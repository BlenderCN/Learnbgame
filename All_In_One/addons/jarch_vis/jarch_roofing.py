import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, EnumProperty, CollectionProperty, FloatVectorProperty
from mathutils import Vector, Euler
from math import atan, degrees, cos, tan, sin, radians
from . jarch_utils import point_rotation, object_dimensions, round_tuple, vertex_slope_rot
from . jarch_materials import GlossyDiffuse, Image
from random import uniform
import bmesh

def tin_normal(wh, ow, slope):
    cur_x = 0.0; cur_y = -(wh / 2); con = 39.3701
    faces = []; verts = []
    
    #calculate overall depth/oh
    oh = (wh / 2) / cos(atan((((wh / 2) * slope) / 12) / (wh / 2)))
    
    #set up small variables
    osi = (1 / 16) / con; hi = 0.5 / con; eti = 0.8 / con; nti = 0.9 / con; fei = (5 / 8) / con; tei = (3 / 8) / con; nfei = 0.6875 / con ; oi = 1 / con; otqi = 1.75 / con
    #one sixtenth in,   half in,  eight tenths inch, nine tenths,  five eigths,  three eights inch,  not five eights, one inch,  one &  three quarter inch
    ofei = oi + fei; ohi = oi + hi; qi = hi / 2; ei = (1 / 8) / con; tqi = otqi - oi
    #one and 5/8,    one and 1/2,   quarter inch, eighth inch,       three quarters of a inch
    
    while cur_x < ow:
        p = len(verts); face_normal = False
        #verts  
        v2 = []; a_e = False #verts holder 2, at_edge for putting in last set of verts 
        for i in range(4):
            if i == 0: z = osi
            else: z = 0.0
            
            v = ((cur_x, cur_y, z), (cur_x, cur_y + oh, z), (cur_x + hi, cur_y, eti + z), (cur_x + hi, cur_y + oh, eti + z), (cur_x + fei, cur_y, nti + z), (cur_x + fei, cur_y + oh, nti + z)) #Left Top Of Rib
            v += ((cur_x + nfei, cur_y, oi + z), (cur_x + nfei, cur_y + oh, oi + z)); cur_x += otqi
            v += ((cur_x - nfei, cur_y, oi + z), (cur_x - nfei, cur_y + oh, oi + z), (cur_x - fei, cur_y, nti + z), (cur_x - fei, cur_y + oh, nti + z)) #Right Mid Rib
            v += ((cur_x - hi, cur_y, eti + z), (cur_x - hi, cur_y + oh, eti + z), (cur_x, cur_y, z), (cur_x, cur_y + oh, z)); cur_x += ofei
            
            for i in range(2):
                v += ((cur_x, cur_y, 0.0), (cur_x, cur_y + oh, 0.0), (cur_x + qi, cur_y, ei), (cur_x + qi, cur_y + oh, ei)); cur_x += oi
                v += ((cur_x, cur_y, ei), (cur_x, cur_y + oh, ei), (cur_x + qi, cur_y, 0.0), (cur_x + qi, cur_y + oh, 0.0)); cur_x += ohi + qi
            cur_x += ei
            for i in v: v2.append(i)
            
        v2 += ((cur_x, cur_y, 0.0), (cur_x, cur_y + oh, 0.0), (cur_x + hi, cur_y, eti), (cur_x + hi, cur_y + oh, eti), (cur_x + fei, cur_y, nti), (cur_x + fei, cur_y + oh, nti)) #Left Top Of Rib
        v2 += ((cur_x + nfei, cur_y, oi), (cur_x + nfei, cur_y + oh, oi)); cur_x += otqi; v2 += ((cur_x - nfei, cur_y, oi), (cur_x - nfei, cur_y + oh, oi), (cur_x - fei, cur_y, nti) ,(cur_x - fei, cur_y + oh, nti)) #Right Mid Rib
        v2 += ((cur_x - hi, cur_y, eti), (cur_x - hi, cur_y + oh, eti), (cur_x, cur_y, 0.0), (cur_x, cur_y + oh, 0.0)); cur_x -= otqi; face_normal = True; vts = []   
        
        if cur_x + otqi > ow: #chop off extra
            counter = 0
            for i in v2:
                if i[0] <= ow: vts.append(i)
                elif i[0] > ow and a_e == False: 
                    a_e = True; b_o = v2[counter - 1]; f_o = i; dif_x = f_o[0] - b_o[0]; dif_z = f_o[2] - b_o[2]; r_r = dif_z / dif_x; b = b_o[2] - (r_r * b_o[0])
                    z2 = (ow * r_r) + b; vts.append((ow, cur_y, z2)); vts.append((ow, cur_y, z2))
                counter += 1  
            f_t = int((len(vts) / 2) - 1)
            
        else: 
            vts = v2; f_t = 71 
                               
        for i in vts: verts.append(i)
              
        #faces
        if face_normal == True:
            for i in range(f_t):
                faces.append((p, p + 2, p + 3, p + 1)); p += 2    
    
    #apply rotation
    verts2 = []
    rot = atan(slope / 12)
    
    for num in range(1, len(verts), 2):
        verts2.append(verts[num - 1])
        point = point_rotation((verts[num][1], verts[num][2]), (cur_y, verts[num][2]), rot)
        verts2.append((verts[num][0], point[0], point[1]))        
                     
    return (verts2, faces)

def tin_angular(wh, ow, slope):
    cur_x = 0.0; cur_y = -(wh / 2); cur_z = 0.0
    con = 39.3701
    verts = []; faces = []
    #variables
    osi = (1 / 16) / con; hi = (1 / 2) / con; oqi = (5 / 4) / con; ohi = (3 / 2) / con; ti = ohi + hi; qi = (1 / 4) / con; ei = (1 / 8) / con

    #calculate overall depth/oh
    oh = (wh / 2) / cos(atan((((wh / 2) * slope) / 12) / (wh / 2)))
    
    #main loop    
    while cur_x < ow:
        p = len(verts)
        #verts
        v2 = []; a_e = False
        for i in range(3):
            if i == 0: z = -osi
            else: z = 0.0
            v = ((cur_x, cur_y, z) ,(cur_x, cur_y + oh, z), (cur_x + hi, cur_y, oqi + z), (cur_x + hi, cur_y + oh, oqi + z), (cur_x + ohi, cur_y, oqi + z), (cur_x + ohi, cur_y + oh, oqi + z))
            v += ((cur_x + ti, cur_y, z), (cur_x + ti, cur_y + oh, z)); cur_x += 2 * ti
            for i in range(2):
                v += ((cur_x, cur_y, 0.0), (cur_x, cur_y + oh, z), (cur_x + qi, cur_y, ei), (cur_x + qi, cur_y + oh, ei), (cur_x + ohi, cur_y, ei), (cur_x + ohi, cur_y + oh, ei)); cur_x += ohi
                v += ((cur_x + qi, cur_y, 0.0), (cur_x + qi, cur_y + oh, 0.0)); cur_x += qi + ti + hi
            cur_x -= hi
            for i in v: v2.append(i)
        v2 += ((cur_x, cur_y, 0.0) ,(cur_x, cur_y + oh, 0.0), (cur_x + hi, cur_y, oqi), (cur_x + hi, cur_y + oh, oqi), (cur_x + ohi, cur_y, oqi), (cur_x + ohi, cur_y + oh, oqi))
        v2 += ((cur_x + ti, cur_y, 0.0), (cur_x + ti, cur_y + oh, 0.0)); vts = []
        
        if cur_x + ti > ow: #cut off extra
            counter = 0
            for i in v2:
                if i[0] <= ow: vts.append(i)
                elif i[0] > ow and a_e == False: 
                    a_e = True; b_o = v2[counter - 1]; f_o = i; dif_x = f_o[0] - b_o[0]; dif_z = f_o[2] - b_o[2]; r_r = dif_z / dif_x; b = b_o[2] - (r_r * b_o[0])
                    z2 = (ow * r_r) + b; vts.append((ow, cur_y, z2)); vts.append((ow, cur_y + oh, z2))
                counter += 1  
            f_t = int((len(vts) / 2) - 1)
        else: vts = v2; f_t = 38
                            
        for i in vts: verts.append(i)               
        #faces        
        for i in range(f_t):
            faces.append((p, p + 2, p + 3, p + 1)); p += 2
            
    #adjust points for slope
    verts2 = []
    rot = atan(slope / 12)
    
    for num in range(1, len(verts), 2):
        verts2.append(verts[num - 1])
        point = point_rotation((verts[num][1], verts[num][2]), (cur_y, verts[num][2]), rot)
        verts2.append((verts[num][0], point[0], point[1]))
        
    return (verts2, faces)

def tin_standing_seam(wh, ow, slope):
    verts = []; faces = []
    cur_x = 0.0; cur_y = -(wh / 2); cur_z = 0.0
    con = 39.3701 #convertion factor
    
    #variables
    qi = 0.25 / con; hi = 0.5 / con; fei = 0.625 / con; tei = 0.375 / con; otei = 1.375 / con; fsi = 0.3125 / con; osi = 0.0625 / con
    ei = 0.125 / con; si = 16 / con
    
    #calculate overall height
    oh = (wh / 2) / cos(atan((((wh / 2) * slope) / 12) / (wh / 2)))
    
    while cur_x < ow:
        p = len(verts)
        v2 = []
        a_e = False
        #left side
        v2 += ((cur_x + qi, cur_y, cur_z + otei), (cur_x + qi, cur_y + oh, cur_z + otei), (cur_x + qi, cur_y, cur_z + qi), (cur_x + qi, cur_y + oh, cur_z + qi))
        v2 += ((cur_x + ei, cur_y, cur_z + qi), (cur_x + ei, cur_y + oh, cur_z + qi), (cur_x + ei, cur_y, cur_z + hi), (cur_x + ei, cur_y + oh, cur_z + hi))
        v2 += ((cur_x, cur_y, cur_z + hi), (cur_x, cur_y + oh, cur_z + hi), (cur_x, cur_y, cur_z), (cur_x, cur_y + oh, cur_z))        
        #right side
        cur_x += si
        v2 += ((cur_x - fei, cur_y, cur_z), (cur_x - fei, cur_y + oh, cur_z), (cur_x - fei + qi, cur_y, cur_z + otei), (cur_x - fei + qi, cur_y + oh, cur_z + otei))
        v2 += ((cur_x - qi, cur_y, cur_z + otei), (cur_x - qi, cur_y + oh, cur_z + otei), (cur_x, cur_y, cur_z + osi), (cur_x, cur_y + oh, cur_z + osi))
        v2 += ((cur_x - qi - ei, cur_y, cur_z + osi), (cur_x - qi - ei, cur_y + oh, cur_z + osi))
        cur_x -= hi
        
        #cut-off extra
        if cur_x + hi > ow:
            counter = 0
            for i in v2:
                if i[0] <= ow: vts.append(i)
                elif i[0] > ow and a_e == False: 
                    a_e = True; b_o = v2[counter - 1]; f_o = i; dif_x = f_o[0] - b_o[0]; dif_z = f_o[2] - b_o[2]; r_r = dif_z / dif_x; b = b_o[2] - (r_r * b_o[0])
                    z2 = (ow * r_r) + b; vts.append((ow, cur_y, z2)); vts.append((ow, cur_y + oh, z2))
                counter += 1  
            f_t = int((len(vts) / 2) - 1)
        else: vts = v2; f_t = 9
                            
        for i in vts: verts.append(i)               
        #faces        
        for i in range(f_t):
            faces.append((p, p + 2, p + 3, p + 1)); p += 2
            
    #adjust points for slope
    verts2 = []
    rot = atan(slope / 12)
    
    for num in range(1, len(verts), 2):
        verts2.append(verts[num - 1])
        point = point_rotation((verts[num][1], verts[num][2]), (cur_y, verts[num][2]), rot)
        verts2.append((verts[num][0], point[0], point[1]))
        
    return (verts2, faces)

def shingles_3tab(mode, wh, ow, slope):
    verts = []; faces = []
    cur_y = -(wh / 2); cur_z = 0.0
    con = 39.3701 #convertion factor
    
    #contstants
    tf = 36 / con; of = 12 / con; fi = 5 / con; tsi = 0.125 / con; qi = 0.25 / con; si = 7 / con; ei = 0.125 / con; esfi = 11.75 / con
    tei = 0.25 / con
    
    #calculate overall height
    oh = (wh / 2) / cos(atan((((wh / 2) * slope) / 12) / (wh / 2)))
    end_y = cur_y + oh    
    
    offset = False
    
    row = 1

    #main loop for growing on width
    while cur_y < end_y:        
        temp_offset = False   
        last_row_stay = True        
        cur_x = 0.0
        bj = of #big jump
        sj = fi #small jump
        added_first_verts = False
        
        #determine if shingle needs to be cut down on y axis
        if cur_y + of > end_y and cur_y + fi < end_y:
            bj = end_y - cur_y
        #if last row doesn't stay figure out how much to cut down second row
        elif cur_y + of > end_y and cur_y + fi > end_y:
            sj = end_y - cur_y
            last_row_stay = False
        
        #loop for growing length
        while cur_x < ow:
            #is last shingle?
            last_shingle = False
                        
            if offset == True and cur_x == 0:
                temp_offset = True  
            p = len(verts)                   
            v = []
            
            #determine shingle height at front, middle, and back based on which row it is
            if row == 1:
                h1, h2, h3 = 0, 0, 0 #height 1, 2, and 3
            elif row == 2:
                h1, h2, h3 = tsi, tsi, 0
            elif row >= 3:
                h1, h2, h3 = 2 * tsi, tsi, 0
            
            #first little outcropping
            if temp_offset == False and last_row_stay == True:                           
                v += [(cur_x, cur_y + sj, h2), (cur_x, cur_y + sj, h2 + tsi)] 
                v += [(cur_x, cur_y + bj, h3), (cur_x, cur_y + bj, h3 + tsi)]
                cur_x += ei
                added_first_verts = True                         
            
            big = True
            cut = False
            cut_num = 6
            js = False #just happened, is true only for the fist set of vertices after being cut
            
            #main sets of vertices            
            for i in range(6): 
                #figure out how much to add to know where next row is going to land   
                if big == True:
                    add = esfi
                elif big == False:
                    add = qi
                big = not big
                
                #adjust for offset on first shingle of the row
                if offset == True and cur_x == 0:
                    add = esfi / 2
                    temp_offset = False                                       
                
                if cur_x > ow and cut == False:
                    cur_x = ow
                    cut = True
                    cut_num = i
                    js = True
                    last_shingle = True
                    
                if (cur_x <= ow and cut == False) or (cut == True and js == True):
                    js = False                         
                    v += [(cur_x, cur_y, h1), (cur_x, cur_y, h1 + tsi), (cur_x, cur_y + sj, h2), (cur_x, cur_y + sj, h2 + tsi)]
                    if last_row_stay == True:
                        v += [(cur_x, cur_y + bj, h3), (cur_x, cur_y + bj, h3 + tsi)]
                        
                cur_x += add                                
                
            cur_x -= add - ei           
            
            if cut == False and cur_x != ow and last_row_stay == True:                
                v += [(cur_x, cur_y + sj, h2), (cur_x, cur_y + sj, h2 + tsi)]
                v += [(cur_x, cur_y + bj, h3), (cur_x, cur_y + bj, h3 + tsi)] 
            
            for vt in v:         
                verts.append(vt)
                
            #faces
            f = []
            #first set
            if added_first_verts == True and last_row_stay == True:
                f += [(p, p + 1, p + 3, p + 2)]
                p += 4
                
            #middle sets
            two = True
            
            #if the shingle has been cut the number will be one less than what is needed for the range() iterator
            if cut_num != 6:
                cut_num += 1
                
            for i in range(cut_num):
                #if back row exists
                if last_row_stay == True:
                    if two == True and added_first_verts == True:
                        f += [(p, p + 1, p + 3, p + 2), (p + 2, p + 3, p - 3, p - 4), (p + 3, p + 5, p - 1, p - 3), (p - 2, p - 1, p + 5, p + 4), (p + 2, p - 4, p - 2, p + 4)]
                        p += 6
                    elif two == True and added_first_verts == False:
                        f += [(p, p + 1, p + 3, p + 2), (p + 2, p + 3, p + 5, p + 4)]
                        p += 6
                        added_first_verts = True                   
                    elif two == False:
                        f += [(p, p + 1, p - 5, p - 6), (p + 1, p + 3, p - 3, p - 5), (p + 3, p + 5, p - 1, p - 3), (p - 2, p - 1, p + 5, p + 4), (p, p + 2, p + 3, p + 1), (p, p - 6, p - 4, p + 2), (p + 2, p - 4, p - 2, p + 4)]
                        p += 6
                #otherwise if it doesn't       
                elif last_row_stay == False:
                    if two == True:
                        f += [(p, p + 1, p + 3, p + 2)]
                        p += 4
                    elif two == False:
                        f += [(p, p + 2, p + 3, p + 1), (p - 4, p, p + 1, p - 3), (p - 2, p - 1, p + 3, p + 2), (p + 1, p + 3, p - 1, p - 3), (p - 4, p - 2, p + 2, p)]
                        p += 4

                two = not two                                  
                    
            #last set
            if cut == False and last_row_stay == True: 
                f += [(p, p + 1, p - 3, p - 4), (p, p + 2, p + 3, p + 1), (p + 2, p - 2, p - 1, p + 3), (p + 1, p + 3, p - 1, p - 3), (p, p - 4, p - 2, p + 2)]
                
            for fa in f:
                faces.append(fa)
            
        cur_y += fi
        row += 1
        
        offset = not offset               
        
    #adjust points for slope for verts
    verts2 = []
    rot = atan(slope / 12)
    
    for num in range(len(verts)):
        point = point_rotation((verts[num][1], verts[num][2]), (-(wh / 2), verts[num][2]), rot)
        verts2.append((verts[num][0], point[0], point[1]))
        
    return verts2, faces

def shingles_arch(mode, wh, ow, slope):
    #this shingle face function gets reused with just a slight variation, so instead of copying a bunch of code I just put it in this function
    def arch_shingle_raised_faces(f, p, extra):
        f += [(p, p + 9, p + 10, p + 1), (p + 1, p + 10, p + 11, p + 2), (p + 1, p + 2, p + 5, p + 4), (p + 2, p + 11, p + 14, p + 5),
            (p + 5, p + 14, p + 17, p + 8), (p + 7, p + 8, p + 17, p + 16), (p + 6, p + 7, p + 16, p + 15), (p + 3, p + 6, p + 15, p + 12),
            (p, p + 3, p + 12, p + 9), (p + 10, p + 13, p + 14, p + 11)]
            
        if extra == True:
            f += [(p + 9, p + 12, p + 13, p + 10), (p + 12, p + 15, p + 16, p + 13), (p + 13, p + 16, p + 17, p + 14)]
            
        return f
    
    def arch_shingle_lower_faces(f, p, extra, subtract):
        a = 0 #alter
        if subtract == True:
            a = 1
            
        f += [(p, p + 9, p + 10, p + 1), (p + 1, p + 10, p + 13 - a, p + 4), (p + 4, p + 13 - a, p + 14 - a, p + 5), (p + 5, p + 14 - a, p + 17 - a, p + 8),
                (p + 7, p + 8, p + 17 - a, p + 16 - a), (p + 6, p + 7, p + 16 - a, p + 15 - a), (p, p + 3, p + 12 - a, p + 9), (p + 3, p + 6, p + 15 - a, p + 12 - a)]
                
        if extra == True:
            f += [(p + 9, p + 11, p + 12, p + 10), (p + 11, p + 14, p + 15, p + 12), (p + 12, p + 15, p + 16, p + 13)]
                
        return f
    
    
    verts = []; faces = []
    rot = atan(slope / 12)
    
    cur_y = -(wh / 2)
    con = 39.3701 #convertion factor
    
    #variables
    sfei = 6.625 / con; lth = 0.1875 / con; sw = 39.375 / con; ffei = 5.625 / con; tth = lth / 2; hi = 0.5 / con; large_tab = 10.5 / con; small_tab = (7.875 / con) / 2
    
    oh = (wh / 2) / cos(atan((((wh / 2) * slope) / 12) / (wh / 2)))
    end_y = cur_y + oh
    
    #booleans for cutting purposes
    last_row_stay = True
    
    row = 1
            
    while cur_y < end_y:
        cur_x = 0.0
        sj = ffei
        bj = sfei + ffei
        
        final_row = False        
        
        if cur_y + ffei >= end_y:
            last_row_stay = False
            sj = end_y - cur_y #small jump replaces ffei and is adjusted for if shingle is not full width
        
        if cur_y + ffei < end_y and cur_y + ffei + sfei >= end_y:
            bj = end_y - cur_y #big jump replaces sfei and is adjusted for if shingle is not full width, but row can still be placed
        
        while cur_x < ow:            
            p = len(verts)
            v = []
            sx = cur_x + sw #keep for placement of last row
            row_num = 4 #number of raised and lower sections placed
            ended_raised = False #keeps track of whether the shingles end in on a raised part or not
            
            #determine shingle height at front, middle, and back based on which row it is
            if row == 1:
                h1, h2, h3 = 0, 0, 0 #height 1, 2, and 3
            elif row == 2:
                h1, h2, h3 = lth, lth, 0
            elif row >= 3:
                h1, h2, h3 = 2 * lth, lth, 0
            
            #first row of vertices
            v += [(cur_x, cur_y, h1), (cur_x, cur_y, h1 + tth), (cur_x, cur_y + sj, h2), (cur_x, cur_y + sj, h2 + tth), (cur_x, cur_y + sj, h2 + lth)]
            if last_row_stay == True:
                v += [(cur_x, cur_y + bj, h3), (cur_x, cur_y + bj, h3 + tth), (cur_x, cur_y + bj, h3 + lth)]
                
            #pick random placements and random shift widths for "tabs"
            dist_shifts = [uniform(-2.5 / con, 2.5 / con) for i in range(2)]
            dist_shifts.insert(0, uniform(-2.0 / con, 2.0 / con))
            dist_shifts.append(uniform(-2.0 / con, 2.0 / con))
            
            widths = [uniform(1.0 / con, 2.5 / con) for i in range(2)]
            widths.insert(0, uniform(1.0 / con, 2.0 / con))
            widths.append(uniform(1.0 / con, 2.0 / con))
            
            step_widths = [small_tab, large_tab, large_tab, large_tab, small_tab]                   
            
            for i in range(4):
                cur_x += step_widths[i] + dist_shifts[i]
                
                #left and right widths and shift widths
                lw = widths[i]
                lsw = hi
                rw = widths[i]
                rsw = hi
                
                #booleans
                keep_right = True
                
                #check to see if left side needs trimmed down
                if cur_x >= ow and (cur_x - lsw - lw >= ow or cur_x - lw >= ow):
                    lsw = 0.0
                    lw = cur_x - ow 
                    keep_right = False
                    
                if keep_right == True and (cur_x + rw + rsw >= ow or cur_x + rw >= ow):
                    rsw = 0.0
                    rw = ow - cur_x
                    
                #vertices
                if final_row == False:
                    #left side
                    v += [(cur_x - lsw - lw, cur_y, h1), (cur_x - lsw - lw, cur_y, h1 + tth)]
                    
                    if keep_right == True: #this doesn't get connect to anything if it is final row and there is no verts to the right
                        v += [(cur_x - lsw - lw, cur_y, h1 + lth)]
                        
                    v += [(cur_x - lw, cur_y + sj, h2), (cur_x - lw, cur_y + sj, h2 + tth), (cur_x - lw, cur_y + sj, h2 + lth)]
                    
                    #remove last vertex if top row and last shingle and there is no left
                    if last_row_stay == False and keep_right == False:
                        del v[len(v) - 1]
                    
                    #back set
                    if last_row_stay == True:
                        v += [(cur_x - lw, cur_y + bj, h3), (cur_x - lw, cur_y + bj, h3 + tth), (cur_x - lw, cur_y + bj, h3 + lth)]
                    
                    #right side
                    if keep_right == True:
                        v += [(cur_x + rsw + rw, cur_y, h1), (cur_x + rsw + rw, cur_y, h1 + tth), (cur_x + rsw + rw, cur_y, h1 + lth)]
                        v += [(cur_x + rw, cur_y + sj, h2), (cur_x + rw, cur_y + sj, h2 + tth), (cur_x + rw, cur_y + sj, h2 + lth)]
                        
                        #back set
                        if last_row_stay == True:
                            v += [(cur_x + rw, cur_y + bj, h3), (cur_x + rw, cur_y + bj, h3 + tth), (cur_x + rw, cur_y + bj, h3 + lth)]                        
                
                if cur_x >= ow or (cur_x < ow and cur_x + rw >= ow):
                    final_row = True
                    
                #see if shingle is raised and this is the last shingle and it is cut
                if final_row == True and keep_right == True:
                    ended_raised = True
                    
                #set row_num so that when placing faces it knows what row was the last
                if final_row == True and row_num == 4:
                    row_num = i            

                #update cur_x
                cur_x -= dist_shifts[i]
            
            #final row
            if final_row == False:
                if sx > ow: 
                    sx = ow
                v += [(sx, cur_y, h1), (sx, cur_y, h1 + tth), (sx, cur_y + sj, h2), (sx, cur_y + sj, h2 + tth), (sx, cur_y + sj, h2 + lth)]
                if last_row_stay == True:
                    v += [(sx, cur_y + bj, h3), (sx, cur_y + bj, h3 + tth), (sx, cur_y + bj, h3 + lth)]
                cur_x = sx
                    
            for num in range(len(v)):
                point = point_rotation((v[num][1], v[num][2]), (-(wh / 2), v[num][2]), rot)
                verts.append((v[num][0], point[0], point[1]))
                
            #faces
            f = []            
            
            #first row                                
            if last_row_stay == True:
                f += [(p, p + 1, p + 3, p + 2), (p + 2, p + 3, p + 6, p + 5), (p + 3, p + 4, p + 7, p + 6), (p, p + 8, p + 9, p + 1), (p + 1, p + 9, p + 12, p + 3),
                        (p + 3, p + 12, p + 13, p + 4), (p + 4, p + 13, p + 16, p + 7), (p + 6, p + 7, p + 16, p + 15), (p + 5, p + 6, p + 15, p + 14),
                        (p, p + 2, p + 11, p + 8), (p + 2, p + 5, p + 14, p + 11)]
                p += 8

            else:
                f += [(p, p + 5, p + 6, p + 1), (p, p + 1, p + 3, p + 2), (p + 2, p + 3, p + 9, p + 8), (p, p + 2, p + 8, p + 5), (p + 1, p + 6, p + 9, p + 3)]
                p += 5             
                
            #middle faces
            for i in range(row_num):
                #raised section
                if last_row_stay == True:
                    f = arch_shingle_raised_faces(f, p, False)
                    p += 9
                
                else:
                    f += [(p, p + 6, p + 7, p + 1), (p + 1, p + 7, p + 8, p + 2), (p + 1, p + 2, p + 5, p + 4), (p + 2, p + 8, p + 11, p + 5),
                            (p + 7, p + 10, p + 11, p + 8), (p + 4, p + 5, p + 11, p + 10), (p + 3, p + 4, p + 10, p + 9), (p, p + 3, p + 9, p + 6)]
                    p += 6
                        
                #lower section                      
                if (i < row_num - 1 and ended_raised == False) or (i < row_num and ended_raised == True):                    
                    if last_row_stay == True:
                        if ended_raised == False and i == row_num - 1:
                            f = arch_shingle_lower_faces(f, p, False, True)
                        else:
                            f = arch_shingle_lower_faces(f, p, False, False)
                        p += 9
                    
                    else:
                        f += [(p, p + 6, p + 7, p + 1), (p + 1, p + 7, p + 10, p + 4), (p + 3, p + 4, p + 10, p + 9), (p, p + 3, p + 9, p + 6)]
                        p += 6
                        
            #last section
            if last_row_stay == True and final_row == False:
                f += [(p, p + 9, p + 10, p + 1), (p + 1, p + 10, p + 12, p + 4), (p + 4, p + 12, p + 13, p + 5), (p + 5, p + 13, p + 16, p + 8),
                        (p + 7, p + 8, p + 16, p + 15), (p + 6, p + 7, p + 15, p + 14), (p, p + 3, p + 11, p + 9), (p + 3, p + 6, p + 14, p + 11),
                        (p + 9, p + 11, p + 12, p + 10), (p + 11, p + 14, p + 15, p + 12), (p + 12, p + 15, p + 16, p + 13)]
                p += 9                                
            
            elif last_row_stay == False and final_row == False:
                f += [(p, p + 6, p + 7, p + 1), (p + 1, p + 7, p + 9, p + 4), (p + 3, p + 4, p + 9, p + 8), (p + 6, p + 8, p + 9, p + 7), (p, p + 3, p + 8, p + 6)]
                p += 6
                
            elif last_row_stay == True and final_row == True:
                if ended_raised == True:
                    f = arch_shingle_raised_faces(f, p, True)
                else:
                    f = arch_shingle_lower_faces(f, p, True, True)
                    
            elif last_row_stay == False and final_row == True:
                if ended_raised == True:
                    f += [(p, p + 6, p + 7, p + 1), (p + 6, p + 9, p + 10, p + 7), (p + 7, p + 10, p + 11, p + 8), (p + 1, p + 2, p + 5, p + 4), (p + 2, p + 8, p + 11, p + 5),
                            (p, p + 3, p + 9, p + 6), (p + 1, p + 7, p + 8, p + 2), (p + 4, p + 5, p + 11, p + 10), (p + 3, p + 4, p + 10, p + 9)]                             
                else:
                    f += [(p, p + 6, p + 7, p + 1), (p + 1, p + 7, p + 9, p + 4), (p + 3, p + 4, p + 9, p + 8), (p + 6, p + 8, p + 9, p + 7), (p, p + 3, p + 8, p + 6)]
                    
            for face in f:
                faces.append(face)
                             
            
        row += 1
        cur_y += ffei
        
    return verts, faces

def terra_cotta(wh, ow, slope, res, rad):
    verts = []; faces = []
    rot = atan(slope / 12)
    
    cur_y = -(wh / 2)
    con = 39.3701 #conversion factor
    
    #variables
    th = 0.5 / con; st_h = 2 / con; tile_l1 = 18 / con; tail_h = 0.5 / con
    rot_dif = radians(180 / (res  + 1))
    
    oh = (wh / 2) / cos(atan((((wh / 2) * slope) / 12) / (wh / 2)))
    end_y = cur_y + oh
        
    #main loop for width
    while cur_y < end_y:
        cur_x = rad #reset the distances moved length wise each time        
        
        #check to see if tile is to long
        if cur_y + tile_l1 > end_y:
            tile_l = end_y - cur_y
        else:
            tile_l = tile_l1
            
        while cur_x < ow:
            p = len(verts)
            cut_point = 0
            cur_z = st_h
            v = [] #temporary vert holder
            
            next_x, next_z = 0, 0
                    
            #left vertices
            for i in range(res + 2, 0, -1):
                cur_rot = rot_dif * i #calculate current rotation
                #calculate position    
                x, z = point_rotation((cur_x - rad, cur_z), (cur_x, cur_z), cur_rot + radians(180))               
                
                if x <= ow:
                    #second set of rotations for taper
                    x2, z2 = point_rotation((cur_x - rad + th, cur_z), (cur_x, cur_z), cur_rot + radians(180))
                    #third set or rotations for thickness
                    x3, z3 = point_rotation((cur_x - rad - th, cur_z), (cur_x, cur_z), cur_rot + radians(180))
                    #third set or rotations for thickness taper
                    x4, z4 = point_rotation((cur_x - rad, cur_z), (cur_x, cur_z), cur_rot + radians(180))
                    
                    #create vertice positions
                    v += [(x, cur_y, z + tail_h), (x2, cur_y + tile_l, z2), (x3, cur_y, z3 + tail_h), (x4, cur_y + tile_l, z4)]
                    #update these variables as to know last vertices position to use in update position for second half circle
                    next_x = x
                    next_z = z
                    #update cut_point
                    cut_point += 1
                
            cur_x = next_x + rad
            cur_z = next_z
            
            #right circle
            for i in range(0, res + 1, 1):
                cur_rot = rot_dif * (i + 1)
                #calculate position    
                x, z = point_rotation((cur_x - rad, cur_z), (cur_x, cur_z), cur_rot)
                
                if x <= ow:
                    #second set of rotations for taper
                    x2, z2 = point_rotation((cur_x - rad - th, cur_z), (cur_x, cur_z), cur_rot)
                    #third set or rotations for thickness
                    x3, z3 = point_rotation((cur_x - rad + th, cur_z), (cur_x, cur_z), cur_rot)
                    #third set or rotations for thickness taper
                    x4, z4 = point_rotation((cur_x - rad, cur_z), (cur_x, cur_z), cur_rot)
                    
                    #add
                    v += [(x, cur_y, z + tail_h), (x2, cur_y + tile_l, z2), (x3, cur_y, z3 + tail_h), (x4, cur_y + tile_l, z4)]
                    cut_point += 1
                
            for num in range(len(v)):
                point = point_rotation((v[num][1], v[num][2]), (-(wh / 2), v[num][2]), rot)
                verts.append((v[num][0], point[0], point[1]))
                
            #faces
            f = []
            #first face
            f += [(p, p + 2, p + 3, p + 1)]
            
            for i in range(cut_point - 1):
                f += [(p + 2, p + 6, p + 7, p + 3), (p, p + 1, p + 5, p + 4), (p, p + 4, p + 6, p + 2), (p + 1, p + 3, p + 7, p + 5)]
                p += 4
            
            #last face   
            f += [(p, p + 1, p + 3, p + 2)]
                
            for face in f:
                faces.append(face)
                                            
            #update cur_x    
            cur_x += rad * 1.25
        
        #update cur_y
        cur_y += tile_l1 * 0.75           
        
    return verts, faces
                                                 
def create_roofing(self, context, mode, mat, shingles, tin, length, width, slope, res, radius):
    verts = []; faces = []
    verts2 = []; faces2 = []
    return_ob = ""

    #tin
    if mat == "1":
        #normal
        if tin == "1":
            verts, faces = tin_normal(width, length, slope)
        #angular
        elif tin == "2":
            verts, faces = tin_angular(width, length, slope)
        #standing seam
        elif tin == "3":
            verts, faces = tin_standing_seam(width, length, slope)  

    #shingles
    elif mat == "2":
        #architectural shingles
        if shingles == "1":
            verts, faces = shingles_arch(mode, width, length, slope)
        #3-tab shingles
        elif shingles == "2":
            verts, faces = shingles_3tab(mode, width, length, slope)         
   
    #terra cotta   
    elif mat == "3":
        verts, faces = terra_cotta(width, length, slope, res, radius)
    
    #decide whether to replace current objects mesh or create a new object
    if mode == "add":
        mesh = bpy.data.meshes.new("roofing")
        mesh.from_pydata(verts, [], faces)
        context.object.data = mesh
    
    elif mode == "convert":
        mesh = bpy.data.meshes.new("roofing")
        mesh.from_pydata(verts, [], faces)
        return_ob = bpy.data.objects.new("roofing", mesh)
        context.scene.objects.link(return_ob)
        
    return return_ob 

def UpdateRoofing(self, context):            
    #main object    
    m_ob = context.object    
    obs = []
    ft = True
    
    mats = [] 
    
    #figure out which object needs to be the main object for cutting
    if m_ob.ro_main_name == "none" and m_ob.ro_object_add == "convert" and len(m_ob.face_groups) >= 1:
        #deselect objects and only duplicate active object
        sel = []
        for i in bpy.context.scene.objects:
            if i.select == True:
                sel.append(i.name)
                i.select = False
                
        m_ob.select = True
        
        #get materials on object
        for i in m_ob.data.materials:
            mats.append(i.name)
            
        bpy.ops.object.duplicate()
        n_ob = context.object
        n_ob.name = m_ob.name + "_cutter"
        m_ob.ro_main_name = n_ob.name
        
        bpy.ops.object.move_to_layer(layers = (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))
        context.scene.objects.active = m_ob
        m_ob.select = True
        
        for i in sel:
            bpy.data.objects[i].select = True
            
        use_ob = context.object
        roof_data = [use_ob.ro_object_add, use_ob.ro_mat, use_ob.ro_shingles, use_ob.ro_tin, use_ob.ro_res, use_ob.ro_tile_radius]
        
    #if the object to use for cutting is already on the other layer       
    elif m_ob.ro_main_name != "none":
        #get materials on object
        for i in m_ob.data.materials:
            mats.append(i.name)
            
        ft = False
        use_ob = bpy.data.objects[m_ob.ro_main_name]
        
        sel = []
        for i in bpy.context.scene.objects:
            if i.select == True:
                sel.append(i.name)
                i.select = False
        
        use_ob.select = True
        context.scene.objects.active = use_ob
        
        #collect which layers are selected, move to last layer, move object to active layer, then reselect previously selected layers
        al = context.scene.active_layer
        
        pre_layers = tuple(context.scene.layers)
        to_layers = [False for i in range(19)]
        to_layers.append(True)
        
        context.scene.layers = to_layers
        
        layer_list = [False for i in range(19)]
        layer_list.insert(al, True)
        move_layers = tuple(layer_list)
                                
        bpy.ops.object.move_to_layer(layers = move_layers)
        
        context.scene.layers = pre_layers
        
        roof_data = [m_ob.ro_object_add, m_ob.ro_mat, m_ob.ro_shingles, m_ob.ro_tin, m_ob.ro_res, m_ob.ro_tile_radius]
    
    else:
        use_ob = context.object      
    
    if use_ob.ro_object_add == "convert" and len(use_ob.face_groups) >= 1:                
        #deselect any object that is not the active object
        for ob in context.selected_objects:
            if ob != context.object:
                ob.select = False
                
        #duplicate cutter object and move to last layer for next time
        if ft == False:
            use_ob.select = True
            context.scene.objects.active = use_ob
            
            bpy.ops.object.duplicate()
            
            dup_ob = context.object
            mv_layers = [False for i in range(19)]
            mv_layers.append(True)
            bpy.ops.object.move_to_layer(layers = mv_layers)
            
            dup_ob.select = False
            use_ob.select = True
            context.scene.objects.active = use_ob
                
        #split objects based on face groups
        fg = []        
        #create groups of face centers for cutting use the data in ob.face_groups
        for f_g in use_ob.face_groups:
            st = f_g.data.split(",")
            del st[len(st) - 1]
            
            temp_l = []
            for i in st:
                st2 = i.split("+")
                tl = (float(st2[0]), float(st2[1]), float(st2[2]))
                temp_l.append(tl)
            
            temp_m = [temp_l, f_g.face_slope, f_g.rot]
            fg.append(temp_m)           
            
        #split object
        #deselect all faces and edges to make sure no extra geometry gets separated                   
        for f in use_ob.data.polygons:
            f.select = False
        for e in use_ob.data.edges:
            e.select = False
        for v in use_ob.data.vertices:
            v.select = False
             
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        
        #select faces and separate by selection
        #remove first object from list and apply it to the main object
        main_data = fg[0]
        del fg[0]                  
        
        for i in fg:            
            for i2 in i[0]:
                for face_in_obj in use_ob.data.polygons:
                    if round_tuple(tuple(face_in_obj.center), 4) == i2:                     
                        face_in_obj.select = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.separate(type = "SELECTED")
            bpy.ops.object.editmode_toggle()            
            
            #set newly created plane objects pl_z_rot and pl_pitch for use when creating roofing for it
            temp_ob = bpy.context.selected_objects[0]
            temp_ob.pl_pitch = i[1]
            temp_ob.pl_z_rot = i[2]
            
        use_ob.pl_pitch = main_data[1]
        use_ob.pl_z_rot = main_data[2]
        
        #create list of objects and solidify current ones           
        for ob in context.selected_objects:
            obs.append(ob.name)
            context.scene.objects.active = ob
            bpy.ops.object.modifier_add(type = "SOLIDIFY")
            context.object.modifiers["Solidify"].thickness = 0.1
            context.object.modifiers["Solidify"].offset = 0.0            
        
        #reset main object
        context.scene.objects.active = use_ob
     
    roofing_names = []
    main_name = ""  
    #for each cutter object
    if use_ob.ro_object_add == "convert" and obs != []:
        #deselect all objects
        for i in context.selected_objects:
            i.select = False
            
        #get rid of extra vertices in main object
        index_list = []
        for fa in use_ob.data.polygons:
            for vt in fa.vertices:
                if vt not in index_list:
                    index_list.append(vt)
        for vt in use_ob.data.polygons:
            if vt.index not in index_list:
                vt.select = True
        
        use_ob.select = True
        context.scene.objects.active = use_ob
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.delete(type = "VERT")
        bpy.ops.object.editmode_toggle() 
        use_ob.select = False
               
        for o_name in obs:
            o = bpy.data.objects[o_name]
            
            #calculate size and then create siding and cut it
            xy_dims, z = object_dimensions(o)
            #calculate height
            ang = atan(o.pl_pitch / 12)
            z_dim = 2 * z / sin(ang) #multiplied by two to correct for normally using half width
            
            #create roofing object
            new_ob = create_roofing(self, context, roof_data[0], roof_data[1], roof_data[2], roof_data[3], xy_dims, z_dim, o.pl_pitch, roof_data[4], roof_data[5])
            
            #center o's origin point
            o.select = True
            context.scene.objects.active = o
            
            bpy.ops.object.origin_set(type = "ORIGIN_GEOMETRY")
            
            o.select = False
            #set new object's location and rotation
            new_ob.select = True
            context.scene.objects.active = new_ob
            bpy.ops.object.origin_set(type = "ORIGIN_GEOMETRY")            
             
            new_ob.location = o.location
            eur = Euler((0.0, 0.0, o.pl_z_rot), "XYZ")
            new_ob.rotation_euler = eur
            
            #solidify new object
            if roof_data[1] == "1":
                bpy.ops.object.modifier_add(type = "SOLIDIFY")
                new_ob.modifiers["Solidify"].thickness = 0.00028702
                bpy.ops.object.modifier_apply(modifier = "Solidify", apply_as = "DATA")
            
            #boolean new object
            #fix normals            
            bpy.ops.object.modifier_add(type = "BOOLEAN")
            new_ob.modifiers["Boolean"].object = o
            bpy.ops.object.modifier_apply(modifier = "Boolean", apply_as = "DATA")                                     
            
            #if current object is the main object set roofing objects name to main_name
            if o.name == use_ob.name:
                main_name = new_ob.name
            else:
                roofing_names.append(new_ob.name)          

        #deselect all objects
        for i in context.selected_objects:
            i.select = False
        #get rid of extra objects and join roofing objects
        for na in obs:
            if na != use_ob.name:
                temp_ob = bpy.data.objects[na]
                temp_ob.select = True
                context.scene.objects.active = temp_ob
                bpy.ops.object.delete()
                
        last_ob = bpy.data.objects[main_name]        
        use_ob.data = last_ob.data
        eur = Euler((0.0, 0.0, use_ob.pl_z_rot), "XYZ")
        use_ob.rotation_euler = eur
        last_ob.select = True
        context.scene.objects.active = last_ob
        bpy.ops.object.delete()
        
        #join remaining rooing objects to use_ob
        for na in roofing_names:
            bpy.data.objects[na].select = True
            
        use_ob.select = True
        context.scene.objects.active = use_ob
        bpy.ops.object.join()                
                
        bpy.ops.object.modifier_remove(modifier = "Solidify")
        
        #if this is not the first time creating object transfer mesh to main object
        if ft == False:                        
            m_ob.data = use_ob.data       
            bpy.ops.object.delete()
            m_ob.select = True
            context.scene.objects.active = m_ob                        
            
            dup_ob.name = m_ob.name + "_cutter"
            
        #uvs and materials
        if m_ob.ro_unwrap == True:
            UnwrapRoofing(self, context)
            
            if m_ob.ro_random_uv == True:
                RandomUV(self, context)
                
        for i in mats:
            mat = bpy.data.materials[i]
            m_ob.data.materials.append(mat)
            
    #if object is added, create mesh
    if m_ob.ro_object_add == "add":
        
        #collect materials currently on object
        for i in m_ob.data.materials:
            mats.append(i.name)
            
        #create new object
        nothing = create_roofing(self, context, m_ob.ro_object_add, m_ob.ro_mat, m_ob.ro_shingles, m_ob.ro_tin, m_ob.ro_length, m_ob.ro_width, m_ob.ro_slope, m_ob.ro_res, m_ob.ro_tile_radius)
        
        #add materials back
        for i in mats:
            mat = bpy.data.materials[i]
            m_ob.data.materials.append(mat)
            
        #work on uv's
        if m_ob.ro_unwrap == True:
            UnwrapRoofing(self, context)
            
            if m_ob.ro_random_uv == True:
                RandomUV(self, context)
        
        #create mirrored object
        if m_ob.ro_mirror == True:
            bpy.ops.object.modifier_add(type = "MIRROR")
            context.object.modifiers["Mirror"].use_x = False
            context.object.modifiers["Mirror"].use_y = True
            bpy.ops.object.modifier_apply(apply_as = "DATA", modifier = "Mirror")
    
def DeleteMaterials(self, context):
    o = context.object
    if o.ro_is_material == False:
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
                    if bpy.context.object.ro_is_preview == True: space.viewport_shade = 'RENDERED'
                    else: space.viewport_shade = "SOLID"
                    
def UnwrapRoofing(self, context):
    o = context.object
    #uv unwrap
    for i in bpy.data.objects: i.select = False
    o.select = True; bpy.context.scene.objects.active = o    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    bpy.ops.object.editmode_toggle()
                    override = bpy.context.copy(); override["area"] = area; override["region"] = region; override["active_object"] = (bpy.context.selected_objects)[0]
                    bpy.ops.mesh.select_all(action = "SELECT"); bpy.ops.uv.cube_project(override); bpy.ops.object.editmode_toggle()

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
                        
def RoofingMaterial(self, context):    
    #create material
    o = bpy.context.object; error = False
    
    #check to make sure pictures have been picked
    if o.ro_col_image == "" and o.ro_mat in ("2", "3"): 
        self.report({"ERROR"}, "No Color Image Entered"); error = True
    if o.ro_is_bump == True and o.ro_norm_image == "" and o.ro_mat in ("2", "3"): 
        self.report({"ERROR"}, "No Normal Map Image Entered"); error = True
   
    if error == False:
        if o.ro_mat == "1":
            mat = GlossyDiffuse(bpy, o.ro_color, (1.0, 1.0, 1.0), 0.18, 0.05, "roofing_use")   
        
        elif o.ro_mat in ("2", "3"):
            mat = Image(bpy, context, o.ro_im_scale, o.ro_col_image, o.ro_norm_image, o.ro_bump_amo, o.ro_is_bump, "roofing_use", True, 0.1, 0.05, o.ro_is_rotate, None)
        
        if mat != None:
            if len(o.data.materials) == 0:
                o.data.materials.append(mat.copy())
            else:
                o.data.materials[0] = mat.copy()
            o.data.materials[0].name = "flooring_" + o.name
        else: self.report({"ERROR"}, "Images Not Found, Make Sure Path Is Correct")     
    #remove extra materials
    for i in bpy.data.materials:
        if i.users == 0: bpy.data.materials.remove(i)
        
def update_selection(self, context):
    ##updates which faces are selected based on which face group is selcted in the UI##
    ob = context.object
    bpy.ops.object.editmode_toggle()
    
    if len(ob.face_groups) >= 1:
        fg = ob.face_groups[ob.group_index]        
        
        #deselect all faces and edges
        for f in ob.data.polygons:          
            f.select = False
        for e in ob.data.edges:
            e.select = False            
        
        #get info from face group and use to define selection
        st = fg.data.split(",")
        del st[len(st) - 1]
        
        temp_l = []
        for i in st:
            st2 = i.split("+")
            tl = (float(st2[0]), float(st2[1]), float(st2[2]))
            temp_l.append(tl)            
        
        #select correct faces
        for f in temp_l:
            for face_in_obj in ob.data.polygons:
                if round_tuple(tuple(face_in_obj.center), 4) == f:                    
                    face_in_obj.select = True
                    
        #make sure selection list is up to date
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        
    bpy.ops.object.editmode_toggle()      
    
    #helper object
def UpdateHelper(self, context):
    cur_ob = context.object
    
    #create object if necessary
    if "jarch_vis_roofing_helper" not in bpy.data.objects:
        mw = 1.0 #main width
        ow = 1.2 #outside width
        aw = 0.05 #arrow width
        aow = 0.1 #outside arrow width
        ah = 0.75 #arrow height
        #square
        verts = ((-mw, mw, 0.0), (mw, mw, 0.0), (mw, -mw, 0.0), (-mw, -mw, 0.0))
        verts += ((-ow, ow, 0.0), (ow, ow, 0.0), (ow, -ow, 0.0), (-ow, -ow, 0.0))
        #arrow
        verts += ((-aw, 0.0, 0.0), (-aw, 0.0, ah), (-aow, 0.0, ah), (0.0, 0.0, ah + 0.1), (aow, 0.0, ah), (aw, 0.0, ah), (aw, 0.0, 0.0))
        verts += ((0.0, -aw, 0.0), (0.0, -aw, ah), (0.0, -aow, ah), (0.0, 0.0, ah + 0.1), (0.0, aow, ah), (0.0, aw, ah), (0.0, aw, 0.0))
        #faces
        faces = ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (0, 4, 7, 3), (8, 14, 13, 9), (9, 13, 12, 10), (10, 12, 11), (15, 21, 20, 16),
                (16, 20, 19, 17), (17, 19, 18))
        mesh = bpy.data.meshes.new("jarch_vis_roofing_helper")
        mesh.from_pydata(verts, [], faces)
        obj = bpy.data.objects.new("jarch_vis_roofing_helper", mesh)
        bpy.context.scene.objects.link(obj)
    #if object is hidden
    else:
        obj = bpy.data.objects["jarch_vis_roofing_helper"]
        obj.hide = False
    
    
    #make sure it is on correct layer if not move it
    cur_layers = [i for i in bpy.context.scene.layers]
    to_layers = [i for i in obj.layers]
    
    if to_layers != cur_layers:
        bpy.ops.object.editmode_toggle()
        cur_ob.select = False
        obj.select = True
        context.scene.objects.active = obj            
        
        bpy.context.scene.layers = to_layers
        bpy.ops.object.move_to_layer(layers = cur_layers)
        
        bpy.context.scene.layers = cur_layers
        
        obj.select = False
        cur_ob.select = True
        context.scene.objects.active = cur_ob
        bpy.ops.object.editmode_toggle()
    
    #set location and rotation
    #if there is a face group find and use it
    if False:#len(cur_ob.face_groups) > 0:
        fg = cur_ob.face_groups[cur_ob.group_index]
        
        #face data
        face_centers = []   
        for i in fg.data.split(","):
            temp = i.split("+")
            if len(temp) > 1: #make sure this isn't the last comma
                face_centers.append((float(temp[0]), float(temp[1]), float(temp[2])))
                
        x, y, z = find_face_center(cur_ob, face_centers, False)
        obj.location = (x, y, z)
    #find the center of any currently selected faces
    else:
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        x, y, z = find_face_center(cur_ob, None, False)
        obj.location = (x, y, z)
    
    #determine rotation based on selected face_group
    if False:#len(cur_ob.face_groups) > 0:
        fg = cur_ob.face_groups[cur_ob.group_index]
        x_rot = atan(fg.face_slope / 12)
        rot = Euler((x_rot, 0.0, fg.rot), "XYZ")
    else:
        x_rot = atan(cur_ob.pl_pitch / 12)
        rot = Euler((x_rot, 0.0, cur_ob.pl_z_rot), "XYZ")
    
    obj.rotation_euler = rot 
    
#the obj to look through, faces centers that can be used if they are selcted
def find_face_center(obj, allowed_faces, selected):
    x_med, y_med, z_med = 0, 0, 0
    cc = 0
    
    for fa in obj.data.polygons: #for all the faces in the object
        if (allowed_faces == None and selected) or (allowed_faces == None and fa.select and not selected) or (allowed_faces != None and round_tuple(fa.center, 4) in allowed_faces): #if the rounded version is in this face group
            for v_index in fa.vertices: #go through the vertices indexs and get x, y, z
                vert = obj.matrix_world * obj.data.vertices[v_index].co
                x_med += vert[0]
                y_med += vert[1]
                z_med += vert[2]
                cc += 1
             
    #find average of points
    x, y, z = 0, 0, 0
    if cc > 0:
        x = x_med / cc
        y = y_med / cc
        z = z_med / cc
    
    return x, y, z

def add_item(self, context):
    ob = context.object
    fa_str = ""
    counter = 0
    
    #toggle editmode to update which edges are selected
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()
    
    selected_faces = []
    #create list of selected edges
    for fa in ob.data.polygons:
        if fa.select == True:
            selected_faces.append(fa)
            temp_str = str(round(fa.center[0], 4)) + "+" + str(round(fa.center[1], 4)) + "+" + str(round(fa.center[2], 4))
            fa_str += temp_str + ", "            
            counter += 1
                                
    if counter != 0: #make sure a face is selected
        item = ob.face_groups.add()
        
        #set collection object item data
        item.data = fa_str
        item.num_faces = counter
        
        #calculate slope and rotation
        slope, z_rot = ob.pl_pitch, ob.pl_z_rot
        item.face_slope = slope
        item.rot = z_rot
        
        item.name = "Group " + str(ob.face_groups_num)
        
        ob.group_index = len(ob.face_groups) - 1
        ob.face_groups_num = len(ob.face_groups) 
        
def update_item(self, context):
    ob = context.object
    if len(ob.face_groups) >= 1:
        fg = ob.face_groups[ob.group_index]
        counter = 0
        fa_str = ""
        
        #toggle editmode to update which edges are selected
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
    
        selected_faces = []
        #create list of selected edges
        for fa in ob.data.polygons:
            if fa.select == True:
                selected_faces.append(fa)
                temp_str = str(round(fa.center[0], 4)) + "+" + str(round(fa.center[1], 4)) + "+" + str(round(fa.center[2], 4))
                fa_str += temp_str + ", "            
                counter += 1
                
        #set collection object item data
        fg.data = fa_str
        fg.num_faces = counter
        
        #get slope and rot
        slope, z_rot = ob.pl_pitch, ob.pl_z_rot
        fg.face_slope = slope
        fg.rot = z_rot                       
            
#properties
#face groups
bpy.types.Object.face_groups_num = IntProperty(default = 0)
bpy.types.Object.group_index = IntProperty(update = update_selection)

#planes info
bpy.types.Object.pl_z_rot = FloatProperty(unit = "ROTATION", name = "Object Z Rotation", update = UpdateHelper)
bpy.types.Object.pl_pitch = FloatProperty(min = 1.0, max = 24.0, default = 4.0, name = "Pitch X/12", update = UpdateHelper)

#overall
bpy.types.Object.ro_main_name = StringProperty(default = "none")
bpy.types.Object.ro_object_add = StringProperty(default = "none", update = UpdateRoofing)
bpy.types.Object.ro_mat = EnumProperty(name = "Material", items = (("1", "Tin", ""), ("2", "Shingles", ""), ("3", "Terra Cotta", "")), update = UpdateRoofing)
bpy.types.Object.ro_shingles = EnumProperty(name = "Shingle Style", items = (("1", "Architectural", ""), ("2", "3-Tab", "")), update = UpdateRoofing)
bpy.types.Object.ro_tin = EnumProperty(name = "Tin Type", items = (("1", "Normal", ""), ("2", "Angular", ""), ("3", "Standing Seam", "")), update = UpdateRoofing)
bpy.types.Object.ro_length = FloatProperty(name = "Overall Length", min = 4 / 3.28084, max = 100 / 3.28084, default = 24 / 3.28084, subtype = "DISTANCE", update = UpdateRoofing)
bpy.types.Object.ro_width = FloatProperty(name = "Overall Width", min = 4 / 3.28084, max = 80 / 3.28084, default = 12 / 3.28084, subtype = "DISTANCE", update = UpdateRoofing)
bpy.types.Object.ro_slope = FloatProperty(name = "Slope (X/12)", min = 1.0, max = 12.0, default = 4.0, update = UpdateRoofing)
bpy.types.Object.ro_mirror = BoolProperty(name = "Mirror?", default = True, update = UpdateRoofing)

bpy.types.Object.ro_res = IntProperty(name = "Curve Resolution", min = 3, max = 10, default = 5, update = UpdateRoofing)
bpy.types.Object.ro_tile_radius = FloatProperty(name = "Tile Radius", min = 1.5 / 39.3701, max = 3.0 / 39.3701, default = 2.0 / 39.3701, update = UpdateRoofing, subtype = "DISTANCE")

#materials
bpy.types.Object.ro_is_material = BoolProperty(name = "Cycles Materials?", default = False, description = "Adds Cycles Materials", update = DeleteMaterials)
bpy.types.Object.ro_is_preview = BoolProperty(name = "Preview Material?", default = False, description = "Preview Material On Object", update = PreviewMaterials)
bpy.types.Object.ro_im_scale = FloatProperty(name = "Image Scale", max = 10.0, min = 0.1, default = 1.0, description = "Change Image Scaling")
bpy.types.Object.ro_col_image = StringProperty(name = "", subtype = "FILE_PATH", description = "File Path For Color Image")
bpy.types.Object.ro_is_bump = BoolProperty(name = "Normal Map?", default = False, description = "Add Normal To Material?")
bpy.types.Object.ro_norm_image = StringProperty(name = "", subtype = "FILE_PATH", description = "File Path For Normal Map Image")
bpy.types.Object.ro_bump_amo = FloatProperty(name = "Normal Stength", min = 0.001, max = 2.000, default = 0.250, description = "Normal Map Strength")
bpy.types.Object.ro_unwrap = BoolProperty(name = "UV Unwrap?", default = True, description = "UV Unwraps Siding", update = UnwrapRoofing)
bpy.types.Object.ro_is_rotate = BoolProperty(name = "Rotate Image?", default = False, description = "Rotate Image 90 Degrees")
bpy.types.Object.ro_random_uv = BoolProperty(name = "Random UV's?", default = True, description = "Random UV's", update = UpdateRoofing)
bpy.types.Object.ro_color = FloatVectorProperty(name = "Tin Color", subtype = "COLOR", default = (1.0, 1.0, 1.0), min = 0.0, max = 1.0, description = "Color For Tin")


class RoofingPanel(bpy.types.Panel): ###Panel###
    bl_idname = "OBJECT_PT_jarch_roofing"
    bl_label = "JARCH Vis: Roofing"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "JARCH Vis"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        ob = context.object
        
        #if in edit mode layout UIlist
        if ob != None:
            if ob.object_add == "none" and ob.s_object_add == "none" and ob.f_object_add == "none":
                if context.mode == "EDIT_MESH" and ob.ro_object_add == "none":                
                    layout.template_list("OBJECT_UL_face_groups", "", ob, "face_groups", ob, "group_index")
                    layout.separator()
                    layout.prop(ob, "pl_z_rot")
                    layout.prop(ob, "pl_pitch")
                    layout.separator()
                    layout.operator("mesh.jarch_vis_roofing_update_helper", icon = "FILE_TICK") 
                    layout.separator()
                    layout.operator("mesh.jarch_vis_add_item", icon = "ZOOMIN")
                    layout.operator("mesh.jarch_vis_remove_item", icon = "ZOOMOUT")
                    layout.operator("mesh.jarch_vis_update_item", icon = "FILE_REFRESH")
                
                elif context.mode == "EDIT_MESH" and ob.ro_object_add != "none":
                    layout.label("This Object Is Already A JARCH Vis: Siding Object", icon = "INFO")
                    
                #if in object mode and there are face groups
                if (context.mode == "OBJECT" and len(ob.face_groups) >= 1 and ob.ro_object_add == "convert") or ob.ro_object_add == "add":
                    if ob.ro_object_add != "convert":
                        layout.prop(ob, "ro_mat", icon = "MATERIAL")
                    else:
                        layout.label("Material: Tin", icon = "MATERIAL")
                    
                    if ob.ro_mat == "1":
                        layout.prop(ob, "ro_tin")
                    elif ob.ro_mat == "2":
                        layout.prop(ob, "ro_shingles")               
                        
                    layout.separator()
                    
                    if ob.ro_object_add != "convert":
                        layout.prop(ob, "ro_length")
                        layout.prop(ob, "ro_width")
                        layout.prop(ob, "ro_slope")
                        layout.separator()
                        layout.prop(ob, "ro_mirror", icon = "MOD_MIRROR")
                        
                    layout.separator()
                    
                    if ob.ro_mat == "3":
                        layout.prop(ob, "ro_tile_radius")
                        layout.prop(ob, "ro_res")
                    
                    
                    #uv stuff
                    layout.prop(ob, "ro_unwrap", icon = "GROUP_UVS")
                    layout.prop(ob, "ro_random_uv", icon = "RNDCURVE")
                                        
                    #materials
                    layout.separator()               
                    if context.scene.render.engine == "CYCLES": 
                        layout.prop(ob, "ro_is_material", icon = "MATERIAL")
                    else: 
                        layout.label("Materials Only Supported With Cycles", icon = "POTATO")
                        
                    if ob.ro_is_material == True and context.scene.render.engine == "CYCLES":
                        layout.separator()
                        if ob.ro_mat == "1": #tin
                            layout.prop(ob, "ro_color")
                            
                        elif ob.ro_mat in ("2", "3"): #shingles and terra cotta
                            layout.prop(ob, "ro_col_image", icon = "COLOR")
                            layout.prop(ob, "ro_is_bump", icon = "SMOOTHCURVE")
                            
                            if ob.ro_is_bump == True:                            
                                layout.prop(ob, "ro_norm_image", icon = "TEXTURE")
                                layout.prop(ob, "ro_bump_amo")
                            
                            layout.prop(ob, "ro_im_scale")
                            layout.separator()                       
                            layout.prop(ob, "ro_is_rotate", icon = "MAN_ROT")
                            
                        layout.separator()
                        layout.operator("mesh.jarch_roofing_materials", icon = "MATERIAL")
                        layout.separator()
                        layout.prop(ob, "ro_is_preview", icon = "SCENE")
                                                
                    #operators
                    layout.separator()
                    layout.operator("mesh.jarch_roofing_update", icon = "FILE_REFRESH")
                    layout.operator("mesh.jarch_roofing_mesh", icon = "OUTLINER_OB_MESH")
                    layout.operator("mesh.jarch_roofing_delete", icon = "CANCEL")
                    
                
                elif ob.ro_object_add == "none" and context.mode == "OBJECT" and len(ob.face_groups) == 0:
                    layout.label("Enter Edit Mode And Create Face Groups", icon = "ERROR")
                    
                #if object has      
                elif ob.ro_object_add == "none" and context.mode == "OBJECT" and len(ob.face_groups) >= 1:                
                    layout.operator("mesh.jarch_roofing_convert")
            else:
                layout.label("This Is Already A JARCH Vis Object", icon = "POTATO")              
        else:
            layout.operator("mesh.jarch_roofing_add", icon = "LINCURVE")    

class RunUpdateHelper(bpy.types.Operator):
    bl_idname = "mesh.jarch_vis_roofing_update_helper"
    bl_label = "Update\\Add Helper Object"
    bl_options = {"INTERNAL"}
    
    def execute(self, context):
        UpdateHelper(self, context)
        return {"FINISHED"}                       

class OBJECT_UL_face_groups(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):         
        row = layout.row(align = True)        
        row.prop(item, "name", text="", emboss=False, translate=False, icon = "FACESEL")
        row.label("Faces: " + str(item.num_faces))
        row.label("Pitch: " + str(round(item.face_slope, 3)))
        row.label("Rot: " + str(round(degrees(item.rot), 1)))               

class RoofingUpdate(bpy.types.Operator):
    bl_idname = "mesh.jarch_roofing_update"
    bl_label = "Update Roofing"
    bl_description = "Update Roofing"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        UpdateRoofing(self, context)
        return {"FINISHED"}
    
class RoofingMesh(bpy.types.Operator):
    bl_idname = "mesh.jarch_roofing_mesh" 
    bl_label = "Convert To Mesh"
    bl_description = "Converts Roofing Object To Normal Object (No Longer Editable)"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        o = context.object
        o.ro_object_add = "mesh"
        return {"FINISHED"}
    
class RoofingDelete(bpy.types.Operator):
    bl_idname = "mesh.jarch_roofing_delete"
    bl_label = "Delete Roofing"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        o = context.object
        #deselect any selected objects
        for i in context.selected_objects:
            i.select = False
        
        if o.ro_object_add == "add":
            o.select = True
            bpy.ops.object.delete()
        
        elif o.ro_object_add == "convert":
            second_obj = bpy.data.objects[o.ro_main_name]
            
            if second_obj != None:                
                o.select = False
                second_obj.select = True
                context.scene.objects.active = second_obj

                #move to last layer, move that object back, then move back
                first_layers = [i for i in bpy.context.scene.layers]
                move_layers = [False for i in range(19)]
                move_layers.append(True)
                
                bpy.context.scene.layers = move_layers                        
                bpy.ops.object.move_to_layer(layers = first_layers)
                bpy.context.scene.layers = first_layers
                
                second_obj.ro_object_add = "none"
                #remove "_cutter" from name
                if second_obj.name[len(second_obj.name) - 7:len(second_obj.name)] == "_cutter":
                    second_obj.name = second_obj.name[0:len(second_obj.name) - 7]
                second_obj.select = False                
                
                o.select = True
                context.scene.objects.active = o
                bpy.ops.object.delete()                                
            
        return {"FINISHED"}

class RoofingMaterials(bpy.types.Operator):
    bl_idname = "mesh.jarch_roofing_materials"
    bl_label = "Generate\\Update Materials"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        RoofingMaterial(self, context)
        return {"FINISHED"}
            
class RoofingAdd(bpy.types.Operator):
    bl_idname = "mesh.jarch_roofing_add"
    bl_label = "Add Roofing"
    bl_description = "JARCH Vis: Roofing Generator"
    
    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        o = bpy.context.scene.objects.active
        o.ro_object_add = "add"
        return {"FINISHED"}
    
class RoofingConvert(bpy.types.Operator):
    bl_idname = "mesh.jarch_roofing_convert"
    bl_label = "Convert To Roofing"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        o = context.object
        o.ro_object_add = "convert"
        return {"FINISHED"}    
    
class FGAddItem(bpy.types.Operator):
    bl_idname = "mesh.jarch_vis_add_item"
    bl_label = "Add Group"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        add_item(self, context)
        UpdateHelper(self, context)
        return {"FINISHED"}
    
class FGRemoveItem(bpy.types.Operator):
    bl_idname = "mesh.jarch_vis_remove_item"
    bl_label = "Remove Group"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        ob = context.object
        if len(ob.face_groups) > 0:
            ob.face_groups.remove(context.object.group_index)
            ob.face_groups_num = len(ob.face_groups)
           
            if len(ob.face_groups) == 0:
                ob.group_index = 0
            else:
                ob.group_index = len(ob.face_groups) - 1
        return {"FINISHED"}
    
class FGUpdateItem(bpy.types.Operator):
    bl_idname = "mesh.jarch_vis_update_item"
    bl_label = "Update Group"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        update_item(self, context)
        return {"FINISHED"}           