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
This script exports a Mesh to an Ogre XML triangle format file.

Based fairly heavily on the export_raw file from the blender 2.57 distribution.

Usage:
Execute this script from the "File->Export" menu. You can select
whether modifiers should be applied and if the mesh is triangulated.

"""

import bpy

# this can stay
def faceToTriangles( face ):
    triangles = []
    if ( len( face ) == 4 ): # the face is a quad
        triangles.append( [ face[0], face[1], face[2] ] )
        triangles.append( [ face[2], face[3], face[0] ] )
    else:
        triangles.append( face )

    return triangles

# this can stay
def faceValues( face, mesh, matrix ):
    fv = []
    for verti in face.vertices:
        fv.append( mesh.vertices[verti].co * matrix )
    return fv

def faceToXml( face ):
    v_ids = face['vertex_ids']
    line = "\t\t\t\t<face v1=\"" + str( v_ids[0] ) + "\" v2=\"" + str( v_ids[1] ) + "\" v3=\"" + str( v_ids[2] ) + "\" />\n"
    return line

def vertexToXml( vertex_data ):
    vertex = vertex_data['vertex']
    normal = vertex_data['normal']
    line = "\t\t\t\t\t<vertex>\n"
    line += "\t\t\t\t\t\t<position x=\"" + str( vertex[0] ) + "\" y=\"" + str( vertex[1] ) + "\" z=\"" + str( vertex[2] ) + "\" />\n"
    line += "\t\t\t\t\t\t<normal x=\"" + str( normal[0] ) + "\" y=\"" + str( normal[1] ) + "\" z=\"" + str( normal[2] ) + "\" />\n"
    line += "\t\t\t\t\t\t<colour_diffuse value=\"1 1 1\" />\n"
    line += "\t\t\t\t\t</vertex>\n"
    return line

def export_ogre_xml( filepath, applyMods ):

    # prepare the data structures
    faces = []
    vertices = []
    vertex_ids = {}
    output_faces = []

    # export the meshes
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':  # there are other types as well
            matrix = obj.matrix_world

            if ( applyMods ):
                # apply transformations/etc before exporting
                mesh = obj.to_mesh( bpy.context.scene, True, "PREVIEW" )
            else:
                mesh = obj.data

            output_faces = []
            for face in mesh.faces:
                material_index = face.material_index
                normal = face.normal
                smooth = face.use_smooth  # FIXME: do something with this.

                face_values = faceValues( face, mesh, matrix )
                triangles = faceToTriangles( face_values )

                for triangle in triangles:
                    cur_vertex_ids = []
                    for vertex in triangle:
                        # create a string ID for this vertex, to eliminate dupes
                        vertex_name = str( vertex[0] ) + "-" + str( vertex[1] ) + "-" + str( vertex[2] ) 
                        # see if that name already exists, i.e. if we have seen this vertex before.
                        # FIXME: do we need this anymore, aka are dupes okay after all?
                        if vertex_name in vertex_ids:
                            vertex_id = vertex_ids[ vertex_name ]
                        else:
                            # ogre mesh xml requires the extra data on the vertices, not on the face
                            vertex_data = {
                                    'vertex': vertex,
                                    'name': vertex_name,
                                    'normal': normal,
                                    'material_index': material_index
                                    };
                            vertices.append( vertex_data )
                            vertex_id = len( vertices ) - 1
                            vertex_ids[ vertex_name ] = vertex_id

                        cur_vertex_ids.append( vertex_id )

                    # build the output data structure for this face
                    # don't actually need this, as it turns out :(
                    output_face = {
                            'normal': normal,
                            'material_index': material_index,
                            'vertex_ids': cur_vertex_ids
                            };

                    # push the triangles onto the main faces list.
                    output_faces.append( output_face )

            #for material in mesh.materials:

    faces_xml = ""
    for output_face in output_faces:
        faces_xml += faceToXml( output_face )

    vertices_xml = ""
    for vertex_data in vertices:
        vertices_xml += vertexToXml( vertex_data )

    textures_xml = ""

    template_vars = {
            'num_faces': len( output_faces ), 
            'num_vertices': len( vertices ), 
            'faces_xml': faces_xml, 
            'vertices_xml': vertices_xml,
            'textures_xml': textures_xml 
            }
    # build the output XML file
    output_xml = """<mesh>
    <submeshes>
        <submesh material="Mat01" usesharedvertices="false" use32bitindexes="false" operationtype="triangle_list">
            <faces count="%(num_faces)s">
%(faces_xml)s
            </faces>
            <textures>
%(textures_xml)s
            </textures>
            <geometry vertexcount="%(num_vertices)s">
                <vertexbuffer positions="true" normals="true" colours_diffuse="true">
%(vertices_xml)s
                </vertexbuffer>
            </geometry>
        </submesh>
    </submeshes>
</mesh>
""" % template_vars



    # write the XML to the output file
    file = open( filepath, "w" )
    file.write( output_xml )
    file.close()


from bpy.props import *


class OgreExporter( bpy.types.Operator ):
    '''Save triangle mesh data'''
    bl_idname = "export_mesh.ogrexml"
    bl_label = "Export Ogre XML"

    filepath = StringProperty( name="File Path", description="Filepath used for exporting the Ogre file", maxlen= 1024, default= "", subtype='FILE_PATH' )
    check_existing = BoolProperty( name="Check Existing", description="Check and warn on overwriting existing files", default=True, options={'HIDDEN'} )

    apply_modifiers = BoolProperty( name="Apply Modifiers", description="Use transformed mesh data from each object", default=True )
    triangulate = True

    def execute( self, context ):
        export_ogre_xml( self.filepath, self.apply_modifiers )
        return {'FINISHED'}

    def invoke( self, context, event ):
        wm = context.window_manager
        wm.fileselect_add( self )
        return {'RUNNING_MODAL'}

# package manages registering on import.
