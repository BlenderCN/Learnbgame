import bpy

from ..functions import apply_pose
from ..functions import reset_props
from ..functions import insert_keyframe
from ..functions import store_props


class ApplyPose(bpy.types.Operator):
    bl_label = "Apply Pose Custom"
    bl_idname = "poselib.apply_pose_custom"
    bl_options = {'REGISTER', 'UNDO'}

    pose_index = bpy.props.IntProperty(options={'HIDDEN'})
    blend = bpy.props.FloatProperty(name="Blend : ",min=0,max=1,default = 1.0)

    def execute(self,context):
        apply_pose(self.pose_index,self.blend,context)

        return {'FINISHED'}

class StoreNonZeroValue(bpy.types.Operator) :
    """ Store Non Zero Value
    """
    bl_idname = "store.non_zero_value"
    bl_label = "Store Custom Prop value"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.active_object.type == 'ARMATURE')

    def execute(self, context):
        ob = context.object
        store_props(ob)

        return {'FINISHED'}

'''
class RefreshPoseLib(bpy.types.Operator) :
    """ Refresh PoseLib List
    """
    bl_idname = "refresh.poselib"
    bl_label = "Refresh PoseLib List"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.active_object.type == 'ARMATURE')

    def execute(self, context):
        ob = context.object
        refresh_poseLib(ob)

        return {'FINISHED'}

'''
class ResetProps(bpy.types.Operator) :
    """ Reset Transfrom And Props.
    """
    bl_idname = "pose.reset_props"
    bl_label = "Reset bones transforms and custom propeties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        if len(bpy.context.selected_pose_bones)==0 :
            bones = bpy.context.object.pose.bones

        else :
            bones = bpy.context.selected_pose_bones

        for bone in bones :
            #0 = no keyframe inserted, 1 = keyframe inserted
            if bpy.context.scene.tool_settings.use_keyframe_insert_auto == False :
                reset_props(bone,0)
            else :
                reset_props(bone,1)

        return {'FINISHED'}

class InsertKeyFrame(bpy.types.Operator):
    """ Add key frame to selected bone on available transforms and properties
    """
    bl_idname = "pose.insert_keyframe"
    bl_label = "Insert Key Frame"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        for bone in bpy.context.selected_pose_bones :
            insert_keyframe(bone)


        return {'FINISHED'}
