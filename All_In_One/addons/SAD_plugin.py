import bpy
from utils import parseInputFile, addDataToScene

bl_info = {
    "name": "SAD data importer",
    "description": "Imports a text file containing SAD data.",
    "author": "Martin Valmo Normann",
    "version": (1, 0),
    "blender": (2, 68, 0),
    "location": "File > Import > Import SAD data",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "category": "Learnbgame"
}

class Import_SAD_Data(bpy.types.Operator):
    """Importer operator for SAD data"""
    bl_idname = "import.sad_data"
    bl_label = "Import SAD data"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # with open(self.filepath, 'r') as f:
        data = parseInputFile(self.filepath)
        addDataToScene(data)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


#Add to import menu 
def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(Import_SAD_Data.bl_idname, text="Import SAD data")

def register():
    # Register and add to the file selector
    bpy.utils.register_class(Import_SAD_Data)
    bpy.types.INFO_MT_file_import.append(menu_func)

 
 
def unregister():
    bpy.utils.unregister_class(Import_SAD_Data)
    bpy.types.INFO_MT_file_import.remove(menu_func)

