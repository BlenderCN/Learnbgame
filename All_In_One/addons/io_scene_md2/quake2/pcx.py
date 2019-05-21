import io
import struct


class Header:
    format = '<4B6H48BxB4H54x'
    size = struct.calcsize(format)

    __slots__ = (
        'identifier',
        'version',
        'encoding',
        'bits_per_pixel',
        'x_start',
        'y_start',
        'x_end',
        'y_end',
        'horizontal_resolution',
        'vertical_resolution',
        'palette',
        'number_of_bit_planes',
        'bytes_per_line',
        'palette_type',
        'horizontal_screen_size',
        'vertical_screen_size'
    )

    def __init__(self,
                 identifier,
                 version,
                 encoding,
                 bits_per_pixel,
                 x_start,
                 y_start,
                 x_end,
                 y_end,
                 horizontal_resolution,
                 vertical_resolution,
                 palette,
                 number_of_bit_planes,
                 bytes_per_line,
                 palette_type,
                 horizontal_screen_size,
                 vertical_screen_size):

        self.identifier = identifier
        self.version = version
        self.encoding = encoding
        self.bits_per_pixel = bits_per_pixel
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end
        self.horizontal_resolution = horizontal_resolution
        self.vertical_resolution = vertical_resolution
        self.palette = palette
        self.number_of_bit_planes = number_of_bit_planes
        self.bytes_per_line = bytes_per_line
        self.palette_type = palette_type
        self.horizontal_screen_size = horizontal_screen_size
        self.vertical_screen_size = vertical_screen_size

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.identifier,
            header.version,
            header.encoding,
            header.bits_per_pixel,
            header.x_start,
            header.y_start,
            header.x_end,
            header.y_end,
            header.horizontal_resolution,
            header.vertical_resolution,
            header.palette,
            header.number_of_bit_planes,
            header.bytes_per_line,
            header.palette_type,
            header.horizontal_screen_size,
            header.vertical_screen_size
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        head = header_struct[:10]
        palette = header_struct[10:58]
        tail = header_struct[58:]

        return Header(*head, palette, *tail)


class Pcx:
    @classmethod
    def read(cls, file):
        def _read_byte():
            return struct.unpack('<B', file.read(1))[0]

        header = Header.read(file)

        image_width = header.x_end - header.x_start + 1
        image_height = header.y_end - header.y_start + 1

        scan_line_length = header.number_of_bit_planes * header.bytes_per_line
        line_padding_size = (header.bytes_per_line * header.number_of_bit_planes) * (8 / header.bits_per_pixel) - (header.x_end - header.x_start + 1)

        total = 0
        pixels = b''

        for _ in range(image_height):
            line_buffer = [0,] * scan_line_length
            index = 0

            while index < scan_line_length:
                byte = _read_byte()

                if (byte & 0xC0) == 0xC0:
                    run_count = byte & 0x3F
                    run_value = _read_byte()

                else:
                    run_count = 1
                    run_value = byte

                total += run_count
                while run_count > 0 and index < scan_line_length:
                    line_buffer[index] = run_value

                    run_count -= 1
                    index += 1

            pixels += bytes(line_buffer)

        end_of_pixels = file.tell()
        rest = file.read()
        palette = rest[-768:]

        pcx = Pcx()
        pcx.header = header
        pcx.pixels = pixels
        pcx.palette = palette
        pcx.width = image_width
        pcx.height = image_height

        return pcx
