from typing import List
try:
    from MDLIO_ByteIO import ByteIO
    from Source2.Blocks.Dummy import Dummy
    from Source2.Blocks.Header import InfoBlock
    from Source2.ValveFile import ValveFile
except:
    from ...MDLIO_ByteIO import ByteIO
    from .Dummy import Dummy
    from .Header import InfoBlock
    from ..ValveFile import ValveFile

class RERL(Dummy):
    def __init__(self, valve_file:ValveFile):
        self.valve_file = valve_file
        self.resource_entry_offset = 0
        self.resource_count = 0
        self.resources = []  # type: List[RERLResource]
        self.info_block = None
    def __repr__(self):
        return '<External resources list count:{}>'.format(self.resource_count)

    def print_resources(self):
        for res in self.resources:
            print('\t', res)

    def read(self, reader: ByteIO,block_info:InfoBlock = None):
        self.info_block = block_info
        self.entry = reader.tell()
        self.resource_entry_offset = reader.read_int32()
        self.resource_count = reader.read_int32()
        with reader.save_current_pos():
            reader.seek(self.entry + self.resource_entry_offset)
            for n in range(self.resource_count):
                resource = RERLResource()
                resource.read(reader)
                self.resources.append(resource)


class RERLResource(Dummy):

    def __init__(self):
        self.r_id = 0
        self.resource_name_offset = 0
        self.resource_name = ''

    def __repr__(self):
        return '<External resource "{}">'.format(self.resource_name)

    def read(self, reader: ByteIO):
        self.r_id = reader.read_int64()
        entry = reader.tell()
        self.resource_name_offset = reader.read_int64()
        if self.resource_name_offset:
            self.resource_name = reader.read_from_offset(entry + self.resource_name_offset, reader.read_ascii_string)



