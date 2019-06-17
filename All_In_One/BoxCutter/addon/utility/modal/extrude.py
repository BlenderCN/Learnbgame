from .. import lattice, mesh


def shape(ot, context, event, extrude_only=False):
    lattice.extrude(ot, context, event)

    if ot.shape_type == 'NGON':
        mesh.extrude(ot, context, event, extrude_only=extrude_only)
