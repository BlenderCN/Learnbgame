import bpy
import bmesh

'''
Focuses on two meshs and checks for intersection - T/F

Includes function that returns 2-tuple of the names of the first mesh pair found
'''

def _create_background_scene(name = "backgroundScene"):
	"""
	Returns a background scene for work
	Name defaults to 'backgroundScene'
	"""

	#Grabs the name of the current scene
	origSceneName = bpy.context.scene.name 
	
	#Creates a new scene in the format of 'Scene.XXX'
	bpy.ops.scene.new()
	
	#Creating a new scene auto switches the Screen. Go back to original scene
	bpy.context.screen.scene = bpy.data.scenes[origSceneName]
	
	#Run through all of the scenes to find the newly created scene to act as Background Scene
	largestSceneCount = 000
	for sceneName in bpy.data.scenes.keys():
		if(sceneName[:5] == 'Scene.'):
			if(int(sceneName[6:9] > largestSceneCount)):
				largestSceneCount = int(sceneName[6:9])
	
	tmpSceneName = "Scene." + "{0:0=3d}".format(largestSceneCount)
	bpy.data.scenes[tmpSceneName].name = name
	scene = bpy.data.scenes[name]
	return scene

def _delete_background_scene():
	"""
	Deletes the background scene to conserve memory

	"""

	origSceneName = bpy.context.scene.name
	bpy.context.screen.scene = bpy.data.scenes["backgroundScene"]
	bpy.ops.scene.delete()
	bpy.context.screen.scene = bpy.data.scenes[origSceneName]

def _bmesh_from_object(obj, transform = True, triangulate = True, apply_modifiers = False):
	"""
	Returns a transformed, triangulated copy of the mesh
	"""

	assert(obj.type == 'MESH')

	if apply_modifiers and obj.modifiers:
		me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW', calc_tessface = False)
		bm = bmesh.new()
		bm.from_mesh(me)
		bpy.data.meshes.remove(me)
	else:
		me = obj.data
		if obj.mode == 'EDIT':
			bm_orig == bmesh.from_edit_mesh(me)
			bm = bm_orig.copy()
		else:
			bm = bmesh.new()
			bm.from_mesh(me)

	#remove custom data layers to conserve memory
	for elem in (bm.faces, bm.edges, bm.verts, bm.loops):
		for layers_name in dir(elem.layers):
			if not layers_name.startswith("_"):
				layers = getattr(elem.layers, layers_name)
				for layer_name, layer in layers.items():
					layers.remove(layer)

	if transform:
		bm.transform(obj.matrix_world)

	if triangulate:
		bmesh.ops.triangulate(bm, faces = bm.faces)

	return bm

def check_intersection(obj, obj2):
	"""
	Check if any faces intersect with the other object

	Returns a boolean
	"""

	assert(obj != obj2)

	#Triangulate
	bm = _bmesh_from_object(obj)
	bm2 = _bmesh_from_object(obj2)

	#We want to loop over the mesh that has less edges
	#We cast less rays from the simpler object
	if len(bm.edges) > len(bm2.edges):
		bm2, bm = bm, bm2

	#Create a new mesh for ray cast testing
	scene = _create_background_scene()
	me_tmp = bpy.data.meshes.new(name="temp")
	bm2.to_mesh(me_tmp)
	bm2.free()
	obj_tmp = bpy.data.objects.new(name=me_tmp.name, object_data=me_tmp)
	scene.objects.link(obj_tmp)
	scene.update()
	ray_cast = obj_tmp.ray_cast

	intersect = False

	EPS_NORMAL = 0.000001
	EPS_CENTER = 0.01

	#Loops through edges in bm
	for ed in bm.edges:
		v1, v2 = ed.verts

		#Setup the edge with an offset
		co_1 = v1.co.copy()
		co_2 = v2.co.copy()
		co_mid = (co_1+co_2)*0.5
		no_mid = (v1.normal + v2.normal).normalized() * EPS_NORMAL
		co_1 = co_1.lerp(co_mid, EPS_CENTER) + no_mid
		co_2 = co_2.lerp(co_mid,EPS_CENTER) + no_mid

		intersect, co, no, index = ray_cast(co_1, (co_2 - co_1).normalized(), ed.calc_length())

	#Unlinks object and removes data
	scene.objects.unlink(obj_tmp)
	bpy.data.objects.remove(obj_tmp)
	bpy.data.meshes.remove(me_tmp)

	scene.update()
	_delete_background_scene() #Potentially slows the script down since a new scene has to be created and deleted each iteration
	return intersect

def return_intersecting_meshs():
	'''
	Returns the first pair of meshe that intersect

	Returns a tuple string of names of meshes or ('N','A')

	Hard Coded for least computation
	'''
	mesh_names = [
		"UR5_Base", #0
		"UR5_Elbow", #1
		#"UR5_Mount", - extraneous because it is too low and small
		"UR5_Shoulder", #2
		"UR5_Wrist_1", #3
		"UR5_Wrist_2", #4
		"UR5_Wrist_3" #5
	]
	test_pairs = [ 
		(3,1),
		(5,1),
		(4,1),
		(3,2),
		(5,2),
		(4,2),
		(3,0),
		(5,0),
		(4,0)
	]
	for pair in test_pairs:
		if check_intersection(obj.data.objects[mesh_names[pair[0]]], obj.data.objects[mesh_names[pair[1]]]):
			return (mesh_names[pair[0]],mesh_names[pair[1]])

	return None