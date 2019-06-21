import bpy
import os.path as op
import glob
import numpy as np
from collections import defaultdict
import importlib

import mmvt_utils as mu
import coloring_panel

try:
    import mne
    MNE_EXIST = True
except:
    MNE_EXIST = False


plot_stc = coloring_panel.plot_stc


PARENT_OBJ_NAME = 'meg_clusters'


def _addon():
    return MEGPanel.addon


# def eeg_sensors_data_files_update(self, context):
#     load_eeg_sensors_data()
#
#
# def load_eeg_sensors_data(data_fname='', meta_fname=''):
#     if data_fname == '':
#         data_fname = op.join(mu.get_user_fol(), 'eeg', '{}.npy'.format(bpy.context.scene.eeg_sensors_data_files))
#     if meta_fname == '':
#         meta_fname = op.join(mu.get_user_fol(), 'eeg', '{}.npz'.format(
#             bpy.context.scene.eeg_sensors_data_files.replace('data', 'data_meta')))
#     print('EEG sensros data files were loaded:\n{}\n{}'.format(data_fname, meta_fname))
#     data = np.load(data_fname, mmap_mode='r')
#     meta = np.load(meta_fname)
#     return data, meta


# def meg_sensors_data_files_update(self, context):
#     load_meg_sensors_data()
#
#
# def load_meg_sensors_data(data_fname='', meta_fname=''):
#     if data_fname == '':
#         data_fname = op.join(mu.get_user_fol(), 'meg', '{}.npy'.format(bpy.context.scene.meg_sensors_data_files))
#     if meta_fname == '':
#         meta_fname = op.join(mu.get_user_fol(), 'meg', '{}.npz'.format(
#             bpy.context.scene.meg_sensors_data_files.replace('data', 'data_meta')))
#     print('MEG sensros data files were loaded:\n{}\n{}'.format(data_fname, meta_fname))
#     data = np.load(data_fname, mmap_mode='r')
#     meta = np.load(meta_fname)
#     DataMakerPanel.meg_sensors_data, DataMakerPanel.meg_sensors_meta_data = data, meta

########## getters & setters

def get_meg_sensors_data():
    meg_sensors_data_fname, meg_sensors_meta_data_fname, meg_sensors_data_minmax_fname = get_meg_sensors_files_names()
    meg_sensors_file_name = get_meg_sensors_file()
    # meg_sensors_data = MEGPanel.meg_sensors_data.get(meg_sensors_file_name, None)
    # meg_sensors_meta_data = MEGPanel.meg_sensors_meta_data.get(meg_sensors_file_name, None)
    meg_sensors_data, meg_sensors_meta_data = None, None
    if meg_sensors_data is None:
        meg_sensors_data = np.load(meg_sensors_data_fname)
    if meg_sensors_meta_data is None:
        meta = mu.Bag(np.load(meg_sensors_meta_data_fname))
        meta['names'] = [n.replace(' ', '') for n in meta['names']] # ugly patch
        meg_sensors_meta_data = meta
    return meg_sensors_data, meg_sensors_meta_data
    # return MEGPanel.meg_sensors_data[meg_sensors_file_name], MEGPanel.meg_sensors_meta_data[meg_sensors_file_name]


def get_eeg_sensors_data():
    eeg_sensors_data_fname, eeg_sensors_meta_data_fname, eeg_sensors_data_minmax_fname = get_eeg_sensors_files_names()
    # eeg_sensors_file_name = get_eeg_sensors_file()
    # eeg_sensors_data = MEGPanel.eeg_sensors_data.get(eeg_sensors_file_name, None)
    # eeg_sensors_meta_data = MEGPanel.eeg_sensors_meta_data.get(eeg_sensors_file_name, None)
    # if eeg_sensors_data is None:
    #     MEGPanel.eeg_sensors_data[eeg_sensors_file_name] = np.load(eeg_sensors_data_fname)
    eeg_sensors_data = np.load(eeg_sensors_data_fname)
    # if eeg_sensors_meta_data is None:
    meta = mu.Bag(np.load(eeg_sensors_meta_data_fname))
    meta['names'] = [n.replace(' ', '') for n in meta['names']] # ugly patch
    # MEGPanel.eeg_sensors_meta_data[eeg_sensors_file_name] = meta
    return eeg_sensors_data, meta
    # return MEGPanel.eeg_sensors_data[eeg_sensors_file_name], MEGPanel.eeg_sensors_meta_data[eeg_sensors_file_name]


def get_meg_sensors_file():
    return bpy.context.scene.meg_sensors_files


def set_meg_sensors_file(val):
    bpy.context.scene.meg_sensors_files = val


def get_eeg_sensors_file():
    return bpy.context.scene.eeg_sensors_files


def set_eeg_sensors_file(val):
    bpy.context.scene.eeg_sensors_files = val


# def set_meg_sensors_types(val):
#     bpy.context.scene.meg_sensors_types = val
#
#
# def get_meg_sensors_types():
#     return bpy.context.scene.meg_sensors_types


def set_meg_sensors_conditions(val):
    bpy.context.scene.meg_sensors_conditions = val


def get_meg_sensors_conditions():
    return bpy.context.scene.meg_sensors_conditions


def eeg_sensors_exist():
    return MEGPanel.eeg_sensors_exist


def meg_sensors_exist():
    return MEGPanel.meg_sensors_exist

##################
def init_meg_sensors():
    user_fol = mu.get_user_fol()

    if bpy.data.objects.get('MEG_sensors') is not None and len(MEGPanel.meg_sensors_types) > 0:
        items = [(sensor_type, sensor_type, '', sensor_key) for sensor_type, sensor_key in
                 MEGPanel.meg_sensors_types.items()]
        bpy.types.Scene.meg_sensors_types = bpy.props.EnumProperty(
            items=items, description='Selects the MEG sensors type.', update=meg_sensors_types_update)
        bpy.context.scene.meg_sensors_types = [t for t,t,_,k in items if k == 0][0]

    # meg_data_files = sorted([mu.namebase(f) for f in glob.glob(op.join(
    #     user_fol, 'meg', 'meg_*_mag_sensors_evoked_data*.npy')) if 'minmax' not in mu.namebase(f)])
    meg_data_files = sorted([mu.namebase(f) for f in glob.glob(op.join(
        user_fol, 'meg', 'meg_*_sensors_evoked_data*.npy')) if 'minmax' not in mu.namebase(f)])
    if len(meg_data_files) == 0:
        return False
    items = []
    for ind, meg_data_file in enumerate(meg_data_files):
        # item_name = meg_data_file[len('meg_'):meg_data_file.index('mag_sensors_evoked') - 1]
        item_name = meg_data_file[len('meg_'):meg_data_file.index('sensors_evoked') - 1]
        items.append((item_name, item_name, '', ind + 1))
    # items = [(f, f, '', ind + 1) for ind, f in enumerate(meg_data_files)]
    bpy.types.Scene.meg_sensors_files = bpy.props.EnumProperty(
        items=items, description='Selects the MEG sensors evoked activity file.', update=meg_sensors_files_update)
    bpy.context.scene.meg_sensors_files = items[0][0]

    meg_helmet = bpy.data.objects.get('meg_helmet')
    if meg_helmet is not None and bpy.data.objects.get('MEG_sensors'):
        MEGPanel.meg_vertices_sensors = {}
        meg_vertices_sensors = mu.load(op.join(mu.get_user_fol(), 'meg', 'meg_vertices_sensors.pkl'))
        for sensor_type in MEGPanel.meg_sensors_types.keys():
            MEGPanel.meg_vertices_sensors[sensor_type] = meg_vertices_sensors[sensor_type]
    #     from scipy.spatial.distance import cdist
    #     # meg_sensors_loc = np.array(
    #     #     [meg_obj.matrix_world.to_translation() * 10 for meg_obj in bpy.data.objects['MEG_sensors'].children])
    #     meg_helmet_vets_loc = np.array([v.co for v in meg_helmet.data.vertices])
    #     for sensor_type, sensor_key in MEGPanel.meg_sensors_types.items():
    #         meg_sensors_loc = np.array(
    #             [meg_obj.location * 10 if meg_obj.name.endswith(str(sensor_key)) else (np.inf,np.inf, np.inf)
    #              for meg_obj in bpy.data.objects['MEG_sensors'].children])
    #         if np.all(meg_sensors_loc == np.inf):
    #             print('Couldn\'t find {} sensors!'.format(sensor_type))
    #         MEGPanel.meg_helmet_indices[sensor_type] = np.argmin(cdist(meg_helmet_vets_loc, meg_sensors_loc), axis=1)
    # elif bpy.data.objects.get('MEG_sensors'):
    #     for sensor_type, sensor_key in MEGPanel.meg_sensors_types.items():
    #         MEGPanel.meg_helmet_indices[sensor_type] = np.array(
    #             [ind for ind, meg_obj in enumerate(bpy.data.objects['MEG_sensors'].children)
    #              if meg_obj.name.endswith(str(sensor_key))])
    return True


def meg_sensors_types_update(self, context):
    if bpy.data.objects.get('MEG_sensors') is None:
        return
    for meg_sensors_type_obj in bpy.data.objects['MEG_sensors'].children:
        do_show = bpy.context.scene.meg_sensors_types in meg_sensors_type_obj.name
        # do_show = meg_sensor_obj.name.endswith(
        #     str(MEGPanel.meg_sensors_types[bpy.context.scene.meg_sensors_types]))
        mu.show_hide_hierarchy(do_show, meg_sensors_type_obj, also_parent=True, select=False)


def get_meg_sensors_types():
    return MEGPanel.meg_sensors_types


def get_meg_sensors_files_names():
    user_fol = mu.get_user_fol()
    # name = 'meg_{}_{}_sensors_evoked'.format(bpy.context.scene.meg_sensors_files, bpy.context.scene.meg_sensors_types)
    name = 'meg_{}_sensors_evoked'.format(bpy.context.scene.meg_sensors_files)
    meg_sensors_data_fname = op.join(user_fol, 'meg', '{}_data.npy'.format(name))
    meg_sensors_meta_data_fname = op.join(user_fol, 'meg', '{}_data_meta.npz'.format(name))
    meg_sensors_data_minmax_fname = op.join(user_fol, 'meg', '{}_minmax.npy'.format(name))
    return meg_sensors_data_fname, meg_sensors_meta_data_fname, meg_sensors_data_minmax_fname


def meg_sensors_files_update(self, context):
    meg_sensors_data_fname, meg_sensors_meta_data_fname, meg_sensors_data_minmax_fname = get_meg_sensors_files_names()
    if all([op.isfile(f) for f in [
            meg_sensors_data_fname, meg_sensors_meta_data_fname]]) and \
            bpy.data.objects.get('MEG_sensors') is not None:
        MEGPanel.meg_sensors_exist = True
        # ColoringMakerPanel.meg_sensors_data, ColoringMakerPanel.meg_sensors_meta, = \
        #     _addon().load_meg_sensors_data(meg_sensors_data_fname, meg_sensors_meta_data_fname)
        # data_min, data_max = np.load(meg_sensors_data_minmax_fname)
        # MEGPanel.meg_sensors_colors_ratio = 256 / (data_max - data_min)
        # MEGPanel.meg_sensors_data_minmax = (data_min, data_max)
        meg_sensors_meta_data = np.load(meg_sensors_meta_data_fname)
        if meg_sensors_meta_data is not None:
            items = [(c, c, '', ind + 1) for ind, c in enumerate(meg_sensors_meta_data['conditions'])]
            if len(items) == 2:
                items.append(('diff', 'Conditions difference', '', len(meg_sensors_meta_data['conditions']) +1))
        else:
            items = []
        MEGPanel.meg_sensors_conditions_items = items
        bpy.types.Scene.meg_sensors_conditions = bpy.props.EnumProperty(items=items,
            description='Selects the condition to plot the MEG sensors activity.\n\nCurrent condition')
        if len(items) > 0:
            bpy.context.scene.meg_sensors_conditions = items[0][0]
        _addon().coloring.add_activity_type('meg_sensors')


def get_eeg_sensors_files_names():
    user_fol = mu.get_user_fol()
    name = 'eeg_{}_sensors_evoked'.format(bpy.context.scene.eeg_sensors_files)
    eeg_sensors_data_fname = op.join(user_fol, 'eeg', '{}_data.npy'.format(name))
    eeg_sensors_meta_data_fname = op.join(user_fol, 'eeg', '{}_data_meta.npz'.format(name))
    eeg_sensors_data_minmax_fname = op.join(user_fol, 'eeg', '{}_minmax.npy'.format(name))
    # print('eeg sensors data: {}'.format(eeg_sensors_data_fname))
    return eeg_sensors_data_fname, eeg_sensors_meta_data_fname, eeg_sensors_data_minmax_fname


def init_eeg_sensors():
    user_fol = mu.get_user_fol()

    eeg_data_files = sorted([mu.namebase(f) for f in glob.glob(op.join(
        user_fol, 'eeg', 'eeg_*sensors_evoked_data*.npy')) if 'minmax' not in mu.namebase(f)])
    if len(eeg_data_files) == 0:
        return False
    items = []
    for ind, eeg_data_file in enumerate(eeg_data_files):
        item_name = eeg_data_file[len('eeg_'):eeg_data_file.index('sensors_evoked') - 1]
        if item_name == '':
            item_name = 'eeg_sensors'
        items.append((item_name, item_name, '', ind + 1))
    bpy.types.Scene.eeg_sensors_files = bpy.props.EnumProperty(
        items=items, description='Selects the EEG sensors evoked activity file.', update=eeg_sensors_files_update)
    bpy.context.scene.eeg_sensors_files = items[0][0]

    # eeg_helmet = bpy.data.objects.get('eeg_helmet')
    # if eeg_helmet is not None and bpy.data.objects.get('EEG_sensors'):
    #     MEGPanel.eeg_vertices_sensors = mu.load(op.join(mu.get_user_fol(), 'eeg', 'eeg_vertices_sensors.pkl'))


    # eeg_data_files = sorted([f for f in glob.glob(op.join(user_fol, 'eeg', '*sensors_evoked_data*.npy'))
    #                          if 'minmax' not in mu.namebase(f)])
    # if len(eeg_data_files) == 0:
    #     return False
    # items = [(mu.namebase(f), mu.namebase(f), '', ind + 1) for ind, f in enumerate(eeg_data_files)]
    # bpy.types.Scene.eeg_sensors_files = bpy.props.EnumProperty(
    #     items=items, description='Selects the EEG sensors evoked activity file.', update=eeg_sensors_files_update)
    # bpy.context.scene.eeg_sensors_files = mu.namebase(eeg_data_files[0])

    # eeg_helmet = bpy.data.objects.get('eeg_helmet')
    # if eeg_helmet is not None:
    #     from scipy.spatial.distance import cdist
    #     # eeg_sensors_loc = np.array(
    #     #     [eeg_obj.matrix_world.to_translation() * 10 for eeg_obj in bpy.data.objects['EEG_sensors'].children])
    #     eeg_sensors_loc = np.array(
    #         [eeg_obj.location * 10 for eeg_obj in bpy.data.objects['EEG_sensors'].children])
    #     eeg_helmet_vets_loc = np.array([v.co for v in eeg_helmet.data.vertices])
    #     MEGPanel.eeg_helmet_indices = np.argmin(cdist(eeg_helmet_vets_loc, eeg_sensors_loc), axis=1)
    return True


def eeg_sensors_files_update(self, context):
    eeg_sensors_data_fname, eeg_sensors_meta_data_fname, eeg_sensors_data_minmax_fname= get_eeg_sensors_files_names()
    if all([op.isfile(f) for f in [
            eeg_sensors_data_fname, eeg_sensors_meta_data_fname]]) and \
            bpy.data.objects.get('EEG_sensors') is not None:
        # data_min, data_max = np.load(eeg_sensors_data_minmax_fname)
        # MEGPanel.eeg_sensors_colors_ratio = 256 / (data_max - data_min)
        # MEGPanel.eeg_sensors_data_minmax = (data_min, data_max)
        eeg_sensors_meta_data = np.load(eeg_sensors_meta_data_fname)
        if eeg_sensors_meta_data is not None:
            items = [(c, c, '', ind + 1) for ind, c in enumerate(eeg_sensors_meta_data['conditions'])]
            if len(items) == 2:
                items.append(('diff', 'Conditions difference', '', len(eeg_sensors_meta_data['conditions']) +1))
        else:
            items = []
        MEGPanel.eeg_sensors_conditions_items = items
        bpy.types.Scene.eeg_sensors_conditions = bpy.props.EnumProperty(items=items,
            description='Selects the condition to plot the EEG sensors activity.\n\nCurrent condition')
        if len(items) > 0:
            bpy.context.scene.eeg_sensors_conditions = items[0][0]
        _addon().coloring.add_activity_type('eeg_sensors')


    # eeg_data_file_name = mu.namebase(eeg_data_files[0])
    # eeg_sensors_data_fname = op.join(user_fol, 'eeg', '{}.npy'.format(eeg_data_file_name))
    # eeg_sensors_meta_data_fname = op.join(user_fol, 'eeg', '{}_meta.npz'.format(eeg_data_file_name))
    # eeg_sensors_data_minmax_fname = op.join(user_fol, 'eeg', '{}_minmax.npy'.format(eeg_data_file_name[:-5]))
    # if all([op.isfile(f) for f in
    #         [eeg_sensors_data_fname, eeg_sensors_meta_data_fname, eeg_sensors_data_minmax_fname]]) and \
    #         bpy.data.objects.get('EEG_sensors', None) is  not None:
    #     MEGPanel.eeg_sensors_exist = True
    #     MEGPanel.eeg_sensors_data, MEGPanel.eeg_sensors_meta, = \
    #         load_eeg_sensors_data(eeg_sensors_data_fname, eeg_sensors_meta_data_fname)
    #     data_min, data_max = np.load(eeg_sensors_data_minmax_fname)
    #     MEGPanel.eeg_sensors_colors_ratio = 256 / (data_max - data_min)
    #     MEGPanel.eeg_sensors_data_minmax = (data_min, data_max)
    #     items = [(c, c, '', ind + 1) for ind, c in enumerate(MEGPanel.eeg_sensors_meta['conditions'])]
    #     items.append(('diff', 'Conditions difference', '', len(MEGPanel.eeg_sensors_meta['conditions']) +1))
    #     bpy.types.Scene.eeg_sensors_conditions = bpy.props.EnumProperty(items=items,
    #         description='Selects the condition to plot the EEG sensors activity.\n\nCurrent condition')
    #     bpy.context.scene.eeg_sensors_conditions = 'diff'
    #     _addon.coloring.add_activity_type('eeg_sensors')



# ************** Coloring function
def color_eeg_helmet(use_abs=None, threshold=None):
    if threshold is None:
        threshold = bpy.context.scene.coloring_lower_threshold
    if use_abs is None:
        use_abs = bpy.context.scene.coloring_use_abs
    fol = mu.get_user_fol()
    data, meta = get_eeg_sensors_data()
    # indices = meta.picks - np.min(meta.picks)
    # data = data[indices]
    # names = np.array(meta.names)[indices]

    if data.ndim == 2:
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('EEG sensors')
    elif bpy.context.scene.eeg_sensors_conditions != 'diff':
        cond_ind = np.where(meta['conditions'] == bpy.context.scene.eeg_sensors_conditions)[0][0]
        data = data[:, :, cond_ind]
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('EEG sensors {} condition'.format(meta['conditions'][cond_ind]))
    else:
        data = np.diff(data, axis=2).squeeze()
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('EEG sensors conditions difference')
    lookup = np.load(op.join(fol, 'eeg', 'eeg_faces_verts.npy'))
    threshold = 0
    if _addon().colorbar_values_are_locked():
        data_max, data_min = _addon().get_colorbar_max_min()
    else:
        data_max, data_min = mu.get_data_max_min(data, True, (1, 99))
        _addon().set_colorbar_max_min(data_max, data_min, True)
    colors_ratio = 256 / (data_max - data_min)

    if bpy.context.scene.find_max_eeg_sensors:
        _, bpy.context.scene.frame_current = mu.argmax2d(data)
    data_t = data[:, bpy.context.scene.frame_current]

    eeg_helmet = bpy.data.objects['eeg_helmet']
    indices = meta.channels_sensors_dict
    helmet_data = np.zeros(len(eeg_helmet.data.vertices))
    helmet_data[indices] = data_t

    _addon().coloring.activity_map_obj_coloring(
        eeg_helmet, data_t, lookup, threshold, True, data_min=data_min,
        colors_ratio=colors_ratio, bigger_or_equall=False, use_abs=use_abs)


def color_meg_helmet(use_abs=None, threshold=None):
    if threshold is None:
        threshold = bpy.context.scene.coloring_lower_threshold
    if use_abs is None:
        use_abs = bpy.context.scene.coloring_use_abs
    fol = mu.get_user_fol()
    data, meta = get_meg_sensors_data()
    indices = meta.picks.item()[bpy.context.scene.meg_sensors_types]
    data = data[indices]

    if data.ndim == 2:
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('MEG sensors')
    elif bpy.context.scene.meg_sensors_conditions != 'diff':
        cond_ind = np.where(meta['conditions'] == bpy.context.scene.meg_sensors_conditions)[0][0]
        data = data[:, :, cond_ind]
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('MEG sensors {} condition'.format(meta['conditions'][cond_ind]))
    else:
        C = data.shape[2]
        data = data.squeeze() if C == 1 else np.diff(data, axis=2).squeeze() if C == 2 else \
            np.mean(data, axis=2).squeeze()
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('MEG sensors conditions difference')
    lookup = np.load(op.join(fol, 'meg', 'meg_faces_verts.npy'))
    if _addon().colorbar_values_are_locked():
        data_max, data_min = _addon().get_colorbar_max_min()
    else:
        data_max, data_min = mu.get_data_max_min(data, True, (1, 99))
        _addon().set_colorbar_max_min(data_max, data_min, True)
    colors_ratio = 256 / (data_max - data_min)

    if bpy.context.scene.find_max_meg_sensors:
        _, bpy.context.scene.frame_current = mu.argmax2d(data)
    data_t = data[:, bpy.context.scene.frame_current]

    meg_helmet = bpy.data.objects['meg_helmet']
    indices = meta.channels_sensors_dict.item()[bpy.context.scene.meg_sensors_types]
    helmet_data = np.zeros(len(meg_helmet.data.vertices))
    helmet_data[indices] = data_t

    _addon().coloring.activity_map_obj_coloring(
        meg_helmet, data_t, lookup, threshold, True, data_min=data_min,
        colors_ratio=colors_ratio, bigger_or_equall=False, use_abs=use_abs)


def color_meg_sensors(threshold=None):
    _addon().show_hide_meg_sensors()
    _addon().coloring.add_to_what_is_colored(_addon().coloring.WIC_MEG_SENSORS)
    if threshold is None:
        threshold = _addon().coloring.get_lower_threshold()
    # threshold = bpy.context.scene.coloring_lower_threshold
    data, meta = get_meg_sensors_data()
    # sensors_dict = mu.Bag(np.load(
    #     op.join(mu.get_user_fol(), 'meg', 'meg_{}_sensors_positions.npz'.format(bpy.context.scene.meg_sensors_types))))
    # inds = np.unique(MEGPanel.meg_helmet_indices[bpy.context.scene.meg_sensors_types])
    indices = meta.picks.item()[bpy.context.scene.meg_sensors_types]
    data = data[indices, :, :] if data.ndim == 3 else data[indices, :]
    # names = np.array(meta.names)[indices]

    if data.ndim == 2:
        _addon().set_colorbar_title('MEG sensors')
    elif bpy.context.scene.meg_sensors_conditions != 'diff':
        cond_ind = np.where(meta['conditions'] == bpy.context.scene.meg_sensors_conditions)[0][0]
        data = data[:, :, cond_ind]
        _addon().set_colorbar_title('MEG sensors {} condition'.format(meta['conditions'][cond_ind]))
    else:
        C = data.shape[2]
        data = data.squeeze() if C == 1 else np.diff(data, axis=2).squeeze() if C == 2 else \
            np.mean(data, axis=2).squeeze()
        _addon().set_colorbar_title('MEG sensors conditions difference')

    if _addon().colorbar_values_are_locked():
        data_max, data_min = _addon().get_colorbar_max_min()
    else:
        # data_min_org, data_max_org = ColoringMakerPanel.meg_sensors_data_minmax
        data_max, data_min = mu.get_data_max_min(data, True, (1, 99))
        _addon().set_colorbar_max_min(data_max, data_min)
    colors_ratio = 256 / (data_max - data_min)

    if bpy.context.scene.find_max_meg_sensors:
        _, bpy.context.scene.frame_current = mu.argmax2d(data)

    meg_sensors_obj = bpy.data.objects['MEG_{}_sensors'.format(bpy.context.scene.meg_sensors_types)]
    names = [o.name for o in meg_sensors_obj.children]
    indices = meta.channels_sensors_dict.item()[bpy.context.scene.meg_sensors_types]
    sensors_data = np.zeros((len(names), data.shape[1]))
    sensors_data[indices] = data

    # names = np.array([obj.name for obj in bpy.data.objects['MEG_sensors'].children])[inds]
    if threshold > data_max:
        print('threshold is bigger than data_max ({})! Setting to 0.'.format(data_max))
        threshold = 0
    _addon().coloring.color_objects_homogeneously(sensors_data, names, meta['conditions'], data_min, colors_ratio, threshold)

    if not bpy.data.objects.get('meg_helmet', None) is None:
        color_meg_helmet()


def color_eeg_sensors(threshold=None):
    _addon().show_hide_eeg_sensors()
    _addon().coloring.add_to_what_is_colored(_addon().coloring.WIC_EEG)
    if threshold is None:
        threshold = bpy.context.scene.coloring_lower_threshold
    data, meta = get_eeg_sensors_data()
    # indices = meta.picks - np.min(meta.picks)
    # data = data[indices]
    # names = np.array(meta.names)[indices]

    if data.ndim == 2:
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('EEG sensors')
    elif bpy.context.scene.eeg_sensors_conditions != 'diff':
        cond_ind = np.where(meta['conditions'] == bpy.context.scene.eeg_sensors_conditions)[0][0]
        data = data[:, :, cond_ind]
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('EEG sensors {} condition'.format(meta['conditions'][cond_ind]))
    else:
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('EEG sensors conditions difference')

    if _addon().colorbar_values_are_locked():
        data_max, data_min = _addon().get_colorbar_max_min()
    else:
        # data_min, data_max = ColoringMakerPanel.eeg_sensors_data_minmax
        data_max, data_min = mu.get_data_max_min(data, True, (1, 99))
        _addon().set_colorbar_max_min(data_max, data_min)
    colors_ratio = 256 / (data_max - data_min)
    if threshold >= data_max:
        print('Threshold is bigger than data_max ({}), setting to 0.'.format(data_max))
        threshold = 0

    if bpy.context.scene.find_max_eeg_sensors:
        _, bpy.context.scene.frame_current = mu.argmax2d(data)

    eeg_sensors_obj = bpy.data.objects['EEG_sensors']
    names = [o.name for o in eeg_sensors_obj.children]
    indices = meta.channels_sensors_dict
    sensors_data = np.zeros((len(names), data.shape[1]))
    sensors_data[indices] = data

    _addon().coloring.color_objects_homogeneously(
        sensors_data, names, meta['conditions'], data_min, colors_ratio, threshold)

    if not bpy.data.objects.get('eeg_helmet', None) is None:
        color_eeg_helmet()


# *************** Coloring classes

class ColorMEGSensors(bpy.types.Operator):
    bl_idname = "mmvt.color_meg_sensors"
    bl_label = "mmvt color_meg_sensors"
    bl_description = 'Plots the MEG sensors activity according the selected condition.\n\nScript: mmvt.coloring.color_meg_sensors()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        color_meg_sensors()
        return {"FINISHED"}


class ColorEEGSensors(bpy.types.Operator):
    bl_idname = "mmvt.color_eeg_sensors"
    bl_label = "mmvt color_eeg_sensors"
    bl_description = 'Plots the EEG sensors activity according the selected condition.\n\nScript: mmvt.coloring.color_eeg_sensors()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        color_eeg_sensors()
        return {"FINISHED"}


class ColorEEGHelmet(bpy.types.Operator):
    bl_idname = "mmvt.eeg_helmet"
    bl_label = "mmvt eeg helmet"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        color_eeg_helmet()
        return {"FINISHED"}


class ColorMEGHelmet(bpy.types.Operator):
    bl_idname = "mmvt.meg_helmet"
    bl_label = "mmvt meg helmet"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        color_meg_helmet()
        return {"FINISHED"}

# ***************************8

def clusters_update(self, context):
    if MEGPanel.addon is not None and MEGPanel.init:
        _clusters_update()


def get_cluster_name(cluster):
    return 'cluster_size_{}_max_{:.2f}_{}'.format(cluster.size, cluster.max, cluster.name)


def get_cluster_fcurve_name(cluster):
    return '{}_{}_{:.2f}'.format(cluster.name, cluster.size, cluster.max)


def get_cluster_verts_co(cluster):
    inflated_mesh = 'inflated_{}'.format(cluster.hemi)
    me = bpy.data.objects[inflated_mesh].to_mesh(bpy.context.scene, True, 'PREVIEW')
    vertex_cos = np.zeros((len(cluster.vertices), 3))
    for vert_ind, vert in enumerate(cluster.vertices):
        vertex_cos[vert_ind] = tuple(me.vertices[vert].co)
    bpy.data.meshes.remove(me)
    return vertex_cos


def change_cursor_on_selection():
    # Add a checkbox
    return False


def _clusters_update():
    MEGPanel.current_cluster = cluster = MEGPanel.clusters_lookup[bpy.context.scene.meg_clusters]
    # set_cluster_time_series(cluster)
    cluster_name = get_cluster_name(cluster)
    cluster_max_vert_co = mu.get_vert_co(cluster.max_vert, cluster.hemi)
    bpy.context.scene.cursor_location = cluster_max_vert_co
    _addon().set_cursor_pos()
    _addon().set_closest_vertex_and_mesh_to_cursor(cluster.max_vert, 'inflated_{}'.format(cluster.hemi))
    _addon().save_cursor_position()
    _addon().create_slices()
    if bpy.context.scene.plot_current_meg_cluster:
        # _addon().color_contours(
        #     [cluster_name], cluster.hemi, MEGPanel.contours, bpy.context.scene.cumulate_meg_cluster, False)
        _addon().color_contours(
            [], 'both', MEGPanel.contours, bpy.context.scene.cumulate_meg_cluster, False)
    bpy.data.objects[PARENT_OBJ_NAME].select = True
    # mu.view_all_in_graph_editor()
    fcurves = mu.get_fcurves(PARENT_OBJ_NAME)
    cluster_fcurve_name = get_cluster_fcurve_name(cluster)
    if bpy.context.scene.cumulate_meg_cluster:
        fcurve_ind = [mu.get_fcurve_name(f) for f in fcurves].index(cluster_fcurve_name)
        fcurves[fcurve_ind].hide = False
    else:
        for fcurve in fcurves:
            fcurve_name = mu.get_fcurve_name(fcurve)
            fcurve.hide = fcurve_name != cluster_fcurve_name

    MEGPanel.prev_cluster = bpy.context.scene.meg_clusters


def plot_all_clusters():
    for hemi in mu.INF_HEMIS:
        # Not sure why, but this is needed, otherwise the coloring layer is being erased
        _addon().recreate_coloring_layers(bpy.data.objects[hemi].data, 'contours')
    for cluster in MEGPanel.clusters_labels_filtered:
        _addon().color_contours([get_cluster_name(cluster)], cluster.hemi, MEGPanel.contours, True, False)


def get_selected_clusters_data():
    names = []
    data = None
    fcurves = mu.get_fcurves(PARENT_OBJ_NAME)
    filtered_fcurves_names = [get_cluster_fcurve_name(c) for c in MEGPanel.clusters_labels_filtered]
    filtered_clusters = {fcurve_name:cluster for fcurve_name,cluster in zip(
        filtered_fcurves_names, MEGPanel.clusters_labels_filtered)}
    data_ind = 0
    for fcurve in fcurves:
        fcurve_name = mu.get_fcurve_name(fcurve)
        if fcurve_name in filtered_fcurves_names:
            x = filtered_clusters[fcurve_name].label_data
            if data is None:
                data = np.zeros((len(filtered_fcurves_names), len(x)))
            data[data_ind] = x
            names.append(fcurve_name)
            data_ind += 1
    return data, names, ['all']


# def clear_cluster(cluster):
#     if isinstance(cluster, str):
#         cluster = MEGPanel.clusters_lookup[cluster]
#     cluster_name = get_cluster_name(cluster)
#     contours = MEGPanel.contours[cluster.hemi]
#     label_ind = np.where(np.array(contours['labels']) == cluster_name)[0][0] + 1
#     clustes_contour_vertices = np.where(contours['contours'] == label_ind)[0]
#     hemi_obj_name = 'inflated_{}'.format(cluster.hemi)
#     if hemi_obj_name not in _addon().get_prev_colors():
#         _addon().color_prev_colors(clustes_contour_vertices, hemi_obj_name)


def dipole_fit():
    mu.add_mmvt_code_root_to_path()
    from src.preproc import meg
    importlib.reload(meg)

    subject = mu.get_user()
    args = meg.read_cmd_args(dict(subject=subject, mri_subject=subject, atlas=mu.get_atlas()))
    meg.init(subject, args)
    dipoles_times = [(bpy.context.scene.meg_dipole_fit_tmin, bpy.context.scene.meg_dipole_fit_tmax)]
    dipoloes_title = mask_roi = MEGPanel.current_cluster['intersects'][0]['name']
    meg.dipoles_fit(
        dipoles_times, dipoloes_title, None, mu.get_real_fname('meg_noise_cov_fname'), mu.get_real_fname('meg_evoked_fname'),
        mu.get_real_fname('head_to_mri_trans_mat_fname'), 5., bpy.context.scene.meg_dipole_fit_use_meg,
        bpy.context.scene.meg_dipole_fit_use_eeg, mask_roi=mask_roi, do_plot=False, n_jobs=4)


def set_cluster_time_series(cluster):
    cluster_uid_name = get_cluster_fcurve_name(cluster)
    _addon().create_empty_if_doesnt_exists(
        PARENT_OBJ_NAME, _addon().EMPTY_LAYER, bpy.context.scene.layers, 'Functional maps')
    parent_obj = bpy.data.objects[PARENT_OBJ_NAME]
    if cluster.label_data is None:
        return
    T = len(cluster.label_data)
    cluster.label_data = np.array(cluster.label_data, dtype=np.float64)
    fcurves_names = mu.get_fcurves_names(parent_obj)
    if not cluster_uid_name in fcurves_names:
        # Set the values to zeros in the first and last frame for current object(current label)
        mu.insert_keyframe_to_custom_prop(parent_obj, cluster_uid_name, 0, 1)
        mu.insert_keyframe_to_custom_prop(parent_obj, cluster_uid_name, 0, T + 2)

        # For every time point insert keyframe to current object
        for ind, t_data in enumerate(cluster.label_data):
            mu.insert_keyframe_to_custom_prop(parent_obj, cluster_uid_name, t_data, ind + 2)

        # remove the orange keyframe sign in the fcurves window
        fcurve_ind = len(fcurves_names)
        fcurves = parent_obj.animation_data.action.fcurves[fcurve_ind]
        mod = fcurves.modifiers.new(type='LIMITS')
    else:
        fcurve_ind = fcurves_names.index(cluster_uid_name)
        fcurve = parent_obj.animation_data.action.fcurves[fcurve_ind]
        fcurve.keyframe_points[0].co[1] = 0
        fcurve.keyframe_points[-1].co[1] = 0
        for t in range(T):
            if fcurve.keyframe_points[t + 1].co[1] != cluster.label_data[t]:
                fcurve.keyframe_points[t + 1].co[1] = cluster.label_data[t]
    # mu.view_all_in_graph_editor()


def filter_clusters(val_threshold=None, size_threshold=None, clusters_label=None):
    if val_threshold is None:
        val_threshold = bpy.context.scene.meg_cluster_val_threshold
    if size_threshold is None:
        size_threshold = bpy.context.scene.meg_cluster_size_threshold
    if clusters_label is None:
        clusters_label = bpy.context.scene.meg_clusters_label
    return [c for c in MEGPanel.clusters_labels.values
            if abs(c.max) >= val_threshold and c.size >= size_threshold and \
            clusters_label in c.name]
            # any([clusters_label in inter_label['name'] for inter_label in c.intersects])]


def get_label_data_fname():
    return op.join(mu.get_user_fol(), 'meg', 'labels_data_{}_{}.npz'.format(
        bpy.context.scene.meg_data_labels_files, '{hemi}'))


def get_label_data_minmax_fname():
    return op.join(mu.get_user_fol(), 'meg', 'labels_data_{}_minmax.npz'.format(
        bpy.context.scene.meg_data_labels_files))


def meg_clusters_labels_files_update(self, context):
    if MEGPanel.init:
        # fname = MEGPanel.clusters_labels_fnames[bpy.context.scene.meg_clusters_labels_files]
        # MEGPanel.clusters_labels = mu.load(fname)
        # MEGPanel.clusters_labels = mu.Bag(MEGPanel.clusters_labels)
        # for ind in range(len(MEGPanel.clusters_labels.values)):
        #     MEGPanel.clusters_labels.values[ind] = mu.Bag(MEGPanel.clusters_labels.values[ind])
        _meg_clusters_labels_files_update()


def _meg_clusters_labels_files_update():
    if MEGPanel.should_load_clusters_file:
        MEGPanel.clusters_labels = load_clusters_file()
    load_contours()
    update_clusters()
    load_stc()


def load_clusters_file(clusters_name=''):
    if clusters_name == '':
        clusters_name = bpy.context.scene.meg_clusters_labels_files
    fname = MEGPanel.clusters_labels_fnames[clusters_name]
    c = mu.Bag(mu.load(fname))
    for ind in range(len(c.values)):
        c.values[ind] = mu.Bag(c.values[ind])
    return c


def load_stc():
    if MNE_EXIST:
        stc_fname = op.join(mu.get_user_fol(), 'meg', '{}-lh.stc'.format(MEGPanel.clusters_labels.stc_name))
        if op.isfile(stc_fname):
            MEGPanel.stc = mne.read_source_estimate(stc_fname)
            if mu.max_stc(MEGPanel.stc) < 1e-4:
                MEGPanel.stc._data *= np.power(10, 9) # from Amp to nAmp
            MEGPanel.max_stc = get_max_stc_t(MEGPanel.stc, MEGPanel.clusters_labels.time)
        else:
            print('load_stc: Can\'t find {}!'.format(stc_fname))

def load_contours():
    contours = mu.Bag({hemi:None for hemi in mu.HEMIS})
    for hemi in mu.HEMIS:
        verts_num = len(bpy.data.objects[hemi].data.vertices)
        contours[hemi] = mu.Bag(dict(contours=np.zeros(verts_num), labels=[], max=0))
        contours_fnames = glob.glob(op.join(mu.get_user_fol(), 'labels', 'clusters-{}*_contours_{}.npz'.format(
            bpy.context.scene.meg_clusters_labels_files, hemi)))
        for contours_fname in contours_fnames:
            d = np.load(contours_fname)
            # print(contours_fname, d['labels'], np.unique(d['contours']))
            contours_data = d['contours']
            contours_data[np.where(contours_data)] += len(contours[hemi].labels)
            contours[hemi].contours += contours_data
            labels = [l for l in d['labels'] if 'unknown' not in l]
            contours[hemi].labels.extend(labels)
    for hemi in mu.HEMIS:
        contours[hemi].max = len(contours[hemi].labels)
        # print('contours in {} {}: {}'.format(hemi, bpy.context.scene.meg_clusters_labels_files,
        #                                      np.unique(contours[hemi].contours)))
    MEGPanel.contours = contours


def get_clusters_files(user_fol=''):
    clusters_labels_files = glob.glob(op.join(user_fol, 'meg', 'clusters', 'clusters_labels_*.pkl'))
    files_names = [mu.namebase(fname)[len('clusters_labels_'):] for fname in clusters_labels_files]
    clusters_labels_items = [(c, c, '', ind) for ind, c in enumerate(list(set(files_names)))]
    return files_names, clusters_labels_files, clusters_labels_items


def meg_how_to_sort_update(self, context):
    if MEGPanel.init:
        update_clusters()


def cluster_name(x):
    return _cluster_name(x, bpy.context.scene.meg_how_to_sort)


def _cluster_name(x, sort_mode):
    if sort_mode == 'val':
        return '{}_{:.2f}'.format(x.name, x.max)
    elif sort_mode == 'size':
        return '{}_{:.2f}'.format(x.name, x.size)
    elif sort_mode == 'label':
        return x.name


def update_clusters(val_threshold=None, size_threshold=None, clusters_label=''):
    if val_threshold is None:
        val_threshold = bpy.context.scene.meg_clusters_val_threshold
    if size_threshold is None:
        size_threshold = bpy.context.scene.meg_clusters_size_threshold
    if clusters_label == '':
        clusters_label = bpy.context.scene.meg_clusters_label
    MEGPanel.clusters_labels_filtered = filter_clusters(val_threshold, size_threshold, clusters_label)
    for cluster in MEGPanel.clusters_labels_filtered:
        set_cluster_time_series(cluster)
    if bpy.context.scene.meg_how_to_sort == 'val':
        sort_func = lambda x: abs(x.max)
    elif bpy.context.scene.meg_how_to_sort == 'size':
        sort_func = lambda x: x.size
    elif bpy.context.scene.meg_how_to_sort == 'label':
        sort_func = lambda x: x.name
    clusters_tup = sorted([(sort_func(x), cluster_name(x)) for x in MEGPanel.clusters_labels_filtered])[::-1]
    MEGPanel.clusters = [x_name for x_size, x_name in clusters_tup]
    clusters_names = [cluster_name(x) for x in MEGPanel.clusters_labels_filtered]
    MEGPanel.clusters_lookup = {x_name:cluster for x_name, cluster in
                                zip(clusters_names, MEGPanel.clusters_labels_filtered)}
    # MEGPanel.clusters.sort(key=mu.natural_keys)
    clusters_items = [(c, c, '', ind + 1) for ind, c in enumerate(MEGPanel.clusters)]
    bpy.types.Scene.meg_clusters = bpy.props.EnumProperty(
        items=clusters_items, description="meg clusters", update=clusters_update)
    if len(MEGPanel.clusters) > 0:
        bpy.context.scene.meg_clusters = MEGPanel.clusters[0]


def next_cluster():
    index = MEGPanel.clusters.index(bpy.context.scene.meg_clusters)
    next_cluster = MEGPanel.clusters[index + 1] if index < len(MEGPanel.clusters) - 1 else MEGPanel.clusters[0]
    bpy.context.scene.meg_clusters = next_cluster


def prev_cluster():
    index = MEGPanel.clusters.index(bpy.context.scene.meg_clusters)
    prev_cluster = MEGPanel.clusters[index - 1] if index > 0 else MEGPanel.clusters[-1]
    bpy.context.scene.meg_clusters = prev_cluster


def plot_meg_clusters():
    if MEGPanel.stc is not None:
        if bpy.context.scene.coloring_lower_threshold > MEGPanel.max_stc:
            bpy.context.scene.coloring_lower_threshold = 0
        _addon().plot_stc(MEGPanel.stc, MEGPanel.clusters_labels.time,
                 threshold=bpy.context.scene.coloring_lower_threshold, save_image=False, save_prev_colors=True)
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('MEG activity (nAmp)')
        bpy.context.scene.frame_current = MEGPanel.clusters_labels.time


def get_max_stc_t(stc, t):
    C = max([stc.rh_data.shape[0], stc.lh_data.shape[0]])
    stc_lh_data = stc.lh_data[:, t:t + 1] if stc.lh_data.shape[0] > 0 else np.zeros((C, 1))
    stc_rh_data = stc.rh_data[:, t:t + 1] if stc.rh_data.shape[0] > 0 else np.zeros((C, 1))
    data = np.concatenate([stc_lh_data, stc_rh_data])
    return np.max(np.abs(data))


def select_meg_cluster(event, context, pos=None):
    if not MEGPanel.init:
        return

    # Should be checked in the appearence modal loop
    # area = mu.get_click_area(event, context)
    # if area.type != 'VIEW_3D':
    #     return

    # if pos is None:    #
    # from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d
    #     region = [r for r in area.regions if r.type == 'WINDOW'][0]
    #     rv3d = area.spaces.active.region_3d
    #     coord = (event.mouse_x - area.x, event.mouse_y - area.y)
    #     vec = region_2d_to_vector_3d(region, rv3d, coord)
    #     pos = region_2d_to_location_3d(region, rv3d, coord, vec)
    #     # pos = mu.mouse_coo_to_3d_loc(event, context)
    #     print('pos, ', pos)
    # else:
    #     print('cursor, ', pos)
    if pos is None:
        return
    # bpy.context.scene.cumulate_meg_cluster = event.shift
    for clusters_name in MEGPanel.clusters_labels_fnames.keys():
        clusters = load_clusters_file(clusters_name)
        for cluster in clusters.values: #MEGPanel.clusters_labels.values:
            cluster_hemi_mesh_name = 'inflated_{}'.format(cluster.hemi)
            cluster_hemi_obj = bpy.data.objects[cluster_hemi_mesh_name]
            cluster_pos = pos * cluster_hemi_obj.matrix_world.inverted()

            cluster_vertices_co = get_cluster_verts_co(cluster)
            # dist = np.linalg.norm(cluster_max_vert_co - cluster_pos)
            # print(cluster.name, dist, cluster_max_vert_co, cluster_pos)
            co, index, dist = mu.min_cdist(cluster_vertices_co, [cluster_pos])
            # print(cluster.name, co, index, dist, cluster_pos)
            if dist < 1:
            # if cluster_hemi_mesh_name == closest_mesh_name and vertex_ind in cluster.vertices:
                if bpy.context.scene.meg_clusters_labels_files != clusters_name:
                    MEGPanel.should_load_clusters_file = False
                    MEGPanel.clusters_labels = clusters
                    bpy.context.scene.meg_clusters_labels_files = clusters_name
                    MEGPanel.should_load_clusters_file = True
                bpy.context.scene.meg_clusters = cluster_name(cluster)
                return cluster
    return None


def select_all_clusters():
    parent_obj = bpy.data.objects.get(PARENT_OBJ_NAME, None)
    if parent_obj is not None:
        parent_obj.select = True

    fcurves = mu.get_fcurves(PARENT_OBJ_NAME)
    filtered_fcurves_names = [get_cluster_fcurve_name(c) for c in MEGPanel.clusters_labels_filtered]
    for fcurve in fcurves:
        fcurve_name = mu.get_fcurve_name(fcurve)
        fcurve.hide = fcurve_name not in filtered_fcurves_names
    plot_all_clusters()
    mu.view_all_in_graph_editor()
    # mu.change_selected_fcurves_colors(mu.OBJ_TYPE_ELECTRODE)


def flip_meg_clusters_ts():
    fcurves = mu.get_fcurves(PARENT_OBJ_NAME, only_not_hiden=True)
    for fcurve, cluster in zip(fcurves, MEGPanel.clusters_labels_filtered):
        if cluster.ts_max < 0:
            for t in range(len(cluster.label_data)):
                fcurve.keyframe_points[t].co[1] = -fcurve.keyframe_points[t].co[1]
    MEGPanel.data_is_flipped = not MEGPanel.data_is_flipped


def deselect_all_clusters():
    for fcurve in mu.get_fcurves(PARENT_OBJ_NAME):
        fcurve.hide = True
    clear_all_clusters()


def clear_all_clusters():
    for obj_name in mu.INF_HEMIS:
        mesh = bpy.data.objects[obj_name].data
        _addon().recreate_coloring_layers(mesh, 'contours')
    # for cluster in MEGPanel.clusters:
    #     clear_cluster(cluster)


def plot_activity_contours(activity_contours_name, colormap='RdOrYl'):
    _addon().show_activity()
    all_contours = mu.load(op.join(mu.get_user_fol(), 'meg', 'clusters', '{}.pkl'.format(activity_contours_name)))
    thresholds = sorted([float(k) for k in all_contours.keys()])
    _addon().colorbar.set_colormap(colormap)
    _addon().colorbar.set_colorbar_max_min(np.max(thresholds), 0)
    for hemi in mu.HEMIS:
        hemi_contours = np.zeros(len(bpy.data.objects[hemi].data.vertices))
        for threshold in all_contours.keys():
            if threshold in all_contours and hemi in all_contours[threshold]:
                hemi_contours[all_contours[threshold][hemi]] = threshold
        mesh = mu.get_hemi_obj(hemi).data
        mesh.vertex_colors.active_index = mesh.vertex_colors.keys().index('contours')
        mesh.vertex_colors['contours'].active_render = True
        _addon().color_hemi_data(
            hemi, hemi_contours, 0.1, 256 / np.max(thresholds), override_current_mat=True,
            coloring_layer='contours', check_valid_verts=False)


def meg_draw(self, context):
    layout = self.layout

    if MEGPanel.meg_sensors_exist:
        col = layout.box().column()
        col.prop(context.scene, 'meg_sensors_files', text='')
        col.prop(context.scene, 'meg_sensors_types', text='')
        if len(MEGPanel.meg_sensors_conditions_items) > 1:
            col.prop(context.scene, "meg_sensors_conditions", text="")
        col.operator(ColorMEGSensors.bl_idname, text="Plot MEG sensors", icon='POTATO')
        # if not bpy.data.objects.get('meg_helmet', None) is None:
            # col.operator(ColorMEGHelmet.bl_idname, text="Plot MEG Helmet", icon='POTATO')
            # col.prop(context.scene, 'plot_mesh_using_uv_map', text='Use UV map')
        col.prop(context.scene, 'find_max_meg_sensors', text='Find peak activity')

    if MEGPanel.eeg_sensors_exist:
        col = layout.box().column()
        col.prop(context.scene, 'eeg_sensors_files', text='')
        if len(MEGPanel.eeg_sensors_conditions_items) > 1:
            col.prop(context.scene, "eeg_sensors_conditions", text="")
        col.operator(ColorEEGSensors.bl_idname, text="Plot EEG sensors", icon='POTATO')
        # if not bpy.data.objects.get('eeg_helmet', None) is None:
            # col.operator(ColorEEGHelmet.bl_idname, text="Plot EEG Helmet", icon='POTATO')
            # col.prop(context.scene, 'plot_mesh_using_uv_map', text='Use UV map')
        col.prop(context.scene, 'find_max_eeg_sensors', text='Find peak activity')

    if MEGPanel.meg_labels_data_files_exist:
        col = layout.box().column()
        col.label(text='EEG/MEG labels data: ')
        col.prop(context.scene, 'meg_data_labels_files', text='')

    if MEGPanel.meg_clusters_files_exist:
        layout.prop(context.scene, 'meg_clusters_labels_files', text='')
        if MNE_EXIST:
            layout.operator(PlotMEGClusters.bl_idname, text='Plot STC', icon='POTATO')
        row = layout.row(align=True)
        row.operator(PrevMEGCluster.bl_idname, text="", icon='PREV_KEYFRAME')
        row.prop(context.scene, 'meg_clusters', text='')
        row.operator(NextMEGCluster.bl_idname, text="", icon='NEXT_KEYFRAME')
        row = layout.row(align=True)
        row.label(text='Sort: ')
        row.prop(context.scene, 'meg_how_to_sort', expand=True)
        layout.prop(context.scene, 'meg_show_filtering', text='Refine clusters')
        if bpy.context.scene.meg_show_filtering:
            layout.prop(context.scene, 'meg_clusters_val_threshold', text='Val threshold')
            layout.prop(context.scene, 'meg_clusters_size_threshold', text='Size threshold')
            layout.prop(context.scene, 'meg_clusters_label', text='Label filter')
            layout.operator(FilterMEGClusters.bl_idname, text="Filter clusters", icon='FILTER')
        layout.prop(context.scene, 'plot_current_meg_cluster', text="Plot current cluster's contour")
        layout.prop(context.scene, 'cumulate_meg_cluster', text="Cumulate contours")
        if not MEGPanel.current_cluster is None and len(MEGPanel.current_cluster) > 0: # and not MEGPanel.dont_show_clusters_info:
            cluster_size = MEGPanel.current_cluster['size']
            col = layout.box().column()
            mu.add_box_line(col, 'Max val', '{:.2f}'.format(MEGPanel.current_cluster['max']), 0.7)
            mu.add_box_line(col, 'Size', str(cluster_size), 0.7)
            col = layout.box().column()
            labels_num_to_show = min(7, len(MEGPanel.current_cluster['intersects']))
            for inter_labels in MEGPanel.current_cluster['intersects'][:labels_num_to_show]:
                mu.add_box_line(col, inter_labels['name'], '{:.0%}'.format(inter_labels['num'] / float(cluster_size)), 0.8)
            if labels_num_to_show < len(MEGPanel.current_cluster['intersects']):
                layout.label(text='Out of {} labels'.format(len(MEGPanel.current_cluster['intersects'])))
        layout.operator(SelectAllClusters.bl_idname, text="Select all", icon='BORDER_RECT')
        text = 'Flip time series' if not MEGPanel.data_is_flipped else 'Unflip time series'
        layout.operator(FlipMEGClustersTS.bl_idname, text=text, icon='FORCE_MAGNETIC')
        layout.operator(DeselecAllClusters.bl_idname, text="Deselect all", icon='PANEL_CLOSE')
        layout.operator(ClearClusters.bl_idname, text="Clear all clusters", icon='PANEL_CLOSE')
        layout.operator(_addon().ClearColors.bl_idname, text="Clear activity", icon='PANEL_CLOSE')
        layout.prop(context.scene, 'calc_meg_dipole_fit', text='Show dipole fit info')
        if bpy.context.scene.calc_meg_dipole_fit:
            col = layout.box().column()
            col.prop(context.scene, 'meg_evoked_fname', text='evoked')
            col.prop(context.scene, 'meg_noise_cov_fname', text='noise cov')
            col.prop(context.scene, 'head_to_mri_trans_mat_fname', text='trans mat')
            row = col.row(align=True)
            row.prop(context.scene, 'meg_dipole_fit_tmin', text='from t(s)')
            row.prop(context.scene, 'meg_dipole_fit_tmax', text='to t(s)')
            row = col.row(align=True)
            row.prop(context.scene, 'meg_dipole_fit_use_meg', text='use MEG')
            row.prop(context.scene, 'meg_dipole_fit_use_eeg', text='use EEG')
            col.operator(DipoleFit.bl_idname, text='Dipole fit', icon='OOPS')


bpy.types.Scene.meg_sensors_conditions = bpy.props.EnumProperty(items=[],
    description='Selects the condition to plot the MEG sensors activity.\n\nCurrent condition')
bpy.types.Scene.eeg_sensors_conditions= bpy.props.EnumProperty(items=[],
    description='Selects the condition to plot the EEG sensors activity.\n\nCurrent condition')
bpy.types.Scene.meg_sensors_files = bpy.props.EnumProperty(items=[])
bpy.types.Scene.meg_sensors_types = bpy.props.EnumProperty(items=[])
bpy.types.Scene.eeg_sensors_files = bpy.props.EnumProperty(items=[])


bpy.types.Scene.meg_clusters_labels_files = bpy.props.EnumProperty(
    items=[], description="meg files", update=meg_clusters_labels_files_update)
bpy.types.Scene.meg_clusters = bpy.props.EnumProperty(
    items=[], description="meg clusters", update=clusters_update)
bpy.types.Scene.meg_data_labels_files = bpy.props.EnumProperty(items=[], description="meg labels datafiles")
bpy.types.Scene.meg_clusters_val_threshold = bpy.props.FloatProperty(min=0)
bpy.types.Scene.meg_clusters_size_threshold = bpy.props.FloatProperty(min=0)
bpy.types.Scene.meg_clusters_label = bpy.props.StringProperty()
bpy.types.Scene.meg_how_to_sort = bpy.props.EnumProperty(
    items=[('val', 'val', '', 1), ('size', 'size', '', 2), ('label', 'label', '', 3)],
    description='How to sort', update=meg_how_to_sort_update)
bpy.types.Scene.meg_show_filtering = bpy.props.BoolProperty(default=False)
bpy.types.Scene.plot_current_meg_cluster = bpy.props.BoolProperty(
    default=True, description="Plot current cluster's contour")
bpy.types.Scene.cumulate_meg_cluster = bpy.props.BoolProperty(default=False, description="Cumulate contours")
bpy.types.Scene.calc_meg_dipole_fit = bpy.props.BoolProperty(default=False)
bpy.types.Scene.meg_evoked_fname = bpy.props.StringProperty(subtype='FILE_PATH')
bpy.types.Scene.meg_noise_cov_fname = bpy.props.StringProperty(subtype='FILE_PATH')
bpy.types.Scene.head_to_mri_trans_mat_fname = bpy.props.StringProperty(subtype='FILE_PATH')
bpy.types.Scene.meg_dipole_fit_tmin = bpy.props.FloatProperty()
bpy.types.Scene.meg_dipole_fit_tmax = bpy.props.FloatProperty()
bpy.types.Scene.meg_dipole_fit_use_meg = bpy.props.BoolProperty(default=True)
bpy.types.Scene.meg_dipole_fit_use_eeg = bpy.props.BoolProperty(default=False)
bpy.types.Scene.plot_mesh_using_uv_map = bpy.props.BoolProperty(default=False)
bpy.types.Scene.find_max_meg_sensors = bpy.props.BoolProperty(default=False)
bpy.types.Scene.find_max_eeg_sensors = bpy.props.BoolProperty(default=False)


class NextMEGCluster(bpy.types.Operator):
    bl_idname = 'mmvt.next_meg_cluster'
    bl_label = 'nextMEGCluster'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        next_cluster()
        return {'FINISHED'}


class PrevMEGCluster(bpy.types.Operator):
    bl_idname = 'mmvt.prev_meg_cluster'
    bl_label = 'prevMEGCluster'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        prev_cluster()
        return {'FINISHED'}


class FlipMEGClustersTS(bpy.types.Operator):
    bl_idname = "mmvt.flip_meg_clusters_ts"
    bl_label = "Flip meg clusters ts"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        flip_meg_clusters_ts()
        return {'PASS_THROUGH'}


class DipoleFit(bpy.types.Operator):
    bl_idname = "mmvt.dipole_fit"
    bl_label = "Dipole fit"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        dipole_fit()
        return {'PASS_THROUGH'}


class SelectAllClusters(bpy.types.Operator):
    bl_idname = "mmvt.select_all_meg_clusters"
    bl_label = "Select all meg clusters"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        select_all_clusters()
        return {'PASS_THROUGH'}


class DeselecAllClusters(bpy.types.Operator):
    bl_idname = "mmvt.deselect_all_meg_clusters"
    bl_label = "Deselect all meg clusters"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        deselect_all_clusters()
        return {'PASS_THROUGH'}


class ClearClusters(bpy.types.Operator):
    bl_idname = "mmvt.clear_all_meg_clusters"
    bl_label = "Clear all meg clusters"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        clear_all_clusters()
        return {'PASS_THROUGH'}


class FilterMEGClusters(bpy.types.Operator):
    bl_idname = "mmvt.filter_meg_clusters"
    bl_label = "Filter MEG clusters"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        update_clusters()
        return {'PASS_THROUGH'}


class PlotMEGClusters(bpy.types.Operator):
    bl_idname = "mmvt.plot_meg_clusters"
    bl_label = "Plot MEG clusters"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        plot_meg_clusters()
        return {'PASS_THROUGH'}


class MEGPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "EEG and MEG"
    addon = None
    init = False
    clusters_labels = None
    clusters_labels_fnames = {}
    stc = None
    prev_cluster = ''
    current_cluster = {}
    should_load_clusters_file = True
    data_is_flipped = False
    eeg_helmet_indices = []
    meg_helmet_indices = {}
    meg_sensors_groups = defaultdict(list)
    eeg_sensors_exist = False
    meg_sensors_exist = False
    eeg_sensors_data_minmax, eeg_sensors_colors_ratio = None, None
    meg_sensors_data_minmax, meg_sensors_colors_ratio = None, None
    eeg_sensors_data, eeg_sensors_meta_data, eeg_sensors_data_minmax = {}, {}, None
    meg_sensors_data, meg_sensors_meta_data, meg_sensors_data_minmax = {}, {}, None
    eeg_sensors_conditions_items = []
    meg_sensors_conditions_items = []
    meg_labels_data_files_exist = False

    def draw(self, context):
        if MEGPanel.init:
            meg_draw(self, context)


def init_labels_data():
    labels_data_files = []
    labels_rh_data_files = glob.glob(op.join(mu.get_user_fol(), 'meg', 'labels_data_*_rh.npz'))
    for labels_data_fname in labels_rh_data_files:
        lh_fname = '{}_lh.npz'.format(labels_data_fname[:-7])
        if op.isfile(lh_fname):
            labels_data_files.append(mu.namebase(labels_data_fname)[len('labels_data_'):-3])
    if len(labels_data_files) > 0:
        meg_data_labels_items = [(c, c, '', ind) for ind, c in enumerate(list(set(labels_data_files)))]
        bpy.types.Scene.meg_data_labels_files = bpy.props.EnumProperty(
            items=meg_data_labels_items, description="meg labels data files")
    MEGPanel.meg_labels_data_files_exist = len(labels_data_files) > 0


def init(addon):
    MEGPanel.addon = addon
    user_fol = mu.get_user_fol()

    input_files = glob.glob(op.join(mu.get_user_fol(), 'meg', 'meg_*_sensors_positions.npz'))
    sensors_types = sorted([mu.namebase(input_file).split('_')[1] for input_file in input_files])
    MEGPanel.meg_sensors_types = {sensors_types:num for num, sensors_types in enumerate(sensors_types)}

    MEGPanel.eeg_sensors_exist = init_eeg_sensors()
    MEGPanel.meg_sensors_exist = init_meg_sensors()

    meg_files = glob.glob(op.join(user_fol, 'meg', 'meg*.npz'))
    if len(meg_files) == 0:
        print('No MEG clusters files')
        # return None

    files_names, clusters_labels_files, clusters_labels_items = get_clusters_files(user_fol)
    MEGPanel.meg_clusters_files_exist = len(files_names) > 0
    if not MEGPanel.meg_clusters_files_exist:
        print('No MEG_clusters_files_exist')
    else:
        for fname, name in zip(clusters_labels_files, files_names):
            MEGPanel.clusters_labels_fnames[name] = fname
        bpy.types.Scene.meg_clusters_labels_files = bpy.props.EnumProperty(
            items=clusters_labels_items, description="meg files", update=meg_clusters_labels_files_update)
        bpy.context.scene.meg_clusters_labels_files = files_names[0]
        _meg_clusters_labels_files_update()
        bpy.context.scene.meg_clusters_val_threshold = MEGPanel.clusters_labels.min_cluster_max
        bpy.context.scene.meg_clusters_size_threshold = MEGPanel.clusters_labels.min_cluster_size
        bpy.context.scene.meg_clusters_label = MEGPanel.clusters_labels.clusters_label
        bpy.context.scene.meg_how_to_sort = 'val'
        bpy.context.scene.meg_show_filtering = False
        bpy.context.scene.cumulate_meg_cluster = False

    init_labels_data()
    register()
    MEGPanel.init = True


def register():
    try:
        unregister()
        bpy.utils.register_class(MEGPanel)
        bpy.utils.register_class(NextMEGCluster)
        bpy.utils.register_class(PlotMEGClusters)
        bpy.utils.register_class(PrevMEGCluster)
        bpy.utils.register_class(FilterMEGClusters)
        bpy.utils.register_class(SelectAllClusters)
        bpy.utils.register_class(FlipMEGClustersTS)
        bpy.utils.register_class(DipoleFit)
        bpy.utils.register_class(DeselecAllClusters)
        bpy.utils.register_class(ClearClusters)
        bpy.utils.register_class(ColorMEGSensors)
        bpy.utils.register_class(ColorEEGSensors)
        bpy.utils.register_class(ColorEEGHelmet)
        bpy.utils.register_class(ColorMEGHelmet)
    except:
        print("Can't register MEG Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(MEGPanel)
        bpy.utils.unregister_class(PlotMEGClusters)
        bpy.utils.unregister_class(NextMEGCluster)
        bpy.utils.unregister_class(PrevMEGCluster)
        bpy.utils.unregister_class(FilterMEGClusters)
        bpy.utils.unregister_class(SelectAllClusters)
        bpy.utils.unregister_class(FlipMEGClustersTS)
        bpy.utils.unregister_class(DipoleFit)
        bpy.utils.unregister_class(DeselecAllClusters)
        bpy.utils.unregister_class(ClearClusters)
        bpy.utils.unregister_class(ColorMEGSensors)
        bpy.utils.unregister_class(ColorEEGSensors)
        bpy.utils.unregister_class(ColorEEGHelmet)
        bpy.utils.unregister_class(ColorMEGHelmet)
    except:
        pass

