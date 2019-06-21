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


bl_info = {
    "name": "Render Quack",
    "description": "Plays a sound when rendering is complete.",
    "author": "Jason van Gumster (Fweeb), Northern3D",
    "version": (1, 6, 1),
    "blender": (2, 79, 0),
    "location": "Properties > Render",
    "warning": "",
    "wiki_url": "https://github.com/Northern3D/blender_quack/",
    "tracker_url": "https://github.com/Northern3D/blender_quack/issues",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    imp.reload(render_music)
else:
    from . import render_music

import bpy, os
from bpy.types import AddonPreferences

# UI

class RenderMusicProperties(AddonPreferences):
    bl_idname = __package__
    scriptdir = bpy.path.abspath(os.path.dirname(__file__))
    #XXX Sound CC-0, Matthias Fath, https://freesound.org/people/LamaMakesMusic/sounds/403507/
    endfile = bpy.props.StringProperty(
        name = "End Sound",
        description = "Sound to play when rendering completes",
        subtype = 'FILE_PATH',
        default = scriptdir + "/end.mp3")
    use_end = bpy.props.BoolProperty(
        name = "Play sound upon render completion",
        description = "Enable the ability to play a sound when a render completes",
        default = True)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Render Quack Preferences")
        split = layout.split(percentage=0.3)
        col = split.column()
        col.prop(self, "use_end", text="End Sound")
        col = split.column()
        col.prop(self, "endfile", text="")


def render_panel(self, context):
    user_prefs = context.user_preferences
    addon_prefs = user_prefs.addons[__package__].preferences

    layout = self.layout
    layout.prop(addon_prefs, "use_end")


# Registration

def register():
    bpy.utils.register_class(RenderMusicProperties)
    bpy.types.RENDER_PT_render.append(render_panel)

    bpy.types.RenderSettings.music_handle = None
    bpy.app.handlers.render_complete.append(render_music.end_music)


def unregister():
    bpy.app.handlers.render_complete.remove(render_music.end_music)

    bpy.types.RENDER_PT_render.remove(render_panel)


if __name__ == '__main__':
    register()
