import math
from scout_constants import *
from scout_tools import *

bl_info = {
    'name': 'splitter',
    'description': 'Splits the image down a plan (removing the extra bit)',
    'author': 'morgan',
    'version': (1, 0),
    'blender': (2, 73, 0),
    }

def draw():
    cube_size = 10
    scn = bpy.context.scene
    list_of_obj = [obj.name for obj in scn.objects if obj.type == 'MESH' and obj.name != 'destroyer']
    for ob in list_of_obj:
        #plane = createPlane((0,0,0), plane_size, plane_size, (math.pi/2,0,0))
        destroyer = createCube((0,-cube_size,cube_size), cube_size, cube_size, cube_size, (0,0,0))
        difference(bpy.data.objects[ob], destroyer)

def split():
    draw()
