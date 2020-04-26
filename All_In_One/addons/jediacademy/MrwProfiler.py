# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import time

class SimpleProfiler:
    def __init__(self, printOutput):
        self.startTimes = {}
        self.printOutput = printOutput
    
    # starts a clock of the given name
    def start(self, name):
        self.startTimes[name] = time.clock()
        if self.printOutput:
            print("Start: {}".format(name))
    
    # stop the clock of the given name and returns its value, or -1 if no such clock exists.
    def stop(self, name):
        if name not in self.startTimes:
            return -1
        timeTaken = time.clock() - self.startTimes[name]
        del self.startTimes[name]
        if self.printOutput:
            print("Done: {} - time taken: {:.3f}s".format(name, timeTaken))
        return timeTaken
