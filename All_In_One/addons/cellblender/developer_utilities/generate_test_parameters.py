"""
This program generates large numbers of model parameters for testing within CellBlender.
This addon should only be enabled after CellBlender is already enabled.
"""

bl_info = {
  "version": "0.1",
  "name": "Test Parameters",
  'author': 'Bob Kuczewski',
  "location": "Properties > Scene",
  "category": "Learnbgame",
  "description": "Generates user-selected number of model parameters for testing within CellBlender."
  }

import bpy
from bpy.props import *
import cellblender


class TestParamsPropertyGroup(bpy.types.PropertyGroup):
    next_num = IntProperty(name='Next Parameter Number',default=1)
    num_to_add = IntProperty(name='Number to Add',default=1)
    def draw(self, context, panel):
        app = context.scene.test_params
        layout = panel.layout
        row = layout.row()
        col = row.column()
        col.prop(self,"next_num")
        col = row.column()
        col.prop(self,"num_to_add")
        row = layout.row()
        row.operator("app.add_params", text="Add Parameters")        
        row = layout.row()
        row.operator("app.delete_all_params", text="Delete All Unused Parameters")        
    


class APP_OT_add_params(bpy.types.Operator):
    bl_idname = "app.add_params"
    bl_label = "Add Parameters"
    bl_description = "Adds more general parameters to the list"
    bl_options = {'REGISTER'}

    def execute(self, context):
        app = context.scene.test_params
        mcell = context.scene.mcell
        for i in range(app.num_to_add):
            name = 'P'+str(app.next_num)
            expr = str(app.next_num)
            if (app.next_num) >= 10:
              expr = 'SQRT(2 * P'+str(1+(app.next_num%10))+')'
              #expr = 'SQRT(2 * P1)'
            mcell.parameter_system.add_general_parameter_with_values ( name, expr, 'sec', 'Test parameter ' + str(app.next_num) )
            app.next_num += 1
        return {'FINISHED'}


class APP_OT_delete_all_params(bpy.types.Operator):
    bl_idname = "app.delete_all_params"
    bl_label = "Delete All Unused Parameters"
    bl_description = "Attempts to delete all model parameters not used by others"
    bl_options = {'REGISTER'}

    def execute(self, context):
        app = context.scene.test_params
        mcell = context.scene.mcell
        
        for i in range(len(mcell.parameter_system.general_parameter_list)-1,-1,-1):
            mcell.parameter_system.active_par_index = i
            mcell.parameter_system.remove_active_parameter ( context )
        app.next_num = 1
        return {'FINISHED'}


class TestParams_PT_Explore_Props(bpy.types.Panel):
    bl_label = "Test Parameters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    def draw(self, context):
        context.scene.test_params.draw(context,self)


def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.test_params = bpy.props.PointerProperty(type=TestParamsPropertyGroup)

def unregister():
    print ("Unregistering ", __name__)
    del bpy.types.Scene.test_params
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()


