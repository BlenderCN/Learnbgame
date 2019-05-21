
bl_info = {
    'name': 'WarCraft 3',
    'author': 'Pavel_Blend',
    'version': (0, 0, 0),
    'blender': (2, 7, 8),
    'category': 'Import-Export',
    'location': 'File > Import',
    'description': 'Import *.mdx files (3d models of WarCraft 3)',
    'wiki_url': 'https://github.com/PavelBlend/Blender_WarCraft-3',
    'tracker_url': 'https://github.com/PavelBlend/Blender_WarCraft-3/issues'
    }


from .plugin import register, unregister
