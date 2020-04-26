import bpy
import struct,time,sys,os,zlib,io,mathutils
from bpy_extras.io_utils import load_image, unpack_list, unpack_face_list
from mathutils import Vector, Matrix
#from xml.dom import minidom
import xml.sax.handler

class NodeHandler(xml.sax.handler.ContentHandler):
  def __init__(self,datapath):
    self.inData = 0
    self.datapath = datapath
  def startElement(self, name, attributes):
    if name == "node":
      node_type = attributes["type"]
    elif name == "mesh":
      self.inData = 1

  def characters(self,data):
    if self.inData == 1:
      self.buffer += data

  def endElement(self,name):
    if name == "node":
      pass
    elif name == "mesh":
      self.inData = 0
      mesh_file = self.datapath + self.buffer


def load_mesh_file(filepath):
  file = open(filepath, "rb")
  header = file.read(4)
  if (header == b'mi08'):
    out = "mesh"
  elif (header == b'ms08'):
    out = "smesh"
  else :
    file.close()
    return (None,None)

  data = file.read()
  file.close()
  return (out,io.BytesIO(data))

def read_bounds(data):
  min_x,min_y,min_z = struct.unpack("<fff",data.read(12))
  print ("min (", min_x, ",", min_y, ",",min_z,")")
  max_x,max_y,max_z = struct.unpack("<fff",data.read(12))
  print ("max (", max_x, ",", max_y, ",",max_z,")")
  center_x,center_y,center_z = struct.unpack("<fff",data.read(12))
  print ("center (", center_x, ",", center_y, ",",center_z,")")
  bounding_radius, = struct.unpack("<f",data.read(4))
  print ("radius ",bounding_radius)

def read_string (data):
  length, = struct.unpack("<L",data.read(4))
  name = data.read(length)
  #print("string ",name)
  return str(name,encoding="utf8")

def read_smesh(data):
  n_bones, = struct.unpack("<L",data.read(4))

  if n_bones > 0:
    skel = bpy.data.armatures.new("skeliton")
    arm_ob = bpy.data.objects.new("skeliton",skel)
    bpy.context.scene.objects.link(arm_ob)
    arm_ob.select = True
    bpy.context.scene.objects.active = arm_ob
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    while skel.edit_bones: skel.edit_bones.remove(skel.edit_bones[-1])
  bone_names = []
  parents = []
  print(n_bones," bones")
  for i in range (n_bones):
    bone_name = read_string(data)
    skel.edit_bones.new(bone_name)
    bone_names.append(bone_name)
    parent, =  struct.unpack("<l",data.read(4))
    parents.append(parent)

  for i in range(len(parents)):
    bone = skel.edit_bones[i]
    parent_num = parents[i]
    if parent_num > -1:
      parent = skel.edit_bones[parent_num]
      bone.parent = parent


  n_frames, = struct.unpack("<L",data.read(4))
  print(n_frames," frames")

  for i in range (n_frames):
    for j in range(n_bones):
      pos = struct.unpack("<fff",data.read(12))
      bone = skel.edit_bones[j]
      parent = bone.parent
      print ("bone ", bone.name, "parent ", parent )
      position = Vector(pos)
      bone.translate(position)
      #bone.tail = position
      #children = bone.children
      #for child in children: child.head = position
      #print ("position ", position)
      scale, = struct.unpack("<f",data.read(4))
      #print("scale ",scale)
      rotation = struct.unpack("<ffff",data.read(16))
      #print ("rotation ", rotation)
      #print("---")

  n_surfaces, = struct.unpack("<l",data.read(4))
  #print(n_surfaces, " surfaces")

  for i in range(n_surfaces):
    surface_name = read_string(data)
    #print ("surface_name, ", surface_name)

  for i in range(n_surfaces):
    verts = []
    norms = []
    n_verts, = struct.unpack("<l",data.read(4))
    #print ("num verts ", n_verts)
    for j in range(n_verts):
      vertex = struct.unpack("<fff",data.read(12))
      normal = struct.unpack("<HHH",data.read(6))
      n_weights, = struct.unpack("<B",data.read(1))
      weights = {}
      for k in range (n_weights):
        bone_index, = struct.unpack("<H",data.read(2))
        weight, = struct.unpack("<B",data.read(1))
        weights[bone_index]=weight
      verts.append(vertex)
      norms.append(normal)

    n_uvs0, = struct.unpack("<l",data.read(4))
    for j in range (n_uvs0):
      uvs0 = struct.unpack("<ff",data.read(8))
    n_uvs1, = struct.unpack("<l",data.read(4))
    for j in range (n_uvs1):
      uvs1 = struct.unpack("<ff",data.read(8))

    n_tris, = struct.unpack("<l",data.read(4))
    if n_tris < 65536:
      for j in range (n_tris):
        tri = struct.unpack("<HHH",data.read(6))
    else :
      for j in range(n_tris):
        tri = struct.unpack("<l",data.read(12))
    #print("verts",verts)

    #me = bpy.data.meshes.new(surface_name)
    #ob = bpy.data.objects.new(surface_name,me)
    #bpy.context.scene.objects.link(ob)
    #me.vertices.add(len(verts))
    #me.vertices.foreach_set("co",unpack_list(verts))
    #me.faces.add(len(faces))
    #me.faces.foreachc_set("vertices_raw",unpack_face_list(faces))

    #me.validate()
    #me.update(calc_edges=True)

def read_mesh(data):
  read_bounds(data)

  n_surfaces, = struct.unpack("<L",data.read(4))
  print ("found ",n_surfaces," surfaces")

  surface_names = []
  for i in range(n_surfaces):
    surface_name = read_string(data)
    surface_names.append(surface_name)
    print ("surface_name ",surface_name)
    read_bounds(data)

  for j in range(n_surfaces):
    n_vertices, = struct.unpack("<L",data.read(4))
    verts = []
    norms = []
    print(n_vertices," vertices")
    for i in range(n_vertices):
      x,y,z = struct.unpack("<fff",data.read(12))
      nx,ny,nz = struct.unpack("<hhh",data.read(6))
      verts.append((x,y,z))
      norms.append((float(nx)/33268.0,float(ny)/33268.0,float(nz)/33268.0))
    #print ("verts: ",verts)
    n_uvcoords0, = struct.unpack("<L",data.read(4))
    uvs0 = []
    for i in range(n_uvcoords0):
      (u,v) = struct.unpack("<ff",data.read(8))
      uvs0.append((u,v))
    n_uvcoords1, = struct.unpack("<L",data.read(4))
    uvs1 = []
    for i in range(n_uvcoords1):
      (u,v) = struct.unpack("<ff",data.read(8))
      uvs1.append((u,v))
    n_triangles, = struct.unpack("<L",data.read(4))
    faces = []
    if(n_vertices < 66536):
      for i in range(n_triangles):
        v0,v1,v2 = struct.unpack("<HHH",data.read(6))
        faces.append((v0,v1,v2))
    else:
      for i in range(n_triangles):
        v0,v1,v2  = struct.unpack("<LLL",data.read(12))
        faces.append((v0,v1,v2))
    surface_name = surface_names[j]
    me = bpy.data.meshes.new(surface_name)
    ob = bpy.data.objects.new(surface_name,me)
    bpy.context.scene.objects.link(ob)
    me.vertices.add(len(verts))
    me.vertices.foreach_set("co",unpack_list(verts))
    me.faces.add(len(faces))
    me.faces.foreach_set("vertices_raw",unpack_face_list(faces))

    for i in range(n_vertices):
      me.vertices[i].normal = norms[i]

    me.validate()
    me.update(calc_edges=True)

    if n_uvcoords0 > 0:
      b_uvs0 = me.uv_textures.new()
      for i in range(len(faces)):
        (v0,v1,v2) = faces[i]
        b_uvface = b_uvs0.data[i]
        b_uvface.uv1 = uvs0[v0]
        b_uvface.uv2 = uvs0[v1]
        b_uvface.uv3 = uvs0[v2]
    if n_uvcoords1 > 0:
      b_uvs1 = me.uv_textures.new()
      for i in range(len(faces)):
        (v0,v1,v2) = faces[i]
        b_uvface = b_uvs1.data[i]
        b_uvface.uv1 = uvs1[v0]
        b_uvface.uv2 = uvs1[v1]
        b_uvface.uv3 = uvs1[v2]

def find_datapath(dirpath):
  (dirbase,dirname) = os.path.split(dirpath)
  if dirname == "data":
    return dirpath
  return find_datapath(dirbase)

def read_node(filename,datapath):


def load(operator, context, filepath=""):
  (dirname,filename) = os.path.split(filepath)
  (filename,ext) = os.path.splitext(filename)
  print ("ext ", ext)
  if ext == ".node":
    datapath = find_datapath(dirname)
    read_node(filepath,datapath)
  (mesh_type,data) = load_mesh_file(filepath)

  if mesh_type == "smesh":
    read_smesh(data)
  elif mesh_type == "mesh":
    read_mesh(data)

  return {'FINISHED'}
