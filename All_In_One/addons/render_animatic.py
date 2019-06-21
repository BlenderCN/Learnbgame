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

import bpy
from os import path

bl_info = {
    "name": "Render Animatic",
    "description": "Render only keyframes or only frames pointed to by markers",
    "author": "IRIE Shinsuke",
    "version": (0, 3, 0),
    "blender": (2, 80, 0),  # or (2, 79, 0)
    "location": "Topbar > Render > Render Animatic",
    "tracker_url": "https://github.com/iRi-E/blender_render_animatic/issues",
    "category": "Learnbgame",
}

blender28 = bpy.app.version[0] == 2 and bpy.app.version[1] >= 80 or bpy.app.version[0] >= 3


# utility functions
def collect_keyframes(scene, start, end):
    """Return a list of keyframes visible in the timeline within given frame range"""
    from contextlib import redirect_stdout
    import io

    frames = []
    orig_frame = scene.frame_current
    scene.frame_set(end + 1)

    with redirect_stdout(io.StringIO()):
        while 'FINISHED' in bpy.ops.screen.keyframe_jump(next=False) and scene.frame_current >= start:
            frames.insert(0, scene.frame_current)

    scene.frame_set(orig_frame)
    return frames


def collect_markers(scene, start, end):
    """Return a list of frames pointed to by markers within given frame range"""
    return sorted(set(marker.frame for marker in scene.timeline_markers if start <= marker.frame <= end))


def is_v3d_persp_camera(context):
    """Return True if the current 3D view uses scene camera or the screen has no 3D view"""
    v3d = None
    size = 0

    for area in context.screen.areas:
        if area.type == 'VIEW_3D' and area.width * area.height > size:
            v3d = area
            size = area.width * area.height

    return v3d is None or v3d.spaces[0].camera and v3d.spaces[0].region_3d.view_perspective == 'CAMERA'


# operator
class RENDER_OT_render_animatic(bpy.types.Operator):
    """Render only keyframes or only frames pointed to by markers"""
    bl_idname = "render.render_animatic"
    bl_label = "Render Animatic"
    bl_options = {'REGISTER'}

    filter_type = bpy.props.EnumProperty(
        name="Filter Type",
        description="How to pick frames to render",
        items=[
            ('STEP', "Step",
             "Use constant frame steps same as the regular animation render",
             'CENTER_ONLY' if blender28 else 'ALIGN', 0),
            ('KEYFRAME', "Keyframes",
             "Render only keyframes visible in the current timeline",
             'KEYFRAME_HLT' if blender28 else 'SPACE2', 1),
            ('MARKER', "Markers",
             "Render only frames pointed to by markers",
             'MARKER_HLT', 2)],
        default='KEYFRAME'
        )

    use_opengl = bpy.props.BoolProperty(
        name="Viewport Render",
        description="Use the viewport render instead of the actual rendering engine",
        default=False
        )

    use_both_ends = bpy.props.BoolProperty(
        name="In and Out Points",
        description="Write the start and end frames of the rendering range as well",
        default=False
        )

    use_duplication = bpy.props.BoolProperty(
        name="Frame Duplication",
        description="Copy rendered frames to fill gaps in the image sequence",
        default=False
        )

    use_view_context = bpy.props.BoolProperty(
        name="View Context",
        description="Take snapshots of the active viewport instead of the current scene",
        default=False
        )

    def __init__(self):
        self.orig_frame = 1
        self.orig_output_path = "/tmp/"
        self.frame_current = 1
        self.frames = []
        self.num_rendered = 0
        self.num_copied = 0
        self.rendering = False
        self.started = False
        self.cancelled = False
        self.error = None
        self.timer = None
        self.retry = False
        self.view_suffixes = []

    # internal functions
    def timer_unset(self, context):
        if self.timer:
            context.window_manager.event_timer_remove(self.timer)
            self.timer = None

    def timer_set(self, context):
        self.timer_unset(context)
        self.timer = bpy.context.window_manager.event_timer_add(0.01, window=context.window)

    def duplicate_image(self, scene):
        if self.use_duplication and self.frames:
            from shutil import copyfile

            base_src, ext_src = path.splitext(scene.render.filepath)
            scene.render.filepath = self.orig_output_path

            for dest in range(self.frame_current + 1, self.frames[0]):
                base_dest, ext_dest = path.splitext(scene.render.frame_path(frame=dest))

                for suffix in self.view_suffixes or ['']:
                    path_src = base_src + suffix + ext_src
                    path_dest = base_dest + suffix + ext_dest

                    if scene.render.use_overwrite or not path.isfile(path_dest):
                        try:
                            copyfile(path_src, path_dest)
                        except OSError:
                            self.error = "Failed to copy image to \"{}\"".format(path_dest)
                            return

                        self.num_copied += 1
                        print("Copied '{}' -> '{}'".format(path_src, path_dest))
                    else:
                        print("skipping existing frame \"{}\"".format(path_dest))

    # callbacks
    def render_start(self, dummy):
        self.started = True

    def render_end(self, scene):
        if self.started:
            self.num_rendered += 1
            self.duplicate_image(scene)
        else:
            self.error = "Failed to start rendering"

        self.rendering = False

    def render_cancel(self, dummy):
        self.rendering = False
        self.cancelled = True

    # methods
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "filter_type", expand=True)
        layout.separator()

        col = layout.column()
        col.prop(self, "use_opengl", icon='VIEW3D')
        col.prop(self, "use_both_ends", icon='TRACKING_FORWARDS_SINGLE' if blender28 else 'OUTLINER_DATA_ARMATURE')
        col.prop(self, "use_duplication", icon='DUPLICATE' if blender28 else 'GHOST')

        col = layout.column()
        col.active = self.use_opengl
        col.prop(self, "use_view_context", icon='RESTRICT_VIEW_OFF')
        layout.separator()

    def execute(self, context):
        scene = context.scene

        if scene.render.is_movie_format:
            error = "Movie formats are not supported"
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        self.orig_frame = scene.frame_current
        self.orig_output_path = scene.render.filepath

        if scene.use_preview_range and self.use_opengl:
            start = scene.frame_preview_start
            end = scene.frame_preview_end
        else:
            start = scene.frame_start
            end = scene.frame_end

        if self.filter_type == 'STEP':
            self.frames = list(range(start, end + 1, scene.frame_step))
        elif self.filter_type == 'KEYFRAME':
            self.frames = collect_keyframes(scene, start, end)
        elif self.filter_type == 'MARKER':
            self.frames = collect_markers(scene, start, end)

        if not self.frames:
            info = "There is no frame to render"
            self.report({'INFO'}, info)
            return {'CANCELLED'}

        if self.use_both_ends:
            if self.frames[0] > start:
                self.frames.insert(0, start)
            if self.use_duplication:
                end += 1  # last frame won't be rendered, it will be used only for frame duplication ... (1)
            if self.frames[-1] < end:
                self.frames.append(end)

        if self.use_duplication and scene.render.use_multiview:
            # if not self.use_opengl or not self.use_view_context or is_v3d_persp_camera(context):
            if not self.use_opengl or self.use_view_context and is_v3d_persp_camera(context):  # workaround T58517
                views = scene.render.views[:2 if scene.render.views_format == 'STEREO_3D' else None]
                self.view_suffixes = [view.file_suffix for view in views if view.use]
            print("Multiview file suffixes: {}".format(self.view_suffixes))

        if not self.use_opengl:
            bpy.app.handlers.render_pre.append(self.render_start)
            bpy.app.handlers.render_complete.append(self.render_end)
            bpy.app.handlers.render_cancel.append(self.render_cancel)

        self.timer_set(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            self.cancelled = True
        elif self.rendering or event.type != 'TIMER':
            return {'PASS_THROUGH'}

        scene = context.scene

        if not self.cancelled:
            while (self.frames or self.retry) and not self.error:
                if not self.retry:
                    self.frame_current = self.frames.pop(0)
                    if not self.frames and self.use_both_ends and self.use_duplication:
                        break  # don't render end + 1 frame which was added in (1) above

                scene.frame_set(self.frame_current)
                scene.render.filepath = self.orig_output_path
                path_frame = scene.render.frame_path()
                scene.render.filepath = path_frame

                if scene.render.use_overwrite or not path.isfile(path_frame):
                    if self.use_opengl:
                        try:
                            bpy.ops.render.opengl(write_still=True, view_context=self.use_view_context)
                        except RuntimeError as e:
                            self.error = e.args[0]
                            break

                        self.num_rendered += 1
                        self.duplicate_image(scene)
                        if self.error:
                            break  # error occurred in duplicate_image()
                    else:
                        try:
                            status = bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
                        except RuntimeError as e:
                            self.error = e.args[0]
                            break

                        self.retry = 'CANCELLED' in status  # cancelled if not ready to start new job
                        self.rendering = not self.retry
                        self.started = False

                    return {'RUNNING_MODAL'}

                print("skipping existing frame \"{}\"".format(path_frame))
                self.duplicate_image(scene)

        self.timer_unset(context)

        if not self.use_opengl:
            bpy.app.handlers.render_pre.remove(self.render_start)
            bpy.app.handlers.render_complete.remove(self.render_end)
            bpy.app.handlers.render_cancel.remove(self.render_cancel)

        scene.frame_set(self.orig_frame)
        scene.render.filepath = self.orig_output_path

        if self.error:
            self.report({'ERROR'}, self.error)
            return {'CANCELLED'}

        info = "Rendered {} frames".format(self.num_rendered)
        if self.use_duplication:
            info += " and copied {} frames".format(self.num_copied)
        self.report({'INFO'}, info)

        if self.cancelled:
            return {'CANCELLED'}

        return {'FINISHED'}


# user interface
def render_animatic_button(self, context):
    layout = self.layout
    layout.operator("render.render_animatic", text="Animatic", icon='RENDER_ANIMATION')


def render_animatic_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("render.render_animatic", icon='RENDER_ANIMATION')


# register addon
def register():
    bpy.utils.register_class(RENDER_OT_render_animatic)
    if blender28:
        bpy.types.TOPBAR_MT_render.append(render_animatic_menu)
        bpy.types.VIEW3D_MT_view.append(render_animatic_menu)
    else:
        bpy.types.INFO_MT_render.append(render_animatic_menu)
        bpy.types.VIEW3D_HT_header.append(render_animatic_button)


def unregister():
    bpy.utils.unregister_class(RENDER_OT_render_animatic)
    if blender28:
        bpy.types.TOPBAR_MT_render.remove(render_animatic_menu)
        bpy.types.VIEW3D_MT_view.remove(render_animatic_menu)
    else:
        bpy.types.INFO_MT_render.remove(render_animatic_menu)
        bpy.types.VIEW3D_HT_header.remove(render_animatic_button)


if __name__ == "__main__":
    register()
