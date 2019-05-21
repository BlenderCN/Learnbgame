import bpy
import bmesh
import mathutils
import math
from mathutils import Vector, Matrix
from mathutils.geometry import box_fit_2d
from mathutils.geometry import normal as calculate_normal
from functools import reduce
from perfect_shape.shaper import get_loops, is_clockwise, get_parallel_edges, get_inner_faces, get_boundary_edges
from perfect_shape.utils import (generate_icons, generate_patterns_icons, refresh_icons, get_cache, set_cache,
                                 clear_cache, CacheException, preview_collections)
from perfect_shape.user_interface import PerfectShapeUI


class PerfectPatternAdd(bpy.types.Operator):
    bl_idname = "mesh.perfect_pattern_add"
    bl_label = "Mark Perfect Pattern"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.area.type == "VIEW_3D" and context.object is not None

    def execute(self, context):
        object = context.object
        object.update_from_editmode()

        object_bm = bmesh.from_edit_mesh(object.data)
        selected_edges = [e for e in object_bm.edges if e.select]
        loops = get_loops(selected_edges[:])

        if not loops:
            self.report({'WARNING'}, "Please select boundary loop of selected area.")
            return {'CANCELLED'}

        if len(loops) > 1:
            self.report({'WARNING'}, "Please select one loop.")
            return {'CANCELLED'}

        loop_verts = loops[0][0][0]

        if len(loop_verts) < 2:
            self.report({'WARNING'}, "Please select more edges.")
            return {'CANCELLED'}

        pattern_item = context.scene.perfect_shape.patterns.add()

        shape_bm = bmesh.new()
        for loop_vert in loop_verts:
            pattern_vert = pattern_item.verts.add()
            pattern_vert.co = loop_vert.co.copy()
            shape_bm.verts.new(loop_vert.co.copy())
        shape_bm.verts.ensure_lookup_table()
        verts = shape_bm.verts[:]
        for i in range(len(verts) - 1):
            shape_bm.edges.new((verts[i], verts[i + 1 % len(verts)]))
        bmesh.ops.contextual_create(shape_bm, geom=shape_bm.edges)
        shape_bm.faces.ensure_lookup_table()

        center = shape_bm.faces[0].calc_center_median()

        bmesh.ops.triangulate(shape_bm, faces=shape_bm.faces[:])

        forward = calculate_normal([v.co for v in loop_verts])
        normal_forward = reduce(
            lambda v1, v2: v1.normal.copy() + v2.normal.copy() if isinstance(v1, bmesh.types.BMVert)
            else v1.copy() + v2.normal.copy(), loop_verts).normalized()
        if normal_forward.angle(forward) - math.pi / 2 > 1e-6:
            forward.negate()

        matrix_rotation = forward.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        matrix_rotation.transpose()
        matrix = matrix_rotation * Matrix.Translation(-center)

        for pattern_vert in pattern_item.verts:
            pattern_vert.co = matrix * Vector(pattern_vert.co)

        pattern_faces = pattern_item.faces
        for face in shape_bm.faces:
            item = pattern_faces.add()
            item.indices = [v.index for v in face.verts]

        generate_patterns_icons()
        idx = context.scene.perfect_shape.patterns.values().index(pattern_item)
        context.scene.perfect_shape.active_pattern = str(idx)
        clear_cache()
        return {'FINISHED'}


class PerfectPatternRemove(bpy.types.Operator):
    bl_idname = "mesh.perfect_pattern_remove"
    bl_label = "Delete Pattern"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.area.type == "VIEW_3D" and context.object is not None

    def execute(self, context):
        pcoll = preview_collections["patterns"]
        idx = context.scene.perfect_shape.active_pattern
        context.scene.perfect_shape.patterns.remove(int(idx))
        for i in range(int(idx) + 1, len(pcoll)):
            pcoll[str(i - 1)].image_pixels_float = pcoll[str(i)].image_pixels_float[:]
        del pcoll[str(len(pcoll) - 1)]
        if len(pcoll) > 0:
            context.scene.perfect_shape.active_pattern = str(len(pcoll) - 1)
        else:
            ops = context.window_manager.operators
            if len(ops) > 0:
                if ops[-1].bl_idname == 'MESH_OT_perfect_shape':
                    ops[-1].shape = "CIRCLE"
        clear_cache()
        return {'FINISHED'}


class PerfectShape(bpy.types.Operator, PerfectShapeUI):
    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.area.type == "VIEW_3D" and context.object is not None

    def check(self, context):
        return True

    def execute(self, context):
        object = context.object
        object.update_from_editmode()

        self.pivot_point = context.space_data.pivot_point
        self.transform_orientation = context.space_data.transform_orientation

        object_bm = bmesh.from_edit_mesh(object.data)
        object_bm.verts.ensure_lookup_table()
        object_bm.edges.ensure_lookup_table()
        object_bm.faces.ensure_lookup_table()

        selected_faces = [f for f in object_bm.faces if f.select]
        selected_edges = [e for e in object_bm.edges if e.select]
        selected_verts = [v for v in object_bm.verts if v.select]

        if len(selected_edges) == 0:
            self.report({'WARNING'}, "Please select edges.")
            return {'CANCELLED'}

        try:
            cache_loops = get_cache(self.as_pointer(), "loops")
            loops = []
            for (loop_verts, loop_edges, loop_faces), is_loop_cyclic, is_loop_boundary in cache_loops:
                loops.append((([object_bm.verts[v] for v in loop_verts], [object_bm.edges[e] for e in loop_edges],
                               [object_bm.faces[f] for f in loop_faces]), is_loop_cyclic, is_loop_boundary))
        except CacheException:
            loops = get_loops(selected_edges, selected_faces)
            if loops:
                cache_loops = []
                for (loop_verts, loop_edges, loop_faces), is_loop_cyclic, is_loop_boundary in loops:
                    cache_loops.append((([v.index for v in loop_verts], [e.index for e in loop_edges],
                                         [f.index for f in loop_faces]), is_loop_cyclic, is_loop_boundary))
                set_cache(self.as_pointer(), "loops", cache_loops)

        if loops is None:
            self.report({'WARNING'}, "Please select boundary loop(s) of selected area(s).")
            return {'CANCELLED'}

        selection_center = Vector()
        for vert in selected_verts:
            selection_center += vert.co
        selection_center /= len(selected_verts)

        object_bvh = mathutils.bvhtree.BVHTree.FromObject(object, context.scene, deform=False)

        refresh_icons()
        shape_bm = bmesh.new()
        for loop_idx, ((loop_verts, loop_edges, loop_faces), is_loop_cyclic, is_loop_boundary) in enumerate(loops):
            if len(loop_edges) < 3:
                continue
            loop_verts_len = len(loop_verts)

            shape_verts = None
            shape_edges = None
            try:
                cache_verts = get_cache(self.as_pointer(), "shape_verts_{}".format(loop_idx))
                tmp_vert = None
                for i, cache_vert in enumerate(cache_verts):
                    new_vert = shape_bm.verts.new(cache_vert)
                    if i > 0:
                        shape_bm.edges.new((tmp_vert, new_vert))
                    tmp_vert = new_vert
                shape_verts = shape_bm.verts[:]
                shape_bm.edges.new((shape_verts[-1], shape_verts[0]))
                shape_edges = shape_bm.edges[:]

            except CacheException:
                if self.shape == "CIRCLE":
                    a = sum([e.calc_length() for e in loop_edges]) / loop_verts_len
                    diameter = a / (2 * math.sin(math.pi / loop_verts_len))
                    shape_segments = loop_verts_len + self.span
                    shape_verts = bmesh.ops.create_circle(shape_bm, segments=shape_segments, diameter=diameter)
                    shape_verts = shape_verts["verts"]
                    shape_edges = shape_bm.edges[:]

                elif self.shape == "RECTANGLE":
                    if loop_verts_len % 2 > 0:
                        self.report({'WARNING'}, "An odd number of edges.")
                        del shape_bm
                        return {'FINISHED'}
                    size = sum([e.calc_length() for e in loop_edges])

                    size_a = (size / 2) / (self.ratio_a + self.ratio_b) * self.ratio_a
                    size_b = (size / 2) / (self.ratio_a + self.ratio_b) * self.ratio_b
                    seg_a = (loop_verts_len / 2) / (self.ratio_a + self.ratio_b) * self.ratio_a
                    seg_b = int((loop_verts_len / 2) / (self.ratio_a + self.ratio_b) * self.ratio_b)
                    if seg_a % 1 > 0:
                        self.report({'WARNING'}, "Incorrect sides ratio.")
                        seg_a += 1
                        seg_b += 2
                    seg_a = int(seg_a)
                    if self.is_square:
                        size_a = (size_a + size_b) / 2
                        size_b = size_a
                    seg_len_a = size_a / seg_a
                    seg_len_b = size_b / seg_b

                    for i in range(seg_a):
                        shape_bm.verts.new(Vector((size_b / 2 * -1, seg_len_a * i - (size_a / 2), 0)))
                    for i in range(seg_b):
                        shape_bm.verts.new(Vector((seg_len_b * i - (size_b / 2), size_a / 2, 0)))
                    for i in range(seg_a, 0, -1):
                        shape_bm.verts.new(Vector((size_b / 2, seg_len_a * i - (size_a / 2), 0)))
                    for i in range(seg_b, 0, -1):
                        shape_bm.verts.new(Vector((seg_len_b * i - (size_b / 2), size_a / 2 * -1, 0)))

                    shape_verts = shape_bm.verts[:]
                    for i in range(len(shape_verts)):
                        shape_bm.edges.new((shape_verts[i], shape_verts[(i + 1) % len(shape_verts)]))
                    shape_edges = shape_bm.edges[:]

                elif self.shape == "PATTERN":
                    pattern_idx = context.scene.perfect_shape.active_pattern
                    pattern = context.scene.perfect_shape.patterns[int(pattern_idx)]
                    if len(pattern.verts) == 0:
                        self.report({'WARNING'}, "Empty Pattern Data.")
                        del shape_bm
                        return {'FINISHED'}
                    if len(pattern.verts) != len(loop_verts):
                        self.report({'WARNING'}, "Pattern and loop vertices count must be the same.")
                        del shape_bm
                        return {'FINISHED'}
                    for pattern_vert in pattern.verts:
                        shape_bm.verts.new(Vector(pattern_vert.co))
                    shape_verts = shape_bm.verts[:]
                    for i in range(len(shape_verts)):
                        shape_bm.edges.new((shape_verts[i], shape_verts[(i + 1) % len(shape_verts)]))
                    shape_edges = shape_bm.edges[:]

                elif self.shape == "OBJECT":
                    if self.target in bpy.data.objects:
                        shape_object = bpy.data.objects[self.target]
                        shape_bm.from_object(shape_object, context.scene)
                        loops = get_loops(shape_bm.edges[:])
                        if not loops or len(loops) > 1:
                            self.report({'WARNING'}, "Wrong mesh data.")
                            del shape_bm
                            return {'FINISHED'}
                        if len(loops[0][0][0]) > len(loop_verts):
                            self.report({'WARNING'}, "Shape and loop vertices count must be the same.")
                            del shape_bm
                            return {'FINISHED'}

                        shape_verts = loops[0][0][0]
                        shape_edges = loops[0][0][1]
                if shape_verts:
                    set_cache(self.as_pointer(), "shape_verts_{}".format(loop_idx), [v.co.copy() for v in shape_verts])

            if shape_verts:
                context.scene.perfect_shape.preview_verts_count = loop_verts_len + self.span

                try:
                    center = get_cache(self.as_pointer(), "P_{}_{}".format(self.pivot_point, loop_idx))

                except CacheException:
                    if self.pivot_point == "CURSOR":
                        center = object.matrix_world.copy() * context.scene.cursor_location.copy()
                    else:
                        temp_bm = bmesh.new()
                        for loop_vert in loop_verts:
                            temp_bm.verts.new(loop_vert.co.copy())
                        temp_verts = temp_bm.verts[:]
                        for i in range(len(temp_verts)):
                            temp_bm.edges.new((temp_verts[i], temp_verts[(i + 1) % len(temp_verts)]))
                        temp_bm.faces.new(temp_bm.verts)
                        temp_bm.faces.ensure_lookup_table()
                        if context.space_data.pivot_point == 'BOUNDING_BOX_CENTER':
                            center = temp_bm.faces[0].calc_center_bounds()
                        else:
                            center = temp_bm.faces[0].calc_center_median()
                        del temp_bm
                    set_cache(self.as_pointer(), "P_{}_{}".format(self.pivot_point, loop_idx), center)

                if self.projection == "NORMAL":
                    forward = calculate_normal([v.co.copy() for v in loop_verts])
                    normal_forward = reduce(
                        lambda v1, v2: v1.normal.copy() + v2.normal.copy() if isinstance(v1, bmesh.types.BMVert)
                        else v1.copy() + v2.normal.copy(), loop_verts).normalized()
                    if forward.angle(normal_forward) - math.pi / 2 >= 1e-6:
                        forward.negate()
                else:
                    forward = Vector([v == self.projection for v in ["X", "Y", "Z"]])

                if self.invert_projection:
                    forward.negate()


                rotation_m = 1
                if context.space_data.pivot_point != "INDIVIDUAL_ORIGINS":

                    if (center+selection_center).dot(forward) > 0:
                        rotation_m = -1
                    # if center.cross(forward).angle(selection_center) >= math.pi / 2:
                    #     forward.negate()

                    # if cross.dot(center) < 0:
                    #     forward.negate()
                    # if(center + selection_center).dot(forward) < 0:
                    #     forward.negate()
                    # matrix_rotation = forward.to_track_quat('Z', 'Y').to_matrix().to_4x4()
                    # if (matrix_rotation * center).dot(matrix_rotation * (center + selection_center)) > 0:
                    #     forward.negate()
                    #     if loop_faces:
                    #         rotation_m = - 1
                if not is_clockwise(forward, center, loop_verts):
                    loop_verts.reverse()
                    loop_edges.reverse()

                matrix_rotation = forward.to_track_quat('Z', 'Y').to_matrix().to_4x4()
                matrix_translation = Matrix.Translation(center)

                bmesh.ops.scale(shape_bm, vec=Vector((1, 1, 1)) * (1 + self.offset), verts=shape_verts)

                bmesh.ops.transform(shape_bm, verts=shape_verts, matrix=matrix_translation * matrix_rotation)

                loop_verts_co_2d = [(v.co * matrix_rotation).to_2d() for v in loop_verts]
                shape_verts_co_2d = [(v.co * matrix_rotation).to_2d() for v in shape_verts]

                loop_angle = box_fit_2d(loop_verts_co_2d)
                shape_angle = box_fit_2d(shape_verts_co_2d)

                correct_angle = 0
                if self.loop_rotation:
                    correct_angle = loop_angle

                if self.shape_rotation:
                    correct_angle += shape_angle

                if correct_angle != 0:
                    bmesh.ops.rotate(shape_bm, verts=shape_verts, cent=center,
                                     matrix=Matrix.Rotation(-correct_angle, 3, forward))

                kd_tree = mathutils.kdtree.KDTree(len(loop_verts))
                for idx, loop_vert in enumerate(loop_verts):
                    kd_tree.insert(loop_vert.co, idx)
                kd_tree.balance()
                shape_first_idx = kd_tree.find(shape_verts[0].co)[1]
                shift = shape_first_idx + self.shift
                if shift != 0:
                    loop_verts = loop_verts[shift % len(loop_verts):] + loop_verts[:shift % len(loop_verts)]

                if self.rotation != 0:
                    bmesh.ops.rotate(shape_bm, verts=shape_verts, cent=center,
                                     matrix=Matrix.Rotation(-self.rotation*rotation_m, 3, forward))

                bmesh.ops.translate(shape_bm, vec=self.shape_translation, verts=shape_bm.verts)
                center = Matrix.Translation(self.shape_translation) * center

                if not is_loop_boundary and self.use_ray_cast:
                    for shape_vert in shape_verts:
                        co = shape_vert.co
                        ray_cast_data = object_bvh.ray_cast(co, forward)
                        if ray_cast_data[0] is None:
                            ray_cast_data = object_bvh.ray_cast(co, -forward)
                        if ray_cast_data[0] is not None:
                            shape_vert.co = ray_cast_data[0]

                for idx, vert in enumerate(loop_verts):
                    vert.co = vert.co.lerp(shape_verts[idx].co, self.factor / 100)

                if not is_loop_boundary and is_loop_cyclic and loop_faces:
                    if self.fill_type != "ORIGINAL":
                        smooth = loop_faces[0].smooth
                        bmesh.ops.delete(object_bm, geom=loop_faces, context=5)

                        loop_faces = []
                        center_vert = object_bm.verts.new(center)
                        if self.use_ray_cast:
                            ray_cast_data = object_bvh.ray_cast(center_vert.co, forward)
                            if ray_cast_data[0] is None:
                                ray_cast_data = object_bvh.ray_cast(center_vert.co, -forward)
                            if ray_cast_data[0] is not None:
                                center_vert.co = ray_cast_data[0]
                        for idx, vert in enumerate(loop_verts):
                            new_face = object_bm.faces.new((center_vert, vert, loop_verts[(idx + 1) % loop_verts_len]))
                            new_face.smooth = smooth
                            loop_faces.append(new_face)
                        bmesh.ops.recalc_face_normals(object_bm, faces=loop_faces)


                    if self.outset > 0.0:
                        outset_region_faces = bmesh.ops.inset_region(object_bm, faces=loop_faces,
                                                                     thickness=self.outset, use_even_offset=True,
                                                                     use_interpolate=True, use_outset=True)

                    if self.extrude == 0:
                        verts = loop_verts[:]
                        for face in loop_faces:
                            for vert in face.verts:
                                if vert not in verts:
                                    verts.append(vert)
                        if self.fill_flatten:
                            matrix = Matrix.Translation(-center)
                            bmesh.ops.rotate(object_bm, cent=center, matrix=matrix_rotation.transposed(),
                                             verts=loop_verts)
                            bmesh.ops.scale(object_bm, vec=Vector((1, 1, +0)), space=matrix, verts=verts)
                            bmesh.ops.rotate(object_bm, cent=center, matrix=matrix_rotation, verts=verts)

                        if self.inset > 0.0:
                            bmesh.ops.inset_region(object_bm, faces=loop_faces,
                                                   thickness=self.inset,
                                                   use_even_offset=True,
                                                   use_interpolate=True)
                        if self.fill_type == "HOLE":
                            bmesh.ops.delete(object_bm, geom=loop_faces, context=5)
                        elif self.fill_type == "NGON":
                            bmesh.utils.face_join(loop_faces)

                    else:
                        verts = []
                        edges = []
                        faces = []
                        side_faces = []
                        side_edges = []
                        extrude_geom = bmesh.ops.extrude_face_region(object_bm, geom=loop_faces, use_keep_orig=True)
                        bmesh.ops.delete(object_bm, geom=loop_faces, context=5)
                        for geom in extrude_geom["geom"]:
                            if isinstance(geom, bmesh.types.BMVert):
                                verts.append(geom)
                            elif isinstance(geom, bmesh.types.BMFace):
                                faces.append(geom)
                            elif isinstance(geom, bmesh.types.BMEdge):
                                edges.append(geom)

                        for edge in loop_edges:
                            for face in edge.link_faces:
                                if any((e for e in face.edges if e in edges)):
                                    side_faces.append(face)
                                    for edge in face.edges:
                                        if edge not in side_edges and edge not in edges and edge not in loop_edges:
                                            side_edges.append(edge)

                        if self.fill_flatten:
                            matrix = Matrix.Translation(-center)
                            bmesh.ops.rotate(object_bm, cent=center, matrix=matrix_rotation.transposed(), verts=verts)
                            bmesh.ops.scale(object_bm, vec=Vector((1.0, 1.0, 0.001)), space=matrix, verts=verts)
                            bmesh.ops.rotate(object_bm, cent=center, matrix=matrix_rotation, verts=verts)

                        bmesh.ops.translate(object_bm,
                                            verts=verts,
                                            vec=forward * self.extrude)

                        cuts = max(self.cuts, self.cuts_rings)
                        if cuts > 0:
                            sub = bmesh.ops.subdivide_edges(object_bm, edges=side_edges, cuts=cuts)
                            loop_verts = []
                            first_verts = loop_edges[0].verts[:]
                            for edge in loop_edges:
                                if edge == loop_edges[0]:
                                    continue
                                if edge == loop_edges[1]:
                                    if first_verts[0] == edge.verts[0]:
                                        first_verts.reverse()
                                    loop_verts.extend(first_verts)
                                for vert in edge.verts:
                                    if vert not in loop_verts:
                                        loop_verts.append(vert)
                            split_edges = []
                            for geom in sub["geom_split"]:
                                if isinstance(geom, bmesh.types.BMEdge):
                                    split_edges.append(geom)

                            skip_edges = []
                            for vert in loop_verts:
                                for edge in vert.link_edges:
                                    if edge not in skip_edges and edge not in split_edges:
                                        skip_edges.append(edge)

                            start = self.cuts_shift % loop_verts_len
                            stop = self.cuts_shift % loop_verts_len
                            verts_list = loop_verts[start:] + loop_verts[:stop]
                            for i in range(self.cuts):
                                new_split_edges = []
                                for idx, vert in enumerate(verts_list):
                                    if idx < self.cuts_len+i or idx >= loop_verts_len-i:
                                        continue
                                    for edge in vert.link_edges:
                                        if edge in split_edges:
                                            other_vert = edge.other_vert(vert)
                                            bmesh.ops.weld_verts(object_bm, targetmap={other_vert: vert})
                                    for edge in vert.link_edges:
                                        if edge not in new_split_edges and edge not in skip_edges:
                                            new_split_edges.append(edge)

                                split_edges = new_split_edges

                            cut_edges = []
                            dissolve_edges = []
                            cut_skip = []
                            prev_edge = None
                            first_join = True
                            for i in range(self.cuts_rings):
                                if i >= self.cuts:
                                    break
                                split_edges = []
                                for idx, vert in enumerate(verts_list):
                                    if idx < self.cuts_len+i or idx >= loop_verts_len-i:
                                        for edge in vert.link_edges:
                                            if edge not in skip_edges and edge not in cut_skip:
                                                if prev_edge is not None and idx not in range(self.cuts_len):
                                                    if not any((v for v in edge.verts if v in prev_edge.verts)):
                                                        if edge not in dissolve_edges:
                                                            dissolve_edges.append(edge)

                                                if edge not in dissolve_edges and edge not in split_edges:
                                                    split_edges.append(edge)
                                                    cut_skip.append(edge)
                                                    #edge.select_set(True)
                                                prev_edge = edge

                                if first_join and len(cut_edges) == 1:
                                    cut_edges[0].extend(split_edges)
                                    first_join = False
                                else:
                                    cut_edges.append(split_edges)
                            # if dissolve_edges:
                            #     bmesh.ops.dissolve_edges(object_bm, edges=dissolve_edges)
                            # inner_verts = []
                            # for i, split_edges in enumerate(cut_edges):
                            #     for edge in split_edges:
                            #         sub = bmesh.ops.subdivide_edges(object_bm, edges=[edge], cuts=self.cuts-i)
                            #         sub_verts = [v for v in sub["geom_inner"] if isinstance(v, bmesh.types.BMVert)]
                            #         inner_verts.append(sub_verts)

                        if self.side_inset > 0.0:
                            inset_region = bmesh.ops.inset_region(object_bm, faces=side_faces,
                                                                  thickness=self.side_inset,
                                                                  use_even_offset=True, use_interpolate=True)

                        if self.inset > 0.0:
                            inset_region_faces = bmesh.ops.inset_region(object_bm, faces=faces, thickness=self.inset,
                                                                        use_even_offset=True, use_interpolate=True)
                        if self.fill_type == "HOLE":
                            bmesh.ops.delete(object_bm, geom=faces, context=5)
                        elif self.fill_type == "NGON":
                            bmesh.utils.face_join(faces)

            if not selected_faces and self.extrude != 0:
                self.report({'WARNING'}, "Please select faces to extrude.")

            shape_bm.clear()

        del object_bvh
        object_bm.normal_update()
        bmesh.update_edit_mesh(object.data)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        clear_cache()
        ret = self.execute(context)
        generate_icons()
        generate_patterns_icons()
        if ret == {'FINISHED'}:
            wm.invoke_props_popup(self, event)
        return ret


class PerfectPatternUpdate(bpy.types.Operator):
    bl_idname = "mesh.perfect_pattern_update"
    bl_label = "Update"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.area.type == "VIEW_3D" and context.object is not None

    def execute(self, context):
        ops = context.window_manager.operators
        if ops:
            if ops[-1].bl_idname == 'MESH_OT_perfect_shape':
                ops[-1].execute(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(PerfectShape)
    bpy.utils.register_class(PerfectPatternAdd)
    bpy.utils.register_class(PerfectPatternRemove)
    bpy.utils.register_class(PerfectPatternUpdate)


def unregister():
    bpy.utils.unregister_class(PerfectPatternAdd)
    bpy.utils.unregister_class(PerfectPatternRemove)
    bpy.utils.unregister_class(PerfectShape)
    bpy.utils.register_class(PerfectPatternUpdate)
