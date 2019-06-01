# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = ["Jesse van Herk"]
__version__ = '0.1'
__bpydoc__ = """\
This script imports Ogre Mesh XML File format files to Blender.

Usage:
Execute this script from the "File->Import" menu and choose a OgreXml file to
open.

Notes:
Generates the standard verts and faces lists, but without duplicate
verts. Only *exact* duplicates are removed, there is no way to specify a
tolerance.
"""



import bpy

from io_utils import unpack_face_list, unpack_list

# FIXME: this needs to be completely rewritten!

def readMesh( filename, objName ):
    file = open( filename, "rb" )

    def line_to_face( line ):
        # Each triplet is an xyz float
        line_split = []
        try:
            line_split = list( map( float, line.split() ) )
        except:
            return None

        if len( line_split ) == 9: # the face is a triangle
            f1, f2, f3, f4, f5, f6, f7, f8, f9 = line_split
            return [(f1, f2, f3), (f4, f5, f6), (f7, f8, f9)]
        elif len( line_split ) == 12: # the face is a Quad
            f1, f2, f3, f4, f5, f6, f7, f8, f9, A, B, C = line_split
            return [(f1, f2, f3), (f4, f5, f6), (f7, f8, f9), (A, B, C)]
        else:
            return None


    faces = []
    for line in file.readlines():
        face = line_to_face( line )
        if face:
            faces.append( face )

    file.close()

    # Generate verts and faces lists, without duplicates
    verts = []
    coords = {}
    index_tot = 0
    faces_indices = []
    
    for f in faces:
        fi = []
        for i, v in enumerate( f ):
            index = coords.get( v )

            if index is None:
                index = coords[v] = index_tot
                index_tot += 1
                verts.append(v)

            fi.append(index)

        faces_indices.append(fi)

    mesh = bpy.data.meshes.new(objName)
    mesh.from_pydata(verts, [], faces_indices)

    return mesh


def addMeshObj( mesh, objName ):
    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False

    mesh.update()
    mesh.validate()

    nobj = bpy.data.objects.new( objName, mesh )
    scn.objects.link( nobj )
    nobj.select = True

    if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
        scn.objects.active = nobj


from bpy.props import *

class OgreXmlImporter(bpy.types.Operator):
    '''Load OgreXml triangle mesh data'''
    bl_idname = "import_mesh.ogre_xml"
    bl_label = "Import Ogre Xml"

    filepath = StringProperty( name="File Path", description="Filepath used for importing the mesh.xml file", maxlen=1024, default="", subtype='FILE_PATH' )

    def execute( self, context ):

        #convert the filename to an object name
        objName = bpy.path.display_name( self.filepath.split( "\\" )[-1].split( "/" )[-1] )

        mesh = readMesh( self.filepath, objName )
        addMeshObj( mesh, objName )

        return {'FINISHED'}

    def invoke( self, context, event ):
        wm = context.window_manager
        wm.fileselect_add( self )
        return {'RUNNING_MODAL'}

# the package manages registering on import.
