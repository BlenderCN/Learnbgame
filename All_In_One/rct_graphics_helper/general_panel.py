'''
Copyright (c) 2018 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

def ToggleShadows(self, context):
    shadow_caster = bpy.data.lamps['ShadowCasterLamp']
    if shadow_caster is None:
        return False
    print(shadow_caster.shadow_method)
    if self.cast_shadows:
        shadow_caster.shadow_method = "RAY_SHADOW"
        shadow_caster.use_diffuse = True
    else:
        shadow_caster.shadow_method = "NOSHADOW"
        shadow_caster.use_diffuse = False
    return

class GeneralProperties(bpy.types.PropertyGroup):
    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)
    default_palette_path = directory + "\\res\\palette.gif"
    palette_path = bpy.props.StringProperty(
        name="Palette Path",
        description="Palette to dither to",
        maxlen= 1024,
        subtype='FILE_PATH',
        default= default_palette_path)

    number_of_rider_sets = bpy.props.IntProperty(
        name = "Rider Sets",
        description = "Number of unqique sets of riders. Usually just the amount of peeps for this vehicle/ride. Some rides for example only expect peeps in sets of 2 to lower the amount of required graphics. This is often done on vehicles which carry 4 or more riders.",
        default = 0,
        min = 0)
        
    number_of_animation_frames = bpy.props.IntProperty(
        name = "Animation Frames",
        description = "Number of animation frames. For example in use for swinging, rotating or animated ride vehicles, animated rides, and animated scenery",
        default = 1,
        min = 1)
        
    cast_shadows = bpy.props.BoolProperty(
        name = "Cast Shadows",
        description = "Control wether or not the render contains shadows. Should be disabled for vehicles",
        default = False,
        update = ToggleShadows)
        
    out_start_index = bpy.props.IntProperty(
        name = "Output Starting Index",
        description = "Number to start counting from for the output file names",
        default = 0,
        min = 0)
    
    output_directory = bpy.props.StringProperty(
        name="Output Folder",
        description="Directory to output the sprites to",
        maxlen= 1024,
        subtype='DIR_PATH',
        default= "//output\\")

    
class VehiclesPanel(bpy.types.Panel):
    bl_label = "RCT General"
    bl_idname = "RENDER_PT_rct_general"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properties = scene.rct_graphics_helper_general_properties

        row = layout.row()
        row.prop(properties, "palette_path")
        
        row = layout.row()
        row.prop(properties, "number_of_rider_sets")

        row = layout.row()
        row.prop(properties, "number_of_animation_frames")
        
        row = layout.row()
        row.prop(properties, "cast_shadows")
        
        row = layout.row()
        row.prop(properties, "out_start_index")

        row = layout.row()
        row.prop(properties, "output_directory")

def register_general_panel():
    bpy.types.Scene.rct_graphics_helper_general_properties = bpy.props.PointerProperty(type=GeneralProperties)
    
def unregister_general_panel():
    del bpy.types.Scene.rct_graphics_helper_general_properties
