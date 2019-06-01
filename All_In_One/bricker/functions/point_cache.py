# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import os
import re

# Blender imports
import bpy

# Addon imports
from .common import *
from .general import *


def getFirstUncachedFrame(obj, point_cache):
    if point_cache.is_outdated:
        return point_cache.frame_start
    cache_frames = getCachedFrames(obj, point_cache)
    for f in range(point_cache.frame_start, point_cache.frame_end + 1):
        if f not in cache_frames:
            return f
    return point_cache.frame_end + 1


def getCachedFrames(obj, point_cache):
    # send cache files to disk
    use_disk_cache = point_cache.use_disk_cache
    if not use_disk_cache:
        point_cache.use_disk_cache = True

    # helper functions
    def cacheName(ob, point_cache):
        name = point_cache.name
        if name == "":
            name = "".join(["%02X" % ord(c) for c in ob.name])
        return name
    def cachePath():
        file_path = bpy.data.filepath
        path, name = os.path.split(file_path)
        root, ext = os.path.splitext(name)
        return path + os.sep + "blendcache_" + root # need an API call for that


    # get cache paths and pattern vars
    default_path = cachePath()
    cache_path = bpy.path.abspath(point_cache.filepath) if point_cache.use_external else default_path
    name = cacheName(obj, point_cache)
    index = "%02i" % point_cache.index

    # protect against nonexistent cache
    if not os.path.exists(cache_path):
        return []

    # assemble list of cached frames
    pattern = re.compile(name + "_([0-9]+)_" + index + "\.bphys")
    cache_frames = []
    for cache_file in sorted(os.listdir(cache_path)):
        match = pattern.match(cache_file)
        if match:
            cache_frame = int(match.groups()[0])
            cache_frames.append(cache_frame)  # also can include 'cache_file' cache file name in tuple if desired
    cache_frames.sort()

    # send cache files back to memory
    if not use_disk_cache:
        point_cache.use_disk_cache = False

    return cache_frames
