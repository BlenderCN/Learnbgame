bl_info = {
    'name': 'Quake engine BSP format',
    'author': 'Joshua Skelton',
    'version': (1, 0, 2),
    'blender': (2, 80, 0),
    'location': 'File > Import-Export',
    'description': 'Load a Quake engine BSP file.',
    'warning': '',
    'wiki_url': '',
    'support': 'COMMUNITY',
    'category': 'Import-Export'}

__version__ = '.'.join(map(str, bl_info['version']))


if 'operators' in locals():
    import importlib as il
    il.reload(operators)
    print('io_scene_bsp: reload ready')

else:
    print('io_scene_bsp: ready')


def register():
    from .patch import ensure_modules_dir_on_path
    ensure_modules_dir_on_path()

    from .operators import register
    register()


def unregister():
    from .operators import unregister
    unregister()


if __name__ == '__main__':
    from .operators import register
    register()
