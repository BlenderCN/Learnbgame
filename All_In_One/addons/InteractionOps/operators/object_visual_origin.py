import bpy
import blf
import gpu
import bmesh
import numpy
import math
import copy
from math import radians, degrees
from mathutils import Vector, Matrix, Euler
from math import sin, cos, pi
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d


# get circle vertices on pos 2D by segments
def generate_circle_verts(position, radius, segments):
    coords = []
    coords.append(position)
    mul = (1.0 / segments) * (pi * 2)
    for i in range(segments):
        coord = (sin(i * mul) * radius + position[0], cos(i * mul) * radius + position[1])
        coords.append(coord)
    return coords


# get circle triangles by segments
def generate_circle_tris(segments, startID):
    triangles = []
    tri = startID
    for i in range(segments - 1):
        tricomp = (startID, tri + 1, tri + 2)
        triangles.append(tricomp)
        tri += 1
    tricomp = (startID, tri, startID + 1)
    triangles.append(tricomp)
    return triangles


# draw a circle on scene
def draw_bbox_active_point(self, context):
    point = self.target
    if point != (0, 0):
        position = point
        color = bpy.context.preferences.addons['InteractionOps'].preferences.vo_cage_ap_color
        radius = bpy.context.preferences.addons['InteractionOps'].preferences.vo_cage_ap_size
        segments = 12
        # create vertices
        coords = generate_circle_verts(position, radius, segments)
        # create triangles
        triangles = generate_circle_tris(segments, 0)
        # set shader and draw
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=triangles)
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)


# draw multiple circle in one batch on screen
def draw_bbox_cage_points(self, context):
    positions = (self.object_bbox(context))[0]
    if positions is not None:
        color = bpy.context.preferences.addons['InteractionOps'].preferences.vo_cage_points_color
        radius = bpy.context.preferences.addons['InteractionOps'].preferences.vo_cage_p_size
        segments = 12
        coords = []
        triangles = []
        # create vertices
        for center in positions:
            actCoords = generate_circle_verts(center, radius, segments)
            coords.extend(actCoords)
        # create triangles
        for tris in range(len(positions)):
            actTris = generate_circle_tris(segments, tris * (segments + 1))
            triangles.extend(actTris)
        # set shader and draw
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=triangles)
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)


def draw_bbox_lines(self, context):
    coords = (self.object_bbox(context))[1]
    if len(coords) != 0:
        if len(coords) == 8:
            indices = (
                (0, 1), (1, 2), (2, 3), (3, 0),
                (4, 5), (5, 6), (6, 7), (7, 4),
                (0, 4), (1, 5), (2, 6), (3, 7)
            )
        elif len(coords) > 8:
            indices = (
                # Bbox
                (0, 1), (1, 2), (2, 3), (0, 3),   # X-
                (4, 5), (5, 6), (6, 7), (4, 7),   # X+
                (0, 4),                           # Y- BTM
                (1, 5),                           # Y- UP
                (3, 7),                           # Y-BTM
                (2, 6),                           # Y+UP
                # SUBD
                (8, 10), (9, 11),                 # X-
                (12, 14), (13, 15),               # X+
                (16, 17), (8, 12),                # Y-
                (10, 14), (18, 19),               # Y+
                (11, 15), (16, 19),               # Z-
                (17, 18), (9, 13),                # Z+
                # Center
                (20, 23),                         # +X
                (20, 21),                         # -X
                (20, 27),                         # +Y
                (20, 25),                         # -Y
                (20, 31),                         # +Z
                (20, 29),                         # -Z
            )
        else:
            indices = ()
        color = bpy.context.preferences.addons['InteractionOps'].preferences.vo_cage_color
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)


def draw_iops_text(self, context, _uidpi, _uifactor):
    prefs = bpy.context.preferences.addons['InteractionOps'].preferences
    tColor = prefs.text_color
    tKColor = prefs.text_color_key
    tCSize = prefs.text_size
    tCPosX = prefs.text_pos_x
    tCPosY = prefs.text_pos_y
    tShadow = prefs.text_shadow_toggle
    tSColor = prefs.text_shadow_color
    tSBlur = prefs.text_shadow_blur
    tSPosX = prefs.text_shadow_pos_x
    tSPosY = prefs.text_shadow_pos_y

    iops_text = (
        ("World space group", "F1"),
        ("Local space for active", "F2"),
        ("World space for active", "F3"),
        ("Origin to World center", "W"),
        ("Selected to World center", "M"),
        ("Pick up active object", "Shift + LMB Click"),
    )

    # FontID
    font = 0
    blf.color(font, tColor[0], tColor[1], tColor[2], tColor[3])
    blf.size(font, tCSize, _uidpi)
    if tShadow:
        blf.enable(font, blf.SHADOW)
        blf.shadow(font, int(tSBlur), tSColor[0], tSColor[1], tSColor[2], tSColor[3])
        blf.shadow_offset(font, tSPosX, tSPosY)
    else:
        blf.disable(0, blf.SHADOW)

    textsize = tCSize
    # get leftbottom corner
    offset = tCPosY
    columnoffs = (textsize * 21) * _uifactor
    for line in reversed(iops_text):
        blf.color(font, tColor[0], tColor[1], tColor[2], tColor[3])
        blf.position(font, tCPosX * _uifactor, offset, 0)
        blf.draw(font, line[0])

        blf.color(font, tKColor[0], tKColor[1], tKColor[2], tKColor[3])
        textdim = blf.dimensions(0, line[1])
        coloffset = columnoffs - textdim[0] + tCPosX
        blf.position(0, coloffset, offset, 0)
        blf.draw(font, line[1])
        offset += (tCSize + 5) * _uifactor


class IOPS_OP_VisualOrigin(bpy.types.Operator):
    """Visual origin placing helper tool"""
    bl_idname = "iops.visual_origin"
    bl_label = "Visual origin"
    bl_options = {"REGISTER", "UNDO"}

    mouse_pos = (0, 0)

    # RayCastResults
    result = False
    result_obj = None
    vp_objs = []
    vp_group = None

    # BBoxResults
    pos_batch = []
    pos_batch_3d = []

    # DrawCalculations
    batch_idx = None
    target = (0, 0)

    # Handlers list
    vp_handlers = []

    @classmethod
    def poll(self, context):
        return (context.area.type == "VIEW_3D" and
                context.mode == "OBJECT" and
                context.view_layer.objects.active.type == "MESH" and
                len(context.view_layer.objects.selected) != 0)
    
    # Place origin for selected objects
    def place_origin(self, context):
        objs = context.view_layer.objects.selected
        pos = self.pos_batch_3d[self.batch_idx]
        context.scene.cursor.location = pos
        for ob in objs:
            context.view_layer.objects.active = ob
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    
    # Place origin for selected objects
    def move_selected_to_world(self, context):
        objs = context.view_layer.objects.selected        
        for ob in objs:
            ob.location = (0, 0, 0)    
    
    # Place origin to world center
    def origin_to_world(self, context):
        objs = context.view_layer.objects.selected
        context.scene.cursor.location = (0, 0, 0)
        context.scene.cursor.rotation_euler = (0, 0, 0) 
        for ob in objs:
            context.view_layer.objects.active = ob
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

    # Calculate distance between raycasts
    def calc_distance(self, context):
        mouse_pos = self.mouse_pos
        pos_batch = self.pos_batch
        if len(pos_batch) != 0:
            act_dist = numpy.linalg.norm(pos_batch[0] - Vector(mouse_pos))
            act_id = 0
            counter = 1
            itertargets = iter(self.pos_batch)
            next(itertargets)
            for pos in itertargets:
                dist = numpy.linalg.norm(pos - Vector(mouse_pos))
                if dist < act_dist:
                    act_id = counter
                    act_dist = dist
                counter += 1
            self.batch_idx = act_id
            self.target = pos_batch[act_id]

    def getActiveFromSelected(self, context):
        selected_objects = []
        active_object = None
        for ob in context.view_layer.objects.selected:
            if ob.type == 'MESH':
                selected_objects.append(ob)
        for ob in selected_objects:
            if ob == context.view_layer.objects.active:
                active_object = ob

        return active_object, selected_objects

    def orphan_data_purge(self, context):
        # Clean Up Start
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)
        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)
        for block in bpy.data.textures:
            if block.users == 0:
                bpy.data.textures.remove(block)
        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)
        # Clean Up End

    def getBBOX_from_selected(self, context):
        scene = bpy.context.scene
        sel_objs = []
        # Collect selected
        for ob in context.view_layer.objects.selected:
            if ob.type == 'MESH':
                sel_objs.append(ob)
        # Make duplicates
        dups = []
        for ob in sel_objs:
            matrix = ob.matrix_world
            dup_mesh = ob.data.copy()
            dup_obj = bpy.data.objects.new("iops_dups", dup_mesh)
            dup_obj.matrix_world = matrix
            context.scene.collection.objects.link(dup_obj)
            dups.append(dup_obj)
        # Deselect originals
        for ob in sel_objs:
            ob.select_set(False)
        # Select duplicates
        for ob in dups:
            ob.select_set(True)
        context.view_layer.objects.active = dups[-1]

        # Join duplicates and Apply transformation
        if len(dups) != 1:
            bpy.ops.object.join()
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        else:
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        # Get Bounding box from result
        dup = context.view_layer.objects.active
        dup_bounds = dup.bound_box
        bbox_verts = []
        for v in dup_bounds:
            v_co = Vector(v)
            bbox_verts.append(v_co)

        # Removing duplicates
        bpy.data.objects.remove(dup, do_unlink=True, do_id_user=True, do_ui_user=True)

        # Create a bounding box mesh from duplicated objects
        mesh = bpy.data.meshes.new('iops_bbox_mesh')
        mesh.from_pydata(bbox_verts, [], [])
        bbox = bpy.data.objects.new("iops_bbox", mesh)
        context.scene.collection.objects.link(bbox)

        # Restore selection
        for ob in sel_objs:
            ob.select_set(True)
        context.view_layer.objects.active = sel_objs[-1]

        # Assign vars
        if self.vp_group is None:
            self.result = True
            self.result_obj = bbox
            self.vp_group = bbox

    def active_to_world(self, context):
        # Collect selected
        sel_objs = []
        for ob in context.view_layer.objects.selected:
            if ob.type == 'MESH':
                sel_objs.append(ob)

        res = self.result
        obj = context.view_layer.objects.active
        # Duplicate active obj
        matrix = obj.matrix_world
        dup_mesh = obj.data.copy()
        dup_obj = bpy.data.objects.new("iops_dups", dup_mesh)
        dup_obj.matrix_world = matrix
        context.scene.collection.objects.link(dup_obj)
        # Deselect originals
        for ob in sel_objs:
            ob.select_set(False)
        # Select duplicates
        dup_obj.select_set(True)
        context.view_layer.objects.active = dup_obj
        # Apply transformation
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Get Bounding box from result
        dup_bounds = dup_obj.bound_box
        bbox_verts = []
        for v in dup_bounds:
            v_co = Vector(v)
            bbox_verts.append(v_co)
        # Removing duplicates
        bpy.data.objects.remove(dup_obj, do_unlink=True, do_id_user=True, do_ui_user=True)

        # Create a bounding box mesh from duplicated objects
        mesh = bpy.data.meshes.new('iops_bbox_mesh')
        mesh.from_pydata(bbox_verts, [], [])
        bbox = bpy.data.objects.new("iops_bbox", mesh)
        context.scene.collection.objects.link(bbox)
        # Restore selection
        for ob in sel_objs:
            ob.select_set(True)
        # Restore active obj
        context.view_layer.objects.active = obj
        # Assign vars
        if self.vp_group is None:
            self.result = True
            self.result_obj = bbox
            self.vp_group = bbox

    def scene_ray_cast(self, context):
        # get the context arguments
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = self.mouse_pos
        view_layer = context.view_layer

        # get the ray from the viewport and mouse
        view_vector = region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)

        ray_target = ray_origin + view_vector

        result, location, normal, index, obj, matrix = scene.ray_cast(view_layer, ray_origin, view_vector, distance=1.70141e+38)

        if result and obj in self.vp_objs:
            context.view_layer.objects.active = obj
            self.result_obj = obj
        return result, obj

    def object_bbox(self, context):
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = self.mouse_pos
        view_layer = context.view_layer

        res = self.result
        obj = self.result_obj

        verts_pos = []
        bbox_batch = []
        bbox_batch_3d = []
        face_batch = []
        face_batch_3d = []
        if obj is not None:
            matrix = obj.matrix_world
            matrix_trans = matrix.transposed()
            bbox = obj.bound_box
            bbox_verts_3d = []
            if len(bbox) != 0:
                subd_vert_pos = []
                bbox_edges = (
                    (0, 1), (1, 2), (2, 3), (0, 3),
                    (4, 5), (5, 6), (6, 7), (4, 7),
                    (0, 4), (1, 5), (2, 6), (3, 7), (0, 6))
                bbox_subd_edges = (
                    (8, 10), (9, 11), (12, 14), (13, 15),
                    (16, 17), (8, 12), (10, 14), (18, 19),
                    (11, 15), (16, 19), (17, 18), (9, 13))

                # BBox
                for v in bbox:
                    pos = Vector(v) @  matrix_trans
                    bbox_verts_3d.append(pos)

                # BBox Edge subD
                for e in bbox_edges:
                    v1 = Vector(bbox[e[0]])
                    v2 = Vector(bbox[e[1]])
                    vertmid = (v1 + v2) / 2
                    pos = Vector(vertmid) @  matrix_trans
                    bbox_verts_3d.append(pos)

                for e in bbox_subd_edges:
                    v1 = Vector(bbox_verts_3d[e[0]])
                    v2 = Vector(bbox_verts_3d[e[1]])
                    vertmid = (v1 + v2) / 2
                    pos = Vector(vertmid)
                    bbox_verts_3d.append(pos)

                # BBOX COLLECT
                for v in bbox_verts_3d:
                    pos3D = v
                    pos2D = location_3d_to_region_2d(region, rv3d, pos3D, default=None)
                    bbox_batch_3d.append(pos3D)
                    bbox_batch.append(pos2D)

            self.pos_batch = bbox_batch
            self.pos_batch_3d = bbox_batch_3d
            return [bbox_batch, bbox_batch_3d]
        else:
            return [bbox_batch, bbox_batch]

    def clear_draw_handlers(self):
        for handler in self.vp_handlers:
            bpy.types.SpaceView3D.draw_handler_remove(handler, "WINDOW")

    def execute(self, context):
        self.place_origin(context)
        if self.vp_group is not None:
            bpy.data.objects.remove(self.vp_group, do_unlink=True, do_id_user=True, do_ui_user=True)
            self.vp_group = None
        self.clear_draw_handlers()
        self.orphan_data_purge(context)
        return {"FINISHED"}

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}
        # Pick up in Local space
        elif event.shift:
            if event.type == 'LEFTMOUSE' and event.value == "PRESS":
                self.mouse_pos = event.mouse_region_x, event.mouse_region_y
                self.scene_ray_cast(context)
                self.object_bbox(context)
                self.calc_distance(context)
                if self.vp_group is not None:
                    bpy.data.objects.remove(self.vp_group, do_unlink=True, do_id_user=True, do_ui_user=True)
                    self.vp_group = None
                    self.orphan_data_purge(context)
        # Pick up in world space
        elif event.type == 'F3' and event.value == "PRESS":
            if self.vp_group is not None:
                bpy.data.objects.remove(self.vp_group, do_unlink=True, do_id_user=True, do_ui_user=True)
                self.vp_group = None
                self.orphan_data_purge(context)
            if self.vp_group is None:
                self.active_to_world(context)
                self.object_bbox(context)
                self.calc_distance(context)

        elif event.type == "F1" and event.value == "PRESS":
            if self.vp_group is not None:
                bpy.data.objects.remove(self.vp_group, do_unlink=True, do_id_user=True, do_ui_user=True)
                self.vp_group = None
                self.orphan_data_purge(context)
            if self.vp_group is None:
                self.getBBOX_from_selected(context)
                self.object_bbox(context)
                self.calc_distance(context)
                self.orphan_data_purge(context)

        elif event.type == "F2" and event.value == "PRESS":
            self.result_obj, self.vp_objs = self.getActiveFromSelected(context)
            self.object_bbox(context)
            self.calc_distance(context)
            if self.vp_group is not None:
                bpy.data.objects.remove(self.vp_group, do_unlink=True, do_id_user=True, do_ui_user=True)
                self.vp_group = None
                self.orphan_data_purge(context)
     
        elif event.type == 'W' and event.value == "PRESS":
            self.origin_to_world(context)
            if self.vp_group is not None:
                bpy.data.objects.remove(self.vp_group, do_unlink=True, do_id_user=True, do_ui_user=True)
            self.vp_group = None
            self.clear_draw_handlers()
            self.orphan_data_purge(context)            
            return {"FINISHED"}

        elif event.type == 'M' and event.value == "PRESS":
            self.move_selected_to_world(context)
            if self.vp_group is not None:
                bpy.data.objects.remove(self.vp_group, do_unlink=True, do_id_user=True, do_ui_user=True)
            self.vp_group = None
            self.clear_draw_handlers()
            self.orphan_data_purge(context)             
            return {"FINISHED"}

        elif event.type == 'MOUSEMOVE':
            self.mouse_pos = event.mouse_region_x, event.mouse_region_y
            self.calc_distance(context)            

        elif event.type in {"LEFTMOUSE", "SPACE"}:
            self.execute(context)
            return {"FINISHED"}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.mouse_pos = [0, 0]
            self.result = False
            self.result_obj = None
            if self.vp_group:
                    bpy.data.objects.remove(self.vp_group, do_unlink=True, do_id_user=True, do_ui_user=True)
            self.clear_draw_handlers()
            self.orphan_data_purge(context)
            print("EXIT", self.vp_group)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        preferences = context.preferences
        if context.space_data.type == 'VIEW_3D':
            args = (self, context)
            self.mouse_pos = event.mouse_region_x, event.mouse_region_y
            self.result_obj, self.vp_objs = self.getActiveFromSelected(context)
            self.object_bbox(context)
            self.calc_distance(context)
            uidpi = int((72 * preferences.system.ui_scale))
            args_text = (self, context, uidpi, preferences.system.ui_scale)
            # Add draw handlers
            self._handle_iops_text = bpy.types.SpaceView3D.draw_handler_add(draw_iops_text, args_text, 'WINDOW', 'POST_PIXEL')
            self._handle_bbox_lines = bpy.types.SpaceView3D.draw_handler_add(draw_bbox_lines, args, 'WINDOW', 'POST_VIEW')
            self._handle_bbox_points = bpy.types.SpaceView3D.draw_handler_add(draw_bbox_cage_points, args, 'WINDOW', 'POST_PIXEL')
            self._handle_bbox_act_point = bpy.types.SpaceView3D.draw_handler_add(draw_bbox_active_point, args, 'WINDOW', 'POST_PIXEL')
            self.vp_handlers = [self._handle_iops_text, self._handle_bbox_lines, self._handle_bbox_points, self._handle_bbox_act_point]
            # Add modal handler to enter modal mode
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}
