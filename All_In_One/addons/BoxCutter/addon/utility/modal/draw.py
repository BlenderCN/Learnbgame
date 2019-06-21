from .. import lattice, mesh


def shape(ot, context, event):
    within_x = ot.mouse['location'].x < ot.init_mouse.x + 1 and ot.mouse['location'].x > ot.init_mouse.x - 1
    within_y = ot.mouse['location'].y < ot.init_mouse.y + 1 and ot.mouse['location'].y > ot.init_mouse.y - 1
    if not within_x and not within_y:
        if ot.shape_type != 'NGON':
            lattice.draw(ot, context, event)
        else:
            mesh.draw(ot, context, event)
