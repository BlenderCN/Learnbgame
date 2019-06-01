import bpy
from mathutils import Vector
from mathutils.geometry import intersect_line_line_2d

def canevas_space(point,scale,offset) :
    return scale*Vector(point)+Vector(offset)


def intersect_rectangles(bound, border):  # returns None if rectangles don't intersect
    dx = min(border[1][0],bound[1][0]) - max(border[0][0],bound[0][0])
    dy = min(border[0][1],bound[0][1]) - max(border[2][1],bound[2][1])

    if (dx>=0) and (dy>=0):
        return dx*dy

def point_inside_rectangle(point, rect):
    return rect[0][0]< point[0]< rect[1][0] and rect[2][1]< point[1]< rect[0][1]

def point_over_shape(point,verts,loops,outside_point=(-1,-1)) :
    out = Vector(outside_point)
    pt = Vector(point)

    intersections = 0
    for loop in loops :
        for i,p in enumerate(loop) :
            a = Vector(verts[loop[i-1]])
            b = Vector(verts[p])

            if intersect_line_line_2d(pt,out,a,b):
                intersections += 1

    if intersections%2 == 1 : #chek if the nb of intersection is odd
        return True


def border_over_shape(border,verts,loops) :
    for loop in loops :
        for i,p in enumerate(loop) :
            a = Vector(verts[loop[i-1]])
            b = Vector(verts[p])

            for j in range(0,4):
                c = border[j-1]
                d = border[j]
                if intersect_line_line_2d(a,b,c,d):
                    return True

    for point in verts :
        if point_inside_rectangle(point,border) :
            return True

    for point in border :
        if point_over_shape(point,verts,loops) :
            return True



def border_loop(vert,loop) :
    border_edge =[e for e in vert.link_edges if e.is_boundary or e.is_wire]

    if border_edge :
        for edge in border_edge :
            other_vert = edge.other_vert(vert)

            if not other_vert in loop :
                loop.append(other_vert)
                border_loop(other_vert,loop)

        return loop
    else :
        return [vert]


def border_loops(bm,vert_index,loops,vertex_count):
    bm.verts.ensure_lookup_table()

    loop = border_loop(bm.verts[vert_index],[bm.verts[vert_index]])
    if len(loop) >1 :
        loops.append(loop)

    for v in loop :
        vertex_count.remove(v.index)

    if len(vertex_count) :
        border_loops(bm,vertex_count[0],loops,vertex_count)
    return loops


def get_IK_bones(IK_last):
    ik_chain = IK_last.parent_recursive
    ik_len = 0

    #Get IK len :
    for c in IK_last.constraints :
        if c.type == 'IK':
            ik_len = c.chain_count -2
            break

    IK_root = ik_chain[ik_len]

    IK_mid= ik_chain[:ik_len]

    IK_mid.reverse()
    IK_mid.append(IK_last)

    return IK_root,IK_mid

def find_mirror(name) :
    mirror = None
    prop= False

    if name :

        if name.startswith('[')and name.endswith(']'):
            prop = True
            name= name[:-2][2:]

        match={
        'R' : 'L',
        'r' : 'l',
        'L' : 'R',
        'l' : 'r',
        }

        separator=['.','_']

        if name.startswith(tuple(match.keys())):
            if name[1] in separator :
                mirror = match[name[0]]+name[1:]

        if name.endswith(tuple(match.keys())):
            if name[-2] in separator :
                mirror = name[:-1]+match[name[-1]]

        if mirror and prop == True:
            mirror='["%s"]'%mirror

        return mirror

    else :
        return None


def is_shape(ob) :
    shape = False
    if ob.type in('MESH','CURVE','FONT') :
        if ob.UI.shape_type == 'BONE' :
            if ob.UI.name :
                shape = True
        else :
            shape = True
    return shape

def is_over_region(self,context,event) :
    inside = 2 < event.mouse_region_x < context.region.width -2 and \
    2 < event.mouse_region_y < context.region.height -2 and \
    [a for a in context.screen.areas if a.as_pointer()==self.adress] and \
    not context.screen.show_fullscreen

    return inside

def bound_box_center(ob) :
    points = [ob.matrix_world*Vector(p) for p in ob.bound_box]

    x = [v[0] for v in points]
    y = [v[1] for v in points]
    z = [v[2] for v in points]

    return (sum(x) / len(points), sum(y) / len(points),sum(z) / len(points))
