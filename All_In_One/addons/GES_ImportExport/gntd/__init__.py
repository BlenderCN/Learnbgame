import xml.etree.cElementTree as ET
import ast
import sys

FLOAT_DIGITS = 6


class VectorBase(object):
    def __init__(self, size, *arg):  # size is the size of the array, formed  from *arg
        arg_length = len(arg)
        self.__type = "unknown"
        if arg_length == 0:
            self.__data = tuple([0.0 for i in range(size)])
        elif arg_length == 1:
            self.__data = tuple([arg[0] for i in range(size)])
        else:
            self.__data = tuple([arg[i] if i < len(arg) else 0.0 for i in range(size)])

    def _float_to_string(self, value):
        return str(round(value, FLOAT_DIGITS))

    def set_value(self, index, value):
        if index < len(self.__data):
            a = [v for v in self.__data]
            a[index] = value
            self.__data = tuple(a)

    def get_raw(self):
        return self.__data

    def get_type(self):
        return self.__type


class VectorArray(object):
    def __init__(self, vec_array):
        self.__type = "vectorArray"
        self.__length = len(vec_array)
        self.__data = vec_array

    def _float_to_string(self, value):
        return str(round(value, FLOAT_DIGITS))

    def get_raw(self):
        return self.__data

    def get_type(self):
        return self.__type

    def get_data_string(self):  # vectors_count v1[0] v1[1] v1[2] v2[0] v2[1] v2[3] ...
        str_array = []
        str_array.append(str(self.__length))
        for v in self.__data:
            if isinstance(v, float):
                str_array.append(self._float_to_string(v))
            else:
                v_data = v.get_raw()
                for d in v_data:
                    str_array.append(self._float_to_string(d))
        return " ".join(str_array)


class Closure(object):
    def __init__(self):
        self.__type = "closure"
        self.__data = "empty"

    def get_raw(self):
        return self.__data

    def get_type(self):
        return self.__type


class Color3(VectorBase):
    def __init__(self, *arg):
        super(Color3, self).__init__(3, *arg)
        self.__type = "color3"

    def get_data_string(self):
        r = self.get_raw()
        str_array = [self._float_to_string(r[0]), self._float_to_string(r[1]), self._float_to_string(r[2])]
        return " ".join(str_array)


class Color4(VectorBase):
    def __init__(self, *arg):
        super(Color4, self).__init__(4, *arg)
        if len(arg) < 4:
            self.set_value(3, 1.0)
        self.__type = "color4"

    def get_data_string(self):
        r = self.get_raw()
        str_array = [self._float_to_string(r[0]), self._float_to_string(r[1]), self._float_to_string(r[2]), self._float_to_string(r[3])]
        return " ".join(str_array)


class Normal(VectorBase):
    def __init__(self, *arg):
        super(Normal, self).__init__(3, *arg)
        self.__type = "vector3"

    def get_data_string(self):
        r = self.get_raw()
        str_array = [self._float_to_string(r[0]), self._float_to_string(r[1]), self._float_to_string(r[2])]
        return " ".join(str_array)


class Vector3(VectorBase):
    def __init__(self, *arg):
        super(Vector3, self).__init__(3, *arg)
        self.__type = "vector3"

    def get_data_string(self):
        r = self.get_raw()
        str_array = [self._float_to_string(r[0]), self._float_to_string(r[1]), self._float_to_string(r[2])]
        return " ".join(str_array)


class Vector2(VectorBase):
    def __init__(self, *arg):
        super(Vector2, self).__init__(2, *arg)
        self.__type = "vector2"

    def get_data_string(self):
        r = self.get_raw()
        str_array = [self._float_to_string(r[0]), self._float_to_string(r[1])]
        return " ".join(str_array)


class NodeTree(object):
    class LoggerHelper(object):
        def __init__(self):
            pass

        def log(self, message):
            print(message)

    class Node(object):
        class Output(object):
            def __init__(self, name, type, parent_node):
                self.__name = name
                self.__type = type
                self.__parent = parent_node

            def get_name(self):
                return self.__name

            def get_type(self):
                return self.__type

            def raw_data(self):
                return (self.get_name(), self.get_type(), self.__parent.get_name())

        class Input(object):
            def __init__(self, name, type, value, parent_node):
                self.__name = name
                self.__type = type
                self.__value = value
                self.__parent = parent_node

            def get_name(self):
                return self.__name

            def get_type(self):
                return self.__type

            def get_value(self, as_string=False):
                if self.get_type() == "int":
                    return str(self.__value) if as_string else self.__value
                elif self.get_type() == "float":
                    return str(round(self.__value, FLOAT_DIGITS)) if as_string else self.__value
                elif self.get_type() == "string":
                    return self.__value
                elif self.get_type() == "bool":
                    return ("true" if self.__value else "false") if as_string else (self.__value)
                else:
                    if self.get_type() == "color4":
                        return self.__value.get_data_string() if as_string else self.__value.get_raw()
                    elif self.get_type() == "vector3":
                        return self.__value.get_data_string() if as_string else self.__value.get_raw()
                    elif self.get_type() == "color3":
                        return self.__value.get_data_string() if as_string else self.__value.get_raw()
                    elif self.get_type() == "vector2":
                        return self.__value.get_data_string() if as_string else self.__value.get_raw()
                    elif self.get_type() == "closure":
                        return self.__value.get_raw()
                    elif self.get_type() == "vectorArray":
                        return self.__value.get_data_string() if as_string else self.__value.get_raw()
                    else:
                        return "none" if as_string else None

            def raw_data(self):
                return (self.get_name(), self.get_type(), self.get_value(), self.__parent.get_name())

        def __init__(self, type, name, label, parent_tree):
            self.__logger = NodeTree.LoggerHelper()
            self.__type = type
            self.__name = name
            self.__label = label
            self.__inputs = []
            self.__outputs = []
            self.__parameters = []  # this is the tuple (name, type, value)
            self.__input_name_to_index = {}  # use this for finding element index in the array with the given name
            self.__output_name_to_index = {}
            self.__parameter_name_to_index = {}
            self.__is_elementary = True
            self.__node_tree = None
            self.__parent_tree = parent_tree

        def get_name(self):  # return the name of the node
            return self.__name

        def get_label(self):  # label is not used for identification of the node, but only for visual text
            return self.__label

        def get_type(self):  # return the type (string) of the node (COLOR, DIFFUSE_BSDF, ...)
            return self.__type

        def is_primitive(self):
            return self.__is_elementary

        def get_subtree(self):
            if self.__is_elementary:
                return None
            else:
                return self.__node_tree

        def __is_inputs_contains_name(self, port_name):
            for i in self.__inputs:
                if i.get_name() == port_name:
                    return True
            return False

        def is_input_exist(self, input_name):
            return input_name in self.__input_name_to_index

        def is_output_exist(self, output_name):
            return output_name in self.__output_name_to_index

        def __is_outputs_contains_name(self, port_name):
            for o in self.__outputs:
                if o.get_name() == port_name:
                    return True
            return False

        def __is_parameters_contains_name(self, param_name):
            for p in self.__parameters:
                if p[0] == param_name:
                    return True
            return False

        def add_subtree(self):
            self.__is_elementary = False
            self.__node_tree = NodeTree(self)
            return self.__node_tree

        def add_input(self, port_name, input_type, default_value):  # input_type is a string ("float", "int" and so on)
            # check is the same input port name exists
            if self.__is_inputs_contains_name(port_name):
                self.__logger.log("Input port with the name " + port_name + " already exist.")
                return None
            else:
                new_input = NodeTree.Node.Input(port_name, input_type, default_value, self)
                self.__inputs.append(new_input)
                self.__input_name_to_index[port_name] = len(self.__inputs) - 1
                return new_input

        def get_input(self, input_id):
            python_version = sys.version_info.major
            if python_version == 2:
                if isinstance(input_id, basestring):
                    if input_id in self.__input_name_to_index:
                        return self.__inputs[self.__input_name_to_index[input_id]]
                    else:
                        self.__logger.log("Node " + self.get_name() + " does not contains input " + input_id)
                        return None
                elif isinstance(input_id, (int, long)):
                    if input_id < len(self.__inputs):
                        return self.__inputs[input_id]
                    else:
                        self.__logger.log("Node " + self.get_name() + " does not contains input with index " + str(input_id))
                        return None
            else:
                if isinstance(input_id, str):
                    if input_id in self.__input_name_to_index:
                        return self.__inputs[self.__input_name_to_index[input_id]]
                    else:
                        self.__logger.log("Node " + self.get_name() + " does not contains input " + input_id)
                        return None
                elif isinstance(input_id, int, long):
                    if input_id < len(self.__inputs):
                        return self.__inputs[input_id]
                    else:
                        self.__logger.log("Node " + self.get_name() + " does not contains input with index " + str(input_id))
                        return None

        def get_inputs_count(self):
            return len(self.__inputs)

        def add_output(self, port_name, output_type):
            if self.__is_outputs_contains_name(port_name):
                self.__logger.log("Output " + port_name + " already exist.")
                return None
            else:
                new_output = NodeTree.Node.Output(port_name, output_type, self)
                self.__outputs.append(new_output)
                self.__output_name_to_index[port_name] = len(self.__outputs) - 1
                return new_output

        def get_output(self, out_name):
            if out_name in self.__output_name_to_index:
                return self.__outputs[self.__output_name_to_index[out_name]]
            else:
                self.__logger.log("Node " + self.get_name() + " does not contains output " + out_name)
                return None

        def add_parameter(self, param_name, param_type, param_value):
            if self.__is_parameters_contains_name(param_name):
                self.__logger.log("Node " + self.get_name() + " already contains paramter " + param_name)
            else:
                self.__parameters.append((param_name, param_type, param_value))
                self.__parameter_name_to_index[param_name] = len(self.__parameters) - 1

        def get_parameters_count(self):
            return len(self.__parameters)

        def get_parameter(self, param_id):
            python_version = sys.version_info.major
            if python_version == 2:
                if isinstance(param_id, basestring):
                    if param_id in self.__parameter_name_to_index:
                        return self.__parameters[self.__parameter_name_to_index[param_id]]
                    else:
                        self.__logger.log("Node " + self.get_name() + " does not contains parameter " + param_id)
                        return None
                elif isinstance(param_id, (int, long)):
                    if param_id < len(self.__parameters):
                        return self.__parameters[param_id]
                    else:
                        self.__logger.log("Node " + self.get_name() + " does not contains parameter with index " + str(param_id))
                        return None
            else:
                if isinstance(param_id, str):
                    if param_id in self.__parameter_name_to_index:
                        return self.__parameters[self.__parameter_name_to_index[param_id]]
                    else:
                        self.__logger.log("Node " + self.get_name() + " does not contains parameter " + param_id)
                        return None
                elif isinstance(param_id, int):
                    if param_id < len(self.__parameters):
                        return self.__parameters[param_id]
                    else:
                        self.__logger.log("Node " + self.get_name() + " does not contains parameter with index " + str(param_id))
                        return None

        def _add_to_xml(self, root, input_to_output_dict):
            n_data = {"name": self.__name}
            if len(self.__label) > 0:
                n_data["label"] = self.__label
            node_xml = ET.SubElement(root, self.__type, n_data)

            def get_source(node, port, connections, is_from_output):
                for c in connections:
                    if is_from_output:
                        triple = c.get_output_by_input(node, port)
                    else:
                        triple = c.get_input_by_output(node, port)
                    if triple is not None:
                        return triple
                return None

            # add inputs
            for inp in self.__inputs:
                # try to find source of the input node
                key = (self.__name, inp.get_name())
                source = input_to_output_dict[key] if key in input_to_output_dict else None
                params_dict = {"port": inp.get_name(),
                               "type": inp.get_type(),
                               "default": inp.get_value(True)}
                if source is not None:
                    params_dict["source_node"] = source[0]
                    params_dict["source_port"] = source[1]
                    params_dict["source_external"] = str(source[2])
                ET.SubElement(node_xml, "input", params_dict)
            # nex outputs
            # get connections inside the node
            inner_connections_count = 0
            inner_connections = []
            if not self.__is_elementary:
                inner_connections_count = self.__node_tree.get_connections_count()
                inner_connections = [self.__node_tree.get_connection(c_index) for c_index in range(inner_connections_count)]
            for otp in self.__outputs:
                source = get_source(self.__name, otp.get_name(), inner_connections, False)
                params_dict = {"port": otp.get_name(),
                               "type": otp.get_type()}
                if source is not None and source[2] is True:
                    params_dict["source_node"] = source[0]
                    params_dict["source_port"] = source[1]
                ET.SubElement(node_xml, "output", params_dict)
            # parameters
            for param in self.__parameters:
                p_param_dict = {"name": param[0],
                                "type": param[1]}
                p_param_dict["value"] = str(param[2]) if (param[1] == "int" or param[1] == "string" or param[1] == "bool") else (str(round(param[2], FLOAT_DIGITS)) if param[1] == "float" else param[2].get_data_string())
                ET.SubElement(node_xml, "parameter", p_param_dict)
            # at last nodes if there is node_tree in this node
            if not self.__is_elementary:
                child_node_tree_section = ET.SubElement(node_xml, "node_tree")
                self.__node_tree._add_to_xml(child_node_tree_section)

    class Connection(object):
        def __init__(self, out_node, out_port_name, in_node, in_port_name, is_external=False, external_mode=0):  # mode=0 - input - to - input, mode=1 - output - to - output, 2 - pass-throw
            # for extrnal node:
            # left-input ---- right-output if the inner nod connects to right border of the compund or this is pass=throw connection
            # left-output ---- right-input if from the left is ht boundary of the compound
            self.__output_node_name = out_node.get_name()
            self.__output_port_name = out_port_name
            self.__input_node_name = in_node.get_name()
            self.__input_port_name = in_port_name
            self.__output_node = out_node
            self.__input_node = in_node
            self.__is_external = is_external
            self.__external_mode = external_mode

        def get_raw(self):
            return (self.__output_node_name, self.__output_port_name, self.__input_node_name, self.__input_port_name, self.__is_external, self.__external_mode)

        def get_output_by_input(self, input_node, input_port):
            '''Return the triple (node, port, is_external) if this connection of the form (node, port)<----->(input_node, input_port)
            in the other case return None
            '''
            if self.__input_node_name == input_node and self.__input_port_name == input_port:
                return (self.__output_node_name, self.__output_port_name, self.__is_external)
            else:
                return None

        def get_input_by_output(self, output_node, output_port):
            '''Return the pair (node, port) if this connection of the form (output_node, output_port)<------>(node, port)
            in the other case return None
            '''
            if self.__external_mode == 1 or self.__external_mode == 2:
                if self.__output_node_name == output_node and self.__output_port_name == output_port:
                    return (self.__input_node_name, self.__input_port_name, self.__is_external)
                else:
                    return None

        def _add_to_xml(self, root):
            params_dict = {"out_node": self.__output_node_name,
                           "out_port": self.__output_port_name,
                           "in_node": self.__input_node_name,
                           "in_port": self.__input_port_name}
            if self.__is_external:
                params_dict["external"] = "True"
                params_dict["external_mode"] = "Input" if self.__external_mode == 0 else ("Output" if self.__external_mode == 1 else "Passthrough")
            else:
                params_dict["external"] = "False"
            ET.SubElement(root, "connection", params_dict)

    def __init__(self, parent=None):
        self.__parent_node = parent
        self.__logger = NodeTree.LoggerHelper()
        self.__nodes = []
        self.__connections = []
        self.__node_name_to_index = {}

    def __is_nodes_contains_name(self, node_name):
        for n in self.__nodes:
            if n.get_name() == node_name:
                return True
        return False

    def get_parent_node(self):
        return self.__parent_node

    def get_nodes_count(self):
        return len(self.__nodes)

    def get_connections_count(self):
        return len(self.__connections)

    def get_connection(self, connection_index):
        if connection_index < len(self.__connections):
            return self.__connections[connection_index]
        else:
            self.__logger.log("Connections count is " + str(len(self.__connections)) + ". The index " + str(connection_index) + " is wrong")
            return None

    def is_node_exist(self, node_name):
        return node_name in self.__node_name_to_index

    def add_node(self, type, name, label=""):
        if self.__is_nodes_contains_name(name):
            self.__logger.log("Node tree contains node with name " + name)
        else:
            new_node = NodeTree.Node(type, name, label, self)
            self.__nodes.append(new_node)
            self.__node_name_to_index[name] = len(self.__nodes) - 1
            return new_node

    def get_node(self, node_id):
        python_version = sys.version_info.major
        if python_version == 2:
            if isinstance(node_id, basestring):
                if node_id in self.__node_name_to_index:
                    return self.__nodes[self.__node_name_to_index[node_id]]
                else:
                    self.__logger.log("Node tree does not contains the node " + node_id)
                    return None
            elif isinstance(node_id, (int, long)):
                if node_id < len(self.__nodes):
                    return self.__nodes[node_id]
                else:
                    self.__logger.log("Node tree does not contains the node with index" + str(node_id))
                    return None
        else:
            if isinstance(node_id, str):
                if node_id in self.__node_name_to_index:
                    return self.__nodes[self.__node_name_to_index[node_id]]
                else:
                    self.__logger.log("Node tree does not contains the node " + node_id)
                    return None
            elif isinstance(node_id, int):
                if node_id < len(self.__nodes):
                    return self.__nodes[node_id]
                else:
                    self.__logger.log("Node tree does not contains the node with index" + str(node_id))
                    return None

    def add_connection(self, output_node_name, output_port_name, input_node_name, input_port_name):
        if self.is_node_exist(output_node_name):
            if self.is_node_exist(input_node_name):
                out_node = self.get_node(output_node_name)
                in_node = self.get_node(input_node_name)
                if out_node.is_output_exist(output_port_name):
                    if in_node.is_input_exist(input_port_name):
                        # nodes and ports exist. Check that input port in input node is not used by other connections
                        is_used = False
                        for c in self.__connections:
                            c_data = c.get_raw()
                            if c_data[2] == input_node_name and c_data[3] == input_port_name:
                                is_used = True
                        if is_used is False:
                            # all correct, create connection
                            new_connection = NodeTree.Connection(out_node, output_port_name, in_node, input_port_name)
                            self.__connections.append(new_connection)
                        else:
                            self.__logger.log("The input port " + input_port_name + " of the node " + input_node_name + " is used by other connection")
                    else:
                        self.__logger.log("Node " + input_node_name + " does not contains input port " + input_port_name)
                else:
                    self.__logger.log("Node " + output_node_name + " does not contains output port " + output_port_name)
            else:
                self.__logger.log("There are no node with name " + input_node_name)
        else:
            self.__logger.log("There are no node with name " + output_node_name)

    def add_external_input_connection(self, input_node_name, input_port_name, external_input_name):
        if self.__parent_node is None:
            self.__logger.log("There is no parent node")
        else:
            if self.is_node_exist(input_node_name):
                in_node = self.get_node(input_node_name)
                if in_node.is_input_exist(input_port_name):
                    if self.__parent_node.is_input_exist(external_input_name):
                        # create connection
                        new_connection = NodeTree.Connection(self.__parent_node, external_input_name, in_node, input_port_name, True, 0)
                        self.__connections.append(new_connection)
                    else:
                        self.__logger.log("Parent node " + self.__parent_node.get_name() + " does not contains input port " + external_input_name)
                else:
                    self.__logger.log("Node " + input_node_name + " does not contains input port " + input_port_name)
            else:
                self.__logger.log("There are no node with name " + input_node_name)

    def add_external_output_connection(self, output_node_name, output_port_name, external_output_name):
        if self.__parent_node is None:
            self.__logger.log("There is no parent node")
        else:
            if self.is_node_exist(output_node_name):
                out_node = self.get_node(output_node_name)
                if out_node.is_output_exist(output_port_name):
                    if self.__parent_node.is_output_exist(external_output_name):
                        # create connection
                        new_connection = NodeTree.Connection(self.__parent_node, external_output_name, out_node, output_port_name, True, 1)
                        self.__connections.append(new_connection)
                    else:
                        self.__logger.log("Parent node does not contains output port " + external_output_name)
                else:
                    self.__logger.log("Node " + output_node_name + " does not contains output port " + output_port_name)
            else:
                self.__logger.log("There are no node with name " + output_node_name)

    def add_external_throw_connection(self, external_input_name, external_output_name):  # connection from inner input to inner output without any nodes
        if self.__parent_node is None:
            self.__logger.log("There is no parent node")
        else:
            if self.__parent_node.is_output_exist(external_output_name) and self.__parent_node.is_input_exist(external_input_name):
                new_connection = NodeTree.Connection(self.__parent_node, external_output_name, self.__parent_node, external_input_name, True, 2)
                self.__connections.append(new_connection)
            else:
                self.__logger.log("Parent node " + self.__parent_node.get_name() + " does not contains input port " + external_input_name + " or output port " + external_output_name)

    def _add_to_xml(self, mat):
        # at first add nodes
        # create dictionary with connections data in the form {(input_node, input_port): (output_node, output_port, is_External)}
        input_to_output_dict = {}
        for c in self.__connections:
            raw = c.get_raw()
            if raw[4] is False:
                input_to_output_dict[(raw[2], raw[3])] = (raw[0], raw[1], raw[4])
            else:
                if raw[5] == 0 or raw[5] == 2:
                    input_to_output_dict[(raw[2], raw[3])] = (raw[0], raw[1], raw[4])
                elif raw[5] == 1:
                    input_to_output_dict[(raw[0], raw[1])] = (raw[2], raw[3], raw[4])
        nodes_section = ET.SubElement(mat, "nodes")
        for node in self.__nodes:
            node._add_to_xml(nodes_section, input_to_output_dict)
        # at second add connections
        # connections_section = ET.SubElement(mat, "connections")
        # for connectin in self.__connections:
            # connectin._add_to_xml(connections_section)


class Material(object):
    def __init__(self, mat_name, render_name=None):
        self.__name = mat_name
        self.__renderer = render_name
        self.__node_tree = NodeTree()

    def get_node_tree(self):
        return self.__node_tree

    def get_name(self):
        return self.__name

    def get_renderer(self):
        return self.__renderer

    def _add_to_xml(self, root):
        params_dict = {"name": self.__name}
        if self.__renderer is not None:
            params_dict["render"] = self.__renderer
        mat_section = ET.SubElement(root, "node_tree", params_dict)
        self.__node_tree._add_to_xml(mat_section)


class NodeTreeDescriptor(object):
    def __init__(self, lib_name=None):
        self.__lib_name = lib_name
        if self.__lib_name is None:
            self.__lib_name = "Unknown"
        self.__materials = []
        self.__logger = NodeTree.LoggerHelper()

    def get_materials_count(self):
        return len(self.__materials)

    def get_library_name(self):
        return self.__lib_name

    def get_material(self, mat_index):
        if mat_index < len(self.__materials):
            return self.__materials[mat_index]
        else:
            return None

    def add_material(self, mat_name=None, mat_render=None):
        if mat_name is None:
            name = "Material" + str(len(self.__materials))
        else:
            name = mat_name
        render = mat_render
        new_mat = Material(name, render)
        self.__materials.append(new_mat)
        return new_mat.get_node_tree()

    def indent(self, elem, level=0):
        i = "\n" + level*"    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def write_xml(self, file_name):
        root = ET.Element("library", {"name": self.__lib_name})
        for m in self.__materials:
            m._add_to_xml(root)

        self.indent(root)
        tree = ET.ElementTree(root)
        tree.write(file_name)

    def __string_to_array(self, string):
        parts = string.split(" ")
        to_return = []
        for p in parts:
            to_return.append(ast.literal_eval(p))
        return to_return

    def __get_value(self, input_type, value_str):
        if input_type == "int":
            return ast.literal_eval(value_str)
        elif input_type == "float":
            return ast.literal_eval(value_str)
        elif input_type == "string":
            return value_str
        elif input_type == "bool":
            return ast.literal_eval(value_str)
        elif input_type == "color4":
            d_array = self.__string_to_array(value_str)
            return Color4(d_array[0], d_array[1], d_array[2], d_array[3])
        elif input_type == "vector3":
            d_array = self.__string_to_array(value_str)
            return Vector3(d_array[0], d_array[1], d_array[2])
        elif input_type == "color3":
            d_array = self.__string_to_array(value_str)
            return Color3(d_array[0], d_array[1], d_array[2])
        elif input_type == "vector2":
            d_array = self.__string_to_array(value_str)
            return Vector2(d_array[0], d_array[1])
        elif input_type == "closure":
            return Closure()
        elif input_type == "vectorArray":
            d_array = self.__string_to_array(value_str)
            return VectorArray(d_array)
        else:
            return None

    def __read_node_tree(self, root, node_tree, output_connections=[]):
        # output_connections come from the parent node and has additional key: is_to_myself, which corresponds Passthrough mode
        input_external_connections = []  # contains data in the form [(output_node, output_port, input_node, input_port), ...]
        input_internal_connections = []
        for child in root:
            if child.tag == "nodes":  # this is nodes section
                # iterate throw childs
                for child_node in child:
                    node_type = child_node.tag
                    if "name" in child_node.attrib:
                        node_name = child_node.attrib["name"]
                        node_label = child_node.attrib["label"] if "label" in child_node.attrib.keys() else ""
                        node = node_tree.add_node(node_type, node_name, node_label)
                        out_connections = []
                        subtree_prop = None
                        # next add inputs, outputs and parametrs to the node
                        for p in child_node:
                            if p.tag == "input":
                                if "type" in p.attrib and "default" in p.attrib and "port" in p.attrib:
                                    input_type = p.attrib["type"]
                                    node.add_input(p.attrib["port"], input_type, self.__get_value(input_type, p.attrib["default"]))
                                    # try to find connection to this input port
                                    if "source_external" in p.attrib and "source_node" in p.attrib and "source_port" in p.attrib:
                                        # this input port has connection
                                        is_external = True if p.attrib["source_external"] == "True" else False
                                        if is_external:
                                            input_external_connections.append((p.attrib["source_node"], p.attrib["source_port"], node_name, p.attrib["port"]))
                                        else:
                                            input_internal_connections.append((p.attrib["source_node"], p.attrib["source_port"], node_name, p.attrib["port"]))
                                else:
                                    self.__logger.log("Node " + node_name + " does not contains proper data for input port. Skip it.")
                            elif p.tag == "output":
                                if "port" in p.attrib and "type" in p.attrib:
                                    node.add_output(p.attrib["port"], p.attrib["type"])
                                    # try to find connections to the output port, in fact external connections
                                    if "source_node" in p.attrib and "source_port" in p.attrib:
                                        out_connections.append((p.attrib["source_node"], p.attrib["source_port"], node_name, p.attrib["port"], p.attrib["source_node"] == node_name))
                                else:
                                    self.__logger.log("Node " + node_name + " does not contains proper data for output port. Skip it.")
                            elif p.tag == "parameter":
                                if "type" in p.attrib and "name" in p.attrib:
                                    val_type = p.attrib["type"]
                                    node.add_parameter(p.attrib["name"], val_type, self.__get_value(val_type, p.attrib["value"]))
                                else:
                                    self.__logger.log("Node " + node_name + " does not contains proper data for parameter. Skip it.")
                            elif p.tag == "node_tree":  # this node contains subtree
                                subtree_prop = p
                        if subtree_prop is not None:
                            subtree = node.add_subtree()
                            self.__read_node_tree(subtree_prop, subtree, out_connections)
                    else:
                        self.__logger.log("Node does not contains name data. Skip it.")
            elif child.tag == "connections":  # this is connections section, this section exist only on old version of the file
                for c in child:
                    if c.tag == "connection":
                        if "in_node" in c.attrib and "in_port" in c.attrib and "out_node" in c.attrib and "out_port" in c.attrib:
                            if "external" in c.attrib:
                                is_external = c.attrib["external"] == "True"
                            else:
                                is_external = False
                            if is_external:
                                if "external_mode" in c.attrib:
                                    ext_mode = c.attrib["external_mode"]
                                else:
                                    ext_mode = ""
                                if ext_mode == "Input":
                                    node_tree.add_external_input_connection(c.attrib["in_node"], c.attrib["in_port"], c.attrib["out_port"])
                                elif ext_mode == "Output":
                                    node_tree.add_external_output_connection(c.attrib["in_node"], c.attrib["in_port"], c.attrib["out_port"])
                                elif ext_mode == "Passthrough":
                                    node_tree.add_external_throw_connection(c.attrib["in_port"], c.attrib["out_port"])
                            else:
                                node_tree.add_connection(c.attrib["out_node"], c.attrib["out_port"], c.attrib["in_node"], c.attrib["in_port"])
                        else:
                            self.__logger.log("Connection does not contains data about input and output ports and nodes. Skip it.")
            # at last add connections from input and output ports
            for c_data in input_internal_connections:
                node_tree.add_connection(c_data[0], c_data[1], c_data[2], c_data[3])
            for c_data in input_external_connections:
                node_tree.add_external_input_connection(c_data[2], c_data[3], c_data[1])
            for c_data in output_connections:
                # each c_data is a four-tuple (n1, p1, n2, p2, key), where n2, p2 - actual output of the compount node, n1, p1 - node inside compound
                if c_data[4]:
                    node_tree.add_external_throw_connection(c_data[1], c_data[3])
                else:
                    node_tree.add_external_output_connection(c_data[0], c_data[1], c_data[3])

    def read_xml(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        # set library name
        self.__lib_name = root.attrib["name"] if "name" in root.attrib else "Unknown"
        # next iterate throw node trees
        for node_tree in root:
            if node_tree.tag == "node_tree":  # consider only node_tree segments. Other seements unsupported
                material = self.add_material(node_tree.attrib["name"] if "name" in node_tree.attrib else None, node_tree.attrib["render"] if "render" in node_tree.attrib else None)
                # add nodes to material
                self.__read_node_tree(node_tree, material, [])


def example_create_and_save_node_tree():
    doc = NodeTreeDescriptor("Example library")
    node_tree = doc.add_material()

    bsdf_node = node_tree.add_node("BSDF", "bsdf_node")
    in_color = bsdf_node.add_input("Color", "color4", Color4(0.8))
    in_raugness = bsdf_node.add_input("Roughness", "float", 0.1)
    in_normal = bsdf_node.add_input("Normal", "vector3", Normal(0.0))
    out_bsdf = bsdf_node.add_output("BSDF", "color4")
    bsdf_node.add_parameter("InnerParameter", "vector3", Normal(1.0))
    bsdf_node.add_parameter("FloatParameter", "float", 12.2)
    subtree = bsdf_node.add_subtree()
    subtree.add_node("Color", "sub_color")

    out_node = node_tree.add_node("Output", "material_output")
    out_node.add_input("Surface", "color4", Color4(0.0))
    out_node.add_input("Volume", "color4", Color4(0.0))
    out_node.add_input("Displacement", "float", 0.0)

    node_tree.add_connection(bsdf_node.get_name(), "BSDF", out_node.get_name(), "Surface")

    doc.write_xml("example_material.gem")


def example_read_node_tree_from_file():
    file_path = "example_material.gem"
    doc = NodeTreeDescriptor()
    doc.read_xml(file_path)
    doc.write_xml("example_material_copy.gem")


def example_subnodes():
    doc = NodeTreeDescriptor("Example library")
    node_tree = doc.add_material()
    out_node = node_tree.add_node("Output", "output_node")
    out_node.add_input("Surface", "color4", Color4(0.8))
    complex_node = node_tree.add_node("Complex", "node_with_subtree")
    complex_node.add_output("out", "color4")
    complex_node.add_input("in", "float", 0.0)
    complex_node.add_input("in2", "float", 1.0)
    complex_node.add_output("out2", "float")
    subtree = complex_node.add_subtree()
    convert_node = subtree.add_node("Converter", "convert_node")
    convert_node.add_input("value", "float", 0.0)
    convert_node.add_output("color", "color4")
    subtree.add_external_input_connection("convert_node", "value", "in")
    subtree.add_external_output_connection("convert_node", "color", "out")
    subtree.add_external_throw_connection("in2", "out2")

    node_tree.add_connection("node_with_subtree", "out", "output_node", "Surface")

    doc.write_xml("example_subnodes.gem")


if __name__ == "__main__":
    example_create_and_save_node_tree()
    example_read_node_tree_from_file()
    example_subnodes()
