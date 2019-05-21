import bpy
from ..utils import MACHIN3 as m3


class MESHmachineDebugMenu(bpy.types.Menu):
    bl_idname = "machin3.mesh_machine_debug_menu"
    bl_label = "Debug"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("machin3.loops_or_handles", text="(F) Get Loops/Handles")
        layout.operator("machin3.get_sides", text="Sides")
        layout.operator("machin3.raycast", text="Raycast")
        layout.operator("machin3.draw_hud", text="Draw HUD")
        layout.operator("machin3.draw_stash", text="Draw Stash")
        layout.operator("machin3.get_angle", text="Angle")
        layout.operator("machin3.get_length", text="Length")
        layout.operator("machin3.get_faces_linked_to_verts", text="Faces linked to Verts")


class MESHmachineLoopsMenu(bpy.types.Menu):
    bl_idname = "machin3.mesh_machine_loops_menu"
    bl_label = "Loops"

    def draw(self, context):
        layout = self.layout

        # Mark Loop Edges
        layout.operator("machin3.mark_loop", text="Mark Loop").clear = False
        layout.operator("machin3.mark_loop", text="Clear Loop").clear = True


class MESHmachineNormalsMenu(bpy.types.Menu):
    bl_idname = "machin3.mesh_machine_normals_menu"
    bl_label = "Normal"

    def draw(self, context):
        layout = self.layout

        # Normal Flatten
        layout.operator_context = m3.MM_prefs().modal_NormalFlatten
        layout.operator("machin3.normal_flatten", text="Flatten")

        # Normal Straighten
        layout.operator("machin3.normal_straighten", text="Straighten")

        # Normal Transfer
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("machin3.normal_transfer", text="Transfer")

        # Normal Clear
        layout.operator("machin3.normal_clear", text="Clear")


class MESHmachineSymmetrizeMenu(bpy.types.Menu):
    bl_idname = "machin3.mesh_machine_symmetrize_menu"
    bl_label = "Symmetrize"

    def draw(self, context):
        layout = self.layout

        # Symmetrize X
        op = layout.operator("machin3.symmetrize", text="X")
        op.axis = "X"

        # Symmetrize Y
        op = layout.operator("machin3.symmetrize", text="Y")
        op.axis = "Y"

        # Symmetrize Z
        op = layout.operator("machin3.symmetrize", text="Z")
        op.axis = "Z"


class MESHmachinePlugUtilsMenu(bpy.types.Menu):
    bl_idname = "machin3.mesh_machine_plug_utils_menu"
    bl_label = "Plug Utils"

    def draw(self, context):
        layout = self.layout

        # Create
        layout.operator("machin3.create_plug", text="Create Plug")

        # Add to Library
        layout.operator("machin3.add_plug_to_library", text="Add Plug to Library")
        layout.separator()

        # Plug Properties
        op = layout.operator("machin3.set_plug_props", text="Set Plug Props")
        op.init = True

        layout.operator("machin3.clear_plug_props", text="Clear Plug Props")
        layout.separator()

        # Validate a Plug
        layout.operator("machin3.validate_plug", text="Validate Plug")


class MESHmachineOrphanStashesMenu(bpy.types.Menu):
    bl_idname = "machin3.mesh_machine_orphan_stashes_menu"
    bl_label = "Orphan Stashes"

    def draw(self, context):
        layout = self.layout

        # View Orphans
        layout.operator("machin3.view_orphan_stashes", text="View Orphans")

        # Remove Orphans
        layout.operator("machin3.remove_orphan_stashes", text="Remove Orphans")
