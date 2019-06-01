"""BlenderFDS, voxelize algorithm."""

import bpy
from time import time
from blenderfds.geometry.utilities import epsilon, get_global_mesh, get_new_object, get_bbox, get_tessfaces, move_xbs, calc_movement_from_bbox1_to_bbox0 
from blenderfds.geometry.tmp import set_tmp_object
from blenderfds.types import BFException

DEBUG = False

# "global" coordinates are absolute coordinate referring to Blender main origin of axes,
# that are directly transformed to FDS coordinates (that refer to the only origin of axes) 

def voxelize(context, ob, flat=False) -> "(xbs, voxel_size, timing)":
    """Voxelize object."""
    print("BFDS: voxelize.voxelize:", ob.name)
    
    # ob: original object in local coordinates
    # ob_bvox: original object in global coordinates, before voxelization
    # ob_avox: voxelized object in global coordinates, after voxelization

    ## Init: check, voxel_size
    t0 = time()
    if not ob.data.vertices: raise BFException(sender=ob, msg="Empty object!")
    if ob.bf_xb_custom_voxel: voxel_size = ob.bf_xb_voxel_size
    else: voxel_size = context.scene.bf_default_voxel_size

    ## Voxelize object
    # Get original object and its bbox in global coordinates (remesh works in local coordinates)
    ob_bvox = get_new_object(context, "bvox", get_global_mesh(context, ob), linked=False)
    bbox_bvox = get_bbox(ob_bvox)
    # If flat, solidify and get flatten function for later generated xbs
    if flat: flat_origin, choose_flatten = _solidify_flat_ob(context, ob_bvox, voxel_size/3.)
    # Apply remesh modifier, update voxel_size (can be a little different from desired)
    octree_depth, scale, voxel_size = _calc_remesh_modifier(context, ob.dimensions, voxel_size)
    _apply_remesh_modifier(context, ob_bvox, octree_depth, scale)
    # Get voxelized object and its bbox
    ob_avox = get_new_object(context, "avox", get_global_mesh(context, ob_bvox), linked=False)
    bbox_avox = get_bbox(ob_avox)

    ## Find, build and grow boxes
    # Get and check tessfaces
    tessfaces = get_tessfaces(context, ob_avox.data)
    if not tessfaces: raise BFException(sender=ob, msg="No tessfaces available, cannot voxelize.")
    # Sort tessfaces centers by face normal: normal to x, to y, to z.
    t1 = time()
    x_tessfaces, y_tessfaces, z_tessfaces = _sort_tessfaces_by_normal(tessfaces)
    # Choose fastest procedure: less tessfaces => less time required
    # Better use the smallest collection first!
    t2 = time()
    choose = [
        (len(x_tessfaces), x_tessfaces, _x_tessfaces_to_boxes, _grow_boxes_along_x, _x_boxes_to_xbs),
        (len(y_tessfaces), y_tessfaces, _y_tessfaces_to_boxes, _grow_boxes_along_y, _y_boxes_to_xbs),
        (len(z_tessfaces), z_tessfaces, _z_tessfaces_to_boxes, _grow_boxes_along_z, _z_boxes_to_xbs),
    ]
    choose.sort(key=lambda k:k[0]) # sort by len(tessfaces)
    # Build minimal boxes along 1st axis, using floors
    t3 = time()
    boxes, origin = choose[0][2](choose[0][1], voxel_size) # eg. _x_tessfaces_to_boxes(x_tessfaces, voxel_size)
    # Grow boxes along 2nd axis
    t4 = time()
    boxes = choose[1][3](boxes) # eg. _grow_boxes_along_y(boxes)
    # Grow boxes along 3rd axis
    t5 = time()
    boxes = choose[2][3](boxes) # eg. _grow_boxes_along_z(boxes)

    ## Make xbs
    # Transform grown boxes in xbs
    t6 = time()
    xbs = choose[0][4](boxes, voxel_size, origin) # eg. _x_boxes_to_xbs(boxes, ...)
    # Center xbs to original bbox
    move_xbs(xbs, calc_movement_from_bbox1_to_bbox0(bbox_bvox, bbox_avox))
    # If flat, flatten xbs at flat_origin
    if flat: xbs = choose_flatten(xbs, flat_origin)

    ## Clean up
    if DEBUG:
        bpy.data.objects.remove(ob_bvox)        
        context.scene.objects.link(ob_avox) # create unlinked for speed
        set_tmp_object(context, ob, ob_avox) # it is left as a tmp object
    else:
        bpy.data.objects.remove(ob_bvox)
        bpy.data.objects.remove(ob_avox)

    ## Return
    return xbs, voxel_size, (t2-t1, t4-t3, t5-t4, t6-t5) # this is timing: sort, 1b, 2g, 3g 

def _solidify_flat_ob(context, ob, thickness):
    """Solidify a flat object. Apply modifier, return flat_origin and flatten function for later generated xbs."""
    # Set flat_origin at any vertices of original flat ob
    flat_origin = ob.data.vertices[0].co
    # Choose flat dimension and set according xbs flatten function
    if   ob.dimensions[0] < epsilon: choose_flatten = _x_flatten_xbs # the face is normal to x axis
    elif ob.dimensions[1] < epsilon: choose_flatten = _y_flatten_xbs # ... to y axis
    elif ob.dimensions[2] < epsilon: choose_flatten = _z_flatten_xbs # ... to z axis
    else: raise BFException(sender=ob, msg="Not flat and normal to axis, cannot create pixels.")
    # Solidify
    _apply_solidify_modifier(context, ob, thickness)
    # Return the function that is going to be used to flatten later generated xbs
    return flat_origin, choose_flatten

# When appling a remesh modifier, object max dimension is scaled up
# and divided in 2 ** octree_depth voxels
# Example: dimension = 0.6, voxel_size = 0.2, octree_depth = 2, number of voxels = 2^2 = 4, scale = 3/4 = 0.75
# |-----|-----|-----|-----| voxels, dimension / scale
#    |=====.=====.=====|    dimension

def _calc_remesh_modifier(context, dimensions, voxel_size):
    """Calc Remesh modifier parameters for voxel_size."""
    # Get max dimension and init flag
    dimension = max(dimensions)
    dimension_too_large = True
    # Fix voxel_size for Blender remesh algorithm
    # If dimension / voxel_size is "too integer" voxelization is not very good.
    while abs(dimension / voxel_size - round(dimension / voxel_size)) < 1E-3: voxel_size -= 1E-3
    # Find righ octree_depth and relative scale
    for octree_depth in range(1,11):
        scale = dimension / voxel_size / 2 ** octree_depth
        if 0.100 < scale < 0.900: # Was 0.010...0.990
            dimension_too_large = False
            break
    if dimension_too_large: raise BFException(sender=ob, msg="Too large for desired resolution, split object!")
    # Return
    return octree_depth, scale, voxel_size

def _apply_remesh_modifier(context, ob, octree_depth, scale):
    """Apply remesh modifier for voxelization."""
    mo = ob.modifiers.new('voxels_tmp','REMESH') # apply modifier
    mo.mode, mo.use_remove_disconnected, mo.octree_depth, mo.scale = 'BLOCKS', False, octree_depth, scale

def _apply_solidify_modifier(context, ob, thickness):
    """Apply solidify modifier with centered thickness."""
    mo = ob.modifiers.new('solid_tmp','SOLIDIFY') # apply modifier
    mo.thickness, mo.offset = thickness, thickness / 2. # Set centered thickness

# Sort tessfaces by normal: collection of tessfaces normal to x, to y, to z
# tessfaces created by the Remesh modifier in BLOCKS mode are perpendicular to a local axis
# we used a global object, the trick is done: tessfaces are perpendicular to global axis

def _sort_tessfaces_by_normal(tessfaces):
    """Sort tessfaces: normal to x axis, y axis, z axis."""
    print("BFDS: _sort_tessfaces_by_normal:", len(tessfaces))
    x_tessfaces, y_tessfaces, z_tessfaces = list(), list(), list()
    for tessface in tessfaces:
        normal = tessface.normal
        if   abs(normal[0]) > .9: x_tessfaces.append(tessface) # tessface is normal to x axis
        elif abs(normal[1]) > .9: y_tessfaces.append(tessface) # ... to y axis
        elif abs(normal[2]) > .9: z_tessfaces.append(tessface) # ... to z axis
        else: raise ValueError("BFDS: voxelize._sort_tessfaces_by_normal: abnormal face")
    return x_tessfaces, y_tessfaces, z_tessfaces

# First, we transform the global tessface center coordinates
# in integer coordinates referred to origin point:
# - voxel_size is used as step;
# - origin is the first of tessface centers;
# - (center[0] - origin[0]) / voxel_size is rounded from float to integers: ix, iy, iz

# Then we pile integer heights of floors for each location:
# (ix, iy -> location int coordinates):
#    (iz0, iz1, ... -> list of floors int coordinates)

# Last we use this "floor levels" (eg. izs) to detect solid volumes.
# Eg. at location (ix, iy) of int coordinates, at izs[0] floor go into solid,
# at izs[1] go out of solid, at izs[2] go into solid, ...
# z axis --> floor 0|==solid==1| void 2|==solid==3| void ...
# If solid is manifold, len(izs) is an even number: go into solid at izs[0], get at last out of it at izs[-1].

# In fact this floors can be easily transformed in boxes:
# (ix0, ix1, iy0, iy1, iz0, iz1)
# boxes are very alike XBs, but in integer coordinates.

def _x_tessfaces_to_boxes(x_tessfaces, voxel_size) -> "[(ix0, ix1, iy0, iy1, iz0, iz1), ...], origin":
    """Transform _x_tessfaces into minimal boxes."""
    print("BFDS: _x_tessfaces_to_boxes:", len(x_tessfaces))
    # Create floors
    origin = tuple(x_tessfaces[0].center) # First tessface center becomes origin
    floors = dict() # {(3,4):(3,4,15,25,), (3,5):(3,4,15,25), ...}
    for tessface in x_tessfaces:
        center = tuple(tessface.center)
        ix = round((center[0] - origin[0]) / voxel_size) # integer coordinates for this face (a floor)
        iy = round((center[1] - origin[1]) / voxel_size)
        iz = round((center[2] - origin[2]) / voxel_size)
        try: floors[(iy, iz)].append(ix) # append face ix to list of ixs
        except KeyError: floors[(iy, iz)] = [ix,] # or create new list of ixs from face ix
    # Create minimal boxes
    boxes = list()
    while floors:
        (iy, iz), ixs = floors.popitem()
        ixs.sort() # sort from bottom to top in +x direction
        while ixs:
            ix1 = ixs.pop() # pop from top to bottom in -x direction
            ix0 = ixs.pop()
            boxes.append((ix0, ix1, iy, iy, iz, iz,))
    return boxes, origin

def _y_tessfaces_to_boxes(y_tessfaces, voxel_size) -> "[(ix0, ix1, iy0, iy1, iz0, iz1), ...], origin":
    """Transform _y_tessfaces into minimal boxes."""
    print("BFDS: _y_tessfaces_to_boxes:", len(y_tessfaces))
    # Create floors
    origin = tuple(y_tessfaces[0].center) # First tessface center becomes origin
    floors = dict() # {(3,4):(3,4,15,25,), (3,5):(3,4,15,25), ...}
    for tessface in y_tessfaces:
        center = tuple(tessface.center)
        ix = round((center[0] - origin[0]) / voxel_size) # integer coordinates for this face (a floor)
        iy = round((center[1] - origin[1]) / voxel_size)
        iz = round((center[2] - origin[2]) / voxel_size)
        try: floors[(ix, iz)].append(iy) # append face iy to existing list of iys
        except KeyError: floors[(ix, iz)] = [iy,] # or create new list of iys from face iy
    # Create minimal boxes
    boxes = list()
    while floors:
        (ix, iz), iys = floors.popitem()
        iys.sort() # sort from bottom to top in +y direction
        while iys:
            iy1 = iys.pop() # pop from top to bottom in -y direction
            iy0 = iys.pop()
            boxes.append((ix, ix, iy0, iy1, iz, iz,))
    return boxes, origin

def _z_tessfaces_to_boxes(z_tessfaces, voxel_size) -> "[(ix0, ix1, iy0, iy1, iz0, iz1), ...], origin":
    """Transform _z_tessfaces into minimal boxes."""
    print("BFDS: _z_tessfaces_to_boxes:", len(z_tessfaces))
    # Create floors
    origin = tuple(z_tessfaces[0].center) # First tessface center becomes origin
    floors = dict() # {(3,4):(3,4,15,25,), (3,5):(3,4,15,25), ...}
    for tessface in z_tessfaces:
        center = tuple(tessface.center)
        ix = round((center[0] - origin[0]) / voxel_size) # integer coordinates for this face (a floor)
        iy = round((center[1] - origin[1]) / voxel_size)
        iz = round((center[2] - origin[2]) / voxel_size)
        try: floors[(ix, iy)].append(iz) # append face iz to existing list of izs
        except KeyError: floors[(ix, iy)] = [iz,] # or create new list of izs from face iz
    # Create minimal boxes  
    boxes = list()
    while floors:
        (ix, iy), izs = floors.popitem()
        izs.sort() # sort from bottom to top in +z direction
        while izs:
            iz1 = izs.pop() # pop from top to bottom in -z direction
            iz0 = izs.pop()
            boxes.append((ix, ix, iy, iy, iz0, iz1,))
    return boxes, origin

# Merge each minimal box with available neighbour boxes in axis direction

def _grow_boxes_along_x(boxes) -> "[(ix0, ix1, iy0, iy1, iz0, iz1), ...]":
    """Grow boxes by merging neighbours along x axis."""
    print("BFDS: _grow_boxes_along_x:", len(boxes))
    boxes_grown = list()
    while boxes:
        ix0, ix1, iy0, iy1, iz0, iz1 = boxes.pop()
        while True: # grow into +x direction
            box_desired = (ix1+1, ix1+1, iy0, iy1, iz0, iz1,)
            try: boxes.remove(box_desired)
            except ValueError: break
            ix1 += 1
        while True: # grow into -x direction
            box_desired = (ix0 - 1, ix0 - 1, iy0, iy1, iz0, iz1,)
            try: boxes.remove(box_desired)
            except ValueError: break
            ix0 -= 1
        boxes_grown.append((ix0, ix1, iy0, iy1, iz0, iz1))
    return boxes_grown

def _grow_boxes_along_y(boxes) -> "[(ix0, ix1, iy0, iy1, iz0, iz1), ...]":
    """Grow boxes by merging neighbours along y axis."""
    print("BFDS: _grow_boxes_along_y:", len(boxes))
    boxes_grown = list()
    while boxes:
        ix0, ix1, iy0, iy1, iz0, iz1 = boxes.pop()
        while True: # grow into +y direction
            box_desired = (ix0, ix1, iy1+1, iy1+1, iz0, iz1)
            try: boxes.remove(box_desired)
            except ValueError: break
            iy1 += 1
        while True: # grow into -y direction
            box_desired = (ix0, ix1, iy0 - 1, iy0 - 1, iz0, iz1)
            try: boxes.remove(box_desired)
            except ValueError: break
            iy0 -= 1
        boxes_grown.append((ix0, ix1, iy0, iy1, iz0, iz1))
    return boxes_grown

def _grow_boxes_along_z(boxes) -> "[(ix0, ix1, iy0, iy1, iz0, iz1), ...]":
    """Grow boxes by merging neighbours along z axis."""
    print("BFDS: _grow_boxes_along_z:", len(boxes))
    boxes_grown = list()
    while boxes:
        ix0, ix1, iy0, iy1, iz0, iz1 = boxes.pop()
        while True: # grow into +z direction
            box_desired = (ix0, ix1, iy0, iy1, iz1+1, iz1+1)
            try: boxes.remove(box_desired)
            except ValueError: break
            iz1 += 1
        while True: # grow into -z direction
            box_desired = (ix0, ix1, iy0, iy1, iz0 - 1, iz0 - 1)
            try: boxes.remove(box_desired)
            except ValueError: break
            iz0 -= 1
        boxes_grown.append((ix0, ix1, iy0, iy1, iz0, iz1))
    return boxes_grown

# Trasform boxes in int coordinates to xbs in global coordinates

def _x_boxes_to_xbs(boxes, voxel_size, origin) -> "[(x0, x1, y0, y1, z0, z1), ...]":
    """Trasform boxes (int coordinates) to xbs (global coordinates)."""
    # Init
    print("BFDS: _x_boxes_to_xbs:", len(boxes))
    xbs = list()
    voxel_size_half = voxel_size / 2.
    # Build xbs
    while boxes:
        ix0, ix1, iy0, iy1, iz0, iz1 = boxes.pop()
        x0, y0, z0 = ( # origin + location + movement to lower left corner
            origin[0] + ix0 * voxel_size, # - 0., this is already at floor level
            origin[1] + iy0 * voxel_size - voxel_size_half,
            origin[2] + iz0 * voxel_size - voxel_size_half,
        )
        x1, y1, z1 = ( # origin + location + movement to upper right corner
            origin[0] + ix1 * voxel_size, # + 0., this is already at floor level
            origin[1] + iy1 * voxel_size + voxel_size_half,
            origin[2] + iz1 * voxel_size + voxel_size_half,
        )
        xbs.append([x0, x1, y0, y1, z0, z1],)
    return xbs

def _y_boxes_to_xbs(boxes, voxel_size, origin) -> "[(x0, x1, y0, y1, z0, z1), ...]":
    """Trasform boxes (int coordinates) to xbs (global coordinates)."""
    print("BFDS: _y_boxes_to_xbs:", len(boxes))
    # Init
    xbs = list()
    voxel_size_half = voxel_size / 2.
    # Build xbs
    while boxes:
        ix0, ix1, iy0, iy1, iz0, iz1 = boxes.pop()
        x0, y0, z0 = ( # origin + location + movement to lower left corner
            origin[0] + ix0 * voxel_size - voxel_size_half,
            origin[1] + iy0 * voxel_size, # - 0., this is already at floor level
            origin[2] + iz0 * voxel_size - voxel_size_half,
        )
        x1, y1, z1 = ( # origin + location + movement to upper right corner
            origin[0] + ix1 * voxel_size + voxel_size_half,
            origin[1] + iy1 * voxel_size, # + 0., this is already at floor level
            origin[2] + iz1 * voxel_size + voxel_size_half,
        )
        xbs.append([x0, x1, y0, y1, z0, z1],)
    return xbs

def _z_boxes_to_xbs(boxes, voxel_size, origin) -> "[(x0, x1, y0, y1, z0, z1), ...]":
    """Trasform boxes (int coordinates) to xbs (global coordinates)."""
    # Init
    print("BFDS: _z_boxes_to_xbs:", len(boxes))
    xbs = list()
    voxel_size_half = voxel_size / 2.
    # Build xbs
    while boxes:
        ix0, ix1, iy0, iy1, iz0, iz1 = boxes.pop()
        x0, y0, z0 = ( # origin + location + movement to lower left corner
            origin[0] + ix0 * voxel_size - voxel_size_half,
            origin[1] + iy0 * voxel_size - voxel_size_half,
            origin[2] + iz0 * voxel_size, # - 0., this is already at floor level
        )
        x1, y1, z1 = ( # origin + location + movement to upper right corner
            origin[0] + ix1 * voxel_size + voxel_size_half,
            origin[1] + iy1 * voxel_size + voxel_size_half,
            origin[2] + iz1 * voxel_size, # + 0., this is already at floor level
        )
        xbs.append([x0, x1, y0, y1, z0, z1],)
    return xbs

# Flatten xbs to obtain pixels

def _x_flatten_xbs(xbs, flat_origin) -> "[(l0, l0, y0, y1, z0, z1), ...]":
    """Flatten voxels to obtain pixels (normal to x axis) at flat_origin height."""
    print("BFDS: _x_flatten_xbs:", len(xbs))
    return [[flat_origin[0], flat_origin[0], xb[2], xb[3], xb[4], xb[5]] for xb in xbs]
        
def _y_flatten_xbs(xbs, flat_origin) -> "[(x0, x1, l0, l0, z0, z1), ...]":
    """Flatten voxels to obtain pixels (normal to x axis) at flat_origin height."""
    print("BFDS: _y_flatten_xbs:", len(xbs))
    return [[xb[0], xb[1], flat_origin[1], flat_origin[1], xb[4], xb[5]] for xb in xbs]

def _z_flatten_xbs(xbs, flat_origin) -> "[(x0, x1, y0, y1, l0, l0), ...]":
    """Flatten voxels to obtain pixels (normal to x axis) at flat_origin height."""
    print("BFDS: _z_flatten_xbs:", len(xbs))
    return [[xb[0], xb[1], xb[2], xb[3], flat_origin[2], flat_origin[2]] for xb in xbs]

