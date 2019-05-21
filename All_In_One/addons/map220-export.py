bl_info = {
    "name": "MAP 220 Geometry Export",
    "author": "nemyax",
    "version": (0, 2, 20190214),
    "blender": (2, 7, 9),
    "location": "File > Import-Export",
    "description": "Export Half-Life map editor brushes based on scene geometry",
    "warning": "",
    "wiki_url": "https://sourceforge.net/p/blenderbitsbobs/wiki/MAP%20220%20Exporter",
    "tracker_url": "",
    "category": "Learnbgame"
}

import math
import mathutils as mu
import bpy
import bmesh
from bpy.props import (
    StringProperty,
    FloatProperty,
    BoolProperty)
from bpy_extras.io_utils import (
    ExportHelper,
    path_reference_mode)

def tri_to_texplane(a3d, b3d, c3d):
    dx = c3d - a3d
    dy = b3d - a3d
    dz = (b3d - a3d).cross(c3d - b3d).normalized()
    result = mu.Matrix((
        (dx.x, dy.x, dz.x, a3d.x),
        (dx.y, dy.y, dz.y, a3d.y),
        (dx.z, dy.z, dz.z, a3d.z),
        (0.0,  0.0,  0.0,  1.0)))
    result.invert_safe()
    return result

def uv_to_matrix4x4(ax, ay, bx, by, cx, cy):
    return mu.Matrix((
        (cx-ax, bx-ax, 0.0, ax),
        (cy-ay, by-ay, 0.0, ay),
        (0.0,   0.0,   1.0, 0.0),
        (0.0,   0.0,   0.0, 1.0)))

def tex_vecs_from_pts(a3d, b3d, c3d, a2d, b2d, c2d, x_res, y_res):
    mtx_3dtri_to_texplane = tri_to_texplane(a3d, b3d, c3d)
    mtx_texplane_to_final = uv_to_matrix4x4(
        a2d.x * x_res,
        a2d.y * y_res,
        b2d.x * x_res,
        b2d.y * y_res,
        c2d.x * x_res,
        c2d.y * y_res)
    mtx = mtx_texplane_to_final * mtx_3dtri_to_texplane
    return mtx[0], -mtx[1]

def do_tri(tri, uv, pattern, tx_lookup, thickness):
    item = "{\n"
    tx_name, x_res, y_res = tx_lookup[tri.material_index]
    la, lb, lc = tri.loops
    a3d = la.vert.co
    b3d = lb.vert.co
    c3d = lc.vert.co
    ax, ay, az = a3d
    bx, by, bz = b3d
    cx, cy, cz = c3d
    fl_z_vec = tri.normal * thickness
    apex = fl_z_vec + mu.Vector((
        (ax + bx + cx) * 0.333333,
        (ay + by + cy) * 0.333333,
        (az + bz + cz) * 0.333333))
    dx, dy, dz = [round(i, 3) for i in apex]
    a2d = la[uv].uv
    b2d = lb[uv].uv
    c2d = lc[uv].uv
    vec0, vec1 = tex_vecs_from_pts(a3d, b3d, c3d, a2d, b2d, c2d, x_res, y_res)
    item += pattern.format(
        ax, ay, az,
        bx, by, bz,
        cx, cy, cz,
        tx_name,
        vec0[0], vec0[1], vec0[2], vec0[3],
        vec1[0], vec1[1], vec1[2], vec1[3])
    coords = pattern[:66]
    texcoords = pattern[66:]
    fluff = texcoords.format(
        "NULL",
        -vec0[0], -vec0[1], -vec0[2], -vec0[3],
        vec1[0], vec1[1], vec1[2], vec1[3])
    item += coords.format(bx, by, bz, ax, ay, az, dx, dy, dz)
    item += fluff
    item += coords.format(ax, ay, az, cx, cy, cz, dx, dy, dz)
    item += fluff
    item += coords.format(cx, cy, cz, bx, by, bz, dx, dy, dz)
    item += fluff
    item += "}\n"
    return item

def append_text(file_path, text):
    fh = open(file_path, 'a')
    fh.write(text)
    fh.close()

def do_tris(bm, file_path, tx_lookup, thickness):
    num_tris = len(bm.faces)
    uv = bm.loops.layers.uv.verify()
    pattern = "( {:5f} {:5f} {:5f} ) " * 3 + \
        "{} " + "[ {:5f} {:5f} {:5f} {:5f} ] " * 2 + \
        "0 0 1\n"
    queued = ""
    num_done = 0
    for f in bm.faces:
        queued += do_tri(f, uv, pattern, tx_lookup, thickness)
        num_done += 1
        if (num_done % 500) == 0:
            append_text(file_path, queued)
            queued = ""
    append_text(file_path, queued)

def append_tri_bmesh(bm1, bm2, matrix):
    bm2.transform(matrix)
    uvs1 = bm1.loops.layers.uv.verify()
    uvs2 = bm2.loops.layers.uv.verify()
    for f2 in bm2.faces:
        f2v1, f2v2, f2v3 = f2.verts
        f1v1 = bm1.verts.new(f2v1.co)
        f1v2 = bm1.verts.new(f2v2.co)
        f1v3 = bm1.verts.new(f2v3.co)
        f1 = bm1.faces.new([f1v1,f1v2,f1v3])
        f1.loops[0][uvs1].uv = f2.loops[0][uvs2].uv
        f1.loops[1][uvs1].uv = f2.loops[1][uvs2].uv
        f1.loops[2][uvs1].uv = f2.loops[2][uvs2].uv
        f1.material_index = f2.material_index
    bm2.free()

def combine_meshes(bms, matrices):
    result = bmesh.new()
    for bm, mtx in zip(bms, matrices):
        append_tri_bmesh(result, bm, mtx)
    result.normal_update()
    bmesh.ops.reverse_faces(result, faces=result.faces)
    return result

def modify_lookup(mat_lookup, dummy_idx):
    result = {}
    for mat in mat_lookup:
        width = 0
        height = 0
        for ts in mat.texture_slots:
            if ts:
                tex = ts.texture
                if tex and tex.type == 'IMAGE':
                    im = tex.image
                    if im:
                        width, height = im.size
            if width > 0:
                break
        if width == 0:
            width = 64
            height = 64
        result[mat_lookup[mat]] = (mat.name,width,height)
    result[dummy_idx] = ("CLIP",64,64)
    return result

def prep_combined_mesh(objs):
    bms = []
    matrices = []
    mats = bpy.data.materials
    dummy_idx = len(mats)
    mat_lookup = dict(zip(mats, range(dummy_idx)))
    for o in objs:
        mat_reindex_lookup = {}
        for i in range(len(o.material_slots)):
            m = o.material_slots[i].material
            if m:
                mat_reindex_lookup[i] = mat_lookup[m]
            else:
                mat_reindex_lookup[i] = -1
        bm = bmesh.new()
        bm.from_object(o, bpy.context.scene)
        nontris = []
        for f in bm.faces:
            mi = f.material_index
            if mi in mat_reindex_lookup:
                f.material_index = mat_reindex_lookup[mi]
            else:
                f.material_index = dummy_idx
            if len(f.verts) > 3:
                nontris.append(f)
        bmesh.ops.triangulate(bm, faces=nontris)
        bms.append(bm)
        matrices.append(o.matrix_world)
    return combine_meshes(bms, matrices), modify_lookup(mat_lookup, dummy_idx)

def export_mesh(bm, file_path, tx_lookup, options):
    map_start = "{\n"
    map_start += "\"classname\" \"worldspawn\"\n"
    map_start += "\"mapversion\" \"220\"\n"
    map_start += "\"_generator\" \"Blender (MAP exporter by nemyax)\"\n"
    map_end = "}\n"
    if options['detail']:
        map_start += "}\n{\n"
        map_start += "\"classname\" \"func_detail\"\n"
    fh = open(file_path, 'w')
    fh.write(map_start)
    fh.close()
    do_tris(bm, file_path, tx_lookup, options['thickness'])
    append_text(file_path, map_end)

def do_export(file_path, options):
    if options['vis_layers']:
        check_layers = set(
            [i for (b,i) in zip(bpy.context.scene.layers, range(20)) if b])
    else:
        check_layers = set(range(20))
    objs = [o for o in bpy.data.objects if
        o.type == 'MESH' and
        not o.hide and
        set([i for (b,i) in zip(o.layers, range(20)) if b]) & check_layers]
    if not objs:
        return ("Nothing to export.",{'CANCELLED'})
    was_in_edit_mode = (bpy.context.mode == 'EDIT_MESH')
    if was_in_edit_mode:
        bpy.ops.object.mode_set()
    bm, tx_lookup = prep_combined_mesh(objs)
    bm.transform(mu.Matrix.Scale(options['scale'], 4))
    export_mesh(bm, file_path, tx_lookup, options)
    bm.free()
    if was_in_edit_mode:
        bpy.ops.object.mode_set(mode='EDIT')
    return (
      "Brushes written successfully to {}.".format(file_path),
      {'FINISHED'})
    
class ExportMap220(bpy.types.Operator, ExportHelper):
    '''Save scene geometry as MAP 220 brushes'''
    bl_idname = "export_scene.map220"
    bl_label = 'Export MAP'
    bl_options = {'PRESET'}
    filename_ext = ".map"
    filter_glob = StringProperty(
        default="*.map",
        options={'HIDDEN'})
    path_mode = path_reference_mode
    check_extension = True
    path_mode = path_reference_mode
    scale = FloatProperty(
        name="Scale",
        default=1.0,
        max=10000.0,
        min=1.0,
        description="Scale all data")
    thickness = FloatProperty(
        name="Brush thickness",
        default=4.0,
        max=32.0,
        min=1.0,
        description="Create brushes that are this many units thick")
    vis_layers = BoolProperty(
        name="Export only from visible layers",
        default=True,
        description="Objects on hidden layers will be ignored")
    detail = BoolProperty(
        name="Wrap in func_detail",
        default=True,
        description="Good for making prefabs")
    def execute(self, context):
        options = {
            'vis_layers':self.vis_layers,
            'scale'     :self.scale,
            'detail'    :self.detail,
            'thickness' :self.thickness}
        msg, result = do_export(self.filepath, options)
        if result == {'CANCELLED'}:
            self.report({'ERROR'}, msg)
        print(msg)
        return result

def menu_func_export_map220(self, context):
    self.layout.operator(
        ExportMap220.bl_idname, text="MAP 220 Brushes (.map)")

def register():
    bpy.utils.register_class(ExportMap220)
    bpy.types.INFO_MT_file_export.append(menu_func_export_map220)

def unregister():
    bpy.utils.unregister_class(ExportMap220)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_map220)
