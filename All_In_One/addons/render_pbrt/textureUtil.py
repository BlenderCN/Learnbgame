import bpy
import os
import shutil

globalTextureCounter = 0

def makeNewTextureName(extension):
    global globalTextureCounter
    globalTextureCounter += 1
    return "tex_{}{}".format(globalTextureCounter, extension)

def addTexture(texSource, outDir, block, texType="color"):
    texAbsPath = bpy.path.abspath(texSource)
    baseName = os.path.basename(texAbsPath)
    stem, ext = os.path.splitext(baseName)
    destName = makeNewTextureName(ext)
    destPath = os.path.join(outDir, destName)
    shutil.copyfile(texAbsPath, destPath)
    # Add the texture to the block
    textureLine = 'Texture "{}" "{}" "imagemap" "string filename" "{}"'.format(
        destName, texType, destName
    )
    block.addBeginning(0, textureLine)
    return destName

def copyTexture(texSource, outDir):
    texAbsPath = bpy.path.abspath(texSource)
    baseName = os.path.basename(texAbsPath)
    stem, ext = os.path.splitext(baseName)
    destName = makeNewTextureName(ext)
    destPath = os.path.join(outDir, destName)
    shutil.copyfile(texAbsPath, destPath)
    return destName

def resetTextureCounter():
    global globalTextureCounter
    globalTextureCounter = 0