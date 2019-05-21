# Nikita Akimov
# interplanety@interplanety.org

# --------------------------------------------------------------
# for older compatibility
# used for node groups version 1.4.1
# if there would no 1.4.1 nodegroups - all this file can be removed
# work with - node_io
# --------------------------------------------------------------


from .JsonEx import JsonEx


class GIOCommon:
    @classmethod
    def gio_to_json(cls, io, gio=None):
        gio_json = {
            'type': io.type,
            'bl_type': io.bl_socket_idname,
            'name': io.name,
            'identifier': io.identifier
        }
        # for current gio specification
        cls._gio_to_json_spec(gio_json, io, gio)
        return gio_json

    @classmethod
    def _gio_to_json_spec(cls, gio_json, io, gio=None):
        # extend to current gio data
        pass

    @classmethod
    def json_to_gi(cls, node_tree, group_node, input_number, input_in_json):
        group_input = node_tree.inputs.new(type=input_in_json['bl_type'], name=input_in_json['name'])
        # for current specification
        cls._json_to_gi_spec(group_input, group_node, input_number, input_in_json)
        return group_input

    @classmethod
    def _json_to_gi_spec(cls, group_input, group_node, input_number, input_in_json):
        # extend to current data
        pass

    @classmethod
    def json_to_go(cls, node_tree, output_in_json):
        group_output = node_tree.outputs.new(type=output_in_json['bl_type'], name=output_in_json['name'])
        group_output_number = len(node_tree.outputs) - 1    # the same number in Group Output node
        # for current specification
        cls._json_to_go_spec(group_output, group_output_number, output_in_json)
        return group_output

    @classmethod
    def _json_to_go_spec(cls, group_output, group_output_number, output_in_json):
        # extend to current data
        pass


class GIONodeSocketColor(GIOCommon):
    @classmethod
    def _gio_to_json_spec(cls, gio_json, io, gio=None):
        gio_json['default_value'] = JsonEx.prop_array_to_json(io.default_value)
        if gio:
            gio_json['value'] = JsonEx.prop_array_to_json(gio.default_value)

    @classmethod
    def _json_to_gi_spec(cls, group_input, group_node, input_number, input_in_json):
        JsonEx.prop_array_from_json(group_input.default_value, input_in_json['default_value'])
        if input_in_json['value']:
            JsonEx.prop_array_from_json(group_node.inputs[input_number].default_value, input_in_json['value'])

    @classmethod
    def _json_to_go_spec(cls, group_output, group_output_number, output_in_json):
        JsonEx.prop_array_from_json(group_output.default_value, output_in_json['default_value'])
        if 'value' in output_in_json:
            JsonEx.prop_array_from_json(group_output.node.inputs[group_output_number].default_value, output_in_json['value'])


class GIONodeSocketVector(GIONodeSocketColor):
    pass


class GIONodeSocketVectorDirection(GIONodeSocketVector):
    pass


class GIONodeSocketVectorXYZ(GIONodeSocketVector):
    pass


class GIONodeSocketVectorTranslation(GIONodeSocketVector):
    pass


class GIONodeSocketVectorVelocity(GIONodeSocketVector):
    pass


class GIONodeSocketShader(GIOCommon):
    pass


class GIONodeSocketFloat(GIOCommon):
    @classmethod
    def _gio_to_json_spec(cls, gio_json, io, gio=None):
        gio_json['default_value'] = io.default_value
        gio_json['min_value'] = io.min_value
        gio_json['max_value'] = io.max_value
        if gio:
            gio_json['value'] = gio.default_value

    @classmethod
    def _json_to_gi_spec(cls, group_input, group_node, input_number, input_in_json):
        group_input.default_value = input_in_json['default_value']
        group_input.min_value = input_in_json['min_value']
        group_input.max_value = input_in_json['max_value']
        group_node.inputs[input_number].default_value = input_in_json['value']

    @classmethod
    def _json_to_go_spec(cls, group_output, group_output_number, output_in_json):
        group_output.default_value = output_in_json['default_value']
        if 'value' in output_in_json:
            JsonEx.prop_array_from_json(group_output.node.inputs[group_output_number].default_value, output_in_json['value'])


class GIONodeSocketFloatFactor(GIONodeSocketFloat):
    pass


class GIONodeSocketFloatAngle(GIONodeSocketFloat):
    pass


class GIONodeSocketFloatUnsigned(GIONodeSocketFloat):
    pass


class GIONodeSocketInt(GIONodeSocketFloat):
    pass
