from scout_constants import *
from scout_tools import *

bl_info = {
    'name': 'shield',
    'description': 'Draw a scout lead shield',
    'author': 'morgan',
    "category": "Learnbgame",
    'version': (1, 0),
    'blender': (2, 73, 0),
    }

def draw(vtx, rot_axis, rot_angle):
    # Materials
    shield_exterior = makeMaterial('lead', (0.8, 0.4, 0.15), (1, 1, 1), 0.1)
    shield_interior = makeMaterial('copper', (0.8, 0.2, 0.05), (1, 1, 1), 0.3)
    local_origin = sum_tuple( (0, 0, shield_height/2), vtx )
    # Lead
    outside = createCylinder(local_origin, shield_outer_rad, shield_height, (0,0,0))
    setMaterial(bpy.context.object, shield_exterior)
    inside = createCylinder(local_origin, shield_inner_rad+copper_thickness, shield_height, (0,0,0))
    difference(outside,inside)

    # Copper
    out_copper = createCylinder(local_origin, shield_inner_rad+copper_thickness,
                                shield_height, (0,0,0))
    setMaterial(bpy.context.object, shield_interior)
    in_copper = createCylinder(local_origin, shield_inner_rad,
                               shield_height, (0,0,0))
    difference(out_copper, in_copper)

    name_clean_transform('scout_shield', rot_angle, rot_axis)

if __name__ == '__main__':
    draw((0,0,0), (1,0,0), 0)
