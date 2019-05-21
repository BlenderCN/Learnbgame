import bpy
from bpy.types import Panel, Menu, Operator
from rna_prop_ui import PropertyPanel
from bl_operators.presets import AddPresetBase
from .custom_preset_base import Custom_Preset_Base
import os

class CAMERA_PX_Presets(Menu):
    bl_label = "Resolution Presets"
    default_lable = "Resolution Presets"
    preset_subdir = "pixel"
    preset_operator = "script.execute_preset"
    draw = Custom_Preset_Base.draw_preset


class AddPixelResPreset(Custom_Preset_Base, Operator):
    '''Add a Object Draw Preset'''
    bl_idname = "camera.add_pixel_res_preset"
    bl_label = "Add Camera Res Preset"
    preset_menu = "CAMERA_PX_Presets"

    # variable used for all preset values
    preset_defines = [
        "camera = bpy.context.camera"
        ]

    # properties to store in the preset
    preset_values = [
        "camera.width_px",
        "camera.height_px",
        "camera.percent_scale"
        ]

    # where to store the preset
    preset_subdir = "pixel"
    
    
class CAMERA_PX_SCALE_Presets(Menu):
    bl_label = "Pixel Scale"
    default_lable = "Pixel Scale"
    preset_subdir = "scale_pixel"
    preset_operator = "script.execute_preset"
    draw = Custom_Preset_Base.draw_preset


class AddPixelScalePreset(Custom_Preset_Base, Operator):
    '''Add a Object Draw Preset'''
    bl_idname = "camera.add_pixel_scale_preset"
    bl_label = "Add Camera Scale Preset"
    preset_menu = "CAMERA_PX_SCALE_Presets"

    # variable used for all preset values
    preset_defines = [
        "camera = bpy.context.camera"
        ]

    # properties to store in the preset
    preset_values = [
        "camera.pixel_scale",
        "camera.mod_scale",
        ]

    # where to store the preset
    preset_subdir = "scale_pixel"
    
    
class CAMERA_PAPER_Presets(Menu):
    bl_label = "Paper Size Presets"
    default_lable = "Paper Size Presets"
    preset_subdir = "paper"
    preset_operator = "script.execute_preset"
    draw = Custom_Preset_Base.draw_preset


class AddPaperResPreset(Custom_Preset_Base, Operator):
    bl_idname = "camera.add_paper_res_preset"
    bl_label = "Add Camera Res Preset"
    preset_menu = "CAMERA_PAPER_Presets"

    # variable used for all preset values
    preset_defines = [
        "camera = bpy.context.camera"
        ]

    # properties to store in the preset
    preset_values = [
        "camera.width",
        "camera.height",
        ]

    # where to store the preset
    preset_subdir = "paper"
    
class CAMERA_PAPER_SCALE_Presets(Menu):
    bl_label = "Paper Scale"
    default_lable = "Paper Scale"
    preset_subdir = "scale_paper"
    preset_operator = "script.execute_preset"
    draw = Custom_Preset_Base.draw_preset


class AddPaperScalePreset(Custom_Preset_Base, Operator):
    bl_idname = "camera.add_paper_scale_preset"
    bl_label = "Add paper scale preset"
    preset_menu = "CAMERA_PAPER_SCALE_Presets"

    # variable used for all preset values
    preset_defines = [
        "camera = bpy.context.camera"
        ]

    # properties to store in the preset
    preset_values = [
        "camera.paper_scale",
        "camera.mod_scale",
        ]

    # where to store the preset
    preset_subdir = "scale_paper"


class My_Panel(Panel):
    bl_idname = "camera_size"
    bl_label = "Per Camera Resolution"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return context.camera

    def draw_header(self, context):
        camera = context.camera

        self.layout.prop(camera, "use_camera_res", text="")
        
        
    def draw(self, context):
        scene = context.scene
        camera = context.camera
        
        layout = self.layout
        
        layout.active=camera.use_camera_res
        layout.row().operator("bind_marker.bind_marker", text = "Bind Camera To Frame", icon = 'CAMERA_DATA')
        layout.row().prop(camera, 'res_type', expand=True)
 
        #col1.prop(camera,'use_camera_res')
    
        if camera.res_type == 'res_type_paper':
            
            
            split = layout.split()
            
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Camera Size:")
            
            subrow = sub.row(align=True)
            subrow.menu(CAMERA_PAPER_Presets.__name__, text=CAMERA_PAPER_Presets.bl_label)
            subrow.operator(AddPaperResPreset.bl_idname, text="", icon='ADD')
            subrow.operator(AddPaperResPreset.bl_idname, text="", icon='REMOVE').remove_active = True
            
            sub.prop(camera,'width', text = 'Width:')
            sub.prop(camera,'height', text = 'Height:')
            sub.prop(camera,'res', text = 'Resolution (PPI):')
                        
            col = split.column()
            col.active = camera.type == 'ORTHO'
            sub = col.column(align=True)
            sub.label(text="Ortho Scale:")
            
            subrow = sub.row(align=True)
            
            subrow.menu(CAMERA_PAPER_SCALE_Presets.__name__, text=CAMERA_PAPER_SCALE_Presets.bl_label)
            subrow.operator(AddPaperScalePreset.bl_idname, text="", icon='ADD')
            subrow.operator(AddPaperScalePreset.bl_idname, text="", icon='REMOVE').remove_active = True
            
            sub.prop(camera, 'paper_scale', text = "Paper:")
            sub.label(text = "Is Equal to:")
            sub.prop(camera, 'mod_scale', text = "Model:")
        
        else:
            
                        
            split = layout.split()
 
            col = split.column()
            
            
            sub = col.column(align=True)
            sub.label(text="Camera Size:")
            subrow = sub.row(align=True)
            
            subrow.menu(CAMERA_PX_Presets.__name__, text=CAMERA_PX_Presets.bl_label)
            subrow.operator(AddPixelResPreset.bl_idname, text="", icon='ADD')
            subrow.operator(AddPixelResPreset.bl_idname, text="", icon='REMOVE').remove_active = True

            sub.prop(camera,'width_px')
            sub.prop(camera,'height_px')
            sub.prop(camera,'percent_scale', text = "")
            
                        
            col = split.column()
            col.active = camera.type == 'ORTHO'
            sub = col.column(align=True)
            sub.label(text="Ortho Scale:")
            
            subrow = sub.row(align=True)
            
            subrow.menu(CAMERA_PX_SCALE_Presets.__name__, text=CAMERA_PX_SCALE_Presets.bl_label)
            subrow.operator(AddPixelScalePreset.bl_idname, text="", icon='ADD')
            subrow.operator(AddPixelScalePreset.bl_idname, text="", icon='REMOVE').remove_active = True

            sub.prop(camera, 'pixel_scale', text = "Pixels:")
            
            sub.label(text = "Is Equal to:")
            
            sub.prop(camera, 'mod_scale', text = "Model:")

            

        