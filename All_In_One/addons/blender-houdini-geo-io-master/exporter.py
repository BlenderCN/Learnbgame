from . import hio

import numpy as np

import bpy

from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion

def export_mesh(path:str, me):
	assert len(me.polygons) > 0, 'Only supports polygons. No lines or points.'

	me.flip_normals()
	me.calc_normals_split()

	geo = hio.Geometry()

	vertices = np.empty(len(me.vertices) * 3, dtype=np.float32)
	me.vertices.foreach_get("co", vertices)
	vertices.shape = (len(me.vertices), 3)

	vertex_indices = np.empty(len(me.loops), dtype=np.int64)
	me.loops.foreach_get('vertex_index', vertex_indices)

	loop_total = np.empty(len(me.polygons), dtype=np.int64)
	me.polygons.foreach_get('loop_total', loop_total)

	polys = geo.createPolygons(vertices, vertex_indices, loop_total, True)

	###

	normal = np.empty(len(me.loops) * 3, dtype=np.float32)
	me.loops.foreach_get('normal', normal)
	normal.shape = (len(me.loops), 3)
	normal *= -1

	N = geo.addFloatAttrib(hio.AttribType.Vertex, "N", [0, 0, 0], hio.TypeInfo.Normal)
	N.setAttribValue(normal)

	for uv_layer in me.uv_layers:
		name = uv_layer.name

		UV = geo.addFloatAttrib(hio.AttribType.Vertex, name, [0, 0, 0], hio.TypeInfo.TextureCoord)
		data = np.empty(len(uv_layer.data) * 2, dtype=np.float32)
		uv_layer.data.foreach_get('uv', data)
		data.shape = (len(uv_layer.data), 2)
		data = np.column_stack( (data, np.zeros(data.shape[0])) )
		UV.setAttribValue(data)

	for color_layer in me.vertex_colors:
		name = color_layer.name

		Cd = geo.addFloatAttrib(hio.AttribType.Vertex, name, [0, 0, 0], hio.TypeInfo.Color)
		data = np.empty(len(color_layer.data) * 4, dtype=np.float64)
		color_layer.data.foreach_get("color", data)
		data.shape = (len(color_layer.data), 4)
		data = data[:,:3]
		Cd.setAttribValue(data)

	# TODO: fix material info
	# if len(me.materials) > 0:
	# 	data = np.empty(len(me.polygons), dtype=np.int32)
	# 	me.polygons.foreach_get('material_index', data)
	# 	material_index_attr = geo.addIntAttrib(hio.AttribType.Prim, "material_index", [0], hio.TypeInfo.Value)
	# 	data.shape = (len(me.polygons), 1)
	# 	material_index_attr.setAttribValue(data)

	return geo

def export_curve(path:str, cu):
	geo = hio.Geometry()

	for sp in cu.splines:
		
		if sp.type == 'BEZIER':
			pts = []
			
			if not sp.use_cyclic_u:
				for i, p in enumerate(sp.bezier_points):
					if i > 0:
						pts.append( (p.handle_left.x, p.handle_left.y, p.handle_left.z) )

					pts.append( (p.co.x, p.co.y, p.co.z) )

					if i < len(sp.bezier_points) - 1:
						pts.append( (p.handle_right.x, p.handle_right.y, p.handle_right.z) )

			else:
				for i, p in enumerate(sp.bezier_points):
					pts.append( (p.handle_left.x, p.handle_left.y, p.handle_left.z) )
					pts.append( (p.co.x, p.co.y, p.co.z) )
					pts.append( (p.handle_right.x, p.handle_right.y, p.handle_right.z) )

				pt = pts.pop(0)
				pts.append(pt)

			prim = geo.createBezierCurve(len(pts), is_closed=sp.use_cyclic_u, order=4)

			arr = np.array(pts, dtype=np.float)
			prim.setPositions(arr)

		elif sp.type == 'NURBS':
			prim = geo.createNURBSCurve(len(sp.points), is_closed=sp.use_cyclic_u, order=sp.order_u)

			pts = np.empty(len(sp.points) * 4, dtype=np.float32)
			sp.points.foreach_get("co", pts)
			pts.shape = (len(sp.points), 4)
			vertices = pts[:,:3].copy()
			prim.setPositions(vertices)

			Pw = geo.findPointAttrib("Pw")
			if Pw == None:
				Pw = geo.addFloatAttrib(hio.AttribType.Point, "Pw", [1], hio.TypeInfo.Value)

			weights = pts[:,3:].copy()
			Pw.setAttribValue(weights, prim.vertexStartIndex())

	return geo

def export_grease_pencil(path:str, gp):
	global_matrix = np.matrix(axis_conversion(to_forward="-Z", to_up="Y").to_4x4())

	geo = hio.Geometry()

	datatype_attr = hio.StringAttribute(1, 'datatype', hio.TypeInfo.Value)
	datatype_attr.append(['grease_pencil'])
	geo.detail_attributes.append(datatype_attr)

	material_names = [x.name for x in gp.materials]
	material_name_attr = hio.StringAttribute(1, "material_name", hio.TypeInfo.Value)
	geo.primitive_attributes.append(material_name_attr)

	layer_name_attr = hio.StringAttribute(1, 'layer_name', hio.TypeInfo.Value)
	geo.primitive_attributes.append(layer_name_attr)

	pressure_attr = hio.FloatAttribute(1, 'pressure', hio.TypeInfo.Value)
	geo.point_attributes.append(pressure_attr)

	line_width_attr = hio.FloatAttribute(1, 'line_width', hio.TypeInfo.Value)
	geo.primitive_attributes.append(line_width_attr)

	opacity_attr = hio.FloatAttribute(1, 'opacity', hio.TypeInfo.Value)
	geo.primitive_attributes.append(opacity_attr)

	###

	for layer in gp.layers:
		frame = layer.active_frame

		for stroke in frame.strokes:
			### points

			N = len(stroke.points)

			points = np.empty(N * 3, dtype=np.float)
			stroke.points.foreach_get('co', points)
			points = points.reshape((N, 3))

			points = np.column_stack((points, np.ones(points.shape[0])))
			points = np.matmul(points, global_matrix.T)

			idxs = []
			for point in points:
				idx, _ = geo.createPoint(point[0, 0], point[0, 1], point[0, 2])
				idxs.append(idx)

			pressure = np.empty(N, dtype=np.float)
			stroke.points.foreach_get('pressure', pressure)
			for x in pressure:
				pressure_attr.append([x])

			prim_id, prim = geo.createPrimitive(hio.PrimType.Polygon, idxs)
			prim.closed = False

			line_width_attr.append([stroke.line_width])
			opacity_attr.append([layer.opacity])
			layer_name_attr.append([layer.info])

		material_index = np.empty(len(frame.strokes), dtype=np.int32)
		frame.strokes.foreach_get('material_index', material_index)
		
		for x in material_index:
			n = material_names[x]
			material_name_attr.append([n])

	return geo


###

def export(path:str, ob, opts):

	convert_to_mesh = False

	if convert_to_mesh:
		try:
			data = ob.to_mesh(bpy.context.depsgraph, apply_modifiers=True)
		except RuntimeError:
			return {'CANCELLED'}
	else:
		data = ob.data.copy()

	if hasattr(data, 'transform'):
		global_matrix = (Matrix.Scale(1, 4) @ axis_conversion(to_forward="-Z", to_up="Y").to_4x4())
		data.transform(global_matrix)

	geo = None

	if isinstance(data, bpy.types.Mesh):
		me = data
		geo = export_mesh(path, me)
		bpy.data.meshes.remove(me)

	elif isinstance(data, bpy.types.Curve):
		cu = data
		geo = export_curve(path, cu)
		bpy.data.curves.remove(cu)

	# elif isinstance(data, bpy.types.GreasePencil):
	# 	gp = data
	# 	geo = export_grease_pencil(path, gp)
	# 	bpy.data.grease_pencil.remove(gp)

	else:
		print('Unsurpported object type:', data.__class__)

		# FIXME: Find more static way
		db = eval(repr(data).split('[')[0])
		db.remove(data)

		return False

	if not geo:
		return False

	if not geo.save(path):
		return False

	return True
