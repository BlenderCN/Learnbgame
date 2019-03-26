# Author: Adnan Munawar
# Email: amunawar@wpi.edu
# Lab: aimlab.wpi.edu

bl_info = {
    "name": "Asynchronous Multi-Body Framework (AMBF) Config Creator",
    "author": "Adnan Munawar",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh > AMBF",
    "description": "Helps Generate AMBF Config File and Saves both High and Low Resolution(Collision) Meshes",
    "warning": "",
    "wiki_url": "https://github.com/WPI-AIM/ambf_addon",
    "category": "AMBF",
    }

import bpy
import math
import yaml
import os
from pathlib import Path
import mathutils
from enum import Enum
from collections import OrderedDict, Counter
from datetime import datetime


# https://stackoverflow.com/questions/31605131/dumping-a-dictionary-to-a-yaml-file-while-preserving-order/31609484
def represent_dictionary_order(self, dict_data):
    return self.represent_mapping('tag:yaml.org,2002:map', dict_data.items())


def setup_yaml():
    yaml.add_representer(OrderedDict, represent_dictionary_order)


# Enum Class for Mesh Type
class MeshType(Enum):
    meshSTL = 0
    meshOBJ = 1
    mesh3DS = 2
    meshPLY = 3


def get_extension(val):
    if val == MeshType.meshSTL.value:
        extension = '.STL'
    elif val == MeshType.meshOBJ.value:
        extension = '.OBJ'
    elif val == MeshType.mesh3DS.value:
        extension = '.3DS'
    elif val == MeshType.meshPLY.value:
        extension = '.PLY'
    else:
        extension = None

    return extension


def skew_mat(v):
    m = mathutils.Matrix.Identity(3)
    m.Identity(3)
    m[0][0] = 0
    m[0][1] = -v.z
    m[0][2] = v.y
    m[1][0] = v.z
    m[1][1] = 0
    m[1][2] = -v.x
    m[2][0] = -v.y
    m[2][1] = v.x
    m[2][2] = 0

    return m


def vec_norm(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)


def round_vec(v):
    for i in range(0, 3):
        v[i] = round(v[i], 3)
    return v


# https://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d/897677#897677
def rot_matrix_from_vecs(v1, v2):
    out = mathutils.Matrix.Identity(3)
    vcross = v1.cross(v2)
    vdot = v1.dot(v2)
    rot_angle = v1.angle(v2)
    if 1.0 - vdot < 0.1:
        return out
    elif 1.0 + vdot < 0.1:
        # This is a more involved case, find out the orthogonal vector to vecA
        nx = mathutils.Vector([1, 0, 0])
        temp_ang = v1.angle(nx)
        if 0.1 < abs(temp_ang) < 3.13:
            axis = v1.cross(nx)
            out = out.Rotation(rot_angle, 3, axis)
        else:
            ny = mathutils.Vector([0, 1, 0])
            axis = v1.cross(ny)
            out = out.Rotation(rot_angle, 3, axis)
    else:
        skew_v = skew_mat(vcross)
        out = mathutils.Matrix.Identity(3) + skew_v + skew_v * skew_v * ((1 - vdot) / (vec_norm(vcross) ** 2))
    return out


# Get rotation matrix to represent rotation between two vectors
# Brute force implementation
def get_rot_mat_from_vecs(vecA, vecB):
    # Angle between two axis
    angle = vecA.angle(vecB)
    # Axis of rotation between child's joints axis and constraint_axis
    if abs(angle) <= 0.1:
        # Doesn't matter which axis we chose, the rot mat is going to be identity
        # as angle is almost 0
        axis = mathutils.Vector([0, 1, 0])
    elif abs(angle) >= 3.13:
        # This is a more involved case, find out the orthogonal vector to vecA
        nx = mathutils.Vector([1, 0, 0])
        temp_ang = vecA.angle(nx)
        if 0.1 < abs(temp_ang) < 3.13:
            axis = vecA.cross(nx)
        else:
            ny = mathutils.Vector([0, 1, 0])
            axis = vecA.cross(ny)
    else:
        axis = vecA.cross(vecB)

    mat = mathutils.Matrix()
    # Rotation matrix representing the above angular offset
    rot_mat = mat.Rotation(angle, 4, axis)
    return rot_mat, angle


# Global Variables
class CommonConfig:
    # Since there isn't a convenient way of defining parallel linkages (hence redundant joints) due to the
    # limit on 1 parent per body. We use kind of a hack. This prefix is what we we search for it we find an
    # empty body with the mentioned prefix.
    redundant_joint_prefix = ['redundant', 'Redundant', 'REDUNDANT']
    namespace = ''
    num_collision_groups = 20


def update_global_namespace(context):
    CommonConfig.namespace = context.scene.ambf_namespace
    if CommonConfig.namespace[-1] != '/':
        print('WARNING, MULTI-BODY NAMESPACE SHOULD END WITH \'/\'')
        CommonConfig.namespace += '/'
        context.scene.ambf_namespace += CommonConfig.namespace


def set_global_namespace(context, namespace):
    CommonConfig.namespace = namespace
    if CommonConfig.namespace[-1] != '/':
        print('WARNING, MULTI-BODY NAMESPACE SHOULD END WITH \'/\'')
        CommonConfig.namespace += '/'
    context.scene.ambf_namespace = CommonConfig.namespace


def get_body_namespace(fullname):
    last_occurance = fullname.rfind('/')
    _body_namespace = ''
    if last_occurance >= 0:
        # This means that the name contains a namespace
        _body_namespace = fullname[0:last_occurance+1]
    return _body_namespace


def remove_namespace_prefix(full_name):
    last_occurance = full_name.rfind('/')
    if last_occurance > 0:
        # Body name contains a namespace
        _name = full_name[last_occurance+1:]
    else:
        # Body name doesn't have a namespace
        _name = full_name
    return _name


def replace_dot_from_obj_names(char_subs = '_'):
    for obj in bpy.data.objects:
        obj.name = obj.name.replace('.', char_subs)


def compare_body_namespace_with_global(fullname):
    last_occurance = fullname.rfind('/')
    _is_namespace_same = False
    _body_namespace = ''
    _name = ''
    if last_occurance >= 0:
        # This means that the name contains a namespace
        _body_namespace = fullname[0:last_occurance+1]
        _name = fullname[last_occurance+1:]

        if CommonConfig.namespace == _body_namespace:
            # The CommonConfig namespace is the same as the body namespace
            _is_namespace_same = True
        else:
            # The CommonConfig namespace is different form body namespace
            _is_namespace_same = False

    else:
        # The body's name does not contain and namespace
        _is_namespace_same = False

    # print("FULLNAME: %s, BODY: %s, NAMESPACE: %s NAMESPACE_MATCHED: %d" %
    # (fullname, _name, _body_namespace, _is_namespace_same))
    return _is_namespace_same


def add_namespace_prefix(name):
    return CommonConfig.namespace + name


def get_grand_parent(body):
    grand_parent = body
    while grand_parent.parent is not None:
        grand_parent = grand_parent.parent
    return grand_parent


def downward_tree_pass(body, _heirarichal_bodies_list, _added_bodies_list):
    if body is None or _added_bodies_list[body] is True:
        return

    else:
        # print('DOWNWARD TREE PASS: ', body.name)
        _heirarichal_bodies_list.append(body)
        _added_bodies_list[body] = True

        for child in body.children:
            downward_tree_pass(child, _heirarichal_bodies_list, _added_bodies_list)


def populate_heirarchial_tree():
    # Create a dict with {body, added_flag} elements
    # The added_flag is to check if the body has already
    # been added
    _added_bodies_list = {}
    _heirarchial_bodies_list = []

    for obj in bpy.data.objects:
        _added_bodies_list[obj] = False

    for obj in bpy.data.objects:
        grand_parent = get_grand_parent(obj)
        # print('CALLING DOWNWARD TREE PASS FOR: ', grand_parent.name)
        downward_tree_pass(grand_parent, _heirarchial_bodies_list, _added_bodies_list)

    for body in _heirarchial_bodies_list:
        print(body.name, "--->",)

    return _heirarchial_bodies_list


# Courtesy: https://stackoverflow.com/questions/5914627/prepend-line-to-beginning-of-a-file
def prepend_comment_to_file(filename, comment):
    with open(filename,'r') as f:
        with open('tempfile.txt', 'w') as f2:
            f2.write(comment)
            f2.write(f.read())
    os.rename('tempfile.txt', filename)


def select_all_objects(select=True):
    # First deselect all objects
    for obj in bpy.data.objects:
        obj.select = select


# For shapes such as Cylinder, Cone and Ellipse, this function returns
# the major axis by comparing the dimensions of the bounding box
def get_major_axis(dims):
    d = dims
    axes = {0: 'x', 1: 'y', 2: 'z'}
    sum_diff = [abs(d[0] - d[1]) + abs(d[0] - d[2]),
                abs(d[1] - d[0]) + abs(d[1] - d[2]),
                abs(d[2] - d[0]) + abs(d[2] - d[1])]
    # If the bounds are equal, choose the z axis
    if sum_diff[0] == sum_diff[1] and sum_diff[1] == sum_diff[2]:
        axis_idx = 2
    else:
        axis_idx = sum_diff.index(max(sum_diff))

    return axes[axis_idx], axis_idx


# For shapes such as Cylinder, Cone and Ellipse, this function returns
# the median axis (not-major and non-minor or the middle axis) by comparing
# the dimensions of the bounding box
def get_median_axis(dims):
    axes = {0: 'x', 1: 'y', 2: 'z'}
    maj_ax, maj_ax_idx = get_major_axis(dims)
    min_ax, min_ax_idx = get_minor_axis(dims)
    med_axes_idx = [1, 1, 1]
    med_axes_idx[maj_ax_idx] = 0
    med_axes_idx[min_ax_idx] = 0
    axis_idx = med_axes_idx.index(max(med_axes_idx))

    return axes[axis_idx], axis_idx


# For shapes such as Cylinder, Cone and Ellipse, this function returns
# the minor axis by comparing the dimensions of the bounding box
def get_minor_axis(dims):
    d = dims
    axes = {0: 'x', 1: 'y', 2: 'z'}
    sum_diff = [abs(d[0] - d[1]) + abs(d[0] - d[2]),
                abs(d[1] - d[0]) + abs(d[1] - d[2]),
                abs(d[2] - d[0]) + abs(d[2] - d[1])]
    max_idx = sum_diff.index(max(sum_diff))
    min_idx = sum_diff.index(min(sum_diff))
    sort_idx = [1, 1, 1]
    sort_idx[max_idx] = 0
    sort_idx[min_idx] = 0
    median_idx = sort_idx.index(max(sort_idx))
    return axes[median_idx], median_idx


# Body Template for the some commonly used of afBody's data
class BodyTemplate:
    def __init__(self):
        self._ambf_data = OrderedDict()
        self._ambf_data['name'] = ""
        self._ambf_data['mesh'] = ""
        self._ambf_data['mass'] = 0.0
        self._ambf_data['inertia'] = {'ix': 0.0, 'iy': 0.0, 'iz': 0.0}
        self._ambf_data['collision margin'] = 0.001
        self._ambf_data['scale'] = 1.0
        self._ambf_data['location'] = {'position': {'x': 0, 'y': 0, 'z': 0},
                                       'orientation': {'r': 0, 'p': 0, 'y': 0}}
        self._ambf_data['inertial offset'] = {'position': {'x': 0, 'y': 0, 'z': 0},
                                              'orientation': {'r': 0, 'p': 0, 'y': 0}}
        self._ambf_data['color'] = 'random'
        # Transform of Child Rel to Joint, which in inverse of t_c_j
        self.t_j_c = mathutils.Matrix()


# Joint Template for the some commonly used of afJoint's data
class JointTemplate:
    def __init__(self):
        self._ambf_data = OrderedDict()
        self._ambf_data['name'] = ''
        self._ambf_data['parent'] = ''
        self._ambf_data['child'] = ''
        self._ambf_data['parent axis'] = {'x': 0, 'y': 0.0, 'z': 1.0}
        self._ambf_data['parent pivot'] = {'x': 0, 'y': 0.0, 'z': 0}
        self._ambf_data['child axis'] = {'x': 0, 'y': 0.0, 'z': 1.0}
        self._ambf_data['child pivot'] = {'x': 0, 'y': 0.0, 'z': 0}
        self._ambf_data['joint limits'] = {'low': -1.2, 'high': 1.2}
        self._ambf_data['controller'] = {'P': 1000, 'I': 0, 'D': 1}


class GenerateAMBF(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "ambf.add_create_ambf_config"
    bl_label = "Write Multi-Body AMBF Config"
    bl_description = "This generated the AMBF Config file in the location and filename specified in the field" \
                     " above"

    def __init__(self):
        self._body_names_list = []
        self._joint_names_list = []
        self.body_name_prefix = 'BODY '
        self.joint_name_prefix = 'JOINT '
        self._ambf_yaml = None

    def execute(self, context):
        self.generate_ambf_yaml(context)
        return {'FINISHED'}

    # This joint adds the body prefix str if set to all the bodies in the AMBF
    def add_body_prefix_str(self, urdf_body_str):
        return self.body_name_prefix + urdf_body_str

    # This method add the joint prefix if set to all the joints in AMBF
    def add_joint_prefix_str(self, urdf_joint_str):
        return self.joint_name_prefix + urdf_joint_str

    # Courtesy of:
    # https://blender.stackexchange.com/questions/62040/get-center-of-geometry-of-an-object
    def compute_local_com(self, obj):
        vcos = [ v.co for v in obj.data.vertices ]
        find_center = lambda l: ( max(l) + min(l)) / 2
        x, y, z = [[v[i] for v in vcos] for i in range(3)]
        center = [find_center(axis) for axis in [x, y, z]]
        for i in range(0, 3):
            center[i] = center[i] * obj.scale[i]
        return center

    def generate_body_data(self, ambf_yaml, obj_handle):
        if obj_handle.hide is True:
            return
        body = BodyTemplate()
        body_data = body._ambf_data

        if not compare_body_namespace_with_global(obj_handle.name):
            if get_body_namespace(obj_handle.name) != '':
                body_data['namespace'] = get_body_namespace(obj_handle.name)

        obj_handle_name = remove_namespace_prefix(obj_handle.name)

        body_yaml_name = self.add_body_prefix_str(obj_handle_name)
        output_mesh = bpy.context.scene['mesh_output_type']
        body_data['name'] = obj_handle_name
        # If the obj is root body of a Multi-Body and has children
        # then we should enable the publishing of its joint names
        # and joint positions
        if obj_handle.parent is None and obj_handle.children:
            body_data['publish joint names'] = True
            body_data['publish joint positions'] = True

        world_pos = obj_handle.matrix_world.translation
        world_rot = obj_handle.matrix_world.to_euler()
        body_pos = body_data['location']['position']
        body_rot = body_data['location']['orientation']
        body_pos['x'] = round(world_pos.x, 3)
        body_pos['y'] = round(world_pos.y, 3)
        body_pos['z'] = round(world_pos.z, 3)
        body_rot['r'] = round(world_rot[0], 3)
        body_rot['p'] = round(world_rot[1], 3)
        body_rot['y'] = round(world_rot[2], 3)
        if obj_handle.type == 'EMPTY':
            # Check for a special case for defining joints for parallel linkages
            _is_redundant_joint = False
            for _parallel_prefix_search_str in CommonConfig.redundant_joint_prefix:
                if obj_handle_name.rfind(_parallel_prefix_search_str) == 0:
                    _is_redundant_joint = True
                    break

            if _is_redundant_joint:
                print('INFO: JOINT %s FOR PARALLEL LINKAGE FOUND' % obj_handle_name)
                return
            else:
                body_data['mesh'] = ''

                if obj_handle_name in ['world', 'World', 'WORLD']:
                    body_data['mass'] = 0

                else:
                    body_data['mass'] = 0.1
                    body_data['inertia'] = {'ix': 0.01, 'iy': 0.01, 'iz': 0.01}

        elif obj_handle.type == 'MESH':

            if obj_handle.rigid_body:
                if obj_handle.rigid_body.type == 'PASSIVE':
                    body_data['mass'] = 0.0
                else:
                    body_data['mass'] = round(obj_handle.rigid_body.mass, 3)
                body_data['friction'] = {'rolling': 0.01, 'static': 0.5}
                body_data['damping'] = {'linear': 0.1, 'angular': 0.1}
                body_data['restitution'] = round(obj_handle.rigid_body.restitution)

                body_data['friction']['static'] = round(obj_handle.rigid_body.friction, 3)
                body_data['damping']['linear'] = round(obj_handle.rigid_body.linear_damping, 3)
                body_data['damping']['angular'] = round(obj_handle.rigid_body.angular_damping, 3)

                body_data['collision groups'] = [idx for idx, chk in
                                                 enumerate(obj_handle.rigid_body.collision_groups) if chk == True]

                if obj_handle.rigid_body.use_margin is True:
                    body_data['collision margin'] = round(obj_handle.rigid_body.collision_margin, 3)

                if obj_handle.rigid_body.collision_shape not in ['CONVEX_HULL', 'MESH']:
                    body_data['collision shape'] = obj_handle.rigid_body.collision_shape
                    bcg = OrderedDict()
                    ocs = obj_handle.rigid_body.collision_shape
                    dims = obj_handle.dimensions.copy()
                    od = [round(dims[0], 3), round(dims[1], 3), round(dims[2], 3)]
                    # Now we need to find out the geometry of the shape
                    if ocs == 'BOX':
                        bcg = {'x': od[0], 'y': od[1], 'z': od[2]}
                    elif ocs == 'SPHERE':
                        bcg = {'radius': max(od)/2.0}
                    elif ocs == 'CYLINDER':
                        major_ax_char, major_ax_idx = get_major_axis(od)
                        median_ax_char, median_ax_idx = get_median_axis(od)
                        bcg = {'radius': od[median_ax_idx]/2.0, 'height': od[major_ax_idx], 'axis': major_ax_char}
                    elif ocs == 'CAPSULE':
                        major_ax_char, major_ax_idx = get_major_axis(od)
                        median_ax_char, median_ax_idx = get_median_axis(od)
                        bcg = {'radius': od[median_ax_idx]/2.0, 'height': od[major_ax_idx], 'axis': major_ax_char}
                    elif ocs == 'CONE':
                        major_ax_char, major_ax_idx = get_major_axis(od)
                        median_ax_char, median_ax_idx = get_median_axis(od)
                        bcg = {'radius': od[median_ax_idx]/2.0, 'height': od[major_ax_idx], 'axis': major_ax_char}

                    body_data['collision geometry'] = bcg

            del body_data['inertia']
            body_data['mesh'] = obj_handle_name + get_extension(output_mesh)
            body_com = self.compute_local_com(obj_handle)
            body_d_pos = body_data['inertial offset']['position']
            body_d_pos['x'] = round(body_com[0], 3)
            body_d_pos['y'] = round(body_com[1], 3)
            body_d_pos['z'] = round(body_com[2], 3)

            if obj_handle.data.materials:
                del body_data['color']
                body_data['color rgba'] = {'r': 1.0, 'g': 1.0, 'b': 1.0, 'a': 1.0}
                body_data['color rgba']['r'] = round(obj_handle.data.materials[0].diffuse_color[0], 4)
                body_data['color rgba']['g'] = round(obj_handle.data.materials[0].diffuse_color[1], 4)
                body_data['color rgba']['b'] = round(obj_handle.data.materials[0].diffuse_color[2], 4)
                # Setting alpha as one gives weird artifacts in ambf, so setting the value slightly lower
                body_data['color rgba']['a'] = round(obj_handle.data.materials[0].alpha, 4) - 0.01

        ambf_yaml[body_yaml_name] = body_data
        self._body_names_list.append(body_yaml_name)

    def generate_joint_data(self, ambf_yaml, obj_handle):

        if obj_handle.hide is True:
            return

        if obj_handle.rigid_body_constraint:
            if obj_handle.rigid_body_constraint.object1:
                if obj_handle.rigid_body_constraint.object1.hide is True:
                    return
            if obj_handle.rigid_body_constraint.object2:
                if obj_handle.rigid_body_constraint.object2.hide is True:
                    return

            if obj_handle.rigid_body_constraint.type in ['FIXED', 'HINGE', 'SLIDER']:
                constraint = obj_handle.rigid_body_constraint
                joint_template = JointTemplate()
                joint_data = joint_template._ambf_data
                if constraint.object1:
                    parent_obj_handle = constraint.object1
                    child_obj_handle = constraint.object2

                    parent_obj_handle_name = remove_namespace_prefix(parent_obj_handle.name)
                    child_obj_handle_name = remove_namespace_prefix(child_obj_handle.name)
                    obj_handle_name = remove_namespace_prefix(obj_handle.name)

                    joint_data['name'] = parent_obj_handle_name + "-" + child_obj_handle_name
                    joint_data['parent'] = self.add_body_prefix_str(parent_obj_handle_name)
                    joint_data['child'] = self.add_body_prefix_str(child_obj_handle_name)
                    # parent_body_data = self._ambf_yaml[self.get_body_prefixed_name(parent_obj_handle_name)]
                    # child_body_data = self._ambf_yaml[self.get_body_prefixed_name(child_obj_handle_name)]

                    # Since there isn't a convenient way of defining redundant joints and hence parallel linkages due
                    # to the limit on 1 parent per body. We use a hack. This is how it works. In Blender
                    # we start by defining an empty body that has to have specific prefix as the first word
                    # in its name. Next we set up the rigid_body_constraint of this empty body as follows. For the RBC
                    # , we set the parent of this empty body to be the link that we want as the parent for
                    # the redundant joint and the child body as the corresponding child of the redundant joint.
                    # Remember, this empty body is only a place holder and won't be added to
                    # AMBF. Next, its recommended to set the parent body of this empty body as it's parent in Blender
                    # and by that I mean the tree hierarchy parent (having set the the parent in the rigid body
                    # constraint property is different from parent in tree hierarchy). From there on, make sure to
                    # rotate this empty body such that the z axis / x axis is in the direction of the joint axis if
                    # the redundant joint is supposed to be revolute or prismatic respectively.
                    _is_redundant_joint = False
                    if obj_handle.type == 'EMPTY':
                        # Check for a special case for defining joints for parallel linkages
                        for _parallel_prefix_search_str in CommonConfig.redundant_joint_prefix:
                            if obj_handle_name.rfind(_parallel_prefix_search_str) == 0:
                                _is_redundant_joint = True
                                break

                    if _is_redundant_joint:

                        print('INFO: FOR BODY \"%s\" ADDING PARALLEL LINKAGE JOINT' % obj_handle_name)

                        parent_pivot, parent_axis = self.compute_parent_pivot_and_axis(
                            parent_obj_handle, obj_handle, obj_handle.rigid_body_constraint.type)

                        child_pivot, child_axis = self.compute_parent_pivot_and_axis(
                            child_obj_handle, obj_handle, obj_handle.rigid_body_constraint.type)
                        # Add this field to the joint data, it will come in handy for blender later
                        joint_data['redundant'] = True

                    else:

                        parent_pivot, parent_axis = self.compute_parent_pivot_and_axis(
                            parent_obj_handle, child_obj_handle, obj_handle.rigid_body_constraint.type)
                        child_pivot = mathutils.Vector([0, 0, 0])
                        child_axis = mathutils.Vector([0, 0, 0])
                    if obj_handle.rigid_body_constraint.type == 'HINGE':
                        child_axis = mathutils.Vector([0, 0, 1])
                        if constraint.use_limit_ang_z:
                            joint_data['type'] = 'revolute'
                            higher_limit = constraint.limit_ang_z_upper
                            lower_limit = constraint.limit_ang_z_lower
                        else:
                            joint_data['type'] = 'continuous'
                    elif obj_handle.rigid_body_constraint.type == 'SLIDER':
                        joint_data['type'] = 'prismatic'
                        child_axis = mathutils.Vector([1, 0, 0])
                        higher_limit = constraint.limit_lin_x_upper
                        lower_limit = constraint.limit_lin_x_lower
                    elif obj_handle.rigid_body_constraint.type == 'FIXED':
                        joint_data['type'] = 'fixed'
                        child_axis = mathutils.Vector([0, 0, 1])

                    parent_pivot_data = joint_data["parent pivot"]
                    parent_axis_data = joint_data["parent axis"]
                    parent_pivot_data['x'] = round(parent_pivot.x, 3)
                    parent_pivot_data['y'] = round(parent_pivot.y, 3)
                    parent_pivot_data['z'] = round(parent_pivot.z, 3)
                    parent_axis_data['x'] = round(parent_axis.x, 3)
                    parent_axis_data['y'] = round(parent_axis.y, 3)
                    parent_axis_data['z'] = round(parent_axis.z, 3)
                    child_pivot_data = joint_data["child pivot"]
                    child_axis_data = joint_data["child axis"]
                    child_pivot_data['x'] = round(child_pivot.x, 3)
                    child_pivot_data['y'] = round(child_pivot.y, 3)
                    child_pivot_data['z'] = round(child_pivot.z, 3)
                    child_axis_data['x'] = round(child_axis.x, 3)
                    child_axis_data['y'] = round(child_axis.y, 3)
                    child_axis_data['z'] = round(child_axis.z, 3)

                    if joint_data['type'] == 'fixed':
                        del joint_data["joint limits"]

                    elif joint_data['type'] == 'continuous':
                        del joint_data["joint limits"]['low']
                        del joint_data["joint limits"]['high']

                    else:
                        joint_limit_data = joint_data["joint limits"]
                        joint_limit_data['low'] = round(lower_limit, 3)
                        joint_limit_data['high'] = round(higher_limit, 3)

                    # The use of pivot and axis does not fully define the connection and relative
                    # transform between two bodies it is very likely that we need an additional offset
                    # of the child body as in most of the cases of URDF's For this purpose, we calculate
                    # the offset as follows
                    r_c_p_ambf = rot_matrix_from_vecs(child_axis, parent_axis)
                    r_p_c_ambf = r_c_p_ambf.to_3x3().copy()
                    r_p_c_ambf.invert()

                    t_p_w = parent_obj_handle.matrix_world.copy()
                    r_w_p = t_p_w.to_3x3().copy()
                    r_w_p.invert()
                    r_c_w = child_obj_handle.matrix_world.to_3x3().copy()
                    r_c_p_blender = r_w_p * r_c_w

                    r_angular_offset = r_p_c_ambf * r_c_p_blender

                    offset_axis_angle = r_angular_offset.to_quaternion().to_axis_angle()

                    if abs(offset_axis_angle[1]) > 0.01:
                        # print '*****************************'
                        # print joint_data['name']
                        # print 'Joint Axis, '
                        # print '\t', joint.axis
                        # print 'Offset Axis'
                        # print '\t', offset_axis_angle[1]
                        offset_angle = round(offset_axis_angle[1], 3)
                        # offset_angle = round(offset_angle, 3)
                        # print 'Offset Angle: \t', offset_angle
                        # print('OFFSET ANGLE', offset_axis_angle[1])
                        # print('CHILD AXIS', child_axis)
                        # print('OFFSET AXIS', offset_axis_angle)
                        # print('DOT PRODUCT', parent_axis.dot(offset_axis_angle[0]))

                        if abs(1.0 - child_axis.dot(offset_axis_angle[0])) < 0.1:
                            joint_data['offset'] = offset_angle
                            # print ': SAME DIRECTION'
                        elif abs(1.0 + child_axis.dot(offset_axis_angle[0])) < 0.1:
                            joint_data['offset'] = -offset_angle
                            # print ': OPPOSITE DIRECTION'
                        else:
                            print('ERROR: SHOULD\'NT GET HERE')

                    joint_yaml_name = self.add_joint_prefix_str(joint_data['name'])
                    ambf_yaml[joint_yaml_name] = joint_data
                    self._joint_names_list.append(joint_yaml_name)

                    # Finally get some rough values for the controller gains
                    p_mass = 0.01
                    c_mass = 0.01
                    if parent_obj_handle.rigid_body:
                        p_mass = parent_obj_handle.rigid_body.mass
                    if child_obj_handle.rigid_body:
                        c_mass = child_obj_handle.rigid_body.mass

                    joint_data["controller"]["P"] = round((p_mass + c_mass) * 1000.0, 3)
                    joint_data["controller"]["D"] = round((p_mass + c_mass) / 10.0, 3)

    # Since changing the scale of the bodies directly impacts the rotation matrix, we have
    # to take that into account while calculating offset of child from parent using
    # transform manipulation
    def compute_parent_pivot_and_axis(self, parent, child, joint_type):
        # Since the rotation matrix is carrying the scale, separate out just
        # the rotation component
        # Transform of Parent in World
        t_p_w = parent.matrix_world.copy().to_euler().to_matrix().to_4x4()
        t_p_w.translation = parent.matrix_world.copy().translation

        # Since the rotation matrix is carrying the scale, separate out just
        # the rotation component
        # Transform of Child in World
        t_c_w = child.matrix_world.copy().to_euler().to_matrix().to_4x4()
        t_c_w.translation = child.matrix_world.copy().translation

        # Copy over the transform to invert it
        t_w_p = t_p_w.copy()
        t_w_p.invert()
        # Transform of Child in Parent
        # t_c_p = t_w_p * t_c_w
        t_c_p = t_w_p * t_c_w
        parent_pivot = t_c_p.translation
        if joint_type == 'HINGE':
            col_num = 2
        elif joint_type == 'SLIDER':
            col_num = 0
        elif joint_type == 'FIXED':
            col_num = 2
        # The third col of rotation matrix is the z axes of child in parent
        parent_axis = mathutils.Vector(t_c_p.col[col_num][0:3])
        return parent_pivot, parent_axis

    def generate_ambf_yaml(self, context):
        num_objs = len(bpy.data.objects)
        save_to = bpy.path.abspath(context.scene.ambf_yaml_conf_path)
        file_name = os.path.basename(save_to)
        save_path = os.path.dirname(save_to)
        if not file_name:
            file_name = 'default.yaml'
        output_file_name = os.path.join(save_path, file_name)
        output_file = open(output_file_name, 'w')
        print('Output filename is: ', output_file_name)

        # For inorder processing, set the bodies and joints tag at the top of the map
        self._ambf_yaml = OrderedDict()
        
        self._ambf_yaml['bodies'] = []
        self._ambf_yaml['joints'] = []
        print('SAVE PATH', bpy.path.abspath(save_path))
        print('AMBF CONFIG PATH', bpy.path.abspath(context.scene.ambf_yaml_mesh_path))
        rel_mesh_path = os.path.relpath(bpy.path.abspath(context.scene.ambf_yaml_mesh_path), bpy.path.abspath(save_path))

        self._ambf_yaml['high resolution path'] = rel_mesh_path + '/high_res/'
        self._ambf_yaml['low resolution path'] = rel_mesh_path + '/low_res/'

        self._ambf_yaml['ignore inter-collision'] = context.scene.ignore_inter_collision

        update_global_namespace(context)

        if CommonConfig.namespace is not "":
            self._ambf_yaml['namespace'] = CommonConfig.namespace

        # We want in-order processing, so make sure to
        # add bodies to ambf in a hierarchial fashion.

        _heirarichal_bodies_list = populate_heirarchial_tree()

        for body in _heirarichal_bodies_list:
            self.generate_body_data(self._ambf_yaml, body)

        for body in _heirarichal_bodies_list:
            self.generate_joint_data(self._ambf_yaml, body)

        # Now populate the bodies and joints tag
        self._ambf_yaml['bodies'] = self._body_names_list
        self._ambf_yaml['joints'] = self._joint_names_list
        
        yaml.dump(self._ambf_yaml, output_file)

        header_str = "# AMBF Version: %s\n" \
                     "# Generated By: ambf_addon for Blender %s\n" \
                     "# Link: %s\n" \
                     "# Generated on: %s\n"\
                     % (str(bl_info['version']).replace(', ', '.'),
                        str(bl_info['blender']).replace(', ', '.'),
                        bl_info['wiki_url'],
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        prepend_comment_to_file(output_file_name, header_str)


class SaveMeshes(bpy.types.Operator):
    bl_idname = "ambf.add_save_meshes"
    bl_label = "Save Meshes"
    bl_description = "This saves the meshes in base folder specifed in the field above. Two folders" \
                     " are created in the base folder named, \"high_res\" and \"low_res\" to store the" \
                     " high-res and low-res meshes separately"

    def execute(self, context):
        replace_dot_from_obj_names()
        self.save_meshes(context)
        return {'FINISHED'}

    # This recursive function is specialized to deal with
    # tree based hierarchy. In such cases we have to ensure
    # to move the parent to origin first and then its children successively
    # otherwise moving any parent after its child has been moved with move the
    # child as well
    def set_to_origin(self, p_obj, obj_name_mat_list):
        if p_obj.children is None:
            return
        obj_name_mat_list.append([p_obj.name, p_obj.matrix_world.copy()])
        # Since setting the world transform clears the embedded scale
        # of the object, we need to re-scale the object after putting it to origin
        scale_mat = mathutils.Matrix()
        scale_mat = scale_mat.Scale(p_obj.matrix_world.median_scale, 4)
        p_obj.matrix_world.identity()
        p_obj.matrix_world = scale_mat
        for c_obj in p_obj.children:
            self.set_to_origin(c_obj, obj_name_mat_list)

    # Since Blender exports meshes w.r.t world transform and not the
    # the local mesh transform, we explicitly push each object to origin
    # and remember its world transform for putting it back later on
    def set_all_meshes_to_origin(self):
        obj_name_mat_list = []
        for p_obj in bpy.data.objects:
            if p_obj.parent is None:
                self.set_to_origin(p_obj, obj_name_mat_list)
        return obj_name_mat_list

    # This recursive function works in similar fashion to the
    # set_to_origin function, but uses the know default transform
    # to set the tree back to default in a hierarchial fashion
    def reset_back_to_default(self, p_obj_handle, obj_name_mat_list):
        if p_obj_handle.children is None:
            return
        for item in obj_name_mat_list:
            if p_obj_handle.name == item[0]:
                p_obj_handle.matrix_world = item[1]
        for c_obj_handle in p_obj_handle.children:
            self.reset_back_to_default(c_obj_handle, obj_name_mat_list)

    def reset_meshes_to_original_position(self, obj_name_mat_list):
        for p_obj_handle in bpy.data.objects:
            if p_obj_handle.parent is None:
                self.reset_back_to_default(p_obj_handle, obj_name_mat_list)

    def save_meshes(self, context):
        # First deselect all objects
        select_all_objects(False)

        save_path = bpy.path.abspath(context.scene.ambf_yaml_mesh_path)
        high_res_path = os.path.join(save_path, 'high_res/')
        low_res_path = os.path.join(save_path, 'low_res/')
        os.makedirs(high_res_path, exist_ok=True)
        os.makedirs(low_res_path, exist_ok=True)
        mesh_type = bpy.context.scene['mesh_output_type']

        mesh_name_mat_list = self.set_all_meshes_to_origin()
        for obj_handle in bpy.data.objects:
            # Mesh Type is .stl
            obj_handle.select = True

            obj_handle_name = remove_namespace_prefix(obj_handle.name)

            if obj_handle.type == 'MESH':
                if mesh_type == MeshType.meshSTL.value:
                    obj_name = obj_handle_name + '.STL'
                    filename_high_res = os.path.join(high_res_path, obj_name)
                    filename_low_res = os.path.join(low_res_path, obj_name)
                    bpy.ops.export_mesh.stl(filepath=filename_high_res, use_selection=True, use_mesh_modifiers=False)
                    bpy.ops.export_mesh.stl(filepath=filename_low_res, use_selection=True, use_mesh_modifiers=True)
                elif mesh_type == MeshType.meshOBJ.value:
                    obj_name = obj_handle_name + '.OBJ'
                    filename_high_res = os.path.join(high_res_path, obj_name)
                    filename_low_res = os.path.join(low_res_path, obj_name)
                    bpy.ops.export_scene.obj(filepath=filename_high_res, use_selection=True, use_mesh_modifiers=False)
                    bpy.ops.export_scene.obj(filepath=filename_low_res, use_selection=True, use_mesh_modifiers=True)
                elif mesh_type == MeshType.mesh3DS.value:
                    obj_name = obj_handle_name + '.3DS'
                    filename_high_res = os.path.join(high_res_path, obj_name)
                    filename_low_res = os.path.join(low_res_path, obj_name)
                    # 3DS doesn't support supressing modifiers, so we explicitly
                    # toggle them to save as high res and low res meshes
                    # STILL BUGGY
                    for mod in obj_handle.modifiers:
                        mod.show_viewport = True
                    bpy.ops.export_scene.autodesk_3ds(filepath=filename_low_res, use_selection=True)
                    for mod in obj_handle.modifiers:
                        mod.show_viewport = True
                    bpy.ops.export_scene.autodesk_3ds(filepath=filename_high_res, use_selection=True)
                elif mesh_type == MeshType.meshPLY.value:
                    # .PLY export has a bug in which it only saves the mesh that is
                    # active in context of view. Hence we explicitly select this object
                    # as active in the scene on top of being selected
                    obj_name = obj_handle_name + '.PLY'
                    filename_high_res = os.path.join(high_res_path, obj_name)
                    filename_low_res = os.path.join(low_res_path, obj_name)
                    bpy.context.scene.objects.active = obj_handle
                    bpy.ops.export_mesh.ply(filepath=filename_high_res, use_mesh_modifiers=False)
                    bpy.ops.export_mesh.ply(filepath=filename_low_res, use_mesh_modifiers=True)
                    # Make sure to deselect the mesh
                    bpy.context.scene.objects.active = None

            obj_handle.select = False
        self.reset_meshes_to_original_position(mesh_name_mat_list)


class GenerateLowResMeshModifiers(bpy.types.Operator):
    bl_idname = "ambf.generate_low_res_mesh_modifiers"
    bl_label = "Generate Low-Res Meshes"
    bl_description = "This creates the low-res modifiers for higher speed collision computation" \
                     " . For now, the mesh decimation modifiers are being used but they shall be" \
                     " replaced with other methods"

    def execute(self, context):
        # First off, remove any existing Modifiers:
        bpy.ops.ambf.remove_modifiers()

        # Now deselect all objects
        for obj in bpy.data.objects:
            obj.select = False

        vertices_max = context.scene.mesh_max_vertices
        # Select each object iteratively and generate its low-res mesh
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.hide is False:
                decimate_mod = obj.modifiers.new('decimate_mod', 'DECIMATE')
                if len(obj.data.vertices) > vertices_max:
                    reduction_ratio = vertices_max / len(obj.data.vertices)
                    decimate_mod.use_symmetry = False
                    decimate_mod.use_collapse_triangulate = True
                    decimate_mod.ratio = reduction_ratio
                    decimate_mod.show_viewport = True
        return {'FINISHED'}


class CreateRedundantJoint(bpy.types.Operator):
    bl_idname = "ambf.create_redundant_joint"
    bl_label = "Create Redundant Joint"
    bl_description = "This creates an empty object that can be used to create closed loop mechanisms. Make" \
                     " sure to set the rigid body constraint (RBC) for this empty mesh and ideally parent this empty" \
                     " object with the parent body of its RBC"

    def execute(self, context):
        select_all_objects(False)
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        context.active_object.name = CommonConfig.redundant_joint_prefix[0] + ' joint'
        return {'FINISHED'}


class RemoveModifiers(bpy.types.Operator):
    bl_idname = "ambf.remove_modifiers"
    bl_label = "Remove All Modifiers"
    bl_description = "This removes all the mesh modifiers generated for meshes in the current scene"

    def execute(self, context):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                obj.modifiers.remove(mod)
        return {'FINISHED'}


class ToggleModifiersVisibility(bpy.types.Operator):
    bl_idname = "ambf.toggle_modifiers_visibility"
    bl_label = "Toggle Modifiers Visibility"
    bl_description = "This hides all the mesh modifiers generated for meshes in the current scene"

    def execute(self, context):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_viewport = not mod.show_viewport
        return {'FINISHED'}


class RemoveObjectsNamespaces(bpy.types.Operator):
    bl_idname = "ambf.remove_object_namespaces"
    bl_label = "Remove Object Namespaces"
    bl_description = "This removes any current object namespaces"

    def execute(self, context):
        for obj in bpy.data.objects:
            obj.name = obj.name.split('/')[-1]
        return {'FINISHED'}


class LoadAMBF(bpy.types.Operator):
    bl_idname = "ambf.load_ambf_yaml_config"
    bl_label = "Load AMBF YAML Config"
    bl_description = "This loads an AMBF from the specified config file"

    def __init__(self):
        self._ambf = None
        # A dict of T_c_j frames for each body
        self._body_t_j_c = {}
        self._joint_additional_offset = {}
        # A dict for body name as defined in YAML File and the Name Blender gives
        # the body
        self._blender_remapped_body_names = {}
        self._high_res_path = ''
        self._low_res_path = ''
        self._context = None

    def get_qualified_path(self, path):
        filepath = Path(path)

        if filepath.is_absolute():
            return path
        else:
            ambf_filepath = Path(self._yaml_filepath)
            path = str(ambf_filepath.parent.joinpath(filepath))
            return path

    def load_body(self, body_name):
        body_data = self._ambf[body_name]
        # print(body['name'])
        if 'high resolution path' in body_data:
            body_high_res_path = self.get_qualified_path(body_data['high resolution path'])
        else:
            body_high_res_path = self._high_res_path
        af_name = body_data['name']
        # If body name is world. Check if a world body has already
        # been defined, and if it has been, ignore adding another world body
        if af_name in ['world', 'World', 'WORLD']:
            for temp_obj_handle in bpy.data.objects:
                if temp_obj_handle.type in ['MESH', 'EMPTY']:
                    if temp_obj_handle.name in ['world', 'World', 'WORLD']:
                        self._blender_remapped_body_names[body_name] = temp_obj_handle.name
                        self._body_t_j_c[body_name] = mathutils.Matrix()
                        return
        body_mesh_name = body_data['mesh']
        body_mass = body_data['mass']
        self._body_t_j_c[body_name] = mathutils.Matrix()

        body_location_xyz = {'x': 0, 'y': 0, 'z': 0}
        body_location_rpy = {'r': 0, 'p': 0, 'y': 0}

        if 'location' in body_data:
            if 'position' in body_data['location']:
                body_location_xyz = body_data['location']['position']
            if 'orientation' in body_data['location']:
                body_location_rpy = body_data['location']['orientation']

        mesh_filepath = Path(os.path.join(body_high_res_path, body_mesh_name))
        _is_empty_object = False

        if mesh_filepath.suffix in ['.stl', '.STL']:
            bpy.ops.import_mesh.stl(filepath=str(mesh_filepath.resolve()))

        elif mesh_filepath.suffix in ['.obj', '.OBJ']:
            bpy.ops.import_scene.obj(filepath=str(mesh_filepath.resolve()))

        elif mesh_filepath.suffix in ['.dae', '.DAE']:
            bpy.ops.wm.collada_import(filepath=str(mesh_filepath.resolve()))
            # If we are importing .dae meshes, they can import stuff other than meshes, such as cameras etc.
            # We should remove these extra things and only keep the meshes
            for temp_obj_handle in self._context.selected_objects:
                if temp_obj_handle.type == 'MESH':
                    obj_handle = temp_obj_handle
                    # self._context.scene.objects.active = obj_handle
                else:
                    bpy.data.objects.remove(temp_obj_handle)

            so = bpy.context.selected_objects
            if len(so) > 1:
                self._context.scene.objects.active = so[0]
                bpy.ops.object.join()
                self._context.active_object.name = body_data['name']
                obj_handle = self._context.active_object

                # The lines below are essential in joint the multiple meshes
                # defined in the .dae into one mesh, secondly, making sure that
                # the origin of the mesh is what it is supposed to be as
                # using the join() function call alters the mesh origin
                trans_o = obj_handle.matrix_world.copy()
                obj_handle.matrix_world.identity()
                obj_handle.data.transform(trans_o)

                # Kind of a hack, blender is spawning the collada file
                # a 90 deg offset along the axis axes, this is to correct that
                # Maybe this will not be needed in future versions of blender
                r_x = mathutils.Matrix.Rotation(-1.57, 4, 'X')
                obj_handle.data.transform(r_x)
            else:
                self._context.scene.objects.active = so[0]

        elif mesh_filepath.suffix == '':
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            _is_empty_object = True

        obj_handle = self._context.active_object
        bpy.ops.object.transform_apply(scale=True)

        if 'namespace' in body_data:
            _body_namespace = body_data['namespace']
            obj_handle.name = _body_namespace + af_name
        else:
            obj_handle.name = add_namespace_prefix(af_name)

        self._blender_remapped_body_names[body_name] = obj_handle.name

        if not _is_empty_object:
            if 'color rgba' in body_data:
                mat = bpy.data.materials.new(name=body_name + 'mat')
                mat.diffuse_color[0] = body_data['color rgba']['r']
                mat.diffuse_color[1] = body_data['color rgba']['g']
                mat.diffuse_color[2] = body_data['color rgba']['b']
                mat.use_transparency = True
                mat.transparency_method = 'Z_TRANSPARENCY'
                mat.alpha = body_data['color rgba']['a']
                obj_handle.data.materials.append(mat)

            bpy.ops.rigidbody.object_add()
            if body_mass is 0.0:
                obj_handle.rigid_body.type = 'PASSIVE'
            else:
                obj_handle.rigid_body.mass = body_mass

            # Finall add the rigid body data if defined
            if 'friction' in body_data:
                if 'static' in body_data['friction']:
                    obj_handle.rigid_body.friction = body_data['friction']['static']

            if 'damping' in body_data:
                if 'linear' in body_data['damping']:
                    obj_handle.rigid_body.linear_damping = body_data['damping']['linear']
                if 'angular' in body_data['damping']:
                    obj_handle.rigid_body.angular_damping = body_data['damping']['angular']

            if 'restitution' in body_data:
                obj_handle.rigid_body.restitution = body_data['restitution']

            if 'collision margin' in body_data:
                obj_handle.rigid_body.collision_margin = body_data['collision margin']

            if 'collision shape' in body_data:
                obj_handle.rigid_body.collision_shape = body_data['collision shape']

            if 'collision groups' in body_data:
                col_groups = body_data['collision groups']
                # First clear existing collisoin group of 0
                obj_handle.rigid_body.collision_groups[0] = False
                for group in col_groups:
                    if 0 <= group < 20:
                        obj_handle.rigid_body.collision_groups[group] = True
                    else:
                        print('WARNING, Collision Group Outside [0-20]')

        obj_handle.matrix_world.translation[0] = body_location_xyz['x']
        obj_handle.matrix_world.translation[1] = body_location_xyz['y']
        obj_handle.matrix_world.translation[2] = body_location_xyz['z']
        obj_handle.rotation_euler = (body_location_rpy['r'],
                                     body_location_rpy['p'],
                                     body_location_rpy['y'])




    # print('Remapped Body Names: ', self._blender_remapped_body_names)

    def load_joint(self, joint_name):
        joint_data = self._ambf[joint_name]
        select_all_objects(False)
        self._context.scene.objects.active = None
        parent_body_name = joint_data['parent']
        child_body_name = joint_data['child']
        parent_body_data = self._ambf[parent_body_name]
        child_body_data = self._ambf[child_body_name]
        # Set joint type to blender appropriate name
        joint_type = 'HINGE'
        if 'type' in joint_data:
            if joint_data['type'] in ['hinge', 'revolute', 'continuous']:
                joint_type = 'HINGE'
            elif joint_data['type'] in ['prismatic', 'slider']:
                joint_type = 'SLIDER'
            elif joint_data['type'] in ['fixed', 'FIXED']:
                joint_type = 'FIXED'

        _is_redundant_joint = False

        if 'redundant' in joint_data:
            if joint_data['redundant'] is True or joint_data['redundant'] == 'True':
                _is_redundant_joint = True

        if _is_redundant_joint is True:
            print('INFO, JOINT \"%s\" IS REDUNDANT' % joint_name)
            parent_obj_handle = bpy.data.objects[self._blender_remapped_body_names[parent_body_name]]

            bpy.ops.object.empty_add(type='PLAIN_AXES')
            child_obj_handle = bpy.context.active_object
            joint_name = str(joint_data['name'])

            _has_redundant_prefix = False
            for _redundant_joint_name_str in CommonConfig.redundant_joint_prefix:
                if joint_name.rfind(_redundant_joint_name_str) == 0:
                    _has_redundant_prefix = True

            if _has_redundant_prefix:
                child_obj_handle.name = joint_name
            else:
                child_obj_handle.name = 'redundant joint ' + joint_name

        else:
            parent_obj_handle = bpy.data.objects[self._blender_remapped_body_names[parent_body_name]]
            child_obj_handle = bpy.data.objects[self._blender_remapped_body_names[child_body_name]]

        if 'parent pivot' in joint_data:
            parent_pivot_data = joint_data['parent pivot']
            parent_axis_data = joint_data['parent axis']
            if 'child pivot' in joint_data:
                child_pivot_data = joint_data['child pivot']

                if _is_redundant_joint:
                    child_pivot_data = {'x': 0, 'y': 0, 'z': 0}
                    if joint_data['type'] in ['hinge', 'continuous', 'revolute', 'fixed']:
                        child_axis_data = {'x': 0, 'y': 0, 'z': 1}
                    elif joint_data['type'] in ['prismatic', 'slider']:
                        child_axis_data = {'x': 1, 'y': 0, 'z': 0}
                else:
                    child_axis_data = joint_data['child axis']
                # To fully define a child body's connection and pose in a parent body, just the joint pivots
                # and joint axes are not sufficient. We also need the joint offset which correctly defines
                # the initial pose of the child body in the parent body.
                offset_angle = 0.0
                if not self._context.scene.ignore_ambf_joint_offsets:
                    if 'offset' in joint_data:
                        offset_angle = joint_data['offset']
                # Transformation matrix representing parent in world frame
                t_p_w = parent_obj_handle.matrix_world.copy()
                # Parent's Joint Axis in parent's frame
                parent_axis = mathutils.Vector([parent_axis_data['x'], parent_axis_data['y'], parent_axis_data['z']])
                # Transformation of joint in parent frame
                P_j_p = mathutils.Matrix()
                # P_j_p = P_j_p * r_j_p
                P_j_p.translation = mathutils.Vector(
                    [parent_pivot_data['x'], parent_pivot_data['y'], parent_pivot_data['z']])
                child_axis = mathutils.Vector([child_axis_data['x'], child_axis_data['y'], child_axis_data['z']])
                # Rotation matrix representing child frame in parent frame
                r_c_p, r_c_p_angle = get_rot_mat_from_vecs(child_axis, parent_axis)
                # print ('r_c_p')
                # print(r_c_p)
                # Transformation of joint in child frame
                p_j_c = mathutils.Matrix()
                # p_j_c *= r_j_c
                p_j_c.translation = mathutils.Vector(
                    [child_pivot_data['x'], child_pivot_data['y'], child_pivot_data['z']])
                # print(p_j_c)
                # Transformation of child in joints frame
                P_c_j = p_j_c.copy()
                P_c_j.invert()
                # Offset along constraint axis
                t_c_offset_rot = mathutils.Matrix().Rotation(offset_angle, 4, parent_axis)
                # Transformation of child in parents frame
                t_c_p = t_p_w * P_j_p * t_c_offset_rot * r_c_p * P_c_j
                # Set the child body the pose calculated above
                child_obj_handle.matrix_world = t_c_p
                child_obj_handle.select = True
                parent_obj_handle.select = True
                self._context.scene.objects.active = parent_obj_handle
                bpy.ops.object.parent_set(keep_transform=True)
                self._context.scene.objects.active = child_obj_handle
                child_obj_handle.select = True
                bpy.ops.rigidbody.constraint_add(type=joint_type)
                child_obj_handle.rigid_body_constraint.object1 \
                    = bpy.data.objects[self._blender_remapped_body_names[parent_body_name]]
                child_obj_handle.rigid_body_constraint.object2 \
                    = bpy.data.objects[self._blender_remapped_body_names[child_body_name]]

                if 'joint limits' in joint_data:
                    if joint_data['type'] == 'revolute':
                        child_obj_handle.rigid_body_constraint.limit_ang_z_upper \
                            = joint_data['joint limits']['high'] + offset_angle
                        child_obj_handle.rigid_body_constraint.limit_ang_z_lower \
                            = joint_data['joint limits']['low'] + offset_angle
                        child_obj_handle.rigid_body_constraint.use_limit_ang_z = True
                    elif joint_data['type'] == 'prismatic':
                        child_obj_handle.rigid_body_constraint.limit_lin_x_upper = joint_data['joint limits']['high']
                        child_obj_handle.rigid_body_constraint.limit_lin_x_lower = joint_data['joint limits']['low']
                        child_obj_handle.rigid_body_constraint.use_limit_lin_x = True
                    elif joint_data['type'] == 'continuous':
                        # Do nothing, not enable the limits
                        pass

    def adjust_body_pivots_and_axes(self):
        for joint_name in self._ambf['joints']:
            joint_data = self._ambf[joint_name]
            if 'child pivot' in joint_data:
                if 'redundant' in joint_data:
                    if joint_data['redundant'] is True or joint_data['redundant'] == 'True':
                        print('INFO, JOINT \"%s\" IS REDUNDANT, NO NEED'
                              ' TO ADJUST CHILD BODY\'S AXIS AND PIVOTS' % joint_name)
                        return

                child_body_name = joint_data['child']
                child_pivot_data = joint_data['child pivot']
                child_axis_data = joint_data['child axis']
                parent_axis_data = joint_data['parent axis']

                child_obj_handle = bpy.data.objects[self._blender_remapped_body_names[child_body_name]]

                joint_type = 'HINGE'
                if 'type' in joint_data:
                    if joint_data['type'] in ['hinge', 'revolute', 'continuous']:
                        joint_type = 'HINGE'
                    elif joint_data['type'] in ['prismatic', 'slider']:
                        joint_type = 'SLIDER'
                    elif joint_data['type'] in ['fixed', 'FIXED']:
                        joint_type = 'FIXED'

                # Universal Constraint Axis
                constraint_axis = mathutils.Vector([0, 0, 1])
                # If check is enabled, set the appropriate constraint axis
                if joint_type == 'HINGE':
                    constraint_axis = mathutils.Vector([0, 0, 1])
                elif joint_type == 'SLIDER':
                    constraint_axis = mathutils.Vector([1, 0, 0])
                elif joint_type == 'FIXED':
                    constraint_axis = mathutils.Vector([0, 0, 1])

                # Child's Joint Axis in child's frame
                child_axis = mathutils.Vector([child_axis_data['x'], child_axis_data['y'], child_axis_data['z']])

                # To keep the joint limits intact, we set the constraint axis as
                # negative if the joint axis is negative
                # if any(child_axis[i] < 0.0 for i in range(0, 3)):
                #     constraint_axis = -constraint_axis

                r_j_c, d_angle = get_rot_mat_from_vecs(constraint_axis, child_axis)

                # Transformation of joint in child frame
                p_j_c = mathutils.Matrix()
                p_j_c.translation = mathutils.Vector(
                    [child_pivot_data['x'], child_pivot_data['y'], child_pivot_data['z']])
                # Now apply the rotation based on the axes deflection from constraint_axis
                t_j_c = r_j_c
                t_j_c.translation = p_j_c.translation
                t_c_j = t_j_c.copy()
                t_c_j.invert()
                child_axis_data['x'] = constraint_axis[0]
                child_axis_data['y'] = constraint_axis[1]
                child_axis_data['z'] = constraint_axis[2]

                if child_obj_handle.type != 'EMPTY':
                    child_obj_handle.data.transform(t_c_j)
                self._body_t_j_c[joint_data['child']] = t_c_j

                # Implementing the Alignment Offset Correction Algorithm (AO)

                # Parent's Joint Axis in parent's frame
                parent_axis = mathutils.Vector([parent_axis_data['x'], parent_axis_data['y'], parent_axis_data['z']])

                r_caxis_p, r_cnew_p_angle = get_rot_mat_from_vecs(constraint_axis, parent_axis)
                r_cnew_p = r_caxis_p * t_c_j
                r_c_p, r_c_p_angle = get_rot_mat_from_vecs(child_axis, parent_axis)
                r_p_cnew = r_cnew_p.copy()
                r_p_cnew.invert()
                delta_r = r_p_cnew * r_c_p
                # print('Joint Name: ', joint_name)
                # print('Delta R: ')
                d_axis_angle = delta_r.to_quaternion().to_axis_angle()
                d_axis = round_vec(d_axis_angle[0])
                d_angle = d_axis_angle[1]
                # Sanity Check: The axis angle should be along the the direction of child axis
                # Throw warning if its not
                v_diff = d_axis.cross(child_axis)
                if v_diff.length > 0.1 and abs(d_angle) > 0.1:
                    print('*** WARNING: AXIS ALIGNMENT LOGIC ERROR')
                # print(d_axis, ' : ', d_angle)
                if any(d_axis[i] < 0.0 for i in range(0, 3)):
                    d_angle = - d_angle

                if abs(d_angle) > 0.1:
                    r_ao = mathutils.Matrix().Rotation(d_angle, 4, constraint_axis)
                    child_obj_handle.data.transform(r_ao)
                    self._body_t_j_c[joint_data['child']] = r_ao * t_c_j
                # end of AO algorithm

            # Finally assign joints and set correct positions

    def load_joint_with_adjusted_bodies(self, joint_name):
        joint_data = self._ambf[joint_name]
        select_all_objects(False)
        self._context.scene.objects.active = None
        parent_body_name = joint_data['parent']
        child_body_name = joint_data['child']
        parent_body_data = self._ambf[parent_body_name]
        child_body_data = self._ambf[child_body_name]
         # Set joint type to blender appropriate name
        joint_type = 'HINGE'
        if 'type' in joint_data:
            if joint_data['type'] in ['hinge', 'revolute', 'continuous']:
                joint_type = 'HINGE'
            elif joint_data['type'] in ['prismatic', 'slider']:
                joint_type = 'SLIDER'
            elif joint_data['type'] in ['fixed', 'FIXED']:
                joint_type = 'FIXED'

        _is_redundant_joint = False
        if 'redundant' in joint_data:
            if joint_data['redundant'] is True or joint_data['redundant'] == 'True':
                _is_redundant_joint = True

        if _is_redundant_joint is True:
            print('INFO, JOINT \"%s\" IS REDUNDANT' % joint_name)
            parent_obj_handle = bpy.data.objects[self._blender_remapped_body_names[parent_body_name]]

            bpy.ops.object.empty_add(type='PLAIN_AXES')
            child_obj_handle = bpy.context.active_object
            joint_name = str(joint_data['name'])

            _has_redundant_prefix = False
            for _redundant_joint_name_str in CommonConfig.redundant_joint_prefix:
                if joint_name.rfind(_redundant_joint_name_str) == 0:
                    _has_redundant_prefix = True

            if _has_redundant_prefix:
                child_obj_handle.name = joint_name
            else:
                child_obj_handle.name = 'redundant joint ' + joint_name
        else:
            parent_obj_handle = bpy.data.objects[self._blender_remapped_body_names[parent_body_name]]
            child_obj_handle = bpy.data.objects[self._blender_remapped_body_names[child_body_name]]
        # print('JOINT:', joint_name)
        # print('\tParent: ', parent_obj_handle.name)
        # print('\tChild: ', child_obj_handle.name)
        if 'parent pivot' in joint_data:
            parent_pivot_data = joint_data['parent pivot']
            parent_axis_data = joint_data['parent axis']
            if 'child pivot' in joint_data:
                child_pivot_data = joint_data['child pivot']
                child_axis_data = joint_data['child axis']
                # To fully define a child body's connection and pose in a parent body, just the joint pivots
                # and joint axes are not sufficient. We also need the joint offset which correctly defines
                # the initial pose of the child body in the parent body.
                offset_angle = 0.0
                if not self._context.scene.ignore_ambf_joint_offsets:
                    if 'offset' in joint_data:
                        offset_angle = joint_data['offset']
                # Latest release of blender (2.79) only supports joints along child's z axis
                # which requires a workaround for this limitation. We rotate the joint frame by the
                # angular offset of parent's joint axis, w.r.t to parent's z axis.
                # Transformation matrix representing parent in world frame
                t_p_w = parent_obj_handle.matrix_world.copy()

                # Parent's Joint Axis in parent's frame
                parent_axis = mathutils.Vector([parent_axis_data['x'], parent_axis_data['y'], parent_axis_data['z']])

                # Child's Joint Axis in Child's frame
                child_axis = mathutils.Vector([child_axis_data['x'], child_axis_data['y'], child_axis_data['z']])

                # Transformation of joint in parent frame
                p_j_p = mathutils.Matrix()
                # P_j_p = P_j_p * r_j_p
                p_j_p.translation = mathutils.Vector(
                    [parent_pivot_data['x'], parent_pivot_data['y'], parent_pivot_data['z']])
                # Now we need to transform the child since we could have potentially moved
                # the origin of the mesh in last loop's iterations
                # Child's Joint Axis in child's frame

                # Rotation matrix representing child frame in parent frame
                r_c_p, r_c_p_angle = get_rot_mat_from_vecs(child_axis, parent_axis)
                # print ('r_c_p')
                # print(r_c_p)

                # Offset along constraint axis
                t_c_offset_rot = mathutils.Matrix().Rotation(offset_angle, 4, parent_axis)

                t_p_w_off = self._body_t_j_c[joint_data['parent']]

                # Transformation of child in parents frame
                t_c_p = t_p_w * t_p_w_off * p_j_p * t_c_offset_rot * r_c_p
                # Set the child body the pose calculated above
                child_obj_handle.matrix_world = t_c_p
                child_obj_handle.select = True
                parent_obj_handle.select = True
                self._context.scene.objects.active = parent_obj_handle
                bpy.ops.object.parent_set(keep_transform=True)
                self._context.scene.objects.active = child_obj_handle
                child_obj_handle.select = True
                bpy.ops.rigidbody.constraint_add(type=joint_type)
                child_obj_handle.rigid_body_constraint.object1 \
                    = bpy.data.objects[self._blender_remapped_body_names[parent_body_name]]
                child_obj_handle.rigid_body_constraint.object2 \
                    = bpy.data.objects[self._blender_remapped_body_names[child_body_name]]

                if 'joint limits' in joint_data:
                    if joint_data['type'] in ['revolute', 'hinge']:
                        child_obj_handle.rigid_body_constraint.limit_ang_z_upper \
                            = joint_data['joint limits']['high']
                        child_obj_handle.rigid_body_constraint.limit_ang_z_lower \
                            = joint_data['joint limits']['low']
                        child_obj_handle.rigid_body_constraint.use_limit_ang_z = True
                    elif joint_data['type'] in ['slider', 'prismatic']:
                        child_obj_handle.rigid_body_constraint.limit_lin_x_upper = \
                            joint_data['joint limits']['high']
                        child_obj_handle.rigid_body_constraint.limit_lin_x_lower = \
                            joint_data['joint limits']['low']
                        child_obj_handle.rigid_body_constraint.use_limit_lin_x = True

    def execute(self, context):
        print('HOWDY PARTNER')
        self._yaml_filepath = str(bpy.path.abspath(context.scene['external_ambf_yaml_filepath']))
        print(self._yaml_filepath)
        yaml_file = open(self._yaml_filepath)
        self._ambf = yaml.load(yaml_file)
        self._context = context

        bodies_list = self._ambf['bodies']
        joints_list = self._ambf['joints']

        if 'namespace' in self._ambf:
            set_global_namespace(context, self._ambf['namespace'])
        else:
            set_global_namespace(context, '/ambf/env/')

        num_bodies = len(bodies_list)
        # print('Number of Bodies Specified = ', num_bodies)
        self._high_res_path = self.get_qualified_path(self._ambf['high resolution path'])
        print(self._high_res_path)
        for body_name in bodies_list:
            self.load_body(body_name)

        if context.scene.adjust_joint_pivots is True:
            self.adjust_body_pivots_and_axes()

        for joint_name in joints_list:
            if context.scene.adjust_joint_pivots is True:
                self.load_joint_with_adjusted_bodies(joint_name)
            else:
                self.load_joint(joint_name)

        # print('Printing Blender Remapped Body Names')
        # print(self._blender_remapped_body_names)
        return {'FINISHED'}


class CreateAMBFPanel(bpy.types.Panel):
    """Creates a Panel in the Tool Shelf"""
    bl_label = "AF FILE CREATION"
    bl_idname = "OBJECT_PT_ambf_yaml"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "AMBF"

    bpy.types.Scene.ambf_yaml_conf_path = bpy.props.StringProperty \
      (
        name="Config (Save To)",
        default="",
        description="Define the root path of the project",
        subtype='FILE_PATH'
      )

    bpy.types.Scene.ambf_yaml_mesh_path = bpy.props.StringProperty \
      (
        name="Meshes (Save To)",
        default="",
        description = "Define the path to save to mesh files",
        subtype='DIR_PATH'
      )

    bpy.types.Scene.mesh_output_type = bpy.props.EnumProperty \
        (
            items=[('STL', 'STL', 'STL'),('OBJ', 'OBJ', 'OBJ'),('3DS', '3DS', '3DS'),('PLY', 'PLY', 'PLY')],
            name="Mesh Type"
        )

    # bpy.context.scene['mesh_output_type'] = 0

    bpy.types.Scene.mesh_max_vertices = bpy.props.IntProperty \
        (
            name="",
            default=150,
            description="The maximum number of vertices the low resolution collision mesh is allowed to have",
        )

    bpy.types.Scene.adjust_joint_pivots = bpy.props.BoolProperty \
        (
            name="Adjust Child Pivots",
            default=True,
            description="If the child axis is offset from the joint axis, correct for this offset, keep this to "
                        "default (True) unless you want to debug the model or something advanced",
        )

    bpy.types.Scene.ignore_ambf_joint_offsets = bpy.props.BoolProperty \
        (
            name="Ignore Offsets",
            default=False,
            description="Ignore the joint offsets from ambf yaml file, keep this to default (False) "
                        "unless you want to debug the model or something advanced",
        )

    bpy.types.Scene.ignore_inter_collision = bpy.props.BoolProperty \
            (
            name="Ignore Inter-Collision",
            default=True,
            description="Ignore collision between all the bodies in the scene (default = True)",
        )

    bpy.types.Scene.external_ambf_yaml_filepath = bpy.props.StringProperty \
        (
            name="AMBF Config",
            default="",
            description="Load AMBF YAML FILE",
            subtype='FILE_PATH'
        )

    bpy.types.Scene.ambf_namespace = bpy.props.StringProperty \
        (
            name="AMBF Namespace",
            default="/ambf/env/",
            description="The namespace for all bodies in this scene"
        )

    setup_yaml()

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        # Panel Label
        row.label(text="Step 1: GENERATE LOW-RES COLLISION MESH MODIFIERS")

        # Mesh Reduction Ratio Properties
        row = box.row(align=True)
        row.alignment = 'LEFT'
        split = row.split(percentage=0.7)
        row = split.row()
        row.label('Coll Mesh Max Verts: ')
        row = split.row()
        row.prop(context.scene, 'mesh_max_vertices')

        # Low Res Mesh Modifier Button
        col = box.column()
        col.alignment = 'CENTER'
        col.operator("ambf.generate_low_res_mesh_modifiers")

        # Panel Label
        row = box.row()
        box.label(text="Step 2: SELECT LOCATION AND SAVE MESHES")

        # Meshes Save Location
        col = box.column()
        col.prop(context.scene, 'ambf_yaml_mesh_path')

        # Select the Mesh-Type for saving the meshes
        col = box.column()
        col.alignment = 'CENTER'
        col.prop(context.scene, 'mesh_output_type')

        # Meshes Save Button
        col = box.column()
        col.alignment = 'CENTER'
        col.operator("ambf.add_save_meshes")

        row = box.row()
        row.label(text="Step 3: GENERATE AMBF CONFIG")

        row = box.row()
        row.label(text="Step 3a: AMBF CONFIG PATH")
        # Config File Save Location
        col = box.column()
        col.prop(context.scene, 'ambf_yaml_conf_path')
        # AMBF Namespace
        col = box.column()
        col.alignment = 'CENTER'
        col.prop(context.scene, 'ambf_namespace')
        # Config File Save Button
        row = box.row()
        row.label(text="Step 3a: SAVE AMBF CONFIG")

        # Ignore Inter Collision Button
        col = box.column()
        col.alignment = 'CENTER'
        col.prop(context.scene, "ignore_inter_collision")

        col = box.column()
        col.alignment = 'CENTER'
        col.operator("ambf.add_create_ambf_config")

        box = layout.box()
        row = box.row()
        row.label(text="OPTIONAL :")

        row = box.row()
        # Column for creating redundant joint
        col = box.column()
        col.alignment = 'CENTER'
        col.operator("ambf.remove_object_namespaces")

        # Column for creating redundant joint
        col = box.column()
        col.alignment = 'CENTER'
        col.operator("ambf.create_redundant_joint")

        # Add Optional Button to Remove All Modifiers
        col = box.column()
        col.alignment = 'CENTER'
        col.operator("ambf.remove_modifiers")

        # Add Optional Button to Toggle the Visibility of Low-Res Modifiers
        col = box.column()
        col.alignment = 'CENTER'
        col.operator("ambf.toggle_modifiers_visibility")

        box = layout.box()
        row = box.row()
        # Load AMBF File Into Blender
        row.label(text="LOAD AMBF FILE :")

        # Load
        col = box.column()
        col.alignment = 'CENTER'
        col.prop(context.scene, 'adjust_joint_pivots')

        # Load
        col = box.column()
        col.alignment = 'CENTER'
        col.prop(context.scene, 'ignore_ambf_joint_offsets')

        # Load
        col = box.column()
        col.alignment = 'CENTER'
        col.prop(context.scene, 'external_ambf_yaml_filepath')
        
        col = box.column()
        col.alignment = 'CENTER'
        col.operator("ambf.load_ambf_yaml_config")


def register():
    bpy.utils.register_class(ToggleModifiersVisibility)
    bpy.utils.register_class(RemoveModifiers)
    bpy.utils.register_class(GenerateLowResMeshModifiers)
    bpy.utils.register_class(GenerateAMBF)
    bpy.utils.register_class(SaveMeshes)
    bpy.utils.register_class(LoadAMBF)
    bpy.utils.register_class(CreateAMBFPanel)
    bpy.utils.register_class(CreateRedundantJoint)
    bpy.utils.register_class(RemoveObjectsNamespaces)


def unregister():
    bpy.utils.unregister_class(ToggleModifiersVisibility)
    bpy.utils.unregister_class(RemoveModifiers)
    bpy.utils.unregister_class(GenerateLowResMeshModifiers)
    bpy.utils.unregister_class(GenerateAMBF)
    bpy.utils.unregister_class(SaveMeshes)
    bpy.utils.unregister_class(LoadAMBF)
    bpy.utils.unregister_class(CreateAMBFPanel)
    bpy.utils.unregister_class(CreateRedundantJoint)
    bpy.utils.unregister_class(RemoveObjectsNamespaces)


if __name__ == "__main__":
    register()