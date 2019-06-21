bl_info = {
  "name": "Export Urchin Engine (.urchinMesh, .urchinAnim)",
  "version": (1, 0, 0),
  "blender": (2, 6, 6),
  "api": 31847,
  "location": "File > Export",
  "description": "Export Urchin Engine (.urchinMesh, .urchinAnim)",
  "category": "Learnbgame",
}

import bpy, struct, math, os, time, sys, mathutils, enum
from enum import Enum

# ---------------------------------------------------------------------------
# MATH UTILS
# ---------------------------------------------------------------------------
def vectorCrossProduct(v1, v2):
  return [
    v1[1] * v2[2] - v1[2] * v2[1],
    v1[2] * v2[0] - v1[0] * v2[2],
    v1[0] * v2[1] - v1[1] * v2[0],
    ]

def pointByMatrix(p, m):
  return [p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0] + m[3][0],
          p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1] + m[3][1],
          p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2] + m[3][2]]

def vectorByMatrix(p, m):
  return [p[0] * m.col[0][0] + p[1] * m.col[1][0] + p[2] * m.col[2][0],
          p[0] * m.col[0][1] + p[1] * m.col[1][1] + p[2] * m.col[2][1],
          p[0] * m.col[0][2] + p[1] * m.col[1][2] + p[2] * m.col[2][2]]

def vectorNormalize(v):
  l = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
  try:
    return v[0] / l, v[1] / l, v[2] / l
  except:
    return 1, 0, 0

def matrixInvert(m):
  det = (m.col[0][0] * (m.col[1][1] * m.col[2][2] - m.col[2][1] * m.col[1][2])
         - m.col[1][0] * (m.col[0][1] * m.col[2][2] - m.col[2][1] * m.col[0][2])
         + m.col[2][0] * (m.col[0][1] * m.col[1][2] - m.col[1][1] * m.col[0][2]))
  if det == 0.0: return None
  det = 1.0 / det

  r = [ [
    det * (m.col[1][1] * m.col[2][2] - m.col[2][1] * m.col[1][2]),
    - det * (m.col[0][1] * m.col[2][2] - m.col[2][1] * m.col[0][2]),
    det * (m.col[0][1] * m.col[1][2] - m.col[1][1] * m.col[0][2]),
    0.0,
    ], [
    - det * (m.col[1][0] * m.col[2][2] - m.col[2][0] * m.col[1][2]),
    det * (m.col[0][0] * m.col[2][2] - m.col[2][0] * m.col[0][2]),
    - det * (m.col[0][0] * m.col[1][2] - m.col[1][0] * m.col[0][2]),
    0.0
  ], [
    det * (m.col[1][0] * m.col[2][1] - m.col[2][0] * m.col[1][1]),
    - det * (m.col[0][0] * m.col[2][1] - m.col[2][0] * m.col[0][1]),
    det * (m.col[0][0] * m.col[1][1] - m.col[1][0] * m.col[0][1]),
    0.0,
    ] ]
  r.append([
    - (m.col[3][0] * r[0][0] + m.col[3][1] * r[1][0] + m.col[3][2] * r[2][0]),
    - (m.col[3][0] * r[0][1] + m.col[3][1] * r[1][1] + m.col[3][2] * r[2][1]),
    - (m.col[3][0] * r[0][2] + m.col[3][1] * r[1][2] + m.col[3][2] * r[2][2]),
    1.0,
  ])
  return r


# ---------------------------------------------------------------------------
# MESH DATA OBJECTS
# ---------------------------------------------------------------------------
class Material:
  name = ""
  def __init__(self, materialFileName):
    self.name = materialFileName

  def toUrchinMesh(self):
    return self.name;


class Mesh:
  name = ""
  subMeshes = []
  nextSubMeshId = 0

  def __init__(self, name):
    self.name = name
    self.subMeshes = []
    self.nextSubMeshId = 0

  def toUrchinMesh(self):
    meshNumber = 0
    buf = ""
    for subMesh in self.subMeshes:
      buf = buf + "mesh {\n"
      meshNumber += 1
      buf = buf + subMesh.toUrchinMesh()
      buf = buf + "}\n\n"

    return buf


class SubMesh:
  def __init__(self, mesh, material):
    self.material = material
    self.vertices = []
    self.faces = []
    self.weights = []

    self.nextVertexId = 0
    self.nextLinkedVerticesGroupId = 0
    self.nextWeightId = 0

    self.mesh = mesh
    self.name = mesh.name
    self.id = mesh.nextSubMeshId
    mesh.nextSubMeshId += 1
    mesh.subMeshes.append(self)

  def bindToMesh (self, mesh):
    self.mesh.subMeshes.remove(self)
    self.mesh = mesh
    self.id = mesh.nextSubMeshId
    mesh.nextSubMeshId += 1
    mesh.subMeshes.append(self)

  def generateWeights(self):
    self.weights = []
    self.nextWeightId = 0
    for vert in self.vertices:
      vert.generateWeights()

  def reportDoubleFaces(self):
    for face in self.faces:
      for face2 in self.faces:
        if not face == face2:
          if (not face.vertex1 == face2.vertex1) and (not face.vertex1 == face2.vertex2) and (not face.vertex1 == face2.vertex3):
            return
          if (not face.vertex2 == face2.vertex1) and (not face.vertex2 == face2.vertex2) and (not face.vertex2 == face2.vertex3):
            return
          if (not face.vertex3 == face2.vertex1) and (not face.vertex3 == face2.vertex2) and (not face.vertex3 == face2.vertex3):
            return
          print('[WARNING] Double face: %s %s' % (face, face2))

  def toUrchinMesh(self):
    self.generateWeights()
    self.reportDoubleFaces()

    buf = "\tmaterial \"%s\"\n\n" % (self.material.toUrchinMesh())

    # vertices
    buf = buf + "\tnumVerts %i\n" % (len(self.vertices))
    vnumber = 0
    for vert in self.vertices:
      buf = buf + "\tvert %i %s\n" % (vnumber, vert.toUrchinMesh())
      vnumber += 1

    # faces
    buf = buf + "\n\tnumTris %i\n" % (len(self.faces))
    facenumber = 0
    for face in self.faces:
      buf = buf + "\ttri %i %s\n" % (facenumber, face.toUrchinMesh())
      facenumber += 1

    # weights
    buf = buf + "\n\tnumWeights %i\n" % (len(self.weights))
    weightnumber = 0
    for weight in self.weights:
      buf = buf + "\tweight %i %s\n" % (weightnumber, weight.toUrchinMesh())
      weightnumber += 1

    return buf

class CloneReason(Enum):
  NOT_CLONED = 1
  FLAT_FACE = 2
  DIFFERENT_TEXTURE_COORD = 3

class Vertex:
  def __init__(self, subMesh, coord, clonedFrom = None, cloneReason = CloneReason.NOT_CLONED):
    self.id = subMesh.nextVertexId
    self.coord = coord
    self.textureCoord = None
    self.weights = []
    self.weight = None
    self.firstWeightIndex = 0
    self.clones = []
    self.subMesh = subMesh
    self.clonedFrom = clonedFrom

    if self.clonedFrom != None:
      self.influences = clonedFrom.influences
      clonedFrom.clones.append(self)
    else:
      self.influences = []

    if cloneReason == CloneReason.DIFFERENT_TEXTURE_COORD:
      self.linkedVerticesGroupId = self.clonedFrom.linkedVerticesGroupId
    else:
      self.linkedVerticesGroupId = subMesh.nextLinkedVerticesGroupId
      subMesh.nextLinkedVerticesGroupId += 1

    subMesh.nextVertexId += 1
    subMesh.vertices.append(self)

  def generateWeights(self):
    self.firstWeightIndex = self.subMesh.nextWeightId
    for influence in self.influences:
      self.subMesh.nextWeightId += 1
      newWeight = Weight(influence.bone, influence.weight, self, self.coord[0], self.coord[1], self.coord[2])
      self.subMesh.weights.append(newWeight)
      self.weights.append(newWeight)

  def toUrchinMesh(self):
    buf = "%i " % (self.linkedVerticesGroupId)
    if self.textureCoord:
      buf = buf + self.textureCoord.toUrchinMesh()
    else:
      buf = buf + "( 0.0 0.0 )"
    buf = buf + " ( %i %i )" % (self.firstWeightIndex, len(self.influences))
    return buf


class TextureCoordinate:
  def __init__(self, u, v):
    self.u = u
    self.v = v

  def toUrchinMesh(self):
    buf = "( %f %f )" % (self.u, self.v)
    return buf


class Weight:
  def __init__(self, bone, weight, vertex, x, y, z):
    self.bone = bone
    self.weight = weight
    self.vertex = vertex
    invBoneMatrix = matrixInvert(self.bone.matrix)
    self.x, self.y, self.z = pointByMatrix ((x, y, z), invBoneMatrix)

  def toUrchinMesh(self):
    buf = "%i %f ( %f %f %f )" % (self.bone.id, self.weight, self.x * scale, self.y * scale, self.z * scale)
    return buf


class Influence:
  def __init__(self, bone, weight):
    self.bone = bone
    self.weight = weight


class Face:
  def __init__(self, subMesh, vertex1, vertex2, vertex3):
    self.vertex1 = vertex1
    self.vertex2 = vertex2
    self.vertex3 = vertex3

    self.subMesh = subMesh
    subMesh.faces.append(self)

  def toUrchinMesh(self):
    buf = "%i %i %i" % (self.vertex1.id, self.vertex3.id, self.vertex2.id)
    return buf


class Skeleton:
  def __init__(self):
    self.bones = []
    self.nextBoneId = 0

  def toUrchinMesh(self, numSubMeshes):
    buf = "numJoints %i\n" % (self.nextBoneId)
    buf = buf + "numMeshes %i\n\n" % (numSubMeshes)
    buf = buf + "joints {\n"
    for bone in self.bones:
      buf = buf + bone.toUrchinMesh()
    buf = buf + "}\n\n"
    return buf

bones = {}

class Bone:
  def __init__(self, skeleton, parent, name, mat):
    self.parent = parent
    self.name = name
    self.children = []

    self.matrix = mat
    if parent:
      parent.children.append(self)

    self.skeleton = skeleton
    self.id = skeleton.nextBoneId
    skeleton.nextBoneId += 1
    skeleton.bones.append(self)

    bones[name] = self

  def toUrchinMesh(self):
    buf = "\t\"%s\"\t" % (self.name)
    parentIndex = -1
    if self.parent:
      parentIndex = self.parent.id
    buf = buf + "%i " % (parentIndex)

    pos1, pos2, pos3 = self.matrix.col[3][0], self.matrix.col[3][1], self.matrix.col[3][2]
    buf = buf + "( %f %f %f ) " % (pos1 * scale, pos2 * scale, pos3 * scale)

    m = self.matrix
    bquat = self.matrix.to_quaternion()
    bquat.normalize()
    qx = bquat.x
    qy = bquat.y
    qz = bquat.z
    if bquat.w > 0:
      qx = -qx
      qy = -qy
      qz = -qz
    buf = buf + "( %f %f %f )" % (qx, qy, qz)
    buf = buf + "\n"
    return buf

# ---------------------------------------------------------------------------
# MESH ANIMATION DATA OBJECTS
# ---------------------------------------------------------------------------
class UrchinAnimation:
  def __init__(self, skeleton):
    self.frameData = []  # frameData[boneid] holds the data for each frame
    self.bounds = []
    self.baseFrame = []
    self.skeleton = skeleton
    self.boneFlags = []
    self.boneFrameDataIndex = []  # stores the frameDataIndex for each bone in the skeleton
    self.frameRate = 24
    self.numFrames = 0
    for b in self.skeleton.bones:
      self.frameData.append([])
      self.baseFrame.append([])
      self.boneFlags.append(0)
      self.boneFrameDataIndex.append(0)

  def toUrchinAnim(self):
    currentFrameDataIndex = 0
    for bone in self.skeleton.bones:
      if (len(self.frameData[bone.id]) > 0):
        if (len(self.frameData[bone.id]) > self.numFrames):
          self.numFrames = len(self.frameData[bone.id])

        (x, y, z), (qw, qx, qy, qz) = self.frameData[bone.id][0]
        self.baseFrame[bone.id] = (x * scale, y * scale, z * scale, qx, qy, qz)
        self.boneFrameDataIndex[bone.id] = currentFrameDataIndex
        self.boneFlags[bone.id] = 63
        currentFrameDataIndex += 6
        self.numAnimatedComponents = currentFrameDataIndex
      else:
        rot = bone.matrix.to_quaternion()
        rot.normalize()
        qx = rot.x
        qy = rot.y
        qz = rot.z
        if rot.w > 0:
          qx = -qx
          qy = -qy
          qz = -qz
        self.baseFrame.col[bone.id] = (bone.matrix.col[3][0] * scale, bone.matrix.col[3][1] * scale, bone.matrix.col[3][2] * scale, qx, qy, qz)

    buf = "numFrames %i\n" % (self.numFrames)
    buf = buf + "numJoints %i\n" % (len(self.skeleton.bones))
    buf = buf + "frameRate %i\n" % (self.frameRate)
    buf = buf + "numAnimatedComponents %i\n\n" % (self.numAnimatedComponents)
    buf = buf + "hierarchy {\n"

    for bone in self.skeleton.bones:
      parentIndex = -1
      flags = self.boneFlags[bone.id]
      frameDataIndex = self.boneFrameDataIndex[bone.id]
      if bone.parent:
        parentIndex = bone.parent.id
      buf = buf + "\t\"%s\"\t%i %i %i" % (bone.name, parentIndex, flags, frameDataIndex)
      if bone.parent:
        buf = buf + " " + bone.parent.name
      buf = buf + "\n"
    buf = buf + "}\n\n"

    buf = buf + "bounds {\n"
    for b in self.bounds:
      buf = buf + "\t( %f %f %f ) ( %f %f %f )\n" % (b)
    buf = buf + "}\n\n"

    buf = buf + "baseFrame {\n"
    for b in self.baseFrame:
      buf = buf + "\t( %f %f %f ) ( %f %f %f )\n" % (b)
    buf = buf + "}\n\n"

    for f in range(0, self.numFrames):
      buf = buf + "frame %i {\n" % (f)
      for b in self.skeleton.bones:
        if (len(self.frameData[b.id]) > 0):
          (x, y, z), (qw, qx, qy, qz) = self.frameData[b.id][f]
          if qw > 0:
            qx, qy, qz = -qx, -qy, -qz
          buf = buf + "\t%f %f %f %f %f %f\n" % (x * scale, y * scale, z * scale, qx, qy, qz)
      buf = buf + "}\n\n"

    return buf

  def addKeyForBone(self, boneId, time, loc, rot):
    self.frameData[boneId].append((loc, rot))
    return

# ---------------------------------------------------------------------------
# EXPORT MAIN
# ---------------------------------------------------------------------------
class urchinSettings:
  def __init__(self, savePath, exportMode, scale=1.0):
    self.savePath = savePath
    self.exportMode = exportMode
    self.scale = scale


def getMinMax(listOfPoints):
  if len(listOfPoints) == 0:
    return ([0, 0, 0], [0, 0, 0])
  min = [listOfPoints[0][0], listOfPoints[0][1], listOfPoints[0][2]]
  max = [listOfPoints[0][0], listOfPoints[0][1], listOfPoints[0][2]]
  for i in range(1, len(listOfPoints)):
    if len(listOfPoints[i]) == 3:
      if listOfPoints[i][0] > max[0]: max[0] = listOfPoints[i][0]
      if listOfPoints[i][1] > max[1]: max[1] = listOfPoints[i][1]
      if listOfPoints[i][2] > max[2]: max[2] = listOfPoints[i][2]
      if listOfPoints[i][0] < min[0]: min[0] = listOfPoints[i][0]
      if listOfPoints[i][1] < min[1]: min[1] = listOfPoints[i][1]
      if listOfPoints[i][2] < min[2]: min[2] = listOfPoints[i][2]
  return (min, max)


def generateBoundingBox(objects, urchinAnimation, frameRange):
  scene = bpy.context.scene
  context = scene.render
  for i in range(frameRange[0], frameRange[1] + 1):
    corners = []
    scene.frame_set(i)

    for obj in objects:
      data = obj.data
      if obj.type == 'MESH' and data.polygons:
        (lx, ly, lz) = obj.location
        bbox = obj.bound_box

        matrix = [[1.0, 0.0, 0.0, 0.0],
                  [0.0, 1.0, 0.0, 0.0],
                  [0.0, 1.0, 1.0, 0.0],
                  [0.0, 0.0, 0.0, 1.0],
                  ]
        for v in bbox:
          corners.append(pointByMatrix (v, matrix))
    (min, max) = getMinMax(corners)
    urchinAnimation.bounds.append((min[0] * scale, min[1] * scale, min[2] * scale, max[0] * scale, max[1] * scale, max[2] * scale))


def saveUrchin(settings):
  print("[INFO] Exporting selected objects...")
  bpy.ops.object.mode_set(mode='OBJECT')

  scale = settings.scale
  currArmature = 0

  skeleton = Skeleton()
  bpy.context.scene.frame_set(bpy.context.scene.frame_start)
  for obj in bpy.context.selected_objects:
    if obj.type == 'ARMATURE':
      currArmature = obj
      wMatrix = obj.matrix_world

      def treatBone(b, parent=None):
        print("[INFO] Processing bone: " + b.name)
        if parent and not b.parent.name == parent.name:
          return # only catch direct children

        mat = mathutils.Matrix(wMatrix) * mathutils.Matrix(b.matrix_local)
        bone = Bone(skeleton, parent, b.name, mat)

        if b.children:
          for child in b.children:
            treatBone(child, bone)

      print("[INFO] Processing armature: " + currArmature.name)
      for b in currArmature.data.bones:
        if not b.parent: # only treat root bones
          treatBone(b)

      break  # only pull one skeleton out

  #MESH EXPORT
  meshes = []
  for obj in bpy.context.selected_objects:
    if (obj.type == 'MESH') and (len(obj.data.vertices.values()) > 0):
      apply_modifiers = True
      modifiedMesh = obj.to_mesh(bpy.context.scene, apply_modifiers, 'PREVIEW') #Apply modifier (triangulation...)

      mesh = Mesh(modifiedMesh.name)
      modifiedMesh.update(calc_tessface=True)
      print("[INFO] Processing mesh: " + modifiedMesh.name)
      meshes.append(mesh)

      numTris = 0
      numWeights = 0
      for f in modifiedMesh.polygons:
        numTris += len(f.vertices) - 2
      for v in modifiedMesh.vertices:
        numWeights += len(v.groups)

      wMatrix = obj.matrix_world
      verts = modifiedMesh.vertices

      uv_textures = modifiedMesh.tessface_uv_textures
      faces = []
      for f in modifiedMesh.polygons:
        faces.append(f)

      createVertexA = 0 # normal vertex
      createVertexB = 0 # cloned because flat face
      createVertexC = 0 # cloned because different texture coord

      while faces:
        materialIndex = faces[0].material_index
        material = Material(modifiedMesh.materials[0].name)

        subMesh = SubMesh(mesh, material)
        vertices = {}
        for face in faces[:]:
          if len(face.vertices) < 3:
            faces.remove(face)
          elif face.vertices[0] == face.vertices[1]:
            faces.remove(face)
          elif face.vertices[0] == face.vertices[2]:
            faces.remove(face)
          elif face.vertices[1] == face.vertices[2]:
            faces.remove(face)
          elif face.material_index == materialIndex:
            faces.remove(face)

            if not face.use_smooth :
              p1 = verts[ face.vertices[0] ].co
              p2 = verts[ face.vertices[1] ].co
              p3 = verts[ face.vertices[2] ].co

            faceVertices = []
            for i in range(len(face.vertices)):
              vertex = False
              if face.vertices[i] in vertices:
                vertex = vertices[  face.vertices[i] ]

              if not vertex: # found unique vertex, add to list
                coord = pointByMatrix(verts[face.vertices[i]].co, wMatrix)

                vertex = Vertex(subMesh, coord)
                if face.use_smooth:  # smooth face can share vertex, not flat face
                  vertices[face.vertices[i]] = vertex
                createVertexA += 1

                influences = []
                for j in range(len(modifiedMesh.vertices[ face.vertices[i] ].groups)):
                  inf = [obj.vertex_groups[ modifiedMesh.vertices[ face.vertices[i] ].groups[j].group ].name, modifiedMesh.vertices[ face.vertices[i] ].groups[j].weight]
                  influences.append(inf)

                if not influences:
                  print("[ERROR] There is a vertex without bone attachment in mesh: " + mesh.name)
                sum = 0.0
                for bone_name, weight in influences:
                  sum += weight

                for bone_name, weight in influences:
                  if sum != 0:
                    try:
                      vertex.influences.append(Influence(bones[bone_name], weight / sum))
                    except:
                      continue
                  else: # we have a vertex that is probably not skinned. export anyway
                    try:
                      vertex.influences.append(Influence(bones[bone_name], weight))
                    except:
                      continue

              elif not face.use_smooth:
                vertex = Vertex(subMesh, vertex.coord, vertex, CloneReason.FLAT_FACE)
                createVertexB += 1

              hasFaceUV = len(uv_textures) > 0
              if hasFaceUV:
                uv = [uv_textures.active.data[face.index].uv[i][0], uv_textures.active.data[face.index].uv[i][1]]
                uv[1] = 1.0 - uv[1]
                if not vertex.textureCoord:
                  vertex.textureCoord = TextureCoordinate(*uv)
                elif (vertex.textureCoord.u != uv[0]) or (vertex.textureCoord.v != uv[1]):
                  for clone in vertex.clones:
                    if (clone.textureCoord.u == uv[0]) and (clone.textureCoord.v == uv[1]):
                      vertex = clone
                      break
                  else: # clone vertex because different texture coord
                    vertex = Vertex(subMesh, vertex.coord, vertex, CloneReason.DIFFERENT_TEXTURE_COORD)
                    vertex.textureCoord = TextureCoordinate(*uv)
                    createVertexC += 1

              faceVertices.append(vertex)

            for i in range(1, len(face.vertices) - 1): # split faces with more than 3 vertices
              Face(subMesh, faceVertices[0], faceVertices[i], faceVertices[i + 1])
          else:
            print("[ERROR] Found face with invalid material")
      print("[INFO] Created vertices: A " + str(createVertexA) + ", B " + str(createVertexB) + ", C " + str(createVertexC))
      bpy.data.meshes.remove(modifiedMesh)

  # ANIMATION EXPORT
  animations = {}

  armatureAction = currArmature.animation_data.action
  rangeStart = 0
  rangeEnd = 0
  if armatureAction:
    animation = animations[armatureAction.name] = UrchinAnimation(skeleton)

    bpy.context.scene.update()
    armature = bpy.context.active_object
    action = armature.animation_data.action

    frameMin, frameMax = action.frame_range
    print("[INFO] Frame start: " + str(frameMin))
    print("[INFO] Frame end: " + str(frameMax))
    rangeStart = int(frameMin)
    rangeEnd = int(frameMax)

    currentTime = rangeStart
    while currentTime <= rangeEnd:
      bpy.context.scene.frame_set(currentTime)
      time = (currentTime - 1.0) / 24.0
      pose = currArmature.pose

      for boneName in currArmature.data.bones.keys():
        poseBoneMat = mathutils.Matrix(pose.bones[boneName].matrix)

        try:
          bone = bones[boneName]
        except:
          print("[ERROR] Found a posebone animating a bone that is not part of the exported armature: " + boneName)
          continue
        if bone.parent:
          parentPoseMat = mathutils.Matrix(pose.bones[bone.parent.name].matrix)
          parentPoseMat.invert()
          poseBoneMat = parentPoseMat * poseBoneMat
        else:
          poseBoneMat = currArmature.matrix_world * poseBoneMat
        loc = [poseBoneMat.col[3][0],
               poseBoneMat.col[3][1],
               poseBoneMat.col[3][2],
               ]
        rot = poseBoneMat.to_quaternion()
        rot.normalize()
        rot = [rot.w, rot.x, rot.y, rot.z]

        animation.addKeyForBone(bone.id, time, loc, rot)
      currentTime += 1

  if(settings.exportMode == "mesh & anim" or settings.exportMode == "mesh only"):
    urchinMeshFilename = settings.savePath + ".urchinMesh"

    if len(meshes) > 1: #save all submeshes in the first mesh
      for mesh in range (1, len(meshes)):
        for subMesh in meshes[mesh].subMeshes:
          subMesh.bindToMesh(meshes[0])

    try:
      file = open(urchinMeshFilename, 'w')
    except IOError:
      print("[ERROR] IOError to write in: " + urchinMeshFilename)

    buffer = skeleton.toUrchinMesh(len(meshes[0].subMeshes))
    buffer = buffer + meshes[0].toUrchinMesh()
    file.write(buffer)
    file.close()
    print("[INFO] Saved mesh to " + urchinMeshFilename)

  if(settings.exportMode == "mesh & anim" or settings.exportMode == "anim only"):
    urchinAnimFilename = settings.savePath + ".urchinAnim"

    if len(animations) > 0:
      anim = animations.popitem()[1]
      try:
        file = open(urchinAnimFilename, 'w')
      except IOError:
        print("[ERROR] IOError to write in: " + urchinAnimFilename)
      objects = []
      for subMesh in meshes[0].subMeshes:
        if len(subMesh.weights) > 0:
          obj = None
          for sob in bpy.context.selected_objects:
            if sob and sob.type == 'MESH' and sob.name == subMesh.name:
              obj = sob
          objects.append (obj)
      generateBoundingBox(objects, anim, [rangeStart, rangeEnd])
      buffer = anim.toUrchinAnim()
      file.write(buffer)
      file.close()
      print("[INFO] Saved anim to " + urchinAnimFilename)
    else:
      print("[WARNING] No urchinAnim file generated.")

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
from bpy.props import *
class ExportUrchin(bpy.types.Operator):
  '''Export Urchin Engine (.urchinMesh .urchinAnim)'''
  bl_idname = "export.urchin"
  bl_label = 'Export Urchin Engine'

  exportModes = [("mesh & anim", "Mesh & Anim", "Export mesh and anim"),
                 ("anim only", "Anim only", "Export anim only"),
                 ("mesh only", "Mesh only", "Export mesh only")]

  filepath = StringProperty(subtype='FILE_PATH', name="File Path", description="File path for exporting", maxlen=1024, default="")
  exportMode = EnumProperty(name="Exports", items=exportModes, description="Choose export mode", default='mesh only')
  meshScale = FloatProperty(name="Scale", description="Scale all objects from world origin (0,0,0)", min=0.001, max=1000.0, default=1.0, precision=6)

  def execute(self, context):
    global scale
    scale = self.meshScale
    settings = urchinSettings(savePath=self.properties.filepath, exportMode=self.properties.exportMode)
    saveUrchin(settings)
    return {'FINISHED'}

  def invoke(self, context, event):
    WindowManager = context.window_manager
    WindowManager.fileselect_add(self)
    return {"RUNNING_MODAL"}

def menuFunc(self, context):
  defaultPath = os.path.splitext(bpy.data.filepath)[0]
  self.layout.operator(ExportUrchin.bl_idname, text="Urchin Engine (.urchinMesh .urchinAnim)", icon='BLENDER').filepath = defaultPath

def register():
  bpy.utils.register_module(__name__)
  bpy.types.INFO_MT_file_export.append(menuFunc)

def unregister():
  bpy.utils.unregister_module(__name__)
  bpy.types.INFO_MT_file_export.remove(menuFunc)

if __name__ == "__main__":
  register()
