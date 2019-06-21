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
from math import sin, cos, pi, fmod
from bpy.props import StringProperty
import bgl
import blf
import bisect
from .. functions import srgb_to_linear

class RemoveBrushFilter(bpy.types.Operator):
    bl_idname = "b_painter.remove_brush_filter"
    bl_label = "Remove Brush Filter"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wm = context.window_manager
        wm.b_painter_brush_filter = ""
        return {"FINISHED"}

class AddGradientColorStop(bpy.types.Operator):
    bl_idname = "b_painter.add_gradient_color_stop"
    bl_label = "Add Gradient Color Stop"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wm = context.window_manager
        brush = context.tool_settings.image_paint.brush
        color = brush.color if not context.tool_settings.unified_paint_settings.use_unified_color else context.tool_settings.unified_paint_settings.color
        if brush != None:
            brush.gradient.elements.new(1.0)
        return {"FINISHED"}
        
    
class ToggleEraser(bpy.types.Operator):
    bl_idname = "b_painter.toggle_eraser"
    bl_label = "Toggle Eraser"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        brush = context.tool_settings.image_paint.brush
        if brush != None:
            if brush.name != "Eraser":
                prev_brush = str(context.scene.b_painter_brush)
                context.scene.b_painter_brush = "Eraser"
                brush = bpy.data.brushes[context.scene.b_painter_brush]
                brush["prev_brush"] = prev_brush
            else:
                if "prev_brush" in brush:
                    context.scene.b_painter_brush = brush["prev_brush"]
                    del(brush["prev_brush"])
                    
        return {"FINISHED"}
    
class SetAbsoluteBrushSize(bpy.types.Operator):
    bl_idname = "b_painter.set_absolute_brush_size"
    bl_label = "Set Absolute Brush Size"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    mouse_pos = Vector((0,0))
    mouse_pos_init = Vector((0,0))
    offset = Vector((0,0))
    brush_size = 1.0
    brush_size_init = 1.0
    new_brush_size = 1.0
    brush_color = None
    brush = None
    show_brush = False
    @classmethod
    def poll(cls, context):
        return True
    
    def get_region_3d(self,context):
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        return space.region_3d
        return None  
    
    def invoke(self, context, event):
        self.brush = context.tool_settings.image_paint.brush
        self.brush_size = context.tool_settings.image_paint.brush.size if not context.tool_settings.unified_paint_settings.use_unified_size else context.tool_settings.unified_paint_settings.size
        self.brush_size_init = int(self.brush_size)
        self.offset = Vector((-self.brush_size,0))
        self.mouse_pos_init = Vector((event.mouse_region_x,event.mouse_region_y)) + self.offset
        
        self.show_brush = bool(context.tool_settings.image_paint.show_brush)
        context.tool_settings.image_paint.show_brush = False
        
        if context.tool_settings.unified_paint_settings.use_unified_color:
            self.brush_color = list(context.tool_settings.unified_paint_settings.color)
        else:
            self.brush_color = list(self.color)
        
        args = (self, context)
        if context.area.type == "VIEW_3D":
            self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        elif context.area.type == "IMAGE_EDITOR":
            self._handle = bpy.types.SpaceImageEditor.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
    
    def finish(self):
        bpy.context.area.header_text_set()
        bpy.context.tool_settings.image_paint.show_brush = self.show_brush
        if bpy.context.area.type == "VIEW_3D":
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
        elif bpy.context.area.type == "IMAGE_EDITOR":
            bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, "WINDOW")
        return {"FINISHED"}
    
    def modal(self, context, event):
        settings = context.tool_settings.unified_paint_settings
        brush = context.tool_settings.image_paint.brush
        
        context.area.tag_redraw()
        
        self.mouse_pos.x = event.mouse_region_x
        self.mouse_pos.y = event.mouse_region_y
        
        self.new_brush_size = (self.mouse_pos - self.mouse_pos_init).length
        self.brush_size = self.new_brush_size
        
        region_3d = self.get_region_3d(context)
        if region_3d != None:
            context.scene.b_painter_absolute_size = self.brush_size / 1.767676 /  (1/region_3d.view_distance)
        
        context.area.header_text_set(text="Radius: "+str(int(context.scene.b_painter_absolute_size)))
        
        if event.type == "LEFTMOUSE":
            if settings.use_unified_size:
                settings.size = self.brush_size
            else:
                brush.size = self.brush_size
            if region_3d != None:    
                context.scene.b_painter_absolute_size = self.brush_size / 1.767676 /  (1/region_3d.view_distance)
            else:
                context.scene.b_painter_absolute_size = self.brush_size / 1.767676
            return self.finish()

        elif event.type in {"RIGHTMOUSE", "ESC"}:
            return self.finish()

        return {"RUNNING_MODAL"}
    
    def draw_callback_px(tmp, self, context):
        color = bpy.context.tool_settings.image_paint.brush.cursor_color_add
        
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(color[0], color[1], color[2], .5)
        bgl.glLineWidth(1)
        
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        
        ### draw curve gradient
        ring_count = 12
        segements = 36
                
        for j in range(ring_count):
            bgl.glBegin(bgl.GL_QUAD_STRIP)
            for i in range(segements+1):
                curve = self.brush.curve.curves[0]
                curve_pos = (j*(1/ring_count))
                curve_pos = min(curve_pos,1.0)
                curve_pos = max(curve_pos,0.0)
                curve_pos2 = curve_pos + (1/ring_count)
                curve_pos2 = min(curve_pos2,1.0)
                curve_pos2 = max(curve_pos2,0.0)
                
                alpha1 = curve.evaluate(curve_pos)
                alpha2 = curve.evaluate(curve_pos2)
                
                offset = self.mouse_pos_init
                angle = 2*pi/segements
                size = self.brush_size * (j+1)*(1/ring_count)
                size2 = self.brush_size * j*(1/ring_count)
                point1 = offset + Vector((size* cos(i*angle),(size* sin(i*angle))))
                point2 = offset + Vector((size2* cos(i*angle),(size2* sin(i*angle))))
                
                bgl.glColor4f(self.brush_color[0], self.brush_color[1], self.brush_color[2], alpha2)
                bgl.glVertex2f(point1[0],point1[1])
                bgl.glColor4f(self.brush_color[0], self.brush_color[1], self.brush_color[2], alpha1)
                bgl.glVertex2f(point2[0],point2[1])        
            
            bgl.glEnd()
        
        ### draw brush circles
        bgl.glColor4f(color[0], color[1], color[2], .5)
        bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINE_LOOP)
        segements = 42
        for i in range(segements):
            bgl.glVertex2f(self.mouse_pos_init.x + self.brush_size*cos(i*(2*pi/segements)),self.mouse_pos_init.y + self.brush_size*sin(i*(2*pi/segements)))
        bgl.glEnd()
        
        bgl.glBegin(bgl.GL_LINE_LOOP)
        segements = 42
        for i in range(segements):
            bgl.glVertex2f(self.mouse_pos_init.x + self.brush_size_init*cos(i*(2*pi/segements)),self.mouse_pos_init.y + self.brush_size_init*sin(i*(2*pi/segements)))
        bgl.glEnd()
        
        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0) 
        

class SetBrushHardness(bpy.types.Operator):
    bl_idname = "b_painter.set_brush_hardness"
    bl_label = "Set Brush Hardness"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    mode = StringProperty(default="HARDNESS")
    
    mouse_pos = Vector((0,0))
    mouse_pos_init = Vector((0,0))
    hardness = 1.0
    outer_size = 180
    innter_size = 40
    hardness = 1.0
    strength = 1.0
    init_strength = 0.0
    brush = None
    show_brush = False
    
    settings = None
    
    brush_color = None
    
    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        self.settings = context.tool_settings
        self.brush = context.tool_settings.image_paint.brush
        self.init_strength = self.brush.b_painter_hardness
        self.hardness = 1-self.brush.b_painter_hardness
        self.show_brush = bool(context.tool_settings.image_paint.show_brush)
        context.tool_settings.image_paint.show_brush = False
        
        
        if context.tool_settings.unified_paint_settings.use_unified_color:
            self.brush_color = list(context.tool_settings.unified_paint_settings.color)
        else:
            self.brush_color = list(self.color)
        
        self.inner_size = 40
        self.outer_size = 200
        self.mouse_pos_init = Vector((event.mouse_region_x,event.mouse_region_y))
        self.mouse_pos_init.x -= (self.outer_size - self.inner_size)*self.hardness + self.inner_size
        args = ()
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
    
    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_pos.x = event.mouse_region_x
        self.mouse_pos.y = event.mouse_region_y
        
        self.hardness = (self.mouse_pos - self.mouse_pos_init).length
        
        if event.ctrl:
            divider = ((self.outer_size-self.inner_size)*.1)
            self.hardness = int((self.hardness - self.hardness%divider + divider*.5))
        self.hardness = min(self.outer_size,self.hardness)
        self.hardness = max(self.inner_size,self.hardness)
        self.strength = 1-((self.hardness /(self.outer_size-self.inner_size)) - self.inner_size/(self.outer_size-self.inner_size))
        
        self.brush.b_painter_hardness = self.strength
        
        text = format(self.strength,".3f")
        context.area.header_text_set(text="Hardness: "+text)
        
        
        if event.type == "LEFTMOUSE":
            return self.finish(context)

        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.brush.b_painter_hardness = self.init_strength
            return self.finish(context)

        return {"RUNNING_MODAL"}

    def finish(self,context):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        context.tool_settings.image_paint.show_brush = self.show_brush
        context.area.header_text_set()
        return {"FINISHED"}

    def draw_callback_px(self):
        color = bpy.context.tool_settings.image_paint.brush.cursor_color_add
        
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(color[0], color[1], color[2], .5)
        bgl.glLineWidth(1)
        
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        
        ### draw curve gradient
        ring_count = 12
        segements = 36
                
        for j in range(ring_count):
            bgl.glBegin(bgl.GL_QUAD_STRIP)
            for i in range(segements+1):
                curve = self.brush.curve.curves[0]
                curve_pos = (j*(1/ring_count))
                curve_pos = min(curve_pos,1.0)
                curve_pos = max(curve_pos,0.0)
                curve_pos2 = curve_pos + (1/ring_count)
                curve_pos2 = min(curve_pos2,1.0)
                curve_pos2 = max(curve_pos2,0.0)
                
                alpha1 = curve.evaluate(curve_pos)
                alpha2 = curve.evaluate(curve_pos2)
                
                offset = self.mouse_pos_init
                angle = 2*pi/segements
                size = self.outer_size * (j+1)*(1/ring_count)
                size2 = self.outer_size * j*(1/ring_count)
                point1 = offset + Vector((size* cos(i*angle),(size* sin(i*angle))))
                point2 = offset + Vector((size2* cos(i*angle),(size2* sin(i*angle))))
                
                bgl.glColor4f(self.brush_color[0], self.brush_color[1], self.brush_color[2], alpha2)
                bgl.glVertex2f(point1[0],point1[1])
                bgl.glColor4f(self.brush_color[0], self.brush_color[1], self.brush_color[2], alpha1)
                bgl.glVertex2f(point2[0],point2[1])        
            
            bgl.glEnd()
        
        ### draw brush circles
        bgl.glColor4f(color[0], color[1], color[2], .5)
        bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINE_LOOP)
        segements = 42
        for i in range(segements):
            bgl.glVertex2f(self.mouse_pos_init.x + self.inner_size*cos(i*(2*pi/segements)),self.mouse_pos_init.y + self.inner_size*sin(i*(2*pi/segements)))
        bgl.glEnd()
        
        bgl.glBegin(bgl.GL_LINE_LOOP)
        for i in range(segements):
            bgl.glVertex2f(self.mouse_pos_init.x + self.hardness*cos(i*(2*pi/segements)),self.mouse_pos_init.y + self.hardness*sin(i*(2*pi/segements)))
        bgl.glEnd()
        
        bgl.glBegin(bgl.GL_LINE_LOOP)
        for i in range(segements):
            bgl.glVertex2f(self.mouse_pos_init.x + self.outer_size*cos(i*(2*pi/segements)),self.mouse_pos_init.y + self.outer_size*sin(i*(2*pi/segements)))
        bgl.glEnd()
          
        ### draw brush values
        font_id = 0
        blf.size(font_id, 17, 72)
        
        blf.enable(font_id,blf.SHADOW)
        blf.shadow(font_id,5,0,0,0,.8)
        blf.shadow_offset(font_id,1,-1)
        bgl.glColor4f(color[0], color[1], color[2], .5)
        blf.position(font_id, self.mouse_pos_init.x-24, self.mouse_pos_init.y-6, 0)
        blf.draw(font_id, format(self.strength,".3f"))
        
        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0) 
    

class SetBrushCurve(bpy.types.Operator):
    bl_idname = "b_painter.set_brush_curve"
    bl_label = "Set Brush Curve"
    bl_description = ""
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self,context):
        layout = self.layout
        brush = context.scene.tool_settings.image_paint.brush
        layout.template_curve_mapping(brush, "curve", brush=True)

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
        row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
        row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
        row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
        row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
        row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_popup(self,event)

class DefaultColors(bpy.types.Operator):
    bl_idname = "b_painter.set_default_colors"
    bl_label = "Set Default Colors"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        
        return True

    def execute(self, context):
        settings = context.tool_settings.unified_paint_settings
        brush = context.tool_settings.image_paint.brush
        
        if settings.use_unified_color:
            settings.color = [0,0,0]
            settings.secondary_color = [1,1,1]
        else:
            brush.color = [0,0,0]
            brush.secondary_color = [1,1,1]    
        
        
        return {"FINISHED"}
        
    
class SetCavityCurve(bpy.types.Operator):
    bl_idname = "b_painter.set_cavity_curve"
    bl_label = "Set Brush Curve"
    bl_description = ""
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self,context):
        layout = self.layout
        brush = context.scene.tool_settings.image_paint.brush
        ipaint = context.tool_settings.image_paint
        layout.template_curve_mapping(ipaint, "cavity_curve", brush=True)
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_popup(self,event)        

            