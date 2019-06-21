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

"""HTTP Cache management.

This module configures a cached session for the Requests package.
It allows for filesystem-based caching of HTTP requests.

Requires the 3rd party packages CacheControl and lockfile.
"""

import os
import logging
import requests
import cachecontrol
from cachecontrol.caches import FileCache

from . import appdirs

log = logging.getLogger(__name__)
_session = None  # requests.Session object that's set up for caching by requests_session().


def cache_directory(*subdirs) -> str:
    """Returns an OS-specifc cache location, and ensures it exists.

    Should be replaced with a call to bpy.utils.user_resource('CACHE', ...)
    once https://developer.blender.org/T47684 is finished.

    :param subdirs: extra subdirectories inside the cache directory.

    >>> cache_directory()
    '.../blender_cloud/your_username'
    >>> cache_directory('sub1', 'sub2')
    '.../blender_cloud/your_username/sub1/sub2'
    """

    from . import pillar

    profile = pillar.blender_id_profile()
    if profile:
        username = profile.username
    else:
        username = 'anonymous'

    # TODO: use bpy.utils.user_resource('CACHE', ...)
    # once https://developer.blender.org/T47684 is finished.
    user_cache_dir = appdirs.user_cache_dir(appname='Blender', appauthor=False)
    cache_dir = os.path.join(user_cache_dir, 'blender_cloud', username, *subdirs)

    os.makedirs(cache_dir, mode=0o700, exist_ok=True)

    return cache_dir


def requests_session() -> requests.Session:
    """Creates a Requests-Cache session object."""

    global _session

    if _session is not None:
        return _session

    cache_name = cache_directory('blender_cloud_http')
    log.info('Storing cache in %s' % cache_name)

    _session = cachecontrol.CacheControl(sess=requests.session(),
                                         cache=FileCache(cache_name))

    return _session
