import bpy
import os
from . import preset_setup
def lomo():
    preset_setup.preset_setup(preset_name="Lomo Enrich", blend_name="Enrich.blend")
    enrich_props = bpy.context.scene.enrich_props
    vig = bpy.context.scene.node_tree.nodes['Vignette_E']
    vig.inputs[2].default_value = 80
    enrich_props.vig_opacity=80

    vig_blur = vig.node_tree.nodes["Blur"]
    vig_blur.factor_x = 20
    vig_blur.factor_y = 20
    vig_blur.inputs[1].default_value = 0.9

    vig_mask = vig.node_tree.nodes["Ellipse Mask"]
    vig_mask.y = 0.5
    vig_mask.x = 0.5
    enrich_props.vig_location_y = 0.5
    enrich_props.vig_location_x = 0.5
    vig_mask.width = 0.866
    vig_mask.height = 0.465
    vig_mask.inputs[1].default_value = 1.0
