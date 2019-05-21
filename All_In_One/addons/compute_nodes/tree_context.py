import bpy
from bpy.props import *
from . node_tree import ComputeNodeTree

class TreeContext:
    def is_compute_tree(self, object):
        return isinstance(object, ComputeNodeTree)

    tree = PointerProperty(name = "Node Tree", type = bpy.types.NodeTree, poll = is_compute_tree)


class PropertyTreeContext(bpy.types.PropertyGroup, TreeContext):
    path = StringProperty(name = "Path")

class TreeContexts(bpy.types.PropertyGroup):
    property_contexts = CollectionProperty(type = PropertyTreeContext)

class ObjectTreeContextManagerPanel(bpy.types.Panel):
    bl_idname = "cn_ObjectTreeContextManagerPanel"
    bl_label = "Tree Contexts"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(self, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        object = context.active_object

        props = layout.operator("cn.new_object_property_tree_context")
        props.object_name = object.name
        props.path = "location"


        for prop_context in object.tree_contexts.property_contexts:
            self.draw_prop_context(layout, prop_context)

    def draw_prop_context(self, layout, prop_context):
        row = layout.row()
        row.label(prop_context.path)
        row.prop(prop_context, "tree", text = "")

class NewObjectPropertyTreeContext(bpy.types.Operator):
    bl_idname = "cn.new_object_property_tree_context"
    bl_label = "New Tree Context"

    object_name = StringProperty()
    path = StringProperty()

    def execute(self, context):
        object = bpy.data.objects[self.object_name]

        tree = bpy.data.node_groups.new("My Tree", "cn_ComputeNodeTree")
        output_node = tree.nodes.new("cn_OutputNode")
        output_node.inputs.clear()
        output_node.inputs.new("cn_VectorSocket", self.path)

        item = object.tree_contexts.property_contexts.add()
        item.path = self.path
        item.tree = tree

        return {"FINISHED"}


def update_contexts():
    for object in bpy.data.objects:
        for item in object.tree_contexts.property_contexts:
            new_value = item.tree.get_function()()[0]
            exec("object.{} = value".format(item.path), {"object" : object, "value" : new_value})


def register():
    bpy.types.Object.tree_contexts = PointerProperty(type = TreeContexts)

def unregister():
    del bpy.types.Object.tree_contexts
