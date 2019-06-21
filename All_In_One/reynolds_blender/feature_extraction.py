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
import glob
import operator
import os
import pathlib
from shutil import copy

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

def mark_location_in_mesh(self, context):
    scene = context.scene
    print(scene.cursor_location)
    scene.location_in_mesh = scene.cursor_location
    print(' set loc in mesh ', scene.location_in_mesh)
    return {'FINISHED'}

def show_location_in_mesh(self, context):
    scene = context.scene
    print(' move cursor to loc in mesh ', scene.location_in_mesh)
    scene.cursor_location = scene.location_in_mesh
    return {'FINISHED'}

def generate_surface_dict(self, context):
    scene = context.scene
    surface_feature_dict = ReynoldsFoamDict('surfaceFeatureExtractDict.foam')

    for name, geometry_info in scene.geometries.items():
        if geometry_info['has_features']:
            print('generate feature extract dict for ', name)
            file_path = geometry_info.get('file_path', None)
            if file_path:
                key = os.path.basename(file_path)
            else:
                key = name
            surface_feature_dict[key] = {}
            surface_feature_dict[key]['extractionMethod'] = 'extractFromSurface'
            surface_feature_dict[key]['writeObj'] = 'yes'
            coeffs = {'includedAngle': geometry_info['included_angle']}
            surface_feature_dict[key]['extractFromSurfaceCoeffs'] = coeffs
            print(surface_feature_dict[key])

    print(surface_feature_dict)
    abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)
    system_dir = os.path.join(abs_case_dir_path, "system")
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    sfed_file_path = os.path.join(system_dir, "surfaceFeatureExtractDict")
    with open(sfed_file_path, "w") as f:
        f.write(str(surface_feature_dict))

    return {'FINISHED'}

def extract_surface_features(self, context):
    scene = context.scene
    case_dir = bpy.path.abspath(scene.case_dir_path)

    # -------------------------
    # Start the console operatorr
    # --------------------------
    bpy.ops.reynolds.of_console_op()

    scene.features_extracted = False

    # first copy all obj, stl files
    trisurface_dir = os.path.join(case_dir, 'constant', 'triSurface')
    if not os.path.exists(trisurface_dir):
        print('Creating trisurface dir: ', trisurface_dir)
        pathlib.Path(trisurface_dir).mkdir(parents=True, exist_ok=True)
    for geo_info in scene.geometries.values():
        print(' Geo info : ')
        if 'file_path' in geo_info:
            src_file = geo_info['file_path']
            print(' Copying geometry file ' + src_file + ' to ' + trisurface_dir)
            copy(src_file, trisurface_dir)

    cr = FoamCmdRunner(cmd_name='surfaceFeatureExtract', case_dir=case_dir)

    for info in cr.run():
        self.report({'WARNING'}, info)

    if cr.run_status:
        scene.features_extracted = True
        self.report({'INFO'}, 'SurfaceFeatureExtract : SUCCESS')
        # switch to layer 1
        context.scene.layers[0] = False
        context.scene.layers[2] = True
        glob_obj = os.path.join(case_dir, 'constant',
                                'extendedFeatureEdgeMesh', '*.obj')
        for block_obj_filepath in glob.glob(glob_obj):
            bpy.ops.import_scene.obj(filepath=block_obj_filepath)
            block_obj_filename = os.path.basename(block_obj_filepath)
            block_obj_name = os.path.splitext(block_obj_filename)[0]
            block_obj = context.scene.objects[block_obj_name]
            for i in range(20):
                block_obj.layers[i] = (i == 2)
        # switch back to layer 0
        context.scene.layers[2] = False
        context.scene.layers[0] = True
    else:
        self.report({'ERROR'}, 'SurfaceFeatureExtract : FAILED')

    return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class FeatureExtractionOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_fe_op"
    bl_label = "Feature Extraction"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    # Return True to force redraw
    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=750)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'feature_extraction.yaml')
        gui_renderer.render()

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('feature_extraction.yaml')
    create_custom_operators('feature_extraction.yaml', __name__)

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('feature_extraction.yaml')

if __name__ == "__main__":
    register()
