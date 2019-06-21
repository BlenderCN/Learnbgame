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
#    scene data models
# ------------------------------------------------------------------------
class BlockCellsPG(bpy.types.PropertyGroup):
    convert_to_meters = bpy.props.FloatProperty(name='FloatProperty',
                                                description='Scaling factor',
                                                default=0.001)
    n_cells = bpy.props.IntVectorProperty(name='Cells',
                                          description='Number of cells',
                                          default=[1, 1, 1])
    n_grading = bpy.props.IntVectorProperty(name='Cell expansion ratios',
                                            description='Cell expansion ratios',
                                            default=[1, 1, 1],
                                            subtype='XYZ')

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class BlockMeshCellsOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_bmd_cells_panel"
    bl_label = "Cell ratios, grading"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    # Return True to force redraw
    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ---------------------------------------
        # Render Block Cells using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'block_cells.yaml')
        gui_renderer.render()


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('block_cells.yaml')

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('block_cells.yaml')

if __name__ == "__main__":
    register()
