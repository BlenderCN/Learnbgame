#!BPY

""" Registration info for Blender menus:
Name: 'OGRE (.mesh.xml)...'
Blender: 236
Group: 'Import'
Tip: 'Import an Ogre-Mesh (.mesh.xml) file.'
"""

'''
__author__ = "Daniel Wickert"
__version__ = "0.4 05/11/05"

__bpydoc__ = """\
This script imports Ogre-Mesh models into Blender.

Supported:<br>
    * multiple submeshes (triangle list)
    * uvs
    * materials (textures only)
    * vertex colours

Missing:<br>
    * submeshes provided as triangle strips and triangle fans
    * materials (diffuse, ambient, specular, alpha mode, etc.)
    * skeletons
    * animations

Known issues:<br>
    * blender only supports a single uv set, always the first is taken
      and only the first texture unit in a material, even if it is not for
      the first uv set.
    * code is a bit hacky in parts.
"""
'''

# Copyright (c) 2005 Daniel Wickert
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

# HISTORY:
#     0.1 04/02/05
#     ------------
#     * initial implementation. single submesh as triangle list, no uvs
#
#     0.2 04/03/05
#     ------------
#     * uv support added
#     * texture loading added
#
#     0.3 04/09/05
#     ------------
#     * multiple submeshes added
#     * scaling added
#     * material parsing (only textures yet)
#     * mesh -> mesh.xml conversion if IMPORT_OGREXMLCONVERTER defined
#     * vertex colours
#
#     0.3.1 04/11/05
#     --------------
#     * stdout output streamlined
#     * missing materials and textures are now handled gracefully
#
#     0.3.1a 04/11/05
#     --------------
#     * Mesh is assigned to a correctly named object and added
#       to the current scene
#
#     0.4. 05/11/05
#     --------------
#     * shared vertices support
#     * multiple texture coordinates in meshes are handled correctly no,
#       but only the first coordinate set is used, since Blender doesn't
#       allow multiple uvs.
#     * only the first texture_unit's texture is used now.
#
#     0.4.1 06/02/05
#     --------------
#     * fixed bug: pathes invalid under linux
#     * fixed bug: shared vertices were duplicated with each submesh
#
#     0.5.0 06/06/05
#     --------------
#     * consistent logging scheme with adjustable log level
#     * render materials
#
#     0.5.1 13/07/05
#     --------------
#     * fixed bug: meshes without normals and texture coords cannot be imported
#
#     0.5.2 12/02/06
#     --------------
#     * fixed bug: multiple blender materials created from one ogre material
#
# TODO: implement a consistent naming scheme:
#       bxxx for blender classes; oxxx for ogre(well, sorta) classes

bl_info = {
    "name": "ogre mesh import",
    "author": "Bartek Skorupa, Greg Zaal",
    "version": (0, 1, 6),
    "blender": (2, 70, 0),
    "location": "File > Import > ogre (.mesh)",
    "description": "import ogre mesh file",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Nodes/Nodes_Efficiency_Tools",
    "category": "Import-Export",
}

__version__ = "1.2.3"

import bpy
import glob
import os
import re
import xml.sax
import xml.sax.handler

import bmesh
import mathutils
from mathutils import Vector


# determines the verbosity of loggin.
#   0 - no logging (fatal errors are still printed)
#   1 - standard logging
#   2 - verbose logging
#   3 - debug level. really boring (stuff like vertex data and verbatim lines)
IMPORT_LOG_LEVEL = 1

IMPORT_SCALE_FACTOR = 1
#IMPORT_OGREXMLCONVERTER = "d:\stuff\Torchlight_modding\orge_tools\OgreXmlConverter.exe"
IMPORT_OGREXMLCONVERTER = "/Users/liyong/Download/OgreCommandLineToolsMac_1.8.0/OgreXmlConverter"
#IMPORT_OGREXMLCONVERTER = "F:\\Projekte\\rastullah\checkout\\rl\\branches\python\dependencies\ogre\Tools\Common\\bin\\release\\OgreXmlConverter.exe"


def log(msg):
    if IMPORT_LOG_LEVEL >= 1: print(msg)

def vlog(msg):
    if IMPORT_LOG_LEVEL >= 2: print(msg)

def dlog(msg):
    if IMPORT_LOG_LEVEL >= 3: print(msg)

class Mesh:
    def __init__(self):
        self.submeshes = []
        self.vertices = []
        self.vertexcolours = []
        self.normals = []
        self.uvs = []
    
class Submesh:
    def __init__(self):
        self.vertices = []
        self.vertexcolours = []
        self.normals = []
        self.faces = []
        self.uvs = []
        self.indextype = ""
        self.materialname = ""
        self.sharedvertices = 0

class Material:
    def __init__(self, name):
        self.name = name
        self.texname = ""
        self.diffuse = (1.0, 1.0, 1.0, 1.0)
        self.ambient = (1.0, 1.0, 1.0, 1.0)
        self.specular = (0.0, 0.0, 0.0, 0.0)
        self.blenderimage = 0
        self.loading_failed = 0

    def getTexture(self):
        """
        if self.blenderimage == 0 and not self.loading_failed:
            try:
                f = file(self.texname, 'r')
                f.close()
                self.blenderimage = Blender.Image.Load(self.texname)
            except IOError, (errno, strerror):
                errmsg = "Couldn't open %s #%s: %s" \
                        % (self.texname, errno, strerror)
                log(errmsg)
                self.loading_failed = 1;
        """     
        return self.blenderimage


class OgreMeshSaxHandler(xml.sax.handler.ContentHandler):
    
    global IMPORT_SCALE_FACTOR
    
    def __init__(self):
        self.mesh = 0
        self.submesh = 0
        self.ignore_input = 0
        self.load_next_texture_coords = 0

    def startDocument(self):
        self.mesh = Mesh()
        
    def startElement(self, name, attrs):
        
        if name == 'sharedgeometry':
            self.submesh = self.mesh

        if name == 'submesh':
            self.submesh = Submesh()
            self.submesh.materialname = attrs.get('material', "")
            self.submesh.indextype = attrs.get('operationtype', "")
            if attrs.get('usesharedvertices') == 'true':
                self.submesh.sharedvertices = 1
        
        if name == 'vertex':
            self.load_next_texture_coords = 1

        if name == 'face' and self.submesh:
            face = (
                int(attrs.get('v1',"")),
                int(attrs.get('v2',"")),
                int(attrs.get('v3',""))
            )
            self.submesh.faces.append(face)
        
        if name == 'position':
            vertex = (
                #Ogre x/y/z --> Blender x/-z/y
                float(attrs.get('x', "")) * IMPORT_SCALE_FACTOR,
                -float(attrs.get('z', "")) * IMPORT_SCALE_FACTOR,
                float(attrs.get('y', "")) * IMPORT_SCALE_FACTOR
            )
            self.submesh.vertices.append(vertex)
               
        if name == 'normal':
            normal = (
                #Ogre x/y/z --> Blender x/-z/y
                float(attrs.get('x', "")),
                -float(attrs.get('z', "")),
                float(attrs.get('y', ""))
            )
            self.submesh.normals.append(normal)
        
        if name == 'texcoord' and self.load_next_texture_coords:
            uv = (
                float(attrs.get('u', "")),
                # flip vertical value, Blender's 0/0 is lower left
                # whereas Ogre's 0/0 is upper left
                1.0 - float(attrs.get('v', ""))
            )
            self.submesh.uvs.append(uv)
            self.load_next_texture_coords = 0

        if name == 'colour_diffuse':
            self.submesh.vertexcolours.append(attrs.get('value', "").split())
            
    def endElement(self, name):
        if name == 'submesh':
            self.mesh.submeshes.append(self.submesh)
            self.submesh = 0


def CreateBlenderMesh(name, mesh, materials):
    #bmesh = Blender.NMesh.GetRaw()
    #bmesh = bpy.data.meshes.new("test")

    # dict matname:blender material
    bmaterials = {}
    bmat_idx = -1

    log("Mesh with %d shared vertices." % len(mesh.vertices))
    vertex_count = len(mesh.vertices)
    
    shareVert = mesh.vertices
    shareNormal = mesh.normals
    shareUV = mesh.uvs

    submesh_count = len(mesh.submeshes)
    vertex_offset = 0
    faces = []
    for j in range(0, submesh_count): 
        submesh = mesh.submeshes[j]
        vert = submesh.vertices
        faces = submesh.faces
        uvs = submesh.uvs

        if submesh.sharedvertices == 1:
            vert = shareVert
            uvs = shareUV

        objmesh = bpy.data.meshes.new("mesh"+str(j))

        obj = bpy.data.objects.new("obj"+str(j), objmesh)
        obj.location = bpy.context.scene.cursor_location
        bpy.context.scene.objects.link(obj)

        objmesh.from_pydata(vert, [], faces)
        objmesh.update(calc_edges=True)

        #obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.mode_set(mode="EDIT")
        #if bpy.context.mode == 'EDIT_MESH':
        #for f in bm.faces:

        #add uv coordinate
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()
        bm.faces.layers.tex.verify()

        for f in bm.faces:
            for l in f.loops:
                luv = l[uv_layer]
                ind = l.vert.index
                luv.uv = Vector(uvs[ind])

        bmesh.update_edit_mesh(me)


        bpy.ops.object.mode_set(mode="OBJECT")
        #bmesh.from_pydata(vert, [], faces)
        #break


    """
    for i in range(0, vertex_count):
        ogre_v = mesh.vertices[i]
        dlog("   vertex %d with XYZ: %f %f %f" %\
                (i, ogre_v[0], ogre_v[1], ogre_v[2]))
        blender_v = Blender.NMesh.Vert(ogre_v[0], ogre_v[1], ogre_v[2])
        
        if len(mesh.normals):
            # Set the normals
            blender_v.no[0] = mesh.normals[i][0]
            blender_v.no[1] = mesh.normals[i][1]
            blender_v.no[2] = mesh.normals[i][2]

        if len(mesh.uvs):
            # Set the sticky per vertex uvs
            blender_v.uvco[0] = mesh.uvs[i][0]
            blender_v.uvco[1] = mesh.uvs[i][1]
            
        bmesh.verts.append(blender_v)
        
    
    submesh_count = len(mesh.submeshes)
    vertex_offset = 0
    for j in range(0, submesh_count):
        submesh = mesh.submeshes[j]
        if materials.has_key(submesh.materialname):
            omat = materials[submesh.materialname]
            bmat = 0
            if (not bmaterials.has_key(omat.name)):
                bmat = create_blender_material(omat)
                bmaterials[submesh.materialname] = bmat
                bmesh.addMaterial(bmat)
            else:
                bmat = bmaterials[submesh.materialname]
            bmat_idx = bmesh.materials.index(bmat)
        else:
            omat = 0
            bmat = 0
            bmat_idx = -1
        log("Submesh %d with %d vertices and %d faces..." % \
                (j, len(submesh.vertices), len(submesh.faces)))
        
        # transfer vertices
        vertex_count = len(submesh.vertices)
        for i in range(0, vertex_count):
            ogre_v = submesh.vertices[i]
            blender_v = Blender.NMesh.Vert(ogre_v[0], ogre_v[1], ogre_v[2])

            if len(submesh.normals):
                # Set the normals
                blender_v.no[0] = submesh.normals[i][0]
                blender_v.no[1] = submesh.normals[i][1]
                blender_v.no[2] = submesh.normals[i][2]

            if len(submesh.uvs):
                # Set the sticky per vertex uvs
                blender_v.uvco[0] = submesh.uvs[i][0]
                blender_v.uvco[1] = submesh.uvs[i][1]
            
            bmesh.verts.append(blender_v)

        # transfer faces
        face_count = len(submesh.faces)
        
        # decide whether to take colours and uvs from shared buffer or
        # from the submesh
        faces = submesh.faces
        if submesh.sharedvertices == 1:
            uvs = mesh.uvs
            vertexcolours = mesh.vertexcolours
        else:
            uvs = submesh.uvs
            vertexcolours = submesh.vertexcolours
            
        for i in range(0, face_count):
            ogre_f = submesh.faces[i]
            
            dlog("face %d : %f/%f/%f" % (i, ogre_f[0], ogre_f[1], ogre_f[1]))
            
            f = Blender.NMesh.Face()
            if omat and omat.getTexture():
                f.mode |= Blender.NMesh.FaceModes['TEX']
                f.image = omat.getTexture()
            if bmat:
                f.materialIndex = bmat_idx

            f.v.append(bmesh.verts[ogre_f[0] + vertex_offset])
            f.v.append(bmesh.verts[ogre_f[1] + vertex_offset])
            f.v.append(bmesh.verts[ogre_f[2] + vertex_offset])
            if len(uvs):
                f.uv.append(uvs[ogre_f[0]])
                f.uv.append(uvs[ogre_f[1]])
                f.uv.append(uvs[ogre_f[2]])
            if len(submesh.vertexcolours):
                f.mode |= Blender.NMesh.FaceModes['SHAREDCOL']
                for k in range(3):
                    col = Blender.NMesh.Col()
                    col.r = int(float(vertexcolours[ogre_f[k]][0])*255.0)
                    col.g = int(float(vertexcolours[ogre_f[k]][1])*255.0)
                    col.b = int(float(vertexcolours[ogre_f[k]][2])*255.0)
                    col.a = 255
                    f.col.append(col)

            bmesh.faces.append(f)
        
        # vertices of the new submesh are appended to the NMesh's vertex buffer
        # this offset is added to the indices in the index buffer, so that
        # the right vertices are indexed
        vertex_offset += vertex_count

        log("done.")
        
    # bmesh.hasVertexUV(len(submesh.uvs))
    # TODO: investigate and fix
    # Why oh why ain't this line working...
    # bmesh.hasFaceUV(len(submesh.uvs))
    # ...have to hard set it.
    bmesh.hasFaceUV(1)
    """

    

    # create the mesh
    #object = Blender.Object.New('Mesh', name)
    #object.link(bmesh)
    return None

def convert_meshfile(filename):
    if IMPORT_OGREXMLCONVERTER != '':
        commandline = IMPORT_OGREXMLCONVERTER + ' "' + filename + '"'
        log("executing %s..." % commandline)
        os.system(commandline)
        log("done.")

'''
def collect_materials(dirname):
    # preparing some patterns
    #    to collect the material name
    matname_pattern = re.compile('^\s*material\s+(.*?)\s*$')
    #    to collect the texture name
    texname_pattern = re.compile('^\s*texture\s+(.*?)\s*$')
    #    to collect the diffuse colour
    diffuse_alpha_pattern = re.compile(\
            '^\s*diffuse\s+([^\s]+?)\s+([^\s]+?)\s+([^\s]+?)\s+([^\s]+).*$')
    diffuse_pattern = re.compile(\
            '^\s*diffuse\s+([^\s]+?)\s+([^\s]+?)\s+([^\s]+).*$')
    #    to collect the specular colour
    specular_pattern = re.compile(\
            '^\s*specular\s+([^\s]+?)\s+([^\s]+?)\s+([^\s]+).*$')

    # the dictionary where to put the materials
    materials = {}

    # for all lines in all material files..
    material_files = glob.glob(dirname + '/*.material')
    material = 0
    for filename in material_files:
        f = file(filename, 'r')
        line_number = 0
        for line in f:
            try:
                line_number = line_number + 1
                dlog("line to be matched: %s" % line)
                
                m = matname_pattern.match(line)
                if m:
                    material = Material(m.group(1))
                    materials[material.name] = material
                    vlog("parsing material %s" % m.group(1))
                m = texname_pattern.match(line)
                # load only the first texture unit's texture
                # TODO change to use the first one using the first uv set
                if m and not material.texname:
                    material.texname = dirname + '/' + m.group(1)
                m = diffuse_alpha_pattern.match(line)
                if not m:
                    m = diffuse_pattern.match(line)
                if m:
                    vlog("    parsing diffuse..")
                    groups = m.groups()
                    r = float(groups[0])
                    g = float(groups[1])
                    b = float(groups[2])
                    #TODO: alpha still untested
                    if len(groups) > 3:
                        a = float(groups[3])
                    else:
                        a = 1.0
                    
                    material.diffuse = (r, g, b, a)
                    vlog("   diffuse: %s" % str(material.diffuse))
                m = specular_pattern.match(line)
                if m:
                    vlog("    parsing specular..")
                    groups = m.groups()
                    r = float(groups[0])
                    g = float(groups[1])
                    b = float(groups[2])
                    
                    material.specular = (r, g, b, 1.0)
                    vlog("   specular: %s" % str(material.specular))
            except Exception, e:
                log("    error parsing material %s in %s on line % d: " % \
                    (material.name, filename, line_number))
                log("        exception: %s" % str(e))
    return materials
 '''           

def create_blender_material(omat):
    '''
    bmat = Blender.Material.New(omat.name)
    bmat.rgbCol = (omat.diffuse[0], omat.diffuse[1], omat.diffuse[2])
    bmat.specCol = (omat.specular[0], omat.specular[1], omat.specular[2])
    bmat.alpha = omat.diffuse[3]

    img = omat.getTexture()
    if img:
        tex = Blender.Texture.New(omat.texname)
        tex.setType('Image')
        tex.setImage(omat.getTexture())

        bmat.setTexture(0, tex, Blender.Texture.TexCo.UV,\
                Blender.Texture.MapTo.COL)
    
    return bmat
    '''
    return None

def fileselection_callback(filename):
    log("Reading mesh file %s..." % filename)
    filename = os.path.expanduser(filename)
    #if fileName:
    #    (shortName, ext) = os.path.splitext(filename)


    # is this a mesh file instead of an xml file?
    if (filename.lower().find('.xml') == -1):
        # No. Use the xml converter to fix this
        log("No mesh.xml file. Trying to convert it from binary mesh format.")
        convert_meshfile(filename)
        filename += '.xml'


    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)

    #dirname = Blender.sys.dirname(filename)
    #basename = Blender.sys.basename(filename)
    
    # parse material files and make up a dictionary: {mat_name:material, ..}
    #materials = collect_materials(dirname)
    
    # prepare the SAX parser and parse the file using our own content handler
    parser = xml.sax.make_parser()   
    handler = OgreMeshSaxHandler()
    parser.setContentHandler(handler)
    parser.parse(open(filename))
    
    # create the mesh from the parsed data and link it to a fresh object
    #scene = Blender.Scene.GetCurrent()
    
    meshname = basename[0:basename.lower().find('.mesh.xml')]
    object = CreateBlenderMesh(meshname, handler.mesh, None)
    #scene.link(object)
    #object.select = True

    log("import completed.")
    
    #Blender.Redraw()

#Blender.Window.FileSelector(fileselection_callback, "Import OGRE", "*.xml")
from bpy.props import *
class IMPORT_OT_OGRE(bpy.types.Operator):
    bl_idname = "import_scene.ogre_mesh"
    bl_description = 'Import from mesh file format (.mesh)'
    bl_label = "Import mesh" +' v.'+ __version__
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'}


    filepath = StringProperty(
            subtype='FILE_PATH',
            )

    def draw(self, context):
        layout0 = self.layout
        #layout0.enabled = False

        #col = layout0.column_flow(2,align=True)
        layout = layout0.box()
        col = layout.column()
        #col.prop(self, 'KnotType') waits for more knottypes
        #col.label(text="import Parameters")
        #col.prop(self, 'replace')
        #col.prop(self, 'new_scene')
        
        #row = layout.row(align=True)
        #row.prop(self, 'curves')
        #row.prop(self, 'circleResolution')

        #row = layout.row(align=True)
        #row.prop(self, 'merge')
        #if self.merge:
        #    row.prop(self, 'mergeLimit')
 
        #row = layout.row(align=True)
        #row.label('na')
        #row.prop(self, 'draw_one')
        #row.prop(self, 'thic_on')

        #col = layout.column()
        #col.prop(self, 'codec')
 
        #row = layout.row(align=True)
        #ow.prop(self, 'debug')
        #if self.debug:
         #   row.prop(self, 'verbose')
         
    def execute(self, context):
        '''
        global toggle, theMergeLimit, theCodec, theCircleRes
        O_Merge = T_Merge if self.merge else 0
        #O_Replace = T_Replace if self.replace else 0
        O_NewScene = T_NewScene if self.new_scene else 0
        O_Curves = T_Curves if self.curves else 0
        O_ThicON = T_ThicON if self.thic_on else 0
        O_DrawOne = T_DrawOne if self.draw_one else 0
        O_Debug = T_Debug if self.debug else 0
        O_Verbose = T_Verbose if self.verbose else 0

        toggle =  O_Merge | O_DrawOne | O_NewScene | O_Curves | O_ThicON | O_Debug | O_Verbose
        theMergeLimit = self.mergeLimit*1e-4
        theCircleRes = self.circleResolution
        theCodec = self.codec
        '''
        #readAndBuildDxfFile(self.filepath)
        fileselection_callback(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}



def menu_func(self, context):
    self.layout.operator(IMPORT_OT_OGRE.bl_idname, text="ogre (.mesh)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()

