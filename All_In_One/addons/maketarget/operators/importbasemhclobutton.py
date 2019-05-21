import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from .. import mt, import_obj
from ..maketarget import afterImport, loadAndApplyTarget

class VIEW3D_OT_ImportBaseMhcloButton(bpy.types.Operator):
    bl_idname = "mh.import_base_mhclo"
    bl_label = "Load Human + Fit Tools"
    bl_description = "Load the base object. Clothes fitting enabled."
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            import_obj.importBaseMhclo(context, filepath=mt.baseMhcloFile)
            afterImport(context, mt.baseMhcloFile, False, True)
            loadAndApplyTarget(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}
