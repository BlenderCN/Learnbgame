# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "SpringRTS Feature Tools",
    "author": "Samuel Nicholas",
    "blender": (2, 6, 3),
    "location": "File > Import-Export, properties->scene",
    "description": "Import-Export , feature properties ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy, os, re
from bpy_extras.io_utils import ExportHelper,ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from . import (
    springrts_feature_bits,
    springrts_feature_import,
    springrts_feature_export,
    springrts_feature_presets
)

#############
# Operators #
#############
class SpringRTSFeatureCVScaleCalc(Operator):
    """Calculate the Collision Volume Scale of feature"""
    bl_idname = "springrts_feature.cv_scale_calc"
    bl_label = "Calculate SpringRTS Feature Collision Volume Scale"

    def execute(self, context):
        springrts_feature_bits.cv_scale_calc(self, context)
        return {'FINISHED'}

class SpringRTSFeatureCVOffsetCalc(Operator):
    """Calculate the collision volume offset of feature"""
    bl_idname = "springrts_feature.cv_offset_calc"
    bl_label = "Calculate SpringRTS Feature Collision Volume Offset"

    def execute(self, context):
        springrts_feature_bits.cv_offset_calc(self, context)
        return {'FINISHED'}

class SpringRTSFeatureOVRadiusCalc(Operator):
    """Calculate the occlusion volume radius of feature"""
    bl_idname = "springrts_feature.ov_radius_calc"
    bl_label = "Calculate SpringRTS Feature Occlusion Volume Radius"

    def execute(self, context):
        springrts_feature_bits.ov_radius_calc(self, context)
        return {'FINISHED'}

class SpringRTSFeatureOVMidposCalc(Operator):
    """Calculate the occlusion volume midpos of feature"""
    bl_idname = "springrts_feature.ov_midpos_calc"
    bl_label = "Calculate SpringRTS Feature Occlusion Volume Midpos"

    def execute(self, context):
        springrts_feature_bits.ov_midpos_calc(self, context)
        return {'FINISHED'}

class ImportSpringRTSFeature(Operator, ImportHelper):
    """Load a SpringRTS feature"""
    bl_idname = "import_object.springrts_feature"
    bl_label = "Import SpringRTS Feature"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".lua"
    filter_glob = StringProperty(
            default="*.lua",
            options={'HIDDEN'},
            )

    def execute(self, context):
        print("== Import SpringRTS feature ==")
        return springrts_feature_import.load(context, self.filepath)

class ExportSpringRTSFeature(Operator, ExportHelper):
    """Save a SpringRTS Feature"""
    bl_idname = "export_object.springrts_feature"
    bl_label = 'Export SpringRTS Feature'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.*",
            options={'HIDDEN'},
            )

    invertUV = bpy.props.BoolProperty(
        name = "Invert UV's",
        description = "Invert uv coordinates",
        default = False
        )

    overwrite = bpy.props.BoolProperty(
        name = "Overwrite",
        description = "whether to overwrite existing files",
        default = True
        )

    def execute(self, context):
        print("== Export SpringRTS feature ==")
        return springrts_feature_export.export(self, context)

#########################
# User Interface Panels #
#########################

class SpringRTSFeature(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "SpringRTS Feature"
    bl_idname = "SCENE_PT_SFE_Attributes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw_header(self, context):
        layout = self.layout
        sfp = context.object.sfp
        # FIXME Switch on or off feature panels

    def draw(self, context):
        layout = self.layout
        sfp = context.object.sfp


        layout.prop(context.object, 'name')
        layout.prop(sfp, 'description')
        layout.prop(sfp, 'preset')
        row = layout.row()
        col1 = row.split()
        column = col1.column()
        column.prop(sfp, 'damage')
        column.prop(sfp, 'metal')
        column.prop(sfp, 'energy')
        column = row.column()
        column.prop(sfp, 'mass')
        column.prop(sfp, 'crushResistance')
        column.prop(sfp, 'reclaimTime')

        box = layout.box()
        row = box.row()
        row.prop(sfp, 'indestructible')
        row.prop(sfp, 'flammable')
        row = box.row()
        row.prop(sfp, 'reclaimable')
        row.prop(sfp, 'autoReclaimable')
        row = box.row()
        row.prop(sfp, 'featureDead')
        row = box.row()
        row.prop(sfp, 'smokeTime')
        row = box.row()
        row.prop(sfp, 'resurrectable')
        row = box.row()
        row.prop(sfp, 'upright')
        row.prop(sfp, 'floating')
        row = box.row()
        row.prop(sfp, 'geothermal')
        row.prop(sfp, 'noSelect')

        box = layout.box()
        row = box.row()
        row.label(text="Footprint:")
        row.prop(sfp, 'footprint', "Show")
        row = box.row(align=True)
        row.prop(sfp, 'blocking')
        row.prop(sfp, 'footprintX')
        row.prop(sfp, 'footprintZ')

        box = layout.box()
        row = box.row()
        row.label(text="Collision Volume:")
        row.prop(sfp, 'collisionVolume')
        row = box.row()
        row.prop(sfp, 'collisionVolumeType')
        row.prop(sfp, 'collisionEditMode')
        row = box.row()
        row.active = sfp.collisionEditMode != 'grab'
        row.prop(sfp, 'collisionVolumeScales')
        row.operator('springrts_feature.cv_scale_calc', "Recalc")
        row = box.row()
        row.active = sfp.collisionEditMode != 'grab'
        row.prop(sfp, 'collisionVolumeOffsets')
        row.operator('springrts_feature.cv_offset_calc', "Recalc")

        box = layout.box()
        row = box.row()
        row.label("Occlusion Volume")
        row.prop(sfp, 'occlusionVolume', "Show")
        row = box.row()
        row.prop(sfp, 'occlusionEditMode')
        row = box.row()
        row.active = sfp.occlusionEditMode != 'grab'
        row.prop(sfp, 'radius')
        row.operator('springrts_feature.ov_radius_calc', "Recalc")
        row = box.row()
        row.active = sfp.occlusionEditMode != 'grab'
        row.prop(sfp, 'midpos')
        row.operator('springrts_feature.ov_midpos_calc', "Recalc")

##########################
# Feature Property Group #
##########################

class SpringRTSFeaturePropertyGroup(bpy.types.PropertyGroup):
    # FIXME isFeature = bpy.props.BoolProperty(name="Enable") turn on and off feature panels.
    description = bpy.props.StringProperty(name="Description")

#General
    damage = bpy.props.FloatProperty(
        name="Damage",
        description = "How much damage this feature can take before"
            "being destroyed.",
        min = 0.0,
        default = 0,
        precision = 3)

# Attributes
    metal = bpy.props.FloatProperty(
        name = "Metal",
        description = "Amount of metal this feature gives when reclaimed.",
        default = 0.0,
        min = 0.0)

    energy = bpy.props.FloatProperty(
        name = "Energy",
        description = "Amount of energy this feature gives when reclaimed.",
        default = 0.0,
        min = 0.0)

    mass = bpy.props.FloatProperty(
        name = "Mass",
        description = "The mass of the feature.",
        default = 1.0,
        min = 1.0,
        precision = 3)

    crushResistance = bpy.props.FloatProperty(
        name = "Crush Resistance",
        description = "How resistant is the feature to being crushed.",
        min = 0.0,
        precision = 3)

    reclaimTime = bpy.props.FloatProperty(
        name = "Reclaim Time",
        description = "The time taken to reclaim this feature.")

# Options
    indestructible = bpy.props.BoolProperty(
        name="Indestructible",
        description = "Can the feature take damage?")

    flammable = bpy.props.BoolProperty(
        name = "Flammable",
        description = "Can the feature be set on fire?")

    reclaimable = bpy.props.BoolProperty(
        name = "Reclaimable",
        description = "Can be reclaimed by a construction unit?",
        default = True)

    autoReclaimable = bpy.props.BoolProperty(
        name = "Auto Reclaim",
        description = "Can be be reclaimed by a construction"
            "unit executing a patrol or area-reclaim command?",
        default = True)

    featureDead = bpy.props.StringProperty(
        name = "Death Feature",
        description = "The featureName of the feature to spawn when this"
            "feature is destroyed.")

    smokeTime = bpy.props.IntProperty(
        name = "Smoke Time",
        description = "How many frames a corpse feature should emit smoke"
            "for after unit death.",
        default = 300,
        min = 0)

    resurrectable = bpy.props.EnumProperty(
        name = "Resurrectable",
        items = (('first',"First Corpse","Only if feature is in first level decay"),
            ('no',"No", "feature is not able to be resurrected"),
            ('yes', "Yes", "Unit is always able to be resurrected")),
        description = "Can this feature be resurrected?")

    upright = bpy.props.BoolProperty(
        name = "Upright",
        description = "Tilt with the slope of the terrain or stay upright?")

    floating = bpy.props.BoolProperty(
        name = "Float",
        description = "Float on top of water or sit on the seabed?")

    geothermal = bpy.props.BoolProperty(
        name = "Geothermal Vent",
        description = "Does this feature act as a geothermal vent?")

    noSelect = bpy.props.BoolProperty(
        name = "No Select",
        description = "If true the cursor won't change to `reclaim` when"
            "hovering the feature.")

# Footprint
    footprint = bpy.props.BoolProperty(
        name = "Show Footprint",
        description = "Turn on visual for footprint.",
        default = False,
        update = springrts_feature_bits.update_footprint)

    blocking = bpy.props.BoolProperty(
        name = "Blocking",
        description = "Does this feature block unit movement and is ignored"
            "by weapon aiming",
        default = True)

    footprintX = bpy.props.IntProperty(
        name = "Footprint X",
        description = "How wide the feature is, for pathfinding and blocking.",
        default = 1,
        min = 1,
        update = springrts_feature_bits.update_footprint)

    footprintZ = bpy.props.IntProperty(
        name = "Footprint Z",
        description = "How wide the feature is, for pathfinding and blocking.",
        default = 1,
        min = 1,
        update = springrts_feature_bits.update_footprint)

# Collision Volume
    collisionVolume = bpy.props.BoolProperty(
        name = "Show",
        description = "Turn on visual for Collision Volume.",
        default = False,
        update = springrts_feature_bits.update_collision_volume)

    collisionVolumeType = bpy.props.EnumProperty(
        name = "Type",
        items = (('SME_box',"Box","Simple Box"),
            ('SME_ellipsoid',"Ellipsoid","Spherical like object"),
            ('SME_cylX',"Cylinder X","X Axis Aligned Cylinder"),
            ('SME_cylY',"Cylinder Y","Y Axis Aligned Cylinder"),
            ('SME_cylZ',"Cylinder Z","Z Axis Aligned Cylinder")),
        description = "The Shape of the collision volume",
        update = springrts_feature_bits.update_collision_volume)

    collisionEditMode = bpy.props.EnumProperty(
        name = "Edit Mode",
        items = (('manual',"Manual","Enter Values Manually"),
            ('grab',"Grab","Transform the volume in 3d view"),),
        description = "Collision Volume Edit Mode",
        update = springrts_feature_bits.update_collision_volume)

    collisionVolumeScales = bpy.props.FloatVectorProperty(
        name = "Scale",
        description = "The lengths of the collision volume in each axis",
        default = (1.0,1.0,1.0),
        min = 0.01,
        update = springrts_feature_bits.update_collision_volume)

    collisionVolumeOffsets = bpy.props.FloatVectorProperty(
        name = "Offset",
        description = "The offset from the unit centre to the hit volume"
            "centre in each axis",
        update = springrts_feature_bits.update_collision_volume)

# Mesh
    tex1 = bpy.props.StringProperty(name = "tex1",
        description = "RGB diffuse and team overlay")

    tex2 = bpy.props.StringProperty(name = "tex2",
        description = "ambient, specular, unused and alpha")

    occlusionVolume = bpy.props.BoolProperty(
        name = "Show",
        description = "Turn on visual for occlusion Volume.",
        default = False,
        update = springrts_feature_bits.update_occlusion_volume)

    occlusionEditMode = bpy.props.EnumProperty(
        name = "Edit Mode",
        items = (('manual',"Manual","Enter Values Manually"),
            ('grab',"Grab","Transform the occlusion volume in 3d view"),),
        description = "Occlusion Volume Edit Mode",
        update = springrts_feature_bits.update_occlusion_volume)

    radius = bpy.props.FloatProperty(
        name="Radius",
        description = "",
        min = 0.01,
        default = 1,
        precision = 3,
        update = springrts_feature_bits.update_occlusion_volume)

    midpos = bpy.props.FloatVectorProperty(
        name="Mid Point",
        description = "",
        update = springrts_feature_bits.update_occlusion_volume)

    preset = bpy.props.EnumProperty(
        name = "Preset",
        items = springrts_feature_presets.presets,
        description = "Feature Preset",
        update = springrts_feature_presets.preset_choose)


###################################################
# Functions cause i was copying obj way of things #
###################################################

def menu_func_import(self, context):
    self.layout.operator(ImportSpringRTSFeature.bl_idname, text="SpringRTS Feature")


def menu_func_export(self, context):
    self.layout.operator(ExportSpringRTSFeature.bl_idname, text="SpringRTS Feature")

################
# Registration #
################

def register():
#    bpy.utils.register_module(__name__)

    # Register and use feature property group
    bpy.utils.register_class(SpringRTSFeaturePropertyGroup)
    bpy.types.Object.sfp = bpy.props.PointerProperty(
        type=SpringRTSFeaturePropertyGroup)

    # Register export operator
    bpy.utils.register_class(ExportSpringRTSFeature)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

    # Register import operator
    bpy.utils.register_class(ImportSpringRTSFeature)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

    # Register other operators
    bpy.utils.register_class(SpringRTSFeatureOVRadiusCalc)
    bpy.utils.register_class(SpringRTSFeatureOVMidposCalc)
    bpy.utils.register_class(SpringRTSFeatureCVScaleCalc)
    bpy.utils.register_class(SpringRTSFeatureCVOffsetCalc)

    # Register Scene Menu Panels
    bpy.utils.register_class(SpringRTSFeature)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

    bpy.utils.unregister_class(ExportSpringRTSFeature)
    bpy.utils.unregister_class(ImportSpringRTSFeature)
    bpy.utils.unregister_class(SpringRTSFeaturePropertyGroup)

    # Unregister other operators
    bpy.utils.unregister_class(SpringRTSFeatureOVRadiusCalc)
    bpy.utils.unregister_class(SpringRTSFeatureOVMidposCalc)
    bpy.utils.unregister_class(SpringRTSFeatureCVScaleCalc)
    bpy.utils.unregister_class(SpringRTSFeatureCVOffsetCalc)

    bpy.utils.unregister_class(SpringRTSFeature)

if __name__ == "__main__":
    register()
