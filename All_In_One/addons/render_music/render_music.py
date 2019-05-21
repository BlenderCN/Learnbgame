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

handle = "" #XXX UGLY

@persistent
def play_music(scene):
    global handle

    if scene.render_music.use_play:
        if not hasattr(handle, "status") or (hasattr(handle, "status") and handle.status == False):
            print("Playing elevator music...")
            device = aud.device()
            factory = aud.Factory(scene.render_music.playfile)
            handle = device.play(factory)
            handle.loop_count = -1

@persistent
def kill_music(scene):
    global handle

    if hasattr(handle, "status") and handle.status == True:
        print("Killing elevator music...")
        handle.stop()

@persistent
def end_music(scene):
    
    kill_music(scene)
    
    if scene.render_music.use_end:
        device = aud.device()
        factory = aud.Factory(scene.render_music.endfile)
        handle = device.play(factory)
