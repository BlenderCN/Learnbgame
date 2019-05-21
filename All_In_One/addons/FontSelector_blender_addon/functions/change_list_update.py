import bpy
import os


from .change_font import change_font
from .change_font_strip import change_font_strip
from .misc_functions import avoid_changes_selected, absolute_path, create_warning_font


# change font when change in list to relink fonts
def change_list_update() :
    wm = bpy.data.window_managers['WinMan']
    fontlist = wm.fontselector_list
    missing_list = ""

    # set the avoid objects
    avoid_list = avoid_changes_selected()

    # 3d text object
    for obj in bpy.data.objects :
        if obj.type == 'FONT' and obj.data.fontselector_font != "" :

                # relink if possible
                old_font = obj.data.fontselector_font
                chk_font_exists = 0
                for font in fontlist :
                    if font.name == old_font :
                        obj.data.fontselector_index = font.index
                        change_font(obj, font)
                        chk_font_exists = 1
                        break
                
                # missing
                if chk_font_exists == 0 :

                    # check if file exist, if not, remove datablock and put warning font instead
                    abspath = absolute_path(obj.data.font.filepath)
                    if not os.path.isfile(abspath) :
                        # remove datablock
                        vector_font = obj.data.font
                        bpy.data.fonts.remove(vector_font, do_unlink=True)
                        # warning font
                        obj.data.font = create_warning_font()

                    obj.data.fontselector_font_missing = True
                    # prevent automatic changes via index
                    obj.data.fontselector_index = -1
                    missing_list += "Object : " + obj.name

    # strip text
    for scn in bpy.data.scenes :
        seq = scn.sequence_editor.sequences_all
        for strip in seq :
            if strip.type == 'TEXT' and strip.fontselector_font != "" :

                #relink if possible
                old_font = strip.fontselector_font
                chk_font_exists = 0
                for font in fontlist :
                    if font.name == old_font :
                        strip.fontselector_index = font.index
                        change_font_strip(strip, font)
                        chk_font_exists = 1
                        break
                if chk_font_exists == 0 :

                    # check if file exist, if not, remove datablock and put warning font instead
                    abspath = absolute_path(strip.font.filepath)
                    if not os.path.isfile(abspath) :
                        # remove datablock
                        vector_font = strip.font
                        bpy.data.fonts.remove(vector_font, do_unlink=True)
                        # warning font
                        strip.font = create_warning_font()

                    strip.fontselector_font_missing = True
                    # prevent automatic changes via index
                    strip.fontselector_index = -1
                    missing_list += "Strip : " + strip.name

    # reset avoid properties
    for obj in avoid_list :
        obj.fontselector_avoid_changes = False
    
    # warning message
    if missing_list != "" :
        bpy.ops.fontselector.dialog_message('INVOKE_DEFAULT', code = 8, customstring = missing_list)