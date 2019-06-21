import bpy
import bpy_extras
import mathutils
import os.path as op
import sys
import glob
import numpy as np
import time
import mmvt_utils as mu
import selection_panel
import logging
import shutil
from collections import Iterable
import importlib

STAT_AVG, STAT_DIFF = range(2)

bpy.types.Scene.brain_imported = False
bpy.types.Scene.electrodes_imported = False
bpy.types.Scene.eeg_imported = False
bpy.types.Scene.brain_data_exist = False
bpy.types.Scene.electrodes_data_exist = False
bpy.types.Scene.eeg_data_exist = False


def bipolar_update(self, context):
    try:
        _addon().init_electrodes_labeling(DataMakerPanel.addon)
    except:
        pass


bpy.types.Scene.atlas = bpy.props.StringProperty(name='atlas', default='laus250')
bpy.types.Scene.bipolar = bpy.props.BoolProperty(default=False, update=bipolar_update,
    description='Sets whether the electrodes are bipolar or not')
bpy.types.Scene.electrodes_radius = bpy.props.FloatProperty(default=0.15, min=0.01, max=1,
    description='Sets the electrodes/spheres radius')
bpy.types.Scene.import_unknown = bpy.props.BoolProperty(default=False, description='Imports the data of all unknown labels')
bpy.types.Scene.inflated_morphing = bpy.props.BoolProperty(default=True, description="inflated_morphing")
bpy.types.Scene.meg_labels_data_files = bpy.props.EnumProperty(items=[],
    description='Selects the source estimated evoked response\n\nCurrent')
bpy.types.Scene.add_meg_labels_data_to_parent = bpy.props.BoolProperty(default=True)
bpy.types.Scene.add_meg_data_to_labels = bpy.props.BoolProperty(default=True, description="")
bpy.types.Scene.add_meg_subcorticals_data = bpy.props.BoolProperty(default=False, description="")
bpy.types.Scene.meg_evoked_files = bpy.props.EnumProperty(items=[], description="meg_evoked_files")
bpy.types.Scene.evoked_objects = bpy.props.EnumProperty(items=[], description="meg_evoked_types")
bpy.types.Scene.electrodes_positions_files = bpy.props.EnumProperty(items=[],
    description='Selects the electrodes position file.\n\nCurrent file')
bpy.types.Scene.eeg_sensors_data_files = bpy.props.EnumProperty(items=[],
    description='Selects the EEG sensors data file.\n\nCurrent file')
bpy.types.Scene.meg_sensors_data_files = bpy.props.EnumProperty(items=[],
    description='Selects the MEG sensors data file.\n\nCurrent file')
bpy.types.Scene.fMRI_dynamic_files = bpy.props.EnumProperty(items=[], description="fMRI_dynamic")
bpy.types.Scene.add_fmri_subcorticals_data = bpy.props.BoolProperty(default=True, description="")

bpy.types.Scene.brain_no_conds_stat = bpy.props.EnumProperty(items=[('diff', 'conditions difference', '', 0), ('mean', 'conditions average', '', 1)])
bpy.types.Scene.subcortical_fmri_files = bpy.props.EnumProperty(items=[])
bpy.types.Scene.meg_labels_extract_method = bpy.props.StringProperty()
bpy.types.Scene.fmri_labels_extract_method = bpy.props.StringProperty(default='mean')
bpy.types.Scene.add_meg_labels_data_overwrite = bpy.props.BoolProperty(default=True,
    description='Overwrites the existing evoked data')
bpy.types.Scene.data_overwrite_electrodes = bpy.props.BoolProperty(default=True)


def _addon():
    return DataMakerPanel.addon


def eeg_data_and_meta():
    if DataMakerPanel.eeg_data is None:
        data_fname = op.join(mu.get_user_fol(), 'eeg', 'eeg_data.npy')
        meta_fname = op.join(mu.get_user_fol(), 'eeg', 'eeg_data_meta.npz')
        if op.isfile(data_fname) and op.isfile(meta_fname):
            DataMakerPanel.eeg_data = np.load(data_fname, mmap_mode='r')
            DataMakerPanel.eeg_meta = np.load(meta_fname)
        else:
            DataMakerPanel.eeg_data = DataMakerPanel.eeg_meta = None
    return DataMakerPanel.eeg_data, DataMakerPanel.eeg_meta


@mu.tryit()
def import_hemis_for_functional_maps(base_path):
    mu.change_layer(_addon().BRAIN_EMPTY_LAYER)
    layers_array = bpy.context.scene.layers
    emptys_names = ['Functional maps', 'Subcortical_meg_activity_map', 'Subcortical_fmri_activity_map']
    for name in emptys_names:
        create_empty_if_doesnt_exists(name, _addon().BRAIN_EMPTY_LAYER, layers_array, 'Functional maps')

    print("importing Hemispheres")
    now = time.time()
    ply_files = glob.glob(op.join(base_path, 'surf', '*.ply'))
    N = len(ply_files)
    for ind, ply_fname in enumerate(ply_files):
        try:
            mu.time_to_go(now, ind, N, 10)
            bpy.ops.object.select_all(action='DESELECT')
            obj_name = mu.namebase(ply_fname).split(sep='.')[0]
            surf_name = mu.namebase(ply_fname).split(sep='.')[1]
            if surf_name == 'inflated':
                obj_name = '{}_{}'.format(surf_name, obj_name)
                # mu.change_layer(_addon().INFLATED_ACTIVITY_LAYER)
                layer = _addon().INFLATED_ACTIVITY_LAYER
            elif surf_name == 'pial':
                # mu.change_layer(_addon().ACTIVITY_LAYER)
                layer = _addon().ACTIVITY_LAYER
            else:
                raise Exception('The surface type {} is not supported!'.format(surf_name))
            if bpy.data.objects.get(obj_name) is None:
                load_ply(op.join(base_path, 'surf', ply_fname), obj_name, layer=layer)
        except:
            mu.log_err('Error in importing {}'.format(ply_fname), logging)

    _addon().create_inflated_curv_coloring()
    bpy.ops.object.select_all(action='DESELECT')


def load_ply(ply_fname, obj_name, parent_name='Functional maps', material_name='Activity_map_mat',
             layer=None, new_material_name=''):
    if layer is None:
        layer = _addon().INFLATED_ACTIVITY_LAYER
    mu.change_layer(layer)
    bpy.ops.import_mesh.ply(filepath=ply_fname)
    cur_obj = bpy.context.selected_objects[0]
    cur_obj.select = True
    bpy.ops.object.shade_smooth()
    cur_obj.scale = [0.1] * 3
    cur_obj.hide = False
    cur_obj.name = obj_name
    if new_material_name == '':
        cur_obj.active_material = bpy.data.materials[material_name]
    else:
        cur_obj.active_material = bpy.data.materials[material_name].copy()
        if bpy.data.materials.get(new_material_name) is not None:
            bpy.data.materials[new_material_name].use_fake_user = False
            bpy.data.materials.remove(bpy.data.materials[new_material_name], do_unlink=True)
        cur_obj.active_material.name = new_material_name

    cur_obj.parent = bpy.data.objects[parent_name]
    cur_obj.hide_select = True
    cur_obj.data.vertex_colors.new()
    return cur_obj


def create_subcortical_activity_mat(name):
    cur_mat = bpy.data.materials['subcortical_activity_mat'].copy()
    cur_mat.name = name + '_Mat'


@mu.tryit()
def import_subcorticals(base_path, parent_name='Subcortical'):
    empty_layer = DataMakerPanel.addon.BRAIN_EMPTY_LAYER
    brain_layer = DataMakerPanel.addon.ACTIVITY_LAYER

    bpy.context.scene.layers = [ind == empty_layer for ind in range(len(bpy.context.scene.layers))]
    layers_array = bpy.context.scene.layers
    emptys_names = ['Functional maps', '{}_meg_activity_map'.format(parent_name), '{}_fmri_activity_map'.format(parent_name)]
    for name in emptys_names:
        create_empty_if_doesnt_exists(name, empty_layer, layers_array, 'Functional maps')
    bpy.context.scene.layers = [ind == brain_layer for ind in range(len(bpy.context.scene.layers))]

    print("importing Subcortical structures")
    # for cur_val in bpy.context.scene.layers:
    #     print(cur_val)
    #  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    base_paths = [base_path] * 2 # Read the bast_path twice, for meg and fmri
    PATH_TYPE_SUB_MEG, PATH_TYPE_SUB_FMRI = range(2)
    for path_type, base_path in enumerate(base_paths):
        for ply_fname in glob.glob(op.join(base_path, '*.ply')):
            try:
                obj_name = mu.namebase(ply_fname)
                if path_type==PATH_TYPE_SUB_MEG and not bpy.data.objects.get('{}_meg_activity'.format(obj_name)) is None:
                    continue
                if path_type==PATH_TYPE_SUB_FMRI and not bpy.data.objects.get('{}_fmri_activity'.format(obj_name)) is None:
                    continue
                bpy.ops.object.select_all(action='DESELECT')
                print(ply_fname)
                bpy.ops.import_mesh.ply(filepath=op.join(base_path, ply_fname))
                cur_obj = bpy.context.selected_objects[0]
                cur_obj.select = True
                bpy.ops.object.shade_smooth()
                cur_obj.scale = [0.1] * 3
                cur_obj.hide = False
                cur_obj.name = obj_name

                if path_type == PATH_TYPE_SUB_MEG:
                    cur_obj.name = '{}_meg_activity'.format(obj_name)
                    curMat = bpy.data.materials.get('{}_mat'.format(cur_obj.name))
                    if curMat is None:
                        # todo: Fix the succortical_activity_Mat to succortical_activity_mat
                        curMat = bpy.data.materials['succortical_activity_Mat'].copy()
                        curMat.name = '{}_mat'.format(cur_obj.name)
                    cur_obj.active_material = bpy.data.materials[curMat.name]
                    cur_obj.parent = bpy.data.objects['{}_meg_activity_map'.format(parent_name)]
                elif path_type == PATH_TYPE_SUB_FMRI:
                    cur_obj.name = '{}_fmri_activity'.format(obj_name)
                    if 'cerebellum' in cur_obj.name.lower():
                        cur_obj.active_material = bpy.data.materials['Activity_map_mat']
                    else:
                        cur_obj.active_material = bpy.data.materials['subcortical_activity_mat']
                    cur_obj.parent = bpy.data.objects['{}_fmri_activity_map'.format(parent_name)]
                else:
                    mu.log_err('import_subcorticals: Wrong path_type! Nothing to do...', logging)
                cur_obj.hide_select = True
                mu.fix_children_normals('{}_meg_activity_map'.format(parent_name))
            except:
                mu.log_err('Error in importing {}!'.format(ply_fname), logging)
    bpy.ops.object.select_all(action='DESELECT')


class AnatomyPreproc(bpy.types.Operator):
    bl_idname = "mmvt.anatomy_preproc"
    bl_label = "anatomy_preproc"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        cmd = '{} -m src.preproc.anatomy_preproc -s {} -a {} --ignore_missing 1'.format(
            bpy.context.scene.python_cmd, mu.get_user(), bpy.context.scene.atlas)
        print('Running {}'.format(cmd))
        mu.run_command_in_new_thread(cmd, False)
        return {"FINISHED"}


def import_brain(context=None):
    # self.brain_layer = DataMakerPanel.addon.BRAIN_EMPTY_LAYER
    # self.current_root_path = mu.get_user_fol()  # bpy.path.abspath(bpy.context.scene.conf_path)
    if _addon() is None:
        mu.log_err('import_brain: addon is None!', logging)
        return
    user_fol = mu.get_user_fol()
    mu.write_to_stderr('Importing ROIs...')
    import_rois(user_fol)
    mu.write_to_stderr('Importing functional maps...')
    import_hemis_for_functional_maps(user_fol)
    mu.write_to_stderr('Importing subcorticals...')
    import_subcorticals(op.join(user_fol, 'subcortical'))
    # if op.isdir(op.join(user_fol, 'cerebellum')):
    #     import_subcorticals(op.join(user_fol, 'cerebellum'), 'Cerebellum')
    if context:
        last_obj = context.active_object.name
        print('last obj is -' + last_obj)
    if bpy.context.scene.inflated_morphing:
        mu.write_to_stderr('Creating inflating morphing...')
        create_inflating_morphing()
    if bpy.data.objects.get(' '):
        bpy.data.objects[' '].select = True
        if context:
            context.scene.objects.active = bpy.data.objects[' ']
    if context:
        bpy.data.objects[last_obj].select = False
    DataMakerPanel.addon.show_rois()
    bpy.types.Scene.brain_imported = True
    print('cleaning up')
    for obj in bpy.data.objects['Subcortical_structures'].children:
        # print(obj.name)
        if obj.name[-1] == '1':
            obj.name = obj.name[0:-4]
    bpy.ops.object.select_all(action='DESELECT')
    mu.write_to_stderr('Brain importing is Finished!')
    atlas = mu.get_real_atlas_name(bpy.context.scene.atlas, short_name=True)
    blend_fname = op.join(mu.get_parent_fol(mu.get_user_fol()), '{}_{}.blend'.format(mu.get_user(), atlas))
    bpy.ops.wm.save_as_mainfile(filepath=blend_fname)
    _addon().load_all_panels(first_time=True)


# class FixBrainMaterials(bpy.types.Operator):
#     bl_idname = "mmvt.fix_brain_materials"
#     bl_label = "fix_brain_materials"
#     bl_options = {"UNDO"}
#
#     def invoke(self, context, event=None):
#         _addon().fix_cortex_labels_material()
#         return {"FINISHED"}


class UpdateMMVT(bpy.types.Operator):
    bl_idname = "mmvt.update_mmvt"
    bl_label = "update mmvt"
    bl_description = 'Updates the tool with the latest version.\n*Works on Linux only.' \
                     '\n\nScript: mmvt.data.update_code()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        update_code()
        return {"FINISHED"}


class ImportBrain(bpy.types.Operator):
    bl_idname = "mmvt.brain_importing"
    bl_label = "import2 brain"
    bl_description = 'Imports all the brain objects created using the anatomy preprocessing pipeline (src.preproc.anatomy).' \
                     '\n\nScript: mmvt.data.import_brain()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        import_brain()
        return {"FINISHED"}


def create_empty_if_doesnt_exists(name, brain_layer=None, layers_array=None, parent_obj_name='Brain'):
    if brain_layer is None:
        brain_layer = _addon().BRAIN_EMPTY_LAYER
    if layers_array is None:
        layers_array = bpy.context.scene.layers
    if bpy.data.objects.get(name) is None:
        layers_array[brain_layer] = True
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=(0, 0, 0), layers=layers_array)
        bpy.data.objects['Empty'].name = name
        if name != parent_obj_name:
            bpy.data.objects[name].parent = bpy.data.objects[parent_obj_name]
    return bpy.data.objects[name]


@mu.tryit()
def import_rois(base_path, selected_inputs=None):
    if selected_inputs is None:
        anatomy_inputs = {
            'Cortex-rh': op.join(base_path, 'labels', '{}.pial.rh'.format(bpy.context.scene.atlas)),
            'Cortex-lh': op.join(base_path, 'labels','{}.pial.lh'.format(bpy.context.scene.atlas)),
            'Cortex-inflated-rh': op.join(base_path, 'labels', '{}.inflated.rh'.format(bpy.context.scene.atlas)),
            'Cortex-inflated-lh': op.join(base_path, 'labels', '{}.inflated.lh'.format(bpy.context.scene.atlas)),
            'Subcortical_structures': op.join(base_path, 'subcortical'),
            'Cerebellum': op.join(base_path, 'cerebellum')}
    else:
        anatomy_inputs = selected_inputs
    brain_layer = _addon().BRAIN_EMPTY_LAYER

    bpy.context.scene.layers = [ind == brain_layer for ind in range(len(bpy.context.scene.layers))]
    layers_array = bpy.context.scene.layers
    emptys_names = ['Brain'] + list(anatomy_inputs.keys()) # ["Brain", "Subcortical_structures", "Cortex-lh", "Cortex-rh", 'Cortex-inflated-rh', 'Cortex-inflated-rh']
    for name in emptys_names:
        create_empty_if_doesnt_exists(name, brain_layer, layers_array)
    bpy.context.scene.layers = [ind == DataMakerPanel.addon.ROIS_LAYER for ind in range(len(bpy.context.scene.layers))]

    # todo: check each hemi
    inflated_imported = False
    for anatomy_name, anatomy_input_base_path in anatomy_inputs.items():
        if not op.isdir(anatomy_input_base_path):
            mu.log_err('import_rois: The anatomy folder {} does not exist'.format(anatomy_input_base_path), logging)
            continue
        current_mat = bpy.data.materials['unselected_label_Mat_cortex']
        if anatomy_name in ['Subcortical_structures', 'Cerebellum']:
            current_mat = bpy.data.materials['unselected_label_Mat_subcortical']
        print('importing from {}'.format(anatomy_input_base_path))
        for ply_fname in glob.glob(op.join(anatomy_input_base_path, '*.ply')):
            try:
                new_obj_name = mu.namebase(ply_fname)
                fol_name = anatomy_input_base_path.split(op.sep)[-1]
                surf_name = 'pial' if fol_name == 'subcortical' or len(fol_name.split('.')) == 1 else fol_name.split('.')[-2]
                if surf_name == 'inflated':
                    new_obj_name = '{}_{}'.format(surf_name, new_obj_name)
                    mu.change_layer(_addon().INFLATED_ROIS_LAYER)
                elif surf_name == 'pial':
                    mu.change_layer(_addon().ROIS_LAYER)
                if not bpy.data.objects.get(new_obj_name) is None:
                    # print('{} was already imported'.format(new_obj_name))
                    continue
                if 'inflated' in new_obj_name:
                    inflated_imported = True
                bpy.ops.object.select_all(action='DESELECT')
                # print(ply_fname)
                bpy.ops.import_mesh.ply(filepath=op.join(anatomy_input_base_path, ply_fname))
                cur_obj = bpy.context.selected_objects[0]
                cur_obj.select = True
                bpy.ops.object.shade_smooth()
                cur_obj.parent = bpy.data.objects[anatomy_name]
                cur_obj.scale = [0.1] * 3
                cur_obj.active_material = current_mat
                cur_obj.hide = False
                cur_obj.name = new_obj_name
                mu.fix_children_normals(anatomy_name)
            except:
                mu.log_err('import_rois: Error in importing {}'.format(ply_fname), logging)
            # cur_obj.location[0] += 5.5 if 'rh' in anatomy_name else -5.5
            # time.sleep(0.3)
    # if inflated_imported:
    #     bpy.data.objects['Cortex-inflated-rh'].location[0] += 5.5
    #     bpy.data.objects['Cortex-inflated-lh'].location[0] -= 5.5
    bpy.ops.object.select_all(action='DESELECT')


def create_eeg_mesh():
    eeg_mesh_fname = op.join(mu.get_user_fol(), 'eeg', 'eeg_helmet.ply')
    if not op.isfile(eeg_mesh_fname):
        print('You need to create a mesh first ({})'.format(eeg_mesh_fname))
        return None
    mu.change_layer(_addon().BRAIN_EMPTY_LAYER)
    create_empty_if_doesnt_exists('Helmets', _addon().BRAIN_EMPTY_LAYER, bpy.context.scene.layers, 'Functional maps')
    mu.change_layer(_addon().EEG_LAYER)
    current_mat = bpy.data.materials['Helmet_map_mat']
    bpy.ops.import_mesh.ply(filepath=eeg_mesh_fname)
    mesh_obj = bpy.context.selected_objects[0]
    mesh_obj.name = 'eeg_helmet'
    mesh_obj.select = True
    bpy.ops.object.shade_smooth()
    mesh_obj.parent = bpy.data.objects['Helmets']
    mesh_obj.scale = [0.1] * 3
    mesh_obj.active_material = current_mat
    mesh_obj.hide = False
    return mesh_obj


def recalc_eeg_mesh_faces_verts():
    calc_eeg_mesh_verts_sensors()
    mu.add_mmvt_code_root_to_path()
    from src.utils import utils
    importlib.reload(utils)
    eeg_helmet = bpy.data.objects.get('eeg_helmet')
    if eeg_helmet is None:
        print('eeg helmet is None!')
        return
    verts = np.array([v.co for v in eeg_helmet.data.vertices])
    faces = np.array([f.vertices for f in eeg_helmet.data.polygons])
    out_file = op.join(mu.get_user_fol(), 'eeg', 'eeg_faces_verts.npy')
    ply_file_name = op.join(mu.get_user_fol(), 'eeg', 'eeg_helmet.ply')
    utils.calc_ply_faces_verts(verts, faces, out_file, overwrite=True)
    utils.write_ply_file(verts, faces, ply_file_name, write_also_npz=True)
    mu.fix_children_normals('eeg_helmet')


def calc_eeg_mesh_verts_sensors():
    eeg_helmet = bpy.data.objects.get('eeg_helmet')
    eeg_helmet_indices = None
    if eeg_helmet is not None and bpy.data.objects.get('EEG_sensors'):
        from scipy.spatial.distance import cdist
        eeg_helmet_vets_loc = np.array([v.co for v in eeg_helmet.data.vertices])
        # eeg_sensors_loc = np.array(
        #     [eeg_obj.location * 10 for eeg_obj in bpy.data.objects['EEG_sensors'].children])
        eeg_sensors_loc = np.array(
            [eeg_obj.matrix_world.to_translation() * 10 for eeg_obj in bpy.data.objects['EEG_sensors'].children])
        max_dists = np.max(np.min(cdist(eeg_sensors_loc, eeg_helmet_vets_loc), axis=1))
        if max_dists > 0.01:
            print('calc_eeg_mesh_verts_sensors: Wrong distances!')
        eeg_helmet_indices = np.argmin(cdist(eeg_sensors_loc, eeg_helmet_vets_loc), axis=1)
    mu.save(eeg_helmet_indices, op.join(mu.get_user_fol(), 'eeg', 'eeg_vertices_sensors.pkl'))


def create_meg_mesh():
    meg_mesh_fname = op.join(mu.get_user_fol(), 'meg', 'meg_helmet.ply')
    if not op.isfile(meg_mesh_fname):
        print('You need to create a mesh first ({})'.format(meg_mesh_fname))
        return None
    mu.change_layer(_addon().BRAIN_EMPTY_LAYER)
    create_empty_if_doesnt_exists('Helmets', _addon().BRAIN_EMPTY_LAYER, bpy.context.scene.layers, 'Functional maps')
    mu.change_layer(_addon().MEG_LAYER)
    current_mat = bpy.data.materials['Helmet_map_mat']
    bpy.ops.import_mesh.ply(filepath=meg_mesh_fname)
    mesh_obj = bpy.context.selected_objects[0]
    mesh_obj.name = 'meg_helmet'
    mesh_obj.select = True
    bpy.ops.object.shade_smooth()
    mesh_obj.parent = bpy.data.objects['Helmets']
    mesh_obj.scale = [0.1] * 3
    mesh_obj.active_material = current_mat
    mesh_obj.hide = False
    return mesh_obj


def recalc_meg_mesh_faces_verts():
    calc_meg_mesh_verts_sensors()
    mu.add_mmvt_code_root_to_path()
    from src.utils import utils
    importlib.reload(utils)
    meg_helmet = bpy.data.objects.get('meg_helmet')
    if meg_helmet is None:
        print('meg helmet is None!')
        return
    verts = np.array([v.co for v in meg_helmet.data.vertices])
    faces = np.array([f.vertices for f in meg_helmet.data.polygons])
    out_file = op.join(mu.get_user_fol(), 'meg', 'meg_faces_verts.npy')
    ply_file_name = op.join(mu.get_user_fol(), 'meg', 'meg_helmet.ply')
    utils.calc_ply_faces_verts(verts, faces, out_file, overwrite=True)
    utils.write_ply_file(verts, faces, ply_file_name, write_also_npz=True)
    mu.fix_children_normals('meg_helmet')


def calc_meg_mesh_verts_sensors():
    meg_helmet = bpy.data.objects.get('meg_helmet')
    meg_helmet_indices = {}
    if meg_helmet is not None and bpy.data.objects.get('MEG_sensors'):
        from scipy.spatial.distance import cdist
        meg_helmet_vets_loc = np.array([v.co for v in meg_helmet.data.vertices])
        for sensor_type in _addon().meg.get_meg_sensors_types().keys():
            meg_sensors_loc = np.array(
                [meg_obj.location * 10 for meg_obj in bpy.data.objects['MEG_{}_sensors'.format(sensor_type)].children])
            max_dists = np.max(np.min(cdist(meg_sensors_loc, meg_helmet_vets_loc), axis=1))
            if max_dists > 0.01:
                raise Exception('Wrong distances!')
            meg_helmet_indices[sensor_type] = np.argmin(cdist(meg_sensors_loc, meg_helmet_vets_loc), axis=1)
    mu.save(meg_helmet_indices, op.join(mu.get_user_fol(), 'meg', 'meg_vertices_sensors.pkl'))


class ImportRois(bpy.types.Operator):
    bl_idname = "mmvt.roi_importing"
    bl_label = "import2 ROIs"
    bl_options = {"UNDO"}
    current_root_path = ''

    def invoke(self, context, event=None):
        self.current_root_path = mu.get_user_fol() #bpy.path.abspath(bpy.context.scene.conf_path)
        import_hemis_for_functional_maps(self.current_root_path)
        return {"FINISHED"}


def import_meg_sensors(overwrite_sensors=False):
    layers_array = [False] * 20
    create_empty_if_doesnt_exists('MEG_sensors', _addon().BRAIN_EMPTY_LAYER, layers_array, 'MEG_sensors')

    input_files = glob.glob(op.join(mu.get_user_fol(), 'meg', 'meg_*_sensors_positions.npz'))
    for input_file in input_files:
        sensors_type = mu.namebase(input_file).split('_')[1]
        create_empty_if_doesnt_exists(
            'MEG_{}_sensors'.format(sensors_type), _addon().BRAIN_EMPTY_LAYER, layers_array, 'MEG_sensors')
        import_electrodes(
            input_file, _addon().MEG_LAYER, bipolar=False, parnet_name='MEG_{}_sensors'.format(sensors_type),
            overwrite=overwrite_sensors)
    bpy.types.Scene.meg_sensors_imported = True
    print('MEG sensors importing is Finished ')


def import_eeg_sensors(overwrite_sensors=False):
    input_file = op.join(mu.get_user_fol(), 'eeg', 'eeg_sensors_positions.npz')
    import_electrodes(input_file, _addon().EEG_LAYER, bipolar=False, parnet_name='EEG_sensors',
                      overwrite=overwrite_sensors)
    bpy.types.Scene.eeg_imported = True
    print('EEG sensors importing is Finished ')


def export_eeg_sensors(parnet_name='EEG_sensors'):
    parent_obj = bpy.data.objects.get(parnet_name)
    if parent_obj is None:
        print('Can\'t find the parent object! ({})'.format(parnet_name))
        return
    sensors_tup = [(elc_obj.matrix_world.to_translation() * 10, elc_obj.name) for elc_obj in parent_obj.children]
    sensors_pos = np.array([t[0] for t in sensors_tup])
    sensors_names = np.array([t[1] for t in sensors_tup])
    fol = mu.make_dir(op.join(mu.get_user_fol(), 'eeg'))
    output_fname = op.join(fol, 'eeg_sensors_positions.npz')
    np.savez(output_fname, pos=sensors_pos, names=sensors_names)
    print('EEG sensors were export to {}'.format(output_fname))


def export_meg_sensors(parnet_name='MEG_sensors'):
    parent_obj = bpy.data.objects.get(parnet_name)
    if parent_obj is None:
        print('Can\'t find the parent object! ({})'.format(parnet_name))
        return
    sensors_tup = [(elc_obj.matrix_world.to_translation() * 10, elc_obj.name) for elc_obj in parent_obj.children]
    sensors_pos = np.array([t[0] for t in sensors_tup])
    sensors_names = np.array([t[1] for t in sensors_tup])
    fol = mu.make_dir(op.join(mu.get_user_fol(), 'eeg'))
    output_fname = op.join(fol, 'meg_sensors_positions.npz')
    np.savez(output_fname, pos=sensors_pos, names=sensors_names)
    print('MEG sensors were export to {}'.format(output_fname))


def get_electrodes_radius():
    return bpy.context.scene.electrodes_radius


def create_electrode(pos, elc_name, electrode_size=None, layers_array=None, parnet_name='', color='',
                     subject_tkreg_ras=False):
    if parnet_name == '':
        parnet_name = _addon().electrodes_panel_parent
    if electrode_size is None:
        electrode_size = bpy.context.scene.electrodes_radius
    if layers_array is None:
        layers_array = [False] * 20
        layers_array[_addon().ELECTRODES_LAYER] = True
    if bpy.data.objects.get(parnet_name, None) is None:
        parent_layers_array = [False] * 20
        create_empty_if_doesnt_exists(parnet_name, _addon().BRAIN_EMPTY_LAYER, parent_layers_array, parnet_name)

    if not subject_tkreg_ras:
        x, y, z = mathutils.Vector(pos) * mu.get_matrix_world()
    else:
        x, y, z = pos
    if not bpy.data.objects.get(elc_name) is None:
        cur_obj = bpy.data.objects[elc_name]
        cur_obj.location = [x, y, z]
    else:
        print('creating {}: {}'.format(elc_name, (x, y, z)))
        mu.create_sphere((x, y, z), electrode_size, layers_array, elc_name)
        cur_obj = bpy.data.objects[elc_name]
        cur_obj.select = True
        cur_obj.parent = bpy.data.objects[parnet_name]
        mu.create_and_set_material(cur_obj)
    if color != '':
        _addon().coloring.object_coloring(cur_obj, color)
    return cur_obj


def update_code():
    try:
        import git
    except:
        print('You should install first gitpython. Run the following command:')
        print('python -m src.setup -f install_blender_req')
        return
    g = git.cmd.Git(mu.get_mmvt_code_root())
    g.pull()
    _addon().load_all_panels()


def import_electrodes(input_file='', electrodes_layer=None, bipolar='', electrode_size=None,
                      parnet_name='Deep_electrodes', elecs_pos=None, elecs_names=None, overwrite=False):
    if electrodes_layer is None:
        electrodes_layer = _addon().ELECTRODES_LAYER
    if not electrode_size is None:
        bpy.context.scene.electrodes_radius = electrode_size
    if bipolar != '':
        bpy.context.scene.bipolar = bool(bipolar)
    if overwrite:
        mu.delete_hierarchy(parnet_name)
    if input_file != '':
        if op.isfile(input_file):
            f = np.load(input_file)
            elecs_pos, elecs_names = f['pos'], f['names']
        else:
            print("Can't find electrodes input file! {}".format(input_file))
            return False
    if not overwrite and bpy.data.objects.get(parnet_name, None) is not None:
        electrodes_num = len(bpy.data.objects[parnet_name].children)
        if electrodes_num == len(elecs_names):
            print("The electrodes are already imported.")
            return True
        else:
            print('Wrong number of electrodes, deleting the object')
            mu.delete_hierarchy(parnet_name)

    layers_array = [False] * 20
    create_empty_if_doesnt_exists(parnet_name, _addon().BRAIN_EMPTY_LAYER, layers_array, parnet_name)
    layers_array = [False] * 20
    layers_array[electrodes_layer] = True

    for elc_pos, elc_name in zip(elecs_pos, elecs_names):
        if not isinstance(elc_name, str):
            elc_name = elc_name.astype(str)
        elc_name = elc_name.replace(' ', '')
        create_electrode(elc_pos, elc_name, electrode_size, layers_array, parnet_name)


@mu.tryit(None, False)
def create_inflating_morphing():
    print('Creating inflation morphing')
    for hemi in mu.HEMIS:
        pial = bpy.data.objects[hemi]
        inflated = mu.get_hemi_obj(hemi)
        # if inflated.active_shape_key_index >= 0:
        #     print('{} already has a shape key'.format(hemi))
        #     continue
        inflated.shape_key_add(name='pial')
        inflated.shape_key_add(name='inflated')
        for vert_ind in range(len(inflated.data.vertices)):
            for ii in range(3):
                inflated.data.shape_keys.key_blocks['pial'].data[vert_ind].co[ii] = pial.data.vertices[vert_ind].co[ii]


@mu.tryit(None, False)
def create_inflating_flat_morphing():
    print('Creating inflation flat morphing')
    # for hemi in mu.HEMIS:
    #     verts_faces_dic = op.join(mu.get_user_fol(), 'faces_verts_lookup_{}.pkl'.format(hemi))
    #     flat_surf = op.join(mu.get_user_fol, 'surf', '{}.flat.pial.npz'.format(hemi))
    #     inflated = mu.get_hemi_obj(hemi)
    #     if op.isfile(flat_surf):
    #         flat_verts, _ = np.load(flat_surf)
    #         inflated.shape_key_add(name='flat')
    #         for vert_ind in range(len(inflated.data.vertices)):
    #             for ii in range(3):
    #                 inflated.data.shape_keys.key_blocks['flat'].data[vert_ind].co[ii] = flat_verts[vert_ind][ii]

    for hemi in mu.HEMIS:
        cur_obj = mu.get_hemi_obj(hemi)
        d = np.load(op.join(mu.get_user_fol(), 'surf', '{}.flat.pial.npz'.format(hemi)))
        flat_faces, flat_verts = d['faces'], d['verts']

        # vg = cur_obj.vertex_groups.new('bad_vertices')
        # d = mu.load(op.join(mu.get_user_fol(), 'flat_bad_vertices.pkl'))
        # bad_vertices = d[hemi]
        # good_vertices = list(set(np.unique(flat_faces)))
        # bad_vertices = set(np.arange(0, len(flat_verts))).difference(set(np.unique(flat_faces)))
        vg = cur_obj.vertex_groups.new('valid_vertices')
        valid_vertices = np.unique(flat_faces)
        for vertex_ind in valid_vertices:
            vg.add([int(vertex_ind)], 1.0, 'ADD')
        # for vertex_ind in bad_vertices:
        #     vg.add([int(vertex_ind)], 1.0, 'ADD')

        # flat_verts_means = np.mean(flat_verts[valid_vertices], 0)
        # flat_verts_norm = flat_verts - np.tile(flat_verts_means, (flat_verts.shape[0], 1))

        # for vert_ind in list(bad_vertices):
        #     flat_verts_norm[vert_ind] = (0.0, 0.0, 0.0)

        shapekey = cur_obj.shape_key_add(name='flat')
        postfix = ''
        flatmap_orientation = 1
        if hemi == 'lh':
            postfix = '.001'
            flatmap_orientation = -1
        shapekey.relative_key = bpy.data.shape_keys['Key{}'.format(postfix)].key_blocks["inflated"]
        for vert in cur_obj.data.vertices:
            # shapekey.data[vert.index].co = (flat_verts[vert.index, 1] * -10 + 200 * flatmap_orientation, 0, flat_verts[vert.index, 0] * -10)
            shapekey.data[vert.index].co = tuple([flat_verts[vert.index, ind] for ind in range(3)])

        modifier = cur_obj.modifiers.new('mask_bad_vertices', 'MASK')
        modifier.vertex_group = 'valid_vertices'
        # modifier.vertex_group = 'bad_vertices'
        # modifier.invert_vertex_group = True




class ImportElectrodes(bpy.types.Operator):
    bl_idname = "mmvt.electrodes_importing"
    bl_label = "import2 electrodes"
    bl_description = 'Imports the electrode objects'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        input_file = op.join(mu.get_user_fol(), 'electrodes',
                             '{}.npz'.format(bpy.context.scene.electrodes_positions_files))
        import_electrodes(input_file, _addon().ELECTRODES_LAYER, overwrite=bpy.context.scene.data_overwrite_electrodes)
        bpy.types.Scene.electrodes_imported = True
        print('Electrodes importing is Finished ')
        return {"FINISHED"}


class ImportMEGSensors(bpy.types.Operator):
    bl_idname = "mmvt.import_meg_sensors"
    bl_label = "import meg sensors"
    bl_description = 'Imports MEG Sensors objects.\n\nScript: mmvt.data.import_meg_sensore()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        if bpy.data.objects.get('MEG_sensors', None) is None:
            import_meg_sensors()
        else:
            export_meg_sensors()
        return {"FINISHED"}


class ImportEEGSensors(bpy.types.Operator):
    bl_idname = "mmvt.import_eeg_sensors"
    bl_label = "import eeg sensors"
    bl_description = 'Imports EEG Sensors objects'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        eeg_sensors_positions_file = op.join(mu.get_user_fol(), 'eeg', 'eeg_sensors_positions.npz')
        if bpy.data.objects.get('EEG_sensors', None) is None:
        # if op.isfile(eeg_sensors_positions_file):
            import_eeg_sensors()
        else:
            export_eeg_sensors()
        return {"FINISHED"}


class CreateMEGMesh(bpy.types.Operator):
    bl_idname = "mmvt.meg_mesh"
    bl_label = "meg mesh"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        if bpy.data.objects.get('meg_helmet'):
            recalc_meg_mesh_faces_verts()
        else:
            create_meg_mesh()
        return {"FINISHED"}


class CreateEEGMesh(bpy.types.Operator):
    bl_idname = "mmvt.eeg_mesh"
    bl_label = "eeg mesh"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        if bpy.data.objects.get('eeg_helmet'):
            recalc_eeg_mesh_faces_verts()
        else:
            create_eeg_mesh()
        return {"FINISHED"}


def add_data_to_brain(source_files):
    print('Adding data to Brain')
    conditions = []
    for f in source_files:
        T = len(f['data'][0])
        for obj_name, data in zip(f['names'], f['data']):
            if data.ndim == 1 and len(f['conditions']) == 1:
                data = data.reshape((len(data), 1))
            data = data.squeeze()
            obj_name = obj_name.astype(str)
            if not bpy.context.scene.import_unknown and 'unknown' in obj_name:
                continue
            add_data_to_obj(obj_name, data, f['conditions'])
        conditions.extend(f['conditions'])
    try:
        bpy.ops.graph.previewrange_set()
    except:
        pass

    bpy.types.Scene.maximal_time_steps = T
    for obj in bpy.data.objects:
        obj.select = False
    if bpy.data.objects.get(' '):
        bpy.context.scene.objects.active = bpy.data.objects[' ']
    selection_panel.set_conditions_enum(conditions)
    print('Finished keyframing!!')


def add_data_to_obj(obj_name, data, conditions):
    cur_obj = bpy.data.objects.get(obj_name, None)
    if cur_obj is None:
        print('add_data_to_obj: can\'t find {}!'.format(obj_name))
        return
    data = data.squeeze()
    T = len(data)
    clear_animation = False
    fcurves_num = mu.count_fcurves(cur_obj)
    if cur_obj.animation_data is not None:
        if len(cur_obj.animation_data.action.fcurves[0].keyframe_points) != T + 1:
            clear_animation = True
    if fcurves_num < len(conditions):
        clear_animation = True

    # if fcurves_num != len(f['conditions']) or keyframe_points_num != data.shape[0]:
    if clear_animation:
        cur_obj.animation_data_clear()
        print('keyframing {}'.format(obj_name))
        for cond_ind, cond_str in enumerate(conditions):
            cond_str = cond_str.astype(str)
            # Set the values to zeros in the first and last frame for current object(current label)
            mu.insert_keyframe_to_custom_prop(cur_obj, obj_name + '_' + cond_str, 0, 1)
            mu.insert_keyframe_to_custom_prop(cur_obj, obj_name + '_' + cond_str, 0, len(data))

            # For every time point insert keyframe to current object
            cond_data = data[:, cond_ind] if data.ndim == 2 else np.reshape(data, (len(data), 1))
            for ind, t in enumerate(cond_data):
                mu.insert_keyframe_to_custom_prop(cur_obj, obj_name + '_' + cond_str, t, ind)

            # remove the orange keyframe sign in the fcurves window
            fcurves = bpy.data.objects[obj_name].animation_data.action.fcurves[cond_ind]
            mod = fcurves.modifiers.new(type='LIMITS')
    elif bpy.context.scene.add_meg_labels_data_overwrite:
        for fcurve_ind, fcurve in enumerate(cur_obj.animation_data.action.fcurves):
            fcurve.keyframe_points[0].co[1] = 0
            fcurve.keyframe_points[-1].co[1] = 0
            cond_data = data[:, fcurve_ind] if data.ndim == 2 else np.reshape(data, (len(data), 1))
            for t in range(T):
                fcurve.keyframe_points[t + 1].co[1] = cond_data[t, fcurve_ind]


def add_data_pool(parent_name, data, conditions):
    root_name = 'data_pool'
    root_obj = bpy.data.objects.get(root_name)
    if root_obj is None:
        layers_array = [False] * 20
        create_empty_if_doesnt_exists(root_name, _addon().BRAIN_EMPTY_LAYER, layers_array, root_name)
    data_obj = bpy.data.objects.get(parent_name)
    if data_obj is None:
        layers_array = [False] * 20
        create_empty_if_doesnt_exists(parent_name, _addon().BRAIN_EMPTY_LAYER, layers_array, root_name)
    add_data_to_obj(parent_name, data, conditions)



# def add_data_to_parent_brain_obj(brain_sources, subcorticals_sources, stat=STAT_DIFF):
#     if bpy.context.scene.add_meg_labels_data_to_parent:
#         brain_obj = bpy.data.objects['Brain']
#         add_data_to_parent_obj(brain_obj, brain_sources, stat)
#     if bpy.context.scene.add_meg_subcorticals_data:
#         subcorticals_obj = bpy.data.objects['Subcortical_structures']
#         add_data_to_parent_obj(subcorticals_obj, subcorticals_sources, stat)
#     mu.view_all_in_graph_editor()


def add_fmri_dynamics_to_parent_obj(add_fmri_subcorticals_data=True):
    brain_obj = create_empty_if_doesnt_exists('fMRI')
    measure = bpy.context.scene.fMRI_dynamic_files.split(' ')[-1]
    sources = [np.load(op.join(mu.get_user_fol(), 'fmri', 'labels_data_{}_{}_{}.npz'.format(
        bpy.context.scene.atlas, measure, hemi))) for hemi in mu.HEMIS]
    if (bpy.context.scene.add_fmri_subcorticals_data or add_fmri_subcorticals_data) and \
            DataMakerPanel.subcortical_fmri_data_exist:
        sources.append(np.load(op.join(mu.get_user_fol(), 'fmri', '{}.npz'.format(
            bpy.context.scene.subcortical_fmri_files))))
    add_data_to_parent_obj(brain_obj, sources, STAT_AVG)
    mu.view_all_in_graph_editor()


def add_data_to_meg_sensors(stat=STAT_DIFF):
    parnet_name = 'MEG_sensors'
    parent_obj = bpy.data.objects.get(parnet_name)
    if parent_obj is None:
        layers_array = [False] * 20
        create_empty_if_doesnt_exists(parnet_name, _addon().BRAIN_EMPTY_LAYER, layers_array, parnet_name)

    # data_fname = op.join(mu.get_user_fol(), 'meg', '{}.npy'.format(bpy.context.scene.meg_sensors_data_files))
    # meta_fname = op.join(mu.get_user_fol(), 'meg', '{}_meta.npz'.format(bpy.context.scene.meg_sensors_data_files))
    # pos_files = glob.glob(op.join(mu.get_user_fol(), 'meg', 'meg_*_sensors_positions.npz'))
    # sensors_types = [mu.namebase(f).split('_')[1] for f in pos_files]
    # for bpy.context.scene.meg_sensors_types in sensors_types:
    #     print('sensors types: {}'.format(bpy.context.scene.meg_sensors_types))
    data, meta = _addon().meg.get_meg_sensors_data()
    # if not op.isfile(data_fname) or not op.isfile(meta_fname):
    if data is None or meta is None:
        mu.log_err('Can\'t find MEG sensors data files!')
        # mu.log_err('MEG data should be here {} (data) and here {} (meta data)'.format(data_fname, meta_fname), logging)
    else:
        # data = DataMakerPanel.meg_data = np.load(data_fname, mmap_mode='r')
        # meta = DataMakerPanel.meg_meta = np.load(meta_fname)
        animation_conditions = mu.get_animation_conditions(parent_obj, take_my_first_child=True)
        data_conditions = meta['conditions']
        clear_animation = False # set(animation_conditions) != set(data_conditions)
        # add_data_to_electrodes_parent_obj(parent_obj, data, meta, stat, clear_animation=clear_animation)
        add_data_to_electrodes(data, meta, clear_animation=clear_animation)
        # extra_objs = set([o.name for o in parent_obj.children]) - set(meta['names'])
        # for extra_obj in extra_objs:
        #     mu.delete_object(extra_obj)
        bpy.types.Scene.eeg_data_exist = True
    if bpy.data.objects.get(' '):
        bpy.context.scene.objects.active = bpy.data.objects[' ']


def add_data_to_eeg_sensors():
    parnet_name = 'EEG_sensors'
    parent_obj = bpy.data.objects.get(parnet_name)
    if parent_obj is None:
        layers_array = [False] * 20
        create_empty_if_doesnt_exists(parnet_name, _addon().BRAIN_EMPTY_LAYER, layers_array, parnet_name)
    data, meta = _addon().meg.get_eeg_sensors_data()
    if data is None or meta is None:
        mu.log_err('Can\'t find EEG sensors data files!')
    else:
        # DataMakerPanel.eeg_data, DataMakerPanel.eeg_meta = load_eeg_sensors_data(data_fname, meta_fname)
        # todo: check why window_len==2
        add_data_to_electrodes(data, meta)#, conditions='spikes1')#, window_len=2)
        add_data_to_electrodes_parent_obj(parent_obj, data, meta)#, condition_ind=0)#, window_len=2)
        bpy.types.Scene.eeg_data_exist = True
    if bpy.data.objects.get(' '):
        bpy.context.scene.objects.active = bpy.data.objects[' ']


def add_meg_data_to_parent_obj():
    base_path = mu.get_user_fol()
    brain_obj = bpy.data.objects['Brain']
    brain_sources = [np.load(op.join(base_path, 'meg', 'labels_data_{}_{}.npz'.format(
        bpy.context.scene.meg_labels_data_files, hemi))) for hemi in mu.HEMIS]
    add_data_to_parent_obj(brain_obj, brain_sources, STAT_DIFF)


def add_data_to_parent_obj(parent_obj, source_files, stat):
    sources = {}
    if not isinstance(source_files, Iterable):
        source_files = [source_files]
    for f in source_files:
        for obj_name, data in zip(f['names'], f['data']):
            obj_name = obj_name.astype(str)
            data = data.squeeze()
            # Check if there is only one condition
            if data.ndim == 1 or data.shape[1] == 1:
                stat = STAT_AVG
            if bpy.data.objects.get(obj_name) is None:
                if obj_name.startswith('rh') or obj_name.startswith('lh'):
                    obj_name = obj_name[3:]
                # todo: add a flag to the gui?
                # if bpy.data.objects.get(obj_name) is None:
                #     continue
            if not bpy.context.scene.import_unknown and 'unkown' in obj_name:
                continue
            if stat == STAT_AVG and data.ndim > 1:
                data_stat = np.squeeze(np.mean(data, axis=1))
            elif stat == STAT_DIFF and data.ndim > 1:
                data_stat = np.squeeze(np.diff(data, axis=1))
            else:
                data_stat = data
            sources[obj_name] = data_stat
    if len(sources) == 0:
        mu.log_err('No sources in {}'.format(source_files), logging)
        return
    sources_names = sorted(list(sources.keys()))
    N = len(sources_names)
    T = len(sources[sources_names[0]])
    fcurves_num = mu.count_fcurves(parent_obj)
    if fcurves_num < len(sources_names):
        parent_obj.animation_data_clear()
        now = time.time()
        for obj_counter, source_name in enumerate(sources_names):
            mu.time_to_go(now, obj_counter, N, runs_num_to_print=10)
            data = sources[source_name]
            # Set the values to zeros in the first and last frame for Brain object
            mu.insert_keyframe_to_custom_prop(parent_obj, source_name, 0, 1)
            mu.insert_keyframe_to_custom_prop(parent_obj, source_name, 0, T)

            # For every time point insert keyframe to the main Brain object
            for ind in range(data.shape[0]):
                mu.insert_keyframe_to_custom_prop(parent_obj, source_name, data[ind], ind)

            # remove the orange keyframe sign in the fcurves window
            fcurves = parent_obj.animation_data.action.fcurves[obj_counter]
            mod = fcurves.modifiers.new(type='LIMITS')
    else:
        for fcurve_ind, fcurve in enumerate(parent_obj.animation_data.action.fcurves):
            fcurve_name = mu.get_fcurve_name(fcurve)
            fcurve.keyframe_points[0].co[1] = 0
            fcurve.keyframe_points[-1].co[1] = 0
            T = min([len(fcurve.keyframe_points) - 1, len(sources[fcurve_name])])
            for t in range(T):
                fcurve.keyframe_points[t + 1].co[1] = sources[fcurve_name][t]

    if bpy.data.objects.get(' '):
        bpy.context.scene.objects.active = bpy.data.objects[' ']
    print('Finished keyframing the brain parent obj!!')


class AddDataToBrain(bpy.types.Operator):
    bl_idname = "mmvt.brain_add_data"
    bl_label = "add_data brain"
    bl_description = 'Adds the evoked data'
    bl_options = {"UNDO"}
    current_root_path = ''

    def invoke(self, context, event=None):
        base_path = mu.get_user_fol()
        brain_sources = [
            np.load(op.join(base_path, 'meg', 'labels_data_{}_lh.npz'.format(bpy.context.scene.meg_labels_data_files))),
            np.load(op.join(base_path, 'meg', 'labels_data_{}_rh.npz'.format(bpy.context.scene.meg_labels_data_files)))]
        if op.isfile(op.join(base_path, 'meg', 'subcortical_meg_activity.npz')):
            subcorticals_sources = [np.load(op.join(base_path, 'meg', 'subcortical_meg_activity.npz'))]
        else:
            subcorticals_sources = None
        if bpy.context.scene.add_meg_data_to_labels:
            add_data_to_brain(brain_sources)
        if bpy.context.scene.add_meg_labels_data_to_parent:
            brain_obj = bpy.data.objects['Brain']
            add_data_to_parent_obj(brain_obj, brain_sources, STAT_DIFF)
        if bpy.context.scene.add_meg_subcorticals_data and not subcorticals_sources is None:
            subcorticals_obj = bpy.data.objects['Subcortical_structures']
            add_data_to_parent_obj(subcorticals_obj, subcorticals_sources, STAT_DIFF)

        #todo: why?
        # bpy.context.scene.meg_labels_extract_method = '-'.join(bpy.context.scene.meg_labels_data_files.split('_')[-2:])
        bpy.context.scene.meg_labels_extract_method = '_'.join(bpy.context.scene.meg_labels_data_files.split('_')[-2:])
        _addon().select_all_rois()
        _addon().init_meg_labels_coloring_type()
        mu.view_all_in_graph_editor()
        bpy.types.Scene.brain_data_exist = True
        return {"FINISHED"}


class AddfMRIDynamicsToBrain(bpy.types.Operator):
    bl_idname = "mmvt.add_fmri_dynamics_to_brain"
    bl_label = "add_fmri_dynamics_to_brain"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        add_fmri_dynamics_to_parent_obj()
        return {"FINISHED"}


# class SelectExternalMEGEvoked(bpy.types.Operator):
#     bl_idname = "mmvt.select_external_meg_evoked"
#     bl_label = "select_external_meg_evoked"
#     bl_options = {"UNDO"}
#
#     def invoke(self, context, event=None):
#         evoked_name = '{}_{}'.format(bpy.context.scene.meg_evoked_files, bpy.context.scene.evoked_objects)
#         evoked_obj = bpy.data.objects.get(evoked_name)
#         if not evoked_obj is None:
#             evoked_obj.select = not evoked_obj.select
#         mu.view_all_in_graph_editor(context)
#         selected_objects = mu.get_selected_objects()
#         mu.change_fcurves_colors(selected_objects)
#         return {"FINISHED"}


# def get_external_meg_evoked_selected():
#     evoked_name = '{}_{}'.format(bpy.context.scene.meg_evoked_files, bpy.context.scene.evoked_objects)
#     evoked_obj = bpy.data.objects.get(evoked_name)
#     if not evoked_obj is None:
#         return evoked_obj.select
#     else:
#         return False


# def get_meg_evoked_source_files(base_path, files_prefix):
#     source_files = [op.join(base_path, '{}labels_data_lh.npz'.format(files_prefix)),
#                     op.join(base_path, '{}labels_data_rh.npz'.format(files_prefix)),
#                     op.join(base_path, '{}sub_cortical_activity.npz'.format(files_prefix))]
#     return source_files


# class AddOtherSubjectMEGEvokedResponse(bpy.types.Operator):
#     bl_idname = "mmvt.other_subject_meg_evoked"
#     bl_label = "other_subject_meg_evoked"
#     bl_options = {"UNDO"}
#
#     def invoke(self, context, event=None):
#         evoked_name = bpy.context.scene.meg_evoked_files
#         files_prefix = '{}_'.format(evoked_name)
#         base_path = op.join(mu.get_user_fol(), 'meg_evoked_files')
#         source_files = get_meg_evoked_source_files(base_path, files_prefix)
#         empty_layer = _addon().BRAIN_EMPTY_LAYER
#         layers_array = bpy.context.scene.layers
#         parent_obj_name = 'External'
#         create_empty_if_doesnt_exists(parent_obj_name, empty_layer, layers_array, parent_obj_name)
#         for input_file in source_files:
#             if not op.isfile(input_file):
#                 continue
#             f = np.load(input_file)
#             for label_name in f['names']:
#                 mu.create_empty_in_vertex((0, 0, 0), '{}_{}'.format(evoked_name, label_name),
#                     _addon().BRAIN_EMPTY_LAYER, parent_obj_name)
#
#         add_data_to_brain(base_path, files_prefix, files_prefix)
#         _meg_evoked_files_update()
#         return {"FINISHED"}

@mu.tryit()
def add_data_to_electrodes(all_data, meta_data, window_len=None, conditions=None, clear_animation=False):
    print('Adding data to Electrodes')
    now = time.time()
    N = len(meta_data['names'])
    T = all_data.shape[1] if window_len is None or not 'dt' in meta_data else int(window_len / meta_data['dt'])
    conditions = [mu.to_str(c) for c in meta_data['conditions']] if conditions is None else conditions
    # if isinstance(conditions[0], np.bytes_):
    #     conditions = [c.decode('utf_8') for c in meta_data['conditions']]
    # else:
    #     conditions = [str(c) for c in meta_data['conditions']]
    # if isinstance(conditions, str):
    #     conditions = [conditions]
    print('keyframing for {}'.format(meta_data['names']))
    for obj_counter, (obj_name, data) in enumerate(zip(meta_data['names'], all_data)):
        mu.time_to_go(now, obj_counter, N, runs_num_to_print=10)
        obj_name = mu.to_str(obj_name)
        # print(obj_name)
        if bpy.data.objects.get(obj_name, None) is None:
            obj_name = obj_name.replace(' ', '')
        if bpy.data.objects.get(obj_name, None) is None:
            mu.log_err("{} doesn't exist!".format(obj_name), logging)
            continue
        cur_obj = bpy.data.objects[obj_name]
        fcurves_num = mu.count_fcurves(cur_obj)
        if data.ndim == 1:
            data = data.reshape((-1, 1))
        if fcurves_num == len(conditions):
            fcurve_len = len(cur_obj.animation_data.action.fcurves[0].keyframe_points)
        else:
            fcurve_len = T
        if not clear_animation:
            clear_animation = fcurves_num != len(conditions) or fcurve_len < T
        if clear_animation:
            add_data_to_electrode(data, cur_obj, obj_name, conditions, T)
        else:
            for fcurve_ind, fcurve in enumerate(cur_obj.animation_data.action.fcurves):
                fcurve.keyframe_points[0].co[1] = 0
                fcurve.keyframe_points[-1].co[1] = 0
                for t in range(T):
                    fcurve.keyframe_points[t + 1].co[1] = data[t, fcurve_ind]

    conditions = meta_data['conditions']
    print('Finished keyframing!!')
    return conditions


def add_data_to_electrode(data, cur_obj, obj_name, conditions, T):
    cur_obj.animation_data_clear()
    for cond_ind, cond_str in enumerate(conditions):
        cond_str = cond_str.astype(str) if not isinstance(cond_str, str) else cond_str
        # Set the values to zeros in the first and last frame for current object(current label)
        mu.insert_keyframe_to_custom_prop(cur_obj, obj_name + '_' + cond_str, 0, 1)
        # todo: +2? WTF?!?
        mu.insert_keyframe_to_custom_prop(cur_obj, obj_name + '_' + cond_str, 0, T + 2)

        print('keyframing ' + obj_name + ' object in condition ' + cond_str)
        # For every time point insert keyframe to current object
        data_cond_ind = conditions.index(cond_str)  # np.where(conditions == cond_str)[0][0]
        for ind, t in enumerate(data[:T, data_cond_ind]):
            mu.insert_keyframe_to_custom_prop(cur_obj, obj_name + '_' + str(cond_str), t, ind + 2)
        # remove the orange keyframe sign in the fcurves window
        fcurves = bpy.data.objects[obj_name].animation_data.action.fcurves[cond_ind]
        mod = fcurves.modifiers.new(type='LIMITS')


@mu.tryit()
def add_data_to_electrodes_parent_obj(parent_obj, all_data, meta, stat=STAT_DIFF, window_len=None, condition_ind=None,
                                      clear_animation=False):
    # todo: merge with add_data_to_brain_parent_obj, same code
    sources = {}
    # for obj_name, data in zip(f['names'], f['data']):
    all_data_stat = meta['stat'] if 'stat' in meta else [None] * len(meta['names'])
    T = all_data.shape[1] if window_len is None or 'dt' not in meta else int(window_len / meta['dt'])
    for obj_name, data, data_stat in zip(meta['names'], all_data, all_data_stat):
        obj_name = mu.to_str(parent_obj).replace(' ', '')
        if data.ndim == 1:
            data = data.reshape((-1, 1))
        if data_stat is None:
            if condition_ind is not None:
                data_stat = data[:, condition_ind]
            elif stat == STAT_AVG or data.shape[1] != 2:
                data_stat = np.squeeze(np.mean(data, axis=1))
            elif stat == STAT_DIFF and data.shape[1] == 2:
                data_stat = np.squeeze(np.diff(data, axis=1))
        sources[obj_name] = data_stat

    sources_names = sorted(list(sources.keys()))
    N = len(sources_names)
    # T = _addon().get_max_time_steps() # len(sources[sources_names[0]]) + 2
    fcurves_num = mu.count_fcurves(parent_obj)
    if parent_obj.animation_data is not None:
        if len(parent_obj.animation_data.action.fcurves[0].keyframe_points) != T + 2:
            clear_animation = True
    if fcurves_num < len(sources_names):
        clear_animation = True
    if clear_animation:
        now = time.time()
        parent_obj.animation_data_clear()
        for obj_counter, source_name in enumerate(sources_names):
            mu.time_to_go(now, obj_counter, N, runs_num_to_print=10)
            data = sources[source_name]
            mu.insert_keyframe_to_custom_prop(parent_obj, source_name, 0, 1)
            mu.insert_keyframe_to_custom_prop(parent_obj, source_name, 0, T + 2)

            for ind in range(T):
                mu.insert_keyframe_to_custom_prop(parent_obj, source_name, data[ind], ind + 2)

            fcurves = parent_obj.animation_data.action.fcurves[obj_counter]
            mod = fcurves.modifiers.new(type='LIMITS')
    else:
        for fcurve_ind, fcurve in enumerate(parent_obj.animation_data.action.fcurves):
            fcurve_name = mu.get_fcurve_name(fcurve)
            if fcurve_name not in sources:
                print('{} not in sources!'.format(fcurve_name))
                continue
            fcurve.keyframe_points[0].co[1] = 0
            fcurve.keyframe_points[-1].co[1] = 0
            for t in range(T):
                fcurve.keyframe_points[t + 1].co[1] = sources[fcurve_name][t]

    mu.view_all_in_graph_editor()
    print('Finished keyframing {}!!'.format(parent_obj.name))


def load_meg_labels_data():
    base_path = mu.get_user_fol()
    rh_fname = op.join(base_path, 'meg', 'labels_data_{}_lh.npz'.format(bpy.context.scene.meg_labels_data_files))
    lh_fname = op.join(base_path, 'meg', 'labels_data_{}_rh.npz'.format(bpy.context.scene.meg_labels_data_files))
    if op.isfile(rh_fname) and op.isfile(lh_fname):
        data_rh = np.load(rh_fname)
        data_lh = np.load(lh_fname)
        data = np.concatenate((data_rh['data'], data_lh['data']))
        names = np.concatenate((data_rh['names'], data_lh['names']))
        return data, names, data_rh['conditions']
    else:
        return None, None, None


def load_electrodes_dists():
    if DataMakerPanel.electrodes_dists is None:
        fol = op.join(mu.get_user_fol(), 'electrodes')
        data_file = op.join(fol, 'electrodes_dists.npy')
        if op.isfile(data_file):
            dists = np.load(data_file)
            DataMakerPanel.electrodes_dists = dists
        else:
            dists = None
    else:
        dists = DataMakerPanel.electrodes_dists
    return dists


def load_electrodes_data(stat='diff'):
    return DataMakerPanel.electrodes_data, DataMakerPanel.electrodes_names, DataMakerPanel.electrodes_conditions

    # bip = 'bipolar_' if bpy.context.scene.bipolar else ''
    # if DataMakerPanel.electrodes_data is None:
    #     fol = op.join(mu.get_user_fol(), 'electrodes')
    #     data_file = op.join(fol, 'electrodes_{}data.npz'.format(bip))
    #     if op.isfile(data_file):
    #         f = np.load(data_file)
    #         data = f['data']
    #         names = f['names']
    #         conditions = f['conditions']
    #     elif op.isfile(op.join(fol, 'electrodes_{}data.npy'.format(bip))) and \
    #             op.isfile(op.join(fol, 'electrodes_{}meta_data.npz'.format(bip))):
    #         data_file = op.join(fol, 'electrodes_{}data.npy'.format(bip))
    #         data = np.load(data_file)
    #         meta_data = np.load(op.join(fol, 'electrodes_{}meta_data.npz'.format(bip)))
    #         names = meta_data['names']
    #         conditions = meta_data['conditions']
    #     else:
    #         data, names, conditions = None, None, None
    #     DataMakerPanel.electrodes_data = data
    #     names = DataMakerPanel.electrodes_names = [mu.to_str(n) for n in names]
    #     conditions = DataMakerPanel.electrodes_conditions = [mu.to_str(c) for c in conditions]
    #     return data, names, conditions
    # else:
    #     return DataMakerPanel.electrodes_data, DataMakerPanel.electrodes_names, DataMakerPanel.electrodes_conditions

def set_bipolar(val):
    bpy.context.scene.bipolar = val


def meg_evoked_files_update(self, context):
    _meg_evoked_files_update()


def _meg_evoked_files_update():
    external_obj = bpy.data.objects.get('External', None)
    if not external_obj is None:
        evoked_name = bpy.context.scene.meg_evoked_files
        DataMakerPanel.externals = [ext.name[len(evoked_name) + 1:] for ext in external_obj.children \
                                    if ext.name.startswith(evoked_name)]
        items = [(name, name, '', ind) for ind, name in enumerate(DataMakerPanel.externals)]
        bpy.types.Scene.evoked_objects = bpy.props.EnumProperty(items=items, description="meg_evoked_types")


def add_data_to_electrodes_and_parent():
    # self.current_root_path = bpy.path.abspath(bpy.context.scene.conf_path)
    parent_obj = bpy.data.objects['Deep_electrodes']
    base_path = mu.get_user_fol()
    source_file = glob.glob(op.join(base_path, 'electrodes', 'electrodes{}_data*.npy'.format(
        '_bipolar' if bpy.context.scene.bipolar else '')))[0]
    # 'avg' if bpy.context.scene.selection_type == 'conds' else 'diff'))
    data, meta = DataMakerPanel.electrodes_data, DataMakerPanel.electrodes_meta_data
    if not data is None and not meta is None:
        print('Loading electordes data from {}'.format(source_file))
        add_data_to_electrodes_parent_obj(parent_obj, data, meta)
        add_data_to_electrodes(data, meta)
        # selection_panel.set_conditions_enum(conditions)
        bpy.types.Scene.electrodes_data_exist = True
    if bpy.data.objects.get(' '):
        bpy.context.scene.objects.active = bpy.data.objects[' ']


def data_draw(self, context):
    layout = self.layout
    # layout.prop(context.scene, 'conf_path')
    # col = self.layout.column(align=True)
    layout.operator(UpdateMMVT.bl_idname, text="Update MMVT", icon='POSE_HLT')
    col = layout.box().column()
    # col.prop(context.scene, 'atlas', text="Atlas")
    col.label(text='Atlas: {}'.format(context.scene.atlas))
    col.operator(ImportBrain.bl_idname, text="Import Brain", icon='MATERIAL_DATA')
    # col.prop(context.scene, 'inflated_morphing', text="Include inflated morphing")
    # col.operator(FixBrainMaterials.bl_idname, text="Fix brain materials", icon='PARTICLE_DATA')

    if mu.both_hemi_files_exist(op.join(mu.get_user_fol(), 'surf', '{}.flat.pial.npz'.format('{hemi}'))):
        col.operator(StartFlatProcess.bl_idname, text="Import flat surface", icon='MATERIAL_DATA')

    if DataMakerPanel.electrodes_positions_exist:
        col = layout.box().column()
        col.prop(context.scene, 'electrodes_radius', text="Electrodes' radius")
        col.prop(context.scene, 'electrodes_positions_files', text="")
        col.prop(context.scene, 'bipolar', text="Bipolar")
        col.operator(ImportElectrodes.bl_idname, text="Import Electrodes", icon='COLOR_GREEN')
        if DataMakerPanel.electrodes_data_exist:
            col.operator(AddDataToElectrodes.bl_idname, text="Add data to Electrodes", icon='FCURVE')
        col.operator(ChooseElectrodesPositionsFile.bl_idname, text="Load electrodes positions",
            icon='GROUP_VERTEX').filepath = op.join(mu.get_user_fol(), 'electrodes', '*.npz')
        col.prop(context.scene, 'data_overwrite_electrodes', text='Overwrite')
    else:
        col = layout.box().column()
        col.operator(ChooseElectrodesPositionsFile.bl_idname, text="Load electrodes positions",
            icon='GROUP_VERTEX').filepath = op.join(mu.get_user_fol(), 'electrodes', '*.npz')

    if DataMakerPanel.meg_labels_data_exist:
        col = layout.box().column()
        col.prop(context.scene, 'meg_labels_data_files', text="")
        col.operator(AddDataToBrain.bl_idname, text="Add MEG data to Brain", icon='FCURVE')
        # row = col.row(align=True)
        col.prop(context.scene, 'add_meg_data_to_labels', text="Add data to labels")
        col.prop(context.scene, 'add_meg_labels_data_to_parent', text="Add conditions difference data")
        col.prop(context.scene, 'add_meg_labels_data_overwrite', text="Overwrite")
        col.prop(context.scene, 'import_unknown', text="Import unknown")
    if DataMakerPanel.subcortical_meg_data_exist:
        col.prop(context.scene, 'add_meg_subcorticals_data', text="subcorticals")

    if DataMakerPanel.fMRI_dynamic_exist:
        col = layout.box().column()
        col.prop(context.scene, 'fMRI_dynamic_files', text="")
        if DataMakerPanel.subcortical_fmri_data_exist:
            col.prop(context.scene, 'add_fmri_subcorticals_data', text="add subcorticals")
            if bpy.context.scene.add_fmri_subcorticals_data:
                col.prop(context.scene, 'subcortical_fmri_files', text='')
        col.operator(AddfMRIDynamicsToBrain.bl_idname, text="Add fMRI data", icon='FCURVE')

    meg_sensors_positions_files = glob.glob(op.join(mu.get_user_fol(), 'meg', 'meg_*_sensors_positions.npz'))
    eeg_sensors_positions_file = op.join(mu.get_user_fol(), 'eeg', 'eeg_sensors_positions.npz')
    # todo: do something with eeg_data_minmax
    eeg_data_minmax_exist = len(glob.glob(op.join(mu.get_user_fol(), 'eeg', '*sensors_evoked_minmax.npy'))) > 0

    if len(meg_sensors_positions_files) > 0:
        col = layout.box().column()
        if bpy.data.objects.get('MEG_sensors', None) is None:
            col.operator(ImportMEGSensors.bl_idname, text="Import MEG sensors", icon='COLOR_GREEN')
        else:
            col.operator(ImportMEGSensors.bl_idname, text="Export MEG sensors", icon='LAMP_AREA')
            if _addon().meg.meg_sensors_exist():
                col.prop(context.scene, 'meg_sensors_files', text="")
                col.operator(AddDataToMEGSensors.bl_idname, text="Add data to MEG sensors", icon='FCURVE')

        if bpy.data.objects.get('meg_helmet'):
            col.operator(CreateMEGMesh.bl_idname, text="Export MEG mesh", icon='LAMP_AREA')
        else:
            col.operator(CreateMEGMesh.bl_idname, text="Import MEG mesh", icon='COLOR_GREEN')

    if op.isfile(eeg_sensors_positions_file):
        col = layout.box().column()
        if bpy.data.objects.get('EEG_sensors', None) is None:
            col.operator(ImportEEGSensors.bl_idname, text="Import EEG sensors", icon='COLOR_GREEN')
        else:
            col.operator(ImportEEGSensors.bl_idname, text="Export EEG sensors", icon='LAMP_AREA')
            if _addon().meg.eeg_sensors_exist():
                col.prop(context.scene, 'eeg_sensors_data_files', text="")
                col.operator(AddDataToEEGSensors.bl_idname, text="Add data to EEG", icon='FCURVE')
    
        # eeg_mesh_fname = op.join(mu.get_user_fol(), 'eeg', 'eeg_helmet.ply')
        # if op.isfile(eeg_mesh_fname):
        if bpy.data.objects.get('eeg_helmet'):
            col.operator(CreateEEGMesh.bl_idname, text="Export EEG mesh", icon='LAMP_AREA')
        else:
            col.operator(CreateEEGMesh.bl_idname, text="Import EEG mesh", icon='COLOR_GREEN')

    if DataMakerPanel.pycharm_fol != '':
        col.operator(Debug.bl_idname, text="Debug", icon='GHOST_ENABLED')


class Debug(bpy.types.Operator):
    bl_idname = "mmvt.debug"
    bl_label = "Debug"
    bl_description = 'Connects to a PyCharm debugger on localhost:1090'
    bl_options = {"UNDO"}

    def execute(self, context):
        fol = op.join(DataMakerPanel.pycharm_fol, 'debug-eggs')
        eggpath = op.join(fol, 'pydevd-pycharm.egg')
        if not op.exists(eggpath):
            eggpath = op.join(fol, 'pycharm-debug-py3k.egg')
        if not op.exists(eggpath):
            self.report({'ERROR'}, 'Unable to find debug egg at {}. Configure the addon properties '
                                   'in the User Preferences menu.'.format(eggpath))
            return {'CANCELLED'}

        if not any('pycharm-debug' in p for p in sys.path):
            print('Adding eggpath to the path: {}'.format(eggpath))
            sys.path.append(eggpath)

        import pydevd
        print('Waiting to connects to a PyCharm debugger on localhost:1090')
        pydevd.settrace('localhost', port=1090, stdoutToServer=True, stderrToServer=True)
        return {'FINISHED'}


class AddDataToEEGSensors(bpy.types.Operator):
    bl_idname = "mmvt.eeg_add_data"
    bl_label = "add data eeg"
    bl_description = 'Imports EEG Sensors objects\n\nScript: mmvt.data.add_data_to_eeg_sensors()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        add_data_to_eeg_sensors()
        return {"FINISHED"}


class AddDataToMEGSensors(bpy.types.Operator):
    bl_idname = "mmvt.meg_sensors_add_data"
    bl_label = "add meg sensors data"
    bl_description = 'Adds MEG sensors data.\n\nScript: mmvt.data.add_data_to_meg_sensors()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        add_data_to_meg_sensors()
        return {"FINISHED"}


class AddDataToElectrodes(bpy.types.Operator):
    bl_idname = "mmvt.electrodes_add_data"
    bl_label = "add_data2 electrodes"
    bl_description = 'Imports the electrode objects\n\nScript: mmvt.data.add_data_to_electrodes_and_parent()'
    bl_options = {"UNDO"}
    current_root_path = ''

    def invoke(self, context, event=None):
        add_data_to_electrodes_and_parent()
        return {"FINISHED"}


class StartFlatProcess(bpy.types.Operator):
    bl_idname = "mmvt.start_flat_process"
    bl_label = "deselect all"
    bl_description = 'Imports the flat brain.\n\nScript: mmvt.data.create_inflating_flat_morphing()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        create_inflating_flat_morphing()
        return {"FINISHED"}


class ChooseElectrodesPositionsFile(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "mmvt.load_electrodes_positions_file"
    bl_label = "Choose electrodes positions file (npz)"
    bl_description = 'Imports the electrode objects'

    filename_ext = '.npz'
    filter_glob = bpy.props.StringProperty(default='*.npz', options={'HIDDEN'}, maxlen=255)

    def execute(self, context):
        electrodes_fname = self.filepath
        user_fol = mu.get_user_fol()
        electrodes_fol = mu.get_fname_folder(electrodes_fname)
        if 'electrodes_positions' not in mu.namebase(electrodes_fname):
            new_fname = op.join(electrodes_fol, 'electrodes', '{}_electrodes_positions.npz'.format(mu.namebase(
                electrodes_fname).replace('electrodes', '').replace('__', '_')))
        else:
            new_fname = electrodes_fname
        if electrodes_fol != op.join(user_fol, 'electrodes'):
            shutil.copy(electrodes_fname, op.join(op.join(user_fol, 'electrodes', mu.namebase_with_ext(new_fname))))
        init_electrodes_positions_list()
        bpy.context.scene.electrodes_positions_files = mu.namebase(new_fname)
        return {'FINISHED'}


class DataMakerPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Import objects and data"
    addon = None
    init = False
    meg_evoked_files = []
    evoked_files = []
    externals = []
    eeg_data, eeg_meta = None, None
    meg_labels_data_exist = False
    subcortical_meg_data_exist = False
    subcortical_fmri_data_exist = False
    fMRI_dynamic_exist = False
    electrodes_data = None
    electrodes_meta_data = None
    electrodes_dists = None
    electrodes_names = None
    electrodes_conditions = None
    electrodes_positions_exist = False
    electrodes_data_exist = False
    meg_sensors_data = None
    meg_sensors_meta_data = None
    pycharm_fol = ''

    def draw(self, context):
        data_draw(self, context)

# def load_meg_evoked():
#     evoked_fol = op.join(mu.get_user_fol(), 'meg_evoked_files')
#     if op.isdir(evoked_fol):
#         DataMakerPanel.evoked_files = evoked_files = glob.glob(op.join(evoked_fol, '*_labels_data_rh.npz'))
#         basenames = [mu.namebase(fname).split('_')[0] for fname in evoked_files]
#         files_items = [(name, name, '', ind) for ind, name in enumerate(basenames)]
#         bpy.types.Scene.meg_evoked_files = bpy.props.EnumProperty(
#             items=files_items, description="meg_evoked_files", update=meg_evoked_files_update)


def init(addon):
    DataMakerPanel.addon = addon
    logging.basicConfig(filename='mmvt_addon.log', level=logging.DEBUG)
    bpy.context.scene.electrodes_radius = 0.15
    atlas = bpy.context.scene.atlas
    # load_meg_evoked()
    # _meg_evoked_files_update()
    labels_data_files = glob.glob(op.join(mu.get_user_fol(), 'meg', 'labels_data*_{}_*_rh.npz'.format(atlas)))
    if len(labels_data_files) > 0:
        DataMakerPanel.meg_labels_data_exist = True
        files_names = [mu.namebase(fname)[len('labels_data_'):-3] for fname in labels_data_files]
        items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
        bpy.types.Scene.meg_labels_data_files = bpy.props.EnumProperty(items=items,
            description='Selects the source estimated evoked response\n\nCurrent')
        bpy.context.scene.meg_labels_data_files = files_names[0]
    if op.isfile(op.join(mu.get_user_fol(), 'meg', 'subcortical_meg_activity.npz')):
        DataMakerPanel.subcortical_meg_data_exist = True
    subcortical_fmri_files = glob.glob(op.join(mu.get_user_fol(), 'fmri', 'subcorticals_*.npz'))
    if len(subcortical_fmri_files) > 0:
        DataMakerPanel.subcortical_fmri_data_exist = True
        files_names = [mu.namebase(fname) for fname in subcortical_fmri_files]
        items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
        bpy.types.Scene.subcortical_fmri_files = bpy.props.EnumProperty(items=items, description="subcortical fMRI files")

    # init_meg()
    # init_eeg()
    init_electrodes_positions_list()
    init_electrodes_data()
    if bpy.data.objects.get('Deep_electrodes'):
        bpy.context.scene.bipolar = np.all(['-' in o.name for o in bpy.data.objects['Deep_electrodes'].children])
    fMRI_labels_sources_files = glob.glob(
        op.join(mu.get_user_fol(), 'fmri', 'labels_data_{}_*_rh.npz'.format(bpy.context.scene.atlas)))
    if len(fMRI_labels_sources_files) > 0:
        DataMakerPanel.fMRI_dynamic_exist = True
        files_names = ['fMRI {}'.format(mu.namebase(fname)[len('labels_data_'):-len('_rh')].replace('_', ' '))
                       for fname in fMRI_labels_sources_files if atlas in mu.namebase(fname)]
        items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
        bpy.types.Scene.fMRI_dynamic_files = bpy.props.EnumProperty(
            items=items,description="fMRI_dynamic")
        bpy.context.scene.fMRI_dynamic_files = files_names[0]
    bpy.context.scene.add_meg_labels_data_overwrite = True
    # _addon().create_inflated_curv_coloring()
    pycharm_fol = mu.get_link_dir(mu.get_links_dir(), 'pycharm')
    if op.isdir(pycharm_fol):
        DataMakerPanel.pycharm_fol = pycharm_fol
    DataMakerPanel.init = True
    register()


def init_electrodes_positions_list():
    electrodes_positions_files = glob.glob(op.join(mu.get_user_fol(), 'electrodes', '*electrodes*positions*.npz'))
    if len(electrodes_positions_files) > 0:
        DataMakerPanel.electrodes_positions_exist = True
        files_names = [mu.namebase(fname) for fname in electrodes_positions_files]
        items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
        bpy.types.Scene.electrodes_positions_files = bpy.props.EnumProperty(
            items=items, description='Selects the electrodes position file.\n\nCurrent file')
        bpy.context.scene.electrodes_positions_files = files_names[0]


def init_electrodes_data():
    base_path = mu.get_user_fol()
    source_files = glob.glob(op.join(base_path, 'electrodes', 'electrodes{}_data*.npz'.format(
        '_bipolar' if bpy.context.scene.bipolar else '')))
    if len(source_files) > 0:
        # todo: show all the options
        DataMakerPanel.electrodes_meta_data = np.load(source_files[0])
        DataMakerPanel.electrodes_data = DataMakerPanel.electrodes_meta_data['data']
        DataMakerPanel.electrodes_data_exist = True
    else:
        source_file = op.join(base_path, 'electrodes', 'electrodes{}_data.npy'.format(
            '_bipolar' if bpy.context.scene.bipolar else ''))
        meta_file = op.join(base_path, 'electrodes', 'electrodes{}_meta_data.npz'.format(
            '_bipolar' if bpy.context.scene.bipolar else ''))
        if op.isfile(source_file) and op.isfile(meta_file):
            DataMakerPanel.electrodes_data = np.load(source_file)
            DataMakerPanel.electrodes_meta_data = np.load(meta_file)
            DataMakerPanel.electrodes_data_exist = True
    if DataMakerPanel.electrodes_meta_data is not None:
        DataMakerPanel.electrodes_names = DataMakerPanel.electrodes_meta_data['names']
        if isinstance(DataMakerPanel.electrodes_names[0], np.bytes_):
            DataMakerPanel.electrodes_names = np.array([n.decode('utf_8') for n in DataMakerPanel.electrodes_names])
        DataMakerPanel.electrodes_conditions = DataMakerPanel.electrodes_meta_data['conditions']
        if isinstance(DataMakerPanel.electrodes_conditions[0], np.bytes_):
            DataMakerPanel.electrodes_conditions = np.array(
                [c.decode('utf_8') for c in DataMakerPanel.electrodes_conditions])


# def init_eeg():
#     eeg_sensors_data_files = glob.glob(op.join(mu.get_user_fol(), 'eeg', '*sensors_evoked_data*.npy'))
#     if len(eeg_sensors_data_files) > 0:
#         files_names = [mu.namebase(fname) for fname in eeg_sensors_data_files]
#         items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
#         bpy.types.Scene.eeg_sensors_data_files = bpy.props.EnumProperty(
#             items=items, update=eeg_sensors_data_files_update,
#             description='Selects the EEG sensors data file.\n\nCurrent file')
#         bpy.context.scene.eeg_sensors_data_files = files_names[0]
#
#
# def init_meg():
#     meg_data_files = glob.glob(op.join(mu.get_user_fol(), 'meg', '*sensors_evoked_data*.npy'))
#     if len(meg_data_files) > 0:
#         files_names = [mu.namebase(fname) for fname in meg_data_files]
#         items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
#         bpy.types.Scene.meg_sensors_data_files = bpy.props.EnumProperty(
#             items=items, update=meg_sensors_data_files_update,
#             description='Selects the MEG sensors data file.\n\nCurrent file')
#         bpy.context.scene.meg_sensors_data_files = files_names[0]


def register():
    try:
        unregister()
        bpy.utils.register_class(UpdateMMVT)
        bpy.utils.register_class(StartFlatProcess)
        bpy.utils.register_class(DataMakerPanel)
        bpy.utils.register_class(AddDataToElectrodes)
        # bpy.utils.register_class(AddDataNoCondsToBrain)
        bpy.utils.register_class(AddDataToBrain)
        bpy.utils.register_class(AddfMRIDynamicsToBrain)
        bpy.utils.register_class(AddDataToEEGSensors)
        bpy.utils.register_class(AddDataToMEGSensors)
        bpy.utils.register_class(ImportMEGSensors)
        bpy.utils.register_class(ImportElectrodes)
        bpy.utils.register_class(ImportEEGSensors)
        bpy.utils.register_class(ImportRois)
        bpy.utils.register_class(ImportBrain)
        bpy.utils.register_class(CreateEEGMesh)
        bpy.utils.register_class(CreateMEGMesh)
        bpy.utils.register_class(AnatomyPreproc)
        bpy.utils.register_class(ChooseElectrodesPositionsFile)
        bpy.utils.register_class(Debug)
        # bpy.utils.register_class(FixBrainMaterials)
        # bpy.utils.register_class(AddOtherSubjectMEGEvokedResponse)
        # bpy.utils.register_class(SelectExternalMEGEvoked)
        # print('Data Panel was registered!')
    except:
        import traceback
        print("Can't register Data Panel!")
        print(traceback.format_exc())


def unregister():
    try:
        bpy.utils.unregister_class(UpdateMMVT)
        bpy.utils.unregister_class(StartFlatProcess)
        bpy.utils.unregister_class(DataMakerPanel)
        bpy.utils.unregister_class(AddDataToElectrodes)
        # bpy.utils.unregister_class(AddDataNoCondsToBrain)
        bpy.utils.unregister_class(AddDataToBrain)
        bpy.utils.unregister_class(AddfMRIDynamicsToBrain)
        bpy.utils.unregister_class(AddDataToEEGSensors)
        bpy.utils.unregister_class(AddDataToMEGSensors)
        bpy.utils.unregister_class(ImportMEGSensors)
        bpy.utils.unregister_class(ImportElectrodes)
        bpy.utils.unregister_class(ImportRois)
        bpy.utils.unregister_class(ImportEEGSensors)
        bpy.utils.unregister_class(CreateMEGMesh)
        bpy.utils.unregister_class(ImportBrain)
        bpy.utils.unregister_class(CreateEEGMesh)
        bpy.utils.unregister_class(AnatomyPreproc)
        bpy.utils.unregister_class(ChooseElectrodesPositionsFile)
        bpy.utils.unregister_class(Debug)
        # bpy.utils.unregister_class(FixBrainMaterials)
        # bpy.utils.unregister_class(AddOtherSubjectMEGEvokedResponse)
        # bpy.utils.unregister_class(SelectExternalMEGEvoked)
    except:
        pass


