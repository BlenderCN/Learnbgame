# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
	"name": "Tools",
	"author": "Cenek Strichel",
	"version": (1, 0, 6),
	"blender": (2, 79, 0),
	"location": "Many commands",
	"description": "Many tools",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import Header, Panel


# auto preview range for timeline and current keyframes
class TimeAutoPreviewRangeSet(bpy.types.Operator):

	bl_idname = "time.autopreviewrange_set"
	bl_label = "Auto-Set Preview Range"

	def execute(self, context):
		
		savedframe = bpy.context.scene.frame_current

		TimelineAutoSetPreview( False )
		TimelineAutoSetPreview( True )
		TimelineAutoSetPreview( False ) # HACK

		bpy.context.scene.frame_current = savedframe

		return {'FINISHED'}
	
	
def TimelineAutoSetPreview( nextFrame ):

	counter = 10

	while(True):

		bpy.ops.screen.keyframe_jump( next = nextFrame )
		
		counter = counter - 1
				
		if(counter <= 0):
			
			bpy.context.scene.use_preview_range = True
		
			if(nextFrame):
				bpy.context.scene.frame_preview_end = bpy.context.scene.frame_current
			else:	
				bpy.context.scene.frame_preview_start = bpy.context.scene.frame_current
			
			break
			
			
############################ GUI ####################################	
# replace for classic camera view (NUM 0)		
class ShowCameraView(bpy.types.Operator):

	bl_idname = "screen.show_camera_view"
	bl_label = "Show Camera View"

	def execute(self, context):
		
		space = bpy.context.space_data
		
		if( bpy.context.scene.camera == None ):
			self.report({'ERROR'}, ("Set camera in Scene Settings!") )
			return {'FINISHED'}

		space.lock_camera_and_layers = False # desync
		space.camera = None # reset camera
		bpy.ops.view3d.viewnumpad(type = "CAMERA")
		
		# Normal view
		if(space.region_3d.view_perspective == 'CAMERA'):
			space.show_only_render = False
			space.show_manipulator = True
		#	space.fx_settings.use_ssao  = False
			context.scene.camera.data.passepartout_alpha = 1

		# CAMERA VIEW
		else:
			space.show_only_render = True
			space.show_manipulator = False
		#	space.fx_settings.use_ssao  = True
		

		return {'FINISHED'}
	
	
################################################################
# play animation and stop with restore time position for easy animation play
class AnimationPlayRestore(bpy.types.Operator):

	bl_idname = "screen.animation_play_restore"
	bl_label = "Play Animation Restore"
	
	onlyRender = BoolProperty(name="Only Render",default=False)
	
	def execute(self, context):
		
		# HACK - blender is switching this to false, but dont know why
		bpy.context.scene.show_keys_from_selected_only = True

		# playing
		isplaying = bpy.context.screen.is_animation_playing
		
		# stop / play					
		if( isplaying ):
			bpy.ops.screen.animation_cancel(restore_frame=True)
		else:
			bpy.ops.screen.animation_play()	
		
		# areas #
		for area in bpy.context.screen.areas: # iterate through areas in current screen
			if area.type == 'VIEW_3D':
				for space in area.spaces: # iterate through spaces in current VIEW_3D area
					if space.type == 'VIEW_3D': # check if space is a 3D view
						
						if(space.region_3d.view_perspective == 'CAMERA'):
							break # I dont want to change view with camera
						
						# Previs Play
						if self.onlyRender :
							space.show_only_render = not isplaying
							space.show_manipulator = isplaying
							space.fx_settings.use_ssao = not isplaying
							
						# Normal Play
						else :
							space.show_only_render = False
							space.show_manipulator = isplaying
							space.fx_settings.use_ssao = False

		return {'FINISHED'}
	
	
# stop or rewind animation play	
class AnimationStopRewind(bpy.types.Operator):

	bl_idname = "screen.animation_stop_rewind"
	bl_label = "Stop / Rewind Animation"
	
	
	def execute(self, context):

		# playing
		isplaying = bpy.context.screen.is_animation_playing
		
		# stop / play					
		if( isplaying ):
			bpy.ops.screen.animation_cancel(restore_frame=False)
		else:
			bpy.ops.screen.frame_jump()
	
		return {'FINISHED'}
	
	
# Hotkey for Outliner	
class HideObjects(bpy.types.Operator):
	
	bl_idname = "object.hide_view_and_render"
	bl_label = "Hide View and Render"
	
	def execute(self, context):

		bpy.ops.object.hide_view_set()
		bpy.ops.object.hide_render_set()

				
		return {'FINISHED'}
			
	
############		
# CHANNELS #
############		
class SelectAndFrame(bpy.types.Operator):
	
	bl_idname = "graph.channels_select_and_frame"
	bl_label = "Select and Frame"
	
	extend = BoolProperty(name="Extend", default=False)

#	@classmethod
#	def poll(cls, context):
#		return context.area.type == 'GRAPH_EDITOR'

	def execute(self, context):
		
		# Graph Editor
		if( context.area.type == 'GRAPH_EDITOR' ):
			
			bpy.ops.anim.channels_click('INVOKE_DEFAULT', extend = self.extend)
			bpy.ops.anim.channel_select_keys('INVOKE_DEFAULT', extend = self.extend)
		
			bpy.ops.graph.view_selected('EXEC_REGION_WIN')

			'''
			bpy.ops.screen.region_flip('EXEC_REGION_CHANNELS')		
			bpy.ops.view2d.zoom_out('EXEC_REGION_WIN', zoomfacx = -0.05, zoomfacy = -0.05)
			bpy.ops.screen.region_flip('EXEC_REGION_CHANNELS')
			'''
	#		
	#		bpy.ops.graph.select_all_toggle()
			bpy.ops.anim.channels_expand(all=False)
			
			
			
		# Dope & NLA
		else:

			bpy.ops.anim.channels_click('INVOKE_DEFAULT', extend = self.extend)
			bpy.ops.anim.channels_expand(all=False)
				
		return {'FINISHED'}


# collapse all channels in animation editor		
class ResetExpand(bpy.types.Operator):
	
	bl_idname = "anim.reset_expand"
	bl_label = "Reset Expand"

	def execute(self, context):
		
			
		if( context.area.type == 'GRAPH_EDITOR' ):
			
			bpy.ops.anim.channels_collapse(all=True)
			bpy.ops.anim.channels_expand(all=True)
			bpy.ops.anim.channels_expand(all=True)

		else:

			space_data = bpy.context.space_data
			
			if space_data.type == 'DOPESHEET_EDITOR': # check if space is a 3D view
			
				bpy.ops.anim.channels_collapse(all=True)
				
				# Action editor is not using this
				if (bpy.context.space_data.mode == 'DOPESHEET') :
					bpy.ops.anim.channels_expand(all=True)
					bpy.ops.anim.channels_expand(all=True)
					
				# if summary is on, you need one expand more
				if space_data.dopesheet.show_summary :
					bpy.ops.anim.channels_expand(all=True)
				
		return {'FINISHED'}
	
	
################		
# GRAPH EDITOR #
################
# Double G	
class FrameCurve(bpy.types.Operator):
	
	bl_idname = "graph.frame_curve"
	bl_label = "Frame Curve"

	@classmethod
	def poll(cls, context):
		return context.area.type == 'GRAPH_EDITOR'

	def execute(self, context):
		bpy.ops.graph.select_linked()
		bpy.ops.graph.view_selected()
	#	bpy.ops.view2d.zoom_out(zoomfacx=-0.5, zoomfacy=-0.5)
		
		return {'FINISHED'}	


# Shrink and Grow selected face mask
class WeightMaskSelect(bpy.types.Operator):
	
	bl_idname = "paint.weight_mask_select"
	bl_label = "Weight Mask Select"
	
	SelectTypeEnum = [
		("More", "More", "", "", 0),
	    ("Less", "Less", "", "", 100),
	    ]
	
	selectType = EnumProperty( name = "Select Type", description = "", items=SelectTypeEnum )
	
#	@classmethod
#	def poll(cls, context):
#		return context.area.type == 'GRAPH_EDITOR'

	def execute(self, context):
		
		bpy.ops.object.editmode_toggle()
		
		if(self.selectType == 'More'):
			bpy.ops.mesh.select_more()
			
		elif(self.selectType == 'Less'):
			bpy.ops.mesh.select_less()
			
		bpy.ops.object.editmode_toggle()
		bpy.ops.paint.weight_paint_toggle()
		
		return {'FINISHED'}	
	

# MATERIAL / SOLID / TEXTURE
class DisplaySwitcher(bpy.types.Operator):
	
	bl_idname = "view3d.display_switcher"
	bl_label = "Display Switcher"

	forward = BoolProperty(name="Forward Cycling",default=False)
	
	def execute(self, context):
		
		if(self.forward) :

			if bpy.context.space_data.viewport_shade == 'WIREFRAME' :
				bpy.context.space_data.viewport_shade = 'SOLID'
				
			elif bpy.context.space_data.viewport_shade == 'SOLID' :
				bpy.context.space_data.viewport_shade = 'TEXTURED'
				
			elif bpy.context.space_data.viewport_shade == 'TEXTURED' :
				bpy.context.space_data.viewport_shade = 'MATERIAL'
	
		else :

			if bpy.context.space_data.viewport_shade == 'MATERIAL' :
				bpy.context.space_data.viewport_shade = 'TEXTURED'
				
			elif bpy.context.space_data.viewport_shade == 'TEXTURED' :
				bpy.context.space_data.viewport_shade = 'SOLID'
				
			elif bpy.context.space_data.viewport_shade == 'SOLID' :
				bpy.context.space_data.viewport_shade = 'WIREFRAME'
						
		return {'FINISHED'}	
	
	
# Show / hide manipulator (Translate/Rotate) vs Hide
class ManipulatorSwitcher(bpy.types.Operator):
	
	bl_idname = "view3d.manipulator_switcher"
	bl_label = "Manipulator Switcher"

	def execute(self, context):
			
		if( bpy.context.space_data.show_manipulator and (bpy.context.space_data.transform_manipulators == {'TRANSLATE', 'ROTATE'} ) ) :
			bpy.context.space_data.show_manipulator = False
		else :
			bpy.context.space_data.show_manipulator = True
			bpy.context.space_data.transform_manipulators = {'TRANSLATE', 'ROTATE'}
		
		return {'FINISHED'}

'''
class OrientationSwitcher(bpy.types.Operator):
	
	bl_idname = "view3d.orientation_switcher"
	bl_label = "Orientation Switcher"

	def execute(self, context):
		
		manipulators = bpy.context.space_data.transform_manipulators
		rotate = False
		orientation = bpy.context.space_data.transform_orientation
		
		for m in manipulators :
			if(m == 'ROTATE') :
				rotate = True
		
		locked = True # there must be one unlocked			
		ob = bpy.context.active_object
		
		# only for POSE mode
		if ob and ob.mode == 'POSE' :
			for bone in bpy.context.selected_pose_bones :
				# Quaternion
				if bone.rotation_mode == 'QUATERNION' :			
					if(not bone.lock_rotation_w):
						locked = False
		
				# Euler	+ Quaternion rest				
				for i in range(3):
					if(not bone.lock_rotation[i]):
						locked = False
	#	else :
	#		locked = False	
		
		# switching manipulators
		# with GIMBAL		
		if(rotate and not locked) :
			
			if orientation == "LOCAL" :
				orientation = "GLOBAL"
				
			elif orientation == "GLOBAL" :
				orientation = "GIMBAL"
				
			elif orientation == "GIMBAL" :
				orientation = "LOCAL"
		
		# LOCAL / GLOBAL	
		else :
			print('neni')
			if orientation == "LOCAL" :
				orientation = "GLOBAL"
			else :
				orientation = "LOCAL"
		
		bpy.context.space_data.transform_orientation = orientation
		
		return {'FINISHED'}
'''	

# my isolate version - not working well, don`t use it
'''
class IsolateObject(bpy.types.Operator):
	
	bl_idname = "view3d.isolate_object"
	bl_label = "Isolate Object"

	def execute(self, context):
		
		obj = bpy.context.selected_objects
		if(len(obj) > 0):
			
			bpy.ops.view3d.localview()
			
			if(bpy.context.object.type == 'MESH'):
				bpy.ops.object.select_all(action='TOGGLE')
			
			for o in obj :
				o.select = True

		else:
			bpy.ops.view3d.localview()	
				 
		return {'FINISHED'}
'''	
	
# Join object UV to one UV even it has different names	
class JoinObjectsWithUV(bpy.types.Operator):
	
	bl_idname = "object.join_with_uv"
	bl_label = "Join with UV"
	bl_options = {'REGISTER', 'UNDO'}
	
	uvmerge = BoolProperty(name="UV Merge",default=True)
	
	def execute(self, context):
		
		if(self.uvmerge):
			
			newName = "UVMap"
			
			# rename UV for merge
			if(len(bpy.context.object.data.uv_textures) > 0):
				newName = bpy.context.object.data.uv_textures[0].name
			
			# all objects UV rename
			for obj in bpy.context.selected_objects:
				if(len(obj.data.uv_textures) > 0):
					obj.data.uv_textures[0].name = newName

		# join
		bpy.ops.object.join()	
						 
		return {'FINISHED'}
		

	

## TEXT EDITOR ###############
class TextToolsButtons(Header):
	
	bl_space_type = 'TEXT_EDITOR'

	def draw(self, context):
		
		currentIcon = ""
		
		if( bpy.app.debug_wm ):
			currentIcon = "CHECKBOX_HLT"
		else:
			currentIcon = "CHECKBOX_DEHLT"

		layout = self.layout
		row = layout.row()
		row = layout.row(align=True)
		row.operator( "text.show_all_op" , icon = currentIcon)	

				
class ShowAllOp(bpy.types.Operator):

	'''Show all commands in Info output'''
	bl_idname = "text.show_all_op"
	bl_label = "Show All Operators"
#	bl_options = {'REGISTER', 'UNDO'}

	
	def execute(self, context):
		bpy.app.debug_wm = not bpy.app.debug_wm
		return {'FINISHED'}	


def FrameForEditor( currentArea, testedArea ):
	
	if currentArea.type == testedArea:
		for region in currentArea.regions:
			if region.type == 'WINDOW':
				ctx = bpy.context.copy()
				ctx[ 'area'] = currentArea
				ctx['region'] = region
				
				if(testedArea == 'TIMELINE'):
					bpy.ops.time.view_all(ctx)
					
				elif(testedArea == 'DOPESHEET_EDITOR'):
					bpy.ops.action.view_all(ctx)
					
				elif(testedArea == 'GRAPH_EDITOR'):
					bpy.ops.graph.view_all(ctx)
						
				break
			
			
###########################################################
class SetInOutRange(bpy.types.Operator):

	'''Set In and Out Range'''
	bl_idname = "time.range_in_out"
	bl_label = "Set In and Out Range"
	bl_options = {'REGISTER', 'UNDO'}
	
	
	options = [
	("StartRange", "Start Range", "", "", 0),
    ("EndRange", "End Range", "", "", 1)
    ]

	range = EnumProperty( name = "Range", description = "", items = options )
	
	
	def execute(self, context):

		bpy.context.scene.use_preview_range = True

		if(self.range == 'StartRange'):
			bpy.context.scene.frame_preview_start = bpy.context.scene.frame_current

		else:
			bpy.context.scene.frame_preview_end = bpy.context.scene.frame_current

		return {'FINISHED'}	
		

## SHOW MATERIAL SETTINGS in Properties and Node Editor #	
class ShowMaterial(bpy.types.Operator):

	'''Show Material'''
	bl_idname = "scene.show_material"
	bl_label = "Show Material"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		
		obj = bpy.context.active_object

		#
		if(obj.type == "MESH"):
			
			for area in bpy.context.screen.areas: # iterate through areas in current screen
				
				# Set Properties
				if area.type == 'PROPERTIES':
					for space in area.spaces: # iterate through all founded panels
						if space.type == 'PROPERTIES':	
							space.context = 'MATERIAL'
							
				# Set Node editor
				if area.type == 'NODE_EDITOR':
					for space in area.spaces: # iterate through all founded panels
						if space.type == 'NODE_EDITOR':	
							space.tree_type = 'ShaderNodeTree'
							space.shader_type = 'OBJECT'
							'''
							override = {}
							override['area'  ] = area
							override['region'] = space
							
							bpy.ops.node.view_all(override)
							'''
						
		return {'FINISHED'}	
	
	
class ParentObject(bpy.types.Operator):

	'''Make Parent and Show'''
	bl_idname = "object.parent_and_show"
	bl_label = "Make Parent and Show"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		
		# show all
		for obj in bpy.context.selected_objects:
			obj.hide = False
			
		bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
				
		return {'FINISHED'}
	
	
class ProportionalSwitcher(bpy.types.Operator):

	'''Proportional Switcher'''
	bl_idname = "scene.proportional_switcher"
	bl_label = "Proportional Switcher"
#	bl_options = {'REGISTER', 'UNDO'}

	proportionalType = [
#	("DISABLED", "DISABLED", "", "", 0),
    ("ENABLED", "Enable", "", "", 0),
	("PROJECTED", "Projected", "", "", 1),
    ("CONNECTED", "Connected", "", "", 2)
    ]

	type = EnumProperty( name = "Type", description = "", items = proportionalType )
	
	def execute(self, context):
		
		# same is calling toggle
		if( bpy.context.scene.tool_settings.proportional_edit != 'DISABLED' ):
			bpy.context.scene.tool_settings.proportional_edit = 'DISABLED'
			
		elif( bpy.context.scene.tool_settings.proportional_edit == 'DISABLED' ): 
			bpy.context.scene.tool_settings.proportional_edit = self.type
			
		else:
			bpy.context.scene.tool_settings.proportional_edit = 'DISABLED'
	
		# TODO - add also DOPE and GRAPH
		
		return {'FINISHED'}
	
	
# Switch like in the Photoshop ("X" key)
class SwitchWeight(bpy.types.Operator):

	'''Switch Weight value from 1 to 0'''
	bl_idname = "scene.switch_weight"
	bl_label = "Switch Weight"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		
		bpy.context.scene.tool_settings.unified_paint_settings.use_unified_weight = True

		# show all
		if(bpy.context.scene.tool_settings.unified_paint_settings.weight == 0):
			bpy.context.scene.tool_settings.unified_paint_settings.weight = 1
		else:
			bpy.context.scene.tool_settings.unified_paint_settings.weight = 0	
	
		return {'FINISHED'}
	

# set UV mark and set seam to view	
class MarkSeamWithDisplay(bpy.types.Operator):

	'''Mark UV seam with display'''
	bl_idname = "mesh.mark_seam_with_display"
	bl_label = "Mark UV Seam"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		
		# show all
		bpy.ops.mesh.mark_seam(clear=False)
		bpy.context.object.data.show_edge_crease = False
		bpy.context.object.data.show_edge_seams = True
		bpy.context.object.data.show_edge_sharp = False
		bpy.context.object.data.show_edge_bevel_weight = False
				
		return {'FINISHED'}

	
# TIMELINE #	
def TIMELINE_HT_AudioMute(self, context):
	
	layout = self.layout
	
	if(bpy.context.scene.use_audio):
		icon = "MUTE_IPO_ON"
	else:
		icon = "MUTE_IPO_OFF"

	row = layout.row(align=True)
	row.operator( "screen.audio_mute_toggle", text = "Audio", icon = icon )
		
		
class AudioMuteToggle(bpy.types.Operator):

	bl_idname = "screen.audio_mute_toggle"
	bl_label = "Audio Mute Toggle"

	def execute(self, context):
	
		bpy.context.scene.use_audio = not bpy.context.scene.use_audio

		return {'FINISHED'}	
		

# Add mist with settings (start and depth), it is just command for call		
class AddMistPass(bpy.types.Operator):


	bl_idname = "scene.add_mist_pass"
	bl_label = "Add Mist Pass"
	bl_options = {'REGISTER', 'UNDO'}
	
	start = FloatProperty( name="Start", default=5 )
	depth = FloatProperty( name="Depth", default=25 )
	
	
	def execute(self, context):
	
		# activate mist pass
		bpy.context.scene.render.layers[ bpy.context.scene.render.layers.active.name ].use_pass_mist = True

		bpy.context.scene.world.mist_settings.start = self.start
		bpy.context.scene.world.mist_settings.depth = self.depth

		# show mist settings
		if(bpy.context.scene.objects.active.type == "CAMERA"):
			bpy.context.scene.objects.active.data.show_mist = True
			
		elif(bpy.context.scene.camera != None):
			bpy.context.scene.camera.data.show_mist = True

		return {'FINISHED'}	
			
								
################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	bpy.types.TIME_HT_header.prepend(TIMELINE_HT_AudioMute)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.TIME_HT_header(TIMELINE_HT_AudioMute)
	
if __name__ == "__main__":
	register()