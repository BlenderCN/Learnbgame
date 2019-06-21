'''
Copyright (C) 2016 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
    
import bpy
from mathutils import Vector, Matrix, Euler, Quaternion
import math
import bgl
import blf
import bpy_extras
from . functions import *
from .operators.sketch_operator import get_zoom

def restore_opengl_defaults():
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

def get_grid_mat(self,context):
    wm = context.window_manager
    asset_sketcher = wm.asset_sketcher
    mat_rot = Matrix.Rotation(math.radians(90.0),4,'X')
    mat_trans = Matrix.Translation(self.projected_mouse)
    mat = mat_trans * mat_rot
    
    if asset_sketcher.sketch_plane_axis == "XY":
        mat_rot = Matrix.Rotation(math.radians(0),4,'X')
        mat_trans = Matrix.Translation(self.projected_mouse)
        mat = mat_trans * mat_rot
    if asset_sketcher.sketch_plane_axis == "YZ":
        mat_rot = Matrix.Rotation(math.radians(90.0),4,'Y')
        mat_trans = Matrix.Translation(self.projected_mouse)
        mat = mat_trans * mat_rot
    elif asset_sketcher.sketch_plane_axis == "XZ":
        mat_rot = Matrix.Rotation(math.radians(90.0),4,'X')
        mat_trans = Matrix.Translation(self.projected_mouse)
        mat = mat_trans * mat_rot
    return mat    
    
def draw_brush_cursor(self,context,event):
    wm = context.window_manager
    asset_sketcher = wm.asset_sketcher
    region = bpy.context.region
    rv3d = bpy.context.space_data.region_3d
    

    self.circle_color = [0.102758, 0.643065, 1.000000, 1.000000]
    if event.ctrl and not self.f_key and event.type != "MIDDLEMOUSE":
        self.circle_color = [1.000000, 0.202489, 0.401234, 1.000000]
    elif self.f_key:
        self.circle_color = [1.0, 1.0, 1.0, .7]   
    
    ### draw brush
    if wm.asset_sketcher.sketch_mode in ["SCALE","PAINT"]:
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(self.circle_color[0],self.circle_color[1],self.circle_color[2],self.circle_color[3])
        bgl.glLineWidth(2)
        
        ### draw brush circle
        bgl.glBegin(bgl.GL_LINE_STRIP)
        steps = 32
        angle = (2*math.pi)/steps
        
        if self.brush_stroke:
            radius = (wm.asset_sketcher.brush_size/2) * self.pen_pressure
        else:
            radius = (wm.asset_sketcher.brush_size/2)    
        
        ### calc smooth visual normal interpolation
       
        rot_mat = self.ground_normal_current.rotation_difference(Vector((0,0,1))).to_matrix().to_3x3()
        
        for i in range(steps+1):
            x = self.projected_mouse[0] + radius*math.cos(angle*i)
            y = self.projected_mouse[1] + radius*math.sin(angle*i)
            z = self.projected_mouse[2]
            
            p = Vector((x,y,z))
            
            ### rotate circle to match the ground normal
            p -= self.projected_mouse
            p = p *  rot_mat
            p += self.projected_mouse
            
            ### convert 3d vectors to 2d screen 
            p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
            if p_2d != None:
                bgl.glVertex2f(p_2d[0],p_2d[1])
            #bgl.glVertex3f(p[0],p[1],p[2])
        bgl.glEnd()
            
        
        bgl.glBegin(bgl.GL_LINE_STRIP)
        
        p1 = self.projected_mouse
        p2 = self.projected_mouse + (self.ground_normal_current * get_zoom(self,context)*.05)
        p1_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p1)
        p2_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p2)
        if p1_2d != None and p2_2d != None:
            bgl.glVertex2f(p1_2d[0],p1_2d[1])
            bgl.glVertex2f(p2_2d[0],p2_2d[1])
        
        bgl.glEnd()
        
    
    elif wm.asset_sketcher.sketch_mode == "GRID":
        
        
        mat = get_grid_mat(self,context)
        
        ### draw grid cursor
        
        bgl.glColor4f(self.circle_color[0],self.circle_color[1],self.circle_color[2],self.circle_color[3])
        bgl.glLineWidth(2)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        
        ### draw tile square    
        p = self.projected_mouse + (Vector((asset_sketcher.sketch_grid_size/2,asset_sketcher.sketch_grid_size/2,0)) * mat)
        p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
        if p_2d != None:
            bgl.glVertex2f(p_2d[0],p_2d[1])
        
        p = self.projected_mouse + (Vector((asset_sketcher.sketch_grid_size/2,-asset_sketcher.sketch_grid_size/2,0)) * mat)
        p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
        if p_2d != None:
            bgl.glVertex2f(p_2d[0],p_2d[1])
        
        p = self.projected_mouse + (Vector((-asset_sketcher.sketch_grid_size/2,-asset_sketcher.sketch_grid_size/2,0)) * mat)
        p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
        if p_2d != None:
            bgl.glVertex2f(p_2d[0],p_2d[1])
        
        p = self.projected_mouse + (Vector((-asset_sketcher.sketch_grid_size/2,asset_sketcher.sketch_grid_size/2,0)) * mat)
        p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
        if p_2d != None:
            bgl.glVertex2f(p_2d[0],p_2d[1])
        
        p = self.projected_mouse + (Vector((asset_sketcher.sketch_grid_size/2,asset_sketcher.sketch_grid_size/2,0)) * mat)
        p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
        if p_2d != None:
            bgl.glVertex2f(p_2d[0],p_2d[1])
        bgl.glEnd()
    
    restore_opengl_defaults()    

def draw_scale_line(self,context,event):
    wm = context.window_manager
    region = bpy.context.region
    rv3d = bpy.context.space_data.region_3d
    

    self.circle_color = [0.102758, 0.643065, 1.000000, 1.000000]
    if event.ctrl and not self.f_key and event.type != "MIDDLEMOUSE" and not self.scale_stroke:
        self.circle_color = [1.000000, 0.202489, 0.401234, 1.000000]
    
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(self.circle_color[0],self.circle_color[1],self.circle_color[2],self.circle_color[3])
    bgl.glLineWidth(3)
    
    ### draw line code here
    p1 = self.stroke_start_pos
    p2 = self.stroke_start_pos + (self.stroke_direction*(self.stroke_start_pos - self.mouse_on_plane).length)
    p1_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p1)
    p2_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p2)
    if self.scale_stroke:
        bgl.glBegin(bgl.GL_LINE_STRIP)
        
        if p1_2d != None and p2_2d != None:
            bgl.glVertex2f(p1_2d[0],p1_2d[1])
            bgl.glVertex2f(p2_2d[0],p2_2d[1])
        
        bgl.glEnd()
    
    bgl.glPointSize(5)
    p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.projected_mouse)
    if self.scale_stroke:
        bgl.glPointSize(14)
        p = p2_2d
    bgl.glBegin(bgl.GL_POINTS)
    if p != None:
        bgl.glVertex2f(p[0],p[1])
    bgl.glEnd()
    ###
    
    restore_opengl_defaults()
    
def draw_text(self,context,event):  
    wm = context.window_manager
    region = bpy.context.region
    rv3d = bpy.context.space_data.region_3d
    

    self.circle_color = [0.102758, 0.643065, 1.000000, 1.000000]
    if event.ctrl and not self.f_key:
        self.circle_color = [1.000000, 0.202489, 0.401234, 1.000000]
    elif self.f_key:
        self.circle_color = [1.0, 1.0, 1.0, .7]   
          
    ### draw brush size text
    
    if self.f_key or event.alt or self.f_key_shift or self.scale_stroke:
        bgl.glColor4f(1.0, 1.0, 1.0, .7)
        text_pos = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.projected_mouse)
        if text_pos != None:
            blf.position(0, text_pos[0]-30, text_pos[1]+10, 0)
        blf.size(0, 18, 72)
            

    if self.f_key:
        
        blf.draw(0, "Size: " + str(round(wm.asset_sketcher.brush_size,2)))
    elif self.f_key_shift:
        blf.draw(0, "Density: " + str(wm.asset_sketcher.brush_density))    
    elif event.alt:
        blf.draw(0, str(self.picked_asset_name))
    if self.scale_stroke:
        vec = Vector((0,1,0))# * self.ground_normal_mat
        angle = vec.rotation_difference(self.stroke_direction.normalized()).to_euler()
        
        #angle = self.stroke_direction.normalized().rotation_difference(Vector((0,1,0))).to_euler()
        
        
        text1 = "Scale: " + str(round(self.stroke_length,2))
        text2 = "Angle: " + str(round(math.degrees(angle[2]),2))
        blf.draw(0, text1)
        #blf.position(0, text_pos[0]-30, text_pos[1]+10+20, 0)
        #blf.draw(0, text2)
    
    restore_opengl_defaults()


def draw_grid(self,context,event):
    wm = context.window_manager
    asset_sketcher = wm.asset_sketcher
    region = bpy.context.region
    rv3d = bpy.context.space_data.region_3d
    
    self.circle_color = [0.102758, 0.643065, 1.000000, 1.000000]
    if event.ctrl and event.type != "MIDDLEMOUSE":
        self.circle_color = [1.000000, 0.202489, 0.401234, 1.000000]
    
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(self.circle_color[0],self.circle_color[1],self.circle_color[2],self.circle_color[3])
    
    ### draw brush center point
    bgl.glPointSize(5)
    bgl.glColor4f(self.circle_color[0],self.circle_color[1],self.circle_color[2],.5)
    bgl.glBegin(bgl.GL_POINTS)
    p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.projected_mouse)
    if p != None:
        bgl.glVertex2f(p[0],p[1])
    bgl.glEnd()
    
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(self.circle_color[0],self.circle_color[1],self.circle_color[2],self.circle_color[3])
    bgl.glLineWidth(2)    
    
    ### Plane XY
    mat = get_grid_mat(self,context)
    
    bgl.glBegin(bgl.GL_LINE_STRIP)      
    ### draw tile grid
    grid_size = 18
    for i in range(grid_size):
        
        self.circle_color = [0.102758, 0.643065, 1.000000, 1.000000]
        bgl.glColor4f(self.circle_color[0],self.circle_color[1],self.circle_color[2],.4)
        bgl.glLineWidth(1)
        
        
        offset = Vector(((grid_size/2)-.5,(grid_size/2)-.5,0))*asset_sketcher.sketch_grid_size
        
        bgl.glBegin(bgl.GL_LINE_STRIP)
        p = self.projected_mouse + ((Vector((0,i*asset_sketcher.sketch_grid_size,0)) -offset)* mat)
        p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
        bgl.glVertex3f(p[0],p[1],p[2])
        
        p = self.projected_mouse + ((Vector(((grid_size-1)*asset_sketcher.sketch_grid_size,i*asset_sketcher.sketch_grid_size,0)) -offset)* mat)
        p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
        bgl.glVertex3f(p[0],p[1],p[2])
        bgl.glEnd()
        
        bgl.glBegin(bgl.GL_LINE_STRIP)
        p = self.projected_mouse + ((Vector((i*asset_sketcher.sketch_grid_size,0,0)) -offset)* mat)
        p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
        bgl.glVertex3f(p[0],p[1],p[2])
        
        p = self.projected_mouse + ((Vector((i*asset_sketcher.sketch_grid_size,(grid_size-1)*asset_sketcher.sketch_grid_size,0))-offset) * mat)
        p_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
        bgl.glVertex3f(p[0],p[1],p[2])
        bgl.glEnd()  
    
    restore_opengl_defaults()