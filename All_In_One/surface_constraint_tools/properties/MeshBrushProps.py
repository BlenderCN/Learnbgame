# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

import bpy
from ..auxiliary_classes.Brushes import Brushes
from ..auxiliary_classes.FalloffCurve import FalloffCurve
from ..auxiliary_classes.Octree import Octree
from ..auxiliary_classes.RainbowRamp import RainbowRamp
from ..auxiliary_classes.VertexProperties import VertexProperties
from ..auxiliary_classes.View3DGraphic import View3DGraphic

class MeshBrushProps(bpy.types.PropertyGroup):
    data_path =(
        "user_preferences.addons['{0}'].preferences.mesh_brush"
    ).format(__package__.split(".")[0])

    # Brush Settings
    iterations = bpy.props.IntProperty(
        name = "Iterations",
        description = "Number of smoothing iterations",
        default = 1,
        min = 1,
        soft_max = 25
    ) 
    position_x = bpy.props.IntProperty() 
    position_y = bpy.props.IntProperty() 
    radius = bpy.props.IntProperty(
        name = "Radius",
        description = "Radius, in pixels, of the mesh brush",
        default = 75,
        min = 1,
        soft_max = 250
    ) 
    spacing = bpy.props.IntProperty(
        name = "Spacing",
        description =\
            "Distance between dabs as a percentage of the brush's radius",
        default = 25,
        min = 1,
        soft_max = 100,
        subtype = 'PERCENTAGE'
    )

    # Display Properties
    brush_is_visible = bpy.props.BoolProperty(
        name = "Show Brush",
        description = "Show/hide the brush.",
        default = True
    )
    brush_influence_is_visible = bpy.props.BoolProperty(
        name = "Show Influence",
        description = "Show/hide the brush's influence.",
        default = False
    )
    interior_color = bpy.props.FloatVectorProperty(
        name = "Interior Color",
        description = "Color of the brush's interior",
        default = (1.0, 0.522, 0, 0.1),
        min = 0,
        max = 1,
        subtype = 'COLOR',
        size = 4
    )
    outline_color = bpy.props.FloatVectorProperty(
        name = "Outline Color",
        description = "Color of the brush's outline",
        default = (1.0, 0.522, 0, 1.0),
        min = 0,
        max = 1,
        subtype = 'COLOR',
        size = 4
    )
    outline_thickness = bpy.props.IntProperty(
        name = "Outline Thickness",
        description = "Thickness of the brush's outline",
        default = 1,
        min = 1,
        soft_max = 10
    )

    # Falloff
    falloff_profile = bpy.props.EnumProperty(
        name = "Falloff Curve",
        description = "The intensity profile of the brush",
        default = 'SMOOTH',
        items = [
            ('SMOOTH', "Profile", "Smooth", 'SMOOTHCURVE', 0),
            ('ROUND', "Profile", "Round", 'SPHERECURVE', 1),
            ('ROOT', "Profile", "Root", 'ROOTCURVE', 2),
            ('SHARP', "Profile", "Sharp", 'SHARPCURVE', 3),
            ('LINEAR', "Profile", "Linear", 'LINCURVE', 4),
            ('CONSTANT', "Profile", "Constant", 'NOCURVE', 5),
            ('RANDOM', "Profile", "Random", 'RNDCURVE', 6)
        ]
    )

    # Options
    backfacing_are_ignored = bpy.props.BoolProperty(
        name = "Ignore Backfacing",
        description =\
            "Ignore vertices with normals pointing away from the brush.",
        default = False
    )
    boundary_is_locked = bpy.props.BoolProperty(
        name = "Lock Boundary",
        description = "Lock vertices that are on the boundary of the mesh.",
        default = False
    )
    selection_is_isolated = bpy.props.BoolProperty(
        name = "Isolate Selection",
        description = (
            "Isolate the selected faces from the rest of the mesh object, " +
            "and lock the selection border."
        ),
        default = False
    )

    # Symmetry
    radial_count = bpy.props.IntProperty(
        name = "Radial Count",
        description =\
            "Number of radially symmetrical brushes per axis of symmetry",
        default = 1,
        min = 1,
        soft_max = 12
    )
    symmetry_type = bpy.props.EnumProperty(
        name = "Symmetry Type",
        description =\
            "The type of symmetry to employ in modifying the mesh object",
        default = 'MIRROR',
        items = [
            ('MIRROR', "Mirror", "Mirror across planes of symmetry."),
            ('RADIAL', "Radial", "Rotate around axes of symmetry.")
        ]
    )
    x_axis_symmetry_is_enabled = bpy.props.BoolProperty(
        name = "X Symmetry",
        description =(
            "Enable/disable symmetrical modification of the mesh object " +
            "using the x-axis of its local space axes."
        ),
        default = False
    )
    y_axis_symmetry_is_enabled = bpy.props.BoolProperty(
        name = "Y Symmetry",
        description =(
            "Enable/disable symmetrical modification of the mesh object " +
            "using the y-axis of its local space axes."
        ),
        default = False
    )
    z_axis_symmetry_is_enabled = bpy.props.BoolProperty(
        name = "Z Symmetry",
        description =(
            "Enable/disable symmetrical modification of the mesh object " +
            "using the z-axis of its local space axes."
        ),
        default = False
    )

    # UI Visibility
    display_props_ui_is_visible = bpy.props.BoolProperty(
        name = "Display Properties UI Visibility",
        description = "Show/hide the Display Properties UI.",
        default = False
    )
    falloff_ui_is_visible = bpy.props.BoolProperty(
        name = "Curve UI Visibility",
        description = "Show/hide the Curve UI.",
        default = False
    )
    options_ui_is_visible = bpy.props.BoolProperty(
        name = "Options UI Visibility",
        description = "Show/hide the Options UI.",
        default = False
    )
    settings_ui_is_visible = bpy.props.BoolProperty(
        name = "Settings UI Visibility",
        description = "Show/hide the Settings UI.",
        default = False
    )
    symmetry_ui_is_visible = bpy.props.BoolProperty(
        name = "Symmetry UI Visibility",
        description = "Show/hide the Symmetry UI.",
        default = False
    )

    # Persistent Objects
    brushes = Brushes()
    color_ramp = RainbowRamp()
    falloff_curve = FalloffCurve()
    brush_graphic = View3DGraphic()
    brush_influence_graphic = View3DGraphic()
    brush_strength_graphic = View3DGraphic()
    octree = Octree(max_indices_per_leaf = 50)
    redo_stack = list()
    undo_stack = list()