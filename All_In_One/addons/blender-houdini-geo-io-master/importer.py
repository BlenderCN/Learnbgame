from . import hio

import os

import numpy as np

import bpy
import bmesh

from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion
from bpy_extras.io_utils import unpack_list

def import_mesh(geo:hio.Geometry, name:str):
	me = bpy.data.meshes.new(name)

	pdata = geo._dataByType([hio.PrimitiveTypes.Poly])
	
	me.vertices.add(geo.getNumPoints())
	points = geo.points().flatten()
	me.vertices.foreach_set("co", points)
	
	# prims = pdata['prims']

	vertex_indices = pdata['vertices']
	vertices_lut = pdata['vertices_lut']

	loop_start = pdata['vertex_start_index']
	loop_total = pdata['vertex_count']

	###

	me.loops.add(len(vertex_indices))
	me.loops.foreach_set("vertex_index", vertex_indices)

	me.polygons.add(len(loop_start))
	me.polygons.foreach_set("loop_start", loop_start)
	me.polygons.foreach_set("loop_total", loop_total)

	###

	N = geo.findVertexAttrib("N")

	if N:
		data = N.attribValue()

		me.create_normals_split()

		data = np.take(data, vertices_lut, axis=0)
		data = data.flatten()
		data *= -1
		me.loops.foreach_set("normal", data)

	material_index = geo.findPrimAttrib("material_index")
	if material_index:
		data = material_index.attribValue()
		data = data.flatten()
		me.polygons.foreach_set('material_index', data)

	###

	for attr in geo.vertexAttribs():
		if attr.typeInfo() == hio.TypeInfo.TextureCoord:
			uv_layer = me.uv_layers.new(name=attr.name())
			
			data = attr.attribValue()
			data = np.take(data, vertices_lut, axis=0)
			data = data[:,:2]
			data = data.flatten()

			uv_layer.data.foreach_set("uv", data)

		elif attr.typeInfo() == hio.TypeInfo.Color:
			color_layer = me.vertex_colors.new(name=attr.name())
			data = attr.attribValue()
			data = np.take(data, vertices_lut, axis=0)
			data = np.column_stack( (data, np.ones(data.shape[0])) )
			data = data.flatten()

			color_layer.data.foreach_set("color", data)

	###

	if N:
		me.validate(clean_customdata=False)

		clnors = np.empty(len(me.loops) * 3, dtype=np.float32)
		
		me.loops.foreach_get("normal", clnors)
		me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), dtype=np.bool))
		
		clnors = np.reshape(clnors, (int(len(clnors)/3), 3))
		me.normals_split_custom_set(clnors)

		me.use_auto_smooth = True

	me.flip_normals()
	me.update()

	return me

def import_curve(geo:hio.Geometry, name:str):
	cu = bpy.data.curves.new(name, type="CURVE")
	cu.dimensions = '3D'
	cu.fill_mode = 'FULL'

	points = geo.getPoints()

	target_type = [hio.PrimType.NURBS, hio.PrimType.Bezier]
	pdata = geo.getPrimitivesByType(target_type)

	vertex_indices = pdata['vertices']
	prim_types = pdata['type']
	vertex_count = pdata['vertex_count']
	vertex_start_index = pdata['vertex_start_index']
	closed = pdata['closed']

	for i, prim_type in enumerate(prim_types):
		t = hio.PrimType(prim_type)

		if t == hio.PrimType.NURBS:
			sp = cu.splines.new('NURBS')

			N = vertex_count[i]
			sp.points.add(N-1)

			idxs = list(range(vertex_start_index[i], vertex_start_index[i] + N))
			idxs = np.take(vertex_indices, idxs)

			pos = np.take(points, idxs, axis=0)
			pos = np.column_stack((pos, np.ones((N, 1))))
			pos = pos.flatten()

			sp.points.foreach_set("co", pos)
			sp.use_cyclic_u = closed[i]
			sp.use_endpoint_u = True
			sp.order_u = 4

		elif t == hio.PrimType.Bezier:
			sp = cu.splines.new('BEZIER')

			N = int((vertex_count[i] + 2) / 3)
			sp.bezier_points.add(N-1)

			idxs = list(range(vertex_start_index[i], vertex_start_index[i] + vertex_count[i]))
			idxs = np.take(vertex_indices, idxs)

			pos = np.take(points, idxs, axis=0)

			if closed[i]:
				for n in range(N):
					pt = sp.bezier_points[n]
					pt.handle_left = pos[n * 3 - 1]
					pt.co = pos[n * 3 ]
					pt.handle_right = pos[n * 3 + 1]
						
			else:
				for n in range(N):
					pt = sp.bezier_points[n]
					if n == 0:
						pt.handle_left = pos[0]
						pt.co = pos[0]
						pt.handle_right = pos[1]
					elif n == N - 1:
						pt.handle_left = pos[n * 3 - 1]
						pt.co = pos[n * 3]
						pt.handle_right = pos[n * 3]
					else:
						pt.handle_left = pos[n * 3 - 1]
						pt.co = pos[n * 3]
						pt.handle_right = pos[n * 3 + 1]

			sp.use_cyclic_u = closed[i]
			sp.use_endpoint_u = True
			sp.order_u = 4

	return cu

def import_(path:str, ob, opts):
	data = None

	temp_name = 'temp_' + os.path.basename(path)

	geo = hio.Geometry()
	if not geo.load(path):
		return None

	if ob.type == 'MESH':
		data = import_mesh(geo, temp_name)
		for x in ob.data.materials:
			data.materials.append(x)

	# elif ob.type == 'CURVE':
	# 	data = import_curve(geo, temp_name)

	if hasattr(data, 'transform'):
		global_matrix = (Matrix.Scale(1, 4) @ axis_conversion(from_forward="-Z", from_up="Y").to_4x4())
		data.transform(global_matrix)

	return data
