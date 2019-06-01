__author__ = "monkeyman192"
__version__ = "0.5"

from .utils import serialize, pad


class mbinCompiler():
    def __init__(self, NMSstruct, out_name):
        # this is the struct containing all the data that needs to be
        # serialized
        self.struct = NMSstruct
        self.output = open('{}'.format(out_name), 'wb')
        self.list_worker = ListWorker()

    def header(self):
        data = bytearray()
        # return the header bytes (0x60 long)
        data.extend(b'\xDD\xDD\xDD\xDD')        # magic
        data.extend(serialize(2500))               # version
        # TODO: change this to the correct GUID?
        data.extend(pad(b'CUSTOMGEOMETRY', 0x10))      # custom name thing
        template_name = 'c' + '{}'.format(self.struct.name)
        data.extend(pad(template_name.encode('utf-8'), 0x40))     # struct name
        data.extend(b'\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE')
        return data

    def serialize(self):
        # this is the workhorse function.
        # we will keep track of the current location and also the current
        # expected final location
        # so that list data can be placed there
        self.output.write(self.header())
        # add on the size of the struct to know where the current finish is
        self.list_worker['end'] = 0x60 + len(self.struct)
        self.struct.serialize(self.output)
        self.output.close()


class ListWorker():
    def __init__(self, initial_state=(0x60, 0x60)):
        self.curr = initial_state[0]
        self.end = initial_state[1]
        # a list containing queued data that will be serialized once the main
        # struct is done
        self.dataQ = []

    def __call__(self):
        return (self.curr, self.end)

    def __setitem__(self, key, item):
        # only allow keys that are currently in the dict to be set
        if key in self.__dict__:
            self.__dict__[key] = item

    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            raise KeyError


# TODO: redo as tests
if __name__ == "__main__":
    from NMS.classes import TkPhysicsComponentData

    pd = TkPhysicsComponentData()
    mbinc = mbinCompiler(pd, 'newmbin')
    mbinc.serialize()
