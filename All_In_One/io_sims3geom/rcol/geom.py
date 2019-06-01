'''
Copyright (C) 2018 SmugTomato

Created by SmugTomato

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from .datareader import DataReader
from .datawriter import DataWriter


class Geom:
    """ Handle GEOM data """


    embed_materialtype = {
        0x548394b9: "SimSkin",
        0xcf8a70b4: "SimEyes",
        0x00000000: "None"
    }


    def __init__(self, filedata):
        self.reader = DataReader(filedata)

        self.mergegroup  = None
        self.sortorder   = None
        self.embedded_id = None
        self.mtnf_parms  = None
        self.vertices    = None
        self.triangles   = None
        self.skin_ctrl   = None
        self.bonehashes  = None
        self.tgisets     = None


    @staticmethod
    def from_file(filepath):
        print("Reading .simgeom file...\n")

        try:
            file = open(filepath, "rb")
            filedata = file.read()
            file.close()
        except:
            print("Failed to open file")
            return False
        else:
            return(Geom(filedata))


    def read_data(self, strict=False):
        """
            Read data from GEOM fileself.

            Set 'strict' to 'True' to exit on unexpected TGI values,
            by default it will print a warning, but will continue anyway.
        """
        # <editor-fold> -- HEADER SECTION
        # RCOL Header section
        self.reader.read_int32()     # Version
        self.reader.read_int32()     # Count of Internal Public Chunks
        self.reader.read_int32()     # Index3 (unused)
        self.reader.read_int32()     # ExternalCount

        internalct = self.reader.read_int32()
        # GEOM files have TGI values of 0
        # TGI: Type, Group, Instance
        for _ in range(internalct):
            val = self.reader.read_uint64()
            if val != 0:
                print("Unexpected Instance value at", hex(self.reader.offset))
                print("Expected '0x0', got '", hex(val), "'", sep="")
                if strict:
                    return False

            val = self.reader.read_uint32()
            if val != 0:
                print("Unexpected Resource Type value at", hex(self.reader.offset))
                print("Expected '0x0', got '", hex(val), "'", sep="")
                if strict:
                    return False

            val = self.reader.read_uint32()
            if val != 0:
                print("Unexpected Resource Group values at", hex(self.reader.offset))
                print("Expected '0x0', got '", hex(val), "'", sep="")
                if strict:
                    return False

        for _ in range(internalct):
            self.reader.read_uint32()    # Position of the Chunk (absolute)
            self.reader.read_uint32()    # Size of the Chunk


        # GEOM Data section
        # 0x4d4f4547 'GEOM' in ascii, identifies a GEOM block
        if self.reader.read_uint32() != 0x4d4f4547:
            print("Error, invalid geom file")
            return False

        self.reader.read_uint32()       # GEOM VERSION
        self.reader.read_uint32()       # TGI OFFSET (From after this value)
        self.reader.read_uint32()       # TGI SIZE
        embedded_id = self.reader.read_uint32()
        # </editor-fold> -- END HEADER SECTION


        # <editor-fold> -- MTNF CHUNK
        # Probably important so should be saved as property in Blender
        if embedded_id != 0:
            mtnf_parms = []

            self.reader.read_int32()        # CHUNKSIZE
            self.reader.read_uint32()       # 'MTNF'
            self.reader.read_int32()        # UNKNOWN
            self.reader.read_int32()        # DATASIZE

            count = self.reader.read_int32()
            for _ in range(count):
                parm = {
                    'hash'      :None,
                    'typecode'  :None,
                    'size'      :None,
                    'offset'    :None,
                    'data'      :None
                }
                parm['hash'] = hex(self.reader.read_uint32())
                parm['typecode'] = self.reader.read_int32()
                parm['size'] = self.reader.read_int32()
                parm['offset'] = self.reader.read_int32()
                mtnf_parms.append(parm)

            for p in mtnf_parms:
                # FLOATS
                if p['typecode'] == 1:
                    p['data'] = []
                    for _ in range(p['size']):
                        p['data'].append(self.reader.read_float())
                # INTEGERS
                elif p['typecode'] == 2:
                    p['data'] = []
                    for _ in range(p['size']):
                        p['data'].append(self.reader.read_int32())
                # TEXTURES
                elif p['typecode'] == 4:
                    p['data'] = []
                    for _ in range(p['size']):
                        p['data'].append(self.reader.read_int32())

        mergegroup = self.reader.read_int32()
        sortorder  = self.reader.read_int32()

        vertcount  = self.reader.read_int32()
        fcount     = self.reader.read_int32()

        vertformats = []
        for i in range(fcount):
            _datatype = self.reader.read_int32()
            _subtype  = self.reader.read_int32()
            _byteamount = self.reader.read_byte()
            vertformats.append({
                'datatype'  :_datatype,
                'subtype'   :_subtype,
                'byteamount': _byteamount
            })
        # </editor-fold> -- END MTNF CHUNK


        # <editor-fold> -- VERTEX DATA
        vertices = []
        for i in range(vertcount):
            vert = {
                'id'        :None,
                'position'  :None,
                'normal'    :None,
                'uv'        :None,
                'bone_asn'  :None,
                'bone_wgt'  :None,
                'tangent'   :None,
                'tagval'    :None
            }

            for j in range(fcount):
                type = vertformats[j]['datatype']

                # POSITION
                if type == 1:
                    arr = []
                    for _ in range(3):
                        arr.append( self.reader.read_float() )
                    vert['position'] = arr
                # NORMAL
                elif type == 2:
                    arr = []
                    for _ in range(3):
                        arr.append( self.reader.read_float() )
                    vert['normal'] = arr
                # UV COORDINATES
                elif type == 3:
                    arr = []
                    for _ in range(2):
                        arr.append( self.reader.read_float() )
                    vert['uv'] = arr
                # BONE ASSIGNMENTS
                elif type == 4:
                    arr = []
                    for _ in range(4):
                        arr.append( self.reader.read_byte() )
                    vert['bone_asn'] = arr
                # BONE WEIGHTS
                elif type == 5:
                    arr = []
                    for _ in range(4):
                        arr.append( self.reader.read_float() )
                    vert['bone_wgt'] = arr
                # TANGENT
                elif type == 6:
                    arr = []
                    for _ in range(3):
                        arr.append( self.reader.read_float() )
                    vert['tangent'] = arr
                # TAGVAL
                elif type == 7:
                    arr = []
                    for _ in range(4):
                        arr.append( self.reader.read_byte() )
                    vert['tagval'] = arr
                # VERTEX ID
                elif type == 10:
                    vert['id'] = self.reader.read_int32()

            vertices.append(vert)
            # ENDLOOP
        # ENDLOOP
        # </editor-fold> -- END VERTEX DATA


        # <editor-fold> -- TRIANGLES
        if self.reader.read_int32() != 1:
            print("Unsupported Itemcount at", hex(self.reader.offset))
            return False

        if self.reader.read_byte() != 2:
            print("Unsupported Integer length for face indices at", hex(self.reader.offset))
            return False

        numfacepoints = self.reader.read_int32()
        triangles = []
        for _ in range(int(numfacepoints / 3)):
            tri = []
            for _ in range(3):
                tri.append(self.reader.read_int16())
            triangles.append(tri)
        # </editor-fold> -- END TRIANGLES


        # BONES
        skin_ctrl = self.reader.read_int32()
        bonehash_ct = self.reader.read_int32()
        bonehashes = []
        for _ in range(bonehash_ct):
            bonehashes.append(self.reader.read_uint32())


        # TGI SETS
        tgi_count = self.reader.read_int32()
        tgisets = []
        for _ in range(tgi_count):
            tgi = []
            tgi.append(self.reader.read_uint32())
            tgi.append(self.reader.read_uint32())
            tgi.append(self.reader.read_uint64())
            tgisets.append(tgi)


        self.mergegroup  = mergegroup
        self.sortorder   = sortorder
        self.embedded_id = embedded_id
        self.mtnf_parms  = mtnf_parms
        self.vertices    = vertices
        self.triangles   = triangles
        self.skin_ctrl   = skin_ctrl
        self.bonehashes  = bonehashes
        self.tgisets     = tgisets

        # Return True if nothing failed
        print("Finished at", self.reader.offset, "/", len(self.reader.data))
        del(self.reader)
        return True
