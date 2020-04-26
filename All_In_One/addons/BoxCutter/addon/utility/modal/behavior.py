from ... import topbar


def change(ot, context, to='DESTRUCTIVE'):
    value = to

    ot.behavior = value
    topbar.change_prop(context, 'behavior', value)
