## Defines all of scout's dimensions
import math

bl_info = {
    'name': 'scout_constants',
    'description': 'Contains the dimensions of all of scouts parts',
    'author': 'morgan',
    'version': (1, 0),
    'blender': (2, 73, 0),
    }

# Constants
inches = 1/4
cm = inches * 2.54
# Shield dimensions
shield_inner_rad = 10.5/2*inches
shield_outer_rad = 10*inches
shield_height = 16*inches
copper_thickness = 0.01*inches
# PMT dimensions
pmt_top_radius = 3/2*inches
pmt_bottom_radius = 2/2*inches
pmt_length = 8.5*inches
pmt_top_size = 1*inches
pmt_taper_length = 1*inches
pmt_location = pmt_top_radius + 1/4*inches
pmt_bottom_clearance = 2.5*inches
# AV dimensions
# Maximal
av_side_clearance = 1/4*inches
av_top_clearance = 1/2*inches
av_inset = 1/4*inches
av_thickness = 1/4*inches
av_big_radius = shield_inner_rad-av_side_clearance
av_small_radius_outer = av_big_radius-av_inset
av_small_radius_inner =av_small_radius_outer - av_thickness
av_height = shield_height - av_top_clearance - pmt_length - pmt_bottom_clearance
## AV using mcmaster tube
av_small_radius_outer = 10/2*inches
av_small_radius_inner = 9.75/2*inches
av_volume = math.pi * (av_height-2*av_thickness) * (av_small_radius_inner ** 2)
av_volume_litres = av_volume/(inches**3)*(cm/inches)**3/1000
# PMT holder dimensions
holder_thickness = 1/4*inches
holder_distance = pmt_taper_length/2 + pmt_top_size
holder_pmt_clearance = 1/16*inches
holder_pmt_radii = holder_pmt_clearance + pmt_top_radius
holder_small_radii = 2.75/2*inches
holder_rod_radius = 1/2*inches
holder_rod_cut = holder_rod_radius + 1/16*inches
holder_rod_clearance = 1/2*inches
holder_rod_length = pmt_length + pmt_bottom_clearance - holder_thickness

def print_dimensions():
    print('Shield inner radius:', shield_inner_rad/inches, '"')
    print('Shield height:', shield_height/inches, '"')
    print('Top clearance:', av_top_clearance/inches, '"')
    print('Side clearance:', av_side_clearance/inches, '"')
    print('AV Lid and bottom radius:', av_big_radius/inches, '"')
    print('AV cylinder outer radius:', av_small_radius_outer/inches, '"')
    print('AV cylinder inner radius:', av_small_radius_inner/inches, '"')
    print('AV cylinder height:', (av_height-2*av_thickness)/inches, '"')
    print('AV thickness:', av_thickness/inches, '"')
    print('AV volume: %g' % av_volume_litres, 'litres')
    print('Holder rod length:', holder_rod_length/inches, '"')


if __name__ == '__main__':
    print_dimensions()
