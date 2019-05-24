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

bl_info = {
    "name": "Make Pillow",
    "author": "Mark C <BlendedMarks>",
    "version": (0,2),
    "blender": (2, 79, 0),
    "location": "View3D >Spacebar Menu",
    "description": "Generates a pillow",
    "warning": "Modifiers must be applied before scaling newly created pillow",
    "wiki_url": "https://blenderartists.org/forum/showthread.php?432659-MakePillow-py-Generate-a-pillow",
    "tracker_url": "https://blenderartists.org/forum/showthread.php?432659-MakePillow-py-Generate-a-pillow",
    "category": "Learnbgame",
}

import bpy

class MakePillow(bpy.types.Operator):
    """Make Pillows The Easy Way"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.make_pillow"        # unique identifier for buttons and menu items to reference.
    bl_label = "Make Pillow"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):        # execute() is called by blender when running the operator.

        # The original script
       scene = context.scene
       bpy.ops.object.effector_add(type='FORCE', radius=1.0, view_align=False, enter_editmode=False, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
       bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0), enter_editmode=True)
       bpy.ops.transform.resize(value=(1.0, 1.0, 0.2))
       bpy.ops.mesh.subdivide(number_cuts=10, smoothness=0.0, quadtri=False, quadcorner='STRAIGHT_CUT', fractal=0.0, fractal_along_normal=0.0, seed=0)
       bpy.ops.object.modifier_add(type='SUBSURF')
       bpy.ops.object.modifier_apply(apply_as='DATA')
       bpy.ops.object.mode_set(mode='OBJECT', toggle=True)
       bpy.ops.object.shade_smooth()
       bpy.ops.object.modifier_add(type='CLOTH')
       bpy.context.object.modifiers["Cloth"].settings.effector_weights.gravity = 0
       bpy.data.objects['Field'].select = True
       bpy.data.objects['Field'].field.strength = 200
       bpy.context.object.modifiers["Cloth"].settings.mass = 0.3
       bpy.ops.screen.frame_jump(end=False)
       bpy.ops.screen.animation_play()
       
       return {'FINISHED'}            # this lets blender know the operator finished successfully.

def register():
    bpy.utils.register_class(MakePillow)


def unregister():
    bpy.utils.unregister_class(MakePillow)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
	register()
