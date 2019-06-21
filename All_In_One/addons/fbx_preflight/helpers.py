# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import re


def redraw_properties():
    for area in bpy.context.screen.areas:
        if area.type == 'PROPERTIES':
            area.tag_redraw()


def group_is_valid(group):
    if not group.name:
        return False
    if len(group.obj_names) < 1:
        return False

    for obj in group.obj_names:
        if not obj.obj_pointer:
            return False
        if bpy.data.objects.get(obj.obj_pointer.name) is None:
            return False

    return True


def groups_are_valid(groups):
    return (len(groups) > 0) and groups_are_unique(groups)


def groups_are_unique(groups):
    group_names = [group.name for group in groups]
    return len(group_names) == len(set(group_names))


def to_camelcase(s):
    """
    Return the given string converted to camelcase. Remove all spaces.
    """
    words = re.split("[^a-zA-Z0-9]+", s)
    return "".join(
        w.lower() if i is 0 else w.title() for i, w in enumerate(words))
