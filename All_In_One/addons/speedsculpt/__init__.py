'''
Copyright (C) 2016 CEDRIC LEPILLER
pitiwazou@gmail.com

Created by CEDRIC LEPILLER

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
    "name": "SpeedSculpt",
    "description": "Create models for sculpt and manage Dyntopo sculpt",
    "author": "pitiwazou",
    "version": (0, 1, 7),
    "blender": (2, 79, 0),
    "location": "View3D",
    "wiki_url": "",
    "category": "Object" }


import bpy
from bpy.types import Menu, Operator
from bpy.props import PointerProperty, StringProperty, BoolProperty, \
    EnumProperty, IntProperty, FloatProperty, FloatVectorProperty, \
    CollectionProperty, BoolVectorProperty

from .ui import *
# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())
from .ui import *

##------------------------------------------------------  
#
# Preferences
#
##------------------------------------------------------  

def update_panel_position(self, context):
    try:
        bpy.utils.unregister_class(SpeedSculptMenu)
        bpy.utils.unregister_class(SpeedSculptMenuUI)
    except:
        pass
    
    try:
        bpy.utils.unregister_class(SpeedSculptMenuUI)
    except:
        pass
    
    if context.user_preferences.addons[__name__].preferences.Speedsculpt_tab_location == 'tools':
        SpeedSculptMenu.bl_category = context.user_preferences.addons[__name__].preferences.category
        bpy.utils.register_class(SpeedSculptMenu)
    
    else:
        bpy.utils.register_class(SpeedSculptMenuUI)


## Addons Preferences Update Panel
def update_panel(self, context):
    try:
        bpy.utils.unregister_class(SpeedSculptMenu)
    except:
        pass
    SpeedSculptMenu.bl_category = context.user_preferences.addons[__name__].preferences.category
    bpy.utils.register_class(SpeedSculptMenu)   
    
    
class SCPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
        
    prefs_tabs = EnumProperty(
        items=(('info', "Info", "Info"),
               ('options', "Options", "Options"),
               ('links', "Links", "Links")),
               default='info'
               )
                      
    category = bpy.props.StringProperty(
            name="Category",
            description="Choose a name for the category of the panel",
            default="Tools",
            update=update_panel) 
    
    show_help = BoolProperty(
            name="",
            default=True,
            description="Show the help on the Addon"
            )     
    
    auto_save = BoolProperty(
            name="",
            default=True,
            description="Auto save the scene when updating a mesh or making booleans"
            )

    smooth_mesh = BoolProperty(
        name="",
        default=True,
        description="Smooth the mesh when updating a mesh or making booleans"
    )

    fill_holes_dyntopo = BoolProperty(
        name="",
        default=False,
        description="Close holes on the mesh when updating a mesh or making booleans"
    )

    update_detail_flood_fill = BoolProperty(
        name="",
        default=True,
        description="Update Detail Flood Fill when updating a mesh or making booleans"
    )

    flat_shading = BoolProperty(
        name="",
        default=False,
        description="Use Flat shading"
    )


    #Tab Location           
    Speedsculpt_tab_location = EnumProperty(
        name = 'Panel Location',
        description = 'The 3D view shelf to use. (Save user settings and restart Blender)',
        items=(('tools', 'Tool Shelf', 'Places the Asset Management panel in the tool shelf'),
               ('ui', 'Property Shelf', 'Places the Asset Management panel in the property shelf.')),
               default='tools',
               update = update_panel_position,
               )
                                    
    def draw(self, context):
            layout = self.layout
            wm = bpy.context.window_manager
            
            
            row= layout.row(align=True)
            row.prop(self, "prefs_tabs", expand=True)
            if self.prefs_tabs == 'info':
                layout = self.layout
                layout.label("Welcome to SpeedSculpt, this addon allows you to create objects for sculpting")
                layout.label("You can make booleans, adjust the Detail Size etc")
                layout.operator("wm.url_open",
                                text="Blender Artist Post").url = "https://blenderartists.org/forum/showthread.php?405035-Addon-SpeedSculpt"

            if self.prefs_tabs == 'options':
                layout = self.layout
                box = layout.box()
                box.label("Panel Location: ")
                
                row= box.row(align=True)
                row.prop(self, 'Speedsculpt_tab_location', expand=True)
                row = box.row()
                if self.Speedsculpt_tab_location == 'tools':
                    split = box.split()
                    col = split.column()
                    col.label(text="Change Category:")
                    col = split.column(align=True)
                    col.prop(self, "category", text="") 

                split = box.split()
                col = split.column()
                col.label("Show Help")
                col = split.column(align=True)  
                col.prop(self, "show_help") 
                
                split = box.split()
                col = split.column()
                col.label("Auto Save Scene")
                col = split.column(align=True)  
                col.prop(self, "auto_save")

                split = box.split()
                col = split.column()
                col.label("UPDATE MESH OPTIONS :")

                split = box.split()
                col = split.column()
                col.label("Smooth the Mesh")
                col = split.column(align=True)
                col.prop(self, "smooth_mesh")

                split = box.split()
                col = split.column()
                col.label("Update the Mesh")
                col = split.column(align=True)
                col.prop(self, "update_detail_flood_fill")

                split = box.split()
                col = split.column()
                col.label("Fill Holes")
                col = split.column(align=True)
                col.prop(self, "fill_holes_dyntopo")

                split = box.split()
                col = split.column()
                col.label("Flat Shading")
                col = split.column(align=True)
                col.prop(self, "flat_shading")
                  

                
            if self.prefs_tabs == 'links':
                layout.label(text="Support")
                layout.operator("wm.url_open", text="Discord").url = "https://discord.gg/ctQAdbY"
                layout.separator()
                layout.label(text="Addons")
                layout.operator("wm.url_open", text="Asset Management").url = "https://gumroad.com/l/kANV"
                layout.operator("wm.url_open", text="SpeedFlow").url = "https://gumroad.com/l/speedflow"
                layout.operator("wm.url_open", text="SpeedSculpt").url = "https://gumroad.com/l/SpeedSculpt"
                layout.operator("wm.url_open", text="SpeedRetopo").url = "https://gumroad.com/l/speedretopo"
                layout.operator("wm.url_open",
                                text="RMB Pie Menu v2").url = "https://gumroad.com/l/wazou_rmb_pie_menu_v2"
                layout.operator("wm.url_open", text="Smart cursor").url = "https://gumroad.com/l/smart_cursor"
                layout.separator()
                layout.label(text="Web")
                layout.operator("wm.url_open", text="Pitiwazou.com").url = "http://www.pitiwazou.com"
                layout.operator("wm.url_open", text="Pistiwique").url = "https://github.com/pistiwique"
                layout.operator("wm.url_open",
                                text="Wazou's Ghitub").url = "https://github.com/pitiwazou/Scripts-Blender"
                layout.operator("wm.url_open", text="BlenderLounge Forum ").url = "http://blenderlounge.fr/forum/"



                # register
##################################

import traceback

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    update_panel(None, bpy.context)   
    
    update_panel_position(None, bpy.context)
    
def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
