import bpy
import bmesh
import mathutils


def debug_sweeps(sweeps, index=None, cyclic=False, verts=True, edges=True, loop_candidates=True, loops=True, loop_types=True, handles=True, avg_face_normals=True):
    for idx, sweep in enumerate(sweeps):
        if index:
            idx = index
        print("sweep:", idx)
        if verts:
            print("  » verts:", sweep["verts"][0].index, " - ", sweep["verts"][1].index)
        if edges:
            print("  » edges:", sweep["edges"][0].index)
        if loop_candidates:
            print("  » loop_candidates:", [[l.index for l in lcs] for lcs in sweep["loop_candidates"]])
        if loops:
            print("  » loops:", [l.index for l in sweep["loops"]])
        if loop_types:
            print("  » loop_types", [lt for lt in sweep["loop_types"]])
        if handles:
            print("  » handles:", [hco for hco in sweep["handles"]])
        if avg_face_normals:
            print("  » avg_face_normals:", [ino for ino in sweep["avg_face_normals"]])
        print()

    if cyclic:
        print("Selection is cyclic!")


def vert_debug_print(debug, vert, msg, end="\n"):
    if debug:
        if type(debug) is list:
            if vert.index in debug:
                print(msg, end=end)
        else:
            print(msg, end=end)


def draw_vector(vector):
    vec_mesh = bpy.data.meshes.new("vector_mesh")
    vec = bpy.data.objects.new(name="vector", object_data=vec_mesh)
    bpy.context.scene.objects.link(vec)

    # create bmesh
    bm = bmesh.new()
    bm.from_mesh(vec_mesh)

    v1 = bm.verts.new(mathutils.Vector())
    v2 = bm.verts.new(v1.co + vector)

    bm.edges.new([v1, v2])

    bm.to_mesh(vec_mesh)
    bm.clear()

    return vec
