import bpy
import os
import struct
from bpy.props import *
import bgl
from pprint import pprint
from . import autorail, helpers
from . constants import *
from . autorail import *
from . helpers import *
from . import script_template
from mathutils import Vector

# PROPERTIES
#############################################
checksumLookupTable = {0x00000000: ''}


# METHODS
#############################################
def script_exists(name):
    return "script_" + name in bpy.data.texts 

def blub_int(integer):
    return "%i({},{:08})".format(integer, integer)
#----------------------------------------------------------------------------------
def blub_float(value):
    return "%f({})".format(value)
#----------------------------------------------------------------------------------
def blub_str(string):
    return "%s({},\"{}\")".format(len(string), string)
#----------------------------------------------------------------------------------
def _generate_script(_ob):
    script_props = _ob.thug_triggerscript_props
    tmpl = script_template.get_template(script_props.template_name_txt)
    
    script_name, script_code = script_template.generate_template_script(_ob, tmpl, 'Blub')
    
    return script_name, script_code

#----------------------------------------------------------------------------------
def get_custom_node_props():
    node_props_text = bpy.data.texts.get("THUG_NODES", None)
    if not node_props_text: return {}
    node_props = {}

    current_node_name = None
    for line in node_props_text.as_string().split('\n'):
        if line.startswith("#="):
            current_node_name = line[2:]
        else:
            node_props[current_node_name] = node_props.get(current_node_name, "") + line + '\n'
    return node_props
#----------------------------------------------------------------------------------
def get_custom_func_code():
    funcs_text = bpy.data.texts.get("THUG_FUNCS", None)
    if not funcs_text: return {}
    funcs_code = {}

    current_node_name = None
    for line in funcs_text.as_string().split('\n'):
        if line.startswith("#="):
            current_node_name = line[2:].lower()
        else:
            funcs_code[current_node_name] = funcs_code.get(current_node_name, "") + line + '\n'
    return funcs_code

#----------------------------------------------------------------------------------
#- Exports the node array to a .qb file!
#----------------------------------------------------------------------------------
def export_qb(filename, directory, target_game, operator=None):
    checksums = {}

    def v3(v):
        return "%vec3({:6f},{:6f},{:6f})".format(*v)
    def c(s):
        if s not in checksums:
            if is_hex_string(s):
                checksums[s] = int(s, 0)
            else:
                checksums[s] = crc_from_string(bytes(s, 'ascii'))
        return "$" + s + "$"
    i = blub_int
    f = blub_float
    _string = blub_str

    # List of scripts which are generated during export
    premade_scripts = [
        "TRG_CTF_BlueScript"
        ,"TRG_CTF_RedScript"
        ,"TRG_CTF_YellowScript"
        ,"TRG_CTF_GreenScript"
        ,"TRG_CTF_Blue_BaseScript"
        ,"TRG_CTF_Red_BaseScript"
        ,"TRG_CTF_Yellow_BaseScript"
        ,"TRG_CTF_Green_BaseScript"
        ,"TRG_Flag_BlueScript"
        ,"TRG_Flag_RedScript"
        ,"TRG_Flag_YellowScript"
        ,"TRG_Flag_GreenScript"
        ,"TRG_Flag_Blue_BaseScript"
        ,"TRG_Flag_Red_BaseScript"
        ,"TRG_Flag_Yellow_BaseScript"
        ,"TRG_Flag_Green_BaseScript"
    ]
    
    # Step 0: go through all objects and ensure that any TriggerScripts referenced actually exist
    # (this can happen with imported scenes)
    for ob in bpy.data.objects:
        # If a custom script is referenced on the whole object, create it if it doesn't actually exist
        if hasattr(ob, 'thug_triggerscript_props') and ob.thug_triggerscript_props.template_name_txt == "Custom" and ob.thug_triggerscript_props.custom_name != "": 
            # Don't bother creating an empty script if it's going to be generated during export
            if ob.thug_triggerscript_props.custom_name not in premade_scripts:
                get_triggerscript(ob.thug_triggerscript_props.custom_name)
            
        # Handle individual point script references on paths
        if ob.type == "CURVE" and ob.thug_path_type in ("Rail", "Ladder", "Waypoint"): 
            for spline in ob.data.splines:
                points = spline.points
                p_num = -1
                for point in points:
                    p_num += 1
                    if len(ob.data.thug_pathnode_triggers) > p_num:
                        if ob.data.thug_pathnode_triggers[p_num].script_name != "":
                            get_triggerscript(ob.data.thug_pathnode_triggers[p_num].script_name)
                        if ob.data.thug_pathnode_triggers[p_num].spawnobjscript != "":
                            get_triggerscript(ob.data.thug_pathnode_triggers[p_num].spawnobjscript)
                    
    generated_scripts = {}
    custom_triggerscript_names = []
    custom_node_props = get_custom_node_props()
    custom_func_code = get_custom_func_code()

    with open(os.path.join(directory, filename + ".txt"), "w") as outp:
        from io import StringIO
        string_output = StringIO()
        p = lambda *args, **kwargs: print(*args, **kwargs, file=string_output)
        p("%include \"qb_table.qbi\"")

        # Dump all TriggerScript text blocks here!
        all_triggerscripts = [s for s in bpy.data.texts if s.name.startswith("script_")]
        for ts in all_triggerscripts:
            p(":i function $" + ts.name[7:] + "$")
            if target_game != "THUG2":
                # Make sure we don't export the THUG2 if/else conditions!
                p(ts.as_string().replace(":i if", ":i doIf").replace(":i else", ":i doElse"))
            else:
                p(ts.as_string())
            p(":i endfunction")
            p("")
        p("")
        p("#/ custom script code end")
        p("")
        
        # Start listing the actual NodeArray...
        if target_game == "THUG2":
            p("$" + filename + "_NodeArray$ =")
        else:
            p("$NodeArray$ =")
        p(":i :a{")

        print("Exporting level QB...")
        
        rail_custom_triggerscript_names, rail_generated_scripts, rail_node_offsets = autorail._export_rails(p, c, operator)
        custom_triggerscript_names += rail_custom_triggerscript_names
        generated_scripts.update(rail_generated_scripts)
            
        # Used further down to determine if we need to auto-generate nodes of certain types
        has_restart_p1 = False
        has_restart_p2 = False
        has_restart_multi = False
        has_restart_gen = False
        has_restart_ctf = False
        has_restart_team = False
        has_restart_horse = False
        has_koth = False
        has_ctf_base_red = False
        has_ctf_base_yellow = False
        has_ctf_base_green = False
        has_ctf_base_blue = False
        has_ctf_red = False
        has_ctf_yellow = False
        has_ctf_green = False
        has_ctf_blue = False
        has_team_red = False
        has_team_yellow = False
        has_team_green = False
        has_team_blue = False
        has_team_red_base = False
        has_team_yellow_base = False
        has_team_green_base = False
        has_team_blue_base = False
        
        
        for ob in bpy.data.objects:
            # -----------------------------------------------------------------------------------------------------------
            # - Export node definitions for mesh-based objects (level geometry, level object)
            # -----------------------------------------------------------------------------------------------------------
            if ob.type == "MESH" and not ob.get("thug_autosplit_object_no_export_hack"):
                if ob.name.endswith("_SCN") and bpy.data.objects.get(ob.name[:-4]):
                    #print("Skipping scene mesh " + ob.name + ". It has a collision mesh we will work from")
                    continue
                if ob.name.endswith("_COL"):
                    print("Special collision mesh: " + ob.name + ". It is not meant to be exported to the QB. Skipping...")
                    continue
                col_ob = ob # Collision object may have different properties than the scene object (Triggers, etc)
                if bpy.data.objects.get(ob.name + "_SCN"):
                    #print("Mesh " + ob.name + " also has a scene mesh. Using its properties instead!")
                    ob = bpy.data.objects.get(ob.name + "_SCN")
                    
                is_levelobject = col_ob.thug_object_class == "LevelObject"
                clean_name = get_clean_name(ob)
                
                if not ob.thug_always_export_to_nodearray and \
                    not operator.is_park_editor and \
                    not is_levelobject and \
                    col_ob.thug_created_at_start and \
                    not custom_node_props.get(clean_name) and \
                    col_ob.thug_occluder == False and \
                    ob.thug_lightgroup == "None" and \
                    not ob.name.lower().startswith("NightOn") and \
                    not ob.name.lower().startswith("NightOff") :
                    if (not getattr(ob, "thug_is_trickobject", False) and
                            (col_ob.thug_triggerscript_props.template_name_txt == "None" or \
                            col_ob.thug_triggerscript_props.template_name_txt == "")) or not \
                        (getattr(ob, "thug_export_collision", True) or
                         getattr(ob, "thug_export_scene", True)):
                        continue
                    
                print("Exporting node definition for " + ob.name + " (" + clean_name + ")...")
                if is_hex_string(clean_name):
                    print("Error: Object name must not be a checksum when exporting to the level QB.")
                    raise Exception("Object {} does not have a proper name. Please assign one before exporting to a level QB.".format(clean_name))
                    
                p("\t:i :s{")
                if ob.parent:
                    p("\t\t:i {} = {}".format(c("Pos"), v3(to_thug_coords(ob.parent.location + ob.location)))) # v3(get_sphere(ob))))
                else:
                    p("\t\t:i {} = {}".format(c("Pos"), v3(to_thug_coords(ob.location)))) # v3(get_sphere(ob))))
                if is_levelobject:
                    p("\t\t:i {} = {}".format(c("Angles"), v3(to_thug_coords_ns(ob.rotation_euler))))
                else:
                    p("\t\t:i {} = {}".format(c("Angles"), v3((0, 0, 0))))
                    
                p("\t\t:i {} = {}".format(c("Name"), c(clean_name)))
                p("\t\t:i {} = {}".format(c("Class"), c("LevelGeometry") if not is_levelobject else c("LevelObject")))
                # Exporting LevelObject specific properties below
                if is_levelobject:
                    if col_ob.thug_levelobj_props.obj_type != '':
                        p("\t\t:i {} = {}".format(c("Type"), c(col_ob.thug_levelobj_props.obj_type)))
                    else:
                        p("\t\t:i {} = {}".format(c("Type"), c("Normal")))
                    if col_ob.thug_levelobj_props.obj_bouncy:
                        # Bouncy Object properties go here!
                        p("\t\t:i {}".format(c("Bouncy")))
                        #p("\t\t:i {} = :a{{ ".format(c("contacts")))
                        _ctnum = 0
                        _prop = "\t\t:i {} = :a{{ "
                        # Imported scenes will have contacts defined directly in custom props
                        if len(col_ob.thug_levelobj_props.contacts) > 0:
                            for _contact in col_ob.thug_levelobj_props.contacts:
                                _ctnum += 1
                                if _ctnum > 1:
                                    _prop += ";"
                                firstc = False
                                _prop += v3(_contact.contact)
                        # For other scenes, we need to get the verts from the object data
                        else:
                            for _contact in get_vertices_thug(col_ob):
                                _ctnum += 1
                                if _ctnum > 1:
                                    _prop += ";"
                                firstc = False
                                _prop += v3(_contact)
                        _prop += ":a}}"
                        p(_prop.format(c("contacts")))
                        #p(":a}}")
                        p("\t\t:i {} = {}".format(c("center_of_mass"), v3(col_ob.thug_levelobj_props.center_of_mass)))
                        p("\t\t:i {} = {}".format(c("coeff_restitution"), f(col_ob.thug_levelobj_props.coeff_restitution)))
                        p("\t\t:i {} = {}".format(c("coeff_friction"), f(col_ob.thug_levelobj_props.coeff_friction)))
                        p("\t\t:i {} = {}".format(c("skater_collision_impulse_factor"), f(col_ob.thug_levelobj_props.skater_collision_impulse_factor)))
                        p("\t\t:i {} = {}".format(c("skater_collision_rotation_factor"), f(col_ob.thug_levelobj_props.skater_collision_rotation_factor)))
                        p("\t\t:i {} = {}".format(c("skater_collision_assent"), i(col_ob.thug_levelobj_props.skater_collision_assent)))
                        p("\t\t:i {} = {}".format(c("skater_collision_radius"), i(col_ob.thug_levelobj_props.skater_collision_radius)))
                        if col_ob.thug_levelobj_props.mass_over_moment >= 0:
                            p("\t\t:i {} = {}".format(c("mass_over_moment"), f(col_ob.thug_levelobj_props.mass_over_moment)))
                        if col_ob.thug_levelobj_props.stuckscript != "":
                            p("\t\t:i {} = {}".format(c("stuckscript"), c(col_ob.thug_levelobj_props.stuckscript)))
                        if col_ob.thug_levelobj_props.SoundType != "":
                            p("\t\t:i {} = {}".format(c("SoundType"), c(col_ob.thug_levelobj_props.SoundType)))
                    # Only export Links on LevelObjects                    
                    if col_ob.thug_rail_connects_to:
                        if col_ob.thug_rail_connects_to not in bpy.data.objects:
                            operator.report({"ERROR"}, "Object {} connects to nonexistent path {}".format(col_ob.name, col_ob.thug_rail_connects_to))
                        else:
                            connected_to = bpy.data.objects[col_ob.thug_rail_connects_to]
                            if connected_to.name in rail_node_offsets:
                                p("\t\t:i {} = :a{{{}:a}}".format(
                                    c("Links"),
                                i(rail_node_offsets[connected_to.name])))
    
                if col_ob.thug_occluder:
                    p("\t\t:i {}".format(c("Occluder")))
                if col_ob.thug_created_at_start:
                    p("\t\t:i {}".format(c("CreatedAtStart")))
                if col_ob.thug_network_option != "Default":
                    p("\t\t:i {}".format(c(col_ob.thug_network_option)))
                    if col_ob.thug_network_option == "NetEnabled":
                        p("\t\t:i {}".format(c("Permanent")))
                if ob.thug_lightgroup != "None" and ob.thug_export_scene:
                    p("\t\t:i {} = {}".format(c("LightGroup"), c(ob.thug_lightgroup)))
                    
                if getattr(col_ob, "thug_is_trickobject", False):
                    p("\t\t:i call {} arguments".format(c("TrickObject")))
                    p("\t\t\t{} = {}".format(c("Cluster"),
                                             c(col_ob.thug_cluster_name if col_ob.thug_cluster_name else clean_name)))
                # Fallback in case someone is setting TrickObject props on the scene mesh instead of the collision
                elif getattr(ob, "thug_is_trickobject", False):
                    p("\t\t:i call {} arguments".format(c("TrickObject")))
                    p("\t\t\t{} = {}".format(c("Cluster"),
                                             c(ob.thug_cluster_name if ob.thug_cluster_name else clean_name)))
                p("\t\t:i {} = {}".format(c("CollisionMode"), c("Geometry")))

                if col_ob.thug_triggerscript_props.template_name_txt != "" and col_ob.thug_triggerscript_props.template_name_txt != "None":
                    if col_ob.thug_triggerscript_props.template_name_txt == "Custom":
                        script_name = col_ob.thug_triggerscript_props.custom_name
                        custom_triggerscript_names.append(script_name)
                    else:
                        script_name, script_code = _generate_script(col_ob)
                        generated_scripts.setdefault(script_name, script_code)
                    if script_name != "":
                        p("\t\t:i {} = {}".format(c("TriggerScript"), c(script_name)))
                    else:
                        operator.report({'WARNING'}, "Unable to determine a TriggerScript for object {}.".format(col_ob.name))

                if col_ob.thug_node_expansion:
                    p("\t\t:i {}".format(c(col_ob.thug_node_expansion)))

            # -----------------------------------------------------------------------------------------------------------
            # - Export node definitions for lamps (LevelLights)!
            # -----------------------------------------------------------------------------------------------------------
            elif ob.type == "LAMP" and ob.data.type == "POINT":
                clean_name = get_clean_name(ob)
                    
                p("\t:i :s{")
                p("\t\t:i {} = {}".format(c("Pos"), v3(to_thug_coords(ob.location))))
                p("\t\t:i {} = {}".format(c("Angles"), v3(to_thug_coords_ns(ob.rotation_euler))))
                p("\t\t:i {} = {}".format(c("Name"), c(clean_name)))
                p("\t\t:i {} = {}".format(c("Class"), c("LevelLight")))
                if ob.thug_created_at_start:
                    p("\t\t:i {}".format(c("CreatedAtStart")))
                if ob.thug_network_option != "Default":
                    p("\t\t:i {}".format(c(ob.thug_network_option)))
                    if ob.thug_network_option == "NetEnabled":
                        p("\t\t:i {}".format(c("Permanent")))
                p("\t\t:i {} = {}".format(c("Brightness"), i(int(ob.data.energy))))
                p("\t\t:i {} = {}".format(c("InnerRadius"), i(int(ob.data.thug_light_props.light_radius[0]))))
                p("\t\t:i {} = {}".format(c("OuterRadius"), i(int(ob.data.thug_light_props.light_radius[1]))))
                if ob.data.thug_light_props.light_excludeskater:
                    p("\t\t:i {}".format(c("ExcludeSkater")))
                if ob.data.thug_light_props.light_excludelevel:
                    p("\t\t:i {}".format(c("ExcludeLevel")))
                light_color = [ int((ob.data.color[0] * 255) / 1), 
                                int((ob.data.color[1] * 255) / 1) , 
                                int((ob.data.color[2] * 255) / 1)]
                p("\t\t:i {} = :a{{ {};{};{} :a}}".format(c("Color"),
                            i(light_color[0]), i(light_color[1]),i(light_color[2])))
                if ob.thug_node_expansion:
                    p("\t\t:i {}".format(c(ob.thug_node_expansion)))
                #p("\t:i :s}")
                
            # -----------------------------------------------------------------------------------------------------------
            # - Export node definitions for empties 
            # -----------------------------------------------------------------------------------------------------------
            elif ob.type == "EMPTY" and ob.thug_empty_props.empty_type != "" and ob.thug_empty_props.empty_type != "None":
                if ob.thug_empty_props.empty_type == "BouncyObject":
                    continue
                    
                clean_name = get_clean_name(ob)
                    
                if ob.thug_empty_props.empty_type == "GameObject":
                    # Need special logic for exporting CTF nodes, as they use a specific naming convention that
                    # must be followed for everything to work correctly - we should also check for duplicate flags
                    # and alert in the case we find any, as that can cause unexpected behavior
                    if ob.thug_go_props.go_type == "Flag_Blue":
                        if has_ctf_blue:
                            print("Duplicate CTF Flag_Blue found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_CTF_Blue"
                        has_ctf_blue = True
                    elif ob.thug_go_props.go_type == "Flag_Blue_Base":
                        if has_ctf_base_blue:
                            print("Duplicate CTF Flag_Blue_Base found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_CTF_Blue_Base"
                        has_ctf_base_blue = True
                    elif ob.thug_go_props.go_type == "Team_Blue":
                        if has_team_blue:
                            print("Duplicate CTF Team_Blue found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_Flag_Blue"
                        has_team_blue = True
                    elif ob.thug_go_props.go_type == "Team_Blue_Base":
                        if has_team_blue_base:
                            print("Duplicate CTF Team_Blue_Base found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_Flag_Blue_Base"
                        has_team_blue_base = True
                        
                    elif ob.thug_go_props.go_type == "Flag_Red":
                        if has_ctf_red:
                            print("Duplicate CTF Flag_Red found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_CTF_Red"
                        has_ctf_red = True
                    elif ob.thug_go_props.go_type == "Flag_Red_Base":
                        if has_ctf_base_red:
                            print("Duplicate CTF Flag_Red_Base found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_CTF_Red_Base"
                        has_ctf_base_red = True
                    elif ob.thug_go_props.go_type == "Team_Red":
                        if has_team_red:
                            print("Duplicate CTF Team_Red found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_Flag_Red"
                        has_team_red = True
                    elif ob.thug_go_props.go_type == "Team_Red_Base":
                        if has_team_red_base:
                            print("Duplicate CTF Team_Red_Base found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_Flag_Red_Base"
                        has_team_red_base = True
                        
                    elif ob.thug_go_props.go_type == "Flag_Green":
                        if has_ctf_green:
                            print("Duplicate CTF Flag_Green found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_CTF_Green"
                        has_ctf_green = True
                    elif ob.thug_go_props.go_type == "Flag_Green_Base":
                        if has_ctf_base_green:
                            print("Duplicate CTF Flag_Green_Base found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_CTF_Green_Base"
                        has_ctf_base_green = True
                    elif ob.thug_go_props.go_type == "Team_Green":
                        if has_team_green:
                            print("Duplicate CTF Team_Green found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_Flag_Green"
                        has_team_green = True
                    elif ob.thug_go_props.go_type == "Team_Green_Base":
                        if has_team_green_base:
                            print("Duplicate CTF Team_Green_Base found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_Flag_Green_Base"
                        has_team_green_base = True
                        
                    elif ob.thug_go_props.go_type == "Flag_Yellow":
                        if has_ctf_yellow:
                            print("Duplicate CTF Flag_Yellow found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_CTF_Yellow"
                        has_ctf_yellow = True
                    elif ob.thug_go_props.go_type == "Flag_Yellow_Base":
                        if has_ctf_base_yellow:
                            print("Duplicate CTF Flag_Yellow_Base found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_CTF_Yellow_Base"
                        has_ctf_base_yellow = True
                    elif ob.thug_go_props.go_type == "Team_Yellow":
                        if has_team_yellow:
                            print("Duplicate CTF Team_Yellow found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_Flag_Yellow"
                        has_team_yellow = True
                    elif ob.thug_go_props.go_type == "Team_Yellow_Base":
                        if has_team_yellow_base:
                            print("Duplicate CTF Team_Yellow_Base found. Skipping {}...".format(ob.name))
                            continue
                        clean_name = "TRG_Flag_Yellow_Base"
                        has_team_yellow_base = True
                
                p("\t:i :s{")
                p("\t\t:i {} = {}".format(c("Pos"), v3(to_thug_coords(ob.location))))
                p("\t\t:i {} = {}".format(c("Angles"), v3(to_thug_coords_ns(ob.rotation_euler))))
                p("\t\t:i {} = {}".format(c("Name"), c(clean_name)))
                # RESTART NODE
                if ob.thug_empty_props.empty_type == "Restart":
                    p("\t\t:i {} = {}".format(c("Class"), c("Restart")))
                    p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_restart_props.restart_type)))
                    auto_restart_name = ""
                    str_all_types = ":a{"
                    if ob.thug_restart_props.restart_p1:
                        has_restart_p1 = True
                        str_all_types += c("Player1")
                        if auto_restart_name == "": auto_restart_name = "P1: Restart"
                    if ob.thug_restart_props.restart_p2:
                        has_restart_p2 = True
                        str_all_types += c("Player2")
                        if auto_restart_name == "": auto_restart_name = "P2: Restart"
                    if ob.thug_restart_props.restart_gen:
                        has_restart_gen = True
                        str_all_types += c("Generic")
                        if auto_restart_name == "": auto_restart_name = "Gen: Restart"
                    if ob.thug_restart_props.restart_multi:
                        has_restart_multi = True
                        str_all_types += c("Multiplayer")
                        if auto_restart_name == "": auto_restart_name = "Multi: Restart"
                    if ob.thug_restart_props.restart_team:
                        has_restart_team = True
                        str_all_types += c("Team")
                        if auto_restart_name == "": auto_restart_name = "Team: Restart"
                    if ob.thug_restart_props.restart_horse:
                        has_restart_horse = True
                        str_all_types += c("Horse")
                        if auto_restart_name == "": auto_restart_name = "Horse: Restart"
                    if ob.thug_restart_props.restart_ctf:
                        has_restart_ctf = True
                        str_all_types += c("CTF")
                        if auto_restart_name == "": auto_restart_name = "CTF: Restart"
                    
                    if auto_restart_name == "":
                        # If none of the type boxes were checked off, use the primary type!
                        #raise Exception("Restart node {} has no restart type(s).".format(ob.name))
                        if ob.thug_restart_props.restart_type == "Player1":
                            str_all_types += c("Player1")
                            auto_restart_name = "P1: Restart"
                            has_restart_p1 = True
                        elif ob.thug_restart_props.restart_type == "Player2":
                            str_all_types += c("Player2")
                            auto_restart_name = "P2: Restart"
                            has_restart_p2 = True
                        if ob.thug_restart_props.restart_type == "Generic":
                            str_all_types += c("Generic")
                            auto_restart_name = "Gen: Restart"
                            has_restart_gen = True
                        if ob.thug_restart_props.restart_type == "Multiplayer":
                            str_all_types += c("Multiplayer")
                            auto_restart_name = "Multi: Restart"
                            has_restart_multi = True
                        if ob.thug_restart_props.restart_type == "Team":
                            str_all_types += c("Team")
                            auto_restart_name = "Team: Restart"
                            has_restart_team = True
                        if ob.thug_restart_props.restart_type == "Horse":
                            str_all_types += c("Horse")
                            auto_restart_name = "Ho: Restart"
                            has_restart_horse = True
                        if ob.thug_restart_props.restart_type == "CTF":
                            str_all_types += c("CTF")
                            auto_restart_name = "CTF: Restart"
                            has_restart_ctf = True
                    str_all_types += ":a}"
                    p("\t\t:i {} = {}".format(c("restart_types"), str_all_types))
                    actual_restart_name = ob.thug_restart_props.restart_name
                    if ob.thug_restart_props.restart_name == "":
                        actual_restart_name = auto_restart_name
                    p("\t\t:i {} = {}".format(c("RestartName"), blub_str(actual_restart_name)))
                    
                # PROXIMITY NODE
                elif ob.thug_empty_props.empty_type == "ProximNode":
                    p("\t\t:i {} = {}".format(c("Class"), c("ProximNode")))
                    p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_proxim_props.proxim_type)))
                    if ob.thug_proxim_props.proxim_object == True:
                        p("\t\t:i {}".format(c("ProximObject")))
                    if ob.thug_proxim_props.proxim_rendertoviewport == True:
                        p("\t\t:i {}".format(c("RenderToViewport")))
                    if ob.thug_proxim_props.proxim_selectrenderonly == True:
                        p("\t\t:i {}".format(c("SelectRenderOnly")))
                    p("\t\t:i {} = {}".format(c("Shape"), c(ob.thug_proxim_props.proxim_shape)))
                    p("\t\t:i {} = {}".format(c("Radius"), i(ob.thug_proxim_props.proxim_radius)))
                    
                # EMITTER OBJECT NODE
                elif ob.thug_empty_props.empty_type == "EmitterObject":
                    p("\t\t:i {} = {}".format(c("Class"), c("EmitterObject")))
                    p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_emitter_props.emit_type)))
                    if ob.thug_emitter_props.emit_radius > 0:
                        p("\t\t:i {} = {}".format(c("radius"), f(ob.thug_emitter_props.emit_radius)))
                        
                # PARTICLE OBJECT NODE
                elif ob.thug_empty_props.empty_type == "ParticleObject":
                    p("\t\t:i {} = {}".format(c("Class"), c("ParticleObject")))
                    #p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_particle_props.particle_profile)))
                    p("\t\t:i {} = {}".format(c("SuspendDistance"), i(ob.thug_particle_props.particle_suspend)))
                    p("\t\t:i {} = {}".format(c("lod_dist1"), i(1024)))
                    p("\t\t:i {} = {}".format(c("lod_dist2"), i(2048)))
                    p("\t\t:i {} = {}".format(c("BoxDimsStart"), v3(to_thug_coords_scalar(ob.thug_particle_props.particle_boxdimsstart))))
                    p("\t\t:i {} = {}".format(c("BoxDimsMid"), v3(to_thug_coords_scalar(ob.thug_particle_props.particle_boxdimsmid))))
                    p("\t\t:i {} = {}".format(c("BoxDimsEnd"), v3(to_thug_coords_scalar(ob.thug_particle_props.particle_boxdimsend))))
                    # Always use local space!
                    p("\t\t:i {}".format(c("LocalSpace")))
                    #if ob.thug_particle_props.particle_usestartpos == True:
                    p("\t\t:i {}".format(c("UseStartPosition")))
                    p("\t\t:i {} = {}".format(c("StartPosition"), v3(to_thug_coords_scalar(ob.thug_particle_props.particle_startposition))))
                    p("\t\t:i {} = {}".format(c("MidPosition"), v3(to_thug_coords_scalar(ob.thug_particle_props.particle_midposition))))
                    p("\t\t:i {} = {}".format(c("EndPosition"), v3(to_thug_coords_scalar(ob.thug_particle_props.particle_endposition))))
                    p("\t\t:i {} = {}".format(c("Texture"), c(ob.thug_particle_props.particle_texture)))
                    if ob.thug_particle_props.particle_usemidpoint == True:
                        p("\t\t:i {}".format(c("UseMidPoint")))
                    if ob.thug_particle_props.particle_midpointpct >= 0:
                        p("\t\t:i {} = {}".format(c("MidPointPCT"), i(ob.thug_particle_props.particle_midpointpct)))
                    p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_particle_props.particle_type)))
                    p("\t\t:i {} = {}".format(c("BlendMode"), c(ob.thug_particle_props.particle_blendmode)))
                    p("\t\t:i {} = {}".format(c("FixedAlpha"), i(ob.thug_particle_props.particle_fixedalpha)))
                    if ob.thug_particle_props.particle_alphacutoff >= 0:
                        p("\t\t:i {} = {}".format(c("AlphaCutoff"), i(ob.thug_particle_props.particle_alphacutoff)))
                    p("\t\t:i {} = {}".format(c("MaxStreams"), i(ob.thug_particle_props.particle_maxstreams)))
                    p("\t\t:i {} = {}".format(c("EmitRate"), f(ob.thug_particle_props.particle_emitrate)))
                    if ob.thug_particle_props.particle_radius[0] >= 0:
                        p("\t\t:i {} = {}".format(c("StartRadius"), f(ob.thug_particle_props.particle_radius[0])))
                    if ob.thug_particle_props.particle_radius[1] >= 0:
                        p("\t\t:i {} = {}".format(c("MidRadius"), f(ob.thug_particle_props.particle_radius[1])))
                    if ob.thug_particle_props.particle_radius[2] >= 0:
                        p("\t\t:i {} = {}".format(c("EndRadius"), f(ob.thug_particle_props.particle_radius[2])))
                    if ob.thug_particle_props.particle_radiusspread[0] >= 0:
                        p("\t\t:i {} = {}".format(c("StartRadiusSpread"), f(ob.thug_particle_props.particle_radiusspread[0])))
                    if ob.thug_particle_props.particle_radiusspread[1] >= 0:
                        p("\t\t:i {} = {}".format(c("MidRadiusSpread"), f(ob.thug_particle_props.particle_radiusspread[1])))
                    if ob.thug_particle_props.particle_radiusspread[2] >= 0:
                        p("\t\t:i {} = {}".format(c("EndRadiusSpread"), f(ob.thug_particle_props.particle_radiusspread[2])))
                    
                    if ob.thug_particle_props.EmitScript != "":
                        p("\t\t:i " + c("EmitScript") + " = :a{ " + c(ob.thug_particle_props.EmitScript) + " :a}")
                    if ob.thug_particle_props.Force[0] >= 0:
                        p("\t\t:i {} = {}".format(c("Force_X"), f(ob.thug_particle_props.Force[0])))
                        p("\t\t:i {} = {}".format(c("Force_Y"), f(ob.thug_particle_props.Force[1])))
                        p("\t\t:i {} = {}".format(c("Force_Z"), f(ob.thug_particle_props.Force[2])))
                    if ob.thug_particle_props.Speed[0] >= 0:
                        p("\t\t:i {} = {}".format(c("SpeedMin"), f(ob.thug_particle_props.Speed[0])))
                        p("\t\t:i {} = {}".format(c("SpeedMax"), f(ob.thug_particle_props.Speed[1])))
                    if ob.thug_particle_props.Size[0] >= 0:
                        p("\t\t:i {} = {}".format(c("EmitWidth"), f(ob.thug_particle_props.Size[0])))
                        p("\t\t:i {} = {}".format(c("EmitHeight"), f(ob.thug_particle_props.Size[1])))
                    if ob.thug_particle_props.Width[0] >= 0:
                        p("\t\t:i {} = {}".format(c("StartWidth"), f(ob.thug_particle_props.Width[0])))
                        p("\t\t:i {} = {}".format(c("EndWidth"), f(ob.thug_particle_props.Width[1])))
                    if ob.thug_particle_props.AngleSpread >= 0:
                        p("\t\t:i {} = {}".format(c("AngleSpread"), f(ob.thug_particle_props.AngleSpread)))
                        
                    if ob.thug_particle_props.UsePulseEmit:
                        p("\t\t:i {} = {}".format(c("UsePulseEmit"), c("TRUE")))
                    else:
                        p("\t\t:i {} = {}".format(c("UsePulseEmit"), c("FALSE")))
                    if ob.thug_particle_props.RandomEmitRate:
                        p("\t\t:i {} = {}".format(c("RandomEmitRate"), c("TRUE")))
                    else:
                        p("\t\t:i {} = {}".format(c("RandomEmitRate"), c("FALSE")))
                    if ob.thug_particle_props.RandomEmitDelay:
                        p("\t\t:i {} = {}".format(c("RandomEmitDelay"), c("TRUE")))
                    else:
                        p("\t\t:i {} = {}".format(c("RandomEmitDelay"), c("FALSE")))
                    if ob.thug_particle_props.UseMidTime:
                        p("\t\t:i {} = {}".format(c("UseMidTime"), c("TRUE")))
                    else:
                        p("\t\t:i {} = {}".format(c("UseMidTime"), c("FALSE")))
                        
                    if ob.thug_particle_props.MidTime >= 0:
                        p("\t\t:i {} = {}".format(c("MidTime"), i(ob.thug_particle_props.MidTime)))
                    
                    if ob.thug_particle_props.EmitTarget[0] >= 0:
                        p("\t\t:i {} = {}".format(c("EmitTarget_X"), f(ob.thug_particle_props.EmitTarget[0])))
                        p("\t\t:i {} = {}".format(c("EmitTarget_Y"), f(ob.thug_particle_props.EmitTarget[1])))
                        p("\t\t:i {} = {}".format(c("EmitTarget_Z"), f(ob.thug_particle_props.EmitTarget[2])))
                        
                    if ob.thug_particle_props.EmitRate1[0] > 0:
                        p("\t\t:i {} = {}".format(c("EmitRate1"), f(ob.thug_particle_props.EmitRate1[0])))
                        p("\t\t:i {} = {} ; {}".format(c("EmitRate1Rnd"), i(int(ob.thug_particle_props.EmitRate1[1])), i(int(ob.thug_particle_props.EmitRate1[2]))))
                    if ob.thug_particle_props.EmitRate1Delay[0] > 0:
                        p("\t\t:i {} = {}".format(c("EmitRate1Delay"), f(ob.thug_particle_props.EmitRate1Delay[0])))
                        p("\t\t:i {} = {} ; {}".format(c("EmitRate1DelayRnd"), i(int(ob.thug_particle_props.EmitRate1Delay[1])), i(int(ob.thug_particle_props.EmitRate1Delay[2]))))
                    if ob.thug_particle_props.EmitRate2[0] > 0:
                        p("\t\t:i {} = {}".format(c("EmitRate2"), f(ob.thug_particle_props.EmitRate2[0])))
                        p("\t\t:i {} = {} ; {}".format(c("EmitRate2Rnd"), i(int(ob.thug_particle_props.EmitRate2[1])), i(int(ob.thug_particle_props.EmitRate2[2]))))
                    if ob.thug_particle_props.EmitRate2Delay[0] > 0:
                        p("\t\t:i {} = {}".format(c("EmitRate2Delay"), f(ob.thug_particle_props.EmitRate2Delay[0])))
                        p("\t\t:i {} = {} ; {}".format(c("EmitRate2DelayRnd"), i(int(ob.thug_particle_props.EmitRate2Delay[1])), i(int(ob.thug_particle_props.EmitRate2Delay[2]))))
                        
                        
                    start_color = [ int(ob.thug_particle_props.particle_startcolor[0] * 255), 
                                    int(ob.thug_particle_props.particle_startcolor[1] * 255) , 
                                    int(ob.thug_particle_props.particle_startcolor[2] * 255) , 
                                    int(ob.thug_particle_props.particle_startcolor[3] * 255) ]
                    mid_color = [ int(ob.thug_particle_props.particle_midcolor[0] * 255), 
                                    int(ob.thug_particle_props.particle_midcolor[1] * 255) , 
                                    int(ob.thug_particle_props.particle_midcolor[2] * 255) , 
                                    int(ob.thug_particle_props.particle_midcolor[3] * 255) ]
                    end_color = [ int(ob.thug_particle_props.particle_endcolor[0] * 255), 
                                    int(ob.thug_particle_props.particle_endcolor[1] * 255) , 
                                    int(ob.thug_particle_props.particle_endcolor[2] * 255) , 
                                    int(ob.thug_particle_props.particle_endcolor[3] * 255) ]
                                    
                    p("\t\t:i {} = :a{{ {};{};{} :a}}".format(c("StartRGB"),
                                i(start_color[0]), i(start_color[1]),i(start_color[2])))
                    p("\t\t:i {} = {}".format(c("StartAlpha"), i(start_color[3])))
                    p("\t\t:i {} = :a{{ {};{};{} :a}}".format(c("EndRGB"),
                                i(end_color[0]), i(end_color[1]),i(end_color[2])))
                    p("\t\t:i {} = {}".format(c("EndAlpha"), i(end_color[3])))
                    if ob.thug_particle_props.particle_usecolormidtime == True:
                        p("\t\t:i {}".format(c("UseColorMidTime")))
                        p("\t\t:i {} = {}".format(c("ColorMidTime"), f(ob.thug_particle_props.particle_colormidtime)))
                        p("\t\t:i {} = :a{{ {};{};{} :a}}".format(c("MidRGB"),
                                i(mid_color[0]), i(mid_color[1]),i(mid_color[2])))
                        p("\t\t:i {} = {}".format(c("MidAlpha"), i(mid_color[3])))
                                
                
                # GAME OBJECT NODE
                elif ob.thug_empty_props.empty_type == "GameObject":
                    p("\t\t:i {} = {}".format(c("Class"), c("GameObject")))
                    if ob.thug_go_props.go_type == "Custom":
                        p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_go_props.go_type_other)))
                    else:
                        gameobj_type = ob.thug_go_props.go_type
                        if gameobj_type.startswith("Team_"):
                            gameobj_type = gameobj_type.replace("Team_", "Flag_")
                        p("\t\t:i {} = {}".format(c("Type"), c(gameobj_type)))
                        
                    # Override the TriggerScript settings for CTF nodes
                    # We want to use an auto-generated script which sets the appropriate game logic
                    if ob.thug_go_props.go_type.startswith("Flag_") or ob.thug_go_props.go_type.startswith("Team_"):
                        if ob.thug_triggerscript_props.template_name_txt == "" or ob.thug_triggerscript_props.template_name_txt == "None" or ob.thug_triggerscript_props.custom_name == "":
                            ob.thug_triggerscript_props.template_name_txt = "Custom"
                            ob.thug_triggerscript_props.custom_name = clean_name + "Script"
                            
                    # Removing temporarily to make imported levels easier to work with!
                    #if ob.thug_go_props.go_model != "":
                    #    p("\t\t:i {} = {}".format(c("Model"), c(ob.thug_go_props.go_type)))
                    if ob.thug_go_props.go_type in THUG_DefaultGameObjects:
                        p("\t\t:i {} = {}".format(c("Model"), blub_str(THUG_DefaultGameObjects[ob.thug_go_props.go_type])))
                    elif ob.thug_go_props.go_type == "Custom":
                        if ob.thug_go_props.go_model == "":
                            raise Exception("Game object " + clean_name + " has no model specified.")
                        else:
                            p("\t\t:i {} = {}".format(c("Model"), blub_str(ob.thug_go_props.go_model)))
                    p("\t\t:i {} = {}".format(c("SuspendDistance"), i(ob.thug_go_props.go_suspend)))
                    p("\t\t:i {} = {}".format(c("lod_dist1"), i(1024)))
                    p("\t\t:i {} = {}".format(c("lod_dist2"), i(2048)))
                    
                # PEDESTRIAN NODE
                elif ob.thug_empty_props.empty_type == "Pedestrian":
                    p("\t\t:i {} = {}".format(c("Class"), c("Pedestrian")))
                    p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_ped_props.ped_type)))
                    if ob.thug_ped_props.ped_source == "Profile":
                        p("\t\t:i {} = {}".format(c("profile"), c(ob.thug_ped_props.ped_profile)))
                    else:
                        p("\t\t:i {} = {}".format(c("model"), blub_str(ob.thug_ped_props.ped_model)))
                    if ob.thug_ped_props.ped_nologic:
                        p("\t\t:i {}".format(c("NoPedLogic")))
                    p("\t\t:i {} = {}".format(c("SkeletonName"), c(ob.thug_ped_props.ped_skeleton)))
                    p("\t\t:i {} = {}".format(c("AnimName"), c(ob.thug_ped_props.ped_animset)))
                    if ob.thug_ped_props.ped_extra_anims != "":
                        p("\t\t:i {} = {}".format(c("Extra_Anims"), c(ob.thug_ped_props.ped_extra_anims)))
                    p("\t\t:i {} = {}".format(c("SuspendDistance"), i(ob.thug_ped_props.ped_suspend)))
                    p("\t\t:i {} = {}".format(c("lod_dist1"), i(1024)))
                    p("\t\t:i {} = {}".format(c("lod_dist2"), i(2048)))
                    
                # VEHICLE NODE
                elif ob.thug_empty_props.empty_type == "Vehicle":
                    p("\t\t:i {} = {}".format(c("Class"), c("Vehicle")))
                    p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_veh_props.veh_type)))
                    p("\t\t:i {} = {}".format(c("model"), blub_str(ob.thug_veh_props.veh_model)))
                    if ob.thug_veh_props.veh_skeleton != "":
                        p("\t\t:i {} = {}".format(c("SkeletonName"), c(ob.thug_veh_props.veh_skeleton)))
                    p("\t\t:i {} = {}".format(c("SuspendDistance"), i(ob.thug_veh_props.veh_suspend)))
                    if ob.thug_veh_props.veh_norail == True:
                        p("\t\t:i {}".format(c("NoRail")))
                    if ob.thug_veh_props.veh_noskitch == True:
                        p("\t\t:i {}".format(c("NoSkitch")))
                    if ob.thug_veh_props.veh_usemodellights == True:
                        p("\t\t:i {}".format(c("UseModelLights")))
                    if ob.thug_veh_props.veh_allowreplacetex == True:
                        p("\t\t:i {}".format(c("AllowReplaceTex")))
                        
                    p("\t\t:i {} = {}".format(c("lod_dist1"), i(1024)))
                    p("\t\t:i {} = {}".format(c("lod_dist2"), i(2048)))
                    
                # GENERIC NODE
                elif ob.thug_empty_props.empty_type == "GenericNode":
                    p("\t\t:i {} = {}".format(c("Class"), c("GenericNode")))
                    p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_generic_props.generic_type)))
                    if ob.thug_generic_props.generic_type == 'Crown':
                        has_koth = True
                
                # COMMON PROPERTIES
                if ob.thug_created_at_start:
                    p("\t\t:i {}".format(c("CreatedAtStart")))
                if ob.thug_network_option != "Default":
                    p("\t\t:i {}".format(c(ob.thug_network_option)))
                    if ob.thug_network_option == "NetEnabled":
                        p("\t\t:i {}".format(c("Permanent")))
                        
                if ob.thug_triggerscript_props.template_name_txt != "" and ob.thug_triggerscript_props.template_name_txt != "None":
                    if ob.thug_triggerscript_props.template_name_txt == "Custom":
                        script_name = ob.thug_triggerscript_props.custom_name
                        custom_triggerscript_names.append(script_name)
                    else:
                        script_name, script_code = _generate_script(ob)
                        generated_scripts.setdefault(script_name, script_code)
                        
                    if script_name != "":
                        p("\t\t:i {} = {}".format(c("TriggerScript"), c(script_name)))
                    else:
                        operator.report({'WARNING'}, "Unable to determine a TriggerScript for object {}.".format(ob.name))

                if ob.thug_rail_connects_to:
                    if ob.thug_rail_connects_to not in bpy.data.objects:
                        operator.report({"ERROR"}, "Object {} connects to nonexistent path {}".format(ob.name, ob.thug_rail_connects_to))
                    else:
                        connected_to = bpy.data.objects[ob.thug_rail_connects_to]
                        if connected_to.name in rail_node_offsets:
                            p("\t\t:i {} = :a{{{}:a}}".format(
                                c("Links"),
                                i(rail_node_offsets[connected_to.name])))

                if ob.thug_node_expansion:
                    p("\t\t:i {}".format(c(ob.thug_node_expansion)))

            else:
                continue

            if custom_node_props.get(clean_name):
                p("#/ custom props")
                p(custom_node_props.get(clean_name).strip('\n'))
                p("#/ end custom props")
            p("\t:i :s}")

        # -----------------------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------
        single_restarts = []
        multi_restarts = []
        team_restarts = []
        generic_restarts = []
        koth_nodes = []
        ctf_nodes = []
        team_nodes = []

        if not has_restart_p1:
            single_restarts = [("TRG_Playerone_0", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))]
            print("Level has no Player 1 restarts. Generating one...")
        if not has_restart_multi:
            single_restarts = [("TRG_Multiplayer_0", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))]
            print("Level has no Multiplayer restarts. Generating one...")
        if not has_restart_team:
            single_restarts = [("TRG_Team_Restart", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))]
            print("Level has no Team restarts. Generating one...")
        if not has_koth:
            koth_nodes = [("TRG_KOTH", (0.0, 108.0, 0.0), (0.0, 0.0, 0.0))]
            print("Level has no KOTH crown. Generating one...")
        # Generate CTF components if any are missing, then alert with a warning for future reference
        if not has_ctf_blue:
            ctf_nodes.append(("TRG_CTF_Blue", "Flag_Blue", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
            print("Level has no CTF Blue Flag. Generating one...")
        if not has_ctf_base_blue:
            ctf_nodes.append(("TRG_CTF_Blue_Base", "Flag_Blue_Base", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
            print("Level has no CTF Blue Base. Generating one...")
        if not has_ctf_red:
            ctf_nodes.append(("TRG_CTF_Red", "Flag_Red", (500.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
            print("Level has no CTF Red Flag. Generating one...")
        if not has_ctf_base_red:
            ctf_nodes.append(("TRG_CTF_Red_Base", "Flag_Red_Base", (500.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
            print("Level has no CTF Red Base. Generating one...")
        if not has_ctf_green:
            ctf_nodes.append(("TRG_CTF_Green", "Flag_Green", (0.0, 0.0, 500.0), (0.0, 0.0, 0.0)))
            print("Level has no CTF Green Flag. Generating one...")
        if not has_ctf_base_green:
            ctf_nodes.append(("TRG_CTF_Green_Base", "Flag_Green_Base", (0.0, 0.0, 500.0), (0.0, 0.0, 0.0)))
            print("Level has no CTF Green Base. Generating one...")
        if not has_ctf_yellow:
            ctf_nodes.append(("TRG_CTF_Yellow", "Flag_Yellow", (-500.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
            print("Level has no CTF Yellow Flag. Generating one...")
        if not has_ctf_base_yellow:
            ctf_nodes.append(("TRG_CTF_Yellow_Base", "Flag_Yellow_Base", (-500.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
        if not has_team_blue:
            ctf_nodes.append(("TRG_Flag_Blue", "Flag_Blue", (1000.0, 0.0, 1000.0), (0.0, 0.0, 0.0)))
            print("Level has no Blue Team Flag. Generating one...")
        if not has_team_red:
            ctf_nodes.append(("TRG_Flag_Red", "Flag_Red", (700.0, 0.0, 1000.0), (0.0, 0.0, 0.0)))
            print("Level has no Red Team Flag. Generating one...")
        if not has_team_green:
            ctf_nodes.append(("TRG_Flag_Green", "Flag_Green", (400.0, 0.0, 1000.0), (0.0, 0.0, 0.0)))
            print("Level has no Green Team Flag. Generating one...")
        if not has_team_yellow:
            ctf_nodes.append(("TRG_Flag_Yellow", "Flag_Yellow", (100.0, 0.0, 1000.0), (0.0, 0.0, 0.0)))
            print("Level has no Yellow Team Flag. Generating one...")
            
        for (name, loc, rot) in single_restarts:
            p("""\t:i :s{{
\t\t:i $Pos$ = %vec3({:.6f},{:.6f},{:.6f})
\t\t:i $Angles$ = %vec3({:.6f},{:.6f},{:.6f})
\t\t:i $Name$ = {}
\t\t:i $Class$ = $Restart$
\t\t:i $Type$ = $Generic$
\t\t:i $RestartName$ = %s(11,"P1: Restart")
\t\t:i $CreatedAtStart$
\t\t:i $restart_types$ = :a{{$Player1$:a}}
\t:i :s}}""".format(loc[0], loc[1], loc[2], rot[0], rot[1], rot[2], c(name)))

        for (name, loc, rot) in multi_restarts:
            p("""\t:i :s{{
\t\t:i $Pos$ = %vec3({:.6f},{:.6f},{:.6f})
\t\t:i $Angles$ = %vec3({:.6f},{:.6f},{:.6f})
\t\t:i $Name$ = {}
\t\t:i $Class$ = $Restart$
\t\t:i $Type$ = $Multiplayer$
\t\t:i $CreatedAtStart$
\t\t:i $RestartName$ = %s(14,"Multi: Restart")
\t\t:i $restart_types$ = :a{{call $Multiplayer$ arguments
\t\t\t\t$Horse$:a}}
\t:i :s}}""".format(loc[0], loc[1], loc[2], rot[0], rot[1], rot[2], c(name)))

        for (name, loc, rot) in team_restarts:
            p("""\t:i :s{{
\t\t:i $Pos$ = %vec3({:.6f},{:.6f},{:.6f})
\t\t:i $Angles$ = %vec3({:.6f},{:.6f},{:.6f})
\t\t:i $Name$ = {}
\t\t:i $Class$ = $Restart$
\t\t:i $Type$ = $Team$
\t\t:i $CreatedAtStart$
\t\t:i $RestartName$ = %s(13,"Team: Restart")
\t\t:i $restart_types$ = :a{{$Team$:a}}
\t:i :s}}""".format(loc[0], loc[1], loc[2], rot[0], rot[1], rot[2], c(name)))

        for (name, loc, rot) in koth_nodes:
            p("""
\t:i :s{{
\t\t:i $Pos$ = %vec3{}
\t\t:i $Angles$ = %vec3{}
\t\t:i $Name$ = {}
\t\t:i $Class$ = $GenericNode$
\t\t:i $Type$ = $Crown$
\t:i :s}}
""".format(loc, rot, c(name)))

        for (name, ctf_type, loc, rot) in ctf_nodes:
            model_path = THUG_DefaultGameObjects[ctf_type]
            p("""\t:i :s{{
\t\t:i $Pos$ = %vec3({:.6f},{:.6f},{:.6f})
\t\t:i $Angles$ = %vec3({:.6f},{:.6f},{:.6f})
\t\t:i $Name$ = ${}$
\t\t:i $Class$ = $GameObject$
\t\t:i $Type$ = ${}$
\t\t:i $NeverSuspend$
\t\t:i $model$ = {}
\t\t:i $lod_dist1$ = %i(800,00000320)
\t\t:i $lod_dist2$ = %i(801,00000321)
\t\t:i $TriggerScript$ = ${}Script$
\t:i :s}}""".format(loc[0], loc[1], loc[2], rot[0], rot[1], rot[2], name, ctf_type, blub_str(model_path), name))

        p(":i :a}") # end node array =======================

        print("Exporting base TriggerScripts...")
        # -------------------------------------
        # Export GOALS script
        scr_goals = bpy.data.texts.get("_Goals", None)
        if not scr_goals:
            # Auto-fill goals script if it doesn't exist
            scr_goals = bpy.data.texts.new(name="_Goals")
            scr_goals.write("    :i if $InMultiplayerGame$" + "\n")
            scr_goals.write("        :i call $add_multiplayer_mode_goals$" + "\n")
            scr_goals.write("    :i endif" + "\n")
        p(":i function $" + filename + "_Goals" + "$")
        if target_game != "THUG2" and scr_goals:
            # Make sure we don't export the THUG2 if/else conditions!
            print("Writing _Goals script...")
            p(scr_goals.as_string().replace(":i if", ":i doIf").replace(":i else", ":i doElse"))
        elif scr_goals:
            print("Writing _Goals script...")
            p(scr_goals.as_string())
        p(":i endfunction")
        p("")
        # -------------------------------------
        # -------------------------------------
        # Export STARTUP script (if it exists)
        scr_start = bpy.data.texts.get("_Startup", None)
        p(":i function $" + filename + "_Startup" + "$")
        if target_game != "THUG2" and scr_start:
            # Make sure we don't export the THUG2 if/else conditions!
            print("Writing _Startup script...")
            p(scr_start.as_string().replace(":i if", ":i doIf").replace(":i else", ":i doElse"))
        elif scr_start:
            print("Writing _Startup script...")
            p(scr_start.as_string())
        p(":i endfunction")
        p("")
        # -------------------------------------
        # -------------------------------------
        # Export SETUP script (if it exists)
        scr_setup = bpy.data.texts.get("_Setup", None)
        p(":i function $" + filename + "_Setup" + "$")
        if target_game != "THUG2" and scr_setup:
            # Make sure we don't export the THUG2 if/else conditions!
            print("Writing _Setup script...")
            p(scr_setup.as_string().replace(":i if", ":i doIf").replace(":i else", ":i doElse"))
        elif scr_setup:
            print("Writing _Setup script...")
            p(scr_setup.as_string())
        p(":i endfunction")
        p("")
        # -------------------------------------
            
        if target_game == "THUG1": # not sure if this is needed?
            p("""\n:i $TriggerScripts$ =
:i :a{
\t:i $LoadTerrain$
            """)

            p(":i $TRG_CTF_BlueScript$")
            p(":i $TRG_CTF_RedScript$")
            p(":i $TRG_CTF_YellowScript$")
            p(":i $TRG_CTF_GreenScript$")
            p(":i $TRG_CTF_Blue_BaseScript$")
            p(":i $TRG_CTF_Red_BaseScript$")
            p(":i $TRG_CTF_Yellow_BaseScript$")
            p(":i $TRG_CTF_Green_BaseScript$")
            p(":i $TRG_Flag_BlueScript$")
            p(":i $TRG_Flag_RedScript$")
            p(":i $TRG_Flag_YellowScript$")
            p(":i $TRG_Flag_GreenScript$")
            p(":i $TRG_Flag_Blue_BaseScript$")
            p(":i $TRG_Flag_Red_BaseScript$")
            p(":i $TRG_Flag_Yellow_BaseScript$")
            p(":i $TRG_Flag_Green_BaseScript$")

            for script_name, script_code in generated_scripts.items():
                p("\t:i {}".format(c(script_name)))
            p('\n'.join("\t:i ${}$".format(script_name) for script_name in custom_triggerscript_names))
            p("\n:i :a}\n")

        # ------------------------------
        # GENERATED CTF FLAG SCRIPTS 
        # ------------------------------
        if not script_exists("TRG_CTF_BlueScript"):
            p("""
:i function $TRG_CTF_BlueScript$
    :i call $Team_Flag$ arguments $blue$
:i endfunction""")
        if not script_exists("TRG_CTF_RedScript"):
            p("""
:i function $TRG_CTF_RedScript$
    :i call $Team_Flag$ arguments $red$
:i endfunction""")
        if not script_exists("TRG_CTF_YellowScript"):
            p("""
:i function $TRG_CTF_YellowScript$
    :i call $Team_Flag$ arguments $yellow$
:i endfunction""")
        if not script_exists("TRG_CTF_GreenScript"):
            p("""
:i function $TRG_CTF_GreenScript$
    :i call $Team_Flag$ arguments $green$
:i endfunction""")
        # ------------------------------
        # GENERATED TEAM FLAG SCRIPTS 
        # ------------------------------
        if not script_exists("TRG_Flag_BlueScript"):
            p("""
:i function $TRG_Flag_BlueScript$
    :i call $Team_Flag$ arguments $blue$
:i endfunction""")
        if not script_exists("TRG_Flag_RedScript"):
            p("""
:i function $TRG_Flag_RedScript$
    :i call $Team_Flag$ arguments $red$
:i endfunction""")
        if not script_exists("TRG_Flag_YellowScript"):
            p("""
:i function $TRG_Flag_YellowScript$
    :i call $Team_Flag$ arguments $yellow$
:i endfunction""")
        if not script_exists("TRG_Flag_GreenScript"):
            p("""
:i function $TRG_Flag_GreenScript$
    :i call $Team_Flag$ arguments $green$
:i endfunction""")
        # ------------------------------
        # GENERATED TEAM BASE SCRIPTS 
        # ------------------------------
        if not script_exists("TRG_Flag_Blue_BaseScript"):
            p("""
:i function $TRG_Flag_Blue_BaseScript$
    :i call $Team_Flag_Base$ arguments $blue$
:i endfunction""")
        if not script_exists("TRG_Flag_Red_BaseScript"):
            p("""
:i function $TRG_Flag_Red_BaseScript$
    :i call $Team_Flag_Base$ arguments $red$
:i endfunction""")
        if not script_exists("TRG_Flag_Yellow_BaseScript"):
            p("""
:i function $TRG_Flag_Yellow_BaseScript$
    :i call $Team_Flag_Base$ arguments $yellow$
:i endfunction""")
        if not script_exists("TRG_Flag_Green_BaseScript"):
            p("""
:i function $TRG_Flag_Green_BaseScript$
    :i call $Team_Flag_Base$ arguments $green$
:i endfunction""")
        # ------------------------------
        # GENERATED CTF BASE SCRIPTS 
        # ------------------------------
        if not script_exists("TRG_CTF_Blue_BaseScript"):
            p("""
:i function $TRG_CTF_Blue_BaseScript$
    :i call $Team_Flag_Base$ arguments $blue$
:i endfunction""")
        if not script_exists("TRG_CTF_Red_BaseScript"):
            p("""
:i function $TRG_CTF_Red_BaseScript$
    :i call $Team_Flag_Base$ arguments $red$
:i endfunction""")
        if not script_exists("TRG_CTF_Yellow_BaseScript"):
            p("""
:i function $TRG_CTF_Yellow_BaseScript$
    :i call $Team_Flag_Base$ arguments $yellow$
:i endfunction""")
        if not script_exists("TRG_CTF_Green_BaseScript"):
            p("""
:i function $TRG_CTF_Green_BaseScript$
    :i call $Team_Flag_Base$ arguments $green$
:i endfunction""")

        # Export generic LoadAllParticleTextures script, if there isn't a script defined for it already
        if not script_exists("LoadAllParticleTextures"):
            p(":i function $LoadAllParticleTextures$")
            for ob in bpy.data.objects:
                if ob.type == 'EMPTY' and hasattr(ob, 'thug_empty_props') and ob.thug_empty_props.empty_type == 'ParticleObject' and ob.thug_particle_props.particle_texture != '':
                    p("\t:i $LoadParticleTexture$ %s(1,\"particles\\{}\")".format( ob.thug_particle_props.particle_texture ))
            p(":i endfunction")

        if target_game == "THUG1":
            def col(color):
                return blub_int(to_color_int(color))
                
            print("Writing script DoTODSetup...")
            # Underground+ TOD setup script for all 4 TOD states
            p(":i function $DoTODSetup$")
            scene = bpy.context.scene
            if hasattr(scene, 'thug_level_props'):
                tod_slots = [ scene.thug_level_props.tod_day
                        , scene.thug_level_props.tod_evening
                        , scene.thug_level_props.tod_night
                        , scene.thug_level_props.tod_morning ]
                tod_index = -1
                for slot in tod_slots:
                    tod_index += 1
                    str_tod_index = "$tod_index$ = {}".format(i(tod_index))
                    str_ambient_down = "$ambient_down_r$ = {} $ambient_down_g$ = {} $ambient_down_b$ = {}".format(
                        col(slot.ambient_down_rgb[0])
                        , col(slot.ambient_down_rgb[1])
                        , col(slot.ambient_down_rgb[2]) )
                    str_ambient_up = "$ambient_range_r$ = {} $ambient_range_g$ = {} $ambient_range_b$ = {}".format(
                        col(slot.ambient_up_rgb[0])
                        , col(slot.ambient_up_rgb[1])
                        , col(slot.ambient_up_rgb[2]) )
                    str_sun = "$sun_pitch$ = {} $sun_angle$ = {} $sun_r$ = {} $sun_g$ = {} $sun_b$ = {}".format(
                        i(slot.sun_headpitch[0])
                        , i(slot.sun_headpitch[1])
                        , col(slot.sun_rgb[0])
                        , col(slot.sun_rgb[1])
                        , col(slot.sun_rgb[2]) )
                    str_light1 = "$light1_pitch$ = {} $light1_angle$ = {} $light1_r$ = {} $light1_g$ = {} $light1_b$ = {}".format(
                        i(slot.light1_headpitch[0])
                        , i(slot.light1_headpitch[1])
                        , col(slot.light1_rgb[0])
                        , col(slot.light1_rgb[1])
                        , col(slot.light1_rgb[2]) )
                    str_fogdist = "$fog_dist_start$ = {} $fog_dist_end$ = {} $fog_bottom$ = {} $fog_top$ = {}".format(
                        i(slot.fog_startend[0])
                        , i(slot.fog_startend[1])
                        , i(slot.fog_bottomtop[0])
                        , i(slot.fog_bottomtop[1]) )
                    str_fogcolor = "$fog_r$ = {} $fog_g$ = {} $fog_b$ = {} $fog_a$ = {}".format(
                        col(slot.fog_rgba[0])
                        , col(slot.fog_rgba[1])
                        , col(slot.fog_rgba[2])
                        , col(slot.fog_rgba[3]) )
                    
                    str_todprops = " ".join([str_tod_index, str_ambient_down, str_ambient_up, str_sun, str_light1, str_fogdist, str_fogcolor])
                    
                    p("\t:i $UGPlus_SetTODProperties$ " + str_todprops)
                p("\t:i $UGPlus_SetTODScale$ $value$ = {}".format(f(scene.thug_level_props.tod_scale)) )
            p(":i endfunction")
        
            # Export script for adding cubemap probes into the level
            print("Writing script LoadCubemaps...")
            p(":i function $LoadCubemaps$")
            for ob in bpy.data.objects:
                if ob.type == 'EMPTY' and ob.thug_empty_props and ob.thug_empty_props.empty_type == 'CubemapProbe' \
                    and ob.thug_cubemap_props and ob.thug_cubemap_props.exported == True:
                    cm_pos = to_thug_coords(ob.location)
                    cm_file = "{}\{}.dds".format(filename, ob.name)
                    bbox, bbox_min, bbox_max, bbox_mid = get_bbox_from_node(ob)
                    p("\t:i $UGPlus_AddReflectionProbe$ $pos$ = {} $box_min$ = {} $box_max$ = {} $tex_file$ = {}".format(
                        v3(cm_pos)
                        , v3(bbox_min)
                        , v3(bbox_max)
                        , blub_str(cm_file) ) )
                        
                elif ob.type == 'EMPTY' and ob.thug_empty_props and ob.thug_empty_props.empty_type == 'LightProbe' \
                    and ob.thug_cubemap_props and ob.thug_cubemap_props.exported == True:
                    cm_pos = to_thug_coords(ob.location)
                    cm_file = "{}\{}.dds".format(filename, ob.name)
                    p("\t:i $UGPlus_AddLightProbe$ $pos$ = {} $tex_file$ = {}".format(
                        v3(cm_pos)
                        , blub_str(cm_file) ) )
            p(":i endfunction")
            
            # Export script for adding PBR area lights into the level
            if not script_exists("AddPBRLights"):
                print("Writing script AddPBRLights...")
                p(":i function $AddPBRLights$")
                # We need to add the light bounding volumes first, as the lights immediately check for these when added
                for ob in bpy.data.objects:
                    if ob.type == 'EMPTY' and hasattr(ob, 'thug_empty_props') and ob.thug_empty_props.empty_type == 'LightVolume':
                        # Get light volume min/max coords and export
                        bbox, bbox_min, bbox_max, bbox_mid = get_bbox_from_node(ob)
                        p("\t:i $UGPlus_AddLightVolume$ $box_min$ = {} $box_max$ = {} $box_mid$ = {}".format( 
                            v3(bbox_min), v3(bbox_max), v3(bbox_mid)))
                        
                for ob in bpy.data.objects:
                    if ob.type == 'LAMP' and hasattr(ob.data, 'thug_light_props'):
                        lightprops = ob.data.thug_light_props
                        # Collect light properties for QB export
                        tmpl_type = lightprops.light_type
                        tmpl_radius = lightprops.light_area[0] if lightprops.light_type == 'AREA' else lightprops.light_radius[0]
                        if lightprops.light_type == 'POINT':
                            tmpl_radius = 0.0
                        tmpl_height = lightprops.light_area[1] if lightprops.light_type == 'AREA' else 0.0
                        cm_pos = to_thug_coords(ob.location)
                        cm_end_pos = to_thug_coords(lightprops.light_end_pos)
                        tmpl_x = cm_pos[0]
                        tmpl_y = cm_pos[1]
                        tmpl_z = cm_pos[2]
                        tmpl_r = ob.data.color[0]
                        tmpl_g = ob.data.color[1]
                        tmpl_b = ob.data.color[2]
                        tmpl_end_x = tmpl_x + cm_end_pos[0] if lightprops.light_type == 'TUBE' else tmpl_x
                        tmpl_end_y = tmpl_y + cm_end_pos[1] if lightprops.light_type == 'TUBE' else tmpl_y
                        tmpl_end_z = tmpl_z + cm_end_pos[2] if lightprops.light_type == 'TUBE' else tmpl_z
                        tmpl_intensity = ob.data.energy
                        # Add the script line (AddAreaLight)
                        p("\t:i $UGPlus_AddAreaLight$ $light_type$ = {} $light_id$ = {} $pos_x$ = {} $pos_y$ = {} $pos_z$ = {} $r$ = {} $g$ = {} $b$ = {} $radius$ = {} $height$ = {} $intensity$ = {} $end_pos_x$ = {} $end_pos_y$ = {} $end_pos_z$ = {} $light_dir$ = {} $light_up$ = {} $light_left$ = {}".format( 
                            c(tmpl_type)
                            , c(get_clean_name(ob))
                            , f(tmpl_x)
                            , f(tmpl_y)
                            , f(tmpl_z)
                            , f(tmpl_r)
                            , f(tmpl_g)
                            , f(tmpl_b)
                            , f(tmpl_radius)
                            , f(tmpl_height)
                            , f(tmpl_intensity)
                            , f(tmpl_end_x)
                            , f(tmpl_end_y)
                            , f(tmpl_end_z)
                            , v3(ob.matrix_world.to_quaternion() * Vector((0.0, -1.0, 0.0)))
                            , v3(ob.matrix_world.to_quaternion() * Vector((0.0, 0.0, 1.0)))
                            , v3(ob.matrix_world.to_quaternion() * Vector((1.0, 0.0, 0.0)))
                            ))
                p(":i endfunction")
            
        print("Writing generated scripts...")
        for script_name, script_code in generated_scripts.items():
            p("")
            p(script_code)


        # Export generic LoadTerrain script, if there isn't a script defined for it already
        if not script_exists("LoadTerrain"):
            p(":i function $LoadTerrain$\n")

            for terrain_type in TERRAIN_TYPES:
                if terrain_type != "WHEELS":
                    if target_game == "THUG2":
                        p("\t:i $LoadTerrainSounds$$terrain$ = $TERRAIN_{}$\n".format(terrain_type))
                    else:
                        p("\t:i $SetTerrain{}$\n".format(terrain_type))

            if target_game == "THUG1":
                p(""":i call $LoadSound$ arguments %s(22,"Shared\Water\FallWater") $FLAG_PERM$\n""")


            p("""
    #/    :i call $script_change_tod$ arguments $tod_action$ = $set_tod_night$
    #/    :i call $start_dynamic_tod$

        :i endfunction""")

        # Export generic load_level_anims script, if there isn't a script defined for it already
        if not script_exists("load_level_anims"):
            p(""":i function $load_level_anims$
#/    :i $animload_THPS5_human$
:i endfunction""")

        # Export generic load_level_anims script, if there isn't a script defined for it already
        if not script_exists("LoadCameras"):
            p(""":i function $LoadCameras$
:i endfunction""")

        # Export generic LoadObjectAnims script, if there isn't a script defined for it already
        if not script_exists("LoadObjectAnims"):
            p(""":i function $LoadObjectAnims$
:i endfunction
""")

        print("Writing ncomp data...")
        ncomp_text = bpy.data.texts.get("NCOMP", None)
        if ncomp_text:
            p(ncomp_text.as_string())
            p("")
            p("#/ ncomp end")
            p("")

        p(":i :end")

        string_final = string_output.getvalue()
        import re
        for qb_identifier in re.findall(r"\$([A-Za-z_0-9]+)\$", string_final):
            c(qb_identifier)
        outp.write(string_final)

    with open(os.path.join(directory, "qb_table.qbi"), "w") as outp:
        for s, checksum in checksums.items():
            outp.write("#addx 0x{:08x} \"{}\"\n".format(checksum, s))

    with open(os.path.join(directory, filename + "_scripts.txt"), "w") as outp:
        print("Writing [level]_scripts data...")
        scripts_text = bpy.data.texts.get("_SCRIPTS", None)
        if scripts_text:
            if target_game != "THUG2":
                # Make sure we don't export the THUG2 if/else conditions!
                outp.write(scripts_text.as_string().replace(":i if", ":i doIf").replace(":i else", ":i doElse"))
            else:
                outp.write(scripts_text.as_string())
            outp.write("\n")
            outp.write("#/ level_scripts end")
            outp.write("\n")
        outp.write(":end")

    if target_game == "THUG2":
        with open(os.path.join(directory, filename + "_thugpro.qb"), "wb") as outp:
            outp.write(b'\x00')

#----------------------------------------------------------------------------------
#- Exports QB in the format used for models (or anything that isn't a level)
#----------------------------------------------------------------------------------
def export_model_qb(filename, directory, target_game, operator=None):
    checksums = {}

    def v3(v):
        return "%vec3({:6f},{:6f},{:6f})".format(*v)
    def c(s):
        if s not in checksums:
            if is_hex_string(s):
                checksums[s] = int(s, 0)
            else:
                checksums[s] = crc_from_string(bytes(s, 'ascii'))
        return "$" + s + "$"
    i = blub_int
    _string = blub_str

    generated_scripts = {}
    custom_triggerscript_names = []
    custom_node_props = get_custom_node_props()
    custom_func_code = get_custom_func_code()

    with open(os.path.join(directory, filename + ".txt"), "w") as outp:
        from io import StringIO
        string_output = StringIO()
        p = lambda *args, **kwargs: print(*args, **kwargs, file=string_output)
        p("%include \"qb_table.qbi\"")

        # Dump all TriggerScript text blocks here!
        all_triggerscripts = [s for s in bpy.data.texts if s.name.startswith("script_")]
        for ts in all_triggerscripts:
            p(":i function $" + ts.name[7:] + "$")
            if target_game != "THUG2":
                # Make sure we don't export the THUG2 if/else conditions!
                p(ts.as_string().replace(":i if", ":i doIf").replace(":i else", ":i doElse"))
            else:
                p(ts.as_string())
            p(":i endfunction")
            p("")
        p("")
        p("#/ custom script code end")
        p("")
        
        # Start listing the actual NodeArray...
        p("$" + filename + "_NodeArray$ =")
        p(":i :a{")

        rail_custom_triggerscript_names, rail_generated_scripts, rail_node_offsets = autorail._export_rails(p, c, operator)
        custom_triggerscript_names += rail_custom_triggerscript_names
        generated_scripts.update(rail_generated_scripts)

        for ob in bpy.data.objects:
            if ob.type == "MESH" and not ob.get("thug_autosplit_object_no_export_hack"):
                is_levelobject = ob.thug_object_class == "LevelObject"
                clean_name = get_clean_name(ob)
                    
                if not ob.thug_always_export_to_nodearray and \
                    not is_levelobject and \
                    ob.thug_created_at_start and \
                    not custom_node_props.get(clean_name) and \
                    not ob.name.lower().startswith("NightOn") and \
                    not ob.name.lower().startswith("NightOff") :
                    if (not getattr(ob, "thug_is_trickobject", False) and
                            ob.thug_triggerscript_props.triggerscript_type == "None") \
                        or not \
                        (getattr(ob, "thug_export_collision", True) or
                         getattr(ob, "thug_export_scene", True)):
                        continue
                p("\t:i :s{")
                p("\t\t:i {} = {}".format(c("Pos"), v3(to_thug_coords(ob.location)))) # v3(get_sphere(ob))))
                if is_levelobject:
                    p("\t\t:i {} = {}".format(c("Angles"), v3(to_thug_coords_ns(ob.rotation_euler))))
                    # p("\t\t:i {} = {}".format(c("Scale"), v3(to_thug_coords(ob.scale))))
                else:
                    p("\t\t:i {} = {}".format(c("Angles"), v3((0, 0, 0))))
                    # p("\t\t:i {} = {}".format(c("Scale"), v3((2, 0.5, 1))))
                p("\t\t:i {} = {}".format(c("Name"), c(clean_name)))
                p("\t\t:i {} = {}".format(c("Class"), c("LevelGeometry") if not is_levelobject else c("LevelObject")))

                if ob.thug_created_at_start:
                    p("\t\t:i {}".format(c("CreatedAtStart")))

                if getattr(ob, "thug_is_trickobject", False):
                    p("\t\t:i call {} arguments".format(c("TrickObject")))
                    p("\t\t\t{} = {}".format(c("Cluster"),
                                             c(ob.thug_cluster_name if ob.thug_cluster_name else clean_name)))
                p("\t\t:i {} = {}".format(c("CollisionMode"), c("Geometry")))

                if ob.thug_triggerscript_props.template_name_txt != "" and ob.thug_triggerscript_props.template_name_txt != "None":
                    if ob.thug_triggerscript_props.template_name_txt == "Custom":
                        script_name = ob.thug_triggerscript_props.custom_name
                        custom_triggerscript_names.append(script_name)
                    else:
                        script_name, script_code = _generate_script(ob)
                        generated_scripts.setdefault(script_name, script_code)
                    
                    if script_name != "":
                        p("\t\t:i {} = {}".format(c("TriggerScript"), c(script_name)))
                    else:
                        operator.report({'WARNING'}, "Unable to determine a TriggerScript for object {}.".format(ob.name))

                if ob.thug_node_expansion:
                    p("\t\t:i {}".format(c(ob.thug_node_expansion)))

            elif ob.type == "EMPTY" and ob.thug_empty_props.empty_type == "Custom":
                clean_name = get_clean_name(ob)

                p("\t:i :s{")
                p("\t\t:i {} = {}".format(c("Pos"), v3(to_thug_coords(ob.location))))
                p("\t\t:i {} = {}".format(c("Angles"), v3(to_thug_coords_ns(ob.rotation_euler))))
                # p("\t\t:i {} = {}".format(c("Scale"), v3(to_thug_coords_ns(ob.scale))))
                p("\t\t:i {} = {}".format(c("Name"), c(clean_name)))

                if ob.thug_node_expansion:
                    p("\t\t:i {}".format(c(ob.thug_node_expansion)))

            else:
                continue

            if custom_node_props.get(clean_name):
                p("#/ custom props")
                p(custom_node_props.get(clean_name).strip('\n'))
                p("#/ end custom props")
            p("\t:i :s}")

            
        p(":i :a}") # end node array =======================

        if target_game == "THUG1": # not sure if this is needed?
            p("""\n:i $""" + filename + """TriggerScripts$ = 
:i :a{ """)
        elif target_game == "THUG2":
            p("""\n:i $""" + filename + """TriggerScripts$ = 
:i :a{ """)

        for script_name, script_code in generated_scripts.items():
            p("\t:i {}".format(c(script_name)))
        p('\n'.join("\t:i ${}$".format(script_name) for script_name in custom_triggerscript_names))
        p("\n:i :a}\n")

        
        for script_name, script_code in generated_scripts.items():
            p("")
            p(script_code)

        p(":i :end")

        string_final = string_output.getvalue()
        import re
        for qb_identifier in re.findall(r"\$([A-Za-z_0-9]+)\$", string_final):
            c(qb_identifier)
        outp.write(string_final)

    with open(os.path.join(directory, "qb_table.qbi"), "w") as outp:
        for s, checksum in checksums.items():
            outp.write("#addx 0x{:08x} \"{}\"\n".format(checksum, s))



#----------------------------------------------------------------------------------
#- Skips through the level QB until the checksum table is found
#- In the future, this could be updated to a full QB parser
#----------------------------------------------------------------------------------
def seek_to_checksum_table(r, fileLen):
    while (r.offset < fileLen):
        token = r.u8()
        len = 0

        if token == 0x02: # newline
            r.i32()
        elif token == 0x16: # checksum
            r.i32()
        elif token == 0x17: # int
            r.i32()
        elif token == 0x1a: # float
            r.i32()
        elif (token == 0x1b) or (token == 0x1c):
            len = r.i32()
            r.offset += len
        elif token == 0x1e: # vec3
            r.i32()
            r.i32()
            r.i32()
        elif token == 0x1f: # vec2
            r.i32()
            r.i32()
        elif (token == 0x47) or (token == 0x48) or (token == 0x49):
            len = r.u16()
            r.offset += len
        elif token == 0x2B: # table
            r.offset -= 1
            break
#----------------------------------------------------------------------------------
#- Reads object names from the level .QB file
#- Currently, this is the only QB importing that can be done directly
#----------------------------------------------------------------------------------
def parse_qb_checksums(filename, directory):
    p = Printer()
    input_file = os.path.join(directory, filename)

    if os.path.isfile(input_file):
        p("input_file={}", input_file)
        with open(input_file, "rb") as inp:
            r = Reader(inp.read())
        statinfo = os.stat(input_file)
        fileLen = statinfo.st_size
        seek_to_checksum_table(r, fileLen)
        while (r.offset < fileLen):

            if r.u8() == 0x2b:
                checksumName = ''
                checksum = str(hex(r.u32()))

                stringBytes = []
                while (r.u8() != 0x00):
                    r.offset -= 1
                    stringBytes.append(chr(r.u8()))
                    checksumName = ''.join(stringBytes)

                p("checksum: {} checksumName: {}", checksum, checksumName)
                if checksum not in checksumLookupTable:
                    checksumLookupTable[checksum] = checksumName 
    else:
        p("cant find file: \"{}\"", input_file)
        return
        
    # Find any objects in the scene with this checksum in the name and rename!
    for ob in bpy.data.objects:
        if not ob.type == 'MESH': continue
        ob_name = get_clean_name(ob)
        if ob_name in checksumLookupTable:
            if ob.thug_export_collision:
                new_name = checksumLookupTable[ob_name]
            else:
                new_name = checksumLookupTable[ob_name] + '_SCN'
                
            print("Renamed {} to: {}".format(ob.name, new_name))
            ob.name = new_name
            
#----------------------------------------------------------------------------------
#- Either switches view to the assigned script, or creates a new one
#----------------------------------------------------------------------------------
def maybe_create_triggerscript(self, context):
    if context.object.thug_triggerscript_props.custom_name != '':
        script_name = context.object.thug_triggerscript_props.custom_name
    else:
        script_name = context.object.name + "Script"
        
    if not script_name in context.window_manager.thug_all_nodes.scripts:
        bpy.data.texts.new('script_' + script_name)
    
    if context.object.thug_triggerscript_props.custom_name == '':
        context.object.thug_triggerscript_props.custom_name = script_name
    
    editor_found = False
    for area in context.screen.areas:
        if area.type == "TEXT_EDITOR":
            editor_found = True
            break

    if editor_found:
        area.spaces[0].text = bpy.data.texts['script_' + script_name]
        


# OPERATORS
#############################################
class THUGCreateTriggerScript(bpy.types.Operator):
    bl_idname = "io.thug_create_triggerscript"
    bl_label = "Create/View TriggerScript"
    # bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        maybe_create_triggerscript(self, context)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

class THUGImportLevelQB(bpy.types.Operator):
    bl_idname = "io.thug_import_levelqb"
    bl_label = "THPS Level QB (.qb)"
    # bl_options = {'REGISTER', 'UNDO'}

    filter_glob = StringProperty(default="*.qb", options={"HIDDEN"})
    filename = StringProperty(name="File Name")
    directory = StringProperty(name="Directory")
    
    def execute(self, context):
        filename = self.filename
        directory = self.directory

        parse_qb_checksums(filename, directory)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}
