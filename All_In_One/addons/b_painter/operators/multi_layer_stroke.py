'''
Copyright (C) 2017 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
    
import bpy
from mathutils import Vector
from math import fmod        
        
######################################################################################################################################### Cutout Animatin Tools Modal Operator    
class BPainterMultiLayerPaint(bpy.types.Operator):
    bl_idname = "b_painter.multi_layer_paint"
    bl_label = "BPainter Multi Layer Paint"
    bl_options = {"REGISTER","UNDO"}
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()
    
    def __init__(self):
        self.brush = None
        
        self.mouse_pos = Vector((0,0))
        self.mouse_pos_init = Vector((0,0))
        self.mouse_pos_stamp = Vector((0,0))
        self.pressure_stamp = 0.0
        self.brush_size_stamp = 0.0
        self.stroke_length = 0
        self.brush_size = 1
        self.spacing = 600
        
        self.paint_stroke_preview = []
        self.paint_stroke = []
        self.start = True
        
        self.tex_slot_idx = 0
        self.canvas = None
        
        self.mask_map_mode = ""
        self.map_mode = ""
        self.offset = [0,0,0]
        
        self.spacing = 0.4
        self.init = True
        self.channels = []
        self.color = [0,0,0,1]
        self.unified_color = [0,0,0,1]
        
    def get_brush_size(self,context):
        if context.tool_settings.unified_paint_settings.use_unified_size:
            self.brush_size = context.tool_settings.unified_paint_settings.size
        else:
            self.brush_size = context.tool_settings.image_paint.brush.size
         
         
    def get_pressure(self,context,event):
        if context.tool_settings.unified_paint_settings.use_pressure_size:
            return event.pressure
        else:
            return 1.0
            
        
        
    def modal(self,context,event):
        
        self.get_brush_size(context)
        spacing = max(self.brush_size * event.pressure * self.spacing,2)
        if spacing == 0:
            spacing = 0.1
        self.mouse_pos = Vector((event.mouse_region_x,event.mouse_region_y))
        
        
        
        stroke_vec = self.mouse_pos_stamp - self.mouse_pos
        stroke_length = stroke_vec.magnitude
        
        tex_offset = self.mouse_pos_init - self.mouse_pos
        
            
        if stroke_length > spacing:# or self.init:
            dot_count = min(int(stroke_length / spacing),30)
            
            for i,channel in enumerate(self.channels):
                context.tool_settings.image_paint.canvas = channel
                context.tool_settings.image_paint.brush.color = channel.b_painter_channel.color
                context.tool_settings.unified_paint_settings.color = channel.b_painter_channel.color
                
                for i in range(dot_count):
                    final_pos = self.mouse_pos + (stroke_vec * (1/(dot_count/(i+1))))
                    
                    if self.brush.texture != None and self.map_mode == "VIEW_PLANE":
                        offset = (stroke_vec * (1/(dot_count/(i+1))))
                        self.brush.texture_slot.offset = [-final_pos[0]/self.brush_size,-final_pos[1]/self.brush_size,0]
                    if i == 0:
                        is_start = True
                    else:
                        is_start = False    
                    self.paint_stroke_preview.append({'name':'', 'location':(0,0,0), 'mouse':final_pos, 'size': self.brush_size*self.get_pressure(context,event), 'pen_flip':False, 'is_start':is_start, 'pressure':self.get_pressure(context,event), 'time':10000})
                    self.start = False
                
            self.mouse_pos_stamp = self.mouse_pos
        
            
        if event.value == "RELEASE" and event.type == "MOUSEMOVE":
            override = bpy.context.copy()
            override["tool_settings"] = bpy.context.tool_settings
            bpy.ops.paint.image_paint(override, "EXEC_DEFAULT",False, stroke=self.paint_stroke_preview, mode="SMOOTH")
            
            self.paint_stroke_preview = []
            
            context.tool_settings.image_paint.brush.texture_slot.mask_map_mode = self.mask_map_mode
            context.tool_settings.image_paint.brush.texture_slot.map_mode = self.map_mode
            context.tool_settings.image_paint.brush.texture_slot.offset = self.offset
            context.tool_settings.image_paint.canvas = self.canvas
            
            
            context.tool_settings.image_paint.brush.color = self.color
            context.tool_settings.unified_paint_settings.color = self.unified_color
            return{'FINISHED'}
        
        return{'RUNNING_MODAL'}
    
    def create_tmp_tex(self,context):
        obj = bpy.context.active_object
        img = bpy.data.images.new("tmp_buffer_img",512,512,alpha=True)
        img.generated_color = [0,0,0,0]
        img.use_alpha = True
        tex = bpy.data.textures.new("tmp_buffer_tex","IMAGE")
        mat = obj.active_material
        tex_slot = mat.texture_slots.create(17)
        tex.image = img
        tex_slot.texture = tex
        
        context.tool_settings.image_paint.canvas = img
    
    def delete_tmp_tex(self,context):
        obj = bpy.context.active_object
        for tex in bpy.data.textures:
            if "tmp_buffer_tex" in tex.name:
                bpy.data.textures.remove(tex,do_unlink=True)
        for img in bpy.data.images:
            if "tmp_buffer_img" in img.name:
                bpy.data.images.remove(img,do_unlink=True)
        mat = obj.active_material
        mat.texture_slots.clear(17)
    
    def get_paint_channels(self,context):
        obj = context.active_object
        
        mat = obj.active_material
        mats = [mat]
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "MATERIAL" and node.material != mat:
                    mats.append(node.material)
        
        images = []
        for layer in mat.b_painter.paint_layers:
            if layer.name in bpy.data.images:
                img = bpy.data.images[layer.name]
                if img not in images and img.b_painter_channel.active:
                    images.append(bpy.data.images[layer.name])
        return images        
        
        
    def invoke(self,context,event):
        self.brush = context.tool_settings.image_paint.brush
        self.color = context.tool_settings.image_paint.brush.color
        self.unified_color = context.tool_settings.unified_paint_settings.color
        
        self.channels = self.get_paint_channels(context)
        
        self.canvas = context.tool_settings.image_paint.canvas
        
        self.offset = Vector(context.tool_settings.image_paint.brush.texture_slot.offset)
        self.map_mode = str(context.tool_settings.image_paint.brush.texture_slot.map_mode)
        self.mask_map_mode = str(context.tool_settings.image_paint.brush.texture_slot.mask_map_mode)
        
        if context.tool_settings.image_paint.brush.texture_slot.map_mode == "VIEW_PLANE":
            context.tool_settings.image_paint.brush.texture_slot.mask_map_mode = "TILED"
            context.tool_settings.image_paint.brush.texture_slot.map_mode = "TILED"
        
        self.mouse_pos_stamp = Vector((event.mouse_region_x,event.mouse_region_y))
        self.mouse_pos_init = Vector((event.mouse_region_x,event.mouse_region_y))
        wm = context.window_manager
        wm.modal_handler_add(self)
        return{'RUNNING_MODAL'}         