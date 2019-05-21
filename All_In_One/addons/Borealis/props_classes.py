# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

'''
Contains basic property classes which are used by all parts of Borealis.

This module contains a set of classes for interfacing between blenders custom
properties and the properties used in Neverwinter Nights models. They are used
as holders of the model data and used for dynamically building the GUI in
blender.

:Classes:
`Property`: Base class for all properties.

@author: Erik Ylipää
'''

TAB_SPACE = 2


class Property:
    nodes = []
    name = ""
    blender_ignore = False
    value = None
    data_type = str
    value_written = False
    default = None
    show_in_gui = True
    gui_group = None
    description = None

    def __init__(self, name="", nodes=[], description="", gui_name="",
                 blender_ignore=False, default=None, show_in_gui=True,
                 gui_group="Ungrouped", **kwargs):

        self.name = name
        self.nodes = nodes
        self.description = description
        if gui_name:
            self.gui_name = gui_name
        else:
            self.gui_name = self.name
        self.blender_ignore = blender_ignore
        self.default = default
        if blender_ignore:
            self.show_in_gui = False
        else:
            self.show_in_gui = show_in_gui
        self.gui_group = gui_group

    def get_default_value(self):
        return self.default

    def read_value(self, current_line, model_data):
        self.value = self.format_input(current_line[1])
        self.value_written = True

    def output_values(self):
        yield " " * TAB_SPACE + "%s %s" % (self.name, str(self.value))

    def __str__(self):
        return "\n".join(line for line in self.output_values())

    def update_value(self, value):
        self.value = self.format_input(value)
        self.value_written = True

    def format_input(self, input):
        return self.data_type(input)


class NumberProperty(Property):
    min = None
    max = None

    def __init__(self, min=None, max=None, **kwargs):
        self.min = min
        self.max = max
        super().__init__(**kwargs)


#vector properties are properties that have many values on one row
class VectorProperty(Property):
    data_type = str
    size = None

    def __init__(self, size=3, **kwargs):
        self.size = size
        super().__init__(**kwargs)

    def read_value(self, current_line, model_data):
        self.value = [self.format_input(val) for val in current_line[1:]]
        self.value_written = True

    def update_value(self, value):
        self.value = [self.format_input(val) for val in value]
        self.value_written = True

    def output_values(self):
        yield " " * TAB_SPACE + "%s %s" % (self.name, " ".join([str(val) for val in self.value]))


#matrix properties are properties that have values on multiple rows
class MatrixProperty(Property):
    data_type = str

    def read_value(self, current_line, model_data):
        self.value = []
        #if the current line has less than two tokens, the list is terminated with an endlist
        #token instead of a given number of rows
        if len(current_line) < 2:
            done_reading = False
            while not done_reading:
                line = model_data.pop(0)
                if not line:  # skip empty lines
                    continue
                if line[0] == "endlist":
                    break
                self.value.append([self.format_input(value) for value in line])
        else:
            lines = int(current_line[-1])
            while lines:
                line = model_data.pop(0)
                if not line:  # skip empty lines
                    continue
                self.value.append([self.format_input(value) for value in line])

                lines -= 1

        self.value_written = True

    def update_value(self, value):
        """
        Updates the value of the matrix. value must be a matrix, a sequence of sequences
        """
        self.value = [[self.format_input(val) for val in row] for row in value]
        self.value_written = True

    def output_values(self):
        yield " " * TAB_SPACE + "%s %i" % (self.name, len(self.value))
        for row in self.value:
            yield " " * TAB_SPACE * 2 + " ".join([str(val) for val in row])


class StringProperty(Property):
    data_type = str


class BooleanProperty(Property):
    data_type = bool

    def format_input(self, input):
        #Ugly, but it makes sure float strings are first cast to int, then bool
        # It will convert values between (1,1) to False. I had an issue where
        # a bool value was written as 0.0 in the ascii file
        return bool(int(float(input)))

    def output_values(self):
        value = "0"
        if self.value:
            value = "1"
        yield " " * TAB_SPACE + "%s %s" % (self.name, value)


class EnumProperty(Property):
    """ A property that can only assume a fixed set of values.

        The values are supplied to the constructor as a list or a dictionary,
        but will always be stored as a dictionary. The keys are the names of
        the enums, while the values are the output in the mdl file.
        The name is used as values in Blender, while the outputs are used as
        values in the ascii .mdl file.
    """
    enums = {}
    """ The dictionary which holds the enums in the form {name: output } """
    inverse_enums = {}
    """ An inverse dictionary of the enum in the form {output: name} """
    def __init__(self, enums={}, **kwargs):
        """ The constructor takes the enums as a keyword argument.
            It can be supplied as a list for compability with how it was
            handled before. A list will be converted to a dictionary with keys the
            same as values """
        self.enums = {}
        self.inverse_enums = {}

        if isinstance(enums, list):
            enums = dict(zip(enums, enums))

        #this simply makes sure the values are all strings
        for name, output in enums.items():
            name = str(name)
            output = str(output)
            self.enums[name] = output
            self.inverse_enums[output] = name

        super().__init__(**kwargs)

    def update_value(self, value):
        # Make sure the value is saved as the name, which is what blender expects
        value = str(value)
        if value in self.enums:
            self.value = value
        elif value in self.inverse_enums:
            self.value = self.inverse_enums[value]
        else:
            raise ValueError("Not a valid Enum: %s for %s, valid enums: %s" % (val, self.name, self.enums))
        self.value_written = True

    def read_value(self, current_line, model_data):
        val = str(current_line[1])
        if val in self.enums:
            self.value = val
        elif val in self.inverse_enums:
            self.value = self.inverse_enums[val]
        else:
            raise ValueError("Not a valid Enum: %s for %s, valid enums: %s" % (val, self.name, self.enums))

        self.value_written = True

    def output_values(self):
        if self.value in self.enums:
            val = self.enums[self.value]
        else:
            val = self.value
        yield " " * TAB_SPACE + "%s %s" % (self.name, val)

    def get_blender_items(self):
        return [(name, name, name) for name, output in self.enums.items()]


class IntProperty(NumberProperty):
    data_type = int

    def format_input(self, input):
        # Some export scripts export values that should be integers as floats
        # and the int constructor won't accept float strings as input,
        # therefore we first cast the string to a float, then an int
        return int(float(input))


class IntVectorProperty(IntProperty, VectorProperty):
    data_type = int


class IntMatrixProperty(IntProperty, MatrixProperty):
    data_type = int


class FloatProperty(NumberProperty):
    data_type = float

    def output_values(self):
        # This tidies values, like the max export script seems to do
        yield " " * TAB_SPACE + "%s %.9g" % (self.name, self.value)


class FloatVectorProperty(VectorProperty, FloatProperty):
    data_type = float

    def output_values(self):
        yield " " * TAB_SPACE + "%s %s" % (self.name, " ".join(["%.9g" % val for val in self.value]))


class FloatMatrixProperty(MatrixProperty, FloatProperty):
    data_type = float

    def output_values(self):
        yield " " * TAB_SPACE + "%s %i" % (self.name, len(self.value))
        for row in self.value:
            yield " " * TAB_SPACE * 2 + " ".join(["%.9g" % val for val in row])


class ColorProperty(FloatVectorProperty):
    data_type = float


class AABBTree(MatrixProperty):
    def read_value(self, current_line, model_data):
        def new_node(x1, y1, z1, x2, y2, z2, index, parent=None):
            tree_node = {"co1": [float(x1), float(y1), float(z1)],
                         "co2": [float(x2), float(y2), float(z2)],
                         "left": None,
                         "right": None,
                         "index": int(index),
                         "parent": parent}
            return tree_node

        aabb, x1, y1, z1, x2, y2, z2, index = current_line
        root_node = new_node(x1, y1, z1, x2, y2, z2, index)
        node_stack = [root_node]
        self.value = root_node
        done = False

        while(not done):
            #Peek ahead to see if the next line is also a node in the tree
            if len(model_data[0]) == 7:
                current_line = model_data.pop(0)
                x1, y1, z1, x2, y2, z2, index = current_line
                parent = node_stack[-1]
                current_node = new_node(x1, y1, z1, x2, y2, z2,
                                         index, parent)
                if not parent["left"]:
                    parent["left"] = current_node
                else:
                    parent["right"] = current_node
                    node_stack.pop()

                if current_node["index"] == -1:
                    node_stack.append(current_node)
            else:
                done = True
        self.value_written = True

    def update_value(self, value):
        self.value = value
        self.value_written = True

    def output_values(self):
        root_node = self.value
        x1, y1, z1 = root_node["co1"]
        x2, y2, z2 = root_node["co2"]
        index = root_node["index"]
        yield " " * TAB_SPACE + "aabb %.7f %.7f %.7f %.7f %.7f %.7f %d" % (x1, y1, z1,
                                                         x2, y2, z2, index)
        level = 2
        node_stack = []
        node_stack.append((level, root_node["right"],))
        node_stack.append((level, root_node["left"],))

        while node_stack:
            level, current_node = node_stack.pop()
            x1, y1, z1 = current_node["co1"]
            x2, y2, z2 = current_node["co2"]
            index = current_node["index"]
            yield (" " * TAB_SPACE * level +
                   "%.7f %.7f %.7f %.7f %.7f %.7f %d" %
                   (x1, y1, z1, x2, y2, z2, index))

            left = current_node["left"]
            right = current_node["right"]
            if right:
                node_stack.append((level + 1, current_node["right"],))
            if left:
                node_stack.append((level + 1, current_node["left"],))
