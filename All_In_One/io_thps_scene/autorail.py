import bpy
import bgl
import bmesh
import mathutils
from bpy.props import *
from pprint import pprint
from . import collision, helpers, qb
from . collision import update_triggered_by_ui_updater 
from . constants import *
from . helpers import *
from . import prefs

# PROPERTIES
#############################################
AUTORAIL_NONE = 0 # -2
AUTORAIL_AUTO = -1

# METHODS
#############################################

def get_path_bevel_size():
    addon_prefs = bpy.context.user_preferences.addons[ADDON_NAME].preferences
    return (2 * addon_prefs.path_bevel_size) / bpy.context.scene.thug_level_props.export_props.export_scale
    
def get_autorail_image():
    if bpy.data.images.get("Autorail_Metal"):
        return bpy.data.images.get("Autorail_Metal")
        
    addon_prefs = bpy.context.user_preferences.addons[ADDON_NAME].preferences
    base_files_dir_error = prefs._get_base_files_dir_error(addon_prefs)
    if base_files_dir_error:
        self.report({"WARNING"}, "Base files directory error: {} - Unable to find autorail texture, using color instead.".format(base_files_dir_error))
        size = 32, 32
        img = bpy.data.images.new(name="Autorail_Metal", width=size[0], height=size[1])
        img.generated_color = ( 0.1, 0.1, 0.1, 1.0 )
        img.use_fake_user = True
        return
    base_files_dir = addon_prefs.base_files_dir
    
    img = bpy.data.images.load(base_files_dir + "textures\\autorail_cap.png")
    img.name = "Autorail_Metal"
    img.use_fake_user = True
    return img
    
#----------------------------------------------------------------------------------
def get_autorail_material():
    if not bpy.data.materials.get('Autorail_Metal'):
        blender_mat = bpy.data.materials.new('Autorail_Metal') 
        blender_mat.use_transparency = True
        blender_mat.diffuse_color = (1, 1, 1)
        blender_mat.diffuse_intensity = 1
        blender_mat.specular_intensity = 0.25
        blender_mat.alpha = 1
        
        if bpy.data.textures.get("Autorail_Metal"):
            rail_tex = bpy.data.textures.get("Autorail_Metal")
        else:
            rail_tex = bpy.data.textures.new("Autorail_Metal", "IMAGE")
        rail_tex.image = get_autorail_image()
        rail_tex.thug_material_pass_props.blend_mode = 'vBLEND_MODE_DIFFUSE'
        tex_slot = blender_mat.texture_slots.add()
        tex_slot.texture = rail_tex
        tex_slot.uv_layer = str('Rail')
        tex_slot.blend_type = 'MIX'
        
    else:
        blender_mat = bpy.data.materials.get('Autorail_Metal') 
    return blender_mat
    

#----------------------------------------------------------------------------------
def build_rail_mesh(ob_rail, thickness = 2):
    if not ob_rail.data.splines:
        raise Exception("Object is not a rail path.")
        
    thickness = get_path_bevel_size()
    
    rail_path = ob_rail.data.splines[0]
    
    mesh_name = "OBJ_Rail0"
    rail_name_idx = 0
    # Create new rail path
    while mesh_name in bpy.data.objects:
        rail_name_idx += 1
        mesh_name = "OBJ_Rail" + str(rail_name_idx)
        #print("TRG_RailPath" + str(rail_name_idx))
        
    # Set up the path, which will be converted to mesh after
    curveData = bpy.data.curves.new(mesh_name, type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 12
    curveData.bevel_depth = thickness
    #curveData.bevel_resolution = 3
    curveData.bevel_resolution = 0
    curveData.fill_mode = 'FULL'
    polyline = curveData.splines.new('POLY')
    
    point_index = -1
    for pnt in rail_path.points:
        point_index += 1
        if point_index > 0:
            polyline.points.add()
        # Make the rail mesh slightly lower so we don't interfere with grinds
        point_world = ob_rail.matrix_world * pnt.co
        polyline.points[point_index].co = pnt.co - mathutils.Vector( [0, 0, curveData.bevel_depth, 0] )
        #print("Adding point {}".format(point_index))
        # Add post
        post_line = curveData.splines.new('POLY')
        post_line.points.add()
        post_line.points[0].co = ( pnt.co[0], pnt.co[1], 0, 0)
        post_line.points[1].co = pnt.co - mathutils.Vector( [0, 0, curveData.bevel_depth * 16, 0] )
        
    is_cyclic = False
    if rail_path.use_cyclic_u:
        is_cyclic = True
        polyline.use_cyclic_u = True
    polyline.use_smooth = True
    
    # create Object
    curveOB = bpy.data.objects.new(mesh_name, curveData)
    #for i, coord in enumerate(rail_nodes[0]):
    #    curveOB.data.thug_pathnode_triggers.add()
    # attach to scene and validate context
    
    # Now we have the path for the rail mesh, let's convert to mesh and assign materials!
    rail_mesh = curveOB.to_mesh(bpy.context.scene, True, 'PREVIEW')
    actual_ob = bpy.data.objects.new('Rail' + mesh_name, rail_mesh)
    bpy.context.scene.objects.link(actual_ob)
    bpy.context.scene.objects.active = actual_ob
    
    # Fill the gaps in the ends and assign mats
    if is_cyclic == False:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    # Add UV map
    bpy.ops.mesh.uv_texture_add({"object": actual_ob})
    actual_ob.data.uv_layers[len(actual_ob.data.uv_layers)-1].name = 'Rail'
    actual_ob.data.uv_textures['Rail'].active = True
    actual_ob.data.uv_textures['Rail'].active_render = True
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    #bpy.ops.uv.follow_active_quads()
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    #bpy.ops.uv.smart_project()
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    
    # Add Material
    actual_ob.data.materials.append(get_autorail_material())
    actual_ob.parent = ob_rail
    #Done! You should now have a decent-looking generated rail :)

#----------------------------------------------------------------------------------
def _update_pathnodes_collections():
    for ob in bpy.data.objects:
        if ob.type == "CURVE" and ob.thug_path_type in ("Rail", "Ladder", "Waypoint", "Custom"):
            tmp_idx = -1
            if len(ob.data.splines):
                for p in ob.data.splines[0].points:
                    tmp_idx += 1
                    if len(ob.data.thug_pathnode_triggers) < (tmp_idx + 1):
                            ob.data.thug_pathnode_triggers.add()
                            
#----------------------------------------------------------------------------------
# Handles the updating of points along a path node (rail, waypoint, etc)
# This event is fired from the WindowManager in scene_props.py
#----------------------------------------------------------------------------------
def update_pathnode(props, context):
    #print("Attempting to update pathnode data...")
    global update_triggered_by_ui_updater
    if update_triggered_by_ui_updater:
        #print("Triggered by UI updater")
        return
    if not context.edit_object:
        #print("Not in edit mode")
        return
    ob = context.edit_object
    wm = bpy.context.window_manager
    
    if ob.type == "CURVE" and ob.thug_path_type in ("Rail", "Ladder", "Waypoint", "Custom"):
        tmp_idx = -1
        if len(ob.data.splines):
            #print("Found curve data...")
            for sp in ob.data.splines:
                for p in sp.points:
                    tmp_idx += 1
                    # Add an entry to the pathnode_triggers list if it doesn't exist (new path point)
                    if len(ob.data.thug_pathnode_triggers) < (tmp_idx + 1):
                        ob.data.thug_pathnode_triggers.add()
                    # If this point is selected, set its properties with the wm pathnode_triggers data
                    if p.select:
                        #print("Found point: {}".format(tmp_idx))
                        print("Setting props on point {}: {}".format(tmp_idx, props.SkateAction))
                        ob.data.thug_pathnode_triggers[tmp_idx].name = props.name
                        ob.data.thug_pathnode_triggers[tmp_idx].script_name = props.script_name
                        if props.terrain != "":
                            ob.data.thug_pathnode_triggers[tmp_idx].terrain = props.terrain
                        ob.data.thug_pathnode_triggers[tmp_idx].spawnobjscript = props.spawnobjscript
                        ob.data.thug_pathnode_triggers[tmp_idx].PedType = props.PedType
                        ob.data.thug_pathnode_triggers[tmp_idx].do_continue = props.do_continue
                        ob.data.thug_pathnode_triggers[tmp_idx].JumpToNextNode = props.JumpToNextNode
                        if props.Priority != "":
                            ob.data.thug_pathnode_triggers[tmp_idx].Priority = props.Priority
                        if props.SkateAction != "":
                            ob.data.thug_pathnode_triggers[tmp_idx].SkateAction = props.SkateAction
                        ob.data.thug_pathnode_triggers[tmp_idx].JumpHeight = props.JumpHeight
                        ob.data.thug_pathnode_triggers[tmp_idx].Deceleration = props.Deceleration
                        ob.data.thug_pathnode_triggers[tmp_idx].SpinAngle = props.SpinAngle
                        ob.data.thug_pathnode_triggers[tmp_idx].RandomSpin = props.RandomSpin
                        ob.data.thug_pathnode_triggers[tmp_idx].SpineTransfer = props.SpineTransfer
                        if props.SpinDirection != "":
                            ob.data.thug_pathnode_triggers[tmp_idx].SpinDirection = props.SpinDirection
                        #return
                                
#----------------------------------------------------------------------------------
# Handles UI updates to path node data (rail, waypoint, etc)
# This ensures the data for the active point is passed to the WindowManager
#----------------------------------------------------------------------------------
@bpy.app.handlers.persistent
def update_pathnode_ui_properties(scene):
    global update_triggered_by_ui_updater
    if update_triggered_by_ui_updater:
        #print("Triggered by UI updater")
        return
    update_triggered_by_ui_updater = True
    try:
        ob = scene.objects.active
        if not ob or ob.mode != "EDIT" or ob.type != "CURVE" or not ob.thug_path_type in ("Rail", "Ladder", "Waypoint", "Custom"):
            return
        wm = bpy.context.window_manager
        tmp_idx = -1
        if len(ob.data.splines):
            #print("Attempting to update path node UI props...")
            for sp in ob.data.splines:
                for p in sp.points:
                    tmp_idx += 1
                    # Add an entry to the pathnode_triggers list if it doesn't exist (new path point)
                    if len(ob.data.thug_pathnode_triggers) < (tmp_idx + 1):
                        ob.data.thug_pathnode_triggers.add()
                    # If this point is selected, set its properties with the wm pathnode_triggers data
                    if p.select:
                        wm.thug_pathnode_props.name = ob.data.thug_pathnode_triggers[tmp_idx].name
                        wm.thug_pathnode_props.script_name = ob.data.thug_pathnode_triggers[tmp_idx].script_name
                        if ob.data.thug_pathnode_triggers[tmp_idx].terrain != "":
                            wm.thug_pathnode_props.terrain = ob.data.thug_pathnode_triggers[tmp_idx].terrain
                        wm.thug_pathnode_props.spawnobjscript = ob.data.thug_pathnode_triggers[tmp_idx].spawnobjscript
                        #wm.thug_pathnode_props.PedType = ob.data.thug_pathnode_triggers[tmp_idx].PedType
                        wm.thug_pathnode_props.do_continue = ob.data.thug_pathnode_triggers[tmp_idx].do_continue
                        wm.thug_pathnode_props.JumpToNextNode = ob.data.thug_pathnode_triggers[tmp_idx].JumpToNextNode
                        if ob.data.thug_pathnode_triggers[tmp_idx].Priority != "":
                            wm.thug_pathnode_props.Priority = ob.data.thug_pathnode_triggers[tmp_idx].Priority
                        if ob.data.thug_pathnode_triggers[tmp_idx].SkateAction != "":
                            wm.thug_pathnode_props.SkateAction = ob.data.thug_pathnode_triggers[tmp_idx].SkateAction
                        wm.thug_pathnode_props.JumpHeight = ob.data.thug_pathnode_triggers[tmp_idx].JumpHeight
                        wm.thug_pathnode_props.Deceleration = ob.data.thug_pathnode_triggers[tmp_idx].Deceleration
                        wm.thug_pathnode_props.SpinAngle = ob.data.thug_pathnode_triggers[tmp_idx].SpinAngle
                        wm.thug_pathnode_props.RandomSpin = ob.data.thug_pathnode_triggers[tmp_idx].RandomSpin
                        wm.thug_pathnode_props.SpineTransfer = ob.data.thug_pathnode_triggers[tmp_idx].SpineTransfer
                        if ob.data.thug_pathnode_triggers[tmp_idx].SpinDirection != "":
                            wm.thug_pathnode_props.SpinDirection = ob.data.thug_pathnode_triggers[tmp_idx].SpinDirection
                        break
        
    finally:
        update_triggered_by_ui_updater = False


    
#----------------------------------------------------------------------------------
def update_autorail_terrain_type(wm, context):
    global update_triggered_by_ui_updater
    if update_triggered_by_ui_updater:
        return
    if not context.edit_object:
        return
    bm = bmesh.from_edit_mesh(context.edit_object.data)

    arl = bm.edges.layers.int.get("thug_autorail")
    if not arl:
        if wm.thug_autorail_terrain_type == "None":
            return
        arl = bm.edges.layers.int.new("thug_autorail")
        for edge in bm.edges:
            edge[arl] = AUTORAIL_NONE

    for edge in bm.edges:
        if not edge.select:
            continue
        type_ = wm.thug_autorail_terrain_type
        edge[arl] = AUTORAIL_AUTO if type_ == "Auto" else \
                    AUTORAIL_NONE if type_ == "None" else \
                    TERRAIN_TYPES.index(wm.thug_autorail_terrain_type)

    bmesh.update_edit_mesh(context.edit_object.data)

#----------------------------------------------------------------------------------
def _resolve_autorail_terrain_type(ob, bm, edge, arl):
    if edge[arl] != AUTORAIL_AUTO:
        return edge[arl]

    lfs = list(edge.link_faces)
    if not lfs:
        return 0

    face_tt = collision._resolve_face_terrain_type(ob, bm, lfs[0])
    return TERRAIN_TYPES.index(TERRAIN_TYPE_TO_GRIND.get(TERRAIN_TYPES[face_tt], "DEFAULT"))


#----------------------------------------------------------------------------------
def _get_autorails(mesh_object, operator=None):
    from contextlib import ExitStack
    assert mesh_object.type == "MESH"
    ob = mesh_object

    all_autorails = []

    with ExitStack() as exit_stack:
        if mesh_object.modifiers:
            final_mesh = mesh_object.to_mesh(bpy.context.scene, True, 'PREVIEW')
            exit_stack.callback(bpy.data.meshes.remove, final_mesh)
        else:
            final_mesh = mesh_object.data

        bm = bmesh.new()
        exit_stack.callback(bm.free)

        bm.from_mesh(final_mesh)
        arl = bm.edges.layers.int.get("thug_autorail")
        if not arl: return []

        eligible_edges = set(bm.edges)

        # start_co = start.co.copy().freeze()

        while eligible_edges:
            root_edge = eligible_edges.pop()
            if root_edge[arl] == AUTORAIL_NONE:
                continue

            edge_beginning = root_edge.verts[0]
            edge_end = root_edge.verts[1]
            autorail_points = [AutorailPoint(
                ob.matrix_world * edge_beginning.co.copy(),
                _resolve_autorail_terrain_type(mesh_object, bm, root_edge, arl)
                )]

            # going forwards
            while True:
                forward_edge = None
                for edge in edge_end.link_edges:
                    if edge[arl] != AUTORAIL_NONE and edge in eligible_edges:
                        forward_edge = edge
                        eligible_edges.remove(forward_edge)

                if forward_edge:
                    if forward_edge.verts[0] == edge_end:
                        edge_beginning = forward_edge.verts[0]
                        edge_end = forward_edge.verts[1]
                    else:
                        edge_beginning = forward_edge.verts[1]
                        edge_end = forward_edge.verts[0]

                    autorail_points.append(AutorailPoint(
                        ob.matrix_world * edge_beginning.co.copy(),
                        _resolve_autorail_terrain_type(mesh_object, bm, forward_edge, arl)))
                else:
                    autorail_points.append(AutorailPoint(
                        ob.matrix_world * edge_end.co.copy(),
                        AUTORAIL_AUTO))
                    break
            forward_edge = None

            edge_beginning = root_edge.verts[0]
            edge_end = root_edge.verts[1]

            # going backwards
            while True:
                backward_edge = None
                for edge in edge_beginning.link_edges:
                    if edge[arl] != AUTORAIL_NONE and edge in eligible_edges:
                        backward_edge = edge
                        eligible_edges.remove(backward_edge)

                if backward_edge:
                    if backward_edge.verts[1] == edge_beginning:
                        edge_beginning = backward_edge.verts[0]
                        edge_end = backward_edge.verts[1]
                    else:
                        edge_beginning = backward_edge.verts[1]
                        edge_end = backward_edge.verts[0]

                    autorail_points = [(AutorailPoint(
                        ob.matrix_world * edge_beginning.co.copy(),
                        _resolve_autorail_terrain_type(mesh_object, bm, backward_edge, arl))),
                        *autorail_points]
                else:
                    break

            all_autorails.append(Autorail(autorail_points, ob))

    return all_autorails


#----------------------------------------------------------------------------------
def _try_merge_autorails(autorail, other_autorail):
    if autorail.is_cyclical():
        return False
    if other_autorail.is_cyclical():
        return False
    if autorail.next_merged:
        return False

    if not other_autorail.prev_merged:
        dist_between = (other_autorail.points[0].position - autorail.points[-1].position).length
        if dist_between < 0.25:
            autorail.next_merged = other_autorail
            other_autorail.prev_merged = autorail
            last_point = autorail.points.pop()
            other_autorail.points[0].position = (other_autorail.points[0].position + last_point.position) / 2
            return True

    if other_autorail.can_reverse():
        dist_between = (other_autorail.points[-1].position - autorail.points[-1].position).length
        if dist_between < 0.25:
            autorail.next_merged = other_autorail
            other_autorail.reverse()
            other_autorail.prev_merged = autorail
            last_point = autorail.points.pop()
            other_autorail.points[0].position = (other_autorail.points[0].position + last_point.position) / 2
            return True

#----------------------------------------------------------------------------------
def _export_autorails(p, c, i, v3, operator):
    import mathutils

    rail_node_counter = 0
    all_autorails = []
    for ob in bpy.data.objects:
        if ob.get("thug_autosplit_object_no_export_hack"):
            continue
        if ob.type == "MESH" and not ob.name.startswith("GEN_ShadowCaster_"):
            autorails = _get_autorails(ob, operator)
            all_autorails += autorails
    del ob

    autorail_tree = mathutils.kdtree.KDTree(len(all_autorails) * 2)
    autorail_idx = 0
    for autorail in all_autorails:
        autorail_tree.insert(autorail.points[0].position, autorail_idx)
        autorail_tree.insert(autorail.points[-1].position, autorail_idx + 1)
        autorail_idx += 2
    autorail_tree.balance()

    to_merge = list(all_autorails)
    while to_merge:
        autorail = to_merge.pop()
        if autorail.next_merged or autorail.is_cyclical():
            continue

        for other_autorail in (
            autorail_tree.find_range(autorail.points[ 0].position, 0.25) +
            autorail_tree.find_range(autorail.points[-1].position, 0.25)):
            other_autorail = all_autorails[other_autorail[1]//2]
            if autorail is other_autorail or other_autorail.is_cyclical():
                continue
            if _try_merge_autorails(autorail, other_autorail):
                #LOG.debug("Merged autorail {} ({}) with {} ({})".format(autorail, autorail.object, other_autorail, other_autorail.object))
                break

    output_offsets = {}
    while all_autorails:
        autorail = all_autorails.pop()

        while autorail:
            next_autorail = None
            beginning_node_index = rail_node_counter
            output_offsets[autorail] = beginning_node_index

            autorail_point_index = 0
            while autorail_point_index < len(autorail.points):
                autorail_point = autorail.points[autorail_point_index]
                obj_clean_name = get_clean_name(autorail.object)
                p("\t:i :s{")
                p("\t\t:i {} = {}".format(c("Pos"),
                    v3(mathutils.Vector(to_thug_coords(autorail_point.position)) + mathutils.Vector((0, 1, 0)))))
                p("\t\t:i {} = {}".format(c("Angles"), v3((0, 0, 0))))
                # name = "{}_AutoRailNode__{}".format(obj_clean_name, autorail_point_index) # rail_node_counter)
                name = "{}__AutoRailNode_{}".format(obj_clean_name, rail_node_counter)
                p("\t\t:i {} = {}".format(c("Name"), c(name)))
                p("\t\t:i {} = {}".format(c("Class"), c("RailNode")))
                p("\t\t:i {} = {}".format(c("Type"), c("Concrete")))
                p("\t\t:i {} = {}".format(c("CollisionMode"), c("Geometry")))
                autorail_type = autorail_point.terrain_type
                if autorail_type == AUTORAIL_AUTO:
                    autorail_type = "TERRAIN_GRINDCONC"
                else:
                    autorail_type = "TERRAIN_" + TERRAIN_TYPES[autorail_type]
                p("\t\t:i {} = {}".format(c("TerrainType"), c(autorail_type)))

                if getattr(autorail.object, "thug_is_trickobject", False):
                    p("\t\t:i call {} arguments".format(c("TrickObject")))
                    if autorail.object.thug_cluster_name:
                        cluster_name = autorail.object.thug_cluster_name
                    else:
                        cluster_name = get_clean_name(autorail.object)
                    p("\t\t\t{} = {}".format(c("Cluster"), c(cluster_name)))

                if autorail_point_index + 1 == len(autorail.points):
                    if autorail.is_cyclical():
                        links = [i(beginning_node_index)]
                    elif autorail.next_merged:
                        if autorail.next_merged in output_offsets:
                            links = [i(output_offsets[autorail.next_merged])]
                        else:
                            links = [i(rail_node_counter + 1)]

                            next_autorail = autorail.next_merged
                    else:
                        links = []
                else:
                    links = [i(rail_node_counter + 1)]

                # Bugfix: the park editor specifically does not like an empty array of Links (crashes), 
                # so only output the Links property if there are actually links
                if len(links):
                    p("\t\t:i {} = :a{{ {} :a}}".format(c("Links"), ' '.join(links)))
                if autorail.object.thug_created_at_start:
                    p("\t\t:i {}".format(c("CreatedAtStart")))
                p("\t:i :s}")
                rail_node_counter += 1
                autorail_point_index += 1

            if next_autorail:
                all_autorails.remove(next_autorail)
            autorail = next_autorail
    return rail_node_counter


#----------------------------------------------------------------------------------
def _export_rails(p, c, operator=None):
    def v3(v):
        return "%vec3({:6f},{:6f},{:6f})".format(*v)

    def i(integer):
        return "%i({},{:08})".format(integer, integer)
    def f(value):
        return "%f({})".format(value)

    rail_node_counter = _export_autorails(p, c, i, v3, operator)

    generated_scripts = {}
    custom_triggerscript_names = []

    obj_rail_node_start_offset_counter = rail_node_counter
    obj_rail_node_start_offsets = {}
    
    # Make a first pass through paths to get the node numbers, which are used when linking two paths together
    temp_rail_node_counter = rail_node_counter
    for ob in bpy.data.objects:
        if ob.type != "CURVE" or ob.thug_path_type not in ("Rail", "Ladder", "Waypoint"): 
            continue
        if ob.thug_path_type == "Custom" and ob.thug_node_expansion == "": 
            continue # Path with no class will break the game!
        obj_rail_node_start_offsets[ob.name] = temp_rail_node_counter
        for spline in ob.data.splines:
            temp_rail_node_counter += len(spline.points)

    # Actually export rails
    for ob in bpy.data.objects:
        if ob.type != "CURVE" or ob.thug_path_type not in ("Rail", "Ladder", "Waypoint"): 
            continue
        if ob.thug_path_type == "Custom" and ob.thug_node_expansion == "": 
            continue # Path with no class will break the game!
        
        clean_name = get_clean_name(ob)
        point_idx = 1
        first_node_idx = rail_node_counter
        for spline in ob.data.splines:
            points = spline.points
            point_count = len(points)
            p_num = -1
            for point in points:
                p_num += 1
                p("\t:i :s{")
                p("\t\t:i {} = {}".format(c("Pos"), v3(to_thug_coords(ob.matrix_world * point.co.to_3d()))))

                if ob.thug_path_type == "Rail":
                    p("\t\t:i {} = {}".format(c("Class"), c("RailNode")))
                    p("\t\t:i {} = {}".format(c("Type"), c("Concrete")))
                    p("\t\t:i {} = {}".format(c("Angles"), v3((0, 0, 0))))
                    name = "RailNode_" + str(rail_node_counter)
                elif ob.thug_path_type == "Ladder":
                    p("\t\t:i {} = {}".format(c("Class"), c("ClimbingNode")))
                    p("\t\t:i {} = {}".format(c("Type"), c("Ladder")))
                    p("\t\t:i {} = {}".format(c("Angles"), v3((0, ob.rotation_euler[2], 0))))
                    name = "LadderNode_" + str(rail_node_counter)
                elif ob.thug_path_type == "Waypoint":
                    p("\t\t:i {} = {}".format(c("Class"), c("Waypoint")))
                    #p("\t\t:i {} = {}".format(c("Type"), c("Default")))
                    p("\t\t:i {} = {}".format(c("Angles"), v3((0, 0, 0))))
                    if ob.thug_waypoint_props.waypt_type != "None":
                        p("\t\t:i {} = {}".format(c("Type"), c(ob.thug_waypoint_props.waypt_type)))
                    name = "Waypoint_" + str(rail_node_counter)
                elif ob.thug_path_type == "Custom":
                    p("\t\t:i {} = {}".format(c("Angles"), v3((0, 0, 0))))
                    name = "CustomPathNode_" + str(rail_node_counter)
                else:
                    assert False
                    
                # Insert individual node properties here, if they exist!
                if len(ob.data.thug_pathnode_triggers) > p_num:
                    # individual rail/path node names
                    if ob.data.thug_pathnode_triggers[p_num].name != "":
                        name = ob.data.thug_pathnode_triggers[p_num].name
                        p("\t\t:i {} = {}".format(c("Name"), c(name)))
                    else:
                        name = clean_name + "__" + str(point_idx - 1)
                        p("\t\t:i {} = {}".format(c("Name"), c(name)))
                            
                    if ob.thug_path_type == "Rail":
                        # Output terrain type - use either the whole rail definition or the 
                        # point-specific definition, depending on which one is set!
                        if ob.data.thug_pathnode_triggers[p_num].terrain != "" and ob.data.thug_pathnode_triggers[p_num].terrain != "None" and ob.data.thug_pathnode_triggers[p_num].terrain != "Auto":
                            # Terrain is also used for AI skaters, so don't output twice!
                            rail_type = ob.data.thug_pathnode_triggers[p_num].terrain
                        else:
                            rail_type = ob.thug_rail_terrain_type
                        
                        if rail_type == "Auto" or rail_type == "None":
                            rail_type = "TERRAIN_GRINDCONC"
                        else:
                            rail_type = "TERRAIN_" + rail_type
                        p("\t\t:i {} = {}".format(c("TerrainType"), c(rail_type)))
                        
                    # Output waypoint-specific data below!
                    elif ob.thug_path_type == "Waypoint" and ob.thug_waypoint_props.waypt_type != "None":
                        p("\t\t:i {} = {}".format(c("PedType"), c(ob.thug_waypoint_props.PedType)))
                        # Output skater AI node properties here!
                        if ob.thug_waypoint_props.PedType == "Skate":
                            # Skate action types defined here!
                            _skateaction = ob.data.thug_pathnode_triggers[p_num].SkateAction
                            # ---
                            if ob.data.thug_pathnode_triggers[p_num].Priority == "":
                                p("\t\t:i {} = {}".format(c("Priority"), c("Normal")))
                            else:
                                p("\t\t:i {} = {}".format(c("Priority"), c(ob.data.thug_pathnode_triggers[p_num].Priority)))
                            if _skateaction == "":
                                p("\t\t:i {} = {}".format(c("SkateAction"), c("Continue")))
                            else:
                                p("\t\t:i {} = {}".format(c("SkateAction"), c(_skateaction)))
                            # Output specific props depending on the skate action below
                            #if ob.data.thug_pathnode_triggers[p_num].do_continue:
                            p("\t\t:i {}".format(c("Continue")))
                            p("\t\t:i {} = {}".format(c("ContinueWeight"), f(1.0)))
                            if ob.data.thug_pathnode_triggers[p_num].JumpToNextNode:
                                p("\t\t:i {}".format(c("JumpToNextNode")))
                                if ob.data.thug_pathnode_triggers[p_num].JumpHeight == 0.0:
                                    p("\t\t:i {} = {}".format(c("JumpHeight"), f(75.0)))
                                else:
                                    p("\t\t:i {} = {}".format(c("JumpHeight"), f(ob.data.thug_pathnode_triggers[p_num].JumpHeight)))
                                if ob.data.thug_pathnode_triggers[p_num].SpinAngle > 0:
                                    p("\t\t:i {} = {}".format(c("SpinAngle"), f(ob.data.thug_pathnode_triggers[p_num].SpinAngle)))
                                    p("\t\t:i {} = {}".format(c("SpinDirection"), c(ob.data.thug_pathnode_triggers[p_num].SpinDirection)))
                            elif _skateaction == "Grind":
                                rail_type = ob.data.thug_pathnode_triggers[p_num].terrain
                                if rail_type == "Auto":
                                    rail_type = "TERRAIN_GRINDCONC"
                                else:
                                    rail_type = "TERRAIN_" + rail_type
                                p("\t\t:i {} = {}".format(c("TerrainType"), c(rail_type)))
                          
                                
                        # Walking ped logic goes here!
                        elif ob.thug_waypoint_props.PedType == "Walk":
                            p("\t\t:i {}".format(c("Continue")))
                            p("\t\t:i {} = {}".format(c("ContinueWeight"), f(1.0)))
                            if ob.data.thug_pathnode_triggers[p_num].Priority == "":
                                p("\t\t:i {} = {}".format(c("Priority"), c("Normal")))
                            else:
                                p("\t\t:i {} = {}".format(c("Priority"), c(ob.data.thug_pathnode_triggers[p_num].Priority)))
                            
                # No individual node properties are defined, so use the object-level settings    
                else:
                    name = clean_name + "__" + str(point_idx - 1)
                    p("\t\t:i {} = {}".format(c("Name"), c(name)))
                    # Generate terrain type using the object terrain settings
                    if ob.thug_path_type != "Custom" and ob.thug_path_type != "Waypoint" :
                        p("\t\t:i {} = {}".format(c("CollisionMode"), c("Geometry")))
                        rail_type = ob.thug_rail_terrain_type
                        if rail_type == "Auto":
                            rail_type = "TERRAIN_GRINDCONC"
                        else:
                            rail_type = "TERRAIN_" + rail_type
                        p("\t\t:i {} = {}".format(c("TerrainType"), c(rail_type)))

                # Other object-level properties defined here!
                if ob.thug_path_type != "Custom" and ob.thug_path_type != "Waypoint" :
                    if getattr(ob, "thug_is_trickobject", False):
                        p("\t\t:i call {} arguments".format(c("TrickObject")))
                        if ob.thug_cluster_name:
                            cluster_name = ob.thug_cluster_name
                        elif ob.parent and ob.parent.type == "MESH":
                            cluster_name = get_clean_name(ob.parent)
                        else:
                            cluster_name = name
                        p("\t\t\t{} = {}".format(c("Cluster"), c(cluster_name)))

                if ob.thug_node_expansion:
                    p("\t\t:i {}".format(c(ob.thug_node_expansion)))

                if ob.thug_created_at_start:
                    p("\t\t:i {}".format(c("CreatedAtStart")))

                # Select TriggerScripts to export below - basically, if there is a script defined
                # for the whole rail, then use that. Otherwise, use the point-specific setting
                if ob.thug_triggerscript_props.template_name_txt != "None" and ob.thug_triggerscript_props.template_name_txt != "":
                    if ob.thug_triggerscript_props.template_name_txt == "Custom":
                        script_name = format_triggerscript_name(ob.thug_triggerscript_props.custom_name)
                        custom_triggerscript_names.append(script_name)
                    else:
                        script_name, script_code = qb._generate_script(ob)
                        generated_scripts.setdefault(script_name, script_code)
                    p("\t\t:i {} = {}".format(c("TriggerScript"), c(script_name)))
                    
                # Export trigger script assigned to individual rail nodes (not entire rail)
                elif len(ob.data.thug_pathnode_triggers) > p_num and ob.data.thug_pathnode_triggers[p_num].script_name != "":
                    script_name = format_triggerscript_name(ob.data.thug_pathnode_triggers[p_num].script_name)
                    custom_triggerscript_names.append(script_name)
                        
                    p("\t\t:i {} = {}".format(c("TriggerScript"), c(script_name)))
                # - End TriggerScript generation code

                if point_idx != point_count:
                    p("\t\t:i {} = :a{{{}:a}}".format(c("Links"), i(rail_node_counter + 1)))
                elif spline.use_cyclic_u:
                    p("\t\t:i {} = :a{{{}:a}}".format(c("Links"), i(first_node_idx)))
                elif ob.thug_rail_connects_to:
                    if ob.thug_rail_connects_to not in bpy.data.objects:
                        operator.report({"ERROR"}, "Rail {} connects to nonexistent rail {}".format(ob.name, ob.thug_rail_connects_to))
                    else:
                        connected_to = bpy.data.objects[ob.thug_rail_connects_to]
                        if connected_to.name in obj_rail_node_start_offsets:
                            p("\t\t:i {} = :a{{{}:a}}".format(
                                c("Links"),
                                i(obj_rail_node_start_offsets[connected_to.name])))

                p("\t:i :s}")
                point_idx += 1
                rail_node_counter += 1

    return custom_triggerscript_names, generated_scripts, obj_rail_node_start_offsets




# OPERATORS
#############################################
class AutorailPoint:
    def __init__(self, position, terrain_type, trickobject_cluster=""):
        self.position = position
        self.terrain_type = terrain_type
        self.trickobject_cluster = trickobject_cluster
        # self.max_distance_for_merging = 0.25


class Autorail:
    def __init__(self, points, object=None):
        self.points = points
        self.object = object
        self.prev_merged = None
        self.next_merged = None

    def is_cyclical(self):
        return len(self.points) >= 2 and self.points[0].position == self.points[-1].position

    def can_reverse(self):
        return not self.prev_merged and not self.next_merged

    def reverse(self):
        assert self.can_reverse()
        reversed_points = []
        if len(self.points) == 1:
            return

        i = len(self.points) - 1
        while i >= 0:
            point = self.points[i]
            prev_point = None if i - 1 < 0 else self.points[i]
            if prev_point:
                point.terrain_type = prev_point.terrain_type
            else:
                point.terrain_type = AUTORAIL_AUTO
            reversed_points.append(point)
            i -= 1

        self.points = reversed_points

class MarkAutorail(bpy.types.Operator):
    bl_idname = "mesh.thug_mark_autorail"
    bl_label = "Mark Rail"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.object.type == "MESH"

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        arl = bm.edges.layers.int.get("thug_autorail")

        if not arl:
            arl = bm.edges.layers.int.new("thug_autorail")
            for edge in bm.edges:
                edge[arl] = AUTORAIL_NONE

        for edge in bm.edges:
            if edge.select:
                edge[arl] = AUTORAIL_AUTO

        bmesh.update_edit_mesh(context.object.data)

        return {'FINISHED'}


class ClearAutorail(bpy.types.Operator):
    bl_idname = "mesh.thug_clear_autorail"
    bl_label = "Clear Rail"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.object.type == "MESH"

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        arl = bm.edges.layers.int.get("thug_autorail")
        if not arl:
            return {'FINISHED'}

        for edge in bm.edges:
            if edge.select:
                edge[arl] = AUTORAIL_NONE
        bmesh.update_edit_mesh(context.object.data)

        return {'FINISHED'}


class ExtractRail(bpy.types.Operator):
    bl_idname = "object.thug_extract_rail"
    bl_label = "Extract Rail"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.object.type == "MESH"

    def execute(self, context):
        # If the current edge(s) are marked as rails, clear them so we don't get duplicate rails!
        bpy.ops.mesh.thug_clear_autorail('EXEC_DEFAULT')
        old_object = context.object
        bpy.ops.mesh.duplicate()
        before = set(bpy.data.objects)
        bpy.ops.mesh.separate()
        after = set(bpy.data.objects)
        new_object = list(after - before)[0]
        new_name_idx = 0
        new_name = "RailPath0"
        while new_name in bpy.data.objects:
            new_name_idx += 1
            new_name = "RailPath" + str(new_name_idx)
        new_object.name = new_name
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all()
        new_object.select = True
        context.scene.objects.active = new_object
        bpy.ops.object.convert(target='CURVE')
        new_object.parent = old_object
        new_object.matrix_parent_inverse = old_object.matrix_basis.inverted()
        new_object.thug_path_type = "Rail"
        
        # Configure bevels and materials to match imported rails and placed presets!

        new_object.data.dimensions = '3D'
        new_object.data.resolution_u = 12
        new_object.data.bevel_depth = get_path_bevel_size()
        new_object.data.bevel_resolution = 2
        new_object.data.fill_mode = 'FULL'
        rail_mat = helpers.get_material('io_thps_scene_RailMaterial')
        new_object.data.materials.append(rail_mat)

        
        return {"FINISHED"}

        
class AutoRailMesh(bpy.types.Operator):
    bl_idname = "path.thug_generate_rail_mesh"
    bl_label = "Create Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object.type == "CURVE"

    def execute(self, context):
        if context.selected_objects:
            for ob in context.selected_objects:
                build_rail_mesh(ob)
        return {'FINISHED'}

        
class UpdateRails(bpy.types.Operator):
    bl_idname = "path.thug_update_rails"
    bl_label = "Update Rails/Paths"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object.type == "CURVE"

    def execute(self, context):
        _update_pathnodes_collections()
        return {'FINISHED'}

