import bpy
import mmvt_utils as mu
import colors_utils as cu
import os.path as op
import glob
import time
import numpy as np
from collections import defaultdict

PARENT_OBJ_NAME = 'Deep_electrodes'


def _addon():
    return ElecsPanel.addon


def get_electrodes_names():
    parent = bpy.data.objects.get('Deep_electrodes')
    electrodes_names = [o.name for o in parent.children] if parent is not None else []
    return electrodes_names


# bpy.types.Scene.electrodes_hemis = bpy.props.EnumProperty(
#     items=[('left', 'lh', '', 1), ('right', 'rh', '', 2)], update=electrodes_hemis_update)
# bpy.types.Scene.electrodes_hemi_labels = bpy.props.EnumProperty(items=[])

def electrodes_hemis_update(self, context):
    if bpy.context.scene.electrodes_hemis == 'rh':
        labels = []


def elc_size_update(self, context):
    try:
        for elec_obj in ElecsPanel.parent.children:
            elec_obj.scale[0] = bpy.context.scene.elc_size
            elec_obj.scale[1] = bpy.context.scene.elc_size
            elec_obj.scale[2] = bpy.context.scene.elc_size
    except:
        pass


def show_electrodes_labels_update(self, context):
    for elec_obj in ElecsPanel.parent.children:
        elec_obj.show_name = bpy.context.scene.show_electrodes_labels


def set_show_electrodes_groups_leads(val):
    bpy.context.scene.show_electrodes_groups_leads = val


def show_electrodes_groups_leads_update(self, context):
    parent_name = 'leads'
    leads_obj = bpy.data.objects.get(parent_name, None)
    show_leads = bpy.context.scene.show_electrodes_groups_leads
    if show_leads and leads_obj is None:
        leads_obj = mu.create_empty_if_doesnt_exists(parent_name, _addon().BRAIN_EMPTY_LAYER, None)
    elif not show_leads and leads_obj is None:
        return

    if len(leads_obj.children) == 0:
        for group, electrodes in ElecsPanel.groups_electrodes.items():
            points = [get_elc_pos(e) for e in electrodes]
            # points_inside_cylinder, _, dists = mu.points_in_cylinder(
            #     get_elc_pos(electrodes[0]), get_elc_pos(electrodes[-1]), points, 0.1)
            # if len(points_inside_cylinder) == len(electrodes):
            if bpy.context.scene.electrodes_create_curved_leads:
                for ind, (p1, p2) in enumerate(zip(points[:-1], points[1:])):
                    create_lead(p1, p2, '{}_lead_{}'.format(group, ind))
            else:
                create_lead(get_elc_pos(electrodes[0]), get_elc_pos(electrodes[-1]), '{}_lead'.format(group))
            # group_new_pos = mu.move_electrodes_to_line(get_elc_pos(electrodes[0]), get_elc_pos(electrodes[-1]), points)
            # for elc_name, elc_new_pos in zip(electrodes, group_new_pos):
            #     bpy.data.objects[elc_name].location = elc_new_pos


    for group_lead_obj in leads_obj.children:
        group_lead_obj.hide = not show_leads


def create_lead(p1, p2, lead_name, radius=0.03):
    if bpy.data.objects.get(lead_name) is not None:
        return bpy.data.objects.get(lead_name)
    layers = [False] * 20
    lead_layer = _addon().ELECTRODES_LAYER
    layers[lead_layer] = True
    parent_name = 'leads'
    mu.create_empty_if_doesnt_exists(parent_name, _addon().BRAIN_EMPTY_LAYER, None, parent_name)

    mu.cylinder_between(p1, p2, radius, layers)
    color = tuple(np.concatenate((bpy.context.scene.electrodes_leads_color, [1])))
    mu.create_material('{}_mat'.format(lead_name), color, 1)
    cur_obj = bpy.context.active_object
    cur_obj.name = lead_name
    cur_obj.parent = bpy.data.objects[parent_name]
    bpy.data.objects[lead_name].select = False
    return bpy.data.objects[lead_name]


def get_leads():
    return ElecsPanel.leads


def get_lead_electrodes(lead):
    electrodes = []
    for electrode in ElecsPanel.groups_electrodes[lead]:
        if not ElecsPanel.lookup.get(electrode, None) is None:
            electrodes.append(electrode)
    return electrodes


def get_electrode_lead(electrode):
    return ElecsPanel.groups.get(electrode, '')


def what_to_color_update(self, context):
    if ElecsPanel.init:
        _what_to_color_update()


def _what_to_color_update():
    pass


def leads_update(self, context):
    if ElecsPanel.init:
        _leads_update()


# @mu.profileit(op.join(mu.get_user_fol(), 'leads_update_profile'), 'cumtime')
def _leads_update():
    if _addon() is None or not ElecsPanel.init:
        return
    ElecsPanel.current_lead = bpy.context.scene.leads
    init_electrodes_list()
    _show_only_current_lead_update()
    _addon().show_electrodes()


def set_current_electrode(electrode, lead=''):
    if lead == '':
        lead = get_electrode_lead(electrode)
    print('set_current_electrode: {}'.format(electrode))
    bpy.context.scene.leads = lead
    bpy.context.scene.electrodes = electrode


def electrodes_update(self, context):
    if ElecsPanel.init:
        _electrodes_update()


def get_ela_model():
    return ElecsPanel.lookup


def _electrodes_update():
    if _addon() is None or not ElecsPanel.init:
        return
    # mu.print_traceback()
    ElecsPanel.prev_elect = prev_elect = ElecsPanel.current_electrode
    ElecsPanel.current_electrode = current_electrode = bpy.context.scene.electrodes
    bpy.context.scene.current_lead = ElecsPanel.groups[current_electrode]
    update_cursor()
    # color_electrodes(current_electrode, prev_elect)
    # todo: fix electrodes_selection_coloring!
    electrodes_selection_coloring()
    if not ElecsPanel.lookup is None:
        loc = ElecsPanel.lookup.get(current_electrode, None)
        if loc is None:
            print("Can't find {} in ElecsPanel.lookup!".format(current_electrode))
        else:
            print_electrode_loc(loc)
            if bpy.context.scene.color_lables:
                plot_labels_probs(loc)
            if bpy.context.scene.electrode_rotate:
                rotate_brain_via_lookup(current_electrode, loc)
    else:
        pass
        # print('lookup table is None!')
    # mu.change_fcurves_colors(bpy.data.objects[current_electrode])
    # select_electrode(current_electrode)
    bpy.data.objects[current_electrode].select = True
    mu.change_selected_fcurves_colors(mu.OBJ_TYPE_ELECTRODE)
    _addon().show_electrodes()

    # Ugly fix
    # ani =  bpy.data.objects[current_electrode].animation_data
    # if ani is not None:
    #     for fcurve in ani.action.fcurves:
    #         fcurve.keyframe_points[0].co[1] = fcurve.keyframe_points[1].co[1]


def electrodes_selection_coloring():
    current_electrode = bpy.context.scene.electrodes
    selected_electrodes = get_selected_electrodes()
    # Check if it's a new selection:
    # print(len(selected_electrodes), current_electrode, ElecsPanel.prev_electrodes)
    if len(selected_electrodes) == 1 and current_electrode not in ElecsPanel.prev_electrodes:
        # Clear and init prev_electrodes
        unselect_prev_electrode(ElecsPanel.prev_electrodes)
        ElecsPanel.prev_electrodes = set([current_electrode])
    # Check if this is a new electrodes where the shift is pressed
    elif len(selected_electrodes) > 1 and current_electrode not in ElecsPanel.prev_electrodes:
        # Add current electrode to prev_electrodes
        ElecsPanel.prev_electrodes.add(current_electrode)
    # Check if the user unselect one of the selected electrodes
    elif len(selected_electrodes) > 1 and current_electrode in ElecsPanel.prev_electrodes:
        bpy.data.objects[current_electrode].select = False
        unselect_prev_electrode([current_electrode])
        ElecsPanel.prev_electrodes.remove(current_electrode)
    else:
        clear_electrodes_selection()
    # print(get_selected_electrodes())


def get_selected_electrodes():
    return [obj.name for obj in bpy.context.selected_objects if
            mu.check_obj_type(obj.name) == mu.OBJ_TYPE_ELECTRODE]


def clear_electrodes_selection():
    unselect_prev_electrode(ElecsPanel.prev_electrodes)
    ElecsPanel.prev_electrodes = set()


def select_electrode(current_electrode):
    # group, elc1, elc2 = mu.elec_group_number(current_electrode, True)
    for elec in ElecsPanel.all_electrodes:
        bpy.data.objects[elec].select = elec == current_electrode
    # _addon().filter_electrode_func(bpy.context.scene.electrodes)


def get_electrodes_pos():
    electrode_names = get_electrodes_names()
    electrodes_pos = np.zeros((len(electrode_names), 3))
    for elc_ind, electrode_name in enumerate(electrode_names):
        electrodes_pos[elc_ind] = bpy.data.objects[electrode_name].matrix_world.to_translation()
    return electrodes_pos


def get_electrode_pos(electrode_name):
    return bpy.data.objects[electrode_name].matrix_world.to_translation()


def electode_was_manually_selected(selected_electrode_name):
    bpy.context.scene.cursor_location = bpy.data.objects[selected_electrode_name].matrix_world.to_translation()
    tkreg_ras = bpy.context.scene.cursor_location * 10
    _addon().set_tkreg_ras(tkreg_ras, move_cursor=False)
    _addon().create_slices(pos=tkreg_ras)
    _addon().freeview.save_cursor_position()
    if not ElecsPanel.init or len(ElecsPanel.leads) == 0:
        return
    # print(selected_electrode_name, bpy.context.active_object, bpy.context.selected_objects)
    group = ElecsPanel.groups.get(selected_electrode_name)
    if group is None:
        print("Can't find electrode {} in the leads dict!".format(selected_electrode_name))
        return
    # It's enough to update the lead to update also the elecctrode, according to bpy.context.active_object
    try:
        # This line will call _leads_update() that will call _electrodes_update()
        bpy.context.scene.leads = group
    except:
        print("Can't update the selected electrode ({})".format(selected_electrode_name))


def color_electrodes(current_electrode, prev_electrode):
    # bpy.context.scene.bipolar = '-' in current_electrode
    current_electrode_group = mu.elec_group(current_electrode, bpy.context.scene.bipolar)
    if ElecsPanel.groups_hemi:
        current_electrode_hemi = ElecsPanel.groups_hemi[current_electrode_group]
        prev_electrode_group = mu.elec_group(prev_electrode, bpy.context.scene.bipolar)
        prev_electrode_hemi = ElecsPanel.groups_hemi[prev_electrode_group]
        if current_electrode_hemi != prev_electrode_hemi:
            print('flip hemis! clear {}'.format(prev_electrode_hemi))
            _addon().clear_cortex([prev_electrode_hemi])
    else:
        _addon().clear_cortex()
    # color = bpy.context.scene.electrodes_color
    # _addon().object_coloring(bpy.data.objects[current_electrode], tuple(color)) #cu.name_to_rgb('green'))
    # if prev_electrode != current_electrode:
    #     _addon().object_coloring(bpy.data.objects[prev_electrode], (1, 1, 1, 1))


def is_current_electrode_marked():
    current_electrode_marked = False
    current_electrode_obj = bpy.data.objects.get(bpy.context.scene.electrodes, None)
    if not current_electrode_obj is None:
        current_electrode_marked = _addon().get_obj_color(current_electrode_obj)[:3] == tuple(
            bpy.context.scene.electrodes_color)
    return current_electrode_marked


def print_electrode_loc(loc):
    # print('{}:'.format(ElecsPanel.current_electrode))
    # for subcortical_name, subcortical_prob in zip(loc['subcortical_rois'], loc['subcortical_probs']):
    #     print('{}: {}'.format(subcortical_name, subcortical_prob))
    # for cortical_name, cortical_prob in zip(loc['cortical_rois'], loc['cortical_probs']):
    #     print('{}: {}'.format(cortical_name, cortical_prob))
    ElecsPanel.subcortical_rois = loc['subcortical_rois']
    ElecsPanel.subcortical_probs = loc['subcortical_probs']
    ElecsPanel.cortical_rois = loc['cortical_rois']
    ElecsPanel.cortical_probs = loc['cortical_probs']


def update_cursor():
    if not ElecsPanel.init:
        return
    current_electrode_obj = bpy.data.objects[ElecsPanel.current_electrode]
    # Getting the electrode pos after translation if any
    # loc, rot, scale = bpy.context.object.matrix_world.decompose()
    bpy.context.scene.cursor_location = current_electrode_obj.matrix_world.to_translation() #current_electrode_obj.location
    # bpy.context.scene.cursor_location = current_electrode_obj.location + bpy.data.objects[PARENT_OBJ_NAME].location
    if _addon().freeview_panel is not None:
        _addon().freeview_panel.save_cursor_position()
    _addon().set_cursor_pos()
    _addon().create_slices(pos=current_electrode_obj.location)
    _addon().set_tkreg_ras(bpy.context.scene.cursor_location * 10)


def export_electrodes():
    import csv
    output_fol = op.join(mu.get_user_fol(), 'electrodes')
    subject = mu.get_user()
    csv_fname = op.join(output_fol, '{}_RAS.csv'.format(subject))
    with open(csv_fname, 'w') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_NONE)
        wr.writerow(['Electrode Name', 'R', 'A', 'S'])
        for group, electrodes  in ElecsPanel.groups_electrodes.items():
            for elc_name in electrodes:
                coords = get_elc_pos(elc_name) * 10
                wr.writerow([elc_name, *['{:.2f}'.format(loc) for loc in coords]])
    print('The electrodes file was exported to {}'.format(csv_fname))


def get_elc_pos(elc_name):
    return np.array(bpy.data.objects[elc_name].matrix_world.to_translation())


def show_lh_update(self, context):
    if ElecsPanel.init:
        show_hide_hemi_electrodes('lh', bpy.context.scene.show_lh_electrodes)
        updade_lead_hemis()
        init_electrodes_list()


def show_rh_update(self, context):
    if ElecsPanel.init:
        show_hide_hemi_electrodes('rh', bpy.context.scene.show_rh_electrodes)
        updade_lead_hemis()
        init_electrodes_list()


def show_hide_hemi_electrodes(hemi, val):
    for elec_obj in ElecsPanel.parent.children:
        elec_hemi = get_elec_hemi(elec_obj.name)
        if elec_hemi == hemi:
            elec_obj.hide = not val
            elec_obj.hide_render = not val
    leads_parent = bpy.data.objects.get('leads', None)
    if leads_parent is not None:
        for lead_obj in leads_parent.children:
            lead_group = lead_obj.name.split('_')[0]
            if lead_group not in ElecsPanel.groups_first_electrode:
                continue
            group_hemi = get_elec_hemi(ElecsPanel.groups_first_electrode[lead_group])
            if group_hemi == hemi:
                lead_obj.hide = not val
                lead_obj.hide_render = not val


def show_hide_electrodes(val):
    for elec_obj in ElecsPanel.parent.children:
        elec_obj.hide = not val
        elec_obj.hide_render = not val


def get_elec_hemi(elec_name):
    if elec_name in ElecsPanel.groups and ElecsPanel.groups[elec_name] in ElecsPanel.groups_hemi:
        return ElecsPanel.groups_hemi[ElecsPanel.groups[elec_name]]
    else:
        return ''


def updade_lead_hemis():
    if bpy.context.scene.show_lh_electrodes and bpy.context.scene.show_rh_electrodes:
        leads = ElecsPanel.sorted_groups['lh'] + ElecsPanel.sorted_groups['rh']
    elif bpy.context.scene.show_lh_electrodes and not bpy.context.scene.show_rh_electrodes:
        leads = ElecsPanel.sorted_groups['lh']
    elif not bpy.context.scene.show_lh_electrodes and bpy.context.scene.show_rh_electrodes:
        leads = ElecsPanel.sorted_groups['rh']
    else:
        leads = []
    init_leads_list(leads)


def color_the_relevant_lables(val):
    bpy.context.scene.color_lables = val


def show_only_the_current_lead(val):
    bpy.context.scene.show_only_lead = val


def set_electrodes_labeling_file(fname):
    bpy.context.scene.electrodes_labeling_files = mu.namebase(fname)


def color_labels_update(self, context):
    if ElecsPanel.init:
        if bpy.context.scene.color_lables:
            _electrodes_update()
        else:
            _addon().clear_cortex()
            _addon().clear_subcortical_regions()


def electrodes_labeling_files_update(self, context):
    # if ElecsPanel.init:
    # todo: How to get the other file names?
    # list(bpy.types.Scene.electrodes_labeling_files[1].items())[3][1]
    if ElecsPanel.init:
        _electrodes_labeling_files_update()


def _electrodes_labeling_files_update():
    labeling_fname = op.join(mu.get_user_fol(), 'electrodes', '{}.pkl'.format(
        bpy.context.scene.electrodes_labeling_files))
    ElecsPanel.electrodes_locs = mu.load(labeling_fname)
    ElecsPanel.lookup = create_lookup_table(ElecsPanel.electrodes_locs, ElecsPanel.all_electrodes)


def show_only_current_lead_update(self, context):
    if ElecsPanel.init:
        _show_only_current_lead_update()


def _show_only_current_lead_update():
    if bpy.context.scene.show_only_lead:
        bpy.context.scene.current_lead = ElecsPanel.groups[ElecsPanel.current_electrode]
        for elec_obj in ElecsPanel.parent.children:
            elec_obj.hide = elec_obj.hide_render = ElecsPanel.groups[elec_obj.name] != bpy.context.scene.current_lead
    else:
        show_hide_hemi_electrodes('lh', bpy.context.scene.show_lh_electrodes)
        show_hide_hemi_electrodes('rh', bpy.context.scene.show_rh_electrodes)
        # updade_lead_hemis()


def set_show_only_lead(val):
    bpy.context.scene.show_only_lead = val


# def show_elecs_hemi_update():
#     if ElecsPanel.init:
#         show_hide_hemi_electrodes('lh', bpy.context.scene.show_lh_electrodes)
#         show_hide_hemi_electrodes('rh', bpy.context.scene.show_rh_electrodes)
#         updade_lead_hemis()

@mu.timeit
def rotate_brain_via_lookup(elc_name, loc):
    cortical_probs_max, subcortical_probs_max = 0, 0
    cortical_probs_rois = \
        [(p, r) for p, r in zip(loc['cortical_probs'], loc['cortical_rois']) if 'white' not in r.lower()]
    subcortical_probs_rois = \
        [(p, r) for p, r in zip(loc['subcortical_probs'], loc['subcortical_rois']) if 'white' not in r.lower()]
    if len(cortical_probs_rois) > 0:
        cortical_probs_ind = np.argmax(cortical_probs_rois, 0)[0]
        cortical_probs_max = cortical_probs_rois[cortical_probs_ind][0]
    if len(subcortical_probs_rois) > 0:
        subcortical_probs_ind = np.argmax(subcortical_probs_rois, 0)[0]
        subcortical_probs_max = subcortical_probs_rois[subcortical_probs_ind][0]
    if cortical_probs_max > subcortical_probs_max:
        max_roi = cortical_probs_rois[cortical_probs_ind][1]
        max_roi_is_cortical = True
    else:
        max_roi = subcortical_probs_rois[subcortical_probs_ind][1]
        max_roi_is_cortical = False
    if max_roi_is_cortical:
        atlas = bpy.context.scene.electrodes_labeling_files.split('_')[1]
        hemi = mu.get_obj_hemi(max_roi)
        annot_fname = mu.get_annot_fname(hemi, atlas)
        max_roi_vertices_indices = mu.read_label_vertices_from_annot(annot_fname, max_roi)
        if max_roi_vertices_indices is None:
            print('Can\'t find {} vertices in {}!'.format(max_roi, annot_fname))
            return
        elc_pos = bpy.data.objects[elc_name].location
        mesh = 'inflated_{}'.format(hemi)
        vert_ind, vert_pos = _addon().vertex_data.find_closest_vertices(
            elc_pos, max_roi_vertices_indices, mesh, False)
        vert_pos *= 0.1
        mu.rotate_view_to_vertice(vert_ind, mesh)

        # _addon().colorbar.set_colorbar_max_min(10, 0, update_colorbar=True)
        # _addon().colorbar.set_colormap('jet')
        # faces_verts = _addon().coloring.get_faces_verts()
        # hemi_verts_num = {hemi: faces_verts[hemi].shape[0] for hemi in mu.HEMIS}
        # data = {hemi: np.zeros((hemi_verts_num[hemi])) for hemi in mu.HEMIS}
        # data[hemi][max_roi_vertices_indices] = 10
        # data[hemi][vert_ind] = 3
        # print('vert_ind in max_roi_vertices_indices: {}'.format(vert_ind in max_roi_vertices_indices))
        # _addon().coloring.color_hemi_data('inflated_{}'.format(hemi), data[hemi], 0, 25.6, threshold=1, color_even_if_hide=True)


def plot_labels_probs(elc):
    _addon().init_activity_map_coloring('FMRI')
    if bpy.context.scene.electrodes_what_to_color == 'probs':
        if len(elc['cortical_rois']) > 0:
            hemi = mu.get_obj_hemi(elc['cortical_rois'][0])
            if not hemi is None:
                labels_data = dict(data=elc['cortical_probs'], names=elc['cortical_rois'])
                if not _addon().colorbar_values_are_locked():
                    _addon().set_colorbar_title('Electrodes probabilities')
                    _addon().set_colormap('YlOrRd')
                atlas = bpy.context.scene.electrodes_labeling_files.split('_')[1:-6][0]
                _addon().labels_coloring_hemi(
                    labels_data, ElecsPanel.faces_verts, hemi, 0, colors_min=0, colors_max=1, atlas=atlas)
                colors = mu.get_distinct_colors(len(elc['cortical_rois']))
                if bpy.context.scene.electrodes_label_contours:
                    _addon().color_contours(elc['cortical_rois'], specific_colors=colors)
            else:
                print("Can't get the rois hemi!")
        else:
            _addon().clear_cortex()
        _addon().clear_subcortical_regions()
        if len(elc['subcortical_rois']) > 0:
            cm = _addon().get_cm()
            colors = mu.calc_colors_from_cm(elc['subcortical_probs'], 0, 256, cm)
            for region, color in zip(elc['subcortical_rois'], colors):
                _addon().color_subcortical_region(region, color)

    elif bpy.context.scene.electrodes_what_to_color == 'verts':
        if len(elc['cortical_indices']) > 0:
            hemi = bpy.data.objects[elc['hemi']]
            if not hemi is None:
                _addon().init_activity_map_coloring('FMRI', subcorticals=True)
                vertices_num = np.max(elc['cortical_indices']) + 1
                activity = np.ones((vertices_num, 4))
                activity[:, 0] = 0
                activity[elc['cortical_indices'], 0] = 1
                activity[elc['cortical_indices'], 1:] = np.tile(
                    cu.name_to_rgb('blue'), (len(elc['cortical_indices']), 1))
                print('Plot {} vertices with blue'.format(len(elc['cortical_indices'])))
                _addon().activity_map_obj_coloring(hemi, activity, ElecsPanel.faces_verts[elc['hemi']], 0, True)
            else:
                print("Can't get the elec's hemi!")
        else:
            _addon().clear_cortex()
            print('No cortical vertices for {}'.format(elc['name']))


def unselect_prev_electrode(prev_electrodes):
    for prev_electrode in prev_electrodes:
        prev_elc = bpy.data.objects.get(prev_electrode)
        if not prev_elc is None:
            _addon().de_select_electrode_and_sensor(prev_elc, False)
        # prev_elc.select = False


def run_ela_alg():
    mmvt_code_fol = mu.get_mmvt_code_root()
    ela_code_fol = op.join(mu.get_parent_fol(mmvt_code_fol), 'electrodes_rois')
    if not op.isdir(ela_code_fol) or not op.isfile(op.join(ela_code_fol, 'find_rois', 'find_rois.py')):
        print("Can't find ELA folder!")
        return

    import importlib
    import sys
    if ela_code_fol not in sys.path:
        sys.path.append(ela_code_fol)
    from find_rois import find_rois
    importlib.reload(find_rois)
    args = find_rois.get_args(['-s', mu.get_user(), '-a', bpy.context.scene.ela_atlas,
                               '-b', str(bpy.context.scene.ela_bipolar)])
    find_rois.run_for_all_subjects(args)
    import shutil
    ela_output_fname_template = op.join(
        ela_code_fol, 'electrodes', '{}_{}_electrodes_cigar_r_*_l_*{}.pkl'.format(
            mu.get_user(), bpy.context.scene.ela_atlas, '_bipolar' if bpy.context.scene.ela_bipolar else '' ))
    ela_output_fnames = glob.glob(ela_output_fname_template)
    if len(ela_output_fnames) > 0:
        for ela_output_fname in ela_output_fnames:
            shutil.copyfile(ela_output_fname, op.join(
                mu.get_user_fol(), 'electrodes', mu.namebase_with_ext(ela_output_fname)))
    else:
        print('couldn\'t find any ELA output! ({})'.format(ela_output_fname_template))
    init(_addon(), False)


def delete_electrodes():
    mu.delete_hierarchy('Deep_electrodes')


def elecs_draw(self, context):
    layout = self.layout
    box = layout.box()
    if ElecsPanel.electrodes_labeling_file_exist and len(ElecsPanel.labling_files) > 1:
        box.prop(context.scene, "electrodes_labeling_files", text="")
    if ElecsPanel.electrodes_labeling_file_exist and len(ElecsPanel.labling_files) > 0:
        box.label(text='Model: {}'.format(context.scene.electrodes_labeling_files.split('_')[1]))
    row = box.row(align=True)
    row.operator(PrevLead.bl_idname, text="", icon='PREV_KEYFRAME')
    row.prop(context.scene, "leads", text="")
    row.operator(NextLead.bl_idname, text="", icon='NEXT_KEYFRAME')
    row = box.row(align=True)
    row.operator(PrevElectrode.bl_idname, text="", icon='PREV_KEYFRAME')
    row.prop(context.scene, "electrodes", text="")
    row.operator(NextElectrode.bl_idname, text="", icon='NEXT_KEYFRAME')

    if len(ElecsPanel.subcortical_rois) > 0 or len(ElecsPanel.cortical_rois) > 0:
        # box = layout.box()
        col = box.column()
        for subcortical_name, subcortical_prob in zip(ElecsPanel.subcortical_rois, ElecsPanel.subcortical_probs):
            mu.add_box_line(col, subcortical_name, '{:.3f}'.format(subcortical_prob), 0.8)
        for cortical_name, cortical_prob in zip(ElecsPanel.cortical_rois, ElecsPanel.cortical_probs):
            if cortical_prob >= 0.001:
                mu.add_box_line(col, cortical_name, '{:.3f}'.format(cortical_prob), 0.8)

        # box = layout.box()
        # box.prop(context.scene, "electrodes_hemis", text="")
        # box.prop(context.scene, "electrodes_hemi_labels", text="")

    if bpy.context.scene.electrodes_more_settings:
        layout.prop(context.scene, 'show_electrodes_labels', text="Show labels")
        layout.prop(context.scene, 'show_only_lead', text="Show only the current lead")
        # row = layout.row(align=True)
        if ElecsPanel.electrodes_labeling_file_exist:
            layout.prop(context.scene, 'color_lables', text="Color probabilities")
            # row.prop(context.scene, 'electrodes_label_contours', text="Color contours")
        # layout.label(text='What to color: ')
        # if bpy.context.scene.color_lables:
        #     layout.prop(context.scene, 'electrodes_what_to_color', text='What to color', expand=True)
        if ElecsPanel.groups_hemi:
            row = layout.row(align=True)
            row.prop(context.scene, "show_lh_electrodes", text="Left hemi")
            row.prop(context.scene, "show_rh_electrodes", text="Right hemi")
        if ElecsPanel.electrodes_labeling_file_exist:
            layout.prop(context.scene, "electrode_rotate", text="Rotate view on click")

        row = layout.row(align=True)
        row.prop(context.scene, "show_electrodes_groups_leads", text="Show leads")
        leads_obj = bpy.data.objects.get('leads', None)
        if leads_obj is None or len(leads_obj.children) == 0:
            row.prop(context.scene, "electrodes_create_curved_leads", text="Curved")
        # row.prop(context.scene, "electrodes_leads_color", text='')

        if ElecsPanel.ela_code_exist and ElecsPanel.atlases_exist:
            layout.prop(context.scene, "show_ela", text="Show ELA options")
            if bpy.context.scene.show_ela:
                col = layout.box().column()
                col.prop(context.scene, "ela_bipolar", text="Bipolar")
                col.prop(context.scene, "ela_atlas", text='')
                col.operator(RunELA.bl_idname, text="Calc electrodes probs", icon='TEXTURE')

        row = layout.row(align=True)
        if not bpy.context.scene.listen_to_keyboard:
            layout.operator(KeyboardListener.bl_idname, text="Listen to keyboard", icon='COLOR_GREEN')
        else:
            layout.operator(KeyboardListener.bl_idname, text="Stop listen to keyboard", icon='COLOR_RED')
            box = layout.box()
            col = box.column()
            mu.add_box_line(col, 'Left', 'Previous electrodes')
            mu.add_box_line(col, 'Right', 'Next electrodes')
            mu.add_box_line(col, 'Down', 'Previous lead')
            mu.add_box_line(col, 'Up', 'Next lead')
        row.operator(ColorElectrodes.bl_idname, text="Color electrodes")
        row.prop(context.scene, "electrodes_color_only_selected", text='Only selected')
        row.prop(context.scene, 'electrodes_color', text='')
        layout.operator(ExportElectrodes.bl_idname, text="Export", icon='EXPORT')
        layout.prop(context.scene, "elc_size", text="size")
        layout.operator(DeleteElectrodes.bl_idname, text="Delete electrodes", icon='CANCEL')

    layout.operator(ClearElectrodes.bl_idname, text="Clear", icon='PANEL_CLOSE')
    layout.prop(context.scene, 'electrodes_more_settings', text='More settings')

    # Color picker:
    # row = layout.row(align=True)
    # row.label(text='Selected electrode color:')
    # row = layout.row(align=True)
    # row.label(text='             ')
    # row.prop(context.scene, 'electrodes_color', text='')
    # row.label(text='             ')


class DeleteElectrodes(bpy.types.Operator):
    bl_idname = "mmvt.delete_electrodes"
    bl_label = "delete_electrodes"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        delete_electrodes()
        return {'PASS_THROUGH'}


class ExportElectrodes(bpy.types.Operator):
    bl_idname = 'mmvt.electrodes_export'
    bl_label = 'exportElectrodes'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        export_electrodes()
        return {'FINISHED'}


class RunELA(bpy.types.Operator):
    bl_idname = 'mmvt.calc_ela'
    bl_label = 'calc_ela'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        run_ela_alg()
        return {'FINISHED'}


class ClearElectrodes(bpy.types.Operator):
    bl_idname = 'mmvt.electrodes_clear'
    bl_label = 'clearElectrodes'
    bl_description = 'Clears all the plotted activity. \n*For deselecting the electrodes go to the ‘Selection Panel’ ' \
                     'and press the ‘Deselect All’ button.\n\nScript: mmvt.electrodes._addon().clear_colors()'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        _addon().clear_colors()
        return {'FINISHED'}


class NextElectrode(bpy.types.Operator):
    bl_idname = 'mmvt.next_electrode'
    bl_label = 'nextElectrodes'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        next_electrode()
        return {'FINISHED'}


def next_electrode():
    # index = ElecsPanel.electrodes.index(bpy.context.scene.electrodes)
    electrode_lead = mu.elec_group(bpy.context.scene.electrodes, bpy.context.scene.bipolar)
    lead_electrodes = ElecsPanel.groups_electrodes[electrode_lead]
    index = lead_electrodes.index(bpy.context.scene.electrodes)
    if index < len(lead_electrodes) - 1:
        next_elc = lead_electrodes[index + 1]
    else:
        next_elc = lead_electrodes[0]
    bpy.context.scene.electrodes = next_elc
    bpy.data.objects[ElecsPanel.prev_elect].select = False
    # _addon().de_select_electrode_and_sensor(ElecsPanel.prev_elect)
    # bpy.data.objects[next_elc].select = True
    # _addon().curves_sep_update()


class PrevElectrode(bpy.types.Operator):
    bl_idname = 'mmvt.prev_electrode'
    bl_label = 'prevElectrodes'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        prev_electrode()
        return {'FINISHED'}


def prev_electrode():
    electrode_lead = mu.elec_group(bpy.context.scene.electrodes, bpy.context.scene.bipolar)
    lead_electrodes = ElecsPanel.groups_electrodes[electrode_lead]
    index = lead_electrodes.index(bpy.context.scene.electrodes)
    if index > 0:
        prev_elc = lead_electrodes[index - 1]
    else:
        prev_elc = lead_electrodes[-1]
    bpy.context.scene.electrodes = prev_elc
    bpy.data.objects[ElecsPanel.prev_elect].select = False
    # _addon().de_select_electrode_and_sensor(ElecsPanel.prev_elect)
    # bpy.data.objects[prev_elc].select = True
    # _addon().curves_sep_update()


class NextLead(bpy.types.Operator):
    bl_idname = 'mmvt.next_lead'
    bl_label = 'nextLead'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        next_lead()
        return {'FINISHED'}


def next_lead():
    index = ElecsPanel.leads.index(bpy.context.scene.leads)
    next_lead = ElecsPanel.leads[index + 1] if index < len(ElecsPanel.leads) - 1 else ElecsPanel.leads[0]
    bpy.context.scene.leads = next_lead


class PrevLead(bpy.types.Operator):
    bl_idname = 'mmvt.prev_lead'
    bl_label = 'prevLead'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        prev_lead()
        return {'FINISHED'}


def prev_lead():
    index = ElecsPanel.leads.index(bpy.context.scene.leads)
    prev_lead = ElecsPanel.leads[index - 1] if index > 0 else ElecsPanel.leads[-1]
    bpy.context.scene.leads = prev_lead


class ColorElectrodes(bpy.types.Operator):
    bl_idname = 'mmvt.color_electrodes'
    bl_label = 'color_electrodes'
    bl_description = 'Colors all the electrodes with the selected color'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        if bpy.context.scene.electrodes_color_only_selected:
            for elc_obj in bpy.context.selected_objects:
                if not elc_obj.hide and mu.check_obj_type(elc_obj) == mu.OBJ_TYPE_ELECTRODE:
                    _addon().object_coloring(elc_obj, bpy.context.scene.electrodes_color)
        else:
            for elc_obj in ElecsPanel.parent.children:
                if not elc_obj.hide:
                    _addon().object_coloring(elc_obj, bpy.context.scene.electrodes_color)
        return {'FINISHED'}


class KeyboardListener(bpy.types.Operator):
    bl_idname = 'mmvt.keyboard_listener'
    bl_label = 'keyboard_listener'
    bl_description = 'Opens a window with instructions on how to use the keyboard to select electrodes'
    bl_options = {'UNDO'}
    press_time = time.time()
    funcs = {'LEFT_ARROW':prev_electrode, 'RIGHT_ARROW':next_electrode, 'UP_ARROW':prev_lead, 'DOWN_ARROW':next_lead}

    def modal(self, context, event):
        if time.time() - self.press_time > 1 and bpy.context.scene.listen_to_keyboard and \
                event.type not in ['TIMER', 'MOUSEMOVE', 'WINDOW_DEACTIVATE', 'INBETWEEN_MOUSEMOVE', 'TIMER_REPORT', 'NONE']:
            self.press_time = time.time()
            # print(event.type)
            if event.type in KeyboardListener.funcs.keys():
                KeyboardListener.funcs[event.type]()
            else:
                pass
        return {'PASS_THROUGH'}

    def invoke(self, context, event=None):
        if not bpy.context.scene.listener_is_running:
            context.window_manager.modal_handler_add(self)
            bpy.context.scene.listener_is_running = True
            _addon().show_electrodes()
            _leads_update()
        bpy.context.scene.listen_to_keyboard = not bpy.context.scene.listen_to_keyboard
        return {'RUNNING_MODAL'}


bpy.types.Scene.show_only_lead = bpy.props.BoolProperty(
    default=False, update=show_only_current_lead_update, description='Shows only the last selected leads')
bpy.types.Scene.color_lables = bpy.props.BoolProperty(
    default=False, update=color_labels_update,
    description='Plots the labels with the highest probabilities the signal for the electrode was received from')
bpy.types.Scene.electrodes_label_contours = bpy.props.BoolProperty(
    default=False, description="Color the relevant lables contours", update=color_labels_update)
bpy.types.Scene.show_lh_electrodes = bpy.props.BoolProperty(
    default=True, update=show_lh_update, description='Shows only the electrodes in the left hemisphere')
bpy.types.Scene.show_rh_electrodes = bpy.props.BoolProperty(
    default=True, update=show_rh_update, description='Shows only the electrodes in the right hemisphere')
bpy.types.Scene.listen_to_keyboard = bpy.props.BoolProperty(default=False)
bpy.types.Scene.listener_is_running = bpy.props.BoolProperty(default=False)
bpy.types.Scene.current_lead = bpy.props.StringProperty()
bpy.types.Scene.electrodes_color = bpy.props.FloatVectorProperty(
    name="object_color", subtype='COLOR', default=(0, 0.5, 0), min=0.0, max=1.0,
    description='Selects the color to color the electrodes')
    # size=2, subtype='COLOR_GAMMA', min=0, max=1)
bpy.types.Scene.electrodes_labeling_files = bpy.props.EnumProperty(
    items=[], update=electrodes_labeling_files_update, description='List of electrodes labeling type.\n\nCurrent')
bpy.types.Scene.electrodes = bpy.props.EnumProperty(
    items=[], update=electrodes_update, description='Selects each electrode on the selected lead.\n\nCurrent electrode')
bpy.types.Scene.leads = bpy.props.EnumProperty(items=[], update=leads_update,
    description='Selects leads name.\n\nCurrent lead')
bpy.types.Scene.electrodes_what_to_color = bpy.props.EnumProperty(
    items=[('probs', 'probabilities', '', 1), ('verts', 'vertices', '', 2)], description="what to color",
    update=what_to_color_update)
bpy.types.Scene.elc_size = bpy.props.FloatProperty(min=0.1, description="", update=elc_size_update)
bpy.types.Scene.show_electrodes_groups_leads = bpy.props.BoolProperty(default=False,
    update=show_electrodes_groups_leads_update, description='Shows the leads connecting the electrodes')
bpy.types.Scene.electrodes_leads_color = bpy.props.FloatVectorProperty(
    name="object_color", subtype='COLOR', default=(0.5, 0.175, 0.02), min=0.0, max=1.0, description="color picker")
bpy.types.Scene.show_ela = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ela_bipolar = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ela_atlas = bpy.props.EnumProperty(items=[])
bpy.types.Scene.electrode_rotate = bpy.props.BoolProperty(default=False,
    description='Rotates the view of the brain to show the selected electrode')
bpy.types.Scene.electrodes_more_settings = bpy.props.BoolProperty(default=False)
bpy.types.Scene.electrodes_create_curved_leads = bpy.props.BoolProperty(default=False)
bpy.types.Scene.electrodes_color_only_selected = bpy.props.BoolProperty(default=False)
bpy.types.Scene.show_electrodes_labels = bpy.props.BoolProperty(default=False, update=show_electrodes_labels_update,
    description ='Shows the label of each electrode')


bpy.types.Scene.electrodes_hemis = bpy.props.EnumProperty(
    items=[('left', 'lh', '', 1), ('right', 'rh', '', 2)], update=electrodes_hemis_update)
bpy.types.Scene.electrodes_hemi_labels = bpy.props.EnumProperty(items=[])
bpy.types.Scene.electrodes_labeling_files = bpy.props.EnumProperty(items=[])


class ElecsPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Electrodes"
    addon, parent = None, None
    init = False
    electrodes, leads = [], []
    current_electrode = ''
    prev_elect = ''
    prev_electrodes = set()
    electrodes_locs, lookup = None, None
    subcortical_rois, subcortical_probs = [], []
    cortical_rois, cortical_probs = [], []
    groups_electrodes, groups, groups_hemi = [], {}, {}
    sorted_groups = {'rh':[], 'lh':[]}
    ela_code_exist = False
    bpy.context.scene.elc_size = 1
    atlases_exist = False
    labling_files = []
    electrodes_labeling_file_exist = False

    def draw(self, context):
        elecs_draw(self, context)


def init(addon, do_register=True):
    ElecsPanel.init = False
    ElecsPanel.addon  = addon
    ElecsPanel.parent = bpy.data.objects.get('Deep_electrodes')
    if ElecsPanel.parent is None or len(ElecsPanel.parent.children) == 0:
        print("Can't register electrodes panel, no Deep_electrodes object")
        return
    mu.make_dir(op.join(mu.get_user_fol(), 'electrodes'))
    init_sorted_groups()
    # show_hide_electrodes(True)
    ElecsPanel.groups_hemi = create_groups_hemi_lookup(ElecsPanel.sorted_groups)
    ElecsPanel.all_electrodes = [el.name for el in ElecsPanel.parent.children]
    ElecsPanel.groups = create_groups_lookup_table(ElecsPanel.all_electrodes)
    ElecsPanel.groups_first_electrode = find_first_electrode_per_group(ElecsPanel.all_electrodes)
    ElecsPanel.groups_electrodes = create_groups_electrodes_lookup(ElecsPanel.all_electrodes)
    init_leads_list()
    ret = init_electrodes_list()
    # if not ret:
    #     return
    ret = init_electrodes_labeling(addon)
    if ret:
        ElecsPanel.electrodes_labeling_file_exist = True
        _electrodes_labeling_files_update()
    else:
        ElecsPanel.electrodes_labeling_file_exist = False
        print('No electrodes labeling files.')

    # addon.clear_colors_from_parent_childrens('Deep_electrodes')
    # addon.clear_cortex()
    bpy.context.scene.show_only_lead = False
    bpy.context.scene.listen_to_keyboard = False
    bpy.context.scene.listener_is_running = False
    bpy.context.scene.show_lh_electrodes = True
    bpy.context.scene.show_rh_electrodes = True
    bpy.context.scene.show_ela = False
    bpy.context.scene.electrode_rotate = False
    bpy.context.scene.electrodes_more_settings = False
    bpy.context.scene.electrodes_create_curved_leads = False
    bpy.context.scene.show_electrodes_labels = False
    if not ElecsPanel.electrodes_locs or not ElecsPanel.lookup:
        if not ElecsPanel.electrodes_locs:
            print("!!! Can't find electrodes labeling files in user/electrdes!")
        if not ElecsPanel.lookup:
            print('No electrodes lookup table!')
        print("!!! Can't plot electrodes' probabilties !!!")
    # if not ElecsPanel.groups or not ElecsPanel.groups_first_electrode or not ElecsPanel.sorted_groups or \
    #     not ElecsPanel.groups_hemi or not ElecsPanel.groups_electrodes:
    #         print('Error in electrodes panel init!')
    # else:
    if do_register:
        register()
    ElecsPanel.init = True
    # print('Electrodes panel initialization completed successfully!')


def init_sorted_groups():
    import shutil
    sorted_groups_fname = op.join(mu.get_user_fol(), 'electrodes', 'sorted_groups.pkl')
    if not op.isfile(sorted_groups_fname):
        # Try to get the file from the subject's root folder
        if op.isfile(op.join(mu.get_user_fol(), 'sorted_groups.pkl')):
            shutil.move(op.join(mu.get_user_fol(), 'sorted_groups.pkl'), sorted_groups_fname)
        else:
            print("electrodes_panel: no sorted groups file")
            # return
    if op.isfile(sorted_groups_fname):
        ElecsPanel.sorted_groups = mu.load(sorted_groups_fname)


def init_leads_list(leads=None):
    # ElecsPanel.leads = sorted(list(set([mu.elec_group(elc, bipolar) for elc in ElecsPanel.electrodes])))
    if leads is None:
        ElecsPanel.leads = list(ElecsPanel.groups_electrodes.keys()) # ElecsPanel.sorted_groups['lh'] + ElecsPanel.sorted_groups['rh']
        print('init_leads_list: {}'.format(ElecsPanel.leads))
    else:
        ElecsPanel.leads = leads
    leads_items = [(lead, lead, '', ind) for ind, lead in enumerate(ElecsPanel.leads)]
    bpy.types.Scene.leads = bpy.props.EnumProperty(
        items=leads_items, update=leads_update, description='Selects leads name.\n\nCurrent lead')
    if len(ElecsPanel.leads) > 0:
        bpy.context.scene.leads = ElecsPanel.current_lead = ElecsPanel.leads[0]
    else:
        ElecsPanel.current_lead = ''
        print('len(ElecsPanel.leads) = 0!')


def init_electrodes_list():
    if ElecsPanel.current_lead == '':
        return False
    ElecsPanel.electrodes = ElecsPanel.groups_electrodes[ElecsPanel.current_lead]
    if len(ElecsPanel.electrodes) == 0:
        print('init_electrodes_list: No electrodes found for {}!'.format(ElecsPanel.current_lead))
        return False
    ElecsPanel.electrodes.sort(key=mu.natural_keys)
    electrodes_items = [(elec, elec, '', ind) for ind, elec in enumerate(ElecsPanel.electrodes)]
    bpy.types.Scene.electrodes = bpy.props.EnumProperty(
        items=electrodes_items, update=electrodes_update, description='Selects each electrode on the selected lead.\n\nCurrent electrode')
    if ElecsPanel.electrodes[0] in ElecsPanel.groups:
        lead = ElecsPanel.groups[ElecsPanel.electrodes[0]]
        last_obj_name = bpy.context.active_object.name if bpy.context.active_object is not None else ''
        # mu.print_traceback()
        if last_obj_name != '' and last_obj_name in ElecsPanel.groups and ElecsPanel.groups[last_obj_name] == lead:
            bpy.context.scene.electrodes = ElecsPanel.current_electrode = last_obj_name
        else:
            bpy.context.scene.electrodes = ElecsPanel.current_electrode = ElecsPanel.groups_first_electrode[lead]
        return True
    else:
        print('{} not in groups!'.format(ElecsPanel.electrodes[0]))
        return False


def init_electrodes_labeling(addon):
    ela_code_fol = op.join(mu.get_parent_fol(mu.get_mmvt_code_root()), 'electrodes_rois')
    ElecsPanel.ela_code_exist = op.isfile(op.join(ela_code_fol, 'find_rois', 'find_rois.py'))
    ElecsPanel.labling_files = labling_files = find_elecrode_labeling_files()
    if len(labling_files) > 0:
        files_names = [mu.namebase(fname) for fname in labling_files if mu.load(fname)]
        labeling_items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
        bpy.types.Scene.electrodes_labeling_files = bpy.props.EnumProperty(
            items=labeling_items, update=electrodes_labeling_files_update,
            description='List of electrodes labeling type.\n\nCurrent')
        bpy.context.scene.electrodes_labeling_files = files_names[0]
        # ElecsPanel.electrodes_locs = mu.load(labling_files[0])
        # ElecsPanel.lookup = create_lookup_table(ElecsPanel.electrodes_locs, ElecsPanel.electrodes)
    ElecsPanel.faces_verts = addon.get_faces_verts()

    atlases = mu.get_annot_files()
    if len(atlases) > 0:
        ElecsPanel.atlases_exist = True
        atlases_items = [(c, c, '', ind) for ind, c in enumerate(atlases)]
        bpy.types.Scene.ela_atlas = bpy.props.EnumProperty(items=atlases_items, description='atlases')
        bpy.context.scene.ela_atlas = atlases[0]
    bpy.context.scene.ela_bipolar = bpy.context.scene.bipolar
    return len(labling_files) > 0


def find_elecrode_labeling_files():
    files = []
    blender_electrodes_names = set([o.name for o in bpy.data.objects['Deep_electrodes'].children])
    # labeling_template = '{}_{}_electrodes_cigar_r_*_l_*.pkl'.format(mu.get_user(), bpy.context.scene.atlas)
    labeling_template = '{}_*_electrodes_cigar_r_*_l_*.pkl'.format(mu.get_user(), bpy.context.scene.atlas)
    labling_files = glob.glob(op.join(mu.get_user_fol(), 'electrodes', labeling_template))
    for labling_file in labling_files:
        try:
            d = mu.load(labling_file)
            electrodes_names = set([e['name'] for e in d])
            # todo: find what is the problem... (mg96)
            # if len(electrodes_names - blender_electrodes_names) == 0:
            files.append(labling_file)
        except:
            print('Error reading {}'.format(labling_file))
            continue
    if len(files) == 0:
        print("Can't find any labeling file that match the electrodes names in{}!".format(
            op.join(mu.get_user_fol(), 'electrodes')))
    return files


def create_lookup_table(electrodes_locs, electrodes):
    lookup = {}
    if electrodes_locs is None:
        print('electrodes_locs is None!!!')
        return None
    for elc in electrodes:
        for electrode_loc in electrodes_locs:
            if electrode_loc['name'] == elc:
                lookup[elc] = electrode_loc
                break
    return lookup


def find_first_electrode_per_group(electrodes):
    groups = defaultdict(list)
    first_electrodes = {}
    bipolar = '-' in electrodes[0]
    for elc in electrodes:
        groups[mu.elec_group(elc, bipolar)].append(elc)
    for group, group_electrodes in groups.items():
        first_electrode = sorted(group_electrodes)[0]
        first_electrodes[group] = first_electrode
    return first_electrodes


def create_groups_lookup_table(electrodes):
    groups = {}
    bipolar = '-' in electrodes[0]
    for elc in electrodes:
        group = mu.elec_group(elc, bipolar)
        groups[elc] = group
    return groups


def create_groups_electrodes_lookup(electrodes):
    groups = defaultdict(list)
    bipolar = '-' in electrodes[0]
    for elc in electrodes:
        if bipolar and '-' in elc:
            group, num, _ = mu.elec_group_number(elc, bipolar)
        else:
            group, num = mu.elec_group_number(elc, bipolar)
        # group = mu.elec_group(elc, bipolar)
        groups[group].append((num, elc))
    for group in groups.keys():
        groups[group] = [t[1] for t in sorted(groups[group])]
    return groups


def create_groups_hemi_lookup(sorted_groups):
    groups_hemi = {}
    for hemi, groups in sorted_groups.items():
        for group in groups:
            groups_hemi[group] = hemi
    return groups_hemi


def register():
    try:
        unregister()
        bpy.utils.register_class(ElecsPanel)
        bpy.utils.register_class(NextElectrode)
        bpy.utils.register_class(PrevElectrode)
        bpy.utils.register_class(NextLead)
        bpy.utils.register_class(PrevLead)
        bpy.utils.register_class(ColorElectrodes)
        bpy.utils.register_class(KeyboardListener)
        bpy.utils.register_class(ClearElectrodes)
        bpy.utils.register_class(ExportElectrodes)
        bpy.utils.register_class(RunELA)
        bpy.utils.register_class(DeleteElectrodes)
        # print('Electrodes Panel was registered!')
    except:
        print("Can't register Electrodes Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(ElecsPanel)
        bpy.utils.unregister_class(NextElectrode)
        bpy.utils.unregister_class(PrevElectrode)
        bpy.utils.unregister_class(NextLead)
        bpy.utils.unregister_class(PrevLead)
        bpy.utils.unregister_class(ColorElectrodes)
        bpy.utils.unregister_class(KeyboardListener)
        bpy.utils.unregister_class(ClearElectrodes)
        bpy.utils.unregister_class(ExportElectrodes)
        bpy.utils.unregister_class(RunELA)
        bpy.utils.unregister_class(DeleteElectrodes)
    except:
        pass
        # print("Can't unregister Electrodes Panel!")


