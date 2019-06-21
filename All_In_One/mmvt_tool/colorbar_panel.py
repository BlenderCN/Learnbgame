import bpy
import os.path as op
import glob
import numpy as np
import mmvt_utils as mu
import colors_utils as cu
import shutil

# PERC_FORMATS = {0:'{:.0f}', 1:'{:.1f}', 2:'{:.2f}', 3:'{:.3f}', 4:'{:.4f}', 5:'{:.5f}'}
PERC_FORMATS = {p:'{:.' + str(p) + 'f}' for p in range(15)}

def _addon():
    return ColorbarPanel.addon


# todo: change the name
def change_colorbar_default_cm(val):
    if len(val) != 2:
        print('default cm should be a tuple of 2 default maps')
    else:
        ColorbarPanel.default_cm = val


def set_colorbar_defaults():
    init = ColorbarPanel.init
    ColorbarPanel.should_not_lock_values = True
    ColorbarPanel.init = False
    set_colorbar_title('')
    set_colorbar_max_min(1, -1, True)
    set_colorbar_prec(2)
    set_colormap(ColorbarPanel.default_cm[1])
    ColorbarPanel.should_not_lock_values = False
    ColorbarPanel.init = init


def set_colorbar_default_cm():
    if not ColorbarPanel.init:
        return
    # todo: take those values from an ini file
    data_min, data_max = bpy.context.scene.colorbar_min, bpy.context.scene.colorbar_max
    if not bpy.context.scene.coloring_use_abs:
        data_min = bpy.context.scene.colorbar_min = bpy.context.scene.coloring_lower_threshold
    if not (data_min == 0 and data_max == 0) and not colorbar_values_are_locked():
        if data_min == 0 or data_max == 0 or np.sign(data_min) == np.sign(data_max):
            if data_max > data_min >= 0:
                set_colormap(ColorbarPanel.default_cm[0])
            else:
                set_colormap(ColorbarPanel.default_cm[1])
        else:
            set_colormap(ColorbarPanel.default_cm[2])


def get_cm():
    return ColorbarPanel.cm


def save_colorbar(min_val=None, max_val=None, color_map=None, ticks_num=None, ticks_font_size=None, prec=None,
                  title=None, background_color_name=None, colorbar_name='', fol=''):
    org_colorbar_min, org_colorbar_max  = (get_colorbar_min(), get_colorbar_max())
    org_background_color = _addon().get_panels_background_color()
    if min_val is None:
        min_val = get_colorbar_min()
    if max_val is None:
        max_val = get_colorbar_max()
    if color_map is None:
        color_map = get_colormap_name()
    if ticks_num is None:
        ticks_num = get_colorbar_ticks_num()
    if ticks_font_size is None:
        ticks_font_size = get_cb_ticks_font_size()
    if prec is None:
        prec = get_colorbar_prec()
    if title is None:
        title = get_colorbar_title()
    if background_color_name is None:
        background_color_rgb = _addon().get_background_rgb_string()
    else:
        background_color_rgb = ','.join([str(x) for x in cu.name_to_rgb(background_color_name)])
    if colorbar_name == '':
        colorbar_name = '{}_colorbar.jpg'.format(color_map)
    else:
        if not colorbar_name.endswith('.jpg'):
            colorbar_name = '{}.jpg'.format(colorbar_name)
    if fol == '' or not op.isdir(fol):
        fol = _addon().get_output_path()
    cb_ticks = ','.join(get_colorbar_ticks(ticks_num, prec, min_val, max_val))
    cb_ticks = cb_ticks.replace('-', '*') # Bug in argparse. todo: change the , to space
    flags = '--colorbar_name "{}" --data_max "{}" --data_min "{}" --colors_map {} --background_color {} '.format(
        colorbar_name, max_val, min_val, color_map, background_color_rgb) + \
        '--cb_title "{}" --cb_ticks "{}" --cb_ticks_font_size {} --fol "{}"'.format(
            title, cb_ticks, ticks_font_size, fol)
    mu.run_mmvt_func('src.utils.figures_utils', 'plot_color_bar', flags=flags)

    set_colorbar_max_min(org_colorbar_max, org_colorbar_min, force_update=True)
    _addon().set_panels_background_color(org_background_color)


def set_colorbar_background_color(color_name):
    color_rgb = cu.name_to_rgb(color_name)
    _addon().set_panels_background_color(color_rgb)


def get_colorbar_ticks_num():
    return bpy.context.scene.cb_ticks_num


def colorbar_values_are_locked():
    return bpy.context.scene.lock_min_max


def lock_colorbar_values(val=True):
    bpy.context.scene.lock_min_max = val


def load_colormap():
    colormap_fname = op.join(mu.file_fol(), 'color_maps', '{}.npy'.format(
        bpy.context.scene.colorbar_files)) # .replace('-', '_')
    colormap = np.load(colormap_fname)
    ColorbarPanel.cm = colormap
    for ind in range(colormap.shape[0]):
        cb_obj_name = 'cb.{0:0>3}'.format(ind)
        cb_obj = bpy.data.objects[cb_obj_name]
        cur_mat = cb_obj.active_material
        cur_mat.diffuse_color = colormap[ind]
        # print('Changing {} to {}'.format(cb_obj_name, colormap[ind]))


def get_colormap_name():
    return bpy.context.scene.colorbar_files


@mu.tryit()
def set_colorbar_title(val):
    val = val.lstrip()
    val = '     {}'.format(val)
    init = ColorbarPanel.init
    bpy.data.objects['colorbar_title'].data.body = bpy.data.objects['colorbar_title_camera'].data.body = val
    ColorbarPanel.init = False
    bpy.context.scene.colorbar_title = val
    ColorbarPanel.init = init


def get_colorbar_title():
    return bpy.context.scene.colorbar_title


def set_colorbar_min_max(min_val, max_val, force_update=False):
    set_colorbar_max_min(max_val, min_val, force_update)


def set_colorbar_max_min(max_val, min_val, force_update=False, update_colorbar=True):
    if max_val >= min_val:
        init = ColorbarPanel.init
        if force_update:
            ColorbarPanel.init = True
        ColorbarPanel.should_not_lock_values = True
        bpy.context.scene.colorbar_max = max_val
        bpy.context.scene.colorbar_min = min_val
        ColorbarPanel.should_not_lock_values = False
        if update_colorbar:
            set_colorbar_default_cm()
        # mu.set_graph_att('colorbar_max', max_val)
        # mu.set_graph_att('colorbar_min', min_val)
        # _addon().s.colorbar_max = max_val
        # _addon().s.colorbar_min = min_val
        ColorbarPanel.init = init
        # todo: do this only if the use changed the fields (and wasn't called from other func)
        # lock_colorbar_values(True)
    else:
        print('set_colorbar_max_min: ax_val < min_val!')


def get_colorbar_max_min():
    return bpy.context.scene.colorbar_max, bpy.context.scene.colorbar_min


def set_colorbar_max(val, prec=None, check_minmax=True):
    if not check_minmax or bpy.context.scene.colorbar_max > bpy.context.scene.colorbar_min:
        _set_colorbar_min_max('max', val, prec)
    else:
        prev_max = float(bpy.data.objects['colorbar_max'].data.body)
        ColorbarPanel.init = False
        bpy.context.scene.colorbar_max = prev_max
        ColorbarPanel.init = True


def get_colorbar_max():
    return bpy.context.scene.colorbar_max


def set_colorbar_min(val, prec=None, check_minmax=True):
    if not check_minmax or bpy.context.scene.colorbar_max > bpy.context.scene.colorbar_min:
        _set_colorbar_min_max('min', val, prec)
    else:
        prev_min = float(bpy.data.objects['colorbar_min'].data.body)
        ColorbarPanel.init = False
        bpy.context.scene.colorbar_min = prev_min
        ColorbarPanel.init = True


def get_colorbar_min():
    return bpy.context.scene.colorbar_min


def get_colorbar_prec():
    return bpy.context.scene.colorbar_prec


def set_colorbar_prec(val):
    bpy.context.scene.colorbar_prec = val


def _set_colorbar_min_max(field, val, prec):
    if prec is None or prec not in PERC_FORMATS:
        prec = bpy.context.scene.colorbar_prec
        if prec not in PERC_FORMATS:
            print('Wrong value for prec, should be in {}'.format(PERC_FORMATS.keys()))
    prec_str = PERC_FORMATS[prec]
    cb_obj = bpy.data.objects.get('colorbar_{}'.format(field))
    cb_camera_obj = bpy.data.objects.get('colorbar_{}_camera'.format(field))
    if not cb_obj is None and not cb_camera_obj is None:
        cb_obj.data.body = cb_camera_obj.data.body = prec_str.format(val)
    else:
        print('_set_colorbar_min_max: field error ({})! must be max / min!'.format(field))


def get_colorbar_ticks(ticks_num=2, prec=None, cb_min=None, cb_max=None):
    if cb_min is None:
        cb_min = get_colorbar_min()
    if cb_max is None:
        cb_max = get_colorbar_max()
    if prec is None:
        prec = bpy.context.scene.colorbar_prec
    step = (cb_max - cb_min) / (ticks_num - 1)
    ticks = np.arange(cb_min, cb_max + step, step)
    return [str(mu.round_n_digits(x, prec)) for x in ticks]
    # return [PERC_FORMATS[prec].format(x) for x in ticks]


def get_colormaps_names():
    return ColorbarPanel.maps_names


def set_colormap(colormap_name):
    if colormap_name in ColorbarPanel.maps_names:
        ColorbarPanel.should_not_lock_values = True
        # print('set_colormap: {}'.format(colormap_name))
        # print(mu.print_traceback())
        bpy.context.scene.colorbar_files = colormap_name
        ColorbarPanel.should_not_lock_values = False
    elif colormap_name is not None:
        print('No such colormap! {}'.format(colormap_name))


def get_colormap():
    return bpy.context.scene.colorbar_files


def get_colorbar_figure_fname():
    return op.join(_addon().get_output_path(), '{}_colorbar.jpg'.format(get_colormap()))


def get_cb_ticks_num():
    return bpy.context.scene.cb_ticks_num


def set_cb_ticks_num(val):
    bpy.context.scene.cb_ticks_num = val


def get_cb_ticks_font_size():
    return bpy.context.scene.cb_ticks_font_size


def set_cb_ticks_font_size(val):
    bpy.context.scene.cb_ticks_font_size = val


def hide_cb_center_update(self, context):
    hide_center(bpy.context.scene.hide_cb_center)


def hide_center(do_hide):
    n = len(bpy.data.objects['cCB'].children)
    for cb in bpy.data.objects['cCB'].children:
        if not do_hide:
            cb.hide = False
        num = int(cb.name.split('.')[-1])
        if do_hide and n / 2 - 10 < num < n / 2 + 10:
            cb.hide = True


def show_progress(progress):
    cb_prog = len(bpy.data.objects['cCB'].children) * (progress / 100)
    for ind, cb in enumerate(bpy.data.objects['cCB'].children):
        cb.hide = ind > cb_prog


def colormap_update(self, context):
    if ColorbarPanel.init:
        load_colormap()
        if not ColorbarPanel.should_not_lock_values:
            lock_colorbar_values()


def colorbar_update(self, context):
    if ColorbarPanel.init:
        ColorbarPanel.colorbar_updated = True
        set_colorbar_title(bpy.context.scene.colorbar_title)
        set_colorbar_max(bpy.context.scene.colorbar_max)
        set_colorbar_min(bpy.context.scene.colorbar_min)
        if not ColorbarPanel.should_not_lock_values:
            lock_colorbar_values()
        # todo: we shouldn't change coloring_use_abs, because in some cases the user will want to plot only the
        # positive values (fMRI for example)
        # bpy.context.scene.coloring_use_abs = np.sign(bpy.context.scene.colorbar_max) != \
        #                                      np.sign(bpy.context.scene.colorbar_min)


def show_vertical_cb_update(self, context):
    if bpy.context.scene.show_vertical_cb is True:
        bpy.data.objects['full_colorbar'].rotation_euler[1] = 0
        bpy.context.window.screen = bpy.data.screens['Neuro_vertical_colorbar']
    else:
        bpy.data.objects['full_colorbar'].rotation_euler[1] = np.pi/2.0
        bpy.context.window.screen = bpy.data.screens['Neuro']


def show_cb_in_render_update(self, context):
    show_cb_in_render(bpy.context.scene.show_cb_in_render)


def show_cb_in_render(val=True):
    mu.show_hide_hierarchy(val, 'colorbar_camera', True, False)
    mu.show_hide_hierarchy(val, 'cCB_camera', True, False)


def colorbar_y_update(self, context):
    bpy.data.objects['cCB'].location[0] = -bpy.context.scene.colorbar_y


def colorbar_text_y_update(self, context):
    bpy.data.objects['colorbar_max'].location[0] = -bpy.context.scene.colorbar_text_y
    bpy.data.objects['colorbar_min'].location[0] = -bpy.context.scene.colorbar_text_y
    bpy.data.objects['colorbar_title'].location[0] = -bpy.context.scene.colorbar_text_y


def colorbar_draw(self, context):
    layout = self.layout
    layout.prop(context.scene, "colorbar_files", text="")
    layout.prop(context.scene, "colorbar_title", text="Title:")
    row = layout.row(align=0)
    row.prop(context.scene, "colorbar_min", text="min:")
    row.prop(context.scene, "colorbar_max", text="max:")
    if np.sign(bpy.context.scene.colorbar_min) != np.sign(bpy.context.scene.colorbar_max):
        layout.prop(context.scene, 'hide_cb_center', text='Hide center')
    layout.prop(context.scene, 'colorbar_prec', text='precision')
    layout.prop(context.scene, 'lock_min_max', text='Lock values')
    if bpy.data.screens.get('Neuro_vertical_colorbar') is not None:
        layout.prop(context.scene, 'show_vertical_cb', text='Show vertical colorbar')
    # layout.prop(context.scene, 'show_cb_in_render', text='Show in rendering')
    layout.prop(context.scene, 'update_cb_location', text='Update location')
    if bpy.context.scene.update_cb_location:
        layout.prop(context.scene, "colorbar_y", text="y axis")
        layout.prop(context.scene, "colorbar_text_y", text="text y axis")
    # layout.operator(ColorbarButton.bl_idname, text="Do something", icon='ROTATE')


class ColorbarButton(bpy.types.Operator):
    bl_idname = "mmvt.colorbar_button"
    bl_label = "Colorbar botton"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        load_colormap()
        return {'PASS_THROUGH'}


bpy.types.Scene.colorbar_files = bpy.props.EnumProperty(items=[], update=colormap_update,
    description='Selects the colorbar color palette.\n\nCurrent palette')
bpy.types.Scene.colorbar_max = bpy.props.FloatProperty(update=colorbar_update, description='Sets the maximum value of the colorbar')
bpy.types.Scene.colorbar_min = bpy.props.FloatProperty(update=colorbar_update, description='Sets the minimum value of the colorbar')
bpy.types.Scene.colorbar_title = bpy.props.StringProperty(update=colorbar_update,
    description='Renames the colorbar’s title in the display area.\n\nScript mmvt.colorbar.get_colorbar_title() and set_colorbar_title(val)')
bpy.types.Scene.colorbar_prec = bpy.props.IntProperty(min=0, default=2, max=15, update=colorbar_update,
    description='Sets the number of the decimal places in the colorbar.\n\nScript: mmvt.colorbar.get_colorbar_prec() and set_colorbar_prec(val)')
bpy.types.Scene.show_cb_in_render = bpy.props.BoolProperty(
    default=True, description="show_cb_in_render", update=show_cb_in_render_update)
bpy.types.Scene.show_vertical_cb = bpy.props.BoolProperty(default=True, description="show_vertical_cb", update=show_vertical_cb_update)
bpy.types.Scene.hide_cb_center = bpy.props.BoolProperty(default=False, update=hide_cb_center_update, description='Hides the center of the colorbar')
bpy.types.Scene.update_cb_location = bpy.props.BoolProperty(default=False, description='Centers the colorbar position in the display area')
bpy.types.Scene.colorbar_y = bpy.props.FloatProperty(min=-2, max=2, default=0, update=colorbar_y_update)
bpy.types.Scene.colorbar_text_y = bpy.props.FloatProperty(min=-2, max=2, default=0, update=colorbar_text_y_update)
bpy.types.Scene.lock_min_max = bpy.props.BoolProperty(default=False, description='Locks the colorbar values')


class ColorbarPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Colorbar"
    addon = None
    init = False
    colorbar_updated = False
    cm = None
    maps_names = []
    should_not_lock_values = False
    default_cm = ('RdOrYl', 'PuBu', 'BuPu-YlOrRd') # ''YlOrRd'

    def draw(self, context):
        if ColorbarPanel.init:
            colorbar_draw(self, context)


def init(addon):
    if not bpy.data.objects.get('full_colorbar', None):
        print("No full_colorbar object, Can't load the colorbar panel")
        return
    ColorbarPanel.addon = addon
    colorbar_files_fol = mu.make_dir(op.join(mu.get_parent_fol(mu.get_user_fol()), 'color_maps'))
    colorbar_files_code_fol = op.join(mu.get_resources_dir(), 'color_maps')
    colorbar_files_template = op.join(colorbar_files_fol, '*.npy')
    colorbar_files_code_template = op.join(colorbar_files_code_fol, '*.npy')
    # colorbar_files_template = op.join(mu.file_fol(), 'color_maps', '*.npy')
    colorbar_files = glob.glob(colorbar_files_template)
    colorbar_code_files = glob.glob(colorbar_files_code_template)
    extra_files = list(set([mu.namebase_with_ext(f) for f in colorbar_code_files]) -
                       set([mu.namebase_with_ext(f) for f in colorbar_files]))
    for extra_file in extra_files:
        print('Coping missing cb file: {}'.format(mu.namebase_with_ext(extra_file)))
        shutil.copyfile(op.join(colorbar_files_code_fol, extra_file),
                        op.join(colorbar_files_fol, mu.namebase_with_ext(extra_file)))
    if len(colorbar_files) == 0:
        print("No colorbar files ({}), Can't load the colorbar panel".format(colorbar_files_template))
        return None
    colorbar_files = glob.glob(colorbar_files_template)
    files_names = [mu.namebase(fname) for fname in colorbar_files] # .replace('_', '-')
    ColorbarPanel.maps_names = files_names
    colorbar_items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
    bpy.types.Scene.colorbar_files = bpy.props.EnumProperty(
        items=colorbar_items,update=colormap_update, description='Selects the colorbar color palette.\n\nCurrent palette')
    if not colorbar_values_are_locked():
        bpy.context.scene.colorbar_files = files_names[0]
    else:
        load_colormap()
    for space in mu.get_3d_spaces():
        if space.lock_object and space.lock_object.name == 'full_colorbar':
            space.show_only_render = True
    register()
    ColorbarPanel.init = True
    bpy.context.scene.show_cb_in_render = False
    mu.select_hierarchy('colorbar_camera', False, False)
    if not ColorbarPanel.colorbar_updated and not colorbar_values_are_locked():
        ColorbarPanel.should_not_lock_values = True
        # bpy.context.scene.colorbar_min = -1
        # bpy.context.scene.colorbar_max = 1
        # bpy.context.scene.colorbar_title = '     MEG'
        bpy.context.scene.colorbar_y = 0.18
        bpy.context.scene.colorbar_text_y = -1.53
        bpy.context.scene.colorbar_prec = 2
        ColorbarPanel.should_not_lock_values = False
    # if not colorbar_values_are_locked():
    #     if 'fMRI' in bpy.context.scene.colorbar_title:
    #         bpy.context.scene.colorbar_files = 'PuBu-RdOrYl'
    #     else:
    #         bpy.context.scene.colorbar_files = 'BuPu-YlOrRd'


def register():
    try:
        unregister()
        bpy.utils.register_class(ColorbarPanel)
        bpy.utils.register_class(ColorbarButton)
    except:
        print("Can't register Colorbar Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(ColorbarPanel)
        bpy.utils.unregister_class(ColorbarButton)
    except:
        pass
