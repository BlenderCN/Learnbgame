from ... import topbar


def change(ot, context, to='NONE'):
    value = to

    ot.axis = value
    topbar.change_prop(context, 'axis', value)
