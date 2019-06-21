import bpy

# Adds EdgeSplit To Meshes Only For Octane


class HOPS_OT_AddEdgeSplit(bpy.types.Operator):
    bl_idname = "add.edge_split"
    bl_label = "Add Edge Split"
    bl_description = "Add Edge Split Modifier To All Selected Meshes"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            obj.modifiers.new(type='EDGE_SPLIT', name='EdgeSplit')
            if object.hops.status == "CSTEP":
                object.hops.status = "CSTEP (EdgeSplit)"
            if object.hops.status == "CSHARP":
                object.hops.status = "CSHARP (EdgeSplit)"
            else:
                object.hops.status = "UNDEFINED (EdgeSplit)"

        return {"FINISHED"}
