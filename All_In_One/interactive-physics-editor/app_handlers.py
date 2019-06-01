# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Blender imports
import bpy
from bpy.types import Panel, Operator, Scene
from bpy.app.handlers import persistent
from mathutils import Matrix, Vector

# Addon imports
from .functions.common import *

# global vars
collection_name = "interactive_edit_session"

@persistent
def handle_edit_session_pre(scene):
    if type(scene) != Scene or scene.name != "Interactive Physics Session":
        return
    if scene.frame_current != scene.frame_end:
        return
    c = bpy_collections().get(collection_name)
    if c is None:
        return
    for obj in c.objects:
        obj["d3tool_last_matrix"] = obj.matrix_world.copy()

@persistent
def handle_edit_session_post(scene):
    if type(scene) != Scene or scene.name != "Interactive Physics Session":
        return
    if scene.frame_current != scene.frame_start:
        return
    c = bpy_collections().get(collection_name)
    if c is None:
        return
    for obj in c.objects:
        try:
            obj.matrix_world = Matrix(obj["d3tool_last_matrix"])
        except KeyError:
            pass
