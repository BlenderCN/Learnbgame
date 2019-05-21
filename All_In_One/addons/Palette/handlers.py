import bpy
import os

from bpy.app.handlers import persistent

from .files_functions import CreatePrefFolder, GetPrefPath, ImportPaletteFile, RefreshPaletteFromFile, CreatePaletteProp
from .node_functions import CreateNodeGroupFromPalette, CreateNodeGroupPaletteGeneral

#handler  
@persistent
def Palette_Startup(scene):
    #create dir if not
    CreatePrefFolder()
    #create winman prop if not
    CreatePaletteProp()
    #refresh palettes
    RefreshPaletteFromFile()
    #create nodegroups
    prop=bpy.data.window_managers['WinMan'].palette[0]
    for p in prop.palettes:
        CreateNodeGroupFromPalette(p)
    CreateNodeGroupPaletteGeneral()
    
    
    print("Color Palettes loaded")