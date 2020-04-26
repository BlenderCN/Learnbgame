import bpy

from ..functions.misc_functions import absolute_path

def load_fake_user() :
    wm = bpy.data.window_managers['WinMan']
    fontlist = wm.fontselector_list
    for font in bpy.data.fonts :
        if font.use_fake_user :
            for font2 in fontlist :
                if font2.filepath == font.filepath :
                    font2.fake_user = True
                    break