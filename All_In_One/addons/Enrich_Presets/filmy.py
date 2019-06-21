import bpy
from . import preset_setup
def filmy():
    preset_setup.preset_setup(preset_name="Filmy Enrich", blend_name="Enrich.blend")
    enrich_props = bpy.context.scene.enrich_props
    enrich_props.cinema_border = True
    enrich_props.cinema_border_height = 0.1
