#
#    Copyright (c) 2015 Shane Ambler
#
#    All rights reserved.
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:
#
#    1.  Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#    2.  Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
#    OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# made in response to -
# http://blender.stackexchange.com/q/40436/935

bl_info = {
    "name": "Save File Prefix",
    "author": "sambler",
    "version": (1,1),
    "blender": (2, 80, 0),
    "location": "File->Save Prefixed Blendfile",
    "description": "Add a prefix to the filename before saving.",
    "warning": "Runs user specified python code",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/file_prefix.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Learnbgame",
}

import bpy
import os
import time, datetime

class PrefixSavePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    prefix : bpy.props.StringProperty(name="Prefix calculation",
                    description="Python string that calculates the file prefix",
                    default="timestamp().strftime('%Y_%m_%d_%H_%M_%S') + '_'")

    copies : bpy.props.BoolProperty(name="Save as copies",
                    description="Save prefixed copies instead of renaming the existing file",
                    default=True)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        row = col.row()
        row.prop(self,"copies")
        row = col.row()
        row.prop(self,"prefix")

def timestamp():
    # convienience function that is available to the user in their calculations
    return datetime.datetime.fromtimestamp(time.time())

class PrefixFileSave(bpy.types.Operator):
    """Set a filename prefix before saving the file"""
    bl_idname = "wm.save_prefix"
    bl_label = "Save Prefixed Blendfile"

    def execute(self, context):
        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        outname = eval(addon_prefs.prefix) + bpy.path.basename(bpy.data.filepath)
        outpath = os.path.dirname(bpy.path.abspath(bpy.data.filepath))
        print(os.path.join(outpath, outname))
        if addon_prefs.copies:
            return bpy.ops.wm.save_as_mainfile(filepath=os.path.join(outpath, outname),
                    check_existing=True, copy=True)
        return bpy.ops.wm.save_mainfile(filepath=os.path.join(outpath, outname),
                    check_existing=True)

def menu_save_prefix(self, context):
    self.layout.operator(PrefixFileSave.bl_idname, text=PrefixFileSave.bl_label, icon="FILE_TICK")

def register():
    bpy.utils.register_class(PrefixSavePreferences)
    bpy.utils.register_class(PrefixFileSave)

    # add the menuitem to the top of the file menu
    bpy.types.TOPBAR_MT_file.prepend(menu_save_prefix)

    wm = bpy.context.window_manager
    win_keymaps = wm.keyconfigs.user.keymaps.get('Window')
    if win_keymaps:
        # disable standard save file keymaps
        for kmi in win_keymaps.keymap_items:
            if kmi.idname == 'wm.save_mainfile':
                kmi.active = False

        # add a keymap for our save operator
        kmi = win_keymaps.keymap_items.new(PrefixFileSave.bl_idname, 'S', 'PRESS', ctrl=True)

def unregister():

    wm = bpy.context.window_manager
    win_keymaps = wm.keyconfigs.user.keymaps.get('Window')
    if win_keymaps:
        for kmi in win_keymaps.keymap_items:
            # re-enable standard save file
            if kmi.idname == 'wm.save_mainfile':
                kmi.active = True
            if kmi.idname == PrefixFileSave.bl_idname:
                win_keymaps.keymap_items.remove(kmi)

    bpy.types.TOPBAR_MT_file.remove(menu_save_prefix)

    bpy.utils.unregister_class(PrefixFileSave)
    bpy.utils.unregister_class(PrefixSavePreferences)

if __name__ == "__main__":
    register()

