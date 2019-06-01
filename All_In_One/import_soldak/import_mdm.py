import sys
import os
import time

import mdm

if __name__ != '__main__':
    import bpy
    import bmesh
    import mathutils

# Loader -----

def load(operator,
         context,
         filepath=""
         ):

    print("importing MDM: %r..." % (filepath), end="")

    time1 = time.clock()

    name = os.path.split(os.path.splitext(filepath)[0])[-1]

    with open(filepath, 'rb') as file:

        header = mdm.read_header(file)
        if header.id != 0x12121212:
            print('\tFatal Error:  Not a valid mdm file: %r' % filepath)
            file.close()
            return

        scene = context.scene

        # Load all surfaces
        surface_data = []
        file.seek(header.surfaceOffset)
        for s in range(header.numSurfaces):
            surface_data.append(mdm.read_surface(file))

        # Create start offset into vertices so we can look up vertBones
        surface_startVerts = []
        total = 0
        for s in surface_data:
            surface_startVerts.append(total)
            total += s.numVerts

        # Read all vertBone data into memory
        file.seek(header.weightsOffset)
        vertbone_data = []
        for _ in range(header.numVerts):
            vertbone_data.append(mdm.read_vertbone(file))

        # Loop over all surfaces
        for surf_num, surface in enumerate(surface_data[:1]):

            # Create a new mesh (not editable)
            mesh = bpy.data.meshes.new("mesh" + str(surf_num))
            obj = bpy.data.objects.new("Foo" + str(surf_num), mesh)
            scene.objects.link(obj)

            # Make a bmesh (editable) per surface
            bm = bmesh.new()

            # Add the vertices
            file.seek(surface.vertsOffset)
            vertices = [] # these are blender objects
            st = surface_startVerts[surf_num]
            # Match vertbones to vertices
            for vb_data in vertbone_data[st : st + surface.numVerts]:
                vert_data = mdm.read_vert(file)
                v = bm.verts.new(vb_data.vertOffset)
                v.normal = mathutils.Vector(vert_data.normal)
                vertices.append(v)

            # Add the triangles
            file.seek(surface.trisOffset)
            for _ in range(surface.numTris):
                tri = mdm.read_tri(file)
                bm.faces.new([vertices[i] for i in tri])
                #bm.faces.new([vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]])

            # Convert back to mesh
            # mesh = context.object.data
            mesh = obj.data
            bm.to_mesh(mesh)
            bm.free()

        scene.objects.active = obj
        obj.select = True

        print(" done in %.4f sec." % (time.clock() - time1))

    return {'FINISHED'}

