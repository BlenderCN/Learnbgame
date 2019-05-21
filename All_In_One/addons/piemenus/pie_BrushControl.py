'''
Created on Jan 21, 2013

@author: Patrick
'''
# -*- coding: utf-8 -*-
 
# Copyright (c) 2010, Dan Eicher.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 
# <pep8 compliant>

import bpy
from pie_menu import MenuItem, PieMenu, PiePropSlider, PiePropRadio
import pie_menu_utils as pmu
import modal_behavior

import math
import blf
import bgl

default_keybind = 'V'
 
bl_info = {
    "name": "Pie: Brush Control Menu",
    "author": "Dan Eicher, Sean Olson",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "View3D",
    "description": "Sculpt Mode Brush Control Menu",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}
 
class VIEW3D_MT_brush_control_Menu(bpy.types.Operator):
    '''Pie Brush Control Menu'''
    bl_idname = "view3d.brush_control"
    bl_label = "Pie Brush Control Menu"
 
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'
        
    def modal(self, context, event):
        context.area.tag_redraw()
        
        ret_val = modal_behavior.slider_modal(self, context, event) #could it be this simple?
        
        return ret_val
 
    def invoke(self, context, event):
        self.current = None
        current_keybind = bpy.context.window_manager.keyconfigs.user.keymaps['Sculpt'].keymap_items['view3d.brush_control'].type
        # generate menu content
        self.menu = menu_init(PieMenu(context, x=event.mouse_region_x,
                                      y=event.mouse_region_y,
                                      keybind = default_keybind,
                                      layout_radius=50,
                                      text_size=11,
                                      text_dpi=72,
                                      center_radius_squared=225,
                                      max_radius_squared=62500#22500
                                      ))
 
        context.window_manager.modal_handler_add(self)
        pmu.callback_register(self,context)
        return {'RUNNING_MODAL'}
 
 
def menu_init(menu):

    
    #PiePropRadio(id, data, property, width, height, x, y, rot, scale)
    #menu.menu_items.append(PiePropRadio("Falloff Overlay",bpy.context.tool_settings.sculpt.brush, "use_cursor_overlay", -240, 40, 0))
    menu.menu_items.append(PiePropRadio("Texture Overlay",bpy.context.tool_settings.sculpt.brush, "use_primary_overlay", -180, 40, 0))
    menu.menu_items.append(PiePropRadio("Smooth",bpy.context.tool_settings.sculpt.brush,"use_smooth_stroke", -80, -70, 0))
    menu.menu_items.append(dynamic("Tog Dyn",bpy.context.object,"use_dynamic_topology_sculpting", -180, -40, 0))  #TODO: change icon to dyntopo icon...meaning update the sheet and dictionary 
      
    
    #Add any sliders
    #id, data, property, width, height, x, y, rot = 0, scale = 1, rad = 5)
    menu.sliders.append(PiePropSlider("Autosmooth",bpy.context.tool_settings.sculpt.brush,"auto_smooth_factor", 100,18, 0,70))
    menu.sliders.append(PiePropSlider("Spacing",bpy.context.tool_settings.sculpt.brush,"spacing", 100,18, 100,40))
    menu.sliders.append(PiePropSlider("Strength", bpy.context.tool_settings.sculpt.brush, "strength", 100,18, 120, 0))
    menu.sliders.append(PiePropSlider("Jitter", bpy.context.tool_settings.sculpt.brush, "jitter", 100,18,100, -40))
    menu.sliders.append(PiePropSlider("Smooth Radius", bpy.context.tool_settings.sculpt.brush, "smooth_stroke_radius", 100,18,0, -70))
    menu.sliders.append(PiePropSlider("Smooth Factor", bpy.context.tool_settings.sculpt.brush, "smooth_stroke_factor", 100,18,0, -110))   
    menu.sliders.append(PiePropSlider("Dyn-Detail", bpy.context.scene.tool_settings.sculpt, "detail_size", 100,18,-100, -40))  
    menu.sliders.append(PiePropSlider("Size",bpy.context.tool_settings.unified_paint_settings,"size", 100,18,-120,0))
    menu.sliders.append(PiePropSlider("Angle", bpy.context.tool_settings.sculpt.brush.texture_slot, "angle", 100,18, -100, 40))
    
    
    
    
    

    menu.calc_text() #need to figure out the box size from text..only once...not every draw.
    menu.calc_boxes() #make the round boxes and icons for anything not already manually defined
        
    menu.layout_predefined(auto_slice = True)  #this includes updating the local box coords to screen coords
    
    return menu
 

#class brush_strength(PiePropSlider):
    #def push_to_prop(self):
        #bpy.ops.wm.radial_control(data_path_primary = "bpy.context.tool_settings.sculpt.brush.strength")
 
#class overlay(PiePropRadio):
    #def op(self, parent, context):
        #if bpy.context.tool_settings.sculpt.brush.use_primary_overlay == True:
        #    bpy.context.tool_settings.sculpt.brush.use_primary_overlay = False
        #    bpy.context.tool_settings.sculpt.brush.use_cursor_overlay = False
        #else:
        #    bpy.context.tool_settings.sculpt.brush.use_primary_overlay = True
        #    bpy.context.tool_settings.sculpt.brush.use_cursor_overlay = True
 
class smooth(MenuItem):
    def op(self, parent, context):
        if bpy.context.tool_settings.sculpt.brush.use_smooth_stroke:
            bpy.context.tool_settings.sculpt.brush.use_smooth_stroke=False
        else:
            bpy.context.tool_settings.sculpt.brush.use_smooth_stroke=True

class dynamic(PiePropRadio):
    def op(self, parent, context):
        bpy.ops.sculpt.dynamic_topology_toggle()
        self.pull_from_prop()
        self.update_local_to_screen()
        


  
class downright(MenuItem):
    def op(self, parent, context):
        print('do sometihng!')
 
class down(MenuItem):
    def op(self, parent, context):
        print('do sometihng!')

class downleft(MenuItem):
    def op(self, parent, context):
        print('do sometihng!')

class left(MenuItem):
    def op(self, parent, context):
        print('do sometihng!')


class upleft(MenuItem):
    def op(self, parent, context):
        print('do sometihng!')
       
def setBind():
    #enable the addon keybinding
    bpy.context.window_manager.keyconfigs.user.keymaps['Sculpt'].keymap_items['view3d.brush_control'].active=True
         

def removeBind():
    #disable the addon keybinding
    bpy.context.window_manager.keyconfigs.user.keymaps['Sculpt'].keymap_items['view3d.brush_control'].active=False

 
def register():
    bpy.utils.register_class(VIEW3D_MT_brush_control_Menu)

    #add the keybinding   
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Sculpt']
    km.keymap_items.new('view3d.brush_control', default_keybind, 'PRESS')

    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Sculpt']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
 
 
def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_brush_control_Menu)

    #replace default
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Sculpt']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break
   
    #remove pie key
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.brush_control':
            km.keymap_items.remove(kmi)
            break
 
if __name__ == "__main__":
    register()
