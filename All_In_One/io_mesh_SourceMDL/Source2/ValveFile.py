import math
import os.path
import sys
from pathlib import Path
from pprint import pprint
from typing import List, TextIO

try:
    from MDLIO_ByteIO import ByteIO
    from Source2.Blocks.Common import SourceVector
    from Source2.Blocks.Header import CompiledHeader, InfoBlock
except:
    from ..MDLIO_ByteIO import ByteIO
    from .Blocks.Common import SourceVector
    from .Blocks.Header import CompiledHeader, InfoBlock


class ValveFile:

    def __init__(self, filepath):
        try:
            from Source2.Blocks.NTRO import NTRO
            from Source2.Blocks.REDI import REDI
            from Source2.Blocks.RERP import RERL
            from Source2.Blocks.VBIB import VBIB
            from Source2.Blocks.DATA import DATA
        except:
            from .Blocks.NTRO import NTRO
            from .Blocks.REDI import REDI
            from .Blocks.RERP import RERL
            from .Blocks.VBIB import VBIB
            from .Blocks.DATA import DATA

        print('Reading {}'.format(filepath))
        self.reader = ByteIO(path=filepath, copy_data_from_handle=False, )
        self.filepath = Path(filepath)
        self.filename = self.filepath.stem
        self.filepath = os.path.abspath(os.path.dirname(filepath))
        self.header = CompiledHeader()
        self.header.read(self.reader)
        self.blocks_info = []  # type: List[InfoBlock]
        self.rerl = RERL(self)
        self.nrto = NTRO(self)
        self.redi = REDI(self)
        self.vbib = VBIB(self)
        self.data = DATA(self)
        self.available_resources = {}

    def read_block_info(self):
        for n in range(self.header.block_count):
            block_info = InfoBlock()
            block_info.read(self.reader)
            self.blocks_info.append(block_info)
            print(block_info)
            if block_info.block_name == 'RERL':
                with self.reader.save_current_pos():
                    self.reader.seek(block_info.entry + block_info.block_offset)
                    self.rerl.read(self.reader, block_info)
                    # print(self.rerl)
            if block_info.block_name == 'NTRO':
                with self.reader.save_current_pos():
                    self.reader.seek(block_info.entry + block_info.block_offset)
                    self.nrto.read(self.reader, block_info)

            if block_info.block_name == 'REDI':
                with self.reader.save_current_pos():
                    self.reader.seek(block_info.entry + block_info.block_offset)
                    self.redi.read(self.reader, block_info)
                    # print(self.redi)
            if block_info.block_name == 'VBIB':
                with self.reader.save_current_pos():
                    self.reader.seek(block_info.entry + block_info.block_offset)
                    self.vbib.read(self.reader, block_info)
                    # print(self.vbib)
            if block_info.block_name == 'DATA':
                with self.reader.save_current_pos():
                    self.reader.seek(block_info.entry + block_info.block_offset)
                    self.data.read(self.reader, block_info)
                    # pprint(self.data.data)

    def dump_structs(self, file: TextIO):
        file.write('''struct vector2
{
    float x,y
}
struct vector3
{
    float x,y,z
}
struct vector4
{
    float x,y,z,w
}
struct quaternion
{
    float x,y,z,w
}
struct RGB
{
    byte r,g,b
}
''')
        for struct in self.nrto.structs:
            # print(struct)
            # for mem in struct.fields:
                # print('\t', mem)
            file.write(struct.as_c_struct())
            # print(struct.as_c_struct())
        for enum in self.nrto.enums:
            # print(enum)
            # for mem in enum.fields:
            #     print('\t', mem)
            file.write(enum.as_c_enum())
            # print(struct.as_c_struct())

    def dump_resources(self):
        for block in self.rerl.resources:
            pass
            # print(block)
            # for block in self.redi.blocks:
            #     print(block)
            #     for dep in block.container:
            #         print('\t',dep)
            # print(block)
            # for block in self.vbib.vertex_buffer:
            #     for vert in block.vertexes:
            #         print(vert.boneWeight)
            # print(block)

    def check_external_resources(self):
        for block in self.rerl.resources:
            name = os.path.basename(block.resource_name)
            if os.path.exists(os.path.join(self.filepath, name + '_c')):
                self.available_resources[name] = os.path.abspath(os.path.join(self.filepath, name + '_c'))
                print('Found', name)
            else:
                print('Can\'t find', name)


def quaternion_to_euler_angle(w, x, y, z):
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = math.degrees(math.atan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    Y = math.degrees(math.asin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = math.degrees(math.atan2(t3, t4))

    return SourceVector(X, Y, Z)


if __name__ == '__main__':
    # with open('log.log', "w") as f:  # replace filepath & filename
    #     with f as sys.stdout:
            # model = r'../test_data/source2/sniper.vmdl_c'
            # model_path = r'../test_data/source2/victory.vanim_c'
            # model_path = r'../test_data/source2/sniper_lod1.vmesh_c'
            # model = r"F:\PYTHON\io_mesh_SourceMDL\test_data\Source2\Invoker\enchantress_cc033ae4.vseq_c"
            # model = r'../test_data/source2/sniper_model.vmesh_c'
            # model_path = r'../test_data/source2/gordon_at_desk.vmdl_c'
            # model_path = r'../test_data/source2/abaddon_body.vmat_c'

            model = r'../test_data/source2/vr_controller_vive_1_5.vmesh_c'
            # model = r'../test_data/source2/sniper_model.vmorf_c'
            # model_path = r'../test_data/source2/sniper.vphys_c'

            vmdl = ValveFile(model)
            vmdl.read_block_info()
            vmdl.dump_structs(open("structures/{}.h".format(model.split('.')[-1]), 'w'))
            vmdl.dump_resources()
            vmdl.check_external_resources()
            print(vmdl.available_resources)
            print(vmdl.header)
            pprint(vmdl.data.data)
