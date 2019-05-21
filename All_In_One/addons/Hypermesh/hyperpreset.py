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
import bmesh
from .updatehyperpositions import clean_mesh
from .projections import map4to3
from mathutils import Vector
from .hypermeshpreferences import debug_message


def project_to_3d(me):
    debug_message("Projecting " + me.name + " to 3D")

    h = bpy.context.scene.hyperpresets[me.hypersettings.preset]
    if me.is_editmode:
        bm = bmesh.from_edit_mesh(me)
    else:
        bm = bmesh.new()
        bm.from_mesh(me)
    layw = bm.verts.layers.float['hyperw']
    layx = bm.verts.layers.float['hyperx']
    layy = bm.verts.layers.float['hypery']
    layz = bm.verts.layers.float['hyperz']
    for v in bm.verts:
        p = Vector([v[layw], v[layx], v[layy], v[layz]])
        newco = map4to3(h, p)
        v.co = newco
    if me.is_editmode:
        bmesh.update_edit_mesh(me)
    else:
        bm.to_mesh(me)
    me.update()


def find_dirty_meshes_with_given_hyperpreset(pr):
    meshes = []
    for me in bpy.data.meshes:
        if not me.hypersettings.hyper:
            continue
        if not bpy.context.scene.hyperpresets[me.hypersettings.preset] == pr:
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


def get_preset_property(self, prop, default):
    try:
        return self[prop]
    except KeyError:
        self[prop] = default
        return self[prop]


def set_preset_property(self, prop, value):
    debug_message("Set preset property")
    dirties = find_dirty_meshes_with_given_hyperpreset(self)
    for me in dirties:
        clean_mesh(me)
    self[prop] = value
    for me in bpy.data.meshes:
        if not me.hypersettings.hyper:
            continue
        if not bpy.context.scene.hyperpresets[me.hypersettings.preset] == self:
            continue
        me["hypermesh-dirty"] = False
        me["hypermesh-justcleaned"] = True
        project_to_3d(me)  # this will trigger handle_scene_changed


class HyperPreset(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
        name="Name",
        description="Name of the projection",
        default="AwesomeProjection")
    perspective = bpy.props.BoolProperty(
        name="Perspective",
        description="Use perspective when mapping to 3-space",
        get=(lambda x: get_preset_property(x, "perspective", False)),
        set=(lambda x, y: set_preset_property(x, "perspective", y)))
    viewcenter = bpy.props.FloatVectorProperty(
        name="View center",
        size=4,
        description="The point in 4-space at the origin of the image plane",
        get=(lambda x: get_preset_property(x, "viewcenter", (0.0, 0.0, 0.0, 0.0))),
        set=(lambda x, y: set_preset_property(x, "viewcenter", y)),
        subtype='QUATERNION')
    cameraoffset = bpy.props.FloatVectorProperty(
        name="Camera offset",
        size=4,
        description="Vector from the view center to the camera position",
        get=(lambda x: get_preset_property(x, "cameraoffset", (-4.0, 0.0, 0.0, 0.0))),
        set=(lambda x, y: set_preset_property(x, "cameraoffset", y)),
        subtype='QUATERNION')
    xvec = bpy.props.FloatVectorProperty(
        name="X vector",
        size=4,
        description="Vector in image plane such that (view center + X vector) "
                    "is mapped to (1,0,0)",
        get=(lambda x: get_preset_property(x, "xvec", (0.0, 1.0, 0.0, 0.0))),
        set=(lambda x, y: set_preset_property(x, "xvec", y)),
        subtype='QUATERNION')
    yvec = bpy.props.FloatVectorProperty(
        name="Y vector",
        size=4,
        description="Vector in image plane such that (view center + Y vector) "
                    "is mapped to (0,1,0)",
        get=(lambda x: get_preset_property(x, "yvec", (0.0, 0.0, 1.0, 0.0))),
        set=(lambda x, y: set_preset_property(x, "yvec", y)),
        subtype='QUATERNION')
    zvec = bpy.props.FloatVectorProperty(
        name="Z vector",
        size=4,
        description="Vector in image plane such that (view center + Z vector) "
                    "is mapped to (0,0,1)",
        get=(lambda x: get_preset_property(x, "zvec", (0.0, 0.0, 0.0, 1.0))),
        set=(lambda x, y: set_preset_property(x, "zvec", y)),
        subtype='QUATERNION')


# set a hyperpreset to a builtin preset
# what is meant by builtin? Well, anything that's given by this function...
def set_to_builtin_preset(hyperpreset, builtin='noW'):
    hyperpreset.perspective = False
    hyperpreset.viewcenter = (0.0, 0.0, 0.0, 0.0)
    w = (1.0, 0.0, 0.0, 0.0)
    x = (0.0, 1.0, 0.0, 0.0)
    y = (0.0, 0.0, 1.0, 0.0)
    z = (0.0, 0.0, 0.0, 1.0)
    if builtin == 'noX':
        hyperpreset.xvec = w
        hyperpreset.yvec = y
        hyperpreset.zvec = z
        hyperpreset.cameraoffset = tuple([5 * t for t in x])
        hyperpreset.name = "No X"
    elif builtin == 'noY':
        hyperpreset.xvec = w
        hyperpreset.yvec = x
        hyperpreset.zvec = z
        hyperpreset.cameraoffset = tuple([5 * t for t in y])
        hyperpreset.name = "No Y"
    elif builtin == 'noZ':
        hyperpreset.xvec = w
        hyperpreset.yvec = x
        hyperpreset.zvec = y
        hyperpreset.cameraoffset = tuple([5 * t for t in z])
        hyperpreset.name = "No Z"
    else:
        hyperpreset.xvec = x
        hyperpreset.yvec = y
        hyperpreset.zvec = z
        hyperpreset.cameraoffset = tuple([5 * t for t in w])
        hyperpreset.name = "No W"


def ensure_scene_is_hyper(scene):
    hps = scene.hyperpresets
    if len(hps) > 0:
        return
    hps.add()
    hps.add()
    hps.add()
    hps.add()
    set_to_builtin_preset(hps[0], 'noW')
    set_to_builtin_preset(hps[1], 'noX')
    set_to_builtin_preset(hps[2], 'noY')
    set_to_builtin_preset(hps[3], 'noZ')
