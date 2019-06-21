from mathutils import Vector
import fnmatch
import bpy

from . import cycler
from . import log

def match_name(_list, _glob='*'):
    in_name = lambda n: fnmatch.fnmatchcase(n, _glob)
    return (o for o in _list if in_name(o.name))

def in_groups(_list, _glob='*'):
    # All objects shared in list
    all_obj = set(_list.pop().objects)
    for _g in _list:
        all_obj &= set(_g.objects)
    # All shared objects that match
    return match_name(all_obj, _glob)

def near_z(nodes, mesh_z):
    # Node names with only digits
    dig = lambda n: n.name.split('.')[0]
    is_dig = lambda n: dig(n).isdigit()
    all_z = filter(is_dig, nodes)
    def sort_name(node):
        n_num = int(dig(node))
        return abs(mesh_z - n_num)
    # All materials closest to z
    return sorted(all_z, key=sort_name)

def slice_z(obj, mesh_z):
    material = obj.active_material
    node_tree = material.node_tree
    nodes = node_tree.nodes
    z_node = near_z(nodes, mesh_z)[0]
    # Activate texture for z node
    cycler.link(material, z_node)

def slice_w_z(obj, w_z, rel=True):
    """ Material for z (in blender units)
    """
    groups = obj.users_group
    VOL = next(match_name(groups, 'VOL*'))
    SUB = next(match_name(groups, 'SUB*'))
    SRC = next(match_name(groups, 'SRC*'))
    # Translate image by origin and offset
    if not rel:
        vol_z = VOL.origin[-1]
        sub_z = SUB.offset[-1]
        w_z = w_z - vol_z - sub_z
    # Get local z texture
    mesh_z = w_z / SRC.from_mesh[-1]
    # Set texture to specified Z
    slice_z(obj, mesh_z)

def move_z(obj, mesh_z):
    groups = obj.users_group
    VOL = next(match_name(groups, 'VOL*'))
    SUB = next(match_name(groups, 'SUB*'))
    SRC = next(match_name(groups, 'SRC*'))
    # Translate image by origin and offset
    vol_z = VOL.origin[-1]
    sub_z = SUB.offset[-1]
    origin_z = vol_z + sub_z
    # Move to specified Z
    stack_z = SRC.from_mesh[-1] * mesh_z
    obj.location.z = origin_z + stack_z
    # Set texture to specified Z
    slice_z(obj, mesh_z)

def move_w_z(obj, w_z):
    """ Move to slice z (in blender units)
    """
    groups = obj.users_group
    SUB = next(match_name(groups, 'SUB*'))
    SRC = next(match_name(groups, 'SRC*'))
    # Get the range of the subvolume
    sub_depth = SUB.subvolume[-1]
    sub_z = SUB.offset[-1]
    # Get the z with respect to the stack
    stack_z = w_z - sub_z
    # Use mesh z to move if in range
    if 0 <= stack_z <= sub_depth:
        mesh_z = stack_z / SRC.from_mesh[-1]
        move_z(obj, mesh_z)
        obj.hide = False
    # Hide the object
    else:
        obj.hide = True

def move_w_vol(vol, obj, w_off):
    """ Move relative to vol (blender units)
    """
    origin = Vector(vol.origin)
    volume = Vector(vol.volume)
    center = origin + volume/2
    center.z = origin.z
    # Move object from the center of slice 0
    obj.location = center + Vector(w_off)

def energy(area, dist, bright=0):
    brights = {
        'Area': 10000,
        'Over': 100,
        'Under': 100,
    }
    if not bright:
        a_bright = brights.get(area.name, 0)
    # Calculate power per square unit
    a_pow = a_bright * (dist ** 2)
    return a_pow * (area.size ** 2)

def in_box(o):
    bounds = (Vector(b) for b in o.bound_box)
    center = sum(bounds, Vector()) / 8.0
    return  o.matrix_world * center

def look_at(scene, objs):
    
    c_center = scene.camera.matrix_world.to_translation()
    o_center = sum(map(in_box, objs), Vector()) / len(objs)

    direction = o_center - c_center
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    scene.camera.rotation_euler = rot_quat.to_euler()

def look(scene):
    # Select mesh
    is_mesh = lambda x: x.type == 'MESH'
    selected = [o for o in scene.objects if is_mesh(o)]
    look_at(scene, selected)

