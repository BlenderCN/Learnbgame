import bpy
from . step1_ui import  \
    VIEW3D_PT_jet_step1, \
    VIEW3D_OT_jet_flat_smooth

def register():
    bpy.utils.register_class(VIEW3D_OT_jet_flat_smooth)
    bpy.utils.register_class(VIEW3D_PT_jet_step1)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_jet_step1)
    bpy.utils.unregister_class(VIEW3D_OT_jet_flat_smooth)

