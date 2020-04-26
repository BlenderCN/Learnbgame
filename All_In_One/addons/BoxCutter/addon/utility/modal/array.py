from .. import addon, modifier
from .. screen import dpi_factor


# XXX: bevel before array
def shape(ot, context, event):
    preference = addon.preference()
    bc = context.window_manager.bc
    snap = preference.behavior.snap and preference.behavior.snap_increment
    axis_index = [ot.axis == axis for axis in 'XYZ'].index(True)

    array = None

    for mod in bc.shape.modifiers:
        if mod.type == 'ARRAY':
            array = mod

            break

    if not array:
        mod = bc.shape.modifiers.new('Array', 'ARRAY')
        mod.use_constant_offset = True
        mod.count = ot.last['modifier']['count']
        mod.constant_offset_displace[axis_index] = ot.last['modifier']['offset']

        modifier.sort(ot, bc.shape)

    else:
        mod = array

    del array

    for index, offset in enumerate(mod.constant_offset_displace):
        if index != axis_index:
            mod.relative_offset_displace[index] = 0
            mod.constant_offset_displace[index] = 0

    mod.count = 2 if mod.count < 2 else mod.count
    ot.last['modifier']['count'] = mod.count

    offset = (ot.mouse['location'].x - ot.last['mouse'].x) / dpi_factor()
    factor = 0.0001 if event.shift and not event.ctrl else 0.0075
    offset = ot.last['modifier']['offset'] + offset * factor
    relative = 1.0 if offset > 0 else -1.0

    if snap and event.ctrl:
        increment_amount = round(preference.behavior.increment_amount, 8)
        split = str(increment_amount).split('.')[1]
        increment_length = len(split) if int(split) != 0 else 0

        if event.shift:
            offset = round(round(offset * 10 / increment_amount) * increment_amount, increment_length)
            offset *= 0.1

        else:
            offset = round(round(offset / increment_amount) * increment_amount, increment_length)

    else:
        ot.last['modifier']['offset'] = offset
        ot.last['mouse'].x = ot.mouse['location'].x

    mod.relative_offset_displace[axis_index] = relative if not ot.flip else -relative
    mod.constant_offset_displace[axis_index] = offset if not ot.flip else -offset
