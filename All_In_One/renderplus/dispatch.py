# ------------------------------------------------------------------------------
# LICENSE
# ------------------------------------------------------------------------------
# Render+ - Blender addon
# (c) Copyright Diego Garcia Gangl (januz) - 2014, 2015
# <diego@sinestesia.co>
# ------------------------------------------------------------------------------
# This file is part of Render+
#
# Render+ is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ------------------------------------------------------------------------------

import os
import logging

import bpy
from bpy.app.handlers import persistent


from . import utils
from . import stats
from . import notifications
from . import actions
from . import slots

import renderplus.batch_render.control as batch_control
import renderplus.batch_render.state   as batch_state


# ------------------------------------------------------------------------------
#  INTERNAL VARIABLES
# ------------------------------------------------------------------------------

# State
rendering = False

# Logging
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
#  CALLBACKS
# ------------------------------------------------------------------------------

@persistent
def on_file_open(dummy):
    """ Make sure pre/post actions are disabled for security"""

    settings = bpy.context.scene.renderplus

    if settings:
        # Don't use R+ for evil!
        settings.pre_enabled = False
        settings.post_enabled = False
        settings.off_options = 'DISABLED'

        # Build render slots
        if len(settings.slots) == 0:
            slots.generate_list()
        else:
            # They should be disabled by default
            for slot in settings.slots:
                slot.is_used = False

    # Reset batch state
    batch_control.running = False
    batch_control.errors = {}

    # Check for running batch
    if bpy.data.is_saved:
        batch_name = bpy.path.basename(bpy.data.filepath)
        state_file = batch_control.get_temp_path('_state.json')
        proc_file = batch_control.get_temp_path('.pid')

        try:
            batch_state.from_file(state_file)
        except FileNotFoundError:
            return
        else:
            # Check for an actual process
            if not os.path.isfile(proc_file):
                log.debug(('Found state file but no batch process. '
                           'Going to clean.'))
                batch_control.clean()
                return

            log.debug('Found running batch')
            batch_control.running = True
            batch_state.watch_file()


@persistent
def on_cancel(dummy):
    """ Clean up if render is cancelled """

    global rendering
    rendering = False

    stats.cancel()

    log.debug('Render Cancel Called')


@persistent
def on_post_render(scene):
    """ Change data for animation renders """

    log.debug('Post render called at frame: ' + str(scene.frame_current))

    try:
        stats.update_frame()
    except AttributeError:
        # on_post is sometimes called after on_complete, which will
        # make this throw an AttributeError. But it could be something else
        # too.
        log.debug('AttributeError in stats. Check for on_complete.')

    utils.force_redraw()


@persistent
def on_complete(scene):
    """ Call the different functions after rendering """

    global rendering

    settings = scene.renderplus

    log.debug('Render Complete called')


    # --------------------------------------------------------------------------
    #  CLEAN UP

    rendering = False
    stats.stop()
    utils.force_redraw()
    slots.update_list()

    # --------------------------------------------------------------------------
    #  NOTIFICATIONS

    if settings.notifications_desktop:
        notifications.desktop()

    if settings.notifications_sound:
        notifications.sound()

    if settings.notifications_mail:
        notifications.mail()

    # --------------------------------------------------------------------------
    #  ACTIONS

    if settings.autosave:
        actions.autosave()

    if settings.post_enabled:
        actions.run('POST')

    if settings.off_options != "DISABLED":
        actions.power_off()


@persistent
def on_scene_update(dummy):
    """ Detect scene changes to update slots """

    if len(bpy.context.scene.renderplus.slots) == 0:
        slots.generate_list()


@persistent
def on_pre_render(scene):
    """ Call the different functions before rendering or frame change """

    global rendering

    settings = scene.renderplus

    log.debug('Pre-Render called at frame: ' + str(scene.frame_current))

    notifications.error = None

    # --------------------------------------------------------------------------
    #  BATCH
    if batch_control.running:
        return

    if not rendering:
        stats.start()

    if settings.pre_enabled:
        if not rendering:
            actions.run('PRE')

    rendering = True
