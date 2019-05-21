bl_info = {
    'name':     'OGF Tools',
    'author':   'Vakhurin Sergey (igel)',
    'version':  (0, 0, 0),
    'blender':  (2, 68, 0),
    'category': 'Import-Export',
    'location': 'File > Import/Export',
    'description': 'Import STALKER OGF files',
    'wiki_url': 'https://github.com/igelbox/blender-ogf',
    'tracker_url': 'https://github.com/igelbox/blender-ogf/issues',
    'warning':  'Under construction!'
}

try:
    #noinspection PyUnresolvedReferences
    from .ogf_plugin import register, unregister
except ImportError:
    pass
