import bpy
import numpy as np
import os.path as op
import time
import mmvt_utils as mu
import colors_utils as cu
import glob

# try:
#     import matplotlib as mpl
#     mpl.use('Agg')
#     import matplotlib.pyplot as plt
# except ImportError:
#     print('No matplotlib!')

# PARENT_OBJ = 'connections'
HEMIS_WITHIN, HEMIS_BETWEEN = range(2)
STAT_AVG, STAT_DIFF = range(2)


def _addon():
    return ConnectionsPanel.addon


def get_connections_parent_name():
    if ConnectionsPanel.connections_files_exist:
        return 'connections_{}'.format(bpy.context.scene.connectivity_files.replace(' ', '_'))
    else:
        return 'no-connections'


def get_first_existing_parent_obj_name():
    for con_name in ConnectionsPanel.conn_names:
        if connections_exist(con_name):
            return con_name
    return ''


def connections_exist(parent_name=''):
    if parent_name == '':
        parent_name = get_connections_parent_name()
    else:
        parent_name = parent_name.replace(' ', '_')
    return not bpy.data.objects.get(parent_name, None) is None


def get_connections_data():
    return ConnectionsPanel.d


def select_connection(connection_name):
    fcurves = mu.get_fcurves(connection_name)
    for fcurve in fcurves:
        fcurve.hide = False
        fcurve.select = True
    mu.view_all_in_graph_editor()


def check_connections(stat=STAT_DIFF):
    # d = load_connections_file()
    d = ConnectionsPanel.d
    if d is None:
        print('No connection file!')
        return None
    threshold = bpy.context.scene.connections_threshold
    threshold_type = bpy.context.scene.connections_threshold_type
    if d.con_values.ndim >= 2:
        windows_num = d.con_values.shape[1]
    else:
        windows_num = 1
    if d.con_values.ndim > 2 and d.con_values.shape[2] > 1:
        stat_data = calc_stat_data(d.con_values, stat)
    else:
        stat_data = d.con_values
    mask = calc_mask(stat_data, threshold, threshold_type, windows_num)
    indices = np.where(mask)[0]
    parent_obj = bpy.data.objects.get(get_connections_parent_name(), None)
    if parent_obj and len(parent_obj.children) > 0:
        bpy.context.scene.connections_num = min(len(parent_obj.children) - 1, len(indices))
    else:
        bpy.context.scene.connections_num = len(indices)
    parent_obj = bpy.data.objects.get(get_connections_parent_name(), None)
    if parent_obj:
        ConnectionsPanel.selected_objects, ConnectionsPanel.selected_indices = get_all_selected_connections(d)
        if len(ConnectionsPanel.selected_objects) > 0:
            bpy.context.scene.connections_min = np.min(d.con_values[ConnectionsPanel.selected_indices])
            bpy.context.scene.connections_max = np.max(d.con_values[ConnectionsPanel.selected_indices])
        else:
            bpy.context.scene.connections_min = np.min(d.con_values[indices]) if len(indices) > 0 else d['data_min']
            bpy.context.scene.connections_max = np.max(d.con_values[indices]) if len(indices) > 0 else d['data_max']
    else:
        bpy.context.scene.connections_min = np.min(d.con_values[indices]) if len(indices) > 0 else d['data_min']
        bpy.context.scene.connections_max = np.max(d.con_values[indices]) if len(indices) > 0 else d['data_max']
    return d


# d(Bag): labels, locations, hemis, con_colors (L, W, 2, 3), con_values (L, W, 2), indices, con_names, conditions
def create_keyframes(d, threshold, threshold_type, radius=.1, stat=STAT_DIFF, verts_color='pink'):
    layers_rods = [False] * 20
    rods_layer = _addon().CONNECTIONS_LAYER
    layers_rods[rods_layer] = True
    mu.delete_hierarchy(get_connections_parent_name())
    mu.create_empty_if_doesnt_exists(get_connections_parent_name(), _addon().BRAIN_EMPTY_LAYER, None, 'Functional maps')
    d.con_values = d.con_values.squeeze()
    if d.con_values.ndim >= 2:
        windows_num = d.con_values.shape[1]
    else:
        windows_num = 1
    T = ConnectionsPanel.addon.get_max_time_steps(windows_num)
    if T == 0:
        T = windows_num
    norm_fac = T / windows_num
    if d.con_values.ndim > 2:
        stat_data = calc_stat_data(d.con_values, stat)
    else:
        stat_data = d.con_values
    ConnectionsPanel.mask = mask = calc_mask(stat_data, threshold, threshold_type, windows_num)
    indices = np.where(mask)[0]
    parent_obj = bpy.data.objects[get_connections_parent_name()]
    parent_obj.animation_data_clear()
    N = len(indices)
    print('{} connections are above the threshold'.format(N))
    create_vertices(d, mask, verts_color)
    create_conncection_per_condition(d, layers_rods, indices, mask, windows_num, norm_fac, T, radius)
    print('Create connections for the conditions {}'.format('difference' if stat == STAT_DIFF else 'mean'))
    create_keyframes_for_parent_obj(d, indices, mask, windows_num, norm_fac, T, stat)
    print('finish keyframing!')


def calc_mask(stat_data, threshold, threshold_type, windows_num):
    if threshold_type == 'percentile':
        threshold = np.percentile(np.abs(stat_data), threshold)
    threshold_type = bpy.context.scene.above_below_threshold
    if threshold_type == 'abs_above':
        mask = abs(stat_data) >= threshold if stat_data.ndim == 1 else np.max(abs(stat_data), axis=1) >= threshold
    elif threshold_type == 'above':
        mask = stat_data >= threshold if stat_data.ndim == 1 else np.max(stat_data, axis=1) >= threshold
    elif threshold_type == 'abs_below':
        mask = abs(stat_data) <= threshold if stat_data.ndim == 1 else np.max(abs(stat_data), axis=1) <= threshold
    elif threshold_type == 'below':
        mask = stat_data <= threshold if stat_data.ndim == 1 else np.max(stat_data, axis=1) <= threshold
    else:
        print('Wrong threshold_type! {}'.format(threshold_type))
        mask = [False] * len(stat_data)
    return mask


def create_conncection_per_condition(d, layers_rods, indices, mask, windows_num, norm_fac, T, radius):
    N = len(indices)
    parent_obj = bpy.data.objects[get_connections_parent_name()]
    print('Create connections for both conditions')
    con_color = (1, 1, 1, 1)
    now = time.time()
    for run, (ind, conn_name, (i, j)) in enumerate(zip(indices, d.con_names[mask], d.con_indices[mask])):
        mu.time_to_go(now, run, N, runs_num_to_print=10)
        # p1, p2 = d.locations[i, :] * 0.1, d.locations[j, :] * 0.1
        # mu.cylinder_between(p1, p2, radius, layers_rods)

        node1_obj, node2_obj = [bpy.data.objects['{}_vertice'.format(d.labels[k])] for k in [i, j]]
        mu.create_bezier_curve(node1_obj, node2_obj, layers_rods)
        # p1, p2 = d.locations[i, :] * 0.01, d.locations[j, :] * 0.01
        # mu.hook_curves(node1_obj, node2_obj, p1, p2)
        cur_obj = bpy.context.active_object
        cur_obj.name = conn_name
        cur_obj.parent = parent_obj

        # mu.create_material('{}_mat'.format(conn_name), con_color, 1)
        mu.create_and_set_material(cur_obj)
        # cur_mat = bpy.data.materials['{}_mat'.format(conn_name)]
        # cur_obj.active_material = cur_mat
        # cur_obj.animation_data_clear()
        if windows_num == 1:
            continue
        for cond_id, cond in enumerate(d.conditions):
            # insert_frame_keyframes(cur_obj, '{}-{}'.format(conn_name, cond), d.con_values[ind, -1, cond_id], T)
            for t in range(windows_num):
                extra_time_points = 0 if norm_fac == 1 else 2
                timepoint = t * norm_fac + extra_time_points
                mu.insert_keyframe_to_custom_prop(cur_obj, '{}-{}'.format(conn_name, cond),
                                                  d.con_values[ind, t, cond_id], timepoint)
            fcurve = cur_obj.animation_data.action.fcurves[cond_id]
            fcurve.keyframe_points[0].co[1] = 0
            fcurve.keyframe_points[-1].co[1] = 0
        finalize_fcurves(cur_obj)
    mu.change_fcurves_colors(parent_obj.children)


def create_vertices(d, mask, verts_color='green'):
    layers = [False] * 20
    layers[_addon().CONNECTIONS_LAYER] = True
    vert_color = np.hstack((cu.name_to_rgb(verts_color), [0.]))
    get_connection_parent()
    parent_name = '{}_connections_vertices'.format(bpy.context.scene.connectivity_files)
    parent_obj = mu.create_empty_if_doesnt_exists(parent_name, _addon().BRAIN_EMPTY_LAYER, None, get_connections_parent_name())
    for vertice in ConnectionsPanel.vertices:
    # for ind in range(len(d.names[mask])):
    # for indice in indices:
        p1 = d.locations[vertice, :] * 0.1
        vert_name = '{}_vertice'.format(d.labels[vertice])
        mu.create_ico_sphere(p1, layers, vert_name)
        mu.create_material('{}_mat'.format(vert_name), vert_color, 1)
        cur_obj = bpy.context.active_object
        cur_obj.name = vert_name
        cur_obj.parent = parent_obj


def get_connections_show_vertices():
    return bpy.context.scene.connections_show_vertices


def set_connections_show_vertices(val):
    bpy.context.scene.connections_show_vertices = val


def get_connections_width():
    return bpy.context.scene.connections_width


def set_connections_width(val):
    bpy.context.scene.connections_width = val


def connections_width_update(self, context):
    connection_parent = get_connection_parent()
    if connection_parent is None:
        return
    for c in connection_parent.children:
        if c.data is None:
            continue
        c.data.bevel_depth = bpy.context.scene.connections_width


def connections_show_vertices_update(self, context):
    vertices_obj = get_vertices_obj()
    if vertices_obj is not None:
        do_show = bpy.context.scene.connections_show_vertices
        mu.show_hide_hierarchy(do_show, vertices_obj)
        if do_show:
            _addon().filter_nodes(True)


def get_vertices_obj():
    vertices_obj = None
    connection_parent = get_connection_parent()
    if connection_parent is not None:
        vertices_parent_name = '{}_connections_vertices'.format(bpy.context.scene.connectivity_files)
        vertices_objs = [c for c in connection_parent.children if c.name == vertices_parent_name]
        if len(vertices_objs) == 1:
            vertices_obj = vertices_objs[0]
    return vertices_obj


def get_connection_parent():
    return bpy.data.objects.get('connections_{}'.format(bpy.context.scene.connectivity_files))


@mu.timeit
def update_vertices_location():
    if not ConnectionsPanel.connections_files_exist or ConnectionsPanel.d is None:
        return
    d = ConnectionsPanel.d
    if 'verts' not in d:
        return
    vertices_obj = get_vertices_obj()
    if vertices_obj is None:
        print('connections_vertices is None!')
        return
    new_locations = mu.get_verts_co(d.verts, d.hemis)
    existing_nodes = []
    for label_name, new_location in zip(d.labels, new_locations):
        node_name = '{}_vertice'.format(label_name)
        node_obj = bpy.data.objects.get(node_name)
        if node_obj is None:
            continue
        node_obj.location = new_location
        existing_nodes.append(label_name)
    for node1_name in existing_nodes:
        for node2_name in existing_nodes:
            con_obj = bpy.data.objects.get('{}-{}'.format(node1_name, node2_name))
            if con_obj is None:
                continue
            curve = con_obj.data
            curve.splines[0].bezier_points[0].co = bpy.data.objects['{}_vertice'.format(node1_name)].location
            curve.splines[0].bezier_points[1].co = bpy.data.objects['{}_vertice'.format(node2_name)].location


def vertices_selected(vertice_name):
    label_name = vertice_name[:-len('_vertice')]
    if _addon().both_conditions():
        for conn_name in ConnectionsPanel.vertices_lookup[label_name]:
            conn_obj = bpy.data.objects.get(conn_name, None)
            if conn_obj and not conn_obj.hide:
                conn_obj.select = True
    elif _addon().conditions_diff():
        parent_obj = bpy.context.scene.objects[get_connections_parent_name()]
        if parent_obj.animation_data is None:
            return
        parent_obj.select = True
        for fcurve in parent_obj.animation_data.action.fcurves:
            con_name = mu.get_fcurve_name(fcurve)
            fcurve.select = con_name in ConnectionsPanel.vertices_lookup[label_name]
            fcurve.hide = not con_name in ConnectionsPanel.vertices_lookup[label_name]
    mu.change_fcurves_colors(bpy.data.objects[get_connections_parent_name()].children)
    _addon().fit_selection()


def create_keyframes_for_parent_obj(d, indices, mask, windows_num, norm_fac, T, stat=STAT_DIFF):
    # Create keyframes for the parent obj (conditions diff)
    if windows_num == 1:
        return
    if stat not in [STAT_DIFF, STAT_AVG]:
        print("Wrong type of stat!")
        return
    parent_obj = bpy.data.objects[get_connections_parent_name()]
    stat_data = calc_stat_data(d.con_values, stat)
    N = len(indices)
    now = time.time()
    for run, (ind, conn_name) in enumerate(zip(indices, d.con_names[mask])):
        mu.time_to_go(now, run, N, runs_num_to_print=100)
        # insert_frame_keyframes(parent_obj, conn_name, stat_data[ind, -1], T)
        for t in range(windows_num):
            extra_time_points = 0 if norm_fac ==1 else 2
            timepoint = t * norm_fac + extra_time_points
            mu.insert_keyframe_to_custom_prop(parent_obj, conn_name, stat_data[ind, t], timepoint)
        fcurve = parent_obj.animation_data.action.fcurves[run]
        fcurve.keyframe_points[0].co[1] = 0
        fcurve.keyframe_points[-1].co[1] = 0

    finalize_fcurves(parent_obj)
    finalize_objects_creations()


def calc_stat_data(data, stat):
    if data.ndim == 1:
        return data
    axis = data.ndim - 1
    if data.shape[axis] == 1:
        stat = STAT_AVG
    if stat == STAT_AVG:
        stat_data = np.squeeze(np.mean(data, axis=axis))
    elif stat == STAT_DIFF:
        stat_data = np.squeeze(np.diff(data, axis=axis))
    else:
        raise Exception('Wrong stat value!')
    return stat_data


def insert_frame_keyframes(parent_obj, conn_name, last_data, T):
    mu.insert_keyframe_to_custom_prop(parent_obj, conn_name, 0, 1)
    mu.insert_keyframe_to_custom_prop(parent_obj, conn_name, 0, T + 1)  # last_data, T + 1)
    mu.insert_keyframe_to_custom_prop(parent_obj, conn_name, 0, T + 2)


def finalize_fcurves(parent_obj, interpolation=''):
    if not parent_obj.animation_data:
        return
    for fcurve in parent_obj.animation_data.action.fcurves:
        fcurve.modifiers.new(type='LIMITS')
        if interpolation == '':
            interpolation = 'BEZIER' if len(fcurve.keyframe_points) > 10 else 'LINEAR'
        for kf in fcurve.keyframe_points:
            kf.interpolation = interpolation
    mu.change_fcurves_colors([parent_obj])


def finalize_objects_creations():
    try:
        bpy.ops.graph.previewrange_set()
    except:
        pass
    for obj in bpy.data.objects:
        obj.select = False
    if bpy.data.objects.get(' '):
        bpy.context.scene.objects.active = bpy.data.objects[' ']


def unfilter_graph(context, d, condition):
    filter_graph(context, d, condition, 0, 'value', '')


# d: labels, locations, hemis, con_colors (L, W, 2, 3), con_values (L, W, 2), indices, con_names, conditions, con_types
def filter_graph(context, d, condition, threshold, threshold_type, connections_type, stat=STAT_DIFF):
    parent_obj_name = get_connections_parent_name()
    mu.show_hide_hierarchy(False, parent_obj_name)
    masked_con_names = calc_masked_con_names(d, threshold, threshold_type, connections_type, condition, stat)
    parent_obj = bpy.data.objects[parent_obj_name]
    bpy.context.scene.connections_num = min(len(masked_con_names), len(parent_obj.children) - 1)
    conn_show = 0
    selected_objects, selected_indices = [], []
    for con_ind, con_name in enumerate(d.con_names):
        cur_obj = bpy.data.objects.get(con_name)
        if cur_obj:
            if con_name in masked_con_names:
                selected_objects.append(cur_obj)
                selected_indices.append(con_ind)
                conn_show += 1
            cur_obj.hide = con_name not in masked_con_names
            cur_obj.hide_render = con_name not in masked_con_names
            if bpy.context.scene.selection_type == 'conds':
                cur_obj.select = not cur_obj.hide
    ConnectionsPanel.selected_objects = selected_objects
    ConnectionsPanel.selected_indices = selected_indices
    print('Showing {} connections after filtering'.format(conn_show))
    if conn_show > 0:
        bpy.context.scene.connections_min = np.min(d.con_values[selected_indices])
        bpy.context.scene.connections_max = np.max(d.con_values[selected_indices])
    if parent_obj.animation_data is None:
        return
    now = time.time()
    fcurves_num = len(parent_obj.animation_data.action.fcurves)
    for fcurve_index, fcurve in enumerate(parent_obj.animation_data.action.fcurves):
        # mu.time_to_go(now, fcurve_index, fcurves_num, runs_num_to_print=10)
        con_name = mu.get_fcurve_name(fcurve)
        # cur_obj = bpy.data.objects[con_name]
        # cur_obj.hide = con_name not in masked_con_names
        # cur_obj.hide_render = con_name not in masked_con_names
        if bpy.context.scene.selection_type != 'conds':
            fcurve.hide = con_name not in masked_con_names
            fcurve.select = not fcurve.hide

    parent_obj.select = True
    mu.view_all_in_graph_editor(context)


def calc_masked_con_names(d, threshold, threshold_type, connections_type, condition, stat):
    # For now, we filter only according to both conditions, not each one seperatly
    #todo: filter only the connections that were created, not all the possible connections
    if bpy.context.scene.selection_type == 'conds' and d.con_values.ndim == 3 and d.con_values.shape[2] > 1:
        if threshold_type == 'percentile':
            threshold = np.percentile(np.abs(np.max(d.con_values, axis=1)), threshold)
        above_below_threshold = bpy.context.scene.above_below_threshold
        if above_below_threshold == 'abs_above':
            mask1 = np.max(abs(d.con_values[:, :, 0]), axis=1) >= threshold
            mask2 = np.max(abs(d.con_values[:, :, 1]), axis=1) >= threshold
        elif above_below_threshold == 'above':
            mask1 = np.max(d.con_values[:, :, 0], axis=1) >= threshold
            mask2 = np.max(d.con_values[:, :, 1], axis=1) >= threshold
        elif above_below_threshold == 'abs_below':
            mask1 = np.max(abs(d.con_values[:, :, 0]), axis=1) <= threshold
            mask2 = np.max(abs(d.con_values[:, :, 1]), axis=1) <= threshold
        elif above_below_threshold == 'below':
            mask1 = np.max(d.con_values[:, :, 0], axis=1) <= threshold
            mask2 = np.max(d.con_values[:, :, 1], axis=1) <= threshold
        threshold_mask = mask1 | mask2
    else:
        stat_data = calc_stat_data(d.con_values, stat)
        windows_num = d.con_values.shape[1] if d.con_values.ndim >= 2 else 1
        threshold_mask = calc_mask(stat_data, threshold, threshold_type, windows_num)
        # threshold_mask = np.max(stat_data, axis=1) > threshold
    if connections_type == 'between':
        con_names_hemis = set(d.con_names[d.con_types == HEMIS_BETWEEN])
    elif connections_type == 'within':
        con_names_hemis = set(d.con_names[d.con_types == HEMIS_WITHIN])
    else:
        con_names_hemis = set(d.con_names)
    return set(d.con_names[threshold_mask]) & con_names_hemis


# d: labels, locations, hemis, con_colors (L, W, 3), con_values (L, W, 2), indices, con_names, conditions, con_types
# def plot_connections(self, context, d, plot_time, connections_type, condition, threshold, abs_threshold=True):
def plot_connections(d=None, plot_time=None, threshold=None, calc_t=True, data_minmax=None):
    if d is None:
        d = get_connections_data()
    if plot_time is None:
        plot_time = bpy.context.scene.frame_current
    _addon().show_hide_connections()
    windows_num = d.con_values.shape[1] if d.con_values.ndim >= 2 else 1
    if calc_t:
        t = int(plot_time / ConnectionsPanel.T * windows_num) if windows_num > 1 else 0
    else:
        t = plot_time
    print('plotting connections for t:{}'.format(t))
    if 1 < windows_num <= t:
        print('time out of bounds! {}'.format(plot_time))
    else:
        # selected_objects, selected_indices = get_all_selected_connections(d)
        selected_objects = ConnectionsPanel.selected_objects
        selected_indices = ConnectionsPanel.selected_indices
        if len(selected_objects) == 0:
            selected_objects, selected_indices = get_all_selected_connections(d)
        if data_minmax is not None:
            data_min, data_max = -data_minmax, data_minmax
            _addon().set_colorbar_max_min(data_max, data_min)
        elif _addon().colorbar_values_are_locked():
            data_min = _addon().get_colorbar_min()
            data_max = _addon().get_colorbar_max()
        else:
            # Should set the percentile in GUI
            data_min, data_max = ConnectionsPanel.data_minmax
            _addon().set_colorbar_max_min(data_max, data_min)
        colors_ratio = 256 / (data_max - data_min)
        stat_vals = [calc_stat_data(d.con_values[ind, t], STAT_DIFF) if d.con_values.ndim >= 2 else d.con_values[ind]
                     for ind in selected_indices]
        if not isinstance(stat_vals[0], float) and len(stat_vals[0]) == 2:
            stat_vals = [np.diff(v) for v in stat_vals]
        colors = _addon().calc_colors(np.array(stat_vals).squeeze(), data_min, colors_ratio)
        # colors = np.concatenate((colors, np.zeros((len(colors), 1))), 1)
        _addon().show_hide_connections()
        if threshold is None:
            threshold = bpy.context.scene.coloring_lower_threshold
        for ind, (cur_obj, obj_color) in enumerate(zip(selected_objects, colors)):
            if isinstance(cur_obj, str):
                cur_obj = bpy.data.objects.get(cur_obj)
            if bpy.context.scene.hide_connection_under_threshold:
                if abs(stat_vals[ind]) < threshold:
                    cur_obj.hide = True
                    cur_obj.hide_render = True
            bpy.context.scene.objects.active = cur_obj
            _addon().coloring.object_coloring(cur_obj, colors[ind])
            # mu.create_material('{}_mat'.format(cur_obj.name), colors[ind], 1, False)
        if bpy.context.scene.hide_connection_under_threshold:
            filter_nodes()
        parent_obj_name = get_connections_parent_name()
        bpy.data.objects[parent_obj_name].select = True
        connectivity_method = d['connectivity_method'] if 'connectivity_method' in d else 'connectivity'
        # if 'corr' in connectivity_method:
        #     _addon().set_colorbar_max_min(1, -1)
        # else:
        # data_max, data_min = np.max(d.con_values[selected_indices]), np.min(d.con_values[selected_indices])
        modality_names = dict(electrodes='Electrodes', meg='MEG', fmri='fMRI')
        colorbar_title = 'Electrodes {}'.format(connectivity_method) \
            if 'electrodes' in bpy.context.scene.connectivity_files else \
                '{} {}'.format(bpy.context.scene.connectivity_files, connectivity_method) # Cortical labels
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title(colorbar_title)


def get_connectivity_name():
    return bpy.context.scene.connectivity_files


def get_all_selected_connections(d):
    objs, inds = [], []
    parent_obj_name = get_connections_parent_name()
    parent_obj = bpy.data.objects[parent_obj_name]
    # con_objs_names = [obj.name for obj in bpy.data.objects[get_connections_parent_name()].children if obj.name != 'connections_vertices']
    # all_con_set = set(d.con_names.tolist())
    # indices = [np.where(d.con_names == obj_name)[0][0] for obj_name in con_objs_names]
    if bpy.context.scene.selection_type == 'conds' or parent_obj.animation_data is None:
        for ind, con_name in enumerate(d.con_names):
            cur_obj = bpy.data.objects.get(con_name)
            if cur_obj and not cur_obj.hide:
                objs.append(cur_obj.name)
                inds.append(ind)
    else:
        for fcurve in parent_obj.animation_data.action.fcurves:
            con_name = mu.get_fcurve_name(fcurve)
            if fcurve.select and not fcurve.hide:
                objs.append(con_name)
                ind = np.where(d.con_names == con_name)[0][0]
                inds.append(ind)
    return objs, inds


# Called from FilterPanel, FindCurveClosestToCursor
def find_connections_closest_to_target_value(closet_object_name, closest_curve_name, target):
    parent_obj_name = get_connections_parent_name()
    parent_obj = bpy.data.objects[parent_obj_name]
    if bpy.context.scene.selection_type == 'conds':
        for cur_obj in parent_obj.children:
            if not cur_obj.animation_data:
                continue
            for fcurve in cur_obj.animation_data.action.fcurves:
                if cur_obj.name == closet_object_name:
                    fcurve_name = mu.get_fcurve_name(fcurve)
                    fcurve.select = fcurve_name == closest_curve_name
                    fcurve.hide = fcurve_name != closest_curve_name
                else:
                    fcurve.select = False
                    fcurve.hide = True
    else:  # diff
        # todo: implement this part
        for fcurve in parent_obj.animation_data.action.fcurves:
            conn_name = mu.get_fcurve_name(conn_name)


def filter_nodes(do_filter=True, connectivity_file=''):
    if connectivity_file != '':
        bpy.context.scene.connectivity_files = connectivity_file
    parent = get_connections_parent_name()
    if parent is None:
        print('{} is None!'.format(parent))
        return
    vertices_parent_name = '{}_connections_vertices'.format(bpy.context.scene.connectivity_files)
    vertices_obj = bpy.data.objects.get(vertices_parent_name)
    if vertices_obj is None:
        print('connections_vertices is None!')
        return
    for node in vertices_obj.children:
        if do_filter:
            conn_found = False
            label_name = node.name[:-len('_vertice')]
            for conn in bpy.data.objects[parent].children:
                if label_name in conn.name and not conn.hide:
                    conn_found = True
                    break
            if not conn_found:
                node.hide = True
                node.hide_render = True
        else:
            node.hide = False
            node.hide_render = False


def filter_electrodes_via_connections(context, do_filter):
    display_conds = bpy.context.scene.selection_type == 'conds'
    for elc_name in ConnectionsPanel.addon.play_panel.PlayPanel.electrodes_names:
        cur_obj = bpy.data.objects.get(elc_name)
        if cur_obj:
            cur_obj.hide = do_filter
            cur_obj.hide_render = do_filter
            cur_obj.select = not do_filter and display_conds
            for fcurve in cur_obj.animation_data.action.fcurves:
                fcurve.hide = do_filter
                fcurve.select = not do_filter

    elecs_parent_obj = bpy.data.objects['Deep_electrodes']
    elecs_parent_obj.select = not display_conds
    for fcurve in elecs_parent_obj.animation_data.action.fcurves:
        fcurve.hide = do_filter
        fcurve.select = not do_filter

    if do_filter:
        selected_electrodes = set()
        for ind, con_name in enumerate(ConnectionsPanel.d.con_names):
            cur_obj = bpy.data.objects.get(con_name)
            if not cur_obj or cur_obj.hide:
                continue
            electrodes = con_name.split('-')
            for elc in electrodes:
                cur_elc = bpy.data.objects.get(elc)
                if not cur_elc or elc in selected_electrodes:
                    continue
                selected_electrodes.add(elc)
                # if bpy.context.scene.selection_type == 'conds':
                cur_elc.hide = False
                cur_elc.hide_render = False
                cur_elc.select = display_conds
                for fcurve in cur_elc.animation_data.action.fcurves:
                    fcurve.hide = False
                    fcurve.select = True
        for fcurve in elecs_parent_obj.animation_data.action.fcurves:
            elc_name = mu.get_fcurve_name(fcurve)
            if elc_name in selected_electrodes:
                fcurve.hide = False
                fcurve.select = True

    mu.view_all_in_graph_editor()


def capture_graph_data(per_condition):
    parent_obj_name = get_connections_parent_name()
    parent_obj = bpy.data.objects.get(parent_obj_name, None)
    if parent_obj:
        time_range = range(0, ConnectionsPanel.addon.get_max_time_steps(), bpy.context.scene.play_dt)
        if per_condition:
            #todo: implement
            pass
        else:
            data, colors = mu.evaluate_fcurves(parent_obj, time_range)
        return data, colors
    else:
        return {}, {}

# def capture_graph(context, image_fol):
#     data, colors = {}, {}
#     data['Coherence'], colors['Coherence'] = capture_graph_data()
#     data['Electrodes'], colors['Electrodes'] = ConnectionsPanel.addon.play_panel.get_electrodes_data()
#     # data.update(elcs_data)
#     # colors.update(elcs_colors)
#     ConnectionsPanel.addon.play_panel.plot_graph(context, data, colors, image_fol)
#     ConnectionsPanel.addon.play_panel.save_graph_data(data, colors, image_fol)


def load_connections_file(connectivity_files=''):
    if connectivity_files == '':
        connectivity_files = bpy.context.scene.connectivity_files
    d, vertices, vertices_lookup = None, None, None
    conn_file_name = connectivity_files.replace(' ', '_')
    connectivity_file = op.join(mu.get_user_fol(), 'connectivity', '{}.npz'.format(conn_file_name))
    vertices_file = op.join(mu.get_user_fol(), 'connectivity', '{}_vertices.pkl'.format(
        conn_file_name.replace('_static', '')))
    if op.isfile(connectivity_file):
        print('loading connectivity: {}'.format(connectivity_file))
        d = mu.Bag(np.load(connectivity_file))
        d.labels = [l.astype(str) for l in d.labels]
        d.hemis = [l.astype(str) for l in d.hemis]
        d.con_names = np.array([l.astype(str) for l in d.con_names], dtype=np.str)
        d.conditions = [l.astype(str) for l in d.conditions]
        if d.con_values.ndim == 2:
            d.con_values = d.con_values[:, :, np.newaxis]
        conditions_items = [(cond, cond, '', cond_ind) for cond_ind, cond in enumerate(d.conditions)]
        if len(d.conditions) > 1:
            diff_cond = '{}-{} difference'.format(d.conditions[0], d.conditions[1])
            conditions_items.append((diff_cond, diff_cond, '', len(d.conditions)))
        bpy.types.Scene.conditions = bpy.props.EnumProperty(items=conditions_items, description="Conditions")
        # bpy.context.scene.connections_max, bpy.context.scene.connections_min = d['data_max'], d['data_min']
    else:
        print('No connections file! {}'.format(connectivity_file))
    if op.isfile(vertices_file):
        vertices, vertices_lookup = mu.load(vertices_file)
    else:
        name_parts = mu.namebase(vertices_file).split('_')
        vertices_files = glob.glob(
            op.join(mu.get_parent_fol(vertices_file), '{}*_{}.pkl'.format(name_parts[0], name_parts[-1])))
        if len(vertices_files) == 1:
            vertices, vertices_lookup = mu.load(vertices_files[0])
        else:
            print('No vertices file! ({})'.format(vertices_file))
    ConnectionsPanel.d, ConnectionsPanel.vertices, ConnectionsPanel.vertices_lookup = d, vertices, vertices_lookup


def create_connections():
    # load_connections_file()
    threshold = bpy.context.scene.connections_threshold
    threshold_type = bpy.context.scene.connections_threshold_type
    create_keyframes(ConnectionsPanel.d, threshold, threshold_type, stat=STAT_DIFF)
    ConnectionsPanel.selected_objects, ConnectionsPanel.selected_indices = \
        get_all_selected_connections(ConnectionsPanel.d)


class CheckConnections(bpy.types.Operator):
    bl_idname = "mmvt.check_connections"
    bl_label = "mmvt check connections"
    bl_description = 'Checks the connections number above the threshold.\n\nScript: mmvt.connections.check_connections()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        check_connections()
        return {"FINISHED"}


class CreateConnections(bpy.types.Operator):
    bl_idname = "mmvt.create_connections"
    bl_label = "mmvt create connections"
    bl_description = 'Imports the connections objects.\n\nScript: mmvt.connections.create_connections()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        create_connections()
        return {"FINISHED"}


class FilterGraph(bpy.types.Operator):
    bl_idname = "mmvt.filter_graph"
    bl_label = "mmvt filter graph"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        parent_obj_name = get_connections_parent_name()
        if not bpy.data.objects.get(parent_obj_name):
            self.report({'ERROR'}, 'No parent node was found, you first need to create the connections.')
        else:
            connections_type = bpy.context.scene.connections_type
            threshold = bpy.context.scene.connections_threshold
            threshold_type = bpy.context.scene.connections_threshold_type
            # abs_threshold = False  # bpy.context.scene.abs_threshold
            condition = bpy.context.scene.conditions
            # print(connections_type, condition, threshold, abs_threshold)
            if bpy.context.scene.connections_filter:
                unfilter_graph(context, ConnectionsPanel.d, condition)
            else:
                filter_graph(context, ConnectionsPanel.d, condition, threshold, threshold_type, connections_type)
            bpy.context.scene.connections_filter = not bpy.context.scene.connections_filter
        return {"FINISHED"}


# # todo: Should move to coloring_panel
# class PlotConnections(bpy.types.Operator):
#     bl_idname = "mmvt.plot_connections"
#     bl_label = "mmvt plot connections"
#     bl_options = {"UNDO"}
#
#     @staticmethod
#     def invoke(self, context, event=None):
#         if not bpy.data.objects.get(PARENT_OBJ):
#             self.report({'ERROR'}, 'No parent node was found, you first need to create the connections.')
#         else:
#             connections_type = bpy.context.scene.connections_type
#             threshold = bpy.context.scene.connections_threshold
#             abs_threshold = bpy.context.scene.abs_threshold
#             condition = bpy.context.scene.conditions
#             plot_time = bpy.context.scene.frame_current
#             print(connections_type, condition, threshold, abs_threshold)
#             # mu.delete_hierarchy(PARENT_OBJ)
#             # plot_connections(ConnectionsPanel.d, plot_time, connections_type, condition, threshold,
#             #                  abs_threshold)
#             plot_connections(ConnectionsPanel.d, plot_time)
#         return {"FINISHED"}


# class ShowHideConnections(bpy.types.Operator):
#     bl_idname = "mmvt.show_hide_connections"
#     bl_label = "mmvt show_hide_connections"
#     bl_options = {"UNDO"}
#
#     @staticmethod
#     def invoke(self, context, event=None):
#         if not bpy.data.objects.get(PARENT_OBJ):
#             self.report({'ERROR'}, 'No parent node was found, you first need to create the connections.')
#         else:
#             d = ConnectionsPanel.d
#             condition = bpy.context.scene.conditions
#             connections_type = bpy.context.scene.connections_type
#             threshold = bpy.context.scene.connections_threshold
#             time = bpy.context.scene.frame_current
#             show_hide_connections(context, ConnectionsPanel.show_connections, d, condition,
#                                   threshold, connections_type, time)
#             ConnectionsPanel.show_connections = not ConnectionsPanel.show_connections
#         return {"FINISHED"}


class UpdateNodesLocations(bpy.types.Operator):
    bl_idname = "mmvt.update_nodes_locations"
    bl_label = "mmvt update_nodes_locations"
    bl_description = 'Updates the nodes and edges locations after morphing the brain.' \
                     '\n\nScript: mmvt.connections.update_vertices_location()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        update_vertices_location()
        return {"FINISHED"}


class FilterNodes(bpy.types.Operator):
    bl_idname = "mmvt.filter_nodes"
    bl_label = "mmvt filter nodes"
    bl_description = 'Hides all the nodes with no edges'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        parent_obj_name = get_connections_parent_name()
        if not bpy.data.objects.get(parent_obj_name):
            self.report({'ERROR'}, 'No parent node was found, you first need to create the connections.')
        else:
            filter_nodes(ConnectionsPanel.do_filter)
            ConnectionsPanel.do_filter = not ConnectionsPanel.do_filter
        return {"FINISHED"}


class FilterElectrodes(bpy.types.Operator):
    bl_idname = "mmvt.filter_electrodes"
    bl_label = "mmvt filter electrodes"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        parent_obj_name = get_connections_parent_name()
        if not bpy.data.objects.get(parent_obj_name):
            self.report({'ERROR'}, 'No parent node was found, you first need to create the connections.')
        else:
            filter_electrodes_via_connections(ConnectionsPanel.do_filter)
            ConnectionsPanel.do_filter = not ConnectionsPanel.do_filter
        return {"FINISHED"}


class ClearConnections(bpy.types.Operator):
    bl_idname = "mmvt.clear_connections"
    bl_label = "mmvt clear connections"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        mu.delete_hierarchy(get_connections_parent_name())
        return {"FINISHED"}


# class ExportGraph(bpy.types.Operator):
#     bl_idname = "mmvt.export_graph"
#     bl_label = "mmvt export_graph"
#     bl_options = {"UNDO"}
#     uuid = mu.rand_letters(5)
#
#     @staticmethod
#     def invoke(self, context, event=None):
#         image_fol = op.join(mu.get_user_fol(), 'images', ExportGraph.uuid)
#         capture_graph(context, image_fol)
#         return {"FINISHED"}


def connectivity_files_update(self, context):
    # if ConnectionsPanel.d == {} or ConnectionsPanel.d is None :
    load_connections_file()
    check_connections()
    for obj in bpy.data.objects['Functional maps'].children:
        if obj.name.startswith('connections'):
            val = obj.name == get_connections_parent_name()
            mu.show_hide_hierarchy(val, obj.name, True, False)
    data = ConnectionsPanel.d.con_values
    # data_max = np.percentile(data[ConnectionsPanel.selected_indices], 97)
    # data_min = np.percentile(data[ConnectionsPanel.selected_indices], 3)
    if data.ndim == 3 and data.shape[2] == 2:
        data = np.diff(data, axis=2).squeeze()
    if len(ConnectionsPanel.selected_indices) > 0:
        data_max = np.nanmax(data[ConnectionsPanel.selected_indices])
        data_min = np.nanmin(data[ConnectionsPanel.selected_indices])
    else:
        data_max = np.nanmax(data)
        data_min = np.nanmin(data)
    if np.sign(data_max) != np.sign(data_min) and data_min != 0 and data_max != 0:
        data_minmax = max(map(abs, [data_max, data_min]))
        data_max, data_min = data_minmax, -data_minmax
    ConnectionsPanel.data_minmax = (data_min, data_max)


def connections_draw(self, context):
    layout = self.layout
    # layout.prop(context.scene, "connections_origin", text="")
    layout.prop(context.scene, "connectivity_files", text="")
    layout.operator(CheckConnections.bl_idname, text="Check connections ", icon='RNA_ADD')
    layout.label(text='# Connections: {}'.format(bpy.context.scene.connections_num))
    layout.label(text='{:.2f} < values < {:.2f}'.format(bpy.context.scene.connections_min, bpy.context.scene.connections_max))
    layout.operator(CreateConnections.bl_idname, text="Create connections ", icon='RNA_ADD')
    layout.prop(context.scene, 'connections_threshold', text="Threshold")
    layout.prop(context.scene, 'above_below_threshold', text='')
    # layout.prop(context.scene, 'abs_threshold')
    layout.prop(context.scene, "connections_type", text="")
    layout.label(text='Show connections for:')
    layout.prop(context.scene, "conditions", text="")
    layout.label(text='Filter type:')
    layout.prop(context.scene, 'connections_threshold_type', text='threshold type', expand=True)
    filter_text = 'Remove filter' if bpy.context.scene.connections_filter else 'Filter connections'
    layout.operator(FilterGraph.bl_idname, text=filter_text, icon='BORDERMOVE')
    # layout.prop(context.scene, 'connections_filter_vertices', text="Hide non connected vertices")
    if 'electrodes' in bpy.context.scene.connectivity_files:
        filter_text = '{} electrodes'.format('Filter' if ConnectionsPanel.do_filter else 'Remove filter from')
        layout.operator(FilterElectrodes.bl_idname, text=filter_text, icon='BORDERMOVE')
    if 'fmri' in bpy.context.scene.connectivity_files.lower() or 'meg' in bpy.context.scene.connectivity_files.lower():
        filter_text = '{} nodes'.format('Filter' if ConnectionsPanel.do_filter else 'Remove filter from')
        layout.operator(FilterNodes.bl_idname, text=filter_text, icon='BORDERMOVE')
    layout.operator(UpdateNodesLocations.bl_idname, text='Update locations', icon='IPO')
    layout.prop(context.scene, 'connections_show_vertices', text='Show nodes')
    layout.prop(context.scene, 'connections_width', text='Width')
    # layout.operator("mmvt.export_graph", text="Export graph", icon='SNAP_NORMAL')
    # layout.operator("mmvt.clear_connections", text="Clear", icon='PANEL_CLOSE')


bpy.types.Scene.connectivity_files = bpy.props.EnumProperty(items=[('', '', '', 0)], update=connectivity_files_update,
    description='Selects the connectivity file.\n\nCurrent file')
bpy.types.Scene.connections_threshold = bpy.props.FloatProperty(default=5, min=0,
    description='Sets the threshold to calculate the connections number')
bpy.types.Scene.abs_threshold = bpy.props.BoolProperty(
    name='abs threshold', description="check if abs(val) > threshold")
bpy.types.Scene.connections_type = bpy.props.EnumProperty(
        items=[("all", "All connections", "", 1), ("between", "Only between hemispheres", "", 2),
               ("within", "Only within hemispheres", "", 3)],
        description='Displays the connections within/between hemispheres.\n\nCurrent')
bpy.types.Scene.above_below_threshold = bpy.props.EnumProperty(
        items=[("abs_above", "Abs above threshold", "", 1), ("above", "Above threshold", "", 2),
               ("abs_below", "Below threshold", "", 2), ("below", "Below threshold", "", 3)],
        description='Selects the method used to calculate the number of connections using the threshold.\n\n Current method')
bpy.types.Scene.conditions = bpy.props.EnumProperty(items=[], description="Conditions")
bpy.types.Scene.connections_file = bpy.props.StringProperty(default='', description="connection file")
bpy.types.Scene.connections_threshold_type = bpy.props.EnumProperty(
    items=[("value", "value", "", 1), ("percentile", "percentile", "", 2)], #, ("top_k", "top k", "", 3)],
    description="Threshold type")
bpy.types.Scene.connections_filter = bpy.props.BoolProperty(name='connections_filter')
bpy.types.Scene.connections_num = bpy.props.IntProperty(min=0, default=0, description="")
# bpy.types.Scene.connections_filter_vertices = bpy.props.BoolProperty(default=True, description="")

bpy.types.Scene.connections_min = bpy.props.FloatProperty(default=0)
bpy.types.Scene.connections_max = bpy.props.FloatProperty(default=0)
bpy.types.Scene.connections_show_vertices = bpy.props.BoolProperty(
    default=True, description='Show/hide nodes', update=connections_show_vertices_update)
bpy.types.Scene.connections_width = bpy.props.FloatProperty(
    default=0, min=0, max=0.2, update=connections_width_update, description='Connections depth')


class ConnectionsPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Connections"
    addon = None
    init = False
    d = None #mu.Bag({})
    show_connections = True
    do_filter = True
    connections_files_exist = False
    conn_names = []
    selected_indices = []
    mask = None

    def draw(self, context):
        connections_draw(self, context)

#
# def set_connection_type(connection_type):
#     bpy.context.scene.connections_origin = connection_type


def set_connections_threshold(threshold):
    bpy.context.scene.connections_threshold = threshold


def init(addon):
    import glob
    conn_keys = set(['conditions', 'labels', 'locations', 'hemis', 'con_indices', 'con_names', 'con_values',
                     'con_types', 'data_max', 'data_min', 'connectivity_method'])
    conn_files_template = op.join(mu.get_user_fol(), 'connectivity', '*.npz')
    conn_files = [f for f in glob.glob(conn_files_template) if 'backup' not in mu.namebase(f)]
    try:
        conn_files = [f for f in conn_files if all([k in set(np.load(f).keys()) for k in conn_keys])]
    except:
        pass

    ConnectionsPanel.connections_files_exist = len(conn_files) > 0
    addon.set_connection_files_exist(ConnectionsPanel.connections_files_exist)
    if not ConnectionsPanel.connections_files_exist:
        print('No connectivity files were found in {}'.format(conn_files_template))
        ConnectionsPanel.init = False
        # unregister()
        return

    conn_names = [mu.namebase(fname).replace('_', ' ') for fname in conn_files]
    conn_items = [(c, c, '', ind) for ind, c in enumerate(conn_names)]
    if len(conn_names) > 0:
        bpy.types.Scene.connectivity_files = bpy.props.EnumProperty(items=conn_items, update=connectivity_files_update,
            description='Selects the connectivity file.\n\nCurrent file')
        ConnectionsPanel.conn_names = conn_names
        conn_obj_names = ['connections_{}'.format(con_name.replace(' ', '_')) for con_name in conn_names]
        for parent_obj in bpy.data.objects['Functional maps'].children:
            if parent_obj.name in conn_obj_names:
                conn_index = conn_obj_names.index(parent_obj.name)
                bpy.context.scene.connectivity_files = conn_names[conn_index]  # get_first_existing_parent_obj_name() #
                break

    ConnectionsPanel.T = addon.get_max_time_steps()
    ConnectionsPanel.addon = addon
    bpy.context.scene.connections_threshold = 0
    bpy.context.scene.connections_width = 0.1
    check_connections()
    ConnectionsPanel.init = True
    register()


def register():
    try:
        unregister()
        bpy.utils.register_class(ConnectionsPanel)
        bpy.utils.register_class(CheckConnections)
        bpy.utils.register_class(CreateConnections)
        bpy.utils.register_class(FilterGraph)
        bpy.utils.register_class(FilterElectrodes)
        bpy.utils.register_class(FilterNodes)
        bpy.utils.register_class(UpdateNodesLocations)
        # print('ConnectionsPanel was registered!')
    except:
        print("Can't register ConnectionsPanel!")


def unregister():
    try:
        bpy.utils.unregister_class(ConnectionsPanel)
        bpy.utils.unregister_class(CheckConnections)
        bpy.utils.unregister_class(CreateConnections)
        bpy.utils.unregister_class(FilterGraph)
        bpy.utils.unregister_class(FilterElectrodes)
        bpy.utils.unregister_class(FilterNodes)
        bpy.utils.unregister_class(UpdateNodesLocations)
    except:
        pass
        # print("Can't unregister ConnectionsPanel!")
