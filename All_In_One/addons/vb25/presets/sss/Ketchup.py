import bpy

from bl_ui.properties_material import active_node_mat


ma = active_node_mat(bpy.context.active_object.active_material)
ma.diffuse_color = 1.0,1.0,1.0 # This will also trigger the update

VRayMaterial = ma.vray
VRayMaterial.type = 'BRDFSSS2Complex'

BRDFSSS2Complex = VRayMaterial.BRDFSSS2Complex

BRDFSSS2Complex.sub_surface_color = 0.400,0.110,0.000
BRDFSSS2Complex.specular_glossiness = 0.7
BRDFSSS2Complex.scatter_radius = 0.690,0.243,0.196
BRDFSSS2Complex.scatter_radius_mult = 1.0
BRDFSSS2Complex.diffuse_color = 0.400,0.110,0.000
BRDFSSS2Complex.ior = 1.3
BRDFSSS2Complex.phase_function = 0.9
BRDFSSS2Complex.specular_amount = 1.0
