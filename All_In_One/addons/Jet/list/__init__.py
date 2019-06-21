from . list_data import ItemPropertyGroup, \
    HiObjListPropertyGroup, \
    LowItemPropertyGroup, \
    LowObjListPropertyGroup

from bpy.utils import register_class, unregister_class

from . low_res_list_ui import \
    DATA_OT_jet_low_res_list_add, \
    DATA_OT_jet_low_res_list_remove, \
    DATA_UL_jet_low_res_list, \
    DATA_OT_jet_low_res_list_select, \
    DATA_OT_jet_low_res_list_hide, \
    DATA_OT_jet_low_res_list_clear

from . hi_res_list_ui import \
    DATA_OT_jet_hi_res_list_add, \
    DATA_OT_jet_hi_res_list_remove, \
    DATA_UL_jet_hi_res_list, \
    DATA_OT_jet_hi_res_list_select, \
    DATA_OT_jet_hi_res_list_hide, \
    DATA_OT_jet_hi_res_list_clear

def register():
    register_class(ItemPropertyGroup)
    register_class(HiObjListPropertyGroup)
    register_class(LowItemPropertyGroup)
    register_class(LowObjListPropertyGroup)

    register_class(DATA_OT_jet_low_res_list_add)
    register_class(DATA_OT_jet_low_res_list_remove)
    register_class(DATA_OT_jet_low_res_list_select)
    register_class(DATA_OT_jet_low_res_list_hide)
    register_class(DATA_OT_jet_low_res_list_clear)
    register_class(DATA_UL_jet_low_res_list)

    register_class(DATA_OT_jet_hi_res_list_add)
    register_class(DATA_OT_jet_hi_res_list_remove)
    register_class(DATA_OT_jet_hi_res_list_select)
    register_class(DATA_OT_jet_hi_res_list_hide)
    register_class(DATA_OT_jet_hi_res_list_clear)
    register_class(DATA_UL_jet_hi_res_list)


def unregister():
    unregister_class(DATA_OT_jet_low_res_list_add)
    unregister_class(DATA_OT_jet_low_res_list_remove)
    unregister_class(DATA_OT_jet_low_res_list_select)
    unregister_class(DATA_OT_jet_low_res_list_hide)
    unregister_class(DATA_OT_jet_low_res_list_clear)
    unregister_class(DATA_UL_jet_low_res_list)

    unregister_class(DATA_OT_jet_hi_res_list_add)
    unregister_class(DATA_OT_jet_hi_res_list_remove)
    unregister_class(DATA_OT_jet_hi_res_list_select)
    unregister_class(DATA_OT_jet_hi_res_list_hide)
    unregister_class(DATA_OT_jet_hi_res_list_clear)
    unregister_class(DATA_UL_jet_hi_res_list)

    unregister_class(LowObjListPropertyGroup)
    unregister_class(LowItemPropertyGroup)
    unregister_class(HiObjListPropertyGroup)
    unregister_class(ItemPropertyGroup)
