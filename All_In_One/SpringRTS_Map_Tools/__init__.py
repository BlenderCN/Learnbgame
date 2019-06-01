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
    "name": "SpringRTS Map Tools",
    "author": "Samuel Nicholas",
    "blender": (2, 6, 3),
    "location": "File > Import-Export, properties->scene",
    "description": "Various utilities for creating maps for Spring RTS Engine ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    if "springrts_map_export_features" in locals():
        imp.reload(stringrts_feature_ui)
    if "springrts_map_import_features" in locals():
        imp.reload(stringrts_feature_import)
    if "springrts_map_render" in locals():
        imp.reload(stringrts_feature_export)


import bpy, os, re

from bpy_extras.io_utils import ExportHelper,ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from . import springrts_map_features_export, springrts_map_features_import

class ImportSpringRTSMapInfo(Operator, ExportHelper):
    """Save SpringRTS Map Info"""
    bl_idname = "export_scene.springrts_mapinfo"
    bl_label = 'Export SpringRTS Map Info'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.*",
            options={'HIDDEN'},
            )

    def execute(self, context):
        print("Export SpringRTS Map Info")
        return {'FINISHED'}
#        return springrts_map_bits.export_mapinfo(context, self.filepath)

class ImportSpringRTSMapFeatures(Operator, ImportHelper):
    """Load SpringRTS Map feature locations"""
    bl_idname = "import_scene.springrts_map_features"
    bl_label = "Import SpringRTS Map Features"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".lua"
    filter_glob = StringProperty(
            default="*.lua",
            options={'HIDDEN'},
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    size_x = bpy.props.IntProperty(
            name="Map Width(x)",
            description="The Width of the map in SpringRTS map units",
            min=2, max=64,
            soft_min=4, soft_max=32,
            step=2,
            default=8,
            )

    size_z = bpy.props.IntProperty(
            name="Map Length(z)",
            description="The Length of the map in SpringRTS map units",
            min=2, max=64,
            soft_min=4, soft_max=32,
            step=2,
            default=8,
            )

    def execute(self, context):
        return springrts_map_features_import.load(
            context, self.filepath, self.size_x, self.size_z)

class ExportSpringRTSMapInfo(Operator, ExportHelper):
    """Save SpringRTS Map Info"""
    bl_idname = "export_scene.springrts_mapinfo"
    bl_label = 'Export SpringRTS Map Info'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.*",
            options={'HIDDEN'},
            )

    def execute(self, context):
        print("Export SpringRTS Map Info")
        return springrts_map_bits.export_mapinfo(self, context)

class ExportSpringRTSMapFeatures(Operator, ExportHelper):
    """Save SpringRTS Map Feature locations"""
    bl_idname = "export_scene.springrts_map_features"
    bl_label = 'Export SpringRTS Map Features'

    filename_ext = ".lua"
    filter_glob = StringProperty(
            default="*.*",
            options={'HIDDEN'},
            )

    exportType = bpy.props.EnumProperty(
        name        = "Export",
        description = "What to export",
        items = ( ( 'particles', "Particles", "Particle systems of the active object" ),
                  ( 'selection', "Selection", "All objects selected" ) ),
        default = 'particles'
        )

    def execute(self, context):
        print("==Export SpringRTS Map Features==")
        return springrts_map_features_export.export(self, context)

###################
# Other Operators #
###################

class SpringRTSMap(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "SpringRTS Map Attributes"
    bl_idname = "SCENE_PT_SME_Attributes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        smp = context.scene.smp

        layout.label(text=" Attributes:")
        row = layout.row()
        row.prop(smp, 'name')        
        row = layout.row()
        row.prop(smp, 'shortName')
        row.prop(smp, 'version')
        row = layout.row()
        row.prop(smp, 'description')
        row = layout.row()
        row.prop(smp, 'authors')
        row = layout.row()
        row.prop(smp, 'deformable')
        row = layout.row()
        row.prop(smp, 'width')
        row = layout.row()
        row.prop(smp, 'length')
        row = layout.row()
        row.prop(smp, 'hardness')
        row = layout.row()
        row.prop(smp, 'gravity')
        row = layout.row()
        row.prop(smp, 'tidalStrength')
        row = layout.row()
        row.prop(smp, 'maxMetal')
        row = layout.row()
        row.prop(smp, 'extractorRadius')
        row = layout.row()
        row.prop(smp, 'voidWater')
        row = layout.row()
        row.prop(smp, 'showMetal')
        row = layout.row()
        row.prop(smp, 'minHeight')
        row = layout.row()
        row.prop(smp, 'maxHeight')

######################
# Map Property Group #
######################

class SpringRTSMapPropertyGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty( name = "Name")

    shortName = bpy.props.StringProperty(
        name = "Short Name",
        description = "Short Name of the Map")

    description = bpy.props.StringProperty(
        name = "Description",
        description = "Description of the map")

    authors = bpy.props.StringProperty(
        name = "Credits",
        description = "Names of people credited to have worked on the map")

    version = bpy.props.StringProperty(
        name = "Version",
        description = "Version information")

#Properties
    deformable = bpy.props.BoolProperty(
        name="Deformable",
        description = "if the terrain will be effected by explosions",
        default = True)

    width = bpy.props.IntProperty(
        name = "Width",
        description = "X Dimension of the map",
        subtype = 'UNSIGNED',
        min = 2,
        max = 64,
        step = 2,
        default = 8)

    length = bpy.props.IntProperty(
        name = "Length",
        description = "Z Dimension of the map",
        subtype = 'UNSIGNED',
        min = 2,
        max = 64,
        step = 2,
        default = 8)

    hardness = bpy.props.IntProperty(
        name = "Hardness",
        description = "How resistant the map is to deforming",
        subtype = 'UNSIGNED',
        min = 1,
        default = 1000)

    gravity = bpy.props.IntProperty(
        name="Gravity",
        description = "Gravity in Centimeters per second",
        subtype = 'UNSIGNED',
        min = 0,
        default = 130)

    tidalStrength = bpy.props.IntProperty(
        name="Tidal Strength",
        description = "Strength of the tide, for tidal power generators",
        subtype = 'UNSIGNED',
        min = 0,
        default = 20)

    maxMetal = bpy.props.FloatProperty(
        name="Maximum Metal",
        description = "The Maximum value of metal from any spot.",
        default = 0.21)

    extractorRadius = bpy.props.FloatProperty(
        name="Extractor Radius",
        description = "shouldnt this be set by the mod? doesnt seem like a mappy thing.",
        min = 1.0,
        default = 100.0)

    voidWater = bpy.props.BoolProperty(
        name = "Void Water",
        description = "creates empty space where water is, good for space maps",
        default = False)

    showMetal = bpy.props.BoolProperty(
        name = "Auto Show Metal",
        description = "not really sure. probably shouldnt be set by the map.",
        default = True)

# Terrain Settings(smf)
    minHeight = bpy.props.IntProperty(
        name = "Min Height",
        description = "The distance below the water level that black on the heightmap represents",
        default = 10)

    maxHeight = bpy.props.IntProperty(
        name = "Max Height",
        description = "The distance above the water level that white on the heightmap represents",
        default = 522)

# splats
    
#    bpy.types.Scene.MapMaxHeight = bpy.props.StringProperty(
 #       name = "Splat Distribution texture",
  #      description = "The distance above the water level that white on the heightmap represents",
   #     default = 522)

#    bpy.types.Scene.MapMaxHeight = bpy.props.IntProperty(
 #       name = "Max Height",
  #      description = "The distance above the water level that white on the heightmap represents",
   #     default = 522)


#Export Functions
def menu_func_export_features(self, context):
    self.layout.operator(ExportSpringRTSMapFeatures.bl_idname, text="SpringRTS Map Features")

def menu_func_export_mapinfo(self, context):
    self.layout.operator(ExportSpringRTSMapInfo.bl_idname, text="SpringRTS Map Info")

# Import Functions
def menu_func_import_features(self, context):
    self.layout.operator(ImportSpringRTSMapFeatures.bl_idname, text="SpringRTS Map Features")

def menu_func_import_mapinfo(self, context):
    self.layout.operator(ImportSpringRTSMapInfo.bl_idname, text="SpringRTS Map Info")


def register():
#    bpy.utils.register_module(__name__)

    # Reister Map Property Group
    bpy.utils.register_class(SpringRTSMapPropertyGroup)
    bpy.types.Scene.smp = bpy.props.PointerProperty(
        type=SpringRTSMapPropertyGroup)

    # Register Export Operators
    bpy.utils.register_class(ExportSpringRTSMapFeatures)
    bpy.types.INFO_MT_file_export.append(menu_func_export_features)
#    bpy.utils.register_class(ExportSpringRTSMapInfo)
#    bpy.types.INFO_MT_file_export.append(menu_func_export_mapinfo)

    # Register Import Operators
    bpy.utils.register_class(ImportSpringRTSMapFeatures)
    bpy.types.INFO_MT_file_import.append(menu_func_import_features)
#    bpy.utils.register_class(ImportSpringRTSMapInfo)
#    bpy.types.INFO_MT_file_import.append(menu_func_import_mapinfo)

    # Register Other Operators
    # Register Scene Menu panels
    bpy.utils.register_class(SpringRTSMap)


def unregister():
    bpy.utils.unregister_module(__name__)

    # Unregister Export Operators
    bpy.utils.unregister_class(ExportSpringRTSMapFeatures)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_features)
#    bpy.utils.unregister_class(ExportSpringRTSMapInfo)
#    bpy.types.INFO_MT_file_export.remove(menu_func_export_mapinfo)

    # Unregister Import Operators
    bpy.utils.unregister_class(ImportSpringRTSMapFeatures)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_features)
#    bpy.utils.unregister_class(ImportSpringRTSMapInfo)
#    bpy.types.INFO_MT_file_import.remove(menu_func_import_mapinfo)

    bpy.utils.unregister_class(SpringRTSMap)

    bpy.utils.unregister_class(SpringRTSMapPropertyGroup)

if __name__ == "__main__":
    register()
