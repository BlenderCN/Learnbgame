# <pep8>

import os
import time
import re

import bpy
import mathutils
import bpy_extras.io_utils


# #####################################################
# Templates
# #####################################################

TEMPLATE_CAO_FILE = u"""\
{
V1,
# 3D points,
%(nPoints)d,
[%(points)s],
# 3D lines,
%(nLines)d,
[%(lines)s],
# Faces from 3D lines,
%(nFacelines)d,
[%(facelines)s],
# Faces from 3D points,
%(nFacepoints)d,
[%(facepoints)s],
# 3D cylinders,
%(nCylinder)d,
[%(cylinders)s],
# 3D circles,
%(nCircles)d,
[%(circles)s]
}
"""

TEMPLATE_LINES = "%d %d"

TEMPLATE_VERTEX = "%f %f %f"

TEMPLATE_CYLINDER = "%d %d %f"

TEMPLATE_CIRCLE = "%f %d %d %d"

# #####################################################
# Utils
# #####################################################

def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

def generate_vertices(v):
    return  TEMPLATE_VERTEX % (v[0], v[1], v[2])

def generate_lines(l):
    return TEMPLATE_LINES % (l[0], l[1])

def generate_facelines(fl):
    return " ".join(map(str,[x for x in fl]))

def generate_faces(v):
    return str(len(v)) + " " + " ".join(map(str,[x-1 for x in v]))

def generate_cylinders(c):
    return TEMPLATE_CYLINDER % (c[0], c[1], c[2])

def generate_circles(c):
    return TEMPLATE_CIRCLE % (c[0], c[1], c[2], c[3])

def write_file(filepath, objects, scene,
               EXPORT_TRI=False,
               EXPORT_EDGES=False,
               EXPORT_NORMALS=False,
               EXPORT_APPLY_MODIFIERS=True,
               EXPORT_GLOBAL_MATRIX=None,
               ):

    print('CAO Export path: %r' % filepath)

    time1 = time.time()

    file = open(filepath, "w", encoding="utf8", newline="\n")
    fw = file.write

    # Write Header
    fw('# Blender v%s CAO File\n' % (bpy.app.version_string))

    # Initialize
    totverts = 1
    face_vert_index = 1
    copy_set = set()

    vertices = []
    faces = []
    lines = []
    facelines = []
    gcylinders = []
    gcircles = []

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            if area.spaces[0].transform_orientation == 'GLOBAL':
                EXPORT_GLOBAL_MATRIX = mathutils.Matrix()
                break
            else:
                EXPORT_GLOBAL_MATRIX = None

    # Get all meshes
    for ob_main in objects:

        # ignore dupli children
        if ob_main.parent and ob_main.parent.dupli_type in {'VERTS', 'FACES'}:
            continue

        obs = []
        if ob_main.dupli_type != 'NONE':
            # print('creating dupli_list on', ob_main.name)
            ob_main.dupli_list_create(scene)
            obs = [(dob.object, dob.matrix) for dob in ob_main.dupli_list]

        else:
            obs = [(ob_main, ob_main.matrix_world)]

        try:  
            ob_main["vp_model_types"]
        except:
            continue

        for ob, ob_mat in obs:

            try:
                me = ob.to_mesh(scene, EXPORT_APPLY_MODIFIERS, 'PREVIEW', calc_tessface=False)
            except RuntimeError:
                me = None

            if me is None or ob_main["vp_model_types"] not in ["3D Faces","3D Lines"]:
                continue

            if EXPORT_GLOBAL_MATRIX is not None:
                me.transform(EXPORT_GLOBAL_MATRIX * ob_mat)# Translate to World Coordinate System

            if EXPORT_TRI:
                mesh_triangulate(me)

            me_verts = me.vertices[:]

            face_index_pairs = [(face, index) for index, face in enumerate(me.polygons)]

            if EXPORT_EDGES:
                edges = me.edges
            else:
                edges = []

            if not (len(face_index_pairs) + len(edges) + len(me.vertices)):
                bpy.data.meshes.remove(me)
                continue  # ignore this mesh.

            smooth_groups, smooth_groups_tot = (), 0

            # no materials
            if smooth_groups:
                sort_func = lambda a: smooth_groups[a[1] if a[0].use_smooth else False]
            else:
                sort_func = lambda a: a[0].use_smooth

            face_index_pairs.sort(key=sort_func)
            del sort_func

            # fw('# %s\n' % (ob_main.name))

            # Vertices
            for v in me_verts:
                vertices.append(v.co[:])

            # Faces
            for f, f_index in face_index_pairs:
                f_v = [(vi, me_verts[v_idx], l_idx) for vi, (v_idx, l_idx) in enumerate(zip(f.vertices, f.loop_indices))]
                f_side = []

                for vi, v, li in f_v:
                    f_side.append(totverts + v.index)

                # Lines/Edges
                if ob_main["vp_model_types"] == "3D Lines":
                    initialen = len(lines)
                    for i in range(0,len(f_side)-1):
                        lines.append([f_side[i]-1,f_side[i+1]-1])# TODO: Remove duplicates
                    lines.append([f_side[len(f_side)-1]-1,f_side[0]-1])
                    if ob_main["vp_line_face"]:
                        facelines.append([len(lines)-initialen, list(range(initialen, len(lines)))])

                else:
                    faces.append(f_side)

            # If no faces are present but only lines
            if len(face_index_pairs) == 0 and ob_main["vp_model_types"] == "3D Lines":
                for key in me.edge_keys:
                    lines.append([key[0],key[1]])

            # Make the indices global rather then per mesh
            totverts += len(me_verts)

            # clean up
            bpy.data.meshes.remove(me)

        if ob_main["vp_model_types"] == "3D Cylinders":
            gcylinders.append([len(vertices), len(vertices)+1, ob_main["vp_radius"]]) # Get radius
            vertices.append(ob_main["vp_obj_Point1"])
            vertices.append(ob_main["vp_obj_Point2"])
            totverts += 2

        elif ob_main["vp_model_types"] == "3D Circles":
            gcircles.append([ob_main["vp_radius"], len(vertices), len(vertices)+1, len(vertices)+2])
            vertices.append(ob_main["vp_obj_Point3"])
            vertices.append(ob_main["vp_obj_Point1"])
            vertices.append(ob_main["vp_obj_Point2"])
            totverts += 3

        if ob_main.dupli_type != 'NONE':
            ob_main.dupli_list_clear()

    npoints = len(vertices)
    nfacepoints = len(faces)
    nlines = len(lines)
    nfacelines = len(facelines)
    ncylinders = len(gcylinders)
    ncircles = len(gcircles)

    text = TEMPLATE_CAO_FILE % {
        "nPoints"  : npoints,
        "points" : "\n".join(generate_vertices(v) for v in vertices),
        "nLines" : nlines,
        "lines" : "\n".join(generate_lines(l) for l in lines),
        "nFacelines" : nfacelines,
        "facelines" : "\n".join(generate_facelines(fl) for fl in facelines),
        "nFacepoints" : nfacepoints,
        "facepoints" : "\n".join(generate_faces(f) for f in faces),
        "nCylinder" : ncylinders,
        "cylinders" : "\n".join(generate_cylinders(c) for c in gcylinders),
        "nCircles" : ncircles,
        "circles" : "\n".join(generate_circles(c) for c in gcircles)
    }

    text = text.replace(',', '').replace('{', '').replace('}', '').replace('{', '').replace('[', '').replace(']', '')
    text = "".join([s for s in text.strip().splitlines(True) if s.strip()])

    fw(text)
    file.close()

    # copy all collected files.
    bpy_extras.io_utils.path_reference_copy(copy_set)

    print("Export time: %.2f" % (time.time() - time1))


def _write(context, filepath,
              EXPORT_TRI,  # ok
              EXPORT_EDGES,
              EXPORT_NORMALS,  # not yet
              EXPORT_APPLY_MODIFIERS,  # ok
              EXPORT_SEL_ONLY,  # ok
              EXPORT_GLOBAL_MATRIX,
              ):  # Not used

    base_name, ext = os.path.splitext(filepath)
    context_name = [base_name, '', '', ext]  # Base name, scene name, frame number, extension
    scene = context.scene

    # Exit edit mode before exporting, so current object states are exported properly.
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    orig_frame = scene.frame_current
    scene_frames = [orig_frame]
    EXPORT_SEL_ONLY = True   # Hard-coded?

    # Loop through all frames in the scene and export.
    for frame in scene_frames:

        scene.frame_set(frame, 0.0)
        if EXPORT_SEL_ONLY:
            objects = context.selected_objects
        else:
            objects = scene.objects

        full_path = ''.join(context_name)

        # EXPORT THE FILE.
        write_file(full_path, objects, scene,
                   EXPORT_TRI,
                   EXPORT_EDGES,
                   EXPORT_NORMALS,
                   EXPORT_APPLY_MODIFIERS,
                   EXPORT_GLOBAL_MATRIX,
                   )

    scene.frame_set(orig_frame, 0.0)

def save(operator, context, filepath="",
         use_triangles=False,
         use_edges=True,
         use_normals=False,
         use_mesh_modifiers=True,
         use_selection=True,
         global_matrix=None,
         ):

    _write(context, filepath,
           EXPORT_TRI=use_triangles,
           EXPORT_EDGES=use_edges,
           EXPORT_NORMALS=use_normals,
           EXPORT_APPLY_MODIFIERS=use_mesh_modifiers,
           EXPORT_SEL_ONLY=use_selection,
           EXPORT_GLOBAL_MATRIX=global_matrix,
           )

    return {'FINISHED'}
