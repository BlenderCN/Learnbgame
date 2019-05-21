import bpy
from bpy_extras.mesh_utils import ngon_tessellate
from . import se3

def get_se3_mesh_form_file(filepath):
    file_query = se3.ASCIIFileQuery(filepath)
    
    version = file_query.get_num_value("SE_MESH")
    mesh = se3.Mesh(version)
    
    num_of_layers = file_query.get_num_value("LAYERS")
    file_query.follows_block_begin_decl() #open layers block
    
    processed_layers = 0
    while processed_layers < num_of_layers:
        layer_name = file_query.get_str_value("LAYER_NAME")
        layer_index = file_query.get_long_value("LAYER_INDEX")
        file_query.follows_block_begin_decl() #open layer block
        
        layer = se3.Layer(layer_name, layer_index)
        mesh.layers.append(layer)
        
        num_of_maps = file_query.get_long_value("VERTEX_MAPS")
        file_query.follows_block_begin_decl() #open vertex maps block
        
        processed_maps = 0
        num_of_texcoord_maps = 0
        num_of_weight_maps = 0
        num_of_morph_maps = 0
        while processed_maps < num_of_maps:
            map_type = file_query.get_map_type()
            map_name = file_query.get_map_name()
            file_query.follows_block_begin_decl() #open vertex map block
            
            if map_type == se3.VERTEX_MAP_TYPE_MORPH:
                type_index = num_of_morph_maps
                get_map_elem = file_query.get_morph_elem
                map_is_relative = file_query.get_bool_value("RELATIVE")
                num_of_morph_maps += 1
            elif map_type == se3.VERTEX_MAP_TYPE_TEXCOORD:
                type_index = num_of_texcoord_maps
                get_map_elem = file_query.get_texcoord_elem
                num_of_texcoord_maps += 1
            elif map_type == se3.VERTEX_MAP_TYPE_WEIGHT:
                type_index = num_of_weight_maps
                get_map_elem = file_query.get_weight_elem
                num_of_weight_maps += 1
            
            map = se3.VertexMap(map_type, map_name, map_is_relative)
            map.type_index = type_index
            
            num_of_map_elems = file_query.get_long_value("ELEMENTS")
            file_query.follows_block_begin_decl() # open elements block
            
            processed_elems = 0
            while processed_elems < num_of_map_elems:
                file_query.follows_block_begin_decl() #open element block
                map.elements.append(get_map_elem())
                file_query.follows_block_end_decl() #close element block
                processed_elems += 1
            file_query.follows_block_end_decl() #close elements block
            
            processed_maps += 1
            layer.vertex_maps_append(map)
            file_query.follows_block_end_decl() #close vertex map block
        
        file_query.follows_block_end_decl() #close vertex maps block
        
        
        num_of_verts = file_query.get_long_value("VERTICES")
        file_query.follows_block_begin_decl() #open vertices block
        
        num_of_processed_vertices = 0
        while num_of_processed_vertices < num_of_verts:
            vertex = se3.Vertex()
            
            morph_pointers = vertex.morph_pointers
            weight_pointers = vertex.weight_pointers
            uv_pointers = vertex.uv_pointers
            
            file_query.follows_block_begin_decl() #open vertex block
            num_of_pointers = file_query.get_num_of_values()
            
            num_of_processed_pointers = 0
            is_last_pointer = False
            last_pointer_index = num_of_pointers - 1
            while num_of_processed_pointers < num_of_pointers:
                if num_of_processed_pointers == last_pointer_index:
                    is_last_pointer = True
                
                vertex_data_pointer = file_query.get_vertex_data_pointer(is_last_pointer)
                vertex_map_index = vertex_data_pointer[0]
                vertex_map_type = layer.vertex_maps[vertex_map_index].type
                
                if vertex_map_type == se3.VERTEX_MAP_TYPE_MORPH:
                    morph_pointers.append(vertex_data_pointer)
                elif vertex_map_type == se3.VERTEX_MAP_TYPE_WEIGHT:
                    weight_pointers.append(vertex_data_pointer)
                elif vertex_map_type == se3.VERTEX_MAP_TYPE_TEXCOORD:
                    uv_pointers.append(vertex_data_pointer)
                
                num_of_processed_pointers += 1
            
            layer.vertices.append(vertex)
            file_query.follows_block_end_decl() #close vertex block
            num_of_processed_vertices += 1
        
        file_query.follows_block_end_decl() #close vertices block
        
        num_of_polys = file_query.get_long_value("POLYGONS")
        file_query.follows_block_begin_decl() #open polygons block
        
        processed_polys = 0
        while processed_polys < num_of_polys:
            poly = []
            
            file_query.follows_block_begin_decl() #open polygon block
            
            num_of_values = file_query.get_num_of_values()
            
            processed_values = 0
            is_last_value = False
            last_value_idx = num_of_values - 1
            while processed_values < num_of_values:
                if processed_values == last_value_idx:
                    is_last_value = True
                
                poly.append(file_query.get_vert_idx(is_last_value))
                processed_values += 1
            
            file_query.follows_block_end_decl() #close polygon block
            layer.polygons.append(tuple(poly))
            processed_polys += 1
        
        file_query.follows_block_end_decl() #close polygons block
        
        num_of_poly_maps = file_query.get_long_value("POLYGON_MAPS")
        file_query.follows_block_begin_decl() #open polygon maps block
        
        processed_poly_maps = 0
        while processed_poly_maps < num_of_poly_maps:
            map_type = file_query.get_map_type(False)
            map_name = file_query.get_map_name()
            map_smoothing_angle = file_query.get_num_value("POLYGON_MAP_SMOOTHING_ANGLE")
            polygon_count = file_query.get_long_value("POLYGONS_COUNT")
            file_query.follows_block_begin_decl() #open polygon count block
            
            poly_map = se3.PolygonMap(map_type, map_name, map_smoothing_angle)
            
            processed_poly_idxs = 0
            while processed_poly_idxs < polygon_count:
                poly_map.polygons.append(file_query.get_poly_idx())
                processed_poly_idxs += 1
            
            file_query.follows_block_end_decl() #close polygon count block
            processed_poly_maps += 1
            layer.polygon_maps.append(poly_map)
            layer.surface_maps.append(poly_map)
        
        file_query.follows_block_end_decl() #close polygon maps block
        
        file_query.follows_block_end_decl() #close layer block
        processed_layers += 1
    
    file_query.follows_block_end_decl() #close layers block
    
    return mesh

def get_bl_face(se3_layer, se3_vertex_indices):
    new_indices = []
    
    num_of_texcoord_maps = len(se3_layer.texcoord_maps)
    uvs_data = []
    
    for i in range(num_of_texcoord_maps):
        uvs_data.append([])
    
    se3_texcoord_maps = se3_layer.texcoord_maps
    
    for index in se3_vertex_indices:
        se3_vertex = se3_layer.vertices[index]
        new_indices.append(se3_vertex.basic_morph_pointer[1])
        
        for uv_index, uv_pointer in enumerate(se3_vertex.uv_pointers):
            elem = se3_texcoord_maps[uv_index].elements[uv_pointer[1]]
            uvs_data[uv_index].append(tuple([elem[0], (-elem[1]) + 1]) )
    
    return tuple([tuple(new_indices), uvs_data])

def get_bl_edges(se3_vertex_indices):
    edges = []
    
    num_of_indices = len(se3_vertex_indices)
    last_index = num_of_indices - 1
    
    for current_index in range(num_of_indices):
        next_index = se3_vertex_indices[current_index + 1] if current_index != last_index else se3_vertex_indices[0]
        edges.append((se3_vertex_indices[current_index], next_index))
    
    return edges

def get_bl_fgons(vertices, ngon_face):
    fgon_faces = []
    tessed_faces = ngon_tesselate(vertices, ngon_face)
    
    for tessed_face in tessed_faces:
        fgon_face = []
        for tessed_index in tessed_face:
            fgon_face.append(ngon_face[tessed_index])
        fgon_faces.append(tuple(fgon_face))
    
    return fgon_faces

def edge_not_in(which_edge, edges):
    for edge in edges:
        edge_rev = (edge[0], edge[1])
        if which_edge == edge or which_edge == edge_rev:
            return False
    return True

def get_bl_face_uv_data(real_face, bl_face):
    num_of_uv_tex = len(real_face[1])
    
    uvs_data = []
    
    for i in range(num_of_uv_tex):
        uvs_data.append([])
    
    for vert_index in bl_face:
        real_index = real_face[0].index(vert_index)
        
        for idx, uv_data in enumerate(uvs_data):
            try:
                data = real_face[1][idx][real_index]
            except:
                data = (1,0)
            
            uv_data.append(data)
    
    return uvs_data
 
def read_file(operator, context):
    from mathutils import (Matrix, Vector)
    import math
    
    filepath = operator.filepath
    
    se3_mesh = get_se3_mesh_form_file(filepath)
    
    for se3_layer in se3_mesh.layers:
        fgon_edge_indices = []
        vertices = se3_layer.vertex_maps[0].elements
        edges = []
        
        
        real_faces = []
        se3_surface_map_indices = [0] * len(se3_layer.polygons)
        material_indices = []
        
        for se3_surface_map_index, se3_surface_map in enumerate(se3_layer.surface_maps):
            for polygon_index in se3_surface_map.polygons:
                se3_surface_map_indices[polygon_index] = se3_surface_map_index
        
        edge_index_count = 0
        for se3_polygon_index, se3_polygon in enumerate(se3_layer.polygons):
            se3_num_of_vertex_indices = len(se3_polygon)
            se3_is_tri_or_quad = se3_num_of_vertex_indices <= 4
            
            se3_surface_map_index = se3_surface_map_indices[se3_polygon_index]
            
            if se3_is_tri_or_quad:
                material_indices.append(se3_surface_map_index)
                
                face = get_bl_face(se3_layer, se3_polygon)
                real_faces.append(face)
                
                face_edges = get_bl_edges(face[0])
                
                for face_edge in face_edges:
                    """
                    if edge_not_in(face_edge, edges):
                        edges.append(face_edge)
                        edge_index_count += 1
                    """
                    edges.append(face_edge)
                    edge_index_count += 1
            else:
                ngon_face = get_bl_face(se3_layer, se3_polygon)
                bound_edges = get_bl_edges(ngon_face[0])
                
                fgon_faces = get_bl_fgons(vertices, ngon_face[0])
                
                for fgon_face in fgon_faces:
                    material_indices.append(se3_surface_map_index)
                    
                    real_faces.append(tuple( [fgon_face, get_bl_face_uv_data(ngon_face, fgon_face)] ))
                    face_edges = get_bl_edges(fgon_face)
                    
                    for face_edge in face_edges:
                        is_fgon_edge = edge_not_in(face_edge, bound_edges)

                        edges.append(face_edge)
                        
                        if is_fgon_edge:
                            fgon_edge_indices.append(edge_index_count)
                        
                        edge_index_count += 1
        
        faces = [real_face[0] for real_face in real_faces]
        
        mesh = bpy.data.meshes.new("Test mesh")
        mesh.from_pydata(vertices, edges, faces)
        
        for fgon_edge_index in fgon_edge_indices:
            mesh.edges[fgon_edge_index].is_fgon = True
        
        for uv_index, se3_texcoord_map in enumerate(se3_layer.texcoord_maps):
            uv_tex = mesh.uv_textures.new(se3_texcoord_map.name)
            uv_loop = mesh.uv_layers[0]
            
            for face_index, tex_data in enumerate(uv_tex.data):
                real_tex_face = real_faces[face_index][1][uv_index]
                poly = mesh.polygons[face_index]

                for j, k in enumerate(poly.loop_indices):
                    uv_loop.data[k].uv = real_tex_face[j]
        
        tranf_mat = Matrix(((-1.0, 0.0, 0.0, 0.0),
                            ( 0.0, 0.0, 1.0, 0.0),
                            ( 0.0, 1.0, 0.0, 0.0),
                            ( 0.0, 0.0, 0.0, 1.0)))
        
        obj = bpy.data.objects.new(se3_layer.name, mesh)
        
        scene = context.scene
        scene.objects.link(obj)
        scene.objects.active = obj
        
        obj.select = True
        
        se3_non_basic_morph_map = se3_layer.non_basic_morph_maps
        
        se3_vertices = se3_layer.vertices
        
        if se3_non_basic_morph_map:
            obj.shape_key_add("position")
            
            shape_keys = []
            for se3_other_mmap in se3_non_basic_morph_map:
                shape_keys.append(obj.shape_key_add(se3_other_mmap.name))
            
            for se3_vertex in se3_vertices:
                other_morph_pnts = se3_vertex.non_basic_morph_pointers
                
                if other_morph_pnts:
                    for idx, other_mp in enumerate(other_morph_pnts):
                        type_idx = se3_layer.vertex_maps[other_mp[0]].type_index
                        se3_disp = se3_layer.vertex_maps[other_mp[0]].elements[other_mp[1]]
                        se3_vert = se3_vertex.basic_morph_pointer[1]
                        vert_data = se3_layer.vertex_maps[se3_vertex.basic_morph_pointer[0]].elements[se3_vertex.basic_morph_pointer[1]]
                        
                        shape_keys[type_idx - 1].data[se3_vert].co = Vector(vert_data) + Vector(se3_disp)
        
        se3_weight_maps = se3_layer.weight_maps
        
        if se3_weight_maps:
            vertex_groups = []
            
            for se3_weight_map in se3_weight_maps:
                vertex_groups.append(obj.vertex_groups.new(se3_weight_map.name))
            
            for se3_vertex in se3_vertices:
                se3_weight_pointers = se3_vertex.weight_pointers
                
                if se3_weight_pointers:
                    for se3_weight_pointer in se3_weight_pointers:
                        vertex_index = se3_vertex.basic_morph_pointer[1]
                        se3_vertex_map_index = se3_weight_pointer[0]
                        se3_vertex_weight = se3_layer.vertex_maps[se3_vertex_map_index].elements[se3_weight_pointer[1]]
                        vertex_group_index = se3_layer.vertex_maps[se3_vertex_map_index].type_index
                        vertex_groups[vertex_group_index].add([vertex_index], se3_vertex_weight, 'REPLACE')
        
        if se3_layer.surface_maps:
            materials = []
            
            for se3_surface_map in se3_layer.surface_maps:
                material = bpy.data.materials.new(se3_surface_map.name)
                materials.append(material)
                bpy.ops.object.material_slot_add()
                obj.material_slots[-1].material = material
            
            for face in mesh.polygons:
                face.material_index = material_indices[face.index]
        
        obj.matrix_world = tranf_mat
        bpy.ops.object.transform_apply(rotation=True)
        
        scene.update()
    
    return {'FINISHED'}