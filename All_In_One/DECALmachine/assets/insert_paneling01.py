import os
import bpy
from bpy.props import StringProperty
from .. utils.blender_ui import open_error_message
from .. utils.libraries import load_object_from_other_file
from .. utils.asset_loader import share_materials, prepare_scene, blends_folder, adjust_scale, match_to_base_material
from .. import M3utils as m3


class InsertPanelDecal01(bpy.types.Operator):
    bl_idname = "machin3.insert_panel_decal01"
    bl_label = "Insert Panel Decal01"

    panel_decal01_name = StringProperty()

    def execute(self, context):
        insert_panel_decal01(self.panel_decal01_name)
        context.area.tag_redraw()
        return {"FINISHED"}


def insert_panel_decal01(panel_decal01_name):
    if panel_decal01_name.startswith("c_"):
        filepath = os.path.join(blends_folder("paneling01", custom=True), panel_decal01_name + ".blend")
    else:
        filepath = os.path.join(blends_folder("paneling01"), panel_decal01_name + ".blend")

    try:
        decal = load_object_from_other_file(filepath, panel_decal01_name.replace("paneling", "panel_decal", 1))
        bpy.context.scene.objects.link(decal)
    except NameError:
        open_error_message("The Decal '{}' does not exist in the assets file".format(panel_decal01_name))
        return
    except OSError:
        open_error_message("The file does not exist: {}".format(filepath))
        return

    m3.move_to_cursor(decal, bpy.context.scene)

    # avoid bringing in duplicate materials
    decalgroup = share_materials(decal)

    if m3.DM_prefs().autobasematerial:
        if decalgroup:
            match_to_base_material(decalgroup)

    # MACHIN3tools material viewport compensation
    if bpy.app.version >= (2, 79, 0):
        if m3.M3_check():
            if m3.M3_prefs().activate_ShadingSwitch:
                if m3.M3_prefs().viewportcompensation:
                    bpy.ops.machin3.adjust_principled_pbr_node(isdecal=True)

    # adjust scale according to unit settings
    if m3.DM_prefs().consistantscale:
        adjust_scale(decal)

    # add to group pro group
    if m3.GP_check():
        if m3.DM_prefs().groupproconnection:
            if len(bpy.context.scene.storedGroupSettings) > 0:
                bpy.ops.object.add_to_grouppro()

    # set up face snapping
    prepare_scene(bpy.context.scene)
