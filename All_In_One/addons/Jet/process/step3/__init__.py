import bpy
from . step3_ui import \
    VIEW3D_PT_jet_step3, \
    VIEW3D_OT_jet_autosmooth, \
    VIEW3D_OT_jet_sharp


def register():
    bpy.utils.register_class(VIEW3D_OT_jet_autosmooth)
    bpy.utils.register_class(VIEW3D_OT_jet_sharp)
    bpy.utils.register_class(VIEW3D_PT_jet_step3)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_jet_step3)
    bpy.utils.unregister_class(VIEW3D_OT_jet_autosmooth)
    bpy.utils.unregister_class(VIEW3D_OT_jet_sharp)

