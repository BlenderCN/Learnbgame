import bpy
from . step4_ui import \
    VIEW3D_PT_jet_step4, \
    VIEW3D_PT_jet_step4_UVEditor, \
    VIEW3D_OT_jet_sharp_to_seam, \
    VIEW3D_OT_jet_unwrap, \
    VIEW3D_OT_jet_seam, \
    VIEW3D_OT_jet_triangulate, \
    VIEW3D_OT_jet_texture_atlas_on, \
    VIEW3D_OT_jet_no_uvs


def register():
    bpy.utils.register_class(VIEW3D_OT_jet_sharp_to_seam)
    bpy.utils.register_class(VIEW3D_OT_jet_no_uvs)
    bpy.utils.register_class(VIEW3D_OT_jet_unwrap)
    bpy.utils.register_class(VIEW3D_OT_jet_seam)
    bpy.utils.register_class(VIEW3D_OT_jet_triangulate)
    bpy.utils.register_class(VIEW3D_OT_jet_texture_atlas_on)
    bpy.utils.register_class(VIEW3D_PT_jet_step4_UVEditor)
    bpy.utils.register_class(VIEW3D_PT_jet_step4)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_jet_step4)
    bpy.utils.unregister_class(VIEW3D_PT_jet_step4_UVEditor)
    bpy.utils.unregister_class(VIEW3D_OT_jet_sharp_to_seam)
    bpy.utils.unregister_class(VIEW3D_OT_jet_unwrap)
    bpy.utils.unregister_class(VIEW3D_OT_jet_no_uvs)
    bpy.utils.unregister_class(VIEW3D_OT_jet_seam)
    bpy.utils.unregister_class(VIEW3D_OT_jet_triangulate)
    bpy.utils.unregister_class(VIEW3D_OT_jet_texture_atlas_on)