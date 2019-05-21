import bpy
from . step6_ui import \
    VIEW3D_PT_jet_step6


def register():
    #bpy.utils.register_class(VIEW3D_OT_jet_add_sufix)
    bpy.utils.register_class(VIEW3D_PT_jet_step6)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_jet_step6)
    #bpy.utils.unregister_class(VIEW3D_OT_jet_add_sufix)


