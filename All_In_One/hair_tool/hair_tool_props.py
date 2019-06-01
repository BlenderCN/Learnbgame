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
# from .hair_baking.hair_tree_update import handleHandlers

class hairUVPoints(bpy.types.PropertyGroup):
    start_point = bpy.props.FloatVectorProperty(name="", description="", default=(0.0, 0.0), size=2)
    end_point = bpy.props.FloatVectorProperty(name="", description="", default=(1.0, 1.0), size=2)

class hair_mesh_settings(bpy.types.PropertyGroup):
    hair_mesh_parent = StringProperty(name="", default="")
    hair_curve_child = StringProperty(name="", default="")
    hair_uv_points = bpy.props.CollectionProperty(type=hairUVPoints)
    uv_seed = IntProperty(name="UV Seed", default=20, min=1, max=1000)

class last_hair_settings(bpy.types.PropertyGroup):
    # material = StringProperty(name="", default="")
    material = bpy.props.PointerProperty(type=bpy.types.Material)
    hair_uv_points = bpy.props.CollectionProperty(type=hairUVPoints)

class ribbon_settings(bpy.types.PropertyGroup):
    strandResU = IntProperty(name="Segments U", default=3, min=1, max=5, description="Additional subdivision along strand length")
    strandResV = IntProperty(name="Segments V", default=2, min=1, max=5, description="Subdivisions perpendicular to strand length ")
    strandWidth = FloatProperty(name="Strand Width", default=0.5, min=0.0, max=10)
    strandPeak = FloatProperty(name="Strand peak", default=0.4, min=0.0, max=1,
                               description="Describes how much middle point of ribbon will be elevated")
    strandUplift = FloatProperty(name="Strand uplift", default=0.0, min=-1, max=1, description="Moves whole ribbon up or down")

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

    render_quality = bpy.props.EnumProperty(name="Bake Quality", default="2",
                                           items=(
                                               ("1", "Low", ""),
                                               ("2", "Normal", ""),
                                               ("4", "High", ""),
                                           ))
    bakeResolution = bpy.props.EnumProperty(name="Resolution", default="1024",
                                            items=(("256",  "256", ""),
                                                   ("512",  "512", ""),
                                                   ("1024", "1024", ""),
                                                   ("2048", "2048", ""),
                                                   ("4096", "4096", "")),
                                            )
    render_passes = bpy.props.EnumProperty(name="Pass", default={"NORMAL"},
                                           items=passes,
                                           options={'ENUM_FLAG'},
                                           update=update_materials)

    hair_bake_path = StringProperty(name="Bake Path", default="", description="Define the path where to Bake", subtype='DIR_PATH')
    hair_bake_file_name = StringProperty(name="Bake Name", default="Hair", description="Define output texture name")
    
    hair_bake_composite = BoolProperty(name="Composite Channels", default=False, description="Composite and pack bake maps channels")

    my_items = (
        ('PNG', "PNG", ""),
        ('TARGA', "TGA", "")
    )
    output_format = bpy.props.EnumProperty(name="Format", description="Format", items=my_items, default='PNG')


def register_properties():
    bpy.types.Object.hair_settings = bpy.props.PointerProperty(type=hair_mesh_settings)
    bpy.types.Scene.last_hair_settings = bpy.props.PointerProperty(type=last_hair_settings)
    bpy.types.Object.ribbon_settings = bpy.props.PointerProperty(type=ribbon_settings)
    bpy.types.Object.is_braid = bpy.props.BoolProperty(name="is_braid", default=False)
    bpy.types.Object.targetObjPointer = StringProperty(name="Target", description="Target of operation")
    bpy.types.Scene.GPSource = BoolProperty(name="Scene GreasePencil", description="Use Scene as Grease Pencil source if enabled \n" "otherwise use Object GP strokes.", default = True)
    bpy.types.Scene.hair_bake_settings = bpy.props.PointerProperty(type=hair_bake_settings)
    bpy.types.Scene.modal_hair = bpy.props.PointerProperty(type=ModalHairSettings)


def unregister_properties():
    del bpy.types.Scene.last_hair_settings
    del bpy.types.Object.hair_settings
    del bpy.types.Object.ribbon_settings
    del bpy.types.Object.targetObjPointer
    del bpy.types.Object.is_braid
    del bpy.types.Scene.GPSource
    del bpy.types.Scene.hair_bake_settings
    del bpy.types.Scene.modal_hair
