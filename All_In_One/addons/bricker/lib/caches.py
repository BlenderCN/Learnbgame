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

# initialize the brick bmesh cache dictionary
bricker_mesh_cache = {}

# initialize the source mesh cache dictionary
bricker_source_mesh_cache = {}

# initialize the BFMCache
bricker_bfm_cache = {}

# cache functions
def cacheExists(cm):
    """check if light or deep matrix cache exists for cmlist item"""
    return bricker_bfm_cache.get(cm.id) is not None or cm.BFMCache not in ("", "null")
