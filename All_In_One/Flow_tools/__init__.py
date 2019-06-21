'''
Copyright (C) Jean Da Costa Machado
jean3dimesional@gmail.com

Created by Jean Da Costa Machado

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

bl_info = {
    "name": "Flow Tools 2",
    "description": "Sculpting and retopology utils",
    "author": "Jean Da Costa Machado",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Learnbgame",
}


import bpy


# load and reload submodules
##################################

modules = [
    "booleans",
    "remesh_optimized",
    "enveloper",
    "ui_panels",
    "lightloader",
    "decimate"
]

import importlib

for module in modules:
    if module in locals():
        importlib.reload(locals()[module])
    else:
        exec("from . import %s" % module)
import bpy


# menus
#################################

def add_envelope_armature(self, context):
    self.layout.operator("f_tools_2.add_envelope_armature",
                         text="Envelope Bone", icon="BONE_DATA")

# register
##################################


import traceback


def register():
    try:
        bpy.utils.register_module(__name__)

        bpy.types.INFO_MT_armature_add.prepend(add_envelope_armature)

        bpy.types.Scene.slash_cut_thickness = bpy.props.FloatProperty(
            name="Cut Thickness",
            description="The spacing of the cut though the mesh",
            default=0.001,
            min=0.000001
        )

        bpy.types.Scene.slash_cut_distance = bpy.props.FloatProperty(
            name="Cut Distance",
            description="The distance the cut spams over the stroke location",
            default=50,
            min=0.000001
        )

        bpy.types.Scene.slash_boolean_solver = bpy.props.EnumProperty(
            name="Boolean Solver",
            description="Which method to use, Carve fails less often but is slower",
            items=[("BMESH", "Bmesh", "Bmesh"), ("CARVE", "Carve", "Carve")],
            default="CARVE"
        )

        bpy.types.Scene.lightloader_preset = bpy.props.EnumProperty(
            name="Preset",
            description="Which solid lighting preset to choose from",
            items=lightloader.list_presets_callback,
            update=lambda self, context: lightloader.load_unpack(
                context.scene.lightloader_preset)
        )
        
        bpy.types.Scene.decimate_factor = bpy.props.FloatProperty(
            name="Ratio",
            description="How much to recuce",
            default=0.7,
            min = 0.0000001,
            max = 1.0
        )

    except:
        traceback.print_exc()


def unregister():
    try:
        bpy.utils.unregister_module(__name__)
        del bpy.types.Scene.slash_cut_thickness
        del bpy.types.Scene.slash_cut_distance
        del bpy.types.Scene.slash_boolean_solver
        del bpy.types.Scene.lightloader_preset
        del bpy.types.Scene.decimate_factor

        bpy.types.INFO_MT_add.remove(add_envelope_armature)
    except:
        traceback.print_exc()
