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

def generate_laplacianFoam_fvsolution(fvsolution, scene):
    fvsolution['solvers']['T']['solver'] = scene.solvers_T_solver
    fvsolution['solvers']['T']['preconditioner'] = scene.solvers_T_preconditioner
    fvsolution['solvers']['T']['tolerance'] = scene.solvers_T_tolerance
    fvsolution['solvers']['T']['relTol'] = scene.solvers_T_relTol
    fvsolution['SIMPLE']['nNonOrthogonalCorrectors'] = scene.simple_nNonOrthogonalCorrectors

def generate_icoFoam_fvsolution(fvsolution, scene):
    fvsolution['solvers']['p']['solver'] = scene.solvers_p_solver
    fvsolution['solvers']['p']['preconditioner'] = scene.solvers_p_preconditioner
    fvsolution['solvers']['p']['tolerance'] = scene.solvers_p_tolerance
    fvsolution['solvers']['p']['relTol'] = scene.solvers_p_relTol
    fvsolution['solvers']['pFinal']['$p'] = scene.solvers_pfinal_p
    fvsolution['solvers']['pFinal']['relTol'] = scene.solvers_pfinal_relTol
    fvsolution['solvers']['U']['solver'] = scene.solvers_U_solver
    fvsolution['solvers']['U']['smoother'] = scene.solvers_U_smoother
    fvsolution['solvers']['U']['tolerance'] = scene.solvers_U_tolerance
    fvsolution['solvers']['U']['relTol'] = scene.solvers_U_relTol
    fvsolution['PISO']['nNonOrthogonalCorrectors'] = scene.piso_nCorrectors
    fvsolution['PISO']['nNonOrthogonalCorrectors'] = scene.piso_nNonOrthogonalCorrectors
    fvsolution['PISO']['pRefCell'] = scene.piso_pRefCell
    fvsolution['PISO']['pRefValue'] = scene.piso_pRefValue

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class FVSolutionOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_fvsolutionop"
    bl_label = "FVSolution"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        print('Generate fvsolution for solver: ' + scene.solver_name)
        abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)
        fvsolution = ReynoldsFoamDict('fvSolution.foam', solver_name=scene.solver_name)
        if scene.solver_name == 'laplacianFoam':
            generate_laplacianFoam_fvsolution(fvsolution, scene)
        elif scene.solver_name == 'icoFoam':
            generate_icoFoam_fvsolution(fvsolution, scene)
        system_dir = os.path.join(abs_case_dir_path, "system")
        if not os.path.exists(system_dir):
            os.makedirs(system_dir)
        fvsolution_file_path = os.path.join(system_dir, "fvSolution")
        with open(fvsolution_file_path, "w+") as f:
            f.write(str(fvsolution))
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
                                           scene.solver_name + 'Solution.yaml')
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
