import bpy
from bpy.types import Operator
from .object_lib import ActivateObject, FocusObject, SelectObject, RecordSelectedState, RestoreSelectedState
from .update import Update_ObjectOrigin, Update_ObjectVGOrigin, SetMeshOrigin

class OX_Update_Origin(Operator):
    """Updates the origin point based on each object's origin setting, for all selected objects"""

    bl_idname = "origin.update_origin"
    bl_label = ""

    def execute(self, context):
        print(self)

        print("RAWR")

        atv = context.active_object
        sel = context.selected_objects
        selRecord = RecordSelectedState(context)

        for obj in sel:
            FocusObject(obj)
            SetMeshOrigin(int(obj.OXObj.origin_point), obj.name)

        FocusObject(atv)
        SetMeshOrigin(int(atv.OXObj.origin_point), atv.name)

        RestoreSelectedState(selRecord)

        return {'FINISHED'}
