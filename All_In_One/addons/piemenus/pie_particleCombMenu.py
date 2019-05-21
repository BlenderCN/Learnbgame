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
from pie_menu import MenuItem, PieMenu
import pie_menu_utils as pmu
import modal_behavior

import math
import blf
import bgl

default_keybind='ONE'
 
bl_info = {
    "name": "Pie: Particle Comb Menu",
    "author": "Dan Eicher, Sean Olson",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "View3D",
    "description": "3d View delete pie menu",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}
 
class VIEW3D_MT_particle_comb_Menu(bpy.types.Operator):
    '''Pie Particle Comb Menu'''
    bl_idname = "view3d.particle_comb_menu"
    bl_label = "Particle Comb Menu"
 
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'
        

 
    def modal(self, context, event):
        context.area.tag_redraw()
        
        ret_val = modal_behavior.slider_modal(self, context, event) #could it be this simple?
        
        return ret_val
 
    def invoke(self, context, event):
        self.current = None
        current_keybind = bpy.context.window_manager.keyconfigs.user.keymaps['Particle'].keymap_items['view3d.particle_comb_menu'].type
        # generate menu content
        self.menu = menu_init(PieMenu(context, x=event.mouse_region_x,
                                      y=event.mouse_region_y,
                                      keybind = current_keybind,
                                      layout_radius=80,
                                      text_size=11,
                                      text_dpi=72,
                                      center_radius_squared=225,
                                      max_radius_squared=62500#22500
                                      ))
 
        context.window_manager.modal_handler_add(self)
        pmu.callback_register(self,context)
        return {'RUNNING_MODAL'}
 
 
def menu_init(menu):
    menu.menu_items.append(none("None",icon="EDGESEL"))
    menu.menu_items.append(comb("Comb", icon="MOD_DISPLACE")) #TODO finda  better one
    menu.menu_items.append(smooth("Smooth",icon="FACESEL"))
    menu.menu_items.append(add("Add", icon="SNAP_FACE"))
    menu.menu_items.append(length("Length", icon = "MOD_REMESH"))
    menu.menu_items.append(puff("Puff", icon = "SNAP_EDGE"))
    menu.menu_items.append(cut("Cut",icon = "VERTEXSEL"))
    menu.menu_items.append(weight("Weight",icon="BORDER_LASSO"))
    
    
    menu.calc_text() #need to figure out the box size from text..only once...not every draw.
    menu.calc_boxes() #make the round boxes and icons for anything not already manually defined    
    menu.layout_cardinal(rotate=False)
    
    return menu
 
 
class none(MenuItem):
    def op(self, parent, context):
        bpy.context.scene.tool_settings.particle_edit.tool = 'NONE'
 
class comb(MenuItem):
    def op(self, parent, context):
        bpy.context.scene.tool_settings.particle_edit.tool = 'COMB'

class smooth(MenuItem):
    def op(self, parent, context):
        bpy.context.scene.tool_settings.particle_edit.tool = 'SMOOTH'
  
class add(MenuItem):
    def op(self, parent, context):
        bpy.context.scene.tool_settings.particle_edit.tool = 'ADD'
 
class length(MenuItem):
    def op(self, parent, context):
        bpy.context.scene.tool_settings.particle_edit.tool = 'LENGTH'

class puff(MenuItem):
    def op(self, parent, context):
        bpy.context.scene.tool_settings.particle_edit.tool = 'PUFF'

class cut(MenuItem):
    def op(self, parent, context):
        bpy.context.scene.tool_settings.particle_edit.tool = 'CUT'

class weight(MenuItem):
    def op(self, parent, context):
        bpy.context.scene.tool_settings.particle_edit.tool = 'WEIGHT'
      
def setBind():
    #enable the addon keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Particle']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.particle_comb_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break

    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.layers':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==True and kmi.shift==True and kmi.oskey==True and kmi.any==True and kmi.key_modifier=='NONE':
                kmi.active=False
                break
    

def removeBind():
    #disable the addon keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Particle']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.particle_comb_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break

    #enable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.layers':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==True and kmi.shift==True and kmi.oskey==True and kmi.any==True and kmi.key_modifier=='NONE':
                kmi.active=True
                break
                
    
 
def register():
    bpy.utils.register_class(VIEW3D_MT_particle_comb_Menu)

    #add the keybinding   
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Particle']
    km.keymap_items.new('view3d.particle_comb_menu', default_keybind, 'PRESS')

    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.layers':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==True and kmi.shift==True and kmi.oskey==True and kmi.any==True and kmi.key_modifier=='NONE':
                kmi.active=False
                break
                
def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_particle_comb_Menu)

    #replace default
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.layers':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==True and kmi.shift==True and kmi.oskey==True and kmi.any==True and kmi.key_modifier=='NONE':
                kmi.active=True
                break
    
   
    #remove pie key
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.particle_comb_menu':
            km.keymap_items.remove(kmi)
            break
 
if __name__ == "__main__":
    register()
