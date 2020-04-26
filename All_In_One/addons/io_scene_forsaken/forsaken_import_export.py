#
# Copyright(C) 2017-2018 Samuel Villarreal
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import os
import bpy
from bpy.props import (
        CollectionProperty,
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        path_reference_mode,
        axis_conversion,
        )
        
#-----------------------------------------------------------------------------
#
# Importing Tools
#
#-----------------------------------------------------------------------------

IOForsakenOrientationHelper = orientation_helper_factory("IOForsakenOrientationHelper", axis_forward='Y', axis_up='Z')
IOForsakenImportMXOrientationHelper = orientation_helper_factory("IOForsakenImportMXOrientationHelper", axis_forward='Z', axis_up='Y')

# -----------------------------------------------------------------------------
#
class ImportForsakenMXData(bpy.types.Operator, ImportHelper, IOForsakenImportMXOrientationHelper):
    bl_idname = "import_mesh.mx"
    bl_label = "Import MX"
    bl_options = {'UNDO'}

    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the MX file",
                          type=bpy.types.OperatorFileListElement)

    directory = StringProperty()

    filename_ext = ".mx"
    filter_glob = StringProperty(default="*.mx;*.mxa", options={'HIDDEN'})

    def execute(self, context):
        paths = [os.path.join(self.directory, name.name)
                 for name in self.files]
        if not paths:
            paths.append(self.filepath)

        from mathutils import Matrix
        from . import import_forsaken_mx
        
        global_matrix = (Matrix.Scale(1.0/256.0, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
                                         
        import_forsaken_mx.load(self, context, self.filepath, global_matrix)

        return {'FINISHED'}
 
# -----------------------------------------------------------------------------
#
class ImportForsakenCOBData(bpy.types.Operator, ImportHelper, IOForsakenImportMXOrientationHelper):
    bl_idname = "import_mesh.cob"
    bl_label = "Import COB"
    bl_options = {'UNDO'}

    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the COB file",
                          type=bpy.types.OperatorFileListElement)

    directory = StringProperty()

    filename_ext = ".cob"
    filter_glob = StringProperty(default="*.cob", options={'HIDDEN'})

    def execute(self, context):
        paths = [os.path.join(self.directory, name.name)
                 for name in self.files]
        if not paths:
            paths.append(self.filepath)

        from mathutils import Matrix
        from . import import_forsaken_cob
        
        global_matrix = (Matrix.Scale(1.0/256.0, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
                                         
        import_forsaken_cob.load(self, context, self.filepath, global_matrix)

        return {'FINISHED'}
        
 
# -----------------------------------------------------------------------------
#
class ImportForsakenLevel(bpy.types.Operator, ImportHelper, IOForsakenImportMXOrientationHelper):
    bl_idname = "import_level.mxv"
    bl_label = "Import MXV"
    bl_options = {'UNDO'}

    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the MXV file",
                          type=bpy.types.OperatorFileListElement)

    directory = StringProperty()

    filename_ext = ".mxv"
    filter_glob = StringProperty(default="*.mxv", options={'HIDDEN'})

    def execute(self, context):
        paths = [os.path.join(self.directory, name.name)
                 for name in self.files]
        if not paths:
            paths.append(self.filepath)

        from mathutils import Matrix
        from . import import_forsaken_level
        
        global_matrix = (Matrix.Scale(1.0/256.0, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
                                         
        import_forsaken_level.load(self, context, self.filepath, global_matrix)

        return {'FINISHED'}
        
#-----------------------------------------------------------------------------
#
# Exporting Tools
#
#-----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
class ExportForsakenCOBData(bpy.types.Operator, ExportHelper, IOForsakenImportMXOrientationHelper):
    bl_idname = "export_mesh.cob"
    bl_label = 'Export COB'
    bl_options = {'PRESET'}

    filename_ext = ".cob"
    filter_glob = StringProperty(
            default="*.cob",
            options={'HIDDEN'},
            )
            
    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    path_mode = path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import export_forsaken_cob

        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "check_existing",
                                            "filter_glob",
                                            ))

        global_matrix = (Matrix.Scale(256.0, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())

        keywords["global_matrix"] = global_matrix
        return export_forsaken_cob.save(context, **keywords)
        
        
# -----------------------------------------------------------------------------
#
class ExportForsakenMXData(bpy.types.Operator, ExportHelper, IOForsakenImportMXOrientationHelper):
    bl_idname = "export_mesh.mx"
    bl_label = 'Export MX'
    bl_options = {'PRESET'}

    filename_ext = ".mx"
    filter_glob = StringProperty(
            default="*.mx;*.mxa",
            options={'HIDDEN'},
            )
            
    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    path_mode = path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import export_forsaken_mx

        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "check_existing",
                                            "filter_glob",
                                            ))

        global_matrix = (Matrix.Scale(256.0, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())

        keywords["global_matrix"] = global_matrix
        return export_forsaken_mx.save(context, **keywords)
        
# -----------------------------------------------------------------------------
#
class ExportForsakenLevelData(bpy.types.Operator, ExportHelper, IOForsakenOrientationHelper):
    bl_idname = "export_scene.txt"
    bl_label = 'Export TXT'
    bl_options = {'PRESET'}

    filename_ext = ".txt"
    filter_glob = StringProperty(
            default="*.txt;*.mtl",
            options={'HIDDEN'},
            )
            
    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    path_mode = path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import export_forsaken

        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "check_existing",
                                            "filter_glob",
                                            ))

        global_matrix = (Matrix.Scale(256.0, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())

        keywords["global_matrix"] = global_matrix
        return export_forsaken.save(context, **keywords)
        
#-----------------------------------------------------------------------------
#
# Menu Function Defines
#
#-----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
def menu_func_export(self, context):
    self.layout.operator(ExportForsakenLevelData.bl_idname, text="Forsaken Level Info (.txt)")

# -----------------------------------------------------------------------------
#
def menu_func_import_mx(self, context):
    self.layout.operator(ImportForsakenMXData.bl_idname, text="Forsaken Model Data (.mx/.mxa)")
    
# -----------------------------------------------------------------------------
#
def menu_func_export_mx(self, context):
    self.layout.operator(ExportForsakenMXData.bl_idname, text="Forsaken Model Data (.mx/.mxa)")
 
# -----------------------------------------------------------------------------
#
def menu_func_import_cob(self, context):
    self.layout.operator(ImportForsakenCOBData.bl_idname, text="Forsaken Componented Model Data (.cob)")
 
# -----------------------------------------------------------------------------
#
def menu_func_export_cob(self, context):
    self.layout.operator(ExportForsakenCOBData.bl_idname, text="Forsaken Componented Model Data (.cob)")

# -----------------------------------------------------------------------------
#
def menu_func_import_mxv(self, context):
    self.layout.operator(ImportForsakenLevel.bl_idname, text="Forsaken Level Data (.mxv)")
    
# -----------------------------------------------------------------------------
#
def register():
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_file_import.append(menu_func_import_mx)
    bpy.types.INFO_MT_file_export.append(menu_func_export_mx)
    bpy.types.INFO_MT_file_import.append(menu_func_import_cob)
    bpy.types.INFO_MT_file_export.append(menu_func_export_cob)
    bpy.types.INFO_MT_file_import.append(menu_func_import_mxv)

# -----------------------------------------------------------------------------
#
def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_mx)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_mx)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_cob)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_cob)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_mxv)
