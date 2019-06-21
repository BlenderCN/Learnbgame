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


import bpy
from bpy.types import Operator


class SCENE_OT_messythings_deps_select(Operator):
    bl_label = "Messy Things Select Dependencies"
    bl_description = "Select objects which are used in modifiers and constraints by currently selected objects"
    bl_idname = "scene.messythings_deps_select"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        dep_obs = set()

        for ob in context.selected_objects:
            ob.select_set(False)

            if ob.modifiers:
                for mod in ob.modifiers:
                    if (
                        (mod.type in {"CURVE", "LATTICE", "BOOLEAN"} and mod.object) or
                        (mod.type == "SHRINKWRAP" and mod.target)
                    ):
                        mod_ob = mod.target if mod.type == "SHRINKWRAP" else mod.object
                        mod_ob.hide_viewport = False
                        mod_ob.select_set(True)
                        dep_obs.add(mod_ob)

            if ob.constraints:
                for con in ob.constraints:
                    if con.type == "FOLLOW_PATH" and con.target:
                        con.target.hide_viewport = False
                        con.target.select_set(True)
                        dep_obs.add(con.target)

        if dep_obs:
            count = len(dep_obs)

            for ob in dep_obs:
                context.view_layer.objects.active = ob
                break

            self.report({"INFO"}, f"{count} dependencies selected")

        return {"FINISHED"}


class SCENE_OT_messythings_sort(Operator):
    bl_label = "Messy Things Sort By Collections"
    bl_description = "Sort all objects in the scene in Main, Helpers, Gems, Lights and Gpencil collections"
    bl_idname = "scene.messythings_sort"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obs_main = set()
        obs_gems = set()
        obs_helpers = set()
        obs_lights = set()
        obs_gpencil = set()

        for ob in context.scene.objects:
            ob.hide_viewport = False
            is_dupliface = False

            if ob.is_instancer:
                for child in ob.children:
                    if "gem" in child:
                        is_dupliface = True
                        break

            if "gem" in ob or is_dupliface:
                obs_gems.add(ob)
            elif (
                (ob.type == "MESH" and ob.display_type in {"TEXTURED", "SOLID"}) or
                (ob.type == "CURVE" and (ob.data.bevel_depth or ob.data.bevel_object)) or
                ob.type in {"FONT", "META"}
            ):
                obs_main.add(ob)
            elif ob.type == "GPENCIL":
                obs_gpencil.add(ob)
            elif ob.type in {"LIGHT", "LIGHT_PROBE"}:
                obs_lights.add(ob)
            else:
                obs_helpers.add(ob)

        # Unlink objects

        for coll in context.scene.collection.children:
            for ob in coll.objects:
                coll.objects.unlink(ob)

        if context.scene.collection.objects:
            coll = context.scene.collection
            for ob in coll.objects:
                coll.objects.unlink(ob)

        # Link objects

        for name, obs in (
            ("Main", obs_main),
            ("Gems", obs_gems),
            ("Helpers", obs_helpers),
            ("Lights", obs_lights),
            ("Gpensil", obs_gpencil),
        ):
            if obs:
                coll = bpy.data.collections.new(name)
                context.scene.collection.children.link(coll)
                for ob in obs:
                    coll.objects.link(ob)

        self.report({"INFO"}, "Objects sorted")

        return {"FINISHED"}
