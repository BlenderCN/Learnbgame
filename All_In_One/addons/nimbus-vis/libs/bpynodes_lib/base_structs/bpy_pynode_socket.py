# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber


:synopsis:
    Base socket class definition, methods and functions
    Currently unused, but module was included to be later expanded and implemented

:description:
    This module contains the Blender Socket class definition. 
    The class has a set of of both private and public methods.
    Private methods generally are not overwritten in any subclasses and are used for
     utility purposes
    Most public methods may be overwritten in subclasses and are listed under the 
    docstring heading. 
    Class Properties also provided for convenience for accessing useful socket parameters
    and calling functions to return processed values.

:applications:
    Blender 3D

:see_also:
    ./base_node.py

:license:
    see LICENSE.txt.md

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
from collections import defaultdict
from ..utils.io import IO

try:
    import bpy
    from bpy.props import *
except ImportError:
    IO.info("Unable to import bpy module. Setting bpy to None for non-blender environment")
    bpy = None

socket_color_override = dict()
alt_socket_ids = defaultdict(list)


# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#
def to_socket_id(socket):
    """ Returns an ID lookup for a socket"""
    node = socket.node
    return ((node.id_data.name, node.name), socket.is_output, socket.identifier)

def get_node_tree(socket):
    """Returns the node tree this socket's node is in"""
    return socket.node.id_data

def is_socket_unlinked(socket):
    return not socket.is_linked

def get_socket_index(socket, node=None):
    """Returns an index of the current socket"""
    if node is None: node = socket.node
    if socket.is_output:
        return list(node.outputs).index(socket)
    return list(node.inputs).index(socket)

def get_node_link(socket):
    nlink = ''
    node_tree = socket.get_node_tree()
    link_list = node_tree.links
    for nodelink in link_list:
        if nodelink.to_socket.identifier == socket.identifier:
            socket_index = nodelink.from_socket.get_socket_index
            nlink = (nodelink.from_node.name,
                     nodelink.from_socket.identifier,
                     socket_index())
    return nlink


# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#
class CustomBlenderSocket(object):
    """Base BlenderSocket Class. All other sockets Subclass this."""

    # Class Variables that all subclasses inherit
    text = StringProperty(default="Socket Name")
    display_property = BoolProperty(default=True)

    @classmethod
    def has_property(cls):
        """Determines if the socket class has a property to draw."""
        return hasattr(cls, "draw_property")

    '''UI and Drawing'''

    def draw(self, context, layout, node, text):
        """Draws the Socket."""
        row = layout.row(align=True)
        if self.is_input_socket and self.is_socket_unlinked:
            # Input socket, Unlinked, draw the socket
            self.draw_socket(row, self.text, node, self.display_property)
        else:
            # Output Socket, just label the socket
            if self.is_output_socket: row.alignment = "RIGHT"
            self.draw_socket(row, self.text, node, self.display_property)

    def draw_socket(self, layout, text, node, display_prop):
        """Socket draw helper function."""
        if display_prop is False:
            # Only display the text for this socket
            layout.label(text)
        elif display_prop is True:
            # Check for draw property function and display the property
            if self.has_property():
                self.draw_property(layout, text, node)
            # If draw_property() method is undefined, simply draw the text
            else:
                layout.label(text)

    '''Define these functions in subclass'''

    # def draw_color(self, context, node):
    #     raise NotImplementedError("All sockets have to define a draw_color method")

    def draw_property(self, layout, text, node):
        pass

    '''Override in Subclass'''

    @classmethod
    def get_default_value(cls):
        """Gets the default value of the socket."""
        raise NotImplementedError("All sockets have to define a get_default_value method")

    @classmethod
    def correct_value(cls, value):
        """
        Returns a correct value tuple.
        :param value: the socket's value
        :rtype: correct_type = (value, 0)
        :rtype: correctable_type = (correced_value, 1)
        :rtype: uncorrectable_type = (default_value, 2)
        :return: rtype
        """
        raise NotImplementedError("All sockets have to define a correct_value method")

    @classmethod
    def get_conversion_code(cls, data_type):
        """Method to convert the value of the socket to a different type."""
        return None

    def set_property(self, data):
        """Set a socket property."""
        pass

    def get_property(self):
        """Get a socket property."""
        pass

    '''Link and Remove Utilities'''

    def link_with(self, socket):
        """Link to another socket."""
        if self.is_output_socket:
            return self.node_tree.links.new(socket, self)
        else:
            return self.node_tree.links.new(self, socket)

    def remove(self):
        """Remove the socket."""
        self.free()
        node = self.node
        node._remove_socket(self)

    def remove_links(self):
        """Remove any links to this socket."""
        removed_link = False
        if self.is_linked:
            tree = self.node_tree
            for link in self.links:
                tree.links.remove(link)
                removed_link = True
        return removed_link

    # def is_linked_to_type(self, data_type):
    #     return any(socket.data_type == data_type for socket in self.linkedSockets)

    '''Socket Class Properties'''

    @property
    def node_tree(self):
        """The NodeTree of the Node that this socket belongs to."""
        return self.node.id_data

    @property
    def group_node_tree(self):
        """The NodeGroup NodeTree this socket belongs to."""
        return self.id_data

    @property
    def node_link(self):
        # link = tuple(node, socket, index)
        node_tree = self.node_tree
        link_list = node_tree.links
        for nodelink in link_list:
            if nodelink.from_socket.identifier == self.identifier:
                link = (nodelink.to_node.name,
                        nodelink.to_socket.identifier,
                        nodelink.to_socket.socket_index)
                return link

    @property
    def socket_index(self):
        return get_socket_index(self)

    @property
    def is_output_socket(self):
        """Check if this socket is an output socket."""
        return self.is_output

    @property
    def is_input_socket(self):
        """Check if this socket is an input socket."""
        return not self.is_output

    @property
    def is_socket_linked(self):
        """Check if this socket is linked to another socket."""
        return self.is_linked

    @property
    def is_socket_unlinked(self):
        """Check if this socket is unlinked to another socket."""
        return not self.is_linked

    @property
    def sockets(self):
        """Returns all sockets next to this one (all inputs or outputs)."""
        return self.node.outputs if self.is_output else self.node.inputs

    '''Misc methods and properties'''

    def free(self):
        """Method called to cleanup this socket upon removal."""
        try:
            del alt_socket_ids[self.get_temp_id()]
        except:
            pass
        try:
            del socket_color_override[self.get_temp_id()]
        except:
            pass

    @property
    def alt_ids(self):
        """Returns an alternate socket identifiers."""
        return alt_socket_ids[self.get_temp_id()]

    @alt_ids.setter
    def alt_ids(self, value):
        """Sets alternate socket identifier."""
        alt_socket_ids[self.get_temp_id()] = value

    def get_temp_id(self):
        """Returns a temporary identifier."""
        return str(hash(self)) + self.identifier


def register():
    """Blender's register. Extends bpy.types classes with new properties and funcs."""
    bpy.types.NodeSocket.to_socket_id = to_socket_id
    bpy.types.NodeSocket.get_node_tree = get_node_tree
    bpy.types.NodeSocket.get_socket_index = get_socket_index
    bpy.types.NodeSocket.is_socket_unlinked = is_socket_unlinked
    bpy.types.NodeSocket.socket_id = StringProperty()
    bpy.types.NodeSocket.get_linked_node = get_node_link


def unregister():
    """Blender's unregister. Removes extended funcs and props from bpy.types classes."""
    del bpy.types.NodeSocket.to_socket_id
    del bpy.types.NodeSocket.get_socket_index
    del bpy.types.NodeSocket.get_node_tree
    del bpy.types.NodeSocket.is_socket_unlinked
    del bpy.types.NodeSocket.socket_id
    del bpy.types.NodeSocket.get_linked_node
