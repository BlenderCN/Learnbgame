import bpy
import math
import random
from math import pi as PI
from .tect import Tectonics
from .srbf import *
from .shared import rsign

######################################################################

SRBFPrefs = {
    Plateau :   {"collision" : 1., "shear" : .2},
    Gaussian :  {"collision" : 1., "shear" : .4},
    DOG :       {"collision" : .5, "shear" : .8},
    Gabor :     {"collision" : .2, "shear" : 1.},
}

def evalPrefs(tectType):
    prefs = SRBFPrefs.copy()
    for srbf in prefs.keys():
        prefs[srbf] = sum( abs(tectType[key])*value for key, value in prefs[srbf].items() )

    norm = sum(prefs.values())
    for srbf in prefs.keys():
        prefs[srbf] /= norm
    
    return prefs

def randomFromPrefs(prefs):
    p = random.random()
    for srbf in prefs.keys():
        p -= prefs[srbf]
        if p <= 0:
            return srbf
    return random.choice(prefs.keys())

######################################################################

class SharedOperatorBase:
    bl_options = {"REGISTER", "UNDO"}

    numFeatures = bpy.props.IntProperty(
        name        = "Features",
        description = "Number of randomly placed features to generate",
        default     = 50,
        min         = 0
    )
    
    nPlates = bpy.props.IntProperty(
        name        = "Plates",
        description = "Number of tectonic plates",
        default     = 30,
        min         = 4, soft_min = 8
    )
    
    featureDensity = bpy.props.FloatProperty(
        name        = "Feature Density",
        description = "Density of features along tectonic borders; in 1/rad",
        default     = 40, step = 100,
        min         = 0,
        soft_max    = 100
    )
    
    spread = bpy.props.FloatProperty(
        name        = "Feature Spread",
        description = "Standard deviation of distance to tectonic border",
        precision   = 4,
        default     = .025,
        min         = 0,
        soft_max    = .1
    )
    
    widthRange = bpy.props.FloatVectorProperty(
        name        = "Min/Max Width",
        description = "Width of features along tectonic borders",
        size        = 2,
        default     = (100,1000), step = 100,
        min         = 1
    )
    
    heightRange = bpy.props.FloatVectorProperty(
        name        = "Min/Max Height",
        description = "Height of features along tectonic borders",
        size        = 2,
        default     = (50,100), step = 100,
        min         = 1
    )
    
    fillOceans = bpy.props.BoolProperty(
        name        = "Fill Oceans",
        description = "Deactivate to see the ocean floor",
        default     = True
    )
    
    expPlates = bpy.props.BoolProperty(
        name        = "Plate Mesh",
        description = "Show the mesh of the tectonic plates",
        default     = False
    )
    
    def execute(self, context):
        assert context.object.type == 'MESH', "Select a mesh to operate on!"
        
        tect = Tectonics(self.nPlates)
        
        hm = SRBFCollection()
        #for plate in tect.mesh.polygons:
        #    hm.add( Plateau(plate.center, math.sqrt(plate.area/PI), rsign(.01)) )
        
        for border in tect.bmesh.edges:
            vert1, vert2 = list( v.co for v in border.verts )
            center = (vert1 + vert2) / 2
            orthoTangent = center.cross(vert1-vert2).normalized()
            
            arcLength = vert1.angle( vert2 )
            count = round( arcLength*self.featureDensity + random.random() )

            type = tect.classifyEdge(border)
            activity = max( abs(type["collision"]), type["shear"] )
            p_positiveSign = (type["collision"]+1)/2
            p_positiveSign = p_positiveSign*p_positiveSign*(3-2*p_positiveSign) # smoothing
            prefs = evalPrefs(type)
            
            for _ in range(count):
                sign = +1 if random.random() < p_positiveSign else -1
                
                position = vert1.lerp( vert2, random.random() )
                position += random.gauss(0, self.spread*(1+activity))*orthoTangent # we don't want features in straight lines

                func = randomFromPrefs(prefs)
                width = (0.25 + activity) * random.uniform(*self.widthRange)*kmWide
                amplitude = sign * (0.25 + activity) * random.uniform(*self.heightRange)*kmHigh
                amplitude *= SharedOperatorBase.featureDensity[1]["default"]/self.featureDensity # normalise to default, as heights add up
                
                hm.add( func(position, width, amplitude) )
            
        for _ in range(self.numFeatures):
            hm.add( randomSRBF() )
        
        self.processHeightmap(context, hm, tect)
        
        if self.expPlates:
            tect.linkMeshToScene(context)
        tect.bmesh.free()
        
        return {'FINISHED'}
    
    def processHeightmap(self, context, srbfs, tectonics):
        raise NotImplementedError("Implement in subclass!")
