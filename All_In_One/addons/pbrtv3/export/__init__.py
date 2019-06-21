# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
# ***** END GPL LICENCE BLOCK *****
#
import collections, math, os, sys

import bpy, mathutils

from ..extensions_framework import util as efutil

from ..outputs import PBRTv3Manager, PBRTv3Log
from ..util import bencode_file2string_with_size


class ExportProgressThread(efutil.TimerThread):
    message = '%i%%'
    KICK_PERIOD = 0.2
    total_objects = 0
    exported_objects = 0
    last_update = 0

    def start(self, number_of_meshes):
        self.total_objects = number_of_meshes
        self.exported_objects = 0
        self.last_update = 0
        super().start()

    def kick(self):
        if self.exported_objects != self.last_update:
            self.last_update = self.exported_objects
            pc = int(100 * self.exported_objects / self.total_objects)
            PBRTv3Log(self.message % pc)


class ExportCache(object):
    def __init__(self, name='Cache'):
        self.name = name
        self.cache_keys = set()
        self.cache_items = {}
        self.serial_counter = collections.Counter()

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


class ParamSetItem(list):
    WRAP_WIDTH = 100

    def __init__(self, *args):
        self.type, self.name, self.value = args
        self.type_name = "%s %s" % (self.type, self.name)
        self.append(self.type_name)
        self.append(self.value)

    def getSize(self, vl=None):
        sz = 0

        if vl is None:
            vl = self.value
            sz += 100  # Rough overhead for encoded paramset item

        if type(vl) in (list, tuple):
            for v in vl:
                sz += self.getSize(vl=v)

        if type(vl) is str:
            sz += len(vl)
        if type(vl) is float:
            sz += 14
        if type(vl) is int:
            if vl == 0:
                sz += 1
            else:
                sz += math.floor(math.log10(abs(vl))) + 1

        return sz

    def list_wrap(self, lst, cnt, type='f'):
        fcnt = float(cnt)
        flen = float(len(lst))

        if False:  # flen > fcnt:
            # List wrapping disabled because it is hideously expensive
            s = ''
            if type == 'f':
                for row in range(math.ceil(flen / fcnt)):
                    s += ' '.join(['%0.15f' % i for i in lst[(row * cnt):(row + 1) * cnt]]) + '\n'
            elif type == 'i':
                for row in range(math.ceil(flen / fcnt)):
                    s += ' '.join(['%i' % i for i in lst[(row * cnt):(row + 1) * cnt]]) + '\n'
        else:
            if type == 'f':
                s = ' '.join(['%0.15f' % i for i in lst])
            elif type == 'i':
                s = ' '.join(['%i' % i for i in lst])
        return s

    def to_string(self):
        fs_num = '"%s %s" [%s]'
        fs_str = '"%s %s" ["%s"]'

        if self.type == "float" and type(self.value) in (list, tuple):
            lst = self.list_wrap(self.value, self.WRAP_WIDTH, 'f')
            return fs_num % ('float', self.name, lst)
        if self.type == "float":
            return fs_num % ('float', self.name, '%0.15f' % self.value)
        if self.type == "integer" and type(self.value) in (list, tuple):
            lst = self.list_wrap(self.value, self.WRAP_WIDTH, 'i')
            return fs_num % ('integer', self.name, lst)
        if self.type == "integer":
            return fs_num % ('integer', self.name, '%i' % self.value)
        if self.type == "string":
            if type(self.value) is list:
                return fs_num % ('string', self.name, '\n'.join(['"%s"' % v for v in self.value]))
            else:
                return fs_str % ('string', self.name, self.value.replace('\\', '\\\\'))
        if self.type == "vector":
            lst = self.list_wrap(self.value, self.WRAP_WIDTH, 'f')
            return fs_num % ('vector', self.name, lst)
        if self.type == "point":
            lst = self.list_wrap(self.value, self.WRAP_WIDTH, 'f')
            return fs_num % ('point', self.name, lst)
        if self.type == "normal":
            lst = self.list_wrap(self.value, self.WRAP_WIDTH, 'f')
            return fs_num % ('normal', self.name, lst)
        if self.type == "color":
            return fs_num % ('color', self.name, ' '.join(['%0.8f' % i for i in self.value]))
        if self.type == "texture":
            return fs_str % ('texture', self.name, self.value)
        if self.type == "bool":
            if self.value:
                return fs_str % ('bool', self.name, 'true')
            else:
                return fs_str % ('bool', self.name, 'false')

        return '# unknown param (%s, %s, %s)' % (self.type, self.name, self.value)


class ParamSet(list):
    def __init__(self):
        self.names = []
        self.item_sizes = {}

    def increase_size(self, param_name, sz):
        self.item_sizes[param_name] = sz

    def getSize(self):
        sz = 0
        item_sizes_keys = self.item_sizes.keys()
        for p in self:
            if p.name in item_sizes_keys:
                sz += self.item_sizes[p.name]
            else:
                sz += p.getSize()
        return sz

    def update(self, other):
        for p in other:
            self.add(p.type, p.name, p.value)
        return self

    def add(self, type, name, value):
        if name in self.names:
            for p in self:
                if p.name == name:
                    self.remove(p)

        self.append(
            ParamSetItem(type, name, value)
        )
        self.names.append(name)
        return self

    def add_float(self, name, value):
        self.add('float', name, value)
        return self

    def add_integer(self, name, value):
        self.add('integer', name, value)
        return self

    def add_bool(self, name, value):
        self.add('bool', name, bool(value))
        return self

    def add_string(self, name, value):
        if type(value) is list:
            self.add('string', name, [str(v) for v in value])
        else:
            self.add('string', name, str(value))
        return self

    def add_vector(self, name, value):
        self.add('vector', name, [i for i in value])
        return self

    def add_point(self, name, value):
        self.add('point', name, [p for p in value])
        return self

    def add_normal(self, name, value):
        self.add('normal', name, [n for n in value])
        return self

    def add_color(self, name, value):
        self.add('color', name, [c for c in value])
        return self

    def add_texture(self, name, value):
        self.add('texture', name, str(value))
        return self


def is_obj_visible(scene, obj, is_dupli=False, is_viewport_render=False):
    hidden = obj.hide if is_viewport_render else obj.hide_render

    ov = False
    for lv in [ol and sl and rl for ol, sl, rl in zip(obj.layers, scene.layers, scene.render.layers.active.layers)]:
        ov |= lv
    return (ov or is_dupli) and not hidden


def get_worldscale(as_scalematrix=True):
    """
    For usability, previev_scale is not an own property but calculated from the object dimensions
    A user can directly judge mappings on an adjustable object_size, we simply scale the whole preview
    """
    preview_scale = bpy.context.scene.pbrtv3_world.preview_object_size / 2

    # This is a safety net to prevent previewscale affecting render
    ws = 1 / preview_scale if PBRTv3Manager.CurrentScene.name == "preview" else 1

    scn_us = PBRTv3Manager.CurrentScene.unit_settings

    if scn_us.system in ['METRIC', 'IMPERIAL']:
        # The units used in modelling are for display only. behind
        # the scenes everything is in meters
        ws = scn_us.scale_length

    if as_scalematrix:
        return mathutils.Matrix.Scale(ws, 4)
    else:
        return ws


def object_anim_matrices(scene, obj, steps=1):
    """
    steps		Number of interpolation steps per frame

    Returns a list of animated matrices for the object, with the given number of
    per-frame interpolation steps.
    The number of matrices returned is at most steps+1.
    """
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


# hack for the matrix order api change in r42816
# TODO remove this when obsolete
def fix_matrix_order_old(matrix):
    return matrix.transposed()


def fix_matrix_order_new(matrix):
    return matrix


if bpy.app.version >= (2, 62, 0 ):
    fix_matrix_order = fix_matrix_order_new
else:
    fix_matrix_order = fix_matrix_order_old


def matrix_to_list(matrix, apply_worldscale=False, invert=False):
    """
    matrix		  Matrix

    Flatten a 4x4 matrix into a list

    Returns list[16]
    """

    if apply_worldscale:
        matrix = matrix.copy()
        sm = get_worldscale()
        matrix *= sm
        ws = get_worldscale(as_scalematrix=False)
        matrix = fix_matrix_order(matrix)  # matrix indexing hack
        matrix[0][3] *= ws
        matrix[1][3] *= ws
        matrix[2][3] *= ws
    else:
        matrix = fix_matrix_order(matrix)  # matrix indexing hack

    if invert:
        matrix.invert()

    l = [matrix[0][0], matrix[1][0], matrix[2][0], matrix[3][0],
         matrix[0][1], matrix[1][1], matrix[2][1], matrix[3][1],
         matrix[0][2], matrix[1][2], matrix[2][2], matrix[3][2],
         matrix[0][3], matrix[1][3], matrix[2][3], matrix[3][3]]

    return [float(i) for i in l]


def get_expanded_file_name(obj, file_path):
    """
    :param obj: object where file_path comes from
    :param file_path: file name relative to object
    :return: full file name (on disk), basename of file
    """
    file_path = file_path.replace("\\", os.path.sep)
    file_basename = os.path.basename(file_path)

    if hasattr(obj, 'library') and obj.library:
        return bpy.path.abspath(file_path, library=obj.library), file_basename

    return bpy.path.abspath(file_path), file_basename


def process_filepath_data(scene, obj, file_path, paramset, parameter_name):
    file_basename = os.path.basename(file_path)
    library_filepath = obj.library.filepath if (hasattr(obj, 'library') and obj.library) else ''
    file_library_path = efutil.filesystem_path(bpy.path.abspath(file_path, library_filepath))
    file_relative = efutil.filesystem_path(file_library_path) if (
        hasattr(obj, 'library') and obj.library) else efutil.filesystem_path(file_path)

    if scene.pbrtv3_engine.allow_file_embed():
        paramset.add_string(parameter_name, file_basename)
        encoded_data, encoded_size = bencode_file2string_with_size(file_relative)
        paramset.increase_size('%s_data' % parameter_name, encoded_size)
        paramset.add_string('%s_data' % parameter_name, encoded_data.splitlines())
    else:
        paramset.add_string(parameter_name, file_relative)


def get_output_filename(scene):
    return '%s.%s.%05d' % (efutil.scene_filename(), bpy.path.clean_name(scene.name), scene.frame_current)
