'''
File created by Micah Stewart for Impulse Dental Technologies @ 2018
Collection of functions written by:
    Patrick Moore,
    Thomas Beck,
    Micah Stewart

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import bpy

from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
from mathutils import Vector
from .blender import bversion

def get_view_ray_data(context, coord):
    ''' get data to use in ray casting '''
    view_vector = region_2d_to_vector_3d(context.region, context.region_data, coord)
    ray_origin = region_2d_to_origin_3d(context.region, context.region_data, coord)
    ray_target = ray_origin + (view_vector * 1000)
    return [view_vector, ray_origin, ray_target]

def ray_cast(ob, imx, ray_origin, ray_target, also_do_this):
    '''
    cast ray from to view to specified target on object. 
    '''
    if bversion() < '002.077.000':
        loc, no, face_ind = ob.ray_cast(imx * ray_origin, imx * ray_target)
        if face_ind == -1:
            if also_do_this:
                also_do_this()
                return [None, None, None]
            else:
                pass
    else:
        res, loc, no, face_ind = ob.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)
        if not res:
            if also_do_this:
                also_do_this()
                return [None, None, None]
            else:
                pass

    return [loc, no, face_ind]

def ray_cast_bvh(bvh, imx, ray_origin, ray_target, also_do_this=None):
    '''
    cast ray from to view to specified target on object.
    '''
    if bversion() < '002.077.000':
        print('NO GOING BACK TO 2.77')
        return None, None, None
    else:
        loc, no, face_ind, d = bvh.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)
        if loc == None:
            if also_do_this:
                also_do_this()
                return [None, None, None]
            else:
                pass

    return [loc, no, face_ind]

def ray_cast_region2d(region, rv3d, screen_coord, ob, settings):
    '''
    performs ray casting on object given region, rv3d, and coords wrt region.
    returns tuple of ray vector (from coords of region) and hit info
    '''
    mx = ob.matrix_world
    imx = mx.inverted()
    
    ray_vector = region_2d_to_vector_3d(region, rv3d, screen_coord).normalized()
    ray_origin = region_2d_to_origin_3d(region, rv3d, screen_coord)
    
    if rv3d.is_perspective:
        #ray_target = ray_origin + ray_vector * 100
        r1 = get_ray_origin(ray_origin, -ray_vector, ob)
        ray_target = r1
    else:
        # need to back up the ray's origin, because ortho projection has front and back
        # projection planes at inf
        r0 = get_ray_origin(ray_origin,  ray_vector, ob)
        r1 = get_ray_origin(ray_origin, -ray_vector, ob)
        #dprint(str(r0) + '->' + str(r1), l=4)
        ray_origin = r0
        ray_target = r1
    
    #TODO: make a max ray depth or pull this depth from clip depth
    
    ray_start_local  = imx * ray_origin
    ray_target_local = imx * ray_target
    
    if settings.debug > 3:
        print('ray_persp  = ' + str(rv3d.is_perspective))
        print('ray_origin = ' + str(ray_origin))
        print('ray_target = ' + str(ray_target))
        print('ray_vector = ' + str(ray_vector))
        print('ray_diff   = ' + str((ray_target - ray_origin).normalized()))
        print('start:  ' + str(ray_start_local))
        print('target: ' + str(ray_target_local))
    
    if bversion() >= '002.077.000':
        hit = ob.ray_cast(ray_start_local, (ray_target_local - ray_start_local))
        
    else:
        hit = ob.ray_cast(ray_start_local, ray_target_local)
    return (ray_vector, hit)

def ray_cast_path(context, ob, screen_coords):
    rgn  = context.region
    rv3d = context.space_data.region_3d
    mx   = ob.matrix_world
    imx  = mx.inverted()
    
    r2d_origin = region_2d_to_origin_3d
    r2d_vector = region_2d_to_vector_3d
    
    rays = [(r2d_origin(rgn, rv3d, co),r2d_vector(rgn, rv3d, co).normalized()) for co in screen_coords]
    
    if rv3d.is_perspective:
        rays = [(ray_o, get_ray_origin(ray_o, -ray_v, ob)) for ray_o,ray_v in rays]
    else:
        rays = [(get_ray_origin(ray_o, ray_v, ob),get_ray_origin(ray_o, -ray_v, ob)) for ray_o,ray_v in rays]
    
    

    if bversion() < '002.077.00':
        hits = [ob.ray_cast(imx * ray_o, imx * ray_v) for ray_o,ray_v in rays]
    else:
        hits = [ob.ray_cast(imx * ray_o, imx * ray_v - imx * ray_o) for ray_o,ray_v in rays]
        
        
    if bversion() <= '002.076.000':
        world_coords = [mx*co for co,no,face in hits if face != -1]
    else:
        world_coords = [mx*co for ok,co,no,face in hits if ok]

    return world_coords

def ray_cast_stroke(context, ob, stroke):
    '''
    strokes have form [((x,y),p)] with a pressure or radius value
    
    returns list [Vector(x,y,z), p] leaving the pressure/radius value untouched
    does drop any values that do not successfully ray_cast
    '''
    rgn  = context.region
    rv3d = context.space_data.region_3d
    mx   = ob.matrix_world
    imx  = mx.inverted()
    
    r2d_origin = region_2d_to_origin_3d
    r2d_vector = region_2d_to_vector_3d
    
    rays = [(r2d_origin(rgn, rv3d, co),r2d_vector(rgn, rv3d, co).normalized()) for co,_ in stroke]
    
    back = 0 if rv3d.is_perspective else 1
    mult = 100 #* (1 if rv3d.is_perspective else -1)
    bver = '%03d.%03d.%03d' % (bpy.app.version[0],bpy.app.version[1],bpy.app.version[2])
    if (bver < '002.072.000') and not rv3d.is_perspective: mult *= -1
    
    sten = [(imx*(o-d*back*mult), imx*(o+d*mult)) for o,d in rays]
    
    if bver < '002.077.00':
        hits = [ob.ray_cast(st,st+(en-st)*1000) for st,en in sten]
    else:
        hits = [ob.ray_cast(st,(en-st)) for st,en in sten]
    
    
    world_stroke = [(mx*hit[0],stroke[i][1])  for i,hit in enumerate(hits) if hit[2] != -1]
    
    return world_stroke

def ray_cast_visible(verts, ob, rv3d):
    '''
    returns list of Boolean values indicating whether the corresponding vert
    is visible (not occluded by object) in region associated with rv3d
    '''
    view_dir = (rv3d.view_rotation * Vector((0,0,1))).normalized()
    imx = ob.matrix_world.inverted()
    
    if rv3d.is_perspective:
        eyeloc = rv3d.view_location + rv3d.view_distance*view_dir
        #eyeloc = Vector(rv3d.view_matrix.inverted().col[3][:3]) #this is brilliant, thanks Gert
        eyeloc_local = imx*eyeloc
        source = [eyeloc_local for vert in verts]
        target = [imx*(vert+0.01*view_dir) for vert in verts]
    else:
        source = [imx*(vert+100*view_dir) for vert in verts]
        target = [imx*(vert+0.01*view_dir) for vert in verts]
    
    if bversion() < '002.077.00':
        return [ob.ray_cast(s,t)[2]==-1 for s,t in zip(source,target)]
    else:
        return [ob.ray_cast(s,t-s)[3]==-1 for s,t in zip(source,target)]

def get_ray_origin_target(region, rv3d, screen_coord, ob):
    ray_vector = region_2d_to_vector_3d(region, rv3d, screen_coord).normalized()
    ray_origin = region_2d_to_origin_3d(region, rv3d, screen_coord)
    if not rv3d.is_perspective:
        # need to back up the ray's origin, because ortho projection has front and back
        # projection planes at inf
        
        bver = '%03d.%03d.%03d' % (bpy.app.version[0],bpy.app.version[1],bpy.app.version[2])
        # why does this need to be negated?
        # but not when ortho front/back view??
        if bver < '002.073.000' and abs(ray_vector.y)<1: ray_vector = -ray_vector
        
        r0 = get_ray_origin(ray_origin, ray_vector, ob)
        r1 = get_ray_origin(ray_origin, -ray_vector, ob)
        ray_origin = r0
        ray_target = r1
    else:
        ray_target = get_ray_origin(ray_origin, -ray_vector, ob)
    
    return (ray_origin, ray_target)

def ray_cast_world_size(region, rv3d, screen_coord, screen_size, ob, settings):
    mx  = ob.matrix_world
    imx = mx.inverted()
    
    ray_origin,ray_target = get_ray_origin_target(region, rv3d, screen_coord, ob)
    ray_direction         = (ray_target - ray_origin).normalized()
    
    ray_start_local  = imx * ray_origin
    ray_target_local = imx * ray_target
    
    if bversion() < '002.077.000':
        pt_local,no,idx  = ob.ray_cast(ray_start_local, ray_target_local)
    else:
        ok, loc, no, idx = ob.ray_cast(ray_start_local, ray_target_local - ray_start_local)
    
    if idx == -1: return float('inf')
    
    pt = mx * pt_local
    
    screen_coord_offset = (screen_coord[0]+screen_size, screen_coord[1])
    ray_origin_offset,ray_target_offset = get_ray_origin_target(region, rv3d, screen_coord_offset, ob)
    ray_direction_offset = (ray_target_offset - ray_origin_offset).normalized()
    
    d = get_ray_plane_intersection(ray_origin_offset, ray_direction_offset, pt, (rv3d.view_rotation*Vector((0,0,-1))).normalized() )
    pt_offset = ray_origin_offset + ray_direction_offset * d
    
    return (pt-pt_offset).length

def get_ray_plane_intersection(ray_origin, ray_direction, plane_point, plane_normal):
    d = ray_direction.dot(plane_normal)
    if abs(ray_direction.dot(plane_normal)) <= 0.00000001: return float('inf')
    return (plane_point-ray_origin).dot(plane_normal) / d

def get_ray_origin(ray_origin, ray_direction, ob):
    mx = ob.matrix_world
    q  = ob.rotation_quaternion
    bbox = [Vector(v) for v in ob.bound_box]
    bm = Vector((min(v.x for v in bbox),min(v.y for v in bbox),min(v.z for v in bbox)))
    bM = Vector((max(v.x for v in bbox),max(v.y for v in bbox),max(v.z for v in bbox)))
    x,y,z = Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))
    planes = []
    if abs(ray_direction.x)>0.0001: planes += [(bm,x), (bM,-x)]
    if abs(ray_direction.y)>0.0001: planes += [(bm,y), (bM,-y)]
    if abs(ray_direction.z)>0.0001: planes += [(bm,z), (bM,-z)]
    dists = [get_ray_plane_intersection(ray_origin,ray_direction,mx*p0,q*no) for p0,no in planes]

    return ray_origin + ray_direction * min(dists)

