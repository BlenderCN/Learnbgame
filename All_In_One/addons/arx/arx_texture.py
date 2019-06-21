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
import mathutils
import re
import os
import os.path
import shutil
from bpy.props import *
from . arx_base import Base_Material

def is_image_local(image):
	if image.filepath[0] == '/' and image.filepath[1] == '/':
		return 1
	else:
		return 0

def file_exists(path):
	if os.path.exists(path): return 1
	else: return 0

def get_base_path(path):
	return os.path.dirname(path)

def get_blend_path():
	return get_base_path(bpy.data.filepath)

def build_path(type):
	if type == "Original":
		path = get_blend_path() + "/textures"
	else:
		path = get_blend_path() + "/textures"
		path += "/" + type

	return path

def build_abs_path(path):
	return bpy.path.abspath(path)

def check_dir(path):
	if not file_exists(path):
		os.makedirs(path)

def make_image_local(image):

	if not is_image_local(image):

		# Check Blend Is Saved
		path = get_blend_path()

		# Check /textures
		if(path):
			path += "/textures"
			check_dir(path)

		# Check image
		path += "/" + image.name

		# Copy
		if not file_exists(path):
			shutil.copy2(image.filepath,path)

		# Change Path
		name = image.name
		image.filepath = "//textures/" + name
		
		return 1
	else:
		return 0

def build_image(img,type):

	# Make Local
	if not is_image_local(img):
		make_image_local(img)

	# Path
	path = build_path(type)

	# Check Dir exists
	check_dir(path)

	# Check File exists
	path = path + "/" + img.name

	# Copy
	src_path = build_abs_path(img.filepath)

	#if check_dir(src_path):
	if file_exists(src_path):
		if not file_exists(path):
			shutil.copy2(src_path,path)

			width = img.size[0]
			height = img.size[1]

			if type == "Low":
				dim = 200
			elif type == "Medium":
				dim = 800
			elif type == "High":
				dim = 1500
			else:
				dim = 0

			# If Not Original
			if dim:
				if height > width:
					largest = height
					command = "mogrify -resize x" + str(dim) + " " + path
				else:
					largest = width
					command = "mogrify -resize " + str(dim) + " " + path

				os.system(command)
	else:
		return 1


def set_image_size(image):
	
	size = image.arx_image_resolution
	path = "//textures"
	if size == "Low":
		path += "/Low/" + image.name
	elif size == "Medium":
		path += "/Medium/" + image.name
	elif size == "High":
		path += "/High/" + image.name
	# Original
	else:
		path += "/" + image.name

	# Set New Path
	image.filepath = path

def get_image(context):

	mat = context.material
	render_engine = bpy.context.scene.render.engine

	if(render_engine == 'CYCLES'):
		if mat:
			tree = mat.node_tree
			for node in tree.nodes:
				if node.name == 'Image Texture':
					image = node.image
		else:
			image = 0
	else:
		tex = context.texture
		if tex.type == 'IMAGE':
			image=tex.image

	return image

def get_texture_image(texture):

	mat = context.material
	render_engine = bpy.context.scene.render.engine

	if(render_engine == 'CYCLES'):
		if mat:
			tree = mat.node_tree
			for node in tree.nodes:
				if node.name == 'Image Texture':
					image = node.image
		else:
			image = 0
	else:
		tex = context.texture
		if tex.type == 'IMAGE':
			image=tex.image

	return image



class OP_Image_Resize(Base_Material,bpy.types.Operator):

	bl_idname="object.arx_resize"
	bl_label="image_resize"
	bl_description="Resize Image"

	def invoke(self,context,event):
		return {'RUNNING_MODAL'}
	
	@classmethod
	def poll(self, context):
		image = get_image(context)
		if(image): return 1
		else: return 0

	def execute(self,context):

		image = get_image(context)

		if(image):
			build_image(image, image.arx_image_resolution)
			set_image_size(image)

		return {'FINISHED'}

	def invoke(self,context,event):
		return self.execute(context)


class OP_Make_textures_local(bpy.types.Operator):

	bl_idname = "object.make_textures_local"
	bl_label = "Remove double materials"
	bl_description = "set textures path to //textures/"

	lst=[]
	textures=""
	msg=""

	def execute(self, context):
		self.report({'INFO'}, self.textures)
		self.report({'INFO'}, "DONE"  )
		return {'FINISHED'}

	def invoke(self,context,event):
		images = bpy.data.images

		for image in images:
			name = image.name
			image.filepath = "//textures/" + name
			self.msg+=name+"\n"
			
		return self.execute(context)

class OP_Make_Image_Local(bpy.types.Operator):

	bl_idname = "mage.make_local"
	bl_label = "Make Image Local"
	bl_description = "Set Image Path to //textures/"

	def execute(self, context):

		image = get_image(context)

		if(image):

			if(make_image_local(image)):
				self.report({'INFO'}, "DONE"  )
			else:
				self.report({'INFO'}, "ALREADY LOCAL")

		return {'FINISHED'}

	def invoke(self,context,event):
		return self.execute(context)


class OP_Copy_textures_local(bpy.types.Operator):

	bl_idname = "object.copy_textures_local"
	bl_label = "Copy textures to local"
	bl_description = "copy textures"

	lst=[]
	textures=""
	msg=""
	err=0

	def execute(self, context):

		filepath=bpy.data.filepath

		print("COPY TEXTURE LOCAL")

		# If File is saved (filpath)
		if(filepath):
			images = bpy.data.images
			basepath = os.path.dirname(filepath)
			texturespath = basepath+"/textures"
			
			# Make Textures Folder
			if not os.path.exists(texturespath):
				print("make dir:" + texturespath)
				os.makedirs(texturespath)

			# Copy Local
			for image in images:
				print(">>" + image.name)
				name = image.name
				if name != "Render Result":
					imagepath = bpy.path.abspath(image.filepath)
					target = texturespath+"/"+name
					if imagepath:
						print("imagepath:"+imagepath)
						print("target:"+target)
						#if check_dir(imagepath):
						if file_exists(imagepath):
							if not os.path.exists(target):
								print("src:" + imagepath)
								print("dst:" + target)
								shutil.copy2(imagepath,target)
						else:
							self.report({'INFO'},"path dont exists:"+imagepath)
							self.err=1

		print("[DONE] COPY TEXTURE LOCAL")


		if self.err:
			self.report({'INFO'}, "ERROR"  )
		else:
			self.report({'INFO'}, "DONE"  )

		return {'FINISHED'}
			

	def invoke(self,context,event):
		return self.execute(context)

class OP_Set_Global_Resolution(bpy.types.Operator):

	bl_idname="scene.set_global_resolution"
	bl_label="Set global resolution"

	lst=[]
	err=0

	def check_error(self,err,name):
		if(err==1):
			self.report({'INFO'},"image doesn't exists:" + name)

	def execute(self, context):

		textures = bpy.data.textures
		scene = bpy.context.scene
		resolution = scene.arx_global_resolution

		images = bpy.data.images
		for image in images:
			if (image.name != "Render Result" and image.name != "Viewer Node"):
				if not image.arx_image_use_local_resolution:
					image.arx_image_resolution = resolution
					self.check_error(build_image(image,image.arx_image_resolution),image.name)
					set_image_size(image)

		if self.err:
			for item in self.lst:
				self.report({'INFO'},item)
			self.report({'INFO'},"ERROR");

		return {'FINISHED'}

	def invoke(self,context,event):
		return self.execute(context)


# Panel Texture
class Panel_Rvba_Texture(bpy.types.Panel):

	bl_space_type='PROPERTIES'
	bl_region_type='WINDOW'
	bl_context="texture"
	bl_label="Texture Resolution"

	# Image resolution
	bpy.types.Image.arx_image_resolution = bpy.props.EnumProperty(
						items=[
							("Original","Original","Original"),
							("Low","Low","Low"),
							("Medium","Medium","Medium"),
							("High","High","High"),
							],
						name="arx_image_resolution")

	# Global Image Resolution
	bpy.types.Scene.arx_global_resolution = bpy.props.EnumProperty(
						items=[
							("Original","Original","Original"),
							("Low","Low","Low"),
							("Medium","Medium","Medium"),
							("High","High","High"),
							],
						name="arx_global_resolution")


	# Use Local resolution
	bpy.types.Image.arx_image_use_local_resolution = bpy.props.BoolProperty("arx_image_use_local_resolution",default=False)

	def draw(self,context):

		# ** Global
		col=self.layout.column(align=True)
		col.label("Textures",icon='MODIFIER')

		# Copy textures local
		col.operator(OP_Copy_textures_local.bl_idname,text="Copy Textures Local")

		# Set textures local
		col.operator(OP_Make_textures_local.bl_idname,text="Set Textures Local")

		# ** Global resolution
		col=self.layout.column(align=True)
		scene = bpy.context.scene
		col.prop(scene,"arx_global_resolution",text="")
		col.operator(OP_Set_Global_Resolution.bl_idname,text="Set Global Resolution")

		mat = context.material
		tex = context.texture
	
		if mat: col.label(mat.name)

		render_engine = bpy.context.scene.render.engine

		if(render_engine == 'CYCLES'):
			if mat:
				tree = mat.node_tree
				for node in tree.nodes:
					if node.name == 'Image Texture':
						img = node.image
			else:
				img = 0
		else:
			if tex:
				if tex.type == 'IMAGE':
					# Get Image
					img=tex.image
				else:
					img=0
			else:
				img = 0

		# ** Individual
		if img:

			# LOCAL
			is_local = 0
			if(is_image_local(img)): is_local = 1

			row=self.layout.row(align=True)

			if is_local:
				row.label("LOCAL")
			else:
				row.label("DISTANT")

			row.label(str(img.size[0]) + "x" + str(img.size[1]))
			
			col=self.layout.column(align=True)
			# Make Local
			col.operator(OP_Make_Image_Local.bl_idname,text="Make local")
			# Choose resolution
			col.prop(img,"arx_image_resolution",text="")
			# Resize
			col.operator(OP_Image_Resize.bl_idname,text="Resize")
			col.prop(img,"arx_image_use_local_resolution",text="Use local resolution")




