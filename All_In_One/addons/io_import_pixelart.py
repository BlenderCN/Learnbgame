# coding: UTF-8

bl_info = {
	"name": "Import Pixel Art",
	"author": "Mathias Panzenböck",
	"version": (1, 0, 3),
	"blender": (2, 76, 0),
	"location": "File > Import > Pixel Art",
	"description": "Imports pixel art images, creating colored cubes for each pixel.",
	"wiki_url": "https://github.com/panzi/blender-addon-import-pixelart/blob/master/README.md",
	"tracker_url": "https://github.com/panzi/blender-addon-import-pixelart/issues",
	"category": "Import-Export"
}

import os.path
import bpy

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

PARENT_NAME = '{filename}'
MATERIAL_NAME = 'pixel_art_{color}'
CUBE_NAME = '{filename}_{x}_{y}'
MESH_NAME = '{filename}_{x}_{y}_mesh'

def read_pixel_art(context, filepath,
		use_nodes=True,
		reuse_materials=False,
		material_name=MATERIAL_NAME,
		cube_name=CUBE_NAME,
		mesh_name=MESH_NAME,
		parent_name=PARENT_NAME):

	cube_verts = [
		(0, 0, 0), # 0
		(1, 0, 0), # 1
		(1, 1, 0), # 2
		(0, 1, 0), # 3
		(0, 0, 1), # 4
		(1, 0, 1), # 5
		(1, 1, 1), # 6
		(0, 1, 1)  # 7
	]

	cube_edges = []

	cube_faces = [
		(0, 1, 2, 3),
		(0, 1, 5, 4),
		(1, 2, 6, 5),
		(4, 5, 6, 7),
		(2, 3, 7, 6),
		(0, 3, 7, 4)
	]

	struse_nodes = 'nodes' if use_nodes else ''
	blender_cycles = bpy.context.scene.render.engine == 'CYCLES'
	filename = os.path.split(filepath)[1]
	image = bpy.data.images.load(filepath)

	try:
		channels = image.channels
		if channels not in (1, 3, 4):
			raise Exception("cannot handle number of channels in image")

		layers = bpy.context.scene.layers
		params = dict(filename=filename, use_nodes=struse_nodes)
		parent = bpy.data.objects.new(name=parent_name.format(**params), object_data=None)
		parent.layers = layers
		bpy.context.scene.objects.link(parent)

		materials = {}
		width, height = image.size
		pixels = image.pixels
		a = 1.0
		for y in range(height):
			offset = y * channels * width
			for x in range(width):
				if channels == 1:
					r = g = b = image.pixels[offset + x]
				elif channels == 3:
					index = offset + x * channels
					r = pixels[index]
					g = pixels[index + 1]
					b = pixels[index + 2]
				else:
					index = offset + x * channels
					r = pixels[index]
					g = pixels[index + 1]
					b = pixels[index + 2]
					a = pixels[index + 3]

					if a == 0:
						continue

				color = (r, g, b, a)
				strcolor = '%02X%02X%02X%02X' % (int(r * 255), int(g * 255), int(b * 255), int(a * 255))
				params = dict(filename=filename, color=strcolor, x=x, y=y, use_nodes=struse_nodes)
				name = material_name.format(**params)

				if color in materials:
					material = materials[color]

				elif reuse_materials and name in bpy.data.materials:
					material = bpy.data.materials[name]

				else:
					material = materials[color] = bpy.data.materials.new(name=name)
					material.diffuse_color = (r, g, b)
					material.alpha = a
					material.use_transparency = a < 1
					material.use_nodes = use_nodes

					if use_nodes:
						tree = material.node_tree
						tree.nodes.clear()

						if blender_cycles:
							diffuse_node = tree.nodes.new('ShaderNodeBsdfDiffuse')
							diffuse_node.inputs[0].default_value = color

							output_node = tree.nodes.new('ShaderNodeOutputMaterial')

							if a < 1:
								mix_node = tree.nodes.new('ShaderNodeMixShader')
								mix_node.inputs[0].default_value = a

								transparent_node = tree.nodes.new('ShaderNodeBsdfTransparent')
								transparent_node.inputs[0].default_value = color

								tree.links.new(diffuse_node.outputs[0], mix_node.inputs[1])
								tree.links.new(transparent_node.outputs[0], mix_node.inputs[2])
								tree.links.new(mix_node.outputs[0], output_node.inputs[0])

							else:
								tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

						else:
							output_node = tree.nodes.new('ShaderNodeOutput')
							output_node.inputs[0].default_value = color
							output_node.inputs[1].default_value = a

				cube_mesh_name = mesh_name.format(**params)
				mesh = bpy.data.meshes.new(cube_mesh_name)
				mesh.from_pydata(cube_verts, cube_edges, cube_faces)
				mesh.materials.append(material)
				mesh.update()

				cube_object_name = cube_name.format(**params)
				obj = bpy.data.objects.new(name=cube_object_name, object_data=mesh)
				obj.layers = layers
				obj.location = (x, y, 0)
				obj.parent = parent
				bpy.context.scene.objects.link(obj)


	finally:
		image.user_clear()
		bpy.data.images.remove(image)

	return {'FINISHED'}

class ImportPixelArt(Operator, ImportHelper):
	"""Imports pixel art images, creating colored cubes for each pixel."""
	bl_idname = "import_image.pixel_art"
	bl_label = "Import Pixel Art"
	bl_options = {'REGISTER', 'UNDO'}

	filter_glob = StringProperty(default="*.png;*.gif;*.bmp", options={'HIDDEN'})

	use_nodes       = BoolProperty(default=True, name="Use material nodes")
	reuse_materials = BoolProperty(default=False, name="Reuse existing materials with matching names")

	parent_name   = StringProperty(default=PARENT_NAME, name="Object Name")
	cube_name     = StringProperty(default=CUBE_NAME, name="Pixel Names")
	mesh_name     = StringProperty(default=MESH_NAME, name="Mesh Names")
	material_name = StringProperty(default=MATERIAL_NAME, name="Material Names")

	def execute(self, context):
		return read_pixel_art(context, self.filepath,
			use_nodes=self.use_nodes,
			reuse_materials=self.reuse_materials,
			material_name=self.material_name,
			cube_name=self.cube_name,
			mesh_name=self.mesh_name,
			parent_name=self.parent_name)


def menu_func_import(self, context):
	self.layout.operator(ImportPixelArt.bl_idname, text="Import Pixel Art (.png/.gif/.bmp)")


def register():
	bpy.utils.register_class(ImportPixelArt)
	bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
	bpy.utils.unregister_class(ImportPixelArt)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
	try:
		unregister()
	except:
		pass
	register()
