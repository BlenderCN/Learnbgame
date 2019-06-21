import bpy
import os

class ISCDPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "ISCD"

class ioPanel(ISCDPanel):
    bl_idname      = "iscd.setup_panel"
    bl_label       = "Import / Export"
    def draw(self, context):
        self.layout.operator("iscd.import_mesh", icon="IMPORT", text="Import a .mesh")
        self.layout.operator("iscd.export_mesh", icon="EXPORT", text="Export a .mesh")
        self.layout.operator("iscd.import_mesh_sequence_morphing", icon="IMPORT", text="Import a .mesh morphing")
        self.layout.operator("iscd.import_mesh_sequence_fluids",   icon="IMPORT", text="Import a .mesh fluidsim")
        self.layout.operator("iscd.import_mesh_sequence_fds",      icon="IMPORT", text="Import a fds simulation")

#register and unregister
def register():
    bpy.utils.register_class(ioPanel)
    #bpy.types.INFO_MT_file_import.append(import_func)
    #bpy.types.INFO_MT_file_export.append(export_func)
def unregister():
    bpy.utils.unregister_class(ioPanel)
    #bpy.types.INFO_MT_file_import.remove(import_func)
    #bpy.types.INFO_MT_file_export.remove(export_func)
