### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# Contact for more information about the Addon:
# Email:    germano.costa@ig.com.br
# Twitter:  wii_mano @mano_wii

bl_info = {
    "name": "Change Panel Categories",
    "author": "Germano Cavalcante",
    "version": (0, 1),
    "blender": (2, 75, 4),
    "location": "View3D > TOOLS > My Category > Change Category",
    "description": "Change Panel Categories",
    #"wiki_url" : "http://blenderartists.org/forum/showthread.php?363859-Addon-CAD-Snap-Utilities",
    "category": "Learnbgame"
}

import bpy
from bpy.types import Panel, PropertyGroup, AddonPreferences
from bpy.props import PointerProperty, StringProperty

class VIEW3D_PT_change_category(Panel):
    """Change the category of a panel"""
    bl_label = "Change Category"
    bl_idname = "VIEW3D_PT_change_category"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "My Category"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        preferences = bpy.context.user_preferences.addons['ui_change_category'].preferences

        col = layout.column(align=False)
        col.label("Panel:")
        col.prop_search(wm, "chosen_panel",  preferences, "tool_panels",  text="", icon="MENU_PANEL")
        if wm.chosen_panel:
            col.prop(wm, "panel_category")
        col.operator("wm.save_userpref")

def get_category(self, context):
    preferences = context.user_preferences.addons['ui_change_category'].preferences
    wm = context.window_manager
    name = wm.chosen_panel
    if name in preferences.tool_panels:
        category = preferences.tool_panels[name].category
        bpy.types.WindowManager.panel_category = bpy.props.StringProperty(
            name="Category",
            description="Choose a name for the category of the panel",
            default=preferences.tool_panels[name].defa_cat,
            update=update_category,
            )
        wm.panel_category = category

def update_category(self, context):
    preferences = context.user_preferences.addons[__name__].preferences
    wm = context.window_manager
    name = wm.chosen_panel
    if name in preferences.tool_panels:
        category = preferences.tool_panels[name].category
        if category != wm.panel_category:
            idname = preferences.tool_panels[name].idname
            panel = getattr(bpy.types, idname)
            panel.bl_category = wm.panel_category
            bpy.utils.unregister_class(panel)
            bpy.utils.register_class(panel)
            preferences.tool_panels[name].category = wm.panel_category
            preferences.tool_panels[name].name = panel.bl_category + ' (' + panel.bl_label + ', ' + idname + ')'
            print(category, 'to', wm.panel_category)

# Assign a collection
class GroupNames(PropertyGroup):
    name = StringProperty(name="Label", default="")
    idname = StringProperty(name="Panel", default="VIEW3D_PT_change_category")
    category = StringProperty(name="Category", default="My Category")
    defa_cat = StringProperty(name="Category", default="Default")

class ChangeCategoryPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    tool_panels = bpy.props.CollectionProperty(type=GroupNames)

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        col = layout.column(align=False)
        col.label("Tool Panels:")
        col.prop_search(wm, "chosen_panel",  self, "tool_panels",  text="", icon="MENU_PANEL")
        if wm.chosen_panel:
            col.prop(wm, "panel_category")

def register():
    bpy.types.WindowManager.chosen_panel = bpy.props.StringProperty(update=get_category)
    bpy.utils.register_class(GroupNames)
    bpy.utils.register_class(ChangeCategoryPreferences)
    preferences = bpy.context.user_preferences.addons[__name__].preferences

    if bpy.context.user_preferences.addons[-1].module != __name__:
        cache = {}
        for k in preferences.tool_panels:
            cache[k.name] = k.idname, k.category, k.defa_cat
        # Register this addon last next startup
        module_name = __name__
        addons = bpy.context.user_preferences.addons

        while module_name in addons:
            addon = addons.get(module_name)
            if addon:
                addons.remove(addon)

        addon = addons.new()
        addon.module = module_name
        preferences = bpy.context.user_preferences.addons[module_name].preferences
        for k, v in cache.items():
            my_item = preferences.tool_panels.add()
            my_item.name = k
            my_item.idname = v[0]
            my_item.category = v[1]
            my_item.defa_cat = v[2]
        del cache

    #print(preferences.tool_panels)
    bpy.types.WindowManager.panel_category = bpy.props.StringProperty(
        name="Category",
        description="Choose a name for the category of the panel",
        default="My Category",
        update=update_category,
        )
    bpy.utils.register_class(VIEW3D_PT_change_category)

    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'bl_category'):
            name = panel.bl_category + ' (' + panel.bl_label + ', ' + panel.__name__ + ')'
            #if name not in preferences.tool_panels:
            for pref in preferences.tool_panels:
                if panel.__name__ == pref.idname:
                    if panel.bl_category != pref.category and\
                       panel.is_registered:
                        #print(name, ' to ', pref.category)
                        panel.bl_category = pref.category
                        bpy.utils.unregister_class(panel)
                        bpy.utils.register_class(panel)
                        break
                    break

            else:
                my_item = preferences.tool_panels.add()
                my_item.name = name
                my_item.idname = panel.__name__
                my_item.category = panel.bl_category
                my_item.defa_cat = panel.bl_category

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_change_category)
    bpy.utils.unregister_class(ChangeCategoryPreferences)
    bpy.utils.unregister_class(GroupNames)
    del bpy.types.WindowManager.panel_category
    del bpy.types.WindowManager.chosen_panel

if __name__ == "__main__":
    __name__ = "ui_change_category"
    register()
