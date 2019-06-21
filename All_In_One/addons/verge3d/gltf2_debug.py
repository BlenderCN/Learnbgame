# Copyright (c) 2017 The Khronos Group Inc.
# Modifications Copyright (c) 2017-2018 Soft8Soft LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#
# Imports
#

import time

#
# Globals
#

g_profile_started = False
g_profile_start = 0.0
g_profile_end = 0.0
g_profile_delta = 0.0

g_output_levels = ['ERROR', 'WARNING', 'INFO', 'PROFILE', 'DEBUG', 'VERBOSE']
g_current_output_level = 'DEBUG'

#
# Functions
#

def set_output_level(level):
    """
    Allows to set an output debug level.
    """

    global g_current_output_level

    if g_output_levels.index(level) < 0:
        return

    g_current_output_level = level


def printLog(level, output):
    """
    Prints to Blender console with a given header and output.
    """

    global g_output_levels
    global g_current_output_level

    if g_output_levels.index(level) > g_output_levels.index(g_current_output_level):
        return

    print(level + ': ' + output)


def print_newline():
    """
    Prints a new line to Blender console.
    """
    print()


def print_timestamp(label = None):
    """
    Print a timestamp to Blender console.
    """
    output = 'Timestamp: ' + str(time.time())

    if label is not None:
        output = output + ' (' + label + ')'

    printLog('PROFILE', output)


def profile_start():
    """
    Start profiling by storing the current time.
    """
    global g_profile_start
    global g_profile_started

    if g_profile_started:
        printLog('ERROR', 'Profiling already started')
        return

    g_profile_started = True

    g_profile_start = time.time()


def profile_end(label = None):
    """
    Stops profiling and printing out the delta time since profile start.
    """
    global g_profile_end
    global g_profile_delta
    global g_profile_started

    if not g_profile_started:
        printLog('ERROR', 'Profiling not started')
        return

    g_profile_started = False

    g_profile_end = time.time()
    g_profile_delta = g_profile_end - g_profile_start

    output = 'Delta time: ' + str(g_profile_delta)

    if label is not None:
        output = output + ' (' + label + ')'

    printLog('PROFILE', output)
