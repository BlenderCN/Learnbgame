'''
Copyright (C) 2016 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from math import radians,degrees
from mathutils import Vector,Quaternion,Euler

def get_prop_object(self,context,prop_name,obj):
    wm = context.window_manager
    
    data = obj.data
    bone = None
    shape_keys = None
    mat = obj.active_material
    tex = None
    modifier = None
    scene = context.scene
    render = scene.render
    
    if obj.type in ["MESH", "CURVE"] and obj.data.shape_keys != None:
        shape_keys = obj.data.shape_keys
                    
    if mat != None:
        tex = mat.active_texture
        
    
    ### return if property is found in modifier
    if len(obj.modifiers) > 0 and '"' in prop_name:
        modifier_name = prop_name.split('"')[1]
        if modifier_name in obj.modifiers:
            modifier = obj.modifiers[modifier_name]
            return modifier, "MODIFIER_PROPERTY"
        
    ### return if property is found in texture slots    
    if "texture_slots" in prop_name and "[" in prop_name:
        index = int ( prop_name[prop_name.find("[")+1:prop_name.find("]")])
        texture_slot = mat.texture_slots[index]
        return texture_slot, "TEXTURE_PROPERTY"
            
    
    ### return if property is found in shapekeys    
    if shape_keys != None and '"' in prop_name:
        shape_name = prop_name.split('"')[1]
        if shape_name in shape_keys.key_blocks:
            return shape_keys, "SHAPEKEY_PROPERTY"
    if hasattr(shape_keys,prop_name):
        return shape_keys, "SHAPEKEY_PROPERTY"
    
    
    ### return if property is found in bone constraint
    if '"' in prop_name:
        if len(prop_name.split('"')) > 3:
            bone_name = prop_name.split('"')[1]
            const_name = prop_name.split('"')[3]
            if hasattr(obj.pose,"bones") and bone_name in obj.pose.bones and const_name in obj.pose.bones[bone_name].constraints:
                return obj.pose.bones[bone_name].constraints[const_name], "BONE_CONSTRAINT_PROPERTY"
            
    ### return if property is found in bone
    if obj.type == "ARMATURE" and '"' in prop_name and "bones" in prop_name:
        
        if len(prop_name.split('"')) >= 3:
            bone_name = prop_name.split('"')[1]
            if bone_name in obj.data.bones:
                if prop_name.rfind("]") == len(prop_name)-1:
                    from_idx = prop_name.rfind("[")
                    to_idx = prop_name.rfind("]")+1
                    prop = prop_name[from_idx:to_idx]
                else:
                    from_idx = prop_name.rfind(".")+1
                    prop = prop_name[from_idx:]
                if hasattr(obj.data.bones[bone_name],prop):
                    bone = obj.data.bones[bone_name]
                    
                elif hasattr(obj.pose.bones[bone_name],prop):
                    bone = obj.pose.bones[bone_name]
                return bone, "BONE_PROPERTY"
                        
                    
        
    ### return if property is found in object    
    if hasattr(obj,prop_name):
        return obj, "OBJECT_PROPERTY"
    
    ### return if property is found in object data (armature, mesh)
    if hasattr(data,prop_name):
        return data, "OBECT_DATA_PROPERTY"
    
    ### return if property is found in material
    if mat != None and hasattr(mat,prop_name):
        return mat, "MATERIAL_PROPERTY"
        
    
    ### return if property is found in texture
    if tex != None and hasattr(tex,prop_name):
        return tex, "TEXTURE_PROPERTY"
    
    ### return if property is found in object constraint
    if '"' in prop_name and "constraint" in prop_name:
        if len(prop_name.split('"')) == 3:
            const_name = prop_name.split('"')[1]
            if const_name in obj.constraints:
                return obj.constraints[const_name], "OBJECT_CONSTRAINT_PROPERTY"

def get_action_length(action):
    action_length = 0
    for fcurve in action.fcurves:
        if len(fcurve.keyframe_points) > 0:
            length = fcurve.keyframe_points[len(fcurve.keyframe_points)-1].co[0]
            action_length = max(action_length,length)
    return action_length

class CreateDriverConstraint(bpy.types.Operator):
    #"""This Operator creates a driver for a shape and connects it to a posebone transformation"""
    bl_idname = "object.create_driver_constraint"
    bl_label = "Create Driver Constraint"
    bl_description = "This Operator creates a driver for a shape and connects it to a posebone transformation"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def check(self,context):
        return True
    
    def get_shapes(self,context):
        shapes = []
        i=0
        
        if len(context.selected_objects) > 1:
            obj = None
            for obj2 in context.selected_objects:
                if obj2 != context.scene.objects.active:
                    obj = obj2
                    break
        else:
            obj = context.selected_objects[0]
        shape_keys = None
        if obj.type in ["MESH","CURVE"] and obj.data.shape_keys != None:
            shape_keys = obj.data.shape_keys.key_blocks
              
        if shape_keys != None:
            for shape in shape_keys:
                if shape.relative_key != shape:
                    shapes.append((shape.name,shape.name,shape.name,'SHAPEKEY_DATA',i)) 
                    i+=1
        shapes.append(("CREATE_NEW_SHAPE","create new shape","create new shape",'NEW',i)) 
        
            
        return shapes
    
    def search_for_prop(self,context):
        wm = context.window_manager
        if hasattr(self,"property_type") and self.prop_data_path != "":
            if len(context.selected_objects) > 1:
                obj = None
                for obj2 in context.selected_objects:
                    if obj2 != context.scene.objects.active:
                        obj = obj2
                        break
            else:
                obj = context.selected_objects[0]
            
            if get_prop_object(self,context,self.prop_data_path,obj) != None:
                self.property_type = get_prop_object(self,context,self.prop_data_path,obj)[1]
            else:
                self.prop_data_path = ""    
 
    
    def get_actions(self,context):
        ACTIONS = []
        for i,action in enumerate(bpy.data.actions):
            ACTIONS.append((action.name,action.name,action.name,"ACTION",i))
        return ACTIONS
    
    def get_action_constraints(self,context):
        action_names = []
        ACTIONS = []
        i = 0
        for bone in context.selected_pose_bones:
            for const in bone.constraints:
                if const.name not in action_names:
                    action_names.append(const.name)
                    ACTIONS.append((const.name,const.name,const.name,"ACTION",i))
                    i += 1
        ACTIONS.append(("ALL_ACTIONS","All Actions","All Actions","ACTION",i))            
        return ACTIONS            
                    
    
    def get_property_type_items(self,context):
        if len(context.selected_objects) > 1:
            obj = None
            for obj2 in context.selected_objects:
                if obj2 != context.scene.objects.active:
                    obj = obj2
                    break
        else:
            obj = context.selected_objects[0]
        
        object_data_icon = "MESH_DATA"
        if obj.type == "ARMATURE":
            object_data_icon = "ARMATURE_DATA"
        
        items = []
        items.append(("OBJECT_PROPERTY","Object Property","Object Property","OBJECT_DATAMODE",0))
        if obj.type in ["MESH","CURVE"]:
            items.append(("SHAPEKEY_PROPERTY","Shapekey Property","Shapekey Property","SHAPEKEY_DATA",1))
            items.append(("MODIFIER_PROPERTY","Modifier Property","Modifier Property","MODIFIER",5))
        items.append(("OBECT_DATA_PROPERTY","Data Property","Data Property",object_data_icon,2))
        items.append(("MATERIAL_PROPERTY","Material Property","Material Property","MATERIAL",3))
        items.append(("TEXTURE_PROPERTY","Texture Property","Texture Property","TEXTURE",4))
        items.append(("BONE_PROPERTY","Bone Property","Bone Property","BONE_DATA",6))
        items.append(("BONE_CONSTRAINT_PROPERTY","Bone Constraint Property","Bone Constraint Property","CONSTRAINT_BONE",7))
        items.append(("OBJECT_CONSTRAINT_PROPERTY","Object Constraint Property","Object Constraint Property","CONSTRAINT",8))
        return items
    
    def driver_limits_flip(self,context):
        val1 = float(self.min_value)
        val2 = float(self.max_value)
        
        self.min_value = val2
        self.max_value = val1
    
    def property_limits_flip(self,context):
        val1 = float(self.prop_min_value)
        val2 = float(self.prop_max_value)
        
        self.prop_min_value = val2
        self.prop_max_value = val1    
    
    
    
    def get_animation_length(self,context):
        action = bpy.data.actions[self.action]
        self.action_frame_end = get_action_length(action)
    
    
    mode = bpy.props.EnumProperty(name="Operator Mode",items=(("DRIVER","Driver","Driver"),("ACTION","Action","Action")))
        
    property_type = bpy.props.EnumProperty(name = "Mode",items=get_property_type_items, description="Set the space the bone is transformed in. Local Space recommended.")
    
    prop_data_path = bpy.props.StringProperty(name="Property Data Path", default="",update=search_for_prop)
    
    shape_name = bpy.props.EnumProperty(items = get_shapes, name = "Shape", description="Select the shape you want to add a driver to.")
    get_limits_auto = bpy.props.BoolProperty(name = "Get Limits",default=True,description="This will set the limits based on the bone location/rotation/scale automatically.")
    
    
    int_type_values = []
    int_type_values.append(("LINEAR","Linear","Linear","IPO_LINEAR",0))
    int_type_values.append(("CONSTANT","Constant","Constant","IPO_CONSTANT",1))
    int_type_values.append(("BEZIER","Bezier","Bezier","IPO_BEZIER",2))
    interpolation_type = bpy.props.EnumProperty(name = "Interpolation Type",items=int_type_values, description="Defines the transition from one value to another.")
    
    type_values = []
    type_values.append(("LOC_X","X Location","X Location","None",0))
    type_values.append(("LOC_Y","Y Location","Y Location","None",1))
    type_values.append(("LOC_Z","Z Location","Z Location","None",2))
    type_values.append(("ROT_X","X Rotation","X Rotation","None",3))
    type_values.append(("ROT_Y","Y Rotation","Y Rotation","None",4))
    type_values.append(("ROT_Z","Z Rotation","Z Rotation","None",5))
    type_values.append(("SCALE_X","X Scale","X Scale","None",6))
    type_values.append(("SCALE_Y","Y Scale","Y Scale","None",7))
    type_values.append(("SCALE_Z","Z Scale","Z Scale","None",8))
    type = bpy.props.EnumProperty(name = "Type",items=type_values, description="Set the type you want to be used as input to drive the shapekey.")
    
    action = bpy.props.EnumProperty(name="Action",items=get_actions,description="Choose Action that will be driven by Bone",update=get_animation_length)
    action_constraint = bpy.props.EnumProperty(name="Action",items=get_action_constraints,description="Choose Action Constraint that will be deleted for selected bones.")
    action_mode = bpy.props.EnumProperty(name="Action",items=(("ADD_CONSTRAINT","Add Constraints","Add Constraints"),("DELETE_CONSTRAINT","Delete Constraints","Delete Constraints")),description="Delete or Add Action Constraints for selected bones.")
    
    space_values = []
    space_values.append(("LOCAL_SPACE","Local Space","Local Space","None",0))
    space_values.append(("TRANSFORM_SPACE","Transform Space","Transform Space","None",1))
    space_values.append(("WORLD_SPACE","World Space","World Space","None",2))
    space = bpy.props.EnumProperty(name = "Space",items=space_values, description="Set the space the bone is transformed in. Local Space recommended.")
    
    min_value = bpy.props.FloatProperty(name = "Min Value",default=0.0, description="That value is used as 0.0 value for the shapekey.")
    max_value = bpy.props.FloatProperty(name = "Max Value",default=1.0, description="That value is used as 1.0 value for the shapekey.")
    
    action_frame_start = bpy.props.IntProperty(name = "Min Value",default=0, description="Value where the animations is starting.")
    action_frame_end = bpy.props.IntProperty(name = "Max Value",default=10, description="Value where the animation is ending.")
    
    prop_min_value = bpy.props.FloatProperty(name = "Min Value",default=0.0, description="That value is used as 0.0 value for the Property.")
    prop_max_value = bpy.props.FloatProperty(name = "Max Value",default=1.0, description="That value is used as 1.0 value for the Property.")
    flip_driver_limits = bpy.props.BoolProperty(name = "Flip Driver Limits",default=False,description="This Bool Property flips the Driver Limits.",update=driver_limits_flip)
    flip_property_limits = bpy.props.BoolProperty(name = "Flip Property Limits",default=False,description="This Bool Property flips the Property Limits.",update=property_limits_flip)
    
    set_driver_limit_constraint = bpy.props.BoolProperty(name = "Set Driver limit Constraint",default=False,description="Set Driver Limit Constraint with given settings.")
    driver = None
    limit_type = None   
    
    def draw(self,context):
        if self.mode == "DRIVER":
            layout = self.layout
            
            row = layout.row()
            row.label(text="Property Type")
            row.prop(self,"property_type",text="")
            
            row = layout.row()
            row.label(text="Get Driver Limits")
            row.prop(self,"get_limits_auto",text="")
            
            row = layout.row()
            row.label(text="Set Driver Limits")
            row.prop(self,"set_driver_limit_constraint",text="")
            
            row = layout.row()
            row.label(text="Property Data Path")
            row.prop(self,"prop_data_path",text="")
            
            row = layout.row()
            row.label(text="Transform Type")
            row.prop(self,"type",text="")
            
            row = layout.row()
            row.label(text="Space")
            row.prop(self,"space",text="")
            
            row = layout.row()
            col = row.column()
            col.label(text="Driver Limits")
            
            row1 = row.row(align=True)
            row1.scale_x = 0.9
            col1 = row1.column(align=True)
            col1.prop(self,"min_value",text="Min Value")
            col1.prop(self,"max_value",text="Max Value")
            
            col2 = row1.column(align=True)
            col2.scale_y = 2.0
            col2.prop(self,"flip_driver_limits",text="",toggle=True,icon="ARROW_LEFTRIGHT")
            
            row = layout.row()
            row.label(text="Interpolation Type")
            row.prop(self,"interpolation_type",text="")
            
            row = layout.row()
            col = row.column()
            col.label(text="Property Limits")
            
            row1 = row.row(align=True)
            row1.scale_x = 0.9
            col1 = row1.column(align=True)
            col1.prop(self,"prop_min_value",text="Min Value")
            col1.prop(self,"prop_max_value",text="Max Value")
                
            col2 = row1.column(align=True)
            col2.scale_y = 2.0
            col2.prop(self,"flip_property_limits",text="",toggle=True,icon="ARROW_LEFTRIGHT")
        elif self.mode == "ACTION":
            layout = self.layout
            col = layout.row()
            col.prop(self,"action_mode",expand=True)
            if self.action_mode == "ADD_CONSTRAINT":
                col = layout.column()
                row = layout.row()
                row.label(text="Action")
                row.prop(self,"action",text="")
                
                
                row = layout.row()
                row.label(text="Transform Type")
                row.prop(self,"type",text="")
                
                row = layout.row()
                row.label(text="Space")
                row.prop(self,"space",text="")
                
                row = layout.row()
                col = row.column()
                col.label(text="Property Limits")
                
                
                row = layout.row()
                row1 = row.row(align=True)
                row1.scale_x = 0.9
                col1 = row1.column(align=True)
                col1.prop(self,"min_value",text="Min Value")
                col1.prop(self,"max_value",text="Max Value")
                
                row = layout.row()
                col = row.column()
                col.label(text="Action Range")
                
                row = layout.row()
                row1 = row.row(align=True)
                row1.scale_x = 0.9
                col1 = row1.column(align=True)
                col1.prop(self,"action_frame_start",text="Start")
                col1.prop(self,"action_frame_end",text="End")
            elif self.action_mode == "DELETE_CONSTRAINT":
                col = layout.column()
                row = layout.row()
                row.label(text="Action")
                row.prop(self,"action_constraint",text="")  
        
    
    def create_actions_constraints(self,context):
        if self.action_mode == "ADD_CONSTRAINT":
            for bone in context.selected_pose_bones:
                if context.active_pose_bone != bone:
#                    const = None
#                    for c in bone.constraints:
#                        if c.action.name == self.action:
#                            const = c
#                    if const == None:        
                    const = bone.constraints.new("ACTION")
                    if "LOCAL" in self.space:
                        const.target_space = "LOCAL"
                    elif "WORLD" in self.space:
                        const.target_space = "WORLD"
                    const.target = context.active_object
                    const.subtarget = context.active_pose_bone.name 
                    
                    
                    if self.type == "LOC_X":
                        const.transform_channel = "LOCATION_X"
                    elif self.type == "LOC_Y":
                        const.transform_channel = "LOCATION_Y"
                    elif self.type == "LOC_Z":
                        const.transform_channel = "LOCATION_Z"
                    elif self.type == "ROT_X":
                        const.transform_channel = "ROTATION_X"
                    elif self.type == "ROT_Y":
                        const.transform_channel = "ROTATION_Y"
                    elif self.type == "ROT_Z":
                        const.transform_channel = "ROTATION_Z"
                    else:
                        const.transform_channel = self.type    
                    
                    
                    const.min = self.min_value
                    const.max = self.max_value
                    const.frame_start = self.action_frame_start
                    const.frame_end = self.action_frame_end
                    const.action = bpy.data.actions[self.action]
            bpy.ops.ed.undo_push(message="Action Constraints generated.")
            self.report({'INFO'},"Action constraints generated.")
        elif self.action_mode == "DELETE_CONSTRAINT":
            for bone in context.selected_pose_bones:
                for const in bone.constraints:
                    if (const.name == self.action_constraint):# or (self.action_constraint == "ALL_ACTIONS"):
                        #bone.constraints.remove(const)
                        #if self.action_constraint != "ALL_ACTIONS":
                        #    break
                        pass
            bpy.ops.ed.undo_push(message="Action Constraints deleted.")
            self.report({'INFO'},"Action constraints deleted.")            
               
    
    def set_defaults(self,context):
        ### set location
        if self.driver.location != Vector((0,0,0)):
            l = [abs(self.driver.location.x),abs(self.driver.location.y),abs(self.driver.location.z)]
            m = max(l)
            type = ["LOC_X","LOC_Y","LOC_Z"]
            
            for i,value in enumerate(l):
                if l[i] == m:
                    self.min_value = 0.0
                    self.max_value = self.driver.location[i]
                    self.type = type[i] 
                    break       
            return "LIMIT_LOCATION"
        
        ### set rotation
        driver_rotation = Euler()
        if self.driver.rotation_mode == "QUATERNION":
            driver_rotation = self.driver.rotation_quaternion.to_euler("XYZ")
        else:
            driver_rotation = self.driver.rotation_euler
        
        if Vector((driver_rotation.x,driver_rotation.y,driver_rotation.z)) != Vector((0,0,0)):
            l = [abs(driver_rotation.x),abs(driver_rotation.y),abs(driver_rotation.z)]
            m = max(l)
            type = ["ROT_X","ROT_Y","ROT_Z"]
            
            for i,value in enumerate(l):
                if l[i] == m:
                    self.min_value = 0.0
                    self.max_value = degrees(driver_rotation[i])
                    self.type = type[i]
                    break
            return "LIMIT_ROTATION"
        
        ### set scale
        if self.driver.scale != Vector((1,1,1)):
            l = [abs(self.driver.scale.x),abs(self.driver.scale.y),abs(self.driver.scale.z)]
            l_delta = [abs(1.0-self.driver.scale.x),abs(1.0-self.driver.scale.y),abs(1.0-self.driver.scale.z)]
            m_delta = max(l_delta)
            m = max(l)
            type = ["SCALE_X","SCALE_Y","SCALE_Z"]
            
            for i,value in enumerate(l):
                if l_delta[i] == m_delta:
                    self.min_value = 1.0
                    self.max_value = l[i]
                    self.type = type[i]
                    break
            return "LIMIT_SCALE"

    
    def execute(self, context):
        wm = context.window_manager
        context = bpy.context
        scene = context.scene
        active_object = context.active_object
        
        if self.mode == "DRIVER":
            self.create_property_driver(wm,context,scene,active_object)
        elif self.mode == "ACTION":
            self.create_actions_constraints(context)
        
        return {'FINISHED'}
        
    def create_property_driver(self,wm,context,scene,active_object):
        if len(context.selected_objects) > 1:
            obj = None
            for obj2 in context.selected_objects:
                if obj2 != context.scene.objects.active:
                    obj = obj2
                    break
        else:
            obj = context.selected_objects[0]    
        
        driver_found = False
        for obj in context.selected_objects:
            if obj != context.scene.objects.active or len(context.selected_objects) == 1:
                if get_prop_object(self,context,self.prop_data_path,obj) != None:
                    prop_type = get_prop_object(self,context,self.prop_data_path,obj)[1]
                    data = get_prop_object(self,context,self.prop_data_path,obj)[0]
                    if data == obj and self.property_type == "OBECT_DATA_PROPERTY":
                        data = data.data
                    if prop_type in ["MODIFIER_PROPERTY","OBJECT_CONSTRAINT_PROPERTY"]:
                        data_path = self.prop_data_path.split(".")[1]
                        curve = data.driver_add(data_path)    
                    elif prop_type in ["BONE_PROPERTY"]:
                        if self.prop_data_path.rfind("]") == len(self.prop_data_path)-1: ### this is used for props of that type: bones["bone_name"]["property_name"]
                            from_idx = self.prop_data_path.rfind("[")
                            to_idx = self.prop_data_path.rfind("]")+1
                            data_path = self.prop_data_path[from_idx:to_idx]
                        else: ### this is used for props of that type: bones["bone_name"].property_name
                            data_path = self.prop_data_path.split(".")[1]
                        curve = data.driver_add(data_path)        
                    elif prop_type in ["BONE_CONSTRAINT_PROPERTY"]  :  
                        string_elements = self.prop_data_path.split(".")
                        data_path = string_elements[len(string_elements)-1]
                        
                        curve = data.driver_add(data_path)
                    elif "texture_slots" in self.prop_data_path and "[" in self.prop_data_path:
                        data_path = self.prop_data_path.split(".")[1]
                        curve = data.driver_add(data_path)
                    else:    
                        curve = data.driver_add(self.prop_data_path)
                else:
                    curve = None
                
                curves = [curve]
                if type(curve) == list:
                    curves = curve
                
                ### create driver fcurve which defines how the value is driven
                for curve in curves:
                    if curve != None:
                        driver_found = True
                        if len(curve.driver.variables) < 1:
                            curve_var = curve.driver.variables.new()
                        else:
                            curve_var = curve.driver.variables[0]
                        
                        if len(curve.modifiers) > 0:
                            curve.modifiers.remove(curve.modifiers[0])
                        curve.driver.type = "SUM"
                        curve_var.type = "TRANSFORMS"
                        ### setup driver object/bone
                        driver_obj = context.active_object
                        curve_var.targets[0].id = driver_obj
                        if driver_obj.type == "ARMATURE":
                            curve_var.targets[0].bone_target = bpy.context.active_pose_bone.name
                        curve_var.targets[0].transform_space = self.space
                        curve_var.targets[0].transform_type = self.type
                        
                        if self.type in ["ROT_X","ROT_Y","ROT_Z"]:
                            min_value = radians(self.min_value)
                            max_value = radians(self.max_value)
                        else:
                            min_value = self.min_value
                            max_value = self.max_value
                        
                        delete_len = 0
                        for point in curve.keyframe_points:
                            delete_len += 1
                        for i in range(delete_len):    
                            curve.keyframe_points.remove(curve.keyframe_points[0])
                        
                        point_a = curve.keyframe_points.insert(min_value,self.prop_min_value)
                        point_a.interpolation = self.interpolation_type
                        
                        point_b = curve.keyframe_points.insert(max_value,self.prop_max_value)
                        point_b.interpolation = self.interpolation_type
        

        self.set_limit_constraint(context)        
        
        if driver_found:
            msg = self.prop_data_path +" Driver has been added."
            self.report({'INFO'},msg)
        else:
            msg = self.prop_data_path +" Property has not been found."
            self.report({'WARNING'},msg)

    def set_limit_constraint(self,context):
        if self.set_driver_limit_constraint:
            if self.limit_type != None:
                if "Driver Limit" in self.driver.constraints:
                    self.driver.constraints.remove(self.driver.constraints["Driver Limit"])    
                const = self.driver.constraints.new(self.limit_type)
                const.name = "Driver Limit"
                if "LOCAL" in self.space:
                    const.owner_space = "LOCAL"
                elif "WORLD" in self.space:
                    const_owner_space = "WORLD"    
                
                if self.min_value < self.max_value:
                    min_value = self.min_value
                    max_value = self.max_value
                else:
                    min_value = self.max_value
                    max_value = self.min_value
                if self.limit_type in ["LIMIT_LOCATION","LIMIT_SCALE"]:
                                    
                    if "X" in self.type:
                        const.use_min_x = True
                        const.use_max_x = True 
                        const.min_x = min_value
                        const.max_x = max_value
                    elif "Y" in self.type:
                        const.use_min_y = True
                        const.use_max_y = True 
                        const.min_y = min_value
                        const.max_y = max_value
                    elif "Z" in self.type:
                        const.use_min_z = True
                        const.use_max_z = True
                        const.min_z = min_value
                        const.max_z = max_value
                elif self.limit_type == "LIMIT_ROTATION":
                    if "X" in self.type:
                        const.use_limit_x = True
                        const.min_x = radians(min_value)
                        const.max_x = radians(max_value)
                    elif "Y" in self.type:
                        const.use_limit_y = True
                        const.min_y = radians(min_value)
                        const.max_y = radians(max_value)
                    elif "Z" in self.type:
                        const.use_limit_z = True
                        const.min_z = radians(min_value)
                        const.max_z = radians(max_value)
                        
        
    def invoke(self, context, event):
        wm = context.window_manager 
        
        self.driver = None
        if context.active_object.type == "ARMATURE" and context.active_pose_bone != None:
            self.driver = context.active_pose_bone
        elif context.active_object.type in ["MESH","EMPTY"]:
            self.driver = context.active_object
            
        
        if len(context.selected_objects) > 1:
            obj = None
            for obj2 in context.selected_objects:
                if obj2 != context.scene.objects.active:
                    obj = obj2
                    break
        else:
            obj = context.selected_objects[0]
        
        if wm.clipboard != "":
            if get_prop_object(self,context,wm.clipboard,obj) != None:
                self.prop_data_path = wm.clipboard
                self.property_type = get_prop_object(self,context,wm.clipboard,obj)[1]
            else:
                self.property_type = "OBJECT_PROPERTY"
        
        if self.get_limits_auto:
            self.limit_type = self.set_defaults(context)
        
        
        if self.action in bpy.data.actions:
            action = bpy.data.actions[self.action]
            self.action_frame_end = get_action_length(action)
                
        return wm.invoke_props_dialog(self)
