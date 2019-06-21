import bpy

from bl_ui.properties_material import active_node_mat

material = active_node_mat(bpy.context.active_object.active_material)

VRayMaterial = material.vray
VRayMaterial.type = 'BRDFSSS2Complex'

BRDFSSS2Complex = VRayMaterial.BRDFSSS2Complex

BRDFSSS2Complex.sub_surface_color = 0.878,0.788,0.459
BRDFSSS2Complex.specular_glossiness = 0.6
BRDFSSS2Complex.scatter_radius = 0.843,0.600,0.318
BRDFSSS2Complex.scatter_radius_mult = 2.0
BRDFSSS2Complex.diffuse_color = 0.878,0.788,0.459
BRDFSSS2Complex.ior = 1.3
BRDFSSS2Complex.phase_function = 0.8
BRDFSSS2Complex.specular_amount = 1.0
