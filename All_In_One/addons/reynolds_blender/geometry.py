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

def import_stl(self, context):
    scene = context.scene
    bpy.ops.import_mesh.stl(filepath=scene.stl_file_path,
                            axis_forward='Z',
                            axis_up='Y')
    obj = scene.objects.active
    print('active objects after import ', obj)
    # -------------------------------------------------------------
    # TBD : OBJ IS NONE, if multiple objects are added after import
    # -------------------------------------------------------------
    scene.geometries[obj.name] = {'file_path': scene.stl_file_path}
    print('STL IMPORT: ', scene.geometries)
    return {'FINISHED'}

def import_obj(self, context):
    scene = context.scene
    bpy.ops.import_scene.obj(filepath=scene.obj_file_path)
    obj = scene.objects.active
    print('active objects after import ', obj)
    bpy.ops.object.transform_apply(location=False,
                                   rotation=True,
                                   scale=False)
    # -------------------------------------------------------------
    # TBD : OBJ IS NONE, if multiple objects are added after import
    # -------------------------------------------------------------
    scene.geometries[obj.name] = {'file_path': scene.obj_file_path}
    print('OBJ IMPORT: ', scene.geometries)
    return {'FINISHED'}

def assign_shmd_geometry(self, context):
    scene = context.scene
    obj = scene.objects.active
    item = scene.shmd_geometries[scene.shmd_gindex]
    item.name = obj.name
    scene.geometry_name = obj.name

    # store refinement and features info
    print(scene.geometries)
    geometry_info = scene.geometries.get(obj.name, {})
    print('obj ', obj.name, 'geometry_info :' , geometry_info)
    geometry_info['type'] = scene.geometry_type
    if geometry_info['type'] == 'searchableSphere':
        local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
        geometry_info['centre'] = obj.matrix_world * local_bbox_center
        x = [v[0] for v in obj.bound_box]
        x.sort()
        geometry_info['radius'] = (abs(x[0]) + abs(x[7])) / 2.0
    if geometry_info['type'] == 'searchableBox':
        x = [v[0] for v in obj.bound_box]
        x.sort()
        y = [v[2] for v in obj.bound_box]
        y.sort()
        z = [v[1] for v in obj.bound_box]
        z.sort()
        geometry_info['min'] = [x[0], y[0], z[0]]
        geometry_info['max'] = [x[7], y[7], z[7]]
    geometry_info['refinement_type'] = scene.refinement_type
    if scene.refinement_type == 'Surface':
        geometry_info['refinementSurface'] = {'min': scene.refinement_level_min,
                                                'max': scene.refinement_level_max}
    if scene.refinement_type == 'Region':
        geometry_info['refinementRegion'] = {'mode': scene.refinement_mode,
                                             'dist': scene.ref_reg_dist,
                                             'level': scene.ref_reg_level}
    # if has features, then generate emesh file name
    geometry_info['has_features'] = scene.has_features
    geometry_info['feature_level'] = scene.feature_extract_ref_level
    geometry_info['included_angle'] = scene.feature_extract_included_angle
    scene.geometries[obj.name] = geometry_info

    print('Assigned scene geometry...')
    print(scene.geometries)

    return {'FINISHED'}

def remove_shmd_geometry(self, context):
    print('remove_shmd_geometry: TBD')

    return {'FINISHED'}
# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class GeometryOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_geo_op"
    bl_label = "Geometry"

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
        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'geometry.yaml')
        gui_renderer.render()

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('geometry.yaml')
    create_custom_operators('geometry.yaml', __name__)

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('geometry.yaml')

if __name__ == "__main__":
    register()
