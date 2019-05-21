# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

class Base_Material(bpy.types.Operator):

	bl_idname = "material.basemat"
	bl_label = "base_mat"
	bl_description = "Make a new material"

	# Nodes coords
	# 'Cursor' position
	x=0
	y=0

	# Translate value
	t=300

	# Error msg
	error=0
	msg=""
	has_image=False

	# Get Named Node or Create It
	def get_node(self,tree,engine,name):

		found=0

		if engine == 'blender':
			for node in tree.nodes:
				if node.name==name:
					found=1
					return node

			if not found:
				if name == 'Output':
					tree.nodes.new('ShaderNodeOutput')
					node=tree.nodes['Output']
					node.location=(self.x,self.y)
					self.x+=self.t
					return node
				else:
					tree.nodes.new('ShaderNodeMaterial')
					node=tree.nodes['Material']
					node.location=(self.x,self.y)
					self.x+=self.t
					return node
	
		else:

			for node in tree.nodes:
				if node.name==name:
					found=1
					self.x+=self.t
					return node

			if not found:
				if name=='Material Output':
					tree.nodes.new('ShaderNodeOutputMaterial')
					node=tree.nodes['Material Output']
					node.location=(self.x,self.y)
					self.x+=self.t
					return node
				elif name=="Diffuse BSDF":
					tree.nodes.new('ShaderNodeBsdfDiffuse')
					node=tree.nodes['Diffuse BSDF']
					node.location=(self.x,self.y)
					self.x+=self.t
					return node
				elif name=="Image Texture":
					tree.nodes.new('ShaderNodeTexImage')
					node=tree.nodes['Image Texture']
					node.location=(self.x,self.y)
					self.x+=self.t
					return node
				elif name=="Texture Coordinate":
					tree.nodes.new('ShaderNodeTexCoord')
					node=tree.nodes['Texture Coordinate']
					node.location=(self.x,self.y)
					self.x+=self.t
					return node
				elif name=="Mapping":
					tree.nodes.new('ShaderNodeMapping')
					node=tree.nodes['Mapping']
					node.location=(self.x,self.y)
					self.x+=self.t
					return node
				elif name=="Transparent BSDF":
					tree.nodes.new('ShaderNodeBsdfTransparent')
					node=tree.nodes['Transparent BSDF']
					node.location=(self.x,self.y)
					self.x+=self.t
					return node
				elif name=="Mix Shader":
					tree.nodes.new('ShaderNodeMixShader')
					node=tree.nodes['Mix Shader']
					node.location=(self.x,self.y)
					self.x+=self.t
					return node

	def is_cutout(self,mat):
		
		if mat.arx_material_type in ['Vegetal','Human']: return True
		else: return False

	def with_texture(self,mat):
		
		if mat.arx_material_type in ['Texture','Vegetal','Human','Cutout']: return True
		else: return False

	def get_image(self,mat):

		image_name=mat.texture_slots[0].name

		if image_name in bpy.data.images:
			image=bpy.data.images[image_name]
			return image
		else:
			if image_name + '.png' in bpy.data.images:
				image=bpy.data.images[image_name+'.png']
				return image
			else:
				return "NULL"

	def set_image(self,mat,node):

		image=self.get_image(mat)
		if(image!="NULL"): node.image=image
		else: 
			self.msg+= "[ERROR] image not found"
			self.error=1

	def build_cutout(self,mat):

		tree=mat.node_tree

		self.x = 0
		self.y -= 300

		# NODES
		node_texture_coordinate=self.get_node(tree,"cycles","Texture Coordinate")
		node_texture=self.get_node(tree,"cycles","Image Texture")

		self.set_image(mat,node_texture)
		node_texture.projection='FLAT'

		node_transparent=self.get_node(tree,"cycles","Transparent BSDF")
		self.y-=150
		
		node_diffuse=self.get_node(tree,"cycles","Diffuse BSDF")

		self.y+=150

		node_mix=self.get_node(tree,"cycles","Mix Shader")
		node_output=self.get_node(tree,"cycles","Material Output")	

		# SOCKETS

		diffuse_out=node_diffuse.outputs['BSDF']
		diffuse_in=node_diffuse.inputs['Color']

		transparent_out=node_transparent.outputs['BSDF']

		mix_fac_in=node_mix.inputs['Fac']
		mix_shader_1_in=node_mix.inputs[1]
		mix_shader_2_in=node_mix.inputs[2]
		mix_out=node_mix.outputs['Shader']

		texture_coordinate_out=node_texture_coordinate.outputs['UV']

		texture_in=node_texture.inputs['Vector']
		texture_out=node_texture.outputs['Color']
		texture_alpha_out=node_texture.outputs['Alpha']

		output_in=node_output.inputs['Surface']

		if not texture_coordinate_out.is_linked: tree.links.new(texture_coordinate_out,texture_in)
		if not texture_out.is_linked: tree.links.new(texture_out,diffuse_in)
		if not texture_alpha_out.is_linked: tree.links.new(texture_alpha_out,mix_fac_in)
		if not transparent_out.is_linked: tree.links.new(transparent_out,mix_shader_1_in)
		if not diffuse_out.is_linked: tree.links.new(diffuse_out,mix_shader_2_in)
		if not mix_out.is_linked: tree.links.new(mix_out,output_in)

	def build_default(self,mat):

		tree=mat.node_tree

		self.x = 0
		self.y -= 300

		# NODES
		node_texture_coordinate=self.get_node(tree,"cycles","Texture Coordinate")
		node_texture=self.get_node(tree,"cycles","Image Texture")

		self.set_image(mat,node_texture)

		node_diffuse=self.get_node(tree,"cycles","Diffuse BSDF")

		node_output=self.get_node(tree,"cycles","Material Output")	

		texture_coordinate_out=node_texture_coordinate.outputs['UV']

		# SOCKETS

		diffuse_out=node_diffuse.outputs['BSDF']
		diffuse_in=node_diffuse.inputs['Color']

		texture_in=node_texture.inputs['Vector']
		texture_out=node_texture.outputs['Color']

		output_in=node_output.inputs['Surface']

		if not texture_coordinate_out.is_linked: tree.links.new(texture_coordinate_out,texture_in)
		if not texture_out.is_linked: tree.links.new(texture_out,diffuse_in)

		if not diffuse_out.is_linked: tree.links.new(diffuse_out,output_in)



	def build_shadow_material(self,context,ob):
		
		current_engine=bpy.context.scene.render.engine

		# Switch to 'CYCLES'
		bpy.context.scene.render.engine='CYCLES'

		# Get Material
		mat=ob.material_slots[0].material
		print("current material:" + mat.name)

		# Copy 
		shadow_mat = mat.copy()
		name = mat.name
		shadow_mat.name = name + "_shadow"
		shadow_mat.arx_material_is_shadow = True

		# Set Options
		shadow_mat.arx_alpha_use_texture = 0
		shadow_mat.arx_alpha_use_global_id = 0
		shadow_mat.arx_alpha_exclude = 1

		# Add New Slot
		bpy.context.scene.objects.active = ob
		print("build shadow")
		print("active object:" + bpy.context.active_object.name)
		bpy.ops.object.material_slot_add()
		ob.material_slots[1].material = shadow_mat

		# Adjust Tree
		tree = shadow_mat.node_tree

		first_mix_node=tree.nodes['Mix Shader']
		loc = first_mix_node.location

		output_node = tree.nodes['Material Output']
		output_node.location[0]+=500

		light_node=tree.nodes.new('ShaderNodeLightPath')
		light_node.location = (loc[0],loc[1]+600)

		mix_node=tree.nodes.new('ShaderNodeMixShader')
		mix_node.location=(loc[0]+500,loc[1])

		transparent_node=tree.nodes.new('ShaderNodeBsdfTransparent')
		transparent_node.location=(loc[0],loc[1]+300)

		tree.links.new(light_node.outputs['Is Shadow Ray'],mix_node.inputs['Fac'])
		tree.links.new(transparent_node.outputs['BSDF'],mix_node.inputs[1])
		tree.links.new(first_mix_node.outputs['Shader'],mix_node.inputs[2])
		tree.links.new(mix_node.outputs['Shader'],output_node.inputs['Surface'])
		print("done")

		return shadow_mat

	# Build Material Nodes
	def build(self,context,ob):
		
		# Get Engine
		current_engine=bpy.context.scene.render.engine

		# Switch to 'BLENDER'
		bpy.context.scene.render.engine='BLENDER_RENDER'

		# Add default nodes
		mat=ob.material_slots[0].material

		# Delete all nodes
		if(mat.use_nodes):
			mat.node_tree.nodes.clear()

		# Use Nodes
		mat.use_nodes=True

		# Use Transparent Shadow
		mat.use_transparent_shadows=True

		# Tree
		tree=mat.node_tree

		# Textures
		if(self.with_texture(mat)):

			# Material Options
			mat.use_transparency=True
			mat.transparency_method='RAYTRACE'
			mat.alpha=0
			mat.specular_intensity=0
	
			slot=mat.texture_slots[0]
			tex=slot.texture

			# Texture Options
			if(tex):

				tex.use_preview_alpha=True
				if(tex.type == 'IMAGE'):

					# Set Image
					img=tex.image
					has_image=True
					img.alpha_mode='PREMUL'
					img.use_alpha=True
					slot.use_map_alpha=True
		

		# Build Blender Render Nodes
		node_material=self.get_node(tree,"blender","Material")
		node_output=self.get_node(tree,"blender","Output")

		# Set Material Node's material  
		node_material.material=bpy.data.materials[mat.name]

		# Get Sockets
		color_out=node_material.outputs['Color']
		color_in=node_output.inputs['Color']
		alpha_out=node_material.outputs['Alpha']
		alpha_in=node_output.inputs['Alpha']

		# Connect Material Color > Output Color
		if not color_out.is_linked : tree.links.new(color_out,color_in)

		# If Cutout, connect Alphas
		if(self.is_cutout(mat)):
			if not alpha_out.is_linked : tree.links.new(alpha_out,alpha_in)
			mat.arx_alpha_use_global_id=True
			if mat.arx_material_type=='Tree': mat.arx_alpha_global_id=2
			if mat.arx_material_type=='Human': mat.arx_alpha_global_id=1

			mat.arx_alpha_use_texture=True

		# switch to 'CYCLES'
		bpy.context.scene.render.engine='CYCLES'

		tree=mat.node_tree

		mat_type=mat.arx_material_type

		# Cutout Type
		if(self.is_cutout(mat)): 
			self.build_cutout(mat)

		# Default Type
		else:
			self.build_default(mat)

		# switch back to previous engine
		bpy.context.scene.render.engine=current_engine


