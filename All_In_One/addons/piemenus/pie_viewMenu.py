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
import os

default_keybind='Q'
 
bl_info = {
    "name": "Pie: ViewMenu",
    "author": "Dan Eicher, Sean Olson, Patrick Moore",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "View3D",
    "description": "3d View view modes pie menu",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}
 
class VIEW3D_MT_View_Menu(bpy.types.Operator):
    '''View Menu'''
    bl_idname = "view3d.view_menu"
    bl_label = "Pie View Menu"
 
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'
        

 
    def modal(self, context, event):
        context.area.tag_redraw()
        
        ret_val = modal_behavior.slider_modal(self, context, event) #could it be this simple?
        
        return ret_val
    
    def invoke(self, context, event):
        self.current = None

        # generate menu content
        current_keybind = bpy.context.window_manager.keyconfigs.user.keymaps['3D View'].keymap_items['view3d.view_menu'].type
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
        #self.menu.layout(2*math.pi)  commented out to preserve hand set layouts
        pmu.callback_register(self,context)
        return {'RUNNING_MODAL'}
 
 
def menu_init(menu):
    #ViewTop.__init__(  #uncomment to see PyDev auto prediction
    #ViewTop.__init__(self, id, x, y, rot, scale, angle, icon, poly_bound)
    menu.menu_items.append(ViewLeft("Left", -80, 0, 0))
    menu.menu_items.append(ViewRight("Right", 80, 0, 0))
    menu.menu_items.append(ViewBottom("Bottom", 0, -55, 0))
    menu.menu_items.append(ViewTop("Top", 0, 55, 0))  
    menu.menu_items.append(ViewBack("Back", -65, 30, 0))
    menu.menu_items.append(ViewFront("Front", 65, 30, 0))
    menu.menu_items.append(ViewSelected("Selected", -65, -30, 0, icon="EDIT"))
    menu.menu_items.append(ViewCamera("Camera", 65, -30, 0, icon="OUTLINER_DATA_CAMERA"))
    menu.menu_items.append(ViewOrtho("Orth/Persp", -200, 100, 0, calc_mode = "POLY_LOOP", layout = "PREDEF")) #top left corner.
    menu.menu_items.append(ViewLocal("Local", -200, 70, calc_mode = "POLY_LOOP", layout = "PREDEF", icon="ZOOM_SELECTED")) #top left corner.
    
    menu.calc_text() #need to figure out the box size from text..only once...not every draw.
    menu.calc_boxes()
        
    menu.layout_predefined(auto_slice = True)  #this includes updating the local box coords to screen coords
    
    
    return menu
 
 
class ViewFront(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.viewnumpad(type='FRONT', align_active=False)
         
 
 
class ViewTop(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.viewnumpad(type='TOP', align_active=False)
 
 
class ViewRight(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.viewnumpad(type='RIGHT', align_active=False)
 
 
class ViewCamera(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.viewnumpad(type='CAMERA', align_active=False)
        

class PerspectiveToggle(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.view_persportho()
 
class ViewBack(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.viewnumpad(type='BACK', align_active=False)
 
 
class ViewBottom(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.viewnumpad(type='BOTTOM', align_active=False)
 
 
class ViewLeft(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.viewnumpad(type='LEFT', align_active=False)
       

class ViewSelected(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.view_selected()
 
class ViewOrtho(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.view_persportho()
        
class ViewLocal(MenuItem):
    def op(self, parent, context):
        bpy.ops.view3d.localview()
        
def setBind():
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.view_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break

def removeBind():
    #replace default
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.view_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
    

def register():
    bpy.utils.register_class(VIEW3D_MT_View_Menu)
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    km.keymap_items.new('view3d.view_menu', default_keybind, 'PRESS')



 
def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_View_Menu)

    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.view_menu':
            km.keymap_items.remove(kmi)
            break
 
if __name__ == "__main__":
    register()
