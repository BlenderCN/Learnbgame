# TkGeometryData struct

from collections import OrderedDict
from struct import pack
from .Struct import Struct
from .List import List
from .TkVertexLayout import TkVertexLayout
from ...serialization.utils import serialize, list_header
from ...serialization.formats import write_half, write_int_2_10_10_10_rev


class TkGeometryData(Struct):
    def __init__(self, **kwargs):
        super(TkGeometryData, self).__init__()

        """ Contents of the struct """
        self.data['VertexCount'] = kwargs.get('VertexCount', 0)
        self.data['IndexCount'] = kwargs.get('IndexCount', 0)
        self.data['Indices16Bit'] = kwargs.get('Indices16Bit', 1)
        self.data['CollisionIndexCount'] = kwargs.get('CollisionIndexCount', 0)
        self.data['JointBindings'] = kwargs.get('JointBindings', List())
        self.data['JointExtents'] = kwargs.get('JointExtents', List())
        self.data['JointMirrorPairs'] = kwargs.get('JointMirrorPairs', List())
        self.data['JointMirrorAxes'] = kwargs.get('JointMirrorAxes', List())
        self.data['SkinMatrixLayout'] = kwargs.get('SkinMatrixLayout', List())
        self.data['MeshVertRStart'] = kwargs.get('MeshVertRStart', List())
        self.data['MeshVertREnd'] = kwargs.get('MeshVertREnd', List())
        self.data['BoundHullVertSt'] = kwargs.get('BoundHullVertSt', List())
        self.data['BoundHullVertEd'] = kwargs.get('BoundHullVertEd', List())
        self.data['MeshBaseSkinMat'] = kwargs.get('MeshBaseSkinMat', List())
        self.data['MeshAABBMin'] = kwargs.get('MeshAABBMin', List())
        self.data['MeshAABBMax'] = kwargs.get('MeshAABBMax', List())
        self.data['BoundHullVerts'] = kwargs.get('BoundHullVerts', List())
        self.data['VertexLayout'] = kwargs.get('VertexLayout',
                                               TkVertexLayout())
        self.data['SmallVertexLayout'] = kwargs.get('SmallVertexLayout',
                                                    TkVertexLayout())
        self.data['IndexBuffer'] = kwargs.get('IndexBuffer', List())
        self.data['StreamMetaDataArray'] = kwargs.get('StreamMetaDataArray',
                                                      List())
        """ End of the struct contents"""

    def serialize_list(self, data_name):
        # iterate over a list and serialize each value (assuming it is of a
        # normal type...)
        data = bytearray()
        for val in self.data[data_name]:
            data.extend(serialize(val))
        return data

    def serialize(self, output):
        # list header ending
        lst_end = b'\x01\x00\x00\x00'

        bytes_in_list = 0
        curr_offset = 0xE0

        list_data = OrderedDict()

        if self.data['IndexCount'] % 2 != 0 or self.data['IndexCount'] > 32767:
            # in this case we have an odd number of verts. set the Indices16Bit
            # value to be 0.
            # or we have too many verts to pack it using a half...
            self.data['Indices16Bit'] = 0

        Indices16Bit = self.data['Indices16Bit']

        # this will be a specific serialisation method for this whole struct
        for pname in self.data:
            print(pname)
            if pname in ['VertexCount', 'IndexCount', 'Indices16Bit',
                         'CollisionIndexCount']:
                output.write(pack('<i', self.data[pname]))
            elif pname in ['JointBindings', 'JointExtents', 'JointMirrorPairs',
                           'JointMirrorAxes', 'SkinMatrixLayout']:
                output.write(list_header(0, 0, lst_end))
            elif pname in ['MeshVertRStart', 'MeshVertREnd']:
                length = len(self.data[pname])
                output.write(list_header(curr_offset + bytes_in_list, length,
                                         lst_end))
                bytes_in_list += 4 * length
                curr_offset -= 0x10
                list_data[pname] = self.serialize_list(pname)
            elif pname in ['BoundHullVertSt', 'BoundHullVertEd']:
                # we need to handle this separately so that it goes right
                # before the BoundHullVerts data
                length = len(self.data[pname])
                # *0x10 for each of the 4 byte values, and *2 as there will be
                # equal amounts
                extra_offset = 0x20 * len(self.data['MeshAABBMin'])
                output.write(
                    list_header(curr_offset + bytes_in_list + extra_offset,
                                length, lst_end))
                bytes_in_list += 4 * length
                curr_offset -= 0x10
                # just leave as none for now. Will be overridden later when we
                # look at the MeshAABBMin/Max...
                list_data[pname] = None
                # list_data[pname] = self.serialize_list(pname)
            elif pname == 'MeshBaseSkinMat':
                output.write(list_header(0, 0, lst_end))
                curr_offset -= 0x10
            elif pname in ['MeshAABBMin', 'MeshAABBMax']:
                length = len(self.data[pname])
                # to compensate for the moving of the data earlier
                extra_offset = 8*len(self.data['BoundHullVertSt'])
                output.write(
                    list_header(curr_offset + bytes_in_list - extra_offset,
                                length, lst_end))
                bytes_in_list += 0x10 * length
                curr_offset -= 0x10
                # need to do a bit of a hack here to have the data appear in
                # the mbin in order...
                if pname == 'MeshAABBMin':
                    list_data['BoundHullVertSt'] = self.serialize_list(
                        'MeshAABBMin')
                    list_data['MeshAABBMin'] = self.serialize_list(
                        'BoundHullVertSt')
                elif pname == 'MeshAABBMax':
                    list_data['BoundHullVertEd'] = self.serialize_list(
                        'MeshAABBMax')
                    list_data['MeshAABBMax'] = self.serialize_list(
                        'BoundHullVertEd')
            elif pname == 'BoundHullVerts':
                length = len(self.data[pname])
                print(len)
                output.write(list_header(curr_offset + bytes_in_list, length,
                                         lst_end))
                bytes_in_list += 0x10 * length
                curr_offset -= 0x10
                list_data[pname] = self.serialize_list(pname)
            elif pname in ['VertexLayout', 'SmallVertexLayout']:
                # just pull the data directly
                output.write(pack('<I', self.data[pname].data['ElementCount']))
                output.write(pack('<I', self.data[pname].data['Stride']))
                output.write(bytes(self.data[pname].data['PlatformData']))
                curr_offset -= 0x10
                length = len(self.data[pname].data['VertexElements'])
                output.write(list_header(curr_offset + bytes_in_list, length,
                                         lst_end))
                bytes_in_list += 0x20 * length
                curr_offset -= 0x10
                list_data[pname] = bytes(
                    self.data[pname].data['VertexElements'])
            elif pname == 'IndexBuffer':
                if Indices16Bit == 0:
                    length = len(self.data[pname])
                else:
                    # this should be an int anyway, but cast to an int so that
                    # we can pack it correctly
                    length = int(len(self.data[pname]) / 2)
                output.write(list_header(curr_offset + bytes_in_list, length,
                                         lst_end))
                curr_offset -= 0x10
                bytes_in_list += 0x4 * length
                data = bytearray()
                if Indices16Bit == 0:
                    for val in self.data['IndexBuffer']:
                        data.extend(pack('<I', val))
                else:
                    for val in self.data['IndexBuffer']:
                        data.extend(pack('<H', val))
                list_data['IndexBuffer'] = data
                # list_data.append(data)
            elif pname in ['VertexStream', 'SmallVertexStream']:
                # total length. With INT_2_10_10_10_REV format normals and
                # verts they are half the size, so this will be int(1.5*~)
                length = int(1.5 * len(self.data[pname]))
                output.write(list_header(curr_offset + bytes_in_list, length,
                                         lst_end))
                curr_offset -= 0x10
                bytes_in_list += length
                data = bytearray()
                # [0, 4, 8, etc up to final point] These are the indexes at
                # which things start
                start_indexes = range(len(self.data[pname]))[0::4]
                # this will keep track of what type of data we are dealing with
                spec = 0
                for start_index in start_indexes:
                    d = self.data[pname][start_index:start_index+4]
                    if spec in [0, 1]:
                        for val in d:
                            # write the half-float representation
                            data.extend(write_half(val))
                    elif spec in [2, 3]:
                        # write the INT_2_10_10_10_REV representation
                        data.extend(write_int_2_10_10_10_rev(d))
                    if pname == 'VertexStream':
                        spec = (spec + 1) % 4
                    elif pname == 'SmallVertexStream':
                        spec = (spec + 1) % 2
                """
                for val in self.data[pname]:
                    data.extend(binary16(val))
                """
                list_data[pname] = data
            elif pname == 'StreamMetaDataArray':
                length = len(self.data[pname])
                output.write(list_header(curr_offset + bytes_in_list, length,
                                         lst_end))
                curr_offset -= 0x10
                bytes_in_list += 0x98 * length
                list_data[pname] = bytes(self.data[pname])
            elif 'Padding' in pname:
                self.data[pname].serialize(output)
        for data in list_data.keys():
            output.write(list_data[data])
