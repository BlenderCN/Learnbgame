import bpy
def execute():
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    ag.buildSpeed = 1.0
    ag.velocity = 3.0
    ag.xLocOffset = 0.0
    ag.yLocOffset = 0.0
    ag.zLocOffset = 0.0
    ag.locInterpolationMode = 'BEZIER'
    ag.locationRandom = 20.0
    ag.xRotOffset = 0.0
    ag.yRotOffset = 0.0
    ag.zRotOffset = 0.0
    ag.rotInterpolationMode = 'BEZIER'
    ag.rotationRandom = 20.0
    ag.xOrient = 0.0
    ag.yOrient = 0.0
    ag.orientRandom = 50.0
    ag.layerHeight = 0.1
    ag.buildType = 'ASSEMBLE'
    ag.invertBuild = 0
    ag.skipEmptySelections = False
    ag.useGlobal = False
    ag.meshOnly = False
    return None
