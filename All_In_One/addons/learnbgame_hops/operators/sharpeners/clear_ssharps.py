import bpy
from bpy.props import BoolProperty
import bpy.utils.previews

# _____________________________________________________________clear ssharps (OBJECT MODE)________________________


class HOPS_OT_UnSharpOperator(bpy.types.Operator):
    bl_idname = "clean.sharps"
    bl_label = "Remove Ssharps"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """REMOVES all BEVEL modifiers and EDGE markings / Resets mesh to FLAT shading.
F6 for additional parameters"""

    removeMods: BoolProperty(default=True)
    clearsharps: BoolProperty(default=True)
    clearbevel: BoolProperty(default=True)
    clearcrease: BoolProperty(default=True)

    text = "SSharps Removed"
    op_tag = "Clean Ssharp"
    op_detail = "Selected Ssharps Removed"

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop(self, 'removeMods', text="RemoveModifiers?")
        box.prop(self, 'clearsharps', text="Clear Sharps")
        box.prop(self, 'clearbevel', text="Clear Bevels")
        box.prop(self, 'clearcrease', text="Clear Crease")

    def execute(self, context):
        clear_ssharps_active_object(
            self.removeMods,
            self.clearsharps,
            self.clearbevel,
            self.clearcrease,
            self.text)

        return {'FINISHED'}

# _____________________________________________________________clear ssharps________________________


def clear_ssharps_active_object(removeMods, clearsharps, clearbevel, clearcrease, text):
    remove_mods_shadeflat(removeMods)
    clear_sharps(
        clearsharps,
        clearbevel,
        clearcrease)
    # show_message(text)
    object = bpy.context.active_object
    object.hops.status = "UNDEFINED"
    try:
        bpy.data.collections['Hardops'].objects.unlink(object)
    except:
        pass
    bpy.ops.object.shade_flat()


def clear_sharps(clearsharps, clearbevel, clearcrease):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

    if clearsharps:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='TOGGLE')

        bpy.ops.mesh.mark_sharp(clear=True)
    if clearbevel:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.transform.edge_bevelweight(value=-1)
    if clearcrease:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='TOGGLE')

        bpy.ops.transform.edge_crease(value=-1)
    bpy.ops.object.editmode_toggle()


def remove_mods_shadeflat(removeMods):
    if removeMods:
        bpy.ops.object.modifier_remove(modifier="Bevel")
        bpy.ops.object.modifier_remove(modifier="Solidify")

    else:
        bpy.context.object.modifiers["Bevel"].limit_method = 'WEIGHT'
        bpy.context.object.modifiers["Bevel"].angle_limit = 0.7


def show_message(text):
    pass
