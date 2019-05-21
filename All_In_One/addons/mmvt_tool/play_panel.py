import bpy
import mmvt_utils as mu
import os.path as op
import numpy as np
import traceback
import time
import os
import pprint as pp # pretty printing: pp.pprint(something)
from collections import OrderedDict
import glob
import re
import shutil

HEMIS = mu.HEMIS

bpy.types.Scene.play_from = bpy.props.IntProperty(default=0, min=0,
    description='Sets the starting time point of the activity')
bpy.types.Scene.play_to = bpy.props.IntProperty(default=bpy.context.scene.frame_end, min=0,
    description='Sets the ending time point of the activity')
bpy.types.Scene.play_dt = bpy.props.IntProperty(default=50, min=1, description='Transition')
bpy.types.Scene.play_time_step = bpy.props.FloatProperty(default=0.1, min=0,
                                                  description="How much time (s) to wait between frames")
bpy.types.Scene.render_movie = bpy.props.BoolProperty(default=False, description='Renders each frame')
bpy.types.Scene.save_images = bpy.props.BoolProperty(default=False,
    description='Saves the played images in the subject’s ‘movies’ folder.'
                '\nExample: ..mmvt_root/mmvt_blend/colin27/movies')
bpy.types.Scene.rotate_brain_while_playing = bpy.props.BoolProperty(default=False,
    description='Rotates the brain while playing according to the x,y,z axis set bellow')
bpy.types.Scene.meg_threshold = bpy.props.FloatProperty(default=2, min=0)
bpy.types.Scene.electrodes_threshold = bpy.props.FloatProperty(default=2, min=0)
bpy.types.Scene.connectivity_threshold = bpy.props.FloatProperty(default=2, min=0)
items_names = [("meg", "MEG activity"), ("meg_labels", 'MEG Labels'),
       ('fmri', 'fMRI'), ('fmri_dynamics', 'fMRI dynamics'),
       ('fmri_labels', 'fMRI labels dynamics'),
       ("labels_connectivity", "Labels connectivity"),
       ("elecs", "Electrodes activity"), ("elecs_connectivity", "Electrodes connectivity"),
       ("elecs_coh", "Electrodes coherence"), ("elecs_act_coh", "Electrodes activity & coherence"),
       ("stim", "Electrodes stimulation"), ("stim_sources", "Electrodes stimulation & sources"),
       ("meg_elecs", "Meg & Electrodes activity"),
       ("meg_elecs_coh", "Meg & Electrodes activity & coherence"),
       ("meg_sensors", "MEG sensors"), ("meg_helmet", "MEG helmet"),
       ("eeg_helmet", "EEG helmet"), ("eeg_sensors", "EEG sensors"),
       ('meg_helmet_source', 'MEG helmet & source'),
       ('eeg_helmet_source', 'EEG helmet & source')]
items = [(n[0], n[1], '', ind) for ind, n in enumerate(items_names)]
bpy.types.Scene.play_type = bpy.props.EnumProperty(items=items, description='Chooses the displayed modality\n\nCurrent modality')
bpy.types.Scene.frames_num = bpy.props.IntProperty(default=5, min=1, description='Sets the frames per second for the video')
bpy.types.Scene.add_reverse_frames = bpy.props.BoolProperty(
    default=False, description='Add reverse frames to the end of the movie')
bpy.types.Scene.play_miscs = bpy.props.EnumProperty(
    items=[('inflating', 'inflating', '', 1), ('slicing', 'slicing', '', 2)])


def _addon():
    return PlayPanel.addon


def get_current_t():
    return bpy.context.scene.frame_current


def set_current_t(t):
    bpy.context.scene.frame_current = t


def set_rotate_brain_while_playing(val=True):
    bpy.context.scene.rotate_brain_while_playing = val


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    # limits = bpy.props.IntProperty(default=bpy.context.scene.play_from)
    limits = bpy.context.scene.play_from
    _timer = None
    _time = time.time()
    _uuid = mu.rand_letters(5)

    def modal(self, context, event):
        # First frame initialization:
        if PlayPanel.init_play:
            ModalTimerOperator._uuid = mu.rand_letters(5)
            self.limits = bpy.context.scene.frame_current

        if not PlayPanel.is_playing:
            return {'PASS_THROUGH'}

        if event.type in {'RIGHTMOUSE', 'ESC'} or self.limits > bpy.context.scene.play_to:
            plot_something(self, context, bpy.context.scene.play_to, ModalTimerOperator._uuid)
            print('Stop!')
            self.limits = bpy.context.scene.play_from
            PlayPanel.is_playing = False
            bpy.context.scene.update()
            self.cancel(context)
            return {'PASS_THROUGH'}

        if event.type == 'TIMER':
            # print(time.time() - self._time)
            if time.time() - self._time > bpy.context.scene.play_time_step:
                rotate_while_playing()
                # if bpy.context.scene.rotate_brain_while_playing and (
                #             bpy.context.scene.render_movie or bpy.context.scene.save_images):
                #     _addon().camera_mode('ORTHO')
                #     _addon().rotate_brain()
                #     _addon().camera_mode('CAMERA')
                # elif bpy.context.scene.rotate_brain_while_playing:
                #     _addon().rotate_brain()

                bpy.context.scene.frame_current = self.limits
                # print(self.limits, time.time() - self._time)
                self._time = time.time()
                try:
                    plot_something(self, context, self.limits, ModalTimerOperator._uuid)
                except:
                    print(traceback.format_exc())
                    print('Error in plotting at {}!'.format(self.limits))
                self.limits = self.limits - bpy.context.scene.play_dt if PlayPanel.play_reverse else \
                        self.limits + bpy.context.scene.play_dt
                bpy.context.scene.frame_current = self.limits

        return {'PASS_THROUGH'}

    def execute(self, context):
        # ModalTimerOperator._timer = wm.event_timer_add(time_step=bpy.context.scene.play_time_step, window=context.window)
        wm = context.window_manager
        # if ModalTimerOperator._timer:
        #     print('timer is already running!')
        #     print('last tick {}'.format(time.time() - self._time))
        # else:
        self.cancel(context)
        ModalTimerOperator._timer = wm.event_timer_add(time_step=0.05, window=context.window)
        self._time = time.time()
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # if ModalTimerOperator._timer:
        if ModalTimerOperator._timer:
            wm = context.window_manager
            wm.event_timer_remove(ModalTimerOperator._timer)


def rotate_while_playing():
    if bpy.context.scene.rotate_brain_while_playing and (
            bpy.context.scene.render_movie or bpy.context.scene.save_images):
        _addon().camera_mode('ORTHO')
        _addon().rotate_brain()
        _addon().camera_mode('CAMERA')
    elif bpy.context.scene.rotate_brain_while_playing:
        _addon().rotate_brain()


def render_movie(play_type, play_from, play_to, camera_fname='', play_dt=1, set_to_camera_mode=True, rotate_brain=False):
    set_play_to(play_to)
    bpy.context.scene.play_type = play_type
    bpy.context.scene.render_movie = True
    bpy.context.scene.rotate_brain_while_playing = rotate_brain
    print('In play movie!')
    play_range = list(range(play_from, play_to + 1, play_dt))
    runs_num = len(play_range)
    for run, limits in enumerate(play_range):
        print('limits: {}'.format(limits))
        mu.write_to_stderr('Plotting {} frame {} ({}-{}, dt {})'.format(play_type, limits, play_from, play_to, play_dt))
        bpy.context.scene.frame_current = limits
        rotate_while_playing()
        try:
            now = time.time()
            plot_something(None, bpy.context, limits, camera_fname=camera_fname, set_to_camera_mode=set_to_camera_mode)
        except:
            print(traceback.format_exc())
            print('Error in plotting at {}!'.format(limits))
            mu.write_to_stderr(traceback.format_exc())
        else:
            time_took = time.time() - now
            more_time = time_took / (run + 1) * (runs_num - (run +  1))
            mu.write_to_stderr(('{}/{}, {:.2f}s, {:.2f}s to go!'.format(run, runs_num, time_took, more_time)))


def plot_something(self=None, context=None, cur_frame=0, uuid='', camera_fname='', set_to_camera_mode=True,
                   play_type=None):
    if context is None:
        context = bpy.context
    if bpy.context.scene.frame_current > bpy.context.scene.play_to:
        bpy.context.scene.frame_current = bpy.context.scene.play_from

    plot_subcorticals = True
    if play_type is None:
        play_type = bpy.context.scene.play_type

    # todo: implement the important times
    # imp_time = False
    # for imp_time_range in PlayPanel.imp_times:
    #     if imp_time_range[0] <= cur_frame <= imp_time_range[1]:
    #         imp_time = True
    # if not imp_time:
    #     return

    #todo: Check the init_play!
    # if False: #PlayPanel.init_play:

    successful_ret = True
    if play_type in ['meg', 'meg_elecs', 'meg_elecs_coh', 'meg_helmet_source', 'eeg_helmet_source']:
        # if PlayPanel.loop_indices:
        #     _addon().default_coloring(PlayPanel.loop_indices)
        # PlayPanel.loop_indices =
        _addon().coloring.plot_meg()
        _addon().colorbar.lock_colorbar_values(False)
        # successful_ret = _addon().plot_activity('MEG', PlayPanel.faces_verts, bpy.context.scene.meg_threshold,
        #     PlayPanel.meg_sub_activity, plot_subcorticals)
    if play_type in ['fmri']:
        successful_ret = _addon().activity_map_coloring('FMRI')
    if play_type in ['fmri_dynamics']:
        successful_ret = _addon().plot_activity(
            'FMRI_DYNAMICS', PlayPanel.faces_verts, bpy.context.scene.meg_threshold, None, False)
    if play_type in ['elecs', 'meg_elecs', 'elecs_act_coh', 'meg_elecs_coh', 'elecs_connectivity']:
        # _addon().set_appearance_show_electrodes_layer(bpy.context.scene, True)
        plot_electrodes(cur_frame, bpy.context.scene.electrodes_threshold)
    if play_type in ['elecs_connectivity']:
        _addon().coloring.color_connections()
    if play_type == 'meg_labels':
        # todo: get the aparc_name
        labels_data_fname = _addon().meg.get_label_data_fname()
        labels_data_dict = {hemi:np.load(labels_data_fname.format(hemi=hemi)) for hemi in mu.HEMIS}
        _addon().meg_labels_coloring(override_current_mat=True, labels_data_dict=labels_data_dict)
    if play_type == 'labels_connectivity':
        _addon().color_connections()
    if play_type in ['elecs_coh', 'elecs_act_coh', 'meg_elecs_coh']:
        p = _addon().connections_panel
        d = p.ConnectionsPanel.d
        connections_type = bpy.context.scene.connections_type
        abs_threshold = bpy.context.scene.abs_threshold
        condition = bpy.context.scene.conditions
        p.plot_connections(self, context, d, cur_frame, connections_type, condition,
                           bpy.context.scene.connectivity_threshold, abs_threshold)
    if play_type in ['stim', 'stim_sources']:
        plot_electrodes(cur_frame, bpy.context.scene.electrodes_threshold, stim=True)
        # _addon().color_objects_homogeneously(PlayPanel.stim_data)
    if play_type in ['stim_sources']:
        _addon().color_electrodes_sources()
    if play_type in ['eeg_helmet', 'eeg_helmet_source']:
        bpy.context.scene.find_max_eeg_sensors = False
        _addon().color_eeg_sensors()
        # _addon().color_eeg_helmet()
    if play_type in ['eeg_sensors']:
        _addon().color_eeg_sensors()
    if play_type in ['meg_sensors']:
        _addon().color_meg_sensors()
    if play_type in ['meg_helmet', 'meg_helmet_source']:
        bpy.context.scene.find_max_meg_sensors = False
        _addon().color_meg_sensors()
        # _addon().color_meg_helmet()
    if successful_ret:
        if bpy.context.scene.save_images:
            _addon().save_image(play_type, bpy.context.scene.save_selected_view, bpy.context.scene.frame_current)
        if bpy.context.scene.render_movie:
            _addon().render_image(set_to_camera_mode=set_to_camera_mode)
    else:
        print("The image wasn't rendered due to an error in the plotting.")


def capture_graph(play_type=None, output_path=None, selection_type=None):
    if play_type:
        bpy.context.scene.play_type = play_type
    if output_path:
        bpy.context.scene.output_path = output_path
    if selection_type:
        bpy.context.scene.selection_type = selection_type

    play_type = bpy.context.scene.play_type
    # image_fol = op.join(mu.get_user_fol(), 'images', ExportGraph.uuid)
    image_fol = bpy.path.abspath(bpy.context.scene.output_path)
    if not op.isdir(image_fol):
        raise Exception('You need to set first the images folder in the Render panel!')
    graph_data, graph_colors = {}, {}
    per_condition = bpy.context.scene.selection_type == 'conds'

    if play_type in ['elecs_coh', 'elecs_act_coh', 'meg_elecs_coh']:
        graph_data['coherence'], graph_colors['coherence'] = _addon().connections_panel.capture_graph_data(per_condition)
    if play_type in ['elecs', 'meg_elecs', 'elecs_act_coh', 'meg_elecs_coh']:
        graph_data['electrodes'], graph_colors['electrodes'] = get_electrodes_data(per_condition)
    if play_type in ['meg', 'meg_elecs', 'meg_elecs_coh']:
        graph_data['meg'], graph_colors['meg'] = get_meg_data(per_condition)
    if play_type in ['fmri']:
        graph_data['fmri'], graph_colors['fmri'] = get_fmri_data()
    if play_type in ['meg_labels']:
        graph_data['meg_labels'], graph_colors['meg_labels'] = get_meg_labels_data()
    if play_type in ['labels_connectivity']:
        graph_data['labels_connectivity'], graph_colors['labels_connectivity'] = get_connectivity_data()
    if play_type in ['stim', 'stim_sources']:
        graph_data['stim'], graph_colors['stim'] = get_electrodes_data(per_condition=True)
    if play_type in ['stim_sources']:
        graph_data['stim_sources'], graph_colors['stim_sources'] = get_electrodes_sources_data()
    # should let the user set the:
    #  xticklabels (--xticklabels '-1,stim_onset,0,end_of_stim')
    #  time_range (--time_range '-1,1.5,0.01')
    #  xtick_dt (--xtick_dt 0.5)
    T = _addon().get_max_time_steps()
    cmd = "{} -m src.make_movie -f plot_only_graph --data_in_graph {} --time_range {} --xlabel time --images_folder '{}'".format(
        bpy.context.scene.python_cmd, play_type, T, image_fol)
    print('Running {}'.format(cmd))
    # mu.run_command_in_new_thread(cmd, False)

    # if op.isfile(op.join(image_fol, 'data.pkl')):
    #     print('The file already exists!')
    #     return

    save_graph_data(graph_data, graph_colors, image_fol)


def create_movie():
    output_file = op.join(bpy.context.scene.output_path, 'combine_images_cmd.txt')
    if op.isfile(output_file):
        os.remove(output_file)
    flags = '--fol {} --copy_files 1 --frame_rate {} --add_reverse_frames {}'.format(
        bpy.context.scene.output_path, bpy.context.scene.frames_num,
        bpy.context.scene.add_reverse_frames)
    mu.run_mmvt_func('src.utils.movies_utils', 'combine_images', flags=flags)


def save_graph_data(data, graph_colors, image_fol):
    if not os.path.isdir(image_fol):
        os.makedirs(image_fol)
    mu.save((data, graph_colors), op.join(image_fol, 'data.pkl'))
    print('Saving data into {}'.format(op.join(image_fol, 'data.pkl')))


def plot_graph(context, data, graph_colors, image_fol, plot_time=False):
    if not os.path.isdir(image_fol):
        os.makedirs(image_fol)

    try:
        # http://stackoverflow.com/questions/4931376/generating-matplotlib-graphs-without-a-running-x-server/4935945#4935945
        import matplotlib as mpl
        mpl.use('Agg')
        import matplotlib.pyplot as plt

        # fig = plt.figure()
        time_range = range(_addon().get_max_time_steps())
        fig, ax1 = plt.subplots()
        axes = [ax1]
        if len(data.keys()) > 1:
            ax2 = ax1.twinx()
            axes = [ax1, ax2]
        for (data_type, data_values), ax in zip(data.items(), axes):
            for k, values in data_values.items():
                ax.plot(time_range, values, label=k, color=tuple(graph_colors[data_type][k]))
        current_t = context.scene.frame_current
        # ax = plt.gca()
        # ymin, ymax = axes[0].get_ylim()
        # plt.xlim([0, time_range[-1]])

        # Shrink current axis by 20%
        # box = ax.get_position()
        # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        # ax.legend(loc='upper center', bbox_to_anchor=(1, 0.5))

        # plt.legend(loc='best')
        plt.xlabel('Time (ms)')
        # plt.title('Coherence')
        image_fname = op.join(image_fol, 'g.{}'.format(_addon().get_figure_format()))
        fig.savefig(image_fname)
        # mu.save(ax, op.join(image_fol, 'plt.pkl'))
        # if plot_time:
        #     plt.plot([current_t, current_t], [ymin, ymax], 'g-')
        #     image_fname_t = op.join(image_fol, 'g{}.png'.format(current_t))
        #     fig.savefig(image_fname_t)
        print('saving to {}'.format(image_fname))
    except:
        print('No matplotlib!')


def plot_electrodes(cur_frame, threshold, stim=False):
    _addon().color_electrodes()


def get_meg_data(per_condition=True):
    time_range = range(_addon().get_max_time_steps())
    brain_obj = bpy.data.objects['Brain']
    if per_condition:
        meg_data, meg_colors = OrderedDict(), OrderedDict()
        rois_objs = bpy.data.objects['Cortex-lh'].children + bpy.data.objects['Cortex-rh'].children
        for roi_obj in rois_objs:
            if roi_obj.animation_data:
                meg_data_roi, meg_colors_roi = mu.evaluate_fcurves(roi_obj, time_range)
                meg_data.update(meg_data_roi)
                meg_colors.update(meg_colors_roi)
    else:
        meg_data, meg_colors = mu.evaluate_fcurves(brain_obj, time_range)
    return meg_data, meg_colors


def get_fmri_data():
    time_range = range(_addon().get_max_time_steps())
    brain_obj = bpy.data.objects['fMRI']
    data, colors = mu.evaluate_fcurves(brain_obj, time_range)
    return data, colors


def get_meg_labels_data():
    meg_data, meg_colors = OrderedDict(), OrderedDict()
    for hemi in HEMIS:
        labels_data = np.load(os.path.join(mu.get_user_fol(), 'meg', 'meg_labels_coloring_{}.npz'.format(hemi)))
        for label_data, label_colors, label_name in zip(labels_data['data'], labels_data['colors'], labels_data['names']):
            meg_data[label_name] = label_data
            meg_colors[label_name] = label_colors
    return meg_data, meg_colors


def get_connectivity_data():
    time_range = range(_addon().get_max_time_steps())
    parent_name = _addon().get_connections_parent_name()
    parent_obj = bpy.data.objects.get(parent_name)
    if not parent_obj is None:
        return mu.evaluate_fcurves(parent_obj, time_range)
    else:
        return None, None


def get_electrodes_data(per_condition=True):
    if bpy.context.scene.selection_type == 'spec_cond' and bpy.context.scene.conditions_selection == '':
        print('You must choose the condition first!')
        return None, None
    elecs_data, elecs_colors = OrderedDict(), OrderedDict()
    time_range = range(_addon().get_max_time_steps())
    if per_condition:
        for obj_name in PlayPanel.electrodes_names:
            if bpy.data.objects.get(obj_name) is None:
                continue
            elec_obj = bpy.data.objects[obj_name]
            if elec_obj.hide or elec_obj.animation_data is None:
                continue
            curr_cond = bpy.context.scene.conditions_selection if \
                bpy.context.scene.selection_type == 'spec_cond' else None
            data, colors = mu.evaluate_fcurves(elec_obj, time_range, curr_cond)
            elecs_data.update(data)
            elecs_colors.update(colors)
    else:
        parent_obj = bpy.data.objects['Deep_electrodes']
        elecs_data, elecs_colors = mu.evaluate_fcurves(parent_obj, time_range)
    return elecs_data, elecs_colors


def get_electrodes_sources_data():
    elecs_sources_data, elecs_sources_colors = OrderedDict(), OrderedDict()
    labels_data, subcortical_data = _addon().get_elecctrodes_sources()
    cond_inds = np.where(subcortical_data['conditions'] == bpy.context.scene.conditions_selection)[0]
    if len(cond_inds) == 0:
        print("!!! Can't find the current condition in the data['conditions'] !!!")
        return
    for region, color_mat, data_mat in zip(subcortical_data['names'], subcortical_data['colors'],
                                           subcortical_data['data']):
        color = color_mat[:, cond_inds[0], :]
        data = data_mat[:, cond_inds[0]]
        elecs_sources_data[region] = data
        elecs_sources_colors[region] = color
    for hemi in mu.HEMIS:
        for label, color_mat, data_mat in zip(labels_data[hemi]['names'], labels_data[hemi]['colors'],
                                              labels_data[hemi]['data']):
            color = color_mat[:, cond_inds[0], :]
            data = data_mat[:, cond_inds[0]]
            elecs_sources_data[label] = data
            elecs_sources_colors[label] = color
    return elecs_sources_data, elecs_sources_colors


def init_plotting():
    stat = 'avg' if bpy.context.scene.selection_type == 'conds' else 'diff'
    fol = op.join(mu.get_user_fol(), 'electrodes')
    bip = 'bipolar_' if bpy.context.scene.bipolar else ''
    data_meta_fname = op.join(fol, 'electrodes_{}data.npz'.format(bip))
    data_fname = op.join(fol, 'electrodes_{}data.npy'.format(bip))
    meta_fname = op.join(fol, 'electrodes_{}meta_data.npz'.format(bip))
    d = None
    if op.isfile(data_meta_fname):
        d = np.load(data_meta_fname)
        PlayPanel.electrodes_data = d['data']
        # if 'colors' in d:
        #     PlayPanel.electrodes_colors = d['colors']
    elif op.isfile(meta_fname) and op.isfile(data_fname):
        d = np.load(meta_fname)
        PlayPanel.electrodes_data = np.load(data_fname)
    #     PlayPanel.electrodes_colors = np.load(colors_fname)
    else:
        print('No electrodes data file!')
    if not d is None:
        PlayPanel.electrodes_names = [elc.astype(str) for elc in d['names']]
        data_min = np.mean(PlayPanel.electrodes_data)
        data_max = np.max(PlayPanel.electrodes_data)
        data_minmax = max(map(abs, [data_max, data_min]))
        PlayPanel.electrodes_data_max = data_minmax
        PlayPanel.electrodes_data_min = -data_minmax
        PlayPanel.electrodes_colors_ratio = 256 / (2 * data_minmax)
    # Warning: Not sure why we call this line, it changes the brain to the rendered brain
    # _addon().init_activity_map_coloring('MEG')
    PlayPanel.faces_verts = _addon().get_faces_verts()
    PlayPanel.meg_sub_activity = _addon().load_meg_subcortical_activity()
    bpy.context.scene.save_images = False
    bpy.context.scene.render_movie = False
    # connections_file = op.join(mu.get_user_fol(), 'electrodes_coh.npz')
    # if not op.isfile(connections_file):
    #     print('No connections coherence file! {}'.format(connections_file))
    # else:
    #     PlayPanel.electrodes_coherence = mu.Bag(np.load(connections_file))


def init_stim():
    stim_fname = op.join(mu.get_user_fol(), 'electrodes',
        'stim_electrodes_{}.npz'.format(bpy.context.scene.stim_files.replace(' ', '_')))
    if op.isfile(stim_fname):
        PlayPanel.stim_data = np.load(stim_fname)
        PlayPanel.electrodes_names = [elc.astype(str) for elc in PlayPanel.stim_data['names']]
        # PlayPanel.stim_colors = d['colors']
        # PlayPanel.stim_names = [elc.astype(str) for elc in d['names']]


def inflating_movie():
    _addon().hide_subcorticals()
    if _addon().flat_map_exists():
        inf_range = np.arange(-1, 1, 0.01)
    else:
        inf_range = np.arange(-1, 0, 0.01)
    for inflating in inf_range:
        bpy.context.scene.inflating = inflating
        _addon().save_image('inflating', bpy.context.scene.save_selected_view)


def slicing_movie():
    coordinates = bpy.context.scene.cursor_location
    _addon().create_slices()
    for z in np.arange(7.3, -3.6, -0.1):
        cut_pos = [0, 0, z]
        coordinates[2] = z
        _addon().slice_brain(cut_pos, save_image=True)
        _addon().clear_slice()
        _addon().create_slices(pos=coordinates)


def set_play_from(play_from):
    bpy.context.scene.frame_current = play_from
    bpy.context.scene.play_from = play_from
    bpy.data.scenes['Scene'].frame_preview_start = play_from
    ModalTimerOperator.limits = play_from


def set_play_to(play_to):
    bpy.context.scene.play_to = play_to
    bpy.data.scenes['Scene'].frame_preview_end = play_to


def set_play_dt(play_dt):
    bpy.context.scene.play_dt = play_dt


def set_play_type(play_type):
    bpy.context.scene.play_type = play_type


class PlayPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Play"
    addon = None
    init = False
    data = None
    loop_indices = None
    is_playing = False
    play_reverse = False
    first_time = True
    init_play = True
    # imp_times = [[148, 221], [247, 273], [410, 555], [903, 927]]

    def draw(self, context):
        play_panel_draw(context, self.layout)


def play_panel_draw(context, layout):
    play_type = bpy.context.scene.play_type
    if play_type in ['meg', 'meg_elecs', 'meg_elecs_coh']:
        layout.prop(context.scene, "meg_threshold", text="MEG threshold")
    if play_type in ['elecs', 'meg_elecs', 'elecs_act_coh', 'meg_elecs_coh']:
        layout.prop(context.scene, "electrodes_threshold", text="Electrodes threshold")
    if play_type in ['elecs_coh', 'elecs_act_coh', 'meg_elecs_coh']:
        layout.prop(context.scene, "connectivity_threshold", text="Conectivity threshold")

    row = layout.row(align=0)
    row.prop(context.scene, "play_from", text="From")
    row.operator(GrabFromPlay.bl_idname, text="", icon='BORDERMOVE')
    row.prop(context.scene, "play_to", text="To")
    row.operator(GrabToPlay.bl_idname, text="", icon='BORDERMOVE')
    # row = layout.row(align=0)
    layout.prop(context.scene, "play_dt", text="dt")
    # row.prop(context.scene, "play_time_step", text="time step")
    layout.prop(context.scene, "play_type", text="")
    row = layout.row(align=True)
    # row.operator(Play.bl_idname, text="", icon='PLAY' if not PlayPanel.is_playing else 'PAUSE')
    row.operator(PrevKeyFrame.bl_idname, text="", icon='PREV_KEYFRAME')
    row.operator(Reverse.bl_idname, text="", icon='PLAY_REVERSE')
    row.operator(Pause.bl_idname, text="", icon='PAUSE')
    row.operator(Play.bl_idname, text="", icon='PLAY')
    row.operator(NextKeyFrame.bl_idname, text="", icon='NEXT_KEYFRAME')
    layout.prop(context.scene, 'render_movie', text="Render to a movie")
    layout.prop(context.scene, 'save_images', text="Save images")
    layout.prop(context.scene, 'rotate_brain_while_playing', text='Rotate the brain while playing')
    if bpy.context.scene.rotate_brain_while_playing:
        row = layout.row(align=True)
        row.prop(context.scene, 'rotate_dx')
        row.prop(context.scene, 'rotate_dy')
        row.prop(context.scene, 'rotate_dz')

    row = layout.row(align=0)
    row.prop(context.scene, 'play_miscs', text='')
    row.operator(InflatingMovie.bl_idname, text="Play", icon='LOGIC')
    layout.operator(ExportGraph.bl_idname, text="Export graph", icon='SNAP_NORMAL')

    try:
        images = glob.glob(op.join(bpy.context.scene.output_path, '*.{}'.format(_addon().get_figure_format())))
        if len(images) < 2:
            images = glob.glob(op.join(bpy.context.scene.output_path, 'screencast*.jpg'))
        files_with_numbers = 0 if len(images) < 2 else sum([len(re.findall('\d+', mu.namebase(f))) for f in images])
    except:
        files_with_numbers = 0

    if files_with_numbers > 0:
        if not CreateMovie.running:
            layout.operator(CreateMovie.bl_idname, text="Create Movie", icon='RENDER_ANIMATION')
            layout.label(text='From images in {}'.format(mu.namebase(bpy.context.scene.output_path)))
            layout.prop(context.scene, 'frames_num', text="frames per second")
            layout.prop(context.scene, 'add_reverse_frames', text='add reverse loop')
        else:
            layout.label(text='Rendering the movie...')


class Play(bpy.types.Operator):
    bl_idname = "mmvt.play"
    bl_label = "play"
    bl_description = 'Play'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = True
        PlayPanel.play_reverse = False
        PlayPanel.init_play = True
        if PlayPanel.first_time:
            print('Starting the play timer!')
            # todo: why this line is marked??
            # PlayPanel.first_time = False
            ModalTimerOperator.limits = bpy.context.scene.play_from
            bpy.ops.wm.modal_timer_operator()
        return {"FINISHED"}


class Reverse(bpy.types.Operator):
    bl_idname = "mmvt.reverse"
    bl_label = "reverse"
    bl_description = 'Reverse'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = True
        PlayPanel.play_reverse = True
        if PlayPanel.first_time:
            PlayPanel.first_time = False
            PlayPanel.timer_op = bpy.ops.wm.modal_timer_operator()
        return {"FINISHED"}


class Pause(bpy.types.Operator):
    bl_idname = "mmvt.pause"
    bl_label = "pause"
    bl_description = 'Pause'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = False
        plot_something(self, context, bpy.context.scene.frame_current, ModalTimerOperator._uuid)
        print('Stop!')
        return {"FINISHED"}


class PrevKeyFrame(bpy.types.Operator):
    bl_idname = 'mmvt.prev_key_frame'
    bl_label = 'prevKeyFrame'
    bl_description = 'Previous'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = False
        bpy.context.scene.frame_current -= bpy.context.scene.play_from
        plot_something(self, context, bpy.context.scene.frame_current, ModalTimerOperator._uuid)
        return {'FINISHED'}


class NextKeyFrame(bpy.types.Operator):
    bl_idname = "mmvt.next_key_frame"
    bl_label = "nextKeyFrame"
    bl_description = 'Next'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = False
        bpy.context.scene.frame_current += bpy.context.scene.play_dt
        plot_something(self, context, bpy.context.scene.frame_current, ModalTimerOperator._uuid)
        return {"FINISHED"}


class GrabFromPlay(bpy.types.Operator):
    bl_idname = "mmvt.grab_from_play"
    bl_label = "grab from"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        set_play_from(bpy.context.scene.frame_current)
        return {"FINISHED"}


class GrabToPlay(bpy.types.Operator):
    bl_idname = "mmvt.grab_to_play"
    bl_label = "grab to"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        set_play_to(bpy.context.scene.frame_current)
        return {"FINISHED"}


class InflatingMovie(bpy.types.Operator):
    bl_idname = "mmvt.inflating_movie"
    bl_label = "mmvt inflating movie"
    bl_options = {"UNDO"}
    uuid = mu.rand_letters(5)

    @staticmethod
    def invoke(self, context, event=None):
        if bpy.context.scene.play_miscs == 'inflating':
            inflating_movie()
        elif bpy.context.scene.play_miscs == 'slicing':
            slicing_movie()
        return {"FINISHED"}


class ExportGraph(bpy.types.Operator):
    bl_idname = "mmvt.export_graph"
    bl_label = "mmvt export_graph"
    bl_options = {"UNDO"}
    uuid = mu.rand_letters(5)

    @staticmethod
    def invoke(self, context, event=None):
        capture_graph()
        return {"FINISHED"}


class CreateMovie(bpy.types.Operator):
    bl_idname = "mmvt.create_movie"
    bl_label = "mmvt create_movie"
    bl_description = 'Concatenates the frames into a video'
    bl_options = {"UNDO"}
    running = False

    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        CreateMovie.running = False
        return {'CANCELLED'}

    def invoke(self, context, event=None):
        CreateMovie.running = True
        create_movie()
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            output_file = op.join(bpy.context.scene.output_path, 'combine_images_cmd.txt')
            if op.isfile(output_file):
                movies = glob.glob(op.join(bpy.context.scene.output_path, '**', '*.mp4'), recursive=True)
                if len(movies) > 0:
                    output_fname = op.join(mu.get_user_fol(), 'figures', '{}.mp4'.format(
                        mu.namebase(bpy.context.scene.output_path)))
                    if output_fname != movies[0] and op.isfile(movies[0]):
                        shutil.copy(movies[0], output_fname)
                #     temp_fol = op.join(bpy.context.scene.output_path, 'new_images')
                #     if op.isdir(temp_fol):
                #         shutil.rmtree(temp_fol)
                self.cancel(context)
        return {'PASS_THROUGH'}


def init(addon):
    register()
    PlayPanel.addon = addon
    init_plotting()
    PlayPanel.init = True
    # print('PlayPanel initialization completed successfully!')


def register():
    try:
        unregister()
        bpy.utils.register_class(PlayPanel)
        bpy.utils.register_class(GrabFromPlay)
        bpy.utils.register_class(GrabToPlay)
        bpy.utils.register_class(Play)
        bpy.utils.register_class(Reverse)
        bpy.utils.register_class(PrevKeyFrame)
        bpy.utils.register_class(NextKeyFrame)
        bpy.utils.register_class(Pause)
        bpy.utils.register_class(ModalTimerOperator)
        bpy.utils.register_class(ExportGraph)
        bpy.utils.register_class(CreateMovie)
        bpy.utils.register_class(InflatingMovie)
        # print('PlayPanel was registered!')
    except:
        print("Can't register PlayPanel!")
        print(traceback.format_exc())


def unregister():
    try:
        bpy.utils.unregister_class(PlayPanel)
        bpy.utils.unregister_class(GrabFromPlay)
        bpy.utils.unregister_class(GrabToPlay)
        bpy.utils.unregister_class(Play)
        bpy.utils.unregister_class(Reverse)
        bpy.utils.unregister_class(PrevKeyFrame)
        bpy.utils.unregister_class(NextKeyFrame)
        bpy.utils.unregister_class(Pause)
        bpy.utils.unregister_class(ModalTimerOperator)
        bpy.utils.unregister_class(ExportGraph)
        bpy.utils.unregister_class(CreateMovie)
        bpy.utils.unregister_class(InflatingMovie)
    except:
        pass
        # print("Can't unregister PlayPanel!")
        # print(traceback.format_exc())