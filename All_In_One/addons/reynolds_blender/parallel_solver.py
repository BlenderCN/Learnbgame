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
#    Operator Panel
# ------------------------------------------------------------------------

class ParallelSolverOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_dpd_panel"
    bl_label = "DecomposeParDict"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return True

    # Return True to force redraw
    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=750)

    def execute(self, context):
        scene = context.scene
        # -------------------------
        # Start the console operatorr
        # --------------------------
        bpy.ops.reynolds.of_console_op()

        print('Generate decomposeParDict parallel config: ')

        decompose_par_dict = ReynoldsFoamDict('decomposeParDict.foam')

        # mandatory
        decompose_par_dict['numberOfSubdomains'] = scene.number_of_subdomains
        decompose_par_dict['method'] = scene.decompose_method

        # simpleCoeffs
        simple_nxyz = (str(scene.nSimpleCoeffsX),
                       str(scene.nSimpleCoeffsY),
                       str(scene.nSimpleCoeffsZ))
        decompose_par_dict['simpleCoeffs']['n'] = '(' + ' '.join(simple_nxyz) + ')'
        decompose_par_dict['simpleCoeffs']['delta'] = scene.simpleCoeffDelta

        # hierarchicalCoeffs
        hierarchical_nxyz = (str(scene.nHierarchicalCoeffsX),
                             str(scene.nHierarchicalCoeffsY),
                             str(scene.nHierarchicalCoeffsZ))
        decompose_par_dict['hierarchicalCoeffs']['n'] =  '(' + ' '.join(hierarchical_nxyz) + ')'
        decompose_par_dict['hierarchicalCoeffs']['delta'] = scene.hierarchicalCoeffDelta
        decompose_par_dict['hierarchicalCoeffs']['order'] = scene.order_of_decomposition

        # metisCoeffs
        decompose_par_dict['metisCoeffs']['processorWeights'] = scene.metisCoeffs_processor_weights
        decompose_par_dict['metisCoeffs']['strategy'] = scene.metisCoeffs_strategy

        # manualCoeffs
        if scene.manual_datafile_path:
            data_file_path = bpy.path.abspath(scene.manual_datafile_path)
            decompose_par_dict['manualCoeffs']['datafile'] = """ '"{}"' """.format(data_file_path)


        print("DECOMPOSE PAR DICT")
        print(decompose_par_dict)

        abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)
        system_dir = os.path.join(abs_case_dir_path, "system")
        if not os.path.exists(system_dir):
            os.makedirs(system_dir)

        dpd_file_path = os.path.join(system_dir, "decomposeParDict")
        with open(dpd_file_path, "w") as f:
            f.write(str(decompose_par_dict))


        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ---------------------------------------
        # Render Block Panel using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'parallel_solver.yaml')
        gui_renderer.render()

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('parallel_solver.yaml')

def unregister():
    del_scene_attrs('parallel_solver.yaml')
    unregister_classes(__name__)

if __name__ == "__main__":
    register()
