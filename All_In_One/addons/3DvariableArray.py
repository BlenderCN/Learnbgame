bl_info = {
    "name": "3D Cloner Array",
    "category": "Object",
}

import bpy
from bpy import *

class VarArray(bpy.types.Operator):
    bl_idname = "object.mograph_array"
    bl_label = "Creaate Array"
    bl_options = {'REGISTER', 'UNDO'}
    
    scn = context.window_manager

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
       
        obj = scene.objects.active

        for i in range(bpy.context.window_manager.num[0]):
            factor_x = i / bpy.context.window_manager.num[0]
          
            for j in range(bpy.context.window_manager.num[1]):
                factor_y=j/bpy.context.window_manager.num[1]
                
                for k in range(bpy.context.window_manager.num[2]):
                    factor_z=k/bpy.context.window_manager.num[2]
                    
                    obj_new = obj.copy()
                    scene.objects.link(obj_new)
                    
                    obj_new.location = obj.location 
                    obj_new.location.x += context.window_manager.Space[0]*factor_x
                    obj_new.location.y += context.window_manager.Space[1]*factor_y
                    obj_new.location.z += context.window_manager.Space[2]*factor_z

        return {'FINISHED'}
    
    
class ArrayPanel(bpy.types.Panel):
    bl_label = "MoGraph: 3D Array Cloner"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        scn = context.window_manager
        
        layout = self.layout

        obj = context.object
        
        row = layout.row()
        row.prop(scn, "num")
        
        row=layout.row()
        row.prop(scn, "Space")
        
        row = layout.row()
        row.operator("object.mograph_array")

def menu_func(self, context):
    self.layout.operator(VarArray.bl_idname)

def register():
    bpy.utils.register_class(VarArray)
    bpy.utils.register_class(ArrayPanel)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(VarArray)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(ArrayPanel)

if __name__ == "__main__":
    bpy.types.WindowManager.num = bpy.props.IntVectorProperty(name="EDGE:", description = "Number of Cloner Objects to be created on an edge", default = (1,1,1))
    bpy.types.WindowManager.Space = bpy.props.FloatVectorProperty(name="Spacing")

    register()