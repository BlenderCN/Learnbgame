# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "RGBCMYW Material Creator",
    "description": "Creates RGBCMYW Materials for use as selection masks",
    "author": "Andy Davies (metalliandy)",
    "version": (0,1),
    "blender": (2, 6, 3),
    "api": 50372,
    "location": "Tool Shelf",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}
    
"""About this script:-
This script enables the fast creation of RGBCMYW Materials for use as selection masks during texturing.

Usage:-
1)Click the Make RGBCMYW Mats button on the Tool Shelf to activate the tool.
2)Assign the materials to your meshes.
2)Done! :)

Related Links:-

http://www.metalliandy.com

Thanks to:-


Version history:-
v0.1 - Initial revision."""

import bpy
  

def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.0
    mat.alpha = alpha
    mat.ambient = 1
    return mat
    
def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)


class OBJECT_OT_RGBCMYW(bpy.types.Operator):
    bl_idname = "materials.rgbcmyw"
    bl_label = "Make RGBCMYW Mats"
    
    def execute(self, context):
        # Create materials
        red = makeMaterial('Red', (1,0,0), (1,1,1), 1)
        green = makeMaterial('Green', (0,1,0), (1,1,1), 1)
        blue = makeMaterial('Blue', (0,0,1), (1,1,1), 1)
        cyan = makeMaterial('Cyan', (0,1,1), (1,1,1), 1)
        magenta = makeMaterial('Magenta', (1,0,1), (1,1,1), 1)
        yellow = makeMaterial('Yellow', (1,1,0), (1,1,1), 1)
        white = makeMaterial('White', (1,1,1), (1,1,1), 1)
         
        return{'FINISHED'}


class MakeRGBCMYWMaterialButton(bpy.types.Panel):
    bl_label = "RGBCMYW Mats"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("materials.rgbcmyw")


script_classes = [OBJECT_OT_RGBCMYW, MakeRGBCMYWMaterialButton]


def register():
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    

if __name__ == "__main__":
    register()