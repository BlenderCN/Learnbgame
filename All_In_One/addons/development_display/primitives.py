import bpy, blf
import numpy as np
from mathutils import Vector, Matrix
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bgl import *
glEnable(GL_BLEND_DST_ALPHA)
glShadeModel(GL_FLAT)

### Text Primitive
def draw_text(text, vec, offset=(5, -5)):
    context = bpy.context
    region = context.region
    region3d = context.space_data.region_3d
    settings = bpy.context.window_manager.display_settings
    
    if not type(text) == str:
        text = str(text)
    
    font_id=0
    if len(vec) == 3:
        vec = location_3d_to_region_2d(region, region3d, vec)

    if len(settings.color_text) == 3:
        glColor3f(*settings.color_text)
    elif len(settings.color_text) == 4:
        glColor4f(*settings.color_text)
        
    blf.position(font_id, vec.x + offset[0], vec.y + offset[1], 1)
    blf.size(font_id, 11, 72)
    blf.draw(font_id, text)


### GL PRIMITIVES

def draw_vert(v1, width=2.0, color=(1,0,0)):
    if len(color) == 3:
        glColor3f(*color)
    elif len(color) == 4:
        glColor4f(*color)
    
    glBegin(GL_POINTS)
    glPointSize(width)
    if len(v1) == 3:
        glVertex3f(*v1)
    elif len(v1) == 2:
        glVertex2f(*v1)
    glPointSize(1)
    glEnd()

def draw_verts(verts, width=2.0, color=(1,0,0)):
    if len(color) == 3:
        glColor3f(*color)
    elif len(color) == 4:
        glColor4f(*color)
    
    glBegin(GL_POINTS)
    glPointSize(width)
    if all(len(v)==3 for v in verts):
        for v in verts:
            glVertex3f(*v)
    else:
        for v in verts:
            glVertex2f(*v)
    glPointSize(1)
    glEnd()


def draw_edge(v1, v2, width=1, color=(1,1,1)):
    if len(color) == 3:
        glColor3f(*color)
    elif len(color) == 4:
        glColor4f(*color)
        
    glLineWidth(width)
    glBegin(GL_LINE_STRIP)
    if (len(v1) == 3 and len(v2) == 3):
        glVertex3f(*v1)
        glVertex3f(*v2)
    elif (len(v1) == 2 and len(v2) == 2):
        glVertex2f(*v1)
        glVertex2f(*v2)
    glEnd()
    glLineWidth(1)

def draw_edge_stippled(v1,v2,width=1,color=(0.5, 0.5, 0.5)):
    if len(color) == 3:
        glColor3f(*color)
    elif len(color) == 4:
        glColor4f(*color)

    glLineWidth(width)
    glLineStipple(1, 0xAAAA)
    glEnable(GL_LINE_STIPPLE)
    glBegin(GL_LINES)
    if (len(v1) == 3 and len(v2) == 3):
        glVertex3f(*v1)
        glVertex3f(*v2)
    elif (len(v1) == 2 and len(v2) == 2):
        glVertex2f(*v1)
        glVertex2f(*v2)
    glEnd()
    glLineWidth(1)
    glDisable(GL_LINE_STIPPLE)

def draw_point_chain(verts, width=1, color=(1,1,1)):
    if len(color) == 3:
        glColor3f(*color)
    elif len(color) == 4:
        glColor4f(*color)
    
    glLineWidth(width)
    glBegin(GL_LINE_STRIP)
    if all(len(v)==3 for v in verts):
        for v in verts:
            glVertex3f(*v)
    else:
        for v in verts:
            glVertex2f(*v)
    glEnd()
    glLineWidth(1)
    
def draw_face(verts, color=(1,1,1)):
    if len(color) == 3:
        glColor3f(*color)
    elif len(color) == 4:
        glColor4f(*color)

    glBegin(GL_POLYGON)
    if all(len(v)==3 for v in verts):
        for v in verts:
            glVertex3f(*v)
    else:
        for v in verts:
            glVertex2f(*v)
    glEnd()

def draw_matrix(mat):
    zero = Vector((0.0, 0.0, 0.0))
    x_p = Vector((1.0, 0.0, 0.0))
    x_n = Vector((-1.0, 0.0, 0.0))
    y_p = Vector((0.0, 1.0, 0.0))
    y_n = Vector((0.0, -1.0, 0.0))
    z_p = Vector((0.0, 0.0, 1.0))
    z_n = Vector((0.0, 0.0, -1.0))
    zero_tx = mat * zero
    
    # x
    draw_edge(zero_tx, mat * x_p, width=2, color=(1.0, 0.2, 0.2))
    draw_edge(zero_tx, mat * x_n, width=2, color=(0.6, 0.0, 0.0))
    
    # y
    draw_edge(zero_tx, mat * y_p, width=2, color=(0.2, 1.0, 0.2))
    draw_edge(zero_tx, mat * y_n, width=2, color=(0.0, 0.6, 0.0))
    
    # z
    draw_edge(zero_tx, mat * z_p, width=2, color=(0.2, 0.2, 1.0))
    draw_edge(zero_tx, mat * z_n, width=2, color=(0.0, 0.0, 0.6))
    
    # bounding box
    bb = [Vector() for i in range(8)]
    i = 0
    for x in (-1.0, 1.0):
        for y in (-1.0, 1.0):
            for z in (-1.0, 1.0):
                bb[i][:] = x, y, z
                bb[i] = mat * bb[i]
                i += 1

    bb_edges=[  (0,1), (1,3), (3,2), (2,0),
                (0,4), (4,5), (5,7), (7,6),
                (6,4), (1,5), (2,6), (3,7)]

    glColor4f(1.0, 1.0, 1.0, 0.5)
    for e in bb_edges:
        draw_edge_stippled(bb[e[0]], bb[e[1]])


