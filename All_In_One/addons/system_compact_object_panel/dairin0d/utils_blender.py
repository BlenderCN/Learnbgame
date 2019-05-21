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

import time

import mathutils
from mathutils import Color, Vector, Euler, Quaternion, Matrix

from .bpy_inspect import BlEnums

from .utils_math import lerp, matrix_LRS, matrix_compose, matrix_decompose, matrix_inverted_safe, orthogonal_XYZ, orthogonal, transform_point_normal
from .utils_python import setattr_cmp, setitem_cmp, AttributeHolder, attrs_to_dict, dict_to_attrs, bools_to_int, binary_search

# ========================== TOGGLE OBJECT MODE ============================ #
#============================================================================#
class ToggleObjectMode:
    def __init__(self, mode='OBJECT'):
        if not isinstance(mode, str):
            mode = ('OBJECT' if mode else None)
        
        self.mode = mode
    
    def __enter__(self):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            active_obj = bpy.context.object
            self.global_undo = edit_preferences.use_global_undo
            self.prev_mode = (active_obj.mode if active_obj else 'OBJECT')
            
            if self.prev_mode != self.mode:
                edit_preferences.use_global_undo = False
                bpy.ops.object.mode_set(mode=self.mode)
        
        return self
    
    def __exit__(self, type, value, traceback):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            if self.prev_mode != self.mode:
                bpy.ops.object.mode_set(mode=self.prev_mode)
                edit_preferences.use_global_undo = self.global_undo

# =============================== MESH CACHE =============================== #
#============================================================================#
class MeshCacheItem:
    def __init__(self):
        self.variants = {}
    
    def __getitem__(self, variant):
        return self.variants[variant][0]
    
    def __setitem__(self, variant, conversion):
        obj, converted = conversion
        mesh = obj.data
        #mesh.update(calc_tessface=True)
        #mesh.calc_tessface()
        mesh.calc_normals()
        
        self.variants[variant] = (obj, converted, mesh)
    
    def __contains__(self, variant):
        return variant in self.variants
    
    def dispose(self):
        for obj, converted, mesh in self.variants.values():
            if not converted: continue
            if obj and obj.name: bpy.data.objects.remove(obj)
            if mesh and mesh.name: bpy.data.meshes.remove(mesh)
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
    
    def __init__(self, scene, convert_types=None):
        self.scene = scene
        self.convert_types = convert_types or self.conversible_types
        self.cached = {}
    
    def __del__(self):
        self.clear()
    
    def clear(self, expect_zero_users=False):
        for cache_item in self.cached.values():
            if not cache_item: continue
            try:
                cache_item.dispose()
            except RuntimeError:
                if expect_zero_users: raise
        self.cached.clear()
    
    def __delitem__(self, obj):
        cache_item = self.cached.pop(obj, None)
        if cache_item: cache_item.dispose()
    
    def __contains__(self, obj):
        return obj in self.cached
    
    def __getitem__(self, obj):
        if isinstance(obj, tuple): return self.get(*obj)
        return self.get(obj)
    
    def get(self, obj, variant='PREVIEW', reuse=True):
        if not (obj or obj.name): return None # deleted objects have empty name
        
        if variant not in self.variants_enum:
            raise ValueError("Mesh variant must be one of %s" % self.variants_enum)
        
        # Make sure the variant is proper for this type of object
        variant = self.variants_normalization[obj.type].get(variant, variant)
        
        if obj in self.cached:
            cache_item = self.cached[obj]
            try:
                # cache_item is None if object isn't conversible to mesh
                return (None if (cache_item is None) else cache_item[variant])
            except KeyError:
                pass
        else:
            cache_item = None
        
        if not ((self.convert_types == 'ALL') or (obj.type in self.convert_types)):
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
            force_objectmode = (obj_mode in ('EDIT', 'SCULPT'))
            if reuse and ((variant == 'RAW') or (len(obj.modifiers) == 0)) and (not force_objectmode):
                return (obj, False)
            else:
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
        else:
            bm = bmesh.new()
            bm.verts.new(Vector()) # just a vertex at the origin
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
        
        if src_obj:
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

# =============================== MESH BAKER =============================== #
#============================================================================#
class MeshBaker:
    def __init__(self, scene, include=None, exclude=None, obj_types=None, edit=False, selection=True, geometry='DEFAULT', origins='DEFAULT', bbox='NONE', dupli=True, solid_only=False, matrix=None, auto_clear=False, collect_materials=False, remove_doubles=None):
        self.scene = scene
        self.mode = BlEnums.mode_from_object(scene.objects.active)
        self.edit = edit # whether to add object geometry in editmode
        self.selection = selection # allow or exclude selection
        self.geometry_mode = geometry # how to add geometry
        self.origins_mode = origins # whether to add origins (None means "only when there is no geometry")
        self.bbox_mode = bbox # whether to add bbox
        self.dupli_mode = dupli # whether to add dupli objects
        self.solid_only = solid_only # whether to ignore non-geometry objects and objects with wire/bounds draw type
        self.matrix = matrix or Matrix()
        self.matrix_inv = matrix_inverted_safe(self.matrix)
        self.auto_clear = auto_clear
        self.collect_materials = collect_materials
        self.remove_doubles = remove_doubles
        self.bm = bmesh.new()
        self._mesh = None
        self._obj = None
        self._vert_to_obj = []
        self._edge_to_obj = []
        self._face_to_obj = []
        self._materials_dict = {}
        self._materials_list = []
        
        self.obj_types = obj_types
        self.objects = set(include or (obj for obj in scene.objects if obj.is_visible(scene)))
        if exclude: self.objects.difference_update(exclude)
        if (self.mode == 'OBJECT') and (not self.selection):
            self.objects = [obj for obj in self.objects if not obj.select]
        else:
            self.objects = list(self.objects)
        self.counter = 0
    
    finished = property(lambda self: self.counter >= len(self.objects))
    
    def mesh(self):
        if self._mesh: return self._mesh
        if self.counter < len(self.objects): return None
        self._mesh = bpy.data.meshes.new("BakedMesh")
        self.bm.to_mesh(self._mesh)
        #self._mesh.update(calc_tessface=True) # calc_tessface() # is this necessary?
        if self._materials_list:
            materials = self._mesh.materials
            for material in self._materials_list:
                materials.append(material)
        return self._mesh
    
    def object(self, mode='UNLINK'):
        if self._obj: return self._obj
        if self.counter < len(self.objects): return None
        self._obj = bpy.data.objects.new("BakedObject", self.mesh())
        self._obj.matrix_world = self.matrix
        # Make Blender recognize object as having geometry
        self.scene.objects.link(self._obj)
        self.scene.update()
        obj = self._obj # save reference in case mode == 'FORGET'
        if mode == 'UNLINK':
            # We don't need this object in scene
            self.scene.objects.unlink(self._obj)
        elif mode == 'HIDE':
            self._obj.hide = True
        elif mode == 'FORGET':
            self.forget_results()
        return obj
    
    @staticmethod
    def _index_cmp(item, i):
        if i < item[0]: return 1
        if i > item[1]: return -1
        return 0
    
    def _names_to_instances(self, result):
        obj = bpy.data.objects.get(result[0])
        bone = None
        if obj and (obj.type == 'ARMATURE'):
            if obj.mode == 'EDIT':
                bone = obj.data.edit_bones.get(result[1])
            else:
                bone = obj.pose.bones.get(result[1])
        return (obj, bone, result[2])
    
    _default_to_obj = ("", "", None)
    
    def vert_to_obj(self, i, instances=True):
        result = self._default_to_obj
        i = binary_search(self._vert_to_obj, i, cmp=self._index_cmp)
        if (i >= 0) and (i < len(self._vert_to_obj)): result = self._vert_to_obj[i][-1]
        if instances: result = self._names_to_instances(result)
        return result
    
    def edge_to_obj(self, i, instances=True):
        result = self._default_to_obj
        i = binary_search(self._edge_to_obj, i, cmp=self._index_cmp)
        if (i >= 0) and (i < len(self._edge_to_obj)): result = self._edge_to_obj[i][-1]
        if instances: result = self._names_to_instances(result)
        return result
    
    def face_to_obj(self, i, instances=True):
        result = self._default_to_obj
        i = binary_search(self._face_to_obj, i, cmp=self._index_cmp)
        if (i >= 0) and (i < len(self._face_to_obj)): result = self._face_to_obj[i][-1]
        if instances: result = self._names_to_instances(result)
        return result
    
    def forget_results(self): # so that they won't be deleted on MeshBaker's destruction
        self._obj = None
        self._mesh = None
    
    def delete_results(self): # old alias, remains for compatibility
        self.cleanup()
    
    def cleanup(self):
        if self._obj and self._obj.name:
            if self._obj.name in self.scene.objects:
                self.scene.objects.unlink(self._obj)
            bpy.data.objects.remove(self._obj)
        self._obj = None
        
        if self._mesh and self._mesh.name:
            bpy.data.meshes.remove(self._mesh)
        self._mesh = None
        
        self._delete_bm()
    
    def update(self, dt=None):
        use_dt = (dt is not None)
        if use_dt: time_stop = time.clock() + dt
        max_count = len(self.objects)
        while self.counter < max_count:
            obj = self.objects[self.counter]
            self.counter += 1
            self._add_obj(obj)
            if self.counter == max_count: self._on_finish()
            if use_dt and (time.clock() > time_stop): return
    
    def _on_finish(self):
        if isinstance(self.remove_doubles, (float, int)): # this will invalidate indices
            bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=self.remove_doubles)
        else:
            self.bm.verts.index_update()
            self.bm.edges.index_update()
            self.bm.faces.index_update()
    
    def _delete_bm(self):
        if self.bm and self.bm.is_valid:
            self.bm.free()
        self.bm = None
    
    def __del__(self):
        if self.auto_clear: self.cleanup()
    
    def _merge(self, bm_copy):
        # As of 2.75, the "dest" argument does not work yet
        #geom = bm_copy.verts[:] + bm_copy.edges[:] + bm_copy.faces[:]
        #bmesh.ops.duplicate(bm_copy, geom=geom, dest=self.bm, use_select_history=False)
        
        # BMesh elements' copy_from() doesn't seem to work on other-mesh elements as well
        
        verts_map = {}
        for vS in bm_copy.verts:
            vD = self.bm.verts.new(Vector(vS.co))
            vD.normal = Vector(vS.normal)
            verts_map[vS] = vD
        for eS in bm_copy.edges:
            try:
                eD = self.bm.edges.new(tuple(verts_map[vS] for vS in eS.verts))
            except ValueError: # edge already exists
                continue
            eD.seam = eS.seam
            eD.smooth = eS.smooth
        for fS in bm_copy.faces:
            try:
                fD = self.bm.faces.new(tuple(verts_map[vS] for vS in fS.verts))
            except ValueError: # face already exists
                continue
            fD.normal = Vector(fS.normal)
            fD.material_index = fS.material_index
            fD.smooth = fS.smooth
    
    def _to_mesh(self, obj, force_objectmode=False):
        force_objectmode |= self.collect_materials
        bm_copy = bmesh.new()
        if obj.type == 'MESH':
            with ToggleObjectMode(force_objectmode):
                bm_copy.from_object(obj, self.scene, deform=True, render=False, cage=False, face_normals=True)
        else:
            with ToggleObjectMode(force_objectmode):
                mesh = obj.to_mesh(self.scene, True, 'PREVIEW')
            bm_copy.from_mesh(mesh)
            bpy.data.meshes.remove(mesh)
        return bm_copy
    
    def _add_sub_obj(self, obj, matrix_world, vert_offsets, edge_offsets):
        if isinstance(obj, bpy.types.DupliObject):
            if obj.hide: return
            main_obj = obj.id_data
            matrix_world = obj.matrix
            obj = obj.object
            
            geometry_mode = self.geometry_mode
            origins_mode = self.origins_mode
            bbox_mode = self.bbox_mode
            dupli_mode = self.dupli_mode
            gather_bone_offsets = False
        else:
            main_obj = obj
            
            geometry_mode = self.geometry_mode
            origins_mode = self.origins_mode
            bbox_mode = self.bbox_mode
            dupli_mode = self.dupli_mode
            gather_bone_offsets = True
        
        default_material_id = None
        material_id_map = {}
        
        if self.collect_materials:
            for slot_id, material_slot in enumerate(obj.material_slots):
                material = material_slot.material
                material_id = self._materials_dict.get(material)
                if material_id is None:
                    material_id = len(self._materials_list)
                    self._materials_dict[material] = material_id
                    self._materials_list.append(material)
                
                material_id_map[slot_id] = material_id
                if default_material_id is None: default_material_id = material_id
        
        bbox = BlUtil.Object.bounding_box(obj)
        
        add_obj = (self.obj_types is None) or (obj.type in self.obj_types)
        add_dupli = bool(dupli_mode)
        
        if self.solid_only:
            if main_obj.draw_type in ('WIRE', 'BOUNDS'):
                add_obj = False
                add_dupli = False
            elif obj.draw_type in ('WIRE', 'BOUNDS'):
                add_obj = False
            elif obj.type not in BlEnums.object_types_geometry:
                add_obj = False
        
        if add_obj:
            obj_type = obj.type
            obj_mode = obj.mode
            data = obj.data
            
            no_selection = not self.selection
            
            bm_copy = None
            
            # WYSIWYG would require reimplementing all of the virtual geometry...
            # It's easier (and probably more often useful) to have SOLID_ONLY mode.
            
            add_geometry = geometry_mode and (geometry_mode != 'NONE')
            if add_geometry:
                if obj_type == 'MESH':
                    if obj_mode == 'EDIT':
                        bm_edit = bmesh.from_edit_mesh(data)
                        if no_selection:
                            bm_copy = bm_edit.copy()
                            for v in tuple(v for v in bm_copy.verts if v.select):
                                bm_copy.verts.remove(v)
                        else:
                            bm_copy = bm_edit.copy()
                    elif obj_mode == 'SCULPT':
                        bm_copy = self._to_mesh(obj, True)
                    else:
                        bm_copy = self._to_mesh(obj, False)
                elif obj_type in ('CURVE', 'SURFACE'):
                    if obj_mode == 'EDIT':
                        bm_copy = (self._to_mesh(obj, True) if self.edit else bmesh.new())
                        for spline in data.splines:
                            for point in spline.bezier_points:
                                if no_selection and (point.select_control_point or
                                    point.select_left_handle or point.select_right_handle): continue
                                vc = bm_copy.verts.new(point.co)
                                vl = bm_copy.verts.new(point.handle_left)
                                vr = bm_copy.verts.new(point.handle_right)
                                #bm_copy.edges.new((vc, vl))
                                #bm_copy.edges.new((vc, vr))
                            for point in spline.points:
                                if no_selection and point.select: continue
                                bm_copy.verts.new(point.co[:3])
                                # TODO: edges between non-bezier points?
                    else:
                        bm_copy = self._to_mesh(obj, False)
                elif obj_type == 'FONT':
                    bm_copy = self._to_mesh(obj, True)
                elif obj_type == 'META':
                    if obj_mode == 'EDIT':
                        # metaelements' geometry is one single whole, so we can't really exclude just some of them.
                        bm_copy = (self._to_mesh(obj, True) if self.edit else bmesh.new())
                        for elem in data.elements:
                            # cannot know if it's selected
                            bm_copy.verts.new(elem.co)
                    else:
                        bm_copy = self._to_mesh(obj, False)
                elif obj_type == 'ARMATURE':
                    bbox = [None, None] # Blender does not return valid bbox for armature
                    bm_copy = bmesh.new()
                    for bone, selected in BlUtil.Object.iter_bone_info(obj):
                        #self._add_bbox(bbox, bone.head) # outdated code - test again?
                        #self._add_bbox(bbox, bone.tail) # outdated code - test again?
                        if no_selection and any(selected): continue
                        if gather_bone_offsets:
                            vert_offsets.append((len(bm_copy.verts), bone.name))
                            edge_offsets.append((len(bm_copy.edges), bone.name))
                        head = bm_copy.verts.new(bone.head)
                        tail = bm_copy.verts.new(bone.tail)
                        bm_copy.edges.new((head, tail))
                    bbox = (bbox[0] or Vector(), bbox[1] or Vector())
                elif obj_type == 'LATTICE':
                    # is this considered "not real geometry"?
                    bbox = [None, None] # Blender does not return valid bbox for lattice
                    bm_copy = bmesh.new()
                    for point in data.points:
                        bm_copy.verts.new(point.co_deform)
                        # TODO: edges between points?
                        #self._add_bbox(bbox, point.co_deform) # outdated code - test again?
                    bbox = (bbox[0] or Vector(), bbox[1] or Vector())
                else:
                    bm_copy = bmesh.new()
            
            if bm_copy is None: bm_copy = bmesh.new()
            verts = bm_copy.verts
            matrix = self.matrix_inv * matrix_world
            
            add_origin = (origins_mode == 'ALWAYS') or ((origins_mode == 'DEFAULT') and (len(verts) == 0))
            if add_origin: self._add_origin(bm_copy, matrix)
            
            add_bbox = bbox_mode and (bbox_mode != 'NONE')
            if add_bbox: self._add_bbox(bm_copy, bbox_mode, bbox, matrix)
            
            if len(verts) > 0:
                if material_id_map:
                    for face in bm_copy.faces:
                        face.material_index = material_id_map.get(face.material_index, default_material_id)
                
                bm_copy.transform(matrix)
                self._merge(bm_copy)
            
            bm_copy.free()
        
        if add_dupli:
            if obj.dupli_type != 'NONE':
                if obj.dupli_list: obj.dupli_list_clear()
                obj.dupli_list_create(self.scene, settings='VIEWPORT')
                for dupli in obj.dupli_list:
                    self._add_sub_obj(dupli, matrix_world, vert_offsets, edge_offsets)
                obj.dupli_list_clear()
        
        return bbox
    
    def _add_origin(self, bm_copy, matrix):
        verts = bm_copy.verts
        v = verts.new(Vector())
        n = Vector((0,0,1))
        n = transform_point_normal(matrix, v.co, n)[1] # normals of loose vertices are not transformed by bmesh.transform
        v.normal = n
    
    def _add_bbox(self, bm_copy, bbox_mode, bbox, matrix):
        verts = bm_copy.verts
        edges = bm_copy.edges
        
        bbox_center = (bbox[1] + bbox[0]) * 0.5
        bbox_extents = (bbox[1] - bbox[0]) * 0.5
        
        def add_bbox_vert(x,y,z):
            v = verts.new(bbox_center+Vector((x*bbox_extents[0], y*bbox_extents[1], z*bbox_extents[2])))
            n = Vector((x,y,z)).normalized()
            if n.length_squared < 0.5: n = Vector((0,0,1))
            n = transform_point_normal(matrix, v.co, n)[1] # normals of loose vertices are not transformed by bmesh.transform
            v.normal = n
            return v
        
        if bbox_mode == 'FACES':
            bbox_matrix = matrix_compose(bbox_extents.x, bbox_extents.y, bbox_extents.z, bbox_center)
            bmesh.ops.create_cube(bm_copy, size=2.0, matrix=bbox_matrix)
        else:
            v000 = add_bbox_vert(-1,-1,-1)#verts.new(bbox_center-bbox_x-bbox_y-bbox_z)
            v100 = add_bbox_vert(+1,-1,-1)#verts.new(bbox_center+bbox_x-bbox_y-bbox_z)
            v010 = add_bbox_vert(-1,+1,-1)#verts.new(bbox_center-bbox_x+bbox_y-bbox_z)
            v110 = add_bbox_vert(+1,+1,-1)#verts.new(bbox_center+bbox_x+bbox_y-bbox_z)
            v001 = add_bbox_vert(-1,-1,+1)#verts.new(bbox_center-bbox_x-bbox_y+bbox_z)
            v101 = add_bbox_vert(+1,-1,+1)#verts.new(bbox_center+bbox_x-bbox_y+bbox_z)
            v011 = add_bbox_vert(-1,+1,+1)#verts.new(bbox_center-bbox_x+bbox_y+bbox_z)
            v111 = add_bbox_vert(+1,+1,+1)#verts.new(bbox_center+bbox_x+bbox_y+bbox_z)
            
            if bbox_mode == 'EDGES':
                edges.new((v000, v100))
                edges.new((v000, v010))
                edges.new((v000, v001))
                edges.new((v111, v011))
                edges.new((v111, v101))
                edges.new((v111, v110))
                edges.new((v100, v101))
                edges.new((v010, v011))
                edges.new((v001, v101))
                edges.new((v001, v011))
                edges.new((v100, v110))
                edges.new((v010, v110))
        
        add_bbox_vert(0,0,0)#verts.new(bbox_center)
        add_bbox_vert(+1,0,0)#verts.new(bbox_center+bbox_x)
        add_bbox_vert(-1,0,0)#verts.new(bbox_center-bbox_x)
        add_bbox_vert(0,+1,0)#verts.new(bbox_center+bbox_y)
        add_bbox_vert(0,-1,0)#verts.new(bbox_center-bbox_y)
        add_bbox_vert(0,0,+1)#verts.new(bbox_center+bbox_z)
        add_bbox_vert(0,0,-1)#verts.new(bbox_center-bbox_z)
        add_bbox_vert(-1,-1,0)#verts.new(bbox_center-bbox_x-bbox_y)
        add_bbox_vert(-1,+1,0)#verts.new(bbox_center-bbox_x+bbox_y)
        add_bbox_vert(+1,-1,0)#verts.new(bbox_center+bbox_x-bbox_y)
        add_bbox_vert(+1,+1,0)#verts.new(bbox_center+bbox_x+bbox_y)
        add_bbox_vert(-1,0,-1)#verts.new(bbox_center-bbox_x-bbox_z)
        add_bbox_vert(-1,0,+1)#verts.new(bbox_center-bbox_x+bbox_z)
        add_bbox_vert(+1,0,-1)#verts.new(bbox_center+bbox_x-bbox_z)
        add_bbox_vert(+1,0,+1)#verts.new(bbox_center+bbox_x+bbox_z)
        add_bbox_vert(0,-1,-1)#verts.new(bbox_center-bbox_y-bbox_z)
        add_bbox_vert(0,-1,+1)#verts.new(bbox_center-bbox_y+bbox_z)
        add_bbox_vert(0,+1,-1)#verts.new(bbox_center+bbox_y-bbox_z)
        add_bbox_vert(0,+1,+1)#verts.new(bbox_center+bbox_y+bbox_z)
    
    def _add_obj(self, obj):
        if not (obj and obj.name): return
        
        nv0 = len(self.bm.verts)
        ne0 = len(self.bm.edges)
        nf0 = len(self.bm.faces)
        
        vert_offsets = []
        edge_offsets = []
        bbox = self._add_sub_obj(obj, obj.matrix_world, vert_offsets, edge_offsets)
        
        nv1 = len(self.bm.verts)
        ne1 = len(self.bm.edges)
        nf1 = len(self.bm.faces)
        
        if nv1 == nv0: return
        
        obj_info = (obj.name, "", bbox)
        if (obj.type == 'ARMATURE') and self.geometry:
            i = nv0
            for di, bone_name in vert_offsets:
                i = nv0+di
                self._vert_to_obj.append((i, i+1, (obj.name, bone_name, bbox)))
                i += 2
            if (i < nv1-1): self._vert_to_obj.append((i, nv1-1, obj_info))
            
            i = ne0
            for di, bone_name in edge_offsets:
                i = ne0+di
                self._edge_to_obj.append((i, i, (obj.name, bone_name, bbox)))
                i += 1
            if (i < ne1-1): self._vert_to_obj.append((i, ne1-1, obj_info))
        else:
            self._vert_to_obj.append((nv0, nv1-1, obj_info))
            self._edge_to_obj.append((ne0, ne1-1, obj_info))
            self._face_to_obj.append((nf0, nf1-1, obj_info))

# =============================== SELECTION ================================ #
#============================================================================#
class Selection:
    def __init__(self, context=None, mode=None, elem_types=None, container=set, brute_force_update=False, pose_bones=True, copy_bmesh=False):
        self.context = context
        self.mode = mode
        self.elem_types = elem_types
        self.brute_force_update = brute_force_update
        self.pose_bones = pose_bones
        self.copy_bmesh = copy_bmesh
        # In some cases, user might want a hashable type (e.g. frozenset or tuple)
        self.container = container
        # We MUST keep reference to bmesh, or it will be garbage-collected
        self.bmesh = None
    
    def get_context(self):
        context = self.context or bpy.context
        mode = self.mode or context.mode
        active_obj = context.active_object
        actual_mode = BlEnums.mode_from_object(active_obj)
        mode = BlEnums.normalize_mode(mode, active_obj)
        if not BlEnums.is_mode_valid(mode, active_obj):
            mode = None # invalid request
        return context, active_obj, actual_mode, mode
    
    @property
    def normalized_mode(self):
        return self.get_context()[-1]
    
    @property
    def stateless_info(self):
        history, active, total = next(self.walk(), (None,None,0))
        active_id = active.name if hasattr(active, "name") else hash(active)
        return (total, active_id)
    
    @property
    def active(self):
        return next(self.walk(), (None,None))[1]
    @active.setter
    def active(self, value):
        self.update_active(value)
    
    @property
    def history(self):
        return next(self.walk(), (None,))[0]
    @history.setter
    def history(self, value):
        self.update_history(value)
    
    @property
    def selected(self):
        walker = self.walk()
        next(walker, None) # skip active item
        return dict(item for item in walker if item[1])
    @selected.setter
    def selected(self, value):
        self.update(value)
    
    def __iter__(self):
        walker = self.walk()
        next(walker, None) # skip active item
        for item in walker:
            if item[1]: yield item
    
    def __bool__(self):
        """Returns True if there is at least 1 element selected"""
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return False
        
        if mode == 'OBJECT':
            return bool(context.selected_objects)
        elif mode == 'EDIT_MESH':
            mesh = active_obj.data
            if actual_mode == 'EDIT_MESH':
                return bool(mesh.total_vert_sel)
            else:
                return any(item.select for item in mesh.vertices)
        elif mode in {'EDIT_CURVE', 'EDIT_SURFACE'}:
            for spline in active_obj.data.splines:
                for item in spline.bezier_points:
                    if (item.select_control_point or
                        item.select_left_handle or
                        item.select_right_handle):
                        return True
                for item in spline.points:
                    if item.select:
                        return True
        elif mode == 'EDIT_METABALL':
            return bool(active_obj.data.elements.active)
        elif mode == 'EDIT_LATTICE':
            return any(item.select for item in active_obj.data.points)
        elif mode == 'EDIT_ARMATURE':
            return any(item.select_head or item.select_tail
                       for item in active_obj.data.edit_bones)
        elif mode == 'POSE':
            return any(item.select for item in active_obj.data.bones)
        elif mode == 'PARTICLE':
            # Theoretically, particle keys can be selected,
            # but there seems to be no API for working with this
            pass
        else:
            pass # no selectable elements in other modes
        
        return False
    
    def walk(self):
        """Iterates over selection, returning (history, active, count) first, then (element, selected_attributes) until exhausted"""
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return
        
        container = self.container
        sel_map = {False: container(), True: container(("select",))}
        
        if mode != 'EDIT_MESH': self.bmesh = None
        
        if mode == 'OBJECT':
            total = len(context.selected_objects)
            item = active_obj
            yield ([], item, total)
            
            select = sel_map[True] # selected by definition
            for item in context.selected_objects:
                if not (item and item.name): return # object deleted (state disrupted)
                yield (item, select)
        elif mode == 'EDIT_MESH':
            mesh = active_obj.data
            elem_types = self.elem_types
            if actual_mode == 'EDIT_MESH':
                if self.copy_bmesh:
                    self.bmesh = bmesh.from_edit_mesh(mesh).copy()
                else:
                    if not (self.bmesh and self.bmesh.is_valid):
                        self.bmesh = bmesh.from_edit_mesh(mesh)
                bm = self.bmesh
                
                item = bm.faces.active
                
                if mesh.total_vert_sel == 0: # non-0 only in Edit mode
                    yield ([], item, 0)
                    return
                
                # No, by default all selected elements should be returned!
                #if not elem_types:
                #    elem_types = bm.select_mode
                
                colls = []
                if (not elem_types) or ('FACE' in elem_types):
                    colls.append(bm.faces)
                if (not elem_types) or ('EDGE' in elem_types):
                    colls.append(bm.edges)
                if (not elem_types) or ('VERT' in elem_types):
                    colls.append(bm.verts)
                
                total = sum(len(items) for items in colls)
                if bm.select_history:
                    yield (list(bm.select_history), item, total)
                else:
                    yield ([], item, total)
                
                for items in colls:
                    for item in items:
                        if not item.is_valid:
                            self.bmesh = None
                            return
                        yield (item, sel_map[item.select])
            else:
                self.bmesh = None
                
                colls = []
                if (not elem_types) or ('FACE' in elem_types):
                    colls.append(mesh.polygons)
                if (not elem_types) or ('EDGE' in elem_types):
                    colls.append(mesh.edges)
                if (not elem_types) or ('VERT' in elem_types):
                    colls.append(mesh.vertices)
                
                total = sum(len(items) for items in colls)
                item = None
                if mesh.polygons.active >= 0:
                    item = mesh.polygons[mesh.polygons.active]
                yield ([], item, total)
                
                for items in colls:
                    for item in items:
                        yield (item, sel_map[item.select])
        elif mode in {'EDIT_CURVE', 'EDIT_SURFACE'}:
            total = sum(len(spline.bezier_points) + len(spline.points)
                for spline in active_obj.data.splines)
            yield ([], None, total)
            
            bezier_sel_map = {
                (False, False, False): container(),
                (True, False, False): container(("select_left_handle",)),
                (False, True, False): container(("select_control_point",)),
                (False, False, True): container(("select_right_handle",)),
                (True, True, False): container(("select_left_handle", "select_control_point")),
                (False, True, True): container(("select_control_point", "select_right_handle")),
                (True, False, True): container(("select_left_handle", "select_right_handle")),
                (True, True, True): container(("select_left_handle", "select_control_point", "select_right_handle")),
            }
            
            # It seems like the only way the validity of spline can be determined
            # is to check if path_from_id() returns empty string.
            # However, it also seems that Blender does not crash when trying to
            # access deleted splines or theri points.
            for spline in active_obj.data.splines:
                for item in spline.bezier_points:
                    yield (item, bezier_sel_map[(item.select_left_handle, item.select_control_point, item.select_right_handle)])
                
                for item in spline.points:
                    yield (item, sel_map[item.select])
        elif mode == 'EDIT_METABALL':
            total = 1 # only active is known in current API
            item = active_obj.data.elements.active
            yield ([], item, total)
            
            # We don't even know if active element is actually selected
            # Just assume it is, to have at least some information
            #yield (item, container())
            yield (item, sel_map[True])
        elif mode == 'EDIT_LATTICE':
            total = len(active_obj.data.points)
            yield ([], None, total)
            
            for item in active_obj.data.points:
                yield (item, sel_map[item.select])
        elif mode == 'EDIT_ARMATURE':
            total = len(active_obj.data.edit_bones)
            item = active_obj.data.edit_bones.active
            yield ([], item, total)
            
            editbone_sel_map = {
                (False, False, False): container(),
                (True, False, False): container(("select_head",)),
                (False, True, False): container(("select",)),
                (False, False, True): container(("select_tail",)),
                (True, True, False): container(("select_head", "select")),
                (False, True, True): container(("select", "select_tail")),
                (True, False, True): container(("select_head", "select_tail")),
                (True, True, True): container(("select_head", "select", "select_tail")),
            }
            
            for item in active_obj.data.edit_bones:
                if not (item and item.name): return # object deleted (state disrupted)
                yield (item, editbone_sel_map[(item.select_head, item.select, item.select_tail)])
        elif mode == 'POSE':
            total = len(active_obj.data.bones)
            item = active_obj.data.bones.active
            
            if self.pose_bones:
                pose_bones = active_obj.pose.bones
                
                pb = (pose_bones.get(item.name) if item else None)
                yield ([], pb, total)
                
                for item in active_obj.data.bones:
                    if not (item and item.name): return # object deleted (state disrupted)
                    yield (pose_bones.get(item.name), sel_map[item.select])
            else:
                yield ([], item, total)
                
                for item in active_obj.data.bones:
                    if not (item and item.name): return # object deleted (state disrupted)
                    yield (item, sel_map[item.select])
        elif mode == 'PARTICLE':
            # Theoretically, particle keys can be selected,
            # but there seems to be no API for working with this
            pass
        else:
            pass # no selectable elements in other modes
    
    def update_active(self, item):
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return
        
        if mode == 'OBJECT':
            context.scene.objects.active = item
        elif mode == 'EDIT_MESH':
            mesh = active_obj.data
            if actual_mode == 'EDIT_MESH':
                bm = self.bmesh or bmesh.from_edit_mesh(mesh)
                self.bmesh = bm
                bm.faces.active = item
            else:
                mesh.polygons.active = (item.index if item else -1)
        elif mode in {'EDIT_CURVE', 'EDIT_SURFACE'}:
            pass # no API for active element
        elif mode == 'EDIT_METABALL':
            active_obj.data.elements.active = item
        elif mode == 'EDIT_LATTICE':
            pass # no API for active element
        elif mode == 'EDIT_ARMATURE':
            active_obj.data.edit_bones.active = item
        elif mode == 'POSE':
            if item: item = active_obj.data.bones.get(item.name)
            active_obj.data.bones.active = item
        elif mode == 'PARTICLE':
            # Theoretically, particle keys can be selected,
            # but there seems to be no API for working with this
            pass
        else:
            pass # no selectable elements in other modes
    
    def update_history(self, history):
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return
        
        if mode == 'EDIT_MESH':
            mesh = active_obj.data
            if actual_mode == 'EDIT_MESH':
                bm = self.bmesh or bmesh.from_edit_mesh(mesh)
                self.bmesh = bm
                
                bm.select_history.clear()
                for item in history:
                    bm.select_history.add(item)
                #bm.select_history.validate()
            else:
                pass # history not supported
        else:
            pass # history not supported
    
    def __update_strategy(self, is_actual_mode, data, expr_info):
        # We use select_all(action) only when the context is right
        # and iterating over all objects can be avoided.
        select_all_action = None
        if not is_actual_mode: return select_all_action, data
        
        operation, new_toggled, invert_new, old_toggled, invert_old = expr_info
        
        # data = {} translates to "no exceptions"
        if operation == 'SET':
            if new_toggled is False:
                select_all_action = 'DESELECT'
                data = {} # False --> False
            elif new_toggled is True:
                select_all_action = 'SELECT'
                data = {} # True --> True
            elif invert_new:
                select_all_action = 'SELECT'
            else:
                select_all_action = 'DESELECT'
        elif operation == 'OR':
            if new_toggled is False:
                if old_toggled is False:
                    select_all_action = 'DESELECT'
                    data = {} # False OR False --> False
                elif old_toggled is True:
                    select_all_action = 'SELECT'
                    data = {} # True OR False --> True
                else:
                    data = {} # x OR False --> x
            elif new_toggled is True:
                select_all_action = 'SELECT'
                data = {} # x OR True --> True
            elif invert_new:
                pass # need to iterate over all objects anyway
            else:
                if invert_old:
                    select_all_action = 'INVERT'
                else:
                    select_all_action = '' # use data, but no select_all
        elif operation == 'AND':
            if new_toggled is False:
                select_all_action = 'DESELECT'
                data = {} # x AND False --> False
            elif new_toggled is True:
                if old_toggled is False:
                    select_all_action = 'DESELECT'
                    data = {} # False AND False --> False
                elif old_toggled is True:
                    select_all_action = 'DESELECT'
                    data = {} # True AND False --> False
                else:
                    data = {} # x AND True --> x
            elif invert_new:
                if invert_old:
                    select_all_action = 'INVERT'
                else:
                    select_all_action = '' # use data, but no select_all
            else:
                pass # need to iterate over all objects anyway
        elif operation == 'XOR':
            if new_toggled is False:
                if old_toggled is False:
                    select_all_action = 'DESELECT'
                    data = {} # False != False --> False
                elif old_toggled is True:
                    select_all_action = 'SELECT'
                    data = {} # True != False --> True
            elif new_toggled is True:
                if old_toggled is False:
                    select_all_action = 'SELECT'
                    data = {} # False != True --> True
                elif old_toggled is True:
                    select_all_action = 'DESELECT'
                    data = {} # True != True --> False
            elif invert_new:
                pass # need to iterate over all objects anyway
            else:
                pass # need to iterate over all objects anyway
        
        return select_all_action, data
    
    def __update_make_selector_expression(self, name, use_kv, expr_info):
        operation, new_toggled, invert_new, old_toggled, invert_old = expr_info
        
        data_code = ("value" if use_kv else "data.get(item, '')")
        
        if new_toggled is not None:
            code_new = repr(new_toggled)
        elif invert_new:
            code_new = "({} not in {})".format(repr(name), data_code)
        else:
            code_new = "({} in {})".format(repr(name), data_code)
        
        if old_toggled is not None:
            code_old = repr(old_toggled)
        elif invert_old:
            code_old = "(not item.{})".format(name)
        else:
            code_old = "item.{}".format(name)
        
        if operation == 'OR':
            code = "{} or {}".format(code_old, code_new)
        elif operation == 'AND':
            code = "{} and {}".format(code_old, code_new)
        elif operation == 'XOR':
            code = "{} != {}".format(code_old, code_new)
        else:
            code = code_new # SET
        
        return "item.{0} = ({1})".format(name, code)
    
    def __update_make_selector(self, build_infos, expr_info):
        tab = "    "
        expr_maker = self.__update_make_selector_expression
        localvars = {"isinstance":isinstance}
        type_cnt = 0
        lines = []
        for i, build_info in enumerate(build_infos):
            use_kv = build_info.get("use_kv", False)
            item_map = build_info.get("item_map", None)
            type_names = build_info["names"]
            
            expr_tab = tab*2
            
            if item_map: lines.append(tab + "item_map = {}".format(item_map))
            
            if use_kv:
                lines.append(tab + "for item, value in args[{}].items():".format(i))
                lines.append(expr_tab + "if not item: continue")
            else:
                lines.append(tab + "for item in args[{}]:".format(i))
            
            if item_map:
                lines.append(expr_tab + "item = item_map.get(item.name)")
                lines.append(expr_tab + "if not item: continue")
            
            if len(type_names) < 2:
                item_type, names = type_names[0]
                if (not use_kv) and (len(names) > 1):
                    lines.append(expr_tab + "value = data.get(item, '')")
                    use_kv = True
                for name in names:
                    lines.append(expr_tab + expr_maker(name, use_kv, expr_info))
            else:
                tab_if = expr_tab
                expr_tab += tab
                j = 0
                for item_type, names in type_names:
                    j += 1
                    type_name = "type{}".format(type_cnt)
                    type_cnt += 1
                    localvars[type_name] = item_type
                    if j == 1:
                        lines.append(tab_if + "if isinstance(item, {}):".format(type_name))
                    elif j < len(type_names):
                        lines.append(tab_if + "elif isinstance(item, {}):".format(type_name))
                    else:
                        lines.append(tab_if + "else:")
                    
                    for name in names:
                        lines.append(expr_tab + expr_maker(name, use_kv, expr_info))
        
        code = "def apply(*args, data=None, context=None):\n{}".format("\n".join(lines))
        #print(code.strip())
        
        exec(code, localvars, localvars)
        return localvars["apply"]
    
    __cached_selectors = {}
    
    def update(self, data, operation='SET'):
        if not isinstance(data, dict):
            raise ValueError("data must be a dict")
        
        toggle_old = operation.startswith("^")
        invert_old = operation.startswith("!")
        toggle_new = operation.endswith("^")
        invert_new = operation.endswith("!")
        operation = operation.replace("!", "").replace("^", "")
        
        if operation not in {'SET', 'OR', 'AND', 'XOR'}:
            raise ValueError("operation must be one of {'SET', 'OR', 'AND', 'XOR'}")
        
        context, active_obj, actual_mode, mode = self.get_context()
        if not mode: return
        
        new_toggled = (not any(data.values()) if toggle_new else None)
        old_toggled = (not bool(self) if toggle_old else None)
        
        expr_info = (operation, new_toggled, invert_new, old_toggled, invert_old)
        
        is_actual_mode = (mode == actual_mode)
        if self.brute_force_update:
            select_all_action = None
        else:
            select_all_action, data = self.__update_strategy(is_actual_mode, data, expr_info)
        #print("Strategy: action={}, data={}".format(repr(select_all_action), bool(data)))
        use_brute_force = select_all_action is None
        
        def make_selector(*build_infos):
            selector_key = (mode, is_actual_mode, use_brute_force, expr_info)
            selector = Selection.__cached_selectors.get(selector_key)
            #print(selector_key)
            if selector is None:
                selector = self.__update_make_selector(build_infos, expr_info)
                Selection.__cached_selectors[selector_key] = selector
            #print(selector)
            return selector
        
        if mode == 'OBJECT':
            if select_all_action:
                bpy.ops.object.select_all(action=select_all_action)
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select"])]})
                selector(context.scene.objects, data=data)
            else:
                selector = make_selector({"names":[(None, ["select"])], "use_kv":True})
                selector(data)
        elif mode == 'EDIT_MESH':
            if select_all_action:
                bpy.ops.mesh.select_all(action=select_all_action)
            
            mesh = active_obj.data
            if is_actual_mode:
                bm = self.bmesh or bmesh.from_edit_mesh(mesh)
                self.bmesh = bm
                faces, edges, verts = bm.faces, bm.edges, bm.verts
            else:
                faces, edges, verts = mesh.polygons, mesh.edges, mesh.vertices
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select"])]})
                selector(faces, data=data)
                selector(edges, data=data)
                selector(verts, data=data)
            else:
                selector = make_selector({"names":[(None, ["select"])], "use_kv":True})
                selector(data)
            
            if is_actual_mode:
                #bm.select_flush(True) # ?
                #bm.select_flush(False) # ?
                #bm.select_flush_mode() # ?
                pass
        elif mode in {'EDIT_CURVE', 'EDIT_SURFACE'}:
            if select_all_action:
                bpy.ops.curve.select_all(action=select_all_action)
            
            bezier_names = (bpy.types.BezierSplinePoint, ["select_control_point", "select_left_handle", "select_right_handle"])
            if use_brute_force:
                selector = make_selector({"names":[bezier_names]}, {"names":[(None, ["select"])]})
                for spline in active_obj.data.splines:
                    selector(spline.bezier_points, spline.points, data=data)
            else:
                selector = make_selector({"names":[bezier_names, (None, ["select"])], "use_kv":True})
                selector(data)
        elif mode == 'EDIT_METABALL':
            if select_all_action:
                bpy.ops.mball.select_all(action=select_all_action)
            # Otherwise, we can't do anything with current API
        elif mode == 'EDIT_LATTICE':
            if select_all_action:
                bpy.ops.lattice.select_all(action=select_all_action)
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select"])]})
                selector(active_obj.data.points, data=data)
            else:
                selector = make_selector({"names":[(None, ["select"])], "use_kv":True})
                selector(data)
        elif mode == 'EDIT_ARMATURE':
            if select_all_action:
                bpy.ops.armature.select_all(action=select_all_action)
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select_head", "select", "select_tail"])]})
                selector(active_obj.data.edit_bones, data=data)
            else:
                selector = make_selector({"names":[(None, ["select_head", "select", "select_tail"])], "use_kv":True})
                selector(data)
        elif mode == 'POSE':
            if select_all_action:
                bpy.ops.pose.select_all(action=select_all_action)
            
            if use_brute_force:
                selector = make_selector({"names":[(None, ["select"])], "item_map":"context.data.bones"})
                selector(active_obj.data.bones, data=data, context=active_obj)
            else:
                selector = make_selector({"names":[(None, ["select"])], "item_map":"context.data.bones", "use_kv":True})
                selector(data, context=active_obj)
        elif mode == 'PARTICLE':
            if select_all_action:
                bpy.ops.particle.select_all(action=select_all_action)
            # Theoretically, particle keys can be selected,
            # but there seems to be no API for working with this
        else:
            pass # no selectable elements in other modes

class SelectionSnapshot:
    # The goal of SelectionSnapshot is to leave as little side-effects as possible,
    # so brute_force_update=True (since select_all operators are recorded in the info log)
    def __init__(self, context=None, brute_force_update=True):
        sel = Selection(context, brute_force_update=brute_force_update)
        self.snapshot_curr = (sel, sel.active, sel.history, sel.selected)
        
        self.mode = sel.normalized_mode
        if self.mode == 'OBJECT':
            self.snapshot_obj = self.snapshot_curr
        else:
            sel = Selection(context, 'OBJECT', brute_force_update=brute_force_update)
            self.snapshot_obj = (sel, sel.active, sel.history, sel.selected)
    
    # Attention: it is assumed that there was no Undo,
    # objects' modes didn't change, and all elements are still valid
    def restore(self):
        if self.mode != 'OBJECT':
            sel, active, history, selected = self.snapshot_obj
            sel.selected = selected
            sel.history = history
            sel.active = active
        
        sel, active, history, selected = self.snapshot_curr
        sel.selected = selected
        sel.history = history
        sel.active = active
    
    def __str__(self):
        if self.mode != 'OBJECT':
            return str({'OBJECT':self.snapshot_obj[1:], self.mode:self.snapshot_curr[1:]})
        else:
            return str({'OBJECT':self.snapshot_obj[1:]})
    
    def __enter__(self):
        pass
    
    def __exit__(self, type, value, traceback):
        self.restore()

def IndividuallyActiveSelected(objects, context=None, make_visble=False):
    if context is None: context = bpy.context
    
    prev_selection = SelectionSnapshot(context)
    sel, active, history, selected = prev_selection.snapshot_obj
    
    sel.selected = {}
    
    scene = context.scene
    scene_objects = scene.objects
    
    all_layers = (True,) * len(scene.layers)
    
    for obj in objects:
        try:
            scene_objects.active = obj
            obj.select = True
        except Exception as exc:
            continue # for some reason object doesn't exist anymore
        
        if make_visble:
            prev_hide = obj.hide
            prev_layers = tuple(obj.layers)
            obj.hide = False
            obj.layers = all_layers
        
        yield obj
        
        if make_visble:
            obj.hide = prev_hide
            obj.layers = prev_layers
        
        obj.select = False
    
    prev_selection.restore()

class ResumableSelection:
    def __init__(self, *args, **kwargs):
        kwargs["copy_bmesh"] = True # seems like this is REQUIRED to avoid crashes
        self.selection = Selection(*args, **kwargs)
        self.selection_walker = None
        self.selection_initialized = False
        self.selection_total = 0
        self.selection_count = 0
        
        # Screen change doesn't actually invalidate the selection,
        # but it's a big enough change to justify the extra wait.
        # I added it to make batch-transform a bit more efficient.
        self.mode = None
        self.obj_hash = None
        self.screen_hash = None
        self.scene_hash = None
        self.undo_hash = None
        self.operators_len = None
        self.objects_len = None
        self.objects_selected_len = None
    
    def __call__(self, duration=0):
        if duration is None: duration = float("inf")
        context = bpy.context
        wm = context.window_manager
        screen = context.screen
        scene = context.scene
        active_obj = context.object
        mode = context.mode
        obj_hash = (active_obj.as_pointer() if active_obj else 0)
        screen_hash = screen.as_pointer()
        scene_hash = scene.as_pointer()
        undo_hash = bpy.data.as_pointer()
        operators_len = len(wm.operators)
        objects_len = len(scene.objects)
        objects_selected_len = len(context.selected_objects)
        
        object_updated = False
        if active_obj and ('EDIT' in active_obj.mode):
            object_updated |= (active_obj.is_updated or active_obj.is_updated_data)
            data = active_obj.data
            if data: object_updated |= (data.is_updated or data.is_updated_data)
            
            # ATTENTION: inside mesh editmode, undo/redo DOES NOT affect
            # the rest of the blender objects, so pointers/hashes don't change.
            if mode == 'EDIT_MESH':
                bm = self.selection.bmesh
                object_updated |= (bm is None) or (not bm.is_valid)
        
        reset = object_updated
        reset |= (self.mode != mode)
        reset |= (self.obj_hash != obj_hash)
        reset |= (self.screen_hash != screen_hash)
        reset |= (self.scene_hash != scene_hash)
        reset |= (self.undo_hash != undo_hash)
        reset |= (self.operators_len != operators_len)
        #reset |= (self.objects_len != objects_len)
        reset |= (self.objects_selected_len != objects_selected_len)
        if reset:
            self.mode = mode
            self.obj_hash = obj_hash
            self.screen_hash = screen_hash
            self.scene_hash = scene_hash
            self.undo_hash = undo_hash
            self.operators_len = operators_len
            self.objects_len = objects_len
            self.objects_selected_len = objects_selected_len
            
            self.selection.bmesh = None
            self.selection_walker = None
        
        clock = time.clock
        time_stop = clock() + duration
        
        if self.selection_walker is None:
            self.selection.bmesh = None
            self.selection_walker = self.selection.walk()
            self.selection_initialized = False
            self.selection_total = 0
            self.selection_count = 0
            yield (-2, None) # RESET
            if clock() > time_stop: return
        
        if not self.selection_initialized:
            item = next(self.selection_walker, None)
            if item: # can be None if active mode does not support selections
                history, active, total = item
                if mode == 'EDIT_MESH': active = (history[-1] if history else None)
                self.selection_initialized = True
                self.selection_total = total
                yield (0, active) # ACTIVE
                if clock() > time_stop: return
        
        for item in self.selection_walker:
            self.selection_count += 1
            if item[1]: yield (1, item[0]) # SELECTED
            if clock() > time_stop: break
        else: # the iterator is exhausted
            self.selection.bmesh = None
            self.selection_walker = None
            yield (-1, None) # FINISHED
    
    RESET = -2
    FINISHED = -1
    ACTIVE = 0
    SELECTED = 1

# ============================ CHANGE MONITOR ============================== #
#============================================================================#
class ChangeMonitor:
    reports_cleanup_trigger = 512
    reports_cleanup_count = 128
    max_evaluation_time = 0.002
    
    def __init__(self, context=None, update=True, **kwargs):
        if not context: context = bpy.context
        wm = context.window_manager
        
        self.selection = Selection(container=frozenset)
        
        self.mode = None
        self.active_obj = None
        self.selection_walker = None
        self.selection_recorded = False
        self.selection_recorder = []
        self.selection_record_id = 0
        self.scene_hash = 0
        self.undo_hash = 0
        self.operators_len = 0
        self.reports = []
        self.reports_len = 0
        
        if update: self.update(context, **kwargs)
        
        self.mode_changed = False
        self.active_obj_changed = False
        self.selection_changed = False
        self.scene_changed = False
        self.undo_performed = False
        self.object_updated = False
        self.operators_changed = 0
        self.reports_changed = 0
    
    def get_reports(self, context=None, **kwargs):
        if not context: context = bpy.context
        wm = context.window_manager
        
        area = kwargs.get("area") or context.area
        
        try:
            prev_clipboard = wm.clipboard
        except UnicodeDecodeError as exc:
            #print(exc)
            prev_clipboard = ""
        
        prev_type = area.type
        if prev_type != 'INFO':
            area.type = 'INFO'
        
        try:
            bpy.ops.info.report_copy(kwargs)
            if wm.clipboard: # something was selected
                bpy.ops.info.select_all_toggle(kwargs) # something is selected: deselect all
                #bpy.ops.info.reports_display_update(kwargs)
            bpy.ops.info.select_all_toggle(kwargs) # nothing is selected: select all
            #bpy.ops.info.reports_display_update(kwargs)
            
            bpy.ops.info.report_copy(kwargs)
            reports = wm.clipboard.splitlines()
            
            bpy.ops.info.select_all_toggle(kwargs) # deselect everything
            #bpy.ops.info.reports_display_update(kwargs)
            
            if len(reports) >= self.reports_cleanup_trigger:
                for i in range(self.reports_cleanup_count):
                    bpy.ops.info.select_pick(kwargs, report_index=i)
                    #bpy.ops.info.reports_display_update(kwargs)
                bpy.ops.info.report_delete(kwargs)
                #bpy.ops.info.reports_display_update(kwargs)
        except Exception as exc:
            #print(exc)
            reports = []
        
        if prev_type != 'INFO':
            area.type = prev_type
        
        wm.clipboard = prev_clipboard
        
        return reports
    
    something_changed = property(lambda self:
        self.mode_changed or
        self.active_obj_changed or
        self.selection_changed or
        self.scene_changed or
        self.undo_performed or
        self.object_updated or
        bool(self.operators_changed) or
        bool(self.reports_changed)
    )
    
    def hash(self, obj):
        if obj is None: return 0
        if hasattr(obj, "as_pointer"): return obj.as_pointer()
        return hash(obj)
    
    def update(self, context=None, **kwargs):
        if not context: context = bpy.context
        wm = context.window_manager
        
        self.mode_changed = False
        self.active_obj_changed = False
        self.selection_changed = False
        self.scene_changed = False
        self.undo_performed = False
        self.object_updated = False
        self.operators_changed = 0
        self.reports_changed = 0
        
        mode = kwargs.get("mode") or context.mode
        active_obj = kwargs.get("object") or context.object
        scene = kwargs.get("scene") or context.scene
        
        if (self.mode != mode):
            self.mode = mode
            self.mode_changed = True
        
        if (self.active_obj != active_obj):
            self.active_obj = active_obj
            self.active_obj_changed = True
        
        scene_hash = self.hash(scene)
        if (self.scene_hash != scene_hash):
            self.scene_hash = scene_hash
            self.scene_changed = True
        
        undo_hash = self.hash(bpy.data)
        if (self.undo_hash != undo_hash):
            self.undo_hash = undo_hash
            self.undo_performed = True
        
        if active_obj and ('EDIT' in active_obj.mode):
            if active_obj.is_updated or active_obj.is_updated_data:
                self.object_updated = True
            data = active_obj.data
            if data and (data.is_updated or data.is_updated_data):
                self.object_updated = True
            
            # ATTENTION: inside mesh editmode, undo/redo DOES NOT affect
            # the rest of the blender objects, so pointers/hashes don't change.
            if (mode == 'EDIT_MESH') and (self.selection.bmesh is not None):
                object_updated |= (not self.selection.bmesh.is_valid)
        
        operators_len = len(wm.operators)
        if (operators_len != self.operators_len):
            self.operators_changed = operators_len - self.operators_len
            self.operators_len = operators_len
        else: # maybe this would be a bit safer?
            reports = self.get_reports(context, **kwargs) # sometimes this causes Blender to crash
            reports_len = len(reports)
            if (reports_len != self.reports_len):
                self.reports_changed = reports_len - self.reports_len
                self.reports = reports
                self.reports_len = reports_len
        
        self.analyze_selection()
    
    def reset_selection(self):
        self.selection.bmesh = None
        self.selection_walker = None
        self.selection_recorded = False
        self.selection_recorder = []
        self.selection_record_id = 0
    
    def analyze_selection(self):
        reset_selection = self.mode_changed
        reset_selection |= self.active_obj_changed
        reset_selection |= self.scene_changed
        reset_selection |= self.undo_performed
        reset_selection |= self.object_updated
        reset_selection |= self.operators_changed
        reset_selection |= self.reports_changed
        if reset_selection:
            #print("Selection reseted for external reasons")
            self.reset_selection()
            # At this point we have no idea if the selection
            # has actually changed. This is more of a warning
            # about a potential change of selection.
            self.selection_changed = True
        
        if self.selection_walker is None:
            self.selection.bmesh = None
            self.selection_walker = self.selection.walk()
        
        clock = time.clock()
        hash = self.hash
        
        if self.selection_recorded:
            time_stop = clock() + self.max_evaluation_time
            
            if self.selection_record_id == 0:
                item = next(self.selection_walker, None)
                history, active, total = item
                item = tuple(hash(h) for h in history), hash(active), total
                self.selection_record_id = 1
                if self.selection_recorder[0] != item:
                    #print("Active/history/total changed")
                    self.selection_changed = True
                    self.reset_selection()
                    return
            
            recorded_count = len(self.selection_recorder)
            for item in self.selection_walker:
                if item[1]:
                    item = hash(item[0]), item[1]
                    i = self.selection_record_id
                    if (i >= recorded_count) or (self.selection_recorder[i] != item):
                        #print("More than necessary or selection changed")
                        self.selection_changed = True
                        self.reset_selection()
                        return
                    self.selection_record_id = i + 1
                if clock() > time_stop: break
            else: # the iterator is exhausted
                if self.selection_record_id < recorded_count:
                    #print("Less than necessary")
                    self.selection_changed = True
                    self.reset_selection()
                    return
                self.selection.bmesh = None
                self.selection_walker = None
                self.selection_record_id = 0
        else:
            time_stop = clock() + self.max_evaluation_time
            
            if self.selection_record_id == 0:
                item = next(self.selection_walker, None)
                history, active, total = item
                item = tuple(hash(h) for h in history), hash(active), total
                self.selection_record_id = 1
                self.selection_recorder.append(item) # first item is special
            
            for item in self.selection_walker:
                if item[1]:
                    item = hash(item[0]), item[1]
                    self.selection_recorder.append(item)
                if clock() > time_stop: break
            else: # the iterator is exhausted
                self.selection.bmesh = None
                self.selection_walker = None
                self.selection_recorded = True
                self.selection_record_id = 0

# ============================= BLENDER UTILS ============================== #
#============================================================================#
class BlUtil:
    class Object:
        @staticmethod
        def layers_intersect(a, b, name_a="layers", name_b=None):
            return any(l0 and l1 for l0, l1 in zip(getattr(a, name_a), getattr(b, name_b or name_a)))
        
        @staticmethod
        def iterate(search_in, context=None, obj_types=None):
            if context is None: context = bpy.context
            scene = context.scene
            if search_in == 'SELECTION':
                for obj in context.selected_objects:
                    if ((obj_types is None) or (obj.type in obj_types)):
                        yield obj
            elif search_in == 'VISIBLE':
                for obj in scene.objects:
                    if ((obj_types is None) or (obj.type in obj_types)) and obj.is_visible(scene):
                        yield obj
            elif search_in == 'LAYER':
                layers_intersect = BlUtil.Object.layers_intersect
                for obj in scene.objects:
                    if ((obj_types is None) or (obj.type in obj_types)) and layers_intersect(obj, scene):
                        yield obj
            elif search_in == 'SCENE':
                for obj in scene.objects:
                    if ((obj_types is None) or (obj.type in obj_types)):
                        yield obj
            elif search_in == 'FILE':
                for obj in bpy.data.objects:
                    if ((obj_types is None) or (obj.type in obj_types)):
                        yield obj
        
        @staticmethod
        def rotation_convert(src_mode, q, aa, e, dst_mode, always4=False):
            if src_mode == dst_mode: # and coordsystem is 'BASIS'
                if src_mode == 'QUATERNION':
                    R = Quaternion(q)
                elif src_mode == 'AXIS_ANGLE':
                    R = Vector(aa)
                else:
                    R = Euler(e)
            else:
                if src_mode == 'QUATERNION':
                    R = Quaternion(q)
                elif src_mode == 'AXIS_ANGLE':
                    R = Quaternion(aa[1:], aa[0])
                else:
                    R = Euler(e).to_quaternion()
                
                if dst_mode == 'QUATERNION':
                    pass # already quaternion
                elif dst_mode == 'AXIS_ANGLE':
                    R = R.to_axis_angle()
                    R = Vector((R[1], R[0].x, R[0].y, R[0].z))
                else:
                    R = R.to_euler(dst_mode)
            
            if always4:
                if len(R) == 4: R = Vector(R)
                else: R = Vector((0.0, R[0], R[1], R[2]))
            
            return R
        
        @staticmethod
        def rotation_apply(obj, R, mode):
            if (len(R) == 4) and (mode not in ('QUATERNION', 'AXIS_ANGLE')): R = R[1:]
            
            if obj.rotation_mode == mode: # and coordsystem is 'BASIS'
                if mode == 'QUATERNION':
                    obj.rotation_quaternion = Quaternion(R)
                elif mode == 'AXIS_ANGLE':
                    obj.rotation_axis_angle = tuple(R)
                else:
                    obj.rotation_euler = Euler(R)
            else:
                if mode == 'QUATERNION':
                    R = Quaternion(R)
                elif mode == 'AXIS_ANGLE':
                    R = Quaternion(R[1:], R[0])
                else:
                    R = Euler(R).to_quaternion()
                R.normalize()
                
                if obj.rotation_mode == 'QUATERNION':
                    obj.rotation_quaternion = R
                elif obj.rotation_mode == 'AXIS_ANGLE':
                    R = R.to_axis_angle()
                    R = Vector((R[1], R[0].x, R[0].y, R[0].z))
                    obj.rotation_axis_angle = R
                else:
                    R = R.to_euler(obj.rotation_mode)
                    obj.rotation_euler = R
        
        @staticmethod
        def vertex_location(obj, i, undeformed=False):
            if (not obj) or (i < 0): return Vector()
            if obj.type == 'MESH':
                if (i >= len(obj.data.vertices)): return Vector()
                v = obj.data.vertices[i]
                return Vector(v.undeformed_co if undeformed else v.co)
            elif obj.type in ('CURVE', 'SURFACE'):
                for spline in obj.data.splines:
                    points = (spline.bezier_points if spline.type == 'BEZIER' else spline.points)
                    if i >= len(points):
                        i -= len(points)
                    else:
                        return Vector(points[i].co)
                return Vector()
            elif obj.type == 'LATTICE':
                if (i >= len(obj.data.points)): return Vector()
                p = obj.data.points[i]
                return Vector(v.co if undeformed else v.co_deform)
            else:
                return Vector()
        
        @staticmethod
        def matrix_world(obj, bone_name=""):
            if not obj: return Matrix()
            if bone_name:
                obj = obj.id_data
                if obj.type == 'ARMATURE':
                    bone = obj.pose.bones.get(bone_name)
                    if bone: return obj.matrix_world * bone.matrix
                return obj.matrix_world
            elif hasattr(obj, "matrix_world"):
                return Matrix(obj.matrix_world)
            else:
                bone = obj
                obj = bone.id_data
                return obj.matrix_world * bone.matrix
        
        @staticmethod
        def matrix_world_set(obj, m):
            if not obj: return
            if hasattr(obj, "matrix_world"):
                obj.matrix_world = Matrix(m)
            else:
                bone = obj
                obj = bone.id_data
                bone.matrix = matrix_inverted_safe(obj.matrix_world) * m
        
        @staticmethod
        def matrix_parent(obj):
            if not obj: return Matrix()
            parent = obj.parent
            if not parent: return Matrix()
            
            parent_type = getattr(obj, "parent_type", 'OBJECT')
            if parent_type == 'BONE': # NOT TESTED
                parent_bone = parent.pose.bones.get(obj.parent_bone)
                if not parent_bone: return BlUtil.Object.matrix_world(parent)
                return BlUtil.Object.matrix_world(parent_bone)
            elif parent_type == 'VERTEX': # NOT TESTED
                v = BlUtil.Object.vertex_location(parent, obj.parent_vertices[0])
                return Matrix.Translation(BlUtil.Object.matrix_world(parent) * v)
            elif parent_type == 'VERTEX_3': # NOT TESTED
                pm = BlUtil.Object.matrix_world(parent)
                v0 = pm * BlUtil.Object.vertex_location(parent, obj.parent_vertices[0])
                v1 = pm * BlUtil.Object.vertex_location(parent, obj.parent_vertices[1])
                v2 = pm * BlUtil.Object.vertex_location(parent, obj.parent_vertices[2])
                t = v0
                x = (v1 - v0).normalized()
                y = (v2 - v0).normalized()
                z = x.cross(y).normalized()
                return matrix_compose(x, y, z, t)
            else:
                # I don't know how CURVE and KEY are supposed to behave,
                # so for now I just treat them the same as OBJECT/ARMATURE.
                # LATTICE isn't a rigid-body/affine transformation either.
                return BlUtil.Object.matrix_world(parent)
        
        @staticmethod
        def parents(obj, include_this=False):
            if not obj: return
            if include_this: yield obj
            parent = obj.parent
            while parent:
                yield parent
                parent = parent.parent
        
        @staticmethod
        def iter_bone_info(obj):
            data = obj.data
            if obj.mode == 'EDIT':
                for bone in data.edit_bones:
                    yield (bone, (bone.select, bone.select_head, bone.select_tail))
            else:
                for bone in obj.pose.bones:
                    _bone = bone.bone #data.bones[bone.name] # equivalent
                    yield (bone, (_bone.select, _bone.select_head, _bone.select_tail))
        
        @staticmethod
        def bounding_box(obj):
            def bbox_add(bbox, p):
                b0, b1 = bbox
                if b0:
                    b0.x = min(b0.x, p.x)
                    b0.y = min(b0.y, p.y)
                    b0.z = min(b0.z, p.z)
                    b1.x = max(b1.x, p.x)
                    b1.y = max(b1.y, p.y)
                    b1.z = max(b1.z, p.z)
                else:
                    bbox[0] = Vector(p)
                    bbox[1] = Vector(p)
            
            if obj.type == 'ARMATURE':
                bbox = [None, None] # Blender does not return valid bbox for armature
                for bone, selected in BlUtil.Object.iter_bone_info(obj):
                    bbox_add(bbox, bone.head)
                    bbox_add(bbox, bone.tail)
                bbox = (bbox[0] or Vector(), bbox[1] or Vector())
            elif obj.type == 'LATTICE':
                bbox = [None, None] # Blender does not return valid bbox for lattice
                for point in obj.data.points:
                    bbox_add(bbox, point.co_deform)
                bbox = (bbox[0] or Vector(), bbox[1] or Vector())
            else:
                bbox = (Vector(obj.bound_box[0]), Vector(obj.bound_box[-2]))
            
            return bbox
        
        @staticmethod
        def instantiate_duplis(obj, scene=None, settings='VIEWPORT', depth=-1):
            if (not obj) or (obj.dupli_type == 'NONE'): return
            if not scene: scene = bpy.context.scene
            
            if depth == 0: return
            if depth > 0: depth -= 1
            
            filter = None
            if obj.dupli_type in ('VERTS', 'FACES'):
                filter = set(obj.children)
            elif (obj.dupli_type == 'GROUP') and obj.dupli_group:
                filter = set(obj.dupli_group.objects)
            
            roots = []
            if obj.dupli_list: obj.dupli_list_clear()
            obj.dupli_list_create(scene, settings)
            for dupli in obj.dupli_list:
                if (not filter) or (dupli.object in filter):
                    roots.append((dupli.object, Matrix(dupli.matrix)))
            obj.dupli_list_clear()
            
            dupli_type = obj.dupli_type
            # Prevent recursive copying in FRAMES dupli mode
            obj.dupli_type = 'NONE'
            
            dst_info = []
            src_dst = {}
            for src_obj, matrix in roots:
                dst_obj = src_obj.copy()
                dst_obj.constraints.clear()
                scene.objects.link(dst_obj)
                if dupli_type == 'FRAMES':
                    dst_obj.animation_data_clear()
                dst_info.append((dst_obj, src_obj, matrix))
                src_dst[src_obj] = dst_obj
            
            scene.update() # <-- important
            
            for dst_obj, src_obj, matrix in dst_info:
                dst_parent = src_dst.get(src_obj.parent)
                if dst_parent:
                    # parent_type, parent_bone, parent_vertices
                    # should be copied automatically
                    dst_obj.parent = dst_parent
                else:
                    dst_obj.parent_type = 'OBJECT'
                    dst_obj.parent = obj
            
            for dst_obj, src_obj, matrix in dst_info:
                dst_obj.matrix_world = matrix
            
            for dst_obj, src_obj, matrix in dst_info:
                BlUtil.Object.instantiate_duplis(dst_obj, scene, settings, depth)
    
    class Scene:
        @staticmethod
        def cursor(context):
            if context:
                container = getattr(context, "space_data", None)
                if (not container) or (container.type != 'VIEW_3D'): container = context.scene
            else: # make sure we deal with global cursor
                container = bpy.context.scene
            
            return Vector(container.cursor_location)
        
        @staticmethod
        def cursor_set(context, value, force=True):
            if context:
                container = getattr(context, "space_data", None)
                if (not container) or (container.type != 'VIEW_3D'): container = context.scene
            else: # make sure we deal with global cursor
                container = bpy.context.scene
            
            cursor_location = Vector(value)
            if force or (cursor_location != container.cursor_location):
                container.cursor_location = cursor_location
        
        @staticmethod
        def bounding_box(scene, matrix=None, exclude=()):
            if matrix is None: matrix = Matrix()
            
            m_to = matrix_inverted_safe(matrix)
            points = []
            
            exclude = {(scene.objects.get(obj) if isinstance(obj, str) else obj) for obj in exclude}
            
            mesh_cache = MeshCache(scene)
            for obj in scene.objects:
                if obj in exclude: continue
                
                m = m_to * obj.matrix_world
                
                mesh_obj = mesh_cache.get(obj)
                if mesh_obj and mesh_obj.data.vertices:
                    points.extend(m * v.co for v in mesh_obj.data.vertices)
                else:
                    points.append(m * Vector())
                
                if obj.mode == 'EDIT':
                    mesh_obj = mesh_cache.get(obj, 'RAW')
                    if mesh_obj and mesh_obj.data.vertices:
                        points.extend(m * v.co for v in mesh_obj.data.vertices)
                
                mesh_cache.clear() # don't waste memory
            
            if not points: return (None, None) # maybe use numpy? (if 2.70 has it included)
            points_iter = iter(points)
            x0, y0, z0 = next(points_iter)
            x1, y1, z1 = x0, y0, z0
            for x, y, z in points_iter:
                x0 = min(x0, x)
                y0 = min(y0, y)
                z0 = min(z0, z)
                x1 = max(x1, x)
                y1 = max(y1, y)
                z1 = max(z1, z)
            return (Vector((x0, y0, z0)), Vector((x1, y1, z1)))
    
    class Selection:
        @staticmethod
        def bounding_box(context, matrix=None):
            if matrix is None: matrix = Matrix()
            mode = context.mode
            m_to = matrix_inverted_safe(matrix)
            points = []
            
            if (mode in BlEnums.paint_sculpt_modes) or (mode in {'EDIT_TEXT'}):
                pass
            elif mode.startswith('EDIT'):
                obj = context.object
                m = m_to * obj.matrix_world
                if mode == 'EDIT_MESH':
                    for item, select_names in Selection(context, elem_types={'VERT'}):
                        points.append(m * item.co)
                elif mode in ('EDIT_CURVE', 'EDIT_SURFACE'):
                    SplinePoint = bpy.types.SplinePoint
                    for item, select_names in Selection(context):
                        if isinstance(item, SplinePoint):
                            points.append(m * item.co)
                        else:
                            if item.select_control_point: points.append(m * item.co)
                            if item.select_left_handle: points.append(m * item.handle_left)
                            if item.select_right_handle: points.append(m * item.handle_right)
                elif mode == 'EDIT_ARMATURE':
                    for item, select_names in Selection(context):
                        if item.select or item.select_head: points.append(m * item.head)
                        if item.select or item.select_tail: points.append(m * item.tail)
                elif mode == 'EDIT_METABALL':
                    for item, select_names in Selection(context):
                        points.append(m * item.co)
                elif mode == 'EDIT_LATTICE':
                    for item, select_names in Selection(context):
                        points.append(m * item.co_deform)
            else: # OBJECT, POSE
                mesh_cache = MeshCache(context.scene)
                for obj, select_names in Selection(context):
                    m = m_to * obj.matrix_world
                    mesh_obj = mesh_cache.get(obj)
                    if mesh_obj and mesh_obj.data.vertices:
                        points.extend(m * v.co for v in mesh_obj.data.vertices)
                    else:
                        points.append(m * Vector())
                    mesh_cache.clear() # don't waste memory
            
            if not points: return (None, None) # maybe use numpy? (if 2.70 has it included)
            points_iter = iter(points)
            x0, y0, z0 = next(points_iter)
            x1, y1, z1 = x0, y0, z0
            for x, y, z in points_iter:
                x0 = min(x0, x)
                y0 = min(y0, y)
                z0 = min(z0, z)
                x1 = max(x1, x)
                y1 = max(y1, y)
                z1 = max(z1, z)
            return (Vector((x0, y0, z0)), Vector((x1, y1, z1)))
    
    class Camera:
        @staticmethod
        def projection_info(cam, scene=None):
            if scene is None: scene = bpy.context.scene
            render = scene.render
            
            w = render.resolution_x * render.pixel_aspect_x
            h = render.resolution_y * render.pixel_aspect_y
            if cam.sensor_fit == 'HORIZONTAL':
                wh_norm = w
                sensor_size = cam.sensor_width
            elif cam.sensor_fit == 'VERTICAL':
                wh_norm = h
                sensor_size = cam.sensor_height
            else:
                wh_norm = max(w, h)
                sensor_size = cam.sensor_width
            w = w / wh_norm
            h = h / wh_norm
            
            if cam.type == 'ORTHO':
                persp = 0.0
                scale = cam.ortho_scale
                sx = w * scale
                sy = h * scale
                dx = cam.shift_x * scale
                dy = cam.shift_y * scale
                dz = scale
            else:
                persp = 1.0
                sx = w
                sy = h
                dx = cam.shift_x
                dy = cam.shift_y
                dz = cam.lens / sensor_size
            
            return (Vector((sx, sy, persp)), Vector((dx, dy, dz)))
    
    class Orientation:
        @staticmethod
        def create(context, name, matrix=None, overwrite=False, normalize=True):
            scene = context.scene
            
            if not overwrite:
                basename = name
                i = 1
                while name in scene.orientations:
                    name = "%s.%03i" % (basename, i)
                    i += 1
            
            bpy.ops.transform.create_orientation(attrs_to_dict(context), name=name, use_view=True, use=False, overwrite=overwrite)
            
            tfm_orient = scene.orientations[-1]
            tfm_orient.name = name
            
            if matrix:
                matrix = matrix.to_3x3()
                if normalize: matrix.normalize()
                tfm_orient.matrix = matrix
            
            return tfm_orient
        
        @staticmethod
        def update(context, name, matrix, auto_create=True, normalize=True):
            scene = context.scene
            tfm_orient = scene.orientations.get(name)
            if tfm_orient:
                matrix = matrix.to_3x3()
                if normalize: matrix.normalize()
                tfm_orient.matrix = matrix
            elif auto_create:
                tfm_orient = BlUtil.Orientation.create(context, name, matrix, normalize=normalize)
    
    class BMesh:
        @staticmethod
        def layer_get(bmlc, elem, default, layer=None):
            if layer is None: layer = bmlc.active
            elif isinstance(layer, str): layer = bmlc.get(layer)
            if layer is None: return default
            return elem[layer]
        
        @staticmethod
        def layer_set(bmlc, elem, value, layer=None):
            if layer is None:
                layer_name = "Active"
                layer = bmlc.active
            elif isinstance(layer, str):
                layer_name = layer
                layer = bmlc.get(layer)
            if layer is None: layer = bmlc.new(layer_name)
            elem[layer] = value
    
    class Spline:
        @staticmethod
        def find_point(curve, p):
            if isinstance(p, bpy.types.SplinePoint):
                for spline in curve.splines:
                    if spline.type == 'BEZIER': continue
                    for i, wp in enumerate(spline.points):
                        if wp == p: return (spline, i)
            else:
                for spline in curve.splines:
                    if spline.type != 'BEZIER': continue
                    for i, wp in enumerate(spline.bezier_points):
                        if wp == p: return (spline, i)
            return (None, -1)
        
        @staticmethod
        def neighbors(spline, i):
            points = (spline.bezier_points if spline.type == 'BEZIER' else spline.points)
            n = len(points)
            i0 = i-1
            i1 = i+1
            
            if (i0 < 0):
                if spline.use_cyclic_u:
                    p0 = points[n + i0]
                else:
                    p0 = None
            else:
                p0 = points[i0]
            
            if (i1 >= n):
                if spline.use_cyclic_u:
                    p1 = points[i1 - n]
                else:
                    p1 = None
            else:
                p1 = points[i1]
            
            return p0, p1
        
        @staticmethod
        def point_xyztw(p, obj=None):
            if not obj: obj = bpy.context.object # expected to be a Curve
            
            if isinstance(p, bpy.types.SplinePoint):
                co = p.co
                w = co[3]
                t = Vector((co[0], co[1], co[2]))
                return None, None, None, t, w
            else:
                p0, p1 = None, None
                if obj and (obj.type == 'CURVE'):
                    spline, i = BlUtil.Spline.find_point(obj.data, p)
                    if spline:
                        p0, p1 = BlUtil.Spline.neighbors(spline, i)
                
                if p.select_control_point:
                    t = Vector(p.co)
                    z = -(p.handle_right - p.handle_left).normalized()
                elif p.select_left_handle and p.select_right_handle:
                    t = (p.handle_right + p.handle_left) * 0.5
                    z = -(p.handle_right - p.handle_left).normalized()
                elif p.select_left_handle:
                    t = Vector(p.handle_left)
                    z = -(p.co - p.handle_left).normalized()
                elif p.select_right_handle:
                    t = Vector(p.handle_right)
                    z = -(p.handle_right - p.co).normalized()
                
                x_from_handles = (p.handle_left_type in ('VECTOR', 'FREE')) or (p.handle_right_type in ('VECTOR', 'FREE'))
                if x_from_handles:
                    x = -(p.handle_left - p.co).cross(p.handle_right - p.co).normalized()
                    y = -z.cross(x)
                elif (p0 and p1):
                    x = -(p0.co - p.co).cross(p1.co - p.co).normalized()
                    y = -z.cross(x)
                else:
                    x = None
                    y = None
                
                return x, y, z, t, None
