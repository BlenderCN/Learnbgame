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

#============================================================================#

import bpy

import time
import json

from mathutils import Vector

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_view3d import SmartView3D
from {0}dairin0d.utils_blender import Selection, BlUtil
from {0}dairin0d.utils_userinput import KeyMapUtils
from {0}dairin0d.utils_ui import NestedLayout, tag_redraw
from {0}dairin0d.bpy_inspect import prop, BlRna, BlEnums, bpy_struct
from {0}dairin0d.utils_accumulation import Aggregator, PatternRenamer
from {0}dairin0d.utils_addon import AddonManager
""".format(dairin0d_location))

from .batch_common import (
    LeftRightPanel, make_category, idnames_separator, iterate_workset
)

addon = AddonManager()

#============================================================================#
Category_Name = "Material"
CATEGORY_NAME = Category_Name.upper()
category_name = Category_Name.lower()
Category_Name_Plural = "Materials"
CATEGORY_NAME_PLURAL = Category_Name_Plural.upper()
category_name_plural = Category_Name_Plural.lower()
category_icon = 'MATERIAL'

Material = bpy.types.Material
MaterialSlot = bpy.types.MaterialSlot

class BatchOperations:
    clipbuffer = None
    
    @classmethod
    def to_material(cls, material):
        if isinstance(material, Material): return material
        if isinstance(material, MaterialSlot): return material.material
        return bpy.data.materials.get(material)
    
    @classmethod
    def set_material_slot(cls, obj, ms, material):
        max_users = (2 if obj.data.use_fake_user else 1)
        if (obj.data.users > max_users): ms.link = 'OBJECT'
        ms.material = material
    
    @classmethod
    def add_material_to_obj(cls, obj, idname):
        material = cls.to_material(idname)
        if not material: return
        for ms in obj.material_slots:
            if not ms.material:
                cls.set_material_slot(obj, ms, material)
                break
        else: # no free slots found
            obj.data.materials.append(None)
            ms = obj.material_slots[len(obj.material_slots)-1]
            cls.set_material_slot(obj, ms, material)
    
    @classmethod
    def clear_obj_materials(cls, obj, idnames=None, check_in=True):
        for ms in obj.material_slots:
            if (idnames is None) or ((ms.name in idnames) == check_in):
                cls.set_material_slot(obj, ms, None)
    
    @classmethod
    def clean_name(cls, mat):
        return mat.name
    
    @classmethod
    def iter_names(cls, obj):
        for ms in obj.material_slots:
            if not ms.material: continue
            yield ms.name
    
    @classmethod
    def iter_idnames(cls, obj):
        for ms in obj.material_slots:
            if not ms.material: continue
            yield ms.name
    
    @classmethod
    def iter_scene_objs_idnames(cls, scene):
        for obj in scene.objects:
            for ms in obj.material_slots:
                if ms.material: yield (obj, ms.name)
    
    @classmethod
    def enum_all(cls):
        for mat in bpy.data.materials:
            yield (mat.name, mat.name, mat.name)
    
    @classmethod
    def icon_kwargs(cls, idname, use_value=True):
        # Currently only 2 layout commands support icon_value parameter
        if (not idname) or (not use_value): return {"icon": category_icon}
        try:
            return {"icon_value": bpy.types.UILayout.icon(bpy.data.materials.get(idname))}
        except:
            return {"icon": category_icon}
    
    @classmethod
    def iterate(cls, search_in, context=None):
        if search_in != 'FILE':
            for obj in cls.iterate_objects(search_in, context):
                for ms in obj.material_slots:
                    if ms.material: yield ms.material
        else:
            yield from bpy.data.materials
    
    @classmethod
    def iterate_objects(cls, search_in, context=None):
        return iterate_workset(search_in, context, BlEnums.object_types_geometry)
    
    @classmethod
    def split_idnames(cls, idnames):
        if idnames is None: return None
        if not isinstance(idnames, str): return set(idnames)
        return set(idnames.split(idnames_separator))
    
    @classmethod
    def new(cls, idname):
        mat = bpy.data.materials.new(idname)
        return mat.name
    
    @classmethod
    def set_attr(cls, name, value, objects, idnames, **kwargs):
        idnames = cls.split_idnames(idnames)
        
        if name == "use_fake_user":
            mesh = None
            
            for idname in idnames:
                mat = cls.to_material(idname)
                if not mat: continue
                
                if value:
                    # can't set use_fake_user if 0 users
                    if mat.users == 0:
                        if mesh is None: mesh = bpy.data.meshes.new("TmpMesh")
                        mesh.materials.append(mat)
                else:
                    # can't unset use_fake_user if fake is the only user
                    if mat.users == 1:
                        if mesh is None: mesh = bpy.data.meshes.new("TmpMesh")
                        mesh.materials.append(mat)
                
                mat.use_fake_user = value
                
                if mesh and (len(mesh.materials) > 0): mesh.materials.pop(0)
            
            if mesh: bpy.data.meshes.remove(mesh)
        else:
            use_kwargs = False
            
            _setattr = setattr
            if isinstance(value, str):
                if PatternRenamer.is_pattern(value):
                    _setattr = PatternRenamer.apply_to_attr
                    use_kwargs = True
            
            if not use_kwargs: kwargs = {}
            
            for obj in objects:
                if isinstance(obj, Material):
                    if obj.name in idnames:
                        _setattr(obj, name, value, **kwargs)
                else:
                    for ms in obj.material_slots:
                        if not ms.material: continue
                        if ms.name in idnames:
                            _setattr(ms.material, name, value, **kwargs)
    
    @classmethod
    def clear(cls, objects):
        for obj in objects:
            cls.clear_obj_materials(obj)
    
    @classmethod
    def add(cls, objects, idnames):
        idnames = cls.split_idnames(idnames)
        for obj in objects:
            for idname in idnames:
                cls.add_material_to_obj(obj, idname)
    
    @classmethod
    def remove(cls, objects, idnames, from_file=False):
        cls.assign('REPLACE', None, objects, idnames, "", from_file)
    
    @classmethod
    def find_objects(cls, idnames, search_in, context=None):
        idnames = cls.split_idnames(idnames)
        for obj in cls.iterate_objects(search_in, context):
            if any((ms.name in idnames) for ms in obj.material_slots):
                yield obj
    
    @classmethod
    def select(cls, context, idnames, operation='SET'):
        idnames = cls.split_idnames(idnames)
        data = {obj:"select" for obj in context.scene.objects if any((ms.name in idnames) for ms in obj.material_slots)}
        Selection(context).update(data, operation)
        #for obj in context.scene.objects:
        #    obj.select = any((ms.name in idnames) for ms in obj.material_slots)
    
    @classmethod
    def purge(cls, even_with_fake_users, idnames=None):
        if idnames is None:
            if even_with_fake_users:
                fake_idnames = (mat.name for mat in bpy.data.materials if mat.use_fake_user and (mat.users == 1))
                cls.set_attr("use_fake_user", False, None, fake_idnames)
            for mat in tuple(bpy.data.materials):
                if mat.users > 0: continue
                bpy.data.materials.remove(mat)
        else:
            cls.remove(None, idnames, True)
            cls.set_attr("use_fake_user", False, None, idnames)
            idnames = cls.split_idnames(idnames)
            for mat in tuple(bpy.data.materials):
                if mat.name in idnames:
                    bpy.data.materials.remove(mat)
    
    @classmethod
    def copy(cls, active_obj, exclude=()):
        if not active_obj:
            cls.clipbuffer = []
        else:
            cls.clipbuffer = [ms.name for ms in active_obj.material_slots if ms.material and (ms.name not in exclude)]
    
    @classmethod
    def paste(cls, objects, paste_mode):
        idnames = cls.clipbuffer
        if idnames is None: return
        if paste_mode != 'AND':
            for obj in objects:
                if paste_mode == 'SET': cls.clear_obj_materials(obj)
                for idname in idnames:
                    cls.add_material_to_obj(obj, idname)
        else:
            for obj in objects:
                cls.clear_obj_materials(obj, idnames, False)
    
    @classmethod
    def merge_identical(cls):
        unique = set(bpy.data.materials)
        identical = []
        # ignore all properties from bpy_struct
        ignore = {"name", "id_data", "users", "use_fake_user", "tag", "is_updated", "is_updated_data", "is_library_indirect", "library"}
        
        def compare_node_tree(rna_prop, valueA, valueB):
            if (valueA is None) and (valueB is None): return True
            if (valueA is None) or (valueB is None): return False
            if not BlRna.compare(valueA.animation_data, valueB.animation_data): return False
            # ignore grease pencil
            ntkA = NodeTreeComparer.nodetree_key(valueA)
            ntkB = NodeTreeComparer.nodetree_key(valueB)
            return ntkA == ntkB
        specials = {"node_tree":compare_node_tree}
        
        for item in bpy.data.materials:
            duplicates = None
            unique.discard(item)
            
            for item2 in unique:
                if BlRna.compare(item, item2, ignore=ignore, specials=specials):
                    if duplicates is None: duplicates = {item}
                    duplicates.add(item2)
            
            if duplicates is not None:
                identical.append(duplicates)
                unique.difference_update(duplicates)
        
        for duplicates in identical:
            # find best candidate for preservation
            best, best_users, best_len = None, 0, 0
            for item in duplicates:
                if item.users >= best_users:
                    is_better = (item.users > best_users)
                    is_better |= (best_len <= 0)
                    is_better |= (len(item.name) < best_len)
                    if is_better:
                        best, best_users, best_len = item, item.users, len(item.name)
            duplicates.discard(best)
            src_idnames = idnames_separator.join(item.name for item in duplicates)
            dst_idname = best.name
            cls.assign('REPLACE', None, None, src_idnames, dst_idname, from_file=True, purge=True)
    
    assign_mode_default = 'ADD'
    assign_mode_default1 = 'FILTER'
    assign_mode_default2 = 'OVERRIDE'
    assign_modes = [
        ('ADD', "Add", "Add"),
        ('FILTER', "Filter", "Filter"),
        ('REPLACE', "Replace", "Replace"),
        ('OVERRIDE', "Override", "Override"),
        ('OVERRIDE_KEEP_SLOTS', "Override+", "Override without removing material slots"),
    ]
    @classmethod
    def assign(cls, assign_mode, active_obj, objects, src_idnames, dst_idnames, from_file=False, purge=False):
        src_idnames = cls.split_idnames(src_idnames) # can be None
        dst_idnames = cls.split_idnames(dst_idnames)
        
        # option: {switch slot to OBJECT | allow modifying the data}
        if assign_mode == 'ADD': # previously known as "Ensure"
            # option: {only reuse empty slots | only create new slots | create if cannot reuse}
            for obj in objects:
                for idname in dst_idnames.difference(cls.iter_idnames(obj)):
                    cls.add_material_to_obj(obj, idname)
        elif assign_mode == 'FILTER':
            # option: {make slots empty | remove slots}
            for obj in objects:
                for ms in obj.material_slots:
                    if ms.name not in dst_idnames:
                        cls.set_material_slot(obj, ms, None)
        else:
            replaced_idnames = set()
            
            def should_replace(mat):
                if (src_idnames is None) or (mat and (mat.name in src_idnames)):
                    if mat: replaced_idnames.add(mat.name)
                    return True
                return False
            
            dst_materials = [cls.to_material(idname) for idname in sorted(dst_idnames) if idname]
            if not dst_materials: dst_materials.append(None)
            
            if not from_file:
                for obj in objects:
                    i_repl = 0
                    for ms in obj.material_slots:
                        if should_replace(ms.material):
                            cls.set_material_slot(obj, ms, dst_materials[i_repl])
                            i_repl = (i_repl + 1) % len(dst_materials)
                    
                    if assign_mode != 'REPLACE':
                        for i_repl in range(len(obj.material_slots), len(dst_materials)):
                            obj.data.materials.append(None)
                            ms = obj.material_slots[i_repl]
                            cls.set_material_slot(obj, ms, dst_materials[i_repl])
                    if assign_mode == 'OVERRIDE':
                        for i in range(len(dst_materials), len(obj.material_slots)):
                            obj.data.materials.pop(len(obj.material_slots)-1, update_data=True)
            else:
                for obj in bpy.data.objects:
                    i_repl = 0
                    for ms in obj.material_slots:
                        if should_replace(ms.material):
                            ms.material = dst_materials[i_repl]
                            i_repl = (i_repl + 1) % len(dst_materials)
                
                for datas in (bpy.data.meshes, bpy.data.curves, bpy.data.metaballs):
                    for data in datas:
                        i_repl = 0
                        for i in range(len(data.materials)):
                            mat = data.materials[i]
                            if should_replace(mat):
                                data.materials[i] = dst_materials[i_repl]
                                i_repl = (i_repl + 1) % len(dst_materials)
                        
                        if assign_mode != 'REPLACE':
                            for i_repl in range(len(data.materials), len(dst_materials)):
                                data.materials.append(None)
                                data.materials[i_repl] = dst_materials[i_repl]
                        if assign_mode == 'OVERRIDE':
                            for i in range(len(dst_materials), len(data.materials)):
                                data.materials.pop(len(data.materials)-1, update_data=True)
            
            replaced_idnames.difference_update(dst_idnames)
            
            if purge and replaced_idnames:
                cls.set_attr("use_fake_user", False, None, replaced_idnames)
                for mat in tuple(bpy.data.materials):
                    if mat.name in replaced_idnames:
                        bpy.data.materials.remove(mat)

class NodeTreeComparer:
    @classmethod
    def link_key(cls, link):
        return (
            link.from_node.bl_idname,
            link.from_node.name,
            link.from_socket.bl_idname,
            link.from_socket.type,
            link.from_socket.identifier,
            link.from_socket.enabled,
            link.to_socket.bl_idname,
            link.to_socket.name,
            link.to_socket.bl_idname,
            link.to_socket.type,
            link.to_socket.identifier,
            link.to_socket.enabled,
        )
    
    @classmethod
    def socket_key(cls, socket):
        default_value = (BlRna.serialize_value(socket.default_value)
            if hasattr(socket, "default_value") else None)
        return (socket.bl_idname, socket.identifier,
            socket.enabled, socket.type, default_value,
            tuple(cls.link_key(link) for link in socket.links))
    
    @classmethod
    def node_key(cls, node):
        idname = node.bl_idname # type of node
        name = node.name
        internal_links = frozenset(
            cls.link_key(link)
            for link in node.internal_links
        )
        parent = node.parent
        if parent is not None: parent = parent.name
        inputs = frozenset(
            cls.socket_key(socket)
            for socket in node.inputs
        )
        outputs = frozenset(
            cls.socket_key(socket)
            for socket in node.outputs
        )
        return (idname, name, parent,
            internal_links, inputs, outputs)
    
    @classmethod
    def nodetree_key(cls, nodetree):
        return frozenset(cls.node_key(node) for node in nodetree.nodes)

#============================================================================#

make_category(globals(), is_ID=True, copy_paste_contexts={'MATERIAL'})
