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


bl_info = {
  'name': 'Export SKMA format',
  'description': '[wip] Export model, blendshape, skeleton and animation.',
  'author': 'Thibault Coppex <tcoppex@gmail.com>',
  'version': (1, 0),
  'blender': (2, 6, 4),
  'location': 'File > Export > Skeleton Model format (.skm)',
  "category": "Learnbgame",
}

'''
  + Note +

  This script is inspired by io_export_unreal_psk_psa.py, thanks to the 
  developpers.

  + TODO +
  * make it possible to merge SKM & SKA data in a special file
  * Create a new chunk in the SKM identifying the skeleton name
  * Create null material when no one exist ?
  * Sort vertices per face / material id
  * Improve face sorting from O(nlogn) to O(n) using bucket sort
  * Hash vertices with normals information (even when not exporting them) in order
    to have duplicate vertices when face normal doesnt matches.
  * Better material handling (new material format like Source's)
  * It could be tricky to compute normals for shape keys afterward. We may have to
    export them here.
  * Modifiers are not applied before export. Display an alert if some are present
  (non armatures)
'''


# ================================================= #
# LIBS
# ================================================= #

# Python libs
import os
import time
import sys

# Blender API
import mathutils
import operator
import bpy
from bpy.props import *

# Structures used to represents models data in the chunks
from datastructs import *


# ================================================= #
# Utils data
# ================================================= #

# Quaternion to transform from Blender to OpenGL space coordinate
# (Blender X, Y, Z is OpenGL X, Z, -Y so we rotate -90deg around x axis)
qBlenderToGL = mathutils.Quaternion( (0.707, -0.707, 0.0, 0.0))

python_epsilon = sys.float_info.epsilon


# ================================================= #
# Export utils classes
# ================================================= #

class ObjMap:  
  def __init__(self):
    self.dict = {}
    self.next = 0
  
  def get(self, obj):
    if obj in self.dict:
      return self.dict[obj]
    else:
      index = self.next
      self.next += 1
      self.dict[obj] = index
      return index
  
  def items(self):
    getval = operator.itemgetter(0)
    getkey = operator.itemgetter(1)
    return map(getval, sorted(self.dict.items(), key=getkey))



# -- BEGIN class ArmatureParser --
class ArmatureParser():
  __doc__ = '''
  '''

  def parse(self, skaFile, armature):
    # Search for root candidates
    Bones = armature.data.bones    
    root_candidates = [b for b in Bones if not b.parent]
    # root_candidates = [b for b in Bones if not b.parent and b.name[:4].lower() == 'root']
    
    # Only one node can be eligible
    if len(root_candidates) > 1:
      raise Exception( 'A single root must exist in the armature.')
    elif len(root_candidates) == 0:
      raise Exception( 'No root found.')
    
    # Get the root
    root = root_candidates[0]
    del root_candidates  
    
    # Root orientation & position
    rotMatrix = root.matrix * armature.matrix_local.to_3x3()
    qRotation = rotMatrix.to_quaternion()
    qRotation *= qBlenderToGL
    vPosition = armature.matrix_local * root.head
    vPosition = qBlenderToGL * vPosition

    #return the root id, which is 0
    root_id = self.addBone(skaFile,  root.name, -1, qRotation, vPosition)            #
      
    # recursively compute others bones data
    for child in root.children:
      self.recursively_add_bone(skaFile, child, root_id)


  def addBone(self, skaFile, name, parentId, qRot, vPos):
    bone = TBone()
    bone.name = name
    bone.parentId = parentId
    bone.boneJoint.qRotation  = TQuaternion(qRot.w, qRot.x, qRot.y, qRot.z)
    bone.boneJoint.vTranslate = TVector(vPos.x, vPos.y, vPos.z)
    skaFile.AddBone(bone)
    boneId = skaFile.GetNumBones()-1
    return boneId    


  def recursively_add_bone(self, skaFile, bone, parent_id):
    qRotation = bone.matrix.to_quaternion()

    qRotParent = bone.parent.matrix.to_quaternion().inverted()
    offsetParent = qRotParent * (bone.parent.tail - bone.parent.head)      
    vPosition = offsetParent + bone.head
    
    bone_id = self.addBone(skaFile,  bone.name, parent_id, qRotation, vPosition)     #
    
    for child in bone.children:
      self.recursively_add_bone(skaFile, child, bone_id)

# -- END class ArmatureParser --


# -- Begin class AnimationParser --
class AnimationParser():

  def parse(self, skaFile, armature):
    if armature.animation_data == None:
      print( "Error: no animations set for %s", armature.name)
      return
    
    Scene = bpy.context.scene
    
    # Push current anim info
    restore_action = armature.animation_data.action
    restore_frame  = Scene.frame_current
    
    for action in (a for a in bpy.data.actions if a.users > 0):
      self.export_action(skaFile, armature, action)
    
    # Pop anim info
    armature.animation_data.action = restore_action
    Scene.frame_set(restore_frame)


  def export_action(self, skaFile, armature, action):
    ''' Create every inter Keyframes sample and export them '''

    frameStart = int(action.frame_range.x)
    frameEnd   = int(action.frame_range.y)
    frameRange = range(frameStart, frameEnd + 1)
    frameCount = len(frameRange)
    
    Scene = bpy.context.scene

    # Export the sequence (aka action) properties
    frameOffset = skaFile.GetNumFrames()
    animRate = Scene.render.fps #
    sequence = TSequence(action.name, frameOffset, frameCount, animRate)
    skaFile.AddSequence(sequence)

    # Change current action
    armature.animation_data.action = action
    Scene.update()
    
    for frame in frameRange:

      # Update current frame
      Scene.frame_set(frame)

      # Export animation data for each bone
      # !! be sure bones are in the same order that skaFile !!
      for bone in armature.pose.bones:
        pose_matrix = bone.matrix
        # multiply by parent's bind matrix if not the Root
        if bone.parent != None:
          pose_matrix = bone.parent.matrix.inverted() * pose_matrix

        qRot = pose_matrix.to_quaternion().normalized() 
        head = pose_matrix.to_translation().xyz #

        # transform Root in OpenGL space
        if bone.parent == None:
          qRot = qBlenderToGL * qRot
          head = qBlenderToGL * head

        qR = TQuaternion(qRot.w, qRot.x, qRot.y, qRot.z)
        vT = TVector(head.x, head.y, head.z)
        skaFile.AddFrame(TFrame(qR, vT))

# -- End class AnimationParser --


# -- Begin class MeshParser --
class MeshParser():
  __doc__ = ''' '''


  @staticmethod
  def Triangulate(obj):
    Scene = bpy.context.scene
    
    triObj      = obj.copy()
    triObj.data = obj.to_mesh(Scene, apply_modifiers=False, settings='PREVIEW')
    Scene.objects.link(triObj)
    Scene.update()

    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Deselect all objects but the new one
    for o in Scene.objects:
      o.select = False
    triObj.select        = True
    Scene.objects.active = triObj
    
    # Triangulate the mesh in EDIT mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    Scene.update()  
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # needed to get access to tessfaces
    triObj.data = triObj.to_mesh(Scene, apply_modifiers=False, settings='PREVIEW')
    Scene.update()
    
    return triObj


  def parse(self, skmFile, mesh):
    # Saved to export shapekeys, not present in copied object.. [FIX THIS]
    AOname = bpy.context.active_object.name

    # Triangulate the mesh
    obj = self.Triangulate(mesh)
    
    if len(obj.data.uv_textures) > 0:
      bHasTexCoord   = True   
      obj_texCoords = obj.data.tessface_uv_textures.active
      #face_uv       = uv_layer.data[face_index]
    else:
      bHasTexCoord = False

    # Retrieve materials
    LUT_matId = self.parseMaterial(skmFile, obj.material_slots)

    pointsMap   = ObjMap()
    verticesMap = ObjMap()
    
    # LUT to retrieve vertex id from Blender to SKM
    blenderToSKM_vertexId = dict()

    for tface in obj.data.tessfaces:
      vertex_list = []

      # (Note: faces must be triangles)
      for i in range(3):
        blVertexId = tface.vertices[i]
        vert = obj.data.vertices[ blVertexId ]

        vPos = obj.matrix_local * vert.co
        vPos = qBlenderToGL * vPos

        texCoord = [0.0, 0.0]
        if bHasTexCoord:
          tface_tc = obj_texCoords.data[tface.index]
          texCoord = tface_tc.uv[i][:2]

        # Point to export
        point = TPoint(vPos.x, vPos.y, vPos.z)

        # Vertex to export
        vertex                = TVertex()
        vertex.pointId        = pointsMap.get(point)
        vertex.u              = texCoord[0]
        vertex.v              = texCoord[1]
        vertex.auxTexCoordId  = 0
        vertex.materialId     = 0             # unused
        
        # Put the vertex in the map & retrieve its index
        v_index = verticesMap.get(vertex)
        vertex_list.append(v_index)        
        blenderToSKM_vertexId[blVertexId] = v_index
      # -- END for range(3) --

      # Face to export
      face            = TFace()
      face.v0         = vertex_list[0]
      face.v1         = vertex_list[1]
      face.v2         = vertex_list[2]
      face.materialId = LUT_matId.get(tface.material_index, -1) #

      skmFile.AddFace(face)
    # -- END for face --

    # Sort faces with material id
    skmFile.Faces.Data = sorted(skmFile.Faces.Data, key=lambda f: f.materialId)

    for p in pointsMap.items():
      skmFile.AddPoint(p)

    for v in verticesMap.items():
      skmFile.AddVertex(v)


    vgMap = self.parseVertexGroups(obj, blenderToSKM_vertexId, skmFile)
    self.parseBoneWeights(vgMap, skmFile)
    self.parseShapeKeys(bpy.data.objects[AOname], blenderToSKM_vertexId, skmFile)

    # Remove the triangulated object from the scene
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.parent = None
    bpy.context.scene.objects.unlink(obj)


  def parseMaterial(self, skmFile, materials):
    ___doc___ = '''
    Parse the object material and return a LUT to get material index
    from Blender to SKM/user specification
    '''
    materialMap = ObjMap()
    lut = dict()

    #materialMap.get(TMaterial("SKM_NoMaterial")) # create a default material

    for i in range(len(materials)):
      mat = TMaterial(materials[i].material)
      lut[i] = materialMap.get(mat)

    for m in materialMap.items():
      skmFile.AddMaterial(m)

    return lut


  def parseVertexGroups(self, obj, blenderToSKM_vertexId, skmFile):
    # 1) Initialized an empty list for each VG, index by VG's name
    VertexGroups = obj.vertex_groups

    if len(VertexGroups) == 0:
      print( "no VertexGroup found.")
      return

    vgMap = { k:set() for k in VertexGroups.keys() }

    # 2) Associate each vertices/points to their groups with weight
    for v in obj.data.vertices:
      for vg in v.groups:

        # TODO: strange error here and i'm not sure where it come from
        # (looks like old VertexGroup are not cleaned from vertices)
        if vg.group >= len(VertexGroups):
          #print("parseVertexGroups: Error on group index (%d)." % vg.group)
          continue

        key = VertexGroups[vg.group].name
        vertexId = blenderToSKM_vertexId[v.index]
        pointId  = skmFile.Vertices.Data[vertexId].pointId 
        vgMap[key].add( (pointId, vg.weight)) #~

    return vgMap


  def parseBoneWeights(self, vgMap, skmFile):
    if not skmFile.bones_ref:
      return

    # 1) Add bone weights to the SKM structure
    BonesList = skmFile.bones_ref.Data

    if len(BonesList) == 0:
      return

    for boneId in range(len(BonesList)):
      bone = BonesList[boneId]
      vwList = vgMap.get(bone.name, None)
      if vwList == None:
        continue
      for vw in vwList:
        # for bones, unspecified vertices have a null weight
        if vw[1] < python_epsilon:
          continue
        bw = TBoneWeight(boneId, vw[0], vw[1])
        skmFile.AddBoneWeight(bw)
      # Remove the bone VG
      del vgMap[bone.name]

    # 2) Sort bone weights on pointId
    skmFile.BoneWeights.Data = sorted(skmFile.BoneWeights.Data, key=lambda f: f.pointId) # ~


  def parseShapeKeys(self, mesh, blenderToSKM_vertexId, skmFile):
    shape_keys = mesh.data.shape_keys
    if shape_keys == None:
      return

    start = 0
    for sk in shape_keys.key_blocks:
      # Don't take base key
      if sk.name == sk.relative_key.name:
        continue

      # Here if VertexGroup handled
      #skmFile.AddShapeKeyInfo(TShapeKeyInfo(sk.name))
      
      if sk.vertex_group != '':
        print('Warning: ShapeKey export with vertex group not implemented yet.')
        continue

      keyVertices = sk.data
      relativeVertices = sk.relative_key.data
      count = 0
      for vid in range(len(keyVertices)):
        tvec = keyVertices[vid].co - relativeVertices[vid].co
        # Export modified vertices only
        if (tvec.dot(tvec) > python_epsilon):
          tvec = qBlenderToGL * tvec
          vertexId = blenderToSKM_vertexId[vid]
          pointId  = skmFile.Vertices.Data[vertexId].pointId #~
          ShapeKeyData = TShapeKeyData(pointId, tvec.x, tvec.y, tvec.z)
          skmFile.AddShapeKeyData(ShapeKeyData)
          count += 1

      skmFile.AddShapeKeyInfo(TShapeKeyInfo(sk.name, start, count))
      start += count

# -- END class MeshParser --



#-----------------------------------------------------
# todo: Change this later
#-----------------------------------------------------
def get_armature():
  print( 'get_armature : bad, to change')

  bpy.ops.object.mode_set(mode='OBJECT')

  Scene = bpy.context.scene
  arms = [o for o in Scene.objects if o.type == 'ARMATURE']
  
  '''
  if len(arms) != 1:
    raise Exception('Error : a single armature must be selected.')  
  '''
  if len(arms) == 0:
    return None

  armature = arms[0]
  return armature


def get_mesh():
  ''' Return an OBJECT of type MESH '''
  C = bpy.context
  mesh = None

  obj = C.active_object
  if obj and (obj.type == 'MESH'):
    mesh = obj

  return mesh

#-----------------------------------------------------
#-----------------------------------------------------


def export(filepath=''):
  tick = time.clock()

  # Data handlers
  skmFile = SKMFile()
  skaFile = SKAFile()

  # Retrieve armature & mesh OBJECT, if any
  armature = get_armature()
  mesh     = get_mesh()

  if mesh and armature != mesh.parent:
    print('Warning: The selected mesh and armature are unrelated.')
    armature = mesh.parent

  saved_pose_position = 'POSE' # ~
  if True and armature != None:    
    # Parse bones and animations
    ArmatureParser().parse(skaFile, armature)
    
    # Parse animation sequences and keyframes
    AnimationParser().parse(skaFile, armature)
    #print("Animation export disabled")

    # Copy skeleton joint data from SKA to SKM (XXX)
    skmFile.bones_ref = skaFile.Bones
    skmFile.AddSKAInfo(TSKAInfo(os.path.basename(filepath)))

    # the mesh must be exported in rest pose (unless otherwise specified)
    # (Note that armature modifier is not applied)
    saved_pose_position = armature.data.pose_position
    armature.data.pose_position = 'REST'
  else:
    skmFile.bones_ref = None

  if mesh != None:
    # Parse geometry, materials and bone weights
    MeshParser().parse(skmFile, mesh)


  if armature != None:
    armature.data.pose_position = saved_pose_position


  # Dump datas to file
  skmFile.save(filepath)
  skaFile.save(filepath)

  export_time = time.clock() - tick
  print('Export time: %f seconds' % (export_time))



# ================================================= #
# Blender interfaces
# ================================================= #

class ExportSKM(bpy.types.Operator):
  __doc__   = 'Export a skinned model to the SKM format'

  bl_idname = 'model.export_skm'
  bl_label  = 'Export to SKM'
  filepath  = bpy.props.StringProperty(subtype='FILE_PATH')

  def execute(self, context):
    scene = bpy.context.scene
    save_frame = scene.frame_current
    export(self.filepath)
    scene.frame_current = save_frame

    return {'FINISHED'}


# ================================================= #
# REGISTER / UNREGISTER
# ================================================= #

def menu_func(self, context):
  default_path = os.path.splitext(bpy.data.filepath)[0]
  self.layout.operator(ExportSKM.bl_idname, \
                       text='Skeleton Model data (.skm)').filepath = default_path

def register():
  bpy.utils.register_module(__name__)
  bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
  bpy.utils.unregister_module(__name__)
  bpy.types.INFO_MT_file_export.remove(menu_func)



# ================================================= #
# MAIN
# ================================================= #

def main():
  register()

if __name__ == '__main__':
  main()

