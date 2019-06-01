# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 02:35:29 2019

@author: AsteriskAmpersand
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 14:09:29 2019

@author: AsteriskAmpersand
"""
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from ..fmod import FModImporterLayer

class ImportFMOD(Operator, ImportHelper):
    bl_idname = "custom_import.import_mhf_fmod"
    bl_label = "Load MHF FMOD file (.fmod)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
 
    # ImportHelper mixin class uses this
    filename_ext = ".fmod"
    filter_glob = StringProperty(default="*.fmod", options={'HIDDEN'}, maxlen=255)

    clear_scene = BoolProperty(
        name = "Clear scene before import.",
        description = "Clears all contents before importing",
        default = True)
    import_textures = BoolProperty(
        name = "Import Textures.",
        description = "Imports textures through the God give me Wisdom algorithm that randomly and desperately looks for them.",
        default = True)

    def execute(self,context):
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        bpy.ops.object.select_all(action='DESELECT')
        importer = FModImporterLayer.FModImporter()
        importer.clearScene()
        importer.maximizeClipping()
        importer.execute(self.properties.filepath, self.import_textures)
        importer.maximizeClipping()
        return {'FINISHED'}
    
    
def menu_func_import(self, context):
    self.layout.operator(ImportFMOD.bl_idname, text="MHF FMOD (.fmod)")
