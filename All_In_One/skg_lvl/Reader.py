from array import array
import os
import struct

BIG_ENDIAN = '>'
LITTLE_ENDIAN = '<'


class Reader():
    """
    Base class for any reader
    Requires a file that supplies bytes when using .read() (mode 'rb')
    # plan: read float / read boolean / read arrays of x
    # plan: read string (set encoding/null terminated/pascal ==> always contains a maximum of bytes read and raise
    # later:
    # helper: set_bit in a given byte (a single one) / endianess swapper for all built in types
    # match_bitmask
    """

    def __init__(self, file, file_size, endianness='<'):
        self.current_endianness = endianness
        self.file = file
        self.file_size = file_size
        self.file_position = 0

    def read_string(self, length):
        if length < 0:
            raise ValueError("String length has to be 0 or more")
        return self.file.read(length).decode('ascii')

    def get_bit(self, bit_position=None, single_byte=None):
        if bit_position is None:
            raise ValueError("No bit position given")
        # Get byte if none is supplied
        if single_byte is None:
            single_byte = self.file.read(1)
        return single_byte & (2 ** (bit_position-1)) != 0

    def get_bit_array(self, single_byte=None, lsb=True):
        """
        Returns bit array of a byte with boolean values
        The array is ordered from least significant bit to most signifcant bit
        :param single_byte: The byte to split
        :return: boolean array containing bit values
        """
        # Get byte if none is supplied
        if single_byte is None:
            single_byte = self.file.read(1)

        # For each bit in the byte the value is converted to a boolean
        result_list = []
        for i in range(0, 8):
            result_list.append((single_byte[0] & (2 ** i)) != 0)
        return result_list if lsb else result_list.reverse()

    @staticmethod
    def bitmask_match(single_int, bitmask):
        # TODO is this a good way to do things?
        """
        True if one or more values match, False otherwise
        :param single_int: The int to compare
        :param bitmask:
        :return:
        """
        if bitmask is None:
            raise ValueError("No bitmask given")
        if single_int & bitmask != 0:
            return True
        return False

    def read_float(self, length_in_bytes=4, endianness=None, source_bytes=None):
        """
        Reads a float or double (IEEE 754)
        :param length_in_bytes: 4 or 8, default 4
        :param endianness: default: attribute current_endianess
        :param source_bytes: Unpack these instead of reading from the file
        :return: float
        """
        if length_in_bytes == 4:
            float_type = 'f'
        elif length_in_bytes == 8:
            float_type = 'd'
        else:
            raise NotImplementedError("Only floats with 4 or 8 bytes are allowed")
        if endianness is None:
            if source_bytes is None:
                return struct.unpack(self.current_endianness + float_type, self.file.read(length_in_bytes))[0]
            else:
                return struct.unpack(self.current_endianness + float_type, source_bytes)[0]
        else:
            if source_bytes is None:
                return struct.unpack(endianness + float_type, self.file.read(length_in_bytes))[0]
            else:
                return struct.unpack(endianness + float_type, source_bytes)[0]

    def read_int(self, length_in_bytes=4, is_signed=False, endianness=None, source_bytes=None):
        """
        Reads an integer, default is 4 bytes, unsigned
        :param length_in_bytes: 1,2,4 or 8 bytes int, default 4
        :param is_signed: Is the int signed?, default False
        :param endianness: default: attribute current_endianness
        :param source_bytes Unpack these instead of reading from the file
        :return: int
        """
        if length_in_bytes == 1:
            integer_type = 'b'
        elif length_in_bytes == 2:
            integer_type = 'h'
        elif length_in_bytes == 4:
            integer_type = 'i'
        elif length_in_bytes == 8:
            integer_type = 'q'
        else:
            raise NotImplementedError("Only Integers with 1,2,4 or 8 bytes for now")

        if not is_signed:
            integer_type = integer_type.capitalize()

        if endianness is None:
            if source_bytes is None:
                return struct.unpack(self.current_endianness + integer_type, self.file.read(length_in_bytes))[0]
            else:
                return struct.unpack(self.current_endianness + integer_type, source_bytes)[0]
        else:
            if source_bytes is None:
                return struct.unpack(endianness + integer_type, self.file.read(length_in_bytes))[0]
            else:
                return struct.unpack(endianness + integer_type, source_bytes)[0]

    # Untested
    def read_int_array(self, elements, int_length_in_bytes=4, is_signed=False, endianness=None):
        return array('i', (self.read_int(int_length_in_bytes, is_signed, endianness) for _ in elements))

    # TODO currently MSB+little endian+unsigned only, make it lsb/big endian/signed too, test it with more values
    def bits_to_int(self, source_bytes, bit_offset, bit_length):
        if bit_length > 8:
            raise ValueError("Bit length must be less or equal 8")
        # Find byte or 2 bytes to read
        bytes_to_read = 2 if (bit_offset % 8) + bit_length > 8 else 1
        extracted_bytes = source_bytes[(bit_offset // 8):(bit_offset // 8 + bytes_to_read)]
        converted_int = self.read_int(bytes_to_read, endianness='>', source_bytes=extracted_bytes)
        # Shift right until on position
        result = converted_int >> ((bytes_to_read * 8) - bit_length - (bit_offset % 8))
        # Only take the bits wanted by applying bitmask
        result &= (2 ** bit_length) - 1
        return result

    def export_files(self, output_description):
        """
        Export filesOld, for details see param
        :raise OSError: A file could not be created properly or reading/writing failed
        :param output_description: Dict, with path string and metadata array in form [[offset,length,path],...]
        :return:
        """
        base_path = output_description['path']
        metadata = output_description['metadata']

        # Make folders to given path (may raise OSError)
        os.makedirs(base_path, exist_ok=True)
        initial_position = self.file.tell()

        for entry in metadata:
            offset = entry[0]
            length_in_bytes = entry[1]
            file_path = os.path.abspath(os.path.join(base_path, entry[2]))

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            self.file.seek(offset, 0)

            if length_in_bytes < 0:
                raise ValueError("Invalid argument")
            with open(file_path, 'wb', 4096) as output_file:
                for _ in range(int(length_in_bytes / 4096)):
                    output_file.write(self.file.read(4096))
                output_file.write(self.file.read(length_in_bytes % 4096))
        self.file.seek(initial_position)

    def skip_bytes(self, amount_of_bytes):
        self.file.seek(self.file.tell()+amount_of_bytes)
