import bpy
from ctypes import *

#Converts a single face to 1 or 2 triangles.
def TrianglesFromFace(face):
    n_verts = len(face.vertices)
    t_list = [(face.vertices[0], face.vertices[1], face.vertices[2])]
    m_list = [face.material_index]
    if n_verts == 4:
        t_list.append((face.vertices[0], face.vertices[2], face.vertices[3]))
        m_list.append(face.material_index)
        
    return t_list, m_list

#Converts a texture coordinate face to 1 or 2 triangles.
def UVFromFace(uv_face, n_verts, out_list):
    out_list.append((uv_face.uv1, uv_face.uv2, uv_face.uv3))
    if n_verts == 4:
        out_list.append((uv_face.uv1, uv_face.uv3, uv_face.uv4))

#Converts a vertex color face to 1 or 2 triangles.
def VColorFromFace(vcol_face, n_verts, out_list):
    out_list.append((vcol_face.color1, vcol_face.color2, vcol_face.color3))
    if n_verts == 4:
        out_list.append((vcol_face.color1, vcol_face.color3, vcol_face.color4))

#Flattens a list of points into a ctype array.
def FlattenList(pt_list):
    arr = []
    for pt in pt_list:
        for i in range(3):
            for x in range(len(pt[i])):
                arr.append(pt[i][x])
    
    result = (len(arr)*c_float)()
    for i in range(len(arr)):
        result[i] = arr[i]
    
    return result

#Converts an array of triangles to an array of integer offsets.
def TriangleListToArray(t_list, shader_list):
    t_len = 3*len(t_list)
    s_len = len(t_list)

    t_arr = (t_len*c_int)()
    s_arr = (s_len*c_int)()

    idx = 0
    s_idx = 0
    
    for tri in t_list:
        t_arr[idx] = tri[0]
        t_arr[idx+1] = tri[1]
        t_arr[idx+2] = tri[2]
        s_arr[s_idx] = shader_list[s_idx]

        idx += 3
        s_idx += 1
        
    return t_arr, s_arr

#Generates arrays for transformed vertex coordinates and normals.
def VectorListToArray(v_list, world_tfm, normal_tfm):
    arr_len = 3*len(v_list)
    v_arr = (arr_len*c_float)()
    n_arr = (arr_len*c_float)()
    idx = 0

    #print("Original Vertex 9:", v_list[9].co)
    #print("Transformed Vertex 9:", world_tfm * v_list[9].co)

    for v in v_list:
        t_v = world_tfm * v.co
        t_n = normal_tfm * v.normal

        v_arr[idx] = t_v.x
        n_arr[idx] = t_n.x
        idx += 1

        v_arr[idx] = t_v.y
        n_arr[idx] = t_n.y
        idx += 1

        v_arr[idx] = t_v.z
        n_arr[idx] = t_n.z
        idx += 1

    #print("Final Vertex 9:", v_arr[27], v_arr[28], v_arr[29])

    return v_arr, n_arr

#Applies modifiers to an object and returns the resulting mesh data.
def ObjectToMesh(scene, obj, world_tfm, normal_3x3_tfm, do_preview):
    #convert object to mesh (applying all modifiers)
    mode = 'RENDER'
    if do_preview:
        mode = 'PREVIEW'
    
    bl_mesh = obj.to_mesh(scene, True, mode)

    #load mesh vertices and vertex normals
    v_data, v_norms = VectorListToArray(bl_mesh.vertices, world_tfm, normal_3x3_tfm)
    
    #load triangles
    triangles = []
    shader_list = []
    for face in bl_mesh.tessfaces:
        t_list, shader = TrianglesFromFace(face)
        triangles.extend(t_list)
        shader_list.extend(shader)

    t_data, s_data = TriangleListToArray(triangles, shader_list)

    #Load UV coords

    uv_maps = {}
    for uv_map in bl_mesh.tessface_uv_textures:
        uv = []

        for i in range(len(uv_map.data)):
            uv_face = uv_map.data[i]
            UVFromFace(uv_face, len(bl_mesh.tessfaces[i].vertices), uv)
    
        uv_maps[uv_map.name] = FlattenList(uv)
    

    #Load vertex colors
    vertex_colors = {}
    for vcolor_map in bl_mesh.tessface_vertex_colors:
        vcol = []

        for i in range(len(vcolor_map.data)):
            vcol_face = vcolor_map.data[i]
            VColorFromFace(vcol_face, len(bl_mesh.tessfaces[i].vertices), vcol)

        vertex_colors[vcolor_map.name] = FlattenList(vcol)

    #Free this temporary mesh object
    bpy.data.meshes.remove(bl_mesh)
    
    return {
        'vertices' : v_data,
        'vertex_norms' : v_norms,
        'triangles' : t_data,
        'texcoords' : uv_maps,
        'vertex_colors' : vertex_colors,
        'shaders' : s_data
        }


#Loads an object, applying any transforms.
def LoadMeshObject(scene, obj, is_preview):
    world_transform = obj.matrix_world
    normal_transform = obj.matrix_world.to_3x3()
    normal_transform.invert()
    normal_transform.transpose()

    return ObjectToMesh(scene, obj, world_transform, normal_transform, is_preview)
    
