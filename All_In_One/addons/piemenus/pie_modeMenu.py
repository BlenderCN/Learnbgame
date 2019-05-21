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
from pie_menu import MenuItem, PieMenu, PiePropSlider
import pie_menu_utils as pmu
import modal_behavior

import math
import blf
import bgl
import random

default_keybind = 'TAB'
 
bl_info = {
    "name": "Pie: Mode Menu",
    "author": "Dan Eicher, Sean Olson",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "View3D > Q-key",
    "description": "3d View modes pie menu",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}
 
class VIEW3D_MT_Mode_Menu(bpy.types.Operator):
    '''Mode Menu'''
    bl_idname = "view3d.mode_menu"
    bl_label = "Pie Mode Menu"
 
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'
        
    def modal(self, context, event):
        
        context.area.tag_redraw()
        
        ret_val = modal_behavior.slider_modal(self, context, event) #could it be this simple?
        
        return ret_val
        
    def invoke(self, context, event):
        
        if context.selected_objects:
            self.current = None
            self.mouse_drag = False  #this might be a good property for the PieMenu isntead of the Operator?  Brainstorm on that.
            current_keybind = bpy.context.window_manager.keyconfigs.user.keymaps['Object Non-modal'].keymap_items['view3d.mode_menu'].type
            # generate menu content
            self.menu = menu_init(PieMenu(context, x=event.mouse_region_x,
                                          y=event.mouse_region_y,
                                          keybind = current_keybind, #TODO:  Should this come from some other place, not in the file...how would the user change it.
                                          layout_radius=80,
                                          text_size=11,
                                          text_dpi=72,
                                          center_radius_squared=225,
                                          max_radius_squared=62500#22500
                                          ))
     
            context.window_manager.modal_handler_add(self)
            pmu.callback_register(self,context)
            return {'RUNNING_MODAL'}
        else:
            return{'CANCELLED'}
 

def menu_init(menu):
    #Add regular Items
    menu.menu_items.append(Sculpt("Sculpt Mode", 0, 55,icon="SCULPTMODE_HLT"))
    menu.menu_items.append(Pose("Pose Mode", 75, 30,icon="POSE_HLT"))
    menu.menu_items.append(Edit("Edit Mode", 100, 0,icon="EDITMODE_HLT"))
    menu.menu_items.append(WeightPaint("Weight Paint", 75, -30,icon="WPAINT_HLT"))
    menu.menu_items.append(TexturePaint("Texture Paint", 0, -55,icon="TPAINT_HLT"))  
    menu.menu_items.append(VertexPaint("Vertex Paint", -75, -30,icon="VPAINT_HLT"))
    menu.menu_items.append(Object("Object Mode", -100, 0,icon="OBJECT_DATAMODE"))
    menu.menu_items.append(Particle("Particle Mode", -75, 30, icon="PARTICLEMODE"))
    
    #Add any sliders
    #id, data, property, width, height, x, y, rot = 0, scale = 1, rad = 5)
    #menu.sliders.append(PiePropSlider("Diffuse",bpy.context.object.material_slots[0].material,"diffuse_intensity", 100,10,0,85))
    #menu.sliders.append(PiePropSlider("Diffuse_2", bpy.context.object.material_slots[0].material, "alpha", 100, 10, -175, 0, rot = math.pi/2))

    #do initial calcing and laying out
    menu.calc_text() #need to figure out the box size from text..only once...not every draw.
    menu.calc_boxes()

    menu.layout_predefined(auto_slice = True)  #this includes updating the local box coords to screen coords
    return menu
 
 
class Object(MenuItem):
    def op(self, parent, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.ed.undo_push(message="Enter Object Mode")
 
 
class Edit(MenuItem):
    def op(self, parent, context):
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.ed.undo_push(message="Enter Edit Mode")

    def poll(self, context):
        objecttype=bpy.context.object.type
        if objecttype=='LATTICE' or objecttype=='MESH' or objecttype=='CURVE' or objecttype=='SURFACE' or objecttype=='META' or objecttype=='FONT' or objecttype=='ARMATURE':
            return True
        else:
            return False

class Sculpt(MenuItem):
    def op(self, parent, context):
         bpy.ops.object.mode_set(mode = 'SCULPT')
         
    def poll(self, context):
        if bpy.context.object.type=='MESH':
            return True
        else:
            return False
 
 
class VertexPaint(MenuItem):
    def op(self, parent, context):
        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')

    def poll(self, context):
        if bpy.context.object.type=='MESH':
            return True
        else:
            return False
 
 
class TexturePaint(MenuItem):
    def op(self, parent, context):
        bpy.ops.object.mode_set(mode = 'TEXTURE_PAINT')

    def poll(self, context):
        if bpy.context.object.type=='MESH':
            return True
        else:
            return False
 
 
class WeightPaint(MenuItem):
    def op(self, parent, context):
        bpy.ops.object.mode_set(mode = 'WEIGHT_PAINT')

    def poll(self, context):
        if bpy.context.object.type=='MESH':
            return True
        else:
            return False
 
 
class Pose(MenuItem):
    def op(self, parent, context):
        bpy.ops.object.mode_set(mode = 'POSE')

    def poll(self, context):
        if bpy.context.object.type == 'ARMATURE':
            return True
        else:
            return False

class Particle(MenuItem):
    def op(self, parent, context):
        if bpy.ops.particle.particle_edit_toggle.poll():
            bpy.ops.particle.particle_edit_toggle()


    def poll(self, context):
        if not len(bpy.context.object.particle_systems.items())==0:
            return True
        else:
            return False

            

def setBind():
    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Non-modal']
    for kmi in km.keymap_items:
        if kmi.idname == 'object.mode_set':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break

    #enable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Non-modal']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.mode_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break

def removeBind():
    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Non-modal']
    for kmi in km.keymap_items:
        if kmi.idname == 'object.mode_set':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break

    #enable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Non-modal']
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.mode_menu':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
        
def register():
    bpy.utils.register_class(VIEW3D_MT_Mode_Menu)
    
    #add the keybinding   
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Non-modal']
    km.keymap_items.new('view3d.mode_menu', default_keybind, 'PRESS')

    #disable the default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Non-modal']
    for kmi in km.keymap_items:
        if kmi.idname == 'object.mode_set':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=False
                break
 
 
def unregister(): 
    

    #replace default
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Non-modal']
    for kmi in km.keymap_items:
        if kmi.idname == 'object.mode_set':
            if kmi.type == default_keybind and kmi.ctrl==False and kmi.alt==False and kmi.shift==False and kmi.oskey==False and kmi.any==False and kmi.key_modifier=='NONE':
                kmi.active=True
                break
   
    #remove pie key
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.mode_menu':
            km.keymap_items.remove(kmi)
            break

    bpy.utils.unregister_class(VIEW3D_MT_Mode_Menu)
 
if __name__ == "__main__":
    register()
