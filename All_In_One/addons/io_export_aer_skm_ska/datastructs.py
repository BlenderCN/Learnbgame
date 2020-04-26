# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


# ============================================================================ #
#
# NOTE:
#   + the Material file (MATFile) is linked to the SKMFile and save along with it.
#     It can be confusing at first and may change in a future version.
#
# TODO :
#   + Put structure version in header
#
# ============================================================================ #


from struct import pack, calcsize

# ================================================= #
# Exported file representation
# ================================================= #

# ------------------------------
# SKeletal Mesh file
# ------------------------------
class SKMFile(object):
  Extension = ".skm"

  def __init__(self):
    self.Header           = ChunkHeader("SKMHEADER", 0)
    self.Points           = Chunk("PNTS0000", TPoint.mDataSize)
    self.Vertices         = Chunk("VERT0000", TVertex.mDataSize)
    self.Faces            = Chunk("FACE0000", TFace.mDataSize)
    self.VertexMaterials  = Chunk("VMAT0000", TVertexMaterial.mDataSize) # to remove
    self.FaceMaterials    = Chunk("FMAT0000", TFaceMaterial.mDataSize)
    self.BoneWeights      = Chunk("BWGT0000", TBoneWeight.mDataSize)
    self.ShapeKeyInfos    = Chunk("SKEYINFO", TShapeKeyInfo.mDataSize)
    self.ShapeKeyDatas    = Chunk("SKEYDATA", TShapeKeyData.mDataSize)
    self.SKAInfo          = Chunk("SKAINFO0", TSKAInfo.mDataSize)
    #self.VertexGroups

    # Material file associated with the SKM file
    self._matFile = MATFile()


  def AddPoint(self, o):
    self.Points.add(o)

  def AddVertex(self, o):
    self.Vertices.add(o)

  def AddFace(self, o):
    self.Faces.add(o)

  def AddVertexMaterial(self, o):
    self.VertexMaterials.add(o)

  def AddFaceMaterial(self, o):
    self.FaceMaterials.add(o)

  def AddBoneWeight(self, o):
    self.BoneWeights.add(o)

  def AddShapeKeyInfo(self, o):
    self.ShapeKeyInfos.add(o)

  def AddShapeKeyData(self, o):
    self.ShapeKeyDatas.add(o)

  # XXX Could be confuse with with AddFaceMaterial
  def AddMaterial(self, o):
    self.AddFaceMaterial(TFaceMaterial(o.name) )#
    self._matFile.AddMaterial(o)

  # NOTE : no sense to have more than one
  def AddSKAInfo(self, o):
    self.SKAInfo.add(o)


  def dump(self):
    return self.Header.dump()       + self.Points.dump()          + self.Vertices.dump()      +\
           self.Faces.dump()        + self.VertexMaterials.dump() + self.FaceMaterials.dump() +\
           self.BoneWeights.dump()  + self.ShapeKeyInfos.dump()   + self.ShapeKeyDatas.dump() +\
           self.SKAInfo.dump()

  def save(self, filepath):
    filename = filepath + SKMFile.Extension
    fd = open(filename, "wb") 
    fd.write(self.dump() )
    fd.close()

    if self._matFile.HasMaterials():
      self._matFile.save(filepath)


# ------------------------------
# MATerial file
# ------------------------------
class MATFile(object):
  Extension = ".mat"

  def __init__(self):
    self.materials = []

  def AddMaterial(self, o):
    self.materials.append(o)

  def HasMaterials(self):
    return len(self.materials) > 0

  def dump(self):
    out = ""
    for m in self.materials:
      sub = m.name + "\n"
      for key in m.params:
        img_name = m.params[key]
        if img_name != "":
          sub += "%s %s\n" % (key, img_name)
      if len(m.params) < 1:
        sub += "null\n"
      out += sub + "\n"
    return out

  def save(self, filepath):
    filename = filepath + MATFile.Extension
    fd = open(filename, "w")
    fd.write(self.dump())
    fd.close()


# ------------------------------
# SKeletal Animation file
# ------------------------------
class SKAFile(object):
  Extension = ".ska"

  def __init__(self):
    self.Header    = ChunkHeader("SKAHEADER", 0)
    self.Bones     = Chunk("BONE0000", TBone.mDataSize)
    self.Sequences = Chunk("SEQU0000", TSequence.mDataSize)
    self.Frames    = Chunk("FRAM0000", TFrame.mDataSize)
    

  def AddBone(self, o):
    self.Bones.add(o)

  def AddSequence(self, o):
    self.Sequences.add(o)

  def AddFrame(self, o):
    self.Frames.add(o)

  def GetNumBones(self):
    return self.Bones.Header.dataCount

  def GetNumSequences(self):
    return self.Sequences.Header.dataCount

  def GetNumFrames(self):
    return self.Frames.Header.dataCount

  def dump(self):
    return self.Header.dump() + self.Bones.dump() + self.Sequences.dump() +\
           self.Frames.dump()

  def save(self, filepath):
    filename = filepath + SKAFile.Extension
    fd = open(filename, "wb") 
    fd.write(self.dump())
    fd.close()



# ================================================= #
# Chunk Info
# ================================================= #

class ChunkHeader(object):
  mFormat   = "20sIII"
  mDataSize = calcsize(mFormat) # ! error prone

  def __init__(self, chunkId, dataSize, tag=0):
    self.id         = str.encode(chunkId)
    self.dataSize   = dataSize
    self.dataCount  = 0
    self.tag        = tag

  def dump(self):
    print( "%s | dataSize: %d | dataCount: %d" % (self.id, self.dataSize, self.dataCount) )
    return pack(self.mFormat, self.id, self.dataSize, self.dataCount, self.tag)


class Chunk(object):
  def __init__(self, chunkId, dataSize):
    self.Header = ChunkHeader(chunkId, dataSize)
    self.Data = list() # use a list or a set ?

  def add(self, value):
    self.Data.append(value)
    self.Header.dataCount = len(self.Data)

  def dump(self):
    if self.Header.dataCount == 0:
      # Blender"s python version can"t natively concat str with bytes objects
      return b""

    dumped = self.Header.dump()
    for data in self.Data:
      dumped += data.dump()
    return dumped



# ================================================= #
# Algebraic objects
# (alternatively, use blender.mathutils)
# ================================================= #

class TVector(object):
  mFormat   = "fff"
  mDataSize = calcsize(mFormat)

  def __init__(self, X=0.0, Y=0.0, Z=0.0):
    self.x = X
    self.y = Y
    self.z = Z

  def dot(self, obj):
    return self.x * obj.x + self.y * obj.y + self.z * obj.z

  def cross(self, obj):
    return TVector(self.x*obj.y - self.y*obj.x,\
                    self.y*obj.z - self.z*obj.y,\
                    self.z*obj.x - self.x*obj.z )

  def dump(self):
    return pack(self.mFormat, self.x, self.y, self.z)

  def _key(self):
    return (self.__class__.__name__, self.x, self.y, self.z)

  def __hash__(self):
    return hash(self._key())

  def __eq__(self, obj):
    if not hasattr(obj, "_key"):
      return False
    return self._key() == obj._key()

  def __cmp__(self, obj):
    return cmp(self.x, obj.x) or\
           cmp(self.x, obj.y) or\
           cmp(self.x, obj.z)

  def __sub__(self, obj):
    return TVector(self.x - obj.x, self.y - obj.y, self.z - z)

  def __str__(self):
    return "TVector( %f, %f, %f)" % (self.x, self.y, self.z)


class TQuaternion(object):
  mFormat   = "ffff"
  mDataSize = calcsize(mFormat)

  def __init__(self, W=1.0, X=0.0, Y=0.0, Z=0.0):
    self.w = W
    self.x = X
    self.y = Y
    self.z = Z

  def dump(self):
    return pack(self.mFormat, self.w, self.x, self.y, self.z)

  def _key(self):
    return (self.__class__.__name__, self.w, self.x, self.y, self.z)

  def __hash__(self):
    return hash(self._key())

  def __eq__(self, obj):
    if not hasattr(obj, "_key"):
      return False
    return self._key() == obj._key()

  def __cmp__(self, obj):
    return cmp(self.w, obj.w) or\
           cmp(self.x, obj.x) or\
           cmp(self.x, obj.y) or\
           cmp(self.x, obj.z)

  def __str__(self):
    return "TQuaternion( %f, %f, %f, %f)" % ( self.w, self.x, self.y, self.z)



# ================================================= #
# Type of datas to store
# ================================================= #

class TPoint():
  mFormat   = TVector.mFormat
  mDataSize = TVector.mDataSize

  def __init__(self, X=0.0, Y=0.0, Z=0.0):
    self.point = TVector(X, Y, Z)

  def dump(self):
    return self.point.dump()

  def _key(self):
    return (self.__class__.__name__, self.point)

  def __hash__(self):
    return hash(self._key())

  def __eq__(self, obj):
    if not hasattr(obj, "_key"):
      return False
    return self._key() == obj._key()

  def __cmp__(self, obj):
    return cmp(self.point, obj.point)


class TVertex():
  mFormat   = "IffHH"
  mDataSize = calcsize(mFormat)

  def __init__(self):
    self.pointId        = 0
    self.u              = 0.0
    self.v              = 0.0
    self.auxTexCoordId  = 0
    self.materialId     = 0

  def dump(self):
    return pack(self.mFormat,\
           self.pointId, self.u, self.v, self.auxTexCoordId, self.materialId)

  def _key(self):
    return (self.__class__.__name__, self.pointId, self.u, self.v, self.auxTexCoordId,\
            self.materialId)

  def __hash__(self):
    return hash(self._key())

  def __eq__(self, obj):
    if not hasattr(obj, "_key"):
      return False
    return self._key() == obj._key()

  def __str__(self):
    return "pointId(%d) texCoord( %f, %f) auxTexCoordId(%d) materialId(%d)" %\
            (self.pointId, self.u, self.v, self.auxTexCoordId, self.materialId)



class TFace():
  mFormat   = "IIIhH"
  mDataSize = calcsize(mFormat)

  def __init__(self):
    self.v0         = 0
    self.v1         = 0
    self.v2         = 0
    self.materialId = -1    # default to no material (do better)
    self.padding    = 0

  def dump(self):
    return pack(self.mFormat, self.v0, self.v1, self.v2, self.materialId, self.padding)


# to remove (unused)
class TVertexMaterial():
  mFormat   = "IfffHH"
  mDataSize = calcsize(mFormat)

  def __init__(self):
    self.vertexId             = 0
    self.value                = TVector()
    self.materialType         = 0
    self.auxVertexMaterialId  = 0

  def dump(self):
    return pack(self.mFormat, self.vertexId, self.value.x, self.value.y, self.value.z,\
                self.materialType, self.auxVertexMaterialId)


# to modify
class TFaceMaterial():
  mFormat   = "64sII"
  mDataSize = calcsize(mFormat)

  def __init__(self, texturePath="", materialType=0, auxFaceMaterialId=0):
    self.texturePath        = texturePath         #material name
    self.materialType       = materialType        #unused
    self.auxFaceMaterialId  = auxFaceMaterialId   #unused

  def dump(self):
    bPath = bytes(self.texturePath, encoding="ascii")
    return pack(self.mFormat, bPath, self.materialType, self.auxFaceMaterialId)


class TSKAInfo():
  mFormat   = "32s"
  mDataSize = calcsize(mFormat)

  def __init__(self, basename):
    if len(basename) > 32:
      print("TSKAInfo basename too long [max size : 32 bytes]")
    self.basename = basename

  def dump(self):
    bBasename = bytes(self.basename, encoding="ascii")
    return pack(self.mFormat, bBasename)


class TBoneWeight():
  mFormat   = "IIf"
  mDataSize = calcsize(mFormat)

  def __init__(self, boneId=0, pointId=0, weight=0.0):
    self.boneId   = boneId
    self.pointId  = pointId
    self.weight   = weight

  def dump(self):
    return pack(self.mFormat, self.boneId, self.pointId, self.weight)


class TShapeKeyInfo():
  mFormat   = "32sII"
  mDataSize = calcsize(mFormat)

  def __init__(self, name="", start=0, count=0):
    self.name  = name
    self.start = start
    self.count = count

  def dump(self):
    bName = bytes(self.name, encoding="ascii")
    return pack(self.mFormat, bName, self.start, self.count)


class TShapeKeyData():
  mFormat   = "Ifff"
  mDataSize = calcsize(mFormat)

  def __init__(self, pointId=0, X=0.0, Y=0.0, Z=0.0):
    self.pointId = pointId
    self.X = X
    self.Y = Y
    self.Z = Z

  def dump(self):
    return pack(self.mFormat, self.pointId, self.X, self.Y, self.Z)


# --------------------------------
# Used by SKAFile
# --------------------------------

# Used by TBone
class TJoint():
  mFormat   = "f"  # ! not the complete data format
  mDataSize = TQuaternion.mDataSize + TVector.mDataSize + calcsize(mFormat)

  def __init__(self):
    self.qRotation  = TQuaternion()
    self.vTranslate = TVector()
    self.fScale     = 1.0

  def dump(self):
    return self.qRotation.dump() + self.vTranslate.dump() + \
           pack(self.mFormat, self.fScale)

class TBone():
  mFormat   = "32si" # ! not the complete data format
  mDataSize = calcsize(mFormat) + TJoint.mDataSize

  def __init__(self):
    self.name       = ""
    self.parentId   = 0         # could be negative (root"s parent)
    self.boneJoint  = TJoint()

  def dump(self):
    return pack(self.mFormat, bytes(self.name, encoding="ascii"), self.parentId) +\
           self.boneJoint.dump()

class TSequence():
  mFormat   = "32sIIfI"
  mDataSize = calcsize(mFormat)

  def __init__(self, name="", startFrame=0, numFrame=0, animRate=0.0, flag=0):
    self.name       = name
    self.startFrame = startFrame
    self.numFrame   = numFrame
    self.animRate   = animRate
    self.flag       = flag

  def dump(self):
    bName = bytes(self.name, encoding="ascii")
    return pack(self.mFormat, bName, self.startFrame, self.numFrame, \
                               self.animRate, self.flag)


class TFrame():
  mFormat   = "f" # ! not the complete data format
  mDataSize = TQuaternion.mDataSize + TVector.mDataSize + calcsize(mFormat)

  def __init__(self, qR=TQuaternion(), vT=TVector(), fS=1.0):
    self.qRotation  = qR
    self.vTranslate = vT
    self.fScale     = fS
    #self.time       = time

  def dump(self):
    return self.qRotation.dump() + self.vTranslate.dump() +\
           pack(self.mFormat, self.fScale)


# --------------------------------
# Used by MATFile
# --------------------------------
class TMaterial():
  # Type of texture allowed [texture name must be prefixed by this]
  TextureKeys = ["Kd", "Ks", "Bump"]

  def __init__(self, Bmat):
    self.name   = Bmat.name
    self.params = {}

    texGenerator = (ts for ts in Bmat.texture_slots if ts != None)
    for ts in texGenerator:
      tex = ts.texture
      if tex.type != "IMAGE":
        continue

      if ts.use_map_color_diffuse:
        key = self.TextureKeys[0]
      elif ts.use_map_color_spec:
        key = self.TextureKeys[1]      
      # default slot
      elif ts.use_map_normal:
        key = self.TextureKeys[2]
      else:
        print("Texture \"%s\" not handled." % (tex.image.name))
        continue

      self.params[key] = tex.image.name

  def __hash__(self):
    if len(self.params) == 0:
      return 0

    hashed_items = [hash(t) for t in self.params.items()]
    while len(hashed_items)>1:
      hashed_items[0] = hash( (hashed_items[0], hashed_items.pop()) )

    return hashed_items[0]

  def __eq__(self, obj):
    return self.params == obj.params




# ================================================= #
# MAIN (for debug)
# ================================================= #

def main():
  pass

if __name__ == "__main__":
  main()