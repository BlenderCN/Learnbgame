import bpy
from bpy.props import FloatVectorProperty, BoolProperty, FloatProperty, StringProperty, IntProperty, EnumProperty
from math import sqrt, radians, atan, degrees
from random import uniform, choice, random
from mathutils import Euler, Vector
from . jarch_materials import *
import bmesh
from . jarch_utils import object_rotation, object_dimensions, point_rotation

#manages sorting out which type of siding needs to be create, gets corner data for cutout objects
def create_siding(context, mat, if_tin, if_wood, if_vinyl, is_slope, ow, oh, bw, slope, is_width_vary, width_vary, 
        is_cutout, num_cutouts, nc1, nc2, nc3, nc4, nc5, baw, bs, is_length_vary, length_vary, max_boards, b_w, 
        b_h, b_offset, b_gap, m_d, b_ran_offset, b_vary, is_corner, is_invert, is_soldier,  is_left, is_right, 
        avw, avh, s_random, b_random, x_off):

    #percentages
    width_vary = 1 / (100 / width_vary)
    length_vary = 1 / (100 / length_vary)   
    
    #evaluate cutouts
    cutouts = []
    if is_cutout == True:
        if nc1 != "" and num_cutouts >= 1:
            add = nc1.split(",")
            cutouts.append(add)
        if nc2 != "" and num_cutouts >= 2:
            add = nc2.split(",")
            cutouts.append(add)
        if nc3 != "" and num_cutouts >= 3:
            add = nc3.split(",")
            cutouts.append(add)
        if nc4 != "" and num_cutouts >= 4:
            add = nc4.split(",")
            cutouts.append(add)
        if nc5 != "" and num_cutouts >= 5:
            add = nc5.split(",")
            cutouts.append(add)
    cuts = [] #create list of data if cutout has correct info and is numbers
    for i in cutouts:
        pre = []
        skip = False
        if len(i) == 4:
            for i2 in i:
                try:
                    if bpy.context.scene.unit_settings.system == "IMPERIAL":
                        i2 = round(float(i2) / 3.28084, 5)
                    else:
                        i2 = float(i2)
                    pre.append(i2)
                except:
                    skip = True
        if skip == False and pre != []:
            cuts.append(pre)
    #determine corner points
    corner_data = []; corner_data_l = []
    for i in cuts:
        cut = []        
        cut.append(i[0]); cut.append(i[1]) #Start X & Z
        cut.append(i[0] + i[3]); cut.append(i[1] + i[2]) #Bottom > Right & Top > Left
        corner_data.append(cut)
        if is_soldier == True:
            cut2 = []; cut2.append(i[0]); cut2.append(i[1])
            cut2.append(i[0] + i[3]); cut2.append(i[1] + i[2] + b_w + b_gap)
            corner_data_l.append(cut2)
    #verts and faces
    verts = []; faces = []
    v = []; f = []
    
    #Wood
    if mat == "1" and if_wood == "1": #Wood > Vertical
        data_back = wood_vertical(oh, ow, is_slope, slope, is_width_vary, width_vary, bw, verts, faces, bs, is_length_vary, length_vary, max_boards)
        verts = data_back[0]; faces = data_back[1]              
    elif mat == "1" and if_wood == "2": #Wood > Vertical: Tongue & Groove
        data_back = wood_ton_gro(oh, ow, is_slope, slope, bw, verts, faces, is_length_vary, length_vary, max_boards)
        verts = data_back[0]; faces = data_back[1]
    elif mat == "1" and if_wood == "3": #Wood > Vertical: Board & Batten
        data_back = wood_vertical(oh, ow, is_slope, slope, False, width_vary, bw, verts, faces, 0.00635, is_length_vary, length_vary, max_boards)
        verts = data_back[0]; faces = data_back[1]
        batten_pos = data_back[2]
        #add battens
        if is_slope == True:
            z_dif = round(((slope * baw) / 12), 5)
        else:
            z_dif = 0.0
        p = len(v) 
        c = 0.00635 / 2
        for i in batten_pos[1]:
            if (bw / 2) - (0.125 / 39.3701) < baw / 2:
                baw = 2 * (bw / 2) - (0.125 / 39.3701)
            is_center = False
            cur_x = (i[0] + c) - (baw / 2)
            s_dif = (slope * (i[0] - cur_x)) / 12
            cur_z = i[1]
            if is_slope == True:
                if  cur_x < ow / 2:
                    cur_z -= s_dif
                else:
                    cur_z += s_dif
            if cur_x + baw < ow:
                p = len(v)
                v.append((cur_x, -0.02539, 0.0)); v.append((cur_x, -0.04444, 0.0)) #Bottom > Left
                v.append((cur_x + baw, -0.04444, 0.0)); v.append((cur_x + baw, -0.02539, 0.0)) #Bottom > Right
                v.append((cur_x, -0.02539, cur_z)); v.append((cur_x, -0.04444, cur_z)) #Top > Left
                if is_slope == False: #flat
                    v.append((cur_x + baw, -0.04444, oh)); v.append((cur_x + baw, -0.02539, oh)) #Top > Right 
                elif is_slope == True:  
                    if cur_x < ow /2 and cur_x + baw < ow / 2: #slope up
                        v.append((cur_x + baw, -0.04444, cur_z + z_dif)); v.append((cur_x + baw, -0.02539, cur_z + z_dif)) #Top > Right
                    elif cur_x < ow / 2 and cur_x + baw > ow / 2: #middle board
                        del v[len(v) - 1]; del v[len(v) - 1] #remove top > right set         
                        v.insert(len(v) - 2, (ow / 2, -0.04444, 0.0)); v.insert(len(v) - 2, (ow / 2, -0.02539, 0.0)) #insert bottom middle set
                        z_pos = oh - ((slope * ((ow / 2) - cur_x)) / 12) #figure out whats on left and calculate height
                        v.append((cur_x, -0.02539, z_pos)); v.append((cur_x, -0.04444, z_pos)) #Top > Left
                        v.append((ow / 2, -0.04444, oh)); v.append((ow / 2, -0.02539, oh)) #Top > Middle
                        z_pos = oh - ((slope * ((cur_x + baw) - (ow / 2))) / 12) #figure out what on right and calculate height
                        v.append((cur_x + baw, -0.04444, z_pos)); v.append((cur_x + baw, -0.02539, z_pos)); is_center = True #Top > Right
                    elif cur_x > ow / 2: #slope down
                        v.append((cur_x + baw, -0.04444, cur_z - z_dif)); v.append((cur_x + baw, -0.02539, cur_z - z_dif)) #Top > Right
                if is_center == False:
                    a = ((p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7), (p, p + 1, p + 5, p + 4), (p + 1, p + 2, p + 6, p + 5),
                            (p + 2, p + 3, p + 7, p + 6), (p, p + 4, p + 7, p + 3))
                    for i in a:
                        f.append(i)   
                else:
                    a = ((p, p + 4, p + 7, p + 3), (p + 2, p + 3, p + 5, p + 4), (p + 6, p + 7, p + 8, p + 9), (p + 8, p + 10, p + 11, p + 9),
                            (p, p + 1, p + 7, p + 6), (p + 1, p + 2, p + 8, p + 7), (p + 2, p + 4, p + 10, p + 8), (p + 4, p + 5, p + 11, p + 10),
                            (p, p + 6, p + 9, p + 3), (p + 3, p + 9, p + 11, p + 5))
                    for i in a:
                        f.append(i)
    elif mat == "1" and if_wood == "4": #Wood > Horizontal: Lap
        data_back = wood_lap(oh, ow, is_slope, slope, bw, verts, faces, is_length_vary, length_vary, max_boards, 0.02540)
        verts = data_back[0]; faces = data_back[1]
    elif mat == "1" and if_wood == "5": #Wood > Horizontal: Lap Bevel
        data_back = wood_lap_bevel(oh, ow, is_slope, slope, bw, is_length_vary, length_vary, faces, verts, max_boards)
        verts = data_back[0]
        faces = data_back[1]
    #Vinyl
    elif mat == "2" and if_vinyl == "1": #Vinyl > Vertical
        data_back = vinyl_vertical(oh, ow, is_slope, slope, is_length_vary, length_vary, bw, baw, faces, verts, max_boards)
        verts = data_back[0]; faces = data_back[1]
    elif mat == "2" and if_vinyl == "2": #Vinyl > Horizontal: Lap
        data_back = vinyl_lap(oh, ow, is_slope, slope, is_length_vary, length_vary, bw, faces, verts, max_boards)
        verts = data_back[0]; faces = data_back[1]
    elif mat == "2" and if_vinyl == "3": #EVinyl > Horizontal: Dutch Lap
        data_back = vinyl_dutch_lap(oh, ow, is_slope, slope, is_length_vary, length_vary, bw, faces, verts, max_boards)
        verts = data_back[0]; faces = data_back[1]
    #Tin
    elif mat == "3" and if_tin == "1": #Tin > Normal
        data_back = tin_normal(oh, ow, is_slope, slope, faces, verts)
        verts = data_back[0]; faces = data_back[1]
    elif mat == "3" and if_tin == "2": #Tin > Angular
        data_back = tin_angular(oh, ow, is_slope, slope, faces, verts)
        verts = data_back[0]; faces = data_back[1]
    #Fiber Cement
    elif mat == "4": #Fiber Cement > Horizontal: Half-Lap
        data_back = wood_lap(oh, ow, is_slope, slope, bw, verts, faces, is_length_vary, length_vary, max_boards, 0.009525)
        verts = data_back[0]; faces = data_back[1]
    #Bricks
    elif mat == "5": #Bricks
        data_back = bricks(oh, ow, is_slope, slope, b_w, b_h, b_offset, b_gap, b_ran_offset, b_vary, faces, verts, is_corner, is_invert, is_left, is_right)
        verts = data_back[0]; faces = data_back[1]
    #Stone
    elif mat == "6": #Stone
        data_back = stone_faces(oh, ow, avw, avh, s_random, b_random, b_gap)
        verts = data_back[0]; faces = data_back[1]   
    
    #adjust for x_offset
    out_verts = []; out_v = []
    for i in verts:
        l = list(i); l[0] += x_off
        out_verts.append(l)
    for i in v:
        l = list(i); l[0] += x_off
        out_v.append(l)
    return (out_verts, faces, corner_data, corner_data_l, out_v, f)   

def bool(corner_data): #creates list of vertices and faces for all the cutout objects
    verts = []; faces = [] #Verts and Faces
    for ob in corner_data:
        p = len(verts)
        verts.append((ob[0], 0.5, ob[1])); verts.append((ob[0], -0.5, ob[1])) #Bottom > Left
        verts.append((ob[2], -0.5, ob[1])); verts.append((ob[2], 0.5, ob[1])) #Bottom > Right
        verts.append((ob[0], 0.5, ob[3])); verts.append((ob[0], -0.5, ob[3])) #Top > Left
        verts.append((ob[2], -0.5, ob[3])); verts.append((ob[2], 0.5, ob[3])) #Top > Right
        faces.append((p, p + 3, p + 2, p + 1)); faces.append((p + 4, p + 5, p + 6, p + 7)) #Top & Bottom
        faces.append((p, p + 1, p + 5, p + 4)); faces.append((p + 2, p + 3, p + 7, p + 6)) #Left & Right
        faces.append((p, p + 4, p + 7, p + 3)); faces.append((p + 1, p + 2, p + 6, p + 5)) #Back & Front
    return (verts, faces)
def wood_vertical(oh, ow, is_slope, slope, is_width_vary, width_vary, bw, verts, faces, bs, is_length_vary, length_vary, max_boards):
    cur_x = 0.0
    batten_pos = []
    m_b_n = False
    m_b = None #middle board location
    last_z = oh - ((slope * (ow / 2)) / 12) #height - what that slope and width would give for height
    if last_z <= 0: #check is it is a negative number
        slope = ((24 * oh) / ow) - 0.01
        last_z = oh - ((slope * (ow / 2)) / 12) #if it is change to slope that fits
    if is_slope == False: #if flat
        last_z = oh
    while cur_x < ow: #while x position is less than overall width
        if is_length_vary == True: #if varied length, generate length
            v = oh * (length_vary * 0.45)
            bl = uniform((oh / 2) - v, (oh / 2) + v) 
        else:
            bl = oh
            max_boards = 1
        if is_width_vary == True: #if varied width, generate width
            v = bw * (width_vary * 0.75)
            bw2 = uniform(bw - v, bw + v)
        else: 
            bw2 = bw
        if is_slope == True: #if slope calculate height difference between edges of the board
            z_dif = (slope * bw2) / 12
        bz = 0.0
        counter = 1
        faces_normal = False
        while bz < last_z:
            if cur_x + bw2 > ow: #finish with correct width board
                bw2 = ow - cur_x
            p = len(verts) #get index for adding faces at end
            if is_slope == True:
                if cur_x + bw2 < ow / 2: #slope up
                    verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2 #Bottom > Left
                    verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2; bz += bl #Bottom > Right
                    if bz < last_z - 0.25 and counter != max_boards:
                        verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2 #Top > Left
                        verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2; bz += 0.003175 #Top > Right
                    else:
                        bz = last_z
                        verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2; bz += z_dif #Top > Left
                        batten_pos.append([cur_x, bz])
                        verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2 #Top > Right  
                        bz += (slope * bs) / 12 #height gained over gap
                        if bz > oh:
                            bz = oh - ((slope * ((cur_x  + bw2 + bs) - (ow / 2))) / 12)
                        last_z = bz
                    face_normal = True
                elif cur_x >= ow / 2: #slope down
                    verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2 #Bottom > Left
                    verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2; bz += bl #Bottom > Right
                    if bz < last_z - z_dif and counter != max_boards:
                        verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2 #Top > Left
                        verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2; bz += 0.003175 #Top > Right
                    else:
                        bz = last_z
                        verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2 #Top > Left
                        z_dif = (slope * bw2) / 12; bz -= z_dif 
                        batten_pos.append([cur_x, bz])
                        verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2 #Top > Right
                        bz -= (slope * bs) / 12 #height lost over gap
                        last_z = bz
                    face_normal = True
                elif cur_x < ow / 2 and cur_x + bw2 > ow / 2: #middle board
                    verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2 #Bottom > Left
                    verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2; bz += bl #Bottom > Right
                    if bz < last_z - 0.25 and counter != max_boards:
                        verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2 #Top > Left
                        verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2; bz += 0.003175 #Top > Right
                        face_normal = True
                    else:
                        face_normal = False
                        bz -= bl
                        #insert verts before last set
                        verts.insert(len(verts) - 2, (ow / 2, -0.02539, bz)); verts.insert(len(verts) - 2, (ow / 2, 0.0, bz)) #Bottom > Middle
                        #top verts
                        verts.append((cur_x, 0.0, last_z)); verts.append((cur_x, -0.02539, last_z)); cur_x += bw2 #Top > Left
                        verts.append((ow / 2, -0.02539, oh)); verts.append((ow / 2, 0.0, oh)) #Top > Middle
                        bz = oh - (slope * (cur_x - (ow / 2)) / 12)
                        batten_pos.append([cur_x, bz])
                        verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2 #Top > Right
                        m_b_n = len(verts)
                        bz -= (slope * bs) / 12 #height lost over gap
                        last_z = bz   
            #flat
            elif is_slope == False:
                verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2 #Bottom > Left
                verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); cur_x -= bw2; bz += bl #Bottom > Right
                if bz > oh:
                    bz = oh
                elif bz < oh and counter == max_boards:
                    bz = oh
                verts.append((cur_x, 0.0, bz)); verts.append((cur_x, -0.02539, bz)); cur_x += bw2 #Top > Left
                if bz == oh: #record data for battens
                    batten_pos.append([cur_x, oh])  
                verts.append((cur_x, -0.02539, bz)); verts.append((cur_x, 0.0, bz)); bz += 0.003175; cur_x -= bw2 # Top > Right
            counter += 1
            #faces
            if is_slope == False or face_normal == True:
                faces.append((p, p + 3, p + 2, p + 1)); faces.append((p + 4, p + 5, p + 6, p + 7)) #Bottom & Top
                faces.append((p, p + 1, p + 5, p + 4)); faces.append((p + 1, p + 2, p + 6, p + 5)) #Left & Front
                faces.append((p + 2, p + 3, p + 7, p + 6)); faces.append((p, p + 4, p + 7, p + 3)) #Right
            else:
                faces.append((p, p + 3, p + 2, p + 1)); faces.append((p + 2, p + 3, p + 5, p + 4)) #Bottom
                faces.append((p + 6, p + 7, p + 8, p + 9)); faces.append((p + 8, p + 10, p + 11, p + 9)) #Top
                faces.append((p, p + 1, p + 7, p + 6)); faces.append((p + 1, p + 2, p + 8, p + 7)) #Left & Front Left
                faces.append((p + 2, p + 4, p + 10, p + 8)); faces.append((p + 4, p + 5, p + 11, p + 10)) #Front Right & Right
                faces.append((p, p + 6, p + 9, p + 3)); faces.append((p + 3, p + 9, p + 11, p + 5)) #Back
        cur_x += bw2 + bs
    out_data = [m_b_n, batten_pos]
    return (verts, faces, out_data)

def wood_ton_gro(oh, ow, is_slope, slope, bw, verts, faces, is_length_vary, length_vary, max_boards): #wood tongue and groove
    cur_x = 0.0 #current x position
    hi = 0.01270 #half inch
    fei = 0.015875 #five/eights inch
    oi = 0.02540 #inch
    #get variables ready
    if is_slope == True: #if slope make sure slope is possible
        last_z = oh - ((slope * (ow / 2)) / 12)
        if last_z <= 0:
            slope = ((24 * oh) / ow) - 0.01
            last_z = oh - ((slope * (ow / 2)) / 12)
        z_dif = (slope * bw) / 12 #difference in height between board edges
        h_dif = (slope * 0.01270) / 12 #find height differnece for half inch sideways movement
    else:
        last_z = oh
        z_dif = 0.0
    while cur_x < ow: #while not full width
        cur_z = 0.0
        if is_length_vary == True: #if varied length calculate length
            v = oh * (length_vary * 0.45)
            bl = uniform((oh / 2) - v, (oh / 2) + v)
        else:
            bl = oh
        counter = 1
        while cur_z < last_z: #while not full height
            p = len(verts)
            face_normal = False
            do_slope = False
            #flat
            if is_slope == False:
                #bottom
                if cur_x + bw > ow: bw = ow - cur_x
                verts.append((cur_x + hi, -fei, cur_z)); verts.append((cur_x, -fei, cur_z)) #Left > Back
                verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z)); cur_x += bw #Left > Front
                verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                cur_x -= bw
                #top
                cur_z += bl
                if cur_z > last_z - 0.25 or counter == max_boards: cur_z = last_z
                verts.append((cur_x + hi, -fei, cur_z)); verts.append((cur_x, -fei, cur_z)) #Left > Back
                verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z)); cur_x += bw #Let > Front
                verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                cur_x -= bw; cur_z += 0.003175; face_normal = True
            else: #if sloped
                #slope up
                if cur_x + bw < ow / 2:
                    verts.append((cur_x + hi, -fei, cur_z)); verts.append((cur_x, -fei, cur_z)) #Left > Back
                    verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z)); cur_x += bw #Left > Front
                    verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z)); cur_x -= bw
                    #top
                    cur_z += bl
                    if cur_z > last_z - 0.25 or counter == max_boards:
                        cur_z = last_z
                        verts.append((cur_x + hi, -fei, cur_z + h_dif)); verts.append((cur_x, -fei, cur_z)) #Left > Back
                        verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z + h_dif)); cur_x += bw #Left > Front
                        verts.append((cur_x, -oi, cur_z + z_dif)); verts.append((cur_x, -hi, cur_z + z_dif))
                        verts.append((cur_x + hi, -hi, cur_z + z_dif + h_dif))
                        cur_x -= bw; cur_z += z_dif + ((slope * 0.006350) / 12); last_z = cur_z
                    else:
                        verts.append((cur_x + hi, -fei, cur_z)); verts.append((cur_x, -fei, cur_z)) #Left > Back
                        verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z)); cur_x += bw
                        verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                        cur_x -= bw; cur_z += 0.003175
                    face_normal = True  
                #slope down
                elif cur_x > ow / 2:
                    if cur_x + bw > ow:
                        bw = ow - cur_x
                        z_dif = (slope * bw) / 12
                    verts.append((cur_x + hi, -fei, cur_z)); verts.append((cur_x, -fei, cur_z))
                    verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z)); cur_x += bw
                    verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                    cur_x -= bw; cur_z += bl
                    if cur_z > last_z - z_dif - 0.1 or counter == max_boards: #do top
                        cur_z = last_z
                        verts.append((cur_x + hi, -fei, cur_z - h_dif)); verts.append((cur_x, -fei, cur_z))
                        verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z - h_dif)); cur_x += bw; cur_z -= z_dif
                        verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z - h_dif))
                        cur_x -= bw; cur_z -= (slope * 0.006350) / 12; last_z = cur_z; face_normal = True
                    else:
                        verts.append((cur_x + hi, -fei, cur_z)); verts.append((cur_x, -fei, cur_z))
                        verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z)); cur_x += bw
                        verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                        cur_x -= bw; cur_z += 0.003175; face_normal = True
                #middle board
                elif cur_x < ow / 2 and cur_x + bw > ow / 2:
                    c = ow / 2 #center
                    if cur_x + hi < c: #center is not in first half inch
                        verts.append((cur_x + hi, -fei, cur_z)); verts.append((cur_x, -fei, cur_z)) #Left > Back
                        verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z)) #Left > Front
                        if cur_z + bl > last_z - 0.25 or counter == max_boards: #put middle set in
                            cur_x += bw; verts.append((c, -oi, cur_z)); verts.append((c, -hi, cur_z)) #Middle
                            verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z)) #Right
                            cur_x -= bw; verts.append((cur_x + hi, -fei, last_z + h_dif)); verts.append((cur_x, -fei, last_z)) #Left > Back
                            verts.append((cur_x, -oi, last_z)); verts.append((cur_x + hi, -oi, last_z + h_dif)); cur_x += bw #Left > Front
                            verts.append((c, -oi, oh)); verts.append((c, -hi, oh)); b_l = cur_x - c #Center
                            cur_z = oh - ((slope * b_l) / 12); verts.append((cur_x, -oi, cur_z))
                            verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z - h_dif)); cur_x -= bw
                            cur_z -= (slope * 0.006350) / 12; last_z = cur_z; face_normal = "middle"
                        else: #normal board
                            cur_x += bw; verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                            cur_x -= bw; cur_z += bl; verts.append((cur_x + hi, -fei, cur_z)); verts.append((cur_x, -fei, cur_z))
                            verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z)); cur_x += bw
                            verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                            cur_z += 0.003175; face_normal = True; cur_x -= bw    
                    elif cur_x + hi > c: #center is in first half inch
                        if cur_z < last_z - 0.25 and is_length_vary == True and counter != max_boards:
                            verts.append((cur_x + hi, -fei, cur_z)); verts.append((cur_x, -fei, cur_z))
                            verts.append((cur_x, -oi, cur_z)); verts.append((cur_x + hi, -oi, cur_z)); cur_x += bw
                            verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                            cur_x -= bw; cur_z += 0.003175; face_normal = True 
                        else:
                            c = ow / 2; verts.append((c, -fei, cur_z)); verts.append((cur_x, -fei, cur_z))
                            verts.append((cur_x, -oi, cur_z)); verts.append((c, -oi, cur_z)) #Left Side and Left Middle
                            verts.append((cur_x + hi, -oi, cur_z)); verts.append((cur_x + hi, -hi, cur_z)); cur_x += bw #Left Left
                            verts.append((cur_x, -oi, cur_z)); verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                            cur_x -= bw; cur_z = last_z
                            verts.append((c, -fei, oh)); verts.append((cur_x, -fei, cur_z))
                            verts.append((cur_x, -oi, cur_z)); verts.append((c, -oi, oh)); b_l = (cur_x + hi) - c               
                            cur_z = oh - ((slope * b_l) / 12); verts.append((cur_x + hi, -oi, cur_z)); verts.append((cur_x + hi, -hi, cur_z))
                            #figure right edge top height
                            cur_z = oh - ((slope * (bw - hi)) / 12); cur_x += bw; verts.append((cur_x, -oi, cur_z))
                            verts.append((cur_x, -hi, cur_z)); verts.append((cur_x + hi, -hi, cur_z - h_dif))
                            cur_z -= (slope * 0.006350) / 12; cur_x -= bw; last_z = cur_z; face_normal = "not_middle"                                   
            counter += 1
            #faces
            if is_slope == False or face_normal == True:
                a = ((p, p + 1, p + 8, p + 7), (p + 1, p + 2, p + 9, p + 8), (p + 2, p + 3, p + 10, p + 9), (p + 3, p + 4, p + 11, p + 10),
                        (p + 4, p + 5, p + 12, p + 11), (p + 2, p + 3, p + 10, p + 9), (p, p + 3, p + 2, p + 1), (p, p + 5, p + 4, p + 3),
                        (p + 7, p + 8, p + 9, p + 10), (p + 7, p + 10, p + 11, p + 12), (p, p + 7, p + 12, p + 5), (p + 5, p + 6, p + 13, p + 12))
                for i in a:
                    faces.append(i)
            elif is_slope == True and face_normal in ("not_middle", "middle"):
                a = ((p, p + 1, p + 2, p + 3), (p, p + 3, p + 4, p + 5), (p + 4, p + 6, p + 7, p + 5), (p + 9, p + 10, p + 11, p + 12),
                        (p + 9, p + 12, p + 13, p + 14), (p + 13, p + 15, p + 16, p + 14), (p + 1, p + 2, p + 11, p + 10),
                        (p + 2, p + 3, p + 12, p + 11), (p + 3, p + 4, p + 13, p + 12), (p + 4, p + 6, p + 15, p + 13), (p + 7, p + 8, p + 17, p + 16),
                        (p + 6, p + 7, p + 16, p + 15), (p + 7, p + 8, p + 17, p + 16), (p, p + 9, p + 14, p + 5), (p + 5, p + 14, p + 16, p + 7))
                for i in a:
                    faces.append(i)
                if face_normal == "middle":
                    faces.append((p, p + 1, p + 10, p + 9))
                elif face_normal == "not_middle":
                    faces.append((p, p + 1, p + 10, p + 9))
                        
        cur_x += bw + 0.006350
    return (verts, faces)
                
def wood_lap(oh, ow, is_slope, slope, bw, verts, faces, is_length_vary, length_vary, max_boards, thickness): #wood lap and fiber cement
    cur_z = 0.0 #current z
    oi = 0.02540 #inch
    th = thickness #thickness
    y_dif = (th / (bw - th)) * bw #how far out the bottom of the board is on y
    if is_slope == True: #if slope check and see if slope is possible, if not recalculate
        square = oh - ((slope * (ow / 2)) / 12) #z height where slope starts
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / ow) - 0.01
            square = oh - ((slope * (ow / 2)) / 12)
        x_dif = (12 * bw) / slope #distance to loose on each side if sloped
        last_x = ow #what the last x value was
    else:
        square = oh
        last_x = ow
    start_x = 0.0 #used to jumpstart cur_x if sloped
    step = ((oi * 39.3701) / ((bw * 39.3701) - (oi * 39.3701))) ** 2 #y gain per inch down
    while cur_z < oh:
        fb = True #for conditional on left side split board
        cur_x = 0.0 #current x in this row
        counter = 1 #counts boards
        while cur_x < last_x:   
            face_normal = False
            p = len(verts)
            if is_length_vary == True: #if varied length calculate length
                v = ow * (length_vary * 0.49)
                bl = uniform((ow / 2) - v, (ow / 2) + v)
            else: #else length is full width
                bl = last_x
            b_z = sqrt(((bw * 39.3701) ** 2) - 1) 
            b_z = b_z / 39.3701
            if is_slope == False or cur_z + b_z < square: #flat
                verts.append((cur_x, -y_dif, cur_z)); verts.append((cur_x, -y_dif - th, cur_z)) #Bottom > Left
                if cur_x + bl > ow or counter == max_boards:
                    bl = ow - cur_x
                if cur_z + b_z > oh and square == oh:
                    b_z = oh - cur_z
                cur_x += bl; verts.append((cur_x, -y_dif - th, cur_z)); verts.append((cur_x, -y_dif, cur_z)); cur_x -= bl #Bottom > Right
                cur_z += b_z
                verts.append((cur_x, 0.0, cur_z)); verts.append((cur_x, -th, cur_z)); cur_x += bl #Top > Left
                verts.append((cur_x, -th, cur_z)); verts.append((cur_x, 0.0, cur_z)); cur_x += 0.003175
                if cur_x < ow:
                    cur_z -= b_z
                else:
                    if cur_z < oh:
                        cur_z -= (sqrt(1 - step)) / 39.3701
                face_normal = True
            elif cur_z > square: #slope the ends                
                if cur_z + b_z < oh: #do normal sloped boards
                    if cur_x == 0.0:
                        cur_x = start_x
                    if cur_x + bl <= cur_x + x_dif or cur_x + bl >= last_x - x_dif: #recalculate bl
                        l = (last_x - x_dif) - (cur_x + x_dif)
                        v = l * (length_vary * 0.49)
                        bl = uniform((l / 2) - v, (l / 2) + v); bl += x_dif 
                    if is_length_vary == True:                                       
                        if cur_x == start_x: #left side board            
                            verts.append((cur_x, -y_dif, cur_z)); verts.append((cur_x, -y_dif - th, cur_z)) #Bottom > Left
                            verts.append((cur_x + bl, -y_dif - th, cur_z)); verts.append((cur_x + bl, -y_dif, cur_z)) #Bottom > Right
                            cur_z += b_z; cur_x += x_dif; bl -= x_dif; start_x = cur_x; 
                            verts.append((cur_x, 0.0, cur_z)); verts.append((cur_x, -th, cur_z)) #Top > Left
                            verts.append((cur_x + bl, -th, cur_z)); verts.append((cur_x + bl, 0.0, cur_z)); cur_x += bl #Top > Right
                            cur_z -= b_z; cur_x += 0.003175; start_x -= ((12 * sqrt(1 - step)) / slope) / 39.3701
                        elif cur_x > start_x and cur_x + bl < last_x - x_dif and max_boards > 2: #middle board
                            verts.append((cur_x, -y_dif, cur_z)); verts.append((cur_x, -y_dif - th, cur_z)) #Bottom > Left
                            verts.append((cur_x + bl, -y_dif - th, cur_z)); verts.append((cur_x + bl, -y_dif, cur_z)); cur_z += b_z #Bottom > Right 
                            verts.append((cur_x, 0.0, cur_z)); verts.append((cur_x, -th, cur_z)) #Top > Left
                            verts.append((cur_x + bl, -th, cur_z)); verts.append((cur_x + bl, 0.0, cur_z)); cur_x += bl #Top > Right
                            cur_x += 0.003175; cur_z -= b_z
                        elif cur_x + bl > last_x - x_dif or counter == max_boards or max_boards == 2: #right side board
                            verts.append((cur_x, -y_dif, cur_z)); verts.append((cur_x, -y_dif - th, cur_z)) #Bottom > Left
                            verts.append((last_x, -y_dif - th, cur_z)); verts.append((last_x, -y_dif, cur_z)) #Bottom > Right
                            cur_z += b_z; last_x -= x_dif
                            verts.append((cur_x, 0.0, cur_z)); verts.append((cur_x, -th, cur_z)) #Top > Left
                            verts.append((last_x, -th, cur_z)); verts.append((last_x, 0.0, cur_z)) #Top > Right
                            c = ((12 * sqrt(1 - step)) / slope) / 39.3701; last_x += c; cur_x = last_x
                            cur_z -= (sqrt(1 - step)) / 39.3701
                        face_normal = True
                    else: #one board
                        verts.append((cur_x, -y_dif, cur_z)); verts.append((cur_x, -y_dif - th, cur_z)) #Bottom > Left
                        verts.append((last_x, -y_dif - th, cur_z)); verts.append((last_x, -y_dif, cur_z)) #Bottom > Right
                        cur_z += b_z; cur_x += x_dif
                        verts.append((cur_x, 0.0, cur_z)); verts.append((cur_x, -th, cur_z)); last_x -= x_dif #Top > Left
                        verts.append((last_x, -th, cur_z)); verts.append((last_x, 0.0, cur_z)) #Top > Right
                        face_normal = True; cur_z -= (sqrt(1 - step)) / 39.3701; c = (12 * ((sqrt(1 - step)) / 39.3701)) / slope
                        cur_x -= c; start_x = cur_x; last_x += c; cur_x = last_x; face_normal = True #update variables
                else: #top board
                    cur_x = start_x; verts.append((cur_x, -y_dif, cur_z)); verts.append((cur_x, -y_dif - th, cur_z)) #Bottom > Left
                    verts.append((last_x, -y_dif - th, cur_z)); verts.append((last_x, -y_dif, cur_z)) #Bottom > Right
                    cur_z += (((ow / 2) - cur_x) * slope) / 12
                    verts.append((ow / 2, 0.0, cur_z)); verts.append((ow / 2, -th, cur_z)) #Top
                    face_normal = "triangle"; cur_x = ow; cur_z = oh #finish loop
            elif cur_z < square and cur_z + b_z > square: #split board
                if is_length_vary == False: #one board
                    verts.append((cur_x, -y_dif, cur_z)); verts.append((cur_x, -y_dif - th, cur_z)) #Bottom > Left
                    verts.append((ow, -y_dif - th, cur_z)); verts.append((ow, -y_dif, cur_z)) #Bottom > Right
                    y = ((cur_z + b_z) - square) * (y_dif / bw) #calculate y distance at square
                    verts.append((cur_x, -y, square)); verts.append((cur_x, -y - th, square)) #Middle > Left
                    verts.append((ow, -y - th, square)); verts.append((ow, -y, square)); cur_z += b_z  #Middle > Right
                    s = (x_dif / bw) * (cur_z - square); cur_x += s; last_x -= s #figure out distance to slope back
                    verts.append((cur_x, 0.0, cur_z)); verts.append((cur_x, -th, cur_z)) #Top > Left
                    verts.append((last_x, -th, cur_z)); verts.append((last_x, 0.0, cur_z)) #Top > Right 
                    if (cur_z - square) * 39.3701 < 1:
                        start_x = 0.0; last_x = ow; cur_x = last_x
                    else:
                        c = ((12 * sqrt(1 - step)) / slope) / 39.3701; start_x = cur_x - c; last_x += c; cur_x = last_x
                    cur_z -= (sqrt(1 - step)) / 39.3701; face_normal = "split board"
                elif fb == True: #if multiple boards: this is left side split one
                    if bl < cur_x + x_dif: #makes sure board is not to long
                        bl = cur_x + x_dif + 0.1
                    verts.append((0.0, -y_dif, cur_z)); verts.append((0.0, -y_dif - th, cur_z)); cur_x += bl #Bottom > Left
                    verts.append((cur_x, -y_dif - th, cur_z)); verts.append((cur_x, -y_dif, cur_z)); cur_x -= bl #Bottom > Right
                    y = ((cur_z + b_z) - square) * (y_dif / bw) #figures out y distance at square based on board width
                    verts.append((0.0, -y, square)); verts.append((0.0, -y - th, square)); cur_x += bl #Middle > Left
                    verts.append((cur_x, -y - th, square)); verts.append((cur_x, -y, square)); cur_x -= bl #Middle > Right
                    cur_z += b_z; s = (12 * (cur_z - square)) / slope; cur_x += s; start_x = cur_x  #add board z height, figure out slope distance based on width left, add it
                    verts.append((cur_x, 0.0, cur_z)); verts.append((cur_x, -th, cur_z)); cur_x -= s; cur_x += bl #Top > Left
                    verts.append((cur_x, -th, cur_z)); verts.append((cur_x, 0.0, cur_z)); cur_z -= b_z
                    last_x -= s; cur_x += 0.003175; start_x -= ((12 * sqrt(1 - step)) / slope) / 39.3701 #update variables 
                    face_normal = "split board"; fb = False
                elif cur_x + bl < ow - x_dif and max_boards != 2: #middle board
                    if counter != max_boards:
                        verts.append((cur_x, -y_dif, cur_z)); verts.append((cur_x, -y_dif - th, cur_z)); cur_x += bl #Bottom > Left
                        verts.append((cur_x, - y_dif - th, cur_z)); verts.append((cur_x, -y_dif, cur_z)); cur_x -= bl #Bottom > Right
                        cur_z += b_z; verts.append((cur_x, 0.0, cur_z)); verts.append((cur_x, -th, cur_z)); cur_x += bl #Top > Left
                        verts.append((cur_x, -th, cur_z)); verts.append((cur_x, 0.0, cur_z)); cur_x += 0.003175 #Top > Right
                        cur_z -= b_z; face_normal = True
                elif cur_x + bl >= ow - x_dif or counter == max_boards or max_boards == 2: #right side board
                    verts.append((cur_x, -y_dif, cur_z)); verts.append((cur_x, -y_dif - th, cur_z))#Bottom > Left
                    verts.append((ow, -y_dif - th, cur_z)); verts.append((ow, -y_dif, cur_z)) #Bottom > Right
                    y = ((cur_z + b_z) - square) * (y_dif / bw) #figures out y distance at square based on board width
                    verts.append((cur_x, -y, square)); verts.append((cur_x, -y - th, square)) #Middle > Left
                    verts.append((ow, -y - th, square)); verts.append((ow, -y, square)); cur_z += b_z  #Middle > Right
                    verts.append((cur_x, 0.0, cur_z)); verts.append((cur_x, -th, cur_z)) #Top > Left
                    s = (12 * (cur_z - square)) / slope; x2 = ow - s; last_x = x2
                    verts.append((x2, -th, cur_z)); verts.append((x2, 0.0, cur_z)) #Top > Right
                    face_normal = "split board"; cur_z -= (sqrt(1 - step)) / 39.3701
                    c = (12 * ((sqrt(1 - step)) / 39.3701)) / slope #subtract distance gained during lap
                    last_x += c; fb = True; cur_x = last_x
            counter += 1
            #faces
            if is_slope == False or face_normal == True:
                a = ((p, p + 1, p + 5, p + 4), (p + 1, p + 2, p + 6, p + 5), (p + 2, p + 3, p + 7, p + 6),
                        (p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7), (p, p + 4, p + 7, p + 3))           
                for i in a:
                    faces.append(i)
            elif face_normal == "split board":
                a = ((p, p + 1, p + 5, p + 4), (p + 4, p + 5, p + 9, p + 8), (p + 9, p + 10, p + 11, p + 8),
                        (p + 6, p + 7, p + 11, p + 10), (p + 2, p + 3, p + 7, p + 6), (p, p + 3, p + 2, p + 1),
                        (p + 1, p + 2, p + 6, p + 5), (p + 5, p + 6, p + 10, p + 9), (p, p + 4, p + 7, p + 3), (p + 4, p + 8, p + 11, p + 7))
                for i in a:
                    faces.append(i)
            elif face_normal == "triangle":
                a = ((p, p + 3, p + 2, p + 1), (p, p + 1, p + 5, p + 4), (p + 1, p + 2, p + 5), (p + 2, p + 3, p + 4, p + 5), (p, p + 4, p + 3))
                for i in a:
                    faces.append(i)
    return (verts, faces)

def wood_lap_bevel(oh, ow, is_slope, slope, bw, is_length_vary, length_vary, faces, verts, max_boards): #beveled lapped siding
    cur_z = 0.0
    last_x = ow
    start_x = 0.0
    oi = 0.02540 #inch
    tb = bw / 2.5 #thrid of board width
    tb2 = (bw * 39.3701) / 2.5
    ohi = (tb2 * 0.5) / (tb2 - 0.5); ohi /= 39.3701 #bottom y
    hi = oi - ohi #top y
    y_step = ohi / tb #per unit down this is how far you go on y
    if is_slope == True:
        square = oh - ((slope * (ow / 2)) / 12) #z height where slope starts
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / ow) - 0.01
            square = oh - ((slope * (ow / 2)) / 12)
        x_dif = (12 * bw) / slope #distance to per whole board
        tb_dif = (12 * tb) / slope #x difference for tb height
        m_dif = (12 * (bw - (2 * tb))) / slope #x difference for middle of board height
    else:
        square = oh   
    while cur_z < oh:
        temp_x = 0.0
        cur_x = 0.0
        face_normal = False
        counter = 1
        if start_x != 0.0:
            cur_x = start_x
        if cur_x >= last_x:
            cur_z = oh
        while cur_x < last_x:
            s_d = False; enter = False #square done   
            if is_length_vary == True:   
                v = ow * (length_vary * 0.45)
                bl = uniform((ow / 2) - v, (ow / 2) + v)
                if cur_x + bl > ow or counter == max_boards:
                    bl = ow - cur_x
            else:
                bl = ow 
            p = len(verts) #position for vert indexs
            #verts
            if is_slope == False or cur_z + bw <= square: #flat or below square
                if cur_z == oh: 
                    cur_z -= oi   
                v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, -ohi, cur_z)); cur_z += tb  #Bottom Row  
                if cur_z > oh:
                    cur_z = oh; face_normal = "eight" #eight vertices 
                v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)) #Second Row
                if cur_z < oh:
                    cur_z += bw - (2 * tb)
                    if cur_z > oh:
                        cur_z = oh; face_normal = "twelve" #twelve vertices   
                    v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)) #Third Row   
                if cur_z < oh:  
                    cur_z += tb
                    if cur_z > oh:
                        cur_z = oh
                    v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z)); face_normal = True #Top Row                    
                cur_x += bl
                if is_length_vary == False:
                    cur_x = last_x
                    if cur_z < oh:
                        cur_z -= oi
                else:        
                    if cur_x < ow:
                        cur_z -= bw; cur_x += 0.003175
                    elif cur_x >= ow and cur_z < oh:
                        cur_z -= oi 
                for i in v:
                    verts.append(i) 
            elif cur_z < square and cur_z + bw > square: #middle board  
                if is_length_vary == False: #single board        
                    v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, -ohi, cur_z)) #Bottom Row
                    cur_z += tb
                    if cur_z > square:
                        y = (cur_z - square) * y_step; v += ((cur_x, -y, square), (cur_x, -oi, square), (last_x, -oi, square), (last_x, -y, square)) #At Square
                        s = (12 * (cur_z - square)) / slope; cur_x += s; last_x -= s; s_d = True                   
                    v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)); cur_z += bw - (2 * tb)  #Second Row                    
                    if s_d == True: s = (12 * (bw - (2 * tb))) / slope; cur_x += s; last_x -= s
                    if s_d != True and cur_z > square: #Now do square row
                        v += ((cur_x, 0.0, square), (cur_x, -oi, square), (last_x, -oi, square), (last_x, 0.0, square))
                        s = (12 * (cur_z - square)) / slope; cur_x += s; last_x -= s; s_d = True                    
                    v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)); cur_z += tb #Third Row  
                    if s_d == True: s = (12 * tb) / slope; cur_x += s; last_x -= s
                    if s_d != True and cur_z > square: #Now do square row
                        y = hi + ((ohi / tb) * (cur_z - square)); v += ((cur_x, 0.0, square), (cur_x, -y, square), (last_x, -y, square), (last_x, 0.0, square)) #At Square
                        s = (12 * (cur_z - square)) / slope; cur_x += s; last_x -= s; s_d = True                          
                    v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (last_x, -hi, cur_z), (last_x, 0.0, cur_z)) #Third Row
                    cur_z -= oi; face_normal = "square"
                    if cur_z > square: s = (12 * oi) / slope; start_x = cur_x - s; last_x += s; cur_x = last_x
                    else: last_x += s; cur_x = last_x
                    for i in v:
                        verts.append(i)
                else:
                    if cur_x == 0.0: #left board
                        v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, -ohi, cur_z)) #Bottom Row
                        cur_z += tb
                        if cur_z > square:
                            y = (cur_z - square) * y_step; v += ((cur_x, -y, square), (cur_x, -oi, square), (cur_x + bl, -oi, square), (cur_x + bl, -y, square)) #At Square
                            s = (12 * (cur_z - square)) / slope; cur_x += s; bl -= s; s_d = True
                        v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)); cur_z += bw - (2 * tb) #Second Row
                        if s_d == True: s = (12 * (bw - (2 * tb))) / slope; cur_x += s; bl -= s
                        if cur_z > square and s_d != True:
                            v += ((cur_x, 0.0, square), (cur_x, -oi, square), (cur_x + bl, -oi, square), (cur_x + bl, 0.0, square)) #At Square
                            s = (12 * (cur_z - square)) / slope; cur_x += s; bl -= s; s_d = True
                        v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)); cur_z += tb #Third Row
                        if s_d == True: s = (12 * tb) / slope; cur_x += s; bl -= s
                        if cur_z > square and s_d != True: 
                            y = hi + ((ohi / tb) * (cur_z - square)); v += ((cur_x, 0.0, square), (cur_x, -y, square), (cur_x + bl, -y, square), (cur_x + bl, 0.0, square)) #At Square
                            s = (12 * (cur_z - square)) / slope; cur_x += s; bl -= s; s_d = True
                        v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z)); temp_x = cur_x #Top Row
                        if s_d == False: 
                            face_normal = True
                        else:
                            face_normal = "square"
                        cur_z -= bw; cur_x += 0.003175; cur_x += bl
                        for i in v:
                            verts.append(i)
                    elif cur_x + bl < last_x - x_dif and max_boards > 2 and counter != max_boards: #middle board
                        v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, -ohi, cur_z)) #Bottom Row
                        cur_z += tb; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)) #Second Row
                        cur_z += bw - (2 * tb); v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)) #Third Row
                        cur_z += tb; v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z)) #Top Row
                        face_normal = True; cur_z -= bw; cur_x += 0.003175; cur_x += bl
                        for i in v:
                            verts.append(i)
                    elif cur_x + bl >= last_x - x_dif or counter == max_boards: #right board
                        v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, -ohi, cur_z)) #Bottom Row
                        cur_z += tb
                        if cur_z > square:
                            y = (cur_z - square) * y_step; v += ((cur_x, -y, square), (cur_x, -oi, square), (last_x, -oi, square), (last_x, -y, square)) #At Square
                            s = (12 * (cur_z - square)) / slope; last_x -= s; s_d = True
                        v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)); cur_z += bw - (2 * tb) #Second Row
                        if s_d == True: s = (12 * (bw - (2 * tb))) / slope; last_x -= s
                        if cur_z > square and s_d != True:
                            v += ((cur_x, 0.0, square), (cur_x, -oi, square), (last_x, -oi, square), (last_x, 0.0, square)) #At Square
                            s = (12 * (cur_z - square)) / slope; last_x -= s; s_d = True
                        v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)); cur_z += tb #Third Row
                        if s_d == True: s = (12 * tb) / slope; last_x -= s
                        if cur_z > square and s_d != True: 
                            y = hi + ((ohi / tb) * (cur_z - square)); v += ((cur_x, 0.0, square), (cur_x, -y, square), (last_x, -y, square), (last_x, 0.0, square)) #At Square
                            s = (12 * (cur_z - square)) / slope; last_x -= s; s_d = True
                        v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (last_x, -hi, cur_z), (last_x, 0.0, cur_z)) #Top Row
                        if s_d == False: 
                            face_normal = True
                        else: 
                            face_normal = "square"
                        cur_z -= oi; start_x = temp_x
                        if cur_z <= square:
                            start_x = 0.0; last_x = ow; cur_x = last_x
                        else:
                            s = (12 * oi) / slope; start_x -= s; last_x += s; cur_x = last_x
                        for i in v:
                            verts.append(i)
            elif cur_z >= square and cur_z + bw <= oh: #regular sloping boards  
                if is_length_vary == False: #single sloping board
                    v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, -ohi, cur_z)) #Bottom Row
                    cur_z += tb; cur_x += tb_dif; last_x -= tb_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)) #Second Row
                    cur_z += bw - (2 * tb); cur_x += m_dif; last_x -= m_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)) #Third Row
                    cur_z += tb; cur_x += tb_dif; last_x -= tb_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (last_x, -hi, cur_z), (last_x, 0.0, cur_z)) #Top Row
                    cur_z -= oi; s = (12 * oi) / slope; cur_x -= s; last_x += s; start_x = cur_x; face_normal = True; cur_x = last_x
                    for i in v:
                        verts.append(i)
                elif is_length_vary == True:
                    if face_normal == False: #figure out if single board
                        if last_x - start_x < 1.25: enter = True
                        elif (last_x - x_dif) - (cur_x + x_dif) < 1: enter = True
                    if enter == True: #single board
                        v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, -ohi, cur_z)) #Bottom Row
                        cur_z += tb; cur_x += tb_dif; last_x -= tb_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)) #Second Row
                        cur_z += bw - (2 * tb); cur_x += m_dif; last_x -= m_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)) #Third Row
                        cur_z += tb; cur_x += tb_dif; last_x -= tb_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (last_x, -hi, cur_z), (last_x, 0.0, cur_z)) #Top Row
                        cur_z -= oi; s = (12 * oi) / slope; cur_x -= s; last_x += s; start_x = cur_x; face_normal = True; cur_x = last_x
                        if cur_z + oi >= oh: cur_z = oh
                        for i in v:
                            verts.append(i)
                    else:
                        if cur_x == start_x: #left board                         
                            if cur_x + bl > last_x - x_dif or x_dif > bl:
                                l = (last_x - x_dif) - (cur_x + x_dif); v = l * (length_vary * 0.45); bl = uniform(l - v, x_dif + v)
                            v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, -ohi, cur_z)) #Bottom Row
                            cur_z += tb; cur_x += tb_dif; bl -= tb_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)) #Second Row
                            cur_z += bw - (2 * tb); cur_x += m_dif; bl -= m_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)) #Third Row
                            cur_z += tb; cur_x += tb_dif; bl -= tb_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z)) #Top Row
                            cur_z -= bw; start_x = cur_x; cur_x += bl + 0.003175; face_normal = True
                            for i in v:
                                verts.append(i)
                        elif cur_x + bl < last_x - x_dif and counter != max_boards and max_boards > 2: #middle board
                            v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, -ohi, cur_z)) #Bottom Row
                            cur_z += tb; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)) #Second Row
                            cur_z += bw - (2 * tb); v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (cur_x + bl, -oi, cur_z), (cur_x + bl, 0.0, cur_z)) #Third Row
                            cur_z += tb; v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z)) #Top Row
                            cur_z -= bw; cur_x += bl + 0.003175; face_normal = True
                            for i in v:
                                verts.append(i)
                        elif cur_x + bl > last_x - x_dif or counter == max_boards or max_boards == 2: #right board   
                            v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, -ohi, cur_z)) #Bottom Row
                            cur_z += tb; last_x -= tb_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)) #Second Row
                            cur_z += bw - (2 * tb); last_x -= m_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)) #Third Row
                            cur_z += tb; last_x -= tb_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (last_x, -hi, cur_z), (last_x, 0.0, cur_z)) #Top Row
                            cur_z -= oi; s = (12 * oi) / slope; start_x -= s; last_x += s; cur_x = last_x; face_normal = True
                            for i in v:
                                verts.append(i)
            elif cur_z + bw > oh: #top triangle board
                v = ((cur_x, -ohi, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, -ohi, cur_z)) #Bottom Row
                cur_z += tb
                if cur_z > oh: #If currently higher than overall height make triangle        
                    cur_z -= tb; s = (12 * (oh - cur_z)) / slope; cur_z = oh; cur_x += s; last_x -= s
                    v += ((ow / 2, 0.0, cur_z), (ow / 2, -oi, cur_z)); cur_x = last_x; face_normal = "tri_lev_one" #Top Row
                else: #not yet
                    cur_x += tb_dif; last_x -= tb_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)) #Second Row
                    cur_z += bw - (2 * tb)
                    if cur_z > oh: #if now
                        cur_z -= tb; s = (12 * (oh - cur_z)) / slope; cur_z = oh; cur_x += s; last_x -= s
                        v += ((ow / 2, 0.0, cur_z), (ow / 2, -oi, cur_z)); cur_x = last_x; face_normal = "tri_lev_two" #Top Row
                    else: #not yet
                        cur_x += m_dif; last_x -= m_dif; v += ((cur_x, 0.0, cur_z), (cur_x, -oi, cur_z), (last_x, -oi, cur_z), (last_x, 0.0, cur_z)) #Third Row
                        cur_z = oh; v += ((ow / 2, 0.0, cur_z), (ow / 2, -hi, cur_z)); face_normal = "tri_lev_three"; cur_x = ow #Top Row            
                cur_x = last_x; cur_z = oh                   
                for i in v:
                    verts.append(i)   
            counter += 1                 
            #faces
            if face_normal == True or face_normal == "square":
                f = [(p, p + 3, p + 2, p + 1), (p, p + 1, p + 5, p + 4), (p + 4, p + 5, p + 9, p + 8), (p + 8, p + 9, p + 13, p + 12),
                        (p + 1, p + 2, p + 6, p + 5), (p + 5, p + 6, p + 10, p + 9), (p + 9, p + 10, p + 14, p + 13), (p, p + 4, p + 7, p + 3),
                        (p + 2, p + 3, p + 7, p + 6), (p + 6, p + 7, p + 11, p + 10), (p + 10, p + 11, p + 15, p + 14), (p + 12, p + 13, p + 14, p + 15),
                        (p + 4, p + 8, p + 11, p + 7), (p + 8, p + 12, p + 15, p + 11)]
                if face_normal == "square":
                    del f[11]; f += ((p + 8, p + 12, p + 15, p + 11), (p + 12, p + 13, p + 17, p + 16), (p + 13, p + 14, p + 18, p + 17), (p + 14, p + 15, p + 19, p + 18),
                                        (p + 12, p + 16, p + 19, p + 15), (p + 16, p + 17, p + 18, p + 19))  
                for i in f:
                    faces.append(i)
            elif face_normal == "eight":
                f = ((p, p + 3, p + 2, p + 1), (p + 1, p + 2, p + 6, p + 5), (p, p + 1, p + 5, p + 4), (p + 2, p + 3, p + 7, p + 6), (p + 4, p + 5, p + 6, p + 7), (p, p + 4, p + 7, p + 3))
                for i in f:
                    faces.append(i)
            elif face_normal == "twelve":
                f = ((p, p + 3, p + 2, p + 1), (p + 1, p + 2, p + 6, p + 5), (p, p + 1, p + 5, p + 4), (p + 2, p + 3, p + 7, p + 6), (p, p + 4, p + 7, p + 3),
                        (p + 4, p + 5, p + 9, p + 8), (p + 5, p + 6, p + 10, p + 9), (p + 6, p + 7, p + 11, p + 10), (p + 4, p + 8, p + 11, p + 7), (p + 8, p + 9, p + 10, p + 11))
                for i in f:
                    faces.append(i)
            elif face_normal in ("tri_lev_one", "tri_lev_two", "tri_lev_three"):
                f = []
                if face_normal == "tri_lev_one": #level on
                    f.append((p, p + 3, p + 2, p + 1))  
                elif face_normal == "tri_lev_two": #level two
                    f += ((p, p + 3, p + 2, p + 1), (p, p + 1, p + 5, p + 4), (p + 1, p + 2, p + 6, p + 5), (p + 2, p + 3, p + 7, p + 6), (p, p + 4, p + 7, p + 3)); p += 4
                elif face_normal == "tri_lev_three": #level three
                    f += ((p, p + 3, p + 2, p + 1), (p, p + 1, p + 5, p + 4), (p + 1, p + 2, p + 6, p + 5), (p + 2, p + 3, p + 7, p + 6), (p, p + 4, p + 7, p + 3),
                            (p + 4, p + 5, p + 9, p + 8), (p + 5, p + 6, p + 10, p + 9), (p + 6, p + 7, p + 11, p + 10), (p + 4, p + 8, p + 11, p + 7)); p += 8
                f += ((p, p + 1, p + 5, p + 4), (p + 1, p + 2, p + 5), (p + 2, p + 3, p + 4, p + 5), (p, p + 4, p + 3))
                for i in f:
                    faces.append(i)
    return (verts, faces)

def vinyl_vertical(oh, ow, is_slope, slope, is_length_vary, length_vary, bw, baw, faces, verts, max_boards):
    cur_x = 0.0   
    if (bw / 2) - 0.003175 <= baw: #batten to wide
        baw = (bw / 2) - 0.003175
    hi = 0.01270; ei = 0.003175; tei = 0.009525 #convenience variables; half inch, left side distance to batten, 1/8 inch, 3/8 inch
    space = (bw - (2 * baw)) / 2; rsx = space + baw; lsx = bw - baw  
    if is_slope == True:
        square = oh - ((slope * (ow / 2)) / 12); last_z = square; z_dif = (slope * bw) / 12 #z height where slope starts
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / ow) - 0.01; square = oh - ((slope * (ow / 2)) / 12); last_z = square; z_dif = (slope * bw) / 12
    else:
        last_z = oh
    c_d = False
    while cur_x < ow: #main loop for width
        counter = 1
        cur_z = 0.0
        while cur_z < last_z: #while height it not enough
            face_normal = False; p = len(verts)
            if is_length_vary == True and counter != max_boards: #calculate board length
                v = oh* (length_vary * 0.45); bl = uniform((oh/ 2) - v, (oh / 2) + v)
            else:
                bl = oh
            if cur_z + bl > oh:
                bl = oh - cur_z   
            #verts
            if is_slope == False: #normal boards                
                v = []
                for i in range(2):
                    v += ((cur_x, -tei, cur_z), (cur_x, 0.0, cur_z), (cur_x + space + ei, 0.0, cur_z), (cur_x + space, -hi, cur_z)) #Left Side First Batten
                    v += ((cur_x + rsx, -hi, cur_z), (cur_x + rsx - ei, 0.0, cur_z), (cur_x + lsx + ei, 0.0, cur_z), (cur_x + lsx, -hi, cur_z)) #Left Side Second Batten
                    v += ((cur_x + bw, -hi, cur_z), (cur_x + bw, -ei, cur_z)); cur_z += bl
                cur_z -= bl 
                if cur_x + bw <= ow: 
                    cur_z += ei; face_normal = True
                else:
                    if cur_x + space >= ow: #cut back to beginning and then place last set of verts
                        del v[2:10]; del v[4: len(v)]; v.insert(2, (ow, 0.0, cur_z - bl)); v.insert(len(v), (ow, 0.0, cur_z)); face_normal = "lev_one"
                    elif cur_x + rsx >= ow:
                        del v[4:10]; del v[8: len(v)]; v.insert(4, (ow, -hi, cur_z - bl)); v.insert(len(v), (ow, -hi, cur_z)); face_normal = "lev_two"
                    elif cur_x + lsx >= ow:
                        del v[6:10]; del v[12: len(v)]; v.insert(6, (ow, 0.0, cur_z - bl)); v.insert(len(v), (ow, 0.0, cur_z)); face_normal = "lev_three"
                    elif cur_x + bw > ow:
                        del v[8:10]; del v[16: len(v)]; v.insert(8, (ow, -hi, cur_z - bl)); v.insert(len(v), (ow, -hi, cur_z)); face_normal = "lev_four"
                if cur_z >= oh:
                    cur_x += bw - ei
                for i in v:
                    verts.append(i)
            elif is_slope == True:
                if cur_x + bw <= ow / 2: #Sloping up                    
                    v = ((cur_x, -tei, cur_z), (cur_x, 0.0, cur_z), (cur_x + space + ei, 0.0, cur_z), (cur_x + space, -hi, cur_z)) #Left Side First Batten
                    v += ((cur_x + rsx, -hi, cur_z), (cur_x + rsx - ei, 0.0, cur_z), (cur_x + lsx + ei, 0.0, cur_z), (cur_x + lsx, -hi, cur_z)) #Left Side Second Batten
                    v += ((cur_x + bw, -hi, cur_z), (cur_x + bw, -ei, cur_z)); cur_z += bl
                    if cur_z >= last_z - 0.004: #slope top
                        z1 = last_z; z2 = last_z + ((slope * (space + ei)) / 12); z3 = last_z + ((slope * space) / 12); z4 = last_z + ((slope * rsx) / 12); z5 = last_z + ((slope * (rsx - ei)) / 12)
                        z6 = last_z + ((slope * (lsx + ei)) / 12); z7 = last_z + ((slope * lsx) / 12); z8 = last_z + ((slope * bw) / 12)
                    else:
                        z1 = cur_z; z2 = cur_z; z3 = cur_z; z4 = cur_z; z5 = cur_z; z6 = cur_z; z7 = cur_z; z8 = cur_z
                    v += ((cur_x, -tei, z1), (cur_x, 0.0, z1), (cur_x + space + ei, 0.0, z2), (cur_x + space, -hi, z3)) #Left Side First Batten
                    v += ((cur_x + rsx, -hi, z4), (cur_x + rsx - ei, 0.0, z5), (cur_x + lsx + ei, 0.0, z6), (cur_x + lsx, -hi, z7)) #Left Side Second Batten
                    v += ((cur_x + bw, -hi, z8), (cur_x + bw, -ei, z8)); face_normal = True
                    if is_length_vary == False or z1 == last_z:
                        cur_x += bw - ei; last_z = z8 - ((slope * ei) / 12); cur_z = last_z
                    elif is_length_vary == True and z1 == cur_z:
                        cur_z += 0.003175
                    for i in v:
                        verts.append(i)
                elif cur_x < ow / 2 and cur_x + bw > ow / 2: #Middle board
                    if is_length_vary == True and cur_z + bl < last_z - z_dif: #bottom board
                        v = []
                        for i in range(2):
                            v += ((cur_x, -tei, cur_z), (cur_x, 0.0, cur_z), (cur_x + space + ei, 0.0, cur_z), (cur_x + space, -hi, cur_z)) #Left Side First Batten
                            v += ((cur_x + rsx, -hi, cur_z), (cur_x + rsx - ei, 0.0, cur_z), (cur_x + lsx + ei, 0.0, cur_z), (cur_x + lsx, -hi, cur_z)) #Left Side Second Batten
                            v += ((cur_x + bw, -hi, cur_z), (cur_x + bw, -ei, cur_z)); cur_z += bl
                        cur_z -= bl; cur_z += ei; face_normal = True
                        for i in v:
                            verts.append(i)
                    else: #top split board
                        v = ((cur_x, -tei, cur_z), (cur_x, 0.0, cur_z), (cur_x, 0.0, last_z), (cur_x, -tei, last_z)); cur_x += space #Left
                        if cur_x > ow / 2: #if past peak
                            v += ((ow / 2, 0.0, cur_z), (ow / 2, 0.0, oh)); last_z = oh - ((slope * (cur_x - (ow / 2))) / 12); c_d = True; face_normal = "s_1"; slope_ei = -((slope * ei) / 12) #place peak and slope other side down
                        else: last_z += (slope * space) / 12; slope_ei = ((slope * ei) / 12) #if not peak keep slopping up
                        v += ((cur_x + ei, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x, -hi, last_z), (cur_x + ei, 0.0, last_z + slope_ei)); cur_x += baw #place next row
                        if cur_x > ow / 2 and c_d == False: #if past peak and peak not done yet
                            v += ((ow / 2, -hi, cur_z), (ow / 2, -hi, oh)); last_z = oh - ((slope * (cur_x - (ow / 2))) / 12); c_d = True; face_normal = "s_2"; slope_ei = -((slope * ei) / 12) #place peak and slope down other side
                        elif c_d == True: last_z -= (slope * baw) / 12 #if already slopped countinue down
                        else: last_z += (slope * baw) / 12; slope_ei = ((slope * ei) / 12) #otherwise keep slopping up
                        v += ((cur_x, -hi, cur_z), (cur_x - ei, 0.0, cur_z), (cur_x - ei, 0.0, last_z - slope_ei), (cur_x, -hi, last_z)); cur_x += space #Third Set
                        if cur_x > ow / 2 and c_d == False: #if past peak and peak not done yet
                            v += ((ow / 2, 0.0, cur_z), (ow / 2, 0.0, oh)); last_z = oh - ((slope * (cur_x - (ow / 2))) / 12); c_d = True; face_normal = "s_3"; slope_ei = -((slope * ei) / 12) #place peak and slope down on other side
                        elif c_d == True: last_z -= (slope * space) / 12 #slope down
                        else: last_z += (slope * space) / 12; slope_ei = ((slope * ei) / 12) #slope up
                        v += ((cur_x + ei, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x, -hi, last_z), (cur_x + ei, 0.0, last_z + slope_ei)); cur_x += baw #Fourth Set
                        if cur_x > ow / 2 and c_d == False: #peak
                            v += ((ow / 2, -hi, cur_z), (ow / 2, -hi, oh)); last_z = oh - ((slope * (cur_x - (ow / 2))) / 12); face_normal = "s_4" #place peak and slope down on other side
                        elif c_d == True:
                            last_z -= (slope * baw) / 12
                        v += ((cur_x, -hi, cur_z), (cur_x, -ei, cur_z), (cur_x, -ei, last_z), (cur_x, -hi, last_z)); cur_x -= ei
                        if cur_x < ow / 2: last_z = oh - ((slope * ((ow / 2) - cur_x)) / 12); cur_z = last_z
                        else: last_z += (slope * ei) / 12; cur_z = last_z
                        for i in v:
                            verts.append(i) 
                elif cur_x >= ow / 2: #Sloping down
                    spacez = (slope * space) / 12; rsz = (slope * rsx) / 12; lsz = (slope * lsx) / 12; eiz = (slope * ei) / 12; l_b = False  
                    v = [(cur_x, -tei, cur_z), (cur_x, 0.0, cur_z), (cur_x + space + ei, 0.0, cur_z), (cur_x + space, -hi, cur_z), (cur_x + rsx, -hi, cur_z)]
                    v += ((cur_x + rsx - ei, 0.0, cur_z), (cur_x + lsx + ei, 0.0, cur_z), (cur_x + lsx, -hi, cur_z), (cur_x + bw, -hi, cur_z), (cur_x + bw, -ei, cur_z))
                    if cur_z + bl > last_z - z_dif - 0.05 or is_length_vary == False: #slope top
                        v += ((cur_x, -tei, last_z), (cur_x, 0.0, last_z), (cur_x + space + ei, 0.0, last_z - spacez - eiz), (cur_x + space, -hi, last_z - spacez), (cur_x + rsx, -hi, last_z - rsz))
                        v += ((cur_x + rsx - ei, 0.0, last_z - rsz + eiz), (cur_x + lsx + ei, 0.0, last_z - lsz - eiz), (cur_x + lsx, -hi, last_z - lsz), (cur_x + bw, -hi, last_z - z_dif), (cur_x + bw, -ei, last_z - z_dif)); l_b = "slope"
                    elif is_length_vary == True and cur_z + bl <= last_z - z_dif - 0.05: #flat top
                        cur_z += bl; v += ((cur_x, -tei, cur_z), (cur_x, 0.0, cur_z), (cur_x + space + ei, 0.0, cur_z), (cur_x + space, -hi, cur_z), (cur_x + rsx, -hi, cur_z))
                        v += ((cur_x + rsx - ei, 0.0, cur_z), (cur_x + lsx + ei, 0.0, cur_z), (cur_x + lsx, -hi, cur_z), (cur_x + bw, -hi, cur_z), (cur_x + bw, -ei, cur_z)); l_b = "flat"
                    if cur_x + bw > ow: #cut boards back
                        if l_b == "slope": bottom = cur_z; top = last_z - (slope * (ow - cur_x)) / 12
                        elif l_b == "flat": bottom = cur_z - bl; top = cur_z
                        if cur_x + space >= ow: #cut back to beginning and then place last set of verts
                            del v[2:10]; del v[4: len(v)]; v.insert(2, (ow, 0.0, bottom)); v.insert(len(v), (ow, 0.0, top)); face_normal = "lev_one"
                        elif cur_x + rsx >= ow:
                            del v[4:10]; del v[8: len(v)]; v.insert(4, (ow, -hi, bottom)); v.insert(len(v), (ow, -hi, top)); face_normal = "lev_two"
                        elif cur_x + lsx >= ow:
                            del v[6:10]; del v[12: len(v)]; v.insert(6, (ow, 0.0, bottom)); v.insert(len(v), (ow, 0.0, top)); face_normal = "lev_three"
                        elif cur_x + bw > ow:
                            del v[8:10]; del v[16: len(v)]; v.insert(8, (ow, -hi, bottom)); v.insert(len(v), (ow, -hi, top)); face_normal = "lev_four"                    
                    else: face_normal = True
                    if l_b == "slope": cur_x += bw - ei; last_z -= z_dif - eiz; cur_z = last_z
                    elif l_b == "flat": cur_z += ei
                    for i in v:
                        verts.append(i)
            counter += 1                   
            #faces
            if face_normal == True:
                f = ((p, p + 1, p + 11, p + 10), (p + 1, p + 2, p + 12, p + 11), (p + 2, p + 3, p + 13, p + 12), (p + 3, p + 4, p + 14, p + 13), (p + 4, p + 5, p + 15, p + 14),
                        (p + 5, p + 6, p + 16, p + 15), (p + 6, p + 7, p + 17, p + 16), (p + 7, p + 8, p + 18, p + 17), (p + 8, p + 9, p + 19, p + 18))
            elif face_normal == "lev_one":
                f = ((p, p + 1, p + 4, p + 3), (p + 1, p + 2, p + 5, p + 4))
            elif face_normal == "lev_two":
                f = ((p, p + 1, p + 6, p + 5), (p + 1, p + 2, p + 7, p + 6), (p + 2, p + 3, p + 8, p + 7), (p + 3, p + 4, p + 9, p + 8))
            elif face_normal == "lev_three":
                f = ((p, p + 1, p + 8, p + 7), (p + 1, p + 2, p + 9, p + 8), (p + 2, p + 3, p + 10, p + 9), (p + 3, p + 4, p + 11, p + 10), (p + 4, p + 5, p + 12, p + 11), (p + 5, p + 6, p + 13, p + 12))
            elif face_normal == "lev_four":
                f = ((p, p + 1, p + 10, p + 9), (p + 1, p + 2, p + 11, p + 10), (p + 2, p + 3, p + 12, p + 11), (p + 3, p + 4, p + 13, p + 12), (p + 4, p + 5, p + 14, p + 13),
                        (p + 5, p + 6, p + 15, p + 14), (p + 6, p + 7, p + 16, p + 15), (p + 7, p + 8, p + 17, p + 16))   
            elif face_normal == "s_1":
                f = ((p, p + 1, p + 2, p + 3), (p + 1, p + 4, p + 5, p + 2), (p + 4, p + 6, p + 9, p + 5), (p + 6, p + 7, p + 8, p + 9), (p + 7, p + 10, p + 13, p + 8), (p + 10, p + 11, p + 12, p + 13),
                        (p + 11, p + 14, p + 17, p + 12), (p + 14, p + 15, p + 16, p + 17), (p + 15, p + 18, p + 21, p + 16), (p + 18, p + 19, p + 20, p + 21))
            elif face_normal == "s_2":
                f = ((p, p + 1, p + 2, p + 3), (p + 1, p + 4, p + 7, p + 2), (p + 4, p + 5, p + 6, p + 7), (p + 5, p + 8, p + 9, p + 6), (p + 8, p + 10, p + 13, p + 9), (p + 10, p + 11, p + 12, p + 13),
                        (p + 11, p + 14, p + 17, p + 12), (p + 14, p + 15, p + 16, p + 17), (p + 15, p + 18, p + 21, p + 16), (p + 18, p + 19, p + 20, p + 21))
            elif face_normal == "s_3":
                f = ((p, p + 1, p + 2, p + 3), (p + 1, p + 4, p + 7, p + 2), (p + 4, p + 5, p + 6, p + 7), (p + 5, p + 8, p + 11, p + 6), (p + 8, p + 9, p + 10, p + 11), (p + 9, p + 12, p + 13, p + 10),
                        (p + 12, p + 14, p + 17,p + 13), (p + 14, p + 15, p + 16, p + 17), (p + 15, p + 18, p + 21, p + 16), (p + 18, p + 19, p + 20, p + 21))
            elif face_normal == "s_4":
                f = ((p, p + 1, p + 2, p + 3), (p + 1, p + 4, p + 7, p + 2), (p + 4, p + 5, p + 6, p + 7), (p + 5, p + 8, p + 11, p + 6), (p + 8, p + 9, p + 10, p + 11), (p + 9, p + 12, p + 15, p + 10),
                        (p + 12, p + 13, p + 14, p + 15), (p + 13, p + 16, p + 17, p + 14), (p + 16, p + 18, p + 21, p + 17), (p + 18, p + 19, p + 20, p + 21))  
            if face_normal != False:
                for i in f:
                    faces.append(i)
    return (verts, faces)

def vinyl_lap(oh, ow, is_slope, slope, is_length_vary, length_vary, bw, faces, verts, max_boards): #vinyl horizontal lapped siding
    cur_z = 0.0
    start_x = 0.0; tqi = 0.01905
    if is_slope == True:
        square = oh - ((slope * (ow / 2)) / 12)
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / ow) - 0.01; square = oh - ((slope * (ow / 2)) / 12)
    else: square = oh
    last_x = ow; y_step = tqi / bw; x_dif = (bw * 12) / slope
    while cur_z < oh:
        cur_x = start_x; counter = 1; sd = False
        while cur_x < last_x:
            p = len(verts); face_normal = False
            if is_length_vary == True:
                l = (last_x - x_dif) - (start_x + x_dif); v = l * length_vary * 0.49; bl = uniform((l / 2) - v, (l / 2) + v); bl += x_dif
            elif is_length_vary == False:
                bl = ow
            if cur_x + bl > ow or counter == max_boards: bl = ow - cur_x
            #verts
            if is_slope == False or cur_z + bw <= square: #flat or below square
                if cur_z + bw > oh: bw = oh - cur_z
                v = ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z), (cur_x, 0.0, cur_z + bw), (cur_x + bl, 0.0, cur_z), (cur_x + bl, -tqi, cur_z), (cur_x + bl, 0.0, cur_z + bw))
                for i in v: verts.append(i)
                cur_x += bl + 0.003175; face_normal = True
                if cur_x >= ow: cur_z += bw
            elif cur_z < square and cur_z + bw > square:
                if is_length_vary == False:
                    y = tqi - ((square - cur_z) * y_step); face_normal = "split"; s = ((cur_z + bw - square) * 12) / slope
                    v = ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z), (cur_x, -y, square), (cur_x + s, 0.0, cur_z + bw))
                    v += ((ow, 0.0, cur_z), (ow, -tqi, cur_z), (ow, -y, square), (ow - s, 0.0, cur_z + bw))
                    for i in v: verts.append(i)
                    start_x = cur_x + s; last_x = ow - s; cur_z += bw; cur_x = last_x
                else:
                    if cur_x == 0.0: #right side
                        y = tqi - ((square - cur_z) * y_step); face_normal = "split"; s = ((cur_z + bw - square) * 12) / slope
                        v = ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z), (cur_x, -y, square), (cur_x + s, 0.0, cur_z + bw)); start_x = cur_x + s; cur_x += bl - s
                        v += ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z), (cur_x, -y, square), (cur_x, 0.0, cur_z + bw)); cur_x += 0.003175
                        for i in v: verts.append(i) 
                    elif cur_x + bl < last_x - x_dif and max_boards != 2: #middle            
                        v = ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z) (cur_x, 0.0, cur_z + bw)); cur_x += bl - 0.003175
                        v += ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z), (cur_x, 0.0, cur_z + bw)); cur_x += 0.003175; face_normal = True
                        for i in v: verts.append(i) 
                    else: #right side
                        y = tqi - ((square - cur_z) * y_step); face_normal = "split"; s = ((cur_z + bw - square) * 12) / slope
                        v = ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z), (cur_x, -y, square), (cur_x, 0.0, cur_z + bw))
                        v += ((ow, 0.0, cur_z), (ow, -tqi, cur_z), (ow, -y, square), (ow - s, 0.0, cur_z + bw)); last_x = ow - s; cur_x = last_x; cur_z += bw
                        for i in v: verts.append(i) 
            elif cur_z >= square and cur_z + bw < oh and is_slope == True: #sloping
                if last_x - cur_x < 1 and sd == False and cur_x == start_x: sd = True
                if is_length_vary == True and sd == False:
                    if cur_x == start_x: #left
                        x1 = cur_x + x_dif; x2 = cur_x + bl; x3 = x2; start_x = x1; nx = cur_x + bl + 0.003175
                    elif cur_x + bl < last_x - x_dif: #middle
                        x1 = cur_x; x2 = cur_x + bl; x3 = x2; nx = cur_x + bl + 0.003175
                    else: #right
                        x1 = cur_x; x2 = last_x; x3 = last_x - x_dif; last_x -= x_dif; nx = last_x
                    v = ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z), (x1, 0.0, cur_z + bw), (x2, 0.0, cur_z), (x2, -tqi, cur_z), (x3, 0.0, cur_z + bw)); cur_x = nx; face_normal = True
                    for i in v: verts.append(i)
                    if cur_x >= last_x: cur_z += bw
                else:
                    v = ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z), (cur_x + x_dif, 0.0, cur_z + bw), (last_x, 0.0, cur_z), (last_x, -tqi, cur_z), (last_x - x_dif, 0.0, cur_z + bw))
                    for i in v: verts.append(i)
                    start_x = cur_x + x_dif; last_x -= x_dif; cur_x = last_x; face_normal = True; cur_z += bw                            
            elif cur_z + bw >= oh and is_slope == True: #triangle
                v = ((cur_x, 0.0, cur_z), (cur_x, -tqi, cur_z), (last_x, 0.0, cur_z), (last_x, -tqi, cur_z), (ow / 2, 0.0, oh))
                for i in v: verts.append(i)
                cur_x = ow; cur_z = oh; face_normal = "triangle"                               
            counter += 1
            #faces
            if face_normal == True:
                faces.append((p, p + 3, p + 4, p + 1)); faces.append((p + 1, p + 4, p + 5, p + 2))
            elif face_normal == "split":
                faces.append((p, p + 4, p + 5, p + 1)); faces.append((p + 1, p + 5, p + 6, p + 2)); faces.append((p + 2, p + 6, p + 7, p + 3))
            elif face_normal == "triangle":
                faces.append((p, p + 2, p + 3, p + 1)); faces.append((p + 1, p + 3, p + 4)) 
    return (verts, faces)

def vinyl_dutch_lap(oh, ow, is_slope, slope, is_length_vary, length_vary, bw, faces, verts, max_boards):
    cur_z = 0.0; last_x = ow; start_x = 0.0
    if is_slope == True:
        square = oh - ((slope * (ow / 2)) / 12) #z height where slope starts
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / ow) - 0.01; square = oh - ((slope * (ow / 2)) / 12)    
    else: square = oh
    bw = bw / 2; bb = bw * (2 / 3); bt = bw * (1 / 3); hi = 0.01270; y_step = hi / bt #board width, board bottom width, board top width, half inch
    x_dif = (12 * bw) / slope; bb_dif = (12 * bb) / slope; bt_dif = (12 * bt) / slope #x diff for board, x dif for board bottom, x dif for board top    
    while cur_z < oh:
        cur_x = start_x; counter = 1
        while cur_x < last_x:
            face_normal = False; p = len(verts); sd = False
            if is_length_vary == True and counter != max_boards: #figure board length   
                l = (last_x - x_dif) - (start_x + x_dif); v = l * length_vary * 0.49; bl = uniform((l / 2) - v, (l / 2) + v); bl += x_dif
            else: bl = ow
            if cur_x + bl > ow:
                bl = ow - cur_x
            #verts
            if is_slope == False or cur_z + bw <= square: #flat or below square  
                v = ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z)); cur_z += bb
                if cur_z > oh: cur_z = oh; v += ((cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z)); face_normal = "two"
                else: 
                    v += ((cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z)); cur_z += bt
                    if cur_z > oh: y = (cur_z - oh) * y_step; cur_z = oh; v += ((cur_x, -y, cur_z), (cur_x + bl, -y, cur_z))
                    else: v += ((cur_x, 0.0, cur_z), (cur_x + bl, 0.0, cur_z))
                    face_normal = True            
                for i in v: verts.append(i)
                cur_x += bl + 0.003175
                if cur_x < ow: cur_z -= bw
            elif is_slope == True and cur_z < square and cur_z + bw > square: #middle board
                if is_length_vary == False: #single board
                    v = ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (ow, -hi, cur_z), (ow, 0.0, cur_z)); cur_z += bb
                    if cur_z > square: 
                        v += ((cur_x, -hi, square), (ow, -hi, square)); s = (12 * (cur_z - square)) / slope; cur_x += s; last_x -= s; sd = True
                    v += ((cur_x, -hi, cur_z), (last_x, -hi, cur_z)); cur_z += bt
                    if cur_z > square and sd == False:
                        y = (cur_z - square) * y_step; v += ((cur_x, -y, square), (ow, -y, square)); s = (12 * (cur_z - square)) / slope; cur_x += s; last_x -= s; sd = True
                    else: cur_x += bt_dif; last_x -= bt_dif
                    v += ((cur_x, 0.0, cur_z), (last_x, 0.0, cur_z)); start_x = cur_x; cur_x = last_x
                    if sd == False: face_normal = True
                    elif sd == True: face_normal = "split"
                    for i in v: verts.append(i)
                elif cur_x == start_x: #left single
                    v = ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z)); cur_z += bb
                    if cur_z > square: 
                        v += ((cur_x, -hi, square), (cur_x + bl, -hi, square)); s = (12 * (cur_z - square)) / slope; cur_x += s; bl -= s; sd = True
                    v += ((cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z)); cur_z += bt
                    if cur_z > square and sd == False:
                        y = (cur_z - square) * y_step; v += ((cur_x, -y, square), (cur_x + bl, -y, square)); s = (12 * (cur_z - square)) / slope; cur_x += s; bl -= s; sd = True
                    else: cur_x += bt_dif; bl -= bt_dif
                    v += ((cur_x, 0.0, cur_z), (cur_x + bl, 0.0, cur_z)); start_x = cur_x; cur_x += bl + 0.003175; cur_z -= bw
                    if sd == False: face_normal = True
                    elif sd == True: face_normal = "split"
                    for i in v: verts.append(i)
                elif cur_x + bl < last_x - x_dif - 0.1: #middle single
                    v = ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z), (cur_x, -hi, cur_z + bb), (cur_x + bl, -hi, cur_z + bb))
                    v += ((cur_x, 0.0, cur_z + bw), (cur_x + bl, 0.0, cur_z + bw)); face_normal = True; cur_x += bl + 0.003175
                    for i in v: verts.append(i)
                else: #right single
                    v = ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (ow, -hi, cur_z), (ow, 0.0, cur_z)); cur_z += bb
                    if cur_z > square:
                        v += ((cur_x, -hi, square), (ow, -hi, square)); s = (12 * (cur_z - square)) / slope; last_x -= s; sd = True
                    v += ((cur_x, -hi, cur_z), (last_x, -hi, cur_z)); cur_z += bt
                    if cur_z > square and sd == False:
                        y = (cur_z - square) * y_step; v += ((cur_x, -y, square), (ow, -y, square)); s = (12 * (cur_z - square)) / slope; last_x -= s; sd = True
                    else: last_x -= bt_dif
                    v += ((cur_x, 0.0, cur_z), (last_x, 0.0, cur_z)); cur_x = last_x
                    if sd == False: face_normal = True
                    elif sd == True: face_normal = "split"
                    for i in v: verts.append(i)
            elif cur_z >= square and cur_z + bw < oh - 0.01: #sloping
                if is_length_vary == False or last_x - start_x <= 1 and cur_x == start_x: #single board
                    v = ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (last_x, -hi, cur_z), (last_x, 0.0, cur_z), (cur_x + bb_dif, -hi, cur_z + bb), (last_x - bb_dif, -hi, cur_z + bb))
                    v += ((cur_x + x_dif, 0.0, cur_z + bw), (last_x - x_dif, 0.0, cur_z + bw)); start_x = cur_x + x_dif; last_x -= x_dif; face_normal = True; cur_x = last_x; cur_z += bw
                    for i in v: verts.append(i)
                elif cur_x == start_x: #left single
                    v = ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z), (cur_x + bb_dif, -hi, cur_z + bb), (cur_x + bl, -hi, cur_z + bb))
                    v += ((cur_x + x_dif, 0.0, cur_z + bw), (cur_x + bl, 0.0, cur_z + bw)); start_x = cur_x + x_dif; cur_x += bl + 0.003175; face_normal = True
                    for i in v: verts.append(i) 
                elif cur_x + bl < last_x - x_dif: #middle single
                    v = ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (cur_x + bl, -hi, cur_z), (cur_x + bl, 0.0, cur_z), (cur_x, -hi, cur_z + bb), (cur_x + bl, -hi, cur_z + bb))
                    v += ((cur_x, 0.0, cur_z + bw), (cur_x + bl, 0.0, cur_z + bw)); face_normal = True; cur_x += bl + 0.003175
                    for i in v: verts.append(i)
                else: #right single
                    v = ((cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (last_x, -hi, cur_z), (last_x, 0.0, cur_z), (cur_x, -hi, cur_z + bb), (last_x - bb_dif, -hi, cur_z + bb))
                    v += ((cur_x, 0.0, cur_z + bw), (last_x - x_dif, 0.0, cur_z + bw)); last_x -= x_dif; cur_z += bw; face_normal = True; cur_x = last_x
                    for i in v: verts.append(i)
            else: #triangle
                v = [(cur_x, 0.0, cur_z), (cur_x, -hi, cur_z), (last_x, -hi, cur_z), (last_x, 0.0, cur_z)]; cur_z += bb
                if cur_z >= oh: v.append((ow / 2, -hi, oh)); face_normal = "tri_lev_one"
                else:
                     v += ((cur_x + bb_dif, -hi, cur_z), (last_x - bb_dif, -hi, cur_z)); cur_z += bt; y = (cur_z - oh) * y_step
                     v.append((ow / 2, -y, oh)); face_normal = "tri_lev_two"
                cur_x = last_x; cur_z = oh
                for i in v: verts.append(i)           
            counter += 1           
            #faces
            if face_normal == True:
                faces.append((p, p + 3, p + 2, p + 1)); faces.append((p + 1, p + 2, p + 5, p + 4)); faces.append((p + 4, p + 5, p + 7, p + 6))
            elif face_normal == "two":
                faces.append((p, p + 3, p + 2, p + 1)); faces.append((p + 1, p + 2, p + 5, p + 4))
            elif face_normal == "split":
                faces.append((p, p + 3, p + 2, p + 1)); faces.append((p + 1, p + 2, p + 5, p + 4)); faces.append((p + 4, p + 5, p + 7, p + 6)); faces.append((p + 6, p + 7, p + 9, p + 8))
            elif face_normal == "tri_lev_one":
                faces.append((p, p + 3, p + 2, p + 1)); faces.append((p + 1, p + 2, p + 4))
            elif face_normal == "tri_lev_two":
                faces.append((p, p + 3, p + 2, p + 1)); faces.append((p + 1, p + 2, p + 5, p + 4)); faces.append((p + 4, p + 5, p + 6))
    return (verts, faces)

def tin_normal(oh, ow, is_slope, slope, faces, verts):
    cur_x = 0.0; cur_z = 0.0; con = 39.3701
    osi = (1 / 16) / con; hi = 0.5 / con; eti = 0.8 / con; nti = 0.9 / con; fei = (5 / 8) / con; tei = (3 / 8) / con; nfei = 0.6875 / con ; oi = 1 / con; otqi = 1.75 / con
    #one sixtenth in,   half in,  eight tenths inch, nine tenths,  five eigths,  three eights inch,  not five eights, one inch,  one &  three quarter inch
    ofei = oi + fei; ohi = oi + hi; qi = hi / 2; ei = (1 / 8) / con; tqi = otqi - oi
    if is_slope == True:
        square = oh - ((slope * (ow / 2)) / 12) #z height where slope starts
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / ow) - 0.01; square = oh - ((slope * (ow / 2)) / 12)
        hid = (hi * slope) / 12; feid = (fei * slope) / 12; nfeid = (nfei * slope) / 12; cur_z = square  
    while cur_x < ow:
        p = len(verts); face_normal = False
        #verts  
        if is_slope == False: #flat
            v2 = []; a_e = False #verts holder 2, at_edge for putting in last set of verts  
            for i in range(4):
                if i == 0: y = -osi
                else: y = 0.0
                v = ((cur_x, y, cur_z), (cur_x, y, oh), (cur_x + hi, -eti + y, cur_z), (cur_x + hi, -eti + y, oh), (cur_x + fei, -nti + y, cur_z), (cur_x + fei, -nti + y, oh)) #Left Top Of Rib
                v += ((cur_x + nfei, -oi + y, cur_z), (cur_x + nfei, -oi + y, oh)); cur_x += otqi; v += ((cur_x - nfei, -oi + y, cur_z), (cur_x - nfei, -oi + y, oh), (cur_x - fei, -nti + y, cur_z) ,(cur_x - fei, -nti + y, oh)) #Right Mid Rib
                v += ((cur_x - hi, -eti + y, cur_z), (cur_x - hi, -eti + y, oh), (cur_x, 0.0 + y, cur_z), (cur_x, 0.0 + y, oh)); cur_x += ofei
                for i in range(2):
                    v += ((cur_x, 0.0, cur_z), (cur_x, 0.0, oh), (cur_x + qi, -ei, cur_z), (cur_x + qi, -ei, oh)); cur_x += oi
                    v += ((cur_x, -ei, cur_z), (cur_x, -ei, oh), (cur_x + qi, 0.0, cur_z), (cur_x + qi, 0.0, oh)); cur_x += ohi + qi
                cur_x += ei
                for i in v: v2.append(i)
            v2 += ((cur_x, 0.0, cur_z), (cur_x, 0.0, oh), (cur_x + hi, -eti, cur_z), (cur_x + hi, -eti, oh), (cur_x + fei, -nti, cur_z), (cur_x + fei, -nti, oh)) #Left Top Of Rib
            v2 += ((cur_x + nfei, -oi, cur_z), (cur_x + nfei, -oi, oh)); cur_x += otqi; v2 += ((cur_x - nfei, -oi, cur_z), (cur_x - nfei, -oi, oh), (cur_x - fei, -nti, cur_z) ,(cur_x - fei, -nti, oh)) #Right Mid Rib
            v2 += ((cur_x - hi, -eti, cur_z), (cur_x - hi, -eti, oh), (cur_x, 0.0, cur_z), (cur_x, 0.0, oh)); cur_x -= otqi; face_normal = True; vts = []   
            if cur_x + otqi > ow: #chop off extra
                counter = 0
                for i in v2:
                    if i[0] <= ow: vts.append(i)
                    elif i[0] > ow and a_e == False: 
                        a_e = True; b_o = v2[counter - 1]; f_o = i; dif_x = f_o[0] - b_o[0]; dif_y = f_o[1] - b_o[1]; r_r = dif_y / dif_x; b = b_o[1] - (r_r * b_o[0])
                        y2 = (ow * r_r) + b; vts.append((ow, y2, cur_z)); vts.append((ow, y2, oh))
                    counter += 1  
                f_t = int((len(vts) / 2) - 1)
            else: vts = v2; f_t = 71                        
            for i in vts: verts.append(i)
        elif is_slope == True: #slopped
            v2 = []; a_e = False
            for i in range(4):
                #calculate z's coming up for rib
                x_list = [cur_x, cur_x + hi, cur_x + fei, cur_x + nfei, cur_x + otqi - nfei, cur_x + otqi - fei, cur_x + otqi - hi, cur_x + otqi, cur_x + otqi + ofei]
                z = []
                for x in x_list:
                    if x <= ow / 2: cz = oh - ((((ow / 2) - x) * slope) / 12)
                    else: cz = oh - (((x - (ow / 2)) * slope) / 12)
                    z.append(cz)
                if i == 0: y = -osi
                else: y = 0.0
                v = ((cur_x, y, 0.0), (cur_x, y, z[0]), (cur_x + hi, -eti + y, 0.0), (cur_x + hi, -eti + y, z[1]))
                v += ((cur_x + fei, -nti + y, 0.0), (cur_x + fei, -nti + y, z[2]), (cur_x + nfei, -oi + y, 0.0), (cur_x + nfei, -oi + y, z[3])); cur_x += otqi
                v += ((cur_x - nfei, -oi + y, 0.0), (cur_x - nfei, -oi + y, z[4]), (cur_x - fei, -nti + y, 0.0), (cur_x - fei, -nti + y, z[5]))
                v += ((cur_x - hi, -eti + y, 0.0), (cur_x - hi, -eti + y, z[6]), (cur_x, 0.0 + y, 0.0), (cur_x, 0.0 + y, z[7])); cur_x += ofei; cur_z = z[8]
                for i in range(2):
                    x_list = [cur_x, cur_x + qi, cur_x + oi, cur_x + oi + qi, cur_x + ohi + oi + qi]
                    z = []
                    for x in x_list:
                        if x <= ow / 2: cz = oh - ((((ow / 2) - x) * slope) / 12)
                        else: cz = oh - (((x - (ow / 2)) * slope) / 12)
                        z.append(cz)
                    v += ((cur_x, 0.0, 0.0), (cur_x, 0.0, z[0]), (cur_x + qi, -ei, 0.0), (cur_x + qi, -ei, z[1])); cur_x += oi
                    v += ((cur_x, -ei, 0.0), (cur_x, -ei, z[2]), (cur_x + qi, 0.0, 0.0), (cur_x + qi, 0.0, z[3])); cur_x += ohi + qi; cur_z = z[4]
                cur_x += ei
                if cur_x <= ow / 2: cur_z = oh - ((((ow / 2) - cur_x) * slope) / 12)
                else: cur_z = oh - (((cur_x - (ow / 2)) * slope) / 12)
                for i in v: v2.append(i)
            x_list = [cur_x, cur_x + hi, cur_x + fei, cur_x + nfei, cur_x + otqi - nfei, cur_x + otqi - fei, cur_x + otqi - hi, cur_x + otqi, cur_x - otqi]
            z = []
            for x in x_list:
                if x <= ow / 2: cz = oh - ((((ow / 2) - x) * slope) / 12)
                else: cz = oh - (((x - (ow / 2)) * slope) / 12)
                z.append(cz)
            v2 += ((cur_x, 0.0, 0.0), (cur_x, 0.0, z[0]), (cur_x + hi, -eti, 0.0), (cur_x + hi, -eti, z[1]))
            v2 += ((cur_x + fei, -nti, 0.0), (cur_x + fei, -nti, z[2]), (cur_x + nfei, -oi, 0.0), (cur_x + nfei, -oi, z[3])); cur_x += otqi
            v2 += ((cur_x - nfei, -oi, 0.0), (cur_x - nfei, -oi, z[4]), (cur_x - fei, -nti, 0.0), (cur_x - fei, -nti, z[5]))
            v2 += ((cur_x - hi, -eti, 0.0), (cur_x - hi, -eti, z[6]), (cur_x, 0.0, 0.0), (cur_x, 0.0, z[7])) 
            cur_x -= otqi; face_normal = True; vts = []; cur_z = z[8]
            #finalize verts
            if cur_x + otqi > ow: #chop off extra
                counter = 0
                for i in v2:
                    if i[0] <= ow: vts.append(i)
                    elif i[0] > ow and a_e == False: 
                        a_e = True; b_o = v2[counter - 1]; f_o = i; dif_x = f_o[0] - b_o[0]; dif_y = f_o[1] - b_o[1]; r_r = dif_y / dif_x; b = b_o[1] - (r_r * b_o[0])
                        y2 = (ow * r_r) + b; vts.append((ow, y2, 0.0)); vts.append((ow, y2, square))
                    counter += 1  
                f_t = int((len(vts) / 2) - 1)
            elif cur_x - 0.9144 < ow / 2 and cur_x > ow / 2: #middle sheet
                counter = 0
                for i in v2:
                    vts.append(i)
                    if i[0] < ow / 2 and (v2[counter + 1])[0] > ow / 2: #place middle set
                        b_o = i; f_o = v2[counter + 1]; dif_x = f_o[0] - b_o[0]; dif_y = f_o[1] - b_o[1]; r_r = dif_y / dif_x; b = b_o[1] - (r_r * b_o[0])
                        y2 = ((ow / 2)* r_r) + b; vts.append((ow / 2, y2, 0.0)); vts.append((ow / 2, y2, oh))
                    counter += 1  
                f_t = int((len(vts) / 2) - 1)        
            else: vts = v2; f_t = 71              
            for set in vts: verts.append(set)            
        #faces
        if face_normal == True:
            for i in range(f_t):
                faces.append((p, p + 2, p + 3, p + 1)); p += 2  
    return (verts, faces)

def tin_angular(oh, ow, is_slope, slope, faces, verts):
    cur_x = 0.0; cur_z = 0.0; con = 39.3701
    #variables
    osi = (1 / 16) / con; hi = (1 / 2) / con; oqi = (5 / 4) / con; ohi = (3 / 2) / con; ti = ohi + hi; qi = (1 / 4) / con; ei = (1 / 8) / con
    if is_slope == True:
        square = oh - ((slope * (ow / 2)) / 12) #z height where slope starts
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / ow) - 0.01; square = oh - ((slope * (ow / 2)) / 12)
        cur_z = square
    while cur_x < ow:
        p = len(verts); face_normal = False
        #verts
        if is_slope == False: #flat
            v2 = []; a_e = False
            for i in range(3):
                if i == 0: y = -osi
                else: y = 0.0
                v = ((cur_x, y, 0.0) ,(cur_x, y, oh), (cur_x + hi, -oqi + y, 0.0), (cur_x + hi, -oqi + y, oh), (cur_x + ohi, -oqi + y, 0.0), (cur_x + ohi, -oqi + y, oh))
                v += ((cur_x + ti, 0.0 + y, 0.0), (cur_x + ti, 0.0 + y, oh)); cur_x += 2 * ti
                for i in range(2):
                    v += ((cur_x, 0.0, 0.0), (cur_x, 0.0, oh), (cur_x + qi, -ei, 0.0), (cur_x + qi, -ei, oh), (cur_x + ohi, -ei, 0.0), (cur_x + ohi, -ei, oh)); cur_x += ohi
                    v += ((cur_x + qi, 0.0, 0.0), (cur_x + qi, 0.0, oh)); cur_x += qi + ti + hi
                cur_x -= hi
                for i in v: v2.append(i)
            v2 += ((cur_x, 0.0, 0.0) ,(cur_x, 0.0, oh), (cur_x + hi, -oqi, 0.0), (cur_x + hi, -oqi, oh), (cur_x + ohi, -oqi, 0.0), (cur_x + ohi, -oqi, oh))
            v2 += ((cur_x + ti, 0.0, 0.0), (cur_x + ti, 0.0, oh)); vts = []; face_normal = True
            if cur_x + ti > ow: #cut off extra
                counter = 0
                for i in v2:
                    if i[0] <= ow: vts.append(i)
                    elif i[0] > ow and a_e == False: 
                        a_e = True; b_o = v2[counter - 1]; f_o = i; dif_x = f_o[0] - b_o[0]; dif_y = f_o[1] - b_o[1]; r_r = dif_y / dif_x; b = b_o[1] - (r_r * b_o[0])
                        y2 = (ow * r_r) + b; vts.append((ow, y2, cur_z)); vts.append((ow, y2, oh))
                    counter += 1  
                f_t = int((len(vts) / 2) - 1)
            else: vts = v2; f_t = 38                    
            for i in vts: verts.append(i)
        elif is_slope == True: #slope
            v2 = []; a_e = False
            for i in range(3):
                if i == 0: y = -osi
                else: y = 0.0
                x_list = [cur_x, cur_x + hi, cur_x + ohi, cur_x + ti, cur_x + ti + ti]; z = []
                for x in x_list:
                    if x <= ow / 2: cz = oh - ((((ow / 2) - x) * slope) / 12)
                    else: cz = oh - (((x - (ow / 2)) * slope) / 12)  
                    z.append(cz)    
                v = ((cur_x, y, 0.0) ,(cur_x, y, z[0]), (cur_x + hi, -oqi + y, 0.0), (cur_x + hi, -oqi + y, z[1]), (cur_x + ohi, -oqi + y, 0.0), (cur_x + ohi, -oqi + y, z[2]))
                v += ((cur_x + ti, 0.0 + y, 0.0), (cur_x + ti, 0.0 + y, z[3])); cur_x += 2 * ti; cur_z = z[4]
                for i in range(2):
                    x_list = [cur_x, cur_x + qi, cur_x + ohi, cur_x + ohi + qi, cur_x + ohi + qi + ti + hi]; z = []
                    for x in x_list:
                        if x <= ow / 2: cz = oh - ((((ow / 2) - x) * slope) / 12)
                        else: cz = oh - (((x - (ow / 2)) * slope) / 12)  
                        z.append(cz)
                    v += ((cur_x, 0.0, 0.0), (cur_x, 0.0, z[0]), (cur_x + qi, -ei, 0.0), (cur_x + qi, -ei, z[1]), (cur_x + ohi, -ei, 0.0), (cur_x + ohi, -ei, z[2])); cur_x += ohi
                    v += ((cur_x + qi, 0.0, 0.0), (cur_x + qi, 0.0, z[3])); cur_x += qi + ti + hi; cur_z = z[4]
                cur_x -= hi
                if cur_x <= ow / 2: cur_z = oh - ((((ow / 2) - cur_x) * slope) / 12)
                else: cur_z = oh - (((cur_x - (ow / 2)) * slope) / 12)
                for set in v: v2.append(set)
            x_list = [cur_x, cur_x + hi, cur_x + ohi, cur_x + ti]; z = []
            for x in x_list:
                if x <= ow / 2: cz = oh - ((((ow / 2) - x) * slope) / 12)
                else: cz = oh - (((x - (ow / 2)) * slope) / 12)  
                z.append(cz) 
            v2 += ((cur_x, 0.0, 0.0) ,(cur_x, 0.0, z[0]), (cur_x + hi, -oqi, 0.0), (cur_x + hi, -oqi, z[1]), (cur_x + ohi, -oqi, 0.0), (cur_x + ohi, -oqi, z[2]))
            v2 += ((cur_x + ti, 0.0, 0.0), (cur_x + ti, 0.0, z[3])); vts = []; face_normal = True; cur_z = z[0]
            if cur_x + ti > ow: #cut off extra
                counter = 0
                for i in v2:
                    if i[0] <= ow: vts.append(i)
                    elif i[0] > ow and a_e == False: 
                        a_e = True; b_o = v2[counter - 1]; f_o = i; dif_x = f_o[0] - b_o[0]; dif_y = f_o[1] - b_o[1]; r_r = dif_y / dif_x; b = b_o[1] - (r_r * b_o[0])
                        y2 = (ow * r_r) + b; vts.append((ow, y2, 0.0)); vts.append((ow, y2, square))
                    counter += 1  
                f_t = int((len(vts) / 2) - 1)
            elif cur_x - 0.9144 < ow / 2 and cur_x > ow / 2: #middle sheet
                counter = 0
                for i in v2:
                    vts.append(i)
                    if i[0] < ow / 2 and (v2[counter + 1])[0] > ow / 2: #place middle set
                        b_o = i; f_o = v2[counter + 1]; dif_x = f_o[0] - b_o[0]; dif_y = f_o[1] - b_o[1]; r_r = dif_y / dif_x; b = b_o[1] - (r_r * b_o[0])
                        y2 = ((ow / 2)* r_r) + b; vts.append((ow / 2, y2, 0.0)); vts.append((ow / 2, y2, oh))
                    counter += 1  
                f_t = int((len(vts) / 2) - 1) 
            else: vts = v2; f_t = 38                    
            for i in vts: verts.append(i)      
        #faces
        if face_normal == True:
            for i in range(f_t):
                faces.append((p, p + 2, p + 3, p + 1)); p += 2  
    return (verts, faces)

def tin_screws(oh, ow, is_slope, slope): #screw heads
    verts, faces = [], []
    #for each row determine row start, row end
    #determine correct number of rows
    MI = 39.3701 #metric_inch    
    rows = int((oh - 4 / MI) / (16 / MI))
    
    row_offset = (oh - 4 / MI) / rows
    column_offset = 9 / MI
    dia_w = 0.25 / MI
    dia_s = 0.15 / MI
    
    x_off = 0.05715
    cur_z = 2 / MI
    
    print(ow)
    
    while cur_z < oh:
        cur_x = x_off
        
        while cur_x < ow:
            #confirm if screw head exists
            exists = True
            
            if is_slope:
                #calculate height at current x value
                cur_h = oh                
                if cur_x < (ow / 2):
                    if cur_z > ((slope / 12) * (cur_x - (ow / 2))) + oh:
                        exists = False
                else:
                    if cur_z > ((-slope / 12) * (cur_x - (ow / 2))) + oh:
                        exists = False   
            
            if exists:
                p = len(verts)                            
                #place screw
                #step by a sixteenth of an inch each time
                for i in range(2):
                    for j in range(-30, 330, 60): #angle
                        x, z = point_rotation((cur_x + dia_w, cur_z), (cur_x, cur_z), radians(j))
                        verts += [(x, i * -((1 / 16) / MI), z)]   
                for i in range(2):
                    for j in range(-30, 330, 60): #angle
                        x, z = point_rotation((cur_x + dia_s, cur_z), (cur_x, cur_z), radians(j))
                        verts += [(x, -((1 / 16) / MI) + (i * -(0.2 / MI)), z)]  
                        
                #faces
                for i in range(3):
                    tp = p
                    for j in range(5):
                        faces += [(tp, tp + 1, tp + 7, tp + 6)]
                        tp += 1
                    faces += [(tp, tp - 5, tp + 1, tp + 6)]
                    p += 6  
                #top two faces
                faces += [(p, p + 1, p + 2, p + 5), (p + 5, p + 2, p + 3, p + 4)]
            
            cur_x += column_offset
            
        cur_z += row_offset            
    
    return (verts, faces)

def bricks(oh, ow, is_slope, slope, b_w, b_h, b_offset, gap, ran_offset, b_vary, faces, verts, is_corner, is_invert, is_left, is_right): #bricks
    cur_z = 0.0 ; 
    if b_offset > 0: off = 1 / (100 / b_offset)  
    else: off = 0.0
    last_x = ow; depth = 3.5 / 39.3701; offset = False
    while cur_z < oh:   
        cur_x = 0.0
        if ran_offset == True:
            off = uniform(0.1 * b_vary, 1.0 * b_vary)
        if is_corner == True:   
            if is_left == True:
                if is_invert == False and offset == False: cur_x = -(b_w / 2)
                elif is_invert == True and offset == True: cur_x = -(b_w / 2)
                else: cur_x = 0.0
            if is_right == True:
                last_x = ow + (b_w / 2)
        while cur_x < last_x:
            #verts
            if is_corner == False:
                face_normal = False; p = len(verts); b_w2 = b_w
                if cur_x == 0.0 and offset == True: b_w2 = b_w * off
                elif cur_x == 0.0 and offset == False and ran_offset == True: b_w2 = b_w * off
                elif cur_x + b_w2 > last_x: b_w2 = last_x - cur_x
                if cur_z + b_h > oh: b_h = oh - cur_z
                v = ((cur_x, 0.0, cur_z), (cur_x, -depth, cur_z), (cur_x + b_w2, -depth, cur_z), (cur_x + b_w2, 0.0, cur_z)); cur_z += b_h
                v += ((cur_x, 0.0, cur_z), (cur_x, -depth, cur_z), (cur_x + b_w2, -depth, cur_z), (cur_x + b_w2, 0.0, cur_z)); cur_z -= b_h
                cur_x += b_w2 + gap; face_normal = True
            else:
                 face_normal = False; p = len(verts); add = 0
                 #offset rows on left side
                 if is_left == False and offset == True and cur_x == 0.0: b_w2 = b_w / 2
                 else: b_w2 = b_w
                 #get end brick correct
                 if offset == False and is_invert == False and cur_x + b_w > ow: b_w2 = ow - cur_x; add = 1
                 elif offset == True and is_invert == False and cur_x + b_w > last_x: b_w2 = last_x - cur_x; add = 0                 
                 elif offset == True and is_invert == True and cur_x + b_w > ow: b_w2 = ow - cur_x; add = 1
                 elif offset == False and is_invert == True and cur_x + b_w > last_x: b_w2 = last_x - cur_x; add = 0                 
                 if cur_z + b_h > oh: b_h = oh - cur_z
                 v = ((cur_x, 0.0, cur_z), (cur_x, -depth, cur_z), (cur_x + b_w2, -depth, cur_z), (cur_x + b_w2, 0.0, cur_z)); cur_z += b_h
                 v += ((cur_x, 0.0, cur_z), (cur_x, -depth, cur_z), (cur_x + b_w2, -depth, cur_z), (cur_x + b_w2, 0.0, cur_z)); cur_z -= b_h               
                 cur_x += b_w2 + gap; face_normal = True; cur_x += add
            for i in v: verts.append(i)
            #faces
            if face_normal == True:
                f = ((p, p + 3, p + 2, p + 1), (p, p + 1, p + 5, p + 4), (p + 1, p + 2, p + 6, p + 5), (p + 2, p + 3, p + 7, p + 6),
                        (p + 4, p + 5, p + 6, p + 7), (p, p + 4, p + 7, p + 3))
                for i in f: faces.append(i)
        cur_z += gap + b_h
        if offset == False: offset = True
        elif offset == True: offset = False
    return (verts, faces)

def bricks_cut(oh, ow, slope, is_corner, b_w): #creates object to cut slope
    verts = []; faces = []
    if is_corner == False:
        square = oh - ((slope * (ow / 2)) / 12) #z height where slope starts
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / ow) - 0.01; square = oh - ((slope * (ow / 2)) / 12)
        v = ((0.0, 0.5, square), (0.0, -0.5, square), (ow / 2, 0.5, oh), (ow / 2, -0.5, oh), (ow, 0.5, square), (ow, -0.5, square))
        v += ((0.0, 0.5, oh + 0.5), (0.0, -0.5, oh + 0.5), (ow / 2, 0.5, oh + 0.5), (ow / 2, -0.5, oh + 0.5), (ow, 0.5, oh + 0.5), (ow, -0.5, oh + 0.5))
    elif is_corner == True:
        square = oh - ((slope * ((ow + (2 * b_w)) / 2)) / 12)
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / (ow + (2 * b_w))) - 0.01; square = oh - ((slope * ((ow + (2 * b_w)) / 2)) / 12)
        v = ((-b_w, 0.5, square), (-b_w, -0.5, square), (ow / 2, 0.5, oh), (ow / 2, -0.5, oh), (ow + b_w, 0.5, square), (ow + b_w, -0.5, square))
        v += ((-b_w, 0.5, oh + 0.5), (-b_w, -0.5, oh + 0.5), (ow / 2, 0.5, oh + 0.5), (ow / 2, -0.5, oh + 0.5), (ow + b_w, 0.5, oh + 0.5), (ow + b_w, -0.5, oh + 0.5))
    for i in v: verts.append(i)
    f = ((0, 2, 3, 1), (2, 4, 5, 3), (0, 1, 7, 6), (1, 3, 9, 7), (3, 5, 11, 9), (5, 4, 10, 11), (4, 2, 8, 10), (2, 0, 6, 8), (6, 7, 9, 8), (8, 9, 11, 10))
    for i in f: faces.append(i)
    return (verts, faces)

def bricks_mortar(oh, ow, m_d, is_slope, slope, is_corner, is_left, is_right, convert, b_w, m_gap, bricks, x_off): #creates mortar object
    verts = []; faces = []; depth = 3.5 / 39.3701
    if bricks == True: y = depth - m_d
    else: y = m_d
    bw = round(b_w / 39.3701, 5); gap = round(m_gap / 39.3701, 5)
    #expand mortar if brick has usable corners or if it is a convert object
    x = 0.0; fx = ow
    if convert == "convert":
        fx = ow + (bw / 2)
    elif is_corner == True:
        if is_left == True: x = -(bw / 2) + gap
        if is_right == True: fx = (bw / 2) - gap + ow
    if is_slope == True:
        square = oh - ((slope * (ow / 2)) / 12) #z height where slope starts
        if square <= 0: #recalculate slope if it would put the edges below zero
            slope = ((24 * oh) / ow) - 0.01; square = oh - ((slope * (ow / 2)) / 12)
        ls = square; rs = square
        #get correct square height if usable corners is enabled
        if is_corner == True:
            if is_left == True: ls = oh - ((slope * ((ow / 2) + ((bw / 2) - gap))) / 12)
            if is_right == True: rs = oh - ((slope * ((ow / 2) + ((bw / 2) - gap))) / 12)
    if is_slope == False:   
        v = ((x, 0.0, 0.0), (x, -y, 0.0), (fx, -y, 0.0), (fx, 0.0, 0.0), (x, 0.0, oh), (x, -y, oh), (fx, -y, oh), (fx, 0.0, oh))
        f = ((0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (0, 4, 7, 3), (4, 5, 6, 7))
    else:
        v = ((x, 0.0, 0.0), (x, -y, 0.0), (fx, -y, 0.0), (fx, 0.0, 0.0), (x, 0.0, ls), (x, -y, ls), (fx, -y, rs), (fx, 0.0, rs), (ow / 2, 0.0, oh), (ow / 2, -y, oh))   
        f = ((0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (0, 4, 7, 3), (4, 5, 9, 8), (5, 6, 9), (6, 7, 8, 9), (7, 4, 8))
    for i in v: verts.append(i) 
    for i in f: faces.append(i)
    out_verts = []
    for i in verts:
        l = list(i); l[0] += x_off
        out_verts.append(l)
    return (out_verts, faces)

def bricks_soldier(corner_data, b_h, gap, b_w, oh): #creates top row of bricks
    verts = []; faces = []
    d = 3.75 / 39.3701
    #corner data: x, z, far x, far z    
    for i in corner_data:
        cur_x = i[0] + gap; cur_z = i[3]; bw2 = b_w
        if cur_z + b_w > oh: bw2 = oh - cur_z
        if cur_z < oh:  
            while cur_x < i[2]:
                bh2 = b_h; p = len(verts)
               
                if cur_x + b_h + gap > i[2]: bh2 = i[2] - cur_x - gap 
                
                v = ((cur_x, 0.0, cur_z), (cur_x, -d, cur_z), (cur_x + bh2, -d, cur_z), (cur_x + bh2, 0.0, cur_z)); cur_z += bw2
                v += ((cur_x, 0.0, cur_z), (cur_x, -d, cur_z), (cur_x + bh2, -d, cur_z), (cur_x + bh2, 0.0, cur_z)); cur_z -= bw2
                cur_x += gap + bh2
                
                for i2 in v: verts.append(i2)
                f = ((p, p + 3, p + 2, p + 1), (p, p + 1, p + 5, p + 4), (p + 1, p + 2, p + 6, p + 5), (p + 2, p + 3, p + 7, p + 6), (p, p + 4, p + 7, p + 3), (p + 4, p + 5, p + 6, p + 7))
                for i2 in f: faces.append(i2)
    
    return (verts, faces)

def stone_sizes(num, columns, grid, total):
    p = []; o = []; n = num; rows = 0
    #find 7X5 block around number and collect them
    while n > columns - 1:
        n -= columns; rows += 1
    rows += 2
    for i in range(5):
        if rows >= 0:
            row = grid[rows * columns: (rows * columns) + columns]; pos = n + (rows * columns)  
            l = [pos - 3, pos - 2, pos - 1, pos, pos + 1, pos + 2, pos + 3]
            for i2 in l:
                if i2 in row:           
                    o.append(row[row.index(i2)])
                else:
                    o.append(False)   
        else:
            c = [o.append(False) for i2 in range(7)]
        rows -= 1
    n = num
    #figure possible sizes
    #1 X 2
    if o[10] != False: p.append((o[10], n)) 
    if o[24] != False: p.append((n, o[24]))
    #2 X 1
    if o[16] != False: p.append((o[16], n))
    if o[18] != False: p.append((n, o[18]))
    #2X2
    if o[9] != False and o[10] != False and o[16] != False: p.append((o[9], o[10], o[16], n))
    if o[16] != False and o[23] != False and o[24] != False: p.append((o[16], n, o[23], o[24]))
    if o[10] != False and o[11] != False and o[18] != False: p.append((o[10], o[11], n, o[18]))
    if o[18] != False and o[24] != False and o[25] != False: p.append((n, o[18], o[24], o[25]))
    #3X1
    if o[15] != False and o[16] != False: p.append((o[15], o[16], n))
    if o[16] != False and o[18] != False: p.append((o[16], n, o[18]))
    if o[18] != False and o[19] != False: p.append((n, o[18], o[19]))
    #3X2
    if o[8] != False and o[9] != False and o[10] != False and o[15] != False and o[16] != False: p.append((o[8], o[9], o[10], o[15], o[16], n))
    if o[9] != False and o[10] != False and o[11] != False and o[16] != False and o[18] != False: p.append((o[9], o[10], o[11], o[16], n, o[18]))
    if o[10] != False and o[11] != False and o[12] != False and o[18] != False and o[19] != False: p.append((o[10], o[11], o[12], n, o[18], o[19]))
    if o[15] != False and o[16] != False and o[22] != False and o[23] != False and o[24] != False: p.append((o[15], o[16], n, o[22], o[23], o[24]))
    if o[16] != False and o[18] != False and o[23] != False and o[24] != False and o[25] != False: p.append((o[16],n,  o[18], o[23], o[24], o[25]))
    if o[18] != False and o[19] != False and o[24] != False and o[25] != False and o[26] != False: p.append((n, o[18], o[19], o[24], o[25], o[26]))
    #3X3
    #first row
    if o[1] != False and o[2] != False and o[3] != False and o[8] != False and o[9] != False and o[10] != False and o[15] != False and o[16] != False:
        p.append((o[1], o[2], o[3], o[8], o[9], o[10], o[15], o[16], n))
    if o[2] != False and o[3] != False and o[4] != False and o[9] != False and o[10] != False and o[11] != False and o[16] != False and o[18] != False:
        p.append((o[2], o[3], o[4], o[9], o[10], o[11], o[16], n, o[18]))
    if o[3] != False and o[4] != False and o[5] != False and o[10] != False and o[11] != False and o[12] != False and o[18] != False and o[19] != False:
        p.append((o[3], o[4], o[5], o[10], o[11], o[12], n, o[18], o[19]))
    #second row
    if o[8] != False and o[9] != False and o[10] != False and o[15] != False and o[16] != False and o[22] != False and o[23] != False and o[24] != False:
        p.append((o[8], o[9], o[10], o[15], o[16], n, o[22], o[23], o[24]))
    if o[9] != False and o[10] != False and o[11] != False and o[16] != False and o[18] != False and o[23] != False and o[24] != False and o[25] != False:
        p.append((o[9], o[10], o[11], o[16], n, o[18], o[23], o[24], o[25]))
    if o[10] != False and o[11] != False and o[12] != False and o[18] != False and o[19] != False and o[24] != False and o[25] != False and o[26] != False:
        p.append((o[10], o[11], o[12], n, o[18], o[19], o[24], n, o[25], o[26]))
    #thrid row
    if o[15] != False and o[16] != False and o[22] != False and o[23] != False and o[24] != False and o[29] != False and o[30] != False and o[31] != False:
        p.append((o[15], o[16], n, o[22], o[23], o[24], o[29], o[30], o[31]))
    if o[16] != False and o[18] != False and o[23] != False and o[24] != False and o[25] != False and o[30] != False and o[31] != False and o[32] != False:
        p.append((o[16], n, o[18], o[23], o[24], o[25], o[30], o[31], o[32]))
    if o[18] != False and o[19] != False and o[24] != False and o[25] != False and o[26] != False and o[31] != False and o[32] != False and o[33] != False:
        p.append((n, o[18], o[19], o[24], o[25], o[26], o[31], n, o[32], o[33]))             
    #4X3
    #first row
    if o[0] != False and o[1] != False and o[2] != False and o[3] != False and o[7] != False and o[8] != False and o[9] != False and o[10] != False \
        and o[14] != False and o[15] != False and o[16] != False: p.append((o[0], o[1], o[2], o[3], o[7], o[8], o[9], o[10], o[14], o[15], o[16], n))
    if o[1] != False and o[2] != False and o[3] != False and o[4] != False and o[8] != False and o[9] != False and o[10] != False and o[11] != False \
        and o[15] != False and o[16] != False and o[18] != False: p.append((o[1], o[2], o[3], o[4], o[8], o[9], o[10], o[11], o[15], o[16], n, o[18])) 
    if o[2] != False and o[3] != False and o[4] != False and o[5] != False and o[9] != False and o[10] != False and o[11] != False and o[12] != False \
        and o[16] != False and o[18] != False and o[19] != False: p.append((o[2], o[3], o[4], o[5], o[9], o[10], o[11], o[12], o[16], n, o[18], o[19])) 
    if o[3] != False and o[4] != False and o[5] != False and o[6] != False and o[10] != False and o[11] != False and o[12] != False and o[13] != False \
        and o[18] != False and o[19] != False and o[20] != False: p.append((o[3], o[4], o[5], o[6], o[10], o[11], o[12], o[13], n, o[18], o[19], o[20]))
    #second row
    if o[7] != False and o[8] != False and o[9] != False and o[10] != False and o[14] != False and o[15] != False and o[16] != False and o[21] != False \
        and o[22] != False and o[23] != False and o[24] != False: p.append((o[7], o[8], o[9], o[10], o[14], o[15], o[16], n, o[21], o[22], o[23], o[24]))
    if o[8] != False and o[9] != False and o[10] != False and o[11] != False and o[15] != False and o[16] != False and o[18] != False and o[22] != False \
        and o[23] != False and o[24] != False and o[25] != False: p.append((o[8], o[9], o[10], o[11], o[15], o[16], n, o[18], o[22], o[23], o[24], o[25]))
    if o[9] != False and o[10] != False and o[11] != False and o[12] != False and o[16] != False and o[18] != False and o[19] != False and o[23] != False \
        and o[24] != False and o[25] != False and o[26] != False: p.append((o[9], o[10], o[11], o[12], o[16], n, o[18], o[19], o[23], o[24], o[25], o[26]))
    if o[10] != False and o[11] != False and o[12] != False and o[13] != False and o[18] != False and o[19] != False and o[20] != False and o[24] != False \
        and o[25] != False and o[26] != False and o[27] != False: p.append((o[10], o[11], o[12], o[13], n, o[18], o[19], o[20], o[24], o[25], o[26], o[27]))
    #third row
    if o[14] != False and o[15] != False and o[16] != False and o[21] != False and o[22] != False and o[23] != False and o[24] != False and o[28] != False \
        and o[29] != False and o[30] != False and o[31] != False: p.append((o[14], o[15], o[16], n, o[21], o[22], o[23], o[24], o[28], o[29], o[30], o[31]))
    if o[15] != False and o[16] != False and o[18] != False and o[22] != False and o[23] != False and o[24] != False and o[25] != False and o[29] != False \
        and o[30] != False and o[31] != False and o[32] != False: p.append((o[15], o[16], n, o[18], o[22], o[23], o[24], o[25], o[29], o[30], o[31], o[32]))
    if o[16] != False and o[18] != False and o[19] != False and o[23] != False and o[24] != False and o[25] != False and o[26] != False and o[30] != False \
        and o[31] != False and o[32] != False and o[33] != False: p.append((o[16], n, o[18], o[19], o[23], o[24], o[25], o[26], o[30], o[31], o[32], o[33]))
    if o[18] != False and o[19] != False and o[20] != False and o[24] != False and o[25] != False and o[26] != False and o[27] != False and o[31] != False \
        and o[32] != False and o[33] != False and o[34] != False: p.append((n, o[18], o[19], o[20], o[24], o[25], o[26], o[27], o[31], o[32], o[33], o[34]))
    return p

def stone_grid(oh, ow, avw, avh, sr): #generate grid and figure stone sizes
    hh = avh / 2; hw = avw / 2
    rows = int(oh / hh); columns = int(ow / hw)
    hh2 = oh / rows; hw2 = ow / columns
    grid = [i for i in range(rows * columns)]; total = len(grid); out = []
    clist = grid[:] #list to have numbers chosen from   
    while clist != []:
        #pick number choice
        if sr != 0:
            num = choice(clist)
        else:
            num = clist[0]
        #calculate possible sizes for this number   
        possible = stone_sizes(num, columns, grid, total)
        twos = []; threes = []; fours = []; sixs = []; nines = []; twelves = []
        for i in possible:
            if len(i) == 2: twos.append(i)
            elif len(i) == 3: threes.append(i)
            elif len(i) == 4: fours.append(i)
            elif len(i) == 6: sixs.append(i)
            elif len(i) == 9: nines.append(i)
            elif len(i) == 12: twelves.append(i)
        #probability
        rs = 100 - sr #flip 0 -> 100 and 100 -> 0
        pick = []
        if twos != []: c = [pick.append("two") for i in range(int((-0.105 * rs) + 10))]
        if threes != []: c = [pick.append("three") for i in range(int((-0.11 * rs) + 10))]
        if fours != []: c = [pick.append("four") for i in range(int((-0.09 * rs) + 10))]
        if sixs != []: c = [pick.append("six") for i in range(int((-0.12 * rs) + 10))]
        if nines != []: c = [pick.append("nine") for i in range(int((-0.14 * rs) + 10))]
        if twelves != []: c = [pick.append("twelve") for i in range(int((-0.15 * rs) + 10))]
        if sr != 0:
            c = [pick.append("one") for i in range (int((-0.14 * rs) + 10))]
        if pick == []: pick.append("one")   
    
        size = choice(pick)
        #picked size
        if size == "two":
            rock = choice(twos); out.append(rock)
        elif size == "three":
            rock = choice(threes); out.append(rock)
        elif size == "four":
            rock = choice(fours); out.append(rock)
        elif size == "six":
            rock = choice(sixs); out.append(rock)
        elif size == "nine":
            rock = choice(nines); out.append(rock)
        elif size == "twelve":
            rock = choice(twelves); out.append(rock)
        elif size == "one":
            rock = [num, num]; del rock[0]; out.append(rock)
        #update lists
        for i in rock:
            clist.remove(i)
            grid[i] = False
            
    return (out, columns, hh2, hw2)

def stone_faces(oh, ow, avw, avh, sr, br, b_gap): #convert grid data to faces
    verts = []; faces = []; g = b_gap / 2
    stones, columns, hh, hw = stone_grid(oh, ow, avw, avh, sr)
    h = hh - (2 * g); w = hw - (2 * g)
    #create verts
    for rock in stones:
        depth = 0.0508
        #calculate bump
        if br != 0:
            vary = depth * br * 0.0045
            y = uniform(depth - vary, depth + vary)
        else:
            y = depth
        p = len(verts); v = []
        if len(rock) == 1: #single stone
            x, z = stone_pos(rock[0], columns, hh, hw, g)
            v = ((x, 0.0, z), (x, -y, z), (x + w, -y, z), (x + w, 0.0, z), (x, 0.0, z + h), (x, -y, z + h), (x + w, -y, z + h), (x + w, 0.0, z + h))
        elif len(rock) == 2: #double stone
            if rock[1] == rock[0] + 1: #if in row
                j = (2 * w) + b_gap
                x, z = stone_pos(rock[0], columns, hh, hw, g)
                v = ((x, 0.0, z), (x, -y, z), (x + j, -y, z), (x + j, 0.0, z), (x, 0.0, z + h), (x, -y, z + h), (x + j, -y, z + h), (x + j, 0.0, z + h))                
            else: #in column
                j = (2 * h) + b_gap
                x, z = stone_pos(rock[1], columns, hh, hw, g)
                v = ((x, 0.0, z), (x, -y, z), (x + w, -y, z), (x + w, 0.0, z), (x, 0.0, z + j), (x, -y, z + j), (x + w, -y, z + j), (x + w, 0.0, z + j))                            
        elif len(rock) == 3: #triple stone
            x, z = stone_pos(rock[0], columns, hh, hw, g)
            j = (3 * w) + (2 * b_gap)
            v = ((x, 0.0, z), (x, -y, z), (x + j, -y, z), (x + j, 0.0, z), (x, 0.0, z + h), (x, -y, z + h), (x + j, -y, z + h), (x + j, 0.0, z + h)) 
        elif len(rock) == 4: #normal stone
            x, z = stone_pos(rock[2], columns, hh, hw, g)
            jx = (2 * w) + b_gap; jz = (2 * h) + b_gap
            v = ((x, 0.0, z), (x, -y, z), (x + jx, -y, z), (x + jx, 0.0, z), (x, 0.0, z + jz), (x, -y, z + jz), (x + jx, -y, z + jz), (x + jx, 0.0, z + jz)) 
        elif len(rock) == 6: #hex stone
            x, z = stone_pos(rock[3], columns, hh, hw, g)
            jx = (3 * w) + (2 * b_gap); jz = (2 * h) + b_gap
            v = ((x, 0.0, z), (x, -y, z), (x + jx, -y, z), (x + jx, 0.0, z), (x, 0.0, z + jz), (x, -y, z + jz), (x + jx, -y, z + jz), (x + jx, 0.0, z + jz))    
        elif len(rock) == 9: #nona stone
            x, z = stone_pos(rock[6], columns, hh, hw, g)
            jx = (3 * w) + (2 * b_gap); jz = (3 * h) + (2 * b_gap)
            v = ((x, 0.0, z), (x, -y, z), (x + jx, -y, z), (x + jx, 0.0, z), (x, 0.0, z + jz), (x, -y, z + jz), (x + jx, -y, z + jz), (x + jx, 0.0, z + jz)) 
        elif len(rock) == 12: #normal stone
            x, z = stone_pos(rock[8], columns, hh, hw, g)
            jx = (4 * w) + (3 * b_gap); jz = (3 * h) + (2 * b_gap)
            v = ((x, 0.0, z), (x, -y, z), (x + jx, -y, z), (x + jx, 0.0, z), (x, 0.0, z + jz), (x, -y, z + jz), (x + jx, -y, z + jz), (x + jx, 0.0, z + jz))     
                       
        for vert in v: verts.append(vert)   
        
        #faces
        f = ((p, p + 3, p + 2, p + 1), (p, p + 1, p + 5, p + 4), (p + 1, p + 2, p + 6, p + 5), (p + 2, p + 3, p + 7, p + 6), (p, p + 4, p + 7, p + 3), (p + 4, p + 5, p + 6, p + 7))
        for face in f: faces.append(face)
    return (verts, faces)

def stone_pos(num, columns, hh, hw, g):
    row = 0; column = 0; n = num
    while n >= columns:
        n -= columns; row += 1
    x = (n * hw) + g; z = (hh * row) + g
    return (x, z)

def UpdateSiding(self, context):    
    o = context.object; mats = []
    
    for i in o.data.materials:
        mats.append(i.name) 
    pre_scale = tuple(o.scale.copy())
    
    if tuple(o.scale.copy()) != (1.0, 1.0, 1.0) and o.from_dims != "none": #apply scale  
        bpy.ops.object.transform_apply(scale = True)              
    
    #update from_dims
    if o.dims == "none":
        dim = object_dimensions(o)
        o.dims = str(dim[0]) + ", " + str(dim[1])
    else:
        dim_temp = o.dims.split(",")
        dim = [float(dim_temp[0]), float(dim_temp[1])]
    
    #caclculate dimensions based on vertex locations
    #create object
    if o.object_add == "add":
        verts, faces, corner_data, corner_data_l, v, f = create_siding(context, o.mat, o.if_tin, o.if_wood, o.if_vinyl, o.is_slope, o.over_width,
                o.over_height, o.board_width, o.slope, o.is_width_vary, o.width_vary, o.is_cutout, o.num_cutouts,
                o.nc1, o.nc2, o.nc3, o.nc4, o.nc5, o.batten_width, o.board_space, o.is_length_vary, o.length_vary,
                o.max_boards, o.b_width, o.b_height, o.b_offset, o.b_gap, o.m_depth, o.b_ran_offset, o.b_vary, o.is_corner, o.is_invert, 
                o.is_soldier, o.is_left, o.is_right, o.av_width, o.av_height, o.s_random, o.b_random, o.x_offset)   
    elif o.object_add == "convert": 
        #figure out whether the x axis or the y axis is the long side
        if o.from_dims == "none": 
            ow = dim[0]; oh = dim[1]
        else: ow = dim[0]; oh = dim[1]
        o.from_dims = "something"     
        verts, faces, corner_data, corner_data_l, v, f = create_siding(context, o.mat, o.if_tin, o.if_wood, o.if_vinyl, o.is_slope, ow,
                oh, o.board_width, o.slope, o.is_width_vary, o.width_vary, o.is_cutout, o.num_cutouts,
                o.nc1, o.nc2, o.nc3, o.nc4, o.nc5, o.batten_width, o.board_space, o.is_length_vary, o.length_vary,
                o.max_boards, o.b_width, o.b_height, o.b_offset, o.b_gap, o.m_depth, o.b_ran_offset, o.b_vary, o.is_corner, o.is_invert, 
                o.is_soldier, o.is_left, o.is_right, o.av_width, o.av_height, o.s_random, o.b_random, o.x_offset) 
    emesh = o.data
       
    if o.object_add == "add":   
        mesh = bpy.data.meshes.new(name = "siding")
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges = True)
         
    elif o.object_add == "convert": #from object
        mesh = bpy.data.meshes.new(name = "siding")
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges = True)   
        if o.cut_name == "none": #if cutter object hasn't been created yet   
            for ob in context.scene.objects:
                ob.select = False
            cutter = bpy.data.objects.new(o.name + "_cutter", o.data.copy())            
            context.scene.objects.link(cutter); cutter.location = o.location.copy(); cutter.rotation_euler = o.rotation_euler.copy(); cutter.scale = o.scale.copy()
            o.cut_name = cutter.name; cutter.select = True; bpy.context.scene.objects.active = cutter
            bpy.ops.object.modifier_add(type = "SOLIDIFY"); pos = len(cutter.modifiers) - 1
            bpy.context.object.modifiers[pos].offset = 0
            bpy.context.object.modifiers[pos].thickness = 1   
            o.select = True; bpy.context.scene.objects.active = o
            #getting extreme position
            verts = [vert.co for vert in o.data.vertices] #get vertex data
            tup_verts = [vert.to_tuple() for vert in verts] #convert to tuples
            x = None; z = None; y = None; coords = []
            #find smallest x, y, and z positions
            for i in tup_verts: #find smallest x and z values
                if x == None: 
                    x = i[0]
                    y = i[1]
                elif i[0] < x:
                    x = i[0]
                    y = i[1]
                if z == None: z = i[2]
                elif i[2] < z: z = i[2]
            #find object rotation
            angle = object_rotation(o)
            position = o.matrix_world * Vector((x, y, z)) #get world space
            print(position)
            coords.append(tuple(position)); eur = (o.rotation_euler).copy()
            if o.is_cut == "none":
                o.angle_off = str(angle)
                eur.rotate_axis("Z", angle) #subtract rotation from object to make up for rotating up
            coords.append(eur)
        elif o.cut_name in bpy.data.objects: 
            (bpy.data.objects[o.cut_name]).name = o.name + "_cutter"; o.cut_name = o.name + "_cutter"; coords = [o.location.copy(), o.rotation_euler.copy()]
        else: 
            self.report({"ERROR"}, "Can't Find Cutter Object")
    for i in bpy.data.objects:
        if i.data == emesh:
            i.data = mesh
    emesh.user_clear()
    bpy.data.meshes.remove(emesh)
    
    #create battens if needed
    if v != []:
        bats = bpy.data.meshes.new("bats")
        bats.from_pydata(v, [], f)
        battens = bpy.data.objects.new("battens", bats)
        context.scene.objects.link(battens)
        battens.location = o.location; battens.rotation_euler = o.rotation_euler; battens.scale = o.scale
    #solidfy and bevel as needed
    if o.mat == "2": #vinyl
        bpy.context.scene.objects.active = o
        bpy.ops.object.modifier_add(type = "BEVEL"); pos = len(o.modifiers) - 1  
        bpy.context.object.modifiers[pos].width = 0.003048
        if o.if_vinyl == "3": bpy.context.object.modifiers[pos].use_clamp_overlap = False
        bpy.context.object.modifiers[pos].segments = o.res
        bpy.context.object.modifiers[pos].limit_method = "ANGLE"
        bpy.context.object.modifiers[pos].angle_limit = 1.4
        bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = o.modifiers[pos].name)
        bpy.ops.object.modifier_add(type = "SOLIDIFY"); pos = len(o.modifiers) - 1 
        bpy.context.object.modifiers[pos].thickness = 0.002
        bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = o.modifiers[pos].name)
    #solidify tin
    elif o.mat == "3": #tin
        bpy.context.scene.objects.active = o
        bpy.ops.object.modifier_add(type = "SOLIDIFY"); pos = len(o.modifiers) - 1 
        bpy.context.object.modifiers[pos].thickness = 0.0003429
        bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = o.modifiers[pos].name) 
    #bevel brick
    elif (o.mat in ("5", "6") or (o.mat == "1" and o.if_wood == "1")) and o.is_bevel == True:
        bpy.context.scene.objects.active = o
        bpy.ops.object.modifier_add(type = "BEVEL"); pos = len(o.modifiers) - 1
        if o.mat == "1": width = o.bevel_width
        else: width = 0.0024384
        bpy.context.object.modifiers[pos].width = width
        bpy.context.object.modifiers[pos].use_clamp_overlap = False 
        bpy.context.object.modifiers[pos].segments = o.res
        bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = o.modifiers[pos].name)  
    #cut slope in brick or stone
    if o.mat in ("5", "6") and o.object_add == "add":
        if o.is_slope == True:
            verts2, faces2 = bricks_cut(o.over_height, o.over_width, o.slope, o.is_corner, o.b_width)
            bc_s = bpy.data.meshes.new("slope_cut")
            bc_s.from_pydata(verts2, [], faces2)
            cut = bpy.data.objects.new("slope_cut", bc_s)
            context.scene.objects.link(cut)
            cut.location = o.location; cut.rotation_euler = o.rotation_euler; cut.scale = o.scale
            bpy.context.scene.objects.active = o; bpy.ops.object.modifier_add(type = "BOOLEAN"); pos = len(o.modifiers) - 1 
            bpy.context.object.modifiers[pos].object = cut
            bpy.context.object.modifiers[pos].operation = "DIFFERENCE"
            bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = o.modifiers[pos].name)
            for obs in context.scene.objects:
                if obs.name.startswith("slope_cut"): obs.select = True
                else: obs.select = False
            bpy.ops.object.delete(); o.select = True
    #add mortar
    if o.mat in ("5", "6"):
        if o.mat == "5": depth = round(o.m_depth, 5); bricks = True
        else: depth = round(o.s_mortar, 5); bricks = False
        if o.object_add == "convert":        
            verts3, faces3 = bricks_mortar(dim[0], dim[1], depth, o.is_slope, o.slope, o.is_corner, o.is_left, o.is_right, o.object_add, o.b_width, o.b_gap, bricks, o.x_offset)
        else:
            verts3, faces3 = bricks_mortar(o.over_height, o.over_width, depth, o.is_slope, o.slope, o.is_corner, o.is_left, o.is_right, o.object_add, o.b_width, o.b_gap, bricks, o.x_offset)
        bc_m = bpy.data.meshes.new("mortar"); bc_m.from_pydata(verts3, [], faces3)  
        mortar = bpy.data.objects.new("mortar", bc_m); context.scene.objects.link(mortar)
        mortar.location = o.location; mortar.rotation_euler = o.rotation_euler; mortar.scale = o.scale; enter = True
        for i in mats:
            if "mortar_" in i or len(mats) >= 2: enter = False
        if enter == True:
            mat = bpy.data.materials.new("mortar_temp"); mat.use_nodes = True; mortar.data.materials.append(mat)
        elif enter == False:
            mat = bpy.data.materials.get(mats[1]); mortar.data.materials.append(mat)
        #bevel edges slightly so that a subdivision modifer won't mess it up
        o.select = False; mortar.select = True; context.scene.objects.active = mortar
        bpy.ops.object.modifier_add(type = "BEVEL")
        mortar.modifiers["Bevel"].width = 0.001524
        bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = "Bevel")
        o.select = True; mortar.select = False; context.scene.objects.active = o
    #tin screws
    if o.mat == "3" and o.is_screws == True:
        if o.object_add == "convert":   
            verts2, faces2 = tin_screws(dim[1], dim[0], o.is_slope, o.slope)
        else:
            verts2, faces2 = tin_screws(o.over_height, o.over_width, o.is_slope, o.slope)
        screws = bpy.data.meshes.new(name = "screws")
        screws.from_pydata(verts2, [], faces2)
        screwOb = bpy.data.objects.new("screws", screws)
        context.scene.objects.link(screwOb)
        screwOb.location = o.location; screwOb.rotation_euler = o.rotation_euler
        for ob in context.scene.objects:
            ob.select = False
        screwOb.select = True; o.select = True; bpy.context.scene.objects.active = o; bpy.ops.object.join()
    #cutouts
    if o.is_cutout == True and o.object_add == "add":
        bool_stuff = bool(corner_data)
        if o.mat == "5" and o.is_soldier == True:
            verts3, faces3 = bool(corner_data_l)
            bool_me_l = bpy.data.meshes.new("bool2")
            bool_me_l.from_pydata(verts3, [], faces3)
            bool_ob_l = bpy.data.objects.new("bool2", bool_me_l)
            context.scene.objects.link(bool_ob_l)
            bool_ob_l.location = o.location; bool_ob_l.rotation_euler = o.rotation_euler; bool_ob_l.scale = o.scale   
        if bool_stuff[0] != []:
            verts2 = bool_stuff[0]; faces2 = bool_stuff[1]
            bool_me = bpy.data.meshes.new("bool")
            bool_me.from_pydata(verts2, [], faces2)
            bool_ob = bpy.data.objects.new("bool", bool_me)
            context.scene.objects.link(bool_ob)
            bool_ob.location = o.location; bool_ob.rotation_euler = o.rotation_euler; bool_ob.scale = o.scale
            bpy.context.scene.objects.active = o
            bpy.ops.object.modifier_add(type = "BOOLEAN"); pos = len(o.modifiers) - 1 
            if o.mat == "5" and o.is_soldier == True:
                bpy.context.object.modifiers[pos].object = bool_ob_l
            else:
                bpy.context.object.modifiers[pos].object = bool_ob  
            bpy.context.object.modifiers[pos].operation = "DIFFERENCE"
            bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = o.modifiers[pos].name)   
            for ob in context.scene.objects:
                ob.select = False 
            #battens
            if v != []:
                battens.select = True; context.scene.objects.active = battens
                bpy.ops.object.modifier_add(type = "BOOLEAN")
                bpy.context.object.modifiers["Boolean"].object = bool_ob                 
                bpy.context.object.modifiers["Boolean"].operation = "DIFFERENCE"
                bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = "Boolean"); battens.select = False 
            if o.mat in ("5", "6"):
                mortar.select = True; bpy.context.scene.objects.active = mortar  
                bpy.ops.object.modifier_add(type = "BOOLEAN"); pos = len(mortar.modifiers) - 1 
                bpy.context.object.modifiers[pos].object = bool_ob  
                bpy.context.object.modifiers[pos].operation = "DIFFERENCE"
                bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = mortar.modifiers[pos].name); mortar.select = False
            if "bool2" in bpy.data.objects: bool_ob_l.select = True
            bool_ob.select = True; bpy.ops.object.delete(); o.select = True; bpy.context.scene.objects.active = o
    
    if o.object_add == "convert": #set position
        o.location = coords[0]; o.rotation_euler = coords[1]
        cutter = bpy.data.objects[o.cut_name] #update cutter object scale, rotation, location, origin point  
        for ob in bpy.data.objects:
            ob.select = False
        cursor = context.scene.cursor_location.copy(); o.select = True; bpy.context.scene.objects.active = o
        bpy.ops.view3d.snap_cursor_to_selected(); o.select = False; eur = o.rotation_euler.copy()
        if o.is_cut == "none":   
            cutter.select = True; bpy.context.scene.objects.active = cutter 
            bpy.ops.object.origin_set(type = "ORIGIN_CURSOR")
            bpy.ops.object.move_to_layer(layers = (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))      
            cutter.select = False; o.is_cut = "cut"
        eur.rotate_axis("Z", -(float(o.angle_off)))
        o.select = True; bpy.context.scene.objects.active = o  
        cutter.location = o.location.copy(); cutter.rotation_euler = eur
        if pre_scale != (1.0, 1.0, 1.0):
            layers = [i for i in bpy.context.scene.layers]; counter = 1; true = []
            for i in layers:
                if i == True: true.append(counter)
                counter += 1
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area
                    bpy.ops.view3d.layers(override, nr = 20, toggle = True)
            cutter.select = True; o.select = False; bpy.context.scene.objects.active = cutter   
            cutter.scale = (pre_scale[0], pre_scale[2], pre_scale[1]); bpy.ops.object.transform_apply(scale = True)
            cutter.select = False
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area  
                    for i in true:
                        bpy.ops.view3d.layers(override, nr = i, extend = True, toggle = True)
                    bpy.ops.view3d.layers(override, nr = 20, extend = True, toggle = True)
            bpy.context.scene.objects.active = o; o.select = True
        bpy.context.scene.cursor_location = cursor #change cursor location back to original
        #cut
        bpy.ops.object.modifier_add(type = "BOOLEAN"); pos = len(o.modifiers) - 1 
        bpy.context.object.modifiers[pos].object = bpy.data.objects[o.cut_name]
        bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = o.modifiers[0].name)
        if o.mat in ("5", "6"):
            o.select = False; mortar.select = True; bpy.context.scene.objects.active = mortar
            bpy.ops.object.modifier_add(type = "BOOLEAN"); pos = len(mortar.modifiers) - 1 
            bpy.context.object.modifiers[pos].object = bpy.data.objects[o.cut_name]
            bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = mortar.modifiers[pos].name)
            mortar.select = False; o.select = True; bpy.context.scene.objects.active = o
        elif v != []:
            o.select = False; battens.select = True; bpy.context.scene.objects.active = battens
            bpy.ops.object.modifier_add(type = "BOOLEAN")
            bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[o.cut_name]
            bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = "Boolean")
            battens.select = False; o.select = True; bpy.context.scene.objects.active = o   
    if o.mat in ("5", "6"): #join mortar and brick
        VertexGroup(self, context)
        for ob in context.scene.objects:
            ob.select = False
        #if soldier
        if o.is_soldier == True and o.is_cutout == True:
            verts2, faces2 = bricks_soldier(corner_data, o.b_height, o.b_gap, o.b_width, o.over_height)
            p_mesh = bpy.data.meshes.new("soldier")
            p_mesh.from_pydata(verts2, [], faces2)
            soldier = bpy.data.objects.new("soldier", p_mesh)
            context.scene.objects.link(soldier)
            soldier.location = o.location.copy(); soldier.rotation_euler = o.rotation_euler.copy(); soldier.scale = o.scale.copy()
            soldier.select = True; o.select = True; bpy.context.scene.objects.active = o; bpy.ops.object.join(); o.select = False
        enter = True
        for i in mats:
            if "siding_" in i or len(mats) >= 2: enter = False
        if enter == True:   
            mat = bpy.data.materials.new("siding_" + o.name); mat.use_nodes = True; o.data.materials.append(mat)
        elif enter == False:
            mat = bpy.data.materials.get(mats[0]); o.data.materials.append(mat)
        for i in bpy.data.objects: i.select = False
        mortar.select = True; o.select = True; bpy.context.scene.objects.active = o; bpy.ops.object.join()
    #join battens and siding if needed
    elif v != []:
        for ob in context.scene.objects:
            ob.select = False
        battens.select = True; o.select = True; bpy.context.scene.objects.active = o; bpy.ops.object.join()
    for i in mats:
        if i not in o.data.materials:   
            mat = bpy.data.materials.get(i); o.data.materials.append(mat)
    UnwrapSiding(self, context)
    if o.random_uv == True and o.unwrap == True:
        RandomUV(self, context)

def SidingMaterial(self, context):
    o = bpy.context.object; cur_mat = None
    #look and see if material is already on there, get the material and its index
    data = o.data.materials; counter = 0; index = None; mat = None; error = False
    for i in data:
        if i.name[0:7] == "siding_":
            cur_mat = i; index = counter
        else: index = 0
        counter += 1       
    if o.mat in ("2", "3", "4"): #vinyl, tin, fiber cement
        if o.mat == "2": rough = 0.3
        elif o.mat == "3": rough = 0.18
        elif o.mat == "4": rough = 0.35
        mat = GlossyDiffuse(bpy, o.mat_color, (1.0, 1.0, 1.0), rough, 0.05, "siding_use")
    elif o.mat == "1" or (o.mat == "6" and o.s_mat == "1"): #wood   
        if o.col_image == "": self.report({"ERROR"}, "No Color Image Entered"); error = True
        elif o.is_bump == True and o.norm_image == "": self.report({"ERROR"}, "No Normal Map Image Entered"); error = True
        if error == False:
            mat = Image(bpy, context, o.im_scale, o.col_image, o.norm_image, o.bump_amo, o.is_bump, "siding_use", False, 1.0, 1.0, o.is_rotate, None)
            if mat != None:
                if o.mat == "6" and len(o.data.materials) >= 2:
                    o.data.materials[0] = mat.copy(); o.data.materials[0].name = "siding_" + o.name
                elif len(o.data.materials) < 2 and o.mat == "6":
                    error = True; self.report({"ERROR"}, "Material Needed For Stone Not Found")
            else: self.report({"ERROR"}, "Images Not Found, Make Sure Path Is Correct")
    elif o.mat == "5" or (o.mat == "6" and o.s_mat == "2"): #bricks
        if len(o.data.materials) >= 2:  
            mat = Brick(bpy, context, o.color_style, o.mat_color, o.mat_color2, o.mat_color3, o.color_sharp, o.color_scale, o.bump_type, o.brick_bump, o.bump_scale, "siding_use")
            o.data.materials[0] = mat.copy(); o.data.materials[0].name = "siding_" + o.name
        else:
            self.report({"ERROR"}, "Material Needed For Bricks//Stones Not Found, Please Update Siding"); error = True
    if o.mat in ("5", "6"): #mortar
        if len(o.data.materials) >= 2:
            if "mortar_temp" in o.data.materials: mname = "mortar_temp"
            else: mname = o.data.materials[1].name
            mat2 = Mortar(bpy, context, o.mortar_color, o.mortar_bump, mname); o.data.materials[1] = mat2.copy(); o.data.materials[1].name = "mortar_" + o.name
        else:
            self.report({"ERROR"}, "Material Needed For Mortar Not Found, Please Update Siding"); error = True   
    #set material
    if cur_mat != None and error == False and o.mat != "5": #update current material
        cur_mat = mat.copy(); o.data.materials[index] = cur_mat
    elif cur_mat == None and error == False and o.mat != "5": #add material
        o.data.materials.append(mat.copy()); index = len(o.data.materials) - 1
    for i in bpy.data.materials: #remove unused materials
        if i.users == 0: bpy.data.materials.remove(i)
    if error == False: #if no errors, then update name on material
        o.data.materials[index].name = "siding_" + o.name

def DeleteMaterials(self, context):
    o = context.object
    if o.is_material == False and o.mat not in ("5", "6"):
        for i in o.data.materials:
            bpy.ops.object.material_slot_remove()
        for i in bpy.data.materials:
            if i.users == 0:
                bpy.data.materials.remove(i)

def PreviewMaterials(self, context):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if bpy.context.object.is_preview == True: space.viewport_shade = 'RENDERED'
                    else: space.viewport_shade = "SOLID"                    

def UnwrapSiding(self, context):
    o = context.object
    #uv unwrap
    if o.mat in ("1", "5", "6") and o.unwrap == True:
        for i in bpy.data.objects: i.select = False
        o.select = True; bpy.context.scene.objects.active = o
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        bpy.ops.object.editmode_toggle()
                        override = bpy.context.copy(); override["area"] = area; override["region"] = region; override["active_object"] = (bpy.context.selected_objects)[0]
                        bpy.ops.mesh.select_all(action = "SELECT"); bpy.ops.uv.cube_project(override); bpy.ops.object.editmode_toggle()

def VertexGroup(self, context):
    o = context.object
    for i in bpy.data.objects: i.select = False
    o.select = True; bpy.context.scene.objects.active = o
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    bpy.ops.object.editmode_toggle()
                    if "JARCH" in o.vertex_groups:
                        group = o.vertex_groups.get("JARCH"); o.vertex_groups.remove(group)
                    bpy.ops.object.vertex_group_add(); bpy.ops.object.vertex_group_assign(); active = o.vertex_groups.active
                    active.name = "JARCH"; bpy.ops.object.editmode_toggle()

def RandomUV(self, context):
    for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        bpy.ops.object.editmode_toggle()
                        bpy.ops.mesh.select_all(action = "SELECT")
                        obj = bpy.context.object
                        me = obj.data
                        bm = bmesh.from_edit_mesh(me)    

                        uv_layer = bm.loops.layers.uv.verify()
                        bm.faces.layers.tex.verify()
                        # adjust UVs                        
                        for f in bm.faces:
                            offset = Vector((uniform(-1.0, 1.0), uniform(-1.0, 1.0)))
                            for v in f.loops:
                                luv = v[uv_layer]   
                                luv.uv = (luv.uv + offset).xy

                        bmesh.update_edit_mesh(me)
                        bpy.ops.object.editmode_toggle()
                    
#Properties
#types
bpy.types.Object.mat = EnumProperty(items = (("1", "Wood", ""), ("2", "Vinyl", ""), ("3", "Tin", ""), ("4", "Fiber Cement", "" ), ("5", "Bricks", ""), ("6", "Stone", "")),
                            default = "1", name = "", update = UpdateSiding)
bpy.types.Object.if_tin = EnumProperty(items = (("1", "Normal", ""), ("2", "Angular", "")), default = "1",
                            name = "", update = UpdateSiding)
bpy.types.Object.if_wood = EnumProperty(items = (("1", "Vertical", ""), ("2", "Vertical: Tongue & Groove", ""),
                            ("3", "Vertical: Board & Batten", ""), ("4", "Horizontal: Lap", ""),
                            ("5", "Horizontal: Lap Bevel", "")), default = "1", name = "", update = UpdateSiding)
bpy.types.Object.if_vinyl = EnumProperty(items = (("1", "Vertical", ""), ("2", "Horizontal: Lap", ""),
                            ("3", "Horizontal: Dutch Lap", "")), default = "1", name = "", update = UpdateSiding)
#measurements
bpy.types.Object.is_cut = StringProperty(default = "none")
bpy.types.Object.cut_name = StringProperty(default = "none")
bpy.types.Object.object_add = StringProperty(default = "none", update = UpdateSiding)
bpy.types.Object.from_dims = StringProperty(default = "none")
bpy.types.Object.angle_off = StringProperty(default = "none")
bpy.types.Object.dims = StringProperty(default = "none")
bpy.types.Object.is_slope = BoolProperty(name = "Slope Top?", default = False, update = UpdateSiding)
bpy.types.Object.over_height = FloatProperty(name = "Overall Height", min = 0.6096, max = 15.2399, default = 2.4384, subtype = "DISTANCE", description = "Height", update = UpdateSiding)
bpy.types.Object.over_width = FloatProperty(name = "Overall Width", min = 0.3048, max = 30.4799, default = 6.0959, subtype = "DISTANCE", description = "Width From Left To Right", update = UpdateSiding)
bpy.types.Object.board_width = FloatProperty(name = "Board Width", min = 0.1016, max = 0.3048, default = 0.1524, subtype = "DISTANCE", description = "Board Width (Or Average If Width Varience Is Checked)", update = UpdateSiding)
bpy.types.Object.batten_width = FloatProperty(name = "Batten Width", min = 0.5 / 39.3701, max = 4 / 39.3701, default = 2 / 39.3701, subtype = "DISTANCE", description = "Width Of Batten", update = UpdateSiding)
bpy.types.Object.board_space = FloatProperty(name = "Board Gap", min = 0.05 / 39.3701, max = 2 / 39.3701, default = 0.25 / 39.3701, subtype = "DISTANCE", description = "Gap Between Boards", update = UpdateSiding)
bpy.types.Object.slope = FloatProperty(name = "Slope (X/12)", min = 1.0, max = 12.0, default = 4.0, description = "Slope In RISE/RUN Format In Inches", update = UpdateSiding)
bpy.types.Object.is_width_vary = BoolProperty(name = "Vary Width?", default = False, update = UpdateSiding)
bpy.types.Object.width_vary = FloatProperty(name = "Width Varience", min = 0.001, max = 100.0, default = 50.0, subtype = "PERCENTAGE", update = UpdateSiding)
bpy.types.Object.is_cutout = BoolProperty(name = "Cutouts?", default = False, description = "Cutout Rectangles? *Cutouts May Take Some Time*", update = UpdateSiding)
bpy.types.Object.num_cutouts = IntProperty(name = "# Cutouts", min = 1, max = 6, default = 1, update = UpdateSiding)
bpy.types.Object.is_length_vary = BoolProperty(name = "Vary Length?", default = False, update = UpdateSiding)
bpy.types.Object.length_vary = FloatProperty(name = "Length Varience", min = 0.001, max = 100.0, default = 50.0, subtype = "PERCENTAGE", update = UpdateSiding)
bpy.types.Object.max_boards = IntProperty(name = "Max # Of Boards", min = 2, max = 6, default = 2, description = "Max Number Of Boards Possible To Be Placed", update = UpdateSiding)
bpy.types.Object.res = IntProperty(name = "Bevel Resolution", min = 1, max = 6, default = 1, description = "Bevel Modifier  # Of Segments", update = UpdateSiding)
bpy.types.Object.is_screws = BoolProperty(name = "Screw Heads?", default = False, description = "Add Screw Heads?", update = UpdateSiding)
bpy.types.Object.bevel_width = FloatProperty(name = "Bevel Width", min = 0.05 / 39.3701, max = 0.5 / 39.3701, default = 0.2 / 39.3701, subtype = "DISTANCE", update = UpdateSiding)
bpy.types.Object.x_offset = FloatProperty(name = "X-Offset", min = -2.0 / 39.3701, max = 2.0 / 39.3701, default = 0.0, subtype = "DISTANCE", update = UpdateSiding)
#brick specific
bpy.types.Object.b_width = FloatProperty(name = "Brick Width", min = 4.0 / 39.3701, max = 10.0 / 39.3701, default = 7.625 / 39.3701, subtype = "DISTANCE", description = "Brick Width", update = UpdateSiding)
bpy.types.Object.b_height = FloatProperty(name = "Brick Height", min = 2.0 / 39.3701, max = 5.0 / 39.3701, default = 2.375 / 39.3701, subtype = "DISTANCE", description = "Brick Height", update = UpdateSiding)
bpy.types.Object.b_ran_offset = BoolProperty(name = "Random Offset?", default = False, description = "Random Offset Between Rows", update = UpdateSiding)
bpy.types.Object.b_offset = FloatProperty(name = "Brick Offset", subtype = "PERCENTAGE", min = 0.001, max = 100.0, default = 50.0, description = "Brick Offset Between Rows", update = UpdateSiding)
bpy.types.Object.b_gap = FloatProperty(name = "Gap", min = 0.1 / 39.3701, max = 1 / 39.3701, default = 0.5 / 39.3701, subtype = "DISTANCE", description = "Gap Between Bricks", update = UpdateSiding)
bpy.types.Object.m_depth = FloatProperty(name = "Mortar Depth", min = 0.1 / 39.3701, max = 1.0 / 39.3701, default = 0.25 / 39.3701, subtype = "DISTANCE", description = "Mortar Depth", update = UpdateSiding)
bpy.types.Object.b_vary = FloatProperty(name = "Offset Varience", min = 0.1, soft_max = 1.0, default = 0.5, max = 2.0, description = "Offset Varience", update = UpdateSiding)
bpy.types.Object.is_bevel = BoolProperty(name = "Bevel?", default = False, description = "Bevel Brick *Vertices Add Up Quickly*", update = UpdateSiding)
bpy.types.Object.bump_type = EnumProperty(items = (("1", "Dimpled", ""), ("2", "Ridges", ""), ("3", "Flaky", ""), ("4", "Smooth", "")), name = "Bump Type")
bpy.types.Object.color_style = EnumProperty(items = (("constant", "Constant", "Single Color"), ("speckled", "Speckled", "Speckled Pattern"), ("multiple", "Multiple", "Two Mixed Colors"), ("extreme", "Extreme", "Three Mixed Colors")), name = "Color Style")
bpy.types.Object.mat_color2 = FloatVectorProperty(name = "Color 2", subtype = "COLOR", default = (1.0, 1.0, 1.0), min = 0.0, max = 1.0, description = "Color 2 For Siding")
bpy.types.Object.mat_color3 = FloatVectorProperty(name = "Color 3", subtype = "COLOR", default = (1.0, 1.0, 1.0), min = 0.0, max = 1.0, description = "Color 3 For Siding")
bpy.types.Object.color_sharp = FloatProperty(name = "Color Sharpness", min = 0.0, max = 10.0, default = 1.0, description = "Sharpness Of Color Edges")
bpy.types.Object.mortar_color = FloatVectorProperty(name = "Mortar Color", subtype = "COLOR", default = (1.0, 1.0, 1.0), min = 0.0, max = 1.0, description = "Color For Mortar")
bpy.types.Object.mortar_bump = FloatProperty(name = "Mortar Bump", min = 0.0, max = 1.0, default = 0.25, description = "Mortar Bump Amount")
bpy.types.Object.brick_bump = FloatProperty(name = "Brick Bump", min = 0.0, max = 1.0, default = 0.25, description = "Brick Bump Amount")
bpy.types.Object.color_scale = FloatProperty(name = "Color Scale", min = 0.01, max = 20.0, default = 1.0, description = "Color Scale")
bpy.types.Object.bump_scale = FloatProperty(name = "Bump Scale", min = 0.01, max = 20.0, default = 1.0, description = "Bump Scale")
bpy.types.Object.is_corner = BoolProperty(name = "Usable Corners?", default = False, description = "Offset First And Last Row To Make Corners Possible", update = UpdateSiding)
bpy.types.Object.is_invert = BoolProperty(name = "Flip Rows?", default = False, description = "Flip Offset Staggering", update = UpdateSiding)
bpy.types.Object.is_soldier = BoolProperty(name = "Soldier Bricks?", default = False, description = "Bricks Above Cutouts", update = UpdateSiding)
bpy.types.Object.is_left = BoolProperty(name = "Corners Left?", default = True, description = "Usable Corners On Left", update = UpdateSiding)
bpy.types.Object.is_right = BoolProperty(name = "Corners Right?", default = True, description = "Usable Corners On Right", update = UpdateSiding)
#stone
bpy.types.Object.av_width = FloatProperty(name = "Average Width", default = 10.00 / 39.3701, min = 4.00 / 39.3701, max = 36.00 / 39.3701, subtype = "DISTANCE", description = "Average Width Of Stones", update = UpdateSiding)
bpy.types.Object.av_height = FloatProperty(name = "Average Height", default = 6.00 / 39.3701, min = 2.00 / 39.3701, max = 36.00 / 39.3701, subtype = "DISTANCE", description = "Average Height Of Stones", update = UpdateSiding)
bpy.types.Object.s_random = FloatProperty(name = "Size Randomness", default = 25.00, max = 100.00, min = 0.00, subtype = "PERCENTAGE", description = "Size Randomness Of Stones", update = UpdateSiding)
bpy.types.Object.b_random = FloatProperty(name = "Bump Randomness", default = 25.00, max = 100.00, min = 0.00, subtype = "PERCENTAGE", description = "Bump Randomness Of Stones", update = UpdateSiding)
bpy.types.Object.s_mortar = FloatProperty(name = "Mortar Depth", default = 1.5 / 39.3701, min = 0.5 / 39.3701, max = 3.0 / 39.3701, subtype = "DISTANCE", description = "Depth Of Mortar", update = UpdateSiding)
bpy.types.Object.s_mat = EnumProperty(name = "", items = (("1", "Image", ""), ("2", "Procedural", "")), default = "1", description = "Stone Material Type")
#materials
bpy.types.Object.is_material = BoolProperty(name = "Cycles Materials?", default = False, description = "Adds Cycles Materials", update = DeleteMaterials)
bpy.types.Object.mat_color = FloatVectorProperty(name = "Color", subtype = "COLOR", default = (1.0, 1.0, 1.0), min = 0.0, max = 1.0, description = "Color For Siding")
bpy.types.Object.is_preview = BoolProperty(name = "Preview Material?", default = False, description = "Preview Material On Object", update = PreviewMaterials)
bpy.types.Object.im_scale = FloatProperty(name = "Image Scale", max = 10.0, min = 0.1, default = 1.0, description = "Change Image Scaling")
bpy.types.Object.col_image = StringProperty(name = "", subtype = "FILE_PATH", description = "File Path For Color Image")
bpy.types.Object.is_bump = BoolProperty(name = "Normal Map?", default = False, description = "Add Normal To Material?")
bpy.types.Object.norm_image = StringProperty(name = "", subtype = "FILE_PATH", description = "File Path For Normal Map Image")
bpy.types.Object.bump_amo = FloatProperty(name = "Normal Stength", min = 0.001, max = 2.000, default = 0.250, description = "Normal Map Strength")
bpy.types.Object.unwrap = BoolProperty(name = "UV Unwrap?", default = True, description = "UV Unwraps Siding", update = UnwrapSiding)
bpy.types.Object.is_rotate = BoolProperty(name = "Rotate Image?", default = False, description = "Rotate Image 90 Degrees")
bpy.types.Object.random_uv = BoolProperty(name = "Random UV's?", default = True, description = "Random UV's", update = UpdateSiding)
#cutout variables
bpy.types.Object.nc1 = StringProperty(name = "", default = "", description = "X, Y, Height, Width In (ft/m)", update = UpdateSiding)
bpy.types.Object.nc2 = StringProperty(name = "", default = "", description = "X, Y, Height, Width In (ft/m)", update = UpdateSiding)
bpy.types.Object.nc3 = StringProperty(name = "", default = "", description = "X, Y, Height, Width In (ft/m)", update = UpdateSiding)
bpy.types.Object.nc4 = StringProperty(name = "", default = "", description = "X, Y, Height, Width In (ft/m)", update = UpdateSiding)
bpy.types.Object.nc5 = StringProperty(name = "", default = "", description = "X, Y, Height, Width In (ft/m)", update = UpdateSiding)
bpy.types.Object.nc6 = StringProperty(name = "", default = "", description = "X, Y, Height, Width In (ft/m)", update = UpdateSiding)

class SidingUpdate(bpy.types.Operator):
    bl_idname = "mesh.jarch_siding_update"
    bl_label = "Update Siding"
    bl_description = "Update Siding, Specifically For Updating Stone"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        UpdateSiding(self, context)
        return {"FINISHED"}
    
class SidingMesh(bpy.types.Operator):
    bl_idname = "mesh.jarch_siding_mesh" 
    bl_label = "Convert To Mesh"
    bl_description = "Converts Siding Object To Normal Object (No Longer Editable)"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        o = context.object
        o.object_add = "mesh"
        return {"FINISHED"}
    
class SidingDelete(bpy.types.Operator):
    bl_idname = "mesh.jarch_siding_delete"
    bl_label = "Delete Siding"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        o = context.object; convert = False
        if o.object_add == "convert" and o.cut_name in bpy.data.objects:
            cutter = bpy.data.objects[o.cut_name]; o.select = False
            layers = [i for i in bpy.context.scene.layers]; counter = 1; true = []
            for i in layers:
                if i == True: true.append(counter)
                counter += 1
            o_layers = []
            for i in bpy.context.object.layers: o_layers.append(i) 
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area
                    bpy.ops.view3d.layers(override, nr = 20, toggle = True)
            cutter.select = True; bpy.context.scene.objects.active = cutter; bpy.ops.object.modifier_remove(modifier = "Solidify")  
            bpy.ops.object.move_to_layer(layers = o_layers); convert = True; cutter.select = False
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area  
                    for i in true:
                        bpy.ops.view3d.layers(override, nr = i, extend = True, toggle = True)
                    bpy.ops.view3d.layers(override, nr = 20, extend = True, toggle = True)
        m_name = o.name; c_name = o.cut_name
        o.select = True; bpy.context.scene.objects.active = o; bpy.ops.object.delete()
        for i in bpy.data.materials:
            if i.users == 0: bpy.data.materials.remove(i)
        if convert == True:
            bpy.data.objects[c_name].name = m_name   
        return {"FINISHED"}
    
class SidingMaterials(bpy.types.Operator):
    bl_idname = "mesh.jarch_siding_materials"
    bl_label = "Generate\\Update Materials"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        SidingMaterial(self, context)
        return {"FINISHED"}

class SidingPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_jarch_siding"
    bl_label = "JARCH Vis: Siding"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "JARCH Vis"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        if bpy.context.mode == "EDIT_MESH":
            layout.label("JARCH Vis Doesn't Work In Edit Mode", icon = "ERROR")
        else:
            o = context.object
            if o != None:
                if o.type == "MESH":                    
                    if o.f_object_add == "none" and o.s_object_add == "none" and o.ro_object_add == "none":                   
                        if o.object_add in ("convert", "add"): 
                            layout.label("Material:"); layout.prop(o, "mat", icon = "MATERIAL"); layout.label("Type(s):")
                            if o.mat == "1": layout.prop(o, "if_wood", icon = "OBJECT_DATA")
                            elif o.mat == "2": layout.prop(o, "if_vinyl", icon = "OBJECT_DATA")
                            elif o.mat == "3": layout.prop(o, "if_tin", icon = "OBJECT_DATA")
                            elif o.mat == "4": layout.label("Horizontal: Lap", icon = "OBJECT_DATA")
                            elif o.mat == "5": layout.label("Bricks", icon = "OBJECT_DATA")
                            elif o.mat == "6": layout.label("Stone", icon = "OBJECT_DATA")
                            layout.separator()
                            #measurements
                            if o.object_add == "add":
                                layout.prop(o, "over_width"); layout.prop(o, "over_height"); layout.separator()
                            if o.mat not in ("3", "5", "6"): layout.prop(o, "board_width")
                            elif o.mat == "3": layout.label("Sheet Lays: 36 (in)", icon = "ARROW_LEFTRIGHT"); layout.prop(o, "is_screws", icon = "PLUS")
                            if o.mat not in ("5", "6"): #if not bricks or stone
                                if o.mat == "1" and o.if_wood == "1": layout.prop(o, "board_space"); layout.separator()
                                if o.mat in ("1", "2"):
                                    if (o.if_vinyl == "1" and o.mat == "2") or (o.if_wood == "3" and o.mat == "1"):
                                        layout.prop(o, "batten_width")
                                        if o.batten_width / 2 > (o.board_width / 2) - (0.125 / 39.3701):
                                            layout.label("Max Width: " + str(round(2 * ((o.board_width / 2) - (0.125 / 39.3701)), 3)) + " in", icon = "ERROR")
                            elif o.mat == "5": #bricks
                                layout.prop(o, "b_width"); layout.prop(o, "b_height"); layout.separator()
                                if o.object_add == "add": layout.prop(o, "is_corner", icon = "VIEW3D")
                                if o.is_corner == False:
                                    layout.separator(); layout.prop(o, "b_ran_offset", icon = "NLA")
                                    if o.b_ran_offset == False: layout.prop(o, "b_offset")
                                    else: layout.prop(o, "b_vary")
                                else: 
                                    layout.separator(); layout.prop(o, "is_left", icon = "TRIA_LEFT"); layout.prop(o, "is_right", icon = "TRIA_RIGHT"); layout.prop(o, "is_invert", icon = "FILE_REFRESH"); layout.separator()
                                layout.prop(o, "b_gap"); layout.separator(); layout.prop(o, "m_depth"); layout.separator()
                            if o.object_add == "convert":
                                layout.prop(o, "x_offset"); layout.separator()
                            if o.mat in ("5", "6") or (o.mat == "1" and o.if_wood == "1"):
                                layout.prop(o, "is_bevel", icon = "MOD_BEVEL")
                                if o.is_bevel == True and o.mat != "1":
                                    layout.prop(o, "res", icon = "OUTLINER_DATA_CURVE"); layout.separator()
                                elif o.mat == "1" and o.is_bevel == True:
                                    layout.prop(o, "bevel_width")
                            if o.mat == "6": #stone
                                layout.prop(o, "av_width"); layout.prop(o, "av_height"); layout.separator()
                                layout.prop(o, "s_random"); layout.prop(o, "b_random"); layout.separator()
                                layout.prop(o, "b_gap"); layout.prop(o, "s_mortar")
                            layout.separator()
                            if o.object_add == "add":                                              
                                layout.prop(o, "is_slope", icon = "TRIA_UP")
                                if o.is_slope == True:
                                    layout.label("Pitch x/12", icon = "LINCURVE"); layout.prop(o, "slope"); units = " m"
                                    if o.is_corner == False:
                                        ht = round(o.over_height - ((o.slope * (o.over_width / 2)) / 12), 2)
                                        if ht <= 0:
                                            slope = round(((24 * o.over_height) / o.over_width) - 0.01, 2)
                                            ht = round(o.over_height - ((slope * (o.over_width / 2)) / 12), 2)
                                            layout.label("Max Slope: " + str(slope), icon = "ERROR")
                                    else:
                                        ht = round(o.over_height - ((o.slope * ((o.over_width + (2 * o.b_width)) / 2)) / 12), 2)
                                        if ht <= 0:
                                            slope = round(((24 * o.over_height) / o.over_width + (2 * o.b_width)) - 0.01, 2)
                                            ht = round(o.over_height - ((slope * ((o.over_width + (2 * o.b_width)) / 2)) / 12), 2)            
                                            layout.label("Max Slope: " + str(slope), icon = "ERROR")
                                    if context.scene.unit_settings.system == "IMPERIAL": ht = round(3.28084 * ht, 2); units = " ft"
                                    layout.label("Height At Edges: " + str(ht) + units, icon = "TEXT")
                            if o.mat not in ("5", "6"):
                                if o.mat == "1":
                                    if o.if_wood == "1":
                                        layout.prop(o, "is_width_vary", icon = "UV_ISLANDSEL")
                                        if o.is_width_vary == True: layout.prop(o, "width_vary")
                                if o.mat != "3": layout.prop(o, "is_length_vary", icon = "NLA")
                                if o.is_length_vary == True: layout.prop(o, "length_vary"); layout.prop(o, "max_boards")
                                if o.mat == "2": layout.separator(); layout.prop(o, "res", icon = "OUTLINER_DATA_CURVE"); layout.separator()
                            if o.object_add == "add":
                                layout.prop(o, "is_cutout", icon = "MOD_BOOLEAN"); units = " m"
                                if context.scene.unit_settings.system == "IMPERIAL": units = " ft"
                                if o.is_cutout == True:
                                    if o.mat == "5": layout.separator(); layout.prop(o, "is_soldier", icon = "DOTSUP"); layout.separator()
                                    layout.prop(o, "num_cutouts"); layout.separator(); layout.label("X, Z, Height, Width in" + units)
                                    for i in range(1, o.num_cutouts + 1):
                                        layout.label("Cutout " + str(i) + ":", icon = "MOD_BOOLEAN"); layout.prop(o, "nc" + str(i))
                            layout.separator(); layout.prop(o, "unwrap", icon = "GROUP_UVS")
                            if o.unwrap == True:
                                layout.prop(o, "random_uv", icon = "RNDCURVE") 
                            layout.separator()
                            #materials   
                            if context.scene.render.engine == "CYCLES": layout.prop(o, "is_material", icon = "MATERIAL")
                            else: layout.label("Materials Only Supported With Cycles", icon = "POTATO")
                            layout.separator()
                            if o.is_material == True and context.scene.render.engine == "CYCLES":
                                if o.mat == "6":
                                    layout.prop(o, "s_mat"); layout.separator()
                                if o.mat in ("2", "3", "4"): layout.prop(o, "mat_color", icon = "COLOR") #vinyl and tin
                                elif o.mat == "1" or (o.mat == "6" and o.s_mat == "1"): #wood and fiber cement
                                    layout.prop(o, "col_image", icon = "COLOR"); layout.prop(o, "is_bump", icon = "SMOOTHCURVE")
                                    if o.is_bump == True: layout.prop(o, "norm_image", icon = "TEXTURE"); layout.prop(o, "bump_amo")
                                    layout.prop(o, "im_scale", icon = "MAN_SCALE"); layout.prop(o, "is_rotate", icon = "MAN_ROT")
                                elif o.mat == "5" or (o.mat == "6" and s_mat == "2"): #bricks
                                    layout.prop(o, "color_style", icon = "COLOR"); layout.prop(o, "mat_color", icon = "COLOR")
                                    if o.color_style != "constant": layout.prop(o, "mat_color2", icon = "COLOR")
                                    if o.color_style == "extreme": layout.prop(o, "mat_color3", icon = "COLOR")
                                    layout.prop(o, "color_sharp"); layout.prop(o, "color_scale"); layout.separator(); layout.prop(o, "mortar_color", icon = "COLOR")
                                    layout.prop(o, "mortar_bump"); layout.prop(o, "bump_type", icon = "SMOOTHCURVE")
                                    if o.bump_type != "4": layout.prop(o, "brick_bump"); layout.prop(o, "bump_scale")
                                if o.mat == "6":
                                    layout.separator(); layout.prop(o, "mortar_color", icon = "COLOR"); layout.prop(o, "mortar_bump"); layout.prop(o, "bump_scale")
                                layout.separator(); layout.operator("mesh.jarch_siding_materials", icon = "MATERIAL"); layout.separator(); layout.prop(o, "is_preview", icon = "SCENE")
                            layout.separator(); layout.separator()
                            layout.operator("mesh.jarch_siding_update", icon = "FILE_REFRESH")  
                            layout.operator("mesh.jarch_siding_mesh", icon = "OUTLINER_OB_MESH")               
                            layout.operator("mesh.jarch_siding_delete", icon = "CANCEL")
                        else:
                            if o.f_object_add == "none" and o.s_object_add == "none" and o.ro_object_add == "none" and o.object_add != "mesh":
                                layout.operator("mesh.jarch_siding_convert")
                            elif o.object_add == "mesh":
                                layout.label("This Is A Mesh JARCH Vis Object", icon = "INFO")
                    else:
                        layout.label("This Is Already A JARCH Vis Object", icon = "POTATO")              
                else:
                    layout.label("Only Mesh Objects Can Be Used", icon = "ERROR")
            else:
                layout.operator("mesh.jarch_siding_add", text = "Add Siding", icon = "UV_ISLANDSEL")      
            
class SidingAdd(bpy.types.Operator):
    bl_idname = "mesh.jarch_siding_add"
    bl_label = "Add Siding"
    bl_description = "JARCH Vis: Siding Generator"
    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        o = bpy.context.scene.objects.active
        o.object_add = "add"
        return {"FINISHED"}
    
class SidingConvert(bpy.types.Operator):
    bl_idname = "mesh.jarch_siding_convert"
    bl_label = "Convert To Siding"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        o = context.object
        o.object_add = "convert"
        return {"FINISHED"}   