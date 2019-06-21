# -------------------------------------------------------------------------
# LICENSE
# -------------------------------------------------------------------------
# Render+ - Blender addon
# (c) Copyright Diego Garcia Gangl (januz) - 2014, 2015
# <diego@sinestesia.co>
# -------------------------------------------------------------------------
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
# -------------------------------------------------------------------------

import time
import logging
import csv

import bpy

from . import utils


# -----------------------------------------------------------------------------
#  INTERNAL VARIABLES
# -----------------------------------------------------------------------------

# Logger
log = logging.getLogger(__name__)


# Statsdata instance
instance = None

# Detect if it's the first render
run_once = False


# -----------------------------------------------------------------------------
#  STATS DATA
# -----------------------------------------------------------------------------

class StatsData(object):

    """Container for statistics data

    This class contains and calculates all data related to stats.
    There's no need to instantiate this directly, use the convenience
    functions below.

    """

    def __init__(self):

        # List of render time per frames
        self.frame_times = []

        # Time it took for the last frame to render
        self.last_frame_time = time.time()

        # Timestamp for render
        self.start_time = time.time()

        log.debug('Stats started.')
        log.debug('start_time is: ' + str(self.start_time))

    def update_frame(self):
        """ Update time on a frame """

        current_time = time.time() - self.last_frame_time
        scene = bpy.context.scene

        self.frame_times.append((scene.frame_current, current_time))
        self.last_frame_time = time.time()

        log.debug('Updating frame time: ' + str(current_time))

    def total(self):
        """ Calculate complete rendertime """

        total = time.time() - self.start_time

        log.debug('Total Rendertime: ' + str(total))

        return total

    def average_frame(self, rendertime):
        """ Calculate average frame render time """

        average = rendertime / len(self.frame_times)

        log.debug('Total Rendertime: ' + str(average))

        return average

    def slowest_frame(self):
        """ Calculate slowest frame render """

        slowest = [0, 0]

        for frame in self.frame_times:
            if frame[1] > slowest[1]:
                slowest = frame

        log.debug('Slowest frame: ' + str(slowest))

        return slowest

    def fastest_frame(self):
        """ Calculate fastest frame render """

        fastest = [999999, 999999]

        for frame in self.frame_times:
            if frame[1] < fastest[1]:
                fastest = frame

        log.debug('Fastest frame: ' + str(fastest))

        return fastest

    def remaining(self):
        """ Estimate remaining time for animation renders """

        total = 0
        scene = bpy.context.scene

        for frame in self.frame_times:
            total += frame[1]

        avg = total / len(self.frame_times)
        frames_to_go = (scene.frame_end) - scene.frame_current
        remaining = avg * frames_to_go

        log.debug('Remaining time: ' + str(remaining))

        return remaining

    def is_animation(self):
        """ Determine if we're rendering animation  """

        return (len(self.frame_times) > 1)


# -----------------------------------------------------------------------------
#  CONVENIENCE FUNCTIONS
# -----------------------------------------------------------------------------

def start():
    """ Start recording time for stats """

    global instance
    global run_once

    settings = bpy.context.scene.renderplus.stats

    settings.total = 0
    settings.average = 0
    settings.slowest = (0, 0)
    settings.fastest = (0, 0)

    if not run_once:
        run_once = True

    instance = StatsData()


def stop():
    """ Stop recording the stats and calculate them """

    global instance
    settings = bpy.context.scene.renderplus.stats

    # Calculate all data
    settings.total = instance.total()

    if instance.is_animation():
        # Slowest frame
        settings.slowest = instance.slowest_frame()

        # Fastest frame
        settings.fastest = instance.fastest_frame()

        # Remaining Time
        settings.average = instance.average_frame(settings.total)

        if settings.save_file:

            export_csv(utils.blendpath('_stats.csv'))

    instance = None
    log.debug('Stats stopped')


def is_running():
    """ Detect if stats are still gathering data """

    global instance
    return (instance is not None)


def cancel():
    """ Cancel running stats """

    global instance
    instance = None

    log.debug('Stats cancelled')


def update_frame():
    """ Update the current frame render time  """

    settings = bpy.context.scene.renderplus.stats

    instance.update_frame()

    if instance.is_animation():
        settings.remaining = instance.remaining()


# -----------------------------------------------------------------------------
#  PRINT TO CSV
# -----------------------------------------------------------------------------

def export_csv(filepath):
    """ Export stats data to a csv file """

    global instance

    settings = bpy.context.scene.renderplus.stats

    fastest = '{1} (#{0})'.format(
        int(settings.fastest[0]), utils.time_format(settings.fastest[1]))
    slowest = '{1} (#{0})'.format(
        int(settings.slowest[0]), utils.time_format(settings.slowest[1]))

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(['Frame', 'Time'])

        for frame in instance.frame_times:
            writer.writerow([frame[0], utils.time_format(frame[1])])

        writer.writerow(['Fastest', fastest])
        writer.writerow(['Slowest', slowest])
        writer.writerow(['Average', utils.time_format(settings.average)])
        writer.writerow(['Total', utils.time_format(settings.total)])
