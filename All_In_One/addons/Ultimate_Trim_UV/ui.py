# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
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

import bpy

from . import global_def
from . import operator_manager
from bpy.props import EnumProperty
from bl_operators.presets import AddPresetBase

##############
#   UI
##############

#Setup preset adding/removing operator and define what parameters are stored in presets
class UV_OT_ultimate_trim_preset_add(AddPresetBase, bpy.types.Operator):
        '''Add or remove an Ultimate Trim Preset'''
        bl_idname = "uv.ultimate_trim_preset_add"
        bl_label = "Add Ultimate Trim Preset"
        bl_options = {'REGISTER', 'UNDO'}
        preset_menu = "UV_MT_ultimate_trim_uv_presets"
        preset_subdir = "ultimate_trim_uv_preset"

        preset_defines = [
            "scene = bpy.context.scene",
            "window = bpy.context.window_manager"
        ]

        preset_values = [
            "scene.numTrims",
            "scene.trimRes",
            "window.uv_padding",
            "window.trim_pixel_height_1",
            "window.trim_pixel_height_2",
            "window.trim_pixel_height_3",
            "window.trim_pixel_height_4",
            "window.trim_pixel_height_5",
            "window.trim_pixel_height_6",
            "window.trim_pixel_height_7",
            "window.trim_pixel_height_8",
            "window.trim_pixel_height_9",
            "window.trim_pixel_height_10",
            "window.trim_pixel_height_11",
            "window.trim_pixel_height_12",
        ]

#Create dropdown menu for selecting added presets
class UV_MT_ultimate_trim_uv_presets(bpy.types.Menu):
    '''Presets for Ultimate Trim Settings'''
    bl_label = "Presets"
    bl_idname = "UV_MT_ultimate_trim_uv_presets"
    preset_subdir = "ultimate_trim_uv_preset"
    preset_operator = "script.execute_preset"

    draw = bpy.types.Menu.draw_preset

#Create settings menu to allow user to configure custom trim sheet sizes.
class IMAGE_PT_ultimate_trim_settings(bpy.types.Panel):
    bl_label = "Ultimate Trim Settings"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Ultimate Trim"
    #new items below for blender 2.8 update   
    bl_context = 'mesh_edit'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sima = context.space_data
        return sima.show_uvedit and \
            not (context.tool_settings.use_uv_sculpt
                 or context.scene.tool_settings.use_uv_select_sync)

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        
        #Create Presets label, dropdown, and add/remove buttons
        col = layout.column_flow(align=True)
        col.label(text="Trim Presets:")
        row = col.row(align=True)
        row.menu("UV_MT_ultimate_trim_uv_presets",
                 text=bpy.types.UV_MT_ultimate_trim_uv_presets.bl_label)
        
        #Need to figure out out to add/remove presets in 2.8 This is broken for the moment
        row.operator("uv.ultimate_trim_preset_add", text="", icon='ADD')
        row.operator("uv.ultimate_trim_preset_add", text="", icon='REMOVE').remove_active = True

        #Create dropdowns to allow user to select number to trim segments, and total vertical resolution of texture 
        layout.prop(scn, "numTrims",)
        layout.prop(scn, "trimRes",)

        ##global trimTotal 

        if context.scene.numTrims == '2_trims':
            global_def.trimTotal = 2
        elif context.scene.numTrims == '3_trims':
            global_def.trimTotal = 3
        elif context.scene.numTrims == '4_trims':
            global_def.trimTotal = 4
        elif context.scene.numTrims == '5_trims':
            global_def.trimTotal = 5
        elif context.scene.numTrims == '6_trims':
            global_def.trimTotal = 6
        elif context.scene.numTrims == '7_trims':
            global_def.trimTotal = 7
        elif context.scene.numTrims == '8_trims':
            global_def.trimTotal = 8
        elif context.scene.numTrims == '9_trims':
            global_def.trimTotal = 9
        elif context.scene.numTrims == '10_trims':
            global_def.trimTotal = 10
        elif context.scene.numTrims == '11_trims':
            global_def.trimTotal = 11
        else: 
            global_def.trimTotal = 12

        for y in range(1, (global_def.trimTotal + 1)):
            #Make row for location and size customization sliders, make sliders
            layout.label(text="Index {} Pixel Height :".format(y))
            row = layout.row(align=True)
            row.prop(context.window_manager, "trim_pixel_height_{}".format(y))

#Create Ultimate Trim buttons menu for operators that respect settings setup in settings menu. 
#Also includes padding input
class IMAGE_PT_ultimate_trim_uv(bpy.types.Panel):
    
    
    bl_label = "Ultimate Trim UV"
    bl_space_type = 'IMAGE_EDITOR'
    #two modified items below for blender 2.8
    bl_region_type = 'UI'
    bl_category = "Ultimate Trim"
    #New two items below for blender 2.8
    bl_context = 'mesh_edit'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sima = context.space_data
        return sima.show_uvedit and \
            not (context.tool_settings.use_uv_sculpt
                 or context.scene.tool_settings.use_uv_select_sync)

    def draw(self, context):
        scn = context.scene
        layout = self.layout

        #Create label and user input for UV Padding multiplier
        layout.label(text="UV Padding Multiplier")
        layout.prop(context.window_manager, "uv_padding")

        #Create Trim UI elements based on the number of Trims the user selects from the drop down menu
        for x in range(1, (global_def.trimTotal + 1)):
                ##################
                # Trim Index loop
                ##################
                layout.label(text="Trim Index {}:".format(x))

                #Grab pixel height set by user for left, right, and center buttons
                pixelHeight = getattr(context.window_manager, "trim_pixel_height_{}".format(x))
                
                #Calculate the percentage of uv space a trim takes up and store it in a global dict
                global_def.trimHeight['{}'.format(x)] = pixelHeight / int(context.scene.trimRes)
            
                #Make Row for top 3 buttons
                row = layout.row(align=True)
            
                #Create left button
                customize = row.operator("uv.trim_left_id_{}".format(x), text="Left")
                #Allow margin float in UI to affect the output of the button
                customize.uvMargin = context.window_manager.uv_padding
                #Sets the button's size ratio based on the needed info from global dict
                customize.sizeRatio = global_def.trimHeight['{}'.format(x)]
                                
                #Create center button
                customize = row.operator("uv.trim_center_id_{}".format(x), text="Center")
                #Allow margin float in UI to affect the output of the button
                customize.uvMargin = context.window_manager.uv_padding
                #Sets the button's size ratio based on the needed info from global dict
                customize.sizeRatio = global_def.trimHeight['{}'.format(x)]
                   
                
                #Create right button
                customize = row.operator("uv.trim_right_id_{}".format(x), text="Right")
                #Allow margin float in UI to affect the output of the button
                customize.uvMargin = context.window_manager.uv_padding
                #Sets the button's size ratio based on the needed info from global dict
                customize.sizeRatio = global_def.trimHeight['{}'.format(x)]
                
                
#################################
#################################
# REGISTRATION
#################################
#################################


_om = operator_manager.om
_om.addOperator(UV_OT_ultimate_trim_preset_add)
_om.addOperator(UV_MT_ultimate_trim_uv_presets)
_om.addOperator(IMAGE_PT_ultimate_trim_settings)
_om.addOperator(IMAGE_PT_ultimate_trim_uv)


