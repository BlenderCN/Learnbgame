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
import bgl
from mathutils import Vector
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty, FloatVectorProperty
from .. functions import update_paint_layers, update_all_paint_layers, get_node_recursive, get_context_node_tree, get_materials_recursive, set_material_shading
import traceback
import os 

class ForceLayerUpdate(bpy.types.Operator):
    bl_idname = "b_painter.force_layer_update"
    bl_label = "Force Layer Update"
    bl_description = "BPainter Layer Data needs to be Updated. Please Synchronize."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.active_object
        update_all_paint_layers(self,context)
        if obj != None:
            mat = bpy.data.materials[obj.b_painter_active_material]
            if mat != None:
                mat.b_painter.paint_channel_active = mat.b_painter.paint_channel_active
            
        return {"FINISHED"}
        

class UpdateImageData(bpy.types.Operator):
    bl_idname = "b_painter.update_image_data"
    bl_label = "Update Image Data"
    bl_description = "Update Image Data"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for image in bpy.data.images:
            if os.path.exists(bpy.path.abspath(image.filepath)):
                image.reload()
                image.update_tag()
        context.scene.update()        
        return {"FINISHED"}
        

class PlaneTexturePreview(bpy.types.Operator):
    bl_idname = "b_painter.plane_texture_preview"
    bl_label = "Plane Texture Preview"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    plane = None
    paint_obj = None
    
    @classmethod
    def poll(cls, context):
        return True
            
    def set_local_view(self,local):
        area = bpy.context.area
        override = bpy.context.copy()
        override["area"] = area
        if local:
            if area.spaces.active.local_view == None:
                bpy.ops.view3d.localview(override)
                bpy.ops.view3d.viewnumpad(type='TOP',align_active=True)
        else:
            if area.spaces.active.local_view != None:
                bpy.ops.view3d.localview(override)
        
    def leave_preview_mode(self,context):
            context.area.header_text_set()
            wm = context.window_manager
            scene = context.scene
            scene.b_painter_texture_preview = False
            self.set_local_view(False)
            bpy.ops.object.mode_set(mode="OBJECT")
            
            if self.plane != None:
                if "paint_obj" in self.plane:
                    context.scene.objects.active = bpy.data.objects[self.plane["paint_obj"]]
                
                    if self.plane.name in context.scene.objects:
                        context.scene.objects.unlink(self.plane)
                    bpy.ops.object.mode_set(mode="TEXTURE_PAINT")
    
    def modal(self,context,event):
        wm = context.window_manager
        scene = context.scene
        
        
        if not scene.b_painter_texture_preview or (hasattr(context.space_data,"local_view") and context.space_data.local_view == None):
            self.leave_preview_mode(context)
            return {"FINISHED"}

        return {"PASS_THROUGH"}
                
    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        space_data = bpy.context.space_data
        self.paint_obj = bpy.data.objects[context.active_object.name]
        
        if not scene.b_painter_texture_preview and space_data.local_view == None:
            scene.b_painter_texture_preview = True
            
            if "BPainter Texture Preview" in bpy.data.objects:
                self.plane = bpy.data.objects["BPainter Texture Preview"]
                context.scene.objects.link(self.plane)
                context.scene.update()
                context.scene.objects.active = self.plane
            else:    
                bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=True,location=(0,0,0))
                bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.0)
                
            bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
            self.plane = context.active_object
            self.plane.name = "BPainter Texture Preview"
            self.plane.active_material = self.paint_obj.active_material
            self.plane["paint_obj"] = self.paint_obj.name
            local_view = self.set_local_view(True)
            context.window_manager.modal_handler_add(self)
            
            return {"RUNNING_MODAL"}
        
        
        scene.b_painter_texture_preview = False
        self.plane = context.active_object if context.active_object.name == "BPainter Texture Preview" else None
        self.leave_preview_mode(context)
        return {"FINISHED"}
            
        

class SetNodeAsPaintlayer(bpy.types.Operator):
    bl_idname = "b_painter.set_node_as_paintlayer"
    bl_label = "Set Node As Paintlayer"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.active_object
        if obj.mode != "TEXTURE_PAINT":
            bpy.ops.object.mode_set(mode="TEXTURE_PAINT")
        
        mat = obj.active_material
        if mat != None:
            node_tree = get_context_node_tree(context)
            if node_tree != None:
                active_node = node_tree.nodes.active
                if active_node.label == "BPaintLayer" and active_node.type == "GROUP":
                    update_all_paint_layers(self,context)
                    mat.b_painter.paint_channel_active = active_node.node_tree.name
                elif active_node.type == "TEX_IMAGE" and active_node.image != None:
                    mat.b_painter.paint_channel_active = "Unordered Images"
                    update_all_paint_layers(self,context)
                    for i,layer in enumerate(mat.b_painter.paint_layers):
                        if layer.name == active_node.image.name:
                            mat.b_painter.paint_layers_index = i
                            break
                        
                
        return {"FINISHED"}
        

class ClearLayer(bpy.types.Operator):
    bl_idname = "b_painter.clear_layer"
    bl_label = "Clear Layer"
    bl_description = "Clears the layer. Be carefull, undo not possible."
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True
    
    def clear_image(self,img):
        pixels = img.pixels[:] 
        pixels = list(img.pixels) 

        for i in range(0, len(pixels), 4):
            alpha=pixels[i+3] = 0

        img.pixels[:] = pixels

        img.update()
        img.update_tag()
    
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.label(text="No Undo supported.",icon="ERROR")
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
            
    def execute(self, context):
        if context.active_object.active_material != None:
            paint_layers = context.active_object.active_material.b_painter.paint_layers
            paint_layers_index = context.active_object.active_material.b_painter.paint_layers_index
            if len(paint_layers) > 0:
                layer = paint_layers[paint_layers_index]
            
                img = bpy.data.images[layer.name]
                self.clear_image(img)
                
                
        bpy.ops.ed.undo_push(message="Clear Layer")
        return {"FINISHED"}

   

class ColorPipette(bpy.types.Operator):
    bl_idname = "b_painter.color_pipette"
    bl_label = "Color Pipette"
    bl_description = "Picks the unshaded Screencolor of your texture. (Alt+Click)"
    bl_options = {"REGISTER"}
    
    pick_mode = StringProperty(default="DRAG")
    mode = "SHADED"
    timer = 9
    _timer = None
    settings = None
    init_color = []
    current_color = []
    brush = None
    show_brush = False
    mouse_x = 0
    mouse_y = 0
    mouse_x_hist = 0
    mouse_y_hist = 0
    image_editor_mode = ""
        
    @classmethod
    def poll(cls, context):
        if context.active_object != None and context.active_object.mode == "TEXTURE_PAINT":
            return True
    
    
    def check_mode(self,context):
        active_object = context.active_object
        mat = bpy.data.materials[active_object.b_painter_active_material] if active_object.b_painter_active_material in bpy.data.materials else None
            
        node_tree = mat.node_tree if mat != None else None
        if node_tree != None:
            for node in node_tree.nodes:
                if node.type == "EMISSION" and node.label == "BPainterPreview" and len(node.outputs[0].links) > 0:
                    self.mode = "SHADELESS"
                    
    def get_current_color(self,context):
        self.brush = bpy.context.scene.tool_settings.image_paint.brush
        self.settings = bpy.context.scene.tool_settings.unified_paint_settings
        if self.settings.use_unified_color:
            color = list(self.settings.color)
        else:
            color = list(self.brush.color)
        return color   
            
            
    def invoke(self, context, event):
        try:
            context.area.header_text_set(text="Pick a custom Color from the Screen. Press Esc or Rightclick to Cancel")
            
            self.show_brush = bool(context.tool_settings.image_paint.show_brush)
            context.tool_settings.image_paint.show_brush = False
            
            
            wm = context.window_manager
            self.check_mode(context)
            bpy.context.window.cursor_set("EYEDROPPER") 
            active_object = context.active_object
            
            if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
                set_material_shading(self,context.active_object,shadeless=True,ignore_prop=True)
            elif context.scene.render.engine in ["CYCLES"]:
                if self.mode == "SHADED":
                    bpy.ops.b_painter.separate_paint_channel(mat_name=active_object.b_painter_active_material,force_preview=True)
            self.init_color = self.get_current_color(context)
            self.current_color = self.get_current_color(context)
            
            if context.area.type == "IMAGE_EDITOR":
                self.image_editor_mode = context.area.spaces[0].mode
                context.area.spaces[0].mode = "PAINT"
            bpy.ops.paint.sample_color( location=(event.mouse_region_x,event.mouse_region_y),merged=True)

            self._timer = wm.event_timer_add(0.05, context.window)
            
            
            args = (self, context)
            if context.area.type != "IMAGE_EDITOR":
                self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
            else:
                self._handle = bpy.types.SpaceImageEditor.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")    
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        except Exception:
            context.tool_settings.image_paint.show_brush = self.show_brush
            traceback.print_exc()
            return {"FINISHED"}
    
    def exit_modal(self,context,event):
        context.tool_settings.image_paint.show_brush = self.show_brush
        
        if self.image_editor_mode != "":
            context.area.spaces[0].mode = self.image_editor_mode
        
        wm = context.window_manager
        bpy.context.window.cursor_set("DEFAULT")
        active_object = context.active_object
        if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
            set_material_shading(self,context.active_object,shadeless=False,ignore_prop=True)
        if context.scene.render.engine in ["CYCLES"]:
            if self.mode == "SHADED":
                bpy.ops.b_painter.separate_paint_channel(mat_name=active_object.b_painter_active_material)
        context.area.header_text_set()
        
        if context.area.type != "IMAGE_EDITOR":
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
        else:
            bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, "WINDOW")
        wm.event_timer_remove(self._timer)
        context.area.tag_redraw()  
            
    
    def modal(self, context, event):
        bpy.context.window.cursor_set("EYEDROPPER") 
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        self.current_color = self.get_current_color(context)
        
        self.timer += 1
        if self.timer%10 == 0:
            bpy.ops.paint.sample_color(location=(event.mouse_region_x,event.mouse_region_y),merged=True)
        
        if event.type == "RIGHTMOUSE" or event.type == "ESC":
            if self.settings.use_unified_color:
                self.settings.color = self.init_color
            else:
                self.brush.color = self.init_color  
            self.exit_modal(context,event)
            return{"CANCELLED"}
        
        if event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.pick_mode == "DRAG":
            bpy.ops.paint.sample_color(location=(event.mouse_region_x,event.mouse_region_y),merged=True)
            self.exit_modal(context,event)
            return {"FINISHED"}
        elif event.type == "LEFTMOUSE" and event.value == "PRESS" and self.pick_mode == "PRESS":
            bpy.ops.paint.sample_color(location=(event.mouse_region_x,event.mouse_region_y),merged=True)
            self.exit_modal(context,event)
            return {"FINISHED"}
        elif event.value == "RELEASE" and self.pick_mode == "HOTKEY":
            bpy.ops.paint.sample_color(location=(event.mouse_region_x,event.mouse_region_y),merged=True)
            self.exit_modal(context,event)
            return {"FINISHED"}
        
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
    

    def draw_callback_px(tmp,self, context):
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(self.current_color[0], self.current_color[1], self.current_color[2], 1.0)
        bgl.glLineWidth(2)

        bgl.glBegin(bgl.GL_QUADS)
        offset = Vector((-10,16))
        size = [40,40]
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glVertex2i(self.mouse_x+size[0] + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glVertex2i(self.mouse_x+size[0] + int(offset.x), self.mouse_y+size[1] + int(offset.y))
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y+size[1] + int(offset.y))
        bgl.glEnd()
        
        bgl.glColor4f(0.2,0.2,0.2,1)
        bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glVertex2i(self.mouse_x+size[0] + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glVertex2i(self.mouse_x+size[0] + int(offset.x), self.mouse_y+size[1] + int(offset.y))
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y+size[1] + int(offset.y))
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glEnd()
        
        
        bgl.glColor4f(self.init_color[0], self.init_color[1], self.init_color[2], 1.0)
        bgl.glBegin(bgl.GL_QUADS)
        offset = Vector((30,16))
        size = [40,40]
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glVertex2i(self.mouse_x+size[0] + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glVertex2i(self.mouse_x+size[0] + int(offset.x), self.mouse_y+size[1] + int(offset.y))
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y+size[1] + int(offset.y))
        bgl.glEnd()
        
        bgl.glColor4f(0.2,0.2,0.2,1)
        bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glVertex2i(self.mouse_x+size[0] + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glVertex2i(self.mouse_x+size[0] + int(offset.x), self.mouse_y+size[1] + int(offset.y))
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y+size[1] + int(offset.y))
        bgl.glVertex2i(self.mouse_x + int(offset.x), self.mouse_y + int(offset.y))
        bgl.glEnd()
        
        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0) 

class MovePaintLayer(bpy.types.Operator):
    bl_idname = "b_painter.move_paint_layer"
    bl_label = "Move Paint Layer"
    bl_description = "Move Layer in Stack"
    bl_options = {"REGISTER"}
    
    type = StringProperty(default="UP")
    mat_name = StringProperty(default="")
    @classmethod
    def poll(cls, context):
        return True
    
    def move_layer_blender_render(self,context,mat):
        if mat != None:
            paint_layer = mat.b_painter.paint_layers
            paint_layer_idx = mat.b_painter.paint_layers_index
            if len(paint_layer) > 1:
                if self.type == "UP":
                    direction = -1
                    if paint_layer_idx == 0:
                        direction = 0
                elif self.type == "DOWN":
                    direction = 1    
                    if paint_layer_idx >= len(paint_layer)-1:
                        direction = 0
                
                
                tex_slot1 = mat.texture_slots[paint_layer[paint_layer_idx].index]
                tex_slot2 = mat.texture_slots[paint_layer[paint_layer_idx + direction].index]
                tmp_values1 = {}
                tmp_values2 = {}
                for attr in tex_slot1.bl_rna.properties.keys():
                    if attr != "output_node":
                        tmp_values1[attr] = getattr(tex_slot1,attr)
                        tmp_values2[attr] = getattr(tex_slot2,attr)
                for attr in tmp_values1:
                    try:
                        setattr(tex_slot1,attr,tmp_values2[attr])
                        setattr(tex_slot2,attr,tmp_values1[attr])
                    except:    
                        pass
                mat.b_painter.paint_layers_index += direction
            update_all_paint_layers("DUMMY",context)        
                
    def get_input_socket(self,node,name="Color"):
        for socket in node.inputs:
            if name in socket.name:
                return socket
    def get_output_socket(self,node,name="Color"):        
        for socket in node.outputs:
            if name in socket.name:
                return socket
        
    def get_linked_sockets(self,node,socket):
        linked_sockets = []
        for link in socket.links:
            if not socket.is_output:
                for s in link.from_node.outputs:
                    if s == link.from_socket:
                        linked_sockets.append(s)
                        break
            elif socket.is_output:
                for s in link.to_node.inputs:
                    if s == link.to_socket:
                        linked_sockets.append(s)
                        break
        return linked_sockets
    
    def move_layer_cycles(self,context,mat):
        if mat != None:
            
            paint_layers = mat.b_painter.paint_layers
            paint_layer_idx = mat.b_painter.paint_layers_index
            if len(paint_layers) > 0:
                paint_layer = paint_layers[paint_layer_idx]
                paint_channel_info = mat.b_painter.paint_channel_info
                paint_channel_active = mat.b_painter.paint_channel_active
                
                if paint_channel_active == "Unordered Images":
                    return
                node_tree = bpy.data.node_groups[paint_channel_info[paint_channel_active].name]
                
                
                if self.type == "UP":
                    direction = -1
                    if paint_layer_idx == 0:
                        direction = 0
                        return
                elif self.type == "DOWN":
                    direction = 1    
                    if paint_layer_idx >= len(paint_layers)-1:
                        direction = 0
                        return
                mat.b_painter.paint_layers_index += direction        
                pl1 = paint_layers[paint_layer_idx]
                pl2 = paint_layers[paint_layer_idx + direction]
                
                
                if pl1.layer_type in ["PAINT_LAYER"]:
                    mix_node = node_tree.nodes[pl1.mix_node_name]
                    
                    output_links = self.get_linked_sockets(mix_node,mix_node.outputs["Color"])
                    input_links = self.get_linked_sockets(mix_node,mix_node.inputs["Color1"])
                    
                    tex_node = node_tree.nodes[pl1.tex_node_name]
                    uv_node = tex_node.inputs["Vector"].links[0].from_node
                    math_node = mix_node.inputs["Fac"].links[0].from_node
                    nodes_active = {"layer_node":mix_node,"tex_node":tex_node,"math_node":math_node,"uv_node":uv_node,"output_links":output_links,"input_links":input_links}
                    
                elif pl1.layer_type in ["ADJUSTMENT_LAYER"]:
                    adj_node =  node_tree.nodes[pl1.name]
                    
                    output_links = self.get_linked_sockets(adj_node,adj_node.outputs["Color"])
                    input_links = self.get_linked_sockets(adj_node,adj_node.inputs["Color"])
                    
                    nodes_active = {"layer_node":adj_node,"output_links":output_links,"input_links":input_links}
                elif pl1.layer_type in ["PROCEDURAL_TEXTURE"]:
                    proc_node = node_tree.nodes[pl1.mix_node_name]
                    output_links = self.get_linked_sockets(proc_node,proc_node.outputs["Color"])
                    input_links = self.get_linked_sockets(proc_node,proc_node.inputs["Color1"])
                    
                    math_node = proc_node.inputs["Fac"].links[0].from_node
                    ramp_node = node_tree.nodes[pl1.proc_ramp_node_name]
                    proc_tex_node = node_tree.nodes[pl1.proc_tex_node_name]
                    proc_coord_node = proc_tex_node.inputs["Vector"].links[0].from_node
                    
                    nodes_active = {"layer_node":proc_node,"output_links":output_links,"input_links":input_links,"math_node":math_node,"ramp_node":ramp_node,"proc_tex_node":proc_tex_node,"proc_coord_node":proc_coord_node}
                    
                if pl1.mask_mix_node_name != "":
                    mask_mix_node = node_tree.nodes[pl1.mask_mix_node_name]
                    mask_invert_node = mask_mix_node.inputs["Fac"].links[0].from_node
                    mask_tex_node = mask_invert_node.inputs["Color"].links[0].from_node
                    
                    output_links = self.get_linked_sockets(mask_mix_node,mask_mix_node.outputs["Color"])
                    input_links = self.get_linked_sockets(mask_mix_node,mask_mix_node.inputs["Color2"])
                    
                    nodes_active["mask_mix_node"] = mask_mix_node
                    nodes_active["mask_invert_node"] = mask_invert_node
                    nodes_active["mask_tex_node"] = mask_tex_node
                    nodes_active["mask_output_links"] = output_links
                    nodes_active["mask_input_links"] = input_links
                    
                
                if pl2.layer_type in ["PAINT_LAYER"]:
                    mix_node = node_tree.nodes[pl2.mix_node_name]
                    
                    output_links = self.get_linked_sockets(mix_node,mix_node.outputs["Color"])
                    input_links = self.get_linked_sockets(mix_node,mix_node.inputs["Color1"])
                    
                    tex_node = node_tree.nodes[pl2.tex_node_name]
                    uv_node = tex_node.inputs["Vector"].links[0].from_node
                    math_node = mix_node.inputs["Fac"].links[0].from_node
                    nodes_next = {"layer_node":mix_node,"tex_node":tex_node,"math_node":math_node,"uv_node":uv_node,"output_links":output_links,"input_links":input_links}
                elif pl2.layer_type in ["ADJUSTMENT_LAYER"]:
                    adj_node =  node_tree.nodes[pl2.name]
                    
                    output_links = self.get_linked_sockets(adj_node,adj_node.outputs["Color"])
                    input_links = self.get_linked_sockets(adj_node,adj_node.inputs["Color"])
                    
                    nodes_next = {"layer_node":adj_node,"output_links":output_links,"input_links":input_links}
                elif pl2.layer_type in ["PROCEDURAL_TEXTURE"]:
                    proc_node =  node_tree.nodes[pl2.mix_node_name]
                    
                    output_links = self.get_linked_sockets(proc_node,proc_node.outputs["Color"])
                    input_links = self.get_linked_sockets(proc_node,proc_node.inputs["Color1"])
                    
                    math_node = proc_node.inputs["Fac"].links[0].from_node
                    ramp_node = node_tree.nodes[pl2.proc_ramp_node_name]
                    proc_tex_node = node_tree.nodes[pl2.proc_tex_node_name]
                    proc_coord_node = proc_tex_node.inputs["Vector"].links[0].from_node
                    
                    nodes_next = {"layer_node":proc_node,"output_links":output_links,"input_links":input_links,"math_node":math_node,"ramp_node":ramp_node,"proc_tex_node":proc_tex_node,"proc_coord_node":proc_coord_node}
                
                if pl2.mask_mix_node_name != "":
                    mask_mix_node = node_tree.nodes[pl2.mask_mix_node_name]
                    mask_invert_node = mask_mix_node.inputs["Fac"].links[0].from_node
                    mask_tex_node = mask_invert_node.inputs["Color"].links[0].from_node
                    
                    output_links = self.get_linked_sockets(mask_mix_node,mask_mix_node.outputs["Color"])
                    input_links = self.get_linked_sockets(mask_mix_node,mask_mix_node.inputs["Color2"])
                    
                    nodes_next["mask_mix_node"] = mask_mix_node
                    nodes_next["mask_invert_node"] = mask_invert_node
                    nodes_next["mask_tex_node"] = mask_tex_node
                    nodes_next["mask_output_links"] = output_links
                    nodes_next["mask_input_links"] = input_links
                    
                
                tmp_loc = Vector(nodes_active["layer_node"].location)
                nodes_active["layer_node"].location = nodes_next["layer_node"].location
                
                ### move paint node
                try:
                    nodes_active["math_node"].location = nodes_active["layer_node"].location + Vector((0,-40))
                    nodes_active["tex_node"].location = nodes_active["layer_node"].location + Vector((0,-40))
                    nodes_active["uv_node"].location = nodes_active["tex_node"].location + Vector((0,-40))
                    
                except:
                    pass  
                
                ### move procedural texture node
                try:
                    nodes_active["math_node"].location = nodes_active["layer_node"].location + Vector((0,-40))
                    nodes_active["ramp_node"].location = nodes_active["math_node"].location + Vector((0,-40))
                    nodes_active["proc_tex_node"].location = nodes_active["ramp_node"].location + Vector((0,-40))
                    nodes_active["proc_coord_node"].location = nodes_active["proc_tex_node"].location + Vector((0,-40))
                    
                except:
                    pass   
                
                ### if mask node existent, move it
                if "mask_mix_node" in nodes_active:
                    nodes_active["mask_mix_node"].location = nodes_active["layer_node"].location + Vector((0,160))
                    nodes_active["mask_invert_node"].location = nodes_active["layer_node"].location + Vector((0,120))
                    nodes_active["mask_tex_node"].location = nodes_active["layer_node"].location + Vector((0,80))
                    
                nodes_next["layer_node"].location = tmp_loc
                try:
                    nodes_next["tex_node"].location = nodes_next["layer_node"].location + Vector((0,-40))
                    nodes_next["uv_node"].location = nodes_next["tex_node"].location + Vector((0,-40))
                    nodes_next["math_node"].location = nodes_next["uv_node"].location + Vector((0,-40))
                    
                except:
                    pass
                
                ### move procedural texture node
                try:
                    nodes_next["math_node"].location = nodes_next["layer_node"].location + Vector((0,-40))
                    nodes_next["ramp_node"].location = nodes_next["math_node"].location + Vector((0,-40))
                    nodes_next["proc_tex_node"].location = nodes_next["ramp_node"].location + Vector((0,-40))
                    nodes_next["proc_coord_node"].location = nodes_next["proc_tex_node"].location + Vector((0,-40))
                    
                except:
                    pass   
                
                ### if mask node existent, move it
                if "mask_mix_node" in nodes_next:
                    nodes_next["mask_mix_node"].location = nodes_next["layer_node"].location + Vector((0,160))
                    nodes_next["mask_invert_node"].location = nodes_next["layer_node"].location + Vector((0,120))
                    nodes_next["mask_tex_node"].location = nodes_next["layer_node"].location + Vector((0,80))
                

                if self.type == "DOWN":
                    ### link active node outputs
                    for socket in nodes_active["input_links"]:
                        node_tree.links.new(self.get_input_socket(nodes_next["layer_node"]),socket)
                    if pl1.mask_mix_node_name != "": # active node has a mask
                        if pl2.mask_mix_node_name != "":
                            for socket in nodes_next["mask_output_links"]:
                                node_tree.links.new(nodes_active["mask_mix_node"].outputs["Color"],socket)
                        else: # active node has no mask
                            for socket in nodes_next["output_links"]:
                                node_tree.links.new(nodes_active["mask_mix_node"].outputs["Color"],socket)
                    else:
                        if pl2.mask_mix_node_name != "":
                            for socket in nodes_next["mask_output_links"]:
                                node_tree.links.new(nodes_active["layer_node"].outputs["Color"],socket)
                        else: # active node has no mask
                            for socket in nodes_next["output_links"]:
                                node_tree.links.new(nodes_active["layer_node"].outputs["Color"],socket)
                        
                    
                    ### link next node inputs
                    if pl2.mask_mix_node_name != "":    
                        if pl1.mask_mix_node_name != "": # next node has a mask
                            for socket in nodes_active["mask_input_links"]:
                                node_tree.links.new(nodes_next["mask_mix_node"].inputs["Color2"],socket)
                        else: # next node has no mask
                            for socket in nodes_active["input_links"]:
                                node_tree.links.new(nodes_next["mask_mix_node"].inputs["Color2"],socket)
                                    
                    ### swap active and next input/output
                    if pl1.mask_mix_node_name != "":
                        if pl2.mask_mix_node_name != "":
                            node_tree.links.new(nodes_next["mask_mix_node"].outputs["Color"],nodes_active["mask_mix_node"].inputs["Color2"])
                            node_tree.links.new(nodes_next["mask_mix_node"].outputs["Color"],self.get_input_socket(nodes_active["layer_node"]))
                        else:
                            node_tree.links.new(nodes_next["layer_node"].outputs["Color"],nodes_active["mask_mix_node"].inputs["Color2"])
                            node_tree.links.new(nodes_next["layer_node"].outputs["Color"],self.get_input_socket(nodes_active["layer_node"]))
                    else:
                        if pl2.mask_mix_node_name != "":
                            node_tree.links.new(nodes_next["mask_mix_node"].outputs["Color"],self.get_input_socket(nodes_active["layer_node"]))
                        else:
                            node_tree.links.new(nodes_next["layer_node"].outputs["Color"],self.get_input_socket(nodes_active["layer_node"]))
                
                elif self.type == "UP":
                    ### link active node inputs
                    if pl1.mask_mix_node_name == "": ### active layer has no mask
                        if pl2.mask_mix_node_name == "":
                            for socket in nodes_next["input_links"]:
                                node_tree.links.new(self.get_input_socket(nodes_active["layer_node"]),socket)
                        else:
                            for socket in nodes_next["mask_input_links"]:
                                node_tree.links.new(self.get_input_socket(nodes_active["layer_node"]),socket)
                    else: ### active layer has mask
                        if pl2.mask_mix_node_name == "":
                            for socket in nodes_next["input_links"]:
                                node_tree.links.new(nodes_active["mask_mix_node"].inputs["Color2"],socket)
                                node_tree.links.new(self.get_input_socket(nodes_active["layer_node"]),socket)
                        else:
                            for socket in nodes_next["mask_input_links"]:
                                node_tree.links.new(nodes_active["mask_mix_node"].inputs["Color2"],socket)
                                node_tree.links.new(self.get_input_socket(nodes_active["layer_node"]),socket)
                    
                    ### link next node outputs
                    if pl2.mask_mix_node_name == "": ### next layer has no mask
                        if pl1.mask_mix_node_name == "":
                            for socket in nodes_active["output_links"]:
                                node_tree.links.new(nodes_next["layer_node"].outputs["Color"],socket)
                        else:
                            for socket in nodes_active["mask_output_links"]:
                                node_tree.links.new(nodes_next["layer_node"].outputs["Color"],socket)
                    else: ### next layer has mask
                        if pl1.mask_mix_node_name == "":
                            for socket in nodes_active["output_links"]:
                                node_tree.links.new(nodes_next["mask_mix_node"].outputs["Color"],socket)
                        else:
                            for socket in nodes_active["mask_output_links"]:
                                node_tree.links.new(nodes_next["mask_mix_node"].outputs["Color"],socket)
                                
                    ### swap active and next input/output
                    if pl1.mask_mix_node_name == "":
                        if pl2.mask_mix_node_name == "":
                            node_tree.links.new(nodes_active["layer_node"].outputs["Color"],self.get_input_socket(nodes_next["layer_node"]))
                        else:
                            node_tree.links.new(nodes_active["layer_node"].outputs["Color"],self.get_input_socket(nodes_next["layer_node"]))    
                            node_tree.links.new(nodes_active["layer_node"].outputs["Color"],nodes_next["mask_mix_node"].inputs["Color2"])
                    else:
                        if pl2.mask_mix_node_name == "":
                            node_tree.links.new(nodes_active["mask_mix_node"].outputs["Color"],self.get_input_socket(nodes_next["layer_node"]))
                        else:
                            node_tree.links.new(nodes_active["mask_mix_node"].outputs["Color"],nodes_next["mask_mix_node"].inputs["Color2"])
                            node_tree.links.new(nodes_active["mask_mix_node"].outputs["Color"],self.get_input_socket(nodes_next["layer_node"]))
                update_all_paint_layers(self,context)         
    
    def execute(self, context):
        ob = context.active_object
        
        mat = None
        if self.mat_name in bpy.data.materials:
            mat = bpy.data.materials[self.mat_name]
            
        if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
            self.move_layer_blender_render(context,mat)
        elif context.scene.render.engine == 'CYCLES':
            self.move_layer_cycles(context,mat) 
        
        if mat != None:
            mat.b_painter.paint_layers_index = mat.b_painter.paint_layers_index
        return {"FINISHED"}

def get_input_socket(self,node,name="Color"):
        for socket in node.inputs:
            if name in socket.name:
                return socket
def get_output_socket(self,node,name="Color"):        
    for socket in node.outputs:
        if name in socket.name:
            return socket    

class DeletePaintLayer(bpy.types.Operator):
    bl_idname = "b_painter.delete_paint_layer"
    bl_label = "Delete Paint Layer"
    bl_description = "Delete selected Paint Layer. No Undo possible in Texture Paint Mode."
    bl_options = {"REGISTER","UNDO"}
    
    mat_name = StringProperty(default="")
    index = IntProperty(default=-1)
    
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        
        return wm.invoke_confirm(self,event)
    
    ### reposition nodes after deleted. Keeps them in a clean order.
    def reposition_nodes(self,node_tree,pos):
        for node in node_tree.nodes:
            if node.location[0] > pos and node.type not in ["GROUP_INPUT","GROUP_OUTPUT"]:
                node.location[0] -= 100
    
    def execute(self, context):
        ob = context.active_object
        mat = bpy.data.materials[self.mat_name]
        layer_index_init = int(mat.b_painter.paint_layers_index)
        if self.index != -1:
            mat.b_painter.paint_layers_index = self.index
        
        layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
        
        if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
            mat.texture_slots.clear(layer.index)
            
            update_all_paint_layers(self,context)
            
            mat.b_painter.paint_layers_index = mat.b_painter.paint_layers_index 
        elif context.scene.render.engine == 'CYCLES':
            if mat.b_painter.paint_channel_active != "Unordered Images":
                if len(mat.b_painter.paint_layers) > 0:
                    active_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
                    node_tree = bpy.data.node_groups[mat.b_painter.paint_channel_active]
                    
                    if active_layer.paint_layer_active or active_layer.mask_mix_node_name == "":
                        if active_layer.layer_type in ["PAINT_LAYER"]:
                            mix_node = node_tree.nodes[active_layer.mix_node_name]
                            math_node = mix_node.inputs["Fac"].links[0].from_node if len(mix_node.inputs["Fac"].links) > 0 else None
                            tex_node = node_tree.nodes[active_layer.tex_node_name]
                            uv_node = (tex_node.inputs[0].links[0].from_node if (len(tex_node.inputs[0].links) > 0) else None)
                            
                            
                            if active_layer.mask_mix_node_name != "":
                                mask_mix_node = node_tree.nodes[active_layer.mask_mix_node_name]
                                for socket in mask_mix_node.outputs["Color"].links:
                                    node_tree.links.new( mask_mix_node.inputs["Color2"].links[0].from_socket,  socket.to_socket)
                            else:
                                for socket in mix_node.outputs["Color"].links:
                                    node_tree.links.new( get_input_socket(self,mix_node).links[0].from_socket,  socket.to_socket)    
                            
                            self.reposition_nodes(node_tree,mix_node.location[0])
                            
                            node_tree.nodes.remove(mix_node)
                            node_tree.nodes.remove(uv_node)
                            node_tree.nodes.remove(math_node)
                            node_tree.nodes.remove(tex_node)
                            
                            if active_layer.mask_mix_node_name != "":
                                mask_mix_node = node_tree.nodes[active_layer.mask_mix_node_name]
                                invert_node = mask_mix_node.inputs["Fac"].links[0].from_node
                                mask_tex_node = invert_node.inputs["Color"].links[0].from_node
                                
                                node_tree.nodes.remove(mask_mix_node)
                                node_tree.nodes.remove(invert_node)
                                node_tree.nodes.remove(mask_tex_node)
                            
                        elif active_layer.layer_type == "ADJUSTMENT_LAYER":
                            adj_node = node_tree.nodes[active_layer.name]
                            
                            if active_layer.mask_mix_node_name != "":
                                mask_mix_node = node_tree.nodes[active_layer.mask_mix_node_name]
                                for socket in mask_mix_node.outputs["Color"].links:
                                    node_tree.links.new( mask_mix_node.inputs["Color2"].links[0].from_socket,  socket.to_socket)
                            else:
                                for socket in adj_node.outputs["Color"].links:
                                    node_tree.links.new( get_input_socket(self,adj_node).links[0].from_socket,  socket.to_socket) 
                            
                            if active_layer.mask_mix_node_name != "":
                                mask_mix_node = node_tree.nodes[active_layer.mask_mix_node_name]
                                invert_node = mask_mix_node.inputs["Fac"].links[0].from_node
                                mask_tex_node = invert_node.inputs["Color"].links[0].from_node
                                
                                self.reposition_nodes(node_tree,mask_mix_node.location[0])
                                
                                node_tree.nodes.remove(mask_mix_node)
                                node_tree.nodes.remove(invert_node)
                                node_tree.nodes.remove(mask_tex_node)
                            
                            node_tree.nodes.remove(adj_node)
                        elif active_layer.layer_type in ["PROCEDURAL_TEXTURE"]:
                            mix_node = node_tree.nodes[active_layer.mix_node_name]
                            math_node = mix_node.inputs["Fac"].links[0].from_node if len(mix_node.inputs["Fac"].links) > 0 else None
                            ramp_node = node_tree.nodes[active_layer.proc_ramp_node_name]
                            proc_tex_node = node_tree.nodes[active_layer.proc_tex_node_name]
                            proc_coord_node = proc_tex_node.inputs["Vector"].links[0].from_node
                            
                            
                            if active_layer.mask_mix_node_name != "":
                                mask_mix_node = node_tree.nodes[active_layer.mask_mix_node_name]
                                for socket in mask_mix_node.outputs["Color"].links:
                                    node_tree.links.new( mask_mix_node.inputs["Color2"].links[0].from_socket,  socket.to_socket)
                            else:
                                for socket in mix_node.outputs["Color"].links:
                                    node_tree.links.new( get_input_socket(self,mix_node).links[0].from_socket,  socket.to_socket)    
                            
                            self.reposition_nodes(node_tree,mix_node.location[0])
                            
                            node_tree.nodes.remove(mix_node)
                            node_tree.nodes.remove(math_node)
                            node_tree.nodes.remove(ramp_node)
                            node_tree.nodes.remove(proc_tex_node)
                            node_tree.nodes.remove(proc_coord_node)
                            
                            if active_layer.mask_mix_node_name != "":
                                mask_mix_node = node_tree.nodes[active_layer.mask_mix_node_name]
                                invert_node = mask_mix_node.inputs["Fac"].links[0].from_node
                                mask_tex_node = invert_node.inputs["Color"].links[0].from_node
                                
                                node_tree.nodes.remove(mask_mix_node)
                                node_tree.nodes.remove(invert_node)
                                node_tree.nodes.remove(mask_tex_node)    
                    else:
                        mix_node = node_tree.nodes[active_layer.mix_node_name] if active_layer.mix_node_name != "" else node_tree.nodes[active_layer.name]
                        mask_mix_node = node_tree.nodes[active_layer.mask_mix_node_name]
                        invert_node = mask_mix_node.inputs["Fac"].links[0].from_node
                        mask_tex_node = invert_node.inputs["Color"].links[0].from_node
                        
                        mask_mix_node = node_tree.nodes[active_layer.mask_mix_node_name]
                        for socket in mask_mix_node.outputs["Color"].links:
                            node_tree.links.new( mix_node.outputs["Color"] ,  socket.to_socket)
                        
                        node_tree.nodes.remove(mask_mix_node)
                        node_tree.nodes.remove(invert_node)
                        node_tree.nodes.remove(mask_tex_node)
                        
            else:
                node_tree = mat.node_tree
                if node_tree != None:
                    if len(mat.b_painter.paint_layers) > 0:
                        layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
                        node = node_tree.nodes[layer.tex_node_name]
                        node_tree.nodes.remove(node)
            update_all_paint_layers(self,context)            
                        
        context.tool_settings.image_paint.canvas = None
        mat.b_painter.paint_layers_index = mat.b_painter.paint_layers_index
            
        bpy.ops.ed.undo_push(message="Layer Delete")
        return {"FINISHED"}
             

def create_paint_group(self,mat,name="Diffuse Channel"):
    context = bpy.context
    node_tree = mat.node_tree
    
    for node in node_tree.nodes:
        node.select = False
    
    paint_group_name = mat.name + "_PaintLayer"
    paint_group_node_tree = bpy.data.node_groups.new(paint_group_name,"ShaderNodeTree")
    
    
    input_node = paint_group_node_tree.nodes.new("NodeGroupInput")
    input_node.location = (-650,0)
    socket = paint_group_node_tree.inputs.new("NodeSocketColor","Background Color")
    socket.default_value = [.8,.8,.8,1]
    
    output_node = paint_group_node_tree.nodes.new("NodeGroupOutput")
    output_node.location = (650,0)
    socket = paint_group_node_tree.outputs.new("NodeSocketColor","Color")
    socket.default_value = [.8,.8,.8,1]
    socket_alpha = paint_group_node_tree.outputs.new("NodeSocketFloat","Alpha")
    
    paint_group = node_tree.nodes.new("ShaderNodeGroup")
    paint_group.label = "BPaintLayer"
    paint_group.name = name
    paint_group.node_tree = paint_group_node_tree
    
    update_all_paint_layers(self,context) 
    mat.b_painter.paint_channel_active = paint_group.node_tree.name
    
    paint_group.select = True
    node_tree.nodes.active = paint_group

    return paint_group
        


def connect_default(mat,paint_group):
    if mat.node_tree != None:
        for node in mat.node_tree.nodes:
            if node.type == "OUTPUT_MATERIAL":
                if len(node.inputs["Surface"].links) > 0:
                    shader = node.inputs["Surface"].links[0].from_node
                    for input in shader.inputs:
                        if input.type == "RGBA" and len(input.links) == 0:
                            mat.node_tree.links.new(input,paint_group.outputs["Color"])
                else:
                    diffuse_bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfDiffuse")
                    diffuse_bsdf.location = node.location + Vector((-200,0))
                    paint_group.location =  diffuse_bsdf = Vector((-200,0))
                    mat.node_tree.links.new(diffuse_bsdf.inputs["Color"],paint_group.outputs["Color"])
                    mat.node_tree.links.new(diffuse_bsdf.outputs["BSDF"],node.inputs["Surface"])
                               

def unwrap_object(ob):
    bpy.ops.mesh.uv_texture_add()
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(island_margin=0.02)
    bpy.ops.object.mode_set(mode="TEXTURE_PAINT")
    
IMAGES = []
class NewPaintLayer(bpy.types.Operator):
    bl_idname = "b_painter.new_paint_layer"
    bl_label = "New Layer"
    bl_description = "Create new Layer"
    bl_options = {"REGISTER"}
    
    def get_images(self,context):
        global IMAGES
        IMAGES = []
        for i,img in enumerate(bpy.data.images):
            if "b_painter_brush_img" not in img.name:
                IMAGES.append((img.name,img.name,img.name,bpy.types.UILayout.icon(img),i))
        
        return IMAGES
    
    image = EnumProperty(items=get_images)
    custom_img = BoolProperty(default=False)
    mat_name = StringProperty(default="")
    
    TYPES = []
    TYPES.append(("DIFFUSE","Diffuse","Diffuse"))
    TYPES.append(("BUMP","Bump","Bump"))
    TYPES.append(("SPECULAR","Specular","Specular"))
    TYPES.append(("GLOSSY","Glossy","Glossy"))
    TYPES.append(("ALPHA","Alpha","Alpha"))
    TYPES.append(("STENCIL","Stencil","Stencil"))
    layer_type = EnumProperty(items=TYPES,name="Paint Layer Type")
    
    PROC_LAYER = []
    PROC_LAYER.append(("ShaderNodeTexVoronoi","Voronoi Texture","Voronoi Texture","None",0))
    PROC_LAYER.append(("ShaderNodeTexNoise","Noise Texture","Noise Texture","None",1))
    PROC_LAYER.append(("ShaderNodeTexBrick","Brick Texture","Brick Texture","None",2))
    PROC_LAYER.append(("ShaderNodeTexChecker","Checker Texture","Checker Texture","None",3))
    PROC_LAYER.append(("ShaderNodeTexMusgrave","Musgrave Texture","Musgrave Texture","None",4))
    PROC_LAYER.append(("ShaderNodeTexWave","Wave Texture","Wave Texture","None",5))
    proc_layer = EnumProperty(items=PROC_LAYER,name="Procedural Texture Type")
    
    TYPES = []
    TYPES.append(("PAINT_LAYER","Paint Layer","Paint Layer"))
    TYPES.append(("ADJUSTMENT_LAYER","Adjustment Layer","Adjustment Layer"))
    TYPES.append(("PROCEDURAL_LAYER","Procedural Layer","Procedural Layer"))
    layer_type_cycles = EnumProperty(items=TYPES,name="Paint Layer Type")
    
    ADJUSTMENT_LAYER = []
    ADJUSTMENT_LAYER.append(("ShaderNodeRGBCurve","RGB Curve","RGB Curve","IPO_EASE_IN_OUT",0))
    ADJUSTMENT_LAYER.append(("ShaderNodeHueSaturation","Hue","Hue","SEQ_CHROMA_SCOPE",1))
    ADJUSTMENT_LAYER.append(("ShaderNodeInvert","Invert","Invert","IMAGE_ALPHA",2))
    adjustment_layer = EnumProperty(items=ADJUSTMENT_LAYER,name="Adjustment Layer Type")
    
    resolution_x = IntProperty(default=1024, min=0)
    resolution_y = IntProperty(default=1024, min=0)
    bit_32 = BoolProperty(default=False)
    
    color = FloatVectorProperty(name="Layer Color",description="",min=0.0,max=1.0,default=(0,0,0,0),subtype="COLOR_GAMMA",size=4)
    
    layer_type_prev = ""
    
    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        if self.layer_type != self.layer_type_prev:
            if self.layer_type == "BUMP":
                self.bit_32 = True
            else:
                self.bit_32 = False
        self.layer_type_prev = self.layer_type
        return True
    
    def draw(self,context):
        layout = self.layout
        col = layout.column()
        if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
            col.prop(self,"layer_type",text="")
        
        if self.layer_type_cycles == "PROCEDURAL_LAYER":
            col.prop(self,"proc_layer",expand=True)
        elif self.layer_type_cycles == "ADJUSTMENT_LAYER":
            col.row().prop(self,"adjustment_layer",expand=True)
            
        elif self.layer_type_cycles == "PAINT_LAYER":
            col.prop(self,"custom_img",text="Choose existing Image as Layer")
            if self.custom_img:
                col2 = layout.column()
                col2.scale_y = .5
                col2.template_icon_view(self,"image",show_labels=True)
            else:
                if self.layer_type == "DIFFUSE" or context.scene.render.engine == "CYCLES":
                    row = layout.row(align=True)
                    row.prop(self,"color")
                row = layout.row(align=True)
                subcol = row.column(align=True)
                subcol.prop(self,"resolution_x",text="X")
                subcol.prop(self,"resolution_y",text="Y")
                row = layout.row(align=True)
                row.prop(self,"bit_32",text="32 Bit Texture")    
            
    def invoke(self,context,event):
        wm = context.window_manager
        self.custom_img = False
        
        return wm.invoke_props_dialog(self)
    
    def get_input_socket(self,node,name="Color"):
        for socket in node.inputs:
            if name in socket.name:
                return socket
    def get_output_socket(self,node,name="Color"):        
        for socket in node.outputs:
            if name in socket.name:
                return socket
    
    def create_bi_layer(self,context,ob,mat):
        index = mat.b_painter.paint_layers_index
        idx = 0
        for i,tex_slot in enumerate(mat.texture_slots):
            if tex_slot != None:
                idx = i    
        tex_slot = mat.texture_slots.create(idx+1)
              
        if mat != None:
            layer_index = int(mat.b_painter.paint_layers_index)
        else:
            layer_index = 0    
        
        ### auto unwrap if on uvmap is detected
        if len(ob.data.uv_textures) == 0:
            unwrap_object(ob)

        tex_slot.use_map_color_diffuse = False
        
        name = ""
        if self.layer_type == "DIFFUSE":
            name = "Diffuse"
        elif self.layer_type == "BUMP":
            name = "Bump"
        elif self.layer_type == "NORMAL":
            name = "Normal"
        elif self.layer_type == "SPECULAR":
            name = "Specular"
        elif self.layer_type == "GLOSSY":
            name = "Glossy"
        elif self.layer_type == "STENCIL":
            name = "Stencil"
        elif self.layer_type == "ALPHA":
            name = "Alpha"
        tex = bpy.data.textures.new(name,"IMAGE")
        
        if self.layer_type == "DIFFUSE":
            name = "Diffuse"
            tex_slot.use_map_color_diffuse = True
        elif self.layer_type == "BUMP":
            name = "Bump"
            tex_slot.use_map_normal = True
        elif self.layer_type == "NORMAL":
            name = "Normal"
            tex_slot.use_map_normal = True
            tex.use_normal_map = True
        elif self.layer_type == "SPECULAR":
            name = "Specular"
            tex_slot.use_map_specular = True
            tex.use_alpha = False
            mat.specular_intensity = 0.0
        elif self.layer_type == "GLOSSY":
            name = "Glossy"
            tex_slot.use_map_hardness = True
            tex.use_alpha = False
            mat.specular_hardness = 25
        elif self.layer_type == "STENCIL":
            name = "Stencil"
            tex_slot.use_stencil = True
            tex_slot.use_rgb_to_intensity = True
        elif self.layer_type == "ALPHA":
            name = "Alpha"
            tex_slot.alpha_factor = 1.0
            tex_slot.use_map_alpha = True
            tex.use_alpha = False
            mat.use_transparency = True
            mat.alpha = 0.0
        
        if self.custom_img:
            img = bpy.data.images[self.image]
        else:    
            img = bpy.data.images.new(name,self.resolution_x,self.resolution_y,alpha=True,float_buffer=self.bit_32)
            
            if self.layer_type in ["DIFFUSE"]:
                img.generated_color = self.color
            elif self.layer_type in ["GLOSSY","SPECULAR","STENCIL"]:
                img.generated_color = [0,0,0,1]
            elif self.layer_type in ["NORMAL"]:
                img.generated_color = [0.215861, 0.215861, 1.000000, 1.000000]
            elif self.layer_type in ["BUMP"]:
                img.generated_color = [0.207916, 0.207916, 0.207916, 1.000000]
            elif self.layer_type in ["ALPHA"]:
                img.generated_color = [1.0, 1.0, 1.0, 1.0]
 
        tex.image = img
        tex_slot.texture = tex

        context.tool_settings.image_paint.canvas = img
        
        #update_paint_layers(self,context)
        update_all_paint_layers(self,context)
        
        if len(mat.b_painter.paint_layers) > 0:
            layers = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
            mat.b_painter.paint_layers_index = len(mat.b_painter.paint_layers)-1
        
            
        #update_paint_layers(self,context)
        update_all_paint_layers(self,context)
        mat.b_painter.paint_layers_index = mat.b_painter.paint_layers_index 
        
        ### move paint layer beneath current selected layer
        count = len(mat.b_painter.paint_layers) - index - 2
        for i in range(count):
            bpy.ops.b_painter.move_paint_layer(type="UP",mat_name=mat.name)
    
    def get_last_node_in_chain(self,node):
        while len(node.outputs) > 0 and len(node.outputs[0].links) > 0:
            if len(node.outputs[0].links[0].to_node.outputs) > 0:
                node = node.outputs[0].links[0].to_node
            else:
                return node    
        return node    
    
    def create_cycles_layer(self,context,ob,mat):
        index = mat.b_painter.paint_layers_index
        
        if len(ob.data.uv_textures) == 0:
            unwrap_object(ob)
        
        name = "Layer"
        active_paint_channel = mat.b_painter.paint_channel_active
        node_tree = None
        if active_paint_channel != "Unordered Images":
            paint_channel_info = mat.b_painter.paint_channel_info[active_paint_channel]
            node_tree = bpy.data.node_groups[paint_channel_info.name] if active_paint_channel != "Unordered Images" else mat.node_tree
        else:
            node_tree = mat.node_tree
        if self.layer_type_cycles == "PAINT_LAYER" or active_paint_channel == "Unordered Images":
            if self.custom_img:
                img = bpy.data.images[self.image]
            else:    
                img = bpy.data.images.new(name,self.resolution_x,self.resolution_y,alpha=True,float_buffer=self.bit_32)
                img.generated_color = self.color
        
            
        if active_paint_channel == "Unordered Images" and node_tree != None:
            tex_node = node_tree.nodes.new("ShaderNodeTexImage")
            tex_node.image = img
        elif active_paint_channel != "Unordered Images" and node_tree != None:
            
            active_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index] if mat.b_painter.paint_layers_index <= len(mat.b_painter.paint_layers)-1 else None
            paint_layers_length = len(mat.b_painter.paint_layers)
            group_input = [node for node in node_tree.nodes if node.type == "GROUP_INPUT"][0]
            group_output = [node for node in node_tree.nodes if node.type == "GROUP_OUTPUT"][0]
            last_node = self.get_last_node_in_chain(group_input)
            
            if self.layer_type_cycles == "PAINT_LAYER":
                ### create paint layer
                mix_node = node_tree.nodes.new("ShaderNodeMixRGB")
                mix_node.hide = True
                mix_node.use_clamp = True
                
                tex_node = node_tree.nodes.new("ShaderNodeTexImage")
                tex_node.hide = True
                tex_node.image = img
                tex_node.label = "BPaintLayer"
                
                uv_node = node_tree.nodes.new("ShaderNodeUVMap")
                uv_node.hide = True
                
                math_node = node_tree.nodes.new("ShaderNodeMath")
                math_node.hide = True
                math_node.use_clamp = True
                math_node.operation = "MULTIPLY"
                math_node.inputs[0].default_value = 1.0
                math_node.inputs[1].default_value = 1.0
                
                node_tree.links.new(tex_node.outputs['Color'],mix_node.inputs['Color2'])
                node_tree.links.new(tex_node.outputs['Alpha'],math_node.inputs[0])
                node_tree.links.new(math_node.outputs[0],mix_node.inputs["Fac"])
                node_tree.links.new(tex_node.inputs['Vector'],uv_node.outputs["UV"])
                
                offset = Vector((0,-160)) if last_node.label == "BPaintMask" else Vector((0,0,))
                mix_node.location = last_node.location + Vector((100,0)) + offset
                tex_node.location = mix_node.location + Vector((0,-40))
                uv_node.location = tex_node.location + Vector((0,-40))
                math_node.location = uv_node.location + Vector((0,-40))
                
                node_tree.links.new(self.get_output_socket(last_node),mix_node.inputs["Color1"])
                node_tree.links.new(mix_node.outputs["Color"],group_output.inputs["Color"])
            elif self.layer_type_cycles == "ADJUSTMENT_LAYER":
                adj_node = node_tree.nodes.new(self.adjustment_layer)
                adj_node.hide = True
                node_tree.links.new(self.get_output_socket(last_node),adj_node.inputs["Color"])
                node_tree.links.new(adj_node.outputs["Color"],group_output.inputs["Color"])
                offset = Vector((0,-160)) if last_node.label == "BPaintMask" else Vector((0,0,))
                
                adj_node.location = last_node.location + Vector((100,0)) + offset
            elif self.layer_type_cycles == "PROCEDURAL_LAYER":
                ### create paint layer
                mix_node = node_tree.nodes.new("ShaderNodeMixRGB")
                mix_node.hide = True
                mix_node.use_clamp = True
                mix_node.label = "BPaintProcTex"
                
                math_node = node_tree.nodes.new("ShaderNodeMath")
                math_node.hide = True
                math_node.use_clamp = True
                math_node.operation = "MULTIPLY"
                math_node.inputs[0].default_value = 1.0
                math_node.inputs[1].default_value = 1.0
                
                ramp_node = node_tree.nodes.new("ShaderNodeValToRGB")
                ramp_node.hide = True
                
                proc_tex_node = node_tree.nodes.new(self.proc_layer)
                proc_tex_node.hide = True
                
                proc_coord_node = node_tree.nodes.new("ShaderNodeTexCoord")
                proc_coord_node.hide = True
                
                node_tree.links.new(mix_node.inputs["Fac"],math_node.outputs["Value"])
                node_tree.links.new(mix_node.inputs["Color2"],ramp_node.outputs["Color"])
                node_tree.links.new(math_node.inputs[0],ramp_node.outputs["Alpha"])
                node_tree.links.new(proc_tex_node.outputs["Color"],ramp_node.inputs["Fac"])
                node_tree.links.new(proc_tex_node.inputs["Vector"],proc_coord_node.outputs["Object"])
                
                offset = Vector((0,-160)) if last_node.label == "BPaintMask" else Vector((0,0,))
                mix_node.location = last_node.location + Vector((100,0)) + offset
                math_node.location = mix_node.location + Vector((0,-40))
                ramp_node.location = math_node.location + Vector((0,-40))
                proc_tex_node.location = ramp_node.location + Vector((0,-40))
                proc_coord_node.location = proc_tex_node.location + Vector((0,-40))
                
                node_tree.links.new(self.get_output_socket(last_node),mix_node.inputs["Color1"])
                node_tree.links.new(mix_node.outputs["Color"],group_output.inputs["Color"])
            
        update_all_paint_layers(self,context)
        mat.b_painter.paint_layers_index = len(mat.b_painter.paint_layers)-1
        
        ### move paint layer beneath current selected layer
        count = len(mat.b_painter.paint_layers) - index - 2
        for i in range(count):
            bpy.ops.b_painter.move_paint_layer(type="UP",mat_name=mat.name)
            
    def execute(self, context):
        
        ob = context.active_object
        mat = bpy.data.materials[self.mat_name]
        
        if mat == None:
            mat = bpy.data.materials.new("Material")
            if len(ob.material_slots) == 0:
                bpy.ops.object.material_slot_add()
            
            ob.material_slots[0].material = mat
            
        if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
            self.create_bi_layer(context,ob,mat)
            
        elif bpy.context.scene.render.engine == 'CYCLES':
            if "b_painter_init" not in mat :
                mat["b_painter_init"] = True
                if mat.b_painter.paint_channel_active == "Unordered Images":
                    bpy.ops.b_painter.create_new_paint_channel(mat_name=mat.name,paint_group_name = "Diffuse Channel")
                    update_all_paint_layers(self,context)
            self.create_cycles_layer(context,ob,mat)
            
        
        return {"FINISHED"}

class CreateStencilLayer(bpy.types.Operator):
    bl_idname = "b_painter.create_stencil_layer"
    bl_label = "Create Stencil Layer"
    bl_description = "Create Stencil Layer"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.active_object
        if obj != None:
            mat = obj.active_material
            if mat != None:
                node_tree = get_context_node_tree(context)
                if node_tree != None:
                    selected_nodes = []
                    
                    ### get all nodes with RGBA Color Output Socket
                    for node in node_tree.nodes:
                        if node.select:
                            for output in node.outputs:
                                if output.type == "RGBA":
                                    selected_nodes.append(node)
                                    break
                    selected_nodes.sort(key= lambda x: -x.location[1])            
                    if len(selected_nodes) > 0:
                        mat.b_painter.paint_channel_active = "Unordered Images"
                        
                        for i,node in enumerate(selected_nodes):
                            if i == 0:
                                prev_node = node
                            if (i+1) < len(selected_nodes):
                                
                                next_node = selected_nodes[i+1]
                                
                                mix_node_loc = Vector(( max(prev_node.location[0],next_node.location[0]) + 260, next_node.location[1]))
                                mix_node = node_tree.nodes.new("ShaderNodeMixRGB")
                                mix_node.location = mix_node_loc
                                
                                
                                node_tree.links.new(prev_node.outputs["Color"],mix_node.inputs["Color1"])
                                node_tree.links.new(next_node.outputs["Color"],mix_node.inputs["Color2"])
                                
                                
                                prev_node = mix_node
                                
                                img = bpy.data.images.new("Stencil",1024,1024,alpha=True)
                                img.generated_color = [0,0,0,0]
                                stencil_node = node_tree.nodes.new("ShaderNodeTexImage")
                                stencil_node.hide = True
                                stencil_node.image = img
                                stencil_node.location = mix_node.location + Vector((-100,0))
                                
                                node_tree.links.new(stencil_node.outputs["Color"],mix_node.inputs["Fac"])
        update_all_paint_layers(self,context)                        
                            
        
        return {"FINISHED"}
        

class CreateLayerMask(bpy.types.Operator):
    bl_idname = "b_painter.create_layer_mask"
    bl_label = "Create Layer Mask"
    bl_description = "Create Layer Mask"
    bl_options = {"REGISTER"}
    
    def get_images(self,context):
        global IMAGES
        IMAGES = []
        for i,img in enumerate(bpy.data.images):
            if "b_painter_brush_img" not in img.name:
                IMAGES.append((img.name,img.name,img.name,bpy.types.UILayout.icon(img),i))
        
        return IMAGES
    
    image = EnumProperty(items=get_images)
    custom_img = BoolProperty(default=False)
    
    mat_name = StringProperty()
    resolution_x = IntProperty(default=256)
    resolution_y = IntProperty(default=256)
    color = FloatVectorProperty(name="Mask Color",description="",min=0.0,max=1.0,default=(0,0,0),subtype="COLOR_GAMMA",size=3)
    
    def check(self,context):
        return True
    
    def draw(self,context):
        layout = self.layout
        col = layout.column()
        col.prop(self,"custom_img",text="Choose existing Image as Layer")
        if self.custom_img:
            col2 = layout.column()
            col2.scale_y = .5
            col2.template_icon_view(self,"image",show_labels=True)
        else:
            row = layout.row()
            row.prop(self,"color")
            col = layout.column(align=True)
            col.prop(self,"resolution_x",text="X")
            col.prop(self,"resolution_y",text="Y") 
    
    @classmethod
    def poll(cls, context):
        return True
    
    def get_input_socket(self,node,name="Color"):
        for socket in node.inputs:
            if name in socket.name:
                return socket
    def get_output_socket(self,node,name="Color"):        
        for socket in node.outputs:
            if name in socket.name:
                return socket
    
    def invoke(self,context,event):
        wm = context.window_manager
        self.custom_img = False
        
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        mat = bpy.data.materials[self.mat_name]
        paint_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
        if paint_layer.mask_mix_node_name == "":
            
            node_tree = bpy.data.node_groups[paint_layer.node_tree_name]
            
            mix_node = node_tree.nodes[paint_layer.mix_node_name] if paint_layer.layer_type == "PAINT_LAYER" else node_tree.nodes[paint_layer.name]
            
            mask_mix_node = node_tree.nodes.new("ShaderNodeMixRGB")
            mask_mix_node.label = "BPaintMask"
            mask_mix_node.hide = True
            mask_mix_node.use_clamp = True
            
            invert_node = node_tree.nodes.new("ShaderNodeInvert")
            invert_node.label = "BPaintMask"
            invert_node.hide = True
            
            img = None
            if self.custom_img:
                img = bpy.data.images[self.image]
            else:    
                name = paint_layer.name+"_mask"
                img = bpy.data.images.new(name,self.resolution_x,self.resolution_y,alpha=False,float_buffer=False)
                img.generated_color = [self.color[0],self.color[1],self.color[2],1]
                
            tex_node = node_tree.nodes.new("ShaderNodeTexImage")
            tex_node.hide = True
            tex_node.image = img
            tex_node.label = "BPaintLayer"
            
            mask_mix_node.location = mix_node.location + Vector((0,160))
            invert_node.location = mask_mix_node.location + Vector((0,-40))
            tex_node.location = invert_node.location + Vector((0,-40))
            
            ### wire nodes
            for link in mix_node.outputs["Color"].links:
                node_tree.links.new(mask_mix_node.outputs["Color"],link.to_socket)
                
            node_tree.links.new(tex_node.outputs["Color"],invert_node.inputs["Color"])
            node_tree.links.new(invert_node.outputs["Color"],mask_mix_node.inputs["Fac"])
            node_tree.links.new(mix_node.outputs["Color"], mask_mix_node.inputs["Color1"])
            node_tree.links.new(self.get_input_socket(mix_node).links[0].from_socket,mask_mix_node.inputs["Color2"])
            
            paint_layer.mask_layer_active = True
            update_all_paint_layers(self,context)
            mat.b_painter.paint_layers_index = mat.b_painter.paint_layers_index
        else:
            self.report({'INFO'}, "Layer has a Mask already.")
        
        
        return {"FINISHED"}
        
    
class CreateNewPaintChannel(bpy.types.Operator):
    bl_idname = "b_painter.create_new_paint_channel"
    bl_label = "Create New Paint Channel"
    bl_description = "Create Paint Channel"
    bl_options = {"REGISTER"}
    
    mat_name = StringProperty()
    paint_group_name = StringProperty(default="Diffuse Channel")
    
    @classmethod
    def poll(cls, context):
        return True

    def draw(self,context):
        layout = self.layout
        col = layout.column()
        col.prop(self,"paint_group_name",text="Channel Name")  
            
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        mat = bpy.data.materials[self.mat_name]
        
        paint_group = create_paint_group(self,mat,self.paint_group_name)
        connect_default(mat,paint_group)
        
        return {"FINISHED"}
    
class DeletePaintChannel(bpy.types.Operator):
    bl_idname = "b_painter.delete_paint_channel"
    bl_label = "Delete Paint Channel"
    bl_description = "Delete Paint Channel"
    bl_options = {"REGISTER"}
    
    mat_name = StringProperty()
    group_name = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_confirm(self,event)

    def execute(self, context):
        #items = bpy.types.BPainterProperties.bl_rna.properties['paint_channel'].enum_items
        mat = bpy.data.materials[self.mat_name]
        if mat.node_tree != None:
            node_tree = mat.node_tree
            paint_groups = get_node_recursive(node_tree,[])
            for group in paint_groups:
                if group.name == self.group_name and group.label == "BPaintLayer":
                    if len(group.inputs[0].links) > 0 and len(group.outputs[0].links) > 0:
                        group.id_data.links.new(group.inputs[0].links[0].from_socket,group.outputs[0].links[0].to_socket)
                    
                    group.id_data.nodes.remove(group)
            update_all_paint_layers(self,context)
            
            if len(mat.b_painter.paint_channel_info) > 0:
                mat.b_painter.paint_channel_active = mat.b_painter.paint_channel_info[0].name
        return {"FINISHED"}    
                
class SeparatePaintChannel(bpy.types.Operator):
    bl_idname = "b_painter.separate_paint_channel"
    bl_label = "Separate Paint Channel"
    bl_description = "Separate Paint Channel"
    bl_options = {"REGISTER"}
    
    mat_name = StringProperty()
    mode = "SET_CHANNEL_PREVIEW"
    force_preview = BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return True
    
    def create_emission_shader(self,context):
        mat = bpy.data.materials[self.mat_name]
        if mat.node_tree != None:
            emission_node = mat.node_tree.nodes.new("ShaderNodeEmission")
        return emission_node    
    
    def check_mode(self,context):
        mat = bpy.data.materials[self.mat_name]
        node_tree = mat.node_tree
        for node in node_tree.nodes:
            if node.type == "EMISSION" and node.label == "BPainterPreview":
                self.mode = "REMOVE_CHANNEL_PREVIEW"
                
    def create_emission_node(self,context,node_tree,mat):
        for node in node_tree.nodes:
            if "BPainterPreview" in node.name and "BPainterPreview" in node.label:
                return node
        emission_node = mat.node_tree.nodes.new("ShaderNodeEmission")
        return emission_node
            
    
    def execute(self, context):
        mat = bpy.data.materials[self.mat_name]
        node_tree = mat.node_tree
        paint_groups = get_node_recursive(node_tree,[])
        group_name = ""
        if mat.b_painter.paint_channel_active in mat.b_painter.paint_channel_info:
            group_name = mat.b_painter.paint_channel_info[mat.b_painter.paint_channel_active].group_name
        output_node = None
        emission_node = None
        prev_connected_node = None
        
        self.check_mode(context)
        if self.mode == "SET_CHANNEL_PREVIEW" or self.force_preview:
            if node_tree != None:
                for node in node_tree.nodes:
                    if node.type == "OUTPUT_MATERIAL":
                        output_node = node
                        break
                emission_node = self.create_emission_node(context,node_tree,mat)
                emission_node.name = "BPainterPreview"
                emission_node.label = "BPainterPreview"
                emission_node.location = output_node.location + Vector((0,80))
                emission_node.hide = True
                if len(output_node.inputs["Surface"].links) > 0:
                    prev_connected_node = output_node.inputs["Surface"].links[0].from_node
                
                emission_node["prev_connected_node"] = prev_connected_node.name
                
                paint_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
                
                if mat.b_painter.paint_channel_active != "Unordered Images" and (paint_layer.paint_layer_active or paint_layer.mask_mix_node_name == ""):
                    for group in paint_groups:
                        if group.name == group_name and group.label == "BPaintLayer":
                            group_node = node_tree.nodes.new(group.bl_idname)
                            group_node.node_tree = group.node_tree
                            group_node.inputs["Background Color"].default_value = group.inputs["Background Color"].default_value
                            group_node.location = output_node.location + Vector((-100,80))
                            group_node.hide = True
                            node_tree.links.new(emission_node.inputs["Color"],group_node.outputs["Color"])
                            node_tree.links.new(output_node.inputs["Surface"],emission_node.outputs["Emission"])
                else:
                    layer_node_tree = bpy.data.node_groups[paint_layer.node_tree_name] if paint_layer.node_tree_name in bpy.data.node_groups else mat.node_tree
                    if paint_layer.paint_layer_active or paint_layer.mask_mix_node_name == "":
                        tex_node = layer_node_tree.nodes[paint_layer.tex_node_name]
                    elif paint_layer.mask_layer_active and paint_layer.mask_mix_node_name != "":
                        tex_node = layer_node_tree.nodes[paint_layer.mask_tex_node_name]
                    tex_node_new = node_tree.nodes.new(tex_node.bl_idname)
                    tex_node_new.label = "BPaintLayer"
                    tex_node_new.hide = True
                    tex_node_new.image = tex_node.image
                    tex_node_new.location = output_node.location + Vector((-100,80))
                    node_tree.links.new(emission_node.inputs["Color"],tex_node_new.outputs["Color"])
                    node_tree.links.new(output_node.inputs["Surface"],emission_node.outputs["Emission"])
                    node_tree.links.new(tex_node_new.outputs["Alpha"],emission_node.inputs["Strength"])
                    
        elif self.mode == "REMOVE_CHANNEL_PREVIEW":
            if node_tree != None:
                for node in node_tree.nodes:
                    if node.type == "EMISSION" and node.label == "BPainterPreview":
                        emission_node = node
                        if emission_node["prev_connected_node"] in node_tree.nodes:
                            prev_connected_node = node_tree.nodes[emission_node["prev_connected_node"]]
                    elif node.type == "OUTPUT_MATERIAL":
                        output_node = node    
                            
                node_tree.links.new(prev_connected_node.outputs[0],output_node.inputs["Surface"])
                if len(emission_node.inputs["Color"].links) > 0:
                    node_tree.nodes.remove(emission_node.inputs["Color"].links[0].from_node)
                node_tree.nodes.remove(emission_node)
                    
                                        
        return {"FINISHED"}
        
class InvertLayerMask(bpy.types.Operator):
    bl_idname = "b_painter.invert_layer_mask"
    bl_label = "Invert Layer Mask"
    bl_description = "Mask -> Ctr + Click to invert"
    bl_options = {"REGISTER"}
    
    index = IntProperty()
    mat_name = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return True
        
    
    def invoke(self,context,event):
        mat = bpy.data.materials[self.mat_name]
        paint_layer = mat.b_painter.paint_layers[self.index]
        node_tree = bpy.data.node_groups[paint_layer.node_tree_name] if paint_layer.node_tree_name != "" else mat.node_tree
        mask_node = node_tree.nodes[paint_layer.mask_mix_node_name]
        mask_invert_node = mask_node.inputs["Fac"].links[0].from_node
        
        if event.ctrl:
            mask_invert_node.mute = not(mask_invert_node.mute)
            self.report({'INFO'}, "Layer Mask inverted.")
        elif event.shift:
            mask_node.b_painter_layer_hide = not(mask_node.b_painter_layer_hide)
        else:
            paint_layer.mask_layer_active = True
        return {"FINISHED"}
            