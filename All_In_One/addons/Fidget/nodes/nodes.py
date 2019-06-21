# Objects visible
#     Used as the if visible objects check and the check for if the amount visible is of value
# Objects type
# Property
#     Check a properties value (such as whether object xray is enabled)
#     Should be able to paste commands copied from copy data path, will assume object property otherwise
#     Should detect property type and produce corresponding options
# Selection mode
#     Needs to check for modes this applies to
#     Check for whether in verts/edge/face selection mode as example
# Selection amount
#     Needs to check for modes this applies to
#     Check for number of verts/edges/faces selected as example

import traceback

import bpy
import os
import json
import mathutils

from bpy.props import *
from bpy.types import Operator, NodeTree, Node, NodeSocket
from bpy.app.handlers import persistent

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

from . import button
from .. preferences import get_preferences

class FidgetNodeTree(NodeTree):
    bl_idname = "FidgetNodeTree"
    bl_label = "Fidget Node Tree"
    bl_icon = "NODETREE"

class FidgetCommandSocket(NodeSocket):
    bl_idname = "FidgetCommandSocket"
    bl_label = "Evaluate Socket"

    info_text = StringProperty(
        name = "Info Text",
        description = "The text to display while hovering over the button",
        default = "Info Text")

    event_value = EnumProperty(
        name = "Event Value",
        description = "Execute this command on either press or release of the LMB",
        items = [
            ("PRESS", "Press", ""),
            ("RELEASE", "Release", "Most things behave better with this value")],
        default = "RELEASE")

    command = StringProperty(
        name = "Command",
        description = "Command to execute",
        default = "")

    def draw(self, context, layout, node, text):
        if self.is_linked and not self.is_output:
            pass
        elif self.is_output:
            layout.label(text="Output")
        else:
            self.row(context, layout, node)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.22, 1.0)

    def row(self, context, layout, node, specials=True):
        col = layout.column() # HACK: forces row to span width
        col.scale_x = 10

        row = col.row(align=True)
        row.prop(self, "command", text="")

        if specials:
            op = row.operator("fidget.command_options", text="", icon="COLLAPSEMENU")
            op.tree = node.id_data.name
            op.node = node.name
            op.socket = self.name

class FidgetBoolSocket(NodeSocket):
    bl_idname = "FidgetBoolSocket"
    bl_label = "Bool Socket"

    value = BoolProperty(
        name = "Value",
        description = "The value of this boolean socket",
        default = True)

    compare_logic = EnumProperty(
        name = "Logic",
        description = "Type of logic to use for comparison",
        items = [
            ("XNOR", "Xnor", "If neither or both"),
            ("XOR", "Xor", "If either"),
            ("NOR", "Nor", "If neither"),
            ("NAND", "Nand", "If not both"),
            ("OR", "Or", "If either or both"),
            ("AND", "And", "If both")],
        default = "AND")

    active_object_mode = EnumProperty(
        name = "Object Mode",
        description = "Mode requirements to allow executing",
        items = [
            ("PARTICLE_EDIT", "Particle Edit", "", "PARTICLEMODE", 6),
            ("TEXTURE_PAINT", "Texture Paint", "", "TPAINT_HLT", 5),
            ("WEIGHT_PAINT", "Weight Paint", "", "WPAINT_HLT", 4),
            ("VERTEX_PAINT", "Vertex Paint", "", "VPAINT_HLT", 3),
            ("SCULPT", "Sculpt", "", "SCULPTMODE_HLT", 2),
            ("EDIT", "Edit", "", "EDITMODE_HLT", 1),
            ("OBJECT", "Object", "", "OBJECT_DATAMODE", 0)],
        default = "OBJECT")

    object_type = EnumProperty(
        name = "Object Type",
        description = "Type requirements to allow executing",
        items = [
            ('LAMP', "Lamp", "", "OUTLINER_OB_LAMP", 10),
            ('CAMERA', "Camera", "", "OUTLINER_OB_CAMERA", 9),
            ('SPEAKER', "Speaker", "", "OUTLINER_OB_SPEAKER", 8),
            ('EMPTY', "Empty", "", "OUTLINER_OB_EMPTY", 7),
            ('LATTICE', "Lattice", "", "OUTLINER_OB_LATTICE", 6),
            ('ARMATURE', "Armature", "", "OUTLINER_OB_ARMATURE", 5),
            ('FONT', "Font", "", "OUTLINER_OB_FONT", 4),
            ('META', "Metaball", "", "OUTLINER_OB_META", 3),
            ('SURFACE', "Serface", "", "OUTLINER_OB_SURFACE", 2),
            ('CURVE', "Curve", "", "OUTLINER_OB_CURVE", 1),
            ('MESH', "Mesh", "", "OUTLINER_OB_MESH", 0)],
        default = "MESH")

    objects_selected_amount = EnumProperty(
        name = "Objects Selected Amount",
        description = "",
        items = [
            ('ANY', "Any", "Executes if there is any selected objects"),
            ('AMOUNT', "Amount", "Executes based on amount of selected objects")],
        default = 'ANY')

    objects_visible_amount = EnumProperty(
        name = "Objects Visible Amount",
        description = "",
        items = [
            ('ANY', "Any", "Executes if there is any visible objects"),
            ('AMOUNT', "Amount", "Executes based on amount of visible objects")],
        default = 'ANY')

    bool_statement = StringProperty(
        name = "Statement",
        description = "Statement to evaluate",
        default = "")

    def draw(self, context, layout, node, text):
        self.draw_socket_row(layout)

    def draw_color(self, context, node):
        return (0.698, 0.651, 0.188, 1.0)

    def draw_socket_row(self, layout):
        col = layout.column()
        col.scale_x = 10

        row = col.row(align=True)
        getattr(self, self.node.bl_idname[6:-4].lower())(row)

    def switch(self, row):
        row.label(text=self.name)

    def compare(self, row):
        if self.is_output:
            row.prop(self, "compare_logic", text="")
        else:
            row.label(text="Boolean")

    def activeobject(self, row):
        if self.name == "Object":
            sub = row.row()
            sub.prop(self, "value", text="")
            row.label(text="{} active object".format("Is" if self.value else "Isn't"))

    def activeobjectmode(self, row):
        row.prop(self, "active_object_mode", text="")

    def activeobjecttype(self, row):
        row.prop(self, "object_type", text="")

    def objectsselected(self, row):
        row.prop(self, "objects_selected_amount", expand=True)

    def objectsvisible(self, row):
        row.prop(self, "objects_visible_amount", expand=True)

    def statement(self, row):
        row.prop(self, "bool_statement", text="")

class FidgetTreeNode:
    bl_width_min = 150

    @classmethod
    def poll(build, ntree):
        return ntree.bl_idname == "FidgetNodeTree"

class FidgetCommandNode(FidgetTreeNode, Node):
    bl_idname = "FidgetCommandNode"
    bl_label = "Command"

    info_text = StringProperty(
        name = "Info Text",
        description = "The text to display while hovering over the button",
        default = "Info Text")

    event_value = EnumProperty(
        name = "Event Value",
        description = "Execute this command on either press or release of the LMB",
        items = [
            ("PRESS", "Press", ""),
            ("RELEASE", "Release", "Most things behave better with this value")],
        default = "RELEASE")

    command = StringProperty(
        name = "Command",
        description = "Command to execute",
        default = "")

    def init(self, context):
        self.outputs.new("FidgetCommandSocket", "")

    def draw_buttons(self, context, layout):
        layout.separator()

        col = layout.column()
        col.prop(self, "command", text="")

        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(self, "info_text", text="")
        row = col.row(align=True)
        row.prop(self, "event_value", expand=True)

class FidgetSwitchNode(FidgetTreeNode, Node):
    bl_idname = "FidgetSwitchNode"
    bl_label = "Switch"

    def init(self, context):
        self.inputs.new("FidgetBoolSocket", "Use First")
        self.inputs.new("FidgetCommandSocket", "Command 1")
        self.inputs.new("FidgetCommandSocket", "Command 2")
        self.outputs.new("FidgetCommandSocket", "")

    def draw_buttons(self, context, layout):
        layout.separator()

        col = layout.column()
        col.scale_x = 10

        split = col.split(align=True)

        sub = split.column(align=True)
        sub.scale_y = 1.25
        sub.enabled = len(self.inputs) > 3

        op = sub.operator("fidget.command_remove", text="", icon="ZOOMOUT")
        op.tree = self.id_data.name
        op.node = self.name

        sub = split.column(align=True)
        sub.scale_y = 1.25
        sub.enabled = len(self.inputs) < 21

        op = sub.operator("fidget.command_add", text="", icon="ZOOMIN")
        op.tree = self.id_data.name
        op.node = self.name

class FidgetScriptNode(FidgetTreeNode, Node):
    bl_idname = "FidgetScriptNode"
    bl_label = "Script"

    def init(self, context):
        self.outputs.new("FidgetCommandSocket", "")

    def draw_buttons(self, context, layout):
        layout.separator()

class FidgetCompareNode(FidgetTreeNode, Node):
    bl_idname = "FidgetCompareNode"
    bl_label = "Compare"

    def init(self, context):
        self.outputs.new("FidgetBoolSocket", "")
        self.inputs.new("FidgetBoolSocket", "Boolean")
        self.inputs.new("FidgetBoolSocket", "Boolean")

class FidgetActiveObjectNode(FidgetTreeNode, Node):
    bl_idname = "FidgetActiveObjectNode"
    bl_label = "Active Object"

    def init(self, context):
        self.outputs.new("FidgetBoolSocket", "")

    def draw_buttons(self, context, layout):
        layout.separator()

class FidgetActiveObjectModeNode(FidgetTreeNode, Node):
    bl_idname = "FidgetActiveObjectModeNode"
    bl_label = "Object Mode"

    def init(self, context):
        self.outputs.new("FidgetBoolSocket", "")

    def draw_buttons(self, context, layout):
        layout.separator()

class FidgetActiveObjectTypeNode(FidgetTreeNode, Node):
    bl_idname = "FidgetActiveObjectTypeNode"
    bl_label = "Active Object Type"

    def init(self, context):
        self.outputs.new("FidgetBoolSocket", "")

    def draw_buttons(self, context, layout):
        layout.separator()

class FidgetObjectsSelectedNode(FidgetTreeNode, Node):
    bl_idname = "FidgetObjectsSelectedNode"
    bl_label = "Objects Selected"

    relation = EnumProperty(
        name = "Relation",
        description = "",
        items = [
            ('EQUAL', "Equal to", ""),
            ('LESSER', "Less then", ""),
            ('LESSEREQUAL', "Lesser or equal to", ""),
            ('GREATER', "Greater then", ""),
            ('GREATEREQUAL', "Greater or equal to", ""),
            ('NOT', "Not equal to", "")],
        default = "EQUAL")

    amount = IntProperty(
        name = "Amount",
        description = "The amount to use for the above relation operation",
        min = 0,
        default = 0)

    def init(self, context):
        self.outputs.new("FidgetBoolSocket", "")

    def draw_buttons(self, context, layout):
        if self.outputs[0].objects_selected_amount == "AMOUNT":
            column = layout.column(align=True)
            column.prop(self, 'relation', text="")
            column.prop(self, 'amount', text="")
        else:
            layout.separator()

class FidgetObjectsVisibleNode(FidgetTreeNode, Node):
    bl_idname = "FidgetObjectsVisibleNode"
    bl_label = "Objects Visible"

    relation = EnumProperty(
        name = "Relation",
        description = "",
        items = [
            ('EQUAL', "Equal to", ""),
            ('LESSER', "Less then", ""),
            ('LESSEREQUAL', "Lesser or equal to", ""),
            ('GREATER', "Greater then", ""),
            ('GREATEREQUAL', "Greater or equal to", ""),
            ('NOT', "Not equal to", "")],
        default = "EQUAL")

    amount = IntProperty(
        name = "Amount",
        description = "The amount to use for the above relation operation",
        min = 0,
        default = 0)

    def init(self, context):
        self.outputs.new("FidgetBoolSocket", "")

    def draw_buttons(self, context, layout):
        if self.outputs[0].objects_visible_amount == "AMOUNT":
            column = layout.column(align=True)
            column.prop(self, 'relation', text="")
            column.prop(self, 'amount', text="")
        else:
            layout.separator()

class FidgetStatementNode(FidgetTreeNode, Node):
    bl_idname = "FidgetStatementNode"
    bl_label = "Statement"

    def init(self, context):
        self.outputs.new("FidgetBoolSocket", "")

    def draw_buttons(self, context, layout):
        layout.separator()

class FidgetOutputNode(FidgetTreeNode, Node):
    bl_idname = "FidgetOutputNode"
    bl_label = "Output"

    button = EnumProperty(
        name = "Fidget Button",
        description = "The fidget button to target",
        items = [
            ("LEFT", "Left Button", ""),
            ("RIGHT", "Right Button", ""),
            ("TOP", "Top Button", "")],
        default = "TOP")

    mode = EnumProperty(
        name = "Fidget Mode",
        description = "The fidget mode to target",
        items = [
            ("MODE3", "Mode 3", ""),
            ("MODE2", "Mode 2", ""),
            ("MODE1", "Mode 1", "")],
        default = "MODE1")

    def init(self, context):
        self.inputs.new("FidgetCommandSocket", "Command")

    def draw_buttons(self, context, layout):
        layout.prop(self, "button", text="")
        layout.prop(self, "mode", text="")

        row = layout.row(align=True)
        row.scale_y = 1.25

        op = row.operator("fidget.update")
        op.output_id = str((self.id_data.name, self.name))
        op.write = True
        op.update_all_outputs = False

        # TODO: write_file and reset behavior
        # row.operator("fidget.save", text="", icon="FILE_TICK")
        # row.operator("fidget.reset", text="", icon="LOAD_FACTORY")

class FidgetNodeCategory(NodeCategory):

    @classmethod
    def poll(build, context):
        return context.space_data.tree_type == "FidgetNodeTree"

node_categories = [

    FidgetNodeCategory('FIDGETBOOLEAN', "Boolean", items=[
        NodeItem('FidgetCompareNode'),
        NodeItem('FidgetActiveObjectNode'),
        NodeItem('FidgetActiveObjectModeNode'),
        NodeItem('FidgetActiveObjectTypeNode'),
        NodeItem('FidgetObjectsSelectedNode'),
        NodeItem('FidgetObjectsVisibleNode'),
        NodeItem('FidgetStatementNode')]),

    FidgetNodeCategory('FIDGETCOMMAND', "Command", items=[
        NodeItem('FidgetCommandNode'),
        NodeItem('FidgetSwitchNode'),
        NodeItem('FidgetScriptNode')]),

    FidgetNodeCategory('FIDGETOUTPUT', "Output", items=[
        NodeItem('FidgetOutputNode')]),

    FidgetNodeCategory('LAYOUT', "Layout", items=[
        NodeItem("NodeFrame"),
        NodeItem("NodeReroute")])]

class FidgetNodeOperators:

    tree = StringProperty()
    node = StringProperty()
    socket = StringProperty()

    @classmethod
    def poll(build, context):
        if context.area is not None:
            return context.area.type == "NODE_EDITOR" and context.space_data.tree_type == "FidgetNodeTree"
        else:
            return True

    @staticmethod
    def get_count_word(integer):
        convert = [
            'First',
            'Second',
            'Third',
            'Fourth',
            'Fifth',
            'Sixth',
            'Seventh',
            'Eighth',
            'Ninth',
            'Tenth']

        return convert[integer]

class FidgetCommandOptions(FidgetNodeOperators, Operator):
    bl_idname = "fidget.command_options"
    bl_label = "Command Options"
    bl_description = "Adjust command options"

    def draw(self, context):
        layout = self.layout
        tree = bpy.data.node_groups[self.tree]
        node = tree.nodes[self.node]

        if node.bl_idname == "FidgetCommandNode":
            socket = node.outputs[0]
        else:
            socket = node.inputs[self.socket]

        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(socket, "info_text", text="")
        row = col.row(align=True)
        row.prop(socket, "event_value", expand=True)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):

        context.window_manager.invoke_popup(self, width=200)

        return {'RUNNING_MODAL'}

class FidgetCommandAdd(FidgetNodeOperators, Operator):
    bl_idname = "fidget.command_add"
    bl_label = "Add Command"
    bl_description = "Add a command and bool input socket pair to this node"

    def execute(self, context):
        tree = bpy.data.node_groups[self.tree]
        node = tree.nodes[self.node]

        split = len(node.inputs)//2
        bool_count = len(node.inputs[:split])

        node.inputs.new("FidgetBoolSocket", "Use {}".format(self.get_count_word(bool_count)))
        node.inputs.move(len(node.inputs)-1, bool_count)

        command_count = len(node.inputs[split:])

        node.inputs.new("FidgetCommandSocket", "Command {}".format(command_count))

        return {'FINISHED'}

class FidgetCommandRemove(FidgetNodeOperators, Operator):
    bl_idname = "fidget.command_remove"
    bl_label = "Remove Command"
    bl_description = "Remove the last command and bool input socket pair from this node"

    def execute(self, context):
        tree = bpy.data.node_groups[self.tree]
        node = tree.nodes[self.node]

        bool_index = len(node.inputs[:len(node.inputs)//2])-1
        node.inputs.remove(node.inputs[bool_index])
        node.inputs.remove(node.inputs[-1])
        return {'FINISHED'}

class FidgetSaveOperator(FidgetNodeOperators, Operator):
    bl_idname = "fidget.save_startup"
    bl_label = "Save"
    bl_description = "Save this node tree and have it be loaded automatically."

    def execute(self, context):
        tree = context.space_data.node_tree
        nodes = tree.nodes
        links = tree.links

        nodeTree = {"Tree": tree.name, "Nodes": [], "Links": []}
        
        for l in links:
            nodeTree["Links"].append({"from_node": l.from_node.name, "to_node": l.to_node.name, "from_socket": l.from_socket.identifier, "to_socket": l.to_socket.identifier})

        for n in nodes:

            data = {}

            properties = dir(n)
            parent = properties[properties.index("parent")]
            properties[0], parent = parent, properties[0]

            #illegalAttributes = []#"identifier", "dimensions", "type", "is_linked", "is_output"]
            types = [str, bool, float, int, tuple, list]

            for prop in properties:
                if hasattr(n, prop):
                    value = getattr(n, prop)
                    if prop == "parent" and value is not None:
                        value = value.name
                    if type(value) in [mathutils.Vector, mathutils.Color]:
                        value = tuple(value)
                    if type(value) in types and "__" not in prop:
                        data.update({prop: value})

            
            data.update({"inputs": [i.identifier for i in n.inputs]})
            data.update({"outputs": [i.identifier for i in n.outputs]})
            data.update({"insockets": []})
            data.update({"outsockets": []})


            for sock in n.inputs:
                insocketDict = {}
                for prop in dir(sock):
                    if hasattr(sock, prop) and "__" not in prop:
                        value = getattr(sock, prop)
                        if type(value) in [mathutils.Vector, mathutils.Color]:
                            value = tuple(value)
                        if type(value) in types and "__" not in prop:
                            insocketDict.update({prop: value})

                data["insockets"].append(insocketDict)


            for sock in n.outputs:
                outsocketDict = {}
                for prop in dir(sock):
                    if hasattr(sock, prop) and "__" not in prop:
                        value = getattr(sock, prop)
                        if type(value) in [mathutils.Vector, mathutils.Color]:
                            value = tuple(value)
                        if type(value) in types and "__" not in prop:
                            outsocketDict.update({prop: value})

                data["outsockets"].append(outsocketDict)


            nodeTree["Nodes"].append(data)


        path = os.path.dirname(os.path.abspath(__file__))
        startupFile = open(os.path.join(path, "startup_fidget_tree.json"), 'w')
        startupFile.write(json.dumps(nodeTree, indent = 4))
        startupFile.close()
        
        return {'FINISHED'}


class FidgetLoadOperator(FidgetNodeOperators, Operator):
    bl_idname = "fidget.load_startup"
    bl_label = "Load"
    bl_description = "Load the saved fidget tree"

    def execute(self, context):

        path = os.path.dirname(os.path.abspath(__file__))

        if not os.path.exists(path):
            return {'CANCELLED'}
        
        startupFile = open(os.path.join(path, "startup_fidget_tree.json"), 'r')
        data = startupFile.read()
        data = json.loads(data)
        startupFile.close()


        tree = bpy.data.node_groups.new(type="FidgetNodeTree", name=data["Tree"])
        nodes = tree.nodes

        for n in data["Nodes"]:
            
            node = tree.nodes.new(n["bl_idname"])

            for prop in n:

                value = n[prop]

                if hasattr(node, prop) and value is not None and prop not in ["inputs", "outputs"]:
                    
                    if prop == "parent":
                        value = nodes[n[prop]]
                    try:
                        setattr(node, prop, value)
                    except:
                        pass


            if node.bl_idname == "FidgetSwitchNode":

                for count, socket in enumerate(n["inputs"]):
                
                    split = len(node.inputs)//2
                    bool_count = len(node.inputs[:split])
                    title = "Use {}".format(self.get_count_word(bool_count))

                    if socket != node.inputs[count].identifier:

                        node.inputs.new("FidgetBoolSocket", title)
                        node.inputs.move(len(node.inputs)-1, bool_count)
                        command_count = len(node.inputs[split:])
                        node.inputs.new("FidgetCommandSocket", "Command {}".format(command_count))


            for count, sock in enumerate(n["insockets"]):
                for prop in sock:                
                    value = sock[prop]
                    try:
                        setattr(node.inputs[count], prop, value)
                    except:
                        pass

            for count, sock in enumerate(n["outsockets"]):
                for prop in sock:                
                    value = sock[prop]
                    try:
                        setattr(node.outputs[count], prop, value)
                    except:
                        pass


        for l in data["Links"]:

            from_node = nodes[l["from_node"]]
            to_node = nodes[l["to_node"]]

            for count, sock in enumerate(from_node.outputs):
                
                if sock.identifier == l["from_socket"]:
                    
                    from_socket = from_node.outputs[count]
                    to_socket = to_node.inputs[l["to_socket"]]
                    tree.links.new(from_socket, to_socket)

        return {'FINISHED'}
         

class FidgetUpdateOperator(FidgetNodeOperators, Operator):
    bl_idname = "fidget.update"
    bl_label = "Update"
    bl_description = "Update this fidget button"

    output_id = StringProperty()
    write = BoolProperty()
    reset = BoolProperty()
    update_all_outputs = BoolProperty()

    @staticmethod
    def get_input(socket):
        return socket.links[0].from_node if socket.links else None

    def execute(self, context):
        
        if self.output_id != "":
            tree_name, output_name = eval(self.output_id)
            #print(tree_name)
            tree = bpy.data.node_groups[tree_name]
            trees = [tree]
            self.outputs = [tree.nodes[output_name]]
            
        if self.output_id == "" or self.update_all_outputs:
            tree_name, output_name = ('NodeTree', 'Output')
            trees = [t for t in bpy.data.node_groups]
            self.outputs = []
            for tree in trees:
                self.outputs.extend([n for n in tree.nodes if n.bl_label == "Output"])

        for output in self.outputs:

            self.output = output
            self.input = self.output.inputs[0].links[0].from_node if len(self.output.inputs[0].links) else None
            links = self.output.inputs[0].links

            if self.input:
                if self.input.bl_idname in {'FidgetCommandNode', 'FidgetScriptNode', 'FidgetSwitchNode'}:
                    self.build(context)

                else:
                    self.report({'WARNING'}, "{} node is an invalid input command for {}".format(self.input.bl_label.capitalize(), self.output.bl_label.lower()))
                    #return {'CANCELLED'}

            elif self.output.inputs[0].command:
                self.build(context)

            else:
                self.report({'WARNING'}, self.output.name+": Must have a command for output")
                #return {'CANCELLED'}

        return {'FINISHED'}

    def build(self, context):
        self.command_value = "import bpy\n\ndef command(self, context, event):\n"
        self.indent = 1
        self.base_switch = self.input if self.input and self.input.bl_idname == "FidgetSwitchNode" else None

        if self.base_switch:
            # TODO: place into functions, optimize
            self.switches = []
            self.switch_data = {}
            self.node_logic(self.input)

            self.base_switch = None
            self.switches = self.switches[::-1]

            # update nested switches
            for node in self.switches:
                for index in range(len(self.switch_data[node.name]['bool'])):

                    if not isinstance(self.switch_data[node.name]['bool'][index], str):
                        bool_node = self.switch_data[node.name]['bool'][index]
                        self.switch_data[node.name]['bool'][index] = "{if_type} {bool}:".format(
                            if_type = "if" if index == 0 else "elif",
                            bool = self.node_logic(bool_node))

                    if not isinstance(self.switch_data[node.name]['command'][index], str):
                        command_node = self.switch_data[node.name]['command'][index]
                        self.switch_data[node.name]['command'][index] = self.node_logic(command_node)

                else:
                    self.switch_data[node.name]['bool'].append("else:")

                    if not isinstance(self.switch_data[node.name]['command'][-1], str):
                        command_node = self.switch_data[node.name]['command'][-1]
                        self.switch_data[node.name]['command'][-1] = self.node_logic(command_node)

            # replace switch nodes with indented switch data
            for node_index, node in enumerate(self.switches):

                # self.indent -= node_index
                self.indent = len(self.switches) - node_index

                for index, bool in enumerate(self.switch_data[node.name]['bool']):

                    self.switch_data[node.name]['bool'][index] = self.insert_indentation(bool)
                    self.indent += 1

                    command = self.switch_data[node.name]['command'][index]
                    if isinstance(command, str):
                        self.switch_data[node.name]['command'][index] = self.insert_indentation(command)

                    self.indent -= 1

            # add in switch data to other switches
            for node_index, node in enumerate(self.switches):

                command = ""

                for index, bool in enumerate(self.switch_data[node.name]['bool']):
                    command += bool
                    command += self.switch_data[node.name]['command'][index]

                if node_index < len(self.switches) - 1:
                    found_command = False
                    index = node_index

                    while not found_command:
                        index += 1
                        next_node = self.switches[index]
                        if node in self.switch_data[next_node.name]['command']:
                            switch_index = self.switch_data[next_node.name]['command'].index(node)
                            found_command = True

                    self.switch_data[next_node.name]['command'][switch_index] = command

            # output last switch to command value
            node = self.switches[-1]

            for index, bool in enumerate(self.switch_data[node.name]['bool']):
                self.command_value += bool
                self.command_value += self.switch_data[node.name]['command'][index]

        elif self.input:
            self.command_value += "{command}\n".format(
                tab = "\t"*self.indent,
                command = self.insert_indentation(self.node_logic(self.input)))
        else:
            self.command_value += "{command}\n".format(
                tab = "\t"*self.indent,
                command = self.insert_indentation(self.socket_logic(self.output.inputs[0])))

        self.command_value = self.command_value.replace("\t", "    ")

        # debug
        print("\n*****************")
        print("* Fidget Output *")
        print("*****************\n")
        print(self.command_value)

        self.replace_command()


    def insert_indentation(self, string):
        logic_split = string.split("\n")

        for split_index in range(len(logic_split)):
            logic_split[split_index] = "{tab}{logic}".format(tab="\t"*self.indent, logic=logic_split[split_index])

        return "{logic_joined}\n".format(logic_joined="\n".join(logic_split))

    def node_logic(self, node):
        return getattr(self, node.bl_idname[6:-4].lower())(node)

    def socket_logic(self, socket):
        node = self.get_input(socket)
        return self.node_logic(node) if node else self.no_input(socket)

    def no_input(self, socket):
        # TODO: handle boolean socket type
        return self.command_output(socket)

    def command_output(self, socket):
        return "self.info_text = '{info_text}'\nif event.type == 'LEFTMOUSE' and event.value == '{event_value}':\n\t{command}".format(
            info_text = socket.info_text if socket.node.bl_idname != 'FidgetCommandNode' else socket.node.info_text,
            event_value = socket.event_value if socket.node.bl_idname != 'FidgetCommandNode' else socket.node.event_value,
            command = socket.command if socket.node.bl_idname != 'FidgetCommandNode' else socket.node.command)

    def set_output(self):
        if self.write:
            self.replace_command()
        if self.reset:
            pass

    def replace_command(self):
        code = compile(self.command_value, "", "exec")

        new_command = {}

        exec(code, new_command)

        setattr(getattr(button, "{}_{}".format(self.output.button.lower(), self.output.mode.lower())), "command", new_command['command'])

    def command(self, node):
        if self.base_switch:
            return node
        else:
            return self.command_output(node.outputs[0])

    def script(self, node):
        if self.base_switch:
            return node
        else:
            return ""

    def switch(self, node):
        if self.base_switch:

            self.switches.append(node)

            split = len(node.inputs)//2
            self.switch_data[node.name] = {
                'bool': [self.socket_logic(bool) for bool in node.inputs[:split]],
                'command': [self.socket_logic(command) for command in node.inputs[split:]]}

        return node

    def compare(self, node):
        if self.base_switch:
            return node
        else:
            logic = {
                'AND': lambda a, b: "{bool1} and {bool2}".format(bool1=a, bool2=b),
                'OR': lambda a, b: "{bool1} or {bool2}".format(bool1=a, bool2=b),
                'NAND': lambda a, b: "(not ({bool1} and {bool2}))".format(bool1=a, bool2=b),
                'NOR': lambda a, b: "(not ({bool1} or {bool2}))".format(bool1=a, bool2=b),
                'XOR': lambda a, b: "(({bool1} and not {bool2}) or (not {bool1} and {bool2}))".format(bool1=a, bool2=b),
                'XNOR': lambda a, b: "(not (({bool1} and not {bool2}) or (not {bool1} and {bool2})))".format(bool1=a, bool2=b)}

            bool1 = self.socket_logic(node.inputs[0])
            bool2 = self.socket_logic(node.inputs[1])

            return logic[node.outputs[0].compare_logic](bool1, bool2)

    def activeobject(self, node):
        if self.base_switch:
            return node
        else:
            if node.outputs['Object'].value:
                return "context.active_object"
            else:
                return "(not context.active_object)"

    def activeobjectmode(self, node):
        if self.base_switch:
            return node
        else:
            logic = {
                'OBJECT': "context.active_object.mode == 'OBJECT'",
                'EDIT': "context.active_object.mode == 'EDIT'",
                'SCULPT': "context.active_object.mode == 'SCULPT'",
                'VERTEX_PAINT': "context.active_object.mode == 'VERTEX_PAINT'",
                'WEIGHT_PAINT': "context.active_object.mode == 'WEIGHT_PAINT'",
                'TEXTURE_PAINT': "context.active_object.mode == 'TEXTURE_PAINT'",
                'PARTICLE_EDIT': "context.active_object.mode == 'PARTICLE_EDIT'"}

            return "(context.active_object and {logic})".format(logic=logic[node.outputs[0].active_object_mode])

    def activeobjecttype(self, node):
        if self.base_switch:
            return node
        else:
            logic = {
                'LAMP': "context.active_object.type == 'LAMP'",
                'CAMERA': "context.active_object.type == 'CAMERA'",
                'SPEAKER': "context.active_object.type == 'SPEAKER'",
                'EMPTY': "context.active_object.type == 'EMPTY'",
                'LATTICE': "context.active_object.type == 'LATTICE'",
                'ARMATURE': "context.active_object.type == 'ARMATURE'",
                'FONT': "context.active_object.type == 'FONT'",
                'META': "context.active_object.type == 'META'",
                'SURFACE': "context.active_object.type == 'SURFACE'",
                'CURVE': "context.active_object.type == 'CURVE'",
                'MESH': "context.active_object.type == 'MESH'"}

            return "(context.active_object and {logic})".format(logic=logic[node.outputs[0].object_type])

    def objectsselected(self, node):
        if self.base_switch:
            return node
        else:
            logic = {
                'ANY': "context.selected_objects",
                'EQUAL': "len(context.selected_objects) == ",
                'LESSER': "len(context.selected_objects) < ",
                'LESSEREQUAL': "len(context.selected_objects) <= ",
                'GREATER': "len(context.selected_objects) > ",
                'GREATEREQUAL': "len(context.selected_objects) >= ",
                'NOT': "len(context.selected_objects) != "}

            if node.outputs[0].objects_selected_amount == 'ANY':
                return logic['ANY']
            else:
                return "{relation}{amount}".format(
                    relation = logic[node.relation],
                    amount = node.amount)

    def objectsvisible(self, node):
        if self.base_switch:
            return node
        else:
            logic = {
                'ANY': "context.visible_objects",
                'EQUAL': "len(context.visible_objects) == ",
                'LESSER': "len(context.visible_objects) < ",
                'LESSEREQUAL': "len(context.visible_objects) <= ",
                'GREATER': "len(context.visible_objects) > ",
                'GREATEREQUAL': "len(context.visible_objects) >= ",
                'NOT': "len(context.visible_objects) != "}

            if node.outputs[0].objects_visible_amount == 'ANY':
                return logic['ANY']
            else:
                return "{relation}{amount}".format(
                    relation = logic[node.relation],
                    amount = node.amount)

    def statement(self, node):
        if self.base_switch:
            return node
        else:
            return node.outputs[0].bool_statement

@persistent
def startup_graph_loader(dummy):
    bpy.ops.fidget.load_startup()
    
def nodes_register():
    nodeitems_utils.register_node_categories("FIDGET_NODES", node_categories)
    bpy.app.handlers.load_post.append(startup_graph_loader)

def nodes_unregister():
    nodeitems_utils.unregister_node_categories("FIDGET_NODES")
