from mathutils import Vector, Matrix

last = {
    'mouse': Vector((0, 0)),
    'mode': 'NONE',
    'surface': 'OBJECT',
    'placed_mouse': Vector((0, 0)),
    'track': 0,
    'event_value': '',
    'operation': 'NONE',
    'axis': 'NONE',
    'origin': 'CORNER',
    'thickness': -0.1,
    'extrude': float(),
    'modifier': {
        'thickness': 0.01,
        'offset': 0.01,
        'count': 2,
        'segments': 6,
        'width': 0.02},
    'angle': 0.0,
    'matrix': Matrix(),
    'points': list(),
    'geo': {
        'verts': list(),
        'edges': list(),
        'faces': list()}}


def offset(option, context):
    bc = context.window_manager.bc
    if bc.running:
        offset = Vector((0, 0, option.offset)) @ bc.lattice.matrix_world.inverted()
        bc.lattice.matrix_world.translation = Vector(bc.location[:]) + offset
        bc.shape.matrix_world = bc.lattice.matrix_world
        bc.plane.matrix_world = bc.lattice.matrix_world


def circle_vertices(option, context):
    bc = context.window_manager.bc
    if bc.running:
        for mod in bc.shape.modifiers:
            if mod.type == 'SCREW':
                mod.steps = option.circle_vertices


def bevel_width(option, context):
    bc = context.window_manager.bc
    if bc.running:
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                mod.width = option.bevel_width

                last['modifier']['width'] = option.bevel_width


def bevel_segments(option, context):
    bc = context.window_manager.bc
    if bc.running:
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                mod.segments = option.bevel_segments

                last['modifier']['segments'] = option.bevel_segments


def quad_bevel(option, context):
    bc = context.window_manager.bc
    if bc.running:
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                bc.shape.modifiers.remove(mod)


def straight_edges(option, context):
    bc = context.window_manager.bc
    if bc.running:
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                bc.shape.modifiers.remove(mod)


def inset_thickness(option, context):
    bc = context.window_manager.bc
    if bc.running:
        for mod in bc.inset.modifiers:
            if mod.type == 'SOLIDIFY':
                mod.thickness = option.inset_thickness

                last['thickness'] = option.inset_thickness


def solidify_thickness(option, context):
    bc = context.window_manager.bc
    if bc.running:
        for mod in bc.shape.modifiers:
            if mod.type == 'SOLIDIFY':
                mod.thickness = option.solidify_thickness

                last['modifier']['thickness'] = option.solidify_thickness


def array_count(option, context):
    bc = context.window_manager.bc
    if bc.running:
        for mod in bc.shape.modifiers:
            if mod.type == 'ARRAY':
                mod.count = option.array_count

                last['modifier']['count'] = option.array_count


def allow_selection(option, context):
    wm = context.window_manager
    active_keyconfig = wm.keyconfigs.active
    addon_keyconfig = wm.keyconfigs.addon


    for kc in (active_keyconfig, addon_keyconfig):
        for kmi in kc.keymaps['3D View Tool: BoxCutter'].keymap_items:
            if kmi.idname == 'bc.draw_shape' and not kmi.ctrl and not kmi.shift and kmi.map_type != 'TWEAK':
                kmi.active = not option.allow_selection

    del active_keyconfig
    del addon_keyconfig
