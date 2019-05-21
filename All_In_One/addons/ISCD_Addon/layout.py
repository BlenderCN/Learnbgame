import bpy
import os
import importlib

#Check which softwares are allready installed
installed = {"cork":False, "medit":False, "mmgs_O3":False, "mpmetis":False, "super4PCS":False, "tetgen":False}
for software in installed:
    err = os.system("which "+software)
    if not err:
        installed[software] = True

#Define the UI layout
class uiPanel(bpy.types.Panel):
    bl_idname      = "panel.mesh_panel"
    bl_label       = "built in tools"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "ISCD"
    def draw(self, context):
        self.layout.operator("import_mesh.mesh", icon="IMPORT", text="Import .mesh")
        self.layout.operator("export_mesh.mesh", icon="EXPORT", text="Export .mesh")
        self.layout.operator("import_mesh.sequence", icon="ANIM_DATA", text="Import sequence")
        self.layout.operator("object.weight2vertexcol", icon="MOD_VERTEX_WEIGHT", text="Weight paint to vertex color")
        self.layout.operator("mesh.bake", icon="RENDER_STILL", text="Baking")
        self.layout.operator("mesh.adddomain", icon="FORCE_WIND", text="Add a computational domain")
class uiPanel2(bpy.types.Panel):
    bl_idname      = "panel.mesh_panel2"
    bl_label       = "external tools"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "ISCD"
    def draw(self, context):
        if installed["mmgs_O3"]:
            self.layout.operator("mesh.mmgs", icon="MOD_DECIM", text="mmgs remesh")
        if installed["tetgen"]:
            self.layout.operator("mesh.tetgen_fill", icon="MOD_BUILD", text="tetgen fill")
        if installed["medit"]:
            self.layout.operator("preview.medit", icon="FILE_MOVIE", text="medit preview")
        if installed["mpmetis"]:
            self.layout.operator("mesh.metis_partition", icon="MOD_EXPLODE", text="metis partition")
        if installed["cork"]:
            self.layout.operator("mesh.cork", icon="MOD_BOOLEAN", text="cork booleans")
class uiPanel3(bpy.types.Panel):
    bl_idname      = "panel.mesh_panel3"
    bl_label       = "other"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "ISCD"
    def draw(self, context):
        if importlib.find_loader('scipy') is not None:
            self.layout.operator("mesh.icp", icon="MOD_ARRAY", text="ICP alignement")
        if installed["super4PCS"]:
            self.layout.operator("mesh.superpcs", icon="MOD_ARRAY", text="Super4PCS alignement")

#Menus
def import_func(self, context):
    self.layout.operator("import_mesh.mesh", text="Import .mesh")
def export_func(self, context):
    self.layout.operator("export_mesh.mesh", text="Export .mesh")

#register and unregister
def register():
    bpy.utils.register_class(uiPanel)
    bpy.utils.register_class(uiPanel2)
    bpy.utils.register_class(uiPanel3)
    bpy.types.INFO_MT_file_import.append(import_func)
    bpy.types.INFO_MT_file_export.append(export_func)
def unregister():
    bpy.utils.unregister_class(uiPanel)
    bpy.utils.unregister_class(uiPanel2)
    bpy.utils.unregister_class(uiPanel3)
    bpy.types.INFO_MT_file_import.remove(import_func)
    bpy.types.INFO_MT_file_export.remove(export_func)
