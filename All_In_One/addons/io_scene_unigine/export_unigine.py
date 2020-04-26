import bpy
import io, struct
from math import sqrt

class Surface:
  def __init__(self, mesh, material):
    self.material = material
    self.vertices = []
    self.faces = []
    self.mesh = mesh
    self.name = mesh.name

def write_objects(data,objects):
  surfaces = []
  for ob in objects:
    if(ob.type == 'MESH') and (len(ob.data.vertices.values()) > 0):
      n_tris = 0
      for f in ob.data.faces:
        n_tris += len(f.vertices) - 2
      w_matrix = ob.matrix_world
      verts = ob.data.vertices
      uvs = ob.data.uv_textures
      faces = []
      for f in ob.data.faces:
        faces.append(f)
      va = 0
      vb = 0
      vc = 0
      #surface = Surface()
      while faces:
        material_index = faces[0].material_index
        material = Material(ob.data.materials[0].name)
        vertices = {}
        for face in faces[:]:
          if len(face.vertices) < 3: faces.remove(face)
          elif face.vertices[0] == face.vertices[1]: faces.remove(face)
          elif face.vertices[0] == face.vertices[2]: faces.remove(face)
          elif face.vertices[1] == face.vertices[2]: faces.remove(face)
          elif face.material_index == material_index:
            faces.remove(face)
            if not face.use_smooth:
              p0 = verts[face.vertices[0]].co
              p1 = verts[face.vertices[1]].co
              p2 = verts[face.vertices[2]].co
            face_verts = []
            for i in range(len(face.vertices)):
              vertex = False
              if face.vertices[i] in vertices:
                vertex = vertices[face.verticesi]
              if not vertex:


def get_bounds(ob):
    bounds = ob.bound_box
    coords = bounds[0]
    min_x = bounds[0][0]
    min_y = bounds[0][1]
    min_z = bounds[0][2]
    max_x = bounds[0][0]
    max_y = bounds[0][1]
    max_z = bounds[0][2]
    for i in range(1,8):
      x = bounds[i][0]
      y = bounds[i][1]
      z = bounds[i][2]
      if x < min_x: min_x = x
      elif x > max_x: max_x = x
      if y < min_y: min_y = y
      elif y > max_y: max_y = y
      if z < min_z: min_z = z
      elif z > max_z: max_z = z

    x = max_x - min_x
    y = max_y - min_y
    z = max_z - min_z

    r = sqrt(x*x+y*y+z*z)
    return ((min_x,min_y,min_z),(max_x,max_y,max_z),(x,y,z),r)

def write_string(data,value):
  data.write(struct.pack("<l",len(value)))
  data.write(bytes(value,encoding="utf8"))

def write_mesh_header(data,objects):
  data.write(b'mi08')
  ((min_x,min_y,min_z),(max_x,max_y,max_z),(x,y,z),radius) = get_bounds(objects[0])
  data.write(struct.pack("<fff",min_x,min_y,min_z))
  data.write(struct.pack("<fff",max_x,max_y,max_z))
  data.write(struct.pack("<fff",x,y,z))
  data.write(struct.pack("<f",radius))
  n_surfaces = 0
  for ob in objects:
    mats = ob.material_slots
    n = len(mats)
    if (n == 0): n = 1
    n_surfaces += n
  print("n_surfaces ",n_surfaces)
  data.write(struct.pack("<l",n_surfaces))

def write_object(data,ob):
  mats = ob.material_slots
  if len(mats) == 0:
    write_string(data,ob.name)
  else:
    write_string(data,ob.name+"_"+mats[0].name)
  return

def save(operator, context, filepath):
  objects = context.selected_objects
  if len(objects) == 0: return {'FINISHED'}
  data = io.BytesIO()
  write_mesh_header(data,objects)
  for ob in objects:
    write_object(data,ob)

  file = open(filepath, "wb")
  file.write(data.getvalue())
  file.close()
  return {'FINISHED'}