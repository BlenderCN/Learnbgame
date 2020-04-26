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
import bpy
from bpy.types import (Panel,
                       PropertyGroup)
from bpy.props import StringProperty, BoolProperty


from progress_report import ProgressReport

# ------------------------
# reynolds blender imports
# ------------------------

from reynolds_blender.gui.attrs import set_scene_attrs
from reynolds_blender.gui.register import register_classes, unregister_classes
from reynolds_blender.gui.renderer import ReynoldsGUIRenderer
from reynolds_blender.fvschemes import FVSchemesOperator
from reynolds_blender.fvsolution import FVSolutionOperator
from reynolds_blender.controldict import ControlDictOperator
from reynolds_blender.transportproperties import TransportPropertiesOperator

# ---------------
# reynolds imports
# ----------------
from reynolds.foam.start import FoamRunner
from reynolds_blender.gui.custom_operator import create_custom_operators

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

def start_openfoam(self, context):
    scene = context.scene
    obj = context.active_object

    scene.foam_started = False

    # -------------------------
    # Start the console operatorr
    # --------------------------
    bpy.ops.reynolds.of_console_op()

    print("Start openfoam")

    fr = FoamRunner()

    if fr.start():
        scene.foam_started = True
        self.report({'INFO'}, 'OpenFoam started: SUCCESS')
    else:
        scene.foam_started = False
        self.report({'INFO'}, 'OpenFoam started: FAILED')

    return{'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class FoamPanel(Panel):
    bl_idname = "of_foam_panel"
    bl_label = "Open Foam"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # -------------------------------------
        # Render Foam Panel using YAML GUI Spec
        # -------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout, 'foam_panel.yaml')
        gui_renderer.render()

        row = layout.row()
        row.operator(FVSchemesOperator.bl_idname, text='', icon='SETTINGS')
        row.operator(FVSolutionOperator.bl_idname, text='', icon='SETTINGS')
        row.operator(ControlDictOperator.bl_idname, text='', icon='SETTINGS')
        row.operator(TransportPropertiesOperator.bl_idname, text='', icon='SETTINGS')


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    set_scene_attrs('foam_panel.yaml')
    create_custom_operators('foam_panel.yaml', __name__)
    register_classes(__name__)

def unregister():
    unregister_classes(__name__)

if __name__ == '__main__':
    register()
