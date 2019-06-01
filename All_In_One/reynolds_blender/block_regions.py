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

def assign_region(self, context):
    print("Assigning region")

    scene = context.scene
    obj = context.active_object

    r_faces = []

    if scene.select_front_face:
        r_faces.append("Front")
    if scene.select_back_face:
        r_faces.append("Back")
    if scene.select_top_face:
        r_faces.append("Top")
    if scene.select_bottom_face:
        r_faces.append("Bottom")
    if scene.select_left_face:
        r_faces.append("Left")
    if scene.select_right_face:
        r_faces.append("Right")

    print(r_faces)
    item = scene.bmd_regions[scene.bmd_rindex]
    region_name = scene.region_name
    face_str = region_name + " : " + ' '.join(str(f) for f in r_faces)
    # empty {} for time properties p, U, T etc
    r = (scene.region_name, scene.region_type, r_faces, {}) 
    item.name = face_str
    scene.regions[region_name] = r
    print(scene.regions)

    # reset selections
    scene.select_front_face = False
    scene.select_back_face = False
    scene.select_top_face = False
    scene.select_bottom_face = False
    scene.select_right_face = False
    scene.select_left_face = False

    return{'FINISHED'}

def remove_region(self, context):
    scene = context.scene
    obj = context.active_object

    print("Before: Removing region")
    print(scene.bmd_regions)


    print(scene.bmd_rindex, scene.bmd_regions[scene.bmd_rindex])
    item = scene.bmd_regions[scene.bmd_rindex]
    r_name, _ = item.name.split(" : ", 1)
    scene.regions.pop(r_name, None)
    print("After: Removing region")
    print(scene.bmd_regions)
    item.name = ""
    return{'FINISHED'}

def load_regions(self, context):
    print("Initial loading of regions")
    scene = context.scene
    if not scene.regions_loaded:
        item_coll = scene.bmd_regions
        item_coll .clear()
        faces = ["Front", "Back", "Top", "Bottom", "Left", "Right"]
        index = 0
        for f in faces:
            r_faces = [f]
            item = item_coll.add()
            scene.bmd_rindex = index
            region_name = f
            face_str = region_name + " : " + region_name
            region_type = 'patch'
            r = (region_name, region_type, r_faces, {})
            item.name = face_str
            scene.regions[region_name] = r
            index += 1
        scene.regions_loaded = True

def assign_time_prop(self, context):
    print("Assigning time property")

    scene = context.scene
    obj = context.active_object

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
    item = scene.bmd_regions[scene.bmd_rindex]
    print ('Select region: ' + item.name)
    region_name = item.name.split(':')[0].strip()
    print(' Region data: ')
    _, _, _, time_prop_info = scene.regions[region_name]
    if not time_prop_type in time_prop_info:
        time_prop_info[time_prop_type] = {}
    time_prop_info[time_prop_type]['type'] = scene.time_prop_patch_type
    time_prop_info[time_prop_type]['value'] = scene.time_prop_value

    print(scene.time_props)
    print(scene.time_props_dimensions)
    print(scene.time_props_internal_field)
    for _, r in scene.regions.items():
        print(r)

    return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class BlockMeshRegionsOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_bmd_regions_panel"
    bl_label = "Regions"
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
        load_regions(self, context)
        return context.window_manager.invoke_props_dialog(self, width=750)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ---------------------------------------
        # Render Block Panel using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'block_regions.yaml')
        gui_renderer.render()


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('block_regions.yaml')
    create_custom_operators('block_regions.yaml', __name__)

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('block_regions.yaml')

if __name__ == "__main__":
    register()
