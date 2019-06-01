import os
from struct import unpack, calcsize

import bpy
from bpy_extras.io_utils import unpack_list

FileVersion = 3
MaterialGroups = 8
BlockSize = 256
BlockSize2 = BlockSize * BlockSize

def read(fd, fmt):
	return unpack(fmt, fd.read(calcsize(fmt)))

def read_str(fd):
	return fd.read(read(fd, "B")[0]).decode("cp1252")

def read_str_32(fd):
	return fd.read(read(fd, "I")[0]).decode("cp1252")

class TerrainFile:
    pass

def root_name(path):
	return os.path.basename(path).rsplit(".", 1)[0]

def read_ter(fd):
	version, = read(fd, "B")
	assert version == FileVersion, "unsupported format version"

	ret = TerrainFile()

	ret.heightMap = read(fd, str(BlockSize2) + "H")
	ret.materialFlags = read(fd, str(BlockSize2) + "B")
	ret.materialNames = [read_str(fd) for k in range(MaterialGroups)]
	ret.materialAlpha = [None] * MaterialGroups

	for k in range(MaterialGroups):
		if ret.materialNames[k]:
			ret.materialAlpha[k] = read(fd, str(BlockSize2) + "B")

	ret.textureScript = read_str_32(fd)
	ret.heightfieldScript = read_str_32(fd)

	return ret

texture_extensions = ("png", "jpg")

def resolve_texture(filepath, name):
	dirname = os.path.dirname(filepath)

	while True:
		texbase = os.path.join(dirname, name)

		for extension in texture_extensions:
			texname = texbase + "." + extension

			if os.path.isfile(texname):
				return texname

		if os.path.ismount(dirname):
			break

		prevdir, dirname = dirname, os.path.dirname(dirname)

		if prevdir == dirname:
			break

def load(context, filepath):
	with open(filepath, "rb") as fd:
		ter = read_ter(fd)

	name = root_name(filepath)
	me = bpy.data.meshes.new(name)

	for orig_path in ter.materialNames:
		if not orig_path:
			continue

		mat_name = root_name(orig_path)
		mat_file = resolve_texture(filepath, mat_name)

		mat = bpy.data.materials.new(mat_name)
		me.materials.append(mat)

		if mat_file:
			try:
				image = bpy.data.images.load(mat_file)
			except:
				print("Cannot load image", mat_file)
				continue

			slot = mat.texture_slots.add()
			slot.texture = bpy.data.textures.new(mat_name, "IMAGE")
			slot.texture.image = image
			slot.texture_coords = "ORCO"
			slot.scale = 32, 32, 32

	# This is a bit of a mess.
	# Feel free to clean it up :)

	# me.vertices.add(BlockSize2)
	#
	# for i, vert in enumerate(me.vertices):
	# 	vert.co = (
	# 		(i // BlockSize) * 8 / 32,
	# 		(i %  BlockSize) * 8 / -32,
	# 		ter.heightMap[i] / 32 / 32
	# 	)

	verts = []

	for x in range(BlockSize + 1):
		for y in range(BlockSize + 1):
			i = (y % BlockSize) * BlockSize + (x % BlockSize)

			verts.append((
				x * 8 - 1024,
				y * 8 - 1024,
				ter.heightMap[i] / 32
			))

	faces = []

	for x in range(BlockSize):
		for y in range(BlockSize):
			vert0 = y * 257 + x
			vert1 = y * 257 + x + 1
			vert2 = y * 257 + x + 257
			vert3 = y * 257 + x + 258

			if x % 2 == y % 2:
				faces.append(((vert0, vert2, vert3), (x, y)))
				faces.append(((vert3, vert1, vert0), (x, y)))
			else:
				faces.append(((vert0, vert2, vert1), (x, y)))
				faces.append(((vert3, vert1, vert2), (x, y)))

	me.vertices.add(len(verts))
	me.vertices.foreach_set("co", unpack_list(verts))

	me.polygons.add(len(faces))
	me.loops.add(len(faces) * 3)

	# me.uv_textures.new()
	# uvs = me.uv_layers[0]

	for i, ((verts, (gx, gy)), poly) in enumerate(zip(faces, me.polygons)):
		poly.use_smooth = True
		poly.loop_total = 3
		poly.loop_start = i * 3

		# For now, just solidly fill in the material with the highest alpha
		best_mat_index = None
		best_mat_alpha = None
		grid_idx = gx * BlockSize + gy # ... this is the wrong way around?

		for mat_index in range(MaterialGroups):
			if ter.materialAlpha[mat_index]:
				alpha = ter.materialAlpha[mat_index][grid_idx]

				if best_mat_index == None or alpha > best_mat_alpha:
					best_mat_index = mat_index
					best_mat_alpha = alpha

		if best_mat_index is not None:
			poly.material_index = best_mat_index

		for j, index in zip(poly.loop_indices, verts):
			me.loops[j].vertex_index = index
			# uvs.data[j].uv = ()

	me.validate()
	me.update()

	ob = bpy.data.objects.new(name, me)
	context.scene.objects.link(ob)

	return {"FINISHED"}
