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

bl_info = {
    'name': 'Freen\'s Animation Tools',
    'author': 'Beorn Leonard',
    'version': (2, 2),
    "blender": (2, 64, 0),
    "api": 36157,
    'location': 'View3D > Properties panel > Animation Tools',
    'description': 'A simple panel  for the 3D view properties panel with some common tools used by animators',
    "wiki_url": "",
    "tracker_url": "",
    'category': 'Animation'}

"""
This script simply places some commonly used controls into the 3D view Properies panel. Nothing special, just a timesaver for animators. Includes some changes by Shane Ambler.
"""


import bpy

class AnimPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Freen's Anim Tools"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        screen = context.screen

        row = layout.row()
        row.prop(scene.render, "use_simplify", text="Simplify")
        row.prop(scene.render, "simplify_subdivision", text="levels")

#show_only_render
        row = layout.row()
        row.prop(context.space_data, "show_only_render", text="Hide controllers")


        row = layout.row(align=True)
        row.prop(context.tool_settings, "use_keyframe_insert_auto", text="", toggle=True)
        row.prop(context.user_preferences.edit, "keyframe_new_interpolation_type", text="")
        row = layout.row()
        row.prop_search(scene.keying_sets_all, "active", scene, "keying_sets_all", text="")
        row = layout.row(align=True)
        row.prop(scene, "use_audio_scrub", text="", toggle=True, icon='SPEAKER')
        row.prop(scene, "sync_mode", text="")

        layout.label("Scene duration")
        layout.prop(scene, "use_preview_range", text="Preview", toggle=True)
        row = layout.row(align=True)
        if not scene.use_preview_range:
            row.prop(scene, "frame_start", text="In")
            row.prop(scene, "frame_end", text="Out")
        else:
            row.prop(scene, "frame_preview_start", text="In")
            row.prop(scene, "frame_preview_end", text="Out")

        row = layout.row(align=True)
        row.prop(scene, "frame_current", text="")
        row.separator()
        row.operator("screen.frame_jump", text="", icon='REW').end = False
        row.operator("screen.keyframe_jump", text="", icon='PREV_KEYFRAME').next = False
        if not screen.is_animation_playing:
            # if using JACK and A/V sync:
            #   hide the play-reversed button
            #   since JACK transport doesn't support reversed playback
            if scene.sync_mode == 'AUDIO_SYNC' and context.user_preferences.system.audio_device == 'JACK':
                sub = row.row()
                sub.scale_x = 2.0
                sub.operator("screen.animation_play", text="", icon='PLAY')
            else:
                row.operator("screen.animation_play", text="", icon='PLAY_REVERSE').reverse = True
                row.operator("screen.animation_play", text="", icon='PLAY')
        else:
            sub = row.row()
            sub.scale_x = 2.0
            sub.operator("screen.animation_play", text="", icon='PAUSE')
        row.operator("screen.keyframe_jump", text="", icon='NEXT_KEYFRAME').next = True
        row.operator("screen.frame_jump", text="", icon='FF').end = True

def register():
    bpy.utils.register_class(AnimPanel)

def unregister():
    bpy.utils.unregister_class(AnimPanel)

