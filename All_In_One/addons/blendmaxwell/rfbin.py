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
import re
import struct
import shutil
import string
import time
import datetime
import math

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, FloatProperty, BoolProperty
from mathutils import Matrix, Vector

from .log import log, LogStyles


class RFBinWriter():
    """RealFlow particle .bin writer"""
    def __init__(self, directory, name, frame, particles, fps=24, size=0.001, log_indent=0, ):
        """
        directory   string (path)
        name        string ascii
        frame       int >= 0
        particles   list of (id int, x float, y float, z float, normal x float, normal y float, normal z float, velocity x float, velocity y float, velocity z float, radius float)
        fps         int > 0
        size        float > 0
        """
        cn = self.__class__.__name__
        self.log_indent = log_indent
        log("{}:".format(cn), 0 + self.log_indent, LogStyles.MESSAGE)
        
        if(not os.path.exists(directory)):
            raise OSError("{}: did you point me to an imaginary directory? ({})".format(cn, directory))
        if(not os.path.isdir(directory)):
            raise OSError("{}: not a directory. ({})".format(cn, directory))
        if(not os.access(directory, os.W_OK)):
            raise OSError("{}: no write access. ({})".format(cn, directory))
        self.directory = directory
        
        if(name == ""):
            raise ValueError("{}: name is an empty string".format(cn))
        ch = "-_.() {0}{1}".format(string.ascii_letters, string.digits)
        valid = "".join(c for c in name if c in ch)
        if(name != valid):
            log("invalid name.. changed to {0}".format(valid), 1 + self.log_indent, LogStyles.WARNING)
        self.name = valid
        
        if(int(frame) < 0):
            raise ValueError("{}: frame is less than zero".format(cn))
        self.frame = int(frame)
        
        self.extension = ".bin"
        self.path = os.path.join(self.directory, "{0}-{1}{2}".format(self.name, str(self.frame).zfill(5), self.extension))
        
        particle_length = 11 + 3
        if(all(len(v) == particle_length for v in particles) is False):
            raise ValueError("{}: bad particle data.".format(cn))
        self.particles = particles
        
        if(int(fps) < 0):
            raise ValueError("{}: fps is less than zero".format(cn))
        self.fps = int(fps)
        
        if(size <= 0):
            raise ValueError("{}: size is less than/or zero".format(cn))
        self.size = size
        
        self.version = 11
        
        self._write()
    
    def _write(self):
        self._t = time.time()
        p = self.path
        log("writing particles to: {0}".format(p), 1 + self.log_indent, )
        with open("{0}.tmp".format(p), 'wb') as f:
            log("writing header..", 1 + self.log_indent, )
            self._header(f)
            log("writing particles..", 1 + self.log_indent, )
            self._particles(f)
            log("writing appendix..", 1 + self.log_indent, )
            self._appendix(f)
        if(os.path.exists(p)):
            os.remove(p)
        shutil.move("{0}.tmp".format(p), p)
        log("done.", 1 + self.log_indent, )
        _d = datetime.timedelta(seconds=time.time() - self._t)
        log("completed in {0}".format(_d), 1 + self.log_indent, )
    
    def _header(self, f, ):
        p = struct.pack
        fw = f.write
        # magic
        fw(p("=i", 0xFABADA))
        # name, should match with name
        fw(p("=250s", self.name.encode('utf-8')))
        # version, scale, fluid type, simulation time
        fw(p("=hfif", self.version, 1.0, 9, 1.0))
        # frame number
        fw(p("=i", self.frame))
        # fps
        fw(p("=i", self.fps))
        # number of particles
        fw(p("=i", len(self.particles)))
        # particle size
        fw(p("=f", self.size))
        # pressure (max,min,average), speed (max,min,average), temperature (max,min,average)
        fw(p("=9f", 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
        # emitter_position (x,y,z), emitter_rotation (x,y,z), emitter_scale (x,y,z)
        fw(p("=9f", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0))
    
    def _particles(self, f, ):
        p = struct.pack
        fw = f.write
        for v in self.particles:
            # 3 position
            fw(p("=3f", *v[1:4]))
            # 3 velocity
            fw(p("=3f", *v[7:10]))
            # 3 force, 3 vorticity
            fw(p("=ffffff", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
            # 3 normal
            fw(p("=3f", *v[4:7]))
            # neighbors
            fw(p("=i", 0, ))
            # 3 texture
            fw(p("=fff", *v[11:14]))
            # infobits, age, isolationtime, viscosity, density, pressure, mass, temperature
            fw(p("=hfffffff", 7, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
            # id
            fw(p("=i", v[0]))
    
    def _appendix(self, f, ):
        p = struct.pack
        fw = f.write
        # number of additional data per particle
        fw(p("=i", 1))
        # id of the data
        fw(p("=i", 2))
        # type of the data
        fw(p("=i", 4))
        # size of the data
        fw(p("=i", 4))
        # owner of the particle id
        fw(p("=i", 0))
        
        for v in self.particles:
            # additional data?
            fw(p("=?", True))
            # additional data
            fw(p("=f", v[10]))
        
        # RF4 internal data
        fw(p("=?", False))
        # RF5 internal data
        fw(p("=?", False))


class ExportRFBin(Operator, ExportHelper):
    bl_idname = "maxwell_render.export_bin"
    bl_label = 'Realflow Particles (.bin)'
    bl_description = 'Realflow Particles (.bin)'
    
    def _proper_bin_name_with_full_path(self, context, name, filepath):
        e = "bin"
        d, f = os.path.split(filepath)
        fnm, fext = os.path.splitext(f)
        if(fext != e):
            fnm = "{0}.{1}".format(fnm, fext)
            fext = ""
        if(fext == ""):
            fext = e
        if(name == ""):
            name = context.active_object.name
        cf = context.scene.frame_current
        binnm = "{0}-{1}.{2}".format(name, str(cf).zfill(5), e)
        path = os.path.join(d, binnm)
        return path
    
    def _filepath_update(self, context):
        d, n = os.path.split(self.filepath)
        p = re.compile('^.+-[0-9]{5}.bin$')
        if(not re.fullmatch(p, n)):
            n = os.path.splitext(os.path.split(self.filepath)[1])[0]
            self.filepath = ExportRFBin._proper_bin_name_with_full_path(self, context, n, self.filepath)
    
    # maxlen 1024 - len('-00000.bin'): '-00000.bin' filename frame number suffix and extension
    filepath = StringProperty(name="File Path", description="", maxlen=1024 - len('-00000.bin'), subtype='FILE_PATH', update=_filepath_update, )
    filename_ext = ".bin"
    check_extension = True
    filter_glob = StringProperty(default="*.bin", options={'HIDDEN'}, )
    
    use_velocity = BoolProperty(name="Particle Velocity", default=False, )
    use_size = BoolProperty(name="Size Per Particle", default=False, )
    size = FloatProperty(name="Size", default=0.1, min=0.000001, max=1000000.0, step=3, precision=6, )
    use_uv = BoolProperty(name="Particle UV", default=False, )
    uv_layer = StringProperty(name="UV Layer", default="", )
    
    @classmethod
    def poll(cls, context):
        o = context.active_object
        if(o is not None):
            # there is active object
            if(len(o.particle_systems) > 0):
                # has particle systems
                if(o.particle_systems.active.settings.type == 'EMITTER'):
                    # and is emitter (not hair)
                    return True
        return False
    
    def invoke(self, context, event):
        p = context.blend_data.filepath
        d = os.path.split(p)[0]
        self.filepath = self._proper_bin_name_with_full_path(context, "", d)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        l = self.layout
        
        c = l.column()
        c.prop(self, 'use_velocity')
        c.prop(self, 'use_size')
        c.prop(self, 'size')
        
        c = l.column()
        c.prop(self, 'use_uv')
        o = context.active_object
        r = c.row()
        r.prop_search(self, 'uv_layer', o.data, 'uv_textures', )
        if(len(o.data.uv_textures) == 0):
            c.enabled = False
        if(not self.use_uv):
            r.enabled = False
    
    def execute(self, context):
        log('Export Realflow Particles (.bin)', 0, LogStyles.MESSAGE, )
        log('use_velocity: {}, use_size: {}, size: {}, use_uv: {}, uv_layer: "{}"'.format(self.use_velocity, self.use_size, self.size, self.use_uv, self.uv_layer, ), 1, )
        
        o = context.active_object
        ps = o.particle_systems.active
        pset = ps.settings
        
        # no particles (number of particles set to zero) and no alive particles > kill export
        if(len(ps.particles) == 0):
            log("particle system {} has no particles".format(ps.name), 1, LogStyles.ERROR, )
            self.report({'ERROR'}, "particle system {} has no particles".format(ps.name), )
            return {'CANCELLED'}
        ok = False
        for p in ps.particles:
            if(p.alive_state == "ALIVE"):
                ok = True
                break
        if(not ok):
            log("particle system {} has no 'ALIVE' particles".format(ps.name), 1, LogStyles.ERROR, )
            self.report({'ERROR'}, "particle system {} has no 'ALIVE' particles".format(ps.name), )
            return {'CANCELLED'}
        
        mat = o.matrix_world.copy()
        mat.invert()
        
        locs = []
        vels = []
        sizes = []
        
        # location, velocity and size from alive particles
        for part in ps.particles:
            if(part.alive_state == "ALIVE"):
                l = part.location.copy()
                l = mat * l
                locs.append(l)
                if(self.use_velocity):
                    v = part.velocity.copy()
                    v = mat * v
                    vels.append(v)
                else:
                    vels.append(Vector((0.0, 0.0, 0.0)))
                # size per particle
                if(self.use_size):
                    sizes.append(part.size / 2)
                else:
                    sizes.append(self.size / 2)
        
        # transform
        # TODO: axis conversion is overly complicated, is it?
        ROTATE_X_90 = Matrix.Rotation(math.radians(90.0), 4, 'X')
        rfms = Matrix.Scale(1.0, 4)
        rfms[0][0] = -1.0
        rfmr = Matrix.Rotation(math.radians(-90.0), 4, 'Z')
        rfm = rfms * rfmr * ROTATE_X_90
        mry90 = Matrix.Rotation(math.radians(90.0), 4, 'Y')
        for i, l in enumerate(locs):
            locs[i] = Vector(l * rfm).to_tuple()
        if(self.use_velocity):
            for i, v in enumerate(vels):
                vels[i] = Vector(v * rfm).to_tuple()
        
        # particle uvs
        if(self.uv_layer is not "" and self.use_uv):
            uv_no = 0
            for i, uv in enumerate(o.data.uv_textures):
                if(self.uv_layer == uv.name):
                    uv_no = i
                    break
            
            uv_locs = tuple()
            
            if(len(ps.child_particles) > 0):
                # NOT TO DO: use bvhtree to make uvs for particles, like with hair - no way to get child particles locations = no uvs
                log("child particles uvs are not supported yet..", 1, LogStyles.WARNING, )
                self.report({'WARNING'}, "child particles uvs are not supported yet..")
            else:
                # no child particles, use 'uv_on_emitter'
                nc0 = len(ps.particles)
                nc1 = len(ps.child_particles) - nc0
                uv_no = 0
                for i, uv in enumerate(o.data.uv_textures):
                    if(self.uv_layer == uv.name):
                        uv_no = i
                        break
                mod = None
                for m in o.modifiers:
                    if(m.type == 'PARTICLE_SYSTEM'):
                        if(m.particle_system == ps):
                            mod = m
                            break
                uv_locs = tuple()
                for i, p in enumerate(ps.particles):
                    co = ps.uv_on_emitter(mod, p, particle_no=i, uv_no=uv_no, )
                    # (x, y, 0.0, )
                    t = co.to_tuple() + (0.0, )
                    uv_locs += (t[0], 1.0 - t[1], t[2], )
                if(nc1 != 0):
                    ex = int(nc1 / nc0)
                for i in range(ex):
                    uv_locs += uv_locs
            has_uvs = True
        else:
            uv_locs = [0.0] * (len(ps.particles) * 3)
            if(self.use_uv):
                log("emitter has no UVs or no UV is selected to be used.. UVs will be exported, but set to (0.0, 0.0)", 1, LogStyles.WARNING, )
                self.report({'WARNING'}, "emitter has no UVs or no UV is selected to be used.. UVs will be exported, but set to (0.0, 0.0)")
        
        flip_xy = Matrix(((-1.0, 0.0, 0.0, 0.0), (0.0, -1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)))
        fv = Vector((-1.0, -1.0, 0.0))
        particles = []
        for i, ploc in enumerate(locs):
            # normal from velocity
            pnor = Vector(vels[i])
            pnor.normalize()
            uv = uv_locs[i * 3:(i * 3) + 3]
            uvv = Vector(uv).reflect(fv) * flip_xy
            uvt = (uvv.z, uvv.x, uvv.y, )
            particles.append((i, ) + tuple(ploc[:3]) + pnor.to_tuple() + tuple(vels[i][:3]) + (sizes[i], ) + uvt, )
        
        # and now.. export!
        h, t = os.path.split(self.filepath)
        n, e = os.path.splitext(t)
        # remove frame number automaticaly added in ui
        n = n[:-6]
        
        cf = bpy.context.scene.frame_current
        prms = {'directory': bpy.path.abspath(h),
                'name': "{}".format(n),
                'frame': cf,
                'particles': particles,
                'fps': bpy.context.scene.render.fps,
                # blender's size is in fact diameter, but we need radius..
                'size': 1.0 if self.use_size else self.size / 2,
                'log_indent': 1, }
        rfbw = RFBinWriter(**prms)
        
        log('done.', 1, )
        
        return {'FINISHED'}
    
    def _menu(self, context):
        self.layout.operator(ExportRFBin.bl_idname, text="Realflow Particles (.bin)")
    
    @classmethod
    def register(cls):
        bpy.types.INFO_MT_file_export.append(cls._menu)
    
    @classmethod
    def unregister(cls):
        bpy.types.INFO_MT_file_export.remove(cls._menu)
