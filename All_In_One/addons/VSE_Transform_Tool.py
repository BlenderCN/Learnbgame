bl_info = {
    "name": "VSE Transform tool",
    "description": "",
    "author": "kgeogeo & DoubleZ",
    "version": (1, 0),
    "blender": (2, 6, 5),
    "wiki_url": "",
    "tracker_url":"",
    "category": "Learnbgame"
}

import bpy
import bgl
import blf
from mathutils import *
from math import *
from bpy_extras import view3d_utils
from bpy_extras import image_utils
from bpy.props import BoolProperty, IntProperty, FloatProperty, IntVectorProperty, StringProperty, CollectionProperty

######################################  add transform channel #############################################################################
class TF_Add_Transform(bpy.types.Operator):
    bl_idname = "sequencer.tf_add_transform"
    bl_label = "Add Transform Effect"

    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR'
                
    def execute(self, context):   
        selection = [seq for seq in context.scene.sequence_editor.sequences if seq.select and seq.type not in ['SOUND','TRANSFORM']]
        
        fc = context.scene.frame_current
        lower = 1000
        
        lower_seq = -1
        for seq in context.scene.sequence_editor.sequences:
            if seq.channel < lower and seq.frame_start <= fc and (seq.frame_start + seq.frame_final_duration) >= fc:
                lower = seq.channel
                lower_seq = seq
                
        for seq in selection:            
            bpy.ops.sequencer.select_all(action='DESELECT')
            context.scene.sequence_editor.active_strip = seq
            bpy.ops.sequencer.effect_strip_add(type = "TRANSFORM")
            active_seq = context.scene.sequence_editor.active_strip
            active_seq.name = "[TR]-%s" % seq.name
            seq.mute = True           
            active_seq.blend_alpha = seq.blend_alpha
            
            if seq == lower_seq:
                active_seq.blend_type = seq.blend_type
                seq.blend_alpha = 1    
            else:
                active_seq.blend_type = 'ALPHA_OVER'  
            if seq.type in ['MOVIE','IMAGE']:
                if not seq.use_crop:
                    seq.use_crop = True 
                    seq.crop.min_x = seq.crop.min_y = seq.crop.max_x = seq.crop.max_y = 0
                                       
                if seq.use_translation:
                    len_crop_x = seq.elements[0].orig_width - (seq.crop.min_x + seq.crop.max_x)
                    len_crop_y = seq.elements[0].orig_height - (seq.crop.min_y + seq.crop.max_y)
                    res_x = context.scene.render.resolution_x
                    res_y = context.scene.render.resolution_y
                    ratio_x = len_crop_x/res_x
                    ratio_y = len_crop_y/res_y
                    if ratio_x > 1:
                        ratio_y *= 1/ratio_x
                    if ratio_y > 1:
                        ratio_x *= 1/ratio_y    
                    active_seq.scale_start_x = ratio_x
                    active_seq.scale_start_y = ratio_y
  
                    active_seq.translate_start_x = set_pos_x(active_seq, seq.transform.offset_x + len_crop_x/2 - context.scene.render.resolution_x/2)
                    active_seq.translate_start_y = set_pos_x(active_seq, seq.transform.offset_y + len_crop_y/2 - context.scene.render.resolution_y/2)
                    seq.use_translation = False
                else:
                    crop_scale(active_seq,1)
                                                           
        return {'FINISHED'}

######################################  Draw code for ratote scale    ####################################################
def draw_callback_px_point(self, context):
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 0.5, 0.0, 1.0)

    bgl.glLineStipple(4, 0x5555) 
    bgl.glEnable(bgl.GL_LINE_STIPPLE)
      
    bgl.glPushMatrix()
    bgl.glTranslatef(self.center_area.x, self.center_area.y,0)
    bgl.glBegin(bgl.GL_LINES)
    bgl.glVertex2f(0,0)
    bgl.glVertex2f(self.vec_act.x, self.vec_act.y)
    bgl.glEnd()
    bgl.glPopMatrix()    
    
    bgl.glDisable(bgl.GL_LINE_STIPPLE)
    
    bgl.glLineWidth(3)
    
    self.vec_act
    vx = Vector((1,0))
    bgl.glPushMatrix()
    bgl.glTranslatef(self.center_area.x+self.vec_act.x, self.center_area.y+self.vec_act.y,0)
    if self.bl_idname == 'SEQUENCER_OT_tf_scale':
        bgl.glRotatef(degrees(self.vec_act.angle_signed(vx)),0,0,1)
    if self.bl_idname == 'SEQUENCER_OT_tf_rotation':
        bgl.glRotatef(degrees(self.vec_act.angle_signed(vx))+90,0,0,1)
    bgl.glBegin(bgl.GL_LINES)
    bgl.glVertex2f(5,0)
    bgl.glVertex2f(15, 0)
    bgl.glVertex2f(15, 0)
    bgl.glVertex2f(10, -7)
    bgl.glVertex2f(15, 0)
    bgl.glVertex2f(10, 7)
    
    bgl.glVertex2f(-5,0)
    bgl.glVertex2f(-15, 0)
    bgl.glVertex2f(-15, 0)
    bgl.glVertex2f(-10, -7)
    bgl.glVertex2f(-15, 0)
    bgl.glVertex2f(-10, 7)
    bgl.glEnd()
    bgl.glPopMatrix()
    
    bgl.glLineWidth(1)
    
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

######################################  Draw code for the axis    ####################################################
def draw_callback_draw_axes(self, context,angle):
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineWidth(2)
    
    bgl.glPushMatrix()
    bgl.glTranslatef(self.center_area.x, self.center_area.y,0)
    bgl.glRotatef(angle,0,0,1)
    
    bgl.glBegin(bgl.GL_LINES)
    bgl.glColor4f(1.0, 0.0, 0.0, 0.2 * self.choose_axe + self.axe_x * 0.8)
    bgl.glVertex2f(-10000,0)   
    bgl.glVertex2f(10000,0)   
    bgl.glColor4f(0.0, 1.0, 0.0, 0.2 * self.choose_axe + self.axe_y * 0.8)
    bgl.glVertex2f(0, -10000)   
    bgl.glVertex2f(0, 10000)
    bgl.glEnd()
    
    bgl.glPopMatrix()
            
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
######################################  Input decode function    ####################################################
def func_key_val(self, key, value):
    key_list = ['NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_PERIOD', 'PERIOD']
        
    if key in  key_list and value == 'PRESS':
        if key in ['NUMPAD_PERIOD', 'PERIOD']:
            c = '.' if self.key_val.count('.') == 0 else ''    
        else:
            c = key[7]
        self.key_val += c
                        
    if key in ['NUMPAD_MINUS', 'MINUS'] and value == 'PRESS':
        self.key_val = self.key_val.replace('+','-') if self.key_val[0] == '+' else self.key_val.replace('-','+')
            
######################################  Constraint axis function    ####################################################
def func_contraint_axis(self, context, key, value, angle):                                
    if len(self.tab)>1:
        angle = 0
    if key in ['X','Y']:
        if self._handle_axes == None:
            args = (self, context,angle)
            self._handle_axes = bpy.types.SpaceSequenceEditor.draw_handler_add(draw_callback_draw_axes, args, 'PREVIEW', 'POST_PIXEL')        
        if key == 'X' and value == 'PRESS':
            if self.axe_x == True and self.axe_y == True:
                self.axe_y = False
            elif self.axe_x == True and self.axe_y == False:
                self.axe_y = True
            elif self.axe_x == False and self.axe_y == True:
                self.axe_y = False
                self.axe_x = True   
        
        if key == 'Y' and value == 'PRESS':
            if self.axe_x == True and self.axe_y == True:
                self.axe_x = False
            elif self.axe_x == False and self.axe_y == True:
                self.axe_x = True
            elif self.axe_x == True and self.axe_y == False:
                self.axe_y = True
                self.axe_x = False 
        
        if self.axe_x and self.axe_y:
            if self._handle_axes:
                bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_axes, 'PREVIEW')  
                self._handle_axes = None 
                
######################################  chose axis with MMB function    ####################################################
def func_contraint_axis_mmb(self, context, key, value, angle): 
    if len(self.tab)>1:
        angle = 0
    if key == 'MIDDLEMOUSE' :
        if value == 'PRESS' :
            if self._handle_axes == None:
                args = (self, context, angle)
                self._handle_axes = bpy.types.SpaceSequenceEditor.draw_handler_add(draw_callback_draw_axes, args, 'PREVIEW', 'POST_PIXEL')
            self.choose_axe = True
            self.pos_clic = self.pos_mouse
        if value == 'RELEASE' :
            self.choose_axe = False
            if self.pos_clic == self.pos_mouse:
                self.axe_x = self.axe_y = True
                if self._handle_axes:
                    bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_axes, 'PREVIEW')  
                    self._handle_axes = None
    if self.choose_axe :
        vec_axe_z = Vector((0,0,1))
        vec_axe_x = Vector((1,0,0))
        vec_axe_x.rotate(Quaternion(vec_axe_z, radians(angle)))
        vec_axe_x = vec_axe_x.to_2d()
        vec_axe_y = Vector((0,1,0))
        vec_axe_y.rotate(Quaternion(vec_axe_z,radians(angle)))
        vec_axe_y = vec_axe_y.to_2d()
        
        ang_x = degrees(vec_axe_x.angle(self.vec_act))
        ang_y = degrees(vec_axe_y.angle(self.vec_act))
        
        if ang_x > 90:
            ang_x = 180 - ang_x
        if ang_y > 90:
            ang_y = 180 - ang_y   
            
        if ang_x < ang_y:
            self.axe_x = True
            self.axe_y = False
        else :
            self.axe_x = False
            self.axe_y = True                              
######################################  Scale ##########################################################################
class TF_Scale(bpy.types.Operator):
    bl_idname = "sequencer.tf_scale"
    bl_label = "Transform Scale"

    axe_x = True
    axe_y = True
    choose_axe = False
    
    first_mouse = Vector((0,0))
    pos_clic = Vector((0,0))
    pos_mouse = Vector((0,0))
    
    tab_init = []
    tab_init_t = []
    tab = []

    center_area = Vector((0,0))
    center_real = Vector((0,0))
    vec_init = Vector((0,0))
    vec_act = Vector((0,0))
    
    key_val = '+0'
    key_period = False
    key_period_val = 1  
    
    _handle_line = None
    _handle_axes = None

    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            if context.scene.sequence_editor.active_strip:
                if context.scene.sequence_editor.active_strip.type == 'TRANSFORM':
                    ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR' and context.region.type == 'PREVIEW'

    def modal(self, context, event):
        context.area.tag_redraw()
        
        if self.tab:
            self.pos_mouse = Vector((event.mouse_region_x,event.mouse_region_y))
            self.vec_act = self.pos_mouse - self.center_area                 
            diff = self.vec_act.length / self.vec_init.length
            
            func_contraint_axis_mmb(self, context, event.type, event.value, self.sign_rot*context.scene.sequence_editor.active_strip.rotation_start)

            func_key_val(self, event.type, event.value)            
            if self.key_val != '+0':
                diff = abs(float(self.key_val))

            func_contraint_axis(self, context, event.type, event.value, self.sign_rot*context.scene.sequence_editor.active_strip.rotation_start)
                    
            diff_x = diff if self.axe_x else 1        
            
            diff_y = diff if self.axe_y else 1                           
    
            precision = 1 if event.ctrl else 5
                
            info_x = round(diff_x, precision)
            info_y = round(diff_y, precision)
            if not self.axe_x:
                context.area.header_text_set("Scale: %.4f along local Y" % info_y)#
            if not self.axe_y:
                context.area.header_text_set("Scale: %.4f along local X" % info_x)#
            if self.axe_x and self.axe_y :
                context.area.header_text_set("Scale X:%.4f Y: %.4f" % (info_x, info_y))#
               
            for seq, init_s, init_t in zip(self.tab, self.tab_init, self.tab_init_t):
                seq.scale_start_x =  init_s[0] * round(diff_x, precision)
                seq.scale_start_y =  init_s[1] * round(diff_y, precision)
                
                sign_x = -1 if seq.use_flip_x else 1
                sign_y = -1 if seq.use_flip_y else 1
                if context.scene.seq_pivot_type in ['0','3']:
                    seq.translate_start_x = set_pos_x(seq, (init_t[0] - sign_x*self.center_real.x) * round(diff_x, precision) + sign_x*self.center_real.x)
                    seq.translate_start_y = set_pos_y(seq, (init_t[1] - sign_y*self.center_real.y) * round(diff_y, precision) + sign_y*self.center_real.y)
                
                if context.scene.seq_pivot_type == '2':                    
                    fac = get_fac() 
                    center_c2d = Vector((sign_x*context.scene.seq_cursor2d_loc[0],sign_y*context.scene.seq_cursor2d_loc[1]))/fac                    
                    seq.translate_start_x = set_pos_x(seq, (init_t[0] - center_c2d.x) * round(diff_x, precision) + center_c2d.x)
                    seq.translate_start_y = set_pos_y(seq, (init_t[1] - center_c2d.y) * round(diff_y, precision) + center_c2d.y)
                    
        if event.type == 'LEFTMOUSE' or event.type == 'RET' or event.type == 'NUMPAD_ENTER' or not self.tab:           
            bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_line, 'PREVIEW')
            if self._handle_axes:
                bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_axes, 'PREVIEW')
            context.area.header_text_set()
            return {'FINISHED'}
              
        if event.type == 'ESC' or event.type == 'RIGHTMOUSE':
            for seq, init_s, init_t in zip(self.tab, self.tab_init, self.tab_init_t):
                seq.scale_start_x = init_s[0]
                seq.scale_start_y = init_s[1]
                seq.translate_start_x = set_pos_x(seq, init_t[0])
                seq.translate_start_y = set_pos_y(seq, init_t[1])
     
            bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_line, 'PREVIEW')
            if self._handle_axes:
                bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_axes, 'PREVIEW')
            context.area.header_text_set()
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
                
    def invoke(self, context, event):         
        
        if event.alt :
            for seq in context.scene.sequence_editor.sequences:
                if seq.select and seq.type == 'TRANSFORM':
                    if seq.input_1.type in ['MOVIE','IMAGE']:
                        crop_scale(seq,1) 
                    else:
                        seq.scale_start_x = 1
                        seq.scale_start_y = 1
            ret = 'FINISHED'
        else:  
            fac = get_fac() 
            self.tab_init = []
            self.tab_init_t = []
            self.tab = []
            self.center_real = Vector((0,0))
            self.center_area = Vector((0,0))
            key_val = '+0'
            x = 0
            
            for seq in context.scene.sequence_editor.sequences:
                if seq.select and seq.type == 'TRANSFORM':
                    self.tab_init.append([seq.scale_start_x,seq.scale_start_y])
                    self.tab_init_t.append([get_pos_x(seq),get_pos_y(seq)])
                    self.tab.append(seq)                    
                    sign_x = -1 if seq.use_flip_x else 1
                    sign_y = -1 if seq.use_flip_y else 1
                    self.sign_rot = sign_x*sign_y
                    self.center_real += Vector((sign_x*get_pos_x(seq), sign_y*get_pos_y(seq)))
                    self.center_area += Vector((sign_x*get_pos_x(seq), sign_y*get_pos_y(seq)))
                    x += 1
            if self.tab:        
                self.center_real /= x
                if context.scene.seq_pivot_type == '2':                   
                    self.center_area = Vector(context.region.view2d.view_to_region(context.scene.seq_cursor2d_loc[0],context.scene.seq_cursor2d_loc[1]))
                elif context.scene.seq_pivot_type == '3':
                    act_seq = context.scene.sequence_editor.active_strip
                    sign_x = -1 if act_seq.use_flip_x else 1
                    sign_y = -1 if act_seq.use_flip_y else 1
                    self.center_real = Vector((sign_x*get_pos_x(act_seq), sign_y*get_pos_y(act_seq)))
                    self.center_area = Vector(context.region.view2d.view_to_region(sign_x*get_pos_x(act_seq)*fac,sign_y*get_pos_y(act_seq)*fac))
                else:
                    self.center_area /= x    
                    self.center_area = Vector(context.region.view2d.view_to_region(self.center_area.x*fac, self.center_area.y*fac,clip=False))
                self.vec_init = Vector((event.mouse_region_x, event.mouse_region_y)) - self.center_area  
                
            args = (self, context)
            self._handle_line = bpy.types.SpaceSequenceEditor.draw_handler_add(draw_callback_px_point, args, 'PREVIEW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            ret = 'RUNNING_MODAL'                           
        return {ret}

######################################  Rotation ##########################################################################                
class TF_Rotation(bpy.types.Operator):
    bl_idname = "sequencer.tf_rotation"
    bl_label = "Transform Rotation"
    
    first_mouse = Vector((0,0))
    tab_init = []
    tab_init_t = []
    tab = []
    
    center_area = Vector((0,0))
    center_real = Vector((0,0))
    vec_init = Vector((0,0))
    vec_act = Vector((0,0))
    
    key_val = '+0'
    key_period = False
    key_period_val = 1       
                            
    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            if context.scene.sequence_editor.active_strip:
                if context.scene.sequence_editor.active_strip.type == 'TRANSFORM':
                    ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR' and context.region.type == 'PREVIEW'

    def modal(self, context, event):
        context.area.tag_redraw()
                
        if self.tab:
            self.vec_act = Vector((event.mouse_region_x, event.mouse_region_y)) - self.center_area  
            rot =  degrees(-self.vec_init.angle_signed(self.vec_act))

            if event.ctrl:
                rot -= rot % 5
            
            func_key_val(self, event.type, event.value)            
            if self.key_val != '+0':
                rot = float(self.key_val) 
                
            for seq, init_rot, init_t in zip(self.tab, self.tab_init, self.tab_init_t):
                if init_rot <-180:
                    init_rot = 360 + init_rot
                if init_rot > 180:
                    init_rot = -360 + init_rot
                sign_x = -1 if seq.use_flip_x else 1
                sign_y = -1 if seq.use_flip_y else 1      
                
                seq.rotation_start = init_rot + sign_x*sign_y*rot
                
                if context.scene.seq_pivot_type in ['0','3']:                    
                    np = rotate_point(Vector((init_t[0], init_t[1])) - Vector((sign_x*self.center_real.x,sign_y*self.center_real.y)), sign_x*sign_y*radians(rot))
                    seq.translate_start_x = set_pos_x(seq, np.x + sign_x*self.center_real.x)
                    seq.translate_start_y = set_pos_y(seq, np.y + sign_y*self.center_real.y)
                
                if context.scene.seq_pivot_type == '2':                    
                    fac = get_fac()
                    center_c2d = Vector((sign_x*context.scene.seq_cursor2d_loc[0],sign_y*context.scene.seq_cursor2d_loc[1]))/fac                    
                    np = rotate_point(Vector((init_t[0], init_t[1])) - center_c2d, sign_x*sign_y*radians(rot))
                    seq.translate_start_x = set_pos_x(seq, np.x + center_c2d.x)
                    seq.translate_start_y = set_pos_y(seq, np.y + center_c2d.y) 
                    
            info_rot = (rot)
            context.area.header_text_set("Rotation %.4f " % info_rot)
                        
        if event.type == 'LEFTMOUSE' or event.type == 'RET' or event.type == 'NUMPAD_ENTER' or not self.tab:
            bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_line, 'PREVIEW')
            context.area.header_text_set()
            return {'FINISHED'}
        
        if event.type == 'ESC' or event.type == 'RIGHTMOUSE':
            for seq, init_rot, init_t in zip(self.tab, self.tab_init, self.tab_init_t):
                seq.rotation_start = init_rot
                seq.translate_start_x = set_pos_x(seq, init_t[0])
                seq.translate_start_y = set_pos_y(seq, init_t[1])
            bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_line, 'PREVIEW')
            context.area.header_text_set()
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
                
    def invoke(self, context, event):   
        
        
        if event.alt :
            for seq in context.scene.sequence_editor.sequences:
                if seq.select and seq.type == 'TRANSFORM':
                    seq.rotation_start = 0.0
            ret = 'FINISHED'
        else:
            
            fac = get_fac()
            self.tab_init = []
            self.tab = []
            self.tab_init_t = []
            self.center_real = Vector((0,0))
            self.center_area = Vector((0,0))
            self.key_val = '+0'
            x = 0
            
            for seq in context.scene.sequence_editor.sequences:
                if seq.select and seq.type == 'TRANSFORM':
                    self.tab_init.append(seq.rotation_start)
                    self.tab_init_t.append([get_pos_x(seq),get_pos_y(seq)])
                    self.tab.append(seq)
                    
                    sign_x = -1 if seq.use_flip_x else 1
                    sign_y = -1 if seq.use_flip_y else 1
                    self.center_real += Vector((sign_x*get_pos_x(seq), sign_y*get_pos_y(seq)))
                    self.center_area += Vector((sign_x*get_pos_x(seq), sign_y*get_pos_y(seq)))
                    x += 1
                    
            if self.tab:
                self.center_real /= x           
                if context.scene.seq_pivot_type == '2':
                    self.center_area = Vector(context.region.view2d.view_to_region(context.scene.seq_cursor2d_loc[0],context.scene.seq_cursor2d_loc[1]))
                elif context.scene.seq_pivot_type == '3':
                    act_seq = context.scene.sequence_editor.active_strip
                    sign_x = -1 if act_seq.use_flip_x else 1
                    sign_y = -1 if act_seq.use_flip_y else 1
                    self.center_real = Vector((sign_x*get_pos_x(act_seq), sign_y*get_pos_y(act_seq)))
                    self.center_area = Vector(context.region.view2d.view_to_region(sign_x*get_pos_x(act_seq)*fac,sign_y*get_pos_y(act_seq)*fac))    
                else:
                    self.center_area /= x
                    self.center_area = Vector(context.region.view2d.view_to_region(self.center_area.x*fac,self.center_area.y*fac,clip=False))   
                self.vec_init = Vector((event.mouse_region_x, event.mouse_region_y)) - self.center_area
            args = (self, context)
            self._handle_line = bpy.types.SpaceSequenceEditor.draw_handler_add(draw_callback_px_point, args, 'PREVIEW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            ret = 'RUNNING_MODAL'    
                        
        return {ret}

######################################  Position ##########################################################################
def view_zoom_preview():
    width = bpy.context.region.width
    height = bpy.context.region.height
    rv1 = bpy.context.region.view2d.region_to_view(0,0)
    rv2 = bpy.context.region.view2d.region_to_view(width-1,height-1)
    zoom = (1/(width/(rv2[0]-rv1[0])))/get_fac()
    return zoom

class TF_Position(bpy.types.Operator):
    bl_idname = "sequencer.tf_position"
    bl_label = "Transform Position"
    
    axe_x = True
    axe_y = True
    choose_axe = False
    
    first_mouse = Vector((0,0))
    pos_clic = Vector((0,0))
    pos_mouse = Vector((0,0))
    center_area = Vector((0,0))
    vec_act = Vector((0,0))
    
    tab_init = []
    tab = []

    key_val = '+0'
    key_period = False
    key_period_val = 1
    
    _handle_axes = None
    
    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            if context.scene.sequence_editor.active_strip:
                if context.scene.sequence_editor.active_strip.type == 'TRANSFORM':
                    ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR' and context.region.type == 'PREVIEW'

    def modal(self, context, event):
        if self.tab:                                   
            self.pos_mouse = Vector((event.mouse_region_x,event.mouse_region_y))
            self.vec_act = self.pos_mouse  - self.center_area
            vec_act_fm = self.pos_mouse - self.first_mouse
            
            func_contraint_axis_mmb(self, context, event.type, event.value, 0)
    
            func_key_val(self, event.type, event.value)        
            if self.key_val != '+0' and (not self.axe_x or not self.axe_y):
                    vec_act_fm = Vector((float(self.key_val) / view_zoom_preview(), float(self.key_val) / view_zoom_preview()))            
            
            func_contraint_axis(self, context, event.type, event.value, 0)
                    
            if event.shift:
                vec_act_fm *= 0.1
                
            precision = -1 if event.ctrl else 5
            
            info_x = round(vec_act_fm.x * view_zoom_preview(), precision)
            info_y = round(vec_act_fm.y * view_zoom_preview(), precision)
            if not self.axe_x:
                vec_act_fm  = Vector((0, vec_act_fm.y))
                context.area.header_text_set("D: %.4f along global Y" % info_y)
            if not self.axe_y:
                vec_act_fm = Vector((vec_act_fm.x, 0))
                context.area.header_text_set("D: %.4f along global X" % info_x)
            if self.axe_x and self.axe_y :
                context.area.header_text_set("Dx: %.4f Dy: %.4f" % (info_x, info_y))
                    
            for seq, init_g in zip(self.tab, self.tab_init):               
                    sign_x = sign_y = 1
                    if seq.use_flip_x:
                        sign_x = -1 
                    if seq.use_flip_y:
                        sign_y = -1 
                              
                    seq.translate_start_x = set_pos_x(seq, init_g[0] + round(sign_x*vec_act_fm.x * view_zoom_preview(), precision))            
                    seq.translate_start_y = set_pos_y(seq, init_g[1] + round(sign_y*vec_act_fm.y * view_zoom_preview(), precision)) 
                    
        if event.type == 'LEFTMOUSE' or event.type == 'RET' or event.type == 'NUMPAD_ENTER' or not self.tab:
            if self._handle_axes:
                bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_axes, 'PREVIEW')
            context.area.header_text_set()
            return {'FINISHED'}
        
        if event.type == 'ESC' or event.type == 'RIGHTMOUSE':
            if self._handle_axes:
                bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_axes, 'PREVIEW')
            context.area.header_text_set()
            for seq, init_g in zip(self.tab, self.tab_init):
                seq.translate_start_x = set_pos_x(seq, init_g[0])
                seq.translate_start_y = set_pos_y(seq, init_g[1])
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
                
    def invoke(self, context, event):   
              
        if event.alt :
            for seq in context.scene.sequence_editor.sequences:
                if seq.select and seq.type == 'TRANSFORM':
                    seq.translate_start_x = 0
                    seq.translate_start_y = 0
            ret = 'FINISHED'
        else:    
            self.first_mouse.x = event.mouse_region_x
            self.first_mouse.y = event.mouse_region_y            
            self.key_val = '+0'
            fac = get_fac()
            self.tab = []
            self.tab_init = []
            self.center_area = Vector((0,0))
            x = 0
            for seq in context.scene.sequence_editor.sequences:
                if seq.select and seq.type == 'TRANSFORM': 
                    self.tab_init.append([get_pos_x(seq),get_pos_y(seq)])
                    self.tab.append(seq)
                    sign_x = -1 if seq.use_flip_x else 1
                    sign_y = -1 if seq.use_flip_y else 1
                    self.center_area += Vector((sign_x*get_pos_x(seq), sign_y*get_pos_y(seq)))             
                    x += 1
                    
            if self.tab:
                self.center_area /= x           
                self.center_area = Vector(context.region.view2d.view_to_region(self.center_area.x*fac, self.center_area.y*fac,clip=False))  
            context.window_manager.modal_handler_add(self)
            ret = 'RUNNING_MODAL'    
        
        return {ret}

def get_pos_x(seq):
    if seq.translation_unit == 'PERCENT':
        pos = seq.translate_start_x*bpy.context.scene.render.resolution_x/100
    else:
        pos = seq.translate_start_x    
    return pos

def set_pos_x(seq,pos):
    if seq.translation_unit == 'PERCENT':
        pos = pos*100/bpy.context.scene.render.resolution_x
    return pos  

def get_pos_y(seq):
    if seq.translation_unit == 'PERCENT':
        pos = seq.translate_start_y*bpy.context.scene.render.resolution_y/100
    else:
        pos = seq.translate_start_y    
    return pos

def set_pos_y(seq,pos):
    if seq.translation_unit == 'PERCENT':
        pos = pos*100/bpy.context.scene.render.resolution_y
    return pos 

def get_fac():
    if bpy.context.space_data.proxy_render_size == 'SCENE':
        fac = bpy.context.scene.render.resolution_percentage/100
    else:
        fac = 1    
    return fac
      
##################################### Alpha func ##########################################################
def draw_callback_px_alpha(self, context):    
    w = context.region.width
    h = context.region.height
    x = self.first_mouse.x
    y = self.first_mouse.y + 15 + self.pos.y
    
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineWidth(1)
    
    bgl.glColor4f(0, 1, 1, 1)
    
    bgl.glPushMatrix()    
    bgl.glTranslatef(x - w/10 + self.pos.x,y,0)
    font_id = 0 
    blf.position(font_id, 0, 10, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, str(self.fac))
    bgl.glPopMatrix()
    
    bgl.glPushMatrix()   
    bgl.glTranslatef(x,y,0)
    bgl.glBegin(bgl.GL_LINE_LOOP)
    bgl.glVertex2f(-w/10, 0)
    bgl.glVertex2f(w/10, 0)   
    bgl.glEnd()
    bgl.glPopMatrix()

    bgl.glEnable(bgl.GL_POINT_SMOOTH)
    bgl.glPointSize(10)

    bgl.glPushMatrix()    
    bgl.glTranslatef(x,y,0)
    bgl.glBegin(bgl.GL_POINTS)
    bgl.glVertex2f(-w/10, 0)
    bgl.glVertex2f(w/10, 0)   
    bgl.glEnd()
    bgl.glPopMatrix()
    
    bgl.glColor4f(1, 0, 0, 1)
    bgl.glPushMatrix()    
    bgl.glTranslatef(x - w/10 + self.pos.x,y,0)
    bgl.glBegin(bgl.GL_POINTS)
    bgl.glVertex2f(0, 0) 
    bgl.glEnd()
    bgl.glPopMatrix()
    
    bgl.glDisable(bgl.GL_POINT_SMOOTH)
    bgl.glPointSize(1)
                
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

class TF_Alpha(bpy.types.Operator):
    bl_idname = "sequencer.tf_draw_alpha"
    bl_label = "Draw the selection"
    quad_list = []
    first_mouse = Vector((0,0))
    pos = Vector((0,0))
    alpha_init = 0
    fac = 0
    key_val = '+0'
    
    _handle_alpha = None

    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            if context.scene.sequence_editor.active_strip:
                if context.scene.sequence_editor.active_strip.type == 'TRANSFORM':
                    if context.scene.sequence_editor.active_strip.select:
                        ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR' and context.region.type == 'PREVIEW'
        
    def modal(self, context, event):
        context.area.tag_redraw()
        w = context.region.width
        self.pos = Vector((event.mouse_region_x + self.alpha_init * w/5,event.mouse_region_y)) - self.first_mouse
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.x > w/5:
            self.pos.x = w/5
        self.fac = self.pos.x / (w/5)
        
        func_key_val(self, event.type, event.value)        
        if self.key_val != '+0':
            self.fac = abs(float(self.key_val))
            self.pos.x =  self.fac*(w/5)    
                    
        precision = 1 if event.ctrl else 3
        
        self.fac = round(self.fac,precision)    
        context.scene.sequence_editor.active_strip.blend_alpha = self.fac    
        
        if event.type == 'LEFTMOUSE' or event.type == 'RET' or event.type == 'NUMPAD_ENTER':
            bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_alpha, 'PREVIEW')                
            return {'FINISHED'}
        
        if event.type == 'ESC' or event.type == 'RIGHTMOUSE':
            context.scene.sequence_editor.active_strip.blend_alpha = self.alpha_init
            bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_alpha, 'PREVIEW')                
            return {'FINISHED'}
         
        return {'RUNNING_MODAL'}   
                
    def invoke(self, context, event): 
        if event.alt :
            for seq in context.scene.sequence_editor.sequences:
                if seq.select and seq.type == 'TRANSFORM':
                    seq.blend_alpha = 1.0
            ret = 'FINISHED'
        else :
            self.first_mouse = Vector((event.mouse_region_x,event.mouse_region_y))
            self.alpha_init = context.scene.sequence_editor.active_strip.blend_alpha 
            self.key_val != '+0'
            
            args = (self, context)
            self._handle_alpha = bpy.types.SpaceSequenceEditor.draw_handler_add(draw_callback_px_alpha, args, 'PREVIEW', 'POST_PIXEL')       
            context.window_manager.modal_handler_add(self)
            ret = 'RUNNING_MODAL'
               
        return {ret}  

######################################   Crop draw Function ########################################
def crop_scale(seq,fac_init):     
    seq_in = seq.input_1
    len_crop_x = seq_in.elements[0].orig_width - (seq_in.crop.min_x + seq_in.crop.max_x)
    len_crop_y = seq_in.elements[0].orig_height - (seq_in.crop.min_y + seq_in.crop.max_y)
    res_x = bpy.context.scene.render.resolution_x
    res_y = bpy.context.scene.render.resolution_y
    ratio_x = len_crop_x/res_x
    ratio_y = len_crop_y/res_y
    ratio_x = 0.00001 if ratio_x == 0 else ratio_x
    ratio_y = 0.00001 if ratio_y == 0 else ratio_y
    if ratio_x > ratio_y:                       
        ratio_y *= fac_init/ratio_x
        ratio_x = fac_init
    else:
        ratio_x *= fac_init/ratio_y 
        ratio_y = fac_init  
         
    seq.scale_start_x = ratio_x
    seq.scale_start_y = ratio_y
    

def draw_callback_px_crop(self, context):
    active_seq = context.scene.sequence_editor.active_strip.input_1
             
    global image_size, origine, vec_bl, vec_tr, vec_ct
    image_fac = 2*image_size/active_seq.elements[0].orig_width
    fac  = active_seq.elements[0].orig_height/active_seq.elements[0].orig_width    
    vec_bl = Vector((origine[0]-image_size + active_seq.crop.min_x*image_fac,origine[1]-image_size*fac + active_seq.crop.min_y*image_fac))
    vec_tr = Vector((origine[0]+image_size - active_seq.crop.max_x*image_fac,origine[1] + image_size*fac - active_seq.crop.max_y*image_fac))
    vec_ct = (vec_bl + (vec_tr- vec_bl)/2)
    
    #Init
    bgl.glEnable(bgl.GL_BLEND)     
    bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
    bgl.glEnable(bgl.GL_TEXTURE_2D)
    bgl.glEnable(bgl.GL_DEPTH_TEST)
    
    #Texture    
    texture1 = self.img.bindcode
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture1[0]);
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)        
    
    bgl.glPushMatrix() 
    bgl.glTranslatef(origine[0],origine[1],0)               
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glTexCoord2d(0,0)
    bgl.glVertex2f(-image_size, -image_size*fac)   
    bgl.glTexCoord2d(0,1)
    bgl.glVertex2f(-image_size , image_size*fac)
    bgl.glTexCoord2d(1,1)
    bgl.glVertex2f(image_size , image_size*fac)
    bgl.glTexCoord2d(1,0)
    bgl.glVertex2f(image_size , -image_size*fac)
    bgl.glEnd()
    
    bgl.glDisable(bgl.GL_TEXTURE_2D)
    
    #Cadre
    bgl.glLineWidth(2)
    bgl.glColor4f(0.0, 1.0, 1.0, 1.0)                        
    
    bgl.glBegin(bgl.GL_LINE_LOOP)
    bgl.glVertex2f(-image_size + active_seq.crop.min_x*image_fac, -image_size*fac + active_seq.crop.min_y*image_fac)   
    bgl.glVertex2f(-image_size + active_seq.crop.min_x*image_fac, image_size*fac - active_seq.crop.max_y*image_fac)
    bgl.glVertex2f(image_size - active_seq.crop.max_x*image_fac, image_size*fac - active_seq.crop.max_y*image_fac)
    bgl.glVertex2f(image_size - active_seq.crop.max_x*image_fac, -image_size*fac + active_seq.crop.min_y*image_fac)
    bgl.glEnd()
    
    #Point
    bgl.glEnable(bgl.GL_POINT_SMOOTH)
    bgl.glPointSize(15)
    
    bgl.glBegin(bgl.GL_POINTS)
    bgl.glVertex2f(-image_size + active_seq.crop.min_x*image_fac, -image_size*fac + active_seq.crop.min_y*image_fac)
    bgl.glVertex2f(image_size - active_seq.crop.max_x*image_fac, image_size*fac - active_seq.crop.max_y*image_fac)
    #bgl.glVertex2f(vec_ct.x-origine[0],vec_ct.y-origine[1])
    bgl.glEnd()
    bgl.glPopMatrix()
    for i in range(4):
        bgl.glPushMatrix()        
        bgl.glTranslatef(vec_ct.x,vec_ct.y,0)
        bgl.glRotatef(i*90,0,0,1)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(0,0)
        bgl.glVertex2f(10, 0)
        bgl.glEnd()
        
        bgl.glPopMatrix()
    
    
    
    bgl.glEnable(bgl.GL_POINT_SMOOTH)
    bgl.glPointSize(1) 
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

#Global variable    
vec_bl = Vector((0,0))
vec_tr = Vector((0,0))
origine = [10000,10000] 
image_size = 200
fframe = 0

class TF_Crop(bpy.types.Operator):
    bl_idname = "sequencer.tf_crop"
    bl_label = "Draw the crop"
    
    _handle_crop = None
    sel_point = 0
    mmb = False
    
    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            if context.scene.sequence_editor.active_strip:
                if context.scene.sequence_editor.active_strip.type == 'TRANSFORM':
                    if context.scene.sequence_editor.active_strip.select:
                        if context.scene.sequence_editor.active_strip.input_1.type in ['MOVIE','IMAGE']:
                            ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR' and context.region.type == 'PREVIEW'
        
    def modal(self, context, event):
        context.area.tag_redraw()
        seq = context.scene.sequence_editor.active_strip 
        active_seq = context.scene.sequence_editor.active_strip.input_1
        global image_size, fframe
        self.pos_mouse = Vector((event.mouse_region_x,event.mouse_region_y))              
        
        if self.enter_modal:
            self.img.reload()
            self.enter_modal = False
        #move fram       
        if event.type in ['RIGHT_ARROW','LEFT_ARROW']:
            if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
                context.scene.frame_current +=1
                fframe = fframe + 1
            if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
                context.scene.frame_current -=1
                fframe = fframe - 1
            if seq.input_1.type == 'MOVIE' and event.value == 'RELEASE':
                self.img.reload()            
            if seq.input_1.type == 'IMAGE' and event.value == 'RELEASE':       
                if len(seq.input_1.elements) == 1:
                    index = 0
                else:                
                    index = context.scene.frame_current - seq.frame_start + seq.input_1.frame_offset_start 
                    if index < seq.input_1.frame_offset_start:
                        index = seq.input_1.frame_offset_start
                    if index > seq.input_1.frame_final_duration + seq.input_1.frame_offset_start - 1:
                        index = seq.input_1.frame_final_duration + seq.input_1.frame_offset_start - 1 
                
                self.img.user_clear()
                bpy.data.images.remove(self.img)                
                name = seq.input_1.elements[index].filename    
                dir = seq.input_1.directory
                fp = dir+name
                self.img = bpy.data.images.load(fp)
        ret = self.img.gl_load(fframe, bgl.GL_NEAREST, bgl.GL_NEAREST)                    
            
        #zoom image
        if event.type in ['WHEELDOWNMOUSE','WHEELUPMOUSE']:
            if event.type =='WHEELDOWNMOUSE':
                image_size -=10
            if event.type =='WHEELUPMOUSE':
                image_size +=10   
        
        #select a corner
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            len_bl = self.pos_mouse - vec_bl
            len_tr = self.pos_mouse - vec_tr
            len_org = self.pos_mouse - vec_ct
            if len_bl.length < 7.5:
                self.sel_point = 1
                self.init_min_x = active_seq.crop.min_x
                self.init_min_y = active_seq.crop.min_y
                
            elif len_tr.length < 7.5:
                self.sel_point = 2
                self.init_max_x = active_seq.crop.max_x
                self.init_max_y = active_seq.crop.max_y
            
            elif len_org.length < 7.5:
                self.sel_point = 3
                self.init_min_x = active_seq.crop.min_x
                self.init_min_y = active_seq.crop.min_y
                self.init_max_x = active_seq.crop.max_x
                self.init_max_y = active_seq.crop.max_y    
            else:
                self.sel_point = 0
            
            #init for scaling the strip according to the crop
            self.first_mouse = Vector((event.mouse_region_x,event.mouse_region_y))            
            self.org_w = active_seq.elements[0].orig_width
            self.org_h = active_seq.elements[0].orig_height
            self.ratio_org = self.org_h/self.org_w
            crop_x = self.org_w - (active_seq.crop.min_x + active_seq.crop.max_x)
            crop_y = self.org_h - (active_seq.crop.min_y + active_seq.crop.max_y)             

            self.fac_init = max(seq.scale_start_x,seq.scale_start_y)
            
        #crop
        if event.type == 'MOUSEMOVE' and self.sel_point != 0:             
            limit = 50
            vec_act = (self.pos_mouse - self.first_mouse)/(2*image_size)
            step_x = self.org_w*vec_act.x
            step_y = self.org_h*vec_act.y/self.ratio_org
            if self.sel_point == 1:
                active_seq.crop.min_x = self.init_min_x + step_x
                active_seq.crop.min_y = self.init_min_y + step_y
            if self.sel_point == 2:
                active_seq.crop.max_x = self.init_max_x - step_x 
                active_seq.crop.max_y = self.init_max_y - step_y
            if self.sel_point == 3:
                active_seq.crop.min_x = self.init_min_x + step_x
                active_seq.crop.min_y = self.init_min_y + step_y
                active_seq.crop.max_x = self.init_max_x - step_x 
                active_seq.crop.max_y = self.init_max_y - step_y     
            
            #scale the strip according to the crop
            crop_scale(seq,self.fac_init)          
            
        #move the image                                
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.sel_point = 0

        if event.type == 'MIDDLEMOUSE' and event.value == 'PRESS':
            self.mmb = True
            self.first_mouse = Vector((event.mouse_region_x,event.mouse_region_y))
            
        if event.type == 'MOUSEMOVE' and self.mmb:
            vec_act = Vector((event.mouse_region_x,event.mouse_region_y)) - self.first_mouse
            global origine
            origine = [origine[0]+vec_act.x,origine[1]+vec_act.y]
            self.first_mouse = Vector((event.mouse_region_x,event.mouse_region_y))
            
        if event.type == 'MIDDLEMOUSE' and event.value == 'RELEASE':
            self.mmb = False
        #keyframe
        if event.type == 'I':
            bpy.ops.sequencer.tf_call_menu('INVOKE_DEFAULT')
        #clear the crop inside the modal
        if event.alt and event.type =='C':
            seq.input_1.crop.min_x = seq.input_1.crop.min_y = 0
            seq.input_1.crop.max_x = seq.input_1.crop.max_y = 0
            crop_scale(seq,max(seq.scale_start_x,seq.scale_start_y))    
        #close                                
        if event.type == 'C' and event.value == 'PRESS':    
            bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_crop, 'PREVIEW')                
            if active_seq.type in ['MOVIE','IMAGE']:
                self.img.user_clear()
                bpy.data.images.remove(self.img)
       
            return {'FINISHED'}
         
        return {'RUNNING_MODAL'}   
                
    def invoke(self, context, event): 
        seq = context.scene.sequence_editor.active_strip
        if event.alt :
            seq.input_1.crop.min_x = seq.input_1.crop.min_y = 0
            seq.input_1.crop.max_x = seq.input_1.crop.max_y = 0
            crop_scale(seq,max(seq.scale_start_x,seq.scale_start_y))
            ret = 'FINISHED'
        else:    
            global origine, fframe
            if origine == [10000,10000]:
                origine = context.region.view2d.view_to_region(0,0,clip=False)
        
            if seq.input_1.type == 'MOVIE':                
                fp = seq.input_1.filepath
                self.img = bpy.data.images.load(fp)
                fframe = -seq.frame_start  + seq.input_1.frame_offset_start + context.scene.frame_current + 1 
                self.enter_modal = True
                
            if seq.input_1.type == 'IMAGE':       
                if len(seq.input_1.elements) == 1:
                    index = 0
                else:                
                    index = context.scene.frame_current - seq.frame_start + seq.input_1.frame_offset_start
                    if index < seq.input_1.frame_offset_start:
                        index = seq.input_1.frame_offset_start
                    if index > seq.input_1.frame_final_duration + seq.input_1.frame_offset_start - 1:
                        index = seq.input_1.frame_final_duration + seq.input_1.frame_offset_start - 1
                                
                name = seq.input_1.elements[index].filename    
                dir = seq.input_1.directory
                fp = dir+name
                self.img = bpy.data.images.load(fp)
                self.enter_modal = False
                
            args = (self, context)
            self._handle_crop = bpy.types.SpaceSequenceEditor.draw_handler_add(draw_callback_px_crop, args, 'PREVIEW', 'POST_PIXEL')         
            context.window_manager.modal_handler_add(self)        
            ret = 'RUNNING_MODAL'
            
        return {ret}
          
######################################   Selection draw Function ########################################
def rotate_point(p, angle):
    s = sin(angle);
    c = cos(angle);    
    v = Vector((p.x * c - p.y * s, p.x * s + p.y * c))         
    return v

def make_quad(seq):
    p = get_fac()
    w = bpy.context.scene.render.resolution_x * p/2
    h = bpy.context.scene.render.resolution_y * p/2
    
    vt = Vector((get_pos_x(seq), get_pos_y(seq)))*p
    sc_x = w*seq.scale_start_x
    sc_y = sc_x if seq.use_uniform_scale else h*seq.scale_start_y
    rot = radians(seq.rotation_start)
    
    p0 = vt + rotate_point(Vector((-sc_x, -sc_y)), rot)
    p1 = vt + rotate_point(Vector((-sc_x, sc_y)), rot)
    p2 = vt + rotate_point(Vector((sc_x, sc_y)), rot)
    p3 = vt + rotate_point(Vector((sc_x, -sc_y)), rot)        

    sign_x = -1 if seq.use_flip_x else 1
    sign_y = -1 if seq.use_flip_y else 1
    
    p0 = Vector((sign_x*p0.x,sign_y*p0.y))
    p1 = Vector((sign_x*p1.x,sign_y*p1.y))
    p2 = Vector((sign_x*p2.x,sign_y*p2.y))
    p3 = Vector((sign_x*p3.x,sign_y*p3.y))
    
    return [p0,p1,p2,p3]

def draw_callback_px_select(self, context):
    bgl.glEnable(bgl.GL_BLEND)
    col_act = context.user_preferences.themes['Default'].view_3d.object_active
    col_sel = context.user_preferences.themes['Default'].view_3d.object_selected
    act_seq = context.scene.sequence_editor.active_strip
    bgl.glLineWidth(4)
    
    for seq, quad in self.quad_list:
        if seq.select:
            bgl.glColor4f(col_sel[0], col_sel[1], col_sel[2], 0.9-self.t/20)
            if seq == context.scene.sequence_editor.active_strip:
                bgl.glColor4f(col_act[0], col_act[1], col_act[2], 0.9-self.t/20)
                
            bgl.glBegin(bgl.GL_LINE_LOOP)
            for vec in quad:
                pos = context.region.view2d.view_to_region(vec.x,vec.y, clip=False)
                bgl.glVertex2i(pos[0], pos[1])   
            bgl.glEnd()
            
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

class TF_Draw_Selection(bpy.types.Operator):
    bl_idname = "sequencer.tf_draw_selection"
    bl_label = "Draw the selection"
    quad_list = []
    
    t = 0
    close = False
    _timer = None
    _handle_select = None
    
    def modal(self, context, event):
        context.area.tag_redraw()
        mb = bpy.context.user_preferences.inputs.select_mouse
 
        if event.type == 'TIMER':
            self.t += 1   
     
        if self.t>20:
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceSequenceEditor.draw_handler_remove(self._handle_select, 'PREVIEW')
                
            return {'FINISHED'}
         
        return {'PASS_THROUGH'}   
                
    def invoke(self, context, event): 
        args = (self, context)
        self._handle_select = bpy.types.SpaceSequenceEditor.draw_handler_add(draw_callback_px_select, args, 'PREVIEW', 'POST_PIXEL')
        self._timer = context.window_manager.event_timer_add(0.01, context.window)          
        context.window_manager.modal_handler_add(self)

        self.quad_list=[]
                
        for seq in reversed(context.scene.sequence_editor.sequences):
            if seq.type == 'TRANSFORM':           
                self.quad_list.append([seq,make_quad(seq)])
                
        return {'RUNNING_MODAL'}
        
######################################   Selection ########################################
class TF_Select(bpy.types.Operator):
    bl_idname = "sequencer.tf_select"
    bl_label = "Select Transform Sequence"
    
    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR' and context.region.type == 'PREVIEW' 
                
    def invoke(self, context, event):
        
        pos = context.region.view2d.region_to_view(event.mouse_region_x,event.mouse_region_y)
        po = Vector((pos[0],pos[1]))
        list_sel = []
        
        fc = context.scene.frame_current
        for seq in reversed(context.scene.sequence_editor.sequences):
            if seq.type == 'TRANSFORM' and not seq.mute:          
                p0,p1,p2,p3 = make_quad(seq)                     
                if not event.type == 'A':
                    if geometry.intersect_point_quad_2d(po, p0, p1, p2, p3) and seq.frame_start <= fc and (seq.frame_start + seq.frame_final_duration) >= fc:
                        list_sel.append(seq)
                        if not event.shift :
                            bpy.ops.sequencer.select_all(action='DESELECT')
                            seq.select = True
                            bpy.context.scene.sequence_editor.active_strip = seq
                            break
                        else :
                            if not seq.select:
                                seq.select = True
                                bpy.context.scene.sequence_editor.active_strip = seq
                                break
                            else:
                                seq.select = False
                                break
        if not list_sel and not event.shift and not event.type == 'A':
            bpy.ops.sequencer.select_all(action='DESELECT')
            
        if event.type == 'A':
            temp_sel = False
            for seq in reversed(context.scene.sequence_editor.sequences):
                if seq.select:
                    temp_sel = True     
                if seq.type == 'TRANSFORM' and seq.frame_start <= fc and (seq.frame_start + seq.frame_final_duration) >= fc:
                    seq.select = True
            if temp_sel == True:
                bpy.ops.sequencer.select_all(action='DESELECT')       
            
        bpy.ops.sequencer.tf_draw_selection('INVOKE_DEFAULT') 
        return {'FINISHED'}
        
########################   Menu Key frame #######################################################
class TF_Call_Menu(bpy.types.Operator):
    bl_idname = "sequencer.tf_call_menu"
    bl_label = "Transform Call Menu"
       
    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR' and context.region.type == 'PREVIEW'
                
    def execute(self, context):   
        bpy.ops.wm.call_menu(name="VSE_MT_Insert_keyframe_Menu")
        return {'FINISHED'}

class TF_Insert_KeyFrame(bpy.types.Operator):
    bl_idname = "sequencer.tf_insert_keyframe"
    bl_label = "Transform Insert KeyFrame"
    
    ch = bpy.props.IntVectorProperty(name="ch",default=(0,0,0,0,0),size=5)
    
    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR'
                
    def execute(self, context):   
        cf = context.scene.frame_current
        
        for seq in context.scene.sequence_editor.sequences:
            if seq.select and seq.type == 'TRANSFORM':
                if self.ch[0] ==1:
                    seq.keyframe_insert(data_path="translate_start_x", frame=cf)
                    seq.keyframe_insert(data_path="translate_start_y", frame=cf)
                if self.ch[1] == 1:
                    seq.keyframe_insert(data_path="rotation_start", frame=cf)
                if self.ch[2] == 1:
                    seq.keyframe_insert(data_path="scale_start_x", frame=cf)
                    seq.keyframe_insert(data_path="scale_start_y", frame=cf)
                if self.ch[3] == 1:
                    seq.keyframe_insert(data_path="blend_alpha", frame=cf)
                if self.ch[4] == 1 and seq.input_1.use_crop:
                    seq.input_1.crop.keyframe_insert(data_path="min_x", frame=cf)
                    seq.input_1.crop.keyframe_insert(data_path="max_x", frame=cf)
                    seq.input_1.crop.keyframe_insert(data_path="min_y", frame=cf)
                    seq.input_1.crop.keyframe_insert(data_path="max_y", frame=cf)    
                
        return {'FINISHED'}

class TF_Menu_Insert_KF(bpy.types.Menu):
    bl_label = "Insert KeyFrame Menu"
    bl_idname = "VSE_MT_Insert_keyframe_Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("sequencer.tf_insert_keyframe",  text="Location").ch = (1,0,0,0,0)
        layout.operator("sequencer.tf_insert_keyframe",  text="Rotation").ch = (0,1,0,0,0)
        layout.operator("sequencer.tf_insert_keyframe", text="Scale").ch = (0,0,1,0,0)
        layout.operator("sequencer.tf_insert_keyframe", text="LocRot").ch = (1,1,0,0,0)
        layout.operator("sequencer.tf_insert_keyframe", text="LocScale").ch =(1,0,1,0,0)
        layout.operator("sequencer.tf_insert_keyframe", text="RotScale").ch = (0,1,1,0,0)
        layout.operator("sequencer.tf_insert_keyframe", text="LocRotScale").ch = (1,1,1,0,0)
        layout.separator()
        layout.operator("sequencer.tf_insert_keyframe", text="Alpha").ch = (0,0,0,1,0)
        layout.separator()
        layout.operator("sequencer.tf_insert_keyframe", text="CropScale").ch = (0,0,1,0,1)
        layout.separator()
        layout.operator("sequencer.tf_insert_keyframe", text="All").ch = (1,1,1,1,1)
####################  Menu select layer #####################################################"
class TF_Call_Menu_Layers(bpy.types.Operator):
    bl_label = "Transform Call Menu Layers"
    bl_idname = "sequencer.tf_call_menu_layers"
       
    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR' and context.region.type == 'PREVIEW'
                
    def invoke(self, context,event):   
        global multi
        global po
                
        pos = context.region.view2d.region_to_view(event.mouse_region_x,event.mouse_region_y)
        po = Vector((pos[0],pos[1]))
        
        multi = True if event.shift else False 
           
        bpy.ops.wm.call_menu(name="VSE_MT_Menu_Layers")
        return {'FINISHED'}

multi = False
po = Vector((0,0))

class TF_Menu_Layers(bpy.types.Menu):
    bl_label = "Select layer menu :"
    bl_idname = "VSE_MT_Menu_Layers"

    global po
    def draw(self, context):
        layout = self.layout
        
        fc = context.scene.frame_current
        
        for seq in reversed(context.scene.sequence_editor.sequences):
            if seq.type == 'TRANSFORM' and not seq.mute:          
                p0,p1,p2,p3 = make_quad(seq)
                if geometry.intersect_point_quad_2d(po, p0, p1, p2, p3) and seq.frame_start <= fc and (seq.frame_start + seq.frame_final_duration) >= fc: 
                    layout.operator("sequencer.select_layers",  text=seq.input_1.name, icon='SEQUENCE' ).name = seq.name

class TF_Select_Layers(bpy.types.Operator):
    bl_label = "Select Layers"
    bl_idname = "sequencer.select_layers"

    name = StringProperty()
    
    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR'
                
    def execute(self, context):
        seq = context.scene.sequence_editor.sequences[self.name]
        if not multi :
            bpy.ops.sequencer.select_all(action='DESELECT')
            seq.select = True
        else :
            seq.select = False if seq.select else True
            
        bpy.context.scene.sequence_editor.active_strip = context.scene.sequence_editor.sequences[self.name]
        bpy.ops.sequencer.tf_draw_selection('INVOKE_DEFAULT') 
        return {'FINISHED'}
##########################  Draw 2d cursor ###################################
def draw_callback_px_2d_cursor(self, context):
    c2d = context.region.view2d.view_to_region(context.scene.seq_cursor2d_loc[0],context.scene.seq_cursor2d_loc[1],clip=False)

    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineWidth(1)
    bgl.glColor4f(0.7, 0.7, 0.7, 1.0)
    bgl.glPushMatrix()          
    bgl.glTranslatef(c2d[0],c2d[1],0)
    bgl.glBegin(bgl.GL_LINES)
    bgl.glVertex2i(0, -15)   
    bgl.glVertex2i(0, -5)    
    bgl.glVertex2i(0, 15)
    bgl.glVertex2i(0, 5)
    bgl.glVertex2i(-15, 0)   
    bgl.glVertex2i(-5, 0)
    bgl.glVertex2i(15, 0)    
    bgl.glVertex2i(5, 0)
    bgl.glEnd()
    
    size = 10
    c = []
    s = []
    for i in range(16):
        c.append(cos(i*pi/8))
        s.append(sin(i*pi/8)) 
    bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
    bgl.glBegin(bgl.GL_LINE_LOOP)
    for i in range(16):
        bgl.glVertex2f(size*c[i], size*s[i])         
    bgl.glEnd()
    
    bgl.glEnable(bgl.GL_LINE_STIPPLE)
    bgl.glLineStipple(4, 0x5555)
    bgl.glColor4f(1.0, 0.0, 0.0, 1.0)
    
    bgl.glBegin(bgl.GL_LINE_LOOP)
    for i in range(16):
        bgl.glVertex2f(size*c[i], size*s[i])         
    bgl.glEnd()
    
    bgl.glPopMatrix()
    
    bgl.glDisable(bgl.GL_LINE_STIPPLE)            
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
##########################  Set the cursor2D location ###################################
class TF_Set_Cursor2D(bpy.types.Operator):
    bl_label = "Set le Cursor2D"
    bl_idname = "sequencer.tf_set_cursor2d"
    
    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR' and context.region.type == 'PREVIEW' and context.scene.seq_pivot_type == '2'
                
    def invoke(self, context, event):
        temp = context.region.view2d.region_to_view(event.mouse_region_x,event.mouse_region_y)
        context.scene.seq_cursor2d_loc = [round(temp[0]),round(temp[1])]
        return {'FINISHED'}    
##########################  Icone    ###################################
def Add_Icon_Pivot_Point(self, context):
    seq = context.scene
    layout = self.layout
    layout.prop(context.scene, "seq_pivot_type", text='', expand=False,  icon_only=True)
        

##########################  Register    ###################################

_handle_2d_cursor = None

def update_seq_cursor2d_loc(self,context):
    context.area.tag_redraw()
        
def update_pivot_point(self,context):
    global _handle_2d_cursor
    
    if context.scene.seq_pivot_type == '2':
        args = (self, context)
        _handle_2d_cursor = bpy.types.SpaceSequenceEditor.draw_handler_add(draw_callback_px_2d_cursor, args, 'PREVIEW', 'POST_PIXEL') 
    else:
        if _handle_2d_cursor:
            bpy.types.SpaceSequenceEditor.draw_handler_remove(_handle_2d_cursor, 'PREVIEW')
            _handle_2d_cursor = None   
    
item_pivot_point = (('0','Median Point','', 'ROTATECENTER', 0),('1','Individual Origins','', 'ROTATECOLLECTION', 1),('2','2D Cursor','', 'CURSOR', 2),('3','Active Strip','', 'ROTACTIVE', 3))  
        
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.seq_cursor2d_loc = IntVectorProperty(name="Scales", description="location of the cursor2d",
                                          subtype = 'XYZ',
                                          default=(50, 50),
                                          size=2,
                                          step=1,
                                          update = update_seq_cursor2d_loc)
    bpy.types.Scene.seq_pivot_type = bpy.props.EnumProperty(name="Pivot Point",default = "1", items=item_pivot_point,update = update_pivot_point)
    bpy.types.SEQUENCER_HT_header.append(Add_Icon_Pivot_Point)
        
    km = bpy.context.window_manager.keyconfigs.default.keymaps['View2D']
    kmi = km.keymap_items.new("sequencer.tf_position", 'G', 'PRESS')
    kmi = km.keymap_items.new("sequencer.tf_position", 'G', 'PRESS', alt=True)
    kmi = km.keymap_items.new("sequencer.tf_scale", 'S', 'PRESS')
    kmi = km.keymap_items.new("sequencer.tf_scale", 'S', 'PRESS',alt=True)
    kmi = km.keymap_items.new("sequencer.tf_rotation", 'R', 'PRESS')
    kmi = km.keymap_items.new("sequencer.tf_rotation", 'R', 'PRESS',alt=True)
    kmi = km.keymap_items.new("sequencer.tf_add_transform", 'T', 'PRESS')
    kmi = km.keymap_items.new("sequencer.tf_call_menu", 'I', 'PRESS')
    kmi = km.keymap_items.new("sequencer.tf_select", 'A', 'PRESS')
    kmi = km.keymap_items.new("sequencer.tf_draw_alpha", 'Q', 'PRESS')
    kmi = km.keymap_items.new("sequencer.tf_draw_alpha", 'Q', 'PRESS', alt=True)
    kmi = km.keymap_items.new("sequencer.tf_crop", 'C', 'PRESS')
    kmi = km.keymap_items.new("sequencer.tf_crop", 'C', 'PRESS', alt=True)
    
    mb = bpy.context.user_preferences.inputs.select_mouse        
    kmi = km.keymap_items.new("sequencer.tf_select", mb + 'MOUSE', 'PRESS')
    kmi = km.keymap_items.new("sequencer.tf_select", mb + 'MOUSE', 'PRESS', shift=True)
    kmi = km.keymap_items.new("sequencer.tf_call_menu_layers", mb + 'MOUSE', 'PRESS', alt=True)
    kmi = km.keymap_items.new("sequencer.tf_call_menu_layers", mb + 'MOUSE', 'PRESS', shift=True, alt=True)
    kmi = km.keymap_items.new("sequencer.tf_set_cursor2d", mb + 'MOUSE', 'PRESS', ctrl=True)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.SEQUENCER_HT_header.remove(Add_Icon_Pivot_Point)
    
    km = bpy.context.window_manager.keyconfigs.default.keymaps['View2D']
    for kmi in (kmi for kmi in km.keymap_items if kmi.idname in {"sequencer.tf_draw_crop", "sequencer.tf_position", "sequencer.tf_scale", "sequencer.tf_rotation", "sequencer.tf_add_transform", "sequencer.tf_call_menu", "sequencer.tf_select", "sequencer.tf_set_cursor2d", }):
            km.keymap_items.remove(kmi)
            
if __name__ == "__main__":
    register()
