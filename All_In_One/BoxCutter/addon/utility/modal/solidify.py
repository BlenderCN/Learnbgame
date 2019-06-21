from .. import addon
from .. screen import dpi_factor


def shape(ot, context, event):
    preference = addon.preference()
    bc = context.window_manager.bc
    snap = preference.behavior.snap and preference.behavior.snap_increment

    objects = [bc.shape] if ot.mode != 'INSET' else ot.datablock['slices']
    last = ot.last['modifier']['thickness'] if ot.mode != 'INSET' else ot.last['thickness']

    thickness = (ot.mouse['location'].x - ot.last['mouse'].x) / dpi_factor() * 0.001

    if snap and event.ctrl:
        if event.shift:
            thickness = -round(thickness, 1)

        else:
            thickness = -round(thickness)

    elif event.shift:
        thickness = (ot.mouse['location'].x - ot.last['mouse'].x) / dpi_factor() * 0.0001

    for obj in objects:
        solidify = None
        for mod in obj.modifiers:
            if mod.type == 'SOLIDIFY':
                solidify = mod
                mod.thickness = last + thickness

                if ot.mode != 'INSET':
                    preference.shape['solidify_thickness'] = mod.thickness
                else:
                    preference.shape['inset_thickness'] = mod.thickness

                if event.ctrl:
                    mod.thickness = round(mod.thickness, 2 if event.shift else 1)
                else:
                    if ot.mode != 'INSET':
                        ot.last['modifier']['thickness'] = mod.thickness
                    else:
                        ot.last['thickness'] = mod.thickness
                    ot.last['mouse'].x = ot.mouse['location'].x

                if mod.thickness > 0:

                    if mod.thickness < 0.001:
                        mod.thickness = 0.001

                    mod.thickness = -mod.thickness

                if mod.thickness > -0.001:
                    mod.thickness = -0.001

                break

        if not solidify:
            mod = obj.modifiers.new(name='Solidify', type='SOLIDIFY')
            mod.offset = -1
            mod.use_even_offset = True
            mod.use_quality_normals = True
            mod.thickness = last

    del objects
