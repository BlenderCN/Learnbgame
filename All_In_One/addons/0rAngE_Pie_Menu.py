# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "0rAngE Pie Menu",
    "author": "0rAngE",
    "blender": (2, 80, 0),
    "category": "Learnbgame"
}

import bpy
from bpy.types import Menu

###################################
#       Particle Edit Class       #               
###################################

class ParticleNone(bpy.types.Operator):
    bl_idname = "particle_none.pie"
    bl_label = "Particle None"

    def execute(self, context):
        layout = self.layout
        bpy.context.scene.tool_settings.particle_edit.tool = 'NONE'
        return {'FINISHED'}

class ParticleComb(bpy.types.Operator):
    bl_idname = "particle_comb.pie"
    bl_label = "Particle Comb"

    def execute(self, context):
        layout = self.layout
        bpy.context.scene.tool_settings.particle_edit.tool = 'COMB'
        return {'FINISHED'}

class ParticleSmooth(bpy.types.Operator):
    bl_idname = "particle_smooth.pie"
    bl_label = "Particle Smooth"

    def execute(self, context):
        layout = self.layout
        bpy.context.scene.tool_settings.particle_edit.tool = 'SMOOTH'
        return {'FINISHED'}

class ParticleAdd(bpy.types.Operator):
    bl_idname = "particle_add.pie"
    bl_label = "Particle Add"

    def execute(self, context):
        layout = self.layout
        bpy.context.scene.tool_settings.particle_edit.tool = 'ADD'
        return {'FINISHED'}

class ParticleLength(bpy.types.Operator):
    bl_idname = "particle_length.pie"
    bl_label = "Particle Length"

    def execute(self, context):
        layout = self.layout
        bpy.context.scene.tool_settings.particle_edit.tool = 'LENGTH'
        return {'FINISHED'}

class ParticlePuff(bpy.types.Operator):
    bl_idname = "particle_puff.pie"
    bl_label = "Particle Puff"

    def execute(self, context):
        layout = self.layout
        bpy.context.scene.tool_settings.particle_edit.tool = 'PUFF'
        return {'FINISHED'}

class ParticleCut(bpy.types.Operator):
    bl_idname = "particle_cut.pie"
    bl_label = "Particle Cut"

    def execute(self, context):
        layout = self.layout
        bpy.context.scene.tool_settings.particle_edit.tool = 'CUT'
        return {'FINISHED'}

class ParticleWeight(bpy.types.Operator):
    bl_idname = "particle_weight.pie"
    bl_label = "Particle Weight"

    def execute(self, context):
        layout = self.layout
        bpy.context.scene.tool_settings.particle_edit.tool = 'WEIGHT'
        return {'FINISHED'}

######################
#     Pie Menus      #               
######################

# Poly Pie
class PiePoly(Menu):
    bl_idname = "poly.pie"
    bl_label = "Poly Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("mira.poly_loop", text="Mira Poly Loop")
        #6 - RIGHT
        pie.operator("objects.multiedit_exit_operator", text="MultiEdit Exit")
        #2 - BOTTOM
        pie.operator("mesh.offset_edges", text="Offset Edge")
        #8 - TOP
        pie.operator("mesh.fill_grid", text="Grid Fill")
        #7 - TOP - LEFT
        box = pie.split().column()
        row = box.split(align=True)
        box.prop(context.scene.mi_cur_stretch_settings, "points_number", text="Points")
        box.operator("mira.curve_stretch", text="Mira Curve Stretch")
        #9 - TOP - RIGHT
        box = pie.split().column()
        row = box.split(align=True)
        box.operator("mira.linear_deformer", text="Mira Linear Deformer")
        box.operator("mira.deformer", text="Mira Deformer")
        #1 - BOTTOM - LEFT
        box = pie.split().column()
        row = box.split(align=True)
        box.operator("mesh.loop_multi_select", text="Select Loop").ring=False
        box.operator("mesh.loop_multi_select", text="Select Ring").ring=True
        box.operator("mesh.loop_to_region", text="Select Loop-InnerRegion")
        box.operator("mesh.region_to_loop", text="Select Boundary Loop")
        box.operator("mesh.select_nth", text="Checker DeSelect")
        #3 - BOTTOM - RIGHT
        pie.operator("mesh.edgetune", text="Edge Tune")
        
# Object Pie
class PieObject(Menu):
    bl_idname = "object.pie"
    bl_label = "Object Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        box = pie.split().column()
        row = box.split(align=True)
        box.operator("view3d.modifiers_subsurf_level_0", text="SubSurf 0")
        box.operator("view3d.modifiers_subsurf_level_1", text="SubSurf 1")
        box.operator("view3d.modifiers_subsurf_level_2", text="SubSurf 2")
        #6 - RIGHT
        pie.operator("objects.multiedit_enter_operator", text="MultiEdit Enter")
        #2 - BOTTOM
        pie.operator("object.convert", text="Convert To Mesh").target="MESH"
        #8 - TOP
        pie.operator("object.align_location_all", text="Align Location", icon = 'MAN_TRANS')
        #7 - TOP - LEFT
        pie.operator("object.align_rotation_all", text="Align Rotation", icon = 'MAN_ROT')
        #9 - TOP - RIGHT
        pie.operator("object.align_objects_scale_all", text="Align Scale", icon = 'MAN_SCALE')
        #1 - BOTTOM - LEFT
        box = pie.split().column()
        row = box.split(align=True)
        box.operator("view3d.display_modifiers_apply", text="Apply Modifiers", icon = 'MODIFIER')
        box.operator("view3d.display_modifiers_delete", text="Delete Modifiers", icon = 'X')
        #3 - BOTTOM - RIGHT
        box = pie.split().column()
        row = box.split(align=True)
        box.operator("view3d.display_modifiers_viewport_on", text="Modifiers On", icon = 'RESTRICT_VIEW_OFF')
        box.operator("view3d.display_modifiers_viewport_off", text="Modifiers Off", icon = 'RESTRICT_VIEW_ON')

#Sculpt Pie
class PieSculpt(Menu):
    bl_idname = "sculpt.pie"
    bl_label = "Sculpt Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("paint.brush_select", text="Crease", icon='BRUSH_CREASE').sculpt_tool='CREASE'
        #6 - RIGHT
        pie.operator("paint.brush_select", text='Pinch/Magnify', icon='BRUSH_PINCH').sculpt_tool= 'PINCH'
        #2 - BOTTOM
        pie.operator("paint.brush_select", text='Claystrips', icon='BRUSH_CREASE').sculpt_tool= 'CLAY_STRIPS'
        #8 - TOP
        pie.operator("paint.brush_select", text='Brush', icon='BRUSH_SCULPT_DRAW').sculpt_tool='DRAW'
        #7 - TOP - LEFT 
        pie.operator("paint.brush_select", text='Grab', icon='BRUSH_GRAB').sculpt_tool='GRAB'
        #9 - TOP - RIGHT
        pie.operator("paint.brush_select", text='Snakehook', icon='BRUSH_SNAKE_HOOK').sculpt_tool= 'SNAKE_HOOK'
        #1 - BOTTOM - LEFT
        #pie.operator("paint.brush_select", text='Mask', icon='BRUSH_MASK').sculpt_tool='MASK'
        box = pie.split().column()
        row = box.row(align=True)
        box.operator("paint.brush_select", text='Fill/Deepen', icon='BRUSH_FILL').sculpt_tool='FILL'
        box.operator("paint.brush_select", text='Polish/Flatten', icon='BRUSH_FLATTEN').sculpt_tool= 'FLATTEN'
        box.operator("paint.brush_select", text='Scrape/Peaks', icon='BRUSH_SCRAPE').sculpt_tool= 'SCRAPE'
        #3 - BOTTOM - RIGHT
        pie.operator("paint.brush_select", text='Inflate/Deflate', icon='BRUSH_INFLATE').sculpt_tool='INFLATE'

#Vertex Paint Pie
class PieVertexPaint(Menu):
    bl_idname = "vpaint.pie"
    bl_label = "Vertex Paint Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("paint.brush_select", text='Add').vertex_paint_tool='ADD'
        #6 - RIGHT
        pie.operator("paint.brush_select", text='Subtract').vertex_paint_tool='SUB'
        #2 - BOTTOM
        pie.operator("paint.brush_select", text='Blur').vertex_paint_tool='BLUR'
        #8 - TOP
        pie.operator("paint.brush_select", text='Brush/Draw/Mix').vertex_paint_tool='MIX'
        #7 - TOP - LEFT 
        pie.operator("paint.brush_select", text='Lighten').vertex_paint_tool='LIGHTEN'
        #9 - TOP - RIGHT
        pie.operator("paint.brush_select", text='Darken').vertex_paint_tool='DARKEN'
        #1 - BOTTOM - LEFT
        pie.operator("paint.brush_select", text='Multiply').vertex_paint_tool='MUL'
        #3 - BOTTOM - RIGHT

#Weight Paint Pie
class PieWeightPaint(Menu):
    bl_idname = "wpaint.pie"
    bl_label = "Weight Paint Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("paint.brush_select", text='Add').weight_paint_tool='ADD'
        #6 - RIGHT
        pie.operator("paint.brush_select", text='Subtract').weight_paint_tool='SUB'
        #2 - BOTTOM
        pie.operator("paint.brush_select", text='Blur').weight_paint_tool='BLUR'
        #8 - TOP
        pie.operator("paint.brush_select", text='Brush/Draw/Mix').weight_paint_tool='MIX'
        #7 - TOP - LEFT 
        pie.operator("paint.brush_select", text='Lighten').weight_paint_tool='LIGHTEN'
        #9 - TOP - RIGHT
        pie.operator("paint.brush_select", text='Darken').weight_paint_tool='DARKEN'
        #1 - BOTTOM - LEFT
        pie.operator("paint.brush_select", text='Multiply').weight_paint_tool='MUL'
        #3 - BOTTOM - RIGHT

#Texture Paint Pie
class PieTexturePaint(Menu):
    bl_idname = "tpaint.pie"
    bl_label = "Texture Paint Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("paint.brush_select", text='Mask').texture_paint_tool='MASK'
        #6 - RIGHT
        pie.operator("paint.brush_select", text='Fill').texture_paint_tool='FILL'
        #2 - BOTTOM
        pie.operator("paint.brush_select", text='Soften').texture_paint_tool='SOFTEN'
        #8 - TOP
        pie.operator("paint.brush_select", text='Brush/Draw/TexDraw').texture_paint_tool='DRAW'
        #7 - TOP - LEFT 
        pie.operator("paint.brush_select", text='Clone').texture_paint_tool='CLONE'
        #9 - TOP - RIGHT
        pie.operator("paint.brush_select", text='Smear').texture_paint_tool='SMEAR'
        #1 - BOTTOM - LEFT
        #3 - BOTTOM - RIGHT

#Particle Edit Pie
class ParticleEdit(Menu):
    bl_idname = "particle_edit.pie"
    bl_label = "Particle Edit"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("particle_comb.pie", text="Comb")
        #6 - RIGHT
        pie.operator("particle_length.pie", text="Length")
        #2 - BOTTOM
        pie.operator("particle_none.pie", text="None")
        #8 - TOP
        pie.operator("particle_add.pie", text="Add")
        #7 - TOP - LEFT 
        pie.operator("particle_puff.pie", text="Puff")
        #9 - TOP - RIGHT
        pie.operator("particle_cut.pie", text="Cut")
        #1 - BOTTOM - LEFT
        pie.operator("particle_weight.pie", text="Weight")
        #3 - BOTTOM - RIGHT
        pie.operator("particle_smooth.pie", text="Smooth")

addon_keymaps = []

def register():
    # Poly Pie_void
    bpy.utils.register_class(PiePoly)
    bpy.utils.register_class(PieObject)
    bpy.utils.register_class(PieSculpt)
    bpy.utils.register_class(PieVertexPaint)
    bpy.utils.register_class(PieWeightPaint)
    bpy.utils.register_class(PieTexturePaint)
    bpy.utils.register_class(ParticleNone)
    bpy.utils.register_class(ParticleComb)
    bpy.utils.register_class(ParticleSmooth)
    bpy.utils.register_class(ParticleAdd)
    bpy.utils.register_class(ParticleLength)
    bpy.utils.register_class(ParticlePuff)
    bpy.utils.register_class(ParticleCut)
    bpy.utils.register_class(ParticleWeight)
    bpy.utils.register_class(ParticleEdit)

# Keympa Config   
    
    wm = bpy.context.window_manager
    
    if wm.keyconfigs.addon:
        #Poly Pie
        km = wm.keyconfigs.addon.keymaps.new(name='Mesh')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'MIDDLEMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "poly.pie"
        
        #Object Pie
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'MIDDLEMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "object.pie"

        #Sculpt Pie Menu
        km = wm.keyconfigs.addon.keymaps.new(name='Sculpt')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'MIDDLEMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "sculpt.pie"

        #Vertex Paint Pie Menu
        km = wm.keyconfigs.addon.keymaps.new(name='Vertex Paint')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'MIDDLEMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "vpaint.pie"

        #Weight Paint Pie Menu
        km = wm.keyconfigs.addon.keymaps.new(name='Weight Paint')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'MIDDLEMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "wpaint.pie"

        #Texture Paint Pie Menu
        km = wm.keyconfigs.addon.keymaps.new(name='Image Paint')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'MIDDLEMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "tpaint.pie"

        #Particle Edit Pie Menu
        km = wm.keyconfigs.addon.keymaps.new(name='Particle')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'MIDDLEMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "particle_edit.pie"

# Register / Unregister Classes
def unregister():
    # Poly Pie_void
    bpy.utils.unregister_class(PiePoly)
    bpy.utils.unregister_class(PieObject)
    bpy.utils.unregister_class(PieSculpt)
    bpy.utils.unregister_class(PieVertexPaint)
    bpy.utils.unregister_class(PieWeightPaint)
    bpy.utils.unregister_class(PieTexturePaint)
    bpy.utils.unregister_class(ParticleNone)
    bpy.utils.unregister_class(ParticleComb)
    bpy.utils.unregister_class(ParticleSmooth)
    bpy.utils.unregister_class(ParticleAdd)
    bpy.utils.unregister_class(ParticleLength)
    bpy.utils.unregister_class(ParticlePuff)
    bpy.utils.unregister_class(ParticleCut)
    bpy.utils.unregister_class(ParticleWeight)
    bpy.utils.unregister_class(ParticleEdit)

    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        for km in addon_keymaps:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)

            wm.keyconfigs.addon.keymaps.remove(km)

    # clear the list
    del addon_keymaps[:]

if __name__ == "__main__":
    register()