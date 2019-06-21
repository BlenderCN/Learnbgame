import bpy
import os
from ..utils import MACHIN3 as m3


class MESHmachineMenu(bpy.types.Menu):
    bl_idname = "machin3.mesh_machine_menu"
    bl_label = "MESHmachine"

    def draw(self, context):
        if context.mode == "EDIT_MESH":
            draw_menu_edit(self, context)
        elif context.mode == "OBJECT":
            draw_menu_object(self, context)


class MESHmachineSpecial(bpy.types.Menu):
    bl_idname = "machin3.mesh_machine_special_menu"
    bl_label = "MESHmachine"

    def draw(self, context):
        if context.mode == "EDIT_MESH":
            draw_menu_edit(self, context, special=True)
        elif context.mode == "OBJECT":
            draw_menu_object(self, context, special=True)


def specials_menu(self, context):
    self.layout.menu("machin3.mesh_machine_special_menu")
    self.layout.separator()


def draw_menu_object(self, context, special=False):
    layout = self.layout

    debug = m3.MM_prefs().debug

    keyboard_layout = m3.MM_prefs().keyboard_layout

    show_delete = m3.MM_prefs().show_delete
    show_documentation = m3.MM_prefs().show_documentation


    # reset plugmode, if it's NONE (the AddPlugToLibrary tool, if aborted, leaves it in this state)
    if m3.MM_prefs().plugmode == "NONE":
        m3.MM_prefs().plugmode = "INSERT"
        m3.MM_prefs().plugremovemode = False


    active = context.active_object
    sel = context.selected_objects

    # Debug
    # if True:
    if debug:
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("machin3.raycast", text="Raycast")
        layout.separator()


    # Plugs
    if active and len(sel) == 2:
        op = layout.operator("machin3.plug", text="Plug")
        op.init = True

    if not any([obj.MM.isplughandle for obj in sel]):
        layout.menu("machin3.mesh_machine_plug_libraries", text="Plug Libraries")

    if active and len(sel) >= 1:
        layout.menu("machin3.mesh_machine_plug_utils_menu", text="Plug Utils")
    layout.separator()


    # Stashes
    if active and active.select:
        layout.operator_context = "INVOKE_DEFAULT"
        if len(sel) <= 2:
            layout.operator("machin3.create_stash", text="Stash it")
        else:
            layout.operator("machin3.create_stash", text="Stash them")
        layout.operator("machin3.view_stashes", text="View Stashes")
        layout.operator("machin3.clear_stashes", text="Clear Stashes")
        layout.operator("machin3.transfer_stashes", text="Transfer Stashes")

    layout.menu("machin3.mesh_machine_orphan_stashes_menu", text="Orphan Stashes")
    layout.separator()


    # Real Mirror
    if any([True for obj in sel for mod in obj.modifiers if mod.type=="MIRROR"]):
        layout.operator("machin3.real_mirror", text="Real Mirror")
        layout.separator()


    # GTape
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator("machin3.tape", text="(D) Tape")


    # BLENDER  TOOLS

    layout.operator_context = 'EXEC_DEFAULT'
    if not special:
        if keyboard_layout == "QWERTY" and show_delete:
            layout.separator()
            layout.operator("object.delete", text="(X) Delete")


    # HELP

    if show_documentation:
        layout.operator_context = "EXEC_DEFAULT"

        layout.separator()
        layout.operator("wm.url_open", text="Documentation", icon="INFO").url = os.path.join(m3.MM_prefs().MMpath, "documentation", "index.html")


def draw_menu_edit(self, context, special=False):
    layout = self.layout

    debug = m3.MM_prefs().debug

    keyboard_layout = m3.MM_prefs().keyboard_layout

    show_looptools_wrappers = m3.MM_prefs().show_looptools_wrappers
    show_mesh_split = m3.MM_prefs().show_mesh_split
    show_delete = m3.MM_prefs().show_delete
    show_documentation = m3.MM_prefs().show_documentation


    # DEBUG TOOLS

    # if True:
    if debug:
        layout.menu("machin3.mesh_machine_debug_menu", text="Debug")
        layout.separator()


    # MAIN TOOLS

    # Fuse
    layout.operator_context = m3.MM_prefs().modal_Fuse
    op = layout.operator("machin3.fuse", text="Fuse")
    op.width = 0
    op.reverse = False
    op.force_projected_loop = False

    # Change Width
    layout.operator_context = m3.MM_prefs().modal_ChangeWidth
    op = layout.operator("machin3.change_width", text="(W) Change Width")
    op.width = 0

    # Flatten
    layout.operator_context = m3.MM_prefs().modal_Flatten
    layout.operator("machin3.flatten", text="(E) Flatten")


    # UN-TOOLS
    layout.separator()

    # Unfuse
    layout.operator_context = m3.MM_prefs().modal_Unfuse
    layout.operator("machin3.unfuse", text="(D) Unfuse")

    # Refuse
    layout.operator_context = m3.MM_prefs().modal_Refuse
    op = layout.operator("machin3.refuse", text="(R) Refuse")
    op.width = 0
    op.reverse = False
    op.init = True

    # Unchamfer
    layout.operator_context = m3.MM_prefs().modal_Unchamfer
    op = layout.operator("machin3.unchamfer", text="(C) Unchamfer")
    op.slide = 0

    # Unbevel
    layout.operator_context = m3.MM_prefs().modal_Unbevel
    op = layout.operator("machin3.unbevel", text="(B) Unbevel")
    op.slide = 0

    # Unf*ck
    layout.operator_context = m3.MM_prefs().modal_Unfuck
    if keyboard_layout == "QWERTY":
        op = layout.operator("machin3.unfuck", text="(Y) Unf*ck")
    else:
        op = layout.operator("machin3.unfuck", text="(X) Unf*ck")
    op.propagate = 0
    op.width = 0


    # CORNER TOOLS
    layout.separator()

    # Turn Corner
    layout.operator_context = m3.MM_prefs().modal_TurnCorner
    layout.operator("machin3.turn_corner", text="Turn Corner")

    # Quad Corner
    layout.operator_context = m3.MM_prefs().modal_QuadCorner
    layout.operator("machin3.quad_corner", text="Quad Corner")


    # LOOP TOOLS
    layout.separator()

    layout.menu("machin3.mesh_machine_loops_menu", text="Loops")


    # BOOLEAN RELATED TOOLS

    # Boolean Cleanup
    layout.separator()
    layout.operator_context = 'INVOKE_DEFAULT'
    op = layout.operator("machin3.boolean_cleanup", text="Boolean Cleanup")
    op.threshold = 0
    op.sharp = False

    # Post Boolean Chamfer
    layout.operator_context = m3.MM_prefs().modal_Chamfer
    op = layout.operator("machin3.chamfer", text="Chamfer")
    op.width = 0
    op.loop_slide_sideA = False
    op.loop_slide_sideB = False
    op.face_method_sideA = "REBUILD"
    op.face_method_sideB = "REBUILD"
    op.mergeA = False
    op.mergeB = False
    op.reachA = 0
    op.reachB = 0


    # Post Boolean Offset
    layout.operator_context = m3.MM_prefs().modal_Offset
    op = layout.operator("machin3.offset", text="Offset")
    op.width = 0.01
    op.loop_slide = False
    op.face_method = "REBUILD"
    op.merge = False
    op.reach = 0


    # STASH TOOLS
    layout.separator()

    # Create Stash
    layout.operator("machin3.create_stash", text="Stash it")

    # View Stashes
    layout.operator("machin3.view_stashes", text="View Stashes")

    # Clear Stashes
    layout.operator("machin3.clear_stashes", text="Clear Stashes")

    layout.separator()


    # CONFORM

    layout.operator_context = 'INVOKE_DEFAULT'
    op = layout.operator("machin3.conform", text="Conform")


    # NORMAL TOOLS

    layout.menu("machin3.mesh_machine_normals_menu", text="Normals")


    # SYMMETRIZE

    layout.menu("machin3.mesh_machine_symmetrize_menu", text="Symmetrize")

    # SELECTION

    layout.separator()
    layout.operator("machin3.vselect", text="VSelect")
    # layout.operator("machin3.loop_step", text="Loop Step")


    # LOOPTOOLS

    if 'mesh_looptools' in context.user_preferences.addons and show_looptools_wrappers:
        layout.separator()

        # Circle
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("machin3.looptools_circle", text="Circle")

        # Relax
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("machin3.looptools_relax", text="Relax")


    # BLENDER  TOOLS

    if not special:
        if keyboard_layout == "QWERTY" and show_delete:
            layout.separator()
            layout.operator("wm.call_menu", text="(X) Delete").name = "VIEW3D_MT_edit_mesh_delete"
        elif keyboard_layout == "QWERTZ" and show_mesh_split:
            layout.separator()
            layout.operator("mesh.split", text="(Y) Split")


    # HELP

    if show_documentation:
        layout.operator_context = "EXEC_DEFAULT"

        layout.separator()
        layout.operator("wm.url_open", text="Documentation", icon="INFO").url = os.path.join(m3.MM_prefs().MMpath, "documentation", "index.html")
