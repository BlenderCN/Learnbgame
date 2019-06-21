import sys, os
import utils
import bpy
import bgl
from OpenGL.GL import*
from OpenGL.GL.framebufferobjects import * 
from ATOM_Types import *
import inspect
import numpy

fs ="""
#version 120

uniform vec3 color;

void main()
{
    gl_FragColor.rgb = color;
}
"""

file = open("C:\\Users\\Matthieu\\Videos\\Blender\\Blend\\ocean\\frag.glsl", "r")
fs = file.read()

class SP_RenderEngine(bpy.types.RenderEngine):
    # These three members are used by blender to set up the
    # RenderEngine; define its internal name, visible name and capabilities.
    bl_idname = "SPARKLE_ENGINE"
    bl_label = "Sparkle Engine"
    bl_use_preview = True
    
    def __init__(self):
        
        #vertex_shader   = bgl.glCreateShader(bgl.GL_VERTEX_SHADER)
        fragment_shader = bgl.glCreateShader(bgl.GL_FRAGMENT_SHADER)
        program         = bgl.glCreateProgram()
        
        #bgl.glShaderSource(vertex_shader,vs)
        bgl.glShaderSource(fragment_shader,fs)
        
        #bgl.glCompileShader(vertex_shader)
        bgl.glCompileShader(fragment_shader)
        
        #utils.attachShader(program, vertex_shader)
        utils.attachShader(program, fragment_shader)
        
        bgl.glLinkProgram(program)
        
        self.program = program
        
    def view_draw(self, context):

        verco = [(1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0)]
        texco = [(1.0, 1.0), (0.0, 1.0), (0.0, 0.0), (1.0, 0.0)]
        
        viewport = bgl.Buffer(bgl.GL_INT, [4])
        
        bgl.glDisable(bgl.GL_DEPTH_TEST)
        	
        bgl.glGetIntegerv(bgl.GL_VIEWPORT, viewport)

        bgl.glViewport(viewport[0], viewport[1], viewport[2], viewport[3])

        bgl.glMatrixMode(bgl.GL_PROJECTION)
        bgl.glPushMatrix()
        bgl.glLoadIdentity()

        bgl.glMatrixMode(bgl.GL_MODELVIEW)
        bgl.glPushMatrix()
        bgl.glLoadIdentity()

        bgl.glUseProgram(self.program)
        wind = glGetUniformLocation(self.program, "u_wind")
        res = glGetUniformLocation(self.program, "u_resolution")
        size = glGetUniformLocation(self.program, "u_size")

        glUniform2fv(wind , 1, [150.0,150.0] )
        glUniform1f(size, 250.0 )
        glUniform1f(res,  512.0 )

        bgl.glBegin(bgl.GL_QUADS)
        for i in range(4):
            bgl.glTexCoord3f(texco[i][0], texco[i][1], 1.0)
            bgl.glVertex2f(verco[i][0], verco[i][1])
        bgl.glEnd()
        
        bgl.glUseProgram(0)

        bgl.glMatrixMode(bgl.GL_PROJECTION)
        bgl.glPopMatrix()

        bgl.glMatrixMode(bgl.GL_MODELVIEW)
        bgl.glPopMatrix()

    def view_update(self, context):
        pass
    
    def draw_viewport(self): 
        pass                     

def unregister():

    klass = utils.checkRegister("Sparkle Engine", SE_CLASS_NAME | SE_LABEL_NAME)

    spaces = []

    if not klass == None:

        if bpy.context.scene.render.engine == "SPARKLE_ENGINE":
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    for space in area.spaces:
                        if space.type == "VIEW_3D":
                            if space.viewport_shade == "RENDERED":
                                spaces.append(space)
                                space.viewport_shade = "SOLID"
   
        bpy.utils.unregister_class(klass)

        for space in spaces:
            space.viewport_shade = "RENDERED"

def register():

    bpy.utils.register_class(SP_RenderEngine)


