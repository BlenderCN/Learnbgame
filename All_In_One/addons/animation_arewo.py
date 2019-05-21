# bl_info is a dictionary containing addon meta-data such as the title, version and author to be displayed in the user preferences addon list.
bl_info = {
    "name": "ARewO",
    "author": "Frederik Steinmetz & Gottfried Hofmann",
    "version": (0, 3),
    "blender": (2, 66, 0),
    "location": "SpaceBar Search -> ARewO",
    "description": "Animation replicator with offset",
    "category": "Animation",
}

import bpy
import math
import time
import os
# time_start = time.time()

# offset_extra = 0
# replicat = bpy.context.active_object


class ARewO(bpy.types.Operator):
    """Animation Replicator with Offset"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.arewo"        # unique identifier for buttons and menu items to reference.
    bl_label = "ARewO"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    
    #number of copies to create (slider button)
    loops = bpy.props.IntProperty(name="Replications", description="How many times the animation will be duplicated", default=1, min=1, soft_max=1000, step=1)
    
    #offset of the animation in frames (slider button)
    offset = bpy.props.FloatProperty(name="Offset", description="Offset of the animations in frames", default = 10.0, soft_max=1000.0, soft_min=-1000.0, step=1.0)
    
    #for the distance we use a vector which shows up nicely in the UI
    distance = bpy.props.FloatVectorProperty(name="Distance", description="Distance between the elements in BUs", default = (0.1, 0.0, 0.0))
    
    #rotation is in radians atm
    rotation = bpy.props.FloatVectorProperty(name="Rotation", description="Delta rotation of the elements in radians", default = (0.0, 0.0, 0.0))
    
    #delta scale is also Blender Units, maybe it makes more sense to allow only uniform scale, which might be the default case anyways?
    scale = bpy.props.FloatVectorProperty(name="Scale", description="Delta scale of the elements in BUs", default = (0.0, 0.0, 0.0))
    
    # execute() is called by blender when running the operator.
    def execute(self, context):
        
        #the actual script
        for i in range(self.loops):
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False})
            obj = bpy.context.active_object
            
            obj.delta_location[0] += self.distance[0]
            obj.delta_location[1] += self.distance[1]
            obj.delta_location[2] += self.distance[2]
            
            obj.delta_rotation_euler.x += self.rotation[0]
            obj.delta_rotation_euler.y += self.rotation[1]
            obj.delta_rotation_euler.z += self.rotation[2]
            
            obj.delta_scale[0] += self.scale[0]
            obj.delta_scale[1] += self.scale[1]
            obj.delta_scale[2] += self.scale[2]
            
            animData = obj.animation_data
            action = animData.action
            fcurves = action.fcurves
            
            for curve in fcurves:
                keyframePoints = curve.keyframe_points
                for keyframe in keyframePoints:
                    keyframe.co[0] += self.offset #move
                    keyframe.handle_left[0] += self.offset
                    keyframe.handle_right[0] += self.offset
                    
        # this lets blender know the operator finished successfully.
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ARewO.bl_idname)

def register():
    bpy.utils.register_class(ARewO)
    #append ARewO to the 'Object' Menu in the 3D view header
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ARewO)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
 
 
 # This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()