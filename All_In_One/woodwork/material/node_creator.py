from math import modf
from math import pi
from abc import ABCMeta, abstractmethod

import bpy
import mathutils
from mathutils import Vector

class Socket:
    def __init__(self, bpy_socket: bpy.types.NodeSocket):
        self.socket = bpy_socket

    def as_bpy_type(self) -> bpy.types.NodeSocket:
        return self.socket


class Nodes:
    def __init__(self, bpy_node_tree: bpy.types.NodeTree):
        self.node_tree = bpy_node_tree

    def link(self,
             input_socket: Socket,
             output_socket: Socket):

        self.node_tree.links.new(input_socket.as_bpy_type(),
                                 output_socket.as_bpy_type())

    def as_bpy_type(self) -> bpy.types.NodeTree:
        return self.node_tree


class Node:
    pass


class Position:
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_node_position(self, node: Node):
        pass


class Above(Position):
    pass


class Above(Position):
    def __init__(self, relative_node: Node):
        self.relative_node = relative_node
        self.distance = 0.0

    def with_distance(self, dist: float) -> Above:
        self.distance = dist
        return self

    def set_node_position(self, node: Node):
        rel_location = self.relative_node.compute_location()
        height = node.compute_height()
        node.set_location(Vector((rel_location.x, rel_location.y + self.distance + height)))


def above(relative_node: Node) -> Above:
    return Above(relative_node)


class Below(Position):
    pass


class Below(Position):
    def __init__(self, relative_node: Node):
        self.relative_node = relative_node
        self.distance = 0.0

    def with_distance(self, dist: float) -> Below:
        self.distance = dist
        return self

    def set_node_position(self, node: Node):
        location = self.relative_node.compute_location()
        computed_height = self.relative_node.compute_height()
        node.set_location(Vector((location.x, location.y - computed_height - self.distance)))


def below(relative_node: Node) -> Below:
    return Below(relative_node)


class OnTheRightSideOf(Position):
    pass


class OnTheRightSideOf(Position):
    def __init__(self, relative_node: Node):
        self.relative_node = relative_node
        self.distance = 0.0

    def with_distance(self, dist: float) -> OnTheRightSideOf:
        self.distance = dist
        return self

    def set_node_position(self, node: Node):
        ref_x, ref_y = self.relative_node.compute_location()
        computed_width = self.relative_node.compute_width()
        node.set_location(Vector((ref_x + computed_width + self.distance, ref_y)))


def on_the_right_side_of(relative_node: Node) -> OnTheRightSideOf:
    return OnTheRightSideOf(relative_node)


class Between(Position):
    pass


class Between(Position):
    def __init__(self, first_node: Node, second_node: Node):
        self.first_node = first_node
        self.second_node = second_node
        self.distance = 0.0
        self.side = 'right'

    def with_distance(self, dist: float) -> Between:
        self.distance = dist
        return self

    def on_the_right(self) -> Between:
        self.side = 'right'
        return self

    def on_the_left(self) -> Between:
        self.side = 'left'
        return self

    def above(self) -> Between:
        self.side = 'above'
        return self

    def below(self) -> Between:
        self.side = 'below'
        return self

    def __set_node_right_position(self, node: Node):
        ref_x1, ref_y1 = self.first_node.compute_location()
        ref_x2, ref_y2 = self.second_node.compute_location()
        width1 = self.first_node.compute_width()
        width2 = self.second_node.compute_width()
        height1 = self.first_node.compute_height()
        height2 = self.second_node.compute_height()

        right_co_1 = ref_x1 + width1
        right_co_2 = ref_x2 + width2
        if right_co_1 > right_co_2:
            x_location = right_co_1 + self.distance
        else:
            x_location = right_co_2 + self.distance

        y_top = ref_y1 - height1
        y_bottom = ref_y2
        if ref_y2 - height2 > y_top:
            y_top = ref_y2 - height2
            y_bottom = ref_y1
        middle_y = y_bottom + (y_top - y_bottom) / 2.0
        y_location = middle_y + (node.compute_height() / 2.0)

        node.set_location(Vector((x_location, y_location)))

    def __set_node_left_position(self, node: Node):
        ref_x1, ref_y1 = self.first_node.compute_location()
        ref_x2, ref_y2 = self.second_node.compute_location()
        height1 = self.first_node.compute_height()
        height2 = self.second_node.compute_height()

        if ref_x1 > ref_x2:
            x_location = ref_x2 - self.distance
        else:
            x_location = ref_x1 - self.distance

        y_top = ref_y1 - height1
        y_bottom = ref_y2
        if ref_y2 - height2 > y_top:
            y_top = ref_y2 - height2
            y_bottom = ref_y1
        middle_y = y_bottom + (y_top - y_bottom) / 2.0
        y_location = middle_y + (node.compute_height() / 2.0)

        node.set_location(Vector((x_location, y_location)))

    def __set_node_above_position(self, node: Node):
        ref_x1, ref_y1 = self.first_node.compute_location()
        ref_x2, ref_y2 = self.second_node.compute_location()
        width1 = self.first_node.compute_width()
        width2 = self.second_node.compute_width()

        if ref_y1 > ref_y2:
            y_location = ref_y2 - self.distance
        else:
            y_location = ref_y1 - self.distance

        x_start = ref_x1 + width1
        x_end = ref_x2
        if ref_x2 + width2 < x_start:
            x_start = ref_x2 + width2
            x_end = ref_x1
        middle_x = (x_end - x_start) / 2.0
        x_location = middle_x - (node.compute_width() / 2.0)

        node.set_location(Vector((x_location, y_location)))

    def __set_node_below_position(self, node: Node):
        ref_x1, ref_y1 = self.first_node.compute_location()
        ref_x2, ref_y2 = self.second_node.compute_location()
        width1 = self.first_node.compute_width()
        width2 = self.second_node.compute_width()
        height1 = self.first_node.compute_height()
        height2 = self.second_node.compute_height()

        bottom_co_1 = ref_y1 + height1
        bottom_co_2 = ref_y2 + height2
        if bottom_co_1 > bottom_co_2:
            y_location = bottom_co_1 + self.distance
        else:
            y_location = bottom_co_2 + self.distance

        x_start = ref_x1 + width1
        x_end = ref_x2
        if ref_x2 + width2 < x_start:
            x_start = ref_x2 + width2
            x_end = ref_x1
        middle_x = (x_end - x_start) / 2.0
        x_location = middle_x - (node.compute_width() / 2.0)

        node.set_location(Vector((x_location, y_location)))

    def set_node_position(self, node: Node):

        if self.side is 'right':
            self.__set_node_right_position(node)
        elif self.side is 'left':
            self.__set_node_left_position(node)
        elif self.side is 'above':
            self.__set_node_above_position(node)
        else:
            self.__set_node_below_position(node)

def between(first_node: Node, second_node: Node) -> Between:
    return Between(first_node, second_node)


class Location(Position):
    def __init__(self, location: Vector):
        self.location = location

    def set_node_position(self, node: Node):
        node.set_location(self.location)


def location(location: Vector) -> Location:
    return Location(location)


class Node:

    def __init__(self, bpy_node: bpy.types.Node):
        self.node = bpy_node

    @staticmethod
    def create(tree: Nodes,
               node_type: str) -> Node:
        node_type_to_class = {
            'NodeFrame': Frame,
            'NodeReroute': Reroute,
            'NodeGroupInput': GroupInput,
            'ShaderNodeGroup': GroupNode,
            'ShaderNodeTexCoord': TextureCoordinate,
            'ShaderNodeObjectInfo': ObjectInfo,
            'ShaderNodeMixRGB': MixRGB,
            'ShaderNodeTexNoise': NoiseTexture,
            'ShaderNodeTexGradient': GradientTexture,
            'ShaderNodeTexMusgrave': MusgraveTexture,
            'ShaderNodeTexVoronoi': VoronoiTexture,
            'ShaderNodeValToRGB': ColorRamp,
            'ShaderNodeRGBCurve': RGBCurve,
            'ShaderNodeMath': Math,
            'ShaderNodeSeparateRGB': SeparateRGB,
            'ShaderNodeSeparateXYZ': SeparateXYZ,
            'ShaderNodeCombineXYZ': CombineXYZ,
            'ShaderNodeValue': Value,
            'ShaderNodeBsdfDiffuse': BsdfDiffuse,
            'ShaderNodeBsdfGlossy': BsdfGlossy,
            'ShaderNodeMixShader': MixShader,
            'ShaderNodeFresnel': Fresnel,
            'ShaderNodeInvert': Invert,
            'ShaderNodeBump': Bump,
            'ShaderNodeOutputMaterial': OutputMaterial
        }
        nodes = tree.as_bpy_type().nodes
        bpy_node = nodes.new(node_type)
        class_type = node_type_to_class.get(node_type, Node)

        return class_type(bpy_node)

    def set_name(self, name: str) -> Node:
        self.node.name = name
        return self

    def set_label(self, label: str) -> Node:
        self.node.label = label
        return self

    def set_parent(self, parent: Node) -> Node:
        if type(parent) is Frame:
            parent.set_child(self)
        self.node.parent = parent.as_bpy_type()
        return self

    def get_parent(self) -> bpy.types.Node:
        return self.node.parent

    def set_location(self, location: Vector) -> Node:
        self.node.location = location
        return self

    def get_location(self) -> Vector:
        return self.node.location

    def get_width(self)-> float:
        return self.node.width

    def get_height(self)-> float:
        return self.node.height

    def as_bpy_type(self) -> bpy.types.Node:
        return self.node

    def hide(self) -> Node:
        self.node.hide = True
        return self

    def show(self) -> Node:
        self.node.hide = False
        return self

    def is_hidden(self) -> bool:
        return self.node.hide

    def get_input(self, key: str) -> Socket:
        return Socket(self.node.inputs[key])

    def get_input(self, index: int) -> Socket:
        return Socket(self.node.inputs[index])

    def get_output(self, key: str) -> Socket:
        return Socket(self.node.outputs[key])

    def get_output(self, index: int) -> Socket:
        return Socket(self.node.outputs[index])

    def __compute_hidden_radius(self) -> float:
        node_bpy = self.as_bpy_type()
        widget_unit = 20
        hidden_rad = 0.75 * widget_unit
        totout = totin = 0
        for output in node_bpy.outputs:
            if output.hide:
                continue
            totout += 1
        for input in node_bpy.inputs:
            if input.hide:
                continue
            totin += 1
        tot = max(totout, totin)
        if tot > 4:
            hidden_rad += 5.0 * (tot - 4.0)
        return hidden_rad

    def compute_location(self) -> Vector:
        node_bpy = self.as_bpy_type()
        node_loc = self.get_location()
        if node_bpy.hide:
            widget_unit = 20
            node_dy = widget_unit
            hidden_rad = self.__compute_hidden_radius()
            location = Vector((node_loc.x, node_loc.y - 0.5 * node_dy + hidden_rad))
        else:
            location = node_loc
        return location

    def compute_width(self) -> float:
        node_bpy = self.as_bpy_type()
        if node_bpy.hide:
            hidden_rad = self.__compute_hidden_radius()
            mini_width = 42.0
            width = 3 * hidden_rad + mini_width
        else:
            width = self.get_width()
        return width

    def compute_buttons_y_space(self) -> float:
        return 0.0

    # When widget is not drawn yet, dimensions are not available
    # Values taken from node_update_basis in node_draw.c
    def compute_height(self) -> float:
        widget_unit = 20
        node_dy = widget_unit
        node_dys = widget_unit // 2
        node_sockdy = 0.08 * widget_unit

        node_bpy = self.as_bpy_type()
        if node_bpy.hide:
            hidden_rad = self.__compute_hidden_radius()
            height = 2 * hidden_rad
        else:
            dy = node_bpy.location.y
            # header
            dy -= node_dy

            # little bit space in top
            if node_bpy.outputs:
                dy -= node_dys // 2
            # output sockets
            i = 0
            for output in node_bpy.outputs:
                if output.hide:
                    continue
                dy = int(dy - node_dy)
                dy -= node_sockdy
                i += 1
            dy += node_sockdy

            # "buttons" rect
            buttons_y_space = self.compute_buttons_y_space()
            if buttons_y_space > 0.0:
                dy -= node_dys // 2
                dy -= buttons_y_space
                dy -= node_dys // 2

            # input sockets
            for input in node_bpy.inputs:
                if input.hide:
                    continue
                dy = int(dy - node_dy)
                dy -= node_sockdy
            dy += node_sockdy

            # little bit space in end
            has_options_or_preview = node_bpy.show_preview or node_bpy.show_options
            if node_bpy.inputs or not has_options_or_preview:
                dy -= node_dys / 2
            height = node_bpy.location.y - dy
        return height

    def set_position(self, position: Position) -> Node:
        position.set_node_position(self)
        return self


class Group:
    pass


class Group(Nodes):

    @staticmethod
    def create(name: str) -> Group:
        group = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        return Group(group)

    def set_input(self, input_name: str, input_type: str, input_value) -> Group:
        new_input = self.node_tree.inputs.new(name=input_name, type=input_type)
        new_input.default_value = input_value
        return self

    def set_output(self, output_name: str, output_type: str, output_value) -> Group:
        new_output = self.node_tree.outputs.new(name=output_name, type=output_type)
        new_output.default_value = output_value
        return self

    def get_input(self, input_name: str) -> Socket:
        return Socket(self.node_tree.inputs[input_name])

    def get_output(self, output_name: str) -> Socket:
        return Socket(self.node_tree.outputs[output_name])

    def set_float_input(self, input_name: str, input_value: float) -> Group:
        return self.set_input(input_name, 'NodeSocketFloat', input_value)

    def set_vector_input(self, input_name: str, input_value: mathutils.Vector) -> Group:
        return self.set_input(input_name, 'NodeSocketVector', input_value)

    def set_color_input(self, input_name: str, input_value: list) -> Group:
        return self.set_input(input_name, 'NodeSocketColor', input_value)

    def set_vector_output(self, input_name: str, output_value: mathutils.Vector) -> Group:
        return self.set_output(input_name, 'NodeSocketVector', output_value)

    def set_color_output(self, input_name: str, output_value: list) -> Group:
        return self.set_output(input_name, 'NodeSocketColor', output_value)


class Frame(Node):
    pass


class Frame(Node):
    def __init__(self, bpy_node: bpy.types.Node):
        self.children = []
        Node.__init__(self, bpy_node)

    @staticmethod
    def create(tree: Nodes) -> Frame:
        return Node.create(tree, 'NodeFrame')

    def set_shrink(self, shrink: bool) -> Frame:
        self.node.shrink = shrink
        return self

    def set_child(self, child: Node):
        self.children.append(child)

    def __get_bounding_box(self):
        lowests = Vector((99999999999999999.0, 99999999999999999.0))
        highests = Vector((-99999999999999999.0, -99999999999999999.0))
        if len(self.children) > 0:
            for child in self.children:
                child_loc = child.compute_location()

                child_x = child_loc.x
                if child_x < lowests.x:
                    lowests.x = child_x

                child_y = child_loc.y
                if child_y > highests.y:
                    highests.y = child_y

                child_width = child.compute_width()
                child_xmax = child_loc.x + child_width
                if child_xmax > highests.x:
                    highests.x = child_xmax

                child_height = child.compute_height()
                child_ymax = child_loc.y - child_height
                if child_ymax < lowests.y:
                    lowests.y = child_ymax

            widget_unit = 20
            margin = 1.5 * widget_unit
            lowests.x -= margin
            lowests.y -= margin
            highests.x += margin
            highests.y += margin
        else:
            lowests = Vector((0.0, 0.0))
            highests = Vector(self.get_width(),
                              self.get_height())
        return lowests, highests

    def set_location(self, location: Vector) -> Frame:
        if len(self.children) > 0:
            min, max = self.__get_bounding_box()

            Node.set_location(self, Vector((location.x - min.x,
                                            location.y - max.y)))
        return self

    def compute_location(self) -> Vector:

        computed_location = frame_location = self.get_location()

        if len(self.children) > 0:
            min, max = self.__get_bounding_box()

            computed_location = Vector((frame_location.x + min.x,
                                        frame_location.y + max.y))

        return computed_location

    def compute_width(self) -> float:

        width = self.node.width

        if len(self.children) > 0:
            min, max = self.__get_bounding_box()
            width = max.x - min.x

        return width

    def compute_height(self) -> float:

        height = self.node.height

        if len(self.children) > 0:
            min, max = self.__get_bounding_box()
            height = max.y - min.y

        return height


class Reroute(Node):
    pass


class Reroute(Node):
    @staticmethod
    def create(tree: Nodes) -> Reroute:
        return Node.create(tree, 'NodeReroute')


class GroupNode(Node):
    pass


class GroupNode(Node):
    @staticmethod
    def create(tree: Nodes) -> GroupNode:
        return Node.create(tree, 'ShaderNodeGroup')

    def compute_buttons_y_space(self) -> float:
        widget_unit = 20

        # template_ID in interface_templates.c
        dy = widget_unit

        return dy

    def set_node_tree(self, nodes: Nodes) -> GroupNode:
        self.node.node_tree = nodes.as_bpy_type()
        return self

class GroupInput(Node):
    pass


class GroupInput(Node):
    @staticmethod
    def create(tree: Nodes) -> GroupInput:
        return Node.create(tree, 'NodeGroupInput')


class GroupOutput(Node):
    pass


class GroupOutput(Node):
    @staticmethod
    def create(tree: Nodes) -> GroupOutput:
        return Node.create(tree, 'NodeGroupOutput')


class TextureCoordinate(Node):
    pass


class ObjectInfo(Node):
    pass


class MixRGB(Node):
    pass


class MixRGB(Node):
    @staticmethod
    def create(tree: Nodes) -> MixRGB:
        return Node.create(tree, 'ShaderNodeMixRGB')

    def set_blend_type(self, blend_type: str) -> MixRGB:
        self.node.blend_type = blend_type
        return self

    def set_use_clamp(self, use_clamp: bool) -> MixRGB:
        self.node.use_clamp = use_clamp
        return self

    def set_mix_factor(self, mix_factor: float) -> MixRGB:
        self.node.inputs['Fac'].default_value = mix_factor
        return self

    def get_mix_factor_input(self) -> Socket:
        return self.get_input('Fac')

    def set_first_color(self, color: tuple) -> MixRGB:
        self.node.inputs['Color1'].default_value = color
        return self

    def get_first_color_input(self) -> Socket:
        return self.get_input('Color1')

    def set_second_color(self, color: tuple) -> MixRGB:
        self.node.inputs['Color2'].default_value = color
        return self

    def get_second_color_input(self) -> Socket:
        return self.get_input('Color2')

    def get_color_output(self) -> Socket:
        return self.get_output('Color')

    def compute_buttons_y_space(self) -> float:
        widget_unit = 20

        # mix op
        dy = widget_unit

        # use clamp
        dy += widget_unit

        return dy

class NoiseTexture(Node):
    pass


class NoiseTexture(Node):
    @staticmethod
    def create(tree: Nodes) -> NoiseTexture:
        return Node.create(tree, 'ShaderNodeTexNoise')

    def get_vector_input(self) -> Socket:
        return self.get_input('Vector')

    def set_scale(self, scale: float) -> NoiseTexture:
        self.node.inputs['Scale'].default_value = scale
        return self

    def get_scale_input(self) -> Socket:
        return self.get_input('Scale')

    def set_detail(self, detail: float) -> NoiseTexture:
        self.node.inputs['Detail'].default_value = detail
        return self

    def set_distortion(self, distortion: float) -> NoiseTexture:
        self.node.inputs['Distortion'].default_value = distortion
        return self

    def get_color_output(self) -> Socket:
        return self.get_output('Color')

    def get_mix_factor_output(self) -> Socket:
        return self.get_output('Fac')


class GradientTexture(Node):
    pass


class GradientTexture(Node):
    @staticmethod
    def create(tree: Nodes) -> GradientTexture:
        return Node.create(tree, 'ShaderNodeTexGradient')

    def set_type(self, gradient_type: str) -> GradientTexture:
        self.node.gradient_type = gradient_type
        return self

    def get_vector_input(self) -> Socket:
        return self.get_input('Vector')

    def get_color_output(self) -> Socket:
        return self.get_output('Color')

    def compute_buttons_y_space(self) -> float:
        widget_unit = 20

        # gradient type
        dy = widget_unit

        return dy

class MusgraveTexture(Node):
    pass

class MusgraveTexture(Node):
    @staticmethod
    def create(tree: Nodes) -> MusgraveTexture:
        return Node.create(tree, 'ShaderNodeTexMusgrave')

    def set_type(self, musgrave_type: str) -> MusgraveTexture:
        self.node.musgrave_type = musgrave_type
        return self

    def get_vector_input(self) -> Socket:
        return self.get_input('Vector')

    def get_color_output(self) -> Socket:
        return self.get_output('Color')

    def set_scale(self, scale: float) -> MusgraveTexture:
        self.node.inputs['Scale'].default_value = scale
        return self

    def get_scale_input(self) -> Socket:
        return self.get_input('Scale')

    def set_detail(self, detail: float) -> MusgraveTexture:
        self.node.inputs['Detail'].default_value = detail
        return self

    def set_dimension(self, dimension: float) -> MusgraveTexture:
        self.node.inputs['Dimension'].default_value = dimension
        return self

    def set_lacunarity(self, lacunarity: float) -> MusgraveTexture:
        self.node.inputs['Lacunarity'].default_value = lacunarity
        return self

    def set_offset(self, offset: float) -> MusgraveTexture:
        self.node.inputs['Offset'].default_value = offset
        return self

    def set_gain(self, gain: float) -> MusgraveTexture:
        self.node.inputs['Gain'].default_value = gain
        return self

    def get_mix_factor_output(self) -> Socket:
        return self.get_output('Fac')

    def compute_buttons_y_space(self) -> float:
        widget_unit = 20

        # musgrave type
        dy = widget_unit

        return dy


class VoronoiTexture(Node):
    pass


class VoronoiTexture(Node):
    @staticmethod
    def create(tree: Nodes) -> VoronoiTexture:
        return Node.create(tree, 'ShaderNodeTexVoronoi')

    def set_coloring(self, coloring: str) -> VoronoiTexture:
        self.node.coloring = coloring
        return self

    def get_vector_input(self) -> Socket:
        return self.get_input('Vector')

    def get_color_output(self) -> Socket:
        return self.get_output('Color')

    def set_scale(self, scale: float) -> VoronoiTexture:
        self.node.inputs['Scale'].default_value = scale
        return self

    def get_scale_input(self) -> Socket:
        return self.get_input('Scale')

    def get_mix_factor_output(self) -> Socket:
        return self.get_output('Fac')

    def compute_buttons_y_space(self) -> float:
        widget_unit = 20

        # coloring
        dy = widget_unit

        return dy


class ColorRamp(Node):
    pass


class ColorRamp(Node):

    def __init__(self, bpy_node: bpy.types.Node):
        self.stop_index = 0
        Node.__init__(self, bpy_node)

    @staticmethod
    def create(tree: Nodes) -> ColorRamp:
        return Node.create(tree, 'ShaderNodeValToRGB')

    def set_interpolation(self, interpolation: str) -> ColorRamp:
        self.node.color_ramp.interpolation = interpolation
        return self

    def set_mix_factor(self, mix_factor: float) -> ColorRamp:
        self.node.inputs['Fac'].default_value = mix_factor
        return self

    def get_mix_factor_input(self) -> Socket:
        return self.get_input('Fac')

    def add_stop(self, position: float, color: tuple) -> ColorRamp:
        elements = self.node.color_ramp.elements
        if self.stop_index == 0:
            elements.remove(elements[0])
            element = elements[0]
            element.position = position
        else:
            element = elements.new(position)
        element.color = color
        self.stop_index += 1
        return self

    def get_color_output(self) -> Socket:
        return self.get_output('Color')

    def get_alpha_output(self) -> Socket:
        return self.get_output('Alpha')

    def compute_width(self):
        widget_unit = 20
        templateColorRamp_width = 10.0 * widget_unit
        node_width = self.get_width()
        if templateColorRamp_width > node_width:
            node_width = templateColorRamp_width
        return node_width

    def compute_buttons_y_space(self) -> float:
        # see uiTemplateColorRamp interface_templates.c
        widget_unit = 20
        template_space = 5

        dy = template_space

        # add/delete/flip/interpolation buttons row
        dy += widget_unit
        dy += 2  # value in colorband_buttons_large

        # colorband
        dy += widget_unit

        # position / color
        dy += 65  # value in colorband_buttons_large

        return dy


class RGBCurve(Node):
    pass


class RGBCurve(Node):
    def __init__(self, bpy_node: bpy.types.Node):
        self.control_point_index = 0
        Node.__init__(self, bpy_node)

    @staticmethod
    def create(tree: Nodes) -> RGBCurve:
        return Node.create(tree, 'ShaderNodeRGBCurve')

    def set_mix_factor(self, mix_factor: float) -> RGBCurve:
        self.node.inputs['Fac'].default_value = mix_factor
        return self

    def set_color(self, color: tuple) -> RGBCurve:
        self.node.inputs['Color'].default_value = color
        return self

    def get_color_input(self) -> Socket:
        return self.get_input('Color')

    def get_color_output(self) -> Socket:
        return self.get_output('Color')

    def add_control_point(self,
                          location: tuple,
                          handle_type: str='AUTO') -> RGBCurve:
        curve = self.node.mapping.curves[3]
        if self.control_point_index > 1:
            point = curve.points.new(0.0, 0.0)
        else:
            point = curve.points[self.control_point_index]
        point.location = location
        point.handle_type = handle_type

        self.control_point_index += 1
        return self

    def compute_buttons_y_space(self) -> float:
        # see node_buts_curvecol in drawnode.c and and curvemap_buttons_layout
        # in interface_templates.c, and templatespace in interface_layout.c ...

        # ui_litem_layout_root in interface_layout.c => column layout set by
        # default with space set to templatespace from uiBlockLayout
        widget_unit = 20
        template_space = 5
        dy = 0.0

        # buttons row
        button_height = widget_unit
        dy += button_height
        dy += template_space

        # curve
        curve_height = 8.0 * widget_unit
        dy += curve_height
        dy += template_space

        # x/y sliders
        sliders_height = widget_unit
        dy += sliders_height
        dy += template_space

        return dy


class Math(Node):
    pass


class Math(Node):
    @staticmethod
    def create(tree: Nodes) -> Math:
        return Node.create(tree, 'ShaderNodeMath')

    def set_operation(self, operation: str) -> Math:
        self.node.operation = operation
        return self

    def set_use_clamp(self, use_clamp: bool) -> Math:
        self.node.use_clamp = use_clamp
        return self

    def set_first_value(self, value: float) -> Math:
        self.node.inputs[0].default_value = value
        return self

    def set_second_value(self, value: float) -> Math:
        self.node.inputs[1].default_value = value
        return self

    def get_first_value_input(self) -> Socket:
        return self.get_input(0)

    def get_second_value_input(self) -> Socket:
        return self.get_input(1)

    def get_value_output(self) -> Socket:
        return self.get_output('Value')

    def compute_buttons_y_space(self) -> float:
        # see node_buts_math in draw_node.c
        widget_unit = 20
        # block layout space
        template_space = 5

        # operation
        dy = widget_unit
        dy += template_space

        # use clamp
        dy += widget_unit
        dy += template_space

        return dy


class SeparateRGB(Node):
    pass

class SeparateRGB(Node):
    @staticmethod
    def create(tree: Nodes) -> SeparateRGB:
        return Node.create(tree, 'ShaderNodeSeparateRGB')

    def get_image_input(self) -> Socket:
        return self.get_input("Image")

    def get_R_output(self) -> Socket:
        return self.get_output('R')

    def get_G_output(self) -> Socket:
        return self.get_output('G')

    def get_B_output(self) -> Socket:
        return self.get_output('B')


class SeparateXYZ(Node):
    pass


class SeparateXYZ(Node):
    @staticmethod
    def create(tree: Nodes) -> SeparateXYZ:
        return Node.create(tree, 'ShaderNodeSeparateXYZ')

    def get_vector_input(self) -> Socket:
        return self.get_input('Vector')

    def get_X_output(self) -> Socket:
        return self.get_output('X')

    def get_Y_output(self) -> Socket:
        return self.get_output('Y')

    def get_Z_output(self) -> Socket:
        return self.get_output('Z')


class CombineXYZ(Node):
    pass


class CombineXYZ(Node):
    @staticmethod
    def create(tree: Nodes) -> CombineXYZ:
        return Node.create(tree, 'ShaderNodeCombineXYZ')

    def get_X_input(self) -> Socket:
        return self.get_input('X')

    def get_Y_input(self) -> Socket:
        return self.get_input('Y')

    def get_Z_input(self) -> Socket:
        return self.get_input('Z')

    def get_vector_output(self) -> Socket:
        return self.get_output('Vector')


class Value(Node):
    pass


class Value(Node):
    @staticmethod
    def create(tree: Nodes) -> Value:
        return Node.create(tree, 'ShaderNodeValue')

    def set_value(self, value: float) -> Value:
        self.node.outputs['Value'].default_value = value
        return self

    def get_value_output(self) -> Socket:
        return self.get_output('Value')


class BsdfDiffuse(Node):
    pass


class BsdfDiffuse(Node):
    @staticmethod
    def create(tree: Nodes) -> BsdfDiffuse:
        return Node.create(tree, 'ShaderNodeBsdfDiffuse')

    def set_color(self, color: tuple) -> BsdfDiffuse:
        self.node.inputs['Color'].default_value = color
        return self

    def get_color_input(self) -> Socket:
        return self.get_input('Color')

    def set_roughness(self, roughness: float) -> BsdfDiffuse:
        self.node.inputs['Roughness'].default_value = roughness
        return self

    def get_normal_input(self) -> Socket:
        return self.get_input('Normal')

    def get_bsdf_output(self) -> Socket:
        return self.get_output('BSDF')


class BsdfGlossy(Node):
    pass


class BsdfGlossy(Node):
    @staticmethod
    def create(tree: Nodes) -> BsdfGlossy:
        return Node.create(tree, 'ShaderNodeBsdfGlossy')

    def set_distribution(self, distribution: str) -> BsdfGlossy:
        self.node.distribution = distribution
        return self

    def set_color(self, color: tuple) -> BsdfGlossy:
        self.node.inputs['Color'].default_value = color
        return self

    def get_color_input(self) -> Socket:
        return self.get_input('Color')

    def set_roughness(self, roughness: float) -> BsdfGlossy:
        self.node.inputs['Roughness'].default_value = roughness
        return self

    def get_normal_input(self) -> Socket:
        return self.get_input('Normal')

    def get_bsdf_output(self) -> Socket:
        return self.get_output('BSDF')

    def compute_buttons_y_space(self) -> float:
        widget_unit = 20

        # distribution
        dy = widget_unit

        return dy


class MixShader(Node):
    pass


class MixShader(Node):
    @staticmethod
    def create(tree: Nodes) -> MixShader:
        return Node.create(tree, 'ShaderNodeMixShader')

    def set_mix_factor(self, mix_factor: float) -> MixShader:
        self.node.inputs['Fac'].default_value = mix_factor
        return self

    def get_mix_factor_input(self) -> Socket:
        return self.get_input('Fac')

    def get_first_shader_input(self) -> Socket:
        return self.get_input(1)

    def get_second_shader_input(self) -> Socket:
        return self.get_input(2)

    def get_shader_output(self) -> Socket:
        return self.get_output('Shader')


class Fresnel(Node):
    pass


class Fresnel(Node):
    @staticmethod
    def create(tree: Nodes) -> Fresnel:
        return Node.create(tree, 'ShaderNodeFresnel')

    def set_ior(self, ior: float) -> Fresnel:
        self.node.inputs['IOR'].default_value = ior
        return self

    def get_normal_input(self) -> Socket:
        return self.get_input('Normal')

    def get_mix_factor_output(self) -> Socket:
        return self.get_output('Fac')


class Invert(Node):
    pass


class Invert(Node):
    @staticmethod
    def create(tree: Nodes) -> Invert:
        return Node.create(tree, 'ShaderNodeInvert')

    def set_mix_factor(self, mix_factor: float) -> Invert:
        self.node.inputs['Fac'].default_value = mix_factor
        return self

    def get_mix_factor_input(self) -> Socket:
        return self.get_input('Fac')

    def set_color(self, color: tuple) -> Invert:
        self.node.inputs['Color'].default_value = color
        return self

    def get_color_input(self) -> Socket:
        return self.get_input('Color')

    def get_color_output(self) -> Socket:
        return self.get_output('Color')


class Bump(Node):
    pass


class Bump(Node):
    @staticmethod
    def create(tree: Nodes) -> Invert:
        return Node.create(tree, 'ShaderNodeBump')

    def invert(self) -> Bump:
        self.node.invert = True
        return self

    def set_strength(self, strength: float) -> Bump:
        self.node.inputs['Strength'].default_value = strength
        return self

    def set_distance(self, distance: float) -> Bump:
        self.node.inputs['Distance'].default_value = distance
        return self

    def get_height_input(self) -> Socket:
        return self.get_input('Height')

    def get_normal_input(self) -> Socket:
        return self.get_input('Normal')

    def get_normal_output(self) -> Socket:
        return self.get_output('Normal')

    def compute_buttons_y_space(self) -> float:
        widget_unit = 20

        # invert
        dy = widget_unit

        return dy


class OutputMaterial(Node):
    pass


class OutputMaterial(Node):
    @staticmethod
    def create(tree: Nodes) -> OutputMaterial:
        return Node.create(tree, 'ShaderNodeOutputMaterial')

    def get_surface_input(self) -> Socket:
        return self.get_input('Surface')

    def get_volume_input(self) -> Socket:
        return self.get_input('Volume')

    def get_displacement_input(self) -> Socket:
        return self.get_input('Displacement')


class WoodPatternBartek:

    def build(self) -> Group:
        wood_pattern = Group.create("Wood Grain Base Bartek")
        wood_pattern.\
            set_vector_input("Texture coordinates",
                             mathutils.Vector((0.0, 0.0, 0.0))).\
            set_float_input("Tree bend radius", 0.5).\
            set_float_input("Tree bend diversity", 0.2).\
            set_float_input("Additional bend radius", 0.09).\
            set_float_input("Additional bend diversity", 3.0).\
            set_float_input("Growth rings amount", 100.0).\
            set_float_input("Growth rings distort", 0.650).\
            set_float_input("Growth rings distort 2", 0.04).\
            set_color_input("Length axis", [0.0, 1.0, 1.0, 1.0])
        wood_pattern.\
            set_color_output("Grain pattern", [0.0, 0.0, 0.0, 0.0]).\
            set_vector_output("Coordinates", mathutils.Vector((0.0, 0.0, 0.0)))

        group_input = GroupInput.\
            create(wood_pattern).\
            set_location((0.0, 0.0))

        extended_coords = MixRGB.\
            create(wood_pattern).\
            set_label("Extend length axis to infinity").\
            set_position(OnTheRightSideOf(group_input).with_distance(100.0)).\
            set_blend_type('MULTIPLY').\
            set_mix_factor(1.0)

        wood_pattern.link(group_input.get_output("Texture coordinates"),
                          extended_coords.get_first_color_input())
        wood_pattern.link(group_input.get_output("Length axis"),
                          extended_coords.get_second_color_input())
        frame, distorted_coords = self.add_distortion(wood_pattern,
                                                      group_input,
                                                      extended_coords)

        frame, textures_color = self.get_textures_color(wood_pattern,
                                                        group_input,
                                                        distorted_coords,
                                                        frame)
        frame, rings_pattern = self.get_rings_color(wood_pattern,
                                                    group_input,
                                                    textures_color,
                                                    frame)

        pattern_ramp = ColorRamp.\
            create(wood_pattern).\
            set_position(on_the_right_side_of(frame).
                         with_distance(50.0)).\
            add_stop(0.0, (1.0, 1.0, 1.0, 0.0)).\
            add_stop(0.659, (0.0, 0.0, 0.0, 1.0))
        wood_pattern.link(rings_pattern,
                          pattern_ramp.get_mix_factor_input())

        group_output = GroupOutput.\
            create(wood_pattern).\
            set_position(on_the_right_side_of(pattern_ramp).with_distance(100.0))

        wood_pattern.link(pattern_ramp.get_alpha_output(),
                          group_output.get_input("Grain pattern"))
        wood_pattern.link(distorted_coords, group_output.get_input("Coordinates"))

        return wood_pattern


    @staticmethod
    def add_distortion(wood_pattern: Group,
                       group_input: Node,
                       tex_coordinates: MixRGB) -> tuple:
        frame = Frame.\
            create(wood_pattern).\
            set_label("Distortion").\
            set_shrink(True)

        distort_tex = NoiseTexture.\
            create(wood_pattern).\
            set_parent(frame).\
            set_location((50.0, 0.0)).\
            set_detail(2.0).\
            set_distortion(0.0)
        wood_pattern.link(group_input.get_output("Texture coordinates"),
                          distort_tex.get_vector_input())
        wood_pattern.link(group_input.get_output("Tree bend diversity"),
                          distort_tex.get_scale_input())

        small_distort_tex = NoiseTexture.\
            create(wood_pattern).\
            set_parent(frame).\
            set_position(below(distort_tex).
                         with_distance(50.0)).\
            set_detail(2.0).\
            set_distortion(0.0)
        wood_pattern.link(group_input.get_output("Texture coordinates"),
                          small_distort_tex.get_vector_input())
        wood_pattern.link(group_input.get_output("Additional bend diversity"),
                          small_distort_tex.get_scale_input())

        reset_distort_direction = MixRGB.\
            create(wood_pattern).\
            set_label("Reset direction").\
            set_parent(frame).\
            set_position(on_the_right_side_of(distort_tex).
                         with_distance(50.0)).\
            set_blend_type('SUBTRACT').\
            set_mix_factor(1.0).\
            set_second_color((0.5, 0.5, 0.5, 1.0))
        wood_pattern.link(distort_tex.get_color_output(),
                          reset_distort_direction.get_first_color_input())

        reset_small_distort_direction = MixRGB.\
            create(wood_pattern).\
            set_label("Reset direction").\
            set_parent(frame).\
            set_position(on_the_right_side_of(small_distort_tex).
                         with_distance(50.0)).\
            set_blend_type('SUBTRACT').\
            set_mix_factor(1.0).\
            set_second_color((0.5, 0.5, 0.5, 1.0))
        wood_pattern.link(small_distort_tex.get_color_output(),
                          reset_small_distort_direction.get_first_color_input())

        add_distortion = MixRGB.\
            create(wood_pattern).\
            set_label("Add distortion").\
            set_parent(frame).\
            set_position(on_the_right_side_of(reset_distort_direction).
                         with_distance(50.0)).\
            set_blend_type('ADD')
        wood_pattern.link(group_input.get_output("Tree bend radius"),
                          add_distortion.get_mix_factor_input())
        wood_pattern.link(tex_coordinates.get_color_output(),
                          add_distortion.get_first_color_input())
        wood_pattern.link(reset_distort_direction.get_color_output(),
                          add_distortion.get_second_color_input())

        add_small_distortion = MixRGB.\
            create(wood_pattern).\
            set_label("Add smaller distortion").\
            set_parent(frame).\
            set_position(on_the_right_side_of(reset_small_distort_direction).
                         with_distance(50.0)).\
            set_blend_type('ADD')
        wood_pattern.link(group_input.get_output("Additional bend radius"),
                          add_small_distortion.get_mix_factor_input())
        wood_pattern.link(add_distortion.get_color_output(),
                          add_small_distortion.get_first_color_input())
        wood_pattern.link(reset_small_distort_direction.get_color_output(),
                          add_small_distortion.get_second_color_input())

        frame.set_position(on_the_right_side_of(tex_coordinates).
                           with_distance(50.0))

        return frame, add_small_distortion.get_color_output()

    @staticmethod
    def get_textures_color(wood_pattern: Group,
                           group_input: Node,
                           tex_coordinates: Socket,
                           previous_positional_node: Node) -> tuple:
        frame = Frame.\
            create(wood_pattern).\
            set_label("Textures").\
            set_shrink(True)

        gradient = GradientTexture.\
            create(wood_pattern).\
            set_parent(frame).\
            set_location((50.0, 0.0)).\
            set_type('SPHERICAL')
        wood_pattern.link(tex_coordinates, gradient.get_vector_input())

        first_noise_tex = NoiseTexture.\
            create(wood_pattern).\
            set_parent(frame).\
            set_position(below(gradient).
                         with_distance(50.0)).\
            set_scale(0.5).\
            set_detail(16.0).\
            set_distortion(9.5)
        wood_pattern.link(tex_coordinates, first_noise_tex.get_vector_input())

        second_noise_tex = NoiseTexture.\
            create(wood_pattern).\
            set_parent(frame).\
            set_position(below(first_noise_tex).
                         with_distance(50.0)).\
            set_scale(500.0).\
            set_detail(18.0).\
            set_distortion(8.0)
        wood_pattern.link(tex_coordinates, second_noise_tex.get_vector_input())

        ramp_second_noise = ColorRamp.\
            create(wood_pattern).\
            set_parent(frame).\
            set_position(on_the_right_side_of(second_noise_tex).
                         with_distance(50.0)).\
            add_stop(0.456, (0.0, 0.0, 0.0, 1.0)).\
            add_stop(1.0, (1.0, 1.0, 1.0, 1.0))
        wood_pattern.link(second_noise_tex.get_color_output(),
                          ramp_second_noise.get_mix_factor_input())

        overlay_first_noise = MixRGB.\
            create(wood_pattern).\
            set_parent(frame).\
            set_position(on_the_right_side_of(first_noise_tex).
                         with_distance(50.0)).\
            set_blend_type('OVERLAY')
        wood_pattern.link(group_input.get_output("Growth rings distort"),
                          overlay_first_noise.get_mix_factor_input())
        wood_pattern.link(gradient.get_color_output(),
                          overlay_first_noise.get_first_color_input())
        wood_pattern.link(first_noise_tex.get_color_output(),
                          overlay_first_noise.get_second_color_input())

        overlay_second_noise = MixRGB.\
            create(wood_pattern).\
            set_parent(frame).\
            set_position(on_the_right_side_of(ramp_second_noise).
                         with_distance(50.0)).\
            set_blend_type('OVERLAY')
        wood_pattern.link(group_input.get_output("Growth rings distort 2"),
                          overlay_second_noise.get_mix_factor_input())
        wood_pattern.link(overlay_first_noise.get_color_output(),
                          overlay_second_noise.get_first_color_input())
        wood_pattern.link(ramp_second_noise.get_color_output(),
                          overlay_second_noise.get_second_color_input())

        frame.set_position(on_the_right_side_of(previous_positional_node).
                         with_distance(50.0))
        return frame, overlay_second_noise.get_color_output()

    @staticmethod
    def get_rings_color(wood_pattern: Group,
                        group_input: Node,
                        textures_color: Socket,
                        previous_positional_node: Node) -> tuple:
        frame = Frame.\
            create(wood_pattern).\
            set_label("Rings").\
            set_shrink(True)

        density_control = RGBCurve.\
            create(wood_pattern).\
            set_label("Rings density").\
            set_parent(frame).\
            set_location((50.0, 0.0)).\
            add_control_point((0.0, 0.0)).\
            add_control_point((0.309, 0.462)).\
            add_control_point((0.886, 0.831)).\
            add_control_point((1.0, 1.0))
        wood_pattern.link(textures_color,
                          density_control.get_color_input())

        rings_count = Math.\
            create(wood_pattern).\
            set_label("Rings count").\
            set_parent(frame).\
            set_position(below(density_control).
                         with_distance(50.0)).\
            set_operation('DIVIDE').\
            set_first_value(1.0)
        wood_pattern.link(group_input.get_output("Growth rings amount"),
                          rings_count.get_second_value_input())

        make_rings = Math.\
            create(wood_pattern).\
            set_label("Make rings").\
            set_parent(frame).\
            set_position(on_the_right_side_of(density_control).
                         with_distance(50.0)).\
            set_operation('MODULO')
        wood_pattern.link(density_control.get_color_output(),
                          make_rings.get_first_value_input())
        wood_pattern.link(rings_count.get_value_output(),
                          make_rings.get_second_value_input())

        restore_brightness = Math.\
            create(wood_pattern).\
            set_label("Restore brightness").\
            set_parent(frame).\
            set_position(on_the_right_side_of(make_rings).
                         with_distance(50.0)).\
            set_operation('DIVIDE')
        wood_pattern.link(make_rings.get_value_output(),
                          restore_brightness.get_first_value_input())
        wood_pattern.link(rings_count.get_value_output(),
                          restore_brightness.get_second_value_input())

        make_softest_transition = RGBCurve.\
            create(wood_pattern).\
            set_label("Softest transition").\
            set_parent(frame).\
            set_position(on_the_right_side_of(restore_brightness).
                         with_distance(50.0)).\
            add_control_point((0.0, 0.0)).\
            add_control_point((0.923, 1.0), 'VECTOR').\
            add_control_point((1.0, 0.0))
        wood_pattern.link(restore_brightness.get_value_output(),
                          make_softest_transition.get_color_input())

        frame.set_position(on_the_right_side_of(previous_positional_node).
                           with_distance(50.0))
        return frame, make_softest_transition.get_color_output()


# support fibres are "dark background"
class SupportFibresCekhunen:
    def build(self) -> Group:
        support_fibres = Group.create("Support fibres")

        support_fibres.\
            set_vector_input("Texture coordinates",
                             mathutils.Vector((0.0, 0.0, 0.0))).\
            set_color_input("Color1", [0.413, 0.165, 0.038, 1.0]).\
            set_color_input("Color2", [0.546, 0.216, 0.048, 1.0]).\
            set_color_input("Length scale", [0.05, 1.0, 1.0, 1.0]).\
            set_color_input("Depth scale", [1.0, 1.0, 0.5, 1.0]).\
            set_float_input("Fractal texture scale", 2000.0)
        support_fibres.\
            set_color_output("Color", [0.0, 0.0, 0.0, 0.0])

        group_input = GroupInput.\
            create(support_fibres).\
            set_location((0.0, 0.0))

        scale_length = MixRGB.\
            create(support_fibres).\
            set_label("Scale length").\
            set_position(on_the_right_side_of(group_input).
                         with_distance(50.0)).\
            set_blend_type('MULTIPLY').\
            set_mix_factor(1.0)
        support_fibres.link(group_input.get_output("Texture coordinates"),
                            scale_length.get_first_color_input())
        support_fibres.link(group_input.get_output("Length scale"),
                            scale_length.get_second_color_input())

        scale_depth = MixRGB.\
            create(support_fibres).\
            set_label("Scale depth").\
            set_position(on_the_right_side_of(scale_length).
                         with_distance(50.0)).\
            set_blend_type('MULTIPLY').\
            set_mix_factor(1.0)
        support_fibres.link(scale_length.get_color_output(),
                            scale_depth.get_first_color_input())
        support_fibres.link(group_input.get_output("Depth scale"),
                            scale_depth.get_second_color_input())

        musgrave = MusgraveTexture.\
            create(support_fibres).\
            set_position(on_the_right_side_of(scale_depth).
                         with_distance(50.0)).\
            set_type('FBM').\
            set_detail(3.0).\
            set_dimension(2.0).\
            set_lacunarity(1.0).\
            set_offset(0.0).\
            set_gain(1.0)
        support_fibres.link(scale_depth.get_color_output(),
                            musgrave.get_vector_input())
        support_fibres.link(group_input.get_output("Fractal texture scale"),
                            musgrave.get_scale_input())

        mix = MixRGB.\
            create(support_fibres).\
            set_position(on_the_right_side_of(musgrave).
                         with_distance(50.0)).\
            set_blend_type('MIX')
        support_fibres.link(musgrave.get_mix_factor_output(),
                            mix.get_mix_factor_input())
        support_fibres.link(group_input.get_output("Color1"),
                            mix.get_first_color_input())
        support_fibres.link(group_input.get_output("Color2"),
                            mix.get_second_color_input())

        group_output = GroupOutput.\
            create(support_fibres).\
            set_position(on_the_right_side_of(mix).
                         with_distance(50.0))

        support_fibres.link(mix.get_color_output(),
                            group_output.get_input("Color"))

        return support_fibres


class AxialParenchimaCekhunen:

    def build(self) -> Group:
        axial_parenchima = Group.create("Axial Parenchima")
        axial_parenchima.\
            set_vector_input("Texture coordinates",
                             mathutils.Vector((0.0, 0.0, 0.0))).\
            set_color_input("Color1", [0.694, 0.275, 0.061, 1.0]).\
            set_color_input("Color2", [0.831, 0.546, 0.238, 1.0]).\
            set_color_input("Length scale", [0.1, 1.0, 1.0, 1.0]).\
            set_float_input("Noise scale", 200.0)
        axial_parenchima.\
            set_color_output("Color", [0.0, 0.0, 0.0, 0.0])

        group_input = GroupInput.\
            create(axial_parenchima).\
            set_location((0.0, 0.0))

        scale = MixRGB.\
            create(axial_parenchima).\
            set_label("Scale length").\
            set_position(on_the_right_side_of(group_input).
                         with_distance(50.0)).\
            set_blend_type('MULTIPLY').\
            set_mix_factor(1.0)
        axial_parenchima.link(group_input.get_output("Texture coordinates"),
                              scale.get_first_color_input())
        axial_parenchima.link(group_input.get_output("Length scale"),
                              scale.get_second_color_input())

        noise = NoiseTexture.\
            create(axial_parenchima).\
            set_position(on_the_right_side_of(scale).
                         with_distance(50.0)).\
            set_detail(5.0).\
            set_distortion(5.0)
        axial_parenchima.link(scale.get_color_output(),
                              noise.get_vector_input())
        axial_parenchima.link(group_input.get_output("Noise scale"),
                              noise.get_scale_input())

        mix = MixRGB.\
            create(axial_parenchima).\
            set_position(on_the_right_side_of(noise).
                         with_distance(50.0)).\
            set_blend_type('MIX')
        axial_parenchima.link(noise.get_mix_factor_output(),
                              mix.get_mix_factor_input())
        axial_parenchima.link(group_input.get_output("Color1"),
                              mix.get_first_color_input())
        axial_parenchima.link(group_input.get_output("Color2"),
                              mix.get_second_color_input())

        group_output = GroupOutput.\
            create(axial_parenchima).\
            set_position(on_the_right_side_of(mix).
                         with_distance(50.0))

        axial_parenchima.link(mix.get_color_output(),
                              group_output.get_input("Color"))

        return axial_parenchima


class LongGrainVesselsCekhunen:

    def build(self) -> Group:
        vessels = Group.create("Long grain vessels")
        vessels.\
            set_vector_input("Texture coordinates",
                             mathutils.Vector((0.0, 0.0, 0.0))).\
            set_color_input("Length scale", [0.025, 1.0, 1.0, 1.0]).\
            set_float_input("Intensity", 3000.0)
        vessels.\
            set_color_output("Color", [0.0, 0.0, 0.0, 0.0])

        group_input = GroupInput.\
            create(vessels).\
            set_location((0.0, 0.0))

        scale_length = MixRGB.\
            create(vessels).\
            set_label("Scale length").\
            set_position(on_the_right_side_of(group_input).
                         with_distance(50.0)).\
            set_blend_type('MULTIPLY').\
            set_mix_factor(1.0)
        vessels.link(group_input.get_output("Texture coordinates"),
                     scale_length.get_first_color_input())
        vessels.link(group_input.get_output("Length scale"),
                     scale_length.get_second_color_input())

        voronoi = VoronoiTexture.\
            create(vessels).\
            set_position(on_the_right_side_of(scale_length).
                         with_distance(50.0)).\
            set_coloring('INTENSITY')
        vessels.link(scale_length.get_color_output(),
                     voronoi.get_vector_input())
        vessels.link(group_input.get_output("Intensity"),
                     voronoi.get_scale_input())

        select_vessels = ColorRamp.\
            create(vessels).\
            set_label("Select vessels").\
            set_position(on_the_right_side_of(voronoi).
                         with_distance(50.0)).\
            add_stop(0.086, (1.0, 1.0, 1.0, 1.0)).\
            add_stop(0.141, (0.0, 0.0, 0.0, 1.0))
        vessels.link(voronoi.get_mix_factor_output(),
                     select_vessels.get_mix_factor_input())

        group_output = GroupOutput.\
            create(vessels).\
            set_position(on_the_right_side_of(select_vessels).
                         with_distance(50.0))
        vessels.link(select_vessels.get_color_output(),
                     group_output.get_input("Color"))

        return vessels


class Rays:
    @classmethod
    def build(cls) -> Group:
        rays = Group.create("Rays")
        rays.\
            set_vector_input("Texture coordinates",
                             mathutils.Vector((0.0, 0.0, 0.0))).\
            set_float_input("Count", 50.0).\
            set_float_input("Thickness", 0.005).\
            set_float_input("Distortion factor", 0.5).\
            set_float_input("Distortion scale", 0.6)
        rays.\
            set_color_output("Color", [0.0, 0.0, 0.0, 0.0])

        group_input = GroupInput.\
            create(rays).\
            set_location((0.0, 0.0))

        previous, distorted_coords = cls.add_distortion(rays, group_input, group_input)
        previous, angle= cls.get_angle(rays, distorted_coords, previous)
        previous, is_ray = cls.is_ray(rays, group_input, angle, previous)
        previous, cut_rays = cls.cut_rays(rays, group_input, distorted_coords, is_ray, previous)

        group_output = GroupOutput.\
            create(rays).\
            set_position(on_the_right_side_of(previous).
                         with_distance(50.0))
        rays.link(cut_rays,
                  group_output.get_input("Color"))

        return rays

    @staticmethod
    def add_distortion(rays: Group,
                       group_input: Node,
                       previous_positional_node: Node) -> tuple:
        frame = Frame.\
            create(rays).\
            set_label("Distortion").\
            set_shrink(True)

        distort_tex = NoiseTexture.\
            create(rays).\
            set_parent(frame).\
            set_location((50.0, 0.0)).\
            set_detail(16.0).\
            set_distortion(2.1)
        rays.link(group_input.get_output("Texture coordinates"),
                  distort_tex.get_vector_input())
        rays.link(group_input.get_output("Distortion scale"),
                  distort_tex.get_scale_input())

        reset_distort_direction = MixRGB.\
            create(rays).\
            set_label("Reset direction").\
            set_parent(frame).\
            set_position(on_the_right_side_of(distort_tex).
                         with_distance(50.0)).\
            set_blend_type('SUBTRACT').\
            set_mix_factor(1.0).\
            set_second_color((0.5, 0.5, 0.5, 1.0))
        rays.link(distort_tex.get_color_output(),
                  reset_distort_direction.get_first_color_input())

        add_distortion = MixRGB.\
            create(rays).\
            set_label("Add distortion").\
            set_parent(frame).\
            set_position(on_the_right_side_of(reset_distort_direction).
                         with_distance(50.0)).\
            set_blend_type('ADD')
        rays.link(group_input.get_output("Distortion factor"),
                  add_distortion.get_mix_factor_input())
        rays.link(group_input.get_output("Texture coordinates"),
                  add_distortion.get_first_color_input())
        rays.link(reset_distort_direction.get_color_output(),
                  add_distortion.get_second_color_input())

        frame.set_position(on_the_right_side_of(previous_positional_node).
                           with_distance(50.0))

        return frame, add_distortion.get_color_output()

    # RADIAL gradient texture does the same thing ...
    @staticmethod
    def create_angle_group() -> Group:

        angle = Group.create("Angle")
        angle.\
            set_vector_input("Texture coordinates",
                             mathutils.Vector((0.0, 0.0, 0.0)))
        angle.\
            set_color_output("Color", [0.0, 0.0, 0.0, 0.0])

        group_input = GroupInput.\
            create(angle).\
            set_location((0.0, 0.0))

        get_xy = SeparateXYZ.\
            create(angle).\
            set_position(on_the_right_side_of(group_input).
                         with_distance(50.0))
        angle.link(group_input.get_output("Texture coordinates"),
                   get_xy.get_vector_input())

        frame = Frame.\
            create(angle).\
            set_position(on_the_right_side_of(get_xy).
                         with_distance(50.0)).\
            set_label("atan2(y, x)=2 arctan((sqrt(x^2+y^2)-x)/y)").\
            set_shrink(True)

        x_square = Math.\
            create(angle).\
            set_parent(frame).\
            set_location((50.0, 0.0)).\
            set_operation("POWER").\
            set_second_value(2.0)
        angle.link(get_xy.get_X_output(), x_square.get_first_value_input())

        y_square = Math.\
            create(angle).\
            set_parent(frame).\
            set_position(below(x_square).
                         with_distance(50.0)).\
            set_operation("POWER").\
            set_second_value(2.0)
        angle.link(get_xy.get_Y_output(), y_square.get_first_value_input())

        add_squares = Math.\
            create(angle).\
            set_parent(frame).\
            set_position(on_the_right_side_of(x_square).
                         with_distance(50.0)).\
            set_operation("ADD")
        angle.link(x_square.get_value_output(),
                   add_squares.get_first_value_input())
        angle.link(y_square.get_value_output(),
                   add_squares.get_second_value_input())

        square_root = Math.\
            create(angle).\
            set_parent(frame).\
            set_position(on_the_right_side_of(add_squares).
                         with_distance(50.0)).\
            set_operation("POWER").\
            set_second_value(0.5)
        angle.link(add_squares.get_value_output(),
                   square_root.get_first_value_input())

        subtract_x = Math.\
            create(angle).\
            set_parent(frame).\
            set_position(on_the_right_side_of(square_root).
                         with_distance(50.0)).\
            set_operation("SUBTRACT")
        angle.link(square_root.get_value_output(),
                   subtract_x.get_first_value_input())
        angle.link(get_xy.get_X_output(),
                   subtract_x.get_second_value_input())

        divide_by_y = Math.\
            create(angle).\
            set_parent(frame).\
            set_position(on_the_right_side_of(subtract_x).
                         with_distance(50.0)).\
            set_operation("DIVIDE")
        angle.link(subtract_x.get_value_output(),
                   divide_by_y.get_first_value_input())
        angle.link(get_xy.get_Y_output(),
                   divide_by_y.get_second_value_input())

        arctan = Math.\
            create(angle).\
            set_parent(frame).\
            set_position(on_the_right_side_of(divide_by_y).
                         with_distance(50.0)).\
            set_operation("ARCTANGENT")
        angle.link(divide_by_y.get_value_output(),
                   arctan.get_first_value_input())

        multiply_by_2 = Math.\
            create(angle).\
            set_parent(frame).\
            set_position(on_the_right_side_of(arctan).
                         with_distance(50.0)).\
            set_operation("MULTIPLY").\
            set_first_value(2.0)
        angle.link(arctan.get_value_output(),
                   multiply_by_2.get_second_value_input())

        start_from_0 = Math.\
            create(angle).\
            set_label("Start from 0").\
            set_position(on_the_right_side_of(frame).
                         with_distance(50.0)).\
            set_operation("ADD")

        pi_value = Value.\
            create(angle).\
            set_label("PI").\
            set_position(below(start_from_0).
                         with_distance(50.0)).\
            set_value(pi)
        angle.link(multiply_by_2.get_value_output(),
                   start_from_0.get_first_value_input())
        angle.link(pi_value.get_value_output(),
                   start_from_0.get_second_value_input())

        two_pi_value = Math.\
            create(angle).\
            set_label("2PI").\
            set_position(on_the_right_side_of(pi_value).
                         with_distance(50.0)).\
            set_operation("MULTIPLY").\
            set_first_value(2.0)
        angle.link(pi_value.get_value_output(),
                   two_pi_value.get_second_value_input())

        end_to_1 = Math.\
            create(angle).\
            set_label("End to 1").\
            set_position(on_the_right_side_of(start_from_0).
                         with_distance(50.0)).\
            set_operation("DIVIDE")
        angle.link(start_from_0.get_value_output(),
                   end_to_1.get_first_value_input())
        angle.link(two_pi_value.get_value_output(),
                   end_to_1.get_second_value_input())

        group_output = GroupOutput.\
            create(angle).\
            set_position(on_the_right_side_of(end_to_1).
                         with_distance(50.0))
        angle.link(end_to_1.get_value_output(),
                   group_output.get_input("Color"))

        return angle

    @staticmethod
    def get_angle(rays: Group,
                  distorted_coords: Socket,
                  previous_positional_node: Node) -> tuple:
        separate_xyz = SeparateXYZ.\
            create(rays).\
            set_position(below(previous_positional_node).
                         with_distance(50.0))
        rays.link(distorted_coords, separate_xyz.get_vector_input())

        # swap x and z axis
        combine_xyz = CombineXYZ.\
            create(rays).\
            set_position(on_the_right_side_of(separate_xyz).
                         with_distance(50.0))
        rays.link(separate_xyz.get_X_output(), combine_xyz.get_Z_input())
        rays.link(separate_xyz.get_Y_output(), combine_xyz.get_Y_input())
        rays.link(separate_xyz.get_Z_output(), combine_xyz.get_X_input())

        angle = GradientTexture.\
            create(rays).\
            set_label("angle").\
            set_position(on_the_right_side_of(combine_xyz).
                         with_distance(50.0)).\
            set_type("RADIAL")
        rays.link(combine_xyz.get_vector_output(), angle.get_vector_input())
        return separate_xyz, angle.get_color_output()

    @staticmethod
    def is_ray(rays: Group,
               group_input: Node,
               angle: Socket,
               previous_positional_node: Node) -> tuple:

        frame = Frame.\
            create(rays).\
            set_label("Is ray ?").\
            set_shrink(True)

        ray_delta = Math.\
            create(rays).\
            set_label("Ray delta").\
            set_parent(frame).\
            set_location((50.0, 0.0)).\
            set_operation("DIVIDE").\
            set_first_value(1.0)
        rays.link(group_input.get_output("Count"),
                  ray_delta.get_second_value_input())

        angle_quotient = Math.\
            create(rays).\
            set_label("Angle quotient").\
            set_parent(frame).\
            set_position(on_the_right_side_of(ray_delta).
                         with_distance(50.0)).\
            set_operation("DIVIDE")
        rays.link(angle,
                  angle_quotient.get_first_value_input())
        rays.link(ray_delta.get_value_output(),
                  angle_quotient.get_second_value_input())

        nearest_int = Math.\
            create(rays).\
            set_label("Nearest int").\
            set_parent(frame).\
            set_position(on_the_right_side_of(angle_quotient).
                         with_distance(50.0)).\
            set_operation("ROUND")
        rays.link(angle_quotient.get_value_output(),
                  nearest_int.get_first_value_input())

        nearest_int_dist = Math.\
            create(rays).\
            set_label("Nearest int dist.").\
            set_parent(frame).\
            set_position(on_the_right_side_of(nearest_int).
                         with_distance(50.0)).\
            set_operation("SUBTRACT")
        rays.link(angle_quotient.get_value_output(),
                  nearest_int_dist.get_first_value_input())
        rays.link(nearest_int.get_value_output(),
                  nearest_int_dist.get_second_value_input())

        neareast_int_absolute_dist = Math.\
            create(rays).\
            set_label("Nearest int absolute dist.").\
            set_parent(frame).\
            set_position(on_the_right_side_of(nearest_int_dist).
                         with_distance(50.0)).\
            set_operation("ABSOLUTE")
        rays.link(nearest_int_dist.get_value_output(),
                  neareast_int_absolute_dist.get_first_value_input())

        is_ray = Math.\
            create(rays).\
            set_label("Is ray ?").\
            set_parent(frame).\
            set_position(on_the_right_side_of(neareast_int_absolute_dist).
                         with_distance(50.0)).\
            set_operation("LESS_THAN")
        rays.link(neareast_int_absolute_dist.get_value_output(),
                  is_ray.get_first_value_input())
        rays.link(group_input.get_output("Thickness"),
                  is_ray.get_second_value_input())

        frame.set_position(below(previous_positional_node).
                           with_distance(50.0))

        return frame, is_ray.get_value_output()

    @staticmethod
    def cut_rays(rays: Group,
                 group_input: Node,
                 distorted_coords: Socket,
                 is_ray: Socket,
                 previous_positional_node: Node) -> tuple:

        frame = Frame.\
            create(rays).\
            set_label("Cut rays").\
            set_shrink(True)

        musgrave = MusgraveTexture.\
            create(rays).\
            set_parent(frame).\
            set_location((50.0, 0.0)).\
            set_type('FBM').\
            set_scale(50.0).\
            set_detail(2.0).\
            set_dimension(2.0).\
            set_lacunarity(1.0).\
            set_offset(0.0).\
            set_gain(1.0)
        rays.link(distorted_coords,
                  musgrave.get_vector_input())

        mix = MixRGB.\
            create(rays).\
            set_parent(frame).\
            set_position(on_the_right_side_of(musgrave).
                         with_distance(50.0)).\
            set_blend_type("MIX").\
            set_second_color((0.0, 0.0, 0.0, 1.0))
        rays.link(musgrave.get_mix_factor_output(),
                  mix.get_mix_factor_input())
        rays.link(is_ray,
                  mix.get_first_color_input())

        frame.set_position(below(previous_positional_node).
                           with_distance(50.0))

        return frame, mix.get_color_output()


class DiffuseColorBuilder:
    def __init__(self,
                 wood_pattern,
                 axial_parenchima,
                 support_fibres,
                 vessels,
                 rays):
        self.wood_pattern = wood_pattern
        self.axial_parenchima = axial_parenchima
        self.support_fibres = support_fibres
        self.vessels = vessels
        self.rays = rays

    def build(self, tree: Nodes, position: Position):
        groups = self.build_groups(tree, position)

        wood_pattern = groups[0]
        support_fibres = groups[1]
        axial_parenchima = groups[2]
        vessels = groups[3]
        rays = groups[4]

        tree.link(wood_pattern.get_output('Coordinates'),
                  rays.get_input('Texture coordinates'))

        mix_groups_colors_1 = MixRGB.\
            create(tree).\
            set_position(on_the_right_side_of(support_fibres).
                         with_distance(150.0)).\
            set_blend_type("MIX")
        tree.link(wood_pattern.get_output('Grain pattern'),
                  mix_groups_colors_1.get_mix_factor_input())
        tree.link(support_fibres.get_output('Color'),
                  mix_groups_colors_1.get_first_color_input())
        tree.link(axial_parenchima.get_output('Color'),
                  mix_groups_colors_1.get_second_color_input())

        mix_groups_colors_2 = MixRGB.\
            create(tree).\
            set_position(on_the_right_side_of(mix_groups_colors_1).
                         with_distance(50.0)).\
            set_blend_type('MIX').\
            set_second_color((0.494, 0.196, 0.044, 1.0))
        tree.link(vessels.get_output('Color'),
                  mix_groups_colors_2.get_mix_factor_input())
        tree.link(mix_groups_colors_1.get_color_output(),
                  mix_groups_colors_2.get_first_color_input())

        mix_groups_colors_3 = MixRGB.\
            create(tree).\
            set_position(on_the_right_side_of(mix_groups_colors_2).
                         with_distance(50.0)).\
            set_blend_type('MIX').\
            set_second_color((0.651, 0.429, 0.189, 1.0))
        tree.link(rays.get_output('Color'),
                  mix_groups_colors_3.get_mix_factor_input())
        tree.link(mix_groups_colors_2.get_color_output(),
                  mix_groups_colors_3.get_first_color_input())

        diffuse = BsdfDiffuse.\
            create(tree).\
            set_position(on_the_right_side_of(mix_groups_colors_3).
                         with_distance(50.0)).\
            set_roughness(0.0)
        tree.link(mix_groups_colors_3.get_color_output(),
                  diffuse.get_color_input())

        return diffuse, groups

    def build_groups(self, tree: Nodes, position: Position) -> tuple:
        wood_pattern_grp = self.wood_pattern.build()
        axial_parenchima_grp = self.axial_parenchima.build()
        support_fibres_grp = self.support_fibres.build()
        vessels_grp = self.vessels.build()
        rays_grp = self.rays.build()

        wood_pattern = GroupNode.\
            create(tree).\
            set_position(position).\
            set_node_tree(wood_pattern_grp)

        support_fibres = GroupNode.\
            create(tree).\
            set_position(below(wood_pattern).
                         with_distance(50.0)).\
            set_node_tree(support_fibres_grp)

        axial_parenchima = GroupNode.\
            create(tree).\
            set_position(below(support_fibres).
                         with_distance(50.0)).\
            set_node_tree(axial_parenchima_grp)

        vessels = GroupNode.\
            create(tree).\
            set_position(below(axial_parenchima).
                         with_distance(50.0)).\
            set_node_tree(vessels_grp)

        rays = GroupNode.\
            create(tree).\
            set_position(on_the_right_side_of(wood_pattern).
                         with_distance(150.0)).\
            set_node_tree(rays_grp)

        return wood_pattern,\
               support_fibres,\
               axial_parenchima,\
               vessels,\
               rays


class GlossyReflectionBuilder:
    def build(self,
              tree: Nodes,
              position: Position,
              wood_pattern: GroupNode,
              vessels: GroupNode):
        previous, bump_height = self.set_bump_height(tree,
                                                     position,
                                                     wood_pattern,
                                                     vessels)

        bump = Bump.\
            create(tree).\
            set_position(on_the_right_side_of(previous).
                         with_distance(50.0)).\
            set_strength(0.1).\
            set_distance(0.1)
        tree.link(bump_height, bump.get_height_input())

        glossy = BsdfGlossy.\
            create(tree).\
            set_position(on_the_right_side_of(bump).
                         with_distance(50.0)).\
            set_distribution('GGX').\
            set_color((0.8, 0.8, 0.8, 1.0)).\
            set_roughness(0.0)
        tree.link(bump.get_normal_output(),
                  glossy.get_normal_input())

        return glossy


    @staticmethod
    def set_bump_height(tree: Nodes,
                        position: Position,
                        wood_pattern: ColorRamp,
                        vessels: GroupNode) -> tuple:
        invert_vessels = Invert.\
            create(tree).\
            set_position(position).\
            set_mix_factor(1.0)
        tree.link(vessels.get_output("Color"),
                  invert_vessels.get_color_input())

        vessels_height_control = RGBCurve.\
            create(tree).\
            hide().\
            set_position(on_the_right_side_of(invert_vessels).
                         with_distance(50.0)).\
            add_control_point((0.0, 0.0)).\
            add_control_point((1.0, 0.31875))
        tree.link(invert_vessels.get_color_output(),
                  vessels_height_control.get_color_input())

        wood_pattern_height_control = RGBCurve.\
            create(tree).\
            hide().\
            set_position(above(vessels_height_control).
                         with_distance(50.0)).\
            add_control_point((0.0, 0.0)).\
            add_control_point((1.0, 0.5))
        tree.link(wood_pattern.get_output('Grain pattern'),
                  wood_pattern_height_control.get_color_input())

        mix_height = MixRGB.\
            create(tree).\
            set_position(between(vessels_height_control,
                                 wood_pattern_height_control).
                         on_the_right().
                         with_distance(50.0)).\
            set_blend_type("MIX").\
            set_mix_factor(0.5)
        tree.link(wood_pattern_height_control.get_color_output(),
                  mix_height.get_first_color_input())
        tree.link(vessels_height_control.get_color_output(),
                  mix_height.get_second_color_input())
        return mix_height, mix_height.get_color_output()


class DiffuseGlossyMixer:
    def build(self,
              tree: Nodes,
              diffuse: BsdfDiffuse,
              glossy: BsdfGlossy) -> MixShader:

        mix_shader = MixShader.\
            create(tree).\
            set_position(between(diffuse, glossy).
                         on_the_right().
                         with_distance(50.0))
        tree.link(diffuse.get_bsdf_output(),
                  mix_shader.get_first_shader_input())
        tree.link(glossy.get_bsdf_output(),
                  mix_shader.get_second_shader_input())
        return mix_shader


def test():
    mat = bpy.data.materials.new("WoodMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    nodes = Nodes(mat.node_tree)

    wood_pattern = WoodPatternBartek()
    axial_parenchima = AxialParenchimaCekhunen()
    support_fibres = SupportFibresCekhunen()
    vessels = LongGrainVesselsCekhunen()
    rays = Rays()

    position = Location(Vector((0, 0)))
    diffuse_color_builder = DiffuseColorBuilder(
        wood_pattern,
        axial_parenchima,
        support_fibres,
        vessels,
        rays)
    diffuse, groups = diffuse_color_builder.build(nodes, position)

    wood_pattern_group_node = groups[0]
    vessels_group_node = groups[3]
    position = on_the_right_side_of(vessels_group_node).with_distance(150.0)
    glossy_reflection = GlossyReflectionBuilder()
    glossy = glossy_reflection.build(nodes, position, wood_pattern_group_node, vessels_group_node)

    diffuse_glossy_mixer = DiffuseGlossyMixer()
    shader = diffuse_glossy_mixer.build(nodes, diffuse, glossy)

test()