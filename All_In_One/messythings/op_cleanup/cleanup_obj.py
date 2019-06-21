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


def cleanup_objects(context):
    obs_to_del = set()
    obs_in_use = set()
    curve_del_count = 0
    lat_del_count = 0
    mesh_del_count = 0

    # Get objects

    for ob in context.scene.objects:

        ob.hide_viewport = False

        if ob.type in {"CURVE", "LATTICE"}:
            obs_to_del.add(ob)

        elif ob.type == "MESH" and not ob.data.vertices:
            ob_del = True

            if ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type == "BOOLEAN" and mod.operation == "UNION" and mod.object:
                        ob_del = False  # Booltron combined object
                        break

            if ob_del:
                obs_to_del.add(ob)

        # Object dependencies

        if ob.modifiers:
            for mod in ob.modifiers:
                if mod.type in {"CURVE", "LATTICE"} and mod.object:
                    obs_in_use.add(mod.object)

        if ob.constraints:
            for con in ob.constraints:
                if con.type == "FOLLOW_PATH" and con.target:
                    obs_in_use.add(con.target)

        if ob.type == "CURVE":
            if ob.data.bevel_object:
                obs_in_use.add(ob.data.bevel_object)
            if ob.data.taper_object:
                obs_in_use.add(ob.data.taper_object)

    # Remove objects

    if obs_to_del:
        for ob in obs_to_del:
            if ob not in obs_in_use:

                if ob.type == "CURVE":
                    curve_del_count += 1
                elif ob.type == "LATTICE":
                    lat_del_count += 1
                elif ob.type == "MESH":
                    mesh_del_count += 1

                bpy.data.objects.remove(ob)

    # Report

    for area in context.screen.areas:
        area.tag_redraw()

    return curve_del_count, lat_del_count, mesh_del_count
