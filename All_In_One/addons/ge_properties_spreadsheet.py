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

# <pep8 compliant>

bl_info = { 
    "name": "Material Physics Properties Panel",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 6, 9),
    "location": "World context in Properties Editor",
    "description": "Display Material Physics Properties in a spreadsheet for quick editing",
    "warning": "",
    "category": "Learnbgame"
}

"""Display Material Physics Properties in a spreadsheet for quick editing"""

import bpy
from bpy.types import Panel
from bl_ui.properties_game import WorldButtonsPanel

from bpy.props import FloatProperty, StringProperty, BoolProperty

def copy_prop_to_objects(self, context):
    for object in bpy.data.groups['GameObjects'].objects:
        if self.is_material_prop:
            material = object.path_resolve('active_material')
            inner, leaf = self.prop.split('.')
            physics = material.path_resolve(inner)
            setattr(physics, leaf, self.prop_value)
        else:
            prop, attr = self.prop.split('.')
            data_path = eval('object.' + prop)
            setattr(data_path, attr, self.prop_value)

class NoOp(bpy.types.Operator):
    bl_idname = 'object.no_op'
    bl_label = ""
    bl_description = ""
    bl_options = {'MACRO', 'INTERNAL'}
    
    def invoke(self, context, event):
        return {'FINISHED'}

class CopyPropertyOperator(bpy.types.Operator):
    bl_idname = "object.copy_prop"
    bl_label = "Copy property"
    bl_description = "Copy property from active object to other objects"
    bl_options = {'UNDO', 'MACRO'}

    # Control the visibility of this operator
    @classmethod
    def poll(cls, context):
        is_properties_space_type = (context.space_data.type == 'PROPERTIES')
        only_one_selection = (context.selected_objects and len(context.selected_objects) == 1)
        return is_properties_space_type and only_one_selection

    # OperatorProperties
    # When laying out the operators in the panel, the following
    # Operator properties are set.
    # These properties are then used in 
    #      the invoke method
    #      the callback "copy_prop_to_objects"

    prop = StringProperty()
    is_material_prop = BoolProperty(default=False)
    prop_value = FloatProperty(name='', update=copy_prop_to_objects)

    # When the user clicks the column header, this method is invoked
    def invoke(self, context, event):
        object = context.selected_objects[0]
        if self.is_material_prop:
            material = object.path_resolve('active_material')
            inner, leaf = self.prop.split('.')
            physics = material.path_resolve(inner)
            self.prop_value = getattr(physics, leaf)
            return {'FINISHED'}
        else:
            self.prop_value = object.path_resolve(self.prop)
            return {'FINISHED'}            

class WORLD_PT_game_physics_materials(WorldButtonsPanel, Panel):
    bl_label = "Material Physics Properties"
    COMPAT_ENGINES = {'BLENDER_GAME'}  
    
    # The 'col' property is used to get access to the next
    # column while rendering rows
    @property
    def col(self):
        return next(self.columns)
    @col.setter
    def col(self, value):
        self.columns = iter(value)
        
    columnNames = ('Select','Name', 'Material', 'Mass', 'Friction', 'Elasticity', 'Bounds')
    
    def draw(self, context):
        layout = self.layout
        
        if ('GameObjects' not in bpy.data.groups) or \
           (('GameObjects' in bpy.data.groups) and bpy.data.groups['GameObjects'].objects == False):
            box = layout.column().box()
            box.label('Game objects must be part of the group called "GameObjects"')
            return 

        if 'toggle_material' not in context.scene:
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            row.prop(context.scene, '["toggle_material"]')
     
        split = layout.box().split(percentage=1/50, align=True)
        
        # We are going to save the column splits in this list, for later usage
        columns = []
        
        # Draw the HEADER ROW containing column names/operators
        
        for columnName in self.columnNames:
            column = split.column()
            row = column.row()
            row.alert = True
            if columnName == 'Mass':
                oper_props = row.operator('object.copy_prop', text=columnName, emboss=True)
                oper_props.prop = 'game.mass'
                oper_props.is_material_prop = False
            elif columnName == 'Bounds':
                oper_props = row.operator('object.copy_prop', text=columnName)
                oper_props.prop = 'game.radius'
                oper_props.is_material_prop = False
            elif columnName == 'Friction':
                oper_props = row.operator('object.copy_prop', text=columnName)
                oper_props.prop = 'physics.friction'
                oper_props.is_material_prop = True
            elif columnName == 'Elasticity':    
               oper_props = row.operator('object.copy_prop', text=columnName) 
               oper_props.prop = 'physics.elasticity'
               oper_props.is_material_prop = True
            else:
                row.alignment = 'EXPAND'
                row.operator("object.no_op", text=columnName)
            
            # We are going to refer to the following layouts when drawing the rows
            columns.append(column)
        
        objects = sorted(bpy.data.groups['GameObjects'].objects, key=lambda object: object.name)
        
        for object in objects:
            # Store all the columns in a property
            self.col = columns

            material_data_path = object.active_material

            self.col.prop(object, 'select', text='')
            self.col.prop(object, 'name', text = '', icon='OBJECT_DATA')

            column = self.col
            if material_data_path:
                if 'toggle_material' in context.scene and context.scene['toggle_material']:
                    column.template_ID(object, 'active_material', new='material.new')
                else:
                    column.prop(material_data_path, 'name', text='')
            else:
                column.template_ID(object, 'active_material', new='material.new')

            self.col.prop(object.game, 'mass', text = '', slider=True)

            column = self.col
            if material_data_path:
                args = (material_data_path.physics, 'friction')
                kwargs = {'text':'', 'slider': True}
                column.prop(*args, **kwargs)
            else:
                column.label('N/A')

            column = self.col
            if material_data_path:
                column.prop(material_data_path.physics, 'elasticity', text='')
            else:
                column.label('N/A')

            row = self.col.row(align=True)

            if object.game.use_collision_bounds:
                row.prop(object.game, 'collision_bounds_type', text = '')
            else:
                row.prop(object.game, 'radius', text = '')

            row.prop(object.game, 'use_collision_bounds', text='')

def register():
    bpy.utils.register_class(WORLD_PT_game_physics_materials)
    bpy.utils.register_class(CopyPropertyOperator)
    bpy.utils.register_class(NoOp)

def unregister():
    bpy.utils.unregister_class(WORLD_PT_game_physics_materials)
    bpy.utils.unregister_class(CopyPropertyOperator)
    bpy.utils.unregister_class(NoOp)
    
if __name__ == '__main__':
    register()