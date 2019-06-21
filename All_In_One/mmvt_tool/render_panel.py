import bpy
import math
import os.path as op
import glob
import numpy as np
from queue import PriorityQueue
from functools import partial
import traceback
import logging
import mmvt_utils as mu
import importlib
importlib.reload(mu)
import re
import types


bpy.types.Scene.output_path = bpy.props.StringProperty(
    name="", default="", subtype='DIR_PATH', description='Sets the saved images location.'
    '\n\nScript: mmvt.render.get_output_path() and set_output_path(new_path)')


def _addon():
    return RenderingMakerPanel.addon


def render_in_queue():
    return RenderingMakerPanel.render_in_queue


def finish_rendering():
    logging.info('render panel: finish rendering!')
    RenderingMakerPanel.background_rendering = False
    RenderingMakerPanel.render_in_queue = None
    pop_from_queue()
    if queue_len() > 0:
        logging.info('render panel: run another rendering job')
        run_func_in_queue()
    # logging.handlers[0].flush()


def view_distance_update(self, context):
    mu.get_view3d_region().view_distance = bpy.context.scene.view_distance


def get_view_distance():
    return bpy.context.scene.view_distance


def set_view_distance(val):
    bpy.context.scene.view_distance = val


def reading_from_rendering_stdout_func():
    return RenderingMakerPanel.background_rendering


def camera_files_update(self, context):
    load_camera()


def background_color_update(self, context):
    color_rgb = [1.0, 1.0, 1.0] if bpy.context.scene.background_color == 'white' else [.0, .0, .0]
    bpy.data.worlds['World'].horizon_color = color_rgb
    context.user_preferences.themes[0].view_3d.space.gradients.high_gradient = color_rgb


def set_background_color_name(color):
    if color in ['white', 'black']:
        bpy.context.scene.background_color = color
    else:
        print('Background color can be only white/black!')


def set_render_quality(quality):
    bpy.context.scene.quality = quality
    

def set_render_output_path(output_path):
    bpy.context.scene.output_path = output_path
    bpy.context.scene.render.filepath = op.join(output_path, 'screencast')
    

def set_render_smooth_figure(smooth_figure):
    bpy.context.scene.smooth_figure = smooth_figure


def get_rendering_in_the_background():
    return bpy.context.scene.render_background


def set_rendering_in_the_background(val):
    bpy.context.scene.render_background = val


def load_camera(camera_fname=''):
    if camera_fname == '':
        camera_fname = op.join(mu.get_user_fol(), 'camera', '{}.pkl'.format(bpy.context.scene.camera_files))
    if op.isfile(camera_fname):
        camera_name = mu.namebase(camera_fname)
        for hemi in mu.HEMIS:
            if hemi in camera_name:
                _addon().show_hide_hemi(False, hemi)
                _addon().show_hide_hemi(True, mu.other_hemi(hemi))
        X_rotation, Y_rotation, Z_rotation, X_location, Y_location, Z_location = mu.load(camera_fname)
        RenderFigure.update_camera = False
        bpy.context.scene.X_rotation = X_rotation
        bpy.context.scene.Y_rotation = Y_rotation
        bpy.context.scene.Z_rotation = Z_rotation
        bpy.context.scene.X_location = X_location
        bpy.context.scene.Y_location = Y_location
        bpy.context.scene.Z_location = Z_location
        # print('Camera loaded: rotation: {},{},{} locatioin: {},{},{}'.format(
        #     X_rotation, Y_rotation, Z_rotation, X_location, Y_location, Z_location))
        # print('Camera loaded: {}'.format(camera_fname))
        RenderFigure.update_camera = True
        update_camera()
    else:
        pass
        # print('No camera file was found in {}!'.format(camera_fname))


def get_view_mode():
    area = bpy.data.screens['Neuro'].areas[1]
    view = area.spaces[0].region_3d.view_perspective
    return view


def is_camera_view():
    return get_view_mode() == 'CAMERA'


def set_to_camera_view():
    camera_mode('CAMERA')


def exit_from_camera_view():
    camera_mode('ORTHO')


def set_background_color(new_color=(0.227, 0.227, 0.227)):
    if isinstance(new_color, str):
        set_background_color_name(new_color)
    else:
        bpy.context.user_preferences.themes[0].view_3d.space.gradients.high_gradient = new_color


def switch_to_object_mode(area=None):
    if area is None:
        area = bpy.data.screens['Neuro'].areas[1]
    area.spaces[0].region_3d.view_perspective = 'ORTHO'
    mu.select_all_brain(False)
    bpy.data.cameras['Camera'].lens = 35
    _addon().change_to_solid_brain()


def switch_to_camera_mode(area=None):
    # if area is None:
    #     # area = bpy.data.screens['Neuro'].areas[1]
    #     area = next(mu.get_3d_areas())
    _addon().change_to_rendered_brain()
    bpy.data.objects['Camera'].select = True
    bpy.context.scene.objects.active = bpy.data.objects['Camera']
    ob = bpy.context.object
    bpy.context.scene.camera = ob
    area, region = mu.get_3d_area_region()
    for region in area.regions:
        if region.type == 'WINDOW':
            override = bpy.context.copy()
            override['area'] = area
            override['region'] = region
            mu.select_all_brain(True)
            bpy.ops.view3d.camera_to_view(override)
            bpy.ops.view3d.camera_to_view_selected(override)
            bpy.data.cameras['Camera'].lens = 32
            grab_camera()
            break


def camera_mode(view=None):
    area = bpy.data.screens['Neuro'].areas[1]
    if view is None:
        view = area.spaces[0].region_3d.view_perspective
    else:
        view = 'ORTHO' if view == 'CAMERA' else 'CAMERA'
    if view == 'CAMERA':
        switch_to_object_mode(area)
    else:
        switch_to_camera_mode(area)


def grab_camera(self=None, do_save=True, overwrite=True):
    RenderFigure.update_camera = False
    bpy.context.scene.X_rotation = X_rotation = math.degrees(bpy.data.objects['Camera'].rotation_euler.x)
    bpy.context.scene.Y_rotation = Y_rotation = math.degrees(bpy.data.objects['Camera'].rotation_euler.y)
    bpy.context.scene.Z_rotation = Z_rotation = math.degrees(bpy.data.objects['Camera'].rotation_euler.z)
    bpy.context.scene.X_location = X_location = bpy.data.objects['Camera'].location.x
    bpy.context.scene.Y_location = Y_location = bpy.data.objects['Camera'].location.y
    bpy.context.scene.Z_location = Z_location = bpy.data.objects['Camera'].location.z
    if do_save:
        if op.isdir(op.join(mu.get_user_fol(), 'camera')):
            camera_fname = op.join(mu.get_user_fol(), 'camera', 'camera.pkl')
            if not op.isfile(camera_fname) or overwrite:
                mu.save((X_rotation, Y_rotation, Z_rotation, X_location, Y_location, Z_location), camera_fname)
                # print('Camera location was saved to {}'.format(camera_fname))
                print((X_rotation, Y_rotation, Z_rotation, X_location, Y_location, Z_location))
        else:
            mu.message(self, "Can't find the folder {}".format(mu.get_user_fol(), 'camera'))
    RenderFigure.update_camera = True


def render_draw(self, context):
    layout = self.layout
    view_mode = get_view_mode()
    view = bpy.data.screens['Neuro'].areas[1].spaces[0].region_3d.view_perspective

    if 'CAMERA' in view_mode:
        layout.operator(RenderFigure.bl_idname, text="Render image", icon='SCENE')
    else:
        layout.operator(SaveImage.bl_idname, text='Save image', icon='ROTATE')
    func_name = 'Render' if view_mode == 'CAMERA' else 'Save'
    layout.operator(SaveAllViews.bl_idname, text='{} all perspectives'.format(func_name), icon='EDITMODE_HLT')
    if func_name == 'Render':
        layout.operator(ShowHideRenderRot.bl_idname, text="Render full rotation", icon='CLIP')
    layout.operator(SaveColorbar.bl_idname, text='Save the colorbar'.format(func_name), icon='SETTINGS')
    row = layout.row(align=0)
    row.prop(context.scene, 'save_views_with_cb', text="Colorbar")
    if bpy.context.scene.save_views_with_cb:
        row.prop(context.scene, 'cb_ticks_num', text="ticks")
        row.prop(context.scene, 'cb_ticks_font_size', text="size")
    layout.prop(context.scene, 'save_split_views', text="Split views")
    layout.prop(context.scene, 'save_selected_view')
    split = layout.row().split(percentage=0.7)
    split.column().prop(context.scene, 'output_path')
    split.column().prop(bpy.context.scene.render.image_settings, 'file_format', text='')

    if view == 'CAMERA':
        layout.prop(context.scene, "quality", text='Quality')
        layout.prop(context.scene.render, 'resolution_x')
        layout.prop(context.scene.render, 'resolution_y')
        layout.prop(context.scene, "lighting", text='Lighting')
        layout.prop(context.scene, "background_color", expand=True)
        if RenderingMakerPanel.background_rendering:
            layout.label(text='Rendering in the background...')

        layout.prop(context.scene, "show_camera_props", text='Show camera props')
        if bpy.context.scene.show_camera_props:
            col = layout.column(align=True)
            col.prop(context.scene, "X_rotation", text='X rotation')
            col.prop(context.scene, "Y_rotation", text='Y rotation')
            col.prop(context.scene, "Z_rotation", text='Z rotation')
            col = layout.column(align=True)
            col.prop(context.scene, "X_location", text='X location')
            col.prop(context.scene, "Y_location", text='Y location')
            col.prop(context.scene, "Z_location", text='Z location')
    else:
        if not bpy.context.scene.save_selected_view:
            layout.prop(context.scene, 'view_distance', text='View distance')
            layout.prop(bpy.context.scene.render, 'resolution_percentage', text='Resolution')
        layout.prop(context.scene, "background_color", expand=True)

    icon = 'SCENE' if view == 'ORTHO' else 'MESH_MONKEY'
    text = 'Camera' if view == 'ORTHO' else 'Object'
    layout.operator(CameraMode.bl_idname, text='{} view'.format(text), icon=icon)


def update_camera(self=None, context=None):
    if RenderFigure.update_camera:
        bpy.data.objects['Camera'].rotation_euler.x = math.radians(bpy.context.scene.X_rotation)
        bpy.data.objects['Camera'].rotation_euler.y = math.radians(bpy.context.scene.Y_rotation)
        bpy.data.objects['Camera'].rotation_euler.z = math.radians(bpy.context.scene.Z_rotation)
        bpy.data.objects['Camera'].location.x = bpy.context.scene.X_location
        bpy.data.objects['Camera'].location.y = bpy.context.scene.Y_location
        bpy.data.objects['Camera'].location.z = bpy.context.scene.Z_location


def lighting_update(self, context):
    bpy.data.materials['light'].node_tree.nodes["Emission"].inputs[1].default_value = bpy.context.scene.lighting


def set_lighting(val):
    bpy.context.scene.lighting = val


def mirror():
    camera_rotation_z = bpy.context.scene.Z_rotation
    # target_rotation_z = math.degrees(bpy.data.objects['Camera'].rotation_euler.z)
    bpy.data.objects['Target'].rotation_euler.z += math.radians(180 - camera_rotation_z)
    print(bpy.data.objects['Target'].rotation_euler.z)


bpy.types.Scene.X_rotation = bpy.props.FloatProperty(
    default=0, description="Camera rotation around x axis", update=update_camera) # min=-360, max=360
bpy.types.Scene.Y_rotation = bpy.props.FloatProperty(
    default=0, description="Camera rotation around y axis", update=update_camera) # min=-360, max=360,
bpy.types.Scene.Z_rotation = bpy.props.FloatProperty(
    default=0, description="Camera rotation around z axis", update=update_camera) # min=-360, max=360,
bpy.types.Scene.X_location = bpy.props.FloatProperty(description="Camera x location", update=update_camera)
bpy.types.Scene.Y_location = bpy.props.FloatProperty(description="Camera y lovation", update=update_camera)
bpy.types.Scene.Z_location = bpy.props.FloatProperty(description="Camera z locationo", update=update_camera)
bpy.types.Scene.quality = bpy.props.FloatProperty(
    default=20, min=1, max=100, description='Sets the image resolution (size of the image file)')
bpy.types.Scene.smooth_figure = bpy.props.BoolProperty(
    name='Smooth image', description="This significantly affect rendering speed")
bpy.types.Scene.render_background = bpy.props.BoolProperty(
    name='Background rendering', description='Renders via another Blender in the background.'
    '\n\nScript: mmvt.render.get_rendering_in_the_background() and set_rendering_in_the_background(val)')
bpy.types.Scene.lighting = bpy.props.FloatProperty(
    default=1, min=0, max=2, update=lighting_update,
    description='Changes the light levels.\n*Tip: Very useful when rendering with white background. '
                'Lower the light level to have a better contrast')
bpy.types.Scene.camera_files = bpy.props.EnumProperty(items=[('default', 'camera.pkl', '', 0)], update=camera_files_update)
bpy.types.Scene.show_camera_props = bpy.props.BoolProperty(default=False,
    description='Opens fields to change the axis value of the camera view')
bpy.types.Scene.background_color = bpy.props.EnumProperty(
    items=[('black', 'Black', '', 1), ("white", 'White', '', 2)], update=background_color_update,
    description='Sets the background color of the brain & colorbar\n\nCurrent color')
bpy.types.Scene.in_camera_view = bpy.props.BoolProperty(default=False)
bpy.types.Scene.save_selected_view = bpy.props.BoolProperty(default=True, name='Fit image into view',
    description='Fits automatically the view on the brain when the image is saved')
bpy.types.Scene.save_split_views = bpy.props.BoolProperty(default=False,
    description='Saves both sides of the split brain in one image.'
                '\n\nScript: mmvt.render.get_save_split_views() and set_save_split_views(val=True)')
bpy.types.Scene.view_distance = bpy.props.FloatProperty(default=20, update=view_distance_update,
    description='Changes the distance of the 3D brain modal from the front (changes the size of the brain).\nSame can be done by scrolling the MMB.'
    '\n\nScript: mmvt.render.get_view_distance() and set_view_distance(val)')
bpy.types.Scene.save_views_with_cb = bpy.props.BoolProperty(default=False,
    description='Adds colorbar to the saved images (check this box before saving the images)')
bpy.types.Scene.cb_ticks_num = bpy.props.IntProperty(min=2, default=2,
    description='Sets the number of ticks in the colorbar')
bpy.types.Scene.cb_ticks_font_size = bpy.props.IntProperty(min=1, default=16,
    description='Sets the size of the ticks in the colorbar')


class SaveColorbar(bpy.types.Operator):
    bl_idname = "mmvt.save_the_colorbar"
    bl_label = "mmvt save_the_colorbar"
    bl_description = 'Saves an image only of the colorbar.\n\nScript: mmvt.render._addon().save_colorbar()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        _addon().save_colorbar()
        return {"FINISHED"}


class SaveAllViews(bpy.types.Operator):
    bl_idname = "mmvt.save_all_views"
    bl_label = "mmvt save_all_views"
    bl_description = 'Saves all the major perspectives of the brain (Anterior, Inferior, Superior, Posterior, Left, Right, Medial).' \
                     '\n\nScript: mmvt.render.save_all_views()'
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        save_all_views(render_images=get_view_mode() == 'CAMERA')
        return {"FINISHED"}



class MirrorCamera(bpy.types.Operator):
    bl_idname = "mmvt.mirror_camera"
    bl_label = "Mirror Camera"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        mirror()
        return {"FINISHED"}


class SaveImage(bpy.types.Operator):
    bl_idname = "mmvt.save_image"
    bl_label = "Save Image"
    bl_description = 'Saves an image of the brain area.\n\nScript: mmvt.render._save_image()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        _save_image()
        return {"FINISHED"}


class CameraMode(bpy.types.Operator):
    bl_idname = "mmvt.camera_mode"
    bl_label = "Camera Mode"
    bl_description = 'Switches the appearance into Rendered Brain mode and captures all the presented objects in the ' \
                     'camera view.\n\nScript: mmvt.render.camera_mode()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        camera_mode()
        return {"FINISHED"}


class GrabCamera(bpy.types.Operator):
    bl_idname = "mmvt.grab_camera"
    bl_label = "Grab Camera"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        grab_camera(self)
        return {"FINISHED"}


class LoadCamera(bpy.types.Operator):
    bl_idname = "mmvt.load_camera"
    bl_label = "Load Camera"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        load_camera()
        return {"FINISHED"}


class RenderFigure(bpy.types.Operator):
    bl_idname = "mmvt.rendering"
    bl_label = "Render figure"
    bl_description = 'Saves the image in the subjects ‘figures’ folder.\nExample: ..mmvt_root/mmvt_blend/colin27/figures' \
                     '\n\nScript: mmvt.render.render_image()'
    bl_options = {"UNDO"}
    update_camera = True

    def invoke(self, context, event=None):
        render_image()
        return {"FINISHED"}


class RenderPerspectives(bpy.types.Operator):
    bl_idname = "mmvt.render_all_perspectives"
    bl_label = "Render all perspectives"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        camera_files = [op.join(mu.get_user_fol(), 'camera', '{}{}.pkl'.format(
            pers_name, '_inf' if _addon().is_inflated() else '')) for pers_name in
            ['camera_lateral_lh', 'camera_lateral_rh', 'camera_medial_lh', 'camera_medial_rh']]
        render_all_images(camera_files, hide_subcorticals=True)
        if bpy.context.scene.render_background:
            put_func_in_queue(combine_four_brain_perspectives, pop_immediately=True)
        else:
            combine_four_brain_perspectives()
        return {"FINISHED"}


class CombinePerspectives(bpy.types.Operator):
    bl_idname = "mmvt.combine_all_perspectives"
    bl_label = "Combine all perspectives"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        combine_four_brain_perspectives()
        return {"FINISHED"}


# def combine_four_brain_perspectives():
#     cmd = '{} -m src.utils.figures_utils --fol {} -f combine_four_brain_perspectives '.format(
#         bpy.context.scene.python_cmd, op.join(mu.get_user_fol(), 'figures')) + \
#         '--inflated {} --facecolor {}'.format(int(_addon().is_inflated()), bpy.context.scene.background_color)
#     mu.run_command_in_new_thread(cmd, False)


def combine_four_brain_perspectives():
    data_min, data_max = _addon().get_colorbar_max_min()
    background = bpy.context.scene.background_color
    figure_name = 'splitted_lateral_medial_{}_{}.{}'.format(
        'inflated' if _addon().is_inflated() else 'pial', background, _addon().get_figure_format())
    figure_fname = op.join(mu.get_user_fol(), 'figures', figure_name)
    colors_map = _addon().get_colormap().replace('-', '_')
    x_left_crop, x_right_crop, y_top_crop, y_buttom_crop = (300, 300, 0, 0)
    w_fac, h_fac = (1.5, 1)
    cmd = '{} -m src.utils.figures_utils '.format(bpy.context.scene.python_cmd) + \
        '-f combine_four_brain_perspectives,combine_brain_with_color_bar --fol {} --data_max {} --data_min {} '.format(
        op.join(mu.get_user_fol(), 'figures'), data_max, data_min) + \
        '--figure_fname {} --colors_map {} --x_left_crop {} --x_right_crop {} --y_top_crop {} --y_buttom_crop {} '.format(
        figure_fname, colors_map, x_left_crop, x_right_crop, y_top_crop, y_buttom_crop) + \
        '--w_fac {} --h_fac {} --facecolor {}'.format(w_fac, h_fac, background)
    mu.run_command_in_new_thread(cmd, False)


class RenderAllFigures(bpy.types.Operator):
    bl_idname = "mmvt.render_all_figures"
    bl_label = "Render all figures"
    bl_options = {"UNDO"}
    update_camera = True

    def invoke(self, context, event=None):
        render_all_images()
        return {"FINISHED"}


def init_rendering(inflated, inflated_ratio, transparency, light_layers_depth, lighting=1, background_color='black',
                   rendering_in_the_background=False):
    _addon().clear_colors()
    _addon().set_brain_transparency(transparency)
    _addon().set_light_layers_depth(light_layers_depth)
    set_rendering_in_the_background(rendering_in_the_background)
    if inflated:
        _addon().show_inflated()
        _addon().set_inflated_ratio(inflated_ratio)
    else:
        _addon().show_pial()
    set_background_color_name(background_color)
    set_lighting(lighting)


def render_movie(dx=None, dy=None, dz=None):
    dx = bpy.context.scene.rotate_dx if dx is None else dx
    dy = bpy.context.scene.rotate_dy if dy is None else dy
    dz = bpy.context.scene.rotate_dz if dz is None else dz
    stop = False
    rotate_dxyz = np.array([0., 0., 0.])
    run = 0
    while not stop:
        _addon().render.render_image('rotation')
        _addon().render.camera_mode('ORTHO')
        _addon().show_hide.rotate_brain(dx, dy, dz)
        _addon().render.camera_mode('CAMERA')
        rotate_dxyz += np.array([dx, dy, dz])
        run += 1
        stop = any([rotate_dxyz[k] >= 360 for k in range(3)]) or run > 360


def render_all_images(camera_files=None, hide_subcorticals=False):
    if camera_files is None:
        camera_files = glob.glob(op.join(mu.get_user_fol(), 'camera', 'camera_*.pkl'))
    render_image(camera_fname=camera_files, hide_subcorticals=hide_subcorticals)


def render_lateral_medial_split_brain(data_type='', quality=20, overwrite=True):
    image_name = ['lateral_lh', 'lateral_rh', 'medial_lh', 'medial_rh']
    camera = [op.join(mu.get_user_fol(), 'camera', 'camera_{}{}.pkl'.format(
        camera_name, '_inf' if _addon().is_inflated() else '')) for camera_name in image_name]
    image_name = ['{}{}_{}_{}'.format('{}_'.format(data_type) if data_type != '' else '', name, 'inflated_{}'.format(
        _addon().get_inflated_ratio()) if _addon().is_inflated() else 'pial', bpy.context.scene.background_color)
                  for name in image_name]
    render_image(image_name, quality=quality, camera_fname=camera, hide_subcorticals=True, overwrite=overwrite)


@mu.timeit
def render_image(image_name='', image_fol='', quality=0, use_square_samples=None, render_background=None,
                 camera_fname='', hide_subcorticals=False, overwrite=True, set_to_camera_mode=True):
    if not is_camera_view() and set_to_camera_mode:
        set_to_camera_view()
    bpy.context.scene.render.resolution_percentage = bpy.context.scene.quality if quality == 0 else quality
    bpy.context.scene.cycles.use_square_samples = bpy.context.scene.smooth_figure if use_square_samples is None \
        else use_square_samples
    if not render_background is None:
        bpy.context.scene.render_background = render_background
    if camera_fname == '':
        camera_fname = op.join(mu.get_user_fol(), 'camera', '{}.pkl'.format(bpy.context.scene.camera_files))
    current_frame = bpy.context.scene.frame_current
    camera_fnames = [camera_fname] if isinstance(camera_fname, str) else camera_fname
    if image_name == '':
        images_names = ['{}_{}.{}'.format(mu.namebase(camera_fname).replace('camera', ''),
                        current_frame, _addon().get_figure_format())
                        for camera_fname in  camera_fnames]
        images_names = [n[1:] if n.startswith('_') else n for n in images_names]
    else:
        images_names = [image_name] if isinstance(image_name, str) else image_name
    image_fol = bpy.path.abspath(bpy.context.scene.output_path) if image_fol == '' else image_fol
    image_fname = op.join(image_fol, '{}.{}'.format(images_names[0], get_figure_format()))
    if op.isfile(image_fname):
        files = glob.glob(op.join(image_fol, '{}_*.{}'.format(mu.namebase(image_fname), get_figure_format())))
        image_fname = op.join(image_fol, '{}_{}.{}'.format(mu.namebase(image_fname), len(files), get_figure_format()))
    if op.isfile(image_fname):
        print('{} already exist!'.format(image_fname))
        return ''
    print('Image quality: {}'.format(bpy.context.scene.render.resolution_percentage))
    print("Rendering...")
    if not bpy.context.scene.render_background:
        for image_name, camera_fname in zip(images_names, camera_fnames):
            print('file name: {}'.format(image_fname))
            bpy.context.scene.render.filepath = image_fname
            if overwrite or len(glob.glob('{}.*'.format(bpy.context.scene.render.filepath))) == 0:
                # _addon().load_camera(camera_fname)
                _addon().change_to_rendered_brain()
                if hide_subcorticals:
                    _addon().show_hide_sub_corticals()
                bpy.ops.render.render(write_still=True)
        print("Finished")
        return image_fname
    else:
        camera_fnames = ','.join(camera_fnames)
        images_names = ','.join(images_names)
        render_func = partial(render_in_background, image_name=images_names, image_fol=image_fol,
                              camera_fname=camera_fnames, hide_subcorticals=hide_subcorticals, overwrite=overwrite)
        put_func_in_queue(render_func)
        if queue_len() == 1:
            run_func_in_queue()
    return bpy.context.scene.render.filepath


def render_in_background(image_name, image_fol, camera_fname, hide_subcorticals, overwrite=True):
    hide_subs_in_background = True if hide_subcorticals else bpy.context.scene.objects_show_hide_sub_cortical
    mu.change_fol_to_mmvt_root()
    electrode_marked = _addon().is_current_electrode_marked()
    script = 'src.mmvt_addon.scripts.render_image'
    cmd = '{} -m {} -s {} -a {} -i {} -o {} -q {} -b {} -c "{}"'.format(
        bpy.context.scene.python_cmd, script, mu.get_user(), bpy.context.scene.atlas,
        image_name, image_fol, bpy.context.scene.render.resolution_percentage,
        bpy.context.scene.bipolar, camera_fname) + \
        ' --hide_lh {} --hide_rh {} --hide_subs {} --show_elecs {} --curr_elec {} --show_only_lead {}'.format(
        bpy.context.scene.objects_show_hide_lh, bpy.context.scene.objects_show_hide_rh,
        hide_subs_in_background, bpy.context.scene.show_hide_electrodes,
        bpy.context.scene.electrodes if electrode_marked else None,
        bpy.context.scene.show_only_lead if electrode_marked else None) + \
        ' --show_connections {}  --interactive 0  --overwrite {}'.format(
            _addon().connections_visible(), overwrite)
    print('Running {}'.format(cmd))
    RenderingMakerPanel.background_rendering = True
    mu.save_blender_file()
    _, RenderingMakerPanel.render_in_queue = mu.run_command_in_new_thread(
        cmd, read_stderr=False, read_stdin=False, stdout_func=reading_from_rendering_stdout_func)
    # mu.run_command_in_new_thread(cmd, queues=False)


def _save_image():
    if not bpy.context.scene.save_split_views:
        save_image(view_selected=bpy.context.scene.save_selected_view,
                   add_colorbar=bpy.context.scene.save_views_with_cb)
    else:
        images = {}
        org_hide = {hemi: mu.get_hemi_obj(hemi).hide for hemi in mu.HEMIS}
        for hemi in mu.HEMIS:
            mu.get_hemi_obj(hemi).hide = False
            mu.get_hemi_obj(mu.other_hemi(hemi)).hide = True
            images[hemi] = save_image(view_selected=bpy.context.scene.save_selected_view, add_colorbar=False)
        for hemi in mu.HEMIS:
            mu.get_hemi_obj(hemi).hide = org_hide[hemi]
        combine_two_images_and_add_colorbar(images['lh'], images['rh'], images['lh'])


def save_image(image_type='image', view_selected=None, index=-1, zoom_val=0, add_index_to_name=True,
               add_colorbar=None, cb_ticks_num=None, cb_ticks_font_size=None):
    if add_colorbar is None:
        add_colorbar = False #todo: Fix!! bpy.context.scene.save_views_with_cb
    if cb_ticks_num is None:
        cb_ticks_num = bpy.context.scene.cb_ticks_num
    if cb_ticks_font_size is None:
        cb_ticks_font_size = bpy.context.scene.cb_ticks_font_size
    if view_selected is None:
        view_selected = bpy.context.scene.save_selected_view
    if index == -1:
        fol = bpy.path.abspath(bpy.context.scene.output_path)
        files = [mu.namebase(f) for f in glob.glob(op.join(fol, '{}*.{}'.format(image_type, get_figure_format())))]
        files_with_numbers = sum([len(re.findall('\d+', f)) for f in files])
        if files_with_numbers > 0:
            index = max([int(re.findall('\d+', f)[0]) for f in files]) + 1 if len(files) > 0 else 0
        else:
            index = 0

    switch_to_object_mode()
    index = bpy.context.scene.frame_current if index == -1 else index
    mu.show_only_render(True)
    fol = bpy.path.abspath(bpy.context.scene.output_path)
    if add_index_to_name:
        image_name = op.join(fol, '{}_{}.{}'.format(image_type, index, get_figure_format()))
    else:
        image_name = op.join(fol, '{}.{}'.format(image_type, get_figure_format()))
    print('Image saved in {}'.format(image_name))
    bpy.context.scene.render.filepath = image_name
    view3d_context = mu.get_view3d_context()
    if view_selected:
        _addon().view_all()
        # todo: Understand when zoom(-1) is needed
        # if not _addon().subcorticals_are_hiding():
        #     _addon().zoom(-1)
        # mu.select_all_brain(True)
        # bpy.ops.view3d.camera_to_view_selected(view3d_context)
        # mu.view_selected()
    if zoom_val != 0:
        _addon().zoom(zoom_val)
    # _addon().zoom(1)
    # mu.center_view()
    bpy.ops.render.opengl(view3d_context, write_still=True)
    if add_colorbar:
        add_colorbar_to_image(image_name, cb_ticks_num, cb_ticks_font_size)
    # if view_selected:
    #     _addon().zoom(1)
    return image_name


def get_figure_format():
    return str(bpy.context.scene.render.image_settings.file_format).lower()


def set_figure_format(val):
    bpy.context.scene.render.image_settings.file_format = val.upper()


def get_output_path():
    return bpy.path.abspath(bpy.context.scene.output_path)


def get_output_type():
    return bpy.context.scene.render.image_settings.file_format


def set_output_type(val):
    bpy.context.scene.render.image_settings.file_format = val


def set_output_path(new_path):
    bpy.context.scene.output_path = new_path


def get_full_output_fname(img_name):
    return op.join(get_output_path(), '{}.{}'.format(img_name, get_output_type()))


def get_save_views_with_cb():
    return bpy.context.scene.save_views_with_cb


def save_views_with_cb(val=True):
    bpy.context.scene.save_views_with_cb = val


def get_save_split_views():
    return bpy.context.scene.save_split_views


def set_save_split_views(val=True):
    bpy.context.scene.save_split_views = val


# todo: do something with the overwrite flag
def save_all_views(views=None, inflated_ratio_in_file_name=False, rot_lh_axial=None, render_images=False, quality=0,
                   img_name_prefix='', add_colorbar=None, cb_ticks_num=None, cb_ticks_font_size=None, overwrite=True):
    if not render_images:
        _addon().change_to_solid_brain()
    if add_colorbar is None:
        add_colorbar = bpy.context.scene.save_views_with_cb
    if cb_ticks_num is None:
        cb_ticks_num = bpy.context.scene.cb_ticks_num
    if cb_ticks_font_size is None:
        cb_ticks_font_size = bpy.context.scene.cb_ticks_font_size

    _addon().show_hemis()
    if not bpy.context.scene.save_split_views:
        rot_lh_axial = False if rot_lh_axial is None else rot_lh_axial
        _save_all_views(views, inflated_ratio_in_file_name, rot_lh_axial, render_images, quality,  img_name_prefix,
                        add_colorbar, cb_ticks_num, cb_ticks_font_size, overwrite)
    else:
        if views is None:
            views = list(set(_addon().ANGLES_DICT.keys()) - set([_addon().ROT_MEDIAL_LEFT, _addon().ROT_MEDIAL_RIGHT]))
        images_names = []
        rot_lh_axial = True if rot_lh_axial is None else rot_lh_axial
        org_hide = {hemi: mu.get_hemi_obj(hemi).hide for hemi in mu.HEMIS}
        for hemi in mu.HEMIS:
            mu.get_hemi_obj(hemi).hide = False
            mu.get_hemi_obj(mu.other_hemi(hemi)).hide = True
            images_names.extend(_save_all_views(
                views, inflated_ratio_in_file_name, rot_lh_axial, render_images, quality,  img_name_prefix, False,
                overwrite=overwrite))
        for hemi in mu.HEMIS:
            mu.get_hemi_obj(hemi).hide = org_hide[hemi]
        images_hemi_inv_list = set(
            [mu.namebase(fname)[3:] for fname in images_names if mu.namebase(fname)[:2] in ['rh', 'lh']])
        files = [[fname for fname in images_names if mu.namebase(fname)[3:] == img_hemi_inv] for img_hemi_inv in
                 images_hemi_inv_list]
        fol = mu.get_fname_folder(files[0][0])
        for files_coup in files:
            hemi = 'rh' if mu.namebase(files_coup[0]).startswith('rh') else 'lh'
            coup_template = files_coup[0].replace(hemi, '{hemi}')
            coup = {hemi: coup_template.format(hemi=hemi) for hemi in mu.HEMIS}
            new_image_fname = op.join(fol, mu.namebase_with_ext(files_coup[0])[3:])
            combine_two_images_and_add_colorbar(
                coup['lh'], coup['rh'], new_image_fname, cb_ticks_num, cb_ticks_font_size)
    _addon().show_hemis()


def _save_all_views(views=None, inflated_ratio_in_file_name=False, rot_lh_axial=True, render_images=False, quality=0,
                   img_name_prefix='', add_colorbar=False, cb_ticks_num=None, cb_ticks_font_size=None, overwrite=True):
    def get_image_name(view_name):
        return '{}{}{}_{}'.format(
            '{}_'.format(hemi) if hemi != '' else '',
            '{}_'.format(img_name_prefix) if img_name_prefix != '' else '', surf_name, view_name)

    def should_save_image(img_name):
        return overwrite or not op.isfile(get_full_output_fname(img_name))

    def save_medial_views():
        if _addon().ROT_MEDIAL_LEFT in views:
            image_name = '{}_left_medial'.format(surf_name)
            if should_save_image(image_name):
                _addon().hide_hemi('rh')
                _addon().show_hemi('lh')
                _addon().rotate_view(_addon().ROT_SAGITTAL_RIGHT)
                image_fname = save_render_image(
                    image_name, quality, render_images, add_colorbar, cb_ticks_num, cb_ticks_font_size)
                images_names.append(image_fname)
        if _addon().ROT_MEDIAL_RIGHT in views:
            image_name = '{}_right_medial'.format(surf_name)
            if should_save_image(image_name):
                _addon().show_hemi('rh')
                _addon().hide_hemi('lh')
                _addon().rotate_view(_addon().ROT_SAGITTAL_LEFT)
                image_fname = save_render_image(
                    '{}_right_medial'.format(surf_name), quality, render_images, add_colorbar, cb_ticks_num,
                    cb_ticks_font_size)
                images_names.append(image_fname)
        _addon().show_hemi('rh')
        _addon().show_hemi('lh')

    if views is None:
        views = list(_addon().ANGLES_DICT.keys()) # + [_addon().ROT_MEDIAL_LEFT, _addon().ROT_MEDIAL_RIGHT]
    else:
        views = list(map(int, views))
    inf_r = bpy.context.scene.inflating
    if inflated_ratio_in_file_name:
        surf_name_dict = {-1: 'pial', 0: 'inflated', 1: 'flat'}
        surf_name = surf_name_dict.get(inf_r, '')
        if surf_name == '':
            if -1 < inf_r < 0:
                surf_name = '{:.1f}_inflated'.format(1 - inf_r)
            else:
                surf_name = '{:.1f}_flat'.format(inf_r)
    else:
        surf_name = 'pial' if inf_r == -1 else 'inflated' if -1 < inf_r <= 0 else 'flat'
    if mu.get_hemi_obj('rh').hide and not mu.get_hemi_obj('lh').hide:
        hemi = 'lh'
    elif not mu.get_hemi_obj('rh').hide and mu.get_hemi_obj('lh').hide:
        hemi = 'rh'
    elif not mu.get_hemi_obj('rh').hide and not mu.get_hemi_obj('lh').hide:
        hemi = ''
    else:
        mu.write_to_stderr('You need to show at least one hemi')
    org_view_ang = tuple(mu.get_view3d_region().view_rotation)
    images_names = []
    for view in views:
        view_name = _addon().view_name(view)
        img_name = get_image_name(view_name)
        if not should_save_image(img_name):
            continue
        _addon().rotate_view(view)
        if hemi == 'lh' and rot_lh_axial and view in (_addon().ROT_AXIAL_SUPERIOR, _addon().ROT_AXIAL_INFERIOR):
            _addon().rotate_brain(dz=180)
        mu.center_view()
        image_fname = save_render_image(
            img_name, quality, render_images, add_colorbar, cb_ticks_num, cb_ticks_font_size)
        print(image_fname, view, hemi)
        images_names.append(image_fname)
    # if not mu.get_hemi_obj('rh').hide and not mu.get_hemi_obj('lh').hide:
    if views is None:
        save_medial_views()
    # todo: doesn't work
    mu.rotate_view3d(org_view_ang)
    mu.center_view()
    return images_names


# def center_view(view, hemi):
#     if _addon().is_pial():
#         z = 80 if view in (_addon().ROT_AXIAL_SUPERIOR, _addon().ROT_AXIAL_INFERIOR) else 3
#         if view == _addon().ROT_SAGITTAL_LEFT and hemi == 'rh':
#             y = -3
#         elif view == _addon().ROT_SAGITTAL_RIGHT and hemi == 'lh':
#             y = -3
#         else:
#             y = 0
#     else:
#         z = 80 if view in (_addon().ROT_AXIAL_SUPERIOR, _addon().ROT_AXIAL_INFERIOR) else 2
#         y = 0
#     mu.center_view(y, z)


def add_colorbar_to_image(image_fname, cb_ticks_num=None, cb_ticks_font_size=None):
    if cb_ticks_num is None:
        cb_ticks_num = bpy.context.scene.cb_ticks_num
    if cb_ticks_font_size is None:
        cb_ticks_font_size = bpy.context.scene.cb_ticks_font_size
    data_max, data_min = _addon().get_colorbar_max_min()
    cb_ticks = ','.join(_addon().get_colorbar_ticks(cb_ticks_num))
    cb_ticks = cb_ticks.replace('-', '*') # Bug in argparse. todo: change the , to space
    flags = '--figure_fname "{}" --data_max "{}" --data_min "{}" --colors_map {} --background_color {} '.format(
        image_fname, data_max, data_min, _addon().get_colormap(), get_background_rgb_string()) + \
        '--cb_title "{}" --cb_ticks "{}" --cb_ticks_font_size {} --cb_ticks_perc {}'.format(
            _addon().get_colorbar_title(), cb_ticks, cb_ticks_font_size, _addon().get_colorbar_prec())
    mu.run_mmvt_func('src.utils.figures_utils', 'add_colorbar_to_image', flags=flags)


def combine_two_images_and_add_colorbar(lh_figure_fname, rh_figure_fname, new_image_fname, cb_ticks_num=None,
                                        cb_ticks_font_size=None):
    if cb_ticks_num is None:
        cb_ticks_num = bpy.context.scene.cb_ticks_num
    if cb_ticks_font_size is None:
        cb_ticks_font_size = bpy.context.scene.cb_ticks_font_size
    data_max, data_min = _addon().get_colorbar_max_min()
    cb_ticks = ','.join(_addon().get_colorbar_ticks(cb_ticks_num))
    cb_ticks = cb_ticks.replace('-', '*')  # Bug in argparse
    flags = '--lh_figure_fname "{}" --rh_figure_fname "{}" '.format(lh_figure_fname, rh_figure_fname) + \
            '--new_image_fname "{}" --data_max "{}" --data_min "{}" '.format(new_image_fname, data_max, data_min) + \
            '--colors_map {} --background_color {} '.format(_addon().get_colormap(), get_background_rgb_string()) + \
            '--add_cb {} --cb_title "{}" --cb_ticks "{}" --cb_ticks_font_size {} '.format(
                bpy.context.scene.save_views_with_cb, _addon().get_colorbar_title(), cb_ticks, cb_ticks_font_size) + \
            '--crop_figures 1 --remove_original_figures 1'
    print('Combining {} and {}'.format(lh_figure_fname, rh_figure_fname))
    mu.run_mmvt_func(
        'src.utils.figures_utils', 'combine_two_images_and_add_colorbar', flags=flags)


def get_background_rgb_string():
    background = _addon().get_panels_background_color()
    return ','.join([str(x) for x in background])
    # return ','.join([str(background.__getattribute__(x)) for x in ('r', 'g', 'b')])


def save_render_image(img_name, quality, do_render_image, add_colorbar=None, cb_ticks_num=None, cb_ticks_font_size=None):
    if add_colorbar is None:
        add_colorbar = bpy.context.scene.save_views_with_cb
    if cb_ticks_num is None:
        cb_ticks_num = bpy.context.scene.cb_ticks_num
    if cb_ticks_font_size is None:
        cb_ticks_font_size = bpy.context.scene.cb_ticks_font_size
    if do_render_image:
        camera_mode()
        image_fname = render_image(img_name, quality=quality, overwrite=True)
        camera_mode()
    else:
        image_fname = save_image(img_name, add_index_to_name=False, add_colorbar=add_colorbar,
                                 cb_ticks_num=cb_ticks_num, cb_ticks_font_size=cb_ticks_font_size)
    mu.write_to_stderr('Saving image to {}'.format(image_fname))
    return image_fname


def queue_len():
    return len(RenderingMakerPanel.queue.queue)


def put_func_in_queue(func, pop_immediately=False):
    try:
        logging.info('in put_func_in_queue')
        RenderingMakerPanel.queue.put((RenderingMakerPanel.item_id, func, pop_immediately))
        RenderingMakerPanel.item_id += 1
    except:
        print(traceback.format_exc())
        logging.error('Error in put_func_in_queue!')
        logging.error(traceback.format_exc())


def run_func_in_queue():
    try:
        logging.info('run_func_in_queue')
        (_, func, pop_immediately) = RenderingMakerPanel.queue.queue[0]
        func()
        if pop_immediately:
            pop_from_queue()
    except:
        print(traceback.format_exc())
        logging.error('Error in run_func_in_queue!')
        logging.error(traceback.format_exc())


def pop_from_queue():
    try:
        return RenderingMakerPanel.queue.get()
    except:
        print(traceback.format_exc())
        logging.error('Error in pop_from_queue!')
        logging.error(traceback.format_exc())


def update_camera_files():
    if not RenderingMakerPanel.init:
        return
    camera_files = glob.glob(op.join(mu.get_user_fol(), 'camera', '*camera*.pkl'))
    if len(camera_files) > 0:
        files_names = [mu.namebase(fname) for fname in camera_files]
        if _addon().is_inflated():
            files_names = [name for name in files_names if 'inf' in name]
            files_names.append('camera')
        else:
            files_names = [name for name in files_names if 'inf' not in name]
        items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
        bpy.types.Scene.camera_files = bpy.props.EnumProperty(
            items=items, description="electrodes sources", update=camera_files_update)
        bpy.context.scene.camera_files = 'camera'


def get_resolution_percentage():
    return bpy.context.scene.render.resolution_percentage


def set_resolution_percentage(val):
    bpy.context.scene.render.resolution_percentage = val


class ShowHideRenderRot(bpy.types.Operator):
    bl_idname = "mmvt.show_hide_render_rot"
    bl_label = "mmvt show_hide_render_rot"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        render_movie()
        return {"FINISHED"}


class RenderingMakerPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Render"
    addon = None
    init = False
    render_in_queue = None
    background_rendering = False
    queue = None
    item_id = 0

    def draw(self, context):
        render_draw(self, context)


def init(addon):
    RenderingMakerPanel.addon = addon
    bpy.data.objects['Target'].rotation_euler.x = 0
    bpy.data.objects['Target'].rotation_euler.y = 0
    bpy.data.objects['Target'].rotation_euler.z = 0
    bpy.data.objects['Target'].location.x = 0
    bpy.data.objects['Target'].location.y = 0
    bpy.data.objects['Target'].location.z = 0
    mu.make_dir(op.join(mu.get_user_fol(), 'camera'))
    grab_camera(overwrite=False)
    update_camera_files()
    bpy.context.scene.in_camera_view = False
    bpy.context.scene.save_selected_view = False
    bpy.context.scene.view_distance = 17.36
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    # bpy.context.scene.lighting = 1.0
    RenderingMakerPanel.queue = PriorityQueue()
    mu.make_dir(op.join(mu.get_user_fol(), 'logs'))
    logging.basicConfig(
        filename=op.join(mu.get_user_fol(), 'logs', 'reander_panel.log'),
        level=logging.DEBUG, format='%(asctime)-15s %(levelname)8s %(name)s %(message)s')
    RenderingMakerPanel.init = True
    register()


def register():
    try:
        unregister()
        bpy.utils.register_class(RenderingMakerPanel)
        bpy.utils.register_class(RenderAllFigures)
        bpy.utils.register_class(SaveImage)
        bpy.utils.register_class(CameraMode)
        bpy.utils.register_class(GrabCamera)
        bpy.utils.register_class(LoadCamera)
        bpy.utils.register_class(MirrorCamera)
        bpy.utils.register_class(RenderFigure)
        bpy.utils.register_class(RenderPerspectives)
        bpy.utils.register_class(SaveAllViews)
        bpy.utils.register_class(SaveColorbar)
        bpy.utils.register_class(CombinePerspectives)
        bpy.utils.register_class(ShowHideRenderRot)
        # print('Render Panel was registered!')
    except:
        print("Can't register Render Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(RenderingMakerPanel)
        bpy.utils.unregister_class(RenderAllFigures)
        bpy.utils.unregister_class(SaveImage)
        bpy.utils.unregister_class(CameraMode)
        bpy.utils.unregister_class(GrabCamera)
        bpy.utils.unregister_class(LoadCamera)
        bpy.utils.unregister_class(MirrorCamera)
        bpy.utils.unregister_class(RenderFigure)
        bpy.utils.unregister_class(RenderPerspectives)
        bpy.utils.unregister_class(SaveAllViews)
        bpy.utils.unregister_class(SaveColorbar)
        bpy.utils.unregister_class(CombinePerspectives)
        bpy.utils.unregister_class(ShowHideRenderRot)
    except:
        pass
        # print("Can't unregister Render Panel!")
