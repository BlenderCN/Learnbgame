import bpy
import os
import sys
import time
import subprocess
import threading
import re
import importlib
import numpy as np
from collections import deque

from .. import export

pearray_package = __import__(__name__.split('.')[0])


class PearRayRender(bpy.types.RenderEngine):
    bl_idname = 'PEARRAY_RENDER'
    bl_label = "PearRay"
    #bl_use_preview = True
    bl_use_exclude_layers = True


    @staticmethod
    def _setup_package():
        addon_prefs = bpy.context.user_preferences.addons[pearray_package.__package__].preferences

        if addon_prefs.package_dir:
            sys.path.append(bpy.path.resolve_ncase(bpy.path.abspath(addon_prefs.package_dir)))

        return importlib.import_module("pypearray")


    def _proc_wait(self, renderer):
        time.sleep(0.25)

        # User interrupts the rendering
        if self.test_break():
            try:
                renderer.stop()
                print("<<< PEARRAY INTERRUPTED >>>")
            except OSError:
                pass
            return False
        
        if renderer.finished:
            return False
        
        return True

    
    def _handle_render_stat(self, renderer):
        stat = renderer.status
        
        line = "Pass %s S %i R %i EH %i BH %i" % (renderer.currentPass+1,
             stat['global.pixel_sample_count'],
             stat['global.ray_count'],
             stat['global.entity_hit_count'],
             stat['global.background_hit_count'])
        
        self.update_stats("", "PearRay: Rendering [%s]..." % (line))
        self.update_progress(stat.percentage)


    def render(self, scene):
        addon_prefs = bpy.context.user_preferences.addons[pearray_package.__package__].preferences
        pr = PearRayRender._setup_package()
        pr.Logger.instance.verbosity = pr.LogLevel.DEBUG if addon_prefs.verbose else pr.LogLevel.INFO

        specDesc = pr.SpectrumDescriptor.createStandardSpectral()

        import tempfile
        render = scene.render

        x = int(render.resolution_x * render.resolution_percentage * 0.01)
        y = int(render.resolution_y * render.resolution_percentage * 0.01)

        print("<<< START PEARRAY >>>")
        blendSceneName = bpy.data.filepath.split(os.path.sep)[-1].split(".")[0]
        if not blendSceneName:
            blendSceneName = "blender_scene"

        sceneFile = ""
        renderPath = ""

        # has to be called to update the frame on exporting animations
        scene.frame_set(scene.frame_current)

        renderPath = bpy.path.resolve_ncase(bpy.path.abspath(render.filepath))
        
        if not render.filepath:
            renderPath = tempfile.gettempdir()
        
        if scene.pearray.keep_prc:
            sceneFile = os.path.normpath(renderPath + "/scene.prc")
        else:
            sceneFile = tempfile.NamedTemporaryFile(suffix=".prc").name

        
        self.update_stats("", "PearRay: Exporting data")
        scene_exporter = export.Exporter(sceneFile, scene)
        scene_exporter.write_scene(pr)

        self.update_stats("", "PearRay: Starting render")
        environment = pr.SceneLoader.loadFromFile(sceneFile)

        toneMapper = pr.ToneMapper(x, y)
        toneMapper.colorMode = pr.ToneColorMode.SRGB
        toneMapper.gammaMode = pr.ToneGammaMode.NONE
        toneMapper.mapperMode = pr.ToneMapperMode.NONE

        colorBuffer = pr.ColorBuffer(x,y,pr.ColorBufferMode.RGBA)

        environment.registry.set('/renderer/film/width', x)
        environment.registry.set('/renderer/film/height', y)

        if addon_prefs.verbose:
            print("Registry:")
            print(environment.registry.dump())
        
        pr_scene = environment.sceneFactory.create()
        if not pr_scene:
            self.report({'ERROR'}, "PearRay: could not create pearray scene instance")
            print("<<< PEARRAY FAILED >>>")
            return

        factory = pr.RenderFactory(specDesc, pr_scene, environment.registry, renderPath)

        addon_prefs = bpy.context.user_preferences.addons[pearray_package.__package__].preferences
        renderer = factory.create()

        if not renderer:
            self.report({'ERROR'}, "PearRay: could not create pearray render instance")
            print("<<< PEARRAY FAILED >>>")
            return

        environment.setup(renderer)

        if not os.path.exists(renderPath):
            os.makedirs(renderPath)

        threads = 0
        if scene.render.threads_mode == 'FIXED':
            threads = scene.render.threads

        renderer.start(scene.render.tile_x, scene.render.tile_y, threads)

        # Update image
        result = self.begin_result(0, 0, x, y)
        layer = result.layers[0]

        def update_image():
            colorBuffer.map(toneMapper, renderer.output.spectral)
            arr = np.array(colorBuffer, copy=False)
            arr = np.reshape(np.flip(arr,0), (x*y,4), 'C')
            layer.passes["Combined"].rect = arr
            self.update_result(result)

        update_image()

        prog_start = time.time()
        img_start = time.time()
        while self._proc_wait(renderer):
            prog_end = time.time() 
            if addon_prefs.show_progress_interval < (prog_end - prog_start):
                self._handle_render_stat(renderer)
                prog_start = prog_end

            if addon_prefs.show_image_interval > 0:
                img_end = time.time() 
                if addon_prefs.show_image_interval < (img_end - img_start):
                    update_image()
                    img_start = img_end

        update_image()
        self.end_result(result)

        environment.save(renderer, toneMapper, True)

        if not scene.pearray.keep_prc:
            os.remove(sceneFile)
        
        self.update_stats("", "")
        print("<<< PEARRAY FINISHED >>>")