import os
import bpy
from bpy.props import StringProperty
from .. utils.blender_ui import open_error_message
from .. utils.libraries import load_object_from_other_file
from .. utils.asset_loader import share_materials, prepare_scene, blends_folder, adjust_scale
from .. import M3utils as m3


class InsertInfo01(bpy.types.Operator):
    bl_idname = "machin3.insert_info01"
    bl_label = "Insert Info01"

    info01_name = StringProperty()

    def execute(self, context):
        insert_info01(self.info01_name)
        context.area.tag_redraw()
        return {"FINISHED"}


def insert_info01(info01_name):
    if info01_name.startswith("c_"):
        filepath = os.path.join(blends_folder("info01", custom=True), info01_name + ".blend")
    else:
        filepath = os.path.join(blends_folder("info01"), info01_name + ".blend")

    try:
        decal = load_object_from_other_file(filepath, info01_name)
        bpy.context.scene.objects.link(decal)
    except NameError:
        open_error_message("The Decal '{}' does not exist in the assets file".format(info01_name))
        return
    except OSError:
        open_error_message("The file does not exist: {}".format(filepath))
        return

    m3.move_to_cursor(decal, bpy.context.scene)

    # avoid bringing in duplicate materials
    share_materials(decal)

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
