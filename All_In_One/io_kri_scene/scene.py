__author__ = ['Dzmitry Malyshau']
__bpydoc__ = 'Scene module of KRI exporter.'

import mathutils
import math
from io_kri.common	import *
from io_kri.action	import *
from io_kri_mesh.mesh	import *


def cook_mat(mat,log):
	textures = []
	for mt in mat.texture_slots:
		if mt == None: continue
		it = mt.texture
		if it == None: continue
		if it.type != 'IMAGE':
			log.log(2, 'w','Texture "%s": type is not IMAGE' % (it.name))
			continue
		if it.image == None:
			log.log(2, 'w','Texture "%s": image is not assigned' % (it.name))
			continue
		wrap_x = ((0, 1)[it.repeat_x != 0], -1)[it.use_mirror_x]
		wrap_y = ((0, 1)[it.repeat_y != 0], -1)[it.use_mirror_y]
		textures.append(('Texture', {
			'name'	: mt.name,
			'image'	: ('Image', {
				'path': it.image.filepath,
				'space': it.image.colorspace_settings.name,
				'mapping': it.image.mapping,
			}),
			'filter': (1, (2, 3)[it.use_mipmap])[it.use_interpolation],
			'wrap'	: ([wrap_x, wrap_y, 0],),
			'scale'	: list(mt.scale),
			'offset': list(mt.offset),
		}))
	kind = 'phong'
	if mat.use_shadeless:
		kind = 'flat'
	elif mat.use_tangent_shading:
		kind = 'anisotropic'
	diff_params = [mat.diffuse_intensity, float(mat.emit), 0.0, mat.alpha]
	spec_params = [mat.specular_intensity, float(mat.specular_hardness), 0.0, mat.specular_alpha]
	return ('Material', {
		'name'		: mat.name,
		'shader'	: kind,
		'transparent': mat.use_transparency,
		'data'		: {
			'Ambient'		: ('scalar',	[mat.ambient]),
			'DiffuseColor'	: ('color',		list(mat.diffuse_color)),
			'DiffuseParams'	: ('vector',	diff_params),
			'SpecularColor'	: ('color',		list(mat.specular_color)),
			'SpecularParams': ('vector',	spec_params),
		},
		'textures'	: textures,
	})


def cook_space(matrix, name, log):
	pos, rot, sca = matrix.decompose()
	scale = (sca.x + sca.y + sca.z)/3.0
	if sca.x*sca.x+sca.y*sca.y+sca.z*sca.z > 0.01 + sca.x*sca.y+sca.y*sca.z+sca.z*sca.x:
		log.log(1,'w', 'Non-uniform scale (%.1f,%.1f,%.1f) on %s' % (sca.x, sca.y, sca.z, name))
	return {
		'pos'	: list(pos),
		'rot'	: [rot.x, rot.y, rot.z, rot.w],
		'scale'	: scale,
	}

def cook_node(ob, log):
	return {
		'name'		: ob.name,
		'space'		: cook_space(ob.matrix_local, ob.name, log),
		'children'	: [],
		'actions'	: [],
	}

def cook_camera(cam, log):
	return {	#todo: ortho
		'name'	: cam.name,
		'angle'	: [cam.angle_x, cam.angle_y],
		'range'	: [cam.clip_start, cam.clip_end],
		'actions' : [],
	}

def cook_lamp(lamp, log):
	attenu = [0.0, 0.0]
	sphere = False
	params = []
	kind = lamp.type
	if kind not in ('SUN', 'HEMI'):
		attenu = [lamp.linear_attenuation, lamp.quadratic_attenuation]
	if kind in ('SPOT', 'POINT'):
		sphere = lamp.use_sphere
	if kind == 'SPOT':
		params = [lamp.spot_size, lamp.spot_blend, 0.1]
	elif kind == 'AREA':
		params = [lamp.size, lamp.size_y, 0.1]
	return {
		'name'			: lamp.name,
		'kind'			: kind,
		'parameters'	: params,
		'color'			: list(lamp.color),
		'energy'		: lamp.energy,
		'attenuation'	: attenu,
		'distance'		: lamp.distance,
		'spherical'		: sphere,
		'actions'		: [],
	}

def cook_armature(arm, log):
	root = { 'children': [] }
	bones = { '':root }
	for b in arm.bones:
		par = bones['']
		mx = b.matrix_local
		if b.parent:
			par = bones[b.parent.name]
			mx = b.parent.matrix_local.copy().inverted() * mx
		ob = {
			'name'		: b.name,
			'space'		: cook_space(mx, b.name, log),
			'children'	: [],
		}
		par['children'].append(ob)
		bones[b.name] = ob
	return {
		'name'		: arm.name,
		'dual_quat'	: False,
		'bones'		: root['children'],
		'actions'	: [],
	}


def export_value(elem, ofile, num_format, level):
	import collections
	#print('Exporting: %s at level %s' % (str(elem), level))
	new_line = '\n%s' % (level * '\t')
	tip = type(elem)
	if tip is dict: # map
		ofile.write('{')
		for key,val in elem.items():
			ofile.write('%s\t%s\t: ' % (new_line, key))
			export_value(val, ofile, num_format, level+1)
			ofile.write(',' )
		ofile.write(new_line + '}')
	elif tip is tuple: # object/enum
		assert len(elem) <= 2
		if len(elem) > 1:
			first = elem[0]
			tfirst = type(first)
			if tfirst is str:
				ofile.write(first)
			else:
				raise Exception('Tuple fist element %s is unknown: %s' % (str(tfirst), str(first)))
		last = elem[len(elem)-1]
		if len(last):
			ofile.write('(')
			tlast = type(last)				
			if tlast is dict:
				for key,val in last.items():
					ofile.write('%s\t%s\t: ' % (new_line, key))
					export_value(val, ofile, num_format, level+1)
					ofile.write(',')
			elif tlast is list:
				for i,val in enumerate(last):
					export_value(val, ofile, num_format, level+1)
					if i != len(last) - 1:
						ofile.write(', ')
			else:
				raise Exception('Tuple last element %s is unknown: %s' % (str(tlast), str(last)))
			ofile.write(new_line + ')')
	elif tip is bool:
		ofile.write(('false', 'true')[elem])
	elif tip is int:
		ofile.write(str(elem))
	elif tip is float:
		ofile.write(num_format % (elem))
	elif tip is str:
		ofile.write('"%s"' % (elem))
	elif tip is list: #array
		if len(elem):
			subtip = type(elem[0])
			is_class = subtip in (tuple, dict, list, str)
			ofile.write('[')
			for i,sub in enumerate(elem):
				assert type(sub) == subtip
				ofile.write(new_line + '\t')
				export_value(sub, ofile, num_format, level)
				ofile.write(',')
			ofile.write(new_line + ']')
		else:
			ofile.write('[]')
	else:
		raise Exception('Element %s is unknown' % (str(type(elem))))


def export_ron(document,filepath,num_format):
	ofile = open(filepath+'.ron','w')
	export_value(document, ofile, num_format, 1)
	ofile.close()


def save_scene(filepath, context, export_meshes, export_actions, precision):
	glob		= {}
	materials	= []
	nodes		= []
	cameras		= []
	lights		= []
	entities	= []
	# ready...
	import os
	if filepath.endswith('.ron'):
		filepath = filepath[:-4] # cut off the extension here
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	log	= Logger(filepath+'.log')
	out_mesh, out_act_node, out_act_arm = None, None, None
	collection_mesh, collection_node_anim = 'all', 'nodes'
	if export_meshes:
		out_mesh	= Writer('%s/%s.k3mesh' % (filepath, collection_mesh))
	if export_actions:
		out_act_node= Writer('%s/%s.k3act' % (filepath, collection_node_anim))
	sc = context.scene
	print('Exporting Scene...')
	log.logu(0, 'Scene %s' % (filepath))
	# -globals
	bDegrees = (sc.unit_settings.system_rotation == 'DEGREES')
	if not bDegrees:
		#it's easier to convert on loading than here
		log.log(1, 'w', 'Radians are not supported')
	if sc.use_gravity:
		gv = sc.gravity
		log.log(1, 'i', 'gravity: (%.1f,%.1f,%.1f)' % (gv.x, gv.y, gv.z))
		glob['gravity'] = list(sc.gravity)
	else:
		glob['gravity'] = [0,0,0]
	# -materials
	for mat in context.blend_data.materials:
		if log.stop:	break
		materials.append(cook_mat(mat, log))
		#save_actions( mat, 'm','t' )
	# -nodes
	node_tree = {}
	for ob in sc.objects:
		node_tree[ob.name] = n = cook_node(ob,log)
		if ob.parent == None:
			nodes.append(n)
		else:
			node_tree[ob.parent.name]['children'].append(n)
	del node_tree
	# steady...
	for ob in sc.objects:
		if log.stop:	break
		# parse node
		if len(ob.modifiers):
			log.log(1, 'w', 'Unapplied modifiers detected on object %s' % (ob.name))
		current = {
			'actions'	: [],
		}
		if ob.type == 'MESH':
			if out_mesh != None:
				(_, bounds, face_num) = save_mesh(out_mesh, ob, log)
			else:
				(_, bounds, face_num) = collect_attributes(ob.data, None, ob.vertex_groups, True, log)
			if ob.data.materials == []:
				log.log(1, 'w', 'No materials detected')
			has_arm = ob.parent and ob.parent.type == 'ARMATURE'
			current = {
				'node'		: ob.name,
				'mesh'		: '%s@%s' % (ob.data.name, collection_mesh),
				'armature'	: ob.parent.data.name if has_arm else '',
				'bounds'	: ('Bounds', {
					'min': list(bounds[0]),
					'max': list(bounds[1]),
				}),
				'fragments' : [],
				'actions'	: [],
			}
			entities.append(('Entity', current))
			offset = 0
			for fn, m in zip(face_num, ob.data.materials):
				if not fn: break
				s = (m.name	if m else '')
				log.logu(1, '+entity: %d faces, [%s]' % (fn,s))
				fragment = ('Fragment', {
					'material'	: s,
					'slice'		: [3*offset, 3*(offset+fn)],
				})
				current['fragments'].append(fragment)
				offset += fn
		elif ob.type == 'ARMATURE':
			arm = cook_armature(ob.data, log)
			current['node'] = ob.name
			name = ob.data.name
			ani_path = (None, '%s/%s' % (filepath,name))[export_actions]
			anims = save_actions_ext(ani_path, ob, 'pose', log)
			for ani in anims:
				current['actions'].append('%s@%s' % (ani,name))
		elif ob.type == 'CAMERA':
			current = cook_camera(ob.data, log)
			current['node'] = ob.name
			cameras.append(('Camera', current))
		elif ob.type == 'LAMP':
			current = cook_lamp(ob.data, log)
			current['node'] = ob.name
			lights.append(('Lamp', current))
		# animations
		anims = save_actions_int(out_act_node, ob, None, log)
		for ani in anims:
			current['actions'].append('%s@%s' % (ani, collection_node_anim))
	if out_mesh != None:
		out_mesh.close()
	if out_act_node != None:
		out_act_node.close()
	# go!
	document = {
		'global'	: glob,
		'materials'	: materials,
		'nodes'		: nodes,
		'cameras'	: cameras,
		'lights'	: lights,
		'entities'	: entities,
	}
	num_format = '%' + ('.%df' % precision)
	export_ron(document, filepath, num_format)
	# finish
	print('Done.')
	log.conclude()
