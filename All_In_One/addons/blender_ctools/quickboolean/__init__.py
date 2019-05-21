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


bl_info = {
    'name': 'Quick Boolean',
    'author': 'chromoly',
    'version': (1, 0),
    'blender': (2, 77, 0),
    'location': '',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'category': 'Mesh',
}


import collections
import importlib
import itertools
import math
import traceback

import bpy
import bmesh
import bgl
import mathutils.geometry
from mathutils import *

try:
    importlib.reload(unitsystem)
    importlib.reload(utils)
    importlib.reload(vagl)
    importlib.reload(vaview3d)
except NameError:
    from . import unitsystem
    from . import utils
    from . import vagl
    from . import vaview3d


project = vaview3d.project
unproject = vaview3d.unproject

view_operators = [
    'view3d.dolly',
    'view3d.localgrid',
    'view3d.localgrid_ex',
    'view3d.localview',
    'view3d.move',
    'view3d.navigate',
    'view3d.ndof_all',
    'view3d.ndof_orbit',
    'view3d.ndof_orbit_zoom',
    'view3d.ndof_pan',
    'view3d.rotate',
    'view3d.view_all',
    'view3d.view_center_camera',
    'view3d.view_center_cursor',
    'view3d.view_center_lock',
    'view3d.view_center_pick',
    'view3d.view_lock_clear',
    'view3d.view_lock_to_active',
    'view3d.view_orbit',
    'view3d.view_pan',
    'view3d.view_persportho',
    'view3d.view_selected',
    'view3d.viewnumpad',
    'view3d.walk',
    'view3d.zoom',
    'view3d.zoom_border',
    'view3d.zoom_camera_1_to_1',
]


class QuickBooleanPreferences(
        utils.AddonKeyMapUtility,
        utils.AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):

    bl_idname = __name__

    color = bpy.props.FloatVectorProperty(
        name='Color',
        default=(1.0, 0.0, 0.0, 0.3),
        size=4,
        subtype='COLOR_GAMMA',
    )
    snap_color = bpy.props.FloatVectorProperty(
        name='Snap Color',
        default=(1.0, 1.0, 1.0, 1.0),
        size=4,
        subtype='COLOR_GAMMA',
    )

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        col = split.column()
        col.prop(self, 'color')
        col.prop(self, 'snap_color')

        split.column()
        split.column()

        super().draw(context, layout.column())


def unwrap_uvs_edit(bm, faces):
    """適当にUV展開
    :type bm: bmesh.BMesh
    :type faces: list[bmesh.BMFace]
    """
    for uv_layer in bm.loops.layers.uv.values():
        for face in faces:
            face_no = face.normal
            face_co = face.calc_center_median()
            quat = face_no.rotation_difference(Vector((0, 0, 1)))
            vecs = []
            for loop in face.loops:
                vert = loop.vert
                vec = vert.co - face_co
                vecs.append(vec - vec.project(face_no))
            vecs_2d = [(quat * v).to_2d() for v in vecs]
            xmin = min(vecs_2d, key=lambda v: v[0])[0]
            xmax = max(vecs_2d, key=lambda v: v[0])[0]
            ymin = min(vecs_2d, key=lambda v: v[1])[1]
            ymax = max(vecs_2d, key=lambda v: v[1])[1]
            sx = xmax - xmin
            sy = ymax - xmin
            vecs_2d = [v - Vector([xmin, ymin]) for v in vecs_2d]
            f = max(sx, sy)
            if f > 0:
                vecs_2d = [v / f for v in vecs_2d]
            for loop, co in zip(face.loops, vecs_2d):
                loop[uv_layer].uv = co


def unwrap_uvs(context, ob, actob):
    """適当にUV展開
    :type ob: bpy.tpes.Object
    :type actob: bpy.types.Object
    """
    mesh = ob.data

    ctx = context.copy()
    ctx['active_object'] = ctx['object'] = ob
    for i, uv_layer in enumerate(actob.data.uv_layers):
        bpy.ops.mesh.uv_texture_add(ctx)
        mesh.uv_layers[i].name = uv_layer.name

    for poly in mesh.polygons:
        face_no = poly.normal
        face_co = poly.center
        quat = face_no.rotation_difference(Vector((0, 0, 1)))
        vecs = []
        for i in range(poly.loop_start, poly.loop_start + poly.loop_total):
            loop = mesh.loops[i]
            vert = mesh.vertices[loop.vertex_index]
            vec = vert.co - face_co
            vecs.append(vec - vec.project(face_no))
        vecs_2d = [(quat * v).to_2d() for v in vecs]
        xmin = min(vecs_2d, key=lambda v: v[0])[0]
        xmax = max(vecs_2d, key=lambda v: v[0])[0]
        ymin = min(vecs_2d, key=lambda v: v[1])[1]
        ymax = max(vecs_2d, key=lambda v: v[1])[1]
        sx = xmax - xmin
        sy = ymax - xmin
        vecs_2d = [v - Vector([xmin, ymin]) for v in vecs_2d]
        f = max(sx, sy)
        if f > 0:
            vecs_2d = [v / f for v in vecs_2d]
        start = poly.loop_start
        stop = poly.loop_start + poly.loop_total
        for i, co in zip(range(start, stop), vecs_2d):
            for uv_layer in mesh.uv_layers:
                loop = uv_layer.data[i]
                loop.uv = co


def _intersect_edit(context, verts, edges, faces, reverse):
    """
    :type context: bpy.types.Context
    :type verts: list
    :type edges: list
    :type faces: list
    :type reverse: bool
    """

    ob = context.active_object
    obimat = ob.matrix_world.inverted()
    bm = bmesh.from_edit_mesh(ob.data)
    # layer追加は要素の追加前でないと、要素のis_validが偽になる
    layer = bm.faces.layers.int.get('booleancutoff')
    if not layer:
        layer = bm.faces.layers.int.new('booleancutoff')

    cut_verts = [bm.verts.new(obimat * co) for co in verts]
    cut_edges = [bm.edges.new((cut_verts[v1], cut_verts[v2]))
                for v1, v2, in edges]
    cut_faces = [bm.faces.new([cut_verts[v] for v in f]) for f in faces]
    cutting_elems = cut_verts + cut_edges + cut_faces
    cutting_elems = set(cutting_elems)
    for f in bm.faces:
        f[layer] = 0  # エラーが原因でlayerが残っている場合に初期化が必要
    for f in cut_faces:
        f[layer] = 1

    # polygonを時計回りに書いていた場合に法線を直す
    bmesh.ops.recalc_face_normals(bm, faces=cut_faces)
    # bm.normal_update()
    bmesh.update_edit_mesh(ob.data)

    # UV展開
    unwrap_uvs_edit(bm, cut_faces)

    # boolean
    hidden_elems = []
    for ele in itertools.chain(bm.faces, bm.edges, bm.verts):
        if not ele.hide:
            if not ele.select and ele not in cutting_elems:
                ele.hide = True
                hidden_elems.append(ele)
    # 非選択要素で選択要素を切り取る(DIFFERENCE)
    operation = 'INTERSECT' if reverse else 'DIFFERENCE'
    bpy.ops.mesh.intersect_boolean(operation=operation, use_swap=True)

    bpy.ops.mesh.select_all(action='SELECT')

    for ele in hidden_elems:
        if ele.is_valid:
            ele.hide = False

    # material
    bm = bmesh.from_edit_mesh(ob.data)
    layer = bm.faces.layers.int['booleancutoff']
    for face in bm.faces:
        if face[layer]:
            # material
            materials = []
            for edge in face.edges:
                for f in edge.link_faces:
                    if not f[layer]:
                        materials.append(f.material_index)
            if not materials:
                for edge in face.edges:
                    for f in edge.link_faces:
                        for e in f.edges:
                            for f2 in e.link_faces:
                                if not f2[layer]:
                                    materials.append(f2.material_index)
            if materials:
                count = {materials.count(k): k for k in set(materials)}
                face.material_index = count[max(count)]
            # texture image
            for tex_layer in bm.faces.layers.tex.values():
                images = []
                for edge in face.edges:
                    for f in edge.link_faces:
                        if not f[layer]:
                            images.append(f[tex_layer].image)
                if not images:
                    for edge in face.edges:
                        for f in edge.link_faces:
                            for e in f.edges:
                                for f2 in e.link_faces:
                                    if not f2[layer]:
                                        images.append(f2[tex_layer].image)
                if images:
                    count = {images.count(k): k for k in set(images)}
                    face[tex_layer].image = count[max(count)]
            # UV。割と適当
            for uv_layer in bm.loops.layers.uv.values():
                for vert in face.verts:
                    uvs = []
                    for loop in vert.link_loops:
                        if loop.face != face:
                            uvs.append(tuple(loop[uv_layer].uv))
                    if uvs:
                        uv = uvs.pop()
                        for loop in vert.link_loops:
                            if loop.face == face:
                                loop[uv_layer].uv = uv

    bm.faces.layers.int.remove(layer)

    bmesh.update_edit_mesh(ob.data)


def _intersect_object(context, verts, edges, faces, reverse):
    """
    :type context: bpy.types.Context
    :type verts: list
    :type edges: list
    :type faces: list
    :type reverse: bool
    """

    actob = context.active_object
    imat = actob.matrix_world.inverted()
    mesh = bpy.data.meshes.new('tmp')
    mesh_name = mesh.name
    mesh.from_pydata([imat * v for v in verts], edges, faces)
    mesh.update(calc_edges=True, calc_tessface=True)

    # polygonを時計回りに書いていた場合に法線を直す
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)

    ob = bpy.data.objects.new('tmp', mesh)
    ob.matrix_world = actob.matrix_world
    ob_name = ob.name
    context.scene.objects.link(ob)

    unwrap_uvs(context, ob, actob)

    mod = actob.modifiers.new('Boolean Cutoff', 'BOOLEAN')
    mod.object = ob
    mod.operation = 'INTERSECT' if reverse else 'DIFFERENCE'
    i = list(actob.modifiers).index(mod)
    for _ in range(i):
        bpy.ops.object.modifier_move_up(modifier=mod.name)

    # booleanで生成された面は選択状態になる
    me = actob.data
    me.polygons.foreach_set('select', [False] * len(me.polygons))
    me.edges.foreach_set('select', [False] * len(me.edges))
    me.vertices.foreach_set('select', [False] * len(me.vertices))

    bpy.ops.object.modifier_apply(modifier=mod.name)

    # material
    # (index, index) -> MeshEdge
    ekey_edge = {}
    for edge in actob.data.edges:
        ekey_edge[edge.key] = edge
    # (index, index) -> MeshPolygon
    ekey_polys = collections.defaultdict(list)
    for poly in actob.data.polygons:
        for key in poly.edge_keys:
            ekey_polys[key].append(poly)
    # index -> MeshLoop
    vert_loops = collections.defaultdict(list)
    for loop in actob.data.loops:
        vert_loops[loop.vertex_index].append(loop)

    for poly in actob.data.polygons:
        if poly.select:
            # material
            materials = []
            for ekey in poly.edge_keys:
                for f in ekey_polys[ekey]:
                    if not f.select:
                        materials.append(f.material_index)
            if not materials:
                for ekey in poly.edge_keys:
                    for f in ekey_polys[ekey]:
                        for k in f.edge_keys:
                            for f2 in ekey_polys[k]:
                                if not f2.select:
                                    materials.append(f2.material_index)
            if materials:
                count = {materials.count(k): k for k in set(materials)}
                poly.material_index = count[max(count)]
            # texture image
            for tex_layer in actob.data.uv_textures:
                images = []
                for ekey in poly.edge_keys:
                    for f in ekey_polys[ekey]:
                        if not f.select:
                            images.append(tex_layer.data[f.index].image)
                if not images:
                    for ekey in poly.edge_keys:
                        for f in ekey_polys[ekey]:
                            for k in f.edge_keys:
                                for f2 in ekey_polys[k]:
                                    if not f2.select:
                                        images.append(
                                            tex_layer.data[f2.index].image)
                if images:
                    count = {images.count(k): k for k in set(images)}
                    tex_layer.data[poly.index].image = count[max(count)]
            # UV。割と適当
            poly_loops = list(range(poly.loop_start,
                                    poly.loop_start + poly.loop_total))
            for uv_layer in actob.data.uv_layers:
                for vert in poly.vertices:
                    uvs = []
                    for loop in vert_loops[vert]:
                        if loop.index not in poly_loops:
                            uvs.append(tuple(uv_layer.data[loop.index].uv))
                    if uvs:
                        uv = uvs.pop()
                        for loop in vert_loops[vert]:
                            if loop.index in poly_loops:
                                uv_layer.data[loop.index].uv = uv

    ob = bpy.data.objects[ob_name]
    mesh = bpy.data.meshes[mesh_name]
    context.scene.objects.unlink(ob)
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(mesh)


def calc_circle_coords(loc, radius, segments, direction):
    coords = []
    angle = math.pi * 2 / segments
    start = math.pi * 0.5
    d = {'VERT_TOP': 0, 'EDGE_TOP': 1, 'VERT_RIGHT': 2, 'EDGE_RIGHT': 3}
    direction = d[direction]
    if direction % 2 == 1:
        start += angle / 2
    start -= math.pi * 0.5 * int(direction / 2)

    for i in range(segments):
        a = math.pi * 2 / segments * i + start
        x = math.cos(a) * radius
        y = math.sin(a) * radius
        coords.append(loc + Vector([x, y]))
    return coords


def intersect(context, mode, mouse_coords, reverse, circle_segments,
              circle_direction, use_cursor_limit):
    """
    :type context: bpy.types.Context
    """
    EPS = 0.2
    EPS_PX = 3

    # 重複除去
    _mouse_coords = []
    for co in mouse_coords:
        if not _mouse_coords or _mouse_coords[-1] != co:
            _mouse_coords.append(co)
    mouse_coords = _mouse_coords

    if len(mouse_coords) < 2:
        return

    region = context.region
    rv3d = context.region_data
    vmat = rv3d.view_matrix
    pmat = rv3d.perspective_matrix
    view_axis = vmat.inverted().col[2].to_3d()  # 奥から手前に向かう

    ob = context.active_object
    obmat = ob.matrix_world
    obimat = obmat.inverted()

    # bound_box xyz: [---, --+, -++, -+-, +--, +-+, +++, ++-]
    bb = [obmat * Vector(v) for v in ob.bound_box]  # edit modeでも更新される
    bb_proj = [project(region, rv3d, v).to_2d() for v in bb]

    dists = [(v - bb[0]).project(view_axis).dot(view_axis) for v in bb]
    depth_loc_near = bb[dists.index(max(dists))] + view_axis * EPS
    if use_cursor_limit:
        depth_loc_far = context.scene.cursor_location
    else:
        depth_loc_far = bb[dists.index(min(dists))] - view_axis * EPS

    if mode == 'LINE':
        p1, p2 = mouse_coords
        bb_proj_ofs = [v - p1 for v in bb_proj]

        line = (p2 - p1).normalized()
        ofs = line * EPS_PX
        dists = [v.project(line).dot(line) for v in bb_proj_ofs]
        i = dists.index(min(dists))
        line_min = bb_proj_ofs[i].project(line) + p1 - ofs
        i = dists.index(max(dists))
        line_max = bb_proj_ofs[i].project(line) + p1 + ofs

        normal = Vector([-line[1], line[0]])
        dists = [v.project(normal).dot(normal) for v in bb_proj_ofs]
        # i = dists.index(min(dists))
        # normal_min_f = bb_proj_ofs[i].project(normal).dot(normal) - eps
        i = dists.index(max(dists))
        normal_max_f = bb_proj_ofs[i].project(normal).dot(normal) + EPS_PX
        vec = normal * normal_max_f
        coords = [line_min, line_max, line_max + vec, line_min + vec]

    elif mode == 'BOX':
        p1, p2 = mouse_coords
        p3 = Vector([p1[0], p2[1]])
        p4 = Vector([p2[0], p1[1]])
        coords = [p1, p2, p3, p4]
        coords.sort(key=lambda v: (v[1], v[0]))
        coords = coords[:2] + [coords[3], coords[2]]

    elif mode == 'CIRCLE':
        p1, p2 = mouse_coords
        radius = (p2 - p1).length
        coords = calc_circle_coords(p1, radius, circle_segments,
                                    circle_direction)

    else:  # if mode == 'POLYGON':
        coords = mouse_coords

    vert_coords_near = [
        unproject(region, rv3d, co, depth_loc_near)
        for co in coords]
    vert_coords_far = [
        unproject(region, rv3d, co, depth_loc_far)
        for co in coords]

    num = len(coords)
    verts = vert_coords_near + vert_coords_far
    edges = ([((i - 1) % num, i) for i in range(num)] +
             [((i - 1) % num + num, i + num) for i in range(num)] +
             [(i, i + num) for i in range(num)]
             )
    faces = [list(range(num)),
             list(range(num, num + num))[::-1],
             *[(i, (i - 1) % num, (i - 1) % num + num, i + num)
               for i in range(num)]]

    # boolean
    if context.mode == 'EDIT_MESH':
        _intersect_edit(context, verts, edges, faces, reverse)
    else:
        _intersect_object(context, verts, edges, faces, reverse)


class GrabCursor:
    """Continuous Grab (bl_optionsの'GRAB_CURSOR')を再現する。
    modal operator 実行中に他の modal operator を呼ぶと、それが終了した際に
    Continuous Grab が無効化される為。
    """
    def __init__(self):
        self._grab_cursor_wrapping = [None, None]
        """:type: list[int]"""
        self._grab_cursor_outside = False

    def grab_cursor(self, context, event, disable=False):
        """invoke()とmodal()で実行。
        動作中にcontext.regionが変更されないことを前提としている。
        :type context: bpy.types.Context
        :type event: bpy.types.Event
        :param disable: _grab_cursor_wrappingを[0, 0]にした後、
            一時的に無効化する。
        :type disable: Bool
        :return: マウスカーソルのRegion座標
        :rtype: (int, int)
        """

        mx, my = event.mouse_x, event.mouse_y
        area = context.area
        region = context.region
        x, y, w, h = region.x, region.y, region.width, region.height

        U = context.user_preferences
        if not U.inputs.use_mouse_continuous:
            return mx - x, my - y

        if disable:
            self._grab_cursor_wrapping[:] = [0, 0]
            return mx - x, my - y

        if self._grab_cursor_wrapping == [None, None]:
            if not (x <= mx <= x + w - 1 and y <= my <= y + h - 1):
                self._grab_cursor_outside = True
            self._grab_cursor_wrapping[:] = [0, 0]

        if self._grab_cursor_outside:
            x, y, w, h = area.x, area.y, area.width, area.height

        wrapping = self._grab_cursor_wrapping[:]
        if mx < x:
            wrapping[0] -= 1
        elif mx > x + w - 1:
            wrapping[0] += 1
        if my < y:
            wrapping[1] -= 1
        elif my > y + h - 1:
            wrapping[1] += 1
        mx_warp = (mx - x) % w + x
        my_warp = (my - y) % h + y
        if wrapping != self._grab_cursor_wrapping:
            context.window.cursor_warp(mx_warp, my_warp)
            self._grab_cursor_wrapping[:] = wrapping

        return (mx_warp + self._grab_cursor_wrapping[0] * w - region.x,
                my_warp + self._grab_cursor_wrapping[1] * h - region.y)


class MESH_OT_intersect_cutoff(GrabCursor, bpy.types.Operator):
    bl_idname = 'mesh.intersect_cutoff'
    bl_label = 'Intersect (Cutoff)'

    bl_options = {'REGISTER', 'UNDO'}

    props = ('mode', 'reverse', 'use_cursor_limit', 'circle_segments',
             'circle_direction', 'continuity')
    mode = bpy.props.EnumProperty(
        name='Mode',
        items=[('LINE', 'Line', ''),
               ('BOX', 'Box', ''),
               ('CIRCLE', 'Circle', ''),
               ('POLYGON', 'Polygon', ''),
               ],
        default='LINE'
    )
    reverse = bpy.props.BoolProperty(
        name='reverse'
    )
    use_cursor_limit = bpy.props.BoolProperty(
        name='Cursor Limit',
        default=False
    )
    circle_segments = bpy.props.IntProperty(
        name='Circle Vertices',
        default=16,
        min=3,
        max=500
    )
    # circle_direction = bpy.props.IntProperty(
    #     name='Circle Direction',
    #     default=0,
    #     min=0,
    #     max=3,
    # )
    circle_direction = bpy.props.EnumProperty(
        name='Circle Direction',
        items=[
            ('VERT_TOP', 'Vert Top', ''),
            ('EDGE_TOP', 'Edge Top', ''),
            ('VERT_RIGHT', 'Vert Right', ''),
            ('EDGE_RIGHT', 'Edge Right', '')
        ],
        default='VERT_TOP',
    )
    continuity = bpy.props.BoolProperty(
        name='Continuity',
        default=True
    )

    # prop_values = {}

    @classmethod
    def poll(cls, context):
        """
        :type context: bpy.types.Context
        """
        if context.area.type == 'VIEW_3D':
            ob = context.active_object
            return ob and ob.type == 'MESH' and ob.mode in {'EDIT', 'OBJECT'}

    def prop_save(self, context):
        """変更のあったプロパティーを手動で保存する。
        executeが無い所為？でmodal中での変更が保存されないから。
        """
        wm = context.window_manager
        for name, prop in self.rna_type.properties.items():
            if name == 'rna_type' or prop.is_skip_save:
                continue
            if self.properties.is_property_set(name):
                # self.prop_values[name] = getattr(self, name)
                setattr(wm.quick_boolean.cutoff, name, getattr(self, name))

    def prop_load(self, context):
        """変更のあったプロパティーを手動で読み込む。
        executeが無い所為？でmodal中での変更が保存されないから。
        """
        wm = context.window_manager
        for name, prop in self.rna_type.properties.items():
            if name == 'rna_type' or prop.is_skip_save:
                continue
            if not self.properties.is_property_set(name):
                # if name in self.prop_values:
                #     setattr(self, name, self.prop_values[name])
                setattr(self, name, getattr(wm.quick_boolean.cutoff, name))

    def header_text_set(self, context):
        """
        :type context: bpy.types.Context
        """
        def kmi_to_str(kmi):
            prop = bpy.types.Event.bl_rna.properties['type']
            for enum_item in prop.enum_items:
                if enum_item.identifier == kmi.type:
                    name = enum_item.name
            mods = []
            for mod in ('shift', 'ctrl', 'alt', 'oskey'):
                if getattr(kmi, mod):
                    mods.append(mod.title())
            if mods:
                return '+'.join(mods) + '+' + name
            else:
                return name

        def on_off(value):
            return 'ON' if value else 'OFF'

        text = 'Mode (TAB/L/B/C/P): {}'.format(self.mode.title())
        text += ', reverse (R): {}'.format(on_off(self.reverse))
        if self.mode == 'POLYGON':
            text += ', Apply Polygon (Space/Ret/LDoubleClick)'
        if self.mode == 'CIRCLE':
            if self.left_mouse:
                fmt = ', Segments (+/-/WheelUp/WheelDown): {}'
            else:
                fmt = ', Segments (+/-): {}'
            text += fmt.format(self.circle_segments)
            d = self.circle_direction.replace('_', ' ').title()
            text += ', Direction (D): {}'.format(d)

        text += ', Cursor Limit (Z): ' + on_off(self.use_cursor_limit)

        text += ', Snap Grid (Ctrl): ' + on_off(self.mco_ctrl)
        text += ', Precision (Shift): ' + on_off(self.mco_shift)
        text += ', Move (Alt): ' + on_off(self.mco_shift)

        if not self.left_mouse:
            if self.undo_keymap_items:
                text += ', Undo ({})'.format(
                    kmi_to_str(self.undo_keymap_items[0]))
            if self.redo_keymap_items:
                text += ', Redo ({})'.format(
                    kmi_to_str(self.redo_keymap_items[0]))

        # text += ', mco: [{}, {}]'.format(int(self.mco[0]), int(self.mco[1]))
        context.area.header_text_set(text)

    def header_text_clear(self, context):
        """
        :type context: bpy.types.Context
        """
        context.area.header_text_set()

    def bmesh_to_mesh(self, context, bm, mesh):
        mode = context.mode
        if mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT', toggle=True)
        bm.to_mesh(mesh)
        if mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT', toggle=True)

    def undo(self, context):
        """
        :type context: bpy.types.Context
        """
        if self.history_index == -1:
            return
        self.history_index -= 1
        bpy.ops.ed.undo()

    def redo(self, context):
        """
        :type context: bpy.types.Context
        """
        if self.history_index == self.history_count - 1:
            return
        self.history_index += 1
        bpy.ops.ed.redo()

    def exit(self, context):
        """
        :type context: bpy.types.Context
        """
        bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
        self.prop_save(context)
        self.header_text_clear(context)
        self.bm_bak = None

    def cancel(self, context):
        """
        :type context: bpy.types.Context
        """
        # self.bmesh_to_mesh(context, self.bm_bak, context.active_object.data)
        for _ in range(self.history_count):
            bpy.ops.ed.undo()
        bpy.ops.ed.flush_edits()

    def find_keymap_items(self, context):
        kc = context.window_manager.keyconfigs.active  # 'Blender'
        for kmi in kc.keymaps['3D View'].active().keymap_items:
            if kmi.idname in view_operators:
                self.view_keymap_items.append(kmi)

        for kmi in kc.keymaps['Screen'].active().keymap_items:
            if kmi.idname == 'ed.undo':
                self.undo_keymap_items.append(kmi)
            if kmi.idname == 'ed.redo':
                self.redo_keymap_items.append(kmi)

    def is_keymap_item_event(self, context, event, kmi):
        U = context.user_preferences
        right_select = U.inputs.select_mouse == 'RIGHT'
        invert_wheel = U.inputs.invert_zoom_wheel

        kmi_type = kmi.type
        if kmi_type == 'SELECTMOUSE':
            kmi_type = 'RIGHTMOUSE' if right_select else 'LEFTMOUSE'
        elif kmi_type == 'ACTIONMOUSE':
            kmi_type = 'LEFTMOUSE' if right_select else 'RIGHTMOUSE'
        elif kmi_type == 'EVT_TWEAK_S':
            kmi_type = 'EVT_TWEAK_R' if right_select else 'EVT_TWEAK_L'
        elif kmi_type == 'EVT_TWEAK_A':
            kmi_type = 'EVT_TWEAK_L' if right_select else 'EVT_TWEAK_R'
        elif kmi_type == 'WHEELINMOUSE':
            kmi_type = 'WHEELDOWNMOUSE' if invert_wheel else 'WHEELUPMOUSE'
        elif kmi_type == 'WHEELOUTMOUSE':
            kmi_type = 'WHEELUPMOUSE' if invert_wheel else 'WHEELDOWNMOUSE'
        if kmi_type == event.type and kmi.value == event.value:
            match = True
            if not kmi.any:
                # 'key_modifier'は無視
                for mod in ('shift', 'ctrl', 'alt', 'oskey'):
                    if getattr(kmi, mod) != getattr(event, mod):
                        match = False
            if match:
                return True
        return False

    def is_view_event(self, context, event):
        for kmi in self.view_keymap_items:
            if self.is_keymap_item_event(context, event, kmi):
                return True
        return False

    def is_undo_event(self, context, event):
        for kmi in self.undo_keymap_items:
            if self.is_keymap_item_event(context, event, kmi):
                return True
        return False

    def is_redo_event(self, context, event):
        for kmi in self.redo_keymap_items:
            if self.is_keymap_item_event(context, event, kmi):
                return True
        return False

    def modified_mouse_coord(self, context):
        region = context.region
        rv3d = context.region_data

        mco = self.mco
        if self.mco_shift:
            mco = self.mco_shift + (mco - self.mco_shift) * 0.1

        if self.mco_ctrl:
            co = unproject(region, rv3d, mco)
            unit_system = unitsystem.UnitSystem(context)
            co = unit_system.snap_local_grid(context, co, self.mco_shift)
            mco = project(region, rv3d, co).to_2d()

        return mco

    def intersect(self, context):
        intersect(context, self.mode, self.mouse_coords,
                  self.reverse, self.circle_segments, self.circle_direction,
                  self.use_cursor_limit)

        self.history_count += 1
        self.history_index += 1
        msg = self.bl_label + ' (modal)'
        bpy.ops.ed.undo_push(message=msg)

    def alt_move(self, context):
        """alt key押しっぱなしで移動"""
        if self.mco_alt and self.mouse_coords_alt_press:
            unit_system = unitsystem.UnitSystem(context)
            vec = self.mco_mod - self.mco_alt
            if self.mco_ctrl:
                scalar = unit_system.dpg
                if self.mco_shift:
                    scalar *= 0.1
                dx = unit_system.snap_value(vec[0], scalar)
                dy = unit_system.snap_value(vec[1], scalar)
            else:
                dx, dy = vec
            for i, co in enumerate(self.mouse_coords_alt_press):
                self.mouse_coords[i] = co + Vector((dx, dy))
            return True
        else:
            return False

    def modal(self, context, event):
        """
        :type context: bpy.types.Context
        :type event: bpy.types.Event
        :rtype: set
        """

        if (event.type == 'INBETWEEN_MOUSEMOVE' or
                event.type.startswith('TIMER')):
            return {'RUNNING_MODAL'}

        shift = (event.shift or event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT'} and
                 event.value == 'PRESS')
        self.mco = mco = Vector(self.grab_cursor(context, event, not shift))

        block = False

        context.area.tag_redraw()

        if event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT'}:
            if event.value == 'PRESS':
                if self.mco_ctrl:
                    self.mco_shift = self.mco_mod.copy()
                else:
                    self.mco_shift = mco.copy()
            elif event.value == 'RELEASE':
                self.mco_shift = None
            block = True
        elif event.type in {'LEFT_CTRL', 'RIGHT_CTRL'}:
            if event.value == 'PRESS':
                self.mco_ctrl = mco.copy()
            elif event.value == 'RELEASE':
                self.mco_ctrl = None
            block = True
        elif event.type in {'LEFT_ALT', 'RIGHT_ALT'}:
            if event.value == 'PRESS':
                self.mco_alt = mco.copy()
                self.mouse_coords_alt_press = self.mouse_coords[:]
            elif event.value == 'RELEASE':
                self.mco_alt = None
                self.mouse_coords_alt_press.clear()
            block = True

        mco_mod = self.modified_mouse_coord(context)
        if self.mouse_coords and self.mode != 'POLYGON':
            if not self.mouse_coords_alt_press:
                self.mouse_coords[-1] = mco_mod
        self.mco_mod = mco_mod.copy()

        self.alt_move(context)

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if self.mode in {'LINE', 'BOX', 'CIRCLE'}:
                    self.mouse_coords.extend([mco_mod, mco_mod])
                else:
                    self.mouse_coords.append(mco_mod)
                self.left_mouse = True
            elif event.value == 'RELEASE':
                if self.mode in {'LINE', 'BOX', 'CIRCLE'}:
                    self.intersect(context)
                    self.mouse_coords.clear()
                    self.mouse_coords_alt_press.clear()
                    if not self.continuity:
                        self.exit(context)
                        return {'FINISHED'}
                elif self.mode == 'POLYGON':
                    if (len(self.mouse_coords) >= 2 and
                            self.mouse_coords[-2] == self.mouse_coords[-1]):
                        # double click扱い
                        self.mouse_coords.pop(-1)
                        self.intersect(context)
                        self.mouse_coords.clear()
                        self.mouse_coords_alt_press.clear()
                        if not self.continuity:
                            self.exit(context)
                            return {'FINISHED'}
                self.left_mouse = False
            block = True

        elif event.type in {'SPACE', 'RET', 'NUMPAD_ENTER'}:
            if event.value == 'PRESS':
                if self.mode == 'POLYGON' and self.mouse_coords:
                    self.intersect(context)
                    self.mouse_coords.clear()
                    self.mouse_coords_alt_press.clear()
                    if not self.continuity:
                        self.exit(context)
                        return {'FINISHED'}
                else:
                    self.exit(context)
                    return {'FINISHED'}
            block = True

        elif event.type == 'MOUSEMOVE':
            if self.mco_alt and self.mouse_coords_alt_press:
                pass
            else:
                if self.left_mouse and self.mouse_coords:
                    self.mouse_coords[-1] = mco_mod
            block = True

        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            if event.value == 'PRESS':
                if self.mouse_coords:
                    self.mouse_coords.clear()
                    self.mouse_coords_alt_press.clear()
                else:
                    self.cancel(context)
                    self.exit(context)
                    return {'CANCELLED'}
            block = True

        elif event.type == 'TAB':
            if event.value == 'PRESS':
                values = ['LINE', 'BOX', 'CIRCLE', 'POLYGON']
                i = values.index(self.mode)
                self.mode = values[(i + 1) % len(values)]
            block = True
        elif event.type == 'L':
            if event.value == 'PRESS':
                self.mode = 'LINE'
                self.mouse_coords.clear()
                self.mouse_coords_alt_press.clear()
            block = True
        elif event.type == 'B':
            if event.value == 'PRESS':
                self.mode = 'BOX'
                self.mouse_coords.clear()
                self.mouse_coords_alt_press.clear()
            block = True
        elif event.type == 'C':
            if event.value == 'PRESS':
                self.mode = 'CIRCLE'
                self.mouse_coords.clear()
                self.mouse_coords_alt_press.clear()
            block = True
        elif event.type == 'P':
            if event.value == 'PRESS':
                self.mode = 'POLYGON'
                self.mouse_coords.clear()
                self.mouse_coords_alt_press.clear()
            block = True
        elif event.type == 'R':
            if event.value == 'PRESS':
                self.reverse ^= True
            block = True
        elif event.type == 'NUMPAD_PLUS':
            if event.value == 'PRESS':
                self.circle_segments += 1
            block = True
        elif event.type == 'NUMPAD_MINUS':
            if event.value == 'PRESS':
                self.circle_segments -= 1
            block = True
        elif event.type == 'D':
            if event.value == 'PRESS':
                items = {'VERT_TOP': 0, 'EDGE_TOP': 1, 'VERT_RIGHT': 2,
                         'EDGE_RIGHT': 3}
                i = (items[self.circle_direction] + 1) % 4
                self.circle_direction = {v: k for k, v in items.items()}[i]
            block = True
        elif event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            if self.mode == 'CIRCLE' and self.left_mouse:
                if event.value == 'PRESS':
                    if event.type == 'WHEELUPMOUSE':
                        self.circle_segments += 1
                    else:
                        self.circle_segments -= 1
                block = True

        elif event.type == 'Z':
            if (not event.shift and not event.ctrl and not event.alt and
                    not event.oskey):
                if event.value == 'PRESS':
                    self.use_cursor_limit ^= True
                block = True

        if not block:
            if self.left_mouse:
                block = True
            elif self.is_undo_event(context, event):
                self.undo(context)
                block = True
            elif self.is_redo_event(context, event):
                self.redo(context)
                block = True
            elif self.is_view_event(context, event):
                pass
            else:
                block = True

        self.header_text_set(context)

        return {'RUNNING_MODAL'} if block else {'PASS_THROUGH'}

    def invoke(self, context, event):
        """
        :type context: bpy.types.Context
        :type event: bpy.types.Event
        :rtype: set
        """
        self.handle = None
        self.bm_bak = None  # BMesh
        self.history_count = 0
        self.history_index = -1
        self.mouse_coords = []  # region coords (2D Vector)
        self.mouse_coords_alt_press = []
        self.mco = self.mco_mod = None
        self.left_mouse = False
        self.mco_shift = self.mco_ctrl = self.mco_alt = None
        self.view_keymap_items = []
        self.undo_keymap_items = []
        self.redo_keymap_items = []

        self.mco = Vector(self.grab_cursor(context, event))
        self.mco_mod = self.mco

        self.find_keymap_items(context)

        self.prop_load(context)

        wm = context.window_manager
        wm.modal_handler_add(self)
        self.handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback, (context,), 'WINDOW', 'POST_PIXEL')

        self.header_text_set(context)
        context.area.tag_redraw()

        return {'RUNNING_MODAL'}

    def draw_callback(self, context):
        """
        :type context: bpy.types.Context
        """

        prefs = QuickBooleanPreferences.get_instance()
        color = prefs.color
        snap_color = prefs.snap_color

        region = context.region

        glsettings = vagl.GLSettings(context)
        glsettings.push()

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(*color)

        show_reversed = False
        if self.reverse:
            if self.mode == 'POLYGON':
                if len(self.mouse_coords) >= 3:
                    show_reversed = True
            else:
                if len(self.mouse_coords) >= 2:
                    if self.mouse_coords[0] != self.mouse_coords[1]:
                        show_reversed = True
        if show_reversed:
            bgl.glEnable(bgl.GL_DEPTH_TEST)
            bgl.glClearDepth(1.0)
            bgl.glClear(bgl.GL_DEPTH_BUFFER_BIT)
            bgl.glDepthMask(1)
            bgl.glColorMask(0, 0, 0, 0)

        lines = []
        if self.mouse_coords:
            if self.mode == 'LINE':
                w = region.width
                h = region.height
                p1, p2 = self.mouse_coords
                line = (p2 - p1).normalized()
                normal = Vector([-line[1], line[0]])
                corners = [Vector([0, 0]), Vector([w, 0]), Vector([w, h]),
                           Vector([0, h])]
                corners_ofs = [v - p1 for v in corners]
                dists = [v.project(line).dot(line) for v in corners_ofs]
                i = dists.index(min(dists))
                line_min = corners_ofs[i].project(line) + p1
                i = dists.index(max(dists))
                line_max = corners_ofs[i].project(line) + p1
                dists = [v.project(normal).dot(normal) for v in corners_ofs]
                i = dists.index(max(dists))
                normal_max_f = corners_ofs[i].project(normal).dot(normal)
                vec = normal * normal_max_f
                coords = [line_min, line_max, line_max + vec, line_min + vec]
                bgl.glBegin(bgl.GL_QUADS)
                for co in coords:
                    bgl.glVertex2f(*co)
                bgl.glEnd()
                lines = self.mouse_coords

            elif self.mode == 'BOX':
                p1, p2 = self.mouse_coords
                bgl.glRectf(p1[0], p1[1], p2[0], p2[1])
                lines = [p1,
                         Vector((p2[0], p1[1])),
                         Vector((p2[0], p2[1])),
                         Vector((p1[0], p2[1])),
                         p1]
            elif self.mode == 'CIRCLE':
                p1, p2 = self.mouse_coords
                bgl.glBegin(bgl.GL_TRIANGLE_FAN)
                bgl.glVertex2f(*p1)
                r = (p2 - p1).length
                coords = calc_circle_coords(p1, r, self.circle_segments,
                                            self.circle_direction)
                for co in coords:
                    bgl.glVertex2f(*co)
                bgl.glVertex2f(*coords[0])
                bgl.glEnd()
                lines = coords + [coords[0]]
            elif self.mode == 'POLYGON':
                if len(self.mouse_coords) >= 3:
                    tris = mathutils.geometry.tessellate_polygon(
                        [[co.to_3d() for co in self.mouse_coords]])

                    bgl.glBegin(bgl.GL_TRIANGLES)
                    for tri in tris:
                        for i in tri:
                            bgl.glVertex2f(*self.mouse_coords[i])
                    bgl.glEnd()
                if len(self.mouse_coords) > 1:
                    lines = self.mouse_coords + [self.mouse_coords[0]]

        if show_reversed:
            bgl.glColorMask(1, 1, 1, 1)
            bgl.glBegin(bgl.GL_QUADS)
            bgl.glVertex3f(0, 0, -1)
            bgl.glVertex3f(region.width, 0, -1)
            bgl.glVertex3f(region.width, region.height, -1)
            bgl.glVertex3f(0, region.height, -1)
            bgl.glEnd()
            bgl.glDisable(bgl.GL_DEPTH_TEST)

        bgl.glColor4f(*color[:3], 1.0)
        bgl.glPointSize(1)
        bgl.glLineWidth(1)
        if len(lines) > 1:
            bgl.glBegin(bgl.GL_LINE_STRIP)
            for co in lines:
                bgl.glVertex2f(*co)
            bgl.glEnd()
        if self.mode == 'POLYGON':
            if len(self.mouse_coords) == 1:
                bgl.glPointSize(5)
                bgl.glBegin(bgl.GL_POINTS)
                for co in self.mouse_coords:
                    bgl.glVertex2f(*co)
                bgl.glEnd()
                bgl.glPointSize(1)
                bgl.glLineWidth(1)

        if self.mco_ctrl:
            SIZE = 12
            bgl.glColor4f(*snap_color)
            bgl.glBegin(bgl.GL_LINE_LOOP)
            v = self.mco_mod
            x = v[0] - SIZE / 2
            y = v[1] - SIZE / 2
            bgl.glVertex2f(x, y)
            bgl.glVertex2f(x + SIZE, y)
            bgl.glVertex2f(x + SIZE, y + SIZE)
            bgl.glVertex2f(x, y + SIZE)
            bgl.glEnd()

        glsettings.pop()
        glsettings.font_size()


namespace = collections.OrderedDict()
for attr in MESH_OT_intersect_cutoff.props:
    namespace[attr] = getattr(MESH_OT_intersect_cutoff, attr)
namespace['show_boolean_cutoff'] = bpy.props.BoolProperty()

BooleanCutoffProperties = type(
    'BooleanCutoffProperties', (bpy.types.PropertyGroup,), namespace)


class QuickBooleanProperties(bpy.types.PropertyGroup):
    cutoff = bpy.props.PointerProperty(type=BooleanCutoffProperties)


class QuickBooleanPanel(bpy.types.Panel):
    bl_idname = 'QuickBooleanPanel'
    bl_label = 'Quick Boolean'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'

    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob and ob.type == 'MESH' and ob.mode in {'EDIT', 'OBJECT'}

    @classmethod
    def draw_property(cls, src, src_properties, attr, layout, text=None,
                      skip_hidden=True, row=False, **kwargs):

        """オペレータ実行時のプロパティ表示を再現する。
        :type attr: str
        :type layout: bpy.types.UILayout
        :type text: str
        :type skip_hidden: bool
        :type row: bool
        :rtype: bpy.types.UILayout
        """
        if attr == 'rna_type':
            return None

        prop = src_properties[attr] if attr in src_properties else None

        if skip_hidden and prop.is_hidden:
            return None

        col = layout.column(align=True)
        sub = col.row()
        name = prop.name if text is None else text
        if prop.type == 'BOOLEAN' and prop.array_length == 0:
            sub.prop(src, attr, text=name, **kwargs)
        else:
            if name:
                sub.label(name + ':')
            sub = col.row() if row else col.column()
            if prop.type == 'ENUM' and \
                    (prop.is_enum_flag or 'expand' in kwargs):
                sub.prop(src, attr, **kwargs)  # text='' だとボタン名が消える為
            else:
                sub.prop(src, attr, text='', **kwargs)

        return col

    def draw(self, context):
        wm = context.window_manager
        props = wm.quick_boolean

        layout = self.layout
        """:type: bpy.types.UILayout"""

        column = layout.column(align=True)

        # 組み込み
        column.operator('mesh.intersect')
        column.operator('mesh.intersect_boolean')

        # LoopToolsの配置が好きなので真似た
        show_boolean_cutoff = props.cutoff.show_boolean_cutoff
        row = column.row(align=True)
        icon = 'DOWNARROW_HLT' if show_boolean_cutoff else 'RIGHTARROW'
        row.prop(props.cutoff, 'show_boolean_cutoff', text='', icon=icon)
        row.operator('mesh.intersect_cutoff', text='Cutoff')

        if show_boolean_cutoff:
            box = column.box()
            col = box.column()
            """
            NOTE: オペレータのプロパティーはget_rna()を経ていないと取得出来ない
            """
            rna = bpy.ops.mesh.intersect_cutoff.get_rna()
            for attr in rna.bl_rna.properties.keys():
                self.draw_property(props.cutoff, rna.bl_rna.properties, attr,
                                   col)


classes = [
    QuickBooleanPreferences,
    MESH_OT_intersect_cutoff,
    QuickBooleanPanel,
    BooleanCutoffProperties,
    QuickBooleanProperties,
]


addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.quick_boolean = bpy.props.PointerProperty(
        type=QuickBooleanProperties
    )

    wm = bpy.context.window_manager

    kc = wm.keyconfigs.addon
    if kc:
        addon_prefs = QuickBooleanPreferences.get_instance()
        """:type: QuickBooleanPreferences"""
        km = addon_prefs.get_keymap('Mesh')
        kmi = km.keymap_items.new('mesh.intersect_cutoff', 'B', 'PRESS',
                                  shift=True, ctrl=True, alt=True, oskey=True)
        kmi.active = False
        addon_keymaps.append((km, kmi))

        km = addon_prefs.get_keymap('Object Mode')
        kmi = km.keymap_items.new('mesh.intersect_cutoff', 'B', 'PRESS',
                                  shift=True, ctrl=True, alt=True, oskey=True)
        kmi.active = False
        addon_keymaps.append((km, kmi))

        addon_prefs.register_keymap_items(addon_keymaps)


def unregister():
    addon_prefs = QuickBooleanPreferences.get_instance()
    """:type: QuickBooleanPreferences"""
    addon_prefs.unregister_keymap_items()

    del bpy.types.WindowManager.quick_boolean
    try:
        del bpy.context.window_manager['quick_boolean']
    except:
        # traceback.print_exc()
        pass

    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)
