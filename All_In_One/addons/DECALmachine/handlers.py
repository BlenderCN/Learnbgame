import bpy
from bpy.app.handlers import persistent
from . import bl_info
from . utils.material import set_match_material_enum
from . utils.registration import reload_infotextures, reload_infofonts, reload_decal_libraries, reload_panels


@persistent
def update_match_material_enum(none):
    set_match_material_enum()


@persistent
def update_userdecallibs_enum(none):
    scene = bpy.context.scene

    if scene.userdecallibs not in [lib[0] for lib in bpy.types.Scene.userdecallibs[1]['items']]:
        print("Note, the userdecallib defined in this blend file, could not be found among the registered decal libaries. Updating property by reloading decal libraries. Re-saving blend file is recommended.")
        reload_decal_libraries()


@persistent
def update_infodecal_sources(none):
    wm = bpy.context.window_manager
    if wm.updateinfotextures:
        reload_infotextures(default=wm.updateinfotextures)
        wm.updateinfotextures = ''

    if wm.updateinfofonts:
        reload_infofonts(default=wm.updateinfofonts)
        wm.updateinfofonts = ''


@persistent
def update_panels(none):
    reload_panels()

    scene = bpy.context.scene
    revision = bl_info.get("revision")

    if revision and not scene.DM.revision:
        scene.DM.revision = revision
