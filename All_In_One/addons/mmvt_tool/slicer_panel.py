import bpy
import os.path as op
import mmvt_utils as mu
import traceback
import glob


CUT_AXIAL = 'axial'
CUT_CORONAL = 'coronal'
CUT_SAGITAL = 'sagital'
CUTS = [CUT_AXIAL, CUT_CORONAL, CUT_SAGITAL]


def _addon():
    return SlicerPanel.addon


def slices_modality_update(self, context):
    _addon().set_slicer_state(bpy.context.scene.slices_modality)
    bpy.context.scene.slices_modality_mix = 1
    if bpy.context.scene.slices_modality == 'mri':
        _addon().set_t1_value()
    elif bpy.context.scene.slices_modality == 'ct':
        _addon().set_ct_intensity()
    elif bpy.context.scene.slices_modality == 't2':
        _addon().set_t2_value()
    # elif bpy.context.scene.slices_modality == 't1_ct':
    #     _addon().set_t1_ct_value()
    if _addon().get_slicer_state(bpy.context.scene.slices_modality) is not None:
        clim = (bpy.context.scene.slices_x_min, bpy.context.scene.slices_x_max)
        _addon().create_slices(
            modality=bpy.context.scene.slices_modality, zoom_around_voxel=bpy.context.scene.slices_zoom_around_voxel,
            zoom_voxels_num=bpy.context.scene.slices_zoom_voxels_num, smooth=bpy.context.scene.slices_zoom_interpolate,
            clim=clim, plot_cross=bpy.context.scene.slices_plot_cross, mark_voxel=bpy.context.scene.slices_mark_voxel)
    slicer_state = _addon().get_slicer_state(bpy.context.scene.slices_modality)
    bpy.context.scene.slices_x_min, bpy.context.scene.slices_x_max = slicer_state.clim

    slices_zoom()


def slices_update(self, context):
    if not SlicerPanel.init:
        return
    clim = (bpy.context.scene.slices_x_min, bpy.context.scene.slices_x_max)
    if _addon().get_slicer_state(bpy.context.scene.slices_modality) is not None:
        _addon().create_slices(
            modality=bpy.context.scene.slices_modality, zoom_around_voxel=bpy.context.scene.slices_zoom_around_voxel,
            zoom_voxels_num=bpy.context.scene.slices_zoom_voxels_num, smooth=bpy.context.scene.slices_zoom_interpolate,
            clim=clim, plot_cross=bpy.context.scene.slices_plot_cross, mark_voxel=bpy.context.scene.slices_mark_voxel)


def set_slices_plot_cross(val):
    bpy.context.scene.slices_plot_cross = val


def get_perspectives():
    return ['sagital', 'coronal', 'axial']


def get_slices_names(ind=None):
    slices_name_type = set([mu.file_type(img.name) for img in bpy.data.images if img.name != 'Render Result'])
    if len(slices_name_type) > 1:
        print('get_slices_names: different images types! {}'.format(slices_name_type))
        return []
    slice_file_type = list(slices_name_type)[0]
    return ['{}{}.{}'.format(pres, '_{}'.format(ind) if ind is not None else '',
                             slice_file_type) for pres in get_perspectives()]


def get_slices_modality():
    return bpy.context.scene.slices_modality


def ct_exist():
    return SlicerPanel.ct_exist


def slices_modality_mix_update(self, context):
    pass


def slices_zoom_update(self, context):
    slices_zoom()


def slices_zoom():
    # Really slow
    for area, region in mu.get_images_area_regions():
        override = bpy.context.copy()
        override['area'] = area
        override['region'] = region
        # override['region_data'].view_distance = bpy.context.scene.slices_zoom
        bpy.ops.image.view_zoom_ratio(override, ratio=bpy.context.scene.slices_zoom)


def create_new_electrode(elc_name):
    electrode_size = bpy.context.scene.electrodes_radius
    parent_name = _addon().electrodes_panel_parent
    mu.create_empty_if_doesnt_exists(parent_name, _addon().BRAIN_EMPTY_LAYER, root_fol=parent_name)
    layers_array = [False] * 20
    layers_array[_addon().ELECTRODES_LAYER] = True
    x, y, z = bpy.context.scene.cursor_location
    if not bpy.data.objects.get(elc_name) is None:
        elc_obj = bpy.data.objects[elc_name]
        elc_obj.location = [x, y, z]
    else:
        print('creating {}: {}'.format(elc_name, (x, y, z)))
        mu.create_sphere((x, y, z), electrode_size, layers_array, elc_name)
        cur_obj = bpy.data.objects[elc_name]
        cur_obj.select = True
        cur_obj.parent = bpy.data.objects[parent_name]
        mu.create_and_set_material(cur_obj)
    _addon().show_hide_electrodes(True)


def find_nearest_electrde_in_ct(max_iters=100):
    from itertools import product
    x, y, z = bpy.context.scene.ct_voxel_x, bpy.context.scene.ct_voxel_y, bpy.context.scene.ct_voxel_z
    ct_data = _addon().get_slicer_state('ct').data
    bpy.context.scene.ct_intensity = ct_data[x, y, z]
    peak_found, iter_num = True, 0
    while peak_found and iter_num < max_iters:
        max_ct_data = ct_data[x, y, z]
        max_diffs = (0, 0, 0)
        for dx, dy, dz in product([-1, 0, 1], [-1, 0, 1], [-1, 0, 1]):
            print(x+dx, y+dy, z+dz, ct_data[x+dx, y+dy, z+dz], max_ct_data)
            if ct_data[x+dx, y+dy, z+dz] > max_ct_data:
                max_ct_data = ct_data[x+dx, y+dy, z+dz]
                max_diffs = (dx, dy, dz)
        peak_found = max_diffs == (0, 0, 0)
        if not peak_found:
            x, y, z = x+max_diffs[0], y+max_diffs[1], z+max_diffs[2]
            print(max_ct_data, x, y, z)
        iter_num += 1
    if not peak_found:
        print('Peak was not found!')
    print(iter_num, max_ct_data, x, y, z)
    bpy.context.scene.ct_voxel_x, bpy.context.scene.ct_voxel_y, bpy.context.scene.ct_voxel_z = x, y, z
    _addon().create_slices_from_vox_coordinates((x, y, z), 'ct')


def export_electrodes():
    import csv
    mu.make_dir(op.join(mu.get_user_fol(), 'electrodes'))
    csv_fname = op.join(mu.get_user_fol(), 'electrodes', '{}_RAS.csv'.format(mu.get_user()))
    electrodes = [e for e in bpy.data.objects[_addon().electrodes_panel_parent].children]
    with open(csv_fname, 'w') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        wr.writerow(['Electrode Name', 'R', 'A', 'S'])
        for elc in electrodes:
            wr.writerow([elc.name, *['{:.2f}'.format(loc * 10) for loc in elc.location]])


def set_slicer_cut_type(cut_type):
    cuts = ['axial', 'coronal', 'sagital']
    if cut_type in cuts:
        bpy.context.scene.slicer_cut_type = cut_type
    else:
        print('Can be one of this values:'.format(','.join(cuts)))


def get_slicer_cut_type():
    return bpy.context.scene.slicer_cut_type


def slice_brain(cut_pos=None, save_image=False, render_image=False):
    coordinate = bpy.context.scene.cursor_location
    cut_type = bpy.context.scene.slicer_cut_type
    create_joint_brain_obj()
    # coordinate = list(D.screens['Default'].areas[3].spaces[0].cursor_location)
    optional_cut_types = ['sagital', 'coronal', 'axial']
    optional_rots = [[1.5708, 0, 1.5708], [1.5708, 0, 3.14], [0, 3.14, 0]]
    option_ind = optional_cut_types.index(cut_type)
    bpy.context.scene.is_sliced_ind = option_ind
    bpy.context.scene.last_cursor_location = coordinate
    if cut_pos is None:
        cut_pos = [0.0, 0.0, 0.0]
        cut_pos[option_ind] = coordinate[option_ind]
    print('slice_brain: cut pos {}'.format(cut_pos))
    # print('rot={}'.format(optional_rots[option_ind]))
    if bpy.data.objects.get('{}_plane'.format(cut_type)) is None:
        bpy.ops.mesh.primitive_plane_add(radius=25.7 / 2.0, location=tuple(cut_pos))
        bpy.context.object.name = '{}_plane'.format(cut_type)
        bpy.context.object.rotation_euler = optional_rots[option_ind]
        # if cut_type == 'axial':import
        #     bpy.ops.object.mode_set(mode='EDIT')
        #     bpy.ops.mesh.flip_normals()
        #     bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.mesh.uv_texture_add()
        try:
            bpy.context.object.active_material = bpy.data.materials['{}_plane_mat'.format(cut_type)]
        except:
            print('can\'t show slice on rendering mode')

    else:
        bpy.data.objects['{}_plane'.format(cut_type)].hide = False
        bpy.data.objects['{}_plane'.format(cut_type)].hide_render = False
    optional_cut_types.remove(cut_type)
    for cut in optional_cut_types:
        if bpy.data.objects.get('{}_plane'.format(cut)):
            bpy.data.objects['{}_plane'.format(cut)].hide = True
            bpy.data.objects['{}_plane'.format(cut)].hide_render = True

    cur_plane_obj = bpy.data.objects['{}_plane'.format(cut_type)]
    cur_plane_obj.location = tuple(cut_pos)
    # images_path = '{}_{}.png'.format(bpy.context.scene.slices_modality, cut_type)
    images_path = '{}.{}'.format(cut_type, _addon().get_figure_format().upper())
    # slice_image_path = glob.glob('{}*{}*'.format(images_path, cut_type))
    try:
        slice_image = bpy.data.images[images_path]
        print(slice_image)
        cur_plane_obj.data.uv_textures['UVMap'].data[0].image = slice_image
        bpy.data.materials['{}_plane_mat'.format(cut_type)].node_tree.nodes['Image Texture'].image = bpy.data.images[
            '{}.JPEG'.format(cut_type)]
    except:
        print(traceback.format_exc())
        print('can\'t show slice on rendering mode')

    if bpy.data.objects.get('masking_cube') is None:
        bpy.ops.mesh.primitive_cube_add(radius=10)
        bpy.context.object.name = 'masking_cube'
    cube_location = [0, 0, 0]
    # if cut_pos[option_ind] > 0 or cut_type in ['axial','coronal']:
    if bpy.context.scene.what_to_cut == '1':
        cube_location[option_ind] = cut_pos[option_ind] + 9.98
        is_coordinate_positive = True
    # elif cut_pos[option_ind] < 0:
    elif bpy.context.scene.what_to_cut == '2':
        cube_location[option_ind] = cut_pos[option_ind] - 9.98
        is_coordinate_positive = False
    bpy.data.objects['masking_cube'].location = tuple(cube_location)
    bpy.data.objects['masking_cube'].hide = True
    bpy.data.objects['masking_cube'].hide_render = True

    for hemi in ['lh', 'rh']:
        inflated_object = mu.get_hemi_obj(hemi)
        # if inflated_object.modifiers.get('mask_for_slice') is None:
        #     inflated_object.modifiers.new('mask_for_slice', type='BOOLEAN')
        # inflated_object.modifiers['mask_for_slice'].object = bpy.data.objects['masking_cube']
        # inflated_object.modifiers['mask_for_slice'].operation = 'DIFFERENCE'
        # inflated_object.modifiers['mask_for_slice'].double_threshold = 0
        mask_object_with_cube(inflated_object)
    try:
        #  TODO  Noam this is where I slice the head object.
        if bpy.context.scene.slice_seghead:
            # if we need to slice the head :
            mask_object_with_cube(bpy.data.objects['seghead'])
        else:
            # else, make sure we don't show the slicing
            bpy.data.objects['seghead'].modifiers['mask_for_slice'].show_viewport = False
            bpy.data.objects['seghead'].modifiers['mask_for_slice'].show_render = False

    except:
        print('outer skin object does not exist.')
    bpy.context.scene.objects.active = cur_plane_obj
    if cur_plane_obj.modifiers.get('Boolean') is None:
        cur_plane_obj.modifiers.new('Boolean', type='BOOLEAN')
        cur_plane_obj.modifiers['Boolean'].object = bpy.data.objects['joint_brain']
        cur_plane_obj.modifiers['Boolean'].operation = 'INTERSECT'
    flip_slice_plane_if_needed(is_coordinate_positive)
    cur_plane_obj.hide_select = True
    if save_image:
        _addon().save_image('slicing', bpy.context.scene.save_selected_view)
    if render_image:
        _addon().render_image(set_to_camera_mode=True)


def mask_object_with_cube(inflated_object):
    if inflated_object.modifiers.get('mask_for_slice') is None:
        inflated_object.modifiers.new('mask_for_slice', type='BOOLEAN')
    inflated_object.modifiers['mask_for_slice'].object = bpy.data.objects['masking_cube']
    inflated_object.modifiers['mask_for_slice'].operation = 'DIFFERENCE'
    inflated_object.modifiers['mask_for_slice'].double_threshold = 0

def flip_slice_plane_if_needed(is_coordinate_positive):
    if bpy.context.active_object.get('is_flipped') is None:
        bpy.context.active_object['is_flipped'] = False
    slice_is_flipped = bpy.context.active_object['is_flipped']
    # print('is_positive =={}'.format(is_coordinate_positive))
    # print('slice_plane_flipped[cut_type] == {}'.format(slice_is_flipped))
    if slice_is_flipped != is_coordinate_positive:
        # print('in check_to_flip_slice_plane, return False')
        return False
    else:
        # print('in check_to_flip_slice_plane, return True')
        bpy.context.active_object['is_flipped'] = not bpy.context.active_object['is_flipped']
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.mode_set(mode='OBJECT')
        return True


def clear_slice():
    optional_cut_types = ['sagital', 'coronal', 'axial']
    bpy.data.objects['masking_cube'].location = (20, 20, 20)
    bpy.context.scene.is_sliced_ind = -1
    for cut_type in optional_cut_types:
        if bpy.data.objects.get('{}_plane'.format(cut_type)):
            bpy.data.objects['{}_plane'.format(cut_type)].hide = True
            bpy.data.objects['{}_plane'.format(cut_type)].hide_render = True
    return True


def create_joint_brain_obj():
    if bpy.data.objects.get('joint_brain') is None:
        bpy.ops.mesh.primitive_cube_add(radius=0.1, location=(500, 500, 500))
        bpy.context.object.name = 'joint_brain'
        for hemi in ['lh', 'rh', 'Brain-Stem', 'Left-Cerebellum-Cortex', 'Right-Cerebellum-Cortex']:
            if hemi not in bpy.data.objects:
                continue
            bpy.ops.object.modifier_add(type='BOOLEAN')
            bpy.data.objects['joint_brain'].modifiers['Boolean'].object = bpy.data.objects[hemi]
            bpy.data.objects['joint_brain'].modifiers['Boolean'].operation = 'UNION'
            bpy.context.scene.objects.active = bpy.data.objects['joint_brain']
            bpy.ops.object.modifier_apply(modifier='Boolean')
        bpy.data.objects['joint_brain'].hide = True
        bpy.data.objects['joint_brain'].hide_render = True

# def get_cm():
#     return ColorbarPanel.cm
#
#
# def colorbar_values_are_locked():
#     return bpy.context.scene.lock_min_max
#
#
# def lock_colorbar_values(val=True):
#     bpy.context.scene.lock_min_max = val
#
#
# def load_colormap():
#     colormap_fname = op.join(mu.file_fol(), 'color_maps', '{}.npy'.format(
#         bpy.context.scene.colorbar_files.replace('-', '_')))
#     colormap = np.load(colormap_fname)
#     ColorbarPanel.cm = colormap
#     for ind in range(colormap.shape[0]):
#         cb_obj_name = 'cb.{0:0>3}'.format(ind)
#         cb_obj = bpy.data.objects[cb_obj_name]
#         cur_mat = cb_obj.active_material
#         cur_mat.diffuse_color = colormap[ind]
#         # print('Changing {} to {}'.format(cb_obj_name, colormap[ind]))
#
#
# def get_colormap():
#     return bpy.context.scene.colorbar_files
#
#
# @mu.tryit()
# def set_colorbar_title(val):
#     val = val.lstrip()
#     val = '     {}'.format(val)
#     init = ColorbarPanel.init
#     bpy.data.objects['colorbar_title'].data.body = bpy.data.objects['colorbar_title_camera'].data.body = val
#     ColorbarPanel.init = False
#     bpy.context.scene.colorbar_title = val
#     ColorbarPanel.init = init
#
#
# def get_colorbar_title():
#     return bpy.context.scene.colorbar_title
#
#
# def set_colorbar_max_min(max_val, min_val, force_update=False):
#     if max_val >= min_val:
#         init = ColorbarPanel.init
#         if force_update:
#             ColorbarPanel.init = True
#         bpy.context.scene.colorbar_max = max_val
#         bpy.context.scene.colorbar_min = min_val
#         # mu.set_graph_att('colorbar_max', max_val)
#         # mu.set_graph_att('colorbar_min', min_val)
#         # _addon().s.colorbar_max = max_val
#         # _addon().s.colorbar_min = min_val
#         ColorbarPanel.init = init
#     else:
#         print('set_colorbar_max_min: ax_val < min_val!')
#
#
# def get_colorbar_max_min():
#     return bpy.context.scene.colorbar_max, bpy.context.scene.colorbar_min
#
#
# def set_colorbar_max(val, prec=None, check_minmax=True):
#     if not check_minmax or bpy.context.scene.colorbar_max > bpy.context.scene.colorbar_min:
#         _set_colorbar_min_max('max', val, prec)
#     else:
#         prev_max = float(bpy.data.objects['colorbar_max'].data.body)
#         ColorbarPanel.init = False
#         bpy.context.scene.colorbar_max = prev_max
#         ColorbarPanel.init = True
#
#
# def get_colorbar_max():
#     return bpy.context.scene.colorbar_max
#
#
# def set_colorbar_min(val, prec=None, check_minmax=True):
#     if not check_minmax or bpy.context.scene.colorbar_max > bpy.context.scene.colorbar_min:
#         _set_colorbar_min_max('min', val, prec)
#     else:
#         prev_min = float(bpy.data.objects['colorbar_min'].data.body)
#         ColorbarPanel.init = False
#         bpy.context.scene.colorbar_min = prev_min
#         ColorbarPanel.init = True
#
#
# def get_colorbar_min():
#     return bpy.context.scene.colorbar_min
#
#
# def get_colorbar_prec():
#     return bpy.context.scene.colorbar_prec
#
#
# def set_colorbar_prec(val):
#     bpy.context.scene.colorbar_prec = val
#
#
# def _set_colorbar_min_max(field, val, prec):
#     if prec is None or prec not in PERC_FORMATS:
#         prec = bpy.context.scene.colorbar_prec
#         if prec not in PERC_FORMATS:
#             print('Wrong value for prec, should be in {}'.format(PERC_FORMATS.keys()))
#     prec_str = PERC_FORMATS[prec]
#     cb_obj = bpy.data.objects.get('colorbar_{}'.format(field))
#     cb_camera_obj = bpy.data.objects.get('colorbar_{}_camera'.format(field))
#     if not cb_obj is None and not cb_camera_obj is None:
#         cb_obj.data.body = cb_camera_obj.data.body = prec_str.format(val)
#     else:
#         print('_set_colorbar_min_max: field error ({})! must be max / min!'.format(field))
#
#
# def set_colormap(colormap_name):
#     if colormap_name in ColorbarPanel.maps_names:
#         bpy.context.scene.colorbar_files = colormap_name
#     else:
#         print('No such colormap! {}'.format(colormap_name))
#
#
# def hide_cb_center_update(self, context):
#     hide_center(bpy.context.scene.hide_cb_center)
#
#
# def hide_center(do_hide):
#     n = len(bpy.data.objects['cCB'].children)
#     for cb in bpy.data.objects['cCB'].children:
#         if not do_hide:
#             cb.hide = False
#         num = int(cb.name.split('.')[-1])
#         if do_hide and n / 2 - 10 < num < n / 2 + 10:
#             cb.hide = True
#
#
# def colormap_update(self, context):
#     if ColorbarPanel.init:
#         load_colormap()
#
#
# def colorbar_update(self, context):
#     if ColorbarPanel.init:
#         ColorbarPanel.colorbar_updated = True
#         set_colorbar_title(bpy.context.scene.colorbar_title)
#         set_colorbar_max(bpy.context.scene.colorbar_max)
#         set_colorbar_min(bpy.context.scene.colorbar_min)
#
#
# def show_cb_in_render_update(self, context):
#     show_cb_in_render(bpy.context.scene.show_cb_in_render)
#
#
# def show_cb_in_render(val=True):
#     mu.show_hide_hierarchy(val, 'colorbar_camera', True, False)
#     mu.show_hide_hierarchy(val, 'cCB_camera', True, False)
#
#
# def colorbar_y_update(self, context):
#     bpy.data.objects['cCB'].location[0] = -bpy.context.scene.colorbar_y
#
#
# def colorbar_text_y_update(self, context):
#     bpy.data.objects['colorbar_max'].location[0] = -bpy.context.scene.colorbar_text_y
#     bpy.data.objects['colorbar_min'].location[0] = -bpy.context.scene.colorbar_text_y
#     bpy.data.objects['colorbar_title'].location[0] = -bpy.context.scene.colorbar_text_y
#
#
# def colorbar_draw(self, context):
#     layout = self.layout
#     layout.prop(context.scene, "colorbar_files", text="")
#     layout.prop(context.scene, "colorbar_title", text="Title:")
#     row = layout.row(align=0)
#     row.prop(context.scene, "colorbar_min", text="min:")
#     row.prop(context.scene, "colorbar_max", text="max:")
#     layout.prop(context.scene, 'hide_cb_center', text='Hide center')
#     layout.prop(context.scene, 'colorbar_prec', text='precision')
#     layout.prop(context.scene, 'lock_min_max', text='Lock values')
#     layout.prop(context.scene, 'show_cb_in_render', text='Show in rendering')
#     layout.prop(context.scene, 'update_cb_location', text='Update location')
#     if bpy.context.scene.update_cb_location:
#         layout.prop(context.scene, "colorbar_y", text="y axis")
#         layout.prop(context.scene, "colorbar_text_y", text="text y axis")
#     # layout.operator(ColorbarButton.bl_idname, text="Do something", icon='ROTATE')


def show_full_slice_update(self, context):
    for cut_type in ['axial', 'coronal', 'sagital']:
        if bpy.data.objects.get('{}_plane'.format(cut_type)):
            bpy.data.objects['{}_plane'.format(cut_type)].modifiers['Boolean'].show_viewport =\
                not bpy.context.scene.show_full_slice


class SliceBrainButton(bpy.types.Operator):
    bl_idname = "mmvt.slice_brain_button"
    bl_label = "Slice Brain button"
    bl_description = 'Slices the brain according to the axis and the cross position.\n\nScript: mmvt.slicer.slice_brain()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        slice_brain()
        cur_obj = bpy.context.scene.objects.active
        try:
            cur_obj.data.uv_textures['UVMap'].data[0].image = bpy.data.images[cur_obj.name.split('_')[0]+'.JPEG']
        except:
            cur_obj.data.uv_textures['UVMap'].data[0].image = bpy.data.images[cur_obj.name.split('_')[0] + '.PNG']
        # need to handle normals direction.
        return {'FINISHED'}


class SliceBrainClearButton(bpy.types.Operator):
    bl_idname = "mmvt.slice_brain_clear_button"
    bl_label = "Slice Brain Clear button"
    bl_description = 'Resets the brain.\n\nScript: mmvt.slicer.clear_slice()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        clear_slice()
        return {'FINISHED'}


class CreateNewElectrode(bpy.types.Operator):
    bl_idname = "mmvt.create_new_electrode"
    bl_label = "Create new electrode"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        new_elc_name = '{}{}'.format(bpy.context.scene.new_electrode_lead, bpy.context.scene.new_electrode_num)
        create_new_electrode(new_elc_name)
        bpy.context.scene.new_electrode_num += 1
        return {'FINISHED'}


class FindNearestElectrodeInCT(bpy.types.Operator):
    bl_idname = "mmvt.find_nearest_electrde_in_ct"
    bl_label = "find_nearest_electrde_in_ct"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        find_nearest_electrde_in_ct()
        return {'FINISHED'}


class ExportElectrodes(bpy.types.Operator):
    bl_idname = "mmvt.export_electrodes"
    bl_label = "export_electrodes"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        export_electrodes()
        return {'FINISHED'}


def what_to_cut_update(self, context):
    if bpy.context.scene.slicer_cut_type == 'coronal':
        bpy.types.Scene.what_to_cut = bpy.props.EnumProperty(
            items=[('1', 'Anterior', '', 1), ('2', 'Posterior', '', 2)],
            description='')
    elif bpy.context.scene.slicer_cut_type == 'sagital':
        bpy.types.Scene.what_to_cut = bpy.props.EnumProperty(
            items=[('1', 'Right', '', 1), ('2', 'Left', '', 2)],
            description='')
    elif bpy.context.scene.slicer_cut_type == 'axial':
        bpy.types.Scene.what_to_cut = bpy.props.EnumProperty(
            items=[('1', 'Superior', '', 1), ('2', 'Inferior', '', 2)],
            description='')


bpy.types.Scene.slicer_cut_type = bpy.props.EnumProperty(
    items=[(cut_type, cut_type.capitalize(), '', ind) for ind, cut_type in enumerate(CUTS)],
    description='Sets the slicing axis.\n\nCurrent axis',update=what_to_cut_update)
# bpy.types.Scene.slice_using_left_click = bpy.props.BoolProperty(
#     default=True, description="slice_using_left_click", update=show_cb_in_render_update)
bpy.types.Scene.show_full_slice = bpy.props.BoolProperty(default=False, update=show_full_slice_update,
    description='Shows the full image of the slice')
# bpy.types.Scene.show_full_slice = bpy.props.BoolProperty()
bpy.types.Scene.slices_modality = bpy.props.EnumProperty(items=[('mri', 'mri', '', 1)])
bpy.types.Scene.slices_modality_mix = bpy.props.FloatProperty(min=0, max=1, default=0, update=slices_modality_mix_update)
bpy.types.Scene.new_electrode_lead = bpy.props.StringProperty()
bpy.types.Scene.new_electrode_num = bpy.props.IntProperty(default=1, min=1)
bpy.types.Scene.slices_zoom = bpy.props.FloatProperty(default=1, min=1, update=slices_zoom_update,
    description='Zooms in the slices view')
bpy.types.Scene.ct_intensity = bpy.props.FloatProperty()
bpy.types.Scene.t1_value = bpy.props.FloatProperty()
bpy.types.Scene.t2_value = bpy.props.FloatProperty()
bpy.types.Scene.slices_zoom_around_voxel = bpy.props.BoolProperty(default=False, update=slices_update,
    description='Zooms around the center of the cross')
bpy.types.Scene.slices_zoom_voxels_num = bpy.props.IntProperty(default=30, min=1, update=slices_update,
    description='Sets the square number of voxels displayed in the slices view')
bpy.types.Scene.slices_zoom_interpolate = bpy.props.BoolProperty(default=False, update=slices_update,
    description='Smooths the slices view')
bpy.types.Scene.slices_x_max = bpy.props.FloatProperty(default=1, update=slices_update,
    description='Sets the white color intensity in the brain slices')
bpy.types.Scene.slices_x_min = bpy.props.FloatProperty(default=1, update=slices_update,
    description='Sets the black color intensity in the brain slices')
bpy.types.Scene.slices_plot_cross = bpy.props.BoolProperty(default=True, update=slices_update,
    description='Hides/Shows the cross in the slices view')
bpy.types.Scene.slices_mark_voxel = bpy.props.BoolProperty(default=True, update=slices_update,
    description='Hides/Shows the cross center')
bpy.types.Scene.pial_vol_mask_exist = bpy.props.BoolProperty()
bpy.types.Scene.dural_vol_mask_exist = bpy.props.BoolProperty()
bpy.types.Scene.slices_show_pial = bpy.props.BoolProperty(default=False, update=slices_update,
    description='Plots the Pial surface on the slices view')
bpy.types.Scene.slices_show_pial_color = bpy.props.FloatVectorProperty(
    name="object_color", subtype='COLOR', default=(1, 0, 0), min=0.0, max=1.0,
    description='Sets the color of the plotted Pial surface')
bpy.types.Scene.slices_show_dural = bpy.props.BoolProperty(default=False, update=slices_update)
bpy.types.Scene.slices_show_dural_color = bpy.props.FloatVectorProperty(
    name="object_color", subtype='COLOR', default=(1, 0, 0), min=0.0, max=1.0, description="color picker")
bpy.types.Scene.slices_rotate_view_on_click = bpy.props.BoolProperty(
    default=True, description='Rotate the brain for best view')
bpy.types.Scene.what_to_cut = bpy.props.EnumProperty(
        items=[('tval', 't-val', '', 1), ('size', 'size', '', 2)],
        update=what_to_cut_update, description='Sorts the clusters list by t-value, size or name.\n\nCurrent sorting')
bpy.types.Scene.slice_seghead = bpy.props.BoolProperty(default=False)


def slicer_draw(self, context):
    layout = self.layout
    col = layout.box().column()
    col.prop(context.scene, "slicer_cut_type", text="")
    col.prop(context.scene, "what_to_cut", text="")
    col.operator(SliceBrainButton.bl_idname, text="Slice brain", icon='FACESEL_HLT')
    col.operator(SliceBrainClearButton.bl_idname, text="Clear slice", icon='MESH_CUBE')
    col.prop(context.scene, 'show_full_slice', text='Show full slice')
    col.prop(context.scene, 'slice_seghead', text='Slice outer skin')

    col = layout.box().column()
    row = col.row(align=0)
    if SlicerPanel.ct_exist or SlicerPanel.t2_exist:
        row.prop(context.scene, 'slices_modality', expand=True)
        if bpy.context.scene.slices_modality == 'mri':
            col.label(text='T1 value: {:.2f}'.format(bpy.context.scene.t1_value))
        elif bpy.context.scene.slices_modality == 't2':
            col.label(text='T2 value: {:.2f}'.format(bpy.context.scene.t2_value))
        elif bpy.context.scene.slices_modality == 'ct':
            col.label(text='CT intensity: {:.2f}'.format(bpy.context.scene.ct_intensity))
        # layout.prop(context.scene, 'slices_modality_mix')
    row = col.row(align=0)
    row.prop(context.scene, 'slices_x_min', text='xmin')
    row.prop(context.scene, 'slices_x_max', text='xmax')
    row = col.row(align=0)
    row.prop(context.scene, 'slices_zoom', text='Slices zoom')
    row.prop(context.scene, 'slices_zoom_around_voxel', text='zoom around voxel')
    if mu.SCIPY_EXIST and bpy.context.scene.slices_zoom_around_voxel:
        row = col.row(align=0)
        row.prop(context.scene, 'slices_zoom_voxels_num', text='#voxels')
        row.prop(context.scene, 'slices_zoom_interpolate', text='smooth')
    row = col.row(align=0)
    row.prop(context.scene, 'slices_plot_cross', text='Plot cross')
    row.prop(context.scene, 'slices_mark_voxel', text='Mark voxel')
    if bpy.context.scene.pial_vol_mask_exist:
        row = col.row(align=0)
        row.prop(context.scene, 'slices_show_pial', text='Plot pial')
        if context.scene.slices_show_pial:
            row.prop(context.scene, 'slices_show_pial_color', text='')
    if bpy.context.scene.dural_vol_mask_exist:
        row = col.row(align=0)
        row.prop(context.scene, 'slices_show_dural', text='Plot dural')
        if context.scene.slices_show_dural:
            row.prop(context.scene, 'slices_show_dural_color', text='')
    col.prop(context.scene, "slices_rotate_view_on_click", text='Rotate the brain on click')


    # col = layout.box().column()
    # col.prop(context.scene, 'new_electrode_lead', text='Lead')
    # col.prop(context.scene, 'new_electrode_num', text='Number')
    # col.operator(FindNearestElectrodeInCT.bl_idname, text="Find nearest electrodes", icon='MESH_CUBE')
    # col.operator(CreateNewElectrode.bl_idname, text="Create electrode", icon='MESH_CUBE')
    # col.operator(ExportElectrodes.bl_idname, text="Export electrodes", icon='MESH_CUBE')


class SlicerPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Slicer"
    addon = None
    ct_exist = False
    t2_exist = False
    init = False

    def draw(self, context):
        if SlicerPanel.init:
            slicer_draw(self, context)


def init(addon):
    SlicerPanel.addon = addon
    bpy.context.scene.show_full_slice = False
    create_joint_brain_obj()
    # print('init slicer')
    # bpy.context.scene.is_sliced_ind = -1
    # bpy.context.scene.last_cursor_location = [0.0, 0.0, 0.0]
    bpy.types.Scene.last_cursor_location = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0),size=3)
    bpy.types.Scene.is_sliced_ind = bpy.props.IntProperty(default=-1)
    bpy.context.scene.last_cursor_location = (0.0, 0.0, 0.0)
    bpy.context.scene.is_sliced_ind = -1
    bpy.context.scene.slicer_cut_type = 'coronal'
    ct_trans_fname = op.join(mu.get_user_fol(), 'ct', 'ct_trans.npz')
    t2_trans_fname = op.join(mu.get_user_fol(), 't2_trans.npz')
    if op.isfile(ct_trans_fname) or op.isfile(t2_trans_fname):
        items_ind = 1
        items = [('mri', 'MRI', '', items_ind)]
        if op.isfile(t2_trans_fname):
            SlicerPanel.t2_exist = True
            items_ind += 1
            items.append(('t2', 'T2', '', items_ind))
        if op.isfile(ct_trans_fname):
            items_ind += 1
            SlicerPanel.ct_exist = True
            items.append(('ct', 'CT', '', items_ind))
        if op.isfile(op.join(mu.get_user_fol(), 'ct', 't1_ct.mgz')):
            items_ind += 1
            SlicerPanel.t1_ct_exist = True
            items.append(('t1_ct', 'T1&CT', '', items_ind))
        bpy.types.Scene.slices_modality = bpy.props.EnumProperty(items=items, update=slices_modality_update)
    pial_vol_mask_fname = op.join(mu.get_user_fol(), 'freeview', 'pial_vol_mask.npy')
    dural_vol_mask_fname = op.join(mu.get_user_fol(), 'freeview', 'dural_vol_mask.npy')
    bpy.context.scene.pial_vol_mask_exist = op.isfile(pial_vol_mask_fname)
    bpy.context.scene.dural_vol_mask_exist = op.isfile(dural_vol_mask_fname)
    bpy.context.scene.slices_show_pial = False
    bpy.context.scene.slices_show_dural = False
    bpy.context.scene.slices_modality_mix = 0
    bpy.context.scene.slices_zoom = 1
    bpy.context.scene.new_electrode_num = 1
    bpy.context.scene.slices_zoom_around_voxel = False
    bpy.context.scene.slices_zoom_voxels_num = 30
    bpy.context.scene.slices_zoom_interpolate = False
    bpy.context.scene.slices_plot_cross = True
    bpy.context.scene.slices_mark_voxel = True
    bpy.context.scene.slices_modality = 'mri'
    empty_brain_path = op.join(mu.get_mmvt_code_root(), 'resources', 'empty_subject.blend', 'Material')
    for slice_str in ['coronal', 'sagital', 'axial']:
        cur_mat_name = '{}_plane_mat'.format(slice_str)
        if bpy.data.materials.get(cur_mat_name) is None:
            print('Importing {} from empty_brain file'.format(cur_mat_name))
            bpy.ops.wm.append(filename=cur_mat_name, directory=empty_brain_path)
    # bpy.context.scene['slice_plane_flipped'] = {'coronal': False, 'axial': False, 'sagital': False}
    SlicerPanel.init = True
    register()


def register():
    try:
        unregister()
        bpy.utils.register_class(SlicerPanel)
        bpy.utils.register_class(SliceBrainButton)
        bpy.utils.register_class(SliceBrainClearButton)
        bpy.utils.register_class(CreateNewElectrode)
        bpy.utils.register_class(FindNearestElectrodeInCT)
        bpy.utils.register_class(ExportElectrodes)
        # print('SlicerPanel was registered')
        # print('SliceBrainButton was registered')
        # print('SliceBrainClearButton was registered')
    except:
        print("Can't register Slicer Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(SlicerPanel)
        bpy.utils.unregister_class(SliceBrainButton)
        bpy.utils.unregister_class(SliceBrainClearButton)
        bpy.utils.unregister_class(CreateNewElectrode)
        bpy.utils.unregister_class(FindNearestElectrodeInCT)
        bpy.utils.unregister_class(ExportElectrodes)
    except:
        pass
