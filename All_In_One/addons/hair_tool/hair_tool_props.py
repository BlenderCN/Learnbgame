# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python36\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb

import bpy
from bpy.props import StringProperty,IntProperty, FloatProperty, BoolProperty
from hair_tool.hair_baking.hair_bake import setup_pass
from .modal_particle_hair import ModalHairSettings
from .gpencil_to_curve import ModalGPSettings
# from .hair_baking.hair_tree_update import handleHandlers

class hairUVPoints(bpy.types.PropertyGroup):
    start_point: bpy.props.FloatVectorProperty(name="", description="", default=(0.0, 0.0), size=2)
    end_point: bpy.props.FloatVectorProperty(name="", description="", default=(1.0, 1.0), size=2)

class hair_mesh_settings(bpy.types.PropertyGroup):
    hair_mesh_parent: StringProperty(name="", default="")
    hair_curve_child: StringProperty(name="", default="")
    hair_uv_points: bpy.props.CollectionProperty(type=hairUVPoints)
    uv_seed: IntProperty(name="UV Seed", default=20, min=1, max=1000)

class last_hair_settings(bpy.types.PropertyGroup):
    # material: StringProperty(name="", default="")
    material: bpy.props.PointerProperty(type=bpy.types.Material)
    hair_uv_points: bpy.props.CollectionProperty(type=hairUVPoints)

class ribbon_settings(bpy.types.PropertyGroup):
    strandResU: IntProperty(name="Segments U", default=3, min=1, max=5, description="Additional subdivision along strand length")
    strandResV: IntProperty(name="Segments V", default=2, min=1, max=5, description="Subdivisions perpendicular to strand length ")
    strandWidth: FloatProperty(name="Strand Width", default=0.5, min=0.0, max=10)
    strandPeak: FloatProperty(name="Strand peak", default=0.4, min=0.0, max=1,
                               description="Describes how much middle point of ribbon will be elevated")
    strandUplift: FloatProperty(name="Strand uplift", default=0.0, min=-1, max=1, description="Moves whole ribbon up or down")

passes = (
    ("AO", "Ambient Occlusion", "Ambient Occlusion"),
    ("DIFFUSE", "Diffuse", "Diffuse mask"),
    ("OPACITY", "Opacity", "Opacity mask"),
    ("NORMAL", "Normal map", "Normal map"),
    ("ROOT", "Root map", "Gradient from hair root to tip"),
    ("ID", "Random ID mask", "Random color per hair strands"),
    ("TANGENT", "Tangent map", "Drives direction of anisotropic specular"),
    ("DEPTH", "Depth map", "Depth map"))
    

class hair_bake_settings(bpy.types.PropertyGroup):
    def update_materials(self, context):
        if len(self.render_passes)==1:
            setup_pass(self.render_passes.pop())

    def change_particle_step(self, context):
        particle_objs = [obj for obj in bpy.data.objects if obj.type=='MESH' and len(obj.particle_systems)]
        for particle_obj in particle_objs:
            for particle_system in particle_obj.particle_systems:
                if particle_system.settings.type == 'HAIR':
                    particle_system.settings.display_step = self.particle_display_step

    def change_particle_radius(self, context):
        particle_objs = [obj for obj in bpy.data.objects if obj.type=='MESH' and len(obj.particle_systems)]
        for particle_obj in particle_objs:
            for particle_system in particle_obj.particle_systems:
                if particle_system.settings.type == 'HAIR':
                    particle_system.settings.radius_scale = self.particle_width

    def change_particle_shape(self, context):
        particle_objs = [obj for obj in bpy.data.objects if obj.type=='MESH' and len(obj.particle_systems)]
        for particle_obj in particle_objs:
            for particle_system in particle_obj.particle_systems:
                if particle_system.settings.type == 'HAIR':
                    particle_system.settings.shape = self.particle_shape
                    
    render_quality: bpy.props.EnumProperty(name="Bake Quality", default="2",
                                           items=(
                                               ("1", "Low", ""),
                                               ("2", "Normal", ""),
                                               ("4", "High", ""),
                                           ))
    bakeResolution: bpy.props.EnumProperty(name="Resolution", default="1024",
                                            items=(("256",  "256", ""),
                                                   ("512",  "512", ""),
                                                   ("1024", "1024", ""),
                                                   ("2048", "2048", ""),
                                                   ("4096", "4096", ""),
                                                   ("8192", "8192", "")),
                                            )
    render_passes: bpy.props.EnumProperty(name="Pass", default={"NORMAL"},
                                           items=passes,
                                           options={'ENUM_FLAG'},
                                           update=update_materials)

    hair_bake_path: StringProperty(name="Bake Path", default="", description="Define the path where to Bake", subtype='DIR_PATH')
    hair_bake_file_name: StringProperty(name="Bake Name", default="Hair", description="Define output texture name")
    
    hair_bake_composite: BoolProperty(name="Composite Channels", default=False, description="Composite and pack bake maps channels")
    particle_display_step: IntProperty(name="Particle Display step", default=3, min=1, max=7, update = change_particle_step)
    particle_width: FloatProperty(name="Particle Width", default=0.01, min=0.001, max=0.1, update=change_particle_radius)
    particle_shape: FloatProperty(name="Particle Shape", default=0.0, min=-1.0, max=1.0, update=change_particle_shape)

    my_items = (
        ('PNG', "PNG", ""),
        ('TARGA', "TGA", "")
    )
    output_format: bpy.props.EnumProperty(name="Format", description="Format", items=my_items, default='PNG')


class hair_grid_settings(bpy.types.PropertyGroup):
    was_created_from_grid: BoolProperty(name="Created from Grid", description="Was current curve created from grid?", default=False)
    hairMethod: bpy.props.EnumProperty(name="Hair Method", default="edge",
                                        items=(("edge", "Edge Centers", ""),
                                               ("vert", "Vertex position", "")))
    hairType: bpy.props.EnumProperty(name="Hair Type", default="NURBS",
                                      items=(("BEZIER", "Bezier", ""),
                                             ("NURBS", "Nurbs", ""),
                                             ("POLY", "Poly", "")))
    bezierRes: IntProperty(name="Bezier resolution", default=3, min=1, max=12)
    t_in_x: IntProperty(name="Strands amount", default=10, min=1, soft_max=400)
    x_uniform: BoolProperty(name="Uniform Distribution", description="Uniform Distribution", default=True)
    noiseStrandSeparation: FloatProperty(name="Randomize Spacing", description="Randomize spacing between strands", default=0.3, min=0,
                                          max=1, subtype='PERCENTAGE')
    t_in_y: IntProperty(name="Strand Segments", default=7, min=3, soft_max=20)
    y_uniform: BoolProperty(name="Uniform Distribution", description="Uniform Distribution", default=True)
    shortenStrandLen: FloatProperty(name="Shorten Segment", description="Shorten strand length", default=0.1, min=0, max=1, subtype='PERCENTAGE')
    Seed: IntProperty(name="Noise Seed", default=1, min=1, max=1000)
    noiseMixFactor: FloatProperty(name="Noise Mix", description="Uniform vs non uniform noise", default=0.3, min=0,
                                   max=1, subtype='PERCENTAGE')
    noiseMixVsAdditive: BoolProperty(name="Mix additive", description="additive vs mix strand noise", default=False)
    noiseFalloff: FloatProperty(name="Noise falloff", description="Noise influence over strand lenght", default=0,
                                 min=-1, max=1, subtype='PERCENTAGE')
    snapAmount: FloatProperty(name="Snap Amount", default=0.5, min=0.0, max=1.0, subtype='PERCENTAGE')
    freq: FloatProperty(name="Noise freq", default=0.5, min=0.0, soft_max=5.0)
    strandFreq: FloatProperty(name="Strand freq", default=0.5, min=0.0, soft_max=5.0)
    noiseAmplitude: FloatProperty(name="Noise Amplitude", default=1.0, min=0.0, soft_max=10.0)
    offsetAbove: FloatProperty(name="Offset Strands", description="Offset strands above surface", default=0.1,
                                min=0.01, max=1.0)
    Radius: FloatProperty(name="Radius", description="Radius for bezier curve", default=1, min=0, soft_max=100)

    generateRibbons: BoolProperty(name="Generate Ribbons", description="Generate Ribbons on curve", default=False)
    strandResU: IntProperty(name="Segments U", default=3, min=1, max=5, description="Additional subdivision along strand length")
    strandResV: IntProperty(name="Segments V", default=2, min=1, max=5, description="Subdivisions perpendicular to strand length ")
    strandWidth: FloatProperty(name="Strand Width", default=0.5, min=0.0, soft_max=10)
    strandPeak: FloatProperty(name="Strand peak", default=0.4, min=0.0, max=1, description="Describes how much middle point of ribbon will be elevated")
    strandUplift: FloatProperty(name="Strand uplift", default=0.0, min=-1, max=1, description="Moves whole ribbon up or down")

    alignToSurface: BoolProperty(name="Align tilt", description="Align tilt to Surface", default=False)
    # new_int_method: BoolProperty(name="New interpol Method", description="New", default=True)
    clump_amount: FloatProperty(name="clump  Amount", default=0, min=0, max=1, description="clump Amount", subtype='PERCENTAGE')
    clump_Seed: IntProperty(name="Clump Seed", default=1, min=1, max=1000)
    clump_strength: FloatProperty(name="clump_strength", description="clump_strength", default=1, min=0,
            max=1, subtype='PERCENTAGE')
    clump_falloff: FloatProperty(name="clump_fallof", description="clump_fallof", default=0, min=-1.0,
            max=1, subtype='PERCENTAGE')



def register_properties():
    def update_func(self, context):
        if self.targetObjPointer[:3] == '   ':
            self['targetObjPointer'] = self.targetObjPointer[3:]

    bpy.types.Object.hair_settings = bpy.props.PointerProperty(type=hair_mesh_settings)
    bpy.types.Scene.last_hair_settings = bpy.props.PointerProperty(type=last_hair_settings)
    bpy.types.Object.ribbon_settings = bpy.props.PointerProperty(type=ribbon_settings)
    bpy.types.Object.hair_grid_settings = bpy.props.PointerProperty(type=hair_grid_settings)
    bpy.types.Object.is_braid = bpy.props.BoolProperty(name="is_braid", default=False)
    bpy.types.Object.targetObjPointer = StringProperty(name="Target", description="Target of operation", update=update_func)
    bpy.types.Scene.GPSource = BoolProperty(name="Scene GreasePencil", description="Use Scene as Grease Pencil source if enabled \n" "otherwise use Object GP strokes.", default = True)
    bpy.types.Scene.hair_bake_settings = bpy.props.PointerProperty(type=hair_bake_settings)
    
    bpy.types.Object.modal_hair = bpy.props.PointerProperty(type=ModalHairSettings)
    bpy.types.Scene.modal_gp_curves = bpy.props.PointerProperty(type=ModalGPSettings)


def unregister_properties():
    del bpy.types.Scene.last_hair_settings
    del bpy.types.Object.hair_settings
    del bpy.types.Object.ribbon_settings
    del bpy.types.Object.hair_grid_settings
    del bpy.types.Object.targetObjPointer
    del bpy.types.Object.is_braid
    del bpy.types.Scene.GPSource
    del bpy.types.Scene.hair_bake_settings
    del bpy.types.Object.modal_hair
