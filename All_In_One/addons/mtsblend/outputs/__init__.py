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
import importlib

import bpy

from ..extensions_framework import log
from ..extensions_framework.util import TimerThread


def MtsLog(*args, popup=False):
    '''
    Send string to AF log, marked as belonging to Mitsuba module.
    Accepts variable args
    '''
    if len(args) > 0:
        log(' '.join(['%s' % a for a in args]), module_name='Mitsuba', popup=popup)


class MtsFilmDisplay(TimerThread):
    '''
    Periodically update render result with Mitsuba's framebuffer
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
                    err_msg = 'ERROR: Cannot not load render result: resolution unknown. MtsFilmThread will terminate'
                    MtsLog(err_msg)
                    self.stop()
                    return

                if render_end:
                    MtsLog('Final render result (%ix%i)' % (xres, yres))

                elif self.LocalStorage['render_ctx'].RENDER_API_TYPE == 'EXT':
                    MtsLog('Updating render result (%ix%i)' % (xres, yres))

                result = self.LocalStorage['RE'].begin_result(0, 0, xres, yres)

                if result is None:
                    err_msg = 'ERROR: Cannot not load render result: begin_result() returned None. MtsFilmThread will terminate'
                    MtsLog(err_msg)
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
                    MtsLog(err_msg)

                self.LocalStorage['RE'].end_result(result, 0)

        else:
            err_msg = 'ERROR: MtsFilmThread started with insufficient parameters. MtsFilmThread will terminate'
            MtsLog(err_msg)
            self.stop()
            return

FBACK_API = None
PYMTS_API = None


class MtsManager:
    '''
    Manage a Context object for rendering.

    Objects of this class are responsible for the life cycle of
    a Context object, ensuring proper initialisation, usage
    and termination.

    Additionally, MtsManager objects will also spawn timer threads
    in order to update the image framebuffer.
    '''

    ActiveManager = None

    @staticmethod
    def SetActive(MM):
        MtsManager.ActiveManager = MM

    @staticmethod
    def GetActive():
        return MtsManager.ActiveManager

    @staticmethod
    def ClearActive():
        MtsManager.ActiveManager = None

    RenderEngine = None

    @staticmethod
    def SetRenderEngine(engine):
        MtsManager.RenderEngine = engine

    @staticmethod
    def ClearRenderEngine():
        MtsManager.RenderEngine = None

    CurrentScene = None

    @staticmethod
    def SetCurrentScene(scene):
        MtsManager.CurrentScene = scene

    @staticmethod
    def ClearCurrentScene():
        MtsManager.CurrentScene = None

    context_count = 0

    @staticmethod
    def get_context_number():
        '''
        Give each context a unique serial number by keeping
        count in a static member of MtsManager
        '''

        MtsManager.context_count += 1
        return MtsManager.context_count

    manager_name = ''
    render_engine = None
    fback_api = None
    pymts_api = None
    export_ctx = None
    render_ctx = None
    fb_thread = None
    started = True  # unintuitive, but reset() is called in the constructor !

    def __init__(self, manager_name='', api_type='FILE'):
        '''
        Initialise the MtsManager by setting its name.

        Returns MtsManager object
        '''
        global FBACK_API
        global PYMTS_API

        if FBACK_API is None:
            # LOAD API TYPES
            # Write conventional xml files and use external process for rendering
            FBACK_API = importlib.import_module('.file_api', 'mtsblend.outputs')
            # Access Mitsuba through python bindings
            PYMTS_API = importlib.import_module('.pure_api', 'mtsblend.outputs')

        self.fback_api = FBACK_API
        self.pymts_api = PYMTS_API

        if api_type == 'API' and self.pymts_api.PYMTS_AVAILABLE:
            Exporter = self.pymts_api.ApiExportContext

        else:
            Exporter = self.fback_api.FileExportContext

        if manager_name is not '':
            self.manager_name = manager_name
            manager_name = ' (%s)' % manager_name

        self.export_ctx = Exporter()
        self.reset()

    def create_render_context(self, render_type='INT'):
        if MtsManager.RenderEngine is None:
            raise Exception('Error creating MtsManager: Render Engine is not set.')

        self.render_engine = MtsManager.RenderEngine

        if render_type == 'INT' and self.pymts_api.PYMTS_AVAILABLE:
            Renderer = self.pymts_api.InternalRenderContext

        else:
            Renderer = self.fback_api.ExternalRenderContext

        self.render_ctx = Renderer()

    def start(self):
        '''
        Start the Context object rendering.

        Returns None
        '''

        if self.started:
            MtsLog('Already rendering!')
            return

        self.started = True

    def stop(self):
        # If we exit the wait loop (user cancelled) and mitsuba is still running, then send SIGINT
        if self.render_ctx.is_running():
            MtsLog("MtsBlend: Stopping..")
            self.render_ctx.render_stop()

    def start_framebuffer_thread(self):
        '''
        Here we start the timer thread for framebuffer updates.
        '''
        scene = MtsManager.CurrentScene
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

        self.fb_thread = MtsFilmDisplay()

        self.ClearActive()
        self.ClearCurrentScene()

    def __del__(self):
        '''
        Gracefully exit() upon destruction
        '''
        self.reset()
