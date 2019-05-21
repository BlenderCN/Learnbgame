# ##### BEGIN GPL LICENSE BLOCK #####
#
#  game_engine_legacy_start.py
#  Start the BGE in any render context (workaround for Blender >= 2.73)
#  Copyright (C) 2015 Quentin Wenger
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



bl_info = {"name": "Start Game Engine (Legacy)",
           "description": "Start the BGE in any render context with the P-key, like in pre-2.73 Blender Versions",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 1),
           "blender": (2, 73, 0),
           "location": "View3D > P",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "Game Engine"
           }




import bpy




class VIEW3D_OT_legacy_game_start(bpy.types.Operator):
    bl_idname = "view3d.legacy_game_start"
    bl_label = "Start Game Engine (Legacy)"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def execute(self, context):

        # temporarily save previous settings
        engine = bpy.context.scene.render.engine

        if not bpy.context.scene.render.use_game_engine:
            bpy.context.scene.render.engine = 'BLENDER_GAME'

        bpy.ops.view3d.game_start()

        bpy.context.scene.render.engine = engine

        return {'FINISHED'}



def register():
    bpy.utils.register_module(__name__)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        km = kc.keymaps.new(name='Object Mode')
        kmi = km.keymap_items.new('view3d.legacy_game_start', 'P', 'PRESS')
        


def unregister():
    bpy.utils.unregister_module(__name__)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        km = kc.keymaps['Object Mode']
        for kmi in km.keymap_items:
            if kmi.idname == 'view3d.legacy_game_start':
                km.keymap_items.remove(kmi)
                break


if __name__ == "__main__":
    register()
