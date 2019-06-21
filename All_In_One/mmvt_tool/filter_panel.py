import bpy
import mmvt_utils as mu
import colors_utils as cu
import numpy as np
import os.path as op
import glob
import numbers
import importlib
from collections import defaultdict

try:
    import connections_panel
    connections_panel_exist = True
except:
    connections_panel_exist = False


def _addon():
    return FilteringMakerPanel.addon


def filter_from_to_update(self=None, context=None):
    mu.select_time_range(t_start=bpy.context.scene.filter_from)
    mu.select_time_range(t_end=bpy.context.scene.filter_to)


def color_object_uniformly(obj, color, name='selected'):
    mesh = obj.data
    vcol_layer = mesh.vertex_colors.new(name=name)
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            loop_vert_index = mesh.loops[loop_index].vertex_index
            vcol_layer.data[loop_index].color = color


def find_obj_with_val():
    cur_objects = []
    for obj in bpy.data.objects:
        if obj.select is True:
            cur_objects.append(obj)

    graph_editor = mu.get_the_graph_editor()
    target = graph_editor.cursor_position_y

    values, names, obj_names = [], [], []
    for cur_obj in cur_objects:
        for name, val in cur_obj.items():
            if bpy.context.scene.selection_type == 'spec_cond' and bpy.context.scene.conditions_selection not in name:
                continue
            if isinstance(val, numbers.Number):
                values.append(val)
                names.append(name)
                obj_names.append(cur_obj.name)
            # print(name)
    np_values = np.array(values) - target
    try:
        index = np.argmin(np.abs(np_values))
        closest_curve_name = names[index]
        closet_object_name = obj_names[index]
    except ValueError:
        closest_curve_name = ''
        closet_object_name = ''
        print('ERROR - Make sure you select all objects in interest')
    # print(closest_curve_name, closet_object_name)
    bpy.types.Scene.closest_curve_str = closest_curve_name
    # object_name = closest_curve_str
    # if bpy.data.objects.get(object_name) is None:
    #     object_name = object_name[:object_name.rfind('_')]
    print('object name: {}, curve name: {}'.format(closet_object_name, closest_curve_name))
    parent_obj = bpy.data.objects[closet_object_name].parent
    # print('parent: {}'.format(bpy.data.objects[object_name].parent))
    # try:
    if parent_obj:
        if parent_obj.name == 'Deep_electrodes':
            print('filtering electrodes')
            filter_electrode_or_sensor(closet_object_name)
            bpy.context.scene.cursor_location = bpy.data.objects[closet_object_name].location
        elif connections_panel_exist and parent_obj.name == _addon().get_connections_parent_name():
            connections_panel.find_connections_closest_to_target_value(closet_object_name, closest_curve_name, target)
        else:
            filter_roi_func(closet_object_name, closest_curve_name)
    # except KeyError:
    #     filter_roi_func(object_name)


def filter_draw(self, context):
    layout = self.layout
    layout.prop(context.scene, "selection_type", text="")
    layout.prop(context.scene, "filter_topK", text="Top K")
    row = layout.row(align=0)
    row.prop(context.scene, "filter_from", text="From")
    row.operator(GrabFromFiltering.bl_idname, text="", icon='BORDERMOVE')
    row.prop(context.scene, "filter_to", text="To")
    row.operator(GrabToFiltering.bl_idname, text="", icon='BORDERMOVE')
    layout.prop(context.scene, "filter_curves_type", text='Selection type')
    layout.prop(context.scene, "filter_curves_func", text='Filter function')
    layout.prop(context.scene, 'mark_filter_items', text="Mark selected items")
    layout.operator(Filtering.bl_idname, text="Filter " + bpy.context.scene.filter_curves_type, icon='BORDERMOVE')
    # if bpy.types.Scene.filter_is_on:
    layout.operator(ClearFiltering.bl_idname, text="Clear Filtering", icon='PANEL_CLOSE')
    col = layout.column(align=0)
    col.operator(FindCurveClosestToCursor.bl_idname, text="closest curve to cursor", icon='SNAP_SURFACE')
    if bpy.types.Scene.closest_curve_str != '':
        col.label(text=bpy.types.Scene.closest_curve_str)
    layout.prop(context.scene, 'filter_items_one_by_one', text="Show one by one")
    if bpy.context.scene.filter_items_one_by_one:
        row = layout.row(align=0)
        row.operator(PrevFilterItem.bl_idname, text="", icon='PREV_KEYFRAME')
        row.prop(context.scene, 'filter_items', text="")
        row.operator(NextFilterItem.bl_idname, text="", icon='NEXT_KEYFRAME')
    if len(Filtering.objects_indices) > 0:
        box = layout.box()
        col = box.column()
        for ind in Filtering.objects_indices:
            mu.add_box_line(col, Filtering.filter_objects[ind], '{:.2f}'.format(Filtering.filter_values[ind]), 0.8)
    row = layout.row(align=True)
    row.prop(context.scene, "filter_fcurves", text="Filter curves")
    row.operator(ResetCurvesFilter.bl_idname, text="", icon='PANEL_CLOSE')
        # bpy.context.area.type = 'GRAPH_EDITOR'
    # filter_to = bpy.context.scence.frame_preview_end


def clear_filtering():
    # for subhierarchy in bpy.data.objects['Brain'].children:
    #     if subhierarchy.name.startswith('Cortex-inflated'):
    #         for obj in subhierarchy.children:
    #             obj.data.vertex_colors.active_index = obj.data.vertex_colors.keys().index('curve')
    #     else:
    for obj in bpy.data.objects['Subcortical_structures'].children:
        obj.active_material = bpy.data.materials['unselected_label_Mat_subcortical']

    for parent_name in ['Deep_electrodes', 'EEG_sensors', 'MEG_sensors']:
        if bpy.data.objects.get(parent_name):
            for obj in bpy.data.objects[parent_name].children:
                de_select_electrode_and_sensor(obj, calc_best_curves_sep=False)

    Filtering.filter_objects, Filtering.objects_indices = [], []
    bpy.context.scene.filter_fcurves = ''


def de_select_electrode_and_sensor(obj, call_create_and_set_material=True, calc_best_curves_sep=False):
    if isinstance(obj, str):
        obj = bpy.data.objects[obj]
    obj.active_material.node_tree.nodes["Layer Weight"].inputs[0].default_value = 1
    # safety check, if something happened to the electrode's material
    if call_create_and_set_material:
        mu.create_and_set_material(obj)
    # Sholdn't change to color here. If user plot the electrodes, we don't want to change it back to white.
    if obj.name in FilteringMakerPanel.electrodes_colors:
        _addon().object_coloring(obj, FilteringMakerPanel.electrodes_colors[obj.name])
        obj.active_material.diffuse_color = FilteringMakerPanel.electrodes_colors[obj.name][:3]
    else:
        obj.active_material.node_tree.nodes["RGB"].outputs[0].default_value = (1, 1, 1, 1)
        obj.active_material.diffuse_color = (1, 1, 1)
    obj.select = False
    if calc_best_curves_sep:
        _addon().calc_best_curves_sep()


def filter_roi_func(closet_object_name, closest_curve_name=None, mark='mark_green'):
    roi_closet_object_name = closet_object_name
    if _addon().is_inflated():
        closet_object_name = 'inflated_{}'.format(closet_object_name)

    if bpy.context.scene.selection_type == 'conds':
        # todo: set change_selected_fcurves_colors to False, and match the contour's color to the fcurve's color
        _addon().select_roi(roi_closet_object_name, change_selected_fcurves_colors=True)
        obj = bpy.data.objects[closet_object_name]
        obj.select = True
        bpy.context.scene.objects.active = obj
    elif bpy.context.scene.selection_type == 'diff':
        if bpy.context.scene.filter_items_one_by_one:
            bpy.data.objects['Brain'].select = True
            mu.filter_graph_editor(roi_closet_object_name)
    # labels_names = [Filtering.filter_objects[ind] for ind in Filtering.objects_indices]
    # index = labels_names.index(obj_name)
    # print(index)
    # color = mu.get_hs_color(len(Filtering.objects_indices), index)
    # color = mu.get_selected_fcurves_colors(mu.OBJ_TYPES_ROIS, sepcific_obj_name=obj_name)
    _addon().color_contours([roi_closet_object_name], specific_colors=[1, 0, 0], move_cursor=True)
    bpy.types.Scene.filter_is_on = True


def filter_electrode_or_sensor(elec_name, val=0.3):
    elec_obj = bpy.data.objects[elec_name]
    if bpy.context.scene.mark_filter_items:
        FilteringMakerPanel.electrodes_colors[elec_name] = _addon().get_obj_color(elec_obj)
        _addon().object_coloring(elec_obj, cu.name_to_rgb('green'))
    else:
        elec_obj.active_material.node_tree.nodes["Layer Weight"].inputs[0].default_value = val

    # todo: selecting the electrode will show both of their conditions time series
    # We don't want it to happen if selection_type == 'conds'...
    if bpy.context.scene.selection_type == 'conds' or bpy.context.scene.filter_items_one_by_one:
        bpy.data.objects[elec_name].select = True
        fcurves = mu.get_fcurves(bpy.data.objects[elec_name])
        for fcurve in fcurves:
            fcurve.hide = False
            fcurve.select = True

    bpy.context.scene.objects.active = bpy.data.objects[elec_name]
    bpy.types.Scene.filter_is_on = True


def deselect_all_objects():
    for obj in bpy.data.objects:
        if obj.select:
            if obj.parent == bpy.data.objects['Subcortical_structures']:
                obj.active_material = bpy.data.materials['unselected_label_Mat_subcortical']
            # elif obj.parent == bpy.data.objects['Cortex-lh'] or obj.parent == bpy.data.objects['Cortex-rh']:
            #     obj.active_material = bpy.data.materials['unselected_label_Mat_cortex']
            # elif obj.parent == bpy.data.objects['Cortex-inflated-lh'] or obj.parent == bpy.data.objects['Cortex-inflated-rh']:
            #     obj.data.vertex_colors.active_index = obj.data.vertex_colors.keys().index('curve')
            elif bpy.data.objects.get('Deep_electrodes', None) and obj.parent == bpy.data.objects['Deep_electrodes'] or \
                 bpy.data.objects.get('EEG_sensors', None) and obj.parent == bpy.data.objects['EEG_sensors']:
                 de_select_electrode_and_sensor(obj, calc_best_curves_sep=False)
            obj.select = False


def filter_items_update(self, context):
    deselect_all_objects()
    if bpy.context.scene.filter_curves_type in ['Electrodes', 'EEG', 'MEG_sensors']:
        filter_electrode_or_sensor(bpy.context.scene.filter_items)
    elif bpy.context.scene.filter_curves_type == 'MEG':
        filter_roi_func(bpy.context.scene.filter_items)
    mu.view_all_in_graph_editor(context)


def update_filter_items(topk, objects_indices, filter_objects):
    filter_items = []
    FilteringMakerPanel.filter_items = []
    if topk == 0:
        topk = len(objects_indices)
    for loop_ind, ind in enumerate(range(min(topk, len(objects_indices)) - 1, -1, -1)):
        filter_item = filter_objects[objects_indices[ind]]
        if 'unknown' in filter_item:
            continue
        filter_items.append((filter_item, '{}) {}'.format(ind + 1, filter_item), '', loop_ind))
        FilteringMakerPanel.filter_items.append(filter_item)
    bpy.types.Scene.filter_items = bpy.props.EnumProperty(
        items=filter_items, description="filter items", update=filter_items_update)
    if len(filter_items) > 0:
        bpy.context.scene.filter_items = FilteringMakerPanel.filter_items[-1]


def show_one_by_one_update(self, context):
    if bpy.context.scene.filter_items_one_by_one:
        update_filter_items(bpy.context.scene.filter_topK, Filtering.objects_indices, Filtering.filter_objects)


def next_filter_item():
    index = FilteringMakerPanel.filter_items.index(bpy.context.scene.filter_items)
    next_item = FilteringMakerPanel.filter_items[index + 1] if index < len(FilteringMakerPanel.filter_items) -1 \
        else FilteringMakerPanel.filter_items[0]
    bpy.context.scene.filter_items = next_item


def prev_filter_item():
    index = FilteringMakerPanel.filter_items.index(bpy.context.scene.filter_items)
    prev_cluster = FilteringMakerPanel.filter_items[index - 1] if index > 0 else FilteringMakerPanel.filter_items[-1]
    bpy.context.scene.filter_items = prev_cluster


def get_func(module_name):
    lib_name = 'traces_filters.{}'.format(module_name)
    lib = importlib.import_module(lib_name)
    importlib.reload(lib)
    return getattr(lib, 'filter_traces')


def module_has_func(module_name):
    try:
        f = get_func(module_name)
        return True
    except:
        return False


def get_filter_functions():
    functions_names = []
    files = glob.glob(op.join(op.sep.join(__file__.split(op.sep)[:-1]), 'traces_filters', '*.py'))
    for fname in files:
        file_name = op.splitext(op.basename(fname))[0]
        if module_has_func(file_name):
            functions_names.append(file_name)
    bpy.types.Scene.filter_curves_func = bpy.props.EnumProperty(
        items=[(module_name, module_name, '', k + 1) for k, module_name in enumerate(functions_names)],
        description='List of functions.\n\nCurrent function')


def subselect_update(self=None, context=None):
    mu.filter_graph_editor(context.scene.filter_fcurves)


class FindCurveClosestToCursor(bpy.types.Operator):
    bl_idname = "mmvt.curve_close_to_cursor"
    bl_label = "curve close to cursor"
    bl_description = 'Shows the name of the closest curve to the cursor below the button.\n\nScript: mmvt.filter.find_obj_with_val()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        find_obj_with_val()
        return {"FINISHED"}


class GrabFromFiltering(bpy.types.Operator):
    bl_idname = "mmvt.grab_from"
    bl_label = "grab from"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        context.scene.filter_from = bpy.context.scene.frame_current
        mu.select_time_range(t_start=context.scene.frame_current)
        return {"FINISHED"}


class GrabToFiltering(bpy.types.Operator):
    bl_idname = "mmvt.grab_to"
    bl_label = "grab to"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        context.scene.filter_to = bpy.context.scene.frame_current
        mu.select_time_range(t_end=context.scene.frame_current)
        return {"FINISHED"}


class ClearFiltering(bpy.types.Operator):
    bl_idname = "mmvt.filter_clear"
    bl_label = "filter clear"
    bl_description = 'Clears the filtered curves'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        clear_filtering()
        type_of_filter = bpy.context.scene.filter_curves_type
        if type_of_filter == 'MEG':
            _addon().select_all_rois()
            _addon().clear_contours()
            # _addon().clear_cortex()
        elif type_of_filter == 'MEG_sensors':
            _addon().select_all_meg_sensors()
        elif type_of_filter == 'Electrodes':
            _addon().select_all_electrodes()
        elif type_of_filter == 'EEG':
            _addon().select_all_eeg_sensors()
        bpy.data.scenes['Scene'].frame_preview_end = _addon().get_max_time_steps()
        bpy.data.scenes['Scene'].frame_preview_start = 1
        bpy.types.Scene.closest_curve_str = ''
        bpy.types.Scene.filter_is_on = False
        mu.unfilter_graph_editor()
        return {"FINISHED"}


class PrevFilterItem(bpy.types.Operator):
    bl_idname = 'mmvt.prev_filter_item'
    bl_label = 'prev_filter_item'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        prev_filter_item()
        return {'FINISHED'}


class NextFilterItem(bpy.types.Operator):
    bl_idname = 'mmvt.next_filter_item'
    bl_label = 'next_filter_item'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        next_filter_item()
        return {'FINISHED'}

class ResetCurvesFilter(bpy.types.Operator):
    bl_idname = "mmvt.reset_curves_filter"
    bl_label = "reset_curves_filter"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.filter_fcurves = ''
        return {"FINISHED"}

class Filtering(bpy.types.Operator):
    bl_idname = "mmvt.filter"
    bl_label = "Filter deep elctrodes"
    bl_description = 'Filters the modality according the preferences set above'
    bl_options = {"UNDO"}
    topK = -1
    filter_from = 100000
    filter_to = -100000
    current_activity_path = ''
    type_of_filter = None
    type_of_func = None
    current_file_to_upload = ''
    current_root_path = mu.get_user_fol()
    objects_indices = []
    filter_objects = []
    filter_values = []
    objs_colors = []

    def get_object_to_filter(self, source_files, data=None, names=None):
        if data is None:
            data, names = [], []
            for input_file in source_files:
                try:
                    f = np.load(input_file)
                    data.append(f['data'])
                    names.extend([name.astype(str) for name in f['names']])
                except:
                    mu.message(self, "Can't load {}!".format(input_file))
                    return None, None, None

        # print('filtering {}-{}'.format(self.filter_from, self.filter_to))

        # t_range = range(self.filter_from, self.filter_to + 1)
        if self.topK > 0:
            self.topK = min(self.topK, len(names))
        # print(self.type_of_func)
        filter_func = get_func(self.type_of_func)
        if isinstance(data, list):
            d = np.vstack((d for d in data))
        else:
            d = data
        # print('%%%%%%%%%%%%%%%%%%%' + str(len(d[0, :, 0])))
        t_range = range(max(self.filter_from, 1), min(self.filter_to, len(d[0, :, 0])) - 1)
        objects_to_filtter_in, dd = filter_func(d, t_range, self.topK, bpy.context.scene.coloring_lower_threshold)
        # print(dd[objects_to_filtter_in])
        return objects_to_filtter_in, names, dd

    def filter_electrodes_or_sensors(self, parent_name, data, meta):
        # source_files = [op.join(self.current_activity_path, current_file_to_upload)]
        objects_indices, names, Filtering.filter_values = self.get_object_to_filter([], data, meta['names'])
        names = [mu.to_str(e) for e in meta['names']]
        Filtering.objects_indices, Filtering.filter_objects = objects_indices, names
        if objects_indices is None:
            return
        for obj in bpy.data.objects:
            obj.select = False
        parent_obj = bpy.data.objects[parent_name]
        for obj in parent_obj.children:
            obj.active_material.node_tree.nodes["Layer Weight"].inputs[0].default_value = 1

        if bpy.context.scene.selection_type == 'diff' and not parent_obj.animation_data is None:
            filter_obj_names = [names[ind] for ind in objects_indices]
            for fcurve in parent_obj.animation_data.action.fcurves:
                con_name = mu.get_fcurve_name(fcurve)
                fcurve.hide = con_name not in filter_obj_names
                fcurve.select = not fcurve.hide
            parent_obj.select = True
        else:
            parent_obj.select = False

        for ind in range(min(self.topK, len(objects_indices)) - 1, -1, -1):
            if bpy.data.objects.get(names[objects_indices[ind]]):
                orig_name = bpy.data.objects[names[objects_indices[ind]]].name
                filter_electrode_or_sensor(orig_name)
            else:
                print("Can't find {}!".format(names[objects_indices[ind]]))

    def filter_rois(self, current_file_to_upload):
        print('filter_ROIs')
        source_files = [op.join(self.current_activity_path, current_file_to_upload.format(hemi=hemi)) for hemi
                        in mu.HEMIS]
        objects_indices, names, Filtering.filter_values = self.get_object_to_filter(source_files)
        Filtering.objects_indices, Filtering.filter_objects = objects_indices, names
        deselect_all_objects()

        filter_obj_names = [names[ind] for ind in objects_indices]
        if bpy.context.scene.selection_type == 'diff':
            brain_obj = bpy.data.objects['Brain']
            self.objs_colors = []
            for fcurve in brain_obj.animation_data.action.fcurves:
                con_name = mu.get_fcurve_name(fcurve)
                fcurve.hide = con_name not in filter_obj_names
                fcurve.select = not fcurve.hide
                if fcurve.select:
                    self.objs_colors.append(fcurve.color)
            brain_obj.select = True
            _addon().color_contours(filter_obj_names, specific_colors=self.objs_colors, move_cursor=False)
        else:
            for roi_name in filter_obj_names:
                bpy.data.objects[roi_name].select = True
            self.objs_colors = mu.change_selected_fcurves_colors(mu.OBJ_TYPES_ROIS)
            _addon().color_contours(filter_obj_names, specific_colors=self.objs_colors, move_cursor=False)

    def invoke(self, context, event=None):
        _addon().change_view3d()
        #todo: why should we call setup layers here??
        # _addon().setup_layers()
        self.topK = bpy.context.scene.filter_topK
        self.filter_from = bpy.context.scene.filter_from
        self.filter_to = bpy.context.scene.filter_to
        self.current_activity_path = mu.get_user_fol() # bpy.path.abspath(bpy.context.scene.conf_path)
        # self.current_activity_path = bpy.path.abspath(bpy.context.scene.activity_path)
        self.type_of_filter = bpy.context.scene.filter_curves_type
        self.type_of_func = bpy.context.scene.filter_curves_func
        atlas = bpy.context.scene.atlas
        files_names = {
            'MEG': op.join('meg', 'labels_data_{}_{}.npz'.format(
                bpy.context.scene.meg_labels_data_files, '{hemi}')),
            'MEG_sensors': op.join('meg', 'meg_sensors_evoked_data.npy'),
            'Electrodes': op.join('electrodes', 'electrodes_data_{stat}.npz'),
            'EEG': op.join('eeg', 'eeg_data.npz')}
        current_file_to_upload = files_names[self.type_of_filter]

        if self.type_of_filter == 'Electrodes':
            data, meta = get_deep_electrodes_data()
            self.filter_electrodes_or_sensors('Deep_electrodes', data, meta)
        elif self.type_of_filter == 'EEG':
            data, meta = _addon().get_eeg_sensors_data()
            self.filter_electrodes_or_sensors('EEG_sensors', data, meta)
        elif self.type_of_filter == 'MEG':
            self.filter_rois(current_file_to_upload)
        elif self.type_of_filter == 'MEG_sensors':
            data, meta = _addon().get_meg_sensors_data()
            self.filter_electrodes_or_sensors('MEG_sensors', data, meta)

        if bpy.context.scene.filter_items_one_by_one:
            update_filter_items(self.topK, self.objects_indices, self.filter_objects)
        else:
            mu.view_all_in_graph_editor(context)
        # bpy.context.screen.areas[2].spaces[0].dopesheet.filter_fcurve_name = '*'
        return {"FINISHED"}


def get_deep_electrodes_data():
    # todo: should be called once (maybe those files are already loaded?
    fol = op.join(mu.get_user_fol(), 'electrodes')
    bip = 'bipolar_' if bpy.context.scene.bipolar else ''
    meta_files = glob.glob(op.join(fol, 'electrodes_{}meta*.npz'.format(bip)))
    if len(meta_files) > 0:
        data_files = glob.glob(op.join(fol, 'electrodes_{}data*.npy'.format(bip)))
        print('Loading data file: {}'.format(data_files[0]))
        print('Loading meta data file: {}'.format(meta_files[0]))
        data = np.load(data_files[0])
        meta = np.load(meta_files[0])
    else:
        data_files = glob.glob(op.join(mu.get_user_fol(), 'electrodes', 'electrodes_{}data*.npz'.format(bip)))
        print('Loading data file: {}'.format(data_files[0]))
        meta = np.load(data_files[0])
        data = meta['data']
    # todo: check if this part is needed
    if len(data_files) == 0:
        print('No data files!')
    elif len(data_files) == 1:
        current_file_to_upload = data_files[0]
    else:
        print('More the one data file!')
        current_file_to_upload = data_files[0]
        # todo: should decide which one to pick
        # current_file_to_upload = current_file_to_upload.format(
        #     stat='avg' if bpy.context.scene.selection_type == 'conds' else 'diff')
    return data, meta


bpy.types.Scene.closest_curve_str = ''
bpy.types.Scene.filter_is_on = False

bpy.types.Scene.closest_curve = bpy.props.StringProperty(description="Find closest curve to cursor")
bpy.types.Scene.filter_topK = bpy.props.IntProperty(default=1, min=0, description='Sets the top curves number')
bpy.types.Scene.filter_from = bpy.props.IntProperty(
    default=0, min=0, update=filter_from_to_update, description='Sets the starting time point of the activity')
bpy.types.Scene.filter_to = bpy.props.IntProperty(
    default=bpy.context.scene.frame_end, min=0, update=filter_from_to_update, description='Sets the ending time point of the activity')
bpy.types.Scene.filter_curves_type = bpy.props.EnumProperty(
    items=[("MEG", "MEG time course", "", 1), ('MEG_sensors', 'MEG sensors', '', 2),
           ("Electrodes", " Electrodes time course", "", 3), ("EEG", "EEG sensors", "", 4),
           ('fMRI', 'fMRI dynamics', '', 4)],
    description='List of modalities.\n\nCurrent modality')
bpy.types.Scene.filter_curves_func = bpy.props.EnumProperty(items=[], description='List of functions.\n\nCurrent function')
    # items=[("RMS", "RMS", "RMS between the two conditions", 1), ("SumAbs", "SumAbs", "Sum of the abs values", 2),
    #        ("threshold", "Above threshold", "", 3)],
bpy.types.Scene.mark_filter_items = bpy.props.BoolProperty(default=True, description='Shows the filtered objects on the brain')
bpy.types.Scene.filter_items = bpy.props.EnumProperty(items=[], description="Filtering items")
bpy.types.Scene.filter_items_one_by_one = bpy.props.BoolProperty(
    default=False, update=show_one_by_one_update, description='Shows each curve separately')
bpy.types.Scene.filter_fcurves = bpy.props.StringProperty(name="Subselect:", update=subselect_update,
    description='Filters curves by name or first letters')


class FilteringMakerPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Filter number of curves"
    addon = None
    init = False
    electrodes_colors = {}
    filter_items = []

    def draw(self, context):
        filter_draw(self, context)


def init(addon):
    FilteringMakerPanel.addon = addon
    get_filter_functions()
    bpy.context.scene.mark_filter_items = True
    FilteringMakerPanel.init = True
    filter_from_to_update()
    register()


def register():
    try:
        unregister()
        bpy.utils.register_class(Filtering)
        bpy.utils.register_class(FilteringMakerPanel)
        bpy.utils.register_class(ClearFiltering)
        bpy.utils.register_class(GrabToFiltering)
        bpy.utils.register_class(GrabFromFiltering)
        bpy.utils.register_class(FindCurveClosestToCursor)
        bpy.utils.register_class(PrevFilterItem)
        bpy.utils.register_class(NextFilterItem)
        bpy.utils.register_class(ResetCurvesFilter)
        # print('Filtering Panel was registered!')
    except:
        print("Can't register Filtering Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(Filtering)
        bpy.utils.unregister_class(FilteringMakerPanel)
        bpy.utils.unregister_class(ClearFiltering)
        bpy.utils.unregister_class(GrabToFiltering)
        bpy.utils.unregister_class(GrabFromFiltering)
        bpy.utils.unregister_class(FindCurveClosestToCursor)
        bpy.utils.unregister_class(PrevFilterItem)
        bpy.utils.unregister_class(NextFilterItem)
        bpy.utils.unregister_class(ResetCurvesFilter)
    except:
        pass

