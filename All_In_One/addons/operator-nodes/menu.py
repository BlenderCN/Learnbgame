import bpy
from . trees import DataFlowGroupTree, ActionsTree, ParticleSystemTree

def draw_menu(self, context):
    tree = context.space_data.node_tree
    if not isinstance(tree, (DataFlowGroupTree, ActionsTree, ParticleSystemTree)):
        return

    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"
    if isinstance(tree, DataFlowGroupTree):
        insertNode(layout, "en_GroupInputNode", "Group Input")
        insertNode(layout, "en_GroupOutputNode", "Group Output")
    elif isinstance(tree, ActionsTree):
        insertNode(layout, "en_KeyPressEventNode", "Key Press Event")
        insertNode(layout, "en_MouseClickEventNode", "Mouse Click Event")
        insertNode(layout, "en_OnUpdateEventNode", "On Update Event")
        layout.separator()
        insertNode(layout, "en_MoveObjectNode", "Move Object")
        insertNode(layout, "en_RotateObjectNode", "Rotate Object")
        insertNode(layout, "en_MoveViewNode", "Move View")
        insertNode(layout, "en_RotateViewNode", "Rotate View")
        insertNode(layout, "en_SetObjectAttributeNode", "Set Object Attribute")
    elif isinstance(tree, ParticleSystemTree):
        insertNode(layout, "en_ParticleTypeNode", "Particle Type")
        layout.separator()
        insertNode(layout, "en_PointEmitterNode", "Point Emitter")
        layout.separator()
        insertNode(layout, "en_GravityNode", "Gravity")
        insertNode(layout, "en_AttractNode", "Attract")
        layout.separator()
        insertNode(layout, "en_ParticleAgeTriggerNode", "Age Trigger")
        layout.separator()
        insertNode(layout, "en_ChangeParticleDirectionNode", "Change Direction")
        insertNode(layout, "en_ChangeParticleVelocityNode", "Change Velocity")
        insertNode(layout, "en_ChangeParticleColorNode", "Change Color")
        insertNode(layout, "en_KillParticleNode", "Kill Particle")
        insertNode(layout, "en_ParticleInfoNode", "Particle Info")
        insertNode(layout, "en_SpawnParticleNode", "Spawn Particle")

    if isinstance(tree, (ActionsTree, ParticleSystemTree)):
        layout.separator()
        insertNode(layout, "en_ConditionNode", "Condition")

    layout.separator()
    insertNode(layout, "en_FloatMathNode", "Float Math")
    insertNode(layout, "en_VectorMathNode", "Vector Math")
    insertNode(layout, "en_CombineVectorNode", "Combine Vector")
    insertNode(layout, "en_SeparateVectorNode", "Separate Vector")
    insertNode(layout, "en_ObjectTransformsNode", "Object Transforms")
    insertNode(layout, "en_OffsetVectorWithObjectNode", "Offset Vector with Object")
    insertNode(layout, "en_GetObjectParentNode", "Get Object Parent")

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
    bpy.types.NODE_MT_add.append(draw_menu)

def unregister():
    bpy.types.NODE_MT_add.remove(draw_menu)