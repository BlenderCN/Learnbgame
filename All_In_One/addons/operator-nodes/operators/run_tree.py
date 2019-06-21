import bpy

class RunTreeOperator(bpy.types.Operator):
    bl_idname = "en.run_tree"
    bl_label = "Run Tree"

    def execute(self, context):
        print("executing operator")
        context.space_data.node_tree.execute(context)
        return {"FINISHED"}