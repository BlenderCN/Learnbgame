"""
 Kristalli data serialization.

 see http://clb.demon.fi/knet/_immediate_mode_serialization.html
"""
import struct

class KristalliData(object):
    """
    Kristalli binary data
    """
    def __init__(self, data):
        self._data = data
        self._idx = 0
        self._dyn_matrix = {}
        self._dyn_matrix[8] = self.get_u8
        self._dyn_matrix[16] = self.get_u16
        self._dyn_matrix[32] = self.get_u32

    def fill(self, size):
        """
        Fill with zeros up to the specified size
        """
        remaining = size - (len(self._data) - self._idx)
        if remaining >= 0:
            self._data += b'\0'*remaining

    @staticmethod
    def encode_ve16(num):
        """
        Encode a number into VLE-1.7/1.7/16
        """
        if num < 128:
            return struct.pack("<B", num)
        elif num < 16384:
            c = (num & 127) | 128
            b = num>>7
            encoded = struct.pack("<B", c) + struct.pack("<B", b)
            return encoded
        else:
            # XXX TODO
            print("KristalliData:encode_ve16:unimplemented_path")
            encoded = struct.pack("<I", num)
            return encoded

    def get_u8(self):
        """
        Get an 8 bit unsigned integer
        """
        val = struct.unpack('<B', self._data[self._idx:self._idx+1])[0]
        self._idx += 1
        return val

    def get_float(self):
        """
        Get a float
        """
        val = struct.unpack('<f', self._data[self._idx:self._idx+4])[0]
        self._idx += 4
        return val

    def get_u16(self):
        """
        Get a 16 bit unsigned integer
        """
        val = struct.unpack('<H', self._data[self._idx:self._idx+2])[0]
        self._idx += 2
        return val

    def get_u32(self):
        """
        Get a 32 bit unsigned integer
        """
        val = struct.unpack('<I', self._data[self._idx:self._idx+4])[0]
        self._idx += 4
        return val

    def get_s32(self):
        """
        Get a 32 bit signed integer
        """
        val = struct.unpack('<i', self._data[self._idx:self._idx+4])[0]
        self._idx += 4
        return val

    def get_s8(self):
        """
        Get a 8 bit signed integer
        """
        val = self._data[self._idx]
        self._idx += 1
        return val

    def get_dyn_s8(self, dynamic_count):
        """
        Get a dynamic number of 8 bit signed
        at the moment returns raw binary data
        """
        count = self.get_dynamic_count(dynamic_count)
        val = self._data[self._idx:self._idx+count]
        self._idx += count
        return val

    def get_dyn_u8(self, dynamic_count):
        """
        Get a dynamic number of 8 bit unsigned
        at the moment returns raw binary data
        """
        return self.get_dyn_s8(dynamic_count)

    def get_dynamic_count(self, dynamic_count):
        """
        Get the dynamic number with the specified size
        """
        return self._dyn_matrix[dynamic_count]()

    # tundra specific
    def get_transform(self):
        """
        Get a transform (position, rotation, size) as 9 floats
        """
        val = struct.unpack("<fffffffff", self._data[self._idx:self._idx+36])
        self._idx += 36
        return val

    def get_vector4(self):
        """
        Get a vector4 as 4 floats
        """
        val = struct.unpack("<ffff", self._data[self._idx:self._idx+16])
        self._idx += 16
        return val

    def get_vector3(self):
        """
        Get a vector3 as 3 floats
        """
        val = struct.unpack("<fff", self._data[self._idx:self._idx+12])
        self._idx += 12
        return val

    def get_string_list(self, list_count, dynamic_count):
        """
        Get a list of strings
        """
        string_list = []
        nelements = self.get_dynamic_count(list_count)
        for idx in range(nelements):
            string_list.append(self.get_string(dynamic_count))
        return string_list

    def get_string(self, dynamic_count):
        """
        Get a string.
        """
        count = self.get_dynamic_count(dynamic_count)
        end = self._data.find(b'\0', self._idx)
        if not end == -1:
           end = min(end+1, self._idx+count)
        val = self._data[self._idx:end]
        self._idx = end
        return val.strip(b'\0')

    def get_bool(self):
        """
        Get a bool in tundra style (as an int)
        """
        return bool(self.get_u8())


