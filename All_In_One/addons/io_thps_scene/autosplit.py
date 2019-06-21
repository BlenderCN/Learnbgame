import bpy
import bgl
import bmesh
import collections
from bpy.props import *
from . import helpers
from . helpers import *

__reload_order_index__ = -10

# PROPERTIES
#############################################
copy_layers2_type_map = {
    bmesh.types.BMFace: "faces",
    bmesh.types.BMEdge: "edges",
    bmesh.types.BMLoop: "loops",
    bmesh.types.BMVert: "verts",
}
SplitVert = collections.namedtuple("SplitVert", "co uvs vc normal weights")


# METHODS
#############################################
def get_triangle_strip(mesh, bm, faces, split_verts, flags): # ob):
    prev_tri = None
    strip = []

    def idx(loop):
        return split_verts[get_split_vert_for_loop(mesh, bm, loop, flags)]

    for tri in faces:
        assert len(tri.verts) == 3
        assert len(tri.loops) == 3
        if not prev_tri:
            strip += [idx(v) for v in tri.loops]
            prev_tri = tri
        else:
            strip += [idx(prev_tri.loops[2]), idx(prev_tri.loops[2])]
            # strip += [idx(prev_tri.loops[2])]
            strip += [idx(tri.loops[0]), idx(tri.loops[0])]
            strip += [idx(tri.loops[1]), idx(tri.loops[2])]
            prev_tri = tri

    return strip

def get_split_vert_for_loop(mesh, bm, l, flags):
    if flags & SECFLAGS_HAS_TEXCOORDS:
        if len(bm.loops.layers.uv):
            uvs = tuple(l[uv_layer].uv.copy().freeze() for uv_layer in bm.loops.layers.uv.values())
        else:
            uvs = (mathutils.Vector((0.0, 0.0)).freeze(),)
    else:
        uvs = None

    if len(bm.loops.layers.color) and flags & SECFLAGS_HAS_VERTEX_COLORS:
        #vcs = l[bm.loops.layers.color.active]
        vc_layer = bm.loops.layers.color.get("color")
        bake_layer = bm.loops.layers.color.get("bake")
        if bake_layer:
            vcs = [ l[bake_layer].r, l[bake_layer].g, l[bake_layer].b ]
        elif vc_layer:
            vcs = [ l[vc_layer].r, l[vc_layer].g, l[vc_layer].b ]
        else:
            #print("No vertex color layer, using white!")
            vcs = [1.0, 1.0, 1.0]
        alpha_layer = bm.loops.layers.color.get("alpha")
        vcs = (vcs[0], vcs[1], vcs[2], l[alpha_layer].r if alpha_layer else 1.0)
    else:
        vcs = None

    deform_layer = bm.verts.layers.deform.active
    if flags & SECFLAGS_HAS_VERTEX_WEIGHTS:
        dvert = l.vert[deform_layer]
        weights = list(sorted(dvert.items(), key=lambda x: -x[1]))[:4]
        if len(weights) < 4:
            weights += [(0, 0.0)] * (4 - len(weights))
        weights = tuple(weights)
    else:
        weights = None

    if flags & SECFLAGS_HAS_VERTEX_NORMALS:
        normal = mesh.loops[l.index].normal.copy().freeze()
    else:
        #print("no normals")
        normal = None

    return SplitVert(l.vert.co.copy().freeze(), uvs, vcs, normal, weights)

def make_split_verts(mesh, bm, flags, verts=None):
    split_verts = collections.OrderedDict()
    for v in verts if verts is not None else bm.verts:
        for l in v.link_loops:
            sv = get_split_vert_for_loop(mesh, bm, l, flags)
            split_verts.setdefault(sv, len(split_verts))
    return split_verts


def copy_layers(from_bm, to_bm):
    for type_attr in ("faces", "loops", "verts", "edges"):
        type_col = getattr(from_bm, type_attr)
        to_type_col = getattr(to_bm, type_attr)
        for attr_name in dir(type_col.layers):
            if attr_name.startswith("__"): continue
            attr = getattr(type_col.layers, attr_name)
            if isinstance(attr, bmesh.types.BMLayerCollection):
                to_attr = getattr(to_type_col.layers, attr_name)
                for layer_name, from_layer in attr.items():
                    to_attr.get(layer_name) or to_attr.new(layer_name)

#----------------------------------------------------------------------------------
def copy_layers2(from_bm, from_item, to_bm, to_item):
    type_attr = copy_layers2_type_map.get(type(from_item))
    if not type_attr: return
    type_col = getattr(from_bm, type_attr)
    to_type_col = getattr(to_bm, type_attr)
    for attr_name in dir(type_col.layers):
        if attr_name.startswith("__"): continue
        attr = getattr(type_col.layers, attr_name)
        if isinstance(attr, bmesh.types.BMLayerCollection):
            to_attr = getattr(to_type_col.layers, attr_name)
            for layer_name, from_layer in attr.items():
                to_item[to_attr.get(layer_name)] = from_item[from_layer]

#----------------------------------------------------------------------------------
def _alt_split_obj(ob, context, max_radius=500, faces_per_subobject=250, preserve_normals=True):
    if ob.type != "MESH":
        return

    print("Separating {}".format(ob.name))
    ob.data.calc_normals_split()
    import bpy, bmesh, itertools
    # from mathutils.bvhtree import BVHTree
    from mathutils.kdtree import KDTree

    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.transform(bm, matrix=ob.matrix_world, verts=bm.verts)

    """
    old_edges = set(bm.edges)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    arl = bm.edges.layers.int.get("thug_autorail")
    if arl:
        for edge in bm.edges:
            if edge not in old_edges:
                edge[arl] = AUTORAIL_NONE
    """

    tree = None
    total_faces = None
    deleted_faces = None
    face_index = None
    def init():
        nonlocal tree, total_faces, deleted_faces, face_index
        bm.faces.ensure_lookup_table()
        # tree = BVHTree.FromObject(ob, context.scene)
        # tree = BVHTree.FromBMesh(bm, epsilon=0.00001)
        tree = KDTree(len(bm.faces))
        for i, face in enumerate(bm.faces):
            tree.insert(face.calc_center_median(), i)
        tree.balance()

        total_faces = len(bm.faces)
        deleted_faces = [False] * total_faces
        face_index = 0
    init()

    new_meshes = []
    small_mesh = ob.data.copy()
    try:
        if preserve_normals:
            nx = bm.loops.layers.float.new("norm_x")
            ny = bm.loops.layers.float.new("norm_y")
            nz = bm.loops.layers.float.new("norm_z")

            for face in bm.faces:
                face.select = False
                face.select_set(False)

                for loop in face.loops:
                    orig_loop = ob.data.loops[loop.index]
                    loop[nx] = orig_loop.normal[0]
                    loop[ny] = orig_loop.normal[1]
                    loop[nz] = orig_loop.normal[2]
        else:
            for face in bm.faces:
                face.select = False
                face.select_set(False)

        temp_bm = bmesh.new()
        temp_bm.to_mesh(small_mesh)

        object_count = 0
        total_face_counter = 0
        faces_to_delete = []
        while face_index < total_faces:
            if deleted_faces[face_index]:
                face_index += 1
                continue

            root_face = bm.faces[face_index]

            nearest = tree.find_range(root_face.calc_center_median(), max_radius)
            nearest = (x for x in nearest if not deleted_faces[x[1]])
            nearest = itertools.islice(
                nearest,
                faces_per_subobject)

            already_created_verts = {}
            temp_bm.clear()
            copy_layers(bm, temp_bm)
            new_mesh = small_mesh.copy() # bpy.data.meshes.new(ob.name + "__split_" + str(object_count))
            object_count += 1

            # for _, _, face_idx, _ in nearest:
            for _, face_idx, _ in nearest:
                deleted_faces[face_idx] = True
                face = bm.faces[face_idx]
                faces_to_delete.append(face)
                total_face_counter += 1
                new_verts = []
                old_loops = []
                for loop in face.loops:
                    vert = loop.vert
                    old_loops.append(loop)
                    if vert in already_created_verts:
                        new_verts.append(already_created_verts[vert])
                    else:
                        new_vert = temp_bm.verts.new(vert.co)
                        copy_layers2(bm, vert, temp_bm, new_vert)
                        already_created_verts[vert] = new_vert
                        new_verts.append(new_vert)
                try:
                    new_face = temp_bm.faces.new(new_verts)
                except ValueError:
                    print("weird: {} {}", face_idx, new_verts)
                for old_loop, new_loop in zip(old_loops, new_face.loops):
                    copy_layers2(bm, old_loop.edge, temp_bm, new_loop.edge)
                    copy_layers2(bm, old_loop, temp_bm, new_loop)
                new_face.hide = face.hide
                new_face.material_index = face.material_index
                new_face.smooth = face.smooth
                copy_layers2(bm, face, temp_bm, new_face)

            print("Separating! Objects: {}, Faces so far: {}\r".format(object_count, total_face_counter), end='')

            temp_bm.to_mesh(new_mesh)
            new_meshes.append(new_mesh)

            if preserve_normals:
                custom_normals = []
                nx = temp_bm.loops.layers.float.get("norm_x")
                ny = temp_bm.loops.layers.float.get("norm_y")
                nz = temp_bm.loops.layers.float.get("norm_z")

                if nx and ny and nz:
                    for face in temp_bm.faces:
                        for loop in face.loops:
                            custom_normals.append((loop[nx], loop[ny], loop[nz]))

                new_mesh.normals_split_custom_set(custom_normals)

            if len(faces_to_delete) >= 15000:
                bmesh.ops.delete(bm, geom=faces_to_delete, context=5)
                faces_to_delete = []
                init()

        print()
        LOG.debug("Split {} into {} objects".format(ob, object_count))

        nx = bm.loops.layers.float.new("norm_x")
        ny = bm.loops.layers.float.new("norm_y")
        nz = bm.loops.layers.float.new("norm_z")

        if preserve_normals:
            if nx and ny and nz:
                bm.loops.layers.float.remove(nx)
                bm.loops.layers.float.remove(ny)
                bm.loops.layers.float.remove(nz)

        new_objs = []
        for new_mesh in new_meshes:
            new_object = ob.copy()
            new_object.matrix_world = mathutils.Matrix.Identity(4)
            new_object.data = new_mesh
            context.scene.objects.link(new_object)
            new_objs.append(new_object)

        return new_objs
    except:
        for new_mesh in new_meshes:
            bpy.data.meshes.remove(new_mesh)
        raise
    finally:
        bpy.data.meshes.remove(small_mesh)
        
#----------------------------------------------------------------------------------
def _is_levelobject(ob):
    if ob.thug_object_class == "LevelObject":
        return True
    if ob.name.endswith("_SCN"):
        col_name = ob.name[:-4]
        if bpy.data.objects.get(col_name):
            col_obj = bpy.data.objects.get(col_name)
            if col_obj.thug_object_class == "LevelObject":
                return True
    return False
        
#----------------------------------------------------------------------------------
def _prepare_autosplit_objects(operator, context, target_game):
    out_objects = [o for o in bpy.data.objects
                  if (o.type == "MESH" and
                    (getattr(o, 'thug_do_autosplit') or operator.autosplit_everything == True) and
                    (getattr(o, 'thug_export_scene', True) or
                     getattr(o, 'thug_export_collision', True)))]

    safe_mode_set("OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    orig_objects = []
    temporary_objects = []
    for ob in out_objects:
        final_mesh = None
        
        # Use either the object settings or the export setting, depending on whether
        # 'Auto-split everything' is enabled!
        as_faces_per_obj = ob.thug_do_autosplit_faces_per_subobject
        as_max_radius = ob.thug_do_autosplit_max_radius
        if operator.autosplit_everything == True:
            as_faces_per_obj = operator.autosplit_faces_per_subobject
            as_max_radius = operator.autosplit_max_radius
            
        
        if _is_levelobject(ob):
            LOG.debug("Skipping {}, it is a LevelObject!".format(ob.name))
            continue
            
        if ob.modifiers:
            final_mesh = ob.to_mesh(bpy.context.scene, True, 'PREVIEW')

        small_enough = False
        if final_mesh:
            if len(final_mesh.polygons) <= as_faces_per_obj:
                small_enough = True
        elif len(ob.data.polygons) <= as_faces_per_obj:
            small_enough = True

        if small_enough:
            LOG.debug("Skipping {}, it has {} polys".format(ob.name, len(ob.data.polygons)))
            if final_mesh:
                bpy.data.meshes.remove(final_mesh)
            continue
        else:
            LOG.debug("Splitting {}".format(ob.name))

        original_object = ob
        original_object_name = ob.name
        orig_objects.append((original_object, original_object_name))
        ob.name = "TEMP_OBJECT___"

        final_mesh = final_mesh or ob.to_mesh(bpy.context.scene, True, 'PREVIEW')
        # temporary_object = _make_temp_obj(final_mesh)
        temporary_object = original_object.copy()
        temporary_object.modifiers.clear()
        temporary_object.data = final_mesh
        temporary_object.name = original_object_name

        original_object["thug_autosplit_object_no_export_hack"] = True

        LOG.debug("with {} polys".format(len(final_mesh.polygons)))

        bpy.context.scene.objects.link(temporary_object)
        # temporary_object.matrix_world = ob.matrix_world

        if helpers._need_to_flip_normals(ob):
            helpers._flip_normals(temporary_object)

        temporary_object.select = True
        bpy.context.scene.objects.active = temporary_object
        # bpy.ops.object.thug_split_object(
        final_objs = _alt_split_obj(
            temporary_object, context,
            faces_per_subobject=as_faces_per_obj,
            max_radius=as_max_radius)
        # final_objs = context.selected_objects[:]

        bpy.context.scene.objects.unlink(temporary_object)
        bpy.data.objects.remove(temporary_object)
        bpy.data.meshes.remove(final_mesh)

        for fob in final_objs: fob.select = False
        temporary_objects += final_objs
        # LOG.debug("Object {} split into {} objects".format(temporary_object.name, len(final_objs)))

    # bpy.context.scene.update()

    for ob in temporary_objects:
        ob["thug_this_is_autosplit_temp_object"] = True

    return orig_objects, temporary_objects

#----------------------------------------------------------------------------------
def _cleanup_autosplit_objects(operator, context, target_game, orig_objects, temporary_objects):
    for ob in temporary_objects:
        ob_data = ob.data
        bpy.context.scene.objects.unlink(ob)
        bpy.data.objects.remove(ob)
        bpy.data.meshes.remove(ob_data)

    for (ob, ob_name) in orig_objects:
        ob.name = ob_name
        ob["thug_autosplit_object_no_export_hack"] = False
        del ob["thug_autosplit_object_no_export_hack"]

