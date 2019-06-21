import bpy
import os
from . import preset_setup
def attic():
    preset_setup.preset_setup(preset_name="Attic Enrich", blend_name="Enrich.blend")
    enrich_props = bpy.context.scene.enrich_props
    vig = bpy.context.scene.node_tree.nodes['Vignette_E']
    vig.node_tree.nodes['Blur'].factor_x = 20
    vig.node_tree.nodes['Blur'].factor_y = 20
    enrich_props.vig_blur=20
    vig.node_tree.nodes['Blur'].inputs[1].default_value = 1.5

    vig.node_tree.nodes['Ellipse Mask'].y = 0.6
    vig.node_tree.nodes['Ellipse Mask'].x = 0.5
    enrich_props.vig_location_y = 0.6
    enrich_props.vig_location_x = 0.5
    vig.node_tree.nodes["Ellipse Mask"].width = 0.973
    vig.node_tree.nodes["Ellipse Mask"].height = 0.506
    vig.node_tree.nodes["Ellipse Mask"].inputs[1].default_value = 1
    vig.inputs[2].default_value = 100
    enrich_props.vig_opacity=100
