## ***** BEGIN GPL LICENSE BLOCK ***** 
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program; if not, write to the Free Software Foundation, 
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. 
# 
# ***** END GPL LICENCE BLOCK *****
# 
#
# REQUIRED OPTIONS -
# - Make Normals Consistent
# - Remove Doubles
# **********************************
bl_info = {
    "name": "ASCII Scene Exporter",
    "author": "Richard Bartlett, MCampagnini",
    "version": ( 2, 5, 2 ),
    "blender": ( 2, 7, 8 ),
    "api": 36079,
    "location": "File > Export > ASCII Scene Export(.ase)",
    "description": "ASCII Scene Export(.ase)",
    "warning": "",
    "wiki_url": "https://github.com/DarklightGames/io_export_ase",
    "tracker_url": "https://github.com/DarklightGames/io_export_ase/issues",
    "category": "Learnbgame",
}

"""
--  This script is intended to export in the ASE file format for STATIC MESHES ONLY.
--  This script WILL NOT export skeletal meshes, these should be exported using a
--  different file format.

--  More Information at http://code.google.com/p/ase-export-vmc/
--  UDK Thread at http://forums.epicgames.com/threads/776986-Blender-2-57-ASE-export
"""

import os
import bpy
import math
import time

# settings
aseFloat = lambda x: '''{0: 0.4f}'''.format( x )
optionScale = 16.0
optionSubmaterials = False
optionSmoothingGroups = True
optionAllowMultiMats = True

# ASE components
aseHeader = ''
aseScene = ''
aseMaterials = ''
aseGeometry = ''

# Other
matList = []
numMats = 0
currentMatId = 0

#== Error ==================================================================
class Error( Exception ):

    def __init__( self, message ):
        self.message = message
        print( '\n\n' + message + '\n\n' )

#== Header =================================================================
class cHeader:
    def __init__( self ):
        self.comment = "Ascii Scene Exporter v2.51"

    def __repr__( self ):
        return '''*3DSMAX_ASCIIEXPORT\t200\n*COMMENT "{0}"\n'''.format( self.comment )

#== Scene ==================================================================
class cScene:
    def __init__( self ):
        self.filename = bpy.data.filepath
        self.firstframe = 0
        self.lastframe = 100
        self.framespeed = 30
        self.ticksperframe = 160
        self.backgroundstatic = ''.join( [aseFloat( x ) for x in [0.0, 0.0, 0.0]] )
        self.ambientstatic = ''.join( [aseFloat( x ) for x in [0.0, 0.0, 0.0]] )

    def __repr__( self ):
        return '''*SCENE {{\n\t*SCENE_FILENAME "{0}"\
               \n\t*SCENE_FIRSTFRAME {1}\
               \n\t*SCENE_LASTFRAME {2}\
               \n\t*SCENE_FRAMESPEED {3}\
               \n\t*SCENE_TICKSPERFxRAME {4}\
               \n\t*SCENE_BACKGROUND_STATIC {5}\
               \n\t*SCENE_AMBIENT_STATIC {6}\
               \n}}\n'''.format( self.filename, self.firstframe, self.lastframe, self.framespeed, self.ticksperframe, self.backgroundstatic, self.ambientstatic )

#== Materials ==============================================================
class cMaterials:
    def __init__( self ):
        global optionSubmaterials
        global matList
        global numMats

        self.material_list = []

        # Get all of the materials used by non-collision object meshes  
        for object in bpy.context.selected_objects:
            if collisionObject( object ) == True:
                continue
            elif object.type != 'MESH':
                continue
            else:
                print( object.name + ': Constructing Materials' )
                for slot in object.material_slots:
                    # if the material is not in the material_list, add it
                    if self.material_list.count( slot.material ) == 0:
                        self.material_list.append( slot.material )
                        matList.append( slot.material.name )

        self.material_count = len( self.material_list )
        numMats = self.material_count

        # Raise an error if there are no materials found
        if self.material_count == 0:
            raise Error( 'Mesh must have at least one applied material' )
        else:
            if ( optionSubmaterials ):
                self.dump = cSubMaterials( self.material_list )
            else:
                self.dump = cMultiMaterials( self.material_list )

    def __repr__( self ):
        return str( self.dump )
class cMultiMaterials:
    def __init__( self, material_list ):
        self.numMtls = len( material_list )
        # Initialize material information
        self.dump = '''*MATERIAL_LIST {{\
                    \n\t*MATERIAL_COUNT {0}\
                    '''.format( str( self.numMtls ) )

        for index, slot in enumerate( material_list ):
            self.dump += '''\n\t*MATERIAL {0} {{\
                            {1}\
                            \n\t}}'''.format( index, cMaterial( slot ) )

        self.dump += '\n}'

    def __repr__( self ):
        return self.dump
class cSubMaterials:
    def __init__( self, material_list ):
        slot = material_list[0]
        # Initialize material information
        self.dump = '''*MATERIAL_LIST {\
                    \n\t*MATERIAL_COUNT 1\
                    \n\t*MATERIAL 0 {\
                    '''
        self.matDump = ''
        self.name = material_list[0].name
        self.numSubMtls = len( material_list )
        self.diffusemap = cDiffusemap( slot.texture_slots[0] )
        if ( self.numSubMtls > 1 ):
            self.matClass = 'Multi/Sub-Object'
            self.diffuseDump = ''
        else:
            self.matClass = 'Standard'
            self.numSubMtls = 0
            self.diffuseDump = self.diffdump()
        self.ambient = ''.join( [aseFloat( x ) for x in [0.0, 0.0, 0.0]] )
        self.diffuse = ''.join( [aseFloat( x ) for x in slot.diffuse_color] )
        self.specular = ''.join( [aseFloat( x ) for x in slot.specular_color] )
        self.shine = aseFloat( slot.specular_hardness / 511 )
        self.shinestrength = aseFloat( slot.specular_intensity )
        self.transparency = aseFloat( slot.translucency * slot.alpha )
        self.wiresize = aseFloat( 1.0 )
        self.shading = str( material_list[0].specular_shader ).capitalize()
        self.xpfalloff = aseFloat( 0.0 )
        self.xptype = 'Filter'
        self.falloff = 'In'
        self.soften = False
        self.submtls = []
        self.selfillum = aseFloat( material_list[0].emit )

        if ( len( material_list ) > 1 ):
            # Build SubMaterials
            for index, slot in enumerate( material_list ):
                self.matDump += '''\n\t\t*SUBMATERIAL {0} {{\
                                {1}\
                                \n\t\t}}'''.format( index, cMaterial( slot ) )

        self.dump += '''\n\t\t*MATERIAL_NAME "{0}"\
                       \n\t\t*MATERIAL_CLASS "{1}"\
                       \n\t\t*MATERIAL_AMBIENT {2}\
                       \n\t\t*MATERIAL_DIFFUSE {3}\
                       \n\t\t*MATERIAL_SPECULAR {4}\
                       \n\t\t*MATERIAL_SHINE {5}\
                       \n\t\t*MATERIAL_SHINESTRENGTH {6}\
                       \n\t\t*MATERIAL_TRANSPARENCY {7}\
                       \n\t\t*MATERIAL_WIRESIZE {8}\
                       \n\t\t*MATERIAL_SHADING {9}\
                       \n\t\t*MATERIAL_XP_FALLOFF {10}\
                       \n\t\t*MATERIAL_SELFILLUM {11}\
                       \n\t\t*MATERIAL_FALLOFF {12}\
                       \n\t\t*MATERIAL_XP_TYPE {13}\
                       {14}\
                       \n\t\t*NUMSUBMTLS {15}\
                       {16}'''.format( self.name, self.matClass, self.ambient, self.diffuse, self.specular, self.shine, self.shinestrength, self.transparency, self.wiresize, self.shading, self.xpfalloff, self.selfillum, self.falloff, self.xptype, self.diffuseDump, self.numSubMtls, self.matDump )


        self.dump += '\n}'

    def diffdump( self ):
        for x in [self.diffusemap]:
            return x

    def __repr__( self ):
        return self.dump
class cMaterial:
    def __init__( self, slot ):
        self.dump = ''
        self.name = slot.name
        self.matClass = 'Standard'
        self.ambient = ''.join( [aseFloat( x ) for x in [0.0, 0.0, 0.0]] )
        self.diffuse = ''.join( [aseFloat( x ) for x in slot.diffuse_color] )
        self.specular = ''.join( [aseFloat( x ) for x in slot.specular_color] )
        self.shine = aseFloat( slot.specular_hardness / 511 )
        self.shinestrength = aseFloat( slot.specular_intensity )
        self.transparency = aseFloat( slot.translucency * slot.alpha )
        self.wiresize = aseFloat( 1.0 )

        # Material Definition
        self.shading = str( slot.specular_shader ).capitalize()
        self.xpfalloff = aseFloat( 0.0 )
        self.xptype = 'Filter'
        self.falloff = 'In'
        self.soften = False
        self.diffusemap = cDiffusemap( slot.texture_slots[0] )
        self.submtls = []
        self.selfillum = aseFloat( slot.emit )
        self.dump = '''\n\t\t*MATERIAL_NAME "{0}"\
                       \n\t\t*MATERIAL_CLASS "{1}"\
                       \n\t\t*MATERIAL_AMBIENT {2}\
                       \n\t\t*MATERIAL_DIFFUSE {3}\
                       \n\t\t*MATERIAL_SPECULAR {4}\
                       \n\t\t*MATERIAL_SHINE {5}\
                       \n\t\t*MATERIAL_SHINESTRENGTH {6}\
                       \n\t\t*MATERIAL_TRANSPARENCY {7}\
                       \n\t\t*MATERIAL_WIRESIZE {8}\
                       \n\t\t*MATERIAL_SHADING {9}\
                       \n\t\t*MATERIAL_XP_FALLOFF {10}\
                       \n\t\t*MATERIAL_SELFILLUM {11}\
                       \n\t\t*MATERIAL_FALLOFF {12}\
                       \n\t\t*MATERIAL_XP_TYPE {13}\
                       {14}\
                       '''.format( self.name, self.matClass, self.ambient, self.diffuse, self.specular, self.shine, self.shinestrength, self.transparency, self.wiresize, self.shading, self.xpfalloff, self.selfillum, self.falloff, self.xptype, self.diffdump() )

    def diffdump( self ):
        for x in [self.diffusemap]:
            return x

    def __repr__( self ):
        return self.dump
class cDiffusemap:
    def __init__( self, slot ):
        import os
        self.dump = ''
        if slot is None:
            self.name = 'default'
            self.mapclass = 'Bitmap'
            self.bitmap = 'None'
        else:
            self.name = slot.name
            if slot.texture.type == 'IMAGE':
                self.mapclass = 'Bitmap'
                self.bitmap = slot.texture.image.filepath
                if slot.texture.image.has_data:
                    pass
                else:
                    self.bitmap = '\\\\base\\' + self.bitmap.replace( '/', '\\' )
            else:
                self.mapclass = 'Bitmap'
                self.bitmap = 'None'
        self.subno = 1
        self.amount = aseFloat( 1.0 )
        self.type = 'Screen'
        self.uoffset = aseFloat( 0.0 )
        self.voffset = aseFloat( 0.0 )
        self.utiling = aseFloat( 1.0 )
        self.vtiling = aseFloat( 1.0 )
        self.angle = aseFloat( 0.0 )
        self.blur = aseFloat( 1.0 )
        self.bluroffset = aseFloat( 0.0 )
        self.noiseamt = aseFloat( 1.0 )
        self.noisesize = aseFloat( 1.0 )
        self.noiselevel = 1
        self.noisephase = aseFloat( 0.0 )
        self.bitmapfilter = 'Pyramidal'

        self.dump = '''\n\t\t*MAP_DIFFUSE {{\
                       \n\t\t\t*MAP_NAME "{0}"\
                       \n\t\t\t*MAP_CLASS "{1}"\
                       \n\t\t\t*MAP_SUBNO {2}\
                       \n\t\t\t*MAP_AMOUNT {3}\
                       \n\t\t\t*BITMAP "{4}"\
                       \n\t\t\t*MAP_TYPE {5}\
                       \n\t\t\t*UVW_U_OFFSET {6}\
                       \n\t\t\t*UVW_V_OFFSET {7}\
                       \n\t\t\t*UVW_U_TILING {8}\
                       \n\t\t\t*UVW_V_TILING {9}\
                       \n\t\t\t*UVW_ANGLE {10}\
                       \n\t\t\t*UVW_BLUR {11}\
                       \n\t\t\t*UVW_BLUR_OFFSET {12}\
                       \n\t\t\t*UVW_NOUSE_AMT {13}\
                       \n\t\t\t*UVW_NOISE_SIZE {14}\
                       \n\t\t\t*UVW_NOISE_LEVEL {15}\
                       \n\t\t\t*UVW_NOISE_PHASE {16}\
                       \n\t\t\t*BITMAP_FILTER {17}\
                       \n\t\t}}\
                       '''.format( self.name, self.mapclass, self.subno, self.amount, self.bitmap, self.type, self.uoffset, self.voffset, self.utiling, self.vtiling, self.angle, self.blur, self.bluroffset, self.noiseamt, self.noisesize, self.noiselevel, self.noisephase, self.bitmapfilter )

    def __repr__( self ):
        return self.dump

#== Geometry ===============================================================
class cGeomObject:
    def __init__( self, object ):
        print( object.name + ": Constructing Geometry" )
        global optionAllowMultiMats
        global currentMatId

        self.name = object.name
        self.prop_motionblur = 0
        self.prop_castshadow = 1
        self.prop_recvshadow = 1

        if optionAllowMultiMats:
            self.material_ref = 0
        else:
            self.material_ref = currentMatId

        self.nodetm = cNodeTM( object )
        self.mesh = cMesh( object )

        self.dump = '''\n*GEOMOBJECT {{\n\t*NODE_NAME "{0}"\n{1}\n{2}\n\t*PROP_MOTIONBLUR {3}\n\t*PROP_CASTSHADOW {4}\n\t*PROP_RECVSHADOW {5}\n\t*MATERIAL_REF {6}\n}}'''.format( self.name, self.nodetm, self.mesh, self.prop_motionblur, self.prop_castshadow, self.prop_recvshadow, self.material_ref )

    def __repr__( self ):
        return self.dump
class cNodeTM:
    def __init__( self, object ):
        self.name = object.name
        self.inherit_pos = '0 0 0'
        self.inherit_rot = '0 0 0'
        self.inherit_scl = '0 0 0'
        self.tm_row0 = '1.0000 0.0000 0.0000'
        self.tm_row1 = '0.0000 1.0000 0.0000'
        self.tm_row2 = '0.0000 0.0000 1.0000'
        self.tm_row3 = '0.0000 0.0000 0.0000'
        self.tm_pos = '0.0000 0.0000 0.0000'
        self.tm_rotaxis = '0.0000 0.0000 0.0000'
        self.tm_rotangle = '0.0000'
        self.tm_scale = '1.0000 1.0000 1.0000'
        self.tm_scaleaxis = '0.0000 0.0000 0.0000'
        self.tm_scaleaxisang = '0.0000'

        self.dump = '''\t*NODE_TM {{\
                       \n\t\t*NODE_NAME "{0}"\
                       \n\t\t*INHERIT_POS {1}\
                       \n\t\t*INHERIT_ROT {2}\
                       \n\t\t*INHERIT_SCL {3}\
                       \n\t\t*TM_ROW0 {4}\
                       \n\t\t*TM_ROW1 {5}\
                       \n\t\t*TM_ROW2 {6}\
                       \n\t\t*TM_ROW3 {7}\
                       \n\t\t*TM_POS {8}\
                       \n\t\t*TM_ROTAXIS {9}\
                       \n\t\t*TM_ROTANGLE {10}\
                       \n\t\t*TM_SCALE {11}\
                       \n\t\t*TM_SCALEAXIS {12}\
                       \n\t\t*TM_SCALEAXISANG {13}\
                       \n\t}}'''.format( self.name, self.inherit_pos, self.inherit_rot, self.inherit_scl, self.tm_row0, self.tm_row1, self.tm_row2, self.tm_row3, self.tm_pos, self.tm_rotaxis, self.tm_rotangle, self.tm_scale, self.tm_scaleaxis, self.tm_scaleaxisang )

    def __repr__( self ):
        return self.dump
class cMesh:
    def __init__( self, object ):
        bpy.ops.mesh.reveal

        if collisionObject( object ) == False:
            object.data.uv_textures.active_index = 0
            object.data.uv_texture_stencil_index = 0
            self.tvertlist = cTVertlist( object )
            self.numtvertex = self.tvertlist.length
            self.numtvfaces = len( object.data.uv_texture_stencil.data )
            self.tfacelist = cTFacelist( self.numtvfaces )
            self.uvmapchannels = self.uvdump( object )

            # OUTPUT
            self.tvertlist_str = '\n\t\t*MESH_TVERTLIST ' + str( self.tvertlist )
            self.numtvertex_str = '\n\t\t*MESH_NUMTVERTEX ' + str( self.numtvertex )
            self.numtvfaces_str = '\n\t\t*MESH_NUMTVFACES ' + str( self.numtvfaces )
            self.tfacelist_str = '\n\t\t*MESH_TFACELIST ' + str( self.tfacelist )

        else:
            self.tvertlist_str = ''
            self.numtvertex_str = ''
            self.numtvfaces_str = ''
            self.tfacelist_str = ''
            self.uvmapchannels = ''

        self.timevalue = '0'
        self.numvertex = len( object.data.vertices )
        self.numfaces = len( object.data.polygons )
        self.vertlist = cVertlist( object )
        self.facelist = cFacelist( object )

        # Vertex Paint
        if len( object.data.vertex_colors ) > 0:
            self.cvertlist = cCVertlist( object )
            self.numcvertex = self.cvertlist.length
            self.numcvfaces = len( object.data.vertex_colors.data.polygons )
            self.cfacelist = cCFacelist( self.numcvfaces )
            # change them into strings now
            self.cvertlist = '\n{0}'.format( self.cvertlist )
            self.numcvertex = '\n\t\t*MESH_NUMCVERTEX {0}'.format( self.numcvertex )
            self.numcvfaces = '\n\t\t*MESH_NUMCVFACES {0}'.format( self.numcvfaces )
            self.cfacelist = '\n{0}'.format( self.cfacelist )
        else:
            self.cvertlist = ''
            self.numcvertex = ''
            self.numcvfaces = ''
            self.cfacelist = ''

        self.normals = cNormallist( object )

    # get uv layer names for specified object
    def getUVLayerNames( self, object ):
        self.uvLayerNames = []
        obj = object.data
        for uv in obj.uv_textures.keys():
            self.uvLayerNames.append( str( uv ) )

    def uvdump( self, object ):
        self.mappingchannels = ''
        # if there is more than 1 uv layer
        if collisionObject( object ) == False:
            self.getUVLayerNames( object )
            if len( self.uvLayerNames ) > 1:
                # save uv actives
                active_uv = object.data.uv_textures.active_index
                obj = object.data
                activeUV = 0
                for uvname in self.uvLayerNames:
                    if activeUV == 0:
                        activeUV += 1
                        continue
                    obj.uv_textures.active_index = activeUV
                    obj.uv_texture_stencil_index = activeUV
                    self.uvm_tvertlist = cTVertlist( object )
                    self.uvm_numtvertex = self.uvm_tvertlist.length
                    self.uvm_numtvfaces = len( object.data.uv_texture_stencil.data )
                    self.uvm_tfacelist = cTFacelist( self.uvm_numtvfaces )

                    # if len(object.data.vertex_colors) > 0:
                        # self.uvm_cvertlist = cCVertlist(object)
                        # self.uvm_numcvertex = self.uvm_cvertlist.length
                        # self.uvm_numcvfaces = len(object.data.vertex_colors[0].data)
                        # self.uvm_cfacelist = cCFacelist(self.uvm_numcvfaces)

                        # self.uvm_cvertlist = '\n{0}'.format(self.uvm_cvertlist)
                        # self.uvm_numcvertex = '\n\t\t*MESH_NUMCVERTEX {0}'.format(self.uvm_numcvertex)
                        # self.uvm_numcvfaces = '\n\t\t*MESH_NUMCVFACES {0}'.format(self.uvm_numcvfaces)
                        # self.uvm_cfacelist = '\n{0}'.format(self.uvm_cfacelist)
                    # else:
                    self.uvm_numcvertex = ''
                    self.uvm_numcvfaces = ''
                    self.uvm_cvertlist = ''
                    self.uvm_cfacelist = ''

                    # print extra mapping channels
                    self.mappingchannels += '''\n\t\t*MESH_MAPPINGCHANNEL {0} {{\n\t\t\t*MESH_NUMTVERTEX {1}\n\t\t\t*MESH_TVERTLIST {2}\n\t\t*MESH_NUMTVFACES {3}\n\t\t*MESH_TFACELIST {4}{5}{6}{7}{8}\n\t\t}}'''.format( str( activeUV + 1 ), self.uvm_numtvertex, self.uvm_tvertlist, self.uvm_numtvfaces, self.uvm_tfacelist, self.uvm_numcvertex, self.uvm_cvertlist, self.uvm_numcvfaces, self.uvm_cfacelist )
                    activeUV = activeUV + 1

                # restore uv actives
                object.data.uv_textures.active_index = active_uv

        return self.mappingchannels

    # UV textures go AFTER MESH_FACE_LIST
    # MESH_NUMTVERTEX, MESH_TVERTLIST, MESH_NUMTVFACES, MESH_TFACELIST         
    def __repr__( self ):
        temp = '''\t*MESH {{\n\t\t*TIMEVALUE {0}\n\t\t*MESH_NUMVERTEX {1}\n\t\t*MESH_NUMFACES {2}\n\t\t*MESH_VERTEX_LIST {3}\n\t\t*MESH_FACE_LIST {4}{5}{6}{7}{8}{9}{10}{11}{12}{13}\n{14}\n\t}}'''.format( self.timevalue, self.numvertex, self.numfaces, self.vertlist, self.facelist, self.numtvertex_str, self.tvertlist_str, self.numtvfaces_str, self.tfacelist_str, self.numcvertex, self.cvertlist, self.numcvfaces, self.cfacelist, self.uvmapchannels, self.normals )
        return temp
class cVertlist:
    def __init__( self, object ):
        self.vertlist = []
        for data in object.data.vertices:
            temp = cVert( data.index, data.co.to_tuple( 4 ) )
            self.vertlist.append( temp )

    def dump( self ):
        temp = ''
        for x in self.vertlist:
            temp += str( x )
        return temp

    def __repr__( self ):
        return '''{{\n{0}\t\t}}'''.format( self.dump() )
class cVert:
    def __init__( self, index, coord ):
        global optionScale

        self.index = index
        self.x = aseFloat( coord[0] * optionScale )
        self.y = aseFloat( coord[1] * optionScale )
        self.z = aseFloat( coord[2] * optionScale )

    def __repr__( self ):
        return '''\t\t\t*MESH_VERTEX {0} {1} {2} {3}\n'''.format( self.index, self.x, self.y, self.z )
class cFacelist:
    def __init__( self, object ):
        global optionAllowMultiMats
        global matList
        global numMats
        global currentMatId

        self.facelist = []
        sgID = 0

        # Define smoothing groups (if enabled)
        if ( collisionObject( object ) == False ):
            if ( optionSmoothingGroups ):
                self.smoothing_groups = defineSmoothing( self, object )
            else:
                self.smoothing_groups = ''

        for face in object.data.polygons:
            if optionAllowMultiMats:
                if ( collisionObject( object ) == False ):
                    self.matid = matList.index( object.material_slots[face.material_index].material.name )
                else:
                    self.matid = 0
            else:
                self.matid = currentMatId
            if ( collisionObject( object ) == False ):
                if ( optionSmoothingGroups ):
                    for group in self.smoothing_groups:
                        if group.count( face.index ) == 0:
                            continue
                        else:
                            #TODO: Compress sg's
                            index = self.smoothing_groups.index( group )
                            sgID = index % 32

            temp = '''\t\t\t*MESH_FACE {0}: A: {1} B: {2} C: {3} AB: 0 BC: 0 CA: 0 *MESH_SMOOTHING {4} *MESH_MTLID {5}\n'''.format( face.index, face.vertices[0], face.vertices[1], face.vertices[2], sgID, self.matid )
            self.facelist.append( temp )

        if currentMatId < numMats - 1:
            currentMatId += 1
        else:
            currentMatId = 0

    def dump( self ):
        temp = ''
        for x in self.facelist:
            temp = temp + str( x )
        return temp

    def __repr__( self ):
        return '''{{\n{0}\t\t}}'''.format( self.dump() )
class cTVertlist:
    def __init__( self, object ):
        self.vertlist = []

        # update tessface
        mesh = bpy.context.object.data
        mesh.update( calc_tessface = True )
        uv_layers_count = len( object.data.tessface_uv_textures )

        for index, face in enumerate( object.data.tessfaces ):
            if len( object.data.tessface_uv_textures ) == 0:
                raise Error( "Error:  No UV texture data for " + object.name )
            else:
                temp = cTVert( ( index * 3 ), object.data.tessface_uv_textures[object.data.uv_textures.active_index].data[face.index].uv1 )
                self.vertlist.append( temp )
                temp = cTVert( ( index * 3 ) + 1, object.data.tessface_uv_textures[object.data.uv_textures.active_index].data[face.index].uv2 )
                self.vertlist.append( temp )
                temp = cTVert( ( index * 3 ) + 2, object.data.tessface_uv_textures[object.data.uv_textures.active_index].data[face.index].uv3 )
                self.vertlist.append( temp )

        self.length = len( self.vertlist )

    def dump( self ):
        temp = ''
        for x in self.vertlist:
            temp += str( x )
        return temp

    def __repr__( self ):
        return '''{{\n{0}\t\t}}'''.format( self.dump() )
class cTVert:
    def __init__( self, index, coord ):
        self.index = index
        self.u = aseFloat( coord[0] )
        self.v = aseFloat( coord[1] )

    def __repr__( self ):
        return '''\t\t\t*MESH_TVERT {0} {1} {2} 0.0000\n'''.format( self.index, self.u, self.v )
class cTFacelist:
    def __init__( self, facecount ):
        self.facelist = []
        for data in range( facecount ):
            temp = cTFace( data )
            self.facelist.append( temp )

    def dump( self ):
        temp = ''
        for x in self.facelist:
            temp = temp + str( x )
        return temp

    def __repr__( self ):
        return '''{{\n{0}\t\t}}'''.format( self.dump() )
class cTFace:
    def __init__( self, x ):
        self.index = x
        self.vertices = []
        self.vertices.append( x * 3 )
        self.vertices.append( ( x * 3 ) + 1 )
        self.vertices.append( ( x * 3 ) + 2 )

    def __repr__( self ):
        return '''\t\t\t*MESH_TFACE {0} {1} {2} {3}\n'''.format( self.index, self.vertices[0], self.vertices[1], self.vertices[2] )
class cCVertlist:
    def __init__( self, object ):
        self.vertlist = []
        self.index = 0

        # Blender 2.63+
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        object.data.calc_tessface()

        for face in object.data.tessfaces:
            temp = object.data.tessface_vertex_colors[0].data[face.index].color1
            self.vertlist.append( cCVert( self.index, temp ) )
            temp = object.data.tessface_vertex_colors[0].data[face.index].color2
            self.vertlist.append( cCVert( self.index + 1, temp ) )
            temp = object.data.tessface_vertex_colors[0].data[face.index].color3
            self.vertlist.append( cCVert( self.index + 2, temp ) )
            self.index += 3

        self.length = len( self.vertlist )

    def dump( self ):
        temp = ''
        for x in self.vertlist:
            temp = temp + str( x )
        return temp

    def __repr__( self ):
        return '''\t\t*MESH_CVERTLIST {{\n{0}\t\t}}'''.format( self.dump() )
class cCVert:
    def __init__( self, index, temp ):
        self.index = index
        self.r = aseFloat( float( temp[0] ) )
        self.g = aseFloat( float( temp[1] ) )
        self.b = aseFloat( float( temp[2] ) )

    def __repr__( self ):
        return '''\t\t\t*MESH_VERTCOL {0} {1} {2} {3}\n'''.format( self.index, self.r, self.g, self.b )
class cCFacelist:
    def __init__( self, facecount ):
        temp = [0 for x in range( facecount )]
        self.facelist = []
        for index, data in enumerate( temp ):
            self.facelist.append( cCFace( index, data ) )

    def dump( self ):
        temp = ''
        for x in self.facelist:
            temp = temp + str( x )
        return temp

    def __repr__( self ):
        return '''\t\t*MESH_CFACELIST {{\n{0}\t\t}}'''.format( self.dump() )
class cCFace:
    def __init__( self, index, data ):
        self.index = index
        self.vertices = []
        self.vertices.append( index * 3 )
        self.vertices.append( ( index * 3 ) + 1 )
        self.vertices.append( ( index * 3 ) + 2 )

    def __repr__( self ):
        return '''\t\t\t*MESH_CFACE {0} {1} {2} {3}\n'''.format( self.index, self.vertices[0], self.vertices[1], self.vertices[2] )
class cNormallist:
    def __init__( self, object ):
        self.normallist = []
        for face in object.data.polygons:
            self.normallist.append( cNormal( face, object ) )

    def dump( self ):
        temp = ''
        for x in self.normallist:
            temp = temp + str( x )
        return temp

    def __repr__( self ):
        return '''\t\t*MESH_NORMALS {{\n{0}\t\t}}'''.format( self.dump() )
class cNormal:
    def __init__( self, face, object ):
        self.faceindex = face.index
        self.facenormal = [aseFloat( x ) for x in face.normal.to_tuple( 4 )]
        self.vertnormals = []
        for x in face.vertices:
            self.vertnormals.append( [x, [aseFloat( y ) for y in object.data.vertices[x].normal.to_tuple( 4 )]] )

    def __repr__( self ):
        return '''\t\t\t*MESH_FACENORMAL {0} {1} {2} {3}\n\t\t\t\t*MESH_VERTEXNORMAL {4} {5} {6} {7}\n\t\t\t\t*MESH_VERTEXNORMAL {8} {9} {10} {11}\n\t\t\t\t*MESH_VERTEXNORMAL {12} {13} {14} {15}\n'''.format( self.faceindex, self.facenormal[0], self.facenormal[1], self.facenormal[2], self.vertnormals[0][0], self.vertnormals[0][1][0], self.vertnormals[0][1][1], self.vertnormals[0][1][2], self.vertnormals[1][0], self.vertnormals[1][1][0], self.vertnormals[1][1][1], self.vertnormals[1][1][2], self.vertnormals[2][0], self.vertnormals[2][1][0], self.vertnormals[2][1][1], self.vertnormals[2][1][2] )

#== Smoothing Groups and Helper Methods =================================
def defineSmoothing( self, object ):
    print( object.name + ": Constructing Smoothing Groups" )

    seam_edge_list = []
    sharp_edge_list = []

    _mode = bpy.context.scene.objects.active.mode
    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.mesh.select_all( action = 'DESELECT' )
    setSelMode( 'EDGE' )

    # Get seams and clear them
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    for edge in object.data.edges:
        if edge.use_seam:
            seam_edge_list.append( edge.index )
            edge.select = True

    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.mesh.select_all( action = 'SELECT' )
    bpy.ops.mesh.mark_seam( clear = True )

    # Get sharp edges, convert them to seams
    bpy.ops.mesh.select_all( action = 'DESELECT' )
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    for edge in object.data.edges:
        if edge.use_edge_sharp:
            sharp_edge_list.append( edge )
            edge.select = True

    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.mesh.mark_seam()

    bpy.ops.mesh.select_all( action = 'DESELECT' )

    smoothing_groups = []
    face_list = []

    mode = getSelMode( self, False )
    setSelMode( 'FACE' )

    for face in object.data.polygons:
        face_list.append( face.index )

    while len( face_list ) > 0:
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        object.data.polygons[face_list[0]].select = True
        bpy.ops.object.mode_set( mode = 'EDIT' )
        bpy.ops.mesh.select_linked( delimit = {'SEAM'} )

        # TODO - update when API is updated
        selected_faces = getSelectedFaces( self, True )
        smoothing_groups.append( selected_faces )
        for face_index in selected_faces:
            if face_list.count( face_index ) > 0:
                face_list.remove( face_index )
        bpy.ops.mesh.select_all( action = 'DESELECT' )

    setSelMode( mode, False )

    # Clear seams created by sharp edges
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    for edge in object.data.edges:
        if edge.use_seam:
            edge.select = True

    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.mesh.mark_seam( clear = True )

    bpy.ops.mesh.select_all( action = 'DESELECT' )
    # Restore original uv seams
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    for edge_index in seam_edge_list:
        object.data.edges[edge_index].select = True

    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.mesh.mark_seam()

    print( '\t' + str( len( smoothing_groups ) ) + ' smoothing groups found.' )
    return smoothing_groups

#===========================================================================
# // General Helpers
#===========================================================================

# Check if the mesh is a collider
# Return True if collision model, else: false
def collisionObject( object ):
    collisionPrefixes = ['UCX_', 'UBX_', 'USX_']
    for prefix in collisionPrefixes:
        if object.name.find( str( prefix ) ) >= 0:
            return True
    return False

# Set the selection mode    
def setSelMode( mode, default = True ):
    if default:
        if mode == 'VERT':
            bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        elif mode == 'EDGE':
            bpy.context.tool_settings.mesh_select_mode = [False, True, False]
        elif mode == 'FACE':
            bpy.context.tool_settings.mesh_select_mode = [False, False, True]
        else:
            return False
    else:
        bpy.context.tool_settings.mesh_select_mode = mode
        return True
def getSelMode( self, default = True ):
    if default:
        if bpy.context.tool_settings.mesh_select_mode[0] == True:
            return 'VERT'
        elif bpy.context.tool_settings.mesh_select_mode[1] == True:
            return 'EDGE'
        elif bpy.context.tool_settings.mesh_select_mode[2] == True:
            return 'FACE'
        return False
    else:
        mode = []
        for value in bpy.context.tool_settings.mesh_select_mode:
            mode.append( value )

        return mode
def getSelectedFaces( self, index = False ):
    selected_faces = []
    # Update mesh data
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()

    _mode = bpy.context.scene.objects.active.mode
    bpy.ops.object.mode_set( mode = 'EDIT' )

    object = bpy.context.scene.objects.active
    for face in object.data.polygons:
        if face.select == True:
            if index == False:
                selected_faces.append( face )
            else:
                selected_faces.append( face.index )

    bpy.ops.object.mode_set( mode = _mode )

    return selected_faces

#== Core ===================================================================

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, FloatProperty

class ExportAse( bpy.types.Operator, ExportHelper ):
    '''Load an Ascii Scene Export File'''
    bl_idname = "export.ase"
    bl_label = "Export"
    __doc__ = "Ascii Scene Exporter (.ase)"
    filename_ext = ".ase"
    filter_glob = StringProperty( default = "*.ase", options = {'HIDDEN'} )

    filepath = StringProperty( 
        name = "File Path",
        description = "File path used for exporting the ASE file",
        maxlen = 1024,
        default = "" )

    option_triangulate = BoolProperty( 
            name = "Triangulate",
            description = "Triangulates all exportable objects",
            default = True )

    option_normals = BoolProperty( 
            name = "Recalculate Normals",
            description = "Recalculate normals before exporting",
            default = True )

    option_remove_doubles = BoolProperty( 
            name = "Remove Doubles",
            description = "Remove any duplicate vertices before exporting",
            default = True )

    option_apply_scale = BoolProperty( 
            name = "Scale",
            description = "Apply scale transformation",
            default = True )

    option_apply_location = BoolProperty( 
            name = "Location",
            description = "Apply location transformation",
            default = True )

    option_apply_rotation = BoolProperty( 
            name = "Rotation",
            description = "Apply rotation transformation",
            default = True )

    option_smoothinggroups = BoolProperty( 
            name = "Smoothing Groups",
            description = "Construct hard edge islands as smoothing groups",
            default = True )

    option_separate = BoolProperty( 
            name = "Separate",
            description = "A separate ASE file for every selected object",
            default = False )

    option_submaterials = BoolProperty( 
            name = "Use Submaterials (UDK)",
            description = "Export a single material with multiple sub materials",
            default = True )

    option_allowmultimats = BoolProperty( 
            name = "Allow Multiple Materials (UDK)",
            description = "Allow multiple materials per geometry object",
            default = True )

    option_scale = FloatProperty( 
            name = "Scale",
            description = "Object scaling factor (default: 1.0)",
            min = 0.01,
            max = 1000.0,
            soft_min = 0.01,
            soft_max = 1000.0,
            default = 16.0 )

    def draw( self, context ):
        layout = self.layout

        box = layout.box()
        box.label( 'Essentials:' )
        box.prop( self, 'option_triangulate' )
        box.prop( self, 'option_normals' )
        box.prop( self, 'option_remove_doubles' )
        box.label( "Transformations:" )
        box.prop( self, 'option_apply_scale' )
        box.prop( self, 'option_apply_rotation' )
        box.prop( self, 'option_apply_location' )
        box.label( "Materials:" )
        box.prop( self, 'option_submaterials' )
        box.prop( self, 'option_allowmultimats' )
        box.label( "Advanced:" )
        box.prop( self, 'option_scale' )
        box.prop( self, 'option_smoothinggroups' )

    @classmethod
    def poll( cls, context ):
        active = context.active_object
        selected = context.selected_objects
        camera = context.scene.camera
        ok = selected or camera
        return ok

    def writeASE( self, filename, data ):
        print( '\nWriting', filename )
        try:
            file = open( filename, 'w' )
        except IOError:
            print( 'Error: The file could not be written to. Aborting.' )
        else:
            file.write( data )
            file.close()

    def execute( self, context ):
        start = time.clock()

        global optionScale
        global optionSubmaterials
        global optionSmoothingGroups
        global optionAllowMultiMats

        global aseHeader
        global aseScene
        global aseMaterials
        global aseGeometry

        global currentMatId
        global numMats
        global matList

        # Set globals and reinitialize ase components
        aseHeader = ''
        aseScene = ''
        aseMaterials = ''
        aseGeometry = ''

        optionScale = self.option_scale
        optionSubmaterials = self.option_submaterials
        optionSmoothingGroups = self.option_smoothinggroups
        optionAllowMultiMats = self.option_allowmultimats

        matList = []
        currentMatId = 0
        numMats = 0

        # Build ASE Header, Scene
        print( '\nAscii Scene Export by MCampagnini\n' )
        print( 'Objects selected: ' + str( len( bpy.context.selected_objects ) ) )
        aseHeader = str( cHeader() )
        aseScene = str( cScene() )
        aseMaterials = str( cMaterials() )

        # Apply applicable options
        for object in bpy.context.selected_objects:
            if object.type == 'MESH':
                bpy.context.scene.objects.active = object
                object.select = True

                # Options
                bpy.ops.object.mode_set( mode = 'EDIT' )
                if self.option_remove_doubles:
                    bpy.ops.object.mode_set( mode = 'EDIT' )
                    bpy.ops.mesh.select_all( action = 'SELECT' )
                    bpy.ops.mesh.remove_doubles()
                if self.option_triangulate:
                    print( object.name + ': Converting to triangles' )
                    bpy.ops.mesh.select_all( action = 'SELECT' )
                    bpy.ops.mesh.quads_convert_to_tris()
                if self.option_normals:
                    print( object.name + ': Recalculating normals' )
                    bpy.ops.object.mode_set( mode = 'EDIT' )
                    bpy.ops.mesh.select_all( action = 'SELECT' )
                    bpy.ops.mesh.normals_make_consistent()

                # Transformations
                bpy.ops.object.mode_set( mode = 'OBJECT' )
                bpy.ops.object.transform_apply( location = self.option_apply_location, rotation = self.option_apply_rotation, scale = self.option_apply_scale )

                #Construct ASE Geometry Nodes
                aseGeometry += str( cGeomObject( object ) )

            else:
                continue

        aseModel = ''
        aseModel += aseHeader
        aseModel += aseScene
        aseModel += aseMaterials
        aseModel += aseGeometry

        # Write the ASE file
        self.writeASE( self.filepath, aseModel )

        lapse = ( time.clock() - start )
        print( 'Completed in ' + str( lapse ) + ' seconds' )

        return {'FINISHED'}

def menu_func( self, context ):
    self.layout.operator( ExportAse.bl_idname, text = "Ascii Scene Exporter (.ase)" )

def register():
    bpy.utils.register_class( ExportAse )
    bpy.types.INFO_MT_file_export.append( menu_func )

def unregister():
    bpy.utils.unregister_class( ExportAse )
    bpy.types.INFO_MT_file_export.remove( menu_func )

if __name__ == "__main__":
    register()
