import bpy

from bl_ui.properties_material import active_node_mat


ma = active_node_mat(bpy.context.active_object.active_material)

VRayMaterial = ma.vray
VRayMaterial.type = 'BRDFVRayMtl'
VRayMaterial.Mtl2Sided.use = False

BRDFVRayMtl = VRayMaterial.BRDFVRayMtl

BRDFVRayMtl.diffuse = 0.0,0.0,0.0
BRDFVRayMtl.fog_color = 0.78,1.0,0.845
BRDFVRayMtl.refract_color = 1.0,1.0,1.0
BRDFVRayMtl.refract_ior = 1.55
BRDFVRayMtl.refract_affect_shadows = True
BRDFVRayMtl.reflect_color = 0.95,0.95,0.95
BRDFVRayMtl.fresnel = True
