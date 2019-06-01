import os
import bpy
from bpy.props import StringProperty
from .. utils.blender_ui import open_error_message
from .. utils.libraries import load_object_from_other_file
from .. utils.asset_loader import share_materials, prepare_scene, blends_folder, adjust_scale, match_to_base_material
from .. import M3utils as m3


class InsertDecal02(bpy.types.Operator):
    bl_idname = "machin3.insert_decal02"
    bl_label = "Insert Decal02"

    decal02_name = StringProperty()

    def execute(self, context):
        insert_decal02(self.decal02_name)
        context.area.tag_redraw()
        return {"FINISHED"}


def insert_decal02(decal02_name):
    if decal02_name.startswith("c_"):
        filepath = os.path.join(blends_folder("decals02", custom=True), decal02_name + ".blend")
    else:
        filepath = os.path.join(blends_folder("decals02"), decal02_name + ".blend")

    try:
        decal = load_object_from_other_file(filepath, decal02_name)
        bpy.context.scene.objects.link(decal)
    except NameError:
        open_error_message("The Decal '{}' does not exist in the assets file".format(decal02_name))
        return
    except OSError:
        open_error_message("The file does not exist: {}".format(filepath))
        return

    m3.move_to_cursor(decal, bpy.context.scene)

    # avoid bringing in duplicate materials
    decalgroup = share_materials(decal)

    # adjust decal material according to base material params in prefs
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
