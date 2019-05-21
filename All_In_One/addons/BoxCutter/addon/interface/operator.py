from mathutils import Vector, Matrix

import bpy

from bpy.utils import register_class, unregister_class
from bpy.types import Operator
from bpy.props import *

from .. utility import update, addon, data, lattice, shader
from .. utility.ray import cast as ray_cast

#TODO: narrow depth of shape to axis closest matching shape
#TODO: return to starting mode on exit
#TODO: plane picking for open space click
#TODO: copy shape with ctrl+c

datablock = {
    'targets': [],
    'dimensions': Vector((0, 0, 0)),
    'slices': [],
    'operator': None,
    'duplicate': None,
    'plane': None,
    'box': None,
    'simple': None,
    'shape': None,
    'shape_d': None,
    'lattice': None,
    'empty': None}

last = {
    'mouse': Vector((0, 0)),
    'track': 0.0,
    'event_value': '',
    'operation': 'NONE',
    'start_mode': 'CUT',
    'start_operation': 'NONE',
    'axis': 'NONE',
    'coord': {
        'points': list(),
        'geometry': {
            'verts': list(),
            'edges': list(),
            'faces': list()}},
    'origin': 'CORNER',
    'modifier': {
        'thickness': 0.0,
        'offset': 0.0,
        'count': 0.0,
        'segments': 6,
        'width': 0.0},
    'angle': 0.0,
    'matrix': Matrix()}

ray = {
    'location': Vector((0, 0, 0)),
    'normal': Vector((0, 0, 0)),
    'index': 0,
    'distance': 0.0,
    'matrix': Matrix()}


class BC_OT_toolbar_activate(Operator):
    bl_idname = 'bc.toolbar_activate'
    bl_label = 'Activate BoxCutter'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        from bl_ui.space_toolsystem_common import activate_by_name

        activate_by_name(context, 'VIEW_3D', 'BoxCutter')

        #XXX: Remove when toolbar system is ready
        context.window_manager.keyconfigs.addon.keymaps['3D View'].keymap_items['bc.draw_shape'].active = True

        for kmi in context.window_manager.keyconfigs.addon.keymaps['3D View'].keymap_items:
            if kmi.idname == 'bc.draw_shape':
                kmi.active = True

        #TODO: set topbar mode to knife when entering

        addon.log(value='Activated boxcutter')
        self.report({'INFO'}, 'Activated BoxCutter')
        return {'FINISHED'}


class BC_OT_draw_shape(Operator):
    bl_idname = 'bc.draw_shape'
    bl_label = 'Box Cutter'
    bl_description = ('Draw shape\n'
                      ' \u2022 Best tool in the world\n'
                      ' \u2022 Obviously\n'
                      ' \u2022 Needs more pylons')
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR'}

    tool: None
    datablock: dict = datablock
    last: dict = last
    ray: dict = ray

    mouse: Vector = (0, 0)
    tweak: bool = False
    track: int = 0

    modified: bool = False
    lazorcut: bool = False
    show_shape: bool = False
    expand_offset: int = 0

    flip: bool = False

    mode: EnumProperty(
        name = 'Mode',
        description = 'Mode',
        items = [
            ('CUT', 'Cut', 'Modal Shortcut: X', 'MOD_OPACITY', 0),
            ('SLICE', 'Slice', 'Modal Shortcut: Z', 'MOD_BOOLEAN', 1),
            ('JOIN', 'Join', 'Modal Shortcut: J', 'MOD_EDGESPLIT', 2),
            # ('MAKE', 'Make', 'Modal Shortcut: A', 'MESH_CUBE', 3),
            ('KNIFE', 'Knife', 'Modal Shortcut: K', 'MOD_MULTIRES', 4)],
        default = 'CUT')

    shape: EnumProperty(
        name = 'Shape',
        description = 'Shape',
        items = [
            ('BOX', 'Box', '', 'MESH_PLANE', 0),
            ('CIRCLE', 'Circle', '', 'MESH_CIRCLE', 1)], #TODO: screw modifier with mesh vertice control
            # ('NGON', 'Ngon', '', 'MOD_SIMPLIFY', 2)], #TODO: if not manifold has a panel state (drag edge)
            # ('CUSTOM', 'Custom', '', 'FILE_NEW', 3)],
        default = 'BOX')

    vertices: IntProperty(
        name = 'Circle Vertices',
        description = 'Number of vertices in circle perimeter',
        min = 3,
        soft_max = 32,
        max = 64,
        default = 32)

    operation: EnumProperty(
        name = 'Operation',
        description = 'Modal Operation',
        items = [
            ('NONE', 'None', 'Modal Shortcut: TAB', 'LOCKED', 0),
            ('DRAW', 'Draw', 'Modal Shortcut: D', 'GREASEPENCIL', 1),
            ('EXTRUDE', 'Extrude', 'Modal Shortcut: E', 'ORIENTATION_NORMAL', 2),
            # ('OFFSET', 'Offset', 'Modal Shortcut: O', 'MOD_OFFSET', 3),
            ('MOVE', 'Move', 'Modal Shortcut: G', 'RESTRICT_SELECT_ON', 4),
            # ('ROTATE', 'Rotate', 'Modal Shortcut: R', 'DRIVER_ROTATIONAL_DIFFERENCE', 5),
            # ('SCALE', 'Scale', 'Modal Shortcut: S', 'FULLSCREEN_EXIT', 6),
            ('ARRAY', 'Array', 'Modal Shortcut: V', 'MOD_ARRAY', 7),
            # ('SOLIDIFY', 'Solidify', 'Modal Shortcut: T', 'MOD_SOLIDIFY', 8),
            ('BEVEL', 'Bevel', ('Q: Toggle back face bevel\n\n'
                                'Modal Shortcut: B'), 'MOD_BEVEL', 9)],
        default = 'NONE')

    angle: IntProperty(
        name = 'Angle',
        description = 'Angle step amount when rotating',
        min = 1,
        soft_max = 90,
        max = 360,
        default = 45)

    array_count: IntProperty(
        name = 'Array count',
        description = 'Array count',
        min = 1,
        soft_max = 32,
        default = 2)

    segments: IntProperty(
        name = 'Bevel Segments',
        description = 'Number of bevel segments',
        min = 1,
        soft_max = 20,
        max = 100,
        default = 6)
 
    behavior: EnumProperty(
        name = 'Behavior',
        description = 'Behavior',
        items = [
            ('DESTRUCTIVE', 'Destructive', 'Modifiers will be applied'),
            ('NONDESTRUCTIVE', 'Non-Destructive', 'Modifiers will not be applied')],
        default = 'NONDESTRUCTIVE')

    axis: EnumProperty(
        name = 'Axis',
        description = ('Primary axis for transform\n\n'
                       # 'Shared for operations:\n'
                       # '  u2022 DRAW\n' #TODO
                       # ' \u2022 Move\n'
                       # ' \u2022 Rotate\n'
                       # ' \u2022 Scale\n'
                       # ' \u2022 Mirror\n'
                       # ' \u2022 Array\n\n'
                       # ' \u2022 Updates mirror and array out of modal\n\n' #TODO
                       'Axis'),
        items = [
            ('NONE', 'None', 'Use default behavior'),
            ('X', 'X', 'Modal Shortcut: X'),
            ('Y', 'Y', 'Modal Shortcut: Y'),
            ('Z', 'Z', 'Modal Shortcut: Z')],
        default = 'NONE')

    origin: EnumProperty( #TODO: should not move lattice when changed
        name = 'Origin',
        description = 'Shape Origin',
        items = [
            ('CORNER', 'Corner', 'Modal Shortcut: .', 'VERTEXSEL', 0),
            ('CENTER', 'Center', 'Modal Shortcut: .', 'FACESEL', 1)],
        default = 'CORNER')

    mirror: BoolProperty(
        name = 'Mirror',
        description = ('Mirror the shape\n' # add mirror type EnumProperty, for shape/target origin
                       ' 1) Toggle X axis\n'
                       ' 2) Toggle Y axis\n'
                       ' 3) Toggle Z axis\n\n'
                       'Modal Shortcuts: 1, 2, 3'),
        default = False)

    align_to_view: BoolProperty(
        name = 'Align to view',
        description = 'Align the shape to the viewport',
        default = False)

    expand: BoolProperty(
        name = 'Expand',
        description = 'Expand the shape when using view aligned cutting',
        default = True)

    start_offset: FloatProperty(
        name = 'Start offset',
        description = 'Minor offset from object then creating shapes to prevent boolean overlap',
        min = 0.0001,
        max = 0.01,
        default = 0.0001)

    lazorcut_limit: FloatProperty(
        name = 'Lazor Cut Threshold',
        description = 'Depth threshold for automatically cutting through the target',
        min = 0.001,
        max = 0.1,
        default = 0.001)

    live: BoolProperty(
        name = 'Live',
        description = 'Display the cuts during the modal',
        default = True)

    repeat: BoolProperty(
        name = 'Repeat',
        description = 'Repeat the last shape created',
        default = False)


    #TODO: Support quadview and local view
    @classmethod
    def poll(cls, context):
        mode = context.active_object.mode if context.active_object else ''
        localview = bool(context.space_data.local_view)
        quadview = bool(context.space_data.region_quadviews)

        return mode in {'OBJECT', 'EDIT'} and not localview and not quadview


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.alignment = 'RIGHT'
        ot = row.operator('wm.url_open', icon='QUESTION', emboss=False)
        ot.url = 'https://masterxeon1001.com/2018/11/30/boxcutter-7-2-8-betascythe/'

        layout.prop(self, 'mode')
        layout.separator()
        layout.prop(self, 'behavior')
        layout.separator()


    def invoke(self, context, event):

        #TODO: need to create modifiers in a way that supports redo
        #XXX: Remove when toolbar system is ready
        from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools
        if view3d_tools.tool_active_from_context(context).name != 'BoxCutter':
            for kmi in context.window_manager.keyconfigs.addon.keymaps['3D View'].keymap_items:
                if kmi.idname == 'bc.draw_shape':
                    kmi.active = False

            return {'CANCELLED'}
        else:
            for kmi in context.window_manager.keyconfigs.addon.keymaps['3D View'].keymap_items:
                if kmi.idname == 'bc.draw_shape':
                    kmi.active = True

        for tool in context.workspace.tools:
            if tool.name == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                self.tool = tool
                self.mode = tool.operator_properties('bc.draw_shape').mode
                self.shape = tool.operator_properties('bc.draw_shape').shape
                self.vertices = tool.operator_properties('bc.draw_shape').vertices
                self.operation = tool.operator_properties('bc.draw_shape').operation
                self.behavior = tool.operator_properties('bc.draw_shape').behavior
                self.axis = tool.operator_properties('bc.draw_shape').axis
                self.origin = tool.operator_properties('bc.draw_shape').origin
                self.mirror = tool.operator_properties('bc.draw_shape').mirror
                self.align_to_view = tool.operator_properties('bc.draw_shape').align_to_view
                self.expand = tool.operator_properties('bc.draw_shape').expand
                self.live = tool.operator_properties('bc.draw_shape').live

                break
        ### ###

        data.clean(self, dead=True, init=True)
        addon.log(value='Cutter invoked')
        self.modified = False

        datablock = {
            'targets': [],
            'dimensions': Vector((0, 0, 0)),
            'slices': [],
            'operator': None,
            'duplicate': None,
            'plane': None,
            'box': None,
            'simple': None,
            'shape': None,
            'shape_d': None,
            'lattice': None,
            'empty': None}

        self.datablock = datablock
        self.last = last
        self.ray = ray

        preference = addon.preference()

        context.window_manager.bc.running = True

        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last['mouse'] = self.mouse
        self.last['mode'] = self.mode
        self.datablock['targets'] = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not self.datablock['targets']:
            bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')
            return {'CANCELLED'}

        elif preference.auto_smooth:
            for obj in datablock['targets']:

                if not obj.data.use_auto_smooth:
                    obj.data.use_auto_smooth = True

                    for face in obj.data.polygons:
                        face.use_smooth = True

        if preference.display_wires:
            for obj in datablock['targets']:
                obj.show_wire = not obj.show_wire
                obj.show_all_edges = not obj.show_all_edges

        if 'Cutters' not in bpy.data.collections:
            context.scene.collection.children.link(bpy.data.collections.new(name='Cutters'))

        if context.workspace.tools_mode == 'EDIT_MESH':
            update.modal.behavior(self, context, to='DESTRUCTIVE')

        data.create(self, context, event)

        self.ray['location'], self.ray['normal'], self.ray['index'], self.ray['distance'] = ray_cast.object(self, *self.mouse)

        self.last['start_mode'] = self.mode
        self.last['start_operation'] = self.operation

        update.modal.mode(self, context, event, to=self.mode, init=True)

        if self.operation == 'SOLIDIFY':
            update.modal.operation(self, context, event, to='SOLIDIFY', modified=False, init=True)

        elif self.operation == 'ARRAY':
            update.modal.operation(self, context, event, to='ARRAY', modified=False, init=True)

            axis_index = [self.axis == axis for axis in 'XYZ'].index(True)

            for mod in self.datablock['shape'].modifiers:
                if mod.type == 'ARRAY':

                    for index, offset in enumerate(mod.relative_offset_displace):
                        if index != axis_index:
                            mod.relative_offset_displace[index] = 0

                    mod.count = self.last['modifier']['count']
                    mod.relative_offset_displace[axis_index] = self.last['modifier']['offset']
                    break

        elif self.operation == 'BEVEL':
            update.modal.operation(self, context, event, to='BEVEL', modified=False)

        update.modal.operation(self, context, event, to='DRAW', modified=False, init=True)

        if not self.align_to_view and self.ray['location']:
            update.modal.ray(self, context, event)

            if self.repeat:
                self.execute(context)
                return {'FINISHED'}

            context.window_manager.modal_handler_add(self)
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(shader.shape, (self, context), 'WINDOW', 'POST_VIEW')
            addon.log(value='Modal running using ray coords', indent=2)
            return {'RUNNING_MODAL'}

        self.align_to_view = True
        update.modal.screen(self, context, event)

        if self.repeat:
            self.execute(context)
            return {'FINISHED'}

        context.window_manager.modal_handler_add(self)
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(shader.shape, (self, context), 'WINDOW', 'POST_VIEW')
        addon.log(value='Modal running using screen coords', indent=2)
        return {'RUNNING_MODAL'}


    def execute(self, context):
        global datablock
        global last

        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
        del self.draw_handler

        preference = addon.preference()

        context.window_manager.bc.running = False

        if sum(int(abs(dimension) < self.lazorcut_limit) for dimension in self.datablock['lattice'].dimensions[:]) > 1:
            self.origin = last['origin']

            if self.last['coord']['geometry']['verts']:
                dat = bpy.data.meshes.new(name='Cutter')

                verts = self.last['coord']['geometry']['verts']
                edges = self.last['coord']['geometry']['edges']
                faces = self.last['coord']['geometry']['faces']

                dat.from_pydata(verts, edges, faces)
                dat.validate()

                self.datablock['shape'].data = dat

                for modifier in self.datablock['shape'].modifiers:
                    self.datablock['shape'].modifiers.remove(modifier)

        if self.datablock['lattice'].dimensions[2] < self.lazorcut_limit and not self.repeat:

            for point in getattr(lattice, 'front'): #XXX backwards?
                self.datablock['lattice'].data.points[point].co_deform.z -= max(dimension for dimension in self.datablock['duplicate'].dimensions[:]) * 1.75

            addon.log(value='Performed lazorcut', indent=2)

        data.clean(self)
        del self.datablock

        self.report({'INFO'}, 'Executed')
        addon.log(value='Cutter executed', indent=1)

        return {'FINISHED'}


    def cancel(self, context):

        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
        del self.draw_handler

        context.window_manager.bc.running = False

        data.clean(self, all=True)
        del self.datablock

        self.report({'INFO'}, 'Cancelled')
        addon.log(value='Cutter cancelled', indent=1)


    def modal(self, context, event):
        preference = addon.preference()
        option = self.tool.operator_properties('bc.draw_shape')

        if option.mode != self.mode:
            update.modal.mode(self, context, event, to=option.mode)

        if option.vertices != self.vertices:
            self.vertices = option.vertices

            if self.shape == 'CIRCLE':
                for mod in self.datablock['shape'].modifiers:
                    if mod.type == 'SCREW':
                        mod.steps = option.vertices
                        self.vertices = option.vertices

                        break

                for mod in self.datablock['shape_d'].modifiers:
                    if mod.type == 'SCREW':
                        mod.steps = option.vertices

                        break

        if option.segments != self.segments:
            for mod in self.datablock['shape'].modifiers:
                if mod.type == 'BEVEL':
                    mod.segments = option.segments
                    self.segments = option.segments

                    break

        if option.array_count != self.array_count:
            for mod in self.datablock['shape'].modifiers:
                if mod.type == 'ARRAY':
                    mod.count = option.array_count
                    self.array_count = option.array_count

                    break

        if option.operation != self.operation:
            update.modal.operation(self, context, event, to=option.operation)

        if option.behavior != self.behavior:
            update.modal.behavior(self, context, to=option.behavior)

        if option.axis != self.axis:
            update.modal.axis(self, context, to=option.axis)

        if option.origin != self.origin:
            update.modal.origin(self, context, event, to=option.origin)

        if option.mirror != self.mirror:
            update.modal.mirro(self, context, to=option.axis)

        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        region = context.region

        self.show_shape = event.shift
        self.use_cursor_depth = event.alt

        #TOOD: jump to last operation when click dragging open space while locked (bevel by default)
        #TODO: when operation is updated from the topbar (line 786) wait for lmb press before update modal operation
        if event.mouse_region_x < region.width and event.mouse_region_y < region.height:

            # LEFTMOUSE
            if event.type == 'LEFTMOUSE':
                # if event.value == 'PRESS':
                #     if self.operation == 'NONE':
                #         pass
                        # set last moues
                        # if mouse distance greater then tweak
                            # if self.last['operation'] == 'EXTRUDE':
                            #     update.modal.operation(self, context, event, to='BEVEL')
                            # else:
                            #     update.modal.operation(self, context, event, to=self.last['operation'])

                if event.value == 'RELEASE' and not event.alt:
                    quick_apply = self.operation == 'DRAW' and not self.modified and self.align_to_view

                    # coolest way to spell it
                    lazorcut = self.datablock['lattice'].dimensions[0] < 0.001 or self.datablock['lattice'].dimensions[1] < 0.001

                    if quick_apply or (self.operation == 'NONE' and self.modified) or (self.operation == 'EXTRUDE' and not self.modified) or lazorcut:
                        self.execute(context)
                        return {'FINISHED'}

                    elif self.operation == 'DRAW' and not self.modified:
                        self.last['mouse'] = self.mouse
                        update.modal.operation(self, context, event, to='EXTRUDE', modified=False)

                    else:
                        self.last['operation'] = self.operation
                        update.modal.operation(self, context, event, to='NONE')

                return {'RUNNING_MODAL'} # prevent selection changing when locked

            # RIGHTMOUSE
            elif event.type == 'RIGHTMOUSE':
                if event.value == 'RELEASE':
                    if self.operation == 'NONE':
                        self.cancel(context)
                        return {'CANCELLED'}

                    else:
                        update.modal.operation(self, context, event, to='NONE', modified=False)

                return {'RUNNING_MODAL'} # prevent selection changing/right mouse menu when locked

            # MIDDLEMOUSE
            elif event.type == 'MIDDLEMOUSE':
                return {'PASS_THROUGH'}

            # WHEELUPMOUSE
            elif event.type == 'WHEELUPMOUSE':
                if self.operation == 'BEVEL':
                    for mod in self.datablock['shape'].modifiers:
                        if mod.type == 'BEVEL':
                            mod.segments += 1
                            self.last['modifier']['segments'] = mod.segments

                            break

                elif self.operation == 'ARRAY':
                    for mod in self.datablock['shape'].modifiers:
                        if mod.type == 'ARRAY':
                            mod.count += 1
                            self.last['modifier']['count'] = mod.count

                            break

                    if self.shape == 'CIRCLE':
                        for mod in self.datablock['shape_d'].modifiers:
                           if mod.type == 'ARRAY':
                                mod.count += 1
                                self.last['modifier']['count'] = mod.count

                                break

                else: return {'PASS_THROUGH'}

            # WHEELDOWNMOUSE
            elif event.type == 'WHEELDOWNMOUSE':
                if self.operation == 'BEVEL':
                    for mod in self.datablock['shape'].modifiers:
                        if mod.type == 'BEVEL':
                            mod.segments -= 1
                            self.last['modifier']['segments'] = mod.segments

                            break

                elif self.operation == 'ARRAY':
                    for mod in self.datablock['shape'].modifiers:
                        if mod.type == 'ARRAY':
                            mod.count -= 1
                            self.last['modifier']['count'] = mod.count

                            break

                    if self.shape == 'CIRCLE':
                        for mod in self.datablock['shape_d'].modifiers:
                           if mod.type == 'ARRAY':
                                mod.count -= 1
                                self.last['modifier']['count'] = mod.count

                                break


                else: return {'PASS_THROUGH'}

            # ESC
            elif event.type == 'ESC':
                if event.value == 'RELEASE':
                    self.cancel(context)
                    return {'CANCELLED'}

            # TAB
            elif event.type == 'TAB':
                if event.value == 'RELEASE':
                    update.modal.operation(self, context, event, to='NONE', modified=False)

            # .
            elif event.type == 'PERIOD':
                if event.value == 'RELEASE':
                    update.modal.origin(self, context, event, to='CENTER' if self.origin == 'CORNER' else 'CORNER')

            # 1, 2, 3
            # elif event.type in {'ONE', 'TWO', 'THREE'}:
            #     if event.value == 'RELEASE':
            #         axis = {
            #             'ONE': 'X',
            #             'TWO': 'Y',
            #             'THREE': 'Z'}

            #         update.modal.mirror(self, context, event, to=axis[event.type])

            # A
            # elif event.type == 'A':
            #     if event.value == 'RELEASE':
            #         update.modal.mode(self, context, event, to='MAKE')

            # B
            elif event.type == 'B':
                if event.value == 'RELEASE':
                    self.last['mouse'] = self.mouse
                    update.modal.operation(self, context, event, to='BEVEL')

            # D
            elif event.type == 'D':
                if event.value == 'RELEASE':
                    update.modal.operation(self, context, event, to='DRAW')

            # E
            elif event.type == 'E':
                if event.value == 'RELEASE':
                    update.modal.operation(self, context, event, to='EXTRUDE')

            # F
            elif event.type == 'F':
                if event.value == 'RELEASE':
                    self.flip = not self.flip

            # G
            elif event.type in {'G', 'SPACE'}:
                if event.value == 'RELEASE':
                    update.modal.operation(self, context, event, to='MOVE')

            # O
            # elif event.type == 'O':
            #     if event.value == 'RELEASE':
            #         update.modal.operation(self, context, event, to='OFFSET')

            # J
            elif event.type == 'J':
                if event.value == 'RELEASE':
                    update.modal.mode(self, context, event, to='JOIN')

            # K
            elif event.type == 'K':
                if event.value == 'RELEASE':
                    update.modal.mode(self, context, event, to='KNIFE')

            # Q
            elif event.type == 'Q':
                if event.value == 'RELEASE':
                    for mod in self.datablock['shape'].modifiers:
                        if mod.type == 'BEVEL':

                            if self.shape == 'BOX':
                                weight = 0 if self.datablock['shape'].data.edges[2].bevel_weight == 1.0 else 1

                                for index in (2, 5, 8, 11):
                                    self.datablock['shape'].data.edges[index].bevel_weight = weight

                                self.datablock['shape'].data.validate()
                                self.datablock['shape'].data.bc.q_beveled = bool(weight)

                            break

            # R
            # elif event.type == 'R':
            #     if event.value == 'RELEASE':
            #         update.modal.operation(self, context, event, to='ROTATE')

            # S
            # elif event.type == 'S':
            #     if event.value == 'RELEASE':
            #         update.modal.operation(self, context, event, to='SCALE')

            # T
            # elif event.type == 'T':
            #     if event.value == 'RELEASE':
            #         update.modal.operation(self, context, event, to='SOLIDIFY')

            # V
            elif event.type == 'V':
                if event.value == 'RELEASE':
                    update.modal.operation(self, context, event, to='ARRAY')

            # X, Y, Z
            elif event.type in {'X', 'Y', 'Z'}:
                if event.value == 'RELEASE':
                    if self.operation in {'NONE', 'DRAW', 'EXTRUDE', 'OFFSET', 'BEVEL'} and event.type in {'X', 'Z'}:
                        if event.type == 'X':
                            update.modal.mode(self, context, event, to='SLICE')

                        elif event.type == 'Z':
                            update.modal.mode(self, context, event, to='CUT')

                    elif self.operation in {'MOVE', 'ROTATE', 'SCALE', 'ARRAY'}:
                        update.modal.axis(self, context, to=event.type)

            elif self.operation == 'NONE':
                return {'PASS_THROUGH'}

            update.modal(self, context, event)

        else:

            return {'PASS_THROUGH'}


        return {'RUNNING_MODAL'}


classes = [
    BC_OT_toolbar_activate,
    BC_OT_draw_shape]


def register():
    for cls in classes:
        register_class(cls)

    addon.log(value='Added operators')


def unregister():
    for cls in classes:
        unregister_class(cls)

    addon.log(value='Removed operators')
