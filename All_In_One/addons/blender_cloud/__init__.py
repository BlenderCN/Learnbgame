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

# <pep8 compliant>

bl_info = {
    'name': 'Blender Cloud',
    "author": "Sybren A. Stüvel, Francesco Siddi, Inês Almeida, Antony Riakiotakis",
    'version': (1, 7, 5),
    'blender': (2, 77, 0),
    'location': 'Addon Preferences panel, and Ctrl+Shift+Alt+A anywhere for texture browser',
    'description': 'Texture library browser and Blender Sync. Requires the Blender ID addon '
                   'and Blender 2.77a or newer.',
    'wiki_url': 'https://wiki.blender.org/index.php/Extensions:2.6/Py/'
                'Scripts/System/BlenderCloud',
    'category': 'System',
}

import logging

# Support reloading
if 'pillar' in locals():
    import importlib

    wheels = importlib.reload(wheels)
    wheels.load_wheels()

    pillar = importlib.reload(pillar)
    cache = importlib.reload(cache)
else:
    from . import wheels

    wheels.load_wheels()

    from . import pillar, cache

log = logging.getLogger(__name__)


def register():
    """Late-loads and registers the Blender-dependent submodules."""

    import sys

    _monkey_patch_requests()

    # Support reloading
    if '%s.blender' % __name__ in sys.modules:
        import importlib

        def reload_mod(name):
            modname = '%s.%s' % (__name__, name)
            try:
                old_module = sys.modules[modname]
            except KeyError:
                # Wasn't loaded before -- can happen after an upgrade.
                new_module = importlib.import_module(modname)
            else:
                new_module = importlib.reload(old_module)

            sys.modules[modname] = new_module
            return new_module

        reload_mod('blendfile')
        reload_mod('home_project')
        reload_mod('utils')

        async_loop = reload_mod('async_loop')
        flamenco = reload_mod('flamenco')
        attract = reload_mod('attract')
        texture_browser = reload_mod('texture_browser')
        settings_sync = reload_mod('settings_sync')
        image_sharing = reload_mod('image_sharing')
        blender = reload_mod('blender')
    else:
        from . import (blender, texture_browser, async_loop, settings_sync, blendfile, home_project,
                       image_sharing, attract, flamenco)

    async_loop.setup_asyncio_executor()
    async_loop.register()

    flamenco.register()
    attract.register()
    texture_browser.register()
    settings_sync.register()
    image_sharing.register()
    blender.register()

    blender.handle_project_update()


def _monkey_patch_requests():
    """Monkey-patch old versions of Requests.

    This is required for the Mac version of Blender 2.77a.
    """

    import requests

    if requests.__build__ >= 0x020601:
        return

    log.info('Monkey-patching requests version %s', requests.__version__)
    from requests.packages.urllib3.response import HTTPResponse
    HTTPResponse.chunked = False
    HTTPResponse.chunk_left = None


def unregister():
    from . import (blender, texture_browser, async_loop, settings_sync, image_sharing, attract,
                   flamenco)

    image_sharing.unregister()
    attract.unregister()
    settings_sync.unregister()
    blender.unregister()
    texture_browser.unregister()
    async_loop.unregister()
    flamenco.unregister()
