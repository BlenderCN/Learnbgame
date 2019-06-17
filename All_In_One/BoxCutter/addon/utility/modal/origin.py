from . import refresh
from ... import topbar


def change(ot, context, event, to='CORNER'):
    value = to

    ot.origin = value
    topbar.change_prop(context, 'origin', value)

    refresh.shape(ot, context, event)
