import bpy
import os


def change_font(obj, font):
    name = os.path.basename(font.filepath)
    
    if os.path.isfile(font.filepath) :
        chkunused = 0
        chklocal = 0

        #check for local font
        for f in bpy.data.fonts :
            if f.filepath == font.filepath :
                chklocal= 1
                new_font = f
                break

        #check unused font
        if chklocal == 0 :
            for f in bpy.data.fonts :
                if f.users == 0 and f.filepath != font.filepath and chkunused == 0 :
                    chkunused = 1
                    #f.name = os.path.splitext(name)[0]
                    f.name = font.name
                    f.filepath = font.filepath
                    new_font = f
                    break
        
        #import font
        if chkunused == 0 and chklocal == 0 :
            new_font = bpy.data.fonts.load(filepath=font.filepath)

        obj.data.font = new_font
        
        #set object font property
        obj.data.fontselector_font = font.name

        #toggle missing if True
        if obj.data.fontselector_font_missing :
            obj.data.fontselector_font_missing = False
        
    #no font file
    else:
        font.missingfont=True
