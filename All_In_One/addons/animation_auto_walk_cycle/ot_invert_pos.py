import bpy
from bpy.props import IntProperty

class WalkCycleInvertValues(bpy.types.Operator):
    """Invert Position"""
    bl_idname = "armature.walk_cycle_invert_pos"
    bl_label = "Invert Position"
    
    type = IntProperty() 

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'awc_bone')

    def invoke(self, context, event):
        awc_bone = context.awc_bone
        awc_bone.loc1, awc_bone.loc2 = awc_bone.loc2, awc_bone.loc1.copy()
        rotation_mode = context.object.pose.bones[awc_bone.name].rotation_mode
        if rotation_mode == 'QUATERNION':
            awc_bone.qua1, awc_bone.qua2 = awc_bone.qua2, awc_bone.qua1.copy()
        elif rotation_mode == 'AXIS_ANGLE':
            awc_bone.axi1, awc_bone.axi2 = awc_bone.axi2, awc_bone.axi1.copy()
        else:
            awc_bone.eul1, awc_bone.eul2 = awc_bone.eul2, awc_bone.eul1.copy()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(WalkCycleInvertValues)

def unregister():
    bpy.utils.unregister_class(WalkCycleInvertValues)

if __name__ == "__main__":
    register()
