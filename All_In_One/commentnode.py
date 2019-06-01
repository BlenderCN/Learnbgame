
# based on original code from
# http://blender.stackexchange.com/questions/7825/is-there-a-way-to-make-comments-in-the-node-editor
# modifications by Shane Ambler

bl_info = {
    "name": "Comment Node",
    "author": "CoDEmanX",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "location": "Node Editor > Add > Commenting > Comment",
    "description": "Add a comment node to keep notes with a node tree.",
    "warning": "",
    "wiki_url": "https://github.com/sambler/myblendercontrib/blob/master/commentnode.py",
    "tracker_url": "https://github.com/sambler/myblendercontrib/issues",
    "category": "Learnbgame",
    }

import bpy
from bpy.types import Node, Operator
from bpy.props import BoolProperty, IntProperty, CollectionProperty

class NodeComment(Operator):
    bl_idname = "node.comment"
    bl_label = "Node Comment"

    index : IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        return (context.area.type == 'NODE_EDITOR' and
                context.area.spaces[0].node_tree.nodes.active is not None and
                context.area.spaces[0].node_tree.nodes.active.bl_idname == CommentNode.bl_idname)

    def execute(self, context):
        node = context.area.spaces[0].node_tree.nodes.active
        if self.index == -1:
            node.myCollProperty.add()
            node.myBoolProperty = True
        else:
            try:
                node.myCollProperty.remove(self.index)
            except IndexError:
                print("Invalid collection index")
                return {'CANCELLED'}
        return {'FINISHED'}

# Derived from the Node base type.
class CommentNode(Node):
    # === Basics ===
    # Description string
    '''A comment node'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CommentNodeType'
    # Label for nice name display
    bl_label = 'Comment Node'
    # Icon identifier
    bl_icon = 'GREASEPENCIL'

    myBoolProperty : bpy.props.BoolProperty(name="Edit")
    myCollProperty : bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def init(self, context):
        self.width = 300

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        #layout.label("Node settings")

        row = layout.row(align=True)
        row.operator(NodeComment.bl_idname, text="Add", icon="ZOOM_IN").index = -1
        row.prop(self, "myBoolProperty", text="", icon="GREASEPENCIL")

        col = layout.column(align=True)

        if self.myBoolProperty:
            for i, line in enumerate(self.myCollProperty):
                row = col.row(align=True)
                row.prop(line, "name", text="")
                row.operator(NodeComment.bl_idname, text="", icon="ZOOM_OUT").index = i
        else:
            for line in self.myCollProperty:
                col.label(line.name)

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class CommentNodeCategory(NodeCategory):
    pass

# all categories in a list
comment_node_categories = [
    # identifier, label, items list
    CommentNodeCategory("COMMENTNODES", "Commenting", items=[
        NodeItem(CommentNode.bl_idname, label="Comment"),
        ]),
    ]


def register():
    bpy.utils.register_class(NodeComment)
    bpy.utils.register_class(CommentNode)

    try:
        nodeitems_utils.register_node_categories("COMMENT_NODES", comment_node_categories)
    except:
        pass


def unregister():
    nodeitems_utils.unregister_node_categories("COMMENT_NODES")

    bpy.utils.unregister_class(NodeComment)
    bpy.utils.unregister_class(CommentNode)


if __name__ == "__main__":
    register()

