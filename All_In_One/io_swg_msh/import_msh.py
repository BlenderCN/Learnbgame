from . import iffFile
from . import mshFile

import bpy
    
def load(operator, context, filepath):
    print('\nimporting msh %r' % filepath)
    
    msh = mshFile.mshFile()
    iff = iffFile.iff_file(filepath, msh)
        
    print("Mesh Group Count: %d" % len(msh.groups))
    for i in range(len(msh.groups)):
        group = msh.groups[i]
        mesh = bpy.data.meshes.new("mesh%03d" % i)
        
        verts = []
        for vert in group[0]:
            verts.append((vert.vertex.x, vert.vertex.z, vert.vertex.y))
        
        faces = []
        for tri in group[1]:
            faces.append((tri.p1, tri.p2, tri.p3))
        
        mesh.from_pydata( verts, [], faces)
        obj = bpy.data.objects.new("obj%03d" % i, mesh)
        bpy.context.scene.objects.link(obj)
        bpy.context.scene.update()

if __name__ == "__main__":
    register()
