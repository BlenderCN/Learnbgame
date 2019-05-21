import bpy

from . import import_d3dbsp

bl_info = {
    "name": "CoD2D3DBSP Importer",
    "description": "Import Call of Duty 2 d3dbsp map files into blender.",
    "author": "Soma Rádóczi",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "File > Import/Export",
    "category": "Import-Export",
    "warning": "This addon is still in development.",
    #"wiki_url": "",
}


def menu_func_import_d3dbsp(self, context):
    self.layout.operator(import_d3dbsp.D3DBSPImporter.bl_idname, text = "CoD2 D3DBSP map (.d3dbsp)")

def register():
    bpy.utils.register_class(import_d3dbsp.D3DBSPImporter)
    bpy.types.INFO_MT_file_import.append(menu_func_import_d3dbsp)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import_d3dbsp)
    bpy.utils.unregister_class(import_d3dbsp.D3DBSPImporter)

if __name__ == "__main__":
    unregister()
    register()


    