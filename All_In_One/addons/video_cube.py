bl_info = {
	"name": "Video Cube",
	"description": "",
	"author": "",
	"version": (0, 0, 1),
	"blender": (2, 70, 0),
	"location": "3D View > Create",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame",
}

import bpy
import os

from bpy.props import (StringProperty,
					   BoolProperty,
					   IntProperty,
					   FloatProperty,
					   EnumProperty,
					   PointerProperty,
					   )
from bpy.types import (Panel,
					   Operator,
					   PropertyGroup,
					   )

class VideoCubeSettings(PropertyGroup):

	max_slices = IntProperty(
		name = "Limit Slices",
		description="Maximum number of slices to generate",
		default = 500,
		min = 1,
		max = 100000
	)

	slice_thickness = FloatProperty(
		name = "Slice Thickness",
		description = "Width of each object representing a video frame",
		default = 1,
		min = 0.1,
		max = 10
	)
		
	slice_size = FloatProperty(
		name = "Slice Size",
		description = "Relative size of each object representing a video frame",
		default = 1,
		min = 0.1,
		max = 10
	)

	file_path = bpy.props.StringProperty \
	(
		name = "File Path",
		default = "",
		description = "Define a directory to pull video frames from",
		subtype = 'DIR_PATH'
	)

# ------------------------------------------------------------------------
#	operators
# ------------------------------------------------------------------------

class Generate(bpy.types.Operator):
	bl_idname = "wm.video_cube_generate"
	bl_label = "Generate"

	def execute(self, context):
		scene = context.scene
		settings = scene.video_cube

		slice_thickness = settings.slice_thickness
		slice_size = 1e3 * settings.slice_size

		# Set rendering engine to Cycles
		bpy.context.scene.render.engine = "CYCLES"

		# List of objects representing video frames
		layers = []
		# Import images into scene to use as object textures
		for i in range(1, settings.max_slices):
			
			# Name of image file
			name = str(i).zfill(4) + ".jpg"
			# File path (relative to .blend file)
			filepath = settings.file_path + name
			
			if (os.path.isfile(filepath)):
			
				# Load image into scene
				image = bpy.data.images.load(
					filepath,
					check_existing=True
				)
				#bpy.data.images[name].name = str(i)

				# Add objects and materials
				size = image.size
				# Add new cube to scene (one video frame)
				bpy.ops.mesh.primitive_cube_add(location=(
					0,
					0,
					i * (slice_thickness / 100 * 2)
				))
				# Resize cube to be thinner
				bpy.ops.transform.resize(value=(
					size[0] / slice_size,
					size[1] / slice_size,
					slice_thickness / 100
				))
				# Selected object
				ob = bpy.context.active_object
				# Rename slice
				ob.name = "Video Slice " + str(i)
				# Add slice to list of layers
				layers.append(ob)

				# Check if material exists
				mat = bpy.data.materials.get(str(i))
				if mat is None:
					# Create new material if none exists
					mat = bpy.data.materials.new(name=str(i))
				
				# Set material to use node editor
				mat.use_nodes = True;
				# List of nodes in material node tree
				nodes = mat.node_tree.nodes
				# Remove all nodes from material
				for node in nodes:
					nodes.remove(node)
					
				# Add nodes
				output = nodes.new("ShaderNodeOutputMaterial")
				output.location = 500, 0
				diff = nodes.new("ShaderNodeBsdfDiffuse")
				diff.location = 0, 0
				texture = nodes.new("ShaderNodeTexImage")
				texture.location = -250, 0
				coord = nodes.new("ShaderNodeTexCoord")
				coord.location = -500, 0
				trans = nodes.new("ShaderNodeBsdfTransparent")
				trans.location = 0, -250
				mix = nodes.new("ShaderNodeMixShader")
				mix.location = 250, 0
				
				# Set source image for texture
				texture.image = bpy.data.images[str(i).zfill(4) + ".jpg"]
				mix.inputs[0].default_value = 0
				
				# Create links between material nodes
				mat.node_tree.links.new(
					texture.inputs["Vector"],
					coord.outputs["Generated"]
				)
				mat.node_tree.links.new(
					diff.inputs["Color"],
					texture.outputs["Color"]
				)
				mat.node_tree.links.new(
					mix.inputs[1],
					diff.outputs["BSDF"]
				)
				mat.node_tree.links.new(
					mix.inputs[2],
					trans.outputs["BSDF"]
				)
				mat.node_tree.links.new(
					output.inputs["Surface"],
					mix.outputs["Shader"]
				)

				# Assign material to object
				if ob.data.materials:
					ob.data.materials[0] = mat
				else:
					ob.data.materials.append(mat)

		# Select all slices
		for layer in layers:
			layer.select = True
		# Combine layers
		bpy.ops.object.join()
		# Set origin to center of geometry
		bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
		# Set name of object
		bpy.context.object.name = "Video Cube"
		# Deselect
		bpy.ops.object.select_all(action="TOGGLE")

		return {'FINISHED'}

class BasicMenu(bpy.types.Menu):
	bl_idname = "OBJECT_MT_select_test"
	bl_label = "Select"

	def draw(self, context):
		layout = self.layout

class OBJECT_PT_my_panel(Panel):
	bl_idname = "OBJECT_PT_Video_Cube"
	bl_label = "Video Cube"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Create"
	bl_context = "objectmode"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		settings = scene.video_cube

		layout.prop(settings, "max_slices")
		layout.prop(settings, "slice_thickness")
		layout.prop(settings, "slice_size")
		layout.prop(settings, "file_path")
		layout.operator("wm.video_cube_generate", icon="MOD_UVPROJECT")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.video_cube = PointerProperty(type=VideoCubeSettings)

def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.video_cube

if __name__ == "__main__":
	register()