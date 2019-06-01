from typing import List

try:
    from Source2.Blocks.Dummy import Dummy
    from Source2.Blocks.Header import InfoBlock
    from Source2.ValveFile import ValveFile
    from Source2.Blocks.REDI_DATA import *
except:
    from .Dummy import Dummy
    from .Header import InfoBlock
    from ..ValveFile import ValveFile
    from .REDI_DATA import *


redi_blocks = [InputDependencies,
               AdditionalInputDependencies,
               ArgumentDependencies,
               SpecialDependencies,
               CustomDependencies,
               AdditionalRelatedFiles,
               ChildResourceList,
               ExtraIntData,
               ExtraFloatData,
               ExtraStringData
               ]


class REDI(Dummy):

    def __init__(self, valve_file:ValveFile):
        self.valve_file = valve_file
        self.blocks = []  # type:List[Dependencies]
        self.info_block = None
    def read(self, reader: ByteIO,block_info:InfoBlock = None):
        self.info_block = block_info
        for redi_block in redi_blocks:
            block = redi_block()
            entry = reader.tell()
            block.offset = reader.read_int32()
            block.size = reader.read_int32()
            with reader.save_current_pos():
                reader.seek(entry + block.offset)
                block.read(reader)
                self.blocks.append(block)
