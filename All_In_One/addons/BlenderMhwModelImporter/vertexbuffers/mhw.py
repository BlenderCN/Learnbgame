from ..dbg import dbg
from ..common import fileOperations as fileOp
from ..common import constants as cons

def proxima(value1,value2=0,epsilon=0.0001):
    return (value1 <= (value2+epsilon)) and (value1 >= (value2-epsilon))

def MODVertexBufferSelector(BlockType):
    MVBF = eval("MODVertexBuffer%08x"%BlockType)
    return MVBF

def calcBonesAndWeightsArr(cnt,weights,bones):
    #weightArrResult = []
    #boneArrResult = []
    #cwt = []
    #cbn = []
    #for b in range(0,cnt):
    #    if (weights[b]>0) and not proxima(weights[b]):
    #        try:
    #            fitem = cbn.index(bones[b])
    #        except:
    #            fitem = -1
    #        if fitem > -1:
    #            cwt[fitem] += weights[b]
    #        else:
    #            cbn.append(bones[b])
    #            cwt.append(weights[b])
    #return (cwt,cbn)
    return (weights,bones)

def calcBonesAndWeights(cnt,weightVal,weightVal2,bns):
    wt = []
    w1 = (weightVal & cons.BIT_LENGTH_10)*cons.WEIGHT_MULTIPLIER
    w2 = ((weightVal>>10) & cons.BIT_LENGTH_10)*cons.WEIGHT_MULTIPLIER
    w3 = ((weightVal>>20) & cons.BIT_LENGTH_10)*cons.WEIGHT_MULTIPLIER
    wt.append(w1)
    wt.append(w2)
    wt.append(w3)
    
    if cnt > 4:
        wt.append((weightVal2[0]) * cons.WEIGHT_MULTIPLIER2)
        wt.append((weightVal2[1]) * cons.WEIGHT_MULTIPLIER2)
        wt.append((weightVal2[2]) * cons.WEIGHT_MULTIPLIER2)
        wt.append((weightVal2[3]) * cons.WEIGHT_MULTIPLIER2)
        wt.append(1.0 - wt[0] - wt[1] - wt[2] - wt[3] - wt[4] - wt[5]- wt[6])
        if wt[7] < 0:
            wt[7] = 0
    else:
        w4 = 1.0 - w1 - w2 - w3
        wt.append(w4)    
    return calcBonesAndWeightsArr(cnt,wt,bns)

def basicAppendEmptyVertices(cls,fl,VertexRegionEnd,oldVertexCount,addVertexCount):
    dbg("basicAppendEmptyVertices %08x %d %d" % (VertexRegionEnd,oldVertexCount,addVertexCount))
    if(addVertexCount > 0):
        fileOp.InsertEmptyBytes(fl,VertexRegionEnd,cls.getStructSize()*addVertexCount)
    elif(addVertexCount < 0):
        subVertexCount = 0-addVertexCount
        fileOp.DeleteBytes(fl,VertexRegionEnd-subVertexCount*cls.getStructSize(),cls.getStructSize()*subVertexCount)

class MODVertexBuffer():
    def __init__(self, headerref, vertexcount):
        dbg("%s %d" % (self.__class__.__name__, vertexcount))
        self.vertarray   = []
        self.uvs         = []
        self.weights     = []
        self.bones       = []
        self.normalarray = []
        self.headerref   = headerref
        self.vertexcount = vertexcount
        self.readOp = fileOp.ReadBEFloat if headerref.bendian else fileOp.ReadFloat
    @staticmethod
    def getUVOFFAfterTangents():
        return 0
    @classmethod
    def appendEmptyVertices(cls,fl,VertexRegionEnd,oldVertexCount,addVertexCount):
        basicAppendEmptyVertices(cls,fl,VertexRegionEnd,oldVertexCount,addVertexCount)
    def readVertexAndNormals(self, headerref):
        self.vertarray.append([self.readOp(headerref.fl),self.readOp(headerref.fl),self.readOp(headerref.fl)])
        self.normalarray.append((fileOp.Read8s(headerref.fl),fileOp.Read8s(headerref.fl),fileOp.Read8s(headerref.fl)))
        fileOp.ReadByte(headerref.fl)
        fileOp.ReadLong(headerref.fl)
        
#IANonSkin1UVColor
class MODVertexBuffer818904dc(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__(headerref,vertexcount)
        for i in range(0,vertexcount):
            self.vertarray.append([self.readOp(headerref.fl),self.readOp(headerref.fl),self.readOp(headerref.fl)])
            self.normalarray.append((fileOp.Read8s(headerref.fl),fileOp.Read8s(headerref.fl),fileOp.Read8s(headerref.fl)))
            fileOp.ReadByte(headerref.fl)
            fileOp.ReadLong(headerref.fl)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            fileOp.ReadLong(headerref.fl)
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+4
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return -1
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return -1


#IANonSkin2UVColor
class MODVertexBuffer0f06033f(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__(headerref,vertexcount)
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            wts = fileOp.ReadLong(headerref.fl)
            bns = [fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl)]
            [weights,bones] = calcBonesAndWeights(4,wts,[],bns)
            self.weights.append(weights)
            self.bones.append(bones)
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+4+1+ 1+1+1
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return 0
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return 0
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS3_BONES4

#IASkin8wt1UV
class MODVertexBuffer81f58067(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__(headerref,vertexcount)
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            wts = fileOp.ReadLong(headerref.fl)
            wts2 = [fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl)]            
            bns = [fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),
                fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl)]
            [weights,bones] = calcBonesAndWeights(8,wts,wts2,bns)
            self.weights.append(weights)
            self.bones.append(bones)

    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+4+1+1+1+1+1 +1+1+1+1+1+1+1
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return 0
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return 0
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS7_BONES8

#IASkin4wt2UV
class MODVertexBufferf471fe45(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__(headerref,vertexcount)
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            self.uvs2.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            wts = fileOp.ReadLong(headerref.fl)
            bns = [fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl)]
            [weights,bones] = calcBonesAndWeights(4,wts,[],bns)
            self.weights.append(weights)
            self.bones.append(bones)
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+2+2+4+1+1+1+1
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return 0
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return 0
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS3_BONES4

#IASkin4wt1UVColor
class MODVertexBuffer3c730760(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__()
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            wts = fileOp.ReadLong(headerref.fl)
            bns = [fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl)]
            [weights,bones] = calcBonesAndWeights(4,wts,[],bns)
            self.weights.append(weights)
            self.bones.append(bones)
            for _ in range(4):
                fileOp.ReadByte(headerref.fl)
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+4+1+1+1+1+1+1+1+1
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return 0
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return 0      
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS3_BONES4

#IASkin4wt2UVColor
class MODVertexBufferb2fc0083(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__()
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            fileOp.ReadLong(headerref.fl)
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+4
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return -1
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return -1
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS0_BONES0

#IASkin8wt1UVColor
class MODVertexBuffer366995a7(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__()
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            wts = fileOp.ReadLong(headerref.fl)
            wts2 = [fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl)]            
            bns = [fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),
                fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl)]
            [weights,bones] = calcBonesAndWeights(8,wts,wts2,bns)
            self.weights.append(weights)
            self.bones.append(bones)
            fileOp.ReadLong(headerref.fl)
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+4+1+1+1+1 + 8+4
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return 0
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return 0
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS7_BONES8

#FIXME, not referenced by ShaderPackage.sdf, does this even exist?
class MODVertexBufferc9690ab8(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__()
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            for _ in range(4):
                fileOp.ReadHalfFloat(headerref.fl)
            for _ in range(12):
                fileOp.ReadByte(headerref.fl)
            
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+2+2+1+1+1+1 +1+1+1+1+1+1+1+1
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return -1
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return -1
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS7_BONES8

#FIXME, not referenced by ShaderPackage.sdf, does this even exist?
class MODVertexBuffer5e7f202d(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__()
        raise Exception("ToDo")
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            fileOp.ReadLong(headerref.fl)
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+4
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return -1
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return -1
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS0_BONES0

#FIXME, not referenced by ShaderPackage.sdf, does this even exist?
class MODVertexBufferd829702c(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__()
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return -1
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return -1
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS0_BONES0  

#IASkin8wt2UVColor
class MODVertexBufferb8e69244(MODVertexBuffer):
    def __init__(self,headerref,vertexcount):
        super().__init__()
        for i in range(0,vertexcount):
            self.readVertexAndNormals(headerref)
            self.uvs.append((fileOp.ReadHalfFloat(headerref.fl),1-fileOp.ReadHalfFloat(headerref.fl)))
            wts = fileOp.ReadLong(headerref.fl)
            wts2 = [fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl)]            
            bns = [fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),
                fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl),fileOp.ReadByte(headerref.fl)]
            [weights,bones] = calcBonesAndWeights(8,wts,wts2,bns)
            self.weights.append(weights)
            self.bones.append(bones)
            fileOp.ReadLong(headerref.fl)
            for _ in range(4):
                fileOp.ReadByte(headerref.fl)
            
    @staticmethod
    def getStructSize():
        return 4+4+4+1+1+1+1+4+2+2+4+1+1+1+1+1*8+4 +1+1+1+1
    @staticmethod
    def getWeightsOFFAfterUVOFF():
        return 0
    @staticmethod
    def getBonesOFFAfterWeightsOFF():
        return 0
    @staticmethod
    def getBoneMode():
        return cons.WEIGHTS7_BONES8

#FIXME IANonSkin2UV    != NonExisting
MODVertexBuffera5104ca0 = MODVertexBuffer5e7f202d

#FIXME IASkin4wt1UV    != IANonSkin2UVColor
MODVertexBufferf637401c = MODVertexBuffer0f06033f

#FIXME IANonSkin1UV    != NonExisting
MODVertexBuffera756f2f9 = MODVertexBufferd829702c