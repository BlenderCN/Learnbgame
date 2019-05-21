# Nikita Akimov
# interplanety@interplanety.org

from .JsonEx import JsonEx


class NodeIOCommon:
    @classmethod
    def input_to_json(cls, node_input):
        input_json = {
            'type': node_input.type,
            'bl_idname': node_input.bl_idname,
            'identifier': node_input.identifier,
            'name': node_input.name
        }
        # for current io specification
        cls._input_to_json_spec(input_json, node_input)
        return input_json

    @classmethod
    def _input_to_json_spec(cls, input_json, node_input):
        # extend to current io data
        pass

    @classmethod
    def output_to_json(cls, node_output):
        output_json = {
            'type': node_output.type,
            'bl_idname': node_output.bl_idname,
            'identifier': node_output.identifier,
            'name': node_output.name
        }
        # for current io specification
        cls._output_to_json_spec(output_json, node_output)
        return output_json

    @classmethod
    def _output_to_json_spec(cls, output_json, output):
        # extend to current io data
        pass

    @classmethod
    def json_to_i(cls, node_input, input_json):
        if node_input:
            node_input.name = input_json['name']
            if node_input.bl_idname == input_json['bl_idname']:
                # for current input specification
                cls._json_to_i_spec(node_input, input_json)

    @classmethod
    def _json_to_i_spec(cls, node_input, input_json):
        # extend to current input data
        pass

    @classmethod
    def json_to_o(cls, node_output, output_json):
        if node_output:
            node_output.name = output_json['name']
            if node_output.bl_idname == output_json['bl_idname']:
                # for current output specification
                cls._json_to_o_spec(node_output, output_json)

    @classmethod
    def _json_to_o_spec(cls, node_output, output_json):
        # extend to current output data
        pass


class NodeIONodeSocketColor(NodeIOCommon):
    @classmethod
    def _input_to_json_spec(cls, input_json, node_input):
        input_json['default_value'] = JsonEx.prop_array_to_json(node_input.default_value)

    @classmethod
    def _output_to_json_spec(cls, output_json, node_output):
        output_json['default_value'] = JsonEx.prop_array_to_json(node_output.default_value)

    @classmethod
    def _json_to_i_spec(cls, node_input, input_json):
        JsonEx.prop_array_from_json(node_input.default_value, input_json['default_value'])
        if node_input.node.type == 'GROUP':
            JsonEx.prop_array_from_json(node_input.node.inputs[-1].default_value, input_json['default_value'])

    @classmethod
    def _json_to_o_spec(cls, node_output, output_json):
        JsonEx.prop_array_from_json(node_output.default_value, output_json['default_value'])


class NodeIONodeSocketVector(NodeIONodeSocketColor):
    pass


class NodeIONodeSocketVectorDirection(NodeIONodeSocketVector):
    pass


class NodeIONodeSocketVectorXYZ(NodeIONodeSocketVector):
    pass


class NodeIONodeSocketVectorTranslation(NodeIONodeSocketVector):
    pass


class NodeIONodeSocketVectorVelocity(NodeIONodeSocketVector):
    pass


class NodeIONodeSocketShader(NodeIOCommon):
    pass


class NodeIONodeSocketVirtual(NodeIOCommon):
    pass


class NodeIONodeSocketFloat(NodeIOCommon):
    @classmethod
    def _input_to_json_spec(cls, input_json, node_input):
        input_json['default_value'] = node_input.default_value
        if node_input.node.type == 'GROUP':
            node_input_index = node_input.node.inputs[:].index(node_input)
            input_json['min_value'] = node_input.node.node_tree.inputs[node_input_index].min_value
            input_json['max_value'] = node_input.node.node_tree.inputs[node_input_index].max_value

    @classmethod
    def _output_to_json_spec(cls, output_json, node_output):
        output_json['default_value'] = node_output.default_value

    @classmethod
    def _json_to_i_spec(cls, node_input, input_json):
        node_input.default_value = input_json['default_value']
        if node_input.node.type == 'GROUP':
            node_input.node.inputs[-1].default_value = input_json['default_value']
            if 'min_value' in input_json:
                node_input.node.node_tree.inputs[-1].min_value = input_json['min_value']
                node_input.node.node_tree.inputs[-1].max_value = input_json['max_value']

    @classmethod
    def _json_to_o_spec(cls, node_output, output_json):
        node_output.default_value = output_json['default_value']


class NodeIONodeSocketFloatFactor(NodeIONodeSocketFloat):
    pass


class NodeIONodeSocketFloatAngle(NodeIONodeSocketFloat):
    pass


class NodeIONodeSocketFloatUnsigned(NodeIONodeSocketFloat):
    pass


class NodeIONodeSocketInt(NodeIONodeSocketFloat):
    pass


class NodeIONodeGroupInput(NodeIOCommon):
    pass


class NodeIONodeGroupOutput(NodeIONodeGroupInput):
    pass
