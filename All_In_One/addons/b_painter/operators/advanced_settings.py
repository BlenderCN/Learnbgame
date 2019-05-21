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
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
import os

class AdvancedColorSettings(bpy.types.Operator):
    bl_idname = "b_painter.advanced_color_settings"
    bl_label = "Advanced Color Settings"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True
    
    def draw(self,context):
        settings = context.tool_settings.image_paint
        layout = self.layout
        col = layout.column()

        #### panel order operator
        subrow = col.row(align=True)
        #subrow.scale_x = .7
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_UP_VEC",emboss=True)
        op.panel_name = "COLOR"
        op.mode = "UP"
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_DOWN_VEC",emboss=True)
        op.panel_name = "COLOR"
        op.mode = "DOWN"
      
        
        if context.tool_settings.image_paint.palette != None:
            op = col.operator("b_painter.export_palette_as_json",text="Save Custom Palette Settings",icon="COLOR")
            op.palette_name = context.tool_settings.image_paint.palette.name
        
            op = col.operator("b_painter.import_palette_from_json",text="Restore Palette Defaults",icon="LOOP_BACK")
            op.palette_name = context.tool_settings.image_paint.palette.name
            op.restore_default = True

        col.prop(bpy.data.scenes[0],"b_painter_show_color_wheel",text="Show Color Wheel")
        col.prop(bpy.data.scenes[0],"b_painter_show_color_palette",text="Show Color Palette")
        col.label(text="Select Color Palette")
        col.template_ID(settings, "palette", new="palette.new")

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_popup(self)
#        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        return {"FINISHED"}


        
class AdvancedBrushSettings(bpy.types.Operator):
    bl_idname = "b_painter.advanced_brush_settings"
    bl_label = "Advanced Brush Settings"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def set_icon_filepath(self,context):
        context.tool_settings.image_paint.brush.icon_filepath = self.icon_filepath
    
    icon_filepath = StringProperty(update=set_icon_filepath)
    
    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True
      
    def draw(self,context):
        layout = self.layout

        toolsettings = context.tool_settings
        ipaint = toolsettings.image_paint
        brush = ipaint.brush
        
        col = layout.column()
        
        #### panel order operator
        subrow = col.row(align=True)
        #subrow.scale_x = .7
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_UP_VEC",emboss=True)
        op.panel_name = "BRUSH"
        op.mode = "UP"
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_DOWN_VEC",emboss=True)
        op.panel_name = "BRUSH"
        op.mode = "DOWN"
        
        op = col.operator("b_painter.export_brush_as_json",text="Save Custom Brush Settings",icon="BRUSH_DATA")
        op.brush_name = context.tool_settings.image_paint.brush.name
        
        op = col.operator("b_painter.import_brush_from_json",text="Restore Brush Defaults",icon="LOOP_BACK")
        op.brush_name = context.tool_settings.image_paint.brush.name
        op.restore_default = True
        
        row1 = col.row()
        row1 = row1.row(align=True)
        row1.operator_context = 'INVOKE_DEFAULT'
        op = row1.operator("b_painter.add_new_brush",text="Add new Brush",icon="ZOOMIN")
        op = row1.operator("b_painter.delete_brush",text="Delete Brush",icon="ZOOMOUT")
        
        
        
        col.label(text="Brush Settings:")
        col.prop(brush, "stroke_method", text="Stroke Methode")
    
        col = layout.column(align=False)
        row = col.row(align=True)
        row.prop(brush,"spacing",text="Spacing",slider=True)
        row.prop(brush,"use_pressure_spacing",text="")
    
        row = col.row(align=True)
        row.prop(brush,"use_relative_jitter",text="")
        if brush.use_relative_jitter:
            row.prop(brush,"jitter",text="Scatter",slider=True)
        else:    
            row.prop(brush,"jitter_absolute",text="Scatter",slider=True)
        row.prop(brush,"use_pressure_jitter",text="")
        
        ### show brush curve
        row = col.row(align=True)
        if brush.use_cursor_overlay:
            row.prop(brush, "use_cursor_overlay", toggle=True, text="", icon='RESTRICT_VIEW_OFF')
        else:
            row.prop(brush, "use_cursor_overlay", toggle=True, text="", icon='RESTRICT_VIEW_ON')

        sub = row.row(align=True)
        sub.prop(brush, "cursor_overlay_alpha", text="Alpha")
        sub.prop(brush, "use_cursor_overlay_override", toggle=True, text="", icon='BRUSH_DATA')
        
        layout.separator()
        layout.separator()
        layout.box()
        layout.separator()
        
        row = layout.row(align=True)
        col = row.column(align=True)
        col.label(text="Symmetry Settings:")
        row = col.row(align=True)
        row.prop(ipaint, "use_symmetry_x", text="X", toggle=True)
        row.prop(ipaint, "use_symmetry_y", text="Y", toggle=True)
        row.prop(ipaint, "use_symmetry_z", text="Z", toggle=True)
        
        col = layout.column()
        col.label(text="Projection Settings:")
        col.prop(ipaint, "use_occlude")
        col.prop(ipaint, "use_backface_culling")

        row = layout.row()
        row.prop(ipaint, "use_normal_falloff")

        sub = row.row()
        sub.active = (ipaint.use_normal_falloff)
        sub.prop(ipaint, "normal_angle", text="")

        layout.prop(ipaint, "seam_bleed")
        layout.prop(ipaint, "dither")
        
        ups = context.tool_settings.unified_paint_settings
        layout.label(text="Unified Settings:")
        row = layout.row()
        row.prop(ups, "use_unified_size", text="Size")
        row.prop(ups, "use_unified_strength", text="Strength")
        row.prop(ups, "use_unified_color", text="Color")
        
        row = layout.row(align=True)
        row.prop(self, "icon_filepath",text="",icon="IMAGE_DATA")
        
        op = row.operator("b_painter.import_brush_icon",text="",icon="FILESEL")
        op.filepath = context.tool_settings.image_paint.brush.icon_filepath
    
    def invoke(self,context,event):
        self.icon_filepath = context.tool_settings.image_paint.brush.icon_filepath
        
        wm = context.window_manager
        return wm.invoke_popup(self)
#        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        return {"FINISHED"}


class ImportBrushIcon(bpy.types.Operator):#, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "b_painter.import_brush_icon"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Brush Icon"

    # ImportHelper mixin class uses this
    filename_ext = ".png"

    filepath = StringProperty()

    filter_glob = StringProperty(
            default="*.png",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )
    
    def invoke(self,context,event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
    
    def execute(self, context):
        context.tool_settings.image_paint.brush.icon_filepath = self.filepath
        return {'FINISHED'}
    
class AdvancedBrushTextureSettings(bpy.types.Operator):
    bl_idname = "b_painter.advanced_brush_texture_settings"
    bl_label = "Advanced Brush Texture Settings"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True
    
    def draw(self,context):
        brush = context.tool_settings.image_paint.brush
        
        layout = self.layout
        col = layout.column(align=True)
        
        #### panel order operator
        subrow = col.row(align=True)
        #subrow.scale_x = .7
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_UP_VEC",emboss=True)
        op.panel_name = "TEXTURE"
        op.mode = "UP"
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_DOWN_VEC",emboss=True)
        op.panel_name = "TEXTURE"
        op.mode = "DOWN"
        
        col = layout.column(align=True)
        col.prop(brush.texture_slot, "tex_paint_map_mode", text="")
        col.prop(brush.texture_slot, "angle", text="Angle")
        col.prop(brush.texture_slot, "use_rake", text="Rake",toggle=True)
        col.prop(brush.texture_slot, "use_random", text="Random",toggle=True)
        col.prop(brush.texture_slot, "random_angle", text="Random Angle")
        
        col.separator()
        
        row = col.row(align=True)
        if brush.use_primary_overlay:
            row.prop(brush, "use_primary_overlay", toggle=True, text="", icon='RESTRICT_VIEW_OFF')
        else:
            row.prop(brush, "use_primary_overlay", toggle=True, text="", icon='RESTRICT_VIEW_ON')

        sub = row.row(align=True)
        sub.prop(brush, "texture_overlay_alpha", text="Alpha")
        sub.prop(brush, "use_primary_overlay_override", toggle=True, text="", icon='BRUSH_DATA')
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_popup(self)
#        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        return {"FINISHED"}
            
            
            
class AdvancedStencilTextureSettings(bpy.types.Operator):
    bl_idname = "b_painter.advanced_stencil_texture_settings"
    bl_label = "Advanced Stencil Texture Settings"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True
    
    def draw(self,context):
        brush = context.tool_settings.image_paint.brush
        
        layout = self.layout
        col = layout.column(align=True)
        
        #### panel order operator
        subrow = col.row(align=True)
        #subrow.scale_x = .7
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_UP_VEC",emboss=True)
        op.panel_name = "STENCIL"
        op.mode = "UP"
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_DOWN_VEC",emboss=True)
        op.panel_name = "STENCIL"
        op.mode = "DOWN"
        
        col = layout.column(align=True)
        col.prop(brush.mask_texture_slot, "mask_map_mode", text="")
        col.label(text="Angle:")
        col.prop(brush.mask_texture_slot, "angle", text="")
        col.label(text="Offset:")
        col.prop(brush.mask_texture_slot, "offset", text="")
        col.label(text="Scale:")
        col.prop(brush.mask_texture_slot, "scale", text="")
        
        col.separator()
        
        row = col.row(align=True)
        if brush.use_secondary_overlay:
            row.prop(brush, "use_secondary_overlay", toggle=True, text="", icon='RESTRICT_VIEW_OFF')
        else:
            row.prop(brush, "use_secondary_overlay", toggle=True, text="", icon='RESTRICT_VIEW_ON')

        sub = row.row(align=True)
        sub.prop(brush, "mask_overlay_alpha", text="Alpha")
        sub.prop(brush, "use_secondary_overlay_override", toggle=True, text="", icon='BRUSH_DATA')
        
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_popup(self)
#        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        return {"FINISHED"}

class SetExternalPath(bpy.types.Operator):#, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "b_painter.set_external_path"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Set External Image Path"

    # ImportHelper mixin class uses this
    filename_ext = "."
    use_filter_folder = True

    filepath = StringProperty()
    
    mat_name = StringProperty()
    rel_path = BoolProperty(default=True)
    
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.prop(self,"rel_path",text="Relative Path")
    
    def invoke(self,context,event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
    
    def execute(self, context):
        mat = bpy.data.materials[self.mat_name]
        dir = os.path.dirname(self.filepath)
        if self.rel_path:
            dir = bpy.path.relpath(dir)
        mat.b_painter.external_path = dir
        return {'FINISHED'}
                        
class LayerSettings(bpy.types.Operator):
    bl_idname = "b_painter.layer_settings"
    bl_label = "Layer Settings"
    bl_description = ""
    #bl_options = {"REGISTER","UNDO"}
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True
    
    def draw(self,context):
        layout = self.layout
        brush = context.tool_settings.image_paint.brush
        obj = context.active_object
        mat = bpy.data.materials[obj.b_painter_active_material] if obj.b_painter_active_material in bpy.data.materials else None
        
        col = layout.column()
        
        #### panel order operator
        subrow = col.row(align=True)
        #subrow.scale_x = .7
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_UP_VEC",emboss=True)
        op.panel_name = "LAYER"
        op.mode = "UP"
        op = subrow.operator("b_painter.change_panel_order",text="",icon="MOVE_DOWN_VEC",emboss=True)
        op.panel_name = "LAYER"
        op.mode = "DOWN"
        
        #col.label(text="Nothing yet")
        col.prop(context.scene,"b_painter_flip_template_list")
        
        
        active_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index] if len(mat.b_painter.paint_layers) > 0 else None
        if active_layer != None and active_layer.layer_type == "PAINT_LAYER":
            
            col.operator("b_painter.clear_layer",text="Clear Layer",icon="NEW")
            col.operator("b_painter.update_image_data",text="Reload all Images",icon="FILE_REFRESH")
            if mat != None:
                row = col.row(align=True)
                row.prop(mat.b_painter,"external_path",text="Images Path")
                op = row.operator("b_painter.set_external_path",text="",icon="FILE_FOLDER")
                op.mat_name = mat.name
            if obj != None:
                mat = obj.active_material
                if context.scene.render.engine in ["CYCLES"] and mat != None:
                    if mat.b_painter.paint_channel_active != "Unordered Images":
                        if mat.b_painter.paint_layers_index <= len(mat.b_painter.paint_layers)-1:
                            active_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
                            node_tree = (bpy.data.node_groups[mat.b_painter.paint_channel_info[0].name] if mat.b_painter.paint_channel_info[0].name in bpy.data.node_groups else None)
                            if node_tree != None:
                                tex_node = node_tree.nodes[active_layer.tex_node_name]
                                if len(tex_node.inputs["Vector"].links) > 0:
                                    uv_node = tex_node.inputs["Vector"].links[0].from_node
                                    col.prop_search(uv_node,"uv_map",obj.data,"uv_textures",text="UV Map",icon="GROUP_UVS")
                    else:
                        if mat.b_painter.paint_layers_index <= len(mat.b_painter.paint_layers)-1:
                            node_tree = mat.node_tree
                            if node_tree != None:
                                active_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
                                tex_node = node_tree.nodes[active_layer.tex_node_name]
                                if len(tex_node.inputs["Vector"].links) > 0:
                                    uv_node = tex_node.inputs["Vector"].links[0].from_node
                                    col.prop_search(uv_node,"uv_map",obj.data,"uv_textures",text="UV Map",icon="GROUP_UVS")
                                
                                
                elif mat != None and context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
                    active_paint_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
                    tex_slot = mat.texture_slots[active_paint_layer.index]
                    col.prop_search(tex_slot,"uv_layer",obj.data,"uv_textures",text="UV Map",icon="GROUP_UVS")
                                
                
        
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_popup(self)
    
    def execute(self, context):
        return {"FINISHED"}                        

        