import bpy
import bmesh

"""
Script to check if any of the mesh goes below the safe table area

Returns the mesh that does do so
"""

bottom_limit = 0.0

def set_bottom_limit(z):
	this.bottom_limit = z

def _bmesh_from_object(obj):
	"""
	Returns the transformed bmesh for an object mesh
	"""


	assert(obj.type == 'MESH')

	if False and obj.modifiers:
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

	bm.transform(obj.matrix_world)
	bmesh.ops.triangulate(bm, faces = bm.faces)
	return bm

def check_limit(obj):
	"""
	Returns if input mesh goes below the bottom limit
	"""

	me = _bmesh_from_object(obj)
	verts = me.verts
	verts.ensure_lookup_table()
	smallest_z = 999
	for vert in verts:
		if vert.co[2] < smallest_z:
			smallest_z = vert.co[2]
	return smallest_z <= bottom_limit

def return_limiting_mesh():
	"""
	Returns the first mesh as a String that goes below the bottom limit
	
	Hard coded for least computation
	"""
	mesh_names = [
		#"UR5_Base", - will never move in the z axis
		#"UR5_Mount", - extraneous because it is too low and small
		"UR5_Shoulder",
		"UR5_Elbow",
		"UR5_Wrist_1",
		"UR5_Wrist_2",
		"UR5_Wrist_3"
	]
	for name in mesh_names:
		if(check_limit(bpy.data.objects[name]) == True):
			return name
	return None