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
from . arx_base import Base_Material
import bmesh
from mathutils import Vector
from math import radians
import math

class OP_Align_To_Camera(bpy.types.Operator):
	bl_idname="object.align_to_camera"
	bl_label="align_to_camera"

	def execute(self,context):
		for object in bpy.context.selected_objects:
			x = object.location.x
			y = object.location.y
			z = object.location.z

			camera = bpy.data.objects['Camera']

			object.matrix_world = camera.matrix_world
			object.location.x = x
			object.location.y = y
			object.location.z = z

		return {'FINISHED'}
	
	def invoke(self,context,event):
		return self.execute(context)

class OP_Align_To_Sun(bpy.types.Operator):
	bl_idname="object.align_to_sun"
	bl_label="align_to_sun"

	def execute(self,context):
		for object in bpy.context.selected_objects:
			x = object.location.x
			y = object.location.y
			z = object.location.z

			sun  = bpy.data.objects['Lamp']
			object_matrix = object.matrix_basis
			object_euler = object_matrix.to_euler()

			euler = sun.matrix_basis.to_euler()
			euler[0]=math.pi/2.0

			matrix = euler.to_matrix()
			new  = matrix.to_4x4()

			object.matrix_basis = new
			object.location.x = x
			object.location.y = y
			object.location.z = z

		return {'FINISHED'}
	
	def invoke(self,context,event):
		return self.execute(context)



# UnBuild Shadow
class OP_UnBuild_Shadow(Base_Material,bpy.types.Operator):
	bl_idname="object.unbuild_shadow"
	bl_label="unbuild_shadow"

	# Mesh Must Have Exactly 2 Polygons
	@classmethod
	def poll(self, context):
		obj = context.active_object
		if obj != None and obj.type == 'MESH':
			me = obj.data
			p = me.polygons
			if(len(p)==2):
				return 1
			else:
				return 0
		else:
			return 0

	def exec(self,context):

		ob=bpy.context.active_object
		me=ob.data
		p=me.polygons

		# EDIT MODE
		if not (ob.mode == 'EDIT'):
			bpy.ops.object.mode_set(mode='EDIT')

		# Delete
		bpy.ops.mesh.delete()

		# Update Mesh
		bpy.ops.object.mode_set(mode='OBJECT')
		me.update()

		p = me.polygons
		p[0].select = 1

		return {'FINISHED'}

	def invoke(self,context,event):
		return self.exec(context)

# Build Shadow
class OP_Build_Shadow(Base_Material,bpy.types.Operator):
	bl_idname="object.build_shadow"
	bl_label="build_shadow"
	bl_description="build shadow"

	@classmethod
	# Mesh Must Have Exactly 1 Polygon
	def poll(self, context):
		obj = context.active_object
		if obj != None and obj.type == 'MESH':
			me = obj.data
			p = me.polygons
			if(len(p)==1):
				return 1
			else:
				return 0
		else:
			return 0


	def execute(self,context):

		ob=bpy.context.active_object
		me=ob.data
		p=me.polygons

		# EDIT MODE
		is_editmode = (ob.mode == 'EDIT')
		if not is_editmode:
			bpy.ops.object.mode_set(mode='EDIT')

		bm = bmesh.from_edit_mesh(me)

		uv_layer = bm.loops.layers.uv.verify()
		bm.faces.layers.tex.verify()  # currently blender needs both layers.

		# Vectors
		v0=[0,0,0]
		v1=[0,0,0]

		shadow_mat=0
		has_shadow_mat=0

		# Get UVs
		for f in bm.faces:
			for l in f.loops:
				luv = l[uv_layer]
				# Get (0,0)
				if(luv.uv[0] == 0.0 and luv.uv[1] == 0.0):
					v0=l.vert.co.xyz
				# Get (1,0)
				elif(luv.uv[0] == 0.0 and luv.uv[1] == 1.0):
					v1=l.vert.co.xyz


		#bmesh.update_edit_mesh(me)

		# Build Vector
		vv0 = Vector(v0)
		vv1 = Vector(v1)
		vv = vv1 - vv0 

		# Apply Rotation Matrix
		rot = ob.rotation_euler
		vv.rotate(rot)

		# Check For Shadow Material
		for mat in me.materials:
			if mat.arx_material_is_shadow:
				shadow_material = mat
				has_shadow_mat = 1

		# Build default Shadow Material
		if not has_shadow_mat:
			shadow_mat = self.build_shadow_material(self,ob)

		# Duplicate
		bpy.ops.mesh.duplicate()
		bpy.ops.transform.rotate(value=radians(90.0),axis=vv)

		# Update Mesh
		bpy.ops.object.mode_set(mode='OBJECT')
		me.update()

		# Set Shadow Material
		p = ob.data.polygons
		p[1].material_index = 1

		return {'FINISHED'}

	def invoke(self,context,event):
		return self.execute(context)

class OP_Build_Shadow_m(Base_Material,bpy.types.Operator):
	bl_idname="object.build_shadow_m"
	bl_label="build_shadow_m"
	bl_description="build shadow"

	@classmethod
	def poll(self, context):
		obj = context.active_object
		return obj != None and obj.type == 'MESH'

	def execute(self,context):
		print("execute")

		objs = bpy.context.selected_objects
		for ob in objs:
			bpy.context.scene.objects.active = ob
			print("active:"+ob.name)
			bpy.ops.object.build_shadow()

		return {'FINISHED'}

	def invoke(self, context,event):
		print("invoke!")
		return self.execute(context)


# SET DISPLAY OPTIONS
class OP_Set_Options(bpy.types.Operator):

	bl_idname = "object.set_options"
	bl_label = "Set Materials"
	bl_description = "Set materials"

	def invoke(self,context,event):
		for ob in bpy.data.objects:
			if ob.type == 'MESH':
				mesh = ob.data
				if bpy.context.scene.arx_wire_do:
					if bpy.context.scene.arx_wire:
						ob.show_wire = True
					else:
						ob.show_wire = False 
				if bpy.context.scene.arx_normals_do:
					if bpy.context.scene.arx_normals:
						mesh.show_normal_face = True
					else:
						mesh.show_normal_face = False
				if bpy.context.scene.arx_length_do:
					if bpy.context.scene.arx_length:
						mesh.show_extra_edge_length = True
					else:
						mesh.show_extra_edge_length = False
				if bpy.context.scene.arx_name_do:
					if bpy.context.scene.arx_name:
						ob.show_name = True
					else:
						ob.show_name = False
						

		return {'FINISHED'}

# APPLY MODIFIERS
class OP_Apply_all_modifiers(bpy.types.Operator):

	bl_idname = "object.apply_all_modifiers"
	bl_label = "Set Materials"
	bl_description = "Set materials"

	def invoke(self,context,event):
		for ob in bpy.data.objects:
			if ob.type == 'MESH':
				bpy.context.scene.objects.active = ob
				mods = ob.modifiers
				for m in mods:
					if bpy.context.scene.arx_only_array == True:
						if m.type == "ARRAY":
							bpy.ops.object.modifier_apply(apply_as='DATA',modifier=m.name)
					else:
						bpy.ops.object.modifier_apply(apply_as='DATA',modifier=m.name)

		return {'FINISHED'}

# RENAME OBJECTS
class OP_Rename_selected(bpy.types.Operator):

	bl_idname = "object.rename_selected"
	bl_label = "Set Materials"
	bl_description = "Set materials"
	
	i = 0

	def invoke(self,context,event):
		i=0
		objs=bpy.context.selected_objects
		for ob in objs:
			ob.name = bpy.context.scene.arx_rename + "_" + str(self.i)
			self.i+=1
			

		return {'FINISHED'}

# PANEL OBJECT
class RVBA_Display_Panel(bpy.types.Panel):

	bl_space_type='PROPERTIES'
	bl_region_type='WINDOW'
	bl_context="object"
	bl_label="Object Tools"

	bpy.types.Scene.arx_wire = bpy.props.BoolProperty("arx_wire",default=False)
	bpy.types.Scene.arx_wire_do = bpy.props.BoolProperty("arx_wire_do",default=False)
	bpy.types.Scene.arx_normals = bpy.props.BoolProperty("arx_normals",default=False)
	bpy.types.Scene.arx_normals_do = bpy.props.BoolProperty("arx_normals_do",default=False)
	bpy.types.Scene.arx_length = bpy.props.BoolProperty("arx_length",default=False)
	bpy.types.Scene.arx_length_do = bpy.props.BoolProperty("arx_length_do",default=False)
	bpy.types.Scene.arx_name = bpy.props.BoolProperty("arx_name",default=False)
	bpy.types.Scene.arx_name_do = bpy.props.BoolProperty("arx_name_do",default=False)

	bpy.types.Scene.arx_only_array = bpy.props.BoolProperty("arx_only_array",default=False)

	bpy.types.Scene.arx_rename = bpy.props.StringProperty("arx_rename")

	def draw(self,context):

		# DISPLAY
		col=self.layout.column(align=True)
		col.label("Display",icon='MODIFIER')
		col.separator()

		row=col.row()
		row.alignment = 'LEFT'
		row.prop(context.scene,"arx_wire_do",text="")
		row.prop(context.scene,"arx_wire",text="wire")
		row.operator(OP_Set_Options.bl_idname,text="Set Options")

		row=col.row()
		row.alignment = 'LEFT'
		row.prop(context.scene,"arx_normals_do",text="")
		row.prop(context.scene,"arx_normals",text="normals")

		row=col.row()
		row.alignment = 'LEFT'
		row.prop(context.scene,"arx_length_do",text="")
		row.prop(context.scene,"arx_length",text="length")

		row=col.row()
		row.alignment = 'LEFT'
		row.prop(context.scene,"arx_name_do",text="")
		row.prop(context.scene,"arx_name",text="name")

		col.separator()

		# MODIFIERS

		col=self.layout.column(align=True)
		col.label("Modifier",icon='MODIFIER')
		col.separator()
		row = col.row()
		row.prop(context.scene,"arx_only_array",text="only array")
		row.operator(OP_Apply_all_modifiers.bl_idname,text="Apply all modifiers")

		col.separator()

		# NAMES

		col=self.layout.column(align=True)
		col.label("Names",icon='MODIFIER')
		col.separator()
		row = col.row()
		row.prop(context.scene,"arx_rename",text="")
		row = col.row()
		row.operator(OP_Rename_selected.bl_idname,text="Rename selected")

		# SHADOW

		col=self.layout.column(align=True)
		col.label("Shadow",icon='MODIFIER')
		col.separator()
		row = col.row()
		row.operator(OP_Build_Shadow.bl_idname,text="Build Shadow")
		row.operator(OP_UnBuild_Shadow.bl_idname,text="UnBuild Shadow")

		row = col.row()
		row.operator(OP_Build_Shadow_m.bl_idname,text="Build ShadowS")

		row = col.row()

		row.operator(OP_Align_To_Camera.bl_idname,text="Align To Camera")
		row.operator(OP_Align_To_Sun.bl_idname,text="Align To Sun")
