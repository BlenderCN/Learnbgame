import bpy

def drawMenu(self, context):
    if context.space_data.tree_type != "cn_ComputeNodeTree":
        return

    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"
    insertNode(layout, "cn_FloatMathNode", "Math")
    insertNode(layout, "cn_CombineVectorNode", "Combine Vector")
    insertNode(layout, "cn_SeparateVectorNode", "Separate Vector")
    insertNode(layout, "cn_ObjectTransformsNode", "Object Transforms")
    insertNode(layout, "cn_InputNode", "Input")
    insertNode(layout, "cn_OutputNode", "Output")

def insertNode(layout, type, text, settings = {}, icon = "NONE"):
    operator = layout.operator("node.add_node", text = text, icon = icon)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
        item = operator.settings.add()
        item.name = name
        item.value = value
    return operator


def register():
    bpy.types.NODE_MT_add.append(drawMenu)

def unregister():
    bpy.types.NODE_MT_add.remove(drawMenu)
