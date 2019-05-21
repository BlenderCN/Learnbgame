# ##### BEGIN BSD LICENSE BLOCK #####
#
# Copyright 2017 Funjack
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ##### END BSD LICENSE BLOCK #####

bl_info = {
    "name": "Funscripting Addon",
    "author": "Funjack",
    "version": (0, 0, 0),
    "location": "Sequencer",
    "description": "Script Launch haptics data and export as Funscript.",
    "category": "Sequencer",
}

if "bpy" in locals():
    import importlib
    importlib.reload(fun_ui)

import bpy
from . import fun_ui

addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.funscripting = bpy.props.PointerProperty(type=fun_ui.FunscriptSettings)

    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR')
        kmi = km.keymap_items.new(fun_ui.FunscriptFillButton.bl_idname, 'EQUAL', 'PRESS')
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptRepeatButton.bl_idname, 'ACCENT_GRAVE', 'PRESS')
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'ZERO', 'PRESS')
        kmi.properties.launchPosition = 0
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_0', 'PRESS')
        kmi.properties.launchPosition = 0
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'ONE', 'PRESS')
        kmi.properties.launchPosition = 10
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_1', 'PRESS')
        kmi.properties.launchPosition = 10
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'TWO', 'PRESS')
        kmi.properties.launchPosition = 20
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_2', 'PRESS')
        kmi.properties.launchPosition = 20
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'THREE', 'PRESS')
        kmi.properties.launchPosition = 30
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_3', 'PRESS')
        kmi.properties.launchPosition = 30
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'FOUR', 'PRESS')
        kmi.properties.launchPosition = 40
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_4', 'PRESS')
        kmi.properties.launchPosition = 40
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'FIVE', 'PRESS')
        kmi.properties.launchPosition = 50
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_5', 'PRESS')
        kmi.properties.launchPosition = 50
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'SIX', 'PRESS')
        kmi.properties.launchPosition = 60
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_6', 'PRESS')
        kmi.properties.launchPosition = 60
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'SEVEN', 'PRESS')
        kmi.properties.launchPosition = 70
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_7', 'PRESS')
        kmi.properties.launchPosition = 70
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'EIGHT', 'PRESS')
        kmi.properties.launchPosition = 80
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_8', 'PRESS')
        kmi.properties.launchPosition = 80
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NINE', 'PRESS')
        kmi.properties.launchPosition = 90
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_9', 'PRESS')
        kmi.properties.launchPosition = 90
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'MINUS', 'PRESS')
        kmi.properties.launchPosition = 100
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionButton.bl_idname, 'NUMPAD_PERIOD', 'PRESS')
        kmi.properties.launchPosition = 100
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(fun_ui.FunscriptDeleteButton.bl_idname, 'DEL', 'PRESS', ctrl=True)
        kmi.properties.last = True
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(fun_ui.FunscriptPositionLimitButton.bl_idname, 'COMMA', 'PRESS')
        kmi.properties.limitType = "same"
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionLimitButton.bl_idname, 'PERIOD', 'PRESS')
        kmi.properties.limitType = "shortest"
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(fun_ui.FunscriptPositionLimitButton.bl_idname, 'SLASH', 'PRESS')
        kmi.properties.limitType = "longest"
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    del bpy.types.Scene.funscripting
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
