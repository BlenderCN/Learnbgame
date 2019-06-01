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
import bgl
import bmesh

from mathutils import Color, Vector, Matrix, Quaternion, Euler

import mathutils

from bpy_extras.view3d_utils import (
    region_2d_to_location_3d,
    location_3d_to_region_2d,
    region_2d_to_vector_3d,
    region_2d_to_origin_3d,
)

import math
import time

from .bpy_inspect import BlEnums
from .utils_math import matrix_LRS, matrix_compose, angle_signed, snap_pixel_vector, lerp, nautical_euler_from_axes, nautical_euler_to_quaternion, orthogonal_in_XY, transform_point_normal, transform_plane, matrix_inverted_safe, line_line_t, line_plane_t, line_sphere_t, clip_primitive, dist_to_segment
from .utils_ui import calc_region_rect, convert_ui_coord, ui_context_under_coord, rv3d_from_region, ui_hierarchy
from .utils_gl import cgl
from .utils_blender import Selection, SelectionSnapshot, ToggleObjectMode, BlUtil

class SmartView3D:
    def __new__(cls, context=None, **kwargs):
        if context is None:
            context = bpy.context
        elif isinstance(context, (Vector, tuple)):
            context_override = ui_context_under_coord(context[0], context[1], (context[2] if len(context) > 2 else 1))
            if not context_override: return None
            context_override.update(kwargs)
            kwargs = context_override
            context = bpy.context
        
        region = kwargs.get("region")
        if region:
            if (region.type != 'WINDOW'): return None
            
            area = kwargs.get("area")
            window = kwargs.get("window")
            if not (area and window): window, area, region = ui_hierarchy(region)
            if (area.type != 'VIEW_3D'): return None
            
            region_data = kwargs.get("region_data") or rv3d_from_region(area, region)
            if not region_data: return None
            
            space_data = kwargs.get("space_data") or area.spaces.active
        else:
            region = getattr(context, "region", None)
            if (not region) or (region.type != 'WINDOW'): return None
            
            area = getattr(context, "area", None)
            window = getattr(context, "window", None)
            if not (area and window): window, area, region = ui_hierarchy(region)
            if (area.type != 'VIEW_3D'): return None
            
            region_data = getattr(context, "region_data", None) or rv3d_from_region(area, region)
            if not region_data: return None
            
            space_data = getattr(context, "space_data", None) or area.spaces.active
        
        self = object.__new__(cls)
        self.userprefs = bpy.context.user_preferences
        self.window = window
        self.area = area
        self.region = region
        self.space_data = space_data
        self.region_data = region_data
        self.use_camera_axes = kwargs.get("use_camera_axes", False)
        self.use_viewpoint =  kwargs.get("use_viewpoint", False)
        self.bypass_camera_lock = kwargs.get("bypass_camera_lock", False)
        
        return self
    
    @staticmethod
    def find_in_ui(ui_obj):
        if isinstance(ui_obj, bpy.types.Window):
            window = ui_obj
            for area in window.screen.areas:
                if area.type != 'VIEW_3D': continue
                space_data = area.spaces.active
                if space_data.type != 'VIEW_3D': continue
                for region in area.regions:
                    if region.type != 'WINDOW': continue
                    region_data = rv3d_from_region(area, region)
                    sv = SmartView3D(window=window, area=area, space_data=space_data, region=region, region_data=region_data)
                    if sv: yield sv
        elif isinstance(ui_obj, bpy.types.Area):
            if ui_obj.type != 'VIEW_3D': return
            wm = bpy.context.window_manager
            for window in wm.windows:
                for area in window.screen.areas:
                    if area != ui_obj: continue
                    space_data = area.spaces.active
                    if space_data.type != 'VIEW_3D': continue
                    for region in area.regions:
                        if region.type != 'WINDOW': continue
                        region_data = rv3d_from_region(area, region)
                        sv = SmartView3D(window=window, area=area, space_data=space_data, region=region, region_data=region_data)
                        if sv: yield sv
        elif isinstance(ui_obj, bpy.types.Region):
            sv = SmartView3D(region=ui_obj)
            if sv: yield sv
        elif ui_obj is None:
            wm = bpy.context.window_manager
            for window in wm.windows:
                for area in window.screen.areas:
                    if area.type != 'VIEW_3D': continue
                    space_data = area.spaces.active
                    if space_data.type != 'VIEW_3D': continue
                    for region in area.regions:
                        if region.type != 'WINDOW': continue
                        region_data = rv3d_from_region(area, region)
                        sv = SmartView3D(window=window, area=area, space_data=space_data, region=region, region_data=region_data)
                        if sv: yield sv
    
    def __bool__(self):
        return bool(self.area.regions and (self.area.type == 'VIEW_3D'))
    
    screen = property(lambda self: self.window.screen)
    scene = property(lambda self: self.window.screen.scene)
    
    @property
    def context_dict(self):
        scene = self.scene
        active_object = scene.objects.active
        mode = BlEnums.mode_from_object(active_object)
        obj_mode = (active_object.mode if active_object else 'OBJECT')
        obj_name = (active_object.name if active_object else "")
        
        return dict(
            window=self.window,
            screen=self.window.screen,
            area=self.area,
            region=self.region,
            space_data=self.space_data,
            region_data=self.region_data,
            
            mode=mode,
            scene=scene,
            active_base=scene.object_bases.get(obj_name),
            active_object=active_object,
            object=active_object,
            edit_object=(active_object if obj_mode == 'EDIT' else None),
            sculpt_object=(active_object if obj_mode == 'SCULPT' else None),
            vertex_paint_object=(active_object if obj_mode == 'VERTEX_PAINT' else None),
            weight_paint_object=(active_object if obj_mode == 'WEIGHT_PAINT' else None),
            image_paint_object=(active_object if obj_mode == 'TEXTURE_PAINT' else None),
            particle_edit_object=(active_object if obj_mode == 'PARTICLE_EDIT' else None),
            tool_settings=scene.tool_settings,
            blend_data=bpy.data,
        )
    
    @property
    def visible_objects(self):
        scene = self.scene
        if self.space_data.local_view:
            v3d = self.space_data # local-view layers are kept here
            for base in scene.object_bases:
                if not BlUtil.Object.layers_intersect(base, v3d, "layers_local_view"): continue
                obj = base.object
                if not obj.hide: yield obj
        else:
            for obj in scene.objects:
                if obj.is_visible(scene): yield obj
    
    def __get(self):
        return self.space_data.lock_cursor
    def __set(self, value):
        self.space_data.lock_cursor = value
    lock_cursor = property(__get, __set)
    
    def __get(self):
        return self.space_data.lock_object
    def __set(self, value):
        self.space_data.lock_object = value
    lock_object = property(__get, __set)
    
    def __get(self):
        return self.space_data.lock_bone
    def __set(self, value):
        self.space_data.lock_bone = value
    lock_bone_name = property(__get, __set)
    
    def __get(self):
        v3d = self.space_data
        obj = v3d.lock_object
        if obj and (obj.type == 'ARMATURE') and v3d.lock_bone:
            try:
                if obj.mode == 'EDIT':
                    return obj.data.edit_bones[v3d.lock_bone]
                else:
                    return obj.data.bones[v3d.lock_bone]
            except:
                pass
        return None
    def __set(self, value):
        self.space_data.lock_bone = (value.name if value else "")
    lock_bone = property(__get, __set)
    
    def __get(self):
        return self.space_data.lock_camera or self.bypass_camera_lock
    def __set(self, value):
        self.space_data.lock_camera = value
    lock_camera = property(__get, __set)
    
    def __get(self):
        return self.userprefs.view.use_camera_lock_parent
    def __set(self, value):
        self.userprefs.view.use_camera_lock_parent = value
    lock_camera_parent = property(__get, __set)
    
    def __get(self):
        return self.space_data.region_3d
    region_3d = property(__get)
    
    def __get(self):
        return self.region_data == self.space_data.region_3d
    is_region_3d = property(__get)
    
    # 0: bottom left (Front Ortho)
    # 1: top left (Top Ortho)
    # 2: bottom right (Right Ortho)
    # 3: top right (User Persp)
    def __get(self):
        return getattr(self.space_data, "region_quadviews")
    quadviews = property(__get)
    
    def __get(self):
        return bool(self.quadviews)
    quadview_enabled = property(__get)
    
    def __get(self):
        return self.region_data.lock_rotation
    def __set(self, value):
        self.region_data.lock_rotation = value
    quadview_lock = property(__get, __set)
    
    def __get(self):
        return self.region_data.show_sync_view
    def __set(self, value):
        self.region_data.show_sync_view = value
    quadview_sync = property(__get, __set)
    
    def __get(self):
        return Vector(self.region_data.view_camera_offset)
    def __set(self, value):
        self.region_data.view_camera_offset = value
    camera_offset = property(__get, __set)
    
    def __get(self):
        value = self.camera_offset
        value = Vector((value.x * self.region.width, value.y * self.region.height))
        return value * self.camera_zoom_scale
    def __set(self, value):
        value = value * (1.0 / self.camera_zoom_scale)
        value = Vector((value.x / self.region.width, value.y / self.region.height))
        self.camera_offset = value
    camera_offset_pixels = property(__get, __set)
    
    def __get(self):
        return self.region_data.view_camera_zoom
    def __set(self, value):
        self.region_data.view_camera_zoom = value
    camera_zoom = property(__get, __set)
    
    # See source\blender\blenkernel\intern\screen.c
    def __get(self):
        # BKE_screen_view3d_zoom_to_fac magic formula
        value = math.pow(math.sqrt(2.0) + self.camera_zoom / 50.0, 2.0) / 4.0
        return value * 2 # using Blender's formula, at 0 the result is 0.5
    def __set(self, value):
        value *= 0.5
        # BKE_screen_view3d_zoom_from_fac magic formula
        self.camera_zoom = (math.sqrt(4.0 * value) - math.sqrt(2.0)) * 50.0
    camera_zoom_scale = property(__get, __set)
    
    def __get(self):
        return self.space_data.camera
    def __set(self, value):
        self.space_data.camera = value
    camera = property(__get, __set)
    
    def __get(self):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            return self.camera.data.lens
        else:
            return self.space_data.lens
    def __set(self, value):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            if self.lock_camera:
                self.camera.data.lens = value
        else:
            self.space_data.lens = value
    lens = property(__get, __set)
    
    def __get(self):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            return self.camera.data.clip_start
        else:
            return self.space_data.clip_start
    def __set(self, value):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            if self.lock_camera:
                self.camera.data.clip_start = value
        else:
            self.space_data.clip_start = value
    clip_start = property(__get, __set)
    
    def __get(self):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            return self.camera.data.clip_end
        else:
            return self.space_data.clip_end
    def __set(self, value):
        if self.is_camera and (self.camera.type == 'CAMERA'):
            if self.lock_camera:
                self.camera.data.clip_end = value
        else:
            self.space_data.clip_end = value
    clip_end = property(__get, __set)
    
    def __get(self):
        return ((self.region_data.view_perspective == 'CAMERA') and bool(self.space_data.camera))
    def __set(self, value):
        if value and self.space_data.camera:
            self.region_data.view_perspective = 'CAMERA'
        elif self.region_data.is_perspective:
            self.region_data.view_perspective = 'PERSP'
        else:
            self.region_data.view_perspective = 'ORTHO'
    is_camera = property(__get, __set)
    
    def __get(self):
        return self.lock_camera or not self.is_camera
    can_move = property(__get)
    
    def __get(self):
        if self.is_camera:
            if (self.camera.type == 'CAMERA'):
                return self.camera.data.type != 'ORTHO'
            else:
                return True
        else:
            return self.region_data.is_perspective
    def __set(self, value):
        if self.is_camera:
            if self.lock_camera:
                if (self.camera.type == 'CAMERA'):
                    cam_data = self.camera.data
                    old_value = (cam_data.type != 'ORTHO')
                    if value != old_value:
                        if cam_data.type == 'ORTHO':
                            cam_data.type = 'PERSP'
                        else:
                            cam_data.type = 'ORTHO'
        elif self.is_region_3d or not self.quadview_lock:
            self.region_data.is_perspective = value
            if value:
                self.region_data.view_perspective = 'PERSP'
            else:
                self.region_data.view_perspective = 'ORTHO'
    is_perspective = property(__get, __set)
    
    def __get(self):
        region_center = Vector((self.region.width, self.region.height)) * 0.5
        if self.is_camera and (not self.is_perspective):
            return region_center # Somewhy Blender behaves like this
        return region_center - self.camera_offset_pixels
    focus_projected = property(__get)
    
    def __get(self):
        rv3d = self.region_data
        if rv3d.is_perspective or (rv3d.view_perspective == 'CAMERA'):
            return (self.clip_start, self.clip_end, self.viewpoint)
        return (-self.clip_end*0.5, self.clip_end*0.5, self.focus)
    zbuf_range = property(__get)
    
    def __get(self):
        return self.region_data.view_distance
    def __set(self, value):
        if self.quadview_sync and (not self.is_region_3d):
            quadviews = self.quadviews
            quadviews[0].view_distance = value
            quadviews[0].update()
            quadviews[1].view_distance = value
            quadviews[1].update()
            quadviews[2].view_distance = value
            quadviews[2].update()
        else:
            self.region_data.view_distance = value
            self.region_data.update()
    raw_distance = property(__get, __set)
    
    def __get(self):
        return self.region_data.view_location.copy()
    def __set(self, value):
        if self.quadview_sync and (not self.is_region_3d):
            quadviews = self.quadviews
            quadviews[0].view_location = value.copy()
            quadviews[0].update()
            quadviews[1].view_location = value.copy()
            quadviews[1].update()
            quadviews[2].view_location = value.copy()
            quadviews[2].update()
        else:
            self.region_data.view_location = value.copy()
            self.region_data.update()
    raw_location = property(__get, __set)
    
    def __get(self):
        value = self.region_data.view_rotation.copy()#.normalized()
        if not self.use_camera_axes:
            value = value * Quaternion((1, 0, 0), -math.pi*0.5)
        return value
    def __set(self, value):
        if not self.use_camera_axes:
            value = value * Quaternion((1, 0, 0), math.pi*0.5)
        if self.is_region_3d or (not self.quadview_lock):
            self.region_data.view_rotation = value.copy()#.normalized()
            self.region_data.update()
    raw_rotation = property(__get, __set)
    
    def __get(self):
        if self.is_camera and (self.camera.type == 'CAMERA') and (self.camera.data.type == 'ORTHO'):
            return self.camera.data.ortho_scale
        else:
            return self.raw_distance
    def __set(self, value):
        pivot = self.pivot
        value = max(value, 1e-12) # just to be sure that it's never zero or negative
        if self.is_camera and (self.camera.type == 'CAMERA') and (self.camera.data.type == 'ORTHO'):
            if self.lock_camera:
                self.camera.data.ortho_scale = value
        else:
            self.raw_distance = value
        self.pivot = pivot
    distance = property(__get, __set)
    
    def __set_cam_matrix(self, m):
        cam = self.space_data.camera
        if self.lock_camera_parent:
            max_parent = cam
            while True:
                if (max_parent.parent is None) or (max_parent.parent_type == 'VERTEX'):
                    break # 'VERTEX' isn't a rigidbody-type transform
                max_parent = max_parent.parent
            cm_inv = cam.matrix_world.inverted()
            pm = cm_inv * max_parent.matrix_world
            max_parent.matrix_world = m * pm
        else:
            cam.matrix_world = m
    
    def __get(self):
        v3d = self.space_data
        rv3d = self.region_data
        if self.is_camera:
            m = v3d.camera.matrix_world
            return m.translation + self.forward * rv3d.view_distance
        elif v3d.lock_object:
            obj = self.lock_object
            bone = self.lock_bone
            m = obj.matrix_world
            if bone: m = m * (bone.matrix if obj.mode == 'EDIT' else bone.matrix_local)
            return m.translation.copy()
        elif v3d.lock_cursor:
            return v3d.cursor_location.copy()
        else:
            return self.raw_location
    def __set(self, value):
        v3d = self.space_data
        rv3d = self.region_data
        if self.is_camera:
            if self.lock_camera:
                m = v3d.camera.matrix_world.copy()
                m.translation = value - self.forward * rv3d.view_distance
                self.__set_cam_matrix(m)
        elif v3d.lock_object:
            pass
        elif v3d.lock_cursor:
            pass
        else:
            self.raw_location = value
    focus = property(__get, __set)
    
    # Camera (and viewport): -Z is forward, Y is up, X is right
    def __get(self):
        v3d = self.space_data
        rv3d = self.region_data
        if self.is_camera:
            value = v3d.camera.matrix_world.to_quaternion()
            if not self.use_camera_axes:
                value = value * Quaternion((1, 0, 0), -math.pi*0.5)
        else:
            value = self.raw_rotation
        return value
    def __set(self, value):
        v3d = self.space_data
        rv3d = self.region_data
        pivot = self.pivot
        if self.is_camera:
            if not self.use_camera_axes:
                value = value * Quaternion((1, 0, 0), math.pi*0.5)
            if self.lock_camera:
                LRS = v3d.camera.matrix_world.decompose()
                m = matrix_LRS(LRS[0], value, LRS[2])
                forward = -m.col[2].to_3d().normalized() # in camera axes, forward is -Z
                m.translation = self.focus - forward * rv3d.view_distance
                self.__set_cam_matrix(m)
        else:
            self.raw_rotation = value
        self.pivot = pivot
    rotation = property(__get, __set)
    
    def __get(self): # in object axes
        return nautical_euler_from_axes(self.forward, self.right) # or: YXZ euler?
    def __set(self, value): # in object axes
        rot = nautical_euler_to_quaternion(value) # or: YXZ euler?
        if self.use_camera_axes:
            rot = rot * Quaternion((1, 0, 0), math.pi*0.5)
        self.rotation = rot
    turntable_euler = property(__get, __set)
    
    def __get(self):
        v3d = self.space_data
        rv3d = self.region_data
        if self.is_camera:
            return v3d.camera.matrix_world.translation.copy()
        else:
            return self.focus - self.forward * rv3d.view_distance
    def __set(self, value):
        self.focus = self.focus + (value - self.viewpoint)
    viewpoint = property(__get, __set)
    
    def __get(self):
        return (self.viewpoint if self.use_viewpoint else self.focus)
    def __set(self, value):
        if self.use_viewpoint:
            self.viewpoint = value
        else:
            self.focus = value
    pivot = property(__get, __set)
    
    def __get(self, viewpoint=False):
        m = self.rotation.to_matrix()
        m.resize_4x4()
        m.translation = (self.viewpoint if viewpoint else self.focus)
        return m
    def __set(self, m, viewpoint=False):
        if viewpoint:
            self.viewpoint = m.translation.copy()
        else:
            self.focus = m.translation.copy()
        self.rotation = m.to_quaternion()
    matrix = property(__get, __set)
    
    # TODO:
    #matrix_view (origin at near plane)
    #matrix_projection
    #matrix_projview
    #fov angles (x, y) ?
    #aperture (x, y) at distance 1
    # https://unspecified.wordpress.com/2012/06/21/calculating-the-gluperspective-matrix-and-other-opengl-matrix-maths/
    # http://stackoverflow.com/questions/18404890/how-to-build-perspective-projection-matrix-no-api
    # http://gamedev.stackexchange.com/questions/71265/why-are-there-different-ways-of-building-projection-matrices
    
    def __get_axis(self, x, y, z):
        rot = self.rotation
        if self.use_camera_axes: rot = rot * Quaternion((1, 0, 0), -math.pi*0.5)
        return (rot * Vector((x, y, z))).normalized()
    forward = property(lambda self: self.__get_axis(0, 1, 0))
    back = property(lambda self: self.__get_axis(0, -1, 0))
    up = property(lambda self: self.__get_axis(0, 0, 1))
    down = property(lambda self: self.__get_axis(0, 0, -1))
    left = property(lambda self: self.__get_axis(-1, 0, 0))
    right = property(lambda self: self.__get_axis(1, 0, 0))
    
    def __get(self):
        region = self.region
        rv3d = self.region_data
        
        x, y, z, t = self.right, self.up, self.forward, self.viewpoint
        m = matrix_compose(x, y, z, t)
        m_inv = m.inverted()
        refpos = t + z
        def getpoint(px, py):
            p = region_2d_to_location_3d(region, rv3d, Vector((px, py)), refpos).to_3d()
            return (m_inv * p)
        
        w, h = region.width, region.height
        p00 = getpoint(0, 0)
        pW0 = getpoint(w, 0)
        p0H = getpoint(0, h)
        pWH = getpoint(w, h)
        
        persp = float(self.is_perspective)
        sx = (pW0 - p00).magnitude
        sy = (p0H - p00).magnitude
        dx = (p00.x + pW0.x) * 0.5
        dy = (p00.y + p0H.y) * 0.5
        dz = p00.z
        
        return (Vector((sx, sy, persp)), Vector((dx, dy, dz)))
    projection_info = property(__get)
    
    def region_rect(self, overlap=True):
        return calc_region_rect(self.area, self.region, overlap)
    
    def convert_ui_coord(self, xy, src, dst, vector=True):
        return convert_ui_coord(self.area, self.region, xy, src, dst, vector)
    
    def z_distance(self, pos, clamp_near=None, clamp_far=None):
        if clamp_far is None: clamp_far = clamp_near
        
        near, far, origin = self.zbuf_range
        dist = (pos - origin).dot(self.forward)
        
        if self.is_perspective:
            if clamp_near is not None: dist = max(dist, near * (1.0 + clamp_near))
            if clamp_far is not None: dist = min(dist, far * (1.0 - clamp_far))
        else:
            if clamp_near is not None: dist = max(dist, lerp(near, far, clamp_near))
            if clamp_far is not None: dist = min(dist, lerp(far, near, clamp_far))
        
        return dist
    
    def project(self, pos, align=False, coords='REGION'):
        region = self.region
        rv3d = self.region_data
        
        xy = location_3d_to_region_2d(region, rv3d, Vector(pos))
        if xy is None: return None
        
        if align: xy = snap_pixel_vector(xy)
        
        return self.convert_ui_coord(xy, 'REGION', coords)
    
    def unproject(self, xy, pos=None, align=False, coords='REGION'):
        region = self.region
        rv3d = self.region_data
        
        xy = self.convert_ui_coord(xy, coords, 'REGION')
        
        if align: xy = snap_pixel_vector(xy)
        
        if pos is None:
            pos = self.focus
        elif isinstance(pos, (int, float)):
            pos = self.zbuf_range[2] + self.forward * pos
        
        return region_2d_to_location_3d(region, rv3d, Vector(xy), Vector(pos)).to_3d()
    
    def project_primitive(self, primitive, align=False, coords='REGION'):
        primitive = clip_primitive(primitive, self.z_plane(0.0, 1))
        primitive = clip_primitive(primitive, self.z_plane(1.0, -1))
        if not primitive: return primitive
        return [self.project(p, align=align, coords=coords) for p in primitive]
    
    def z_plane(self, z, normal_sign=1):
        normal = self.forward
        near, far, origin = self.zbuf_range
        return (origin + normal * lerp(near, far, z), normal * normal_sign)
    
    def ray(self, xy, coords='REGION'):
        region = self.region
        rv3d = self.region_data
        
        xy = self.convert_ui_coord(xy, coords, 'REGION')
        
        view_dir = self.forward
        near, far, origin = self.zbuf_range
        near = origin + view_dir * near
        far = origin + view_dir * far
        
        # Just to be sure (sometimes scene.ray_cast said that ray start/end aren't 3D)
        a = region_2d_to_location_3d(region, rv3d, xy.to_2d(), near).to_3d()
        b = region_2d_to_location_3d(region, rv3d, xy.to_2d(), far).to_3d()
        return a, b
    
    def read_zbuffer(self, xy, wh=(1, 1), centered=False, cached=True, coords='REGION'):
        cached_zbuf = ZBufferRecorder.buffers.get(self.region)
        if (not cached) or (cached_zbuf is None):
            xy = self.convert_ui_coord(xy, coords, 'WINDOW', False)
            return cgl.read_zbuffer(xy, wh, centered)
        else:
            xy = self.convert_ui_coord(xy, coords, 'REGION', False)
            return cgl.read_zbuffer(xy, wh, centered, (cached_zbuf, self.region.width, self.region.height))
    
    def zbuf_to_depth(self, zbuf):
        near, far, origin = self.zbuf_range
        if self.is_perspective:
            return (far * near) / (zbuf*near + (1.0 - zbuf)*far)
        else:
            return zbuf*far + (1.0 - zbuf)*near
    
    def depth_to_zbuf(self, depth):
        near, far, origin = self.zbuf_range
        if self.is_perspective:
            zbuf = (((far * near) / depth) - far) / (near - far)
        else:
            zbuf = (depth - near) / (far - near)
    
    def depth(self, xy, cached=True, coords='REGION'):
        return self.zbuf_to_depth(self.read_zbuffer(xy, cached=cached, coords=coords)[0])
    
    # NDC means "normalized device coordinates"
    def to_ndc(self, pos, to_01=False):
        region = self.region
        rv3d = self.region_data
        
        near, far, origin = self.zbuf_range
        xy = location_3d_to_region_2d(region, rv3d, Vector(pos))
        z = self.z_distance(pos)
        
        nx = (xy[0] / region.width)
        ny = (xy[1] / region.height)
        nz = ((z - near) / (far - near))
        if not to_01:
            nx = nx * 2.0 - 1.0
            ny = ny * 2.0 - 1.0
            nz = nz * 2.0 - 1.0
        
        return Vector((nx, ny, nz))
    
    def from_ndc(self, pos, to_01=False):
        region = self.region
        rv3d = self.region_data
        
        nx = pos[0]
        ny = pos[1]
        nz = pos[2]
        if not to_01:
            nx = (nx + 1.0) * 0.5
            ny = (ny + 1.0) * 0.5
            nz = (nz + 1.0) * 0.5
        
        near, far, origin = self.zbuf_range
        xy = Vector((nx * region.width, ny * region.height))
        z = near + nz * (far - near)
        pos = origin + self.forward * z
        return region_2d_to_location_3d(region, rv3d, xy, pos).to_3d()
    
    # Extra arguments (all False by default):
    # extend: add the result to the selection or replace the selection with the result
    # deselect: remove the result from the selection
    # toggle: toggle the result's selected state
    # center: use objects' centers, not their contents (geometry)
    # enumerate: list objects/elements?
    # object: if enabled, in edit mode will select objects instead of elements
    def select(self, xy, revert=True, obj_too=True, cycle=False, select_mode={'VERT','EDGE','FACE'}, coords='REGION', **kwargs):
        xy = self.convert_ui_coord(xy, coords, 'REGION', False)
        
        modify = not revert # if revert is None, selection is not reverted but results are still calculated
        
        context_override = self.context_dict
        active_object = context_override["active_object"]
        tool_settings = context_override["tool_settings"]
        
        if not modify:
            prev_selection = SelectionSnapshot()
        else:
            obj_too = False
        
        if obj_too: # obj_too means we want to get either object or element, whichever is closer
            sel = prev_selection.snapshot_curr[0] # current mode
            sel_obj = prev_selection.snapshot_obj[0] # object mode
        else:
            sel = Selection() # current mode
        mode = sel.normalized_mode
        
        # In paint/sculpt modes, we need to look at selection of Object mode
        # In edit modes, we need to first query edit mode, and if it fails, query object mode
        
        rw, rh = self.region.width, self.region.height
        xyOther = (int((xy[0] + rw//2) % rw), int((xy[1] + rh//2) % rh))
        
        if not cycle: # "not cycle" means we want to always get the object closest to camera
            kwargs.pop("extend", None)
            kwargs.pop("deselect", None)
            kwargs.pop("toggle", None)
            kwargs.pop("enumerate", None)
            
            # Select at different coordinate to avoid cycling behavior
            bpy.ops.view3d.select(context_override, 'EXEC_DEFAULT', location=xyOther, object=kwargs.get("object", False))
            
            # clear the selection
            if obj_too:
                sel.selected = {}
                if mode != 'OBJECT': sel_obj.selected = {}
            else:
                sel.selected = {}
        
        # Note: view3d.select does NOT select anything in Particle Edit mode
        
        is_object_selection = (mode == 'OBJECT') or (mode in BlEnums.paint_sculpt_modes)
        
        if select_mode:
            # IMPORTANT: make sure it's a copy, or we will be basically assigning itself to iself
            prev_select_mode = tuple(tool_settings.mesh_select_mode)
            tool_settings.mesh_select_mode = ('VERT' in select_mode, 'EDGE' in select_mode, 'FACE' in select_mode)
        
        if obj_too:
            kwargs["extend"] = False
            kwargs["deselect"] = False
            kwargs["toggle"] = False
            kwargs["enumerate"] = False
            
            if not is_object_selection:
                kwargs["object"] = True
                bpy.ops.view3d.select(context_override, 'EXEC_DEFAULT', location=xy, **kwargs)
            
            kwargs["object"] = False
            bpy.ops.view3d.select(context_override, 'EXEC_DEFAULT', location=xy, **kwargs)
        else:
            bpy.ops.view3d.select(context_override, 'EXEC_DEFAULT', location=xy, **kwargs)
        
        selected_object = None
        selected_element = None
        selected_element_attrs = None
        selected_bmesh = None
        background_object = None
        
        if not (revert is False):
            sel_cur = Selection()
            sel_obj = (sel_cur if sel_cur.normalized_mode == 'OBJECT' else Selection(mode='OBJECT'))
            
            # Analyze the result (only one object/element is expected)
            if is_object_selection:
                selected_object = next(iter(sel_obj), (None, None))[0]
            else:
                if active_object and (active_object.type == 'MESH') and (active_object.mode == 'EDIT'):
                    history = sel_cur.history
                    selected_element = (history[-1] if history else None)
                else:
                    selected_element, selected_element_attrs = next(iter(sel_cur), (None, None))
                
                if selected_element:
                    selected_bmesh = sel_cur.bmesh
                    selected_object = active_object
                    
                    background_object = next(iter(sel_obj), (None, None))[0]
                else:
                    selected_object = next(iter(sel_obj), (None, None))[0]
        
        if select_mode:
            # This must be done AFTER computing the result, since apparently
            # mesh_select_mode immediately deselects not-enabled types of elements.
            tool_settings.mesh_select_mode = prev_select_mode
        
        if not modify:
            prev_selection.restore()
        
        return RaycastResult(bool(selected_object),
            obj = selected_object,
            elem = selected_element,
            elem_attrs = selected_element_attrs,
            bmesh = selected_bmesh,
            bkg_obj = background_object)
        #return (selected_object, selected_element, selected_element_attrs, selected_bmesh, background_object)
    
    def __calc_search_pattern(r, metric):
        points = []
        for y in range(-r, r+1):
            for x in range(-r, r+1):
                d = metric(x, y)
                if d <= r: points.append((x, y, d))
        points.sort(key=lambda item: item[2])
        return points
    __metrics = {
        'RADIAL':(lambda x, y: math.sqrt(x*x + y*y)),
        'SQUARE':(lambda x, y: max(abs(x), abs(y))),
        'DIAMOND':(lambda x, y: (abs(x) + abs(y))),
    }
    __search_patterns = {
        # Cannot make this a dict expression, since
        # it won't see the __calc_search_pattern()
        'RADIAL':__calc_search_pattern(64, __metrics['RADIAL']),
        'SQUARE':__calc_search_pattern(64, __metrics['SQUARE']),
        'DIAMOND':__calc_search_pattern(64, __metrics['DIAMOND']),
    }
    def __search_pattern(self, pattern):
        if isinstance(pattern, str):
            yield from self.__search_patterns[pattern]
        else: # min, max square
            p_min, p_max = pattern
            x0, y0 = p_min
            x1, y1 = p_max
            for y in range(y0, y1+1):
                for x in range(x0, x1+1):
                    d = max(abs(x), abs(y))
                    yield (x, y, d)
    
    # success, object, matrix, location, normal
    def ray_cast(self, xy, radius=0, pattern='RADIAL', coords='REGION'):
        scene = self.scene
        radius = int(radius)
        search = (radius > 0)
        
        def interpret(rc):
            return RaycastResult(rc[0], obj=rc[-2], location=rc[1], normal=rc[2], elem_index=rc[3])
        
        if not search:
            ray = self.ray(xy, coords=coords)
            rc = BlUtil.Scene.line_cast(scene, ray[0], ray[1])
            return interpret(rc)
        else:
            x, y = xy
            for dxy in self.__search_pattern(pattern):
                if dxy[2] > radius: break
                ray = self.ray((x+dxy[0], y+dxy[1]), coords=coords)
                rc = BlUtil.Scene.line_cast(scene, ray[0], ray[1])
                if rc[0]: return interpret(rc)
            return RaycastResult()
    
    # success, object, matrix, location, normal
    def depth_cast(self, xy, radius=0, pattern='RADIAL', search_z=False, cached=True, coords='REGION'):
        xy = self.convert_ui_coord(xy, coords, 'REGION', False)
        
        radius = int(radius)
        search = (radius > 0)
        radius = max(radius, 1)
        sz = radius * 2 + 1 # kernel size
        w, h = sz, sz
        
        zbuf = self.read_zbuffer(xy, (sz, sz), centered=True, cached=cached)
        
        def get_pos(x, y):
            wnd_x = min(max(x+radius, 0), w-1)
            wnd_y = min(max(y+radius, 0), h-1)
            z = zbuf[wnd_x + wnd_y * w]
            if (z >= 1.0) or (z < 0.0): return None
            d = self.zbuf_to_depth(z)
            return self.unproject((xy[0]+x, xy[1]+y), d)
        
        cx, cy = 0, 0
        center = None
        if search:
            view_dir = self.forward
            best_dist = float("inf")
            for dxy in self.__search_pattern(pattern):
                if dxy[2] > radius: break
                p = get_pos(dxy[0], dxy[1])
                if p is not None:
                    dist = p.dot(view_dir)
                    if dist < best_dist:
                        best_dist = dist
                        cx, cy = dxy[0], dxy[1]
                        center = p
                    if not search_z: break
        else:
            center = get_pos(0, 0)
        
        #if center is None: return (False, None, Matrix(), Vector(), Vector())
        if center is None: return RaycastResult()
        
        normal_count = 0
        normal = Vector()
        
        last_i = -10 # just some big number
        last_p = None
        neighbors = ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1))
        for i, nbc in enumerate(neighbors):
            nbx, nby = nbc
            p = get_pos(cx + nbx, cy + nby)
            if p is None: continue
            if (i - last_i) < 4:
                d0 = last_p - center
                d1 = p - center
                normal += d0.cross(d1).normalized()
                normal_count += 1
            last_p = p
            last_i = i
        
        if normal_count > 1: normal.normalize()
        if normal.magnitude < 0.5: normal = -self.forward
        
        return RaycastResult(True, location=center, normal=normal)
        #return (True, None, Matrix(), center, normal)
    
    # grid/increment & axis locks (& matrix) are not represented here, because
    # they are not involved in finding an element/position/normal under the mouse
    def snap_cast(self, xy, coords='REGION', **kwargs):
        snaps = set(kwargs.get("snaps", {'VERT','EDGE','FACE','DEPTH'})) # Selection modes
        #snaps = set(kwargs.get("snaps", {'FACE'})) # Selection modes
        smooth = kwargs.get("smooth", 'NEVER') # 'NEVER', 'ALWAYS', 'SMOOTHNESS' - whether to interpolate normals
        peel_volume = kwargs.get("peel_volume", False) # scene.tool_settings.use_snap_peel_object
        mesh_baker = kwargs.get("mesh_baker", None)
        loose = kwargs.get("loose", True)
        midpoints = kwargs.get("midpoints", False)
        
        # in local view only OBJECT mode is allowed, and "snap to loose" requires editmode
        loose = loose and (self.space_data.local_view is None)
        
        snap_depth = ('DEPTH' in snaps)
        if snap_depth: snaps.discard('DEPTH')
        
        if mesh_baker and mesh_baker.finished:
            scene = self.scene
            ray = self.ray(xy, coords=coords)
            baked_obj = mesh_baker.object()
            m = baked_obj.matrix_world
            m_inv = matrix_inverted_safe(m)
            
            view_dir = self.forward
            
            vert_edge_max_dist = 5.0
            result_f = None
            result_e = None
            result_v = None
            
            raycast_vert = (not loose) and ('VERT' in snaps)
            raycast_edge = (not loose) and ('EDGE' in snaps)
            raycast_face = ('FACE' in snaps)
            if raycast_face: snaps.discard('FACE')
            
            if raycast_face:
                ray0 = m_inv * ray[0]
                ray1 = m_inv * ray[1]
                success, location, normal, index = BlUtil.Object.line_cast(baked_obj, ray0, ray1)
                
                if success:
                    polygon = baked_obj.data.polygons[index]
                    #tessface = baked_obj.data.tessfaces[index] # this will error if tessfaces are not calculated
                    
                    if midpoints: location, normal = Vector(polygon.center), Vector(polygon.normal)
                    
                    location, normal = transform_point_normal(m, location, normal)
                    
                    if view_dir.dot(normal) > 0: normal = -normal
                    
                    obj, bone, bbox = mesh_baker.face_to_obj(index)
                    
                    result = RaycastResult(True, obj=obj, elem=bone, location=location, normal=normal)
                    result.bbox = bbox
                    result.dist = 0.0
                    result.type = 'FACE'
                    result_f = result
                    
                    vertices = [baked_obj.data.vertices[vi] for vi in polygon.vertices]
                    points_normals = [transform_point_normal(m, v.co, v.normal) for v in vertices]
                    
                    plane_near = self.z_plane(0)
                    tangential = None
                    n_verts = len(points_normals)
                    
                    best_dist = float("inf")
                    for i in range(n_verts):
                        v0, n0 = points_normals[i]
                        #print("v0, n0 = points_normals[i]")
                        v1, n1 = points_normals[(i+1) % n_verts]
                        #print("v1, n1 = points_normals[(i+1) % n_verts]")
                        segment = clip_primitive([v0, v1], plane_near)
                        #print("segment = clip_primitive([v0, v1], plane_near)")
                        if not segment: continue
                        
                        p0 = self.project(segment[0], coords=coords)
                        p1 = self.project(segment[1], coords=coords)
                        #print("p0 = self.project(segment[0], coords=coords)")
                        
                        dist = dist_to_segment(xy, p0, p1)
                        #print("dist = dist_to_segment(xy, p0, p1)")
                        if dist < best_dist:
                            best_dist = dist
                            tangential = (v1 - v0).normalized()
                            
                            if raycast_edge and (dist < vert_edge_max_dist):
                                edge_normal = (n0 + n1).normalized()
                                edge_normal2 = tangential.cross(edge_normal)
                                edge_normal = edge_normal2.cross(tangential).normalized()
                                result_e = RaycastResult(True, obj=obj, elem=bone)
                                result_e.bbox = bbox
                                result_e.elem_points_normals = [(v0, edge_normal), (v1, edge_normal)]
                                result_e.dist = float("nan")
                                result_e.type = 'EDGE'
                    
                    if raycast_vert:
                        best_dist = float("inf")
                        for i in range(n_verts):
                            v0, n0 = points_normals[i]
                            p0 = self.project(v0, coords=coords)
                            if not p0: continue
                            
                            dist = (xy - p0).magnitude
                            if (dist < best_dist) and (dist < vert_edge_max_dist):
                                best_dist = dist
                                
                                result_v = RaycastResult(True, obj=obj, elem=bone)
                                result_v.bbox = bbox
                                result_v.elem_points_normals = [(v0, n0)]
                                result_v.dist = float("nan")
                                result_v.type = 'VERT'
                    
                    result.tangential2 = tangential
                    
                    result.elem_points_normals = points_normals
            
            if snaps and loose: # VERT or EDGE
                edit_preferences = bpy.context.user_preferences.edit
                global_undo = edit_preferences.use_global_undo
                
                active_obj = scene.objects.active
                prev_mode = (active_obj.mode if active_obj else 'OBJECT')
                
                # DISRUPTIVE SECTION
                edit_preferences.use_global_undo = False
                
                if baked_obj.name not in scene.objects: scene.objects.link(baked_obj)
                scene.update()
                
                # Mesh select mode outside of edit mode MUST INCLUDE vertices,
                # or vertices WON'T be selected during select()! (Blender's quirk)
                tool_settings = scene.tool_settings
                prev_select_mode = tuple(tool_settings.mesh_select_mode)
                tool_settings.mesh_select_mode = (True, True, True)
                
                if prev_mode != 'OBJECT': bpy.ops.object.mode_set(self.context_dict, mode='OBJECT')
                
                scene.objects.active = baked_obj
                bpy.ops.object.mode_set(self.context_dict, mode='EDIT')
                
                kwargs = dict(
                    revert = None,
                    #cycle = True, # no, this doesn't work good in this case
                    extend = False,
                    deselect = False,
                    toggle = False,
                    enumerate = False,
                )
                
                if 'EDGE' in snaps:
                    result = self.select(xy, coords=coords, select_mode={'EDGE'}, **kwargs)
                    result.type = 'EDGE'
                    result.dist = float("nan")
                    result_e = result
                if 'VERT' in snaps:
                    result = self.select(xy, coords=coords, select_mode={'VERT'}, **kwargs)
                    result.type = 'VERT'
                    result.dist = float("nan")
                    result_v = result
                
                bpy.ops.object.mode_set(self.context_dict, mode='OBJECT')
                scene.objects.active = active_obj
                
                # the operator can error if context is already the same
                if prev_mode != 'OBJECT': bpy.ops.object.mode_set(self.context_dict, mode=prev_mode)
                
                tool_settings.mesh_select_mode = prev_select_mode
                
                scene.objects.unlink(baked_obj)
                
                edit_preferences.use_global_undo = global_undo
                # DISRUPTIVE SECTION
            
            tangential = None
            for result in (result_e, result_v): # edge first (calculates tangential)
                if not result: continue
                result.success &= bool(result.elem_points_normals)
                
                if not result.elem_points_normals: continue
                
                points_normals = result.elem_points_normals
                
                if len(points_normals) == 1: # vertex
                    if result.elem_index is None:
                        obj, bone, bbox = result.obj, result.elem, result.bbox
                    else:
                        obj, bone, bbox = mesh_baker.vert_to_obj(result.elem_index)
                    
                    location, normal = points_normals[0]
                    
                    proj = self.project(location, coords=coords)
                    dist = (proj - Vector(xy)).magnitude
                elif len(points_normals) == 2: # edge
                    if result.elem_index is None:
                        obj, bone, bbox = result.obj, result.elem, result.bbox
                    else:
                        obj, bone, bbox = mesh_baker.edge_to_obj(result.elem_index)
                    
                    v0 = points_normals[0][0]
                    v1 = points_normals[1][0]
                    dv = (v1 - v0)
                    
                    location = v0 + dv * line_line_t((v0, v1), ray, 0.5, clip0=0.0, clip1=1.0)
                    normal = points_normals[0][1]
                    tangential = dv.normalized()
                    
                    # make sure normal is perpendicular to edge
                    normal = (normal - normal.project(tangential)).normalized()
                    
                    proj = self.project(location, coords=coords)
                    dist = (proj - Vector(xy)).magnitude
                    
                    if midpoints: location = (v0 + v1) * 0.5
                
                result.obj = obj
                if bone:
                    result.elem = bone
                else:
                    result.bkg_obj = None
                    result.bmesh = None
                    result.elem = None
                    result.elem_attrs = None
                    result.elem_index = None
                
                result.bbox = bbox
                
                result.location = location
                result.normal = normal
                result.tangential2 = tangential
                result.dist = dist
                
                result.success &= (result.dist < vert_edge_max_dist)
                if result_f:
                    result.success &= (mathutils.geometry.distance_point_to_plane(
                        location, result_f.location, result_f.normal) > -1e-6)
            
            if result_v: return result_v
            if result_e: return result_e
            if result_f: return result_f
        
        if not snap_depth: return RaycastResult()
        
        # non-mesh_baker fallback
        with ToggleObjectMode(True):
            result_sel = self.select(xy, coords=coords)
            #selected_object, selected_element, selected_bmesh, background_object
        
        #window = ((-15, -15), (13, 14)) # ~ the same window that selection uses
        #ray_result = self.depth_cast(xy, radius=16, pattern=window, search_z=True, coords=coords)
        ray_result = self.depth_cast(xy, coords=coords)
        #success, object, matrix, position, normal
        
        # Snap is successful only when we know the snapping
        # location; having snapping object isn't obligatory.
        return RaycastResult(ray_result.success, obj=result_sel.obj, location=ray_result.location, normal=ray_result.normal)
    
    del __get
    del __set

class RaycastResult:
    success = False
    location = None
    normal = None
    tangential1 = None
    tangential2 = None
    normal = None
    bkg_obj = None
    obj = None
    bbox = None
    bmesh = None
    elem = None
    elem_attrs = None
    elem_index = None
    elem_points_normals = None
    
    def __init__(self, success=False, **kwargs):
        self.success = bool(success)
        if not success: return
        
        self.location = kwargs.get("location") or Vector()
        self.normal = kwargs.get("normal") or Vector()
        self.tangential1 = kwargs.get("tangential1")
        self.tangential2 = kwargs.get("tangential2")
        
        self.bkg_obj = kwargs.get("bkg_obj")
        
        obj = kwargs.get("obj")
        if not obj: return
        self.obj = obj
        
        elem = kwargs.get("elem")
        if not elem: return
        self.elem = elem
        self.elem_attrs = kwargs.get("elem_attrs")
        self.bmesh = kwargs.get("bmesh")
        
        if isinstance(elem, bmesh.types.BMVert):
            matrix = self.matrix
            if (len(elem.link_faces) > 0) or (len(elem.link_edges) == 0):
                vertex_normal = elem.normal
            else:
                vertex_normal = Vector()
                for e in elem.link_edges:
                    v_other = e.other_vert(elem)
                    vertex_normal += (elem.co - v_other.co).normalized()
                vertex_normal.normalize()
            if vertex_normal.magnitude < 0.5: vertex_normal = Vector((0, 0, 1))
            self.elem_index = elem.index
            self.elem_points_normals = [transform_point_normal(matrix, elem.co, vertex_normal, False)]
        elif isinstance(elem, bmesh.types.BMEdge):
            matrix = self.matrix
            self.elem_index = elem.index
            edge_normal = Vector()
            for f in elem.link_faces:
                edge_normal += f.normal
            edge_normal.normalize()
            if edge_normal.magnitude < 0.5:
                v0, v1 = elem.verts
                edge_normal = orthogonal_in_XY(v1.co - v0.co).normalized()
            self.elem_points_normals = [transform_point_normal(matrix, v.co, edge_normal, False) for v in elem.verts]
        elif isinstance(self.elem, bmesh.types.BMFace):
            matrix = self.matrix
            self.elem_index = elem.index
            self.elem_points_normals = [transform_point_normal(matrix, v.co, v.normal) for v in elem.verts]
    
    matrix = property(lambda self: Matrix(self.obj.matrix_world) if self.obj else Matrix())
    
    def __bool__(self):
        return self.success
    
    def __str__(self):
        obj_name = (self.obj.name if self.obj else None)
        elem_type = (type(self.elem) if self.elem else None)
        return "({}, {}, {}, {})".format(repr(obj_name), elem_type, self.location, self.normal)

#============================================================================#
class Pick_Base:
    def invoke(self, context, event):
        context.window.cursor_modal_set('EYEDROPPER')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        cancel = (event.type in {'ESC', 'RIGHTMOUSE'})
        confirm = (event.type == 'LEFTMOUSE') and (event.value == 'PRESS')
        
        mouse = Vector((event.mouse_x, event.mouse_y))
        
        raycast_result = None
        sv = SmartView3D((mouse.x, mouse.y, 0))
        if sv:
            #raycast_result = sv.ray_cast(mouse, coords='WINDOW')
            raycast_result = sv.select(mouse, coords='WINDOW')
        
        obj = None
        if raycast_result and raycast_result.success:
            obj = raycast_result.obj
        
        txt = (self.obj_to_info(obj) if obj else "")
        context.area.header_text_set(txt)
        
        if cancel or confirm:
            if confirm:
                self.on_confirm(context, obj)
            context.area.header_text_set()
            context.window.cursor_modal_restore()
            return ({'FINISHED'} if confirm else {'CANCELLED'})
        return {'RUNNING_MODAL'}

#============================================================================#
# Blender has a tendency to clear the contents of Z-buffer during its default operation,
# so user operators usually don't have ability to use depth buffer at their invocation.
# This hack attempts to alleviate this problem, at the cost of likely stalling GL pipeline.
class ZBufferRecorder:
    buffers = {}
    queue = []
    
    @staticmethod
    def draw_pixel_callback(users):
        context = bpy.context # we need most up-to-date context
        area = context.area
        region = context.region
        
        if users > 0:
            xy = (region.x, region.y)
            wh = (region.width, region.height)
            zbuf = cgl.read_zbuffer(xy, wh)
        
        buffers = ZBufferRecorder.buffers
        queue = ZBufferRecorder.queue
        
        if region in buffers:
            # If region is encountered the second time, Blender has made a full redraw cycle.
            # We can safely discard old caches.
            index = queue.index(region)
            for i in range(index+1):
                buffers.pop(queue[i], None)
            queue = queue[index+1:]
            ZBufferRecorder.queue = queue
        
        if users > 0:
            buffers[region] = zbuf
            queue.append(region)
    
    @classmethod
    def copy(cls, other):
        cls.buffers = other.buffers
        cls.queue = other.queue
