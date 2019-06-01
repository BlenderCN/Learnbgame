bl_info = {
    "name": "Multikey",
    "author": "Tal Hershkovich ",
    "version": (0, 2),
    "blender": (2, 78, 0),
    "location": "View3D > Tool Shelf > Animation > Multikey",
    "description": "Edit Multiply Keyframes by adjusting their value or randomizing it",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Animation/Multikey",
    "category": "Learnbgame",
}

import bpy
import random


    

def check_selected_bones(obj):
    if  bpy.context.scene.selectedbones == True:
            bonelist = []
            for knochen in obj.pose.bones:
                if knochen.bone.select == True:
                    bonelist.append(knochen)
            #bpy.context.selected_pose_bones
    else:
        bonelist = obj.pose.bones
    return bonelist
        
def add_value(key, value):
    if key.select_control_point == True:
            #store handle_type 
            handle_r_type = key.handle_right_type
            handle_l_type = key.handle_left_type               
            
            key.co[1] += value
            if bpy.context.scene.handletype == True:
                key.handle_right_type = handle_r_type
                key.handle_left_type = handle_l_type
            else:
                key.handle_right_type = "AUTO_CLAMPED"
                key.handle_left_type = "AUTO_CLAMPED"
                
#calculate the difference between current value and the fcurve value                
def add_diff(fcu, current_value, index):    
    value = current_value[index] - fcu.evaluate(bpy.context.scene.frame_current)
    if value != 0:
        for key in fcu.keyframe_points:
            add_value(key, value)
        fcu.update()
    
def random_value(fcu):
    value_list = []
    threshold = bpy.context.scene.threshold                        
    #create an average value from selected keyframes
    for key in fcu.keyframe_points: 
        if key.select_control_point == True: #and fcu.data_path.find('rotation') == -1:
            value_list.append(key.co[1])
            
    if len(value_list) > 0:
        value = max(value_list)- min(value_list)
        for key in fcu.keyframe_points:
            add_value(key, value * random.uniform(-threshold, threshold))
        fcu.update()
                                
                                
def randomize(self, context):
    
    #threshold = bpy.context.scene.threshold
    
    objects = bpy.context.selected_objects
    
    for obj in objects:
    
        if obj.animation_data.action is not None:
            action = obj.animation_data.action
            for fcu in action.fcurves:
                if obj.type == 'ARMATURE':
                    bonelist = check_selected_bones(obj) 
                    for bone in bonelist:
                        #find the fcurve of the bone
                        if fcu.data_path.rfind(bone.name) == 12 and fcu.data_path[12 + len(bone.name)] == '"':
                            random_value(fcu)                              
                else:
                    random_value(fcu)
            
def evaluate_value(self, context):
    
    for obj in bpy.context.selected_objects:
        
        if obj.animation_data.action is not None:
            action = obj.animation_data.action
            
            for fcu in action.fcurves:     
                index = fcu.array_index
                if obj.type == 'ARMATURE':
                    transformations = ["rotation_quaternion","rotation_euler", "location", "scale"]
                    
                    #add value to the whole armature keyframes
                    if fcu.data_path[0:18] in transformations:
                        current_value = getattr(obj, fcu.data_path)
                        add_diff(fcu, current_value, index)     
                    
                    #add value to bones
                    bonelist = check_selected_bones(obj)
                    for bone in bonelist:
                        
                        #find the fcurve of the bone
                        if fcu.data_path.rfind(bone.name) == 12 and fcu.data_path[12 + len(bone.name)] == '"': 
                            transform = fcu.data_path[15 + len(bone.name):]
                            if transform in transformations:
                                current_value = getattr(obj.pose.bones[bone.name], transform)
                                #calculate the difference between current value and the fcurve value 
                                add_diff(fcu, current_value, index)
                                
             
                else:
                    transform = fcu.data_path
                    current_value = getattr(obj, transform)
                    
                    add_diff(fcu, current_value, index)
                                                    
class RandomizeKeys(bpy.types.Operator):
    """Create Random Keys"""
    bl_label = "Randomize keyframes"
    bl_idname = "fcurves.random"
    bl_options = {'REGISTER', 'UNDO'}  
    
    bpy.types.Scene.threshold = bpy.props.FloatProperty(name="threshold", description="Threshold of keyframes", default=0.1, min=0.0, max = 1.0)
      
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.animation_data
      
    def execute(self, context):
        randomize(self, context)
        return {'FINISHED'} 
                                   
class Multikey(bpy.types.Operator):
    """Edit all selected keyframes"""
    bl_label = "Edit Selected Keyframes"
    bl_idname = "fcurves.multikey"
    bl_options = {'REGISTER', 'UNDO'}  
    
    bpy.types.Scene.selectedbones = bpy.props.BoolProperty(name="Affect only selected bones", description="Affect only selected bones", default=True, options={'HIDDEN'})
    
    bpy.types.Scene.handletype = bpy.props.BoolProperty(name="Keep handle types", description="Keep handle types", default=False, options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.animation_data and bpy.context.scene.tool_settings.use_keyframe_insert_auto == False
      
    def execute(self, context):
        evaluate_value(self, context)
        return {'FINISHED'} 
    
class Multikey_Panel(bpy.types.Panel):
    """Add random value to selected keyframes"""
    bl_label = "Multikey"
    bl_idname = "fcurves.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Animation"
    
    def draw(self, context): 
        layout = self.layout
        layout.prop(context.scene, 'selectedbones')
        layout.prop(context.scene, 'handletype') 
        layout.separator()
        layout.label(text="Edit all selected keyframes")
        layout.operator("fcurves.multikey")
        layout.separator()
        layout.label(text="Randomize selected keyframes")
        layout.operator("fcurves.random")
        layout.prop(context.scene, 'threshold', slider = True)       

def register():
    bpy.utils.register_class(Multikey)
    bpy.utils.register_class(RandomizeKeys)
    bpy.utils.register_class(Multikey_Panel)

def unregister():
    bpy.utils.unregister_class(Multikey)
    bpy.utils.register_class(RandomizeKeys)
    bpy.utils.unregister_class(Multikey_Panel)

if __name__ == "__main__":
    register()                               