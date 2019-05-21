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

default_keybind = 'PERIOD'
 
bl_info = {
    "name": "Pie: Pivot Menu",
    "author": "Dan Eicher, Sean Olson",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "View3D",
    "description": "3d View pivots pie menu",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}
 
class VIEW3D_MT_View_Menu(bpy.types.Operator):
    '''Pivot Menu'''
    bl_idname = "view3d.pivot_menu"
    bl_label = "Pie Pivot Menu"
 
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'
        

 
    def modal(self, context, event):
        
        context.area.tag_redraw()
        
        ret_val = modal_behavior.slider_modal(self, context, event) #could it be this simple?
        
        return ret_val
 
 
    def invoke(self, context, event):
        self.current = None
        current_keybind = bpy.context.window_manager.keyconfigs.user.keymaps['3D View'].keymap_items['view3d.pivot_menu'].type
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
    menu.menu_items.append(Cursor("3D Cursor", 0, 55, icon = "CURSOR"))
    menu.menu_items.append(Individual("Individual", 85, 30, icon = "ROTATECOLLECTION"))
    menu.menu_items.append(Median("Median", 95, 0, icon = "ROTATECENTER"))

    if not bpy.context.space_data.use_pivot_point_align:
        menu.menu_items.append(ManipCenterOn("Origins Only On", 0, -55, icon = "ALIGN"))
    else:
        menu.menu_items.append(ManipCenterOff("Origins Only Off", 0, -55, icon = "ALIGN"))

    menu.menu_items.append(Active("Active", -95, 0, icon = "ROTACTIVE"))
    menu.menu_items.append(BoundingBox("Bounding Box", -85, 30, icon = "ROTATE"))
 
    menu.calc_text() #need to figure out the box size from text..only once...not every draw.
    menu.calc_boxes()
        
    menu.layout_predefined(auto_slice = True)  #this includes updating the local box coords to screen coords
 
    return menu
 
 
class Cursor(MenuItem):
    def op(self, parent, context):
       bpy.context.space_data.pivot_point = 'CURSOR'
 
 
class Active(MenuItem):
    def op(self, parent, context):
        bpy.context.space_data.pivot_point = 'ACTIVE_ELEMENT'
 
 
class Individual(MenuItem):
    def op(self, parent, context):
         bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
 
 
class BoundingBox(MenuItem):
    def op(self, parent, context):
        bpy.context.space_data.pivot_point = 'BOUNDING_BOX_CENTER'
 
 
class Median(MenuItem):
    def op(self, parent, context):
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
 
 
class ManipCenterOn(MenuItem):
    def op(self, parent, context):
        bpy.context.space_data.use_pivot_point_align = True

class ManipCenterOff(MenuItem):
    def op(self, parent, context):
        bpy.context.space_data.use_pivot_point_align = False
             
def setBind():
    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_set_enum':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break

    #enable the addon keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.pivot_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break


def removeBind():
    #enable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_set_enum':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break

    #disable the addon keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.pivot_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
 
def register():
    bpy.utils.register_class(VIEW3D_MT_View_Menu)

    #add the keybinding   
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    km.keymap_items.new('view3d.pivot_menu', default_keybind, 'PRESS')

    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_set_enum':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
 
 
def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_View_Menu)

    #replace default
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.context_set_enum':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break
   
    #remove pie key
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.pivot_menu':
            km.keymap_items.remove(kmi)
            break

 
if __name__ == "__main__":
    register()
