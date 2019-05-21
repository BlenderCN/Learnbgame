# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Messy Things project organizer for Blender.
#  Copyright (C) 2017-2019  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


from bpy.types import Operator
from bpy.props import BoolProperty

from .cleanup_obj import cleanup_objects
from .cleanup_mod import cleanup_modifiers
from .cleanup_mat import cleanup_materials
from .cleanup_gp import cleanup_gpencil


class SCENE_OT_messythings_cleanup(Operator):
    bl_label = "Messy Things Cleanup"
    bl_description = "Remove redundant or purge all datablocks of set type"
    bl_idname = "scene.messythings_cleanup"
    bl_options = {"REGISTER", "UNDO"}

    use_cleanup_objects: BoolProperty(
        name="Objects",
        description=(
            "Remove lattice, curve and empty mesh objects that are not in use by "
            "modifiers, constraints, curve Bevel Object and Taper Object properties"
        ),
    )
    use_cleanup_modifiers: BoolProperty(
        name="Modifiers",
        description="Remove Curve, Lattice, Boolean and Shrinkwrap modifiers with empty Object or Target fields",
    )
    use_cleanup_materials: BoolProperty(
        name="Materials (Purge)",
        description="Purge all materials from file, additionally remove material slots from objects",
    )
    use_cleanup_gpencil: BoolProperty(
        name="Annotations",
        description="Remove redundant (Blender 2.7x) grease pencil object data from non grease pencil objects"
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(self, "use_cleanup_objects")
        row.label(icon="OBJECT_DATA")

        row = col.row(align=True)
        row.prop(self, "use_cleanup_modifiers")
        row.label(icon="MODIFIER_DATA")

        row = col.row(align=True)
        row.prop(self, "use_cleanup_materials")
        row.label(icon="MATERIAL")

        row = col.row(align=True)
        row.prop(self, "use_cleanup_gpencil")
        row.label(icon="OUTLINER_OB_GREASEPENCIL")

    def execute(self, context):
        msgs = []

        if self.use_cleanup_objects:
            curve, lat, mesh = cleanup_objects(context)
            msgs.append(f"{curve} curve")
            msgs.append(f"{lat} lattice")
            msgs.append(f"{mesh} mesh")

        if self.use_cleanup_modifiers:
            mod = cleanup_modifiers(context)
            msgs.append(f"{mod} modifiers")

        if self.use_cleanup_materials:
            mat = cleanup_materials(context)
            msgs.append(f"{mat} materials")

        if self.use_cleanup_gpencil:
            gp = cleanup_gpencil(context)
            msgs.append(f"{gp} grease pencil")

        if not msgs:
            return {"CANCELLED"}

        msg = "Removed: " + ", ".join(msgs)
        self.report({"INFO"}, msg)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
