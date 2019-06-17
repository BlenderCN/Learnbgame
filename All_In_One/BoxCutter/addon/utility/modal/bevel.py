import bpy

from mathutils import Vector

from .. import addon, mesh, modifier
from .. screen import dpi_factor


# XXX: bevel before array
def shape(ot, context, event):
    preference = addon.preference()
    bc = context.window_manager.bc
    snap = preference.behavior.snap and preference.behavior.snap_increment

    if ot.shape_type != 'NGON' or (ot.shape_type == 'NGON' and len(bc.shape.data.vertices) > 2):
        min_dimension = (min(float(i) for i in bc.shape.dimensions if i > 0.001))
        width = ((ot.mouse['location'].x - ot.last['mouse'].x) / dpi_factor()) * abs(min_dimension)
        factor = 0.0001 if event.shift else 0.001

        if preference.shape.quad_bevel:
            if not preference.shape.straight_edges:
                mesh.bevel_weight(ot, context, event)

            else:
                mesh.vertex_group(ot, context, event)
        else:
            mesh.bevel_weight(ot, context, event)

        m = None
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                m = mod
                break

        if not m:
            if ot.shape_type == 'NGON' and not ot.extruded:
                mod = bc.shape.modifiers.new(name='Bevel', type='BEVEL')
                mod.show_expanded = False
                mod.use_only_vertices = True
                mod.width = ot.last['modifier']['width']
                mod.segments = preference.shape.bevel_segments
                mod.limit_method = 'ANGLE'
                mod.offset_type = 'OFFSET'

            elif not preference.shape.quad_bevel or (preference.shape.quad_bevel and not preference.shape.straight_edges):
                mod = bc.shape.modifiers.new(name='Bevel', type='BEVEL')
                mod.show_expanded = False
                mod.width = ot.last['modifier']['width']
                mod.segments = preference.shape.bevel_segments
                mod.limit_method = 'WEIGHT'
                mod.offset_type = 'OFFSET'

                if mod.width > clamp(ot):
                    mod.width = clamp(ot) - 0.0025

            vertex_groups = bc.shape.vertex_groups if not preference.shape.straight_edges else reversed(bc.shape.vertex_groups)
            for group in vertex_groups:
                mod = bc.shape.modifiers.new(name='Bevel', type='BEVEL')
                mod.show_expanded = False
                mod.width = ot.last['modifier']['width']
                mod.segments = preference.shape.bevel_segments
                mod.limit_method = 'VGROUP'
                mod.vertex_group = group.name
                mod.offset_type = 'OFFSET'

                if mod.vertex_group == 'bottom' and not preference.shape.straight_edges:
                    mod.offset_type = 'WIDTH'

                if mod.width > clamp(ot):
                    mod.width = clamp(ot) - 0.0025

            modifier.sort(ot, bc.shape)

        else:
            for mod in bc.shape.modifiers:
                if mod.type == 'BEVEL':
                    mod.width = ot.last['modifier']['width'] + width * factor if ot.last['modifier']['width'] + width * factor > 0.0004 else 0.0004

                    if mod.width > clamp(ot):
                        mod.width = clamp(ot) - 0.0025

                    preference.shape['bevel_width'] = mod.width

                    if snap and event.ctrl:
                        mod.width = round(mod.width, 2 if event.shift else 1)
                    else:
                        ot.last['modifier']['width'] = mod.width
                        ot.last['mouse'].x = ot.mouse['location'].x

# XXX need a better clamp method
def clamp(ot):
    bc = bpy.context.window_manager.bc

    vector1 = Vector(bc.shape.bound_box[0][:])
    vector2 = Vector(bc.shape.bound_box[1][:])
    vector3 = Vector(bc.shape.bound_box[5][:])
    vector4 = Vector(bc.shape.bound_box[6][:])
    distances = [vector4 - vector3, vector3 - vector2]

    if bc.shape.data.bc.q_beveled:
        distances.append((vector2 - vector1) * 2)

    return max(min(distances)) * 0.5
