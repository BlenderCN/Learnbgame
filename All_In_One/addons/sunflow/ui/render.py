# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Version                     2.68
# Exporter Version                    0.0.4
# Created on                          26-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------


import bpy

from bl_ui.properties_render import RenderButtonsPanel
from extensions_framework.ui import property_group_renderer
from .. import SunflowAddon


class SunflowRenderPanel(RenderButtonsPanel, property_group_renderer):
    '''
    Base class for render engine settings panels
    '''
    COMPAT_ENGINES = { 'SUNFLOW_RENDER' }


@SunflowAddon.addon_register_class
class SunflowRender_PT_integrator(SunflowRenderPanel):
    bl_label = "Global Illumination"
    # bl_options = {'DEFAULT_CLOSED'}
    
    display_property_groups = [
        (('scene',), 'sunflow_integrator')
    ]
    

@SunflowAddon.addon_register_class
class SunflowRender_PT_antialiasing(SunflowRenderPanel):
    bl_label = "Anti Aliasing"
    bl_options = {'DEFAULT_CLOSED'}
    
    display_property_groups = [
        (('scene',), 'sunflow_antialiasing')
    ]
            

@SunflowAddon.addon_register_class
class SunflowRender_PT_tracing(SunflowRenderPanel):
    bl_label = "Tracing"
    bl_options = {'DEFAULT_CLOSED'}
    
    display_property_groups = [
        (('scene',), 'sunflow_tracing')
    ]
 

@SunflowAddon.addon_register_class
class SunflowRender_PT_output(SunflowRenderPanel):
    bl_label = "Output"
    bl_options = {'DEFAULT_CLOSED'}
    
    display_property_groups = [
        (('scene', 'camera', 'data'), 'sunflow_film')
    ]
    
    def draw(self, context):
        layout = self.layout
                
        rd = context.scene.render        
        layout.prop(rd, "filepath", text="")
        
        split = layout.split()
        
        col = split.column()
        col.prop(rd, "use_overwrite")
        
        col = split.column()
        col.prop(rd, "use_file_extension")
        # split.prop(rd, "use_file_extension")
        
        film = context.scene.camera.data.sunflow_film
        layout.prop(film, "fileFormat")
        super().draw(context)


@SunflowAddon.addon_register_class
class SunflowRender_PT_performance(SunflowRenderPanel):
    bl_label = "Performance"
    bl_options = {'DEFAULT_CLOSED'}
    
    display_property_groups = [
        (('scene',), 'sunflow_performance')
    ]
    
    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        sfperf = context.scene.sunflow_performance
        split = layout.split()

        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Threads:")
        sub.row().prop(rd, "threads_mode", expand=True)
        subsub = sub.column()
        subsub.enabled = rd.threads_mode == 'FIXED'
        subsub.prop(rd, "threads")

        sub = col.column(align=True)
        sub.label(text="Bucket Size:")
        sub.prop(sfperf, "bucketSize", text="")
        sub.label(text="Bucket Order:")
        sub.prop(sfperf, "bucketOrder", text="")

        col = split.column()
        col.label(text="Optimize:")
        sub = col.column()
        sub.prop(sfperf, "useCacheObjects")
        sub.prop(sfperf, "useSmallMesh")
        sub.prop(sfperf, "threadHighPriority")
        sub.prop(sfperf, "enableVerbosity")
        sub.prop(sfperf, "ipr")
        sub.prop(sfperf, "useRandom")
        sub.prop(rd, "use_instances", text="Instances")
        
        super().draw(context)
        

