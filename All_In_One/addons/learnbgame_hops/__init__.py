'''
Copyright (C) 2015 masterxeon1001
masterxeon1001@gmail.com

Created by masterxeon1001 and team

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


bl_info = {
    "name": "Hard Ops 9",
    "description": "Hard Ops 9 - V7: Eeveium",
    "author": "MX, IS, RF, JM, AR, BF, SE, PL, MKB, CGS, PG, AX, proxe, Adam K, Wazou, Pistiwique, Jacques, MACHIN3 and you",
    "version": (0, 0, 9, 7, 3),
    "blender": (2, 80, 0),
    "location": "View3D",
    # "warning": "Hard Ops - The Global Bevelling Offensive V 007x",
    "wiki_url": "https://masterxeon1001.com/2018/11/29/hard-ops-0097-2-8-release-notes/",
    "category": "Learnbgame",
    }


# from . import developer_utils

import bpy,bgl,blf
from bpy.utils import register_class, unregister_class
from .registration import register_all, unregister_all
from .add_object_to_selection import *
from .extend_bpy_types import *
from .preferences import *
from .material import *
from .mesh_check import *
from .ui_popup import *

from .graphics.rectangle import *

from .icons.__init__ import *

from .legacy.ops_meshtools import *
from .legacy.ops_misc import *
from .legacy.ops_sets import *
from .legacy.ops_sharpeners import *


from .operators.booleans.bool_difference import *
from .operators.booleans.bool_intersection import *
from .operators.booleans.bool_union import *
from .operators.booleans.editmode_difference import *
from .operators.booleans.editmode_union import *

from .operators.cutters.complex_split_boolean import *
from .operators.cutters.cutin import *
from .operators.cutters.slash import *

from .operators.editmode.analysis import *
from .operators.editmode.bevel_weight import *
from .operators.editmode.circle import *
from .operators.editmode.set_bevel_weight import *
from .operators.editmode.star_connect import *

from .operators.Gizmos.mirror import *
from .operators.Gizmos.main import *
from .operators.Gizmos.hops_tool import *
from .operators.Gizmos.array import *

from .operators.meshtools.mesh_clean import *
from .operators.meshtools.meshtools import *
from .operators.meshtools.sclean_rc import *
from .operators.misc.bevel_multiplier import *
from .operators.misc.boolshape_status_swap import *
from .operators.misc.curve_toolsV1 import *
from .operators.misc.decalmachinefix import *
from .operators.misc.empty_image_tools import *
from .operators.misc.mesh_reset import *
from .operators.misc.mesh_toolsV2 import *
from .operators.misc.mirrormirror import *
from .operators.misc.open_keymap_for_editing import *
from .operators.misc.reset_axis import *
from .operators.misc.shrinkwrap import *
from .operators.misc.shrinkwrap2 import *
from .operators.misc.sphere_cast import *
from .operators.misc.toggle_bools import *
from .operators.misc.triangulate_ngons import *

from .operators.modals.adjust_array import *
from .operators.modals.adjust_bevel import *
from .operators.modals.adjust_bevel2d import *
from .operators.modals.adjust_curve import *
from .operators.modals.adjust_tthick import *
from .operators.modals.bool_object_scroll import *
from .operators.modals.bool_regular_scroll import *
from .operators.modals.curve_guide_setup import *
from .operators.modals.curve_guide_setup import *
from .operators.modals.curve_stretch_setup import *
from .operators.modals.mirror import *
from .operators.modals.reset_axis import *

from .operators.preferences.modifiers import *
from .operators.preferences.preferences import *
from .operators.preferences.set_sharpness import *
from .operators.preferences.sharp_manager import *

from .operators.sculpt.brush_toggle import *
from .operators.sculpt.sculpt_tools import *

from .operators.sharpeners.clear_ssharps import *
from .operators.sharpeners.complex_sharpen import *
from .operators.sharpeners.octane_meshsetup import *
from .operators.sharpeners.soft_sharpen import *
from .operators.sharpeners.step import *

from .operators.UV_tools.uv_draw import *
from .operators.UV_tools.x_unwrap import *


from .ui.Panels.a0_help import *
from .ui.Panels.a1_sharpening import *
from .ui.Panels.a2_inserts import *
from .ui.Panels.a3_dynamic_tools import *
from .ui.Panels.a4_operations import *
from .ui.Panels.a5_Booleans import *
from .ui.Panels.a6_meshtools import *
from .ui.Panels.a7_options import *
from .ui.Submenus.inserts import *
from .ui.Submenus.operators import *
from .ui.Submenus.settings import *
from .ui.Submenus.sub_menus import *
from .ui.Submenus.tools import *
from .ui.hops_helper import *
from .ui.main_menu import *
from .ui.main_pie import *
from .ui.status_helper import *

from .utils.context import *
from .utils.blender_ui import *


classes = (
    HOPS_OT_SelectedToSelection,
    HOpsObjectProperties,
    HopsMaterialOptions,
    HOPS_OT_NewMaterial,
    HOPS_OT_AddMaterials,
    HOPS_OT_RemoveMaterials,
    HopsMeshCheckCollectionGroup,
    HOPS_OT_DataOpFaceTypeSelect,
    HardOpsPreferences,
    HOPS_OT_LearningPopup,
    HOPS_OT_InsertsPopupPreview,
    HOPS_OT_AddonPopupPreview,
    HOPS_OT_PizzaPopupPreview,
    # Rectangle,
    # IconsMock,
    HOPS_OT_FacegrateOperator,
    HOPS_OT_FaceknurlOperator,
    HOPS_OT_EntrenchOperatorA,
    HOPS_OT_PanelOperatorA,
    HOPS_OT_StompObjectnoloc,
    HOPS_OT_MakeLink,
    HOPS_OT_SolidAll,
    HOPS_OT_ReactivateWire,
    HOPS_OT_ShowOverlays,
    HOPS_OT_HideOverlays,
    HOPS_OT_UnLinkObjects,
    HOPS_OT_ApplyMaterial,
    HOPS_OT_DeleteModifiers,
    HOPS_OT_BevelWeighSwap,
    HOPS_OT_MaterialOtSimplifyNames,
    HOPS_OT_renset1Operator,
    HOPS_OT_renset2Operator,
    #HOPS_OT_renset3Operator,
    #HOPS_OT_renset4Operator,
    HOPS_OT_ReguiOperator,
    HOPS_OT_CleanuiOperator,
    #HOPS_OT_RedmodeOperator,
    #HOPS_OT_NormodeOperator,
    #HOPS_OT_SilhouettemodeOperator,
    HOPS_OT_EndframeOperator,
    HOPS_OT_MeshdispOperator,
    HOPS_OT_UnsharpOperatorE,
    HOPS_OT_SharpandbevelOperatorE,
    HOPS_OT_BoolDifference,
    HOPS_OT_BoolIntersect,
    HOPS_OT_BoolUnion,
    HOPS_OT_EditBoolDifference,
    HOPS_OT_EditBoolUnion,
    HOPS_OT_ComplexSplitBooleanOperator,
    HOPS_OT_CutIn,
    HOPS_OT_Slash,
    HOPS_OT_Analysis,
    HOPS_OT_AdjustBevelWeightOperator,
    HOPS_OT_ModalCircle,
    HOPS_OT_SetEditSharpen,
    HOPS_OT_StarConnect,
    HOPS_OT_CleanMeshOperator,
    HOPS_OT_VertcircleOperator,
    HOPS_OT_CleanReOrigin,
    HOPS_OT_BevelMultiplier,
    HOPS_OT_BoolshapeStatusSwap,
    HOPS_OT_CurveBevelOperator,
    HOPS_OT_DecalMachineFix,
    HOPS_OT_EmptyToImageOperator,
    HOPS_OT_CenterEmptyOperator,
    HOPS_OT_EmptyTransparencyModal,
    HOPS_OT_EmptyOffsetModal,
    HOPS_OT_ResetStatus,
    HOPS_OT_SimplifyLattice,
    HOPS_OT_ArrayOperator,
    HOPS_OT_SetAsAam,
    # meshdispOperator,
    HOPS_OT_MirrorX,
    HOPS_OT_MirrorY,
    HOPS_OT_MirrorZ,
    HOPS_OT_OpenKeymapForEditing,
    HOPS_OT_ResetAxis,
    HOPS_OT_ResetAxisModal,
    HOPS_OT_Shrinkwrap,
    HOPS_OT_ShrinkwrapRefresh,
    # ZHopsShrinkwrap,
    HOPS_OT_SphereCast,
    HOPS_OT_BoolToggle,
    HOPS_OT_TriangulateNgons,
    HOPS_OT_TriangulateModifier,
    HOPS_OT_AdjustArrayOperator,
    HOPS_OT_AdjustBevelOperator,
    HOPS_OT_TwoDBevelOperator,
    HOPS_OT_AdjustCurveOperator,
    HOPS_OT_AdjustTthickOperator,
    HOPS_OT_BoolObjectScroll,
    HOPS_OT_BoolScroll,
    HOPS_OT_CurveGuide,
    HOPS_OT_CurveStretch,
    HOPS_OT_ModalMirror,
    HOPS_OT_CollapseModifiers,
    HOPS_OT_OpenModifiers,
    HOPS_OT_SetHopsColorToTheme,
    HOPS_OT_SetHopsColorToDefault,
    HOPS_OT_SetHopsColorToTheme2,
    HOPS_OT_SetSharpness30,
    HOPS_OT_SetSharpness45,
    HOPS_OT_SetSharpness60,
    HOPS_OT_SharpManager,
    HOPS_OT_BrushToggle,
    HOPS_OT_SculptDecimate,
    HOPS_OT_UnSharpOperator,
    HOPS_OT_ComplexSharpenOperator,
    HOPS_OT_AddEdgeSplit,
    HOPS_OT_SoftSharpenOperator,
    HOPS_OT_StepOperator,
    HOPS_OT_DrawUV,
    HOPS_OT_XUnwrapF,
    HopsHelperOptions,
    HOPS_OT_HelperPopup,
    HOPS_MT_MainMenu,
    HOPS_PT_MainPie,
    HOPS_OT_StatusHelperPopup,
#    HOPS_PT_HelpPanel,
#    HOPS_PT_SharpPanel,
#    HOPS_PT_InsertsPanel,
#    HOPS_PT_DynamicToolsPanel,
#    HOPS_PT_OperationsPanel,
#    HOPS_PT_BooleansPanel,
#    HOPS_PT_MeshToolsPanel,
#    HOPS_PT_OptionsPanel,
    HOPS_MT_InsertsObjectsSubmenu,
    HOPS_MT_MeshOperatorsSubmenu,
    HOPS_MT_ObjectsOperatorsSubmenu,
    HOPS_MT_MergeOperatorsSubmenu,
    HOPS_MT_BoolScrollOperatorsSubmenu,
    HOPS_MT_SettingsSubmenu,
    HOPS_MT_MaterialListMenu,
    HOPS_MT_SculptSubmenu,
    HOPS_MT_MiraSubmenu,
    HOPS_MT_BasicObjectOptionsSubmenu,
    HOPS_MT_FrameRangeSubmenu,
    HOPS_MT_SelectViewSubmenu,
    HOPS_MT_ViewportSubmenu,
    HOPS_MT_RenderSetSubmenu,
    HOPS_MT_ResetAxiSubmenu,
    HOPS_MT_SymmetrySubmenu,
    HOPS_MT_edgeWizardSubmenu,
    HOPS_MT_BoolSumbenu,
    HOPS_MT_ObjectToolsSubmenu,
    HOPS_MT_MeshToolsSubmenu,
    HOPS_OT_StoreMousePosition,
    # ExecutionContext,
    HopsArrayGizmoGroup,
    HopsArrayExecuteXmGizmo,
    HOPS_OT_MirrorExecuteOption4Gizmo,
    HOPS_OT_MirrorExecuteOption1Gizmo,
    HOPS_OT_MirrorExecuteOption2Gizmo,
    HOPS_OT_MirrorExecuteOption3Gizmo,
    HOPS_OT_MirrorGizmoGroup,
    HOPS_OT_MirrorGizmo,
    HOPS_OT_MirrorRemoveGizmo,
    HOPS_OT_MirrorExecuteXGizmo,
    HOPS_OT_MirrorExecuteXmGizmo,
    HOPS_OT_MirrorExecuteYGizmo,
    HOPS_OT_MirrorExecuteYmGizmo,
    HOPS_OT_MirrorExecuteZGizmo,
    HOPS_OT_MirrorExecuteZmGizmo,
    HOPS_GT_MirrorCustomShapeGizmo
)


def register():
    for cls in classes:
        register_class(cls)
    register_all()
    # hardops_tool_register()
    # print("Registered {} with {} modules".format(bl_info["name"], len(modules)))


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
    # hardops_tool_unregister()
    unregister_all()
    # print("Unregistered {}".format(bl_info["name"]))
