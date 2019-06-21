'''
Copyright (C) 2018 Samy Tichadou (tonton)
samytichadou@gmail.com

Created by Samy Tichadou (tonton)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {  
 "name": "Font Selector",  
 "author": "Samy Tichadou (tonton)",  
 "version": (2, 0),  
 "blender": (2, 80, 0),  
 "location": "Properties > Font > Font selection",  
 "description": "Select Fonts directly in the property panel",  
  "wiki_url": "https://github.com/samytichadou/FontSelector_blender_addon/wiki",  
 "tracker_url": "https://github.com/samytichadou/FontSelector_blender_addon/issues/new",  
 "category": "Learnbgame",
 }


import bpy


# IMPORT SPECIFICS
##################################


from .functions.misc_functions import menu_export_favorites
from .startup_handler import fontselector_startup
from .functions.update_functions import update_change_font, get_subdirectories_items, update_change_font_strip


from .properties import *
from .gui import *
from .preferences import *
from .ui_lists import *
from .operators.add_filepath import *
from .operators.check_changes import *
from .operators.dialog_message import *
from .operators.export_favorites import *
from .operators.load_fontlist import *
from .operators.load_preferences import *
from .operators.modal_refresh import *
from .operators.open_folder import *
from .operators.remove_unused_fonts import *
from .operators.save_favorites import *
from .operators.save_preferences import *
from .operators.suppress_filepath import *
from .operators.open_font_folder import *


# register
##################################

classes = (FontSelectorFontList, 
            FontSelectorFontSubs, 
            FontFolders,
            FontSelectorPanel,
            FontSelectorAddonPrefs,
            FontUIList,
            FontSelectorAddFP,
            FontSelectorCheckChanges,
            FontSelectorDialogMessage,
            FontSelectorExportFavorites,
            FontSelectorLoadFontList,
            FontSelectorLoadFPPrefs,
            FontSelectorModalRefresh,
            FontSelectorOpenSubdirectory,
            FontSelectorRemoveUnused,
            FontSelectorSaveFavorites,
            FontSelectorSaveFPPrefs,
            FontSelectorSuppressFP,
            FontSelectorOpenFontFolder,
            SEQUENCER_PT_font_selector
            )

def register():

    ### OPERATORS ###

    from bpy.utils import register_class
    for cls in classes :
        register_class(cls)

    ### PROPS ###

    # GLOBAL PROPS
    bpy.types.WindowManager.fontselector_list = \
        bpy.props.CollectionProperty(type = FontSelectorFontList)
    bpy.types.WindowManager.fontselector_sub = \
        bpy.props.CollectionProperty(type = FontSelectorFontSubs)
    bpy.types.WindowManager.fontselector_subdirectories = \
        bpy.props.EnumProperty(items = get_subdirectories_items, 
                                name = "Subdirectories",
                                description = "Display only specific Subdirectories")

    # TEXT OBJECT PROPS
    bpy.types.TextCurve.fontselector_index = \
        bpy.props.IntProperty(update = update_change_font, default = -1)

    bpy.types.TextCurve.fontselector_font = \
        bpy.props.StringProperty()

    bpy.types.TextCurve.fontselector_font_missing = \
        bpy.props.BoolProperty(default = False)

    bpy.types.TextCurve.fontselector_avoid_changes = \
        bpy.props.BoolProperty(default = False)

    # TEXT STRIP PROPS
    bpy.types.TextSequence.fontselector_index = \
        bpy.props.IntProperty(update = update_change_font_strip, default = -1)

    bpy.types.TextSequence.fontselector_font = \
        bpy.props.StringProperty()

    bpy.types.TextSequence.fontselector_font_missing = \
        bpy.props.BoolProperty(default = False)

    bpy.types.TextSequence.fontselector_avoid_changes = \
        bpy.props.BoolProperty(default = False)

    ### HANDLER ###

    bpy.app.handlers.load_post.append(fontselector_startup)
    
    ### EXPORT MENU ###

    bpy.types.TOPBAR_MT_file_export.append(menu_export_favorites)

def unregister():
    
    ### OPERATORS ###

    from bpy.utils import unregister_class
    for cls in reversed(classes) :
        unregister_class(cls)

    ### PROPS ###

    # GLOBAL PROPS
    del bpy.types.WindowManager.fontselector_list
    del bpy.types.WindowManager.fontselector_sub
    del bpy.types.WindowManager.fontselector_subdirectories

    # TEXT OBJECT PROPS
    del bpy.types.TextCurve.fontselector_index
    del bpy.types.TextCurve.fontselector_font
    del bpy.types.TextCurve.fontselector_font_missing
    del bpy.types.TextCurve.fontselector_avoid_changes

    # TEXT STRIPS PROPS
    del bpy.types.TextSequence.fontselector_index
    del bpy.types.TextSequence.fontselector_font
    del bpy.types.TextSequence.fontselector_font_missing
    del bpy.types.TextSequence.fontselector_avoid_changes
    
    ### HANDLER

    bpy.app.handlers.load_post.remove(fontselector_startup)
    
    ### EXPORT MENU ###

    bpy.types.TOPBAR_MT_file_export.remove(menu_export_favorites)