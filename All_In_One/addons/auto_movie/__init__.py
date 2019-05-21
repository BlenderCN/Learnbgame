
bl_info = {
    "name": "Auto-movie (.am)",
    "author": "Rabidgremlin",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "File > Import > Auto-movie (.am) ",
    "description": "Import auto-movie files",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

if "bpy" in locals():
    import imp
    if "import_am" in locals():        
        imp.reload(import_am)    
else:
    import bpy    

from bpy.props import StringProperty, BoolProperty

class AmImporter(bpy.types.Operator):
    """Load auto-movie file and create the movie"""
    bl_idname = "import_am.import"
    bl_label = "Import Auto-movie"
    bl_options = {'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(default="*.am", options={'HIDDEN'})

    def execute(self, context):
        from . import import_am
        import_am.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    
def menu_import(self, context):
    self.layout.operator(AmImporter.bl_idname, text="Auto-movie (.am)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_import)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()
