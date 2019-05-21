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

bl_info = {
    "name": "Jedi Academy Import/Export Tools",
    "author": "mrwonko et al",
    "description": "Various Jedi Knight: Jedi Academy related tools: Importers for ASE, GLA, GLM, ROFF and Exporters for ASE, GLA, GLM, animation.cfg, ROFF and MD3",
    "version": (0, 2, 1),
    "blender": (2, 6, 3),
    "location": "File > Import/Export",
    "category": "Import-Export"
}

#  Imports

#  Python
import imp

#  Blender
if "bpy" not in locals():
    import bpy

#  Local
# ASE
if "JAAseExport" in locals():
    imp.reload( JAAseExport )
else:
    from . import JAAseExport
if "JAAseImport" in locals():
    imp.reload( JAAseImport )
else:
    from . import JAAseImport
# Patch
if "JAPatchExport" in locals():
    imp.reload( JAPatchExport )
else:
    from . import JAPatchExport
# ROFF
if "JARoffImport" in locals():
    imp.reload( JARoffImport )
else:
    from . import JARoffImport
if "JARoffExport" in locals():
    imp.reload( JARoffExport )
else:
    from . import JARoffExport
# MD3
if "JAMd3Export" in locals():
    imp.reload( JAMd3Export )
else:
    from . import JAMd3Export
# Ghoul 2
if "JAG2Panels" in locals():
    imp.reload( JAG2Panels )
else:
    from . import JAG2Panels
if "JAG2Operators" in locals():
    imp.reload( JAG2Operators )
else:
    from . import JAG2Operators

# there must be at least one operator in the locals for Blender to reload correctly.
JAAseExportOp = JAAseExport.Operator

def register():
    bpy.utils.register_module(__name__)
    
    JAG2Panels.initG2Properties()
    JAG2Operators.register();
    
    bpy.types.INFO_MT_file_export.append(JAAseExport.menu_func)
    bpy.types.INFO_MT_file_export.append(JAPatchExport.menu_func)
    bpy.types.INFO_MT_file_export.append(JARoffExport.menu_func)
    bpy.types.INFO_MT_file_export.append(JAMd3Export.menu_func)
    
    bpy.types.INFO_MT_file_import.append(JAAseImport.menu_func)
    bpy.types.INFO_MT_file_import.append(JARoffImport.menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    
    JAG2Operators.unregister()
    
    bpy.types.INFO_MT_file_export.remove(JAAseExport.menu_func)
    bpy.types.INFO_MT_file_export.remove(JAPatchExport.menu_func)
    bpy.types.INFO_MT_file_export.remove(JARoffExport.menu_func)
    bpy.types.INFO_MT_file_export.remove(JAMd3Export.menu_func)
    
    bpy.types.INFO_MT_file_import.remove(JAAseImport.menu_func)
    bpy.types.INFO_MT_file_import.remove(JARoffImport.menu_func)


if __name__ == "__main__":
    register()
