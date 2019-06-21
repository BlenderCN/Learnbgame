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

import logging
import os
from subprocess import Popen

import bpy

from . import data
from . import utils


# ------------------------------------------------------------------------------
#  INTERNAL VARIABLES
# ------------------------------------------------------------------------------

# Logger
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
#  FUNCTIONS
# ------------------------------------------------------------------------------

def power_off(option = None):
    """ Run the power off commands """

    if not option:
        settings = bpy.context.scene.renderplus
        option = settings.off_options[:]

    command = {}
    command['SLEEP'] = {}
    command['OFF'] = {}

    # Sleep
    command['SLEEP']['Darwin'] = 'pmset sleepnow'
    command['SLEEP']['Windows'] = ('start /min ""'
                                   ' %windir%\System32\\rundll32.exe'
                                   ' PowrProf.dll,SetSuspendState 0,1,0')

    command['SLEEP']['Linux'] = 'systemctl suspend'

    # Power off
    command['OFF']['Darwin'] = ('osascript -e \'tell application'
                                '"System Events"\' -e \'shut down\' '
                                '-e \'end tell\'')

    command['OFF']['Windows'] = 'shutdown -s'
    command['OFF']['Linux'] = 'systemctl poweroff'

    Popen(command[option][utils.sys], shell=True)
    
    # Disable it for next render to prevent user errors
    if not option:
        settings.off_options = "DISABLED"


def autosave():
    """ Auto-save image renders """

    scene = bpy.context.scene
    use_extension = scene.render.use_file_extension
    use_overwrite = scene.render.use_overwrite

    output_path = bpy.path.abspath(scene.render.filepath)
    extension = scene.render.file_extension
    base_name = os.path.splitext(output_path)[0]

    result = bpy.data.images['Render Result']

    if scene.render.is_movie_format:
        # Blender already autosaves animations
        return False

    if not result:
        # Saving errors
        log.info("Could not autosave render!")
        return False

    if use_extension:
        # Make sure the file has an extension
        final_path = base_name + extension
    elif os.path.splitext(output_path)[1]:
        final_path = base_name + os.path.splitext(output_path)[1]
    else:
        final_path = base_name

    if not use_overwrite:
        # Add duplicate number to filename
        # so it doesn't get overwritten
        dupe_number = 1

        while os.path.isfile(final_path):
            # Deconstruct again
            base, ext = os.path.splitext(final_path)

            # Removing the old number
            old_dupe = '_#' + str(dupe_number - 1)
            base = base.replace(old_dupe, '')

            final_path = str.format('{0}_#{1}{2}', base, dupe_number, ext)

            dupe_number += 1

    result.save_render(final_path)
    log.debug('Autosaved to ' + final_path)


def run(when):
    """ Run post/pre render commands or scripts """

    if when == 'POST':
        settings = bpy.context.scene.renderplus.post_settings
    else:
        settings = bpy.context.scene.renderplus.pre_settings

    if settings.option == 'command':
        log.debug('Running command: ' + settings.command + ' at ' + when)
        return Popen(settings.command, shell=True)
    else:
        log.debug('Running script: ' + settings.script + ' at ' + when)
        log.debug(bpy.data.texts[settings.script].as_string())

        code = bpy.data.texts[settings.script].as_string()
        return exec(code)
