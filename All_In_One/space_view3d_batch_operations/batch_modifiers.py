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
from {0}dairin0d.utils_python import copyattrs, attrs_to_dict, dict_to_attrs
from {0}dairin0d.utils_view3d import SmartView3D
from {0}dairin0d.utils_blender import Selection, BlUtil
from {0}dairin0d.utils_userinput import KeyMapUtils
from {0}dairin0d.utils_ui import NestedLayout, tag_redraw
from {0}dairin0d.bpy_inspect import prop, BlRna, BlEnums
from {0}dairin0d.utils_accumulation import Aggregator, PatternRenamer
from {0}dairin0d.utils_addon import AddonManager
""".format(dairin0d_location))

from .batch_common import (
    LeftRightPanel, make_category, idnames_separator, iterate_workset, apply_modifiers
)

addon = AddonManager()

#============================================================================#
Category_Name = "Modifier"
CATEGORY_NAME = Category_Name.upper()
category_name = Category_Name.lower()
Category_Name_Plural = "Modifiers"
CATEGORY_NAME_PLURAL = Category_Name_Plural.upper()
category_name_plural = Category_Name_Plural.lower()
category_icon = 'MODIFIER'

Modifier = bpy.types.Modifier

class BatchOperations:
    clipbuffer = None
    
    _all_types_enum = BlRna.serialize_value(
        BlRna(bpy.ops.object.modifier_add).properties["type"].enum_items)
    
    @classmethod
    def clean_name(cls, md):
        return md.bl_rna.name.replace(" Modifier", "")
    
    @classmethod
    def iter_names(cls, obj):
        for md in obj.modifiers: yield cls.clean_name(md)
    
    @classmethod
    def iter_idnames(cls, obj):
        for md in obj.modifiers: yield md.type
    
    @classmethod
    def iter_scene_objs_idnames(cls, scene):
        for obj in scene.objects:
            for md in obj.modifiers:
                yield (obj, md.type)
    
    @classmethod
    def enum_all(cls):
        yield from cls._all_types_enum
    
    @classmethod
    def icon_kwargs(cls, idname, use_value=True):
        return {"icon": BlEnums.modifier_icons.get(idname, category_icon)}
    
    @classmethod
    def iterate(cls, search_in, context=None):
        for obj in cls.iterate_objects(search_in, context):
            yield from obj.modifiers
    
    @classmethod
    def iterate_objects(cls, search_in, context=None):
        return iterate_workset(search_in, context, BlEnums.object_types_with_modifiers)
    
    @classmethod
    def split_idnames(cls, idnames):
        if idnames is None: return None
        if not isinstance(idnames, str): return set(idnames)
        return set(idnames.split(idnames_separator))
    
    @classmethod
    def set_attr(cls, name, value, objects, idnames, **kwargs):
        idnames = cls.split_idnames(idnames)
        
        use_kwargs = False
        
        _setattr = setattr
        if isinstance(value, str):
            if PatternRenamer.is_pattern(value):
                _setattr = PatternRenamer.apply_to_attr
                use_kwargs = True
        
        if not use_kwargs: kwargs = {}
        
        for obj in objects:
            if isinstance(obj, Modifier):
                if obj.type in idnames:
                    _setattr(obj, name, value, **kwargs)
            else:
                for md in obj.modifiers:
                    if md.type in idnames:
                        _setattr(md, name, value, **kwargs)
    
    @classmethod
    def clear(cls, objects):
        for obj in objects:
            obj.modifiers.clear()
    
    @classmethod
    def add(cls, objects, idnames):
        idnames = cls.split_idnames(idnames)
        for obj in objects:
            for idname in idnames:
                md = obj.modifiers.new(idname.capitalize(), idname)
    
    @classmethod
    def apply(cls, objects, scene, idnames, options=(), apply_as='DATA'):
        idnames = cls.split_idnames(idnames)
        apply_modifiers(objects, scene, idnames, options, apply_as)
    
    @classmethod
    def remove(cls, objects, idnames, from_file=False):
        cls.assign('REPLACE', None, objects, idnames, "", from_file)
    
    @classmethod
    def find_objects(cls, idnames, search_in, context=None):
        idnames = cls.split_idnames(idnames)
        for obj in cls.iterate_objects(search_in, context):
            if any((md.type in idnames) for md in obj.modifiers):
                yield obj
    
    @classmethod
    def select(cls, context, idnames, operation='SET'):
        idnames = cls.split_idnames(idnames)
        data = {obj:"select" for obj in context.scene.objects if any((md.type in idnames) for md in obj.modifiers)}
        Selection(context).update(data, operation)
        #for obj in context.scene.objects:
        #    obj.select = any((md.type in idnames) for md in obj.modifiers)
    
    @classmethod
    def purge(cls, even_with_fake_users, idnames=None):
        pass # not applicable to modifiers (they are not ID datablocks)
    
    @classmethod
    def copy(cls, active_obj, exclude=()):
        if not active_obj:
            cls.clipbuffer = []
        else:
            cls.clipbuffer = [attrs_to_dict(md) for md in active_obj.modifiers if md.type not in exclude]
    
    @classmethod
    def paste(cls, objects, paste_mode):
        md_infos = cls.clipbuffer
        if md_infos is None: return
        if paste_mode != 'AND':
            for obj in objects:
                if paste_mode == 'SET': obj.modifiers.clear()
                for md_info in md_infos:
                    md = obj.modifiers.new(md_info["name"], md_info["type"])
                    dict_to_attrs(md, md_info)
        else:
            idnames = {md_info["type"] for md_info in md_infos}
            for obj in objects:
                for md in tuple(obj.modifiers):
                    if md.type not in idnames:
                        obj.modifiers.remove(md)
    
    assign_mode_default = 'ADD'
    assign_mode_default1 = 'FILTER'
    assign_mode_default2 = 'OVERRIDE'
    assign_modes = [
        ('ADD', "Add", "Add"),
        ('FILTER', "Filter", "Filter"),
        ('REPLACE', "Replace", "Replace"),
        ('OVERRIDE', "Override", "Override"),
    ]
    @classmethod
    def assign(cls, assign_mode, active_obj, objects, src_idnames, dst_idnames, from_file=False, purge=False):
        src_idnames = cls.split_idnames(src_idnames) # can be None
        dst_idnames = cls.split_idnames(dst_idnames)
        
        objects = (bpy.data.objects if from_file else tuple(objects)) # need to iterate multiple times
        
        if assign_mode != 'FILTER':
            # collect parameter sources (hmm, maybe if not present in given objects, search in all?)
            attr_sources = {}
            for obj in objects:
                for md in obj.modifiers:
                    if md.type not in dst_idnames: continue
                    if (obj == active_obj) or (md.type not in attr_sources):
                        attr_sources[md.type] = md
            
            def copy_params(md):
                attr_source = attr_sources.get(md.type)
                if attr_source: copyattrs(attr_source, md)
        
        if assign_mode == 'ADD': # previously known as "Ensure"
            for obj in objects:
                existing_idnames = set(cls.iter_idnames(obj))
                idnames_to_add = dst_idnames.difference(existing_idnames)
                idnames_to_add.discard("")
                
                for idname in idnames_to_add:
                    copy_params(obj.modifiers.new(idname.capitalize(), idname))
        elif assign_mode == 'FILTER':
            for obj in objects:
                for md in tuple(obj.modifiers):
                    if md.type not in dst_idnames:
                        obj.modifiers.remove(md)
        else:
            for obj in objects:
                existing_idnames = set(cls.iter_idnames(obj))
                if (src_idnames is None) or (assign_mode == 'OVERRIDE'):
                    idnames_to_remove = existing_idnames
                else:
                    idnames_to_remove = src_idnames.intersection(existing_idnames)
                idnames_to_remove = idnames_to_remove.difference(dst_idnames)
                idnames_to_add = dst_idnames.difference(existing_idnames)
                idnames_to_add.discard("")
                
                should_replace = (assign_mode == 'OVERRIDE')
                for md in tuple(obj.modifiers):
                    if md.type in idnames_to_remove:
                        obj.modifiers.remove(md)
                        should_replace = True
                
                if should_replace:
                    for idname in idnames_to_add:
                        copy_params(obj.modifiers.new(idname.capitalize(), idname))

#============================================================================#

@addon.Operator(idname="object.batch_{}_apply".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
"Click: Apply (+Ctrl: globally, +Alt: as shape)")
def Operator_Apply(self, context, event, idnames="", index=0, title=""):
    category = get_category()
    options = get_options()
    apply_as = 'DATA'
    if event and event.alt: apply_as = 'SHAPE'
    bpy.ops.ed.undo_push(message="Batch Apply {}".format(Category_Name_Plural))
    BatchOperations.apply(options.iterate_objects(context, event.ctrl), context.scene, idnames, options.apply_options, apply_as=apply_as)
    category.tag_refresh()
    return {'FINISHED'}

class OptionsMixin:
    # This property uses the update function defined in the final/descendant class. Luckily, AddonManager has a mechanism for that.
    apply_options = {'CONVERT_TO_MESH', 'MAKE_SINGLE_USER', 'REMOVE_DISABLED', 'APPLY_SHAPE_KEYS', 'VISIBLE_ONLY'} | prop("Apply Modifier options", update="update", items=[
        ('CONVERT_TO_MESH', "Convert to mesh", "Convert to mesh", 'OUTLINER_OB_MESH'),
        ('MAKE_SINGLE_USER', "Make single user", "Make single user", 'UNLINKED'),
        ('REMOVE_DISABLED', "Remove disabled", "Remove disabled", 'GHOST_DISABLED'),
        ('DELETE_OPERANDS', "Delete operands", "Delete the remaining boolean operands", 'MOD_BOOLEAN'),
        ('APPLY_SHAPE_KEYS', "Apply shape keys", "Apply shape keys before applying the modifiers", 'SHAPEKEY_DATA'),
        ('VISIBLE_ONLY', "Only visible", "Apply only the modifiers visible in the viewport", 'RESTRICT_VIEW_OFF'),
    ])

@addon.Menu(idname="VIEW3D_MT_batch_{}_options_apply_options".format(category_name_plural), label="Apply Modifier")
def Menu_ApplyModifierOptions(self, context):
    """Apply Modifier options"""
    layout = NestedLayout(self.layout)
    options = get_options()
    layout.props_enum(options, "apply_options")
menu_options_extra = [("menu", dict(menu="VIEW3D_MT_batch_{}_options_apply_options".format(category_name_plural), icon=category_icon))]

aggregate_attrs = [
    #("show_expanded", dict(tooltip="Are modifier(s) expanded in the UI", icons=('TRIA_DOWN', 'TRIA_RIGHT'))),
    ("show_render", dict(tooltip="Use modifier(s) during render")),
    ("show_viewport", dict(tooltip="Display modifier(s) in viewport")),
    ("show_in_editmode", dict(tooltip="Display modifier(s) in edit mode")),
    ("show_on_cage", dict(tooltip="Adjust edit cage to modifier(s) result")),
    ("use_apply_on_spline", dict(tooltip="Apply modifier(s) to splines' points rather than the filled curve/surface")),
]

nongeneric_actions = [
    ("aggregate_toggle", dict(property="show_render", text="Use in render", icons='SCENE')),
    ("aggregate_toggle", dict(property="show_viewport", text="Show in viewport", icons='VISIBLE_IPO_ON')),
    ("aggregate_toggle", dict(property="show_in_editmode", text="Show in editmode", icons='EDITMODE_HLT')),
    ("aggregate_toggle", dict(property="show_on_cage", text="Show on cage", icons='MESH_DATA')),
    ("aggregate_toggle", dict(property="use_apply_on_spline", text="Apply to spline", icons='SURFACE_DATA')),
    ("operator", dict(operator="object.batch_{}_apply".format(category_name), text="Apply modifier")), # use modifier-type-specific icons
]

quick_access_default = {"show_viewport", "object.batch_{}_apply".format(category_name)}

make_category(globals(), "type", menu_options_extra=menu_options_extra, options_mixin=OptionsMixin,
    aggregate_attrs=aggregate_attrs, nongeneric_actions=nongeneric_actions,
    quick_access_default=quick_access_default, copy_paste_contexts={'MODIFIER'})
