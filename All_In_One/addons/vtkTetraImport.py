# Author: Gurten






bl_info = {
    "name": "Tetrahedral model importer (VTK)",
    "author": "Gurten",
    "version": ( 1, 0, 2 ),
    "blender": ( 2, 6, 3 ),
    "location": "File > Import > Tetrahedral model importer (.vtk)",
    "description": "Tetrahedral model importer (.vtk)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mathutils import Vector

def faceToPlane(p):
    vec1 = p[0]- p[1]
    vec2 = p[2]- p[1]
    vec1.normalize()
    vec2.normalize()
    norm = vec1.cross(vec2)
    norm.normalize()
    dist = (norm * p[0])
    return ([-norm[0], -norm[1], -norm[2], -dist]) 

def load_vtk(fpath):
    f = open(fpath, 'r')
    lines = f.read().splitlines()
    f.close()
    n_pts = 0
    tetra_lines = []; vert_lines = []
    for i, l in enumerate(lines):
        if l.startswith("POINTS"):
            id, n, datatype = l.split()
            n_pts = int(n)
            vert_lines = lines[(i+1):(i+1+n_pts)]
        if l.startswith("CELLS"):
            id, n, unk = l.split()
            tetra_lines = lines[(i+1):(i+1+int(n))]
    verts = [Vector([float(c) for c in v.split()[:3]])  for v in vert_lines]
    indices = [[int(i) for i in t.split()[1:5]] for t in tetra_lines]
    flat_indices = [item for sublist in indices for item in sublist]
    # This is a quick fix for an issue encountered where
    # in some .vtk files the indexing begins at 1 instead of 0
    min = 1<<32; max = 0
    for i in flat_indices:
        if i < min:
            min = i
        if i > max:
            max = i
    if min == 1 and max == n_pts:
        for quadruple in indices:
            for i in range(len(quadruple)):
                quadruple[i] -= 1
    return verts, indices

def get_tetras(fpath):
    v, indices = load_vtk(fpath)
    tetra = []
    for t in indices:
        # four triangle windings of tetrahedron
        tris = [[v[t[(j + i)&3]] for i in [0,1,2]] for j in [0,1,2,3]]
        centroid = (v[t[0]] +v[t[1]] +v[t[2]] +v[t[3]] )/ 4.0
        # four planes for the tetra
        planes = [faceToPlane(tri) for tri in tris]
        flip = [False, False, False, False]
        for i,p in enumerate(planes):
            mag = (Vector((p[0], p[1], p[2])) * centroid) - p[3]
            if mag > 0:
                #planes[i] = [-c for c in p] #flip coords to face out if needed
                #tris[i] = [tris[i][2],tris[i][1],tris[i][0]] #flip the winding if needed
                flip[i] = True
        verts = [v[t[i]] for i in [0,1,2,3]] # vertices belonging to the current tetra beginning from index 0
        windings = [[(j + i)&3 for i in ([2,1,0] if flip[j] else [0,1,2])] for j in [0,1,2,3]]
        tetra.append((verts, windings))
    return tetra

def build_tetras_from_vtk(fpath):
    tetras = get_tetras(fpath)
    for verts, faces in tetras:
        mesh = bpy.data.meshes.new("tetra")
        object = bpy.data.objects.new("tetra",mesh)
        bpy.context.scene.objects.link(object)
        mesh.from_pydata(verts,[],faces)
  

class ImportTetraVTK(bpy.types.Operator, ExportHelper):
    bl_idname = "import.vtk"
    bl_label = "Import"
    __doc__ = "Tetrahedral model importer (.vtk)"
    filename_ext = ".vtk"
    filter_glob = StringProperty( default = "*.vtk", options = {'HIDDEN'} )
    
    filepath = StringProperty( 
        name = "File Path",
        description = "File path to tetrahedral vtk file",
        maxlen = 1024,
        default = "" )
    
    def draw( self, context ):
        layout = self.layout
        box = layout.box()

    def execute(self, context):
        build_tetras_from_vtk(self.filepath)
        return {'FINISHED'}
        
        

# Blender register plugin 
def register():
    bpy.utils.register_class(ImportTetraVTK)

def menu_func( self, context ):
    self.layout.operator( ImportTetraVTK.bl_idname, text = "Tetrahedral model importer (.vtk)" )

def register():
    bpy.utils.register_class( ImportTetraVTK )
    bpy.types.INFO_MT_file_import.append( menu_func )

def unregister():
    bpy.utils.unregister_class( ImportTetraVTK )
    bpy.types.INFO_MT_file_import.remove( menu_func )

if __name__ == "__main__":
    register()