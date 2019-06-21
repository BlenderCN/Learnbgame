import bpy
import mmvt_utils as mu
import time
import sys
import traceback
import numpy as np
import os.path as op

import coloring_panel


def _addon():
    return AppearanceMakerPanel.addon


def setup_layers():
    for layer_ind in range(len(bpy.context.scene.layers)):
        bpy.context.scene.layers[layer_ind] = layer_ind == _addon().EMPTY_LAYER

    bpy.context.scene.layers[_addon().ELECTRODES_LAYER] = bpy.context.scene.show_hide_electrodes
    bpy.context.scene.layers[_addon().EEG_LAYER] = bpy.context.scene.show_hide_eeg_sensors
    bpy.context.scene.layers[_addon().ROIS_LAYER] = is_rois()
    # bpy.context.scene.layers[_addon().ACTIVITY_LAYER] = is_activity()
    bpy.context.scene.layers[_addon().CONNECTIONS_LAYER] = bpy.context.scene.appearance_show_connections_layer


def change_view3d():
    viewport_shade = bpy.context.scene.filter_view_type
    if viewport_shade == 'rendered':
        bpy.context.scene.layers[_addon().LIGHTS_LAYER] = True
        viewport_shade_str = 'RENDERED'
        bpy.context.scene.render.engine = 'CYCLES'
        # todo: why?
        # _addon().set_brain_transparency(0.0)
    else:
        bpy.context.scene.layers[_addon().LIGHTS_LAYER] = False
        viewport_shade_str = 'SOLID'
        bpy.context.scene.render.engine = 'BLENDER_RENDER'

    for ii in range(len(bpy.context.screen.areas)):
        if bpy.context.screen.areas[ii].type == 'VIEW_3D':
            bpy.context.screen.areas[ii].spaces[0].viewport_shade = viewport_shade_str
            # break


def panels_background_color_update(self, context):
    context.user_preferences.themes[0].image_editor.space.back = \
        context.user_preferences.themes[0].view_3d.space.gradients.high_gradient = \
        bpy.context.scene.panels_background_color


def set_panels_background_color(color_rgb):
    bpy.context.scene.panels_background_color = color_rgb


def get_panels_background_color():
    return tuple(bpy.context.scene.panels_background_color)


def show_hide_meg_sensors(do_show=True):
    bpy.context.scene.layers[_addon().MEG_LAYER] = do_show


def show_meg_sensors():
    bpy.context.scene.layers[_addon().MEG_LAYER] = True


def hide_meg_sensors():
    bpy.context.scene.layers[_addon().MEG_LAYER] = False


def showing_meg_sensors():
    return bpy.context.scene.layers[_addon().MEG_LAYER]


def show_hide_eeg_sensors(do_show=True):
    bpy.context.scene.layers[_addon().EEG_LAYER] = do_show


def showing_eeg():
    return bpy.context.scene.layers[_addon().EEG_LAYER]


def show_hide_electrodes(do_show):
    bpy.context.scene.layers[_addon().ELECTRODES_LAYER] = do_show
    # mu.show_hide_hierarchy(do_show, 'Deep_electrodes', select=False)
    if do_show:
        bpy.context.scene.show_only_lead = False


def showing_electordes():
    return bpy.context.scene.layers[_addon().ELECTRODES_LAYER]


def show_rois():
    if bpy.context.scene.appearance_show_rois_activity != 'rois':
        bpy.context.scene.appearance_show_rois_activity = 'rois'


def show_activity():
    if bpy.context.scene.appearance_show_rois_activity != 'activity':
        bpy.context.scene.appearance_show_rois_activity = 'activity'


# def show_pial():
#     bpy.context.scene.surface_type = 'pial'
#
#
# def show_inflated():
#     bpy.context.scene.surface_type == 'inflated'


def show_electrodes(value=True):
    show_hide_electrodes(value)


def hide_electrodes():
    show_hide_electrodes(False)


def is_pial():
    return bpy.context.scene.surface_type == 'pial'


def is_inflated():
    return bpy.context.scene.surface_type == 'inflated'


def is_activity():
    return bpy.context.scene.appearance_show_rois_activity == 'activity'


def is_rois():
    return bpy.context.scene.appearance_show_rois_activity == 'rois'


def hemis_inf_distance_update(self, context):
    if AppearanceMakerPanel.init:
        if bpy.data.objects.get('Cortex-inflated-rh') and bpy.data.objects.get('inflated_rh'):
            bpy.data.objects['Cortex-inflated-rh'].location[0] = bpy.data.objects['inflated_rh'].location[0] = \
                AppearanceMakerPanel.cortex_inflated_rh + bpy.context.scene.hemis_inf_distance
            bpy.data.objects['Cortex-inflated-lh'].location[0] = bpy.data.objects['inflated_lh'].location[0] = \
                AppearanceMakerPanel.cortex_inflated_lh - bpy.context.scene.hemis_inf_distance


def hemis_distance_update(self, context):
    if AppearanceMakerPanel.init:
        if bpy.data.objects.get('Cortex-rh') and bpy.data.objects.get('rh'):
            bpy.data.objects['Cortex-rh'].location[0] = bpy.data.objects['rh'].location[0] = \
                AppearanceMakerPanel.cortex_rh + bpy.context.scene.hemis_distance
            bpy.data.objects['Cortex-lh'].location[0] = bpy.data.objects['lh'].location[0] = \
                AppearanceMakerPanel.cortex_lh - bpy.context.scene.hemis_distance

        if bpy.data.objects.get('inflated_rh') and bpy.data.objects.get('Cortex-inflated-rh'):
            bpy.data.objects['inflated_rh'].location[0] = bpy.data.objects['Cortex-inflated-rh'].location[0] = \
                AppearanceMakerPanel.cortex_rh + bpy.context.scene.hemis_distance
            bpy.data.objects['inflated_lh'].location[0] = bpy.data.objects['Cortex-inflated-lh'].location[0] = \
                AppearanceMakerPanel.cortex_rh - bpy.context.scene.hemis_distance

        bpy.context.scene.cursor_is_snapped = bpy.context.scene.hemis_distance == 0

# def inflating_update(self, context):
#     try:
#         if bpy.data.objects.get('rh', None) is None:
#             return
#         bpy.data.shape_keys['Key'].key_blocks["inflated"].value = bpy.context.scene.inflating
#         bpy.data.shape_keys['Key.001'].key_blocks["inflated"].value = bpy.context.scene.inflating
#         # bpy.context.scene.hemis_inf_distance = - (1 - bpy.context.scene.inflating) * 5
#         vert, obj_name = get_closest_vertex_and_mesh_to_cursor()
#         if obj_name != '':
#             if 'inflated' not in obj_name:
#                 obj_name = 'inflated_{}'.format(obj_name)
#             ob = bpy.data.objects[obj_name]
#             scene = bpy.context.scene
#             me = ob.to_mesh(scene, True, 'PREVIEW')
#             bpy.context.scene.cursor_location = me.vertices[vert].co / 10
#             bpy.data.meshes.remove(me)
#     except:
#         print('Error in inflating update!')
#         print(traceback.format_exc())


def inflating_update(self, context):
    _inflating_update()


# @mu.profileit('cumtime', op.join(mu.get_user_fol()))
def _inflating_update():
    try:
        if bpy.data.objects.get('rh', None) is None:
            return
        if bpy.context.scene.inflating > 0: #flattening
            # _addon().show_coronal(True)
            # _addon().view_all()
            if AppearanceMakerPanel.flat_map_exists:
                bpy.data.shape_keys['Key'].key_blocks["flat"].value = bpy.context.scene.inflating
                bpy.data.shape_keys['Key.001'].key_blocks["flat"].value = bpy.context.scene.inflating
            bpy.data.shape_keys['Key'].key_blocks["inflated"].value = 1
            bpy.data.shape_keys['Key.001'].key_blocks["inflated"].value = 1

            bpy.data.objects['inflated_rh'].location[0] = 10 * bpy.context.scene.inflating
            bpy.data.objects['inflated_lh'].location[0] = -10 * bpy.context.scene.inflating
            # bpy.data.objects['inflated_rh'].location[0] = bpy.context.scene.inflating
            # bpy.data.objects['inflated_lh'].location[0] = bpy.context.scene.inflating

            use_masking = True
        else: #deflating
            bpy.data.shape_keys['Key'].key_blocks["inflated"].value = bpy.context.scene.inflating + 1
            bpy.data.shape_keys['Key.001'].key_blocks["inflated"].value = bpy.context.scene.inflating + 1
            if AppearanceMakerPanel.flat_map_exists:
                bpy.data.shape_keys['Key'].key_blocks["flat"].value = 0
                bpy.data.shape_keys['Key.001'].key_blocks["flat"].value = 0

            bpy.data.objects['inflated_rh'].location[0] = 0
            bpy.data.objects['inflated_lh'].location[0] = 0
            use_masking = False

        # mu.set_zoom_level(bpy.context.scene.surface_type, abs(bpy.context.scene.inflating))
        bpy.context.scene.layers[_addon().ACTIVITY_LAYER] = False
        bpy.context.scene.layers[_addon().ELECTRODES_LAYER] = False

        AppearanceMakerPanel.no_surface_type_update = True
        infl = bpy.context.scene.inflating
        if 0 < infl <= 1.0:
            bpy.context.scene.surface_type = 'flat'
            _addon().show_coronal(True)
        elif -1.0 < infl <= 0.0:
            bpy.context.scene.surface_type = 'inflated'
        elif infl == -1.0:
            bpy.context.scene.surface_type = 'pial'
            bpy.context.scene.layers[_addon().ACTIVITY_LAYER] = True
            if bpy.context.scene.show_hide_electrodes:
                bpy.context.scene.layers[_addon().ELECTRODES_LAYER] = True
        AppearanceMakerPanel.no_surface_type_update = False

        if AppearanceMakerPanel.flat_map_exists:
            for hemi in ['rh', 'lh']:
                mu.get_hemi_obj(hemi).modifiers['mask_bad_vertices'].show_viewport = use_masking
                mu.get_hemi_obj(hemi).modifiers['mask_bad_vertices'].show_render = use_masking
                # print(use_masking)
        # bpy.context.scene.hemis_inf_distance = - (1 - bpy.context.scene.inflating) * 5

        if bpy.context.scene.cursor_is_snapped:
            vert, obj_name = get_closest_vertex_and_mesh_to_cursor()
            if obj_name != '':
                if 'inflated' not in obj_name:
                    obj_name = 'inflated_{}'.format(obj_name)
                obj = bpy.data.objects[obj_name]
                move_cursor_according_to_vert(vert, obj)

    except:
        print('Error in inflating update!')
        print(traceback.format_exc())


def move_cursor_according_to_vert(vert, obj):
    if isinstance(obj, str):
        obj = bpy.data.objects[obj]

    me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
    try:
        bpy.context.scene.cursor_location = me.vertices[vert].co * obj.matrix_world  # / 10
        # hemi = 'rh' if 'rh' in obj.name else 'lh' if 'lh' in obj.name else ''
        # bpy.context.scene.cursor_location = AppearanceMakerPanel.mesh[hemi].vertices[vert].co * obj.matrix_world  # / 10
        # print('cursor_location: {}'.format(bpy.context.scene.cursor_location))
    except:
        print('move_cursor_according_to_vert: Error!')
    bpy.data.meshes.remove(me)


def set_inflated_ratio(ratio):
    bpy.context.scene.inflating = ratio

    # todo: why we need those lines?
    # if not is_rendered():
    #     _addon().view_all()


def get_inflated_ratio():
    return bpy.context.scene.inflating


def appearance_show_rois_activity_update(self=None, context=None):
    if not AppearanceMakerPanel.init:
        return
    # todo: Figure out why the hell
    for _ in range(2):
        if bpy.context.scene.surface_type == 'pial':
            bpy.context.scene.layers[_addon().ROIS_LAYER] = is_rois()
            bpy.context.scene.layers[_addon().ACTIVITY_LAYER] = is_activity()
            bpy.context.scene.layers[_addon().INFLATED_ACTIVITY_LAYER] = is_activity()
        elif bpy.context.scene.surface_type == 'inflated':
            bpy.context.scene.layers[_addon().INFLATED_ROIS_LAYER] = is_rois()
            bpy.context.scene.layers[_addon().INFLATED_ACTIVITY_LAYER] = is_activity()
            # if is_activity():
            #     # bpy.context.scene.inflating = 0
            #     # bpy.context.scene.hemis_inf_distance = -5
            #     pass
            # else:
            #     bpy.context.scene.hemis_inf_distance = 0
            #     pass
    # print('roi: {}, activity: {}'.format(bpy.context.scene.layers[ROIS_LAYER], bpy.context.scene.layers[ACTIVITY_LAYER]))
    # print('should be {}, {}'.format(is_rois(), is_activity()))
    # if bpy.context.scene.layers[_addon().ROIS_LAYER] != is_rois() or \
    #                 bpy.context.scene.layers[_addon().ACTIVITY_LAYER] != is_activity():
    #     print('Error in displaying the layers!')
    if not _addon() is None and is_activity():
        fmri_hide = not is_activity() if bpy.context.scene.subcortical_layer == 'fmri' else is_activity()
        meg_hide = not is_activity() if bpy.context.scene.subcortical_layer == 'meg' else is_activity()
        if not bpy.context.scene.objects_show_hide_sub_cortical:
            _addon().show_hide_hierarchy(do_hide=fmri_hide, obj_name="Subcortical_fmri_activity_map")
            _addon().show_hide_hierarchy(do_hide=meg_hide, obj_name="Subcortical_meg_activity_map")


def show_hide_connections(value=True):
    bpy.context.scene.layers[_addon().CONNECTIONS_LAYER] = value
    if value and bpy.data.objects.get(_addon().get_connections_parent_name()):
        _addon().show_hide_hierarchy(False, _addon().get_connections_parent_name())
        # bpy.data.objects.get(_addon().get_connections_parent_name()).hide = False
        # bpy.data.objects.get(_addon().get_connections_parent_name()).hide_render = False


# def show_connections(value=True):
#     bpy.context.scene.appearance_show_connections_layer = value


def connections_visible():
    return bpy.data.objects.get(_addon().get_connections_parent_name()) and bpy.context.scene.layers[_addon().CONNECTIONS_LAYER]


def filter_view_type_update(self, context):
    change_view3d()


def surface_type_update(self, context):
    if AppearanceMakerPanel.no_surface_type_update:
        return
    if bpy.context.scene.surface_type == 'pial':
        bpy.context.scene.inflating = -1
    elif bpy.context.scene.surface_type == 'inflated':
        bpy.context.scene.inflating = 0
    elif bpy.context.scene.surface_type == 'flat':
        bpy.context.scene.inflating = 1
    else:
        print('Wrong value of surface_type! {}'.format(bpy.context.scene.surface_type))
    return
    if bpy.data.objects['inflated_lh'].location[0] != 0:
        _addon().set_normal_view()
    # tmp = bpy.context.scene.surface_type
    inflated = bpy.context.scene.surface_type == 'inflated'
    # todo: why we need the for loop here?!?
    for _ in range(2):
        if is_rois():
            bpy.context.scene.layers[_addon().INFLATED_ROIS_LAYER] = inflated
            bpy.context.scene.layers[_addon().ROIS_LAYER] = not inflated
        elif is_activity():
            # bpy.context.scene.layers[_addon().INFLATED_ACTIVITY_LAYER] = inflated
            # bpy.context.scene.layers[_addon().ACTIVITY_LAYER] = not inflated
            bpy.context.scene.layers[_addon().INFLATED_ACTIVITY_LAYER] = True
            # bpy.context.scene.layers[_addon().ACTIVITY_LAYER] = not True
    if inflated:
        AppearanceMakerPanel.showing_meg_sensors = showing_meg_sensors()
        AppearanceMakerPanel.showing_eeg_sensors = showing_eeg()
        AppearanceMakerPanel.showing_electrodes = showing_electordes()
        show_hide_meg_sensors(False)
        show_hide_eeg_sensors(False)
        show_hide_electrodes(False)
    else:
        show_hide_meg_sensors(AppearanceMakerPanel.showing_meg_sensors)
        show_hide_eeg_sensors(AppearanceMakerPanel.showing_eeg_sensors)
        show_hide_electrodes(AppearanceMakerPanel.showing_electrodes)

    # mu.set_zoom_level(bpy.context.scene.surface_type, 1)
    if bpy.context.scene.surface_type == 'inflated':
        set_inflated_ratio(0)

        # print('inflated - set_inflated_ratio(0) the actual value={}'.format(bpy.context.scene.inflating))
    if bpy.context.scene.surface_type == 'flat':
        set_inflated_ratio(1)
        _addon().show_coronal(True)
        # mu.set_zoom_for_flatmap()
        # print('flat_map - set_inflated_ratio(1) the actual value={}'.format(bpy.context.scene.inflating))
    if bpy.context.scene.surface_type == 'pial':
        set_inflated_ratio(-1)
        bpy.context.scene.layers[_addon().ACTIVITY_LAYER] = True
        # bpy.data.objects['lh'].hide  = True
        # bpy.data.objects['rh'].hide = True
        # print('pial - set_inflated_ratio(-1) the actual value={}'.format(bpy.context.scene.inflating))

    if bpy.context.scene.cursor_is_snapped:
        vertex_ind, closest_mesh_name = get_closest_vertex_and_mesh_to_cursor()
        if closest_mesh_name != '':
            mesh_name = 'inflated_{}'.format(closest_mesh_name) if 'inflated' not in closest_mesh_name else \
                closest_mesh_name.replace('inflated_', '')
            if 'inflated' in mesh_name:
                me = bpy.data.objects[mesh_name].to_mesh(bpy.context.scene, True, 'PREVIEW')
                vert = me.vertices[vertex_ind]
                bpy.data.meshes.remove(me)
            else:
                vert = bpy.data.objects[mesh_name].data.vertices[vertex_ind]
            set_closest_vertex_and_mesh_to_cursor(vertex_ind, mesh_name)
            bpy.context.scene.cursor_location = vert.co / 10.0

    _addon().update_camera_files()


def show_pial():
    bpy.context.scene.inflating = -1
    # bpy.context.scene.surface_type = 'pial'


def show_inflated():
    # bpy.context.scene.surface_type = 'inflated'
    bpy.context.scene.inflating = 0


def show_flat():
    bpy.context.scene.inflating = 1


def change_to_rendered_brain():
    bpy.context.scene.filter_view_type = 'rendered'
    bpy.context.scene.render.engine = 'CYCLES'


def change_to_solid_brain():
    bpy.context.scene.filter_view_type = 'solid'
    bpy.context.scene.render.engine = 'BLENDER_RENDER'


def is_solid():
    return bpy.context.scene.filter_view_type == 'solid'


def is_rendered():
    return bpy.context.scene.filter_view_type == 'rendered'


def make_brain_solid_or_transparent():
    # bpy.data.materials['Activity_map_mat'].node_tree.nodes['transparency_node'].inputs[
    #     'Fac'].default_value = bpy.context.scene.appearance_solid_slider
    set_transparency()
    if 'subcortical_activity_mat' in bpy.data.materials:
        set_transparency('subcortical_activity_mat')
        # subcortical_mat = bpy.data.materials['subcortical_activity_mat']
        # subcortical_mat.node_tree.nodes['transparency_node'].inputs['Fac'].default_value = \
        #     bpy.context.scene.appearance_solid_slider


def set_transparency(material_name='Activity_map_mat', val=None):
    if val is None:
        val = bpy.context.scene.appearance_solid_slider
    else:
        val = 1 - val
    bpy.data.materials[material_name].node_tree.nodes['transparency_node'].inputs['Fac'].default_value = val


def set_layers_depth_trans(material_name='Activity_map_mat', depth=None):
    # depth = bpy.context.scene.appearance_depth_slider if bpy.context.scene.appearance_depth_Bool else 0
    if depth is None:
        depth = bpy.context.scene.appearance_depth_slider
    bpy.data.materials[material_name].node_tree.nodes["layers_depth"].inputs[1].default_value = depth


def appearance_draw(self, context):
    layout = self.layout
    if bpy.context.scene.show_appearance_settings:
        layout.prop(context.scene, 'appearance_show_rois_activity', expand=True)
        layout.prop(context.scene, "filter_view_type", expand=True)
    layout.prop(context.scene, "surface_type", expand=True)
    # if 'Key' in bpy.data.shape_keys and is_inflated() and is_activity():
    #     layout.prop(context.scene, 'inflating')
    row = layout.split(percentage=0.5, align=True)
    c = row.split(percentage=0.95, align=True)
    if 'Key' in bpy.data.shape_keys and is_activity():
        c.prop(context.scene, 'inflating')
    # if bpy.context.scene.surface_type == 'pial':
    row.prop(context.scene, 'hemis_distance', text='hemis dist')
    # else:
    #     if bpy.data.objects.get('Cortex-inflated-rh') and bpy.data.objects.get('Cortex-inflated-lh'):
    #         layout.prop(context.scene, 'hemis_inf_distance', text='hemis dist')
    # layout.operator(SelectionListener.bl_idname, text="", icon='PREV_KEYFRAME')
    row = layout.row(align=True)
    if bpy.data.objects.get(_addon().electrodes_panel_parent) and is_pial():
        show_hide_icon(row, ShowHideElectrodes.bl_idname, bpy.context.scene.show_hide_electrodes, 'Electrodes')
    if bpy.data.objects.get('MEG_sensors') and is_pial():
        show_hide_icon(row, ShowHideMEGSensors.bl_idname, bpy.context.scene.show_hide_meg_sensors, 'MEG sensors')
    if bpy.data.objects.get('EEG_sensors') and is_pial():
        show_hide_icon(row, ShowHideEEGSensors.bl_idname, bpy.context.scene.show_hide_eeg_sensors, 'EEG sensors')
    if bpy.data.objects.get(_addon().get_connections_parent_name()):
        show_hide_icon(row, ShowHideConnections.bl_idname, bpy.context.scene.show_hide_connections, 'Connections')
    # if is_inflated():
    # if bpy.context.scene.cursor_is_snapped:
    #     layout.operator(
    #         SnapCursor.bl_idname, text='Release Cursor from Brain', icon='UNPINNED')
    if bpy.context.scene.show_appearance_settings:
        if bpy.context.scene.hemis_distance == 0 and bpy.data.objects['inflated_lh'].location[0] == 0:
            layout.prop(context.scene, 'cursor_is_snapped', text='Snap cursor to cortex')
        layout.prop(context.scene, 'panels_background_color', text='Background')
    layout.prop(context.scene, 'show_appearance_settings', text='More settings')


def show_hide_icon(layout, bl_idname, show_hide_var, var_name):
    vis = not show_hide_var
    show_text = '{} {}'.format('' if vis else '', var_name)
    icon = mu.show_hide_icon['show' if vis else 'hide']
    layout.operator(bl_idname, text=show_text, icon=icon)


def update_solidity(self, context):
    make_brain_solid_or_transparent()
    set_layers_depth_trans()


def is_view_3d():
    try:
        return bpy.context.area.spaces.active.type == 'VIEW_3D'
    except:
        return False


class SelectionListener(bpy.types.Operator):
    bl_idname = 'mmvt.selection_listener'
    bl_label = 'selection_listener'
    bl_options = {'UNDO'}
    press_time = time.time()
    running = False
    right_clicked, left_clicked = False, False
    cursor_pos = bpy.context.scene.cursor_location.copy()

    # Add info: https://blender.stackexchange.com/questions/76464/how-to-get-the-mouse-coordinates-in-3space-relative-to-the-local-coordinates-of

    def modal(self, context, event):
        if self.left_clicked:
            self.left_clicked = False
            active_image, pos = click_inside_images_view(event)
            if active_image is not None:
                xyz = _addon().slices_were_clicked(active_image, pos)
                bpy.context.scene.cursor_location = tuple(xyz)
                set_cursor_pos()
                if bpy.context.scene.cursor_is_snapped:  # and is_view_3d():
                    _addon().set_tkreg_ras(bpy.context.scene.cursor_location * 10, False)
                    snap_cursor(True)
                    if bpy.context.scene.slices_rotate_view_on_click:
                        mu.rotate_view_to_vertice()
                # if bpy.context.scene.slices_zoom > 1:
                #     ohad(pos/bpy.context.scene.slices_zoom)
                return {'PASS_THROUGH'}
            if not click_inside_3d_view(event):
                return {'PASS_THROUGH'}
            if _addon().meg.change_cursor_on_selection():
                cluster = _addon().select_meg_cluster(event, context, bpy.context.scene.cursor_location)
                if cluster is not None:
                    return {'PASS_THROUGH'}
            cursor_moved = np.linalg.norm(SelectionListener.cursor_pos - bpy.context.scene.cursor_location) > 1e-3
            if cursor_moved and bpy.data.objects.get('inner_skull', None) is not None:
                _addon().find_point_thickness()
                return {'PASS_THROUGH'}
            if bpy.context.scene.cursor_is_snapped:# and is_view_3d():
                snap_cursor(True)
            if _addon().fMRI_clusters_files_exist() and bpy.context.scene.plot_fmri_cluster_per_click:
                _addon().find_closest_cluster(only_within=True)

            tkreg_ras = _addon().calc_tkreg_ras_from_cursor()
            if tkreg_ras is not None:
                _addon().set_tkreg_ras(tkreg_ras, move_cursor=False)
            # if _addon().is_pial():
            #     tkreg_ras = bpy.context.scene.cursor_location * 10
            #     _addon().set_tkreg_ras(tkreg_ras)
            # elif bpy.context.scene.cursor_is_snapped:
            #     tkreg_ras = _addon().calc_tkreg_ras_from_snapped_cursor()
            #     _addon().set_tkreg_ras(tkreg_ras)

            if cursor_moved:
                set_cursor_pos()
                # print('cursor position was changed by the user!')
                _addon().create_slices(pos=tkreg_ras)
                _addon().freeview.save_cursor_position()
                clear_slice()
            if bpy.context.scene.find_closest_label_on_click: # coloring_panel.WIC_CONTOURS in _addon().what_is_colored():
                _addon().find_closest_label(plot_contour=bpy.context.scene.plot_closest_label_contour)

        if self.right_clicked:
            self.right_clicked = False
            if not click_inside_3d_view(event):
                return {'PASS_THROUGH'}
            # print(bpy.context.selected_objects)
            # cluster = _addon().select_meg_cluster(event, context)
            # if cluster is not None:
            #     return {'PASS_THROUGH'}
            if len(bpy.context.selected_objects):
                mu.unfilter_graph_editor()
                if bpy.context.scene.fit_graph_on_selection:
                    mu.view_all_in_graph_editor()
                selected_obj = bpy.context.active_object # bpy.context.selected_objects[-1]
                selected_obj_name = selected_obj.name
                selected_obj_type = mu.check_obj_type(selected_obj_name)
                if selected_obj_type in [mu.OBJ_TYPE_CORTEX_LH, mu.OBJ_TYPE_CORTEX_RH]:
                    _addon().select_roi(selected_obj_name)
                elif selected_obj_type in [mu.OBJ_TYPE_CORTEX_INFLATED_LH, mu.OBJ_TYPE_CORTEX_INFLATED_RH]:
                    pial_obj_name = selected_obj_name[len('inflated_'):]
                    pial_obj = bpy.data.objects.get(pial_obj_name)
                    if not pial_obj is None:
                        # pial_obj.select = True
                        _addon().select_roi(pial_obj_name)
                        # mu.change_selected_fcurves_colors(pial_obj)
                        # mu.change_selected_fcurves_colors()
                elif selected_obj_type == mu.OBJ_TYPE_CON:
                    _addon().select_connection(selected_obj_name)
                elif selected_obj_type == mu.OBJ_TYPE_CON_VERTICE:
                    _addon().vertices_selected(selected_obj_name)
                elif selected_obj_type == mu.OBJ_TYPE_ELECTRODE:
                    bpy.context.scene.cursor_is_snapped = False
                    _addon().electode_was_manually_selected(selected_obj_name)
                    try:
                        _addon().dell.dell_ct_electrode_was_selected(selected_obj_name)
                    except:
                        pass
                if bpy.context.scene.find_curves_sep_auto:
                    _addon().calc_best_curves_sep()
                elif bpy.context.scene.curves_sep > 0:
                    _addon().curves_sep_update()
            else:
                _addon().clear_electrodes_selection()
                #todo: should call to _addon().clear_rois_selection()
                # if is_activity():
                #     bpy.context.scene.cursor_location = mouse_coo_to_3d_loc(event, context)
                #     snap_cursor(True)
                #     _addon().find_closest_label()

        if time.time() - self.press_time > 1 and event.value == 'PRESS':
            if event.type == 'RIGHTMOUSE':
                self.press_time = time.time()
                self.right_clicked = True
            if event.type == 'LEFTMOUSE':
                self.press_time = time.time()
                self.left_clicked = True

        if time.time() - self.press_time > 0.1:
            if event.type == 'TIMER':
                if bpy.context.scene.rotate_brain:
                    if _addon().render.is_camera_view():
                        _addon().render.camera_mode('ORTHO')
                        _addon().show_hide.rotate_brain()
                        _addon().render.camera_mode('CAMERA')
                    else:
                        _addon().show_hide.rotate_brain()

        if _addon() and _addon().render_in_queue():
            rendering_data = mu.queue_get(_addon().render_in_queue())
            if not rendering_data is None:
                try:
                    rendering_data = rendering_data.decode(sys.getfilesystemencoding(), 'ignore')
                    if '*** finish rendering! ***' in rendering_data.lower():
                        print('Finish rendering!')
                        _addon().finish_rendering()
                except:
                    print("Can't read the stdout from the rendering")

        return {'PASS_THROUGH'}

    def invoke(self, context, event=None):
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.running:
            context.window_manager.modal_handler_add(self)
            self._timer = context.window_manager.event_timer_add(0.1, context.window)
            self.running = True
        return {'RUNNING_MODAL'}


def click_inside_3d_view(event):
    for area in mu.get_3d_areas():
        if 0 < event.mouse_x-area.x < area.width and 0 < event.mouse_y-area.y < area.height:
            return True
    return False


def click_inside_images_view(event):
    for area, region in mu.get_images_area_regions():
        if 0 < event.mouse_x-area.x < area.width and 0 < event.mouse_y-area.y < area.height:
            return area.spaces.active.image, tuple(area.spaces.active.cursor_location)
    # screen = bpy.data.screens['Neuro']
    # images_areas = [area for area in screen.areas if area.type == 'IMAGE_EDITOR']
    # slices_cursor_pos = _addon().get_slices_cursor_pos()
    # for area in images_areas:
    #     active_image = area.spaces.active.image
    #     if active_image is not None and active_image.name in slices_cursor_pos:
    #         pos = tuple(area.spaces.active.cursor_location)
    #         if pos != slices_cursor_pos[active_image.name]:
    #             return active_image, pos
    return None, None


def ohad(offset_values):
    for area, region in mu.get_images_area_regions():
        override = bpy.context.copy()
        override['area'] = area
        override['region'] = region
        bpy.ops.image.view_pan(override, offset=(-offset_values[0], -offset_value[1]))


def set_cursor_pos():
    SelectionListener.cursor_pos = bpy.context.scene.cursor_location.copy()


def clear_slice():
    if AppearanceMakerPanel.init:
        try:
            if bpy.context.scene.is_sliced_ind > -1:
                tmp_new = bpy.context.scene.cursor_location[bpy.context.scene.is_sliced_ind]
                tmp_old = bpy.context.scene.last_cursor_location[bpy.context.scene.is_sliced_ind]
                if abs(tmp_new - tmp_old) > 0.005:
                    _addon().clear_slice()
        except:
            pass


def cursor_is_snapped():
    return bpy.context.scene.cursor_is_snapped


def snap_cursor(flag=None, objects_names=mu.INF_HEMIS, use_shape_keys=True, set_snap_cursor_to_true=True):
    flag = not bpy.context.scene.cursor_is_snapped if flag is None else flag
    if flag:
        closest_mesh_name, vertex_ind, vertex_co = _addon().find_closest_vertex_index_and_mesh(
            use_shape_keys=use_shape_keys, objects_names=objects_names)
        bpy.context.scene.cursor_location = vertex_co
        set_cursor_pos()
        set_closest_vertex_and_mesh_to_cursor(vertex_ind, closest_mesh_name, set_snap_cursor_to_true)

        activity_values = _addon().get_activity_values(closest_mesh_name)
        if activity_values is not None and len(activity_values) > vertex_ind:
            _addon().set_vertex_data(activity_values[vertex_ind])
        # print(closest_mesh_name, vertex_ind, vertex_co)
        return vertex_ind, closest_mesh_name
    else:
        clear_closet_vertex_and_mesh_to_cursor()
        return None, None


def set_closest_vertex_and_mesh_to_cursor(vertex_ind, closest_mesh_name, set_snap_cursor_to_true=True):
    AppearanceMakerPanel.closest_vertex_to_cursor = vertex_ind
    AppearanceMakerPanel.closest_mesh_to_cursor = closest_mesh_name
    if set_snap_cursor_to_true:
        bpy.context.scene.cursor_is_snapped = True


def get_closest_vertex_and_mesh_to_cursor():
    return AppearanceMakerPanel.closest_vertex_to_cursor, AppearanceMakerPanel.closest_mesh_to_cursor


def clear_closet_vertex_and_mesh_to_cursor():
    AppearanceMakerPanel.closest_vertex_to_cursor = -1
    AppearanceMakerPanel.closest_mesh_to_cursor = ''
    bpy.context.scene.cursor_is_snapped = False


def flat_map_exists():
    return AppearanceMakerPanel.flat_map_exists


bpy.types.Scene.appearance_show_rois_activity = bpy.props.EnumProperty(
    items=[("activity", "Activity maps", "", 0), ("rois", "ROIs", "", 1)], description="Activity maps – The whole brain is one object. \nROIs – Each label is a separate object.\n\nMode",
    update=appearance_show_rois_activity_update)
bpy.types.Scene.subcortical_layer = bpy.props.StringProperty(description="subcortical layer")
bpy.types.Scene.filter_view_type = bpy.props.EnumProperty(
    items=[("rendered", "Rendered Brain", "", 1), ("solid", "Solid Brain", "", 2)],description="Brain appearance",
    update=filter_view_type_update)
# bpy.types.Scene.surface_type = bpy.props.EnumProperty(
#     items=[("pial", "Pial", "", 1), ("inflated", "Inflated", "", 2)],description="Surface type",
#     update=surface_type_update)

try:
    _ = bpy.data.shape_keys['Key'].key_blocks["flat"].value
    flat_exist = True
    bpy.types.Scene.surface_type = bpy.props.EnumProperty(
        items=[("pial", "Pial", "", 1), ("inflated", "Inflated", "", 2), ("flat", "Flat", "", 3)],
        description="Brain view", update=surface_type_update)
    bpy.types.Scene.inflating = bpy.props.FloatProperty(min=-1, max=1, default=0, step=0.1, update=inflating_update,
        description='Sets the value between Pial view (value = -1.00), Inflated view (value = 0.00) and Flat view (value = 1.00).'
                    '\n\nScript: mmvt.appearance.get_inflated_ratio() and set_inflated_ratio(ratio)')
except:
    flat_exist = False
    bpy.types.Scene.surface_type = bpy.props.EnumProperty(
        items=[("pial", "Pial", "", 1), ("inflated", "Inflated", "", 2)],
        description="Brain view", update=surface_type_update)
    bpy.types.Scene.inflating = bpy.props.FloatProperty(min=-1, max=0, default=0, step=0.1, update=inflating_update,
        description='Sets the value between Pial view (value = -1.00), Inflated view (value = 0.00) and Flat view (value = 1.00)'
                    '\n\nScript: mmvt.appearance.get_inflated_ratio() and set_inflated_ratio(ratio)')


bpy.types.Scene.cursor_is_snapped = bpy.props.BoolProperty(default=False, description='The cross stays on the cortex when clicked')
bpy.types.Scene.show_hide_electrodes = bpy.props.BoolProperty(default=False)
bpy.types.Scene.show_hide_eeg_sensors = bpy.props.BoolProperty(default=False)
bpy.types.Scene.show_hide_meg_sensors = bpy.props.BoolProperty(default=False)
bpy.types.Scene.show_hide_connections = bpy.props.BoolProperty(default=False)
# bpy.types.Scene.inflating = bpy.props.FloatProperty(min=0, max=1, default=0, update=inflating_update)
# bpy.types.Scene.inflating = bpy.props.FloatProperty(min=-1, max=1, default=0, step=0.1, update=inflating_update)
bpy.types.Scene.hemis_inf_distance = bpy.props.FloatProperty(min=-5, max=5, default=0, update=hemis_inf_distance_update)
bpy.types.Scene.hemis_distance = bpy.props.FloatProperty(min=0, max=5, default=0, update=hemis_distance_update,
    description = 'Sets the distance value between the hemispheres')
bpy.types.Scene.show_appearance_settings = bpy.props.BoolProperty(default=False)
bpy.types.Scene.panels_background_color = bpy.props.FloatVectorProperty(
    name="object_color", subtype='COLOR', default=(0, 0, 0), min=0.0, max=1.0, update=panels_background_color_update,
    description='Changes the background of the brain display section. '
                '\n\nScript: mmvt.appearance.get_panels_background_color() and set_panels_background_color()')


class SnapCursor(bpy.types.Operator):
    bl_idname = "mmvt.snap_cursor"
    bl_label = "mmvt snap_cursor"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        snap_cursor()
        return {"FINISHED"}


class ShowHideMEGSensors(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_meg_sensors"
    bl_label = "mmvt show_hide_meg_sensors"
    bl_description = 'Show/Hide MEG sensors. \n\nScript: mmvt.appearance.show_hide_meg_sensors()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.show_hide_meg_sensors = not bpy.context.scene.show_hide_meg_sensors
        show_hide_meg_sensors(bpy.context.scene.show_hide_meg_sensors)
        return {"FINISHED"}


class ShowHideEEGSensors(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_eeg_sensors"
    bl_label = "mmvt show_hide_eeg_sensors"
    bl_description = 'Show/Hide EEG sensors. \n\nScript: mmvt.appearance.shoe_hide_eeg()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.show_hide_eeg_sensors = not bpy.context.scene.show_hide_eeg_sensors
        show_hide_eeg_sensors(bpy.context.scene.show_hide_eeg_sensors)
        return {"FINISHED"}


class ShowHideElectrodes(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_elctrodes"
    bl_label = "mmvt show_hide_electrodes"
    bl_description = 'Show/Hide electrodes. \n\nScript: mmvt.appearance.show_hide_electrodes()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.show_hide_electrodes = not bpy.context.scene.show_hide_electrodes
        show_hide_electrodes(bpy.context.scene.show_hide_electrodes)
        return {"FINISHED"}


class ShowHideConnections(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_connections"
    bl_label = "mmvt show_hide_connections"
    bl_description = 'Show/Hide MEG sensors. \n\nScript: mmvt.appearance.show_hide_connections()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.show_hide_connections = not bpy.context.scene.show_hide_connections
        show_hide_connections(bpy.context.scene.show_hide_connections)
        return {"FINISHED"}


class AppearanceMakerPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Appearance"
    addon = None
    init = False
    init = False
    cortex_inflated_rh = 0
    cortex_inflated_lh = 0
    cortex_rh = 0
    cortex_lh = 0
    showing_meg_sensors = False
    showing_eeg_sensors = False
    showing_electrodes = False
    closest_vertex_to_cursor = -1
    closest_mesh_to_cursor = ''
    has_flatmap = False
    no_surface_type_update = False

    def draw(self, context):
        if AppearanceMakerPanel.init:
            appearance_draw(self, context)


def init(addon):
    AppearanceMakerPanel.addon = addon
    register()
    AppearanceMakerPanel.init = True
    bpy.context.scene.subcortical_layer = 'fmri'
    change_to_solid_brain()
    # show_rois()
    loc_val = 0 #5
    AppearanceMakerPanel.flat_map_exists = True
    bpy.context.scene.show_appearance_settings = False
    if bpy.data.objects.get('Cortex-inflated-rh') and bpy.data.objects.get('inflated_rh'):
        AppearanceMakerPanel.cortex_inflated_rh = bpy.data.objects['Cortex-inflated-rh'].location[0] = \
            bpy.data.objects['inflated_rh'].location[0] = loc_val
        AppearanceMakerPanel.cortex_inflated_lh = bpy.data.objects['Cortex-inflated-lh'].location[0] = \
            bpy.data.objects['inflated_lh'].location[0] = -1*loc_val
        try:
            bpy.data.shape_keys['Key'].key_blocks["flat"].value = 0
            bpy.data.shape_keys['Key.001'].key_blocks["flat"].value = 0
        except:
            print('No flat mapping.')
            AppearanceMakerPanel.flat_map_exists = False
        try:
            bpy.data.shape_keys['Key'].key_blocks["inflated"].value = 1
            bpy.data.shape_keys['Key.001'].key_blocks["inflated"].value = 1
        except:
            AppearanceMakerPanel.flat_map_exists = False
            print('No inflated mapping.')

        for hemi in ['lh', 'rh']:
            try:
                mu.get_hemi_obj(hemi).modifiers['mask_bad_vertices'].show_viewport = True
                mu.get_hemi_obj(hemi).modifiers['mask_bad_vertices'].show_render = True
            except:
                pass
    if bpy.data.objects.get('Cortex-rh') and bpy.data.objects.get('lh'):
        AppearanceMakerPanel.cortex_rh = bpy.data.objects['Cortex-rh'].location[0] = \
            bpy.data.objects['rh'].location[0] = 0
        AppearanceMakerPanel.cortex_lh = bpy.data.objects['Cortex-lh'].location[0] = \
            bpy.data.objects['rh'].location[0] = 0
    bpy.context.scene.hemis_distance = 0
    bpy.context.scene.hemis_inf_distance = 0 #-5
    bpy.context.scene.cursor_is_snapped = True
    # set_inflated_ratio(0)
    appearance_show_rois_activity_update()
    AppearanceMakerPanel.showing_meg_sensors = showing_meg_sensors()
    AppearanceMakerPanel.showing_eeg_sensors = showing_eeg()
    AppearanceMakerPanel.showing_electrodes = showing_electordes()
    # AppearanceMakerPanel.mesh = {hemi:mu.get_hemi_obj(hemi).to_mesh(bpy.context.scene, True, 'PREVIEW')
    #                              for hemi in mu.HEMIS}
    # show_inflated()
    bpy.context.scene.panels_background_color = [0, 0, 0]
    snap_cursor(True)
    AppearanceMakerPanel.init = True

    # bpy.data.objects['lh'].hide = True
    # bpy.data.objects['rh'].hide = True
    # bpy.data.objects['lh'].hide_render = True
    # bpy.data.objects['rh'].hide_render = True


def register():
    try:
        bpy.utils.register_class(AppearanceMakerPanel)
        bpy.utils.register_class(ShowHideMEGSensors)
        bpy.utils.register_class(ShowHideElectrodes)
        bpy.utils.register_class(ShowHideEEGSensors)
        bpy.utils.register_class(ShowHideConnections)
        bpy.utils.register_class(SelectionListener)
        bpy.utils.register_class(SnapCursor)
        bpy.ops.mmvt.selection_listener()
    except:
        print("Can't register Appearance Panel!")
        print(traceback.format_exc())


def unregister():
    try:
        bpy.utils.unregister_class(AppearanceMakerPanel)
        bpy.utils.unregister_class(ShowHideMEGSensors)
        bpy.utils.unregister_class(ShowHideElectrodes)
        bpy.utils.unregister_class(ShowHideEEGSensors)
        bpy.utils.unregister_class(ShowHideConnections)
        bpy.utils.unregister_class(SelectionListener)
        bpy.utils.unregister_class(SnapCursor)
    except:
        pass

