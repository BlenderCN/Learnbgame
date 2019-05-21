# Boomsmash renders a GL preview based on preferred Tube/Helga settings
# Copyright (C) 2012  Bassam Kurdali
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.
bl_info = {
    "name": "Boomsmash",
    "author": "Bassam Kurdali",
    "version": (1, 0),
    "blender": (2, 6, 3),
    "location": "View3D > Header",
    "description": "Boomsmashes the current view for Tube",
    "warning": "",
    "wiki_url": "http://wiki.tube.freefac.org/wiki/Boomsmash",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
import os
import string
import random

scene_settings = {
    "use_preview_range": False, "render": {
            'use_stamp_filename': False, 'filepath': '',
            'use_stamp_camera': False, 'use_stamp_sequencer_strip': False,
            'use_stamp_scene': False, 'use_stamp_lens': False,
            'use_stamp_time': False, 'use_stamp_note': False,            
            'use_placeholder': False, 'use_stamp_render_time': False,
            'use_stamp': True,
            'use_overwrite': True, 'pixel_aspect_x': 1.0, 'pixel_aspect_y': 1.0,
            'use_stamp_marker': False, 'use_stamp_date': False,
            'resolution_percentage': 100, 'use_crop_to_border': False,
            'stamp_font_size': 12, 'display_mode': 'AREA', 'fps_base': 1.0,
            'use_file_extension': True, 'use_stamp_frame': True, "ffmpeg": {
                'use_lossless_output': False, 'gopsize': 18, 'format': 'QUICKTIME',
                'packetsize': 2048, 'video_bitrate': 6000, 'minrate': 0,
                'use_autosplit': False, 'muxrate': 10080000, 'codec': 'H264',
                'audio_bitrate': 192, 'audio_codec': 'NONE', 'maxrate': 9000,
                'buffersize': 1792},
            "image_settings": {
                'color_mode': 'RGB', 'color_depth': '8', 'file_format': 'H264',
                'quality': 80}}}

space_settings = {
    "show_only_render": True, "viewport_shade": 'SOLID'}
    
rig_settings = {'gilga': {'props': {'__fibre':1}}}
prox_level = {'gilga_PROX': 'gilga_HI', 'Roach_LO': 'Roach_HI'}

def backup(prop, settings):
    '''recursively create a settings-like dict of an object'''
    current_settings = {}
    for setting in settings:
        if type(settings[setting]) == dict:
            current_settings[setting] = backup(
                getattr(prop, setting), settings[setting])
        else:
            current_settings[setting] = getattr(prop, setting)
    return current_settings


def save(prop, settings):
    '''recursively set settings from a nested dict to an object'''
    for setting in settings:
        if type(settings[setting]) == dict:
            save(getattr(prop, setting), settings[setting])
        else:
            setattr(prop, setting, settings[setting])

class OBJECT_OT_Boomsmash(bpy.types.Operator):
    """Make a Tube BoomSmash"""
    bl_idname = "scene.boomsmash"
    bl_label = "Make a Tube BoomSmash"
    bl_description = "BooooooooooooomSmaaaaaaaaaash"
    #bl_options = {'MACRO'}
    boomtype = bpy.props.EnumProperty(
        items=[
            ("full movie", "full movie","full movie"),
            ("third movie", "third movie", "third movie"),
            ("full frames", "full frames","full frames"),
            ("third frames", "third frames", "third frames")],
        default="full movie")
    
    def execute(self, context):
        
        #setup
        scene = context.scene
        space = context.space_data
        gilga = [rig for rig in scene.objects if rig.type == 'ARMATURE' and\
             '__rig' in rig.data.keys() and\
             rig.data['__rig']['class']=='hero']
        proxies = [ob for ob in scene.objects if ob.type == 'EMPTY' and\
            ob.dupli_type == 'GROUP' and ob.dupli_group and\
            ob.dupli_group.name in ['gilga_PROX', 'Roach_LO']]
        
        boomtype = self.properties.boomtype
        resolution_percentage = 39 if "third" in boomtype else 100

        if 'movie' in boomtype:
            file_format = 'H264'
            rand_suffix  = ''.join(
              random.choice(string.ascii_uppercase) for x in range (5))
        else:
            file_format = 'JPEG'
            rand_suffix  = ''
        home = os.getenv("HOME") if\
          os.getenv("HOME") else os.getenv("USERPROFILE")           
        filepath = os.path.join(
            home, "boomsmash", file_format, 
            "{}{}_".format(context.scene.name, rand_suffix))

        # store old settings:
        old_scene = backup(scene, scene_settings)
        old_rezez = backup(scene.render, {
            'resolution_x':scene.render.resolution_x,
            'resolution_y':scene.render.resolution_y})
        old_space = backup(space, space_settings)

        for rig in gilga:
            old_fibre = rig.pose.bones['props']['__fibre']   
        old_proxies = {ob.name: ob.dupli_group for ob in proxies}

        # change settings:
        save(scene, scene_settings)
        save(space, space_settings)
        for rez in old_rezez:
            if int(old_rezez[rez] * resolution_percentage // 100) % 2:
                setattr(
                    scene.render, rez, old_rezez[rez] + 100 // resolution_percentage)
        for rig in gilga:
            rig.pose.bones['props']['__fibre'] = 1
        for ob in proxies:
            ob.dupli_group = bpy.data.groups[prox_level[ob.dupli_group.name]]


        # User Choice Options:
        scene.render.image_settings.file_format = file_format
        scene.render.resolution_percentage = resolution_percentage
        scene.render.filepath = filepath
        if not 'movie' in boomtype:
            scene.use_preview_range = old_scene['use_preview_range']
 
        
        # boomsmash

        bpy.ops.render.opengl(animation=True)       
        

        # restore old settings:
        for rig in gilga:
            rig.pose.bones['props']['__fibre'] = old_fibre
        for ob in proxies:
            ob.dupli_group = old_proxies[ob.name]
        save(space, old_space) # restore from backup
        save(scene, old_scene) # restore from backup
        save(scene.render, old_rezez) # in case we changed them

        return {'FINISHED'}


# Registration

def add_boomsmash_button(self, context):
    self.layout.operator_menu_enum(
        OBJECT_OT_Boomsmash.bl_idname,
        'boomtype',
        text="Boomsmash")


def register():
    bpy.utils.register_class(OBJECT_OT_Boomsmash)
 
    bpy.types.VIEW3D_HT_header.append(add_boomsmash_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_Boomsmash)
    bpy.types.VIEW3D_HT_header.remove(add_boomsmash_button)


if __name__ == "__main__":
    register()
