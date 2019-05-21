#!/usr/bin/env python
"""
caption.py -- blender environment setup for 2D captioning footage

Copyright (c) 2015 Dan Panzarella <alsoelp@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""


bl_info = {
	"name": "Captioner",
	"description": "Easy scene setup for quick orthographic captioning (like gifs)",
	"author": "Dan Panzarella (alsoelp@gmail.com)",
	"version": (1, 0),
	"blender": (2, 77, 0),
	"location": "View3D > Tools",
	"wiki_url": "https://github.com/pzl/blender-scripts",
	"tracker_url": "https://github.com/pzl/blender-scripts/issues",
	"support": "COMMUNITY",
	"category": "Scene"
}

import bpy
import math

# 0-indexed
FG_LAYER = 5
BG_LAYER = FG_LAYER + 10

FG_LAYER_NAME = 'Caption Text'
BG_LAYER_NAME = 'Caption Shadow'





FG_LAYER_MASK = [False]*20
BG_LAYER_MASK = [False]*20
FG_LAYER_MASK[FG_LAYER] = True
BG_LAYER_MASK[BG_LAYER] = True


def render_settings():
	# set up render size presets
	bpy.context.scene.render.resolution_x = 1280
	bpy.context.scene.render.resolution_y = 720
	bpy.context.scene.render.resolution_percentage = 100
	bpy.context.scene.render.fps=24

	# CYCLES
	#transparent bg for easy alpha-overing
	bpy.context.scene.cycles.film_transparent = True
	

	
def speedup_settings():
	"""
		Speed optimizations
	"""

	###
	# Cycles
	###
	bpy.context.scene.cycles.device = 'GPU'

	# Speed up rendering with minimal bounces
	bpy.context.scene.cycles.transparent_max_bounces=0
	bpy.context.scene.cycles.transparent_min_bounces=0
	bpy.context.scene.cycles.max_bounces = 0
	bpy.context.scene.cycles.min_bounces = 0
	bpy.context.scene.cycles.diffuse_bounces = 0
	bpy.context.scene.cycles.glossy_bounces = 0
	bpy.context.scene.cycles.transmission_bounces = 0
	bpy.context.scene.cycles.volume_bounces = 0

	# fewer samples for simple scenes and quick rendering
	bpy.context.scene.cycles.samples = 25
	bpy.context.scene.cycles.preview_samples = 10

	# large tiles for better GPU rendering
	bpy.context.scene.render.tile_x = 256
	bpy.context.scene.render.tile_y = 256


	###
	# Blender Internal
	###
	bpy.context.scene.render.use_textures = False
	bpy.context.scene.render.use_shadows = False
	bpy.context.scene.render.use_sss = False
	bpy.context.scene.render.use_envmaps = False
	bpy.context.scene.render.use_raytrace = False


def scene_layers():
	bpy.context.scene.layers[FG_LAYER] = True
	bpy.context.scene.layers[BG_LAYER] = True

	fg = None
	bg = None

	for l in bpy.context.scene.render.layers:
		if l.name == FG_LAYER_NAME:
			fg = l
		elif l.name == BG_LAYER_NAME:
			bg = l

	if not fg:
		bpy.ops.scene.render_layer_add()
		bpy.context.scene.render.layers[0].name = FG_LAYER_NAME
		bpy.context.scene.render.layers[FG_LAYER_NAME].layers = FG_LAYER_MASK
		bpy.context.scene.render.layers[FG_LAYER_NAME].use_solid = True
		bpy.context.scene.render.layers[FG_LAYER_NAME].use_strand = False
		bpy.context.scene.render.layers[FG_LAYER_NAME].use_sky = False

	if not bg:
		bpy.ops.scene.render_layer_add()
		bpy.context.scene.render.layers[1].name = BG_LAYER_NAME
		bpy.context.scene.render.layers[BG_LAYER_NAME].layers = BG_LAYER_MASK
		bpy.context.scene.render.layers[BG_LAYER_NAME].use_solid = True
		bpy.context.scene.render.layers[BG_LAYER_NAME].use_strand = False
		bpy.context.scene.render.layers[BG_LAYER_NAME].use_sky = False

	bpy.context.scene.render.layers.active = bpy.context.scene.render.layers[FG_LAYER_NAME]



def setup_camera():
	if not bpy.context.scene.camera:
		bpy.ops.object.camera_add()
		bpy.context.scene.camera = bpy.context.object

	# set up camera position and type
	bpy.context.scene.camera.location = (0,-21,0)
	bpy.context.scene.camera.data.ortho_scale = 17
	bpy.context.scene.camera.data.type='ORTHO'
	bpy.context.scene.camera.rotation_mode = 'XYZ'
	bpy.context.scene.camera.rotation_euler = (math.radians(90),0,0)


def material_nodes(mat, rgba):
	mat.use_nodes=True

	###
	# Cycles
	###

	mat.node_tree.nodes.remove(mat.node_tree.nodes['Diffuse BSDF'])

	color = mat.node_tree.nodes.new('ShaderNodeRGB')
	emission = mat.node_tree.nodes.new('ShaderNodeEmission')
	mix = mat.node_tree.nodes.new('ShaderNodeMixShader')
	transparent = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')

	color.outputs['Color'].default_value = rgba
	emission.inputs['Strength'].default_value = 2
	mix.inputs['Fac'].default_value=0


	mat.node_tree.links.new(color.outputs['Color'],emission.inputs['Color'])
	mat.node_tree.links.new(color.outputs['Color'],transparent.inputs['Color'])

	mat.node_tree.links.new(emission.outputs['Emission'],mix.inputs[1])
	mat.node_tree.links.new(transparent.outputs['BSDF'],mix.inputs[2])

	mat.node_tree.links.new(mix.outputs['Shader'],mat.node_tree.nodes['Material Output'].inputs['Surface'])

	#tidy up
	mix.location = (118,263)
	emission.location = (-69, 283)
	transparent.location = (-62,155)
	color.location = (-276,238)

	###
	# Blender Internal
	###
	mat.use_shadeless = True

	internal = mat.node_tree.nodes.new('ShaderNodeOutput')

	cy_to_bi = mat.node_tree.nodes.new('ShaderNodeMaterial')
	cy_to_bi.material = mat
	cy_to_bi.use_specular = False


	mat.node_tree.links.new(cy_to_bi.outputs['Color'],internal.inputs['Color'])
	mat.node_tree.links.new(cy_to_bi.outputs['Alpha'],internal.inputs['Alpha'])

	internal.location = (307,156)
	cy_to_bi.location = (97, 31)




def make_text():
	#create text objects
	bpy.ops.object.text_add(radius=2, location=(0,0,0),rotation=(math.radians(90),0,0),layers=FG_LAYER_MASK)
	fg = bpy.context.object
	fg.data.body = "Something"

	bpy.ops.object.text_add(radius=2, location=(0,0.22,0),rotation=(math.radians(90),0,0),layers=BG_LAYER_MASK)
	bg = bpy.context.object
	bg.data.body = "Something"
	bg.data.bevel_depth = 0.043	

	white = None
	black = None
	for m in bpy.data.materials:
		if m.name == "Caption White":
			white = m
		elif m.name == "Caption Shadow":
			black = m

	if not white:
		white = bpy.data.materials.new("Caption White")
		material_nodes(white,(1,1,1,1))
		white.specular_hardness = 1
	if not black:
		black = bpy.data.materials.new("Caption Shadow")
		material_nodes(black,(0,0,0,1))
		black.diffuse_color = (0,0,0)

	fg.data.materials.append(white)
	bg.data.materials.append(black)

def compositor_setup():
	bpy.context.scene.use_nodes = True
	comp = bpy.context.scene.node_tree

	#set backdrop for node editor
	for area in bpy.data.screens['Compositing'].areas:
		if area.type == 'NODE_EDITOR':
			for space in area.spaces:
				if space.type == 'NODE_EDITOR':
					space.show_backdrop = True
					break
			break

	comp.nodes.clear()

	end = comp.nodes.new('CompositorNodeComposite')
	viewer = comp.nodes.new('CompositorNodeViewer')
	render_white = comp.nodes.new('CompositorNodeRLayers')
	render_black = comp.nodes.new('CompositorNodeRLayers')
	text_mixer = comp.nodes.new('CompositorNodeAlphaOver')
	clip = comp.nodes.new('CompositorNodeMovieClip')
	clip_mixer = comp.nodes.new('CompositorNodeAlphaOver')
	clip_size = comp.nodes.new('CompositorNodeScale')
	shadow_blur = comp.nodes.new('CompositorNodeBlur')
	switch = comp.nodes.new('CompositorNodeSwitch')

	end.location = (763,566)
	viewer.location = (766,415)
	render_white.location = (-132,395)
	render_black.location = (-136,153)
	text_mixer.location = (349,393)
	clip.location = (-140,834)
	clip_mixer.location = (551,530)
	clip_size.location = (50,724)
	shadow_blur.location = (52,101)
	switch.location = (228,233)

	render_white.layer=FG_LAYER_NAME
	render_black.layer=BG_LAYER_NAME

	clip_size.space = 'RENDER_SIZE'
	shadow_blur.filter_type = 'FAST_GAUSS'
	shadow_blur.size_x = 2
	shadow_blur.size_y = 2
	shadow_blur.inputs['Size'].default_value = 2

	switch.label = "Enable Blur"

	comp.links.new(clip.outputs['Image'],clip_size.inputs['Image'])
	comp.links.new(clip_size.outputs['Image'],clip_mixer.inputs[1])
	comp.links.new(clip_mixer.outputs['Image'],end.inputs['Image'])
	comp.links.new(clip_mixer.outputs['Image'],viewer.inputs['Image'])
	comp.links.new(render_black.outputs['Image'],shadow_blur.inputs['Image'])
	comp.links.new(render_black.outputs['Image'],switch.inputs['Off'])
	comp.links.new(shadow_blur.outputs['Image'],switch.inputs['On'])
	comp.links.new(switch.outputs['Image'],text_mixer.inputs[1])
	comp.links.new(render_white.outputs['Image'],text_mixer.inputs[2])
	comp.links.new(text_mixer.outputs['Image'],clip_mixer.inputs[2])


class CaptionOperator(bpy.types.Operator):
	bl_idname = "object.caption"
	bl_label = "Caption"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		render_settings()
		speedup_settings()
		setup_camera()
		scene_layers()
		compositor_setup()

		make_text()

		bpy.context.scene.render.engine = 'BLENDER_RENDER'

		return {'FINISHED'}	

class CaptionPanel(bpy.types.Panel):
	bl_label = "Caption"
	bl_idname = "OBJECT_PT_caption"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		row = col.row(align=True)
		row.operator("object.caption", text = "Setup")



def register():
	bpy.utils.register_class(CaptionPanel)
	bpy.utils.register_class(CaptionOperator)
def unregister():
	bpy.utils.unregister_class(CaptionPanel)
	bpy.utils.unregister_class(CaptionOperator)

if __name__ == "__main__":
	register()

