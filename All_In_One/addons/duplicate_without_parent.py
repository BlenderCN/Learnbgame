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

# made in response to
# http://blender.stackexchange.com/q/42365/935

import bpy

bl_info = {
    "name": "Duplicate object(s) without parenting",
    "author": "sambler",
    "version": (1,1),
    "blender": (2, 80, 0),
    "location": "Shift-Alt-D",
    "description": "Duplicate selected objects or bones without copying the parent connection",
    "warning": "",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/duplicate_without_parent.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Learnbgame",
}

class DuplicateWithoutParent(bpy.types.Operator):
    """Duplicate selection without parenting"""
    bl_idname = "object.duplicate_no_parent"
    bl_label = "Duplicate without parenting"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if context.active_object.type == 'ARMATURE' \
                and context.active_object.mode == 'EDIT':
            bpy.ops.armature.duplicate()
            for b in context.selected_bones:
                b.parent = None
        else:
            bpy.ops.object.duplicate()
            bpy.ops.object.parent_clear(type='CLEAR')
        return bpy.ops.transform.translate('INVOKE_DEFAULT')

addon_keymaps = []

def register():
    bpy.utils.register_class(DuplicateWithoutParent)

    if bpy.app.background: return

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new('Armature', space_type='EMPTY')
        kmi = km.keymap_items.new(DuplicateWithoutParent.bl_idname,
                'D', 'PRESS', alt=True, shift=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new('Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(DuplicateWithoutParent.bl_idname,
                'D', 'PRESS', alt=True, shift=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(DuplicateWithoutParent)

if __name__ == "__main__":
    register()
