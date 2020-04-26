# ------------------------------------------------------------------------------
# LICENSE
# ------------------------------------------------------------------------------
# Render+ - Blender addon
# (c) Copyright Diego Garcia Gangl (januz) - 2014, 2015
# <diego@sinestesia.co>
# ------------------------------------------------------------------------------
# This file is part of Render+
#
# Render+ is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ------------------------------------------------------------------------------


import bpy

from bpy.props import BoolProperty

from . import ui

class RP_OT_OpenGL_ShowSettings(bpy.types.Operator):
    """ Toggle OpenGL settings """

    bl_idname = 'renderplus.opengl_show_settings'
    bl_label = 'Show Settings'

    def execute(self, context):
        
        ui.show_opengl_settings = not ui.show_opengl_settings
        return {'FINISHED'}


class RP_OT_OpenGL_Render(bpy.types.Operator):
    """ Render using OpenGL  """

    bl_idname = 'renderplus.opengl_render'
    bl_label = 'Render using OpenGL'
    
    animation = BoolProperty(default=False)

    def execute(self, context):
        
        settings = context.scene.renderplus
        viewport = settings.opengl_use_viewport
        
        transparent = settings.opengl_transparent
        percentage = settings.opengl_percentage
        old_percentage = context.scene.render.resolution_percentage
        old_transparent = context.scene.render.alpha_mode 
        
        context.scene.render.resolution_percentage = percentage   
        
        if transparent:
            context.scene.render.alpha_mode = 'TRANSPARENT'
        
        bpy.ops.render.opengl( animation = self.animation, 
                               view_context = viewport,
                               write_still = settings.autosave )
                               
        context.scene.render.resolution_percentage = old_percentage   
        context.scene.render.alpha_mode = old_transparent
        
        self.report({'INFO'}, 'OpenGL render complete')
        return {'FINISHED'}
