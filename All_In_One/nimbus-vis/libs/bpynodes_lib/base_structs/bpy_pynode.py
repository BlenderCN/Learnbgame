# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber

:synopsis:
    Base node class definition, methods and functions to be used in a Custom Node Tree.
    Currently unused, but module was included to be later expanded and implemented

:description:
    This module contains Base Python Node class definitions. 
    The classes have a set of of both private and public methods.
    Private methods generally are not overwritten in any subclasses and are used for
     utility purposes
    Most public methods may be overwritten in subclasses and are listed under the 
    docstring heading. 
    Class Properties also provided for convenience for accessing useful node parameters
    and calling functions to return processed values. 

:applications:
    Blender 3D

:see_also:
   ./bpy_pynode_socket.py

:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#

import random
from ..utils.dynamic_props import node_parameter
from ..utils.io import IO
try:
    import bpy
    from bpy.props import *
except ImportError:
    IO.info("Unable to import bpy module. Setting bpy to None for non-blender environment")
    bpy = None

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

def create_identifier():
    """Creates a random identifier string."""
    identifierLength = 15
    characters = "abcdefghijklmnopqrstuvwxyz" + "0123456789"
    choice = random.SystemRandom().choice
    return "_" + ''.join(choice(characters) for _ in range(identifierLength))


@node_parameter
def create_parameter(value, **kwargs):
    """Creates and registers a dynamic Blender Property property group using type()"""
    return value


def is_custom_cycles_node(node):
    """Determines if the passed in node is a Custom Cycles Node."""
    return hasattr(node, "_is_custom_cycles_node")


def is_output_node(node):
    """Determines if the passed in node is an output node by looking for output sockets"""
    return not len(node.outputs)


def get_node_tree(node):
    """Gets the NodeTree(ID) Datablock from Blender that the passed in Node belongs to."""
    return node.id_data


def get_sockets(node):
    """Returns a joined list of input and output sockets for the passed in node"""
    return list(node.inputs) + list(node.outputs)

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

class CustomBlenderNode(object):

    # Class Properties
    # Width, Max/Min
    bl_width_min = 40
    bl_width_max = 5000
    # Blender Properties
    identifier = StringProperty(name="Identifier", default="")
    active_input = IntProperty()
    active_output = IntProperty()
    _is_output_node = False

    '''Required functions for a Blender Node. Do not override in subclass'''

    # @classmethod
    # def poll(cls, ntree):
    #     """Determines if this node can be created in the current node tree."""
    #     return ntree.bl_idname == 'mx_MaterialXNodeTree'

    @classmethod
    def iter_node_bpy_types(cls):
        try:
            from nodeitems_utils import node_categories_iter
            for cat in node_categories_iter(context=None):
                if '_NEW_' in cat.identifier:
                    # for node_item in cat.items(context=None):
                    yield from cat.items(context=None)
        except ImportError:
            IO.error("Unable to import nodeitems_utils. Make sure you are in a BPY environment")


    def init(self, context):
        """Initialize a new instance of this node. Sets identifier to a random string."""
        self.identifier = create_identifier()
        self.setup()
        self.create()


    def update(self):
        """Update on editor changes. DO NOT USE"""
        pass


    def free(self):
        """Clean up node on removal"""
        self._clear()
        self.delete()


    def copy(self, source_node):
        """Initialize a new instance of this node from an existing node."""
        self.identifier = create_identifier()
        self.duplicate(source_node)


    def draw_buttons(self, context, layout):
        """Draws buttons on the node"""
        self.draw(layout)


    def draw_label(self):
        """Draws the node label. Should just return the bl_label set in subclass"""
        return self.bl_label


    '''Functions subclasses can override'''


    def duplicate(self, source_node):
        """Called when duplicating the node"""
        pass


    def edit(self):
        """Called when the node is edited"""
        pass


    def save(self):
        """Function to handle saving node properties when file is saved"""
        pass


    def create(self):
        """Function to create this node, called by init()"""
        pass


    def setup(self):
        """Function to setup this node, called by init(), before create()"""
        pass


    def remove(self):
        """Function to remove this node from it's node tree"""
        self.node_tree.nodes.remove(self)


    def delete(self):
        """Helper function for after this node has been deleted/removed"""
        pass


    def draw(self, layout):
        """Draw function"""
        pass


    def reset(self):
        pass

    '''Private functions. Here for convenience when subclassing'''

    def _value_set(self, obj, path, value):
        if '.' in path:
            path_prop, path_attr = path.rsplit('.', 1)
            prop = obj.path_resolve(path_prop)
        else:
            prop = obj
            path_attr = path
        setattr(prop, path_attr, value)


    def _new_input(self, type, name, identifier=None, **kwargs):
        """
        Create's a new input socket.
        :param type: socket data type
        :type type: any socket data type
        :param name: name of socket
        :type name: str
        :param identifier: identifier of the socket, used in code
        :type identifier: str
        :param kwargs: keyword arguments for special socket properties
        :return: socket
        """
        if identifier is None: identifier = name
        socket = self.inputs.new(type, name, identifier)
        self._set_socket_properties(socket, kwargs)
        return socket


    def _new_output(self, type, name, identifier=None, **kwargs):
        """
        Create's a new output socket.
        :param type: socket data type
        :type type: any socket data type
        :param name: name of socket
        :type name: str
        :param identifier: identifier of the socket, used in code
        :type identifier: str
        :param kwargs: keyword arguments for special socket properties
        :return: socket
        """
        if identifier is None: identifier = name
        socket = self.outputs.new(type, name, identifier)
        self._set_socket_properties(socket, kwargs)
        return socket


    def _clear(self):
        """Clears all data on this node."""
        self._clear_sockets()


    def _clear_sockets(self):
        """Clears all input and output sockets"""
        self._clear_inputs()
        self._clear_outputs()


    def _clear_inputs(self):
        """Clears all input sockets. Calls socket's free()
            and then removes all input sockets with inputs.clear()."""
        for socket in self.inputs:
            if hasattr(socket, 'free'):
                socket.free()
        self.inputs.clear()


    def _clear_outputs(self):
        """Clears all output sockets. Calls socket's free()
            and then removes all output sockets with outputs.clear()."""
        for socket in self.outputs:
            if hasattr(socket, 'free'):
                socket.free()
        self.outputs.clear()


    def _remove_socket(self, socket):
        """Removes any node socket by checking it's index and decrementing
         the value of the of the node's active input or output socket."""
        index = socket.get_index(self)
        if socket.is_output_socket:
            if index < self.active_output: self.active_output -= 1
        else:
            if index < self.active_input: self.active_input -= 1
        socket.sockets.remove(socket)


    def _set_socket_properties(self, socket, properties):
        """
        Function to set the properties of a node's sockets. 
        :param socket: bpy.types.NodeSocket()
        :param properties: dict
        :return: 
        """
        for key, value in properties.items():
            if not hasattr(socket, key):
                continue
            if key == 'link_limit':
                if hasattr(socket, '_is_list'):
                    setattr(socket, key, value)
            else:
                setattr(socket, key, value)

    '''Node Properties. Do not override unless absolutely necessary'''

    # @property
    # def node_tree(self):
    #     """Returrns the ID Datablock of this node's current NodeTree."""
    #     return self.id_data
    #
    # @node_tree.setter
    # def node_tree(self, bpy_data_node_tree):
    #     pass
    def _get_connected_node(self, socket, execute=False):
        IO.info("Getting node connected to %s" % self.name)
        node_tree = self.get_node_tree()
        for link in node_tree.links:
            if link.to_socket.name == socket.name:
                from_node, from_socket = link.from_node, link.from_socket
                if execute is True:
                    node_tree.nodes.active = from_node
                    from_node.execute()
                    node_tree.nodes.active = self
                return from_node, from_socket

    @property
    def inputs_by_id(self):
        """Returns all identifiers for this node's input sockets."""
        return {socket.identifier: socket for socket in self.inputs}


    @property
    def outputs_by_id(self):
        """Returns all identifiers for this node's output sockets."""
        return {socket.identifier: socket for socket in self.outputs}


    @property
    def sockets(self):
        """Returns a joined list of this node's input+output sockets."""
        return list(self.inputs) + list(self.outputs)


    @property
    def active_input_socket(self):
        """Returns the currently active input socket's index."""
        if len(self.inputs) == 0: return None
        return self.inputs[self.active_input]


    @property
    def active_output_socket(self):
        """Returns the currently active output socket's index."""
        if len(self.outputs) == 0: return None
        return self.outputs[self.active_output]


class GroupNodeStruct(object):
    def __init__(self, node_list, **kwargs):
        self.name = kwargs.setdefault('name', None)
        self.identifier = kwargs.setdefault("identifier", None)
        self.node_list = node_list
        self.node_map = []
        self.socket_interface = None


class CustomBlenderNodeGroup(CustomBlenderNode):
    """
    Custom Blender Node Group to be implemented in various NodeTrees.
    Sublcasses CustomBlenderNode for access to typical node methods/attributes
    Defines and Extends access to Node Tree information
    """

    _node_tree = None
    _node_tree_name = None
    _node_tree_type = None
    _node_tree_ext = None
    _node_list = []
    _socket_interface = []
    _node_map = []


    def _new_input(self, type, name, **kwargs):
        """
        Create's a new input socket.
        :param type: socket data type
        :type type: any socket data type
        :param name: name of socket
        :type name: str
        :param kwargs: keyword arguments for special socket properties
        :return: socket
        """
        socket = self.inputs.new(type, name)
        self._set_socket_properties(socket, kwargs)
        return socket


    def _new_output(self, type, name, **kwargs):
        """
        Create's a new output socket.
        :param type: socket data type
        :type type: any socket data type
        :param name: name of socket
        :type name: str
        :param kwargs: keyword arguments for special socket properties
        :return: socket
        """
        socket = self.outputs.new(type, name)
        self._set_socket_properties(socket, kwargs)
        return socket


    @property
    def node_list(self):
        return self._node_list

    @node_list.setter
    def node_list(self, node_list):
        self._node_list = node_list


    @property
    def socket_interface(self):
        return self._socket_interface

    @socket_interface.setter
    def socket_interface(self, interface):
        self._socket_interface = interface


    @property
    def node_map(self):
        return self._node_map

    @node_map.setter
    def node_map(self, node_map):
        self._node_map = node_map


    @property
    def node_tree(self):
        """
        The Node Tree in BlendData. This object is either looked up by name in BlendData
        or created in BlendData when CustomBlenderNodeGroup.node_tree is accessed.

        :return: Blender Node Tree
        :rtype: bpy.types.NodeTree(ID)
        """

        node_tree_name = self.node_tree_name  # check the node tree name
        node_tree_type = self.node_tree_type  # check the node tree type
        if node_tree_name is not None:
            # Lookup or Create the Node Tree
            if bpy.data.node_groups.find(node_tree_name) != -1:  # node tree exists
                IO.debug("@node_tree called. Found the node tree.")
                return bpy.data.node_groups[str(node_tree_name)]  # return from BlendData
            else:  # create & return Node Tree
                IO.debug("@node_tree called. Creating new node Tree")
                return bpy.data.node_groups.new(str(node_tree_name), str(node_tree_type))
        else:
            # return None
            raise LookupError(
                "Private attribute '_node_tree_name' is undefined or NoneType.\n"
                "Unable to lookup or create Node Tree in BlendData.\n"
            )

    @node_tree.setter
    def node_tree(self, bpy_data_node_tree):
        """
        Set _node_tree to a Blender Node Tree
        :param bpy_data_node_tree: bpy.types.NodeTree(ID)
        """
        self._node_tree = bpy_data_node_tree


    @property
    def node_tree_name(self):
        """The Node Tree Name in the pattern '_node_tree_name._node_tree_extension'. """
        if self._node_tree_name is None:
            raise AttributeError("Private _node_tree_name attribute is unset or NoneType")
        elif self._node_tree_ext is None:
            raise AttributeError("Private _node_tree_ext attribute is unset or NoneType")
        return "_%s%s" % (str(self._node_tree_name), self._node_tree_ext)

    @node_tree_name.setter
    def node_tree_name(self, name):
        """Set the _node_tree_name private class attribute to name argument"""
        self._node_tree_name = name


    @property
    def node_tree_type(self):
        """The Node Tree Type private class attribute"""
        if self._node_tree_type is None:
            raise AttributeError("Private _node_tree_type attribute is unset or NoneType")
        return self._node_tree_type

    @node_tree_type.setter
    def node_tree_type(self, tree_type):
        """Set the _node_tree_type private class attribute to tree_type"""
        self._node_tree_type = tree_type


    @property
    def node_tree_ext(self):
        """The Node Tree Extension string: i.e.'.mdl'."""
        if self._node_tree_ext is None:
            raise AttributeError("Private _node_tree_ext attribute is unset or NoneType")
        return "%s" % str(self._node_tree_ext)

    @node_tree_ext.setter
    def node_tree_ext(self, ext_type):
        """Set the Node Tree Extension string to ext_type"""
        self._node_tree_ext = ext_type


class CustomCyclesGroup(CustomBlenderNodeGroup):
    _is_custom_cycles_node = True


    @classmethod
    def poll(cls, ntree):
        """Determines if this node can be created in the current node tree."""
        return ntree.bl_idname == 'ShaderNodeTree'


    # def init(self, context):
    #     self.create()


    def create(self):
        """
        Setup Node Tree for this Group
        :return: 
        """
        pass


    def add_node(self, node_type, attrs):
        node = self.node_tree.nodes.new(node_type)
        if attrs:
            for attr in attrs:
                self._value_set(node, attr, attrs[attr])
        return node


    def get_node(self, node_name):
        if self.node_tree.nodes.find(node_name) > -1:
            return self.node_tree.nodes[node_name]
        return None


    def add_socket(self, in_out, socket_type, name):
        # for now duplicated socket names are not allowed

        if in_out == 'Output':
            if self.node_tree.nodes['group_output'].inputs.find(name) == -1:
                socket = self.node_tree.outputs.new(socket_type, name)
        elif in_out == 'Input':
            if self.node_tree.nodes['group_input'].outputs.find(name) == -1:
                socket = self.node_tree.inputs.new(socket_type, name)


    def inner_link(self, in_socket, out_socket):
        IS = self.node_tree.path_resolve(in_socket)
        OS = self.node_tree.path_resolve(out_socket)
        self.node_tree.links.new(IS, OS)


    def free(self):
        """Clean up node on removal"""
        self._clear()
        self.reset()
        self.delete()


    def delete(self):
        IO.info("Deleting Node")


    def _clear(self):
        """Clears all data on this node."""
        IO.info("Clearing Sockets and Nodes")
        self._clear_sockets()
        self._clear_nodes()


    def _clear_nodes(self):
        node_tree = self.node_tree
        node_tree.nodes.clear()


    def _clear_sockets(self):
        """Clears all input and output sockets"""
        self._clear_inputs()
        self._clear_outputs()


    def _clear_inputs(self):
        """Clears all input sockets. Calls socket's free()
            and then removes all input sockets with inputs.clear()."""
        for socket in self.inputs:
            if hasattr(socket, 'free'):
                socket.free()
        self.inputs.clear()
        node_tree = self.node_tree
        node_tree.inputs.clear()


    def _clear_outputs(self):
        """Clears all output sockets. Calls socket's free()
            and then removes all output sockets with outputs.clear()."""
        for socket in self.outputs:
            if hasattr(socket, 'free'):
                socket.free()
        self.outputs.clear()
        node_tree = self.node_tree
        node_tree.outputs.clear()



# ---------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------- REGISTER --#


def register():
    """Blender's register function. Injects methods and classes into Blender"""

    bpy.types.Node.is_custom_cycles_node = BoolProperty(
        name="Custom Cycles Node",
        get=is_custom_cycles_node
    )
    bpy.types.Node.is_output_node = BoolProperty(
        name="Output Node",
        get=is_output_node
    )

    bpy.types.Node.get_node_tree = get_node_tree
    bpy.types.Node.get_sockets = get_sockets


def unregister():
    """Blender's unregister function. Removes methods and classes from Blender"""

    del bpy.types.Node.get_sockets
    del bpy.types.Node.get_node_tree
    del bpy.types.Node.is_output_node
    del bpy.types.Node.is_custom_cycles_node
