#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

bl_info = {
    "name": "Brush Strength/Radius QuickSet",
    "description": "Alter brush radius or strength in the 3D view.",
    "author": "Cody Burrow (vrav)",
    "version": (0, 8, 2),
    "blender": (2, 7, 6),
    "location": "User Preferences > Input > assign 'brush.modal_quickset'",
    "warning": "Automatically assigns brush.modal_quickset to RMB in sculpt mode",
    "category": "Learnbgame",
}

# brush_quickset.py
# brush.modal_quickset for hotkeys
# Brush QuickSet from search menu

# Modify sculpt/paint brush radius and strength in a streamlined manner.
# To use, assign a hotkey to brush.modal_quickset in a paint or sculpt mode.
# Recommended RMB, but any key can be used in a hold-and-release manner.

# What does it do? When you activate the modal operator, you can drag the
#   mouse along either axis to affect brush radius or strength. Which axis
#   affects which is configurable, amongst other things detailed below.

# Operator Options:
#   - Axis Order: Whether X or Y affects brush size, etc.
#   - Key Action: Hotkey activity (press or release) can apply or cancel.
#   - Numeric: Show strength value when adjusted; can pick size
#   - Slider: Represent strength with a visual slider; can pick size
#   - Pixel Deadzone: Distance before an axis starts affecting the brush.
#   - Size Sensitivity: Multiplier for quicker or slower radius adjustment.
#   - Graphic: Represent strength via transparent brush overlay
#   - Lock Axis: Allow only one value to be altered at a time

# Known limitations:
#   - Not available for painting in the image editor.
#   - Holding ctrl does not snap to values, probably should.

from mathutils import Color
import bpy
import bgl
import blf

def draw_callback_px(self, context):
    # circle graphic, text, and slider
    unify_settings = bpy.context.tool_settings.unified_paint_settings
    strength = unify_settings.strength if self.uni_str else self.brush.strength
    size = unify_settings.size if self.uni_size else self.brush.size
    
    if self.graphic:
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(self.brushcolor.r, self.brushcolor.g, self.brushcolor.b, strength * 0.25)
        bgl.glBegin(bgl.GL_POLYGON)
        for x, y in self.circlepoints:
            bgl.glVertex2i(int(size * x) + self.cur[0], int(size * y) + self.cur[1])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    
    if self.text != 'NONE' and self.doingstr:
        if self.text == 'MEDIUM':
            fontsize = 11
        elif self.text == 'LARGE':
            fontsize = 22
        else:
            fontsize = 8
        
        font_id = 0
        blf.size(font_id, fontsize, 72)
        blf.shadow(font_id, 0, 0.0, 0.0, 0.0, 1.0)
        blf.enable(font_id, blf.SHADOW)
        
        if strength < 0.001:
            text = "0.001"
        else:
            text = str(strength)[0:5]
        textsize = blf.dimensions(font_id, text)
        
        xpos = self.start[0] + self.offset[0]
        ypos = self.start[1] + self.offset[1]
        
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(self.backcolor.r, self.backcolor.g, self.backcolor.b, 0.5)
        
        bgl.glBegin(bgl.GL_POLYGON)
        for x, y in self.rectpoints:
            bgl.glVertex2i(int(textsize[0] * x) + xpos, int(textsize[1] * y) + ypos)
        bgl.glEnd()
        
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
        
        blf.position(font_id, xpos, ypos, 0)
        blf.draw(font_id, text)
        
        blf.disable(font_id, blf.SHADOW)
    
    if self.slider != 'NONE' and self.doingstr:
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(self.backcolor.r, self.backcolor.g, self.backcolor.b, 0.5)
        
        xpos = self.start[0] + self.offset[0] - self.sliderwidth + (32 if self.text == 'MEDIUM' else 64 if self.text == 'LARGE' else 23)
        ypos = self.start[1] + self.offset[1] - self.sliderheight# + (1 if self.slider != 'SMALL' else 0)
        
        if strength <= 1.0:
            sliderscale = strength
        elif strength > 5.0:
            sliderscale = strength / 10
        elif strength > 2.0:
            sliderscale = strength / 5
        else:
            sliderscale = strength / 2
        
        bgl.glBegin(bgl.GL_POLYGON)
        for x, y in self.rectpoints:
            bgl.glVertex2i(int(self.sliderwidth * x) + xpos, int(self.sliderheight * y) + ypos - 1)
        bgl.glEnd()
        
        bgl.glColor4f(self.frontcolor.r, self.frontcolor.g, self.frontcolor.b, 0.8)
        
        bgl.glBegin(bgl.GL_POLYGON)
        for x, y in self.rectpoints:
            bgl.glVertex2i(int(self.sliderwidth * x * sliderscale) + xpos, int(self.sliderheight * y * 0.75) + ypos)
        bgl.glEnd()
        
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

def applyChanges(self):
    unify_settings = bpy.context.tool_settings.unified_paint_settings

    if self.doingstr:
        if self.uni_str:
            modrate = self.strmod * 0.0025
            newval  = unify_settings.strength + modrate
            if 10.0 > newval > 0.0:
                unify_settings.strength = newval
                self.strmod_total += modrate
        else:
            modrate = self.strmod * 0.0025
            newval  = self.brush.strength + modrate
            if 10.0 > newval > 0.0:
                self.brush.strength = newval
                self.strmod_total += modrate
    
    if self.doingrad:
        if self.uni_size:
            newval = unify_settings.size + self.radmod
            if 2000 > newval > 0:
                unify_settings.size = newval
                self.radmod_total += self.radmod
        else:
            newval = self.brush.size + self.radmod
            if 2000 > newval > 0:
                self.brush.size = newval
                self.radmod_total += self.radmod

def revertChanges(self):
    unify_settings = bpy.context.tool_settings.unified_paint_settings
    
    if self.doingstr:
        if self.uni_str:
            unify_settings.strength -= self.strmod_total
        else:
            self.brush.strength -= self.strmod_total
    
    if self.doingrad:
        if self.uni_size:
            unify_settings.size -= self.radmod_total
        else:
            self.brush.size -= self.radmod_total



class BrushValuesQuickSet(bpy.types.Operator):
    bl_idname = "brush.modal_quickset"
    bl_label = "Brush QuickSet"
    
    axisaffect = bpy.props.EnumProperty(
        name        = "Axis Order",
        description = "Which axis affects which brush property",
        items       = [('YSTR', 'X: Radius, Y: Strength', ''),
                       ('YRAD', 'Y: Radius, X: Strength', '')],
        default     = 'YRAD')
    
    keyaction = bpy.props.EnumProperty(
        name        = "Key Action",
        description = "Hotkey second press or initial release behaviour",
        items       = [('IGNORE', 'Key Ignored', ''),
                       ('CANCEL', 'Key Cancels', ''),
                       ('FINISH', 'Key Applies', '')],
        default     = 'FINISH')
    
    text = bpy.props.EnumProperty(
        name        = "Numeric",
        description = "Text display; only shows when strength adjusted",
        items       = [('NONE', 'None', ''),
                       ('LARGE', 'Large', ''),
                       ('MEDIUM', 'Medium', ''),
                       ('SMALL', 'Small', '')],
        default     = 'MEDIUM')
    
    slider = bpy.props.EnumProperty(
        name        = "Slider",
        description = "Slider display for strength visualization",
        items       = [('NONE', 'None', ''),
                       ('LARGE', 'Large', ''),
                       ('MEDIUM', 'Medium', ''),
                       ('SMALL', 'Small', '')],
        default     = 'MEDIUM')
    
    deadzone = bpy.props.IntProperty(
        name        = "Pixel Deadzone",
        description = "Screen distance after which movement has effect",
        default     = 16,
        min         = 0)
    
    sens = bpy.props.FloatProperty(
        name        = "Sensitivity",
        description = "Multiplier to affect brush settings by",
        default     = 1.0,
        min         = 0.1,
        max         = 2.0)
    
    graphic = bpy.props.BoolProperty(
        name        = "Graphic",
        description = "Transparent circle to visually represent strength",
        default     = True)
    
    lock = bpy.props.BoolProperty(
        name        = "Lock Axis",
        description = "When adjusting one value, lock the other",
        default     = True)
    
    
    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D'
                and context.mode in {'SCULPT', 'PAINT_WEIGHT', 'PAINT_VERTEX', 'PAINT_TEXTURE', 'PARTICLE'})
    
    
    def modal(self, context, event):
        sens = (self.sens * 0.5) if event.shift else (self.sens)
        self.cur = (event.mouse_region_x, event.mouse_region_y)
        diff = (self.cur[0] - self.prev[0], self.cur[1] - self.prev[1])
        
        if self.axisaffect == 'YRAD':
            # Y corresponds to radius
            if not self.doingrad:
                if self.lock:
                    if not self.doingstr and abs(self.cur[1] - self.start[1]) > self.deadzone:
                        self.doingrad = True
                        self.radmod = diff[1] * sens
                elif abs(self.cur[1] - self.start[1]) > self.deadzone:
                    self.doingrad = True
                    self.radmod = diff[1] * sens
            else:
                self.radmod = diff[1] * sens
            if not self.doingstr:
                if self.lock:
                    if not self.doingrad and abs(self.cur[0] - self.start[0]) > self.deadzone:
                        self.doingstr = True
                        self.strmod = diff[0] * sens
                elif abs(self.cur[0] - self.start[0]) > self.deadzone:
                    self.doingstr = True
                    self.strmod = diff[0] * sens
            else:
                self.strmod = diff[0] * sens
        else:
            # Y corresponds to strength
            if not self.doingrad:
                if self.lock:
                    if not self.doingstr and abs(self.cur[0] - self.start[0]) > self.deadzone:
                        self.doingrad = True
                        self.radmod = diff[0] * sens
                elif abs(self.cur[0] - self.start[0]) > self.deadzone:
                    self.doingrad = True
                    self.radmod = diff[0] * sens
            else:
                self.radmod = diff[0] * sens
            if not self.doingstr:
                if self.lock:
                    if not self.doingrad and abs(self.cur[1] - self.start[1]) > self.deadzone:
                        self.doingstr = True
                        self.strmod = diff[1] * sens
                elif abs(self.cur[1] - self.start[1]) > self.deadzone:
                    self.doingstr = True
                    self.strmod = diff[1] * sens
            else:
                self.strmod = diff[1] * sens
        
        context.area.tag_redraw()
        if event.type in {'LEFTMOUSE'} or self.action == 1:
            # apply changes, finished
            if hasattr(self, '_handle'):
                context.space_data.draw_handler_remove(self._handle, 'WINDOW')
                del self._handle
            applyChanges(self)
            return {'FINISHED'}
        elif event.type in {'ESC'} or self.action == -1:
            # do nothing, return to previous settings
            if hasattr(self, '_handle'):
                context.space_data.draw_handler_remove(self._handle, 'WINDOW')
                del self._handle
            revertChanges(self)
            return {'CANCELLED'}
        elif self.keyaction != 'IGNORE' and event.type in {self.hotkey} and event.value == 'RELEASE':
            # if key action enabled, prepare to exit
            if self.keyaction == 'FINISH':
                if hasattr(self, '_handle'):
                    context.space_data.draw_handler_remove(self._handle, 'WINDOW')
                    del self._handle
                self.action = 1
            elif self.keyaction == 'CANCEL':
                if hasattr(self, '_handle'):
                    context.space_data.draw_handler_remove(self._handle, 'WINDOW')
                    del self._handle
                self.action = -1
            return {'RUNNING_MODAL'}
        else:
            # continuation
            applyChanges(self)
            self.prev = self.cur
            return {'RUNNING_MODAL'}
        return {'CANCELLED'}
    
    
    def invoke(self, context, event):
        if bpy.context.mode == 'SCULPT':
            self.brush = context.tool_settings.sculpt.brush
        elif bpy.context.mode == 'PAINT_TEXTURE':
            self.brush = context.tool_settings.image_paint.brush
        elif bpy.context.mode == 'PAINT_VERTEX':
            self.brush = context.tool_settings.vertex_paint.brush
        elif bpy.context.mode == 'PAINT_WEIGHT':
            self.brush = context.tool_settings.weight_paint.brush
        elif bpy.context.mode == 'PARTICLE':
            if context.tool_settings.particle_edit.tool == 'NONE':
                return {'CANCELLED'}
            self.brush = context.tool_settings.particle_edit.brush
        else:
            self.report({'WARNING'}, "Mode invalid - only paint or sculpt")
            return {'CANCELLED'}
        
        self.hotkey = event.type
        if self.hotkey == 'NONE':
            self.keyaction = 'IGNORE'
        self.action = 0
        unify_settings = context.tool_settings.unified_paint_settings
        
        if bpy.context.mode == 'PARTICLE':
            self.uni_size = False
            self.uni_str = False
        else:
            self.uni_size = unify_settings.use_unified_size
            self.uni_str = unify_settings.use_unified_strength
        
        self.doingrad = False
        self.doingstr = False
        self.start = (event.mouse_region_x, event.mouse_region_y)
        self.prev = self.start
        self.radmod_total = 0.0
        self.strmod_total = 0.0
        self.radmod = 0.0
        self.strmod = 0.0
        
        # self._handle = context.space_data.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')

        if self.graphic:
            if not hasattr(self, '_handle'):
                self._handle = context.space_data.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
            
            if hasattr(self, "brush.cursor_color_add"):
                self.brushcolor = self.brush.cursor_color_add
                if self.brush.sculpt_capabilities.has_secondary_color and self.brush.direction in {'SUBTRACT','DEEPEN','MAGNIFY','PEAKS','CONTRAST','DEFLATE'}:
                    self.brushcolor = self.brush.cursor_color_subtract
            else:
                self.brushcolor = Color((1.0, 0.5, 0.0));
            
            self.circlepoints = (
                (0.000000, 1.000000), (-0.195090, 0.980785), (-0.382683, 0.923880), (-0.555570, 0.831470), 
                (-0.707107, 0.707107), (-0.831470, 0.555570), (-0.923880, 0.382683), (-0.980785, 0.195090), 
                (-1.000000, 0.000000), (-0.980785, -0.195090), (-0.923880, -0.382683), (-0.831470, -0.555570), 
                (-0.707107, -0.707107), (-0.555570, -0.831470), (-0.382683, -0.923880), (-0.195090, -0.980785), 
                (0.000000, -1.000000), (0.195091, -0.980785), (0.382684, -0.923879), (0.555571, -0.831469), 
                (0.707107, -0.707106), (0.831470, -0.555570), (0.923880, -0.382683), (0.980785, -0.195089), 
                (1.000000, 0.000001), (0.980785, 0.195091), (0.923879, 0.382684), (0.831469, 0.555571), 
                (0.707106, 0.707108), (0.555569, 0.831470), (0.382682, 0.923880), (0.195089, 0.980786))
        
        if self.text != 'NONE':
            if not hasattr(self, '_handle'):
                self._handle = context.space_data.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
                
            self.offset = (30, -37)
            
            self.backcolor = Color((1.0, 1.0, 1.0)) - context.user_preferences.themes['Default'].view_3d.space.text_hi
            
            self.rectpoints = (
                (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        
        if self.slider != 'NONE':
            if not hasattr(self, '_handle'):
                self._handle = context.space_data.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
                
            if self.slider == 'LARGE':
                self.sliderheight = 16
                self.sliderwidth = 180
            elif self.slider == 'MEDIUM':
                self.sliderheight = 8
                self.sliderwidth = 80
            else:
                self.sliderheight = 3
                self.sliderwidth = 60
            
            if not hasattr(self, 'offset'):
                self.offset = (30, -37)
            
            if not hasattr(self, 'backcolor'):
                self.backcolor = Color((1.0, 1.0, 1.0)) - context.user_preferences.themes['Default'].view_3d.space.text_hi
            
            self.frontcolor = context.user_preferences.themes['Default'].view_3d.space.text_hi
            
            if not hasattr(self, 'rectpoints'):
                self.rectpoints = (
                    (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        
        # enter modal operation
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(BrushValuesQuickSet)
    
    cfg = bpy.context.window_manager.keyconfigs.addon
    if not cfg.keymaps.__contains__('Sculpt'):
        cfg.keymaps.new('Sculpt', space_type='EMPTY', region_type='WINDOW')
    kmi = cfg.keymaps['Sculpt'].keymap_items
    kmi.new('brush.modal_quickset', 'RIGHTMOUSE', 'PRESS')


def unregister():
    bpy.utils.unregister_class(BrushValuesQuickSet)
    
    cfg = bpy.context.window_manager.keyconfigs.addon
    if cfg.keymaps.__contains__('Sculpt'):
        for kmi in cfg.keymaps['Sculpt'].keymap_items:
            if kmi.idname == 'brush.modal_quickset':
                cfg.keymaps['Sculpt'].keymap_items.remove(kmi)
                break
