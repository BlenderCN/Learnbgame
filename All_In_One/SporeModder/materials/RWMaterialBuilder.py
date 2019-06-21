__author__ = 'Eric'

import struct
from collections import namedtuple, OrderedDict
from . import DirectXEnums
from .. import RW4Base


class RWTextureSlot:
    def __init__(self,
                 sampler_index=0, unknown_has_stage_states=0, unknown_has_sampler_states=0, texture_raster=None,
                 set_default_states=True):
        self.texture_stage_states = OrderedDict()
        self.sampler_states = OrderedDict()
        self.texture_raster = texture_raster
        self.unknown_has_stage_states = unknown_has_stage_states  # usually 0x3F: mask of which samplers can be used
        self.unknown_has_sampler_states = unknown_has_sampler_states  # usually 0x73
        self.sampler_index = sampler_index

        if set_default_states:
            if self.unknown_has_stage_states == 0x3f:
                self.texture_stage_states[DirectXEnums.D3DTEXTURESTAGESTATETYPE.D3DTSS_COLOROP] = \
                    DirectXEnums.D3DTEXTUREOP.D3DTOP_MODULATE

                self.texture_stage_states[DirectXEnums.D3DTEXTURESTAGESTATETYPE.D3DTSS_COLORARG1] = \
                    DirectXEnums.D3DTA.D3DTA_TEXTURE

                self.texture_stage_states[DirectXEnums.D3DTEXTURESTAGESTATETYPE.D3DTSS_COLORARG2] = \
                    DirectXEnums.D3DTA.D3DTA_DIFFUSE

                self.texture_stage_states[DirectXEnums.D3DTEXTURESTAGESTATETYPE.D3DTSS_ALPHAOP] = \
                    DirectXEnums.D3DTEXTUREOP.D3DTOP_MODULATE

                self.texture_stage_states[DirectXEnums.D3DTEXTURESTAGESTATETYPE.D3DTSS_ALPHAARG1] = \
                    DirectXEnums.D3DTA.D3DTA_TEXTURE

                self.texture_stage_states[DirectXEnums.D3DTEXTURESTAGESTATETYPE.D3DTSS_ALPHAARG2] = \
                    DirectXEnums.D3DTA.D3DTA_DIFFUSE

            elif self.unknown_has_stage_states == 0x9:
                self.texture_stage_states[DirectXEnums.D3DTEXTURESTAGESTATETYPE.D3DTSS_COLOROP] = \
                    DirectXEnums.D3DTEXTUREOP.D3DTOP_DISABLE

                self.texture_stage_states[DirectXEnums.D3DTEXTURESTAGESTATETYPE.D3DTSS_ALPHAOP] = \
                    DirectXEnums.D3DTEXTUREOP.D3DTOP_DISABLE

            if self.unknown_has_sampler_states == 0x73:
                self.sampler_states[DirectXEnums.D3DSAMPLERSTATETYPE.D3DSAMP_ADDRESSU] = \
                    DirectXEnums.D3DTEXTUREADDRESS.D3DTADDRESS_WRAP

                self.sampler_states[DirectXEnums.D3DSAMPLERSTATETYPE.D3DSAMP_ADDRESSV] = \
                    DirectXEnums.D3DTEXTUREADDRESS.D3DTADDRESS_WRAP

                self.sampler_states[DirectXEnums.D3DSAMPLERSTATETYPE.D3DSAMP_MAGFILTER] = \
                    DirectXEnums.D3DTEXTUREFILTERTYPE.D3DTEXF_LINEAR

                self.sampler_states[DirectXEnums.D3DSAMPLERSTATETYPE.D3DSAMP_MINFILTER] = \
                    DirectXEnums.D3DTEXTUREFILTERTYPE.D3DTEXF_LINEAR

                self.sampler_states[DirectXEnums.D3DSAMPLERSTATETYPE.D3DSAMP_MIPFILTER] = \
                    DirectXEnums.D3DTEXTUREFILTERTYPE.D3DTEXF_POINT


ShaderConstant = namedtuple('ShaderConstant', ('index', 'offset', 'data'))

ShaderConstants = {
    'skinWeights': 0x003,
    'skinBones': 0x004,
    'modelToClip': 0x006,
    'modelToCamera': 0x007,
    'modelToWorld': 0x008,
    'worldToClip': 0x00C,
    'cameraToWorld': 0x00D,
    'cameraToWorldTranspose': 0x010,
    'worldCameraPosition': 0x01F,
    'worldCameraDirection': 0x021,
    'materialColor': 0x022,
    'ambient': 0x023,
    'time': 0x027,

    'objectTypeColor': 0x202,
    'frameInfo': 0x203,
    'screenInfo': 0x204,
    'customParams': 0x206,
    'materialParams': 0x210,
    'uvTweak': 0x211,
    'dirLightsWorld': 0x214,
    'shCoeffs': 0x21A,
    'expandAmount': 0x220,
    'shadowMapInfo': 0x223,
    'foggingCPU': 0x225,
    'patchLocation': 0x226,
    'viewTransform': 0x252,
    'pcaTexture': 0x22f,
    'renderDepth': 0x231,
    'gameInfo': 0x248,

    'terrainTint': 0x233,
    'terrainBrushCubeMatRot': 0x241,
    'terrainSynthParams': 0x242,
    'ramp': 0x24A,

    'terrainLighting': 0x24C,
    'worldToPatch': 0x23D,
    'beachColor': 0x250,
    'cliffColor': 0x251,
    'terrainTransform': 0x301,
    'decalState': 0x304,
    'terrainState': 0x305,

    # There are up to 2048 indices, but apparently above 1024 they give trouble
    'ModAPIShader': 0x3FF
}


class RWMaterialBuilder:
    FLAG_shader_constants = 0x8
    FLAG_material_color = 0x10
    FLAG_ambient_color = 0x20
    FLAG_vertex_description = 0x100000
    # FLAG_not_use_booleans = 0x80000000

    FLAG_use_booleans = 0x8000

    FLAG3_render_states = 0x20000
    FLAG3_texture_slots = 0x1  # Spore checks for 0xDFFFF, using this should be enough

    def __init__(self):
        self.material_color = None
        self.ambient_color = None
        self.texture_slots = []
        self.render_states = OrderedDict()
        self.shader_constants = []
        self.vertex_description = None
        self.shader_ID = 0
        self.primitive_type = 4
        # 17 booleans. If you don't want to use it, directly assign it to None
        self.unknown_booleans = []

    def get_shader_constant(self, index):
        for shConst in self.shader_constants:
            if shConst.index == index:
                return shConst

        return None

    @staticmethod
    def write_state(stream, state, value):
        stream.extend(struct.pack('<II',
                                  state,  # state
                                  value  # value
                                  ))

    def write(self, renderWare, stream):

        flags1 = 0
        flags2 = 0
        flags3 = 0

        # always used? don't really know what it does
        flags1 |= 4
        flags2 |= 0x8000

        # always used? don't really know what it does
        flags1 |= 4
        flags2 |= 0x8000

        if self.material_color is not None:
            flags1 |= RWMaterialBuilder.FLAG_material_color

        if self.ambient_color is not None:
            flags1 |= RWMaterialBuilder.FLAG_ambient_color

        if self.unknown_booleans is not None:
            flags1 |= RWMaterialBuilder.FLAG_use_booleans

        if len(self.shader_constants) > 0:
            flags1 |= RWMaterialBuilder.FLAG_shader_constants
            flags2 |= RWMaterialBuilder.FLAG_shader_constants

        if self.vertex_description is not None:
            flags1 |= RWMaterialBuilder.FLAG_vertex_description
            flags2 |= RWMaterialBuilder.FLAG_vertex_description

        if len(self.render_states) > 0:
            flags3 |= RWMaterialBuilder.FLAG3_render_states

        for slot in self.texture_slots:
            flags3 |= 1 << slot.sampler_index

        stream.extend(struct.pack('<IIIIIII',
                                  self.primitive_type,
                                  flags1,
                                  flags2,
                                  flags3,
                                  0,  # field_14, also sued as flags
                                  self.shader_ID,
                                  0  # just padding
                                  ))

        if self.vertex_description is not None:
            vertex_description_stream = RW4Base.ArrayFileWriter()
            self.vertex_description.write(vertex_description_stream)

            stream.extend(vertex_description_stream.fileBuffer)

        if len(self.shader_constants) > 0:
            for constant in self.shader_constants:
                stream.extend(struct.pack('<HHI',
                                          constant.index,
                                          constant.offset,
                                          len(constant.data)
                                          ))
                if constant.offset > 0:
                    stream.extend(bytearray(constant.offset))
                stream.extend(constant.data)

            stream.extend(bytearray(8))

        if self.material_color is not None:
            stream.extend(struct.pack('<ffff',
                                      self.material_color[0],
                                      self.material_color[1],
                                      self.material_color[2],
                                      self.material_color[3]))

        if self.ambient_color is not None:
            stream.extend(struct.pack('<fff',
                                      self.ambient_color[0],
                                      self.ambient_color[1],
                                      self.ambient_color[2]))

        if self.unknown_booleans is not None:
            for i in range(17):
                if i >= len(self.unknown_booleans):
                    stream.extend(struct.pack('<?', False))
                else:
                    stream.extend(struct.pack('<?', self.unknown_booleans[i]))

        if len(self.render_states) > 0:
            stream.extend(struct.pack('<I', 0))

            for state in self.render_states.keys():
                RWMaterialBuilder.write_state(stream, state, self.render_states[state])

            stream.extend(struct.pack('<ii', -1, -1))

        if len(self.texture_slots) > 0:
            stream.extend(struct.pack('<i', -1))

            for texture_slot in self.texture_slots:

                stream.extend(struct.pack('<iii',
                                          texture_slot.sampler_index,
                                          renderWare.getIndex(texture_slot.texture_raster),
                                          texture_slot.unknown_has_stage_states
                                          ))

                if texture_slot.unknown_has_stage_states != 0:
                    for state in texture_slot.texture_stage_states:
                        RWMaterialBuilder.write_state(stream, state, texture_slot.texture_stage_states[state])

                    stream.extend(struct.pack('<i', -1))

                stream.extend(struct.pack('<i',
                                          texture_slot.unknown_has_sampler_states))

                if texture_slot.unknown_has_sampler_states != 0:
                    for state in texture_slot.sampler_states.keys():
                        RWMaterialBuilder.write_state(stream, state, texture_slot.sampler_states[state])

                    stream.extend(struct.pack('<i', -1))

            stream.extend(struct.pack('<i', -1))

    def from_compiled_state(self, data_reader):

        """

        :type data_reader: RW4Base.ArrayFileReader
        """
        data_reader.skipBytes(4)  # primitiveType
        flags1 = data_reader.readUInt()
        flags2 = data_reader.readUInt()
        flags3 = data_reader.readUInt()
        field_14 = data_reader.readUInt()
        self.shader_ID = data_reader.readUInt()

        data_reader.skipBytes(4)  # just padding

        if (flags1 & 1) != 0:
            if (flags1 & 2) != 0:
                data_reader.skipBytes(4)
            else:
                data_reader.skipBytes(0x40)

        if (flags1 & RWMaterialBuilder.FLAG_vertex_description) != 0:
            RW4Base.VertexDescription(None).read(data_reader)

        if (flags1 & RWMaterialBuilder.FLAG_shader_constants) != 0:

            index = data_reader.readShort()
            while index != 0:
                if index > 0:
                    self.shader_constants.append(ShaderConstant(
                        index=index,
                        offset=data_reader.readShort(),
                        data=data_reader.read(data_reader.readInt())
                    ))
                else:
                    data_reader.skipBytes(4)
                    
                index = data_reader.readShort()
                
            data_reader.skipBytes(6)

        if (flags1 & RWMaterialBuilder.FLAG_material_color) != 0:
            self.material_color = (
                data_reader.readFloat(),
                data_reader.readFloat(),
                data_reader.readFloat(),
                data_reader.readFloat(),
            )

        if (flags1 & RWMaterialBuilder.FLAG_ambient_color) != 0:
            self.ambient_color = (
                data_reader.readFloat(),
                data_reader.readFloat(),
                data_reader.readFloat(),
            )

        if (flags1 & 0x3FC0) != 0:
            for i in range(8):
                if (flags1 & (1 << (6 + i))) != 0:
                    data_reader.skipBytes(4)

        if (flags1 & RWMaterialBuilder.FLAG_use_booleans) != 0:
            for i in range(0x11):
                self.unknown_booleans.append(data_reader.readBoolean())

        if (flags1 & 0xF0000) != 0:
            if (flags1 & 0x10000) != 0:
                data_reader.skipBytes(4)

            if (flags1 & 0xE0000) != 0:
                if (flags1 & 0x20000) != 0:
                    data_reader.skipBytes(12)

                if (flags1 & 0x40000) != 0:
                    data_reader.skipBytes(4)

                if (flags1 & 0x80000) != 0:
                    data_reader.skipBytes(4)

        if field_14 != 0:
            if (field_14 & 0x20000) != 0:
                data_reader.skipBytes(0x1C)

            if (field_14 & 0x40000) != 0:
                data_reader.skipBytes(0x44)

            if (field_14 & 0x80000) != 0:
                data_reader.skipBytes(0x44)

        if (flags3 & RWMaterialBuilder.FLAG3_render_states) != 0:
            data_reader.skipBytes(4)

            while True:
                state = data_reader.readInt()
                value = data_reader.readInt()

                if state == -1 and value == -1:
                    break

                self.render_states[state] = value

        # here would go the render states, but we don't need to read them

    def set_render_states(self, alpha_mode='NO_ALPHA'):
        """
        :param alpha_mode: Possible options are 'NO_ALPHA', 'ALPHA', 'EXCLUDING_ALPHA'
        :return:
        """

        if alpha_mode == 'NO_ALPHA':
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ZWRITEENABLE] = 1
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHATESTENABLE] = 0
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_CULLMODE] = DirectXEnums.D3DCULL.D3DCULL_CW
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ZFUNC] = \
                DirectXEnums.D3DCMPFUNC.D3DCMP_LESSEQUAL
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHABLENDENABLE] = 0

        elif alpha_mode == 'ALPHA':
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ZWRITEENABLE] = 1
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHATESTENABLE] = 1
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_SRCBLEND] = \
                DirectXEnums.D3DBLEND.D3DBLEND_SRCALPHA
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_DESTBLEND] = \
                DirectXEnums.D3DBLEND.D3DBLEND_INVSRCALPHA
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_CULLMODE] = DirectXEnums.D3DCULL.D3DCULL_CW
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ZFUNC] = \
                DirectXEnums.D3DCMPFUNC.D3DCMP_LESSEQUAL
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHAREF] = 0
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHAFUNC] = \
                DirectXEnums.D3DCMPFUNC.D3DCMP_GREATER
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHABLENDENABLE] = 1

        elif alpha_mode == 'EXCLUDING_ALPHA':
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ZWRITEENABLE] = 1
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHATESTENABLE] = 1
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_CULLMODE] = DirectXEnums.D3DCULL.D3DCULL_CW
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ZFUNC] = \
                DirectXEnums.D3DCMPFUNC.D3DCMP_LESSEQUAL
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHAREF] = 127
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHAFUNC] = \
                DirectXEnums.D3DCMPFUNC.D3DCMP_GREATER
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHABLENDENABLE] = 0
            self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_FOGENABLE] = 0

        else:
            raise NameError("Unsupported render states %s" % alpha_mode)

    def detect_render_states(self):
        if DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHATESTENABLE not in self.render_states:
            return None

        if self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHATESTENABLE] == 0:
            return 'NO_ALPHA'

        else:
            if DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHAREF not in self.render_states or \
                    self.render_states[DirectXEnums.D3DRENDERSTATETYPE.D3DRS_ALPHAREF] == 0:

                return 'ALPHA'

            else:
                return 'EXCLUDING_ALPHA'
