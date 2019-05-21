import re
import bpy
from . import se3
from . import blutils

def transform_data_to_se3_vec(vec):
    return (-vec.x, vec.z, vec.y)

def write_file(filepath, context):
    active_object = context.active_object
    selected_objects = list(context.selected_objects)
    
    if not selected_objects:
        selected_objects.append(active_object)
    
    amf = open(filepath, 'w')
    
    se3_mesh = se3.Mesh(version = 1.01)
    
    for se3_layer_index, object in enumerate(selected_objects):
        mesh = object.data
        non_basis_shape_keys = blutils.get_non_basis_keys(mesh)
        vertex_groups = object.vertex_groups
        
        has_uv_textures = False
        has_materials = False
        
        se3_layer_name = mesh.name
        se3_layer = se3.Layer(se3_layer_name, se3_layer_index)
        se3_mesh.layers.append(se3_layer)
        
        se3_basic_morph_map = se3.VertexMap(se3.VERTEX_MAP_TYPE_MORPH, "position")
        se3_layer.basic_morph_map = se3_basic_morph_map
        se3_layer.vertex_maps.append(se3_basic_morph_map)
        
        if non_basis_shape_keys:
            has_non_basis_non_basis_shape_keys = True
            
            se3_non_basic_morph_maps = []
            se3_non_basic_mmap_elem_count = [0] * len(non_basis_shape_keys)
            
            for shape_key in non_basis_shape_keys:
                se3_map_name = shape_key.name

                if re.match("^position", se3_map_name, re.IGNORECASE):
                    se3_map_name = "_" + se3_map_name
                
                se3_morph_map = se3.VertexMap(se3.VERTEX_MAP_TYPE_MORPH, se3_map_name)
                se3_non_basic_morph_maps.append(se3_morph_map)
            
            se3_layer.non_basic_morph_maps.extend(se3_non_basic_morph_maps)
            se3_layer.vertex_maps.extend(se3_non_basic_morph_maps)
        else:
            has_non_basis_non_basis_shape_keys = False
        
        if vertex_groups:
            has_vertex_groups = True
            
            se3_weight_maps = []
            se3_wmap_elem_count = [0] * len(vertex_groups)
            
            for vertex_group in vertex_groups:
                se3_weight_map = se3.VertexMap(se3.VERTEX_MAP_TYPE_WEIGHT, vertex_group.name)
                se3_weight_maps.append(se3_weight_map)
            
            se3_layer.weight_maps.extend(se3_weight_maps)
            se3_layer.vertex_maps.extend(se3_weight_maps)
        else:
            has_vertex_groups = False
        
        mesh.update(calc_tessface=True)
        uv_textures = mesh.tessface_uv_textures
        
        if uv_textures:
            has_uv_textures = True
            
            se3_texcoord_maps = []
            se3_texcoord_map_elem_count = [0] * len(uv_textures)
            
            for uv_texure in uv_textures:
                se3_texcoord_map = se3.VertexMap(se3.VERTEX_MAP_TYPE_TEXCOORD, uv_texure.name)
                se3_texcoord_maps.append(se3_texcoord_map)
            
            se3_layer.texcoord_maps.extend(se3_texcoord_maps)
            se3_layer.vertex_maps.extend(se3_texcoord_maps)
        
        se3_vertices = se3_layer.vertices
        
        se3_building_vertices = []
        
        
        for vertex in mesh.vertices:
            vertex_index = vertex.index
            vertex_co = vertex.co
            
            se3_building_vertex = se3.BuildingVertex(len(uv_textures))
            
            se3_point = transform_data_to_se3_vec(vertex_co)
            se3_basic_morph_map.elements.append(se3_point)
            
            se3_vertex = se3.Vertex(vertex_index)
            se3_vertices.append(se3_vertex)
            
            se3_vertex_map_index = 0
            
            se3_vertex.morph_pointers.append((se3_vertex_map_index, vertex_index))
            
            if has_non_basis_non_basis_shape_keys:
                for j, shape_key in enumerate(non_basis_shape_keys):
                    relative_key = shape_key.relative_key
                    vertex_group = shape_key.vertex_group
                    
                    vertex_co = relative_key.data[vertex_index].co
                    key_vertex_co = shape_key.data[vertex_index].co
                    
                    weight = 1
                    
                    if vertex_group:
                        try:
                            weight = object.vertex_groups[vertex_group].weight(vertex_index)
                        except:
                            weight = 0
                    
                    se3_vertex_map_index += 1
                    
                    if key_vertex_co != vertex_co:
                        disp_vec = (key_vertex_co - vertex_co) * weight
                        
                        se3_disp_vec = transform_data_to_se3_vec(disp_vec)
                        
                        se3_non_basic_morph_maps[j].elements.append(se3_disp_vec)
                        
                        se3_vertex.morph_pointers.append((se3_vertex_map_index, se3_non_basic_mmap_elem_count[j]))
                        se3_non_basic_mmap_elem_count[j] += 1
            
            if has_vertex_groups:
                for j, group in enumerate(object.vertex_groups):
                    se3_vertex_map_index += 1
                    try:
                        se3_weight = group.weight(vertex_index)
                        
                        se3_weight_maps[j].elements.append(se3_weight)
                        se3_vertex.weight_pointers.append((se3_vertex_map_index, se3_wmap_elem_count[j]))
                        se3_wmap_elem_count[j] += 1
                    except:
                        pass
            
            se3_building_vertex.final_vertices.append(se3_vertex)
            se3_building_vertices.append(se3_building_vertex)
        
        
        se3_polygons = se3_layer.polygons
        
        edges = mesh.edges
        useful_edges = [edge for edge in edges if edge.is_loose]
        
        se3_polygons_count = 0
        if useful_edges:
            for edge in useful_edges:
                se3_polygons_count += 1
                se3_polygons.append((edge.vertices[0], edge.vertices[1]))
        
        se3_polygon_maps = se3_layer.polygon_maps
        materials = mesh.materials
        
        if materials:
            has_materials = True
            se3_surface_maps = []
            
            for material in materials:
                se3_surface_map = se3.PolygonMap(se3.POLYGON_MAP_TYPE_SURFACE, material.name, 89)
                se3_surface_maps.append(se3_surface_map)
                se3_layer.surface_maps.append(se3_surface_map)
            se3_polygon_maps.extend(se3_surface_maps)
        
        faces = mesh.tessfaces
        
        se3_vertex_map_stride = se3_vertex_map_index
        se3_vertex_count = len(mesh.vertices)
        if faces:
            for face in faces:
                face_index = face.index
                se3_polygon = []
                
                for uv_vertex_index, vertex_index in enumerate(face.vertices):
                    vertex = mesh.vertices[vertex_index]
                    se3_building_vertex = se3_building_vertices[vertex_index]
                    se3_first_vertex = se3_building_vertex.first_vertex
                    
                    se3_found_new_uv_pointers = False
                    
                    se3_uv_pointers = []
                    if has_uv_textures:
                        for uv_texture_index, uv_texture in enumerate(uv_textures):
                            texture_face = uv_texture.data[face_index]
                            uv = texture_face.uv[uv_vertex_index]
                            se3_uv = (uv[0], (-uv[1]) + 1)
                            se3_uv_vertices = se3_building_vertex.uv_vertices[uv_texture_index]
                            se3_texcoord_map_index = se3_vertex_map_stride + uv_texture_index + 1
                            
                            se3_uv_vertex = se3_uv_vertices.get_vertex_with(se3_uv)
                            
                            if se3_uv_vertex and se3_uv_vertex.vertex_index == vertex_index and se3_uv_vertex.map_index == uv_texture_index:
                                se3_uv_pointers.append((se3_texcoord_map_index, se3_uv_vertex.map_element_index))
                            else:
                                se3_found_new_uv_pointers = True
                                
                                se3_texcoord_maps[uv_texture_index].elements.append(se3_uv)
                                
                                se3_texcoord_map_elem_index = se3_texcoord_map_elem_count[uv_texture_index]
                                se3_uv_pointers.append((se3_texcoord_map_index, se3_texcoord_map_elem_index))
                                se3_uv_vertex = se3.UvVertex(se3_uv, se3_texcoord_map_elem_index, vertex_index, uv_texture_index)
                                
                                se3_uv_vertices.append(se3_uv_vertex)
                                
                                se3_texcoord_map_elem_count[uv_texture_index] += 1
                    
                    if se3_found_new_uv_pointers:
                        se3_need_new_vertex = True if se3_first_vertex.uv_pointers else False
                        
                        if se3_need_new_vertex:
                            se3_vertex_index = se3_vertex_count
                            se3_vertex = se3.Vertex(se3_vertex_index)
                            se3_vertex.set_unique_pointers_from(se3_first_vertex)
                            se3_vertex.uv_pointers.extend(se3_uv_pointers)
                            se3_building_vertex.final_vertices.append(se3_vertex)
                            se3_vertices.append(se3_vertex)
                            se3_vertex_count += 1
                        else:
                            se3_vertex_index = vertex_index
                            se3_first_vertex.uv_pointers.extend(se3_uv_pointers)
                    else:
                        se3_vertex_index = se3_building_vertex.get_vertex_index_with(se3_uv_pointers)
                    
                    se3_polygon.append(se3_vertex_index)
                
                se3_polygons.append(se3_polygon)
                
                if has_materials:
                    se3_surface_map = se3_surface_maps[face.material_index]
                    se3_surface_map.polygons.append(se3_polygons_count + face_index)
    
    se3_mesh.write_to_file(amf)
    amf.close()
    return {'FINISHED'}