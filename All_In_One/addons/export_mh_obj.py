""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
Obj exporter
"""

bl_info = {
    "name": "MakeHuman obj exporter",
    "author": "Thomas Larsson",
    "version": "0.1",
    "blender": (2, 6, 0),
    "api": 40000,
    'location': "File > Import > Export MH OBJ (.obj)",
    'description': 'Export files in OBJ format (.obj). For internal MakeHuman use.',
    'category': 'MakeHuman'}


import bpy, os, mathutils
import math
from mathutils import *
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

#
#   GroupZOrderSuffix
#   Determines the Z-order of face groups.
#   Faces with lower Z-order are exported first
#   Only looks at the last part of the group name
#   Groups not listed have Z-order 0.
#   Faces within a given Z-order are exported with lower face number first.
#   Preferably add new groups with higher Z-order, to not ruin numbering 
#   of existing faces. It is not a disaster to change face numbers, but
#   it does require some changes in MHX export.
#

GroupZOrderSuffix = {
    1: ["lash","eyebrown","cornea"],
    2: ["tights","skirt"]
}

#
#   When materials represent face groups, we must figure out the real materials
#   in some other way. Use this dict.
#   If the group name contains the key string, assign it to the value material.
#   If not, material is "skin".
#
#   Ignored when object has real materials.
#

GroupMaterials = {
    "nail" : "nail", 
    "eye-ball" : "eye", 
    "teeth" : "teeth", 
    "cornea" : "cornea", 
    "joint" : "joint", 
    "skirt" : "joint",
    "tights" : "joint",
}

# Minimal distance for merging tex verts

Epsilon = 1e-4

#
#   exportObjFile(path, groupsAsMaterials, context):
#

def exportObjFile(path, groupsAsMaterials, context):
    ob = context.object
    me = ob.data
    if (not me) or (len(me.materials) < 2):
        raise NameError("Mesh must have materials")
    (name,ext) = os.path.splitext(path)
    if ext.lower() != ".obj":
        path = path + ".obj"
    fp = open(path, "w")
    scn = context.scene
    for v in me.vertices:
        fp.write("v %.4f %.4f %.4f\n" % (v.co[0], v.co[2], -v.co[1]))
        
    for v in me.vertices:
        fp.write("vn %.4f %.4f %.4f\n" % (v.normal[0], v.normal[2], -v.normal[1]))
        
    orderedFaces = zOrderFaces(me)
    
    info =  (-1, None)
    if me.uv_textures:
        (uvFaceVerts, texVerts, nTexVerts) = setupTexVerts(me)
        for vtn in range(nTexVerts):
            vt = texVerts[vtn]
            fp.write("vt %.4f %.4f\n" % (vt[0], vt[1]))
        for f in orderedFaces:
            info = writeNewGroup(fp, f,info, me, ob, groupsAsMaterials)
            uvVerts = uvFaceVerts[f.index]
            fp.write("f ")
            for n,v in enumerate(f.vertices):
                (vt, uv) = uvVerts[n]
                fp.write("%d/%d " % (v+1, vt+1))
            fp.write("\n")
    else:
        for f in orderedFaces:
            info = writeNewGroup(fp, f, info, me, ob, groupsAsMaterials)
            fp.write("f ")
            for vn in f.vertices:
                fp.write("%d " % (vn+1))
            fp.write("\n")

    fp.close()
    print("%s written" % path)
    return

def writeNewGroup(fp, f, info, me, ob, groupsAsMaterials):            
    (gnum, mname) = info
    if groupsAsMaterials:
        if f.material_index != gnum:
            gnum = f.material_index
            gname = me.materials[gnum].name
            mname1 = "skin"
            for key in GroupMaterials.keys():
                if key in gname:
                    mname1 = GroupMaterials[key]
                    break
            if mname != mname1:                    
                mname = mname1
                fp.write("usemtl %s\n" % mname)
            fp.write("g %s\n" % gname)
            info = (gnum, mname)
    else:
        nhits = {}
        for vn in f.vertices:
            v = me.vertices[vn]
            for grp in v.groups:
                try:
                    nhits[grp.group] += 1
                except:
                    nhits[grp.group] = 1
        gn = -1
        nverts = len(f.vertices)
        for (gn1,n) in nhits.items():
            if n == nverts:
                gn = gn1
                break
        if gn < 0:
            raise NameError("Did not find group for face %d" % f.index)
        if gn != gnum:            
            mat = me.materials[f.material_index]
            if mname != mat.name:
                mname = mat.name
                fp.write("usemtl %s\n" % mname)
            gnum = gn  
            for vgrp in ob.vertex_groups:
                if vgrp.index == gnum:                    
                    fp.write("g %s\n" % vgrp.name)
                    break
            info = (gnum, mname)
    return info       

#
#   zOrderFaces(me):
#

def zOrderFaces(me):
    zGroupFaces = {}
    zGroupFaces[0] = []
    for n in GroupZOrderSuffix.keys():
        zGroupFaces[n] = []        
    for f in me.faces:
        group = me.materials[f.material_index].name
        suffix = group.split("-")[-1]
        zgroup = zGroupFaces[0]
        for (prio,suffices) in GroupZOrderSuffix.items():
            if suffix in suffices:
                zgroup = zGroupFaces[prio]
                break
        zgroup.append(f)
    zlist = list(zGroupFaces.items())
    zlist.sort()
    faces = []
    for (key, flist) in zlist:
        faces += flist
    return faces

#
#   setupTexVerts(me):
#

def setupTexVerts(me):
    vertEdges = {}
    vertFaces = {}
    for v in me.vertices:
        vertEdges[v.index] = []
        vertFaces[v.index] = []
    for e in me.edges:
        for vn in e.vertices:
            vertEdges[vn].append(e)
    for f in me.faces:
        for vn in f.vertices:
            vertFaces[vn].append(f)
    
    edgeFaces = {}
    for e in me.edges:
        edgeFaces[e.index] = []
    faceEdges = {}
    for f in me.faces:
        faceEdges[f.index] = []
    for f in me.faces:
        for vn in f.vertices:
            for e in vertEdges[vn]:
                v0 = e.vertices[0]
                v1 = e.vertices[1]
                if (v0 in f.vertices) and (v1 in f.vertices):
                    if f not in edgeFaces[e.index]:
                        edgeFaces[e.index].append(f)
                    if e not in faceEdges[f.index]:
                        faceEdges[f.index].append(e)
        
    faceNeighbors = {}
    uvFaceVerts = {}
    for f in me.faces:
        faceNeighbors[f.index] = []
        uvFaceVerts[f.index] = []
    for f in me.faces:
        for e in faceEdges[f.index]:
            for f1 in edgeFaces[e.index]:
                if f1 != f:
                    faceNeighbors[f.index].append((e,f1))

    uvtex = me.uv_textures[0]
    vtn = 0
    texVerts = {}    
    for f in me.faces:
        uvf = uvtex.data[f.index]
        vtn = findTexVert(uvf.uv1, vtn, f, faceNeighbors, uvFaceVerts, texVerts)
        vtn = findTexVert(uvf.uv2, vtn, f, faceNeighbors, uvFaceVerts, texVerts)
        vtn = findTexVert(uvf.uv3, vtn, f, faceNeighbors, uvFaceVerts, texVerts)
        if len(f.vertices) > 3:
            vtn = findTexVert(uvf.uv4, vtn, f, faceNeighbors, uvFaceVerts, texVerts)
    return (uvFaceVerts, texVerts, vtn)     

#
#   findTexVert(uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts):
#

def findTexVert(uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts):
    for (e,f1) in faceNeighbors[f.index]:
        for (vtn1,uv1) in uvFaceVerts[f1.index]:
            vec = uv - uv1
            if vec.length < Epsilon:
                uvFaceVerts[f.index].append((vtn1,uv))                
                return vtn
    uvFaceVerts[f.index].append((vtn,uv))
    texVerts[vtn] = uv
    return vtn+1
    
#
#   class ExportObj(bpy.types.Operator, ImportHelper):
#

class ExportObj(bpy.types.Operator, ImportHelper):
    '''Export to OBJ file format (.obj)''' 
    bl_idname = "export.makehuman_obj"
    bl_description = 'Export to OBJ file format (.obj)'
    bl_label = "Export MH OBJ"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".obj"
    filter_glob = StringProperty(default="*.obj", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="File path for the exported OBJ file", maxlen= 1024, default= "")
    
    groupsAsMaterials = BoolProperty(name="Groups as materials", default=False)
 
    def execute(self, context):        
        exportObjFile(self.properties.filepath, self.groupsAsMaterials, context)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
 
 #
 #  Register
 #
 
def menu_func(self, context):
    self.layout.operator(ExportObj.bl_idname, text="MakeHuman OBJ (.obj)...")
 
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)
  
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)
 
if __name__ == "__main__":
    register()