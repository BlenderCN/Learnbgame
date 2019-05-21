"""BlenderFDS, FDS MESH routines"""

from blenderfds.lib import utilities
from blenderfds import geometry

def n_for_poisson(n):
    """Get a good number for poisson solver at least bigger than n"""
    good = set((1, 2, 3, 5))
    while True:
        if [i for i in utilities.factor(n) if i not in good]: n += 1
        else: break
    return n

def get_good_ijk(current_ijk):
    """Get a good IJK near to the current one"""
    return current_ijk[0], n_for_poisson(current_ijk[1]), n_for_poisson(current_ijk[2])

def get_cell_sizes(context, ob):
    """Get MESH cell sizes from object"""
    # Init
    bf_mesh_ijk = ob.bf_mesh_ijk
    dimensions = geometry.utilities.get_global_dimensions(context, ob)
    return [
        dimensions[0] / bf_mesh_ijk[0],
        dimensions[1] / bf_mesh_ijk[1],
        dimensions[2] / bf_mesh_ijk[2],
    ]
    
def set_cell_sizes(context, ob, desired_cell_sizes, snap_to_origin=True, poisson_restriction=True):
    """Set exact MESH cell size to Blender object by adapting its dimensions.
    Apply Poisson Solver restriction on IJK and snap to global origin of axis, if requested."""
    # Get current_xbs and unpack it
    current_xbs, msg = geometry.to_fds.ob_to_xbs_bbox(context, ob)
    x0, x1, y0, y1, z0, z1 = current_xbs[0]
    # Calc nearest ijk values and optimize them for Poisson solver
    new_ijk = (
        round(abs(x1-x0) / desired_cell_sizes[0]) or 1, # along x
        round(abs(y1-y0) / desired_cell_sizes[1]) or 1, # along y
        round(abs(z1-z0) / desired_cell_sizes[2]) or 1, # along z
    )
    if poisson_restriction: new_ijk = get_good_ijk(new_ijk)
    # Update bbox xb for element
    if snap_to_origin:
        x0 = round(x0 / desired_cell_sizes[0]) * desired_cell_sizes[0]
        y0 = round(y0 / desired_cell_sizes[1]) * desired_cell_sizes[1]
        z0 = round(z0 / desired_cell_sizes[2]) * desired_cell_sizes[2]
    x1 = x0 + new_ijk[0] * desired_cell_sizes[0]
    y1 = y0 + new_ijk[1] * desired_cell_sizes[1]
    z1 = z0 + new_ijk[2] * desired_cell_sizes[2]
    # Send new geometry to object, do not change the center
    ob.bf_mesh_ijk = new_ijk
    geometry.from_fds.xbs_to_ob(((x0, x1, y0, y1, z0, z1),), context, ob, bf_xb="BBOX", update_center=False)
    
def get_cell_infos(context, ob):
    """Get many cell infos from object"""
    # Init
    bf_mesh_ijk = ob.bf_mesh_ijk
    cell_sizes = get_cell_sizes(context, ob)
    # Good IJK
    has_good_ijk = tuple(bf_mesh_ijk) == get_good_ijk(bf_mesh_ijk)
    # Cell number
    cell_number = bf_mesh_ijk[0] * bf_mesh_ijk[1] * bf_mesh_ijk[2]
    # Cell aspect ratio
    cell_sizes.sort()
    try: cell_aspect_ratio = max(cell_sizes[2] / cell_sizes[0], cell_sizes[2] / cell_sizes[1], cell_sizes[1] / cell_sizes[0])
    except ZeroDivisionError: cell_aspect_ratio = 999.
    # Return
    return has_good_ijk, cell_sizes, cell_number, cell_aspect_ratio

