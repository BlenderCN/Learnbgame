#------------------------------------------------------------------------------
# Reynolds-Blender | The Blender add-on for Reynolds, an OpenFoam toolbox.
#------------------------------------------------------------------------------
# Copyright|
#------------------------------------------------------------------------------
#     Deepak Surti       (dmsurti@gmail.com)
#     Prabhu R           (IIT Bombay, prabhu@aero.iitb.ac.in)
#     Shivasubramanian G (IIT Bombay, sgopalak@iitb.ac.in)
#------------------------------------------------------------------------------
# License
#
#     This file is part of reynolds-blender.
#
#     reynolds-blender is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     reynolds-blender is distributed in the hope that it will be useful, but
#     WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#     Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with reynolds-blender.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

# -----------
# bpy imports
# -----------
import bpy, bmesh
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       IntVectorProperty,
                       FloatVectorProperty,
                       CollectionProperty
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       UIList
                       )
from bpy.path import abspath
from mathutils import Matrix, Vector

# --------------
# python imports
# --------------
import operator
import os
import pathlib

# ------------------------
# reynolds blender imports
# ------------------------

from reynolds_blender.gui.register import register_classes, unregister_classes
from reynolds_blender.gui.attrs import set_scene_attrs, del_scene_attrs
from reynolds_blender.gui.custom_operator import create_custom_operators
from reynolds_blender.gui.renderer import ReynoldsGUIRenderer

# ----------------
# reynolds imports
# ----------------
from reynolds.dict.parser import ReynoldsFoamDict
from reynolds.foam.cmd_runner import FoamCmdRunner

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

def generate_laplacianFoam_fvschemes(fvschemes, scene):
    fvschemes['ddtSchemes']['default'] = scene.ddt_schemes_default
    fvschemes['gradSchemes']['default'] = scene.grad_schemes_default
    fvschemes['gradSchemes']['grad(T)'] = scene.grad_schemes_grad_T
    fvschemes['divSchemes']['default'] = scene.div_schemes_default
    fvschemes['laplacianSchemes']['default'] = scene.lap_schemes_default
    fvschemes['laplacianSchemes']['laplacian(DT,T)'] = scene.lap_schemes_dt_t
    fvschemes['interpolationSchemes']['default'] = scene.interp_schemes_default
    fvschemes['snGradSchemes']['default'] = scene.sngrad_schemes_default
    fvschemes['fluxRequired']['default'] = scene.flux_required_default
    fvschemes['fluxRequired']['T'] = scene.flux_required_t

def generate_icoFoam_fvschemes(fvschemes, scene):
    fvschemes['ddtSchemes']['default'] = scene.ddt_schemes_default
    fvschemes['gradSchemes']['default'] = scene.grad_schemes_default
    fvschemes['gradSchemes']['grad(p)'] = scene.grad_schemes_grad_p
    fvschemes['divSchemes']['default'] = scene.div_schemes_default
    fvschemes['divSchemes']['div(phi,U)'] = scene.div_schemes_phi_U
    fvschemes['laplacianSchemes']['default'] = scene.lap_schemes_default
    fvschemes['interpolationSchemes']['default'] = scene.interp_schemes_default
    fvschemes['snGradSchemes']['default'] = scene.sngrad_schemes_default

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class FVSchemesOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_fvschemes"
    bl_label = "FVSchemes"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        print('Generate fvschemes for solver: ' + scene.solver_name)
        abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)
        fvschemes = ReynoldsFoamDict('fvSchemes.foam', solver_name=scene.solver_name)
        if scene.solver_name == 'laplacianFoam':
            generate_laplacianFoam_fvschemes(fvschemes, scene)
        elif scene.solver_name == 'icoFoam':
            generate_icoFoam_fvschemes(fvschemes, scene)
        system_dir = os.path.join(abs_case_dir_path, "system")
        if not os.path.exists(system_dir):
            os.makedirs(system_dir)
        fvschemes_file_path = os.path.join(system_dir, "fvSchemes")
        with open(fvschemes_file_path, "w+") as f:
            f.write(str(fvschemes))
        return {'FINISHED'}

    # Return True to force redraw
    def check(self, context):
        return True

    def invoke(self, context, event):
        scene = context.scene
        return context.window_manager.invoke_props_dialog(self, width=1000)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           scene.solver_name + 'Schemes.yaml')
        gui_renderer.render()

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)

def unregister():
    unregister_classes(__name__)

if __name__ == "__main__":
    register()
