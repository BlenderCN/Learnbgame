# -*- coding: utf-8 -*-
"""LDR Importer GPLv2 license.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""


import bpy

from . import import_ldraw

bl_info = {
    "name": "LDR Importer",
    "description": "Import LDraw models in .ldr and .dat format",
    "author": "LDR Importer developers and contributors",
    "version": (1, 4, 0),
    "blender": (2, 67, 0),
    "api": 31236,
    "location": "File > Import",
    "warning": "Incomplete Cycles support, MPD and Bricksmith models not supported",  # noqa
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Import-Export/LDRAW_Importer",  # noqa
    "tracker_url": "https://github.com/le717/LDR-Importer/issues",
    "category": "Learnbgame",
    }


def menuImport(self, context):
    """Import menu listing label."""
    self.layout.operator(import_ldraw.LDRImporterOps.bl_idname,
                         text="LDraw (.ldr/.dat)")


def register():
    """Register Menu Listing."""
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menuImport)


def unregister():
    """Unregister Menu Listing."""
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menuImport)


if __name__ == "__main__":
    register()
