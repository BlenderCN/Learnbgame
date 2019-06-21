#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

import mathutils
from mathutils import Color, Vector, Matrix, Quaternion, Euler

import math
import itertools

# Newton's binomial coefficients / Pascal's triangle coefficients / n choose k / nCk
# https://stackoverflow.com/questions/26560726/python-binomial-coefficient
# https://stackoverflow.com/questions/3025162/statistics-combinations-in-python
def binomial(n, k): # A fast way to calculate binomial coefficients by Andrew Dalke
    if not (0 <= k <= n): return 0
    ntok = 1
    ktok = 1
    for t in range(1, min(k, n - k) + 1):
        ntok *= n
        ktok *= t
        n -= 1
    return ntok // ktok

def lerp(v0, v1, t):
    return v0 * (1.0 - t) + v1 * t

def clamp(v, v_min, v_max):
    return (v_min if (v < v_min) else (v if v < v_max else v_max))
    #return min(max(v, v_min), v_max)

def round_step(x, s=1.0):
    #return math.floor(x * s + 0.5) / s
    return math.floor(x / s + 0.5) * s

def clamp_angle(ang, pi=math.pi):
    # Attention! In Python the behaviour is:
    # -359.0 % 180.0 == 1.0
    # -359.0 % -180.0 == -179.0
    twoPi = 2.0*pi
    ang = (ang % twoPi)
    return ((ang - twoPi) if (ang > pi) else ang)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! TODO: check if Blender has a correct implementation now !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def angle_axis_to_quat(angle, axis):
    w = math.cos(angle / 2.0)
    xyz = axis.normalized() * math.sin(angle / 2.0)
    return Quaternion((w, xyz.x, xyz.y, xyz.z))

def angle_signed(n, v0, v1, fallback=None):
    angle = v0.angle(v1, fallback)
    if (angle != fallback) and (angle > 0):
        angle *= math.copysign(1.0, v0.cross(v1).dot(n))
    return angle

def snap_pixel_vector(v, d=0.5): # to have 2d-stable 3d drawings
    return Vector((round(v.x)+d, round(v.y)+d))

def nautical_euler_from_axes(forward, right):
    x = Vector(right)
    y = Vector(forward)
    
    world_x = Vector((1, 0, 0))
    world_z = Vector((0, 0, 1))
    
    if abs(y.z) > (1 - 1e-12): # sufficiently close to vertical
        roll = 0.0
        xdir = x.copy()
    else:
        xdir = y.cross(world_z)
        rollPos = angle_signed(-y, x, xdir, 0.0)
        rollNeg = angle_signed(-y, x, -xdir, 0.0)
        if abs(rollNeg) < abs(rollPos):
            roll = rollNeg
            xdir = -xdir
        else:
            roll = rollPos
    xdir = Vector((xdir.x, xdir.y, 0)).normalized()
    
    yaw = angle_signed(-world_z, xdir, world_x, 0.0)
    
    zdir = xdir.cross(y).normalized()
    pitch = angle_signed(-xdir, zdir, world_z, 0.0)
    
    return Euler((pitch, roll, yaw), 'YXZ')

def nautical_euler_to_quaternion(ne):
    rot_x = Quaternion((1, 0, 0), ne[0])
    rot_y = Quaternion((0, 1, 0), ne[1])
    rot_z = Quaternion((0, 0, 1), ne[2])
    return rot_z * rot_x * rot_y

def dist_to_segment(p, a, b):
    l2 = (b - a).length_squared
    if l2 == 0.0: return (p - a).magnitude
    t = min(max((p - a).dot(b - a) / l2, 0.0), 1.0)
    return (a.lerp(b, t) - p).magnitude

def line_line_t(line, line1, fallback=None, normalized=True, clip0=None, clip1=None):
    v00, v01 = line
    res = mathutils.geometry.intersect_line_line(v00, v01, line1[0], line1[1])
    if not res: return fallback
    delta = v01 - v00
    mag2 = delta.length_squared
    delta *= 1.0/mag2
    t = (res[0] - v00).dot(delta) # res is tuple of vectors
    if clip0 is not None: t = max(t, clip0)
    if clip1 is not None: t = min(t, clip1)
    if not normalized: t *= math.sqrt(mag2)
    return t

def line_plane_t(line, plane, fallback=None, normalized=True, clip0=None, clip1=None):
    v00, v01 = line
    res = mathutils.geometry.intersect_line_plane(v00, v01, plane[0], plane[1])
    if not res: return fallback
    delta = v01 - v00
    mag2 = delta.length_squared
    delta *= 1.0/mag2
    t = (res - v00).dot(delta) # res is vector
    if clip0 is not None: t = max(t, clip0)
    if clip1 is not None: t = min(t, clip1)
    if not normalized: t *= math.sqrt(mag2)
    return t

def line_sphere_t(line, sphere, fallback=None, normalized=True, clip0=None, clip1=None):
    v00, v01 = line
    res = mathutils.geometry.intersect_line_sphere(v00, v01, sphere[0], sphere[1], False)
    if not res: return fallback
    pA, pB = res
    if (not pA) or (not pB): return fallback
    delta = v01 - v00
    mag2 = delta.length_squared
    delta *= 1.0/mag2
    tA = (pA - v00).dot(delta)
    tB = (pB - v00).dot(delta)
    if clip0 is not None:
        tA = max(tA, clip0)
        tB = max(tB, clip0)
    if clip1 is not None:
        tA = min(tA, clip1)
        tB = min(tB, clip1)
    if not normalized:
        tA *= math.sqrt(mag2)
        tB *= math.sqrt(mag2)
    return (tA, tB)

def clip_primitive(primitive, plane): # expected to be a list of vertices
    primitive_size = len(primitive)
    if primitive_size == 0:
        return primitive
    elif primitive_size == 1:
        dist = mathutils.geometry.distance_point_to_plane(primitive[0], plane[0], plane[1])
        return ([] if dist < 0 else primitive)
    elif primitive_size == 2:
        dist0 = mathutils.geometry.distance_point_to_plane(primitive[0], plane[0], plane[1])
        dist1 = mathutils.geometry.distance_point_to_plane(primitive[1], plane[0], plane[1])
        if (dist0 >= 0) and (dist1 >= 0): return primitive
        if (dist0 < 0) and (dist1 < 0): return []
        t = line_plane_t(primitive, plane, clip0=0.0, clip1=1.0)
        if t is None: return primitive
        delta = primitive[1] - primitive[0]
        if dist1 < dist0: return [primitive[0], primitive[0] + delta * t]
        return [primitive[0] + delta * t, primitive[1]]
    else: # should be convex and planar?
        res = []
        for i in range(primitive_size):
            v0 = primitive[i]
            v1 = primitive[(i+1) % primitive_size]
            segment = clip_primitive([v0, v1], plane)
            if not segment: continue
            if (len(res) == 0) or (res[-1] != segment[0]): res.append(segment[0])
            if (i < primitive_size-1): res.append(segment[1])
        return res

def transform_point_normal(m, t, n, as_plane=True):
    if as_plane:
        x, y, z = orthogonal_XYZ(None, None, n)
        x, y, z, t = transform_plane(m, x, y, z, t)
        return (t, z)
    else:
        t = m * t
        n = (m.to_3x3() * n).normalized()
        return (t, n)

def transform_plane(m, x, y, z, t):
    if (x is None) or (y is None): x, y, z = orthogonal_XYZ(x, y, z, "z")
    
    p0 = Vector(t)
    px = p0 + Vector(x)
    py = p0 + Vector(y)
    pz = p0 + Vector(z)
    
    p0 = m * p0
    px = m * px
    py = m * py
    pz = m * pz
    
    t = p0
    y = (py - p0).normalized()
    z = (px - p0).cross(y).normalized()
    x = y.cross(z)
    
    return (x, y, z, t)

def _orthogonal_rest(x, y, z, ort_XY):
    _y = (Vector() if z is None else z.cross(x).normalized())
    _z = (Vector() if y is None else x.cross(y).normalized())
    if _y.length_squared > 0.5:
        y = _y
        z = x.cross(_y).normalized()
    elif _z.length_squared > 0.5:
        z = _z
        y = _z.cross(x).normalized()
    else:
        y = orthogonal(x, ort_XY).normalized()
        z = x.cross(y).normalized()
    return y, z

def orthogonal_XYZ(x, y, z, main_axis=None, ort_XY=True):
    if main_axis == "x":
        # y = z.cross(x)
        # z = x.cross(y)
        y, z = _orthogonal_rest(x, y, z, ort_XY)
    elif main_axis == "y":
        # z = x.cross(y)
        # x = y.cross(z)
        z, x = _orthogonal_rest(y, z, x, ort_XY)
    elif main_axis == "z":
        # x = y.cross(z)
        # y = z.cross(x)
        x, y = _orthogonal_rest(z, x, y, ort_XY)
    else:
        n_missing = int(x is None) + int(y is None) + int(z is None)
        
        if n_missing == 2:
            if x is not None:
                y = (orthogonal_in_XY(x) if ort_XY else orthogonal(x))
            elif y is not None:
                z = (orthogonal_in_XY(y) if ort_XY else orthogonal(y))
            elif z is not None:
                x = (orthogonal_in_XY(z) if ort_XY else orthogonal(z))
        
        if x is None:
            x = y.cross(z)
            if main_axis:
                if main_axis == "y": z = x.cross(y)
                elif main_axis == "z": y = z.cross(x)
        elif y is None:
            y = z.cross(x)
            if main_axis:
                if main_axis == "x": z = x.cross(y)
                elif main_axis == "z": x = y.cross(z)
        elif z is None:
            z = x.cross(y)
            if main_axis:
                if main_axis == "x": y = z.cross(x)
                elif main_axis == "y": x = y.cross(z)
    
    return x, y, z

def orthogonal(v, in_XY=False): # Vector.orthogonal isn't present in 2.70
    size = len(v)
    if size == 2: return Vector((-v[1], v[0]))
    if in_XY: return orthogonal_in_XY(v)
    if v.length_squared < 1e-8: return Vector.Fill(size)
    v = (Vector((v[0], v[1], 0.0)) if size == 2 else Vector(v))
    ort = Vector((0,0,1)).cross(v).normalized()
    if ort.length_squared < 0.5: ort = Vector((0,1,0)).cross(v).normalized()
    return (ort.to_2d() if size == 2 else ort)

def orthogonal_in_XY(v):
    v = v.normalized()
    return (Vector((0,0,1)).cross(v) if (1.0 - abs(v.z)) > 1e-6 else Vector((1,0,0)))

def matrix_flatten(m):
    return tuple(itertools.chain(*m.col))

def matrix_unflatten(array):
    size = len(array)
    if size == 16:
        m = Matrix.Identity(4)
        m.col[0] = array[0:4]
        m.col[1] = array[4:8]
        m.col[2] = array[8:12]
        m.col[3] = array[12:16]
    elif size == 9:
        m = Matrix.Identity(3)
        m.col[0] = array[0:3]
        m.col[1] = array[3:6]
        m.col[2] = array[6:9]
    elif size == 4:
        m = Matrix.Identity(2)
        m.col[0] = array[0:2]
        m.col[1] = array[2:4]
    return m

def matrix_LRS(L, R, S):
    m = R.to_matrix()
    m.col[0] *= S[0]
    m.col[1] *= S[1]
    m.col[2] *= S[2]
    m.resize_4x4()
    m.translation = L
    return m

def to_matrix4x4(orient, pos):
    if not isinstance(orient, Matrix):
        orient = orient.to_matrix()
    m = orient.to_4x4()
    m.translation = pos.to_3d()
    return m

def matrix_compose(*args):
    size = len(args)
    m = Matrix.Identity(size)
    axes = m.col
    
    if size == 2:
        for i in (0, 1):
            c = args[i]
            if isinstance(c, Vector):
                axes[i] = c.to_2d()
            elif hasattr(c, "__iter__"):
                axes[i] = Vector(c).to_2d()
            else:
                axes[i][i] = c
    else:
        for i in (0, 1, 2):
            c = args[i]
            if isinstance(c, Vector):
                axes[i][:3] = c.to_3d()
            elif hasattr(c, "__iter__"):
                axes[i][:3] = Vector(c).to_3d()
            else:
                axes[i][i] = c
        
        if size == 4:
            c = args[3]
            if isinstance(c, Vector):
                m.translation = c.to_3d()
            elif hasattr(c, "__iter__"):
                m.translation = Vector(c).to_3d()
    
    return m

def matrix_decompose(m, res_size=None):
    size = len(m)
    axes = m.col # m.row
    if res_size is None: res_size = size
    
    if res_size == 2: return (axes[0].to_2d(), axes[1].to_2d())
    
    x = axes[0].to_3d()
    y = axes[1].to_3d()
    z = (axes[2].to_3d() if size > 2 else Vector())
    if res_size == 3: return (x, y, z)
    
    t = (m.translation.to_3d() if size == 4 else Vector())
    if res_size == 4: return (x, y, z, t)

# for compatibility with 2.70
def matrix_invert_safe(m):
    try:
        m.invert()
        return
    except ValueError:
        pass
    m.col[0][0] += 1e-6
    m.col[1][1] += 1e-6
    m.col[2][2] += 1e-6
    m.col[3][3] += 1e-6
    try:
        m.invert()
    except ValueError:
        pass
def matrix_inverted_safe(m):
    try:
        return m.inverted()
    except ValueError:
        pass
    m = Matrix()
    m.col[0][0] += 1e-6
    m.col[1][1] += 1e-6
    m.col[2][2] += 1e-6
    m.col[3][3] += 1e-6
    try:
        return m.inverted()
    except ValueError:
        return Matrix()
