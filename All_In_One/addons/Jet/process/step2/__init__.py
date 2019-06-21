import bpy
from . step2_ui import \
    VIEW3D_PT_jet_step2, \
    VIEW3D_OT_jet_merge, \
    VIEW3D_OT_jet_delete_menu

def register():
    bpy.utils.register_class(VIEW3D_OT_jet_merge)
    bpy.utils.register_class(VIEW3D_OT_jet_delete_menu)
    bpy.utils.register_class(VIEW3D_PT_jet_step2)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_jet_step2)
    bpy.utils.unregister_class(VIEW3D_OT_jet_delete_menu)
    bpy.utils.unregister_class(VIEW3D_OT_jet_merge)


