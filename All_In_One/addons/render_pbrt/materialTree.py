import bpy

def materialDependencies(matName):
    if matName not in bpy.data.materials:
        return []

    matObj = bpy.data.materials[matName]

    matType = matObj.iileMaterial

    if matType == "MIX":
        return [
            matObj.iileMatMixSlot1Val,
            matObj.iileMatMixSlot2Val
        ]
    else:
        return []

def _resolveMaterialDependencies(acc, seen, currMaterial):
    if currMaterial in seen:
        return
    
    # Add the dependencies of the current material
    dependencies = materialDependencies(currMaterial)
    for i in range(len(dependencies)):
        aDep = dependencies[i]
        _resolveMaterialDependencies(acc, seen, aDep)

    # Add current material
    acc.append(currMaterial)

    # Add to seen
    seen[currMaterial] = True

def buildMaterialsDependencies():
    materialsList = list(bpy.data.materials.keys())

    acc = []
    seen = {}
    for i in range(len(materialsList)):
        aMatName = materialsList[i]
        _resolveMaterialDependencies(acc, seen, aMatName)
    
    print("Resolved materials order is {}".format(acc))
    return acc