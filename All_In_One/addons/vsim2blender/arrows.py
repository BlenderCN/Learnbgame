import bpy
from math import pi, sin, cos, asin, acos, sqrt, atan2
import mathutils
import os
import time

def add_arrow(loc=[0,0,0], rot_euler=False, scale=1, mass=1):
    """Add an arrow to the scene

    :param loc: Origin of the arrow in *Cartesian coordinates*
    :type loc: 3-tuple or 3-list of floats
    :param rot_euler: Set of euler rotations (about x-, y- then z-axis) in radians. If False, arrow remains pointing along x-axis.
    :type rot_euler: 3-tuple/list or Boolean False
    :return: Arrow object
    :rtype: bpy object
    """
    # Check Blender version to account for API change
    if bpy.app.version[0] == 2 and bpy.app.version[1] < 70:
        bpy.ops.wm.link_append(directory=os.path.dirname(__file__)+'/arrow_cylinder.blend/Object/', filepath="arrow_cylinder.blend",  filename="Arrow", link=True)
    else:
        bpy.ops.wm.link(directory=os.path.dirname(__file__)+'/arrow_cylinder.blend/Object/', filepath="arrow_cylinder.blend",  filename="Arrow")
    arrow = bpy.data.objects['Arrow']
    arrow.location = loc
    if rot_euler:
        arrow.rotation_mode='XYZ'
        arrow.rotation_euler=rot_euler
    scale = scale * mass**-.5  # Inverse square root of mass gives a physical relative size of motions
    arrow.scale = [scale] * 3 # Scalar to 3 elements: scale uniformly
    arrow.name = 'Arrow.{0}'.format(time.time()) # This is a hack to give arrows unique names. There should be a better solution.
    return arrow

def _norm(*args):
    assert len(args) > 0
    sqargs = [x**2 for x in args]
    return sqrt(sum(sqargs))

def vector_to_euler(vector):
    """ Euler rotations to bring arrow along (1,0,0) to line up with vector
    
    :param vector: Input vector (i.e. a vector to align the arrow with by rotation)
    :type vector: 3-Vector of floats

    :returns: Euler rotations for Blender
    :rtype: 3-list of values in radians

    """
    if len(vector) != 3:
        raise Exception("Need 3 coordinates")
    a, b, c = (float(x) for x in vector)

    theta_y = atan2(-c, _norm(a,b))
    theta_z = atan2(b,a)

    return [0, theta_y, theta_z]
