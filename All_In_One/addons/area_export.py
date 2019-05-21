# Export scene as a lua script along with IQE files.

bl_info = {
	"name": "Export Area",
	"description": "Export Area for Mio project.",
	"author": "Tor Andersson",
	"version": (2013, 9, 8),
	"blender": (2, 6, 7),
	"location": "File > Export > Area",
	"wiki_url": "http://github.com/ccxvii/mio",
	"category": "Import-Export",
}

import bpy, math, struct, os, sys

from bpy.props import *
from bpy_extras.io_utils import ExportHelper
from mathutils import Matrix, Quaternion, Vector

done_meshes = set()

def quote(s):
	return "\"%s\"" % s

def file_write_transform(file, matrix, noscale=False):
	t, r, s = matrix.decompose()
	file.write("\ttransform = {\n")
	file.write("\t\tposition = {%g, %g, %g},\n" % (t.x, t.y, t.z))
	file.write("\t\trotation = {%g, %g, %g, %g},\n" % (r.x, r.y, r.z, r.w))
	if not noscale:
		file.write("\t\tscale = {%.9g, %.9g, %.9g},\n" % (s.x, s.y, s.z))
	file.write("\t},\n")

def export_mesh(filename, mesh):
	if mesh in done_meshes:
		return
	done_meshes.add(mesh)

	print("exporting mesh", filename)

	file = open(filename, "w")
	file.write("# Inter-Quake Export\n")

	mesh.calc_tessface()
	texcoords = mesh.tessface_uv_textures.get('UVMap')
	colors = mesh.tessface_vertex_colors.get('Col')

	out = {}
	for face in mesh.tessfaces:
		fm = face.material_index
		if not fm in out:
			out[fm] = []
		out[fm].append(face)

	for fm in out.keys():
		vertex_map = {}
		vertex_list = []
		face_list = []

		for face in out[fm]:
			ft = texcoords and texcoords.data[face.index]
			fc = colors and colors.data[face.index]
			ft = ft and [ft.uv1, ft.uv2, ft.uv3, ft.uv4]
			fc = fc and [fc.color1, fc.color2, fc.color3, fc.color4]
			f = []
			for i, v in enumerate(face.vertices):
				vp = tuple(mesh.vertices[v].co)
				vn = tuple(mesh.vertices[v].normal)
				vt = ft and tuple(ft[i])
				vc = fc and tuple(fc[i])
				v = vp, vn, vt, vc
				if v not in vertex_map:
					vertex_map[v] = len(vertex_list)
					vertex_list.append(v)
				f.append(vertex_map[v])
			face_list.append(f)

		file.write("\n")
		file.write("mesh %s\n" % quote(mesh.name))
		if fm < len(mesh.materials):
			file.write("material %s\n" % quote(mesh.materials[fm].name))
		else:
			file.write("material None\n")
		for vp, vn, vt, vc in vertex_list:
			file.write("vp %.9g %.9g %.9g\n" % vp)
			file.write("vn %.9g %.9g %.9g\n" % vn)
			if vt: file.write("vt %.9g %.9g\n" % (vt[0], 1.0 - vt[1]))
			if vc: file.write("vc %.9g %.9g %.9g\n" % vc)
		for f in face_list:
			if len(f) == 3:
				file.write("fm %d %d %d\n" % (f[2], f[1], f[0]))
			else:
				file.write("fm %d %d %d %d\n" % (f[3], f[2], f[1], f[0]))

	file.close()

def export_object_lamp(dir, file, scene, obj, lamp):
	if lamp.type == 'AREA': return
	if lamp.type == 'HEMI': return
	file.write("\tlamp = {\n")
	file.write("\t\ttype = '%s',\n" % lamp.type)
	file.write("\t\tcolor = {%g, %g, %g},\n" % tuple(lamp.color[:3]))
	file.write("\t\tenergy = %g,\n" % lamp.energy)
	if lamp.type == 'SPOT' or lamp.type == 'POINT':
		file.write("\t\tdistance = %g,\n" % lamp.distance)
		file.write("\t\tuse_sphere = %s,\n" % ("true" if lamp.use_sphere else "false"))
	if lamp.type == 'SPOT':
		file.write("\t\tspot_angle = %g,\n" % math.degrees(lamp.spot_size))
		file.write("\t\tspot_blend = %g,\n" % lamp.spot_blend)
	file.write("\t\tuse_shadow = %s,\n" % ("true" if lamp.use_shadow else "false"))
	file.write("\t},\n")

def export_object_mesh(dir, file, scene, obj):
	if len(obj.modifiers) == 0:
		mesh = obj.data
		meshname = mesh.name
		export_mesh(dir + "/" + meshname + ".iqe", mesh)
	else:
		mesh = obj.to_mesh(scene, True, 'PREVIEW')
		meshname = "object_" + obj.name
		export_mesh(dir + "/" + meshname + ".iqe", mesh)
		bpy.data.meshes.remove(mesh)
	file.write("\tmesh = %s,\n" % quote(meshname))
	#file_write_color(file, obj.color)

def export_object_dupli_group(dir, file, scene, obj):
	file.write("\tmesh = %s,\n" % quote(obj.dupli_group.name))

def export_object(dir, file, scene, obj):
	file.write("\nentity {\n")
	file.write("\tname = %s,\n" % quote(obj.name))
	file_write_transform(file, obj.matrix_world)
	if obj.type == 'LAMP':
		export_object_lamp(dir, file, scene, obj, obj.data)
	elif obj.type == 'MESH':
		export_object_mesh(dir, file, scene, obj)
	elif obj.type == 'EMPTY':
		if obj.dupli_type == 'GROUP':
			export_object_dupli_group(dir, file, scene, obj)
	file.write("}\n")

def export_scene(dir, scene):
	print("exporting scene", scene.name)
	file = open(dir + "/" + scene.name + ".lua", "w")
	file.write("-- scene: " + scene.name + "\n")
	for obj in scene.objects:
		export_object(dir, file, scene, obj)
	file.close()

def export_blend(dir):
	print("exporting to directory", dir)
	os.makedirs(dir, exist_ok=True)
	for scene in bpy.data.scenes:
		export_scene(dir, scene)

if __name__ == "__main__":
	if len(sys.argv) > 4 and sys.argv[-2] == '--':
		export_blend(sys.argv[-1])
	else:
		dir = os.path.splitext(bpy.data.filepath)[0]
		export_blend(dir)
