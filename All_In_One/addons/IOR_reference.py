# ## BEGIN GPL LICENSE BLOCK ##
#
#   Copyright (C) 2017 Diego Gangl
#   <diego@sinestesia.co>
#
#   Copyright (C) 2017 Emmanuel Boyer
#
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ## END GPL LICENSE BLOCK ##

""" IOR Reference Addon """

import bpy
from bpy.props import (StringProperty, FloatProperty,
                       IntProperty, CollectionProperty)

bl_info = {
    'name': 'IOR Reference Fork Emmanuel',
    'description': 'Adds a panel with a searchable list of IOR values',
    'author': 'Diego Gangl, Emmanuel Boyer',
    'version': (1, 0, 0),
    'blender': (2, 75, 0),
    'location': 'Nodes',
    'warning': '',
    'wiki_url': '',
    'category': 'Material'
}


# -----------------------------------------------------------------------------
# VALUES
# -----------------------------------------------------------------------------

class IORREF_PROP_Value(bpy.types.PropertyGroup):
    name = StringProperty(
        name='Name',
        description='Material name')

    value = FloatProperty(
        name='IOR Value',
        precision=3,
        description='The IOR value for the selected item')


def build_IOR_list():
    """ Fill the list with IOR values """

    def add(val):
        item = bpy.context.window_manager.IORRef.add()
        item.name = val[0]
        item.value = val[1]

    # BEGIN List of IOR values
    IOR_list = [
        ('Acetone', 1.36),
        ('Actinolite', 1.618),
        ('Agate', 1.544),
        ('Agate, Moss', 1.540),
        ('Air 20°', 1.000377),
        ('Air 45°', 1.0003402),
        ('Air 20°', 1.000272),
        ('Air 0°', 1.0002926),
        ('Alcohol', 1.329),
        ('Alexandrite', 1.745),
        ('Aluminum', 1.44),
        ('Amber', 1.546),
        ('Amblygonite', 1.611),
        ('Amethyst', 1.544),
        ('Anatase', 2.490),
        ('Andalusite', 1.641),
        ('Anhydrite', 1.571),
        ('Apatite', 1.632),
        ('Apophyllite', 1.536),
        ('Aquamarine', 1.577),
        ('Aragonite', 1.530),
        ('Argon', 1.000281),
        ('Asphalt', 1.635),
        ('Augelite', 1.574),
        ('Axinite', 1.675),
        ('Azurite', 1.730),
        ('Barite', 1.636),
        ('Barytocalcite', 1.684),
        ('Benitoite', 1.757),
        ('Benzene', 1.501),
        ('Beryl', 1.577),
        ('Beryllonite', 1.553),
        ('Brazilianite', 1.603),
        ('Bromine (liq)', 1.661),
        ('Bronze', 1.18),
        ('Calcite', 1.486),
        ('Cancrinite', 1.491),
        ('Carbon Dioxide (gas)', 1.000449),
        ('Carbon Disulfide', 1.628),
        ('Carbon Tetrachloride', 1.460),
        ('Cassiterite', 1.997),
        ('Celestite', 1.622),
        ('Cerussite', 1.804),
        ('Ceylanite', 1.770),
        ('Chalcedony', 1.530),
        ('Chalk', 1.510),
        ('Chalybite', 1.630),
        ('Chlorine (gas)', 1.000768),
        ('Chlorine (liq)', 1.385),
        ('Chrome Green', 2.4),
        ('Chrome Red', 2.42),
        ('Chrome Yellow', 2.31),
        ('Chromium', 2.97),
        ('Chrysoberyl', 1.745),
        ('Chrysocolla', 1.500),
        ('Chrysoprase', 1.534),
        ('Citrine', 1.550),
        ('Clinozoisite', 1.724),
        ('Cobalt Blue', 1.74),
        ('Cobalt Green', 1.97),
        ('Cobalt Violet', 1.71),
        ('Colemanite', 1.586),
        ('Copper', 1.10),
        ('Copper Oxide', 2.705),
        ('Coral', 1.486),
        ('Cordierite', 1.540),
        ('Corundum', 1.766),
        ('Crocoite', 2.310),
        ('Crystal', 2.00),
        ('Cuprite', 2.850),
        ('Danburite', 1.633),
        ('Diamond', 2.417),
        ('Diopside', 1.680),
        ('Dolomite', 1.503),
        ('Dumortierite', 1.686),
        ('Ebonite', 1.66),
        ('Ekanite', 1.600),
        ('Elaeolite', 1.532),
        ('Emerald', 1.576),
        ('Emerald, Synth flux', 1.561),
        ('Emerald, Synth hydro', 1.568),
        ('Enstatite', 1.663),
        ('Epidote', 1.733),
        ('Ethanol', 1.36),
        ('Ethyl Alcohol', 1.36),
        ('Euclase', 1.652),
        ('Feldspar, Adventurine', 1.532),
        ('Feldspar, Albite', 1.525),
        ('Feldspar, Amazonite', 1.525),
        ('Feldspar, Labradorite', 1.565),
        ('Feldspar, Microcline', 1.525),
        ('Feldspar, Oligoclase', 1.539),
        ('Feldspar, orthoclase', 1.525),
        ('Fluoride', 1.56),
        ('Fluorite', 1.434),
        ('Formica', 1.47),
        ('Garnet, Almandine', 1.760),
        ('Garnet, Almandite', 1.790),
        ('Garnet, Andradite', 1.820),
        ('Garnet, Demantoid', 1.880),
        ('Garnet, Grossular', 1.738),
        ('Garnet, Hessonite', 1.745),
        ('Garnet, Rhodolite', 1.760),
        ('Garnet, Spessartite', 1.810),
        ('Gaylussite', 1.517),
        ('Glass', 1.51714),
        ('Glass, Albite', 1.4890),
        ('Glass, Crown', 1.520),
        ('Glass, Crown, Zinc', 1.517),
        ('Glass, Flint, Dense', 1.66),
        ('Glass, Flint, Heaviest', 1.89),
        ('Glass, Flint, Heavy', 1.65548),
        ('Glass, Flint, Lanthanum', 1.80),
        ('Glass, Flint, Light', 1.58038),
        ('Glass, Flint, Medium', 1.62725),
        ('Glycerine', 1.473),
        ('Gold', 0.47),
        ('Hambergite', 1.559),
        ('Hauynite', 1.502),
        ('Helium', 1.000036),
        ('Hematite', 2.940),
        ('Hemimorphite', 1.614),
        ('Hiddenite', 1.655),
        ('Howlite', 1.586),
        ('Hydrogen (gas)', 1.000140),
        ('Hydrogen (liq)', 1.0974),
        ('Hypersthene', 1.670),
        ('Ice', 1.309),
        ('Idocrase', 1.713),
        ('Iodine Crystal', 3.34),
        ('Iolite', 1.548),
        ('Iron', 1.51),
        ('Ivory', 1.540),
        ('Jade, Nephrite', 1.610),
        ('Jadeite', 1.665),
        ('Jasper', 1.540),
        ('Jet', 1.660),
        ('Kornerupine', 1.665),
        ('Kunzite', 1.655),
        ('Kyanite', 1.715),
        ('Lapis Gem', 1.500),
        ('Lapis Lazuli', 1.61),
        ('Lazulite', 1.615),
        ('Lead', 2.01),
        ('Leucite', 1.509),
        ('Magnesite', 1.515),
        ('Malachite', 1.655),
        ('Meerschaum', 1.530),
        ('Mercury (liq)', 1.62),
        ('Methanol', 1.329),
        ('Moldavite', 1.500),
        ('Moonstone, Adularia', 1.525),
        ('Moonstone, Albite', 1.535),
        ('Natrolite', 1.480),
        ('Nephrite', 1.600),
        ('Nitrogen (gas)', 1.000297),
        ('Nitrogen (liq)', 1.2053),
        ('Nylon', 1.53),
        ('Obsidian', 1.489),
        ('Olivine', 1.670),
        ('Onyx', 1.486),
        ('Opal', 1.450),
        ('Oxygen (gas)', 1.000276),
        ('Oxygen (liq)', 1.221),
        ('Painite', 1.787),
        ('Pearl', 1.530),
        ('Periclase', 1.740),
        ('Peridot', 1.654),
        ('Peristerite', 1.525),
        ('Petalite', 1.502),
        ('Phenakite', 1.650),
        ('Phosgenite', 2.117),
        ('Plastic', 1.460),
        ('Plexiglas', 1.50),
        ('Polystyrene', 1.55),
        ('Prase', 1.540),
        ('Prasiolite', 1.540),
        ('Prehnite', 1.610),
        ('Proustite', 2.790),
        ('Purpurite', 1.840),
        ('Pyrite', 1.810),
        ('Pyrope', 1.740),
        ('Quartz', 1.544),
        ('Quartz, Fused', 1.45843),
        ('Rhodizite', 1.690),
        ('Rhodonite', 1.735),
        ('Rock Salt', 1.544),
        ('Rubber, Natural', 1.5191),
        ('Ruby', 1.760),
        ('Rutile', 2.62),
        ('Sanidine', 1.522),
        ('Sapphire', 1.760),
        ('Scapolite', 1.540),
        ('Scapolite, Yellow', 1.555),
        ('Scheelite', 1.920),
        ('Selenium, Amorphous', 2.92),
        ('Serpentine', 1.560),
        ('Shell', 1.530),
        ('Silicon', 4.24),
        ('Sillimanite', 1.658),
        ('Silver', 0.18),
        ('Sinhalite', 1.699),
        ('Smaragdite', 1.608),
        ('Smithsonite', 1.621),
        ('Sodalite', 1.483),
        ('Sodium Chloride', 1.544),
        ('Sphalerite', 2.368),
        ('Sphene', 1.885),
        ('Spinel', 1.712),
        ('Spodumene', 1.650),
        ('Staurolite', 1.739),
        ('Steatite', 1.539),
        ('Steel', 2.50),
        ('Stichtite', 1.520),
        ('Strontium Titanate', 2.410),
        ('Styrofoam', 1.595),
        ('Sulphur', 1.960),
        ('Synthetic Spinel', 1.730),
        ('Taaffeite', 1.720),
        ('Tantalite', 2.240),
        ('Tanzanite', 1.691),
        ('Teflon', 1.35),
        ('Thomsonite', 1.530),
        ('Tiger eye', 1.544),
        ('Topaz', 1.620),
        ('Topaz, Blue', 1.610),
        ('Topaz, Pink', 1.620),
        ('Topaz, White', 1.630),
        ('Topaz, Yellow', 1.620),
        ('Tourmaline', 1.624),
        ('Tremolite', 1.600),
        ('Tugtupite', 1.496),
        ('Turpentine', 1.472),
        ('Turquoise', 1.610),
        ('Ulexite', 1.490),
        ('Uvarovite', 1.870),
        ('Variscite', 1.550),
        ('Vivianite', 1.580),
        ('Wardite', 1.590),
        ('Water (gas)', 1.000261),
        ('Water 100ºC', 1.31819),
        ('Water 20ºC', 1.33335),
        ('Water 35ºC (Room temp)', 1.33157),
        ('Willemite', 1.690),
        ('Witherite', 1.532),
        ('Wulfenite', 2.300),
        ('Zincite', 2.010),
        ('Zircon, High', 1.960),
        ('Zircon, Low', 1.800),
        ('Zirconia, Cubic', 2.170),
        ('Carbonated Beverages', 1.35),
        ('Cranberry Juice (25%)', 1.351),
        ('Honey, 13% water content', 1.504),
        ('Honey, 17% water content', 1.494),
        ('Honey, 21% water content', 1.484),
        ('Milk', 1.35),
        ('Oil, Clove', 1.535),
        ('Oil, Lemon', 1.481),
        ('Oil, Neroli', 1.482),
        ('Oil, Orange', 1.473),
        ('Oil, Safflower', 1.466),
        ('Oil, vegetable (50° C)', 1.47),
        ('Oil of Wintergreen', 1.536),
        ('Rum, White', 1.361),
        ('Shampoo', 1.362),
        ('Sugar Solution 30%', 1.38),
        ('Sugar Solution 80%', 1.49),
        ('Vodka', 1.363),
        ('Water (0° C)', 1.33346),
        ('Whisky', 1.356),
        ('Almandine', 1.76),
        ('Ammolite', 1.52),
        ('Axenite', 1.674),
        ('Beryl, Red', 1.570),
        ('Chrome Tourmaline,', 1.62),
        ('Clinohumite', 1.625),
        ('Crysoberyl, Catseye', 1.746),
        ('Emerald Catseye', 1.560),
        ('Garnet, Mandarin', 1.790),
        ('Garnet, Pyrope', 1.73),
        ('Garnet, Rhodolite', 1.740),
        ('Garnet, Tsavorite', 1.739),
        ('Garnet, Uvarovite', 1.74),
        ('Hauyn', 1.490),
        ('Labradorite', 1.560),
        ('Moonstone', 1.518),
        ('Morganite', 1.585),
        ('Opal, Black', 1.440),
        ('Opal, Fire', 1.430),
        ('Opal, White', 1.440),
        ('Oregon Sunstone', 1.560),
        ('Padparadja', 1.760),
        ('Sapphire, Star', 1.760),
        ('Spessarite', 1.79),
        ('Spinel, Blue', 1.712),
        ('Spinel, Red', 1.708),
        ('Star Ruby', 1.76),
        ('Topaz, Imperial', 1.605),
        ('Tourmaline, Red', 1.64),
        ('Plexiglas', 1.51),
        ('Gallium phosphide', 3.50),
        ('Degreaser', 1.377),
        ('Shower Gel', 1.51),
        ('Baby Wash', 1.26),
        ('Mylar', 1.65),
        ('Nickel', 1.08),
        ('Platinum', 2.33),
        ('Titanium', 2.16),
        ('Eye, Aqueous humor', 1.33),
        ('Eye, Cornea', 1.38),
        ('Eye, Lens', 1.41),
        ('Eye, Vitreous humor', 1.34),
        ('Glass, Arsenic Trisulfide', 2.04),
        ('Glass, Fused Silica', 1.459),
        ('Glass, Pyrex', 1.474),
        ('Lucite', 1.495),
        ('Salt', 1.516)]
    # END List of IOR values

    [add(val) for val in IOR_list]


# -----------------------------------------------------------------------------
# OPERATOR
# -----------------------------------------------------------------------------

class IORREF_OT_AddNode(bpy.types.Operator):
    bl_idname = 'iorref.add_value_node'
    bl_label = 'Add value as node'
    bl_description = 'Add IOR as a value node'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            return context.active_object.active_material.use_nodes
        except (AttributeError, IndexError):
            return False

    def execute(self, context):

        wm = context.window_manager
        item = wm.IORRef[wm.IORRef_index]

        nodes = context.active_object.active_material.node_tree.nodes
        node = nodes.new('ShaderNodeValue')
        node.label = item.name + ' IOR'
        node.outputs[0].default_value = item.value

        return {'FINISHED'}


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------


class IORREF_UIL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(0.75)
            split.label(text=item.name, translate=False)
            split.label(text='{:.3f}'.format(item.value), translate=False)


class IORREF_PT_MainPanel(bpy.types.Panel):
    bl_label = "IOR Reference"
    bl_idname = "IORREF_PT_MainPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        space_node = context.space_data
        return space_node is not None and space_node.node_tree is not None

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        layout.template_list('IORREF_UIL_List', '', wm,
                             'IORRef', wm, 'IORRef_index')

        layout.operator('iorref.add_value_node')


# -----------------------------------------------------------------------------
# Register
# -----------------------------------------------------------------------------

def register():
    bpy.utils.register_class(IORREF_PROP_Value)
    bpy.utils.register_class(IORREF_OT_AddNode)

    wm = bpy.types.WindowManager
    wm.IORRef = CollectionProperty(type=IORREF_PROP_Value)
    wm.IORRef_index = IntProperty(name='IOR Reference Index', default=0)

    if len(bpy.context.window_manager.IORRef) == 0:
        build_IOR_list()

    bpy.utils.register_class(IORREF_UIL_List)
    bpy.utils.register_class(IORREF_PT_MainPanel)


def unregister():
    wm = bpy.types.WindowManager

    del wm.IORRef
    del wm.IORRef_index

    bpy.utils.unregister_class(IORREF_UIL_List)
    bpy.utils.unregister_class(IORREF_PT_MainPanel)
    bpy.utils.unregister_class(IORREF_PROP_Value)
    bpy.utils.unregister_class(IORREF_OT_AddNode)


if __name__ == "__main__":
    register()
