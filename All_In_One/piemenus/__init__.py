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


""" Copyright 2011 GPL licence applies"""

bl_info = {
    "name": "Pie: Menus",
    "description": "Pie Menus for various functionality",
    "author": "Dan Eicher, Sean Olson, Patrick Moore",
    "version": (1, 0, 1),
    "blender": (2, 6, 6),
    "location": "View3D - Set Keybindings in File->Userprefs->Input Tab->(Search: \"pie\")",
    "warning": '',  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

#we need to add the piemenus subdirectory to be searched for imports
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'piemenus'))

#this is the guts of the script
import pie_menu
import pie_menu_utils

#import the individual menus
import pie_viewMenu
import pie_modeMenu
import pie_selectionMenu
import pie_shadeMenu
import pie_pivotMenu
import pie_strokesMenu
import pie_sculptTextureMenu
import pie_greyBrushes
import pie_redBrushes
import pie_tanBrushes
import pie_deleteMenu
import pie_proportionalMenu
import pie_BrushControl
import pie_manipulatorMenu
import pie_particleCombMenu
#import pie_PiePan
#import pie_repeatMenu

import bpy
import addon_utils
from bpy.props import *
from bpy.app.handlers import persistent
from rna_prop_ui import PropertyPanel
from bpy.types import AddonPreferences

 
 
class PieMenuPreferences(AddonPreferences):
    bl_idname = __name__
    

        
    PiePrefs = BoolProperty(
                name="Preferences",
                description="Show Pie Options",
                default=True
                )
                
    pieInnerRadius = IntProperty(
                name="Pie Inner Radius",
                description="Amount that mouse can travel before activating pie slices",
                default=20
                )
    pieOuterRadius = IntProperty(
                name="Pie Outer Radius",
                description="Amount that mouse can travel beyond pies before deactivating menu",
                default=300
                )
    
    double_size = BoolProperty(
                name="Double Size",
                description="Hack for IPS displays",
                default=False
                )
            
    clockBool = BoolProperty(
                name="Clock",
                description="Show pointer at center of pie",
                default=True
                )
                
    pieIconBindcode = IntProperty(
                name = "GL Bind Code",
                description = "used so we only have to load texture to openGL as few times as possible",
                default = 0
                )
    
    pieRobustCleanup = BoolProperty(
                name = "Delete icon image before saving file",
                description = "False if you are working with it otherwise it will be gone",
                default = True
                )
    
    pieBorderDelay = FloatProperty(
                name = "Border Delay",
                description = "How long to wait for border shift to take effect",
                default = .3,
                min = 0,
                max = 5,
                step = 5,
                precision = 2  
                )
    
    pieSquish = FloatProperty(
                name = "Pie Squish",
                description = "0 more oval, 1 more circular",
                default = .5,
                min = 0,
                max = 1,
                step = 10,
                precision = 1  
                )
    
    pieDiamond = FloatProperty(
                name = "Pie Diamond",
                description = "0 more circular, 1 more diamond",
                default = .8,
                min = 0,
                max = 1,
                step = 10,
                precision = 1  
                )
    
    pieThetaShift = FloatProperty(
                name = "Pie Theta Shift",
                description = "Just Gotta Play with this one",
                default = .3,
                min = 0,
                max = 1,
                step = 10,
                precision = 1  
                )
        
    def draw(self, context):
        layout = self.layout
        #split = layout.split()
 
        box = layout.box().column(align=False)
        box.prop(self,'PiePrefs')
        if self.PiePrefs:
            #boxrow=box.row()
            #boxrow.template_list("SCENE_UL_pie_menus","",context.scene, "pie_settings", context.scene, "pie_settings_index", rows=5)
            
            #boxrow=box.row()
            #subrow = boxrow.row(align=True)
            #subrow.operator("activatepie.button", text="On")
            #subrow.operator("disactivatepie.button", text="Off")
            
            #boxrow=box.row()
            #boxrow.operator("pie.keybinding", text="Keybindings")

            boxrow=box.row()
            boxrow.label(text="General Preferences")

            boxrow=box.row()
            boxrow.prop(self, 'clockBool')
            
            boxrow=box.row()
            boxrow.prop(self, 'pieOuterRadius')
            
            boxrow=box.row()
            boxrow.prop(self, 'pieInnerRadius')
            
            boxrow=box.row()
            boxrow.prop(self, 'double_size')
            
            boxrow=box.row()
            boxrow.prop(self, 'pieRobustCleanup')
            
            boxrow=box.row()
            boxrow.prop(self, 'pieBorderDelay')
            
            boxrow=box.row()
            boxrow.prop(self, 'pieSquish')
            
            boxrow=box.row()
            boxrow.prop(self, 'pieDiamond')
            
            boxrow=box.row()
            boxrow.prop(self, 'pieThetaShift')
#collection class to keep track of individual pie menu variables
class PiePropertyGroup(bpy.types.PropertyGroup):
    name = StringProperty(default="")    
    activate = BoolProperty(default=True)


class PieMenuSettings(bpy.types.PropertyGroup):
    
    @classmethod
    def register(cls):
        bpy.types.Scene.piemenus = PointerProperty(
                name="Pie Settings",
                description="Pie settings & Tools",
                type=cls,
                )
    @classmethod
    def initSceneProperties(scn):
        if not bpy.data.scenes[0].pie_settings:
            pie_set = bpy.data.scenes[0].pie_settings
            
            pie_item = pie_set.add()
            pie_item.name = "[ON] 3DView - View Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] 3DView - Mode Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] 3DView - Shade Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] 3DView - Pivot Menu"
            
            pie_item = pie_set.add()
            pie_item.name = "[ON] 3dView - Proportional Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] Edit - Delete Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] Edit - Selection Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] Sculpt - Grey Brushes Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] Sculpt - Red Brushes Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] Sculpt - Tan Brushes Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] Sculpt - Texture Menu"

            pie_item = pie_set.add()
            pie_item.name = "[ON] Sculpt - Strokes Menu"
            
            pie_item = pie_set.add()
            pie_item.name = "[ON] Sculpt - Brush Control Menu"
            
            pie_item = pie_set.add()
            pie_item.name = "[ON] 3DView - Manipulator Menu"
            
            pie_item = pie_set.add()
            pie_item.name = "[ON] 3DView - Particle Comb Menu"
            
            #pie_item = pie_set.add()
            #pie_item.name = "[ON] 3DView - Repeat Menu"
            
            #pie_item = pie_set.add()
            #pie_item.name = "[OFF] 3DView - PiePan Menu"
        
    #Updated all the keybindings..seems like the decorator isn't required yet it works for initSceneProperties so whatever
    @classmethod
    def updateBinds(scn): 

        for i in range(len(bpy.data.scenes[0].pie_settings)):
            name=bpy.data.scenes[0].pie_settings[i].name
            if not name.find('View Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_viewMenu.setBind()
                else:               
                    pie_viewMenu.removeBind()

            if not name.find('Mode Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_modeMenu.setBind()
                else:               
                    pie_modeMenu.removeBind()

            if not name.find('Shade Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_shadeMenu.setBind()
                else:               
                    pie_shadeMenu.removeBind()

            if not name.find('Pivot Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_pivotMenu.setBind()
                else:               
                    pie_pivotMenu.removeBind()

            if not name.find('Delete Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_deleteMenu.setBind()
                else:               
                    pie_deleteMenu.removeBind()

            if not name.find('Selection Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_selectionMenu.setBind()
                else:               
                    pie_selectionMenu.removeBind()

            if not name.find('Strokes Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_strokesMenu.setBind()
                else:               
                    pie_strokesMenu.removeBind()

            if not name.find('Texture Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_sculptTextureMenu.setBind()
                else:               
                    pie_sculptTextureMenu.removeBind()
            
            if not name.find('Grey Brushes Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_greyBrushes.setBind()
                else:               
                    pie_greyBrushes.removeBind()

            if not name.find('Red Brushes Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_redBrushes.setBind()
                else:               
                    pie_redBrushes.removeBind()

            if not name.find('Tan Brushes Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_tanBrushes.setBind()
                else:               
                    pie_tanBrushes.removeBind()
            if not name.find('Proportional Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_proportionalMenu.setBind()
                else:               
                    pie_proportionalMenu.removeBind()
                    
            if not name.find('Brush Control Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_BrushControl.setBind()
                else:               
                    pie_BrushControl.removeBind()
       
            if not name.find('Manipulator Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_manipulatorMenu.setBind()
                else:               
                    pie_manipulatorMenu.removeBind()
                    
            if not name.find('Particle Comb Menu')==-1:
                if bpy.data.scenes[0].pie_settings[i].activate:               
                    pie_particleCombMenu.setBind()
                else:               
                    pie_particleCombMenu.removeBind()
                    
            #if not name.find('Repeat Menu')==-1:
                #if bpy.context.scene.pie_settings[i].activate:               
                    #pie_repeatMenu.setBind()
                #else:               
                    #pie_repeatMenu.removeBind().
                    
            #if not name.find('PiePan Menu')==-1:
                #if bpy.data.scenes[0].pie_settings[i].activate:               
                    #pie_PiePan.setBind()
                #else:               
                    #pie_PiePan.removeBind()    

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.piemenus        
    
class SCENE_UL_pie_menus(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        sce = data
        pie = item
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), this will also make the row easily
            # selectable in the list!
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            layout.label(pie.name)
            #layout.prop(pie.activate)
            #row = layout.row()
            #row.props(pie.activate)
            
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon_value="NODE")

# this the main properties panel panel
class piemenus_panel(bpy.types.Panel):
    bl_label = "Pie Menus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}   
      

    def draw(self, context):
        layout = self.layout
        #split = layout.split()
 
        box = layout.box().column(align=False)


        boxrow=box.row()
        boxrow.template_list("SCENE_UL_pie_menus","",context.scene, "pie_settings", context.scene, "pie_settings_index", rows=5)
            
        boxrow=box.row()
        subrow = boxrow.row(align=True)
        subrow.operator("activatepie.button", text="On")
        subrow.operator("disactivatepie.button", text="Off")
            
        boxrow=box.row()
        boxrow.operator("pie.keybinding", text="Keybindings")

            
#Button to pull up keybindings window with relevent keybindings shown            
class OBJECT_OT_KeybindsButton(bpy.types.Operator):
    bl_idname = "pie.keybinding"
    bl_label = "View Pie Menu Keybinds"

    def execute(self, context):
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        context.user_preferences.active_section='INPUT'
        context.window_manager.windows[1].screen.areas[0].spaces[0].filter_text='Pie'
        return{'FINISHED'}  

#Button to Activate Pie Menus
class OBJECT_OT_ActivatePieButton(bpy.types.Operator):
    bl_idname = "activatepie.button"
    bl_label = "On"
    
    @classmethod
    def poll(self,context):
        return len(context.scene.pie_settings) > 0
         
    def execute(self, context):
        context.scene.pie_settings[bpy.context.scene.pie_settings_index].activate=True
        context.scene.pie_settings[bpy.context.scene.pie_settings_index].name=bpy.context.scene.pie_settings[bpy.context.scene.pie_settings_index].name.replace('[OFF]', '[ON]')
        context.scene.piemenus.updateBinds()
        return{'FINISHED'}

#Button to Deactivate Pie Menus
class OBJECT_OT_DisactivatePieButton(bpy.types.Operator):
    bl_idname = "disactivatepie.button"
    bl_label = "Off"
     
    @classmethod
    def poll(self,context):
        return len(context.scene.pie_settings) > 0
    
    def execute(self, context):
        bpy.context.scene.pie_settings[bpy.context.scene.pie_settings_index].activate=False
        bpy.context.scene.pie_settings[bpy.context.scene.pie_settings_index].name=bpy.context.scene.pie_settings[bpy.context.scene.pie_settings_index].name.replace('[ON]', '[OFF]')
        context.scene.piemenus.updateBinds()
        return{'FINISHED'}                

@persistent
def handler_post_load(dummy):
    print('debug post load handler')
    if addon_utils.check("piemenus")[1]:
        print('made bpy.data ready for pies')
        #load the icon image in case it's not there
        img = bpy.data.images.get('blender_icons_x2.png')
        if not img:
            #load the icon image into blend data.                
            addons_folder = os.path.dirname(__file__)
            icondir=os.path.join(addons_folder, 'icons','blender_icons')
            pie_menu_utils.icons_to_blend_data(icondir)
            img = bpy.data.images['blender_icons_x2.png']
        img.gl_load()
        
        #set the icon loaded property to True and remember the bindcode
        scn = bpy.context.scene
        scn.piemenus.pieIconBindcode = img.bindcode
        

        if not len(scn.pie_settings):
            scn.piemenus.initSceneProperties()

@persistent
def handler_pre_save(dummy):
    #delete the icon image
    settings = bpy.context.user_preferences.addons['piemenus'].preferences
    
    if  settings.pieRobustCleanup:
        img = bpy.data.images.get("blender_icons_x2.png")
        if img:
            img.user_clear()
            bpy.data.images.remove(img)
            
        #set the icon loaded property to false
        scn.piemenus.PieIconBindcode = 0
        
        
        print('removed all traces of pie menus....boyscout ninja addon leaves no trace')
    


#need to put the post load handler so the image is back
#bpy.app.handlers.save_post.append(handler_post_load)
     
def setup(s):
    PieMenuSettings.initSceneProperties(bpy.data.scenes[0])
    PieMenuSettings.updateBinds()
    bpy.app.handlers.scene_update_pre.remove(setup)
    
def register():
    bpy.utils.register_class(PieMenuPreferences)    
    bpy.utils.register_class(PiePropertyGroup)
    bpy.utils.register_class(PieMenuSettings)
    bpy.utils.register_class(SCENE_UL_pie_menus)
    
    bpy.app.handlers.load_post.append(handler_post_load)
    bpy.app.handlers.save_pre.append(handler_pre_save)
    
    bpy.utils.register_module(__name__)

    pie_menu_utils.register()
    pie_modeMenu.register()             
    pie_selectionMenu.register() 
    pie_deleteMenu.register()        
    pie_viewMenu.register()             
    pie_shadeMenu.register()            
    pie_pivotMenu.register()            
    pie_strokesMenu.register()          
    pie_sculptTextureMenu.register()    
    pie_greyBrushes.register()
    pie_redBrushes.register()
    pie_tanBrushes.register()
    pie_proportionalMenu.register()
    pie_BrushControl.register()
    pie_manipulatorMenu.register()
    pie_particleCombMenu.register()
    #pie_repeatMenu.register()
    #pie_PiePan.register()
    
    #places to store stuff
    bpy.types.Scene.pie_settings = CollectionProperty(type=PiePropertyGroup)
    bpy.types.Scene.pie_settings_index = IntProperty()

    #PieMenuSettings.initSceneProperties(bpy.data.scenes[0])
    #PieMenuSettings.updateBinds()
    #bpy.app.handlers.scene_update_pre.append(setup)
    
def unregister():
    bpy.app.handlers.save_pre.remove(handler_pre_save)
    bpy.app.handlers.load_post.remove(handler_post_load)
    #bpy.app.handlers.save_post.remove(handler_post_load)
    
    bpy.utils.unregister_class(PieMenuSettings)
    bpy.utils.unregister_class(SCENE_UL_pie_menus)
    bpy.utils.unregister_module(__name__)

    pie_menu_utils.unregister()
    pie_modeMenu.unregister()
    pie_selectionMenu.unregister()
    pie_deleteMenu.unregister()  
    pie_viewMenu.unregister()
    pie_shadeMenu.unregister()
    pie_pivotMenu.unregister()
    pie_strokesMenu.unregister()
    pie_sculptTextureMenu.unregister()
    pie_greyBrushes.unregister()
    pie_redBrushes.unregister()
    pie_tanBrushes.unregister()
    pie_proportionalMenu.unregister()
    pie_manipulatorMenu.unregister()
    pie_particleCombMenu.unregister()
    pie_BrushControl.unregister()
    #pie_repeatMenu.unregister()
    #pie_PiePan.unregister()
    
    #icon_util.clean_icon_texture()

    
if __name__ == "__main__":
    register()
