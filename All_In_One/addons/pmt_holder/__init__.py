from scout_constants import *
from scout_tools import *

bl_info = {
    'name': 'pmt_holder',
    'description': 'Draw the pmt holder structure for scout',
    'author': 'morgan',
    'version': (1, 0),
    'blender': (2, 73, 0),
    }

def draw(vtx, rot_axis, rot_angle):
    holder_material = makeMaterial('pvc-grey', (0.4, 0.4, 0.4), (1, 1, 1), 0.8)
    top_vtx = sum_tuple(vtx, (0, 0, -holder_thickness/2))
    bot_vtx = sum_tuple(vtx, (0, 0, -holder_distance))

    top_piece = createCylinder(top_vtx, av_big_radius, holder_thickness, (0,0,0))
    setMaterial(top_piece, holder_material)

    cut_out_spots = [sum_tuple((pmt_location, pmt_location, 0), top_vtx),
                     sum_tuple((-pmt_location, -pmt_location, 0), top_vtx),
                     sum_tuple((pmt_location, -pmt_location, 0), top_vtx),
                     sum_tuple((-pmt_location, pmt_location, 0), top_vtx)]
    for spot in cut_out_spots:
        cut_out = createCylinder(spot, holder_pmt_radii, holder_thickness, (0,0,0))
        difference(top_piece, cut_out)
    name_clean_transform('scout_pmt_holder_top', rot_angle, rot_axis)

    bottom_piece = createCylinder(bot_vtx, av_big_radius, holder_thickness, (0,0,0))
    setMaterial(bottom_piece, holder_material)
    hold_cut_spots = [sum_tuple((pmt_location, pmt_location, 0), bot_vtx),
                      sum_tuple((-pmt_location, -pmt_location, 0), bot_vtx),
                      sum_tuple((-pmt_location, pmt_location, 0), bot_vtx),
                      sum_tuple((pmt_location, -pmt_location, 0), bot_vtx)]
    for spot in hold_cut_spots:
        cut_out = createCylinder(spot, holder_small_radii, holder_thickness, (0,0,0))
        difference(bottom_piece, cut_out)
    rod_positions = (av_big_radius - holder_rod_radius - holder_rod_clearance)
    cut_out_spots = [sum_tuple((0, rod_positions, 0), bot_vtx),
                     sum_tuple((rod_positions, 0, 0), bot_vtx),
                     sum_tuple((-rod_positions, 0, 0), bot_vtx),
                     sum_tuple((0, -rod_positions, 0), bot_vtx)]
    for spot in cut_out_spots:
        cut_out = createCylinder(spot, holder_rod_cut, holder_thickness, (0,0,0))
        difference(bottom_piece, cut_out)
        
    name_clean_transform('scout_pmt_holder_bottom', rot_angle, rot_axis)

    rod_spots = [sum_tuple((0, rod_positions, 0), top_vtx),
                     sum_tuple((rod_positions, 0, 0), top_vtx),
                     sum_tuple((-rod_positions, 0, 0), top_vtx),
                     sum_tuple((0, -rod_positions, 0), top_vtx)]
    for spot in rod_spots:
        newrod = createCylinder(sum_tuple(spot, (0, 0, -holder_rod_length/2-holder_thickness/2)),
                                holder_rod_radius, holder_rod_length, (0,0,0))
        setMaterial(newrod, holder_material)
        name_clean_transform('scout_pmt_holder_rod', rot_angle, rot_axis)

if __name__ == '__main__':
    draw((0,0,0), (1,0,0), 0)
