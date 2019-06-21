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

bl_info = {
    "name": "Batch Operations / Manager",
    "description": "Modifiers, Materials, Groups management / batch operations",
    "author": "dairin0d, moth3r",
    "version": (0, 6, 9),
    "blender": (2, 7, 0),
    "location": "View3D > Batch category in Tools panel",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/BatchOperations",
    "tracker_url": "https://github.com/dairin0d/batch-operations/issues",
    "category": "Learnbgame",
}
#============================================================================#

if "dairin0d" in locals():
    import imp
    imp.reload(dairin0d)
    imp.reload(batch_common)
    imp.reload(batch_modifiers)
    imp.reload(batch_materials)
    imp.reload(batch_groups)

import bpy

import time
import json

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_view3d import SmartView3D
from {0}dairin0d.utils_userinput import KeyMapUtils
from {0}dairin0d.utils_ui import NestedLayout, find_ui_area, ui_context_under_coord
from {0}dairin0d.bpy_inspect import prop, BlRna
from {0}dairin0d.utils_addon import AddonManager
""".format(dairin0d_location))

from . import batch_common
from . import batch_modifiers
from . import batch_materials
from . import batch_groups

addon = AddonManager()

"""
Blender Bugs:
* When several panels have menus/enums in their headers, moving the mouse over a menu item, behind which another menu is located, will immdeiately open that menu instead.
* Quaternion() creates Quaternion((0,0,0,0)), which converts to Eluer((pi,0,0)), i.e. not a zero rotation. Is this intentional?
* No API for directly getting the current manipulator position/rotation/matrix.
* No API for getting/setting active element of curve/surface.
* No API for getting/setting selected state metaball element.
* No API for getting/setting active element of lattice.
* No API for directly creating/deleting transform orientations (the operators can be invoked only in certain contexts)


ask wazou how can we streamline my addons
(note: moth3r asks to first discuss all ideas before implementing)

Requests by Wazou:
* when clicking on modifier/material/etc. in Batch Operations, switch the Buttons area(s) to display the corresponding modifier/material/etc.
* Add remove option to remove material from object along with its slot (but not removing from the .blend completely)

Requests by Jerry Perkins:
* a way to push a selected modifier to the bottom of all selected objects


moth3r, 2015-12-22:
maybe is not a bug but at least behavior kinda looks strange, at least to me. When I would like to show or hide a group of linked mesh object I cannot do it via batch panel. It kinda works on a fresh loaded file/scene but after some time item selection stops working completely. 


moth3r, 2016-02-18
add option to display a batch category of objects which don't have materials/modifiers/gorups/etc.


Make sure copy/pasting doesn't crash Blender after Undo (seems like it doesn't crash, but pasted references to objects are invalid)
(TODO: clear clipbuffers on undo detection)
Make a general mechanism of serializing/deserializing links to ID blocks? (also useful for cut/copy/paste addon)



when there is too much lag, the batch-toggles might behave glitchy



make Batch Materials work in edit mode?

select by some attribute (e.g. by vertex group or mesh datablock)

// (not for Batch Operations, maybe Macro addon?):
preset system for modeling (sort of visual scripting/macro system)
(able to change order and parameters and add/remove operations)
apply to current selection or some vertex group(s)





* Operators
    * Batch apply operator (search field) -- not possible, since dynamic dialog drawing is currently impossible in Blender
        * operator's draw (if not defined, use automatic draw)
        * For: selection, visible, layer, scene, .blend
    * [DONE] Repeat last N actions
* Objects?
    * Batch rename with some sort of name pattern detection
    * Set layers
    * single-click parenting: show a list of top-level objects? (i.e. without parents)
        * Actually there is a nice addon http://blenderaddonlist.blogspot.com/2014/06/addon-parent-to-empty.html
        * That could be shift+click or click operation for all selected objects depending on button.
    * aggregate by object types?
    * batch convert object type?
    * replace a number of objects with some other object? (e.g. one type of screw with other type of screw)
    * moth3r suggested copy/pasting objects (in particular, so that pasting an object won't create duplicate materials)
    * copy/paste inside group? (in the selected batch groups)
    * ? see Apply menu (rot/pos/scale, visual transform, make duplicates real?)
    * See also: https://github.com/sebastian-k/scripts/blob/master/power_snapping_pies.py (what of this is applicable to batch operations?)
* Material slots?
    ...
* Constraints
    ...
* Mesh layers
    * Notes:
        * different objects may have similarly different layers which mean different things in each case, so unless the user
          has taken the measures to name each layer properly, displaying a table of layer names won't help the user
          understand what each layer is responsible for.
        * copying/assigning layers is possible only between identical geometry
        * basically, the only batch operation that makes sense for default-named layers of inhomogenous data is "Remove"
    * Vertex Groups (also applicable to Lattice) - stored in object
    * Shape keys (also applicable to Lattice and Curve/Surface)
    * UV maps
    * Vertex colors
    * Custom layers
* Layers?
    * see also: Layer Management addon by Bastien Montagne
* Data?
    * replace/override some datas with another data (data type must be same)
    * some data-specific properties?
    * no add, no paste modes, no remove (? or remove the objects?), no "add"/"filter" assign actions
"""

#============================================================================#

@addon.Operator(idname="object.batch_properties_copy", space_type='PROPERTIES', label="Batch Properties Copy")
def Batch_Properties_Copy(self, context):
    properties_context = context.space_data.context
    Category = addon.preferences.copy_paste_contexts.get(properties_context)
    if Category is None: return
    pin_id = context.space_data.pin_id
    object_name = (pin_id.name if isinstance(pin_id, bpy.types.Object) else "")
    getattr(bpy.ops.object, "batch_{}_copy".format(Category.category_name))(object_name=object_name)

@addon.Operator(idname="object.batch_properties_paste", space_type='PROPERTIES', label="Batch Properties Paste")
def Batch_Properties_Copy(self, context):
    properties_context = context.space_data.context
    Category = addon.preferences.copy_paste_contexts.get(properties_context)
    if Category is None: return
    getattr(bpy.ops.object, "batch_{}_paste".format(Category.category_name))()

@addon.Preferences.Include
class ThisAddonPreferences:
    refresh_interval = 0.5 | prop("Auto-refresh interval", name="Refresh interval", min=0.0)
    use_panel_left = True | prop("Show in T-panel", name="T (left panel)")
    use_panel_right = False | prop("Show in N-panel", name="N (right panel)")
    default_select_state = True | prop("Default row selection state", name="Rows selected by default")
    use_rename_popup = True | prop("Use a separate dialog for batch renaming", name="Use popup dialog for renaming")
    include_duplis = False | prop("Process dupli instances (Groups Pro/nested groups support)", name="Process dupli instances")
    
    show_operations_as_list = False | prop("Show all in one line or each in a separate row")
    
    sync_lock = False
    
    def sync_names(self):
        cls = self.__class__
        names = []
        for Category in cls.categories:
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                names.append(Category.Category_Name_Plural)
        return "/".join(names)
    
    def sync_copy(self, active_obj):
        cls = self.__class__
        for Category in cls.categories:
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                Category.BatchOperations.copy(active_obj, Category.excluded)
    
    def sync_paste(self, context, paste_mode):
        cls = self.__class__
        for Category in cls.categories:
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                Category.BatchOperations.paste(options.iterate_objects(context), paste_mode)
                category = getattr(addon.external, Category.category_name_plural)
                category.tag_refresh()
    
    def sync_add(self, active_options, active_category_name_plural):
        if not active_options.synchronized: return False
        cls = self.__class__
        if cls.sync_lock: return False
        cls.sync_lock = True
        
        src_options = None
        for Category in cls.categories:
            if (Category.category_name_plural == active_category_name_plural): continue
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                src_options = options
                break
        
        if src_options:
            active_options.synchronize_selection = src_options.synchronize_selection
            active_options.prioritize_selection = src_options.prioritize_selection
            active_options.autorefresh = src_options.autorefresh
            active_options.paste_mode = src_options.paste_mode
            active_options.search_in = src_options.search_in
            active_options.aggregate_mode = src_options.aggregate_mode
        
        cls.sync_lock = False
        return True
    
    def sync_update(self, active_options, active_category_name_plural):
        if not active_options.synchronized: return False
        cls = self.__class__
        if cls.sync_lock: return False
        cls.sync_lock = True
        
        for Category in cls.categories:
            if (Category.category_name_plural == active_category_name_plural): continue
            options = getattr(self, Category.category_name_plural)
            if options.synchronized:
                options.synchronize_selection = active_options.synchronize_selection
                options.prioritize_selection = active_options.prioritize_selection
                options.autorefresh = active_options.autorefresh
                options.paste_mode = active_options.paste_mode
                options.search_in = active_options.search_in
                options.aggregate_mode = active_options.aggregate_mode
        
        cls.sync_lock = False
        return True
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        
        with layout.row()(alignment='LEFT'):
            layout.prop(self, "refresh_interval")
            layout.prop(self, "use_panel_left")
            layout.prop(self, "use_panel_right")
        
        with layout.row()(alignment='LEFT'):
            layout.prop(self, "default_select_state")
            layout.prop(self, "use_rename_popup")
            layout.prop(self, "include_duplis")
        
        with layout.row()(alignment='LEFT'):
            with layout.column():
                for Category in self.categories:
                    category = getattr(self, Category.category_name_plural)
                    layout.label(text=Category.Category_Name_Plural+":", icon=Category.category_icon)
            with layout.column():
                for Category in self.categories:
                    category = getattr(self, Category.category_name_plural)
                    layout.prop_menu_enum(category, "quick_access", text="Quick access")

def register():
    addon.register()
    
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Window")
        kmi = km.keymap_items.new("object.batch_properties_copy", 'C', 'PRESS', ctrl=True)
        kmi = km.keymap_items.new("object.batch_properties_paste", 'V', 'PRESS', ctrl=True)

def unregister():
    # Note: if we remove from non-addon keyconfigs, the keymap registration
    # won't work on the consequent addon enable/reload (until Blender restarts)
    kc = bpy.context.window_manager.keyconfigs.addon
    KeyMapUtils.remove("object.batch_properties_copy", place=kc)
    KeyMapUtils.remove("object.batch_properties_paste", place=kc)
    
    addon.unregister()
