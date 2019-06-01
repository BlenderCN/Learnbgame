import bpy, blf
from .primitives import *
from bgl import *
from mathutils import Vector
import numpy as np

class Plot:
    def __init__(self, X, Y, name=''):
        self.points = [Vector((x, y)) for x,y in zip(X, Y)]
        self.X = np.array(X)
        self.Y = np.array(Y)
        self.scale = Vector((100,100))
        self.name = name

    def draw(self):
        settings = bpy.context.window_manager.display_settings
        location = Vector(settings.plot_co)
        

        glEnable(GL_BLEND)
        
        #x-axis
        x = self.X[0]
        if x > 0: x = 0
        x *= self.scale.x * settings.plot_scale.x
        xbeg = Vector((x, 0)) + location
        
        x = self.X[-1] * self.scale.x
        if x < 0: x = 0
        x *= settings.plot_scale.x
        xend = Vector((x, 0)) + location
        
        draw_edge(xbeg, xend, width=2, color=(1, 0.5, 0.5))

        #yaxis
        y = np.min(self.Y)
        if y > 0: y = 0
        y *= self.scale.y * settings.plot_scale.y
        ybeg = Vector((0, y)) + location
        
        y = np.max(self.Y) * self.scale.y
        if y < 0: y = 0
        y *= settings.plot_scale.y
        yend = Vector((0, y)) + location
        
        draw_edge(ybeg, yend, width=2, color=(0.5, 1, 0.5))
        
        points = [Vector(((p.x*self.scale.x*settings.plot_scale.x,
                          p.y*self.scale.y*settings.plot_scale.y)))+location
                          for p in self.points]

        #plot-line
        draw_point_chain(points, color=settings.color_point_chains)

        #plot-points
        draw_verts(points, width=2, color=settings.color_points)

        #text
        font_id=0
        def text(txt, vec):
            blf.position(font_id, vec.x, vec.y, 1)
            blf.size(font_id, 11, 72)
            blf.draw(font_id, txt)
            
        if len(settings.color_text) == 3:
            glColor3f(*settings.color_text)
        elif len(settings.color_text) == 4:
            glColor4f(*settings.color_text)
        
        offsety = Vector((0,-14))
        offsetx = Vector((7,0))
        text(str(round(self.X[-1],3)), xend+offsety)
        text(str(round(self.Y.max(),3)), yend+offsetx)
        if self.X[0] < 0:
            text(str(round(self.X[0],3)), xbeg+offsety)
        if self.Y[0] < 0:
            text(str(round(self.Y.min(),3)), ybeg+offsetx)
        
        text('Plot "%s"'%self.name, points[-1]+offsetx)
