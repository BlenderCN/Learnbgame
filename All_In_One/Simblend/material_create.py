'''
Author :  Dominik Sand 
Date : 23.04.2013

creates a list materials from the list of existing masses that are appended to the created Blender meshes

'''


import bpy


def material_create(Masslist):
	for item in Masslist:
		if bpy.context.scene.animation_type == 'path_id':
			mat = bpy.data.materials.new(item)
			mat.type = 'SURFACE'
			if(bpy.context.scene.ion_tube_mod == True):
				mat.use_vertex_color_light = True
		if bpy.context.scene.animation_type == 'sphere_id':
			mat = bpy.data.materials.new(item)
			mat.type = 'SURFACE'
			if(bpy.context.scene.ion_splat == True):
				bpy.data.materials.new((item + " red_splat"))
				bpy.data.materials.get(item + " red_splat").diffuse_color[0] = 1
				bpy.data.materials.get(item + " red_splat").diffuse_color[1] = 0
				bpy.data.materials.get(item + " red_splat").diffuse_color[2] = 0
		if bpy.context.scene.animation_type == 'particle_id':
			mat = bpy.data.materials.new(item + "Halo")
			mat.type = 'HALO'