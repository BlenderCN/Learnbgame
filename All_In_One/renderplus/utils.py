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
import platform
import time

from datetime import timedelta

import bpy


# OS being used
sys = platform.system()


def show_message(message, wrap=80, pop_type='ERROR'):
    """
        Show messages in a popup.
        Modified from original code by Jon Denning
    """

    lines = []

    if wrap > 0:
        while len(message) > wrap:
            i = message.rfind(' ', 0, wrap)
            if i == -1:
                lines += [message[:wrap]]
                message = message[wrap:]
            else:
                lines += [message[:i]]
                message = message[i + 1:]
    if message:
        lines += [message]

    if pop_type == 'ERROR':
        title = 'Error'
        icon = 'ERROR'
    else:
        title = 'Help & Tips'
        icon = 'HELP'

    def draw(self, context):
        for line in lines:
            self.layout.label(line)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
    return


def force_redraw():
    """
        Forces the UI to redraw

        This makes me cry at night but looks like
        it's the only way to do it.

        Modified from a snippet by CoDEManX in the
        bf-python list to work in a limited context.
    """

    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'PROPERTIES':
                for region in area.regions:
                    try:
                        scene = bpy.context.scene 
                        scene.frame_end = scene.frame_end
                        region.tag_redraw()
                    except AttributeError:
                        pass
                    return


def path(*args):
    """ Return the path relative to the script. Don't include leading slash """

    return os.path.join(os.path.dirname(__file__), *args)


def sane_path(path):
    """ Return a normalized path """

    return os.path.normpath(os.path.abspath(bpy.path.abspath(path)))


def blendpath(suffix=False):
    """ Get filepath of the current blend file with an optional suffix """

    base = bpy.path.abspath("//")
    name = os.path.basename(bpy.data.filepath)

    if not name:
        name = 'Untitled.blend'

    if suffix:
        name += suffix

    return os.path.join(base, name)


def current_time():
    """ Return the current time and date formatted """
    
    return time.strftime('%d %b, %Y at %H:%M') 


def time_format(time):
    """ Formats a R+ time to be HH:MM:SS.UU """

    output = str(timedelta(seconds=time))
    return output[:10]
