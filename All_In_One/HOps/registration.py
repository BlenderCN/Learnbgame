import bpy
from bpy.app.handlers import persistent
from . ui import view_3d_hud
from . import extend_bpy_types
from . keymap import register_keymap, unregister_keymap
from . icons import initialize_icons_collection, unload_icons
from . add_object_to_selection import create_object_to_selection
from . mesh_check import HopsMeshCheckCollectionGroup, updateDisplayColor
from . brush_previews import register_and_load_brushes, unregister_and_unload_brushes, brush_load_handler, brush_update_handler
from . material import HopsMaterialOptions
from . ui.hops_helper import HopsHelperOptions


def register_all():
    register_properties()
    view_3d_hud.register()
    extend_bpy_types.register()
    initialize_icons_collection()
    # overlay_drawer.register_callbacks()
    register_keymap()
    # bpy.app.handlers.load_post.append(brush_load_handler)
    # bpy.app.handlers.scene_update_post.append(brush_update_handler)


def unregister_all():
    unload_icons()
    unregister_properties()
    view_3d_hud.unregister()
    extend_bpy_types.unregister()
    # overlay_drawer.unregister_callbacks()
    unregister_keymap()
    # bpy.app.handlers.load_post.remove(brush_load_handler)
    # bpy.app.handlers.scene_update_post.remove(brush_update_handler)
    unregister_and_unload_brushes()


def register_properties():
    bpy.types.WindowManager.choose_primitive = bpy.props.EnumProperty(
        items=(('cube', 'Cube', '', 'MESH_CUBE', 1),
               ('cylinder_8', 'Cylinder 8', '', 'MESH_CYLINDER', 2),
               ('cylinder_16', "Cylinder 16", '', 'MESH_CYLINDER', 3),
               ('cylinder_24', "Cylinder 24", '', 'MESH_CYLINDER', 4),
               ('cylinder_32', "Cylinder 32", '', 'MESH_CYLINDER', 5),
               ('cylinder_64', "Cylinder 64", '', 'MESH_CYLINDER', 6)),
        default='cylinder_24',
        update=create_object_to_selection)

    bpy.types.WindowManager.m_check = bpy.props.PointerProperty(type=HopsMeshCheckCollectionGroup)
    bpy.types.WindowManager.Hard_Ops_material_options = bpy.props.PointerProperty(type=HopsMaterialOptions)
    bpy.types.WindowManager.Hard_Ops_helper_options = bpy.props.PointerProperty(type=HopsHelperOptions)

def unregister_properties():

    del bpy.types.WindowManager.m_check
    del bpy.types.WindowManager.Hard_Ops_material_options
    del bpy.types.WindowManager.Hard_Ops_helper_options
