'''
Copyright (c) 2018 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

from . render_operator import RCTRender
from . angle_sections.track import track_angle_sections, track_angle_sections_names
from . render_task import *
    

class RenderVehicle(RCTRender, bpy.types.Operator):
    bl_idname = "render.rct_vehicle"
    bl_label = "Render RCT Vehicle"

    scene = None
    props = None

    def key_is_property(self, key):
        for sprite_track_flagset in self.props.sprite_track_flags_list:
            if sprite_track_flagset.section_id == key:
                return True

    def property_value(self, key):
        i = 0
        for sprite_track_flagset in self.props.sprite_track_flags_list:
            if sprite_track_flagset.section_id == key:
                return self.props.sprite_track_flags[i]
            i += 1

    def append_angles_to_rendertask(self, render_layer, inverted):
        start_anim = 0
        if self.scene.rct_graphics_helper_general_properties.number_of_animation_frames != 1:
            start_anim = 4
        anim_count = self.scene.rct_graphics_helper_general_properties.number_of_animation_frames
        for i in range(len(track_angle_sections_names)):
            key = track_angle_sections_names[i]
            track_section = track_angle_sections[key]
            if self.key_is_property(key):
                if self.property_value(key):
                    self.renderTask.add(track_section, render_layer, inverted, start_anim, anim_count)
            elif key == "VEHICLE_SPRITE_FLAG_GENTLE_SLOPE_BANKED_TURNS" or key == "VEHICLE_SPRITE_FLAG_GENTLE_SLOPE_BANKED_TRANSITIONS":
                if self.property_value("SLOPED_TURNS"):
                    self.renderTask.add(track_section, render_layer, inverted, start_anim, anim_count)
            elif key == "VEHICLE_SPRITE_FLAG_FLAT_TO_GENTLE_SLOPE_WHILE_BANKED_TRANSITIONS":
                if self.property_value("SLOPED_TURNS") and self.property_value("VEHICLE_SPRITE_FLAG_FLAT_BANKED"):
                    self.renderTask.add(track_section, render_layer, inverted, start_anim,anim_count)
            elif key == "VEHICLE_SPRITE_FLAG_DIAGONAL_GENTLE_SLOPE_BANKED_TRANSITIONS":
                if self.property_value("SLOPED_TURNS") and self.property_value("VEHICLE_SPRITE_FLAG_DIAGONAL_SLOPES"):
                    self.renderTask.add(track_section, render_layer, inverted, start_anim, anim_count)
            elif key == "VEHICLE_SPRITE_FLAG_FLAT_TO_GENTLE_SLOPE_BANKED_TRANSITIONS":
                if self.property_value("VEHICLE_SPRITE_FLAG_FLAT_BANKED") and self.property_value("VEHICLE_SPRITE_FLAG_GENTLE_SLOPES"):
                    self.renderTask.add(track_section, render_layer, inverted, start_anim, anim_count)
            elif key == "VEHICLE_SPRITE_FLAG_RESTRAINT_ANIMATION" and inverted == False:
                if self.props.restraint_animation:
                    self.renderTask.add(track_section, render_layer, inverted, 1, 3)
                    

    def execute(self, context):
        self.scene = context.scene
        self.props = self.scene.rct_graphics_helper_vehicle_properties

        self.renderTask = RenderTask(context.scene.rct_graphics_helper_general_properties.out_start_index, context)


        for i in range(context.scene.rct_graphics_helper_general_properties.number_of_rider_sets + 1):
            self.append_angles_to_rendertask(i, False)

            if self.props.inverted_set:
                self.append_angles_to_rendertask(i, True)

        return super(RenderVehicle, self).execute(context)
        
    def finished(self, context):
        super(RenderVehicle, self).finished(context)
        self.report({'INFO'}, 'RCT Vehicle render finished.')

class SpriteTrackFlag(object):
    name = ""
    description = ""
    default_value = False
    section_id = None

    def __init__(self, section_id, name, description, default_value):
        self.section_id = section_id
        self.name = name
        self.description = description
        self.default_value = default_value

class VehicleProperties(bpy.types.PropertyGroup):
    sprite_track_flags_list = []

    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_FLAT",
        "Flat", 
        "Render sprites for flat track", 
        True))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_GENTLE_SLOPES",
        "Gentle Slopes",
        "Render sprites for gentle sloped track",
        True))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_STEEP_SLOPES",
        "Steep Slopes",
        "Render sprites for steep sloped track",
        False))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_VERTICAL_SLOPES",
        "Vertical Slopes And Invert",
        "Render sprites for vertically sloped track and inverts",
        False))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_DIAGONAL_SLOPES",
        "Diagonal Slopes",
        "Render sprites for diagonal slopes",
        False))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_FLAT_BANKED",
        "Flat Banked",
        "Render sprites for flat banked track",
        False))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "SLOPED_TURNS",
        "Gentle Sloped Banked",
        "Render sprites for gently sloped banked track and turns",
        False))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_INLINE_TWISTS",
        "Inline twist",
        "Render sprites for the inline twist element",
        False))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_CORKSCREWS",
        "Corkscrew",
        "Render sprites for corkscrews",
        False))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_CURVED_LIFT_HILL",
        "Curved Lift Hill",
        "Render sprites for a curved lift hill",
        False))

    defaults = []
    for sprite_track_flag in sprite_track_flags_list:
        defaults.append(sprite_track_flag.default_value)

    sprite_track_flags = bpy.props.BoolVectorProperty(
        name = "Track Pieces",
        default = defaults,
        description = "Which track pieces to render sprites for",
        size = len(sprite_track_flags_list))

    restraint_animation = bpy.props.BoolProperty(
        name = "Restraint Animation",
        description = "Render with restraint animation. The restrain animation is 3 frames long and starts at frame 1",
        default = False)
        
    inverted_set = bpy.props.BoolProperty(
        name = "Inverted Set",
        description = "Used for rides which can invert for an extended amount of time like the flying and lay-down rollercoasters",
        default = False)

class VehiclesPanel(bpy.types.Panel):
    bl_label = "RCT Vehicles"
    bl_idname = "RENDER_PT_rct_vehicles"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properties = scene.rct_graphics_helper_vehicle_properties
        
        box = layout.box()

        row = box.row()
        row.label("Ride Vehicle Track Properties:")

        split = box.split(.50)
        columns = [split.column(), split.column()]
        i = 0
        for sprite_track_flagset in properties.sprite_track_flags_list:
            columns[i % 2].row().prop(properties, "sprite_track_flags", index = i, text = sprite_track_flagset.name)
            i += 1

        row = layout.row()
        row.prop(properties, "restraint_animation")
        
        row = layout.row()
        row.prop(properties, "inverted_set")

        row = layout.row()
        row.operator("render.rct_vehicle", text = "Render Vehicle")
        

      
def register_vehicles_panel():
    bpy.types.Scene.rct_graphics_helper_vehicle_properties = bpy.props.PointerProperty(type=VehicleProperties)
    
def unregister_vehicles_panel():
    del bpy.types.Scene.rct_graphics_helper_vehicle_properties