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

# <pep8 compliant>

# Old info, kept here for reference, so that we can merge wiki pages,
# descriptions, etc.
#
# bl_info = {
#     "name": "Attract",
#     "author": "Francesco Siddi, Inês Almeida, Antony Riakiotakis",
#     "version": (0, 2, 0),
#     "blender": (2, 76, 0),
#     "location": "Video Sequence Editor",
#     "description":
#         "Blender integration with the Attract task tracking service"
#         ". *requires the Blender ID add-on",
#     "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
#                 "Scripts/Workflow/Attract",
#     "category": "Workflow",
#     "support": "TESTING"
# }

import contextlib
import functools
import logging

if "bpy" in locals():
    import importlib

    draw = importlib.reload(draw)
    pillar = importlib.reload(pillar)
    async_loop = importlib.reload(async_loop)
else:
    from . import draw
    from .. import pillar, async_loop

import bpy
import pillarsdk
from pillarsdk.nodes import Node
from pillarsdk.projects import Project
from pillarsdk import exceptions as sdk_exceptions

from bpy.types import Operator, Panel, AddonPreferences

log = logging.getLogger(__name__)

# Global flag used to determine whether panels etc. can be drawn.
attract_is_active = False


def active_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return None


def selected_shots(context):
    """Generator, yields selected strips if they are Attract shots."""
    selected_sequences = context.selected_sequences

    if selected_sequences is None:
        return

    for strip in selected_sequences:
        atc_object_id = getattr(strip, 'atc_object_id')
        if not atc_object_id:
            continue

        yield strip


def all_shots(context):
    """Generator, yields all strips if they are Attract shots."""
    sequence_editor = context.scene.sequence_editor

    if sequence_editor is None:
        # we should throw an exception, but at least this change prevents an error
        return []

    for strip in context.scene.sequence_editor.sequences_all:
        atc_object_id = getattr(strip, 'atc_object_id')
        if not atc_object_id:
            continue

        yield strip


def shown_strips(context):
    """Returns the strips from the current meta-strip-stack, or top-level strips.

    What is returned depends on what the user is currently editing.
    """

    if context.scene.sequence_editor.meta_stack:
        return context.scene.sequence_editor.meta_stack[-1].sequences

    return context.scene.sequence_editor.sequences


def remove_atc_props(strip):
    """Resets the attract custom properties assigned to a VSE strip"""

    strip.atc_name = ""
    strip.atc_description = ""
    strip.atc_object_id = ""
    strip.atc_is_synced = False


def shot_id_use(strips):
    """Returns a mapping from shot Object ID to a list of strips that use it."""

    import collections

    # Count the number of uses per Object ID, so that we can highlight double use.
    ids_in_use = collections.defaultdict(list)
    for strip in strips:
        if not getattr(strip, 'atc_is_synced', False):
            continue

        ids_in_use[strip.atc_object_id].append(strip)

    return ids_in_use


def compute_strip_conflicts(scene):
    """Sets the strip property atc_object_id_conflict for each strip."""

    if not attract_is_active:
        return

    if not scene or not scene.sequence_editor or not scene.sequence_editor.sequences_all:
        return

    tag_redraw = False
    ids_in_use = shot_id_use(scene.sequence_editor.sequences_all)
    for strips in ids_in_use.values():
        is_conflict = len(strips) > 1
        for strip in strips:
            if strip.atc_object_id_conflict != is_conflict:
                tag_redraw = True
            strip.atc_object_id_conflict = is_conflict

    if tag_redraw:
        draw.tag_redraw_all_sequencer_editors()
    return ids_in_use


@bpy.app.handlers.persistent
def scene_update_post_handler(scene):
    compute_strip_conflicts(scene)


class AttractPollMixin:
    @classmethod
    def poll(cls, context):
        return attract_is_active


class AttractToolsPanel(AttractPollMixin, Panel):
    bl_label = 'Attract'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    def draw_header(self, context):
        strip = active_strip(context)
        if strip and strip.atc_object_id:
            self.layout.prop(strip, 'atc_is_synced', text='')

    def draw(self, context):
        strip = active_strip(context)
        layout = self.layout
        strip_types = {'MOVIE', 'IMAGE', 'META'}

        selshots = list(selected_shots(context))
        if strip and strip.type in strip_types and strip.atc_object_id:
            if len(selshots) > 1:
                noun = '%i Shots' % len(selshots)
            else:
                noun = 'This Shot'

            if strip.atc_object_id_conflict:
                warnbox = layout.box()
                warnbox.alert = True
                warnbox.label('Warning: This shot is linked to multiple sequencer strips.',
                              icon='ERROR')

            layout.prop(strip, 'atc_name', text='Name')
            layout.prop(strip, 'atc_status', text='Status')

            # Create a special sub-layout for read-only properties.
            ro_sub = layout.column(align=True)
            ro_sub.enabled = False
            ro_sub.prop(strip, 'atc_description', text='Description')
            ro_sub.prop(strip, 'atc_notes', text='Notes')

            if strip.atc_is_synced:
                sub = layout.column(align=True)
                row = sub.row(align=True)
                if bpy.ops.attract.submit_selected.poll():
                    row.operator('attract.submit_selected',
                                 text='Submit %s' % noun,
                                 icon='TRIA_UP')
                else:
                    row.operator(ATTRACT_OT_submit_all.bl_idname)
                row.operator(AttractShotFetchUpdate.bl_idname,
                             text='', icon='FILE_REFRESH')
                row.operator(ATTRACT_OT_shot_open_in_browser.bl_idname,
                             text='', icon='WORLD')
                row.operator(ATTRACT_OT_copy_id_to_clipboard.bl_idname,
                             text='', icon='COPYDOWN')
                sub.operator(ATTRACT_OT_make_shot_thumbnail.bl_idname,
                             text='Render Thumbnail for %s' % noun,
                             icon='RENDER_STILL')

                # Group more dangerous operations.
                dangerous_sub = layout.split(0.6, align=True)
                dangerous_sub.operator('attract.strip_unlink',
                                       text='Unlink %s' % noun,
                                       icon='PANEL_CLOSE')
                dangerous_sub.operator(AttractShotDelete.bl_idname,
                                       text='Delete %s' % noun,
                                       icon='CANCEL')

        elif context.selected_sequences:
            if len(context.selected_sequences) > 1:
                noun = 'Selected Strips'
            else:
                noun = 'This Strip'
            layout.operator(AttractShotSubmitSelected.bl_idname,
                            text='Submit %s as New Shot' % noun)
            layout.operator('attract.shot_relink')
        else:
            layout.operator(ATTRACT_OT_submit_all.bl_idname)


class AttractOperatorMixin(AttractPollMixin):
    """Mix-in class for all Attract operators."""

    def _project_needs_setup_error(self):
        self.report({'ERROR'}, 'Your Blender Cloud project is not set up for Attract.')
        return {'CANCELLED'}

    @functools.lru_cache()
    def find_project(self, project_uuid: str) -> Project:
        """Finds a single project.

        Caches the result in memory to prevent more than one call to Pillar.
        """

        from .. import pillar

        project = pillar.sync_call(Project.find_one, {'where': {'_id': project_uuid}})
        return project

    def find_node_type(self, node_type_name: str) -> dict:
        from .. import pillar, blender

        prefs = blender.preferences()
        project = self.find_project(prefs.project.project)

        # FIXME: Eve doesn't seem to handle the $elemMatch projection properly,
        # even though it works fine in MongoDB itself. As a result, we have to
        # search for the node type.
        node_type_list = project['node_types']
        node_type = next((nt for nt in node_type_list if nt['name'] == node_type_name), None)

        if not node_type:
            return self._project_needs_setup_error()

        return node_type

    def submit_new_strip(self, strip):
        from .. import pillar, blender

        # Define the shot properties
        user_uuid = pillar.pillar_user_uuid()
        if not user_uuid:
            self.report({'ERROR'}, 'Your Blender Cloud user ID is not known, '
                                   'update your credentials.')
            return {'CANCELLED'}

        prop = {'name': strip.name,
                'description': '',
                'properties': {'status': 'todo',
                               'notes': '',
                               'used_in_edit': True,
                               'trim_start_in_frames': strip.frame_offset_start,
                               'trim_end_in_frames': strip.frame_offset_end,
                               'duration_in_edit_in_frames': strip.frame_final_duration,
                               'cut_in_timeline_in_frames': strip.frame_final_start},
                'order': 0,
                'node_type': 'attract_shot',
                'project': blender.preferences().project.project,
                'user': user_uuid}

        # Create a Node item with the attract API
        node = Node(prop)
        post = pillar.sync_call(node.create)

        # Populate the strip with the freshly generated ObjectID and info
        if not post:
            self.report({'ERROR'}, 'Error creating node! Check the console for now.')
            return {'CANCELLED'}

        strip.atc_object_id = node['_id']
        strip.atc_is_synced = True
        strip.atc_name = node['name']
        strip.atc_description = node['description']
        strip.atc_notes = node['properties']['notes']
        strip.atc_status = node['properties']['status']

        draw.tag_redraw_all_sequencer_editors()

    def submit_update(self, strip):
        import pillarsdk
        from .. import pillar

        patch = {
            'op': 'from-blender',
            '$set': {
                'name': strip.atc_name,
                'properties.trim_start_in_frames': strip.frame_offset_start,
                'properties.trim_end_in_frames': strip.frame_offset_end,
                'properties.duration_in_edit_in_frames': strip.frame_final_duration,
                'properties.cut_in_timeline_in_frames': strip.frame_final_start,
                'properties.status': strip.atc_status,
                'properties.used_in_edit': True,
            }
        }

        node = pillarsdk.Node({'_id': strip.atc_object_id})
        result = pillar.sync_call(node.patch, patch)
        log.info('PATCH result: %s', result)

    def relink(self, strip, atc_object_id, *, refresh=False):
        from .. import pillar

        # The node may have been deleted, so we need to send a 'relink' before we try
        # to fetch the node itself.
        node = Node({'_id': atc_object_id})
        pillar.sync_call(node.patch, {'op': 'relink'})

        try:
            node = pillar.sync_call(Node.find, atc_object_id, caching=False)
        except (sdk_exceptions.ResourceNotFound, sdk_exceptions.MethodNotAllowed):
            verb = 'refresh' if refresh else 'relink'
            self.report({'ERROR'}, 'Shot %r not found on the Attract server, unable to %s.'
                        % (atc_object_id, verb))
            strip.atc_is_synced = False
            return {'CANCELLED'}

        strip.atc_is_synced = True
        if not refresh:
            strip.atc_name = node.name
            strip.atc_object_id = node['_id']

        # We do NOT set the position/cuts of the shot, that always has to come from Blender.
        strip.atc_status = node.properties.status
        strip.atc_notes = node.properties.notes or ''
        strip.atc_description = node.description or ''
        draw.tag_redraw_all_sequencer_editors()


class AttractShotFetchUpdate(AttractOperatorMixin, Operator):
    bl_idname = "attract.shot_fetch_update"
    bl_label = "Fetch Update From Attract"
    bl_description = 'Update status, description & notes from Attract'

    @classmethod
    def poll(cls, context):
        return AttractOperatorMixin.poll(context) and any(selected_shots(context))

    def execute(self, context):
        for strip in selected_shots(context):
            status = self.relink(strip, strip.atc_object_id, refresh=True)
            # We don't abort when one strip fails. All selected shots should be
            # refreshed, even if one can't be found (for example).
            if not isinstance(status, set):
                self.report({'INFO'}, "Shot {0} refreshed".format(strip.atc_name))
        return {'FINISHED'}


class AttractShotRelink(AttractShotFetchUpdate):
    bl_idname = "attract.shot_relink"
    bl_label = "Relink With Attract"

    strip_atc_object_id = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        if not AttractOperatorMixin.poll(context):
            return False

        strip = active_strip(context)
        return strip is not None and not getattr(strip, 'atc_object_id', None)

    def execute(self, context):
        strip = active_strip(context)

        status = self.relink(strip, self.strip_atc_object_id)
        if isinstance(status, set):
            return status

        strip.atc_object_id = self.strip_atc_object_id
        self.report({'INFO'}, "Shot {0} relinked".format(strip.atc_name))

        return {'FINISHED'}

    def invoke(self, context, event):
        maybe_id = context.window_manager.clipboard
        if len(maybe_id) == 24:
            try:
                int(maybe_id, 16)
            except ValueError:
                pass
            else:
                self.strip_atc_object_id = maybe_id

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'strip_atc_object_id', text='Shot ID')


class ATTRACT_OT_shot_open_in_browser(AttractOperatorMixin, Operator):
    bl_idname = 'attract.shot_open_in_browser'
    bl_label = 'Open in Browser'
    bl_description = 'Opens a webbrowser to show the shot on Attract'

    @classmethod
    def poll(cls, context):
        return AttractOperatorMixin.poll(context) and \
               bool(context.selected_sequences and active_strip(context))

    def execute(self, context):
        from ..blender import PILLAR_WEB_SERVER_URL
        import webbrowser
        import urllib.parse

        strip = active_strip(context)

        url = urllib.parse.urljoin(PILLAR_WEB_SERVER_URL,
                                   'nodes/%s/redir' % strip.atc_object_id)
        webbrowser.open_new_tab(url)
        self.report({'INFO'}, 'Opened a browser at %s' % url)

        return {'FINISHED'}


class AttractShotDelete(AttractOperatorMixin, Operator):
    bl_idname = 'attract.shot_delete'
    bl_label = 'Delete Shot'
    bl_description = 'Remove this shot from Attract'

    confirm = bpy.props.BoolProperty(name='confirm')

    @classmethod
    def poll(cls, context):
        return AttractOperatorMixin.poll(context) and \
               bool(context.selected_sequences)

    def execute(self, context):
        from .. import pillar

        if not self.confirm:
            self.report({'WARNING'}, 'Delete aborted.')
            return {'CANCELLED'}

        removed = kept = 0
        for strip in selected_shots(context):
            node = pillar.sync_call(Node.find, strip.atc_object_id)
            if not pillar.sync_call(node.delete):
                self.report({'ERROR'}, 'Unable to delete shot %s on Attract.' % strip.atc_name)
                kept += 1
                continue
            remove_atc_props(strip)
            removed += 1

        if kept:
            self.report({'ERROR'}, 'Removed %i shots, but was unable to remove %i' %
                        (removed, kept))
        else:
            self.report({'INFO'}, 'Removed all %i shots from Attract' % removed)

        draw.tag_redraw_all_sequencer_editors()
        return {'FINISHED'}

    def invoke(self, context, event):
        self.confirm = False
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        selshots = list(selected_shots(context))
        if len(selshots) > 1:
            noun = '%i shots' % len(selshots)
        else:
            noun = 'this shot'

        col.prop(self, 'confirm', text="I hereby confirm: delete %s from The Edit." % noun)


class AttractStripUnlink(AttractOperatorMixin, Operator):
    bl_idname = 'attract.strip_unlink'
    bl_label = 'Unlink Shot From This Strip'
    bl_description = 'Remove Attract props from the selected strip(s)'

    @classmethod
    def poll(cls, context):
        return AttractOperatorMixin.poll(context) and \
               bool(context.selected_sequences)

    def execute(self, context):
        unlinked_ids = set()

        # First remove the Attract properties from the strips.
        for strip in context.selected_sequences:
            atc_object_id = getattr(strip, 'atc_object_id')
            remove_atc_props(strip)

            if atc_object_id:
                unlinked_ids.add(atc_object_id)

        # For all Object IDs that are no longer in use in the edit, let Attract know.
        # This should be done with care, as the shot could have been attached to multiple
        # strips.
        id_to_shots = compute_strip_conflicts(context.scene)
        for oid in unlinked_ids:
            if len(id_to_shots[oid]):
                # Still in use
                continue

            node = Node({'_id': oid})
            pillar.sync_call(node.patch, {'op': 'unlink'})

        if len(unlinked_ids) == 1:
            shot_id = unlinked_ids.pop()
            context.window_manager.clipboard = shot_id
            self.report({'INFO'}, 'Copied unlinked shot ID %s to clipboard' % shot_id)
        else:
            self.report({'INFO'}, '%i shots have been marked as Unused.' % len(unlinked_ids))

        draw.tag_redraw_all_sequencer_editors()
        return {'FINISHED'}


class AttractShotSubmitSelected(AttractOperatorMixin, Operator):
    bl_idname = 'attract.submit_selected'
    bl_label = 'Submit All Selected'
    bl_description = 'Submits all selected strips to Attract'

    @classmethod
    def poll(cls, context):
        return AttractOperatorMixin.poll(context) and \
               bool(context.selected_sequences)

    def execute(self, context):
        # Check that the project is set up for Attract.
        maybe_error = self.find_node_type('attract_shot')
        if isinstance(maybe_error, set):
            return maybe_error

        for strip in context.selected_sequences:
            status = self.submit(strip)
            if isinstance(status, set):
                return status

        self.report({'INFO'}, 'All selected strips sent to Attract.')

        return {'FINISHED'}

    def submit(self, strip):
        atc_object_id = getattr(strip, 'atc_object_id', None)

        # Submit as new?
        if not atc_object_id:
            return self.submit_new_strip(strip)

        # Or just save to Attract.
        return self.submit_update(strip)


class ATTRACT_OT_submit_all(AttractOperatorMixin, Operator):
    bl_idname = 'attract.submit_all'
    bl_label = 'Submit All Shots to Attract'
    bl_description = 'Updates Attract with the current state of the edit'

    def execute(self, context):
        # Check that the project is set up for Attract.
        maybe_error = self.find_node_type('attract_shot')
        if isinstance(maybe_error, set):
            return maybe_error

        for strip in all_shots(context):
            status = self.submit_update(strip)
            if isinstance(status, set):
                return status

        self.report({'INFO'}, 'All strips re-sent to Attract.')

        return {'FINISHED'}


class ATTRACT_OT_open_meta_blendfile(AttractOperatorMixin, Operator):
    bl_idname = 'attract.open_meta_blendfile'
    bl_label = 'Open Blendfile'
    bl_description = 'Open Blendfile from movie strip metadata'

    @classmethod
    def poll(cls, context):
        return AttractOperatorMixin.poll(context) and \
               bool(any(cls.filename_from_metadata(s) for s in context.selected_sequences))

    @staticmethod
    def filename_from_metadata(strip):
        """Returns the blendfile name from the strip metadata, or None."""

        # Metadata is a dict like:
        # meta = {'END_FRAME': '88',
        #         'BLEND_FILE': 'metadata-test.blend',
        #         'SCENE': 'SüperSčene',
        #         'FRAME_STEP': '1',
        #         'START_FRAME': '32'}

        meta = strip.get('metadata', None)
        if not meta:
            return None

        return meta.get('BLEND_FILE', None) or None

    def execute(self, context):
        for strip in context.selected_sequences:
            meta = strip.get('metadata', None)
            if not meta:
                continue

            fname = meta.get('BLEND_FILE', None)
            if not fname: continue

            scene = meta.get('SCENE', None)
            self.open_in_new_blender(fname, scene)

        return {'FINISHED'}

    def open_in_new_blender(self, fname, scene):
        """
        :type fname: str
        :type scene: str
        """
        import subprocess
        import sys

        cmd = [
            bpy.app.binary_path,
            str(fname),
        ]

        cmd[1:1] = [v for v in sys.argv if v.startswith('--enable-')]

        if scene:
            cmd.extend(['--python-expr',
                        'import bpy; bpy.context.screen.scene = bpy.data.scenes["%s"]' % scene])
            cmd.extend(['--scene', scene])

        subprocess.Popen(cmd)


class ATTRACT_OT_make_shot_thumbnail(AttractOperatorMixin,
                                     async_loop.AsyncModalOperatorMixin,
                                     Operator):
    bl_idname = 'attract.make_shot_thumbnail'
    bl_label = 'Render Shot Thumbnail'
    bl_description = 'Renders the current frame, and uploads it as thumbnail for the shot'

    stop_upon_exception = True

    @classmethod
    def poll(cls, context):
        return AttractOperatorMixin.poll(context) and bool(context.selected_sequences)

    @contextlib.contextmanager
    def thumbnail_render_settings(self, context, thumbnail_width=512):
        # Remember current settings so we can restore them later.
        orig_res_x = context.scene.render.resolution_x
        orig_res_y = context.scene.render.resolution_y
        orig_percentage = context.scene.render.resolution_percentage
        orig_file_format = context.scene.render.image_settings.file_format
        orig_quality = context.scene.render.image_settings.quality

        try:
            # Update the render size to something thumbnaily.
            factor = orig_res_y / orig_res_x
            context.scene.render.resolution_x = thumbnail_width
            context.scene.render.resolution_y = round(thumbnail_width * factor)
            context.scene.render.resolution_percentage = 100
            context.scene.render.image_settings.file_format = 'JPEG'
            context.scene.render.image_settings.quality = 85

            yield
        finally:
            # Return the render settings to normal.
            context.scene.render.resolution_x = orig_res_x
            context.scene.render.resolution_y = orig_res_y
            context.scene.render.resolution_percentage = orig_percentage
            context.scene.render.image_settings.file_format = orig_file_format
            context.scene.render.image_settings.quality = orig_quality

    @contextlib.contextmanager
    def temporary_current_frame(self, context):
        """Allows the context to set the scene current frame, restores it on exit.

        Yields the initial current frame, so it can be used for reference in the context.
        """
        current_frame = context.scene.frame_current
        try:
            yield current_frame
        finally:
            context.scene.frame_current = current_frame

    async def async_execute(self, context):
        nr_of_strips = len(context.selected_sequences)
        do_multishot = nr_of_strips > 1

        with self.temporary_current_frame(context) as original_curframe:
            # The multishot and singleshot branches do pretty much the same thing,
            # but report differently to the user.
            if do_multishot:
                context.window_manager.progress_begin(0, nr_of_strips)
                try:
                    self.report({'INFO'}, 'Rendering thumbnails for %i selected shots.' %
                                nr_of_strips)

                    strips = sorted(context.selected_sequences, key=self.by_frame)
                    for idx, strip in enumerate(strips):
                        context.window_manager.progress_update(idx)

                        # Pick the middle frame, except for the strip the original current frame
                        # marker was over.
                        if not self.strip_contains(strip, original_curframe):
                            self.set_middle_frame(context, strip)
                        else:
                            context.scene.frame_set(original_curframe)
                        await self.thumbnail_strip(context, strip)

                        if self._state == 'QUIT':
                            return
                    context.window_manager.progress_update(nr_of_strips)
                finally:
                    context.window_manager.progress_end()

            else:
                strip = active_strip(context)
                if not self.strip_contains(strip, original_curframe):
                    self.report({'WARNING'}, 'Rendering middle frame as thumbnail for active shot.')
                    self.set_middle_frame(context, strip)
                else:
                    self.report({'INFO'}, 'Rendering current frame as thumbnail for active shot.')

                context.window_manager.progress_begin(0, 1)
                context.window_manager.progress_update(0)
                try:
                    await self.thumbnail_strip(context, strip)
                finally:
                    context.window_manager.progress_update(1)
                    context.window_manager.progress_end()

                if self._state == 'QUIT':
                    return

        self.report({'INFO'}, 'Thumbnail uploaded to Attract')
        self.quit()

    @staticmethod
    def strip_contains(strip, framenr: int) -> bool:
        """Returns True iff the strip covers the given frame number"""
        return strip.frame_final_start <= framenr <= strip.frame_final_end

    @staticmethod
    def set_middle_frame(context, strip):
        """Sets the current frame to the middle frame of the strip."""

        middle = round((strip.frame_final_start + strip.frame_final_end) / 2)
        context.scene.frame_set(middle)

    @staticmethod
    def by_frame(sequence_strip) -> int:
        """Returns the start frame number of the sequence strip.

        This can be used for sorting strips by time.
        """

        return sequence_strip.frame_final_start

    async def thumbnail_strip(self, context, strip):
        atc_object_id = getattr(strip, 'atc_object_id', None)
        if not atc_object_id:
            self.report({'ERROR'}, 'Strip %s not set up for Attract' % strip.name)
            self.quit()
            return

        with self.thumbnail_render_settings(context):
            bpy.ops.render.render()
        file_id = await self.upload_via_tempdir(bpy.data.images['Render Result'],
                                                'attract_shot_thumbnail.jpg')

        if file_id is None:
            self.quit()
            return

        # Update the shot to include this file as the picture.
        node = pillarsdk.Node({'_id': atc_object_id})
        await pillar.pillar_call(
            node.patch,
            {
                'op': 'from-blender',
                '$set': {
                    'picture': file_id,
                }
            })

    async def upload_via_tempdir(self, datablock, filename_on_cloud) -> pillarsdk.Node:
        """Saves the datablock to file, and uploads it to the cloud.

        Saving is done to a temporary directory, which is removed afterwards.

        Returns the node.
        """
        import tempfile
        import os.path

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, filename_on_cloud)
            self.log.debug('Saving %s to %s', datablock, filepath)
            datablock.save_render(filepath)
            return await self.upload_file(filepath)

    async def upload_file(self, filename: str, fileobj=None):
        """Uploads a file to the cloud, attached to the image sharing node.

        Returns the node.
        """
        from .. import blender

        prefs = blender.preferences()
        project = self.find_project(prefs.project.project)

        self.log.info('Uploading file %s', filename)
        resp = await pillar.pillar_call(
            pillarsdk.File.upload_to_project,
            project['_id'],
            'image/jpeg',
            filename,
            fileobj=fileobj)

        self.log.debug('Returned data: %s', resp)
        try:
            file_id = resp['file_id']
        except KeyError:
            self.log.error('Upload did not succeed, response: %s', resp)
            self.report({'ERROR'}, 'Unable to upload thumbnail to Attract: %s' % resp)
            return None

        self.log.info('Created file %s', file_id)
        self.report({'INFO'}, 'File succesfully uploaded to the cloud!')

        return file_id


class ATTRACT_OT_copy_id_to_clipboard(AttractOperatorMixin, Operator):
    bl_idname = 'attract.copy_id_to_clipboard'
    bl_label = 'Copy shot ID to clipboard'

    @classmethod
    def poll(cls, context):
        return AttractOperatorMixin.poll(context) and \
               bool(context.selected_sequences and active_strip(context))

    def execute(self, context):
        strip = active_strip(context)

        context.window_manager.clipboard = strip.atc_object_id
        self.report({'INFO'}, 'Shot ID %s copied to clipboard' % strip.atc_object_id)

        return {'FINISHED'}


def draw_strip_movie_meta(self, context):
    strip = active_strip(context)
    if not strip:
        return

    meta = strip.get('metadata', None)
    if not meta:
        return None

    box = self.layout.column(align=True)
    row = box.row(align=True)
    fname = meta.get('BLEND_FILE', None) or None
    if fname:
        row.label('Original Blendfile: %s' % fname)
        row.operator(ATTRACT_OT_open_meta_blendfile.bl_idname,
                     text='', icon='FILE_BLEND')
    sfra = meta.get('START_FRAME', '?')
    efra = meta.get('END_FRAME', '?')
    box.label('Original Frame Range: %s-%s' % (sfra, efra))


def activate():
    global attract_is_active

    log.info('Activating Attract')
    attract_is_active = True
    bpy.app.handlers.scene_update_post.append(scene_update_post_handler)
    draw.callback_enable()


def deactivate():
    global attract_is_active

    log.info('Deactivating Attract')
    attract_is_active = False
    draw.callback_disable()

    try:
        bpy.app.handlers.scene_update_post.remove(scene_update_post_handler)
    except ValueError:
        # This is thrown when scene_update_post_handler does not exist in the handler list.
        pass


def register():
    bpy.types.Sequence.atc_is_synced = bpy.props.BoolProperty(name="Is Synced")
    bpy.types.Sequence.atc_object_id = bpy.props.StringProperty(name="Attract Object ID")
    bpy.types.Sequence.atc_object_id_conflict = bpy.props.BoolProperty(
        name='Object ID Conflict',
        description='Attract Object ID used multiple times',
        default=False)
    bpy.types.Sequence.atc_name = bpy.props.StringProperty(name="Shot Name")
    bpy.types.Sequence.atc_description = bpy.props.StringProperty(name="Shot Description")
    bpy.types.Sequence.atc_notes = bpy.props.StringProperty(name="Shot Notes")

    # TODO: get this from the project's node type definition.
    bpy.types.Sequence.atc_status = bpy.props.EnumProperty(
        items=[
            ('on_hold', 'On Hold', 'The shot is on hold'),
            ('todo', 'Todo', 'Waiting'),
            ('in_progress', 'In Progress', 'The show has been assigned'),
            ('review', 'Review', ''),
            ('final', 'Final', ''),
        ],
        name="Status")
    bpy.types.Sequence.atc_order = bpy.props.IntProperty(name="Order")

    bpy.types.SEQUENCER_PT_edit.append(draw_strip_movie_meta)

    bpy.utils.register_class(AttractToolsPanel)
    bpy.utils.register_class(AttractShotRelink)
    bpy.utils.register_class(AttractShotDelete)
    bpy.utils.register_class(AttractStripUnlink)
    bpy.utils.register_class(AttractShotFetchUpdate)
    bpy.utils.register_class(AttractShotSubmitSelected)
    bpy.utils.register_class(ATTRACT_OT_submit_all)
    bpy.utils.register_class(ATTRACT_OT_open_meta_blendfile)
    bpy.utils.register_class(ATTRACT_OT_shot_open_in_browser)
    bpy.utils.register_class(ATTRACT_OT_make_shot_thumbnail)
    bpy.utils.register_class(ATTRACT_OT_copy_id_to_clipboard)


def unregister():
    deactivate()
    bpy.utils.unregister_module(__name__)
    del bpy.types.Sequence.atc_is_synced
    del bpy.types.Sequence.atc_object_id
    del bpy.types.Sequence.atc_object_id_conflict
    del bpy.types.Sequence.atc_name
    del bpy.types.Sequence.atc_description
    del bpy.types.Sequence.atc_notes
    del bpy.types.Sequence.atc_status
    del bpy.types.Sequence.atc_order
