import mstree
import mst_blender
import numpy as np
import bpy
import mathutils
from pam import pam

def create_uv_tree(obj, quantity, uv_center, mean = [0.0, 0.0], variance = [0.005, 0.005], balancing_factor = 0.0, build_type = 'CURVE', interpolation_resolution = 0):

    # Generate scattered points
    x = [uv_center[0]]
    y = [uv_center[1]]
    x = np.concatenate((x, np.random.normal(uv_center[0], variance[0], quantity) + mean[0]))
    y = np.concatenate((y, np.random.normal(uv_center[1], variance[1], quantity) + mean[1]))

    points = np.dstack((x, y))
    np.clip(points, 0., 1., out = points)
    # all items are stored in the first list-item of the output
    points = points[0]
    
    # Run mstree
    root_point = mstree.mstree(points, balancing_factor)

    # Convert node positions from uv to 3d
    nodes = mstree.tree_to_list(root_point)
    
    interpolated_nodes = []
    for node in nodes:
        parent = node.parent
        interpolated_nodes.append(node)
        if parent is None:
            continue
        points = interpolate(parent.pos, node.pos, interpolation_resolution)[1:-1]
        print(len(points))
        parent.children.remove(node)
        active_parent = parent
        for point in points:
            new_node = mstree.Node(active_parent, np.array(point), -1)
            interpolated_nodes.append(new_node)
            active_parent = new_node
        node.parent = active_parent
        active_parent.children.append(node)


    node_uv_points = [mathutils.Vector((node.pos[0], node.pos[1])) for node in interpolated_nodes]
    print(len(node_uv_points))

    node_3d_points = pam.mapUVPointTo3d(obj, node_uv_points)
    print(len(node_3d_points))

    for i, node in enumerate(interpolated_nodes):
        node.pos = node_3d_points[i]

    if build_type == 'CURVE':
        curve_obj = mst_blender.buildTreeCurve(root_point)
        curve_obj.data.bevel_depth = 0.002
    elif build_type == 'MESH':
        mesh_obj = mst_blender.buildTreeMesh(root_point)

def interpolate_by_resolution(p1, p2, interpolation_length):
    """Interpolates between two given points by a defined resolution.
    :param p1: First point
    :type p1: List with max. 4 elements
    :param p2: Second point
    :type p2: List with max. 4 elements
    :param interpolation_length: Resolution for interpolation. Smaller numbers means more points
    :type interpolation_length: float
    :returns: List of interpolated points including the two starting points
    :return type: List"""
    if interpolation_length == 0:
        return [p1, p2]
    if interpolation_length < 0:
        raise ValueError("Interpolation resolution must be positive")
    p1 = mathutils.Vector(p1)
    p2 = mathutils.Vector(p2)
    dist = (p1 - p2).length
    no_interpolations = int(np.floor(dist / interpolation_length))
    print(no_interpolations)
    if no_interpolations < 1:
        return [p1.to_tuple(), p2.to_tuple()]
    ps = np.linspace(0., 1., no_interpolations)
    new_points = []
    for p in ps:
        p_new = p1.lerp(p2, p)
        new_points.append(p_new.to_tuple())
    print(len(new_points))
    return new_points

def export_swc(root_node, outfilename, structure_identifier = 2):
    nodes = mstree.tree_to_list(root_node)
    f = open(outfilename, 'w')
    index = 0
    for node in nodes:
        node.index = index
        index += 1

        if node.parent is not None:
            parent_index = node.parent.index
        else:
            parent_index = -1

        f.write(' '.join((str(node.index), str(structure_identifier), str(node.pos[0]), str(node.pos[1]), str(node.pos[2]), str(0), str(parent_index))))
        f.write('\n')
    f.close()
    
def createAxons(p_obj, s_obj, quantity, mean, variance):
    for p in p_obj.particle_systems[0].particles:
        uv = pam.map3dPointToUV(p_obj, s_obj, p.location)
        create_uv_tree(s_obj, quantity, uv, mean, variance)

if __name__ == '__main__':
    create_uv_tree(bpy.data.objects['CA3_sp_axons_all'], 100, (0.3, 0.5), [-0.1, 0.], [0.02, 0.005], build_type = 'MESH')
# ca3 = bpy.data.objects['CA3_sp']
# ca3_s = bpy.data.objects['CA3_sp_axons_all']
# createAxons(ca3, ca3_s, 100, [-0.1, 0.0], [0.02, 0.005])