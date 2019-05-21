import bpy

from .functions.update_functions import update_save_favorites


class FontSelectorFontList(bpy.types.PropertyGroup) :
    '''name : StringProperty() '''
    filepath : bpy.props.StringProperty(name = "File Path")
    missingfont : bpy.props.BoolProperty(name = "Missing Font", default = False)
    favorite : bpy.props.BoolProperty(name = "Favorite",
                                    default = False, 
                                    update = update_save_favorites,
                                    description = "Mark/Unmark as Favorite Font")
    subdirectory : bpy.props.StringProperty(name="Subdirectory")
    index : bpy.props.IntProperty()

class FontSelectorFontSubs(bpy.types.PropertyGroup) :
    '''name : StringProperty() '''
    filepath : bpy.props.StringProperty(name = "filepath")

class FontFolders(bpy.types.PropertyGroup) :
    '''name : StringProperty() '''
    folderpath : bpy.props.StringProperty(
            name = "Folder path",
            description = "Folders where Fonts are stored",
            subtype = "DIR_PATH",
            )