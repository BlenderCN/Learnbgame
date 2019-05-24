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

# <pep8-80 compliant>

bl_info = {
        "name":         "StructureSynth Scene Importer",
        "author":       "Ed Arellano",
        "blender":      (2,67,0),
        "version":      (0,0,1),
        "location":     "File > Import-Export",
        "description":  "Import StructureSynth Scene",
        "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    if "import_ssynth" in locals():
        imp.reload(import_ssynth)

import time
import datetime
import os
import bpy
from bpy.props import (CollectionProperty,
                       StringProperty,
                       BoolProperty,
                       EnumProperty,
                       FloatProperty,
                       )
from bpy_extras.io_utils import (ImportHelper,
                                 axis_conversion,
                                 )

class ImportSSynth(bpy.types.Operator, ImportHelper):
    """Load a StructureSynth scene export"""
    bl_idname       = "import_mesh.ssynth";
    bl_label        = "Import SSynth (.ssynth)";
    bl_options      = {'PRESET', 'UNDO'};

    filename_ext = '.ssynth'
    filter_glob = StringProperty(default='*.ssynth', options={'HIDDEN'})

    
    def execute(self, context):
        
        from . import import_ssynth
        
        print('Importing file', self.filepath)
        
        t = time.mktime(datetime.datetime.now().timetuple())
        
        with open(self.filepath, 'r') as file:
            import_ssynth.load_ssynth_mesh(file, context)
        
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        
        file.close()
        
        print('Finished importing in', t, 'seconds')
        #print('\nSuccessfully imported %r in %.3f sec' % (file, time.time() - t))
        
        return {'FINISHED'}



def menu_func_import(self, context):
    self.layout.operator(ImportSSynth.bl_idname, text="SSynth(.ssynth)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()