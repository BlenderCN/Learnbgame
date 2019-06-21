import bpy
import bmesh

from math import pi, cos, sin
from mathutils import Vector, Matrix

from . import addon, modifier, object, modal


def remove_point(ot, context, event, index=-1, fill=True):
    bc = context.window_manager.bc

    bm = bmesh.new()
    bm.from_mesh(bc.shape.data)

    bm.verts.ensure_lookup_table()
    if len(bm.verts) > 2 or index != -1:
        bm.verts.remove(bm.verts[index])

        if fill and len(bm.verts) > 2:
            bm.verts.ensure_lookup_table()
            bm.faces.new(bm.verts[:])

    bm.to_mesh(bc.shape.data)
    bm.free()


def add_point(ot, context, event):
    bc = context.window_manager.bc

    bm = bmesh.new()
    bm.from_mesh(bc.shape.data)

    if len(bm.verts) > 2:
        if len(bm.faces):
            bm.faces.ensure_lookup_table()
            bm.faces.remove(bm.faces[0])

    if len(bm.edges) == len(bm.verts):
        bm.edges.ensure_lookup_table()
        bm.edges.remove(bm.edges[-1])

    bm.verts.ensure_lookup_table()
    bm.verts.new((0.0, 0.0, 0.0))

    bm.verts.ensure_lookup_table()
    bm.edges.new(bm.verts[-2:])

    if len(bm.verts) > 2:
        bm.edges.ensure_lookup_table()
        bm.edges.new([bm.verts[0], bm.verts[-1]])

        bm.faces.ensure_lookup_table()
        bm.faces.new(bm.verts[:])

    bm.to_mesh(bc.shape.data)
    bm.free()


# edge length based on increment snap
# snap to draw dots
# last point snapping
def draw(ot, context, event):
    bc = context.window_manager.bc
    preference = addon.preference()

    point = bc.shape.data.vertices[-1]

    if not ot.add_point and not ot.add_point_lock:
        point.co = (ot.view3d['location'].x, ot.view3d['location'].y, point.co.z)

        snap = event.ctrl

        if snap:
            point1 = Vector(point.co[:-1])
            point2 = Vector(bc.shape.data.vertices[-2].co[:-1])
            point3 = None
            edge_angle = 0.0

            if len(bc.shape.data.vertices) > 2:
                point3 = Vector(bc.shape.data.vertices[-3].co[:-1])
                edge_angle = (point2 - point3).angle_signed(Vector((1, 0)), 0.0)

            delta = point1 - point2
            angle = delta.angle_signed(Vector((1, 0)), 0.0)

            step = pi*2/(360/preference.behavior.ngon_snap_angle)

            angle = round((angle - edge_angle)/step)*step + edge_angle
            direction = Vector((cos(angle), sin(angle)))

            point1 = point2 + delta.project(direction)

            point.co = Vector((point1.x, point1.y, point.co.z))

    del point


def offset(ot, context, event):
    preference = addon.preference()
    bc = context.window_manager.bc
    snap = preference.behavior.snap and preference.behavior.snap_increment
    snap_lock = snap and preference.behavior.increment_lock

    if not ot.extruded:
        extrude(ot, context, event)

    location_z = ot.view3d['location'].z

    if snap and event.ctrl or snap_lock:
        increment_amount = round(preference.behavior.increment_amount, 8)
        split = str(increment_amount).split('.')[1]
        increment_length = len(split) if int(split) != 0 else 0

        if event.shift:
            location_z = round(round(location_z * 10 / increment_amount) * increment_amount, increment_length)
            location_z *= 0.1

        else:
            location_z = round(round(location_z / increment_amount) * increment_amount, increment_length)

    if ot.view3d['location'].z > ot.start['extrude']:
        matrix = ot.start['matrix'] @ Matrix.Translation(Vector((0, 0, ot.view3d['location'].z)))
        bc.shape.matrix_world.translation = matrix.translation

        points = [bc.shape.data.vertices[point] for point in ot.geo['indices']['extrusion']]

        for point in points:
            point.co.z = -location_z + ot.start['extrude']

    else:
        matrix = ot.start['matrix'] @ Matrix.Translation(Vector((0, 0, ot.start['extrude'])))
        bc.shape.matrix_world.translation = matrix.translation

        points = [bc.shape.data.vertices[point] for point in ot.geo['indices']['extrusion']]

        for point in points:
            point.co.z = 0.0


def extrude(ot, context, event, extrude_only=True):
    preference = addon.preference()
    bc = context.window_manager.bc
    snap = preference.behavior.snap and preference.behavior.snap_increment
    snap_lock = snap and preference.behavior.increment_lock
    shape = bc.shape

    if not ot.extruded:
        bm = bmesh.new()
        bm.from_mesh(shape.data)

        ret = bmesh.ops.extrude_face_region(bm, geom=bm.edges[:] + bm.faces[:])
        extruded_verts = [ele for ele in ret['geom'] if isinstance(ele, bmesh.types.BMVert)]
        ot.geo['indices']['extrusion'] = [vert.index for vert in extruded_verts]
        del ret

        for point in extruded_verts:
            point.co.z = 0.0

        mid_edges = [e for e in bm.edges if (e.verts[0] in extruded_verts and e.verts[1] not in extruded_verts) or (e.verts[1] in extruded_verts and e.verts[0] not in extruded_verts)]
        bot_edges = [e for e in bm.edges if (e.verts[0] in extruded_verts and e.verts[1] in extruded_verts)]

        ot.geo['indices']['mid_edge'] = [edge.index for edge in mid_edges]
        ot.geo['indices']['bot_edge'] = [edge.index for edge in bot_edges]

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        for f in bm.faces:
            f.smooth = True

        bm.to_mesh(shape.data)
        bm.free()

        shape.data.update()

        ot.extruded = True

    if not extrude_only:
        location_z = ot.view3d['location'].z

        if snap and event.ctrl or snap_lock:
            increment_amount = round(preference.behavior.increment_amount, 8)
            split = str(increment_amount).split('.')[1]
            increment_length = len(split) if int(split) != 0 else 0

            if event.shift:
                location_z = round(round(location_z * 10 / increment_amount) * increment_amount, increment_length)
                location_z *= 0.1

            else:
                location_z = round(round(location_z / increment_amount) * increment_amount, increment_length)

        points = [shape.data.vertices[point] for point in ot.geo['indices']['extrusion']]

        for point in points:
            point.co.z = location_z if ot.view3d['location'].z < 0 else -0.0001


def vertex_group(ot, context, event, q_only=False):
    bc = context.window_manager.bc
    shape = bc.shape

    if not (ot.shape_type == 'NGON' and not ot.extruded):
        if ot.shape_type == 'CIRCLE':
            if 'bottom' not in shape.vertex_groups:
                group = shape.vertex_groups.new(name='bottom')
                group.add(index=[1], weight=1.0, type='ADD')

        if not q_only:
            mid_group = None
            for grp in shape.vertex_groups:
                if grp.name[:4] == 'edge':
                    mid_group = grp
                    break

            if not mid_group:
                for index, mid_edge in enumerate(ot.geo['indices']['mid_edge']):
                    group = shape.vertex_groups.new(name=F'edge{index + 1}')
                    group.add(index=shape.data.edges[mid_edge].vertices[:], weight=1.0, type='ADD')

        bot_group = None
        for grp in shape.vertex_groups:
            if grp.name == 'bottom':
                bot_group = grp
                break

        if not bot_group and shape.data.bc.q_beveled:
            verts = []
            for index in ot.geo['indices']['bot_edge']:
                for vert_index in shape.data.edges[index].vertices:
                    if vert_index not in verts:
                        verts.append(vert_index)

            group = shape.vertex_groups.new(name='bottom')
            group.add(index=verts, weight=1.0, type='ADD')

        elif ot.shape_type != 'CIRCLE' and bot_group and not shape.data.bc.q_beveled:
            shape.vertex_groups.remove(shape.vertex_groups['bottom'])


def bevel_weight(ot, context, event):
    bc = context.window_manager.bc
    preference = addon.preference()
    shape = bc.shape

    if not (ot.shape_type == 'NGON' and not ot.extruded):
        if ot.shape_type == 'CIRCLE':
            vertex_group(ot, context, event, q_only=True)

        else:
            shape.data.use_customdata_edge_bevel = True

            for index in ot.geo['indices']['mid_edge']:
                edge = shape.data.edges[index]
                edge.bevel_weight = 1

            if preference.shape.quad_bevel:
                vertex_group(ot, context, event, q_only=True)

            elif shape.data.bc.q_beveled:
                for index in ot.geo['indices']['bot_edge']:
                    edge = shape.data.edges[index]
                    edge.bevel_weight = 1

            elif not shape.data.bc.q_beveled:
                for index in ot.geo['indices']['bot_edge']:
                    edge = shape.data.edges[index]
                    edge.bevel_weight = 0

            shape.data.validate()


def knife(ot, context, event):
    bc = context.window_manager.bc

    targets = ot.datablock['targets']
    overrides = ot.datablock['overrides']

    original_active = context.active_object
    original_selected = context.selected_objects[:]

    bpy.ops.object.mode_set(mode='OBJECT')

    for obj in original_selected:
        obj.select_set(False)

    if not overrides:
        ot.datablock['overrides'] = [obj.data for obj in targets]

    for pair in zip(targets, overrides):
        obj = pair[0]
        override = pair[1]

        bm = bmesh.new()
        applied_shape = bc.shape.to_mesh(context.depsgraph, apply_modifiers=True)
        bm.from_mesh(applied_shape)

        bpy.data.meshes.remove(applied_shape)

        shape_matrix = bc.shape.matrix_world.copy()
        obj_matrix = obj.matrix_world.copy()

        shape_matrix.translation -= obj_matrix.translation
        obj_matrix.translation = Vector((0, 0, 0))

        bm.verts.ensure_lookup_table()
        shape_vert_indices = list()
        for v in bm.verts:
            v.tag = True
            v.select_set(True)
            v.co = bc.shape.matrix_world @ v.co
            shape_vert_indices.append(v.index)


        bm.edges.ensure_lookup_table()
        ret = bmesh.ops.bisect_edges(bm, edges=bm.edges[:], cuts=1)

        for ele in ret['geom_split']:
            if isinstance(ele, bmesh.types.BMVert):
                ele.select_set(True)
                shape_vert_indices.append(ele.index)

        bm.select_flush(True)

        bm.from_mesh(override)

        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            if not v.tag:
                v.select_set(False)
                v.co = obj.matrix_world @ v.co

        bm.select_flush(False)

        dat = bpy.data.meshes.new(name='bc-temporary-knife')
        new = bpy.data.objects.new(name='bc-temporary-knife', object_data=dat)
        new.data.use_auto_smooth = True

        bm.to_mesh(new.data)
        bm.free()

        bc.collection.objects.link(new)

        bpy.context.view_layer.objects.active = new
        new.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT')
        original_selection_mode = tuple(bpy.context.tool_settings.mesh_select_mode)
        bpy.context.scene.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.intersect() # TODO: use bmesh edgenet
        bpy.ops.mesh.loop_to_region(select_bigger=ot.flip) # can use bmesh for this
        bpy.context.scene.tool_settings.mesh_select_mode = original_selection_mode
        bpy.ops.object.mode_set(mode='OBJECT')

        bm = bmesh.new()
        bm.from_mesh(new.data)

        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[index] for index in shape_vert_indices], context='VERTS')
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0001)

        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            if not v.tag:
                v.co = obj.matrix_world.inverted() @ v.co

        bm.to_mesh(new.data)
        bm.free()

        original_name = obj.data.name
        original_data = obj.data
        obj.data.name = 'tmp'
        obj.data = new.data
        obj.data.name = original_name

        if original_data not in overrides:
            bpy.data.meshes.remove(original_data)

        bpy.data.objects.remove(new)

    del targets
    del overrides

    bpy.context.view_layer.objects.active = original_active
    original_active.select_set(True)

    del original_active

    for obj in original_selected:
        obj.select_set(True)

    del original_selected

    if ot.original_mode == 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')


def inset(ot, context, event):
    pass


class create:


    def shape(ot, context, event):
        preference = addon.preference()
        bc = context.window_manager.bc

        verts = [
            Vector((-0.5, -0.5, 0.0)), Vector(( 0.5, -0.5, 0.0)),
            Vector((-0.5,  0.5, 0.0)), Vector(( 0.5,  0.5, 0.0))]

        edges = [
            (0, 2), (0, 1),
            (1, 3), (2, 3)]

        faces = [(0, 1, 3, 2)]

        dat = bpy.data.meshes.new(name='Plane')
        dat.bc.removeable = True

        dat.from_pydata(verts, edges, faces)
        dat.validate()

        ot.datablock['plane'] = bpy.data.objects.new(name='Plane', object_data=dat)
        bc.plane = ot.datablock['plane']

        del dat

        if ot.shape_type == 'BOX':
            verts = [
                Vector((-0.5, -0.5, -0.5)), Vector((-0.5, -0.5,  0.5)),
                Vector((-0.5,  0.5, -0.5)), Vector((-0.5,  0.5,  0.5)),
                Vector(( 0.5, -0.5, -0.5)), Vector(( 0.5, -0.5,  0.5)),
                Vector(( 0.5,  0.5, -0.5)), Vector(( 0.5,  0.5,  0.5))]

            edges = [
                (0, 2), (0, 1), (1, 3), (2, 3),
                (2, 6), (3, 7), (6, 7), (4, 6),
                (5, 7), (4, 5), (0, 4), (1, 5)]

            faces = [
                (0, 1, 3, 2), (2, 3, 7, 6),
                (6, 7, 5, 4), (4, 5, 1, 0),
                (2, 6, 4, 0), (7, 3, 1, 5)]

            ot.geo['indices']['top_edge'] = [0, 4, 7, 10]
            ot.geo['indices']['mid_edge'] = [1, 3, 6, 9]
            ot.geo['indices']['bot_edge'] = [2, 5, 8, 11]

        elif ot.shape_type == 'CIRCLE':
            verts = [
                Vector((0.0, -0.5, -0.5)), Vector((0.0, -0.5,  0.5)),
                Vector((0.0,  0.0, -0.5)), Vector((0.0,  0.0,  0.5))]

            edges = [(0, 2), (0, 1), (1, 3)]

            faces = []

        elif ot.shape_type == 'NGON':
            verts = [Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.0))]

            edges = [(0, 1)]

            faces = []

        dat = bpy.data.meshes.new(name='Cutter')

        dat.from_pydata(verts, edges, faces)
        dat.validate()

        bc.shape = bpy.data.objects.new(name='Cutter', object_data=dat)

        del dat

        bc.shape.bc.shape = True

        bc.collection.objects.link(bc.shape)

        if ot.mode != 'MAKE':
            bc.shape.display_type = 'WIRE'
            bc.shape.cycles_visibility.camera = False
            bc.shape.cycles_visibility.diffuse = False
            bc.shape.cycles_visibility.glossy = False
            bc.shape.cycles_visibility.transmission = False
            bc.shape.cycles_visibility.scatter = False
            bc.shape.cycles_visibility.shadow = False

        if addon.preference().behavior.auto_smooth:
            bc.shape.data.use_auto_smooth = True

            for face in bc.shape.data.polygons:
                face.use_smooth = True

        if ot.shape_type == 'CIRCLE':
            mod = bc.shape.modifiers.new(name='Screw', type='SCREW')
            mod.steps = preference.shape.circle_vertices
            mod.use_normal_calculate = True
            mod.use_normal_flip = True
            mod.use_smooth_shade = True
            mod.use_merge_vertices = True

        if bc.original_active and preference.behavior.parent_shape:
            bc.shape.parent = bc.original_active

        bc.shape.data.uv_layers.new(name="UVMap", do_init=True)
