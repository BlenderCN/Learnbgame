import bpy
import bgl
from bpy.props import *
import glob
from . constants import *
from . helpers import *
from . autorail import *
from . collision import *
from . material import *
from . ui_draw import *
from . presets import *
from .  import script_template
from . tex import import_img
from . import bake

# METHODS
#############################################
#----------------------------------------------------------------------------------
# Applies a context-specific mesh as a child of the empty when applicable
# This just makes it easier to see presets like restarts, CTF flags etc
#----------------------------------------------------------------------------------
def thug_empty_update(self, context):
    if context.object.type != "EMPTY":
        return
    ob = context.object
    for mdl_ob in ob.children:
        if mdl_ob.type == 'MESH':
            context.scene.objects.unlink(mdl_ob)
            bpy.data.objects.remove(mdl_ob)
    mdl_mesh = ''
    mdl_preview = ''
    preset_scale = get_actual_preset_size() / 2.0
    
    if ob.thug_empty_props.empty_type == 'Restart':
        mdl_mesh = 'Sk3Ed_RS_1p'
        if ob.thug_restart_props.restart_type == 'Player2':
            mdl_mesh = 'Sk3Ed_RS_Mp'
        elif ob.thug_restart_props.restart_type == 'Multiplayer':
            mdl_mesh = 'Sk3Ed_RS_Ho'
        elif ob.thug_restart_props.restart_type == 'Horse':
            mdl_mesh = 'Sk3Ed_RS_Ho'
        elif ob.thug_restart_props.restart_type == 'CTF':
            mdl_mesh = 'Sk3Ed_RS_Ho'
        ob.empty_draw_type = 'CUBE'
        ob.empty_draw_size = 36 * preset_scale
        
    if ob.thug_empty_props.empty_type == 'GameObject':
        mdl_mesh = ''
        if ob.thug_go_props.go_type == 'Flag_Blue' or ob.thug_go_props.go_type == 'Team_Blue' :
            mdl_mesh = 'CTF_Flag_Blue'
        elif ob.thug_go_props.go_type == 'Flag_Red' or ob.thug_go_props.go_type == 'Team_Red':
            mdl_mesh = 'CTF_Flag_Red'
        elif ob.thug_go_props.go_type == 'Flag_Green' or ob.thug_go_props.go_type == 'Team_Green':
            mdl_mesh = 'CTF_Flag_Green'
        elif ob.thug_go_props.go_type == 'Flag_Yellow' or ob.thug_go_props.go_type == 'Team_Yellow':
            mdl_mesh = 'CTF_Flag_Yellow'
        if ob.thug_go_props.go_type == 'Flag_Blue_Base' or ob.thug_go_props.go_type == 'Team_Blue_Base':
            mdl_mesh = 'CTF_Base_Blue'
        elif ob.thug_go_props.go_type == 'Flag_Red_Base' or ob.thug_go_props.go_type == 'Team_Red_Base':
            mdl_mesh = 'CTF_Base_Red'
        elif ob.thug_go_props.go_type == 'Flag_Green_Base' or ob.thug_go_props.go_type == 'Team_Green_Base':
            mdl_mesh = 'CTF_Base_Green'
        elif ob.thug_go_props.go_type == 'Flag_Yellow_Base' or ob.thug_go_props.go_type == 'Team_Yellow_Base':
            mdl_mesh = 'CTF_Base_Yellow'
        elif ob.thug_go_props.go_type == 'Secret_Tape':
            mdl_mesh = 'SecretTape'
        elif ob.thug_go_props.go_type.startswith('Combo_'):
            mdl_mesh = ob.thug_go_props.go_type
        elif ob.thug_go_props.go_model != '':
            mdl_preview = ob.thug_go_props.go_model 
            
        ob.empty_draw_type = 'CUBE'
        ob.empty_draw_size = 36 * preset_scale
        
    elif ob.thug_empty_props.empty_type == 'CubemapProbe' or ob.thug_empty_props.empty_type == 'LightProbe':
        mdl_mesh = ''
        ob.empty_draw_type = 'SPHERE'
        ob.empty_draw_size = 64 * preset_scale
        ob.show_name = True
        ob.show_x_ray = True
        
    elif ob.thug_empty_props.empty_type == 'LightVolume':
        mdl_mesh = ''
        ob.empty_draw_type = 'ARROWS'
        ob.empty_draw_size = 64 * preset_scale
        
    elif ob.thug_empty_props.empty_type == 'GenericNode' and ob.thug_generic_props.generic_type == 'Crown':
        mdl_mesh = 'Sk3Ed_RS_KOTH'
        ob.empty_draw_type = 'CUBE'
        ob.empty_draw_size = 42 * preset_scale
        
    elif ob.thug_empty_props.empty_type == 'Pedestrian':
        if ob.thug_ped_props.ped_source == 'Model' and ob.thug_ped_props.ped_model != '':
            mdl_preview = ob.thug_ped_props.ped_model
        mdl_mesh = 'Ped01'
        ob.empty_draw_type = 'CUBE'
        ob.empty_draw_size = 42 * preset_scale
        
    elif ob.thug_empty_props.empty_type == 'Vehicle':
        if ob.thug_veh_props.veh_model != '':
            mdl_preview = ob.thug_veh_props.veh_model 
        mdl_mesh = 'Veh_Taxi'
        ob.empty_draw_type = 'CUBE'
        ob.empty_draw_size = 42 * preset_scale
        
    elif ob.thug_empty_props.empty_type == 'ParticleObject':
        ob.empty_draw_type = 'PLAIN_AXES'
        ob.empty_draw_size = 64 * preset_scale
        draw_particle_preview(ob, context)
        return
        
    # Add the helper/preview mesh if it applies to this object
    use_fallback = False
    if mdl_preview != '':
        print("Attempting to generate preview mesh from asset {}".format(mdl_preview))
        scn = context.scene
        if not hasattr(scn, 'thug_level_props') or not hasattr(scn.thug_level_props, 'export_props'):
            print("Export props not found")
            use_fallback = True
        
        elif scn.thug_level_props.export_props.target_game == '':
            print("Target game not found")
            use_fallback = True
            
        if not use_fallback:
            target_game = scn.thug_level_props.export_props.target_game
            mdl_obs = append_from_assets( os.path.join('Models', mdl_preview), target_game, context )
            if len(mdl_obs) == 0:
                print("No meshes were found in {}".format(os.path.join('Models', mdl_preview)))
                use_fallback = True
                
            for mdl_ob in mdl_obs:
                mdl_ob.name = ob.name + '_MDL'
                #mdl_ob.location = [ 0, 0, 0 ]
                #mdl_ob.rotation_euler = [ 0, 0, 0 ]
                mdl_ob.scale = [preset_scale, preset_scale, preset_scale]
                mdl_ob.parent = ob
                mdl_ob.hide_select = True
                mdl_ob.hide_render = True
                mdl_ob.thug_export_scene = False
                mdl_ob.thug_export_collision = False
                to_group(mdl_ob, "Visual Helpers")
            
        
    if mdl_mesh != '' and (mdl_preview == '' or use_fallback):
        mdl_ob = append_from_dictionary('presets', mdl_mesh, context.scene)
        mdl_ob.name = ob.name + '_MDL'
        mdl_ob.location = [ 0, 0, 0 ]
        mdl_ob.rotation_euler = [ 0, 0, 0 ]
        mdl_ob.scale = [preset_scale, preset_scale, preset_scale]
        mdl_ob.parent = ob
        mdl_ob.hide_select = True
        mdl_ob.hide_render = True
        mdl_ob.thug_export_scene = False
        mdl_ob.thug_export_collision = False
        to_group(mdl_ob, "Visual Helpers")
    
def draw_particle_preview(ob, context):
    scene = context.scene
    expected_obs = [ ob.name + "_START", ob.name + "_MID", ob.name + "_END" ]
    found_obs = []
    for mdl_ob in ob.children:
        if mdl_ob.type != 'EMPTY': continue
        for name in expected_obs:
            if mdl_ob.name == name:
                found_obs.append(name)
                    
    # Look for the particle properties
    if not hasattr(ob, 'thug_particle_props'): return
    particle_img = None
    if ob.thug_particle_props.particle_texture != '':
        # Search for the .img file referenced and load it, if we don't have it already
        if not bpy.data.images.get(ob.thug_particle_props.particle_texture + ".img"):
            game_paths, ext_suffix = get_game_asset_paths(context)
            img_path = os.path.join('images', 'particles', ob.thug_particle_props.particle_texture + ".img" + ext_suffix)
            for game_path in game_paths:
                if os.path.exists(os.path.join(game_path, img_path)):
                    particle_img = import_img( os.path.join(game_path, img_path), ob.thug_particle_props.particle_texture + ".img" )
                    particle_img.pack(as_png=True)
        else:
            particle_img = bpy.data.images.get(ob.thug_particle_props.particle_texture + ".img")
                
    for name in expected_obs:
        if name not in found_obs:
            new_ob = bpy.data.objects.new(name, None)
            new_ob.rotation_euler = [ 1.570796, 0, 0 ]
            new_ob.empty_draw_type = 'IMAGE'
            new_ob.parent = ob
            scene.objects.link(new_ob)
        
    ob_start = bpy.data.objects.get(expected_obs[0])
    ob_mid = bpy.data.objects.get(expected_obs[1])
    ob_end = bpy.data.objects.get(expected_obs[2])
    
    if particle_img:
        ob_start.data = particle_img
        ob_mid.data = particle_img
        ob_end.data = particle_img
    ob_start.location = ob.thug_particle_props.particle_startposition
    ob_mid.location = ob.thug_particle_props.particle_midposition
    ob_end.location = ob.thug_particle_props.particle_endposition
    ob_start.empty_draw_size = ob.thug_particle_props.particle_boxdimsstart[2]
    ob_mid.empty_draw_size = ob.thug_particle_props.particle_boxdimsmid[2]
    ob_end.empty_draw_size = ob.thug_particle_props.particle_boxdimsend[2]
                
            
                    
            
#----------------------------------------------------------------------------------
#- Updates the list(s) of TH nodes in the current scene
#- Used by the WindowManager to fill autocomplete lists on other props
#----------------------------------------------------------------------------------
@bpy.app.handlers.persistent
def update_node_collection(*args):
    #print("Updating node collections...")
    context = bpy.context
    context.window_manager.thug_all_nodes.paths.clear()
    context.window_manager.thug_all_nodes.restarts.clear()
    context.window_manager.thug_all_nodes.meshes.clear()
    context.window_manager.thug_all_nodes.scripts.clear()
    
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and ( ob.thug_export_collision or ob.thug_export_scene ):
            entry = context.window_manager.thug_all_nodes.meshes.add()
            entry.name = ob.name
        elif ob.type == 'EMPTY' and ob.thug_empty_props.empty_type == 'Restart':
            entry = context.window_manager.thug_all_nodes.restarts.add()
            entry.name = ob.name
        elif ob.type == 'CURVE' and ob.thug_path_type in [ 'Rail', 'Ladder', 'Waypoint' ]:
            entry = context.window_manager.thug_all_nodes.paths.add()
            entry.name = ob.name
            
    for tx in bpy.data.texts:
        if tx.name.startswith('script_'):
            entry = context.window_manager.thug_all_nodes.scripts.add()
            entry.name = format_triggerscript_name(tx.name)
            
            
#----------------------------------------------------------------------------------
#- Updates the list of available models/images and other assets from the base game
#- Requires the plugin settings pointing to a valid game path
#----------------------------------------------------------------------------------
@bpy.app.handlers.persistent
def update_game_files_collections(*args):
    print("Generating asset lists from the base game...")
    
    context = bpy.context
    context.window_manager.thug_game_assets.models.clear()
    context.window_manager.thug_game_assets.skins.clear()
    context.window_manager.thug_game_assets.images.clear()
    context.window_manager.thug_game_assets.particle_textures.clear()
    
    # Make sure we actually have a target game first
    scn = context.scene
    if not hasattr(scn, 'thug_level_props') or not hasattr(scn.thug_level_props, 'export_props'):
        print("Unable to read game files - Cannot find level/export properties")
        return
    if scn.thug_level_props.export_props.target_game == '':
        print("Unable to read game files - target game not set")
        return
        
    target_game = scn.thug_level_props.export_props.target_game
    addon_prefs = bpy.context.user_preferences.addons[ADDON_NAME].preferences
    ext_suffix = ""
    
    game_paths = []
    if target_game == 'THUG1':
        game_paths.append(addon_prefs.game_data_dir_thug1)
    elif target_game == 'THUG2':
        game_paths.append(addon_prefs.game_data_dir_thug2)
        game_paths.append(addon_prefs.game_data_dir_thugpro)
        ext_suffix = ".xbx"
    else:
        print("Unable to read game files - target game is {}".format(target_game))
        return
        
    for game_path in game_paths:
        # Then, make sure the path to that game is correctly configured in the plugin settings
        if not is_valid_game_path(game_path):
            print("Unable to read game files - game path {} is not valid.".format(game_path))
            continue
        
        #print("Searching for files in: {}".format(game_path))
        
        model_files = glob.glob(game_path + "Models/**/*.mdl" + ext_suffix, recursive=True)
        print("Searching for MODELS...")
        for temp_path in model_files:
            short_path = os.path.relpath(temp_path, game_path + "Models")
            if target_game == 'THUG2':
                short_path = short_path[:-4]
                
            #print(short_path)
            entry = context.window_manager.thug_game_assets.models.add()
            entry.name = short_path
            
        skin_files = glob.glob(game_path + "Models/**/*.skin" + ext_suffix, recursive=True)
        print("Searching for SKINS...")
        for temp_path in skin_files:
            short_path = os.path.relpath(temp_path, game_path + "Models")
            if target_game == 'THUG2':
                short_path = short_path[:-4]
            entry = context.window_manager.thug_game_assets.skins.add()
            entry.name = short_path
            #print(short_path)
            
        img_files = glob.glob(game_path + "images/**/*.img" + ext_suffix, recursive=True)
        print("Searching for IMAGES...")
        for temp_path in img_files:
            short_path = os.path.relpath(temp_path, game_path + "images")
            if target_game == 'THUG2':
                short_path = short_path[:-4]
            entry = context.window_manager.thug_game_assets.images.add()
            entry.name = short_path
            #print(short_path)
            
        tex_files = glob.glob(game_path + "images/particles/*.img" + ext_suffix, recursive=False)
        print("Searching for PARTICLE TEXTURES...")
        for temp_path in tex_files:
            short_path = os.path.relpath(temp_path, game_path + "images/particles")
            if target_game == 'THUG2':
                short_path = short_path[:-4]
            short_path = short_path[:-4]
            entry = context.window_manager.thug_game_assets.particle_textures.add()
            entry.name = short_path
            #print(short_path)
        
    

#----------------------------------------------------------------------------------
#- Determines the version of the Blender plugin that the scene was created with
#- and if it's out of date, attempts to automatically convert old nodes to any
#- systems that have been updated - e.g., empty nodes on the asdf plugin need to be
#- migrated, along with TriggerScript references
#----------------------------------------------------------------------------------
@bpy.app.handlers.persistent
def maybe_upgrade_scene(*args):
    should_upgrade = False
    something_was_updated = False
    fix_objects = []
    
    newmat_passes = [
        'ugplus_matslot_diffuse'
        ,'ugplus_matslot_detail'
        ,'ugplus_matslot_normal'
        ,'ugplus_matslot_normal2'
        ,'ugplus_matslot_displacement'
        ,'ugplus_matslot_displacement2'
        ,'ugplus_matslot_specular'
        #,'ugplus_matslot_smoothness'
        ,'ugplus_matslot_reflection'
        ,'ugplus_matslot_lightmap'
        ,'ugplus_matslot_lightmap2'
        ,'ugplus_matslot_lightmap3'
        ,'ugplus_matslot_lightmap4'
        ,'ugplus_matslot_weathermask'
        ,'ugplus_matslot_snow'
        ,'ugplus_matslot_fallback'
        ,'ugplus_matslot_diffuse_night'
        ,'ugplus_matslot_diffuse_evening'
        ,'ugplus_matslot_diffuse_morning'
        ,'ugplus_matslot_cloud'
    ]
    # Hack for the new material system's image fields - read from the txt reference and set the image
    for mat in bpy.data.materials:
        if hasattr(mat, 'thug_material_props') and hasattr(mat.thug_material_props, 'grass_props'):
            gps = mat.thug_material_props.grass_props
            for i in range(len(gps.grass_textures)):
                if gps.grass_textures[i].tex_image_name != '':
                    thisimage = bpy.data.images.get(gps.grass_textures[i].tex_image_name)
                    if thisimage:
                        #print("Updating grass texture {}...".format(i))
                        gps.grass_textures[i].tex_image = thisimage
                    
                
        if hasattr(mat, 'thug_material_props') and hasattr(mat.thug_material_props, 'ugplus_shader') \
            and mat.thug_material_props.ugplus_shader != '':
            for passname in newmat_passes:
                thispass = getattr(mat.thug_material_props, passname)
                if thispass and thispass.tex_image_name:
                    thisimage = bpy.data.images.get(thispass.tex_image_name)
                    if thisimage:
                        thispass.tex_image = thisimage
                    
                    
    #print("Updating node collections...")
    context = bpy.context
    if 'io_thps_scene_version' not in context.scene or context.scene['io_thps_scene_version'] == None:
        print("This blend file was built with the asdf plugin, or a pre-release version of io_thps_scene. Needs to be updated!")
        should_upgrade = True
    elif context.scene['io_thps_scene_version'] != ADDON_VERSION:
        print("This blend file was built with an older version io_thps_scene. May need to be updated in the future!")
        # Any future versions which require node conversions can be handled here!
        
    if should_upgrade:
        print("Attempting to update nodes in scene to match current version of io_thps_scene...")
        # This is where we actually convert the nodes!
        for ob in bpy.data.objects:
            if ob.type in ['MESH', 'EMPTY', 'CURVE'] and ob.thug_triggerscript_props.triggerscript_type:
            
                # Per-point script references need to be updated from pre-release builds, as they still used the unfiltered script names
                if hasattr(ob.data, 'thug_pathnode_triggers'):
                    tmp_idx = -1
                    for tmp_trig in ob.data.thug_pathnode_triggers:
                        tmp_idx += 1
                        if tmp_trig.script_name != '':
                            print("Updating point script reference {}".format(tmp_trig.script_name))
                            ob.data.thug_pathnode_triggers[tmp_idx].script_name = format_triggerscript_name(tmp_trig.script_name)
                            
                ob_ts = ob.thug_triggerscript_props
                if ob_ts.triggerscript_type == 'None':
                    continue
                # Should be able to do a straight conversion of these over to the template system, 
                # as the base templates should include everything from the old setup
                old_ts_name = ob_ts.triggerscript_type
                ob.thug_triggerscript_props.template_name = old_ts_name
                ob.thug_triggerscript_props.template_name_txt = old_ts_name
                if ob_ts.target_node and bpy.data.objects.get(ob_ts.target_node):
                    # Target node (for Teleport/Killskater) should always be param1 on the new template(s)
                    ob.thug_triggerscript_props.param1_string = get_clean_name(bpy.data.objects.get(ob_ts.target_node))
                    
                # Custom TriggerScript names now use a filtered list of formatted text block names, so we need to
                # update references to remove any leading 'script_' names
                if old_ts_name == 'Custom':
                    ob.thug_triggerscript_props.custom_name = format_triggerscript_name(ob.thug_triggerscript_props.custom_name)
                    
                
                something_was_updated = True
                print("Updated TriggerScript reference for object: {}. Previous TriggerScript was: {}".format(ob.name, old_ts_name))
        
            if ob.type == 'EMPTY' and ob.thug_empty_props.empty_type != 'None':
                # No easy solution for converting these, just warn the user
                something_was_updated = True
                fix_objects.append(ob.name)
                print("Updated empty data for object: {}".format(ob.name))
                    
        # Auto-update the old THUG_SCRIPTS block!
        if 'THUG_SCRIPTS' in bpy.data.texts:
            bpy.ops.io.import_thug_triggerscripts("EXEC_DEFAULT", import_type='ScriptsAndObjects', replace_scripts=False)
            
    context.scene['io_thps_scene_version'] = ADDON_VERSION
    
    def draw(self, context):
        self.layout.label("This scene was built on an older version of the THPS Blender plugin (io_thug_tools). Your scene has been auto-converted to be compatible with this version of the plugin.")
        self.layout.label("However, it may no longer be BACKWARD compatible with the previous plugin. If this is not desired, please make a backup copy before saving the scene.")
        if len(fix_objects) > 0:
            self.layout.label("-------------------------------------------")
            self.layout.label("Some nodes were unable to be converted automatically, such as restarts/CTF Flags. Please review the following objects, as they may need to be re-configured:")
            for obname in fix_objects:
                self.layout.label("        " + obname)
            
    if something_was_updated:
        bpy.context.window_manager.popup_menu(draw, title="Conversion Notice", icon='INFO')
          
          
# PROPERTIES
#############################################
#----------------------------------------------------------------------------------
#- Defines the Class of an empty
#----------------------------------------------------------------------------------
class THUGEmptyProps(bpy.types.PropertyGroup):
    empty_type = EnumProperty(items=(
        ("None", "None", ""),
        ("Restart", "Restart", "Player restarts."),
        ("GenericNode", "Generic Node", "KOTH crown and other objects."),
        ("Pedestrian", "Pedestrian", ""),
        ("Vehicle", "Vehicle", ""),
        ("CubemapProbe", "Reflection Probe", "(Underground+ 1.5+ only) Point used to generate a reflection cubemap. Used by nearby objects"),
        ("ProximNode", "Proximity Node", "Node that can fire events when objects are inside its radius."),
        ("EmitterObject", "Emitter Object", "Node used to play audio streams (typically, ambient sounds in a level)."),
        ("GameObject", "Game Object", "CTF Flags, COMBO letters, etc."),
        ("BouncyObject", "Bouncy Object", "Legacy node type, not used, only for identification in imported levels."),
        ("ParticleObject", "Particle Object", "Used to preserve particle systems in imported levels."),
        ("Custom", "Custom", ""),
        ("LightProbe", "Light Probe", "Approximates nearby ambient lighting for moving objects"),
        ("LightVolume", "Light Volume", "Bounding box used to mark the boundaries of area lights"),
        ), name="Node Type", default="None", update=thug_empty_update)


#----------------------------------------------------------------------------------
class THUGObjectTriggerScriptProps(bpy.types.PropertyGroup):
    # LEGACY PROPERTY - NO LONGER USED
    # List is maintained so the scene converter can still read the value, scripts are assigned
    # using the new template properties below
    triggerscript_type = EnumProperty(items=(
        ("None", "None", ""),
        ("Killskater", "Killskater", "Bail the skater and restart them at the given node."),
        ("Killskater_Water", "Killskater (Water)", "Bail the skater and restart them at the given node."),
        ("Teleport", "Teleport", "Teleport the skater to a given node without breaking their combo."),
        ("Custom", "Custom", "Runs a custom script."),
        ), name="TriggerScript Type", default="None")
    target_node = StringProperty(name="Target Node")
    custom_name = StringProperty(name="Custom Script Name")
    
    # New props used by the templating system!
    template_name = EnumProperty(items=script_template.get_templates, name="Trigger Script", description="This script is executed when the local skater hits the object (or, for nodes, when it is loaded/triggered from another script).", update=script_template.store_triggerscript_params)
    # This is what we actually use for exporting!
    template_name_txt = StringProperty(name="Trigger Script", default="")
    
    param1_int = IntProperty(name="Temp", description="")
    param1_float = FloatProperty(name="Temp", description="")
    param1_string = StringProperty(name="Temp", description="")
    param1_bool = BoolProperty(name="Temp", description="", default=False)
    param1_enum = EnumProperty(items=script_template.get_param1_values, name="Temp", description="", update=script_template.store_triggerscript_params)
    param1_flags = EnumProperty(items=script_template.get_param1_values, name="Temp", description="", options={'ENUM_FLAG'}, update=script_template.store_triggerscript_params)
    
    param2_int = IntProperty(name="Temp", description="")
    param2_float = FloatProperty(name="Temp", description="")
    param2_string = StringProperty(name="Temp", description="")
    param2_bool = BoolProperty(name="Temp", description="", default=False)
    param2_enum = EnumProperty(items=script_template.get_param2_values, name="Temp", description="", update=script_template.store_triggerscript_params)
    param2_flags = EnumProperty(items=script_template.get_param2_values, name="Temp", description="", options={'ENUM_FLAG'}, update=script_template.store_triggerscript_params)
    
    param3_int = IntProperty(name="Temp", description="")
    param3_float = FloatProperty(name="Temp", description="")
    param3_string = StringProperty(name="Temp", description="")
    param3_bool = BoolProperty(name="Temp", description="", default=False)
    param3_enum = EnumProperty(items=script_template.get_param3_values, name="Temp", description="", update=script_template.store_triggerscript_params)
    param3_flags = EnumProperty(items=script_template.get_param3_values, name="Temp", description="", options={'ENUM_FLAG'}, update=script_template.store_triggerscript_params)
    
    param4_int = IntProperty(name="Temp", description="")
    param4_float = FloatProperty(name="Temp", description="")
    param4_string = StringProperty(name="Temp", description="")
    param4_bool = BoolProperty(name="Temp", description="", default=False)
    param4_enum = EnumProperty(items=script_template.get_param4_values, name="Temp", description="", update=script_template.store_triggerscript_params)
    param4_flags = EnumProperty(items=script_template.get_param4_values, name="Temp", description="", options={'ENUM_FLAG'}, update=script_template.store_triggerscript_params)

#----------------------------------------------------------------------------------
#- Proximity node properties
#----------------------------------------------------------------------------------
class THUGProximNodeProps(bpy.types.PropertyGroup):
    proxim_type = EnumProperty(items=(
        ("Camera", "Camera", ""), 
        ("Other", "Other", "")), 
    name="Type", default="Camera")
    proxim_shape = EnumProperty(items=(
        ("BoundingBox", "Bounding Box", ""), 
        ("Sphere", "Sphere", "")), 
    name="Shape", default="BoundingBox")
    proxim_object = BoolProperty(name="Object", default=True)
    proxim_rendertoviewport = BoolProperty(name="RenderToViewport", default=True)
    proxim_selectrenderonly = BoolProperty(name="SelectRenderOnly", default=True)
    proxim_radius = IntProperty(name="Radius", min=0, max=1000000, default=150)
    

#----------------------------------------------------------------------------------
#- Emitter properties
#----------------------------------------------------------------------------------
class THUGEmitterProps(bpy.types.PropertyGroup):
    emit_type = StringProperty(name="Type", default="BoundingBox")
    emit_radius = FloatProperty(name="Radius", min=0, max=1000000, default=0)
    

#----------------------------------------------------------------------------------
#- Cubemap probe properties
#----------------------------------------------------------------------------------
class THUGCubemapProps(bpy.types.PropertyGroup):
    resolution = EnumProperty(
        name="Resolution",
        items=[
            ("64", "64", ""),
            ("128", "128", ""),
            ("256", "256", ""),
            ("512", "512", ""),
            ("1024", "1024", ""),
            ("2048", "2048", "")],
        default="256", 
        description="Maximum resolution for each side of the baked reflection")
        
    box_size = FloatVectorProperty(name="Size", size=3, default=[256.0,256.0,256.0], description="Approximate size of the area captured by this probe. Use (0,0,0) to disable parallax correction")
    size = FloatProperty(name="Size", default=0.0, min=128.0, max=128000.0, description="Approximate size of the rendered area in Blender units (for parallax correction). Use 0.0 to render cubemap at infinite distance")
    exported = BoolProperty(name="Exported", default=False)
    
    
#----------------------------------------------------------------------------------
#- Emitter properties
#----------------------------------------------------------------------------------
class THUGLightVolumeProps(bpy.types.PropertyGroup):
    box_size = FloatVectorProperty(name="Size", size=3, default=[128.0,128.0,128.0], description="Size of the light volume")
    
#----------------------------------------------------------------------------------
#- If you know of another thing GenericNode is used for, let me know!
#----------------------------------------------------------------------------------
class THUGGenericNodeProps(bpy.types.PropertyGroup):
    generic_type = EnumProperty(items=(
        ("Crown", "KOTH Crown", ""), 
        ("Other", "Other", "")) 
    ,name="Node Type",default="Crown")
    

#----------------------------------------------------------------------------------
#- Game objects - models with collision that affect gameplay
#----------------------------------------------------------------------------------
class THUGGameObjectProps(bpy.types.PropertyGroup):
    go_type = EnumProperty(items=(
        ("Ghost", "Ghost", "No model, used for game logic."), 
        ("Flag_Red", "CTF Flag - Red", "Red team flag for CTF."), 
        ("Flag_Blue", "CTF Flag - Blue", "Blue team flag for CTF."), 
        ("Flag_Green", "CTF Flag - Green", "Green team flag for CTF."), 
        ("Flag_Yellow", "CTF Flag - Yellow", "Yellow team flag for CTF."), 
        ("Flag_Red_Base", "CTF Base - Red", "Red team base for CTF."), 
        ("Flag_Blue_Base", "CTF Base - Blue", "Blue team base for CTF."), 
        ("Flag_Green_Base", "CTF Base - Green", "Green team base for CTF."), 
        ("Flag_Yellow_Base", "CTF Base - Yellow", "Yellow team base for CTF."), 
        ("Team_Red", "Team Flag - Red", "Red team selection flag."), 
        ("Team_Blue", "Team Flag - Blue", "Blue team selection flag."), 
        ("Team_Green", "Team Flag - Green", "Green team selection flag."), 
        ("Team_Yellow", "Team Flag - Yellow", "Yellow team selection flag."), 
        ("Team_Red_Base", "Team Base - Red", "Base for Red team selection flag."), 
        ("Team_Blue_Base", "Team Base - Blue", "Base for Blue team selection flag."), 
        ("Team_Green_Base", "Team Base - Green", "Base for Green team selection flag."), 
        ("Team_Yellow_Base", "Team Base - Yellow", "Base for Yellow team selection flag."), 
        ("Secret_Tape", "Secret Tape", ""), 
        ("Combo_C", "Combo Letter C", ""), 
        ("Combo_O", "Combo Letter O", ""), 
        ("Combo_M", "Combo Letter M", ""), 
        ("Combo_B", "Combo Letter B", ""), 
        ("Custom", "Custom", "Specify a custom type and model.")), 
    name="Type", default="Ghost", update=thug_empty_update)
    go_type_other = StringProperty(name="Type", description="Custom type.")
    go_model = StringProperty(name="Model path", default="none", description="Path to the model, relative to Data/Models/.", update=thug_empty_update)
    go_suspend = IntProperty(name="Suspend Distance", description="Distance at which the logic/motion of the object pauses.", min=0, max=1000000, default=0)
    
    
class THUGBouncyProps(bpy.types.PropertyGroup):
    contact = FloatVectorProperty(name="Contact", description="A point used for collision detection.")
    
#----------------------------------------------------------------------------------
#- A list of node names by type, used by the WindowManager to fill
#- autocomplete lists on other properties
#----------------------------------------------------------------------------------
class THUGNodeListProps(bpy.types.PropertyGroup):
    paths = CollectionProperty(type=bpy.types.PropertyGroup)
    restarts = CollectionProperty(type=bpy.types.PropertyGroup)
    meshes = CollectionProperty(type=bpy.types.PropertyGroup)
    scripts = CollectionProperty(type=bpy.types.PropertyGroup)
    
#----------------------------------------------------------------------------------
#- A list of base game assets, used to fill autocomplete lists in scenes,
#- when the base game path and target game are set
#----------------------------------------------------------------------------------
class THUGAssetListProps(bpy.types.PropertyGroup):
    models = CollectionProperty(type=bpy.types.PropertyGroup)
    skins = CollectionProperty(type=bpy.types.PropertyGroup)
    images = CollectionProperty(type=bpy.types.PropertyGroup)
    particle_textures = CollectionProperty(type=bpy.types.PropertyGroup)
    
#----------------------------------------------------------------------------------
#- Level obj properties! There's a lot of them!
#----------------------------------------------------------------------------------
class THUGLevelObjectProps(bpy.types.PropertyGroup):
    obj_type = StringProperty(name="Type", description="Type of level object.")
    obj_bouncy = BoolProperty(name="Bouncy", description="Enable collision physics on this object.")
    center_of_mass = FloatVectorProperty(name="Center Of Mass")
    contacts = CollectionProperty(type=THUGBouncyProps, name="Contacts")
    coeff_restitution = FloatProperty(name="coeff_restitution", min=0, max=1024, default=0.25)
    coeff_friction = FloatProperty(name="coeff_friction", min=0, max=1024, default=0.25)
    skater_collision_impulse_factor = FloatProperty(name="skater_collision_impulse_factor", min=0, max=1024, default=1.5)
    skater_collision_rotation_factor = FloatProperty(name="skater_collision_rotation_factor", min=0, max=1024, default=1)
    skater_collision_assent = IntProperty(name="skater_collision_assent", min=0, max=1024, default=0)
    skater_collision_radius = IntProperty(name="skater_collision_radius", min=0, max=1024, default=0)
    mass_over_moment = FloatProperty(name="mass_over_moment", min=-1, max=1024, default=-1, description="Use value of -1 to not export this property to the QB.")
    stuckscript = StringProperty(name="stuckscript")
    SoundType = StringProperty(name="Sound", description="Sound used when colliding with the object.")
    
#----------------------------------------------------------------------------------
#- Properties for waypoints curves (applies to all points)
#----------------------------------------------------------------------------------
class THUGWaypointProps(bpy.types.PropertyGroup):
    waypt_type = EnumProperty(items=(
        ("None", "None", ""), 
        ("PedAI", "Ped AI", "This path is used for pedestrian navigation."), 
        ("Accel", "Accel", "(THUG2+) Used for vehicle motion/acceleration."), 
        ("Default", "Default", "(THUG2+) Default waypoint, not needed for THUG1."), 
        ), 
    name="Waypoint Type", default="None", description="Type of waypoint. Use PedAI for detailed pedestrian movement and AI skaters.")
    
    PedType = EnumProperty(items=(
        ("Walk", "Walk", "Movement logic for pedestrians."), 
        ("Skate", "Skate", "Movement/trick logic for AI skaters."), 
        ), 
    name="PedType", default="Walk", description="The kind of navigation logic to use. 'Skate' is for AI skaters.")
    
#----------------------------------------------------------------------------------
#- Properties for individual nodes along a path (rail, ladder, waypoints)
#----------------------------------------------------------------------------------
class THUGPathNodeProps(bpy.types.PropertyGroup):
    name = StringProperty(name="Node Name")
    waypt_type = StringProperty(name="Type")
    script_name = StringProperty(name="TriggerScript Name")
    terrain = StringProperty(name="Terrain Type")
    spawnobjscript = StringProperty(name="SpawnObj Script")
    PedType = StringProperty(name="PedType")
    do_continue = BoolProperty(name="Continue")
    JumpToNextNode = BoolProperty(name="JumpToNextNode")
    Priority = StringProperty(name="Priority")
    ContinueWeight = FloatProperty(name="Continue Weight")
    SkateAction = StringProperty(name="Skate Action")
    JumpHeight = FloatProperty(name="Jump Height")
    skaterai_terrain = StringProperty(name="TerrainType")
    ManualType = StringProperty(name="ManualType")
    Deceleration = FloatProperty(name="Deceleration")
    StopTime = FloatProperty(name="StopTime")
    SpinAngle = FloatProperty(name="SpinAngle")
    RandomSpin = BoolProperty(name="Random Spin", default=False)
    SpineTransfer = BoolProperty(name="Spine Transfer", default=False)
    SpinDirection = StringProperty(name="SpinDirection")
#----------------------------------------------------------------------------------
#- Properties for individual nodes along a path (rail, ladder, waypoints)
#- These are shown to the user via the WindowManager, the separate ones above are
#- what is actually stored on the object
#----------------------------------------------------------------------------------
class THUGPathNodeUIProps(bpy.types.PropertyGroup):
    name = StringProperty(name="Node Name", update=update_pathnode)
    script_name = StringProperty(name="TriggerScript Name", update=update_pathnode)
    terrain = EnumProperty(
        name="Terrain Type",
        items=[(t, t, t) for t in ["None", "Auto"] + [tt for tt in TERRAIN_TYPES if tt.lower().startswith("grind")]], default="Auto", update=update_pathnode)
    spawnobjscript = StringProperty(name="SpawnObj Script", update=update_pathnode)
    PedType = StringProperty(name="Ped Type", update=update_pathnode)
    do_continue = BoolProperty(name="Continue", update=update_pathnode)
    JumpToNextNode = BoolProperty(name="Jump To Next Node", description="The AI skater will jump to the next point.", update=update_pathnode)
    Priority = EnumProperty(items=(
        ("Normal", "Normal", ""),
        ("Low", "Low", ""),
        ), 
    name="Priority", default="Normal", description="Used for branching paths (coming soon!)", update=update_pathnode)
    SkateAction = EnumProperty(items=(
        ("Continue", "Continue", ""),
        ("Grind", "Grind", ""),
        ("Vert_Grind", "Vert_Grind", ""),
        ("Grind_Off", "Grind_Off", ""),
        ("Flip_Trick", "Flip_Trick", ""),
        ("Vert_Flip", "Vert_Flip", ""),
        ("Grab_Trick", "Grab_Trick", ""),
        ("Vert_Grab", "Vert_Grab", ""),
        ("Vert_Lip", "Vert_Lip", ""),
        ("Vert_Land", "Vert_Land", ""),
        ("Jump", "Jump", ""),
        ("Vert_Jump", "Vert_Jump", ""),
        ("Roll_Off", "Roll_Off", ""),
        ("Manual", "Manual", ""),
        ("Manual_Down", "Manual_Down", ""),
        ("Stop", "Stop", ""),
        ), 
    name="Skate Action", default="Continue", description="The action taken by the AI skater when they reach this point.", update=update_pathnode)
    JumpHeight = FloatProperty(name="Jump Height", min=0, max=100000, description="How high the AI skater will jump.", update=update_pathnode)
    Deceleration = FloatProperty(name="Deceleration", update=update_pathnode)
    SpinAngle = FloatProperty(name="Spin Angle", min=0, max=10000, description="Rotation done by the AI skater.", update=update_pathnode)
    RandomSpin = BoolProperty(name="Random Spin", default=False, description="Use a random spin amount instead of the spin angle.", update=update_pathnode)
    SpineTransfer = BoolProperty(name="Spine Transfer", default=False, description="AI skater should do a spine transfer.", update=update_pathnode)
    SpinDirection = EnumProperty(items=(
        ("BS", "BS", ""),
        ("FS", "FS", ""),
        ("Rand", "Random", "Random direction."),
        ), 
    name="Spin Direction", default="Rand", description="Direction in which the AI skater spins.", update=update_pathnode)
        
#----------------------------------------------------------------------------------
#- Restart properties
#----------------------------------------------------------------------------------
class THUGRestartProps(bpy.types.PropertyGroup):
    restart_p1 = BoolProperty(name="Player 1", default=False)
    restart_p2 = BoolProperty(name="Player 2", default=False)
    restart_gen = BoolProperty(name="Generic", default=False)
    restart_multi = BoolProperty(name="Multiplayer", default=False)
    restart_team = BoolProperty(name="Team", default=False)
    restart_horse = BoolProperty(name="Horse", default=False)
    restart_ctf = BoolProperty(name="CTF", default=False)
    restart_type = EnumProperty(items=(
        ("Player1", "Player 1", ""),
        ("Player2", "Player 2", ""),
        ("Generic", "Generic", ""),
        ("Team", "Team", ""),
        ("Multiplayer", "Multiplayer", ""),
        ("Horse", "Horse", ""),
        ("CTF", "CTF", "")),
    name="Primary Type", default="Player1", update=thug_empty_update)
    restart_name = StringProperty(name="Restart Name", description="Name that appears in restart menu.")
    

#----------------------------------------------------------------------------------
#- Pedestrian properties
#----------------------------------------------------------------------------------
class THUGPedestrianProps(bpy.types.PropertyGroup):
    ped_type = StringProperty(name="Type", default="Ped_From_Profile")
    ped_source = EnumProperty(name="Source", items=(
        ( 'Profile', 'Profile', 'Pedestrian model is defined in a profile.'),
        ( 'Model', 'Model', 'Use an explicit path to the mdl file.')
    ), default="Profile", update=thug_empty_update)
    ped_profile = StringProperty(name="Profile", default="random_male_profile", description="Pedestrian profile name.")
    ped_skeleton = StringProperty(name="Skeleton", default="THPS5_human")
    ped_animset = StringProperty(name="Anim Set", default="animload_THPS5_human", description="Anim set to load for this pedestrian.")
    ped_extra_anims = StringProperty(name="Extra Anims", description="Additional anim sets to load.")
    ped_suspend = IntProperty(name="Suspend Distance", description="Distance at which the logic/motion pauses.", min=0, max=1000000, default=0)
    ped_model = StringProperty(name="Model", default="", description="Relative path to mdl file.", update=thug_empty_update)
    ped_nologic = BoolProperty(name="No Logic", default=False, description="Pedestrian will not have any logic, only animations.")
    
#----------------------------------------------------------------------------------
#- Vehicle properties
#----------------------------------------------------------------------------------
class THUGVehicleProps(bpy.types.PropertyGroup):
    veh_type = StringProperty(name="Type", default="Generic", description="Type of vehicle.")
    veh_model = StringProperty(name="Model", default="", description="Relative path to mdl file.", update=thug_empty_update)
    veh_skeleton = StringProperty(name="Skeleton", default="car", description="Name of skeleton.")
    veh_suspend = IntProperty(name="Suspend Distance", description="Distance at which the logic/motion pauses.", min=0, max=1000000, default=0)
    veh_norail = BoolProperty(name="No Rails", default=False, description="Vehicle will not have any rails (even if the model does).")
    veh_noskitch = BoolProperty(name="No Skitch", default=False, description="Vehicle cannot be skitched.")
    veh_usemodellights = BoolProperty(name="Use Model Lights", default=False)
    veh_allowreplacetex = BoolProperty(name="Texture Replacement", default=False, description="Allow model textures to be changed by scripts.")
    
def thug_light_update(self, context):
    if context.object.type == "LAMP":
        if self.light_type == 'POINT':
            context.object.data.type = "POINT"
            context.object.data.distance = self.light_radius[0]
        elif self.light_type == 'SPHERE':
            context.object.data.type = "POINT"
            context.object.data.distance = self.light_radius[0]
        elif self.light_type == 'TUBE':
            context.object.data.type = "POINT"
            context.object.data.distance = self.light_radius[0]
        elif self.light_type == 'AREA':
            context.object.data.type = "AREA"
            context.object.data.shape = "RECTANGLE"
            context.object.data.size = self.light_area[0]
            context.object.data.size_y = self.light_area[1]
        elif self.light_type == 'DISK':
            context.object.data.type = "AREA"
            context.object.data.shape = "SQUARE"
            context.object.data.size = self.light_radius[0]
        
    
#----------------------------------------------------------------------------------
#- Light properties
#----------------------------------------------------------------------------------
class THUGLightProps(bpy.types.PropertyGroup):
    light_type = EnumProperty(name="Source", items=(
        ( 'POINT', 'Point', 'Punctual light source'),
        ( 'SPHERE', 'Sphere', 'Spherical light source with a custom radius'),
        ( 'TUBE', 'Tube', 'Light which emits from a tube shape, with a custom size/radius'),
        ( 'AREA', 'Rectangle', 'Rectangular area light'),
        ( 'DISK', 'Disk', 'Disk area light')
    ), default="POINT", update=thug_light_update)
    light_end_pos = FloatVectorProperty(name="End", size=3, default=[0,256,0], description="End position for lamp")
    light_radius = FloatVectorProperty(name="Radius", size=2, min=0, max=128000, default=[300,300], description="Inner/outer radius", update=thug_light_update)
    light_area = FloatVectorProperty(name="Area", size=2, min=0, max=128000, default=[256,256], description="Width/height of area light", update=thug_light_update)
    light_excludeskater = BoolProperty(name="Exclude Skater", default=False, description="Light will not influence the skater")
    light_excludelevel = BoolProperty(name="Exclude Level", default=False, description="Light will not influence the scene")
    
#----------------------------------------------------------------------------------
#- Light properties
#----------------------------------------------------------------------------------
class THUGBillboardProps(bpy.types.PropertyGroup):
    is_billboard = BoolProperty(name="Billboard", default=False, description="This mesh is rendered as a billboard")
    type = EnumProperty(name="Type", items=(
        ( 'SCREEN', 'Screen', 'Billboard that always faces the screen'),
        ( 'AXIS', 'Axis-aligned', 'Billboard fixed around an axis')
    ), default="SCREEN")
    custom_pos = BoolProperty(name="Custom Position", default=False, description="Use a custom pivot position")
    pivot_origin = FloatVectorProperty(name="Pivot Origin", size=3, default=[0,0,0], description="Midpoint of the billboard")
    pivot_pos = FloatVectorProperty(name="Pivot Position", size=3, default=[0,0,0], description="Position the billboard pivots around (for axis-aligned billboards)")
    pivot_axis = FloatVectorProperty(name="Pivot Axis", size=3, default=[0,0,1], description="Axis the billboard pivots around (for axis-aligned billboards)")
    
#----------------------------------------------------------------------------------
#- Particle system properties! There's a lot of them!
#----------------------------------------------------------------------------------
class THUGParticleProps(bpy.types.PropertyGroup):
    particle_boxdimsstart = FloatVectorProperty(name="Box Dims Start", update=thug_empty_update)
    particle_boxdimsmid = FloatVectorProperty(name="Box Dims Mid", update=thug_empty_update)
    particle_boxdimsend = FloatVectorProperty(name="Box Dims End", update=thug_empty_update)
    particle_usestartpos = BoolProperty(name="Use Start Pos", default=False)
    particle_startposition = FloatVectorProperty(name="Start Position", update=thug_empty_update)
    particle_midposition = FloatVectorProperty(name="Mid Position", update=thug_empty_update)
    particle_endposition = FloatVectorProperty(name="End Position", update=thug_empty_update)
    
    particle_texture = StringProperty(name="Texture", description="Texture assigned to the particles.", update=thug_empty_update)
    particle_usemidpoint = BoolProperty(name="Use Midpoint", default=False)
    particle_profile = StringProperty(name="Profile", default="Default")
    particle_type = EnumProperty(name="Type", items=(
        ( 'NewFlat', 'NewFlat', ''),
        ( 'Line', 'Line', ''),
        ( 'Flat', 'Flat', ''),
        ( 'Shaded', 'Shaded', ''),
        ( 'Smooth', 'Smooth', ''),
        ( 'Glow', 'Glow', ''),
        ( 'Star', 'Star', ''),
        ( 'SmoothStar', 'SmoothStar', ''),
        ( 'Ribbon', 'Ribbon', ''),
        ( 'SmoothRibbon', 'SmoothRibbon', ''),
        ( 'RibbonTrail', 'RibbonTrail', ''),
        ( 'GlowRibbonTrail', 'GlowRibbonTrail', ''),
    ), default="NewFlat")
    
    particle_blendmode = EnumProperty(items=(
     ('Diffuse', 'Diffuse', ''),
     ('Blend', 'Blend', ''),
     ('Add', 'Add', ''),
     ('Subtract', 'Subtract', ''),
     ('Modulate', 'Modulate', ''),
     ('Brighten', 'Brighten', ''),
     ('FixBlend', 'Blend (Fixed Alpha)', ''),
     ('FixAdd', 'Add (Fixed Alpha)', ''),
     ('FixSubtract', 'Subtract (Fixed Alpha)', ''),
     ('FixModulate', 'Modulate (Fixed Alpha)', ''),
     ('FixBrighten', 'Brighten (Fixed Alpha)', ''),
    ), name="Blend Mode", default="Blend")
    particle_fixedalpha = IntProperty(name="Fixed Alpha", min=0, max=256, default=128)
    particle_alphacutoff = IntProperty(name="Alpha Cutoff", soft_min=0, max=256, default=-1)
    particle_maxstreams = IntProperty(name="Max Streams", soft_min=0, max=256, default=-1)
    particle_emitrate = FloatProperty(name="Emit Rate", soft_min=0, max=4096, default=-1)
    particle_lifetime = FloatProperty(name="Lifetime", soft_min=0, max=128000, default=-1)
    particle_midpointpct = IntProperty(name="Midpoint Pct", soft_min=0, max=100, default=-1)
    particle_radius = FloatVectorProperty(name="Radius", description="Start, mid and end radius.", default=(-1,-1,-1))
    particle_radiusspread = FloatVectorProperty(name="Radius Spread", default=(-1, -1, -1))
    particle_startcolor = FloatVectorProperty(name="Start Color",
                           subtype='COLOR',
                           default=(1.0, 1.0, 1.0, 1.0),
                           size=4,
                           min=0.0, max=1.0,
                           description="Start Color (with alpha).")
    particle_usecolormidtime = BoolProperty(name="Use Color Mid Time", default=False)
    particle_colormidtime = FloatProperty(name="Color Mid Time", min=0, max=128000, default=50)
    particle_midcolor = FloatVectorProperty(name="Mid Color",
                           subtype='COLOR',
                           default=(1.0, 1.0, 1.0, 1.0),
                           size=4,
                           min=0.0, max=1.0,
                           description="Mid Color (with alpha).")
    particle_endcolor = FloatVectorProperty(name="End Color",
                           subtype='COLOR',
                           default=(1.0, 1.0, 1.0, 1.0),
                           size=4,
                           min=0.0, max=1.0,
                           description="End Color (with alpha).")
    particle_suspend = IntProperty(name="Suspend Distance", description="Distance at which the system pauses.", min=0, max=1000000, default=0)
    
    # Even more particle properties that I missed the first time!
    #EmitSize = FloatVectorProperty(name="Emit Size", size=3, min=0, max=4096, default=16)
    EmitScript = StringProperty(name="Emit Script")
    Force = FloatVectorProperty(name="Emit Force", size=3, soft_min=0, soft_max=4096, default=(-1, -1, -1))
    Speed = FloatVectorProperty(name="Speed", size=2, soft_min=0, soft_max=4096, default=(-1, -1))
    Size = FloatVectorProperty(name="Emit Size", description="Width/height.", size=2, soft_min=0, soft_max=4096, default=(-1, -1))
    Width = FloatVectorProperty(name="Start/End Width", size=2, soft_min=0, soft_max=4096, default=(-1, -1))
    AngleSpread = FloatProperty(name="Angle Spread", soft_min=0, soft_max=4096, default=-1)
    UsePulseEmit = BoolProperty(name="UsePulseEmit", default=False)
    RandomEmitRate = BoolProperty(name="RandomEmitRate", default=False)
    RandomEmitDelay = BoolProperty(name="RandomEmitDelay", default=False)
    UseMidTime = BoolProperty(name="UseMidTime", default=False)
    MidTime = IntProperty(name="MidTime", default=-1)
    EmitTarget = FloatVectorProperty(name="Emit Target", size=3, default=(-1, -1, -1))
    EmitRate1 = FloatVectorProperty(name="Emit Rate 1", size=3, default=(-1, -1, -1))
    EmitRate1Delay = FloatVectorProperty(name="Emit Delay 1", size=3, default=(-1, -1, -1))
    EmitRate2 = FloatVectorProperty(name="Emit Rate 2", size=3, default=(-1, -1, -1))
    EmitRate2Delay = FloatVectorProperty(name="Emit Delay 2", size=3, default=(-1, -1, -1))
    
    
#----------------------------------------------------------------------------------
#- Properties for new 'Quick Export' option - same as the level export operators
#----------------------------------------------------------------------------------
class THUGLevelExportProps(bpy.types.PropertyGroup):

    def report(self, category, message):
        LOG.debug("OP: {}: {}".format(category, message))
        #super().report(category, message)
        
    # The following properties are unique to the quick export option
    use_quick_export = BoolProperty(name="Quick Export", description="When this option is enabled, the settings below will be used by default when exporting.", default=False)
    filename = StringProperty(name="Filename")
    directory = StringProperty(name="Export Path", description="Path the scene/model will be exported to when using the 'Quick Export' option. If exporting directly to a TH game, choose the 'Data' folder.", subtype='DIR_PATH')
    target_game = EnumProperty(name="Target Game", items=(
        ( 'THUG1', 'THUG1', 'THUG1/Underground+'),
        ( 'THUG2', 'THUG2', 'THUG2/THUG PRO'),
    ), default="THUG2")
    scene_type = EnumProperty(name="Scene Type", items=(
        ( 'Level', 'Level', 'Export this scene as a level.'),
        ( 'Model', 'Model', 'Export this scene as a model.'),
    ), default="Level")
    # These are the same as the normal export operators
    
    always_export_normals = BoolProperty(name="Export normals", default=False)
    use_vc_hack = BoolProperty(name="Vertex color hack",
        description = "Doubles intensity of vertex colours. Enable if working with an imported scene that appears too dark in game."
        , default=False)
    speed_hack = BoolProperty(name="No modifiers (speed hack)",
        description = "Don't apply any modifiers to objects. Much faster with large scenes, but all mesh must be triangles prior to export.", default=False)
    # AUTOSPLIT SETTINGS
    autosplit_everything = BoolProperty(name="Autosplit All",
        description = "Applies the autosplit setting to all objects in the scene, with default settings.", default=False)
    autosplit_faces_per_subobject = IntProperty(name="Faces Per Subobject",
        description="The max amount of faces for every created subobject.",
        default=800, min=50, max=6000)
    autosplit_max_radius = FloatProperty(name="Max Radius",
        description="The max radius of for every created subobject.",
        default=2000, min=100, max=5000)
    # /AUTOSPLIT SETTINGS
    pack_pre = BoolProperty(name="Pack files into .prx", default=True)
    is_park_editor = BoolProperty(name="Is Park Editor",
        description="Use this option when exporting a park editor dictionary.", default=False)
    generate_tex_file = BoolProperty(name="Generate a .tex file", default=True)
    generate_scn_file = BoolProperty(name="Generate a .scn file", default=True)
    generate_sky = BoolProperty(name="Generate skybox", default=True,description="Check to export a skybox with this scene.")
    generate_col_file = BoolProperty(name="Generate a .col file", default=True)
    generate_scripts_files = BoolProperty(name="Generate scripts", default=True)
    skybox_name = StringProperty(name="Skybox name", default="THUG_Sky")
    export_scale = FloatProperty(name="Export scale", default=1)
    mipmap_offset = IntProperty(
        name="Mipmap offset",
        description="Offsets generation of mipmaps (default is 0). For example, setting this to 1 will make the base texture 1/4 the size. Use when working with very large textures.",
        min=0, max=4, default=0)
    only_offset_lightmap = BoolProperty(name="Only Lightmaps", default=False, description="Mipmap offset only applies to lightmap textures.")

    # The following props are specific to models
    model_type = EnumProperty(items = (
        ("skin", ".skin", "Character skin, used for playable characters and pedestrians."),
        ("mdl", ".mdl", "Model used for vehicles and other static mesh."),
    ), name="Model Type", default="skin")
        
        
#----------------------------------------------------------------------------------
#- Properties for a TOD slot
#----------------------------------------------------------------------------------
class THUGTODProps(bpy.types.PropertyGroup):
    ambient_down_rgb = FloatVectorProperty(name="Ambient: Down Color",
                           subtype='COLOR',
                           default=(0.25, 0.25, 0.3),
                           size=3, min=0.0, max=1.0,
                           description="Light color used for faces which point down")
    ambient_up_rgb = FloatVectorProperty(name="Ambient: Up Color",
                           subtype='COLOR',
                           default=(0.6, 0.55, 0.5),
                           size=3, min=0.0, max=1.0,
                           description="Light color used for faces which point up")
    sun_headpitch = IntVectorProperty(name="Sun: Heading/Pitch", size=2, soft_min=0, soft_max=360, default=(0, 0))
    light1_headpitch = IntVectorProperty(name="Light 2: Heading/Pitch", size=2, soft_min=0, soft_max=360, default=(0, 0))
    sun_rgb = FloatVectorProperty(name="Sun: Diffuse Color",
                           subtype='COLOR',
                           default=(0.7, 0.65, 0.6),
                           size=3, min=0.0, max=1.0)
    light1_rgb = FloatVectorProperty(name="Light 2: Diffuse Color",
                           subtype='COLOR',
                           default=(0.7, 0.65, 0.6),
                           size=3, min=0.0, max=1.0)
    fog_startend = IntVectorProperty(name="Fog: Start/End", size=2, default=(0, 25000))
    fog_bottomtop = IntVectorProperty(name="Fog: Bottom/Top", size=2, default=(-5000, 5000), description="Start/end height for fog")
    fog_rgba = FloatVectorProperty(name="Fog: Color/Alpha",
                           subtype='COLOR',
                           default=(0.5, 0.5, 0.5, 0.25),
                           size=4,
                           min=0.0, max=1.0,
                           description="Fog color/alpha")
    
#----------------------------------------------------------------------------------
#- Properties for the entire level
#----------------------------------------------------------------------------------
class THUGLevelProps(bpy.types.PropertyGroup):
    level_name = StringProperty(name="Level Name", description="Name of your level, used for in-game menus")
    scene_name = StringProperty(name="Scene Name", description="Short name referenced by scripts")
    creator_name = StringProperty(name="Creator Name", description="Name of the person(s) who created this level")
    level_skybox = StringProperty(name="Skybox Name", description="Name of the skybox to be used with this level")
    
    export_props = PointerProperty(type=THUGLevelExportProps)
    
    # These properties are used in Underground+ 1.5
    tod_scale = FloatProperty(name="Default TOD", description="Default TOD range (0.0 = full day, 1.0 = full evening, 2.0 = full night, 3.0 = full morning)", default=0.0, min=0.0, max=4.0)
    tod_slot = EnumProperty(name="TOD Slot", items=(
        ( 'DAY', 'Day', ''),
        ( 'EVENING', 'Evening', ''),
        ( 'NIGHT', 'Night', ''),
        ( 'MORNING', 'Morning', ''),
    ), default="DAY", description="TOD slot to edit")
    
    
    tod_day = PointerProperty(type=THUGTODProps)
    tod_evening = PointerProperty(type=THUGTODProps)
    tod_night = PointerProperty(type=THUGTODProps)
    tod_morning = PointerProperty(type=THUGTODProps)
    
    # Legacy properties - used in the base games
    level_ambient_rgba = FloatVectorProperty(name="Ambient: Color/Mod",
                           subtype='COLOR',
                           default=(0.5, 0.5, 0.5, 0.25),
                           size=4,
                           min=0.0, max=1.0,
                           description="Light color, with alpha used as the mod value")
    level_light0_rgba = FloatVectorProperty(name="Light #1: Color/Mod",
                           subtype='COLOR',
                           default=(0.5, 0.5, 0.5, 0.25),
                           size=4,
                           min=0.0, max=1.0,
                           description="Light color, with alpha used as the mod value")
    level_light0_headpitch = FloatVectorProperty(name="Heading/Pitch", size=2, soft_min=0, soft_max=360, default=(0, 0))
    level_light1_rgba = FloatVectorProperty(name="Light #2: Color/Mod",
                           subtype='COLOR',
                           default=(0.5, 0.5, 0.5, 0.25),
                           size=4,
                           min=0.0, max=1.0,
                           description="Light color, with alpha used as the mod value")
    level_light1_headpitch = FloatVectorProperty(name="Heading/Pitch", size=2, soft_min=0, soft_max=360, default=(0, 0))
    
    level_flag_offline = BoolProperty(name="Offline Only", description="This level is not enabled for online play", default=False)
    level_flag_indoor = BoolProperty(name="Indoor", description="(THUG PRO only) This level is indoor", default=False)
    level_flag_nosun = BoolProperty(name="No Sun", description="(THUG PRO only) Don't display the dynamic sun in this level", default=False)
    level_flag_defaultsky = BoolProperty(name="Default Sky", description="(THUG PRO only) Use the default skybox", default=False)
    level_flag_wallridehack = BoolProperty(name="Wallride Hack", description="(THUG PRO only) Automatically makes all walls wallridable", default=False)
    level_flag_nobackfacehack = BoolProperty(name="No Backface Hack", description="(THUG PRO only)", default=False)
    level_flag_modelsinprx = BoolProperty(name="Models in scripts .prx", description="(THUG PRO only)", default=False)
    level_flag_nogoaleditor = BoolProperty(name="Disable goal editor", description="(THUG PRO only)", default=False)
    level_flag_nogoalattack = BoolProperty(name="Disable goal attack", description="(THUG PRO only)", default=False)
    level_flag_noprx = BoolProperty(name="Don't use prx files", description="(THUG PRO only) This level uses uncompressed files, not packed in .prx files", default=False)
    level_flag_biglevel = BoolProperty(name="Big Level", description="(THUG PRO only) Use extended online position broadcast limits", default=False)
    
# METHODS
#############################################
#----------------------------------------------------------------------------------
def __init_wm_props():
    def make_updater(flag):
        return lambda wm, ctx: update_collision_flag_mesh(wm, ctx, flag)

    FLAG_NAMES = {
        "mFD_VERT": ("Vert", "Vert. This face is a vert (used for ramps)."),
        "mFD_WALL_RIDABLE": ("Wallridable", "Wallridable. This face is wallridable"),
        "mFD_NON_COLLIDABLE": ("Non-Collidable", "Non-Collidable. The skater won't collide with this face. Used for triggers."),
        "mFD_NO_SKATER_SHADOW": ("No Skater Shadow", "No Skater Shadow"),
        "mFD_NO_SKATER_SHADOW_WALL": ("No Skater Shadow Wall", "No Skater Shadow Wall"),
        "mFD_TRIGGER": ("Trigger", "Trigger. The object's TriggerScript will be called when a skater goes through this face."),
        
        # Newly added flags!
        "mFD_SKATABLE": ( "Skatable", "Explicitly marks the surface skatable." ),
        "mFD_NOT_SKATABLE": ( "Not Skatable", "Collidable, but not skateable. Players can walk on this surface." ),
        "mFD_UNDER_OK": ( "Under OK", "Description goes here." ),
        "mFD_INVISIBLE": ( "Invisible", "Object won't be rendered." ),
        #"mFD_DECAL": ( "mFD_DECAL", "Description goes here." ),
        #"mFD_CAMERA_COLLIDABLE": ( "Camera Collidable", "Description goes here." ),
        #"mFD_SKATER_SHADOW": ( "mFD_SKATER_SHADOW", "Description goes here." ),
        #"mFD_CASFACEFLAGSEXIST": ( "mFD_CASFACEFLAGSEXIST", "Description goes here." ),
        #"mFD_PASS_1_DISABLED": ( "mFD_PASS_1_DISABLED", "Description goes here." ),
        #"mFD_PASS_2_ENABLED": ( "mFD_PASS_2_ENABLED", "Description goes here." ),
        #"mFD_PASS_3_ENABLED": ( "mFD_PASS_3_ENABLED", "Description goes here." ),
        #"mFD_PASS_4_ENABLED": ( "mFD_PASS_4_ENABLED", "Description goes here." ),
        #"mFD_RENDER_SEPARATE": ( "mFD_RENDER_SEPARATE", "Description goes here." ),
        #"mFD_LIGHTMAPPED": ( "mFD_LIGHTMAPPED", "Description goes here." ),
        #"mFD_NON_WALL_RIDABLE": ( "mFD_NON_WALL_RIDABLE", "Description goes here." ),
        #"mFD_NON_CAMERA_COLLIDABLE": ( "mFD_NON_CAMERA_COLLIDABLE", "Description goes here." ),
        #"mFD_EXPORT_COLLISION": ( "mFD_EXPORT_COLLISION", "Description goes here." )
    }

    for ff in SETTABLE_FACE_FLAGS:
        fns = FLAG_NAMES.get(ff)
        if fns:
            fn, fd = fns
        else:
            fn = ff
            fd = ff
        setattr(bpy.types.WindowManager,
                "thug_face_" + ff,
                BoolProperty(name=fn,
                             description=fd,
                             update=make_updater(ff)))

    bpy.types.WindowManager.thug_autorail_terrain_type = EnumProperty(
        name="Autorail Terrain Type",
        items=[(t, t, t) for t in ["None", "Auto"] + [tt for tt in TERRAIN_TYPES if tt.lower().startswith("grind")]],
        update=update_autorail_terrain_type)

    bpy.types.WindowManager.thug_face_terrain_type = EnumProperty(
        name="Terrain Type",
        items=[(t, t, t) for t in ["Auto"] + TERRAIN_TYPES],
        update=update_terrain_type_mesh)

    bpy.types.WindowManager.thug_show_face_collision_colors = BoolProperty(
        name="Colorize faces and edges",
        description="Colorize faces and edges in the 3D view according to their collision flags and autorail settings.",
        default=True)
#----------------------------------------------------------------------------------
def register_props():
    __init_wm_props()
    bpy.types.Object.thug_object_class = EnumProperty(
        name="Object Class",
        description="Object Class.",
        items=[
            ("LevelGeometry", "LevelGeometry", "LevelGeometry. Use for static geometry."),
            ("LevelObject", "LevelObject", "LevelObject. Use for dynamic objects.")],
        default="LevelGeometry")
    bpy.types.Object.thug_do_autosplit = BoolProperty(
        name="Autosplit Object on Export",
        description="Split object into multiple smaller objects of sizes suitable for the THUG engine. Note that this will create multiple objects, which might cause issues with scripting. Using this for LevelObjects or objects used in scripts is not advised.",
        default=False)
    bpy.types.Object.thug_node_expansion = StringProperty(
        name="Node Expansion",
        description="The struct with this name will be merged to this node's definition in the NodeArray.",
        default="")
    bpy.types.Object.thug_do_autosplit_faces_per_subobject = IntProperty(
        name="Faces Per Subobject",
        description="The max amount of faces for every created subobject.",
        default=800, min=50, max=6000)
    bpy.types.Object.thug_do_autosplit_max_radius = FloatProperty(
        name="Max Radius",
        description="The max radius of for every created subobject.",
        default=2000, min=100, max=5000)
    """
    bpy.types.Object.thug_do_autosplit_preserve_normals = BoolProperty(
        name="Preserve Normals",
        description="Preserve the normals of the ",
        default=True)
    """
    bpy.types.Object.thug_col_obj_flags = IntProperty()
    bpy.types.Object.thug_created_at_start = BoolProperty(name="Created At Start", default=True)
    bpy.types.Object.thug_network_option = EnumProperty(
        name="Network Options",
        items=[
            ("Default", "Default", "Appears in network games."),
            ("AbsentInNetGames", "Offline Only", "Only appears in single-player."),
            ("NetEnabled", "Online (Broadcast)", "Appears in network games, events/scripts appear on all clients.")],
        default="Default")
    bpy.types.Object.thug_export_collision = BoolProperty(name="Export to Collisions", default=True, description='This object will be exported to the collision (.col) file.')
    bpy.types.Object.thug_export_scene = BoolProperty(name="Export to Scene", default=True, description='This object will be exported to the scene (.scn) file.')
    bpy.types.Object.thug_always_export_to_nodearray = BoolProperty(name="Always Export to Nodearray", default=False)
    bpy.types.Object.thug_cast_shadow = BoolProperty(name="Cast Shadow", default=False, 
        description="(Underground+ 1.5+ only) If selected, this object will render dynamic shadows. Expensive effect - use carefully")
        
    #bpy.types.Object.thug_is_billboard = BoolProperty(name="Billboard", description="This mesh is rendered as a billboard", default=False)
    bpy.types.Object.thug_no_skater_shadow = BoolProperty(name="No Skater Shadow", description="Dynamic shadows will not render on this object.", default=False)
    bpy.types.Object.thug_is_shadow_volume = BoolProperty(name="Detail Mesh", default=False, description="(Underground+ 1.5+ only) This mesh is treated as extra detail, and will be culled based on distance from camera (or not rendered at all on lower graphics settings)")
    bpy.types.Object.thug_material_blend = BoolProperty(name="Mat Blend", default=False, description="The first two material slots attached to this mesh will be blended together using the vertex alpha channel")
    bpy.types.Object.thug_occluder = BoolProperty(name="Occluder", description="Occludes (hides) geometry behind this mesh. Used for performance improvements.", default=False)
    bpy.types.Object.thug_is_trickobject = BoolProperty(
        name="Is a TrickObject",
        default=False,
        description="This must be checked if you want this object to be taggable in Graffiti.")
    bpy.types.Object.thug_cluster_name = StringProperty(
        name="Cluster",
        description="The name of the graffiti group this object belongs to. If this is empty and this is a rail with a mesh object parent this will be set to the parent's name. Otherwise it will be set to this object's name.")
    bpy.types.Object.thug_path_type = EnumProperty(
        name="Path Type",
        items=[
            ("None", "None", "None"),
            ("Rail", "Rail", "Rail"),
            ("Ladder", "Ladder", "Ladder"),
            ("Waypoint", "Waypoint", "Navigation path for pedestrians/vehicles/AI skaters."),
            ("Custom", "Custom", "Custom")],
        default="None")
    bpy.types.Object.thug_rail_terrain_type = EnumProperty(
        name="Rail Terrain Type",
        items=[(t, t, t) for t in ["Auto"] + TERRAIN_TYPES],
        default="Auto")
    bpy.types.Object.thug_rail_connects_to = StringProperty(name="Linked To", description="Path this object links to (must be a rail/ladder/waypoint).")


    bpy.types.Object.thug_lightgroup = EnumProperty(
        name="Light Group",
        items=[
            ("None", "None", ""),
            ("Outdoor", "Outdoor", ""),
            ("NoLevelLights", "NoLevelLights", ""),
            ("Indoor", "Indoor", "")],
        default="None")
        
        
    bpy.types.Object.thug_levelobj_props = PointerProperty(type=THUGLevelObjectProps)
    bpy.types.Object.thug_triggerscript_props = PointerProperty(type=THUGObjectTriggerScriptProps)
    bpy.types.Object.thug_empty_props = PointerProperty(type=THUGEmptyProps)
    bpy.types.Object.thug_cubemap_props = PointerProperty(type=THUGCubemapProps)
    bpy.types.Object.thug_lightvolume_props = PointerProperty(type=THUGLightVolumeProps)
    bpy.types.Object.thug_proxim_props = PointerProperty(type=THUGProximNodeProps)
    bpy.types.Object.thug_emitter_props = PointerProperty(type=THUGEmitterProps)
    bpy.types.Object.thug_generic_props = PointerProperty(type=THUGGenericNodeProps)
    bpy.types.Object.thug_restart_props = PointerProperty(type=THUGRestartProps)
    bpy.types.Object.thug_go_props = PointerProperty(type=THUGGameObjectProps)
    bpy.types.Object.thug_ped_props = PointerProperty(type=THUGPedestrianProps)
    bpy.types.Object.thug_veh_props = PointerProperty(type=THUGVehicleProps)
    bpy.types.Object.thug_particle_props = PointerProperty(type=THUGParticleProps)
    
    bpy.types.Mesh.thug_billboard_props = PointerProperty(type=THUGBillboardProps)
    
    bpy.types.Lamp.thug_light_props = PointerProperty(type=THUGLightProps)
    
    bpy.types.Curve.thug_pathnode_triggers = CollectionProperty(type=THUGPathNodeProps)
    bpy.types.Object.thug_waypoint_props = PointerProperty(type=THUGWaypointProps)
    
    bpy.types.Image.thug_image_props = PointerProperty(type=THUGImageProps)

    bpy.types.Material.thug_material_props = PointerProperty(type=THUGMaterialProps)
    bpy.types.Texture.thug_material_pass_props = PointerProperty(type=THUGMaterialPassProps)

    bpy.types.WindowManager.thug_all_nodes = PointerProperty(type=THUGNodeListProps)
    bpy.types.WindowManager.thug_game_assets = PointerProperty(type=THUGAssetListProps)
    bpy.types.WindowManager.thug_all_rails = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.WindowManager.thug_all_restarts = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.WindowManager.thug_pathnode_props = PointerProperty(type=THUGPathNodeUIProps)

    bpy.types.Scene.thug_level_props = PointerProperty(type=THUGLevelProps)
    
    bake.register_props_bake()

    global draw_handle
    draw_handle = bpy.types.SpaceView3D.draw_handler_add(draw_stuff, (), 'WINDOW', 'POST_VIEW')
    # bpy.app.handlers.scene_update_pre.append(draw_stuff_pre_update)
    bpy.app.handlers.scene_update_post.append(draw_stuff_post_update)
    bpy.app.handlers.scene_update_post.append(update_collision_flag_ui_properties)
    bpy.app.handlers.scene_update_post.append(update_pathnode_ui_properties)

    bpy.app.handlers.load_pre.append(draw_stuff_pre_load_cleanup)
    bpy.app.handlers.load_post.append(update_node_collection)
    bpy.app.handlers.load_post.append(maybe_upgrade_scene)
    bpy.app.handlers.load_post.append(update_game_files_collections)
    
    
#----------------------------------------------------------------------------------
def unregister_props():
    bgl.glDeleteLists(draw_stuff_display_list_id, 1)

    global draw_handle
    if draw_handle:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handle, 'WINDOW')
        draw_handle = None

    """
    if draw_stuff_pre_update in bpy.app.handlers.scene_update_pre:
        bpy.app.handlers.scene_update_pre.remove(draw_stuff_pre_update)
    """

    if update_collision_flag_ui_properties in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(update_collision_flag_ui_properties)
    if draw_stuff_post_update in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(draw_stuff_post_update)
    if update_pathnode_ui_properties in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(update_pathnode_ui_properties)

    if draw_stuff_pre_load_cleanup in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(draw_stuff_pre_load_cleanup)
    if update_node_collection in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(update_node_collection)
    if maybe_upgrade_scene in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(maybe_upgrade_scene)
    if update_game_files_collections in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(update_game_files_collections)
