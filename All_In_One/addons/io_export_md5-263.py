# ***** BEGIN GPL LICENSE BLOCK ***** 
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program; if not, write to the Free Software Foundation, 
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. 
# 
# ***** END GPL LICENCE BLOCK *****
#

#"""
#Name: 'Quake Model 5 (.md5)...'
#Blender: 263
#Group: 'Export'
#Tooltip: 'Export a Quake Model 5 File'
#
#credit to der_ton for the 2.4x Blender export script
#"""

bl_info = { # changed from bl_addon_info in 2.57 -mikshaw
    "name": "Export idTech4 (.md5)",
    "author": "Paul Zirkle aka Keless, credit to der_ton, ported to Blender 2.62 by motorsep and tested by kat, special thanks to MCampagnini",
    "version": (1,0,0),
    "blender": (2, 6, 3),
    "api": 31847,
    "location": "File > Export > Skeletal Mesh/Animation Data (.md5mesh/.md5anim)",
    "description": "Export idTech4 (.md5)",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/File_I-O/idTech4_md5",
    "tracker_url": "http://www.katsbits.com/smforum/index.php?topic=167.0",
    "category": "Learnbgame"
}

import bpy,struct,math,os,time,sys,mathutils

#MATH UTILTY

def vector_crossproduct(v1, v2):
  return [
    v1[1] * v2[2] - v1[2] * v2[1],
    v1[2] * v2[0] - v1[0] * v2[2],
    v1[0] * v2[1] - v1[1] * v2[0],
    ]

def point_by_matrix(p, m):
  #print( str(type( p )) + " " + str(type(m)) )
  return [p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0] + m[3][0],
          p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1] + m[3][1],
          p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2] + m[3][2]]

def vector_by_matrix(p, m):
  return [p[0] * m.col[0][0] + p[1] * m.col[1][0] + p[2] * m.col[2][0],
          p[0] * m.col[0][1] + p[1] * m.col[1][1] + p[2] * m.col[2][1],
          p[0] * m.col[0][2] + p[1] * m.col[1][2] + p[2] * m.col[2][2]]

def vector_normalize(v):
  l = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
  try:
    return v[0] / l, v[1] / l, v[2] / l
  except:
    return 1, 0, 0

def matrix2quaternion(m):
  s = math.sqrt(abs(m.col[0][0] + m.col[1][1] + m.col[2][2] + m.col[3][3]))
  if s == 0.0:
    x = abs(m.col[2][1] - m.col[1][2])
    y = abs(m.col[0][2] - m.col[2][0])
    z = abs(m.col[1][0] - m.col[0][1])
    if   (x >= y) and (x >= z): return 1.0, 0.0, 0.0, 0.0
    elif (y >= x) and (y >= z): return 0.0, 1.0, 0.0, 0.0
    else:                       return 0.0, 0.0, 1.0, 0.0
  return quaternion_normalize([
    -(m.col[2][1] - m.col[1][2]) / (2.0 * s),
    -(m.col[0][2] - m.col[2][0]) / (2.0 * s),
    -(m.col[1][0] - m.col[0][1]) / (2.0 * s),
    0.5 * s,
    ])
    
def matrix_invert(m):
  det = (m.col[0][0] * (m.col[1][1] * m.col[2][2] - m.col[2][1] * m.col[1][2])
       - m.col[1][0] * (m.col[0][1] * m.col[2][2] - m.col[2][1] * m.col[0][2])
       + m.col[2][0] * (m.col[0][1] * m.col[1][2] - m.col[1][1] * m.col[0][2]))
  if det == 0.0: return None
  det = 1.0 / det
# transposed matrix
#  r = [ [
#      det * (m.col[1][1] * m.col[2][2] - m.col[2][1] * m.col[1][2]),
#    - det * (m.col[1][0] * m.col[2][2] - m.col[2][0] * m.col[1][2]),
#      det * (m.col[1][0] * m.col[2][1] - m.col[2][0] * m.col[1][1]),
#    ], [
#    - det * (m.col[0][1] * m.col[2][2] - m.col[2][1] * m.col[0][2]),
#     det * (m.col[0][0] * m.col[2][2] - m.col[2][0] * m.col[0][2]),
#   - det * (m.col[0][0] * m.col[2][1] - m.col[2][0] * m.col[0][1]),
#    ], [
#      det * (m.col[0][1] * m.col[1][2] - m.col[1][1] * m.col[0][2]),
#    - det * (m.col[0][0] * m.col[1][2] - m.col[1][0] * m.col[0][2]),
#      det * (m.col[0][0] * m.col[1][1] - m.col[1][0] * m.col[0][1]),
#    ], [
#      0.0,
#      0.0,
#      0.0,
#    ] ]
# original matrix from 2.61 compaticle script adopted for 2.62; the mesh with this matric is consistent, but rotated 180 degrees around Z axis and centered at 0 0 0
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
    -(m.col[3][0] * r[0][0] + m.col[3][1] * r[1][0] + m.col[3][2] * r[2][0]),
    -(m.col[3][0] * r[0][1] + m.col[3][1] * r[1][1] + m.col[3][2] * r[2][1]),
    -(m.col[3][0] * r[0][2] + m.col[3][1] * r[1][2] + m.col[3][2] * r[2][2]),
    1.0,
    ])
  return r
    
def quaternion_normalize(q):
  l = math.sqrt(q.col[0] * q.col[0] + q.col[1] * q.col[1] + q.col[2] * q.col[2] + q.col[3] * q.col[3])
  return q.col[0] / l, q.col[1] / l, q.col[2] / l, q.col[3] / l
  

#shader material
class Material:
  name = ""		#string
  def __init__(self, textureFileName):
    self.name = textureFileName
  
  def to_md5mesh(self):
    return self.name;

#the 'Model' class, contains all submeshes
class Mesh:
  name = "" 		#string
  submeshes = []	#array of SubMesh
  next_submesh_id = 0	#int

  def __init__(self, name):
    self.name      = name
    self.submeshes = []
    
    self.next_submesh_id = 0

    
  def to_md5mesh(self):
    meshnumber=0
    buf = ""
    for submesh in self.submeshes:
      buf=buf + "mesh {\n"
#      buf=buf + "mesh {\n\t// meshes: " + submesh.name + "\n"  # used for Sauerbraten -mikshaw
      meshnumber += 1
      buf=buf + submesh.to_md5mesh()
      buf=buf + "}\n\n"

    return buf


#submeshes reference a parent mesh
class SubMesh:
  def __init__(self, mesh, material):
    self.material   = material
    self.vertices   = []
    self.faces      = []
    self.nb_lodsteps = 0
    self.springs    = []
    self.weights    = []
    
    self.next_vertex_id = 0
    self.next_weight_id = 0
    
    self.mesh = mesh
    self.name = mesh.name
    self.id = mesh.next_submesh_id
    mesh.next_submesh_id += 1
    mesh.submeshes.append(self)

  def bindtomesh (self, mesh):
    # HACK: this is needed for md5 output, for the time being...
    # appending this submesh to the specified mesh, disconnecting it from the original one
    self.mesh.submeshes.remove(self)
    self.mesh = mesh
    self.id = mesh.next_submesh_id
    mesh.next_submesh_id += 1
    mesh.submeshes.append(self)

  def generateweights(self):
    self.weights = []
    self.next_weight_id = 0
    for vert in self.vertices:
      vert.generateweights()

  def reportdoublefaces(self):
    for face in self.faces:
      for face2 in self.faces:
        if not face == face2:
          if (not face.vertex1==face2.vertex1) and (not face.vertex1==face2.vertex2) and (not face.vertex1==face2.vertex3):
            return
          if (not face.vertex2==face2.vertex1) and (not face.vertex2==face2.vertex2) and (not face.vertex2==face2.vertex3):
            return
          if (not face.vertex3==face2.vertex1) and (not face.vertex3==face2.vertex2) and (not face.vertex3==face2.vertex3):
            return
          print('doubleface! %s %s' % (face, face2))
          
  def to_md5mesh(self):
    self.generateweights()

    self.reportdoublefaces()
    
    buf="\tshader \"%s\"\n\n" % (self.material.to_md5mesh())
    if len(self.weights) == 0:
      buf=buf + "\tnumverts 0\n"
      buf=buf + "\n\tnumtris 0\n"
      buf=buf + "\n\tnumweights 0\n"
      return buf
    
    # output vertices
    buf=buf + "\tnumverts %i\n" % (len(self.vertices))
    vnumber=0
    for vert in self.vertices:
      buf=buf + "\tvert %i %s\n" % (vnumber, vert.to_md5mesh())
      vnumber += 1
    
    # output faces
    buf=buf + "\n\tnumtris %i\n" % (len(self.faces))
    facenumber=0
    for face in self.faces:
      buf=buf + "\ttri %i %s\n" % (facenumber, face.to_md5mesh())
      facenumber += 1
      
    # output weights
    buf=buf + "\n\tnumweights %i\n" % (len(self.weights))
    weightnumber=0
    for weight in self.weights:
      buf=buf + "\tweight %i %s\n" % (weightnumber, weight.to_md5mesh())
      weightnumber += 1
      
    return buf
    
#vertex class contains and outputs 'verts' but also generates 'weights' data
class Vertex:
  def __init__(self, submesh, loc, normal):
    self.loc    = loc
    self.normal = normal
    self.collapse_to         = None
    self.face_collapse_count = 0
    self.maps       = []
    self.influences = []
    self.weights = []
    self.weight = None
    self.firstweightindx = 0
    self.cloned_from = None
    self.clones      = []
    
    self.submesh = submesh
    self.id = submesh.next_vertex_id
    submesh.next_vertex_id += 1
    submesh.vertices.append(self)
    
  def generateweights(self):
    self.firstweightindx = self.submesh.next_weight_id
    for influence in self.influences:
      weightindx = self.submesh.next_weight_id
      self.submesh.next_weight_id += 1
      newweight = Weight(influence.bone, influence.weight, self, weightindx, self.loc[0], self.loc[1], self.loc[2])
      self.submesh.weights.append(newweight)
      self.weights.append(newweight)

  def to_md5mesh(self):
    if self.maps:
      buf = self.maps[0].to_md5mesh()
    else:
      buf = "( %f %f )" % (self.loc[0], self.loc[1])
    buf = buf + " %i %i" % (self.firstweightindx, len(self.influences))
    return buf    
    
#texture coordinate map 
class Map:
  def __init__(self, u, v):
    self.u = u
    self.v = v
    

  def to_md5mesh(self):
    buf = "( %f %f )" % (self.u, self.v)
    return buf

#NOTE: uses global 'scale' to scale the size of model verticies
#generated and stored in Vertex class
class Weight:
  def __init__(self, bone, weight, vertex, weightindx, x, y, z):
    self.bone = bone
    self.weight = weight
    self.vertex = vertex
    self.indx = weightindx
    invbonematrix = matrix_invert(self.bone.matrix)
    self.x, self.y, self.z = point_by_matrix ((x, y, z), invbonematrix)
    
  def to_md5mesh(self):
    buf = "%i %f ( %f %f %f )" % (self.bone.id, self.weight, self.x*scale, self.y*scale, self.z*scale)
    return buf

#used by SubMesh class
class Influence:
  def __init__(self, bone, weight):
    self.bone   = bone
    self.weight = weight
    
#outputs the 'tris' data
class Face:
  def __init__(self, submesh, vertex1, vertex2, vertex3):
    self.vertex1 = vertex1
    self.vertex2 = vertex2
    self.vertex3 = vertex3
    
    self.can_collapse = 0
    
    self.submesh = submesh
    submesh.faces.append(self)
    

  def to_md5mesh(self):
    buf = "%i %i %i" % (self.vertex1.id, self.vertex3.id, self.vertex2.id)
    return buf

#holds bone skeleton data and outputs header above the Mesh class
class Skeleton:
  def __init__(self, MD5Version = 10, commandline = ""):
    self.bones = []
    self.MD5Version = MD5Version
    self.commandline = commandline
    self.next_bone_id = 0
    

  def to_md5mesh(self, numsubmeshes):
    buf = "MD5Version %i\n" % (self.MD5Version)
    buf = buf + "commandline \"%s\"\n\n" % (self.commandline)
    buf = buf + "numJoints %i\n" % (self.next_bone_id)
    buf = buf + "numMeshes %i\n\n" % (numsubmeshes)
    buf = buf + "joints {\n"
    for bone in self.bones:
      buf = buf + bone.to_md5mesh()
    buf = buf + "}\n\n"
    return buf

BONES = {}

#held by Skeleton, generates individual 'joint' data
class Bone:
  def __init__(self, skeleton, parent, name, mat, theboneobj):
    self.parent = parent #Bone
    self.name   = name   #string
    self.children = []   #list of Bone objects
    self.theboneobj = theboneobj #Blender.Armature.Bone
    # HACK: this flags if the bone is animated in the one animation that we export
    self.is_animated = 0  # = 1, if there is an ipo that animates this bone

    self.matrix = mat
    if parent:
      parent.children.append(self)
    
    self.skeleton = skeleton
    self.id = skeleton.next_bone_id
    skeleton.next_bone_id += 1
    skeleton.bones.append(self)
    
    BONES[name] = self


  def to_md5mesh(self):
    buf= "\t\"%s\"\t" % (self.name)
    parentindex = -1
    if self.parent:
        parentindex=self.parent.id
    buf=buf+"%i " % (parentindex)
    
    pos1, pos2, pos3= self.matrix.col[3][0], self.matrix.col[3][1], self.matrix.col[3][2]
    buf=buf+"( %f %f %f ) " % (pos1*scale, pos2*scale, pos3*scale)
    #qx, qy, qz, qw = matrix2quaternion(self.matrix)
    #if qw<0:
    #    qx = -qx
    #    qy = -qy
    #    qz = -qz
    m = self.matrix
#    bquat = self.matrix.to_quat()  #changed from matrix.toQuat() in blender 2.4x script
    bquat = self.matrix.to_quaternion()  #changed from to_quat in 2.57 -mikshaw
    bquat.normalize()
    qx = bquat.x
    qy = bquat.y
    qz = bquat.z
    if bquat.w > 0:
        qx = -qx
        qy = -qy
        qz = -qz
    buf=buf+"( %f %f %f )\t\t// " % (qx, qy, qz)
    if self.parent:
        buf=buf+"%s" % (self.parent.name)    
    
    buf=buf+"\n"
    return buf


class MD5Animation:
  def __init__(self, md5skel, MD5Version = 10, commandline = ""):
    self.framedata    = [] # framedata[boneid] holds the data for each frame
    self.bounds       = []
    self.baseframe    = []
    self.skeleton     = md5skel
    self.boneflags    = []  # stores the md5 flags for each bone in the skeleton
    self.boneframedataindex = [] # stores the md5 framedataindex for each bone in the skeleton
    self.MD5Version   = MD5Version
    self.commandline  = commandline
    self.numanimatedcomponents = 0
    self.framerate    = 24
    self.numframes    = 0
    for b in self.skeleton.bones:
      self.framedata.append([])
      self.baseframe.append([])
      self.boneflags.append(0)
      self.boneframedataindex.append(0)
      
  def to_md5anim(self):
    currentframedataindex = 0
    for bone in self.skeleton.bones:
      if (len(self.framedata[bone.id])>0):
        if (len(self.framedata[bone.id])>self.numframes):
          self.numframes=len(self.framedata[bone.id])
        (x,y,z),(qw,qx,qy,qz) = self.framedata[bone.id][0]
        self.baseframe[bone.id]= (x*scale,y*scale,z*scale,qx,qy,qz)
        self.boneframedataindex[bone.id]=currentframedataindex
        self.boneflags[bone.id] = 63
        currentframedataindex += 6
        self.numanimatedcomponents = currentframedataindex
      else:
        rot=bone.matrix.to_quaternion()
        rot.normalize()
        qx=rot.x
        qy=rot.y
        qz=rot.z
        if rot.w > 0:
            qx = -qx
            qy = -qy
            qz = -qz            
        self.baseframe.col[bone.id]= (bone.matrix.col[3][0]*scale, bone.matrix.col[3][1]*scale, bone.matrix.col[3][2]*scale, qx, qy, qz)
        
    buf = "MD5Version %i\n" % (self.MD5Version)
    buf = buf + "commandline \"%s\"\n\n" % (self.commandline)
    buf = buf + "numFrames %i\n" % (self.numframes)
    buf = buf + "numJoints %i\n" % (len(self.skeleton.bones))
    buf = buf + "frameRate %i\n" % (self.framerate)
    buf = buf + "numAnimatedComponents %i\n\n" % (self.numanimatedcomponents)
    buf = buf + "hierarchy {\n"

    for bone in self.skeleton.bones:
      parentindex = -1
      flags = self.boneflags[bone.id]
      framedataindex = self.boneframedataindex[bone.id]
      if bone.parent:
        parentindex=bone.parent.id
      buf = buf + "\t\"%s\"\t%i %i %i\t//" % (bone.name, parentindex, flags, framedataindex)
      if bone.parent:
        buf = buf + " " + bone.parent.name
      buf = buf + "\n"
    buf = buf + "}\n\n"

    buf = buf + "bounds {\n"
    for b in self.bounds:
      buf = buf + "\t( %f %f %f ) ( %f %f %f )\n" % (b)
    buf = buf + "}\n\n"

    buf = buf + "baseframe {\n"
    for b in self.baseframe:
      buf = buf + "\t( %f %f %f ) ( %f %f %f )\n" % (b)
    buf = buf + "}\n\n"

    for f in range(0, self.numframes):
      buf = buf + "frame %i {\n" % (f)
      for b in self.skeleton.bones:
        if (len(self.framedata[b.id])>0):
          (x,y,z),(qw,qx,qy,qz) = self.framedata[b.id][f]
          if qw>0:
            qx,qy,qz = -qx,-qy,-qz
          buf = buf + "\t%f %f %f %f %f %f\n" % (x*scale, y*scale, z*scale, qx,qy,qz)
      buf = buf + "}\n\n"
      
    return buf
  
  def addkeyforbone(self, boneid, time, loc, rot):
    # time is ignored. the keys are expected to come in sequentially
    # it might be useful for future changes or modifications for other export formats
    self.framedata[boneid].append((loc, rot))
    return
    

def getminmax(listofpoints):
  if len(listofpoints[0]) == 0: return ([0,0,0],[0,0,0])
  min = [listofpoints[0][0], listofpoints[1][0], listofpoints[2][0]]
  max = [listofpoints[0][0], listofpoints[1][0], listofpoints[2][0]]
  if len(listofpoints[0])>1:
    for i in range(1, len(listofpoints[0])):
      if listofpoints[i][0]>max[0]: max[0]=listofpoints[i][0]
      if listofpoints[i][1]>max[1]: max[1]=listofpoints[i][1]
      if listofpoints[i][2]>max[2]: max[2]=listofpoints[i][2]
      if listofpoints[i][0]<min[0]: min[0]=listofpoints[i][0]
      if listofpoints[i][1]<min[1]: min[1]=listofpoints[i][1]
      if listofpoints[i][2]<min[2]: min[2]=listofpoints[i][2]
  return (min, max)

def generateboundingbox(objects, md5animation, framerange):
  scene = bpy.context.scene #Blender.Scene.getCurrent()
  context = scene.render #scene.getRenderingContext()
  for i in range(framerange[0], framerange[1]+1):
    corners = []
    #context.currentFrame(i)
    #scene.makeCurrent()
    scene.frame_set( i ) 
    
    for obj in objects:
      data = obj.data #obj.getData()
      #if (type(data) is Blender.Types.NMeshType) and data.faces:
      if obj.type == 'MESH' and data.polygons:
        #obj.makeDisplayList()
        #(lx, ly, lz) = obj.getLocation()
        (lx, ly, lz ) = obj.location
        #bbox = obj.getBoundBox()
        bbox = obj.bound_box
# transposed matrix
#        matrix = [[1.0,  0.0,  0.0,  0.0],
#          [0.0,  1.0,  1.0,  0.0],
#          [0.0,  0.0,  1.0,  0.0],
#          [0.0,  0.0,  0.0,  1.0],
#          ]
# original matrix from the 2.61 compatible script
        matrix = [[1.0,  0.0, 0.0, 0.0],
          [0.0,  1.0, 0.0, 0.0],
          [0.0,  1.0, 1.0, 0.0],
          [0.0,  0.0, 0.0, 1.0],
          ]
        for v in bbox:
          corners.append(point_by_matrix (v, matrix))
    (min, max) = getminmax(corners)
    md5animation.bounds.append((min[0]*scale, min[1]*scale, min[2]*scale, max[0]*scale, max[1]*scale, max[2]*scale))
  
    
#exporter settings
class md5Settings:
  def __init__(self,
               savepath,
               exportMode,
               scale=1.0
#               scale,
               ):
    self.savepath = savepath
    self.exportMode = exportMode
    self.scale = scale

#scale = 1.0

#SERIALIZE FUNCTION
def save_md5(settings):
  print("Exporting selected objects...")
  bpy.ops.object.mode_set(mode='OBJECT')
  
  scale = settings.scale
  
  
  
  thearmature = 0  #null to start, will assign in next section 
  
  #first pass on selected data, pull one skeleton
  skeleton = Skeleton(10, "Exported from Blender by io_export_md5.py by Paul Zirkle")
  bpy.context.scene.frame_set(bpy.context.scene.frame_start)
  for obj in bpy.context.selected_objects:
    if obj.type == 'ARMATURE':
      #skeleton.name = obj.name
      thearmature = obj
      w_matrix = obj.matrix_world
      
      #define recursive bone parsing function
      def treat_bone(b, parent = None):
        if (parent and not b.parent.name==parent.name):
          return #only catch direct children
        
        mat =  mathutils.Matrix(w_matrix) * mathutils.Matrix(b.matrix_local)  #reversed order of multiplication from 2.4 to 2.5!!! ARRRGGG
        
        bone = Bone(skeleton, parent, b.name, mat, b)
        
        if( b.children ):
          for child in b.children: treat_bone(child, bone)
          
      for b in thearmature.data.bones:
        if( not b.parent ): #only treat root bones'
          print( "root bone: " + b.name )
          treat_bone(b)
    
      break #only pull one skeleton out
  
  #second pass on selected data, pull meshes
  meshes = []
  for obj in bpy.context.selected_objects:
    if ((obj.type == 'MESH') and ( len(obj.data.vertices.values()) > 0 )):
      #for each non-empty mesh
      mesh = Mesh(obj.name)
      obj.data.update(calc_tessface=True)
      print( "Processing mesh: "+ obj.name )
      meshes.append(mesh)

      numTris = 0
      numWeights = 0
      for f in obj.data.polygons:
        numTris += len(f.vertices) - 2
      for v in obj.data.vertices:
        numWeights += len( v.groups )
        
      w_matrix = obj.matrix_world
      verts = obj.data.vertices
      
      uv_textures = obj.data.tessface_uv_textures
      faces = []
      for f in obj.data.polygons:
        faces.append( f )
      
      createVertexA = 0
      createVertexB = 0
      createVertexC = 0
        
      while faces:
        material_index = faces[0].material_index
        material = Material(obj.data.materials[material_index].name) #call the shader name by the material's name
        
        submesh = SubMesh(mesh, material)
        vertices = {}
        for face in faces[:]:
          # der_ton: i added this check to make sure a face has at least 3 vertices.
          # (pdz) also checks for and removes duplicate verts
          if len(face.vertices) < 3: # throw away faces that have less than 3 vertices
            faces.remove(face)
          elif face.vertices[0] == face.vertices[1]:  #throw away degenerate triangles
            faces.remove(face)
          elif face.vertices[0] == face.vertices[2]:
            faces.remove(face)
          elif face.vertices[1] == face.vertices[2]:
            faces.remove(face)
          elif face.material_index == material_index:
            #all faces in each sub-mesh must have the same material applied
            faces.remove(face)
            
            if not face.use_smooth :
              p1 = verts[ face.vertices[0] ].co
              p2 = verts[ face.vertices[1] ].co
              p3 = verts[ face.vertices[2] ].co
              normal = vector_normalize(vector_by_matrix(vector_crossproduct( \
              	[p3[0] - p2[0], p3[1] - p2[1], p3[2] - p2[2]], \
              	[p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]], \
              	), w_matrix))
            
            #for each vertex in this face, add unique to vertices dictionary
            face_vertices = []
            for i in range(len(face.vertices)):
              vertex = False
              if face.vertices[i] in vertices: 
                vertex = vertices[  face.vertices[i] ] #type of Vertex
              if not vertex: #found unique vertex, add to list
                coord  = point_by_matrix( verts[face.vertices[i]].co, w_matrix ) #TODO: fix possible bug here
                if face.use_smooth: normal = vector_normalize(vector_by_matrix( verts[face.vertices[i]].normal, w_matrix ))
                vertex  = vertices[face.vertices[i]] = Vertex(submesh, coord, normal) 
                createVertexA += 1
                
                influences = []
                for j in range(len( obj.data.vertices[ face.vertices[i] ].groups )):
                  inf = [obj.vertex_groups[ obj.data.vertices[ face.vertices[i] ].groups[j].group ].name, obj.data.vertices[ face.vertices[i] ].groups[j].weight]
                  influences.append( inf )
                
                if not influences:
                  print( "There is a vertex without attachment to a bone in mesh: " + mesh.name )
                sum = 0.0
                for bone_name, weight in influences: sum += weight
                
                for bone_name, weight in influences:
                  if sum != 0:
                    try:
                        vertex.influences.append(Influence(BONES[bone_name], weight / sum))
                    except:
                        continue
                  else: # we have a vertex that is probably not skinned. export anyway
                    try:
                        vertex.influences.append(Influence(BONES[bone_name], weight))
                    except:
                        continue
                
                #print( "vert " + str( face.vertices[i] ) + " has " + str(len( vertex.influences ) ) + " influences ")
                        
              elif not face.use_smooth:
                # We cannot share vertex for non-smooth faces, since Cal3D does not
                # support vertex sharing for 2 vertices with different normals.
                # => we must clone the vertex.
                
                old_vertex = vertex
                vertex = Vertex(submesh, vertex.loc, normal)
                createVertexB += 1
                vertex.cloned_from = old_vertex
                vertex.influences = old_vertex.influences
                old_vertex.clones.append(vertex)
              
              hasFaceUV = len(uv_textures) > 0 #borrowed from export_obj.py
              
              if hasFaceUV: 
              	uv = [uv_textures.active.data[face.index].uv[i][0], uv_textures.active.data[face.index].uv[i][1]]
              	uv[1] = 1.0 - uv[1]  # should we flip Y? yes, new in Blender 2.5x
              	if not vertex.maps: vertex.maps.append(Map(*uv))
              	elif (vertex.maps[0].u != uv[0]) or (vertex.maps[0].v != uv[1]):
                  # This vertex can be shared for Blender, but not for MD5
                  # MD5 does not support vertex sharing for 2 vertices with
                  # different UV texture coodinates.
                  # => we must clone the vertex.

                  for clone in vertex.clones:
                    if (clone.maps[0].u == uv[0]) and (clone.maps[0].v == uv[1]):
                      vertex = clone
                      break
                  else: # Not yet cloned...  (PDZ) note: this ELSE belongs attached to the FOR loop.. python can do that apparently
                    old_vertex = vertex
                    vertex = Vertex(submesh, vertex.loc, vertex.normal)
                    createVertexC += 1
                    vertex.cloned_from = old_vertex
                    vertex.influences = old_vertex.influences
                    vertex.maps.append(Map(*uv))
                    old_vertex.clones.append(vertex)

              face_vertices.append(vertex)
              
            # Split faces with more than 3 vertices
            for i in range(1, len(face.vertices) - 1):
              Face(submesh, face_vertices[0], face_vertices[i], face_vertices[i + 1])
          else:
            print( "found face with invalid material!!!!" )
      print( "created verts at A " + str(createVertexA) + ", B " + str( createVertexB ) + ", C " + str( createVertexC ) )
      
  # Export animations
  ANIMATIONS = {}

  arm_action = thearmature.animation_data.action
  rangestart = 0
  rangeend = 0
  if arm_action:
    animation = ANIMATIONS[arm_action.name] = MD5Animation(skeleton)
#    armature.animation_data.action = action
    bpy.context.scene.update()
    armature = bpy.context.active_object
    action = armature.animation_data.action
#    framemin, framemax	= bpy.context.active_object.animation_data.Action(fcurves.frame_range)
    framemin, framemax  = action.frame_range
    rangestart = int(framemin)
    rangeend = int(framemax)
#    rangestart = int( bpy.context.scene.frame_start ) # int( arm_action.frame_range[0] )
#    rangeend = int( bpy.context.scene.frame_end ) #int( arm_action.frame_range[1] )
    currenttime = rangestart
    while currenttime <= rangeend: 
      bpy.context.scene.frame_set(currenttime)
      time = (currenttime - 1.0) / 24.0 #(assuming default 24fps for md5 anim)
      pose = thearmature.pose

      for bonename in thearmature.data.bones.keys():
        posebonemat = mathutils.Matrix(pose.bones[bonename].matrix ) # @ivar poseMatrix: The total transformation of this PoseBone including constraints. -- different from localMatrix

        try:
          bone  = BONES[bonename] #look up md5bone
        except:
          print( "found a posebone animating a bone that is not part of the exported armature: " + bonename )
          continue
        if bone.parent: # need parentspace-matrix
          parentposemat = mathutils.Matrix(pose.bones[bone.parent.name].matrix ) # @ivar poseMatrix: The total transformation of this PoseBone including constraints. -- different from localMatrix
#          posebonemat = parentposemat.invert() * posebonemat #reverse order of multiplication!!!
          parentposemat.invert() # mikshaw
          posebonemat = parentposemat * posebonemat # mikshaw
        else:
          posebonemat = thearmature.matrix_world * posebonemat  #reverse order of multiplication!!!
        loc = [posebonemat.col[3][0],
            posebonemat.col[3][1],
            posebonemat.col[3][2],
            ]
#        rot = posebonemat.to_quat().normalize()
        rot = posebonemat.to_quaternion() # changed from to_quat in 2.57 -mikshaw
        rot.normalize() # mikshaw
        rot = [rot.w,rot.x,rot.y,rot.z]
        
        animation.addkeyforbone(bone.id, time, loc, rot)
      currenttime += 1
        
  # here begins md5mesh and anim output
  # this is how it works
  # first the skeleton is output, using the data that was collected by the above code in this export function
  # then the mesh data is output (into the same md5mesh file)

  if( settings.exportMode == "mesh & anim" or settings.exportMode == "mesh only" ):
	  md5mesh_filename = settings.savepath + ".md5mesh"

	  #save all submeshes in the first mesh
	  if len(meshes)>1:
	    for mesh in range (1, len(meshes)):
	      for submesh in meshes[mesh].submeshes:
	        submesh.bindtomesh(meshes[0])
	  if (md5mesh_filename != ""):
	    try:
	      file = open(md5mesh_filename, 'w')
	    except IOError:
	      errmsg = "IOError " #%s: %s" % (errno, strerror)
	    buffer = skeleton.to_md5mesh(len(meshes[0].submeshes))
	    #for mesh in meshes:
	    buffer = buffer + meshes[0].to_md5mesh()
	    file.write(buffer)
	    file.close()
	    print( "saved mesh to " + md5mesh_filename )
	  else:
	    print( "No md5mesh file was generated." )

  if( settings.exportMode == "mesh & anim" or settings.exportMode == "anim only" ):
	  md5anim_filename = settings.savepath + ".md5anim"

	  #save animation file
	  if len(ANIMATIONS)>0:
	    anim = ANIMATIONS.popitem()[1] #ANIMATIONS.values()[0]
	    print( str( anim ) )
	    try:
	      file = open(md5anim_filename, 'w')
	    except IOError:
	      errmsg = "IOError " #%s: %s" % (errno, strerror)
	    objects = []
	    for submesh in meshes[0].submeshes:
	      if len(submesh.weights) > 0:
	        obj = None
	        for sob in bpy.context.selected_objects:
	            if sob and sob.type == 'MESH' and sob.name == submesh.name:
	              obj = sob
	        objects.append (obj)
	    generateboundingbox(objects, anim, [rangestart, rangeend])
	    buffer = anim.to_md5anim()
	    file.write(buffer)
	    file.close()
	    print( "saved anim to " + md5anim_filename )
	  else:
	    print( "No md5anim file was generated." )
  
##########
#export class registration and interface
from bpy.props import *
class ExportMD5(bpy.types.Operator):
  '''Export to idTech 4 MD5 (.md5mesh .md5anim)'''
  bl_idname = "export.md5"
  bl_label = 'idTech 4 MD5'
  
  logenum = [("console","Console","log to console"),
             ("append","Append","append to log file"),
             ("overwrite","Overwrite","overwrite log file")]
             
  #search for list of actions to export as .md5anims
  #md5animtargets = []
  #for anim in bpy.data.actions:
  #	md5animtargets.append( (anim.name, anim.name, anim.name) )
  	
  #md5animtarget = None
  #if( len( md5animtargets ) > 0 ):
  #	md5animtarget = EnumProperty( name="Anim", items = md5animtargets, description = "choose animation to export", default = md5animtargets[0] )
  	
  exportModes = [("mesh & anim", "Mesh & Anim", "Export .md5mesh and .md5anim files."),
  		 ("anim only", "Anim only.", "Export .md5anim only."),
  		 ("mesh only", "Mesh only.", "Export .md5mesh only.")]

  filepath = StringProperty(subtype = 'FILE_PATH',name="File Path", description="Filepath for exporting", maxlen= 1024, default= "")
  md5name = StringProperty(name="MD5 Name", description="MD3 header name / skin path (64 bytes)",maxlen=64,default="")
  md5exportList = EnumProperty(name="Exports", items=exportModes, description="Choose export mode.", default='mesh & anim')
  #md5logtype = EnumProperty(name="Save log", items=logenum, description="File logging options",default = 'console')
  md5scale = FloatProperty(name="Scale", description="Scale all objects from world origin (0,0,0)", min=0.001, max=1000.0, default=1.0,precision=6)
  #md5offsetx = FloatProperty(name="Offset X", description="Transition scene along x axis",default=0.0,precision=5)
  #md5offsety = FloatProperty(name="Offset Y", description="Transition scene along y axis",default=0.0,precision=5)
  #md5offsetz = FloatProperty(name="Offset Z", description="Transition scene along z axis",default=0.0,precision=5)
  
  

  def execute(self, context):
    global scale
    scale = self.md5scale
    settings = md5Settings(savepath = self.properties.filepath,
                           exportMode = self.properties.md5exportList
                           )
    save_md5(settings)
    return {'FINISHED'}

  def invoke(self, context, event):
        WindowManager = context.window_manager
        # fixed for 2.56? Katsbits.com (via Nic B)
        # original WindowManager.add_fileselect(self)
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}  

def menu_func(self, context):
  default_path = os.path.splitext(bpy.data.filepath)[0]
  self.layout.operator(ExportMD5.bl_idname, text="idTech 4 MD5 (.md5mesh .md5anim)", icon='BLENDER').filepath = default_path
  
def register():
  bpy.utils.register_module(__name__)  #mikshaw
  bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
  bpy.utils.unregister_module(__name__)  #mikshaw
  bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
  register()