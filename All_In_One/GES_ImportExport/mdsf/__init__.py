import struct
import sys

# keys
KEY_SECTION_FRAME = 0
KEY_SECTION_ZERO = 1
KEY_SECTION_HEADER = 2

KEY_DATA_VOLUME = 3
KEY_DATA_TOTALVOLUME = 4
KEY_DATA_TYPE = 5
KEY_DATA_COUNT = 6
KEY_DATA_NAME = 7
KEY_DATA_CONTEXT = 8

KEY_TYPE_UNKNOWN = 0
KEY_TYPE_POSITION = 1
KEY_TYPE_ROTATION = 2
KEY_TYPE_SCALE = 3
KEY_TYPE_POLYGON_CORNER_INDEX = 4
KEY_TYPE_NORMAL = 5
KEY_TYPE_UV_COORDINATES = 6
KEY_TYPE_VERTEX_WEIGHT = 7
KEY_TYPE_CLUSTER = 8  # for points, edges or polygons by setting context parameter
KEY_TYPE_POLYGON_CORNER_INDEXE_AND_NORMAL = 9
KEY_TYPE_VERTEX_COLOR = 10
KEY_TYPE_HARD_SAMPLE = 11  # also for points and edges
KEY_TYPE_CREASE_SAMPLE = 12  # for points and edges
KEY_TYPE_DENSITY = 13  # for volume data
KEY_TYPE_VELOCITY = 14
KEY_TYPE_TEMPERATURE = 15
KEY_TYPE_COLOR = 16

KEY_CONTEXT_UNKNOWN = 0
KEY_CONTEXT_VERTEX = 1
KEY_CONTEXT_POLYGON = 2
KEY_CONTEXT_POLYGON_CORNER = 3
KEY_CONTEXT_EDGE = 4
KEY_CONTEXT_OBJECT = 5
KEY_CONTEXT_STRAND = 6
KEY_CONTEXT_VOLUME = 7

KEY_FORMAT = 31250
KEY_VERSION = 1


def is_python_three():
    return sys.version_info[0] == 3


def code_string(string):  # return array of the string with ascii codes
    if is_python_three():
        return list(string.encode("ascii"))
    else:
        return [ord(s) for s in string.encode("ascii")]


class DataContainer(object):
    def __init__(self, data_array, data_name=None, data_context=KEY_CONTEXT_UNKNOWN, data_type=KEY_TYPE_UNKNOWN):
        self._zero_signature = "<HHH"  # zero section length: 2 + 2 + 2 = 6
        self._zero_key = KEY_SECTION_ZERO
        self._header_key = KEY_SECTION_HEADER
        self._data_name = "" if data_name is None else data_name
        self._is_correct = self._calculate_data_signature(data_array[0])
        self._packer = struct.Struct(self._data_signature)
        self._params_dict = {KEY_DATA_COUNT: len(data_array),
                             KEY_DATA_VOLUME: self._packer.size,
                             KEY_DATA_TOTALVOLUME: len(data_array) * self._packer.size,
                             KEY_DATA_TYPE: data_type,
                             KEY_DATA_CONTEXT: data_context,
                             KEY_DATA_NAME: len(self._data_name)  # if data name has 0 length, then there is no name section in the data
                             }
        self._params_count = len(self._params_dict)  # data contains 4 default parameters: data name, number of records, length, total length, data type (vertex position, polygon indexes and so on)
        self._calc_header_signature()
        self._data = data_array

    def is_correct(self):
        return self._is_correct

    def get_type(self):
        '''Return the key of the data type. 0 is unknown type.
        '''
        if KEY_DATA_TYPE in self._params_dict:
            return self._params_dict[KEY_DATA_TYPE]
        else:
            return KEY_TYPE_UNKNOWN

    def get_context(self):
        '''Return the context key of the data. 0 is unknown context.
        '''
        if KEY_DATA_CONTEXT in self._params_dict:
            return self._params_dict[KEY_DATA_CONTEXT]
        else:
            return KEY_CONTEXT_UNKNOWN

    def get_name(self):
        '''Return the data name.
        '''
        return self._data_name

    def get_data_count(self):
        '''Return the number of data records.
        '''
        return len(self._data)

    def get_data_array(self):
        '''Return the link to the data array.
        '''
        return self._data

    def get_data_element(self, index):
        '''Return the data ercord by specific index.
        '''
        return self._data[index]

    def _calculate_data_signature(self, element):
        '''Current version can store only int and float data
        '''
        types_array = []
        for v in element:
            if isinstance(v, int):
                types_array.append("i")
            elif isinstance(v, float):
                types_array.append("f")
            elif isinstance(v, bool):
                types_array.append("?")
            else:
                self._data_signature = "<"
                return False
        self._data_signature = "<" + "".join(types_array)
        return True

    def _get_section_length(self):
        return 6 + (2 + len(self._data_signature) + 10 * len(self._params_dict)) + len(self._data_name) + self._params_dict[KEY_DATA_TOTALVOLUME]

    def _calc_header_signature(self):
        self._header_signature = "<H" + "".join(["B" for v in self._data_signature]) + "".join(["HQ" for p in self._params_dict])

    def _write_to_file(self, file):
        s_zero = struct.Struct(self._zero_signature)
        file.write(s_zero.pack(self._zero_key, len(self._data_signature), len(self._params_dict)))
        s_header = struct.Struct(self._header_signature)
        array_to_pack = [self._header_key] + code_string(self._data_signature)
        for param_key in self._params_dict.keys():
            array_to_pack.append(param_key)
            array_to_pack.append(self._params_dict[param_key])
        array_to_pack = tuple(array_to_pack)
        file.write(s_header.pack(*array_to_pack))
        if len(self._data_name) > 0:
            s_name = struct.Struct("<" + "".join(["B" for v in self._data_name]))
            # file.write(s_name.pack(*name))
            file.write(s_name.pack(*code_string(self._data_name)))
        # next write the data
        for d in self._data:
            file.write(self._packer.pack(*d))


class FrameContainer(object):
    def __init__(self, start_frame=None, end_frame=None):  # start_frame included, but end_frame excluded
        self._start_frame = start_frame if start_frame is not None else -2147483648
        self._end_frame = end_frame if end_frame is not None else 2147483647
        self._key = KEY_SECTION_FRAME
        self._total_length = 0  # here we only sum data length without current section header
        self._section_signature = "<HiiQ"  # header size is 2 + 4 + 4 + 8 = 18
        self._start_pointer = None  # store the shift in file to the start of the section (after header)
        self._file_path = None  # use it for open it and read data when we need it
        self._evaluated = False  # turn on after evaluating data from the file
        self._datas = []

    def get_frames(self):
        return (self._start_frame, self._end_frame - 1)

    def get_start_frame(self):
        return self._start_frame

    def get_end_frame(self):
        return self._end_frame - 1

    def get_datablocks_count(self):
        '''Return the count of data block in the frame container.
        '''
        return len(self._datas)

    def get_datablock(self, index):
        '''Return the data block with the given index.
        '''
        return self._datas[index]

    def get_datablock_by_type(self, type_key):
        '''Return data block with specific data type. If there are several such blocks, return the first one. If there is no such block return None.
        '''
        for d in self._datas:
            if d.get_type() == type_key:
                return d
        return None

    def get_datablock_by_context_type(self, type_key, context_key):
        '''Return the first data block which match the given type and context.
        '''
        for d in self._datas:
            if d.get_type() == type_key and d.get_context() == context_key:
                return d
        return None

    def get_all_datablocks_by_context_type(self, type_key, context_key):
        '''Return all data blocks which match the given type and context.
        '''
        to_return = []
        for d in self._datas:
            if d.get_type() == type_key and d.get_context() == context_key:
                to_return.append(d)
        return to_return

    def get_data_by_type(self, type_key):
        '''Return data array for the given key
        '''
        data_block = self.get_datablock_by_type(type_key)
        if data_block is not None:
            return data_block.get_data_array()
        else:
            return None

    def get_all_datablocks_by_type(self, type_key):
        '''Return all blcoks as array with gove data type. Can be used for obtain all uv-ccordinates data or clusters
        '''
        to_return = []
        for d in self._datas:
            if d.get_type() == type_key:
                to_return.append(d)
        return to_return

    def get_datablock_name(self, index):
        '''Return the name of the given data block
        '''
        return self._datas[index].get_name()

    def add_data(self, data_array, data_name=None, data_context=KEY_CONTEXT_UNKNOWN, data_type=KEY_TYPE_UNKNOWN):
        '''Add data to the container
        '''
        # check is data exist and correct - array of tuples. Signature will be defined by the first element
        if len(data_array) > 0 and isinstance(data_array[0], tuple):
            new_data = DataContainer(data_array, data_name=data_name, data_context=data_context, data_type=data_type)
            if new_data.is_correct():
                self._datas.append(new_data)
                self._total_length += new_data._get_section_length()
            else:
                print("Data element " + str(data_array[0]) + " contains unsuported type")
        else:
            print("Wrong data array. Use non-empy array of tuples.")

    def _get_header_signature(self, i, j):
        array = ["<", "H"] + ["B"]*i + ["H", "Q"]*j
        return "".join(array)

    def _evaluate_data(self):
        if self._evaluated is False:
            # here we should create datas array by reading file from pointer
            pointer_shift = 0
            with open(self._file_path, "rb") as file:
                while pointer_shift < self._total_length:
                    file.seek(self._start_pointer + pointer_shift)
                    s_zero = struct.Struct("<HHH")
                    # pointer point to the start of 0-section of the first data block
                    zero_bin = file.read(6)  # <-- the size of zero-section
                    zero_data = s_zero.unpack(zero_bin)  # return (1, i, j), wheer i is the length of data signature (with < symbol), j is the number of props pairs
                    # next read header-section
                    header_bin = file.read(2 + zero_data[1] + 10 * zero_data[2])
                    header_signature = self._get_header_signature(zero_data[1], zero_data[2])
                    s_header = struct.Struct(header_signature)
                    header_data = s_header.unpack(header_bin)
                    # decode data signature
                    data_signature = "".join([chr(header_data[i]) for i in range(1, zero_data[1] + 1)])
                    # geather properties to the dictionary
                    props_dict = {}
                    for i in range(zero_data[2]):
                        props_dict[header_data[1 + zero_data[1] + 2 * i]] = header_data[1 + zero_data[1] + 2 * i + 1]
                    # next find properties on this dictionary
                    data_count = props_dict[KEY_DATA_COUNT] if KEY_DATA_COUNT in props_dict.keys() else 0
                    data_volume = props_dict[KEY_DATA_VOLUME] if KEY_DATA_VOLUME in props_dict.keys() else 0
                    data_total_volume = props_dict[KEY_DATA_TOTALVOLUME] if KEY_DATA_TOTALVOLUME in props_dict.keys() else 0
                    data_context = props_dict[KEY_DATA_CONTEXT] if KEY_DATA_CONTEXT in props_dict.keys() else KEY_CONTEXT_UNKNOWN
                    data_type = props_dict[KEY_DATA_TYPE] if KEY_DATA_TYPE in props_dict.keys() else KEY_TYPE_UNKNOWN
                    data_name_length = props_dict[KEY_DATA_NAME] if KEY_DATA_NAME in props_dict.keys() else 0
                    data_name = ""
                    if data_name_length > 0:  # next read data name
                        name_bin = file.read(data_name_length)
                        s_name = struct.Struct("<" + "B"*data_name_length)
                        name_data = s_name.unpack(name_bin)
                        data_name = "".join([chr(name_data[i]) for i in range(len(name_data))])
                    # next read data array
                    data_array = []
                    s_data = struct.Struct(data_signature)
                    for i in range(data_count):
                        data_array.append(s_data.unpack(file.read(data_volume)))
                    # finally create DataContainer
                    new_data = DataContainer(data_array, data_name=data_name, data_context=data_context, data_type=data_type)
                    self._datas.append(new_data)
                    pointer_shift += 6 + data_total_volume + data_name_length + (2 + zero_data[1] + 10 * zero_data[2])
            self._evaluated = True

    def _write_to_file(self, file):
        s = struct.Struct(self._section_signature)
        file.write(s.pack(self._key, self._start_frame, self._end_frame, self._total_length))
        for data in self._datas:
            data._write_to_file(file)

    def _read_from_file(self, header_bin_data, file, file_path):
        # unpuck bin_data by signature
        self._file_path = file_path
        s = struct.Struct(self._section_signature)
        unpack_data = s.unpack(header_bin_data)
        if unpack_data[0] == self._key:
            self._start_frame = unpack_data[1]
            self._end_frame = unpack_data[2]
            self._total_length = unpack_data[3]
            # save pointer to the file
            self._start_pointer = file.tell()
            # we don't read actual data now, we will do it when the host application ask it
            # jamp to the next contaiter
            file.seek(self._total_length, 1)


class MeshSerializer(object):
    def __init__(self, file_path=None):
        self._section_signature = "<HH"  # the size is 2 + 2 = 4. H from 0 to 65 536
        self._section_data = None
        self._containers = []
        self._create_from_file = False
        self._saved_container_indexes = []
        self._is_start_save = False  # turn on if we call save method
        if file_path is None:
            self._section_data = (KEY_FORMAT, KEY_VERSION)  # format id and version
        else:  # we should create serializer from existing file
            with open(file_path, "rb") as file:
                self._create_from_file = True
                bin_data = file.read(4)  # read first 4 bytes with version number
                s = struct.Struct(self._section_signature)
                self._section_data = s.unpack(bin_data)
                if self._section_data[0] == KEY_FORMAT and self._section_data[1] == KEY_VERSION:  # this is valid version, read file data
                    # read headers for each container here, but recognize it in FrameContainer class. Each container header has 18 bytes
                    is_finish = False
                    while not is_finish:
                        cont_bin_data = file.read(18)  # <-- this is the size of header for description (frame section)
                        if len(cont_bin_data) < 18:  # if we read less than it should be, breake it.
                            is_finish = True
                        else:
                            new_frame_container = FrameContainer()
                            new_frame_container._read_from_file(cont_bin_data, file, file_path)
                            self._containers.append(new_frame_container)

    def evaluate_all(self):
        '''Fill all frame containers by corresponding data.
        '''
        if self._create_from_file is True:
            for c in self._containers:
                c._evaluate_data()

    def create_container_frames(self, start_frame=None, end_frame=None):
        '''Simply create the link to the container and return it. This method does not fill any data.
        '''
        new_container = FrameContainer(start_frame, end_frame)
        self._containers.append(new_container)
        return new_container

    def create_container(self, frame=None):
        '''Create container only for one frame and return it. This method does not fill any data.
        '''
        if frame is not None:
            return self.create_container_frames(frame, frame + 1)
        else:
            return self.create_container_frames()

    def get_frame_container(self, frame):
        '''Return the frame continer, which contains data for the specific frame.
        '''
        for container in self._containers:
            frames = container.get_frames()
            if frame >= frames[0] and frame < frames[1] + 1:
                # evaluate data in this container
                container._evaluate_data()
                return container
        return None

    def get_existed_frames(self):
        '''Return frame intervals as array of pairs [(start1, finish1), (start2, finish2), ...]
        '''
        return [c.get_frames() for c in self._containers]

    def get_minimal_frame(self):
        '''Return minimal frame in all containers
        '''
        return min([c.get_start_frame() for c in self._containers])

    def get_maximal_frame(self):
        '''Return maximal frame in all containers
        '''
        return max([c.get_end_frame() for c in self._containers])

    def get_containers_count(self):
        '''Return the count of frame containers in the serializer
        '''
        return len(self._containers)

    def save_to_file(self, file_path, additive=False):
        '''Save data in all containers to the file. If additive=True then add to the end of this file only new data (since last record call)
        '''
        with open(file_path, (("a" if self._is_start_save else "w") if additive else "w") + "b") as file:
            if (self._is_start_save is False) or (additive is False):
                s = struct.Struct(self._section_signature)
                file.write(s.pack(*self._section_data))
                self._is_start_save = True
            for container_index in range(len(self._containers)):
                if (not (container_index in self._saved_container_indexes)) or (additive is False):
                    self._containers[container_index]._write_to_file(file)
                    self._saved_container_indexes.append(container_index)


# -----------------------------------------------
# ------------------Examples---------------------
# -----------------------------------------------

def example_read_data(file_path):
    read_doc = MeshSerializer(file_path)  # create reader
    min_frame = read_doc.get_minimal_frame()  # extract minimal and maximal frames, available in the file
    max_frame = read_doc.get_maximal_frame()
    for select_frame in range(min_frame, max_frame + 1):  # iterate through all available frames
        print("Frame " + str(select_frame) + " ( from " + str(min_frame) + " to " + str(max_frame) + ")")
        container = read_doc.get_frame_container(select_frame)  # get data container for the current frame
        if container is not None:
            blocks_count = container.get_datablocks_count()
            print(" "*4 + "Total data blocks: " + str(blocks_count))
            for b_index in range(blocks_count):  # iterate through blocks
                block = container.get_datablock(b_index)  # get block by index
                # print data of this block
                print(" "*8 + "Block index " + str(b_index))
                print(" "*8 + "Name: " + block.get_name() + ", data type: " + str(block.get_type()) + ", context: " + str(block.get_context()) + ", data count: " + str(block.get_data_count()))
                print(" "*8 + "Data: " + str(block.get_data_array()))
        else:
            print("Data for the frame " + str(select_frame) + " does not exists")


def example_write_data(file_path):
    doc = MeshSerializer()  # create main object to store and write all data
    c1 = doc.create_container(1)  # create the container which will store the data for the frame = 1
    c1.add_data([(0, 0), (1, 1), (2, 2)], data_name="int pairs", data_context=KEY_CONTEXT_UNKNOWN, data_type=KEY_TYPE_UNKNOWN)  # add some data
    c1.add_data([(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)], data_name="float triples", data_context=KEY_CONTEXT_UNKNOWN, data_type=KEY_TYPE_UNKNOWN)  # add another data

    doc.save_to_file(file_path)  # call to save file with all embeded data

    c2 = doc.create_container(2)  # create data container for the frame = 2
    c2.add_data([(3, 3), (4, 4), (5, 5)], data_name="int pairs", data_context=KEY_CONTEXT_UNKNOWN, data_type=KEY_TYPE_UNKNOWN)
    c2.add_data([(3.0, 3.0, 3.0), (4.0, 4.0, 4.0), (5.0, 5.0, 5.0)], data_name="float triples", data_context=KEY_CONTEXT_UNKNOWN, data_type=KEY_TYPE_UNKNOWN)

    doc.save_to_file(file_path, additive=True)  # append to existed file ne data for the frame 2


if __name__ == "__main__":
    example_write_data("example.data")
    example_read_data("example.data")
