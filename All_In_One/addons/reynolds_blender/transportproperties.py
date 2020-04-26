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

def generate_laplacianFoam_transport(transport, scene):
    if scene.tp_dt_scalar_elt1 != "":
        transport['DT'][1] = scene.tp_dt_scalar_elt1
    if scene.tp_dt_scalar_elt1 != 0:
        transport['DT'][2] = scene.tp_dt_scalar_elt2

def generate_icoFoam_transport(transport, scene):
    if scene.tp_dt_scalar_elt1 != "":
        transport['nu'][1] = scene.tp_dt_scalar_elt1
    if scene.tp_dt_scalar_elt1 != 0:
        transport['nu'][2] = scene.tp_dt_scalar_elt2

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class TransportPropertiesOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_transportproperties"
    bl_label = "TransportProperties"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        print('Generate transport props for solver: ' + scene.solver_name)
        abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)
        transport = ReynoldsFoamDict('transportProperties.foam',
                                     solver_name=scene.solver_name)
        if scene.solver_name == 'laplacianFoam':
            generate_laplacianFoam_transport(transport, scene)
        elif scene.solver_name == 'icoFoam':
            generate_icoFoam_transport(transport, scene)
        constant_dir = os.path.join(abs_case_dir_path, "constant")
        if not os.path.exists(constant_dir):
            os.makedirs(constant_dir)
        transport_file_path = os.path.join(constant_dir,
                                           "transportProperties")
        with open(transport_file_path, "w+") as f:
            f.write(str(transport))
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
                                           'transportProperties.yaml')
        gui_renderer.render()

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('transportProperties.yaml')

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('transportProperties.yaml')

if __name__ == "__main__":
    register()
