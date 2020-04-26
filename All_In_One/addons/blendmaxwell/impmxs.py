# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import math
import shlex
import subprocess
import uuid
import shutil
import struct
import json
import sys
import re

import bpy
from mathutils import Matrix, Vector
from bpy_extras import io_utils
import bmesh

from .log import log, LogStyles
from . import utils
from . import maths
from . import system
from . import rfbin
from . import mxs


class MXSImportMacOSX():
    def __init__(self, mxs_path, emitters, objects, cameras, sun, keep_intermediates=False, ):
        self.TEMPLATE = system.check_for_import_template()
        self.mxs_path = os.path.realpath(mxs_path)
        self.import_emitters = emitters
        self.import_objects = objects
        self.import_cameras = cameras
        self.import_sun = sun
        self.keep_intermediates = keep_intermediates
        self._import()
    
    def _import(self):
        log("{0} {1} {0}".format("-" * 30, self.__class__.__name__), 0, LogStyles.MESSAGE, prefix="", )
        
        self.uuid = uuid.uuid1()
        
        h, t = os.path.split(self.mxs_path)
        n, e = os.path.splitext(t)
        if(bpy.data.filepath == ""):
            p = os.path.join(h, '{}-tmp-import_scene-{}'.format(n, self.uuid))
            self.tmp_dir = utils.tmp_dir(override_path=p)
        else:
            self.tmp_dir = utils.tmp_dir(purpose='import_scene', uid=self.uuid, use_blend_name=True, )
        
        self.scene_data_name = "{0}-{1}.json".format(n, self.uuid)
        self.script_name = "{0}-{1}.py".format(n, self.uuid)
        self.scene_data_path = os.path.join(self.tmp_dir, self.scene_data_name)
        
        log("executing script..", 1, LogStyles.MESSAGE)
        self._pymaxwell()
        log("processing objects..", 1, LogStyles.MESSAGE)
        self._process()
        log("cleanup..", 1, LogStyles.MESSAGE)
        self._cleanup()
        log("done.", 1, LogStyles.MESSAGE)
    
    def _process(self):
        """Loop over all data from pymaxwell and create corresponding blender objects."""
        data = None
        
        if(not os.path.exists(self.scene_data_path)):
            raise RuntimeError("Protected MXS?")
        
        with open(self.scene_data_path, 'r') as f:
            data = json.load(f)
        
        for d in data:
            t = None
            try:
                t = d['type']
            except KeyError:
                log("element without type: {0}".format(d), 1, LogStyles.WARNING)
            if(d['type'] == 'EMPTY'):
                o = self._empty(d)
                
                if(d['referenced_mxs']):
                    o.maxwell_render.reference.enabled = True
                    o.maxwell_render.reference.path = d['referenced_mxs_path']
                
                d['created'] = o
            elif(d['type'] == 'MESH'):
                o = self._mesh(d)
                d['created'] = o
            elif(d['type'] == 'INSTANCE'):
                o = self._instance(d)
                d['created'] = o
            elif(d['type'] == 'CAMERA'):
                o = self._camera(d)
                d['created'] = o
            elif(d['type'] == 'SUN'):
                o = self._sun(d)
                d['created'] = o
            else:
                log("unknown type: {0}".format(t), 1, LogStyles.WARNING)
        
        # log("setting object hierarchy..", 1, LogStyles.MESSAGE)
        # self._hierarchy(data)
        log("setting object transformations..", 1, LogStyles.MESSAGE)
        self._transformations(data)
        log("setting object hierarchy..", 1, LogStyles.MESSAGE)
        self._hierarchy(data)
        log("finalizing..", 1, LogStyles.MESSAGE)
        self._finalize()
    
    def _empty(self, d):
        n = d['name']
        log("empty: {0}".format(n), 2)
        o = utils.add_object2(n, None)
        return o
    
    def _mesh(self, d):
        nm = d['name']
        log("mesh: {0}".format(nm), 2)
        
        l = len(d['vertices']) + len(d['triangles'])
        nuv = len(d['trianglesUVW'])
        for i in range(nuv):
            l += len(d['trianglesUVW'][i])
        
        # mesh
        me = bpy.data.meshes.new(nm)
        vs = []
        fs = []
        sf = []
        for v in d['vertices']:
            vs.append(v)
        for t in d['triangles']:
            fs.append((t[0], t[1], t[2]))
            if(t[3] == t[4] == t[5]):
                sf.append(False)
            else:
                sf.append(True)
        
        me.from_pydata(vs, [], fs)
        for i, p in enumerate(me.polygons):
            p.use_smooth = sf[i]
        
        nuv = len(d['trianglesUVW'])
        for i in range(nuv):
            muv = d['trianglesUVW'][i]
            uv = me.uv_textures.new(name="uv{0}".format(i))
            uvloops = me.uv_layers[i]
            for j, p in enumerate(me.polygons):
                li = p.loop_indices
                t = muv[j]
                v0 = (t[0], t[1])
                v1 = (t[3], t[4])
                v2 = (t[6], t[7])
                # no need to loop, maxwell meshes are always(?) triangles
                uvloops.data[li[0]].uv = v0
                uvloops.data[li[1]].uv = v1
                uvloops.data[li[2]].uv = v2
        
        # mr90 = Matrix.Rotation(math.radians(90.0), 4, 'X')
        # me.transform(mr90)
        
        o = utils.add_object2(nm, me)
        
        return o
    
    def _instance(self, d):
        log("instance: {0}".format(d['name']), 2)
        o = None
        io = bpy.data.objects[d['instanced']]
        if(io.type == 'MESH'):
            m = bpy.data.meshes[d['instanced']]
            o = utils.add_object2(d['name'], m)
        elif(io.type == 'EMPTY'):
            o = utils.add_object2(d['name'], None)
            if(d['referenced_mxs']):
                o.maxwell_render.reference.enabled = True
                o.maxwell_render.reference.path = d['referenced_mxs_path']
        return o
    
    def _camera(self, d):
        log("camera: {0}".format(d['name']), 2)
        
        mx_type = d['type']
        mx_name = d['name']
        mx_origin = d['origin']
        mx_focal_point = d['focal_point']
        mx_up = d['up']
        mx_focal_length = d['focal_length']
        mx_sensor_fit = d['sensor_fit']
        mx_film_width = d['film_width']
        mx_film_height = d['film_height']
        mx_xres = d['x_res']
        mx_yres = d['y_res']
        mx_active = d['active']
        mx_zclip = d['zclip']
        mx_zclip_near = d['zclip_near']
        mx_zclip_far = d['zclip_far']
        mx_shift_x = d['shift_x']
        mx_shift_y = d['shift_y']
        
        # convert axes
        cm = io_utils.axis_conversion(from_forward='-Y', to_forward='Z', from_up='Z', to_up='Y')
        cm.to_4x4()
        eye = Vector(mx_origin) * cm
        target = Vector(mx_focal_point) * cm
        up = Vector(mx_up) * cm
        
        cd = bpy.data.cameras.new(mx_name)
        c = bpy.data.objects.new(mx_name, cd)
        bpy.context.scene.objects.link(c)
        
        m = self._matrix_look_at(eye, target, up)
        c.matrix_world = m
        
        # distance
        mx_dof_distance = self._distance(mx_origin, mx_focal_point)
        
        # camera properties
        cd.lens = mx_focal_length
        cd.dof_distance = mx_dof_distance
        cd.sensor_fit = mx_sensor_fit
        cd.sensor_width = mx_film_width
        cd.sensor_height = mx_film_height
        
        cd.clip_start = mx_zclip_near
        cd.clip_end = mx_zclip_far
        cd.shift_x = mx_shift_x / 10.0
        cd.shift_y = mx_shift_y / 10.0
        
        if(mx_active):
            render = bpy.context.scene.render
            render.resolution_x = mx_xres
            render.resolution_y = mx_yres
            render.resolution_percentage = 100
            bpy.context.scene.camera = c
        
        return c
    
    def _sun(self, d):
        n = d['name']
        log("sun: {0}".format(n), 2)
        l = bpy.data.lamps.new(n, 'SUN')
        o = utils.add_object2(n, l)
        v = Vector(d['xyz'])
        mrx90 = Matrix.Rotation(math.radians(90.0), 4, 'X')
        v.rotate(mrx90)
        m = self._matrix_look_at(v, Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0)))
        o.matrix_world = m
        
        # align sun ray (which is 25bu long) end with scene center
        d = 25
        l, r, s = m.decompose()
        n = Vector((0.0, 0.0, 1.0))
        n.rotate(r)
        loc = maths.shift_vert_along_normal(l, n, d - 1)
        o.location = loc
        
        return o
    
    def _hierarchy(self, data):
        """Set parent child relationships in scene."""
        types = ['MESH', 'INSTANCE', 'EMPTY']
        for d in data:
            t = d['type']
            if(t in types):
                # o = self._get_object_by_name(d['name'])
                o = d['created']
                if(d['parent'] is not None):
                    # p = self._get_object_by_name(d['parent'])
                    p = None
                    for q in data:
                        if(q['name'] == d['parent']):
                            p = q['created']
                            break
                    o.parent = p
    
    def _transformations(self, data):
        """Apply transformation to all objects."""
        types = ['MESH', 'INSTANCE', 'EMPTY']
        mrx90 = Matrix.Rotation(math.radians(90.0), 4, 'X')
        mrxneg90 = Matrix.Rotation(math.radians(-90.0), 4, 'X')
        for d in data:
            t = d['type']
            if(t in types):
                o = d['created']
                if(o.type == 'MESH'):
                    if(d['type'] != 'INSTANCE'):
                        o.data.transform(mrx90)
                
                m = self._base_and_pivot_to_matrix(d)
                o.matrix_local = m * mrxneg90
    
    def _distance(self, a, b):
        ax, ay, az = a
        bx, by, bz = b
        return ((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2) ** 0.5
    
    def _base_and_pivot_to_matrix(self, d):
        '''
        am = io_utils.axis_conversion(from_forward='-Z', from_up='Y', to_forward='Y', to_up='Z', ).to_4x4()
        b = d['base']
        o = b[0]
        x = b[1]
        y = b[2]
        z = b[3]
        bm = Matrix([(x[0], y[0], z[0], o[0]), (x[1], y[1], z[1], o[1]), (x[2], y[2], z[2], o[2]), (0.0, 0.0, 0.0, 1.0)])
        p = d['pivot']
        o = p[0]
        x = p[1]
        y = p[2]
        z = p[3]
        pm = Matrix([(x[0], y[0], z[0], o[0]), (x[1], y[1], z[1], o[1]), (x[2], y[2], z[2], o[2]), (0.0, 0.0, 0.0, 1.0)])
        mat = am * bm * pm
        obj.matrix_world = mat
        '''
        am = io_utils.axis_conversion(from_forward='-Z', from_up='Y', to_forward='Y', to_up='Z', ).to_4x4()
        
        def cbase_to_matrix4(cbase):
            o = cbase[0]
            x = cbase[1]
            y = cbase[2]
            z = cbase[3]
            m = Matrix([(x[0], y[0], z[0], o[0]),
                        (x[1], y[1], z[1], o[1]),
                        (x[2], y[2], z[2], o[2]),
                        (0.0, 0.0, 0.0, 1.0)])
            return m
        
        bm = cbase_to_matrix4(d['base'])
        pm = cbase_to_matrix4(d['pivot'])
        m = am * bm * pm
        return m
    
    def _matrix_look_at(self, eye, target, up):
        # https://github.com/mono/opentk/blob/master/Source/OpenTK/Math/Matrix4.cs
        
        z = eye - target
        x = up.cross(z)
        y = z.cross(x)
        
        x.normalize()
        y.normalize()
        z.normalize()
        
        rot = Matrix()
        rot[0][0] = x[0]
        rot[0][1] = y[0]
        rot[0][2] = z[0]
        rot[0][3] = 0
        rot[1][0] = x[1]
        rot[1][1] = y[1]
        rot[1][2] = z[1]
        rot[1][3] = 0
        rot[2][0] = x[2]
        rot[2][1] = y[2]
        rot[2][2] = z[2]
        rot[2][3] = 0
        
        # eye not need to be minus cmp to opentk
        # perhaps opentk has z inverse axis
        tran = Matrix.Translation(eye)
        return tran * rot
    
    def _pymaxwell(self):
        # generate script
        self.script_path = os.path.join(self.tmp_dir, self.script_name)
        with open(self.script_path, mode='w', encoding='utf-8') as f:
            # read template
            with open(self.TEMPLATE, encoding='utf-8') as t:
                code = "".join(t.readlines())
            # write template to a new file
            f.write(code)
        
        if(system.PLATFORM == 'Darwin'):
            system.python34_run_script_helper_import(self.script_path, self.mxs_path, self.scene_data_path, self.import_emitters, self.import_objects, self.import_cameras, self.import_sun, )
        elif(system.PLATFORM == 'Linux'):
            pass
        elif(system.PLATFORM == 'Windows'):
            pass
        else:
            pass
    
    def _finalize(self):
        # maybe i am just setting normals badly? how to find out?
        
        # remove strange smooth shading >> cycle edit mode on all meshes..
        # i have no idea why this happens, never happended before, but this seems to fix that.
        cycled_meshes = []
        for o in bpy.data.objects:
            if(o.type == 'MESH'):
                # skip instances, apply only on first mesh multiuser encountered..
                if(o.data in cycled_meshes):
                    pass
                else:
                    bpy.ops.object.select_all(action='DESELECT')
                    o.select = True
                    bpy.context.scene.objects.active = o
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    cycled_meshes.append(o.data)
    
    def _cleanup(self):
        if(self.keep_intermediates):
            return
        
        # remove script, data, temp directory
        def rm(p):
            if(os.path.exists(p)):
                os.remove(p)
            else:
                log("_cleanup(): {} does not exist?".format(p), 1, LogStyles.WARNING, )
        
        rm(self.script_path)
        rm(self.scene_data_path)
        
        if(os.path.exists(self.tmp_dir)):
            os.rmdir(self.tmp_dir)
        else:
            log("_cleanup(): {} does not exist?".format(self.tmp_dir), 1, LogStyles.WARNING, )


class MXSImportWinLin():
    def __init__(self, mxs_path, emitters=True, objects=True, cameras=True, sun=True, ):
        self.mxs_path = os.path.realpath(mxs_path)
        self.import_emitters = emitters
        self.import_objects = objects
        if(self.import_objects):
            self.import_emitters = False
        self.import_cameras = cameras
        self.import_sun = sun
        self._import()
    
    def _import(self):
        log("{0} {1} {0}".format("-" * 30, self.__class__.__name__), 0, LogStyles.MESSAGE, prefix="", )
        reader = mxs.MXSReader(self.mxs_path)
        
        if(self.import_objects or self.import_emitters):
            data = reader.objects(self.import_emitters)
            for d in data:
                t = None
                try:
                    t = d['type']
                except KeyError:
                    log("element without type: {0}".format(d), 1, LogStyles.WARNING)
                if(t is None):
                    continue
                if(t == 'EMPTY'):
                    o = self._empty(d)
                    
                    if(d['referenced_mxs']):
                        o.maxwell_render.reference.enabled = True
                        o.maxwell_render.reference.path = d['referenced_mxs_path']
                    
                    d['created'] = o
                elif(t == 'MESH'):
                    o = self._mesh(d)
                    d['created'] = o
                elif(t == 'INSTANCE'):
                    o = self._instance(d)
                    d['created'] = o
                else:
                    log("unknown type: {0}".format(t), 1, LogStyles.WARNING)
            
            log("setting object hierarchy..", 1, LogStyles.MESSAGE)
            self._hierarchy(data)
            log("setting object transformations..", 1, LogStyles.MESSAGE)
            self._transformations(data)
            log("finalizing..", 1, LogStyles.MESSAGE)
            self._finalize()
        
        if(self.import_cameras):
            data = reader.cameras()
            for d in data:
                t = None
                try:
                    t = d['type']
                except KeyError:
                    log("element without type: {0}".format(d), 1, LogStyles.WARNING)
                if(t is None):
                    continue
                if(t == 'CAMERA'):
                    o = self._camera(d)
                else:
                    log("unknown type: {0}".format(t), 1, LogStyles.WARNING)
        
        if(self.import_sun):
            data = reader.sun()
            for d in data:
                t = None
                try:
                    t = d['type']
                except KeyError:
                    log("element without type: {0}".format(d), 1, LogStyles.WARNING)
                if(t is None):
                    continue
                if(t == 'SUN'):
                    o = self._sun(d)
                else:
                    log("unknown type: {0}".format(t), 1, LogStyles.WARNING)
        
        log("done.", 1)
    
    def _empty(self, d):
        n = d['name']
        log("empty: {0}".format(n), 2)
        o = utils.add_object2(n, None)
        return o
    
    def _mesh(self, d):
        nm = d['name']
        log("mesh: {0}".format(nm), 2)
        
        l = len(d['vertices']) + len(d['triangles'])
        nuv = len(d['trianglesUVW'])
        for i in range(nuv):
            l += len(d['trianglesUVW'][i])
        
        me = bpy.data.meshes.new(nm)
        vs = []
        fs = []
        sf = []
        for v in d['vertices']:
            vs.append(v)
        for t in d['triangles']:
            fs.append((t[0], t[1], t[2]))
            if(t[3] == t[4] == t[5]):
                sf.append(False)
            else:
                sf.append(True)
        
        me.from_pydata(vs, [], fs)
        for i, p in enumerate(me.polygons):
            p.use_smooth = sf[i]
        
        nuv = len(d['trianglesUVW'])
        for i in range(nuv):
            muv = d['trianglesUVW'][i]
            uv = me.uv_textures.new(name="uv{0}".format(i))
            uvloops = me.uv_layers[i]
            for j, p in enumerate(me.polygons):
                li = p.loop_indices
                t = muv[j]
                v0 = (t[0], t[1])
                v1 = (t[3], t[4])
                v2 = (t[6], t[7])
                # no need to loop, maxwell meshes are always(?) triangles
                uvloops.data[li[0]].uv = v0
                uvloops.data[li[1]].uv = v1
                uvloops.data[li[2]].uv = v2
        
        o = utils.add_object2(nm, me)
        return o
    
    def _instance(self, d):
        log("instance: {0}".format(d['name']), 2)
        o = None
        io = bpy.data.objects[d['instanced']]
        if(io.type == 'MESH'):
            m = bpy.data.meshes[d['instanced']]
            o = utils.add_object2(d['name'], m)
        elif(io.type == 'EMPTY'):
            o = utils.add_object2(d['name'], None)
            if(d['referenced_mxs']):
                o.maxwell_render.reference.enabled = True
                o.maxwell_render.reference.path = d['referenced_mxs_path']
        return o
    
    def _camera(self, d):
        log("camera: {0}".format(d['name']), 2)
        
        mx_type = d['type']
        mx_name = d['name']
        mx_origin = d['origin']
        mx_focal_point = d['focal_point']
        mx_up = d['up']
        mx_focal_length = d['focal_length']
        mx_sensor_fit = d['sensor_fit']
        mx_film_width = d['film_width']
        mx_film_height = d['film_height']
        mx_xres = d['x_res']
        mx_yres = d['y_res']
        mx_active = d['active']
        mx_zclip = d['zclip']
        mx_zclip_near = d['zclip_near']
        mx_zclip_far = d['zclip_far']
        mx_shift_x = d['shift_x']
        mx_shift_y = d['shift_y']
        
        # convert axes
        cm = io_utils.axis_conversion(from_forward='-Y', to_forward='Z', from_up='Z', to_up='Y')
        cm.to_4x4()
        eye = Vector(mx_origin) * cm
        target = Vector(mx_focal_point) * cm
        up = Vector(mx_up) * cm
        
        cd = bpy.data.cameras.new(mx_name)
        c = bpy.data.objects.new(mx_name, cd)
        bpy.context.scene.objects.link(c)
        
        m = self._matrix_look_at(eye, target, up)
        c.matrix_world = m
        
        # distance
        mx_dof_distance = self._distance(mx_origin, mx_focal_point)
        
        # camera properties
        cd.lens = mx_focal_length
        cd.dof_distance = mx_dof_distance
        cd.sensor_fit = mx_sensor_fit
        cd.sensor_width = mx_film_width
        cd.sensor_height = mx_film_height
        
        cd.clip_start = mx_zclip_near
        cd.clip_end = mx_zclip_far
        cd.shift_x = mx_shift_x / 10.0
        cd.shift_y = mx_shift_y / 10.0
        
        if(mx_active):
            render = bpy.context.scene.render
            render.resolution_x = mx_xres
            render.resolution_y = mx_yres
            render.resolution_percentage = 100
            bpy.context.scene.camera = c
        
        return c
    
    def _sun(self, d):
        n = d['name']
        log("sun: {0}".format(n), 2)
        l = bpy.data.lamps.new(n, 'SUN')
        o = utils.add_object2(n, l)
        v = Vector(d['xyz'])
        mrx90 = Matrix.Rotation(math.radians(90.0), 4, 'X')
        v.rotate(mrx90)
        m = self._matrix_look_at(v, Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0)))
        o.matrix_world = m
        
        # align sun ray (which is 25bu long) end with scene center
        d = 25
        l, r, s = m.decompose()
        n = Vector((0.0, 0.0, 1.0))
        n.rotate(r)
        loc = maths.shift_vert_along_normal(l, n, d - 1)
        o.location = loc
        
        return o
    
    def _hierarchy(self, data):
        types = ['MESH', 'INSTANCE', 'EMPTY']
        for d in data:
            t = d['type']
            if(t in types):
                # o = self._get_object_by_name(d['name'])
                o = d['created']
                if(d['parent'] is not None):
                    # p = self._get_object_by_name(d['parent'])
                    p = None
                    for q in data:
                        if(q['name'] == d['parent']):
                            p = q['created']
                            break
                    o.parent = p
    
    def _transformations(self, data):
        types = ['MESH', 'INSTANCE', 'EMPTY']
        mrx90 = Matrix.Rotation(math.radians(90.0), 4, 'X')
        for d in data:
            t = d['type']
            if(t in types):
                # o = self._get_object_by_name(d['name'])
                o = d['created']
                m = self._base_and_pivot_to_matrix(d)
                if(o.type == 'MESH'):
                    if(d['type'] != 'INSTANCE'):
                        o.data.transform(mrx90)
                o.matrix_local = m
    
    def _distance(self, a, b):
        ax, ay, az = a
        bx, by, bz = b
        return ((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2) ** 0.5
    
    def _base_and_pivot_to_matrix(self, d):
        b = d['base']
        p = d['pivot']
        o, x, y, z = b
        m = Matrix(((x[0], z[0] * -1, y[0], o[0]),
                    (x[2] * -1, z[2], y[2] * -1, o[2] * -1),
                    (x[1], z[1] * -1, y[1], o[1]),
                    (0.0, 0.0, 0.0, 1.0), ))
        return m
    
    def _matrix_look_at(self, eye, target, up):
        # https://github.com/mono/opentk/blob/master/Source/OpenTK/Math/Matrix4.cs
        
        z = eye - target
        x = up.cross(z)
        y = z.cross(x)
        
        x.normalize()
        y.normalize()
        z.normalize()
        
        rot = Matrix()
        rot[0][0] = x[0]
        rot[0][1] = y[0]
        rot[0][2] = z[0]
        rot[0][3] = 0
        rot[1][0] = x[1]
        rot[1][1] = y[1]
        rot[1][2] = z[1]
        rot[1][3] = 0
        rot[2][0] = x[2]
        rot[2][1] = y[2]
        rot[2][2] = z[2]
        rot[2][3] = 0
        
        # eye not need to be minus cmp to opentk
        # perhaps opentk has z inverse axis
        tran = Matrix.Translation(eye)
        return tran * rot
    
    def _finalize(self):
        # maybe i am just setting normals badly? how to find out?
        
        # remove strange smooth shading >> cycle edit mode on all meshes..
        # i have no idea why this happens, never happended before, but this seems to fix that.
        cycled_meshes = []
        for o in bpy.data.objects:
            if(o.type == 'MESH'):
                # skip instances, apply only on first mesh multiuser encountered..
                if(o.data in cycled_meshes):
                    pass
                else:
                    bpy.ops.object.select_all(action='DESELECT')
                    o.select = True
                    bpy.context.scene.objects.active = o
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    cycled_meshes.append(o.data)


class MXMImportMacOSX():
    def __init__(self, mxm_path, ):
        self.TEMPLATE = system.check_for_import_mxm_template()
        self.mxm_path = os.path.realpath(mxm_path)
        self._import()
    
    def _import(self):
        log("{0} {1} {0}".format("-" * 30, self.__class__.__name__), 0, LogStyles.MESSAGE, prefix="", )
        
        self.uuid = uuid.uuid1()
        
        h, t = os.path.split(self.mxm_path)
        n, e = os.path.splitext(t)
        if(bpy.data.filepath == ""):
            p = os.path.join(h, '{}-tmp-import_material-{}'.format(n, self.uuid))
            self.tmp_dir = utils.tmp_dir(override_path=p)
        else:
            self.tmp_dir = utils.tmp_dir(purpose='import_material', uid=self.uuid, use_blend_name=False, custom_name=n, )
        
        self.data_name = "{0}-{1}.json".format(n, self.uuid)
        self.script_name = "{0}-{1}.py".format(n, self.uuid)
        self.data_path = os.path.join(self.tmp_dir, self.data_name)
        
        log("executing script..", 1, LogStyles.MESSAGE)
        self._pymaxwell()
        log("processing objects..", 1, LogStyles.MESSAGE)
        self._process()
        log("cleanup..", 1, LogStyles.MESSAGE)
        self._cleanup()
        log("done.", 1, LogStyles.MESSAGE)
    
    def _pymaxwell(self):
        # generate script
        self.script_path = os.path.join(self.tmp_dir, self.script_name)
        with open(self.script_path, mode='w', encoding='utf-8') as f:
            # read template
            with open(self.TEMPLATE, encoding='utf-8') as t:
                code = "".join(t.readlines())
            # write template to a new file
            f.write(code)
        
        if(system.PLATFORM == 'Darwin'):
            system.python34_run_script_helper_import_mxm(self.script_path, self.mxm_path, self.data_path, )
        elif(system.PLATFORM == 'Linux'):
            pass
        elif(system.PLATFORM == 'Windows'):
            pass
        else:
            pass
    
    def _process(self):
        data = None
        
        if(not os.path.exists(self.data_path)):
            raise RuntimeError("Protected MXS?")
        
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        self.data = data
    
    def _cleanup(self):
        def rm(p):
            if(os.path.exists(p)):
                os.remove(p)
            else:
                log("_cleanup(): {} does not exist?".format(p), 1, LogStyles.WARNING, )
        
        rm(self.script_path)
        rm(self.data_path)
        
        if(os.path.exists(self.tmp_dir)):
            os.rmdir(self.tmp_dir)
        else:
            log("_cleanup(): {} does not exist?".format(self.tmp_dir), 1, LogStyles.WARNING, )


class MXMImportWinLin():
    def __init__(self, mxm_path, ):
        log("{0} {1} {0}".format("-" * 30, self.__class__.__name__), 0, LogStyles.MESSAGE, prefix="", )
        log("path: {}".format(mxm_path), 1, LogStyles.MESSAGE)
        r = mxs.MXMReader(mxm_path)
        self.data = r.data
