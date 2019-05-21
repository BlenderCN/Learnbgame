import struct

HEADER = (b'\x7f\x7f\x7fz',)

class Util:
    @staticmethod
    def readshort(f):
        chunk = f.read(2)
        return struct.unpack('>H', chunk)[0]

    @staticmethod
    def readuint(f):
        chunk = f.read(4)
        return struct.unpack('>I', chunk)[0]

    @staticmethod
    def readstr(f):
        len = Util.readshort(f)

        chunk = f.read(len)

        return struct.unpack('>%is' % len, chunk)[0].decode('ascii')

    @staticmethod
    def readfloat(f):
        chunk = f.read(4)
        return struct.unpack('>f', chunk)[0]

    @staticmethod
    def readfloatblock(f):
        block_len = Util.readuint(f)
        assert(block_len == 4)

        block_frames = Util.readuint(f)

        floatblocks = []
        for i in range(0, block_frames):
            floatblocks.append(
                (Util.readuint(f), Util.readfloat(f),))

        return floatblocks

class Sequence:
    def __init__(self):
        pass

    def _from_file_joints(self, f, joints_len):
        self.joints = {}

        for i in range(0, joints_len):
            joint = {}

            joint['name'] = Util.readstr(f)
            joint['frames'] = []
            
            data_len = Util.readuint(f)
            assert(data_len == 16)

            frames = Util.readuint(f)

            for ii in range(0, frames):
                joint['frames'].append({
                    'frame': Util.readuint(f),
                    'quat': (Util.readfloat(f), Util.readfloat(f),
                             Util.readfloat(f), Util.readfloat(f))
                })

            self.joints[joint['name']] = joint

    def _from_file_blocks(self, f):
        blocks_len = Util.readuint(f)
        assert(blocks_len > 3)

        self.x_block = Util.readfloatblock(f)
        self.y_block = Util.readfloatblock(f)
        self.z_block = Util.readfloatblock(f)
        
    @staticmethod
    def from_file(filename):
        sequence = Sequence()

        f = open(filename, "rb")

        try:
            chunk = f.read(4)
            assert(any([chunk == h for h in HEADER]))

            sequence.frames = Util.readshort(f)
            sequence.joints_len = Util.readuint(f)
            sequence.model = Util.readstr(f)
            sequence.root = Util.readstr(f)

            sequence._from_file_joints(f, sequence.joints_len)

            sequence._from_file_blocks(f)

        finally:
            f.close()

        return sequence
