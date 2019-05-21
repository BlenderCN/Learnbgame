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

# <pep8-80 compliant>

bl_info = {
    "name": "Render Selected Frames",
    "author": "Agnieszka Pas",
    "version": (1, 1, 0),
    "blender": (2, 79, 0),
    "location": "Properties > Render",
    "warning": "",
    "description": "Render Selected Frames",
    "category": "Render",
}


import bpy
from bpy.types import Operator


class RenderSelectedFramesOperator(Operator):
    """Render Selected Frames"""
    bl_idname = "render.render_frames"
    bl_label = "Render Frames"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        path = scene.render.filepath
        scene.render.image_settings.file_format = 'PNG'
        frames_string = scene.NewSelectedFrames
        frames_list = []

        if frames_string == '':
            self.report({'WARNING'}, "Choose frames to render first")
            return {'CANCELLED'}
        else:
            splitted = frames_string.split(',')
            for s in splitted:
                if s.find('-') > -1:
                    range_ends = s.split('-')
                    start = int(range_ends[0])
                    end = int(range_ends[1])

                    for num in range(start,end):
                        frames_list.append(num)

                    frames_list.append(end)
                else:
                    if s.isdigit():
                        frames_list.append(int(s))

            for frame in frames_list:
                scene.frame_set(frame)
                scene.render.filepath = path + str(frame)
                bpy.ops.render.render(write_still=True)

            scene.render.filepath = path
            return {'FINISHED'}


def draw_render_frames(self, context):
    layout = self.layout
    col = layout.column()

    row = col.row()
    row.label("Selected Frames:")
    col.prop(context.scene, "NewSelectedFrames", text="")
    col.operator("render.render_frames")


def register():
    bpy.types.Scene.NewSelectedFrames = bpy.props.StringProperty(
        name="Frames",
        default="",
        description="Frames to render, for example: 1,3-5,8")
    bpy.utils.register_module(__name__)
    bpy.types.RENDER_PT_render.append(draw_render_frames)


def unregister():
    del bpy.types.Scene.NewSelectedFrames
    bpy.types.RENDER_PT_render.remove(draw_render_frames)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
