# coding=utf-8
import bpy
import mmvt_utils as mu
import mathutils
import math
import numpy as np
import glob
import os.path as op
import re

(ROT_SAGITTAL_LEFT, ROT_SAGITTAL_RIGHT, ROT_CORONAL_ANTERIOR, ROT_CORONAL_POSTERIOR, ROT_AXIAL_SUPERIOR,
 ROT_AXIAL_INFERIOR, ROT_MEDIAL_LEFT, ROT_MEDIAL_RIGHT) = range(8)


ROT_45 = np.sin(np.deg2rad(45)) # np.rad2deg(np.arcsin(0.7071068286895752)) = 45
SAGITTAL_LEFT = [0.5, 0.5, -0.5, -0.5]
SAGITTAL_RIGHT = [0.5, 0.5, 0.5, 0.5]
CORONAL_ANTERIOR = [0.0, 0.0, ROT_45, ROT_45]
CORONAL_POSTERIOR = [ROT_45, ROT_45, 0.0, 0.0]
AXIAL_SUPERIOR = (0.6829140186309814, -0.007170889526605606, 0.007669730577617884, -0.7304232716560364)
AXIAL_INFERIOR = (0.015227699652314186, 0.7250200510025024, 0.6884075403213501, 0.014458661898970604)
'''
Originally:
CORONAL_ANTERIOR = [1, 0, 0, 0]
CORONAL_POSTERIOR = [0, 1, 0, 0]
The current rotation is after rotating it in 45 in the z(?) axis
https://www.mathworks.com/matlabcentral/answers/123763-how-to-rotate-entire-3d-data-with-x-y-z-values-along-a-particular-axis-say-x-axis
'''
# todo: change those ugly numbers to an equation like in the link

ANGLES_DICT = {
    ROT_SAGITTAL_LEFT: SAGITTAL_LEFT,
    ROT_SAGITTAL_RIGHT: SAGITTAL_RIGHT,
    ROT_CORONAL_ANTERIOR: CORONAL_ANTERIOR,
    ROT_CORONAL_POSTERIOR: CORONAL_POSTERIOR,
    ROT_AXIAL_SUPERIOR: AXIAL_SUPERIOR,
    ROT_AXIAL_INFERIOR: AXIAL_INFERIOR,
    ROT_MEDIAL_LEFT: None,
    ROT_MEDIAL_RIGHT: None
}
ANGLES_NAMES_DICT = {
    ROT_SAGITTAL_LEFT: 'left',
    ROT_SAGITTAL_RIGHT: 'right',
    ROT_CORONAL_ANTERIOR: 'anterior',
    ROT_CORONAL_POSTERIOR: 'posterior',
    ROT_AXIAL_SUPERIOR: 'superior',
    ROT_AXIAL_INFERIOR: 'inferior',
    ROT_MEDIAL_LEFT: 'left_medial',
    ROT_MEDIAL_RIGHT: 'right_medial'
}


def _addon():
    return ShowHideObjectsPanel.addon


def rotate_view(view_ang):
    rotation_in_quaternions = ANGLES_DICT.get(view_ang, '')
    if rotation_in_quaternions != '':
        if view_ang == ROT_MEDIAL_LEFT:
            _addon().hide_hemi('rh')
            _addon().show_hemi('lh')
            mu.rotate_view3d(ANGLES_DICT[ROT_SAGITTAL_RIGHT])
        elif view_ang == ROT_MEDIAL_RIGHT:
            _addon().show_hemi('rh')
            _addon().hide_hemi('lh')
            mu.rotate_view3d(ANGLES_DICT[ROT_SAGITTAL_LEFT])
        else:
            mu.rotate_view3d(rotation_in_quaternions)
    else:
        print('angle should be one of ROT_SAGITTAL_LEFT, ROT_SAGITTAL_RIGHT, ROT_CORONAL_ANTERIOR, ' + \
              'ROT_CORONAL_POSTERIOR, ROT_AXIAL_SUPERIOR, ROT_AXIAL_INFERIOR,ROT_MEDIAL_LEFT,ROT_MEDIAL_RIGHT')


def view_name(view):
    if mu.get_hemi_obj('rh').hide and not mu.get_hemi_obj('lh').hide:
        hemi = 'lh'
    elif not mu.get_hemi_obj('rh').hide and mu.get_hemi_obj('lh').hide:
        hemi = 'rh'
    elif not mu.get_hemi_obj('rh').hide and not mu.get_hemi_obj('lh').hide:
        hemi = 'both'
    if (hemi == 'rh' and view == ROT_SAGITTAL_LEFT) or (hemi == 'lh' and view == ROT_SAGITTAL_RIGHT):
        view_name = 'medial'
    elif (hemi == 'lh' and view == ROT_SAGITTAL_LEFT) or (hemi == 'rh' and view == ROT_SAGITTAL_RIGHT):
        view_name = 'lateral'
    else:
        view_name = ANGLES_NAMES_DICT[view]
    return view_name


def zoom(delta):
    c = mu.get_view3d_context()
    bpy.ops.view3d.zoom(c, delta=delta)


def view_all():
    c = mu.get_view3d_context()
    bpy.ops.view3d.view_all(c)
    zoom(1)
    # bpy.ops.view3d.localview(c)


def rotate_brain(dx=None, dy=None, dz=None, keep_rotating=False, save_image=False, render_image=False):
    dx = bpy.context.scene.rotate_dx if dx is None else dx
    dy = bpy.context.scene.rotate_dy if dy is None else dy
    dz = bpy.context.scene.rotate_dz if dz is None else dz
    ShowHideObjectsPanel.rotate_dxyz += np.array([dx, dy, dz])
    bpy.context.scene.rotate_dx, bpy.context.scene.rotate_dy, bpy.context.scene.rotate_dz = dx, dy, dz
    rv3d = mu.get_view3d_region()
    rv3d.view_rotation.rotate(mathutils.Euler((math.radians(d) for d in (dx, dy, dz))))
    if bpy.context.scene.rotate_and_save or save_image:
        _addon().save_image('rotation', view_selected=bpy.context.scene.save_selected_view)
    # if bpy.context.scene.rotate_and_render or render_image:
    #     _addon().render_image('rotation')
    if bpy.context.scene.rotate_360 and any([ShowHideObjectsPanel.rotate_dxyz[k] >= 360 for k in range(3)]):
        stop_rotating()
    elif keep_rotating:
        start_rotating()


def set_rotate_brain(dx=0, dy=0, dz=0):
    bpy.context.scene.rotate_dx, bpy.context.scene.rotate_dy, bpy.context.scene.rotate_dz = dx, dy, dz


# def view_all():
#     c = mu.get_view3d_context()
#     bpy.ops.view3d.view_all(c)


def start_rotating():
    bpy.context.scene.rotate_brain = True


def stop_rotating():
    bpy.context.scene.rotate_brain = False


def get_rotate_dxyz():
    return ShowHideObjectsPanel.rotate_dxyz


def rotate_brain_update(self, context):
    if not bpy.context.scene.rotate_brain:
        ShowHideObjectsPanel.rotate_dxyz = np.array([0., 0., 0.])


def show_only_redner_update(self, context):
    mu.show_only_render(bpy.context.scene.show_only_render)


def show_hide_cerebellum_update(self, context):
    set_show_hide_cerebellum(context.scene.show_hide_cerebellum)


def set_show_hide_cerebellum(val):
    obj_names = [
        'Left-Cerebellum-Cortex', 'Right-Cerebellum-Cortex',
        'Left-Cerebellum-Cortex_fmri_activity', 'Right-Cerebellum-Cortex_fmri_activity',
        'Left-Cerebellum-Cortex_meg_activity', 'Right-Cerebellum-Cortex_meg_activity']
    for obj_name in obj_names:
        show_hide_hierarchy(not val, obj_name)


def show_cerebellum():
    bpy.context.scene.show_hide_cerebellum = True


def hide_cerebellum():
    bpy.context.scene.show_hide_cerebellum = False


def show_hide_hierarchy(do_hide, obj_name, hemi='both'):
    if bpy.data.objects.get(obj_name) is not None:
        obj = bpy.data.objects[obj_name]
        # hide_obj(obj, do_hide)
        show_hide_obj(do_hide, obj, hemi)
        for child in obj.children:
            show_hide_obj(do_hide, child, hemi)
            # hide_obj(child, do_hide)


def show_hide_obj(do_hide, obj, hemi='both'):
    if hemi == 'both':
        hide_obj(obj, do_hide)
    else:
        if (hemi == 'rh' and ('rh' in obj.name or 'Right' in obj.name)) or \
                (hemi == 'lh' and ('lh' in obj.name or 'Left' in obj.name)):
            hide_obj(obj, do_hide)
        # elif 'rh' not in obj.name and 'lh' not in obj.name and 'Right' not in obj.name and 'Left' not in obj.name:
        #     hide_obj(obj, do_hide)


def get_hierarchy_show(obj_name, show=True):
    all_show = []
    if bpy.data.objects.get(obj_name) is not None:
        obj = bpy.data.objects[obj_name]
        all_show.append(not obj.hide)
        for child in obj.children:
            all_show.append(not child.hide)
    return all(all_show) if show else not all(all_show)


def show_hide_hemi(val, hemi):
    show_hide_hierarchy(val, 'Cortex-{}'.format(hemi))
    show_hide_hierarchy(val, 'Cortex-inflated-{}'.format(hemi))
    # for obj_name in [hemi, 'inflated_{}'.format(hemi)]:
    obj_name = 'inflated_{}'.format(hemi)
    if bpy.data.objects.get(obj_name) is not None:
        hide_obj(bpy.data.objects[obj_name], val)


def hide_hemi(hemi):
    show_hide_hemi(True, hemi)


def show_hemi(hemi):
    show_hide_hemi(False, hemi)


def show_hemis():
    for hemi in mu.HEMIS:
        show_hide_hemi(False, hemi)
    # for obj_name in ['Cortex-inflated-rh', 'Cortex-inflated-lh']: # 'rh', 'lh'
    #     show_hide_hierarchy(False, obj_name)


def hide_hemis():
    for hemi in mu.HEMIS:
        show_hide_hemi(True, hemi)


def hide_obj(obj, val=True):
    obj.hide = val
    obj.hide_render = val


def show_hide_sub_cortical_update(self, context):
    show_hide_sub_corticals(bpy.context.scene.objects_show_hide_sub_cortical)


def hide_subcorticals():
    show_hide_sub_corticals(True)


def show_subcorticals():
    show_hide_sub_corticals(False)


def subcorticals_are_hiding():
    return get_hierarchy_show('Subcortical_structures', False)
    # return bpy.context.scene.objects_show_hide_sub_cortical


def show_hide_sub_corticals(do_hide=True, hemi='both'):
    show_hide_hierarchy(do_hide, "Subcortical_structures", hemi)
    # show_hide_hierarchy(bpy.context.scene.objects_show_hide_sub_cortical, "Subcortical_activity_map")
    # We split the activity map into two types: meg for the same activation for the each structure, and fmri
    # for a better resolution, like on the cortex.
    if not do_hide:
        fmri_show = bpy.context.scene.subcortical_layer == 'fmri'
        meg_show = bpy.context.scene.subcortical_layer == 'meg'
        show_hide_hierarchy(not fmri_show, "Subcortical_fmri_activity_map", hemi)
        show_hide_hierarchy(not meg_show, "Subcortical_meg_activity_map", hemi)
    else:
        show_hide_hierarchy(True, "Subcortical_fmri_activity_map", hemi)
        show_hide_hierarchy(True, "Subcortical_meg_activity_map", hemi)


# def flip_camera_ortho_view():
#     options = ['ORTHO', 'CAMERA']
#     bpy.types.Scene.in_camera_view = not bpy.types.Scene.in_camera_view
#     mu.get_view3d_region().view_perspective = options[
#         int(bpy.types.Scene.in_camera_view)]


def show_sagital(direction=None):
    if bpy.types.Scene.in_camera_view and bpy.data.objects.get("Camera_empty") is not None:
        if mu.get_time_from_event(mu.get_time_obj()) > 2 or bpy.context.scene.current_view != 'sagittal':
            bpy.data.objects["Camera_empty"].rotation_euler = [0.0, 0.0, np.pi / 2]
            bpy.context.scene.current_view = 'sagittal'
            bpy.context.scene.current_view_flip = 0
        else:
            if bpy.context.scene.current_view_flip == 1:
                bpy.data.objects["Camera_empty"].rotation_euler = [0.0, 0.0, np.pi / 2]
            else:
                # print('in ShowSagittal else')
                bpy.data.objects["Camera_empty"].rotation_euler = [0.0, 0.0, -np.pi / 2]
            bpy.context.scene.current_view_flip = not bpy.context.scene.current_view_flip
            # ShowHideObjectsPanel.time_of_view_selection = mu.get_time_obj()
    else:
        mu.get_view3d_region().view_perspective = 'ORTHO'
        if direction in ['left', 'right']:
            bpy.context.scene.current_view = 'sagittal'
            if direction == 'left':
                mu.rotate_view3d(SAGITTAL_LEFT)
            else:
                mu.rotate_view3d(SAGITTAL_RIGHT)
        elif mu.get_time_from_event(mu.get_time_obj()) > 2 or bpy.context.scene.current_view != 'sagittal':
            mu.rotate_view3d(SAGITTAL_LEFT)
            bpy.context.scene.current_view = 'sagittal'
            bpy.context.scene.current_view_flip = False
        else:
            mu.rotate_view3d(SAGITTAL_LEFT) if bpy.context.scene.current_view_flip else mu.rotate_view3d(SAGITTAL_RIGHT)
            bpy.context.scene.current_view_flip = not bpy.context.scene.current_view_flip

    # view_all()
    # zoom(-1)
    ShowHideObjectsPanel.time_of_view_selection = mu.get_time_obj()


def show_coronal(show_frontal=False):
    if show_frontal:
        mu.rotate_view3d(CORONAL_ANTERIOR)
        bpy.context.scene.current_view = 'coronal'
        bpy.context.scene.current_view_flip = 0
        return

    if bpy.types.Scene.in_camera_view and bpy.data.objects.get("Camera_empty") is not None:
        if mu.get_time_from_event(mu.get_time_obj()) > 2 or bpy.context.scene.current_view != 'coronal':
            bpy.data.objects["Camera_empty"].rotation_euler = [0.0, 0.0, np.pi]
            bpy.context.scene.current_view = 'coronal'
            bpy.context.scene.current_view_flip = 0
        else:
            if bpy.context.scene.current_view_flip == 1:
                bpy.data.objects["Camera_empty"].rotation_euler = [0.0, 0.0, np.pi]
            else:
                # print('in ShowCoronal else')
                bpy.data.objects["Camera_empty"].rotation_euler = [0.0, 0.0, 0.0]
            bpy.context.scene.current_view_flip = not bpy.context.scene.current_view_flip
        ShowHideObjectsPanel.time_of_view_selection = mu.get_time_obj()
    else:
        mu.get_view3d_region().view_perspective = 'ORTHO'
        if mu.get_time_from_event(mu.get_time_obj()) > 2 or bpy.context.scene.current_view != 'coronal':
            mu.rotate_view3d(CORONAL_ANTERIOR)
            bpy.context.scene.current_view = 'coronal'
            bpy.context.scene.current_view_flip = False
        else:
            mu.rotate_view3d(CORONAL_ANTERIOR) if bpy.context.scene.current_view_flip else mu.rotate_view3d(CORONAL_POSTERIOR)
            bpy.context.scene.current_view_flip = not bpy.context.scene.current_view_flip
        ShowHideObjectsPanel.time_of_view_selection = mu.get_time_obj()
        # print(bpy.ops.view3d.viewnumpad())
    # view_all()
    # zoom(-1)


def show_axial():
    if bpy.types.Scene.in_camera_view and bpy.data.objects.get("Camera_empty") is not None:
        if mu.get_time_from_event(mu.get_time_obj()) > 2 or bpy.context.scene.current_view != 'axial':
            bpy.data.objects["Camera_empty"].rotation_euler = [np.pi / 2, 0.0, np.pi]
            bpy.context.scene.current_view = 'axial'
            bpy.context.scene.current_view_flip = 0
        else:
            if bpy.context.scene.current_view_flip == 1:
                bpy.data.objects["Camera_empty"].rotation_euler = [np.pi / 2, 0.0, np.pi]
            else:
                # print('in ShowAxial else')
                bpy.data.objects["Camera_empty"].rotation_euler = [-np.pi / 2, 0.0, np.pi]
            bpy.context.scene.current_view_flip = not bpy.context.scene.current_view_flip
        ShowHideObjectsPanel.time_of_view_selection = mu.get_time_obj()
    else:
        mu.get_view3d_region().view_perspective = 'ORTHO'
        # todo: first term is always False...
        if mu.get_time_from_event(mu.get_time_obj()) > 2 or bpy.context.scene.current_view != 'axial':
            mu.get_view3d_region().view_rotation = AXIAL_SUPERIOR # [1, 0, 0, 0]
            bpy.context.scene.current_view = 'axial'
            bpy.context.scene.current_view_flip = 0
        else:
            mu.rotate_view3d(AXIAL_SUPERIOR) if bpy.context.scene.current_view_flip else mu.rotate_view3d(AXIAL_INFERIOR)
            bpy.context.scene.current_view_flip = not bpy.context.scene.current_view_flip
        ShowHideObjectsPanel.time_of_view_selection = mu.get_time_obj()
    # view_all()
    # zoom(-1)


def set_normal_view():
    split_view(0)
    ShowHideObjectsPanel.split_view = 0


def _split_view():
    ShowHideObjectsPanel.split_view += 1
    if ShowHideObjectsPanel.split_view == 3:
        ShowHideObjectsPanel.split_view = 0
        _addon().appearance.show_electrodes(ShowHideObjectsPanel.electrodes_are_shown)
    elif ShowHideObjectsPanel.split_view == 1:
        ShowHideObjectsPanel.electrodes_are_shown = _addon().appearance.showing_electordes()
        _addon().appearance.hide_electrodes()
    view = ShowHideObjectsPanel.split_view
    split_view(view)
    if bpy.context.scene.render_split:
        names = {0:'normal', 1:'split_lateral', 2:'split_medial'}
        _addon().save_image(names[view])


@mu.tryit()
def split_view(view):
    import math
    if not ShowHideObjectsPanel.init:
        return
    if view != 0:
        _addon().hide_subcorticals()
    pial_shift, inflated_shift = 10, 15
    shift = pial_shift + (bpy.context.scene.inflating + 1) * (inflated_shift - pial_shift)
    bpy.context.scene.cursor_is_snapped = view == 0
    if view == 0:  # Normal
        # show_coronal()
        mu.set_zoom_level(bpy.context.scene.surface_type, relative=1)
        # if _addon().is_inflated():
        bpy.data.objects['inflated_lh'].location[0] = 0
        bpy.data.objects['inflated_lh'].rotation_euler[2] = 0
        bpy.data.objects['inflated_rh'].location[0] = 0
        bpy.data.objects['inflated_rh'].rotation_euler[2] = 0
    elif view == 1:  # Split lateral
        show_coronal(show_frontal=True)
        mu.set_zoom_level(bpy.context.scene.surface_type, relative=1, split=True)
        # lateral split view
        # inflated_lh: loc  x:13, rot z: -90
        # inflated_lr: loc  x:-13, rot z: 90
        bpy.data.objects['inflated_lh'].location[0] = shift
        bpy.data.objects['inflated_lh'].rotation_euler[2] = -math.pi / 2
        bpy.data.objects['inflated_rh'].location[0] = -shift
        bpy.data.objects['inflated_rh'].rotation_euler[2] = math.pi / 2
    elif view == 2:
        # medial split medial
        # inflated_lh: loc  x:13, rot z: 90
        # inflated_lr: loc  x:-13, rot z: -90
        bpy.data.objects['inflated_lh'].location[0] = shift
        bpy.data.objects['inflated_lh'].rotation_euler[2] = math.pi / 2
        bpy.data.objects['inflated_rh'].location[0] = -shift
        bpy.data.objects['inflated_rh'].rotation_euler[2] = -math.pi / 2


def maximize_brain():
    context = mu.get_view3d_context()
    bpy.ops.screen.screen_full_area(context)


def minimize_brain():
    context = mu.get_view3d_context()
    bpy.ops.screen.back_to_previous(context)


class CenterView(bpy.types.Operator):
    bl_idname = "mmvt.center_view"
    bl_label = "mmvt center_view"
    bl_description = 'Moves the brain back to the center of the window. \n\nScript: mmvt.show_hide.mu.center_view()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        mu.center_view()
        return {"FINISHED"}


class ShowSagittal(bpy.types.Operator):
    bl_idname = "mmvt.show_sagittal"
    bl_label = "mmvt show_sagittal"
    bl_description = 'Moves the brain to an Sagital view. \n\nScript: mmvt.show_hide.show_sagital()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        show_sagital()
        return {"FINISHED"}


class ShowCoronal(bpy.types.Operator):
    bl_idname = "mmvt.show_coronal"
    bl_label = "mmvt show_coronal"
    bl_description = 'Moves the brain to an Coronal view. \n\nScript: mmvt.show_hide.show_coronal()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        show_coronal()
        return {"FINISHED"}


class MaxMinBrain(bpy.types.Operator):
    bl_idname = "mmvt.max_min_brain"
    bl_label = "mmvt max_min_brain"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        if bpy.context.scene.brain_max_min:
            maximize_brain()
        else:
            minimize_brain()
        bpy.context.scene.brain_max_min = not bpy.context.scene.brain_max_min
        return {"FINISHED"}


class SplitView(bpy.types.Operator):
    bl_idname = "mmvt.split_view"
    bl_label = "mmvt split view"
    bl_description = 'Split Lateral – Splits the hemispheres into lateral view.' \
                     '\nSplit Medial – Turns the hemispheres into medial view.' \
                     '\nNormal View - Changes the brain back to regular view. ' \
                     '\n\nScript: mmvt.show_hide._split_view()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        _split_view()
        return {"FINISHED"}


class ShowAxial(bpy.types.Operator):
    bl_idname = "mmvt.show_axial"
    bl_label = "mmvt show_axial"
    bl_description = 'Moves the brain to an Axial view. \n\nScript: mmvt.show_hide.show_axial()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        show_axial()
        return {"FINISHED"}




# class FlipCameraView(bpy.types.Operator):
#     bl_idname = "mmvt.flip_camera_view"
#     bl_label = "mmvt flip camera view"
#     bl_options = {"UNDO"}
#
#     @staticmethod
#     def invoke(self, context, event=None):
#         flip_camera_ortho_view()
#         return {"FINISHED"}


class ShowHideLH(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_lh"
    bl_label = "mmvt show_hide_lh"
    bl_description = 'Hide/Show left hemisphere. \n\nScript: mmvt.show_hide.show_hide_hemi()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.objects_show_hide_lh = not bpy.context.scene.objects_show_hide_lh
        show_hide_hemi(bpy.context.scene.objects_show_hide_lh, 'lh')
        return {"FINISHED"}


class ShowHideRH(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_rh"
    bl_label = "mmvt show_hide_rh"
    bl_description = 'Hide/Show right hemisphere. \n\nScript: mmvt.show_hide.show_hide_hemi()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.objects_show_hide_rh = not bpy.context.scene.objects_show_hide_rh
        show_hide_hemi(bpy.context.scene.objects_show_hide_rh, 'rh')
        return {"FINISHED"}


class ShowHideSubCorticals(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_sub"
    bl_label = "mmvt show_hide_sub"
    bl_description = 'Hide/Show subcortical region. \n\nScript: mmvt.show_hide.show_hide_sub_corticals()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.objects_show_hide_sub_cortical = \
            bpy.context.scene.objects_show_hide_rh_subs = \
            bpy.context.scene.objects_show_hide_lh_subs = \
            bpy.context.scene.show_hide_cerebellum = \
            not bpy.context.scene.objects_show_hide_sub_cortical
        show_hide_sub_corticals(bpy.context.scene.objects_show_hide_sub_cortical)
        return {"FINISHED"}


class ShowHideLHSubs(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_sub_left"
    bl_label = "mmvt show_hide_sub_left"
    bl_description = 'Hide/Show left side of the subcortical region. \n\nScript: mmvt.show_hide.show_hide_sub_corticals()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.objects_show_hide_lh_subs = not bpy.context.scene.objects_show_hide_lh_subs
        show_hide_sub_corticals(bpy.context.scene.objects_show_hide_lh_subs, 'lh')
        return {"FINISHED"}


class ShowHideRHSubs(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_sub_right"
    bl_label = "mmvt show_hide_sub_right"
    bl_description = 'Hide/Show right side of the subcortical region. \n\nScript: mmvt.show_hide.show_hide_sub_corticals()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.objects_show_hide_rh_subs = not bpy.context.scene.objects_show_hide_rh_subs
        show_hide_sub_corticals(bpy.context.scene.objects_show_hide_rh_subs, 'rh')
        return {"FINISHED"}


def show_head():
    bpy.context.scene.objects_show_hide_head = True
    hide_obj(bpy.data.objects['seghead'], False)


def hide_head():
    bpy.context.scene.objects_show_hide_head = False
    hide_obj(bpy.data.objects['seghead'], True)


class ShowHideHead(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_head"
    bl_label = "mmvt show_hide_head"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.objects_show_hide_head = not bpy.context.scene.objects_show_hide_head
        hide_obj(bpy.data.objects['seghead'], not bpy.context.scene.objects_show_hide_head)
        return {"FINISHED"}


class ShowHideSubCerebellum(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_cerebellum"
    bl_label = "mmvt show_hide_cerebellum"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        bpy.context.scene.objects_show_hide_cerebellum = not bpy.context.scene.objects_show_hide_cerebellum
        show_hide_hierarchy(bpy.context.scene.objects_show_hide_cerebellum, 'Cerebellum')
        show_hide_hierarchy(bpy.context.scene.objects_show_hide_cerebellum, 'Cerebellum_fmri_activity_map')
        show_hide_hierarchy(bpy.context.scene.objects_show_hide_cerebellum, 'Cerebellum_meg_activity_map')
        return {"FINISHED"}


class ShowHideObjectsPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Show Hide Brain"
    addon = None
    init = False
    split_view = 0
    split_view_text = {0:'Split Lateral', 1:'Split Medial', 2:'Normal view'}
    electrodes_are_shown = False
    time_of_view_selection = mu.get_time_obj
    rotate_dxyz = np.array([0., 0., 0.])

    def draw(self, context):
        if not ShowHideObjectsPanel.init:
            return
        layout = self.layout
        vis = dict(Right = not bpy.context.scene.objects_show_hide_rh,
                   Left = not bpy.context.scene.objects_show_hide_lh)
        vis_subs = dict(Right = not bpy.context.scene.objects_show_hide_rh_subs,
                        Left = not bpy.context.scene.objects_show_hide_lh_subs)
        show_hide_icon = dict(show='RESTRICT_VIEW_OFF', hide='RESTRICT_VIEW_ON')
        row = layout.row(align=True)
        for hemi in ['Left', 'Right']:
            action = 'show' if vis[hemi] else 'hide'
            show_text = '{} {}'.format('Hide' if vis[hemi] else 'Show', hemi)
            show_icon = show_hide_icon[action]
            bl_idname = ShowHideLH.bl_idname if hemi == 'Left' else ShowHideRH.bl_idname
            row.operator(bl_idname, text=show_text, icon=show_icon)

        subs_exist = bpy.data.objects.get('Subcortical_structures', None) is not None and \
                     len(bpy.data.objects['Subcortical_structures'].children) > 0
        if _addon().is_pial() and subs_exist:
            sub_vis = not bpy.context.scene.objects_show_hide_sub_cortical
            sub_show_text = '{} Subcorticals'.format('Hide' if sub_vis else 'Show')
            sub_icon = show_hide_icon['show' if sub_vis else 'hide']
            if not context.scene.hide_half_subcorticals:
                layout.operator(ShowHideSubCorticals.bl_idname, text=sub_show_text, icon=sub_icon)
            else:
                row = layout.row(align=True)
                for hemi in ['Left', 'Right']:
                    action = 'show' if vis_subs[hemi] else 'hide'
                    show_text = '{} {} Subcorticals'.format('Hide' if vis_subs[hemi] else 'Show', hemi)
                    show_icon = show_hide_icon[action]
                    bl_idname = ShowHideLHSubs.bl_idname if hemi == 'Left' else ShowHideRHSubs.bl_idname
                    row.operator(bl_idname, text=show_text, icon=show_icon)
            if context.scene.show_hide_settings:
                layout.prop(context.scene, 'hide_half_subcorticals', text='{} only one side'.format(
                    'Hide' if sub_vis else 'Show'))
        if context.scene.show_hide_settings:
            layout.prop(context.scene, 'show_hide_cerebellum', text='Show Cerebellum')

        if bpy.data.objects.get('seghead', None) is not None and bpy.context.scene.show_hide_settings:
            action = 'show' if bpy.context.scene.objects_show_hide_head else 'hide'
            show_text = '{} outer skin'.format('Hide' if bpy.context.scene.objects_show_hide_head else 'Show')
            show_icon = show_hide_icon[action]
            layout.operator(ShowHideHead.bl_idname, text=show_text, icon=show_icon)


        # if bpy.data.objects.get('Cerebellum'):
        #     sub_vis = not bpy.context.scene.objects_show_hide_cerebellum
        #     sub_show_text = '{} Cerebellum'.format('Hide' if sub_vis else 'Show')
        #     sub_icon = show_hide_icon['show' if sub_vis else 'hide']
        #     layout.operator(ShowHideSubCerebellum.bl_idname, text=sub_show_text, icon=sub_icon)
        row = layout.row(align=True)
        row.operator(ShowAxial.bl_idname, text='Axial', icon='AXIS_TOP')
        row.operator(ShowCoronal.bl_idname, text='Coronal', icon='AXIS_FRONT')
        row.operator(ShowSagittal.bl_idname, text='Sagittal', icon='AXIS_SIDE')
        if bpy.context.scene.surface_type != 'flat_map':
            layout.operator(SplitView.bl_idname, text=self.split_view_text[self.split_view], icon='ALIGN')
        # layout.prop(context.scene, 'render_split', text='Render images')
        # layout.operator(MaxMinBrain.bl_idname,
        #                 text="{} Brain".format('Maximize' if bpy.context.scene.brain_max_min else 'Minimize'),
        #                 icon='TRIA_UP' if bpy.context.scene.brain_max_min else 'TRIA_DOWN')
        if context.scene.show_hide_settings:
            col = layout.box().column()
            col.prop(context.scene, 'rotate_brain')
            row = col.row(align=True)
            row.prop(context.scene, 'rotate_dx')
            row.prop(context.scene, 'rotate_dy')
            row.prop(context.scene, 'rotate_dz')
            # row = col.row(align=True)
            col.prop(context.scene, 'rotate_360')
            col.prop(context.scene, 'rotate_and_save')
            # col.prop(context.scene, 'rotate_and_render')

        # views_options = ['Camera', 'Ortho']
        # next_view = views_options[int(bpy.context.scene.in_camera_view)]
        # icons = ['SCENE', 'MANIPUL']
        # next_icon = icons[int(bpy.context.scene.in_camera_view)]
        # row = layout.row(align=True)
        # layout.operator(FlipCameraView.bl_idname, text='Change to {} view'.format(next_view), icon=next_icon)
        layout.operator(CenterView.bl_idname, text='Center View', icon='FREEZE')
        if context.scene.show_hide_settings:
            layout.prop(context.scene, 'show_only_render', text="Show only rendered objects")
        layout.prop(context.scene, 'show_hide_settings', text='More settings')
        # layout.label(text=','.join(['{:.3f}'.format(x) for x in mu.get_view3d_region().view_rotation]))


bpy.types.Scene.objects_show_hide_lh = bpy.props.BoolProperty(
    default=True, description="Show left hemisphere")#,update=show_hide_lh)
bpy.types.Scene.objects_show_hide_rh = bpy.props.BoolProperty(
    default=True, description="Show right hemisphere")#, update=show_hide_rh)
bpy.types.Scene.objects_show_hide_sub_cortical = bpy.props.BoolProperty(
    default=True, description="Show sub cortical")#, update=show_hide_sub_cortical_update)
bpy.types.Scene.objects_show_hide_lh_subs = bpy.props.BoolProperty(
    default=True, description="Show left subcorticals")#,update=show_hide_lh)
bpy.types.Scene.objects_show_hide_rh_subs = bpy.props.BoolProperty(
    default=True, description="Show right subcorticals")#, update=show_hide_rh)
bpy.types.Scene.objects_show_hide_cerebellum = bpy.props.BoolProperty(
    default=True, description="Show Cerebellum")
bpy.types.Scene.objects_show_hide_head = bpy.props.BoolProperty(
    default=True, description="Show head")
bpy.types.Scene.show_hide_cerebellum = bpy.props.BoolProperty(default=False, update=show_hide_cerebellum_update,
    description='Hide/Show the cerebellum')
bpy.types.Scene.show_only_render = bpy.props.BoolProperty(
    default=True, update=show_only_redner_update, description='Removes the crosshairs and other descriptive markers')
bpy.types.Scene.rotate_brain = bpy.props.BoolProperty(default=False, name='Rotate the brain', update=rotate_brain_update,
    description='When the box is checked the brain starts to rotate according the values that were set to the x,y,x '
                'axis below the check box')
bpy.types.Scene.rotate_and_save = bpy.props.BoolProperty(default=False, name='Save an image each rotation',
    description='Saves an image each rotation according the values that were set to the x,y,x axis below the check box. '
                '\nThe pictures are saved inside the ‘figures’ folder under the subjects’ name folder. '
                '\nExample:  ..\ mmvt\mmvt_root\mmvt_blend\colin27\\figures')
bpy.types.Scene.rotate_360 = bpy.props.BoolProperty(default=False, name='Rotate full 360 deg',
    description='Rotates the brain 360 deg and stops when done')
bpy.types.Scene.rotate_and_render = bpy.props.BoolProperty(default=False, name='Render an image each rotation',
    description='Renders an image each rotation according the values that were set to the x,y,x axis below the check box. '
                '\nThe pictures are saved inside the ‘figures’ folder under the subjects’ name folder. '
                '\nExample:  ..\ mmvt\mmvt_root\mmvt_blend\colin27\\figures')
bpy.types.Scene.brain_max_min = bpy.props.BoolProperty()
bpy.types.Scene.render_split = bpy.props.BoolProperty()
bpy.types.Scene.hide_half_subcorticals = bpy.props.BoolProperty(default=False,
    description='Changes the ‘Hide Subcorticals’ button into two buttons which Hide/Show left or right side of the'
                ' subcortical region')
bpy.types.Scene.show_hide_settings = bpy.props.BoolProperty(default=False)

bpy.types.Scene.rotate_dx = bpy.props.FloatProperty(default=0, step=1, name='x',
    description='Sets the value of the x axis for the brain rotation (The brain rotation starts after checking the '
                '‘Rotate The Brain’ check box)')#, min=-0.1, max=0.1, )
bpy.types.Scene.rotate_dy = bpy.props.FloatProperty(default=0, step=1, name='y',
    description='Sets the value of the y axis for the brain rotation (The brain rotation starts after checking the '
                '‘Rotate The Brain’ check box)')#, min=-0.1, max=0.1, )
bpy.types.Scene.rotate_dz = bpy.props.FloatProperty(default=0, step=1, name='z',
    description='Sets the value of the z axis for the brain rotation (The brain rotation starts after checking the '
                '‘Rotate The Brain’ check box)')#, min=-0.1, max=0.1, name='z')


# bpy.types.Scene.current_view = 'free'
bpy.types.Scene.current_view_flip = bpy.props.BoolProperty()
# bpy.types.Scene.in_camera_view = 0
bpy.types.Scene.current_view = bpy.props.EnumProperty(
    items=[("sagittal", "Sagittal", "", 1), ("coronal", "Coronal", "", 2), ("axial", "Axial", "", 3)])


def init(addon):
    ShowHideObjectsPanel.addon = addon
    if bpy.data.objects.get('lh', None) is None:
        print('No brain!')
        return
    bpy.context.scene.objects_show_hide_rh = False
    bpy.context.scene.objects_show_hide_lh = False
    bpy.context.scene.objects_show_hide_sub_cortical = False
    bpy.context.scene.objects_show_hide_rh_subs = \
        bpy.context.scene.objects_show_hide_lh_subs = \
        bpy.context.scene.objects_show_hide_sub_cortical
    bpy.context.scene.hide_half_subcorticals = False
    bpy.context.scene.show_hide_cerebellum = True
    show_hide_sub_corticals(False)
    show_hemis()
    bpy.context.scene.show_only_render = False
    bpy.context.scene.brain_max_min = True
    for fol in ['Cerebellum', 'Cerebellum_fmri_activity_map', 'Cerebellum_meg_activity_map']:
        show_hide_hierarchy(True, fol)
    bpy.context.scene.rotate_brain = False
    bpy.context.scene.rotate_and_save = False
    bpy.context.scene.rotate_and_render = False
    bpy.context.scene.render_split = False
    bpy.context.scene.rotate_dz = 0
    bpy.context.scene.rotate_dx = 0
    bpy.context.scene.rotate_dy = 0
    bpy.context.scene.show_hide_settings = False
    # show_hide_hemi(False, 'rh')
    # show_hide_hemi(False, 'lh')
    # hide_obj(bpy.data.objects[obj_func_name], val)
    # view_all()
    # zoom(-1)

    register()
    ShowHideObjectsPanel.init = True


def register():
    try:
        unregister()
        bpy.utils.register_class(ShowHideObjectsPanel)
        bpy.utils.register_class(ShowHideLH)
        bpy.utils.register_class(ShowHideRH)
        bpy.utils.register_class(ShowSagittal)
        bpy.utils.register_class(ShowCoronal)
        bpy.utils.register_class(ShowAxial)
        bpy.utils.register_class(SplitView)
        bpy.utils.register_class(MaxMinBrain)
        bpy.utils.register_class(CenterView)
        bpy.utils.register_class(ShowHideSubCorticals)
        bpy.utils.register_class(ShowHideLHSubs)
        bpy.utils.register_class(ShowHideRHSubs)
        bpy.utils.register_class(ShowHideSubCerebellum)
        bpy.utils.register_class(ShowHideHead)
        # print('Show Hide Panel was registered!')
    except:
        print("Can't register Show Hide Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(ShowHideObjectsPanel)
        bpy.utils.unregister_class(ShowHideLH)
        bpy.utils.unregister_class(ShowHideRH)
        bpy.utils.unregister_class(ShowSagittal)
        bpy.utils.unregister_class(ShowCoronal)
        bpy.utils.unregister_class(ShowAxial)
        bpy.utils.unregister_class(SplitView)
        bpy.utils.unregister_class(MaxMinBrain)
        bpy.utils.unregister_class(CenterView)
        bpy.utils.unregister_class(ShowHideSubCorticals)
        bpy.utils.unregister_class(ShowHideLHSubs)
        bpy.utils.unregister_class(ShowHideRHSubs)
        bpy.utils.unregister_class(ShowHideSubCerebellum)
        bpy.utils.unregister_class(ShowHideHead)
    except:
        pass
        # print("Can't unregister Freeview Panel!")
