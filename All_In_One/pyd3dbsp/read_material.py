import struct
import os
import re

from collections import namedtuple

"""
MTLHeader type definition. Used to store header information.

Fields:
-------
mtl_name_ofs        - unsigned integer  - material name offset
colormap_name_ofs   - unsigned integer  - colormap name offset
mapinfoblock_number - unsigned short    - number of MapInfoBlocks represented in file
mtl_type_ofs        - unsigned integer  - material type offset
mapinfoblock_ofs    - unsigned integer  - offset to first MapInfoBlock
-------

"""
MTLHeader = namedtuple('MTLHeader',
    ('mtl_name_ofs, colormap_name_ofs,'
    'mapinfoblock_number, mtl_type_ofs,'
    'mapinfoblock_ofs')
    )
fmt_MTLHeader = '<II44xH2xII8x' # MTLHeader format

"""
MTLMapInfoBlock type definition. Used to store map (texture) information.

Fields:
-------
first_ofs   - unsigned integer - Offset to first string
second_ofs  - unsigned integer - Offset to second string
-------

"""
MTLMapInfoBlock = namedtuple('MTLMapInfoBlock', 'first_ofs, second_ofs')
fmt_MTLMapInfoBlock = '<I4xI' # MTLMapInfoBlock format

"""
MTLMapTypes dictionary that defines the types of maps that the material can refer to.
Reason of using dictionary because it is easier to access the value by the key as it is
having the same identifier.
"""
MTLMapTypes = {
    'colorMap' : 'colorMap', 
    'specularMap' : 'specularMap', 
    'normalMap' : 'normalMap', 
    'detailMap' : 'detailMap'
    }

class MTL:
    """
    MTL class for reading and storing necessary information about Call of Duty 2 material files.
    """

    def __init__(self):
        """
        Class constructor to initialize the class properties.

        Properties:
        -----------
        materialtype    - string        - Type of material
        materialname    - string        - Name of material
        mapinfo         - dictionary    - Dictionary containing map types and names the material uses
        -----------

        """
        self.materialtype = None
        self.materialname = None
        self.mapinfo = {}

    def _read_data(self, file):
        """
        Read all necessary data from the file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        """


        # read header
        file.seek(0)
        header_data = file.read(struct.calcsize(fmt_MTLHeader))
        header = MTLHeader._make(struct.unpack(fmt_MTLHeader, header_data))

        # read material name
        file.seek(header.mtl_name_ofs, os.SEEK_SET)
        _materialname = file.read((header.colormap_name_ofs - header.mtl_name_ofs))
        self.materialname = _materialname.decode('utf-8').rstrip('\x00')

        # read material type
        file.seek(header.mtl_type_ofs, os.SEEK_SET)
        _materialtype = file.read((header.mtl_name_ofs - header.mtl_type_ofs))
        self.materialtype = _materialtype.decode('utf-8').rstrip('\x00')
        
        # read mapinfoblocks
        file.seek(header.mapinfoblock_ofs, os.SEEK_SET)
        for i in range(0, header.mapinfoblock_number):

            # we jump to the current mapinfoblock offset
            file.seek((header.mapinfoblock_ofs + (i * struct.calcsize(fmt_MTLMapInfoBlock))), os.SEEK_SET)
            mapinfoblock_data = file.read(struct.calcsize(fmt_MTLMapInfoBlock))
            mapinfoblock = MTLMapInfoBlock._make(struct.unpack(fmt_MTLMapInfoBlock, mapinfoblock_data))

            # if the first offset of the mapinfoblock is bigger than the second we swap them
            if(mapinfoblock.first_ofs > mapinfoblock.second_ofs):
                tmp_ofs = mapinfoblock.first_ofs
                mapinfoblock = mapinfoblock._replace(first_ofs = mapinfoblock.second_ofs)
                mapinfoblock = mapinfoblock._replace(second_ofs = tmp_ofs)
            
            # read the first string of the mapinfoblock (from first offset to second offset)
            file.seek(mapinfoblock.first_ofs)
            str_first = file.read(mapinfoblock.second_ofs - mapinfoblock.first_ofs)
            str_first = str_first.decode('utf-8').rstrip('\x00')

            # since we don't know where the second string ends 
            # we read until we have completely read in a NULL terminated string
            
            # (well technically we could read until the next mapinfoblock's first offset, but then
            # we would have to do a special case for the last mapinfoblock, where we cant measure
            # the length until the next mapinfoblock, since there are no more mapinfoblocks)
            file.seek(mapinfoblock.second_ofs)
            str_second = b''
            c = None
            while(c != b'\x00'):
                c = file.read(1)
                str_second += c
            str_second = str_second.decode('utf-8').rstrip('\x00')

            # material files might contain the map type and name in different order 
            # so we make sure to store the type as key and the name as value
            if(str_first in MTLMapTypes):
                self.mapinfo[str_first] = str_second
            elif(str_second in MTLMapTypes):
                self.mapinfo[str_second] = str_first

    def load_material(self, filepath):
        """
        Load a Call of Duty 2 material file and read all the necessary data from it.

        Parameters:
        -----------
        filepath - string - Path to the file
        -----------

        """

        with open(filepath, 'rb') as file:
            self._read_data(file)

#TODO some error handling so we know if we made some mistakes and/or the file cannot be opened or contains incorrect data