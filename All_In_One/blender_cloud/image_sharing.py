# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import logging
import os.path
import tempfile
import datetime

import bpy
import pillarsdk
from pillarsdk import exceptions as sdk_exceptions
from .pillar import pillar_call
from . import async_loop, pillar, home_project, blender

REQUIRES_ROLES_FOR_IMAGE_SHARING = {'subscriber', 'demo'}
IMAGE_SHARING_GROUP_NODE_NAME = 'Image sharing'
log = logging.getLogger(__name__)


async def find_image_sharing_group_id(home_project_id, user_id):
    # Find the top-level image sharing group node.
    try:
        share_group, created = await pillar.find_or_create_node(
            where={'project': home_project_id,
                   'node_type': 'group',
                   'parent': None,
                   'name': IMAGE_SHARING_GROUP_NODE_NAME},
            additional_create_props={
                'user': user_id,
                'properties': {},
            },
            projection={'_id': 1},
            may_create=True)
    except pillar.PillarError:
        log.exception('Pillar error caught')
        raise pillar.PillarError('Unable to find image sharing folder on the Cloud')

    return share_group['_id']


class PILLAR_OT_image_share(pillar.PillarOperatorMixin,
                            async_loop.AsyncModalOperatorMixin,
                            bpy.types.Operator):
    bl_idname = 'pillar.image_share'
    bl_label = 'Share an image/screenshot via Blender Cloud'
    bl_description = 'Uploads an image for sharing via Blender Cloud'

    log = logging.getLogger('bpy.ops.%s' % bl_idname)

    home_project_id = None
    home_project_url = 'home'
    share_group_id = None  # top-level share group node ID
    user_id = None

    target = bpy.props.EnumProperty(
        items=[
            ('FILE', 'File', 'Share an image file'),
            ('DATABLOCK', 'Datablock', 'Share an image datablock'),
            ('SCREENSHOT', 'Screenshot', 'Share a screenshot'),
        ],
        name='target',
        default='SCREENSHOT')

    name = bpy.props.StringProperty(name='name',
                                    description='File or datablock name to sync')

    screenshot_show_multiview = bpy.props.BoolProperty(
        name='screenshot_show_multiview',
        description='Enable Multi-View',
        default=False)

    screenshot_use_multiview = bpy.props.BoolProperty(
        name='screenshot_use_multiview',
        description='Use Multi-View',
        default=False)

    screenshot_full = bpy.props.BoolProperty(
        name='screenshot_full',
        description='Full Screen, Capture the whole window (otherwise only capture the active area)',
        default=False)

    def invoke(self, context, event):
        # Do a quick test on datablock dirtyness. If it's not packed and dirty,
        # the user should save it first.
        if self.target == 'DATABLOCK':
            if not self.name:
                self.report({'ERROR'}, 'No name given of the datablock to share.')
                return {'CANCELLED'}

            datablock = bpy.data.images[self.name]
            if datablock.type == 'IMAGE' and datablock.is_dirty and not datablock.packed_file:
                self.report({'ERROR'}, 'Datablock is dirty, save it first.')
                return {'CANCELLED'}

        return async_loop.AsyncModalOperatorMixin.invoke(self, context, event)

    async def async_execute(self, context):
        """Entry point of the asynchronous operator."""

        # We don't want to influence what is included in the screen shot.
        if self.target == 'SCREENSHOT':
            print('Blender Cloud add-on is communicating with Blender Cloud')
        else:
            self.report({'INFO'}, 'Communicating with Blender Cloud')

        try:
            # Refresh credentials
            try:
                db_user = await self.check_credentials(context, REQUIRES_ROLES_FOR_IMAGE_SHARING)
                self.user_id = db_user['_id']
                self.log.debug('Found user ID: %s', self.user_id)
            except pillar.NotSubscribedToCloudError:
                self.log.exception('User not subscribed to cloud.')
                self.report({'ERROR'}, 'Please subscribe to the Blender Cloud.')
                self._state = 'QUIT'
                return
            except pillar.UserNotLoggedInError:
                self.log.exception('Error checking/refreshing credentials.')
                self.report({'ERROR'}, 'Please log in on Blender ID first.')
                self._state = 'QUIT'
                return

            # Find the home project.
            try:
                home_proj = await home_project.get_home_project({
                    'projection': {'_id': 1, 'url': 1}
                })
            except sdk_exceptions.ForbiddenAccess:
                self.log.exception('Forbidden access to home project.')
                self.report({'ERROR'}, 'Did not get access to home project.')
                self._state = 'QUIT'
                return
            except sdk_exceptions.ResourceNotFound:
                self.report({'ERROR'}, 'Home project not found.')
                self._state = 'QUIT'
                return

            self.home_project_id = home_proj['_id']
            self.home_project_url = home_proj['url']

            try:
                gid = await find_image_sharing_group_id(self.home_project_id,
                                                        self.user_id)
                self.share_group_id = gid
                self.log.debug('Found group node ID: %s', self.share_group_id)
            except sdk_exceptions.ForbiddenAccess:
                self.log.exception('Unable to find Group ID')
                self.report({'ERROR'}, 'Unable to find sync folder.')
                self._state = 'QUIT'
                return

            await self.share_image(context)
        except Exception as ex:
            self.log.exception('Unexpected exception caught.')
            self.report({'ERROR'}, 'Unexpected error %s: %s' % (type(ex), ex))

        self._state = 'QUIT'

    async def share_image(self, context):
        """Sends files to the Pillar server."""

        if self.target == 'FILE':
            self.report({'INFO'}, "Uploading %s '%s'" % (self.target.lower(), self.name))
            node = await self.upload_file(self.name)
        elif self.target == 'SCREENSHOT':
            node = await self.upload_screenshot(context)
        else:
            self.report({'INFO'}, "Uploading %s '%s'" % (self.target.lower(), self.name))
            node = await self.upload_datablock(context)

        self.report({'INFO'}, 'Upload complete, creating link to share.')
        share_info = await pillar_call(node.share)
        url = share_info.get('short_link')
        context.window_manager.clipboard = url
        self.report({'INFO'}, 'The link has been copied to your clipboard: %s' % url)

        await self.maybe_open_browser(url)

    async def upload_file(self, filename: str, fileobj=None) -> pillarsdk.Node:
        """Uploads a file to the cloud, attached to the image sharing node.

        Returns the node.
        """

        self.log.info('Uploading file %s', filename)
        node = await pillar_call(pillarsdk.Node.create_asset_from_file,
                                 self.home_project_id,
                                 self.share_group_id,
                                 'image',
                                 filename,
                                 extra_where={'user': self.user_id},
                                 always_create_new_node=True,
                                 fileobj=fileobj,
                                 caching=False)
        node_id = node['_id']
        self.log.info('Created node %s', node_id)
        self.report({'INFO'}, 'File succesfully uploaded to the cloud!')

        return node

    async def maybe_open_browser(self, url):
        prefs = blender.preferences()
        if not prefs.open_browser_after_share:
            return

        import webbrowser

        self.log.info('Opening browser at %s', url)
        webbrowser.open_new_tab(url)

    async def upload_datablock(self, context) -> pillarsdk.Node:
        """Saves a datablock to file if necessary, then upload.

        Returns the node.
        """

        self.log.info("Uploading datablock '%s'" % self.name)
        datablock = bpy.data.images[self.name]

        if datablock.type == 'RENDER_RESULT':
            # Construct a sensible name for this render.
            filename = '%s-%s-render%s' % (
                os.path.splitext(os.path.basename(context.blend_data.filepath))[0],
                context.scene.name,
                context.scene.render.file_extension)
            return await self.upload_via_tempdir(datablock, filename)

        if datablock.packed_file is not None:
            return await self.upload_packed_file(datablock)

        if datablock.is_dirty:
            # We can handle dirty datablocks like this if we want.
            # However, I (Sybren) do NOT think it's a good idea to:
            # - Share unsaved data to the cloud; users can assume it's saved
            #   to disk and close blender, losing their file.
            # - Save unsaved data first; this can overwrite a file a user
            #   didn't want to overwrite.
            filename = bpy.path.basename(datablock.filepath)
            return await self.upload_via_tempdir(datablock, filename)

        filepath = bpy.path.abspath(datablock.filepath)
        return await self.upload_file(filepath)

    async def upload_via_tempdir(self, datablock, filename_on_cloud) -> pillarsdk.Node:
        """Saves the datablock to file, and uploads it to the cloud.

        Saving is done to a temporary directory, which is removed afterwards.

        Returns the node.
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, filename_on_cloud)
            self.log.debug('Saving %s to %s', datablock, filepath)
            datablock.save_render(filepath)
            return await self.upload_file(filepath)

    async def upload_packed_file(self, datablock) -> pillarsdk.Node:
        """Uploads a packed file directly from memory.

        Returns the node.
        """

        import io

        filename = '%s.%s' % (datablock.name, datablock.file_format.lower())
        fileobj = io.BytesIO(datablock.packed_file.data)
        fileobj.seek(0)  # ensure PillarSDK reads the file from the beginning.
        self.log.info('Uploading packed file directly from memory to %r.', filename)
        return await self.upload_file(filename, fileobj=fileobj)

    async def upload_screenshot(self, context) -> pillarsdk.Node:
        """Takes a screenshot, saves it to a temp file, and uploads it."""

        self.name = datetime.datetime.now().strftime('Screenshot-%Y-%m-%d-%H%M%S.png')
        self.report({'INFO'}, "Uploading %s '%s'" % (self.target.lower(), self.name))

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, self.name)
            self.log.debug('Saving screenshot to %s', filepath)
            bpy.ops.screen.screenshot(filepath=filepath,
                                      show_multiview=self.screenshot_show_multiview,
                                      use_multiview=self.screenshot_use_multiview,
                                      full=self.screenshot_full)
            return await self.upload_file(filepath)


def image_editor_menu(self, context):
    image = context.space_data.image

    box = self.layout.row()
    if image and image.has_data:
        text = 'Share on Blender Cloud'
        if image.type == 'IMAGE' and image.is_dirty and not image.packed_file:
            box.enabled = False
            text = 'Save image before sharing on Blender Cloud'

        props = box.operator(PILLAR_OT_image_share.bl_idname, text=text,
                             icon_value=blender.icon('CLOUD'))
        props.target = 'DATABLOCK'
        props.name = image.name


def window_menu(self, context):
    props = self.layout.operator(PILLAR_OT_image_share.bl_idname,
                                 text='Share screenshot via Blender Cloud',
                                 icon_value=blender.icon('CLOUD'))
    props.target = 'SCREENSHOT'
    props.screenshot_full = True


def register():
    bpy.utils.register_class(PILLAR_OT_image_share)

    bpy.types.IMAGE_MT_image.append(image_editor_menu)
    bpy.types.INFO_MT_window.append(window_menu)


def unregister():
    bpy.utils.unregister_class(PILLAR_OT_image_share)

    bpy.types.IMAGE_MT_image.remove(image_editor_menu)
    bpy.types.INFO_MT_window.remove(window_menu)
