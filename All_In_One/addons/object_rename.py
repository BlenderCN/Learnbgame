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
    'name': 'Object Rename',
    'author': 'Oscurart, meta-androcto',
    'version': (0,1),
    'blender': (2, 5, 9),
    'api': 39685,
    'location': 'ToolShelf',
    'warning': '',
    'description': 'Rename Selected objects',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/' \
        'Scripts/Object/Object_Rename',
    'tracker_url': 'https://projects.blender.org/tracker/index.php?'\
        'func=detail&aid=21681&group_id=153&atid=468',
    'category': 'Object'}

import bpy
import math
import sys

class ReNameTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Object Rename"


    def draw(self, context):
        active_obj = context.active_object
        layout = self.layout        
        col = layout.column(align=0)
        row = col.row()

        col.label("Rename tools:")   
        row = col.row(align=1)
        row.prop(bpy.context.scene,"RenameObject")
        row = col.row(align=1) 
        row.operator("object.rnm",icon="SHORTDISPLAY") 
        
        col.label("Select tools:")   
        row = col.row(align=1)                      
        row.prop(bpy.context.scene,"SearchSelect")
        row = col.row(align=1) 
        row.operator("object.sas",icon="ZOOM_SELECTED")
		

##------------------------ SEARCH AND SELECT ------------------------

## SETEO VARIABLE DE ENTORNO
bpy.types.Scene.SearchSelect = bpy.props.StringProperty(default="Type Here")


class SearchAndSelect(bpy.types.Operator):
    bl_idname = "object.sas"
    bl_label = "Search & Select"
    def execute(self, context): 
        for objeto in bpy.context.scene.objects:
            variableNombre = bpy.context.scene.SearchSelect
            if objeto.name.startswith(variableNombre) == True :
                objeto.select = 1
                print("Selecciona:" + str(objeto.name))
        return{"FINISHED"}

##-------------------------RENAME OBJECTS----------------------------------    

## CREO VARIABLE
bpy.types.Scene.RenameObject = bpy.props.StringProperty(default="Type here")

class renameObjects (bpy.types.Operator):
    bl_idname = "object.rnm"
    bl_label = "Rename Objects" 
    def execute(self,context):

        ## LISTA
        listaObj = bpy.context.selected_objects
        
        
        
        for objeto in listaObj:
            print (objeto.name)
            objeto.name = bpy.context.scene.RenameObject
        return{"FINISHED"}


def register():
    bpy.utils.register_module(__name__)
    pass


def unregister():
    bpy.utils.unregister_module(__name__)
    pass


if __name__ == "__main__":
    register()
