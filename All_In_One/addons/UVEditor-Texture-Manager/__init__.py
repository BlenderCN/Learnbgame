'''
Copyright (C) 2017
jim159093@gmial.com

Created by Stokes Lee

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
bl_info = {
    "name": "UVEditor Texture Manager",
    "author": "Stokes Lee",
    "version": (1, 0, 3),
    "blender": (2, 79, 0),
    "location": "UV > Properties Shelf",
    "category": "UV",
    "tracker_url": "https://github.com/StokesLee/UIEditor-Texture-Manager/issues",
}
import bpy
from bpy.types import PropertyGroup, Panel, AddonPreferences
from bpy.props import EnumProperty, BoolProperty
from bpy.app.handlers import persistent

from .utils import Manager

class Texture_Manager_Prop(PropertyGroup):
    manager = Manager()
    slot_textures_item = EnumProperty(
        name="Texture",
        description="",
        items = lambda scene, context : context.scene.Texture_Manager_Prop.manager.slot_textures_item,
        update = lambda self, context : context.scene.Texture_Manager_Prop.manager.slot_textures_item_update(int(self.slot_textures_item))
        )
    node_texture_item = EnumProperty(
        name="Texture",
        description="",
        items = lambda scene, context : context.scene.Texture_Manager_Prop.manager.texture_nodes_item,
        update = lambda self, context : context.scene.Texture_Manager_Prop.manager.texture_nodes_item_update(int(self.node_texture_item))
        )

class Texture_Manager_AddonPreferences(AddonPreferences):
    bl_idname = __name__
    
    Enable_AutoUpdate = BoolProperty(
            name="AutoUpdate",
            default=True,
            update = lambda self, context : self.register_update(self.Enable_AutoUpdate),
            )
    Enable_Engine = BoolProperty(
            name="Engine",
            default=False,
            )
    Enable_Material = BoolProperty(
            name="Material",
            default=False,
            )
    Enable_Use_nodes = BoolProperty(
            name="use_nodes",
            default=False,
            )
    def register_update(self, register):
        if register:
            if not scene_update.__name__ in [handler.__name__ for handler in bpy.app.handlers.scene_update_post]:
                bpy.app.handlers.scene_update_post.append(scene_update)
        else:
            if scene_update.__name__ in [handler.__name__ for handler in bpy.app.handlers.scene_update_post]:
                bpy.app.handlers.scene_update_post.remove(scene_update)
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "Enable_AutoUpdate")
        col.label(text="Panel Display")
        col.prop(self, "Enable_Engine")
        col.prop(self, "Enable_Material")
        col.prop(self, "Enable_Use_nodes")

class Texture_Manager_Panel(Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Texture Manager"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        Texture_Manager_Prop = context.scene.Texture_Manager_Prop
        manager = Texture_Manager_Prop.manager
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        col = layout.column()
        if manager.is_support:
            col.prop(addon_prefs,"Enable_AutoUpdate")
            if addon_prefs.Enable_Engine:
                col.prop(context.scene.render, "engine")

            material = manager.material
            ob = context.object

            if addon_prefs.Enable_Material:
                if context.object is not None:
                    is_sortable = (len(ob.material_slots) > 1)
                    rows = 1
                    if is_sortable:
                        rows = 4
                    row = col.row()
                    row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            if material is not None:
                if addon_prefs.Enable_Use_nodes:
                    if manager is not None:
                        col.prop(material, "use_nodes", icon='NODETREE')
                if material.use_nodes:
                    col.label("Texture Node")
                    col.prop(Texture_Manager_Prop,"node_texture_item")
                else:
                    if manager.render_engine == 'BLENDER_RENDER':
                        col.label("Texture Slot")
                        col.prop(Texture_Manager_Prop,"slot_textures_item")
            else:
                col.label("Do not exist material")
        else:
            col.label("Engine unspport")

@persistent
def scene_update(context):
    manager = bpy.context.scene.Texture_Manager_Prop.manager
    if manager.is_support:
        if manager.is_active_object_update:
            manager.set_first_texture()
            manager._last_active_object = manager.active_object
            manager._last_material = manager.material
            manager._last_first_image = manager.first_image
        elif manager.is_material_update:
            manager.set_first_texture()
            manager._last_material = manager.material
            manager._last_first_image = manager.first_image
        elif manager.is_first_image_update:
            manager.set_first_texture()
            manager._last_first_image = manager.first_image

def register():
    bpy.utils.register_class(Texture_Manager_Prop)
    bpy.types.Scene.Texture_Manager_Prop = bpy.props.PointerProperty(type = Texture_Manager_Prop)
    bpy.utils.register_class(Texture_Manager_AddonPreferences)
    bpy.utils.register_class(Texture_Manager_Panel)
    
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences
    if addon_prefs.Enable_AutoUpdate:
        if not scene_update.__name__ in [handler.__name__ for handler in bpy.app.handlers.scene_update_post]:
            bpy.app.handlers.scene_update_post.append(scene_update)
    
def unregister():
    if scene_update.__name__ in [handler.__name__ for handler in bpy.app.handlers.scene_update_post]:
        bpy.app.handlers.scene_update_post.remove(scene_update)
    bpy.utils.unregister_class(Texture_Manager_Panel)
    bpy.utils.unregister_class(Texture_Manager_AddonPreferences)
    del bpy.types.Scene.Texture_Manager_Prop
    bpy.utils.unregister_class(Texture_Manager_Prop)
    
if __name__ == "__main__":
    register()