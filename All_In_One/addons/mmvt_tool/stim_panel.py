import bpy
import os.path as op
import glob
import numpy as np
import mmvt_utils as mu
import data_panel
import selection_panel
import play_panel


def _adoon():
    return StimPanel.addon

def stim_files_update(self, context):
    play_panel.init_stim()


def import_electrodes():
    electrodes_positions_fname = 'stim_electrodes_{}_positions.npz'.format(
        bpy.context.scene.stim_files.replace(' ', '_'))
    data_panel.import_electrodes(op.join(mu.get_user_fol(), 'electrodes', electrodes_positions_fname))


def load_stim_data():
    stim_fname = 'stim_electrodes_{}.npz'.format(bpy.context.scene.stim_files.replace(' ', '_'))
    stim_data_fname = op.join(mu.get_user_fol(), 'electrodes', stim_fname)
    # todo: maybe create new electrodes in a different layer
    try:
        data_panel.add_data_to_electrodes([stim_data_fname])
    except:
        print("Can't load the stim data!")
    load_conditions()


def load_conditions():
    stim_fname = 'stim_electrodes_{}.npz'.format(bpy.context.scene.stim_files.replace(' ', '_'))
    stim_data_fname = op.join(mu.get_user_fol(), 'electrodes', stim_fname)
    stim_data = np.load(stim_data_fname)
    conditions = sorted(stim_data['conditions'], key=lambda x:int(x.split('-')[0]))
    selection_panel.set_conditions_enum(conditions)


def stim_draw(self, context):
    layout = self.layout
    layout.prop(context.scene, 'stim_files', text='')
    # layout.operator(ImportStimElectrodes.bl_idname, text="Import the electrodes", icon='RNA_ADD')
    if bpy.data.objects.get(_addon().electrodes_panel_parent, None):
        layout.operator(LoadStim.bl_idname, text="Load the data", icon='RNA_ADD')
        layout.operator(LoadStimConditions.bl_idname, text="Load the frequencies", icon='RNA_ADD')


class ImportStimElectrodes(bpy.types.Operator):
    bl_idname = "mmvt.import_stim_electrodes"
    bl_label = "Import the stim electrodes"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        import_electrodes()
        return {'PASS_THROUGH'}


class LoadStimConditions(bpy.types.Operator):
    bl_idname = "mmvt.load_stim_conditions"
    bl_label = "Load the stim conditions"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        load_conditions()
        return {'PASS_THROUGH'}


class LoadStim(bpy.types.Operator):
    bl_idname = "mmvt.load_stim"
    bl_label = "Load the stim data"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        load_stim_data()
        return {'PASS_THROUGH'}


bpy.types.Scene.stim_files = bpy.props.EnumProperty(items=[], description="stim files")


class StimPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Stimulation"
    addon = None
    init = False

    def draw(self, context):
        if StimPanel.init:
            stim_draw(self, context)


def init(addon):
    user_fol = mu.get_user_fol()
    stim_files = glob.glob(op.join(user_fol, 'electrodes', 'stim_electrodes_*.npz'))
    stim_files = [sf for sf in stim_files if 'positions' not in sf]
    # stim_positions_files = glob.glob(op.join(user_fol, 'electrodes', 'stim_electrodes*positions.npz'))
    if len(stim_files) == 0:
        return None
    StimPanel.addon = addon
    files_names = [mu.namebase(fname)[len('stim_electrodes_'):].replace('_', ' ') for fname in stim_files]
    stim_items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
    bpy.types.Scene.stim_files = bpy.props.EnumProperty(
        items=stim_items, description='stim files', update=stim_files_update)
    bpy.context.scene.stim_files = files_names[0]
    load_conditions()
    register()
    StimPanel.init = True


def register():
    try:
        unregister()
        bpy.utils.register_class(StimPanel)
        bpy.utils.register_class(ImportStimElectrodes)
        bpy.utils.register_class(LoadStim)
        bpy.utils.register_class(LoadStimConditions)
    except:
        print("Can't register Stim Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(StimPanel)
        bpy.utils.unregister_class(ImportStimElectrodes)
        bpy.utils.unregister_class(LoadStim)
        bpy.utils.unregister_class(LoadStimConditions)
    except:
        pass
