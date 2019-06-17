'''
Copyright (C) 2015-2018 Team C All Rights Reserved

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    'name': 'BoxCutter',
    'description': 'BoxCutter 7.1.2: BetaScythe PHASE: Custom Paw',
    'author': 'AR, MX, proxe, JL, EA, dairin1d, AgentX, RedFrost',
    'version': (0, 7, 1, 2),
    'blender': (2, 80, 0),
    'location': 'View3D',
    'wiki_url': 'https://masterxeon1001.com/2019/02/15/boxcutter-711-release-notes/',
    'category': '3D View'}

from . addon import operator, panel, keymap, pie, preference, property, topbar


def register():
    preference.register()
    property.register()
    keymap.register()

    operator.register()
    panel.register()
    pie.register()
    topbar.register()


def unregister():
    topbar.unregister()
    pie.unregister()
    panel.unregister()
    operator.unregister()

    keymap.unregister()
    property.unregister()
    preference.unregister()
