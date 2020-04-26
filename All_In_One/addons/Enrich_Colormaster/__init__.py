bl_info = {
    "name": "ColorMaster",
    "author": "John Roper",
    "version": (2, 2),
    "blender": (2, 78, 0),
    "location": "Node Editor/Image Editor/Scene Panel (Properties editor) > Tools > ImageMaster > ColorMaster",
    "description": "Quickly add color grading looks to your renders.",
    "wiki_url": "https://cgcookiemarkets.com/all-products/colormaster/",
    "tracker_url": "mailto:johnroper100@gmail.com",
    "category": "Render"
}


import bpy
import re
import ctypes
import os
import shutil

from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bl_operators.presets import AddPresetBase
from bpy.app.handlers import persistent

@persistent
def load_handler(dummy):
    wm = bpy.context.window_manager
    wm.my_previews = bpy.context.scene.view_settings.look

# global vars
image_paths = []

def enum_previews_from_directory_items(self, context):
    """EnumProperty callback"""
    global image_paths

    if context is None:
        return []

    wm = context.window_manager
    directory = wm.my_previews_dir

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    if directory == pcoll.my_previews_dir:
        return pcoll.my_previews

    #print("Scanning directory: %s" % directory)
    enum_items = []

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(""):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((name, name, name, thumb.icon_id, i))

    pcoll.my_previews = enum_items
    pcoll.my_previews_dir = directory

    return pcoll.my_previews

def change_image_cb(self,context):
    bpy.context.scene.view_settings.look = self.my_previews

class Color_Master_preset_add(AddPresetBase, bpy.types.Operator):
    """Add a new color master preset."""
    bl_idname = 'render.color_master_preset_add'
    bl_label = 'Add a preset'
    bl_options = {'REGISTER', 'UNDO'}
    preset_menu = 'Color_Master_presets'
    preset_subdir = 'color_master_preset'

    preset_defines = [
        "color  = bpy.context.scene.view_settings",
        ]

    preset_values = [
        "color.view_transform",
        "color.exposure",
        "color.gamma",
        "color.look",
        ]

class Color_Master_presets(bpy.types.Menu):
    '''Presets for render settings.'''
    bl_label = "ColorMaster Presets"
    bl_idname = "Color_Master_presets"
    preset_subdir = "color_master_preset"
    preset_operator = "script.execute_preset"

    draw = bpy.types.Menu.draw_preset

#################
# Add more luts #
#################
class Add_More_Luts(bpy.types.Operator):
    """Add more luts"""
    bl_idname = "scene.add_more_luts"
    bl_label = "Add more looks"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global lut_label
        global lut_label_icon
        global just_installed

        colormanagement = os.path.dirname(__file__) + "/colormanagement"

        #dstnew = os.path.join(bpy.app.binary_path, "2.77", "datafiles", "colormanagement")
        dstnew = bpy.utils.user_resource('DATAFILES')
        dst = os.path.join(dstnew, "colormanagement")

        dirExists = os.path.isdir(dst)

        if dirExists:
            shutil.rmtree(dst)

        shutil.copytree(colormanagement, dst)
        self.report({'INFO'}, "The New Looks Are Installed!")

        lut_label = "The new looks are installed! You must restart Blender for the changes to take effect."
        lut_label_icon = 'FILE_TICK'
        just_installed = "installed"

        return {'FINISHED'}

###################
# Remove the luts #
###################
class Remove_The_Luts(bpy.types.Operator):
    """Remove the luts"""
    bl_idname = "scene.remove_the_luts"
    bl_label = "Remove the looks"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global just_installed
        dstnew = bpy.utils.user_resource('DATAFILES')
        dst = os.path.join(dstnew, "colormanagement")

        dirExists = os.path.isdir(dst)

        if dirExists:
            shutil.rmtree(dst)

        self.report({'INFO'}, "The New Looks Are Uninstalled!")

        lut_label = "The new looks have been uninstalled! You must restart Blender for the changes to take effect."
        lut_label_icon = 'FILE_TICK'
        just_installed = "installed"

        return {'FINISHED'}

######################
# Previous Enum Item #
######################
class Previous_Enum_Item(bpy.types.Operator):
    """Previous enum item"""
    bl_idname = "scene.previous_enum_item"
    bl_label = "Previous look"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        global image_paths
        try:
            current_enum = context.window_manager.my_previews
            current_index = image_paths.index(current_enum)
        except:
            self.report({'ERROR'}, "Current enum value not in list")
            return {'CANCELLED'}

        if current_index == 0:
            context.window_manager.my_previews = image_paths[-1] # will re-call update function
            # tehcncially this is unnecessary, but separated to show the wrap-around
        else:
            context.window_manager.my_previews = image_paths[current_index-1] # will re-call update function

        return {'FINISHED'}

##################
# Next Enum Item #
##################
class Next_Enum_Item(bpy.types.Operator):
    """Next enum item"""
    bl_idname = "scene.next_enum_item"
    bl_label = "Next look"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # try:
        global image_paths
        try:
            current_enum = context.window_manager.my_previews
            current_index = image_paths.index(current_enum)
        except:
            self.report({'ERROR'}, "Current enum value not in list")
            return {'CANCELLED'}

        if current_index == len(image_paths)-1:
            context.window_manager.my_previews = image_paths[0] # will re-call update function
        else:
            context.window_manager.my_previews = image_paths[current_index+1] # will re-call update function

        return {'FINISHED'}

class ColorMasterPanel(bpy.types.Panel):
    """Creates a Panel in the node toolshelf"""
    bl_label = "ColorMaster"
    bl_idname = "OBJECT_PT_previews"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "BlenderMaster"
    
    @classmethod
    def poll(self, context):
        try:
            preferences = context.user_preferences.addons["colormaster"].preferences
            return (preferences.use_node_panel)
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        
        col = layout.column_flow(align=True)
        row = col.row(align=True)
        row.menu("Color_Master_presets", text=bpy.types.Color_Master_presets.bl_label)
        row.operator("render.color_master_preset_add", text="", icon='ZOOMIN')
        row.operator("render.color_master_preset_add", text="", icon='ZOOMOUT').remove_active = True
        
        row = layout.row()
        col = row.column()
        col.scale_y= 6
        col.operator("scene.previous_enum_item", icon="TRIA_LEFT",text="")
        col = row.column()
        col.scale_y= 1
        col.template_icon_view(wm, "my_previews", show_labels=True)
        col = row.column()
        col.scale_y= 6
        col.operator("scene.next_enum_item", icon="TRIA_RIGHT",text="")
        
        col = layout.column()
        col.template_colormanaged_view_settings(scene, "view_settings")
        
class ColorMasterImagePanel(bpy.types.Panel):
    """Creates a Panel in the image editor toolshelf"""
    bl_label = "ColorMaster"
    bl_idname = "OBJECT_PT_imagepreviews"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "BlenderMaster"
    
    @classmethod
    def poll(self, context):
        try:
            preferences = context.user_preferences.addons["colormaster"].preferences
            return (preferences.use_image_panel)
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        
        col = layout.column_flow(align=True)
        row = col.row(align=True)
        row.menu("Color_Master_presets", text=bpy.types.Color_Master_presets.bl_label)
        row.operator("render.color_master_preset_add", text="", icon='ZOOMIN')
        row.operator("render.color_master_preset_add", text="", icon='ZOOMOUT').remove_active = True
        
        row = layout.row()
        col = row.column()
        col.scale_y= 6
        col.operator("scene.previous_enum_item", icon="TRIA_LEFT",text="")
        col = row.column()
        col.scale_y= 1
        col.template_icon_view(wm, "my_previews", show_labels=True)
        col = row.column()
        col.scale_y= 6
        col.operator("scene.next_enum_item", icon="TRIA_RIGHT",text="")
        
        col = layout.column()
        col.template_colormanaged_view_settings(scene, "view_settings")

class ColorMasterScreenPanel(bpy.types.Panel):
    """Creates a Panel in the node toolshelf"""
    bl_label = "ColorMaster"
    bl_idname = "OBJECT_PT_previews"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
    @classmethod
    def poll(self, context):
        try:
            preferences = context.user_preferences.addons["colormaster"].preferences
            return (preferences.use_scene_panel)
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        
        col = layout.column_flow(align=True)
        row = col.row(align=True)
        row.menu("Color_Master_presets", text=bpy.types.Color_Master_presets.bl_label)
        row.operator("render.color_master_preset_add", text="", icon='ZOOMIN')
        row.operator("render.color_master_preset_add", text="", icon='ZOOMOUT').remove_active = True
        
        row = layout.row()
        col = row.column()
        col.scale_y= 6
        col.operator("scene.previous_enum_item", icon="TRIA_LEFT",text="")
        col = row.column()
        col.scale_y= 1
        col.template_icon_view(wm, "my_previews", show_labels=True)
        col = row.column()
        col.scale_y= 6
        col.operator("scene.next_enum_item", icon="TRIA_RIGHT",text="")
        
        col = layout.column()
        col.template_colormanaged_view_settings(scene, "view_settings")

# We can store multiple preview collections here,
# however in this example we only store "main"
preview_collections = {}

class ColorMasterPreferences(bpy.types.AddonPreferences):
    # bl_idname = "colormaster"
    bl_idname = __package__
    scriptdir = bpy.path.abspath(os.path.dirname(__file__))

    use_node_panel = bpy.props.BoolProperty(
        name="Use Node Editor Panel",
        description="Use the BlenderMaster > ColorMaster section in the node editor.",
        default=True,
    )
    
    use_image_panel = bpy.props.BoolProperty(
        name="Use Image Editor Panel",
        description="Use the BlenderMaster > ColorMaster section in the image editor.",
        default=True,
    )
    
    use_scene_panel = bpy.props.BoolProperty(
        name="Use Scene Panel",
        description="Use the ColorMaster section in the scene panel of the properties editor.",
        default=True,
    )

    global just_installed
    just_installed = "uninstalled"

    def draw(self, context):
        global lut_label
        global lut_label_icon

        dst1 = bpy.utils.user_resource('DATAFILES')
        dst2 = os.path.join(dst1, "colormanagement")

        dirExists = os.path.isdir(dst2)

        if dirExists:
            if just_installed != "uninstalled":
                lut_label = "The new looks are installed! You must restart Blender for the changes to take effect."
                lut_label_icon = 'FILE_TICK'

            elif just_installed != "installed":
                lut_label = "Press the button below re-install the extra looks."
                lut_label_icon = 'FILE_REFRESH'

        else:
            lut_label = "Press the button below to add the extra looks. You must restart Blender afterwards."
            lut_label_icon = 'CANCEL'

        layout = self.layout
        preferences = context.user_preferences.addons[__package__].preferences
        
        pcoll = preview_collections["main"]

        layout.label(text=lut_label, icon=lut_label_icon)

        row = layout.row()
        row.scale_y = 1.5
        row.operator("scene.add_more_luts", icon='COLOR')

        if dirExists:
            row = layout.row()
            row.scale_y = 1.25
            row.operator("scene.remove_the_luts", icon='CANCEL')

        layout.separator()
        layout.label(
            text="Here you can choose where the ColorMaster panel is, "
                 "in case it interferes with other tools or is just plain annoying")
        
        #my_icon = pcoll["my_icon"]
        #layout.label(text="l", icon_value=my_icon.icon_id)

        split = layout.split(percentage=0.25)

        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Node Editor", icon="NODETREE")
        sub.prop(self, "use_node_panel")

        sub.separator()

        sub.label(text="Image Editor", icon="IMAGE_COL")
        sub.prop(self, "use_image_panel")

        sub.separator()
        
        sub.label(text="Scene Panel", icon="SCENE_DATA")
        sub.prop(self, "use_scene_panel")

        col = split.column()
        sub = col.column(align=True)
        sub.label(text="")  # Node icon
        sub.label(
            text="Use the BlenderMaster > ColorMaster section in the node editor.")

        sub.separator()
        sub.label(text="")  # Image icon
        sub.label(
            text="Use the BlenderMaster > ColorMaster section in the image editor.")
        
        sub.separator()
        sub.label(text="")  # Scene icon
        sub.label(
            text="Use the ColorMaster section in the scene panel of the properties editor.")

################
# Registration #
################

addon_dir = bpy.utils.user_resource('SCRIPTS', "addons")

def register():
    from bpy.types import WindowManager
    from bpy.props import (
            StringProperty,
            EnumProperty,
            )

    WindowManager.my_previews_dir = StringProperty(
            name="Folder Path",
            subtype='DIR_PATH',
            default=addon_dir + "/colormaster/color_previews"
            )

    WindowManager.my_previews = EnumProperty(
            items=enum_previews_from_directory_items,
            update=change_image_cb
            )

    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()

    preview_collections["main"] = pcoll
    
    bpy.app.handlers.scene_update_post.append(load_handler)
    
    bpy.utils.register_class(Color_Master_preset_add)
    bpy.utils.register_class(Color_Master_presets)

    bpy.utils.register_class(ColorMasterPanel)
    bpy.utils.register_class(ColorMasterImagePanel)
    bpy.utils.register_class(ColorMasterScreenPanel)
    
    bpy.utils.register_class(ColorMasterPreferences)
    
    bpy.utils.register_class(Add_More_Luts)
    bpy.utils.register_class(Remove_The_Luts)
    
    bpy.utils.register_class(Previous_Enum_Item)
    bpy.utils.register_class(Next_Enum_Item)

def unregister():
    bpy.app.handlers.scene_update_post.remove(load_handler)

    from bpy.types import WindowManager

    del WindowManager.my_previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    bpy.utils.unregister_class(Color_Master_preset_add)
    bpy.utils.unregister_class(Color_Master_presets)

    bpy.utils.unregister_class(ColorMasterPanel)
    bpy.utils.unregister_class(ColorMasterImagePanel)
    bpy.utils.unregister_class(ColorMasterScreenPanel)
    
    bpy.utils.unregister_class(ColorMasterPreferences)
    
    bpy.utils.unregister_class(Add_More_Luts)
    bpy.utils.unregister_class(Remove_The_Luts)
    
    bpy.utils.unregister_class(Previous_Enum_Item)
    bpy.utils.unregister_class(Next_Enum_Item)

if __name__ == "__main__":
    register()
