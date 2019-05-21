bl_info = {
    "name": "SWG Static Mesh (.msh)",
    "author": "Powerking",
    "blender": (2, 6, 1),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Import-Export Swg Static Mesh Files.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    import imp
    if "import_msh" in locals():
        imp.reload(import_msh)
    if "export_msh" in locals():
        imp.reload(export_msh)

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

class ImportMSH(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.msh"
    bl_label = "Import SWG .msh"
    bl_options = {'PRESET'}

    filename_ext = ".msh"
    filter_glob = StringProperty(default="*.msh", options={'HIDDEN'})

    def execute(self, context):
        bpy.context.user_preferences.edit.use_global_undo = False
        
        # print("Selected: " + context.active_object.name)
        from . import import_msh
        import_msh.load(self, context, self.filepath)
        
        
        bpy.context.user_preferences.edit.use_global_undo = True
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

class ExportMSH(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.msh"
    bl_label = "Export SWG .msh"
    bl_options = {'PRESET'}

    filename_ext = ".msh"
    filter_glob = StringProperty(default="*.msh", options={'HIDDEN'})

    gen_box = BoolProperty(name="Generate Box", description="Generate Bounding Box", default=True)
    gen_sphr = BoolProperty(name="Generate Sphere", description="Generate Bounding Sphere", default=True)
    gen_cyln = BoolProperty(name="Generate Cylinder", description="Generate Bounding Cylinder", default=False)
    
    selected_only = BoolProperty(name="Selected Only", description="Only export selected objects.", default=False)
    
    def execute(self, context):
        from . import export_msh
        export_msh.save(self, context, self.filepath, self.gen_box, self.gen_sphr, self.gen_cyln, self.selected_only)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "gen_box")
        row.prop(self, "gen_sphr")
        row.prop(self, "gen_cyln")
        
        row = layout.row(align=True)
        row.prop(self, "selected_only")

def menu_func_import(self, context):
    self.layout.operator(ImportMSH.bl_idname, text="SWG Static Mesh (.msh)")

def menu_func_export(self, context):
    self.layout.operator(ExportMSH.bl_idname, text="SWG Static Mesh (.msh)")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


# CONVERSION ISSUES
# - matrix problem
# - duplis - only tested dupliverts
# - all scenes export
# + normals calculation

if __name__ == "__main__":
    register()
