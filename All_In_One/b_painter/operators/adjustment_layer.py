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
from bpy.props import StringProperty, IntProperty

class ConfigureAdjustmentLayer(bpy.types.Operator):
    bl_idname = "b_painter.configure_adjustment_layer"
    bl_label = "Configure Adjustment Layer"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    node_name = StringProperty()
    node_tree_name = StringProperty()
    index = IntProperty()
    mat_name = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True
    
    def draw(self,context):
        node_tree = bpy.data.node_groups[self.node_tree_name]
        node = node_tree.nodes[self.node_name]
        layout = self.layout
        col = layout.column(align=True)
        
        if node.type == "CURVE_RGB":
            col.template_curve_mapping(node,"mapping",type="COLOR")
        elif node.type == "HUE_SAT":
            col.prop(node.inputs[0],"default_value","Hue",slider=True)
            col.prop(node.inputs[1],"default_value","Saturation",slider=True)
            col.prop(node.inputs[2],"default_value","Value",slider=True)
        
          
        
    def invoke(self,context,event):
        
        node_tree = bpy.data.node_groups[self.node_tree_name]
        node = node_tree.nodes[self.node_name]
        if node.type == "INVERT":
            return{"FINISHED"}
        mat = bpy.data.materials[self.mat_name]
        mat.b_painter.paint_layers_index = self.index
        paint_layer = mat.b_painter.paint_layers[self.index]
        paint_layer.paint_layer_active = True
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        return {"FINISHED"}
    
class ConfigureProceduralTexture(bpy.types.Operator):
    bl_idname = "b_painter.configure_procedural_texture"
    bl_label = "Configure Procedural Texture"
    bl_description = "Configure Procedural Texture"
    bl_options = {"REGISTER"}
    
    node_tree_name = StringProperty()
    proc_tex_node_name = StringProperty()
    proc_ramp_node_name = StringProperty()
    index = IntProperty()
    mat_name = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True
    
    def draw(self,context):
        node_tree = bpy.data.node_groups[self.node_tree_name]
        proc_tex_node = node_tree.nodes[self.proc_tex_node_name]
        proc_ramp_node = node_tree.nodes[self.proc_ramp_node_name]
        
        layout = self.layout
        col = layout.column()
        proc_tex_node.draw_buttons_ext(context,col)
        for input in proc_tex_node.inputs:
            if input.name != "Vector":
                col.prop(input,"default_value",text=input.name)
        proc_ramp_node.draw_buttons_ext(context,col)        
    
        
    def invoke(self,context,event):
        node_tree = bpy.data.node_groups[self.node_tree_name]
        proc_tex_node = node_tree.nodes[self.proc_tex_node_name]
        proc_ramp_node = node_tree.nodes[self.proc_ramp_node_name]
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        return {"FINISHED"}
            