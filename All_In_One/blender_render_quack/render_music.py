# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


import bpy, aud
from bpy.app.handlers import persistent

@persistent
def end_music(scene):
    handle = bpy.types.RenderSettings.music_handle
    addon_prefs = bpy.context.user_preferences.addons[__package__].preferences
    
    if addon_prefs.use_end:
        device = aud.device()
        factory = aud.Factory(addon_prefs.endfile)
        bpy.types.RenderSettings.music_handle = device.play(factory)
