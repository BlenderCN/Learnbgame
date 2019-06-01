import bpy

def active_node_material(ma):
	ma_node= ma.active_node_material
	if ma_node:
		return ma_node
	else:
		return ma

ma= active_node_material(bpy.context.active_object.active_material)

VRayMaterial= ma.vray
VRayMaterial.type= 'BRDFVRayMtl'

VRayMaterial.Mtl2Sided.use= True

BRDFVRayMtl= VRayMaterial.BRDFVRayMtl
