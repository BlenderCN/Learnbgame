import os
import importlib

import bpy

from ..extensions_framework import log
from ..extensions_framework.util import TimerThread


def BrlLog(*args, popup=False):
    '''
    Send string to AF log, marked as belonging to BRLCAD module.
    Accepts variable args
    '''
    if len(args) > 0:
        log(' '.join(['%s' % a for a in args]), module_name='BRLCAD', popup=popup)


class BrlFilmDisplay(TimerThread):
    '''
    Periodically update render result with BRLCAD's framebuffer
    '''

    STARTUP_DELAY = 2  # Add additional time to first KICK PERIOD

    def kick(self, render_end=False):
        if 'RE' in self.LocalStorage.keys():
            direct_transfer = False

            if not bpy.app.background or render_end:

                xres = yres = -1

                if 'resolution' in self.LocalStorage.keys():
                    xres, yres = self.LocalStorage['resolution']

                if xres == -1 or yres == -1:
                    err_msg = 'ERROR: Cannot not load render result: resolution unknown. BrlFilmThread will terminate'
                    BrlLog(err_msg)
                    self.stop()
                    return

                if render_end:
                    BrlLog('Final render result (%ix%i)' % (xres, yres))

                elif self.LocalStorage['render_ctx'].RENDER_API_TYPE == 'EXT':
                    BrlLog('Updating render result (%ix%i)' % (xres, yres))

                result = self.LocalStorage['RE'].begin_result(0, 0, xres, yres)

                if result is None:
                    err_msg = 'ERROR: Cannot not load render result: begin_result() returned None. BrlFilmThread will terminate'
                    BrlLog(err_msg)
                    self.stop()
                    return

                lay = result.layers[0]

                if self.LocalStorage['render_ctx'].RENDER_API_TYPE == 'INT':
                    bitmap_buffer = self.LocalStorage['render_ctx'].get_bitmap_buffer()
                    lay.passes.foreach_set('rect', bitmap_buffer)

                elif os.path.exists(self.LocalStorage['RE'].output_file):
                    lay.load_from_file(self.LocalStorage['RE'].output_file)

                else:
                    err_msg = 'ERROR: Could not load render result from %s' % self.LocalStorage['RE'].output_file
                    BrlLog(err_msg)

                self.LocalStorage['RE'].end_result(result, 0)

        else:
            err_msg = 'ERROR: BrlFilmThread started with insufficient parameters. BrlFilmThread will terminate'
            BrlLog(err_msg)
            self.stop()
            return

FBACK_API = None
PYBRL_API = None


class BrlManager:
    '''
    Manage a Context object for rendering.

    Objects of this class are responsible for the life cycle of
    a Context object, ensuring proper initialisation, usage
    and termination.

    Additionally, BrlManager objects will also spawn timer threads
    in order to update the image framebuffer.
    '''

    ActiveManager = None

    @staticmethod
    def SetActive(MM):
        BrlManager.ActiveManager = MM

    @staticmethod
    def GetActive():
        return BrlManager.ActiveManager

    @staticmethod
    def ClearActive():
        BrlManager.ActiveManager = None

    RenderEngine = None

    @staticmethod
    def SetRenderEngine(engine):
        BrlManager.RenderEngine = engine

    @staticmethod
    def ClearRenderEngine():
        BrlManager.RenderEngine = None

    CurrentScene = None

    @staticmethod
    def SetCurrentScene(scene):
        BrlManager.CurrentScene = scene

    @staticmethod
    def ClearCurrentScene():
        BrlManager.CurrentScene = None

    context_count = 0

    @staticmethod
    def get_context_number():
        '''
        Give each context a unique serial number by keeping
        count in a static member of BrlManager
        '''

        BrlManager.context_count += 1
        return BrlManager.context_count

    manager_name = ''
    render_engine = None
    fback_api = None
    pybrl_api = None
    export_ctx = None
    render_ctx = None
    fb_thread = None
    started = True  # unintuitive, but reset() is called in the constructor !

    def __init__(self, manager_name='', api_type='FILE'):
        '''
        Initialise the BrlManager by setting its name.

        Returns BrlManager object
        '''
        global FBACK_API
        global PYBRL_API

        if FBACK_API is None:
            # LOAD API TYPES
            # Write conventional xml files and use external process for rendering
            FBACK_API = importlib.import_module('.file_api', 'brlblend.outputs')
            # Access BRLCAD through python bindings
            PYBRL_API = importlib.import_module('.pure_api', 'brlblend.outputs')

        self.fback_api = FBACK_API
        self.pybrl_api = PYBRL_API

        if api_type == 'API' and self.pybrl_api.PYBRL_AVAILABLE:
            Exporter = self.pybrl_api.ApiExportContext

        else:
            Exporter = self.fback_api.FileExportContext

        if manager_name is not '':
            self.manager_name = manager_name
            manager_name = ' (%s)' % manager_name

        self.export_ctx = Exporter()
        self.reset()

    def create_render_context(self, render_type='INT'):
        if BrlManager.RenderEngine is None:
            raise Exception('Error creating BrlManager: Render Engine is not set.')

        self.render_engine = BrlManager.RenderEngine

        if render_type == 'INT' and self.pybrl_api.PYBRL_AVAILABLE:
            Renderer = self.pybrl_api.InternalRenderContext

        else:
            Renderer = self.fback_api.ExternalRenderContext

        self.render_ctx = Renderer()

    def start(self):
        '''
        Start the Context object rendering.

        Returns None
        '''

        if self.started:
            BrlLog('Already rendering!')
            return

        self.started = True

    def stop(self):
        # If we exit the wait loop (user cancelled) and mitsuba is still running, then send SIGINT
        if self.render_ctx.is_running():
            BrlLog("BrlBlend: Stopping..")
            self.render_ctx.render_stop()

    def start_framebuffer_thread(self):
        '''
        Here we start the timer thread for framebuffer updates.
        '''
        scene = BrlManager.CurrentScene
        self.fb_thread.LocalStorage['resolution'] = scene.camera.data.mitsuba_camera.mitsuba_film.resolution(scene)
        self.fb_thread.LocalStorage['RE'] = self.render_engine
        self.fb_thread.LocalStorage['render_ctx'] = self.render_ctx

        if self.render_engine.is_preview:
            self.fb_thread.set_kick_period(2)

        else:
            self.fb_thread.set_kick_period(scene.mitsuba_engine.refresh_interval)

        self.fb_thread.start()

    def reset(self):
        '''
        Stop the current Context from rendering, and reset the
        timer threads.

        Returns None
        '''

        # Firstly stop the renderer
        if self.export_ctx is not None:
            self.export_ctx.exit()

        if not self.started:
            return

        self.started = False

        # Stop the framebuffer update thread
        if self.fb_thread is not None and self.fb_thread.isAlive():
            self.fb_thread.stop()
            self.fb_thread.join()
            # Get the last image
            self.fb_thread.kick(render_end=True)

        # Clean up after last framebuffer update
        if self.export_ctx is not None:
            # cleanup() destroys the Context
            self.export_ctx.cleanup()

        self.fb_thread = BrlFilmDisplay()

        self.ClearActive()
        self.ClearCurrentScene()

    def __del__(self):
        '''
        Gracefully exit() upon destruction
        '''
        self.reset()
