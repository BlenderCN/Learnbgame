bl_info = {
    "name": "Final Fantasy VII Format",
    "author": "Jacob Valenta (jacob.valenta@gmail.com)",
    "blender": (2, 7, 3),
    "location": "File > Import-Export",
    "description": "Adds support for import/export of Final Fantasy VII files",
    "warning": "",
    "wiki_url": "www.github.com/jacobvalenta/ffimport/",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Learnbgame"
}

import bpy
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       )
from bpy_extras.io_utils import (ExportHelper,
                                 ImportHelper,
                                 path_reference_mode,
                                 axis_conversion,
                                 )


class ImportFF7(bpy.types.Operator, ImportHelper):
    '''Load a Final Fantasy VII file'''
    bl_idname = "import_scene.ff7"
    bl_label = "Import FF7"
    bl_options = {'UNDO'}

    filename_ext = ".hrc"
    filter_glob = StringProperty(
            default="*.hrc;*.p",
            options={'HIDDEN'},
            )

    debug = BoolProperty(
            name="Debug",
            description="Show Debug information",
            default=True,
            )

    def execute(self, context):
        from . import import_ff7
        return import_ff7.load(self.properties)

    # def draw(self, context):
    #     layout = self.layout

    #     row = layout.row(align=True)
    #     row.prop(self, "simpleBool")




class ExportFF7(bpy.types.Operator, ExportHelper):
    '''Save a Final Fantasy VII File'''
    bl_idname = "export_scene.ff7"
    bl_label = 'Export FF7'
    bl_options = {'UNDO'}
    filename_ext = ".hrc"
    filter_glob = StringProperty(default="*.hrc;*.p", options={'HIDDEN'},)

    # context group
    myBool = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    def execute(self, context):
        #from . import export_ff7
        return {'FINISHED'}
        #return export_obj.save(self, context, **keywords)



def menu_func_import(self, context):
    self.layout.operator(ImportFF7.bl_idname, text="Final Fantasy VII")

def menu_func_export(self, context):
    self.layout.operator(ExportFF7.bl_idname, text="Final Fantasy VII")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
