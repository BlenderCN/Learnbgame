
import bpy;
import struct;
from bpy_extras.io_utils import ExportHelper

def write(operator, context, filepath, p_export_animation, p_export_selection_only, p_apply_modifiers, p_export_global_matrix, p_export_uv, p_frame_skip, p_export_vertex_groups):

	# Use OBJECT mode to allow data access. 
	bpy.ops.object.mode_set(mode='OBJECT')

	# Set the default return state
	result = {'FINISHED'}

	# Round a 2D vector
	def veckey2d(v):
		return round(v[0], 4), round(v[1], 4)
	# Round a 3D vector
	def veckey3d(v):
		return round(v.x, 4), round(v.y, 4), round(v.z, 4)
	# Triangulate the given mesh
	def triangulate(me):
		import bmesh
		bm = bmesh.new()
		bm.from_mesh(me)
		bmesh.ops.triangulate(bm, faces=bm.faces)
		bm.to_mesh(me)
		bm.free()
		
	EXPORT_TRIANGULATE = True
	scene = context.scene
	orig_frame = scene.frame_current 
	
	if p_export_selection_only:
		objects = context.selected_objects
	else:
		objects = context.scene.objects

	if p_export_animation:
		scene_frames = range(scene.frame_start, scene.frame_end + 1, (p_frame_skip + 1))  # Up to and including the end frame.
	else:
		scene_frames = [orig_frame]  # Don't export animation

	file = open(filepath,'w')

	# Go through the selected frame range; export vertex positions
	for frame in scene_frames:
		# Set current frame in blender
		scene.frame_set(frame,subframe=0.0)
		#bpy.context.scene.set_frame(frame)
		# 'F' in out file means new frame
		file.write('F\n')
		for ob_main in objects:
			# Skip objects which are not meshes
			if not ob_main or ob_main.type != 'MESH':
				continue
			# Convert object to mesh; apply transformations and modifiers
			me = ob_main.to_mesh(context.depsgraph, p_apply_modifiers )
			me.transform(p_export_global_matrix * ob_main.matrix_world)
			# Triangulate mesh
			if EXPORT_TRIANGULATE:
				triangulate(me)
			# Export all vertices
			for v in enumerate(me.vertices):
				x = v[1].co.x
				y = v[1].co.y
				z = v[1].co.z
				exp_str = "V "+ str(x)+" "+str(y) + " " +str(z)+"\n";
				file.write(exp_str)

	# Export face data (index + UV coords)
	tot_verts = 0
	for ob_main in objects:
		# Skip objects which are not meshes
		if not ob_main or ob_main.type != 'MESH':
			continue
		# Transform object, convert into mesh
		me = ob_main.to_mesh(context.depsgraph, apply_modifiers=p_apply_modifiers )
		me.transform(p_export_global_matrix * ob_main.matrix_world)		
		# Triangulate it if needed
		if EXPORT_TRIANGULATE:
			triangulate(me)
		me_verts = me.vertices[:]
		face_index_pairs = [(face, index) for index, face in enumerate(me.polygons)]
		# Does the object have a UV layer?
		faceuv = p_export_uv and (len(me.uv_layers) > 0)  
		# Set the UV layer we are going to export
		if faceuv:
			uv_layer = me.uv_layers.active.data[:]

		uv_face_mapping = [None] * len(face_index_pairs)
		uv_dict = {}
		uv_get = uv_dict.get
		# Go through all faces
		for f, f_index in face_index_pairs:
			f_v = [(vi, me_verts[v_idx], l_idx) for vi, (v_idx, l_idx) in enumerate(zip(f.vertices, f.loop_indices))]
			file.write('f ')

			# Write vertex indices of the current face
			for vi, v, li in f_v:
				file.write(str(v.index+tot_verts)+" ")
			file.write('\n')
			# Write the UV of the face (in case it's needed)
			if faceuv:
				file.write('u ')
				uv_ls = uv_face_mapping[f_index] = []
				for uv_index, l_index in enumerate(f.loop_indices):
					uv = uv_layer[l_index].uv
					uv_key = veckey2d(uv)
					uv_val = uv_get(uv_key)
					file.write(str(uv_key[0])+" "+str(uv_key[1])+" ")

					uv_ls.append(uv_val)
				file.write('\n')
				
				
		# Count total number of vertex groups used
		file.write('G ' + str(countUsedVertexGroups(ob_main)) + '\n')
		
		# Export vertex groups for the current object
		exportVertexGroups(file, ob_main, tot_verts)			
				
		# Count total vertices. Needed to determine vertex index offset for the next object
		tot_verts += len(me.vertices)
		
	file.close()
	return result

# Count total number of vertex groups used
def countUsedVertexGroups(ob_main):
	numberGroups = 0	
	for v in ob_main.data.vertices:
		for g in v.groups:
			numberGroups = max(numberGroups, g.group+1)
	return numberGroups

# Write vertex groups to file (vertex index, group index, vertex weight)
def exportVertexGroups(file, ob_main, tot_verts):
	for v in ob_main.data.vertices:
		for g in v.groups:
			if g.weight <= 0 :
				continue
			file.write('W ' + str(v.index + tot_verts) + ' ' + str(g.group) + ' ' + str(g.weight) + '\n')	
	