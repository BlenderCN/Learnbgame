try:
    from MDLIO_ByteIO import ByteIO
    from Source2.Blocks.Dummy import Dummy
    from Source2.Blocks.Header import InfoBlock
    from Source2.ValveFile import ValveFile
    from Source2.Blocks.BinaryKeyValue import BinaryKeyValue
except:
    from ...MDLIO_ByteIO import ByteIO
    from .Dummy import Dummy
    from .Header import InfoBlock
    from ..ValveFile import ValveFile
    from .BinaryKeyValue import BinaryKeyValue


class DATA(Dummy):
    def __init__(self, valve_file: ValveFile):
        self.valve_file = valve_file
        self.data = {}
        self.info_block = None

    def read(self, reader: ByteIO, block_info: InfoBlock = None):
        self.info_block = block_info
        with reader.save_current_pos():
            fourcc = reader.read_bytes(4)
        if tuple(fourcc) == (0x56, 0x4B, 0x56, 0x03):
            kv = BinaryKeyValue(self.info_block)
            kv.read(reader)
            self.data = kv.kv
        else:
            for struct in self.valve_file.nrto.structs[:1]:
                self.data[struct.name] = struct.read_struct(reader)
