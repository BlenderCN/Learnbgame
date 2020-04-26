#############################################
# OBJECT PRESETS
# Handles the generation of TH engine presets
# - nodes, objects, CAP pieces, etc
#############################################
import bpy
import bmesh
import struct
import mathutils
import math
import numpy
from bpy.props import *
from . helpers import *
from . material import *
from . pieces import *
from . autorail import *
from . tex import *
from . import_thug1 import *
from . import_thug2 import *
import fnmatch

# Park piece rotation constants
ROTATE_0 = 0
ROTATE_90 = 1
ROTATE_180 = 2
ROTATE_270 = 3

# METHODS
#############################################
def get_actual_preset_size():
    return 1.0 / bpy.context.scene.thug_level_props.export_props.export_scale
    
def preset_place_node(node_type, position):
    scene = bpy.context.scene
    bpy.ops.object.select_all(action='DESELECT')
    print("Placing a {}".format(node_type))
    # Create a new Empty, which we will fill in with TH specific data
    ob = bpy.data.objects.new( "empty", None ) 
    ob.location = position
    actual_scale = get_actual_preset_size()
    
    if node_type == 'RESTART':
        ob.name = get_unique_name('TRG_Restart')
        scene.objects.link( ob )
        scene.objects.active = ob 
        ob.select = True
        ob.thug_empty_props.empty_type = 'Restart'
        ob.thug_restart_props.restart_type = "Player1"
        ob.thug_restart_props.restart_p1 = True
        to_group(ob, "Restarts")
        
    elif node_type == 'KOTH_CROWN':
        ob.name = get_unique_name('TRG_KOTH')
        scene.objects.link( ob )
        scene.objects.active = ob 
        ob.select = True
        ob.thug_empty_props.empty_type = "GenericNode"
        ob.thug_generic_props.generic_type = "Crown"
        to_group(ob, "GenericNodes")
        
    elif node_type == 'PEDESTRIAN':
        ob.name = get_unique_name('TRG_Pedestrian')
        scene.objects.link( ob )
        scene.objects.active = ob 
        ob.select = True
        ob.thug_empty_props.empty_type = 'Pedestrian'
        ob.thug_ped_props.ped_type = "Ped_From_Profile"
        ob.thug_ped_props.ped_source = "Profile"
        ob.thug_ped_props.ped_profile = "random_male_profile"
        ob.thug_ped_props.ped_skeleton = "THPS5_human"
        ob.thug_ped_props.ped_animset = "animload_THPS5_human"
        to_group(ob, "Pedestrians")
        
    elif node_type == 'VEHICLE':
        ob.name = get_unique_name('TRG_Vehicle')
        scene.objects.link( ob )
        scene.objects.active = ob 
        ob.select = True
        ob.thug_empty_props.empty_type = 'Vehicle'
        ob.thug_veh_props.veh_type = "Generic"
        to_group(ob, "Vehicles")
        
    elif node_type == 'CUBEMAP_PROBE':
        ob.name = get_unique_name('ReflectionProbe')
        ob.rotation_euler = [math.radians(90), 0, math.radians(-90)]
        scene.objects.link( ob )
        ob.thug_empty_props.empty_type = 'CubemapProbe'
        ob.empty_draw_type = 'SPHERE'
        ob.empty_draw_size = 64
        ob.show_name = True
        ob.show_x_ray = True
        to_group(ob, "Reflection Probes")
        
        # Also add a camera used in cubemap rendering, with the correct settings filled in
        bpy.ops.object.camera_add(view_align=False,
                          location=[0, 0, 0],
                          rotation=[0, 0, 0])
        camera_ob = bpy.context.object
        camera_ob.name = get_unique_name('CAM_ReflectionProbe')
        camera_ob.parent = ob
        camera_ob.data.draw_size = 48.0
        
        scene.objects.active = ob 
        ob.select = True
        
    elif node_type == 'LIGHT_PROBE':
        ob.name = get_unique_name('LightProbe')
        ob.rotation_euler = [math.radians(90), 0, math.radians(-90)]
        scene.objects.link( ob )
        ob.thug_empty_props.empty_type = 'LightProbe'
        ob.empty_draw_type = 'SPHERE'
        ob.empty_draw_size = 64
        ob.show_name = True
        ob.show_x_ray = True
        to_group(ob, "Light Probes")
        
        # Also add a camera used in cubemap rendering, with the correct settings filled in
        bpy.ops.object.camera_add(view_align=False,
                          location=[0, 0, 0],
                          rotation=[0, 0, 0])
        camera_ob = bpy.context.object
        camera_ob.name = get_unique_name('CAM_LightProbe')
        camera_ob.parent = ob
        camera_ob.data.draw_size = 48.0
        
        scene.objects.active = ob 
        ob.select = True
        
    elif node_type == 'LIGHT_VOLUME':
        ob.name = get_unique_name('LightVolume')
        scene.objects.link( ob )
        scene.objects.active = ob 
        ob.select = True
        ob.thug_empty_props.empty_type = 'LightVolume'
        
        
    elif node_type == 'GAMEOBJECT' or node_type == 'CTF_FLAG' or node_type == 'CTF_BASE':
        if node_type.startswith('CTF_'):
            ob.name = get_unique_name('TRG_CTF')
        else:
            ob.name = get_unique_name('TRG_GO')
        scene.objects.link( ob )
        scene.objects.active = ob 
        ob.select = True
        ob.thug_empty_props.empty_type = 'GameObject'
        if node_type == 'CTF_FLAG':
            ob.thug_go_props.go_type = 'Flag_Red'
        elif node_type == 'CTF_BASE':
            ob.thug_go_props.go_type = 'Flag_Red_Base'
        else:
            ob.thug_go_props.go_type = 'Ghost'
        to_group(ob, "GameObjects")
        
    elif node_type == 'PARTICLEOBJECT':
        ob.name = get_unique_name('Particle')
        scene.objects.link( ob )
        scene.objects.active = ob 
        ob.select = True
        ob.thug_empty_props.empty_type = 'ParticleObject'
        ob.thug_particle_props.particle_boxdimsstart = [0, 0, 24]
        ob.thug_particle_props.particle_boxdimsmid = [30, 30, 30]
        ob.thug_particle_props.particle_boxdimsend = [60, 60, 60]
        ob.thug_particle_props.particle_startposition = [0, 0, 0]
        ob.thug_particle_props.particle_midposition = [0, 0, 400]
        ob.thug_particle_props.particle_endposition = [0, 0, 1000]
        ob.thug_particle_props.particle_texture = 'dt_generic_particle01'
        ob.thug_particle_props.particle_type = 'NewFlat'
        ob.thug_particle_props.particle_blendmode = 'Blend'
        ob.thug_particle_props.particle_startcolor = [0.25, 0.25, 0.25, 0.4]
        ob.thug_particle_props.particle_midcolor = [0.35, 0.35, 0.35, 0.4]
        ob.thug_particle_props.particle_endcolor = [0.45, 0.45, 0.45, 0.0]
        ob.thug_particle_props.particle_maxstreams = 2
        ob.thug_particle_props.particle_emitrate = 60.0
        ob.thug_particle_props.particle_lifetime = 2.0
        ob.thug_particle_props.particle_usemidpoint = True
        ob.thug_particle_props.particle_midpointpct = 50
        
        ob.thug_particle_props.particle_radius = [25, 40, 100]
        ob.thug_particle_props.particle_radiusspread = [5, 10, 0]
        to_group(ob, "ParticleObjects")
        
        
    elif node_type == 'RAIL_NODE' or node_type == 'RAIL_PREMADE':
        rail_path_name = get_unique_name('TRG_RailPath')
        curveData = bpy.data.curves.new(rail_path_name, type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 12
        curveData.bevel_depth = get_path_bevel_size()
        curveData.bevel_resolution = 2
        curveData.fill_mode = 'FULL'
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(1)
        rail_pos = mathutils.Vector([position[0], position[1], position[2], 0])
        polyline.points[0].co = rail_pos + mathutils.Vector([ 0, 0, 0, 0])
        polyline.points[1].co = rail_pos + mathutils.Vector([ 0, 250 * get_path_bevel_size(), 0, 0])
        
        curveOB = bpy.data.objects.new(rail_path_name, curveData)
        curveOB.thug_path_type = "Rail"
        curveOB.thug_rail_terrain_type = "GRINDMETAL"
        curveOB.data.thug_pathnode_triggers.add()
        curveOB.data.thug_pathnode_triggers.add()
        
        # Add shared rail material to curve (lets the user customize rail/path colors)
        rail_mat = get_material('io_thps_scene_RailMaterial')
        if not curveOB.data.materials.get(rail_mat.name):
            curveOB.data.materials.append(rail_mat)
            
        # attach to scene and validate context
        scene.objects.link(curveOB)
        scene.objects.active = curveOB
        curveOB.select = True
        to_group(curveOB, "RailNodes")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        if node_type == 'RAIL_PREMADE':
            build_rail_mesh(curveOB)
    
    elif node_type == 'RAIL_POINT' or node_type == 'RAIL_POINT_PREMADE':
        rail_path_name = get_unique_name('TRG_RailPoint')
        curveData = bpy.data.curves.new(rail_path_name, type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 12
        curveData.bevel_depth = get_path_bevel_size()
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        rail_pos = mathutils.Vector([position[0], position[1], position[2], 0])
        
        if node_type == 'RAIL_POINT':
            polyline.points[0].co = mathutils.Vector([ 0, 0, 0, 0])
        else:
            polyline.points[0].co = mathutils.Vector([ 0, 0, 24, 0])
        
        curveOB = bpy.data.objects.new(rail_path_name, curveData)
        curveOB.location = [ 0, 0, 0 ]
        if node_type == 'RAIL_POINT':
            curveOB.location = position
        curveOB.thug_path_type = "Rail"
        curveOB.thug_rail_terrain_type = "GRINDMETAL"
        curveOB.data.thug_pathnode_triggers.add()
        
        # Add shared rail material to curve (lets the user customize rail/path colors)
        rail_mat = get_material('io_thps_scene_RailMaterial')
        if not curveOB.data.materials.get(rail_mat.name):
            curveOB.data.materials.append(rail_mat)
        
        if node_type == 'RAIL_POINT_PREMADE':
            meshOB = append_from_dictionary('presets', 'Rail_Post', scene)
            meshOB.location = position
            meshOB.scale = [actual_scale, actual_scale, actual_scale]
        
        # attach to scene and validate context
        scene.objects.link(curveOB)
        scene.objects.active = curveOB
        if node_type == 'RAIL_POINT_PREMADE':
            curveOB.parent = meshOB
        curveOB.select = True
        curveOB.show_texture_space = True
        curveOB.show_name = True
        to_group(curveOB, "RailNodes")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        
    
    elif node_type == 'WAYPOINT' or node_type == 'LADDER':
        path_name = get_unique_name('TRG_Waypoint')
        curveData = bpy.data.curves.new(path_name, type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 12
        curveData.bevel_depth = get_path_bevel_size()
        curveData.bevel_resolution = 2
        curveData.fill_mode = 'FULL'
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(1)
        rail_pos = mathutils.Vector([position[0], position[1], position[2], 0])
        polyline.points[0].co = rail_pos + mathutils.Vector([ 0, 0, 0, 0])
        if node_type == 'LADDER':
            polyline.points[1].co = rail_pos + mathutils.Vector([ 0, 0, 250 * get_path_bevel_size(), 0])
        else:
            polyline.points[1].co = rail_pos + mathutils.Vector([ 0, 250 * get_path_bevel_size(), 0, 0])
        
        curveOB = bpy.data.objects.new(path_name, curveData)
        curveOB.thug_path_type = 'Waypoint' if node_type == 'WAYPOINT' else 'Ladder'
        curveOB.data.thug_pathnode_triggers.add()
        curveOB.data.thug_pathnode_triggers.add()
        
        # Add shared rail material to curve (lets the user customize rail/path colors)
        if node_type == 'LADDER':
            rail_mat = get_material('io_thps_scene_LadderMaterial')
        else:
            rail_mat = get_material('io_thps_scene_WaypointMaterial')
        if not curveOB.data.materials.get(rail_mat.name):
            curveOB.data.materials.append(rail_mat)
            
        # attach to scene and validate context
        scene.objects.link(curveOB)
        scene.objects.active = curveOB
        curveOB.select = True
        if node_type == 'WAYPOINT':
            to_group(curveOB, 'Waypoints')
        else:
            to_group(curveOB, 'ClimbingNodes')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    
def append_from_assets(asset_path, target_game, context):
    addon_prefs = context.user_preferences.addons[ADDON_NAME].preferences
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
        return []

    tex_path = os.path.splitext(asset_path)[0] + '.tex'
    
    if ext_suffix != '':
        asset_path += ext_suffix
        tex_path += ext_suffix
        
    
    # Check for the tex file first (if applicable)
    if tex_path:
        for game_path in game_paths:
            #print("Asset path: {}".format(os.path.join(game_path, asset_path)))
            #print("TEX path: {}".format(os.path.join(game_path, tex_path)))
            if os.path.exists(os.path.join(game_path, tex_path)):
                #print("Found TEX asset: {}".format(os.path.join(game_path, tex_path)))
                p = Printer()
                p.on = False
                with open(os.path.join(game_path, tex_path), "rb") as inp:
                    r = Reader(inp.read())
                    read_tex(r, p)
                break
            
    # Then load the MDL/SKIN/IMG file
    objects = []
    for game_path in game_paths:
        #print("Asset path: {}".format(os.path.join(game_path, asset_path)))
        #print("TEX path: {}".format(os.path.join(game_path, tex_path)))
        if os.path.exists(os.path.join(game_path, asset_path)):
            #print("Found asset: {}".format(os.path.join(game_path, asset_path)))
            p = Printer()
            p.on = False
            with open(os.path.join(game_path, asset_path), "rb") as inp:
                r = Reader(inp.read())
                
            _mat_version = r.u32()
            _mesh_version = r.u32()
            _vert_version = r.u32()
            num_materials = p("num materials: {}", r.u32())
            read_materials(r, p, num_materials, game_path, None)
            num_sectors = p("num sectors: {}", r.i32())
            if target_game == 'THUG1':
                #print("Reading {} as a THUG1 mesh".format(os.path.join(game_path, asset_path)))
                objects = read_sectors_ug1(r, p, num_sectors, context, None)
            elif target_game == 'THUG2':
                #print("Reading {} as a THUG2 mesh".format(os.path.join(game_path, asset_path)))
                objects = read_sectors_ug2(r, p, num_sectors, context, None)
            rename_imported_materials()
            break
                
    return objects
            
            
def append_from_dictionary(dict_name, piece_name, scn, use_existing = False, include_rails = True):
    # Get the path to the dictionary .blend file - it should always be within the
    # base files as defined in the plugin configuration
    addon_prefs = bpy.context.user_preferences.addons[ADDON_NAME].preferences
    base_files_dir_error = prefs._get_base_files_dir_error(addon_prefs)
    if base_files_dir_error:
        self.report({"WARNING"}, "Base files directory error: {} - Unable to find path to template .blend files.".format(base_files_dir_error))
        raise Exception("Unable to find template .blend file.")
    base_files_dir = addon_prefs.base_files_dir
    actual_scale = get_actual_preset_size()
    
    # This flag tells us to try using an object of the same name from the scene first, then
    # read from the external blend file. Used by the PRK importer to stop us from pulling the
    # dictionary blend files once per object!
    if use_existing:
        piece_search = [obj for obj in scn.objects if fnmatch.fnmatch(obj.name, piece_name)]
        if piece_search:
            source_piece = piece_search[0]
            new_piece = source_piece.copy()
            new_piece.data = source_piece.data.copy()
            parent_piece = new_piece
            # If this piece is a child of a SCN mesh, copy that as well
            if new_piece.parent:
                parent_piece = new_piece.parent.copy()
                parent_piece.data = new_piece.parent.data.copy()
                new_piece.parent = parent_piece
                scn.objects.link(parent_piece)
                scn.objects.link(new_piece)
            else:
                scn.objects.link(new_piece)
            
            # Also search for a rail path, if desired
            if include_rails and bpy.data.objects.get(piece_name + '_RAIL'):
                rail_piece = bpy.data.objects.get(piece_name + '_RAIL').copy()
                rail_piece.data = bpy.data.objects.get(piece_name + '_RAIL').data.copy()
                rail_piece.parent = parent_piece
                scn.objects.link(rail_piece)
                
            return parent_piece
            
            
    # This is where we append the object and determine the name when it is added to the scene
    filepath = base_files_dir + "scenes\\" + dict_name + ".blend"
    linked_obs = []
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        if include_rails:
            data_to.objects = [name for name in data_from.objects if ( fnmatch.fnmatch(name, piece_name) or \
            fnmatch.fnmatch(name, piece_name + '_SCN*') or fnmatch.fnmatch(name, piece_name + '_RAIL*') )]
        else:
            data_to.objects = [name for name in data_from.objects if ( fnmatch.fnmatch(name, piece_name) or \
            fnmatch.fnmatch(name, piece_name + '_SCN*') )]

    # Link object(s) to the scene, then figure out which one should be parent (if there are multiple)
    for obj in data_to.objects:
        if obj is not None:
            #print(obj.name)
            scn.objects.link(obj)
            linked_obs.append(obj.name)
            
    parent_ob = None
    for ob_name in linked_obs:
        if bpy.data.objects.get(ob_name).type == 'MESH' and bpy.data.objects.get(ob_name).thug_export_scene:
            parent_ob = bpy.data.objects.get(ob_name)
    if parent_ob:
        for ob_name in linked_obs:
            if ob_name != parent_ob.name:
                child_ob = bpy.data.objects.get(ob_name)
                # Use the relative position to the parent object
                child_ob.location = child_ob.location - parent_ob.location
                child_ob.parent = parent_ob
    elif len(linked_obs) == 1 and bpy.data.objects.get(linked_obs[0]):
        parent_ob = bpy.data.objects.get(linked_obs[0])
                
    parent_ob.scale = [actual_scale, actual_scale, actual_scale]
    return parent_ob
        
def preset_place_mesh(dictionary_name, piece_name, position):
    scene = bpy.context.scene
    bpy.ops.object.select_all(action='DESELECT')
    new_piece = append_from_dictionary(dictionary_name, piece_name, scene)
    #new_piece.data = source_piece.data.copy()
    new_piece.location = position
    new_piece.hide = False
    new_piece.hide_render = False
    #new_piece.thug_export_scene = True
    #new_piece.thug_export_collision = True
    #scene.objects.link(new_piece)
    scene.objects.active = new_piece
    new_piece.select = True
    return new_piece
    
def preset_place_compositeobject(piece_name):
    piece_data = {}
    found = False
    pieces = []
    for category in Ed_Pieces_UG1:
        for ob in category:
            # Single object definitions don't use "single" for the mesh name
            if "single" in ob and ob["single"] == piece_name:
                found = True
                piece = {}
                piece["name"] = ob["single"]
                if "pos" in ob:
                    piece["pos"] = ob["pos"]
                else:
                    piece["pos"] = [0,0,0]
                if "is_riser" in ob:
                    piece["riser"] = 1
                pieces.append(piece)
                break
                
            # Multi-object composites have a "name" property we can look up
            elif "name" in ob and ob["name"] == piece_name:
                found = True
                piece_data["name"] = piece_name
            
                for cob in ob["multiple"]:
                    piece = {}
                    piece["name"] = cob["name"]
                    if "pos" in cob:
                        piece["pos"] = cob["pos"]
                    else:
                        piece["pos"] = [0,0,0]
                    pieces.append(piece)
                            
    if not found:
        raise Exception("Unable to find object {} in piece list.".format(piece_name))
    
    piece_data["pieces"] = pieces
    return piece_data

    
#----------------------------------------------------------------------------------
preset_node_list = [
    { 'name': 'RESTART', 'title': 'Restart', 'desc': 'Add a restart point.' },
    { 'name': 'KOTH_CROWN', 'title': 'KOTH Crown', 'desc': 'Add a crown for KOTH games.' },
    { 'name': 'PEDESTRIAN', 'title': 'Pedestrian', 'desc': 'Add a new pedestrian.' },
    { 'name': 'VEHICLE', 'title': 'Vehicle', 'desc': 'Add a new vehicle.' },
    { 'name': 'RAIL_NODE', 'title': 'Rail Node', 'desc': 'Add a new rail with 2 points (no mesh).' },
    { 'name': 'RAIL_PREMADE', 'title': 'Premade Rail', 'desc': 'Add a new rail with 2 points and mesh.' },
    { 'name': 'RAIL_POINT', 'title': 'Point Rail', 'desc': 'Add a new rail with 1 point.' },
    { 'name': 'RAIL_POINT_PREMADE', 'title': 'Premade Point Rail', 'desc': 'Add a 1-point rail with a post.' },
    { 'name': 'WAYPOINT', 'title': 'Waypoint', 'desc': 'Add a waypoint path with 2 points.' },
    { 'name': 'LADDER', 'title': 'Ladder', 'desc': 'Add a climbing path with 2 points.' },
    { 'name': 'GAMEOBJECT', 'title': 'GameObject', 'desc': 'Add a new GameObject.' },
    
    { 'name': 'CTF_FLAG', 'title': 'CTF Flag', 'desc': 'Add a CTF Flag.' },
    { 'name': 'CTF_BASE', 'title': 'CTF Base', 'desc': 'Add a CTF Base.' },
    
    { 'name': 'PARTICLEOBJECT', 'title': 'Particle Emitter', 'desc': 'Add a Particle object.' },
    { 'name': 'CUBEMAP_PROBE', 'title': 'Reflection Probe', 'desc': 'Add a reflection probe' },
    { 'name': 'LIGHT_PROBE', 'title': 'Light Probe', 'desc': 'Add a light probe' },
    { 'name': 'LIGHT_VOLUME', 'title': 'Light Volume', 'desc': 'Add a light volume' },
]

preset_template_list = [
    { "name": "presets", "title": "Presets", "list": Preset_Pieces }
    , { "name": "sk5ed", "title": "Park Editor (UG+)", "list": Ed_Pieces_UG1 }
    , { "name": "sk6ed", "title": "Park Editor (THUG PRO)", "list": Ed_Pieces_UG2}
    , { "name": "sk4ed", "title": "Park Editor (THPS4)", "list": Ed_Pieces_THPS4}
    , { "name": "sk3ed_bch", "title": "Park Editor (THPS3)", "list": Ed_Pieces_THPS3}
]

# this holds the custom operators so we can cleanup when turned off
preset_nodes = []
preset_mesh = {}
mesh_submenus = []
mesh_categories = {}

def addPresetNodes():
    for node in preset_node_list:
        op_name = 'object.add_custom_' + node['name'].lower()
        nc = type(  'DynOp_' + node['name'],
                    (AddTHUGNode, ),
                    {'bl_idname': op_name,
                    'bl_label': node['title'],
                    'bl_description': node['desc'],
                    'node_type': node['name']
                })
        preset_nodes.append(nc)
        bpy.utils.register_class(nc)

def addPresetMesh():
    for template in preset_template_list:
        if not template["name"] in preset_mesh:
            preset_mesh[template["name"]] = {}
            mesh_categories[template["name"]] = []
            
            new_submenu = type(  'DynMenu_' + template["name"],
                        (THUGMeshSubMenu, ),
                        {'bl_idname': THUGMeshSubMenu.bl_idname + '_' + template["name"],
                        'bl_label': template["title"],
                        'template_name': template["name"]
                    })
            bpy.utils.register_class(new_submenu)
            mesh_submenus.append(new_submenu)
            
        for cat_name, category in template["list"].items():
            # Create the submenu for the category if it doesn't exist
            if not cat_name in preset_mesh:
                preset_mesh[template["name"]][cat_name] = []
                new_submenu = type(  'DynMenu_' + template["name"] + '_' + cat_name,
                        (THUGMeshSubSubMenu, ),
                        {'bl_idname': THUGMeshSubSubMenu.bl_idname + '_' + template["name"] + '_' + cat_name,
                        'bl_label': cat_name,
                        'template_name': template["name"],
                        'category_name': cat_name,
                    })
                bpy.utils.register_class(new_submenu)
                mesh_submenus.append(new_submenu)
                
            mesh_categories[template["name"]].append(cat_name) 
            for ob in category:
                # Single object definitions don't use "single" for the mesh name
                if "single" in ob:
                    piece_name = ob["single"]
                    op_name = 'object.add_custom_' + template["name"] + '_' + ob["single"].lower()
                    op_label = ob["single"]
                    if "text_name" in ob:
                        op_label = ob["text_name"]
                    
                    nc = type(  'DynOp_' + template["name"] + '_' + cat_name + '_' + ob["single"],
                                (AddTHUGMesh, ),
                                {'bl_idname': op_name,
                                'bl_label': op_label,
                                'bl_description': 'Add this piece to the scene.',
                                'template_name': template["name"],
                                'piece_name': ob["single"]
                            })
                    
                    preset_mesh[template["name"]][cat_name].append(nc)
                    bpy.utils.register_class(nc)

def clearPresetNodes():
    for c in preset_nodes:
        bpy.utils.unregister_class(c)
        
def clearPresetMesh():
    for template_name in preset_mesh:
        for category in preset_mesh[template_name]:
            for mesh_op in preset_mesh[template_name][category]:
                print("Unregistering: {}".format(mesh_op))
                try:
                    bpy.utils.unregister_class(mesh_op)
                except RuntimeError:
                    print("Unregister failed!")
                
    for menu in mesh_submenus:
        bpy.utils.unregister_class(menu)
        

# OPERATORS
#############################################
class AddTHUGNode(bpy.types.Operator):
    bl_idname = "mesh.thug_preset_addnode"
    bl_label = "Add Node"
    bl_description = "Base operator for adding custom objects"
    bl_options = {'REGISTER', 'UNDO'}

    node_type = bpy.props.StringProperty()

    def execute(self, context):
        preset_place_node(self.node_type, bpy.context.scene.cursor_location)
        return {'FINISHED'}
        
class AddTHUGMesh(bpy.types.Operator):
    bl_idname = "mesh.thug_preset_addmesh"
    bl_label = "Add Mesh"
    bl_description = "Base operator for adding custom mesh (usually CAP pieces)"
    bl_options = {'REGISTER', 'UNDO'}

    piece_name = bpy.props.StringProperty()
    template_name = bpy.props.StringProperty()

    def execute(self, context):
        preset_place_mesh(self.template_name, self.piece_name, bpy.context.scene.cursor_location)
        return {'FINISHED'}


# MENUS
#############################################
class THUGNodesMenu(bpy.types.Menu):
    bl_label = 'Nodes'
    bl_idname = 'mesh.thug_preset_nodes'

    def draw(self, context):
        layout = self.layout
        for o in preset_nodes:
            layout.operator(o.bl_idname)
            
class THUGMeshSubSubMenu(bpy.types.Menu):
    bl_label = 'Objects'
    bl_idname = 'mesh.thug_presetsubmenu'
    template_name = bpy.props.StringProperty()
    category_name = bpy.props.StringProperty()
    
    def draw(self, context):
        print("drawing mesh menu")
        layout = self.layout
        if self.template_name in preset_mesh:
            if self.category_name in preset_mesh[self.template_name]:
                for o in preset_mesh[self.template_name][self.category_name]:
                    layout.operator(o.bl_idname, icon='OBJECT_DATAMODE')
                    
                    
class THUGMeshSubMenu(bpy.types.Menu):
    bl_label = 'Objects'
    bl_idname = 'mesh.thug_presetmenu'
    template_name = bpy.props.StringProperty()
    
    def draw(self, context):
        print("drawing mesh menu")
        layout = self.layout
        if self.template_name in mesh_categories:
            for category_name in mesh_categories[self.template_name]:
                layout.menu(THUGMeshSubSubMenu.bl_idname + '_' + self.template_name + '_' + category_name, 
                icon='GROUP')
                    

class THUGMeshMenu(bpy.types.Menu):
    bl_label = 'Objects'
    bl_idname = 'mesh.thug_preset_pieces'

    def draw(self, context):
        print("drawing mesh menu")
        layout = self.layout
        for template_name in preset_mesh:
            for category in template_name:
                layout.menu(THUGMeshSubMenu.bl_idname + '_' + template_name + '_' + category)
                


class THUGPresetsMenu(bpy.types.Menu):
    bl_label = 'my materials'
    bl_idname = 'mesh.thug_presets'

    def draw(self, context):
        layout = self.layout

        layout.row().menu(THUGNodesMenu.bl_idname)
        layout.row().menu(THUGMeshSubMenu.bl_idname + '_' + 'presets')
        layout.row().menu(THUGMeshSubMenu.bl_idname + '_' + 'sk5ed')
        layout.row().menu(THUGMeshSubMenu.bl_idname + '_' + 'sk6ed')
        layout.row().menu(THUGMeshSubMenu.bl_idname + '_' + 'sk4ed')
        layout.row().menu(THUGMeshSubMenu.bl_idname + '_' + 'sk3ed_bch')