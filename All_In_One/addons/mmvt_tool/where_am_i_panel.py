import bpy
import mathutils
import numpy as np
import importlib
import glob
import traceback
from collections import Counter
import os.path as op
import os
import mmvt_utils as mu
import slicer
importlib.reload(slicer)


def _addon():
    return WhereAmIPanel.addon


def t1_trans():
    return WhereAmIPanel.subject_t1_trans


def t2_trans():
    return WhereAmIPanel.subject_t2_trans


def _ct_trans():
    return WhereAmIPanel.subject_ct_trans


def get_trans(modality):
    if modality == 'mri':
        return t1_trans()
    elif modality == 't2':
        return t2_trans()
    elif modality == 'ct':
        return _ct_trans()
    else:
        print('get_trans: {} is not supported!'.format(modality))
        return None


def set_ct_intensity():
    if get_slicer_state('ct') is not None:
        x, y, z = bpy.context.scene.ct_voxel_x, bpy.context.scene.ct_voxel_y, bpy.context.scene.ct_voxel_z
        ct_data = _addon().get_slicer_state('ct').data
        x, y, z = mu.in_mat(x, y, z, ct_data)
        bpy.context.scene.ct_intensity = ct_data[x, y, z]
    else:
        bpy.context.scene.ct_intensity = 0


def set_t1_value():
    if get_slicer_state('mri') is not None:
        x, y, z = bpy.context.scene.voxel_x, bpy.context.scene.voxel_y, bpy.context.scene.voxel_z
        t1_data = _addon().get_slicer_state('mri').data
        x, y, z = mu.in_mat(x, y, z, t1_data)
        bpy.context.scene.t1_value = t1_data[x, y, z]
    else:
        bpy.context.scene.t1_value = 0


def set_t2_value():
    if get_slicer_state('t2') is not None:
        x, y, z = bpy.context.scene.voxel_x, bpy.context.scene.voxel_y, bpy.context.scene.voxel_z
        t2_data = _addon().get_slicer_state('t2').data
        x, y, z = mu.in_mat(x, y, z, t2_data)
        bpy.context.scene.t2_value = t2_data[x, y, z]
    else:
        bpy.context.scene.t2_value = 0


def subject_annot_files_update(self, context):
    d = {}
    user_fol = mu.get_user_fol()
    contours_template = op.join(user_fol, 'labels', '{}_contours_{}.npz'.format(
            bpy.context.scene.subject_annot_files, '{hemi}'))
    if mu.both_hemi_files_exist(contours_template):
        for hemi in mu.HEMIS:
            d[hemi] = np.load(contours_template.format(hemi=hemi))
        WhereAmIPanel.labels_contours = d
    else:
        WhereAmIPanel.labels_contours = None


def where_i_am_draw(self, context):
    layout = self.layout
    layout.label(text='tkreg RAS (surface):')
    row = layout.row(align=0)
    row.prop(context.scene, "tkreg_ras_x", text="x")
    row.prop(context.scene, "tkreg_ras_y", text="y")
    row.prop(context.scene, "tkreg_ras_z", text="z")
    row.operator(TkregToClipboard.bl_idname, text="", icon='PASTEDOWN')
    row.operator(ClipboardToTkreg.bl_idname, text="", icon='PASTEFLIPUP')
    if not t1_trans() is None:
        layout.label(text='mni305:')
        row = layout.row(align=0)
        row.prop(context.scene, "ras_x", text="x")
        row.prop(context.scene, "ras_y", text="y")
        row.prop(context.scene, "ras_z", text="z")
        row.operator(MNIToClipboard.bl_idname, text="", icon='PASTEDOWN')
        row.operator(ClipboardToMNI.bl_idname, text="", icon='PASTEFLIPUP')
        layout.label(text='T1 voxel:')
        row = layout.row(align=0)
        row.prop(context.scene, "voxel_x", text="x")
        row.prop(context.scene, "voxel_y", text="y")
        row.prop(context.scene, "voxel_z", text="z")
    if not _ct_trans() is None:
        layout.label(text='CT:')
        row = layout.row(align=0)
        row.prop(context.scene, "ct_voxel_x", text="x")
        row.prop(context.scene, "ct_voxel_y", text="y")
        row.prop(context.scene, "ct_voxel_z", text="z")
    for atlas, name in WhereAmIPanel.atlas_ids.items():
        row = layout.row(align=0)
        row.label(text='{}: {}'.format(atlas, name))
        # row.operator(ChooseVoxelID.bl_idname, text="Select", icon='SNAP_SURFACE')
    row = layout.row(align=0)
    row.operator(WhereAmI.bl_idname, text="Find closest object", icon='SNAP_SURFACE')
    if bpy.context.scene.where_am_i_str != '':
        row.label(text=bpy.context.scene.where_am_i_str)
    if len(WhereAmIPanel.annot_files) > 0:
        col = layout.box().column()
        col.prop(context.scene, 'subject_annot_files', text='')
        col.operator(ClosestLabel.bl_idname, text="Find closest label", icon='SNAP_SURFACE')
        if bpy.context.scene.closest_label_output != '':
            col.label(text=bpy.context.scene.closest_label_output)
        col.prop(context.scene, 'find_closest_label_on_click', text='Find each click on brain')
        if WhereAmIPanel.labels_contours is not None:
            col.prop(context.scene, 'plot_closest_label_contour', text="Plot label's contour")
    layout.operator(ClearWhereAmI.bl_idname, text="Clear", icon='PANEL_CLOSE')


def get_labels_contours():
    return WhereAmIPanel.labels_contours


def tkras_coo_update(self, context):
    if not WhereAmIPanel.call_update:
        return

    # print('tkras_coo_update')
    if WhereAmIPanel.move_cursor:
        bpy.context.scene.cursor_location[0] = bpy.context.scene.tkreg_ras_x / 10
        bpy.context.scene.cursor_location[1] = bpy.context.scene.tkreg_ras_y / 10
        bpy.context.scene.cursor_location[2] = bpy.context.scene.tkreg_ras_z / 10
        _addon().create_slices()
        _addon().slices_zoom()
        if bpy.context.scene.cursor_is_snapped:
            _addon().snap_cursor(True)

    if not t1_trans() is None and WhereAmIPanel.update:
        coo = [bpy.context.scene.tkreg_ras_x, bpy.context.scene.tkreg_ras_y, bpy.context.scene.tkreg_ras_z]
        vox = apply_trans(t1_trans().ras_tkr2vox, np.array([coo]))
        ras = apply_trans(t1_trans().vox2ras, vox)
        WhereAmIPanel.update = False
        set_mni(ras[0])
        set_voxel(vox[0])
        if not _ct_trans() is None:
            ct_vox = apply_trans(_ct_trans().ras2vox, [ras])
            set_ct_coo(ct_vox[0])
        WhereAmIPanel.update = True


def ras_coo_update(self, context):
    if not WhereAmIPanel.call_update:
        return

    # print('ras_coo_update')
    if not t1_trans() is None and WhereAmIPanel.update:
        coo = [bpy.context.scene.ras_x, bpy.context.scene.ras_y, bpy.context.scene.ras_z]
        vox = apply_trans(t1_trans().ras2vox, np.array([coo]))
        ras_tkr = apply_trans(t1_trans().vox2ras_tkr, vox)
        WhereAmIPanel.update = False
        set_tkreg_ras(ras_tkr[0])
        set_voxel(vox[0])
        if not _ct_trans() is None:
            ct_vox = apply_trans(_ct_trans().ras2vox, np.array([coo]))
            set_ct_coo(ct_vox[0])
        WhereAmIPanel.update = True


def voxel_coo_update(self, context):
    if not WhereAmIPanel.call_update:
        return

    # print('voxel_coo_update')
    vox_x, vox_y, vox_z = bpy.context.scene.voxel_x, bpy.context.scene.voxel_y, bpy.context.scene.voxel_z
    if not t1_trans() is None and WhereAmIPanel.update:
        vox = [vox_x, vox_y, vox_z]
        ras = apply_trans(t1_trans().vox2ras, np.array([vox]))
        ras_tkr = apply_trans(t1_trans().vox2ras_tkr, [vox])
        WhereAmIPanel.update = False
        set_tkreg_ras(ras_tkr[0])
        set_mni(ras[0])
        if not _ct_trans() is None:
            ct_vox = apply_trans(_ct_trans().ras2vox, np.array([ras]))
            set_ct_coo(ct_vox[0])
        WhereAmIPanel.update = True
    get_3d_atlas_name()
    if _addon().get_slices_modality() == 'mri':
        set_t1_value()
    elif _addon().get_slices_modality() == 't2':
        set_t2_value()
    # create_slices()


def ct_voxel_coo_update(self, context):
    if not WhereAmIPanel.call_update:
        return

    # print('voxel_coo_update')
    vox_x, vox_y, vox_z = bpy.context.scene.ct_voxel_x, bpy.context.scene.ct_voxel_y, bpy.context.scene.ct_voxel_z
    if t1_trans() is not None and _ct_trans() is not None and WhereAmIPanel.update:
        ct_vox = [vox_x, vox_y, vox_z]
        ras = apply_trans(_ct_trans().vox2ras, np.array([ct_vox]))[0]
        vox = apply_trans(t1_trans().ras2vox, [ras])[0]
        ras_tkr = apply_trans(t1_trans().vox2ras_tkr, [vox])[0]
        WhereAmIPanel.update = False
        set_tkreg_ras(ras_tkr)
        set_mni(ras)
        set_voxel(vox)
        WhereAmIPanel.update = True
    get_3d_atlas_name()
    set_ct_intensity()


def get_3d_atlas_name():
    vox_x, vox_y, vox_z = bpy.context.scene.voxel_x, bpy.context.scene.voxel_y, bpy.context.scene.voxel_z
    names = {}
    for atlas in WhereAmIPanel.vol_atlas.keys():
        try:
            vol_atlas = WhereAmIPanel.vol_atlas[atlas]
            vol_atlas_lut = WhereAmIPanel.vol_atlas_lut[atlas]
            try:
                id = vol_atlas[vox_x, vox_y, vox_z]
            except:
                continue
            id_inds = np.where(vol_atlas_lut['ids'] == id)[0]
            if len(id_inds) == 0:
                continue
            id_ind = id_inds[0]
            names[atlas] = vol_atlas_lut['names'][id_ind]
            if names[atlas] == 'Unknown':
                all_vals = vol_atlas[vox_x - 1:vox_x + 2, vox_y - 1:vox_y + 2, vox_z - 1:vox_z + 2]
                vals = np.unique(all_vals)
                vals = list(set(vals) - set([0]))
                if len(vals) > 0:
                    val = vals[0]
                    if len(vals) > 1:
                        mcs = Counter(all_vals.ravel()).most_common()
                        # print(atlas, mcs)
                        val = mcs[0][0] if val != 0 else mcs[1][0]
                    id_inds = np.where(vol_atlas_lut['ids'] == val)[0]
                    if len(id_inds) > 0:
                        names[atlas] = str(vol_atlas_lut['names'][id_ind])
        except:
            print(traceback.format_exc())
            print('Error in trying to get the 3D atlas voxel value!')
        WhereAmIPanel.atlas_ids = names


def set_tkreg_ras(coo, move_cursor=True):
    # print('set_tkreg_ras')
    WhereAmIPanel.call_update = False
    WhereAmIPanel.move_cursor = move_cursor
    bpy.context.scene.tkreg_ras_x = coo[0]
    bpy.context.scene.tkreg_ras_y = coo[1]
    WhereAmIPanel.call_update = True
    bpy.context.scene.tkreg_ras_z = coo[2]
    WhereAmIPanel.move_cursor = True


def get_tkreg_ras():
    return np.array([bpy.context.scene.tkreg_ras_x, bpy.context.scene.tkreg_ras_y, bpy.context.scene.tkreg_ras_z])


def set_mni(coo):
    # print('set_mni')
    WhereAmIPanel.call_update = False
    bpy.context.scene.ras_x = coo[0]
    bpy.context.scene.ras_y = coo[1]
    WhereAmIPanel.call_update = True
    bpy.context.scene.ras_z = coo[2]


def get_ras():
    return np.array([bpy.context.scene.ras_x, bpy.context.scene.ras_y, bpy.context.scene.ras_z])


def set_voxel(coo):
    # print('set_voxel')
    WhereAmIPanel.call_update = False
    bpy.context.scene.voxel_x = mu.round_np_to_int(coo[0])
    bpy.context.scene.voxel_y = mu.round_np_to_int(coo[1])
    WhereAmIPanel.call_update = True
    bpy.context.scene.voxel_z = mu.round_np_to_int(coo[2])


def get_T1_voxel():
    return np.array([bpy.context.scene.voxel_x, bpy.context.scene.voxel_y, bpy.context.scene.voxel_z])


def set_ct_coo(coo):
    WhereAmIPanel.call_update = False
    bpy.context.scene.ct_voxel_x = mu.round_np_to_int(coo[0])
    bpy.context.scene.ct_voxel_y = mu.round_np_to_int(coo[1])
    WhereAmIPanel.call_update = True
    bpy.context.scene.ct_voxel_z = mu.round_np_to_int(coo[2])
    _addon().set_ct_intensity()


def get_ct_voxel():
    return np.array([bpy.context.scene.ct_voxel_x, bpy.context.scene.ct_voxel_y, bpy.context.scene.ct_voxel_z])


def apply_trans(trans, points):
    return np.array([np.dot(trans, np.append(p, 1))[:3] for p in points])


def find_closest_obj(search_also_for_subcorticals=True):
    distances, names, indices = [], [], []

    parent_objects_names = ['Cortex-lh', 'Cortex-rh']
    if _addon().is_inflated():
        parent_objects_names = ['Cortex-inflated-lh', 'Cortex-inflated-rh']
    if search_also_for_subcorticals:
        parent_objects_names.append('Subcortical_structures')
    for parent_object_name in parent_objects_names:
        parent_object = bpy.data.objects.get(parent_object_name, None)
        if parent_object is None:
            continue
        # if subHierarchy == bpy.data.objects['Subcortical_structures']:
        #     cur_material = bpy.data.materials['unselected_label_Mat_subcortical']
        # else:
        #     cur_material = bpy.data.materials['unselected_label_Mat_cortex']
        for obj in parent_object.children:
            # obj.active_material = cur_material
            obj.select = False
            obj.hide = parent_object.hide

            # 3d cursor relative to the object data
            cursor = bpy.context.scene.cursor_location
            if bpy.context.object and bpy.context.object.parent == bpy.data.objects.get('Deep_electrodes', None):
                cursor = bpy.context.object.location

            co_find = cursor * obj.matrix_world.inverted()

            mesh = obj.data
            size = len(mesh.vertices)
            kd = mathutils.kdtree.KDTree(size)

            for i, v in enumerate(mesh.vertices):
                kd.insert(v.co, i)

            kd.balance()

            # Find the closest point to the 3d cursor
            for (co, index, dist) in kd.find_n(co_find, 1):
                if 'unknown' not in obj.name:
                    distances.append(dist)
                    names.append(obj.name)
                    indices.append(index)

    # print(np.argmin(np.array(distances)))
    min_index = np.argmin(np.array(distances))
    closest_area = names[np.argmin(np.array(distances))]
    # print('closest area is: '+closest_area)
    # print('dist: {}'.format(np.min(np.array(distances))))
    # print('closets vert is {}'.format(bpy.data.objects[closest_area].data.vertices[min_index].co))
    return closest_area


def find_closest_label(atlas=None, plot_contour=True):
    subjects_dir = mu.get_link_dir(mu.get_links_dir(), 'subjects')
    if bpy.context.scene.cursor_is_snapped:
        vertex_ind, hemi = _addon().get_closest_vertex_and_mesh_to_cursor()
    else:
        closest_mesh_name, vertex_ind, _ = \
            _addon().find_closest_vertex_index_and_mesh(use_shape_keys=True)
        hemi = closest_mesh_name[len('infalted_'):] if _addon().is_inflated() else closest_mesh_name
    if vertex_ind == -1:
        print("find_closest_label: Can't find the closest vertex")
        return
    hemi = 'rh' if 'rh' in hemi else 'lh'
    if atlas is None:
        atlas = bpy.context.scene.subject_annot_files
    annot_fname = op.join(subjects_dir, mu.get_user(), 'label', '{}.{}.annot'.format(hemi, atlas))
    if not op.isfile(annot_fname):
        annot_fname = op.join(mu.get_user_fol(), 'labels', '{}.{}.annot'.format(hemi, atlas))
    if op.isfile(annot_fname):
        labels = mu.read_labels_from_annot(annot_fname)
        vert_labels = [l for l in labels if vertex_ind in l.vertices]
        if len(vert_labels) > 0:
            label = vert_labels[0]
            bpy.context.scene.closest_label_output = label.name
            if plot_contour:
                plot_closest_label_contour(label.name, hemi)
        return label.name
    else:
        print("Can't find the annotation file for atlas {}!".format(atlas))


def plot_closest_label_contour(label, hemi):
    # contours_files = glob.glob(op.join(mu.get_user_fol(), 'labels', '*contours_lh.npz'))
    # contours_names = [mu.namebase(fname)[:-len('_contours_lh')] for fname in contours_files]
    # if bpy.context.scene.subject_annot_files in contours_names:
    if WhereAmIPanel.labels_contours is not None:
        # bpy.context.scene.contours_coloring = bpy.context.scene.subject_annot_files
        _addon().color_contours([label], hemi, WhereAmIPanel.labels_contours, False, False, (0, 0, 1))
    else:
        mu.create_labels_contours()


# @mu.timeit
def update_slices(modality='mri', ratio=1, images=None):
    screen = bpy.data.screens['Neuro']
    perspectives = ['sagital', 'coronal', 'axial']
    images_names = ['{}.{}'.format(pres, _addon().get_figure_format()) for pres in perspectives]
    images_fol = op.join(mu.get_user_fol(), 'figures', 'slices')
    ind = 0
    for area in screen.areas:
        if area.type == 'IMAGE_EDITOR':
            override = bpy.context.copy()
            override['area'] = area
            override["screen"] = screen
            if images is None:
                if images_names[ind] not in bpy.data.images:
                    bpy.data.images.load(op.join(images_fol, images_names[ind]), check_existing=False)
                    area.spaces.active.mode = 'MASK'
                # bpy.data.images[images_names[ind]].reload()
                image = bpy.data.images[images_names[ind]]
                image.reload()
            else:
                image = images[perspectives[ind]]
                if area.spaces.active.mode != 'MASK':
                    area.spaces.active.mode = 'MASK'
            area.spaces.active.image = image
            # bpy.ops.image.replace(override, filepath=op.join(images_fol, images_names[ind]))
            # Takes ~1s, should find a better way to do it (if at all)
            # bpy.ops.image.view_zoom_ratio(override, ratio=ratio)
            ind += 1


def init_slices():
    ftype = _addon().get_figure_format()
    extra_images = set([img.name for img in bpy.data.images]) - set(['Render Result']) - \
                   set(['coronal.{}'.format(ftype), 'axial.{}'.format(ftype), 'sagital.{}'.format(ftype)])
    try:
        for img_name in extra_images:
            if img_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[img_name])
    except:
        pass
    # save_slices_cursor_pos()


def start_slicer_server():
    cmd = '{} -m src.listeners.slicer_listener'.format(bpy.context.scene.python_cmd)
    mu.run_command_in_new_thread(cmd, False)


def init_listener():
    if mu.conn_to_listener.handle_is_open:
        return True
    ret = False
    tries = 0
    while not ret and tries < 3:
        try:
            ret = mu.conn_to_listener.init()
            if ret:
                mu.conn_to_listener.send_command(b'Hey!\n')
            else:
                mu.message(None, 'Error initialize the listener. Try again')
        except:
            print("Can't open connection to listener")
            print(traceback.format_exc())
        tries += 1
    return ret


def calc_tkreg_ras_from_cursor():
    tkreg_ras = None
    if _addon().is_pial():
        tkreg_ras = bpy.context.scene.cursor_location * 10
    elif bpy.context.scene.cursor_is_snapped:
        tkreg_ras = calc_tkreg_ras_from_snapped_cursor()
    return tkreg_ras


def calc_tkreg_ras_from_snapped_cursor():
    vert, obj_name = _addon().get_closest_vertex_and_mesh_to_cursor()
    pos = None
    if obj_name != '' and ('rh' in obj_name or 'lh' in obj_name):
        obj_name = 'rh' if 'rh' in obj_name else 'lh'
        ob = bpy.data.objects[obj_name]
        pos = ob.data.vertices[vert].co
    return pos


def create_slices(modality=None, pos=None, zoom_around_voxel=None, zoom_voxels_num=-1, smooth=None, clim=None,
                  plot_cross=None, mark_voxel=None, pos_in_vox=False):
    if zoom_around_voxel is None:
        zoom_around_voxel = bpy.context.scene.slices_zoom_around_voxel
    if zoom_voxels_num == -1:
        zoom_voxels_num = bpy.context.scene.slices_zoom_voxels_num
    if smooth is None:
        smooth = bpy.context.scene.slices_zoom_interpolate
    if clim is None:
        clim = (bpy.context.scene.slices_x_min, bpy.context.scene.slices_x_max)
    if plot_cross is None:
        plot_cross = bpy.context.scene.slices_plot_cross
    if mark_voxel is None:
        mark_voxel = bpy.context.scene.slices_mark_voxel

    if WhereAmIPanel.slicer_state.mri is None:
        return
    if modality is None:
        modality = bpy.context.scene.slices_modality
    pos_was_none = pos is None
    if pos is None:
        pos = bpy.context.scene.cursor_location * 10
    # if bpy.context.scene.cursor_is_snapped and pos_was_none:
    #     pos = calc_tkreg_ras_from_snapped_cursor()
    if pos_was_none:
        pos = calc_tkreg_ras_from_cursor()
    if pos is None:
        print("Can't calc slices if the cursor isn't snapped and the brain is inflated!")
        return
    # pos = np.array(pos) * 10
    if WhereAmIPanel.run_slices_listener:
        init_listener()
        xyz = ','.join(map(str, pos))
        ret = mu.conn_to_listener.send_command(dict(cmd='slice_viewer_change_pos', data=dict(
            subject=mu.get_user(), xyz=xyz, modalities=modality, coordinates_system='tk_ras')))
        flag_fname = op.join(mu.get_user_fol(), 'figures', 'slices', '{}_slices.txt'.format(
            '_'.join(modality.split(','))))
        bpy.ops.mmvt.wait_for_slices()
        return

    if WhereAmIPanel.mri_data is None or WhereAmIPanel.gray_colormap is None:
        print('To be able to see the slices, you need to do the following:')
        if WhereAmIPanel.mri_data is None:
            print('python -m src.preproc.anatomy -s {} -f save_images_data_and_header'.format(mu.get_user()))
        if WhereAmIPanel.gray_colormap is None:
            print('python -m src.setup -f copy_resources_files')
        return

    if modality in ('mri', 't1_ct'):
        x, y, z = np.rint(apply_trans(t1_trans().ras_tkr2vox, np.array([pos]))[0]).astype(int) if not pos_in_vox else pos
    elif modality == 't2':
        x, y, z = np.rint(apply_trans(t2_trans().ras_tkr2vox, np.array([pos]))[0]).astype(int) if not pos_in_vox else pos
    elif modality == 'ct':
        vox = apply_trans(t1_trans().ras_tkr2vox, np.array([pos]))[0] if not pos_in_vox else pos
        ras = apply_trans(t1_trans().vox2ras, np.array([vox]))[0]
        x, y, z = np.rint(apply_trans(_ct_trans().ras2vox, np.array([ras]))[0]).astype(int)
    xyz = [x, y, z]
    # print('Create slices, slicer_state.coordinates: {}'.format(WhereAmIPanel.slicer_state.coordinates))
    create_slices_from_vox_coordinates(xyz, modality, zoom_around_voxel, zoom_voxels_num, smooth, clim, plot_cross,
                                       mark_voxel)


def create_slices_from_vox_coordinates(xyz, modality, zoom_around_voxel=False, zoom_voxels_num=30, smooth=False,
                                       clim=None, plot_cross=True, mark_voxel=True):
    images = slicer.create_slices(
        _addon(), xyz, WhereAmIPanel.slicer_state, modality, zoom_around_voxel=zoom_around_voxel, zoom_voxels_num=zoom_voxels_num,
        smooth=smooth, clim=clim, plot_cross=plot_cross, mark_voxel=mark_voxel)
    update_slices(modality=modality, ratio=1, images=images)
    #todo: really slow...
    # _addon().slices_zoom()


def save_slices_cursor_pos():
    screen = bpy.data.screens['Neuro']
    for area in screen.areas:
        if area.type == 'IMAGE_EDITOR':
            active_image = area.spaces.active.image
            if active_image is not None:
                pos = area.spaces.active.cursor_location
                WhereAmIPanel.slices_cursor_pos[active_image.name] = tuple(pos)


def get_slices_cursor_pos():
    return WhereAmIPanel.slices_cursor_pos


def get_annot_files():
    return WhereAmIPanel.annot_files


def slices_were_clicked(active_image, pos):
    if WhereAmIPanel.slicer_state.mri is None:
        return
    modality = bpy.context.scene.slices_modality
    images_names = ['{}.{}'.format(persp, _addon().get_figure_format()) for persp in ['sagital', 'coronal', 'axial']]
    # images_names = ['mri_sagital.png', 'mri_coronal.png', 'mri_axial.png']
    WhereAmIPanel.slices_cursor_pos[active_image.name] = pos
    print('Image {} was click in {}'.format(active_image.name, pos))
    # print(active_image.name, pos)
    image_ind = images_names.index(active_image.name.lower())
    new_pos_vox = slicer.on_click(_addon(), image_ind, pos, WhereAmIPanel.slicer_state, modality)
    if modality == 'ct':
        new_pial_ras = apply_trans(_ct_trans().vox2ras, np.array([new_pos_vox]))[0]
        new_pos_vox = apply_trans(t1_trans().ras2vox, np.array([new_pial_ras]))[0]
    new_pos_pial = apply_trans(t1_trans().vox2ras_tkr, np.array([new_pos_vox]))[0]#.astype(np.int)[0]
    if _addon().appearance.cursor_is_snapped():
        # Find the closest vertex on the pial brain, and convert it to the current inflation
        new_pos_pial = pos_to_current_inflation(new_pos_pial)
    else:
        new_pos_pial = new_pos_pial / 10
    bpy.context.scene.cursor_location = new_pos_pial
    _addon().save_cursor_position()
    _addon().set_ct_intensity()
    return new_pos_pial
    # print('image_found: {}'.format(image_found))
    # save_slices_cursor_pos()


def mni305_ras_to_subject_tkreg_ras(mni305_ras):
    matrix_world = mu.get_matrix_world()
    if mu.get_user() == 'fsaverage':
        ras_tkr = mathutils.Vector(mni305_ras) * matrix_world
    else:
        vox = mu.apply_trans(np.linalg.inv(t1_trans().vox2ras), mni305_ras)
        ras_tkr = mathutils.Vector(mu.apply_trans(np.linalg.inv(t1_trans().ras_tkr2vox), vox)) * matrix_world
    return ras_tkr


def pos_to_current_inflation(pos, hemis=mu.HEMIS, subject_tkreg_ras=False):
    if not subject_tkreg_ras:
        pos = mathutils.Vector(pos) * mu.get_matrix_world()
    closest_mesh_name, vertex_ind, vertex_co = _addon().find_closest_vertex_index_and_mesh(pos, hemis)
    obj = bpy.data.objects['inflated_{}'.format(closest_mesh_name)]
    me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
    try:
        new_pos = me.vertices[vertex_ind].co * mu.get_matrix_world()
        # Bug in windows, Blender crashses here
        # todo: Figure out why...
        if not mu.IS_WINDOWS:
            bpy.data.meshes.remove(me)
        return new_pos
    except:
        print('pos_to_current_inflation: Error! ({})'.format(pos))
        return np.array([0, 0, 0])


def set_slicer_state(modality):
    if WhereAmIPanel.slicer_state is None or modality not in WhereAmIPanel.slicer_state:
        WhereAmIPanel.slicer_state[modality] = slicer.init(_addon(), modality)


def get_slicer_state(modality):
    return WhereAmIPanel.slicer_state.get(modality, None)


# def load_slicer_fmri_vol_data():
#     WhereAmIPanel.slicer_state['mri'].fmri_vol =

def clipboard_to_coords():
    clipboard = bpy.context.window_manager.clipboard
    if ',' in clipboard:
        coords = clipboard.split(',')
    elif ' ' in clipboard:
        coords = clipboard.split(' ')
    else:
        print("Can't find 3 coordinates in clipboard!")
        return None

    coords = [x.strip() for x in coords]
    if all([mu.is_float(x) for x in coords]):
        return [float(x) for x in coords]
    else:
        print("Can't find 3 coordinates in clipboard! '{}'".format(clipboard))
        return None


def clipboard_to_tkreg():
    coords = clipboard_to_coords()
    if coords is not None:
        set_tkreg_ras(coords)
        create_slices()


def tkreg_to_clipboard():
    bpy.context.window_manager.clipboard = ','.join([str(x) for x in get_tkreg_ras()])


def clipboard_to_mni():
    coords = clipboard_to_coords()
    if coords is not None:
        set_mni(coords)
        create_slices()


def mni_to_clipboard():
    bpy.context.window_manager.clipboard = ','.join(['{:.2f}'.format(x) for x in get_ras()])


class WaitForSlices(bpy.types.Operator):
    bl_idname = "mmvt.wait_for_slices"
    bl_label = "wait_for_slices"
    bl_options = {"UNDO"}
    running = False
    modalities = 'mri'

    def cancel(self, context):
        # print('WaitForSlices: cancel')
        try:
            if self._timer:
                context.window_manager.event_timer_remove(self._timer)
                self._timer = None
                self.running = False
        except:
            print('Error in WaitForSlices.cancel')
        return {'CANCELLED'}

    def invoke(self, context, event=None):
        # print('WaitForSlices: invoke')
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # print('WaitForSlices: execute')
        if not self.running:
            self.running = True
            context.window_manager.modal_handler_add(self)
            self._timer = context.window_manager.event_timer_add(0.1, context.window)
            return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER' and self.running:
            output_file = op.join(mu.get_user_fol(), 'figures', 'slices', '{}_slices.txt'.format(
                '_'.join(self.modalities.split(','))))
            if op.isfile(output_file):
                os.remove(output_file)
                # print('took {:.5f}s'.format(time.time() - WhereAmIPanel.tic))
                update_slices()
                self.cancel(context)
        return {'PASS_THROUGH'}


class ChooseVoxelID(bpy.types.Operator):
    bl_idname = "mmvt.choose_voxel_id"
    bl_label = "mmvt choose_voxel_id"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        obj = bpy.data.objects.get(bpy.context.scene.where_am_i_atlas, None)
        if not obj is None:
            obj.select = True
        return {"FINISHED"}


class ClipboardToTkreg(bpy.types.Operator):
    bl_idname = "mmvt.clipboard_to_tkreg"
    bl_label = "mmvt clipboard_to_tkreg"
    bl_description = 'Paste\n\nScript: mmvt.where_am_i.clipboard_to_tkreg()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        clipboard_to_tkreg()
        return {"FINISHED"}


class TkregToClipboard(bpy.types.Operator):
    bl_idname = "mmvt.tkreg_to_clipboard"
    bl_label = "mmvt tkreg_to_clipboard"
    bl_description = 'Copy\n\nScript: mmvt.where_am_i.tkreg_to_clipboard()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        tkreg_to_clipboard()
        return {"FINISHED"}


class MNIToClipboard(bpy.types.Operator):
    bl_idname = "mmvt.mni_to_clipboard"
    bl_label = "mmvt mni_to_clipboard"
    bl_description = 'Copy\n\nScript: mmvt.where_am_i.mni_to_clipboard()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        mni_to_clipboard()
        return {"FINISHED"}


class ClipboardToMNI(bpy.types.Operator):
    bl_idname = "mmvt.clipboard_to_mni"
    bl_label = "mmvt clipboard_to_mni"
    bl_description = 'Copy\n\nScript: mmvt.where_am_i.clipboard_to_mni()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        clipboard_to_mni()
        return {"FINISHED"}


class ClosestLabel(bpy.types.Operator):
    bl_idname = "mmvt.closest_label"
    bl_label = "mmvt closest label"
    bl_description = 'Finds the closest label to the cursor according to the chosen atlas above.' \
                     '\n\nScript: mmvt.where_am_i.find_closest_label(plot_contour=bpy.context.scene.plot_closest_label_contour)'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        find_closest_label(plot_contour=bpy.context.scene.plot_closest_label_contour)
        return {"FINISHED"}


class WhereAmI(bpy.types.Operator):
    bl_idname = "mmvt.where_i_am"
    bl_label = "mmvt where i am"
    bl_description = 'Finds the closest object to the cursor'
    bl_options = {"UNDO"}

    where_am_I_selected_obj = None
    where_am_I_selected_obj_org_hide = True

    # @staticmethod
    # def setup_environment(self):
    #     WhereAmIPanel.addon.show_rois()

    @staticmethod
    def main_func(self):
        bpy.data.objects['Brain'].select = False
        closest_area = find_closest_obj()
        bpy.types.Scene.where_am_i_str = closest_area
        WhereAmI.where_am_I_selected_obj = bpy.data.objects[closest_area]
        WhereAmI.where_am_I_selected_obj_org_hide = bpy.data.objects[closest_area].hide
        bpy.context.scene.objects.active = bpy.data.objects[closest_area]
        # closest_area_type = mu.check_obj_type(closest_area)
        # if closest_area_type in [mu.OBJ_TYPE_CORTEX_LH, mu.OBJ_TYPE_CORTEX_RH, mu.OBJ_TYPE_ELECTRODE,
        #                          mu.OBJ_TYPE_EEG]:
        #
        #     _addon().select_roi(closest_area)
        # else:
        #     bpy.data.objects[closest_area].select = True
        bpy.data.objects[closest_area].hide = False
        # todo: don't change the material! Do something else!
        # bpy.data.objects[closest_area].active_material = bpy.data.materials['selected_label_Mat']

    def invoke(self, context, event=None):
        # self.setup_environment(self)
        self.main_func(self)
        return {"FINISHED"}


class ClearWhereAmI(bpy.types.Operator):
    bl_idname = "mmvt.where_am_i_clear"
    bl_label = "where am i clear"
    bl_description = 'Clears all the plotted labels'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        new_mat = bpy.data.materials['unselected_label_Mat_subcortical']
        for subHierarchy in bpy.data.objects['Subcortical_structures'].children:
            for obj in subHierarchy.children:
                obj.active_material = new_mat

        if 'Deep_electrodes' in bpy.data.objects:
            for obj in bpy.data.objects['Deep_electrodes'].children:
                obj.active_material.node_tree.nodes["Layer Weight"].inputs[0].default_value = 1
        if bpy.data.objects.get(' '):
            context.scene.objects.active = bpy.data.objects[' ']

        for obj in bpy.data.objects:
            obj.select = False

        if WhereAmI.where_am_I_selected_obj is not None:
            WhereAmI.where_am_I_selected_obj.hide = WhereAmI.where_am_I_selected_obj_org_hide
            WhereAmI.where_am_I_selected_obj = None

        if bpy.context.scene.closest_label_output != '':
            _addon().clear_cortex()

        bpy.types.Scene.where_am_i_str = ''
        bpy.context.scene.closest_label_output = ''
        bpy.context.scene.new_label_name = 'New-label'
        # where_i_am_draw(self, context)
        return {"FINISHED"}


bpy.types.Scene.where_am_i = bpy.props.StringProperty(description="Find closest curve to cursor",
                                                      update=where_i_am_draw)
bpy.types.Scene.ras_x = bpy.props.FloatProperty(update=ras_coo_update,
    description='Sets the cursor according to X tmni305 coordinates (same as RAS coordinates in Free Surfer).'
                '\n\nScript: mmvt.where_am_i.get_ras() and set_mni(coo)')
bpy.types.Scene.ras_y = bpy.props.FloatProperty(update=ras_coo_update,
    description='Sets the cursor according to Y tmni305 coordinates (same as RAS coordinates in Free Surfer).'
                '\n\nScript: mmvt.where_am_i.get_ras() and set_mni(coo)')
bpy.types.Scene.ras_z = bpy.props.FloatProperty(update=ras_coo_update,
    description='Sets the cursor according to Z tmni305 coordinates (same as RAS coordinates in Free Surfer).'
                '\n\nScript: mmvt.where_am_i.get_ras() and set_mni(coo)')
bpy.types.Scene.tkreg_ras_x = bpy.props.FloatProperty(update=tkras_coo_update,
    description='Sets the cursor according to Free Surfers X tkreg coordinates.'
                '\n\nScript: mmvt.where_am_i.get_tkreg_ras() and set_tkreg_ras(coo, move_cursor=True)')
bpy.types.Scene.tkreg_ras_y = bpy.props.FloatProperty(update=tkras_coo_update,
    description='Sets the cursor according to Free Surfers Y tkreg coordinates.'
                '\n\nScript: mmvt.where_am_i.get_tkreg_ras() and set_tkreg_ras(coo, move_cursor=True)')
bpy.types.Scene.tkreg_ras_z = bpy.props.FloatProperty(update=tkras_coo_update,
    description='Sets the cursor according to Free Surfers Z tkreg coordinates.'
                '\n\nScript: mmvt.where_am_i.get_tkreg_ras() and set_tkreg_ras(coo, move_cursor=True)')
bpy.types.Scene.voxel_x = bpy.props.IntProperty(update=voxel_coo_update,
    description='Sets the cursor according to X T1 Voxel coordinates')
bpy.types.Scene.voxel_y = bpy.props.IntProperty(update=voxel_coo_update,
    description='Sets the cursor according to Y T1 Voxel coordinates')
bpy.types.Scene.voxel_z = bpy.props.IntProperty(update=voxel_coo_update,
    description='Sets the cursor according to Z T1 Voxel coordinates')
bpy.types.Scene.ct_voxel_x = bpy.props.IntProperty(update=ct_voxel_coo_update)
bpy.types.Scene.ct_voxel_y = bpy.props.IntProperty(update=ct_voxel_coo_update)
bpy.types.Scene.ct_voxel_z = bpy.props.IntProperty(update=ct_voxel_coo_update)
bpy.types.Scene.where_am_i_str = bpy.props.StringProperty()
bpy.types.Scene.subject_annot_files = bpy.props.EnumProperty(items=[], description='List of different atlases.\n\nCurrent atlas')
bpy.types.Scene.closest_label_output = bpy.props.StringProperty()
bpy.types.Scene.closest_label = bpy.props.StringProperty()
bpy.types.Scene.cut_type = 'sagital'
bpy.types.Scene.find_closest_label_on_click = bpy.props.BoolProperty(default=False,
    description='Finds the closest label each time an area clicked (right click) on the brain')
bpy.types.Scene.plot_closest_label_contour = bpy.props.BoolProperty(default=False,
    description='Plots the selected label’s contour')

# bpy.types.Scene.where_am_i_atlas = bpy.props.StringProperty()


class WhereAmIPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Where Am I"
    addon = None
    init = False
    subject_t1_trans = None
    subject_t2_trans = None
    subject_ct_trans = None
    vol_atlas = {}
    vol_atlas_lut = {}
    atlas_ids = {}
    update = True
    call_update = True
    move_cursor = True
    mri_data = None
    gray_colormap = None
    slices_cursor_pos = {}
    slicer_state = None
    annot_files = []
    labels_contours = None

    def draw(self, context):
        where_i_am_draw(self, context)


def init(addon):
    try:
        t1_trans_fname = op.join(mu.get_user_fol(), 't1_trans.npz')
        if not op.isfile(t1_trans_fname):
            # backward compatibility
            t1_trans_fname = op.join(mu.get_user_fol(), 'orig_trans.npz')
        t2_trans_fname = op.join(mu.get_user_fol(), 't2_trans.npz')
        ct_trans_fname = op.join(mu.get_user_fol(), 'ct', 'ct_trans.npz')
        volumes = glob.glob(op.join(mu.get_user_fol(), 'freeview', '*+aseg.npy'))
        luts = glob.glob(op.join(mu.get_user_fol(), 'freeview', '*ColorLUT.npz'))
        if op.isfile(t1_trans_fname):
            WhereAmIPanel.subject_t1_trans = mu.Bag(np.load(t1_trans_fname))
        if op.isfile(t2_trans_fname):
            WhereAmIPanel.subject_t2_trans = mu.Bag(np.load(t2_trans_fname))
        if op.isfile(ct_trans_fname):
            WhereAmIPanel.subject_ct_trans = mu.Bag(np.load(ct_trans_fname))
        for atlas_vol_fname, atlas_vol_lut_fname in zip(volumes, luts):
            atlas = mu.namebase(atlas_vol_fname)[:-len('+aseg')]
            WhereAmIPanel.vol_atlas[atlas] = np.load(atlas_vol_fname)
            WhereAmIPanel.vol_atlas_lut[atlas] = np.load(atlas_vol_lut_fname)
        try:
            subjects_dir = mu.get_link_dir(mu.get_links_dir(), 'subjects')
            annot_files = [mu.namebase(fname)[3:] for fname in glob.glob(
                op.join(subjects_dir, mu.get_user(), 'label', 'rh.*.annot'))]
            annot_files += [mu.namebase(fname)[3:] for fname in glob.glob(
                op.join(mu.get_user_fol(), 'labels', 'rh.*.annot'))]
            WhereAmIPanel.annot_files = annot_files = list(set(annot_files))
            if len(annot_files) > 0:
                items = [(c, c, '', ind) for ind, c in enumerate(annot_files)]
                bpy.types.Scene.subject_annot_files = bpy.props.EnumProperty(
                    items=items, update=subject_annot_files_update, description='List of different atlases.\n\nCurrent atlas')
                ind = mu.index_in_list(bpy.context.scene.atlas, annot_files, 0)
                bpy.context.scene.subject_annot_files = annot_files[ind]
            else:
                bpy.types.Scene.subject_annot_files = bpy.props.EnumProperty(items=[])
                # bpy.context.scene.subject_annot_files = ''
        except:
            bpy.types.Scene.subject_annot_files = bpy.props.EnumProperty(items=[])
        bpy.context.scene.closest_label_output = ''
        bpy.context.scene.new_label_r = 5
        bpy.context.scene.find_closest_label_on_click = False
        bpy.context.scene.plot_closest_label_contour = False

        mri_data_fname = op.join(mu.get_user_fol(), 'freeview', 'mri_data.npz')
        if op.isfile(mri_data_fname):
            WhereAmIPanel.mri_data = mu.Bag(np.load(mri_data_fname))
        gray_colormap_fname = op.join(mu.file_fol(), 'color_maps', 'gray.npy')
        if op.isfile(gray_colormap_fname):
            WhereAmIPanel.gray_colormap = np.load(gray_colormap_fname)

        WhereAmIPanel.addon = addon
        WhereAmIPanel.init = True
        WhereAmIPanel.run_slices_listener = False
        init_slices()
        if WhereAmIPanel.run_slices_listener:
            start_slicer_server()
        else:
            WhereAmIPanel.slicer_state = mu.Bag({})
            WhereAmIPanel.slicer_state['mri'] = slicer.init(_addon(), 'mri')
            create_slices(None, bpy.context.scene.cursor_location)
        save_slices_cursor_pos()
        register()
    except:
        print("Can't init where-am-I panel!")
        print(traceback.format_exc())


def register():
    try:
        unregister()
        bpy.utils.register_class(WhereAmIPanel)
        bpy.utils.register_class(WhereAmI)
        bpy.utils.register_class(ClearWhereAmI)
        bpy.utils.register_class(ClosestLabel)
        bpy.utils.register_class(ChooseVoxelID)
        bpy.utils.register_class(ClipboardToTkreg)
        bpy.utils.register_class(TkregToClipboard)
        bpy.utils.register_class(MNIToClipboard)
        bpy.utils.register_class(ClipboardToMNI)
        bpy.utils.register_class(WaitForSlices)
        # print('Where am I Panel was registered!')
    except:
        print("Can't register Where am I Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(WhereAmIPanel)
        bpy.utils.unregister_class(WhereAmI)
        bpy.utils.unregister_class(ClearWhereAmI)
        bpy.utils.unregister_class(ClosestLabel)
        bpy.utils.unregister_class(ChooseVoxelID)
        bpy.utils.unregister_class(ClipboardToTkreg)
        bpy.utils.unregister_class(TkregToClipboard)
        bpy.utils.unregister_class(MNIToClipboard)
        bpy.utils.unregister_class(ClipboardToMNI)
        bpy.utils.unregister_class(WaitForSlices)
    except:
        # print("Can't unregister Where am I Panel!")
        pass
