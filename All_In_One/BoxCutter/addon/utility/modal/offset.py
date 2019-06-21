from ... import topbar
from .. import lattice, mesh


def shape(ot, context, event):
    bc = context.window_manager.bc

    ngon = ot.shape_type == 'NGON'

    if ot.shape_type == 'NGON':
        if not ot.extruded:
            mesh.extrude(ot, context, event)

    if not ngon:
        lattice.offset(ot, context, event)
    else:
        mesh.offset(ot, context, event)
