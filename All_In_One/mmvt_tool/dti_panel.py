import bpy
import numpy as np
import os.path as op
import time
import mmvt_utils as mu
import os
import glob
from pprint import pprint

PARENT_OBJ = 'dti'
TRACULA = 'tracula'
SUBJECT_DTI_FOL = op.join(mu.get_user_fol(), 'dti')

TRACULA_PATHWAYS_DIC = {
    'lh.cst_AS': 'Left corticospinal tract',
    'rh.cst_AS': 'Right corticospinal tract',
    'lh.ilf_AS': 'Left inferior longitudinal fasciculus',
    'rh.ilf_AS': 'Right inferior longitudinal fasciculus',
    'lh.unc_AS': 'Left uncinate fasciculus',
    'rh.unc_AS': 'Right uncinate fasciculus',
    'fmajor_PP': 'Corpus callosum - forceps major',
    'fminor_PP': 'Corpus callosum - forceps minor',
    'lh.atr_PP': 'Left anterior thalamic radiations',
    'rh.atr_PP': 'Right anterior thalamic radiations',
    'lh.ccg_PP': 'Left cingulum - cingulate gyrus endings',
    'rh.ccg_PP': 'Right cingulum - cingulate gyrus endings',
    'lh.cab_PP': 'Left cingulum - angular bundle',
    'rh.cab_PP': 'Right cingulum - angular bundle',
    'lh.slfp_PP': 'Left superior longitudinal fasciculus - parietal endings',
    'rh.slfp_PP': 'Right superior longitudinal fasciculus - parietal endings',
    'lh.slft_PP': 'Left superior longitudinal fasciculus - temporal endings',
    'rh.slft_PP': 'Right superior longitudinal fasciculus - temporal endings'
}

TRACULA_POSTFIX = '_avg33_mni_bbr'


def set_dti_pathways(self=None, value=None):
    if bpy.context.scene.dti_type == TRACULA:
        bpy.types.Scene.dti_pathways = bpy.props.EnumProperty(items=get_tracula_pathways(), description="pathways")


def get_tracula_pathways():
    pathways = [get_group_name(pkl_fname) for pkl_fname in glob.glob(op.join(SUBJECT_DTI_FOL, TRACULA, '*.pkl'))]
    items = [(pathway, TRACULA_PATHWAYS_DIC[pathway], '', ind) for ind, pathway in enumerate(pathways)]
    items = sorted(items, key=lambda x:x[1])
    return items


def get_group_name(pkl_fname):
    pathway = mu.namebase(pkl_fname)
    pathway = pathway[:-len(TRACULA_POSTFIX)]
    return pathway


def plot_pathway(self, context, layers_dti, pathway_name, pathway_type):
    if pathway_type == TRACULA:
        pkl_fname = op.join(SUBJECT_DTI_FOL, TRACULA, '{}{}.pkl'.format(pathway_name, TRACULA_POSTFIX))
        mu.create_empty_if_doesnt_exists(pathway_name, DTIPanel.addon.CONNECTIONS_LAYER, None, PARENT_OBJ)
        parent_obj = bpy.data.objects[pathway_name]
        tracks = mu.load(pkl_fname)
        N = len(tracks)
        now = time.time()
        for ind, track in enumerate(tracks[:1000]):
            mu.time_to_go(now, ind, N, 100)
            track = track * 0.1
            # pprint(track)
            cur_obj = mu.create_spline(track, layers_dti, bevel_depth=0.01)
            # cur_obj.scale = [0.1] * 3
            cur_obj.name = '{}_{}'.format(pathway_name, ind)
            cur_obj.parent = parent_obj


class PlotPathway(bpy.types.Operator):
    bl_idname = "mmvt.plot_pathway"
    bl_label = "mmvt plt pathway"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        if not bpy.data.objects.get(PARENT_OBJ):
            self.report({'ERROR'}, 'No parent node was found, you first need to create the connections.')
        else:
            pathway_type = bpy.context.scene.dti_type
            pathway_name = bpy.context.scene.dti_pathways
            layers_dti = [False] * 20
            dti_layer = DTIPanel.addon.CONNECTIONS_LAYER
            layers_dti[dti_layer] = True
            plot_pathway(self, context, layers_dti, pathway_name, pathway_type)
        return {"FINISHED"}


def dti_draw(self, context):
    layout = self.layout
    layout.prop(context.scene, "dti_type", text="")
    layout.prop(context.scene, "dti_pathways", text="")
    layout.operator(PlotPathway.bl_idname, text="plot pathway", icon='POTATO')


bpy.types.Scene.dti_type = bpy.props.EnumProperty(items=[(TRACULA, TRACULA, "", 1)], description="DTI source",
                                                  set=set_dti_pathways)
bpy.types.Scene.dti_pathways = bpy.props.EnumProperty(items=get_tracula_pathways(), description="pathways")


class DTIPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "DTI"
    addon = None
    init = False
    # d = mu.Bag({})

    def draw(self, context):
        dti_draw(self, context)


def check_for_dti_files():
    # Check if the dti files exist
    pathway_types = [TRACULA]
    for pathway_type in pathway_types:
        if pathway_type == TRACULA:
            pathways = [get_group_name(pkl_fname) for pkl_fname in glob.glob(op.join(SUBJECT_DTI_FOL, TRACULA, '*.pkl'))]
    return len(pathways) > 0


def init(addon):
    if not check_for_dti_files():
        unregister()
        DTIPanel.init = False
    else:
        register()
        DTIPanel.addon = addon
        mu.create_empty_if_doesnt_exists(PARENT_OBJ, addon.BRAIN_EMPTY_LAYER, None, 'Brain')
        DTIPanel.init = True
        # DTIPanel.d = d
        # print('DRI panel initialization completed successfully!')


def register():
    try:
        unregister()
        bpy.utils.register_class(DTIPanel)
        bpy.utils.register_class(PlotPathway)
        # print('DTI Panel was registered!')
    except:
        print("Can't register DTI Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(DTIPanel)
        bpy.utils.unregister_class(PlotPathway)
    except:
        pass
        # print("Can't unregister DTI Panel!")

