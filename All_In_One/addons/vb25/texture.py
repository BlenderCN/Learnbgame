'''

  V-Ray/Blender

  http://vray.cgdo.ru

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Blender modules '''
import bpy

''' vb modules '''
from vb25.utils   import *
from vb25.plugins import *


def write_TexAColor(bus, name, node, color_a, mult):
	ofile= bus['files']['textures']
	scene= bus['scene']

	tex_name= "TACOP%sNO%s" % (name, clean_string(node.name))

	ofile.write("\nTexAColorOp %s {" % tex_name)
	ofile.write("\n\tcolor_a= %s;" % color_a)
	ofile.write("\n\tmult_a= %s;" % a(sce,mult))
	ofile.write("\n}\n")

	return tex_name


def write_TexAColor(bus, name, node, color):
	ofile= bus['files']['textures']
	scene= bus['scene']

	tex_name= "TAC%sNO%s" % (name, clean_string(node.name))

	ofile.write("\nTexAColor %s {" % tex_name)
	ofile.write("\n\ttexture= %s;" % a(scene, color))
	ofile.write("\n}\n")

	return tex_name


def write_TexCompMax(ofile, sce, params):
	OPERATOR= {
		'Add':        0,
		'Substract':  1,
		'Difference': 2,
		'Multiply':   3,
		'Divide':     4,
		'Minimum':    5,
		'Maximum':    6
	}

	tex_name= "TexCompMax_%s"%(params['name'])

	ofile.write("\nTexCompMax %s {" % tex_name)
	ofile.write("\n\tsourceA= %s;" % params['sourceA'])
	ofile.write("\n\tsourceB= %s;" % params['sourceB'])
	ofile.write("\n\toperator= %d;" % OPERATOR[params['operator']])
	ofile.write("\n}\n")

	return tex_name


def write_TexFresnel(ofile, sce, ma, ma_name, textures):
	tex_name= "TexFresnel_%s"%(ma_name)

	ofile.write("\nTexFresnel %s {" % tex_name)
	if 'reflect' in textures:
		ofile.write("\n\tblack_color= %s;" % textures['reflect'])
	else:
		ofile.write("\n\tblack_color= %s;" % a(sce,"AColor(%.6f, %.6f, %.6f, 1.0)"%(tuple([1.0 - c for c in ma.vray_reflect_color]))))
	ofile.write("\n\tfresnel_ior= %s;" % a(sce,ma.vray.BRDFVRayMtl.fresnel_ior))
	ofile.write("\n}\n")

	return tex_name


def write_TexInvert(bus):
	ofile= bus['files']['textures']

	tex_name= "TI%s" % bus['mtex']['name']

	ofile.write("\nTexInvert %s {" % tex_name)
	ofile.write("\n\ttexture= %s;" % bus['mtex']['name'])
	ofile.write("\n}\n")

	return tex_name


def write_texture(bus):
	scene   = bus['scene']
	texture = bus['mtex']['texture']

	if not append_unique(bus['cache']['textures'], bus['mtex']['name']):
		if not 'env' in bus['mtex']:
			if 'material' in bus:
				bus['material']['normal_uvwgen'] = bus['cache']['uvwgen'].get(bus['mtex']['name'], bus['defaults']['uvwgen'])
		return bus['mtex']['name']

	if texture.use_nodes:
		return write_node_texture(bus)

	if texture.type == 'IMAGE':
		return PLUGINS['TEXTURE']['TexBitmap'].write(bus)

	elif texture.type == 'VOXEL_DATA':
		return bus['mtex']['name']

	elif texture.type == 'VRAY':
		VRayTexture = texture.vray

		if VRayTexture.type == 'NONE':
			return None

		return PLUGINS['TEXTURE'][VRayTexture.type].write(bus)

	else:
		debug(scene, "Texture \"%s\": \'%s\' type is not supported." % (texture.name, texture.type), error=True)
		return None



'''
  TEXTURE STACK

  Stack naming:
    BAbase_name+TEtexture_name+IDtexture_id_in_stack+PLplugin
  like:
    MAmaterial+TEtexture+IDtexture_id_in_stack
  or:
    LAlamp+TEtexture+IDtexture_id_in_stack
'''
def write_factor(bus):
	ofile=   bus['files']['textures']
	scene=   bus['scene']

	texture= bus['mtex']['texture']
	factor=  bus['mtex']['factor']

	if factor == 1.0:
		return bus['mtex']['name']

	tex_name= "TF%sF%s" % (bus['mtex']['name'], clean_string("%.3f" % factor))

	if factor > 1.0:
		if 0:
			ofile.write("\nTexOutput %s {" % tex_name)
			ofile.write("\n\ttexmap= %s;" % bus['mtex']['name'])
			ofile.write("\n\tcolor_mult= %s;" % a(scene, "AColor(%.3f,%.3f,%.3f,1.0)" % tuple([factor]*3)))
			ofile.write("\n}\n")
		else:
			ofile.write("\nTexAColorOp %s {" % tex_name)
			ofile.write("\n\tcolor_a= %s;" % bus['mtex']['name'])
			ofile.write("\n\tmult_a= %s;" % a(scene, factor))
			ofile.write("\n}\n")
	else:
		ofile.write("\nTexAColorOp %s {" % tex_name)
		ofile.write("\n\tcolor_a= %s;" % bus['mtex']['name'])
		ofile.write("\n\tmult_a= 1.0;")
		ofile.write("\n\tresult_alpha= %s;" % a(scene, factor))
		ofile.write("\n}\n")

	return tex_name


def stack_write_texture(bus):
	slot=    bus['mtex']['slot']
	texture= bus['mtex']['texture']
	mapto=   bus['mtex']['mapto']

	VRayTexture= texture.vray
	VRaySlot=    texture.vray_slot

	bus['mtex']['name']= write_factor(bus)

	# IMPROVE: Bump invert button quick fix
	# There is no invert control for bump
	# so use normal
	if mapto == 'bump':
		mapto = 'normal'

	mapto_invert= 'map_%s_invert' % mapto
	if hasattr(VRaySlot, mapto_invert):
		if getattr(VRaySlot, mapto_invert):
			bus['mtex']['name']= write_TexInvert(bus)

	return bus['mtex']['name']


def remove_alpha(bus):
	ofile=   bus['files']['textures']
	scene=   bus['scene']

	texture= bus['mtex']['texture']

	tex_name= "NOALPHA%s" % (bus['mtex']['name'])

	ofile.write("\nTexAColorOp %s {" % tex_name)
	ofile.write("\n\tcolor_a= %s;" % bus['mtex']['name'])
	ofile.write("\n\tmult_a= 1.0;")
	ofile.write("\n\tresult_alpha= 1.0;")
	ofile.write("\n}\n")

	return tex_name


def write_sub_texture(bus, mtex):
	# Store mtex context
	context_mtex = bus['mtex']

	bus['mtex'] = mtex

	tex_name = write_texture(bus)

	# Restore mtex context
	bus['mtex'] = context_mtex

	return tex_name


def write_sub_textures(bus, rna_pointer, params):
	mapped_params= {}
	for key in params:
		sub_tex_name= getattr(rna_pointer, key)
		if sub_tex_name:
			scene= bus['scene']

			sub_tex= get_data_by_name(scene, 'textures', sub_tex_name)

			if sub_tex:
				texture= bus['mtex']['texture']

				mtex= {}
				mtex['mapto']=   key
				mtex['slot']=    None
				mtex['texture']= sub_tex
				mtex['factor']=  1.0
				mtex['name']=    clean_string("TE%sST%s" % (texture.name,
															sub_tex.name))

				mapped_params[key]= write_sub_texture(bus, mtex)
	return mapped_params


'''
  TEXTURE STACK
'''
def stack_write_TexLayered(bus, layers):
	if len(layers) == 1:
		return layers[0][0]

	ofile= bus['files']['textures']

	BLEND_MODES= {
		'NONE':         '0',
		'STENCIL':      '1',
		'OVER':         '1',
		'IN':           '2',
		'OUT':          '3',
		'ADD':          '4',
		'SUBTRACT':     '5',
		'MULTIPLY':     '6',
		'DIFFERENCE':   '7',
		'LIGHTEN':      '8',
		'DARKEN':       '9',
		'SATURATE':    '10',
		'DESATUREATE': '11',
		'ILLUMINATE':  '12',
	}

	tex_name= 'TL%s' % (''.join([l[0] for l in layers[1:]]))

	if not append_unique(bus['cache']['textures'], tex_name):
		return tex_name

	ofile.write("\nTexLayered %s {" % tex_name)
	ofile.write("\n\ttextures= List(%s);" % (','.join([l[0] for l in layers])))
	ofile.write("\n\tblend_modes= List(%s);" % (','.join([BLEND_MODES[l[1]] for l in layers])))
	ofile.write("\n}\n")

	return tex_name


def stack_write_TexMix(bus, color1, color2, blend_amount):
	ofile= bus['files']['textures']

	tex_name= 'TM%s%s%s' % (color1, color2, blend_amount)

	if not append_unique(bus['cache']['textures'], tex_name):
		return tex_name

	ofile.write("\nTexMix %s {" % tex_name)
	ofile.write("\n\tcolor1= %s;" % color1)
	ofile.write("\n\tcolor2= %s;" % color2)
	ofile.write("\n\tmix_amount= 1.0;")
	ofile.write("\n\tmix_map= %s;" % blend_amount)
	ofile.write("\n}\n")

	return tex_name


def stack_write_textures(bus, layer):
	ofile= bus['files']['textures']
	if type(layer) is dict:
		color_a= stack_write_textures(bus, layer['color_a'])
		color_b= stack_write_textures(bus, layer['color_b'])
		layer_name= stack_write_TexMix(bus, color_a, color_b, layer['blend_amount'])
	elif type(layer) is list:
		layer_name= stack_write_TexLayered(bus, layer)
	return layer_name


def stack_collapse_layers(slots):
	layers= []
	for i,slot in enumerate(slots):
		(texture, stencil, blend_mode)= slot
		if stencil:
			color_a= layers
			color_b= stack_collapse_layers(slots[i+1:])
			if len(color_a) and len(color_b):
				return {'color_a': color_a,
						'color_b': color_b,
						'blend_amount': texture}
		layers.append( (texture, blend_mode) )
	return layers


def write_TexOutput(bus, texmap, mapto):
	ofile = bus['files']['textures']
	scene = bus['scene']

	VRayScene = scene.vray

	if VRayScene.RTEngine.enabled and VRayScene.RTEngine.use_opencl:
		return texmap

	tex_name = "MAPTO%sTE%s" % (mapto, texmap)

	if not append_unique(bus['cache']['textures'], tex_name):
		return tex_name

	ofile.write("\nTexOutput %s {" % tex_name)
	ofile.write("\n\ttexmap=%s;" % texmap)
	ofile.write("\n}\n")

	return tex_name



'''
  NODE TEXTURE
'''
def write_TextureNodeInvert(bus, node, node_params):
	ofile= bus['files']['textures']
	scene= bus['scene']

	node_tree= bus['tex_nodes']['node_tree']

	if 'Color' not in node_params:
		return None

	tex_name= "TI%s" % node_params['Color']

	ofile.write("\nTexInvert %s {" % tex_name)
	ofile.write("\n\ttexture= %s;" % node_params['Color'])
	ofile.write("\n}\n")

	return tex_name


def write_TextureNodeTexture(bus, node, input_params):
	node_tree= bus['tex_nodes']['node_tree']

	mtex = {}
	mtex['mapto']   = 'node'
	mtex['slot']    = None
	mtex['texture'] = node.texture
	mtex['factor']  = 1.0
	mtex['name']    = clean_string("NT%sNO%sTE%s" % (node_tree.name,
													 node.name,
													 node.texture.name))

	tex_name = write_sub_texture(bus, mtex)

	return tex_name


def write_TextureNodeMixRGB(bus, node, input_params):
	ofile= bus['files']['textures']
	scene= bus['scene']

	node_tree= bus['tex_nodes']['node_tree']

	params= {
		'Color1': "",
		'Color2': "",
		'Factor': "",
	}

	for key in params:
		# Key is mapped in input_params
		if key in input_params:
			params[key] = input_params[key]

		# Use node color values
		else:
			if key in ['Color1', 'Color2']:
				c = node.inputs[key].default_value
				params[key] = write_TexAColor(bus, key, node, mathutils.Color((c[0],c[1],c[2])))
			elif key == 'Factor':
				params[key] = write_TexAColor(bus, key, node, mathutils.Color([node.inputs[key].default_value]*3))

	return stack_write_TexMix(bus, params['Color1'], params['Color2'], params['Factor'])


def write_TextureNodeOutput(bus, node, input_params):
	ofile= bus['files']['textures']
	scene= bus['scene']

	params= {
		'Color': "",
	}

	if 'Color' not in input_params:
		c = node.inputs['Color'].default_value
		params['Color'] = write_TexAColor(bus, 'Color', node, mathutils.Color((c[0],c[1],c[2])))
	else:
		params['Color'] = input_params['Color']

	ofile.write("\nTexOutput %s {" % bus['mtex']['name'])
	ofile.write("\n\ttexmap= %s;" % params['Color'])
	ofile.write("\n}\n")

	return bus['mtex']['name']


def write_texture_node(bus, node_tree, node):
	ofile= bus['files']['textures']
	scene= bus['scene']

	VRayScene=      scene.vray
	VRayExporter=   VRayScene.exporter

	node_params= {}

	for input_socket in node.inputs:
		input_node = connected_node(node_tree, input_socket)

		if not input_node:
			continue

		value = write_texture_node(bus, node_tree, input_node)

		if value is not None:
			node_params[input_socket.name]= value

	if VRayExporter.debug:
		print_dict(scene, "Node \"%s\"" % (node.name), node_params)

	if node.type == 'MIX_RGB':
		return write_TextureNodeMixRGB(bus, node, node_params)

	elif node.type == 'OUTPUT':
		return write_TextureNodeOutput(bus, node, node_params)

	elif node.type == 'TEXTURE':
		return write_TextureNodeTexture(bus, node, node_params)

	elif node.type == 'INVERT':
		return write_TextureNodeInvert(bus, node, node_params)

	else:
		return None

	return None


def write_node_texture(bus):
	ofile= bus['files']['textures']
	scene= bus['scene']

	ob=    bus['node']['object']
	base=  bus['node']['base']

	tex=  bus['mtex'].get('texture')
	slot= bus['mtex'].get('slot')

	VRayScene=    scene.vray
	VRayExporter= VRayScene.exporter

	node_tree= tex.node_tree

	output_node_name = None
	if slot and slot.output_node != 'NOT_SPECIFIED':
		output_node_name = slot.output_node

	output_node= get_output_node(node_tree, output_node_name)

	if output_node:
		if VRayExporter.debug:
			debug(scene, "Processing node texture \"%s\":" % (tex.name))

		bus['tex_nodes']= {}
		bus['tex_nodes']['node_tree']= node_tree

		return write_texture_node(bus, node_tree, output_node)

	return None


def write_material_textures(bus):
	ofile= bus['files']['materials']
	scene= bus['scene']
	ma=    bus['material']['material']

	VRayScene=    scene.vray
	VRayExporter= VRayScene.exporter

	VRayMaterial= ma.vray

	mapped_params= PLUGINS['BRDF'][VRayMaterial.type].mapto(bus)

	# Mapped parameters
	bus['textures']= {}

	for i,slot in enumerate(ma.texture_slots):
		if ma.use_textures[i] and slot and slot.texture and (slot.texture.type in TEX_TYPES or slot.texture.use_nodes):
			VRaySlot=    slot.texture.vray_slot
			VRayTexture= slot.texture.vray

			for key in mapped_params:
				if key == 'bump' or getattr(VRaySlot, "map_%s" % (key)):
					factor = getattr(VRaySlot, "%s_mult" % ('normal' if key == 'bump' else key))
					mapto  = key

					if mapto == 'normal' and getattr(VRaySlot, "map_normal") and VRaySlot.BRDFBump.map_type == 'BUMP':
						continue

					if mapto == 'bump' and not (getattr(VRaySlot, "map_normal") and VRaySlot.BRDFBump.map_type == 'BUMP'):
						continue

					if mapto not in bus['textures']: # If texture is first in stack
						bus['textures'][mapto]= []
						# If this texture will be blended over some value
						# we need to add this value
						# (for example, texture blended over diffuse color)
						if factor < 1.0 or VRaySlot.blend_mode != 'NONE' or slot.use_stencil:
							bus['textures'][mapto].append(mapped_params[mapto])

					# Store slot for GeomDisplaceMesh
					if mapto == 'displacement':
						bus['node']['displacement_slot'] = slot
					# Store slot for bump
					elif mapto == 'bump':
						bus['material']['bump_slot'] = slot
					# Store slot for normal
					elif mapto == 'normal':
						bus['material']['normal_slot'] = slot

					bus['mtex']            = {}
					bus['mtex']['slot']    = slot
					bus['mtex']['texture'] = slot.texture
					bus['mtex']['mapto']   = mapto
					bus['mtex']['factor']  = factor

					# Check if we could improve this
					# Better handling of texture blending
					bus['mtex']['name']= clean_string("MA%sMT%.2iTE%s" % (ma.name, i, slot.texture.name))

					if VRayTexture.texture_coords == 'ORCO':
						bus['material']['orco_suffix']= get_name(get_orco_object(scene, bus['node']['object'], VRayTexture),
																 prefix='ORCO')

						bus['mtex']['name']+= bus['material']['orco_suffix']

					if VRayExporter.debug:
						print_dict(scene, "bus['mtex']", bus['mtex'])

					# Write texture
					if write_texture(bus):
						# Append texture to stack and write texture with factor
						bus['textures'][mapto].append( [stack_write_texture(bus),
														slot.use_stencil,
														VRaySlot.blend_mode] )

	if VRayExporter.debug:
		if len(bus['textures']):
			print_dict(scene, "Material \"%s\" texture stack" % ma.name, bus['textures'])

	# Collapsing texture stack
	del_keys= []
	for key in bus['textures']:
		if len(bus['textures'][key]):
			if len(bus['textures'][key]) == 1 and type(bus['textures'][key][0]) is tuple:
				del_keys.append(key)
			else:
				bus['textures'][key]= write_TexOutput(bus, stack_write_textures(bus, stack_collapse_layers(bus['textures'][key])), key)

	for key in del_keys:
		del bus['textures'][key]

	if 'displacement' in bus['textures']:
		bus['node']['displacement_texture']= bus['textures']['displacement']

	if VRayExporter.debug:
		if len(bus['textures']):
			print_dict(scene, "Material \"%s\" textures" % ma.name, bus['textures'])

	return bus['textures']


def write_subtexture(bus, tex_name):
	if not tex_name in bpy.data.textures:
		return None

	context_mtex= None
	if 'mtex' in bus:
		# Store mtex context
		context_mtex= bus['mtex']

	# Prepare data
	bus['mtex']= {}
	bus['mtex']['env']=     True # This is needed!
	bus['mtex']['slot']=    None
	bus['mtex']['texture']= bpy.data.textures[tex_name]
	bus['mtex']['factor']=  1.0
	bus['mtex']['mapto']=   None
	bus['mtex']['name']=    clean_string("TE%s"%(tex_name))

	# Write texture
	texture_name= write_texture(bus)

	# Restore mtex context
	bus['mtex']= context_mtex

	return texture_name
