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
import time
import datetime
import math
import uuid
import shutil
import threading
import traceback
import shlex
import subprocess

import bpy
from bpy.types import RenderEngine
from mathutils import Matrix, Vector
import bgl

import numpy as np

from .log import log, LogStyles, LOG_FILE_PATH, copy_paste_log
from . import export
from . import ops
from . import system
from . import mxs
from . import maths
from . import utils


class ViewportRenderManager():
    __threads = []
    
    @classmethod
    def register(cls, rt, tmp_dir, ):
        cls.__threads.append((rt, tmp_dir))
    
    @classmethod
    def killall(cls):
        for rt, tmp_dir in cls.__threads:
            rt.stop()
            cls._cleanup(tmp_dir)
            
    @classmethod
    def _cleanup(cls, tmp_dir):
        if(not os.path.exists(tmp_dir)):
            return
        
        log("cleanup..", 1)
        
        def rm(p, warn_if_missing=True, ):
            if(os.path.exists(p)):
                os.remove(p)
            else:
                if(warn_if_missing):
                    log("cleanup: {} does not exist?".format(p), 1, LogStyles.WARNING, )
        
        rm(os.path.join(tmp_dir, 'scene.mxs'), True, )
        rm(os.path.join(tmp_dir, 'render.exr'), True, )
        rm(os.path.join(tmp_dir, 'render.mxi'), False, )
        if(system.PLATFORM == 'Darwin'):
            rm(os.path.join(tmp_dir, 'scene.py'))
            rm(os.path.join(tmp_dir, 'preview.npy'), False, )
            rm(os.path.join(tmp_dir, 'preview.py'), False, )
        
        if(os.path.exists(tmp_dir)):
            try:
                os.rmdir(tmp_dir)
            except OSError as e:
                log(e, 0, LogStyles.WARNING)
                # use a bit more force..
                log("removing whole directory tree", 0, LogStyles.ERROR)
                shutil.rmtree(tmp_dir)
        else:
            log("cleanup: {} does not exist?".format(tmp_dir), 1, LogStyles.WARNING, )


class ViewportRenderThread(threading.Thread):
    def __init__(self, cmd, tmp_dir):
        ViewportRenderManager.register(self, tmp_dir, )
        self.cmd = cmd
        self.tmp_dir = tmp_dir
        self.p = None
        threading.Thread.__init__(self)
        self._stop = threading.Event()
    
    def stop(self):
        if(self.p is not None):
            if(self.p.poll() is None):
                if(system.PLATFORM == 'Darwin'):
                    self.p.kill()
                elif(system.PLATFORM == 'Linux'):
                    self.p.kill()
                elif(system.PLATFORM == 'Windows'):
                    os.popen('taskkill /pid ' + str(self.p.pid) + ' /f')
                    time.sleep(1)
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()
    
    def run(self):
        self.p = subprocess.Popen(self.cmd, cwd=self.tmp_dir, )
        self.p.communicate()
        self.stop()


class ViewportUpdateThread(threading.Thread):
    def __init__(self, f, rt, t=1.0, ):
        self.f = f
        self.rt = rt
        self.t = t
        threading.Thread.__init__(self)
        self._stop = threading.Event()
    
    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()
    
    def run(self):
        while True:
            if(self.rt.stopped()):
                self.stop()
                # last redraw call
                self.f()
                return
            self.f()
            self._stop.wait(self.t)


class MaxwellRenderExportEngine(RenderEngine):
    bl_idname = 'MAXWELL_RENDER'
    bl_label = 'Maxwell Render'
    bl_use_preview = True
    
    lock = threading.Lock()
    t = None
    uuid = None
    tmp_dir = None
    
    # TODO: this is getting messy, reduce number of fields somehow.. also their names are confusing a bit. this is the first time i had to add comment to them.. what a mess..
    # viewport rendering, will block view_draw
    vr = False
    # absolute temp directory path
    vr_tmp_dir = None
    # render thread
    vr_rt = None
    # update timer thread
    vr_ut = None
    # ORTHO, CAMERA or PERSP, ORTHO is not supported
    vr_view = None
    # x, y for bgl draw
    vr_draw_offset = None
    # width, height for bgl draw
    vr_draw_dimensions = None
    # previous bgl.Buffer to be drawn if something went wrong while reading new render
    vr_previous_buffer = None
    # previous raw array, used for slicing when in CAMERA
    vr_previous_array = None
    # context.space_data
    vr_space_data = None
    # camera 2d screen coordinates [[int x, int y (top right)], [int x, int y (bottom right)], [int x, int y (bottom left)], int [x, int y (top left)], ]
    vr_camera_frame_points_on_screen = None
    # width and height of 3d viewport region
    vr_space_dimensions = None
    
    def _get_preview_material(self, scene):
        materials = {}
        
        def get_instance_materials(o):
            oms = []
            if hasattr(o, 'material_slots'):
                for ms in o.material_slots:
                    oms.append(ms.material)
            if hasattr(o.data, 'materials'):
                for m in o.data.materials:
                    oms.append(m)
            return oms
        
        for ob in [o for o in scene.objects if o.is_visible(scene) and not o.hide_render]:
            for m in get_instance_materials(ob):
                if m is not None:
                    if ob.name not in materials.keys():
                        materials[ob] = []
                    materials[ob].append(m)
        
        preview_obs = [o for o in materials.keys() if o.name.startswith('preview')]
        if len(preview_obs) < 1:
            return None
        
        mats = materials[preview_obs[0]]
        if(len(mats) < 1):
            return None
        
        return mats[0]
    
    def _fill_black(self):
        w = self.resolution_x
        h = self.resolution_y
        a = np.array((0.0, 0.0, 0.0, 1.0) * (w * h))
        a = a.reshape(w * h, 4)
        
        r = self.begin_result(0, 0, w, h)
        l = r.layers[0] if bpy.app.version < (2, 74, 4) else r.layers[0].passes[0]
        l.rect = a
        self.end_result(r)
        self.update_result(r)
    
    def _fill_grid(self):
        w = self.resolution_x
        h = self.resolution_y
        bg_col = (48 / 256, 48 / 256, 48 / 256, 1.0)
        grid_col = (64 / 256, 64 / 256, 64 / 256, 1.0)
        
        pixels = np.array([bg_col] * (w * h))
        pixels = np.reshape(pixels, (h, w, 4))
        for i in range(0, w, 8):
            pixels[:, i] = grid_col
        for i in range(0, h, 8):
            pixels[i] = grid_col
        
        def g(c):
            r = []
            for i, v in enumerate(c):
                if(v <= 0.03928):
                    r.append(v / 12.92)
                else:
                    r.append(math.pow((v + 0.055) / 1.055, 2.4))
            return r
        
        a1 = np.reshape(pixels, (-1, 4))
        a2 = []
        for c in a1:
            a2.append(g(c[:3]) + [1.0, ])
        
        a = a2
        r = self.begin_result(0, 0, w, h)
        l = r.layers[0] if bpy.app.version < (2, 74, 4) else r.layers[0].passes[0]
        l.rect = a
        self.end_result(r)
        self.update_result(r)
    
    def _draw_array(self, a, mxi_buffer=True, ):
        rw = self.resolution_x
        rh = self.resolution_y
        
        a.astype(float)
        
        # NOTE: fix the need of swapping of w/h and rw/rh..
        # swap w with h and rw with rh, after padding and slicing put it back as it was.. now i am too lazy to rewrite it..
        # w, h, _ = a.shape
        
        # ehm, swap it..
        h, w, _ = a.shape
        _ = rw
        rw = rh
        rh = _
        
        pw = int((rw - w) / 2)
        ph = int((rh - h) / 2)
        
        # pad values
        if(pw < 0):
            # use absolute value or modulo will not work as expected
            # and when result should be sliced, set it back to negative
            pw2 = -(abs(int((rw - w) / 2)) + ((rw - w) % 2))
        else:
            pw2 = abs(int((rw - w) / 2)) + ((rw - w) % 2)
        if(ph < 0):
            ph2 = -(abs(int((rh - h) / 2)) + ((rh - h) % 2))
        else:
            ph2 = abs(int((rh - h) / 2)) + ((rh - h) % 2)
        
        # slice values
        sw, sw2 = 0, 0
        if(pw <= 0 or pw2 <= 0):
            # padding can't be used with negative values, so zero it and set slicing instead
            sw, sw2 = pw, pw2
            pw, pw2 = 0, 0
        sh, sh2 = 0, 0
        if(ph <= 0 or ph2 <= 0):
            sh, sh2 = ph, ph2
            ph, ph2 = 0, 0
        
        # pad
        a = np.pad(a, [(pw, pw2), (ph, ph2), (0, 0)], mode='constant', constant_values=[0.0], )
        
        # slice
        if(sw != 0 and sw2 == 0):
            a = a[-sw:, :, :, ]
        elif(sw == 0 and sw2 != 0):
            a = a[:sw2, :, :, ]
        elif(sw != 0 and sw2 != 0):
            a = a[-sw:sw2, :, :, ]
        if(sh != 0 and sh2 == 0):
            a = a[:, -sh:, :, ]
        elif(sh == 0 and sh2 != 0):
            a = a[:, :sh2, :, ]
        elif(sh != 0 and sh2 != 0):
            a = a[:, -sh:sh2, :, ]
        
        # ehm, and swap it back again..
        w, h, _ = a.shape
        _ = rw
        rw = rh
        rh = _
        
        if(not mxi_buffer):
            # from 8bit to 32bit colors (mxm previews are stored in 8bit colors and gamma corrected)
            a = a[:] / 255
            # gamma uncorrect
            g = 2.2
            a = a[:] ** g
        
        # add alpha
        w, h, _ = a.shape
        b = np.ones((w, h, 1), dtype=np.float, )
        a = np.append(a, b, axis=2, )
        
        # flip
        a = np.flipud(a)
        
        # flatten
        a = np.reshape(a, (w * h, 4))
        
        try:
            r = self.begin_result(0, 0, rw, rh)
            l = r.layers[0] if bpy.app.version < (2, 74, 4) else r.layers[0].passes[0]
            l.rect = a
            self.end_result(r)
            self.update_result(r)
        except Exception as e:
            log(traceback.format_exc(), 0, LogStyles.ERROR)
            return False
        
        return True
    
    def _read_mxm_preview(self, mat, ):
        log("read mxm preview..", 1)
        
        m = mat.maxwell_render
        p = m.mxm_file
        if(p is ''):
            return False
        p = os.path.realpath(bpy.path.abspath(p))
        if(not os.path.exists(p)):
            return False
        
        a = None
        if(system.PLATFORM == 'Darwin'):
            system.python34_run_mxm_preview(p)
            d = os.path.join(os.path.split(os.path.realpath(__file__))[0], "support", )
            f = os.path.split(p)[1]
            npy = os.path.join(d, "{}.npy".format(f))
            if(os.path.exists(npy)):
                a = np.load(npy)
            # cleanup
            if(os.path.exists(npy)):
                os.remove(npy)
        else:
            # win / linux
            a = mxs.read_mxm_preview(p)
        
        if(a is not None and np.count_nonzero(a) != 0):
            log("drawing..", 1)
            ok = self._draw_array(a, mxi_buffer=False, )
            if(not ok):
                return False
            
            return True
        
        return False
    
    def _render_mat_preview(self, mat, ):
        log("render preview..", 1)
        
        smx = bpy.context.scene.maxwell_render
        render_sl = smx.material_preview_sl
        render_t = smx.material_preview_time
        render_s = smx.material_preview_scale
        render_q = smx.material_preview_quality
        render_v = smx.material_preview_verbosity
        
        m = mat.maxwell_render
        render_sc = os.path.abspath(m.preview_scene)
        render_sz = int(m.preview_size)
        
        # blend path, temp directory must be saved next to it
        p = bpy.data.filepath
        if(p == ""):
            # if file is not saved, draw warning in ui and skip rendering
            return False
        
        tmp_dir = utils.tmp_dir(purpose='material_preview', uid=self.uuid, use_blend_name=True, )
        self.tmp_dir = tmp_dir
        
        mxm = os.path.join(tmp_dir, "material.mxm")
        
        log("export mxm to: {}".format(mxm), 1, )
        # save mxm to temp directory
        if(m.use == 'CUSTOM'):
            exmat = export.MXSMaterialCustom(mat.name)
            d = exmat._repr()
            system.mxed_create_and_edit_custom_material_helper(mxm, d, False, "", False, )
        elif(m.use == 'REFERENCE'):
            # when referenced mxm has no saved preview inside
            shutil.copyfile(os.path.realpath(bpy.path.abspath(m.mxm_file)), mxm)
        else:
            exmat = export.MXSMaterialExtension(mat.name)
            d = exmat._repr()
            system.mxed_create_and_edit_custom_material_helper(mxm, d, False, "", False, )
        
        log("preview scene: {}".format(render_sc), 1, )
        # copy preview scene mxs to temp directory
        if(not os.path.exists(render_sc)):
            # if missing, fill black and skip rendering
            log("preview scene '{}' is missing..".format(render_sc), 0, LogStyles.ERROR, )
            return False
        
        scene = os.path.join(tmp_dir, "scene.mxs")
        result = os.path.join(tmp_dir, "render.mxi")
        
        # start rendering..
        if(system.PLATFORM == 'Darwin'):
            PY = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().python_path), 'bin', 'python3.5', ))
            PYMAXWELL_PATH = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().maxwell_path), 'Libs', 'pymaxwell', 'python3.5', ))
            TEMPLATE_SCENE = system.check_for_material_preview_scene_template()
            TEMPLATE_MXI = system.check_for_material_preview_mxi_template()
            NUMPY_PATH = os.path.split(os.path.split(np.__file__)[0])[0]
            
            log("make preview scene..", 1, )
            script_path = os.path.join(tmp_dir, "scene.py")
            with open(script_path, mode='w', encoding='utf-8') as f:
                # read template
                with open(TEMPLATE_SCENE, encoding='utf-8') as t:
                    code = "".join(t.readlines())
                # write template to a new file
                f.write(code)
            
            q = shlex.quote
            p = [q(PY), q(script_path), q(PYMAXWELL_PATH), q(LOG_FILE_PATH), q(render_sc), q(tmp_dir), q(render_q), ]
            cmd = "{} {} {} {} {} {} {}".format(*p)
            log("command:", 2)
            log("{0}".format(cmd), 0, LogStyles.MESSAGE, prefix="")
            args = shlex.split(cmd)
            process_scene = subprocess.Popen(args, cwd=tmp_dir, )
            process_scene.wait()
            if(process_scene.returncode != 0):
                return False
            
            log("render preview scene..", 1, )
            app = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().maxwell_path), 'Maxwell.app', ))
            executable = os.path.join(app, "Contents/MacOS/Maxwell")
            
            q = shlex.quote
            p = [q(executable),
                 q(os.path.join(tmp_dir, 'scene.mxs')),
                 q(os.path.join(tmp_dir, 'render.mxi')),
                 q(os.path.join(tmp_dir, 'render.exr')),
                 q(os.path.split(render_sc)[0]),
                 q(str(render_sz)),
                 q(str(render_sz)),
                 q(str(render_t)),
                 q(str(render_sl)),
                 q(str(render_v)), ]
            line = "{} -mxs:{} -mxi:{} -o:{} -dep:{} -res:{}x{} -time:{} -sl:{} -nowait -nogui -hide -verbose:{}".format(*p)
            cmd = shlex.split(line)
            
            abort = False
            process_render = subprocess.Popen(cmd, cwd=tmp_dir, )
            while(process_render.poll() is None):
                if(self.test_break()):
                    try:
                        process_render.kill()
                        abort = True
                        log('aborting..', 1, )
                    except Exception as e:
                        log(traceback.format_exc(), 0, LogStyles.ERROR)
                    break
                
                log('rendering..', 1, )
                time.sleep(1)
            
            if(abort):
                return False
            
            log("read preview render..", 1, )
            script_path = os.path.join(tmp_dir, "preview.py")
            with open(script_path, mode='w', encoding='utf-8') as f:
                # read template
                with open(TEMPLATE_MXI, encoding='utf-8') as t:
                    code = "".join(t.readlines())
                # write template to a new file
                f.write(code)
            
            q = shlex.quote
            p = [q(PY), q(script_path), q(PYMAXWELL_PATH), q(NUMPY_PATH), q(LOG_FILE_PATH), q(tmp_dir), ]
            cmd = "{} {} {} {} {} {}".format(*p)
            log("command:", 2)
            log("{0}".format(cmd), 0, LogStyles.MESSAGE, prefix="")
            args = shlex.split(cmd)
            process_scene = subprocess.Popen(args, cwd=tmp_dir, )
            process_scene.wait()
            if(process_scene.returncode != 0):
                return False
            
            a = None
            npy = os.path.join(tmp_dir, "preview.npy")
            if(os.path.exists(npy)):
                a = np.load(npy)
            if(a is not None):
                if(a.shape == (1, 1, 3)):
                    # there was an error
                    log('preview render failed..', 1, LogStyles.ERROR, )
                    return False
            else:
                log('preview render pixels read failed..', 1, LogStyles.ERROR, )
                return False
            
            log("drawing..", 1)
            self._draw_array(a, mxi_buffer=True, )
            
            return True
        else:
            log("make preview scene..", 1, )
            scene = mxs.material_preview_scene(render_sc, tmp_dir, render_q, )
            
            log("render preview scene..", 1, )
            if(system.PLATFORM == 'Linux'):
                executable = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().maxwell_path), 'maxwell', ))
                
                q = shlex.quote
                p = [q(executable),
                     q(os.path.join(tmp_dir, 'scene.mxs')),
                     q(os.path.join(tmp_dir, 'render.mxi')),
                     q(os.path.join(tmp_dir, 'render.exr')),
                     q(os.path.split(render_sc)[0]),
                     q(str(render_sz)),
                     q(str(render_sz)),
                     q(str(render_t)),
                     q(str(render_sl)),
                     q(str(render_v)), ]
                line = "{} -mxs:{} -mxi:{} -o:{} -dep:{} -res:{}x{} -time:{} -sl:{} -nowait -nogui -hide -verbose:{}".format(*p)
                cmd = shlex.split(line)
                
                abort = False
                process_render = subprocess.Popen(cmd, cwd=tmp_dir, )
                while(process_render.poll() is None):
                    if(self.test_break()):
                        try:
                            process_render.kill()
                            abort = True
                            log('aborting..', 1, )
                        except Exception as e:
                            log(traceback.format_exc(), 0, LogStyles.ERROR)
                        break
                    
                    log('rendering..', 1, )
                    time.sleep(1)
                
                if(abort):
                    return False
                
            elif(system.PLATFORM == 'Windows'):
                executable = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().maxwell_path), 'maxwell.exe', ))
                
                q = shlex.quote
                p = [q(executable),
                     q(os.path.join(tmp_dir, 'scene.mxs')),
                     q(os.path.join(tmp_dir, 'render.mxi')),
                     q(os.path.join(tmp_dir, 'render.exr')),
                     q(os.path.split(render_sc)[0]),
                     q(str(render_sz)),
                     q(str(render_sz)),
                     q(str(render_t)),
                     q(str(render_sl)),
                     q(str(render_v)), ]
                line = "{} -mxs:{} -mxi:{} -o:{} -dep:{} -res:{}x{} -time:{} -sl:{} -nowait -nogui -hide -verbose:{}".format(*p)
                cmd = shlex.split(line)
                
                abort = False
                process_render = subprocess.Popen(cmd, cwd=tmp_dir, )
                while(process_render.poll() is None):
                    if(self.test_break()):
                        try:
                            os.popen('taskkill /pid ' + str(process_render.pid) + ' /f')
                            time.sleep(1)
                            abort = True
                            log('aborting..', 1, )
                        except Exception as e:
                            log(traceback.format_exc(), 0, LogStyles.ERROR)
                        break
                    
                    log('rendering..', 1, )
                    time.sleep(1)
                
                if(abort):
                    return False
                
            else:
                raise OSError("Unknown platform: {}.".format(system.platform))
            
            log("read preview render..", 1, )
            a = mxs.material_preview_mxi(tmp_dir)
            
            if(a is not None):
                if(a.shape == (1, 1, 3)):
                    # there was an error
                    log('preview render failed..', 1, LogStyles.ERROR, )
                    return False
            else:
                log('preview render pixels read failed..', 1, LogStyles.ERROR, )
                return False
            
            log("drawing..", 1)
            self._draw_array(a, mxi_buffer=True, )
            
            return True
        
        return False
    
    def _render_mat_preview_cleanup(self, finished=True, ):
        log("cleanup.. (finished: {})".format(finished), 1)
        if(self.tmp_dir is None):
            return
        tmp_dir = self.tmp_dir
        
        def rm(p, warn_if_missing=True, ):
            if(os.path.exists(p)):
                os.remove(p)
            else:
                if(warn_if_missing):
                    log("cleanup: {} does not exist?".format(p), 1, LogStyles.WARNING, )
        
        rm(os.path.join(tmp_dir, 'material.mxm'))
        rm(os.path.join(tmp_dir, 'render.mxi'), finished, )
        rm(os.path.join(tmp_dir, 'render.exr'), False, )
        rm(os.path.join(tmp_dir, 'scene.mxs'), finished, )
        if(system.PLATFORM == 'Darwin'):
            rm(os.path.join(tmp_dir, 'scene.py'))
            rm(os.path.join(tmp_dir, 'preview.npy'), finished, )
            rm(os.path.join(tmp_dir, 'preview.py'), finished, )
        
        if(os.path.exists(tmp_dir)):
            try:
                os.rmdir(tmp_dir)
            except OSError as e:
                log(e, 0, LogStyles.WARNING)
                # use a bit more force..
                log("removing whole directory tree", 0, LogStyles.ERROR)
                shutil.rmtree(tmp_dir)
        else:
            log("cleanup: {} does not exist?".format(tmp_dir), 1, LogStyles.WARNING, )
        
        self.tmp_dir = None
    
    def _update(self, data, scene, ):
        if(self.is_preview):
            return
        
        self.t = time.time()
        
        m = scene.maxwell_render
        
        bp = bpy.path.abspath(bpy.context.blend_data.filepath)
        # check if file is saved, if not raise error
        if(bp == ""):
            self.report({'ERROR'}, "Save file first.")
            return
        
        # other checks, like for camera (if not present, blender will raise error anyway)
        cams = [o for o in scene.objects if o.type == 'CAMERA']
        if(len(cams) == 0):
            self.report({'ERROR'}, "No Camera found in scene.")
            return
        
        ed = bpy.path.abspath(m.export_output_directory)
        # check if directory exists else error
        if(not os.path.exists(ed)):
            self.report({'ERROR'}, "Export directory does not exist.")
            return
        # check if directory if writeable else error
        if(not os.access(ed, os.W_OK)):
            self.report({'ERROR'}, "Export directory is not writeable.")
            return
        
        # set some workflow stuff..
        if(self.is_animation):
            m.exporting_animation_now = True
        else:
            m.exporting_animation_now = False
        if(scene.frame_start == scene.frame_current):
            m.exporting_animation_first_frame = True
        else:
            m.exporting_animation_first_frame = False
        m.private_image = m.output_image
        m.private_mxi = m.output_mxi
        m.exporting_animation_frame_number = scene.frame_current
        
        h, t = os.path.split(bp)
        n, e = os.path.splitext(t)
        if(m.exporting_animation_now and not m.exporting_animation_first_frame):
            mxs_name = m.private_name
            mxs_increment = m.private_increment
            mxs_suffix = m.private_suffix
        else:
            mxs_name = n
            mxs_increment = ""
            mxs_suffix = ""
        
        def walk_dir(p):
            r = {'files': [], 'dirs': [], }
            for (root, dirs, files) in os.walk(p):
                r['files'].extend(files)
                r['dirs'].extend(dirs)
                break
            return r
        
        if(m.exporting_animation_now):
            mxs_suffix = '_{:06d}'.format(m.exporting_animation_frame_number)
            if(m.export_incremental):
                # add or increment mxs number
                if(m.exporting_animation_first_frame):
                    # do this just once for a first frame
                    m.exporting_animation_first_frame = False
                    
                    dc = walk_dir(ed)
                    # get files from destination and filter all files starting with mxs_name and with .mxs extension
                    older = [f for f in dc['files'] if(f.startswith(mxs_name) and f.endswith(".mxs"))]
                    nn = 0
                    if(len(older) > 0):
                        older.sort()
                        pat = re.compile(str('^{0}.\d\d\d_\d\d\d\d\d\d.mxs$'.format(mxs_name)))
                        for ofn in older:
                            if(re.search(pat, ofn)):
                                # get increment number from each, if there is some of course
                                num = int(ofn[len(mxs_name) + 1:-len("_000000.mxs")])
                                if(nn < num):
                                    nn = num
                        nn += 1
                    if(nn != 0):
                        # there were some already incremented files, lets make nes increment from highest
                        mxs_increment = '.{:0>3}'.format(nn)
            elif(m.export_overwrite):
                # overwrite, no error reporting, no path changing
                pass
            else:
                # check and raise error if mxs exists, if not continue
                p = os.path.join(ed, "{}{}{}.mxs".format(mxs_name, mxs_increment, mxs_suffix))
                if(os.path.exists(p) and not m.export_overwrite):
                    # reset animation flags
                    self._reset_workflow(scene)
                    self.report({'ERROR'}, "Scene file already exist in Output directory.")
                    return
        else:
            if(m.export_incremental):
                # add or increment mxs number
                dc = walk_dir(ed)
                # get files from destination and filter all files starting with mxs_name and with .mxs extension
                older = [f for f in dc['files'] if(f.startswith(mxs_name) and f.endswith(".mxs"))]
                nn = 0
                if(len(older) > 0):
                    older.sort()
                    pat = re.compile(str('^{0}.\d\d\d.mxs$'.format(mxs_name)))
                    for ofn in older:
                        if(re.search(pat, ofn)):
                            # get increment number from each, if there is some of course
                            num = int(ofn[len(mxs_name) + 1:-len(".mxs")])
                            if(nn < num):
                                nn = num
                    nn += 1
                if(nn != 0):
                    # there were some already incremented files, lets make nes increment from highest
                    mxs_increment = '.{:0>3}'.format(nn)
            elif(m.export_overwrite):
                # overwrite, no error reporting, no path changing
                pass
            else:
                # check and raise error if mxs exists, if not continue
                p = os.path.join(ed, "{}{}{}.mxs".format(mxs_name, mxs_increment, mxs_suffix))
                if(os.path.exists(p) and not m.export_overwrite):
                    self._reset_workflow(scene)
                    self.report({'ERROR'}, "Scene file already exist in Output directory.")
                    return
        
        # store it to use it _render_scene (is this needed? it was in example.. i can do whole work here)
        # but the problem is, when exporting animation, this is called for each frame, so i got to store these props
        # maybe.. maybe not
        m.private_name = mxs_name
        m.private_increment = mxs_increment
        m.private_suffix = mxs_suffix
        m.private_path = os.path.join(ed, "{}{}{}.mxs".format(mxs_name, mxs_increment, mxs_suffix))
        m.private_basepath = os.path.join(ed, "{}{}.mxs".format(mxs_name, mxs_increment))
        
        try:
            s = scene.render.resolution_percentage / 100.0
            self.size_x = int(scene.render.resolution_x * s)
            self.size_y = int(scene.render.resolution_y * s)
            if(scene.name == 'preview'):
                pass
            else:
                self._render_scene(scene)
                m.output_image = m.private_image
                m.output_mxi = m.private_mxi
        except Exception as ex:
            import traceback
            m = traceback.format_exc()
            log(m)
            
            # import sys
            # import traceback
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            # log("".join(lines))
            
            self._reset_workflow(scene)
            self.report({'ERROR'}, m)
        
        _d = datetime.timedelta(seconds=time.time() - self.t)
        log("export completed in {0}".format(_d), 1, LogStyles.MESSAGE)
    
    def _render_scene(self, scene):
        m = scene.maxwell_render
        p = m.private_path
        bp = m.private_basepath
        
        # write default one if not set, do not care if enabled, this is more usable when i change my mind later
        h, t = os.path.split(bp)
        n, e = os.path.splitext(t)
        if(m.output_image == ""):
            m.output_image = os.path.join(h, "{}.png".format(n))
            m.private_image = m.output_image
        if(m.output_mxi == ""):
            m.output_mxi = os.path.join(h, "{}.mxi".format(n))
            m.private_mxi = m.output_mxi
        
        def remove_increment(path):
            h, t = os.path.split(bpy.path.abspath(path))
            n, e = os.path.splitext(t)
            pat = re.compile(str('.\d\d\d{}$'.format(e)))
            if(re.search(pat, t)):
                n = t[:-len(".000{}".format(e))]
            return h, n, e
        
        if(m.export_incremental):
            # increment also both image files, and also do not care if enabled
            if(m.private_increment != ""):
                h, n, e = remove_increment(m.output_image)
                m.output_image = os.path.join(h, "{}{}{}".format(n, m.private_increment, e))
                h, n, e = remove_increment(m.output_mxi)
                m.output_mxi = os.path.join(h, "{}{}{}".format(n, m.private_increment, e))
        
        if(m.output_image_enabled):
            # if exporting animation add correct frame number
            if(m.exporting_animation_now):
                # frame number from image paths will be removed after export is finished in animation operator
                h, t = os.path.split(bpy.path.abspath(m.output_image))
                n, e = os.path.splitext(t)
                m.output_image = os.path.join(h, "{}{}{}".format(n, m.private_suffix, e))
        
        if(m.output_mxi_enabled):
            # if exporting animation add correct frame number
            if(m.exporting_animation_now):
                # frame number from image paths will be removed after export is finished in animation operator
                h, t = os.path.split(bpy.path.abspath(m.output_mxi))
                n, e = os.path.splitext(t)
                m.output_mxi = os.path.join(h, "{}{}{}".format(n, m.private_suffix, e))
        
        log_file_path = None
        ex = None
        
        # import cProfile, pstats, io
        # pr = cProfile.Profile()
        # pr.enable()
        
        ex = export.MXSExport(mxs_path=p, engine=self, )
        
        ex.stats.pprint()
        
        from .log import NUMBER_OF_WARNINGS
        if(NUMBER_OF_WARNINGS > 0):
            if(m.export_suppress_warning_popups):
                self.report({'WARNING'}, "There was {} warnings during export. Check log file for details.".format(NUMBER_OF_WARNINGS))
            else:
                self.report({'ERROR'}, "There was {} warnings during export. Check log file for details.".format(NUMBER_OF_WARNINGS))
            log("There was {} warnings during export. Check log file for details.".format(NUMBER_OF_WARNINGS), 1, LogStyles.WARNING, )
            
            if(m.export_warning_log_write):
                h, t = os.path.split(p)
                n, e = os.path.splitext(t)
                u = ex.uuid
                log_file_path = os.path.join(h, '{}-export_log-{}.txt'.format(n, u))
                copy_paste_log(log_file_path)
        
        # pr.disable()
        # s = io.StringIO()
        # sortby = 'cumulative'
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # print(s.getvalue())
        
        if((m.exporting_animation_now and scene.frame_current == scene.frame_end) or not m.exporting_animation_now):
            if(m.export_log_open):
                if(log_file_path is not None):
                    # open local, it gets written only when some warnigns are encountered
                    system.open_file_in_default_application(log_file_path)
                else:
                    # else open global log file from inside addon files
                    system.open_file_in_default_application(LOG_FILE_PATH)
        
        # open in..
        if(ex is not None and not m.exporting_animation_now):
            bpy.ops.maxwell_render.open_mxs(filepath=ex.mxs_path, application=m.export_open_with, instance_app=m.instance_app, )
    
    def _reset_workflow(self, scene):
        m = scene.maxwell_render
        m.exporting_animation_now = False
        m.exporting_animation_frame_number = 1
        m.exporting_animation_first_frame = True
        m.private_name = ""
        m.private_increment = ""
        m.private_suffix = ""
        m.private_path = ""
        m.private_basepath = ""
        m.private_image = ""
        m.private_mxi = ""
    
    def __init__(self):
        self.uuid = uuid.uuid1()
    
    def update(self, data, scene, ):
        if(self.is_preview):
            if(not bpy.context.scene.maxwell_render.material_preview_enable):
                return
            
            mat = self._get_preview_material(scene)
            
            if(mat is not None):
                mx = mat.maxwell_render
                if(not mx.preview_flag):
                    # skip completelly..
                    return
                else:
                    # HACK: force render of large preview when preview_flag is clicked, not just icon..
                    obj = bpy.context.scene.objects.active
                    for i, slot in enumerate(obj.material_slots):
                        if(slot.material.name == mat.name):
                            break
                    slot.material = None
                    slot.material = bpy.data.materials[mat.name]
                    bpy.data.materials[mat.name].maxwell_render.preview_flag = False
            
            log("material preview (update): '{}'".format(mat.name), 0, )
            
            if(self.resolution_x <= 96):
                # skip icon rendering..
                log("skipping icon render..", 1, )
            else:
                # this is never called? material preview update with large resolution?
                log("RenderEngine.update() unexpected call..", 1, LogStyles.WARNING)
        else:
            self._update(data, scene)
    
    def render(self, scene, ):
        with self.lock:
            abort = False
            
            if(self.is_preview):
                if(not bpy.context.scene.maxwell_render.material_preview_enable):
                    return
                
                mat = self._get_preview_material(scene)
                
                if(self.resolution_x <= 96):
                    # skip icon rendering..
                    pass
                else:
                    log("material preview (render): '{}'".format(mat.name), 0, )
                    
                    # fill with grid to indicate rendering..
                    self._fill_grid()
                    
                    mx = mat.maxwell_render
                    smx = bpy.context.scene.maxwell_render
                    
                    ref = False
                    ok = False
                    try:
                        if(smx.material_preview_external and mx.use == 'REFERENCE'):
                            ok = self._read_mxm_preview(mat)
                            ref = True
                            if(not ok):
                                log("failed to get mxm preview..", 1)
                                ok = self._render_mat_preview(mat)
                                ref = False
                        else:
                            # always render new material preview
                            ok = self._render_mat_preview(mat)
                    except Exception as e:
                        # log(traceback.format_exc())
                        log(traceback.format_exc(), 0, LogStyles.ERROR, )
                        ok = False
                        # self.report({'ERROR'}, '{}'.format(e))
                    
                    if(not ref):
                        # cleanup after loading preview from referenced material is done somewhere else. and on windows/linux is not even needed
                        self._render_mat_preview_cleanup(ok)
                    
                    if(not ok):
                        self._fill_grid()
                    
                    log("done.", 1)
            else:
                # no direct rendering, better to use maxwell itself..
                pass
                
                # process = subprocess.Popen(shlex.split('sleep 10'))
                # while(process.poll() is None):
                #     if(self.test_break()):
                #         try:
                #             process.terminate()
                #             abort = True
                #             log('aborting..', 1, )
                #         except Exception as e:
                #             log(traceback.format_exc(), 0, LogStyles.ERROR)
                #         break
                #     log('rendering..', 1, )
                #     time.sleep(1)
    
    def __del__(self):
        # if(self.vr_ut is not None):
        #     self.vr_ut.stop()
        # if(self.vr_rt is not None):
        #     self.vr_rt.stop()
        pass
    
    def _vr_render_start(self):
        self.update_stats("Starting render..", "")
        
        m = bpy.context.scene.maxwell_render
        vr_sl = m.viewport_render_sl
        vr_time = m.viewport_render_time
        vr_quality = m.viewport_render_quality
        vr_verbosity = m.viewport_render_verbosity
        
        scene_path = os.path.join(self.vr_tmp_dir, 'scene.mxs')
        
        if(not os.path.exists(scene_path)):
            self.update_stats("Something went wrong. Check console log.", "")
            raise Exception("Something went wrong. Check console log.")
        
        if(system.PLATFORM == 'Darwin'):
            PY = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().python_path), 'bin', 'python3.5', ))
            PYMAXWELL_PATH = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().maxwell_path), 'Libs', 'pymaxwell', 'python3.5', ))
            TEMPLATE_SCENE = system.check_for_viewport_render_scene_settings_template()
            log("scene render settings..", 1, )
            
            script_path = os.path.join(self.vr_tmp_dir, "scene.py")
            with open(script_path, mode='w', encoding='utf-8') as f:
                # read template
                with open(TEMPLATE_SCENE, encoding='utf-8') as t:
                    code = "".join(t.readlines())
                # write template to a new file
                f.write(code)
            
            q = shlex.quote
            p = [q(PY), q(script_path), q(PYMAXWELL_PATH), q(LOG_FILE_PATH), q(self.vr_tmp_dir), q(vr_quality), ]
            cmd = "{} {} {} {} {} {}".format(*p)
            # log("command:", 2)
            # log("{0}".format(cmd), 0, LogStyles.MESSAGE, prefix="")
            args = shlex.split(cmd)
            process_scene = subprocess.Popen(args, cwd=self.vr_tmp_dir, )
            process_scene.wait()
            if(process_scene.returncode != 0):
                self.update_stats("Something went wrong. Check console log.", "")
                raise Exception("Something went wrong. Check console log.")
            
            log("render scene..", 1, )
            app = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().maxwell_path), 'Maxwell.app', ))
            executable = os.path.join(app, "Contents/MacOS/Maxwell")
            
            q = shlex.quote
            p = [q(executable),
                 q(os.path.join(self.vr_tmp_dir, 'scene.mxs')),
                 q(os.path.join(self.vr_tmp_dir, 'render.mxi')),
                 q(os.path.join(self.vr_tmp_dir, 'render.exr')),
                 q(str(vr_time)),
                 q(str(vr_sl)),
                 q(str(vr_verbosity)), ]
            line = "{} -mxs:{} -mxi:{} -o:{} -time:{} -sl:{} -nowait -nogui -hide -verbose:{}".format(*p)
            cmd = shlex.split(line)
            
            self.vr_rt = ViewportRenderThread(cmd, self.vr_tmp_dir)
            
            m = bpy.context.scene.maxwell_render
            
            self.vr_ut = ViewportUpdateThread(self._vr_update_timer, self.vr_rt, m.viewport_render_update_interval, )
            self.vr_rt.start()
            self.vr_ut.start()
        elif(system.PLATFORM in ['Windows', 'Linux', ]):
            # set scene parameters and result paths
            mxs.viewport_render_scene(self.vr_tmp_dir, vr_quality, )
            
            executable = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().maxwell_path), 'maxwell.exe', ))
            
            q = shlex.quote
            p = [q(executable),
                 q(os.path.join(self.vr_tmp_dir, 'scene.mxs')),
                 q(os.path.join(self.vr_tmp_dir, 'render.mxi')),
                 q(os.path.join(self.vr_tmp_dir, 'render.exr')),
                 q(str(vr_time)),
                 q(str(vr_sl)),
                 q(str(vr_verbosity)), ]
            line = "{} -mxs:{} -mxi:{} -o:{} -time:{} -sl:{} -nowait -nogui -hide -verbose:{}".format(*p)
            cmd = shlex.split(line)
            
            self.vr_rt = ViewportRenderThread(cmd, self.vr_tmp_dir)
            
            m = bpy.context.scene.maxwell_render
            
            self.vr_ut = ViewportUpdateThread(self._vr_update_timer, self.vr_rt, m.viewport_render_update_interval, )
            self.vr_rt.start()
            self.vr_ut.start()
    
    def _vr_update_timer(self):
        try:
            if(self.vr_space_data.viewport_shade != 'RENDERED'):
                log('stopping viewport render thread', 1, )
                self.vr_rt.stop()
        except ReferenceError:
            # just kill them all, killing it more than once is not a problem..
            ViewportRenderManager.killall()
            return
        
        self.tag_redraw()
    
    def view_update(self, context=None, ):
        if(not bpy.context.scene.maxwell_render.viewport_render_enabled):
            self.update_stats("Disabled", "")
            return
        
        # if(system.PLATFORM != 'Darwin'):
        #     self.update_stats("Currently Mac OS X only", "")
        #     return
        
        # called when started and when some parameters are updated, anything from buttons for example
        
        # when called for first time, export temp scene. then block all other calls. this won't be interactive engine session..
        # then start rendering
        # from timer thread check if new render is saved and if so, load it to buffer (stored somewhere) and flag it to update and then call tag_redraw()
        
        # somehow detect the rendering is no longer requested and kill rendering, changing viewport shading is not triggering anything
        # so maybe timer thread will also check if viewport is still on 'RENDERED', if not kill it. will be a bit delayed though
        # having persistent handler on scene_update_post can't get correct reference to RenderEngine instance
        
        # would be nice if i can get maxwell console output to read what is happening in sync updates with it. also print some status info from it..
        # but how to do it in non-blocking way?
        
        if(self.vr):
            return
        
        # viewport properties
        region = context.region
        region_data = context.region_data
        space_data = context.space_data
        self.vr_space_data = space_data
        perspective = region_data.view_perspective
        
        if(perspective == 'ORTHO'):
            self.update_stats("Orthographic camera is not supported.", "")
            log("orthographic camera is not supported.", 1, LogStyles.ERROR)
            return
        elif(perspective == 'CAMERA'):
            log("Viewport Render:", 1, LogStyles.MESSAGE, )
            self.vr = True
            self.vr_view = perspective
            
            # get x,y and w,h of camera view
            scene_camera = bpy.context.scene.camera
            
            cdname = 'CAMERA-{}'.format(self.uuid)
            cd = scene_camera.data.copy()
            cd.name = cdname
            is_clone = True
            
            frame = scene_camera.data.view_frame()
            center = sum(frame, Vector()) / 4
            
            rs = bpy.context.scene.render
            y = rs.resolution_y
            x = rs.resolution_x
            if(x > y):
                ar = y / x
                vec = Vector((0.0, 1.0, 0.0))
                landscape = True
            else:
                ar = x / y
                vec = Vector((1.0, 0.0, 0.0))
                landscape = False
            
            scale = Matrix.Scale(ar, 4, vec)
            if(landscape):
                scale[1][3] = (-center[1]) * scale[1][1] + center[1]
            else:
                scale[0][3] = (-center[0]) * scale[0][0] + center[0]
            
            mat = scene_camera.matrix_world
            points = map(lambda v: mat * scale * v, (frame[0], frame[1], frame[2], frame[3]))
            
            from bpy_extras import view3d_utils
            # points_on_screen = [top right, bottom right, bottom left, top left]
            points_on_screen = [view3d_utils.location_3d_to_region_2d(region, region_data, point, ) for point in points]
            points_on_screen = [[int(v.x), int(v.y)] for v in points_on_screen]
            self.vr_camera_frame_points_on_screen = points_on_screen
            self.vr_draw_dimensions = [points_on_screen[0][0] - points_on_screen[3][0],
                                       points_on_screen[3][1] - points_on_screen[2][1], ]
            self.vr_draw_offset = [points_on_screen[3][0], points_on_screen[3][1] - self.vr_draw_dimensions[1], ]
            
            # set render size to camera view w,h
            rs = bpy.context.scene.render
            orx = rs.resolution_x
            ory = rs.resolution_y
            orp = rs.resolution_percentage
            rs.resolution_x = self.vr_draw_dimensions[0]
            rs.resolution_y = self.vr_draw_dimensions[1]
            rs.resolution_percentage = 100.0
            
            # use border render when camera is zoomed outside viewport area to speed things up
            from collections import namedtuple
            Rectangle = namedtuple('Rectangle', 'x y w h')
            # camera rectangle
            coords = points_on_screen[:]
            a = Rectangle(coords[3][0], region.height - coords[3][1], coords[1][0] - coords[3][0], coords[3][1] - coords[1][1], )
            # viewport rectangle
            b = Rectangle(0, 0, region.width, region.height, )
            
            # intersection rectangle, zero point assumed at top left
            x = 0
            y = 0
            w = 0
            h = 0
            if(a.x > b.x):
                x = a.x
                if(a.x + a.w < b.x + b.w):
                    w = a.w
                else:
                    w = b.w - a.x
            else:
                x = b.x
                if(a.x + a.w < b.x + b.w):
                    w = a.w - (b.x - a.x)
                else:
                    w = b.w
            if(a.y > b.y):
                y = a.y
                if(a.y + a.h < b.y + b.h):
                    h = a.h
                else:
                    h = b.h - a.y
            else:
                y = b.y
                if(a.y + a.h < b.y + b.h):
                    h = a.h - (b.y - a.y)
                else:
                    h = b.h
            
            c = Rectangle(x, y, w, h)
            
            w = a.w
            if(a.x < 0):
                w = a.w + a.x
                
            h = a.h
            if(a.y < 0):
                h = a.h + a.y
                
            aa = Rectangle(0, 0, w, h)
            
            minx = 0.0
            miny = 0.0
            maxx = 1.0
            maxy = 1.0
            if(a.x > b.x):
                pass
            else:
                minx = abs(a.x) / a.w
            if(a.x + a.w < b.x + b.w):
                pass
            else:
                maxx = (b.w - a.x) / a.w
            if(a.y > b.y):
                pass
            else:
                miny = abs(a.y) / a.h
            if(a.y + a.h < b.y + b.h):
                pass
            else:
                maxy = (b.h - a.y) / a.h
            
            # flip y axis
            miny = 1.0 - miny
            maxy = 1.0 - maxy
            
            if(miny > maxy):
                q = maxy
                maxy = miny
                miny = q
            
            # set it properly..
            rs = bpy.context.scene.render
            oborder = (rs.use_border, rs.border_min_x, rs.border_min_y, rs.border_max_x, rs.border_max_y, )
            rs.use_border = True
            rs.border_min_x = minx
            rs.border_min_y = miny
            rs.border_max_x = maxx
            rs.border_max_y = maxy
            rp = bpy.context.scene.render
            x_res = int(rp.resolution_x * rp.resolution_percentage / 100.0)
            y_res = int(rp.resolution_y * rp.resolution_percentage / 100.0)
            x = int(x_res * rp.border_min_x)
            h = y_res - int(y_res * rp.border_min_y)
            w = int(x_res * rp.border_max_x)
            y = y_res - int(y_res * rp.border_max_y)
            
            cam = bpy.data.objects.new(cdname, cd)
            bpy.context.scene.objects.link(cam)
            bpy.context.scene.camera = cam
            cam.matrix_world = mat
            
            m = cam.data.maxwell_render
            m.screen_region = 'REGION'
            m.screen_region_x = x
            m.screen_region_y = y
            m.screen_region_w = w
            m.screen_region_h = h
            
            self.vr_space_dimensions = [region.width, region.height]
            
        elif(perspective == 'PERSP'):
            log("Viewport Render:", 1, LogStyles.MESSAGE, )
            self.vr = True
            self.vr_view = perspective
            
            m = Matrix(region_data.view_matrix).inverted()
            w = region.width
            h = region.height
            lens = space_data.lens / 2
            
            # get active camera
            scene_camera = bpy.context.scene.camera
            # clone data
            cdname = 'VIEWPORT_CAMERA-{}'.format(self.uuid)
            is_clone = False
            if(scene_camera is None):
                # create one with default settings
                cd = bpy.data.cameras.new(cdname)
            else:
                # copy active
                cd = scene_camera.data.copy()
                cd.name = cdname
                is_clone = True
            
            # camera properties
            cd.lens = lens
            
            # auto focus (if requested and if possible)
            mx = bpy.context.scene.maxwell_render
            if(mx.viewport_render_autofocus):
                d = 1000000.0
                e, t, u = maths.eye_target_up_from_matrix(m, d)
                a = e.copy()
                b = maths.shift_vert_along_normal(a, t, d)
                
                # blender 2.77 api change
                # hit, _, _, loc, _ = bpy.context.scene.ray_cast(a, b)
                if bpy.app.version < (2, 77, 0):
                    hit, _, _, loc, _ = bpy.context.scene.ray_cast(a, b)
                else:
                    hit, loc, _, _, _, _ = bpy.context.scene.ray_cast(a, b)
                
                if(hit):
                    cd.dof_object = None
                    cd.dof_distance = maths.distance_vectors(a, loc)
                else:
                    if(is_clone):
                        # is cloned from active scene camera
                        pass
                    else:
                        # nothing to do..
                        pass
            
            # add to scene just for e while to export it
            cam = bpy.data.objects.new(cdname, cd)
            bpy.context.scene.objects.link(cam)
            bpy.context.scene.camera = cam
            cam.matrix_world = m
            
            rs = bpy.context.scene.render
            orx = rs.resolution_x
            ory = rs.resolution_y
            orp = rs.resolution_percentage
            rs.resolution_x = w
            rs.resolution_y = h
            rs.resolution_percentage = 100.0
            
            self.vr_draw_offset = [0, 0]
            self.vr_draw_dimensions = [w, h]
            self.vr_space_dimensions = [w, h]
        
        # export..
        p = bpy.data.filepath
        if(p == ""):
            self.update_stats("Save file first.", "")
            log("save file first.", 1, LogStyles.ERROR)
            return
        
        self.update_stats("Exporting scene..", "")
        log("exporting scene..", 1, )
        
        self.vr_tmp_dir = utils.tmp_dir(purpose='viewport_render', uid=self.uuid, use_blend_name=True, )
        
        # set output image and mxi to something if empty
        mx = bpy.context.scene.maxwell_render
        if(mx.output_image == ''):
            mx.output_depth = 'RGB32'
            mx.output_image = bpy.path.abspath(os.path.join(h, '{}.exr'.format(n)))
        if(mx.output_mxi == ''):
            mx.output_mxi = bpy.path.abspath(os.path.join(h, '{}.mxi'.format(n)))
        
        # and export mxs
        p = bpy.path.abspath(os.path.join(self.vr_tmp_dir, 'scene.mxs'))
        ex = export.MXSExport(mxs_path=p, )
        
        if(perspective == 'ORTHO'):
            pass
        elif(perspective == 'CAMERA'):
            utils.wipe_out_object(cam, and_data=True, )
            bpy.context.scene.camera = scene_camera
            
            bpy.ops.view3d.viewnumpad(type='CAMERA')
            
            # restore settings
            rs.resolution_x = orx
            rs.resolution_y = ory
            rs.resolution_percentage = orp
            
            rs.use_border = oborder[0]
            rs.border_min_x = oborder[1]
            rs.border_min_y = oborder[2]
            rs.border_max_x = oborder[3]
            rs.border_max_y = oborder[4]
            
        elif(perspective == 'PERSP'):
            # then remove it again, it is no longer needed
            utils.wipe_out_object(cam, and_data=True, )
            # and restore settings
            rs.resolution_x = orx
            rs.resolution_y = ory
            rs.resolution_percentage = orp
            bpy.context.scene.camera = scene_camera
        
        # mxs is ready, all changes reverted, now start rendering
        self._vr_render_start()
    
    def _vr_get_buffer(self):
        p = os.path.join(self.vr_tmp_dir, 'render.exr')
        pp = os.path.join(self.vr_tmp_dir, 'render2.exr')
        if(os.path.exists(p)):
            if(not os.access(p, os.R_OK, )):
                # skip if not accessible (maxwell is writing to it?)
                return None
            
            # copy to skip possible conflict
            shutil.copyfile(p, pp)
            
            # load and draw
            log("reading render..", 1, )
            
            a = None
            if(system.PLATFORM == 'Darwin'):
                PY = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().python_path), 'bin', 'python3.5', ))
                PYMAXWELL_PATH = os.path.abspath(os.path.join(bpy.path.abspath(system.prefs().maxwell_path), 'Libs', 'pymaxwell', 'python3.5', ))
                TEMPLATE_MXI = system.check_for_viewport_render_mxi_template()
                NUMPY_PATH = os.path.split(os.path.split(np.__file__)[0])[0]
                
                script_path = os.path.join(self.vr_tmp_dir, "preview.py")
                with open(script_path, mode='w', encoding='utf-8') as f:
                    # read template
                    with open(TEMPLATE_MXI, encoding='utf-8') as t:
                        code = "".join(t.readlines())
                    # write template to a new file
                    f.write(code)
                
                q = shlex.quote
                p = [q(PY), q(script_path), q(PYMAXWELL_PATH), q(NUMPY_PATH), q(LOG_FILE_PATH), q(self.vr_tmp_dir), ]
                cmd = "{} {} {} {} {} {}".format(*p)
                # log("command:", 2)
                # log("{0}".format(cmd), 0, LogStyles.MESSAGE, prefix="")
                args = shlex.split(cmd)
                process_scene = subprocess.Popen(args, cwd=self.vr_tmp_dir, )
                process_scene.wait()
                if(process_scene.returncode != 0):
                    return None
                
                # remove copy, it is no longer needed
                os.remove(pp)
                
                npy = os.path.join(self.vr_tmp_dir, "preview.npy")
                if(os.path.exists(npy)):
                    a = np.load(npy)
                if(a is not None):
                    if(a.shape == (1, 1, 3)):
                        # there was an error
                        log('preview render failed..', 1, LogStyles.ERROR, )
                        return None
                else:
                    log('preview render pixels read failed..', 1, LogStyles.ERROR, )
                    return None
                
            elif(system.PLATFORM in ['Windows', 'Linux', ]):
                # get render as numpy float array
                a = mxs.viewport_render_mxi(self.vr_tmp_dir)
                
                # remove copy, it is no longer needed
                os.remove(pp)
                
                if(a is not None):
                    if(a.shape == (1, 1, 3)):
                        # there was an error
                        log('preview render failed..', 1, LogStyles.ERROR, )
                        return None
                else:
                    log('preview render pixels read failed..', 1, LogStyles.ERROR, )
                    return None
            
            # gamma uncorrect
            g = 1 / 2.2
            a = a[:] ** g
            # flip
            a = np.flipud(a)
            # flip dimensions
            h, w, d = a.shape
            # flatten
            sz = w * h * d
            a = np.reshape(a, (sz))
            # gl_buffer = bgl.Buffer(bgl.GL_FLOAT, [sz], a)
            # return gl_buffer
            return a, sz, w, h, d
        
        # leave it as it is. upon render finish and last draw, tmp files should be removed. or not?
        return None
    
    def view_draw(self, context=None, ):
        if(not bpy.context.scene.maxwell_render.viewport_render_enabled):
            return
        
        # if(system.PLATFORM != 'Darwin'):
        #     self.update_stats("Currently Mac OS X only", "")
        #     return
        
        if(not self.vr):
            return
        
        # NOTE: when render finished normally, this is called one more time after files were removed and complains about missing files, update: seems to be fixed, but leave it here as reminder..
        
        # called right after view_update and each time when viewport is moved
        
        # block calls from blender
        # allow only those which follows buffer update. then draw to viewport new buffer
        
        self.update_stats("Rendering..", "")
        if(self.vr_rt is not None):
            if(self.vr_rt.stopped()):
                log("rendering stopped..", 1, )
                self.update_stats("Stopped", "")
        
        log("getting buffer..", 1)
        a = None
        gl_buffer = None
        r = self._vr_get_buffer()
        if(r is not None):
            a, sz, _, _, _ = r
            if(a is not None):
                gl_buffer = bgl.Buffer(bgl.GL_FLOAT, [sz], a)
        
        draw = True
        if(gl_buffer is None):
            if(self.vr_previous_buffer is None):
                draw = False
            else:
                log("something went wrong, using previous buffer..", 1, LogStyles.WARNING)
                gl_buffer = self.vr_previous_buffer
                a = self.vr_previous_array
        else:
            self.vr_previous_buffer = gl_buffer
            self.vr_previous_array = a
        
        if(not draw):
            log("nothing to draw..", 1)
            return
        
        log("drawing..", 1)
        # if(self.vr_view == 'CAMERA'):
        #     bgl.glRasterPos2i(*self.vr_draw_offset)
        #     bgl.glDrawPixels(self.vr_draw_dimensions[0], self.vr_draw_dimensions[1], bgl.GL_RGB, bgl.GL_FLOAT, gl_buffer)
        # else:
        #     bgl.glRasterPos2i(0, 0)
        #     bgl.glDrawPixels(w, h, bgl.GL_RGB, bgl.GL_FLOAT, gl_buffer)
        
        x, y = self.vr_draw_offset
        w, h = self.vr_draw_dimensions
        
        if(self.vr_view == 'CAMERA'):
            # camera can be moved to negative coordinates
            if(x < 0 or y < 0):
                # negative offset, nothing will be drawn, so slice array and make new buffer
                a = np.reshape(a, (h, w, 3))
                # slice
                if(x < 0):
                    a = a[:, abs(x):, :, ]
                    x = 0
                if(y < 0):
                    a = a[abs(y):, :, :, ]
                    y = 0
                h, w, _ = a.shape
                # flatten
                sz = w * h * 3
                a = np.reshape(a, (sz))
                # and create new buffer
                gl_buffer = bgl.Buffer(bgl.GL_FLOAT, [sz], a)
        
        bgl.glRasterPos2i(x, y)
        bgl.glDrawPixels(w, h, bgl.GL_RGB, bgl.GL_FLOAT, gl_buffer)
        log("done.", 1)
        
        # remove files after last buffer read
        if(self.vr_rt is not None):
            if(self.vr_rt.stopped()):
                self._vr_cleanup()
    
    def _vr_cleanup(self):
        if(self.vr_tmp_dir is None):
            return
        
        # NOTE: when render is finished normally, cleanup is called more times then it should, result in warning about missing files, following is a quick fix, seems like view_draw is also called one more extra time, and complains about missing files, i guess this is cause by global cleanup in ViewportRenderManager and cleanup here. leave it as it is for now..
        if(not os.path.exists(self.vr_tmp_dir)):
            return
        
        log("cleanup..", 1)
        tmp_dir = self.vr_tmp_dir
        
        def rm(p, warn_if_missing=True, ):
            if(os.path.exists(p)):
                os.remove(p)
            else:
                if(warn_if_missing):
                    log("cleanup: {} does not exist?".format(p), 1, LogStyles.WARNING, )
        
        rm(os.path.join(tmp_dir, 'scene.mxs'), True, )
        rm(os.path.join(tmp_dir, 'render.exr'), True, )
        rm(os.path.join(tmp_dir, 'render.mxi'), False, )
        if(system.PLATFORM == 'Darwin'):
            rm(os.path.join(tmp_dir, 'scene.py'))
            rm(os.path.join(tmp_dir, 'preview.npy'), False, )
            rm(os.path.join(tmp_dir, 'preview.py'), False, )
        
        if(os.path.exists(tmp_dir)):
            try:
                os.rmdir(tmp_dir)
            except OSError as e:
                log(e, 0, LogStyles.WARNING)
                # use a bit more force..
                log("removing whole directory tree", 0, LogStyles.ERROR)
                shutil.rmtree(tmp_dir)
        else:
            log("cleanup: {} does not exist?".format(tmp_dir), 1, LogStyles.WARNING, )
