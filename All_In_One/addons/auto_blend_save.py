#
#    Copyright (c) 2017 Shane Ambler
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# made in response to BSE question -
# https://blender.stackexchange.com/q/95070/935

bl_info = {
    "name": "Auto Blend Save",
    "author": "sambler",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "location": "blender",
    "description": "Automatically save multiple copies of a blend file",
    "warning": "Deletes old files - check your settings.",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/auto_blend_save.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Learnbgame",
    }

import bpy
from bpy.app.handlers import persistent
import datetime as dt
import os

## TIME_FMT_STR is used for filename prefix so keep path friendly
## deleting old files relies on this format - CHANGE WITH CAUTION
TIME_FMT_STR = '%Y_%m_%d_%H_%M_%S'

last_saved = None

class AutoBlendSavePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    save_after_open : bpy.props.BoolProperty(name='Save on open',
                    description='Save a copy of file after opening it',
                    default=True)
    save_before_close : bpy.props.BoolProperty(name='Save before close',
                    description='Save the current file before opening another file',
                    default=True)
    save_on_interval : bpy.props.BoolProperty(name='Save at intervals',
                    description='Save the file at timed intervals',
                    default=True)
    save_interval : bpy.props.IntProperty(name='Save interval',
                    description='Number of minutes between each save',
                    default=5, min=1, max=120, soft_max=30)
    save_to_path : bpy.props.StringProperty(name='Save to path',
                    description='Path to auto save files into',
                    default='//AutoSave')
    max_save_files : bpy.props.IntProperty(name='Max save files',
                    description='Maximum number of copies to save, 0 means unlimited',
                    default=10, min=0, max=100)
    compress_backups : bpy.props.BoolProperty(name='Compress backups',
                    description='Save backups with compression enabled',
                    default=True)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        row = col.row()
        row.prop(self,'save_after_open')
        row = col.row()
        row.prop(self,'save_before_close')
        row = col.row()
        row.prop(self,'save_on_interval')
        if self.save_on_interval:
            row.prop(self,'save_interval')
        row = col.row()
        row.prop(self,'save_to_path')
        row = col.row()
        if bpy.data.filepath == '':
            par = os.getcwd()
        else:
            par = None
        row.label(text='Current file will save to: '+bpy.path.abspath(self.save_to_path, start=par))
        row = col.row()
        row.prop(self,'max_save_files')
        row = col.row()
        row.prop(self,'compress_backups')

def prefs():
    user_preferences = bpy.context.preferences
    return user_preferences.addons[__name__].preferences

def time_since_save():
    '''Minutes since last saved'''
    global last_saved
    if last_saved is None:
        last_saved = dt.datetime.now()
    now = dt.datetime.now()
    elapsed = now - last_saved
    return elapsed.seconds // 60 #minutes

def save_file():
    global last_saved
    last_saved = dt.datetime.now()
    p = prefs()

    basename = bpy.data.filepath
    if basename == '':
        basename = 'Unsaved.blend'
    else:
        basename = bpy.path.basename(basename)

    try:
        save_dir = bpy.path.abspath(p.save_to_path)
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
    except:
        print("Error creating auto save directory.")
        return

    # delete old files if we want to limit the number of saves
    if p.max_save_files > 0:
        try:
            # as we prefix saved blends with a timestamp
            # sorted puts the oldest prefix at the start of the list
            # this should be quicker than getting system timestamps for each file
            otherfiles = sorted([name for name in os.listdir(save_dir) if name.endswith(basename)])
            if len(otherfiles) >= p.max_save_files:
                while len(otherfiles) >= p.max_save_files:
                    old_file = os.path.join(save_dir,otherfiles[0])
                    os.remove(old_file)
                    otherfiles.pop(0)
        except:
            print('Unable to remove old files.')

    # save the copy
    filename = last_saved.strftime(TIME_FMT_STR) + '_' + basename
    backup_file = os.path.join(save_dir,filename)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=backup_file, copy=True,
                                        compress=p.compress_backups)
    except:
        print('Error auto saving file.')

@persistent
def save_post_open(scn):
    if prefs().save_after_open:
        save_file()

@persistent
def save_pre_close(scn):
    # is_dirty means there are changes that haven't been saved to disk
    if bpy.data.is_dirty and prefs().save_before_close:
        save_file()

@persistent
def timed_save(scn):
    if bpy.data.is_dirty and prefs().save_on_interval \
            and time_since_save() >= prefs().save_interval:
        save_file()

def register():
    bpy.utils.register_class(AutoBlendSavePreferences)
    bpy.app.handlers.load_pre.append(save_pre_close)
    bpy.app.handlers.load_post.append(save_post_open)
    bpy.app.handlers.depsgraph_update_post.append(timed_save)

def unregister():
    bpy.app.handlers.load_pre.remove(save_pre_close)
    bpy.app.handlers.load_post.remove(save_post_open)
    bpy.app.handlers.depsgraph_update_post.remove(timed_save)
    bpy.utils.unregister_class(AutoBlendSavePreferences)

if __name__ == "__main__":
    register()
