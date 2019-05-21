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


bl_info = {
	"name": "Keying Tools",
	"category": "Cenda Tools",
	"author": "Cenek Strichel",
	"version": (1, 0, 0),
	"blender": (2, 79, 0),
	"description": "Tools for Keying",
	"location": "Timeline header, View3D header, Dopesheet (only selected mode) header",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
}

import bpy
from bpy.types import Header
from bpy.props import StringProperty, IntProperty, BoolProperty

global current_icon



############################ GUI ####################################
class TIMELINE_HT_header(Header):
	
	bl_space_type = 'TIMELINE'
#	bl_region_type = 'UI'

#	@classmethod
#	def poll(cls, context):
#		return (context.object is not None)

	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')


	def draw(self, context):

		state = bpy.context.user_preferences.edit.use_keyframe_insert_needed

		if (state) :
			current_icon = 'CHECKBOX_HLT'
		else:
			current_icon = 'CHECKBOX_DEHLT'
			
		layout = self.layout
		row = layout.row()

		# only for pose mode
		if (context.active_object != None and context.mode == 'POSE') :
			
			row = layout.row(align=True)
			layout.separator()
			row.operator( "pose.key_all_unlocked" , icon = "KEY_HLT", text = "Selected")
			row.operator( "pose.key_whole_character" , icon = "KEY_HLT", text = "Whole Character")
			
		row = layout.row(align=True)
		row.operator( "scene.only_insert_needed" , icon = current_icon)	
		
		
################################################################		
class OnlyInsertNeeded(bpy.types.Operator):

	bl_label = "Only Insert Needed"
	bl_idname = "scene.only_insert_needed"

	def execute(self, context):
		prefs = bpy.context.user_preferences.edit
		prefs.use_keyframe_insert_needed = not prefs.use_keyframe_insert_needed

		return{'FINISHED'}
	
	
class QuaternionToXYZ(bpy.types.Operator):

	bl_label = "Quaternion to XYZ"
	bl_idname = "scene.quaternion_to_xyz"

	def execute(self, context):
		for bone in bpy.context.selected_pose_bones:
			if(bone.rotation_mode == "QUATERNION"):
				bone.rotation_mode = "XYZ"

		return{'FINISHED'}
		
		
class KeyWholeCharacter(bpy.types.Operator):
	
	'''Key Whole Character'''
	bl_idname = "pose.key_whole_character"
	bl_label = "Key Whole Character"
	bl_options = {'REGISTER', 'UNDO'}
			
	def execute(self, context):

		# only for pose mode
		obj = context.active_object
		if obj and obj.mode == 'POSE':
			
			DeselectAllKeyframes()
			
			# insert needed
			prefs = bpy.context.user_preferences.edit
			currentSetting = prefs.use_keyframe_insert_needed
			prefs.use_keyframe_insert_needed = False

			# key character set
			bpy.ops.anim.keying_set_active_set(type='WholeCharacter')
			bpy.ops.anim.keyframe_insert_menu(type='__ACTIVE__', confirm_success=True)
			bpy.ops.anim.keying_set_active_set() # zruseni keying setu
			
			# set keyframe to extreme
			area = bpy.context.area
			old_type = area.type
			area.type = 'DOPESHEET_EDITOR'
			
			# I need set all keys to extreme
			onlySelectSetting = context.space_data.dopesheet.show_only_selected
			context.space_data.dopesheet.show_only_selected = False

			bpy.ops.action.keyframe_type(type='EXTREME')
			
			context.space_data.dopesheet.show_only_selected = onlySelectSetting

			area.type = old_type
			

			# return setting back
			prefs.use_keyframe_insert_needed = currentSetting
			self.report({'INFO'},"Keying Whole Character")
			
		return {'FINISHED'}


class KeyAllUnlocked(bpy.types.Operator):

	'''Key All Unlocked'''
	bl_idname = "pose.key_all_unlocked"
	bl_label = "Key All Unlocked"
	bl_options = {'REGISTER', 'UNDO'}
	
#	@classmethod
#	def poll(cls, context):
#		return context.area.type == 'VIEW_3D'
		
	def execute(self, context):
		
		# delete locked
		ob = bpy.context.active_object
		
		if ob and ob.mode == 'POSE':
			
			# insert needed
			prefs = bpy.context.user_preferences.edit
			currentSetting = prefs.use_keyframe_insert_needed
			prefs.use_keyframe_insert_needed = False

			# keying
			
			# key for all
			bpy.ops.anim.keyframe_insert(type='LocRotScale')

			# delete locked
			for bone in bpy.context.selected_pose_bones:
				
				# location
				for i in range(3):
					if(bone.lock_location[i]):
						bone.keyframe_delete(data_path="location", index=i)
				
				# quaternion
				if bone.rotation_mode == 'QUATERNION' :
					
					if(bone.lock_rotation_w):
						bone.keyframe_delete(data_path="rotation_quaternion", index = 0 )
							
					for i in range(3):
						if(bone.lock_rotation[i]):
							bone.keyframe_delete(data_path="rotation_quaternion", index=(i+1))
							
				# euler			
				else :	
					
					for i in range(3):
						if(bone.lock_rotation[i]):
							bone.keyframe_delete(data_path="rotation_euler", index=i)
	
				# scale
				for i in range(3):
					if(bone.lock_scale[i]):
						bone.keyframe_delete(data_path="scale", index=i)
				
			# return setting back
			prefs.use_keyframe_insert_needed = currentSetting
			
			self.report({'INFO'},"Keying All Selected")
			
		return {'FINISHED'}
	


################################################################	
class VIEW3DKeyingButtons(Header):
	
	bl_space_type = 'VIEW_3D'
	
#	@classmethod
#	def poll(cls, context):
#		return (context.active_object != None and context.mode == 'POSE')

	def draw(self, context):
		
		layout = self.layout
		col = layout.column()
		col = layout.column()
		row = col.row(align = True)

		if (context.active_object != None and context.mode == 'POSE') :
			# Auto IK
			if(context.object.data.use_auto_ik):
				ikonka = "CHECKBOX_HLT"
			else:
				ikonka = "CHECKBOX_DEHLT"	
			row.operator( "pose.auto_ik_switch" , icon = ikonka )
			
			# Flip animation
			row.operator( "pose.pose_flipped" , icon = "PASTEFLIPUP", text = "")
			
################
# POSE FLIPPED #
################

# copy and flip pose in one step
class PoseFlipped(bpy.types.Operator):

	'''Copy and Paste Flipped'''
	bl_idname = "pose.pose_flipped"
	bl_label = "Pose Flipped"
	bl_options = {'REGISTER', 'UNDO'}

	
	def execute(self, context):
	
		bpy.ops.pose.copy()
		bpy.ops.pose.paste(flipped=True)
		
		return {'FINISHED'}

class AutoIK(bpy.types.Operator):

	'''Auto IK switch'''
	bl_idname = "pose.auto_ik_switch"
	bl_label = "Auto IK"
	bl_options = {'REGISTER', 'UNDO'}

	
	def execute(self, context):
		context.object.data.use_auto_ik = not context.object.data.use_auto_ik
		
		# redraw 
		for area in bpy.context.screen.areas:
			if area.type == 'VIEW_3D':
				area.tag_redraw()
				
		return {'FINISHED'}


################################################################	
class DOPESHEETKeyingButtons(Header):
	
	bl_space_type = 'DOPESHEET_EDITOR'
	
	
	bpy.types.Scene.SelectGroup = BoolProperty(
	name = "Group",
	default = True,
	description = "Offset whole group")
	
	
	bpy.types.Scene.AutoKeyOffset = BoolProperty(
	name = "Auto",
	default = True,
	description = "Offset is taken by Frame Range")
	
	
	bpy.types.Scene.KeyOffset = IntProperty(
	name = "",
	default = 0,
	soft_min = 0,
	soft_max = 100,
	description = "Offset key is setted by user")
	

	def draw(self, context):
		
		layout = self.layout
		row = layout.row(align = True)
		scn = context.scene
		
		if( context.space_data.dopesheet.show_only_selected ):
			
			row.label( icon = "POSE_DATA", text = "Mirror" )
			
			# select group
			row.prop( scn, "SelectGroup" )
			
			# toggle
			row.prop( scn, "AutoKeyOffset" )
			
			# set value for offset
			if(not scn.AutoKeyOffset):
				row.prop( scn, "KeyOffset" )
				
			# offset!
			row.operator( "action.locomotion" , text = "Offset")

		# Mirror
		col = layout.column()
		row = col.row(align = True)
		row.operator( "action.animation_mirror" , icon = "MOD_MIRROR")	
		
		
			
################
# POSE ANIMATION FLIPPED #
################

# copy and flip pose in one step
class Locomotion(bpy.types.Operator):


	'''Copy and Paste mirror animation (All visible keyframes)'''
	bl_idname = "action.locomotion"
	bl_label = "Locomotion"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		
		obj = context.object
		scn = context.scene
	
		if(obj.animation_data != None and obj.animation_data.action != None):
			
			# select whole group for mirror offset
			if(scn.SelectGroup):
				bpy.ops.pose.select_grouped(type='GROUP')
			
			SelectAllKeyframes()
			
			bpy.ops.action.extrapolation_type(type='MAKE_CYCLIC') # cycle for original frames

			# copy
			bpy.ops.action.copy()
			bpy.ops.pose.select_mirror(extend=False) # select flipped
			bpy.ops.pose.key_all_unlocked() # i need some key
			
			# paste
			bpy.ops.action.paste(merge='OVER_ALL', flipped=True, offset='NONE' )
			bpy.ops.action.extrapolation_type(type='MAKE_CYCLIC')
	
			# keyframe are offseted
			if(scn.AutoKeyOffset):
			
				# move keyframes # I can not detect last frame, because last frame doesn`t mean end of cycle
				if( bpy.context.scene.use_preview_range ) :
					frameOffset = bpy.context.scene.frame_preview_end / 2
				else :
					frameOffset = bpy.context.scene.frame_end / 2
					
			else:
				frameOffset = scn.KeyOffset
		
			# offset move	
			bpy.ops.transform.transform(
			mode='TIME_TRANSLATE', 
			value=(frameOffset, 0, 0, 0), 
			axis=(0, 0, 0), 
			constraint_axis=(False, False, False), 
			constraint_orientation='GLOBAL')

	        # select previous objects
			bpy.ops.pose.select_mirror(extend=False) # select flipped

			# deselecting frame
			bpy.ops.action.select_all_toggle(invert=False)
		
		return {'FINISHED'}



# copy and flip pose in one step
class MirrorAnimation(bpy.types.Operator):

	'''Flipping whole animation by X (All visible keyframes)'''
	bl_idname = "action.animation_mirror"
	bl_label = "Mirror Action"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		
		SelectAllKeyframes()
	
		# copy
		bpy.ops.action.copy()
		
		# paste overwrite
		bpy.ops.action.paste(offset='NONE', merge='OVER_ALL', flipped=True)
		
		# deselecting frame
		bpy.ops.action.select_all_toggle(invert=False)
		
		return {'FINISHED'}
	

def SelectAllKeyframes():
	bpy.ops.action.select_leftright(mode='LEFT', extend=False)	
	bpy.ops.action.select_leftright(mode='RIGHT', extend=True)
	bpy.ops.action.select_more() # if current time is on the frame


def DeselectAllKeyframes():

	obj = bpy.context.object
	
	if(obj.animation_data != None and obj.animation_data.action != None):

		# switch to DE
		area = bpy.context.area
		old_type = area.type
		area.type = 'DOPESHEET_EDITOR'

		SelectAllKeyframes()
		
		bpy.ops.action.select_all_toggle(invert=False)

		# set back
		area.type = old_type
			

# auto blend on / off
class NLAAutoBlend(bpy.types.Operator):

	'''Auto blend toggle'''
	bl_idname = "nla.auto_blend_toggle"
	bl_label = "NLA Auto Blend"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
	
		try:
			selected_strips = [strip for strip in bpy.context.object.animation_data.nla_tracks.active.strips if strip.select]		
		except AttributeError:
			selected_strips = []
			
		selected_strips.use_auto_blend = not selected_strips.use_auto_blend
		
		return {'FINISHED'}


# ANIMATION EDITORs ###########################################################################################
'''
class AnimKeyingMenu( bpy.types.Menu ):

	bl_label = "Insert Keyframes"
	bl_idname = "ANIM_MT_insert_keyframes"

	def draw(self, context):
		layout = self.layout
		layout.operator("anim.keyframe_insert_needed", text = "All Channels").allChannels = True
		layout.operator("anim.keyframe_insert_needed", text = "Only Selected Channels").allChannels = False


class AnimKeyInsertNeeded( bpy.types.Operator ):
'''
#	'''Insert Keyframes Needed'''
'''
	bl_idname = "anim.keyframe_insert_needed"
	bl_label = "Key All Unlocked"
	bl_options = {'REGISTER', 'UNDO'}
	
	allChannels = BoolProperty(name="All Channels",default=True)
	
	def execute(self, context):

		# insert needed
		prefs = bpy.context.user_preferences.edit
		currentSetting = prefs.use_keyframe_insert_needed
		prefs.use_keyframe_insert_needed = False

		# keying type
		channelsType = 'SEL'
		if(self.allChannels):
			channelsType = 'ALL'
		
		#key
		if( context.area.type == 'GRAPH_EDITOR' ):
			bpy.ops.graph.keyframe_insert( type = channelsType )
		else:		
			bpy.ops.action.keyframe_insert( type = channelsType )

		# return setting back
		prefs.use_keyframe_insert_needed = currentSetting
	
		return {'FINISHED'}
'''		
		
# VIEWPORT ###########################################################################################
class AnimKeyingMenuViewport( bpy.types.Menu ):

	bl_label = "Insert Keyframe Menu"
	bl_idname = "ANIM_MT_insert_keyframes_menu"

	def draw(self, context):
		
		if(bpy.context.object.type != "ARMATURE"):
			
			layout = self.layout
			op = layout.operator("anim.keyframe_insert_menu_needed", icon = "MAN_TRANS", text = "Location")
			op.location = True
			op.rotation = False
			op.scale = False
			
			op = layout.operator("anim.keyframe_insert_menu_needed", icon = "MAN_ROT", text = "Rotation")
			op.location = False
			op.rotation = True
			op.scale = False
			
			op = layout.operator("anim.keyframe_insert_menu_needed", icon = "MAN_SCALE", text = "Scale")
			op.location = False
			op.rotation = False
			op.scale = True
			
		else:
			layout = self.layout
			layout.operator( "pose.key_all_unlocked" , icon = "KEY_HLT", text = "Selected")
			layout.operator( "pose.key_whole_character" , icon = "KEY_HLT", text = "Whole Character")


class AnimKeyInsertMenuNeededViewport( bpy.types.Operator ):

	'''Insert Keyframes Menu Needed'''
	bl_idname = "anim.keyframe_insert_menu_needed"
	bl_label = "Key All Unlocked"
	bl_options = {'REGISTER', 'UNDO'}
	
	location = BoolProperty(name="Location", default=False)
	rotation = BoolProperty(name="Rotation", default=False)
	scale = BoolProperty(name="Scale", default=False)
	
	def execute(self, context):

		if(bpy.context.object.type != "ARMATURE"):
			
			# insert needed
			prefs = bpy.context.user_preferences.edit
			currentSetting = prefs.use_keyframe_insert_needed
			prefs.use_keyframe_insert_needed = False

			# keying type
			if(self.location):

				bpy.ops.anim.keyframe_insert_menu(type='Location')
				
				for i in range (0,3):
					if(bpy.context.object.lock_location[i]):
						bpy.context.object.keyframe_delete(data_path="location", index=i)

							
			elif(self.rotation):

				bpy.ops.anim.keyframe_insert_menu(type='Rotation')
				
				for ir in range (0,3):
					if(bpy.context.object.lock_rotation[ir]):
						bpy.context.object.keyframe_delete(data_path="rotation_euler", index=ir)
						
			elif(self.scale):

				bpy.ops.anim.keyframe_insert_menu(type='Scaling')
				
				for iscale in range (0,3):
					if(bpy.context.object.lock_scale[iscale]):
						bpy.context.object.keyframe_delete(data_path="scale", index=iscale)

			# return setting back
			prefs.use_keyframe_insert_needed = currentSetting
	
		else:
			
			self.report({'ERROR'}, "Armature is not supported!")
			
		return {'FINISHED'}
	
			
############################################################################################
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()