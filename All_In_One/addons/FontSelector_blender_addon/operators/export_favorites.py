import bpy
import os
import shutil
from bpy_extras.io_utils import ExportHelper

from ..functions.misc_functions import absolute_path

from ..global_messages import export_finished, print_statement

class FontSelectorExportFavorites(bpy.types.Operator, ExportHelper) :
    bl_idname = "fontselector.export_fonts"
    bl_label = "Export Fonts"
    bl_description = "Export Favorites of Fake User Fonts"
    filename_ext = ""
    filepath : bpy.props.StringProperty(default = "favorite_fonts")

    zip_toggle : bpy.props.BoolProperty(name = "Zip Compression")
    export_mode : bpy.props.EnumProperty(name = "Fonts to Export",
                                    items={
                                    ('FAVORITES', 'Favorites', 'Export Favorite Fonts'),
                                    ('FAKE_USER', 'Fake User', 'Export Fonts with Fake User'),
                                    ('BOTH', 'Both', 'Export Favorite and Fake User Fonts')},
                                    default='BOTH'
                                    )

    favorites_list = []
    fake_user_list = []
        
    @classmethod
    def poll(cls, context) :
        fontlist = bpy.data.window_managers['WinMan'].fontselector_list
        chk_favorites_fake = 0
        for f in fontlist : 
            if f.favorite :
                chk_favorites_fake = 1
                break
        for f in bpy.data.fonts :
            if f.use_fake_user :
                chk_favorites_fake = 1
                break
        return chk_favorites_fake == 1

    def __init__(self) :
        fontlist = bpy.data.window_managers['WinMan'].fontselector_list
        for f in fontlist :
            if f.favorite :
                self.favorites_list.append(f.filepath)
        for f in bpy.data.fonts :
            if f.use_fake_user :
                self.fake_user_list.append(f.filepath)
        if not self.favorites_list and self.fake_user_list :
            self.export_mode = 'FAKE_USER'
        elif self.favorites_list and not self.fake_user_list :
            self.export_mode = 'FAVORITES'

    def draw(self, context) :
        layout = self.layout
        layout.prop(self, 'zip_toggle')
        if self.favorites_list and self.fake_user_list :
            layout.prop(self, 'export_mode', text = '')
        elif self.favorites_list and not self.fake_user_list :
            layout.label("Favorites Fonts will be exported", icon = 'SOLO_ON')
        elif not self.favorites_list and self.fake_user_list :
            layout.label("Fake User Fonts will be exported", icon = 'FONT_DATA')
    
    def execute(self, context) :
        # return info to user
        self.report({'INFO'}, export_finished)
        print(print_statement + export_finished)
        return fontselector_export_favorites(self.filepath, self.export_mode, self.zip_toggle, self.favorites_list, self.fake_user_list, context)

### Write Export Function ###
def fontselector_export_favorites(filepath, export_mode, zip, favorites_list, fake_user_list, context) :
    export_path = absolute_path(filepath)
    
    # create folder
    if not os.path.isdir(export_path) :
        os.makedirs(export_path)
    
    # copy fonts
    if export_mode in {"BOTH", "FAVORITES"} :
        for filepath in favorites_list :
            newpath = os.path.join(export_path, os.path.basename(filepath))
            shutil.copy2(filepath, newpath)
            shutil.copystat(filepath, newpath)
    if export_mode in {"BOTH", "FAKE_USER"} :
        for filepath in fake_user_list :
            newpath = os.path.join(export_path, os.path.basename(filepath))
            shutil.copy2(filepath, newpath)
            shutil.copystat(filepath, newpath)

    # create zip archive
    if zip :
        shutil.make_archive(export_path, 'zip', export_path)
        shutil.rmtree(export_path)
 
    return {'FINISHED'} 