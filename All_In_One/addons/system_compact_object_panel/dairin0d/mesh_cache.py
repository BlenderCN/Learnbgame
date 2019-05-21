# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
import bmesh

from mathutils import Vector, Matrix, Quaternion, Euler

import math

from various_utils import ToggleObjectMode
#============================================================================#

# TODO: update to match the current API
# TODO: documentation

class MeshCacheItem:
    def __init__(self):
        self.variants = {}
    
    def __getitem__(self, variant):
        return self.variants[variant][0]
    
    def __setitem__(self, variant, conversion):
        mesh = conversion[0].data
        #mesh.update(calc_tessface=True)
        #mesh.calc_tessface()
        mesh.calc_normals()
        
        self.variants[variant] = conversion
    
    def __contains__(self, variant):
        return variant in self.variants
    
    def dispose(self):
        for obj, converted in self.variants.values():
            if converted:
                mesh = obj.data
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(mesh)
        self.variants = None

class MeshCache:
    """
    Keeps a cache of mesh equivalents of requested objects.
    It is assumed that object's data does not change while
    the cache is in use.
    """
    
    variants_enum = {'RAW', 'PREVIEW', 'RENDER'}
    variants_normalization = {
        'MESH':{},
        'CURVE':{},
        'SURFACE':{},
        'FONT':{},
        'META':{'RAW':'PREVIEW'},
        'ARMATURE':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'LATTICE':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'EMPTY':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'CAMERA':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'LAMP':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
        'SPEAKER':{'RAW':'PREVIEW', 'RENDER':'PREVIEW'},
    }
    conversible_types = {'MESH', 'CURVE', 'SURFACE', 'FONT',
                         'META', 'ARMATURE', 'LATTICE'}
    convert_types = conversible_types
    
    def __init__(self, scene, convert_types=None):
        self.scene = scene
        if convert_types:
            self.convert_types = convert_types
        self.cached = {}
    
    def __del__(self):
        self.clear()
    
    def clear(self, expect_zero_users=False):
        for cache_item in self.cached.values():
            if cache_item:
                try:
                    cache_item.dispose()
                except RuntimeError:
                    if expect_zero_users:
                        raise
        self.cached.clear()
    
    def __delitem__(self, obj):
        cache_item = self.cached.pop(obj, None)
        if cache_item:
            cache_item.dispose()
    
    def __contains__(self, obj):
        return obj in self.cached
    
    def __getitem__(self, obj):
        if isinstance(obj, tuple):
            return self.get(*obj)
        return self.get(obj)
    
    def get(self, obj, variant='PREVIEW', reuse=True):
        if variant not in self.variants_enum:
            raise ValueError("Mesh variant must be one of %s" %
                             self.variants_enum)
        
        # Make sure the variant is proper for this type of object
        variant = (self.variants_normalization[obj.type].
                   get(variant, variant))
        
        if obj in self.cached:
            cache_item = self.cached[obj]
            try:
                # cache_item is None if object isn't conversible to mesh
                return (None if (cache_item is None)
                        else cache_item[variant])
            except KeyError:
                pass
        else:
            cache_item = None
        
        if obj.type not in self.conversible_types:
            self.cached[obj] = None
            return None
        
        if not cache_item:
            cache_item = MeshCacheItem()
            self.cached[obj] = cache_item
        
        conversion = self._convert(obj, variant, reuse)
        cache_item[variant] = conversion
        
        return conversion[0]
    
    def _convert(self, obj, variant, reuse=True):
        obj_type = obj.type
        obj_mode = obj.mode
        data = obj.data
        
        if obj_type == 'MESH':
            if reuse and ((variant == 'RAW') or (len(obj.modifiers) == 0)):
                return (obj, False)
            else:
                force_objectmode = (obj_mode in ('EDIT', 'SCULPT'))
                return (self._to_mesh(obj, variant, force_objectmode), True)
        elif obj_type in ('CURVE', 'SURFACE', 'FONT'):
            if variant == 'RAW':
                bm = bmesh.new()
                for spline in data.splines:
                    for point in spline.bezier_points:
                        bm.verts.new(point.co)
                        bm.verts.new(point.handle_left)
                        bm.verts.new(point.handle_right)
                    for point in spline.points:
                        bm.verts.new(point.co[:3])
                return (self._make_obj(bm, obj), True)
            else:
                if variant == 'RENDER':
                    resolution_u = data.resolution_u
                    resolution_v = data.resolution_v
                    if data.render_resolution_u != 0:
                        data.resolution_u = data.render_resolution_u
                    if data.render_resolution_v != 0:
                        data.resolution_v = data.render_resolution_v
                
                result = (self._to_mesh(obj, variant), True)
                
                if variant == 'RENDER':
                    data.resolution_u = resolution_u
                    data.resolution_v = resolution_v
                
                return result
        elif obj_type == 'META':
            if variant == 'RAW':
                # To avoid the hassle of snapping metaelements
                # to themselves, we just create an empty mesh
                bm = bmesh.new()
                return (self._make_obj(bm, obj), True)
            else:
                if variant == 'RENDER':
                    resolution = data.resolution
                    data.resolution = data.render_resolution
                
                result = (self._to_mesh(obj, variant), True)
                
                if variant == 'RENDER':
                    data.resolution = resolution
                
                return result
        elif obj_type == 'ARMATURE':
            bm = bmesh.new()
            if obj_mode == 'EDIT':
                for bone in data.edit_bones:
                    head = bm.verts.new(bone.head)
                    tail = bm.verts.new(bone.tail)
                    bm.edges.new((head, tail))
            elif obj_mode == 'POSE':
                for bone in obj.pose.bones:
                    head = bm.verts.new(bone.head)
                    tail = bm.verts.new(bone.tail)
                    bm.edges.new((head, tail))
            else:
                for bone in data.bones:
                    head = bm.verts.new(bone.head_local)
                    tail = bm.verts.new(bone.tail_local)
                    bm.edges.new((head, tail))
            return (self._make_obj(bm, obj), True)
        elif obj_type == 'LATTICE':
            bm = bmesh.new()
            for point in data.points:
                bm.verts.new(point.co_deform)
            return (self._make_obj(bm, obj), True)
    
    def _to_mesh(self, obj, variant, force_objectmode=False):
        tmp_name = chr(0x10ffff) # maximal Unicode value
        
        with ToggleObjectMode(force_objectmode):
            if variant == 'RAW':
                mesh = obj.to_mesh(self.scene, False, 'PREVIEW')
            else:
                mesh = obj.to_mesh(self.scene, True, variant)
            mesh.name = tmp_name
        
        return self._make_obj(mesh, obj)
    
    def _make_obj(self, mesh, src_obj):
        tmp_name = chr(0x10ffff) # maximal Unicode value
        
        if isinstance(mesh, bmesh.types.BMesh):
            bm = mesh
            mesh = bpy.data.meshes.new(tmp_name)
            bm.to_mesh(mesh)
        
        tmp_obj = bpy.data.objects.new(tmp_name, mesh)
        
        tmp_obj.matrix_world = src_obj.matrix_world
        
        # This is necessary for correct bbox display # TODO
        # (though it'd be better to change the logic in the raycasting)
        tmp_obj.show_x_ray = src_obj.show_x_ray
        
        tmp_obj.dupli_faces_scale = src_obj.dupli_faces_scale
        tmp_obj.dupli_frames_end = src_obj.dupli_frames_end
        tmp_obj.dupli_frames_off = src_obj.dupli_frames_off
        tmp_obj.dupli_frames_on = src_obj.dupli_frames_on
        tmp_obj.dupli_frames_start = src_obj.dupli_frames_start
        tmp_obj.dupli_group = src_obj.dupli_group
        #tmp_obj.dupli_list = src_obj.dupli_list
        tmp_obj.dupli_type = src_obj.dupli_type
        
        # Make Blender recognize object as having geometry
        # (is there a simpler way to do this?)
        self.scene.objects.link(tmp_obj)
        self.scene.update()
        # We don't need this object in scene
        self.scene.objects.unlink(tmp_obj)
        
        return tmp_obj
