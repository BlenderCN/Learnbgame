import bpy
import bpy_extras
import os.path as op
import glob
import time
import traceback
import shutil
import numpy as np
import re
import mmvt_utils as mu
import colors_utils as cu
import mne


def _addon():
    return LabelsPanel.addon


def contours_coloring_update(self, context):
    _addon().set_no_plotting(True)
    LabelsPanel.labels_contours = labels_contours = load_labels_contours()
    items = [('all labels', 'all labels', '', 0)]
    for hemi_ind, hemi in enumerate(mu.HEMIS):
        LabelsPanel.labels[hemi] = labels_contours[hemi]['labels']
        extra = 0 if hemi_ind == 0 else len(labels_contours[mu.HEMIS[0]]['labels'])
        items.extend([(c, c, '', ind + extra + 1) for ind, c in enumerate(labels_contours[hemi]['labels'])])
    bpy.types.Scene.labels_contours = bpy.props.EnumProperty(items=items, update=labels_contours_update,
        description='List of all labels names. Plots selected label contour.\n\nCurrent label')
    bpy.context.scene.labels_contours = 'all labels' #d[hemi]['labels'][0]
    _addon().set_no_plotting(False)


def labels_contours_filter_update(self, context):
    filter_re = re.compile(bpy.context.scene.labels_contours_filter)
    items = []
    labels_contours = LabelsPanel.labels_contours
    for hemi_ind, hemi in enumerate(mu.HEMIS):
        labels_contours_hemi = [l for l in labels_contours[hemi]['labels'] if filter_re.search(l)]
        LabelsPanel.labels[hemi] = labels_contours_hemi
        extra = 0 if hemi_ind == 0 else len(labels_contours[mu.HEMIS[0]]['labels'])
        items.extend([(c, c, '', ind + extra ) for ind, c in enumerate(labels_contours_hemi)])
    bpy.types.Scene.labels_contours = bpy.props.EnumProperty(items=items, update=labels_contours_update)


def load_labels_contours(atlas=''):
    labels_contours = {}
    if atlas == '':
        atlas = bpy.context.scene.contours_coloring
    for hemi in mu.HEMIS:
        labels_contours[hemi] = np.load(op.join(mu.get_user_fol(), 'labels', '{}_contours_{}.npz'.format(atlas, hemi)))
        if len(np.where(labels_contours[hemi]['contours'])[0]) == 0:
            print('No contours in {} {}!'.format(atlas, hemi))
    return labels_contours


def labels_contours_update(self, context):
    if not _addon().coloring_panel_initialized or _addon().get_no_plotting():
        return
    if bpy.context.scene.labels_contours == 'all labels':
        color_contours(cumulate=bpy.context.scene.cumulate_contours)
    else:
        hemi = 'rh' if bpy.context.scene.labels_contours in LabelsPanel.labels['rh'] else 'lh'
        color_contours(bpy.context.scene.labels_contours, hemi, cumulate=bpy.context.scene.cumulate_contours)


def clear_contours():
    # todo: there is a better way to do it
    labels_contours = LabelsPanel.labels_contours
    for hemi in mu.HEMIS:
        contours = labels_contours[hemi]['contours']
        selected_contours = np.zeros(contours.shape)
        mesh = mu.get_hemi_obj(hemi).data
        mesh.vertex_colors.active_index = mesh.vertex_colors.keys().index('contours')
        mesh.vertex_colors['contours'].active_render = True
        _addon().color_hemi_data(hemi, selected_contours, 0.1, 256, override_current_mat=True,
                        coloring_layer='contours', check_valid_verts=False)


def plot_labels_data():
    # Support more than one file type (npz and mat)
    labels_data_template = op.join(mu.get_user_fol(), 'labels', 'labels_data', '{}.*'.format(
        bpy.context.scene.labels_data_files.replace(' ', '_')))
    labels_data_fnames = glob.glob(labels_data_template)
    if len(labels_data_fnames) == 1:
        load_labels_data(labels_data_fnames[0])
    else:
        print('No files found! {}'.format(labels_data_template))


def labels_data_files_update(self, context):
    if LabelsPanel.init:
        labels_data_fname = glob.glob(op.join(mu.get_user_fol(), 'labels', 'labels_data', '{}.*'.format(
            bpy.context.scene.labels_data_files.replace(' ', '_'))))[0]
        ret = _load_labels_data(labels_data_fname)
        if isinstance(ret, bool):
            return
        d, labels, data, atlas, cb_title, labels_max, labels_min, cmap = ret
        _addon().init_labels_colorbar(data, cb_title, labels_max, labels_min, cmap)


def new_label_r_update(self, context):
    build_new_label_name()


def build_new_label_name():
    closest_label_output = bpy.context.scene.closest_label_output
    if closest_label_output == '':
        new_label_name = 'Unknown'
    else:
        delim, pos, label, label_hemi = mu.get_hemi_delim_and_pos(closest_label_output)
        label = '{}-{}mm'.format(label, bpy.context.scene.new_label_r)
        new_label_name = mu.build_label_name(delim, pos, label, label_hemi)
    bpy.context.scene.new_label_name = new_label_name


def grow_a_label():
    closest_mesh_name, vertex_ind, _ = \
        _addon().find_closest_vertex_index_and_mesh(use_shape_keys=True)
    hemi = closest_mesh_name[len('infalted_'):] if _addon().is_inflated() else closest_mesh_name
    subject, atlas = mu.get_user(), bpy.context.scene.subject_annot_files
    label_name, label_r = bpy.context.scene.new_label_name, bpy.context.scene.new_label_r
    flags = '-a {} --vertice_indice {} --hemi {} --label_name {} --label_r {}'.format(
        atlas, vertex_ind, hemi, label_name, label_r)
    mu.run_mmvt_func('src.preproc.anatomy', 'grow_label', flags=flags)


def color_contours(specific_labels=[], specific_hemi='both', labels_contours=None, cumulate=False, change_colorbar=False,
                   specific_colors=None, atlas='', move_cursor=True, filter=''):
    if _addon() is None:
        return
    if filter != '':
        bpy.context.scene.labels_contours_filter = filter
        if isinstance(LabelsPanel.labels['rh'], np.ndarray):
            specific_labels = LabelsPanel.labels['rh'].tolist() + LabelsPanel.labels['lh'].tolist()
        else:
            specific_labels = LabelsPanel.labels['rh'] + LabelsPanel.labels['lh']
    elif isinstance(specific_labels, str):
        specific_labels = [specific_labels]
    if atlas != '' and atlas != bpy.context.scene.contours_coloring and atlas in LabelsPanel.existing_contoures:
        bpy.context.scene.contours_coloring = atlas
    if atlas == '' and bpy.context.scene.atlas in LabelsPanel.existing_contoures:
        bpy.context.scene.contours_coloring = bpy.context.scene.atlas
    if labels_contours is None:
        labels_contours = LabelsPanel.labels_contours
    contour_max = max([labels_contours[hemi]['max'] for hemi in mu.HEMIS])
    if contour_max == 0:
        print('No contours!')
        return False
    if not _addon().colorbar_values_are_locked() and change_colorbar:
        _addon().set_colormap('jet')
        _addon().set_colorbar_title('{} labels contours'.format(bpy.context.scene.contours_coloring))
        _addon().set_colorbar_max_min(contour_max, 1)
        _addon().set_colorbar_prec(0)
    _addon().show_activity()
    specific_label_ind = 0
    if specific_colors is not None:
        specific_colors = np.tile(specific_colors, (len(specific_labels), 1))
    for hemi in mu.HEMIS:
        contours = labels_contours[hemi]['contours']
        if specific_hemi != 'both' and hemi != specific_hemi:
            selected_contours = np.zeros(contours.shape) if specific_colors is None else np.zeros((contours.shape[0], 4))
        elif len(specific_labels) > 0:
            selected_contours = np.zeros(contours.shape) if specific_colors is None else np.zeros((contours.shape[0], 4))
            for specific_label in specific_labels:
                if mu.get_hemi_from_fname(specific_label) != hemi:
                    continue
                label_ind = np.where(np.array(labels_contours[hemi]['labels']) == specific_label)
                if len(label_ind) > 0 and len(label_ind[0]) > 0:
                    label_ind = label_ind[0][0]
                    selected_contours[np.where(contours == label_ind + 1)] = \
                        label_ind + 1 if specific_colors is None else [1, *specific_colors[specific_label_ind]]
                    specific_label_ind += 1
                    if move_cursor and len(specific_labels) == 1 and 'centers' in labels_contours[hemi]:
                        vert = labels_contours[hemi]['centers'][label_ind]
                        _addon().move_cursor_according_to_vert(vert, 'inflated_{}'.format(hemi))
                        _addon().set_closest_vertex_and_mesh_to_cursor(vert, 'inflated_{}'.format(hemi))
                        _addon().create_slices()
                        _addon().snap_cursor(True)
                        _addon().set_tkreg_ras(bpy.context.scene.cursor_location * 10, False)
                else:
                    print("Can't find {} in the labels contours!".format(specific_label))
        else:
            selected_contours = labels_contours[hemi]['contours']
        mesh = mu.get_hemi_obj(hemi).data
        mesh.vertex_colors.active_index = mesh.vertex_colors.keys().index('contours')
        mesh.vertex_colors['contours'].active_render = True
        _addon().color_hemi_data(hemi, selected_contours, 0.1, 256 / contour_max, override_current_mat=not cumulate,
                        coloring_layer='contours', check_valid_verts=False)
    _addon().what_is_colored().add(_addon().WIC_CONTOURS)

    # if bpy.context.scene.contours_coloring in _addon().get_annot_files():
    #     bpy.context.scene.subject_annot_files = bpy.context.scene.contours_coloring


def load_labels_data(labels_data_fname):
    ret = _load_labels_data(labels_data_fname)
    if isinstance(ret, bool):
        return ret
    d, labels, data, atlas, cb_title, labels_max, labels_min, cmap = ret
    _addon().color_labels_data(labels, data, atlas, cb_title, labels_max, labels_min, cmap)
    new_fname = op.join(mu.get_user_fol(), 'labels', 'labels_data', mu.namebase_with_ext(labels_data_fname))
    if 'atlas' not in d:
        npz_dict = dict(d)
        npz_dict['atlas'] = atlas
        np.savez(new_fname, **npz_dict)
    else:
        if new_fname != labels_data_fname:
            shutil.copy(labels_data_fname, new_fname)
        # init_labels_data_files()
    if atlas in _addon().where_am_i.get_annot_files() and bpy.context.scene.subject_annot_files != atlas:
        bpy.context.scene.subject_annot_files = atlas
    bpy.context.scene.find_closest_label_on_click = True
    _addon().find_closest_label(atlas=atlas, plot_contour=bpy.context.scene.plot_closest_label_contour)
    return True


def _load_labels_data(labels_data_fname):
    labels_data_type = mu.file_type(labels_data_fname)
    if labels_data_type == 'npz':
        d = mu.load_npz_to_bag(labels_data_fname)
    elif labels_data_type == 'mat':
        d = mu.load_mat_to_bag(labels_data_fname)
        d.names = mu.matlab_cell_str_to_list(d.names)
        d.atlas = d.atlas[0] if not isinstance(d.atlas, str) else d.atlas
        #d.cmap = d.cmap[0] if not isinstance(d.cmap, str) else d.cmap
    else:
        print('Currently we support only mat and npz files')
        return False
    labels, data = d.names, d.data
    if len(labels) == 0:
        return False
    if isinstance(labels[0], mne.Label):
        labels = [l.name for l in labels]
    if data.ndim == 2:
        if data.shape[0] == len(labels):
            data = data[:, bpy.context.scene.frame_current]
        elif data.shape[1] == len(labels):
            data = data[bpy.context.scene.frame_current]
        else:
            data = data.mean(axis=1) if data.shape[0] == len(labels) else data.mean(axis=0)
    if 'atlas' not in d:
        atlas = mu.check_atlas_by_labels_names(labels)
        if atlas == '':
            print('The labeling file must contains an atlas field!')
            return False
    else:
        atlas = str(d.atlas)
    LabelsPanel.atlas_in_annot_files = atlas in _addon().where_am_i.get_annot_files()
    LabelsPanel.labels_data_atlas = atlas
    labels = [l.replace('.label', '') for l in labels]
    cb_title = str(d.get('title', ''))
    labels_min = d.get('data_min', np.min(data))
    labels_max = d.get('data_max', np.max(data))
    cmap = str(d.get('cmap', None))
    return d, labels, data, atlas, cb_title, labels_max, labels_min, cmap


def plot_label(label, color=''):
    if isinstance(label, str):
        label = mu.read_label_file(label)
    else:
        try:
            _, _, _ = label.name, label.vertices, label.pos
        except:
            raise Exception('plot_label: label can be label fname or label object!')

    if bpy.context.scene.plot_label_contour:
        _addon().color_contours(specific_labels=[label.name])
    else:
        color = list(bpy.context.scene.labels_color) if color == '' else color
        LabelsPanel.labels_plotted.append((label, color))
        _plot_labels()


def _plot_labels(labels_plotted_tuple=None, faces_verts=None, choose_rand_colors=False):
    if labels_plotted_tuple is None:
        labels_plotted_tuple = LabelsPanel.labels_plotted
    if faces_verts is None:
        faces_verts = _addon().coloring.get_faces_verts()
    hemi_verts_num = {hemi: faces_verts[hemi].shape[0] for hemi in mu.HEMIS}
    data = {hemi: np.zeros((hemi_verts_num[hemi], 4)) for hemi in mu.HEMIS}
    colors_num = len(labels_plotted_tuple)
    rand_colors = mu.get_distinct_colors(colors_num) if choose_rand_colors else [''] * colors_num
    for (label, color), rand_color in zip(labels_plotted_tuple, rand_colors):
        label.vertices = label.vertices[label.vertices < hemi_verts_num[label.hemi]]
        if choose_rand_colors:
            color = rand_color
        data[label.hemi][label.vertices] = [1, *color]
    for hemi in mu.HEMIS:
        _addon().coloring.color_hemi_data('inflated_{}'.format(hemi), data[hemi], threshold=0.5)
    _addon().show_activity()


def plot_labels(labels_names, colors, atlas, atlas_labels_rh=[], atlas_labels_lh=[], do_plot=True):
    if len(atlas_labels_rh) == 0 and len(atlas_labels_lh) == 0: # or atlas == bpy.context.scene.atlas:
        atlas_labels_rh = mu.read_labels_from_annots(atlas, hemi='rh')
        atlas_labels_lh = mu.read_labels_from_annots(atlas, hemi='lh')
    atlas_labels = atlas_labels_rh + atlas_labels_lh
    if len(atlas_labels) == 0:
        print("Couldn't find the atlas! ({})".format(atlas))
        return
    annot_verts_ok = check_annot_verts(atlas_labels_lh, atlas_labels_rh, atlas)
    if not annot_verts_ok:
        return
    org_delim, org_pos, label, label_hemi = mu.get_hemi_delim_and_pos(atlas_labels[0].name)
    labels_names_fix = []
    for label_name in labels_names:
        delim, pos, label, label_hemi = mu.get_hemi_delim_and_pos(label_name)
        label = mu.get_label_hemi_invariant_name(label_name)
        label_fix = mu.build_label_name(org_delim, org_pos, label, label_hemi)
        labels_names_fix.append(label_fix)
    labels = [l for l in atlas_labels if l.name in labels_names_fix]
    if len(labels) < len(labels_names):
        dump_fname = op.join(mu.get_user_fol(), 'logs', '{}_labels.txt'.format(atlas))
        print("Can't find all the labels ({}) in the {} atlas!".format(labels_names, atlas))
        print("Take a look here for the {} labels names: {}".format(atlas, dump_fname))
        with open(dump_fname, 'w') as output_file:
            output_file.write("Can't find all the labels ({}) in the {} atlas!\n".format(labels_names, atlas))
            output_file.write("Take a look here for the {} labels names:\n".format(atlas))
            for label in atlas_labels:
                output_file.write('{}\n'.format(label.name))
        import webbrowser
        webbrowser.open_new(dump_fname)
        return
    labels.sort(key=lambda x: labels_names_fix.index(x.name))
    # todo: check if bpy.context.scene.color_rois_homogeneously
    for label, color in zip(labels, colors):
        print('color {}: {}'.format(label, color))
        # plot_label(label, color)
        LabelsPanel.labels_plotted.append((label, color))
    if do_plot:
        _plot_labels()


def check_annot_verts(atlas_labels_lh, atlas_labels_rh, atlas):
    annot_verts_num_lh = max([max(l.vertices) for l in atlas_labels_lh]) if len(atlas_labels_lh) > 0 else 0
    annot_verts_num_rh = max([max(l.vertices) for l in atlas_labels_rh]) if len(atlas_labels_rh) > 0 else 0
    hemi_verts_num_lh = len(bpy.data.objects['lh'].data.vertices)
    hemi_verts_num_rh = len(bpy.data.objects['rh'].data.vertices)
    if annot_verts_num_lh >= hemi_verts_num_lh or annot_verts_num_rh >= hemi_verts_num_rh:
        print('{} has wrong number of vertices!'.format(atlas))
        print('rh: annot {}, hemi {}'.format(annot_verts_num_lh, hemi_verts_num_lh))
        print('lh: annot {}, hemi {}'.format(annot_verts_num_rh, hemi_verts_num_rh))
        return False
    else:
        return True


def plot_labels_folder():
    labels_files = glob.glob(op.join(bpy.path.abspath(bpy.context.scene.labels_folder), '*.label'))
    if len(labels_files) == 0:
        print('No labels were found in {}!'.format(op.realpath(bpy.context.scene.labels_folder)))
    else:
        colors = cu.get_distinct_colors_hs(len(labels_files))
        # todo: same color for each hemi
        for label_fname, color in zip(labels_files, colors):
            plot_label(label_fname)


def get_labels_plotted():
    return LabelsPanel.labels_plotted


def set_labels_plotted(val):
    LabelsPanel.labels_plotted = val


def both_dkt():
    return bpy.context.scene.atlas.startswith('aparc.DKTatlas') and \
           LabelsPanel.labels_data_atlas.startswith('aparc.DKTatlas')


def labels_draw(self, context):
    layout = self.layout

    col = layout.box().column()
    col.label(text='Cortical labels data:')
    if len(LabelsPanel.labels_data_files) > 0:
        col.prop(context.scene, 'labels_data_files', text='')
        if LabelsPanel.labels_data_atlas == bpy.context.scene.atlas or both_dkt():
            col.prop(context.scene, 'color_rois_homogeneously', text="Color labels homogeneously")
        if LabelsPanel.atlas_in_annot_files:
            row = col.row(align=True)
            row.prop(context.scene, 'find_closest_label_on_click', text='Find label on click')
            if _addon().get_labels_contours() is not None:
                row.prop(context.scene, 'plot_closest_label_contour', text="Plot label's contour")
        vertex_data = _addon().get_vertex_data()
        if bpy.context.scene.closest_label_output != '' and vertex_data != '' and vertex_data is not None:
            col.label(text='{} ({})'.format(bpy.context.scene.closest_label_output, vertex_data))
        elif bpy.context.scene.closest_label_output != '':
            col.label(text=bpy.context.scene.closest_label_output)
        elif vertex_data != '' and vertex_data is not None:
            col.label('Cursor value: {}'.format(vertex_data))
        col.operator(PlotLabelsData.bl_idname, text="Plot labels", icon='TPAINT_HLT')
        layout.prop(context.scene, 'plot_label_contour', text='Plot labels as contour')
    col.operator(ChooseLabesDataFile.bl_idname, text="Load labels file", icon='LOAD_FACTORY')

    if LabelsPanel.contours_coloring_exist:
        col = layout.box().column()
        col.label(text='Contours:')
        col.prop(context.scene, 'contours_coloring', '')
        col.operator(ColorContours.bl_idname, text="Plot Contours", icon='POTATO')
        row = col.row(align=True)
        row.operator(PrevLabelConture.bl_idname, text="", icon='PREV_KEYFRAME')
        row.prop(context.scene, 'labels_contours', '')
        row.operator(NextLabelConture.bl_idname, text="", icon='NEXT_KEYFRAME')
        row = col.row(align=True)
        row.prop(context.scene, 'labels_contours_filter', 'Filter')
        row.operator(ResetContoursFilter.bl_idname, text="", icon='PANEL_CLOSE')
        # col.prop(context.scene, 'cumulate_contours', 'Cumulate')

    col = layout.box().column()
    row = col.row(align=True)
    row.operator(ChooseLabelFile.bl_idname, text="plot a label", icon='GAME').filepath = op.join(
        mu.get_user_fol(), '*.label')
    row.prop(context.scene, 'labels_color', text='')
    if not GrowLabel.running:
        col.label(text='Creating a new label:')
        col.prop(context.scene, 'new_label_name', text='')
        col.prop(context.scene, 'new_label_r', text='Radius (mm)')
        txt = 'Grow a label' if bpy.context.scene.cursor_is_snapped else 'First Snap the cursor'
        col.operator(GrowLabel.bl_idname, text=txt, icon='OUTLINER_DATA_MESH')
    else:
        col.label(text='Growing the label...')

    layout.operator(ClearContours.bl_idname, text="Clear contours", icon='PANEL_CLOSE')
    layout.operator(_addon().ClearColors.bl_idname, text="Clear", icon='PANEL_CLOSE')


class PlotLabelsFolder(bpy.types.Operator):
    bl_idname = "mmvt.plot_labels_folder"
    bl_label = "mmvt plot labels folder"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        plot_labels_folder()
        return {'FINISHED'}
    

class ResetContoursFilter(bpy.types.Operator):
    bl_idname = "mmvt.reset_contours_filter"
    bl_label = "reset contours filter"

    def execute(self, context):
        bpy.context.scene.labels_contours_filter = ''
        return {'FINISHED'}


class ChooseLabesDataFile(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "mmvt.choose_labels_npz_file"
    bl_label = "Choose labels data"
    bl_description = 'Loads labels data file (npz/mat)'

    filename_ext = '.*'
    filter_glob = bpy.props.StringProperty(default='*.*', options={'HIDDEN'}, maxlen=255)

    def execute(self, context):
        _addon().load_labels_data(self.filepath.replace('.*', ''))
        return {'FINISHED'}


class GrowLabel(bpy.types.Operator):
    bl_idname = "mmvt.grow_label"
    bl_label = "mmvt grow label"
    bl_description = 'Creates the label according the features selected above'
    bl_options = {"UNDO"}
    running = False

    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
            GrowLabel.running = False
        return {'CANCELLED'}

    @staticmethod
    def invoke(self, context, event=None):
        if not bpy.context.scene.cursor_is_snapped:
            _addon().snap_cursor(True)
            _addon().find_closest_label()
            build_new_label_name()
        else:
            GrowLabel.running = True
            context.window_manager.modal_handler_add(self)
            self._timer = context.window_manager.event_timer_add(0.1, context.window)
            grow_a_label()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER' and GrowLabel.running:
            new_label_fname = op.join(
                mu.get_user_fol(), 'labels', '{}.label'.format(bpy.context.scene.new_label_name))
            if op.isfile(new_label_fname):
                _addon().plot_label(new_label_fname)
                GrowLabel.running = False
                self.cancel(context)
        return {'PASS_THROUGH'}


class PlotLabelsData(bpy.types.Operator):
    bl_idname = "mmvt.plot_labels_data"
    bl_label = "plot_labels_data"
    bl_description = 'Plots labels on the brain.\n\nScript: mmvt.labels.plot_labels_data()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        plot_labels_data()
        return {'PASS_THROUGH'}


class ColorContours(bpy.types.Operator):
    bl_idname = "mmvt.color_contours"
    bl_label = "mmvt color contours"
    bl_description = 'Plots the labels contours according the selected atlas above'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        if bpy.context.scene.labels_contours_filter == '':
            color_contours(atlas=bpy.context.scene.contours_coloring)
        else:
            if isinstance(LabelsPanel.labels['rh'], np.ndarray):
                labels = LabelsPanel.labels['rh'].tolist() + LabelsPanel.labels['lh'].tolist()
            else:
                labels = LabelsPanel.labels['rh'] + LabelsPanel.labels['lh']
            color_contours(labels, atlas=bpy.context.scene.contours_coloring)
        return {"FINISHED"}


class ClearContours(bpy.types.Operator):
    bl_idname = "mmvt.clear_contours"
    bl_label = "mmvt clear contours"
    bl_description = 'Clears the plotted contours.\n\nScript: mmvt.labels.clear_contours()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        clear_contours()
        return {"FINISHED"}


class PrevLabelConture(bpy.types.Operator):
    bl_idname = "mmvt.labels_contours_prev"
    bl_label = "mmvt labels contours prev"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        all_labels = np.concatenate((LabelsPanel.labels['rh'], LabelsPanel.labels['lh']))
        if bpy.context.scene.labels_contours == 'all labels':
            bpy.context.scene.labels_contours = all_labels[-1]
        else:
            label_ind = np.where(all_labels == bpy.context.scene.labels_contours)[0][0]
            bpy.context.scene.labels_contours = all_labels[label_ind - 1] if label_ind > 0 else all_labels[-1]
        return {"FINISHED"}


class NextLabelConture(bpy.types.Operator):
    bl_idname = "mmvt.labels_contours_next"
    bl_label = "mmvt labels contours next"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        all_labels = np.concatenate((LabelsPanel.labels['rh'], LabelsPanel.labels['lh']))
        if bpy.context.scene.labels_contours == 'all labels':
            bpy.context.scene.labels_contours = all_labels[0]
        else:
            label_ind = np.where(all_labels == bpy.context.scene.labels_contours)[0][0]
            bpy.context.scene.labels_contours = all_labels[label_ind + 1] \
                if label_ind < len(all_labels) else all_labels[0]
        return {"FINISHED"}


class ChooseLabelFile(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "mmvt.plot_label_file"
    bl_label = "Plot label file"
    bl_description = 'Plots label files of MNE type'

    filename_ext = '.label'
    filter_glob = bpy.props.StringProperty(default='*.label', options={'HIDDEN'}, maxlen=255)

    def execute(self, context):
        label_fname = self.filepath
        plot_label(label_fname)
        return {'FINISHED'}


bpy.types.Scene.labels_data_files = bpy.props.EnumProperty(
    items=[], update=labels_data_files_update, description='Selects labels file from the subject’s labels folder:'
    '\n../mmvt_root/mmvt_blend/colin27/labels/labels_data\n\nCurrent file')
bpy.types.Scene.new_label_name = bpy.props.StringProperty(description='Creates the labels name')
bpy.types.Scene.new_label_r = bpy.props.IntProperty(min=1, default=5, update=new_label_r_update,
    description='Selects the labels radius')
bpy.types.Scene.contours_coloring = bpy.props.EnumProperty(items=[],
    description='Selects the atlas to plot the labels contour\n\nCurrent atlas')
bpy.types.Scene.labels_contours = bpy.props.EnumProperty(items=[],
    description='List of all labels names. Plots selected label contour.\n\nCurrent label')
bpy.types.Scene.plot_label_contour = bpy.props.BoolProperty(default=False, description='Plots the labels as contours only')
bpy.types.Scene.labels_contours_filter = bpy.props.StringProperty(update=labels_contours_filter_update,
    description='Filters the labels list by a regular expression')
bpy.types.Scene.cumulate_contours = bpy.props.BoolProperty(default=False, description='cumulate contours')


class LabelsPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Cortical Labels"
    addon = None
    init = False
    
    labels_data_files = []
    existing_contoures = []
    labels_plotted = []
    contours_coloring_exist = False
    labels_contours = {}
    labels = dict(rh=[], lh=[])
    labels_data_atlas = ''
    atlas_in_annot_files = False

    def draw(self, context):
        if LabelsPanel.init:
            labels_draw(self, context)


def init(addon):
    LabelsPanel.addon = addon
    init_labels_data_files()
    init_contours_coloring()
    register()
    LabelsPanel.init = True


def init_contours_coloring():
    user_fol = mu.get_user_fol()
    contours_files = glob.glob(op.join(user_fol, 'labels', '*contours_lh.npz'))
    if len(contours_files) > 0:
        LabelsPanel.contours_coloring_exist = True
        LabelsPanel.existing_contoures = files_names = \
            [mu.namebase(fname)[:-len('_contours_lh')] for fname in contours_files]
        items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
        bpy.types.Scene.contours_coloring = bpy.props.EnumProperty(items=items, update=contours_coloring_update,
            description='Selects the atlas to plot the labels contour\n\nCurrent atlas')
        bpy.context.scene.contours_coloring = files_names[0]
    bpy.context.scene.cumulate_contours = False


def init_labels_data_files():
    user_fol = mu.get_user_fol()
    mu.make_dir(op.join(user_fol, 'labels', 'labels_data'))
    LabelsPanel.labels_data_files = labels_data_files = \
        glob.glob(op.join(user_fol, 'labels', 'labels_data', '*.npz')) + \
        glob.glob(op.join(user_fol, 'labels', 'labels_data', '*.mat'))
    try:
        if len(labels_data_files) > 0:
            files_names = [mu.namebase(fname).replace('_', ' ') for fname in labels_data_files]
            labels_items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
            bpy.types.Scene.labels_data_files = bpy.props.EnumProperty(
                items=labels_items, update=labels_data_files_update,
                description='Selects labels file from the subject’s labels folder:'
                '\n../mmvt_root/mmvt_blend/colin27/labels/labels_data\n\nCurrent file')
            bpy.context.scene.labels_data_files = files_names[0]
    except:
        print('init_labels_data_files: Error!')


def register():
    try:
        unregister()
        bpy.utils.register_class(LabelsPanel)
        bpy.utils.register_class(GrowLabel)
        bpy.utils.register_class(ColorContours)
        bpy.utils.register_class(ClearContours)
        bpy.utils.register_class(NextLabelConture)
        bpy.utils.register_class(PrevLabelConture)
        bpy.utils.register_class(PlotLabelsData)
        bpy.utils.register_class(ChooseLabesDataFile)
        bpy.utils.register_class(ChooseLabelFile)
        bpy.utils.register_class(ResetContoursFilter)
    except:
        print("Can't register Labels Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(LabelsPanel)
        bpy.utils.unregister_class(GrowLabel)
        bpy.utils.unregister_class(ColorContours)
        bpy.utils.unregister_class(ClearContours)
        bpy.utils.unregister_class(NextLabelConture)
        bpy.utils.unregister_class(PrevLabelConture)
        bpy.utils.unregister_class(PlotLabelsData)
        bpy.utils.unregister_class(ChooseLabesDataFile)
        bpy.utils.unregister_class(ChooseLabelFile)
        bpy.utils.unregister_class(ResetContoursFilter)
    except:
        pass
