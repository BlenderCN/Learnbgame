import bpy
import struct,time,sys,os,zlib,io,mathutils
from mathutils.geometry import tesselate_polygon,normal
from io_utils import load_image, unpack_list, unpack_face_list
from math import radians,sin,cos
import os.path

def BPyMesh_ngon(from_data, indices, PREF_FIX_LOOPS=True):
    '''
    Takes a polyline of indices (fgon)
    and returns a list of face indicie lists.
    Designed to be used for importers that need indices for an fgon to create from existing verts.

    from_data: either a mesh, or a list/tuple of vectors.
    indices: a list of indices to use this list is the ordered closed polyline to fill, and can be a subset of the data given.
    PREF_FIX_LOOPS: If this is enabled polylines that use loops to make multiple polylines are delt with correctly.
    '''

    if not set:  # Need sets for this, otherwise do a normal fill.
        PREF_FIX_LOOPS = False

    Vector = mathutils.Vector
    if not indices:
        return []

    #    return []
    def rvec(co):
        return round(co.x, 6), round(co.y, 6), round(co.z, 6)

    def mlen(co):
        return abs(co[0]) + abs(co[1]) + abs(co[2])  # manhatten length of a vector, faster then length

    def vert_treplet(v, i):
        return v, rvec(v), i, mlen(v)

    def ed_key_mlen(v1, v2):
        if v1[3] > v2[3]:
            return v2[1], v1[1]
        else:
            return v1[1], v2[1]

    if not PREF_FIX_LOOPS:
        '''
        Normal single concave loop filling
        '''
        if type(from_data) in (tuple, list):
            verts = [Vector(from_data[i]) for ii, i in enumerate(indices)]
        else:
            verts = [from_data.vertices[i].co for ii, i in enumerate(indices)]

        for i in range(len(verts) - 1, 0, -1):  # same as reversed(xrange(1, len(verts))):
            if verts[i][1] == verts[i - 1][0]:
                verts.pop(i - 1)

        fill = fill_polygon([verts])

    else:
        '''
        Seperate this loop into multiple loops be finding edges that are used twice
        This is used by lightwave LWO files a lot
        '''

        if type(from_data) in (tuple, list):
            verts = [vert_treplet(Vector(from_data[i]), ii) for ii, i in enumerate(indices)]
        else:
            verts = [vert_treplet(from_data.vertices[i].co, ii) for ii, i in enumerate(indices)]

        edges = [(i, i - 1) for i in range(len(verts))]
        if edges:
            edges[0] = (0, len(verts) - 1)

        if not verts:
            return []

        edges_used = set()
        edges_doubles = set()
        # We need to check if any edges are used twice location based.
        for ed in edges:
            edkey = ed_key_mlen(verts[ed[0]], verts[ed[1]])
            if edkey in edges_used:
                edges_doubles.add(edkey)
            else:
                edges_used.add(edkey)

        # Store a list of unconnected loop segments split by double edges.
        # will join later
        loop_segments = []

        v_prev = verts[0]
        context_loop = [v_prev]
        loop_segments = [context_loop]

        for v in verts:
            if v != v_prev:
                # Are we crossing an edge we removed?
                if ed_key_mlen(v, v_prev) in edges_doubles:
                    context_loop = [v]
                    loop_segments.append(context_loop)
                else:
                    if context_loop and context_loop[-1][1] == v[1]:
                        #raise "as"
                        pass
                    else:
                        context_loop.append(v)

                v_prev = v
        # Now join loop segments

        def join_seg(s1, s2):
            if s2[-1][1] == s1[0][1]:
                s1, s2 = s2, s1
            elif s1[-1][1] == s2[0][1]:
                pass
            else:
                return False

            # If were stuill here s1 and s2 are 2 segments in the same polyline
            s1.pop()  # remove the last vert from s1
            s1.extend(s2)  # add segment 2 to segment 1

            if s1[0][1] == s1[-1][1]:  # remove endpoints double
                s1.pop()

            s2[:] = []  # Empty this segment s2 so we dont use it again.
            return True

        joining_segments = True
        while joining_segments:
            joining_segments = False
            segcount = len(loop_segments)

            for j in range(segcount - 1, -1, -1):  # reversed(range(segcount)):
                seg_j = loop_segments[j]
                if seg_j:
                    for k in range(j - 1, -1, -1):  # reversed(range(j)):
                        if not seg_j:
                            break
                        seg_k = loop_segments[k]

                        if seg_k and join_seg(seg_j, seg_k):
                            joining_segments = True

        loop_list = loop_segments

        for verts in loop_list:
            while verts and verts[0][1] == verts[-1][1]:
                verts.pop()

        loop_list = [verts for verts in loop_list if len(verts) > 2]
        # DONE DEALING WITH LOOP FIXING

        # vert mapping
        vert_map = [None] * len(indices)
        ii = 0
        for verts in loop_list:
            if len(verts) > 2:
                for i, vert in enumerate(verts):
                    vert_map[i + ii] = vert[2]
                ii += len(verts)

        fill = tesselate_polygon([[v[0] for v in loop] for loop in loop_list])
        #draw_loops(loop_list)
        #raise 'done loop'
        # map to original indices
        fill = [[vert_map[i] for i in reversed(f)] for f in fill]

    if not fill:
        print('Warning Cannot scanfill, fallback on a triangle fan.')
        fill = [[0, i - 1, i] for i in range(2, len(indices))]
    else:
        # Use real scanfill.
        # See if its flipped the wrong way.
        flip = None
        for fi in fill:
            if flip != None:
                break
            for i, vi in enumerate(fi):
                if vi == 0 and fi[i - 1] == 1:
                    flip = False
                    break
                elif vi == 1 and fi[i - 1] == 0:
                    flip = True
                    break

        if not flip:
            for i, fi in enumerate(fill):
                fill[i] = tuple([ii for ii in reversed(fi)])

    return fill

# ------------- UTIL FUNCTION ----------------#

token_byte = b'a'
token_int32 = b'b'
token_double_str = b'c'
token_atom = b'd'
token_tuple = b'h'
token_array_end = b'j'
token_string = b'k'
token_array_start = b'l'
token_map = b'm'

# read erlang binary data
#========================
def skip_token(data):
  token = data.read(1)
  if token == token_byte:
    data.read(1)
  elif token == token_int32:
    data.read(4)
  elif token == token_double_str:
    data.read(31)
  elif token == token_atom:
    size, = struct.unpack(">H",data.read(2))
    data.read(size)
  elif token == token_tuple:
    skip_tuple(data,strip=0)
  elif token == token_array_end:
    return
  elif token == token_string:
    size, = struct.unpack(">H",data.read(2))
    data.read(size)
  elif token == token_array_start:
    skip_array(data,strip=0)
  elif token == token_map:
    size, = struct.unpack(">L",data.read(4))
    data.read(size)
  return

def skip_tuple(data,strip=1):
  if strip > 0: data.read(strip)
  size, = struct.unpack(">B",data.read(1))
  for i in range(size):
    skip_token(data)
  return

def skip_array(data,strip=1):
  if strip > 0:
    token = data.read(1)
    if token == token_array_end:
      return
  size, = struct.unpack(">L",data.read(4))
  #print("skipping: array size, ",size)
  for i in range(size):
    skip_token(data)
  data.read(1)
  return

def read_token(data):
  token = data.read(1)
  #print("token",token)
  if token == token_byte:
    out, = struct.unpack(">B",data.read(1))
    return out
  elif token == token_int32:
    out, = struct.unpack(">L",data.read(4))
    return out
  elif token == token_double_str:
    double_str = str(data.read(31),encoding="utf8")
    double_str = double_str.rstrip("\x00")
    out = float(double_str)
    print ("double ", out)
    return out
  elif token == token_atom:
    size, = struct.unpack(">H",data.read(2))
    out = data.read(size)
    return out
  elif token == token_tuple:
    out = read_tuple(data,strip=0)
    return out
  elif token == token_array_end:
    return []
  elif token == token_string:
    size, = struct.unpack(">H",data.read(2))
    out = data.read(size)
    print("out,",out)
    return str(out,encoding="utf8")
  elif token == token_array_start:
    out = read_array(data,strip=0)
    return out
  elif token == token_map:
    size, = struct.unpack(">L",data.read(4))
    out = data.read(size)
    return out
  return

def read_tuple(data,strip=1):
  if strip > 0: data.read(strip)

  size, = struct.unpack(">B",data.read(1))
  if size == 1:
    return read_token(data)
  elif size == 2:
    return (read_token(data),read_token(data))
  elif size == 3:
    return (read_token(data),read_token(data),read_token(data))
  elif size == 4:
    return (read_token(data),read_token(data),read_token(data),read_token(data))
  else :
    out = []
    for i in range(size):
      out.append(read_token(data))
    return out

def read_array(data,fn=read_token,strip=1):
  out = []
  if strip > 0:
    token = data.read(1)
    if token == token_array_end : #empty array
      return out
    elif token == token_string: #compressed array
      size, = struct.unpack(">H",data.read(2))
      for i in range(size):
        d, = struct.unpack(">B",data.read(1))
        out.append(d)
      return out

  size, = struct.unpack(">L",data.read(4))
  #print("array size ",size)
  for i in range(size):
    out.append(fn(data))
  data.read(1)
  return out

#def foreach_in_array(data,fn=read_token,strip=1):
  #token = data.read(1)
  #if token == token_array_end: return
  #size, = struct.unpack(">L",data.read(4))
  #for i in range(size): fn(data)
  #data.read(1)
  #return

def read_key(data):
  read_tuple_header(data)
  attrib_type = read_token(data)
  print("attrib_type, ",attrib_type)
  t = read_token(data)
  return (attrib_type,t)

def read_double_from_string(data):
  data.read(1)
  bd = data.read(30)
  double_str = str(bd,encoding="utf8")
  double_str = double_str.rstrip("\x00")
  return float(double_str)

def read_array_as_dict(data,fn=read_key,strip=1):
  out = {}
  if strip > 0:
    token = data.read(1)
    #print ("token: ",token)
    if token == token_array_end:
      return out
  size, = struct.unpack(">L",data.read(4))
  #print("keys: ",size)
  for i in range(size):
    k,d = fn(data)
    out[k] = d
  data.read(1)
  return out

def read_tuple_header(data):
    misc,size = struct.unpack(">BB", data.read(2))
    return size

# read specific mesh data
# =======================

def read_edge(data):
  read_tuple_header(data)
  edge_type = read_token(data)
  if edge_type == b'edge':
    e = []
    for i in range(8):
      token = data.read(1)
      if token == token_byte:
        entry, = struct.unpack(">B",data.read(1))
        e.append(entry)
      elif token == token_int32:
        entry, = struct.unpack(">L",data.read(4))
        e.append(entry)
    return (edge_type,e)
  elif edge_type == b'uv_lt':
    return (edge_type,read_texcoord(data))
  elif edge_type == b'uv_rt':
    return (edge_type,read_texcoord(data))
  elif edge_type == b'color_lt':
    return (edge_type,read_color(data))
  elif edge_type == b'color_rt':
    return (edge_type,read_color(data))

def read_texcoord(data):
  data.read(5)
  u,v = struct.unpack(">dd",data.read(16))
  return (u,v)

def read_color(data):
  data.read(5)
  r,g,b = struct.unpack(">fff",data.read(12))
  return (r,g,b)

def read_vertex_array(data):
  out = read_array(data,read_vertex)
  return out[0]

def read_vertex(data):
  data.read(5)
  x,y,z = struct.unpack(">ddd",data.read(24))
  return (x,-z,y)



# convert edge data to face data
# ===============================

def build_face_table(edge_table):
  face_table = {}
  for i in range(len(edge_table)):
    edge = edge_table[i][b'edge']
    lf = edge[2]
    rf = edge[3]
    face_table[lf] = i
    face_table[rf] = i
  return face_table

def build_vert_table(edge_table):
  vert_table = {}
  for i in range(len(edge_table)):
    edge = edge_table[i][b'edge']
    lf = edge[0]
    rf = edge[1]
    vert_table[vs]=i
    vert_table[ve]=i
  return vert_table

# grab a tri or a quad from what would be the mirror face

def get_mirror_face(fvs,verts):
   if len(fvs) > 4:
     ngons = BPyMesh_ngon(verts,fvs)
     (i0,i1,i2) = ngons[int(len(ngons)/2)]
     f = [fvs[i0],fvs[i1],fvs[i2]]
   else :
     f = fvs
   return f

def sort_edge(v0,v1):
  if v0 >v1: return (v1,v0)
  return (v0,v1)

def add_edge_if_new(face,v0,v1,edges,new_edges,hide_edges):
  print ("new edges: ", new_edges)
  (v0,v1) = sort_edge(v0,v1)
  f0 = face[v0]
  f1 = face[v1]
  for (a,b) in new_edges:
    print("f1 ",f0," a ",a," f2 ",f1," b ",b)
    if f0 == a and f1 == b: return
  if v0 + 1 == v1: return
  if v1 == len(face)-1 and v0 == 0: return
  new_edges.append((f0,f1))
  hide_edges.append(len(edges))
  edges.append((f0,f1))

def faces_from_edge_table(edge_table,verts,props,face_props,edges,use_cols=0,use_uvs=0):
  face_table = build_face_table(edge_table)
  faces = []
  face_cols = []
  face_uvs = []
  hide_edges = []
  mirror_face = -1
  extra_faces = 0
  mirror_face_out = None
  holes = None
  if b'holes' in props:
    holes = props[b'holes']

  if b'mirror_face' in props :
    mirror_face = props[b'mirror_face']

  for i in range(len(face_table)):

    fvs = []
    fcs = []
    fuvs = []
    current = face_table[i]

    while (True):
      edge_set = edge_table[current]
      edge = edge_set[b'edge']
      if i == edge[3]: #right face
        next_edge = edge[7]
        fvs.append(edge[0])
        if b'color_rt' in edge_set:
          fcs.append(edge_set[b'color_rt'])
        if b'uv_rt' in edge_set:
          fuvs.append(edge_set[b'uv_rt'])
      else: # left face
        next_edge = edge[5]
        fvs.append(edge[1])
        if b'color_lt' in edge_set:
          fcs.append(edge_set[b'color_lt'])
        if b'uv_lt' in edge_set:
          fuvs.append(edge_set[b'uv_lt'])
      current = next_edge
      if current == face_table[i]: break

    fvs.reverse()
    fvs.insert(0,fvs.pop())
    fcs.reverse()
    fuvs.reverse()

    if i ==  mirror_face :
      del face_props[i+extra_faces]
      mirror_face_out = get_mirror_face(fvs,verts)
      continue
    elif holes != None:
      if holes.count(i):
        index = holes.index(i)
        del holes[index]
        del face_props[i+extra_faces]
        continue

    if len(fvs) > 4: #ngon
      ngons = BPyMesh_ngon(verts,fvs)
      face_prop = face_props.pop(i)
      new_edges = []
      for ngon in ngons:
        (v0,v1,v2) = tuple(ngon)
        add_edge_if_new(fvs,v0,v1,edges,new_edges,hide_edges)
        add_edge_if_new(fvs,v1,v2,edges,new_edges,hide_edges)
        add_edge_if_new(fvs,v2,v0,edges,new_edges,hide_edges)
        faces.append([fvs[v0],fvs[v1],fvs[v2]])
        if len(fcs)>0: face_cols.append([fcs[v0],fcs[v1],fcs[v2]])
        if len(fuvs)>0: face_uvs.append([fuvs[v0],fuvs[v1],fuvs[v2]])
        face_props.insert(i,face_prop)
      extra_faces += len(ngons)-1
    else:
      faces.append(fvs)
      face_cols.append(fcs)
      face_uvs.append(fuvs)
  return faces,face_cols,face_uvs,hide_edges,mirror_face_out

# read objects from erlang data
# =============================

def read_shapes(data,use_subsurf,use_hidden):
  token = data.read(1)
  if token == token_array_end: return
  size, = struct.unpack(">L",data.read(4))
  for i in range(size): read_shape(data,use_subsurf,use_hidden)
  data.read(1)
  return

def read_shape(data,use_subsurf,use_hidden):
  read_tuple_header(data)
  skip_token(data) #object
  shape_name = read_token(data)
  print ("shape: ",shape_name)
  read_tuple_header(data)
  skip_token(data) #winged

  #read mesh data
  edge_table = read_array(data,read_edge_set)
  print("edge_table: ",edge_table)
  face_props = read_array(data,read_array_as_dict)
  print("face_mats: ",face_props)
  verts = read_array(data,read_vertex_array)
  print("verts: ",verts)
  hard_edges = read_array(data)
  print("hard_edges: ",hard_edges)
  props = read_array_as_dict(data,read_prop)
  print("props: ",props)

  # if we are ignoring hidden objects
  # we can stop now
  if use_hidden == True and b'state' in props:
    state = props[b'state']
    if state == b'hidden' or state == b'hidden_locked':
      return

  # make a list of edges with just the vert part
  # of the list eg [(v0,v1),(v0,v1)...]
  edges = get_edges(edge_table)
  print("edges: ",edges)

  # build a list of faces from edge data,
  # also vertex colors, face_uvs and a few other bits
  # and pieces
  faces,face_cols,face_uvs,hide_edges,mirror_face = faces_from_edge_table(edge_table,verts,props,face_props,edges)
  print("edges: ",edges)
  print("faces: ",faces)
  print("colors: ",face_cols)
  print("uvs: ",face_uvs)
  print("hide edges: ",hide_edges)

  #create bleneder mesh
  me = bpy.data.meshes.new(shape_name)
  ob = bpy.data.objects.new(shape_name,me)
  bpy.context.scene.objects.link(ob)
  me.vertices.add(len(verts))
  me.vertices.foreach_set("co", unpack_list(verts))
  me.faces.add(len(faces))
  me.faces.foreach_set("vertices_raw",unpack_face_list(faces))
  me.edges.add(len(edges))
  me.edges.foreach_set("vertices",unpack_list(edges))
  me.validate()
 # me.update(calc_edges=True)

  #add edges to blender mesh, mark special edges
  #b_edges = me.edges
  #for i in range(len(b_edges)):
    #(v0,v1) = b_edges[i].vertices
    #print("edge ", i, " ",v0,"-",v1)

  build_hard_edges(me,hard_edges)
  hide_fgon_edges(me,hide_edges)

  if len(face_cols) > 0: build_face_colors(me,face_cols)
  if len(face_uvs) > 0: build_face_uvs(me,face_uvs)
  for i in range(len(faces)): me.faces[i].use_smooth = True
  add_material_indices(me,face_props)

  mods = ob.modifiers
  if use_subsurf == True:
    mod = mods.new("subsurf",'SUBSURF')
    mod.levels = 2
  if  mirror_face != None:
    pivot = build_mirror_pivot(mirror_face,verts,ob)
    mirror = mods.new("mirror",'MIRROR')
    mirror.mirror_object = pivot
    mirror.use_clip = True
    mirror.use_mirror_merge = True
    #ob.parent = pivot

  if b'state' in props:
    state = props[b'state']
    if state == b'locked' or state == b'hidden_locked':
      ob.hide_select = True
    if state == b'hidden' or state == b'hidden_locked':
      ob.hide = True
      ob.hide_render = True
  if b'plugin_states' in props:
    plugin_states = props[b'plugin_states']
    if b'wings_shape' in plugin_states:
      folder = plugin_states[b'wings_shape']
      if folder != b'no_folder':
        dummy = bpy.data.objects.get(folder)
        if dummy == None:
          dummy = bpy.data.objects.new(folder,None)
          bpy.context.scene.objects.link(dummy)
        ob.parent = dummy

def read_edge_set(data):
  return read_array_as_dict(data,read_edge)


# build mesh in blender functions
# ===============================

def build_hard_edges(me,hard_edges):
  for hard_edge in hard_edges:
    edge = me.edges[hard_edge]
    edge.crease = 1.0

def hide_fgon_edges(me,hide_edges):
  for hidden_edge in hide_edges:
    edge = me.edges[hidden_edge]
    edge.is_fgon = True

def build_face_colors(me,face_cols):
  blender_me_vcols = me.vertex_colors.new()
  for i in range(len(face_cols)):
    source_vcol = face_cols[i]
    if len(source_vcol) == 0: continue
    blender_vcol_face = blender_me_vcols.data[i]
    blender_vcol_face.color1 = source_vcol[0]
    blender_vcol_face.color2 = source_vcol[1]
    blender_vcol_face.color3 = source_vcol[2]
    if len(source_vcol) > 3:
      blender_vcol_face.color4 = source_vcol[3]

def build_face_uvs(me,face_uvs):
  blender_me_uvs = me.uv_textures.new()
  for i in range(len(face_uvs)):
    source_uvs = face_uvs[i]
    if len(source_uvs) == 0: continue
    blender_uv_face = blender_me_uvs.data[i]
    blender_uv_face.uv1 = source_uvs[0]
    blender_uv_face.uv2 = source_uvs[1]
    blender_uv_face.uv3 = source_uvs[2]
    if len(source_uvs) > 3:
      blender_uv_face.uv4 = source_uvs[3]

def build_mirror_pivot(f,verts,ob):
  v0 = mathutils.Vector(verts[f[0]])
  v1 = mathutils.Vector(verts[f[1]])
  v2 = mathutils.Vector(verts[f[2]])
  if len(f) == 4:
    v3 = mathutils.Vector(verts[f[3]])
    norm = normal(v0,v1,v2,v3)
  else:
    v3 = None
    norm = normal(v0,v1,v2)
  rot = norm.to_track_quat('X','Z')
  r = rot.to_euler('XYZ')
  p0 = v0.lerp(v1,0.5)
  if v3 == None: p1 = v2
  else: p1 = v2.lerp(v3,0.5)
  center = p0.lerp(p1,0.5)

  dummy = bpy.data.objects.new(ob.name + "_mirror_pivot",None)
  dummy.location = center.to_tuple()
  print("ROTATING TO ",r.x," ",r.y," ",r.z)
  dummy.rotation_euler = (r.x,r.y,r.z)
  bpy.context.scene.objects.link(dummy)
  return dummy

def get_face_material(facemat):
  if b'material' in facemat: return facemat[b'material']
  else: return b'default'

def add_material_indices(me,face_props):
  mats = {}
  bfaces = me.faces
  for i in range (len(bfaces)):
    blender_face = bfaces[i]
    face_mat = get_face_material(face_props[i])
    if face_mat in mats:
      index = mats[face_mat]
    else:
      mat_name = str(face_mat,encoding="utf8")
      mat = bpy.data.materials.get(mat_name)
      if mat == None: mat = bpy.data.materials.new(mat_name)
      me.materials.append(mat)
      index = len(mats)
      mats[face_mat]=index
    blender_face.material_index = index

def get_edges(edge_table):
  edges = []
  for e in edge_table:
    edge = e[b'edge']
    edges.append((edge[0],edge[1]))
  return edges

# property related functions
# ==========================

def read_prop(data):
  read_tuple_header(data)
  prop_type = read_token(data)
  print ("prop type: ",prop_type)
  if prop_type == b'scene_prefs':
    out = read_array(data)
  elif prop_type == b'plugin_states':
    out = read_array_as_dict(data)
  elif prop_type == b'current_view':
    out = read_token(data)
  elif prop_type == b'views':
    out = read_array(data,read_view)
  elif prop_type == b'images':
    out = read_array(data,read_image)
  elif prop_type == b'lights':
    out = read_array(data,read_light)
  elif prop_type == b'holes':
    out = read_array(data)
  elif prop_type == b'selection':
    skip_token(data)
    out = []
  else :
    out = read_token(data)
  return (prop_type,out)

def read_view(data):
  read_tuple_header(data)
  skip_token(data) #view
  v_props = read_array_as_dict(data)
  return v_props

def build_cameras(views):
  for view in views:
    camera_name = view[b'name']
    cam = bpy.data.cameras.new(camera_name)
    ob = bpy.data.objects.new(camera_name,cam)
    bpy.context.scene.objects.link(ob)
    r = view[b'distance_to_aim']
    az = radians(view[b'azimuth'])
    el = radians(view[b'elevation'])
    (track_x,track_y)=  view[b'tracking'] #TODO figure out what this does cameras will probably not be positioned properly until
    (x,y,z) = view[b'aim' ]
    cx = r*sin(el)*cos(az)
    cy = r*sin(el)*sin(az)
    cz = r*cos(el)
    ob.location = (cx + x,cy - z,cz + y)
    dummy = bpy.data.objects.new(cam.name + "_aim", None)
    dummy.location = (x,-z,y)
    dummy.scale = (0.2, 0.2, 0.2)
    bpy.context.scene.objects.link(dummy)
    aim = ob.constraints.new('TRACK_TO')
    aim.target = dummy
    aim.track_axis = 'TRACK_NEGATIVE_Z'
    aim.up_axis = 'UP_Y'
    ob.parent = dummy
    cam.angle = radians(view[b'fov'])
    cam.clip_start = view[b'hither']
    cam.clip_end = view[b'yon']

def read_image(data):
  read_tuple_header(data)
  img_index = read_token(data)
  out = read_array_as_dict(data)
  return (img_index,out)

def read_light(data):
  read_tuple_header(data)
  light_name = read_token(data)
  print ("light name::: ",light_name)
  out = read_array_as_dict(data,read_light_section)
  return (light_name,out)

def read_light_section(data):
  read_tuple_header(data)
  attrib_name = read_token(data)
  print ("lightattrib name: ",attrib_name)
  if attrib_name == b'opengl':
    out = read_array_as_dict(data)
  else: out = read_token(data)
  return (attrib_name,out)

def build_lamps(lights):
  #print("lights ",lights)
  for (lamp_name,light) in lights:
    print("light ",light)
    if b'opengl' in light == False: continue
    props = light[b'opengl']
    lamp_type = props[b'type']
    if lamp_type == b'infinite':
      lamp = bpy.data.lamps.new(lamp_name,'SUN')
      set_lamp_common_props(lamp,props)
    elif lamp_type == b'point':
      lamp = bpy.data.lamps.new(lamp_name,'POINT')
      set_lamp_common_props(lamp,props)
      if b'linear_attenuation' in props:
        lamp.linear_attenuation = props[b'linear_attenuation']
      if b'quadratic_attenuation' in props:
        lamp.quadratic_attenuation = props[b'quadratic_attenuation']
    elif lamp_type == b'spot':
      lamp = bpy.data.lamps.new(lamp_name,'SPOT')
      set_lamp_common_props(lamp,props)
      if b'linear_attenuation' in props:
        lamp.linear_attenuation = props[b'linear_attenuation']
      if b'quadratic_attenuation' in props:
        lamp.quadratic_attenuation = props[b'quadratic_attenuation']
      if b'cone_angle' in props:
        lamp.spot_size = radians(props[b'cone_angle'])
      if b'spot_exponent' in props:
        lamp.spot_blend = props[b'spot_exponent']
    elif lamp_type == b'area':
      lamp = bpy.data.lamps.new(lamp_name,'AREA')
      set_lamp_common_props(lamp,props)
      if b'mesh' in props:
        print ("MESH >>>> ",props[b'mesh'])

def set_lamp_common_props(light,props):
  ob = bpy.data.objects.new(light.name,light)
  bpy.context.scene.objects.link(ob)
  #print ("light props: ",props)
  if b'position' in props:
    (x,y,z) = props[b'position']
    ob.location = (x,-z,y)
  if b'aim_point' in props and props[b'type'] != b'point': #point lights don't need to aim
    dummy = bpy.data.objects.new(light.name + "_aim", None)
    (x,y,z) = props[b'aim_point']
    dummy.location = (x,-z,y)
    dummy.scale = (0.2, 0.2, 0.2)
    bpy.context.scene.objects.link(dummy)
    aim = ob.constraints.new('TRACK_TO')
    aim.target = dummy
    aim.track_axis = 'TRACK_NEGATIVE_Z'
    aim.up_axis = 'UP_Y'
    ob.parent = dummy
  if b'diffuse' in props:
    (r,g,b,a) = props[b'diffuse']
    light.color = (r,g,b)
  if b'ambient' in props:
    (r,g,b,a) = props[b'ambient']
  if b'specular' in props:
    (r,g,b,a) = props[b'specular']

# materials related functions
# ===========================

def read_material_part(data):
  read_tuple_header(data)
  attrib_type = read_token(data)
  if attrib_type == b'opengl':
    t = read_array_as_dict(data)
  else:
    t = read_token(data)
  return (attrib_type,t)

def read_material(data):
  read_tuple_header(data)
  mat_name, = read_token(data),
  print ("mat name: ",mat_name)
  name_str = str(mat_name,encoding="utf8")
  mats = read_array_as_dict(data,read_material_part)
  print ("mats: ", mats)
  material = bpy.data.materials.get(name_str)
  if material == None:
    return (mat_name,[])
  m_attribs = mats[b'opengl']
  if b'diffuse' in m_attribs :
    (r,g,b,a) = m_attribs[b'diffuse']
    material.diffuse_color = (r,g,b)
  if b'specular' in m_attribs :
    (r,g,b,a) = m_attribs[b'specular']
    material.specular_color = (r,g,b)
  if b'ambient' in m_attribs :
    (r,g,b,a) = m_attribs[b'ambient']
    material.ambient = (r+g+b+a)/4.0
  if b'emission' in m_attribs :
    (r,g,b,a) = m_attribs[b'emission']
    material.emit = (r+g+b+a)/4.0
  if b'shininess' in m_attribs :
    s = m_attribs[b'shininess']
    material.specular_hardness = int(s*511)
  return (mat_name,mats[b'maps'])

def add_textures(images,mappings,current_filepath):
  for (index,image) in images:

    if b'filename' in image:
      texture = bpy.data.textures.get(image[b'name'])
      if texture == None:
        texture = bpy.data.textures.new(name=image[b'name'], type='IMAGE')
      filenpath = image[b'filename']
      (dirname,filename) = os.path.split(filenpath)
      print ("filename: ",filename," dirname: ",dirname)
      if os.path.isfile(filenpath):
        texture.image = load_image(filename,dirname)
      else:
        (current_dir,cfilename) = os.path.split(current_filepath)
        if os.path.isfile(current_dir + filename):
          texture.image = load_image(current_dir,filename)
        else: continue

      has_data = texture.image.has_data
      mapkeys = mappings.keys()
      for mapkey in mapkeys:
        print ("mat name: ",mapkey)
        mat = bpy.data.materials.get(str(mapkey,encoding="utf8"))
        if mat == None: continue
        mapping = mappings[mapkey]
        for i in range(len(mapping)):
          (channel,tex_index)=mapping[i]
          if tex_index == index:
            #print ("channel:",channel)
            if channel == b'diffuse':
              if has_data and image.depth == 32:
                # Image has alpha
                mtex = mat.texture_slots.add()
                mtex.texture = texture
                mtex.texture_coords = 'UV'
                mtex.use_map_color_diffuse = True
                mtex.use_map_alpha = True

                texture.use_mipmap = True
                texture.use_interpolation = True
                texture.use_alpha = True
                mat.use_transparency = True
                mat.alpha = 0.0
              else:
                #print("adding non alpha texture")
                mtex = mat.texture_slots.add()
                mtex.texture = texture
                mtex.texture_coords = 'UV'
                mtex.use_map_color_diffuse = True
            elif channel == b'gloss':
              mtex = mat.texture_slots.add()
              mtex.texture = texture
              mtex.texture_coords = 'UV'
              mtex.use_map_specular = True
            elif channel == b'bump':
              mtex = mat.texture_slots.add()
              mtex.texture = texture
              mtex.texture_coords = 'UV'
              mtex.use_map_normal = True
            elif channel == b'normal':
              mtex = mat.texture_slots.add()
              mtex.texture = texture
              mtex.texture_coords = 'UV'
              mtex.use_map_normal = True

# core functions
# ==============================

def load_wings_file(filepath):
  file = open(filepath,"rb")
  header = file.read(15)
  fsize, = struct.unpack(">L", file.read(4))
  misc, = struct.unpack(">H", file.read(2))
  dsize, = struct.unpack(">L",file.read(4))
  data = file.read(fsize-6)
  file.close()
  data = zlib.decompress(data)
  file = open(filepath + ".dump","wb")
  file.write(data)
  file.close()
  return io.BytesIO(data)

def read_wings_header(data):
  read_tuple_header(data)
  skip_token(data)
  version = read_token(data)
  read_tuple_header(data)
  return version

def load(operator, context, filepath="",use_lamps=True,use_cameras=False,use_subsurfs=True,use_hidden=True):
  data = load_wings_file(filepath)
  version = read_wings_header(data)
  print ("version",version)
  read_shapes(data,use_subsurfs,use_hidden)
  matmaps = read_array_as_dict(data,read_material)
  print ("matmaps: ",matmaps)
  props = read_array_as_dict(data,read_prop)
  #print ("Props: ",props)
  if use_lamps == True and b'lights' in props:
    build_lamps(props[b'lights'])
  if b'images' in props: add_textures(props[b'images'],matmaps,filepath)
  return {'FINISHED'}
