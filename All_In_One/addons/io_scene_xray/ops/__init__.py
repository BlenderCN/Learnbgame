import bpy


class BaseOperator(bpy.types.Operator):
    bl_idname = "xray.base"
    bl_label = "Base xray operator"
    bl_description = "Base xray operator"

    report_catcher = None

    def __getattribute__(self, item):
        if (item == 'report') and (self.report_catcher is not None):
            return self.report_catcher
        return super().__getattribute__(item)
