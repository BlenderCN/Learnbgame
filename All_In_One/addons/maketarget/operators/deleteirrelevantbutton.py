import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from ..maketarget import deleteIrrelevant

class VIEW3D_OT_DeleteIrrelevantButton(bpy.types.Operator):
    bl_idname = "mh.delete_irrelevant"
    bl_label = "Delete Irrelevant Verts"
    bl_description = "Delete not affected vertices for better visibility."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        setObjectMode(context)
        try:
            ob = context.object
            deleteIrrelevant(ob, ob.MhAffectOnly)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

