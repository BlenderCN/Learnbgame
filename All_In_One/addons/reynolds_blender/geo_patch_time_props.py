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

def load_geo_patch_objs(self, context):
    print ('load geo patch objs from case dir')
    scene = context.scene
    case_dir = bpy.path.abspath(scene.case_dir_path)
    print(scene.geometries)
    print(scene.regions)
    # get data items for UIList
    geo_patch_objs = []
    for info in scene.geometries.values():
        # geometry
        file_path = info.get('file_path', None)
        if file_path:
            key = os.path.basename(file_path)
            key_without_ext = os.path.splitext(key)[0]
            for r in scene.regions.keys():
                geo_patch_objs.append(key_without_ext + "_" + r)
    print(geo_patch_objs)

    # now populate UIList
    index = 0
    item_coll = scene.geo_patch_objs
    item_idx = scene.geo_patch_rindex
    item_coll.clear()
    for geo_patch in geo_patch_objs:
        item = item_coll.add()
        scene.geo_patch_rindex = index
        item.name = geo_patch
        index += 1
        scene.geo_patches[geo_patch] = {}
    print(scene.geo_patch_rindex, scene.geo_patch_objs)

    return {'FINISHED'}

def add_geo_patch_time_prop(self, context):
    print("Add geo patch time  prop")
    scene = context.scene

    # Store the distint time properties
    if scene.time_props is None:
        scene.time_props = []
    time_prop_type = scene.time_prop_type
    if not scene.time_prop_type in scene.time_props:
        scene.time_props.append(time_prop_type)

    # Store the dimensions for a time property
    if scene.time_props_dimensions is None:
        scene.time_props_dimensions = {}
    if not time_prop_type in scene.time_props_dimensions:
        scene.time_props_dimensions[time_prop_type] = scene.time_prop_dimensions

    # Store the internal field for a time property
    if scene.time_props_internal_field is None:
        scene.time_props_internal_field = {}
    if not time_prop_type in scene.time_props_internal_field:
        scene.time_props_internal_field[time_prop_type] = scene.time_prop_internal_field

    # Store the time property type and value for the patch
    item = scene.geo_patch_objs[scene.geo_patch_rindex]
    print ('Select geo region: ' + item.name)
    region_name = item.name
    print(' Region data: ')
    time_prop_info = scene.geo_patches[region_name]
    if not time_prop_type in time_prop_info:
        time_prop_info[time_prop_type] = {}
    time_prop_info[time_prop_type]['type'] = scene.time_prop_patch_type
    time_prop_info[time_prop_type]['value'] = scene.time_prop_value

    print(scene.time_props)
    print(scene.time_props_dimensions)
    print(scene.time_props_internal_field)
    print(scene.geo_patches)

    return{'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class GeometryPatchTimePropsOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_geo_patch_time_props"
    bl_label = "Add Geometry Patch Time Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return len(scene.geometries.keys()) > 0 and len(scene.regions.keys()) > 0

    def execute(self, context):
        return {'FINISHED'}

    # Return True to force redraw
    def check(self, context):
        return True

    def invoke(self, context, event):
        load_geo_patch_objs(self, context)
        return context.window_manager.invoke_props_dialog(self, width=750)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ---------------------------------------
        # Render Block Panel using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'geo_patch_time_props.yaml')
        gui_renderer.render()


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('geo_patch_time_props.yaml')
    create_custom_operators('geo_patch_time_props.yaml', __name__)

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('geo_patch_time_props.yaml')

if __name__ == "__main__":
    register()
