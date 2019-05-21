from ..functions import snap_IKFK


import bpy

class SnapIKFK(bpy.types.Operator):
    bl_label = "Snap FK bones to IK"
    bl_idname = "rigui.snap_ikfk"
    #bl_options = {'REGISTER', 'UNDO'}

    limb = bpy.props.StringProperty()
    way = bpy.props.StringProperty()

    def execute(self,context):

        snap_IKFK(self.limb,self.way)

        return {'FINISHED'}
