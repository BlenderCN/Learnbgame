#############################################
# THUG1/2 PRK (.prk) IMPORT
#############################################
import bpy
import bmesh
import struct
import mathutils
import math
from bpy.props import *
from . helpers import *
from . material import *
from . pieces import *
from . autorail import *
from . presets import *
import fnmatch

# Park piece rotation constants
ROTATE_0 = 0
ROTATE_90 = 1
ROTATE_180 = 2
ROTATE_270 = 3

# METHODS
#############################################
def parked_place_piece(version, piece_name, loc_x, loc_y, loc_z, angle, add_rails = True):
    scene = bpy.context.scene
    append_scene = 'sk5ed'
    if version == 6:
        append_scene = 'sk6ed'
        
    new_piece = append_from_dictionary(append_scene, piece_name, scene, True, add_rails)
    if new_piece == None:
        append_scene = 'sk5ed'
        new_piece = append_from_dictionary(append_scene, piece_name, scene, True, add_rails)
    if new_piece == None:
        raise Exception("Unable to locate piece {} from dictionary scene {}.".format(piece_name, append_scene))
        
    new_piece.location[0] = loc_y * 120
    new_piece.location[1] = loc_x * 120
    new_piece.location[2] = loc_z * 48
    new_piece.hide = False
    new_piece.hide_render = False
    #new_piece.thug_export_scene = True
    #new_piece.thug_export_collision = True
    
    final_angle = (angle + 4) & 3
    dimensions = [ new_piece.dimensions.x, new_piece.dimensions.y ]
    if dimensions[0] < 120:
        dimensions[0] = 120
    if dimensions[1] < 120:
        dimensions[1] = 120
    
    if final_angle == ROTATE_90 or final_angle == ROTATE_270:
        new_piece.location[0] += dimensions[0] / 2
        new_piece.location[1] += dimensions[1] / 2
    else:
        new_piece.location[0] += dimensions[1] / 2
        new_piece.location[1] += dimensions[0] / 2
    
    new_piece.rotation_euler[2] = math.radians((90.0 * (final_angle + 2)) - 90)
    return new_piece
    
def get_composite_piece(piece_name, version):
    piece_data = {}
    found = False
    pieces = []
    piece_list = Ed_Pieces_UG1
    if version == 6:
        piece_list = Ed_Pieces_UG2
        
    for cat_name, category in piece_list.items():
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
    #print(piece_data)
    return piece_data

def build_floor_grid(version, grid_data):
    grid_count = -1
    for x in range(0, 58):
        for y in range(0, 58):
            grid_count += 1
            loc_x = x
            loc_y = y
            loc_z = grid_data[grid_count][0]
            # Walls are not stored in the save file, so we need to build those here!
            # riser pieces:
            #
            # Sk3Ed_Rd1b_10x10x4 - underground bottom (> 1 square)
            # Sk3Ed_Rd1m_10x10x4 - underground wall (> 1 square)
            # Sk3Ed_Rd1s_10x10x4 - underground wall (1 square)
            # Sk3Ed_Rd1t_10x10x4 - underground wall top (> 1 square)
            #
            # Sk3Ed_Ru1s_10x10x4 - riser wall (1 square)
            # Sk3Ed_Ru1b_10x10x4 - riser wall bottom (> 1 square)
            # Sk3Ed_Ru1m_10x10x4 - riser wall mid (> 1 square)
            # Sk3Ed_Ru1t_10x10x4 - riser wall top (> 1 square)
            #
            #
            #
            #
            riser_pieces = []
            for i in range(0, loc_z):
                # Determine the riser piece we want based on the height
                #print("i = {}, loc_z = {}".format(i, loc_z))
                if i == 0:
                    if loc_z == 1:
                        riser_name = 'Sk3Ed_Ru1s_10x10x4'
                    else:
                        riser_name = 'Sk3Ed_Ru1b_10x10x4'
                elif (i == (loc_z -1) and loc_z > 1):
                    riser_name = 'Sk3Ed_Ru1t_10x10x4'
                elif i > 0:
                    riser_name = 'Sk3Ed_Ru1m_10x10x4'
                elif i == -1:
                    if loc_z == -1:
                        riser_name = 'Sk3Ed_Rd1s_10x10x4'
                    else:
                        riser_name = 'Sk3Ed_Rd1b_10x10x4'
                elif i == -15:
                    riser_name = 'Sk3Ed_Rd1b_10x10x4'
                elif i < 0: 
                    riser_name = 'Sk3Ed_Rd1m_10x10x4'
                    
                riser_pieces.append(parked_place_piece(version, riser_name, loc_x, loc_y, i, 0, False))
            #bpy.ops.object.select_all(action='DESELECT')
            #for ob in riser_pieces:
            #    bpy.context.scene.objects.active = ob
            #    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            #    ob.select = True
            #bpy.ops.object.join()
            parked_place_piece(version, 'Sk3Ed_Fd1_10x10', loc_x, loc_y, loc_z, 0, False)
            

    
def import_prk(filename, directory, context, operator):
    p = Printer()
    p.on = True
    input_file = os.path.join(directory, filename)
    with open(input_file, "rb") as inp:
        r = Reader(inp.read())

    # Read the header for the park save to gather basic info about it, then read the actual
    # pieces and rail blocks which we are interested in
    prk_checksum = r.u32()
    values_checksum = r.u32()
    values_size = r.u32()
    r.u32() # Offset to padding
    version = p("version: {}", r.u32()) # Version (5 for THUG1, 6 for THUG2)
    r.u8()
    r.u32() # num_edited_goals
    num_edited_goals = p("num_edited_goals: {}", r.u8())
    r.u32() # MaxPlayers
    max_players = p("max_players: {}", r.u8())
    r.u8()
    r.u32() # num_gaps
    # num_gaps is not included when there are no gaps, so we just 
    # check for the 0x35 marker from the num_pieces checksum
    # We don't care how many there are anyway, so we don't need to store it
    while (r.u8() != 0x35):
        continue
    r.offset -= 1
    r.u32() # num_pieces
    num_pieces = p("num_pieces: {}", r.u16())
    r.u8()
    r.u32() # theme
    theme = p("theme: {}", r.u8())
    r.u32() # tod_script
    tod_script = p("tod_script: {}", r.u32())
    r.u32() # park dimensions, not needed
    r.u32() # length 
    r.u16() # length 
    r.u32() # Filename 
    park_name = ''
    name_bytes = []
    while (r.u8() != 0x00):
        r.offset -= 1
        name_bytes.append(chr(r.u8()))
        park_name = ''.join(name_bytes)
    p("park_name: {}", park_name)
    
    r.u16()
    r.u32() # Park_editor_map 
    r.u8() 
    r.u16() # padding 
    
    p("park data checksum: {}", r.u32())
    parkdata_offset = r.offset
    parkdata_size = p("section size: {}", r.u16())
    r.u16() # padding 
    park_theme = p("theme: {}", r.u16())  
    r.u16() # padding 
    park_position = [ r.u8(), r.u8() ] 
    park_size = [ r.u8(), r.u8() ]
    num_pieces = p("num_pieces: {}", r.u16())  
    num_gaps = p("num_gaps: {}", r.u16())  
    max_players = p("max_players: {}", r.u8())  
    r.read("7B") # Unknown section/padding right before park name
    
    # Park name from the actual park data - this is always 64 bytes even though it is
    # null terminated, we need to read all 64 bytes for the following ground map to be accurate
    park_name2 = ''
    name_bytes2 = []
    for n in range(0, 64):
        name_bytes2.append(chr(r.u8()))
        park_name2 = ''.join(name_bytes)
    p("park_name2: {}", park_name2)
    
    # Set up the ground mapping - tells us what height each square on the grid is at
    # Values away from 0 are risers, away from 255 are sunken ground
    ground_x = 58
    ground_y = 58
    riser_data = []
    # Ground data starts here - x=0 y=0, x=0 y=1, and so on
    for i in range(0, ground_x):
        for j in range(0, ground_y):
            riser_data.append(r.read("b"))
            
    print("****************************************************")
    print("Riser data processed! Moving onto park pieces...")
    print("****************************************************")
    
    for p in range(0, num_pieces):
        piece_data = r.u32()
        piece_data2 = r.u32()
        # Don't actually import the piece if the option is disabled
        if operator.import_pieces == False:
            continue
        piece_index = piece_data & 1023
        piece_pos_x = (piece_data >> 10) & 255
        piece_pos_y = (piece_data >> 18) & 255
        piece_pos_z = ((piece_data2 >> 2) & 31) - 16
        piece_rotation = piece_data2 & 3
        
        if version == 5:
            piece_name = Ed_Save_Map_UG1[piece_index]
        elif version == 6:
            piece_name = Ed_Save_Map_UG2[piece_index]
        else:
            raise Exception("Version #{} is not supported by the CAP save importer.".format(version))
            
        if not piece_name or piece_name == None:
            print("--------------------------")
            print("Piece index {} was not found in list!".format(piece_index))
            print("--------------------------")
            continue
            
        ob_piece = get_composite_piece(piece_name, version)
            
        for pc in ob_piece["pieces"]:
            print("Piece {}".format(pc["name"]))
            if piece_rotation == ROTATE_0:
                translated_pos = [ piece_pos_x + pc["pos"][0], piece_pos_y + pc["pos"][2], piece_pos_z + pc["pos"][1] ]
            
            elif piece_rotation == ROTATE_90:
                translated_pos = [ piece_pos_x + pc["pos"][2], piece_pos_y + pc["pos"][0], piece_pos_z + pc["pos"][1] ]
            
            elif piece_rotation == ROTATE_180:
                translated_pos = [ piece_pos_x + pc["pos"][0], piece_pos_y + pc["pos"][2], piece_pos_z + pc["pos"][1] ]
            
            elif piece_rotation == ROTATE_270:
                translated_pos = [ piece_pos_x + pc["pos"][2], piece_pos_y + pc["pos"][0], piece_pos_z + pc["pos"][1] ]
                
            extra_rotation = 0
            if len(pc["pos"]) > 3:
                # The fourth Position element in a composite piece is rotation, apply that here
                extra_rotation = pc["pos"][3]
                
            #print("Pos x/y/z: {} {} {}".format(translated_pos[0], translated_pos[1], translated_pos[2]))
            #print("Rotation: {}".format(piece_rotation))
            #print("--------------------------")
            parked_place_piece(version, pc["name"], translated_pos[0], translated_pos[1], translated_pos[2], (piece_rotation + extra_rotation), False)
        
    empty_slots = (1443 - num_pieces)
    print("Empty piece slots: {}".format(empty_slots))
    for x in range(0, empty_slots):
        r.read("8B")
        #piece_data = r.u32()
        #piece_data2 = r.u32()
        # These are empty slots - the format always stores one piece per grid square
    #r.offset = parkdata_offset
    #r.offset += parkdata_size
        
    print("I am at offset: {}".format(r.offset))
    
    # Don't actually import the piece if the option is disabled
    if operator.import_floors:
        print("****************************************************")
        print("Park data processed! Building floor/riser grid...")
        print("****************************************************")
            #p_meta->SetRot(Mth::ERot90(rot));
        build_floor_grid(version, riser_data)   
    
    
    if operator.import_rails == False:
        print("****************************************************")
        print("Import complete! Have fun :)")
        print("****************************************************")
        return
        
    print("****************************************************")
    print("Complete! Building rails...")
    print("****************************************************")
    r.u8() # padding
    r.u32() # park_editor_goals
    r.u8() 
    r.u32() # goals
    r.u32() # padding - normally goals go here, but this section is undocumented :(
    r.u8() 
    r.u32() # createdrails
    r.u8() 
    num_rails = r.u16()
    print("num_rails: {}".format(num_rails))
    # Loop over each rail and grab the points
    for rail in range(0, num_rails):
        r.u8() #0x0C
        r.u32() # points 
        r.u8() #0x0A
        num_points = r.u16()
        if num_points > 100:
            raise Exception("Invalid rail data at {}".format(r.offset))
            
        print("num_points: {}".format(num_points)) 
        print("-------------------")
        print("RAIL #{} OF {}".format(rail, num_rails))
        
        rail_path_name = "TRG_RailPath0"
        rail_name_idx = 0
        # Create new rail path
        while rail_path_name in bpy.data.objects:
            rail_name_idx += 1
            rail_path_name = "TRG_RailPath" + str(rail_name_idx)
            #print("TRG_RailPath" + str(rail_name_idx))
        
        print("Creating rail ")
        curveData = bpy.data.curves.new(rail_path_name, type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 12
        curveData.bevel_depth = get_path_bevel_size()
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(num_points - 1)
                
        # Parse rail points
        for pnt in range(0, num_points):
            r.u8() #0x06
            r.u32() # pos 
            pnt_pos = r.read("3f")
            print("Rail point #{}: {}".format(pnt, pnt_pos))
            x,y,z = pnt_pos
            polyline.points[pnt].co = (z+3480, x+3480, y, 1)
            
            if r.u8() == 0: 
                continue
            r.u32() # 00 00 00 00
            r.u32() # haspost
            r.u8() # padding
    
        r.u8() # padding... ?
         
        # create Object
        curveOB = bpy.data.objects.new(rail_path_name, curveData)
        curveOB.thug_path_type = "Rail"
        curveOB.thug_rail_terrain_type = "GRINDMETAL"
        #for i, coord in enumerate(rail_nodes[0]):
        #    curveOB.data.thug_pathnode_triggers.add()
        # attach to scene and validate context
        bpy.context.scene.objects.link(curveOB)
        bpy.context.scene.objects.active = curveOB
        build_rail_mesh(curveOB)
    #read_prk_sections(r, p, num_sectors, context, operator)
    
    print("****************************************************")
    print("Import complete! Have fun :)")
    print("****************************************************")
    
#----------------------------------------------------------------------------------


# OPERATORS
#############################################
class ImportTHUGPrk(bpy.types.Operator):
    bl_idname = "io.thug_prk_generate_scene"
    bl_label = "THUG1/2 Custom Park (.prk)"
    # bl_options = {'REGISTER', 'UNDO'}

    filter_glob = StringProperty(default="*.prk", options={"HIDDEN"})
    filename = StringProperty(name="File Name")
    directory = StringProperty(name="Directory")
    import_floors = BoolProperty(name="Generate Floor/Risers", default=True)
    import_pieces = BoolProperty(name="Import Pieces", default=True)
    import_rails = BoolProperty(name="Import Rails", default=True)

    def execute(self, context):
        filename = self.filename
        directory = self.directory

        import_prk(filename, directory, context, self)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}
