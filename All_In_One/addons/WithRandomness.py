bl_info = {
    "name": "3D Cloner Array",
    "category": "Object",
}

import bpy
from bpy import *
import random

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
                    
                    if (context.window_manager.RandomScale == True):
                        obj_new.scale.magnitude = (obj.scale.magnitude * 0.5) +(obj.scale.magnitude * random.random() * context.window_manager.RandomScaleVal)
                                               
                    if (context.window_manager.RandomRot == True):
                        if(context.window_manager.RandomRotX == True):
                            obj_new.rotation_euler.x = random.random() * context.window_manager.RandomRotVal
                        if(context.window_manager.RandomRotY == True):
                            obj_new.rotation_euler.y = random.random() * context.window_manager.RandomRotVal
                        if(context.window_manager.RandomRotZ == True):
                            obj_new.rotation_euler.z = random.random() * context.window_manager.RandomRotVal
                            
        
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
        row.prop(scn, "RandomRot")
        
        if(scn.RandomRot == True):
            row.prop(scn, "RandomRotVal")
            
            row=layout.row()
            row.prop(scn, "RandomRotX")
            row.prop(scn, "RandomRotY")
            row.prop(scn, "RandomRotZ")
            
        
        row = layout.row()
        row.prop(scn, "RandomScale")
           
        if(scn.RandomScale == True):
            row.prop(scn, "RandomScaleVal")
            
            
        
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
    bpy.types.WindowManager.RandomScale = bpy.props.BoolProperty(name="Random Scale", default=False)
    bpy.types.WindowManager.RandomRot = bpy.props.BoolProperty(name="Random Rotation", default=False)
    bpy.types.WindowManager.RandomScaleVal = bpy.props.FloatProperty(name="RandomScale", default=0.0)
    bpy.types.WindowManager.RandomRotVal = bpy.props.FloatProperty(name="RandomRotation", default=0.0)
    
    bpy.types.WindowManager.RandomRotX = bpy.props.BoolProperty(name="X", default=False)
    bpy.types.WindowManager.RandomRotY = bpy.props.BoolProperty(name="Y", default=False)
    bpy.types.WindowManager.RandomRotZ = bpy.props.BoolProperty(name="Z", default=False)
    
    register()
