#convert
def convert(num, to):
    if to == "ft":
        out = num / 3.28084
    elif to == "in":
        out = num / 39.3701
    re = round(out, 5)
    return re

#point rotation
def point_rotation(data, origin, rot):
    from math import sin, cos
    ###Takes in a single tuple (x, y) or a tuple of tuples ((x, y), (x, y)) and rotates them rot radians around origin, returns new (x, y) or ((x, y), (x, y)) values###
    if len(data) == 2 and (isinstance(data[0], float) or isinstance(data[0], int)):
        point = data; new_point = (point[0] - origin[0], point[1] - origin[1]); x = new_point[0]; y = new_point[1]
        new_x = (x * cos(rot)) - (y * sin(rot)); new_y = (x * sin(rot)) - (y * cos(rot))
        out = (new_x + origin[0], new_y + origin[1])
        return (round(out[0], 4), round(out[1], 4))
    else:
        out_list = []
        for point in data:
            new_point = (point[0] - origin[0], point[1] - origin[1]); x = new_point[0]; y = new_point[1]
            new_x = (x * cos(rot)) - (y * sin(rot)); new_y = (x * sin(rot)) - (y * cos(rot))
            out = (new_x + origin[0], new_y + origin[1]); out_list.append((round(out[0], 4), round(out[1], 4)))
        return out_list
    
#find objects rotation
def object_rotation(obj):
    from math import atan, radians    
    #get list of vertices
    verts = [(obj.matrix_world * i.co).to_tuple() for i in obj.data.vertices]
    #create temporary list then round any numbers that are really small to zero
    v1_temp = verts[0]
    v1 = []
    for num in v1_temp:
        if -0.00001 < num < 0.00001:
            num = 0.0
        v1.append(round(num, 5))
    #find numbers that work with the original number    
    v2_temp = 0
    for i in verts:
        i2 = []
        for num in i: #round off numbers if close
            if -0.00001 < num < 0.00001:
                num = 0.0
            i2.append(round(num, 5))
        #are number correct?
        if (i2[0] != v1[0] and i2[1] == v1[1]) or (i2[0] == v1[0] and i2[1] != v1[1]) or (i2[0] != v1[0] and i2[1] != v1[1]) and v2_temp == 0:
            v2_temp = i2
    #calculate angle        
    if v2_temp != 0:
        skip = False
        if v2_temp[0] != v1[0] and v2_temp[1] == v1[1]: #plane is inline with x-axis
            skip = True
        if skip != True:  
            v2 = (v2_temp[0] - v1[0], v2_temp[1] - v1[1], v2_temp[2] - v1[2])
            if v2[0] != 0:
                angle = atan(v2[1] / v2[0])
            else:
                angle = radians(90)
        else:
            angle = 0
    else:
        angle = radians(90)

    return angle

#figure exact object dimensions
def object_dimensions(obj):
    from math import sqrt
    
    verts = [(obj.matrix_world * i.co).to_tuple() for i in obj.data.vertices]
    sx, bx, sy, by, sz, bz = 0, 0, 0, 0, 0, 0

    for val in verts:
        #x axis
        if val[0] < sx:
            sx = val[0]
        elif val[0] > bx:
            bx = val[0]
        #y axis
        if val[1] < sy:
            sy = val[1]
        elif val[1] > by:
            by = val[1]
        #z axis
        if val[2] < sz:
            sz = val[2]
        elif val[2] > bz:
            bz = val[2]
    #lengths
    x = (round(bx - sx, 5)) * obj.scale[0]
    y = (round(by - sy, 5)) * obj.scale[1]
    z = (round(bz - sz, 5)) * obj.scale[2]

    dia = sqrt(x ** 2 + y ** 2)
    
    return [dia, z]

def round_tuple(tup, digits):
    temp = []
    for i in tup:
        temp.append(round(i, digits))
    return tuple(temp)

def vertex_slope_rot(faces, obj):
    from math import sqrt, asin
    
    face = faces[0]
    
    verts_indexs = []
    
    for i in face.vertices: #get positions
        verts_indexs.append(i)        

    p1, p2, p3, p4 = 0, 0, 0, 0
        
    for i in obj.data.edges:
        #check and see if verts are in face
        if i.vertices[0] in verts_indexs and i.vertices[1] in verts_indexs:            
            p1_temp = obj.matrix_world * obj.data.vertices[i.vertices[0]].co
            p2_temp = obj.matrix_world * obj.data.vertices[i.vertices[1]].co
            
            #check and see if this works for finding z_rot
            if round(p1_temp[2], 5) == round(p2_temp[2], 5): #have same z value so horizontal edge
                p1 = p1_temp
                p2 = p2_temp                
            else:
                p3 = p1_temp
                p4 = p2_temp 

    x_dif = p2[0] - p1[0]
    y_dif = p2[1] - p1[1]

    long_side = sqrt(x_dif ** 2 + y_dif ** 2)
        
    z_rot = asin(y_dif / long_side)

    #slope
    
    x_dif2 = p4[0] - p3[0]
    y_dif2 = p4[1] - p3[1]
    z_dif2 = p4[2] - p3[2]

    slope = sqrt(x_dif2 ** 2 + y_dif2 ** 2)
    y_rot = abs(round((12 / slope) * z_dif2, 2))
    
    return y_rot, z_rot