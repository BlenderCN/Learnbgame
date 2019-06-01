'''
Created on Oct 10, 2015

@author: Patrick

#TODO, replaced with CGCoookie AddonPro library
'''
import bgl
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_vector_3d, region_2d_to_location_3d, region_2d_to_origin_3d
##############  3d Drawing Utilities #################
##### To be added to post_vew handler ################


def draw3d_polyline(context, points, color, thickness, LINE_TYPE):
    if LINE_TYPE == "GL_LINE_STIPPLE":
        bgl.glLineStipple(4, 0x5555)  #play with this later
        bgl.glEnable(bgl.GL_LINE_STIPPLE)  
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(*color)
    bgl.glLineWidth(thickness)
    bgl.glDepthRange(0.0, 0.997)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for coord in points: bgl.glVertex3f(*coord)
    bgl.glEnd()
    bgl.glLineWidth(1)
    if LINE_TYPE == "GL_LINE_STIPPLE":
        bgl.glDisable(bgl.GL_LINE_STIPPLE)
        bgl.glEnable(bgl.GL_BLEND)  # back to uninterrupted lines  


def draw3d_closed_polylines(context, lpoints, color, thickness, LINE_TYPE):
    lpoints = list(lpoints)
    if LINE_TYPE == "GL_LINE_STIPPLE":
        bgl.glLineStipple(4, 0x5555)  #play with this later
        bgl.glEnable(bgl.GL_LINE_STIPPLE)  
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineWidth(thickness)
    bgl.glDepthRange(0.0, 0.997)
    bgl.glColor4f(*color)
    for points in lpoints:
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for coord in points:
            bgl.glVertex3f(*coord)
        bgl.glVertex3f(*points[0])
        bgl.glEnd()
    #if settings.symmetry_plane == 'x':
    #    bgl.glColor4f(*color_mirror)
    #    for points in lpoints:
    #        bgl.glBegin(bgl.GL_LINE_STRIP)
    #        for coord in points:
    #            bgl.glVertex3f(-coord.x, coord.y, coord.z)
    #        bgl.glVertex3f(-points[0].x, points[0].y, points[0].z)
    #        bgl.glEnd()
        
    bgl.glLineWidth(1)
    if LINE_TYPE == "GL_LINE_STIPPLE":
        bgl.glDisable(bgl.GL_LINE_STIPPLE)
        bgl.glEnable(bgl.GL_BLEND)  # back to uninterrupted lines  

def draw3d_quad(context, points, color):
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glDepthRange(0.0, 0.999)
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glColor4f(*color)
    for coord in points:
        bgl.glVertex3f(*coord)
    
    #if settings.symmetry_plane == 'x':
    #    bgl.glColor4f(*color_mirror)
    #    for coord in points:
    #        bgl.glVertex3f(-coord.x,coord.y,coord.z)
    bgl.glEnd()


def draw3d_quads(context, lpoints, color): #, color_mirror):
    lpoints = list(lpoints)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glDepthRange(0.0, 0.999)
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glColor4f(*color)
    for points in lpoints:
        for coord in points:
            bgl.glVertex3f(*coord)
    
    #TODO, generic mirror pt and plane
    #if settings.symmetry_plane == 'x':
    #    bgl.glColor4f(*color_mirror)
    #    for points in lpoints:
    #        for coord in points:
    #            bgl.glVertex3f(-coord.x,coord.y,coord.z)
    bgl.glEnd()

def draw3d_points(context, points, color, size):
    bgl.glColor4f(*color)
    bgl.glPointSize(size)
    bgl.glDepthRange(0.0, 0.997)
    bgl.glBegin(bgl.GL_POINTS)
    for coord in points: bgl.glVertex3f(*coord)
    bgl.glEnd()
    bgl.glPointSize(1.0)


##############  2d Drawing Utilities #################
##### To be added to post_pixel handler ################
def draw_3d_points(context, points, size, color = (1,0,0,1)):
    region = context.region
    rv3d = context.space_data.region_3d

    bgl.glEnable(bgl.GL_POINT_SMOOTH)
    bgl.glPointSize(size)
    # bgl.glEnable(bgl.GL_BLEND)
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

    bgl.glBegin(bgl.GL_POINTS)
    # draw red
    bgl.glColor4f(*color)
    for coord in points:
        vector3d = (coord.x, coord.y, coord.z)
        vector2d = location_3d_to_region_2d(region, rv3d, vector3d)
        if vector2d and vector3d:
            bgl.glVertex2f(*vector2d)
    bgl.glEnd()

    bgl.glDisable(bgl.GL_POINT_SMOOTH)
    bgl.glDisable(bgl.GL_POINTS)
    return

def draw_polyline_from_3dpoints(context, points_3d, color, thickness, LINE_TYPE):
    '''
    a simple way to draw a line
    slow...becuase it must convert to screen every time
    but allows you to pan and zoom around

    args:
        points_3d: a list of tuples representing x,y SCREEN coordinate eg [(10,30),(11,31),...]
        color: tuple (r,g,b,a)
        thickness: integer? maybe a float
        LINE_TYPE:  eg...bgl.GL_LINE_STIPPLE or
    '''

    points = [location_3d_to_region_2d(context.region, context.space_data.region_3d, loc) for loc in points_3d]

    if LINE_TYPE == "GL_LINE_STIPPLE":
        bgl.glLineStipple(4, 0x5555)  #play with this later
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
    bgl.glEnable(bgl.GL_BLEND)

    bgl.glColor4f(*color)
    bgl.glLineWidth(thickness)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for coord in points:
        if coord:
            bgl.glVertex2f(*coord)

    bgl.glEnd()

    if LINE_TYPE == "GL_LINE_STIPPLE":
        bgl.glDisable(bgl.GL_LINE_STIPPLE)
        bgl.glEnable(bgl.GL_BLEND)  # back to uninterupted lines
        bgl.glLineWidth(1)
    return

def draw_polyline_from_points(context, points, color, thickness, LINE_TYPE):
    '''
    a simple way to draw a line
    args:
        points: a list of tuples representing x,y SCREEN coordinate eg [(10,30),(11,31),...]
        color: tuple (r,g,b,a)
        thickness: integer? maybe a float
        LINE_TYPE:  eg...bgl.GL_LINE_STIPPLE or
    '''

    if LINE_TYPE == "GL_LINE_STIPPLE":
        bgl.glLineStipple(4, 0x5555)  #play with this later
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
    bgl.glEnable(bgl.GL_BLEND)

    current_width = bgl.GL_LINE_WIDTH
    bgl.glColor4f(*color)
    bgl.glLineWidth(thickness)
    bgl.glBegin(bgl.GL_LINE_STRIP)

    for coord in points:
        bgl.glVertex2f(*coord)

    bgl.glEnd()
    bgl.glLineWidth(1)
    if LINE_TYPE == "GL_LINE_STIPPLE":
        bgl.glDisable(bgl.GL_LINE_STIPPLE)
        bgl.glEnable(bgl.GL_BLEND)  # back to uninterupted lines

    return
