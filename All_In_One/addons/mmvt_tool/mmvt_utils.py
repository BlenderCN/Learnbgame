import colorsys
# Blender and addon libs
try:
    import bpy
    import bmesh
    import mathutils
    import colors_utils as cu
except:
    pass
    # print("Can't import bpy, mathutils and color_utils")

# Not vanilla python libs
try:
    import numpy as np
except:
    pass


try:
    import scipy
    SCIPY_EXIST = True
except:
    SCIPY_EXIST = False

try:
    import mne
    MNE_EXIST = True
except:
    MNE_EXIST = False


try:
    import nibabel as nib
    NIB_EXIST = True
except:
    NIB_EXIST = False

import traceback
import math
import sys
import os
import os.path as op
import re
import shutil
import uuid
from collections import OrderedDict, Iterable
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT
from multiprocessing.connection import Client
import threading
from queue import Queue, Empty
import cProfile
from itertools import chain
from sys import platform as _platform
from datetime import datetime
import glob
import functools
import importlib

_addon = None


class empty_bpy(object):
    class types(object):
        class Scene(object): pass
        class Panel(object): pass
        Operator = object
    class props(object):
        class BoolProperty(object):
            def __init__(self, **kargs): pass
        class EnumProperty(object):
            def __init__(self, **kargs): pass
        class FloatProperty(object):
            def __init__(self, **kargs): pass
        class IntProperty(object):
            def __init__(self, **kargs): pass


class empty_bpy_extras(object):
    class io_utils(object):
        class ExportHelper(object): pass

try:
    import connections_panel as con_pan
except:
    try:
        sys.path.append(op.split(__file__)[0])
        import connections_panel as con_pan
    except:
        pass
        # print('no bpy')

IS_LINUX = _platform == "linux" or _platform == "linux2"
IS_MAC = _platform == "darwin"
IS_WINDOWS = _platform == "win32"

# print('platform: {}'.format(_platform))

HEMIS = ['rh', 'lh']
INF_HEMIS = ['inflated_{}'.format(hemi) for hemi in HEMIS]
(OBJ_TYPE_CORTEX_RH, OBJ_TYPE_CORTEX_LH, OBJ_TYPE_CORTEX_INFLATED_RH, OBJ_TYPE_CORTEX_INFLATED_LH, OBJ_TYPE_SUBCORTEX,
    OBJ_TYPE_ELECTRODE, OBJ_TYPE_EEG, OBJ_TYPE_CEREBELLUM, OBJ_TYPE_CON, OBJ_TYPE_CON_VERTICE, OBJ_TYPE_LABEL) = \
    range(11)
OBJ_TYPES_ROIS = [OBJ_TYPE_CORTEX_RH, OBJ_TYPE_CORTEX_LH, OBJ_TYPE_CORTEX_INFLATED_RH, OBJ_TYPE_CORTEX_INFLATED_LH]

show_hide_icon = dict(show='RESTRICT_VIEW_OFF', hide='RESTRICT_VIEW_ON')

try:
    import cPickle as pickle
except:
    import pickle

try:
    from scripts import scripts_utils as su
    importlib.reload(su)
except:
    from src.mmvt_addon.scripts import scripts_utils as su

get_link_dir = su.get_link_dir
get_links_dir = su.get_links_dir
get_resources_dir = su.get_resources_dir
get_mmvt_dir = su.get_mmvt_dir
get_subjects_dir = su.get_subjects_dir
get_subject_dir = su.get_subject_dir
get_fmri_dir = su.get_fmri_dir
get_real_atlas_name = su.get_real_atlas_name
get_parent_fol = su.get_parent_fol
select_one_file = su.select_one_file
is_true = su.is_true


def get_fmri_dir():
    return get_link_dir(get_links_dir(), 'fMRI')


floats_const_pattern = r"""
     [-+]?
     (?: \d* \. \d+ )
     """
floats_pattern_rx = re.compile(floats_const_pattern, re.VERBOSE)

numeric_const_pattern = r"""
     [-+]? # optional sign
     (?:
         (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
         |
         (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
     )
     # followed by optional exponent part if desired
     # (?: [Ee] [+-]? \d+ ) ?
     """
numeric_pattern_rx = re.compile(numeric_const_pattern, re.VERBOSE)


def get_hemis_objs():
    return [bpy.data.objects[obj_name] for obj_name in INF_HEMIS]


def read_floats_rx(str):
    return floats_pattern_rx.findall(str)


def read_numbers_rx(str):
    return numeric_pattern_rx.findall(str)


def is_mac():
    return IS_MAC


def is_windows():
    return IS_WINDOWS


def is_linux():
    return IS_LINUX


def namebase(fname):
    name_with_ext = fname.split(op.sep)[-1]
    if not name_with_ext.endswith('nii.gz'):
        ret = '.'.join(name_with_ext.split('.')[:-1])
        return ret if ret != '' else name_with_ext
    else:
        return name_with_ext[:-len('.nii.gz')]


# def namebase(file_name):
#     if file_name[-1] == op.sep:
#         file_name = file_name[:-1]
#     return op.splitext(op.basename(file_name))[0]


def namebase_with_ext(fname):
    return fname.split(op.sep)[-1]


def get_fname_folder(fname):
    return op.sep.join(fname.split(op.sep)[:-1])


def get_current_fol():
    return op.dirname(op.realpath(__file__))


def file_type(fname):
    if fname.endswith('nii.gz'):
        return 'nii.gz'
    else:
        return fname.split('.')[-1]


def change_fname_extension(fname, new_extension):
    return op.join(get_fname_folder(fname), '{}.{}'.format(namebase(fname), new_extension))


def get_obj(obj_name):
    return bpy.data.objects.get(obj_name, None)


@functools.lru_cache(maxsize=None)
def file_fol():
    return os.path.dirname(bpy.data.filepath)


def save(obj, fname):
    with open(fname, 'wb') as fp:
        pickle.dump(obj, fp, protocol=4)


def load(fname):
    with open(fname, 'rb') as fp:
        obj = pickle.load(fp)
    if obj is None:
        print('the data in {} is None!'.format(fname))
    return obj


class Bag( dict ):
    """ a dict with d.key short for d["key"]
        d = Bag( k=v ... / **dict / dict.items() / [(k,v) ...] )  just like dict
    """
        # aka Dotdict

    def __init__(self, *args, **kwargs):
        dict.__init__( self, *args, **kwargs )
        self.__dict__ = self

    def __getnewargs__(self):  # for cPickle.dump( d, file, protocol=-1)
        return tuple(self)


def add_keyframe(parent_obj, conn_name, value, T):
    try:
        insert_keyframe_to_custom_prop(parent_obj, conn_name, 0, 0)
        insert_keyframe_to_custom_prop(parent_obj, conn_name, value, 1)
        insert_keyframe_to_custom_prop(parent_obj, conn_name, value, T)
        insert_keyframe_to_custom_prop(parent_obj, conn_name, 0, T + 1)
        # print('insert keyframe with value of {}'.format(value))
    except:
        print("Can't add a keyframe! {}, {}, {}".format(parent_obj, conn_name, value))
        print(traceback.format_exc())


def insert_keyframe_to_custom_prop(obj, prop_name, value, keyframe):
    bpy.context.scene.objects.active = obj
    obj.select = True
    obj[prop_name] = value
    obj.keyframe_insert(data_path='[' + '"' + prop_name + '"' + ']', frame=keyframe)


def get_object(obj_name, default=None):
    return bpy.data.objects.get(obj_name, default)


def delete_current_obj():
    bpy.ops.object.delete()


def create_and_set_material(obj):
    # curMat = bpy.data.materials['OrigPatchesMat'].copy()
    if obj.active_material is None or obj.active_material.name != obj.name + '_Mat':
        if obj.name + '_Mat' in bpy.data.materials:
            cur_mat = bpy.data.materials[obj.name + '_Mat']
        else:
            cur_mat = bpy.data.materials['Deep_electrode_mat'].copy()
            cur_mat.name = obj.name + '_Mat'
        # Wasn't it originally (0, 0, 1, 1)?
        cur_mat.node_tree.nodes["RGB"].outputs[0].default_value = (1, 1, 1, 1) # (0, 0, 1, 1) # (0, 1, 0, 1)
        obj.active_material = cur_mat


# def mark_objects(objs_names):
#     for obj_name in objs_names:
#         if bpy.data.objects.get(obj_name):
#             bpy.data.objects[obj_name].active_material = bpy.data.materials['selected_label_Mat']


def cylinder_between(p1, p2, r, layers_array):
    # From http://blender.stackexchange.com/questions/5898/how-can-i-create-a-cylinder-linking-two-points-with-python
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    dist = math.sqrt(dx**2 + dy**2 + dz**2)

    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=dist, location=(dx/2 + x1, dy/2 + y1, dz/2 + z1))#, layers=layers_array)

    phi = math.atan2(dy, dx)
    theta = math.acos(dz/dist)
    bpy.context.object.rotation_euler[1] = theta
    bpy.context.object.rotation_euler[2] = phi
    bpy.ops.object.move_to_layer(layers=layers_array)


def create_bezier_curve(obj1, obj2, layers_array, bevel_depth=0.1, resolution_u=1):
    bpy.ops.curve.primitive_bezier_curve_add()
    obj = bpy.context.active_object
    obj.location = (0, 0, 0)
    curve = obj.data
    curve.dimensions = '3D'
    curve.fill_mode = 'FULL'
    curve.splines[0].bezier_points[0].co = obj1.location
    curve.splines[0].bezier_points[1].co = obj2.location
    curve.bevel_depth = bevel_depth
    curve.resolution_u = resolution_u
    bpy.ops.object.move_to_layer(layers=layers_array)


def hook_curves(o1, o2, co1, co2, bevel_depth=0.1, resolution_u=5):
    # https://blender.stackexchange.com/questions/51745/moving-cylinders-into-specific-points
    # https://blender.stackexchange.com/questions/13484/using-python-to-create-a-curve-and-attach-its-endpoints-with-hooks-to-two-sphere?rq=1
    # https://blender.stackexchange.com/questions/43468/low-level-location-rotation-and-scale-for-sphere-cylinders/43631#43631
    x1, y1, z1 = co1
    x2, y2, z2 = co2
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1

    scn = bpy.context.scene
    curve = bpy.data.curves.new("link", 'CURVE')
    curve.dimensions = '3D'
    curve.fill_mode = 'FULL'
    curve.bevel_depth = bevel_depth

    spline = curve.splines.new('BEZIER')
    spline.resolution_u = resolution_u

    spline.bezier_points.add(1)
    p0 = spline.bezier_points[0]
    p1 = spline.bezier_points[1]
    p0.co = (dx/2 + x1, dy/2 + y1, dz/2 + z1) #o1.location / 10
    p0.handle_right_type = 'VECTOR'
    p1.co = (-dx/2 + x2, -dy/2 + y2, -dz/2 + z2) #o2.location / 10
    p1.handle_left_type = 'VECTOR'

    obj = bpy.data.objects.new("link", curve)

    m0 = obj.modifiers.new("alpha", 'HOOK')
    m0.object = o1
    m1 = obj.modifiers.new("beta", 'HOOK')
    m1.object = o2

    scn.objects.link(obj)
    scn.objects.active = obj

    # using anything in bpy.ops is a giant pain in the butt
    bpy.ops.object.mode_set(mode='EDIT')

    # the mode_set() invalidated the pointers, so get fresh ones
    p0 = curve.splines[0].bezier_points[0]
    p1 = curve.splines[0].bezier_points[1]

    p0.co[2] = co1[2] + dz/2
    p1.co[2] = co2[2] - dz/2

    p0.select_control_point = True
    bpy.ops.object.hook_assign(modifier="alpha")

    p0.select_control_point = False
    p1.select_control_point = True
    bpy.ops.object.hook_assign(modifier="beta")
    bpy.ops.object.mode_set(mode='OBJECT')


def create_cubes(data, values, vol_tkreg, indices, data_min, data_max, name, cm, radius=0.1,
                 parent='Functional maps', material_name='Deep_electrode_mat'):
    # https://stackoverflow.com/questions/48818274/quickly-adding-large-numbers-of-mesh-primitives-in-blender
    _addon.data.create_empty_if_doesnt_exists(name, _addon.BRAIN_EMPTY_LAYER, None, parent)
    orig_cube = create_cube(_addon.ACTIVITY_LAYER, radius=0.1)
    orig_cube.name = 'original_cube'
    orig_mat = bpy.data.materials[material_name]
    materials = {}
    colors_ratio = 256 / (data_max - data_min)
    colors_indices = calc_colors_indices(values, data_min, colors_ratio)
    colors = calc_colors_from_indices_cm(colors_indices, cm)
    now, N = time.time(), len(indices)
    dxyzs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    inner_cubes = 0
    for run, (voxel, ind, color, color_ind) in enumerate((zip(vol_tkreg, indices, colors, colors_indices))):
        time_to_go(now, run, N, 1000)
        # Don't create inner or lonely cubes
        if all([data[tuple(ind + dxyz)] >= data_min for dxyz in dxyzs]) or \
                all([data[tuple(ind + dxyz)] < data_min for dxyz in dxyzs]):
            inner_cubes += 1
            continue
        cube_name = 'cube_{}_{}_{}_{}'.format(name[:3], ind[0], ind[1], ind[2])
        cur_obj = get_object(cube_name)
        curr_material_name = 'cube_{}'.format(color_ind)
        if curr_material_name not in materials:
            print('New material was created for color ind {}'.format(color_ind))
            materials[curr_material_name] = orig_mat.copy()
            materials[curr_material_name].name = curr_material_name
        if cur_obj is not None:
            color_obj(materials[curr_material_name], color)
        else:
            copy_cube(orig_cube, voxel * 0.1, cube_name, name, materials[curr_material_name], color)
    print('{} inner cubes out of {} ({:.2f}%)'.format(inner_cubes, N, (inner_cubes / N) * 100))
    # Deleting the original cube
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[orig_cube.name].select = True
    bpy.ops.object.delete()
    print('create_cubes: Finish!')


def create_cube(layer, radius=0.1):
    layers = [False] * 20
    layers[layer] = True
    bpy.ops.mesh.primitive_cube_add(radius=radius)
    bpy.ops.object.move_to_layer(layers=layers)
    return bpy.context.active_object


def copy_cube(orig_cube, pos, cube_name, name, material, color=(1, 1, 1)):
    m = orig_cube.data.copy()
    cur_obj = bpy.data.objects.new('cube', m)
    cur_obj.name = cube_name
    cur_obj.active_material = material
    cur_obj.location = mathutils.Vector(tuple(pos))
    cur_obj.parent = bpy.data.objects[name]
    color_obj(material, color)
    bpy.context.scene.objects.link(cur_obj)
    return cur_obj


def color_obj(cur_mat, color):
    cur_mat.node_tree.nodes["RGB"].outputs[0].default_value = (color[0], color[1], color[2], 1)
    cur_mat.diffuse_color = color[:3]


def create_empty_if_doesnt_exists(name, brain_layer, layers_array=None, root_fol='Brain'):
    # if not bpy.data.objects.get(root_fol):
    #     print('root fol, {}, does not exist'.format(root_fol))
    #     return
    if layers_array is None:
        # layers_array = bpy.context.scene.layers
        layers_array = [False] * 20
        layers_array[brain_layer] = True
    if bpy.data.objects.get(name) is None:
        # layers_array[brain_layer] = True
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=(0, 0, 0), layers=layers_array)
        bpy.ops.object.move_to_layer(layers=layers_array)
        bpy.data.objects['Empty'].name = name
        if name != root_fol:
            bpy.data.objects[name].parent = bpy.data.objects[root_fol]
    return bpy.data.objects[name]


def select_hierarchy(obj, val=True, select_parent=True):
    if bpy.data.objects.get(obj) is not None:
        bpy.data.objects[obj].select = select_parent
        for child in bpy.data.objects[obj].children:
            if val:
                child.hide_select = False
            child.select = val


def create_material(name, diffuseColors, transparency, copy_material=True):
    curMat = None
    if bpy.context.active_object is not None:
        curMat = bpy.context.active_object.active_material
    if curMat is None or copy_material or 'MyColor' not in curMat.node_tree.nodes:
        #curMat = bpy.data.materials['OrigPatchesMat'].copy()
        curMat = bpy.data.materials['OrigPatchMatTwoCols'].copy()
        curMat.name = name
        bpy.context.active_object.active_material = curMat
    curMat.node_tree.nodes['MyColor'].inputs[0].default_value = diffuseColors
    curMat.node_tree.nodes['MyColor1'].inputs[0].default_value = diffuseColors
    curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = transparency
    bpy.context.active_object.active_material.diffuse_color = diffuseColors[:3]


def delete_hierarchy(parent_obj_name, exceptions=(), delete_only_animation=False):
    def get_child_names(obj):
        for child in obj.children:
            names.add(child.name)
            if child.children:
                get_child_names(child)

    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.data.objects.get(parent_obj_name)
    if obj is None:
        return
    obj.animation_data_clear()
    # Go over all the objects in the hierarchy like @zeffi suggested:
    names = set()
    get_child_names(obj)
    names = names - set(exceptions)
    # Remove the animation from the all the child objects
    for child_name in names:
        bpy.data.objects[child_name].animation_data_clear()

    bpy.context.scene.objects.active = obj
    if not delete_only_animation:
        objects = bpy.data.objects
        [setattr(objects[n], 'select', True) for n in names]
        result = bpy.ops.object.delete()
        if result == {'FINISHED'}:
            print ("Successfully deleted object")
        else:
            print ("Could not delete object")


def delete_object(obj_name):
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return
    bpy.ops.object.select_all(action='DESELECT')
    obj.animation_data_clear()
    obj.select = True
    result = bpy.ops.object.delete()
    if result == {'FINISHED'}:
        print("Successfully deleted {}".format(obj_name))
    else:
        print("Could not delete {}".format(obj_name))


@functools.lru_cache(maxsize=None)
def get_atlas():
    # name_split = namebase(bpy.data.filepath).split('_')
    # if len(name_split) > 1:
    #     return name_split[1]
    # else:
    #     return default
    blend_fname = namebase(bpy.data.filepath)
    if blend_fname.find('_') == -1:
        print("Can't find the atlas in the blender file! The Blender's file name needs to end with " + \
                        "'_atlas-name.blend' (sub1_dkt.blend for example)")
        return ''
    atlas = blend_fname.split('_')[-1]
    real_atlas_name = get_real_atlas_name(atlas)
    real_atlas_name = fix_atlas_name(get_user(), real_atlas_name, get_subjects_dir())
    print('Real atlas name {}'.format(real_atlas_name))
    return real_atlas_name


def atlas_exist(subject, atlas, subjects_dir):
    return both_hemi_files_exist(get_atlas_template(subject, atlas, subjects_dir))


def get_atlas_template(subject, atlas, subjects_dir):
    return op.join(subjects_dir, subject, 'label', '{}.{}.annot'.format('{hemi}', atlas))


def fix_atlas_name(subject, atlas, subjects_dir=''):
    if atlas in ['dkt', 'dkt40', 'aparc.DKTatlas', 'aparc.DKTatlas40']:
        if os.environ.get('FREESURFER_HOME', '') != '':
            if op.isfile(op.join(os.environ.get('FREESURFER_HOME'), 'average', 'rh.DKTatlas.gcs')):
                atlas = 'aparc.DKTatlas'
            elif op.isfile(op.join(os.environ.get('FREESURFER_HOME'), 'average', 'rh.DKTatlas40.gcs')):
                atlas = 'aparc.DKTatlas40'
        else:
            if not atlas_exist(subject, 'aparc.DKTatlas', subjects_dir) and \
                    atlas_exist(subject, 'aparc.DKTatlas40', subjects_dir):
                atlas = 'aparc.DKTatlas40'
            elif not atlas_exist(subject, 'aparc.DKTatlas40', subjects_dir) and \
                    atlas_exist(subject, 'aparc.DKTatlas', subjects_dir):
                atlas = 'aparc.DKTatlas'
    return atlas



# def get_real_atlas_name(atlas, csv_fol='', short_name=False):
#     if csv_fol == '':
#         csv_fol = get_mmvt_root()
#     csv_fname = op.join(csv_fol, 'atlas.csv')
#     real_atlas_name = ''
#     if op.isfile(csv_fname):
#         for line in csv_file_reader(csv_fname, ',', 1):
#             if len(line) < 2:
#                 continue
#             if atlas in [line[0], line[1]]:
#                 real_atlas_name = line[1]
#                 break
#         if real_atlas_name == '':
#             print("Can't find the atlas {} in {}! Please add it to the csv file.".format(atlas, csv_fname))
#             return atlas
#         return real_atlas_name
#     else:
#         print('No atlas file was found! Please create a atlas file (csv) in {}, where '.format(csv_fname) +
#                         'the columns are name in blend file, annot name, description')
#         return ''


def get_mmvt_fol():
    return bpy.path.abspath('//')


@functools.lru_cache(maxsize=None)
def get_user_fol():
    root_fol = bpy.path.abspath('//')
    user = get_user()
    return op.join(root_fol, user)


def view_all_in_graph_editor(context=None):
    try:
        if context is None:
            context = bpy.context
        graph_area = [context.screen.areas[k] for k in range(len(context.screen.areas)) if
                      context.screen.areas[k].type == 'GRAPH_EDITOR'][0]
        graph_window_region = [graph_area.regions[k] for k in range(len(graph_area.regions)) if
                               graph_area.regions[k].type == 'WINDOW'][0]
        # ui = [graph_area.regions[k] for k in range(len(graph_area.regions)) if graph_area.regions[k].type == 'UI'][0]

        c = context.copy()  # copy the context
        c['area'] = graph_area
        c['region'] = graph_window_region
        bpy.ops.graph.view_all(c)
    except:
        pass


def show_hide_hierarchy(val, obj, also_parent=False, select=True):
    if isinstance(obj, str):
        obj = bpy.data.objects.get(obj, None)
    if obj is None:
        print('show_hide_hierarchy: obj is None!')
        return
    if also_parent:
        obj.hide_render = not val
    for child in obj.children:
        child.hide = not val
        child.hide_render = not val
        if select:
            child.select = val


def show_hide_obj(obj, val=True):
    obj.hide = not val
    obj.hide_render = not val


def rand_letters(num):
    return str(uuid.uuid4())[:num]


def evaluate_fcurves(parent_obj, time_range, specific_condition=None):
    data = OrderedDict()
    colors = OrderedDict()
    for fcurve in parent_obj.animation_data.action.fcurves:
        if fcurve.hide:
            continue
        name = fcurve.data_path.split('"')[1]
        if not specific_condition is None:
            cond = name[len(parent_obj.name) + 1:]
            if cond != specific_condition:
                continue
        print('{} extrapolation'.format(name))
        # todo: we should return the interpolation to its previous value
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'BEZIER'
        data[name] = []
        for t in time_range:
            d = fcurve.evaluate(t)
            data[name].append(d)
        colors[name] = tuple(fcurve.color)
    return data, colors


def get_fcurve_current_frame_val(parent_obj_name, obj_name, cur_frame):
    for fcurve in bpy.data.objects[parent_obj_name].animation_data.action.fcurves:
        name = get_fcurve_name(fcurve)
        if name == obj_name:
            return fcurve.evaluate(cur_frame)


def get_fcurve_name(fcurve):
    return fcurve.data_path.split('"')[1].replace(' ', '')


def show_only_selected_fcurves(context):
    space = context.space_data
    dopesheet = space.dopesheet
    dopesheet.show_only_selected = True


# def get_fcurve_values(parent_name, fcurve_name):
#     xs, ys = [], []
#     parent_obj = bpy.data.objects[parent_name]
#     for fcurve in parent_obj.animation_data.action.fcurves:
#         if get_fcurve_name(fcurve) == fcurve_name:
#             for kp in fcurve.keyframe_points:
#                 xs.append(kp.co[0])
#                 ys.append(kp.co[1])
#     return xs, ys


def time_to_go(now, run, runs_num, runs_num_to_print=10, thread=-1, do_write_to_stderr=False):
    if run % runs_num_to_print == 0 and run != 0:
        time_took = time.time() - now
        more_time = time_took / run * (runs_num - run)
        if thread > 0:
            str = '{}: {}/{}, {:.2f}s, {:.2f}s to go!'.format(thread, run, runs_num, time_took, more_time)
        else:
            str = '{}/{}, {:.2f}s, {:.2f}s to go!'.format(run, runs_num, time_took, more_time)
        if do_write_to_stderr:
            write_to_stderr(str)
        else:
            print(str)


def show_hide_obj_and_fcurves(objs, val, exclude=[]):
    if not isinstance(objs, Iterable):
        objs = [objs]
    for obj in objs:
        if obj.name in exclude:
            continue
        obj.select = val
        if obj.animation_data:
            for fcurve in obj.animation_data.action.fcurves:
                fcurve_name = get_fcurve_name(fcurve)
                if fcurve_name in exclude:
                    fcurve.hide = True
                    fcurve.select = False
                else:
                    fcurve.hide = not val
                    fcurve.select = val
        else:
            pass
            # print('No animation in {}'.format(obj.name))


def message(self, message):
    # todo: Find how to send messaages without the self
    if self:
        self.report({'ERROR'}, message)
    else:
        print(message)


def show_only_group_objects(objects, group_name='new_filter'):
    ge = get_the_graph_editor()
    dopesheet = ge.dopesheet
    # space = context.space_data
    # dopesheet = space.dopesheet
    selected_group = bpy.data.groups.get(group_name, bpy.data.groups.new(group_name))
    for obj in objects:
        if isinstance(obj, str):
            obj = bpy.data.objects[obj]
        selected_group.objects.link(obj)
    dopesheet.filter_group = selected_group
    dopesheet.show_only_group_objects = True


def create_sphere(loc, rad, my_layers, name):
    bpy.ops.mesh.primitive_uv_sphere_add(
        ring_count=30, size=rad, view_align=False, enter_editmode=False, location=loc, layers=my_layers)
    bpy.ops.object.shade_smooth()
    bpy.context.active_object.name = name


def create_ico_sphere(location, layers, name, size=.3, subdivisions=2, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_ico_sphere_add(
        location=location, layers=layers, size=size, subdivisions=subdivisions,rotation=rotation)
    bpy.ops.object.shade_smooth()
    bpy.context.active_object.name = name
    return bpy.context.active_object


def create_spline(points, layers_array, bevel_depth=0.045, resolution_u=5):
    # points = [ [1,1,1], [-1,1,1], [-1,-1,1], [1,-1,-1] ]
    curvedata = bpy.data.curves.new(name="Curve", type='CURVE')
    curvedata.dimensions = '3D'
    curvedata.fill_mode = 'FULL'
    curvedata.bevel_depth = bevel_depth
    ob = bpy.data.objects.new("CurveObj", curvedata)
    bpy.context.scene.objects.link(ob)

    spline = curvedata.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for num in range(len(spline.bezier_points)):
        spline.bezier_points[num].co = points[num]
        spline.bezier_points[num].handle_right_type = 'AUTO'
        spline.bezier_points[num].handle_left_type = 'AUTO'
    spline.resolution_u = resolution_u
    #spline.order_u = 6
    #spline.use_bezier_u = True
    #spline.radius_interpolation = 'BSPLINE'
    #print(spline.type)
    #spline.use_smooth = True
    bpy.ops.object.move_to_layer(layers=layers_array)
    return ob


def get_subfolders(fol):
    return [os.path.join(fol,subfol) for subfol in os.listdir(fol) if os.path.isdir(os.path.join(fol,subfol))]


def hemi_files_exists(fname):
    if '*' in fname or '?' in fname:
        return len(glob.glob(fname.format(hemi='rh'))) >= 1 and len(glob.glob(fname.format(hemi='rh'))) >= 1
    else:
        return os.path.isfile(fname.format(hemi='rh')) and os.path.isfile(fname.format(hemi='lh'))


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    # http://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    if isinstance(text, tuple):
        text = text[0]
    return [atoi(c) for c in re.split('(\d+)', text)]


def split_bipolar_name(elec_name):
    splits = elec_name.split('-')
    if len(splits) == 2:
        elec_name2, elec_name1 = splits
    elif len(splits) == 3:
        elec_name2, elec_name1 = '-'.join(splits[:2]), '-'.join(splits[2:3])
    elif len(splits) == 4:
        elec_name2, elec_name1 = '-'.join(splits[:2]), '-'.join(splits[2:4])
    return elec_name1, elec_name2


def elec_group_number(elec_name, bipolar=False, num_to_int=True):
    if isinstance(elec_name, bytes):
        elec_name = elec_name.decode('utf-8')
    if bipolar and '-' in elec_name:
        elec_name1, elec_name2 = split_bipolar_name(elec_name)
        group1, num1 = elec_group_number(elec_name1, False)
        group2, num2 = elec_group_number(elec_name2, False)
        group = group1 if group1 != '' else group2
        return group.strip(), num1, num2
    else:
        elec_name = elec_name.strip()
        num = re.sub('\D', ',', elec_name).split(',')[-1]
        group = elec_name[:elec_name.rfind(num)]
        if num_to_int and is_int(num):
            num = int(num)
        return group.strip(), num if num != '' else ''


def get_group_and_number(ch_name):
    return elec_group_number(ch_name, False, False)



def elec_group(elec_name, bipolar=False):
    #todo: should check the electrode type, if it's grid, it should be bipolar
    if '-' in elec_name:
        group, _, _ = elec_group_number(elec_name, True)
    else:
        group, _ = elec_group_number(elec_name, False)
    return group


def csv_file_reader(csv_fname, delimiter=',', skip_header=0, encoding=None, find_encoding=False, max_lines=0):
    import csv
    if find_encoding:
        encoding = find_file_encoding(csv_fname)
    with open(csv_fname, 'r', encoding=encoding) as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        for line_num, line in enumerate(reader):
            if line_num < skip_header:
                continue
            if max_lines > 0 and line_num > max_lines:
                break
            if encoding == 'utf-8':
                line = [v.encode('utf-8').decode('utf-8-sig') for v in line]
            yield [val.strip() for val in line]


def get_matrix_world():
    return bpy.data.objects['rh'].matrix_world


def find_file_encoding(fname):
    import io
    encodings = ['utf-8', 'windows-1250', 'windows-1252']
    for e in encodings:
        try:
            fh = io.open(fname, 'r', encoding=e)
            fh.readlines()
            fh.seek(0)
        except UnicodeDecodeError:
            # print('got unicode error with %s , trying different encoding' % e)
            continue
        else:
            # print('opening the file with encoding:  %s ' % e)
            return e
    else:
        return None


def check_obj_type(obj_name):
    import bpy_types
    if isinstance(obj_name, bpy_types.Object):
        obj = obj_name
    elif isinstance(obj_name, str):
        obj = bpy.data.objects.get(obj_name, None)
    else:
        return None
    if obj is None or obj.parent is None:
        return None
    if obj.parent.name == 'Cortex-lh':
        obj_type = OBJ_TYPE_CORTEX_LH
    elif obj.parent.name == 'Cortex-rh':
        obj_type = OBJ_TYPE_CORTEX_RH
    elif obj.parent.name == 'Cortex-inflated-lh':
        obj_type = OBJ_TYPE_CORTEX_INFLATED_LH
    elif obj.parent.name == 'Cortex-inflated-rh':
        obj_type = OBJ_TYPE_CORTEX_INFLATED_RH
    elif obj.name == 'inflated_lh':
        obj_type = OBJ_TYPE_CORTEX_INFLATED_LH
    elif obj.name == 'inflated_rh':
        obj_type = OBJ_TYPE_CORTEX_INFLATED_RH
    elif obj.parent.name == 'Subcortical_structures':
        obj_type = OBJ_TYPE_SUBCORTEX
    elif obj.parent.name == 'Deep_electrodes':
        obj_type = OBJ_TYPE_ELECTRODE
    elif obj.parent.name == 'EEG_sensors':
        obj_type = OBJ_TYPE_EEG
    elif obj.parent.name in ['Cerebellum', 'Cerebellum_fmri_activity_map', 'Cerebellum_meg_activity_map']:
        obj_type = OBJ_TYPE_CEREBELLUM
    elif obj.parent.name == con_pan.get_connections_parent_name():
        obj_type = OBJ_TYPE_CON
    elif obj.parent.name == 'connections_vertices':
        obj_type = OBJ_TYPE_CON_VERTICE
    else:
        obj_type = None
        # print("Can't find the object type ({})!".format(obj_name))
    return obj_type


def obj_is_cortex(obj_name):
    return check_obj_type(obj_name) in [OBJ_TYPE_CORTEX_LH, OBJ_TYPE_CORTEX_RH, OBJ_TYPE_CORTEX_INFLATED_LH,
                                        OBJ_TYPE_CORTEX_INFLATED_RH]


def get_obj_hemi(obj_name):
    _, _, _, hemi = get_hemi_delim_and_pos(obj_name)
    return hemi
    # obj_type = check_obj_type(obj_name)
    # if obj_type == OBJ_TYPE_CORTEX_LH:
    #     hemi = 'lh'
    # elif obj_type == OBJ_TYPE_CORTEX_RH:
    #     hemi = 'rh'
    # else:
    #     hemi = None
    # return hemi


def run_command_in_new_thread(cmd, queues=True, shell=True, read_stdin=True, read_stdout=True, read_stderr=False,
                              stdin_func=lambda: True, stdout_func=lambda: True, stderr_func=lambda: True, cwd=None):
    if queues:
        q_in, q_out = Queue(), Queue()
        thread = threading.Thread(target=run_command_and_read_queue, args=(
            cmd, q_in, q_out, shell, read_stdin, read_stdout, read_stderr,
            stdin_func, stdout_func, stderr_func, cwd))
    else:
        thread = threading.Thread(target=run_command, args=(cmd, shell, False, cwd))
        q_in, q_out = None, None
    # print('start!')
    thread.start()
    return q_in, q_out


def run_command_and_read_queue(cmd, q_in, q_out, shell=True, read_stdin=True, read_stdout=True, read_stderr=False,
                               stdin_func=lambda:True, stdout_func=lambda:True, stderr_func=lambda:True, cwd=None):

    def write_to_stdin(proc, q_in, while_func):
        while while_func():
            # Get some data
            data = q_in.get()
            try:
                print('Writing data into stdin: {}'.format(data))
                output = proc.stdin.write(data.encode())  # decode('utf-8'))
                proc.stdin.flush()
                print('stdin output: {}'.format(output))
            except:
                print("Something is wrong with the in pipe, can't write to stdin!!!")
                break
                # print(traceback.format_exc())
        print('End of write_to_stdin')

    def read_from_stdout(proc, q_out, while_func):
        while while_func():
            try:
                line = proc.stdout.readline()
                if line != b'':
                    q_out.put(line)
                    # print('stdout: {}'.format(line))
            except:
                print('Error in reading stdout!!!')
                break
                # print(traceback.format_exc())
        print('End of read_from_stdout')

    def read_from_stderr(proc, while_func):
        while while_func():
            try:
                line = proc.stderr.readline()
                line = line.decode(sys.getfilesystemencoding(), 'ignore')
                if line != '':
                    print('stderr: {}'.format(line))
            except:
                print('Error in reading stderr!!!')
                break
                # print(traceback.format_exc())
        print('End of read_from_stderr')

    stdout = PIPE if read_stdout else None
    stdin = PIPE if read_stdin else None
    stderr = PIPE if read_stderr else None
    p = Popen(cmd, shell=shell, stdout=stdout, stdin=stdin, stderr=stderr, bufsize=1, close_fds=True, cwd=cwd) #, universal_newlines=True)
    if read_stdin:
        thread_write_to_stdin = threading.Thread(target=write_to_stdin, args=(p, q_in, stdin_func))
        thread_write_to_stdin.start()
    if read_stdout:
        thread_read_from_stdout = threading.Thread(target=read_from_stdout, args=(p, q_out, stdout_func))
        thread_read_from_stdout.start()
    if read_stderr:
        thread_read_from_stderr = threading.Thread(target=read_from_stderr, args=(p, stderr_func))
        thread_read_from_stderr.start()


def run_thread(target_func, while_func=lambda:True, **kwargs):
    q = Queue()
    t = threading.Thread(target=target_func, args=(q, while_func), kwargs=kwargs)
    t.start()
    return q


def run_thread_2q(target_func, while_func=lambda:True, **kwargs):
    q1, q2 = Queue(), Queue()
    t = threading.Thread(target=target_func, args=(q1, q2, while_func), kwargs=kwargs)
    t.start()
    return q1, q2


def run_command(cmd, shell=True, pipe=False, cwd=None):
    # global p
    from subprocess import Popen, PIPE, STDOUT
    print('run: {}'.format(cmd))
    if (IS_WINDOWS):
        if cwd is not None:
            os.chdir(cwd)
        os.system(cmd)
        return None
    else:
        if pipe:
            p = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=cwd)
        else:
            p = subprocess.call(cmd, shell=shell, cwd=cwd)
        # p = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        # p.stdin.write(b'-zoom 2\n')
        return p


# class Unbuffered(object):
#    def __init__(self, stream):
#        self.stream = stream
#    def write(self, data):
#        self.stream.write(dataf)
#        self.stream.flush()
#    def __getattr__(self, attr):
#        return getattr(self.stream, attr)
#
# import sys
# sys.stdout = Unbuffered(sys.stdout)


def make_dir(fol):
    try:
        if not op.isdir(fol) and not op.islink(fol):
            os.makedirs(fol)
    except:
        pass
    return fol


def move_file(fname, fol, overwrite=False):
    if op.isfile(fname):
        output_fname = op.join(fol, namebase_with_ext(fname))
        if op.isfile(output_fname):
            if not overwrite:
                print('{} already exist!'.format(output_fname))
                return
            else:
                os.remove(output_fname)
        shutil.move(fname, op.join(fol, namebase_with_ext(fname)))
    else:
        print('{} does not exist!'.format(fname))


def copy_file(fname, fol):
    if op.isfile(fname):
        new_fname = op.join(fol, namebase_with_ext(fname))
        shutil.copy(fname, new_fname)
        return new_fname
    return ''


def profileit(sort_field='cumtime', root_folder=''):
    """
    Parameters
    ----------
    prof_fname
        profile output file name
    sort_field
        "calls"     : (((1,-1),              ), "call count"),
        "ncalls"    : (((1,-1),              ), "call count"),
        "cumtime"   : (((3,-1),              ), "cumulative time"),
        "cumulative": (((3,-1),              ), "cumulative time"),
        "file"      : (((4, 1),              ), "file name"),
        "filename"  : (((4, 1),              ), "file name"),
        "line"      : (((5, 1),              ), "line number"),
        "module"    : (((4, 1),              ), "file name"),
        "name"      : (((6, 1),              ), "function name"),
        "nfl"       : (((6, 1),(4, 1),(5, 1),), "name/file/line"),
        "pcalls"    : (((0,-1),              ), "primitive call count"),
        "stdname"   : (((7, 1),              ), "standard name"),
        "time"      : (((2,-1),              ), "internal time"),
        "tottime"   : (((2,-1),              ), "internal time"),
    Returns
    -------
    None

    """

    def actual_profileit(func):
        def wrapper(*args, **kwargs):
            prof = cProfile.Profile()
            retval = prof.runcall(func, *args, **kwargs)
            prof_root_folder = get_user_fol() if root_folder == '' else root_folder
            make_dir(prof_root_folder)
            prof_dir = op.join(prof_root_folder, 'profileit')
            make_dir(prof_dir)
            prof_fname = op.join(prof_dir, '{}_{}'.format(func.__name__, rand_letters(5)))
            stat_fname = '{}.stat'.format(prof_fname)
            prof.dump_stats(prof_fname)
            print_profiler(prof_fname, stat_fname, sort_field)
            print('dump stat in {}'.format(stat_fname))
            return retval
        return wrapper
    return actual_profileit


def print_profiler(profile_input_fname, profile_output_fname, sort_field='cumtime'):
    import pstats
    with open(profile_output_fname, 'w') as f:
        stats = pstats.Stats(profile_input_fname, stream=f)
        stats.sort_stats(sort_field)
        stats.print_stats()


def timeit(func):
    def wrapper(*args, **kwargs):
        now = time.time()
        retval = func(*args, **kwargs)
        print('{} took {:.5f}s'.format(func.__name__, time.time() - now))
        return retval

    return wrapper


def dump_args(func):
    # Decorator to print function call details - parameters names and effective values
    # http://stackoverflow.com/a/25206079/1060738
    def wrapper(*func_args, **func_kwargs):
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        args = func_args[:len(arg_names)]
        defaults = func.__defaults__ or ()
        args = args + defaults[len(defaults) - (func.__code__.co_argcount - len(args)):]
        params = list(zip(arg_names, args))
        args = func_args[len(arg_names):]
        if args: params.append(('args', args))
        if func_kwargs: params.append(('kwargs', func_kwargs))
        try:
            return func(*func_args, **func_kwargs)
        except:
            print('Error in {}!'.format(func.__name__))
            print(func.__name__ + ' (' + ', '.join('%s = %r' % p for p in params) + ' )')
            print(traceback.format_exc())
            # try:
            #     print('Current context:')
            #     get_current_context()
            # except:
            #     print('Error finding the context!')
            #     print(traceback.format_exc())
    return wrapper


# def tryit(throw_exception=True):
def tryit(except_retval=False, throw_exception=False, print_only_last_error_line=True):
    def real_tryit(func):
        def wrapper(*args, **kwargs):
            try:
                retval = func(*args, **kwargs)
            except:
                print('Error in {}!'.format(func.__name__))
                if (throw_exception):
                    raise Exception(traceback.format_exc())
                if print_only_last_error_line:
                    print_last_error_line()
                else:
                    print(traceback.format_exc())
                retval = except_retval
            return retval
        return wrapper
    return real_tryit


def print_last_error_line():
    try:
        last_err_line = [l for l in traceback.format_exc().split('\n') if len(l) > 0][-1]
        print(last_err_line)
        return last_err_line
    except:
        return ''


def get_all_children(parents):
    children = [bpy.data.objects[parent].children for parent in parents if bpy.data.objects.get(parent)]
    return list(chain.from_iterable([obj for obj in children]))


def get_non_functional_objects():
    return get_all_children((['Cortex-lh', 'Cortex-rh', 'Subcortical_structures', 'Deep_electrodes', 'External']))


def get_selected_objects():
    return [obj for obj in get_non_functional_objects() if obj.select]


def get_corticals_labels():
    return bpy.data.objects['Cortex-lh'].children + bpy.data.objects['Cortex-rh'].children


def add_box_line(col, text1, text2='', percentage=0.3, align=True):
    row = col.split(percentage=percentage, align=align)
    row.label(text=text1)
    if text2 != '':
        row.label(text=text2)


@functools.lru_cache(maxsize=None)
def get_user():
    spl = namebase(bpy.data.filepath).split('_')
    root = get_mmvt_root()
    k = 1
    subject = '_'.join(spl[:-k])
    while not op.isdir(op.join(root, subject)) and k < len(spl):
        print('get_user: no folder {}'.format(op.join(root, subject)))
        k += 1
        subject = '_'.join(spl[:-k])
    if not op.isdir(op.join(root, subject)):
        raise Exception('No folder was found for {}!'.format(subject))
    return subject


def current_path():
    return os.path.dirname(os.path.realpath(__file__))


# def get_parent_fol(fol=None):
#     if fol is None:
#         fol = os.path.dirname(os.path.realpath(__file__))
#     return os.path.split(fol)[0]


def get_mmvt_code_root():
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.dirname(os.path.split(curr_dir)[0])


def add_mmvt_code_root_to_path():
    code_root_fol = get_mmvt_code_root()
    if code_root_fol not in sys.path:
        sys.path.append(code_root_fol)


def add_fol_to_path(fol):
    if fol not in sys.path:
        sys.path.append(fol)


def get_mmvt_root():
    return bpy.path.abspath('//')
    # return get_parent_fol(get_user_fol())


def get_real_fname(field):
    return op.abspath(bpy.path.abspath(bpy.context.scene[field]))


def change_fol_to_mmvt_root():
    os.chdir(get_mmvt_code_root())


class connection_to_listener(object):
    # http://stackoverflow.com/a/6921402/1060738

    conn = None
    handle_is_open = False

    @staticmethod
    def check_if_open():
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('localhost', 6000))

        if result == 0:
            print('socket is open')
        s.close()

    def init(self):
        try:
            # connection_to_listener.check_if_open()
            # connection_to_listener.run_addon_listener()
            address = ('localhost', 6000)
            self.conn = Client(address, authkey=b'mmvt')
            self.handle_is_open = True
            return True
        except:
            print('Error in connection_to_listener.init()!')
            print(traceback.format_exc())
            return False

    @staticmethod
    def run_addon_listener():
        cmd = 'python {}'.format(op.join(current_path(), 'addon_listener.py'))
        print('Running {}'.format(cmd))
        run_command_in_new_thread(cmd, shell=True)
        time.sleep(1)

    def send_command(self, cmd):
        if self.handle_is_open:
            self.conn.send(cmd)
            return True
        else:
            # print('Handle is close')
            return False

    def close(self):
        self.send_command('close\n')
        self.conn.close()
        self.handle_is_open = False

conn_to_listener = connection_to_listener()


def min_cdist_from_obj(obj, Y):
    vertices = obj.data.vertices
    kd = mathutils.kdtree.KDTree(len(vertices))
    for ind, x in enumerate(vertices):
        kd.insert(x.co, ind)
    kd.balance()
    # Find the closest point to the 3d cursor
    res = []
    for y in Y:
        res.append(kd.find_n(y, 1)[0])
    # co, index, dist
    return res


def min_cdist(X, Y):
    kd = mathutils.kdtree.KDTree(X.shape[0])
    for ind, x in enumerate(X):
        kd.insert(x, ind)
    kd.balance()
    # Find the closest point to the 3d cursor
    res = []
    for y in Y:
        res.append(kd.find_n(y, 1)[0])
    # co, index, dist
    if len(Y) == 1:
        return res[0]
    else:
        return res


# def cdist(x, y):
#     return np.sqrt(np.dot(x, x) - 2 * np.dot(x, y) + np.dot(y, y))


# Warning! This method is really slow, ~3s per hemi
def obj_has_activity(obj):
    activity = False
    for mesh_loop_color_layer_data in obj.data.vertex_colors.active.data:
        if tuple(mesh_loop_color_layer_data.color) != (1, 1, 1):
            activity = True
            break
    return activity


def other_hemi(hemi):
    if 'inflated' in hemi:
        return 'inflated_lh' if hemi == 'inflated_rh' else 'inflated_rh'
    else:
        return 'lh' if hemi == 'rh' else 'rh'


# http://blender.stackexchange.com/a/30739/16364
def show_progress(job_name):
    sys.stdout.write('{}: '.format(job_name))
    sys.stdout.flush()
    some_list = [0] * 100
    for idx, item in enumerate(some_list):
        msg = "item %i of %i" % (idx, len(some_list)-1)
        sys.stdout.write(msg + chr(8) * len(msg))
        sys.stdout.flush()
        time.sleep(0.02)

    sys.stdout.write("DONE" + " "*len(msg)+"\n")
    sys.stdout.flush()


def update_progress(job_title, progress):
    length = 20 # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()

    def test():
        for i in range(100):
            time.sleep(0.1)
            update_progress("Some job", i / 100.0)
        update_progress("Some job", 1)


def get_spaced_colors(n):
    import colorsys
    # if n <= 7:
    #     colors = ['r', 'g', 'c', 'm', 'y', 'b', 'k'][:n]
    # else:
    HSV_tuples = [(x*1.0/n, 0.5, 0.5) for x in range(n)]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
    return colors


def create_empty_in_vertex(vertex_location, obj_name, layer, parent_name=''):
    layers = [False] * 20
    layers[layer] = True
    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=vertex_location, layers=layers)
    bpy.context.object.name = obj_name
    if parent_name != '' and not bpy.data.objects.get(parent_name, None) is None:
        bpy.context.object.parent = bpy.data.objects[parent_name]


def read_ply_file(ply_file):
    with open(ply_file, 'r') as f:
        lines = f.readlines()
        verts_num = int(lines[2].split(' ')[-1])
        faces_num = int(lines[6].split(' ')[-1])
        verts_lines = lines[9:9 + verts_num]
        faces_lines = lines[9 + verts_num:]
        verts = np.array([list(map(float, l.strip().split(' '))) for l in verts_lines])
        faces = np.array([list(map(int, l.strip().split(' '))) for l in faces_lines])[:,1:]
    return verts, faces


def change_selected_fcurves_colors(selected_objects_types, color_also_objects=True, exclude=()):
    import colorsys
    # print('change_selected_fcurves_colors')
    if not isinstance(selected_objects_types, Iterable):
        selected_objects_types = [selected_objects_types]
    selected_objects = [obj for obj in bpy.context.scene.objects if obj.select if
                        check_obj_type(obj.name) in selected_objects_types]
    # selected_objects = [obj for obj in bpy.context.selected_objects if
    #                     check_obj_type(obj.name) in selected_objects_types]
    selected_objects = [obj for obj in selected_objects if obj.animation_data is not None and
                        obj.name not in exclude][::-1]
    if len(selected_objects) == 0:
        return
    selected_objects_len = 6 if len(selected_objects) <= 6 else len(selected_objects)
    Hs = np.linspace(0, 360, selected_objects_len + 1)[:-1] / 360
    fcurves_per_obj = count_fcurves(selected_objects[0])
    Ls = [0.3, 0.7] if fcurves_per_obj == 2 else [0.5]

    obj_colors = []
    for obj_ind, obj in enumerate(selected_objects):
        if color_also_objects:
            obj_color = colorsys.hls_to_rgb(Hs[obj_ind], 0.5, 1)
            obj_colors.append(obj_color)
            _addon.object_coloring(obj, obj_color)
        for fcurve_ind, fcurve in enumerate(obj.animation_data.action.fcurves):
            new_color = colorsys.hls_to_rgb(Hs[obj_ind], Ls[fcurve_ind], 1)
            change_fcurve_color(fcurve, new_color, exclude)
    return obj_colors


def get_selected_fcurves_colors(selected_objects_types, sepcific_obj_name='', exclude=()):
    import colorsys
    if not isinstance(selected_objects_types, Iterable):
        selected_objects_types = [selected_objects_types]
    selected_objects = [obj for obj in bpy.context.scene.objects if obj.select if
                        check_obj_type(obj.name) in selected_objects_types]
    selected_objects = [obj for obj in selected_objects if obj.animation_data is not None and
                        obj.name not in exclude][::-1]
    if len(selected_objects) == 0:
        return []
    selected_objects_len = 6 if len(selected_objects) <= 6 else len(selected_objects)
    Hs = np.linspace(0, 360, selected_objects_len + 1)[:-1] / 360
    obj_colors = [colorsys.hls_to_rgb(Hs[obj_ind], 0.5, 1) for obj_ind, obj in enumerate(selected_objects)]
    if sepcific_obj_name != '':
        selected_objects_names = [o.name for o in selected_objects]
        if sepcific_obj_name in selected_objects_names:
            return obj_colors[selected_objects_names.index(sepcific_obj_name)]
    return obj_colors


def get_hs_color(objs_num, obj_ind):
    Hs = np.linspace(0, 360, objs_num + 1)[:-1] / 360
    return colorsys.hls_to_rgb(Hs[obj_ind], 0.5, 1)


def change_fcurves_colors(objs=[], exclude=[], fcurves=[]):
    colors_num = count_fcurves(objs)
    colors = cu.get_distinct_colors(colors_num)
    if len(fcurves) > 0:
        for fcurve in fcurves:
            change_fcurve_color(fcurve, colors, exclude)
    else:
        if not isinstance(objs, Iterable):
            objs = [objs]
        for obj in objs:
            if obj.animation_data is None:
                obj.select = True
                obj.hide = False
                continue
            if obj.name in exclude:
                continue
            for fcurve in obj.animation_data.action.fcurves:
                change_fcurve_color(fcurve, colors, exclude)


def change_fcurve_color(fcurve, color, exclude=[]):
    fcurve_name = get_fcurve_name(fcurve)
    if fcurve_name in exclude:
        return
    fcurve.color_mode = 'CUSTOM'
    fcurve.color = color if isinstance(color, tuple) and len(color) == 3 else tuple(next(color))
    fcurve.select = True
    fcurve.hide = False


def get_animation_conditions(obj, take_my_first_child=False):
    try:
        if take_my_first_child:
            return [get_fcurve_name(f).split('_')[-1] for f in obj.children[0].animation_data.action.fcurves]
        else:
            return [get_fcurve_name(f).split('_')[-1] for f in obj.animation_data.action.fcurves]
    except:
        return []


def count_fcurves(objs, recursive=False):
    if not isinstance(objs, Iterable):
        objs = [objs]
    curves_num = 0
    for obj in objs:
        if not obj is None and 'unknown' not in obj.name:
            if not obj is None and not obj.animation_data is None:
                curves_num += len(obj.animation_data.action.fcurves)
        if recursive:
            curves_num += count_fcurves(obj.children)
    return curves_num


def get_fcurves(obj, recursive=False, only_selected=True, only_not_hiden=False):
    if isinstance(obj, str):
        obj = bpy.data.objects.get(obj)
        if obj is None:
            return None
    fcurves, fcurves_inds = [], []
    if not obj is None and not obj.animation_data is None:
        if not only_selected or obj.select:
            if only_not_hiden:
                fcurves.extend([f for f in obj.animation_data.action.fcurves if not f.hide])
            else:
                fcurves.extend(obj.animation_data.action.fcurves)
    if recursive:
        for obj in obj.children:
            if not only_selected or obj.select:
                fcurves.extend(get_fcurves(obj, recursive, only_selected))
    return fcurves


def get_all_selected_fcurves(parent_obj_name):
    children = bpy.data.objects[parent_obj_name].children
    parent_obj = bpy.data.objects[parent_obj_name]
    children_have_fcurves = count_fcurves(children) > 0
    parent_have_fcurves = not parent_obj.animation_data is None
    fcurves = []
    if parent_have_fcurves and (bpy.context.scene.selection_type == 'diff' or not children_have_fcurves):
        fcurves = get_fcurves(parent_obj, recursive=False, only_selected=True)
    elif children_have_fcurves:
        for child in children:
            fcurves.extend(get_fcurves(child, recursive=False, only_selected=True))
    return fcurves


def if_cond_is_diff(parent_obj):
    if isinstance(parent_obj, str):
        parent_obj = bpy.data.objects[parent_obj]
    children = parent_obj.children
    children_have_fcurves = count_fcurves(children) > 0
    parent_have_fcurves = parent_obj.animation_data is not None
    return parent_have_fcurves and (bpy.context.scene.selection_type == 'diff' or not children_have_fcurves)


def get_fcurves_names(obj, recursive=False):
    if isinstance(obj, str):
        obj = bpy.data.objects.get(obj)
    fcurves_names = []
    if not obj is None and not obj.animation_data is None:
        fcurves_names = [get_fcurve_name(fcurve) for fcurve in obj.animation_data.action.fcurves]
    if recursive:
        for obj in obj.children:
            fcurves_names.extend(get_fcurves_names(obj))
    return fcurves_names


def get_the_graph_editor():
    for ii in range(len(bpy.data.screens['Neuro'].areas)):
        if bpy.data.screens['Neuro'].areas[ii].type == 'GRAPH_EDITOR':
            for jj in range(len(bpy.data.screens['Neuro'].areas[ii].spaces)):
                if bpy.data.screens['Neuro'].areas[ii].spaces[jj].type == 'GRAPH_EDITOR':
                    return bpy.data.screens['Neuro'].areas[ii].spaces[jj]
    return None


def set_show_textured_solid(val=True, only_neuro=False):
    for space in get_3d_spaces(only_neuro):
        space.show_textured_solid = val


def show_only_render(val=True, only_neuro=False):
    for space in get_3d_spaces():
        # Don't change it for the colorbar's space
        if space.lock_object and space.lock_object.name == 'full_colorbar':
            continue
        space.show_only_render = val


def hide_relationship_lines(val=False):
    for space in get_3d_spaces():
        # Don't change it for the colorbar's space
        if space.lock_object and space.lock_object.name == 'full_colorbar':
            continue
        space.show_relationship_lines = val


def get_3d_spaces(only_neuro=False):
    for screen in bpy.data.screens:
        areas = bpy.data.screens['Neuro'].areas if only_neuro else screen.areas
        for area in areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        yield space


def get_3d_areas(only_neuro=True):
    for screen in bpy.data.screens:
        areas = bpy.data.screens['Neuro'].areas if only_neuro else screen.areas
        for area in areas:
            if area.type == 'VIEW_3D':
                yield area


def filter_graph_editor(filter):
    ge = get_the_graph_editor()
    ge.dopesheet.filter_fcurve_name = filter


def unfilter_graph_editor():
    filter_graph_editor('')


def unique_save_order(arr):
    ret = []
    for val in arr:
        if val not in ret:
            ret.append(val)
    return ret


def remove_items_from_set(x, items):
    for item in items:
        if item in x:
            x.remove(item)


@functools.lru_cache(maxsize=None)
def save_blender_file(blend_fname=''):
    if blend_fname == '':
        blend_fname = bpy.data.filepath
    print('Saving current file to {}'.format(blend_fname))
    bpy.ops.wm.save_as_mainfile(filepath=blend_fname)


def update():
    # return
    # bpy.context.scene.frame_current += 1
    # bpy.data.objects['Brain'].select = True
    # bpy.ops.mmvt.where_i_am()
    # print(bpy.ops.ed.undo())
    # print(bpy.ops.ed.redo())
    # bpy.ops.ed.undo_history()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()


def change_layer(layer):
    bpy.context.scene.layers = [ind == layer for ind in range(len(bpy.context.scene.layers))]


def select_layer(layer, val=True):
    layers = bpy.context.scene.layers
    layers[layer] = val
    bpy.context.scene.layers = layers


def get_time():
    # print(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
    return str(datetime.now())


def get_time_obj():
    return datetime.now()


def get_time_from_event(time_obj):
    return(datetime.now()-time_obj).seconds


# def change_fcurve(obj_name, fcurve_name, data):
#     bpy.data.objects[obj_name].select = True
#     parent_obj = bpy.data.objects[obj_name]
#     for fcurve in parent_obj.animation_data.action.fcurves:
#         if get_fcurve_name(fcurve) == fcurve_name:
#             N = min(len(fcurve.keyframe_points), len(data))
#             for ind in range(N):
#                 fcurve.keyframe_points[ind].co[1] = data[ind]

@timeit
def change_fcurves(obj_name, data, ch_names):
    bpy.data.objects[obj_name].select = True
    parent_obj = bpy.data.objects[obj_name]
    ch_inds = get_fcurves_ordering(obj_name, ch_names)
    for fcurve, ch_ind in zip(parent_obj.animation_data.action.fcurves, ch_inds):
        fcurve_name = get_fcurve_name(fcurve)
        if fcurve_name != ch_names[ch_ind]:
            raise Exception('Wrong ordering!')
        N = min(len(fcurve.keyframe_points), data.shape[1])
        fcurve.keyframe_points[0].co[1] = 0
        for time_ind in range(N):
            fcurve.keyframe_points[time_ind + 1].co[1] = data[ch_ind, time_ind]
        fcurve.keyframe_points[N].co[1] = 0


@timeit
def get_fcurves_data(obj_name='', fcurves=[], with_kids=True, return_names=False):
    if obj_name != '':
        parent_obj = bpy.data.objects[obj_name]
        if parent_obj.animation_data is not None:
            fcurves = parent_obj.animation_data.action.fcurves
        if with_kids:
            for obj in parent_obj.children:
                if obj.animation_data is not None:
                    fcurves.extend(obj.animation_data.action.fcurves)
    if len(fcurves) == 0:
        return []
    T = len(fcurves[0].keyframe_points)
    data = np.zeros((len(fcurves), T))
    for fcurve_ind, fcurve in enumerate(fcurves):
        for time_ind in range(T):
            data[fcurve_ind, time_ind] = fcurve.keyframe_points[time_ind].co[1]
    if return_names:
        names = [get_fcurve_name(f) for f in fcurves]
        return data, names
    else:
        return data


@timeit
def get_fcurves_ordering(obj_name, ch_names):
    parent_obj = bpy.data.objects[obj_name]
    fcurves_names = [get_fcurve_name(fcurve) for fcurve in parent_obj.animation_data.action.fcurves]
    ch_inds = []
    for fcurve_ind, fcurve_name in enumerate(fcurves_names):
        if fcurve_name != ch_names[fcurve_ind]:
            ch_ind = np.where(ch_names == fcurve_name)[0][0]
        else:
            ch_ind = fcurve_ind
        ch_inds.append(ch_ind)
    return ch_inds


def ceil_floor(x):
    import math
    return math.ceil(x) if x < 0 else math.floor(x)


def round_n_digits(x, n):
    import math
    return ceil_floor(x * math.pow(10, n)) / math.pow(10, n)


def round_np_to_int(x):
    return np.rint(x).astype(int)


def get_data_max_min(data, norm_by_percentile=False, norm_percs=None, data_per_hemi=False, hemis=HEMIS, symmetric=True):
    if data_per_hemi:
        if norm_by_percentile:
            no_nan_data = {hemi:data[hemi][~np.isnan(data[hemi])] for hemi in hemis}
            data_max = max([np.percentile(no_nan_data[hemi], norm_percs[1]) for hemi in hemis])
            data_min = min([np.percentile(no_nan_data[hemi], norm_percs[0]) for hemi in hemis])
        else:
            data_max = max([np.nanmax(data[hemi]) for hemi in hemis])
            data_min = min([np.nanmin(data[hemi]) for hemi in hemis])
    else:
        if norm_by_percentile:
            no_nan_data = data[~np.isnan(data)]
            data_max = np.percentile(no_nan_data, norm_percs[1])
            data_min = np.percentile(no_nan_data, norm_percs[0])
        else:
            data_max = np.nanmax(data)
            data_min = np.nanmin(data)
    if symmetric and data_min != 0 and data_max != 0 and np.sign(data_min) != np.sign(data_max):
        data_minmax = get_max_abs(data_max, data_min)
        data_max, data_min = data_minmax, -data_minmax
    return data_max, data_min


def get_max_abs(data_max, data_min):
    return max(map(abs, [data_max, data_min]))


def calc_min(x, x_min=None, norm_percs=None):
    x_no_nan = x[np.where(~np.isnan(x))]
    if x_min is None:
        x_min = np.nanmin(x) if norm_percs is None else np.percentile(x_no_nan, norm_percs[0])
    return x_min


def calc_max(x, x_max=None, norm_percs=None):
    x_no_nan = x[np.where(~np.isnan(x))]
    if x_max is None:
        x_max = np.nanmax(x) if norm_percs is None else np.percentile(x_no_nan, norm_percs[1])
    return x_max


def calc_min_max(x, x_min=None, x_max=None, norm_percs=None):
    x_no_nan = x[np.where(~np.isnan(x))]
    x_min = calc_min(x_no_nan, x_min, norm_percs)
    x_max = calc_max(x_no_nan, x_max, norm_percs)
    if x_min == 0 and x_max == 0 and norm_percs is not None:
        x_min, x_max = calc_min_max(x)
    if x_min == 0 and x_max == 0:
        print('calc_min_max: min and max are 0!!!')
    return x_min, x_max


def queue_get(queue):
    try:
        if queue is None:
            return None
        else:
            return queue.get(block=False)
    except Empty:
        return None

#
# class dummy_bpy(object):
#     class types(object):
#         class Operator(object):
#             pass
#         class Panel(object):
#             pass


def caller_func():
    return sys._getframe(2).f_code.co_name


def log_err(text, logging=None):
    message = '{}: {}'.format(caller_func(), text)
    print(message)
    if not logging is None:
        logging.error(message)


def to_float(x_str, def_val=0.0):
    try:
        return float(x_str)
    except ValueError:
        return def_val


def to_int(x_str, def_val=0):
    try:
        return int(x_str)
    except ValueError:
        return def_val


def counter_to_dict(counter):
    return {k: v for k, v in counter.items()}


def to_str(s):
    if isinstance(s, str):
        return s
    elif (isinstance(s, np.bytes_)):
        return s.decode(sys.getfilesystemencoding(), 'ignore')
    else:
        return str(s)


def read_config_ini(fol='', ini_name='config.ini'):
    import configparser

    class EmptySettings(object):
        def sections(self):
            return {}

    if fol == '':
        fol = get_user_fol()
    if op.isfile(op.join(fol, ini_name)):
        config = configparser.ConfigParser()
        config.read(op.join(fol, ini_name))
    else:
        config = EmptySettings()
    return config


def get_graph_context():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'GRAPH_EDITOR':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = bpy.context.copy()
                        override['area'] = area
                        override["region"] = region
                        return override
    print("Couldn't find the graph editor!")


def get_3d_area_region(only_neuro=True):
    # for window in bpy.context.window_manager.windows:
    for screen in bpy.data.screens:
        areas = bpy.data.screens['Neuro'].areas if only_neuro else screen.areas
        # for area in window.screen.areas:
        for area in areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return area, region


def get_images_area_regions(only_neuro=True):
    # for window in bpy.context.window_manager.windows:
    for screen in bpy.data.screens:
        areas = bpy.data.screens['Neuro'].areas if only_neuro else screen.areas
        # for area in window.screen.areas:
        for area in areas:
            if area.type == 'IMAGE_EDITOR':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        yield area, region


def set_graph_att(att, val):
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'GRAPH_EDITOR':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        bpy.context.scene[att] = val


def get_view3d_contexts(only_neuro=True):
    for screen in bpy.data.screens:
        areas = bpy.data.screens['Neuro'].areas if only_neuro else screen.areas
        for area in areas:
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = bpy.context.copy()
                    override['area'] = area
                    override["region"] = region
                    yield override


def get_view3d_context():
    area = bpy.data.screens['Neuro'].areas[1]
    for region in area.regions:
        if region.type == 'WINDOW':
            override = bpy.context.copy()
            override['area'] = area
            override["region"] = region
            return override


def call_3d_view_func(func):
    for v3d_context in get_view3d_contexts():
        try:
            func(v3d_context)
            break
        except Exception as e:
            pass
    else:
        print('center_view: No context was found!')


def center_view():
    view_distance = bpy.context.scene.view_distance
    call_3d_view_func(bpy.ops.view3d.view_all)
    bpy.context.scene.view_distance = view_distance


# def find_center():
#     bpy.data.objects['inflated_lh'].hide_select = not val
#     bpy.data.objects['inflated_lh'].select = val
#     bpy.data.objects['inflated_rh'].hide_select = not val
#     bpy.data.objects['inflated_rh'].select = val
#     if not bpy.data.objects['Subcortical_fmri_activity_map'].hide:
#         select_hierarchy('Subcortical_fmri_activity_map', val)
#         if not val:
#             for child in bpy.data.objects['Subcortical_fmri_activity_map'].children:
#                 child.hide_select = True
#
#
#     if bpy.data.objects.get(obj) is not None:
#         bpy.data.objects[obj].select = select_parent
#         for child in bpy.data.objects[obj].children:
#             if val:
#                 child.hide_select = False
#             child.select = val

# def get_view3d_region():
#     area = bpy.data.screens['Neuro'].areas[1]
#     for region in area.regions:
#         if region.type == 'WINDOW':
#             return region
#     return None


def get_image_context():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'IMAGE_EDITOR':
                override = bpy.context.copy()
                override['area'] = area
                override["screen"] = screen
                return override
    print("Can't find image context!")


def view_selected():
    area = bpy.data.screens['Neuro'].areas[1]
    for region in area.regions:
        if region.type == 'WINDOW':
            override = bpy.context.copy()
            override['area'] = area
            override["region"] = region
            select_all_brain(True)
            bpy.ops.view3d.view_selected(override)


def deselect_all_objects():
    bpy.ops.object.select_all(action='DESELECT')


def select_all_brain(val):
    bpy.data.objects['inflated_lh'].hide_select = not val
    bpy.data.objects['inflated_lh'].select = val
    bpy.data.objects['inflated_rh'].hide_select = not val
    bpy.data.objects['inflated_rh'].select = val
    if not bpy.data.objects['Subcortical_fmri_activity_map'].hide:
        select_hierarchy('Subcortical_fmri_activity_map', val)
        if not val:
            for child in bpy.data.objects['Subcortical_fmri_activity_map'].children:
                child.hide_select = True
    # head = bpy.data.objects.get('seghead', None)
    # if head is not None and not head.hide:
    #     head.select = val
    #     head.hide_select = not val
    for obj in [bpy.data.objects.get(obj_name, None) for obj_name in ['eeg_helmet', 'meg_helmet', 'seghead']]:
        if obj is not None and not obj.hide:
            if obj is not None:
                obj.select = val


def get_view3d_region():
    return bpy.data.screens['Neuro'].areas[1].spaces[0].region_3d


def rotate_view3d(rotation_in_quaternions):
    get_view3d_region().view_rotation = rotation_in_quaternions


def rotate_view_to_vertice(vert_ind=None, mesh=None):
    if _addon is None:
        return
    if vert_ind is None or mesh is None:
        vert_ind, mesh = _addon.appearance.get_closest_vertex_and_mesh_to_cursor()
    vert = bpy.data.objects[mesh].data.vertices[vert_ind]
    vert_normal = vert.normal
    rotate_view3d(vert_normal.to_track_quat('Z', 'Y'))


def get_screen(screen_name='Neuro'):
    return bpy.data.screens[screen_name]


def get_images_areas(screen_name='Neuro'):
    screen = get_screen(screen_name)
    return [area for area in screen.areas if area.type == 'IMAGE_EDITOR']


def get_image_area_override(area):
    override = bpy.context.copy()
    override['area'] = area
    override['screen'] = get_screen()
    return override


# def set_zoom_for_flatmap(relative=False):
#     if relative is False:
#         get_view3d_region().view_distance = 23.0
#     else:
#         get_view3d_region().view_distance = 23.0 * relative + get_view3d_region().view_distance*(1-relative)
#
#
# def set_zoom_for_inflated(relative=False):
#     get_view3d_region().view_distance = 17.7
#
#
# def set_zoom_for_pial(relative=False):
#     get_view3d_region().view_distance = 11.6
#

def set_zoom_level(surface, relative=1, split=False):
    surface_zoom_level = {'pial': 17.36, 'inflated': 20.7, 'flat': 23.0}
    surface_split_zoom_level = {'pial': 22.7, 'inflated': 32.7}
    zoom_level = surface_zoom_level[surface]
    if split:
        get_view3d_region().view_distance = surface_split_zoom_level[surface]
    else:
        get_view3d_region().view_distance = zoom_level * relative + get_view3d_region().view_distance * (1 - relative)


def get_current_context():
    # all the area types except 'EMPTY' from blender.org/api/blender_python_api_current/bpy.types.Area.html#bpy.types.Area.type
    types = {'VIEW_3D', 'TIMELINE', 'GRAPH_EDITOR', 'DOPESHEET_EDITOR', 'NLA_EDITOR', 'IMAGE_EDITOR', 'SEQUENCE_EDITOR',
             'CLIP_EDITOR', 'TEXT_EDITOR', 'NODE_EDITOR', 'LOGIC_EDITOR', 'PROPERTIES', 'OUTLINER', 'USER_PREFERENCES',
             'INFO', 'FILE_BROWSER', 'CONSOLE'}

    # save the current area
    area = bpy.context.area.type

    # try each type
    for type in types:
        # set the context
        bpy.context.area.type = type

        # print out context where operator works (change the ops below to check a different operator)
        if bpy.ops.sequencer.duplicate.poll():
            print(type)

    # leave the context where it was
    bpy.context.area.type = area


@dump_args
def set_context_to_graph_editor(context=None):
    if context is None:
        context = bpy.context
    graph_area = [context.screen.areas[k] for k in range(len(context.screen.areas)) if
                  context.screen.areas[k].type == 'GRAPH_EDITOR'][0]
    graph_window_region = [graph_area.regions[k] for k in range(len(graph_area.regions)) if
                           graph_area.regions[k].type == 'WINDOW'][0]
    c = context.copy()
    c['area'] = graph_area
    c['region'] = graph_window_region


def get_n_jobs(n_jobs):
    import multiprocessing
    cpu_num = multiprocessing.cpu_count()
    n_jobs = int(n_jobs)
    if n_jobs > cpu_num:
        n_jobs = cpu_num
    elif n_jobs < 0:
        n_jobs = cpu_num + n_jobs
    return n_jobs


def get_args_list(val):
    val = val.replace("'", '')
    if ',' in val:
        ret = val.split(',')
    elif len(val) == 0:
        ret = []
    else:
        ret = [val]
    return ret


def get_hemi_delim_and_pos(label_name):
    delim, pos, label, label_hemi = '', '', label_name, ''
    for hemi in ['rh', 'lh']:
        if label_name == hemi:
            delim, pos, label = '', '', ''
            label_hemi = hemi
            break
        if label_name.startswith('{}-'.format(hemi)):
            delim, pos, label = '-', 'start', label_name[3:]
            label_hemi = hemi
            break
        if label_name.startswith('{}_'.format(hemi)):
            delim, pos, label = '_', 'start', label_name[3:]
            label_hemi = hemi
            break
        if label_name.startswith('{}.'.format(hemi)):
            delim, pos, label = '.', 'start', label_name[3:]
            label_hemi = hemi
            break
        if label_name.endswith('-{}'.format(hemi)):
            delim, pos, label = '-', 'end', label_name[:-3]
            label_hemi = hemi
            break
        if label_name.endswith('_{}'.format(hemi)):
            delim, pos, label = '_', 'end', label_name[:-3]
            label_hemi = hemi
            break
        if label_name.endswith('.{}'.format(hemi)):
            label_hemi = hemi
            delim, pos, label = '.', 'end', label_name[:-3]
            break
    return delim, pos, label, label_hemi


def get_hemi_from_fname(fname):
    _, _, _, hemi = get_hemi_delim_and_pos(fname)
    return hemi


def get_label_and_hemi_from_fname(fname):
    _, _, label, hemi = get_hemi_delim_and_pos(fname)
    return label, hemi


def get_label_hemi_invariant_name(label_name):
    _, _, label_inv_name, _ = get_hemi_delim_and_pos(label_name)
    while label_inv_name != label_name:
        label_name = label_inv_name
        _, _, label_inv_name, _ = get_hemi_delim_and_pos(label_name)
    return label_inv_name


def remove_hemi_template(template):
    new_template = template.replace('.{hemi}', '').replace('{hemi}.', '').replace('_{hemi}', '').replace('{hemi}_', '')
    return new_template


def get_hemi_from_full_fname(fname):
    folder = namebase(fname)
    other_hemi_fname = full_fname = fname
    hemi = get_hemi_from_fname(folder)
    org_hemi = ''
    if hemi != '':
        other_hemi_fname = other_hemi_fname.replace(folder, get_other_hemi_label_name(folder))
        org_hemi = hemi
        # print('get_hemi_from_full_fname: org_hemi: {}'.format(org_hemi))
    # print('get_hemi_from_full_fname: folder, hemi: {}, {}'.format(folder, hemi))
    while folder != '': # and hemi == '':
        fname = get_parent_fol(fname)
        folder = fname.split(op.sep)[-1]
        hemi = get_hemi_from_fname(folder)
        # print('get_hemi_from_full_fname: fname, folder, hemi: {}, {} ,{}'.format(fname, folder, hemi))
        if hemi != '':
            # print('get_hemi_from_full_fname: get_other_hemi_label_name({}): {}'.format(folder, get_other_hemi_label_name(folder)))
            other_hemi_fname = other_hemi_fname.replace(folder, get_other_hemi_label_name(folder))
            org_hemi = hemi
            # print('get_hemi_from_full_fname: org_hemi: {}'.format(org_hemi))
        # print('get_hemi_from_full_fname: other_hemi_fname {}'.format(other_hemi_fname))
        # file_name_hemi = get_hemi_from_fname(namebase(other_hemi_fname))
        # print('get_hemi_from_full_fname: file_name_hemi {}'.format(file_name_hemi))
        # if file_name_hemi != '':
        #     file_name_other_hemi = get_other_hemi_label_name(namebase_with_ext(other_hemi_fname))
        #     print('get_hemi_from_full_fname: file_name_other_hemi {}'.format(file_name_other_hemi))
        #     other_hemi_fname = op.join(get_parent_fol(other_hemi_fname), file_name_other_hemi)
        #     print('get_hemi_from_full_fname: other_hemi_fname {}'.format(other_hemi_fname))
        # print('get_hemi_from_full_fname: hemi, other_hemi_fname: {}, {}'.format(hemi, other_hemi_fname))
    if org_hemi == '':
        print('get_hemi_from_full_fname: Can\'t find the hemi from {}!'.format(fname))
        return '', {'rh': '', 'lh': ''}
    hemis_fnames = {org_hemi: full_fname, other_hemi(org_hemi): other_hemi_fname}
    # else:
    #     hemis_fnames = {'rh':'', 'lh':''}
    return org_hemi, hemis_fnames


def get_label_for_full_fname(fname, delim='-'):
    fname_file_type = file_type(fname)
    names = [get_label_hemi_invariant_name(namebase(fname))]
    folder = get_parent_fol(fname) # namebase(fname)
    hemi_delim, pos, label, hemi = get_hemi_delim_and_pos(folder)
    while hemi == '' and folder != '':
        fname = get_parent_fol(fname)
        folder = fname.split(op.sep)[-1]
        names.insert(0, get_label_hemi_invariant_name(folder))
        hemi_delim, pos, label, hemi = get_hemi_delim_and_pos(folder)
    # return '{}.{}.{}'.format(delim.join(names), hemi, fname_file_type)
    return '{}.{}'.format(build_label_name(hemi_delim, pos, delim.join(names), hemi), fname_file_type)


def get_both_hemis_files(fname):
    # if hemi == '':
    #     hemi = get_hemi_from_fname(namebase(fname))
    # if hemi == '':
    #     print("Can't find the file's hemi! {}".format(fname))
    #     return {'rh': '', 'lh': ''}
    full_fname = fname
    # if hemi != '':
    #     other_hemi_fname = op.join(get_parent_fol(fname), get_other_hemi_label_name(fname))
    # else:
    hemi = ''
    folder = get_parent_fol(fname)
    while hemi == '' and folder != '':
        fname = get_parent_fol(fname)
        folder = fname.split(op.sep)[-1]
        hemi = get_hemi_from_fname(folder)
    if hemi == '':
        print("Can't find the file's hemi! {}".format(fname))
        return {'rh': '', 'lh': ''}
    other_hemi_fname = full_fname.replace(folder, get_other_hemi_label_name(folder))
    return {hemi: full_fname, other_hemi(hemi): other_hemi_fname}


def get_other_hemi_label_name(label_name):
    add_file_type = False
    delim, pos, label, hemi = get_hemi_delim_and_pos(label_name)
    if hemi == '':
        delim, pos, label, hemi = get_hemi_delim_and_pos(namebase(label_name))
        add_file_type = True
    if hemi == '':
        print("Can't find the hemi in {}!".format(label_name))
        return ''
    else:
        other_hemi = 'rh' if hemi == 'lh' else 'lh'
        other_hemi_fname = build_label_name(delim, pos, label, other_hemi)
        if add_file_type:
            other_hemi_fname = '{}.{}'.format(other_hemi_fname, file_type(label_name))
        return other_hemi_fname


def get_template_hemi_label_name(label_name, wild_char=False, wanted_pos=''):
    # add_file_type = False
    ft = file_type(label_name)
    delim, pos, label, hemi = get_hemi_delim_and_pos(label_name[:-len(ft) - 1])
    if hemi == '':
        delim, pos, label, hemi = get_hemi_delim_and_pos(namebase(label_name))
        # add_file_type = True
    hemi_temp = '?h' if wild_char else '{hemi}'
    if wanted_pos == '':
        wanted_pos = pos
    res_label_name = build_label_name(delim, wanted_pos, label, hemi_temp)
    # if add_file_type:
    res_label_name = '{}.{}'.format(res_label_name, file_type(label_name))
    return res_label_name


def build_label_name(delim, pos, label, hemi):
    if pos == 'end':
        return '{}{}{}'.format(label, delim, hemi)
    else:
        return '{}{}{}'.format(hemi, delim, label)


def min_stc_hemi(stc, hemi, min_perc=None):
    if stc is None:
        return 0
    data = stc.rh_data if hemi == 'rh' else stc.lh_data
    if data.shape[0] == 0:
        return 0
    if min_perc is None:
        return np.min(data)
    else:
        return np.percentile(data, min_perc)


def min_stc(stc, min_perc=None):
    return min([min_stc_hemi(stc, hemi, min_perc) for hemi in HEMIS])


def max_stc_hemi(stc, hemi, max_perc=None):
    data = stc.rh_data if hemi == 'rh' else stc.lh_data
    if data.shape[0] == 0:
        return 0
    if max_perc is None:
        return np.max(data)
    else:
        return np.percentile(data, max_perc)


def max_stc(stc, max_perc=None):
    return max([max_stc_hemi(stc, hemi, max_perc) for hemi in HEMIS])


def calc_min_max_stc(stc, min_perc=None, max_perc=None):
    return min_stc(stc, min_perc), max_stc(stc, max_perc)


def calc_mean_stc(stc):
    data = np.concatenate([stc.lh_data, stc.rh_data])
    return np.mean(data)


def calc_mean_stc_hemi(stc, hemi):
    data = stc.lh_data if hemi=='lh' else stc.rh_data
    return np.mean(data)


def check_hemi(hemi):
    if hemi in HEMIS:
        hemi = [hemi]
    elif hemi=='both':
        hemi = HEMIS
    else:
        raise ValueError('wrong hemi value!')
    return hemi


if MNE_EXIST:
    class Label(mne.label.Label):
        pass
else:
    class Label(object):
        vertices, pos, values = [], [], []
        comment, hemi, name = '', '', ''

        def __init__(self, vertices, pos=None, values=None, hemi=None, comment='', name=None):
            self.name = name
            self.hemi = hemi
            self.vertices = vertices
            self.pos = pos
            self.values = values
            self.comment = comment


def read_label_file(label_fname):
    """Read FreeSurfer Label file.

    Parameters
    ----------
    filename : string
        Path to label file.

    Returns
    -------
    - ``vertices``: vertex indices (0 based, column 1)
    - ``pos``: locations in meters (columns 2 - 4 divided by 1000)
    - ``values``: values at the vertices (column 5)
    """
    # read the file
    try:
        with open(label_fname, 'r') as fid:
            comment = fid.readline().replace('\n', '')[1:]
            nv = int(fid.readline())
            data = np.empty((5, nv))
            for i, line in enumerate(fid):
                data[:, i] = line.split()
    except:
        print('Error reading {}!'.format(label_fname))
        return None
    # let's make sure everything is ordered correctly
    vertices = np.array(data[0], dtype=np.int32)
    pos = 1e-3 * data[1:4].T
    values = data[4]
    order = np.argsort(vertices)
    vertices = vertices[order]
    pos = pos[order]
    values = values[order]
    _, _, label, hemi = get_hemi_delim_and_pos(namebase(label_fname))
    name = '{}-{}'.format(label, hemi)
    return Label(vertices, pos, values, hemi, name=name)


def read_labels_from_annots(atlas, hemi='both', labels_fol=''):
    if labels_fol == '':
        labels_fol = get_atlas_labels_fol(atlas)
    if labels_fol == '':
        return []
    labels = []
    for hemi in check_hemi(hemi):
        hemi_annot_fname = op.join(labels_fol, '{}.{}.annot'.format(hemi, atlas))
        if op.isfile(hemi_annot_fname):
            labels.extend(read_labels_from_annot(hemi_annot_fname))
        else:
            labels_files = glob.glob(op.join(labels_fol, atlas, '*.label'))
            for label_fname in labels_files:
                new_label = read_label_file(label_fname)
                if new_label is not None and new_label.hemi == hemi:
                    labels.append(new_label)
    return sorted(labels, key=lambda l: l.name)


def read_label_from_annot(atlas, hemi='both', labels_fol=''):
    if labels_fol == '':
        labels_fol = get_atlas_labels_fol(atlas)
    if labels_fol == '':
        return []
    for hemi in check_hemi(hemi):
        hemi_annot_fname = op.join(labels_fol, '{}.{}.annot'.format(hemi, atlas))
        if op.isfile(hemi_annot_fname):
            labels = read_labels_from_annot(hemi_annot_fname)

def get_atlas_labels_fol(atlas):
    subjects_labels_fol = op.join(get_subjects_dir(), get_user(), 'label')
    mmvt_labels_fol = op.join(get_user_fol(), 'labels')
    if check_if_atlas_exist(subjects_labels_fol, atlas):
        return subjects_labels_fol
    elif check_if_atlas_exist(mmvt_labels_fol, atlas):
        return mmvt_labels_fol
    else:
        return ''


def check_if_atlas_exist(labels_fol, atlas):
    return both_hemi_files_exist(op.join(labels_fol, '{}.{}.annot'.format('{hemi}', atlas))) or \
        len(glob.glob(op.join(labels_fol, atlas, '*.label'))) > 0


def find_annot_labels(subjects_dir='', atlas='aparc.DKTatlas'):
    if subjects_dir == '':
        subjects_dir = get_link_dir(get_links_dir(), 'subjects')
    labels = []
    lh_annot_files = glob.glob(op.join(subjects_dir, 'fsaverage*', 'label', 'lh.{}.annot'.format(atlas)))
    if len(lh_annot_files) == 0:
        lh_annot_files = glob.glob(op.join(subjects_dir, '**', 'label', 'lh.{}.annot'.format(atlas)), recursive=True)
    if len(lh_annot_files) > 0:
        for lh_annot_file in lh_annot_files:
            annot_fol = get_parent_fol(lh_annot_file)
            rh_annot_file = op.join(annot_fol, 'rh.{}.annot'.format(atlas))
            if op.isfile(rh_annot_file):
                labels = read_labels_from_annots(atlas, hemi='both', labels_fol=annot_fol)
                break
    return labels


def check_atlas_by_labels_names(labels_names):
    subjects_dir = get_link_dir(get_links_dir(), 'subjects')
    for atlas in ['aparc.DKTatlas', 'aparc', 'aparc.a2009s', 'aparc250', 'laus125', 'laus250', 'laus500']:
        atlas_labels = find_annot_labels(subjects_dir, atlas)
        atlas_labels_names = set([l.name for l in atlas_labels])
        if set(labels_names).issubset(atlas_labels_names):
            return atlas
    return ''


def read_label_vertices_from_annot(annot_fname, label_name):
    annot, ctab, label_names = _read_annot(annot_fname)
    label_ids = ctab[:, -1]
    inv_label_name = get_label_hemi_invariant_name(label_name)
    vertices = None
    for label_id, label_name in zip(label_ids, label_names):
        if inv_label_name == label_name.decode():
            vertices = np.where(annot == label_id)[0]
            break
    return vertices


@functools.lru_cache(maxsize=None)
def read_labels_from_annot(annot_fname):
    """Read labels from a FreeSurfer annotation file.

    Note: Only cortical labels will be returned.

    Parameters
    ----------
    subject : str
        The subject for which to read the parcellation for.
    parc : str
        The parcellation to use, e.g., 'aparc' or 'aparc.a2009s'.
    hemi : str
        The hemisphere to read the parcellation for, can be 'lh', 'rh',
        or 'both'.
    surf_name : str
        Surface used to obtain vertex locations, e.g., 'white', 'pial'
    annot_fname : str or None
        Filename of the .annot file. If not None, only this file is read
        and 'parc' and 'hemi' are ignored.
    regexp : str
        Regular expression or substring to select particular labels from the
        parcellation. E.g. 'superior' will return all labels in which this
        substring is contained.
    subjects_dir : string, or None
        Path to SUBJECTS_DIR if it is not set in the environment.
    verbose : bool, str, int, or None
        If not None, override default verbose level (see :func:`mne.verbose`
        and :ref:`Logging documentation <tut_logging>` for more).

    Returns
    -------
    labels : list of Label
        The labels, sorted by label name (ascending).
    """
    labels = list()
    hemi = get_hemi_from_fname(namebase_with_ext(annot_fname))
    annot, ctab, label_names = _read_annot(annot_fname)
    label_rgbas = ctab[:, :4]
    label_ids = ctab[:, -1]

    for label_id, label_name, label_rgba in zip(label_ids, label_names, label_rgbas):
        vertices = np.where(annot == label_id)[0]
        if len(vertices) == 0:
            # label is not part of cortical surface
            continue
        name = label_name.decode() + '-' + hemi
        # label = Label(name, hemi, vertices, [], [])
        label = Label(vertices, None, None, hemi, name=name)
        labels.append(label)

    # sort the labels by label name
    labels = sorted(labels, key=lambda l: l.name)
    return labels


def _read_annot(fname):
    """Read a Freesurfer annotation from a .annot file.

    Note : Copied from PySurfer

    Parameters
    ----------
    fname : str
        Path to annotation file

    Returns
    -------
    annot : numpy array, shape=(n_verts)
        Annotation id at each vertex
    ctab : numpy array, shape=(n_entries, 5)
        RGBA + label id colortable array
    names : list of str
        List of region names as stored in the annot file

    """
    with open(fname, "rb") as fid:
        n_verts = np.fromfile(fid, '>i4', 1)[0]
        data = np.fromfile(fid, '>i4', n_verts * 2).reshape(n_verts, 2)
        annot = data[data[:, 0], 1]
        ctab_exists = np.fromfile(fid, '>i4', 1)[0]
        if not ctab_exists:
            raise Exception('Color table not found in annotation file')
        n_entries = np.fromfile(fid, '>i4', 1)[0]
        if n_entries > 0:
            length = np.fromfile(fid, '>i4', 1)[0]
            # orig_tab = np.fromfile(fid, '>c', length)
            # orig_tab = orig_tab[:-1]

            names = list()
            ctab = np.zeros((n_entries, 5), np.int)
            for i in range(n_entries):
                name_length = np.fromfile(fid, '>i4', 1)[0]
                name = np.fromfile(fid, "|S%d" % name_length, 1)[0]
                names.append(name)
                ctab[i, :4] = np.fromfile(fid, '>i4', 4)
                ctab[i, 4] = (ctab[i, 0] + ctab[i, 1] * (2 ** 8) +
                              ctab[i, 2] * (2 ** 16) +
                              ctab[i, 3] * (2 ** 24))
        else:
            ctab_version = -n_entries
            if ctab_version != 2:
                raise Exception('Color table version not supported')
            n_entries = np.fromfile(fid, '>i4', 1)[0]
            ctab = np.zeros((n_entries, 5), np.int)
            length = np.fromfile(fid, '>i4', 1)[0]
            np.fromfile(fid, "|S%d" % length, 1)  # Orig table path
            entries_to_read = np.fromfile(fid, '>i4', 1)[0]
            names = list()
            for i in range(entries_to_read):
                np.fromfile(fid, '>i4', 1)  # Structure
                name_length = np.fromfile(fid, '>i4', 1)[0]
                name = np.fromfile(fid, "|S%d" % name_length, 1)[0]
                names.append(name)
                ctab[i, :4] = np.fromfile(fid, '>i4', 4)
                ctab[i, 4] = (ctab[i, 0] + ctab[i, 1] * (2 ** 8) +
                              ctab[i, 2] * (2 ** 16))

        # convert to more common alpha value
        ctab[:, 3] = 255 - ctab[:, 3]

    return annot, ctab, names


def create_labels_contours():
    subject, atlas = get_user(), bpy.context.scene.subject_annot_files
    cmd = '{} -m src.preproc.anatomy -s {} -a {} -f create_spatial_connectivity,calc_labeles_contours --ignore_missing 1'.format(
        bpy.context.scene.python_cmd, subject, atlas)
    # get_code_root_dir
    run_command_in_new_thread(cmd, False)


def make_link(source, target, overwrite=False, copy_if_fails=True):
    if is_windows():
        try:
            # https://stackoverflow.com/questions/1447575/symlinks-on-windows
            import ctypes
            kdll = ctypes.windll.LoadLibrary("kernel32.dll")
            ret = kdll.CreateSymbolicLinkA(source, target, 0)
            if (not ret or op.getsize(target) == 0) and copy_if_fails:
                remove_file(target)
                shutil.copy(source, target)
            return op.exists(target)
        except:
            print(traceback.format_exc())
    try:
        if op.exists(source):
            ret = os.symlink(source, target)
            if not ret and copy_if_fails:
                shutil.copy(source, target)
            return True
        else:
            print('make_link: source {} doesn\'t exist!'.format(source))
            return False
    except FileExistsError as e:
        if not overwrite:
            print('{} already exist'.format(target))
        else:
            try:
                if op.isfile(target):
                    os.remove(target)
                os.symlink(source, target)
            except:
                print('Couldn\'t remove {}!'.format(target))
        return True
    except:
        print(traceback.format_exc())
        return False


def both_hemi_files_exist(file_template):
    if isinstance(file_template, dict):
        return all([op.isfile(file_template[hemi]) for hemi in HEMIS])
    if '*' not in file_template:
        return op.isfile(file_template.format(hemi='rh')) and op.isfile(file_template.format(hemi='lh'))
    else:
        return len(glob.glob(file_template.format(hemi='rh'))) == 1 and \
               len(glob.glob(file_template.format(hemi='lh'))) == 1


def delete_files(temp):
    for fname in glob.glob(temp):
        os.remove(fname)


def print_traceback():
    import traceback
    print(''.join(traceback.format_stack().strip()))


def file_modification_time(fname):
    from datetime import datetime
    try:
        mtime = os.path.getmtime(fname)
    except OSError:
        mtime = 0
    return datetime.fromtimestamp(mtime)


def apply_trans(trans, points):
    # return np.dot(trans, np.append(point, 1))[:3]
    if len(points) == 0:
        return []
    if isinstance(points, list):
        points = np.array(points)
    ndim = points.ndim
    if ndim == 1:
        points = np.array([points])
    points = np.hstack((points, np.ones((len(points), 1))))
    points = np.dot(trans, points.T).T
    points = points[:, :3]
    if ndim == 1:
        points = points[0]
    return points


def remove_file(fname, raise_error_if_does_not_exist=False):
    try:
        if op.isfile(fname):
            os.remove(fname)
    except:
        if raise_error_if_does_not_exist:
            raise Exception(traceback.format_exc())
        else:
            print(traceback.format_exc())


def get_click_area(event, context):
    screen = context.window.screen  # or context.screen
    for a in screen.areas:
        if (a.x < event.mouse_x < a.x + a.width
                and a.y < event.mouse_y < a.y + a.height):
            return a


def flat_list_of_lists(l):
    return sum(l, [])


def get_distinct_colors_hs(colors_num=0):
    return np.linspace(0, 360, colors_num + 1)[:-1] / 360


def get_distinct_colors(colors_num=1):
    hs = get_distinct_colors_hs(colors_num)
    return [colorsys.hls_to_rgb(hs[ind], 0.5, 1) for ind in range(colors_num)]


def calc_colors_from_cm(vert_values, data_min, colors_ratio, cm):
    colors_indices = calc_colors_indices(vert_values, data_min, colors_ratio)
    return calc_colors_from_indices_cm(colors_indices, cm)


def calc_colors_indices(vert_values, data_min, colors_ratio):
    return np.rint(((np.array(vert_values) - data_min) * colors_ratio)).astype(int)


def calc_colors_from_indices_cm(colors_indices, cm):
    # take care about values that are higher or smaller than the min and max values that were calculated (maybe using precentiles)
    colors_indices[colors_indices < 0] = 0
    colors_indices[colors_indices > 255] = 255
    verts_colors = cm[colors_indices]
    return verts_colors


def in_shape(xyz, shape):
    x, y, z = xyz
    return 0 <= x < shape[0] and 0 <= y < shape[1] and 0 <= z < shape[2]


def find_hemi_using_vertices_num(fname):
    hemi = ''
    if NIB_EXIST:
        x = nib.load(fname).get_data()
        vertices_num = [n for n in x.shape if n > 5]
        if len(vertices_num) == 0:
            print("Can'f find the vertices number of the nii file! {}".format(fname))
        else:
            vertices_num = vertices_num[0]
            verts_num = get_vertices_num()
            if vertices_num == verts_num['rh']:
                hemi = 'rh'
            elif vertices_num == verts_num['lh']:
                hemi = 'lh'
            else:
                print("The vertices num ({}) in the nii file ({}) doesn't match any hemi! (rh:{}, lh:{})".format(
                    vertices_num, fname, verts_num['rh'], verts_num['lh']))
                hemi = ''
    return hemi


def get_vertices_num():
    return {hemi:len(bpy.data.objects[hemi].data.vertices) for hemi in HEMIS}


def get_hemi_obj(hemi):
    return bpy.data.objects['inflated_{}'.format(hemi)]


def write_to_stderr(str):
    sys.stderr.write('{}\n'.format(str))
    sys.stderr.flush()


def get_vert_co(vert_ind, hemi):
    me, obj = get_hemi_mesh(hemi)
    vertex_co = me.vertices[vert_ind].co * obj.matrix_world
    bpy.data.meshes.remove(me)
    return vertex_co


def get_verts_co(vert_inds, hemis):
    from mathutils import Vector
    hemis_mesh, objs = {}, {}
    vertex_co = []
    surf_dict = {-1:'pial', 0:'inflated', 1:'flat'}
    if bpy.context.scene.inflating in surf_dict.keys():
        surf_type = surf_dict[bpy.context.scene.inflating]
        for hemi in HEMIS:
            objs[hemi] = bpy.data.objects['inflated_{}'.format(hemi)]
            hemis_mesh[hemi] = objs[hemi].data.shape_keys.key_blocks[surf_type].data
        for vert_ind, hemi in zip(vert_inds, hemis):
            vertex_co.append(hemis_mesh[hemi][vert_ind].co * objs[hemi].matrix_world +
                             Vector(tuple(np.array(objs[hemi].matrix_world)[:3, 3])))

    # elif -1 < bpy.context.scene.inflating < 0:
    #     hemis_pial_mesh, hemis_inflated_mesh = {}, {}
    #     for hemi in HEMIS:
    #         objs[hemi] = bpy.data.objects['inflated_{}'.format(hemi)]
    #         hemis_pial_mesh[hemi] = objs[hemi].data.shape_keys.key_blocks['pial'].data
    #         hemis_inflated_mesh[hemi] = objs[hemi].data.shape_keys.key_blocks['inflated'].data
    #     for vert_ind, hemi in zip(vert_inds, hemis):
    #         vertex_co.append((hemis_pial_mesh[hemi][vert_ind].co * objs[hemi].matrix_world * (1 + bpy.context.scene.inflating)) + \
    #                          (hemis_inflated_mesh[hemi][vert_ind].co * objs[hemi].matrix_world * abs(bpy.context.scene.inflating)))
    #

    else:
        for hemi in HEMIS:
            hemis_mesh[hemi], objs[hemi] = get_hemi_mesh(hemi)
        for vert_ind, hemi in zip(vert_inds, hemis):
            vertex_co.append(hemis_mesh[hemi].vertices[vert_ind].co * objs[hemi].matrix_world)
        for hemi in HEMIS:
            bpy.data.meshes.remove(hemis_mesh[hemi])
    return vertex_co


def get_hemi_mesh(hemi):
    obj_name = 'inflated_{}'.format(hemi)
    obj = bpy.data.objects[obj_name]
    return obj.to_mesh(bpy.context.scene, True, 'PREVIEW'), obj


def index_in_list(item, lst, default=-1):
    if item in lst:
        return lst.index(item)
    else:
        return default


def mouse_coo_to_3d_loc(event, context):
    from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d
    coord = event.mouse_region_x, event.mouse_region_y
    region = context.region
    rv3d = context.space_data.region_3d
    vec = region_2d_to_vector_3d(region, rv3d, coord)
    loc = region_2d_to_location_3d(region, rv3d, coord, vec)
    return loc


def points_in_cylinder(pt1, pt2, points, radius_sq, N=100):
    from scipy.spatial.distance import cdist
    # dist = np.linalg.norm(pt1 - pt2)
    # elc_ori = (pt2 - pt1) / dist
    # elc_line = (pt1.reshape(3, 1) + elc_ori.reshape(3, 1) @ np.linspace(0, dist, N).reshape(1, N)).T
    elc_line = get_elc_line(pt1, pt2, N)
    dists = np.min(cdist(elc_line, points), 0)
    points_inside_cylinder = np.where(dists <= radius_sq)[0]
    return points_inside_cylinder, elc_line, dists[points_inside_cylinder]


def get_elc_line(pt1, pt2, N=100):
    dist = np.linalg.norm(pt1 - pt2)
    elc_ori = (pt2 - pt1) / dist
    return (pt1.reshape(3, 1) + elc_ori.reshape(3, 1) @ np.linspace(0, dist, N).reshape(1, N)).T


def move_electrodes_to_line(pt1, pt2, points, N=100):
    from scipy.spatial.distance import cdist
    elc_line = get_elc_line(pt1, pt2, N)
    new_points = []
    for elc_pos in points:
        elc_line_ind = np.argmin(cdist([elc_pos], elc_line), 1)[0]
        new_points.append(elc_line[elc_line_ind])
    return new_points


def argmax2d(data):
    return np.unravel_index(np.argmax(data), data.shape)


def is_float(x):
    try:
        float(x)
        return True
    except:
        return False


def is_int(x):
    try:
        int(x)
        return True
    except:
        return False


def run_mmvt_func(module, func_name='', flags='', add_subject=False):
    if 'preproc' in module.split('.'):
        flags += ' -s {} --ignore_missing 1'.format(get_user())
    elif add_subject:
        flags += ' -s {}'.format(get_user())
    cmd = '{} -m {} {}{} '.format(
        bpy.context.scene.python_cmd, module, '-f {} '.format(func_name) if func_name != '' else '', flags)
    run_command_in_new_thread(cmd, False, cwd=get_mmvt_code_root())


def load_npz_to_bag(npz_fname):
    return Bag(dict(np.load(npz_fname)))


# Those matlab function are taken from matlab_utils
def load_mat_to_bag(mat_fname):
    import scipy.io as sio
    return Bag(dict(**sio.loadmat(mat_fname)))


def matlab_cell_str_to_list(cell_arr):
    if len(cell_arr[0]) > 1:
        ret_list = [cell_arr[0][ind][0].astype(str) for ind in range(len(cell_arr[0]))]
    else:
        ret_list = [cell_arr[ind][0][0].astype(str) for ind in range(len(cell_arr))]
    return ret_list


def write_ply_file(verts, faces, ply_file_name):
    ply_header = 'ply\nformat ascii 1.0\nelement vertex {}\nproperty float x\nproperty float y\n' + \
                 'property float z\nelement face {}\nproperty list uchar int vertex_index\nend_header\n'
    verts_num = verts.shape[0]
    faces_num = faces.shape[0]
    faces = faces.astype(np.int)
    faces_for_ply = np.hstack((np.ones((faces_num, 1)) * faces.shape[1], faces))
    with open(ply_file_name, 'w') as f:
        f.write(ply_header.format(verts_num, faces_num))
    with open(ply_file_name, 'ab') as f:
        np.savetxt(f, verts, fmt='%.5f', delimiter=' ')
        np.savetxt(f, faces_for_ply, fmt='%d', delimiter=' ')


def select_time_range(t_start=None, t_end=None):
    if t_start is not None:
        bpy.data.scenes['Scene'].frame_preview_start = t_start
    if t_end is not None:
        bpy.data.scenes['Scene'].frame_preview_end = t_end


def load_remote_subject_info():
    remote_subject_info_fname = op.join(get_user_fol(), 'remote_subject_info.pkl')
    if op.isfile(remote_subject_info_fname):
        remote_subject_info = load(remote_subject_info_fname)
    else:
        remote_subject_info = None
    return remote_subject_info


def get_remote_subject_info_args():
    remote_subject_info = load_remote_subject_info()
    if remote_subject_info is not None:
        args = Bag(remote_subject_info)
    else:
        args = Bag(dict(remote_subject_dir=get_subjects_dir()))
    return args


def get_annot_files():
    subjects_dir = get_link_dir(get_links_dir(), 'subjects')
    return [namebase(fname)[3:] for fname in glob.glob(op.join(subjects_dir, get_user(), 'label', 'rh.*.annot'))]


def get_annot_fname(hemi, atlas):
    subjects_dir = get_link_dir(get_links_dir(), 'subjects')
    annot_fname = op.join(subjects_dir, get_user(), 'label', '{}.{}.annot'.format(hemi, atlas))
    if not op.isfile(annot_fname):
        annot_fname = op.join(get_user_fol(), 'labels', '{}.{}.annot'.format(hemi, atlas))
    return annot_fname


def children(obj_name):
    obj = bpy.data.objects.get(obj_name)
    return [] if obj is None else obj.children


def is_freesurfer_exist():
    return os.environ.get('FREESURFER_HOME', '') != ''


def in_range(val, min_val, max_val):
    if min_val <= val <= max_val:
        return val
    elif val < min_val:
        return min_val
    elif val > max_val:
        return max_val


def in_mat(x, y, z, mat):
    X, Y, Z = mat.shape
    return in_range(x, 0, X - 1), in_range(y, 0, Y - 1), in_range(z, 0, Z - 1)


def fix_children_normals(parent_obj):
    if isinstance(parent_obj, str):
        parent_obj =  bpy.data.objects.get(parent_obj)
    if parent_obj is None:
        print('Can\'t find {}!'.format(parent_obj.name))
        return
    # for obj in bpy.data.objects:
    #     obj.select = False
    bpy.ops.object.select_all(action='DESELECT')
    bm = bmesh.new()
    for obj in parent_obj.children:
        mesh = obj.data
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.clear()
        mesh.update()
    bm.free()


def fix_normals(obj):
    if isinstance(obj, str):
        obj =  bpy.data.objects.get(obj)
    bpy.ops.object.select_all(action='DESELECT')
    bm = bmesh.new()
    mesh = obj.data
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.clear()
    mesh.update()
    bm.free()


def recalc_normals(obj, calc_inside=False):
    if isinstance(obj, str):
        obj =  bpy.data.objects.get(obj)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    bpy.context.scene.objects.active = obj
    # go edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # select al faces
    bpy.ops.mesh.select_all(action='SELECT')
    # recalculate outside normals
    bpy.ops.mesh.normals_make_consistent(inside=calc_inside)
    # go object mode again
    bpy.ops.object.editmode_toggle()


def prop_exist(prop_name):
    try:
        bpy.context.scene.__getattribute__(prop_name)
        return True
    except:
        return False


def set_prop(prop_name, prop_val):
    if prop_exist(prop_name):
        if is_int(prop_val):
            prop_val = int(prop_val)
        elif is_float(prop_val):
            prop_val = float(prop_val)
        bpy.context.scene.__setattr__(prop_name, prop_val)


def get_cursor_location():
    return bpy.context.scene.cursor_location


def add_marker(index, name):
    bpy.context.scene.frame_current = index
    bpy.ops.marker.add()
    bpy.ops.marker.rename(name=name)


# def mouse_coo_to_3d_loc(event, context):
#     from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d
#     try:
#         # coord = event.mouse_region_x, event.mouse_region_y
#         area, region = get_3d_area_region()
#         coord = (event.mouse_x - area.x, event.mouse_y - area.y)
#         # region = context.region
#         # rv3d = context.space_data.region_3d
#         rv3d = area.spaces.active.region_3d
#         vec = region_2d_to_vector_3d(region, rv3d, coord)
#         pos = region_2d_to_location_3d(region, rv3d, coord, vec)
#     except:
#         pos = None
#         print(traceback.format_exc())
#         print("Couldn't convert mouse coo to 3d loc!")
#     return pos
#

# def mouse_coo_to_3d_loc(event, context):
#     from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d
#
#     mouse_pos = [event.mouse_region_x, event.mouse_region_y]
#
#     # Contextual active object, 2D and 3D regions
#     object = bpy.data.objects['inflated_rh']
#     region = bpy.context.region
#     region3D = bpy.context.space_data.region_3d
#
#     # The direction indicated by the mouse position from the current view
#     view_vector = region_2d_to_vector_3d(region, region3D, mouse_pos)
#     # The 3D location in this direction
#     loc = region_2d_to_location_3d(region, region3D, mouse_pos, view_vector)
#     # The 3D location converted in object local coordinates
#     loc = object.matrix_world.inverted() * loc
#     return loc
