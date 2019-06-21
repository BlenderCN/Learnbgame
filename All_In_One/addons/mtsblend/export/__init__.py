# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK *****

from collections import OrderedDict, Counter

import os

import bpy
import mathutils

from ..extensions_framework import util as efutil

from ..outputs import MtsManager, MtsLog


class ExportProgressThread(efutil.TimerThread):
    KICK_PERIOD = 0.2
    total_objects = 0
    exported_objects = 0
    last_update = 0
    message = '%i%%'

    def start(self, number_of_meshes):
        self.total_objects = number_of_meshes
        self.exported_objects = 0
        self.last_update = 0
        super().start()

    def kick(self):
        if self.exported_objects != self.last_update:
            self.last_update = self.exported_objects
            pc = int(100 * self.exported_objects / self.total_objects)
            MtsLog(self.message % pc)


class ExportCache:
    def __init__(self, name='Cache'):
        self.name = name
        self.cache_keys = set()
        self.cache_items = {}
        self.serial_counter = Counter()

    def clear(self):
        self.__init__(name=self.name)

    def serial(self, name):
        s = self.serial_counter[name]
        self.serial_counter[name] += 1

        return s

    def have(self, ck):
        return ck in self.cache_keys

    def add(self, ck, ci):
        self.cache_keys.add(ck)
        self.cache_items[ck] = ci

    def get(self, ck):
        if self.have(ck):
            return self.cache_items[ck]

        else:
            raise Exception('Item %s not found in %s!' % (ck, self.name))


class ExportContextBase:
    '''
    Export Context base class
    '''

    EXPORT_API_TYPE = ''
    scene_data = None
    counter = 0
    exported_media = set()
    exported_ids = set()
    motion = {}
    color_mode = 'rgb'

    def __init__(self):
        self.scene_data = OrderedDict([('type', 'scene')])
        self.counter = 0
        self.exported_media = set()
        self.exported_ids = set()
        self.motion = {}

    def get_export_path(self, path, id_data=None, relative=False):
        if id_data is not None and id_data.library is not None:
            path = bpy.path.abspath(path, id_data.library.filepath)

        if relative and self.EXPORT_API_TYPE == 'FILE':
            return efutil.path_relative_to_export(path)

        else:
            return efutil.filesystem_path(path)

    def exportMedium(self, scene, medium):
        if medium.name in self.exported_media:
            return

        self.exported_media.add(medium.name)

        params = medium.api_output(self, scene)

        self.data_add(params)

    # Function to add new elements to the scene dict.
    # If a name is provided it will be used as the key of the element.
    # Otherwise the Id of the element is used if it exists
    # or a new key is generated incrementally.
    def data_add(self, mts_dict, name=''):
        if mts_dict is None or not isinstance(mts_dict, dict) or len(mts_dict) == 0 or 'type' not in mts_dict:
            return False

        if not name:
            try:
                name = mts_dict['id']

            except:
                name = 'elm%i' % self.counter

        self.scene_data.update([(name, mts_dict)])
        self.counter += 1

        return True


class Instance:
    obj = None
    motion = []
    mesh = None

    def __init__(self, obj, trafo=None, mesh=None):
        self.obj = obj

        if trafo is not None:
            self.motion = [(0.0, trafo)]

        else:
            self.motion = []

        if mesh is not None:
            self.mesh = [mesh]

        else:
            self.mesh = None

    def append_motion(self, trafo, seq, is_deform=False):
        seqs = len(self.motion)

        if self.motion:
            last_matrix = self.motion[-1][1]

        else:
            last_matrix = None

        if not is_deform and (seqs > 1 and trafo == last_matrix and
                last_matrix == self.motion[-2][1]):
            self.motion[-1] = (seq, trafo)

        else:
            self.motion.append((seq, trafo))


class ReferenceCounter:
    stack = []

    @classmethod
    def reset(cls):
        cls.stack = []

    def __init__(self, name):
        self.ident = name

    def __enter__(self):
        if self.ident in ReferenceCounter.stack:
            raise Exception("Recursion in reference link: %s -- %s" % (self.ident, ' -> '.join(ReferenceCounter.stack)))

        ReferenceCounter.stack.append(self.ident)

    def __exit__(self, exc_type, exc_val, exc_tb):
        ReferenceCounter.stack.pop()


def get_param_recursive_loop(scene_data, params, key):
    if isinstance(params, dict):
        if 'type' in params and params['type'] == 'ref':
            with ReferenceCounter(params['id']):
                for r in get_param_recursive_loop(scene_data, scene_data[params['id']], key):
                    yield r

        else:
            for k, p in params.items():
                if k == key:
                    yield p

                if isinstance(p, dict):
                    for r in get_param_recursive_loop(scene_data, p, key):
                        yield r


def get_param_recursive(scene_data, params, key):
    ReferenceCounter.reset()
    for r in get_param_recursive_loop(scene_data, params, key):
        yield r


def get_references(params):
    if isinstance(params, dict):
        for p in params.values():
            if isinstance(p, dict):
                if 'type' in p and p['type'] == 'ref' and p['id'] != '':
                    yield p

                else:
                    for r in get_references(p):
                        yield r


def object_render_hide_original(ob_type, dupli_type):
    # metaball exception, they duplicate self
    if ob_type == 'META':
        return False

    return dupli_type in {'VERTS', 'FACES', 'FRAMES'}


def object_render_hide_duplis(b_ob):
    parent = b_ob.parent

    return parent is not None and object_render_hide_original(b_ob.type, parent.dupli_type)


def object_render_hide(b_ob, top_level, parent_hide):
    # check if we should render or hide particle emitter
    hair_present = False
    show_emitter = False
    hide_emitter = False
    hide_as_dupli_parent = False
    hide_as_dupli_child_original = False

    for b_psys in b_ob.particle_systems:
        if b_psys.settings.render_type == 'PATH' and b_psys.settings.type == 'HAIR':
            hair_present = True

        if b_psys.settings.use_render_emitter:
            show_emitter = True
        else:
            hide_emitter = True

    if show_emitter:
        hide_emitter = False

    # duplicators hidden by default, except dupliframes which duplicate self
    if b_ob.is_duplicator:
        if top_level or b_ob.dupli_type != 'FRAMES':
            hide_as_dupli_parent = True

    # hide original object for duplis
    parent = b_ob.parent
    while parent is not None:
        if object_render_hide_original(b_ob.type, parent.dupli_type):
            if parent_hide:
                hide_as_dupli_child_original = True
                break

        parent = parent.parent

    hide_mesh = hide_emitter

    if show_emitter:
        return (False, hide_mesh)

    elif hair_present:
        return (hide_as_dupli_child_original, hide_mesh)

    else:
        return ((hide_as_dupli_parent or hide_as_dupli_child_original), hide_mesh)


def is_object_visible(scene, obj, is_dupli=False):
    ov = False
    for lv in [ol and sl and rl for ol, sl, rl in zip(obj.layers, scene.layers, scene.render.layers.active.layers)]:
        ov |= lv

    return (ov or is_dupli) and not obj.hide_render


def is_light(obj):
    return obj.type == 'LAMP'


def is_mesh(obj):
    return obj.type in {'MESH', 'CURVE', 'SURFACE', 'FONT'}


def is_subd_last(obj):
    return obj.modifiers and \
        obj.modifiers[len(obj.modifiers) - 1].type == 'SUBSURF'


def is_subd_displace_last(obj):
    if len(obj.modifiers) < 2:
        return False

    return (obj.modifiers[len(obj.modifiers) - 2].type == 'SUBSURF' and
            obj.modifiers[len(obj.modifiers) - 1].type == 'DISPLACE')


# XXX do this better, perhaps by hooking into modifier type data in RNA?
# Currently assumes too much is deforming when it isn't


def is_deforming(obj):
    deforming_modifiers = {'ARMATURE', 'CAST', 'CLOTH', 'CURVE', 'DISPLACE',
                           'HOOK', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP',
                           'SIMPLE_DEFORM', 'SMOOTH', 'WAVE', 'SOFT_BODY',
                           'SURFACE', 'MESH_CACHE'}
    if obj.type in {'MESH', 'SURFACE', 'FONT'} and obj.modifiers:
        # special cases for auto subd/displace detection
        if len(obj.modifiers) == 1 and is_subd_last(obj):
            return False
        if len(obj.modifiers) == 2 and is_subd_displace_last(obj):
            return False

        for mod in obj.modifiers:
            if mod.type in deforming_modifiers:
                return True

    return False


def get_worldscale(as_scalematrix=True):
    ws = 1

    scn_us = MtsManager.CurrentScene.unit_settings

    if scn_us.system in {'METRIC', 'IMPERIAL'}:
        # The units used in modelling are for display only. behind
        # the scenes everything is in meters
        ws = scn_us.scale_length

    if as_scalematrix:
        return mathutils.Matrix.Scale(ws, 4)

    else:
        return ws


def object_anim_matrices(scene, obj, steps=1):
    '''
    steps       Number of interpolation steps per frame

    Returns a list of animated matrices for the object, with the given number of
    per-frame interpolation steps.
    The number of matrices returned is at most steps+1.
    '''
    old_sf = scene.frame_subframe
    cur_frame = scene.frame_current

    ref_matrix = None
    animated = False

    next_matrices = []

    for i in range(0, steps + 1):
        scene.frame_set(cur_frame, subframe=i / float(steps))

        sub_matrix = obj.matrix_world.copy()

        if ref_matrix is None:
            ref_matrix = sub_matrix

        animated |= sub_matrix != ref_matrix
        next_matrices.append(sub_matrix)

    if not animated:
        next_matrices = []

    # restore subframe value
    scene.frame_set(cur_frame, old_sf)

    return next_matrices


def matrix_to_list(matrix, apply_worldscale=True):
    '''
    matrix        Matrix

    Flatten a 4x4 matrix into a list

    Returns list[16]
    '''

    if apply_worldscale:
        matrix = matrix.copy()
        sm = get_worldscale()
        matrix *= sm
        sm = get_worldscale(as_scalematrix=False)
        matrix[0][3] *= sm
        matrix[1][3] *= sm
        matrix[2][3] *= sm

    l = [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
        matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
        matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
        matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]

    return [float(i) for i in l]


def compute_normalized_radiance(emitter, color):
    max_color = max(color[:])

    if max_color > 1:
        normalized_color = color / max_color
        emitter.inputs['Radiance'].default_value = normalized_color
        emitter.scale = max_color

    else:
        emitter.inputs['Radiance'].default_value = color
        emitter.scale = 1.0


def get_output_subdir(scene, frame=None):
    if frame is None:
        frame = scene.frame_current

    subdir = os.path.join(efutil.export_path, efutil.scene_filename(), bpy.path.clean_name(scene.name), '{:0>5d}'.format(frame))

    if not os.path.exists(subdir):
        os.makedirs(subdir)

    return subdir


def get_output_filename(scene):
    return '%s.%s.%05d' % (efutil.scene_filename(), bpy.path.clean_name(scene.name), scene.frame_current)
