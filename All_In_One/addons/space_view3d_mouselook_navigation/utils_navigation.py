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

import bpy
import bmesh

from mathutils import Color, Vector, Matrix, Quaternion, Euler

import math

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_ui import calc_region_rect
from {0}dairin0d.utils_blender import BlUtil
""".format(dairin0d_location))

def calc_zbrush_border(area, region, scale=0.05, abs_min=16):
    clickable_region_size = calc_region_rect(area, region, overlap=False)[1]
    wrk_sz = min(clickable_region_size.x, clickable_region_size.y)
    return max(wrk_sz*scale, abs_min)

def calc_selection_center(context, non_obj_zero=False): # View3D area is assumed
    context_mode = context.mode
    active_object = context.active_object
    m = (active_object.matrix_world if active_object else None)
    positions = []
    
    is_object_mode = (context_mode == 'OBJECT') or (not active_object)
    
    if is_object_mode:
        m = None
        positions.extend(obj.matrix_world.translation for obj in context.selected_objects)
    elif context_mode == 'EDIT_MESH':
        bm = bmesh.from_edit_mesh(active_object.data)
        if bm.select_history and (len(bm.select_history) < len(bm.verts)/4):
            verts = set()
            for elem in bm.select_history:
                if isinstance(elem, bmesh.types.BMVert):
                    verts.add(elem)
                else:
                    verts.update(elem.verts)
            positions.extend(v.co for v in verts)
        else:
            positions.extend(v.co for v in bm.verts if v.select)
    elif context_mode in {'EDIT_CURVE', 'EDIT_SURFACE'}:
        for spline in active_object.data.splines:
            for point in spline.bezier_points:
                if point.select_control_point:
                    positions.append(point.co)
                else:
                    if point.select_left_handle:
                        positions.append(point.handle_left)
                    if point.select_right_handle:
                        positions.append(point.handle_right)
            positions.extend(point.co.to_3d() for point in spline.points if point.select)
    elif context_mode == 'EDIT_METABALL':
        active_elem = active_object.data.elements.active
        if active_elem:
            positions.append(active_elem.co)
        # Currently there is no API for element.select
        #positions.extend(elem.co for elem in active_object.data.elements if elem.select)
    elif context_mode == 'EDIT_LATTICE':
        # Not point.co! point.co returns very strange and often very big numbers
        positions.extend(point.co_deform for point in active_object.data.points if point.select)
    elif context_mode == 'EDIT_ARMATURE':
        for bone in active_object.data.edit_bones:
            if bone.select_head:
                positions.append(bone.head)
            if bone.select_tail:
                positions.append(bone.tail)
    elif context_mode == 'POSE':
        # consider only topmost parents
        bones = set(bone for bone in active_object.data.bones if bone.select)
        parents = set(bone for bone in bones if not bones.intersection(bone.parent_recursive))
        positions.extend(bone.matrix_local.translation for bone in parents)
    elif context_mode == 'EDIT_TEXT':
        # Blender considers only caret position as the selection center
        # But TextCurve has no API for text edit mode
        positions.append(Vector()) # use active object's position
    elif context_mode == 'PARTICLE':
        positions.append(Vector()) # use active object's position
    elif context_mode in {'SCULPT', 'PAINT_WEIGHT', 'PAINT_VERTEX', 'PAINT_TEXTURE'}:
        # last stroke position? (at least in sculpt mode, when Rotate Around Selection
        # is enabled, the view rotates around the average/center of last stroke)
        # This information is not available in Python, though
        positions.append(Vector()) # use active object's position
    
    if len(positions) == 0:
        if (not is_object_mode) and non_obj_zero:
            return m * Vector()
        return None
    
    n_positions = len(positions)
    if m is not None:
        positions = (m * p for p in positions)
    
    return sum(positions, Vector()) * (1.0 / n_positions)

# Virtual Trackball by Gavin Bell
# Ok, simulate a track-ball.  Project the points onto the virtual
# trackball, then figure out the axis of rotation, which is the cross
# product of P1 P2 and O P1 (O is the center of the ball, 0,0,0)
# Note:  This is a deformed trackball-- is a trackball in the center,
# but is deformed into a hyperbolic sheet of rotation away from the
# center.  This particular function was chosen after trying out
# several variations.
#
# It is assumed that the arguments to this routine are in the range
# (-1.0 ... 1.0)
def trackball(p1x, p1y, p2x, p2y, TRACKBALLSIZE=1.0):
    #"""
    #if (p1x == p2x) and (p1y == p2y):
    #    return Quaternion() # Zero rotation
    
    # First, figure out z-coordinates for projection of P1 and P2 to deformed sphere
    p1 = Vector((p1x, p1y, tb_project_to_sphere(TRACKBALLSIZE, p1x, p1y)))
    p2 = Vector((p2x, p2y, tb_project_to_sphere(TRACKBALLSIZE, p2x, p2y)))
    
    # Now, we want the cross product of P1 and P2
    a = p2.cross(p1) # vcross(p2,p1,a); # Axis of rotation
    
    # Figure out how much to rotate around that axis.
    d = p1 - p2
    t = d.magnitude / (2.0*TRACKBALLSIZE)
    
    # Avoid problems with out-of-control values...
    t = min(max(t, -1.0), 1.0)
    #phi = 2.0 * math.asin(t) # how much to rotate about axis
    phi = 2.0 * t # how much to rotate about axis
    
    return Quaternion(a, phi)

# Project an x,y pair onto a sphere of radius r OR a hyperbolic sheet
# if we are away from the center of the sphere.
def tb_project_to_sphere(r, x, y):
    d = math.sqrt(x*x + y*y)
    if (d < r * math.sqrt(0.5)): # Inside sphere
        z = math.sqrt(r*r - d*d)
    else: # On hyperbola
        t = r / math.sqrt(2)
        z = t*t / d
    return z

# Loosely based on "Improved Collision detection and Response" by Kasper Fauerby
# http://www.peroxide.dk/papers/collision/collision.pdf
def apply_collisions(scene, p_head, v, view_height, is_crouching, parallel, max_slides):
    head_h = 0.75 # relative to total height
    char_h = view_height / head_h
    char_r = char_h * 0.5
    if is_crouching:
        char_h *= 0.5
    
    p_base = p_head - Vector((0, 0, char_h*head_h))
    p_top = p_base + Vector((0, 0, char_h))
    p_center = (p_base + p_top) * 0.5
    
    e2w = Matrix.Identity(3)
    e2w.col[0] = (char_r, 0, 0)
    e2w.col[1] = (0, char_r, 0)
    e2w.col[2] = (0, 0, char_h*0.5)
    e2w.resize_4x4()
    
    subdivs=8
    max_cnt=16
    
    collided = False
    new_center = p_center
    
    v = v.copy()
    
    while max_slides >= 0:
        e2w.translation = new_center
        w2e = e2w.inverted()
        
        #ray_origin = (None if parallel else p_center)
        ray_origin = (head_h-0.5 if parallel else p_head)
        
        p0 = new_center
        d, p, c, n = ellipsoid_sweep(scene, e2w, w2e, v, ray_origin, subdivs, max_cnt)
        new_center = p
        
        if d is None: # didn't colliside with anything
            break
        
        """
        if (d < 1.0) and (not parallel):
            ce = w2e * c
            ne = -ce.normalized()
            pe = ce + ne
            p = e2w * pe
            new_center = p
            n = (e2w * Vector((ne.x, ne.y, ne.z, 0))).to_3d().normalized()
        """
        
        v = v - (p - p0) # subtract moved distance from velocity
        v = v + v.project(n) # project velocity to the sliding plane
        
        collided = True
        max_slides -= 1
    
    return new_center - p_center, collided

def ellipsoid_sweep(scene, e2w, w2e, v, ray_origin, subdivs=8, max_cnt=16):
    v = (w2e * Vector((v.x, v.y, v.z, 0))).to_3d()
    n = v.normalized()
    min_d = None
    d_n = None
    d_p = None
    d_c = None
    contacts_count = 0
    
    use_avg = False
    
    is_parallel = not isinstance(ray_origin, Vector)
    if is_parallel:
        max_cnt = 0 # sides aren't needed for parallel rays
    
    for p1 in ellipsoid_sweep_rays(e2w, v, subdivs, max_cnt):
        if is_parallel:
            p0 = w2e * p1
            p0 = p0 - p0.project(n) - (n * ray_origin)
            p0 = e2w * p0
        else:
            p0 = ray_origin.copy()
        
        raycast_result = BlUtil.Scene.line_cast(scene, p0, p1)
        success = raycast_result[0]
        location = raycast_result[1]
        normal = raycast_result[2]
        
        if success:
            rn = normal
            rn = (w2e * Vector((rn.x, rn.y, rn.z, 0))).to_3d()
            p = w2e * location
            L = p.dot(n)
            r = p - L*n
            h = math.sqrt(max(1.0 - r.length_squared, 0.0))
            if h > 0.1: # ignore almost tangential collisions
                d = L - h # distance of impact
                if not use_avg:
                    if (min_d is None) or (d < min_d):
                        min_d = d
                        d_p = n * min_d # stopping point
                        d_c = p # contact point
                        #d_n = (d_p - d_c) # contact normal
                        d_n = rn
                else:
                    if (min_d is None):
                        d_p = Vector()
                        d_c = Vector()
                        d_n = Vector()
                    min_d = d
                    d_p += n * min_d # stopping point
                    d_c += p # contact point
                    #d_n += (d_p - d_c) # contact normal
                    d_n = rn
                contacts_count += 1
    
    if min_d is None:
        return (None, e2w * v, None, None)
    
    if use_avg:
        d_p = d_p * (1.0 / contacts_count)
        d_c = d_c * (1.0 / contacts_count)
        d_n = d_n * (1.0 / contacts_count)
    
    d_p = e2w * d_p
    d_c = e2w * d_c
    d_n = (e2w * Vector((d_n.x, d_n.y, d_n.z, 0))).to_3d().normalized()
    return (min_d, d_p, d_c, d_n)

def ellipsoid_sweep_rays(e2w, v, subdivs=8, max_cnt=16):
    n = v.normalized()
    t1 = n.orthogonal()
    t2 = n.cross(t1)
    
    full_circle = 2*math.pi
    quarter_circle = 0.5*math.pi
    arc_step = full_circle / subdivs
    v_len = v.magnitude
    v_cnt = min(int(math.ceil(v_len / arc_step)), max_cnt)
    a_cnt = max(int(math.ceil(quarter_circle / arc_step)), 1)
    
    for i_v in range(v_cnt):
        c_n = (i_v / v_cnt) * v_len
        r_cnt = subdivs
        for i_r in range(r_cnt):
            angle = (i_r / r_cnt) * full_circle
            c_t1 = math.cos(angle)
            c_t2 = math.sin(angle)
            ray = c_n*n + c_t1*t1 + c_t2*t2
            yield (e2w * ray)
    
    for i_a in range(a_cnt+1):
        c_a = math.sin((i_a / a_cnt) * quarter_circle)
        r_t = math.sqrt(1 - c_a*c_a)
        c_n = v_len + c_a
        r_cnt = max(int(math.ceil((full_circle * r_t) / arc_step)), 1)
        for i_r in range(r_cnt):
            angle = (i_r / r_cnt) * full_circle
            c_t1 = math.cos(angle) * r_t
            c_t2 = math.sin(angle) * r_t
            ray = c_n*n + c_t1*t1 + c_t2*t2
            yield (e2w * ray)
