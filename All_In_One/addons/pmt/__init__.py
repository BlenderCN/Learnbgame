from scout_constants import *
from scout_tools import *

bl_info = {
    'name': 'pmt',
    'description': 'Draw a scout pmt',
    'author': 'morgan',
    'version': (1, 0),
    'blender': (2, 73, 0),
    }

def draw(vtx, rot_axis, rot_angle):
    # PMT looks like this:
    #    ______    #
    #    |    |    #
    #     \  /     #
    #     |  |     #
    #     |__|     #
    #              #
    ################
    local_origin = sum_tuple( vtx, (0, 0, -pmt_length/2) )
    top_start = pmt_length/2 - pmt_top_size/2
    top_position = sum_tuple(local_origin, (0, 0, top_start))
    curvy_position = sum_tuple(top_position, (0, 0, -pmt_top_size))
    pmt_exterior = makeMaterial('pmt_cover', (0, 0, 0), (0, 0, 0), 1)
    # Top and bottom cylinders
    bpy.ops.group.create(name="pmt")

    bot_cyl = createCylinder(local_origin, pmt_bottom_radius, pmt_length, (0,0,0))
    top_cyl = createCylinder(top_position, pmt_top_radius, pmt_top_size, (0,0,0))
    mid_cone = createCone(curvy_position, pmt_top_radius, pmt_bottom_radius,
                          pmt_taper_length, (0,0,0))
    join(top_cyl, bot_cyl)
    join(top_cyl, mid_cone)
    setMaterial(bpy.context.object, pmt_exterior)

    name_clean_transform('scout_pmt', rot_angle, rot_axis)
    setMaterial(bpy.context.object, pmt_exterior)

if __name__ == '__main__':
    draw((0,0,0), (1,0,0), 0)
