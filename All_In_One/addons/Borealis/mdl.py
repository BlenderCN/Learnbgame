#!/usr/bin/python
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

# <pep8 compliant>

'''
Contains classes and functions for interfacing with Neverwinter Nights ASCII
models.

The classes are organized to mimic how the nodes are organized in a ascii mdl
file. The information about node properties are contained in the `basic_props`
module.

@author: Erik Ylipää
'''

import copy
import os

try:
    from . import basic_props
    from . import node_props
except ValueError:
    import basic_props
    import node_props


TAB_WIDTH = 2
""" The spaces to use for every level of indentation when outputting data"""


def compare(file1, file2):
    """ Compares two Neverwinter Nights ascii models """

    print("Comparing file: %s with %s" % (os.path.basename(file1), os.path.basename(file2)))
    mdl1 = Model()
    mdl2 = Model()

    mdl1.from_file(file1, True)
    mdl2.from_file(file2, True)

    #compare the geometry nodes
    for node1 in mdl1.geometry.nodes:
        for node2 in mdl2.geometry.nodes:
            if node1.name == node2.name:
                if node1.type != node2.type:
                    print("Differing node types; node %s\tmdl1: %s\tmdl2: %s" %
                           (node1.name, node1.type, node2, type))
                for name, prop in node1.properties.items():
                    if node2[name] != node1[name]:
                        print("Property %s differs\tmdl1: %s\tmdl2: %s" %
                              (name, str(node2[name]), str(node1[name])))
                break


class Model(object):
    """ The root class for all Neverwinter Nights models.

            The class is the basic container for the model.
    """

    def __init__(self, name="", **kwargs):
        self.name = name

        self.supermodel = ""
        self.classification = ""
        self.setanimationscale = 1

        self.geometry = Geometry(self.name)
        self.animations = []

    def new_geometry_node(self, type, name):
        """ Creates and returns a new geometry node  """
        return self.geometry.new_node(type, name)

    def new_animation(self, name):
        """ Creates and returns a new empty animation """
        animation = Animation(name, self.name)
        self.animations.append(animation)
        return animation

    def from_file(self, filename, ascii=True):
        """ Loads a model from a ascii mdl file.
        """
        if ascii:
            try:
                model_file = open(filename)

            except:
                pass

            else:
                model_data = model_file.readlines()
                model_file.close()

                #remove comments, keeping empty lines
                tmp_data = []

                for line in model_data:
                    comment_index = line.find('#')
                    if comment_index >= 0:
                        line = line[0:comment_index]

                    tmp_data.append(line)

                model_data = tmp_data
                #done removing comments

                #tokenizes and removes newlines
                model_data = [line.rstrip().split() for line in model_data]

                self.model_data = model_data

                line_count = 0

                while model_data:
                    current_line = model_data.pop(0)
                    line_count += 1

                    if "donemodel" in current_line:
                        break

                    if not current_line:  # skip empty lines
                        continue

                    first_token = current_line[0].lower()

                    if first_token == 'newmodel':
                        self.name = current_line[1]

                    elif first_token == 'setsupermodel':
                        self.supermodel = current_line[2]

                    elif first_token == 'classification':
                        self.classification = str(current_line[1]).lower()

                    elif first_token == 'setanimationscale':
                        self.setanimationscale = current_line[1]

                    elif first_token == 'beginmodelgeom':
                        geom_name = current_line[1]
                        self.geometry.name = geom_name
                        self.geometry.from_file(model_data)

                    elif first_token == 'newanim':
                        anim_name = current_line[1]
                        model_name = current_line[2]

                        new_anim = Animation(anim_name, model_name)
                        new_anim.from_file(model_data)
                        self.animations.append(new_anim)

        else:
            print("Binary mdl-files not supported")

    def __str__(self):
        out_string = ""

        out_string += "newmodel %s\n" % self.name
        out_string += "setsupermodel %s %s\n" % (self.name, self.supermodel)
        out_string += "classification %s\n" % self.classification
        out_string += "setanimationscale %s\n" % self.setanimationscale

        out_string += str(self.geometry) + "\n"

        out_string += "\n".join([str(animation) for animation in self.animations])

        out_string += "\ndonemodel %s\n" % self.name

        return out_string


class Geometry:
    """ Basic container class for the models geometry """

    def __init__(self, name):
        self.name = name
        self.nodes = []

    def from_file(self, model_data):
        """ Read the geometry from the list of lists `model_data`.

                Creates nodes as they are encountered and stops when it reaches
                a line with the tolen 'endmodelgeom'

        """

        while model_data:
            current_line = model_data.pop(0)

            if "endmodelgeom" in current_line:
                break

            if not current_line:  # skip empty lines
                current_line = model_data.pop(0)
                continue

            if current_line[0] == "node":
                node_type = current_line[1]
                node_name = current_line[2]
                node = Node(node_name, node_type)

                node.from_file(model_data)
                self.nodes.append(node)

    def new_node(self, node_type, name):
        """ Create and return a new geometry node """
        node = Node(name, node_type)
        self.nodes.append(node)
        return node

    def output_geometry(self):
        yield "beginmodelgeom %s" % self.name
        for node in self.nodes:
            yield str(node)
        yield "endmodelgeom %s" % self.name

    def __str__(self):
        return "\n".join([line for line in self.output_geometry()])


class Node:
    """ The base class for all nodes """

    def __init__(self, name, type):
        self.name = name
        self.type = type
        props = node_props.GeometryNodeProperties.get_node_properties(self.type)
        self.properties = {}

        for prop in props:
            self.properties[prop.name] = copy.copy(prop)

    def __getitem__(self, key):
        if key in self.properties:
            return self.properties[key].value
        else:
            raise KeyError

    def __setitem__(self, key, value):
        if key in self.properties:
            prop = self.properties[key]
            prop.update_value(value)
        else:
            raise KeyError

    def __iter__(self):
        return self.properties.__iter__()

    def keys(self):
        return self.properties.keys()

    def items(self):
        return self.properties.items()

    def from_file(self, model_data):
        while model_data:
            current_line = model_data.pop(0)

            if "endnode" in current_line:
                break

            if not current_line:  # skip empty lines
                continue

            if current_line[0] == "setfillumcolor":
                current_line[0] = "selfillumcolor"

            if current_line[0] in self.properties:
                self.properties[current_line[0]].read_value(current_line, model_data)

    def get_prop_value(self, property):
        if property not in self.properties:
            return None
        #print("get_prop_value: %s, value: %s" % (property, self.properties[property].value))
        return self.properties[property].value

    def output_node(self):
        # We get the properties list from the GeometryNodeProperties to
        # produce the output in the correct order
        props = node_props.GeometryNodeProperties.get_node_properties(self.type)
        yield "node %s %s" % (self.type, self.name)
        for property in props:
            if property.name in self.properties:
                if self.properties[property.name].value_written:
                    yield str(self.properties[property.name])
        yield "endnode"

    def __str__(self):
        return "\n".join([line for line in self.output_node()])

### Animation classes ###


class Animation:
    def __init__(self, name, mdl_name):
        self.name = name
        self.mdl_name = mdl_name
        self.length = 0
        self.transtime = 0
        self.animroot = ""
        self.nodes = []
        self.events = []

    def new_node(self, node_type, name):
        animation_node = AnimationNode(name, node_type)
        self.nodes.append(animation_node)
        return animation_node

    def from_file(self, model_data):
        while model_data:
            current_line = model_data.pop(0)

            if "doneanim" in current_line:
                break

            if not current_line:  # skip empty lines
                current_line = model_data.pop(0)
                continue

            if current_line[0] == "length":
                self.length = float(current_line[1])

            elif current_line[0] == "transtime":
                self.transtime = float(current_line[1])

            elif current_line[0] == "animroot":
                self.animroot = current_line[1]

            elif current_line[0] == "event":
                self.events.append((float(current_line[1]), current_line[2]))

            elif current_line[0] == "node":
                node_type = current_line[1]
                node_name = current_line[2]
                node = AnimationNode(node_name, node_type)

                node.from_file(model_data)
                self.nodes.append(node)

    def output_animation(self):
        yield "newanim %s %s" % (self.name, self.mdl_name)
        yield " " * TAB_WIDTH + "length %s" % str(self.length)
        yield " " * TAB_WIDTH + "transtime %s" % str(self.transtime)
        yield " " * TAB_WIDTH + "animroot %s" % self.animroot
        for time, event in self.events:
            yield " " * TAB_WIDTH + "event %.9g %s" % (time, event)
        for node in self.nodes:
            yield str(node)
        yield "doneanim %s %s" % (self.name, self.mdl_name)

    def __str__(self):
        return "\n".join([line for line in self.output_animation()])


class AnimationNode(Node):
    def __init__(self, name, node_type):

        self.name = name
        self.type = node_type
        props = node_props.AnimationNodeProperties.get_node_properties(self.type)
        self.properties = {}

        for prop in props:
            self.properties[prop.name] = copy.copy(prop)

    def output_node(self):
        # We get the properties list from the GeometryNodeProperties to
        # produce the output in the correct order
        props = node_props.AnimationNodeProperties.get_node_properties(self.type)
        yield "node %s %s" % (self.type, self.name)
        for property in props:
            if property.name in self.properties:
                if self.properties[property.name].value_written:
                    yield str(self.properties[property.name])
        yield "endnode"


if __name__ == "__main__":
    mdl = Model()
    mdl.from_file("c_allip.mdl")

    print(mdl)
    #import sys
    #argv = sys.argv
    #compare(*argv[1:3])
    #compare("c_allip.mdl", "untitled.mdl")
