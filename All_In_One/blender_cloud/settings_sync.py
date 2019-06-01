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

"""Synchronises settings & startup file with the Cloud.
Caching is disabled on many PillarSDK calls, as synchronisation can happen
rapidly between multiple machines. This means that information can be outdated
in seconds, rather than the minutes the cache system assumes.
"""
import functools
import logging
import pathlib
import tempfile
import shutil

import bpy

import asyncio

import pillarsdk
from pillarsdk import exceptions as sdk_exceptions
from .pillar import pillar_call
from . import async_loop, pillar, cache, blendfile, home_project

SETTINGS_FILES_TO_UPLOAD = ['userpref.blend', 'startup.blend']

# These are RNA keys inside the userpref.blend file, and their
# Python properties names. These settings will not be synced.
LOCAL_SETTINGS_RNA = [
    (b'dpi', 'system.dpi'),
    (b'virtual_pixel', 'system.virtual_pixel_mode'),
    (b'compute_device_id', 'system.compute_device'),
    (b'compute_device_type', 'system.compute_device_type'),
    (b'fontdir', 'filepaths.font_directory'),
    (b'textudir', 'filepaths.texture_directory'),
    (b'renderdir', 'filepaths.render_output_directory'),
    (b'pythondir', 'filepaths.script_directory'),
    (b'sounddir', 'filepaths.sound_directory'),
    (b'tempdir', 'filepaths.temporary_directory'),
    (b'render_cachedir', 'filepaths.render_cache_directory'),
    (b'i18ndir', 'filepaths.i18n_branches_directory'),
    (b'image_editor', 'filepaths.image_editor'),
    (b'anim_player', 'filepaths.animation_player'),
]

REQUIRES_ROLES_FOR_SYNC = set()  # no roles needed.
SYNC_GROUP_NODE_NAME = 'Blender Sync'
SYNC_GROUP_NODE_DESC = 'The [Blender Cloud Addon](https://cloud.blender.org/services' \
                       '#blender-addon) will synchronize your Blender settings here.'
log = logging.getLogger(__name__)


def set_blender_sync_status(set_status: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bss = bpy.context.window_manager.blender_sync_status
            bss.status = set_status
            try:
                return func(*args, **kwargs)
            finally:
                bss.status = 'IDLE'

        return wrapper

    return decorator


def async_set_blender_sync_status(set_status: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            bss = bpy.context.window_manager.blender_sync_status
            bss.status = set_status
            try:
                return await func(*args, **kwargs)
            finally:
                bss.status = 'IDLE'

        return wrapper

    return decorator


async def find_sync_group_id(home_project_id: str,
                             user_id: str,
                             blender_version: str,
                             *,
                             may_create=True) -> str:
    """Finds the group node in which to store sync assets.

    If the group node doesn't exist and may_create=True, it creates it.
    """

    # Find the top-level sync group node. This should have been
    # created by Pillar while creating the home project.
    try:
        sync_group, created = await pillar.find_or_create_node(
            where={'project': home_project_id,
                   'node_type': 'group',
                   'parent': None,
                   'name': SYNC_GROUP_NODE_NAME,
                   'user': user_id},
            projection={'_id': 1},
            may_create=False)
    except pillar.PillarError:
        raise pillar.PillarError('Unable to find sync folder on the Cloud')

    if not may_create and sync_group is None:
        log.info("Sync folder doesn't exist, and not creating it either.")
        return None, None

    # Find/create the sub-group for the requested Blender version
    try:
        sub_sync_group, created = await pillar.find_or_create_node(
            where={'project': home_project_id,
                   'node_type': 'group',
                   'parent': sync_group['_id'],
                   'name': blender_version,
                   'user': user_id},
            additional_create_props={
                'description': 'Sync folder for Blender %s' % blender_version,
                'properties': {'status': 'published'},
            },
            projection={'_id': 1},
            may_create=may_create)
    except pillar.PillarError:
        raise pillar.PillarError('Unable to create sync folder on the Cloud')

    if not may_create and sub_sync_group is None:
        log.info("Sync folder for Blender version %s doesn't exist, "
                 "and not creating it either.", blender_version)
        return sync_group['_id'], None

    return sync_group['_id'], sub_sync_group['_id']


@functools.lru_cache()
async def available_blender_versions(home_project_id: str, user_id: str) -> list:
    bss = bpy.context.window_manager.blender_sync_status

    # Get the available Blender versions.
    sync_group = await pillar_call(
        pillarsdk.Node.find_first,
        params={
            'where': {'project': home_project_id,
                      'node_type': 'group',
                      'parent': None,
                      'name': SYNC_GROUP_NODE_NAME,
                      'user': user_id},
            'projection': {'_id': 1},
        },
        caching=False)

    if sync_group is None:
        bss.report({'ERROR'}, 'No synced Blender settings in your Blender Cloud')
        log.debug('-- unable to find sync group for home_project_id=%r and user_id=%r',
                  home_project_id, user_id)
        return []

    sync_nodes = await pillar_call(
        pillarsdk.Node.all,
        params={
            'where': {'project': home_project_id,
                      'node_type': 'group',
                      'parent': sync_group['_id'],
                      'user': user_id},
            'projection': {'_id': 1, 'name': 1},
            'sort': '-name',
        },
        caching=False)

    if not sync_nodes or not sync_nodes._items:
        bss.report({'ERROR'}, 'No synced Blender settings in your Blender Cloud.')
        return []

    versions = [node.name for node in sync_nodes._items]
    log.debug('Versions: %s', versions)

    return versions


# noinspection PyAttributeOutsideInit
class PILLAR_OT_sync(pillar.PillarOperatorMixin,
                     async_loop.AsyncModalOperatorMixin,
                     bpy.types.Operator):
    bl_idname = 'pillar.sync'
    bl_label = 'Synchronise with Blender Cloud'
    bl_description = 'Synchronises Blender settings with Blender Cloud'

    log = logging.getLogger('bpy.ops.%s' % bl_idname)
    home_project_id = None
    sync_group_id = None  # top-level sync group node ID
    sync_group_versioned_id = None  # sync group node ID for the given Blender version.

    action = bpy.props.EnumProperty(
        items=[
            ('PUSH', 'Push', 'Push settings to the Blender Cloud'),
            ('PULL', 'Pull', 'Pull settings from the Blender Cloud'),
            ('REFRESH', 'Refresh', 'Refresh available versions'),
            ('SELECT', 'Select', 'Select version to sync'),
        ],
        name='action')

    CURRENT_BLENDER_VERSION = '%i.%i' % bpy.app.version[:2]
    blender_version = bpy.props.StringProperty(name='blender_version',
                                               description='Blender version to sync for',
                                               default=CURRENT_BLENDER_VERSION)

    def bss_report(self, level, message):
        bss = bpy.context.window_manager.blender_sync_status
        bss.report(level, message)

    def invoke(self, context, event):
        if self.action == 'SELECT':
            # Synchronous action
            return self.action_select(context)

        if self.action in {'PUSH', 'PULL'} and not self.blender_version:
            self.bss_report({'ERROR'}, 'No Blender version to sync for was given.')
            return {'CANCELLED'}

        return async_loop.AsyncModalOperatorMixin.invoke(self, context, event)

    def action_select(self, context):
        """Allows selection of the Blender version to use.

        This is a synchronous action, as it requires a dialog box.
        """

        self.log.info('Performing action SELECT')

        # Do a refresh before we can show the dropdown.
        fut = asyncio.ensure_future(self.async_execute(context, action_override='REFRESH'))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fut)

        self._state = 'SELECTING'
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        bss = bpy.context.window_manager.blender_sync_status
        self.layout.prop(bss, 'version', text='Blender version')

    def execute(self, context):
        if self.action != 'SELECT':
            log.debug('Ignoring execute() for action %r', self.action)
            return {'FINISHED'}

        log.debug('Performing execute() for action %r', self.action)
        # Perform the sync when the user closes the dialog box.
        bss = bpy.context.window_manager.blender_sync_status
        bpy.ops.pillar.sync('INVOKE_DEFAULT',
                            action='PULL',
                            blender_version=bss.version)

        return {'FINISHED'}

    @async_set_blender_sync_status('SYNCING')
    async def async_execute(self, context, *, action_override=None):
        """Entry point of the asynchronous operator."""

        action = action_override or self.action
        self.bss_report({'INFO'}, 'Communicating with Blender Cloud')
        self.log.info('Performing action %s', action)

        try:
            # Refresh credentials
            try:
                db_user = await self.check_credentials(context, REQUIRES_ROLES_FOR_SYNC)
                self.user_id = db_user['_id']
                log.debug('Found user ID: %s', self.user_id)
            except pillar.NotSubscribedToCloudError:
                self.log.exception('User not subscribed to cloud.')
                self.bss_report({'SUBSCRIBE'}, 'Please subscribe to the Blender Cloud.')
                self._state = 'QUIT'
                return
            except pillar.UserNotLoggedInError:
                self.log.exception('Error checking/refreshing credentials.')
                self.bss_report({'ERROR'}, 'Please log in on Blender ID first.')
                self._state = 'QUIT'
                return

            # Find the home project.
            try:
                self.home_project_id = await home_project.get_home_project_id()
            except sdk_exceptions.ForbiddenAccess:
                self.log.exception('Forbidden access to home project.')
                self.bss_report({'ERROR'}, 'Did not get access to home project.')
                self._state = 'QUIT'
                return
            except sdk_exceptions.ResourceNotFound:
                self.bss_report({'ERROR'}, 'Home project not found.')
                self._state = 'QUIT'
                return

            # Only create the folder structure if we're pushing.
            may_create = self.action == 'PUSH'
            try:
                gid, subgid = await find_sync_group_id(self.home_project_id,
                                                       self.user_id,
                                                       self.blender_version,
                                                       may_create=may_create)
                self.sync_group_id = gid
                self.sync_group_versioned_id = subgid
                self.log.debug('Found top-level group node ID: %s', self.sync_group_id)
                self.log.debug('Found group node ID for %s: %s',
                               self.blender_version, self.sync_group_versioned_id)
            except sdk_exceptions.ForbiddenAccess:
                self.log.exception('Unable to find Group ID')
                self.bss_report({'ERROR'}, 'Unable to find sync folder.')
                self._state = 'QUIT'
                return

            # Perform the requested action.
            action_method = {
                'PUSH': self.action_push,
                'PULL': self.action_pull,
                'REFRESH': self.action_refresh,
            }[action]
            await action_method(context)
        except Exception as ex:
            self.log.exception('Unexpected exception caught.')
            self.bss_report({'ERROR'}, 'Unexpected error: %s' % ex)

        self._state = 'QUIT'

    async def action_push(self, context):
        """Sends files to the Pillar server."""

        self.log.info('Saved user preferences to disk before pushing to cloud.')
        bpy.ops.wm.save_userpref()

        config_dir = pathlib.Path(bpy.utils.user_resource('CONFIG'))

        for fname in SETTINGS_FILES_TO_UPLOAD:
            path = config_dir / fname
            if not path.exists():
                self.log.debug('Skipping non-existing %s', path)
                continue

            if self.signalling_future.cancelled():
                self.bss_report({'WARNING'}, 'Upload aborted.')
                return

            self.bss_report({'INFO'}, 'Uploading %s' % fname)
            try:
                await pillar.attach_file_to_group(path,
                                                  self.home_project_id,
                                                  self.sync_group_versioned_id,
                                                  self.user_id)
            except sdk_exceptions.RequestEntityTooLarge as ex:
                self.log.error('File too big to upload: %s' % ex)
                self.log.error('To upload larger files, please subscribe to Blender Cloud.')
                self.bss_report({'SUBSCRIBE'}, 'File %s too big to upload. '
                                               'Subscribe for unlimited space.' % fname)
                self._state = 'QUIT'
                return

        await self.action_refresh(context)

        # After pushing, change the 'pull' version to the current version of Blender.
        # Or to the latest version, if by some mistake somewhere the current push
        # isn't available after all.
        bss = bpy.context.window_manager.blender_sync_status
        if self.CURRENT_BLENDER_VERSION in bss.available_blender_versions:
            bss.version = self.CURRENT_BLENDER_VERSION
        else:
            bss.version = max(bss.available_blender_versions)

        self.bss_report({'INFO'}, 'Settings pushed to Blender Cloud.')

    async def action_pull(self, context):
        """Loads files from the Pillar server."""

        # If the sync group node doesn't exist, offer a list of groups that do.
        if self.sync_group_id is None:
            self.bss_report({'ERROR'},
                            'There are no synced Blender settings in your Blender Cloud.')
            return

        if self.sync_group_versioned_id is None:
            self.bss_report({'ERROR'}, 'Therre are no synced Blender settings for version %s' %
                            self.blender_version)
            return

        self.bss_report({'INFO'}, 'Pulling settings from Blender Cloud')
        with tempfile.TemporaryDirectory(prefix='bcloud-sync') as tempdir:
            for fname in SETTINGS_FILES_TO_UPLOAD:
                await self.download_settings_file(fname, tempdir)

        self.bss_report({'WARNING'}, 'Settings pulled from Cloud, restart Blender to load them.')

    async def action_refresh(self, context):
        self.bss_report({'INFO'}, 'Refreshing available Blender versions.')

        # Clear the LRU cache of available_blender_versions so that we can
        # obtain new versions (if someone synced from somewhere else, for example)
        available_blender_versions.cache_clear()

        versions = await available_blender_versions(self.home_project_id, self.user_id)
        bss = bpy.context.window_manager.blender_sync_status
        bss.available_blender_versions = versions

        if versions:
            # There are versions to sync, so we can remove the status message.
            # However, if there aren't any, the status message shows why, and
            # shouldn't be erased.
            self.bss_report({'INFO'}, '')

    async def download_settings_file(self, fname: str, temp_dir: str):
        config_dir = pathlib.Path(bpy.utils.user_resource('CONFIG'))
        meta_path = cache.cache_directory('home-project', 'blender-sync')

        self.bss_report({'INFO'}, 'Downloading %s from Cloud' % fname)

        # Get the asset node
        node_props = {'project': self.home_project_id,
                      'node_type': 'asset',
                      'parent': self.sync_group_versioned_id,
                      'name': fname}
        node = await pillar_call(pillarsdk.Node.find_first, {
            'where': node_props,
            'projection': {'_id': 1, 'properties.file': 1}
        }, caching=False)
        if node is None:
            self.bss_report({'INFO'}, 'Unable to find %s on Blender Cloud' % fname)
            self.log.info('Unable to find node on Blender Cloud for %s', fname)
            return

        async def file_downloaded(file_path: str, file_desc: pillarsdk.File, map_type: str):
            # Allow the caller to adjust the file before we move it into place.

            if fname.lower() == 'userpref.blend':
                await self.update_userpref_blend(file_path)

            # Move the file next to the final location; as it may be on a
            # different filesystem than the temporary directory, this can
            # fail, and we don't want to destroy the existing file.
            local_temp = config_dir / (fname + '~')
            local_final = config_dir / fname

            # Make a backup copy of the file as it was before pulling.
            if local_final.exists():
                local_bak = config_dir / (fname + '-pre-bcloud-pull')
                self.move_file(local_final, local_bak)

            self.move_file(file_path, local_temp)
            self.move_file(local_temp, local_final)

        file_id = node.properties.file
        await pillar.download_file_by_uuid(file_id,
                                           temp_dir,
                                           str(meta_path),
                                           file_loaded_sync=file_downloaded,
                                           future=self.signalling_future)

    def move_file(self, src, dst):
        self.log.info('Moving %s to %s', src, dst)
        shutil.move(str(src), str(dst))

    async def update_userpref_blend(self, file_path: str):
        self.log.info('Overriding machine-local settings in %s', file_path)

        # Remember some settings that should not be overwritten from the Cloud.
        up = bpy.context.user_preferences
        remembered = {}
        for rna_key, python_key in LOCAL_SETTINGS_RNA:
            assert '.' in python_key, 'Sorry, this code assumes there is a dot in the Python key'

            try:
                value = up.path_resolve(python_key)
            except ValueError:
                # Setting doesn't exist. This can happen, for example Cycles
                # settings on a build that doesn't have Cycles enabled.
                continue

            # Map enums from strings (in Python) to ints (in DNA).
            dot_index = python_key.rindex('.')
            parent_key, prop_key = python_key[:dot_index], python_key[dot_index + 1:]
            parent = up.path_resolve(parent_key)
            prop = parent.bl_rna.properties[prop_key]
            if prop.type == 'ENUM':
                log.debug('Rewriting %s from %r to %r',
                          python_key, value, prop.enum_items[value].value)
                value = prop.enum_items[value].value
            else:
                log.debug('Keeping value of %s: %r', python_key, value)

            remembered[rna_key] = value
        log.debug('Overriding values: %s', remembered)

        # Rewrite the userprefs.blend file to override the options.
        with blendfile.open_blend(file_path, 'rb+') as blend:
            prefs = next(block for block in blend.blocks
                         if block.code == b'USER')

            for key, value in remembered.items():
                self.log.debug('prefs[%r] = %r' % (key, prefs[key]))
                self.log.debug('  -> setting prefs[%r] = %r' % (key, value))
                prefs[key] = value


def register():
    bpy.utils.register_class(PILLAR_OT_sync)


def unregister():
    bpy.utils.unregister_class(PILLAR_OT_sync)
