from scout_constants import *
from scout_tools import *

bl_info = {
    'name': 'av',
    'description': 'Draw the scout acrylic vessel',
    'author': 'morgan',
    'version': (1, 0),
    "category": "Learnbgame",
    'blender': (2, 73, 0),
    }

def draw(vtx, rot_axis, rot_angle):
    # Materials
    acrylic = makeMaterial('acrylic', (0.05,0.65,0.8), (1,1,1), 0.1)
    av_bottom = createCylinder(sum_tuple(vtx, (0,0,av_thickness/2)), av_big_radius,
                               av_thickness, (0,0,0))
    setMaterial(bpy.context.object, acrylic)
    av_top = createCylinder(sum_tuple(vtx, (0,0,av_height-av_thickness/2)), av_big_radius,
                            av_thickness, (0,0,0))
    setMaterial(bpy.context.object, acrylic)
    # Walls
    wall_origin = sum_tuple(vtx, (0,0,av_height/2))
    av_wall_out = createCylinder(wall_origin, av_small_radius_outer,
                                 (av_height - 2*av_thickness), (0,0,0))
    setMaterial(bpy.context.object, acrylic)
    av_wall_in = createCylinder(wall_origin, av_small_radius_inner,
                                (av_height - 2*av_thickness), (0,0,0))
    difference(av_wall_out, av_wall_in)
    join(av_bottom, av_top)
    join(av_bottom, av_wall_out)
    join(av_bottom, av_wall_in)
    name_clean_transform('scout_av', rot_angle, rot_axis)

if __name__ == '__main__':
    draw((0,0,0), (1,0,0), 0)
