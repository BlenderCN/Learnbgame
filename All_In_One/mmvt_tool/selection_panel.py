import bpy
import mmvt_utils as mu
import numpy as np
import os.path as op
from functools import partial

SEL_ROIS, SEL_FUNC_ROIS, SEL_SUBS, SEL_ELECTRODES, SEL_MEG_SENSORS, SEL_EEG_SENSORS, SEL_CONNECTIONS = range(7)

def _addon():
    return SelectionMakerPanel.addon


def conditions_diff():
    return bpy.context.scene.selection_type == 'diff'


def both_conditions():
    return bpy.context.scene.selection_type == 'conds'


def spec_condition():
    return bpy.context.scene.selection_type == 'spec_cond'


def fit_selection(context=None):
    mu.view_all_in_graph_editor(context)


def deselect_all():
    for obj in bpy.data.objects:
        obj.select = False
    if bpy.data.objects.get(' '):
        bpy.data.objects[' '].select = True
        bpy.context.scene.objects.active = bpy.data.objects[' ']


def get_selected_fcurves_and_data():
    # todo: support more than one type in selection
    all_fcurves, all_data = [], []
    for selction_type, parent_obj in zip([SEL_ELECTRODES, SEL_ROIS, SEL_FUNC_ROIS],
                                         [_addon().electrodes_panel_parent, '', _addon().meg_panel_parent]):
        if selction_type not in SelectionMakerPanel.get_data:
            continue
        # fcurves = mu.get_fcurves(parent_obj, recursive=True, only_selected=True)
        fcurves = SelectionMakerPanel.fcurves[selction_type]()
        if fcurves is None or len(fcurves) == 0:
            continue
        data, names, conditions = SelectionMakerPanel.get_data[selction_type]()
        # try:
        #     conditions = mu.get_animation_conditions(bpy.data.objects[names[0]])
        # except:
        #     conditions = None
        # if conditions is None:
        #     conditions = _conditions
        if data is None:
            continue
        fcurves_names = set([mu.get_fcurve_name(f) for f in fcurves])
        # todo: fix that for rois!
        # if mu.if_cond_is_diff(parent_obj):
        #     if data.ndim == 3:
        #         data = np.diff(data, axis=2)
        #     selected_indices = [ind for ind, name in enumerate(names) if name in fcurves_names]
        # else:
        if selction_type != SEL_FUNC_ROIS:
            selected_indices = [ind for ind, name in enumerate(names)
                                if any(['{}_{}'.format(name, cond) in fcurves_names for cond in conditions])]
            if len(selected_indices) == 0:
                continue
            data = data[selected_indices]
        all_fcurves.extend(fcurves)
        all_data = data if all_data == [] else np.concatenate((all_data, data))
    return all_fcurves, all_data


def curves_sep_update(self=None, context=None):
    if SelectionMakerPanel.update_curves_sep:
        _curves_sep_update(False)


def _curves_sep_update(force=False):
    # if len(bpy.context.selected_objects) == 1:
    #     return
    fcurves, data = get_selected_fcurves_and_data()
    if len(fcurves) == 0:
        return
    data = data.squeeze()
    if data.ndim == 3:
        N, T, C = data.shape
        get_data = lambda ind, t, c: data[data_ind, t, c]
    elif data.ndim == 2:
        N, T = data.shape
        if N - 10 < len(fcurves[0].keyframe_points) < N + 10:
            N, T = T, N
            # switch dims
            data = data.T
        C = 1
        get_data = lambda ind, t, c: data[data_ind, t]
    elif data.ndim == 1:
        T = len(data)
        N, C = 1, 1
        get_data = lambda ind, t, c: data[t]
    else:
        print('_curves_sep_update: Wrong number dims!')
    sep_inds = np.tile(np.arange(0, N), (C, 1)).T.ravel()
    for data_ind in range(N):
        fcurve_ind = 0
        data_mean = np.median(data[data_ind]) if bpy.context.scene.curves_sep > 0 else 0
        for c in range(C):
            fcurve = fcurves[fcurve_ind]
            fcurve_T = min(T, len(fcurve.keyframe_points)) - 1
            if not force and SelectionMakerPanel.curves_sep.get(mu.get_fcurve_name(fcurve), -1) == \
                    bpy.context.scene.curves_sep:
                fcurve_ind += 1
                continue
            for t in range(fcurve_T):
                fcurve.keyframe_points[t].co[1] = \
                    get_data(data_ind, t, c) - data_mean + (N / 2 - 0.5 - sep_inds[fcurve_ind]) * bpy.context.scene.curves_sep
            fcurve_ind += 1
            if bpy.context.scene.curves_sep == 0:
                fcurve.keyframe_points[0].co[1] = fcurve.keyframe_points[fcurve_T].co[1] = 0
    for fcurve in fcurves:
        SelectionMakerPanel.curves_sep[mu.get_fcurve_name(fcurve)] = bpy.context.scene.curves_sep
    # mu.change_fcurves_colors(fcurves=fcurves)
    mu.view_all_in_graph_editor()


@mu.tryit()
def maximize_graph():
    context = mu.get_graph_context()
    bpy.ops.screen.screen_full_area(context)


@mu.tryit()
def minimize_graph():
    context = mu.get_graph_context()
    bpy.ops.screen.back_to_previous(context)


def calc_best_curves_sep(norm_percs=[3, 97]):
    fcurves, data = get_selected_fcurves_and_data()
    try:
        if data.shape[0] == 1:
            bpy.context.scene.curves_sep = 0
        else:
            bpy.context.scene.curves_sep = _calc_best_curves_sep(data, norm_percs)
            bpy.context.scene.curves_sep += 0.001
    except:
        pass


def _calc_best_curves_sep(data, norm_percs=[3, 97]):
    if len(data) == 0:
        return 0
    try:
        max_diff = max([np.diff(mu.calc_min_max(data[k], norm_percs=norm_percs))[0] for k in range(data.shape[0])])
        return max_diff * 1.1
    except:
        print('Error in _calc_best_curves_sep')
        return 0


def meg_data_loaded():
    parent_obj = bpy.data.objects.get('Brain')
    if parent_obj is None:
        return False
    else:
        parent_data = mu.count_fcurves(parent_obj) > 0
        if bpy.data.objects.get('Cortex-lh') and bpy.data.objects.get('Cortex-rh'):
            labels = bpy.data.objects['Cortex-lh'].children + bpy.data.objects['Cortex-rh'].children
            labels_data = mu.count_fcurves(labels) > 0
            return parent_data or labels_data
        else:
            return False


def meg_sub_data_loaded():
    parent_obj = bpy.data.objects.get('Subcortical_structures')
    if parent_obj is None:
        return False
    else:
        parent_data = mu.count_fcurves(parent_obj) > 0
        labels_data = mu.count_fcurves(parent_obj.children) > 0
        return parent_data or labels_data


def fmri_data_loaded():
    fmri_parent_obj = bpy.data.objects.get('fMRI')
    return mu.count_fcurves(fmri_parent_obj) > 0


def electrodes_exist():
    try:
        electrodes_obj = bpy.data.objects.get(_addon().electrodes_panel_parent)
        return electrodes_obj is not None and len(electrodes_obj.children) > 0
    except:
        return False


def electrodes_data_loaded():
    try:
        electrodes_obj = bpy.data.objects.get(_addon().electrodes_panel_parent)
        return electrodes_obj is not None and mu.count_fcurves(electrodes_obj, recursive=True) > 0
    except:
        return False


def meg_clusters_data_loaded():
    try:
        meg_clusters_obj = bpy.data.objects.get(_addon().meg_panel_parent)
        return meg_clusters_obj is not None and mu.count_fcurves(meg_clusters_obj, recursive=True) > 0
    except:
        return False


def select_roi(roi_name, change_selected_fcurves_colors=True):
    roi = bpy.data.objects.get(roi_name)
    if roi is None:
        return

    # check if MEG data is loaded and attahced to the obj
    if mu.count_fcurves(roi) > 0:
        roi.select = True
        labels_selection_coloring(roi_name)
        # mu.change_fcurves_colors(roi)
    else:
        # Check if dynamic fMRI data is loaded
        fmri_parent_obj = bpy.data.objects.get('fMRI')
        fcurves = mu.get_fcurves(fmri_parent_obj)
        for fcurve in fcurves:
            if mu.get_fcurve_name(fcurve) == roi_name:
                fcurve.hide = False
                fmri_parent_obj.select = True
            else:
                fcurve.hide = True
    if change_selected_fcurves_colors:
        mu.change_selected_fcurves_colors(mu.OBJ_TYPES_ROIS)
    mu.view_all_in_graph_editor()


def labels_selection_coloring(current_label):
    selected_labels = get_selected_labels()
    # Check if it's a new selection:
    if len(selected_labels) == 1 and current_label not in SelectionMakerPanel.prev_labels:
        # Clear and init prev_labels
        unselect_prev_label(SelectionMakerPanel.prev_labels)
        SelectionMakerPanel.prev_labels = set([current_label])
    # Check if this is a new labels where the shift is pressed
    elif len(selected_labels) > 1 and current_label not in SelectionMakerPanel.prev_labels:
        # Add current label to prev_labels
        SelectionMakerPanel.prev_labels.add(current_label)
    # Check if the user unselect one of the selected labels
    elif len(selected_labels) > 1 and current_label in SelectionMakerPanel.prev_labels:
        bpy.data.objects[current_label].select = False
        unselect_prev_label([current_label])
        SelectionMakerPanel.prev_labels.remove(current_label)
    else:
        clear_labels_selection()


def get_selected_labels():
    return [obj.name for obj in bpy.context.selected_objects if
            mu.check_obj_type(obj.name) in [mu.OBJ_TYPE_CORTEX_RH, mu.OBJ_TYPE_CORTEX_LH]]


def unselect_prev_label(prev_labels):
    for prev_label in prev_labels:
        prev_elc = bpy.data.objects.get(prev_label)
        if not prev_elc is None:
            de_select_object(prev_elc)


def clear_selection():
    for sub_hierchy in bpy.data.objects['Brain'].children:
        for obj in sub_hierchy.children:
            de_select_object(obj)

    if bpy.data.objects.get('Deep_electrodes'):
        for obj in bpy.data.objects['Deep_electrodes'].children:
            obj.active_material.node_tree.nodes["Layer Weight"].inputs[0].default_value = 1
            _addon().object_coloring(obj, (1, 1, 1, 1))


def de_select_object(obj):
    if isinstance(obj, str):
        obj = bpy.data.objects[obj]
    try:
        obj.active_material.node_tree.nodes["RGB"].outputs[0].default_value = (1, 1, 1, 1)
    except:
        pass
    try:
        obj.active_material.diffuse_color = (1, 1, 1)
    except:
        pass


def clear_labels_selection():
    unselect_prev_label(SelectionMakerPanel.prev_labels)
    SelectionMakerPanel.prev_labels = set()


def select_all_rois():
    mu.unfilter_graph_editor()
    fmri_parent = bpy.data.objects.get('fMRI')
    if mu.count_fcurves(bpy.data.objects['Brain']) > 0:
        bpy.context.scene.filter_curves_type = 'MEG'
        select_brain_objects('Brain', bpy.data.objects['Cortex-lh'].children + bpy.data.objects['Cortex-rh'].children)
    elif not fmri_parent is None:
        bpy.context.scene.filter_curves_type = 'fMRI'
        select_brain_objects('fMRI')
        # fmri_parent.select = True
        # mu.show_hide_obj_and_fcurves(fmri_parent, True)


def select_only_subcorticals():
    mu.unfilter_graph_editor()
    bpy.context.scene.filter_curves_type = 'MEG'
    select_brain_objects('Subcortical_structures')


def select_all_meg_sensors():
    mu.unfilter_graph_editor()
    bpy.context.scene.filter_curves_type = 'MEG_sensors'
    select_brain_objects('MEG_sensors')


def select_all_eeg_sensors():
    mu.unfilter_graph_editor()
    bpy.context.scene.filter_curves_type = 'EEG'
    select_brain_objects('EEG_sensors')


def select_all_electrodes():
    parent_obj = bpy.data.objects['Deep_electrodes']
    mu.unfilter_graph_editor()
    bpy.context.scene.filter_curves_type = 'Electrodes'
    if 'ELECTRODES' in _addon().settings.sections():
        config = _addon().settings['ELECTRODES']
        bad = mu.get_args_list(config.get('bad', ''))
    else:
        bad = []
    select_brain_objects('Deep_electrodes', exclude=bad)
    mu.unfilter_graph_editor()
    if bpy.context.scene.selection_type == 'diff':
        mu.change_fcurves_colors([parent_obj], bad)
    elif bpy.context.scene.selection_type == 'spec_cond':
        mu.filter_graph_editor(bpy.context.scene.conditions_selection)
    else:
        mu.change_fcurves_colors(parent_obj.children, bad)

    # curves_sep_update()


def select_all_connections():
    mu.unfilter_graph_editor()
    connection_parent_name = _addon().get_connections_parent_name()
    select_brain_objects(connection_parent_name)


def conditions_selection_update(self, context):
    mu.filter_graph_editor(bpy.context.scene.conditions_selection)
    _addon().clear_and_recolor()


def select_brain_objects(parent_obj_name, children=None, exclude=[]):
    if children is None:
        children = bpy.data.objects[parent_obj_name].children
    parent_obj = bpy.data.objects[parent_obj_name]
    children_have_fcurves = mu.count_fcurves(children) > 0
    parent_have_fcurves = not parent_obj.animation_data is None
    if parent_have_fcurves and (bpy.context.scene.selection_type == 'diff' or not children_have_fcurves):
        mu.show_hide_obj_and_fcurves(children, False)
        parent_obj.select = True
        mu.show_hide_obj_and_fcurves(parent_obj, True, exclude)
    elif children_have_fcurves:
        if bpy.context.scene.selection_type == 'diff':
            bpy.context.scene.selection_type = 'conds'
        mu.show_hide_obj_and_fcurves(children, True, exclude)
        parent_obj.select = False
    mu.view_all_in_graph_editor()


def set_conditions_enum(conditions):
    conditions = mu.unique_save_order(conditions)
    selection_items = [(c, '{}'.format(c), '', ind) for ind, c in enumerate(conditions)]
    try:
        bpy.types.Scene.conditions_selection = bpy.props.EnumProperty(
            items=selection_items, description="Condition Selection", update=conditions_selection_update)
    except:
        print("Cant register conditions_selection!")


def set_selection_type(selection_type):
    bpy.context.scene.selection_type = selection_type


class SelectAllRois(bpy.types.Operator):
    bl_idname = "mmvt.roi_selection"
    bl_label = "select2 ROIs"
    bl_description = 'Selects all ROIs. \n\nScript: mmvt.selection.select_all_rois()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        select_all_rois()
        SelectionMakerPanel.selection.append(SEL_ROIS)
        mu.view_all_in_graph_editor(context)
        if bpy.context.scene.selection_type == 'diff':
            mu.change_fcurves_colors([bpy.data.objects['Brain']])
        else:
            corticals_labels = mu.get_corticals_labels()
            mu.change_fcurves_colors(corticals_labels)
        return {"FINISHED"}


class SelectAllSubcorticals(bpy.types.Operator):
    bl_idname = "mmvt.subcorticals_selection"
    bl_label = "select only subcorticals"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        select_only_subcorticals()
        SelectionMakerPanel.selection.append(SEL_SUBS)
        mu.view_all_in_graph_editor(context)
        if bpy.context.scene.selection_type == 'diff':
            mu.change_fcurves_colors([bpy.data.objects['Subcortical_structures']])
        else:
            mu.change_fcurves_colors(bpy.data.objects['Subcortical_structures'].children)
        return {"FINISHED"}


class SelectAllMEGSensors(bpy.types.Operator):
    bl_idname = "mmvt.meg_sensors_selection"
    bl_label = "select meg sensors"
    bl_description = 'Selects all the MEG sensors to show their data. \n\nScript: mmvt.selection.select_meg_sensors()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        select_all_meg_sensors()
        SelectionMakerPanel.selection.append(SEL_MEG_SENSORS)
        mu.unfilter_graph_editor()
        mu.change_fcurves_colors(bpy.data.objects['MEG_sensors'].children)
        mu.view_all_in_graph_editor(context)
        return {"FINISHED"}


class SelectAllEEG(bpy.types.Operator):
    bl_idname = "mmvt.eeg_selection"
    bl_label = "select eeg"
    bl_description = 'Selects all the EEG sensors to show their data. \n\nScript: mmvt.selection.select_eeg_sensors()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        select_all_eeg_sensors()
        SelectionMakerPanel.selection.append(SEL_EEG_SENSORS)
        mu.unfilter_graph_editor()
        # if bpy.context.scene.selection_type == 'diff':
        #     mu.change_fcurves_colors([bpy.data.objects['Deep_electrodes']])
        # elif bpy.context.scene.selection_type == 'spec_cond':
        #     mu.filter_graph_editor(bpy.context.scene.conditions_selection)
        # else:
        mu.change_fcurves_colors(bpy.data.objects['EEG_sensors'].children)
        mu.view_all_in_graph_editor(context)
        return {"FINISHED"}


class SelectAllElectrodes(bpy.types.Operator):
    bl_idname = "mmvt.electrodes_selection"
    bl_label = "select2 Electrodes"
    bl_description = 'Selects all the electrodes to show their data. \n\nScript: mmvt.selection.select_all_electrodes()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        select_all_electrodes()
        SelectionMakerPanel.selection.append(SEL_ELECTRODES)
        # curves_sep_update()
        mu.view_all_in_graph_editor(context)
        return {"FINISHED"}


class SelectAllConnections(bpy.types.Operator):
    bl_idname = "mmvt.connections_selection"
    bl_label = "select connections"
    bl_description = 'Selects all connections. \n\nScript: mmvt.selection.select_all_connections()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        select_all_connections()
        SelectionMakerPanel.selection.append(SEL_CONNECTIONS)
        mu.view_all_in_graph_editor(context)
        return {"FINISHED"}


class ClearSelection(bpy.types.Operator):
    bl_idname = "mmvt.clear_selection"
    bl_label = "deselect all"
    bl_description = 'Deselects all the selected data'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        for obj in bpy.data.objects:
            obj.select = False
        if bpy.data.objects.get(' '):
            bpy.data.objects[' '].select = True
            bpy.context.scene.objects.active = bpy.data.objects[' ']
        SelectionMakerPanel.selection = []
        try:
            if bpy.data.objects.get('Deep_electrodes'):
                for obj in bpy.data.objects['Deep_electrodes'].children:
                    obj.active_material.node_tree.nodes["Layer Weight"].inputs[0].default_value = 1
                    _addon().object_coloring(obj, (1, 1, 1, 1))
            # _addon().clear_electrodes_selection()
        except:
            pass
        try:
            clear_labels_selection()
        except:
            pass
        return {"FINISHED"}


class FitSelection(bpy.types.Operator):
    bl_idname = "mmvt.fit_selection"
    bl_label = "Fit selection"
    bl_description = 'Scales the graph to fit the window optimally. \n\nScript: mmvt.selection.fit_selection()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        fit_selection(context)
        return {"FINISHED"}


# class ResetCurvesFilter(bpy.types.Operator):
#     bl_idname = "mmvt.reset_curves_filter"
#     bl_label = "reset_curves_filter"
#     bl_options = {"UNDO"}
#
#     @staticmethod
#     def invoke(self, context, event=None):
#         bpy.context.scene.filter_fcurves = ''
#         return {"FINISHED"}


class ResetCurvesSep(bpy.types.Operator):
    bl_idname = "mmvt.reset_curves_sep"
    bl_label = "reset_curves_sep"
    bl_description = 'Restarts the curves separation'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        SelectionMakerPanel.update_curves_sep = False
        bpy.context.scene.curves_sep = 0
        SelectionMakerPanel.update_curves_sep = True
        _curves_sep_update(True)
        return {"FINISHED"}


class CalcBestCurvesSep(bpy.types.Operator):
    bl_idname = "mmvt.calc_best_curves_sep"
    bl_label = "calc_best_curves_sep"
    bl_description = 'Separates automatically the best distance between the curves in the graph. ' \
                     '\n\nScript: mmvt.selection.calc_best_curves_sep()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        calc_best_curves_sep()
        return {"FINISHED"}


class MaxMinGraphPanel(bpy.types.Operator):
    bl_idname = "mmvt.max_min_graph_panel"
    bl_label = "max_min_graph_panel"
    bl_description = 'Scales the graph to fit the window optimally. \n\nScript: mmvt.selection.maximize_graph() ' \
                     'and mmvt.selection.minimize_graph()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        if bpy.context.scene.graph_max_min:
            maximize_graph()
        else:
            minimize_graph()
        bpy.context.scene.graph_max_min = not bpy.context.scene.graph_max_min
        return {"FINISHED"}


class PrevWindow(bpy.types.Operator):
    bl_idname = "mmvt.prev_window"
    bl_label = "prev window"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.current_window_selection -= 1
        change_window()
        return {"FINISHED"}


class NextWindow(bpy.types.Operator):
    bl_idname = "mmvt.next_window"
    bl_label = "next window"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.current_window_selection += 1
        change_window()
        return {"FINISHED"}


class JumpToWindow(bpy.types.Operator):
    bl_idname = "mmvt.jump_to_window"
    bl_label = "jump to window"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        change_window()
        return {"FINISHED"}


def change_window():
    import time
    # todo: check what kind of data is displayed in the graph panel
    data_type = 'eeg'
    change = True
    if data_type == 'eeg':
        now = time.time()
        data, meta = _addon().eeg_data_and_meta()
        obj_name = 'EEG_sensors'
        ch_names = meta['names']
        points_in_sec = int(1 / meta['dt'])
        window_len = get_window_length(obj_name)
        new_point_in_time = bpy.context.scene.current_window_selection * points_in_sec
        #todo: add a factor field
        factor = 1000
        new_data = data[:, new_point_in_time:new_point_in_time + window_len - 1] * factor
        print('{} took {:.6f}s'.format('loading', time.time() - now))

    else:
        change = False
    if change:
        mu.change_fcurves(obj_name, new_data, ch_names)
        bpy.data.scenes['Scene'].frame_preview_start = 0
        bpy.data.scenes['Scene'].frame_preview_end = window_len


def get_window_length(obj_name):
    try:
        parent_obj = bpy.data.objects[obj_name]
        fcurve = parent_obj.animation_data.action.fcurves[0]
        N = len(fcurve.keyframe_points)
    except:
        N = 2000
    return N


# def subselect_update(self=None, context=None):
#     mu.filter_graph_editor(context.scene.filter_fcurves)
    # context.screen.areas[0].spaces[0].dopesheet.filter_fcurve_name = context.scene.filter_fcurves


bpy.types.Scene.selection_type = bpy.props.EnumProperty(
    items=[("diff", "Conditions difference", "", 1), ("conds", "All conditions", "", 2)],
    description='Selects the condition that will be displayed. \n\nScript: set_selection_type()\n\nCondition')
           # ("spec_cond", "Specific condition", "", 3)], description="Selection type")
bpy.types.Scene.conditions_selection = bpy.props.EnumProperty(items=[], description="Condition Selection",
                                                              update=conditions_selection_update)
bpy.types.Scene.current_window_selection = bpy.props.IntProperty(min=0, default=0, max=1000, description="")
bpy.types.Scene.selected_modlity = bpy.props.EnumProperty(items=[])
bpy.types.Scene.fit_graph_on_selection = bpy.props.BoolProperty(description='Scales optimally the graph upon selection')
bpy.types.Scene.graph_max_min = bpy.props.BoolProperty()
bpy.types.Scene.curves_sep = bpy.props.FloatProperty(default=0, min=0, update=curves_sep_update,
    description='Separates the curves in the graph')
bpy.types.Scene.find_curves_sep_auto = bpy.props.BoolProperty(
    description='When checked separates automatically the best distance between the curves in the graph')
# bpy.types.Scene.filter_fcurves = bpy.props.StringProperty(name="Subselect:", update=subselect_update)


def get_dt():
    #todo: check what is in the graph panel
    data_type = 'eeg'
    if data_type == 'eeg':
        _, meta = _addon().eeg_data_and_meta()
        return meta['dt'] if meta and 'dt' in meta else None
    else:
        return None


class SelectionMakerPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Selection"
    addon = None
    init = False
    modalities_num = 0
    connection_files_exist = False
    data, names, curves_sep, fcurves = {}, {}, {}, {}
    prev_labels = set()
    update_curves_sep = True

    @staticmethod
    def draw(self, context):
        layout = self.layout
        # if bpy.context.scene.selection_type == 'spec_cond':
        #     layout.prop(context.scene, "conditions_selection", text="")
        # labels_data = ''
        # fmri_parent = bpy.data.objects.get('fMRI')
        # if mu.count_fcurves(bpy.data.objects['Brain']) > 0:
        #     labels_data = 'MEG'
        # elif not fmri_parent is None:
        #     labels_data = 'fMRI'
        layout.prop(context.scene, "selection_type", text="")
        sm = ''
        if SelectionMakerPanel.modalities_num > 0:
            sm = bpy.context.scene.selected_modlity
        if SelectionMakerPanel.modalities_num > 1:
            layout.prop(context.scene, 'selected_modlity', text='')
        if meg_data_loaded() or fmri_data_loaded():
            layout.operator(SelectAllRois.bl_idname, text="Cortical labels ({})".format(sm), icon='BORDER_RECT')
        if meg_sub_data_loaded() or fmri_data_loaded():
            layout.operator(SelectAllSubcorticals.bl_idname, text="Subcorticals ({})".format(sm), icon = 'BORDER_RECT')
        if electrodes_data_loaded() or electrodes_exist():
            layout.operator(SelectAllElectrodes.bl_idname, text="Electrodes", icon='BORDER_RECT')
        if bpy.data.objects.get('MEG_sensors'):
            layout.operator(SelectAllMEGSensors.bl_idname, text="MEG sensors", icon='BORDER_RECT')
        if bpy.data.objects.get('EEG_sensors'):
            layout.operator(SelectAllEEG.bl_idname, text="EEG sensors", icon='BORDER_RECT')
        if SelectionMakerPanel.connection_files_exist:
            layout.operator(SelectAllConnections.bl_idname, text="Connections", icon='BORDER_RECT')

        layout.operator(ClearSelection.bl_idname, text="Deselect all", icon='PANEL_CLOSE')
        layout.operator(FitSelection.bl_idname, text="Fit graph window", icon='MOD_ARMATURE')
        row = layout.row(align=True)
        row.prop(context.scene, 'curves_sep', text='curves separation')
        row.operator(CalcBestCurvesSep.bl_idname, text="Calc best curves sep", icon='RNA_ADD')
        row.operator(ResetCurvesSep.bl_idname, text="", icon='PANEL_CLOSE')
        layout.prop(context.scene, 'fit_graph_on_selection', text='Fit graph on selection')
        layout.prop(context.scene, 'find_curves_sep_auto', text='Always find the best curves separation')
        layout.operator(MaxMinGraphPanel.bl_idname,
                        text="{} graph".format('Maximize' if bpy.context.scene.graph_max_min else 'Minimize'),
                        icon='TRIA_UP' if bpy.context.scene.graph_max_min else 'TRIA_DOWN')
        # row = layout.row(align=True)
        # row.prop(context.scene, "filter_fcurves", text="Filter curves")
        # row.operator(ResetCurvesFilter.bl_idname, text="", icon='PANEL_CLOSE')

        # if not SelectionMakerPanel.dt is None:
        #     points_in_sec = int(1 / SelectionMakerPanel.dt)
        #     window_from = bpy.context.scene.current_window_selection * points_in_sec / 1000
        #     window_to =  window_from + points_in_sec * 2 / 1000
        #
        #     layout.label(text='From {:.2f}s to {:.2f}s'.format(window_from, window_to))
        #     row = layout.row(align=True)
        #     # row.operator(Play.bl_idname, text="", icon='PLAY' if not PlayPanel.is_playing else 'PAUSE')
        #     row.operator(PrevWindow.bl_idname, text="", icon='PREV_KEYFRAME')
        #     row.operator(NextWindow.bl_idname, text="", icon='NEXT_KEYFRAME')
        #     row.prop(context.scene, 'current_window_selection', text='window')
        #     row.operator(JumpToWindow.bl_idname, text='Jump', icon='DRIVER')


def init(addon):
    SelectionMakerPanel.addon = addon
    SelectionMakerPanel.update_curves_sep = False
    SelectionMakerPanel.selection = []
    SelectionMakerPanel.dt = get_dt()
    modalities_itesm = []
    if meg_data_loaded():
        modalities_itesm.append(('MEG', 'MEG', '', 0))
    if fmri_data_loaded():
        modalities_itesm.append(('fMRI', 'fMRI', '', 1))
    SelectionMakerPanel.modalities_num = len(modalities_itesm)
    bpy.types.Scene.selected_modlity = bpy.props.EnumProperty(items=modalities_itesm)
    # SelectionMakerPanel.connection_files_exist = bpy.data.objects.get(_addon().get_connections_parent_name()) and \
    #             bpy.data.objects[_addon().get_connections_parent_name()].animation_data
    get_data()
    bpy.context.scene.fit_graph_on_selection = False
    bpy.context.scene.graph_max_min = True
    bpy.context.scene.curves_sep = 0
    bpy.context.scene.find_curves_sep_auto = True
    SelectionMakerPanel.init = True
    SelectionMakerPanel.update_curves_sep = True
    register()


def set_connection_files_exist(val=True):
    SelectionMakerPanel.connection_files_exist = val


def get_rois_fcruves():
    return  mu.get_fcurves('Brain', recursive=False, only_selected=True) + \
            mu.get_fcurves('Cortex-lh', recursive=True, only_selected=True) + \
            mu.get_fcurves('Cortex-rh', recursive=True, only_selected=True)


def get_data():
    SelectionMakerPanel.get_data = {}
    if meg_data_loaded():
        SelectionMakerPanel.get_data[SEL_ROIS] = _addon().load_meg_labels_data
        SelectionMakerPanel.fcurves[SEL_ROIS] = get_rois_fcruves
    if fmri_data_loaded():
        pass
    if meg_sub_data_loaded():
        pass
    if fmri_data_loaded():
        pass
    if electrodes_data_loaded():
        SelectionMakerPanel.get_data[SEL_ELECTRODES] = _addon().load_electrodes_data
        SelectionMakerPanel.fcurves[SEL_ELECTRODES] = \
            partial(mu.get_fcurves, obj=_addon().electrodes_panel_parent, recursive=True, only_selected=True)
    if meg_clusters_data_loaded():
        SelectionMakerPanel.get_data[SEL_FUNC_ROIS] = _addon().get_selected_clusters_data
        SelectionMakerPanel.fcurves[SEL_FUNC_ROIS] = \
            partial(mu.get_fcurves, obj=_addon().meg_panel_parent, recursive=True, only_selected=True, only_not_hiden=True)

    if bpy.data.objects.get('MEG_sensors'):
        pass
    if bpy.data.objects.get('EEG_sensors'):
        pass


def register():
    try:
        unregister()
        bpy.utils.register_class(SelectionMakerPanel)
        bpy.utils.register_class(FitSelection)
        bpy.utils.register_class(ClearSelection)
        bpy.utils.register_class(SelectAllConnections)
        bpy.utils.register_class(SelectAllElectrodes)
        bpy.utils.register_class(SelectAllEEG)
        bpy.utils.register_class(SelectAllMEGSensors)
        bpy.utils.register_class(SelectAllSubcorticals)
        bpy.utils.register_class(SelectAllRois)
        bpy.utils.register_class(CalcBestCurvesSep)
        bpy.utils.register_class(ResetCurvesSep)
        # bpy.utils.register_class(ResetCurvesFilter)
        bpy.utils.register_class(MaxMinGraphPanel)
        bpy.utils.register_class(NextWindow)
        bpy.utils.register_class(PrevWindow)
        bpy.utils.register_class(JumpToWindow)
        # print('Selection Panel was registered!')
    except:
        print("Can't register Selection Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(SelectionMakerPanel)
        bpy.utils.unregister_class(FitSelection)
        bpy.utils.unregister_class(ClearSelection)
        bpy.utils.unregister_class(SelectAllConnections)
        bpy.utils.unregister_class(SelectAllElectrodes)
        bpy.utils.unregister_class(SelectAllEEG)
        bpy.utils.unregister_class(SelectAllMEGSensors)
        bpy.utils.unregister_class(SelectAllSubcorticals)
        bpy.utils.unregister_class(SelectAllRois)
        bpy.utils.unregister_class(CalcBestCurvesSep)
        bpy.utils.unregister_class(ResetCurvesSep)
        # bpy.utils.unregister_class(ResetCurvesFilter)
        bpy.utils.unregister_class(MaxMinGraphPanel)
        bpy.utils.unregister_class(NextWindow)
        bpy.utils.unregister_class(PrevWindow)
        bpy.utils.unregister_class(JumpToWindow)
    except:
        pass
