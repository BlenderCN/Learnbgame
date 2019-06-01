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
from bpy.types import Operator
import mathutils
import os
import collections
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy_extras.image_utils import load_image
from . arx_base import Base_Material

from mathutils import Vector

# Derived from Import_Cutout < Base_Material (see arx_base.py)
class IMPORT_Cutout(Base_Material, AddObjectHelper):

	bl_idname = "image.arx_import_image"
	bl_label = "Create Cutout"
	bl_options = {'REGISTER', 'UNDO'}

	posx,posy,posz=0,0,0
	location=[0,0,0]

	cutout_type='Regular'

	def make_material(self,img):

		tex=bpy.data.textures.new(img.name,type='IMAGE')
		tex.image=img
		mat=bpy.data.materials.new(img.name)
		mat.arx_material_type=self.cutout_type
		slot=mat.texture_slots.add()
		slot.texture=tex
		slot.texture_coords='UV'

		return mat

	def make_objects(self,context,mat):

		img=mat.texture_slots[0].texture.image
		px,py=img.size

		h=1.65
		l=px*(h/py)

		verts=(	
			((-l)*0.5,0,0),
			( l*0.5,0,0),
			( l*0.5,h,0),
			((-l)*0.5,h,0)
			)
		faces=((0,1,2,3),)

		bpy.ops.mesh.primitive_plane_add('INVOKE_REGION_WIN')
		plane = context.scene.objects.active

		# Why does mesh.primitive_plane_add leave the object in edit mode???
		if plane.mode is not 'OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')

		plane.dimensions = l, h, 0.0
		bpy.ops.object.transform_apply(scale=True)
		plane.data.uv_textures.new()
		plane.data.materials.append(mat)
		plane.data.uv_textures[0].data[0].image = img

		mat.game_settings.use_backface_culling = False
		mat.game_settings.alpha_blend = 'ALPHA'

		plane.rotation_euler[0]=1.570797
		plane.location=(self.posx,self.posy,self.posz)
		self.posx+=l+.5

		bpy.context.scene.cursor_location = plane.location
		bpy.context.scene.cursor_location.z = -h/2

		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		plane.location.z = 0

		bpy.context.scene.cursor_location = Vector([0,0,0])

		return plane


	def make_path(self,context):
		return (fn.name for fn in self.files) , self.directory

	# Main call
	def import_images(self,context):

		import_list,directory=self.make_path(context)
		# Load Images
		images=(load_image( path, directory) for path in import_list)
		# Make Materials
		materials=(self.make_material(img) for img in images)
		# Make Objects
		objects= tuple(self.make_objects(context,mat) for mat in materials)
		# Update Scene
		context.scene.update()
		for ob in objects:ob.select=True
		# Build Material Nodes (Base_Mat)
		for ob in objects:self.build(context,ob)
		self.report({'INFO'},"Added {} objects".format(len(objects)))

	def draw(self,context):
		layout=self.layout
		box=layout.box()
		box.label("Options",icon='FILTER')
	
# Classes, derived from Import_Cutout < Base_Material (see arx_base_mat.py)
class IMPORT_Human(IMPORT_Cutout,Operator):

	bl_idname = "image.arx_import_human"
	bl_label = "Create Cutout"
	bl_options = {'REGISTER', 'UNDO'}

	files=bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement,options={'HIDDEN','SKIP_SAVE'})
	directory=bpy.props.StringProperty(maxlen=1024,subtype='FILE_PATH',options={'HIDDEN','SKIP_SAVE'})
	posx,posy,posz=0,0,0

	def invoke(self,context,event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self,context):
		self.cutout_type="Human"
		# Call
		self.import_images(context)
		return {'FINISHED'}

class IMPORT_Vegetal(IMPORT_Cutout,Operator):

	bl_idname = "image.arx_import_vegetal"
	bl_label = "Create Cutout"
	bl_options = {'REGISTER', 'UNDO'}

	files=bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement,options={'HIDDEN','SKIP_SAVE'})
	directory=bpy.props.StringProperty(maxlen=1024,subtype='FILE_PATH',options={'HIDDEN','SKIP_SAVE'})
	posx,posy,posz=0,0,0

	def invoke(self,context,event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self,context):
		self.cutout_type='Vegetal'
		# Call
		self.import_images(context)
		return {'FINISHED'}

class IMPORT_Cutout(IMPORT_Cutout,Operator):

	bl_idname = "image.arx_import_cutout"
	bl_label = "Create Cutout"
	bl_options = {'REGISTER', 'UNDO'}

	files=bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement,options={'HIDDEN','SKIP_SAVE'})
	directory=bpy.props.StringProperty(maxlen=1024,subtype='FILE_PATH',options={'HIDDEN','SKIP_SAVE'})
	posx,posy,posz=0,0,0

	def invoke(self,context,event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self,context):
		self.cutout_type='Cutout'
		# Call
		self.import_images(context)
		return {'FINISHED'}

# Operators

def import_human(self, context):
	self.layout.operator(IMPORT_Human.bl_idname, text="Human", icon='ARMATURE_DATA')

def import_vegetal(self, context):
	self.layout.operator(IMPORT_Vegetal.bl_idname, text="Vegetal", icon='HAIR')

def import_image(self, context):
	self.layout.operator(IMPORT_Cutout.bl_idname, text="Image" , icon='FILE_IMAGE')



