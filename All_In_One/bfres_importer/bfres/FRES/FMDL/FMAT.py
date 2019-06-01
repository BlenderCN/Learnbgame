import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from bfres.FRES.FresObject import FresObject
from bfres.FRES.Dict import Dict
import struct


shaderParamTypes = {
    # http://mk8.tockdom.com/wiki/FMDL_(File_Format)#Material_Parameter
    0x08: {'fmt':'I',  'name':'ptr',   'outfmt':'%08X'},
    0x0C: {'fmt':'f',  'name':'float', 'outfmt':'%f'},
    0x0D: {'fmt':'2f', 'name':'Vec2f', 'outfmt':'%f, %f'},
    0x0E: {'fmt':'3f', 'name':'Vec3f', 'outfmt':'%f, %f, %f'},
    0x0F: {'fmt':'4f', 'name':'Vec4f', 'outfmt':'%f, %f, %f, %f'},
    0x1E: {'fmt':'I5f','name':'texSRT', # scale, rotation, translation
        'outfmt':'mode=%d XS=%f YS=%f rot=%f X=%f Y=%f'},
}


class ShaderAssign(BinaryStruct):
    fields = (
        String  ('name'),  Padding(4),
        String  ('name2'), Padding(4),
        Offset64('vtx_attr_names'), # -> offsets of attr names
        Offset64('vtx_attr_dict'),
        Offset64('tex_attr_names'),
        Offset64('tex_attr_dict'),
        Offset64('mat_param_vals'), # names from dict
        Offset64('mat_param_dict'), Padding(4),
        ('B',    'num_vtx_attrs'),
        ('B',    'num_tex_attrs'),
        ('H',    'num_mat_params'),
    )


class Header(BinaryStruct):
    """FMAT header."""
    magic  = b'FMAT'
    fields = (
        ('4s',   'magic'), # 0x00
        ('I',    'size'),  # 0x04
        ('I',    'size2'), Padding(4), # 0x08
        String  ('name'),  Padding(4), # 0x10
        Offset64('render_param_offs'), # 0x18
        Offset64('render_param_dict_offs'), # 0x20
        Offset64('shader_assign_offs'), # 0x28 -> name offsets
        Offset64('unk30_offs'), # 0x30
        Offset64('tex_ref_array_offs'), # 0x38
        Offset64('unk40_offs'), # 0x40
        Offset64('sampler_list_offs'), # 0x48
        Offset64('sampler_dict_offs'), # 0x50
        Offset64('shader_param_array_offs'), # 0x58
        Offset64('shader_param_dict_offs'), # 0x60
        Offset64('shader_param_data_offs'), # 0x68
        Offset64('user_data_offs'), # 0x70
        Offset64('user_data_dict_offs'), # 0x78
        Offset64('volatile_flag_offs'), # 0x80
        Offset64('user_offs'), # 0x88
        Offset64('sampler_slot_offs'), # 0x90
        Offset64('tex_slot_offs'), # 0x98
        ('I',    'mat_flags'), # 0xA0
        ('H',    'section_idx'), # 0xA4
        ('H',    'render_param_cnt'), # 0xA6
        ('B',    'tex_ref_cnt'), # 0xA8
        ('B',    'sampler_cnt'), # 0xA9
        ('H',    'shader_param_cnt'), # 0xAA
        ('H',    'shader_param_data_size'), # 0xAC
        ('H',    'raw_param_data_size'), # 0xAE
        ('H',    'user_data_cnt'), # 0xB0
        ('H',    'unkB2'), # 0xB2; usually 0 or 1
        ('I',    'unkB4'), # 0xB4
    )
    size = 0xB8


class FMAT(FresObject):
    """A material object in an FRES."""
    Header = Header

    def __init__(self, fres):
        self.fres         = fres
        self.header       = None
        self.headerOffset = None
        self.name         = None


    def __str__(self):
        return "<FMAT(%s, @%s) at 0x%x>" %(
            str(self.name),
            '?' if self.headerOffset is None else hex(self.headerOffset),
            id(self),
        )


    def dump(self):
        """Dump to string for debug."""
        dicts = ('render_param', 'sampler', 'shader_param', 'user_data')

        res = []
        # Dump dicts
        #for i, name in enumerate(dicts):
        #    d = getattr(self, name+'_dict')
        #    if i == 0: name = '  '+name
        #    if d is None:
        #        res.append(name+": <none>")
        #    else:
        #        res.append(name+': '+ d.dump())

        # Dump render params
        res.append("Render params:")
        res.append("  \x1B[4mParam                           "+
            "│Type    │Cnt│Value\x1B[0m")
        for name, param in self.renderParams.items():
            res.append("  %-32s│%-8s│%3d│%s" % (
                name, param['type'], param['count'], param['vals']))

        # Dump shader params
        res.append("Shader params:")
        res.append("  \x1B[4mParam                                   "+
            "│Type  │Size│Offset│Idx0│Idx1│Unk00│Unk14│Data\x1B[0m")
        for name, param in self.shaderParams.items():
            res.append("  %-40s│%6s│%4d│%06X│%4d│%4d│%5d│%5d│%s" % (
                name,
                param['type']['name'],
                param['size'],    param['offset'],
                param['idxs'][0], param['idxs'][1],
                param['unk00'],   param['unk14'],
                param['data']))

        # Dump texture list
        res.append("Textures:")
        res.append("  \x1B[4mIdx│Slot│Name\x1B[0m")
        for i, tex in enumerate(self.textures):
            res.append("  %3d│%4d│%s" % (
                i, tex['slot'], tex['name']))

        # Dump sampler list
        res.append("Samplers:")
        res.append("  \x1B[4mIdx│Slot│Data\x1B[0m")
        for i, smp in enumerate(self.samplers):
            res.append("  %3d│%4d│%s" % (
                i, smp['slot'], smp['data']))

        # Dump mat param list
        res.append("Material Parameters:")
        for name, val in self.materialParams.items():
            res.append("  %-45s: %4s" % (name, val))

        # Dump tex/vtx attrs
        res.append("Texture Attributes: " + (', '.join(self.texAttrs)))
        res.append("Vertex  Attributes: " + (', '.join(self.vtxAttrs)))

        return '\n'.join(res).replace('\n', '\n  ')


    def readFromFRES(self, offset=None):
        """Read this object from given file."""
        if offset is None: offset = self.fres.file.tell()
        log.debug("Reading FMAT from 0x%06X", offset)
        self.headerOffset = offset
        self.header = self.fres.read(Header(), offset)
        self.name   = self.header['name']

        self._readDicts()
        self._readRenderParams()
        self._readShaderParams()
        self._readTextureList()
        self._readSamplerList()
        self._readShaderAssign()

        return self


    def _readDicts(self):
        """Read the dicts."""
        dicts = ('render_param', 'sampler', 'shader_param', 'user_data')
        for name in dicts:
            offs = self.header[name + '_dict_offs']
            if offs: data = self._readDict(offs, name)
            else:    data = None
            setattr(self, name + '_dict', data)


    def _readDict(self, offs, name):
        """Read a Dict."""
        d = Dict(self.fres).readFromFRES(offs)
        return d


    def _readRenderParams(self):
        """Read the render params list."""
        self.renderParams = {}
        types = ('float[2]', 'float', 'str')
        base  = self.header['render_param_offs']

        for i in range(self.header['render_param_cnt']):
            name, offs, cnt, typ, pad = self.fres.read(
                'QQHHI', base + (i*24))
            name = self.fres.readStr(name)

            if pad != 0:
                log.warning("FRES: FMAT Render info '%s' padding=0x%X",
                    name, pad)
            try: typeName = types[typ]
            except IndexError: typeName = '0x%X' % typ

            param = {
                'name':  name,
                'count': cnt,
                'type':  types[typ],
                'vals':  [],
            }
            for j in range(cnt):
                if   typ == 0: val=self.fres.read('2f', offs)
                elif typ == 1: val=self.fres.read('f',  offs)
                elif typ == 2:
                    offs = self.fres.read('Q', offs)
                    val  = self.fres.readStr(offs)
                else:
                    log.warning("FMAT Render param '%s' unknown type 0x%X",
                        name, typ)
                    val = '<unknown>'
                param['vals'].append(val)

            #log.debug("Render param: %-5s[%d] %-32s: %s",
            #    typeName, cnt, name, ', '.join(map(str, param['vals'])))

            if name in self.renderParams:
                log.warning("FMAT: Duplicate render param '%s'", name)
            self.renderParams[name] = param


    def _readShaderParams(self):
        """Read the shader param list."""
        self.shaderParams = {}
        #print("FRES: FMAT Shader params:")

        array_offs = self.header['shader_param_array_offs']
        data_offs  = self.header['shader_param_data_offs']
        for i in range(self.header['shader_param_cnt']):
            # unk0: always 0; unk14: always -1
            # idx0, idx1: both always == i
            unk0, name, type, size, offset, unk14, idx0, idx1 = \
                self.fres.read('QQBBHiHH', array_offs + (i*32))

            name = self.fres.readStr(name)
            type = shaderParamTypes[type]
            if unk0:
                log.debug("Shader param '%s' unk0=0x%X", name, unk0)
            if unk14 != -1:
                log.debug("Shader param '%s' unk14=%d", name, unk14)
            if idx0 != i or idx1 != i:
                log.debug("Shader param '%s' idxs=%d, %d (expected %d)",
                    name, idx0, idx1, i)

            data = self.fres.read(size, data_offs + offset)
            data = struct.unpack(type['fmt'], data)

            #log.debug("%-38s %-5s %s", name, type['name'],
            #    type['outfmt'] % data)

            if name in self.shaderParams:
                log.warning("Duplicate shader param '%s'", name)

            self.shaderParams[name] = {
                'name':   name,
                'type':   type,
                'size':   size,
                'offset': offset,
                'idxs':   (idx0, idx1),
                'unk00':  unk0,
                'unk14':  unk14,
                'data':   data,
            }


    def _readTextureList(self):
        """Read the texture list."""
        self.textures = []
        for i in range(self.header['tex_ref_cnt']):
            offs = self.header['tex_ref_array_offs'] + (i*8)
            offs = self.fres.read('Q', offs)
            name = self.fres.readStr(offs)
            slot = self.fres.read('q',
                self.header['tex_slot_offs'] + (i*8))
            #log.debug("%3d (%2d): %s", i, slot, name)
            self.textures.append({'name':name, 'slot':slot})


    def _readSamplerList(self):
        """Read the sampler list."""
        self.samplers = []
        for i in range(self.header['sampler_cnt']):
            data = self.fres.readHexWords(8,
                self.header['sampler_list_offs'] + (i*32))
            slot = self.fres.read('q',
                self.header['sampler_slot_offs'] + (i*8))
            #log.debug("%3d (%2d): %s", i, slot, data)
            self.samplers.append({'slot':slot, 'data':data})
            # XXX no idea what to do with this data


    def _readShaderAssign(self):
        """Read the shader assign data."""
        assign = ShaderAssign()
        assign = assign.readFromFile(self.fres.file,
            self.header['shader_assign_offs'])
        self.shader_assign = assign

        self.vtxAttrs = []
        for i in range(assign['num_vtx_attrs']):
            offs = self.fres.read('Q', assign['vtx_attr_names']+(i*8))
            name = self.fres.readStr(offs)
            self.vtxAttrs.append(name)

        self.texAttrs = []
        for i in range(assign['num_tex_attrs']):
            offs = self.fres.read('Q', assign['tex_attr_names']+(i*8))
            name = self.fres.readStr(offs)
            self.texAttrs.append(name)

        self.mat_param_dict = self._readDict(
            assign['mat_param_dict'], "mat_params")
        self.materialParams = {}
        #log.debug("material params:")
        for i in range(assign['num_mat_params']):
            name = self.mat_param_dict.nodes[i+1].name
            offs = self.fres.read('Q', assign['mat_param_vals']+(i*8))
            val  = self.fres.readStr(offs)
            #log.debug("%-40s: %s", name, val)
            if name in self.materialParams:
                log.warning("FMAT: duplicate mat_param '%s'", name)
            if name != '':
                self.materialParams[name] = val
