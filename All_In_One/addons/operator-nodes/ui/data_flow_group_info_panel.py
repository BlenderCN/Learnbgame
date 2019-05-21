import bpy
from .. trees import DataFlowGroupTree

class DataFlowGroupInfoPanel(bpy.types.Panel):
    bl_idname = "en_InfoPanel"
    bl_label = "Info"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Everything Nodes"

    @classmethod
    def poll(cls, context):
        return isinstance(context.space_data.node_tree, DataFlowGroupTree)

    def draw(self, context):
        layout = self.layout
        tree = context.space_data.node_tree

        layout.label(text=str(tree.is_valid_function))
        if tree.is_valid_function:
            layout.label(text=str(tree.signature))

        layout.operator("en.analyse_tree")
        layout.operator("en.modal_runner")