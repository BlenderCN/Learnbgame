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

bl_info = {
    "name": "Enrich - Addon for Visual Compositing",
    "author": "Akash Hamirwasia",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "UV Image Editor > Tools Panel > Enrich",
    "description": "Quickly Complete Compositing using Photo-styled Presets within Blender",
    "warning": "",
    "wiki_url": "http://www.blenderskool.cf/enrich-add-on-documentation/",
    "tracker_url": "http://blenderschool.cf/enrich-report-tracker",
    "category": "Render"}

import os
import bpy
import urllib.request
import zipfile, shutil, webbrowser, datetime
from . import composite_nodes_generate
from . import custom_install
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       CollectionProperty
                       )
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper
                                 )

preview_collections = {}
items = [] #stores the name of the thumbnail
enum_items = []
open_windows = []
changelog_list = []
version = 1.0
#updates the directory to generate the thumbnails
def enum_previews_from_directory_items(self, context):
    pcoll = preview_collections.get("main")
    if not pcoll:
        return []

    if self.enrich_preview_thumbs_dir == "":
        pass
    return pcoll.enrich_preview_thumbs

#generates the thumbnails for the presets
def preview_dir_update(wm, context):
    print("wm.enrich_preview_thumbs_dir = %s" % wm.enrich_preview_thumbs_dir)
    """EnumProperty callback"""
    enrich_props = bpy.context.scene.enrich_props

    if context is None:
        return enum_items

    wm = bpy.context.scene
    directory = wm.enrich_preview_thumbs_dir

    pcoll = preview_collections["main"]

    if directory == pcoll.enrich_preview_thumbs_dir:
        return pcoll.enrich_preview_thumbs
    print("Scanning directory: %s" % directory)

    if directory and os.path.exists(directory):
        # Scan the directory for .png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png" or ".PNG"):
                image_paths.append(fn)

        m = 0
        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            desc = name[:name.rfind(".")].title()
            desc = desc.replace("_", " ")
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((enrich_props.pic_in, name, "Choose the "+desc+" Preset from the library", thumb.icon_id, i)) # Main Item for the Enum
            items.append(name)
            bpy.context.scene.enrich_ui_list.add()
            bpy.context.scene.enrich_ui_list[m].name = desc
            bpy.context.scene.enrich_ui_list[m].description = desc+" Preset is installed"
            enrich_props.pic_in = str(int(enrich_props.pic_in)+1)
            m=m+1

    pcoll.enrich_preview_thumbs = enum_items
    pcoll.enrich_preview_thumbs_dir = directory
    return None

#Update Function when any preset is selected
def preview_enum_update(wm, context):
    enrich_props = bpy.context.scene.enrich_props
    choice = items[int(bpy.context.scene.enrich_preview_thumbs)-1]
    dot = choice.index('.')
    file = choice[:dot]
    exec("from . import " + file)  #Import the File which is selected
    exec(file+"."+file+"()")    #Execute it
    enrich_props.sketchy_thickness = 1.0
    enrich_props.sketchy_color = 1.0
    enrich_props.sketchy_fill = 0.0
    for node in bpy.context.scene.node_tree.nodes:
        if node.name.endswith("Enrich") and node.name != "Sketchy Enrich":
            for filter_node in node.node_tree.nodes:
                if filter_node.name.startswith("Filter") and filter_node.filter_type == 'SHARPEN':
                    enrich_props.sharpen=filter_node.inputs[0].default_value*100
    return None

class EnrichPanel(bpy.types.Panel):
    """The Enrich Panel"""
    bl_idname = "VIEW3D_PT_enrich"
    bl_label = "Enrich Panel"
    bl_context = "scene"

    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = 'Enrich'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        enrich_props = bpy.context.scene.enrich_props
        wm = bpy.context.scene
        col1 = layout.column()
        if enrich_props.gen_bool == False:
            row = col1.row(align=True)
            row.scale_y = 1.5
            row.operator(Enrich_Generate.bl_idname, text="Generate", icon="NEW")  #Generate button
        if enrich_props.gen_bool == True:
            path = get_path(self, context)
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    open_windows.append(area.type)

            empty_files=0
            no_viewer_image = False
            for dirpath, dirnames, files in os.walk(path):
                if not files:
                    empty_files=empty_files+1

            for area in bpy.context.screen.areas: # If Viewer Node image in not active
                if area.type == 'IMAGE_EDITOR':
                    try:
                        if area.spaces.active.image != bpy.data.images['Viewer Node']:
                            no_viewer_image = True
                    except:
                        no_viewer_image = True

            if 'NODE_EDITOR' not in open_windows or empty_files>=1 or enrich_props.update_check_int == 1 or no_viewer_image == True:
                row = col1.row(align=True)
                row.label(text="")
                row.operator(Notification_call.bl_idname, text="", icon="INFO") #Shows the Notification icon, if Node Editor is not open or Presets not insalled
            open_windows.clear()
            if len(wm.enrich_preview_thumbs) != 0:
                box = layout.box()
                colb = box.column()
                colb.template_icon_view(wm, "enrich_preview_thumbs") #Presets Menu
                rowb = colb.row(align=True)
                rowb.scale_x = 5
                rowb.scale_y = 1.2
                rowb.operator(PreviousPreset.bl_idname, text = "", icon = "TRIA_LEFT") #Previous and Next buttons
                #rowb.operator(Refresh.bl_idname, text="", icon = "FILE_REFRESH") #Show the Refresh button always
                rowb.operator(NextPreset.bl_idname, text = "", icon = "TRIA_RIGHT")
                colb.prop(enrich_props, "pre_opacity", text="Opacity", slider=True) #Opacity Slider
            else:
                row5 = col1.row()
                row5.scale_y = 1.2
                row5.operator(Refresh.bl_idname, text="Refresh Presets", icon = "FILE_REFRESH") #Refresh Presets button

            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Sketchy Enrich": #Load Sketchy Preset Settings
                    box2 = layout.box()
                    colb2 = box2.column()
                    colb2.label("Preset Settings", icon="PREFERENCES")
                    colb2_2 = box2.column(align=True)
                    colb2_2.prop(enrich_props, "sketchy_thickness", text="Thickness", slider=True)
                    colb2_2.prop(enrich_props, "sketchy_color", text="Color", slider=True)
                    colb2_2.prop(enrich_props, "sketchy_fill", text="Fill", slider=True)

            for node in bpy.context.scene.node_tree.nodes:
                if node.name.endswith("Enrich") and node.name != "Sketchy Enrich":
                    for filter_node in node.node_tree.nodes:
                        if filter_node.name.startswith("Filter") and filter_node.filter_type == 'SHARPEN': #Load Preset Settings for presets with Sharpen Node
                            box2 = layout.box()
                            colb2 = box2.column()
                            colb2.label("Preset Settings", icon="PREFERENCES")
                            colb2_2 = box2.column(align=True)
                            colb2_2.prop(enrich_props, "sharpen", text="Sharpen", slider=True)

            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Bright/Contrast_E" or node.name == "Vibrance_E" or node.name == "Color Balance_E" or node.name == "Sharp and Soften_E":
                    box4 = layout.box()
                    colb4 = box4.column(align=True)
                    if enrich_props.color_set_bool == False:
                        colb4.prop(enrich_props, "color_set_bool", text="View Color Correction Settings", icon="COLOR", toggle=True)
                    else:
                        colb4.prop(enrich_props, "color_set_bool", text="Hide Color Correction Settings", icon="COLOR", toggle=True)
                        colb4.label()
                        for node in bpy.context.scene.node_tree.nodes:
                            if node.name=="Bright/Contrast_E": #Brightness/Contrast Settings
                                rgb_curves = node.node_tree.nodes['RGB']
                                if enrich_props.bc_bright != 0 or enrich_props.bc_contrast != 0:
                                    colb4.label("Brightness/Contrast Settings", icon='OUTLINER_OB_LAMP')
                                else:
                                    colb4.label("Brightness/Contrast Settings", icon='OUTLINER_DATA_LAMP')
                                colb4.prop(enrich_props, "bc_bright", text="Brightness")
                                colb4.prop(enrich_props, "bc_contrast", text="Contrast")
                                if enrich_props.ui_mode == "1":
                                    box4_1 = box4.box()
                                    colb4_1 = box4_1.column(align=True)
                                    rgb_curves.draw_buttons_ext(context, colb4_1)

                        colb5 = box4.column(align=True)
                        for node in bpy.context.scene.node_tree.nodes:
                            if node.name == "Vibrance_E": #Vibrance/Saturation Settings
                                colb5.label("Vibrance/Saturation Settings")
                                colb5.prop(enrich_props, "vib_strength", text="Vibrance", slider=True)
                                colb5.prop(enrich_props, "satur_strength", text="Saturation", slider=True)
                                colb5.label()

                        for node in bpy.context.scene.node_tree.nodes: #Color Balance Settings
                            if node.name == "Color Balance_E" and enrich_props.ui_mode == "1":
                                colb5.label("Color Balance Settings")
                                rowb5_3 = colb5.row(align=True)
                                rowb5_3.label("Shadows:")
                                rowb5_3.prop(enrich_props, "col_lift", text="")
                                rowb5_4 = colb5.row(align=True)
                                rowb5_4.label("Midtones:")
                                rowb5_4.prop(enrich_props, "col_gamma", text="")
                                rowb5_5 = colb5.row(align=True)
                                rowb5_5.label("Hightlights:")
                                rowb5_5.prop(enrich_props, "col_gain", text="")
                                colb5.label()

                        for node in bpy.context.scene.node_tree.nodes:
                            if node.name == "Sharp and Soften_E": #Sharpen and Soften Settings
                                colb5.label("Sharpen/Soften Settings")
                                colb5.prop(enrich_props, "sharpen_full", text="Sharpen", slider=True)
                                colb5.prop(enrich_props, "soften_full", text="Soften", slider=True)
                    break

            box6 = layout.box() #Exposure/Gamma Settings
            colb6=box6.column(align=True)
            if enrich_props.expo_set_bool==False:
                colb6.prop(enrich_props, "expo_set_bool", text="View Exposure/Gamma Settings", icon='LAMP_SUN', toggle=True)
            else:
                colb6.prop(enrich_props, "expo_set_bool", text="Hide Exposure/Gamma Settings", icon='LAMP_SUN', toggle=True)
                colb6.label()
                colb6.prop(bpy.context.scene.view_settings, "exposure", text="Exposure", slider=True)
                colb6.prop(bpy.context.scene.view_settings, "gamma", text="Gamma", slider=True)

            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Temperature_E": #Temperature Controls
                    box8 = layout.box()
                    colb8 = box8.column(align=True)
                    if enrich_props.temperature_bool == False:
                        colb8.prop(enrich_props, "temperature_bool", text="View Temperature Settings", icon="IPO_CIRC", toggle=True)
                    else:
                        colb8.prop(enrich_props, "temperature_bool", text="Hide Temperature Settings", icon="IPO_CIRC", toggle=True)
                        colb8.label()
                        colb8.prop(enrich_props, "cool_strength", text="Coolness", slider=True)
                        colb8.prop(enrich_props, "warm_strength", text="Warmth", slider=True)
                        colb8_2 = box8.column()
                        colb8_2.prop(enrich_props, "temper_strength", text="Strength", slider=True)

            if enrich_props.ui_mode == "1":
                for node in bpy.context.scene.node_tree.nodes:
                    if node.name == "Colors_E":
                        box10 = layout.box()
                        colb10 = box10.column(align=True)
                        if enrich_props.tint_bool == False:
                            colb10.prop(enrich_props, "tint_bool", text="View Tint Settings", icon="IPO_EASE_IN")
                        else:
                            colb10.prop(enrich_props, "tint_bool", text="Hide Tint Settings", icon="IPO_EASE_IN")
                            colb10.label()
                            row = colb10.row(align=True)
                            row.label("Foreground:")
                            row.prop(enrich_props, "fore_color", text="")
                            row1 = colb10.row(align=True)
                            row1.label("Background:")
                            row1.prop(enrich_props, "back_color", text="")
                            colb10.label()
                            row2 = colb10.row(align=True)
                            row2.label("Overlay:")
                            row2.prop(enrich_props, "darkbg_color", text="")
                            colb10.label()
                            colb10.prop(enrich_props, "color_strength", slider=True, text="Strength")

            if enrich_props.ui_mode == "1":
                for node in bpy.context.scene.node_tree.nodes:
                    if node.name == "Colors_E":
                        box11 = layout.box()
                        colb11 = box11.column(align=False)
                        if enrich_props.mist_bool == False:
                            colb11.prop(enrich_props, "mist_bool", text="View Mist Settings", icon="MOD_SMOKE")
                        else:
                            colb11.prop(enrich_props, "mist_bool", text="Hide Mist Settings", icon="MOD_SMOKE")
                            colb11.label()
                            box11_1 = box11.box()
                            colb11_1 = box11_1.column(align=True)
                            row11_1 = colb11_1.row(align=True)
                            row11_1.label("Mist Map", icon="IMAGE_ZDEPTH")
                            if enrich_props.mist_map == True:
                                row11_1.prop(enrich_props, 'mist_map', text="", icon='RESTRICT_VIEW_OFF', emboss=False)
                            else:
                                row11_1.prop(enrich_props, 'mist_map', text="", icon='RESTRICT_VIEW_ON', emboss=False)
                            znode = node.node_tree.nodes['cr']
                            colb11_1.label()
                            znode.draw_buttons_ext(context, colb11_1)
                            colb11_2 = box11.column()
                            row11 = colb11_2.row(align=True)
                            row11.label("Color:")
                            row11.prop(enrich_props, "mist_color", text="")
                            colb11_2.prop(enrich_props, "mist_stre", text="Strength", slider=True)

            if enrich_props.ui_mode == "1":
                for node in bpy.context.scene.node_tree.nodes:
                    if node.name == "Colors_E":
                        box12 = layout.box()
                        colb12 = box12.column(align=False)
                        if enrich_props.defocus_bool == False:
                            colb12.prop(enrich_props, "defocus_bool", text="View Defocus Settings", icon="ROTATE")
                        else:
                            colb12.prop(enrich_props, "defocus_bool", text="Hide Defocus Settings", icon="ROTATE")
                            colb12.label()
                            box11_1 = box12.box()
                            colb11_1 = box11_1.column(align=True)
                            row11_1 = colb11_1.row(align=True)
                            row11_1.label("Blur Ramp", icon="IMAGE_ZDEPTH")
                            if enrich_props.defocus_map == True:
                                row11_1.prop(enrich_props, 'defocus_map', text="", icon='RESTRICT_VIEW_OFF', emboss=False)
                            else:
                                row11_1.prop(enrich_props, 'defocus_map', text="", icon='RESTRICT_VIEW_ON', emboss=False)
                            colb11_1.label()
                            znode2 = node.node_tree.nodes["blurramp"]
                            defo = node.node_tree.nodes["Defocus"]
                            znode2.draw_buttons_ext(context, colb11_1)
                            box11_2 = box12.box()
                            colb11_2 = box11_2.column(align=True)
                            defo.draw_buttons_ext(context, colb11_2)

            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Lens Effects_E":
                    box9 = layout.box()
                    colb9 = box9.column(align=True)
                    if enrich_props.lens_effects_bool == False:
                        colb9.prop(enrich_props, "lens_effects_bool", text="View Lens Effects", icon="OUTLINER_DATA_CAMERA", toggle=True)
                    else:
                        colb9.prop(enrich_props, "lens_effects_bool", text="Hide Lens Effects", icon="OUTLINER_DATA_CAMERA", toggle=True)
                        colb9.label()
                        colb9.prop(enrich_props, "chromatic_ab", text="Chromatic Aberration", slider=True)
                        colb9.prop(enrich_props, "lens_dis", text="Lens Distort", slider=True)

            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Vignette_E": #Vignette Settings
                    box3 = layout.box()
                    colb3 = box3.column(align=True)
                    if enrich_props.vig_bool == False:
                        colb3.prop(enrich_props, "vig_bool", text="View Vignette Settings", icon="CLIPUV_DEHLT", toggle=True)
                    else:
                        colb3.prop(enrich_props, "vig_bool", text="Hide Vignette Settings", icon="CLIPUV_DEHLT", toggle=True)
                        colb3.label()
                        colb3.prop(enrich_props, "vig_blur", text="Blur", slider=True)
                        colb3.prop(enrich_props, "vig_opacity", text="Opacity", slider=True)
                        colb3.label()
                        if enrich_props.ui_mode == "1":
                            if enrich_props.vig_adv_bool == False: #Advanced vignette Settings
                                colb3.prop(enrich_props, "vig_adv_bool", text="View Advanced Settings", icon='RADIOBUT_OFF', toggle=True)
                            else:
                                colb3.prop(enrich_props, "vig_adv_bool", text="Hide Advanced Settings", icon='RADIOBUT_ON', toggle=True)
                                colb3.label()
                                colb3.label("Size:", icon='MAN_SCALE')
                                colb3.prop(enrich_props, "vig_width", text="Width", slider=True)
                                colb3.prop(enrich_props, "vig_height", text="Height", slider=True)
                                colb3.label("Location:", icon='MANIPUL')
                                colb3.prop(enrich_props, "vig_location_x", text="X Axis")
                                colb3.prop(enrich_props, "vig_location_y", text="Y Axis")

            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Crop_E":
                    box1 = layout.box()
                    colb1 = box1.column()
                    if enrich_props.cinema_border == False: #Cinematic Border Settings
                        colb1.prop(enrich_props, "cinema_border", text="Enable Cinematic Border", icon="GRID", toggle=True)
                    else:
                        colb1.prop(enrich_props, "cinema_border", text="Disable Cinematic Border", icon="GRID", toggle=True)
                        colb1.label()
                        colb1.prop(enrich_props, "cinema_border_height", text="Border Height", slider=True)

            for node in bpy.context.scene.node_tree.nodes:
                if node.name =="Split Viewer":
                    box5 = layout.box()
                    colb5 = box5.column()
                    if enrich_props.split_bool == False: #Split view Settings
                        colb5.prop(enrich_props, "split_bool", text="Enable Split View", icon="UV_ISLANDSEL", toggle=True)
                    else:
                        colb5.prop(enrich_props, "split_bool", text="Disable Split View", icon="UV_ISLANDSEL", toggle=True)
                        colb5.label()
                        colb5.prop(enrich_props, "split_factor", text="Factor", slider=True)

            box4 = layout.box()
            colb4 = box4.column()
            if enrich_props.save_image_bool == False: #Save Image Settings
                colb4.prop(enrich_props, "save_image_bool", text="View Save Image Settings", icon="EXTERNAL_DATA", toggle=True)
            else:
                colb4.prop(enrich_props, "save_image_bool", text="Hide Save Image Settings", icon="EXTERNAL_DATA", toggle=True)
                colb4.label()
                colb4.prop(bpy.context.scene.render.image_settings, "file_format", text="Format")
                colb4.operator(SaveImage.bl_idname, text="Save Image", icon="IMAGE_COL")
            col2 = layout.column()
            col2.operator(Clear.bl_idname, text="Remove Enrich", icon = "QUIT") #Remove Enrich Button

class InstallCustomEnrichPresets(bpy.types.Panel):
    """The Custom Presets Panel"""
    bl_idname = "VIEW3D_PT_panel"
    bl_label = "Custom Enrich Presets"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        enrich_props = bpy.context.scene.enrich_props
        if bpy.context.space_data.tree_type == 'CompositorNodeTree':
            col.prop_search(enrich_props,"install_node_group_name", bpy.data,"node_groups",text="NodeGroup")
            if enrich_props.install_node_group_name == "":
                col.label()
                box = layout.box()
                col = box.column(align=True)
                col.label("Select the Preset NodeGroup", icon='INFO')
                col.label("       from the menu above")
            if enrich_props.install_node_group_bool == 1:
                col.label("This Preset can be installed", icon="FILE_TICK")
                col.label()
                row = col.row(align=True)
                row.scale_y = 1.5
                row.operator(InstallCustom.bl_idname, text="Install Preset", icon="NODE_SEL")
            elif enrich_props.install_node_group_bool == 2:
                col.label("This Preset cannot be installed", icon="ERROR")
            if enrich_props.install_node_bool == 1:
                col.label("Preset Installed!")
            elif enrich_props.install_node_bool == 2:
                col.label("There was some Problem,")
                col.label("try later")
        else:
            col.label("Switch to Compositor NodeTree")
            col.label()
            row = col.row(align=True)
            row.scale_y = 1.5
            row.operator(SwitchCompositorNodeTree.bl_idname, text="To Compositor", icon="NODETREE")


class EnrichProps(bpy.types.PropertyGroup):
    def cinema_bool(self, context): #Cinema Border Disable Settings
        enrich_props=bpy.context.scene.enrich_props
        if(enrich_props.cinema_border==True):
            bpy.context.scene.node_tree.nodes['Crop_E'].rel_min_y = enrich_props.cinema_border_height/2
            bpy.context.scene.node_tree.nodes['Crop_E'].rel_max_y = 1-enrich_props.cinema_border_height/2
        else:
            bpy.context.scene.node_tree.nodes['Crop_E'].rel_min_y = 0.0
            bpy.context.scene.node_tree.nodes['Crop_E'].rel_max_y = 1.0
        reset_viewer(self, context)
        return None
    def cinema_border_float(self, context): #Cinema Border value Control
        enrich_props=bpy.context.scene.enrich_props
        bpy.context.scene.node_tree.nodes['Crop_E'].rel_min_y = enrich_props.cinema_border_height/2
        bpy.context.scene.node_tree.nodes['Crop_E'].rel_max_y = 1-enrich_props.cinema_border_height/2
        reset_viewer(self, context)
        return None
    def sketch_thick(self, context): #Sketchy Thickness Value
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Sketchy Enrich":
                node.inputs[1].default_value = enrich_props.sketchy_thickness
        reset_viewer(self, context)
        return None
    def sketch_color(self, context): #Sketchy Color Value
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Sketchy Enrich":
                node.inputs[2].default_value = enrich_props.sketchy_color
        reset_viewer(self, context)
        return None
    def sketch_fill(self, context): #Sketchy Fill Value
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Sketchy Enrich":
                node.inputs[3].default_value = enrich_props.sketchy_fill
        reset_viewer(self, context)
        return None
    def vignette_update(self, context): #Vignette opacity
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Vignette_E":
                if enrich_props.vig_opacity/100 == 0.0:
                    node.mute = True
                else:
                    node.mute = False
                node.inputs[2].default_value = enrich_props.vig_opacity/100
                node.node_tree.nodes['Blur'].factor_x = enrich_props.vig_blur
                node.node_tree.nodes['Blur'].factor_y = enrich_props.vig_blur
                node.node_tree.nodes['Ellipse Mask'].x = enrich_props.vig_location_x
                node.node_tree.nodes['Ellipse Mask'].y = enrich_props.vig_location_y
                node.node_tree.nodes['Ellipse Mask'].height = enrich_props.vig_height
                node.node_tree.nodes['Ellipse Mask'].width = enrich_props.vig_width
        reset_viewer(self, context)
        return None
    def set_bc(self, context): #Brightness
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Bright/Contrast_E":
                node.inputs["Bright"].default_value = enrich_props.bc_bright
                node.inputs["Contrast"].default_value = enrich_props.bc_contrast
        reset_viewer(self, context)
        return None
    def preset_opacity(self, context): #Preset Opacity
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Mix 1_E":
                node.inputs[0].default_value = 1-(enrich_props.pre_opacity/100)
                if enrich_props.pre_opacity == 0:
                    for node in bpy.context.scene.node_tree.nodes:
                        if node.name.endswith("Enrich"):
                            node.mute = True
                            break
                else:
                    for node in bpy.context.scene.node_tree.nodes:
                        if node.name.endswith("Enrich"):
                            node.mute = False
                            break
        reset_viewer(self, context)
        return None
    def split_view_factor(self, context): #Split view Factor value
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Split Viewer":
                node.factor = enrich_props.split_factor
        reset_viewer(self, context)
        return None
    def split_view_bool(self, context): #Split view Enable/Disable Option
        enrich_props=bpy.context.scene.enrich_props
        if enrich_props.split_bool==False:
            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Split Viewer":
                    node.factor = 100
        else:
            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Split Viewer":
                    enrich_props.split_factor = 50
        reset_viewer(self, context)
        return None
    def vibrance_strength(self, context): #Vibrance Value
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Vibrance_E":
                if enrich_props.vib_strength != 1.0 or enrich_props.satur_strength != 1.0:
                    node.mute = False
                else:
                    node.mute = True
                node.node_tree.nodes["Color Correction"].midtones_saturation = enrich_props.vib_strength
        reset_viewer(self, context)
        return None
    def saturation_strength(self, context): #Saturation Value
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Vibrance_E":
                if enrich_props.satur_strength != 1.0 or enrich_props.vib_strength != 1.0:
                    node.mute = False
                else:
                    node.mute = True
                for grp_node in node.node_tree.nodes:
                    if grp_node.name == "Hue Saturation Value":
                        grp_node.color_saturation=enrich_props.satur_strength
        reset_viewer(self, context)
        return None
    def sharp_strength(self, context): #Sharp Value
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name.endswith("Enrich") and node.name != "Sketchy Enrich":
                for filter_node in node.node_tree.nodes:
                    if filter_node.name.startswith("Filter") and filter_node.filter_type == 'SHARPEN':
                        filter_node.inputs[0].default_value = enrich_props.sharpen/100
        reset_viewer(self, context)
        return None
    def sharp_soft_full_strength(self, context): #Combined for Sharpen and Soften Values
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Sharp and Soften_E":
                if enrich_props.sharpen_full != 0 or enrich_props.soften_full != 0:
                    node.mute = False
                else:
                    node.mute = True
                node.inputs[2].default_value = enrich_props.sharpen_full/100
                node.inputs[1].default_value = enrich_props.soften_full/100
        reset_viewer(self, context)
        return None
    def temperature_strength(self, context): #Temperature values
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Temperature_E":
                if enrich_props.temper_strength != 0:
                    node.mute = False
                else:
                    node.mute = True
                node.inputs[3].default_value = enrich_props.temper_strength/100
                node.inputs[1].default_value = enrich_props.cool_strength/100
                node.inputs[2].default_value = enrich_props.warm_strength/100
        reset_viewer(self, context)
        return None
    def col_bal_full(self, context): #Contorls the Color Balance Node
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Color Balance_E":
                if enrich_props.col_lift[0] != 1.0 or enrich_props.col_lift[1] != 1.0 or enrich_props.col_lift[2] != 1.0 or enrich_props.col_gamma[0] != 1.0 or enrich_props.col_gamma[1] != 1.0 or enrich_props.col_gamma[2] != 1.0 or enrich_props.col_gain[0] != 1.0 or enrich_props.col_gain[1] != 1.0 or enrich_props.col_gain[2] != 1.0:
                    node.mute = False
                else:
                    node.mute = True
                node.lift = enrich_props.col_lift
                node.gamma = enrich_props.col_gamma
                node.gain = enrich_props.col_gain
        reset_viewer(self, context)
        return None
    def lens_effects(self, context): #Comined Controls for the Lens Effects
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Lens Effects_E":
                if enrich_props.chromatic_ab != 0.0 or enrich_props.lens_dis != 0.0:
                    node.mute = False
                else:
                    node.mute = True
                node.inputs[1].default_value = enrich_props.chromatic_ab
                node.inputs[2].default_value = enrich_props.lens_dis
        reset_viewer(self, context)
        return None
    def set_colors(self, context): # Values for the Tint Colors
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Colors_E":
                if enrich_props.color_strength/100 != 0 or enrich_props.mist_stre/100 != 0:
                    node.mute = False
                else:
                    node.mute = True
                node.inputs["Foreground Color"].default_value = enrich_props.fore_color
                node.inputs["Background Color"].default_value = enrich_props.back_color
                node.inputs["Color Strength"].default_value = enrich_props.color_strength/100
                node.inputs["Dark Background"].default_value = enrich_props.darkbg_color
        reset_viewer(self, context)
        return None
    def set_mist(self, context): # Values for the Mist
        enrich_props=bpy.context.scene.enrich_props
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Colors_E":
                if enrich_props.color_strength/100 != 0 or enrich_props.mist_stre/100 != 0:
                    node.mute = False
                else:
                    node.mute = True
                node.inputs["Mist Color"].default_value = enrich_props.mist_color
                node.inputs["Mist Strength"].default_value = enrich_props.mist_stre/100
        reset_viewer(self, context)
        return None
    def set_node_name(self, context): # Setup the NodeGroup for Custom Preset Installation
        enrich_props=bpy.context.scene.enrich_props
        if enrich_props.install_node_group_name in bpy.data.node_groups:
            enrich_props.install_node_group_bool = 1
        elif enrich_props.install_node_group_name == "":
            enrich_props.install_node_group_bool = 0
        else:
            enrich_props.install_node_group_bool = 2

        if not enrich_props.install_node_group_name == "":
            try:
                preset_node = bpy.data.node_groups[enrich_props.install_node_group_name]
                input_node = preset_node.inputs[0]
                output_node = preset_node.outputs[0]
                if input_node.name == "Image" and output_node.name == "Image":
                    enrich_props.install_node_group_bool = 1
                else:
                    enrich_props.install_node_group_bool = 2
            except:
                enrich_props.install_node_group_bool = 2

        return None
    def switch_links(self, context): # Switch the Links
        enrich_props=bpy.context.scene.enrich_props
        colors_check = False
        split_check = False
        temper_check = False
        mix_check = False
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Colors_E":
                colors_check = True
            elif node.name == "Split Viewer":
                split_check = True
            elif node.name == "Temperature_E":
                temper_check = True
            elif node.name == "Mix 2_E":
                mix_check = True

        if split_check==True and colors_check==True and temper_check==True and mix_check==True:
            split = bpy.context.scene.node_tree.nodes['Split Viewer']
            color = bpy.context.scene.node_tree.nodes['Colors_E']
            temper = bpy.context.scene.node_tree.nodes['Temperature_E']
            mix = bpy.context.scene.node_tree.nodes['Mix 2_E']

            if enrich_props.defocus_map == True:
                bpy.context.scene.node_tree.links.new(split.inputs[1], color.outputs[1])
            else:
                bpy.context.scene.node_tree.links.new(split.inputs[1], mix.outputs[0])
                bpy.context.scene.node_tree.links.new(temper.inputs[0], color.outputs[0])

        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Colors_E":
                if enrich_props.color_strength/100 == 0 and enrich_props.mist_stre/100 == 0 and enrich_props.defocus_map == False and bpy.context.scene.node_tree.nodes['Colors_E'].node_tree.nodes["Defocus"].blur_max == 0:
                    node.mute = True
                else:
                    node.mute = False
                break

        if enrich_props.mist_map == True:
            enrich_props.mist_map = True
        return None
    def save_ui(self, context): # Saving the Interface type Externally
        enrich_props=bpy.context.scene.enrich_props
        file_py = open(os.path.join(os.path.dirname(__file__))+"ui_mode.txt", 'w')

        path = os.path.join(os.path.dirname(__file__), "ui_mode.txt")
        f = open(path, 'w+')
        if enrich_props.ui_mode == "0":
            f.write("0"+"\n")
        elif enrich_props.ui_mode == "1":
            f.write("1"+"\n")
        f.close()
        return None
    def set_mist_map(self, context): # Switch Links to view the Mist map
        enrich_props=bpy.context.scene.enrich_props
        colors_check = False
        split_check = False
        temper_check = False
        mix_check = False
        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Colors_E":
                colors_check = True
            elif node.name == "Split Viewer":
                split_check = True
            elif node.name == "Temperature_E":
                temper_check = True
            elif node.name == "Mix 2_E":
                mix_check = True

        if split_check==True and colors_check==True and temper_check==True and mix_check==True:
            split = bpy.context.scene.node_tree.nodes['Split Viewer']
            color = bpy.context.scene.node_tree.nodes['Colors_E']
            temper = bpy.context.scene.node_tree.nodes['Temperature_E']
            mix = bpy.context.scene.node_tree.nodes['Mix 2_E']

            if enrich_props.mist_map == True:
                bpy.context.scene.node_tree.links.new(split.inputs[1], color.outputs[2])
            else:
                bpy.context.scene.node_tree.links.new(split.inputs[1], mix.outputs[0])
                bpy.context.scene.node_tree.links.new(temper.inputs[0], color.outputs[0])

        for node in bpy.context.scene.node_tree.nodes:
            if node.name == "Colors_E":
                if enrich_props.mist_map == True:
                    node.mute = False
                elif enrich_props.mist_map == False or enrich_props.defocus_map == False or enrich_props.mist_stre == 0 or enrich_props.color_strength == 0:
                    node.mute = True

        if enrich_props.defocus_map == True:
            enrich_props.defocus_map = True
        return None
    #Boolean Property
    cinema_border = BoolProperty(name="Enable Cinematic Border", description="Enable/Disable Cinematic Border", default=False, update=cinema_bool)
    gen_bool = BoolProperty(name="Generated Enrich", default=False)
    save_image_bool = BoolProperty(name="View Save Image settings", description="View/Hide Save Image Settings", default=False)
    vig_bool = BoolProperty(name="Vignette Settings", description="View/Hide Vignette Settings", default=False)
    vig_adv_bool = BoolProperty(name="Vignette Advanced Settings", description="View/Hide Advanced Vignette Settings", default=False)
    color_set_bool = BoolProperty(name="Color Settings", description="View/Hide Color Correction Settings", default=False)
    install_preset_bool = BoolProperty(name="Installing Presets", default=False)
    change_bool = BoolProperty(name="View Latest Changelog", description="View/Hide the Changes of the new version of Enrich add-on", default=False)
    expo_set_bool = BoolProperty(name="Exposure/Gamma", description="View/Hide Exposure and Gamma Settings", default=False)
    split_bool = BoolProperty(name="Split View", description="Enable/Disable Split View", default=False, update=split_view_bool)
    temperature_bool = BoolProperty(name="Temperature Settings", description="View/Hide Temperature Settings", default=False)
    lens_effects_bool = BoolProperty(name="Lens Effects", description="View/Hide Lens Effects Settings", default=False)
    bright_bool = BoolProperty(name="Brightness/Contrast", description="View/Hide Brightness and Contrast", default=False)
    defocus_bool = BoolProperty(name="Defocus", description="View/Hide Defocus Settings", default=False)
    mist_bool = BoolProperty(name="Mist", description="View/Hide Mist Settings", default=False)
    tint_bool = BoolProperty(name="Tint", description="View/Hide Tint Settings", default=False)
    mist_map = BoolProperty(name="View Mist Map", description="View/Hide Mist Map", default=False, update=set_mist_map)
    defocus_map = BoolProperty(name="View Defocus Blur Map", description="View/Hide Defocus Blur Map", default=False, update=switch_links)

    #String Property
    install_blend_name = StringProperty(name="Install Blend Name", description="Enter the name of the .blend file which contains the NodeGroup",default="")
    install_node_name = StringProperty(name="Install Node", description="Enter the name of the NodeGroup", default="")
    install_cod_name = StringProperty(name="Install Code", description="Enter the name of the icon file for the Preset. Only .png format is supported", default="")
    install_node_group_name = StringProperty(name="Install Node Group name", description="Enter the Name of the NodeGroup", default="", update=set_node_name)
    pic_in = StringProperty(name="count", description="",default = "1")
    update_check_version = StringProperty(name="New Version", default="")
    update_link = StringProperty(name="Download Update Link", default="http://www.blenderschool.cf/")

    #Float Property
    cinema_border_height = FloatProperty(name="Height of Border", description="Set the Height of the Cinematic Border", default = 0.2, min = 0.0, max = 1.0, update=cinema_border_float)
    sketchy_thickness = FloatProperty(name="Thickness of Sketch", description="Set the Thickness of the Lines", default = 1.0, min = 0.0, max = 10.0, update=sketch_thick)
    sketchy_color = FloatProperty(name="Color Overlay of Sketch", description="Set the Color Overlay of the Sketch", default = 1.0, min = 0.0, max = 1.0, update=sketch_color)
    sketchy_fill = FloatProperty(name="Color Fill of Sketch", description="Set the Fill amount of the Sketch", default = 0.0, min = 0.0, max=1.0, update=sketch_fill)
    #Vignette Node
    vig_opacity = FloatProperty(name="Opacity of Vignette", description="Set the Opacity of the Vignette", subtype='PERCENTAGE', default = 0.0, min=0.0, max=100.0, update=vignette_update)
    vig_blur = FloatProperty(name="Blur Vignette", description="Set the Blur amount of Vignette", default=20.0, min=0.0, max=100.0, update=vignette_update)
    vig_location_x = FloatProperty(name="Vignette X", description="Control the location of Vignette in x-axis", default=0.5, min=-1.0, max=2.0, update=vignette_update)
    vig_location_y = FloatProperty(name="Vignette Y", description="Control the location of Vignette in y-axis", default=0.5, min=-1.0, max=2.0, update=vignette_update)
    vig_height = FloatProperty(name="Vignette Height", description="Control the Height of the Vignette Mask", default=0.573, min=0.0, max=2.0, update=vignette_update)
    vig_width = FloatProperty(name="Vignette Width", description="Control the Width of the Vignette Mask", default=0.909, min=0.0, max=2.0, update=vignette_update)
    #Brightness/Contrast
    bc_bright = FloatProperty(name="Brightness", description="Control the Brightness of the Render", default=0.0, min=-100.0, max=100.0, update=set_bc)
    bc_contrast = FloatProperty(name="Contrast", description="Control the Contrast of the Render", default=0.0, min=-100.0, max=100.0, update=set_bc)
    #Opacity
    pre_opacity = FloatProperty(name="Opacity", description="Control the Opacity of the Preset",subtype='PERCENTAGE', default=100, min=0, max=100, update=preset_opacity)
    #Vibrance and Saturation
    vib_strength = FloatProperty(name="Vibrance", description="Control the Vibrance of the Render", default=1.0, min=0.0, max=4.0, update=vibrance_strength)
    satur_strength = FloatProperty(name="Saturation", description="Control the Saturation of the Render", default=1.0, min=0.0, max=2.0, update=saturation_strength)
    #Sharpen and Soften
    sharpen = FloatProperty(name="Sharpen", description="Set the Sharpen strength", subtype='PERCENTAGE', default=0.0, min=0.0, max=100, update=sharp_strength)
    sharpen_full = FloatProperty(name="Sharpen Full", description="Set the Sharpen of the Full Render",subtype='PERCENTAGE', default=0.0, min=0.0, max=100, update=sharp_soft_full_strength)
    soften_full = FloatProperty(name="Soften Full", description="Set the Soften of the Full Render", subtype='PERCENTAGE', default=0.0, min=0.0, max=100, update=sharp_soft_full_strength)
    #Temperature (Warmth and Coolness)
    cool_strength = FloatProperty(name="Coolness", description="Control the Coolness of the Render", subtype='PERCENTAGE', default=50, min=0.0, max=100, update=temperature_strength)
    warm_strength = FloatProperty(name="Warmth", description="Control the Warmth of the Render", subtype='PERCENTAGE', default=50, min=0.0, max=100, update=temperature_strength)
    temper_strength = FloatProperty(name="Temperature Strength", description="Control the Strength of Temperature Adjustments", subtype='PERCENTAGE', default=0, min=0.0, max=100, update=temperature_strength)
    #Lens Distort and Chromatic Aberration
    lens_dis = FloatProperty(name="Lens Distort", description="Control the Lens Distortion", default=0.0, max=1.0, min=-0.999, update=lens_effects)
    chromatic_ab = FloatProperty(name="Chromatic Aberration", description="Control the Chromatic Aberration Effect on the Render", default=0.0, max=1.0, min=0.0, update=lens_effects)
    #FloatVectorProperties (For Color Balance Node)
    col_lift = FloatVectorProperty(name = "Shadows",description="Control the Colors of Shadows of your Render", subtype="COLOR_GAMMA", update=col_bal_full, min = 0.0, max = 2.0, default = (1.0,1.0,1.0))
    col_gamma = FloatVectorProperty(name = "Midtones",description="Control the Colors of Midtones of your Render", subtype="COLOR_GAMMA", update=col_bal_full, min = 0.0, max = 2.0, default = (1.0,1.0,1.0))
    col_gain = FloatVectorProperty(name = "Highlights",description="Control the Colors of Highlights of your Render", subtype="COLOR_GAMMA", update=col_bal_full, min = 0.0, max = 2.0, default = (1.0,1.0,1.0))
    #Foreground & Background colors
    fore_color = FloatVectorProperty(name="Foreground Color", description="Control the Foreground color of the Render", subtype="COLOR", size=4, default=(0.233312, 0.410415, 0.794959, 1.000000), min=0.0, max=1.0, update=set_colors)
    back_color = FloatVectorProperty(name="Background Color", description="Control the Background color of the Render", subtype="COLOR", size=4, default=(0.787399, 0.394273, 0.308689, 1.000000), min=0.0, max=1.0, update=set_colors)
    color_strength = FloatProperty(name="Colors Strength", description="Control the Strength of Foreground and Background colors", subtype='PERCENTAGE', default=0.0, max=100, min=0.0, update=set_colors)
    darkbg_color = FloatVectorProperty(name="Dark Background Color", description="Control the Dark Background color of the Render", subtype="COLOR", size=4, default=(1.000000, 1.000000, 1.000000, 1.000000), min=0.0, max=1.0, update=set_colors)
    #Mist
    mist_color = FloatVectorProperty(name="Mist Color", description="Control the Color of the Mist", subtype="COLOR", size=4, default=(1.000000, 1.000000, 1.000000, 1.000000), min=0.0, max=1.0, update=set_mist)
    mist_stre = FloatProperty(name="Mist Strength", description="Control the Strength of the Mist", subtype='PERCENTAGE', default=0.0, min=0.0, max=100.0, update=set_mist)

    #Integer Property
    install_blend_bool = IntProperty(name="Install Bool", default=0)
    install_node_group_bool = IntProperty(name="Install Preset Checker", default=0)
    install_node_bool = IntProperty(name="Install Node Checker", default=0)
    update_check_int = IntProperty(name="Update Checker", default=0)
    change_log_int = IntProperty(name="Changelog Checker", default=0)
    split_factor = IntProperty(name="Factor of Split view", description="Factor of Split View",subtype='PERCENTAGE', default=100, min=0, max=100, update=split_view_factor)

    #EnumProperty
    #Assigning default Value during registration
    check = False
    val = ""
    try:
        f = open(os.path.join(os.path.dirname(__file__), "ui_mode.txt"), "r")
        val = f.readline()
        val = val[0]
        f.close()
        check = True
    except:
        check = False

    if check == True:
        ui_mode = EnumProperty(name="Interface Type", description="Choose the Interface style which suits you", items=(('0', 'Simple', 'Simple UI with essential options for quick compositing'), ('1', 'Advanced', 'Advanced UI with in-depth options to control all the aspects of the render')), default=val, update=save_ui)
    else:
        ui_mode = EnumProperty(name="Interface Type", description="Choose the Interface style which suits you", items=(('0', 'Simple', 'Simple UI with essential options for quick compositing'), ('1', 'Advanced', 'Advanced UI with in-depth options to control all the aspects of the render')), default='0', update=save_ui)

class ListItem(bpy.types.PropertyGroup):
    """ Group of properties representing an item in the list """

    ui_list_name = StringProperty(name="", description="Presets Installed in the add-on", default="Untitled") #Presets List

class InstallCustom(bpy.types.Operator): # Installing Custom Presets
    """Install the above selected NodeGroup in the add-on"""
    bl_idname="enrich.install_custom_preset"
    bl_label="Install Custom"
    def execute(self, context):
        enrich_props=bpy.context.scene.enrich_props
        try:
            name = bpy.context.scene.node_tree.nodes.active.name
            try:
                for obj in bpy.data.objects: # Delete all the Objects
                    obj.select = True
                    bpy.ops.object.delete()
            except: # Needed for the recheck of the deletion of all the objects
                for obj in bpy.data.objects:
                    obj.select = True
                    bpy.ops.object.delete()
            path = os.path.join(os.path.dirname(__file__), "blend", "")
            enrich_props.install_node_name = enrich_props.install_node_group_name
            enrich_props.install_blend_name = enrich_props.install_node_group_name+".blend"
            bpy.ops.wm.save_as_mainfile(filepath=path+enrich_props.install_node_group_name+".blend") # Save .blend file
            bpy.ops.enrich.import_preset_thumb('INVOKE_DEFAULT') # Import the Preset Icon file
        except:
            enrich_props.install_node_bool = 2
        return {'FINISHED'}

class NextPreset(bpy.types.Operator): #Switch to Next Preset
    """Select the Next Preset"""
    bl_idname="enrich.preset_next"
    bl_label="Next"

    def execute(self,context):
        if int(bpy.context.scene.enrich_preview_thumbs) == len(items):
            bpy.context.scene.enrich_preview_thumbs = '1'
        else:
            bpy.context.scene.enrich_preview_thumbs = str(int(bpy.context.scene.enrich_preview_thumbs)+1)
        reset_viewer(self, context)
        return{'FINISHED'}

class SwitchCompositorNodeTree(bpy.types.Operator): # Change it to CompositorNodeTree
    """Switch to the Compositor NodeTree to install Custom Presets"""
    bl_idname = "enrich.custom_install_switch_nodetree"
    bl_label = "Switch to Compositor"

    def execute(self, context):
        bpy.context.space_data.tree_type = "CompositorNodeTree"
        if bpy.context.scene.use_nodes == False:
            bpy.context.scene.use_nodes = True
        return{'FINISHED'}

class PreviousPreset(bpy.types.Operator): #Switch to Previous Preset
    """Select the Previous Preset"""
    bl_idname="enrich.preset_previous"
    bl_label="Previous"

    def execute(self,context):
        if bpy.context.scene.enrich_preview_thumbs == '1':
            bpy.context.scene.enrich_preview_thumbs = str(len(items))
        else:
            bpy.context.scene.enrich_preview_thumbs = str(int(bpy.context.scene.enrich_preview_thumbs)-1)
        reset_viewer(self, context)
        return{'FINISHED'}

class Clear(bpy.types.Operator): #Clear the NodeTree
    """Remove Enrich Nodes by clearing the entire Compositor Node Tree"""
    bl_idname="enrich.remove"
    bl_label="Remove Enrich"

    def execute(self,context):
        for node in bpy.context.scene.node_tree.nodes:
            bpy.context.scene.node_tree.nodes.remove(node)
        bpy.context.scene.enrich_props.gen_bool = False
        bpy.context.scene.enrich_props.cinema_border = False
        layer = bpy.context.scene.node_tree.nodes.new(type="CompositorNodeRLayers")
        out = bpy.context.scene.node_tree.nodes.new(type="CompositorNodeComposite")

        layer.location = out.location[0]-300, out.location[1]
        bpy.context.scene.node_tree.links.new(out.inputs[0], layer.outputs[0])
        return{'FINISHED'}

class Refresh(bpy.types.Operator): #Refresh Presets Menu
    """Refresh the Presets menu"""
    bl_idname="enrich.preset_refresh"
    bl_label="Refresh"

    def execute(self,context):
        wm = bpy.context.scene
        wm.enrich_preview_thumbs_dir = os.path.join(os.path.dirname(__file__), "icon")
        reset_viewer(self, context)
        reload(self, context)
        return{'FINISHED'}

class Exec_Notifications(bpy.types.Operator): #Solve all the Notifications
    """Solve all the above Notifications"""
    bl_idname="enrich.notifications_solve"
    bl_label="Solve Notifications"

    def execute(self, context):
        editorcheck = False
        ef_use_sky = True
        efFullscreen = False
        enrich_props=bpy.context.scene.enrich_props
        for area in bpy.context.screen.areas : # Checking if CompositorNodeTree is open
            if area.type == 'NODE_EDITOR' :
                if area.spaces.active.tree_type != 'CompositorNodeTree':
                    area.spaces.active.tree_type = 'CompositorNodeTree'
                editorcheck = True
        if editorcheck == False:
            try:
                bpy.context.area.type='NODE_EDITOR'
                bpy.ops.screen.area_split(factor=1)
                bpy.context.area.type='VIEW_3D'
                bpy.context.area.type='IMAGE_EDITOR'
            except:
                bpy.context.area.type='IMAGE_EDITOR'
                bpy.ops.screen.back_to_previous()
                self.report({'WARNING'}, "Fullscreen is not supported")
                efFullscreen = True
            for area in bpy.context.screen.areas :
                if area.type == 'NODE_EDITOR' :
                    if area.spaces.active.tree_type != 'CompositorNodeTree':
                        area.spaces.active.tree_type = 'CompositorNodeTree'
                    editorcheck = True

        reset_viewer(self, context) # Resets the UV Image Editor Active Image

        path = get_path(self, context)
        for dirpath, dirnames, files in os.walk(path): # Checking if Presets are installed
            if not files:
                self.report({'INFO'}, "Presets need to be installed Manually")
                bpy.ops.enrich.install_presets('INVOKE_DEFAULT')

        if enrich_props.update_check_int == 1: # If there is a new update
            webbrowser.open(enrich_props.update_link)
        return{'FINISHED'}

def nodes_generate(caller, context): #Generate the NodeTree
    composite_nodes_generate.composite_nodes_generate()
    editorcheck = False
    ef_use_sky = True
    efFullscreen = False
    for area in bpy.context.screen.areas :  #Split the Screen for Node Editor
        if area.type == 'NODE_EDITOR' :
            if area.spaces.active.tree_type != 'CompositorNodeTree':
                area.spaces.active.tree_type = 'CompositorNodeTree'
            editorcheck = True
    if editorcheck == False:
        try:
            bpy.context.area.type='NODE_EDITOR'
            bpy.ops.screen.area_split(factor=1)
            bpy.context.area.type='VIEW_3D'
            bpy.context.area.type='IMAGE_EDITOR'
        except:
            bpy.context.area.type='IMAGE_EDITOR'
            bpy.ops.screen.back_to_previous()
            caller.report({'WARNING'}, "Fullscreen is not supported")
            efFullscreen = True
        for area in bpy.context.screen.areas :
            if area.type == 'NODE_EDITOR' :
                if area.spaces.active.tree_type != 'CompositorNodeTree':
                    area.spaces.active.tree_type = 'CompositorNodeTree'
                editorcheck = True

    wm = bpy.context.scene
    wm.enrich_preview_thumbs_dir = os.path.join(os.path.dirname(__file__), "icon")
    if len(wm.enrich_preview_thumbs) != 0: #Set the first preset
        bpy.context.scene.enrich_preview_thumbs = '1'

class Enrich_Generate(bpy.types.Operator): #Generate the Enrich NodeTree
    """Generate the Enrich Node System with Presets"""
    bl_idname="enrich.generate"
    bl_label="Enrich_Generate"
    def execute(self,context):
        layers = False
        output = False
        other_nodes = False
        if bpy.context.scene.use_nodes == False:
            bpy.context.scene.use_nodes = True
        else:
            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Render Layers":
                    layers = True
                elif node.name == "Composite":
                    output = True
                else:
                    other_nodes = True
            if other_nodes == True:
                bpy.ops.wm.call_menu(name=nodes_remove_warning.bl_idname)
                return{'FINISHED'}
            if layers == False and output == False:
                rlayer = bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")
                out = bpy.context.scene.node_tree.nodes.new("CompositorNodeComposite")
                bpy.context.scene.node_tree.links.new(out.inputs[0], rlayer.outputs[0]) #Changes in the Node Links
        nodes_generate(self, context)
        return{'FINISHED'}

class Notification_call(bpy.types.Operator):
    """View the Notifications"""
    bl_idname="enrich.notification_call"
    bl_label="View Notifications"
    def execute(self, context):
        bpy.ops.wm.call_menu(name=Notification.bl_idname) #Calls the Notification Menu
        return{'FINISHED'}

class Notification(bpy.types.Menu): #Notification Menu
    bl_idname="enrich.notifications"
    bl_label="Notifications"
    def draw(self, context):
        layout = self.layout
        enrich_props=bpy.context.scene.enrich_props
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                open_windows.append(area.type)

        if 'NODE_EDITOR' not in open_windows: # If Node Editor is Not Open
            layout.label("Node Editor is not open! Split the screen to view Compositor Node Editor", icon="SPLITSCREEN")

        path = get_path(self, context)
        for dirpath, dirnames, files in os.walk(path): #Not Installed Presets Notification
            if not files:
                layout.label("Enrich Presets are Not Installed! Please install using UserPreferences", icon="UGLYPACKAGE")

        for area in bpy.context.screen.areas: # If Viewer Node image in not active
            if area.type == 'IMAGE_EDITOR':
                try:
                    if area.spaces.active.image != bpy.data.images['Viewer Node']:
                        layout.label("Viewer Node Image is Not Active to view Live Changes", icon="FILE_IMAGE")
                except:
                    layout.label("There is a Problem with Compositor Node Tree", icon="FILE_IMAGE")

        if enrich_props.update_check_int == 1: # If there's a new Update
            layout.label("New Enrich add-on Version "+enrich_props.update_check_version+" available", icon="WORLD")
        row = layout.row()
        row.scale_y = 2
        row.operator(Exec_Notifications.bl_idname,text="Solve") #Solve Button

class UpdateChecker(bpy.types.Operator):
    """Check for the new update of Enrich addon"""
    bl_idname="enrich.update_check"
    bl_label="Check for Updates"
    def execute(self, context):
        enrich_props = bpy.context.scene.enrich_props
        try:
            link = urllib.request.urlopen('https://gitlab.com/blenderskool/enrich/raw/master/version.txt') #URL to get Update File
            for line in link:
                if line:
                    line = str(line)
                    line = line.replace("b'","")
                    line = line.replace("'", "") #Modifications
                    line = line.replace("\\n","")
                    if float(line) > version: #Check for the version
                        enrich_props.update_check_int = 1
                        enrich_props.update_check_version = line
                    else:
                        enrich_props.update_check_int = 2
        except:
            enrich_props.update_check_int = 3
        try:
            link = urllib.request.urlopen('https://gitlab.com/blenderskool/enrich/raw/master/update_link')
            for line in link:
                if line:
                    line = str(line)
                    line = line.replace("b'","")
                    line = line.replace("'", "") #Modifications
                    line = line.replace("\\n","")
                    enrich_props.update_link = line
        except:
            enrich_props.update_check_int = 3

        return{'FINISHED'}

class OpenInstallFolder(bpy.types.Operator): #Button to invoke the File explorer
    """Open the add-on folder for manual preset installing"""
    bl_idname = "enrich.open_install_folder"
    bl_label = "Open Install folder"

    def execute(self,context):
        import subprocess
        path = get_path(self, context)
        try:
            subprocess.Popen('explorer "{x}"'.format(x=bpy.path.abspath(path)))
        except:
            try:
                subprocess.call(["open", bpy.path.abspath(path)])
            except:
                self.report({'ERROR'}, \
                    "Didn't open folder, navigate to {x} manually".format(x=path))
                return {'CANCELLED'}
        return {'FINISHED'}

class nodes_remove_warning(bpy.types.Menu): #Menu when Nodes are detected
    bl_label = "Nodes Detected in Compositor Node Tree"
    bl_idname = "enrich.generate_node_check"
    def draw(self, context):
        layout = self.layout
        layout.label("Nodes detected in Compositor Node Tree! Do you want to keep the nodes?", icon="QUESTION")
        row = layout.row()
        row.scale_y = 2
        row.operator(no_nodes.bl_idname,text="No")
        row = layout.row()
        row.scale_y = 1.5
        row.operator(yes_nodes.bl_idname,text="Yes")

class yes_nodes(bpy.types.Operator):  #If user selects Yes, above
    """Yes, I want to keep my nodes"""
    bl_label = ""
    bl_idname = "enrich.generate_node_yes"
    def execute(self, context):
        for node in bpy.context.scene.node_tree.nodes:
            if node.bl_idname == "CompositorNodeComposite":
                bpy.context.scene.node_tree.nodes.remove(node)
            elif node.bl_idname == "CompositorNodeViewer":
                bpy.context.scene.node_tree.nodes.remove(node)
        out = bpy.context.scene.node_tree.nodes.new("CompositorNodeComposite")
        nodes_generate(self, context)
        return{'FINISHED'}

class no_nodes(bpy.types.Operator): #If user selects No, above
    """No, I don't want to keep my nodes"""
    bl_label = ""
    bl_idname = "enrich.generate_node_no"
    def execute(self, context):
        for node in bpy.context.scene.node_tree.nodes:
            bpy.context.scene.node_tree.nodes.remove(node)
        layer = bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")
        out = bpy.context.scene.node_tree.nodes.new("CompositorNodeComposite")
        links = bpy.context.scene.node_tree.links.new
        links(out.inputs[0], layer.outputs[0])
        nodes_generate(self, context)
        return{'FINISHED'}

class UL_List(bpy.types.UIList): #Preset List
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        custom_icon = 'RENDER_RESULT'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

class LIST_OT_DeleteItem(bpy.types.Operator): #Deleting a Preset
    """ Delete the selected preset from the list """

    bl_idname = "enrich.list_delete_item"
    bl_label = "Deletes a Preset"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        return len(context.scene.enrich_ui_list) > 0

    def execute(self, context):
        list = context.scene.enrich_ui_list
        index = context.scene.enrich_list_index
        try:
            filname = list[index].name.lower()
            filname = filname.replace(' ', '_')
            path = os.path.join(os.path.dirname(__file__), "icon", filname+".png")
            os.remove(path) #Remove the Icon of the Preset
            path = get_path(self, context)
            path = os.path.join(path, filname+".py")
            os.remove(path) #Remove the Code file of the Preset (Blend File of the Preset shall not be deleted)
            list.remove(index)

            if index > 0:
                index = index - 1
            reload(self,context)
        except:
            pass
        return{'FINISHED'}

def reset_viewer(caller, context): #Display the Viewer Node Image if not open
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            try:
                if area.spaces.active.image != bpy.data.images['Viewer Node']:
                    area.spaces.active.image = bpy.data.images['Viewer Node']
            except:
                bpy.ops.enrich.remove('INVOKE_DEFAULT')
                bpy.ops.enrich.generate('INVOKE_DEFAULT')
    if bpy.context.scene.enrich_props.defocus_map == True:
        bpy.context.scene.enrich_props.defocus_map = False
    if bpy.context.scene.enrich_props.mist_map == True:
        bpy.context.scene.enrich_props.mist_map = False

def reload(caller, context): #Reload the Preset Menu and other values
    import bpy.utils.previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    del bpy.types.Scene.enrich_preview_thumbs_dir
    del bpy.types.Scene.enrich_preview_thumbs
    items.clear()
    enum_items.clear()
    bpy.context.scene.enrich_props.pic_in = '1'
    bpy.context.scene.enrich_ui_list.clear()
    del bpy.types.Scene.enrich_list_index

    pcoll = bpy.utils.previews.new()
    pcoll.enrich_preview_thumbs_dir = ""
    pcoll.enrich_preview_thumbs = ()

    preview_collections["main"] = pcoll

    bpy.types.Scene.enrich_preview_thumbs_dir = StringProperty(
            name="Folder Path",
            subtype='DIR_PATH',
            default="",
            update=preview_dir_update,
            )
    bpy.types.Scene.enrich_preview_thumbs = EnumProperty(
            items=enum_previews_from_directory_items,
            update=preview_enum_update,
            )
    bpy.types.Scene.enrich_ui_list = CollectionProperty(type = ListItem)
    bpy.types.Scene.enrich_list_index = IntProperty(name = "Index for Enrich ui list", description="", default = 0)
    bpy.context.scene.enrich_preview_thumbs_dir = os.path.join(os.path.dirname(__file__), "icon")

class Enrich(bpy.types.AddonPreferences): #Addon Prefrences
    bl_idname = __name__

    #Properies
    view_presets = BoolProperty(name="View Presets",description="View/Hide Installed Presets",default=False)
    custom_install_presets = BoolProperty(name="Custom Install Presets",description="Instructions to Install a Custom Preset in the add-on",default=False)
    export = StringProperty(name="Export Directory", description="Select the directory to Export the Presets installed in a .zip format", subtype='DIR_PATH', default=os.path.join(os.path.expanduser("~"), "Desktop", ""))
    def draw(self, context): #Prefrences Panel
        enrich_props = bpy.context.scene.enrich_props
        scene = context.scene
        layout = self.layout
        col = layout.column()

        path = os.path.join(os.path.dirname(__file__), "icon")
        #sl = path.rfind("\\")
        #path = path[:sl]
        file_count = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]) #Checks the number of icon files preset in the path
        row3 = col.row(align=True)
        split = row3.split(percentage=0.45)
        cols1 = split.column()
        if file_count == 0: #Displays the message accordingly
            cols1.label("Enirch Presets are Not Installed!", icon="UGLYPACKAGE")
        elif file_count == 1:
            cols1.label("1 Preset is Installed", icon="FILE_TICK")
        else:
            cols1.label(str(file_count)+" Presets are Installed", icon="FILE_TICK")

        col4 = layout.column()
        col4.label()
        row4 = col4.row()
        row4.scale_y = 1.2
        row4.label("")
        row4.operator(Enrich_Import.bl_idname, text='Install All the Presets', icon='FILESEL') #Install Presets button
        row4.label("")
        col4.label()
        row5 = col4.row()
        split = row5.split(percentage=0.4)
        col_5_1 = split.column()
        col_5_1.label("Interface Mode:")
        row_5_5_1 = col_5_1.row(align=True)
        row_5_5_1.prop(enrich_props, "ui_mode", expand=True)
        col_5_2 = split.column()
        col_5_2.prop(self, "export", text="Export Directory")
        col_5_2.operator(Enrich_Export.bl_idname, "Export Presets", icon="LINKED")
        col4.label()
        box1 = layout.box()
        colb1 = box1.column(align=True)
        if self.view_presets==False: #Installed Presets List
            colb1.prop(self, "view_presets", text="View Installed Presets", icon='COLOR')
        else:
            colb1.prop(self, "view_presets", text="Hide Installed Presets", icon='COLOR')
            colb1.label()
            path = get_path(self, context)
            no_files=0
            for dirpath, dirnames, files in os.walk(path):
                if not files:
                    no_files=no_files+1
            if no_files >=1:
                colb1.label("No Presets are insatlled. Please Install the Presets")
            else:
                if len(bpy.context.scene.enrich_preview_thumbs) == 0:
                    colb1.operator(Refresh.bl_idname, text="Refresh Presets List", icon = "FILE_REFRESH")
                else:
                    colb1.label("Here is a list of all the installed presets in the add-on")
                    colb1.template_list("UL_List", "The_List", scene, "enrich_ui_list", scene, "enrich_list_index")
                    colb1.operator(LIST_OT_DeleteItem.bl_idname, text="Delete Preset" ,icon='CANCEL')

        box2 = layout.box()
        colb2_3 = box2.column(align=True)
        if self.custom_install_presets == False: #Install Custom Preset Settings
            colb2_3.prop(self, "custom_install_presets", text="View Custom Preset Installtion Instructions", icon='DISCLOSURE_TRI_RIGHT', toggle=True)
        else:
            colb2_3.prop(self, "custom_install_presets", text="Hide Custom Preset Installtion Instructions", icon='DISCLOSURE_TRI_DOWN', toggle=True)
            colb2_3.label()
            colb2_3.label("Instructions to Install Custom Preset: ")
            colb2_3.label()
            colb2_3.label("1. Create a NodeGroup of your preset, and open the Properties by pressing 'N'")
            colb2_3.label("2. In the 'Custom Enrich Presets' panel, select the NodeGroup and click 'Install Preset'")
            colb2_3.label("3. Select the icon for the Preset, only .png File is accepted")
            colb2_3.label("4. The add-on would delete all objects in scene, and save it to separate directory")
            colb2_3.label("5. The preset should be installed")
        col2 = layout.column(align=True)
        row2 = col2.row(align=True)
        row2.scale_y = 1.3
        row2.operator(OpenInstallFolder.bl_idname, text="Open Install Folder", icon='FILE_FOLDER') #Open Install Folder Button
        row2.operator(UpdateChecker.bl_idname, text="Check for Updates", icon='LAMP') #Check for Updates Button
        if enrich_props.update_check_int == 1:
            row2_2 = col2.row()
            row2_2.scale_y = 1.5
            row2_2.label("New update is available. Version: "+enrich_props.update_check_version, icon='OUTLINER_OB_LAMP') #New Version Label
            row2_2.operator('wm.url_open', text='Download the New Update', icon='WORLD').url=enrich_props.update_link #Button to go to Download Page
            col3 = layout.column(align=True)
            if enrich_props.change_log_int == 0: #Indicates that the list is empty
                col3.operator(ReadChanges.bl_idname, text="View the Changes", icon='TEXT')
            elif enrich_props.change_log_int == 1: #Indicates that the list has items
                col3.operator(HideChanges.bl_idname, text="Hide the Changes", icon='TEXT')
                col3.label()
                for i in changelog_list:
                    col3.label(str(i))
            elif enrich_props.change_log_int == 2:
                col3.label("There was some problem! Please try Later") #If some Problem, or no Internet Connection
        elif enrich_props.update_check_int == 2:
            col2.label("Your Version is up to date", icon='OUTLINER_DATA_LAMP')
        elif enrich_props.update_check_int == 3:
            col2.label("There was some problem. Please try later!")


class OBJECT_OT_addon_prefs(bpy.types.Operator):  #Addon Prefrences
    """Display preferences"""
    bl_idname = "enrich.addon_prefs"
    bl_label = "Enrich Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        info = ((addon_prefs.PanelLocation, addon_prefs.view_presets, addon_prefs.export, addon_prefs.custom_install_presets))

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}
class ReadChanges(bpy.types.Operator): #Generates the Change-log
    """Display the Change-log below"""
    bl_idname="enrich.update_read_changes"
    bl_label="Display Changes"

    def execute(self, context):
        enrich_props=bpy.context.scene.enrich_props
        try:
            link = urllib.request.urlopen('https://gitlab.com/blenderskool/enrich/raw/master/changelog.txt') #URL to get Change-log
            for line in link:
                if line:
                    line = str(line)
                    line = line.replace("b'","")
                    line = line.replace("'", "") #Modifications
                    line = line.replace("\\n","")
                    line = "* "+line
                    changelog_list.append(line) #Addes the line as an item in a list
                    enrich_props.change_log_int=1
        except:
            enrich_props.change_log_int=2
        return {'FINISHED'}

class HideChanges(bpy.types.Operator): #To Clear the Change-log list
    """Hide the Change-log"""
    bl_idname="enrich.update_hide_changes"
    bl_label="Hide Changes"

    def execute(self, context):
        enrich_props=bpy.context.scene.enrich_props
        if enrich_props.change_log_int == 1:
            changelog_list.clear() #Clears the list
            enrich_props.change_log_int=0
        return {'FINISHED'}

class SaveImage(bpy.types.Operator, ExportHelper):
    """Save The Final Image"""
    bl_idname = "enrich.save_image"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Save Image"

    filename_ext = ""

    filter_glob = StringProperty(
            default="",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    def execute(self, context):
        return save_image(context, self.filepath)

def save_image(context, filepath): #Save the Image through the Enrich add-on
    filepath = filepath+"."+bpy.context.scene.render.image_settings.file_format
    try:
        bpy.ops.image.save_as(save_as_render=True, copy=True, filepath=filepath, relative_path=True, show_multiview=False, use_multiview=False)
    except:
        pass
    return {'FINISHED'}

class Enrich_Export(bpy.types.Operator): #Export the Presets in a zip file
    """Export the Presets in a .zip format"""
    bl_idname = "enrich.export_presets"
    bl_label = "Export Presets"

    def execute(self, context):
        addon_prefs = context.user_preferences.addons[__name__].preferences
        path = get_path(self, context)
        zf = zipfile.ZipFile(addon_prefs.export+"Enrich_Presets_"+str(datetime.date.today())+".zip", "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(path)
        for dirname, subdirs, files in os.walk(path):
            if '__pycache__' in subdirs:
                subdirs.remove('__pycache__')
            for filename in files: #Do not include the main code files
                if filename != "__init__.py" and filename != "composite_nodes_generate.py" and filename != "custom_install.py" and filename != "preset_setup.py" and filename != "Enrich_requirements.blend" and filename != "ui_mode.txt" and filename != "license.txt":
                    absname = os.path.abspath(os.path.join(dirname, filename))
                    arcname = absname[len(abs_src) + 1:]
                    zf.write(absname, arcname)
        zf.close()
        return {'FINISHED'}

class Enrich_Import(bpy.types.Operator, ImportHelper): #Importing Presets
    """Install Presets .zip file in the add-on"""
    bl_idname = "enrich.install_presets"
    bl_label = "Install Enrich Preset"

    filename_ext = ".zip"

    filter_glob = StringProperty(
            default="*.zip",
            options={'HIDDEN'},
            )

    def execute(self, context):
        try:
            zipref = zipfile.ZipFile(self.filepath, 'r')
            path = get_path(self, context)
            if (path != ""):
                zipref.extractall(path) #Extract to the Enrich add-on Folder
                zipref.close()
            bpy.context.scene.enrich_props.install_preset_bool = False
            reload(self, context)
        except:
            bpy.context.scene.enrich_props.install_preset_bool = True
        return {'FINISHED'}

def get_path(caller, context):  # Common Function as Path handling is different on OS(s)
    return os.path.dirname(__file__)

class ImportThumb(bpy.types.Operator, ImportHelper): # To Import an Icon file by invoking the File Browser
    """Select the Thumbnail (Icon) for the Custom Preset"""
    bl_idname = "enrich.import_preset_thumb"
    bl_label = "Select Custom Icon"

    filename_ext = ".png" # File format

    filter_glob = StringProperty(
            default="*.png",
            options={'HIDDEN'}
    )
    def execute(self, context):
        enrich_props=bpy.context.scene.enrich_props
        try:
            path_main = os.path.join(os.path.dirname(__file__), "icon", "")
            if path_main != "":
                path = self.filepath
                sl = path.rfind(str(os.path.join('a', ""))[1])
                thumb = path[sl+1:]
                new_thumb = ""
                bpy.context.scene.enrich_props.install_cod_name = thumb[:-4]
                if " " in thumb or "-" in thumb or "." in thumb:
                    new_thumb = thumb.replace(" ", "_") # Modifications
                    new_thumb = new_thumb.replace(".", "_")
                    new_thumb = new_thumb.replace("-", "_")
                    new_thumb = new_thumb[:-4]
                else:
                    new_thumb = bpy.context.scene.enrich_props.install_cod_name
                shutil.copy(self.filepath, path_main)
                if " " in thumb or "-" in thumb or "." in thumb:
                    path2 = os.path.join(os.path.dirname(__file__), "icon", thumb)
                    path3 = os.path.join(os.path.dirname(__file__), "icon", new_thumb+'.png')
                    os.rename(path2, path3)
                custom_install.custom_install()
                enrich_props.install_node_bool = 1
        except:
            bpy.context.scene.enrich_props.install_cod_name = ""
            enrich_props.install_node_bool = 2
        reload(self, context)
        return{'FINISHED'}

def register(): #Register
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.enrich_preview_thumbs_dir = ""
    pcoll.enrich_preview_thumbs = ()

    preview_collections["main"] = pcoll

    bpy.types.Scene.enrich_preview_thumbs_dir = StringProperty(
            name="Folder Path",
            subtype='DIR_PATH',
            default="",
            update=preview_dir_update,
            )
    bpy.types.Scene.enrich_preview_thumbs = EnumProperty(
            items=enum_previews_from_directory_items,
            update=preview_enum_update,
            )
    bpy.utils.register_module(__name__)
    bpy.types.Scene.enrich_props = PointerProperty(type = EnrichProps)
    bpy.types.Scene.enrich_ui_list = CollectionProperty(type = ListItem)
    bpy.types.Scene.enrich_list_index = IntProperty(name = "Index for Enrich ui list", description="", default = 0)

def unregister(): #Un-register
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    del bpy.types.Scene.enrich_preview_thumbs_dir
    del bpy.types.Scene.enrich_preview_thumbs
    items.clear()
    enum_items.clear()
    open_windows.clear()
    changelog_list.clear()
    bpy.context.scene.enrich_props.pic_in = '1'
    bpy.context.scene.enrich_props.update_check_int = 0  #Reseting a few values
    bpy.context.scene.enrich_props.change_log_int = 0
    bpy.context.scene.enrich_props.install_blend_name = ""
    bpy.context.scene.enrich_props.install_node_name = ""
    bpy.context.scene.enrich_props.install_cod_name = ""
    bpy.context.scene.enrich_props.install_preset_bool = False
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.enrich_props
    bpy.context.scene.enrich_ui_list.clear()
    del bpy.types.Scene.enrich_list_index

#if __name__ == "__main__":
    #register()
