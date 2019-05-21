import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from .. import mt, import_obj
from ..maketarget import afterImport, loadAndApplyTarget

class VIEW3D_OT_ImportBaseObjButton(bpy.types.Operator):
    bl_idname = "mh.import_base_obj"
    bl_label = "Load Human"
    bl_description = "Load the base object. Clothes fitting disabled."
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            import_obj.importBaseObj(context, filepath=mt.baseObjFile)
            afterImport(context, mt.baseObjFile, True, False)
            loadAndApplyTarget(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}