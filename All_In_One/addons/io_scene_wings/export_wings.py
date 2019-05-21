import bpy
import struct, time, sys, os, zlib, io
import mathutils
from mathutils.geometry import tesselate_polygon

token_byte = b'a'
token_int32 = b'b'
token_double_str = b'c'
token_atom = b'd'
token_tuple = b'h'
token_array_end = b'j'
token_string = b'k'
token_array_start = b'l'
token_map = b'm'

def write_token(data,token,value):
  data.write(token)
  if token == token_byte:
    data.write(struct.pack(">B",value))
  elif token == token_int32:
    data.write(struct.pack(">L",value))
  elif token == token_double_str:
    pass
  elif token == token_atom:
    data.write(struct.pack(">H",len(value)))
    data.write(value)
  elif token == token_tuple:
    write_tuple(data,value,strip=0)
  elif token == token_array_end:
    pass
  elif token == token_string:
    size = struct.pack(">H",len(value))
    data.write(size)
    data.write(bytes(value,encoding="utf8"))
  elif token == token_array_start:
    write_array(data,value,write_key=0)
  elif token == token_map:
    data.write(struct.pack(">L",len(value)))
    data.write(value)

def write_tuple_header(data,size):
  data.write(token_tuple);
  data.write(struct.pack(">B",size))
  return

def write_array_header(data,size):
  data.write(token_array_start)
  data.write(struct.pack(">L",size))
  return

def write_array_end(data):
  data.write(token_array_end)

def write_array(data,arr,fn=write_token,write_key=1):
  #if write_key > 0: data.write(token_array_start)
  #size = len(lst)
  #data.write(struct.pack(">L",size)
  ##for i in range(len(arr)):
    ##fn(data,arr[i])
  #data.write(token_aray_end)
  return
  


def write_tuple(data,token,write_key=1):
  if write_key > 0: data.write(token_tuple)
  data.write(struct.pack(">B",len(token)))
  for i in range(len(token)): write_token(data,token[i])
  return

#def write_color(data,color):
  #(r,g,b) = color
  #data.write(struct.pack(">BLfff",token_map,12,r,g,b))

#def write_texcoord(data,tex):
  #(u,v)= tex
  #data.write(struct.pack(">BLdd",token_map,16,u,v))

#def write_vertex(data,v)
  #(x,y,z) = v
  #data.write(struct.pack(">BLddd",token_map,24,x,z,-y))

def init_edge_table():
  edge_table = {}
  for i in range(len(edges)):
    v0 = edges[i].vertices[0]
    v1 = edges[i].vertices[1]
    edge_table[(v0,v1)] = (i,[v0,v1,0,0,0,0,0,0],[],[],[],[])

def add_faces_to_edge_table():
  for i in range(len(faces)):
    edges = []
    face = faces[i]
    int right = False
    for j in range(len(face.vertices)-1):
      va = face.vertices[j]
      vb = face.vertices[j+1]
      if (va,vb) in edge_table:
        i, = edge_table[(va,vb)]
        edges append(i)
      elif (vb,va) in edge_table:
        i, = edge_table[(vb,va)]
        edges.append(i)
        
         
    
def add_face_to_edge():
  if (va,vb) in edges:
    edges[(va,vb)].append(face_index)
  else:
    edges[(va,vb)]=[]
    edges[(va,vb)].append(face_index)
  

def faces_by_edge():
  for i in range(len(faces)):
    face = faces[i]
    n_verts = len(verts)
    for i in range(n_verts-1):
      add_face_to_edge()
      
    
def edges_by_vert():
  for i in range(len(edges)):
    edge = edges[i]
    if(i in array)
  
def build_edge(edge_table,va,vb):
  
  
def build_edge_table(me):
  edge_table = {}
  for face in me.faces:
    verts = face.vertices
    n_verts = len(verts)
    for i in range(n_verts-1): build_edge(edge_table,verts[i],verts[i+1])
    build_edge(edge_table,verts[n_verts-1],verts[0])
    
  return

def write_edge_table(data,edge):
  return
  
def write_shapes(data,objects):
  data.write(token_array_start)
  data.write(struct.pack(">L",len(objects)))
  for ob in objects:
    write_shape(data,ob)
  data.write(token_array_end)
  
def write_shape(data,ob):
  print("found object: ",ob.name, " of type ",ob.type)
  if(ob.type != 'MESH'): return
  me = ob.data
  write_tuple_header(data,4)
  write_token(data,token_atom,b'object')
  write_token(data,token_string,ob.name)
  write_tuple_header(data,5)
  write_token(data,token_atom,b'winged')
  
  #print("edgeloops",me.)
  edges = build_edge_table(me)
  #write_array(data,edges,write_edge_table)
  #print("object name: ",ob.name)
  
def save(operator, context, filepath):
  base_name, ext = os.path.split(filepath)
  context_name = [base_name,'','',ext]
  orig_scene = context.scene
  #if bpy.ops.oject.mode_set.poll():
    #bpy.ops.object.mode_set(mode='OBJECT')
  export_scenes = [orig_scene]

  for scene in export_scenes:
    orig_frame = scene.frame_current
  else:
    scene_frame = [orig_frame]

  objects = context.selected_objects
  #objects = scene.objects
  data = io.BytesIO()
  write_tuple_header(data,3)
  write_token(data,token_atom,b'wings')
  write_token(data,token_byte,2)
  write_tuple_header(data,3)
  write_shapes(data,objects)
  
  full_path = ''.join(context_name)
  #data = generate_data()
  data = data.getvalue()
  #dsize = len(data)
  #data = zlib.compress(data,6)
  #fsize = len(data)+5
  #header = b'#!WINGS-1.0\r\n\032\04'
  #misc = 0x8350

  file = open(filepath, "wb")
  #file.write(header)
  #file.write(struct.pack(">L",fsize))
  #file.write(struct.pack(">H",misc))
  #file.write(struct.pack(">L",dsize))
  file.write(data)

  file.close()
  return {'FINISHED'}