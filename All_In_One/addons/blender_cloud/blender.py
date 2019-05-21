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

"""Blender-specific code.

Separated from __init__.py so that we can import & run from non-Blender environments.
"""
import functools
import logging
import os.path

import bpy
from bpy.types import AddonPreferences, Operator, WindowManager, Scene, PropertyGroup
from bpy.props import StringProperty, EnumProperty, PointerProperty, BoolProperty, IntProperty
import rna_prop_ui

from . import pillar, async_loop, flamenco
from .utils import pyside_cache, redraw

PILLAR_WEB_SERVER_URL = os.environ.get('BCLOUD_SERVER', 'https://cloud.blender.org/')
PILLAR_SERVER_URL = '%sapi/' % PILLAR_WEB_SERVER_URL

ADDON_NAME = 'blender_cloud'
log = logging.getLogger(__name__)

icons = None


@pyside_cache('version')
def blender_syncable_versions(self, context):
    """Returns the list of items used by SyncStatusProperties.version EnumProperty."""

    bss = context.window_manager.blender_sync_status
    versions = bss.available_blender_versions
    if not versions:
        return [('', 'No settings stored in your Blender Cloud', '')]
    return [(v, v, '') for v in versions]


class SyncStatusProperties(PropertyGroup):
    status = EnumProperty(
        items=[
            ('NONE', 'NONE', 'We have done nothing at all yet.'),
            ('IDLE', 'IDLE', 'User requested something, which is done, and we are now idle.'),
            ('SYNCING', 'SYNCING', 'Synchronising with Blender Cloud.'),
        ],
        name='status',
        description='Current status of Blender Sync',
        update=redraw)

    version = EnumProperty(
        items=blender_syncable_versions,
        name='Version of Blender from which to pull',
        description='Version of Blender from which to pull')

    message = StringProperty(name='message', update=redraw)
    level = EnumProperty(
        items=[
            ('INFO', 'INFO', ''),
            ('WARNING', 'WARNING', ''),
            ('ERROR', 'ERROR', ''),
            ('SUBSCRIBE', 'SUBSCRIBE', ''),
        ],
        name='level',
        update=redraw)

    def report(self, level: set, message: str):
        assert len(level) == 1, 'level should be a set of one string, not %r' % level
        self.level = level.pop()
        self.message = message

        # Message can also be empty, just to erase it from the GUI.
        # No need to actually log those.
        if message:
            try:
                loglevel = logging._nameToLevel[self.level]
            except KeyError:
                loglevel = logging.WARNING
            log.log(loglevel, message)

    # List of syncable versions is stored in 'available_blender_versions' ID property,
    # because I don't know how to store a variable list of strings in a proper RNA property.
    @property
    def available_blender_versions(self) -> list:
        return self.get('available_blender_versions', [])

    @available_blender_versions.setter
    def available_blender_versions(self, new_versions):
        self['available_blender_versions'] = new_versions


@pyside_cache('project')
def bcloud_available_projects(self, context):
    """Returns the list of items used by BlenderCloudProjectGroup.project EnumProperty."""

    projs = preferences().project.available_projects
    if not projs:
        return [('', 'No projects available in your Blender Cloud', '')]
    return [(p['_id'], p['name'], '') for p in projs]


@functools.lru_cache(1)
def project_extensions(project_id) -> set:
    """Returns the extensions the project is enabled for.

    At the moment of writing these are 'attract' and 'flamenco'.
    """

    log.debug('Finding extensions for project %s', project_id)

    # We can't use our @property, since the preferences may be loaded from a
    # preferences blend file, in which case it is not constructed from Python code.
    available_projects = preferences().project.get('available_projects', [])
    if not available_projects:
        log.debug('No projects available.')
        return set()

    proj = next((p for p in available_projects
                 if p['_id'] == project_id), None)
    if proj is None:
        log.debug('Project %s not found in available projects.', project_id)
        return set()

    return set(proj.get('enabled_for', ()))


def handle_project_update(_=None, _2=None):
    """Handles changing projects, which may cause extensions to be disabled/enabled.

    Ignores arguments so that it can be used as property update callback.
    """

    project_id = preferences().project.project
    log.info('Updating internal state to reflect extensions enabled on current project %s.',
             project_id)

    project_extensions.cache_clear()

    from blender_cloud import attract, flamenco
    attract.deactivate()
    flamenco.deactivate()

    enabled_for = project_extensions(project_id)
    log.info('Project extensions: %s', enabled_for)
    if 'attract' in enabled_for:
        attract.activate()
    if 'flamenco' in enabled_for:
        flamenco.activate()


class BlenderCloudProjectGroup(PropertyGroup):
    status = EnumProperty(
        items=[
            ('NONE', 'NONE', 'We have done nothing at all yet'),
            ('IDLE', 'IDLE', 'User requested something, which is done, and we are now idle'),
            ('FETCHING', 'FETCHING', 'Fetching available projects from Blender Cloud'),
        ],
        name='status',
        update=redraw)

    project = EnumProperty(
        items=bcloud_available_projects,
        name='Cloud project',
        description='Which Blender Cloud project to work with',
        update=handle_project_update
    )

    # List of projects is stored in 'available_projects' ID property,
    # because I don't know how to store a variable list of strings in a proper RNA property.
    @property
    def available_projects(self) -> list:
        return self.get('available_projects', [])

    @available_projects.setter
    def available_projects(self, new_projects):
        self['available_projects'] = new_projects
        handle_project_update()


class BlenderCloudPreferences(AddonPreferences):
    bl_idname = ADDON_NAME

    # The following two properties are read-only to limit the scope of the
    # addon and allow for proper testing within this scope.
    pillar_server = StringProperty(
        name='Blender Cloud Server',
        description='URL of the Blender Cloud backend server',
        default=PILLAR_SERVER_URL,
        get=lambda self: PILLAR_SERVER_URL
    )

    local_texture_dir = StringProperty(
        name='Default Blender Cloud Texture Storage Directory',
        subtype='DIR_PATH',
        default='//textures')

    open_browser_after_share = BoolProperty(
        name='Open Browser after Sharing File',
        description='When enabled, Blender will open a webbrowser',
        default=True
    )

    # TODO: store project-dependent properties with the project, so that people
    # can switch projects and the Attract and Flamenco properties switch with it.
    project = PointerProperty(type=BlenderCloudProjectGroup)

    cloud_project_local_path = StringProperty(
        name='Local Project Path',
        description='Local path of your Attract project, used to search for blend files; '
                    'usually best to set to an absolute path',
        subtype='DIR_PATH',
        default='//../')

    flamenco_manager = PointerProperty(type=flamenco.FlamencoManagerGroup)
    flamenco_exclude_filter = StringProperty(
        name='File Exclude Filter',
        description='Filter like "*.abc;*.mkv" to prevent certain files to be packed '
                    'into the output directory',
        default='')
    # TODO: before making Flamenco public, change the defaults to something less Institute-specific.
    # NOTE: The assumption is that the workers can also find the files in the same path.
    #       This assumption is true for the Blender Institute.
    flamenco_job_file_path = StringProperty(
        name='Job Storage Path',
        description='Path where to store job files, should be accesible for Workers too',
        subtype='DIR_PATH',
        default='/render/_flamenco/storage')

    # TODO: before making Flamenco public, change the defaults to something less Institute-specific.
    flamenco_job_output_path = StringProperty(
        name='Job Output Path',
        description='Path where to store output files, should be accessible for Workers',
        subtype='DIR_PATH',
        default='/render/_flamenco/output')
    flamenco_job_output_strip_components = IntProperty(
        name='Job Output Path Strip Components',
        description='The final output path comprises of the job output path, and the blend file '
                    'path relative to the project with this many path components stripped off '
                    'the front',
        min=0,
        default=0,
        soft_max=4,
    )
    flamenco_open_browser_after_submit = BoolProperty(
        name='Open Browser after Submitting Job',
        description='When enabled, Blender will open a webbrowser',
        default=True
    )

    def draw(self, context):
        import textwrap

        layout = self.layout

        # Carefully try and import the Blender ID addon
        try:
            import blender_id
        except ImportError:
            blender_id = None
            blender_id_profile = None
        else:
            blender_id_profile = blender_id.get_active_profile()
        if blender_id is None:

            msg_icon = 'ERROR'
            text = 'This add-on requires Blender ID'
            help_text = 'Make sure that the Blender ID add-on is installed and activated'
        elif not blender_id_profile:
            msg_icon = 'ERROR'
            text = 'You are logged out.'
            help_text = 'To login, go to the Blender ID add-on preferences.'
        elif bpy.app.debug and pillar.SUBCLIENT_ID not in blender_id_profile.subclients:
            msg_icon = 'QUESTION'
            text = 'No Blender Cloud credentials.'
            help_text = ('You are logged in on Blender ID, but your credentials have not '
                         'been synchronized with Blender Cloud yet. Press the Update '
                         'Credentials button.')
        else:
            msg_icon = 'WORLD_DATA'
            text = 'You are logged in as %s.' % blender_id_profile.username
            help_text = ('To logout or change profile, '
                         'go to the Blender ID add-on preferences.')

        # Authentication stuff
        auth_box = layout.box()
        auth_box.label(text=text, icon=msg_icon)

        help_lines = textwrap.wrap(help_text, 80)
        for line in help_lines:
            auth_box.label(text=line)
        if bpy.app.debug:
            auth_box.operator("pillar.credentials_update")

        # Texture browser stuff
        texture_box = layout.box()
        texture_box.enabled = msg_icon != 'ERROR'
        sub = texture_box.column()
        sub.label(text='Local directory for downloaded textures', icon_value=icon('CLOUD'))
        sub.prop(self, "local_texture_dir", text='Default')
        sub.prop(context.scene, "local_texture_dir", text='Current scene')

        # Blender Sync stuff
        bss = context.window_manager.blender_sync_status
        bsync_box = layout.box()
        bsync_box.enabled = msg_icon != 'ERROR'
        row = bsync_box.row().split(percentage=0.33)
        row.label('Blender Sync with Blender Cloud', icon_value=icon('CLOUD'))

        icon_for_level = {
            'INFO': 'NONE',
            'WARNING': 'INFO',
            'ERROR': 'ERROR',
            'SUBSCRIBE': 'ERROR',
        }
        msg_icon = icon_for_level[bss.level] if bss.message else 'NONE'
        message_container = row.row()
        message_container.label(bss.message, icon=msg_icon)

        sub = bsync_box.column()

        if bss.level == 'SUBSCRIBE':
            self.draw_subscribe_button(sub)
        self.draw_sync_buttons(sub, bss)

        # Image Share stuff
        share_box = layout.box()
        share_box.label('Image Sharing on Blender Cloud', icon_value=icon('CLOUD'))
        share_box.prop(self, 'open_browser_after_share')

        # Project selector
        project_box = layout.box()
        project_box.enabled = self.project.status in {'NONE', 'IDLE'}

        self.draw_project_selector(project_box, self.project)
        extensions = project_extensions(self.project.project)

        # Flamenco stuff
        if 'flamenco' in extensions:
            flamenco_box = project_box.column()
            self.draw_flamenco_buttons(flamenco_box, self.flamenco_manager, context)

    def draw_subscribe_button(self, layout):
        layout.operator('pillar.subscribe', icon='WORLD')

    def draw_sync_buttons(self, layout, bss):
        layout.enabled = bss.status in {'NONE', 'IDLE'}

        buttons = layout.column()
        row_buttons = buttons.row().split(percentage=0.5)
        row_push = row_buttons.row()
        row_pull = row_buttons.row(align=True)

        row_push.operator('pillar.sync',
                          text='Save %i.%i settings' % bpy.app.version[:2],
                          icon='TRIA_UP').action = 'PUSH'

        versions = bss.available_blender_versions
        version = bss.version
        if bss.status in {'NONE', 'IDLE'}:
            if not versions or not version:
                row_pull.operator('pillar.sync',
                                  text='Find version to load',
                                  icon='TRIA_DOWN').action = 'REFRESH'
            else:
                props = row_pull.operator('pillar.sync',
                                          text='Load %s settings' % version,
                                          icon='TRIA_DOWN')
                props.action = 'PULL'
                props.blender_version = version
                row_pull.operator('pillar.sync',
                                  text='',
                                  icon='DOTSDOWN').action = 'SELECT'
        else:
            row_pull.label('Cloud Sync is running.')

    def draw_project_selector(self, project_box, bcp: BlenderCloudProjectGroup):
        project_row = project_box.row(align=True)
        project_row.label('Project settings', icon_value=icon('CLOUD'))

        row_buttons = project_row.row(align=True)

        projects = bcp.available_projects
        project = bcp.project
        if bcp.status in {'NONE', 'IDLE'}:
            if not projects or not project:
                row_buttons.operator('pillar.projects',
                                     text='Find project to load',
                                     icon='FILE_REFRESH')
            else:
                row_buttons.prop(bcp, 'project')
                row_buttons.operator('pillar.projects',
                                     text='',
                                     icon='FILE_REFRESH')
        else:
            row_buttons.label('Fetching available projects.')

        enabled_for = project_extensions(project)
        if not project:
            return

        if not enabled_for:
            project_box.label('This project is not set up for Attract or Flamenco')
            return

        project_box.label('This project is set up for: %s' %
                          ', '.join(sorted(enabled_for)))

        # This is only needed when the project is set up for either Attract or Flamenco.
        project_box.prop(self, 'cloud_project_local_path',
                         text='Local Cloud Project Path')

    def draw_flamenco_buttons(self, flamenco_box, bcp: flamenco.FlamencoManagerGroup, context):
        from .flamenco import bam_interface

        header_row = flamenco_box.row(align=True)
        header_row.label('Flamenco:', icon_value=icon('CLOUD'))

        manager_split = flamenco_box.split(0.32, align=True)
        manager_split.label('Manager:')
        manager_box = manager_split.row(align=True)

        if bcp.status in {'NONE', 'IDLE'}:
            if not bcp.available_managers or not bcp.manager:
                manager_box.operator('flamenco.managers',
                                     text='Find Flamenco Managers',
                                     icon='FILE_REFRESH')
            else:
                manager_box.prop(bcp, 'manager', text='')
                manager_box.operator('flamenco.managers',
                                     text='',
                                     icon='FILE_REFRESH')
        else:
            manager_box.label('Fetching available managers.')

        path_split = flamenco_box.split(0.32, align=True)
        path_split.label(text='Job File Path:')
        path_box = path_split.row(align=True)
        path_box.prop(self, 'flamenco_job_file_path', text='')
        props = path_box.operator('flamenco.explore_file_path', text='', icon='DISK_DRIVE')
        props.path = self.flamenco_job_file_path

        job_output_box = flamenco_box.column(align=True)
        path_split = job_output_box.split(0.32, align=True)
        path_split.label(text='Job Output Path:')
        path_box = path_split.row(align=True)
        path_box.prop(self, 'flamenco_job_output_path', text='')
        props = path_box.operator('flamenco.explore_file_path', text='', icon='DISK_DRIVE')
        props.path = self.flamenco_job_output_path
        job_output_box.prop(self, 'flamenco_exclude_filter')

        prop_split = job_output_box.split(0.32, align=True)
        prop_split.label('Strip Components:')
        prop_split.prop(self, 'flamenco_job_output_strip_components', text='')

        from .flamenco import render_output_path

        path_box = job_output_box.row(align=True)
        output_path = render_output_path(context)
        if output_path:
            path_box.label(str(output_path))
            props = path_box.operator('flamenco.explore_file_path', text='', icon='DISK_DRIVE')
            props.path = str(output_path.parent)
        else:
            path_box.label('Blend file is not in your project path, '
                           'unable to give output path example.')

        flamenco_box.prop(self, 'flamenco_open_browser_after_submit')


class PillarCredentialsUpdate(pillar.PillarOperatorMixin,
                              Operator):
    """Updates the Pillar URL and tests the new URL."""
    bl_idname = 'pillar.credentials_update'
    bl_label = 'Update credentials'
    bl_description = 'Resynchronises your Blender ID login with Blender Cloud'

    log = logging.getLogger('bpy.ops.%s' % bl_idname)

    @classmethod
    def poll(cls, context):
        # Only allow activation when the user is actually logged in.
        return cls.is_logged_in(context)

    @classmethod
    def is_logged_in(cls, context):
        try:
            import blender_id
        except ImportError:
            return False

        return blender_id.is_logged_in()

    def execute(self, context):
        import blender_id
        import asyncio

        # Only allow activation when the user is actually logged in.
        if not self.is_logged_in(context):
            self.report({'ERROR'}, 'No active profile found')
            return {'CANCELLED'}

        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.check_credentials(context, set()))
        except blender_id.BlenderIdCommError as ex:
            log.exception('Error sending subclient-specific token to Blender ID')
            self.report({'ERROR'}, 'Failed to sync Blender ID to Blender Cloud')
            return {'CANCELLED'}
        except Exception as ex:
            log.exception('Error in test call to Pillar')
            self.report({'ERROR'}, 'Failed test connection to Blender Cloud')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Blender Cloud credentials & endpoint URL updated.')
        return {'FINISHED'}


class PILLAR_OT_subscribe(Operator):
    """Opens a browser to subscribe the user to the Cloud."""
    bl_idname = 'pillar.subscribe'
    bl_label = 'Subscribe to the Cloud'
    bl_description = "Opens a page in a web browser to subscribe to the Blender Cloud"

    def execute(self, context):
        import webbrowser

        webbrowser.open_new_tab('https://cloud.blender.org/join')
        self.report({'INFO'}, 'We just started a browser for you.')

        return {'FINISHED'}


class PILLAR_OT_projects(async_loop.AsyncModalOperatorMixin,
                         pillar.AuthenticatedPillarOperatorMixin,
                         Operator):
    """Fetches the projects available to the user"""
    bl_idname = 'pillar.projects'
    bl_label = 'Fetch available projects'

    stop_upon_exception = True
    _log = logging.getLogger('bpy.ops.%s' % bl_idname)

    async def async_execute(self, context):
        if not await self.authenticate(context):
            return

        import pillarsdk
        from .pillar import pillar_call

        self.log.info('Going to fetch projects for user %s', self.user_id)

        preferences().project.status = 'FETCHING'

        # Get all projects, except the home project.
        projects_user = await pillar_call(
            pillarsdk.Project.all,
            {'where': {'user': self.user_id,
                       'category': {'$ne': 'home'}},
             'sort': '-name',
             'projection': {'_id': True,
                            'name': True,
                            'extension_props': True},
             })

        projects_shared = await pillar_call(
            pillarsdk.Project.all,
            {'where': {'user': {'$ne': self.user_id},
                       'permissions.groups.group': {'$in': self.db_user.groups}},
             'sort': '-name',
             'projection': {'_id': True,
                            'name': True,
                            'extension_props': True},
             })

        # We need to convert to regular dicts before storing in ID properties.
        # Also don't store more properties than we need.
        def reduce_properties(project_list):
            for p in project_list:
                p = p.to_dict()
                extension_props = p.get('extension_props', {})
                enabled_for = list(extension_props.keys())

                self._log.debug('Project %r is enabled for %s', p['name'], enabled_for)
                yield {
                    '_id': p['_id'],
                    'name': p['name'],
                    'enabled_for': enabled_for,
                }

        projects = list(reduce_properties(projects_user['_items'])) + \
                   list(reduce_properties(projects_shared['_items']))

        def proj_sort_key(project):
            return project.get('name')

        preferences().project.available_projects = sorted(projects, key=proj_sort_key)

        self.quit()

    def quit(self):
        preferences().project.status = 'IDLE'
        super().quit()


class PILLAR_PT_image_custom_properties(rna_prop_ui.PropertyPanel, bpy.types.Panel):
    """Shows custom properties in the image editor."""

    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Custom Properties'

    _context_path = 'edit_image'
    _property_type = bpy.types.Image


def preferences() -> BlenderCloudPreferences:
    return bpy.context.user_preferences.addons[ADDON_NAME].preferences


def load_custom_icons():
    global icons

    if icons is not None:
        # Already loaded
        return

    import bpy.utils.previews
    icons = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
    icons.load('CLOUD', os.path.join(my_icons_dir, 'icon-cloud.png'), 'IMAGE')


def unload_custom_icons():
    global icons

    if icons is None:
        # Already unloaded
        return

    bpy.utils.previews.remove(icons)
    icons = None


def icon(icon_name: str) -> int:
    """Returns the icon ID for the named icon.

    Use with layout.operator('pillar.image_share', icon_value=icon('CLOUD'))
    """

    return icons[icon_name].icon_id


def register():
    bpy.utils.register_class(BlenderCloudProjectGroup)
    bpy.utils.register_class(BlenderCloudPreferences)
    bpy.utils.register_class(PillarCredentialsUpdate)
    bpy.utils.register_class(SyncStatusProperties)
    bpy.utils.register_class(PILLAR_OT_subscribe)
    bpy.utils.register_class(PILLAR_OT_projects)
    bpy.utils.register_class(PILLAR_PT_image_custom_properties)

    addon_prefs = preferences()

    WindowManager.last_blender_cloud_location = StringProperty(
        name="Last Blender Cloud browser location",
        default="/")

    def default_if_empty(scene, context):
        """The scene's local_texture_dir, if empty, reverts to the addon prefs."""

        if not scene.local_texture_dir:
            scene.local_texture_dir = addon_prefs.local_texture_dir

    Scene.local_texture_dir = StringProperty(
        name='Blender Cloud texture storage directory for current scene',
        subtype='DIR_PATH',
        default=addon_prefs.local_texture_dir,
        update=default_if_empty)

    WindowManager.blender_sync_status = PointerProperty(type=SyncStatusProperties)

    load_custom_icons()


def unregister():
    unload_custom_icons()

    bpy.utils.unregister_class(BlenderCloudProjectGroup)
    bpy.utils.unregister_class(PillarCredentialsUpdate)
    bpy.utils.unregister_class(BlenderCloudPreferences)
    bpy.utils.unregister_class(SyncStatusProperties)
    bpy.utils.unregister_class(PILLAR_OT_subscribe)
    bpy.utils.unregister_class(PILLAR_OT_projects)
    bpy.utils.unregister_class(PILLAR_PT_image_custom_properties)

    del WindowManager.last_blender_cloud_location
    del WindowManager.blender_sync_status
