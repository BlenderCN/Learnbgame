import bpy
import bmesh
from . import mesh_utils
import time

def is_equal_paths(path1, path2):
    return len(set(path1) ^ set(path2)) == 0

def is_in_array_with_comp(it, array, comp):
    for item in array:
        if comp(it, item):
            return True
    
    return False

def remove_duplicate(array, comp):
    array_uniq = []
    
    for item in array:
        if not is_in_array_with_comp(item, array_uniq, comp):
            array_uniq.append(item)
    
    return array_uniq

def print_path(path):
    mesh_utils.unselect_mesh(bmesh.from_edit_mesh(bpy.context.object.data))
    
    for item in path:
        item.select = True
    
    bpy.context.scene.objects.active = bpy.context.scene.objects.active

def calc_turning_num(path, angle_threshold):
    turning_num = 0
    
    if len(path) <= 3:
        return turning_num
    
    for i in map(lambda x : x + 1, range(0, len(path) - 4, 2)):
        if mesh_utils.calc_edges_angle(path[i], path[i + 2]) < angle_threshold:
            turning_num += 1
    
    if path[0] is path[-1]:
        if mesh_utils.calc_edges_angle(path[1], path[-2]) < angle_threshold:
            turning_num += 1
    
    return turning_num

def turning_limited_dfs(data):
    if calc_turning_num(data["track"], data["angle_threshold"]) > data["polygonNum"]:
        data["track"].pop()
        data["track"].pop()
        return data
    
    if len(data["track"]) >= 3 and data["track"][-1] is data["track"][0]:
        if calc_turning_num(data["track"], data["angle_threshold"]) == data["polygonNum"]:
            data["paths"].append(data["track"][:])
        data["track"].pop()
        data["track"].pop()
        return data
    
    for edge in data["track"][-1].link_edges:
        next_vertex = list(set(edge.verts) - set([data["track"][-1]]))[0]
        if next_vertex is data["track"][0] or next_vertex not in data["track"]:
            data["track"].append(edge)
            data["track"].append(next_vertex)
            data = turning_limited_dfs(data)
    
    if len(data["track"]) >= 3:
        data["track"].pop()
        data["track"].pop()
    return data

def get_polygons(mesh, n, angle_threshold):
    paths = []
    
    for vertex in mesh.verts:
        paths += turning_limited_dfs({"track": [vertex], "polygonNum": n, "paths": [], "angle_threshold": angle_threshold})["paths"]
    
    return remove_duplicate(paths, is_equal_paths)
