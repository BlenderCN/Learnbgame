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

import os
import sys
import time
import numpy

import bpy

from bpy_extras.io_utils import axis_conversion

from ..extensions_framework import util as efutil

# Mitsuba libs
from .. import MitsubaAddon

from ..export import ExportContextBase
from ..export import matrix_to_list
from ..properties import ExportedVolumes

from ..outputs import MtsLog, MtsManager

addon_prefs = MitsubaAddon.get_prefs()
oldflags = None

if not 'PYMTS_AVAILABLE' in locals() and addon_prefs is not None:
    try:
        ver_str = '%d.%d' % bpy.app.version[0:2]
        mitsuba_path = efutil.filesystem_path(addon_prefs.install_path)

        if sys.platform == 'win32':
            os.environ['PATH'] = mitsuba_path + os.pathsep + os.environ['PATH']

        elif sys.platform == 'darwin':
            mitsuba_path = mitsuba_path[:mitsuba_path.index('Mitsuba.app') + 11]
            os.environ['PATH'] = os.path.join(mitsuba_path, 'Contents', 'Frameworks') + os.pathsep + os.environ['PATH']
            os.environ['PATH'] = os.path.join(mitsuba_path, 'plugins') + os.pathsep + os.environ['PATH']

        mts_python_path = {
            'darwin': [
                bpy.utils.user_resource('SCRIPTS', 'addons/mtsblend/mitsuba.so'),
                bpy.app.binary_path[:-7] + ver_str + '/scripts/addons/mtsblend/mitsuba.so',
                os.path.join(mitsuba_path, 'python', '3.4', 'mitsuba.so'),
            ],
            'win32': [
                bpy.utils.user_resource('SCRIPTS', 'addons/mtsblend/mitsuba.pyd'),
                bpy.app.binary_path[:-11] + ver_str + '/scripts/addons/mtsblend/mitsuba.pyd',
                os.path.join(mitsuba_path, 'python', '3.4', 'mitsuba.pyd'),
            ],
            'linux': [
                bpy.app.binary_path[:-7] + ver_str + '/scripts/addons/mtsblend/mitsuba.so',
                '/usr/lib/python3.4/dist-packages/mitsuba.so',
                '/usr/lib/python3.4/lib-dynload/mitsuba.so',
                '/usr/lib64/python3.4/lib-dynload/mitsuba.so',
            ]
        }

        for sp in mts_python_path[sys.platform]:
            if os.path.exists(sp):
                MtsLog('Mitsuba python extension found at: %s' % sp)
                sys.path.append(os.path.dirname(sp))
                break

        if sys.platform == 'linux':
            RTLD_LAZY = 2
            RTLD_DEEPBIND = 8
            oldflags = sys.getdlopenflags()
            sys.setdlopenflags(RTLD_DEEPBIND | RTLD_LAZY)

        import mitsuba

        if sys.platform == 'linux':
            sys.setdlopenflags(oldflags)

        from mitsuba.core import (
            Scheduler, LocalWorker, Thread, Bitmap, Point2i, Vector2i, FileStream,
            PluginManager, Spectrum, InterpolatedSpectrum, BlackBodySpectrum, Vector, Point,
            Matrix4x4, Transform, AnimatedTransform,
            Appender, EInfo, EWarn, EError,
        )
        from mitsuba.render import (
            RenderQueue, RenderJob, RenderListener, Scene, SceneHandler, TriMesh
        )

        import multiprocessing

        main_thread = Thread.getThread()
        main_fresolver = main_thread.getFileResolver()
        main_logger = main_thread.getLogger()

        class CustomAppender(Appender):
            def append(self, logLevel, message):
                MtsLog(message)

            def logProgress(self, progress, name, formatted, eta):
                render_engine = MtsManager.RenderEngine

                if not render_engine.is_preview:
                    percent = progress / 100
                    render_engine.update_progress(percent)
                    render_engine.update_stats('', 'Progress: %s - ETA: %s' % ('{:.2%}'.format(percent), eta))

                else:
                    MtsLog('Progress message: %s' % formatted)

        main_logger.clearAppenders()
        main_logger.addAppender(CustomAppender())
        main_logger.setLogLevel(EWarn)

        scheduler = Scheduler.getInstance()
        # Start up the scheduling system with one worker per local core
        for i in range(0, multiprocessing.cpu_count()):
            scheduler.registerWorker(LocalWorker(i, 'wrk%i' % i))

        scheduler.start()

        class ApiExportContext(ExportContextBase):
            '''
            Python API
            '''

            EXPORT_API_TYPE = 'API'

            thread = None
            scheduler = None
            pmgr = None
            scene = None

            def __init__(self):
                super().__init__()

                self.thread = Thread.registerUnmanagedThread('exporter')
                self.thread.setFileResolver(main_fresolver)
                self.thread.setLogger(main_logger)

                self.pmgr = PluginManager.getInstance()
                self.scene = Scene()

            # Funtions binding to Mitsuba extension API

            def spectrum(self, value, mode=''):
                if not mode:
                    mode = self.color_mode

                spec = None

                if isinstance(value, (dict)):
                    if 'type' in value:
                        if value['type'] in {'rgb', 'srgb', 'spectrum'}:
                            spec = self.spectrum(value['value'], value['type'])

                        elif value['type'] == 'blackbody':
                            spec = Spectrum()
                            spec.fromContinuousSpectrum(BlackBodySpectrum(value['temperature']))
                            spec.clampNegative()
                            spec = spec * value['scale']

                elif isinstance(value, (float, int)):
                    spec = Spectrum(value)

                elif isinstance(value, (str)):
                    contspec = InterpolatedSpectrum(self.get_export_path(value))
                    spec = Spectrum()
                    spec.fromContinuousSpectrum(contspec)
                    spec.clampNegative()

                else:
                    try:
                        items = list(value)

                        for i in items:
                            if not isinstance(i, (float, int, tuple)):
                                raise Exception('Error: spectrum list contains an unknown type')

                    except:
                        items = None

                    if items:
                        totitems = len(items)

                        if isinstance(items[0], (float, int)):
                            if totitems == 3 or totitems == 4:
                                spec = Spectrum()

                                if mode == 'srgb':
                                    spec.fromSRGB(items[0], items[1], items[2])

                                else:
                                    spec.fromLinearRGB(items[0], items[1], items[2])

                            elif totitems == 1:
                                spec = Spectrum(items[0])

                            else:
                                MtsLog('Expected spectrum items to be 1, 3 or 4, got %d.' % len(items), type(items), items)

                        else:
                            spec = Spectrum()
                            contspec = InterpolatedSpectrum()

                            for spd in items:
                                (wlen, val) = spd
                                contspec.append(wlen, val)

                            spec.fromContinuousSpectrum(contspec)
                            spec.clampNegative()

                    else:
                        MtsLog('Unknown spectrum type.', type(value), value)

                if spec is None:
                    spec = Spectrum(0.0)

                return spec

            def vector(self, x, y, z):
                # Blender is Z up but Mitsuba is Y up, convert the vector
                return Vector(x, z, -y)

            def point(self, x, y, z):
                # Blender is Z up but Mitsuba is Y up, convert the point
                return Point(x, z, -y)

            def transform_lookAt(self, origin, target, up, scale=None):
                # Blender is Z up but Mitsuba is Y up, convert the lookAt
                transform = Transform.lookAt(
                    Point(origin[0], origin[2], -origin[1]),
                    Point(target[0], target[2], -target[1]),
                    Vector(up[0], up[2], -up[1])
                )

                if scale is not None:
                    transform *= Transform.scale(Vector(scale, scale, 1))

                return transform

            def animated_lookAt(self, motion):
                if len(motion) == 2 and motion[0][1] == motion[1][1]:
                    del motion[1]

                if len(motion) > 1:
                    transform = AnimatedTransform()

                    for (t, (origin, target, up, scale)) in motion:
                        transform.appendTransform(t, self.transform_lookAt(origin, target, up, scale))

                else:
                    (origin, target, up, scale) = motion[0][1]
                    transform = self.transform_lookAt(origin, target, up, scale)

                return transform

            def transform_matrix(self, matrix):
                # Blender is Z up but Mitsuba is Y up, convert the matrix
                global_matrix = axis_conversion(to_forward="-Z", to_up="Y").to_4x4()
                l = matrix_to_list(global_matrix * matrix)
                mat = Matrix4x4(l)
                transform = Transform(mat)

                return transform

            def animated_transform(self, motion):
                if len(motion) == 2 and motion[0][1] == motion[1][1]:
                    del motion[1]

                if len(motion) > 1:
                    transform = AnimatedTransform()

                    for (t, m) in motion:
                        transform.appendTransform(t, self.transform_matrix(m))

                else:
                    transform = self.transform_matrix(motion[0][1])

                return transform

            def configure(self):
                '''
                Call Scene configure
                '''

                self.scene.addChild(self.pmgr.create(self.scene_data))
                self.scene.configure()

                # Reset the volume redundancy check
                ExportedVolumes.reset_vol_list()

            def cleanup(self):
                self.exit()

            def exit(self):
                # Do nothing
                pass

        class InternalBufferDisplay(RenderListener):
            '''
            Class to monitor rendering and update blender render result
            '''
            def __init__(self, render_ctx):
                super(InternalBufferDisplay, self).__init__()
                self.ctx = render_ctx
                self.film = self.ctx.scene.getFilm()
                self.size = self.film.getSize()
                self.bitmap = Bitmap(Bitmap.ERGBA, Bitmap.EFloat32, self.size)
                self.bitmap.clear()
                self.buffer = None
                self.fast_buffer = True
                self.do_cancel = False
                self.time = 0
                self.delay = .5
                self.ctx.queue.registerListener(self)

            def get_offset_size(self, wu):
                offset = wu.getOffset()
                size = wu.getSize()
                end = offset + size
                offset.x = max(0, offset.x)
                offset.y = max(0, offset.y)
                end.x = min(self.size.x, end.x)
                end.y = min(self.size.y, end.y)
                size = end - offset

                return offset, size

            def workBeginEvent(self, job, wu, thr):
                offset, size = self.get_offset_size(wu)
                self.bitmap.drawWorkUnit(offset, size, thr)
                self.timed_update_result()

            def workEndEvent(self, job, wr, cancelled):
                offset, size = self.get_offset_size(wr)
                self.film.develop(offset, size, offset, self.bitmap)
                self.timed_update_result()

            def refreshEvent(self, job):
                self.film.develop(Point2i(0), self.size, Point2i(0), self.bitmap)
                self.update_result()

            def finishJobEvent(self, job, cancelled):
                MtsLog('Render Job Finished')
                self.film.develop(Point2i(0), self.size, Point2i(0), self.bitmap)
                self.update_result(render_end=True)

            def get_bitmap_buffer(self, passes=1):
                bitmap_clone = self.bitmap.clone()
                bitmap_clone.flipVertically()

                if passes == 1:
                    return bitmap_clone.buffer()

                if self.buffer is None:
                    self.buffer = Bitmap(Bitmap.ERGBA, Bitmap.EFloat32, Vector2i(self.size[0], self.size[1] * passes))
                    self.buffer.clear()

                self.buffer.copyFrom(bitmap_clone)

                return self.buffer.buffer()

            def get_bitmap_list(self):
                self.delay = 1.5
                bitmap_list = numpy.ndarray((self.size[0] * self.size[1], 4), buffer=self.get_bitmap_buffer(), dtype='float32')  # .tolist()

                return bitmap_list

            def timed_update_result(self):
                now = time.time()

                if now - self.time > self.delay:
                    self.time = now
                    self.update_result()

            def update_result(self, render_end=False):
                if self.ctx.test_break():
                    return

                try:
                    render_result = self.ctx.render_engine.begin_result(0, 0, self.size[0], self.size[1])

                    if render_result is None:
                        err_msg = 'ERROR: Cannot not load render result: begin_result() returned None.'
                        self.do_cancel = True
                        raise Exception(err_msg)

                    if self.fast_buffer:
                        passes = len(render_result.layers[0].passes)
                        bitmap_buffer = self.get_bitmap_buffer(passes)
                        render_result.layers[0].passes.foreach_set('rect', bitmap_buffer)

                    else:
                        bitmap_buffer = self.get_bitmap_list()
                        render_result.layers[0].passes[0].rect = bitmap_buffer

                    self.ctx.render_engine.end_result(render_result, 0)

                except Exception as err:
                    MtsLog('%s' % err)

                    if self.fast_buffer:
                        self.fast_buffer = False

                    else:
                        self.do_cancel = True

                    if self.do_cancel:
                        self.ctx.render_cancel()

        class InternalRenderContext:
            '''
            Mitsuba Internal Python API Render
            '''

            RENDER_API_TYPE = 'INT'

            cancelled = False
            thread = None
            scheduler = None
            fresolver = None
            log_level = {
                'default': EWarn,
                'verbose': EInfo,
                'quiet': EError,
            }

            def __init__(self):
                self.fresolver = main_fresolver.clone()
                self.thread = Thread.registerUnmanagedThread('renderer')
                self.thread.setFileResolver(self.fresolver)
                self.thread.setLogger(main_logger)

                self.render_engine = MtsManager.RenderEngine
                self.render_scene = MtsManager.CurrentScene

                if self.render_engine.is_preview:
                    verbosity = 'quiet'

                else:
                    verbosity = self.render_scene.mitsuba_engine.log_verbosity

                main_logger.setLogLevel(self.log_level[verbosity])

            def set_scene(self, export_context):
                if export_context.EXPORT_API_TYPE == 'FILE':
                    scene_path, scene_file = os.path.split(efutil.filesystem_path(export_context.file_names[0]))
                    self.fresolver.appendPath(scene_path)
                    self.scene = SceneHandler.loadScene(self.fresolver.resolve(scene_file))

                elif export_context.EXPORT_API_TYPE == 'API':
                    self.scene = export_context.scene

                else:
                    raise Exception('Unknown exporter type')

            def render_start(self, dest_file):
                self.cancelled = False
                self.queue = RenderQueue()
                self.buffer = InternalBufferDisplay(self)
                self.job = RenderJob('mtsblend_render', self.scene, self.queue)
                self.job.start()

                #out_file = FileStream(dest_file, FileStream.ETruncReadWrite)
                #self.bitmap.write(Bitmap.EPNG, out_file)
                #out_file.close()

            def render_stop(self):
                self.job.cancel()
                # Wait for the render job to finish
                self.queue.waitLeft(0)

            def render_cancel(self):
                self.cancelled = True
                MtsLog('Cancelling render.')

            def test_break(self):
                return self.render_engine.test_break() or self.cancelled

            def is_running(self):
                return self.job.isRunning()

            def returncode(self):
                return 0

            def wait_timer(self):
                pass

        class Serializer:
            '''
            Helper Class for fast mesh export in File API
            '''

            def __init__(self):
                self.thread = Thread.registerUnmanagedThread('serializer')
                self.thread.setFileResolver(main_fresolver)
                self.thread.setLogger(main_logger)

            def serialize(self, fileName, name, mesh, materialID):
                faces = mesh.tessfaces[0].as_pointer()
                vertices = mesh.vertices[0].as_pointer()

                uv_textures = mesh.tessface_uv_textures

                if len(uv_textures) > 0 and mesh.uv_textures.active and uv_textures.active.data:
                    texCoords = uv_textures.active.data[0].as_pointer()

                else:
                    texCoords = 0

                vertex_color = mesh.tessface_vertex_colors.active

                if vertex_color:
                    vertexColors = vertex_color.data[0].as_pointer()

                else:
                    vertexColors = 0

                trimesh = TriMesh.fromBlender(mesh.name, len(mesh.tessfaces),
                    faces, len(mesh.vertices), vertices, texCoords, vertexColors, materialID)

                fstream = FileStream(fileName, FileStream.ETruncReadWrite)
                trimesh.serialize(fstream)
                fstream.writeULong(0)
                fstream.writeUInt(1)
                fstream.close()

        PYMTS_AVAILABLE = True
        MtsLog('Using Mitsuba python extension')

    except ImportError as err:
        MtsLog('WARNING: Binary mitsuba module not available! Visit http://www.mitsuba-renderer.org/ to obtain one for your system.')
        MtsLog(' (ImportError was: %s)' % err)
        PYMTS_AVAILABLE = False

        if sys.platform == 'linux' and oldflags is not None:
            sys.setdlopenflags(oldflags)
