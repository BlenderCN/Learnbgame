import traceback
import sys

import bpy
import bmesh

from mathutils import Vector, Matrix
from bpy.types import Operator, Object
from bpy.props import *

from . import shader
from . change import last
from ... import icon, topbar
from ... utility import addon, data, lattice, mesh, modal, modifier, object, ray
from .... __init__ import bl_info

datablock = {
    'targets': list(),
    'overrides': list(),
    'dimensions': Vector((0, 0, 0)),
    'slices': list(),
    'operator': None,
    'duplicate': None,
    'plane': None,
    'box': None,
    'modifier': {
        'bevel': list()}}

ray_cast = {
    'location': Vector((0, 0, 0)),
    'normal': Vector((0, 0, 0))}

start = {
    'matrix': Matrix(),
    'mode': 'CUT',
    'operation': 'NONE',
    'location': Vector(),
    'extrude': float(),
    'offset': float()}

geo = {
    'points': list(),
    'verts': list(),
    'edges': list(),
    'faces': list(),
    'indices': {
        'extrusion': list(),
        'bot_edge': list(),
        'top_edge': list(),
        'mid_edge': list()}}

mouse = {
    'location': Vector(),
    'intersect': Vector()}

view3d = {
    'origin': Vector(),
    'location': Vector()}

verts = [
    Vector((-1.0,   -1.0,   -0.04)),  Vector((1.0,    -1.0,   -0.04)),
    Vector((-1.0,    1.0,   -0.04)),  Vector((1.0,     1.0,   -0.04)),
    Vector((-0.859,  0.859, -0.04)),  Vector((-0.859, -0.859, -0.04)),
    Vector((0.859,  -0.859, -0.04)),  Vector((0.859,   0.859, -0.04)),
    Vector((-0.657,  0.657, -0.04)),  Vector((-0.657, -0.657, -0.04)),
    Vector((0.657,  -0.657, -0.04)),  Vector((-0.307,  0.307, -0.04)),
    Vector((0.307,  -0.307, -0.04)),  Vector((0.307,   0.307, -0.04)),
    Vector((0.213,   0.213, -0.04)),  Vector((-0.213,  0.213, -0.04)),
    Vector((0.213,  -0.213, -0.04)),  Vector((-1.056, -1.056, -0.366)),
    Vector((-1.056, -1.056,  0.05)),  Vector((-1.056,  1.056, -0.366)),
    Vector((-1.056,  1.056,  0.05)),  Vector((1.056,  -1.056, -0.366)),
    Vector((1.056,  -1.056,  0.05)),  Vector((1.056,   1.056, -0.366)),
    Vector((1.056,   1.056,  0.05)),  Vector((1.0,    -1.0,   -0.366)),
    Vector((-1.0,   -1.0,   -0.366)), Vector((0.859,  -0.859, -0.366)),
    Vector((-0.859, -0.859, -0.366)), Vector((0.307,  -0.307, -0.366)),
    Vector((0.657,  -0.657, -0.366)), Vector((-0.657, -0.657, -0.366)),
    Vector((0.213,  -0.213, -0.366)), Vector((-0.213,  0.213, -0.366)),
    Vector((-0.307,  0.307, -0.366)), Vector((0.307,   0.307, -0.366)),
    Vector((0.213,   0.213, -0.366)), Vector((-0.657,  0.657, -0.366)),
    Vector((0.307,   0.129, -0.366)), Vector((0.859,   0.859, -0.366)),
    Vector((-0.859,  0.859, -0.366)), Vector((-1.0,    1.0,   -0.366)),
    Vector((1.0,     1.0,   -0.366))]

edges = [
    (4,  5),  (5,  6),  (6,  7),  (7,  4),
    (2,  0),  (0,  1),  (1,  3),  (3,  2),
    (19, 41), (4,  2),  (1,  6),  (14, 15),
    (12, 13), (13, 11), (15, 11), (8,  9),
    (11, 8),  (9,  10), (10, 12), (12, 16),
    (14, 16), (19, 17), (17, 18), (18, 20),
    (20, 19), (23, 19), (20, 24), (24, 23),
    (21, 23), (24, 22), (22, 21), (17, 21),
    (22, 18), (26, 25), (27, 28), (30, 29),
    (31, 30), (32, 33), (35, 34), (33, 36),
    (34, 37), (37, 31), (29, 38), (38, 35),
    (40, 39), (28, 40), (39, 27), (25, 42),
    (41, 26), (42, 41), (9,  31), (1,  25),
    (13, 35), (6,  27), (3,  42), (15, 33),
    (8,  37), (0,  26), (12, 29), (5,  28),
    (10, 30), (2,  41), (14, 36), (7,  39),
    (11, 34), (4,  40), (25, 21), (30, 27),
    (37, 40), (16, 15), (36, 32), (16, 32)]

faces = [
    (15, 16, 12, 10, 9, 8, 11), (26, 25, 21, 17, 19, 41),
    (6, 1, 0, 2, 4, 5), (4, 2, 3, 1, 6, 7),
    (4, 40, 28, 5), (5, 28, 27, 6), (6, 27, 39, 7),
    (7, 39, 40, 4), (0, 26, 41, 2), (1, 25, 26, 0),
    (3, 42, 25, 1), (2, 41, 42, 3), (14, 36, 33, 15),
    (15, 33, 32, 16), (13, 35, 38, 29, 12), (11, 34, 35, 13),
    (9, 31, 37, 8), (8, 37, 34, 11), (10, 30, 31, 9),
    (12, 29, 30, 10), (16, 32, 36, 14), (17, 18, 20, 19),
    (19, 20, 24, 23), (23, 24, 22, 21), (21, 22, 18, 17),
    (19, 23, 21, 25, 42, 41), (24, 20, 18, 22),
    (13, 12, 16, 14, 15, 11), (30, 29, 38, 35, 34, 37, 40, 39, 27),
    (33, 36, 32), (27, 28, 40, 37, 31, 30)]


def change_operation(ot, context):
    bc = context.window_manager.bc

    in_operation = ot.operation in {'ARRAY', 'SOLIDIFY', 'BEVEL', 'MIRROR'}

    if in_operation and ot.operation != bc.start_operation:
        bc.start_operation = ot.operation

    elif not in_operation and bc.start_operation != 'NONE':
        bc.start_operation = 'NONE'

    context.workspace.tools.update()


class BC_OT_draw_shape(Operator):
    bl_idname = 'bc.draw_shape'
    bl_label = 'BoxCutter'
    bl_description = F'{bl_info["description"][11:]}'
    bl_options = {'UNDO', 'USE_EVAL_DATA'}

    tool = None
    lmb: bool = False
    rmb: bool = False
    alt_lock: bool = False
    click_count: int = 0
    original_selected: list = []
    original_visible: list = []
    allow_menu: bool = False
    datablock: dict = datablock
    last: dict = last
    ray: dict = ray
    start: dict = start
    geo: dict = geo
    mouse: dict = mouse
    view3d: dict = view3d

    mouse: Vector = (0, 0)
    init_mouse: Vector = (0, 0)
    tweak: bool = False
    track: int = 0
    angle: int = 1

    extruded: bool = False

    lazorcut: bool = False
    show_shape: bool = False
    expand_offset: int = 0
    add_point: bool = False
    add_point_lock: bool = False
    lock_count: int = 0

    flip: bool = False

    snap: BoolProperty(default=False)

    active_only: BoolProperty(
        name = 'Active only',
        description = 'Cut only the active object',
        default = False)

    modified: BoolProperty(
        name = 'Modified',
        description = 'Shape has been modified',
        default = False)

    mode: EnumProperty(
        name = 'Mode',
        description = 'Mode',
        update = topbar.change_mode,
        items = [
            ('CUT', 'Cut', 'Modal Shortcut: X', icon.id('red'), 0),
            ('SLICE', 'Slice', 'Modal Shortcut: X', icon.id('yellow'), 1),
            ('INSET', 'Inset', 'Modal Shortcut: Z', icon.id('purple'), 3),
            ('JOIN', 'Join', 'Modal Shortcut: J', icon.id('green'), 4),
            ('KNIFE', 'Knife', 'Modal Shortcut: K', icon.id('blue'), 5),
            ('MAKE', 'Make', 'Modal Shortcut: A', icon.id('grey'), 6)],
        default = 'CUT')

    shape_type: EnumProperty(
        name = 'Shape',
        description = 'Shape',
        update = topbar.change_mode_behavior,
        items = [
            ('CIRCLE', 'Circle', '', 'MESH_CIRCLE', 0),
            ('BOX', 'Box', '', 'MESH_PLANE', 1),
            ('NGON', 'Ngon', '', 'MOD_SIMPLIFY', 2),
            ('CUSTOM', 'Custom', '', 'FILE_NEW', 3)],
        default = 'BOX')

    operation: EnumProperty(
        name = 'Operation',
        description = 'Modal Operation',
        update = change_operation,
        items = [
            ('NONE', 'Default', 'Modal Shortcut: TAB', 'LOCKED', 0),
            ('DRAW', 'Draw', 'Modal Shortcut: D', 'GREASEPENCIL', 1),
            ('EXTRUDE', 'Extrude', 'Modal Shortcut: E', 'ORIENTATION_NORMAL', 2),
            ('OFFSET', 'Offset', 'Modal Shortcut: O', 'MOD_OFFSET', 3),
            # ('MOVE', 'Move', 'Modal Shortcut: G', 'RESTRICT_SELECT_ON', 4),
            # ('ROTATE', 'Rotate', 'Modal Shortcut: R', 'DRIVER_ROTATIONAL_DIFFERENCE', 5),
            # ('SCALE', 'Scale', 'Modal Shortcut: S', 'FULLSCREEN_EXIT', 6),
            ('ARRAY', 'Array', 'Modal Shortcut: V', 'MOD_ARRAY', 7),
            ('SOLIDIFY', 'Solidify', 'Modal Shortcut: T', 'MOD_SOLIDIFY', 8),
            ('BEVEL', 'Bevel', ('Q: Toggle back face bevel\n\n'
                                'Modal Shortcut: B'), 'MOD_BEVEL', 9),
            ('MIRROR', 'Mirror', 'Modal Shortcut: 1, 2, 3', 'MOD_MIRROR', 10)],
        default = 'NONE')

    behavior: EnumProperty(
        name = 'Behavior',
        description = 'Behavior',
        items = [
            ('DESTRUCTIVE', 'Destructive', 'Modifiers will be applied'),
            ('NONDESTRUCTIVE', 'Non-Destructive', 'Modifiers will not be applied')],
        default = 'NONDESTRUCTIVE')

    axis: EnumProperty(
        items = [
            ('NONE', 'None', 'Use default behavior'),
            ('X', 'X', 'Modal Shortcut: X'),
            ('Y', 'Y', 'Modal Shortcut: Y'),
            ('Z', 'Z', 'Modal Shortcut: Z')],
        default = 'NONE')

    origin: EnumProperty(
        name = 'Origin',
        description = 'Shape Origin',
        items = [
            ('CORNER', 'Corner', 'Modal Shortcut: .', 'NODE_CORNER', 0),
            ('CENTER', 'Center', 'Modal Shortcut: .', 'FULLSCREEN_ENTER', 1)],
        default = 'CORNER')

    # TODO: on update enter ortho if enabled
    align_to_view: BoolProperty(
        name = 'Align to view',
        description = 'Align the shape to the viewport',
        default = False)

    live: BoolProperty(
        name = 'Live',
        description = 'Display the cuts during the modal',
        default = True)

    repeat: BoolProperty(
        name = 'Repeat',
        description = 'Repeat the last shape created',
        default = False)


    def invoke(self, context, event):
        preference = addon.preference()
        bc = context.window_manager.bc

        bc.running = True

        if self.shape_type != 'CUSTOM' or not hasattr(bc.collection, 'objects'):

            if 'Cutters' not in bpy.data.collections:
                bc['collection'] = bpy.data.collections.new(name='Cutters')
                context.scene.collection.children.link(bc.collection)

            else:
                bc['collection'] = bpy.data.collections['Cutters']

        if self.shape_type != 'CUSTOM':
            bc.shape = None

        elif not bc.shape:
            dat = bpy.data.meshes.new(name='Cutter')

            dat.from_pydata(verts, edges, faces)
            dat.validate()

            bc.shape = bpy.data.objects.new(name='Cutter', object_data=dat)
            del dat

            bc.shape.bc.shape = True

            bc.collection.objects.link(bc.shape)

            if addon.preference().behavior.auto_smooth:
                bc.shape.data.use_auto_smooth = True

                for face in bc.shape.data.polygons:
                    face.use_smooth = True

            if bc.original_active and preference.behavior.parent_shape:
                bc.shape.parent = bc.original_active

            bc.shape.hide_set(True)

        datablock = {
            'targets': list(),
            'overrides': list(),
            'dimensions': Vector((0, 0, 0)),
            'slices': list(),
            'operator': None,
            'duplicate': None,
            'plane': None,
            'box': None,
            'modifier': {
                'bevel': list()}}

        self.lmb = True
        self.rmb = False
        self.alt_lock = False
        self.click_count = 0
        self.add_point_lock = False
        self.lock_count = 0
        self.modified = False
        self.datablock = datablock
        self.last = last
        self.ray = ray_cast
        self.start = start
        self.start['extrude'] = 0.0
        self.geo = geo
        self.mouse = mouse
        self.view3d = view3d

        self.mouse['location'] = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last['mouse'] = self.mouse['location']
        self.init_mouse = self.last['mouse']
        self.datablock['targets'] = [obj for obj in context.selected_objects if obj.type == 'MESH']

        self.snap = bc.snap.display

        obj = context.active_object

        if obj:
            bc.original_active = obj
            self.original_selected = context.selected_objects[:]
            self.original_visible = context.visible_objects[:]

            self.datablock['dimensions'] = Vector((obj.dimensions.x, obj.dimensions.y, obj.dimensions.z))

        else:
            self.datablock['dimensions'] = Vector((1, 1, 1))

        del obj

        shapes_only = False not in [obj.bc.shape for obj in self.datablock['targets']]

        updated = topbar.update_operator(self, context)
        if not updated:
            context.window_manager.bc.running = False
            return {'PASS_THROUGH'}

        self.original_mode = context.workspace.tools_mode

        if preference.keymap.allow_selection and preference.keymap.edit_disable_modifiers and ((event.ctrl or (event.ctrl and event.shift)) and self.original_mode == 'EDIT_MESH'):
            context.window_manager.bc.running = False
            return {'PASS_THROUGH'}

        self.last['start_mode'] = self.mode
        self.last['start_operation'] = self.operation

        if not self.datablock['targets'] and preference.surface != 'CENTER':
            self.last['surface'] = preference.surface
            preference.surface = 'CENTER'

        else:
            self.last['surface'] = preference.surface

        if preference.behavior.auto_smooth:
            for obj in datablock['targets']:

                if not obj.data.use_auto_smooth:
                    obj.data.use_auto_smooth = True

                    for face in obj.data.polygons:
                        face.use_smooth = True

        objects = bc.collection.objects[:]
        name = bc.collection.name
        bpy.data.collections.remove(bc.collection)
        bc.collection = bpy.data.collections.new(name=name)
        context.scene.collection.children.link(bc.collection)

        for obj in objects:
            bc.collection.objects.link(obj)

        for obj in objects:
            active = bc.original_active and obj == bc.original_active
            selected = obj in self.original_selected[:]
            visible = obj in self.original_visible[:]
            hide = preference.behavior.autohide_shapes and not active and not selected

            if not active and not selected and not visible or hide:
                obj.hide_set(True)
            else:
                obj.hide_set(False)

        del objects

        if bc.original_active:
            bpy.context.view_layer.objects.active = bc.original_active

        for obj in self.original_selected:
            obj.select_set(True)

        # XXX: edit mode can lose active object info on undo
        if self.original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')

        data.create(self, context, event, custom=bc.shape)

        if self.operation == 'SOLIDIFY':
            bc.shape.bc.solidify = True
            modal.solidify.shape(self, context, event)

        elif self.operation == 'ARRAY':
            bc.shape.bc.array = True

            if self.axis == 'NONE':
                modal.axis.change(self, context, to='X')

            modal.array.shape(self, context, event)

        elif self.operation == 'BEVEL':
            bc.shape.bc.bevel = True
            modal.bevel.shape(self, context, event)

        modal.operation.change(self, context, event, to='DRAW', modified=False, init=True)

        if context.active_object:
            obj = context.active_object
            self.datablock['dimensions'] = Vector((obj.dimensions.x, obj.dimensions.y, obj.dimensions.z))

        else:
            self.datablock['dimensions'] = Vector((1, 1, 1))

        if preference.surface == 'OBJECT':
            hit, self.ray['location'], self.ray['normal'], index, object, matrix = ray.cast.objects(*self.mouse['location'])

            if not self.align_to_view and hit and not (bc.snap.hit and bc.snap.grid):
                modal.ray.surface(self, context, event)

                if self.last['start_operation'] == 'MIRROR':
                    bc.shape.bc.mirror = True
                    modal.mirror.shape(self, context, event)

                if self.repeat:
                    self.execute(context)

                    return {'FINISHED'}

                modal.mode.change(self, context, event, to=self.mode, init=True)
                self.flip = self.mode in {'JOIN', 'MAKE'}

                context.window_manager.modal_handler_add(self)
                self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(shader.shape, (self, context), 'WINDOW', 'POST_VIEW')

                return {'RUNNING_MODAL'}

            self.align_to_view = True
            modal.ray.screen(self, context, event)

            if self.last['start_operation'] == 'MIRROR':
                bc.shape.bc.mirror = True
                modal.mirror.shape(self, context, event)

            if self.repeat:
                self.execute(context)

                return {'FINISHED'}

            modal.mode.change(self, context, event, to=self.mode, init=True)
            self.flip = self.mode in {'JOIN', 'MAKE'}

            context.window_manager.modal_handler_add(self)
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(shader.shape, (self, context), 'WINDOW', 'POST_VIEW')

            return {'RUNNING_MODAL'}

        else:
            self.align_to_view = False
            modal.ray.custom(self, context, event)

            if self.last['start_operation'] == 'MIRROR':
                bc.shape.bc.mirror = True
                modal.mirror.shape(self, context, event)

            if self.repeat:
                self.execute(context)
                return {'FINISHED'}

            mode = self.mode if self.datablock['targets'] else 'MAKE'
            modal.mode.change(self, context, event, to=mode, init=True)
            self.flip = self.mode in {'JOIN', 'MAKE'}

            context.window_manager.modal_handler_add(self)
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(shader.shape, (self, context), 'WINDOW', 'POST_VIEW')

            return {'RUNNING_MODAL'}

        return {'FINISHED'}


    def execute(self, context):
        from ... utility import modifier

        preference = addon.preference()
        bc = context.window_manager.bc

        context.window_manager.bc.running = False

        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
        del self.draw_handler

        bc.shape.bc.target = context.active_object

        if self.original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        if self.shape_type != 'NGON' and sum(int(dimension < preference.shape.lazorcut_limit) for dimension in bc.shape.dimensions[:]) > 1:
            self.origin = last['origin']

            if self.last['geo']['verts']:
                dat = bpy.data.meshes.new(name='Cutter')

                verts = self.last['geo']['verts']
                edges = self.last['geo']['edges']
                faces = self.last['geo']['faces']

                dat.from_pydata(verts, edges, faces)
                dat.validate()

                if preference.behavior.auto_smooth:
                    if not dat.use_auto_smooth:
                        dat.use_auto_smooth = True

                        for face in dat.polygons:
                            face.use_smooth = True

                bc.shape.data = dat

                del dat

                for mod in bc.shape.modifiers:
                    bc.shape.modifiers.remove(mod)

        # TODO: Use lattice coords instead of dimensions, immediate/accurate lazorcut check
        if bc.lattice.dimensions[2] < preference.shape.lazorcut_limit and not self.repeat and bc.original_active:
            for obj in self.datablock['targets']:
                for mod in reversed(obj.modifiers[:]):
                    if mod.type == 'BOOLEAN' and mod.object == bc.shape:
                        mod.show_viewport = True

            if self.shape_type != 'NGON':
                for point in lattice.back:
                    if self.mode != 'MAKE':
                        bc.lattice.data.points[point].co_deform.z -= max(dimension for dimension in context.active_object.dimensions[:]) * 1.75

                    else:
                        bc.lattice.data.points[point].co_deform.z += 2.0

            else:
                if not self.extruded:
                    mesh.extrude(self, context, None)

                verts = [vert for vert in bc.shape.data.vertices[:] if vert.index in self.geo['indices']['extrusion']]

                for vert in verts:
                    vert.co.z -= max(dimension for dimension in context.active_object.dimensions[:]) * 1.75

            self.lazorcut = True
            context.scene.update()

        last['origin'] = self.origin
        last['points'] = [Vector(point.co_deform) for point in bc.lattice.data.points]

        for mod in bc.shape.modifiers:
            if mod.type == 'ARRAY':
                offsets = [abs(o) for o in mod.constant_offset_displace]
                if sum(offsets) < 0.0005:
                    bc.shape.modifiers.remove(mod)

                else:
                    index = offsets.index(max(offsets))
                    last['modifier']['offset'] = mod.constant_offset_displace[index]
                    last['modifier']['count'] = mod.count

            elif mod.type == 'BEVEL':
                if mod.width < 0.0005:
                    bc.shape.modifiers.remove(mod)

                else:
                    last['modifier']['width'] = mod.width if mod.width > last['modifier']['width'] else last['modifier']['width']
                    last['modifier']['segments'] = mod.segments

            elif mod.type == 'SOLIDIFY':
                if abs(mod.thickness) < 0.0005:
                    bc.shape.modifiers.remove(mod)

                else:
                    last['modifier']['thickness'] = mod.thickness

        if not self.repeat:
            duplicate = object.duplicate(bc.shape, link=True)
            original_active = context.active_object
            context.view_layer.objects.active = duplicate
            duplicate.data.bc.removeable = True

            modifier.apply(obj=duplicate)
            last['geo']['verts'] = [vertex.co.copy() for vertex in duplicate.data.vertices]
            last['geo']['edges'] = duplicate.data.edge_keys[:]
            last['geo']['faces'] = [face.vertices[:] for face in duplicate.data.polygons]

            context.view_layer.objects.active = original_active

            bpy.data.objects.remove(duplicate)

            del duplicate

        if self.original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT')

        data.clean(self)

        self.report({'INFO'}, 'Executed')

        return {'FINISHED'}


    def cancel(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
        del self.draw_handler

        self.geo['indices']['extrusion'].clear()

        if self.datablock['overrides']:
            for pair in zip(self.datablock['targets'], self.datablock['overrides']):
                obj = pair[0]
                override = pair[1]

                obj.data = override

        data.clean(self, all=True)

        self.report({'INFO'}, 'Cancelled')

        context.window_manager.bc.running = False


    def modal(self, context, event):
        preference = addon.preference()
        bc = context.window_manager.bc

        option = self.tool.operator_properties('bc.draw_shape')

        if option.mode != self.mode:
            modal.mode.change(self, context, event, to=option.mode)

        if option.operation != self.operation:
            modal.operation.change(self, context, event, to=option.operation)

        if option.behavior != self.behavior:
            modal.behavior.change(self, context, to=option.behavior)

        if option.axis != self.axis:
            modal.axis.change(self, context, to=option.axis)

        if option.origin != self.origin:
            modal.origin.change(self, context, event, to=option.origin)

        self.mouse['location'] = Vector((event.mouse_region_x, event.mouse_region_y))

        region = context.region

        self.show_shape = event.shift and preference.behavior.make_active
        self.use_cursor_depth = event.alt

        # TODO: jump to last operation when click dragging open space while locked (bevel by default)
        # TODO: when operation is updated from the topbar wait for lmb press before modal update
        pass_through = False
        if event.mouse_region_x < region.width and event.mouse_region_y < region.height:

            # MOUSEMOVE
            if event.type == 'MOUSEMOVE' and self.add_point and self.operation == 'DRAW':
                within_x = self.last['placed_mouse'].x - 0.5 < self.mouse['location'].x and self.last['placed_mouse'].x + 0.5 > self.mouse['location'].x
                within_y = self.last['placed_mouse'].y - 0.5 < self.mouse['location'].y and self.last['placed_mouse'].y + 0.5 > self.mouse['location'].y
                #
                if not within_x and not within_y:
                    mesh.add_point(self, context, event)
                    self.add_point = False

                pass_through = True

            elif self.operation != 'DRAW':
                self.add_point = False

            # LEFTMOUSE
            if event.type == 'LEFTMOUSE':
                if event.value == 'PRESS':
                    self.lmb = True

                if event.value == 'RELEASE':
                    self.lmb = False

                # TODO: add alt keymap override pref
                if not (event.alt and preference.keymap.alt_preserve) or (self.operation in {'DRAW', 'EXTRUDE'}):
                    if event.value == 'RELEASE':
                        self.allow_menu = False

                        if preference.behavior.quick_execute:
                            quick_execute = self.operation == 'DRAW' and not self.modified and not self.shape_type == 'NGON'
                        else:
                            quick_execute = False

                        execute_in_none = self.operation == 'NONE' and self.modified
                        execute_in_extrude = self.operation in {'EXTRUDE', 'OFFSET'} and not self.modified
                        self.lazorcut = bc.shape.dimensions[2] < preference.shape.lazorcut_limit

                        extrude_if_unmodified = self.operation == 'DRAW' and not self.modified and self.shape_type != 'NGON'

                        overlap = False
                        extrude_if_overlap = False
                        add_point = False

                        if self.shape_type == 'NGON':
                            matrix = bc.shape.matrix_world
                            enough_verts = len(bc.shape.data.vertices) > 1
                            extrude_if_overlap = self.operation == 'DRAW' and not self.modified and self.add_point
                            add_point = self.shape_type == 'NGON' and self.operation == 'DRAW' and not self.add_point

                        if not self.alt_lock:
                            if quick_execute or execute_in_none or execute_in_extrude or (self.lazorcut and execute_in_none):
                                if self.lazorcut and self.shape_type == 'NGON':
                                    bevel = False
                                    for mod in bc.shape.modifiers:
                                        if mod.type == 'BEVEL':
                                            bc.shape.modifiers.remove(mod)
                                            bevel = True

                                    if not self.extruded:
                                        modal.extrude.shape(self, context, event, extrude_only=True)

                                    if bevel:
                                        modal.bevel.shape(self, context, event)

                                if quick_execute and self.mode not in {'KNIFE', 'MAKE'}:
                                    modifier.create.boolean(self, show=True)

                                self.execute(context)

                                return {'FINISHED'}

                            elif self.modified:
                                self.last['operation'] = self.operation
                                modal.operation.change(self, context, event, to='NONE')

                            elif extrude_if_unmodified or extrude_if_overlap or self.add_point_lock:
                                self.last['mouse'] = self.mouse['location']
                                extrude = self.mode not in {'MAKE', 'JOIN'}
                                modal.operation.change(self, context, event, to='EXTRUDE' if extrude else 'OFFSET', modified=False)

                            elif add_point and not self.add_point_lock:
                                self.add_point = True
                                self.last['placed_mouse'] = self.mouse['location']

                else:
                    return {'PASS_THROUGH'}

                return {'RUNNING_MODAL'}

            # RIGHTMOUSE | BACKSPACE
            elif event.type == 'RIGHTMOUSE' or event.type == 'BACK_SPACE':
                removing_points = False
                if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
                    self.rmb = True

                if event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
                    self.rmb = False

                if not (event.alt and preference.keymap.alt_preserve) or event.type == 'BACK_SPACE':
                    if event.value == 'RELEASE':
                        ngon = self.shape_type == 'NGON' and self.operation == 'DRAW'
                        rmb_cancel = preference.keymap.rmb_cancel_ngon
                        last_count = 0

                        if self.alt_lock or (not rmb_cancel and event.type == 'RIGHTMOUSE' and ngon and len(bc.shape.data.vertices) == 2):
                            self.cancel(context)

                            return {'CANCELLED'}

                        elif ngon:
                            if event.type != 'RIGHTMOUSE' or (event.type == 'RIGHTMOUSE' and not rmb_cancel):
                                if event.type == 'RIGHTMOUSE' and not self.add_point and not self.add_point_lock and self.lock_count == 0:
                                    self.add_point_lock = True
                                    self.add_point = True
                                    self.lock_count = 1
                                elif event.type == 'RIGHTMOUSE' and self.add_point_lock:
                                    self.add_point_lock = False

                                mesh.remove_point(self, context, event)
                                removing_points = True

                            elif event.type == 'RIGHTMOUSE':
                                modal.operation.change(self, context, event, to='NONE')

                        elif self.operation != 'NONE':
                            modal.operation.change(self, context, event, to='NONE', clear_mods=[self.last['operation']] if self.last['operation'] in {'ARRAY', 'SOLIDIFY', 'BEVEL'} else [], modified=self.modified)

                        self.allow_menu = False
                        self.alt_lock = True if self.lmb else False

                        if not removing_points and not self.alt_lock and (self.operation == 'NONE' and not self.allow_menu or not self.modified):
                            self.cancel(context)

                            return {'CANCELLED'}

                else:
                    return {'PASS_THROUGH'}

                return {'RUNNING_MODAL'}

            # MIDDLEMOUSE
            elif event.type == 'MIDDLEMOUSE':
                return {'PASS_THROUGH'}

            # WHEELUPMOUSE
            elif event.type == 'WHEELUPMOUSE':
                if self.operation == 'BEVEL':
                    for mod in bc.shape.modifiers:
                        if mod.type == 'BEVEL':
                            mod.segments += 1
                            preference.shape.bevel_segments = mod.segments

                            break

                elif self.operation == 'ARRAY':
                    for mod in bc.shape.modifiers:
                        if mod.type == 'ARRAY':
                            mod.count += 1
                            # self.last['modifier']['count'] = mod.count
                            preference.shape.array_count = mod.count

                            break

                elif event.alt:
                    modal.cutter.cycle(self, context, event)

                else: return {'PASS_THROUGH'}

            # WHEELDOWNMOUSE
            elif event.type == 'WHEELDOWNMOUSE':
                if self.operation == 'BEVEL':
                    for mod in bc.shape.modifiers:
                        if mod.type == 'BEVEL':
                            mod.segments -= 1
                            preference.shape.bevel_segments = mod.segments

                            break

                elif self.operation == 'ARRAY':
                    for mod in bc.shape.modifiers:
                        if mod.type == 'ARRAY':
                            mod.count -= 1
                            preference.shape.array_count = mod.count

                            break

                elif event.alt:
                    modal.cutter.cycle(self, context, event, index=-1)

                else: return {'PASS_THROUGH'}

            # ESC
            elif event.type == 'ESC':
                if event.value == 'RELEASE':
                    ngon = self.shape_type == 'NGON' and self.operation == 'DRAW' and not self.add_point
                    if self.operation == 'NONE' and not self.allow_menu or (not self.modified and not ngon):
                        self.cancel(context)
                        return {'CANCELLED'}
                    elif self.operation != 'NONE':
                        modal.operation.change(self, context, event, to='NONE', clear_mods=[self.operation] if self.operation in {'ARRAY', 'SOLIDIFY', 'BEVEL'} else [])

                    self.allow_menu = False

            # RET
            elif event.type in {'RET', 'SPACE'}:
                self.execute(context)

                return {'FINISHED'}

            # ACCENT GRAVE
            elif event.type == 'ACCENT_GRAVE':
                if event.value == 'RELEASE':
                    modal.rotate.shape(self, context, event, inside=True)

            # TAB
            elif event.type == 'TAB':
                if event.value == 'RELEASE':
                    modal.operation.change(self, context, event, to='NONE', modified=self.modified)

            # .
            elif event.type == 'PERIOD' and self.shape_type != 'NGON':
                if event.value == 'RELEASE':
                    modal.origin.change(self, context, event, to='CENTER' if self.origin == 'CORNER' else 'CORNER')

            # 1, 2, 3
            elif event.type in {'ONE', 'TWO', 'THREE'}:
                if event.value == 'RELEASE':
                    axis = {
                        'ONE': 'X',
                        'TWO': 'Y',
                        'THREE': 'Z'}

                    modal.mirror.shape(self, context, event, to=axis[event.type])

            # A
            elif event.type == 'A':
                if event.value == 'RELEASE':
                    modal.mode.change(self, context, event, to='MAKE')

            # B
            elif event.type == 'B':
                if event.value == 'RELEASE':
                    self.last['mouse'] = self.mouse
                    modal.operation.change(self, context, event, to='BEVEL', clear_mods=[] if self.operation != 'BEVEL' else ['BEVEL'], modified=True)

            # D
            elif event.type == 'D':
                # if event.value == 'RELEASE':
                self.allow_menu = self.operation == 'NONE'

                if self.allow_menu:
                    return {'PASS_THROUGH'}

            # E
            elif event.type == 'E':
                if event.value == 'RELEASE':
                    mode = 'OFFSET' if self.operation == 'EXTRUDE' else 'EXTRUDE'
                    modal.operation.change(self, context, event, to=mode)

            # F
            elif event.type == 'F':
                if event.value == 'RELEASE':
                    self.flip = not self.flip

                    if self.operation == 'EXTRUDE':
                        modal.operation.change(self, context, event, to='OFFSET')

                    elif self.operation == 'OFFSET':
                        modal.operation.change(self, context, event, to='EXTRUDE')

            # G
            elif event.type == 'G':
                if event.value == 'RELEASE':
                    pass
            #         modal.operation.change(self, context, event, to='MOVE')

            # H
            elif event.type == 'H':
                if event.value == 'RELEASE':
                    preference.display.wire_only = not preference.display.wire_only

            # O
            elif event.type == 'O':
                if event.value == 'RELEASE':
                    modal.operation.change(self, context, event, to='OFFSET')

            # J
            elif event.type == 'J':
                if event.value == 'RELEASE':
                    modal.mode.change(self, context, event, to='JOIN')

            # K
            elif event.type == 'K':
                if event.value == 'RELEASE':
                    modal.mode.change(self, context, event, to='KNIFE')

            # M
            elif event.type == 'M':
                if event.value == 'RELEASE' and self.mode == 'SLICE':
                    wm = context.window_manager
                    hops = wm.Hard_Ops_material_options if hasattr(wm, 'Hard_Ops_material_options') else False
                    if hops:
                        mat = None
                        for obj in self.datablock['slices']:
                            mat = obj.material_slots[0].material
                            break

                        if not mat:
                            for obj in self.datablock['slices']:
                                obj.material_slots[0].material = bpy.data.materials[-1]

                                if not mat:
                                    mat = obj.material_slots[0].material

                        index = bpy.data.materials[:].index(mat)

                        for obj in self.datablock['slices']:
                            obj.material_slots[0].material = bpy.data.materials[index-1]

                        self.report({'INFO'}, mat.name)

            # Q
            elif event.type == 'Q':
                if event.value == 'RELEASE':
                    bc.shape.data.bc.q_beveled = not bc.shape.data.bc.q_beveled

                    for mod in bc.shape.modifiers:
                        if mod.type == 'BEVEL':
                            bc.shape.modifiers.remove(mod)

                    modal.bevel.shape(self, context, event)

            # R
            elif event.type == 'R':
                if event.value == 'RELEASE':
                    modal.rotate.shape(self, context, event, inside=True)
                    # modal.operation.change(self, context, event, to='ROTATE')

            # S
            elif event.type == 'S':
                if event.value == 'RELEASE':
                    pass
            #         modal.operation.change(self, context, event, to='SCALE')

            # T
            elif event.type == 'T':
                if event.value == 'RELEASE':
                    modal.operation.change(self, context, event, to='SOLIDIFY', clear_mods=[] if self.operation != 'SOLIDIFY' else ['SOLIDIFY'])

            # V
            elif event.type == 'V':
                if event.value == 'RELEASE':
                    modal.operation.change(self, context, event, to='ARRAY', clear_mods=[] if self.operation != 'ARRAY' else ['ARRAY'])

            # X, Y, Z
            elif event.type in {'X', 'Y', 'Z'}:
                if event.value == 'RELEASE':
                    if self.shape_type == 'NGON' and self.operation == 'DRAW' and event.type == 'Z' and event.ctrl:
                        mesh.remove_point(self, context, event)

                    elif self.operation in {'NONE', 'DRAW', 'EXTRUDE', 'OFFSET', 'BEVEL', 'SOLIDIFY'} and event.type in {'X', 'Z'}:
                        if event.type == 'X':
                            modal.mode.change(self, context, event, to='CUT' if self.mode != 'CUT' else 'SLICE')

                        elif event.type == 'Z':
                            modal.mode.change(self, context, event, to='INSET')

                    elif self.operation in {'MOVE', 'ROTATE', 'SCALE', 'ARRAY'}:
                        modal.axis.change(self, context, to=event.type)

            elif self.operation == 'NONE':
                return {'PASS_THROUGH'}

            if event.ctrl and not bc.snap.display:
                bpy.ops.bc.display_snap('INVOKE_DEFAULT')

            modal.refresh.shape(self, context, event)

        else:
            pass_through = True

        if pass_through:

            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}
