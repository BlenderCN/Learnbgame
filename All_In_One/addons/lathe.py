# -*- coding: utf-8 -*-

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

bl_info = {
    "name": "lathe",
    "author": "Laurent Laget",
    "version": (0, 9,3),
    "blender": (2, 78, 0),
    "location": "Add > Mesh",
    "description": "Create a lathe",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
    }

import bpy

def main(context):
    for ob in context.scene.objects:
        print(ob)

#Define functions for modifiers stack
def modifierstack():
        #create screw modifier and setup
        bpy.ops.object.modifier_add(type='SCREW')
        bpy.context.object.modifiers["Screw"].steps = 64
        bpy.context.object.modifiers["Screw"].render_steps = 64
        bpy.context.object.modifiers["Screw"].use_normal_flip = True

        #create solidify modifier and setup
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 0.1

        #create edgesplit modifier and setup
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.context.object.modifiers["EdgeSplit"].show_viewport = False
        bpy.context.object.modifiers["EdgeSplit"].show_render = False

#classe lathe
class lathe(bpy.types.Operator):
    """Create a lathe object"""
    bl_idname = "object.lathe"
    bl_label = "Lathe"
    bl_options = {'REGISTER', 'UNDO'}
   

    def invoke(self, context, event):
        
        #init front view, create a cube, name it, toggle edit mode and delete all to start from scratch
        bpy.ops.view3d.viewnumpad(type='FRONT')
        bpy.ops.mesh.primitive_cube_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = "Lathe"
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.delete(type='VERT')
        
        #create first vertex at cursor
        bpy.ops.mesh.primitive_vert_add()
        
        modifierstack()
        bpy.context.object.modifiers["Screw"].use_normal_calculate = True

        return {'FINISHED'}

#classe lathe_libre
class lathe_libre(bpy.types.Operator):
    """Create a lathe object with free draw"""
    bl_idname = "object.lathe_libre"
    bl_label = "Lathe_libre"
    bl_options = {'REGISTER', 'UNDO'}
   
    def invoke(self, context, event):
        
        #init front view, create a curve, name it, toggle edit mode and delete all to start from scratch
        bpy.ops.view3d.viewnumpad(type='FRONT')
        bpy.ops.curve.primitive_bezier_curve_add(view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = "Lathe_libre"
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.delete(type='VERT')
        
        modifierstack()

        return {'FINISHED'}

#definition of the names and operators 
def menu_item(self, context):
       self.layout.operator(lathe.bl_idname, text="lathe", icon="PLUGIN")
       self.layout.operator(lathe_libre.bl_idname, text="lathe_libre", icon="PLUGIN")

#add the names and operators to mesh add menu
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_item)

#Unregister the names and operators from mesh add menu
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_item)

if __name__ == "__main__":
    register()
