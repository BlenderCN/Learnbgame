# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
'''
Created on Nov 26, 2012

@author: Patrick Moore
'''
import bpy
import bgl
import blf
import math
import time
import os
import random

from math import fmod
from mathutils.geometry import intersect_line_line_2d
from mathutils import Vector, Matrix
from bpy_extras.image_utils import load_image


def scale_vec_mult(a,b):
    '''
    performs item wise multiplication return Vec(a0*b0,a1*b1)
    '''
    out = Vector(a[0]*b[0],a[1]*b[1])
    return out

#http://stackoverflow.com/questions/2150108/efficient-way-to-shift-a-list-in-python
def list_shift(seq, n):
    n = n % len(seq)
    return seq[n:] + seq[:n]

#generates a quad scaled, rotated and translated to be passsed to glVertex2f
def make_quad(width, height, x, y ,ang):
    '''
    args: 
    width, height, x, y, float
    ang: float in radians
    return: list of Vectors
    '''
    
    a = width/2
    b = height/2
    #primitive
    p0 = Vector((-a,-b))
    p1 = Vector((-a, b))
    p2 = Vector((a, b))
    p3 = Vector((a,-b))
    
    #put them in a list
    verts = [p0,p1,p2,p3]
    
    #rotation
    rmatrix = Matrix.Rotation(ang,2)

    #rotate them and tranlsate
    for i in range(0,len(verts)):
        vert = rmatrix*verts[i] + Vector((x,y))
        verts[i]=vert
    
    return verts

def quad_size_from_circle(r,n,spacer = 0):
    '''
    args-
    r: size of circle
    n: number of pie segments
    space: buffer space between segments in radians.Eg, 2 degrees is ~.035 radians
    '''
    #total arc available for each slice
    arc = 2*math.pi/n - spacer
    
    #length of arc..and this is why we use radians ladies and gents = arc*r
    arc_len = arc * r
    
    #now some fuzzy math here....make the diag of the quad = arcleng
    #a good approximation when arc is small, bad when arc is large
    #trig...a^2 + b^2 = c^2  => square a = b so 2a^2 = c^2
    size = arc_len/math.pow(2,.5)
    
    return size
    

def view3d_get_size_and_mid(context):
    region = context.region
    rv3d = context.space_data.region_3d

    width = region.width
    height = region.height
    mid = Vector((width/2,height/2))
    aspect = Vector((width,height))

    return [aspect, mid]

def menu_location_filter(context,x,y,safety):
    region = context.region
    rv3d = context.space_data.region_3d

    width = region.width
    height = region.height
    
    xmax = width - safety
    ymax = height - safety
    
    if x > xmax:
        x = xmax
    
    elif x < safety:
        x = safety
    
    if y > ymax:
        y = ymax
    
    elif y < safety:
        y = safety
    
    return (x,y)
    
def image_quad(img,color,verts):
    img.gl_load(bgl.GL_NEAREST, bgl.GL_NEAREST)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, img.bindcode)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)
    bgl.glEnable(bgl.GL_TEXTURE_2D)
    bgl.glEnable(bgl.GL_BLEND)
    #bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
    bgl.glColor4f(color[0], color[1], color[2], color[3])
    bgl.glBegin(bgl.GL_QUADS)
    #http://h30097.www3.hp.com/docs/base_doc/DOCUMENTATION/V51B_HTML/MAN/MAN3/2025____.HTM
    bgl.glTexCoord2f(0,0)
    bgl.glVertex2f(verts[0][0],verts[0][1])
    bgl.glTexCoord2f(0,1)
    bgl.glVertex2f(verts[1][0],verts[1][1])
    bgl.glTexCoord2f(1,1)
    bgl.glVertex2f(verts[2][0],verts[2][1])
    bgl.glTexCoord2f(1,0)
    bgl.glVertex2f(verts[3][0],verts[3][1])
    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_TEXTURE_2D)
    
def icons_to_blend_data(icondir, filext = ".png", overwite = False):
    '''
    TODO: Add suport fo all data that blender supports
    '''
    icon_files = [fi for fi in os.listdir(icondir) if fi.endswith(filext) ]
    
    for fname in icon_files:
        fpath = os.path.join(icondir,fname)
        if fname not in bpy.data.images:
            load_image(fpath, dirname='', place_holder=False, recursive=False, ncase_cmp=True, convert_callback=None, verbose=False)
        elif overwite:
            image = bpy.data.images[fname]
            bpy.data.images.remove(image)
            load_image(fpath, dirname='', place_holder=False, recursive=False, ncase_cmp=True, convert_callback=None, verbose=False)
    
def random_icon(icondir, filext = ".png"):
    '''
    assume all icons in icondir are loaded
    pics a random icon from the directory and returns it's name
    '''
    icon_files = [fi for fi in os.listdir(icondir) if fi.endswith(filext) ]
    index = random.randint(0,len(icon_files)-1)
    
    return icon_files[index] 
    
def radial_locations(r,n,x,y,offset = 0):
    '''
    r: radius of circle
    n: number of divisions
    x: x coord of center
    y: y cood or center
    offset: any angular offset
    '''
    #populate the list of vectors
    locations = [Vector((0,0))]*n
      
    for i in range(0,n):
        theta = offset + i * 2 * math.pi / n
        locx = x + r * math.cos(theta)
        locy = y + r * math.sin(theta)
        locations[i]=Vector((locx,locy))
   
    return locations

def sub_arc_loactions(r,arc,n,x,y,offset = 0):
    print("in development come back later")

def outside_loop(loop):
    '''
    args:
    loop: list of 
       type-Vector or type-tuple
    returns: 
       outside = a location outside bound of loop 
       type-tuple
    '''
       
    xs = [v[0] for v in loop]
    ys = [v[1] for v in loop]
    
    maxx = max(xs)
    maxy = max(ys)    
    bound = (1.1*maxx, 1.1*maxy)
    return bound

def point_inside_loop(loop, point):
    '''
    args:
    loop: list of vertices representing loop
        type-tuple or type-Vector
    point: location of point to be tested
        type-tuple or type-Vector
    
    return:
        True if point is inside loop
    '''    
    #test arguments type
    ptype = str(type(point))
    ltype = str(type(loop[0]))
    nverts = len(loop)
           
    if 'Vector' not in ptype:
        point = Vector(point)
        
    if 'Vector' not in ltype:
        for i in range(0,nverts):
            loop[i] = Vector(loop[i])
        
    #find a point outside the loop and count intersections
    out = Vector(outside_loop(loop))
    intersections = 0
    for i in range(0,nverts):
        a = Vector(loop[i-1])
        b = Vector(loop[i])
        if intersect_line_line_2d(point,out,a,b):
            intersections += 1
    
    inside = False
    if fmod(intersections,2):
        inside = True
    
    return inside
    
def pi_slice(x,y,r1,r2,thta1,thta2,res,t_fan = False):
    '''
    args: 
    x,y - center coordinate
    r1, r2 inner and outer radius
    thta1: beginning of the slice  0 = to the right
    thta2:  end of the slice (ccw direction)
    '''
    points = [[0,0]]*(2*res + 2)  #the two arcs

    for i in range(0,res+1):
        diff = math.fmod(thta2-thta1 + 2*math.pi, 2*math.pi)
        x1 = math.cos(thta1 + i*diff/res) 
        y1 = math.sin(thta1 + i*diff/res)
    
        points[i]=[r1*x1 + x,r1*y1 + y]
        points[(2*res) - i+1] =[x1*r2 + x, y1*r2 + y]
        
    if t_fan: #need to shift order so GL_TRIANGLE_FAN can draw concavity
        new_0 = math.floor(1.5*(2*res+2))
        points = list_shift(points, new_0)
            
    return(points)
 
def make_round_box(minx, miny, maxx, maxy, rad):
       
        vec0 = [[0.195, 0.02],
               [0.383, 0.067],
               [0.55, 0.169],
               [0.707, 0.293],
               [0.831, 0.45],
               [0.924, 0.617],
               [0.98, 0.805]]
        
        #cache so we only scale the corners once
        vec = [[0,0]]*len(vec0)
        for i in range(0,len(vec0)):
            vec[i] = [vec0[i][0]*rad, vec0[i][1]*rad]
            
        verts = [[0,0]]*(9*4)
        
        # start with corner right-bottom
        verts[0] = [maxx-rad,miny]
        for i in range(1,8):
            verts[i]= [maxx - rad + vec[i-1][0], miny + vec[i-1][1]] #done
        verts[8] = [maxx, miny + rad]   #done
               
        #corner right-top    
        verts[9] = [maxx, maxy - rad]
        for i in range(10,17):
            verts[i]= [maxx - vec[i-10][1], maxy - rad + vec[i-10][0]]
        verts[17] = [maxx-rad, maxy]
        
        #corver left top
        verts[18] = [minx + rad, maxy]
        for i in range(19,26):
            verts[i]= [minx + rad - vec[i-19][0], maxy - vec[i-19][1]] #done
        verts[26] = [minx, maxy - rad]
        
        #corner left bottom    
        verts[27] = [minx, miny+rad]
        for i in range(28,35):
            verts[i]= [minx + vec[i-28][1], miny + rad - vec[i-28][0]]    #done
        verts[35]=[minx + rad, miny]
        
        
        return verts
    
def make_round_slider(minx, miny, maxx, maxy, pct, rad):
       
        vec0 = [[0.195, 0.02],
               [0.383, 0.067],
               [0.55, 0.169],
               [0.707, 0.293],
               [0.831, 0.45],
               [0.924, 0.617],
               [0.98, 0.805]]
        
        #cache so we only scale the corners once
        vec = [[0,0]]*len(vec0)
        for i in range(0,len(vec0)):
            vec[i] = [vec0[i][0]*rad, vec0[i][1]*rad]
        
        #pct is calced by area between rounded corners
        middle = minx + rad + (maxx-minx-2*rad)*pct
        
        
        right_side = [[0,0]]*20
            
        
        # start with corner right-bottom
        right_side[0] = [maxx-rad,miny]
        for i in range(1,8):
            right_side[i]= [maxx - rad + vec[i-1][0], miny + vec[i-1][1]] #done
        right_side[8] = [maxx, miny + rad]   #done
               
        #corner right-top    
        right_side[9] = [maxx, maxy - rad]
        for i in range(10,17):
            right_side[i]= [maxx - vec[i-10][1], maxy - rad + vec[i-10][0]]
        right_side[17] = [maxx-rad, maxy]
        
        right_side[18] = [middle, maxy]
        right_side[19] = [middle, miny]
        
        #Now do Left Side
        left_side = [[0,0]]*20
        
        #corver left top
        left_side[0] = [minx + rad, maxy]
        for i in range(1,8):
            left_side[i]= [minx + rad - vec[i-1][0], maxy - vec[i-1][1]] #done
        left_side[8] = [minx, maxy - rad]
        
        #corner left bottom    
        left_side[9] = [minx, miny+rad]
        for i in range(10,17):
            left_side[i]= [minx + vec[i-10][1], miny + rad - vec[i-10][0]]    #done
        left_side[17]=[minx + rad, miny]
        
        left_side[18] = [middle, miny]
        left_side[19] = [middle, maxy]
        
        return [left_side, right_side]
    
def callback_register(self, context):
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.menu.draw, (self, context), 'WINDOW', 'POST_PIXEL')
        return None
            
def callback_cleanup(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
        return None
       
def draw_outline_or_region(mode, points):
        '''  
        arg: 
        mode - either bgl.GL_POLYGON or bgl.GL_LINE_LOOP
        color - will need to be set beforehand using theme colors. eg
        bgl.glColor4f(self.ri, self.gi, self.bi, self.ai)
        '''
            
        bgl.glBegin(mode)
 
        # start with corner right-bottom
        for i in range(0,len(points)):
            bgl.glVertex2f(points[i][0],points[i][1])
 
        bgl.glEnd()

def register():  
    print('register utils')
def unregister():     
    print('unregister utils')
if __name__ == "__main__":
    register()          
