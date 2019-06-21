import re
import bpy
import bge_netlogic
from bge_netlogic import utilities as tools
import math


CONDITION_SOCKET_COLOR = tools.Color.RGBA(1.0, 1.0, 0.0, 1.0)

PARAMETER_SOCKET_COLOR = tools.Color.RGBA(0.0, 1.0, 0.0, 1.0)
PARAM_OBJ_SOCKET_COLOR = PARAMETER_SOCKET_COLOR.darker(0.1)
PARAM_SCENE_SOCKET_COLOR = PARAMETER_SOCKET_COLOR.darker(0.2)
PARAM_SOUND_SOCKET_COLOR = tools.Color.RGBA(0.0, 0.0, 1.0, 1.0)

ACTION_SOCKET_COLOR = tools.Color.RGBA(1.0, 0.5, 0.0, 1.0)

CONDITION_NODE_COLOR = CONDITION_SOCKET_COLOR[:-1]
PARAMETER_NODE_COLOR = PARAMETER_SOCKET_COLOR[:-1]
ACTION_NODE_COLOR = ACTION_SOCKET_COLOR[:-1]
PYTHON_NODE_COLOR = tools.Color.RGBA(0.9, 0.9, 0.9, 1.0)[:-1]

_sockets = []
_nodes = []


_enum_local_axis = [
    ("0", "X Axis", "The Local X Axis [Integer Value 0]"),
    ("1", "Y Axis", "The Local Y Axis [Integer Value 1]"),
    ("2", "Z Axis", "The Local Z Axis [Integer Value 2]")
]

_enum_local_oriented_axis = [
    ("0", "+X Axis", "The Local X Axis [Integer Value 0]"),
    ("1", "+Y Axis", "The Local Y Axis [Integer Value 1]"),
    ("2", "+Z Axis", "The Local Z Axis [Integer Value 2]"),
    ("3", "-X Axis", "The Local X Axis [Integer Value 3]"),
    ("4", "-Y Axis", "The Local Y Axis [Integer Value 4]"),
    ("5", "-Z Axis", "The Local Z Axis [Integer Value 5]")
]

_enum_value_filters_3 = [
    ("1", "Range Constraint", "Limit A between B and C [1]")
]


_enum_mouse_wheel_direction = [
    ("1", "Scroll Up", "Mouse Wheel Scrolled Up [1]"),
    ("2", "Scroll Down", "Mouse Wheel Scrolled Down [2]"),
    ("3", "Scroll Up or Down", "Mouse Wheel Scrolled either Up or Down[3]")
]


_enum_ik_mode_values = [
    ("None", "None", "Not set"),
    ("bge.logic.CONSTRAINT_IK_MODE_INSIDE", "Inside", "Keep the bone with IK Distance of target"),
    ("bge.logic.CONSTRAINT_IK_MODE_OUTSIDE", "Outside", "Keep the bone outside IK Distance of target"),
    ("bge.logic.CONSTRAINT_IK_MODE_ONSURFACE", "On Surface", "Keep the bone exactly at IK Distance of the target")
]


_enum_field_value_types = [
    ("NONE", "None", "The None value"),
    ("EXPRESSION", "Expression", "An expression evaluated at initialization time"),
    ("VECTOR", "Vector", "A Vector"),
    ("STRING", "String", "A String"),
    ("FLOAT", "Float", "A Float value"),
    ("INTEGER", "Integer", "An Integer value"),
    ("BOOLEAN", "Bool", "A True/False value")
]
_enum_boolean_values = [
    ("True", "TRUE", "The True value"),
    ("False", "FALSE", "The False value")
]

_enum_numeric_field_value_types = [
    ("NONE", "None", "The None value"),
    ("INTEGER", "Integer", "An Integer value"),
    ("FLOAT", "Float", " A Float value"),
    ("EXPRESSION", "Expression", "A numeric expression")
]

_enum_optional_float_value_types = [
    ("NONE", "None", "No value"),
    ("FLOAT", "Float", "A decimal value"),
    ("EXPRESSION", "Expression", "A numeric expression")
]

_enum_optional_positive_float_value_types = [
    ("NONE", "None", "No value"),
    ("FLOAT", "Float", "A positive decimal value")
]

_enum_add_scene_types = [
    ("1", "Overlay", "Draw on top of the 3D environment"),
    ("0", "Underlay", "Draw as background of the 3D environment")
]

_enum_mouse_motion = [
    ("UP", "Mouse Up", "Mouse moves up"),
    ("DOWN", "Mouse Down", "Mouse moves down"),
    ("LEFT", "Mouse Left", "Mouse moves left"),
    ("RIGHT", "Mouse Right", "Mouse moves right")
]

_enum_loop_count_values = [
    ("ONCE", "No repeat", "Play once when condition is TRUE, then wait for the condition to become TRUE again to play it again."),
    ("INFINITE", "Infinite", "When condition is TRUE, start repeating the sound until stopped."),
    ("CUSTOM", "N times...", "When the condition it TRUE, play the sound N times")
]


_enum_readable_member_names = [
    ("CUSTOM", "By Name", "Type the name of the attribute"),
    ("localPosition", "Local Position", "The local position of the object"),
    ("localOrientation", "Local Orientation", "The local orientation of the object"),
    ("localScale", "Local Scale", "The local scale of the object"),
    ("localTransform", "Local Transform", "The local transform of the object"),
    ("worldPosition", "World Position", "The World Position of the object"),
    ("worldOrientation", "World Orientation", "The World Orientation of the object"),
    ("worldTransform", "World Transform", "The World Transform of the object"),
    ("color", "Object Color", "The solid color of the object"),
    ("name", "Object Name", "The name of the object"),
    ("visible", "Object Visibility Status", "True if the object is set to visible, False if it is set of invisible")
]

_enum_writable_member_names = [
    ("CUSTOM", "By Name", "Type the name of the attribute"),
    ("localPosition", "Local Position", "The local position of the object"),
    ("localOrientation", "Local Orientation", "The local orientation of the object"),
    ("localScale", "Local Scale", "The local scale of the object"),
    ("localTransform", "Local Transform", "The local transform of the object"),
    ("worldPosition", "World Position", "The World Position of the object"),
    ("worldOrientation", "World Orientation", "The World Orientation of the object"),
    ("worldTransform", "World Transform", "The World Transform of the object"),
    ("color", "Object Color", "The solid color of the object")
]

_enum_mouse_buttons = [
    ("bge.events.LEFTMOUSE", "Left Button", "Left Button of the mouse"),
    ("bge.events.MIDDLEMOUSE", "Middle Button", "Middle Button of the mouse"),
    ("bge.events.RIGHTMOUSE", "Right Button", "Right Button of the mouse")
]

_enum_string_ops = [
    ("0", "Postfix", "OUT = STRING + PARAMETER A"),
    ("1", "Prefix", "OUT = PARAMETER A + STRING"),
    ("2", "Infix", "OUT = PARAMETER A + STRING + PARAMETER B"),
    ("3", "Remove Last", "OUT = STRING - LAST CHARACTER"),
    ("4", "Remove First", "OUT = STRING - FIRST CHARACTER"),
    ("5", "Replace", "OUT = STRING with all PARAMETER A occurrences replaced by PARAMETER B"),
    ("6", "Upper Case", "OUT = STRING to upper case"),
    ("7", "Lower Case", "OUT = STRING to lower case"),
    ("8", "Remove Range", "OUT = STRING - the character from index PARAMETER A to index PARAMETER B"),
    ("9", "Insert At", "OUT = STRING + the PARAMETER A inserted ad the index PARAMETER B"),
    ("10", "Length", "OUT = the length (character cout, integer value) of the input STRING"),
    ("11", "Substring", "OUT = the STRING portion from PARAMETER A to PARAMETER B"),
    ("12", "First Index Of", "OUT = the position (integer value) of the first PARAMETER A occurrence in STRING"),
    ("13", "Last Index Of", "OUT = the position (integer value) of the first PARAMETER A occurrence int STRING")
]

_enum_math_operations = [
    ("ADD", "A + B", "Sum A and B"),
    ("SUB", "A - B", "Subtract B from A"),
    ("DIV", "A : B", "Divide A by B"),
    ("MUL", "A x B", "Multiply A by B")
]

_enum_logic_operators = [
    ("0", "A = B", "A equals B [Integer value 0]"),
    ("1", "A != B", "A not equals B [Integer value 1]"),
    ("2", "A > B", "A greater than B [Integer value 2]"),
    ("3", "A < B", "A less than B [Integer value 3]"),
    ("4", "A >= B", "A greater or equal to B [Integer value 4]"),
    ("5", "A <= B", "A less or equal to B [Integer value 5]")
]


_enum_distance_checks = [
    ("0", "AB = Dist", "AB Distance equal to Dist [Integer value 0]"),
    ("1", "AB != Dist", "AB Distance not equal to Dist [Integer value 1]"),
    ("2", "AB > Dist", "AB Distance greater than Dist [Integer value 2]"),
    ("3", "AB < Dist", "AB Distance less than Dist [Integer value 3]"),
    ("4", "AB >= Dist", "AB Distance greater than or equal to Dist [Integer value 4]"),
    ("5", "AB <= Dist", "AB Distance less than or equal to Dist [Integer value 5]"),
]


_enum_play_mode_values = [
    ("bge.logic.KX_ACTION_MODE_PLAY", "Play", "Play the action once"),
    ("bge.logic.KX_ACTION_MODE_LOOP", "Loop", "Loop the action"),
    ("bge.logic.KX_ACTION_MODE_PING_PONG", "Ping Pong", "Play the action in one direction then in the opposite one")
]

_enum_blend_mode_values = [
    ("bge.logic.KX_ACTION_BLEND_BLEND", "Blend", "Blend layers using linear interpolation"),
    ("bge.logic.KX_ACTION_BLEND_ADD", "Add", "Adds the layer together")
]

OUTCELL = "__standard_logic_cell_value__"


def parse_field_value(value_type, value):
    t = value_type
    v = value
    if t == "NONE": return "None"
    if t == "INTEGER":
        try:
            return int(v)
        except ValueError as ex:
            return "0.0"
    if t == "FLOAT":
        try:
            return float(v)
        except ValueError as ex:
            return "0.0"
    if t == "STRING":
        return '"{}"'.format(v)
    if t == "VECTOR":
        numbers = re.findall("[-+]?\d+[\.]?\d*", v)
        if len(numbers) == 2: return "mathutils.Vector(({},{}))".format(numbers[0], numbers[1])
        if len(numbers) == 3: return "mathutils.Vector(({},{},{}))".format(*numbers)
        if len(numbers) == 4: return "mathutils.Vector(({},{},{},{}))".format(*numbers)
        return "mathutils.Vector()"
    if t == "EULER":
        numbers = re.findall("[-+]?\d+[\.]?\d*", v)
        if len(numbers) == 1: return 'mathutils.Euler(({}, 0.0, 0.0), "XYZ")'.format(numbers[0])
        if len(numbers) == 2: return 'mathutils.Euler(({}, {}, 0.0), "XYZ")'.format(numbers[0], numbers[1])
        if len(numbers) == 3: return 'mathutils.Euler(({}, {}, {}), "XYZ")'.format(numbers[0], numbers[1], numbers[2])
        return 'mathutils.Euler((0,0,0), "XYZ")'
    if t == "EXPRESSION":
        return v
    if t == "BOOLEAN":
        return v
    raise ValueError("Cannot parse enum {} type for NLValueFieldSocket".format(t))
    pass

def update_tree_code(self, context):
    bge_netlogic.update_current_tree_code()
    pass

def socket_field(s):
    return parse_field_value(s.value_type, s.value)



def keyboard_key_string_to_bge_key(ks):
    ks = ks.replace("ASTERIX", "ASTER")
    if ks == "NONE": return "None"
    if ks == "RET": ks = "ENTER"
    if ks.startswith("NUMPAD_"):
        ks = ks.replace("NUMPAD_", "PAD")
        if("SLASH" in ks or "ASTER" in ks or "PLUS" in ks):
            ks = ks.replace("SLASH", "SLASHKEY")
            ks = ks.replace("ASTER", "ASTERKEY")
            ks = ks.replace("PLUS", "PLUSKEY")
        return "bge.events.{}".format(ks)
    x = "{}KEY".format(ks.replace("_", ""))
    return "bge.events.{}".format(x)
    pass


class NetLogicType: pass
class NetLogicSocketType:
    def get_unlinked_value(self): raise NotImplementedError()

class NetLogicStatementGenerator(NetLogicType):

    def write_cell_declaration(self, cell_varname, line_writer):
        classname = self.get_netlogic_class_name()
        line_writer.write_line("{} = {}()", cell_varname, classname)

    def write_cell_fields_initialization(self, cell_varname, uids, line_writer):
        for t in self.get_nonsocket_fields():
            field_name = t[0]
            field_value = t[1]
            if callable(field_value): field_value = field_value()
            line_writer.write_line('{}.{} = {}', cell_varname, field_name, field_value)
        for socket in self.inputs: self.write_socket_field_initialization(socket, cell_varname, uids, line_writer)
    def write_socket_field_initialization(self, socket, cell_varname, uids, line_writer):
        input_names = self.get_input_sockets_field_names()
        input_socket_index = self._index_of(socket, self.inputs)
        field_name = None
        if input_names:
            field_name = input_names[input_socket_index]
        else:
            field_name = self.get_field_name_for_socket(socket)
        field_value = None
        if socket.is_linked:
            field_value = self.get_linked_socket_field_value(socket, cell_varname, field_name, uids)
        else:
            field_value = socket.get_unlinked_value()
        line_writer.write_line("{}.{} = {}", cell_varname, field_name, field_value)
        pass

    def get_nonsocket_fields(self):
        """
        Return a list of (field_name, field_value) tuples, where field_name couples to output socket with a cell field
        and field_value is either a value or a no-arg callable producing a value
        :return: the non socket fields initializers
        """
        return []
    def get_input_sockets_field_names(self): return None
    def get_field_name_for_socket(self, socket): 
        print("not implemented in ", self)
        raise NotImplementedError()
    def get_netlogic_class_name(self): raise NotImplementedError()
    def _index_of(self, item, a_iterable):
        i = 0
        for e in a_iterable:
            if e == item: return i
            i += 1
    def get_linked_socket_field_value(self, socket, cell_varname, field_name, uids):
        output_node = socket.links[0].from_socket.node
        assert isinstance(output_node, NetLogicStatementGenerator)
        output_node_varname = uids.get_varname_for_node(socket.links[0].from_socket.node)
        output_socket = socket.links[0].from_socket
        output_map = output_node.get_output_socket_varnames()
        output_socket_index = self._index_of(output_socket, output_node.outputs)
        if output_map:
            varname = output_map[output_socket_index]
            if varname is OUTCELL: return output_node_varname
            else: return '{}.{}'.format(output_node_varname, varname)
        else:
            return output_node_varname
    def get_output_socket_varnames(self): return None
    def update(self): bge_netlogic.update_current_tree_code()
    pass


class NLConditionSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLConditionSocket"
    bl_label = "Condition"
    default_value = bpy.props.StringProperty(default="None")

    def draw_color(self, context, node):
        return CONDITION_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        layout.label(text)

    def get_unlinked_value(self): return self.default_value

    pass
_sockets.append(NLConditionSocket)


class NLParameterSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLParameterSocket"
    bl_label = "Parameter"

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        layout.label(text)

    def get_unlinked_value(self): return "None"
_sockets.append(NLParameterSocket)


class NLActionSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLActionSocket"
    bl_label = "Action"

    def draw_color(self, context, node):
        return ACTION_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        layout.label(text)

    pass
_sockets.append(NLActionSocket)


class NLAbstractNode(NetLogicStatementGenerator):
    @classmethod
    def poll(cls, node_tree):
        enabled = (node_tree.bl_idname == bge_netlogic.ui.BGELogicTree.bl_idname)

    def free(self): pass

    def draw_buttons(self, context, layout): pass

    def draw_buttons_ext(self, context, layout): pass

    def draw_label(self): return self.__class__.bl_label


class NLConditionNode(NLAbstractNode):
    def init(self, context):
        self.use_custom_color = True
        self.color = CONDITION_NODE_COLOR

    pass


class NLActionNode(NLAbstractNode):
    def init(self, context):
        self.use_custom_color = True
        self.color = ACTION_NODE_COLOR

    pass


class NLParameterNode(NLAbstractNode):
    def init(self, context):
        self.use_custom_color = True
        self.color = PARAMETER_NODE_COLOR

    pass


#Sockets
class NLGameObjectSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLGameObjectSocket"
    bl_label = "Game Object"

    def draw_color(self, context, node):
        return PARAM_OBJ_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        layout.label(text)

    def get_unlinked_value(self):
        return "None"
_sockets.append(NLGameObjectSocket)


class NLSocketAlphaFloat(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketAlphaFloat"
    bl_label = "Factor"
    value = bpy.props.FloatProperty(min=0.0, max=1.0, update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)
        pass

    def get_unlinked_value(self):
        return "{}".format(self.value)
_sockets.append(NLSocketAlphaFloat)


class NLSocketSound(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketSound"
    bl_label = "Sound"
    def draw_color(self, context, node):
        return PARAM_SOUND_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        layout.label(text)

    def get_unlinked_value(self):
        return "None"
_sockets.append(NLSocketSound)


class NLSocketLogicOperator(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketLogicOperator"
    bl_label = "Logic Operator"
    value = bpy.props.EnumProperty(items=_enum_logic_operators, update=update_tree_code)
    def draw_color(self, context, node): return PARAMETER_SOCKET_COLOR
    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output: layout.label(text)
        else: layout.prop(self, "value", text=text)
    def get_unlinked_value(self): return "{}".format(self.value)
_sockets.append(NLSocketLogicOperator)


class NLSocketDistanceCheck(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketDistanceCheck"
    bl_label = "Distance Operator"
    value = bpy.props.EnumProperty(items=_enum_distance_checks, update=update_tree_code)
    def draw_color(self, context, node): return PARAMETER_SOCKET_COLOR
    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output: layout.label(text)
        else: layout.prop(self, "value", text=text)
    def get_unlinked_value(self): return "{}".format(self.value)
_sockets.append(NLSocketDistanceCheck)


class NLSocketLoopCount(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketLoopCount"
    bl_label = "Loop Count"
    value = bpy.props.StringProperty(update=update_tree_code)
    def update_value(self, context):
        current_type = self.value_type
        if current_type == "INFINITE":
            self.value = "-1"
        elif current_type == "ONCE":
            self.value = "1"
        elif current_type == "CUSTOM":
            self.value = '{}'.format(self.integer_editor)
        pass
    value_type = bpy.props.EnumProperty(
        items=_enum_loop_count_values,
        update=update_value
    )
    integer_editor = bpy.props.IntProperty(update=update_value, min=1, description="How many times the sound should be repeated when the condition is TRUE")
    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            current_type = self.value_type
            if (current_type == "INFINITE") or (current_type == "ONCE"):
                layout.label(text)
                layout.prop(self, "value_type", text="")
            else:
                layout.prop(self, "integer_editor", text=text)
                layout.prop(self, "value_type", text="")

    def get_unlinked_value(self):
        current_type = self.value_type
        if current_type == "INFINITE": return "-1"
        if current_type == "ONCE": return "0"
        return '{}'.format(self.value)
_sockets.append(NLSocketLoopCount)


class NLBooleanSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLBooleanSocket"
    bl_label = "Boolean"
    value = bpy.props.BoolProperty(update=update_tree_code)
    use_toggle = bpy.props.BoolProperty(default=False)
    true_label = bpy.props.StringProperty()
    false_label = bpy.props.StringProperty()

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            label = text
            status = self.value
            if self.use_toggle:
                if status: label = '{}: ON'.format(text)
                else: label = '{}: OFF'.format(text)
            if self.true_label and status:
                label = self.true_label
            if self.false_label and (not status):
                label = self.false_label
            layout.prop(self, "value", text=label, toggle=self.use_toggle)

    def get_unlinked_value(self): return "True" if self.value else "False"
_sockets.append(NLBooleanSocket)


class NLPositiveFloatSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLPositiveFloatSocket"
    bl_label = "Positive Float"
    value = bpy.props.FloatProperty(min=0.0, update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)

    def get_unlinked_value(self):
        return '{}'.format(self.value)
_sockets.append(NLPositiveFloatSocket)


class NLSocketOptionalPositiveFloat(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketOptionalPositiveFloat"
    bl_label = "Positive Float"
    value = bpy.props.StringProperty(update=update_tree_code)
    def update_value(self, context):
        enum_value = self.value_type
        if enum_value == "NONE": self.value = ""
        else: self.value = '{}'.format(self.float_editor)
        update_tree_code(self, context)
    value_type = bpy.props.EnumProperty(
        update=update_value,
        items=_enum_optional_positive_float_value_types
    )
    float_editor = bpy.props.FloatProperty(
        min=0.0,
        update=update_value
    )
    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            if self.value_type == "NONE":
                layout.prop(self, "value_type", text=text)
            else:
                layout.prop(self, "float_editor", text=text)
                layout.prop(self, "value_type", text="")

    def get_unlinked_value(self):
        try:
            return '{}'.format(float(self.value))
        except ValueError:
            return "None"
_sockets.append(NLSocketOptionalPositiveFloat)


class NLSocketIKMode(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketIKMode"
    bl_label = "IK Mode"
    value = bpy.props.EnumProperty(items=_enum_ik_mode_values, update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)

    def get_unlinked_value(self):
        return self.value
_sockets.append(NLSocketIKMode)


class NLAlphaSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLAlphaSocket"
    bl_label = "Alpha Float"
    value = bpy.props.StringProperty(update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)

    def get_unlinked_value(self):
        if not self.value: return None
        try:
            return float(self.value)
        except ValueError:
            return None
_sockets.append(NLAlphaSocket)


class NLQuotedStringFieldSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLQuotedStringFieldSocket"
    bl_label = "String"
    value = bpy.props.StringProperty(update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)

    def get_unlinked_value(self): return '"{}"'.format(self.value)
    pass
_sockets.append(NLQuotedStringFieldSocket)


class NLIntegerFieldSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLIntegerFieldSocket"
    bl_label = "Integer"
    value = bpy.props.IntProperty(update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def get_unlinked_value(self): return '{}'.format(self.value)

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)
    pass
_sockets.append(NLIntegerFieldSocket)


class NLPositiveIntegerFieldSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLPositiveIntegerFieldSocket"
    bl_label = "Integer"
    value = bpy.props.IntProperty(min=0, default=0, update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)

    def get_unlinked_value(self): return '{}'.format(self.value)
    pass
_sockets.append(NLPositiveIntegerFieldSocket)


class NLSceneSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSceneSocket"
    bl_label = "Scene"

    def draw_color(self, context, node):
        return PARAM_SCENE_SOCKET_COLOR

    def get_unlinked_value(self): return "None"

    def draw(self, context, layout, node, text):
        layout.label(text)
_sockets.append(NLSceneSocket)


class NLValueFieldSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLValueFieldSocket"
    bl_label = "Value"
    def on_type_changed(self, context):
        tp = self.value_type
        if tp == "BOOLEAN":
            self.value = "True" if (self.bool_editor == "True") else "False"
        update_tree_code(self, context)
        pass
    value_type = bpy.props.EnumProperty(items=_enum_field_value_types, update=on_type_changed)
    value = bpy.props.StringProperty(update=update_tree_code)
    def store_boolean_value(self, context):
        self.value = "True" if (self.bool_editor == "True") else "False"
        update_tree_code(self, context)
    bool_editor = bpy.props.EnumProperty(items=_enum_boolean_values, update=store_boolean_value)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def get_unlinked_value(self): return socket_field(self)

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            split = layout.split(0.25)
            split.label(text)
            if self.value_type == "NONE":
                split.prop(self, "value_type", text="")
            elif self.value_type == "BOOLEAN":
                row = split.row(align=True)
                row.prop(self, "value_type", text="")
                row.prop(self, "bool_editor", text="")
            else:
                row = split.row(align=True)
                row.prop(self, "value_type", text="")
                row.prop(self, "value", text="")
_sockets.append(NLValueFieldSocket)


class NLNumericFieldSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLNumericFieldSocket"
    bl_label = "Value"

    value_type = bpy.props.EnumProperty(items=_enum_numeric_field_value_types, update=update_tree_code)
    value = bpy.props.StringProperty(update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def get_unlinked_value(self): return socket_field(self)

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            split = layout.split(0.25)
            split.label(text)
            if self.value_type == "NONE":
                split.prop(self, "value_type", text="")
            else:
                row = split.row(align=True)
                row.prop(self, "value_type", text="")
                row.prop(self, "value", text="")
_sockets.append(NLNumericFieldSocket)


class NLOptionalRadiansFieldSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLOptionalRadiansFieldSocket"
    bl_label = "Value"
    radians = bpy.props.StringProperty(update=update_tree_code, default="0.0")
    def store_radians(self, context):
        self.radians = str(float(self.float_field))
        update_tree_code(self, context)
    def store_expression(self, context):
        self.radians = self.string_field
        update_tree_code(self, context)
    def on_type_change(self, context):
        if self.type == "NONE": self.radians = "None"
        if self.type == "EXPRESSION": self.radians = self.expression_field
        if self.type == "FLOAT": self.radians = str(float(self.input_field))
        update_tree_code(self, context)
    float_field = bpy.props.FloatProperty(update=store_radians)
    expression_field = bpy.props.StringProperty(update=store_expression)
    input_type = bpy.props.EnumProperty(items=_enum_optional_float_value_types,
                                        update=on_type_change, default="FLOAT")

    def draw_color(self, context, node): return PARAMETER_SOCKET_COLOR
    def get_unlinked_value(self):
        return "None" if self.input_type == "NONE" else self.radians
    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            if self.input_type == "FLOAT":
                row = layout.split(0.6)
                row.prop(self, "float_field", text=text)
                row.prop(self, "input_type", text="")
            elif self.input_type == "EXPRESSION":
                row = layout.split(0.6)
                row.prop(self, "expression_field", text=text)
                row.prop(self, "input_type", text="")
            else:
                layout.prop(self, "input_type", text=text)
_sockets.append(NLOptionalRadiansFieldSocket)


class NLSocketReadableMemberName(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketReadableMemberName"
    bl_label = "Att. Name"
    value = bpy.props.StringProperty(update=update_tree_code)

    def _set_value(self, context):
        t = self.value_type
        if t == "CUSTOM": self.value = ""
        else: self.value = t
        bge_netlogic.update_current_tree_code()
    value_type = bpy.props.EnumProperty(items=_enum_readable_member_names, update=_set_value)

    def draw_color(self, context, node):
        return PARAM_SCENE_SOCKET_COLOR

    def get_unlinked_value(self): return '"{}"'.format(self.value)

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            if self.value_type == "CUSTOM":
                row = layout.row(align=True)
                row.prop(self, "value_type", text="")
                row.prop(self, "value", text="")
                pass
            else:
                layout.prop(self, "value_type", text="")
_sockets.append(NLSocketReadableMemberName)


class NLSocketWritableMemberName(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketWritableMemberName"
    bl_label = "Att. Name"
    value = bpy.props.StringProperty(update=update_tree_code)

    def _set_value(self, context):
        t = self.value_type
        if t == "CUSTOM": self.value = ""
        else: self.value = t
        bge_netlogic.update_current_tree_code()
    value_type = bpy.props.EnumProperty(items=_enum_writable_member_names, update=_set_value)

    def draw_color(self, context, node):
        return PARAM_SCENE_SOCKET_COLOR

    def get_unlinked_value(self): return '"{}"'.format(self.value)

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            if self.value_type == "CUSTOM":
                row = layout.row(align=True)
                row.prop(self, "value_type", text="")
                row.prop(self, "value", text="")
                pass
            else:
                layout.prop(self, "value_type", text="")
_sockets.append(NLSocketWritableMemberName)


class NLKeyboardKeySocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLKeyboardKeySocket"
    bl_label = "Key"
    value = bpy.props.StringProperty(update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def get_unlinked_value(self):
        return keyboard_key_string_to_bge_key(self.value)

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            label = self.value
            if not label: label = "Press & Choose"
            layout.operator("bge_netlogic.waitforkey", text=label)
_sockets.append(NLKeyboardKeySocket)


class NLSocketKeyboardKeyPressed(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketKeyboardKeyPressed"
    bl_label = "Key"
    value = bpy.props.StringProperty(update=update_tree_code)

    def draw_color(self, context, node):
        return CONDITION_SOCKET_COLOR

    def get_unlinked_value(self):
        bge_key = keyboard_key_string_to_bge_key(self.value)
        return 'network.add_cell(bgelogic.ConditionKeyPressed(pulse=True, key_code={}))'.format(bge_key)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.label(text)
            label = self.value
            if not label: label = "Press & Choose"
            layout.operator("bge_netlogic.waitforkey", text=label)
_sockets.append(NLSocketKeyboardKeyPressed)


class NLMouseButtonSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLMouseButtonSocket"
    bl_label = "Mouse Button"
    value = bpy.props.EnumProperty(
        items=_enum_mouse_buttons, default="bge.events.LEFTMOUSE",
        update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def get_unlinked_value(self): return self.value

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text="")
_sockets.append(NLMouseButtonSocket)


class NLPlayActionModeSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLPlayActionModeSocket"
    bl_label = "Play Mode"
    value = bpy.props.EnumProperty(
        items= _enum_play_mode_values,
        description="The play mode of the action",
        update=update_tree_code
    )

    def get_unlinked_value(self): return self.value

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)
_sockets.append(NLPlayActionModeSocket)


class NLFloatFieldSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLFloatFieldSocket"
    bl_label = "Float Value"
    value = bpy.props.FloatProperty(default=0,update=update_tree_code)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def get_unlinked_value(self): return "{}".format(self.value)

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)
_sockets.append(NLFloatFieldSocket)


class NLBlendActionModeSocket(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLBlendActionMode"
    bl_label = "Blend Mode"
    value = bpy.props.EnumProperty(
        items=_enum_blend_mode_values,
        description="The blend mode of the action",
        update=update_tree_code
    )

    def get_unlinked_value(self): return self.value;

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)
_sockets.append(NLBlendActionModeSocket)


class NLSocketMouseMotion(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketMouseMotion"
    bl_label = "Mouse Motion"
    value = bpy.props.EnumProperty(items=_enum_mouse_motion, description="The direction of the mouse movement", update=update_tree_code)

    def draw_color(self, context, node):
        return CONDITION_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.label(text)
            layout.prop(self, "value", text="")

    def get_unlinked_value(self):
        if self.value == "UP": return "network.add_cell(bgelogic.ConditionMouseUp(repeat=True))"
        if self.value == "DOWN": return "network.add_cell(bgelogic.ConditionMouseDown(repeat=True))"
        if self.value == "LEFT": return "network.add_cell(bgelogic.ConditionMouseLeft(repeat=True))"
        if self.value == "RIGHT": return "network.add_cell(bgelogic.ConditionMouseRight(repeat=True))"
_sockets.append(NLSocketMouseMotion)


class NLSocketVectorField(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketVectorField"
    bl_label = "Vector"
    value = bpy.props.StringProperty(
        update=update_tree_code,
        description="Default to (0,0,0), type numbers separated by space or comma or anything but a dot")

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.label(text)
            layout.prop(self, "value", text="")

    def get_unlinked_value(self):
        return parse_field_value("VECTOR", self.value)
_sockets.append(NLSocketVectorField)


class NLOptionalSocketVectorField(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLOptionalSocketVectorField"
    bl_label = "Vector"
    value = bpy.props.StringProperty(
        update=update_tree_code,
        description="Default to None, type numbers separated by space or comma or anything but a dot")

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.label(text)
            layout.prop(self, "value", text="")

    def get_unlinked_value(self):
        if not self.value: return "None"
        return parse_field_value("VECTOR", self.value)
_sockets.append(NLOptionalSocketVectorField)


class NLSocketOptionalFilePath(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketOptionalFilePath"
    bl_label = "File"
    value = bpy.props.StringProperty(update=update_tree_code, description="None if empty. Absolute or Relative path. Relative paths start with //")

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "value", text=text)
    def get_unlinked_value(self):
        if not self.value: return "None"
        return '"{}"'.format(self.value)
_sockets.append(NLSocketOptionalFilePath)


class NLSocketOptionalOrientation(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketOptionalOrientation"
    bl_label = "File"
    value = bpy.props.StringProperty(
        update=update_tree_code,
        description="None if empty. 3 numeric values separated by anything but a dot. Can be linked to any orientation or vector value-")

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.label(text)
            layout.prop(self, "value", text="")
    def get_unlinked_value(self):
        if not self.value: return "None"
        return parse_field_value("EULER", self.value)
_sockets.append(NLSocketOptionalOrientation)


class NLSocketMouseWheelDirection(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketMouseWheelDirection"
    bl_label = "Mouse Wheel"
    value = bpy.props.EnumProperty(items=_enum_mouse_wheel_direction, update=update_tree_code)
    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "value", text="")
    def get_unlinked_value(self):
        return self.value
_sockets.append(NLSocketMouseWheelDirection)


class NLSocketFilter3(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketFilter3"
    bl_label = "Filter 3"
    value = bpy.props.EnumProperty(items=_enum_value_filters_3, update=update_tree_code)
    def draw_color(self, context, node): return PARAMETER_SOCKET_COLOR
    def draw(self, context, layout, node, text):
        if self.is_linked: layout.label(text)
        else: layout.prop(self, "value", text="")
    def get_unlinked_value(self): return self.value
_sockets.append(NLSocketFilter3)


class NLSocketLocalAxis(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketLocalAxis"
    bl_label = "Local Axis"
    value = bpy.props.EnumProperty(items=_enum_local_axis, update=update_tree_code)
    def draw_color(self, context, node): return PARAMETER_SOCKET_COLOR
    def draw(self, context, layout, node, text):
        if self.is_linked: layout.label(text)
        else: layout.prop(self, "value", text=text)
    def get_unlinked_value(self): return self.value
_sockets.append(NLSocketLocalAxis)


class NLSocketOrientedLocalAxis(bpy.types.NodeSocket, NetLogicSocketType):
    bl_idname = "NLSocketOrientedLocalAxis"
    bl_label = "Local Axis"
    value = bpy.props.EnumProperty(items=_enum_local_oriented_axis, update=update_tree_code)
    def draw_color(self, context, node): return PARAMETER_SOCKET_COLOR
    def draw(self, context, layout, node, text):
        if self.is_linked: layout.label(text)
        else: layout.prop(self, "value", text=text)
    def get_unlinked_value(self): return self.value
_sockets.append(NLSocketOrientedLocalAxis)


#Parameters
class NLParameterConstantValue(bpy.types.Node, NLParameterNode):
    bl_idname="NLParameterConstantValue"
    bl_label="Value"
    nl_category="Basic Uncategorized Parameters"
    def on_type_changed(self, context):
        tp = self.value_type
        if tp == "BOOLEAN":
            self.value = "True" if (self.bool_editor == "True") else "False"
        update_tree_code(self, context)
        pass
    value_type = bpy.props.EnumProperty(items=_enum_field_value_types, update=on_type_changed)
    value = bpy.props.StringProperty(update=update_tree_code)
    def store_boolean_value(self, context):
        self.value = "True" if (self.bool_editor == "True") else "False"
        update_tree_code(self, context)
    bool_editor = bpy.props.EnumProperty(items=_enum_boolean_values, update=store_boolean_value)

    def draw_color(self, context, node):
        return PARAMETER_SOCKET_COLOR

    def draw_buttons(self, context, layout):
        split = layout
        if self.value_type == "NONE":
            split.prop(self, "value_type", text="")
        elif self.value_type == "BOOLEAN":
            row = split.row(align=True)
            row.prop(self, "value_type", text="")
            row.prop(self, "bool_editor", text="")
        else:
            row = split.row(align=True)
            row.prop(self, "value_type", text="")
            row.prop(self, "value", text="")

    def init(self, context):
        NLParameterNode.init(self, context)
        self.outputs.new(NLParameterSocket.bl_idname, "")
    def get_nonsocket_fields(self):
        v = parse_field_value(self.value_type, self.value)
        return [("value", v)]
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterConstantValue"
_nodes.append(NLParameterConstantValue)


class NLParameterSound(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterSound"
    bl_label = "Sound"
    nl_category = "Basic Sound Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLSocketOptionalFilePath.bl_idname, "File")
        self.outputs.new(NLSocketSound.bl_idname, "Sound")
        self.outputs.new(NLConditionSocket.bl_idname, "Is Playing")
        self.outputs.new(NLParameterSocket.bl_idname, "Current Frame")
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterSound"
    def get_input_sockets_field_names(self):
        return ["file_path"]
    def get_output_socket_varnames(self):
        return [OUTCELL, "IS_PLAYING", "CURRENT_FRAME"]
_nodes.append(NLParameterSound)


class NLParameterValueFilter3(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterValueFilter"
    bl_label = "Filter Value"
    nl_category = "Basic Math Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLSocketFilter3.bl_idname, "Op")
        self.inputs.new(NLValueFieldSocket.bl_idname, "A")
        self.inputs.new(NLValueFieldSocket.bl_idname, "B")
        self.inputs.new(NLValueFieldSocket.bl_idname, "C")
        self.outputs.new(NLParameterSocket.bl_idname, "Out")
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterValueFilter3"
    def get_input_sockets_field_names(self):
        return ["opcode", "parama", "paramb", "paramc"]
_nodes.append(NLParameterValueFilter3)


class NLParameterScreenPosition(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterScreenPosition"
    bl_label = "Screen Position"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object / Vector 3")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Camera")
        self.outputs.new(NLParameterSocket.bl_idname, "Screen X")
        self.outputs.new(NLParameterSocket.bl_idname, "Screen Y")
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterScreenPosition"
    def get_input_sockets_field_names(self):
        return ["game_object", "camera"]
    def get_output_socket_varnames(self):
        return ["xposition", "yposition"]
_nodes.append(NLParameterScreenPosition)


class NLParameterWorldPosition(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterWorldPosition"
    bl_label = "World Position"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLGameObjectSocket.bl_idname, "Camera")
        self.inputs.new(NLFloatFieldSocket.bl_idname, "Screen X")
        self.inputs.new(NLFloatFieldSocket.bl_idname, "Screen Y")
        self.inputs.new(NLFloatFieldSocket.bl_idname, "Depth")
        self.outputs.new(NLParameterSocket.bl_idname, "Vec3 World Position")
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterWorldPosition"
    def get_input_sockets_field_names(self):
        return ["camera", "screen_x", "screen_y", "world_z"]
_nodes.append(NLParameterWorldPosition)

class NLOwnerGameObjectParameterNode(bpy.types.Node, NLParameterNode):
    """The owner of this logic tree. Each GameObject that has this tree installed is the "owner" of a logic tree"""
    bl_idname = "NLOwnerGameObjectParameterNode"
    bl_label = "Owner GameObject"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.outputs.new(NLGameObjectSocket.bl_idname, "")

    def get_netlogic_class_name(self):
        return "bgelogic.ParamOwnerObject"

    pass
_nodes.append(NLOwnerGameObjectParameterNode)


class NLCurrentSceneNode(bpy.types.Node, NLParameterNode):
    bl_idname = "NLCurrentSceneNode"
    bl_label = "Current Scene"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.outputs.new(NLSceneSocket.bl_idname, "")

    def get_netlogic_class_name(self):
        return "bgelogic.ParameterCurrentScene"

    pass
_nodes.append(NLCurrentSceneNode)


class NLGameObjectPropertyParameterNode(bpy.types.Node, NLParameterNode):
    bl_idname = "NLGameObjectPropertyParameterNode"
    bl_label = "Get Game Object Property"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLGameObjectSocket.bl_idname, "Object")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Name")
        self.inputs.new(NLValueFieldSocket.bl_idname, "Default")
        self.outputs.new(NLParameterSocket.bl_idname, "")

    def get_netlogic_class_name(self): return "bgelogic.ParameterObjectProperty"
    def get_input_sockets_field_names(self): return ["game_object", "property_name", "property_default"]
_nodes.append(NLGameObjectPropertyParameterNode)


class NLObjectAttributeParameterNode(bpy.types.Node, NLParameterNode):
    bl_idname = "NLObjectAttributeParameterNode"
    bl_label = "Get Game Object Member"

    def init(self, context):
        NLParameterNode.init(self, context)
        tools.register_inputs(self, NLGameObjectSocket,"Object", NLSocketReadableMemberName, "Name")
        self.outputs.new(NLParameterSocket.bl_idname, "")
    def get_netlogic_class_name(self): return "bgelogic.ParameterObjectAttribute"
    def get_input_sockets_field_names(self):return ["game_object", "attribute_name"]
_nodes.append(NLObjectAttributeParameterNode)


class NLActiveCameraParameterNode(bpy.types.Node, NLParameterNode):
    bl_idname = "NLActiveCameraParameterNode"
    bl_label = "Active Camera"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        tools.register_inputs(self, NLSceneSocket, "Scene")
        self.outputs.new(NLGameObjectSocket.bl_idname, "")
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterActiveCamera"
    def get_input_sockets_field_names(self): return ["scene"]
_nodes.append(NLActiveCameraParameterNode)


class NLArithmeticOpParameterNode(bpy.types.Node, NLParameterNode):
    bl_idname = "NLArithmeticOpParameterNode"
    bl_label = "Arithmetic Op"
    nl_category = "Basic Math Nodes"
    operator = bpy.props.EnumProperty(items=_enum_math_operations, update=update_tree_code)

    def init(self, context):
        NLParameterNode.init(self, context)
        tools.register_inputs(self,
            NLValueFieldSocket, "A",
            NLValueFieldSocket, "B")
        self.outputs.new(NLParameterSocket.bl_idname, "")
    def draw_buttons(self, context, layout):
        layout.prop(self, "operator", text="")
    def get_nonsocket_fields(self):
        return [("operator", lambda : 'bgelogic.ParameterArithmeticOp.op_by_code("{}")'.format(self.operator))]
    def get_netlogic_class_name(self): return "bgelogic.ParameterArithmeticOp"
    def get_input_sockets_field_names(self): return ["operand_a", "operand_b"]
_nodes.append(NLArithmeticOpParameterNode)


class NLParameterActionStatus(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterActionStatus"
    bl_label = "Action Status"
    nl_category = "Basic Animation Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.inputs.new(NLPositiveIntegerFieldSocket.bl_idname, "Layer")
        self.outputs.new(NLConditionSocket.bl_idname, "Is Playing")
        self.outputs.new(NLConditionSocket.bl_idname, "Not Playing")
        self.outputs.new(NLParameterSocket.bl_idname, "Action Name")
        self.outputs.new(NLParameterSocket.bl_idname, "Action Frame")
    def get_netlogic_class_name(self):
         return "bgelogic.ParameterActionStatus"
    def get_input_sockets_field_names(self):
        return ["game_object", "action_layer"]
    def get_output_socket_varnames(self):
        return [OUTCELL, "NOT_PLAYING", "ACTION_NAME", "ACTION_FRAME"]
_nodes.append(NLParameterActionStatus)


class NLParameterSwitchValue(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterSwitchValue"
    bl_label = "Value Switch"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLValueFieldSocket.bl_idname, "A")
        self.inputs.new(NLConditionSocket.bl_idname, "True A, False B")
        self.inputs.new(NLValueFieldSocket.bl_idname, "B")
        self.outputs.new(NLParameterSocket.bl_idname, "A or B")

    def get_netlogic_class_name(self):
        return "bgelogic.ParameterSwitchValue"
    def get_input_sockets_field_names(self):
        return ["param_a", "switch_condition", "param_b"]
_nodes.append(NLParameterSwitchValue)


class NLParameterTimeNode(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterTimeNode"
    bl_label = "Time"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.outputs.new(NLParameterSocket.bl_idname, "Time Per Frame (sec)")
        self.outputs.new(NLParameterSocket.bl_idname, "Timeline (sec)")
    def get_output_socket_varnames(self): return ["TIME_PER_FRAME", "TIMELINE"]
    def get_netlogic_class_name(self): return "bgelogic.ParameterTime"
_nodes.append(NLParameterTimeNode)


class NLMouseDataParameter(bpy.types.Node, NLParameterNode):
    bl_idname = "NLMouseDataParameter"
    bl_label = "Mouse Data"
    nl_category = "Basic Mouse Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.outputs.new(NLParameterSocket.bl_idname, "X")
        self.outputs.new(NLParameterSocket.bl_idname, "Y")
        self.outputs.new(NLParameterSocket.bl_idname, "DX")
        self.outputs.new(NLParameterSocket.bl_idname, "DY")
        self.outputs.new(NLParameterSocket.bl_idname, "DWHEEL")
        self.outputs.new(NLParameterSocket.bl_idname, "(X,Y,0)")
        self.outputs.new(NLParameterSocket.bl_idname, "(DX,DY,0)")

    def get_netlogic_class_name(self):
        return "bgelogic.ParameterMouseData"

    def get_output_socket_varnames(self):
        return ["MX", "MY", "MDX", "MDY", "MDWHEEL", "MXY0", "MDXY0"]
_nodes.append(NLMouseDataParameter)


class NLParameterOrientationNode(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterOrientationNode"
    bl_label = "Orientation"
    nl_category = "Basic Math Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLOptionalRadiansFieldSocket.bl_idname, "X Rad")
        self.inputs.new(NLOptionalRadiansFieldSocket.bl_idname, "Y Rad")
        self.inputs.new(NLOptionalRadiansFieldSocket.bl_idname, "Z Rad")
        self.inputs.new(NLParameterSocket.bl_idname, "Orientation")
        tools.register_outputs(
            self,
            NLParameterSocket, "Orientation",
            NLParameterSocket, "XYZ Rad Euler",
            NLParameterSocket, "X Rad", NLParameterSocket, "Y Rad", NLParameterSocket, "Z Rad",
        )

    def get_netlogic_class_name(self): return "bgelogic.ParameterOrientation"
    def get_output_socket_varnames(self): return [OUTCELL, "OUTEULER", "OUTX", "OUTY", "OUTZ"]
    def get_input_sockets_field_names(self): return ["input_x", "input_y", "input_z", "source_matrix"]
_nodes.append(NLParameterOrientationNode)


class NLParameterBoneStatus(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterBoneStatus"
    bl_label = "Armature Bone Status"
    nl_category = "Basic Armature Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLGameObjectSocket.bl_idname, "Armature Object")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Bone Name")
        self.outputs.new(NLParameterSocket.bl_idname, "XYZ Pos")
        self.outputs.new(NLParameterSocket.bl_idname, "XYZ Rot")
        self.outputs.new(NLParameterSocket.bl_idname, "XYZ Scale")
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterBoneStatus"
    def get_input_sockets_field_names(self):
        return ["armature", "bone_name"]
    def get_output_socket_varnames(self):
        return ["XYZ_POS","XYZ_ROT", "XYZ_SCA"]
_nodes.append(NLParameterBoneStatus)


class NLParameterPythonModuleFunction(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterPythonModuleFunction"
    bl_label = "Python Module Function"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Module")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Member")
        self.inputs.new(NLParameterSocket.bl_idname, "IN0")
        self.inputs.new(NLParameterSocket.bl_idname, "IN1")
        self.inputs.new(NLParameterSocket.bl_idname, "IN2")
        self.inputs.new(NLParameterSocket.bl_idname, "IN3")
        self.outputs.new(NLParameterSocket.bl_idname, "OUT0")
        self.outputs.new(NLParameterSocket.bl_idname, "OUT1")
        self.outputs.new(NLParameterSocket.bl_idname, "OUT2")
        self.outputs.new(NLParameterSocket.bl_idname, "OUT3")
        self.use_custom_color = True
        self.color = PYTHON_NODE_COLOR
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterPythonModuleFunction"
    def get_input_sockets_field_names(self): return ["module_name", "module_func", "IN0", "IN1", "IN2", "IN3"]
    def get_output_socket_varnames(self): return ["OUT0", "OUT1", "OUT2", "OUT3"]
_nodes.append(NLParameterPythonModuleFunction)


class NLParameterVectorNode(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterVectorNode"
    bl_label = "Vector"
    nl_category = "Basic Math Nodes"

    def init(self, context):
        NLParameterNode.init(self, context)
        tools.register_inputs(
            self,
            NLNumericFieldSocket, "X",
            NLNumericFieldSocket, "Y",
            NLNumericFieldSocket, "Z",
            NLParameterSocket, "Vector"
        )
        self.outputs.new(NLParameterSocket.bl_idname, "X")
        self.outputs.new(NLParameterSocket.bl_idname, "Y")
        self.outputs.new(NLParameterSocket.bl_idname, "Z")
        self.outputs.new(NLParameterSocket.bl_idname, "Vector")
        self.outputs.new(NLParameterSocket.bl_idname, "Normalized Vec")

    def get_netlogic_class_name(self): return "bgelogic.ParameterVector"
    def get_output_socket_varnames(self): return ["OUTX", "OUTY", "OUTZ", "OUTV", "NORMVEC"]
    def get_input_sockets_field_names(self): return ["input_x", "input_y", "input_z", "input_vector"]
_nodes.append(NLParameterVectorNode)


class NLParameterVector4Node(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterVector4Node"
    bl_label = "Vector 4"
    nl_category = "Basic Math Nodes"
    
    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLNumericFieldSocket.bl_idname, "X")
        self.inputs.new(NLNumericFieldSocket.bl_idname, "Y")
        self.inputs.new(NLNumericFieldSocket.bl_idname, "Z")
        self.inputs.new(NLNumericFieldSocket.bl_idname, "W")
        self.inputs.new(NLParameterSocket.bl_idname, "Vector (3/4)")
        self.outputs.new(NLParameterSocket.bl_idname, "X")
        self.outputs.new(NLParameterSocket.bl_idname, "Y")
        self.outputs.new(NLParameterSocket.bl_idname, "Z")
        self.outputs.new(NLParameterSocket.bl_idname, "W")
        self.outputs.new(NLParameterSocket.bl_idname, "Vector4")
    def draw_buttons(self, context, layout):
        pass
    def get_netlogic_class_name(self): return "bgelogic.ParameterVector4"
    def get_output_socket_varnames(self): return ["OUTX","OUTY","OUTZ","OUTV","OUTVEC"]
    def get_input_sockets_field_names(self): return ["in_x", "in_y", "in_z", "in_w", "in_vec"]
_nodes.append(NLParameterVector4Node)


#Conditions
class NLAlwaysConditionNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLAlwaysConditionNode"
    bl_label = "Always"
    repeat = bpy.props.BoolProperty(update=update_tree_code)

    def init(self, context):
        NLConditionNode.init(self, context)
        self.outputs.new(NLConditionSocket.bl_idname, "Always")

    def draw_buttons(self, context, layout):
        layout.prop(self, "repeat", text="Repeat: ON" if self.repeat else "Repeat: OFF", toggle=True)

    def get_netlogic_class_name(self):
        return "bgelogic.ConditionAlways"

    def write_cell_fields_initialization(self, cell_varname, uids, line_writer):
        NetLogicStatementGenerator.write_cell_fields_initialization(self, cell_varname, uids, line_writer)
        line_writer.write_line("{}.{} = {}", cell_varname, "repeat", self.repeat)
        pass
    pass
_nodes.append(NLAlwaysConditionNode)


class NLKeyPressedCondition(bpy.types.Node, NLConditionNode):
    bl_idname = "NLKeyPressedCondition"
    bl_label = "Key Pressed"
    nl_category = "Basic Keyboard Nodes"
    pulse = bpy.props.BoolProperty(
        description="ON: True until the key is released, OFF: True when pressed, then False until pressed again",
        update=update_tree_code)

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLKeyboardKeySocket.bl_idname, "")
        self.outputs.new(NLConditionSocket.bl_idname, "If Pressed")

    def draw_buttons(self, context, layout):
        layout.prop(self, "pulse", text="Pulse: ON" if self.pulse else "Pulse: OFF", toggle=True)

    def get_netlogic_class_name(self): return "bgelogic.ConditionKeyPressed"
    def get_input_sockets_field_names(self): return ["key_code"]
    def write_cell_fields_initialization(self, cell_varname, uids, line_writer):
        NetLogicStatementGenerator.write_cell_fields_initialization(self, cell_varname, uids, line_writer)
        line_writer.write_line("{}.{} = {}", cell_varname, "pulse", self.pulse)
    pass
_nodes.append(NLKeyPressedCondition)


class NLKeyLoggerAction(bpy.types.Node, NLActionNode):
    bl_idname = "NLKeyLoggerAction"
    bl_label = "Key Logger"
    nl_category = "Basic Keyboard Nodes"
    
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.outputs.new(NLConditionSocket.bl_idname, "Key Logged")
        self.outputs.new(NLParameterSocket.bl_idname, "Key Code")
        self.outputs.new(NLParameterSocket.bl_idname, "Logged Char")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionKeyLogger"
    def get_input_sockets_field_names(self):
        return ["condition"]
    def get_output_socket_varnames(self):
        return ["KEY_LOGGED", "KEY_CODE", "CHARACTER"]
    pass
_nodes.append(NLKeyLoggerAction)


class NLKeyReleasedCondition(bpy.types.Node, NLConditionNode):
    bl_idname = "NLKeyReleasedCondition"
    bl_label = "Key Released"
    nl_category = "Basic Keyboard Nodes"
    pulse = bpy.props.BoolProperty(
        description="ON: True until the key is released, OFF: True when pressed, then False until pressed again", default=True,
        update=update_tree_code)

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLKeyboardKeySocket.bl_idname, "")
        self.outputs.new(NLConditionSocket.bl_idname, "If Released")

    def draw_buttons(self, context, layout):
        layout.prop(self, "pulse", text="Pulse: ON" if self.pulse else "Pulse: OFF", toggle=True)

    def get_netlogic_class_name(self): return "bgelogic.ConditionKeyReleased"
    def get_input_sockets_field_names(self): return ["key_code"]
    def write_cell_fields_initialization(self, cell_varname, uids, line_writer):
        NetLogicStatementGenerator.write_cell_fields_initialization(self, cell_varname, uids, line_writer)
        line_writer.write_line("{}.{} = {}", cell_varname, "pulse", self.pulse)
    pass
_nodes.append(NLKeyReleasedCondition)


class NLMousePressedCondition(bpy.types.Node, NLConditionNode):
    bl_idname = "NLMousePressedCondition"
    bl_label = "Mouse Pressed"
    nl_category = "Basic Mouse Nodes"

    pulse = bpy.props.BoolProperty(
        description="ON: True until the button is released, OFF: True when pressed, then False until pressed again", default=False,
        update=update_tree_code)

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLMouseButtonSocket.bl_idname, "")
        self.outputs.new(NLConditionSocket.bl_idname, "If Pressed")

    def draw_buttons(self, context, layout):
        layout.prop(self, "pulse", text="Pulse: ON" if self.pulse else "Pulse: OFF", toggle=True)

    def get_netlogic_class_name(self): return "bgelogic.ConditionMousePressed"
    def get_input_sockets_field_names(self): return ["mouse_button_code"]
    def write_cell_fields_initialization(self, cell_varname, uids, line_writer):
        NetLogicStatementGenerator.write_cell_fields_initialization(self, cell_varname, uids, line_writer)
        line_writer.write_line("{}.{} = {}", cell_varname, "pulse", self.pulse)
    pass
_nodes.append(NLMousePressedCondition)


class NLMouseReleasedCondition(bpy.types.Node, NLConditionNode):
    bl_idname = "NLMouseReleasedCondition"
    bl_label = "Mouse Released"
    nl_category = "Basic Mouse Nodes"

    pulse = bpy.props.BoolProperty(
        description="ON: True until the button is released, OFF: True when pressed, then False until pressed again", default=False,
        update=update_tree_code)

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLMouseButtonSocket.bl_idname, "")
        self.outputs.new(NLConditionSocket.bl_idname, "If Released")

    def draw_buttons(self, context, layout):
        layout.prop(self, "pulse", text="Pulse: ON" if self.pulse else "Pulse: OFF", toggle=True)

    def get_netlogic_class_name(self): return "bgelogic.ConditionMouseReleased"
    def get_input_sockets_field_names(self): return ["mouse_button_code"]

    def write_cell_fields_initialization(self, cell_varname, uids, line_writer):
        NetLogicStatementGenerator.write_cell_fields_initialization(self, cell_varname, uids, line_writer)
        line_writer.write_line("{}.{} = {}", cell_varname, "pulse", self.pulse)
    pass
_nodes.append(NLMouseReleasedCondition)


class NLConditionOnceNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionOnceNode"
    bl_label = "Once"

    def init(self, context):
        NLConditionNode.init(self, context)
        tools.register_inputs(self, NLConditionSocket, "Condition")
        tools.register_outputs(self, NLConditionSocket, "If true, once")

    def get_netlogic_class_name(self):
        return "bgelogic.ConditionOnce"
    def get_input_sockets_field_names(self): return ["input_condition"]
_nodes.append(NLConditionOnceNode)


class NLConditionMousePressedOn(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionMousePressedOn"
    bl_label = "Mouse Pressed On"
    nl_category = "Basic Mouse Nodes"

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLMouseButtonSocket.bl_idname, "Mouse Button")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.outputs.new(NLConditionSocket.bl_idname, "When Pressed On")
    def get_netlogic_class_name(self):
        return "bgelogic.ConditionMousePressedOn"
    def get_input_sockets_field_names(self):
        return ["mouse_button", "game_object"]
_nodes.append(NLConditionMousePressedOn)


class NLConditionMouseWheelMoved(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionMouseWheelMoved"
    bl_label = "Mouse Wheel Moved"
    nl_category = "Basic Mouse Nodes"

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLSocketMouseWheelDirection.bl_idname, "")
        self.outputs.new(NLConditionSocket.bl_idname, "When Scrolled")
    def get_netlogic_class_name(self):
        return "bgelogic.ConditionMouseScrolled"
    def get_input_sockets_field_names(self):
        return ["wheel_direction"]
_nodes.append(NLConditionMouseWheelMoved)


class NLConditionCollisionNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionCollisionNode"
    bl_label = "Collision"

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.outputs.new(NLConditionSocket.bl_idname, "When Colliding")
        self.outputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.outputs.new(NLParameterSocket.bl_idname, "Point")
        self.outputs.new(NLParameterSocket.bl_idname, "Normal")
        self.outputs.new(NLParameterSocket.bl_idname, "Game Object Set")
        self.outputs.new(NLParameterSocket.bl_idname, "(Obj,Pt,Norm) Set")

    def get_netlogic_class_name(self):
        return "bgelogic.ConditionCollision"
    def get_input_sockets_field_names(self): return ["game_object"]
    def get_output_socket_varnames(self): return [OUTCELL, "TARGET", "POINT", "NORMAL", "OBJECTS", "OPN_SET"]
_nodes.append(NLConditionCollisionNode)


class NLConditionMouseTargetingNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionMouseTargetingNode"
    bl_label = "Mouse Targeting"
    nl_category = "Basic Mouse Nodes"

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLGameObjectSocket.bl_idname, "GameObject")
        self.outputs.new(NLConditionSocket.bl_idname, "On Mouse Enter")
        self.outputs.new(NLConditionSocket.bl_idname, "On Mouse Over")
        self.outputs.new(NLConditionSocket.bl_idname, "On Mouse Exit")
        self.outputs.new(NLParameterSocket.bl_idname, "Point")
        self.outputs.new(NLParameterSocket.bl_idname, "Normal")
    def get_netlogic_class_name(self):
        return "bgelogic.ConditionMouseTargeting"
    def get_input_sockets_field_names(self): return ["game_object"]
    def get_output_socket_varnames(self): return ["MOUSE_ENTERED", "MOUSE_OVER", "MOUSE_EXITED", "POINT", "NORMAL"]
_nodes.append(NLConditionMouseTargetingNode)


class NLConditionAndNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionAndNode"
    bl_label = "And"

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "A")
        self.inputs.new(NLConditionSocket.bl_idname, "B")
        self.outputs.new(NLConditionSocket.bl_idname, "A and B")

    def get_netlogic_class_name(self): return "bgelogic.ConditionAnd"
    def get_input_sockets_field_names(self):return ["condition_a", "condition_b"]
_nodes.append(NLConditionAndNode)


class NLConditionOrNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionOrNode"
    bl_label = "Or"

    def init(self, context):
        NLConditionNode.init(self, context)
        tools.register_inputs(self, NLConditionSocket, "A", NLConditionSocket, "B")
        tools.register_outputs(self, NLConditionSocket, "A or B")

    def get_netlogic_class_name(self): return "bgelogic.ConditionOr"
    def get_input_sockets_field_names(self): return ["condition_a", "condition_b"]
_nodes.append(NLConditionOrNode)


class NLConditionOrList(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionOrList"
    bl_label = "Or List"
    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "A")
        self.inputs[-1].default_value = "False"
        self.inputs.new(NLConditionSocket.bl_idname, "B")
        self.inputs[-1].default_value = "False"
        self.inputs.new(NLConditionSocket.bl_idname, "C")
        self.inputs[-1].default_value = "False"
        self.inputs.new(NLConditionSocket.bl_idname, "D")
        self.inputs[-1].default_value = "False"
        self.inputs.new(NLConditionSocket.bl_idname, "E")
        self.inputs[-1].default_value = "False"
        self.inputs.new(NLConditionSocket.bl_idname, "F")
        self.inputs[-1].default_value = "False"
        self.outputs.new(NLConditionSocket.bl_idname, "Or...")
    def get_netlogic_class_name(self): return "bgelogic.ConditionOrList"
    def get_input_sockets_field_names(self): return ["ca", "cb", "cc", "cd", "ce", "cf"]
_nodes.append(NLConditionOrList)


class NLConditionAndList(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionAndList"
    bl_label = "And List"
    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "A")
        self.inputs[-1].default_value = "True"
        self.inputs.new(NLConditionSocket.bl_idname, "B")
        self.inputs[-1].default_value = "True"
        self.inputs.new(NLConditionSocket.bl_idname, "C")
        self.inputs[-1].default_value = "True"
        self.inputs.new(NLConditionSocket.bl_idname, "D")
        self.inputs[-1].default_value = "True"
        self.inputs.new(NLConditionSocket.bl_idname, "E")
        self.inputs[-1].default_value = "True"
        self.inputs.new(NLConditionSocket.bl_idname, "F")
        self.inputs[-1].default_value = "True"
        self.outputs.new(NLConditionSocket.bl_idname, "And...")
    def get_netlogic_class_name(self): return "bgelogic.ConditionAndList"
    def get_input_sockets_field_names(self): return ["ca", "cb", "cc", "cd", "ce", "cf"]
_nodes.append(NLConditionAndList)



class NLConditionValueTriggerNode(bpy.types.Node, NLConditionNode):
    """When input becomes trigger, sends a true signal"""
    bl_idname = "NLConditionValueTriggerNode"
    bl_label = "Value Changed To"

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLParameterSocket.bl_idname, "Value")
        self.inputs.new(NLValueFieldSocket.bl_idname, "To")
        self.inputs[-1].value_type = "BOOLEAN"
        self.inputs[-1].value = "True"
        self.outputs.new(NLConditionSocket.bl_idname, "When Changed To")

    def get_netlogic_class_name(self):
        return "bgelogic.ConditionValueTrigger"
    def get_input_sockets_field_names(self):
        return ["monitored_value", "trigger_value"]
_nodes.append(NLConditionValueTriggerNode)


class NLConditionLogicOperation(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionLogicOperation"
    bl_label = "Logic Operations"
    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLSocketLogicOperator.bl_idname, "Op")
        self.inputs.new(NLValueFieldSocket.bl_idname, "A")
        self.inputs.new(NLValueFieldSocket.bl_idname, "B")
        self.outputs.new(NLConditionSocket.bl_idname, "If A op B")
    def get_netlogic_class_name(self): return "bgelogic.ConditionLogicOp"
    def get_input_sockets_field_names(self): return ["operator", "param_a", "param_b"]
_nodes.append(NLConditionLogicOperation)


class NLConditionDistanceCheck(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionDistanceCheck"
    bl_label = "Check Distance"
    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLSocketDistanceCheck.bl_idname, "Check")
        self.inputs.new(NLSocketVectorField.bl_idname, "A")
        self.inputs.new(NLSocketVectorField.bl_idname, "B")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Dist.")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Hyst.")
        self.outputs.new(NLConditionSocket.bl_idname, "Out")
    def get_netlogic_class_name(self): return "bgelogic.ConditionDistanceCheck"
    def get_input_sockets_field_names(self): return ["operator", "param_a", "param_b", "dist", "hyst"]
_nodes.append(NLConditionDistanceCheck)


class NLConditionValueChanged(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionValueChanged"
    bl_label = "Value Changed"
    initialize = bpy.props.BoolProperty(
        description="When ON, skip the first change. When OFF, compare the first value to None",
        update=update_tree_code)

    def init(self, context):
        NLConditionNode.init(self, context)
        tools.register_inputs(self, NLParameterSocket, "Value")
        self.outputs.new(NLConditionSocket.bl_idname, "If Changed")
        self.outputs.new(NLParameterSocket.bl_idname, "Old Value")
        self.outputs.new(NLParameterSocket.bl_idname, "New Value")
    def draw_buttons(self, context, layout):
        layout.prop(self, "initialize", text="Initialize: ON" if self.initialize else "Initialize: OFF", toggle=True)
    def get_netlogic_class_name(self): return "bgelogic.ConditionValueChanged"
    def get_input_sockets_field_names(self): return ["current_value"]
    def get_nonsocket_fields(self): return [("initialize", lambda: "True" if self.initialize else "False")]
    def get_output_socket_varnames(self):
        return [OUTCELL, "PREVIOUS_VALUE", "CURRENT_VALUE"]
_nodes.append(NLConditionValueChanged)


class NLConditionTimeElapsed(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionTimeElapsed"
    bl_label = "Time Elapsed"
    nl_category = "Basic Time Nodes"

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLBooleanSocket.bl_idname, "Repeat")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Seconds")
        self.outputs.new(NLConditionSocket.bl_idname, "When Elapsed")
        pass
    def get_netlogic_class_name(self): return "bgelogic.ConditionTimeElapsed"
    def get_input_sockets_field_names(self):return ["repeat", "delta_time"]
_nodes.append(NLConditionTimeElapsed)


class NLConditionNotNoneNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionNotNoneNode"
    bl_label = "Not None"

    def init(self, context):
        NLConditionNode.init(self, context)
        tools.register_inputs(self, NLParameterSocket, "Value")
        tools.register_outputs(self, NLConditionSocket, "If Not None")

    def get_netlogic_class_name(self): return "bgelogic.ConditionNotNone"
    def get_input_sockets_field_names(self): return ["checked_value"]
_nodes.append(NLConditionNotNoneNode)


class NLConditionNoneNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionNone"
    bl_label ="None"
    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLParameterSocket.bl_idname, "Value")
        self.outputs.new(NLConditionSocket.bl_idname, "If None")
    def get_netlogic_class_name(self): return "bgelogic.ConditionNone"
    def get_input_sockets_field_names(self): return ["checked_value"]
_nodes.append(NLConditionNoneNode)


class NLConditionNotNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionNotNode"
    bl_label = "Not"

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLBooleanSocket.bl_idname, "Pulse")
        self.inputs[-1].use_toggle = True
        self.outputs.new(NLConditionSocket.bl_idname, "If Not")

    def get_netlogic_class_name(self): return "bgelogic.ConditionNot"
    def get_input_sockets_field_names(self):
        return ["condition", "pulse"]
_nodes.append(NLConditionNotNode)

class NLConditionLogicNetworkStatusNode(bpy.types.Node, NLConditionNode):
    bl_idname = "NLConditionLogitNetworkStatusNode"
    bl_label = "Logic Network Status"
    nl_category = "Basic Logic Tree Nodes"

    def init(self, context):
        NLConditionNode.init(self, context)
        self.inputs.new(NLGameObjectSocket.bl_idname, "GameObject")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Tree Name")
        self.outputs.new(NLConditionSocket.bl_idname, "If Running")
        self.outputs.new(NLConditionSocket.bl_idname, "If Stopped")
    def get_netlogic_class_name(self): return "bgelogic.ConditionLNStatus"
    def get_input_sockets_field_names(self): return ["game_object", "tree_name"]
    def get_output_socket_varnames(self): return ["IFRUNNING", "IFSTOPPED"]
_nodes.append(NLConditionLogicNetworkStatusNode)

#Actions
class NLAddObjectActionNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLAddObjectActionNode"
    bl_label = "Add Object"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLSceneSocket.bl_idname, "Scene")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Name")
        self.inputs.new(NLPositiveIntegerFieldSocket.bl_idname, "Life")
        self.outputs.new(NLGameObjectSocket.bl_idname, "Added Object")

    def get_netlogic_class_name(self): return "bgelogic.ActionAddObject"
    def get_input_sockets_field_names(self): return ["condition", "scene", "name", "life"]
_nodes.append(NLAddObjectActionNode)


class NLSetGameObjectGamePropertyActionNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLSetGameObjectGamePropertyActionNode"
    bl_label = "Set Game Object Property"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Name")
        self.inputs.new(NLValueFieldSocket.bl_idname, "Value")

    def get_netlogic_class_name(self): return "bgelogic.ActionSetGameObjectGameProperty"
    def get_input_sockets_field_names(self): return ["condition", "game_object", "property_name", "property_value"]
_nodes.append(NLSetGameObjectGamePropertyActionNode)


class NLSetObjectAttributeActionNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLSetObjectAttributeActionNode"
    bl_label = "Set Game Object Member"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.inputs.new(NLSocketWritableMemberName.bl_idname, "Name")
        self.inputs.new(NLValueFieldSocket.bl_idname, "Value")

    def get_netlogic_class_name(self): return "bgelogic.ActionSetObjectAttribute"
    def get_input_sockets_field_names(self): return ["condition", "game_object", "attribute_name", "attribute_value"]
_nodes.append(NLSetObjectAttributeActionNode)


class NLActionRayCastNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionRayCastNode"
    bl_label = "Ray Pick"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLParameterSocket.bl_idname, "Origin")
        self.inputs.new(NLParameterSocket.bl_idname, "Destination")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Property")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Distance")
        self.inputs[-1].value = 100.0
        self.outputs.new(NLConditionSocket.bl_idname, "Has Result")
        self.outputs.new(NLGameObjectSocket.bl_idname, "Picked Object")
        self.outputs.new(NLParameterSocket.bl_idname, "Picked Point")
        self.outputs.new(NLParameterSocket.bl_idname, "Picked Normal")
        self.outputs.new(NLParameterSocket.bl_idname, "Ray Direction")

    def get_netlogic_class_name(self):
        return "bgelogic.ActionRayPick"
    def get_input_sockets_field_names(self):
        return ["condition", "origin", "destination", "property_name", "distance"]
    def get_output_socket_varnames(self):
        return [OUTCELL, "PICKED_OBJECT", "POINT", "NORMAL", "DIRECTION"]
_nodes.append(NLActionRayCastNode)


#TODO: should we reset conditions that have been consumed? Like a "once" condition. I'd say no
class NLStartLogicNetworkActionNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLStartLogicNetworkActionNode"
    bl_label = "Start A Logic Network"
    nl_category = "Basic Logic Tree Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        tools.register_inputs(self,
            NLConditionSocket, "Condition",
            NLGameObjectSocket, "GameObject",
            NLQuotedStringFieldSocket, "Tree Name")

    def get_netlogic_class_name(self): return "bgelogic.ActionStartLogicNetwork"
    def get_input_sockets_field_names(self): return ["condition", "game_object", "logic_network_name"]
_nodes.append(NLStartLogicNetworkActionNode)


class NLStopLogicNetworkActionNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLStopLogicNetworkActionNode"
    bl_label = "Stop a Logic Network"
    nl_category = "Basic Logic Tree Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        tools.register_inputs(self,
            NLConditionSocket, "Condition",
            NLGameObjectSocket, "GameObject",
            NLQuotedStringFieldSocket, "Tree Name")

    def get_netlogic_class_name(self): return "bgelogic.ActionStopLogicNetwork"
    def get_input_sockets_field_names(self): return ["condition", "game_object", "logic_network_name"]
_nodes.append(NLStopLogicNetworkActionNode)


class NLActionRepeater(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionRepeater"
    bl_label = "Repeater"
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLParameterSocket.bl_idname, "Input Set")
        self.outputs.new(NLParameterSocket.bl_idname, "Output Step 0")
        self.outputs.new(NLParameterSocket.bl_idname, "Output Step 1")
        self.outputs.new(NLParameterSocket.bl_idname, "Output Step 2")
        self.outputs.new(NLParameterSocket.bl_idname, "Output Step 3")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionRepeater"
    def get_input_sockets_field_names(self):
        return ["condition", "input_value"]
    def write_cell_fields_initialization(self, cell_varname, uids, line_writer):
        super(NLActionRepeater, self).write_cell_fields_initialization(cell_varname, uids, line_writer)
        outpass_0 = self.outputs[0]
        outpass_1 = self.outputs[1]
        outpass_2 = self.outputs[2]
        outpass_3 = self.outputs[3]
        outputs = [outpass_0, outpass_1, outpass_2, outpass_3]
        for output_socket in outputs:
            if output_socket.is_linked:
                for output_link in output_socket.links:
                    output_target = output_link.to_socket.node
                    output_uid = uids.get_varname_for_node(output_target)
                    line_writer.write_line("{}.output_cells.append({})", cell_varname, output_uid)
                    uids.remove_cell_from_tree(output_uid)
_nodes.append(NLActionRepeater)


class NLActionSetGameObjectVisibility(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSetGameObjectVisibility"
    bl_label = "Set Object Visibility"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.inputs.new(NLBooleanSocket.bl_idname, "Visible")
        socket = self.inputs[-1]
        socket.use_toggle = True
        socket.true_label = "Visible"
        socket.false_label = "Not Visibile"
        self.inputs.new(NLBooleanSocket.bl_idname, "Include Children")
    def get_netlogic_class_name(self): return "bgelogic.ActionSetGameObjectVisibility"
    def get_input_sockets_field_names(self): return ["condition", "game_object", "visible", "recursive"]
_nodes.append(NLActionSetGameObjectVisibility)


class NLActionFindObjectNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionFindObjectNode"
    bl_label = "Find GameObject"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        tools.register_inputs(self,
            NLConditionSocket, "Optional Condition",
            NLSceneSocket, "From Scene",
            NLGameObjectSocket, "From Parent",
            NLQuotedStringFieldSocket, "Query")
        self.outputs.new(NLGameObjectSocket.bl_idname, "GameObject")
        self.outputs.new(NLGameObjectSocket.bl_idname, "Parent Object")
        self.outputs.new(NLGameObjectSocket.bl_idname, "Branch Root")

    def get_netlogic_class_name(self): return "bgelogic.ActionFindObject"
    def get_input_sockets_field_names(self): return ["condition", "scene", "from_parent", "query"]
    def get_output_socket_varnames(self):
        return [OUTCELL, "PARENT", "BRANCH_ROOT"]
_nodes.append(NLActionFindObjectNode)


class NLActionSetActiveCamera(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSetActiveCamera"
    bl_label = "Set Active Camera"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        tools.register_inputs(self, NLConditionSocket, "Condition",
                              NLSceneSocket, "Scene",
                              NLGameObjectSocket, "Camera")

    def get_netlogic_class_name(self): return "bgelogic.ActionSetActiveCamera"
    def get_input_sockets_field_names(self): return ["condition", "scene", "camera"]
_nodes.append(NLActionSetActiveCamera)


class NLActionAddScene(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionAddScene"
    bl_label = "Add Scene"
    nl_category = "Basic Scenegraph Nodes"
    overlay = bpy.props.EnumProperty(
        items=_enum_add_scene_types,
        description="Choose how to add the scene",
        default="1",
        update=update_tree_code)

    def init(self, context):
        NLActionNode.init(self, context)
        tools.register_inputs(
            self,
            NLConditionSocket, "Condition",
            NLQuotedStringFieldSocket, "Name"
        )

    def get_netlogic_class_name(self): return "bgelogic.ActionAddScene"
    def get_input_sockets_field_names(self): return ["condition", "scene_name"]
    def get_nonsocket_fields(self): return [("overlay", lambda : self.overlay)]
    def draw_buttons(self, context, layout):
        layout.prop(self, "overlay", text="")
_nodes.append(NLActionAddScene)


class NLActionInstallSubNetwork(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionInstallSubNetwork"
    bl_label = "Install Sub Tree"
    nl_category = "Basic Logic Tree Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Target Object")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Tree Name")
        self.inputs.new(NLBooleanSocket.bl_idname, "Enabled")
        self.inputs[-1].use_toggle = True
    def get_netlogic_class_name(self):
        return "bgelogic.ActionInstalSubNetwork"
    def get_input_sockets_field_names(self):
        return ["condition", "target_object", "tree_name", "initial_status"]
_nodes.append(NLActionInstallSubNetwork)


class NLActionStopAnimation(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionStopAnimation"
    bl_label = "Stop Animation"
    nl_category = "Basic Animation Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.inputs.new(NLPositiveIntegerFieldSocket.bl_idname, "Animation Layer")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionStopAnimation"
    def get_input_sockets_field_names(self):
        return ["condition", "game_object", "action_layer"]
_nodes.append(NLActionStopAnimation)


class NLActionSetAnimationFrame(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSetAnimationFrame"
    bl_label = "Set Animation Frame"
    nl_category = "Basic Animation Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Action Name")
        self.inputs.new(NLPositiveIntegerFieldSocket.bl_idname, "Animation Layer")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Animation Frame")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionSetAnimationFrame"
    def get_input_sockets_field_names(self):
        return ["condition", "game_object", "action_name", "action_layer", "action_frame"]
_nodes.append(NLActionSetAnimationFrame)


class NLActionApplyValue(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionApplyValue"
    bl_label = "Apply Motion/Rotation/Force/Torque to GameObject"
    nl_category = "Basic Cinematic Nodes"
    local = bpy.props.BoolProperty(default=True, update=update_tree_code)

    def init(self, context):
        NLActionNode.init(self, context)
        tools.register_inputs(
            self,
            NLConditionSocket, "Condition",
            NLGameObjectSocket, "GameObject",
            NLValueFieldSocket, "XYZ Movement",
            NLValueFieldSocket, "XYZ Rot",
            NLValueFieldSocket, "XYZ Force",
            NLValueFieldSocket, "XYZ Torque")

    def draw_buttons(self, context, layout):
        layout.prop(self, "local", toggle=True, text="Apply Local" if self.local else "Apply Global")

    def get_netlogic_class_name(self): return "bgelogic.ActionApplyGameObjectValue"
    def get_input_sockets_field_names(self): return ["condition", "game_object", "movement", "rotation", "force", "torque"]
    def get_nonsocket_fields(self): return [("local", lambda : "True" if self.local else "False")]
_nodes.append(NLActionApplyValue)


class NLActionEndObjectNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionEndObjectNode"
    bl_label = "Remove Object"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "GameObject")
    def get_netlogic_class_name(self): return "bgelogic.ActionEndObject"
    def get_input_sockets_field_names(self): return ["condition", "game_object"]
_nodes.append(NLActionEndObjectNode)


class NLActionEndSceneNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionEndSceneNode"
    bl_label = "Remove Scene"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLSceneSocket.bl_idname, "Scene")
    def get_netlogic_class_name(self): return "bgelogic.ActionEndScene"
    def get_input_sockets_field_names(self): return ["condition", "scene"]
_nodes.append(NLActionEndSceneNode)


class NLActionReplaceMesh(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionReplaceMesh"
    bl_label = "Replace Mesh"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Target Game Object")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "New Mesh Name")
        self.inputs.new(NLBooleanSocket.bl_idname, "Use Display")
        self.inputs.new(NLBooleanSocket.bl_idname, "Use Physics")

    def get_netlogic_class_name(self):
        return "bgelogic.ActionReplaceMesh"
    def get_input_sockets_field_names(self):
        return ["condition", "target_game_object", "new_mesh_name", "use_display", "use_physics"]
_nodes.append(NLActionReplaceMesh)


class NLActionPlayActionNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionPlayActionNode"
    bl_label = "Play GameoObject Action"
    nl_category = "Basic Animation Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        tools.register_inputs(#TODO change into self.inputs.new...
            self,
            NLConditionSocket, "Condition",
            NLGameObjectSocket, "Armature",
            NLQuotedStringFieldSocket, "Action Name",
            NLFloatFieldSocket, "Start Frame",
            NLFloatFieldSocket, "End Frame",
            NLPositiveIntegerFieldSocket, "Layer",
            NLPositiveIntegerFieldSocket, "Priority",
            NLPlayActionModeSocket, "Play Mode",
            NLFloatFieldSocket, "Layer Weight",
            NLFloatFieldSocket, "Speed",
            NLFloatFieldSocket, "Blendin",
            NLBlendActionModeSocket, "Blend Mode"
        )
        self.inputs[9].value = 1.0
        self.outputs.new(NLConditionSocket.bl_idname, "Started")
        self.outputs.new(NLConditionSocket.bl_idname, "Running")
        self.outputs.new(NLConditionSocket.bl_idname, "Finished")
        self.outputs.new(NLParameterSocket.bl_idname, "Current Frame")

    def get_netlogic_class_name(self):
        return "bgelogic.ActionPlayAction"
    def get_input_sockets_field_names(self): return [
        "condition", "game_object", "action_name", "start_frame", "end_frame", "layer",
        "priority", "play_mode", "layer_weight", "speed", "blendin", "blend_mode"]
    def get_output_socket_varnames(self):
        return ["STARTED", "RUNNING", "FINISHED", "FRAME"]
_nodes.append(NLActionPlayActionNode)


class NLActionLibLoadNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionLibLoadNode"
    bl_label = "Load Blender File"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Path")
        self.outputs.new(NLConditionSocket.bl_idname, "When Loaded")
    def get_netlogic_class_name(self): return "bgelogic.ActionLibLoad"
    def get_input_sockets_field_names(self): return ["condition", "path"]
_nodes.append(NLActionLibLoadNode)


class NLActionLibFreeNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionLibFreeNode"
    bl_label = "Unload Blender File"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Path")
        self.outputs.new(NLConditionSocket.bl_idname, "When Unloaded")
    def get_netlogic_class_name(self): return "bgelogic.ActionLibFree"
    def get_input_sockets_field_names(self): return ["condition", "path"]
_nodes.append(NLActionLibFreeNode)


class NLActionAlignAxisToVector(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionAlignAxisToVector"
    bl_label = "Align Axis to Vector"
    nl_category = "Basic Cinematic Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.inputs.new(NLSocketVectorField.bl_idname, "Vector")
        self.inputs.new(NLSocketLocalAxis.bl_idname, "Axis")
        self.inputs.new(NLSocketAlphaFloat.bl_idname, "Factor")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionAlignAxisToVector"
    def get_input_sockets_field_names(self):
        return ["condition", "game_object", "vector", "axis", "factor"]
_nodes.append(NLActionAlignAxisToVector)


#If the condition stays true for N seconds, do something, then wait N seconds to repeat
class NLActionTimeBarrier(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionTimeBarrier"
    bl_label = "Time Barrier"
    nl_category = "Basic Time Nodes"
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Delay Sec.")
        self.inputs.new(NLBooleanSocket.bl_idname, "Repeat")
        self.inputs[-1].use_toggle = True
        self.inputs[-1].true_label = "Repeat"
        self.inputs[-1].false_label = "Do not repeat"
        self.inputs[-1].value = True
        self.outputs.new(NLConditionSocket.bl_idname, "Out")
    def get_netlogic_class_name(self): return "bgelogic.ActionTimeBarrier"
    def get_input_sockets_field_names(self): return ["condition", "delay", "repeat"]
_nodes.append(NLActionTimeBarrier)


#When the condition is True, set to True then do the next check only after N seconds have elapsed
class NLActionTimeFilter(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionTimeFilter"
    bl_label = "Time Filter"
    nl_category = "Basic Time Nodes"
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Delay Sec.")
        self.inputs[-1].value = 1.0
        self.outputs.new(NLConditionSocket.bl_idname, "Out")
    def get_netlogic_class_name(self): return "bgelogic.ActionTimeFilter"
    def get_input_sockets_field_names(self): return ["condition", "delay"]
_nodes.append(NLActionTimeFilter)


class NLActionMousePickNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionMousePickNode"
    bl_label = "Mouse Pick"
    nl_category = "Basic Mouse Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Camera")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Property")
        self.inputs.new(NLFloatFieldSocket.bl_idname, "Distance")
        self.inputs[-1].value = 100.0
        self.outputs.new(NLConditionSocket.bl_idname, "Has Result")
        self.outputs.new(NLGameObjectSocket.bl_idname, "Picked Object")
        self.outputs.new(NLParameterSocket.bl_idname, "Picked Point")
        self.outputs.new(NLParameterSocket.bl_idname, "Picked Normal")
    def get_netlogic_class_name(self): return "bgelogic.ActionMousePick"
    def get_input_sockets_field_names(self): return ["condition", "camera", "property", "distance"]
    def get_output_socket_varnames(self): return [OUTCELL, "OUTOBJECT", "OUTPOINT", "OUTNORMAL"]
_nodes.append(NLActionMousePickNode)


class NLActionCameraPickNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionCameraPickNode"
    bl_label = "Camera Pick"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Camera")
        self.inputs.new(NLSocketVectorField.bl_idname, "Aim")
        self.inputs[-1].value = "0.5 0.5"
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Property")
        self.inputs.new(NLFloatFieldSocket.bl_idname, "Distance")
        self.inputs[-1].value = 100.0
        self.outputs.new(NLConditionSocket.bl_idname, "Has Result")
        self.outputs.new(NLGameObjectSocket.bl_idname, "Picked Object")
        self.outputs.new(NLParameterSocket.bl_idname, "Picked Point")
        self.outputs.new(NLParameterSocket.bl_idname, "Picked Normal")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionCameraPick"
    def get_input_sockets_field_names(self):
        return ["condition", "camera", "aim", "property_name", "distance"]
    def get_output_socket_varnames(self):
        return [OUTCELL, "PICKED_OBJECT", "PICKED_POINT", "PICKED_NORMAL"]
_nodes.append(NLActionCameraPickNode)


class NLActionSetParentNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSetParentNode"
    bl_label = "Set Game Object Parent"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Child Game Object")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Parent Game Object")
        self.inputs.new(NLBooleanSocket.bl_idname, "Compound")
        self.inputs[-1].value = True
        self.inputs.new(NLBooleanSocket.bl_idname, "Ghost")
        self.inputs[-1].value = True

    def get_netlogic_class_name(self):
        return "bgelogic.ActionSetParent"
    def get_input_sockets_field_names(self):
        return ["condition", "child_object", "parent_object", "compound", "ghost"]
_nodes.append(NLActionSetParentNode)


class NLActionRemoveParentNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionRemoveParentNode"
    bl_label = "Detach Game Object from Parent"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Child Game Object")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionRemoveParent"
    def get_input_sockets_field_names(self):
        return ["condition", "child_object"]
_nodes.append(NLActionRemoveParentNode)


class NLParameterGameObjectParent(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterGameObjectParent"
    bl_label = "Game Object's Parent"
    nl_category = "Basic Scenegraph Nodes"
    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLGameObjectSocket.bl_idname, "Child Game Object")
        self.outputs.new(NLGameObjectSocket.bl_idname, "Parent Game Object")
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterParentGameObject"
    def get_input_sockets_field_names(self):
        return ["game_object"]
_nodes.append(NLParameterGameObjectParent)


class NLActionSwapParent(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSwapParent"
    bl_label = "Swap Parent"
    nl_category = "Basic Scenegraph Nodes"
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Child Game Object")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "New Parent Name")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionSwapParent"
    def get_input_sockets_field_names(self):
        return ["condition", "child_object", "parent_name"]
_nodes.append(NLActionSwapParent)


class NLActionEditArmatureConstraint(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionEditArmatureConstraint"
    bl_label = "Edit Armature Constraint"
    nl_category = "Basic Armature Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Armature")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Constraint Name")
        self.inputs.new(NLAlphaSocket.bl_idname, "Enforced Factor")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Primary Target")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Secondary Target")
        self.inputs.new(NLBooleanSocket.bl_idname, "Active")
        self.inputs.new(NLAlphaSocket.bl_idname, "IK Weight")
        self.inputs.new(NLAlphaSocket.bl_idname, "IK Distance")
        self.inputs.new(NLSocketIKMode.bl_idname, "Distance Mode")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionEditArmatureConstraint"
    def get_input_sockets_field_names(self):
        return ["condition", "armature", "constraint_name", "enforced_factor", "primary_target",
                "secondary_target", "active", "ik_weight", "ik_distance", "distance_mode"]
_nodes.append(NLActionEditArmatureConstraint)


class NLActionEditBoneNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionEditBoneNode"
    bl_label = "Edit Armature Bone"
    nl_category = "Basic Armature Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Armature")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Bone Name")
        self.inputs.new(NLOptionalSocketVectorField.bl_idname, "Set XYZ Pos")
        self.inputs.new(NLOptionalSocketVectorField.bl_idname, "Set XYZ Rot")
        self.inputs.new(NLOptionalSocketVectorField.bl_idname, "Set XYZ Scale")
        self.inputs.new(NLOptionalSocketVectorField.bl_idname, "Trans XYZ")
        self.inputs.new(NLOptionalSocketVectorField.bl_idname, "Rot XYZ")
        self.inputs.new(NLOptionalSocketVectorField.bl_idname, "Scale XYZ")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionEditBone"
    def get_input_sockets_field_names(self):
        return ["condition", "armature", "bone_name", "set_translation",
                "set_orientation", "set_scale", "translate", "rotate", "scale"]
_nodes.append(NLActionEditBoneNode)


class NLActionSetDynamicsNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSetDynamicsNode"
    bl_label = "Set Game Object Dynamics"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.inputs.new(NLBooleanSocket.bl_idname, "Ghost")
        self.inputs[-1].value = False
        self.inputs.new(NLBooleanSocket.bl_idname, "Activate")
        s = self.inputs[-1]
        s.true_label = "Activate"
        s.false_label = "Suspend"

    def get_netlogic_class_name(self):
        return "bgelogic.ActionSetDynamics"
    def get_input_sockets_field_names(self):
        return ["condition", "game_object", "ghost", "activate"]
_nodes.append(NLActionSetDynamicsNode)


class NLActionFindSceneNode(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionFindSceneNode"
    bl_label = "Find Scene"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Optional Condition")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Query")
        self.outputs.new(NLSceneSocket.bl_idname, "Scene")

    def get_netlogic_class_name(self): return "bgelogic.ActionFindScene"
    def get_input_sockets_field_names(self): return ["condition", "query"]
_nodes.append(NLActionFindSceneNode)


class NLActionSetMousePosition(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSetMousePosition"
    bl_label = "Set Mouse Position"
    nl_category = "Basic Mouse Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLFloatFieldSocket.bl_idname, "Screen X")
        self.inputs[-1].value = 0.5
        self.inputs.new(NLFloatFieldSocket.bl_idname, "Screen Y")
        self.inputs[-1].value = 0.5
    def get_netlogic_class_name(self):
        return "bgelogic.ActionSetMousePosition"
    def get_input_sockets_field_names(self):
        return ["condition", "screen_x", "screen_y"]
_nodes.append(NLActionSetMousePosition)


class NLActionSetMouseCursorVisibility(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSetMouseCursorVisibility"
    bl_label = "Set Mouse Cursor Visibility"
    nl_category = "Basic Mouse Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLBooleanSocket.bl_idname, "Visible")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionSetMouseCursorVisibility"
    def get_input_sockets_field_names(self):
        return ["condition", "visibility_status"]
_nodes.append(NLActionSetMouseCursorVisibility)


class NLActionDynamicCharacterController(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionDynamicCharacterController"
    bl_label = "Dynamic Object Controller"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Head Object")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Body Object")
        self.inputs.new(NLSocketMouseMotion.bl_idname, "Rot Head Up")
        self.inputs[-1].value = "UP"
        self.inputs.new(NLSocketMouseMotion.bl_idname, "Rot Head Down")
        self.inputs[-1].value = "DOWN"
        self.inputs.new(NLSocketMouseMotion.bl_idname, "Rot Body Left")
        self.inputs[-1].value = "LEFT"
        self.inputs.new(NLSocketMouseMotion.bl_idname, "Rot Body Right")
        self.inputs[-1].value = "RIGHT"
        self.inputs.new(NLSocketKeyboardKeyPressed.bl_idname, "Strafe Left")
        self.inputs[-1].value = "A"
        self.inputs.new(NLSocketKeyboardKeyPressed.bl_idname, "Strafe Right")
        self.inputs[-1].value = "D"
        self.inputs.new(NLSocketKeyboardKeyPressed.bl_idname, "Move Forth")
        self.inputs[-1].value = "W"
        self.inputs.new(NLSocketKeyboardKeyPressed.bl_idname, "Move Back")
        self.inputs[-1].value = "S"
        self.inputs.new(NLSocketKeyboardKeyPressed.bl_idname, "Jump")
        self.inputs[-1].value = "SPACE"
        self.inputs.new(NLSocketKeyboardKeyPressed.bl_idname, "Run")
        self.inputs[-1].value = "LEFT_SHIFT"
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Head Rot Arc Size")
        self.inputs[-1].value = 0.785
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Head Rot Speed")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Body Rot Speed")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Walk speed")
        self.inputs[-1].value = 2.0
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Run speed")
        self.inputs[-1].value = 5.0
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Jump Force")
        self.inputs[-1].value = 300.0

    def get_netlogic_class_name(self):
        return "bgelogic.ActionDynamicObjectController"
    def get_input_sockets_field_names(self):
        return [
            "condition", "head_object", "body_object", "rotate_head_up", "rotate_head_down",
            "rotate_body_left", "rotate_body_right", "strafe_left", "strafe_right",
            "move_forth", "move_back",
            "jump", "run", "head_rot_arc_size", "head_rot_speed", "body_rot_speed", "walk_speed",
            "run_speed", "jump_force"
        ]
_nodes.append(NLActionDynamicCharacterController)


class NLActionStartSound(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionStartSound"
    bl_label = "Start Sound"
    nl_category = "Basic Sound Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLSocketSound.bl_idname, "Sound")
        self.inputs.new(NLSocketLoopCount.bl_idname, "Loop Count")
        self.inputs.new(NLSocketVectorField.bl_idname, "XYZ Pos")
        self.inputs.new(NLSocketOptionalOrientation.bl_idname, "Orientation")
        self.inputs.new(NLSocketVectorField.bl_idname, "XYZ Vel")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Pitch")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Volume")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Attenuation")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Distance Ref")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Distance Max")
        self.inputs[-1].value = 1000.0
    def get_netlogic_class_name(self):
        return "bgelogic.ActionStartSound"
    def get_input_sockets_field_names(self):
        return ["condition", "sound", "loop_count", "location", "orientation",
                "velocity", "pitch", "volume", "attenuation", "distance_ref", "distance_max"]
_nodes.append(NLActionStartSound)


class NLActionStopSound(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionStopSound"
    bl_label = "Stop Sound"
    nl_category = "Basic Sound Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLSocketSound.bl_idname, "Sound")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionStopSound"
    def get_input_sockets_field_names(self):
        return ["condition", "sound"]
_nodes.append(NLActionStopSound)


class NLActionPauseSound(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionPauseSound"
    bl_label = "Pause Sound"
    nl_category = "Basic Sound Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLSocketSound.bl_idname, "Sound")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionPauseSound"
    def get_input_sockets_field_names(self):
        return ["condition", "sound"]
_nodes.append(NLActionPauseSound)


class NLActionUpdateSound(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionUpdateSound"
    bl_label = "Update Sound"
    nl_category = "Basic Sound Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLSocketSound.bl_idname, "Sound")
        self.inputs.new(NLSocketVectorField.bl_idname, "XYZ Pos")
        self.inputs.new(NLSocketOptionalOrientation.bl_idname, "Orientation")
        self.inputs.new(NLSocketVectorField.bl_idname, "XYZ Vel")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Pitch")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Volume")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Attenuation")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Distance Ref")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Distance Max")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionUpdateSound"
    def get_input_sockets_field_names(self):
        return ["condition", "sound", "location", "orientation",
                "velocity", "pitch", "volume", "attenuation",
                "distance_ref", "distance_max"]
_nodes.append(NLActionUpdateSound)


class NLActionEndGame(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionEndGame"
    bl_label = "End Game"
    nl_category = "Game"
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionEndGame"
    def get_input_sockets_field_names(self):
        return ["condition"]
_nodes.append(NLActionEndGame)


class NLActionRestartGame(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionRestartGame"
    bl_label = "Restart Game"
    nl_category = "Game"
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
    def get_netlogic_class_name(self): return "bgelogic.ActionRestartGame"
    def get_input_sockets_field_names(self): return ["condition"]
_nodes.append(NLActionRestartGame)


class NLActionStartGame(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionStartGame"
    bl_label = "Start Game"
    nl_category = "Game"
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "File name")
    def get_netlogic_class_name(self): return "bgelogic.ActionStartGame"
    def get_input_sockets_field_names(self): return ["condition", "file_name"]
_nodes.append(NLActionStartGame)


class NLParameterGetGlobalValue(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterGetGlobalValue"
    bl_label = "Get Global Value"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "ID")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Key")
        self.inputs.new(NLValueFieldSocket.bl_idname, "Default")
        self.outputs.new(NLParameterSocket.bl_idname, "Value")
    def get_input_sockets_field_names(self):
        return ["data_id", "key", "default_value"]
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterGetGlobalValue"
_nodes.append(NLParameterGetGlobalValue)


class NLActionSetGlobalValue(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSetGlobalValue"
    bl_label = "Set Global Value"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Optional Condition")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "ID")
        self.inputs.new(NLBooleanSocket.bl_idname, "Persistent")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Key")
        self.inputs.new(NLValueFieldSocket.bl_idname, "Value")
    def get_input_sockets_field_names(self):
        return ["condition", "data_id", "persistent", "key", "value"]
    def get_netlogic_class_name(self):
        return "bgelogic.ActionSetGlobalValue"
_nodes.append(NLActionSetGlobalValue)


class NLParameterFormattedString(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterFormattedString"
    bl_label = "Formatted String"

    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Format String")
        self.inputs[-1].value = "A:{} B:{} C:{} D:{}"
        self.inputs.new(NLValueFieldSocket.bl_idname, "A")
        self.inputs.new(NLValueFieldSocket.bl_idname, "B")
        self.inputs.new(NLValueFieldSocket.bl_idname, "C")
        self.inputs.new(NLValueFieldSocket.bl_idname, "D")
        self.outputs.new(NLParameterSocket.bl_idname, "String")
    def get_input_sockets_field_names(self):
        return ["format_string", "value_a", "value_b", "value_c", "value_d"]
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterFormattedString"
_nodes.append(NLParameterFormattedString)


class NLActionRandomValues(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionRandomValues"
    bl_label = "Random Values"
    nl_category = "Basic Math Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLNumericFieldSocket.bl_idname, "Min")
        self.inputs.new(NLNumericFieldSocket.bl_idname, "Max")
        self.outputs.new(NLParameterSocket.bl_idname, "Random A")
        self.outputs.new(NLParameterSocket.bl_idname, "Random B")
        self.outputs.new(NLParameterSocket.bl_idname, "Random C")
        self.outputs.new(NLParameterSocket.bl_idname, "Random D")
    def get_input_sockets_field_names(self):
        return ["condition", "min_value", "max_value"]
    def get_netlogic_class_name(self):
        return "bgelogic.ActionRandomValues"
    def get_output_socket_varnames(self):
        return ["OUT_A", "OUT_B", "OUT_C", "OUT_D"]
_nodes.append(NLActionRandomValues)


class NLParameterDistance(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterDistance"
    bl_label = "Distance (Vec, XYZ, GameObject)"
    nl_category = "Basic Math Nodes"
    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLSocketVectorField.bl_idname, "A")
        self.inputs.new(NLSocketVectorField.bl_idname, "B")
        self.outputs.new(NLParameterSocket.bl_idname, "Dst")
    def get_input_sockets_field_names(self):
        return ["parama", "paramb"]
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterDistance"
_nodes.append(NLParameterDistance)


class NLParameterKeyboardKeyCode(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterKeyboardKeyCode"
    bl_label = "Keyboard Key Code"
    nl_category = "Basic Keyboard Nodes"
    value = bpy.props.StringProperty(update=update_tree_code)
    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLKeyboardKeySocket.bl_idname, "")
        self.outputs.new(NLParameterSocket.bl_idname, "Code")
    def get_input_sockets_field_names(self): 
        return ["key_code"]
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterKeyboardKeyCode"
_nodes.append(NLParameterKeyboardKeyCode)


class NLActionMoveTo(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionMoveTo"
    bl_label = "Move To"
    nl_category = "Basic Cinematic Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Moving Object")
        self.inputs.new(NLBooleanSocket.bl_idname, "Move as Dynamic")
        self.inputs.new(NLSocketVectorField.bl_idname, "Destination XYZ")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Speed")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLFloatFieldSocket.bl_idname, "Stop At Distance")
        self.inputs[-1].value = 0.5
        self.outputs.new(NLConditionSocket.bl_idname, "When Done")
    def get_input_sockets_field_names(self):
        return ["condition", "moving_object", "dynamic", "destination_point", "speed", "distance"]
    def get_netlogic_class_name(self):
        return "bgelogic.ActionMoveTo"
_nodes.append(NLActionMoveTo)


class NLActionTranslate(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionTranslate"
    bl_label = "Translate"
    nl_category = "Basic Cinematic Nodes"
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Moving Object")
        self.inputs.new(NLFloatFieldSocket.bl_idname, "DX")
        self.inputs.new(NLFloatFieldSocket.bl_idname, "DY")
        self.inputs.new(NLFloatFieldSocket.bl_idname, "DZ")
        self.inputs.new(NLBooleanSocket.bl_idname, "Local")
        self.inputs[-1].value = True
        self.inputs.new(NLFloatFieldSocket.bl_idname, "Speed")
        self.inputs[-1].value = 1.0
        self.outputs.new(NLConditionSocket.bl_idname, "When Done")
    def get_input_sockets_field_names(self):
        return ["condition", "moving_object", "dx", "dy", "dz", "local", "speed"]
    def get_netlogic_class_name(self):
        return "bgelogic.ActionTranslate"
_nodes.append(NLActionTranslate)


class NLActionRotateTo(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionRotateTo"
    bl_label = "Rotate To"
    nl_category = "Basic Cinematic Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Moving Object")
        self.inputs.new(NLSocketVectorField.bl_idname, "Target XYZ")
        self.inputs.new(NLSocketLocalAxis.bl_idname, "Rot Axis")
        self.inputs.new(NLSocketOrientedLocalAxis.bl_idname, "Front")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Speed")
        self.outputs.new(NLConditionSocket.bl_idname, "When Done")

    def get_input_sockets_field_names(self):
        return ["condition", "moving_object", "target_point", "rot_axis", "front_axis", "speed"]

    def get_netlogic_class_name(self):
        return "bgelogic.ActionRotateTo"
_nodes.append(NLActionRotateTo)


class NLActionNavigate(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionNavigate"
    bl_label = "Move To with Navmesh"
    nl_category = "Basic Cinematic Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Moving Object")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Rotating Object")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Navmesh Object")
        self.inputs.new(NLSocketVectorField.bl_idname, "Destination XYZ")
        self.inputs.new(NLBooleanSocket.bl_idname, "Move as Dynamic")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Lin Speed")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Reach Threshold")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLBooleanSocket.bl_idname, "Look At")
        self.inputs[-1].value = True
        self.inputs.new(NLSocketLocalAxis.bl_idname, "Rot Axis")
        self.inputs.new(NLSocketOrientedLocalAxis.bl_idname, "Front")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Rot Speed")
        self.outputs.new(NLConditionSocket.bl_idname, "When Reached")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionNavigateWithNavmesh"
    def get_input_sockets_field_names(self):
        return ["condition", "moving_object", "rotating_object", "navmesh_object",
                "destination_point", "move_dynamic", "linear_speed",
                "reach_threshold", "look_at", "rot_axis","front_axis", "rot_speed"]
_nodes.append(NLActionNavigate)


class NLActionFollowPath(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionFollowPath"
    bl_label = "Follow Path"
    nl_category = "Basic Cinematic Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Moving Object")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Rotating Object")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Path (~Parent of a set of Empties)")
        self.inputs.new(NLBooleanSocket.bl_idname, "Loop")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Optional Navmesh Object")
        self.inputs.new(NLBooleanSocket.bl_idname, "Move as Dynamic")
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Lin Speed")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLPositiveFloatSocket.bl_idname, "Reach Threshold")
        self.inputs[-1].value = 1.0
        self.inputs.new(NLBooleanSocket.bl_idname, "Look At")
        self.inputs[-1].value = True
        self.inputs.new(NLSocketLocalAxis.bl_idname, "Rot Axis")
        self.inputs.new(NLSocketOrientedLocalAxis.bl_idname, "Front")
        self.inputs.new(NLSocketOptionalPositiveFloat.bl_idname, "Rot Speed")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionFollowPath"
    def get_input_sockets_field_names(self):
        return ["condition", "moving_object", "rotating_object", "path_parent", "loop",
                "navmesh_object", "move_dynamic", "linear_speed",
                "reach_threshold", "look_at", "rot_axis","front_axis", "rot_speed"]
_nodes.append(NLActionFollowPath)


class NLActionUpdateBitmapFontQuads(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionUpdateBitmapFontQuads"
    bl_label = "Update Bitmap Font Quads"
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLGameObjectSocket.bl_idname, "Game Object")
        self.inputs.new(NLPositiveIntegerFieldSocket.bl_idname, "Font Grid Size")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "String Expr")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionUpdateBitmapFontQuads"
    def get_input_sockets_field_names(self):
        return ["condition", "game_object", "grid_size", "text"]
_nodes.append(NLActionUpdateBitmapFontQuads)


class NLActionSetCurrentScene(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionSetCurrentScene"
    bl_label = "Change Current Scene"
    nl_category = "Basic Scenegraph Nodes"

    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "Scene Name")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionSetCurrentScene"
    def get_input_sockets_field_names(self):
        return ["condition", "scene_name"]
_nodes.append(NLActionSetCurrentScene)


class NLActionStringOp(bpy.types.Node, NLActionNode):
    bl_idname = "NLActionStringOp"
    bl_label = "String Op"
    nl_category = "Basic String Nodes"
    value = bpy.props.EnumProperty(items=_enum_string_ops, update=update_tree_code)
    def init(self, context):
        NLActionNode.init(self, context)
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        self.inputs.new(NLParameterSocket.bl_idname, "Input String")
        self.inputs.new(NLParameterSocket.bl_idname, "Parameter A")
        self.inputs.new(NLParameterSocket.bl_idname, "Parameter B")
        self.outputs.new(NLParameterSocket.bl_idname, "Output String")
    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="Op")
    def get_netlogic_class_name(self):
        return "bgelogic.ActionStringOp"
    def get_input_sockets_field_names(self):
        return ["condition", "input_string", "input_param_a", "input_param_b"]
    def get_nonsocket_fields(self):
        return [("opcode", self.value)]
_nodes.append(NLActionStringOp)


_enum_predefined_math_fun = {
    ("User Defined", "User Defined", "A formula defined by the user"),
    ("exp(a)", "exp(e)", "e to the power a"),
    ("pow(a,b)", "pow(a,b)", "a to the power b"),
    ("log(a)", "log(a)", "natural log of a"),
    ("log10(a)", "log10(a)", "base 10 log of a"),
    ("acos(a)", "acos(a)", "arc cosine of a, radians"),
    ("asin(a)", "asin(a)", "arc sine of a, radians"),
    ("atan(a)", "atan(a)", "arc tangent of a, radians"),
    ("atan2(a,b)", "atan2(a,b)", "atan(a / b), radians"),
    ("cos(a)", "cos(a)", "cosine of a, radians"),
    ("hypot(a,b)", "hypot(a,b)", "sqrt(a*a + b*b)"),
    ("sin(a)", "sin(a)", "sine of a, radians"),
    ("tan(a)", "tan(a)", "tangent of a, radians"),
    ("degrees(a)", "degrees(a)", "convert a from radians to degrees"),
    ("radians(a)", "radians(a)", "convert a from degrees to radians"),
    ("acosh(a)", "acosh(a)", "inverse hyperbolic cosine of a"),
    ("asinh(a)", "asinh(a)", "inverse hyperbolic cosing of a"),
    ("atanh(a)", "atanh(a)", "inverse hyperbolic tangent of a"),
    ("cosh(a)", "cosh(a)", "hyperbolic cosine of a"),
    ("sinh(a)", "sinh(a)", "hyperbolic sine of a"),
    ("tanh(a)", "tanh(a)", "hyperbolic tangent of a"),
    ("pi", "pi", "the PI constant"),
    ("e", "e", "the e constant"),
    ("ceil(a)", "ceil(a)", "smallest integer value = or > to a"),
    ("sign(a)", "sign(a)", "0 if a is 0, -1 if a < 0, 1 if a > 0"),
    ("abs(a)", "abs(a)", "absolute value of a"),
    ("floor(a)", "floor(a)", "largest integer value < or = to a"),
    ("mod(a,b)", "mod(a,b)", "a modulo b"),
    ("sqrt(a)", "sqrt(a)", "square root of a"),
    ("curt(a)", "curt(a)", "cubic root of a"),
    ("str(a)", "str(a)", "a (non string value) converted to a string"),
    ("int(a)", "int(a)", "a (integer string) converted to an integer value"),
    ("float(a)", "float(a)", "a (float string) converted to a float value")
}
class NLParameterMathFun(bpy.types.Node, NLParameterNode):
    bl_idname = "NLParameterMathFun"
    bl_label = "Formulas (Math & Co.)"
    nl_category = "Basic Math Nodes"
    def on_fun_changed(self, context):
        if(self.predefined_formulas != "User Defined"):
            self.value = self.predefined_formulas
        update_tree_code(self, context)
    value = bpy.props.StringProperty(update=update_tree_code)
    predefined_formulas = bpy.props.EnumProperty(
        items=_enum_predefined_math_fun, 
        update=on_fun_changed,
        default="User Defined")
    def init(self, context):
        NLParameterNode.init(self, context)
        self.inputs.new(NLNumericFieldSocket.bl_idname, "a")
        self.inputs.new(NLNumericFieldSocket.bl_idname, "b")
        self.inputs.new(NLNumericFieldSocket.bl_idname, "c")
        self.inputs.new(NLNumericFieldSocket.bl_idname, "d")
        self.outputs.new(NLParameterSocket.bl_idname, "Result");
    def draw_buttons(self, context, layout):
        layout.prop(self, "predefined_formulas", "Predef.")
        layout.prop(self, "value", "Formula")
    def get_input_sockets_field_names(self):
        return ["a", "b", "c", "d"]
    def get_nonsocket_fields(self):
        return [("formula", '"{0}"'.format(self.value))]
    def get_netlogic_class_name(self):
        return "bgelogic.ParameterMathFun"
_nodes.append(NLParameterMathFun)