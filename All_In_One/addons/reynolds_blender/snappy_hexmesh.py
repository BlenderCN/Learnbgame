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
from reynolds_blender.geometry import GeometryOperator
from reynolds_blender.feature_extraction import FeatureExtractionOperator
from reynolds_blender.castellated_mesh import CastellatedMeshOperator
from reynolds_blender.snapping import SnappingOperator
from reynolds_blender.layers import LayersOperator
from reynolds_blender.mesh_quality import MeshQualityOperator
from reynolds_blender.snappy_steps import SnappyStepsOperator
from reynolds_blender.mesh_objs import ShowMeshObjOperator
from reynolds_blender.geo_patch_time_props import GeometryPatchTimePropsOperator

# ----------------
# reynolds imports
# ----------------
from reynolds.dict.parser import ReynoldsFoamDict
from reynolds.foam.cmd_runner import FoamCmdRunner

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

def generate_snappyhexmeshdict(self, context):
    scene = context.scene
    snappy_dict = ReynoldsFoamDict('snappyHexMeshDict.foam')

    # -------------------------
    # Start the console operatorr
    # --------------------------
    bpy.ops.reynolds.of_console_op()

    abs_case_dir_path = bpy.path.abspath(scene.case_dir_path)
    if abs_case_dir_path is None or abs_case_dir_path == '':
        self.report({'ERROR'}, 'Please select a case directory')
        return {'FINISHED'}

    if not scene.foam_started:
        self.report({'ERROR'}, 'Please start open foam')
        return {'FINISHED'}

    if (not scene.castellated_mesh_step and
        not scene.snap_step and
        not scene.add_layers_step):
        self.report({'ERROR'}, 'Please select the snappyhexmesh steps')
        return {'FINISHED'}

    if len(scene.geometries) == 0:
        self.report({'ERROR'}, 'Please add geometries')
        return {'FINISHED'}

    bmd_file_path = os.path.join(abs_case_dir_path, "system", "blockMeshDict")
    if not os.path.exists(bmd_file_path):
        self.report({'ERROR'}, 'Please generate block mesh dict')
        return {'FINISHED'}

    if not scene.blockmesh_executed:
        self.report({'ERROR'}, 'Please run blockMesh')
        return {'FINISHED'}

    sfed_file_path = os.path.join(abs_case_dir_path, "system",
                                  "surfaceFeatureExtractDict")
    if not os.path.exists(sfed_file_path):
        self.report({'ERROR'}, 'Please generate surface feature dict')
        return {'FINISHED'}

    if not scene.features_extracted:
        self.report({'ERROR'}, 'Please run extract surface features')
        return {'FINISHED'}

    # steps to run
    snappy_dict['castellatedMesh'] = scene.castellated_mesh_step
    snappy_dict['snap'] = scene.snap_step
    snappy_dict['addLayers'] = scene.add_layers_step

    for name, geometry_info in scene.geometries.items():
        print('generate feature extract dict for ', name)

        # geometry
        file_path = geometry_info.get('file_path', None)
        if file_path:
            key = os.path.basename(file_path)
            key_without_ext = os.path.splitext(key)[0]
        else:
            key = name
            key_without_ext = name
        print('key : key without ext' , key, ' : ', key_without_ext)
        if geometry_info['type'] == 'triSurfaceMesh':
            snappy_dict['geometry'][key] = {'type': geometry_info['type'],
                                            'name': key_without_ext }
        if geometry_info['type'] == 'searchableSphere':
            centre = geometry_info['centre']
            snappy_dict['geometry'][key] = {'type': geometry_info['type'],
                                            'centre': [centre.x, centre.z, centre.y],
                                            'radius': geometry_info['radius']}
        if geometry_info['type'] == 'searchableBox':
            level_min = geometry_info['min']
            level_max = geometry_info['max']
            snappy_dict['geometry'][key] = {'type': geometry_info['type'],
                                            'min': [level_min[0], level_min[2], level_min[1]],
                                            'max': [level_max[0], level_max[2], level_max[1]]}
        # features
        features = []
        if geometry_info['has_features']:
            features.append({'file': '"' + key_without_ext + '.eMesh' + '"',
                        'level': geometry_info['feature_level']})
            snappy_dict['castellatedMeshControls']['features'] = features

        # refinement surface
        if geometry_info['refinement_type'] == 'Surface':
            surface = {'level': [geometry_info['refinementSurface']['min'],
                                 geometry_info['refinementSurface']['max']]}
            snappy_dict['castellatedMeshControls']['refinementSurfaces'][key_without_ext] = surface

        # refinement region
        if geometry_info['refinement_type'] == 'Region':
            region = {'mode': geometry_info['refinementRegion']['mode'],
                      'levels': [[geometry_info['refinementRegion']['dist'],
                                  geometry_info['refinementRegion']['level']]]}
            snappy_dict['castellatedMeshControls']['refinementRegions'][key_without_ext] = region

        # castellatedMeshControls
        snappy_dict['castellatedMeshControls']['maxLocalCells'] = scene.max_local_cells
        snappy_dict['castellatedMeshControls']['maxGlobalCells'] = scene.max_global_cells
        snappy_dict['castellatedMeshControls']['minRefinementCells'] = scene.min_refinement_cells
        snappy_dict['castellatedMeshControls']['maxLoadUnbalance'] = scene.max_load_unbalance
        snappy_dict['castellatedMeshControls']['resolveFeatureAngle'] = scene.resolve_feature_angle
        location_in_mesh = scene.location_in_mesh
        if location_in_mesh[0] != 0 and location_in_mesh[1] != 0 and location_in_mesh[2] != 0:
            snappy_dict['castellatedMeshControls']['locationInMesh'] = [location_in_mesh[0],
                                                                        location_in_mesh[2],
                                                                        location_in_mesh[1]]
        snappy_dict['castellatedMeshControls']['allowFreeStandingZoneFaces'] = scene.allow_free_standing_zones

        # snapControls
        snappy_dict['snapControls']['nSmoothPatch'] = scene.n_smooth_patch_iter
        snappy_dict['snapControls']['tolerance'] = scene.tolerance
        snappy_dict['snapControls']['nSolveIter'] = scene.disp_relax_iter
        snappy_dict['snapControls']['nRelaxIter'] = scene.snapping_relax_iter
        snappy_dict['snapControls']['nFeatureSnapIter'] = scene.feature_edge_snapping_iter
        snappy_dict['snapControls']['implicitFeatureSanp'] = scene.implicit_feature_snap
        snappy_dict['snapControls']['explicitFeatureSnap'] = scene.explicit_feature_snap
        snappy_dict['snapControls']['multiRegionFeatureSnap'] = scene.multi_region_feature_snap

        # addLayersControls
        for name, layers in scene.add_layers.items():
            snappy_dict['addLayersControls']['layers'][name] = {'nSurfaceLayers': layers}
        snappy_dict['addLayersControls']['relativeSizes'] = scene.relative_sizes
        snappy_dict['addLayersControls']['expansionRatio'] = scene.expansion_ratio
        snappy_dict['addLayersControls']['finalLayerThickness'] = scene.final_layer_thickness
        snappy_dict['addLayersControls']['minThickness'] = scene.min_layer_thickness
        snappy_dict['addLayersControls']['nGrow'] = scene.n_grow_layers
        snappy_dict['addLayersControls']['featureAngle'] = scene.layer_feature_angle
        snappy_dict['addLayersControls']['nRelaxIter'] = scene.layer_n_relax_iter
        snappy_dict['addLayersControls']['nSmoothSurfaceNormals'] = scene.layer_n_smooth_normal_iter
        snappy_dict['addLayersControls']['nSmoothNormals'] = scene.layer_n_smooth_iter
        snappy_dict['addLayersControls']['nSmoothThickness'] = scene.smooth_layer_thickness
        snappy_dict['addLayersControls']['maxFaceThicknessRatio'] = scene.max_face_thickness_ratio
        snappy_dict['addLayersControls']['maxThicknessToMedialRatio'] = scene.max_thickness_to_medial_ratio
        snappy_dict['addLayersControls']['minMedianAxisAngle'] = scene.min_median_axis_angle
        snappy_dict['addLayersControls']['nBufferCellsNoExtrude'] = scene.n_buffer_cells_no_extrude
        snappy_dict['addLayersControls']['nLayerIter'] = scene.layer_n_add_iter
        snappy_dict['addLayersControls']['nRelaxedIter'] = scene.layer_n_mesh_quality_iter

        #meshQualityControls
        snappy_dict['meshQualityControls']['maxNonOrtho'] = scene.max_non_ortho
        snappy_dict['meshQualityControls']['maxBoundarySkewness'] = scene.max_boundary_skewness
        snappy_dict['meshQualityControls']['maxInternalFaceSkewness'] = scene.max_internal_face_skewness
        snappy_dict['meshQualityControls']['maxConcave'] = scene.max_concaveness
        if scene.min_pyramid_vol != 0:
            snappy_dict['meshQualityControls']['minVol'] = scene.min_pyramid_vol
        if scene.min_tetrahedral_quality != 0:
            snappy_dict['meshQualityControls']['minTetQuality'] = scene.min_tetrahedral_quality
        snappy_dict['meshQualityControls']['minArea'] = scene.min_face_area
        snappy_dict['meshQualityControls']['minTwist'] = scene.min_face_twist
        snappy_dict['meshQualityControls']['minDeterminant'] = scene.min_cell_det
        snappy_dict['meshQualityControls']['minFaceWeight'] = scene.min_face_weight
        snappy_dict['meshQualityControls']['minVolRatio'] = scene.min_vol_ratio
        snappy_dict['meshQualityControls']['minTriangleTwist'] = scene.min_tri_twist
        snappy_dict['meshQualityControls']['nSmoothScale'] = scene.n_smooth_scale
        snappy_dict['meshQualityControls']['errorReduction'] = scene.error_reduction

    print('--------------------')
    print('SNAPPY HEX MESH DICT')
    print('--------------------')
    print(snappy_dict)
    print('--------------------')
    system_dir = os.path.join(abs_case_dir_path, "system")
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    shmd_file_path = os.path.join(system_dir, "snappyHexMeshDict")
    with open(shmd_file_path, "w") as f:
        f.write(str(snappy_dict))


    return {'FINISHED'}

def run_snappyhexmesh(self, context):
    scene = context.scene
    case_dir = bpy.path.abspath(scene.case_dir_path)

    # -------------------------
    # Start the console operatorr
    # --------------------------
    bpy.ops.reynolds.of_console_op()
    generate_snappyhexmeshdict(self, context)

    if case_dir is None or case_dir == '':
        self.report({'ERROR'}, 'Please select a case directory')
        return {'FINISHED'}

    if not scene.foam_started:
        self.report({'ERROR'}, 'Please start open foam')
        return {'FINISHED'}

    shmd_file_path = os.path.join(case_dir, "system", "snappyHexMeshDict")
    if not os.path.exists(shmd_file_path):
        self.report({'ERROR'}, 'Please generate snappyHexMeshDict')
        return {'FINISHED'}

    scene.snappyhexmesh_executed = False
    cr = FoamCmdRunner(cmd_name='snappyHexMesh', case_dir=case_dir,
                       cmd_flags=['-overwrite'])

    for info in cr.run():
        self.report({'WARNING'}, info)

    if cr.run_status:
        scene.snappyhexmesh_executed = True
        self.report({'INFO'}, 'SnappyHexMesh : SUCCESS')
    else:
        self.report({'ERROR'}, 'SnappyHexMesh : FAILED')

    return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class SnappyHexMeshPanel(Panel):
    bl_idname = "of_snappy_hexmesh_panel"
    bl_label = "Snappy HexMesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.operator(SnappyStepsOperator.bl_idname, text='', icon='POSE_HLT')
        row.operator(GeometryOperator.bl_idname, text='', icon='GROUP')
        row.operator(FeatureExtractionOperator.bl_idname, text='', icon='SNAP_VERTEX')
        row.operator(CastellatedMeshOperator.bl_idname, text='', icon='MOD_REMESH')
        row.operator(SnappingOperator.bl_idname, text='', icon='SNAP_SURFACE')
        row.operator(LayersOperator.bl_idname, text='', icon='RENDERLAYERS')
        row.operator(MeshQualityOperator.bl_idname, text='', icon='SETTINGS')
        row.operator(ShowMeshObjOperator.bl_idname, text='', icon='FACESEL_HLT')
        row.operator(GeometryPatchTimePropsOperator.bl_idname, text='', icon='SETTINGS')

        # ---------------------------------------
        # Render Block Panel using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'snappy_hexmesh.yaml')
        gui_renderer.render()


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('snappy_hexmesh.yaml')
    create_custom_operators('snappy_hexmesh.yaml', __name__)

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('snappy_hexmesh.yaml')

if __name__ == "__main__":
    register()
