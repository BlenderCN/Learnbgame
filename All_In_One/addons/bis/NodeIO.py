# Nikita Akimov
# interplanety@interplanety.org

# --------------------------------------------------------------
# for older compatibility
# used for node groups version 1.4.1
# if there would no 1.4.1 nodegroups - all this file can be removed
# work with - node_io
# --------------------------------------------------------------


from .JsonEx import JsonEx


class IOCommon:
    @classmethod
    def io_to_json(cls, io):
        io_json = {
            'type': io.type,
            'bl_type': io.bl_idname,
            'name': io.name,
            'identifier': io.identifier
        }
        # for current io specification
        cls._io_to_json_spec(io_json, io)
        return io_json

    @classmethod
    def _io_to_json_spec(cls, io_json, io):
        # extend to current io data
        pass

    @classmethod
    def json_to_i(cls, node, input_number, input_in_json):
        node.inputs[input_number].name = input_in_json['name']
        # for current input specification
        cls._json_to_i_spec(node, input_number, input_in_json)

    @classmethod
    def _json_to_i_spec(cls, node, input_number, input_in_json):
        # extend to current input data
        pass

    @classmethod
    def json_to_o(cls, node, output_number, output_in_json):
        node.outputs[output_number].name = output_in_json['name']
        # for current output specification
        cls._json_to_o_spec(node, output_number, output_in_json)

    @classmethod
    def _json_to_o_spec(cls, node, output_number, output_in_json):
        # extend to current output data
        pass


class IONodeSocketColor(IOCommon):
    @classmethod
    def _io_to_json_spec(cls, io_json, io):
        io_json['default_value'] = JsonEx.prop_array_to_json(io.default_value)

    @classmethod
    def _json_to_i_spec(cls, node, input_number, input_in_json):
        JsonEx.prop_array_from_json(node.inputs[input_number].default_value, input_in_json['default_value'])

    @classmethod
    def _json_to_o_spec(cls, node, output_number, output_in_json):
        JsonEx.prop_array_from_json(node.outputs[output_number].default_value, output_in_json['default_value'])


class IONodeSocketVector(IONodeSocketColor):
    pass


class IONodeSocketVectorDirection(IONodeSocketVector):
    pass


class IONodeSocketVectorXYZ(IONodeSocketVector):
    pass


class IONodeSocketVectorTranslation(IONodeSocketVector):
    pass


class IONodeSocketVectorVelocity(IONodeSocketVector):
    pass


class IONodeSocketShader(IOCommon):
    pass


class IONodeSocketVirtual(IOCommon):
    pass


class IONodeSocketFloat(IOCommon):
    @classmethod
    def _io_to_json_spec(cls, io_json, io):
        io_json['default_value'] = io.default_value

    @classmethod
    def _json_to_i_spec(cls, node, input_number, input_in_json):
        node.inputs[input_number].default_value = input_in_json['default_value']

    @classmethod
    def _json_to_o_spec(cls, node, output_number, output_in_json):
        node.outputs[output_number].default_value = output_in_json['default_value']


class IONodeSocketFloatFactor(IONodeSocketFloat):
    pass


class IONodeSocketFloatAngle(IONodeSocketFloat):
    pass


class IONodeSocketFloatUnsigned(IONodeSocketFloat):
    pass


class IONodeSocketInt(IONodeSocketFloat):
    pass


class IONodeGroupInput:
    @classmethod
    def io_to_json(cls, io):
        return {}

    @classmethod
    def json_to_i(cls, node, input_number, input_in_json):
        pass

    @classmethod
    def json_to_o(cls, node, output_number, output_in_json):
        pass


class IONodeGroupOutput(IONodeGroupInput):
    pass
