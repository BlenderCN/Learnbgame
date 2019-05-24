from scout_constants import *
from scout_tools import *

bl_info = {
    'name': 'pmt room',
    'description': 'Draw a scout pmt',
    'author': 'morgan',
    'version': (1, 0),
    "category": "Learnbgame",
    'blender': (2, 73, 0),
    }

def draw(vtx, rot_axis, rot_angle):
    # Room size: 20x20x40
    ceiling = 30
    room_size = 20
    # Floor first
    floor = createCube((0,0,-1/2), room_size, room_size, 1/2, (0,0,0))
    floor_mat = makeMaterial('walls', (0.4, 0.65, 0.9), (0, 0, 0), 1)
    floor_mat.raytrace_mirror.use = True
    floor_mat.raytrace_mirror.reflect_factor = 0.5
    setMaterial(bpy.context.object, floor_mat)
    name_clean_transform('scout_floor', rot_angle, rot_axis)

if __name__ == '__main__':
    draw((0,0,0), (1,0,0), 0)
