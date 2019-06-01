import bpy
import os

from .change_font import change_font
from .change_font_strip import change_font_strip
from .misc_functions import clear_collection

first_active_object = ""
    
#update change font
def update_change_font(self, context) :
    global first_active_object

    #check if the loop is run through the active object
    if first_active_object == "" :

        active = first_active_object = context.active_object
        scn = context.scene
        wm = bpy.data.window_managers['WinMan']
        
        selected = []
        chkerror = 0

        fontlist = wm.fontselector_list
        idx = active.data.fontselector_index

        #error handling for not updated list
        try :
            font = fontlist[idx]
        except IndexError :
            chkerror = 1

        if chkerror == 0 :
            #get selected
            if active.type == 'FONT' and not active.select_get() and not active.data.fontselector_avoid_changes :
                selected.append(active)
            for obj in scn.objects :
                if obj.select_get() and obj.type == 'FONT' and not active.data.fontselector_avoid_changes :
                    selected.append(obj)
            
            #blender font exception
            if fontlist[idx].name == 'Bfont' :
                for obj in selected :
                    obj.data.font = bpy.data.fonts['Bfont']
            #regular change of font
            else :
                for obj in selected :
                    #check if font is already changed
                    if font.name != obj.data.font.name :
                        obj.data.fontselector_index = idx
                        change_font(obj, font)

        #reset global variable                        
        first_active_object = ""

#update save favorites
def update_save_favorites(self, context) :
    active = bpy.context.active_object
    if active is not None :
        if active.type == 'FONT' :
            bpy.ops.fontselector.save_favorites()

#get subdirectories item for enum property
def get_subdirectories_items(self, context) :
    subdir_list = []
    subdir_list.append(("All", "All", "All available Fonts"))
    for sub in bpy.data.window_managers['WinMan'].fontselector_sub :
        subdir_list.append((sub.name, sub.name, sub.filepath))
    return subdir_list

#update change font strip
def update_change_font_strip(self, context) :
    global first_active_object

    #check if the loop is run through the active object or other selected ones
    if first_active_object == "" :
        active_strip = first_active_object = context.scene.sequence_editor.active_strip

        wm = bpy.data.window_managers['WinMan']
        
        selected = []
        chkerror = 0

        fontlist = wm.fontselector_list
        idx = active_strip.fontselector_index
        scn = context.scene
        seq = scn.sequence_editor.sequences_all
        
        #error handling for not updated list
        try :
            font = fontlist[idx]
        except IndexError :
            chkerror = 1

        if chkerror == 0 :
            #get selected
            if active_strip.select and not active_strip.fontselector_avoid_changes :
                selected.append(active_strip)
            for strip in seq :
                if strip.type == 'TEXT' and strip.select and not strip.fontselector_avoid_changes :
                    selected.append(strip)
            
            #blender font exception
            if fontlist[idx].name == 'Bfont' :
                for strip in selected :
                    strip.font = bpy.data.fonts['Bfont']

            #regular change of font
            else :
                for strip in selected :
                    #check if there is a strip font
                    if strip.font is None :
                        strip.fontselector_index = idx
                        change_font_strip(strip, font)
                    else :
                        #check if font is already changed
                        if font.name != strip.font.name :
                            strip.fontselector_index = idx
                            change_font_strip(strip, font)

        #reset global variable                        
        first_active_object = ""