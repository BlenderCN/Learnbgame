# This file is part of Hypermesh.
#
# Hypermesh is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hypermesh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hypermesh.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from .updatehyperpositions import clean_mesh
from .hyperpreset import project_to_3d
from .hypermeshpreferences import debug_message


def find_dirty_meshes_with_given_hypersettings(h):
    meshes = []
    for me in bpy.data.meshes:
        if not me.hypersettings.hyper:
            continue
        if not me.hypersettings == h:
            continue
        try:
            if me["hypermesh-dirty"]:
                dirty = True
            else:
                dirty = False
        except KeyError:
            dirty = False
        if dirty:
            meshes.append(me)
    return meshes


def get_preset(self):
    try:
        return self["preset"]
    except KeyError:
        self["preset"] = 0
        return self["preset"]


def set_preset(self, value):
    debug_message("Set preset of a HyperSettings")
    dirties = find_dirty_meshes_with_given_hypersettings(self)
    for me in dirties:
        clean_mesh(me)
    self["preset"] = value
    for me in bpy.data.meshes:
        if not me.hypersettings.hyper:
            continue
        if not me.hypersettings == self:
            continue
        # I suspect this search will match at most once
        me["hypermesh-dirty"] = False
        me["hypermesh-justcleaned"] = True
        project_to_3d(me)  # this will trigger handle_scene_changed


class HyperSettings(bpy.types.PropertyGroup):
    hyper = bpy.props.BoolProperty(
        name="Hyper",
        description="Is this object a hyperobject?",
        default=False)
    preset = bpy.props.IntProperty(
        name="Projection preset",
        description="Which projection from 4-space to 3-space to use",
        min=0,
        max=3,
        get=get_preset,
        set=set_preset)

    def set_preset_without_reprojecting(self, value):
        debug_message("Set preset without reprojecting")
        self["preset"] = value
