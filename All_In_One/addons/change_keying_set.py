#
#  Copyright (c) 2016 Shane Ambler
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

# made in response to
# http://blender.stackexchange.com/q/49541/935

bl_info = {
    "version": (1, 2),
    "blender": (2, 80, 0),
    "author": "sambler",
    "name": "Change Keying Sets",
    "location": "3D view -> properties region",
    "description": "A panel of buttons and shortcuts that change the active keying set.",
    "warning": "",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/change_keying_set.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Learnbgame",
}

import bpy

class SetKeyingSetOperator(bpy.types.Operator):
    """Set the active keying set"""
    bl_idname = 'anim.set_keyingset'
    bl_label = 'Set the active keying set'

    type : bpy.props.StringProperty(default='LocRotScale')

    def execute(self, context):
        ks = context.scene.keying_sets_all
        if self.type == '':
            ks.active = None
        else:
            ks.active = ks[self.type]
        return {'FINISHED'}

class KeyingsetsPanel(bpy.types.Panel):
    """Display some butons to set the active keying set"""
    bl_label = 'Keying Set'
    bl_idname = 'ANIM_PT_set_keyingset'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.label(text='Active Set:')
        col = row.column()
        if scn.keying_sets_all.active:
            col.label(text=scn.keying_sets_all.active.bl_label)
        else:
            col.label(text='None')

        # some preset buttons - add or adjust to what you use
        row = layout.row()
        row.operator('anim.set_keyingset', text='None').type = ''

        row = layout.row()
        row.operator('anim.set_keyingset', text='Location').type = 'Location'

        row = layout.row()
        row.operator('anim.set_keyingset', text='Rotation').type = 'Rotation'

        row = layout.row()
        row.operator('anim.set_keyingset', text='LocRot').type = 'LocRot'

        row = layout.row()
        row.operator('anim.set_keyingset', text='LocRotScale').type = 'LocRotScale'

        # note that the bl_label of the keying set is used for the type
        # for a list of available type values - paste this in blenders python console
        # [k.bl_label for k in bpy.context.scene.keying_sets_all]
        row = layout.row()
        row.operator('anim.set_keyingset', text='WholeCharacter').type = 'Whole Character'

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(SetKeyingSetOperator)
    bpy.utils.register_class(KeyingsetsPanel)

    # some sample shortcuts - adjust to personal taste.
    # As most keys have been assigned to various tasks I have
    # chosen to setup modifier keys - hold K and press the shortcut key
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # add keys for object mode
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')

        kmi = km.keymap_items.new(SetKeyingSetOperator.bl_idname, 'Y',
                    'PRESS', key_modifier='K')
        kmi.properties.type = 'Location'
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(SetKeyingSetOperator.bl_idname, 'U',
                    'PRESS', key_modifier='K')
        kmi.properties.type = 'Rotation'
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(SetKeyingSetOperator.bl_idname, 'I',
                    'PRESS', key_modifier='K')
        kmi.properties.type = 'LocRotScale'
        addon_keymaps.append((km, kmi))


        # add keys for pose mode
        km = wm.keyconfigs.addon.keymaps.new(name='Pose', space_type='EMPTY')

        kmi = km.keymap_items.new(SetKeyingSetOperator.bl_idname, 'Y',
                    'PRESS', key_modifier='K')
        kmi.properties.type = 'Location'
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(SetKeyingSetOperator.bl_idname, 'U',
                    'PRESS', key_modifier='K')
        kmi.properties.type = 'Rotation'
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(SetKeyingSetOperator.bl_idname, 'I',
                    'PRESS', key_modifier='K')
        kmi.properties.type = 'LocRotScale'
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(KeyingsetsPanel)
    bpy.utils.unregister_class(SetKeyingSetOperator)


if __name__ == "__main__":
    register()

