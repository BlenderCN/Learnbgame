import bpy
from bpy.props import *
import bgl
import os
from . constants import *
__reload_order_index__ = -20

# METHODS
#############################################
def _get_base_files_dir_error(prefs):
    self = prefs
    base_files_dir_error = None
    if not os.path.exists(self.base_files_dir):
        base_files_dir_error = "The path doesn't exist."
    elif not os.path.exists(os.path.join(self.base_files_dir, "roq.exe")):
        base_files_dir_error = "The folder doesn't contain the roq compiler."
    elif not all(os.path.exists(os.path.join(self.base_files_dir, "default_sky", sky_file))
                 for sky_file in
                 ["THUG_sky.scn.xbx", "THUG_sky.tex.xbx", "THUG2_sky.scn.xbx", "THUG2_sky.tex.xbx"]):
        base_files_dir_error = "The folder doesn't contain the default sky files."
    return base_files_dir_error

def is_valid_game_path(path):
    # We need at least these folders to be available to consider it a valid game path
    if not os.path.exists(os.path.join(path, "images")):
        return False
    if not os.path.exists(os.path.join(path, "Levels")):
        return False
    if not os.path.exists(os.path.join(path, "models")):
        return False
    if not os.path.exists(os.path.join(path, "textures")):
        return False
        
    return True
    
def get_game_asset_paths(context):
    scn = context.scene
    addon_prefs = context.user_preferences.addons[ADDON_NAME].preferences
    if not hasattr(scn, 'thug_level_props') or not hasattr(scn.thug_level_props, 'export_props'):
        print("Unable to read game files - Cannot find level/export properties")
        return [], ""
    if scn.thug_level_props.export_props.target_game == '':
        print("Unable to read game files - target game not set")
        return [], ""
        
    target_game = scn.thug_level_props.export_props.target_game
    game_paths = []
    ext_suffix = ""
    if target_game == 'THUG1':
        if not is_valid_game_path(addon_prefs.game_data_dir_thug1):
            print("Unable to read game files - game path {} is not valid.".format(addon_prefs.game_data_dir_thug1))
        else:
            game_paths.append(addon_prefs.game_data_dir_thug1)
            
    elif target_game == 'THUG2':
        ext_suffix = ".xbx"
        if not is_valid_game_path(addon_prefs.game_data_dir_thug2):
            print("Unable to read game files - game path {} is not valid.".format(addon_prefs.game_data_dir_thug2))
        else:
            game_paths.append(addon_prefs.game_data_dir_thug2)
            
        if not is_valid_game_path(addon_prefs.game_data_dir_thugpro):
            print("Unable to read game files - game path {} is not valid.".format(addon_prefs.game_data_dir_thugpro))
        else:
            game_paths.append(addon_prefs.game_data_dir_thugpro)
    else:
        print("Unable to read game files - target game is {}".format(target_game))
        return [], ""
        
    return game_paths, ext_suffix
    
    
# PROPERTIES
#############################################
class THUGAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_NAME

    base_files_dir = StringProperty(
        name="Base files directory",
        subtype='DIR_PATH',
        default="D:\\thug_tools\\",
        )

    line_width = FloatProperty(name="Line Width", min=0, max=15, default=10, description="Size of autorail lines displayed in the viewport.")

    autorail_edge_color = FloatVectorProperty(
        name="Mesh Rail Edge Color",
        size=4,
        min=0.0,
        max=1.0,
        subtype="COLOR",
        default=(1.0, 0.0, 0.0, 1.0))

    rail_end_connection_color = FloatVectorProperty(
        name="Rail End Connection Color",
        size=4,
        min=0.0,
        max=1.0,
        subtype="COLOR",
        default=(1.0, 1.0, 0.0, 1.0))

    bad_face_color = FloatVectorProperty(
        name="Bad Face Color",
        size=4,
        min=0.0,
        max=1.0,
        subtype="COLOR",
        default=(1.0, 0.0, 1.0, 0.5))

    vert_face_color = FloatVectorProperty(
        name="Vert Face Color",
        size=4,
        min=0.0,
        max=1.0,
        subtype="COLOR",
        default=(0.0, 0.0, 1.0, 0.5))

    wallridable_face_color = FloatVectorProperty(
        name="Wallridable Face Color",
        size=4,
        min=0.0,
        max=1.0,
        subtype="COLOR",
        default=(0.0, 1.0, 1.0, 0.5))

    trigger_face_color = FloatVectorProperty(
        name="Trigger Face Color",
        size=4,
        min=0.0,
        max=1.0,
        subtype="COLOR",
        default=(0.0, 1.0, 0.0, 0.5))

    non_collidable_face_color = FloatVectorProperty(
        name="Non Collidable Face Color",
        size=4,
        min=0.0,
        max=1.0,
        subtype="COLOR",
        default=(1.0, 1.0, 0.0, 0.5))

    mix_face_colors = BoolProperty(name="Mix Face Colors", default=False)
    show_bad_face_colors = BoolProperty(name="Highlight Bad Faces", default=True,
        description="Colorize faces with bad collision flag combinations using Bad Face Color.")

    object_settings_tools = BoolProperty(name="Show Object Settings in the Tools Tab", default=True)
    material_settings_tools = BoolProperty(name="Show Material Settings in the Tools Tab", default=True)
    material_pass_settings_tools = BoolProperty(name="Show Material Pass Settings in the Tools Tab", default=True)

    # New settings as of io_thps_scene v1.2
    path_bevel_size = FloatProperty(name="Rail/Waypoint path size", min=0.1, max=128, default=1, description="Default size displayed in the viewport for all rail, ladder, and waypoint paths.")
    game_data_dir_thug1 = StringProperty(
        name="Game directory - THUG1",
        subtype='DIR_PATH',
        default="C:\\",
        description="Path to your game files for THUG1 - select the 'Data' folder."
        )
    game_data_dir_thug2 = StringProperty(
        name="Game directory - THUG2",
        subtype='DIR_PATH',
        default="C:\\",
        description="Path to your game files for THUG2 (Base game, NOT the THUG PRO files) - select the 'Data' folder."
        )
    game_data_dir_thugpro = StringProperty(
        name="Game directory - THUG PRO",
        subtype='DIR_PATH',
        default="C:\\",
        description="Path to your game files for THUG PRO (NOT the base game files) - select the 'Data' folder."
        )
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "base_files_dir")
        layout.prop(self, "game_data_dir_thug1")
        layout.prop(self, "game_data_dir_thug2")
        layout.prop(self, "game_data_dir_thugpro")
        base_files_dir_error = _get_base_files_dir_error(self)
        if base_files_dir_error:
            layout.label(
                text="Incorrect path: {}".format(base_files_dir_error),
                icon="ERROR")

        for prop in ["autorail_edge_color",
                     "rail_end_connection_color",
                     "bad_face_color",
                     "vert_face_color",
                     "wallridable_face_color",
                     "trigger_face_color",
                     "non_collidable_face_color",]:
            layout.row().prop(self, prop)
        row = layout.row()
        row.prop(self, "mix_face_colors")
        row.prop(self, "show_bad_face_colors")
        row = layout.row()
        row.prop(self, "line_width")
        row.prop(self, "path_bevel_size")
        layout.prop(self, "object_settings_tools")
        layout.prop(self, "material_settings_tools")
        layout.prop(self, "material_pass_settings_tools")

