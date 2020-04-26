import os.path as op
import numpy as np
import glob
from queue import Empty
from collections import Counter

try:
    from scipy.spatial.distance import cdist
except:
    print('No scipy!')

try:
    import bpy
    import bpy_extras
    import mmvt_utils as mu
    BLENDER_EMBEDDED = True
except:
    from src.mmvt_addon import mmvt_utils as mu
    bpy = mu.dummy_bpy()
    BLENDER_EMBEDDED = False


def _addon():
    return fMRIPanel.addon


def get_clusters_file_names():
    return fMRIPanel.clusters_labels_file_names


def get_parcs_files(user_fol, fmri_file_name):
    fMRIPanel.clusters_labels_files = clusters_labels_files = \
        glob.glob(op.join(user_fol, 'fmri', 'clusters_labels_{}*.pkl'.format(fmri_file_name)))
    return list(set([mu.namebase(fname).split('_')[-1] for fname in clusters_labels_files]))


def fMRI_clusters_files_exist():
    return fMRIPanel.fMRI_clusters_files_exist


def clusters_update(self, context):
    _clusters_update()


def _clusters_update():
    if fMRIPanel.addon is None or not fMRIPanel.init:
        return
    clusters_labels_file = bpy.context.scene.fmri_clusters_labels_files
    # key = '{}_{}'.format(clusters_labels_file, bpy.context.scene.fmri_clusters_labels_parcs)
    key = clusters_labels_file
    fMRIPanel.cluster_labels = cluster = fMRIPanel.lookup[key][bpy.context.scene.fmri_clusters]
    cluster_centroid = np.mean(cluster['coordinates'], 0) / 10.0
    _addon().clear_closet_vertex_and_mesh_to_cursor()
    _addon().set_vertex_data(cluster['max'])
    if 'max_vert' in cluster:
        bpy.context.scene.cursor_location = mu.get_vert_co(cluster.max_vert, cluster.hemi)
        _addon().set_closest_vertex_and_mesh_to_cursor(cluster.max_vert, 'inflated_{}'.format(cluster.hemi))
    else:
        if _addon().is_pial():
            bpy.context.scene.cursor_location = cluster_centroid
            closest_mesh_name, vertex_ind, vertex_co = _addon().find_closest_vertex_index_and_mesh(
                cluster_centroid, mu.HEMIS, False)
            _addon().set_closest_vertex_and_mesh_to_cursor(vertex_ind, closest_mesh_name)
        else:
            closest_mesh_name, vertex_ind, vertex_co = _addon().find_closest_vertex_index_and_mesh(
                cluster_centroid, mu.HEMIS, False)
            inflated_mesh = 'inflated_{}'.format(closest_mesh_name)
            me = bpy.data.objects[inflated_mesh].to_mesh(bpy.context.scene, True, 'PREVIEW')
            bpy.context.scene.cursor_location = me.vertices[vertex_ind].co / 10.0
            bpy.data.meshes.remove(me)
            _addon().set_closest_vertex_and_mesh_to_cursor(vertex_ind, closest_mesh_name)

    tkreg_ras = _addon().calc_tkreg_ras_from_cursor()
    if tkreg_ras is not None:
        _addon().set_tkreg_ras(tkreg_ras, move_cursor=False)

    if bpy.context.scene.plot_current_cluster and not fMRIPanel.blobs_plotted:
        faces_verts = fMRIPanel.addon.get_faces_verts()
        if bpy.context.scene.fmri_what_to_plot == 'blob':
            plot_blob(cluster, faces_verts, True)
    if bpy.context.scene.plot_fmri_cluster_contours:
        inter_labels = [inter_label['name'] for inter_label in cluster['intersects']]
        atlas = fMRIPanel.clusters_labels[bpy.context.scene.fmri_clusters_labels_files].atlas
        _addon().color_contours(
            inter_labels, cluster.hemi, None, False, False,
            specific_colors=bpy.context.scene.fmri_cluster_contours_color, atlas=atlas)

    _addon().save_cursor_position()
    _addon().create_slices(pos=tkreg_ras)
    find_electrodes_in_cluster()
    if bpy.context.scene.fmri_rotate_view_to_vertice:
        mu.rotate_view_to_vertice()


def fmri_blobs_percentile_min_update(self, context):
    if bpy.context.scene.fmri_blobs_percentile_min > bpy.context.scene.fmri_blobs_percentile_max:
        bpy.context.scene.fmri_blobs_percentile_min = bpy.context.scene.fmri_blobs_percentile_max


def fmri_blobs_percentile_max_update(self, context):
    if bpy.context.scene.fmri_blobs_percentile_max < bpy.context.scene.fmri_blobs_percentile_min:
        bpy.context.scene.fmri_blobs_percentile_max = bpy.context.scene.fmri_blobs_percentile_min


def plot_blob(cluster_labels, faces_verts, is_inflated=None, use_abs=None):
    if use_abs is None:
        use_abs = bpy.context.scene.coloring_use_abs
    is_inflated = _addon().is_inflated() if is_inflated is None else is_inflated
    fMRIPanel.dont_show_clusters_info = False
    _addon().init_activity_map_coloring('FMRI')#, subcorticals=False)
    blob_vertices = cluster_labels['vertices']
    hemi = cluster_labels['hemi']
    real_hemi = hemi
    if is_inflated:
        hemi = 'inflated_{}'.format(hemi)
    # fMRIPanel.blobs_plotted = True
    fMRIPanel.colors_in_hemis[hemi] = True
    activity = fMRIPanel.constrast[real_hemi]
    blob_activity = np.zeros(activity.shape)
    blob_activity[blob_vertices] = activity[blob_vertices]
    if fMRIPanel.blobs_activity is None:
        fMRIPanel.blobs_activity, _ = calc_blobs_activity(
            fMRIPanel.constrast, fMRIPanel.clusters_labels_filtered, fMRIPanel.colors_in_hemis)
    # colors_ratio = 256 / (data_max - data_min)
    data_min, colors_ratio = calc_colors_ratio(fMRIPanel.blobs_activity)
    threshold = bpy.context.scene.fmri_clustering_threshold
    cur_obj = bpy.data.objects[hemi]
    _addon().activity_map_obj_coloring(
        cur_obj, blob_activity, faces_verts[real_hemi], threshold, True,
        data_min=data_min, colors_ratio=colors_ratio, use_abs=use_abs)
    other_real_hemi = mu.other_hemi(real_hemi)
    other_hemi = mu.other_hemi(hemi)
    if other_hemi in fMRIPanel.colors_in_hemis and fMRIPanel.colors_in_hemis[other_hemi]:
        _addon().clear_cortex([other_real_hemi])
        fMRIPanel.colors_in_hemis[other_hemi] = False


def calc_clusters():
    import importlib
    mu.add_mmvt_code_root_to_path()
    from src.preproc import fMRI
    importlib.reload(fMRI)
    surf_template_fname = 'fmri_{}.?h.npy'.format(_addon().coloring.get_select_fMRI_contrast())
    print(mu.get_user(), surf_template_fname, bpy.context.scene.fmri_clustering_threshold, bpy.context.scene.atlas)
    fMRI.find_clusters(mu.get_user(), surf_template_fname, bpy.context.scene.fmri_clustering_threshold,
                       bpy.context.scene.subject_annot_files)
    # init(_addon())


# @mu.profileit()
def find_closest_cluster(only_within=False):
    # cursor = np.array(bpy.context.scene.cursor_location)
    # print('cursor {}'.format(cursor))
    if bpy.context.scene.cursor_is_snapped:
        # vertex_ind, mesh = _addon().get_closest_vertex_and_mesh_to_cursor()
        # pial_mesh = 'rh' if mesh == 'inflated_rh' else 'lh'
        vertex_co = _addon().get_tkreg_ras()
    else:
        if _addon().is_inflated(): # and _addon().get_inflated_ratio() == 1:
            closest_mesh_name, vertex_ind, vertex_co = _addon().find_closest_vertex_index_and_mesh(
                use_shape_keys=True)
            # print(closest_mesh_name, vertex_ind, vertex_co)
            # print(vertex_co - bpy.context.scene.cursor_location)
            bpy.context.scene.cursor_location = vertex_co
            _addon().set_closest_vertex_and_mesh_to_cursor(vertex_ind, closest_mesh_name)
            pial_mesh = 'rh' if closest_mesh_name == 'inflated_rh' else 'lh'
            pial_vert = bpy.data.objects[pial_mesh].data.vertices[vertex_ind]
            vertex_co = pial_vert.co
            _addon().set_tkreg_ras(vertex_co, move_cursor=False)
        else:
            closest_mesh_name, vertex_ind, vertex_co = _addon().find_closest_vertex_index_and_mesh()
            bpy.context.scene.cursor_location = vertex_co

    # vertex_co *= 10
    if bpy.context.scene.search_closest_cluster_only_in_filtered:
        cluster_to_search_in = fMRIPanel.clusters_labels_filtered
    else:
        clusters_labels_file = bpy.context.scene.fmri_clusters_labels_files
        # key = '{}_{}'.format(clusters_labels_file, bpy.context.scene.fmri_clusters_labels_parcs)
        key = clusters_labels_file
        cluster_to_search_in = fMRIPanel.clusters_labels[key]['values']
        unfilter_clusters()
    # dists, indices = [], []
    # print('cursor: {}'.format(vertex_co))
    # for ind, cluster in enumerate(cluster_to_search_in):
    #     print(np.mean(cluster['coordinates'], 0))
    #     _, _, dist = mu.min_cdist(cluster['coordinates'], [vertex_co])[0]
    #     dists.append(dist)
    max_verts = np.array([bpy.data.objects[cluster.hemi].data.vertices[cluster.max_vert].co for
                      cluster in cluster_to_search_in])
    dists = [np.linalg.norm(blob - vertex_co) for blob in max_verts]
    if len(dists) == 0:
        print('No cluster was found!')
    else:
        min_index = np.argmin(np.array(dists))
        min_dist = dists[min_index]
        if not (only_within and min_dist > 1):
            fMRIPanel.dont_show_clusters_info = False
            closest_cluster = cluster_to_search_in[min_index]
            bpy.context.scene.fmri_clusters = cluster_name(closest_cluster)
            fMRIPanel.cluster_labels = closest_cluster
            print('Closest cluster: {}, dist: {}'.format(bpy.context.scene.fmri_clusters, min_dist))
            if bpy.context.scene.plot_fmri_cluster_contours:
                inter_labels = [inter_label['name'] for inter_label in closest_cluster['intersects']]
                atlas = fMRIPanel.clusters_labels[bpy.context.scene.fmri_clusters_labels_files].atlas
                _addon().color_contours(inter_labels, closest_cluster.hemi, None, False, False,
                                        specific_colors=bpy.context.scene.fmri_cluster_contours_color, atlas=atlas)
        # _clusters_update()
        else:
            print('only within: dist to big ({})'.format(min_dist))


class CalcClusters(bpy.types.Operator):
    bl_idname = 'mmvt.calc_clusters'
    bl_label = 'calc_clusters'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        calc_clusters()
        return {'FINISHED'}


class NextCluster(bpy.types.Operator):
    bl_idname = 'mmvt.next_cluster'
    bl_label = 'nextCluster'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        next_cluster()
        return {'FINISHED'}


def next_cluster():
    index = fMRIPanel.clusters.index(bpy.context.scene.fmri_clusters)
    next_cluster = fMRIPanel.clusters[index + 1] if index < len(fMRIPanel.clusters) - 1 else fMRIPanel.clusters[0]
    bpy.context.scene.fmri_clusters = next_cluster


class PrevCluster(bpy.types.Operator):
    bl_idname = 'mmvt.prev_cluster'
    bl_label = 'prevcluster'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        prev_cluster()
        return {'FINISHED'}


def prev_cluster():
    index = fMRIPanel.clusters.index(bpy.context.scene.fmri_clusters)
    prev_cluster = fMRIPanel.clusters[index - 1] if index > 0 else fMRIPanel.clusters[-1]
    bpy.context.scene.fmri_clusters = prev_cluster


def fmri_clusters_update(self, context):
    if fMRIPanel.init:
        update_clusters()


def show_only_electrodes_near_cluster_update(self, context):
    _show_only_electrodes_near_cluster_update()


def _show_only_electrodes_near_cluster_update():
    electrodes = _addon().electrodes.get_electrodes_names()
    electrodes_in_cluster = set([elc_name for _, elc_name, _, _ in fMRIPanel.electrodes_in_cluster])
    for elc_name in electrodes:
        bpy.data.objects[elc_name].hide = elc_name not in electrodes_in_cluster if \
            bpy.context.scene.show_only_electrodes_near_cluster else False


def load_fmri_cluster(file_name):
     bpy.context.scene.fmri_clusters_labels_files = file_name


def load_current_fmri_clusters_labels_file():
    constrast_name = bpy.context.scene.fmri_clusters_labels_files
    minmax_fname = op.join(mu.get_user_fol(), 'fmri', '{}_minmax.pkl'.format('_'.join(constrast_name.split('_')[:-1])))
    minmax_exist = op.isfile(minmax_fname)
    # if minmax_exist and not _addon().colorbar_values_are_locked():
    #     min_val, max_val = mu.load(minmax_fname)
    #     _addon().set_colorbar_max_min(max_val, min_val)
    fMRIPanel.constrast = {}
    for hemi in mu.HEMIS:
        contrast_fname = get_contrast_fname(constrast_name, hemi)
        if contrast_fname != '':
            print('Loading {}'.format(contrast_fname))
            fMRIPanel.constrast[hemi] = np.load(contrast_fname)
    if not minmax_exist:
        data = None
        for hemi in mu.HEMIS:
            if hemi in fMRIPanel.constrast:
                x_ravel = fMRIPanel.constrast[hemi]
                data = x_ravel if data is None else np.hstack((x_ravel, data))
        norm_percs = (bpy.context.scene.fmri_blobs_percentile_min, bpy.context.scene.fmri_blobs_percentile_max)
        min_val, max_val = mu.calc_min_max(data, norm_percs=norm_percs)
        _addon().colorbar.set_colorbar_max_min(max_val, min_val, force_update=True)
        mu.save((min_val, max_val), minmax_fname)


def get_contrast_fname(constrast_name, hemi):
    if len(constrast_name.split('_')) == 1:
        constrast_name_template = constrast_name
    else:
        constrast_name_template = '_'.join(constrast_name.split('_')[:-1])
    contrast_fnames = glob.glob(op.join(mu.get_user_fol(), 'fmri', 'fmri_{}*{}.npy'.format(
        constrast_name_template, hemi)))
    if len(contrast_fnames) == 0:
        contrasts = [mu.namebase(f) for f in glob.glob(op.join(mu.get_user_fol(), 'fmri', 'fmri_*{}.npy'.format(hemi)))]
        contrasts = [c for c in contrasts if constrast_name_template.lower() in c.lower()]
        contrast_fnames = [op.join(mu.get_user_fol(), 'fmri', '{}.npy'.format(c)) for c in contrasts]
    if len(contrast_fnames) == 0:
        print("fmri_clusters_labels_files_update: Couldn't find  any clusters data! ({})".format(constrast_name_template))
        return ''
    else:
        if len(contrast_fnames) > 1:
            print("fmri_clusters_labels_files_update: Too many clusters data! ({})".format(constrast_name_template))
            print(contrast_fnames)
        return contrast_fnames[0]


def fmri_clusters_labels_parcs_update(self, context):
    load_current_fmri_clusters_labels_file()
    if fMRIPanel.init:
        clear()
        update_clusters()


def fmri_clusters_labels_files_update(self, context):
    load_current_fmri_clusters_labels_file()
    parcs = get_parcs_files(mu.get_user_fol(), bpy.context.scene.fmri_clusters_labels_files)
    clusters_labels_parcs = [(c, c, '', ind) for ind, c in enumerate(parcs)]
    bpy.types.Scene.fmri_clusters_labels_parcs = bpy.props.EnumProperty(
        items=clusters_labels_parcs, description="fMRI parcs", update=fmri_clusters_labels_parcs_update)
    bpy.context.scene.fmri_clusters_labels_parcs = parcs[0]

    if fMRIPanel.init:
        clear()
        update_clusters()
        fMRIPanel.blobs_activity, _ = calc_blobs_activity(
            fMRIPanel.constrast, fMRIPanel.clusters_labels_filtered, fMRIPanel.colors_in_hemis)


def fmri_how_to_sort_update(self, context):
    if fMRIPanel.init:
        update_clusters()


def update_clusters(val_threshold=None, size_threshold=None, clusters_name=None):
    if not fMRIPanel.update:
        return
    fMRIPanel.dont_show_clusters_info = False
    clusters_labels_file = bpy.context.scene.fmri_clusters_labels_files
    key = clusters_labels_file
    if key not in fMRIPanel.clusters_labels:
        return
    fMRIPanel.update = False
    if val_threshold is None:
        val_threshold = bpy.context.scene.fmri_cluster_val_threshold = bpy.context.scene.fmri_clustering_threshold = \
            fMRIPanel.clusters_labels[key]['threshold']
    if size_threshold is None:
        size_threshold = bpy.context.scene.fmri_cluster_size_threshold
    if clusters_name is None:
        clusters_name = bpy.context.scene.fmri_clustering_filter
    fMRIPanel.update = True
    # if isinstance(fMRIPanel.clusters_labels[key], dict):
    #     bpy.context.scene.fmri_clustering_threshold = val_threshold = fMRIPanel.clusters_labels[key]['threshold']
    # else:
    #     bpy.context.scene.fmri_clustering_threshold = val_threshold = 2
    # bpy.context.scene.fmri_cluster_val_threshold = bpy.context.scene.fmri_clustering_threshold
    fMRIPanel.clusters_labels_filtered = filter_clusters(clusters_labels_file, val_threshold, size_threshold, clusters_name)

    if bpy.context.scene.fmri_only_clusters_with_electrodes:
        fMRIPanel.clusters_labels_filtered = [c for c in fMRIPanel.clusters_labels_filtered if
                                               len(find_electrodes_in_cluster(c)) > 0]

    if bpy.context.scene.fmri_how_to_sort == 'name':
        clusters_tup = sorted([('', cluster_name(x)) for x in fMRIPanel.clusters_labels_filtered])[::-1]
    else:
        sort_field = 'max' if bpy.context.scene.fmri_how_to_sort == 'tval' else 'size'
        clusters_tup = sorted([(abs(x[sort_field]), cluster_name(x)) for x in fMRIPanel.clusters_labels_filtered])[::-1]
    fMRIPanel.clusters = [x_name for x_size, x_name in clusters_tup]
    clusters_num = {clus:1 for clus in set(fMRIPanel.clusters)}
    cnt = Counter(fMRIPanel.clusters)
    for ind, name in enumerate(fMRIPanel.clusters):
        if cnt[fMRIPanel.clusters[ind]] > 1:
            num = clusters_num[name]
            clusters_num[name] += 1
            new_name = '{}~{}'.format(name, num)
            fMRIPanel.clusters[ind] = new_name
            fMRIPanel.lookup[key][new_name] = fMRIPanel.lookup[key][name]

    # fMRIPanel.clusters.sort(key=mu.natural_keys)
    clusters_items = [(c, c, '', ind + 1) for ind, c in enumerate(fMRIPanel.clusters)]
    bpy.types.Scene.fmri_clusters = bpy.props.EnumProperty(
        items=clusters_items, update=clusters_update, description='Displays a list of clusters. The list can be sorted '
        'and refined by the parameters below.\nEach cluster can be chosen to show detailed information below.\n\nSelected cluster')
    if len(fMRIPanel.clusters) > 0:
        bpy.context.scene.fmri_clusters = fMRIPanel.current_cluster = fMRIPanel.clusters[0]
        if bpy.context.scene.fmri_clusters in fMRIPanel.lookup[key]:
            fMRIPanel.cluster_labels = fMRIPanel.lookup[key][bpy.context.scene.fmri_clusters]
    if bpy.data.objects.get('Deep_electrodes') is not None:
        find_electrodes_close_to_cluster()


def unfilter_clusters():
    update_clusters(2, 1)


def fmri_electrodes_intersection():
    electrodes_in_clusters = {}
    for cluster in fMRIPanel.clusters_labels_filtered:
        electrodes_in_cluster = find_electrodes_in_cluster(cluster)
        if len(electrodes_in_cluster) > 0:
            electrodes_in_clusters['{}_{:.2f}'.format(cluster.name, cluster.max)] = electrodes_in_cluster
    print(electrodes_in_clusters)


@mu.tryit()
def find_electrodes_close_to_cluster():
    electrodes_pos = _addon().electrodes.get_electrodes_pos()
    electrodes_names = _addon().electrodes.get_electrodes_names()
    electrodes = _addon().electrodes.get_electrodes_names()
    if len(electrodes) == 0:
        return
    cluster = fMRIPanel.cluster_labels
    if len(cluster) == 0:
        return
    dists = cdist(cluster.coordinates * 0.1, electrodes_pos)
    closest_elec_ind = np.argmin(dists, axis=1)[0]
    closest_elec_dist = np.min(dists, axis=1)[0]
    closest_elec_name = electrodes_names[closest_elec_ind]
    print((closest_elec_name, closest_elec_dist))
    # for elc_name in electrodes_names:
    #     bpy.data.objects[elc_name].hide = elc_name != closest_elec_name


def find_electrodes_in_cluster(fmri_cluster=None):
    ela_model = _addon().electrodes.get_ela_model()
    if ela_model is None:
        return []
    electrodes = _addon().electrodes.get_electrodes_names()
    if len(electrodes) == 0:
        return []
    if fmri_cluster is None:
        fmri_cluster = fMRIPanel.cluster_labels
    fmri_cluster_electrodes, fmri_cluster_electrodes_names = [], []
    for fmri_roi_dict in fmri_cluster.intersects:
        fmri_roi, fmri_roi_hemi = mu.get_label_and_hemi_from_fname(fmri_roi_dict['name'])
        verts_intersects_prob = fmri_roi_dict['num'] / fmri_cluster.size
        if verts_intersects_prob < 0.3:
            continue
        for elec_name in electrodes:
            loc = ela_model.get(elec_name, None)
            if loc is None:
                # print('No ela model for {}!'.format(elec_name))
                continue
            elc_pos = _addon().electrodes.get_electrode_pos(elec_name)
            dist = np.min(cdist(fmri_cluster.coordinates * 0.1, [elc_pos]))
            if dist < .5:
                fmri_cluster_electrodes.append((dist, elec_name, loc['cortical_rois'], 0))
                fmri_cluster_electrodes_names.append(elec_name)
                # for elc_roi_full_name, elc_roi_prob in zip(loc['cortical_rois'], loc['cortical_probs']):
                #     if elc_roi_prob < 0.3:
                #         continue
                #     elc_roi, elc_roi_hemi = mu.get_label_and_hemi_from_fname(elc_roi_full_name)
                #     if elc_roi == fmri_roi and elc_roi_hemi == fmri_roi_hemi:
                #         fmri_cluster_electrodes.append((
                #             dist, elec_name, loc['cortical_rois'], elc_roi_prob * verts_intersects_prob))
                #         fmri_cluster_electrodes_names.append(elec_name)
                #         break
    if len(fmri_cluster_electrodes) == 0:
        fMRIPanel.electrodes_in_cluster = []
        return []

    # probs_sum = sum([p for _, _, _, p in fmri_cluster_electrodes])
    # fmri_cluster_electrodes = [(dist, name, rois, p / probs_sum) for dist, name, rois, p in fmri_cluster_electrodes]
    fmri_cluster_electrodes = sorted(fmri_cluster_electrodes)#[::-1]
    # best_electrode_name = fmri_cluster_electrodes[0][1]
    # _addon().object_coloring(bpy.data.objects[best_electrode_name], (0, 1, 0))  # cu.name_to_rgb('green'))
    # for elc_name in electrodes:
    #     bpy.data.objects[elc_name].hide = elc_name not in fmri_cluster_electrodes_names

    # print(fmri_cluster_electrodes)
    fMRIPanel.electrodes_in_cluster = fmri_cluster_electrodes
    _show_only_electrodes_near_cluster_update()
    return fmri_cluster_electrodes


def plot_all_blobs(use_abs=None):
    # fMRIPanel.dont_show_clusters_info = False
    faces_verts = _addon().get_faces_verts()
    _addon().init_activity_map_coloring('FMRI')#, subcorticals=False)
    blobs_activity, hemis = calc_blobs_activity(
        fMRIPanel.constrast, fMRIPanel.clusters_labels_filtered, fMRIPanel.colors_in_hemis)
    data_min, colors_ratio = calc_colors_ratio(blobs_activity)
    threshold = bpy.context.scene.fmri_clustering_threshold
    for hemi in hemis:
        inf_hemi = 'inflated_{}'.format(hemi)
        _addon().activity_map_obj_coloring(
            bpy.data.objects[inf_hemi], blobs_activity[hemi], faces_verts[hemi], threshold, True,
            data_min=data_min, colors_ratio=colors_ratio, use_abs=use_abs)
        # if bpy.context.scene.coloring_both_pial_and_inflated:
        #     for inf_hemi in [hemi, 'inflated_{}'.format(hemi)]:
        #         _addon().activity_map_obj_coloring(
        #             bpy.data.objects[inf_hemi], blobs_activity[hemi], faces_verts[hemi], threshold, True,
        #             data_min=data_min, colors_ratio=colors_ratio)
        # else:
        #     inf_hemi = hemi if _addon().is_pial() else 'inflated_{}'.format(hemi)
        #     _addon().activity_map_obj_coloring(
        #         bpy.data.objects[inf_hemi], blobs_activity[hemi], faces_verts[hemi], threshold, True,
        #         data_min=data_min, colors_ratio=colors_ratio)
    for hemi in set(mu.HEMIS) - hemis:
        _addon().clear_cortex([hemi])
    fMRIPanel.blobs_plotted = True


def calc_blobs_activity(constrast, clusters_labels_filtered, colors_in_hemis={}):
    fmri_contrast, blobs_activity = {}, {}
    for hemi in mu.HEMIS:
        fmri_contrast[hemi] = constrast[hemi]
        blobs_activity[hemi] = np.zeros(fmri_contrast[hemi].shape)
    hemis = set()
    for cluster_labels in clusters_labels_filtered:
        if bpy.context.scene.fmri_what_to_plot == 'blob':
            blob_vertices = cluster_labels['vertices']
            hemi = cluster_labels['hemi']
            hemis.add(hemi)
            inf_hemi = hemi if _addon().is_pial() else 'inflated_{}'.format(hemi)
            #todo: check if colors_in_hemis should be initialized (I guess it should be...)
            colors_in_hemis[inf_hemi] = True
            blobs_activity[hemi][blob_vertices] = fmri_contrast[hemi][blob_vertices]
    return blobs_activity, hemis


def calc_colors_ratio(activity):
    if _addon().colorbar_values_are_locked():
        data_max, data_min = _addon().get_colorbar_max_min()
    else:
        data_max, data_min = get_activity_max_min(activity)
        if data_max == 0 and data_min == 0:
            bpy.context.scene.fmri_blobs_percentile_min, bpy.context.scene.fmri_blobs_percentile_max = 0, 100
            data_max, data_min = get_activity_max_min(activity)
            if data_max == 0 and data_min == 0:
                print('Both data max and min are zeros!')
                return 0, 0
        _addon().set_colorbar_max_min(data_max, data_min)
        _addon().set_colorbar_title('fMRI')
    colors_ratio = 256 / (data_max - data_min)
    return data_min, colors_ratio


def get_activity_max_min(activity):
    norm_percs = (bpy.context.scene.fmri_blobs_percentile_min, bpy.context.scene.fmri_blobs_percentile_max)
    data_max, data_min = mu.get_data_max_min(
        activity, bpy.context.scene.fmri_blobs_norm_by_percentile, norm_percs=norm_percs, data_per_hemi=True,
        symmetric=True)
    return data_max, data_min


def cluster_name(x):
    return _cluster_name(x, bpy.context.scene.fmri_how_to_sort)


def _cluster_name(x, sort_mode):
    if sort_mode == 'tval' or sort_mode == 'name':
        return '{}_{:.2f}'.format(x['name'], x['max'])
    elif sort_mode == 'size':
        return '{}_{:.2f}'.format(x['name'], x['size'])


def get_clusters_files(user_fol=''):
    clusters_labels_files = glob.glob(op.join(user_fol, 'fmri', 'clusters_labels_*.pkl'))
    files_names = [mu.namebase(fname)[len('clusters_labels_'):] for fname in clusters_labels_files]
    clusters_labels_items = [(c, c, '', ind) for ind, c in enumerate(list(set(files_names)))]
    return files_names, clusters_labels_files, clusters_labels_items


def support_old_verions(clusters_labels):
    # support old versions
    if not isinstance(clusters_labels, dict):
        data = clusters_labels
        new_clusters_labels = dict(values=data, threshold=2)
    else:
        new_clusters_labels = clusters_labels
    if not 'size' in new_clusters_labels['values'][0]:
        for cluster_labels in new_clusters_labels['values']:
            if not 'size' in cluster_labels:
                cluster_labels['size'] = len(cluster_labels['vertices'])
    return new_clusters_labels


def find_fmri_files_min_max():
    _addon().lock_colorbar_values()
    abs_values = []
    for constrast_name in fMRIPanel.clusters_labels_file_names:
        constrast = {}
        constrasts_found = True
        for hemi in mu.HEMIS:
            contrast_fname = op.join(mu.get_user_fol(), 'fmri', 'fmri_{}_{}.npy'.format(constrast_name, hemi))
            if not op.isfile(contrast_fname):
                # Remove the atlas from the contrast name
                new_constrast_name = '_'.join(constrast_name.split[:-1])
                contrast_fname = op.join(mu.get_user_fol(), 'fmri', 'fmri_{}_{}.npy'.format(new_constrast_name, hemi))
            if not op.isfile(contrast_fname):
                constrasts_found = False
                print("Can't find find_fmri_files_min_max for constrast_name!")
            constrast[hemi] = np.load(contrast_fname)
        if constrasts_found:
            clusters_labels_filtered = filter_clusters(constrast_name)
            blobs_activity, _ = calc_blobs_activity(constrast, clusters_labels_filtered)
            data_max, data_min = get_activity_max_min(blobs_activity)
            abs_values.extend([abs(data_max), abs(data_min)])
    data_max = max(abs_values)
    _addon().set_colorbar_max_min(data_max, -data_max)
    cm_name = _addon().get_colormap()
    output_fname = op.join(mu.get_user_fol(), 'fmri', 'fmri_files_minmax_cm.pkl')
    mu.save((data_min, data_max, cm_name), output_fname)


def export_clusters():
    with open(op.join(mu.get_user_fol(), 'fmri', 'clusters_list.txt'), 'w') as text_file:
        for cluster_name in fMRIPanel.clusters:
            print(cluster_name, file=text_file)


def filter_clusters(constrast_name, val_threshold=None, size_threshold=None, clusters_name=None):
    if val_threshold is None:
        val_threshold = bpy.context.scene.fmri_cluster_val_threshold
    if size_threshold is None:
        size_threshold = bpy.context.scene.fmri_cluster_size_threshold
    if clusters_name is None:
        clusters_name = bpy.context.scene.fmri_clustering_filter
    # key = '{}_{}'.format(constrast_name, bpy.context.scene.fmri_clusters_labels_parcs)
    key = constrast_name
    hemis = ['rh', 'lh']
    if bpy.context.scene.fmri_clustering_filter_rh and not bpy.context.scene.fmri_clustering_filter_lh:
        hemis = ['rh']
    elif not bpy.context.scene.fmri_clustering_filter_rh and bpy.context.scene.fmri_clustering_filter_lh:
        hemis = ['lh']
    elif not bpy.context.scene.fmri_clustering_filter_rh and not bpy.context.scene.fmri_clustering_filter_lh:
        hemis = []
    return [c for c in fMRIPanel.clusters_labels[key]['values']
            if abs(c['max']) >= val_threshold and len(c['vertices']) >= size_threshold and
            c['name'].startswith(clusters_name) and c['hemi'] in hemis]


def load_fmri_volume(nii_fname):
    import importlib
    mu.add_mmvt_code_root_to_path()
    from src.preproc import fMRI
    importlib.reload(fMRI)
    fmri_file_template = mu.namebase(nii_fname)
    subject = mu.get_user()
    flag, fmri_contrast_file_template = fMRI.project_volume_to_surface(
        subject, fmri_file_template, remote_fmri_dir=mu.get_parent_fol(nii_fname))
    if not flag:
        print('load_fmri_volume: Error in fMRI.project_volume_to_surface!')
        return False
    flag = fMRI.calc_fmri_min_max(subject, fmri_contrast_file_template)
    if not flag:
        print('load_fmri_volume: Error in fMRI.calc_fmri_min_max!')
        return False
    # _addon().coloring.init(_addon(), register=False)
    fMRI_file_name = fmri_contrast_file_template.replace('fmri_', '')
    _addon().coloring.plot_fmri_file(fMRI_file_name)
    return True


def fMRI_draw(self, context):
    layout = self.layout
    # user_fol = mu.get_user_fol()
    # clusters_labels_files = glob.glob(op.join(user_fol, 'fmri', 'clusters_labels_*.npy'))
    # if len(clusters_labels_files) > 1:
    col = layout.box().column()
    col.prop(context.scene, 'fmri_clustering_threshold', text='Threshold')
    col.prop(context.scene, 'fmri_files', text='')
    col.prop(context.scene, 'subject_annot_files', text='')
    col.operator(CalcClusters.bl_idname, text="Find clusters", icon='GROUP_VERTEX')
    if not fMRIPanel.fMRI_clusters_files_exist and _addon().coloring.fMRI_constrasts_exist() > 0:
        return
    layout.prop(context.scene, 'fmri_clusters_labels_files', text='')
    if len(fMRIPanel.clusters_labels_files) > 1:
        layout.prop(context.scene, 'fmri_clusters_labels_parcs', text='')
    row = layout.row(align=True)
    row.operator(PrevCluster.bl_idname, text="", icon='PREV_KEYFRAME')
    row.prop(context.scene, 'fmri_clusters', text="")
    row.operator(NextCluster.bl_idname, text="", icon='NEXT_KEYFRAME')
    row = layout.row(align=True)
    row.label(text='Sort: ')
    row.prop(context.scene, 'fmri_how_to_sort', expand=True)

    if not fMRIPanel.cluster_labels is None and len(fMRIPanel.cluster_labels) > 0 and \
            not fMRIPanel.dont_show_clusters_info:
        if 'size' not in fMRIPanel.cluster_labels:
            fMRIPanel.cluster_labels['size'] = len(fMRIPanel.cluster_labels['vertices'])
        blob_size = fMRIPanel.cluster_labels['size']
        col = layout.box().column()
        mu.add_box_line(col, 'Max val', '{:.2f}'.format(fMRIPanel.cluster_labels['max']), 0.7)
        mu.add_box_line(col, 'Size', str(blob_size), 0.7)
        col = layout.box().column()
        labels_num_to_show = min(7, len(fMRIPanel.cluster_labels['intersects']))
        for inter_labels in fMRIPanel.cluster_labels['intersects'][:labels_num_to_show]:
            mu.add_box_line(col, inter_labels['name'], '{:.0%}'.format(inter_labels['num'] / float(blob_size)), 0.8)
        if labels_num_to_show < len(fMRIPanel.cluster_labels['intersects']):
            col.label(text='Out of {} labels'.format(len(fMRIPanel.cluster_labels['intersects'])))

        if len(fMRIPanel.electrodes_in_cluster) > 0:
            box = layout.box()
            box.label(text='Electrodes close to cluster:')
            col = box.box().column()
            for dist, elec_name, elc_rois, elec_prob in fMRIPanel.electrodes_in_cluster:
                 # if elec_prob >= 0.01:
                mu.add_box_line(col, elec_name, '{:.2f}'.format(dist), 0.8)#_# '{:.2f}'.format(elec_prob), 0.8) ','.join(elc_rois)
            box.prop(context.scene, 'show_only_electrodes_near_cluster', text='Show only those electrdes')

    # row.prop(context.scene, 'fmri_clustering_threshold', text='Threshold')
    # row.operator(CalcClusters.bl_idname, text="Recalculate clusters", icon='GROUP_VERTEX')
    layout.prop(context.scene, 'fmri_show_filtering', text='Refine clusters')
    if bpy.context.scene.fmri_show_filtering:
        # row.operator(RefinefMRIClusters.bl_idname, text="Find clusters", icon='GROUP_VERTEX')
        col = layout.box().column()
        col.prop(context.scene, 'fmri_cluster_val_threshold', text='clusters t-val threshold')
        col.prop(context.scene, 'fmri_cluster_size_threshold', text='clusters size threshold')
        col.prop(context.scene, 'fmri_clustering_filter', text='starts with')
        row = col.row(align=True)
        row.prop(context.scene, 'fmri_clustering_filter_lh', text='Left hemisphere')
        row.prop(context.scene, 'fmri_clustering_filter_rh', text='Right hemisphere')
        # if len(fMRIPanel.electrodes_in_cluster) > 0:
        col.prop(context.scene, 'fmri_only_clusters_with_electrodes', text='Only with electrodes')
        # layout.operator(FilterfMRIBlobs.bl_idname, text="Filter blobs", icon='FILTER')
    # layout.prop(context.scene, 'plot_current_cluster', text="Plot current cluster")
    if bpy.context.scene.fmri_more_settings:
        row = layout.row(align=True)
        row.prop(context.scene, 'plot_fmri_cluster_contours', text="Plot cluster contours")
        row.prop(context.scene, 'fmri_cluster_contours_color', text="")
        layout.prop(context.scene, 'plot_fmri_cluster_per_click', text="Listen to left clicks")
        layout.prop(context.scene, 'fmri_rotate_view_to_vertice', text='Rotate on update')

    # layout.prop(context.scene, 'fmri_what_to_plot', expand=True)
    # row = layout.row(align=True)
    layout.operator(PlotAllBlobs.bl_idname, text="Plot all blobs", icon='POTATO')
    # if _addon().is_pial(): # or _addon().get_inflated_ratio() == 1:
    layout.operator(NearestCluster.bl_idname, text="Nearest cluster", icon='MOD_SKIN')
    # layout.prop(context.scene, 'search_closest_cluster_only_in_filtered', text="Seach only in filtered blobs")
    # layout.operator(LoadMEGData.bl_idname, text="Save as functional ROIs", icon='IPO')
    if bpy.context.scene.fmri_more_settings:
        layout.prop(context.scene, 'fmri_blobs_norm_by_percentile', text="Norm by percentiles")
        if bpy.context.scene.fmri_blobs_norm_by_percentile:
            row = layout.row(align=True)
            row.prop(context.scene, 'fmri_blobs_percentile_min', text="Percentile min")
            row.prop(context.scene, 'fmri_blobs_percentile_max', text="Percentile max")
    # layout.operator(FindfMRIFilesMinMax.bl_idname, text="Calc minmax for all files", icon='IPO')
    if mu.is_freesurfer_exist and bpy.context.scene.fmri_more_settings:
        layout.operator(LoadVolumefMRIFile.bl_idname, text="Load volume fMRI file", icon='LOAD_FACTORY').filepath = \
            op.join(mu.get_user_fol(), 'fmri', '*.*')
    layout.operator(fmriExportClusters.bl_idname, text="Export clusters", icon='ASSET_MANAGER')
    layout.operator(fmriClearColors.bl_idname, text="Clear", icon='PANEL_CLOSE')
    layout.prop(context.scene, 'fmri_more_settings', text='More settings')


def clear():
    _addon().clear_cortex()
    _addon().clear_subcortical_fmri_activity()
    fMRIPanel.blobs_plotted = False
    fMRIPanel.dont_show_clusters_info = False


class LoadVolumefMRIFile(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "mmvt.load_fmri_volume"
    bl_label = "load_fmri_volume"

    filename_ext = '.*'
    filter_glob = bpy.props.StringProperty(default='*.*', options={'HIDDEN'}, maxlen=255)

    def execute(self, context):
        load_fmri_volume(self.filepath)
        return {'FINISHED'}


class FindfMRIFilesMinMax(bpy.types.Operator):
    bl_idname = "mmvt.find_fmri_files_min_max"
    bl_label = "mmvt find_fmri_files_min_max"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        find_fmri_files_min_max()
        return {"FINISHED"}


class fmriExportClusters(bpy.types.Operator):
    bl_idname = "mmvt.fmri_export_clusters"
    bl_label = "mmvt fmri_export_clusters"
    bl_description = 'Export clusters\n\nScript: mmvt.fMRI.export_clusters()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        export_clusters()
        return {"FINISHED"}


class fmriClearColors(bpy.types.Operator):
    bl_idname = "mmvt.fmri_colors_clear"
    bl_label = "mmvt fmri colors clear"
    bl_description = 'Clears all the plotted clusters\n\nScript: mmvt.fMRI.clear()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        clear()
        return {"FINISHED"}


class LoadMEGData(bpy.types.Operator):
    bl_idname = "mmvt.load_meg_data"
    bl_label = "Load MEG"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):

        return {'PASS_THROUGH'}


class RefinefMRIClusters(bpy.types.Operator):
    bl_idname = "mmvt.refine_fmri_clusters"
    bl_label = "Calc clusters"
    bl_options = {"UNDO"}
    in_q, out_q = None, None
    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not self.out_q is None:
                try:
                    fMRI_preproc = self.out_q.get(block=False)
                    print('fMRI_preproc: {}'.format(fMRI_preproc))
                except Empty:
                    pass
        return {'PASS_THROUGH'}

    def invoke(self, context, event=None):
        subject = mu.get_user()
        threshold = bpy.context.scene.fmri_clustering_threshold
        contrast = bpy.context.scene.fmri_clusters_labels_files
        atlas = bpy.context.scene.atlas
        task = contrast.split('_')[0]
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        mu.change_fol_to_mmvt_root()
        cmd = '{} -m src.preproc.fMRI_preproc -s {} -T {} -c {} -t {} -a {} -f find_clusters --ignore_missing 1'.format(
            bpy.context.scene.python_cmd, subject, task, contrast, threshold, atlas)
        print('Running {}'.format(cmd))
        self.in_q, self.out_q = mu.run_command_in_new_thread(cmd)
        return {'RUNNING_MODAL'}


class NearestCluster(bpy.types.Operator):
    bl_idname = "mmvt.nearest_cluster"
    bl_label = "Nearest Cluster"
    bl_description = 'Finds the closest cluster to the cursor.\n\nScript: mmvt.fMRI.find_closest_cluster()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        find_closest_cluster()
        return {'PASS_THROUGH'}


class PlotAllBlobs(bpy.types.Operator):
    bl_idname = "mmvt.plot_all_blobs"
    bl_label = "Plot all blobs"
    bl_description = 'Plots all the clusters in the list.\n\nScript: mmvt.fMRI.plot_all_blobs()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        plot_all_blobs()
        return {'PASS_THROUGH'}


class FilterfMRIBlobs(bpy.types.Operator):
    bl_idname = "mmvt.filter_fmri_blobs"
    bl_label = "Filter fMRI blobs"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        update_clusters()
        return {'PASS_THROUGH'}

try:
    bpy.types.Scene.plot_current_cluster = bpy.props.BoolProperty(
        default=True, description="Plot current cluster")
    bpy.types.Scene.plot_fmri_cluster_per_click = bpy.props.BoolProperty(
        default=False, description='Finds and selects the closest cluster to the cursor each time left mouse clicked')
    bpy.types.Scene.search_closest_cluster_only_in_filtered = bpy.props.BoolProperty(
        default=False, description="Plot current cluster")
    bpy.types.Scene.fmri_what_to_plot = bpy.props.EnumProperty(
        items=[('blob', 'Plot blob', '', 1)], description='What do plot') # ('cluster', 'Plot cluster', '', 1)
    bpy.types.Scene.fmri_how_to_sort = bpy.props.EnumProperty(
        items=[('tval', 't-val', '', 1), ('size', 'size', '', 2), ('name', 'name', '', 3)],
        update=fmri_how_to_sort_update, description='Sorts the clusters list by t-value, size or name.\n\nCurrent sorting')
    bpy.types.Scene.fmri_clusters = bpy.props.EnumProperty(items=[],
        description='Displays a list of clusters. The list can be sorted and refined by the parameters below. '
                    'Each cluster can be chosen to show detailed information below.\n\nSelected cluster')
    bpy.types.Scene.fmri_cluster_val_threshold = bpy.props.FloatProperty(default=2,
        min=0, max=20, update=fmri_clusters_update, description='Sets the threshold for the t-value to sort the clusters list')
    bpy.types.Scene.fmri_cluster_size_threshold = bpy.props.FloatProperty(default=50,
        min=1, max=2000, update=fmri_clusters_update, description='Sets the threshold for the size to sort the clusters list')
    bpy.types.Scene.fmri_clustering_threshold = bpy.props.FloatProperty(default=2,
        description='clustering threshold', min=0, max=20)
    bpy.types.Scene.fmri_clusters_labels_files = bpy.props.EnumProperty(
        items=[], update=fmri_clusters_labels_files_update,
        description='Selects the contrast for the cluster analysis.\n\nCurrent contrast')
    bpy.types.Scene.fmri_clusters_labels_parcs = bpy.props.EnumProperty(
        items=[], description="fMRI parcs")
    bpy.types.Scene.fmri_blobs_norm_by_percentile = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.fmri_blobs_percentile_min = bpy.props.FloatProperty(
        default=1, min=0, max=100, update=fmri_blobs_percentile_min_update)
    bpy.types.Scene.fmri_blobs_percentile_max = bpy.props.FloatProperty(
        default=99, min=0, max=100, update=fmri_blobs_percentile_max_update)
    bpy.types.Scene.fmri_show_filtering = bpy.props.BoolProperty(default=False,
        description='Opens further options to refine the clusters list')
    bpy.types.Scene.plot_fmri_cluster_contours = bpy.props.BoolProperty(default=False,
        description='Plots the label contours of the selected clusters')
    bpy.types.Scene.fmri_cluster_contours_color = bpy.props.FloatVectorProperty(
        name="contours_color", subtype='COLOR', default=(1, 0, 0), min=0.0, max=1.0,
        description='Sets the color to plot the labels contours')
    bpy.types.Scene.fmri_clustering_filter = bpy.props.StringProperty(update=fmri_clusters_update,
        description='Finds clusters by name or the few first letters that their name starts with')
    bpy.types.Scene.fmri_clustering_filter_lh = bpy.props.BoolProperty(default=True, update=fmri_clusters_update,
        description='Shows only the clusters in the list from the left hemisphere')
    bpy.types.Scene.fmri_clustering_filter_rh = bpy.props.BoolProperty(default=True, update=fmri_clusters_update,
        description='Shows only the clusters in the list from the right hemisphere')
    bpy.types.Scene.fmri_only_clusters_with_electrodes = bpy.props.BoolProperty(
        default=False, update=fmri_clusters_update, description='Shows only clusters with electrodes')
    bpy.types.Scene.fmri_more_settings = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_only_electrodes_near_cluster = bpy.props.BoolProperty(
        default=False, update=show_only_electrodes_near_cluster_update)
    bpy.types.Scene.fmri_rotate_view_to_vertice = bpy.props.BoolProperty(
        default=True, description='Rotate the brain for best view')
except:
    pass


class fMRIPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "fMRI"
    addon = None
    python_bin = 'python'
    init = False
    clusters_labels = None
    cluster_labels = None
    clusters = []
    clusters_labels_filtered = []
    electrodes_in_cluster = []
    colors_in_hemis = {'rh':False, 'lh':False}
    blobs_activity = None
    blobs_plotted = False
    fMRI_clusters_files_exist = False
    constrast = {'rh':None, 'lh':None}
    clusters_labels_file_names = []
    clusters_labels_files = []
    update = True

    @classmethod
    def poll(cls, context):
        return True # Hide when False

    def draw(self, context):
        if fMRIPanel.init:
            fMRI_draw(self, context)

@mu.tryit()
def init(addon):
    user_fol = mu.get_user_fol()
    # clusters_labels_files = glob.glob(op.join(user_fol, 'fmri', 'clusters_labels_*.pkl'))
    # old code was saving those files as npy instead of pkl
    # clusters_labels_files.extend(glob.glob(op.join(user_fol, 'fmri', 'clusters_labels_*.npy')))
    # fmri_blobs = glob.glob(op.join(user_fol, 'fmri', 'blobs_*_rh.npy'))
    fMRIPanel.addon = addon
    fMRIPanel.lookup, fMRIPanel.clusters_labels = {}, {}
    fMRIPanel.cluster_labels = {}
    files_names, clusters_labels_files, clusters_labels_items = get_clusters_files(user_fol)
    fMRIPanel.fMRI_clusters_files_exist = len(files_names) > 0 # and len(fmri_blobs) > 0
    if not fMRIPanel.fMRI_clusters_files_exist:
        register()
        fMRIPanel.init = True
        return
    # files_names = [mu.namebase(fname)[len('clusters_labels_'):] for fname in clusters_labels_files]
    fMRIPanel.clusters_labels_file_names = files_names
    bpy.types.Scene.fmri_clusters_labels_files = bpy.props.EnumProperty(
        items=clusters_labels_items, update=fmri_clusters_labels_files_update,
        description='Selects the contrast for the cluster analysis.\n\nCurrent contrast')
    bpy.context.scene.fmri_clusters_labels_files = files_names[0]
    bpy.context.scene.fmri_blobs_norm_by_percentile = True
    bpy.context.scene.plot_fmri_cluster_contours = False
    bpy.context.scene.fmri_only_clusters_with_electrodes = False
    bpy.context.scene.fmri_rotate_view_to_vertice = True

    for file_name, clusters_labels_file in zip(files_names, clusters_labels_files):
        # Check if the constrast files exist
        if all([get_contrast_fname(file_name, hemi) != '' for hemi in mu.HEMIS]):
            key = file_name
            fMRIPanel.clusters_labels[key] = c = mu.Bag(mu.load(clusters_labels_file))
            for ind in range(len(c.values)):
                c.values[ind] = mu.Bag(c.values[ind])

            fMRIPanel.lookup[key] = create_lookup_table(fMRIPanel.clusters_labels[key])

    # bpy.context.scene.fmri_cluster_val_threshold = 2
    # bpy.context.scene.fmri_cluster_size_threshold = 20
    bpy.context.scene.search_closest_cluster_only_in_filtered = True
    bpy.context.scene.fmri_what_to_plot = 'blob'
    bpy.context.scene.fmri_how_to_sort = 'tval'
    bpy.context.scene.plot_current_cluster = True
    bpy.context.scene.fmri_more_settings = False
    bpy.context.scene.show_only_electrodes_near_cluster = False

    update_clusters()
    fMRIPanel.blobs_activity, _ = calc_blobs_activity(
        fMRIPanel.constrast, fMRIPanel.clusters_labels_filtered, fMRIPanel.colors_in_hemis)
    bpy.context.scene.plot_fmri_cluster_per_click = False
    fMRIPanel.dont_show_clusters_info = False
    # addon.clear_cortex()
    # fmri_electrodes_intersection()
    register()
    fMRIPanel.init = True
    # print('fMRI panel initialization completed successfully!')


def create_lookup_table(clusters_labels):
    lookup = {}
    values = clusters_labels['values'] if 'values' in clusters_labels else clusters_labels
    for cluster_label in values:
        lookup[_cluster_name(cluster_label, 'tval')] = cluster_label
        lookup[_cluster_name(cluster_label, 'size')] = cluster_label
    return lookup


def register():
    try:
        unregister()
        bpy.utils.register_class(fMRIPanel)
        bpy.utils.register_class(CalcClusters)
        bpy.utils.register_class(NextCluster)
        bpy.utils.register_class(PrevCluster)
        bpy.utils.register_class(NearestCluster)
        bpy.utils.register_class(FilterfMRIBlobs)
        bpy.utils.register_class(PlotAllBlobs)
        bpy.utils.register_class(RefinefMRIClusters)
        bpy.utils.register_class(LoadMEGData)
        bpy.utils.register_class(FindfMRIFilesMinMax)
        bpy.utils.register_class(fmriExportClusters)
        bpy.utils.register_class(fmriClearColors)
        bpy.utils.register_class(LoadVolumefMRIFile)
        # print('fMRI Panel was registered!')
    except:
        print("Can't register fMRI Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(fMRIPanel)
        bpy.utils.unregister_class(CalcClusters)
        bpy.utils.unregister_class(NextCluster)
        bpy.utils.unregister_class(PrevCluster)
        bpy.utils.unregister_class(NearestCluster)
        bpy.utils.unregister_class(FilterfMRIBlobs)
        bpy.utils.unregister_class(PlotAllBlobs)
        bpy.utils.unregister_class(RefinefMRIClusters)
        bpy.utils.unregister_class(LoadMEGData)
        bpy.utils.unregister_class(FindfMRIFilesMinMax)
        bpy.utils.unregister_class(fmriExportClusters)
        bpy.utils.unregister_class(fmriClearColors)
        bpy.utils.unregister_class(LoadVolumefMRIFile)
    except:
        pass
        # print("Can't unregister fMRI Panel!")
