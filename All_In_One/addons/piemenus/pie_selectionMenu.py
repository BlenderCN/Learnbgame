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

default_keybind = 'TAB'
 
bl_info = {
    "name": "Pie: Selection Menu",
    "author": "Dan Eicher, Sean Olson",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "View3D",
    "description": "3d selection modes pie menu",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}
 
class VIEW3D_MT_Selection_Menu(bpy.types.Operator):
    '''Selection Menu'''
    bl_idname = "view3d.selection_menu"
    bl_label = "Pie Selection Menu"
 
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'
        

 
    def modal(self, context, event):
        context.area.tag_redraw()
        
        ret_val = modal_behavior.slider_modal(self, context, event) #could it be this simple?
        
        return ret_val
 
    def invoke(self, context, event):
        self.current = None
        current_keybind = bpy.context.window_manager.keyconfigs.user.keymaps['Mesh'].keymap_items['view3d.selection_menu'].type
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
    menu.menu_items.append(Edges("Edges", 0, 55, icon="EDGESEL"))
    menu.menu_items.append(EdgesFaces("Edges & Faces", 80, 30, icon="SNAP_FACE"))
    menu.menu_items.append(Faces("Faces", 100, 0, icon="FACESEL"))
    menu.menu_items.append(VertsEdgesFaces("Verts Edges Faces", 80, -30, icon="SNAP_VOLUME"))
    menu.menu_items.append(VertsFaces("Verts & Faces", -80, -30, icon="ORTHO"))
    menu.menu_items.append(Verts("Verts", -100, 0, icon="VERTEXSEL"))
    menu.menu_items.append(VertsEdges("Verts & Edges", -80, 30, icon="EDITMODE_HLT"))
    if bpy.context.space_data.use_occlude_geometry:
        menu.menu_items.append(UseOccludeGeometry("Occlude On", 0, -55, icon="ORTHO"))
    else:
        menu.menu_items.append(UseOccludeGeometry("Occlude Off", 0, -55, icon="ORTHO"))
    
 
    menu.calc_text() #need to figure out the box size from text..only once...not every draw.
    menu.calc_boxes()
        
    menu.layout_predefined(auto_slice = True)  #this includes updating the local box coords to screen coords
 
    return menu
 
 
class Verts(MenuItem):
    def op(self, parent, context):
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
 
 
class Edges(MenuItem):
    def op(self, parent, context):
        bpy.context.tool_settings.mesh_select_mode = (False, True, False)
 
 
class Faces(MenuItem):
    def op(self, parent, context):
        bpy.context.tool_settings.mesh_select_mode = (False, False, True)
 
 
class VertsEdges(MenuItem):
    def op(self, parent, context):
        bpy.context.tool_settings.mesh_select_mode = (True, True, False)
 
 
class EdgesFaces(MenuItem):
    def op(self, parent, context):
        bpy.context.tool_settings.mesh_select_mode = (False, True, True)
 
 
class VertsFaces(MenuItem):
    def op(self, parent, context):
        bpy.context.tool_settings.mesh_select_mode = (True, False, True)
 
 
class VertsEdgesFaces(MenuItem):
    def op(self, parent, context):
        bpy.context.tool_settings.mesh_select_mode = (True, True, True)
        
class UseOccludeGeometry(MenuItem):
    def op(self, parent, context):
        if bpy.context.space_data.use_occlude_geometry:
            bpy.context.space_data.use_occlude_geometry = False
        else:
            bpy.context.space_data.use_occlude_geometry = True

def setBind():
    #enable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break

    #disable the addon keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.selection_menu':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break              


def removeBind():
    #enable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break

    #disable the addon keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.selection_menu':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break              

def register():
    bpy.utils.register_class(VIEW3D_MT_Selection_Menu)

    #add keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    km.keymap_items.new('view3d.selection_menu', default_keybind, 'PRESS', ctrl=True)

    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
 
 
def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_Selection_Menu)
 
    #enable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.type == default_keybind and kmi.ctrl==True and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break

    #remove the pie key
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.selection_menu':
            km.keymap_items.remove(kmi)
            break
 
if __name__ == "__main__":
    register()
