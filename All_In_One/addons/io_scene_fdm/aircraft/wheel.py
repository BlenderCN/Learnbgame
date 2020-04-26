'''
Parse a wheel from a blender scene and create/update a Wheel object

@author: tom
'''

import bpy, sys

def parse(ob):
	
	mesh = ob.to_mesh(bpy.context.scene, True, 'PREVIEW')
	transform_parent_space = ob.parent.matrix_world.inverted() * ob.matrix_world
		
	min_z = sys.float_info.max
	max_z = sys.float_info.min
		
	for vert in mesh.vertices:
		pos = transform_parent_space * vert.co
	
		if pos.z < min_z:
			min_z = pos.z
		if pos.z > max_z:
			max_z = pos.z
				
	bpy.data.meshes.remove(mesh)

	contact_point = transform_parent_space.to_translation()
	contact_point.z = min_z

	return {
		'ob': ob,
		'contact_point': contact_point,
		'diameter': max_z - min_z
	}