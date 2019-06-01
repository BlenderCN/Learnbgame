import bpy
import os
import math

from sys import platform

from .addon_prefs import get_addon_preferences
from .node_functions import UpdateNodeGroupColor, UpdateNodeGroupColorNames, PaletteNodeUpdate

# absolute path
def AbsolutePath(path):
    absolutepath=os.path.abspath(bpy.path.abspath(path))
    return absolutepath

#get absolute pref path
def GetPrefPath():
    prefs=get_addon_preferences()
    path=AbsolutePath(prefs.prefs_folderpath)
    return path

# create pref folder if doesn't exist
def CreatePrefFolder():
    prefs=get_addon_preferences()
    folder=AbsolutePath(prefs.prefs_folderpath)
    if os.path.isdir(folder)==False:
        os.mkdir(folder)
    return {'FINISHED'}

# get basename no extension with path
def GetFileBasename(path):
    basename=os.path.splitext(os.path.basename(path))[0]
    return basename

# import palette file
def ImportPaletteFile(path):
    file=AbsolutePath(path)
    #check file
    if os.path.isfile(file)==True and file.endswith(".gpl"):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        new_palette=prop.palettes.add()
        new_palette.name=GetFileBasename(file)
        new_palette.filepath=file
        with open(file) as f:
            content = f.readlines()
        #content = [x.strip() for x in content]
        
        for i in range(3, len(content)):
            if content[i]!='':
                col=new_palette.colors.add()
                name=content[i][12:].split(' #')[0]
                col.name=name
                hex=content[i].split('#')[1].strip()
                col.color_value=ConvertRGBBase255toRGBBase1(ConvertHEXtoRGBBase255(hex))
 
    return {'FINISHED'}

# refresh palettes from files
def RefreshPaletteFromFile():
    prefpath=GetPrefPath()
    for f in os.listdir(prefpath):
        ImportPaletteFile(os.path.join(prefpath, f))
    return{'FINISHED'}

# create winman if not
def CreatePaletteProp():
    palette_prop=bpy.data.window_managers['WinMan'].palette
    if len(palette_prop)==0:
        palette_prop.add()
    return {'FINISHED'}

# check if palette file exists
def CheckPaletteFile(name):
    if os.path.isfileos.path.join(GetPrefPath(), name+".gpl")==True:
        check=1
    else:
        check=0
    return check

# create palette file
def SavePaletteFile(palette):
    prefpath=GetPrefPath()
    file=os.path.join(prefpath, palette.name+".gpl")
    nfile = open(file, "w")
    nfile.write("GIMP Palette\n")
    nfile.write("Name: "+palette.name+"\n")
    nfile.write("Columns: 5\n")
    for c in palette.colors:
        r,v,b=ConvertRGBBase1toRGBBase255(c.color_value)
        nfile.write(str(r).rjust(3)+" ")
        nfile.write(str(v).rjust(3)+" ")
        nfile.write(str(b).rjust(3)+" ")
        nfile.write(c.name+" ")
        nfile.write(ConvertRVBBase255toHEX([r,v,b]))
        nfile.write('\n')
    nfile.close()
    return {'FINISHED'}

# update palette files
def UpdatePaletteFiles(self, context):
    prop=bpy.data.window_managers['WinMan'].palette[0]
    for p in prop.palettes:
        SavePaletteFile(p)
        UpdateNodeGroupColor(p)
        
# delete palette file
def RemovePaletteFile(palette):
    file=palette.filepath
    if os.path.isfile(file)==True:
        os.remove(file)
    return {'FINISHED'}

# rename palette files
def RenamePaletteFiles(self, context):
    prefpath=GetPrefPath()
    prop=bpy.data.window_managers['WinMan'].palette[0]
    for p in prop.palettes:
        if p.name!="___temp___":
            if GetFileBasename(p.filepath)!=p.name and os.path.isfile(p.filepath)==True:
                dst=os.path.join(prefpath, p.name+".gpl")
                os.rename(p.filepath,dst)  
                p.filepath=dst
                
# rename colors without dupes
def RenameColorWithoutDupes(palette):
    oname=[]
    torename=[]
    for c in palette.colors:
        if c.name not in oname:
            oname.append(c.name)
        else:
            torename.append(c)
    for n in torename:
        nb=oname.count(n.name)
        n.name+="_"+str(nb)
    return {'FINISHED'}

# update name and palette file
def UpdateColorName(self, context):
    prop=bpy.data.window_managers['WinMan'].palette[0]
    try:
        active=prop.palettes[prop.index]
        #RenameColorWithoutDupes(active)
        UpdateNodeGroupColorNames(active)
        PaletteNodeUpdate(self, context)
        UpdatePaletteFiles(self, context)
    except:
        pass
    
# convert rgb base 1 to rgb base 255
def ConvertRGBBase1toRGBBase255(col):
    r,v,b=col
    nr=round(r*255)
    if nr==256:
        nr=255
    nv=round(v*255)
    if nv==256:
        nv=255
    nb=round(b*255)
    if nb==256:
        nb=255
    ncol=[nr,nv,nb]    
    return ncol

# convert rgb base 255 to rgb base 1
def ConvertRGBBase255toRGBBase1(col):
    r,v,b=col
    nr=r/255
    nv=v/255
    nb=b/255
    ncol=[nr,nv,nb]    
    return ncol

# convert rgb base 255 to hex
def ConvertRVBBase255toHEX(col):
    r,v,b=col
    nr=str(hex(r)).split('0x')[1].upper().zfill(2)
    nv=str(hex(v)).split('0x')[1].upper().zfill(2)
    nb=str(hex(b)).split('0x')[1].upper().zfill(2)
    hexa='#'+nr+nv+nb
    return hexa

# convert hex to rgb base 1
def ConvertHEXtoRGBBase255(colhex):
    r, g, b = bytes.fromhex(colhex)
    ncol=[r,g,b]
    return ncol

# open folder path in explorer
def OpenFolder(folderpath):
    myOS = platform
    if myOS.startswith('linux') or myOS.startswith('freebsd'):
        cmd = 'xdg-open '
    elif myOS.startswith('win'):
        cmd = 'explorer '
        if not folderpath:
            return('/')
    else:
        cmd = 'open '
    if not folderpath:
        return('//')
    folderpath = '"' + folderpath + '"'
    fullcmd = cmd + folderpath
    os.system(fullcmd)
    return {'FINISHED'}

# generate image pantone
def GenerateImageFromPalette(name, palette, sizex, sizey):
    #remove image if existing
    try:
        bpy.data.images.remove(bpy.data.images[name])
    except KeyError:
        pass
    image = bpy.data.images.new(name, width=sizex, height=sizey)
    squarenb=len(palette.colors)
    sqsize=sizex/squarenb
    pixels = [None] * sizex * sizey

    #color squares
    ct=0
    for c in palette.colors:
        ct+=1
        r,v,b=c.color_value
        for x in range(sizex):
            for y in range(sizey):
                if x>=((ct-1)*sqsize) and x<=(ct*sqsize):
                    pixels[(y * (sizex)) + x] = [r, v, b, 1.0]
    # flatten list
    pixels = [chan for px in pixels for chan in px]

    # assign pixels
    image.pixels = pixels
    
    return image