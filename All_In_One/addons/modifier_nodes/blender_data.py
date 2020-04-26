### BEGIN GPL LICENSE BLOCK #####
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

# <pep8 compliant>


class RNAPathValue():
    """Value type for storing bpy paths which get inserted directly into generated code."""

    def __init__(self, path_string):
        self.value = path_string

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


_rna_path_base_map = {
    'bdata' : "bpy.data",
    'object' : "__object__",
    }

def rna_path_value(base, struct_path, prop, prop_index):
    path = "%s." % _rna_path_base_map[base]
    if struct_path:
        path += "%s." % struct_path
    path += prop
    if prop_index is not None:
        path += "[%r]" % prop_index
    return RNAPathValue(path)
