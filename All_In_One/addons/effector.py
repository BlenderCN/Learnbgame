########
"""
This code is open source under the MIT license.

Its purpose is to help create special motion graphics
with effector controls inspired by Cinema 4D.

Example usage:
https://www.youtube.com/watch?v=BYXmV7fObOc

Notes to self:
Create a simialr, lower poly contorl handle and
perhaps auto enable x-ray/bounding.
Long term, might become an entire panel with tools
of all types of effectors, with secitons like 
convinience tools (different split faces/loose buttons)
next to the actual different effector types
e.g. transform effector (as it is)
time effector (..?) etc. Research it more.

another scripting ref:
http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Interface#A_popup_dialog

plans:
- Make checkboxes for fields to have effector affect (loc, rot, scale)
- Name the constraints consistent to effector name, e.g. effector.L.001 for easy removal
- add falloff types (and update-able in driver setting)
- custome driver equation field ('advanced' tweaking, changes drivers for all in that effector group)
- Empty vertex objects for location which AREN'T transformed, so that there is no limit to
how much the location can do (now limited to be between object and base bone)
- create list panel that shows effectors added, and with each selected can do things:
	- all more effector objects
	- select current objects (and rig)
	- change falloff/equation
	- remove selected from effector
	- remove effector (drivers & rig)
	- apply effector in position (removes rig)

Source code available on github:
https://github.com/TheDuckCow/Blender_Effectors

"""

########


bl_info = {
	"name": "Blender Effectors",
	"author": "Patrick W. Crawford",
	"version": (1, 0, 3),
	"blender": (2, 71, 0),
	"location": "3D window toolshelf",
	"category": "Object",
	"description": "Effector special motion graphics",
	"wiki_url": "https://github.com/TheDuckCow/Blender_Effectors"
	}


import bpy

## just in case
from bpy.props import *
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator
from os.path import dirname, join


""" needed? """
"""
class SceneButtonsPanel():
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "scene"

	@classmethod
	def poll(cls, context):
		rd = context.scene.render
		return context.scene and (rd.engine in cls.COMPAT_ENGINES)
"""

""" original """

def createEffectorRig(bones,loc=None):
	[bone_base,bone_control] = bones
	if (loc==None):
		loc = bpy.context.scene.cursor_location

	bpy.ops.object.armature_add(location=loc)
	rig = bpy.context.active_object
	rig.name = "effector"
	bpy.types.Object.one = bpy.props.FloatProperty(name="does this setting do anything at all?", description="one hundred million", default=1.000, min=0.000, max=1.000)
	rig.one = 0.6
	#bpy.ops.wm.properties_add(data_path="object")
	
	"""
	bpy.ops.object.mode_set(mode='EDIT')
	control = rig.data.edit_bones.new('control')
	#bpy.ops.armature.bone_primitive_add() #control
	# eventually add property as additional factor

	rig.data.bones[0].name = 'base'
	rig.data.bones[0].show_wire = True
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='EDIT')
	
	# SCENE REFRESH OR SOMETHING???
	rig.data.bones[1].name = 'control'
	control = obj.pose.bones[bones['base']]
	#rig.data.bones[1].parent = rig.data.[bones['base']] #need other path to bone data
	bpy.ops.object.mode_set(mode='OBJECT')
	rig.pose.bones[0].custom_shape = bone_base
	rig.pose.bones[1].custom_shape = bone_control

	# turn of inherent rotation for control??
	
	# property setup
	#bpy.ops.wm.properties_edit(data_path='object', property='Effector Scale',
	#   value='1.0', min=0, max=100, description='Falloff scale of effector')
	#scene property='Effector.001'
	
	
	
	"""
	
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='SELECT')
	bpy.ops.armature.delete()
	
	arm = rig.data
	bones = {}

	bone = arm.edit_bones.new('base')
	bone.head[:] = 0.0000, 0.0000, 0.0000
	bone.tail[:] = 0.0000, 0.0000, 1.0000
	bone.roll = 0.0000
	bone.use_connect = False
	bone.show_wire = True
	bones['base'] = bone.name
	
	bone = arm.edit_bones.new('control')
	bone.head[:] = 0.0000, 0.0000, 0.0000
	bone.tail[:] = 0.0000, 1.0000, 0.0000
	bone.roll = 0.0000
	bone.use_connect = False
	bone.parent = arm.edit_bones[bones['base']]
	bones['control'] = bone.name

	bpy.ops.object.mode_set(mode='OBJECT')
	pbone = rig.pose.bones[bones['base']]
	#pbone.rigify_type = ''
	pbone.lock_location = (False, False, False)
	pbone.lock_rotation = (False, False, False)
	pbone.lock_rotation_w = False
	pbone.lock_scale = (False, False, False)
	pbone.rotation_mode = 'QUATERNION'
	pbone.bone.layers = [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
	pbone = rig.pose.bones[bones['control']]
	#pbone.rigify_type = ''
	pbone.lock_location = (False, False, False)
	pbone.lock_rotation = (False, False, False)
	pbone.lock_rotation_w = False
	pbone.lock_scale = (False, False, False)
	pbone.rotation_mode = 'QUATERNION'
	#pbone.bone.layers = [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True]

	bpy.ops.object.mode_set(mode='EDIT')
	for bone in arm.edit_bones:
		bone.select = False
		bone.select_head = False
		bone.select_tail = False
	for b in bones:
		bone = arm.edit_bones[bones[b]]
		bone.select = True
		bone.select_head = True
		bone.select_tail = True
		arm.edit_bones.active = bone

	arm.layers = [(x in [0]) for x in range(32)]
	
	bpy.ops.object.mode_set(mode='OBJECT')
	rig.pose.bones[0].custom_shape = bone_base
	rig.pose.bones[1].custom_shape = bone_control
	
	return rig

def createBoneShapes():
	
	if (bpy.data.objects.get("effectorBone1") is None) or (bpy.data.objects.get("effectorBone2") is None):
		bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=8, enter_editmode=True)
		bpy.ops.mesh.delete(type='ONLY_FACE')
		bpy.ops.object.editmode_toggle()
		effectorBone1 = bpy.context.active_object
		effectorBone1.name = "effectorBone1"
		bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, enter_editmode=False, size=0.5)
		effectorBone2 = bpy.context.active_object
		effectorBone2.name = "effectorBone2"
	
		#move to last layer and hide
		[False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True]
		effectorBone1.hide = True
		effectorBone2.hide = True
		effectorBone1.hide_render = True
		effectorBone2.hide_render = True
	
	return [bpy.data.objects["effectorBone1"],bpy.data.objects["effectorBone2"]]

	
def addEffectorObj(objList, rig):
	# store previous selections/active etc
	prevActive = bpy.context.scene.objects.active
	
	#default expression, change later with different falloff etc
	default_expression = "1/(.000001+objDist)*scale"
	
	#empty list versus obj list?
	emptyList = []
	
	# explicit state set
	bpy.ops.object.mode_set(mode='OBJECT')
	
	# iterate over all objects passed in
	for obj in objList:
		if obj.type=="EMPTY": continue
		##############################################
		# Add the empty intermediate object/parent
		bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=obj.location)
		empty = bpy.context.active_object
		empty.name = "effr.empty"
		obj.select = True
		preParent = obj.parent
		bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
		bpy.context.object.empty_draw_size = 0.1
		if (preParent):
			bpy.ops.object.select_all(action='DESELECT')
			
			# need to keep transform!
			preParent.select = True
			empty.select = True
			bpy.context.scene.objects.active = preParent
			bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
			#empty.parent = preParent
			
		bpy.context.scene.objects.active = obj
		preConts = len(obj.constraints)  # starting number of constraints

		###############################################
		# LOCATION
		bpy.ops.object.constraint_add(type='COPY_LOCATION')
		obj.constraints[preConts].use_offset = True
		obj.constraints[preConts].target_space = 'LOCAL'
		obj.constraints[preConts].owner_space = 'LOCAL' 
		obj.constraints[preConts].target = rig
		obj.constraints[preConts].subtarget = "control"
		
		driverLoc = obj.constraints[preConts].driver_add("influence").driver
		driverLoc.type = 'SCRIPTED'
		
		# var for objDist two targets, 1st is "base" second is "distanceRef"
		varL_dist = driverLoc.variables.new()
		varL_dist.type = 'LOC_DIFF'
		varL_dist.name = "objDist"
		varL_dist.targets[0].id = rig
		varL_dist.targets[0].bone_target = 'base'
		varL_dist.targets[1].id = empty
		
		varL_scale = driverLoc.variables.new()
		varL_scale.type = 'TRANSFORMS'
		varL_scale.name = 'scale'
		varL_scale.targets[0].id = rig
		varL_scale.targets[0].transform_type = 'SCALE_Z'
		varL_scale.targets[0].bone_target = 'base'
		
		driverLoc.expression = default_expression

		
		###############################################
		# ROTATION
		bpy.ops.object.constraint_add(type='COPY_ROTATION')
		preConts+=1
		obj.constraints[preConts].target_space = 'LOCAL'
		obj.constraints[preConts].owner_space = 'LOCAL'
		obj.constraints[preConts].target = rig
		obj.constraints[preConts].subtarget = "control"

		driverRot = obj.constraints[preConts].driver_add("influence").driver
		driverRot.type = 'SCRIPTED'
		
		# var for objDist two targets, 1st is "base" second is "distanceRef"
		varR_dist = driverRot.variables.new()
		varR_dist.type = 'LOC_DIFF'
		varR_dist.name = "objDist"
		varR_dist.targets[0].id = rig
		varR_dist.targets[0].bone_target = 'base'
		varR_dist.targets[1].id = obj
		
		
		varR_scale = driverRot.variables.new()
		varR_scale.type = 'TRANSFORMS'
		varR_scale.name = 'scale'
		varR_scale.targets[0].id = rig
		varR_scale.targets[0].transform_type = 'SCALE_Z'
		varR_scale.targets[0].bone_target = 'base'
		
		driverRot.expression = default_expression
		
		###############################################
		# SCALE
		bpy.ops.object.constraint_add(type='COPY_SCALE')
		preConts+=1
		obj.constraints[preConts].target_space = 'LOCAL'
		obj.constraints[preConts].owner_space = 'LOCAL'
		obj.constraints[preConts].target = rig
		obj.constraints[preConts].subtarget = "control"
		
		driverScale = obj.constraints[preConts].driver_add("influence").driver
		driverScale.type = 'SCRIPTED'
		
		# var for objDist two targets, 1st is "base" second is "distanceRef"
		varS_dist = driverScale.variables.new()
		varS_dist.type = 'LOC_DIFF'
		varS_dist.name = "objDist"
		varS_dist.targets[0].id = rig
		varS_dist.targets[0].bone_target = 'base'
		varS_dist.targets[1].id = obj
		
		
		varS_scale = driverScale.variables.new()
		varS_scale.type = 'TRANSFORMS'
		varS_scale.name = 'scale'
		varS_scale.targets[0].id = rig
		varS_scale.targets[0].transform_type = 'SCALE_Z'
		varS_scale.targets[0].bone_target = 'base'

		driverScale.expression = default_expression
		

########################################################################################
#   Above for precursor functions
#   Below for the class functions
########################################################################################


class addEffector(bpy.types.Operator):
	"""Create the effector object and setup"""
	bl_idname = "object.add_effector"
	bl_label = "Add Effector"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		
		objList = bpy.context.selected_objects
		[effectorBone1,effectorBone2] = createBoneShapes()
		rig = createEffectorRig([effectorBone1,effectorBone2])
		addEffectorObj(objList, rig)
		bpy.context.scene.objects.active = rig

		return {'FINISHED'}

class updateEffector(bpy.types.Operator):
	bl_idname = "object.update_effector"
	bl_label = "Update Effector"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		
		print("Update Effector: NOT CREATED YET!")
		# use the popup window??

		return {'FINISHED'}

class selectEmpties(bpy.types.Operator):
	bl_idname = "object.select_empties"
	bl_label = "Select Effector Empties"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		
		print("Selecting effector empties: NOT COMPLETELY CORRECT YET!")
		# just selects all empties, lol.
		bpy.ops.object.select_by_type(type='EMPTY')

		return {'FINISHED'}


class separateFaces(bpy.types.Operator):
	"""Separate all faces into new meshes"""
	bl_idname = "object.separate_faces"
	bl_label = "Separate Faces to Objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		
		# make sure it's currently in object mode for sanity
		bpy.ops.object.mode_set(mode='OBJECT')
		
		for obj in bpy.context.selected_objects:
			bpy.context.scene.objects.active = obj
			if obj.type != "MESH": continue
			#set scale to 1
			try:
				bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
			except:
				print("couodn't transform")
			print("working?")
			#mark all edges sharp
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.mark_sharp()
			bpy.ops.object.mode_set(mode='OBJECT')
			#apply modifier to split faces
			bpy.ops.object.modifier_add(type='EDGE_SPLIT')
			obj.modifiers[-1].split_angle = 0
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier=obj.modifiers[-1].name)
			#clear sharp
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.mark_sharp(clear=True)
			bpy.ops.object.mode_set(mode='OBJECT')
			#separate to meshes
			bpy.ops.mesh.separate(type="LOOSE")
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
		
		return {'FINISHED'}


# SceneButtonsPanel
# ^^ above for attempt to make in scenes panel
class effectorPanel(bpy.types.Panel):
	"""Effector Tools"""
	
	bl_label = "Effector Tools"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Tools"
	"""
	
	bl_label = "Effector Tools"
	bl_space_type = 'VIEW_3D'#"PROPERTIES" #or 'VIEW_3D' ?
	bl_region_type = "WINDOW"
	bl_context = "scene"
	"""

	def draw(self, context):
		
		
		
		view = context.space_data
		scene = context.scene
		layout = self.layout

		split = layout.split()
		col = split.column(align=True)
		col.operator("object.separate_faces", text="Separate Faces")
		split = layout.split()		# uncomment to make vertical
		#col = split.column(align=True) # uncomment to make horizontal
		col.operator("object.add_effector", text="Add Effector")
		split = layout.split()
		col.operator("wm.mouse_position", text="Update Effector alt")
		col.operator("object.select_empties", text="Select Empties")
		
		split = layout.split()
		col = split.column(align=True)
		#col = layout.column()
		layout.label("Disable Recommended:")
		col.prop(view, "show_relationship_lines")
		
		
		# shameless copy from vertex group pa
		
		# funcitons to implement:
		
		# add new (change from current, where it creates just the armature
		# and later need to assign objects to it
		# need to figure out data structure for it! I think properties
		# for each of the objects, either unique per group or over+1 unique per group
		
		# Assign
		# Remove
		
		# Select
		# Deselect
		
		# select Effector Control
		
		"""
		ob = context.object
		group = ob.vertex_groups.active

		rows = 1
		if group:
			rows = 3

		row = layout.row()
		row.template_list("MESH_UL_vgroups", "", ob, "vertex_groups", ob.vertex_groups, "active_index", rows=rows)

		col = row.column(align=True)
		col.operator("object.vertex_group_add", icon='ZOOMIN', text="")
		col.operator("object.vertex_group_remove", icon='ZOOMOUT', text="").all = False
		
		
		if ob.vertex_groups and (ob.mode == 'OBJECT'):
			row = layout.row()

			sub = row.row(align=True)
			sub.operator("object.vertex_group_assign", text="Assign")
			sub.operator("object.vertex_group_remove_from", text="Remove")
			
			row = layout.row()
			sub = row.row(align=True)
			sub.operator("object.vertex_group_select", text="Select")
			sub.operator("object.vertex_group_deselect", text="Deselect")
		"""
		

########################################################################################
#   Above for the class functions
#   Below for extra classes/registration stuff
########################################################################################


#### WIP popup

class WIPpopup(bpy.types.Operator):
	bl_idname = "error.message"
	bl_label = "WIP popup"
	
	
	type = StringProperty()
	message = StringProperty()
	
	def execute(self, context):
		self.report({'INFO'}, self.message)
		print(self.message)
		return {'FINISHED'}
 
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_popup(self, width=350, height=40)
		return self.execute(context)
	
	def draw(self, context):
		self.layout.label("This addon is a work in progress, feature not yet implemented")
		row = self.layout.split(0.80)
		row.label("") 
		row.operator("error.ok")


# shows in header when run
class notificationWIP(bpy.types.Operator):
	bl_idname = "wm.mouse_position"
	bl_label = "Mouse location"
 
	def execute(self, context):
		# rather then printing, use the report function,
		# this way the message appears in the header,
		self.report({'INFO'}, "Not Implemented")
		return {'FINISHED'}
		
	def invoke(self, context, event):
		return self.execute(context)


# WIP OK button general purpose
class OkOperator(bpy.types.Operator):
	bl_idname = "error.ok"
	bl_label = "OK"
	def execute(self, context):
		#eventually another one for url lib
		return {'FINISHED'}



# This allows you to right click on a button and link to the manual
# auto-generated code, not fully changed
def add_object_manual_map():
	url_manual_prefix = "https://github.com/TheDuckCow"
	url_manual_mapping = (
		("bpy.ops.mesh.add_object", "Modeling/Objects"),
		)
	return url_manual_prefix, url_manual_mapping


def register():
	bpy.utils.register_class(addEffector)
	bpy.utils.register_class(updateEffector)
	bpy.utils.register_class(effectorPanel)
	bpy.utils.register_class(separateFaces)
	bpy.utils.register_class(selectEmpties)
	
	bpy.utils.register_class(WIPpopup)
	bpy.utils.register_class(notificationWIP)
	bpy.utils.register_class(OkOperator)
	#bpy.utils.register_manual_map(add_object_manual_map)


def unregister():
	bpy.utils.unregister_class(addEffector)
	bpy.utils.unregister_class(updateEffector)
	bpy.utils.unregister_class(effectorPanel)
	bpy.utils.unregister_class(separateFaces)
	bpy.utils.unregister_class(selectEmpties)
	
	bpy.utils.unregister_class(WIPpopup)
	bpy.utils.unregister_class(notificationWIP)
	bpy.utils.unregister_class(OkOperator)
	#bpy.utils.unregister_manual_map(add_object_manual_map)


if __name__ == "__main__":
	register()

