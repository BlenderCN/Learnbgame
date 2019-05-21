import bpy

from bpy.props import IntProperty, CollectionProperty , StringProperty , BoolProperty, EnumProperty, FloatVectorProperty

from .files_functions import UpdatePaletteFiles, RenamePaletteFiles, UpdateColorName
from .node_functions import PaletteListCallback, PaletteNodeUpdate

class ColorCollection(bpy.types.PropertyGroup):
    name = StringProperty(name='Color Name', default='Color_', update=UpdateColorName)
    temp_name = StringProperty(name='Color Name', default='Color_')
    color_value = FloatVectorProperty(name='Color', step=1, subtype='COLOR_GAMMA', default=(1.0,1.0,1.0), min=0, max=1, update=UpdatePaletteFiles)
    
class PaletteCollection(bpy.types.PropertyGroup):
    name = StringProperty(name='Color Name', default='___temp___', update=RenamePaletteFiles)
    temp_name = StringProperty(name='Palette Name', default='Palette_')
    colors = CollectionProperty(type=ColorCollection)
    hide = BoolProperty(name='Hide', default=False, description='Hide this Palette')
    filepath = StringProperty(name="Palette Filepath", subtype="FILE_PATH")

class PaletteProps(bpy.types.PropertyGroup):
    palettes = CollectionProperty(type=PaletteCollection)
    index = IntProperty(name='Active Palette index', default=0, min=0)
    manage_palette = BoolProperty(name='Manage Palette', description='Manage Active Palette', default=False)
    display_color_names = BoolProperty(name='Display Names', description='Display Color Names', default=False)
    color_per_row = IntProperty(name='Color per row', default=5, min=1, max=24)
    manage_menu = BoolProperty(name='Manage Menu', description='Manage Menu', default=False)
    pantone_base_color = FloatVectorProperty(name='Pantone Base Color', subtype='COLOR_GAMMA', default=(0.007,0.305,0.332), min=0, max=1)
    pantone_type = EnumProperty(items=(('SIMILAR', 'Similar', 'Similar'),
                                ('MONOCHROMATIC', 'Monochromatic', 'Monochromatic'),
                                ('SHADING', 'Shading', 'Shading'),
                                ('TRIAD', 'Triad', 'Triad'),
                                ('COMPLEMENTARY', 'Complementary', 'Complementary'),
                                ), default='SIMILAR', name='Pantone Type')
    pantone_name = StringProperty(name='Pantone Name', default='Pantone')
    pantone_offset = IntProperty(name='Pantone Offset', default=5, min=1, max=25)
    pantone_precision = IntProperty(name='Pantone Precision', default=2, min=0, max=10)
    palette_list = bpy.props.EnumProperty(name='Palette List', items=PaletteListCallback, update=PaletteNodeUpdate)
    node_palette_manager_hide = BoolProperty(name='Hide Palette Manager', default=True, description='Hide Palette Manager')