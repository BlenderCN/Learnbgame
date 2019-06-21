import bpy
from bpy.props import IntProperty

class WalkCycleCopyLocation(bpy.types.Operator):
    """Copies the current position of the bone"""
    bl_idname = "armature.walk_cycle_copy_pos"
    bl_label = "Copy Bone Location"
    
    type = IntProperty() 

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'awc_bone')

    def invoke(self, context, event):
        bone = context.object.pose.bones[context.awc_bone.name]
        if self.type == 0:
            context.awc_bone.loc1 = bone.location
        elif self.type == 1:
            context.awc_bone.loc2 = bone.location
        else:
            if bone.rotation_mode == 'QUATERNION':
                if self.type == 2:
                    context.awc_bone.qua1 = bone.rotation_quaternion
                if self.type == 3:
                    context.awc_bone.qua2 = bone.rotation_quaternion
            elif bone.rotation_mode == 'AXIS_ANGLE':
                if self.type == 2:
                    context.awc_bone.axi1 = bone.rotation_axis_angle
                if self.type == 3:
                    context.awc_bone.axi2 = bone.rotation_axis_angle
            else:
                if self.type == 2:
                    context.awc_bone.eul1 = bone.rotation_euler
                if self.type == 3:
                    context.awc_bone.eul2 = bone.rotation_euler
        return {'FINISHED'}

def register():
    bpy.utils.register_class(WalkCycleCopyLocation)

def unregister():
    bpy.utils.unregister_class(WalkCycleCopyLocation)

if __name__ == "__main__":
    register()
