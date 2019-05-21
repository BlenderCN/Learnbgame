import bpy
import mmvt_utils as mu
import numpy as np
import os.path as op
import mathutils
import time
import glob
import sys
from sys import platform as _platform
import re

# MAC_FREEVIEW_CMD = '/Applications/freesurfer/Freeview.app/Contents/MacOS/Freeview'

def _addon():
    return FreeviewPanel.addon

bpy.types.Scene.freeview_listen_to_keyboard = bpy.props.BoolProperty(default=False)
bpy.types.Scene.freeview_listener_is_running = bpy.props.BoolProperty(default=False)


def save_cursor_position(pos=None):
    # _addon().create_slices(pos=pos) # Don't call here create_slices!!!
    pos = mathutils.Vector(pos) if not pos is None else bpy.context.scene.cursor_location
    root = mu.get_user_fol()
    point = pos * 10.0
    freeview_cmd = 'freeview --ras {} {} {} tkreg\n'.format(point[0], point[1], point[2]) # .encode()
    if FreeviewPanel.freeview_in_queue:
        FreeviewPanel.freeview_in_queue.put(freeview_cmd)
    freeview_fol = op.join(root, 'freeview')
    mu.make_dir(freeview_fol)
    # print('Cursor was saved in {}'.format(op.join(freeview_fol, 'edit.dat')))
    np.savetxt(op.join(freeview_fol, 'edit.dat'), point)
    # cursor_position = np.array(pos) * 10
    # ret = mu.conn_to_listener.send_command(dict(cmd='slice_viewer_change_pos',data=dict(
    #     position=cursor_position)))
    # if not ret:
    #     mu.message(None, 'Listener was stopped! Try to restart')


def goto_cursor_position():
    root = mu.get_user_fol()
    point = np.genfromtxt(op.join(root, 'freeview', 'edit.dat'))
    bpy.context.scene.cursor_location = tuple(point / 10.0)


def freeview_save_cursor():
    if _addon().is_inflated():  # and _addon().get_inflated_ratio() == 1:
        closest_mesh_name, vertex_ind, vertex_co = _addon().find_closest_vertex_index_and_mesh(
            use_shape_keys=True)
        bpy.context.scene.cursor_location = vertex_co
        pial_mesh = 'rh' if closest_mesh_name == 'inflated_rh' else 'lh'
        pial_vert = bpy.data.objects[pial_mesh].data.vertices[vertex_ind]
        cursor = pial_vert.co / 10
    else:
        cursor = bpy.context.scene.cursor_location
    save_cursor_position(cursor)


def open_freeview():
    root = mu.get_user_fol()
    sig_cmd = ''
    if bpy.context.scene.fMRI_files_exist and bpy.context.scene.freeview_load_fMRI:
        sig_fnames = glob.glob(op.join(root, 'freeview', '*{}*.mgz'.format(bpy.context.scene.fmri_files))) + \
                     glob.glob(op.join(root, 'freeview', '*{}*.nii'.format(bpy.context.scene.fmri_files)))
        if len(sig_fnames) > 0:
            sig_fname = sig_fnames[0]
            sig_cmd = '-v "{}":colormap=heat:heatscale=2,3,6 '.format(sig_fname) if op.isfile(sig_fname) else ''
    ct_cmd = ''
    if bpy.context.scene.freeview_load_CT:
        mmvt_ct_fname = op.join(root, 'ct', 'ct_reg_to_mr.mgz')
        if FreeviewPanel.CT_files_exist:
            ct_cmd = '-v "{}":opacity=0 '.format(mmvt_ct_fname)
        else:
            print("Can't find CT {}!".format(mmvt_ct_fname))
    dura_cmd = ''
    if bpy.context.scene.freeview_load_dura:
        dura_fname = FreeviewPanel.dura_srf_fname
        if FreeviewPanel.dura_srf_exist:
            dura_cmd = '-f "{}":edgecolor=blue "{}":edgecolor=blue '.format(
                dura_fname.format(hemi='rh'), dura_fname.format(hemi='lh'))
    T1 = op.join(root, 'freeview', 'T1.mgz')  # sometimes 'orig.mgz' is better
    if not op.isfile(T1):
        T1 = op.join(root, 'freeview', 'orig.mgz')
    if not op.isfile(T1):
        print('No T1 / orig files in freeview folder. Running preproc.freeview')
        bpy.context.scene.freeview_messages = 'Preparing... Try to run again'
        # cmd = '{} -m src.preproc.freeview -s {} -a {} -b {} --ignore_missing 1'.format(
        #     bpy.context.scene.python_cmd, mu.get_user(), bpy.context.scene.atlas, bpy.context.scene.bipolar)
        # mu.run_command_in_new_thread(cmd, False)
        flags = '-a {} -b {}'.format(bpy.context.scene.atlas, bpy.context.scene.bipolar)
        mu.run_mmvt_func('src.preproc.freeview', flags=flags)
        return {'RUNNING_MODAL'}
    bpy.context.scene.freeview_messages = ''
    aseg = op.join(root, 'freeview', '{}+aseg.mgz'.format(bpy.context.scene.atlas))
    if op.isfile(aseg):
        lut = op.join(root, 'freeview', '{}ColorLUT.txt'.format(bpy.context.scene.atlas))
        aseg_cmd = '"{}":opacity=0.05:colormap=lut:lut="{}"'.format(aseg, lut)
    else:
        aseg_cmd = ''
    electrodes_cmd = get_electrodes_command(root)
    cmd = '{} "{}":opacity=0.5 {}{}{}{}{}{}{}'.format(
        FreeviewPanel.addon_prefs.freeview_cmd, T1, aseg_cmd, electrodes_cmd, sig_cmd, ct_cmd, dura_cmd,
        ' -verbose' if FreeviewPanel.addon_prefs.freeview_cmd_verbose else '',
        ' -stdin' if FreeviewPanel.addon_prefs.freeview_cmd_stdin else '')
    print(cmd)
    FreeviewPanel.freeview_in_queue, FreeviewPanel.freeview_out_queue = mu.run_command_in_new_thread(
        cmd)#, read_stderr=reading_freeview_stderr_func, read_stdin=reading_freeview_stdin_func,
        # stdout_func=reading_freeview_stdout_func)


def reading_freeview_stdin_func():
    return FreeviewPanel.freeview_is_open


def reading_freeview_stdout_func():
    return FreeviewPanel.freeview_is_open


def reading_freeview_stderr_func():
    return FreeviewPanel.freeview_is_open


def get_electrodes_command(root):
    if bpy.data.objects.get('Deep_electrodes') and bpy.context.scene.freeview_load_electrodes:
        cmd = ' -c '
        # groups = set([mu.elec_group(obj.name, bpy.context.scene.bipolar)
        #               for obj in bpy.data.objects['Deep_electrodes'].children])
        for group in FreeviewPanel.electrodes_groups:
            cmd += '"{}" '.format(op.join(root, 'freeview', '{}.dat'.format(group)))
    else:
        cmd = ''
    return cmd


# class FreeviewKeyboardListener(bpy.types.Operator):
#     bl_idname = 'mmvt.freeview_keyboard_listener'
#     bl_label = 'freeview_keyboard_listener'
#     bl_options = {'UNDO'}
#     press_time = time.time()
#
#     def modal(self, context, event):
#         if time.time() - self.press_time > 1 and bpy.context.scene.freeview_listen_to_keyboard and \
#                 event.type not in ['TIMER', 'MOUSEMOVE', 'WINDOW_DEACTIVATE', 'INBETWEEN_MOUSEMOVE', 'TIMER_REPORT', 'NONE']:
#             self.press_time = time.time()
#             print(event.type)
#             if event.type == 'LEFTMOUSE':
#                 save_cursor_position()
#             else:
#                 pass
#         return {'PASS_THROUGH'}
#
#     def invoke(self, context, event=None):
#         if not bpy.context.scene.freeview_listener_is_running:
#             context.window_manager.modal_handler_add(self)
#             bpy.context.scene.freeview_listener_is_running = True
#         bpy.context.scene.freeview_listen_to_keyboard = not bpy.context.scene.freeview_listen_to_keyboard
#         return {'RUNNING_MODAL'}


class FreeviewGotoCursor(bpy.types.Operator):
    bl_idname = "mmvt.freeview_goto_cursor"
    bl_label = "Goto Cursor"
    bl_description = 'Changes the cursor position that was saved in Freeview.\n\nScript: mmvt.freeview.goto_cursor_position()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        goto_cursor_position()
        return {"FINISHED"}


class FreeviewSaveCursor(bpy.types.Operator):
    bl_idname = "mmvt.freeview_save_cursor"
    bl_label = "Save Cursor"
    bl_description = 'Saves the MMVT cursor position to be viewed on Freeview.\n\nScript: mmvt.freeview.freeview_save_cursor()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        freeview_save_cursor()
        return {"FINISHED"}


class SliceViewerOpen(bpy.types.Operator):
    bl_idname = "mmvt.slice_viewer"
    bl_label = "Slice Viewer"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        mri_fname = op.join(mu.get_user_fol(), 'freeview', 'orig.mgz')
        cursor_position = np.array(bpy.context.scene.cursor_location) * 10.0
        ret = mu.conn_to_listener.send_command(dict(cmd='open_slice_viewer',data=dict(
            mri_fname=mri_fname, position=cursor_position)))
        if not ret:
            mu.message(self, 'Listener was stopped! Try to restart')
        return {"FINISHED"}


class CreateFreeviewFiles(bpy.types.Operator):
    bl_idname = "mmvt.create_freeview_files"
    bl_label = "CreateFreeviewFiles"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        electrodes_pos_fname = op.join(mu.get_user_fol(), 'electrodes', 'electrodes{}_positions.npz'.format(
            '_bipolar' if bpy.context.scene.bipolar else ''))
        flags = '-a {} -b {} --electrodes_pos_fname {} --ignore_missing 1'.format(
            bpy.context.scene.atlas, bpy.context.scene.bipolar, electrodes_pos_fname)
        mu.run_mmvt_func('src.preproc.freeview', flags=flags)
        bpy.context.scene.freeview_messages = 'Preparing...'
        return {"FINISHED"}


def decode_freesurfer_output(fv_str):
    # fv_str = str(b'\xc0\x8ak\x01tkReg: -8.23399;\x0f(\xa45 0\x96o) 1.28009\n')
    fv_str = str(fv_str)
    fv_str = fv_str.replace('\\xc0\\x8ak\\x01', '')
    fv_str = fv_str.replace('\\n', '')
    from_ind = fv_str.find('\\')
    ind = from_ind
    while from_ind != -1:
        ind2 = fv_str[ind + 1:].find(' ')
        ind3 = fv_str[ind + 1:].find('\\')
        if ind2 == -1 and ind3 == -1:
            ind_to = len(fv_str) - ind
        elif ind2 == -1 or ind3 == -1:
            ind_to = ind2 if ind3 == -1 else ind3
        else:
            ind_to = min([ind2, ind3])
        str_to_remove = fv_str[ind:ind_to + ind + 1]
        fv_str = fv_str.replace(str_to_remove, '')
        from_ind = fv_str[ind:].find('\\')
        ind += from_ind
    print('stdout after cleaning: {}'.format(fv_str))
    return fv_str


class FreeviewOpen(bpy.types.Operator):
    bl_idname = "mmvt.freeview_open"
    bl_label = "Open Freeview"
    bl_description = 'Opens Freeview'
    bl_options = {"UNDO"}
    _updating = False
    _calcs_done = False
    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER' and not self._updating:
            self._updating = True
            # print('Listening to the queue')
            if not FreeviewPanel.freeview_out_queue is None:
                from queue import Empty
                try:
                    freeview_data = FreeviewPanel.freeview_out_queue.get(block=False)
                    try:
                        print('stdout from freeview: {}'.format(freeview_data))
                        # data_deocded = freeview_data.decode(sys.getfilesystemencoding(), 'ignore')
                        data_deocded = decode_freesurfer_output(freeview_data)
                        if 'tkReg' in data_deocded:
                            point = mu.read_numbers_rx(data_deocded)
                            print(point)
                            bpy.context.scene.cursor_location = tuple(np.array(point, dtype=np.float) / 10)
                            _addon().set_tkreg_ras(bpy.context.scene.cursor_location * 10)
                    except:
                        print("Can't read the stdout from freeview")
                except Empty:
                    pass
            self._updating = False
        if self._calcs_done:
            self.cancel(context)
        return {'PASS_THROUGH'}

    def cancel(self, context):
        try:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        except:
            pass
        return {'CANCELLED'}

    def invoke(self, context, event=None):
        if not FreeviewPanel.freeview_is_open:
            FreeviewPanel.freeview_is_open = True
            open_freeview()
            freeview_save_cursor()
            context.window_manager.modal_handler_add(self)
            self._updating = False
            self._timer = context.window_manager.event_timer_add(0.1, context.window)
        else:
            FreeviewPanel.freeview_is_open = False
            return self.cancel(context)
        return {'RUNNING_MODAL'}
        # return {"FINISHED"}


bpy.types.Scene.electrodes_exist = bpy.props.BoolProperty(default=True)
bpy.types.Scene.freeview_load_electrodes = bpy.props.BoolProperty(default=False,
    description='Loads the electrodes coordinates into Freeview')
bpy.types.Scene.fMRI_files_exist = bpy.props.BoolProperty(default=True)
bpy.types.Scene.freeview_load_fMRI = bpy.props.BoolProperty(default=True, description='Load fMRI')
bpy.types.Scene.freeview_load_CT = bpy.props.BoolProperty(default=True, description='Load CT')
bpy.types.Scene.freeview_load_dura = bpy.props.BoolProperty(default=True, description='Load dura')
bpy.types.Scene.freeview_messages = bpy.props.StringProperty()


class FreeviewPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Freeview"
    addon = None
    init = False
    freeview_in_queue = None
    freeview_out_queue = None
    freeview_is_open = False
    dura_srf_exist = False
    dura_srf_fname = ''

    def draw(self, context):
        layout = self.layout
        root = mu.get_user_fol()
        # row = layout.row(align=0)
        if bpy.data.objects.get('Deep_electrodes'):
            layout.prop(context.scene, 'freeview_load_electrodes', text="Load electrodes")
        all_electrodes_exist = True
        if bpy.data.objects.get('Deep_electrodes'):
            all_electrodes_exist = all([op.isfile(op.join(root, 'freeview', '{}.dat'.format(group)))
                                        for group in FreeviewPanel.electrodes_groups])
        if not all_electrodes_exist and bpy.context.scene.freeview_load_electrodes:
            layout.operator(CreateFreeviewFiles.bl_idname, text='Create Freeview files', icon='PARTICLES')
        else:
            text = 'Close Freeview' if FreeviewPanel.freeview_is_open else 'Open Freeview'
            layout.operator(FreeviewOpen.bl_idname, text=text, icon='PARTICLES')
            fmri_files_template = op.join(mu.get_user_fol(),
                    'freeview','*{}*.{}'.format(bpy.context.scene.fmri_files, '{format}'))
            fmri_vol_files = glob.glob(fmri_files_template.format(format='mgz')) + \
                             glob.glob(fmri_files_template.format(format='nii'))
            if bpy.context.scene.fMRI_files_exist and len(fmri_vol_files) > 0:
                layout.prop(context.scene, 'freeview_load_fMRI', text="Load fMRI")
            if FreeviewPanel.CT_files_exist:
                layout.prop(context.scene, 'freeview_load_CT', text="Load CT")
            if FreeviewPanel.dura_srf_exist:
                layout.prop(context.scene, 'freeview_load_dura', text="Load dura")
            row = layout.row(align=0)
            row.operator(FreeviewGotoCursor.bl_idname, text="Goto Cursor", icon='HAND')
            row.operator(FreeviewSaveCursor.bl_idname, text="Save Cursor", icon='FORCE_CURVE')

        if bpy.context.scene.freeview_messages != '':
            layout.label(text=context.scene.freeview_messages)
        # row = layout.row(align=0)
        # row.operator(SliceViewerOpen.bl_idname, text="Slice Viewer", icon='PARTICLES')
        # if not bpy.context.scene.freeview_listen_to_keyboard:
        #     layout.operator(FreeviewKeyboardListener.bl_idname, text="Listen to keyboard", icon='COLOR_GREEN')
        # else:
        #     layout.operator(FreeviewKeyboardListener.bl_idname, text="Stop listen to keyboard", icon='COLOR_RED')


def init(addon, addon_prefs=None):
    FreeviewPanel.addon = addon
    # print('freeview command: {}'.format(addon_prefs.freeview_cmd))
    # print('Use -verbose? {}'.format(addon_prefs.freeview_cmd_verbose))
    # print('Use -stdin? {}'.format(addon_prefs.freeview_cmd_stdin))
    FreeviewPanel.addon_prefs = addon_prefs
    bpy.context.scene.freeview_load_electrodes = False
    bpy.context.scene.freeview_listen_to_keyboard = False
    bpy.context.scene.freeview_listener_is_running = False
    bpy.context.scene.fMRI_files_exist = len(glob.glob(op.join(mu.get_user_fol(), 'fmri', '*_lh.npy'))) > 0
        #mu.hemi_files_exists(op.join(mu.get_user_fol(), 'fmri_{hemi}.npy'))
    bpy.context.scene.electrodes_exist = bpy.data.objects.get('Deep_electrodes', None) is not None
    if bpy.context.scene.electrodes_exist:
        FreeviewPanel.electrodes_groups = set([mu.elec_group(obj.name, bpy.context.scene.bipolar)
                      for obj in bpy.data.objects['Deep_electrodes'].children])
    else:
        FreeviewPanel.electrodes_groups = []
    bpy.context.scene.freeview_messages = ''
    root = mu.get_user_fol()
    mmvt_ct_fname = op.join(root, 'ct', 'ct_reg_to_mr.mgz')
    # if not op.isfile(mmvt_ct_fname):
    #     subjects_ct_fname = op.join(mu.get_subjects_dir(), mu.get_user(), 'mri', 'ct_nas.nii.gz')
    #     if op.isfile(subjects_ct_fname):
    #         shutil.copy(subjects_ct_fname, mmvt_ct_fname)
    FreeviewPanel.CT_files_exist = op.isfile(mmvt_ct_fname)
    if mu.both_hemi_files_exist(op.join(mu.get_subjects_dir(), mu.get_user(), 'surf', '{hemi}.dural')):
        FreeviewPanel.dura_srf_exist = True
        FreeviewPanel.dura_srf_fname = op.join(mu.get_subjects_dir(), mu.get_user(), 'surf', '{hemi}.dural')
    elif mu.both_hemi_files_exist(op.join(mu.get_user_fol(), 'surf', '{hemi}.dural')):
        FreeviewPanel.dura_srf_exist = True
        FreeviewPanel.dura_srf_fname = op.join(mu.get_user_fol(), mu.get_user(), 'surf', '{hemi}.dural')
    else:
        FreeviewPanel.dura_srf_exist = False

    FreeviewPanel.init = True
    FreeviewPanel.freeview_is_open = False
    register()


def register():
    try:
        unregister()
        bpy.utils.register_class(FreeviewGotoCursor)
        bpy.utils.register_class(FreeviewSaveCursor)
        bpy.utils.register_class(FreeviewOpen)
        bpy.utils.register_class(CreateFreeviewFiles)
        bpy.utils.register_class(FreeviewPanel)
        bpy.utils.register_class(SliceViewerOpen)
        # bpy.utils.register_class(FreeviewKeyboardListener)
        # print('Freeview Panel was registered!')
    except:
        print("Can't register Freeview Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(FreeviewGotoCursor)
        bpy.utils.unregister_class(FreeviewSaveCursor)
        bpy.utils.unregister_class(FreeviewOpen)
        bpy.utils.unregister_class(CreateFreeviewFiles)
        bpy.utils.unregister_class(FreeviewPanel)
        bpy.utils.unregister_class(SliceViewerOpen)
        # bpy.utils.unregister_class(FreeviewKeyboardListener)
    except:
        pass
        # print("Can't unregister Freeview Panel!")
