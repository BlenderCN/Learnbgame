'''
Copyright (C) 2017 JOSECONSCO
Created by JOSECONSCO
Thanks to Jaroslaw Cwik for Ideas on aligning curves tilt

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
#DONE: add converting curves (eg from zbrush) to blender Particle Hair
#DONE: randomize spacing by randomizing   t_ins? +- rand dt (same dt over length (in resample 2d)
#DONE: why flipps happnes?? cos bitangetn is 180deg from VectSurfHit. Not a bug (almost like gimaball lock)
#DONE: Resample output point count  proprotional to len of strand
#DONE: Add flip uv to options
#BUG_IN_BLENDER: GP to PartHair still sometimes is broken (depending on viewing angle)... - cos blender messes up attached hair keys,
#                Comb fix dosent always work
#DONE: GenerateVerColorRandom per strand
#CANNOTDO: ribbon profile curve if possible  - Wont work in f6 mode
#DONE: Edit Curve profile option - more complex profile like " /\/\/\ " <- 3 peaks per one curve
#DONE: option to edit uv boxes (delete, resize)
#DONE: fix align curve random flipping
#DONE: fix last material setup
#TODO: add custom clumping maybe? FIX adjust it
#WIP: add vert color, random, gradinet, flow map? Partialy done in Vertex Color Master
#TODO: fix undo in modal uv draw?
#DONE: fix double update when modal hair update generates to muuch undo history
#DONE: why aligning wont work?
#DONE add spline drawwign offset...
#DONE: fix t_in_s in modal particle hair crash
#DONE: Add reset tilt in modal particle hair
#WIP: Particle hair combing to ribbons
#DONE: Added/improved embed operator
#DONE: Fixed Wrong aligning when in edit mode
#DONE: added multi curve attach as particle hair.
#DONE: texturing implementation
#DONE: Diffuse bake
#DONE: fix id baking for curves
#DONE: Add render size for settins
#DONE: Hair baking - make preview settings same as render settings - eg. particle count, spline res etc.
#DONE: add ability to change suffixes for baked textures?
#DONE: add tilt support for child particles
#DONE: Apply curve rotation when aligning titl to prevetn weird rotaton problems
#DONE: add similar to Division strands painitng.. https://www.youtube.com/watch?time_continue=16&v=phanI1WkWgU
#DONE: Include Parents in iinteractive hair with children.
#CANT_REPRODUCE: combing getting slover over time... interactive..
#DONE: randomize curve tilt -> add positive and negative dir.
#DONE: align curve tilt only on sel -> works on whole sel crve now. Make it only on real selection
#DONE: Create Hairs Following Within Geometry Volume ( Like Hair Farm ) - build in blender it seems - Shape Cut
#DONE: add 'use default material' option
#DONE: clumping
#DONE: fix jumping particle whne converting curves to particle hair
#DONE: Allow Rendering 8k Cards
#CANT: change align tilt to Paralel transport - actually slower than current fake method
#DONE: fix goint in and out of mesh -> curve mode - broken uv - caused by braids code - reverted it
#TODO: polygrouping  p hair, curve hair?
#TODO: bake : flatten scalp ? Seams?
#TODO: add editing curve ribbons in obj mode -> to draw hidden splines by bias?
#TODO: curves lost profile curv (maybe just pasting into new blend loses fake user...)
#TODO: Make website like eg. https://squircleart.github.io ? or hard ops manual?
#TODO: Automatic Separate Uvs into Specified Number of Cards even Divisions, Create same uv Divisions


bl_info = {
    "name": "Hair Tool",
    "description": "Make hair planes from curves",
    "author": "Bartosz Styperek",
    "blender": (2, 80, 0),
    "location": "View 3D > Tools > Hair Tool",
    "version": (2, 0, 5),
    "warning": "",
    "wiki_url": "https://joseconseco.github.io/HairToolDocs/",
    "tracker_url": "https://discord.gg/cxZDbqH",
    "category": "Object"
}

# load and reload submodules
##################################
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python37\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb

# load and reload submodules
##################################

if "bpy" in locals():
    import importlib

    importlib.reload(hair_tool_ui)
    importlib.reload(helper_functions)
    importlib.reload(braid_maker)
    importlib.reload(surface_to_splines)
    importlib.reload(ribbons_operations)
    importlib.reload(resample2d)
    importlib.reload(hair_curve_helpers)
    importlib.reload(hair_mesh_helpers)
    importlib.reload(curve_simplify)
    importlib.reload(particle_hair)
    importlib.reload(modal_uv_draw_boxes)
    importlib.reload(modal_particle_hair)
    importlib.reload(curves_resample)
    importlib.reload(gpencil_to_curve)
    importlib.reload(hair_tool_props)
    importlib.reload(hair_bake)
    importlib.reload(hair_bake_ui)
    importlib.reload(hair_bake_nodes)
    importlib.reload(ht_image_operators)
else:

    from . import hair_tool_ui
    from . import helper_functions
    from . import braid_maker
    from . import surface_to_splines
    from . import ribbons_operations
    from . import resample2d
    from . import hair_curve_helpers
    from . import hair_mesh_helpers
    from . import curve_simplify
    from . import particle_hair
    from . import modal_uv_draw_boxes
    from . import modal_particle_hair
    from . import curves_resample
    from . import gpencil_to_curve
    from hair_tool.hair_baking import hair_bake, hair_bake_ui, hair_bake_nodes, ht_image_operators
    from . import hair_tool_props


# register
##################################

import bpy
from bpy.app.handlers import persistent
from . import auto_load
from .gpencil_to_curve import change_draw_keymap
auto_load.init()


def draw_item(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("curve.select_next", text="Select Next").previous = False
    layout.operator("curve.select_next", text="Select Previous").previous = True
    layout.separator()
    layout.operator("curve.select_tips", text="Select Roots").roots = True
    layout.operator("curve.select_tips", text="Select Tips").roots = False


@persistent
def post_load(scene):
    #Scene is None, when addosn is initiailzed. And Keymap'Grease Pencilt' it none too. Lines below work only on new blend load. :<
    use_custom_hair_drawing = bpy.context.scene.modal_gp_curves.runModalHair
    change_draw_keymap(use_custom_hair_drawing)

def register():
    auto_load.register()
    print("Registered Hair Tool")

    hair_tool_props.register_properties()
    hair_bake_nodes.registerNode()

    # lets add ourselves to the main header
    bpy.types.VIEW3D_MT_select_edit_curve.append(draw_item)
    hair_tool_ui.register_keymap()
    
    bpy.app.handlers.load_post.append(post_load)


def unregister():
    bpy.app.handlers.load_post.remove(post_load)

    hair_bake_nodes.unregisterNode()
    hair_tool_ui.unregister_keymap()
    hair_tool_props.unregister_properties()

    auto_load.unregister()
    print("Unregistered Hair Tool.")

    bpy.types.VIEW3D_MT_select_edit_curve.remove(draw_item)

if __name__ == "__main__":
    register()  
