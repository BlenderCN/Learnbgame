
bl_info = {
    'name': 'Fence Generator',
    'author': 'Pavel_Blend',
    'version': (0, 0, 0),
    'blender': (2, 79, 0),
    'category': 'Add Mesh',
    'location': 'View3D > Add > Mesh',
}

from .addon import register, unregister
