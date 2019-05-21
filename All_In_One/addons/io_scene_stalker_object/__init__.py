
bl_info = {
    'name': 'Import S.T.A.L.K.E.R. Object',
    'author': 'Pavel_Blend',
    'version': (0, 0, 0),
    'blender': (2, 7, 6),
    'category': 'Import-Export',
    'location': 'File > Import',
    'description': 'Import X-Ray Engine *.object files',
    'wiki_url': 'https://github.com/PavelBlend/Blender-OBJECT-X-Ray-Engine',
    'tracker_url': 'https://github.com/PavelBlend/Blender-OBJECT-X-Ray-Engine/issues'
    }


from .plugin import register, unregister
