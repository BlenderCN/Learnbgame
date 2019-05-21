import bpy

TEMPLATE_FILE = '''{{
	"exporter_version": [0,0,2],
	"faces": [{0}],
	"vertices": [{1}],
	"uv": [{2}],
	"vertex_group_indices": [{3}],
	"vertex_group_weights": [{4}],
	"vertex_group_names": [{5}],
	"bones": [{6}],
	"bone_names": [{7}],
	"animations": {{{8}}}
}}'''

TEMPLATE_ANIMATION = '''"{name}":{{"length":{length}, "curves":{{{curves}}}}}'''

TEMPLATE_ANIMATION_BONE = '''"{bone}":[{curves}]
'''
TEMPLATE_CURVE = '''{{"type":["{type}",{array_index}], "keys":[{keyframes}]}}
'''

TEMPLATE_KEYFRAME = '''[{frame},{value},[{handle_left}],[{handle_right}]]'''


def write(filepath):
	bpy.ops.object.mode_set(mode='OBJECT')
	out = open(filepath, "w")
	
	'''setup objects'''

	armature = False
	object = False
	mesh = False
	
	# if only one object is selected
	if len(bpy.context.selected_objects) == 1:
		tmp = bpy.context.selected_objects[0]
		#if selected object is mesh
		if tmp.type == 'MESH':
			object = tmp
			mesh = tmp.data
			if tmp.parent and tmp.parent.type == 'ARMATURE':
				armature = tmp.parent
		#if selected object is armature and has only one child
		elif tmp.type == 'ARMATURE':
			if len(tmp.children) == 1:
				armature = tmp
				object = armature.children[0]
				mesh = object.data
	#if could not init object from selection just pick first mesh in data
	if not object:
		for o in bpy.data.objects:
			if o.type == 'MESH':
				object = o
				mesh = o.data
				if o.parent:
					armature = o.parent
				break
	if armature:
		sort_vertex_groups(object, armature)
	''' '''

	faces = faces_string(mesh)

	vertices = vertices_string(object, mesh)
	
	uv = uv_string(mesh)

	vertex_group_indices = vertex_group_indices_string(mesh)
	vertex_group_weights = vertex_group_weights_string(mesh, armature)

	vertex_group_names = vertex_group_names_string(object)

	bones = ''
	bone_names = ''
	animations = ''
	if armature:
		bones = bones_string(armature)
		bone_names = bone_names_string(armature)
		animations = animations_string(armature)
	
	out.write(TEMPLATE_FILE.format(faces, vertices, uv, vertex_group_indices, vertex_group_weights, vertex_group_names, bones, bone_names, animations))
	out.close()


''' Sync vertex group indices with bones. '''
def sort_vertex_groups(object, armature):
	#need to change context to modify vertex groups
	bpy.context.scene.objects.active=object
	bones = armature.data.bones
	groups = object.vertex_groups
	for i in range(0, len(bones)):
		bone = bones[i]
		group = groups[bone.name]
		bpy.ops.object.vertex_group_set_active(group=group.name)
		while group.index != i:
			bpy.ops.object.vertex_group_move(direction='UP')


def faces_string(mesh):
	str_list = []
	for face in mesh.polygons:
		str_list.append('['+ ','.join(map(lambda x: str(x), face.vertices)) + ']' )
	return ','.join(str_list)


def vertices_string(object, mesh):
	str_list = []
	for vertex in mesh.vertices:
		coord = object.matrix_world * vertex.co
		str_list.append(str(coord[0]))
		str_list.append(str(-coord[1]))
		str_list.append(str(coord[2]))
	return ','.join(str_list)


def uv_string(mesh):
	str_list = []
	for v in mesh.uv_layers[0].data:
		str_list.append(str(v.uv[0]))
		str_list.append(str(1-v.uv[1]))
	return ','.join(str_list)

def vertex_group_indices_string(mesh):
	all_vertices = []
	for vertex in mesh.vertices:
		groups = []
		for group in vertex.groups:
			groups.append(str(group.group))
		all_vertices.append('[' + ','.join(groups) +']')
	return ','.join(all_vertices)

def vertex_group_weights_string(mesh, armature):
	bone_amount = 0
	if armature:
		bone_amount = len(armature.data.bones)
	all_vertices = []
	for vertex in mesh.vertices:
		groups = []
		for group in vertex.groups:
			if group.group < bone_amount:
				groups.append(str(group.weight))
		all_vertices.append('[' + ','.join(groups) +']')
	return ','.join(all_vertices)

def vertex_group_names_string(object):
	groups = []
	for group in object.vertex_groups:
		groups.append('"'+group.name+'"')
	return ','.join(groups)

def bones_string(armature):
	#bones have no index so have to do this dict thing...
	index_dict = {}
	bones_list = []
	for i in range(0, len(armature.data.bones)):
		bone = armature.data.bones[ i ]
		index_dict[bone.name] = i
		head = armature.matrix_world * bone.head_local;
		parent = -1
		if bone.parent:
			parent = index_dict[bone.parent.name]
		bone_string = '[' + str(head[0]) + ','+str(-head[1])+','+str(head[2]) +','+str(parent)+']'
		bones_list.append(bone_string)

	return ','.join(bones_list)

def bone_names_string(armature):
	bones_list = []
	for i in range(0, len(armature.data.bones)):
		bone = armature.data.bones[ i ]
		bones_list.append('"'+bone.name+'"')
	return ','.join(bones_list)
		

def animations_string(armature):
	#bones have no index so have to do this dict thing...
	index_dict = {}
	for i in range(0, len(armature.data.bones)):
		bone = armature.data.bones[ i ]
		index_dict[bone.name] = i

	animations_list = []
	for track in armature.animation_data.nla_tracks:
		if len(track.strips) < 1:
			continue
		last_frame = track.strips[len(track.strips)-1].frame_end
		bones={}
		#strips and keyframes are always sorted
		for strip in track.strips:
			for bone in strip.action.groups:
				for curve in bone.channels:
					type = curve.data_path.rsplit('.', 1)[1]
					axis = curve.array_index
					if type == 'rotation_quaternion':
						type = 'q'
					elif type == 'location':
						type = 'l'
					elif type == 'scale':
						type = 's'
					else:
						print('unsupported curve type (euler or something)')
					keyframes = []
					for keyframe in curve.keyframe_points:
						value = keyframe.co[1]
						handle_left = keyframe.handle_left.copy()
						handle_right = keyframe.handle_right.copy()
						#mirror y-axis, cross your fingers
						if (type == 'q' and (axis == 0 or axis == 1)) or (type == 'l' and axis == 1):
							value *= -1
							handle_left[1] *= -1
							handle_right[1] *= -1
						handle_left[0] += strip.frame_start
						handle_right[0] += strip.frame_start
						
						keyframes.append(TEMPLATE_KEYFRAME.format(frame=keyframe.co[0] + strip.frame_start, value=value, handle_left=','.join(map(lambda x: str(x), handle_left)), handle_right=','.join(map(lambda x: str(x), handle_right))))
					#get curves of correct type&array_index (if exists) and extend keyframes
					bones.setdefault(bone.name, {}).setdefault(type, {}).setdefault(axis, []).extend(keyframes)
		print(len(bones))
		bone_strings = []		
		for bone_name in bones.keys():
			curves = []
			bone = bones[bone_name]
			for curve_type in bone.keys():
				for array_index in bone[curve_type].keys():
					curves.append(TEMPLATE_CURVE.format(type=curve_type, array_index=array_index, keyframes=','.join(bone[curve_type][array_index])))
			bone_strings.append(TEMPLATE_ANIMATION_BONE.format(bone=index_dict[bone_name], curves=','.join(curves)))
			
		animations_list.append(TEMPLATE_ANIMATION.format(name=track.name, length=last_frame, curves=','.join(bone_strings) ))
	return ','.join(animations_list)
