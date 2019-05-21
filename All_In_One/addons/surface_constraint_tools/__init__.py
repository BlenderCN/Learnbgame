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

bl_info = {
    "name" : "Surface Constraint Tools",
    "description" : (
        "A collection of tools for modeling on the surface of another mesh"
    ),
    "location" : "3D View > Tool Shelf > Surface Constraint Tools",
    "author" : "Brett Fedack",
    "version" : (1, 0),
    "blender" : (2, 78, 0),
    "category" : "3D View"
}

if "bpy" not in locals():
    import bpy
    from .operators import MeshBrush
    from .operators import PickSurfaceConstraint
    from .operators import Shrinkwrap
    from .operators import SmoothVertices
    from .operators.internal import ResizeMeshBrush
    from .operators.internal import StrokeMove
    from .operators.internal import StrokeSmooth
    from .preferences import SurfaceConstraintToolsPrefs
    from .ui.panels import SurfaceConstraintToolsPanel
else:
    import imp
    imp.reload(MeshBrush)
    imp.reload(PickSurfaceConstraint)
    imp.reload(Shrinkwrap)
    imp.reload(SmoothVertices)
    imp.reload(ResizeMeshBrush)
    imp.reload(StrokeMove)
    imp.reload(StrokeSmooth)
    imp.reload(SurfaceConstraintToolsPrefs)
    imp.reload(SurfaceConstraintToolsPanel)

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
