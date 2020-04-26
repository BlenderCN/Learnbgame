import bpy
import os

addon_name = os.path.basename(os.path.dirname(__file__))

class PlayblasterAddonPrefs(bpy.types.AddonPreferences) :
    bl_idname = addon_name

    prefs_folderpath : bpy.props.StringProperty(
            name = "Preferences Folder Path",
            default = os.path.join(bpy.utils.user_resource('CONFIG'), "playblaster"),
            description = "Folder where temporary Playblast are stored",
            subtype = "DIR_PATH"
            )

    player_path : bpy.props.StringProperty(
            name = "External Player Path",
            description = "Path of the executable of external player",
            subtype = "DIR_PATH"
            )

    # PROGRESS BAR
    progress_bar_color : bpy.props.FloatVectorProperty(
            name = "Progress Bar",
            size = 3,
            min = 0.0,
            max = 1.0,
            default = [1, 1, 1],
            subtype = 'COLOR'
            )

    progress_bar_background_color : bpy.props.FloatVectorProperty(
            name = "Background",
            size = 3,
            min = 0.0,
            max = 1.0,
            default = [0.2, 0.2, 0.2],
            subtype = 'COLOR'
            )

    progress_bar_size : bpy.props.IntProperty(
            name = "Progress Bar Size",
            min = 1,
            max = 100,
            default = 10
            )

    def draw(self, context) :
        layout = self.layout

        layout.prop(self, "prefs_folderpath")

        box = layout.box()
        row = box.row(align = True)
        row.label(text = "Progress Bar", icon = 'TIME')
        row.prop(self, 'progress_bar_color', text = '')
        row.prop(self, 'progress_bar_size', text = 'Size')
        row.prop(self, 'progress_bar_background_color')

# get addon preferences
def get_addon_preferences():
    addon = bpy.context.preferences.addons.get(addon_name)
    return getattr(addon, "preferences", None)
