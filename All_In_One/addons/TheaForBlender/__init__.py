"""
.. module:: TheaForBlender
   :platform: OS X, Windows, Linux
   :synopsis: TheaForBlender plugin

.. moduleauthor:: Grzegorz Rakoczy <grzegorz.rakoczy@solidiris.com>


"""
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
    "name": "Thea Render",
    "author": "Grzegorz Rakoczy",
    "version": (1,5,8,760,1455),
    "blender": (2, 7, 8),
    "location": "Render>Engine>Thea Render",
    "description": "Thea Render",
    "warning": "",
    "wiki_url": "https://thearender.com/site/index.php/products/thea-for-blender.html",
    "tracker_url": "http://thearender.com/forum/viewforum.php?f=70&sid=5afab1703d99826f7cb8926cfe68b2b1",
    "category": "Learnbgame"
}


if "bpy" in locals():
    import imp
    imp.reload(thea_render_main)
    imp.reload(thea_operators)
    imp.reload(thea_properties)
    imp.reload(thea_gui)
    imp.reload(thea_exporter)
    imp.reload(thea_IR)
    imp.reload(thea_globals)

else:
    import bpy
    from bpy.props import *
    from . import thea_render_main
    from . import thea_IR
    from . import thea_operators
    from . import thea_properties
    from . import thea_gui
    from . import thea_exporter
    from . import thea_globals
    from bpy.app.handlers import persistent


import logging


@persistent
def load_pre_handler(arg):
    ''' It's called before scene is loaded and will stop IR in that case.

    '''

    if bpy.context.scene.thea_ir_running:
        from . import thea_render_main
        print("Stopping IR...")
        port = bpy.context.scene.thea_SDKPort

        data = thea_render_main.sendSocketMsg('localhost', port, b'version')

        if data.find('v'):
            message = b'message "./UI/Viewport/Theme/RW_PROG"'
            data = thea_render_main.sendSocketMsg('localhost', port, message)
            message = b'message "exit"'
            data = thea_render_main.sendSocketMsg('localhost', port, message)

bpy.app.handlers.load_pre.append(load_pre_handler)

@persistent
def load_post_handler(arg):
    '''It's called after scene is loaded and will set debug level according to current scene setup.
    '''

    if getattr(bpy.context.scene, 'thea_LogLevel') == "Debug":
        thea_globals.log.setLevel(logging.DEBUG)
        thea_globals.fh.setLevel(logging.DEBUG)
    else:
        thea_globals.log.setLevel(logging.INFO)
        thea_globals.fh.setLevel(logging.INFO)

    thea_globals.getConfig()

#     bpy.context.scene.thea_useLUT = thea_globals.getUseLUT()

bpy.app.handlers.load_post.append(load_post_handler)

def register():
    '''Register the plugin and enable some key mappings for IR if it's enabled.
    '''

    Scene = bpy.types.Scene
    bpy.utils.register_module(__name__)

    if thea_globals.getRemapIRKeys():

        km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View Generic']
        #kmi = km.keymap_items.new('thea.pause_ir',value='PRESS',type='F12',ctrl=False,alt=False,shift=False,oskey=False)
        kmi = km.keymap_items.new('thea.smart_start_ir',value='PRESS',type='F12',ctrl=False,alt=False,shift=False,oskey=True)

        km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View Generic']
        kmi = km.keymap_items.new('thea.start_ir',value='PRESS',type='F12',ctrl=True,alt=False,shift=False,oskey=True)

        #km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View Generic']
        #kmi = km.keymap_items.new('thea.start_ir_reuse',value='PRESS',type='F12',ctrl=True,alt=False,shift=True,oskey=False)

        km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View Generic']
        kmi = km.keymap_items.new('thea.update_ir',value='PRESS',type='F11',ctrl=False,alt=False,shift=False,oskey=True)

        km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View Generic']
        kmi = km.keymap_items.new('thea.big_preview',value='PRESS',type='B',ctrl=False,alt=True,shift=True,oskey=False)



def unregister():
    '''Unregister the plugin.
    '''

    Scene = bpy.types.Scene
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()


import atexit

@atexit.register
def exitRemoteDarkroom():
    ''' Send exit messsages to RemoteDarkroom on Blender exit.
    '''
    thea_globals.log.info("Sending exit signals to RemoteDarkroom processes")
    port = getattr(bpy.context.scene, 'thea_SDKPort', 30000)
    data = thea_render_main.sendSocketMsg('localhost', port, b'exit')
    port = getattr(bpy.context.scene, 'thea_SDKPort', 30000)+2
    data = thea_render_main.sendSocketMsg('localhost', port, b'exit')
    port = getattr(bpy.context.scene, 'thea_PreviewSDKPort', 30001)
    data = thea_render_main.sendSocketMsg('localhost', port, b'exit')

