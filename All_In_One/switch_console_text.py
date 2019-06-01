bl_info = {
    'name': 'Switch Between Console and Text Editor Spaces',
    'description': 'Switch Between Console and Text Editor Spaces by using the SHIFT+ESC key',
    "category": "Learnbgame",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 7, 0),
}

import bpy


def register():
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    
    if keyconfig:
        for source, destination in (('Console', 'TEXT_EDITOR'), ('Text', 'CONSOLE')):
            args = ('wm.context_set_enum', 'ESC', 'PRESS')
            kwargs = {'shift':True}
        
            keymap = keyconfig.keymaps.get(source)
            
            if not keymap:
                keymap = keyconfig.keymaps.new(source)
            
            kmi = keymap.keymap_items.new(*args, **kwargs)

            properties = kmi.properties
            properties.data_path = 'area.type'
            properties.value = destination


def unregister():
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    
    if keyconfig:
        pass
