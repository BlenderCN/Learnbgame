#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy

from . import modifiers as modifier_draw

class ModifierButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    # Let me take this opportunity to rant.
    # For some STUPID REASON, Blender decides which buttons to show in the C code. This is all well
    # and good, EXCEPT THEY DO NOT SHOW THE MODIFIERS BUTTON FOR EMPTIES. This totally breaks the
    # Plasma Modifier workflow. As a shim workaround, we're overtaking the physics panel as our
    # Plasma Modifier Panel. The Physics, Object, and Constraint Panels' visibility determined by
    # the same block of a switch statement in Blender 2.71 (buttons_context_path in buttons_context.c)
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return context.object and context.scene.render.engine == "PLASMA_GAME"


class PlasmaModifiersPanel(ModifierButtonsPanel, bpy.types.Panel):
    bl_label = "Plasma Modifiers"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        # So, I had to read the doggone Blender source code to figure out how to use this because the
        # "documentation" only gives this helpful information about this interesting feature: "operator_menu_enum"
        # Bah. For the record: first param is the operator, second is an EnumProperty on that operator.
        # You define categories by inserting an enum item with an empty key, empty description, and just a name.
        # Any items following that are members of that category, of course...
        # ... I hope that my rambling has helped somebody understand more about the undocumented mess
        #     that is Blender Python.
        row = layout.row(align=True)
        row.operator_menu_enum("object.plasma_modifier_add", "types")
        row.menu("PlasmaModifiersSpecialMenu", icon="DOWNARROW_HLT", text="")

        # First, let's sort the list of modifiers based on their display order
        # We don't do this sort in the property itself because this is really just a UI hint.
        modifiers = sorted(obj.plasma_modifiers.modifiers, key=lambda x: x.display_order)

        # Inside the modifier_draw module, we have draw callbables for each modifier
        # We'll loop through the list of active modifiers and call the drawprocs for the enabled mods
        for i in modifiers:
            modLayout = self._draw_modifier_template(i)
            if i.show_expanded:
                getattr(modifier_draw, i.pl_id)(i, modLayout, context)

    def _draw_modifier_template(self, modifier):
        """This draws our lookalike modifier template and returns a UILayout object for each modifier
           to consume in order to draw its specific properties"""
        layout = self.layout.box()

        # This is the main title row. It mimics the Blender template_modifier, which (unfortunately)
        # requires valid Blender Modifier data. It would be nice if the Blender UI code were consistently
        # C or Python and not a frankenstein mix. I would probably prefer working in C, just because
        # the compiler saves my neck 99.9% of the time...</rant>
        row = layout.row(align=True)
        exicon = "TRIA_DOWN" if modifier.show_expanded else "TRIA_RIGHT"
        row.prop(modifier, "show_expanded", text="", icon=exicon, emboss=False)
        row.label(text=modifier.bl_label, icon=getattr(modifier, "bl_icon", "NONE"))

        row.operator("object.plasma_modifier_move_up", text="", icon="TRIA_UP").active_modifier = modifier.display_order
        row.operator("object.plasma_modifier_move_down", text="", icon="TRIA_DOWN").active_modifier = modifier.display_order
        row.operator("object.plasma_modifier_copy", text="", icon="COPYDOWN").active_modifier = modifier.display_order
        row.operator("object.plasma_modifier_reset", text="", icon="FILE_REFRESH").active_modifier = modifier.display_order
        row.operator("object.plasma_modifier_remove", text="", icon="X").active_modifier = modifier.display_order

        # Now we return the modifier box, which is populated with the modifier specific properties
        # by whatever insanity is in the modifier module. modifier modifier modifier...
        # MODDDDDDDDIFIIIIEEEERRRRRRRR!!!
        return layout


class PlasmaModifiersSpecialMenu(ModifierButtonsPanel, bpy.types.Menu):
    bl_label = "Plasma Modifier Specials"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.plasma_modifier_copy", icon="COPYDOWN", text="Copy Modifiers").active_modifier = -1
        layout.operator("object.plasma_modifier_paste", icon="PASTEDOWN", text="Paste Modifier(s)")
