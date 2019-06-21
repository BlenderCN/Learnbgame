# Working Copy Operator
class WorkingCopyTool(bpy.types.Operator):
    bl_idname = "WorkingCopyToolOperator"
    bl_label = "Copy your working after push ¥"Start¥""

    def execute(self, context):
        print("WorkingCopyExe")
        return {"FINISH"}

    @classmethod
    def register(cls):
        print("WokingCopyRegistor")

    @classmethod
    def unregister(cls):
        print("WorkingCopyUnRegistor")

# Finish Working Copy
