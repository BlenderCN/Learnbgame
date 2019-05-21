import bpy
from mathutils import Vector


def main(caller, context):
    space = context.space_data
    node_tree = space.node_tree
    nodes = node_tree.nodes

    def new_node(t):
        return nodes.new(type=t)

    comb_xyz = new_node("ShaderNodeCombineXYZ")
    geometry = new_node("ShaderNodeNewGeometry")
    add = new_node("ShaderNodeVectorMath")
    noise = new_node("ShaderNodeTexNoise")

    x, y = context.space_data.cursor_location

    geometry.location = Vector((0.000 + x, 0.0000 + y))
    add.location = Vector((190.2 + x, -92.20 + y))
    noise.location = Vector((392.0 + x, -48.00 + y))
    comb_xyz.location = Vector((1.900 + x, -242.0 + y))

    ''' hook up nodes '''

    a = geometry.outputs['Position']
    b = add.inputs[0]
    node_tree.links.new(a, b)

    a = comb_xyz.outputs['Vector']
    b = add.inputs[1]
    node_tree.links.new(a, b)

    a = add.outputs['Vector']
    b = noise.inputs[0]
    node_tree.links.new(a, b)


class NodePlexOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "node.add_noise_plex"
    bl_label = "Simple Plex Add"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


def register():
    bpy.utils.register_class(NodePlexOperator)


def unregister():
    bpy.utils.unregister_class(NodePlexOperator)


if __name__ == "__main__":
    register()
