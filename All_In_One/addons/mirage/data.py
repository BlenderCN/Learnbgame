'''
Copyright (C) 2015 Diego Gangl
<diego@sinestesia.co>

Created by Diego Gangl. This file is part of Mirage.

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

import os

import bpy
from bpy.props import ( IntProperty, 
                        FloatProperty, 
                        BoolProperty, 
                        EnumProperty, 
                        StringProperty,
                        PointerProperty,
                        CollectionProperty )


import mirage

# Dict of Errors to check
errors = {}
errors['tree_performance'] = False
errors['heightmap_file'] = False

heightmap_icons = None
heightmap_count = 0


def get_prefs(pref):
    """ Get a specific value from addons preferences """

    try:
        addons = bpy.context.user_preferences.addons
        return getattr(addons[__package__].preferences, pref)

    except (TypeError, AttributeError, KeyError):
        # TODO: make this return a proper default value 
        # for different settings
        return "Mirage"


# This code is from the CAD Snap Utilities addon
# by Germano Cavalcante
def panel_category_hack(self, context):
    """ Set user selected categories for panel tabs """
    
    try:
        classes = [
                    MG_PT_Presets,
                    MG_PT_TerrainProcedural,
                    MG_PT_TerrainFile,
                    MG_PT_Trees,
                    MG_PT_Tools,
                  ]

        for cls in classes:
            bpy.utils.unregister_class(cls)
            cls.bl_category = data.get_prefs('tab')
            bpy.utils.register_class(cls)

    except:
        pass




def heightmap_enum_items(self, context):
    """ Generate enum for icons in heightmap """
    
    global heightmap_icons
    global heightmap_count

    items = []
    
    # Haven't loaded anything yet    
    if not heightmap_icons.paths:
        return items
    
    # Use cache if possible    
    if heightmap_count == len(heightmap_icons.cache):
        return heightmap_icons.cache
    
    for i, hmap in enumerate(heightmap_icons.paths):
        try:
            thumb = heightmap_icons.load(hmap, hmap, 'IMAGE')
        except: # Make specific when Blender is fixed
            thumb = heightmap_icons[hmap]

        items.append((hmap, hmap, "", thumb.icon_id, i))
              
    heightmap_icons.cache = items
    return items
    
    

def on_heightmap_enum_update(self, context):
    """ Set selected heightmap from icons to filepath """
    
    self.heightmap_filepath = self.heightmap_list
    

def on_custom_detail_update(self, context):
    """ Keep detail base grid at a sane size """

    try:
        if self.detail_custom < self.detail_base:
            self.detail_base = self.detail_custom

        mod = self.detail_custom % self.detail_base

        if mod % 2 > 0:
            self.detail_base += 1
            
    except RecursionError:
       return


    
def edges_enum_items(self, context):
    icons = mirage.icons_storage['main']
    items=(
         ('DEFAULT','No edges',
         'Don\'t change terrain edges',icons['edge_none'].icon_id ,0),    

         ('ISLAND','Island',
         'Apply smoothed edges and add an ocean',icons['edge_island'].icon_id ,1),    

         ('SMOOTH','Smoothed to plane',
         'Smooth terrain from center to edges',icons['edge_smoothed'].icon_id ,2),    
         
         ('STRAIGHT','Straight edge',
          'Set edges to zero without smoothing',icons['edge_straight'].icon_id ,3),    
          )

    return items



def settings(subset = None):
    """ Return settings object """
    
    settings = bpy.context.window_manager.mirage

    if subset is not None:
        return getattr(settings,subset)
    else:
        return settings
            


def register_terrain_features():
    """ Fill in values for terrain features """

    features = bpy.context.window_manager.mirage.terrain.features

    item = features.add()
    item.f_id = 'STRATA'
    item.name = 'Strata'
                                                  

    item = features.add()
    item.f_id = 'THERMAL'
    item.name = 'Thermal Erosion'
    
    item = features.add()
    item.f_id = 'SLOPES'
    item.name = 'Slopes'
    



class MG_PROP_FeatureItem(bpy.types.PropertyGroup):
    """ Group of properties representing an item in the list """

    f_id = StringProperty(
           name="Name",
           description="Feature name",
           default="Untitled")

    name = StringProperty(
           name="Name",
           description="Feature name",
           default="Untitled")




class MG_PROP_Trees(bpy.types.PropertyGroup):
    
    density = FloatProperty(
        name = "Density",
        default = 1000,
        description = 'Amount of trees',
        precision = 2,
        min = 1,
        max = 10000000.0,
    )
    
    
    max_slope = FloatProperty(
        name = "Maximum Slope",
        default = 0.5236, # 30º
        description = 'Maximum slope at which trees can grow',
        precision = 2,
        min = 0.0,
        max = 4.71245, # 270º
        subtype = 'ANGLE',
        unit = 'ROTATION',
    )

    
    max_height = FloatProperty(
        name = "Maximum Height",
        default = 90,
        description = 'Maximum height at which trees can grow',
        precision = 1,
        min = 0.0,
        max = 100.0,
        subtype = 'PERCENTAGE',
    )

    
    scale = FloatProperty(
        name = "Scale",
        default = 0.25,
        description = 'Size of the trees',
        precision = 2,
        min = 0.01,
        max = 10.0,
    )
    
    
    lock_scale_to_terrain = BoolProperty(
        name = "Use terrain scale",
        description = ('Calculate tree scale automatically'
                       ' from terrain scale'),
        default = False,
    )


    src_mesh = StringProperty(
        name = "Tree group",
        description = 'Group that holds the tree objects to use',
        default = '',
    )


    show_performance_help = BoolProperty(
        name = "Show performance help",
        default = False,
    )



class MG_PROP_PresetItem(bpy.types.PropertyGroup):

    name = StringProperty(
        name = "Name",
        description = 'Name for this preset',
        default = '',
    )

    description = StringProperty(
        name = "Description",
        description = 'Description of this preset',
        default = '',
    )

    filepath = StringProperty(
        name = "Path of the preset file",
        description = 'Preset file',
        default = '',
    )


class MG_PROP_Presets(bpy.types.PropertyGroup):

    preset_list = CollectionProperty(type = MG_PROP_PresetItem)

    index = IntProperty(
        name = "Preset Index",
        min = 0,
    )



class MG_PROP_Terrain(bpy.types.PropertyGroup):

    alpine = IntProperty(
        name = 'Alpine',
        default = 0,
        description = 'Increase peaks and flatten valleys',
        min = 0,
        max = 10,
    )
    
    roughness = IntProperty(
        name = "Roughness",
        default = 6,
        description = 'How rough or soft the terrain should be',
        min = 0,
        max = 10,
    )

    seed = IntProperty(
        name = "Seed",
        default = 1,
        description = ('Seed for terrain generation. ' 
                       'Different seeds produce different terrains'),
        min = 1,
        max = 2000000000,
    )

    max_height = FloatProperty(
        name = "Height (Max)",
        default = 3,
        precision = 2,
        description = 'Maximum height. Terrain will be scaled to fit this value',
        min = 0.01,
        max = 500.0,
        soft_max = 100.0,
        unit = 'LENGTH',
    )

   
    sea_level = FloatProperty(
        name = "Sea level",
        default = 0,
        precision = 2,
        description = 'Minimum height. Terrain will be cut off at this value.',
        min = 0,
        max = 100,
        unit = 'LENGTH',
    )


    plateau_level = FloatProperty(
        name = "Plateau",
        default = 10,
        precision = 2,
        description = 'Maximum height. Terrain will be cut off at this value.',
        min = 0.1,
        max = 500,
        soft_max = 100.0,
        unit = 'LENGTH',
    )


    auto_seed = BoolProperty(
        name = "Automatic Seed",
        description = 'Generate a new seed everytime a terrain is generated',
        default = True,
    )


    size = FloatProperty(
        name = "Size",
        description = 'Size of the terrain',
        min = 10.0,
        max = 10000.0,
        default = 100.0,
        unit='AREA',
        precision = 0,
        step = 100.0,
    )

    
    features = CollectionProperty(type = MG_PROP_FeatureItem)

    features_index = IntProperty(
        name = "Features Index",
        min = 0,
    )

    detail_level = EnumProperty(
        name = "Detail",
        description = 'Number of vertices to calculate for terrain mesh',
        items = ( 
                  ('7', '1. Normal', '128 segments'),
                  ('8', '2. Medium', '256 segments '),
                  ('9', '3. High', '512 segments'),
                  ('custom', 'Custom', 'Select a specific number of segments'),
                ),
        default = '7',
    )

    detail_custom = IntProperty(
        name = "Segments",
        description = ('Custom vertex count for terrain.'
                       ' Note this value might be rounded.'),
        default = 100,
        min = 100,
        max = 1000,
        update = on_custom_detail_update,
    )

    detail_base = IntProperty(
        name = "Seed Grid",
        description = ('Grid size for details.'
                       ' Changing this will change your terrain.'),
        default = 100,
        min = 100,
        max = 1000,
        update = on_custom_detail_update,
    )
   
   
    edges = EnumProperty(
        name = "Edges",
        items = edges_enum_items
    )


    edge_smoothed_factor = FloatProperty(
        name = "Smoothing Factor",
        description = 'Amount of smoothing to apply',
        default = 0.5,
        min = 0,
        max = 1,
    )
    
    
    # UI
    # --------------------------------------------------------------------------

    procedural_tab = EnumProperty(
        name = "Procedural tab",
        default = 'GENERAL',
        items=(
             ('GENERAL','General','Main Terrain settings'),    
             ('FEATURES','Features','Settings for specific features'),    
              )
        )


    progress = FloatProperty(
        name='Generation Progress', 
        description = 'Terrain Generation Progress',
        default = 0, 
        max = 100, 
        min = 0, 
        subtype='PERCENTAGE',  
        precision = 0
    )
    


    # Strata
    # --------------------------------------------------------------------------
    

    strata_strength = FloatProperty(
        name = "Strata strength",
        description = 'How much strata affects the terrain',
        default = 1,
        min = 0,
        soft_max = 1,
        max = 2,
    )
    

    strata_frequency = FloatProperty(
        name = "Strata frequency",
        description = 'How many layers of strata to include',
        default = 5,
        min = 0,
        soft_max = 6,
        max = 5,
    )


    strata_invert = BoolProperty(
        name = "Invert Slope",
        description = 'Invert the strata slope',
        default = True,
    )
    
    
    use_strata = BoolProperty(
        name = "Use Strata",
        description = 'Add a stratum effect for the terrain',
        default = False,
    )
    

    # Thermal Erosion
    # --------------------------------------------------------------------------
    
    
    use_thermal = BoolProperty(
        name = "Use Thermal Erosion",
        description = 'Simulate thermal erosion',
        default = False,
    )


    thermal_talus = FloatProperty(
        name = "Repose Angle",
        description = 'Angle at which material stops slumping',
        default = 0.7854,
        min = 0.5236,
        max = 0.7854,
        subtype = 'ANGLE',
        unit = 'ROTATION',
    )

    thermal_strength = IntProperty(
        name = "Strength",
        description = 'Strength of the erosion simulation',
        default = 4,
        min = 1,
        max = 10,
    )





    # Voronoi
    # --------------------------------------------------------------------------

    deformation = IntProperty(
        name = 'Deformation',
        description = 'Add twisting ridges and details',
        default = 5,
        min = 0,
        soft_max = 10,
        max = 20,
    )
    


    # Slopes
    # --------------------------------------------------------------------------
    use_slopes = BoolProperty(
        name = "Use Slopes",
        description = 'Apply a gradual change of height in one axis',
        default = False,
    )

    slope_X = IntProperty(
        name = "Intensity",
        description = 'Intensity of slope at axis X',
        default = 5,
        min = 0,
        max = 10,
    )

    slope_min_X = IntProperty(
        name = "Minimum Height",
        description = 'Minimum height on axis X',
        default = 0,
        min = 0,
        max = 10,
    )

    slope_invert_X = BoolProperty(
        name = "Invert Slope",
        description = 'Invert Slope direction on X',
        default = False,
    )

    slope_Y = IntProperty(
        name = "Intensity",
        description = 'Intensity of slope at axis Y',
        default = 5,
        min = 0,
        max = 10,
    )

    slope_min_Y = IntProperty(
        name = "Minimum Height",
        description = 'Minimum height on axis Y',
        default = 0,
        min = 0,
        max = 10,
    )

    slope_invert_Y = BoolProperty(
        name = "Invert Slope",
        description = 'Invert Slope direction on Y',
        default = False,
    )


    # Heightmap specific
    # --------------------------------------------------------------------------
        
    heightmap_detail   = IntProperty(
        name = 'Detail Level',
        description = 'Vertex amount in the mesh',
        default = 256,
        min = 100,
        max = 250000,
    ) 

    heightmap_strength = FloatProperty(
        name = "Strength",
        default = 1,
        description = ('Strength of the displacement. '
                      'This can be tweaked in the modifiers tab'),
        precision = 2,
        min = 0.01,
        max = 10.0,
    )
    

    heightmap_filepath = StringProperty(
        name = "Filepath",
        default = '',
        description = 'Path to the heightmap image',
        subtype = 'FILE_PATH',
    
    )

    
    heightmap_list = EnumProperty(
        name = "Heightmaps",
        items = heightmap_enum_items,
        update = on_heightmap_enum_update,
    )
    




class MG_PROP_Main(bpy.types.PropertyGroup):

    terrain = PointerProperty(
            type = MG_PROP_Terrain, 
            name = 'Terrain Settings', 
            description = 'Settings for terrain',
    )


    tree = PointerProperty(
            type = MG_PROP_Trees, 
            name = 'Tree Settings', 
            description = 'Settings for Tree distribution',
    )

    presets = PointerProperty(
            type = MG_PROP_Presets, 
            name = 'Presets', 
            description = 'Presets',
    )


class MG_OBJ_Terrain(bpy.types.PropertyGroup):
    
    generator = EnumProperty(
        name = "Generator",
        default = 'PROCEDURAL',
        items=(
             ('PROCEDURAL','Procedural','Generate Terrain Procedurally'),    
             ('DEM','Heightmap','Generate Terrain from DEM'),    
              )
    )
    
    seed = IntProperty(
        name = "Seed",
        default = 1,
        description = ('Seed for terrain generation. ' 
                       'Different seeds produce different terrains'),
        min = 1,
        max = 2000000000,
    )

    
class MG_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    tab = StringProperty (
            name        = "Panel's Tab",
            description = "3D View tab to put Mirage panels in",
            default     = "Mirage",
            update      = panel_category_hack
            )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "tab")
