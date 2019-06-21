import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from ..maketarget import makeBaseObj

class VIEW3D_OT_MakeBaseObjButton(bpy.types.Operator):
    bl_idname = "mh.make_base_obj"
    bl_label = "Set As Base"
    bl_description = "Make the selected object into a maketarget base object."
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            makeBaseObj(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}