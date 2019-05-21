import bpy

import sceneParser
import textureUtil

def createEnvironmentBlock(world, outDir):
    block = sceneParser.SceneBlock([])
    block.appendLine(0, "AttributeBegin")

    color = world.iileEnvcolor
    magnitude = world.iileEnvMagnitude
    path = world.iileEnvmapPath
    rot = world.iileEnvmapRotation

    if color[0] <= 1e-5 and color[1] <= 1e-5 and color[2] <= 1e-5:
        return None
    
    if magnitude <= 1e-5:
        return None
    
    block.appendLine(1, 'Scale 1 1 -1')
    block.appendLine(1, 'Rotate {} 0 0 1'.format(rot))
    block.appendLine(1, 'LightSource "infinite"')
    block.appendLine(1, '"rgb L" [ {} {} {} ]'.format(color[0]*magnitude, color[1]*magnitude, color[2]*magnitude))

    if path != "":
        texName = textureUtil.copyTexture(path, outDir)
        block.appendLine(1, '"string mapname" "{}"'.format(texName))

    block.appendLine(1, '"integer samples" [4]')

    block.appendLine(0, "AttributeEnd")
    return block