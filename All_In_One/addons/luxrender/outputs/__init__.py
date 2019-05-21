# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
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
import time, threading, os

import bpy

from ..extensions_framework import log
from ..extensions_framework.util import TimerThread, format_elapsed_time

# This def ia above the following import statements for a reason!
def LuxLog(*args, popup=False):
    """
    Send string to AF log, marked as belonging to LuxRender module.
    Accepts variable args (can be used as pylux.errorHandler)
    """
    if len(args) > 0:
        log(' '.join(['%s' % a for a in args]), module_name='Lux', popup=popup)

# CHOOSE API TYPE
# Write conventional lx* files and use pylux to manage lux process or external process
from ..outputs import file_api
# Write material definitions to LBM2 format
from ..outputs import lbm2_api
# Write material definitions to LXM format
from ..outputs import lxm_api
# Access lux only through pylux bindings
from ..outputs import pure_api


class LuxAPIStats(TimerThread):
    """
    Periodically get lux stats
    """

    KICK_PERIOD = 1

    stats_string = ''

    def kick(self):
        ctx = self.LocalStorage['lux_context']
        ctx.updateStatisticsWindow()
        self.stats_string = ctx.getAttribute('renderer_statistics_formatted_short', '_recommended_string')


class LuxFilmDisplay(TimerThread):
    """
    Periodically update render result with Lux's framebuffer
    """

    STARTUP_DELAY = 2  # Add additional time to first KICK PERIOD

    def kick(self, render_end=False):
        if 'RE' in self.LocalStorage.keys():
            p_stats = ''
            direct_transfer = False

            if not bpy.app.background or render_end:

                xres = yres = -1

                if 'lux_context' in self.LocalStorage.keys() and self.LocalStorage['lux_context'].statistics(
                        'sceneIsReady') > 0.0:
                    self.LocalStorage['lux_context'].updateFramebuffer()
                    xres = int(self.LocalStorage['lux_context'].getAttribute('film', 'xResolution'))
                    yres = int(self.LocalStorage['lux_context'].getAttribute('film', 'yResolution'))
                    ctx = self.LocalStorage['lux_context']
                    ctx.updateStatisticsWindow()
                    p_stats = ' - %s' % ctx.getAttribute('renderer_statistics_formatted_short', '_recommended_string')
                    direct_transfer = 'blenderCombinedDepthRects' in dir(self.LocalStorage['lux_context'])
                    direct_transfer &= 'integratedimaging' in self.LocalStorage.keys() and self.LocalStorage[
                        'integratedimaging']

                if 'resolution' in self.LocalStorage.keys():
                    xres, yres = self.LocalStorage['resolution']

                if xres == -1 or yres == -1:
                    err_msg = 'ERROR: Cannot not load render result: resolution unknown. LuxFilmThread will terminate'
                    LuxLog(err_msg)
                    self.stop()
                    return

                if render_end:
                    LuxLog('Final render result (%ix%i%s)' % (xres, yres, p_stats))
                else:
                    LuxLog('Updating render result (%ix%i%s)' % (xres, yres, p_stats))

                result = self.LocalStorage['RE'].begin_result(0, 0, xres, yres)

                if result is None:
                    err_msg = 'ERROR: Cannot not load render result: begin_result() returned None.\
                     LuxFilmThread will terminate'
                    LuxLog(err_msg)
                    self.stop()
                    return

                lay = result.layers[0]

                if direct_transfer:
                    # use the framebuffer direct from pylux using a special method
                    # for this purpose, which saves doing a lot of array processing
                    # in python
                    ctx = self.LocalStorage['lux_context']

                    # the fast buffer approach only works if we set all render layers and all passes
                    # so for now, only use optimized route if one layer and one pass
                    if hasattr(ctx, 'blenderCombinedDepthBuffers') and len(result.layers) == 1 and len(
                            result.layers[0].passes) == 1:
                        # use fast buffers
                        pb, zb = ctx.blenderCombinedDepthBuffers()
                        if bpy.app.version < (2, 74, 4 ):
                            result.layers.foreach_set("rect", pb)
                            lay.passes.foreach_set("rect", zb)
                        else:
                            result.layers[0].passes.foreach_set("rect", pb)

                    else:
                        cr, zr = ctx.blenderCombinedDepthRects()
                        if bpy.app.version < (2, 74, 4 ):
                            lay.rect = cr # combined
                            lay.passes[0].rect = zr # z
                        else:
                            lay.passes[0].rect = cr # combined
                            lay.passes[1].rect = zr # z

                elif os.path.exists(self.LocalStorage['RE'].output_file):
                    lay.load_from_file(self.LocalStorage['RE'].output_file)
                else:
                    err_msg = 'ERROR: Could not load render result from %s' % self.LocalStorage['RE'].output_file
                    LuxLog(err_msg)
                self.LocalStorage['RE'].end_result(result, 0) if bpy.app.version > (2, 63, 17 ) else self.LocalStorage[
                    'RE'].end_result(result)  # cycles tiles adaption
        else:
            err_msg = 'ERROR: LuxFilmThread started with insufficient parameters. LuxFilmThread will terminate'
            LuxLog(err_msg)
            self.stop()
            return


class LuxManager(object):
    """
    Manage a pylux.Context object for rendering.

    Objects of this class are responsible for the life cycle of
    a pylux.Context object, ensuring proper initialisation, usage
    and termination.

    Additionally, LuxManager objects will also spawn timer threads
    in order to update the rendering statistics and image framebuffer.
    """

    ActiveManager = None

    @staticmethod
    def SetActive(LM):
        LuxManager.ActiveManager = LM

    @staticmethod
    def GetActive():
        return LuxManager.ActiveManager

    @staticmethod
    def ClearActive():
        LuxManager.ActiveManager = None

    CurrentScene = None

    @staticmethod
    def SetCurrentScene(scene):
        LuxManager.CurrentScene = scene

    @staticmethod
    def ClearCurrentScene():
        LuxManager.CurrentScene = None

    context_count = 0

    @staticmethod
    def get_context_number():
        """
        Give each context a unique serial number by keeping
        count in a static member of LuxManager
        """

        LuxManager.context_count += 1
        return LuxManager.context_count

    lux_context = None
    stats_thread = None
    fb_thread = None
    started = True  # unintuitive, but reset() is called in the constructor !

    def __init__(self, manager_name='', api_type='FILE'):
        """
        Initialise the LuxManager by setting its name, the pylux API type.

        Returns LuxManager object
        """

        # NB: Should not be refactored into a dict switch as it will
        # lead to undefined context in case of pylux module import fail.
        if api_type == 'FILE':
            Context = file_api.Custom_Context
        elif api_type == 'API':
            Context = pure_api.Custom_Context
        elif api_type == 'LBM2':
            Context = lbm2_api.Custom_Context
        elif api_type == 'LXM':
            Context = lxm_api.Custom_Context
        else:
            raise Exception('Unknown exporter API type "%s"' % api_type)

        if manager_name is not '':
            manager_name = ' (%s)' % manager_name

        self.lux_context = Context('LuxContext %04i%s' %
                                   (LuxManager.get_context_number(),
                                    manager_name))
        self.reset()

    def start(self):
        """
        Start the pylux.Context object rendering. This is achieved
        by calling its worldEnd() method.

        Returns None
        """

        if self.started:
            LuxLog('Already rendering!')
            return

        self.started = True

        # Wait until scene is fully parsed before returning control
        while self.lux_context.statistics('sceneIsReady') != 1.0:
            wait_timer = threading.Timer(0.3, self.null_wait)
            wait_timer.start()

            if wait_timer.isAlive():
                wait_timer.join()

    def null_wait(self):
        pass

    def start_worker_threads(self, RE):
        """
        Here we start the timer threads for stats and framebuffer updates.
        """
        self.stats_thread.start()
        self.fb_thread.LocalStorage['RE'] = RE
        self.fb_thread.start()

    def reset(self):
        """
        Stop the current Context from rendering, and reset the
        timer threads.

        Returns None
        """

        # Firstly stop the renderer
        if self.lux_context is not None:
            self.lux_context.exit()
            self.lux_context.wait()

        # Stop the stats thread
        if self.stats_thread is not None and self.stats_thread.isAlive():
            self.stats_thread.stop()
            self.stats_thread.join()

        self.stats_thread = LuxAPIStats(
            {'lux_context': self.lux_context}
        )

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
        if self.lux_context is not None:
            # and disconnect all servers
            for server_info in self.lux_context.getRenderingServersStatus():
                self.lux_context.removeServer(server_info.name)

            # cleanup() destroys the pylux Context
            self.lux_context.cleanup()

        self.fb_thread = LuxFilmDisplay(
            {'lux_context': self.lux_context}
        )

        self.ClearActive()
        self.ClearCurrentScene()

    def __del__(self):
        """
        Gracefully exit() lux upon destruction
        """
        self.reset()
