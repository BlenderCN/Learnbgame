'''
Copyright (C) 2016
pitiwazou@hotmail.com

Created by CEDRIC LEPILLER, JEREMY LEGIGAN

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
    "name": "Speedflow",
    "description": "Improve your workflow with speedflow",
    "author": "cedric lepiller, pistiwique",
    "version": (0, 1, 0),
    "blender": (2, 77, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }


import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty)
from .utils.properties import *
from .ui import *


# load and reload submodules
##################################

#import importlib
#from .utils import developer_utils
#importlib.reload(developer_utils)
#modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


## Addons Preferences Update Panel

def update_Speedflow(self, context):
    try:
        bpy.utils.unregister_class(Speedflow)
    except:
        pass
    if context.user_preferences.addons[__name__].preferences.enabled_panel:
        Speedflow.bl_category = context.user_preferences.addons[__name__].preferences.category
        bpy.utils.register_class(Speedflow)

def update_menu_type(self, context):
    try:
        unregister()
    except:
        pass
    register()        
                    
class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
        
    prefs_tabs = EnumProperty(
        items=(('options', "Options", "Options"),
               ('docs', "Doc", "Documentation"),
               ('links', "Links", "Links")),
               default='options'
               )
    
    work_tool = EnumProperty(
        items=(('mouse', "Mouse", ""),
            ('pen', "Graphic tablet", "")),
            default='pen'
            )
            
            
    # MODAL OPTION
    modal_speed = FloatProperty(
            name="",
            default=1.0,
            min=0.001, max=1000
            )
    
    
    # UI OPTIONS
    enabled_panel = BoolProperty(
            default=False,
            update=update_Speedflow
            )
            
    category = bpy.props.StringProperty(
        name="Category",
        description="Choose a name for the category of the panel",
        default="Tools",
        update=update_Speedflow)
    
    choose_menu_type = EnumProperty(
        items=(('pie', "Pie menu", "Pie menu"),
               ('menu', "Normal Menu", "Normal Menu")),
               default='pie',
                update=update_menu_type
               )
    
    # BEVEL OPTIONS
    subdiv_mode = BoolProperty(
            default=True
            )
    
    sub_bevel_width = FloatProperty(
            name="",
            default=0.04
            )
                   
    sub_bevel_segments = FloatProperty(
            name="",
            default=2,
            min=1, max=13
            )
        
    sub_bevel_profil = FloatProperty(
            name="",
            default=1.0,
            min=0.0, max=1.0
            )
    
    nosub_bevel_width = FloatProperty(
            name="",
            default=0.01
            )
     
    nosub_bevel_segments = FloatProperty(
            name="",
            default=4,
            min=1, max=13
            )
     
    nosub_bevel_profil = FloatProperty(
            name="",
            default=0.7,
            min=0.0, max=1.0
            )
    
    wire_bevel = BoolProperty(
            name="",
            default=True,
            description="Keep the wire coming out of the modal bevel"
            )
            
    
    # TUBIFY OPTIONS
    depth_value = FloatProperty(
            name="",
            default=0.1
            )
    
    reso_u = FloatProperty(
            name="",
            default=12
            )
            
    reso_v = FloatProperty(
            name="",
            default=2
            )
            
            
    # ARRAY OPTIONS
    offset_type = EnumProperty(
        items=(('relative', "Relative", ""),
               ('constant', "Constant", "")),
               default='relative'
               )
               
               
   # TEXT OPTIONS           
    text_color = FloatVectorProperty(
            name="", 
            default=(1, 1, 1), 
            min=0, max=1,
            subtype='COLOR'
            )
     
    text_color_1 = FloatVectorProperty(
            name="", 
            default=(0.5, 1, 0), 
            min=0, max=1,
            subtype='COLOR'
            )
     
    text_color_2 = FloatVectorProperty(
            name="", 
            default=(0, 0.7, 1), 
            min=0, max=1,
            subtype='COLOR'
            )
     
    text_size = IntProperty(
            name="",
            default=20,
            min=10, max=50
            )
     
    keys_size = IntProperty(
            name="",
            default=20,
            min=10, max=50
            )
     
    text_shadow = BoolProperty(
            default=True
            )
     
    shadow_color = FloatVectorProperty(
            name="", 
            default=(0.0, 0.0, 0), 
            min=0, max=1,
            subtype='COLOR'
            )
     
    shadow_alpha = FloatProperty(
            name="",
            default=1,
            min=0, max=1
            )
     
    offset_shadow_x = IntProperty(
            name="",
            default=2,
            min=-5, max=5)
     
    offset_shadow_y = IntProperty(
            name="",
            default=-2,
            min=-5, max=5
            )
     
    text_pos_x = IntProperty(
            name="",
            default=510,
            min=0, max=2000
            )
     
    text_pos_y = IntProperty(
            name="",
            default=250,
            min=0, max=1000
            )
    
    
    def draw(self, context):
        layout = self.layout
        wm = bpy.context.window_manager
        
        
        row= layout.row(align=True)
        row.prop(self, "prefs_tabs", expand=True)
        if self.prefs_tabs == 'options':
            
            # Mouse/pen options
            box = layout.box()
            split = box.split()
            col = split.column()
            col.label("Choose your work tool :")
            col = split.column(align=True)
            col.prop(self, 'work_tool', expand=True)

            # MODAL OPTION
            box = layout.box()
            row = box.row(align=True)
            row.label(text="MODAL OPTION")
            
            row = box.row(align=True)
            row.label(text="Modal Speed")
            row.prop(self, "modal_speed")
            
            # UI OPTIONS
            wm = bpy.context.window_manager
            box = layout.box()
            row = box.row(align=True)
            row.label(text="UI OPTIONS")
            
            row = box.row(align=True)
            row.label("Enable Panel :")
            row.prop(self, 'enabled_panel', expand=True, text=" ")
            
            if self.enabled_panel:
                split = box.split()
                col = split.column()
                col.label(text="Category:")
                col = split.column(align=True)
                col.prop(self, "category", text="") 
                
            
            #Menu Type
            split = box.split()
            col = split.column()
            col.label("Choose Menu type :")
            col = split.column(align=True)
            col.prop(self, 'choose_menu_type', expand=True)

            row = box.row(align=True)
            row.label("Save preferences and restart blender to apply these settings", icon='ERROR')
            
            # Bevel options
            box = layout.box()
            row = box.row(align=True)
            row.label(text="BEVEL OPTIONS")
            
            
            row = box.row(align=True)
            row.label(text="Subdiv Mode as default")
            row.prop(self, "subdiv_mode", text="      ")
            
            
            row = box.row(align=True)
            row.label(text="Subdiv Mode Options --------------------------------")
            
            row = box.row(align=True)
            row.label(text="         - Subdiv bevel width")
            row.prop(self, "sub_bevel_width")
            
            
            row = box.row(align=True)
            row.label(text="         - Subdiv segments")
            row.prop(self, "sub_bevel_segments")
            
            row = box.row(align=True)
            row.label(text="         - Subdiv profil")
            row.prop(self, "sub_bevel_profil")
            
            
            row = box.row()
            row.separator()
            
            row = box.row(align=True)
            row.label(text="No Subdiv Mode Options -----------------------------")
            row = box.row(align=True)
            row.label(text="         - No Subdiv bevel width")
            row.prop(self, "nosub_bevel_width")
             
             
            row = box.row(align=True)
            row.label(text="         - No Subdiv segments")
            row.prop(self, "nosub_bevel_segments")
             
            row = box.row(align=True)
            row.label(text="         - No Subdiv profil")
            row.prop(self, "nosub_bevel_profil")
            
            row = box.row()
            row.separator()
            
            row = box.row(align=True)
            row.label(text="Keep Wire")
            row.prop(self, "wire_bevel", text="      ")
            
            # Tubify options
            box = layout.box()
            row = box.row(align=True)
            row.label(text="TUBIFY OPTIONS")
             
            row = box.row(align=True)
            row.label(text="Depth")
            row.prop(self, "depth_value")
             
            row = box.row(align=True)
            row.label(text="Resolution U")
            row.prop(self, "reso_u")
             
            row = box.row(align=True)
            row.label(text="Resoltion V")
            row.prop(self, "reso_v")
            
            # Array options
            box = layout.box()
            split = box.split()
            row = box.row(align=True)
            row.label(text="ARRAY OPTIONS")
            
            split = box.split()
            col = split.column()
            col.label("Offset type :")
            col = split.column(align=True)
            col.prop(self, 'offset_type', expand=True)
            
            # Texts
            box = layout.box()
            row = box.row(align=True)
            row.label(text="TEXTS OPTIONS")
            
            row = box.row(align=True)
            row.label(text="Text Color")
            row.prop(self, "text_color")
            
            row = box.row(align=True)
            row.label(text="Text Color 1")
            row.prop(self, "text_color_1")
            
            row = box.row(align=True)
            row.label(text="Text Color 2")
            row.prop(self, "text_color_2")
            
            row = box.row(align=True)
            row.label(text="Text Size")
            row.prop(self, "text_size")
            
            row = box.row(align=True)
            row.label(text="Text X position")
            row.prop(self, "text_pos_x")
            
            row = box.row(align=True)
            row.label(text="Text Y position")
            row.prop(self, "text_pos_y")
            
            row = box.row(align=True)
            row.label(text="Keys Size")
            row.prop(self, "keys_size")
            
            row = box.row()
            row.separator()
            
            #Shadows
            row = box.row(align=True)
            row.label(text="SHADOWS")

            row = box.row(align=True)
            row.label(text="Activate Shadows")
            row.prop(self, "text_shadow", text="      ")
            
            if self.text_shadow:
                row = box.row(align=True)
                row.label(text="Shadows Color")
                row.prop(self, "shadow_color")
                
                row = box.row(align=True)
                row.label(text="Shadows Transparency")
                row.prop(self, "shadow_alpha")
                
                row = box.row(align=True)
                row.label(text="Offset Shadows X")
                row.prop(self, "offset_shadow_x")
                
                row = box.row(align=True)
                row.label(text="Offset Shadows Y")
                row.prop(self, "offset_shadow_y")    
            
        if self.prefs_tabs == 'docs':
            row = layout.row()
            row.label(text="Soon available")
            
        #URls
        if self.prefs_tabs == 'links':
            row = layout.row()
            row.operator("wm.url_open", text="Pistiwique").url = "https://github.com/pistiwique"
            row = layout.row()
            row.operator("wm.url_open", text="Pitiwazou.com").url = "http://www.pitiwazou.com"
            row = layout.row()
            row.operator("wm.url_open", text="Wazou's Ghitub").url = "https://github.com/pitiwazou/Scripts-Blender"
            row = layout.row()
            row.operator("wm.url_open", text="BlenderLounge Forum ").url = "http://blenderlounge.fr/forum/"
        

# register
##################################

import traceback

addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
    if bpy.context.user_preferences.addons[__name__].preferences.choose_menu_type == 'pie':
        kmi = km.keymap_items.new('wm.call_menu_pie', 'Q', 'PRESS', shift= True, ctrl= True)
        kmi.properties.name = "pie.speedflow_pie_menu" 
    else:
        kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS', shift= True, ctrl= True)
        kmi.properties.name = "speedflow_simple_menu"
    addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

 
def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    
    register_keymaps()
    bpy.types.WindowManager.MPM = bpy.props.PointerProperty(type=ModalPieMenuCollectionGroup)
        
#    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    update_Speedflow(None, bpy.context)    

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()
    
    unregister_keymaps()
    del bpy.types.WindowManager.MPM

#    print("Unregistered {}".format(bl_info["name"]))