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

default_keybind = 'O'
 
bl_info = {
    "name": "Pie: Proportional Menu",
    "author": "Dan Eicher, Sean Olson, Patrick Moore",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "View3D",
    "description": "Proportional modes pie menu",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}
 
class VIEW3D_MT_Proportional_Menu(bpy.types.Operator):
    '''Proportional Menu'''
    bl_idname = "view3d.proportional_menu"
    bl_label = "Pie Proportional Menu"
 
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'
        

 
    def modal(self, context, event):
        context.area.tag_redraw()
        
        ret_val = modal_behavior.slider_modal(self, context, event) #could it be this simple?
        
        return ret_val
 
    def invoke(self, context, event):
        self.current = None
        if bpy.context.mode == 'EDIT_MESH':
            current_keybind = bpy.context.window_manager.keyconfigs.user.keymaps['Mesh'].keymap_items['view3d.proportional_menu'].type
        else:
            current_keybind = bpy.context.window_manager.keyconfigs.user.keymaps['Object Mode'].keymap_items['view3d.proportional_menu'].type
        # generate menu content
        self.menu = menu_init(PieMenu(context, x=event.mouse_region_x,
                                      y=event.mouse_region_y,
                                      keybind=current_keybind,
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
   
    if bpy.context.mode == 'EDIT_MESH':
        menu.menu_items.append(propConnected("Connected", 0, 45, 0, icon="PROP_CON"))
    menu.menu_items.append(propOn("On", 80, 0, 0, icon="PROP_ON"))
    menu.menu_items.append(propOff("Off", -80, 0, 0, icon="PROP_OFF"))
    
    menu.menu_items.append(fallSmooth("Smooth", -200, 100, 0, calc_mode = "POLY_LOOP", layout = "PREDEF", icon="SMOOTHCURVE")) #top left corner.
    menu.menu_items.append(fallSphere("Sphere", -200, 70, 0, calc_mode = "POLY_LOOP", layout = "PREDEF", icon="SPHERECURVE")) 
    menu.menu_items.append(fallRoot("Root", -200, 40, 0, calc_mode = "POLY_LOOP", layout = "PREDEF", icon="ROOTCURVE")) 
    menu.menu_items.append(fallSharp("Sharp", -200, 10, 0, calc_mode = "POLY_LOOP", layout = "PREDEF", icon="SHARPCURVE"))
    menu.menu_items.append(fallLinear("Linear", -200, -20, 0, calc_mode = "POLY_LOOP", layout = "PREDEF", icon="LINCURVE")) 
    menu.menu_items.append(fallConstant("Constant", -200, -50, 0, calc_mode = "POLY_LOOP", layout = "PREDEF", icon="NOCURVE")) 
    menu.menu_items.append(fallRandom("Random", -200, -80, 0, calc_mode = "POLY_LOOP", layout = "PREDEF", icon="RNDCURVE")) 
 
 
 
    menu.calc_text() #need to figure out the box size from text..only once...not every draw.
    menu.calc_boxes() #make the round boxes and icons for anything not already manually defined     
    menu.layout_predefined(auto_slice = True)  #this includes updating the local box coords to screen coords
        
   
 
    return menu
 
 
class propOn(MenuItem):
    def op(self, parent, context):
        if bpy.context.mode == 'EDIT_MESH':
            bpy.context.tool_settings.proportional_edit = 'ENABLED'
        else:
            bpy.context.tool_settings.use_proportional_edit_objects =  True

class propOff(MenuItem):
    def op(self, parent, context):
        if bpy.context.mode == 'EDIT_MESH':
            bpy.context.tool_settings.proportional_edit = 'DISABLED'
        else:
            bpy.context.tool_settings.use_proportional_edit_objects = False

 
class propConnected(MenuItem):
    def op(self, parent, context):
         bpy.context.tool_settings.proportional_edit = 'CONNECTED'
         
class fallSmooth(MenuItem):
    def op(self, parent, context):
         bpy.context.tool_settings.proportional_edit_falloff = 'SMOOTH'
         
class fallSphere(MenuItem):
    def op(self, parent, context):
         bpy.context.tool_settings.proportional_edit_falloff = 'SPHERE'
         
class fallRoot(MenuItem):
    def op(self, parent, context):
         bpy.context.tool_settings.proportional_edit_falloff = 'ROOT'

class fallSharp(MenuItem):
    def op(self, parent, context):
         bpy.context.tool_settings.proportional_edit_falloff = 'SHARP'
         
class fallLinear(MenuItem):
    def op(self, parent, context):
         bpy.context.tool_settings.proportional_edit_falloff = 'LINEAR'
         
class fallConstant(MenuItem):
    def op(self, parent, context):
         bpy.context.tool_settings.proportional_edit_falloff = 'CONSTANT'
         
class fallRandom(MenuItem):
    def op(self, parent, context):
         bpy.context.tool_settings.proportional_edit_falloff = 'RANDOM'
         
       
def register():
    bpy.utils.register_class(VIEW3D_MT_Proportional_Menu)



    #add the keybinding   
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    km.keymap_items.new('view3d.proportional_menu', default_keybind, 'PRESS')
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode']
    km.keymap_items.new('view3d.proportional_menu', default_keybind, 'PRESS')

    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_toggle_enum':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
                
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_toggle':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
def setBind():
    #set addon
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.proportional_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break
                
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.proportional_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break

    #turn off default
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_toggle_enum':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
                
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_toggle':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break

def removeBind():
    #remove addon keys
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.proportional_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
                
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.proportional_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break

    #turn on default
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_toggle_enum':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break
                
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_toggle':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break
 
 
def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_Proportional_Menu)

    #replace default
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_toggle_enum':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break
    #remove pie key
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.proportional_menu':
            km.keymap_items.remove(kmi)
            break   
     
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_toggle':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break
   
    #remove pie key
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.proportional_menu':
            km.keymap_items.remove(kmi)
            break   
   
 
if __name__ == "__main__":
    register()
