import bpy, bmesh, mathutils, math, bpy_extras, ast, os, time
from mathutils import *
from operator import itemgetter
from . import auto_rig_datas, auto_rig_reset, rig_functions

#custom icons
import bpy.utils.previews


print("\n Starting Auto-Rig Pro...\n")

blender_version = bpy.app.version_string
print('Blender version: ', blender_version)



 ##########################	 CLASSES  ######################### 
 
 
 
class ARP_OT_report_message(bpy.types.Operator):
	""" Report a message in a popup window"""
	bl_label = ''
	bl_idname = "arp.report_message"
	
	message = ""
	icon_type = 'INFO'
	
	def draw(self, context):
		
		layout = self.layout		
		split_message = self.message.split('\n')
	
		for i, line in enumerate(split_message):
			if i == 0:				
				layout.label(text=line, icon = self.icon_type)	
			else:
				layout.label(text=line)		
	
	def execute(self, context):		
		return {"FINISHED"}
		
	def invoke(self, context, event):		
		wm = context.window_manager		
		return wm.invoke_props_dialog(self, width=400)
		
 
class ARP_OT_show_limb_params(bpy.types.Operator):
	  
	#tooltip
	"""Show the selected limb parameters"""
	
	bl_idname = "arp.show_limb_params"
	bl_label = "Limb Options"
	bl_options = {'UNDO'}	
	
	limb_type : bpy.props.StringProperty(default="")	
	ear_count : bpy.props.IntProperty(default = 2, min = 1, max = 16, description="Set the number of ear bones")
	neck_count : bpy.props.IntProperty(default = 1, min = 1, max = 16, description="Set the number of neck bones")
	facial : bpy.props.BoolProperty(default=True, description = "Facial controllers (mouth, eyes, eyelids...)")
	finger_thumb : bpy.props.BoolProperty(default = True)
	finger_index : bpy.props.BoolProperty(default = True)
	finger_middle : bpy.props.BoolProperty(default = True)
	finger_ring : bpy.props.BoolProperty(default = True)
	finger_pinky : bpy.props.BoolProperty(default = True)
	toes_thumb : bpy.props.BoolProperty(default = True)
	toes_index : bpy.props.BoolProperty(default = True)
	toes_middle : bpy.props.BoolProperty(default = True)
	toes_ring : bpy.props.BoolProperty(default = True)
	toes_pinky : bpy.props.BoolProperty(default = True)
	bottom : bpy.props.BoolProperty(default=False, description="Bottom controllers")
	
	
	@classmethod
	def poll(cls, context):
		if is_object_arp(bpy.context.active_object):
			if bpy.context.mode == 'EDIT_ARMATURE':
				if len(context.selected_editable_bones) > 0:
					return True			
			
	def draw(self, context):
		layout = self.layout		
		layout.label(text=self.limb_type.title())
		
		if self.limb_type == "spine":			
			layout.prop(context.object, "rig_spine_count", text="Count")
			layout.prop(self, "bottom", text="Bottom")
		elif self.limb_type == "tail":
			layout.prop(context.object, "rig_tail_count", text="Count")
		elif self.limb_type == "neck":
			layout.prop(self, "neck_count", text="Count")
		elif self.limb_type == "head":
			layout.prop(self, "facial", text="Facial")
		elif self.limb_type == "ear":
			layout.prop(self, 'ear_count', text="Count")
		elif self.limb_type == "arm":
			layout.label(text="Rotate Fingers from Scale:")
			layout.prop(context.active_object, "rig_fingers_rot", text="")
			layout.label(text="Fingers Shapes:")
			layout.prop(context.active_object, "arp_fingers_shape_style", text="")
			
			row = layout.row()
			row.prop(self, "finger_thumb", text="Thumb")
			row.prop(self, "finger_index", text="Index")
			row = layout.row()
			row.prop(self, "finger_middle", text="Middle")
			row.prop(self, "finger_ring", text="Ring")
			row = layout.row()
			row.prop(self, "finger_pinky", text="Pinky")
		elif self.limb_type == "leg":
			row = layout.row()
			row.prop(self, "toes_thumb", text="Thumb")
			row.prop(self, "toes_index", text="Index")
			row = layout.row()
			row.prop(self, "toes_middle", text="Middle")
			row.prop(self, "toes_ring", text="Ring")
			row = layout.row()
			row.prop(self, "toes_pinky", text="Pinky")
		else:
			layout.label(text="This limb has no parameters")#, icon = 'INFO')
				
				
	def execute(self, context):
		
		if self.limb_type == "tail":
			set_tail(True)			
		elif self.limb_type == 'ear':			
			set_ears(self.ear_count)			
		elif self.limb_type == 'neck':
			set_neck(self.neck_count)
		elif self.limb_type == 'arm':
			set_fingers(self.finger_thumb, self.finger_index, self.finger_middle, self.finger_ring, self.finger_pinky)
		elif self.limb_type == 'leg':
			set_toes(self.toes_thumb, self.toes_index, self.toes_middle, self.toes_ring, self.toes_pinky)
		elif self.limb_type == 'head':
			set_facial(self.facial)
		elif self.limb_type == 'spine':
			set_spine(bottom=self.bottom)
		return {'FINISHED'}
		
		
	def invoke(self, context, event):
		
		# Get the selected bone limb type
		sel_bone_name = context.selected_editable_bones[0].name 
		split_name = sel_bone_name.split('_')
		side = sel_bone_name[-2:]
		if "_dupli_" in sel_bone_name:
			side = sel_bone_name[-12:]
			
		arm_bones_ref = ["shoulder", "arm", "forearm", "hand", "index1", "index2", "index3", "thumb1", "thumb2", "thumb3", "middle1", "middle2", "middle3", "ring1", "ring2", "ring3", "pinky1", "pinky2", "pinky3"]
		leg_bones_ref = ["thigh", "leg", "foot", "toes"]
		
		if get_edit_bone(sel_bone_name).layers[17]:# reference bones only
			if split_name[0] == 'root' or split_name[0] == 'spine':
				self.limb_type = "spine"				
				self.bottom = bool(get_edit_bone("bot_bend_ref"+side.replace('.x', '.l')))
			elif split_name[0] == 'tail':
				self.limb_type = "tail"
			elif split_name[0] == 'neck' or split_name[0] == 'subneck':
				self.limb_type = 'neck'
			elif split_name[0] == 'head':
				self.limb_type = 'head'
				# evaluate the facial bones
				self.facial = bool(get_edit_bone("jaw_ref" + side))
				print("c_jawbone" + side)
				
			elif split_name[0] == 'ear':
				self.limb_type = 'ear'
			elif split_name[0] in arm_bones_ref:
				self.limb_type = 'arm'
				# evaluate the current fingers
				hand = get_edit_bone("hand"+side)
				if hand:
					children = [child.name.split('_')[1] for child in hand.children]				
					self.finger_thumb = "thumb1" in children					
					self.finger_index = "index1" in children					
					self.finger_middle = "middle1" in children					
					self.finger_ring = "ring1" in children									
					self.finger_pinky = "pinky1" in children
					
			elif split_name[0] in leg_bones_ref:
				self.limb_type = 'leg'
				# evaluate the current toes
				toes = get_edit_bone("toes_01"+side)
				if toes:					
					children = [child.name.split('.')[0].split('_')[2] for child in toes.children]	
					
					self.toes_thumb = "thumb1" in children					
					self.toes_index = "index1" in children					
					self.toes_middle = "middle1" in children					
					self.toes_ring = "ring1" in children									
					self.toes_pinky = "pinky1" in children
			else:
				self.limb_type = ""
				
		else:
			self.report({"WARNING"},  "Select a reference bone")
			return {'FINISHED'}
		
		# Open dialog
		wm = context.window_manager		
		return wm.invoke_props_dialog(self)
		
		
class ARP_OT_export_data(bpy.types.Operator):
	  
	#tooltip
	"""Export some rig data into file (bone transform constraints values)"""
	
	bl_idname = "arp.export_data"
	bl_label = "export_data"
	bl_options = {'UNDO'}		
	
	
	@classmethod
	def poll(cls, context):
		return is_object_arp(bpy.context.active_object)	
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False	
					   
		try:		   
			_export_data()
			self.report({"INFO"}, "Transform constraints value exported")
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo	
				
		return {'FINISHED'}
		
	
 
class ARP_OT_export_limbs(bpy.types.Operator):
	  
	#tooltip
	"""Export the limbs as separate blend files"""
	
	bl_idname = "arp.export_limbs"
	bl_label = "export_limbs"
	bl_options = {'UNDO'}	
	
	state_proxy_picker : bpy.props.BoolProperty(default=False)
	state_xmirror : bpy.props.BoolProperty(default=False)
	
	
	@classmethod
	def poll(cls, context):
		return is_object_arp(bpy.context.active_object)		
	
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False	
		
					   
		try:		   
			_export_limbs(self)
			self.report({"INFO"}, "Limbs exported")
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo 
				
		return {'FINISHED'}
 
 
class ARP_OT_remove_picker(bpy.types.Operator):
	  
	#tooltip
	"""Remove the picker panel"""
	
	bl_idname = "arp.remove_picker"
	bl_label = "remove_picker"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		return is_object_arp(bpy.context.active_object)		
	
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False	
		
					   
		try:		   
			_remove_picker()
			self.report({"INFO"}, "Picker removed")
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo 
				
		return {'FINISHED'}
 
class ARP_OT_add_picker(bpy.types.Operator):
	  
	#tooltip
	"""Add the picker panel"""
	
	bl_idname = "arp.add_picker"
	bl_label = "add_picker"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		return is_object_arp(bpy.context.active_object)				
	
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False	
		
		addon_directory = os.path.dirname(os.path.abspath(__file__))		
		filepath = addon_directory + "/picker.py"
					   
		try:		   
			add_picker_result = _add_picker(self, context, filepath, True, True)
			
			if add_picker_result:			
				self.report({"INFO"}, "Picker generated")
			else:
				self.report({"INFO"}, "Picker already generated")
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo 
				
		return {'FINISHED'} 
		
		
class ARP_OT_import_picker(bpy.types.Operator):
	  
	"""Import the picker panel"""
	
	bl_idname = "arp.import_picker"
	bl_label = "Import Picker"

	filepath : bpy.props.StringProperty(subtype="FILE_PATH", default='py')
	
	@classmethod
	def poll(cls, context):
		return is_object_arp(bpy.context.active_object)		

	def execute(self, context):		   
	
		try:
			file = open(self.filepath, 'rU')
			file.close()
		except:
			self.report({"ERROR"}, "Invalid file path")
			return {'FINISHED'}
			
		_import_picker(self.filepath, self, context)
				
		self.report({"INFO"}, "Picker imported")
		
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = 'picker.py'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
		
class ARP_OT_export_picker(bpy.types.Operator):
	  
	#tooltip
	"""Export the picker panel"""
	
	bl_idname = "arp.export_picker"
	bl_label = "Export Picker"
	bl_options = {'UNDO'}	
	
	filepath : bpy.props.StringProperty(subtype="FILE_PATH", default='py')
	
	@classmethod
	def poll(cls, context):
		return is_object_arp(bpy.context.active_object)		

	def execute(self, context):		   
	
		_export_picker(self.filepath, self, context)
		
		self.report({"INFO"}, "Picker exported")
		
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = 'picker.py'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
 
class ARP_OT_add_fist_ctrl(bpy.types.Operator):
	  
	#tooltip
	"""Add a controller to the selected hand to blend all fingers into a fist pose by scaling it.\nRequires an action containing 'rig_fist' in its name, rest pose at frame 0, fist at frame 10"""
	
	bl_idname = "arp.add_fist_ctrl"
	bl_label = "add_fist_ctrl"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		return bpy.context.mode == 'POSE'
			
	
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False	
		
		# something selected?		
		if len(bpy.context.selected_pose_bones) == 0:
			self.report({'ERROR'}, "The hand controller must be selected")
			return {'FINISHED'}	  
		
		# hand selected?
		if not "hand" in bpy.context.selected_pose_bones[0].name:
			self.report({'ERROR'}, "The hand controller must be selected")
			return {'FINISHED'}	  
		
		# is "rig_fist" action created?
		fist_action = ""
		
		for act in bpy.data.actions:
			if "rig_fist" in act.name:
				fist_action = act.name
		
		if fist_action == "":
			self.report({'ERROR'}, '"rig_fist" was not found in actions names.\nAn action must be created with "rig_fist" in the name. See documentation.')
			return {'FINISHED'}	  
			   
		try:		   
			_add_fist_ctrl(fist_action)
			self.report({"INFO"}, "Fist controller added.")
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo 
				
		return {'FINISHED'}	  
		
class ARP_OT_remove_fist_ctrl(bpy.types.Operator):
	  
	#tooltip
	"""Remove the fist controller"""
	
	bl_idname = "arp.remove_fist_ctrl"
	bl_label = "remove_fist_ctrl"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return bpy.context.mode == 'POSE'
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False	
		
		# something selected?		
		if len(bpy.context.selected_pose_bones) == 0:
			self.report({'ERROR'}, "Please select the hand controller first.")
			return {'FINISHED'}	  
		
		# hand selected?
		if not "hand" in bpy.context.selected_pose_bones[0].name:
			self.report({'ERROR'}, "Please select the hand controller first.")
			return {'FINISHED'}			
		
			   
		try:		   
			_remove_fist_ctrl()
			self.report({"INFO"}, "Fist controller removed.")
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo 
				
		return {'FINISHED'}	  
 
 

class ARP_OT_mirror_picker(bpy.types.Operator):
	  
	#tooltip
	"""Mirror the selected picker bone(s) transforms"""
	
	bl_idname = "arp.mirror_picker"
	bl_label = "mirror_picker"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if is_object_arp(context.active_object):	
				found_picker = True
				try:
					context.scene.Proxy_Picker.active
				except:
					found_picker = False
				if found_picker:
					if not context.scene.Proxy_Picker.active:
						return True
				  
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False		 
			   
		try:		   
			_mirror_picker()
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 

class ARP_OT_move_picker_layout(bpy.types.Operator):
	  
	#tooltip
	"""Edit the picker layout, buttons and text position. The picker selection will be disabled.\nClick Apply Layout to complete and enable again the picker selection"""
	
	bl_idname = "arp.move_picker_layout"
	bl_label = "move_picker_layout" 
	
	state : bpy.props.StringProperty("")
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if is_object_arp(context.active_object):
				return True
				
	def execute(self, context):			   
			   
		 # Is there a picker?
		if bpy.context.active_object.data.bones.get("Picker"):
		 
			_move_picker_layout(self.state, self)
			
		else:
			self.report({"ERROR"}, "Add the picker panel first.")
			
		return {'FINISHED'} 


 

class ARP_OT_screenshot_head_picker(bpy.types.Operator):
	  
	#tooltip
	"""Capture the current view as the facial picker background image"""
	
	bl_idname = "arp.screenshot_head_picker"
	bl_label = "Save .PNG"	
	
			  
	filepath : bpy.props.StringProperty(subtype="DIR_PATH", default='')
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if is_object_arp(context.active_object):
				return True
				
	def execute(self, context):			   
		_screenshot_head_picker(self.filepath)		   
		return {'FINISHED'}		
	

	def invoke(self, context, event):
		# Is there a picker?
		if bpy.context.active_object.data.bones.get("Picker"):
			self.filepath = 'picker_bg_face.png'
			context.window_manager.fileselect_add(self)
			return {'RUNNING_MODAL'}
			
		else:
			self.report({"ERROR"}, "Add the picker panel first.")
			return {'FINISHED'} 
		

	
		
 
class ARP_OT_assign_colors(bpy.types.Operator):
	  
	#tooltip
	"""Assign the colors"""
	
	bl_idname = "arp.assign_colors"
	bl_label = "assign_colors"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if is_object_arp(context.active_object):
				return True
				  
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False		 
			   
		try:		   
			_assign_colors()
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
		
class ARP_OT_clean_skin(bpy.types.Operator):
	  
	#tooltip
	"""Clean weight groups"""
	
	bl_idname = "arp.clean_skin"
	bl_label = "clean_skin"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context): 
		if context.active_object:
			if context.active_object.type == 'MESH':
				return True
	
				  
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False		 
			   
		try:		   
			_clean_skin()
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
		
		
class ARP_OT_delete_arp(bpy.types.Operator):
	  
	#tooltip
	"""Delete the Auto-Rig Pro armature"""
	
	bl_idname = "arp.delete_arp"
	bl_label = "delete_arp"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if is_object_arp(context.active_object):				
				return True 
				  
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False		 
			   
		try:		   
			_delete_arp()
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}	 
 
 
class ARP_OT_append_arp(bpy.types.Operator):
	  
	#tooltip
	"""Add the Auto-Rig Pro armature in the scene. Only compatible with Blender 2.79 and above, \nappend by hand (Shift-F1) otherwise"""
	
	bl_idname = "arp.append_arp"
	bl_label = "append_arp"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		if not ('2.78' in blender_version) or ('2.78' in blender_version and 'sub 5' in blender_version or 'sub 6' in blender_version):
			if bpy.data.objects.get('rig') == None:				
				return True
	
	rig_presets : bpy.props.EnumProperty(items=(('human', 'Human', ""), ('dog', "Dog", ""), ('horse', 'Horse', ""), ('free', 'Empty', "")))
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False		 
			   
		try:		 
			
			_append_arp(self.rig_presets)
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
 

class ARP_OT_exit_edit_shape(bpy.types.Operator):
	  
	#tooltip
	"""Apply the selected shape"""
	
	bl_idname = "arp.exit_edit_shape"
	bl_label = "exit_edit_shape"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.mode == 'EDIT_MESH':	 
				if 'cs_user' in context.active_object.name:
					return True
				  
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False		 
			   
		try:		   
			_exit_edit_shape()
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
 
 
class ARP_OT_edit_custom_shape(bpy.types.Operator):
	  
	#tooltip
	"""Edit the selected bone shape"""
	
	bl_idname = "arp.edit_custom_shape"
	bl_label = "edit_custom_shape"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'POSE':
			if bpy.context.active_pose_bone:
				return True
				#if 'c_' in bpy.context.active_pose_bone.name:
					
				  
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False		 
			   
		try:		
			if bpy.context.active_pose_bone.custom_shape:
				_edit_custom_shape()
			else:
				self.report({"ERROR"}, "No custom shapes set for this bone. Create one first.")
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
		
class ARP_OT_mirror_custom_shape(bpy.types.Operator):
	  
	#tooltip
	"""Mirror the selected bone shape to the other side"""
	
	bl_idname = "arp.mirror_custom_shape"
	bl_label = "mirror_custom_shape"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'POSE':
			if bpy.context.active_pose_bone:
				#if 'c_' in bpy.context.active_pose_bone.name:
				return True
				  
				
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False		 
			   
		try:	
			if bpy.context.active_pose_bone.custom_shape:
				_mirror_custom_shape()
			else:
				self.report({"ERROR"}, "No custom shapes set for this bone. Create one first.")
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
		
class ARP_OT_import_colors(bpy.types.Operator):
	"""Import the color set"""
	bl_idname = "arp.import_colors"
	bl_label = "Import Colors"

	filepath : bpy.props.StringProperty(subtype="FILE_PATH", default='py')


	def execute(self, context):		   
		_import_colors(self.filepath)
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = 'color_set.py'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
 
class ARP_OT_export_colors(bpy.types.Operator):
	"""Export the color set"""
	bl_idname = "arp.export_colors"
	bl_label = "Export Colors"

	filepath : bpy.props.StringProperty(subtype="FILE_PATH", default='py')
	

	def execute(self, context):		   
		_export_colors(self.filepath)
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = 'color_set.py'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class ARP_OT_export_ref(bpy.types.Operator):
	"""Export the reference bones transforms data"""
	bl_idname = "arp.export_ref"
	bl_label = "Export Ref Bones"

	filepath : bpy.props.StringProperty(subtype="FILE_PATH", default='py')
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'EDIT_ARMATURE':			 
			return True

	def execute(self, context):		   
		_export_ref(self.filepath)
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = 'arp_ref_bones.py'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class ARP_OT_import_ref(bpy.types.Operator):
	"""Import the reference bones transform datas"""
	bl_idname = "arp.import_ref"
	bl_label = "Import Ref Bones"

	filepath : bpy.props.StringProperty(subtype="FILE_PATH", default='py')
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'EDIT_ARMATURE':			 
			return True

	def execute(self, context):		   
		_import_ref(self.filepath)
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = 'arp_ref_bones.py'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}


 
 
class ARP_OT_disable_limb(bpy.types.Operator):
	  
	#tooltip
	"""Disable (remove safely) the selected limb"""
	
	bl_idname = "arp.disable_limb"
	bl_label = "disable_limb"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'EDIT_ARMATURE':
			if len(context.selected_editable_bones) > 0:				
				return True
			else:
				return False
		
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
			   
		try:		   
			_disable_limb(self, context)
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}

		
## Update Armature classes ##

# operator run when clicked 
class ARP_OT_update_armature_clicked(bpy.types.Operator):
	"""Update old armatures to the latest version\nMay require to click 'Match to Rig' afterward to correct bones alignment"""

	bl_idname = "arp.update_armature_clicked"
	bl_label = "update_armature"
	bl_options = {'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if is_object_arp(context.active_object):
				return True

	def execute(self, context):		

		if context.active_object.proxy:
			self.report({'ERROR'}, "Armature cannot be updated in proxy mode")
			return {'FINISHED'}			
		
		
		# open the dialog if necessary to show a warning
		breaking_update = False
		if get_data_bone("c_jawbone.x"):
			if get_data_bone("jawbone.x") == None or get_data_bone("eyelid_top.l") == None:
				breaking_update = True
		
		if breaking_update:
			bpy.ops.arp.update_armature_dialog("INVOKE_DEFAULT")
		else:
			# else just run the default update
			bpy.ops.arp.update_armature_operator()
			
		return {'FINISHED'}
			
		
# window dialog if necessary
class ARP_OT_update_armature_dialog(bpy.types.Operator):
	""" This update includes bones transforms change, then it can break the rig pose and animation"""
	bl_label = ''
	bl_idname = "arp.update_armature_dialog"
	
	
	def draw(self, context):
		layout = self.layout
		layout.label(text="Important Note!", icon='INFO')
		layout.label(text="This update includes transforms changes for the following bone controllers:")
		layout.label(text="Eyelids, Jawbone")
		layout.label(text="Therefore it will break these controllers existing poses or animations.")		
		layout.label(text="Continue?")
		layout.label(text="May require to click Match to Rig afterward to fix bones rotations.", icon='INFO')
		
	
	def execute(self, context):		
		bpy.ops.arp.update_armature_operator()
		self.report({'INFO'}, "Armature Updated")
		return {"FINISHED"}
		
	def invoke(self, context, event):
		wm = context.window_manager 
		return wm.invoke_props_dialog(self, width=400)

# main update operator
class ARP_OT_update_armature_operator(bpy.types.Operator):
	bl_idname = "arp.update_armature_operator"
	bl_label = "Update" 
	
	def execute(self, context): 
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		try:			
			_update_armature(self, context)	
				
			
		finally:
			context.preferences.edit.use_global_undo = use_global_undo
			
		return {"FINISHED"}
		
		
class ARP_OT_set_shape_key_driver(bpy.types.Operator):
	  
	#tooltip
	"""Add a keyframe point on the selected shape key driver curve (0 or 1) according the bone transform value"""
	
	bl_idname = "arp.set_shape_key_driver"
	bl_label = "set_shape_key_driver"
	bl_options = {'UNDO'}	
	
	value : bpy.props.StringProperty(name="Driver Value")
	
	@classmethod
	def poll(cls, context):		  
		return (context.active_object)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		if context.active_object.type != 'MESH':	   
			self.report({'ERROR'}, "Select the mesh and the shape key")
			return{'FINISHED'}
		
		try:		   
			_set_shape_key_driver(self, self.value)		
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
 
class ARP_OT_pick_bone(bpy.types.Operator):
	  
	#tooltip
	"""Get the selected bone"""
	
	bl_idname = "arp.pick_bone"
	bl_label = "pick_bone"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):		  
		return (context.active_object)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		if context.active_object.type != 'ARMATURE':	   
			self.report({'ERROR'}, "First select a bone to pick it.")
			return{'FINISHED'}
		
		try:		   
			_pick_bone()		
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
 
class ARP_OT_create_driver(bpy.types.Operator):
	  
	#tooltip
	"""Create a driver for the selected shape key using the Bone name and Bone transform parameter. Select first the armature then the mesh object"""
	
	bl_idname = "arp.create_driver"
	bl_label = "create_driver"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:		   
			_create_driver()		
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
 
class ARP_OT_set_picker_camera(bpy.types.Operator):
	  
	#tooltip
	"""Display the bone picker in this active view"""
	
	bl_idname = "arp.set_picker_camera"
	bl_label = "set_picker_camera"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if is_object_arp(context.active_object):
				return True

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:		
			
			rig_functions._set_picker_camera(self)		
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
 
class ARP_OT_bind_to_rig(bpy.types.Operator):
	  
	#tooltip
	"""Select first the mesh(es), then the armature and click it to bind"""
	
	bl_idname = "arp.bind_to_rig"
	bl_label = "bind_to_rig"
	bl_options = {'UNDO'}	
	
	binding_error : bpy.props.BoolProperty(default=False)
	
	@classmethod
	def poll(cls, context):		
		if context.active_object:
			if is_object_arp(context.active_object):
				return True

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		# save the bones transforms to restore if any error
		ebones_dict = {}
		bpy.ops.object.mode_set(mode='EDIT')
		for ebone in bpy.context.active_object.data.edit_bones:
			ebones_dict[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll
		
		rig_name = bpy.context.active_object.name
		
		# get the limbs
		limb_sides.get_multi_limbs()
		
		try:
			# simplify for performances reasons		
			simplify_value = bpy.context.scene.render.use_simplify
			simplify_subd = bpy.context.scene.render.simplify_subdivision
			bpy.context.scene.render.use_simplify = True
			bpy.context.scene.render.simplify_subdivision = 0
			
			# make sure to unbind first
			active_obj = context.active_object
			_unbind_to_rig()
			set_active_object(active_obj.name)
			
			if not bpy.context.scene.arp_debug_mode:
				# on release mode, handles error internally
				try:
					_bind_to_rig(self, context)		
				except:
					self.binding_error = True
					self.report({'ERROR'}, "Binding error")
					
			else:		
				# on debug mode, explicitly reports error
				_bind_to_rig(self, context)		
			
			#restore simplify
			bpy.context.scene.render.use_simplify = simplify_value
			bpy.context.scene.render.simplify_subdivision = simplify_subd
					   
		finally:
		
			# If error when binding, restore bones transforms
			if self.binding_error:
			
				set_active_object(rig_name)
				bpy.ops.object.mode_set(mode='EDIT')
				
				for ebone in ebones_dict:
					get_edit_bone(ebone).head, get_edit_bone(ebone).tail, get_edit_bone(ebone).roll = ebones_dict[ebone]
				
				# and delete temporary skinning bones				
				for eb in bpy.context.active_object.data.edit_bones:
					found = False
					for ebone in ebones_dict:
						if eb.name == ebone:
							found = True
					if not found:			
						print("Remove", eb.name)
						bpy.context.active_object.data.edit_bones.remove(eb)						
					
				bpy.ops.object.mode_set(mode='OBJECT')
				
				# hide the rig_add
				rig_add = get_rig_add(bpy.data.objects[rig_name])
				if rig_add:		
					rig_add.select_set(state=False)
					rig_add.hide_viewport = True
					
			
			context.preferences.edit.use_global_undo = use_global_undo
			
		return {'FINISHED'}
		
		
class ARP_OT_unbind_to_rig(bpy.types.Operator):
	  
	#tooltip
	"""Unbind the selected mesh from the rig"""
	
	bl_idname = "arp.unbind_to_rig"
	bl_label = "unbind_to_rig"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context): 
		if context.active_object:
			if context.active_object.type == 'MESH':
				return True

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			
			_unbind_to_rig()		
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}


class ARP_OT_edit_ref(bpy.types.Operator):
	  
	#tooltip
	"""Display and edit the reference bones"""
	
	bl_idname = "arp.edit_ref"
	bl_label = "edit_ref"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if is_object_arp(context.active_object):
				if not context.active_object.data.layers[17]:
					return True

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			try: #check if the armature is selected				  
				get_bones = bpy.context.active_object.data.bones					   
			except AttributeError:
				self.report({'ERROR'}, "Select the rig object")						
				return{'FINISHED'}
				
			_edit_ref()			   
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
		
class ARP_OT_add_limb(bpy.types.Operator):
		  
	#tooltip
	"""Add a limb"""
	
	bl_idname = "arp.add_limb"
	bl_label = "add_limb"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if not ('2.78' in blender_version) or ('2.78' in blender_version and 'sub 5' in blender_version or 'sub 6' in blender_version):			
			return True
	
	limbs : bpy.props.EnumProperty(items=(('spine', 'Spine', ""), ('arm.l', 'Arm (Left)', ""), ('arm.r', 'Arm (Right)', ""), ('leg.l', "Leg (Left)", ""), ('leg.r', "Leg (Right)", ""), ('head', 'Head', ""), ('ears', 'Ears', ''), ('tail', 'Tail', ""), ('breast', 'Breast', '')))
	
	report_message = ""

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		try:			
			_add_limb(self, self.limbs)
			_edit_ref()
			
		finally:
		
			if self.report_message != "":
				#self.report({'INFO'}, self.report_message)
				ARP_OT_report_message.message = self.report_message
				ARP_OT_report_message.icon_type = 'INFO'
				bpy.ops.arp.report_message('INVOKE_DEFAULT')
				
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
class ARP_OT_dupli_limb(bpy.types.Operator):
	  
	#tooltip
	""" Duplicate the selected limb"""
	
	bl_idname = "arp.dupli_limb"
	bl_label = "dupli_limb"
	bl_options = {'UNDO'}	
	
	first_mouse_x : bpy.props.IntProperty()
	first_value : bpy.props.FloatProperty()
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'EDIT_ARMATURE':
			if len(context.selected_editable_bones) > 0:
				bone = context.selected_editable_bones[0]
				if len(bone.keys()) > 0:
					if 'arp_duplicate' in bone.keys():
						return True

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			try: #check if the armature is selected				  
				get_bones = bpy.context.active_object.data.bones					   
			except AttributeError:
				self.report({'ERROR'}, "Select the rig object")						
				return{'FINISHED'}
				
			_dupli_limb()		  
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
	   
		
class Limb_Sides:
	
	arm_sides = [".l", ".r"]
	leg_sides = [".l", ".r"]
	head_sides = [".x"]
	ear_sides = [".l", ".r"]	
	spine_sides = [".x"]	
	
	
	def init_values(self):	
		self.arm_sides = []
		self.leg_sides = []
		self.head_sides = []
		self.ear_sides = [] 
		self.spine_sides = []
			
		
	def get_multi_limbs(self):
	
		current_mode = bpy.context.mode
		bpy.ops.object.mode_set(mode='EDIT')
		
		# reset values
		self.init_values()
		print("Reset limb sides:")	

		# Spines	
		for bone in bpy.context.active_object.data.edit_bones:
			if "root_ref." in bone.name:
				if not bone.name[-2:] in self.spine_sides:
					self.spine_sides.append(bone.name[-2:]) 
					
			if "root_ref_dupli" in bone.name:
				if not bone.name[-12:] in self.spine_sides:
					self.spine_sides.append(bone.name[-12:])	
					
			
		# Arms		
			if "shoulder_ref." in bone.name:
				if not bone.name[-2:] in self.arm_sides:
					self.arm_sides.append(bone.name[-2:])	
					
			if "shoulder_ref_dupli" in bone.name:
				if not bone.name[-12:] in self.arm_sides:
					self.arm_sides.append(bone.name[-12:])	
					
		# Legs			
			if "thigh_ref." in bone.name:
				if not bone.name[-2:] in self.leg_sides:
					self.leg_sides.append(bone.name[-2:])	
					
			if "thigh_ref_dupli" in bone.name:
				if not bone.name[-12:] in self.leg_sides:
					self.leg_sides.append(bone.name[-12:])

		# Heads 
			if "neck_ref." in bone.name:
				if not bone.name[-2:] in self.head_sides:
					self.head_sides.append(bone.name[-2:])
					
			if "neck_ref_dupli" in bone.name:
				if not bone.name[-12:] in self.head_sides:
					self.head_sides.append(bone.name[-12:])
				
		# Ears			
			if "ear_01_ref." in bone.name:
				if not bone.name[-2:] in self.ear_sides:
					self.ear_sides.append(bone.name[-2:])
					
			if "ear_01_ref_dupli_" in bone.name:
				if not bone.name[-12:] in self.ear_sides:
					self.ear_sides.append(bone.name[-12:])
		
		
		print("Found sides:")
		print('Arms', self.arm_sides)
		print('Legs', self.leg_sides)
		print('Heads', self.head_sides)
		print('Ears', self.ear_sides)
		
		# Restore saved mode	   
		if current_mode == 'EDIT_ARMATURE':
			current_mode = 'EDIT'		
		
		bpy.ops.object.mode_set(mode=current_mode)
	

	
	
limb_sides = Limb_Sides()

def refresh_rig_add(_rig):

	# delete current if any
	_rig_add = get_rig_add(_rig)
	if _rig_add:
		bpy.data.objects.remove(_rig_add, do_unlink=True)
		
	# add a new one
	arm_data = bpy.data.armatures.new("rig_add")
	new_rig_add = bpy.data.objects.new("rig_add", arm_data)
	new_rig_add = bpy.data.objects["rig_add"]
	new_rig_add.parent = _rig.parent
	
	# link to group
	for collec in _rig.users_collection:
		collec.objects.link(new_rig_add)				
	
	cns_scale = new_rig_add.constraints.new("COPY_SCALE")
	cns_scale.target = _rig 

	# assign the lost rig_add armature modifiers
	for obj in bpy.data.objects:
		if len(obj.modifiers) > 0:
			for mod in obj.modifiers:
				if mod.type == 'ARMATURE':
					if mod.object == None and mod.name == "rig_add":
						mod.object = new_rig_add
						
	return new_rig_add
	
class ARP_OT_match_to_rig(bpy.types.Operator):
	  
	#tooltip
	"""Generate the final rig from the reference bones"""
	
	bl_idname = "arp.match_to_rig"
	bl_label = "match_to_rig"
	bl_options = {'UNDO'}

	state_proxy_picker : bpy.props.BoolProperty(default=False)
	state_xmirror : bpy.props.BoolProperty(default=False)
	
	
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if is_object_arp(context.active_object):
				return True

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			try:				
				get_bones = bpy.context.active_object.data.bones					   
			except AttributeError:
				self.report({'ERROR'}, "Select the rig object")						
				return{'FINISHED'}
				
			if bpy.context.active_object.data.bones.get("c_head_scale_fix.x"):
				self.report({'ERROR'}, "Armature not up to date. Click Update Armature in the Misc tab.")						
				return{'FINISHED'}
				
						
			# Simplify			
			simplify_value = bpy.context.scene.render.use_simplify
			simplify_subd = bpy.context.scene.render.simplify_subdivision
			bpy.context.scene.render.use_simplify = True
			bpy.context.scene.render.simplify_subdivision = 0
			
			rig_name = context.active_object.name
			rig_add = get_rig_add(bpy.data.objects[rig_name])
			
			# Append the rig_add... if it has been accidentally deleted by the user
			if rig_add == None:
				print("Rig add not found. Append it.")
				rig_add = refresh_rig_add(bpy.data.objects[rig_name])			
				copy_bones_to_rig_add(bpy.data.objects[rig_name], rig_add)
				
			if context.scene.arp_init_scale:			
				# Initialize armatures scale			
				# Apply armature scale only if not already initialized (can lead to bones roll issues otherwise)
				if rig_add.scale != Vector((1.0,1.0,1.0)) or bpy.data.objects[rig_name].scale != Vector((1.0,1.0,1.0)):
					rig_add.hide_viewport = False				
					rig_add.scale = bpy.data.objects[rig_name].scale
					bpy.ops.object.mode_set(mode='OBJECT')	
					bpy.ops.object.select_all(action='DESELECT')
					set_active_object(rig_add.name)		
					bpy.ops.object.mode_set(mode='OBJECT')	
					
					bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
					
					bpy.ops.object.select_all(action='DESELECT')
					set_active_object(rig_name) 
					
					bpy.ops.object.mode_set(mode='OBJECT')	
					bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
					rig_add.select_set(state=False)
					rig_add.hide_viewport = True
				else:
					print("Armature scale already initialized")
					
			
			# Align limbs			
			_initialize_armature(self)			
			
			# Multi limb support
			limb_sides.get_multi_limbs()
	
			# Align bones			
			_align_arm_bones()			
			_align_leg_bones()			
			_align_spine_bones()	
			_set_transform_constraints()			
			_reset_stretches()		
			_set_inverse()		
			
			_finalize_armature(self)
			
			# Set pose position
			bpy.ops.object.mode_set(mode='POSE')			 
			bpy.context.active_object.data.pose_position = 'POSE'	
			
			bpy.context.active_object.show_in_front = False 
			
			#restore simplify
			bpy.context.scene.render.use_simplify = simplify_value
			bpy.context.scene.render.simplify_subdivision = simplify_subd	   
			
			self.report({'INFO'}, "Rig Done")	
			
		finally:
			context.preferences.edit.use_global_undo = use_global_undo 
			
		return {'FINISHED'}	  

	
 ##########################	 FUNCTIONS	##########################
 
	# Utils
def get_point_projection_onto_line_factor(a, b, p):
	# return the factor of the projected point 'p' onto the line 'a,b'	 
	# if below a, factor[0] < 0
	# if above b, factor[1] < 0 
	return ((p-a).dot(b-a), (p-b).dot(b-a))
	
def project_point_onto_line(a, b, p):
	# project the point p onto the line a,b
	ap = p-a
	ab = b-a
	result = a + ap.dot(ab)/ab.dot(ab) * ab
	return result
 
def project_vector_onto_vector(a, b):		
		abdot = (a[0]*b[0])+(a[1]*b[1])+(a[2]*b[2])
		blensq = (b[0]**2)+(b[1]**2)+(b[2]**2)

		temp = abdot/blensq
		c = Vector((b[0]*temp,b[1]*temp,b[2]*temp))
		
		return c	

def project_point_onto_plane(q, p, n):
			n = n.normalized()
			return q - ((q-p).dot(n)) * n	

def is_proxy_bone(bone):
	#bone = edit bone or pose bone
	
	if bone.parent:
			bone_parent1 = bone.parent.name
	else:
		bone_parent1 = "None"
			
	if '_proxy' in bone.name or 'Picker' in bone_parent1 or bone.name == "Picker":
		return True
		
def set_custom_shape(cs_name, target_bone):
	
	# only if the cs is not already edited
	if not "cs_user_" in get_pose_bone(target_bone).custom_shape.name:
		# append the cs into the scene if not found
		if bpy.data.objects.get(cs_name) == None:
			append_from_arp(nodes = [cs_name], type = "object")
			
		# apply it
		get_pose_bone(target_bone).custom_shape = bpy.data.objects[cs_name]
		
		
def _add_limb(self, type):
	
	print("\nAdd limb:", type)
	
	context =  bpy.context
	scene = context.scene
	rig_name = bpy.context.active_object.name	
	current_mode = bpy.context.mode		
	
	# Get the suffix (dupli) for naming
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='DESELECT')
	
	side = type[-2:]
	if not "." in side:
		side = ".x"
		
	suffix, found_base = get_limb_suffix(side, type)
	print("suffix found", suffix)
	bpy.ops.object.mode_set(mode='OBJECT')
	
	# pre-check for single limbs
	single_limbs = ['spine', 'breast', 'tail']
	single_limb_exists = False
	
	if type in single_limbs:
		if found_base:
			single_limb_exists = True
			self.report_message = '"' + type.title() + '" is a single limb. Cannot be added multiple times for now.'
			print(self.report_message)
			
			
	# -- Add limbs --
	# Generated limbs
	if type == "ears":
		print("Dynamically added limb:", type)
		if not found_base:	
			set_ears(2, side_arg=".l")
		else:			
			print("setting ears", '_dupli_' + suffix + '.l')
			set_ears(2, side_arg = '_dupli_' + suffix + '.l', offset_arg = int(suffix))			
	
	elif type == "tail":
		if not single_limb_exists:
			bpy.ops.object.mode_set(mode='POSE')
			set_tail(True)
		
	elif type == "breast":		
		if not single_limb_exists:
			set_breast(True)
			
		
	# Appended limbs
	else:
		# check for single limbs, can be added only once
		if not single_limb_exists:
			
			addon_directory = os.path.dirname(os.path.abspath(__file__))		
			filepath = addon_directory + "/armature_presets/modules.blend"			
			
			# make a list of current custom shapes objects in the scene for removal later
			cs_objects = [obj.name for obj in bpy.data.objects if obj.name[:3] == "cs_"]			
			
			# load the objects in the file internal data
			with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to): 
				# only import the necessary armature
				data_to.objects = [i for i in data_from.objects if i == "rig_" + type]		
				
						
			#check - is it in local view mode?
			# local view removed from Blender 2.8? Disable it for now
			"""
			if context.space_data.lock_camera_and_layers == False:					
				context.space_data.lock_camera_and_layers = True
				context.scene.update()
			"""
			
			# link in scene
			for obj in data_to.objects:				
				scene.collection.objects.link(obj)
			
			# global scale
			bone_scale_ref = 'c_pos'
			if bpy.data.objects[rig_name].data.bones.get(bone_scale_ref):
				b_length = bpy.data.objects[rig_name].data.bones[bone_scale_ref].length
				b_length *= bpy.data.objects[rig_name].scale[0]
				bpy.data.objects['rig_' + type].scale = [b_length/0.22516]*3
			else:
				print(bone_scale_ref, 'not found, scale is not set.')
			
			# replace custom shapes by custom shapes already existing in the scene
			set_active_object('rig_' + type)
			bpy.ops.object.mode_set(mode='POSE')
			for b in bpy.context.active_object.pose.bones:
				if b.custom_shape:
					if b.custom_shape.name not in cs_objects:
						if b.custom_shape.name.replace('.001', '') in cs_objects:
							b.custom_shape = bpy.data.objects[b.custom_shape.name.replace('.001', '')]
							
				# handling of "dupli" naming
				if found_base:					
					b.name = b.name.split('.')[0] + '_dupli_' + suffix + '.' + b.name.split('.')[1]					
					
				# make constraints links
				if len(b.constraints) > 0:
					for cns in b.constraints:
						try:
							if cns.target == None:
								cns.target = bpy.data.objects[rig_name]
						except:
							pass
				
				
			# find added/useless custom shapes and delete them	
			used_shapes = [b.custom_shape.name for b in bpy.context.active_object.pose.bones if b.custom_shape]
			for obj in bpy.data.objects:
				if obj.name[:3] == "cs_":
					if not obj.name in cs_objects and not obj.name in used_shapes:						
						bpy.data.objects.remove(obj, do_unlink=True)
						
			
			bpy.ops.object.mode_set(mode='OBJECT')			
			bpy.context.space_data.overlay.show_relationship_lines = False
			
			# add a transform offset to avoid duplis overlaps
			if found_base:
				offset = int(suffix)				
				if offset:
					bpy.data.objects['rig_' + type].location[0] += offset*0.5
			
			# Merge to the main armature
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object('rig_' + type)
			data_to_del = bpy.data.objects['rig_' + type].data
			set_active_object(rig_name)
			bpy.ops.object.join()
			
			# delete remaining armature data in blend file
			bpy.data.armatures.remove(data_to_del, do_unlink=True)
			
			# Parent lost bones
			bpy.ops.object.mode_set(mode='EDIT')	
			for bn in bpy.context.active_object.data.edit_bones:
				if len(bn.keys()) > 0:
					if "arp_parent" in bn.keys():
						parent_prop = get_edit_bone(bn["arp_parent"])
						if bn.parent == None and parent_prop:
							bn.parent = parent_prop
							
			# clean missing target of constraints
			bpy.ops.object.mode_set(mode='POSE')	
			for pbone in bpy.context.active_object.pose.bones:
				if len(pbone.constraints) > 0:
					for cns in pbone.constraints:
						subtarget_string = ""
						try:
							subtarget_string = cns.subtarget
						except:
							pass
						if subtarget_string != "":
							subtarget = get_pose_bone(subtarget_string)
							if not subtarget:
								cns.subtarget = ""
								
			bpy.ops.object.mode_set(mode='EDIT')	
			# Add the rig_add bones			
			rig_add = get_rig_add(bpy.context.active_object)
			
			if rig_add:				
				bones_added = []
				rig_add.hide_select = False
				rig_add.hide_viewport = False					
				set_active_object(rig_add.name)
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.object.mode_set(mode='EDIT')
				blist = None
				if type[:-2] == "arm":			
					blist = auto_rig_datas.arm_bones_rig_add
					print("found arm")
				if type[:-2] == "leg":			
					blist = auto_rig_datas.leg_bones_rig_add
				if type == "spine":			
					blist = auto_rig_datas.spine_bones_rig_add
					
				if blist:
					for b in blist:
						
						if type == "spine":
							side_suff = ".x"
							b_name = b[:-2]
						else:
							side_suff = '.' + type.split('.')[1]
							b_name = b
							
						new_bname = b_name + side_suff
						
						if found_base:							
							new_bname = b_name + '_dupli_' + suffix + side_suff
							
						if not get_edit_bone(new_bname):							
							newb = rig_add.data.edit_bones.new(new_bname)
							newb.head, newb.tail = [0,0,0], [1,1,1]
							bones_added.append(new_bname)
							print("created", new_bname)
				bpy.ops.object.mode_set(mode='OBJECT')	
				bpy.ops.object.select_all(action='DESELECT')
				rig_add.hide_viewport = True
				rig_add.hide_select = True				
				set_active_object(rig_name)
			else:
				print("Rig add not found")
			
			
			
			
			
	# Restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'		
	
	bpy.ops.object.mode_set(mode=current_mode)
	

def _export_data():
	print("Export transform constraints")
	
	# collect data in dict
	obj = bpy.context.active_object
	bpy.ops.object.mode_set(mode='POSE')
	dict = {}

	for pbone in obj.pose.bones:
		if len(pbone.constraints) > 0:
			for cns in pbone.constraints:   			
				if cns.type == 'TRANSFORM':
					dict[pbone.name] = (cns.name), (cns.from_min_x, cns.from_max_x, cns.from_min_y, cns.from_max_y, cns.from_min_z, cns.from_max_z)
	
	
	# save into file
	addon_directory = os.path.dirname(os.path.abspath(__file__))		
	filepath = addon_directory + "/auto_rig_datas_export.py"
			
	file = open(filepath, "w", encoding="utf8", newline="\n")
	file.write(str(dict)) 
	file.close()
	

def _export_limbs(self):
	print("Export")
	
	_initialize_armature(self)
	
	bpy.ops.armature.select_all(action='DESELECT')
	save_objects = []
	
	# spine
	for b in auto_rig_datas.spine_bones + auto_rig_datas.spine_ref:
		select_edit_bone(b )	
		
	bpy.ops.armature.separate()
	armature_name = "rig_spine"
	bpy.data.objects["rig.001"].name = armature_name
	save_objects.append(armature_name)
	
	# Head
	for b in auto_rig_datas.head_bones + auto_rig_datas.facial_bones + auto_rig_datas.facial_ref + ["head_ref.x", "neck_ref.x"] + auto_rig_datas.neck_bones:
		for side in [".l", ".r"]:
			suff = side
			if b[-2:] == ".x":
				suff = ""
			select_edit_bone(b + suff)	
		
	bpy.ops.armature.separate()
	armature_name = "rig_head"
	bpy.data.objects["rig.001"].name = armature_name
	save_objects.append(armature_name)
	
	# facial
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object("rig_head")
	bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
	bpy.context.active_object.name = "rig_facial_temp"
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='DESELECT')
	
	for bi, b in enumerate(auto_rig_datas.facial_ref + auto_rig_datas.facial_bones):
		bonename = b
		sides = []
		if bonename[-2:] == ".x":
			bonename = bonename.replace(".x", "")
			sides.append(".x")
		else:
			sides.append(".l")
			sides.append(".r")
		
		for side in sides:			
			select_edit_bone(bonename+side)
			ebone = get_edit_bone(bonename+side)
			# save the external parent
			if ebone.parent:
				if ebone.parent == get_edit_bone("c_skull_01.x") or ebone.parent == get_edit_bone("c_skull_02.x") or ebone.parent == get_edit_bone("c_skull_03.x") or ebone.parent == get_edit_bone("head.x"):
					ebone["arp_parent"] = ebone.parent.name		
		
			# save the head matrix in a custom prop, used when appending it near to the head later
			if bi == 0:
				ebone["arp_offset_matrix"] = get_edit_bone("head_ref.x").matrix.inverted()
			
				
	bpy.ops.armature.separate()
	armature_name = "rig_facial"
	bpy.data.objects["rig_facial_temp.001"].name = armature_name
	save_objects.append(armature_name)
	
	bpy.data.objects.remove(bpy.data.objects["rig_facial_temp"], do_unlink=True)
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object("rig")	
	bpy.ops.object.mode_set(mode='EDIT')
	

	# arms		
	for side in [".l", ".r"]:
		for b in auto_rig_datas.arm_bones + auto_rig_datas.arm_ref_bones:
			select_edit_bone(b + side)	
		
		bpy.ops.armature.separate()
		armature_name = "rig_arm" + side
		bpy.data.objects["rig.001"].name = armature_name
		save_objects.append(armature_name)
	
	# Fingers. 
	# TODO: Substitute all of the same repeated list/operations by a single algorithm
		
	for side in [".l", ".r"]:
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object("rig_arm" + side)
		bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
		bpy.context.active_object.name = "rig_fingers" + side
		bpy.ops.object.mode_set(mode='POSE')
		
		# clear inter-fingers constraints, otherwise the other finger is automatically appended when adding the limb
		get_pose_bone("c_middle1_base"+side).constraints["Copy Rotation"].target = None
		get_pose_bone("c_ring1_base"+side).constraints["Copy Rotation"].target = None
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.armature.select_all(action='DESELECT')
		
		# thumb
		for b in auto_rig_datas.thumb_ref_list + auto_rig_datas.thumb_control_list + auto_rig_datas.thumb_intern_list:
			select_edit_bone(b + side)	
		
		# save the hand matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.thumb_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("hand_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_thumb" + side
		bpy.data.objects["rig_fingers" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
		# index
		for b in auto_rig_datas.index_ref_list + auto_rig_datas.index_control_list + auto_rig_datas.index_intern_list:
			select_edit_bone(b + side)	
		
		# save the hand matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.index_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("hand_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_index" + side
		bpy.data.objects["rig_fingers" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
		# middle
		for b in auto_rig_datas.middle_ref_list + auto_rig_datas.middle_control_list + auto_rig_datas.middle_intern_list:
			select_edit_bone(b + side)	
		
		# save the hand matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.middle_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("hand_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_middle" + side
		bpy.data.objects["rig_fingers" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
		
		# ring
		for b in auto_rig_datas.ring_ref_list + auto_rig_datas.ring_control_list + auto_rig_datas.ring_intern_list:
			select_edit_bone(b + side)	
		
		# save the hand matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.ring_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("hand_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_ring" + side
		bpy.data.objects["rig_fingers" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
		# pinky
		for b in auto_rig_datas.pinky_ref_list + auto_rig_datas.pinky_control_list + auto_rig_datas.pinky_intern_list:
			select_edit_bone(b + side)	
		
		# save the hand matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.pinky_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("hand_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_pinky" + side
		bpy.data.objects["rig_fingers" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
				
	bpy.data.objects.remove(bpy.data.objects["rig_fingers" + side], do_unlink=True)
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object("rig")	
	bpy.ops.object.mode_set(mode='EDIT')
	
	# Legs
	for side in [".l", ".r"]:
		for b in auto_rig_datas.leg_bones + auto_rig_datas.leg_ref_bones:
			select_edit_bone(b + side)	
			
		bpy.ops.armature.separate()
		armature_name = "rig_leg" + side
		bpy.data.objects["rig.001"].name = armature_name
		save_objects.append(armature_name)
		
	# Toes 
	# TODO: Substitute all of the same repeated list/operations by a single algorithm
		
	for side in [".l", ".r"]:
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object("rig_leg" + side)
		bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
		bpy.context.active_object.name = "rig_toes" + side
		bpy.ops.object.mode_set(mode='POSE')	
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.armature.select_all(action='DESELECT')
		
		# thumb
		for b in auto_rig_datas.toes_thumb_ref_list + auto_rig_datas.toes_thumb_control_list:
			select_edit_bone(b + side)	
		
		# save the foot(toes_ref) matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.toes_thumb_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("toes_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_toes_thumb" + side
		bpy.data.objects["rig_toes" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
		# index
		for b in auto_rig_datas.toes_index_ref_list + auto_rig_datas.toes_index_control_list:
			select_edit_bone(b + side)	
		
		# save the hand matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.toes_index_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("toes_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_toes_index" + side
		bpy.data.objects["rig_toes" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
		# middle
		for b in auto_rig_datas.toes_middle_ref_list + auto_rig_datas.toes_middle_control_list:
			select_edit_bone(b + side)	
		
		# save the hand matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.toes_middle_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("toes_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_toes_middle" + side
		bpy.data.objects["rig_toes" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
		
		# ring
		for b in auto_rig_datas.toes_ring_ref_list + auto_rig_datas.toes_ring_control_list:
			select_edit_bone(b + side)	
		
		# save the hand matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.toes_ring_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("toes_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_toes_ring" + side
		bpy.data.objects["rig_toes" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
		# pinky
		for b in auto_rig_datas.toes_pinky_ref_list + auto_rig_datas.toes_pinky_control_list:
			select_edit_bone(b + side)	
		
		# save the hand matrix in a custom prop, used when appending it near to the hand later
		get_edit_bone(auto_rig_datas.toes_pinky_ref_list[0] + side)["arp_offset_matrix"] = get_edit_bone("toes_ref"+side).matrix.inverted()
		
		bpy.ops.armature.separate()
		armature_name = "rig_toes_pinky" + side
		bpy.data.objects["rig_toes" + side + ".001"].name = armature_name
		save_objects.append(armature_name)
		
	
	bpy.data.objects.remove(bpy.data.objects["rig_toes" + side], do_unlink=True)
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object("rig")	
	bpy.ops.object.mode_set(mode='EDIT')
	
	
	
	
	# Delete other objects
	for obj in bpy.data.objects:
		if not obj.name in save_objects and obj.name[:3] != "cs_":
			bpy.data.objects.remove(obj, do_unlink=True)
	
	
	# Delete any constraints dependency remaining between armatures
	for obj in bpy.data.objects:
		if obj.type == "ARMATURE":
			set_active_object(obj.name)
			bpy.ops.object.mode_set(mode='POSE')
			for b in obj.pose.bones:
				for cns in b.constraints:
					try:		
						if obj.name != "rig_spine":
							if cns.target == bpy.data.objects["rig_spine"]:
								cns.target = None
					except:
						pass
						
			# Delete invalid drivers from older dependenciespath			
			clean_drivers()
		
	# save the file
	addon_directory = os.path.dirname(os.path.abspath(__file__))		
	fp = addon_directory + "/armature_presets/modules.blend"
	
	bpy.ops.wm.save_as_mainfile(filepath=fp, copy=True)
	
	
	
def _import_picker(filepath, self, context):

	scn = bpy.context.scene 
	
	file = open(filepath, 'rU')
	file_lines = file.readlines()		 
	dict_string = str(file_lines[0])	 
	file.close()
   
	dict_bones = ast.literal_eval(dict_string)
	
	# Disable picker
	proxy_picker_state = False
	
	if len(scn.keys()) > 0:		
		if "Proxy_Picker" in scn.keys():
			proxy_picker_state = scn.Proxy_Picker.active	
			scn.Proxy_Picker.active	 = False
	
	# Save current mode
	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')
	
	# Save X-Mirror state
	xmirror_state = bpy.context.object.data.use_mirror_x
	bpy.context.object.data.use_mirror_x = False	
	
	
	# Add the picker bones if not there
	addon_directory = os.path.dirname(os.path.abspath(__file__))		
	base_filepath = addon_directory + "/picker.py"
	
	if bpy.context.active_object.data.edit_bones.get("Picker") == None: 
		_add_picker(self, context, base_filepath, False, True)	
	
	print("Import bones position...")
	
	for b in dict_bones:
		if bpy.context.active_object.data.edit_bones.get(b):
			ebone = get_edit_bone(b)
			ebone.head, ebone.tail, ebone.roll = dict_bones[b][0], dict_bones[b][1], dict_bones[b][2]
			
			pbone = get_pose_bone(b)
			
			if len(dict_bones[b][3]) > 0:
				for prop in dict_bones[b][3]:
					pbone[prop[0]] = prop[1]
			
		else:
			print(b, "not found in the selected armature, picker bones datas skipped.")
	
	
	# Add the picker background 
		# Delete the current objects
	for child in bpy.context.active_object.children:
		if "rig_ui" in child.name and child.type == "EMPTY":
			delete_children(child, "OBJECT")			
			break
			
	_add_picker(self, context, filepath, True, False)
		
	# Restore X-Mirror state
	bpy.context.object.data.use_mirror_x = xmirror_state	
		
	# Restore picker state
	if len(scn.keys()) > 0:		
		if "Proxy_Picker" in scn.keys():
			scn.Proxy_Picker.active = proxy_picker_state
	
	# Restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
	bpy.ops.object.mode_set(mode=current_mode)
	
	
	
def _export_picker(filepath, self, context):
	
	scn = bpy.context.scene	  
	
	if bpy.context.active_object.data.bones.get("Picker"):
	
		# Add extension to file name
		if filepath[-3:] != ".py":
			filepath += ".py"
			
		file = open(filepath, "w", encoding="utf8", newline="\n")
		dict = {}	
		
		# Save current mode
		current_mode = bpy.context.mode
		bpy.ops.object.mode_set(mode='EDIT')
		
		# Get picker bones
		
			# Save displayed layers
		_layers = [bpy.context.active_object.data.layers[i] for i in range(0,32)]	

			# Display all layers
		for i in range(0,32):
			bpy.context.active_object.data.layers[i] = True

		# Select picker children bones
		bpy.ops.armature.select_all(action='DESELECT')		
		bpy.context.scene.update()	
		bpy.context.active_object.data.edit_bones.active = get_edit_bone("Picker")	
		bpy.ops.armature.select_similar(type='CHILDREN')	
		
		picker_bones = [ebone for ebone in bpy.context.active_object.data.edit_bones if ebone.select]
		
		def listify(vector):
			return [vector[0], vector[1], vector[2]]
		
		# Write bones datas
		for b in picker_bones:
			
			bone_grp = ""
			bone_shape = ""
			pbone = get_pose_bone(b.name)
			prop_list = []
			
			if len(pbone.keys()) > 0:				
				for i in pbone.keys():
					prop_list.append([i, pbone[i]])
				
			if pbone.bone_group:
				bone_grp = pbone.bone_group.name
			if pbone.custom_shape:
				bone_shape = pbone.custom_shape.name
					
			# dict: 0 head, 1 tail, 2 roll, 3 properties,  4 bone group, 5 bone shape
			dict[b.name] = [listify(b.head), listify(b.tail), b.roll, prop_list, bone_grp, bone_shape]		
						
			
		
		file.write(str(dict)) 
			
		# Write object datas
		if bpy.data.objects.get("rig_ui"):
			obj_dict = {}
			for obj in bpy.data.objects["rig_ui"].children:
				mesh_datas = None
				text_datas = []
				empty_datas = []
				
				if obj.type == "MESH":
					vert_list = [(v.co[0], v.co[1], v.co[2]) for v in obj.data.vertices]
					edge_list = [(e.vertices[0], e.vertices[1]) for e in obj.data.edges]
					poly_list = []					
					for p in obj.data.polygons:
						v_list = [v for v in p.vertices]
						poly_list.append(tuple(v_list))					
					mesh_datas = (vert_list, edge_list, poly_list)
					
				if obj.type == "FONT":
					font_text = obj.data.body
					font_size = obj.data.size
					font_align = obj.data.align_x
					text_datas = (font_text, font_size, font_align)
					
				if obj.type == "EMPTY":
					empty_type = obj.empty_draw_type
					empty_img_offset = [obj.empty_image_offset[0], obj.empty_image_offset[1]]
					empty_img_path = ""
					try:
						empty_img_path = obj.data.filepath
					except:
						pass
					empty_datas = [empty_type, empty_img_offset, empty_img_path]
					
				# dict: 0 loc, 1 rot, 2 scale, 3 type, 4 mesh datas, 5 text datas, 6 empty datas
				obj_dict[obj.name] = [[obj.location[0], obj.location[1], obj.location[2]], [obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]], [obj.scale[0], obj.scale[1], obj.scale[2]], obj.type, mesh_datas, text_datas, empty_datas]
			
			file.write("\n" + str(obj_dict)) 
			
			
		# Close file
		file.close()
		
		# Restore layers
		for i in range(0,32):			
			bpy.context.active_object.data.layers[i] = _layers[i]
		
		# Restore saved mode	   
		if current_mode == 'EDIT_ARMATURE':
			current_mode = 'EDIT'
		bpy.ops.object.mode_set(mode=current_mode)
	 
		
		print("Picker saved")
		
	else:
		self.report({"ERROR"}, "No picker found")

def _add_picker(self, context, filepath, with_background, with_bones):

	print("\nGenerating picker panel...")

	scn = bpy.context.scene
	picker_generated = False	
		
	file = open(filepath, 'rU')
	print("Importing from file:", filepath)
	file_lines = file.readlines()		 
	dict_bones_string = str(file_lines[0])	 
	dict_obj_string = str(file_lines[1])	 
	file.close()
   
	dict_bones = ast.literal_eval(dict_bones_string)
	dict_obj = ast.literal_eval(dict_obj_string)
		
	# Disable picker
	proxy_picker_state = False
	
	if len(scn.keys()) > 0:		
		proxy_picker_is_valid = True
		try:
			scn.Proxy_Picker
		except:
			proxy_picker_is_valid = False
			
		if proxy_picker_is_valid:
			proxy_picker_state = scn.Proxy_Picker.active	
			scn.Proxy_Picker.active	 = False
	
	# Save current mode
	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')

	# Save X-Mirror state
	xmirror_state = bpy.context.object.data.use_mirror_x
	bpy.context.object.data.use_mirror_x = False
	
	
	if with_bones: 
		if bpy.context.active_object.data.bones.get("Picker") == None:
			print("Adding picker bones...") 
		
			# Create the main picker group bone
			print("Create the 'Picker' bone")
			pickerb = bpy.context.active_object.data.edit_bones.new("Picker")		
			pickerb.head = [0,0,0]
			pickerb.tail = [0,0,1]	
			bpy.ops.object.mode_set(mode='POSE')	
			bpy.ops.object.mode_set(mode='EDIT')

			# get the limbs
			limb_sides.get_multi_limbs()
		
				# Set layers
			get_edit_bone("Picker").layers[23] = True
			for i, l in enumerate(get_edit_bone("Picker").layers):
				if i != 23:
					get_edit_bone("Picker").layers[i] = False
			
			# Save displayed layers
			_layers = [bpy.context.active_object.data.layers[i] for i in range(0,32)]	

			# Display all layers
			for i in range(0,32):
				bpy.context.active_object.data.layers[i] = True
				
			
			print("Create bones...")
			bones_to_append = ['c_pos_proxy', 'c_traj_proxy', 'layer_disp_main', 'layer_disp_second', 'c_picker_reset']
			
				# morph buttons
			for b in dict_bones:
				if 'c_morph_' in b:
					bones_to_append.append(b)
			
				# legs
			for side in limb_sides.leg_sides:
				if not "dupli" in side:
					for leg_bone_cont in auto_rig_datas.leg_control:
						bname = leg_bone_cont + side
						if get_edit_bone(bname):
							bones_to_append.append(leg_bone_cont + '_proxy' + side)
							
				# arms
			for side in limb_sides.arm_sides:
				if not "dupli" in side:
					for arm_bone_cont in auto_rig_datas.arm_control + auto_rig_datas.fingers_control:
						bname = arm_bone_cont + side
						if get_edit_bone(bname):
							bones_to_append.append(arm_bone_cont + '_proxy' + side)

				# spine
			for side in limb_sides.spine_sides:
				if not "dupli" in side:
					for spine_bone_cont in auto_rig_datas.spine_control:
						bname = spine_bone_cont[:-2] + side
						if get_edit_bone(bname):
							if "_proxy" in spine_bone_cont:
								continue
							bones_to_append.append(spine_bone_cont[:-2] + '_proxy' + side)
							print("appended", spine_bone_cont[:-2] + '_proxy' + side)
							
				# neck			
			for neck_bone_cont in auto_rig_datas.neck_control:
				bname = neck_bone_cont
				if get_edit_bone(bname):
					bones_to_append.append(bname[:-2] + '_proxy.x')
					print("appended", neck_bone_cont[:-2] + '_proxy.x')
		
				# head
			for side in limb_sides.head_sides:
				if not "dupli" in side:
					for head_bone_cont in auto_rig_datas.head_control + auto_rig_datas.facial_control:
						bname = ''
						proxy_name = ''
						
						if '.x' in head_bone_cont:
							bname = head_bone_cont[:-2] + side
							proxy_name = head_bone_cont[:-2] + '_proxy'
							
							if get_edit_bone(bname):
								bones_to_append.append(proxy_name + side)
						else:
							for s in ['.l', '.r']:
								bname = head_bone_cont + s
								proxy_name = head_bone_cont + '_proxy'
								if get_edit_bone(bname):
									bones_to_append.append(proxy_name + s)						
						
							
							
			
			for b in bones_to_append:
				
				bpy.ops.object.mode_set(mode='EDIT')
				ebone = None
				
				if bpy.context.active_object.data.edit_bones.get(b):
					ebone = get_edit_bone(b)			
				else:
					# create a new bone
					ebone = bpy.context.active_object.data.edit_bones.new(b)							
					
				ebone.parent = get_edit_bone("Picker")			
				
				# Set transforms
				ebone.head, ebone.tail, ebone.roll = dict_bones[b][0], dict_bones[b][1], dict_bones[b][2]	
				ebone.use_deform = False
				
				# Set properties and shapes
				bpy.ops.object.mode_set(mode='POSE')
				pbone = get_pose_bone(b)			
				
				if len(dict_bones[b][3]) > 0:
					for prop in dict_bones[b][3]:
						pbone[prop[0]] = prop[1]
						
				# Old old file retro-compatibility -Check the custom shape is in the scene, otherwise append it from the template file
				if len(pbone.keys()) > 0:
					if "normal_shape" in pbone.keys():
						if bpy.data.objects.get(pbone["normal_shape"]) == None:
							obj_to_append = [pbone["normal_shape"]]#, pbone["normal_shape"] + "_sel"]
							append_from_arp(nodes = obj_to_append, type = "object")
							print("Appended custom shape:", obj_to_append)
							
				# Custom shape
				if bpy.data.objects.get(dict_bones[b][5]):				
					pbone.custom_shape = bpy.data.objects[dict_bones[b][5]]
					
					# eyebrows have larger scale
					if "c_eyebrow_full" in pbone.name:
						pbone.custom_shape_scale = 4.0
					
				#Fix the reset button since there is no arp_layer assign
				if "c_picker_reset" in pbone.name:
					pbone["arp_layer"] = 16
					
					# Check if the reset script is in scene, otherwise append it
					if "button" in pbone.keys():						
						if bpy.data.texts.get(pbone["button"]) == None:
							append_from_arp(nodes = pbone["button"], type = "text")
							
					
				# Set layers
				if len(pbone.keys()) > 0:
					if "proxy" in pbone.keys(): 
						if get_pose_bone(pbone["proxy"]):
							proxy_bone = get_pose_bone(pbone["proxy"])						
				
							for i, l in enumerate(pbone.bone.layers):
								pbone.bone.layers[i] = proxy_bone.bone.layers[i]	

					# Make sure buttons are in the layer 16
					if "arp_layer" in pbone.keys():
						if pbone["arp_layer"] == 16:
							pbone.bone.layers[16] = True
							for i, l in enumerate(pbone.bone.layers):
								if i != 16:							
									pbone.bone.layers[i] = False
								
									
							
				# Set group colors			
				try:
					pbone.bone_group = bpy.context.active_object.pose.bone_groups[dict_bones[b][4]]
				except:
					print('Bone group "body ' + dict_bones[b][4] + ' not found')			
			
			
			bpy.ops.object.mode_set(mode='EDIT')
			_set_picker_spine()
			
			
			# Multi limb support	
			multi_limb_support = True
			
			if multi_limb_support:
				multi_ref_list = []		
				dupli_list = ["shoulder_ref_dupli", "thigh_ref_dupli", "thumb1_ref_dupli", "index1_ref_dupli", "middle1_ref_dupli", "ring1_ref_dupli", "pinky1_ref_dupli"]
				bpy.ops.object.mode_set(mode='EDIT') 
				
				for bone in bpy.context.active_object.data.edit_bones:
					for b in dupli_list:
						if b in bone.name:				
							multi_ref_list.append(bone.name)
				
				# Duplicate picker bones		
				for multi in multi_ref_list:
					print("Multi", multi)
					side = multi[-2:]			
					suffix = multi.split("_dupli_")[1][:-2]
					
					bpy.ops.object.mode_set(mode='EDIT') 
					bpy.ops.armature.select_all(action='DESELECT')
				
						# Select	
					current_limb = None
					if "shoulder" in multi:
						current_limb = auto_rig_datas.arm_control
					if "thigh" in multi:
						current_limb = auto_rig_datas.leg_control
						
					fingers = ["thumb", "index", "middle", "ring", "pinky"]
					for finger in fingers:
						
						if finger in multi and not "toes_" in multi:						
							current_limb = ["c_" + finger + "1_base", "c_" + finger + "1",	'c_' + finger + "2", 'c_' + finger + "3"]	
							break
							
						if finger in multi and "toes_" in multi:						
							current_limb = ["c_toes_" + finger + "1_base", "c_toes_" + finger + "1",  'c_toes_' + finger + "2", 'c_toes_' + finger + "3"]					
							break
					
						
					for bone1 in current_limb:
						if get_edit_bone(bone1 + '_proxy' + side):
							proxy_bone = get_edit_bone(bone1 + '_proxy' + side)
							if proxy_bone.layers[22] == False:#if not disabled (finger, toes...)							
								proxy_bone.select = True	
								
								
					bpy.ops.object.mode_set(mode='POSE')			
					bpy.ops.object.mode_set(mode='EDIT')#debug selection					
					
					coef = 1
					if side == '.r':
						coef = -1
					suffix_count = int(float(suffix))#move offset for each dupli, get number of the limb
				
					# Duplicate
					bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "constraint_axis":(False, False, False), "constraint_orientation":'LOCAL', "mirror":False, "proportional":'DISABLED'})
					print("Duplicate...")
					# Move
					for bone in bpy.context.selected_editable_bones:
						move_bone(bone.name, 0.26*coef*suffix_count, 0)
					
					# Rename
					for bone in bpy.context.selected_editable_bones:
						bone.name = bone.name[:-4].replace(side, '_dupli_' + suffix + side)				
						# Set proxy bone				
						get_pose_bone(bone.name)['proxy'] = get_pose_bone(bone.name)['proxy'].replace(side, '_dupli_' + suffix + side)
				
			# Restore layers
			for i in range(0,32):			
				bpy.context.active_object.data.layers[i] = _layers[i]
				
			picker_generated = True
			
		else:		
			print("Picker bones already loaded, nothing to load.")
		
			
			
			
	if with_background:
		rig_ui = None
		rig_collecs = [col for col in bpy.context.active_object.users_collection]
		
		
		
		for child in bpy.context.active_object.children:
			if "rig_ui" in child.name:				
				rig_ui = child		
				print("Found rig_ui")
				
		if rig_ui == None:
			
			print("Adding picker objects...")
			rig_ui = bpy.data.objects.new("rig_ui", None)			
			#scn.collection.objects.link(rig_ui)
			for col in rig_collecs:
				col.objects.link(rig_ui)
			rig_ui.empty_display_size = 0.01
			rig_ui.parent = bpy.context.active_object
			rig_ui.hide_select = True
			
		
				# Meshes and text objects
			for obj in dict_obj:
				# do not import ik-fk texts for now... requires drivers
				if not "label_ik" in obj and not "label_fk" in obj:
				
					if dict_obj[obj][3] == "MESH":
						new_mesh = bpy.data.meshes.new(obj)
						new_obj = bpy.data.objects.new(obj, new_mesh)	
						for col in rig_collecs:
							col.objects.link(new_obj)
						#scn.collection.objects.link(new_obj)
						#create verts and faces
						mesh_datas = dict_obj[obj][4]				
						new_mesh.from_pydata(mesh_datas[0], mesh_datas[1], mesh_datas[2])
						
						# set transforms
						new_obj.location = dict_obj[obj][0]
						new_obj.rotation_euler = dict_obj[obj][1]
						new_obj.scale = dict_obj[obj][2]
						
						# assign mat
						mat_ui = None
						
						for mat in bpy.data.materials:
							if "cs_ui" in mat.name:
								mat_ui = mat
								break
								
						if mat_ui == None:
							mat_ui = bpy.data.materials.new("cs_ui")
							mat_ui.diffuse_color = (0.2, 0.2, 0.2, 1.0)
							
						if mat_ui:
							new_obj.data.materials.append(mat_ui)
						else:
							print("UI material 'cs_ui' not found.")
				
					if dict_obj[obj][3] == "FONT":
						
						new_font = bpy.data.curves.new(obj+"_font", 'FONT')
						new_text = bpy.data.objects.new(obj, new_font)	
						for col in rig_collecs:
							col.objects.link(new_text)
						#scn.collection.objects.link(new_text)
						# set transforms
						new_text.location = dict_obj[obj][0]
						new_text.rotation_euler = dict_obj[obj][1]
						new_text.scale = dict_obj[obj][2]
						
						# text values
						new_text.data.body =  dict_obj[obj][5][0]
						new_text.data.size =  dict_obj[obj][5][1]
						new_text.data.align_x =	 dict_obj[obj][5][2]				
						
						# assign mat
						mat_text = None
						
						for mat in bpy.data.materials:
							if "cs_text" in mat.name:
								mat_text = mat
								break
								
						if mat_text == None:
							mat_text = bpy.data.materials.new("cs_text")
							mat_text.diffuse_color = (0.88, 0.88, 0.88, 1.0)
								
						if mat_text:
							new_text.data.materials.append(mat_text)
						else:
							print("Text material 'cs_text' not found.")
						
						# assign font						
						fnt = None
						
						for f in bpy.data.fonts:
							if "MyriadPro-Bold" in f.name:
								fnt = f
						
						if not fnt:
							append_from_arp(["MyriadPro-Bold"], "font")
						if fnt:							
							print("Assigning MYRIAD PRO font--------------------------------------")
							new_text.data.font = fnt 
							
						
					
					if dict_obj[obj][3] == "EMPTY":
						_draw_type = dict_obj[obj][6][0]
						_image_offset = dict_obj[obj][6][1]
						_img_path = dict_obj[obj][6][2]
						
						new_emp = bpy.data.objects.new(obj, None)
						new_emp.empty_draw_type = _draw_type
						new_emp.empty_image_offset = _image_offset
						
						# load image
						if _img_path != "":		
							try:
								img = bpy.data.images.load(_img_path)								
								new_emp.data = img
							except:
								print("Cannot load image path")								
						
						for col in rig_collecs:
							col.objects.link(new_emp)
						
						#scn.collection.objects.link(new_emp)
						# set transforms
						new_emp.location = dict_obj[obj][0]
						new_emp.rotation_euler = dict_obj[obj][1]
						new_emp.scale = dict_obj[obj][2]
						
							
					bpy.data.objects[obj].parent = rig_ui
					bpy.data.objects[obj].hide_select = True
					
			
			picker_generated = True
			
		else:		
			print("Picker background already loaded, nothing to load.")
			
									
		
		
	# Restore X-Mirror state
	bpy.context.object.data.use_mirror_x = xmirror_state
			
	
	# Restore picker state
	if len(scn.keys()) > 0:		
		proxy_picker_is_valid = True
		try:
			scn.Proxy_Picker
		except:
			proxy_picker_is_valid = False
			
		if proxy_picker_is_valid:
			scn.Proxy_Picker.active = proxy_picker_state
	
	# Restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
	bpy.ops.object.mode_set(mode=current_mode)		

	print("Picker loading finished.")	
	
	# has the picker been generated?
	return picker_generated
		

def _set_picker_spine():
	addon_directory = os.path.dirname(os.path.abspath(__file__))		
	filepath = addon_directory + "/picker.py"
	file = open(filepath, 'rU')
	file_lines = file.readlines()		 
	dict_bones_string = str(file_lines[0])	
	dict_bones = ast.literal_eval(dict_bones_string)	
	#dict_obj_string = str(file_lines[1])	 
	file.close()
   
	dict_bones = ast.literal_eval(dict_bones_string)
	
	# count current spine bones
	total_spine_found = 1
	for idx in range(1, 5):				
		spine_ref = get_data_bone('spine_0' + str(idx) + '_ref.x')
		if spine_ref:			
			total_spine_found += 1
	print("Spine bones found:", total_spine_found)
	
	# create additional picker spine bones
	root_master_name = 'c_root_master_proxy.x'
	root_name = 'c_root_proxy.x'
	root_bend_name = 'c_root_bend_proxy.x'	
	first_spine_name = 'c_spine_01_proxy.x'
	first_spine_bend_name = 'c_spine_01_bend_proxy.x'
	waist_bend_name = 'c_waist_bend_proxy.x'
	second_spine_name = 'c_spine_02_proxy.x'
	second_spine_bend_name = 'c_spine_02_bend_proxy.x'
	third_spine_name = 'c_spine_03_proxy.x'
	
	first_spine = get_edit_bone(first_spine_name)
	first_spine_bend = get_edit_bone(first_spine_bend_name)
	waist_bend = get_edit_bone(waist_bend_name)
	second_spine = get_edit_bone(second_spine_name)
	second_spine_bend = get_edit_bone(second_spine_bend_name)
	third_spine = get_edit_bone(third_spine_name)
		
	# create 
	bones_to_create = []
	
	if total_spine_found >= 1:
		if first_spine == None:
			bones_to_create.append(first_spine_name)
		if first_spine_bend == None:
			bones_to_create.append(first_spine_bend_name)
		if waist_bend == None:
			bones_to_create.append(waist_bend_name)
			
	if total_spine_found >= 2:
		if second_spine == None:
			bones_to_create.append(second_spine_name)
		if second_spine_bend == None:			
			bones_to_create.append(second_spine_bend_name)
	
	for b in bones_to_create:	
		bpy.ops.object.mode_set(mode='EDIT')
		picker_parent_bone = get_edit_bone("Picker")
		
		if picker_parent_bone:
			ebone = bpy.context.active_object.data.edit_bones.new(b)		
			ebone.parent = picker_parent_bone	
			
			# Set transforms
			ebone.head, ebone.tail, ebone.roll = dict_bones[b][0], dict_bones[b][1], dict_bones[b][2]	
			ebone.use_deform = False
			
			# Set properties and shapes
			bpy.ops.object.mode_set(mode='POSE')
			pbone = get_pose_bone(b)			
			
			if len(dict_bones[b][3]) > 0:
				for prop in dict_bones[b][3]:
					pbone[prop[0]] = prop[1]
					
			# Old old file retro-compatibility -Check the custom shape is in the scene, otherwise append it from the template file
			if len(pbone.keys()) > 0:
				if "normal_shape" in pbone.keys():
					if bpy.data.objects.get(pbone["normal_shape"]) == None:
						obj_to_append = [pbone["normal_shape"]]#, pbone["normal_shape"] + "_sel"]
						append_from_arp(nodes = obj_to_append, type = "object")
						print("Appended custom shape:", obj_to_append)
						
			# Custom shape
			if bpy.data.objects.get(dict_bones[b][5]):				
				pbone.custom_shape = bpy.data.objects[dict_bones[b][5]]
		
			# Set layers
			if len(pbone.keys()) > 0:
				if "proxy" in pbone.keys(): 
					if get_pose_bone(pbone["proxy"]):
						proxy_bone = get_pose_bone(pbone["proxy"])	
						for i, l in enumerate(pbone.bone.layers):
							pbone.bone.layers[i] = proxy_bone.bone.layers[i]						
						
			# Set group colors			
			try:
				pbone.bone_group = bpy.context.active_object.pose.bone_groups[dict_bones[b][4]]
			except:
				print('Bone group "body ' + dict_bones[b][4] + ' not found')			
				
						
	if total_spine_found > 3:
		bpy.ops.object.mode_set(mode='EDIT')
		first_spine = get_edit_bone(first_spine_name)
		second_spine = get_edit_bone(second_spine_name)
		third_spine = get_edit_bone(third_spine_name)		
		
		if third_spine == None and first_spine and second_spine:			
			print("adding spine03")		
			# set position
			third_spine = bpy.context.active_object.data.edit_bones.new(third_spine_name)			
			third_spine.head = second_spine.head + (second_spine.head - first_spine.head)
			third_spine.tail = third_spine.head + (second_spine.tail - second_spine.head)
			third_spine.roll = second_spine.roll
			third_spine.parent = get_edit_bone("Picker")
			third_spine.use_deform = False
			# set shape
			bpy.ops.object.mode_set(mode='POSE')
			third_spine_pbone = get_pose_bone(third_spine_name)
			third_spine_pbone["proxy"] = "c_spine_03.x"
			cs = bpy.data.objects.get("cs_solid_bar_01")			
			third_spine_pbone.custom_shape = cs			
			# set layers	
			set_layer_idx = 0
			third_spine_pbone.bone.layers[set_layer_idx] = True
			for i, l in enumerate(third_spine_pbone.bone.layers):
				if i != set_layer_idx:
					third_spine_pbone.bone.layers[i] = False
			# set group
			try:
				third_spine_pbone.bone_group = bpy.context.active_object.pose.bone_groups["body.x"]
			except:
				print('Bone group "' + 'body.x' + '" not found')		
		
			bpy.ops.object.mode_set(mode='EDIT')
	
	# delete
	else:
		bpy.ops.object.mode_set(mode='EDIT')
		third_spine = get_edit_bone(third_spine_name)
		if third_spine:
			bpy.context.active_object.data.edit_bones.remove(third_spine)
			
		second_spine = get_edit_bone(second_spine_name)
		second_spine_bend = get_edit_bone("c_spine_02_bend_proxy.x")		
		if total_spine_found <= 2:
			if second_spine: 
				bpy.context.active_object.data.edit_bones.remove(second_spine)
			if second_spine_bend:
				bpy.context.active_object.data.edit_bones.remove(second_spine_bend)
			
		first_spine = get_edit_bone(first_spine_name)
		first_spine_bend = get_edit_bone(first_spine_bend_name)	
		waist_bend = get_edit_bone(waist_bend_name)	
		
		if total_spine_found <=1:
			if first_spine:
				bpy.context.active_object.data.edit_bones.remove(first_spine)
			if  first_spine_bend:
				bpy.context.active_object.data.edit_bones.remove(first_spine_bend)
			if waist_bend:
				bpy.context.active_object.data.edit_bones.remove(waist_bend)
			

def _remove_picker():
	scn = bpy.context.scene
	
	# Save current mode
	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='POSE')
	
	
	# Delete rig_ui
	for child in bpy.context.active_object.children:
		if "cam_ui" in child.name:
			bpy.data.objects.remove(child)
			break
			
	for child in bpy.context.active_object.children:
		if "rig_ui" in child.name and child.type == "EMPTY":
			delete_children(child, "OBJECT")
			break
			
			
	# Delete proxy bones
	bpy.ops.object.mode_set(mode='EDIT')	
	delete_children(get_edit_bone("Picker"), "EDIT_BONE")
	
	
	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
	bpy.ops.object.mode_set(mode=current_mode)
		
		
	
 
def _mirror_picker():
	pbones = bpy.context.selected_pose_bones
	sides = ['.l', '.r']
	for pbone in pbones:
		if pbone.name[-2:] in sides:
			if pbone.name[-2:] == sides[0]:
				opposite = sides[1]
			else:
				opposite = sides[0]
				
			opposite_bone = bpy.context.active_object.pose.bones[pbone.name[:-2] + opposite]
			opposite_bone.location = pbone.location
			opposite_bone.location[0] *= -1
			opposite_bone.rotation_euler = pbone.rotation_euler
			opposite_bone.rotation_euler[1] *= -1
			opposite_bone.rotation_euler[2] *= -1
			opposite_bone.rotation_quaternion = pbone.rotation_quaternion
			opposite_bone.scale = pbone.scale
			
			
 
def _move_picker_layout(state, self):
	bpy.ops.object.mode_set(mode='POSE')	
	bpy.ops.pose.select_all(action='DESELECT')	

	if state == 'start':
		_value = False
	if state == "end":
		_value = True
		
	#disable picker
	try:
		bpy.context.scene.Proxy_Picker.active = _value
	except:
		pass
		
	if state == "end":
	#Bake the pose transforms to edit transforms
		#save the proxy pose bones transf in a dict
		pbone_dict = {}
		
		for pbone in bpy.context.active_object.pose.bones: 
			
				
			if is_proxy_bone(pbone):
				pbone_dict[pbone.name] = pbone.head.copy(), pbone.tail.copy(), pbone.matrix.copy()
				
		bpy.ops.object.mode_set(mode='EDIT')
		
		#disable mirror
		mirror_state = bpy.context.object.data.use_mirror_x
		bpy.context.object.data.use_mirror_x = False

		
		#apply to edit bones
		for pose_bone in pbone_dict:		
			ebone = bpy.context.active_object.data.edit_bones[pose_bone]
			ebone.matrix = pbone_dict[pose_bone][2]
			ebone.head = pbone_dict[pose_bone][0]
			ebone.tail= pbone_dict[pose_bone][1]
			
		#enable mirror state
		bpy.context.object.data.use_mirror_x = mirror_state
			
		#reset pose transf	
		bpy.ops.object.mode_set(mode='POSE')
		
		for pbone in bpy.context.active_object.pose.bones: 
			if is_proxy_bone(pbone):
				pbone.scale = [1.0,1.0,1.0]
				pbone.location = [0.0,0.0,0.0]
				pbone.rotation_euler = [0.0,0.0,0.0]
					
	
	#lock/unlock bone transforms
	for pbone in bpy.context.active_object.pose.bones:
		if is_proxy_bone(pbone):
			pbone.lock_location[0] = _value
			pbone.lock_location[1] = _value
			pbone.lock_location[2] = _value
			pbone.lock_scale[0] = _value
			pbone.lock_scale[1] = _value
			pbone.lock_scale[2] = _value
			pbone.rotation_mode = 'XYZ'
			pbone.lock_rotation[0] = _value
			pbone.lock_rotation[1] = _value
			pbone.lock_rotation[2] = _value
			
			#some propxy may have constraints
			if len(pbone.constraints) > 0:
				for cns in pbone.constraints:
					cns.mute = True
		
	#get all UI objects
	_mesh = None		
	objects_list = []
	rig_ui = None
	
		#get rig_ui
	for child in bpy.context.active_object.children:
		if 'rig_ui' in child.name:
			rig_ui = child		
	
		#get picker_background
	for obj in bpy.data.objects:
		if 'picker_background' in obj.name:
			objects_list.append(obj.name)
			break		
	
	if rig_ui == None:
		self.report({'INFO'}, "Rig_ui object not found, parent it to the armature.")
		return
		
	for child in rig_ui.children:
		if 'label' in child.name:
			objects_list.append(child.name)
		if '_mesh' in child.name:
			objects_list.append(child.name)
	
	#lock/unlock objects selection and transform
	for obj in objects_list:
		if bpy.data.objects.get(obj):
			child = bpy.data.objects[obj]		
			child.hide_select = _value
			child.lock_location[0] = _value
			child.lock_location[1] = _value
			child.lock_location[2] = _value
			child.lock_scale[0] = _value
			child.lock_scale[1] = _value
			child.lock_scale[2] = _value
			child.rotation_mode = 'XYZ'
			child.lock_rotation[0] = _value
			child.lock_rotation[1] = _value
			child.lock_rotation[2] = _value
		
		
			
	
			
			

def _screenshot_head_picker(filepath):
	
	current_obj = bpy.context.active_object
	
	directory = bpy.path.abspath(filepath)		 
   
	#define the image name		 
	#file_name = 'picker_screenshot'	 
	
	#save render pref
	base_res_x =  bpy.context.scene.render.resolution_x
	base_res_y =  bpy.context.scene.render.resolution_y
	base_percentage =  bpy.context.scene.render.resolution_percentage
	
	#set new render pref
	bpy.context.scene.render.resolution_x = 512*1.3
	bpy.context.scene.render.resolution_y = 512
	bpy.context.scene.render.resolution_percentage = 100
	
	#render
	bpy.context.space_data.show_only_render = True
	bpy.ops.render.opengl(view_context = True)
	bpy.context.space_data.show_only_render = False

	if directory[-4:] != '.png':
		directory += '.png'
	bpy.data.images['Render Result'].save_render(directory)		  
 
	#backup the render pref
	bpy.context.scene.render.resolution_x = base_res_x
	bpy.context.scene.render.resolution_y = base_res_y
	bpy.context.scene.render.resolution_percentage = base_percentage
	
	#delete current empty image
	if bpy.data.objects.get('picker_background'):
		bpy.data.objects.remove(bpy.data.objects['picker_background'], do_unlink=True)
	
	#create empty image
	if bpy.data.objects.get('picker_background') == None:
		empty_image = bpy.data.objects.new("picker_background", None)
		scene = bpy.context.scene	
		scene.collection.objects.link(empty_image)
		empty_image.empty_draw_type = 'IMAGE'
		empty_image.rotation_euler[0] = math.radians(90)
		img = bpy.data.images.load(directory)
		empty_image.data = img
		empty_image.empty_image_offset[0] = -0.5
		empty_image.empty_image_offset[1] = -1.0
		
		#get UI mesh object
		rig_ui = None
		for child in current_obj.children:
			if 'rig_ui' in child.name:
				rig_ui = child
				break
				
		for child in rig_ui.children:
			if '_mesh' in child.name:
				ui_mesh = child
				break
				
		#find upper vert and deeper verts
		up_val = ui_mesh.data.vertices[0].co[2]
		vert_up = ui_mesh.data.vertices[0]
		deep_val = ui_mesh.data.vertices[0].co[1]
		vert_deep = ui_mesh.data.vertices[0]	

		for vert in ui_mesh.data.vertices:
			if vert.co[2] > up_val:
				up_val = vert.co[2]
				vert_up = vert
				
			if vert.co[1] > deep_val:
				deep_val = vert.co[1]
				vert_deep = vert	
				
		vert_up_global = ui_mesh.matrix_world @ vert_up.co
		vert_deep_global = ui_mesh.matrix_world @ vert_deep.co
		
		ui_width = ui_mesh.dimensions[2]
		fac = 0.46
		empty_image.scale = [ui_width*fac, ui_width*fac, ui_width*fac]
		
		empty_image.location[0] = 0.0
		empty_image.location[1] = vert_deep_global[1] - (0.001 * ui_width)
		empty_image.location[2] = vert_up_global[2]
		
		if len(bpy.context.scene.keys()) > 0:
				if 'Proxy_Picker' in bpy.context.scene.keys():
					if bpy.context.scene.Proxy_Picker.active:
						empty_image.hide_select = True
						
		
		empty_image.location = rig_ui.matrix_world.inverted() @ empty_image.location
		empty_image.scale = rig_ui.matrix_world.inverted() @ empty_image.scale
		empty_image.parent = rig_ui
		
		
		current_mode = bpy.context.mode			

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		
		
		set_active_object(current_obj.name)
		bpy.ops.object.mode_set(mode=current_mode)
		
		
		
def _assign_colors():
	scene = bpy.context.scene
	
	#Controls bones color
	_bone_groups = bpy.context.active_object.pose.bone_groups
	
		#Right
	_bone_groups["body.r"].colors.normal = scene.color_set_right
	
	for i, channel in enumerate (_bone_groups["body.r"].colors.select):
		_bone_groups["body.r"].colors.select[i] = scene.color_set_right[i]+0.4
		
	for i, channel in enumerate (_bone_groups["body.r"].colors.active):
		_bone_groups["body.r"].colors.active[i] = scene.color_set_right[i]+0.5
	
	if _bone_groups.get("body.r_sel"):
		for i, channel in enumerate (_bone_groups["body.r_sel"].colors.normal):
			_bone_groups["body.r_sel"].colors.normal[i] = scene.color_set_right[i]+0.6
		
		

		#Middle
	_bone_groups["body.x"].colors.normal = scene.color_set_middle
	
	for i, channel in enumerate (_bone_groups["body.x"].colors.select):
		_bone_groups["body.x"].colors.select[i] = scene.color_set_middle[i]+0.4
		
	for i, channel in enumerate (_bone_groups["body.x"].colors.active):
		_bone_groups["body.x"].colors.active[i] = scene.color_set_middle[i]+0.5
		
	if _bone_groups.get("body.x_sel"):
		for i, channel in enumerate (_bone_groups["body.x_sel"].colors.normal):
			_bone_groups["body.x_sel"].colors.normal[i] = scene.color_set_middle[i]+0.6
		
		#Left
	_bone_groups["body.l"].colors.normal = scene.color_set_left
	
	for i, channel in enumerate (_bone_groups["body.l"].colors.select):
		_bone_groups["body.l"].colors.select[i] = scene.color_set_left[i]+0.4
		
	for i, channel in enumerate (_bone_groups["body.l"].colors.active):
		_bone_groups["body.l"].colors.active[i] = scene.color_set_left[i]+0.5
		
	if _bone_groups.get("body.l_sel"):
		for i, channel in enumerate (_bone_groups["body.l_sel"].colors.normal):
			_bone_groups["body.l_sel"].colors.normal[i] = scene.color_set_left[i]+0.6
			
			
	#Materials
	_materials = bpy.context.blend_data.materials
	
	for mat in _materials:
		#Right
		if 'cs_' in mat.name and "_blue" in mat.name:
			#Selection color
			if '_sel' in mat.name:				
				for i, channel in enumerate (mat.diffuse_color):
					if i == 3:
						break
					mat.diffuse_color[i] = scene.color_set_right[i]+0.4
			#Normal color
			else:
				for i, channel in enumerate (mat.diffuse_color):
					if i == 3:
						break
					mat.diffuse_color[i] = scene.color_set_right[i]
					
		#Middle
		if 'cs_' in mat.name and "_green" in mat.name:
			#Selection color
			if '_sel' in mat.name:				
				for i, channel in enumerate (mat.diffuse_color):
					if i == 3:
						break
					mat.diffuse_color[i] = scene.color_set_middle[i]+0.4
			#Normal color
			else:
				for i, channel in enumerate (mat.diffuse_color):
					if i == 3:
						break
					mat.diffuse_color[i] = scene.color_set_middle[i]
					
		
		#Left
		if 'cs_' in mat.name and "_red" in mat.name:
			#Selection color
			if '_sel' in mat.name:				
				for i, channel in enumerate (mat.diffuse_color):
					if i == 3:
						break
					mat.diffuse_color[i] = scene.color_set_left[i]+0.4
			#Normal color
			else:
				for i, channel in enumerate (mat.diffuse_color):
					if i == 3:
						break
					mat.diffuse_color[i] = scene.color_set_left[i]
					
		#Panel back
		if 'cs' in mat.name and '_ui' in mat.name:			
			mat.diffuse_color = (scene.color_set_panel[0], scene.color_set_panel[1], scene.color_set_panel[2], 1.0)
			mat.specular_color = (0,0,0)
			
		#Panel buttons
		if 'cs' in mat.name and 'button' in mat.name:			
			for i, channel in enumerate (mat.diffuse_color):
				if i == 3:
					break
				mat.diffuse_color[i] = scene.color_set_panel[i]+0.2
			mat.specular_color = (0,0,0)
			
		#Panel text
		if ('cs' in mat.name and '_black' in mat.name) or  ('cs' in mat.name and '_text' in mat.name) or ('test_blend' in mat.name):			
			mat.diffuse_color = (scene.color_set_text[0], scene.color_set_text[1], scene.color_set_text[2], 1.0)
			mat.specular_color = (0,0,0)
		
	
	
 
def _clean_skin():
	head_remove = ['c_arm_twist','arm_stretch', 'c_elbow_bend','forearm_stretch', 'c_arm_bend', 'forearm_twist']
	head_bones = ['head.x', 'c_skull_01.x', 'c_skull_02.x', 'c_skull_03.x', 'c_jawbone.x', 'c_eyelid_corner_02']
	sides = ['.l', '.r']
	obj = bpy.context.active_object
	
	for key in head_remove:									
			
		for side in sides:
			vgroup_exist = False
			try:
				obj.vertex_groups[key+side]									
				vgroup_exist = True
			except:
				print("Vertex Group not found for transfer: ", key)
		
			if vgroup_exist:
				for vgroup in head_bones:
					head_exist = False
					try:
						obj.vertex_groups[vgroup]									
						head_exist = True
					except:
						pass
						
					if head_exist:
						obj.modifiers.new("VWMix", 'VERTEX_WEIGHT_MIX')
						"""
						for i in range(0,15):
							bpy.ops.object.modifier_move_up(modifier="VWMix")
						"""
							
						bpy.context.active_object.modifiers["VWMix"].vertex_group_a = key + side
						bpy.context.active_object.modifiers["VWMix"].vertex_group_b = vgroup
						bpy.context.active_object.modifiers["VWMix"].mix_mode = 'SUB'
						bpy.context.active_object.modifiers["VWMix"].mix_set = 'ALL'
						bpy.context.active_object.modifiers["VWMix"].mask_constant = 1000

						bpy.ops.object.modifier_apply(apply_as='DATA', modifier="VWMix")
						
def delete_children(passed_node, type):
	
	if passed_node:
		if type == "OBJECT":
			parent_obj = passed_node
			children = []
		
			for obj in bpy.data.objects:
				if obj.parent:
					if obj.parent == parent_obj:
						children.append(obj)
						
						for _obj in children:
							for obj_1 in bpy.data.objects:
								if obj_1.parent:
									if obj_1.parent == _obj:
										children.append(obj_1)
			
			meshes_data = []
			
			for child in children:
				# store the mesh data for removal afterward
				if child.data:
					if not child.data.name in meshes_data:
						meshes_data.append(child.data.name)
						
				bpy.data.objects.remove(child, do_unlink=True, do_id_user=True, do_ui_user=True)
				
			for data_name in meshes_data:
				current_mesh = bpy.data.meshes.get(data_name)
				if current_mesh:					
					bpy.data.meshes.remove(current_mesh, do_unlink=True, do_id_user=True, do_ui_user=True)
				
				
			bpy.data.objects.remove(passed_node, do_unlink = True)
			
		if type == "EDIT_BONE":
			# Save current mode
			current_mode = bpy.context.mode 
				
			bpy.ops.object.mode_set(mode='EDIT')
			
			if bpy.context.active_object.data.edit_bones.get(passed_node.name):		
			
				# Save displayed layers
				_layers = [bpy.context.active_object.data.layers[i] for i in range(0,32)]	
			
				# Display all layers
				for i in range(0,32):
					bpy.context.active_object.data.layers[i] = True
			
				bpy.ops.armature.select_all(action='DESELECT')		
				bpy.context.scene.update()	
				bpy.context.active_object.data.edit_bones.active = get_edit_bone(passed_node.name)	
				bpy.ops.armature.select_similar(type='CHILDREN')	
				bpy.ops.armature.delete()
				
				for i in range(0,32):			
					bpy.context.active_object.data.layers[i] = _layers[i]
					
			#restore saved mode	   
			if current_mode == 'EDIT_ARMATURE':
				current_mode = 'EDIT'
			bpy.ops.object.mode_set(mode=current_mode)
		
		
def _delete_arp():	
	
	rig = bpy.context.active_object
	
	# make sure to unparent meshes from the armature
	for obj in bpy.data.objects:
		if obj.parent and obj.type	== "MESH":
			if obj.parent == rig:	
				obj_mat = obj.matrix_world.copy()
				obj.parent = None
				obj.matrix_world = obj_mat	
	
	
	# WARNING, DIRTY DEBUG 2.8
	# the rig_add armature cannot be deleted for some reasons in Blender 2.8 (missing referenced)
	# delete it first to fix it
	master = rig
	if rig.parent:
		master = rig.parent 
		if master.parent:
			master = master.parent
	
	for child in master.children:
		if "rig_add" in child.name and child.type == "ARMATURE":
			bpy.data.objects.remove(child, do_unlink=True, do_id_user=True, do_ui_user=True)
			break
	
	# find children collections
	link_collections = []	
	for col in master.users_collection:
		link_collections.append(col.name)		
		for _col in bpy.data.collections:
			for child in _col.children:
				if child == col and not _col in link_collections:
					link_collections.append(_col.name)
	
	if 'col' in locals():
		del col
		
	# find the cs collec
	cs_collec = None
	for col in bpy.data.collections:
		split_len = len(col.name.split('_'))
		if split_len > 0:
			if col.name.split('_')[split_len-1] == "cs":
				cs_collec = col
				link_collections.append(cs_collec.name)
				break
	
	# delete rig hierarchy
	delete_children(master, "OBJECT")
	
	# delete cs objects
	meshes_to_delete = []
	for cs_object in cs_collec.objects:
		# get the mesh name for deletion later
		cs_data_name = None
		if cs_object.data:
			cs_data_name = cs_object.data.name
			meshes_to_delete.append(cs_data_name)
			
		# delete the object
		bpy.data.objects.remove(cs_object, do_unlink=True, do_id_user=True, do_ui_user=True)			
	
	
	if 'col' in locals():
		del col
	if 'obj' in locals():
		del obj
	
	# update
	bpy.data.collections.update()	
	
	# delete collections
	for col_name in link_collections:
		col = bpy.data.collections.get(col_name)
		if col:
			# safety check, if some objects are left in the collection, make sure to assign them
			# to the scene collection before, if they're not in any other collec
			if len(col.objects) != 0:
				for ob in col.objects:
					if len(ob.users_collection) < 2:
						try:
							bpy.context.scene.collection.objects.link(ob)
						except:
							pass
			# delete the collec
			bpy.data.collections.remove(col)
	
			
	# update
	bpy.data.collections.update()
	# trigger the scene update by adding an empty and removing it, otherwise crashes after collection deletion
	bpy.ops.object.select_all(action='DESELECT')
	bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
	bpy.ops.object.delete(use_global=False)
	
	# Delete meshes at last, Blender crashes otherwise
	for cs_mesh_name in meshes_to_delete:
		cs_mesh = bpy.data.meshes.get(cs_mesh_name)
		if cs_mesh:				
			bpy.data.meshes.remove(cs_mesh)

	
def _append_arp(rig_type):
	context =  bpy.context
	scene = context.scene
	
	try:#if no object exists, error
		bpy.ops.object.mode_set(mode='OBJECT')
	except:
		pass
		
	addon_directory = os.path.dirname(os.path.abspath(__file__))		
	filepath = addon_directory + "/armature_presets/" + rig_type + ".blend"
	group_name = "char_rig"
	
	# Load the objects in the blend file datas
	with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
		data_to.objects = data_from.objects 
		data_to.collections = data_from.collections
		#data_to.groups = [group_name]
	
	
	#check - is it in local view mode?
	# local view removed from Blender 2.8? Disable it for now
	"""
	if context.space_data.lock_camera_and_layers == False:			
		context.space_data.lock_camera_and_layers = True
		context.scene.update()
	"""

	
	for collec in data_to.collections:	
		if len(collec.children) > 0:# only append the master collection
			bpy.context.scene.collection.children.link(collec)		
	
			
	bpy.context.space_data.overlay.show_relationship_lines = False
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object('rig')
	
 
def append_from_arp(nodes = None, type = None):
	
	context =  bpy.context
	scene = context.scene
	
	addon_directory = os.path.dirname(os.path.abspath(__file__))		
	filepath = addon_directory + "/armature_presets/" + "human.blend"
	
	if type == "object":
		#check - is it in local view mode?
		# local view removed from Blender 2.8? Disable it for now
		"""
		if context.space_data.lock_camera_and_layers == False:		
			context.space_data.lock_camera_and_layers = True			
			context.scene.update()
		"""
	
		# Clean the cs_ materials names (avoid .001, .002...)
		for mat in bpy.data.materials:
			if mat.name[:3] == "cs_":
				if mat.name[-3:].isdigit() and bpy.data.materials.get(mat.name[:-4]) == None:
					mat.name = mat.name[:-4]
		
		# make a list of current custom shapes objects in the scene for removal later
		cs_objects = [obj.name for obj in bpy.data.objects if obj.name[:3] == "cs_"]			
			
				
		# Load the objects data in the file
		with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
			data_to.objects = [name for name in data_from.objects if name in nodes]
			
		
		# Add the objects in the scene
		for obj in data_to.objects:		
			if obj:				
				# Link
				bpy.context.scene.collection.objects.link(obj)
				
				# Apply existing scene material if exists
				if len(obj.material_slots) > 0:
					mat_name = obj.material_slots[0].name
					found_mat = None
					
					for mat in bpy.data.materials:
						if mat.name == mat_name[:-4]:# substract .001, .002...
							found_mat = mat.name
							break
					
					# Assign existing material if already in file and delete the imported one
					if found_mat:	
						obj.material_slots[0].material = bpy.data.materials[found_mat]
						bpy.data.materials.remove(bpy.data.materials[mat_name], do_unlink=True)
					
				# If we append a custom shape
				if "cs_" in obj.name or "c_sphere" in obj.name: 
					cs_grp = bpy.data.objects.get("cs_grp")
					if cs_grp:
						# parent the custom shape
						obj.parent = cs_grp
						
						# assign to new collection
						assigned_collections = []
						for collec in cs_grp.users_collection:
							collec.objects.link(obj)					
							assigned_collections.append(collec)
						
						if len(assigned_collections) > 0:
							# remove previous collections
							for i in obj.users_collection:
								if not i in assigned_collections:
									i.objects.unlink(obj)
							# and the scene collection
							try:
								bpy.context.scene.collection.objects.unlink(obj)
							except:
								pass
				
				# If we append other objects,
				# find added/useless custom shapes and delete them
				else:
					for obj in bpy.data.objects:
						if obj.name[:3] == "cs_":
							if not obj.name in cs_objects:						
								bpy.data.objects.remove(obj, do_unlink=True)
								
					if 'obj' in locals():
						del obj
				
	if type == "text":
		# Load the objects data in the file
		with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
			data_to.texts = [name for name in data_from.texts if name in nodes]
		print("Loading text file:", data_to.texts)
		bpy.context.scene.update()
			
	if type == "font":
		# Load the data in the file
		with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
			data_to.fonts = [name for name in data_from.fonts if name in nodes]
		print("Loading font file:", data_to.fonts)
		bpy.context.scene.update()

		
def _set_transform_constraints():

	# set transform constraints factor according to current units	
	print("Set transform constraints values...")
	bpy.ops.object.mode_set(mode='POSE')	
	units_length = bpy.context.scene.unit_settings.scale_length
	
		# get the constraints transform values from file
	addon_directory = os.path.dirname(os.path.abspath(__file__))		
	filepath = addon_directory + "/auto_rig_datas_export.py"
	file = open(filepath, 'rU')
	file_lines = file.readlines()		 
	dict_string = str(file_lines[0])	 
	file.close()
   
		# set values
	dict_bones = ast.literal_eval(dict_string)
	for pbone_name in dict_bones:
		pbone = get_pose_bone(pbone_name)
		if pbone:
			cns = pbone.constraints.get(dict_bones[pbone_name][0])
			if cns:
				cns.from_min_x = dict_bones[pbone_name][1][0] * 1/units_length
				cns.from_max_x = dict_bones[pbone_name][1][1] * 1/units_length
				cns.from_min_y = dict_bones[pbone_name][1][2] * 1/units_length
				cns.from_max_y = dict_bones[pbone_name][1][3] * 1/units_length
				cns.from_min_z = dict_bones[pbone_name][1][4] * 1/units_length
				cns.from_max_z = dict_bones[pbone_name][1][5] * 1/units_length
				
				
		
def _reset_stretches():
	#store active pose
	bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
	bpy.ops.object.mode_set(mode='POSE')
	bpy.ops.pose.select_all(action='SELECT')
	bpy.ops.pose.copy()
		#need to reset the pose
	auto_rig_reset.reset_all()
		#reset stretches
	for pbone in bpy.context.active_object.pose.bones:
		try:							
			pbone.constraints["Stretch To"].rest_length = 0.0					
		except:
			pass
		
		#restore the pose
	bpy.ops.pose.paste(flipped=False)
	
	
def _add_fist_ctrl(fist_action):
	
	# get side
	sel_bone_name = bpy.context.selected_pose_bones[0].name
	
	side = ""	
	
	if not "_dupli_" in sel_bone_name:
		side = sel_bone_name[-2:]
	else:
		side = sel_bone_name[-12:]
	
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	hand_bone = get_edit_bone("hand" + side)
	
	# is the bone already created?
	if get_edit_bone("c_fist" + side):
		print("c_fist" + side + " already created.")
	
	# else create bone
	else:	
		new_bone = bpy.context.active_object.data.edit_bones.new("c_fist" + side)
		print("Created", "c_fist" + side)
		new_bone.head = hand_bone.head + (hand_bone.tail-hand_bone.head) * 1.0 + (hand_bone.tail - hand_bone.head).magnitude * hand_bone.z_axis
		new_bone.tail = new_bone.head + (hand_bone.tail - hand_bone.head)	
		new_bone.roll = 0.0 
		
	new_bone = get_edit_bone("c_fist" + side)
		
	# Set parent
	new_bone.parent = get_edit_bone(hand_bone.name)
	
	# Set layer
	bpy.ops.object.mode_set(mode='POSE')
	
	new_pbone = get_pose_bone("c_fist" + side)
	
	set_in_layer = 0
	
	for layer in range(0,32):		
		if layer == set_in_layer:
			new_pbone.bone.layers[layer] = True					
		else:
			new_pbone.bone.layers[layer] = False
		
	# Set rotation mode
	new_pbone.rotation_mode = 'XYZ'
	
	# Set transforms locks
	for i in range(0,3):
		new_pbone.lock_location[i] = True
		new_pbone.lock_rotation[i] = True
		
	# Set custom shape
	if bpy.data.objects.get("cs_fist") == None:
		obj_to_append = ["cs_fist"]
		append_from_arp(nodes = obj_to_append, type = 'object')
		
		# parent it to the "cs_grp" object
		for obj in obj_to_append:
			if bpy.data.objects.get("cs_grp"):
				bpy.data.objects[obj].parent = bpy.data.objects["cs_grp"]
				
				#link to collection					
				for collec in bpy.data.objects["cs_grp"].users_collection:				
					collec.objects.link(bpy.data.objects[obj])
		
			else:
				print("Could not find the cs_grp object to parent to")
		print("Appended cs_fist shapes")	
	
	if bpy.data.objects.get("cs_fist"):
		new_pbone.custom_shape = bpy.data.objects["cs_fist"]
	else:
		new_pbone.custom_shape = bpy.data.objects["cs_torus_04_rot2"]
		print("Custom shape not found.")
		
	new_pbone.bone.show_wire = True
	
	# Set color group			
	try:
		new_pbone.bone_group = bpy.context.active_object.pose.bone_groups["body"+side[-2:]]
	except:
		print('Bone group "body' + side[-2:] + ' not found')
	
	# Get fingers
	fingers = ["c_pinky", "c_ring", "c_middle", "c_index", "c_thumb"]
	base_fingers = ["c_pinky1_base", "c_ring1_base", "c_middle1_base", "c_index1_base", "c_thumb1_base"]
	fingers_def = []
	for finger in fingers:
		for i in range(0,4):
			if get_pose_bone(finger + str(i) + side):
				ctrl_finger = get_pose_bone(finger + str(i) + side)
				if ctrl_finger.bone.layers[0]:#if in layer 0, it's enabled
					fingers_def.append(ctrl_finger)
	
	for finger_base in base_fingers:
		if get_pose_bone(finger_base + side):
			ctrl_finger = get_pose_bone(finger_base + side)
			if ctrl_finger.bone.use_deform:
				fingers_def.append(ctrl_finger)
				
	# Print debug
	print("\nFingers list:")
	for i in fingers_def:
		print(i.name)
	
	print("")
	
	for pbone in fingers_def:
	
		# Constraint already created?
		create_cns = True
		
		if len(pbone.constraints) > 0:		
			for cns in pbone.constraints:
				if cns.type == "ACTION":
					print("Constraint already created")
					create_cns = False
					
		# Create constraints	
		if create_cns:				
			print("Create constraint")
			action_cns = get_pose_bone(pbone.name).constraints.new("ACTION")
						
			action_cns.target = bpy.context.active_object
			action_cns.subtarget = "c_fist" + side
			action_cns.action = bpy.data.actions[fist_action]
			action_cns.transform_channel = "SCALE_Y"
			action_cns.target_space = "LOCAL"
			action_cns.min = 1.0
			action_cns.max = 0.5
			action_cns.frame_start = 0
			action_cns.frame_end = 10
			
			
def _remove_fist_ctrl():
	
	# get side
	sel_bone_name = bpy.context.selected_pose_bones[0].name
	
	side = ""	
	
	if not "_dupli_" in sel_bone_name:
		side = sel_bone_name[-2:]
	else:
		side = sel_bone_name[-12:]
	
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	hand_bone = get_edit_bone("hand" + side)
	
	# is the bone already created?
	if get_edit_bone("c_fist" + side):		
		bpy.context.active_object.data.edit_bones.remove(get_edit_bone("c_fist" + side))
		print("Removed", "c_fist" + side)
		
	
	bpy.ops.object.mode_set(mode='POSE')	
	
	
	# Get fingers
	fingers = ["c_pinky", "c_ring", "c_middle", "c_index", "c_thumb"]
	fingers_def = []
	for finger in fingers:
		for i in range(0,4):
			if get_pose_bone(finger + str(i) + side):
				ctrl_finger = get_pose_bone(finger + str(i) + side)
				if ctrl_finger.bone.layers[0]:#if in layer 0, it's enabled
					fingers_def.append(ctrl_finger)
		
		# base finger
		if get_pose_bone(finger + "1_base" + side):
			base_finger = get_pose_bone(finger + "1_base" + side)
			if base_finger.bone.layers[0]:#if in layer 0, it's enabled
				fingers_def.append(base_finger)
	
	
	# Print debug
	print("\nFingers list:")
	for i in fingers_def:
		print(i.name)
	
	print("")
	
	for pbone in fingers_def:
	
		# Constraint already created?
		create_cns = True
		
		if len(pbone.constraints) > 0:		
			for cns in pbone.constraints:
				if cns.type == "ACTION":
					pbone.constraints.remove(cns)
					print("Deleted constraint")
				
	


def _mirror_custom_shape():
	
	armature_name = bpy.context.active_object.name
	armature = bpy.data.objects[armature_name]
	cs_grp = None
	cs_collec = []
	if bpy.context.selected_pose_bones[0].custom_shape:
		cshape = bpy.context.selected_pose_bones[0].custom_shape
		
		if cshape.parent:
			if "cs_grp" in cshape.parent.name:
				cs_grp = cshape.parent		
				
		for i in cshape.users_collection:
			cs_collec.append(i)
			
	
	for bone in bpy.context.selected_pose_bones:		
		bone_name = bone.name
		cs = bone.custom_shape
		side = bone.name[-2:]
		mirror_side = ""
		
		if side == '.l':
			mirror_side = ".r"
		if side == ".r":
			mirror_side = ".l"	
		if side == '_l':
			mirror_side = "_r"
		if side == "_r":
			mirror_side = "_l"	
			
		#if there's a mirrored bone
		if bpy.data.objects[armature_name].pose.bones.get(bone.name[:-2] + mirror_side):
			mirror_bone = bpy.data.objects[armature_name].pose.bones[bone.name[:-2] + mirror_side]
			pivot_mode = bpy.context.scene.tool_settings.transform_pivot_point
			
			if not 'cs_user_' in mirror_bone.custom_shape.name:	
				print("OOK")
				#create the cs
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')		
				
				bpy.ops.mesh.primitive_plane_add(size=1, view_align=True, enter_editmode=False, location=(-0, 0, 0.0), rotation=(0.0, 0.0, 0.0))
				mesh_obj = bpy.context.active_object
				mesh_obj.name = 'cs_user_' + mirror_bone.name	
				mesh_obj.data = cs.data
				bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
				mesh_obj.data.name = mesh_obj.name		
				
				#mirror it
				bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
				bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')

				bpy.ops.transform.mirror(constraint_axis=(True, False, False), orient_type='LOCAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.111671)
												
				bpy.ops.object.mode_set(mode='OBJECT')
				
				#assign to bone
				mirror_bone.custom_shape = mesh_obj
				
				# assign to collection and parent
				if cs_grp:			
					print("PARENTED")
					mesh_obj.parent = cs_grp
					for _col in mesh_obj.users_collection:
						_col.objects.unlink(mesh_obj)
					try:
						bpy.context.scene.collection.objects.unlink(mesh_obj)
					except:
						pass
					
					for col in cs_collec:
						col.objects.link(mesh_obj)
						print("LINK COLLEC", col.name, mesh_obj.name)
					
					
			else:
				for col in cs_collec:
					col.hide_viewport = False
					
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				bpy.data.objects[mirror_bone.custom_shape.name].hide_select = False#safety check
				set_active_object(mirror_bone.custom_shape.name)				
				mesh_obj = bpy.context.active_object
				mirror_bone.custom_shape.data = cs.data
				bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=False, obdata=True)
				try:
					mesh_obj.data.name = mesh_obj.name	
				except:
					print("error with", bone)
					
								
				#mirror it				
				bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
				bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.transform.mirror(constraint_axis=(True, False, False), orient_type='LOCAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.111671)				
				bpy.ops.object.mode_set(mode='OBJECT')
				
				for col in cs_collec:
					col.hide_viewport = True
				
			set_active_object(armature_name)
			bpy.ops.object.mode_set(mode='POSE')
			bpy.context.scene.tool_settings.transform_pivot_point = pivot_mode
	
	
def _edit_custom_shape():

	bone = bpy.context.active_pose_bone
	armature = bpy.context.active_object
	armature_name = armature.name
	cs = bpy.context.active_pose_bone.custom_shape
	cs_mesh = cs.data
	
	bpy.ops.object.posemode_toggle()

	# create new mesh data
	bpy.ops.mesh.primitive_plane_add(size=1, view_align=True, enter_editmode=False, location=(-0, 0, 0.0), rotation=(0.0, 0.0, 0.0))	
	mesh_obj = bpy.context.active_object
	mesh_obj.name = 'cs_user_' + bone.name	
	
	if not 'cs_user' in cs.name:#if the shape is not already user tweaked, create new object data		
		mesh_obj.data = cs_mesh.copy()
		mesh_obj.data.name = mesh_obj.name
		bone.custom_shape = mesh_obj
	else:#else just make an instance 
		mesh_obj.data= cs_mesh
		mesh_obj['delete'] = 1.0
	
	# store the current armature name in a custom prop
	mesh_obj['arp_armature'] = armature_name



	if bone.custom_shape_transform:
		bone_transf = bone.custom_shape_transform
		mesh_obj.matrix_world = armature.matrix_world @ bone_transf.matrix
	else:
		mesh_obj.matrix_world = armature.matrix_world @ bone.matrix
		
	mesh_obj.scale *= bone.custom_shape_scale
	mesh_obj.scale *= bone.length 
	
	bpy.ops.object.mode_set(mode='EDIT')

	
def _exit_edit_shape():

	bpy.ops.object.mode_set(mode='OBJECT')
	obj = bpy.context.active_object
	delete_obj = False
	
	if bpy.data.objects.get('cs_grp'):
		obj.parent = bpy.data.objects['cs_grp'] 
	
	arp_armature = None
	
	if len(obj.keys()) > 0:
		for key in obj.keys():
			if 'delete' in obj.keys():
				delete_obj = True
			if 'arp_armature' in key:
				arp_armature = obj['arp_armature']
	
	if delete_obj:
		bpy.ops.object.delete(use_global=False)
	else:		
		#assign to collection
		if arp_armature:
			if len(bpy.data.objects[arp_armature].users_collection) > 0:
				for collec in bpy.data.objects[arp_armature].users_collection:
					if len(collec.name.split('_')) == 1:
						continue
					if collec.name.split('_')[1] == "rig":
						cs_collec = bpy.data.collections.get(collec.name.split('_')[0] + '_cs')
						if cs_collec:
							# remove from root collection	
							if bpy.context.scene.collection.objects.get(obj.name):
								bpy.context.scene.collection.objects.unlink(obj)
							# remove from other collections
							for other_collec in obj.users_collection:
								other_collec.objects.unlink(obj)
							# assign to cs collection
							cs_collec.objects.link(obj)
							print("assigned to collec", cs_collec.name)
						else:
							print("cs collec not found")
					else:
						print("rig collec not found")
									
			else:
				print("Armature has no collection")
		else:
			print("Armature not set")
		
	if arp_armature:	
		set_active_object(arp_armature)
		bpy.ops.object.mode_set(mode='POSE')
				
	
def _import_colors(filepath):
	scene=bpy.context.scene 
	file = open(filepath, 'rU')
	file_lines = file.readlines()		 
	dict_string = str(file_lines[0])	 
	file.close()
   
	dict = ast.literal_eval(dict_string)
	
	scene.color_set_left = dict['left']
	scene.color_set_middle = dict['middle']
	scene.color_set_panel = dict['panel_back']
	scene.color_set_right = dict['right']
	scene.color_set_text = dict['panel_text']
				
def _export_colors(filepath):
	scene=bpy.context.scene	   
	
	#add extension
	if filepath[-3:] != ".py":
		filepath += ".py"
		
	file = open(filepath, "w", encoding="utf8", newline="\n")
	dict = {}	
	
	dict['right'] = [scene.color_set_right[0], scene.color_set_right[1], scene.color_set_right[2]]
	dict['middle'] = [scene.color_set_middle[0], scene.color_set_middle[1], scene.color_set_middle[2]]
	dict['left'] =	[scene.color_set_left[0], scene.color_set_left[1], scene.color_set_left[2]]
	dict['panel_back'] =  [scene.color_set_panel[0], scene.color_set_panel[1], scene.color_set_panel[2]]
	dict['panel_text'] =  [scene.color_set_text[0], scene.color_set_text[1], scene.color_set_text[2]]
	
	file.write(str(dict)) 
		
	# close file
	file.close()
 
def _export_ref(filepath):
	scene=bpy.context.scene	   
	
	#add extension
	if filepath[-3:] != ".py":
		filepath += ".py"
		
	file = open(filepath, "w", encoding="utf8", newline="\n")
	
	dict = {}
	
	for bone in bpy.context.active_object.data.edit_bones:
		if bone.layers[17]:
			dict[bone.name] = [bone.head[0], bone.head[1], bone.head[2]], [bone.tail[0], bone.tail[1], bone.tail[2]], bone.roll			   
	
	file.write(str(dict)) 
		
	# close file
	file.close()
	
def _import_ref(filepath):
	scene=bpy.context.scene
	#file = open(bpy.path.abspath(file_path), 'rU')
	file = open(filepath, 'rU')
	file_lines = file.readlines()		 
	dict_string = str(file_lines[0])	 
	file.close()
   
	bone_dict = ast.literal_eval(dict_string)
	
	for bone in bpy.context.active_object.data.edit_bones:
		if bone.layers[17]:#ref bone layers
			try:
				bone.head, bone.tail, bone.roll = bone_dict[bone.name]
			except:
				print('Ref bone not in file:', bone.name)
	
 
 
def _update_armature(self, context):

	print("\nUpdating armature...............................................................")
	sides = ['.l', '.r']
	
	sel_armature = bpy.context.active_object
	
	# Clear the reference bones constraints
	bpy.ops.object.mode_set(mode='POSE')
	for b in bpy.context.active_object.pose.bones:
		if len(b.constraints) > 0:
			if b.bone.layers[17] and "_ref" in b.name:
				for cns in b.constraints:				
					b.constraints.remove(cns)
			
	
	# Refresh the rig_add
	rig_add = get_rig_add(sel_armature)
	if rig_add:		
		bpy.data.objects.remove(rig_add, do_unlink = True)
	
	rig_add = refresh_rig_add(sel_armature)			
	copy_bones_to_rig_add(sel_armature, rig_add)
	print("Rig add refreshed.")
	
	# Updating collections
	print("\nUpdating collections...")
	
	
		# assign to new collections, for rigs coming from Blender 2.79
	found_rig_collec = False
	rig_collec = ""
	found_cs_collec = False
	
		# are the rig and cs collections there?
	if len(sel_armature.users_collection) > 0:
		for col in sel_armature.users_collection:
			if	len(col.name.split('_')) > 1:
				if col.name.split('_')[1] == 'rig':
					found_rig_collec = True
					rig_collec = col.name
					print("	   rig collection found:", col.name)				
	
	cs_grp = bpy.data.objects.get("cs_grp")
	
	if not cs_grp:
		print("No cs_grp object in the scene")
		bpy.data.objects.new("cs_grp", None)
		bpy.context.scene.collection.objects.link(bpy.data.objects["cs_grp"])
		print("cs_grp created")
	
	cs_grp = bpy.data.objects.get("cs_grp") 
	if len(cs_grp.users_collection) > 0:
		for col in cs_grp.users_collection:
			if	len(col.name.split('_')) > 1:				
				if col.name.split('_')[1] == 'cs':
					found_cs_collec = True
					print("	   cs collection found:", col.name)
	
		
	# if only the rig collec is found, it's likely the obsolete "char_rig" group.
	# delete it
	if found_rig_collec and not found_cs_collec:
		print("	   rig collection is actually the obsolete rig group, delete it.")
		bpy.data.collections.remove(bpy.data.collections[rig_collec])
		found_rig_collec = False
	
	if not found_rig_collec:
		print("	   rig collection not found, creating...")
		collec_rig = bpy.data.collections.get("character1_rig")
		if not collec_rig:
			collec_rig = bpy.data.collections.new("character1_rig")
			bpy.context.scene.collection.children.link(collec_rig)
			print("	   new collection created:", collec_rig.name)
			
		# get the master parent
		master_parent = sel_armature
		reached_top = False
		while reached_top == False:
			if master_parent.parent:
				master_parent = master_parent.parent
			else:
				reached_top = True
		
		print("	   rig master:", master_parent.name)
		
		# get the whole rig hierarchy
		rig_hierarchy = [master_parent]
		
		for obj in bpy.data.objects:
			if obj.parent:
				if obj.parent == master_parent:				
					rig_hierarchy.append(obj)
					
					for _obj in rig_hierarchy:
						for obj_1 in bpy.data.objects:	
							if obj_1.parent:
								if obj_1.parent == _obj:
									rig_hierarchy.append(obj_1)
			
		for child in rig_hierarchy:
			try:
				collec_rig.objects.link(child)
				print("	   linking child", child.name)
			except:
				print(child.name, "is already in the collection", collec_rig.name)
				
			# remove from other collec	
			for _subcol in child.users_collection:
				if _subcol != collec_rig:
					_subcol.objects.unlink(child)
			try:
				bpy.context.scene.collection.objects.unlink(child)
			except:
				pass

	
	
	if not found_cs_collec:
		print("	   cs collection not found, creating...")
		collec_cs = bpy.data.collections.get("character1_cs")
		if not collec_cs:
			collec_cs = bpy.data.collections.new("character1_cs")
			bpy.context.scene.collection.children.link(collec_cs)
			print("	   new collection created:", collec_cs.name)
			
		# get the master parent
		master_parent = bpy.data.objects["cs_grp"]	
		
		# get the whole rig hierarchy
		cs_hierarchy = [master_parent]
		
		for obj in bpy.data.objects:		
			if obj.parent:
				if obj.parent == master_parent:
					cs_hierarchy.append(obj)				
			
		for child in cs_hierarchy:	
			
			try:
				collec_cs.objects.link(child)
			except:
				pass
			# remove from other collec	
			for _subcol in child.users_collection:
				if _subcol != collec_cs:
					_subcol.objects.unlink(child)
			try:
				bpy.context.scene.collection.objects.unlink(child)
			except:
				pass
						
		# hide it
		collec_cs.hide_viewport = True
		collec_cs.hide_render = True
	
	# make sure the rig collections are children of a master rig collection
	collections_to_check = ["character1_rig", "character1_cs"]
	
	for col_name in collections_to_check:
		col = bpy.data.collections.get(col_name)
		if col:
			for child_col in bpy.context.scene.collection.children:# the collection is at the root level
				if child_col == col:
					master_col = bpy.data.collections.get("character1")
					
					if not master_col:
						new_col = bpy.data.collections.new("character1")
						bpy.context.scene.collection.children.link(new_col)
						print("	   Created new collection:", "character1")
						
					new_col.children.link(col)
					bpy.context.scene.collection.children.unlink(col)
					
					
		# delete obsolete "char_rig" group/collection from 2.79 files
	char_rig_collec = bpy.data.collections.get("char_rig")
	if char_rig_collec:
		print("	   Delete collection", char_rig_collec.name)
		bpy.data.collections.remove(char_rig_collec)
		
	print("Collections updated.")
	
	
	# Multi limb support
	limb_sides.get_multi_limbs()	
	arm_sides = limb_sides.arm_sides
	leg_sides = limb_sides.leg_sides
	head_sides = limb_sides.head_sides	
	
	
	def replace_var(dr):
		for v1 in dr.driver.variables:					
			if 'c_ikfk_arm' in v1.targets[0].data_path:							  
				v1.targets[0].data_path = v1.targets[0].data_path.replace('c_ikfk_arm', 'c_hand_ik')
				
			if 'c_ikfk_leg' in v1.targets[0].data_path:								  
				v1.targets[0].data_path = v1.targets[0].data_path.replace('c_ikfk_leg', 'c_foot_ik')
	
	
	#Save current mode
	current_mode = bpy.context.mode
	
	# Clean drivers
	print("Cleaning drivers...")	
	clean_drivers()
	print("Cleaned.")
	
	
	bpy.ops.object.mode_set(mode='EDIT')

	
	#Active all layers
		#save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):  
		layers_select.append(_layers[i])

	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True 
		
	# disable the proxy picker to avoid bugs
	try:	   
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass
	
	need_update = False
	
	# Delete the disabled/hidden bones from previous versions
	found_facial = False
	found_neck = False
	found_legs = []
	found_arms = []
	for b in bpy.context.active_object.data.edit_bones:
		if b.layers[22] and not "_proxy" in b.name and not b.layers[17] and not b.layers[1]:
			if b.name == "jaw_ref.x":
				found_facial = True
			if b.name == "c_neck.x":
				found_neck = True
			if "c_foot_ik" in b.name:
				found_legs.append(b.name[-2:])
			if "c_hand_ik" in b.name:
				found_arms.append(b.name[-2:])
				
			bpy.context.active_object.data.edit_bones.remove(b)			
			
			
		# remove other facial hidden bones
	if found_facial:		
		set_facial(False)
	
	if found_neck:
		for b in auto_rig_datas.neck_bones:
			eb = get_edit_bone(b)
			if eb:
				bpy.context.active_object.data.edit_bones.remove(eb)
				
	if len(found_legs) > 0:
		for s in found_legs:
			for b in auto_rig_datas.leg_bones:
				eb = get_edit_bone(b+s)
				if eb:
					bpy.context.active_object.data.edit_bones.remove(eb)
					
	if len(found_arms) > 0:
		for s in found_arms:
			for b in auto_rig_datas.arm_bones:
				eb = get_edit_bone(b+s)
				if eb:
					bpy.context.active_object.data.edit_bones.remove(eb)
		
	bpy.ops.object.mode_set(mode='POSE')
	
	#create the ik_fk property if necessary (update from older armature version)
	c_foot_ik = get_pose_bone("c_foot_ik.l")
	if c_foot_ik:
		if len(c_foot_ik.keys()) > 0:
			if not 'ik_fk_switch' in c_foot_ik.keys():
				need_update = True
				
				for side in leg_sides:			
					get_pose_bone("c_foot_ik" + side)["ik_fk_switch"] = get_pose_bone("c_ikfk_leg" + side)["ik_fk_switch"]
					foot_ik = get_pose_bone("c_foot_ik" + side)
					
					if foot_ik["_RNA_UI"]["ik_fk_switch"]["min"] != 0.0 and foot_ik["_RNA_UI"]["ik_fk_switch"]["max"] != 1.0:			
						get_pose_bone("c_foot_ik" + side)["_RNA_UI"] = {}	   
						get_pose_bone("c_foot_ik" + side)["_RNA_UI"]['ik_fk_switch'] = {"min":0.0,"max": 1.0, "soft_min":0.0,"soft_max":1.0}
						print("Changed limits of foot IK FK Switch property")
					
					
				for side in arm_sides:		
					get_pose_bone("c_hand_ik" + side)["ik_fk_switch"] = get_pose_bone("c_ikfk_arm" + side)["ik_fk_switch"]
					hand_ik = get_pose_bone("c_hand_ik" + side)
					
					if hand_ik["_RNA_UI"]['ik_fk_switch']['min'] != 0.0 and hand_ik["_RNA_UI"]['ik_fk_switch']['max'] != 1.0:
						get_pose_bone("c_hand_ik" + side)["_RNA_UI"] = {}	   
						get_pose_bone("c_hand_ik" + side)["_RNA_UI"]['ik_fk_switch'] = {"min":0.0,"max": 1.0, "soft_min":0.0,"soft_max":1.0}
						print("Changed limits of hand IK FK Switch property")
					
				
				
				# update drivers
				for obj in bpy.data.objects:
					try:
						drivers1 = obj.animation_data.drivers
						drivers2 = bpy.context.active_object.data.animation_data.drivers				
						
						for dr in drivers1:	   
							replace_var(dr)
									
						for dr in drivers2:	   
							replace_var(dr)		  
						
					except:
						pass
				print('....IK-FK Drivers updated')
		
		
	# Update armature data drivers to pose bone (hide -> scale) to solve the dependency problem when linking the armature into a scene	
	
	if bpy.context.active_object.data.animation_data:
		drivers2 = bpy.context.active_object.data.animation_data.drivers	
	
		for dr in drivers2:		
			if ".hide" in dr.data_path:
				# create the new ones on pose bones
				new_dr = bpy.context.active_object.animation_data.drivers.from_existing(src_driver=dr)
				dp = dr.data_path.replace("bones", "pose.bones")
				dp = dp.replace(".hide", ".custom_shape_scale")			
				new_dr.data_path = dp
				
				# invert the expression
				if new_dr.driver.expression == "1-var":
					new_dr.driver.expression = "var"
				if new_dr.driver.expression == "var":
					new_dr.driver.expression = "1-var"
					
				dp_string = dr.data_path[7:]	
				
				# delete the old one
				bpy.context.active_object.data.driver_remove(dr.data_path, -1)						
						
				# disable the hide
				get_data_bone(dp_string.partition('"')[0]).hide = False
				
			if "inherit_rotation" in dr.data_path:
				try:
					bpy.context.active_object.data.driver_remove(dr.data_path, -1)
				except:
					print("Unknown error when trying to delete a driver.")
				
	# Update shape scales driver curves... was set 0.1 instead of 1.0
	drivers_armature = bpy.context.active_object.animation_data.drivers
	blist = ["c_hand", "c_foot", "c_toes", "c_leg", "c_arm", "c_forearm", "c_thigh"]
	for dr in drivers_armature:
		for b in blist:
			if b in dr.data_path and "custom_shape_scale" in dr.data_path:			
				for key in dr.keyframe_points:
					if key.co[0] > 0.01 and key.co[0] < 0.99:
						key.co[0] = 1.0
						print("Updated driver curve of", dr.data_path)
						
				
	# Update IK-FK constraints drivers, set the first constraints influence in the stack always to 1.0 for better blend betwenn IK-FK	
	for dr in drivers_armature:
		if 'constraints["rotIK"].influence' in dr.data_path or 'constraints["ik_rot"].influence' in dr.data_path:
			if dr.driver.expression != "0":
				dr.driver.expression = "0"# 0 = 1 according to the driver curve
				print("Updated driver expression of", dr.data_path)
		
		if 'constraints["locIK"].influence' in dr.data_path and ('["forearm' in dr.data_path or '["leg' in dr.data_path):
			if dr.driver.expression != "0":
				dr.driver.expression = "0"
				print("Updated driver expression of", dr.data_path)
		
	# Make sure properties limits are corrects
	for side in arm_sides:		
		hand_ik = get_pose_bone("c_hand_ik" + side)		
		if hand_ik:
			if hand_ik["_RNA_UI"]['ik_fk_switch']['min'] != 0.0 and hand_ik["_RNA_UI"]['ik_fk_switch']['max'] != 1.0:
				get_pose_bone("c_hand_ik" + side)["_RNA_UI"] = {}	   
				get_pose_bone("c_hand_ik" + side)["_RNA_UI"]['stretch_length'] = {"min":0.2, "max": 4.0}
				get_pose_bone("c_hand_ik" + side)["_RNA_UI"]['auto_stretch'] = {"min":0.0, "max": 1.0}
				get_pose_bone("c_hand_ik" + side)["_RNA_UI"]['ik_fk_switch'] = {"min":0.0, "max": 1.0}
				print('Properties limits  of arms set')
	
		
	for side in leg_sides:		
		foot_ik = get_pose_bone("c_foot_ik" + side)		
		if foot_ik:
			if foot_ik["_RNA_UI"]["ik_fk_switch"]["min"] != 0.0 and foot_ik["_RNA_UI"]["ik_fk_switch"]["max"] != 1.0:		
				get_pose_bone("c_foot_ik" + side)["_RNA_UI"] = {}	   
				get_pose_bone("c_foot_ik" + side)["_RNA_UI"]['stretch_length'] = {"min":0.2, "max": 4.0}
				get_pose_bone("c_foot_ik" + side)["_RNA_UI"]['auto_stretch'] = {"min":0.0, "max": 1.0}
				get_pose_bone("c_foot_ik" + side)["_RNA_UI"]['ik_fk_switch'] = {"min":0.0, "max": 1.0}
				print('Properties limits of legs set')
	
	# Update arms and leg pole parent
	for side in leg_sides:
		if get_pose_bone("c_leg_pole" + side):
			pole = get_pose_bone("c_leg_pole" + side)
			
			# unparent			
			bpy.ops.object.mode_set(mode='EDIT')
			get_edit_bone("c_leg_pole" + side).parent = None
			bpy.ops.object.mode_set(mode='POSE')
			
			#create the properties
			if not "pole_parent" in pole.keys():
				if not "_RNA_UI" in pole.keys():
					pole["_RNA_UI"] = {}
					
				pole["pole_parent"] = 1				
				pole["_RNA_UI"]["pole_parent"] = {}
				pole["_RNA_UI"]["pole_parent"] = {"min": 0, "max":1, "default": 1, "description": "Pole parent"}	

			# Create the constraints
			cons = [None, None]
			if len(pole.constraints) > 0:
				for cns in pole.constraints:
					if cns.name == "Child Of_local":
						cons[0] = cns
					if cns.name == "Child Of_global":
						cons[1] = cns
						
				if cons[0] == None:
					cns1 = pole.constraints.new("CHILD_OF")
					cns1.name = "Child Of_local"
					cns1.target = bpy.context.active_object
					cns1.subtarget = "c_foot_ik" + side
					
				if cons[1] == None:
					cns2 = pole.constraints.new("CHILD_OF")
					cns2.name = "Child Of_global"
					cns2.target = bpy.context.active_object
					cns2.subtarget = "c_traj"
			
			else:				
				cns1 = pole.constraints.new("CHILD_OF")
				cns1.name = "Child Of_local"
				cns1.target = bpy.context.active_object
				cns1.subtarget = "c_foot_ik" + side
				
				cns2 = pole.constraints.new("CHILD_OF")
				cns2.name = "Child Of_global"
				cns2.target = bpy.context.active_object
				cns2.subtarget = "c_traj"
				
			# Create drivers			
			dr1 = bpy.context.active_object.driver_add('pose.bones["c_leg_pole' + side + '"].constraints["Child Of_local"].influence', -1)
			dr1.driver.expression = "var"
			if len(dr1.driver.variables) == 0:
				base_var = dr1.driver.variables.new()
			else:
				base_var = dr1.driver.variables[0]
			base_var.type = 'SINGLE_PROP'
			base_var.name = 'var'
			base_var.targets[0].id = bpy.context.active_object
			base_var.targets[0].data_path = 'pose.bones["c_leg_pole' + side + '"].["pole_parent"]'
			
			dr2 = bpy.context.active_object.driver_add('pose.bones["c_leg_pole' + side + '"].constraints["Child Of_global"].influence', -1)
			dr2.driver.expression = "1 - var"
			if len(dr2.driver.variables) == 0:
				base_var = dr2.driver.variables.new()
			else:
				base_var = dr2.driver.variables[0]
			base_var.type = 'SINGLE_PROP'
			base_var.name = 'var'
			base_var.targets[0].id = bpy.context.active_object
			base_var.targets[0].data_path = 'pose.bones["c_leg_pole' + side + '"].["pole_parent"]'
	
	for side in arm_sides:
		if get_pose_bone("c_arms_pole" + side):
			pole = get_pose_bone("c_arms_pole" + side)
			
			# unparent			
			bpy.ops.object.mode_set(mode='EDIT')
			get_edit_bone("c_arms_pole" + side).parent = None
			bpy.ops.object.mode_set(mode='POSE')
			
			#create the properties
			if not "pole_parent" in pole.keys():
				if not "_RNA_UI" in pole.keys():
					pole["_RNA_UI"] = {}
					
				pole["pole_parent"] = 1				
				pole["_RNA_UI"]["pole_parent"] = {}
				pole["_RNA_UI"]["pole_parent"] = {"min": 0, "max":1, "default": 1, "description": "Pole parent"}	

			# Create the constraints
			cons = [None, None]
			if len(pole.constraints) > 0:
				for cns in pole.constraints:
					if cns.name == "Child Of_local":
						cons[0] = cns
					if cns.name == "Child Of_global":
						cons[1] = cns
						
				if cons[0] == None:
					cns1 = pole.constraints.new("CHILD_OF")
					cns1.name = "Child Of_local"
					cns1.target = bpy.context.active_object
					cns1.subtarget = "c_root_master.x"
					
				if cons[1] == None:
					cns2 = pole.constraints.new("CHILD_OF")
					cns2.name = "Child Of_global"
					cns2.target = bpy.context.active_object
					cns2.subtarget = "c_traj"
			
			else:				
				cns1 = pole.constraints.new("CHILD_OF")
				cns1.name = "Child Of_local"
				cns1.target = bpy.context.active_object
				cns1.subtarget = "c_root_master.x"
				
				cns2 = pole.constraints.new("CHILD_OF")
				cns2.name = "Child Of_global"
				cns2.target = bpy.context.active_object
				cns2.subtarget = "c_traj"
				
			# Create drivers			
			dr1 = bpy.context.active_object.driver_add('pose.bones["c_arms_pole' + side + '"].constraints["Child Of_local"].influence', -1)
			dr1.driver.expression = "var"
			if len(dr1.driver.variables) == 0:
				base_var = dr1.driver.variables.new()
			else:
				base_var = dr1.driver.variables[0]
			base_var.type = 'SINGLE_PROP'
			base_var.name = 'var'
			base_var.targets[0].id = bpy.context.active_object
			base_var.targets[0].data_path = 'pose.bones["c_arms_pole' + side + '"].["pole_parent"]'
			
			dr2 = bpy.context.active_object.driver_add('pose.bones["c_arms_pole' + side + '"].constraints["Child Of_global"].influence', -1)
			dr2.driver.expression = "1 - var"
			if len(dr2.driver.variables) == 0:
				base_var = dr2.driver.variables.new()
			else:
				base_var = dr2.driver.variables[0]
			base_var.type = 'SINGLE_PROP'
			base_var.name = 'var'
			base_var.targets[0].id = bpy.context.active_object
			base_var.targets[0].data_path = 'pose.bones["c_arms_pole' + side + '"].["pole_parent"]'
			
	# Update Fingers Grasp
	for side in arm_sides:
		if get_pose_bone("c_hand_fk" + side):
			try:
				get_pose_bone("c_hand_fk" + side)["fingers_grasp"]
			except KeyError:
				print("Adding Fingers Grasp...")
			
				#create properties
				get_pose_bone("c_hand_fk" + side)["fingers_grasp"] = 0.0
				get_pose_bone("c_hand_fk" + side)["_RNA_UI"]["fingers_grasp"] = {}
				get_pose_bone("c_hand_fk" + side)["_RNA_UI"]["fingers_grasp"] = {"min": -1.0, "max":2.0, "default": 0.0, "description": "Fingers grasp (bend all fingers)"}
				#create drivers
				drivers_armature = bpy.context.active_object.animation_data.drivers
				fingers_bend_all = ["thumb_bend_all", "index_bend_all", "middle_bend_all", "ring_bend_all", "pinky_bend_all"]			
				
				for driver in drivers_armature:				
					for finger in fingers_bend_all:
						if (finger + side) in driver.data_path:					
							dr = driver.driver
							if 'thumb' in finger:
								dr.expression = "-var - (var_001 * 0.5)"
							else:
								dr.expression = "-var - var_001"
							base_var = dr.variables[0]
							new_var = dr.variables.new()
							new_var.type = 'SINGLE_PROP'
							new_var.name = 'var_001'
							new_var.targets[0].id = base_var.targets[0].id
							new_var.targets[0].data_path = 'pose.bones["c_hand_fk' + side + '"]["fingers_grasp"]'	
							
			
	

	# Update fingers rotation constraints to fix the cyclic dependency issue
	fingers_rot = ['c_thumb1_rot', 'c_index1_rot', 'c_middle1_rot', 'c_ring1_rot', 'c_pinky1_rot']
	
	for side in arm_sides:
		for f in fingers_rot:
			finger_rot = get_pose_bone(f + side)
			if finger_rot:
				if len(finger_rot.constraints) > 0:
					for cns in finger_rot.constraints:
						if cns.type == "COPY_ROTATION":
							print("Deleting", cns.name, "from", finger_rot.name)
							finger_rot.constraints.remove(cns)
							
							new_finger_rot = get_pose_bone(f.split('_')[1] + side)
							if new_finger_rot:
								print("Adding new Copy Rot constraint to", new_finger_rot.name)
								new_cns = new_finger_rot.constraints.new("COPY_ROTATION")
								new_cns.target = bpy.context.active_object
								new_cns.subtarget = f.split('_')[1].replace('1', '') + '_bend_all' + side
								new_cns.use_x = True
								new_cns.use_y = new_cns.use_z = False
								new_cns.target_space = 'LOCAL'
								new_cns.owner_space = 'LOCAL'
							
							break
		
	
	
	# Update spine bones relationships
	spine_bones_to_update = ["spine_02.x", "spine_03.x"]
	
	for bname in spine_bones_to_update:
		# change parent
		bpy.ops.object.mode_set(mode='EDIT')
		ebone = get_edit_bone(bname)
		if ebone:			
			bone_parent = get_edit_bone('c_' + bname)
			if not bone_parent:
				continue
			else:
				if ebone.parent != bone_parent:					
					ebone.parent = bone_parent
					print("Changed spine bone parent", ebone.name)				
		
		# clear constraints
		bpy.ops.object.mode_set(mode='POSE')
		pbone = get_pose_bone(bname)
		if pbone:
			pbone.bone.use_inherit_rotation = True
			if len(pbone.constraints) > 0:
				for cns in pbone.constraints:
					pbone.constraints.remove(cns)
					print("Removed constraint", pbone.name)
					
		bpy.ops.object.mode_set(mode='EDIT')		
	
	bpy.ops.object.mode_set(mode='POSE')
	
	
				
	
	# Update Auto Eyelids
	for side in sides:
		eyeb = get_pose_bone("c_eye"+side)
		if eyeb:
			if len(eyeb.keys()) > 0:
				if not 'auto_eyelid' in eyeb.keys():
					print("auto-eyelid prop not found, updating...")
					#ensure constraints
					cns = get_pose_bone("c_eyelid_base"+side).constraints[0]
					cns.mute = False
					cns.use_x = cns.use_y = cns.use_z = True
					
					#create prop
					eyeb['auto_eyelid'] = 0.1
					eyeb["_RNA_UI"] = {}
					eyeb["_RNA_UI"]['auto_eyelid'] = {"min":0.0, "max":1.0, "default": 0.1, "description": "Automatic eyelid rotation from the eye"}
					
					#create drivers
					dr = bpy.context.active_object.driver_add('pose.bones["' + "c_eyelid_base" + side + '"].constraints["Copy Rotation"].influence', -1)
					dr.driver.expression = "var"
					base_var = dr.driver.variables.new()
					base_var.type = 'SINGLE_PROP'
					base_var.name = 'var'
					base_var.targets[0].id = bpy.context.active_object
					base_var.targets[0].data_path = 'pose.bones["' + eyeb.name + '"]["auto_eyelid"]'
					
					print("Updated.")
					
					
		

	#Fix arm pre_pole constraint type
	for bone in bpy.context.active_object.pose.bones:
		if 'fk_pre_pole' in bone.name:
			for cns in bone.constraints:
				if cns.type == 'TRACK_TO':
					print("Obsolete pre_pole arm constraint found, updating...")
					new_cns = bone.constraints.new('DAMPED_TRACK')
					new_cns.target = cns.target
					new_cns.subtarget = cns.subtarget
					bone.constraints.remove(cns)
					print("Updated.")
					
  
	# Hide/delete obsolete ref bones - Pose mode only	
	for side in leg_sides:
		toes_end_ref = get_data_bone('toes_end_ref' + side)
		if toes_end_ref:
			if toes_end_ref.hide == False:
				toes_end_ref.hide = True
				print("Obsolete toes_end_ref" + side, " has been hidden.")
			
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='DESELECT')
	
		
	try:
		for side in arm_sides:
			get_edit_bone('c_ikfk_arm'+side).select = True
		for side in leg_sides:
			get_edit_bone('c_ikfk_leg'+side).select = True
			need_update = True
			
		bpy.ops.armature.delete()
		print('....Deleted deprecated bones')
	except:
		pass
		
	def add_ik_ctrl(ik_limb_ctrl, limb_nostr, limb2_nostr, ikfk_bone, side):
		if bpy.context.active_object.data.edit_bones.get(ik_limb_ctrl + side) == None:
			# Create bone
			new_ebone = bpy.context.active_object.data.edit_bones.new(ik_limb_ctrl + side)
			new_ebone.head = get_edit_bone(limb_nostr+side).head.copy()
			new_ebone.tail = get_edit_bone(limb_nostr+side).tail.copy()
			new_ebone.roll = get_edit_bone(limb_nostr+side).roll
			
			#Set parent
			if "thigh" in ik_limb_ctrl:
				new_ebone.parent = get_edit_bone("c_thigh_b" + side)
			if "arm" in ik_limb_ctrl:
				new_ebone.parent = get_edit_bone("c_shoulder" + side)
			
			bpy.ops.object.mode_set(mode='POSE')
			
			# Set shape
			new_pbone = get_pose_bone(ik_limb_ctrl + side)
			try:
				new_pbone.custom_shape = bpy.data.objects["cs_box"]
			except:
				print("Could not set the shape of " + ik_limb_ctrl + " bone")
			new_pbone.custom_shape_transform = get_pose_bone(limb_nostr + side)
			new_pbone.bone.show_wire = True
			
			# Lock transforms
			for i in range(0,3):				
				new_pbone.lock_location[i] = True
				new_pbone.lock_scale[i] = True
				new_pbone.lock_rotation[i] = True
				
			new_pbone.lock_rotation[1] = False
			
			# Set axis order
			new_pbone.rotation_mode = "ZXY"
			
			# Set layer
			set_in_layer = 0
			if get_pose_bone(ikfk_bone+side):
				if get_pose_bone(ikfk_bone+side).bone.layers[22]:
					print(ikfk_bone+side, "is disabled")
					set_in_layer = 22
			
			for layer in range(0,32):		
				if layer == set_in_layer:
					new_pbone.bone.layers[layer] = True					
				else:
					new_pbone.bone.layers[layer] = False					
		
					
			# Disable deform
			new_pbone.bone.use_deform = False
			
			# Set color group			
			try:
				new_pbone.bone_group = bpy.context.active_object.pose.bone_groups["body"+side[-2:]]
			except:
				print('Bone group "body' + side[-2:] + ' not found')
			
			# Create driver			
			dr = bpy.context.active_object.driver_add('pose.bones["' + limb2_nostr + side + '"].constraints["IK"].pole_angle', -1)
			dr.driver.expression = "var"
			if len(dr.driver.variables) == 0:
				base_var = dr.driver.variables.new()
			else:
				base_var = dr.driver.variables[0]
			base_var.type = 'SINGLE_PROP'
			base_var.name = 'var'
			base_var.targets[0].id = bpy.context.active_object
			base_var.targets[0].data_path = 'pose.bones["' + ik_limb_ctrl + side + '"].rotation_euler[1]'
			
				# Set cyclic fcurve
			dr.modifiers.remove(dr.modifiers[0])
					# +180 angle for right side = offset -2 on X axis
			val = 0.0
			if side[-2:] == ".r":
				val = -2.0
					
			keyf1 = dr.keyframe_points.insert(-2.0-val, math.radians(-180))
			keyf1.interpolation = 'LINEAR'
			keyf2 = dr.keyframe_points.insert(2.0-val, math.radians(180))
			keyf2.interpolation = 'LINEAR'
			dr.modifiers.new("CYCLES")
			
			# Create driver to hide the bone in FK mode		
			new_dr = bpy.context.active_object.driver_add('pose.bones["' + ik_limb_ctrl + side + '"].custom_shape_scale', -1)					
			new_dr.driver.expression = "1-var"
			base_var = new_dr.driver.variables.new()
			base_var.type = 'SINGLE_PROP'
			base_var.name = 'var'
			base_var.targets[0].id = bpy.context.active_object
			base_var.targets[0].data_path = 'pose.bones["' + ikfk_bone + side + '"]["ik_fk_switch"]'
		
				# Set curve
			new_dr.modifiers.remove(new_dr.modifiers[0])
			keyf1 = new_dr.keyframe_points.insert(0.0, 0.0)
			keyf1.interpolation = 'CONSTANT'
			keyf2 = new_dr.keyframe_points.insert(1.0, 1.0)
			keyf2.interpolation = 'CONSTANT'				
			
			# Add arp_layer
			new_pbone["arp_layer"] = 0
			new_pbone.bone["arp_layer"] = 0
			
			bpy.ops.object.mode_set(mode='EDIT')
			
			# Add proxy bone			
				# load custom shape meshes if necessary
			if bpy.data.objects.get("rig_ui"):
				if bpy.data.objects.get("cs_ctrl_ik_solid_red") == None:
					obj_to_append = ["cs_ctrl_ik_solid_red", "cs_ctrl_ik_solid_blue", "cs_ctrl_ik_solid_red_sel", "cs_ctrl_ik_solid_blue_sel"]
					append_from_arp(nodes = obj_to_append, type = "object")
					
					# parent it to the "cs_grp" object
					for obj in obj_to_append:
						if bpy.data.objects.get("cs_grp"):
							bpy.data.objects[obj].parent = bpy.data.objects["cs_grp"]
						else:
							print("Could not find the cs_grp object to parent to")
					print("Appended cs_ctrl_ik shapes")
			
			if "thigh" in ik_limb_ctrl:
				pole_picker = get_edit_bone("c_leg_pole_proxy" + side)
				limb_picker = get_edit_bone("c_thigh_fk_proxy" + side)
			
			if "arm" in ik_limb_ctrl:
				pole_picker = get_edit_bone("c_arms_pole_proxy" + side)
				limb_picker = get_edit_bone("c_arm_fk_proxy" + side)
				
			if pole_picker and limb_picker: 
				# Create bone
				print("Creating picker bone:", ik_limb_ctrl + "_proxy" + side)
				b = bpy.context.active_object.data.edit_bones.new(ik_limb_ctrl + "_proxy" + side)
			
				b.head = limb_picker.head
				b.tail = limb_picker.tail				
				b.head += limb_picker.z_axis.normalized() * (limb_picker.tail-limb_picker.head).magnitude*1.5
				b.tail += limb_picker.z_axis.normalized() * (limb_picker.tail-limb_picker.head).magnitude*1.5				
								
				b.roll = limb_picker.roll
				
				#Set parent			
				b.parent = get_edit_bone("Picker")				
			
				bpy.ops.object.mode_set(mode='POSE')
				picker_pbone = get_pose_bone(ik_limb_ctrl + "_proxy" + side)
			
				picker_pbone["proxy"] = ik_limb_ctrl + side
				
				if bpy.data.objects.get("cs_ctrl_ik_solid_red"):
					if side[-2:] == ".l":
						picker_pbone["normal_shape"] = "cs_ctrl_ik_solid_red"
						picker_pbone["select_shape"] = "cs_ctrl_ik_solid_red_sel"
					
					if side[-2:] == ".r":
						picker_pbone["normal_shape"] = "cs_ctrl_ik_solid_blue"
						picker_pbone["select_shape"] = "cs_ctrl_ik_solid_blue_sel"
					
				# Assign color group			
				try:
					picker_pbone.bone_group = bpy.context.active_object.pose.bone_groups["body"+side[-2:]]
				except:
					print('Bone group "body' + side[-2:] + ' not found')
					
				# Assign custom shape (proxy picker does not update)
				try:
					picker_pbone.custom_shape = bpy.data.objects[picker_pbone["normal_shape"]]
				except:
					print("Could not set the shape of " + ik_limb_ctrl + " bone")
				
				# Assign layer							
				for layer in range(0,32):
					if layer == set_in_layer:
						picker_pbone.bone.layers[layer] = True
					else:
						picker_pbone.bone.layers[layer] = False
						
				# Add arp_layer prop
				picker_pbone["arp_layer"] = 0
				picker_pbone.bone["arp_layer"] = 0
				
				# Disable deform
				picker_pbone.bone.use_deform = False
						
			bpy.ops.object.mode_set(mode='EDIT')
			
			print("Added " + ik_limb_ctrl + side)
	
	
	# Add IK thigh controller	
	for side in leg_sides:
		if get_edit_bone("c_thigh_ik" + side):
			add_ik_ctrl( "c_thigh_ik", "thigh_ik_nostr", "leg_ik_nostr", "c_foot_ik", side)
	for side in arm_sides:
		if get_edit_bone("c_arm_ik" + side):
			add_ik_ctrl( "c_arm_ik", "arm_ik_nostr", "forearm_ik_nostr", "c_hand_ik", side)
	
			
	# Update bone properties
	duplicate_bones = ['thigh_ref.l', 'leg_ref.l', 'foot_ref.l', 'thigh_ref.r', 'leg_ref.r', 'foot_ref.r', 'shoulder_ref.r', 'arm_ref.r', 'forearm_ref.r', 'hand_ref.r', 'shoulder_ref.l', 'arm_ref.l', 'forearm_ref.l', 'hand_ref.l', 'head_ref.x', 'neck_ref.x', 'ear_01_ref.l', 'ear_02_ref.l', 'ear_01_ref.r', 'ear_02_ref.r']

	for bone in duplicate_bones:
		if get_edit_bone(bone)!= None:
			get_edit_bone(bone)['arp_duplicate'] = 1.0
		
	# Update bones name
	try:		
		get_edit_bone('c_stretch_arm_pin_proxy.r.001').name = 'c_stretch_leg_pin_proxy.r'
		get_edit_bone('c_stretch_arm_pin_proxy.l.001').name = 'c_stretch_leg_pin_proxy.l'
	except:
		pass
	try:
		get_edit_bone('eye_ref.l').name = 'c_eye_ref.l' 
		get_edit_bone('eye_ref.r').name = 'c_eye_ref.r' 
		need_update = True
	except:
		pass 
	
	for bone in bpy.context.active_object.data.edit_bones:
		if "c_head_scale_fix" in bone.name:
			bone.name = bone.name.replace("c_", "")
			print("c_head_scale_fix has been renamed to head_scale_fix")
			
		if "c_neck_thick_proxy" in bone.name:
			bone.name = bone.name.replace("thick", "01")
		
	if get_pose_bone('c_eye_ref_proxy.l'):
		get_pose_bone('c_eye_ref_proxy.l')['proxy'] = 'c_eye_ref.l'
	if get_pose_bone('c_eye_ref_proxy.r'):
		get_pose_bone('c_eye_ref_proxy.r')['proxy'] = 'c_eye_ref.r'

	
	# Update layers 
	for bone in bpy.context.active_object.data.edit_bones:		  
		try:
			bone['arp_layer'] = auto_rig_datas.bones_arp_layer[bone.name]
			
		except:
			pass
			
		# Controllers must not be in protected layers
		if bone.layers[0]:
			for i in range(8,15):
				bone.layers[i] = False
			for i in range(24,30):
				bone.layers[i] = False
				
	# Un-protect the layer 31 (some controllers are deformer too)
	bpy.context.active_object.data.layers_protected[31] = False
			
	bpy.ops.object.mode_set(mode='POSE')		
	
	for bone in bpy.context.active_object.pose.bones:
		try:			
			bone['arp_layer'] = auto_rig_datas.bones_arp_layer[bone.name]			 
		except:
			pass
			
	
	for side in leg_sides:
		if get_pose_bone("c_foot_ik" + side):
			if len(get_pose_bone("c_foot_ik" + side).keys()) > 0:
				if not "fix_roll" in get_pose_bone("c_foot_ik" + side).keys():
					get_pose_bone('c_foot_ik' + side)['fix_roll'] = 0.0
					get_pose_bone('c_foot_ik' + side)['fix_roll'] = 0.0
					print('....Bone properties updated')
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	# Update parent 
		# Arms		
	for side in arm_sides:	
		shoulder_bend = get_edit_bone("c_shoulder_bend" + side)
		if shoulder_bend:
			shoulder_bend.parent = get_edit_bone("arm_twist" + side)
			
		wrist_bend = get_edit_bone("c_wrist_bend" + side)
		if wrist_bend:
			wrist_bend.parent = get_edit_bone("forearm_twist" + side)
	
		# Legs		
	for side in leg_sides:
	
		foot_bank_01 = get_edit_bone('foot_bank_01_ref'+side)
		if foot_bank_01:
			if foot_bank_01.parent == None:
				foot_bank_01.parent = get_edit_bone('foot_ref'+side)
			
		thigh_bend_contact = get_edit_bone("c_thigh_bend_contact" + side)
		if thigh_bend_contact:
			thigh_bend_contact.parent = get_edit_bone("thigh_twist" + side)
			
		thigh_bend_01 = get_edit_bone("c_thigh_bend_01" + side)
		if thigh_bend_01:
			thigh_bend_01.parent = get_edit_bone("thigh_twist" + side)
			
		ankle_bend = get_edit_bone("c_ankle_bend" + side)
		if ankle_bend:
			ankle_bend.parent = get_edit_bone("leg_twist" + side)
			
		# Lips roll
	for head_side in head_sides:
		lips_roll_bot = get_edit_bone('c_lips_roll_bot' + head_side)
		if lips_roll_bot:
			if lips_roll_bot.parent.name == "c_skull_01" + head_side:
				lips_roll_bot.parent = get_edit_bone("c_jawbone" + head_side)		
	

	# Spine
		# change the root bones relationships for better skinning
	c_root_bend = get_edit_bone('c_root_bend.x')
	root = get_edit_bone('root.x')
	c_root = get_edit_bone('c_root.x')
	waist_bend = get_edit_bone('c_waist_bend.x')
	
	if c_root_bend and root and c_root and waist_bend:
		updated_root_bone = False
		
		if c_root_bend.parent == root:
			c_root_bend.parent = c_root
			print("Changed c_root_bend.x parent")
			updated_root_bone = True
			
		if root.parent == c_root:
			root.parent = c_root_bend
			print("Changed root.x parent")
			updated_root_bone = True
			
		for side in ['.l', '.r']:
			bot_bend = get_edit_bone('c_bot_bend' + side)
			if bot_bend:
				if bot_bend.parent == c_root_bend:
					bot_bend.parent = root
					print("Changed", bot_bend.name, "parent")
					updated_root_bone = True
					
		if waist_bend.parent == root:
			waist_bend.parent = c_root		
			updated_root_bone = True
			
		tail = get_edit_bone("c_tail_00.x")
		if tail:
			if tail.parent == root:
				tail.parent = c_root
				print("Changed tail parent")
				updated_root_bone = True
				
		if c_root_bend.use_deform:
			c_root_bend.use_deform = False
			print("Disabled c_root_bend deform")
			updated_root_bone = True
		
		# merge the c_root_bend.x vgroup to root.x vgroup
		def transfer_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None, target_group=None):		
			if group_name in dict:				
				_target_group = dict[group_name]
				# create the vgroup if necessary										
				if object.vertex_groups.get(_target_group) == None:
					object.vertex_groups.new(_target_group)				
				# asssign weights
				object.vertex_groups[_target_group].add([vertice.index], vertex_weight, 'ADD')
				return True
							
		if updated_root_bone:			
			transfer_dict = {'c_root_bend.x':'root.x'}
			for obj in bpy.data.objects:
				if len(obj.vertex_groups) > 0:
					transferred_weights = False
					for vert in obj.data.vertices:
						for grp in vert.groups:
							try:
								grp_name = obj.vertex_groups[grp.group].name
							except:											
								continue
							weight = grp.weight
							transfer_result = transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=transfer_dict)
							if transfer_result:
								transferred_weights = True
					
					# remove the unnecessary group
					if transferred_weights:
						print("c_root_bend.x weights transferred to root.x")
						obj.vertex_groups.remove(obj.vertex_groups['c_root_bend.x'])
						

	# create new bones
	if get_edit_bone('c_p_foot.l'):
		bpy.ops.armature.select_all(action='DESELECT')
		get_edit_bone('c_p_foot.l').select = True
		get_edit_bone('c_p_foot.r').select = True
		bpy.ops.object.mode_set(mode='POSE')		   
		bpy.ops.object.mode_set(mode='EDIT')#debug selection	   
		
		bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0, 0, 0), "mirror":False, "proportional":'DISABLED', "remove_on_cancel":False, "release_confirm":False})
		
		get_edit_bone('c_p_foot.l.001').name = 'c_p_foot_fk.l'
		get_edit_bone('c_p_foot.r.001').name = 'c_p_foot_fk.r'
		
		get_edit_bone('c_p_foot.l').name = 'c_p_foot_ik.l'
		get_edit_bone('c_p_foot.r').name = 'c_p_foot_ik.r'
		print('....New bones created')
	
	# update neck twist
	for side in head_sides:
		if get_edit_bone("neck" + side):
			if get_edit_bone('neck_twist' + side) == None:
				print("Creating neck twist...")
				nbone = bpy.context.active_object.data.edit_bones.new("neck_twist" + side)
				nbone.head = get_edit_bone("neck" + side).tail
				nbone.tail = nbone.head + (get_edit_bone("head" + side).tail - get_edit_bone("head" + side).head) * 0.5
				nbone.roll = get_edit_bone('head' + side).roll
				nbone.parent = get_edit_bone('neck' + side)
				nbone.use_connect = True
				nbone.use_deform = False
				
				for idx in range(len(nbone.layers)):
					if idx != 8:
						nbone.layers[idx] = False
					
				get_edit_bone('neck' + side).bbone_segments = 5
				get_edit_bone('neck' + side).bbone_easein = 0.0
				get_edit_bone('neck' + side).bbone_easeout = 0.0
				bpy.ops.object.mode_set(mode='POSE')
				bpy.ops.object.mode_set(mode='EDIT')			
				pose_nbone = get_pose_bone("neck_twist" + side)
				cns=pose_nbone.constraints.new("COPY_ROTATION")
				cns.target = bpy.context.active_object
				cns.subtarget = 'head' + side	
				
				print("Created.")
		
	# update shoulders
	for side in arm_sides:
		c_p_shoulder = get_edit_bone('c_p_shoulder'+side)
		if c_p_shoulder:
			if c_p_shoulder.parent != get_edit_bone('c_shoulder' + side):
				c_p_shoulder.parent = get_edit_bone('c_shoulder' + side)
				print("c_p_shoulder updated.")
		
	# update layers
	for side in sides:
		switch_bone_layer('eyelid_top'+side, 0, 8, False)
		switch_bone_layer('eyelid_bot'+side, 0, 8, False)
		
	# update toes roll
	for side in leg_sides:		
		toes_ref = get_edit_bone('toes_ref' + side)
		foot_ref = get_edit_bone('foot_ref' + side)		
		if toes_ref and foot_ref:
			bpy.ops.armature.select_all(action='DESELECT')
			bpy.context.active_object.data.edit_bones.active = toes_ref	 
			bpy.context.active_object.data.edit_bones.active = foot_ref
			bpy.ops.armature.calculate_roll(type='ACTIVE') 
			print('Toes roll updated,', side)
	
	# update spine proxy locations
	head_b = get_edit_bone("c_head_proxy.x")
	if head_b:		
		if round(head_b.head[2], 2) != -6.09 and head_b.head[2] > -8:#only for old layout position
			print("Old picker layout detected, update spine button position...")
			spine_dict = auto_rig_datas.bone_update_locations
			
			for bone in spine_dict:
				get_edit_bone(bone).head, get_edit_bone(bone).tail = spine_dict[bone]
		
		
	# change the eye target controller parent to Child Of constraint
	
	for head_side in head_sides:
		c_eye_target = get_edit_bone("c_eye_target" + head_side)
		if c_eye_target:
			if c_eye_target.parent:
				print("Replacing eye_target parent by Child Of constraints...")
				c_eye_target.parent = None				
				bpy.ops.object.mode_set(mode='POSE')
				eye_target_pbone = get_pose_bone("c_eye_target" + head_side)
				cns = eye_target_pbone.constraints.new("CHILD_OF")
				cns.target = bpy.context.active_object
				cns.subtarget = "c_traj"
				cns.inverse_matrix = get_pose_bone(cns.subtarget).matrix.inverted() 
				print("eye_target constraint created.")
	
	# update the lips retain
	for head_side in head_sides:
		jaw = get_edit_bone('c_jawbone' + head_side)
		jaw_ret = get_edit_bone('jaw_ret_bone' + head_side)
		if jaw and not jaw_ret:
			_lips_bones = ['c_lips_top' + head_side, 'c_lips_top', 'c_lips_top_01', 'c_lips_smile', 'c_lips_bot_01', 'c_lips_bot', 'c_lips_bot' + head_side]
			
			lips_offset_dict = {}

			#create jaw_retain bone
			jaw_ret_bone = bpy.context.active_object.data.edit_bones.new('jaw_ret_bone' + head_side)
			jaw_ret_bone.head = jaw.head
			jaw_ret_bone.tail = jaw.tail
			jaw_ret_bone.tail = jaw_ret_bone.head + (jaw_ret_bone.tail-jaw_ret_bone.head)*0.8
			jaw_ret_bone.roll = jaw.roll
			jaw_ret_bone.parent = jaw.parent
			jaw_ret_bone.use_deform = False

				#set to layer 8
			jaw_ret_bone.layers[8] = True
			for i, layer in enumerate(jaw_ret_bone.layers):
				if i != 8:
					jaw_ret_bone.layers[i] = False


			for _bone in _lips_bones:	
				for side in sides:
					if _bone[-2:] != '.x':
						bone = get_edit_bone(_bone + head_side[:-2] + side)
					else:
						bone = get_edit_bone(_bone)
						
					#create lips retain bones
					subs = -2
					if '_dupli_' in bone.name:
						subs = -12
						
					_ret_bone_name = bone.name[:subs] + '_retain' + bone.name[subs:]
					_ret_bone = get_edit_bone(_ret_bone_name)
					if ret_bone == None:
						ret_bone = bpy.context.active_object.data.edit_bones.new(_ret_bone_name)
						ret_bone.head = bone.head.copy()
						ret_bone.tail = bone.tail.copy()
						ret_bone.tail = (ret_bone.tail - ret_bone.head) * 1.8 + ret_bone.head	   
						ret_bone.roll = bone.roll
						ret_bone.parent = jaw_ret_bone 
						ret_bone.use_deform = False
						
							#set to layer 8
						ret_bone.layers[8] = True
						for i, layer in enumerate(ret_bone.layers):
							if i != 8:
								ret_bone.layers[i] = False 
					
					
					#create offset bones
					off_bone_name = bone.name[:subs]+'_offset' + bone.name[subs:]
					off_bone = get_edit_bone(off_bone_name)
					if off_bone == None:
						offset_bone = bpy.context.active_object.data.edit_bones.new(off_bone_name)
						offset_bone.head, offset_bone.tail, offset_bone.roll, offset_bone.parent=  [bone.head.copy(), bone.tail.copy(), bone.roll, bone.parent]
						offset_bone.tail = (offset_bone.tail - offset_bone.head)*1.5 + offset_bone.head
						offset_bone.use_deform = False
						bone.parent = offset_bone
						lips_offset_dict[offset_bone.name] = None

							#set to layer 8
						offset_bone.layers[8] = True
						for i, layer in enumerate(offset_bone.layers):
							if i != 8:
								offset_bone.layers[i] = False 
				
			#create jaw_ret_bone constraint
			bpy.ops.object.mode_set(mode='POSE')

			jaw_ret_pbone = get_pose_bone('jaw_ret_bone' + head_side)
			jaw_pbone = get_pose_bone('c_jawbone' + head_side)
			
			cns = jaw_ret_pbone.constraints.new('COPY_TRANSFORMS')
			cns.target = bpy.context.active_object
			cns.subtarget = 'c_jawbone' + head_side
			cns.influence = 0.5		
			

			#create lips offset constraints
			for lip_offset in lips_offset_dict:
				lip_pbone = get_pose_bone(lip_offset)
				cns_offset = lip_pbone.constraints.new('COPY_TRANSFORMS')
				cns_offset.target = bpy.context.active_object
				cns_offset.subtarget = lip_offset.replace('_offset', '_retain')
				cns_offset.influence = 1.0
				
				#create drivers
				new_driver = cns_offset.driver_add('influence')
				new_driver.driver.expression = 'var'
				var = new_driver.driver.variables.new()
				var.name = 'var'
				var.type = 'SINGLE_PROP'
				var.targets[0].id_type = 'OBJECT'
				var.targets[0].id = bpy.context.active_object
				
					#make sure the properties exists			
				try: 
					jaw_pbone['lips_retain']
				except:
					jaw_pbone['lips_retain'] = 0.0
					jaw_pbone["_RNA_UI"] = {}	   
					jaw_pbone["_RNA_UI"]['lips_retain'] = {'min':0.0, 'max': 1.0, 'soft_min':0.0, 'soft_max':1.0, 'description': 'Maintain the lips sealed when opening the jaw'}		
					
					#create the driver data path
				var.targets[0].data_path = 'pose.bones["c_jawbone' + head_side + '"]["lips_retain"]'
				
			print('....Lips retain updated')				
						
			
		#update the lips stretch			
			#make sure the properties exists
		jaw_pbone = get_pose_bone('c_jawbone' + head_side)
		jaw_ret_pbone = get_pose_bone('jaw_ret_bone' + head_side)
	
		if jaw_pbone:
			if not 'lips_stretch' in jaw_pbone.keys():
			
				jaw_pbone['lips_stretch'] = 1.0
				#jaw_pbone["_RNA_UI"] = {}		
				jaw_pbone["_RNA_UI"]['lips_stretch'] = {'min':0.0, 'max': 5.0, 'soft_min':0.0, 'soft_max':5.0, 'description': 'Stretch and squash the lips when retain is enabled'}	  
			
				#create driver
					#x scale
				jaw_ret_driver = jaw_ret_pbone.driver_add('scale', 0)
				jaw_ret_driver.driver.expression = "max(0.05, 1 - jaw_rot * stretch_value)"
				
				var_jaw_rot = jaw_ret_driver.driver.variables.new()
				var_jaw_rot.name = 'jaw_rot'
				var_jaw_rot.type = 'SINGLE_PROP'
				var_jaw_rot.targets[0].id_type = 'OBJECT'
				var_jaw_rot.targets[0].id = bpy.context.active_object
				var_jaw_rot.targets[0].data_path = 'pose.bones["c_jawbone' + head_side + '"].rotation_euler[0]'
				
				var_stretch_value = jaw_ret_driver.driver.variables.new()
				var_stretch_value.name = 'stretch_value'
				var_stretch_value.type = 'SINGLE_PROP'
				var_stretch_value.targets[0].id_type = 'OBJECT'
				var_stretch_value.targets[0].id = bpy.context.active_object
				var_stretch_value.targets[0].data_path = 'pose.bones["c_jawbone' + head_side + '"]["lips_stretch"]'			
			
				print("....Lips stretch updated")

			
			# Update Jaw
			bpy.ops.object.mode_set(mode='EDIT')
			c_jaw = get_edit_bone('c_jawbone' + head_side)
			if c_jaw:			
				if get_edit_bone('jawbone' + head_side) == None:
					print('jawbone' + head_side +  ' is missing, updating...')				
					
					jaw = bpy.context.active_object.data.edit_bones.new('jawbone' + head_side)
					print('...created jawbone' + head_side)		
						
					# align
					copy_bone_transforms(c_jaw, jaw)
					
					# change parents
					for b in bpy.context.active_object.data.edit_bones:
						if b.parent == c_jaw:
							b.parent = jaw
					print('... parents changed')	
					jaw.parent = c_jaw
					
					# Set color group
					bpy.ops.object.mode_set(mode='POSE')
					jaw_pbone = get_pose_bone('jawbone' + head_side)
					c_jaw_pbone = get_pose_bone('c_jawbone' + head_side)
					jaw_pbone.bone_group = c_jaw_pbone.bone_group
					
					# Deform property
					c_jaw_pbone.bone.use_deform = False
					c_jaw_pbone.bone.layers[31] = False
					
					# set layers
					jaw_pbone.bone.layers[8] = True			
					for i, layer in enumerate(jaw_pbone.bone.layers):
						if i != 8:
							jaw_pbone.bone.layers[i] = False 
							
					# change c_jawbone vgroups to jawbone
					for obj in bpy.data.objects:
						if obj.type == 'MESH':
							if len(obj.vertex_groups) > 0:
								if obj.vertex_groups.get('c_jawbone' + head_side):							
									obj.vertex_groups['c_jawbone' + head_side].name = 'jawbone' + head_side
									
					print('Jaw Updated.')
					bpy.ops.object.mode_set(mode='EDIT')
					
					
				# Full update of the jaw controller (based on translation instead of rotation, more user friendly)
				
				bpy.ops.object.mode_set(mode='POSE')
				
				if len(get_pose_bone('jawbone' + head_side).constraints) == 0:
					print('\nFull update of jaw controller...') 
					bpy.ops.object.mode_set(mode='EDIT')
					c_jaw = get_edit_bone('c_jawbone' + head_side)
					jaw = get_edit_bone('jawbone' + head_side)
					
					# change parent
					jaw.parent = c_jaw.parent
					
					# align positions				
					c_jaw.head = jaw.head + (jaw.tail - jaw.head)*0.5
					c_jaw.tail	= c_jaw.head + (jaw.tail - jaw.head) * 0.5
					c_jaw.roll = jaw.roll			
					
					# setup constraints
					bpy.ops.object.mode_set(mode='POSE')
					jaw_pbone = get_pose_bone('jawbone' + head_side)
					c_jaw_pbone = get_pose_bone('c_jawbone' + head_side)
					
					cns2 = jaw_pbone.constraints.new('COPY_ROTATION')
					cns2.target = bpy.context.active_object
					cns2.subtarget = 'c_jawbone' + head_side
					
					cns = jaw_pbone.constraints.new('DAMPED_TRACK')
					cns.target = bpy.context.active_object
					cns.subtarget = 'c_jawbone' + head_side
					
					# change constraints links
					for pb in bpy.context.active_object.pose.bones:
						if len(pb.constraints) > 0 and pb != jaw_pbone:
							for cns in pb.constraints:
								try:
									if cns.target:
										if cns.subtarget == 'c_jawbone' + head_side:
											cns.subtarget = 'jawbone' + head_side
								# no target property linked to this constraint
								except:
									pass
								
					print('...constraints set')
					
					# set custom shapes				
					jaw_pbone.custom_shape = None
					c_jaw_pbone.bone.show_wire = True
					
					if bpy.data.objects.get('rig_ui'):
						if bpy.data.objects.get('cs_jaw_square') == None:
							obj_to_append = ['cs_jaw_square']
							append_from_arp(nodes = obj_to_append, type = 'object')						
							print('...appended', obj_to_append)
						
					c_jaw_pbone.custom_shape = bpy.data.objects['cs_jaw_square']				
					
					# Set rotation mode
					#c_jaw_pbone.rotation_mode = 'XYZ'
					
					# Set transforms loks
					for i in range(0,3):
						c_jaw_pbone.lock_location[i] = False	
						
					c_jaw_pbone.lock_location[1] = True 
					
					# update lips retain drivers
					for driver in bpy.context.active_object.animation_data.drivers: 
						dp_prop = driver.data_path.split('.')[len(driver.data_path.split('.'))-1]
						if 'jaw_ret_bone' in driver.data_path and dp_prop == 'scale':
							jaw_ret_name = driver.data_path.split('"')[1]
							jaw_ret_length = str(round(get_data_bone(jaw_ret_name).length, 4) * 140)
							dr = driver.driver						
							dr.expression = 'max(0.05, 1 - jaw_rot * ' + jaw_ret_length + ' * stretch_value)'						
							base_var = dr.variables['jaw_rot']
							base_var.targets[0].data_path = base_var.targets[0].data_path.replace("rotation_euler[0]", "location[2]")
							
											
					print('Jaw fully updated.')		
					
					
			else:
				print('c_jawbone.x not found')
				
				
	
			
		
	bpy.ops.object.mode_set(mode='POSE')	

	# Update the base fingers picker shapes 
	fingers_base = ["c_pinky1", "c_ring1", "c_middle1", "c_index1", "c_thumb1"]
	
	if bpy.data.objects.get("cs_solid_circle_02_red"):
		
		for bone_n in fingers_base:
			for side in arm_sides:
			
				mat_color = "_red"
				if side == ".r":				
					mat_color = "_blue"
					
				if get_pose_bone(bone_n + "_base_proxy" + side):	
					pbone_proxy = get_pose_bone(bone_n + "_base_proxy" + side)
					
					if pbone_proxy["normal_shape"] != "cs_solid_circle_02" + mat_color:						
						pbone_proxy["normal_shape"] = "cs_solid_circle_02" + mat_color
						pbone_proxy["select_shape"] = "cs_solid_circle_02" + mat_color + "_sel"
						pbone_proxy.custom_shape = bpy.data.objects["cs_solid_circle_02" + mat_color]
						print("Updated picker shape of", bone_n + "_base_proxy" + side)
					
	# Update the base fingers shapes
	shapes_to_append = []
	if bpy.data.objects.get("cs_base_finger_end") == None:
		shapes_to_append.append("cs_base_finger_end")
		print('Appended "cs_base_finger_end"')
	if bpy.data.objects.get("cs_base_finger") == None:
		shapes_to_append.append("cs_base_finger")
		print('Appended "cs_base_finger"')
	
	if len(shapes_to_append)  > 0:
		append_from_arp(nodes = shapes_to_append, type = "object")
		
		for side in arm_sides:
			for f_name in fingers_base:
				pb = get_pose_bone(f_name.replace("1", "1_base") + side)
				if pb and not "cs_user" in pb.custom_shape.name:
					if not "pinky"in f_name:
						pb.custom_shape = bpy.data.objects["cs_base_finger"]
						pb.custom_shape_scale = 0.3
						print("Updated", pb.name, "custom shape")
						
					else:# pinky
						pb.custom_shape = bpy.data.objects["cs_base_finger_end"]
						pb.custom_shape_scale = 0.3
						pb.lock_location[0] = pb.lock_location[1] = pb.lock_location[2] = True
						print("Updated", pb.name, "custom shape")
						

	# Update secondary arm bones shapes		
	for side in arm_sides:
		for add_bone in auto_rig_datas.arm_bones_rig_add:
			if not get_pose_bone(add_bone + side):
				continue
			if not get_pose_bone(add_bone + side).custom_shape:
				continue
			if get_pose_bone(add_bone + side).custom_shape.name == "cs_circle_02":
				get_pose_bone(add_bone + side).custom_shape = bpy.data.objects["cs_torus_02"]
				print("Updated " + add_bone + side + ' shape.')
			
	# Update constraints
	for side in arm_sides:	  
		if get_pose_bone('c_p_shoulder'+ side):
			get_pose_bone('c_p_shoulder'+ side).constraints[0].mute = True	
			get_pose_bone('arm_stretch' + side).constraints['Copy Location'].subtarget = 'arm_twist' + side
			if bpy.context.active_object.arp_secondary_type == "additive":
				get_pose_bone('arm_stretch' + side).constraints['Copy Location'].head_tail = 1.0
			if bpy.context.active_object.arp_secondary_type == "bendy_bones":
				get_pose_bone('arm_stretch' + side).constraints['Copy Location'].head_tail = 0.0
		
	for side in leg_sides:	 
		if get_pose_bone('thigh_stretch' + side):
			get_pose_bone('thigh_stretch' + side).constraints['Copy Location'].subtarget = 'thigh_twist' + side
			if bpy.context.active_object.arp_secondary_type == "additive":
				get_pose_bone('thigh_stretch' + side).constraints['Copy Location'].head_tail = 1.0
			if bpy.context.active_object.arp_secondary_type == "bendy_bones":
				get_pose_bone('thigh_stretch' + side).constraints['Copy Location'].head_tail = 0.0
		
	# Update fcurve datapath
	def replace_fcurve_dp(action, replace_this, by_this):
		for fcurve in action.fcurves:
			if replace_this in fcurve.data_path:
				fcurve.data_path = fcurve.data_path.replace(replace_this, by_this)
						
	def replace_fcurve_grp(action, replace_this, by_this):
		for group in action.groups:
			if replace_this in group.name:
				group.name = group.name.replace(replace_this, by_this)
					  

	if len(bpy.context.blend_data.actions) > 0:
		for action in bpy.context.blend_data.actions:
			replace_fcurve_dp(action, 'c_ikfk_arm', 'c_hand_ik')
			replace_fcurve_dp(action, 'c_ikfk_leg', 'c_foot_ik')		
			replace_fcurve_grp(action, 'c_ikfk_arm', 'c_hand_ik')
			replace_fcurve_grp(action, 'c_ikfk_leg', 'c_foot_ik')
		   
		
		#remove invalid fcurve // BUGGY, must be run several time :-/	
		invalid_fcurves = []
		for fcurve in action.fcurves:
			if not fcurve.is_valid:				
				invalid_fcurves.append(fcurve)
			   
		for fc in invalid_fcurves:			
			action.fcurves.remove(fc)
			
	#Replace depracted groups names
	depracated_groups_list = ["c_pinky1", "c_ring1", "c_middle1", "c_index1", "c_thumb1"]
	
	found_new_finger_bone = False
	
	for bone in bpy.context.active_object.data.bones:
		if bone.name == "index1.l":
			found_new_finger_bone = True			
			break
			
	if found_new_finger_bone:
		for obj in bpy.data.objects:
			if len(obj.vertex_groups) > 0:
				for vgroup in obj.vertex_groups:	
					for name in depracated_groups_list:
						if name in vgroup.name and not "base" in vgroup.name:				
							vgroup.name = vgroup.name[2:]
							print("Replaced vertex group:", vgroup.name)
			
			
	
	
	secondary_eyelids = ["c_eyelid_top_01", "c_eyelid_top_02", "c_eyelid_top_03", "c_eyelid_corner_01", "c_eyelid_corner_02", "c_eyelid_bot_01", "c_eyelid_bot_02", "c_eyelid_bot_03"]	
	
	rig_name = bpy.context.active_object.name
	rig_add = get_rig_add(bpy.context.active_object)
	
	
	bpy.ops.object.mode_set(mode='EDIT')
	
		
	# Find facial duplis
	facial_duplis = []	
		
	for bone in bpy.context.active_object.data.edit_bones:
		if "eyelid" in bone.name:		
			_side = bone.name[-2:]
			if	"_dupli_" in bone.name:
				_side = bone.name[-12:]				
			if not _side in facial_duplis:
				facial_duplis.append(_side) 
				
	
	bpy.ops.object.mode_set(mode='POSE')
	
	for dupli in facial_duplis:
	
		# Replace the eyes Track_To cns by Damped_Track to avoid rotation issues
		eye = get_pose_bone('c_eye' + dupli)
		if eye:
			track_cns = None
			found = False
			if len(eye.constraints) > 0:
				for cns in eye.constraints:
					if cns.type == 'DAMPED_TRACK':
						found = True
					if cns.type == 'TRACK_TO':
						track_cns = cns						
						
			if not found and track_cns:
				print('Adding the eyelid Damped Track constraint...')
				# create the damped_track constraint
				cns_damp = eye.constraints.new('DAMPED_TRACK')
				cns_damp.target = track_cns.target
				cns_damp.subtarget = track_cns.subtarget
				
				#create drivers
				new_driver = cns_damp.driver_add("influence")
				new_driver.driver.expression = "var"
				var = new_driver.driver.variables.new()
				var.name = "var"
				var.type = "SINGLE_PROP"
				var.targets[0].id_type = "OBJECT"
				var.targets[0].id = bpy.context.active_object
				var.targets[0].data_path = 'pose.bones["c_eye_target.x"]["eye_target"]' 
				
				# remove the track_to constraint
				eye.constraints.remove(track_cns)
				
		# add a Limit Rotation constraint to avoid rotations issues with the auto-eyelids
		eyelid_base = get_pose_bone('c_eyelid_base' + dupli)
		if eyelid_base:
			found = False
			if len(eyelid_base.constraints) > 0:
				for cns in eyelid_base.constraints:
					if cns.type == 'LIMIT_ROTATION':
						found = True
						
				if not found:
					print('Adding the Limit Rotation constraint...')
					limit_cns = eyelid_base.constraints.new('LIMIT_ROTATION')
					limit_cns.use_limit_x = limit_cns.use_limit_y = limit_cns.use_limit_z = True
					limit_cns.min_x = math.radians(-30)
					limit_cns.max_x = math.radians(10)
					limit_cns.min_y = limit_cns.max_y = 0.0
					limit_cns.min_z = math.radians(-20)
					limit_cns.max_z = math.radians(20)
					limit_cns.owner_space = 'LOCAL'
	
	bpy.ops.object.mode_set(mode='EDIT')

	
	# Make sure the secondary eyelids are parented to eyelid_top and eyelid_bot
	for b in secondary_eyelids:
		for dupli in facial_duplis:
			bo = get_edit_bone(b + dupli)
			if bo:				
				if not "corner" in b:					
					id = b.split('_')[2]
					parent_bone = get_edit_bone('eyelid_' + id + dupli)
					if parent_bone:					
						bo.parent = parent_bone
				
		
	# Update eyelids controllers, rotation based to translation based
	bpy.ops.object.mode_set(mode='POSE')
	update_eyelids = True
	if get_pose_bone("eyelid_top.l"):
		if len(get_pose_bone("eyelid_top.l").constraints) == 0:
			update_eyelids = True
		else:
			update_eyelids = False
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	if update_eyelids:	
		xmirror_state = bpy.context.active_object.data.use_mirror_x
		bpy.context.active_object.data.use_mirror_x = False
		
		print("\nUpdating eyelids controllers...")
		for side in facial_duplis:
			
			# delete
			"""
			if get_edit_bone("eyelid_top" + side):
				bpy.context.active_object.data.edit_bones.remove(get_edit_bone("eyelid_top" + side))
				bpy.context.active_object.data.edit_bones.remove(get_edit_bone("eyelid_bot" + side))	
			"""
			bpy.ops.object.mode_set(mode='POSE')
			
			if get_pose_bone("c_eye_offset" + side):
				for id in ["_top", "_bot"]:
					if get_pose_bone("eyelid" + id + side):
						# if it has no constraint, we assume the bone is from an older version and delete it
						if len(get_pose_bone("eyelid" + id + side).constraints) == 0:
							bpy.ops.object.mode_set(mode='EDIT')
							bpy.context.active_object.data.edit_bones.remove(get_edit_bone("eyelid" + id + side))
							print("...Deleted old eyelid" + id + side)
							bpy.ops.object.mode_set(mode='POSE')
							
					if get_pose_bone("eyelid" + id + side) == None: 
						bpy.ops.object.mode_set(mode='EDIT')
						
						# Rename the current c_eyelid to eyelid
						
						get_edit_bone("c_eyelid" + id + side).name = "eyelid" + id + side
						eyel = get_edit_bone("eyelid" + id + side)
						eye_offset = get_edit_bone("c_eye_offset" + side)
						print("...Renamed c_eyelid" + id + side + " to eyelid" + id + side)
						
						# Create the c_eyelid bone
						c_eyel = bpy.context.active_object.data.edit_bones.new("c_eyelid" + id + side)
						c_eyel.parent = eye_offset
						c_eyel.head = eyel.tail + (eyel.tail - eyel.head)*1.5
						c_eyel.tail = c_eyel.head + ((eyel.tail - eyel.head) * 0.5)#.magnitude * eye_offset.y_axis.normalized())						
						c_eyel.roll = eyel.roll
						
						# Copy properties from the previous bone
						for key in eyel.keys():
							c_eyel[key] = eyel[key]
						
						print("... Created new c_eyelid" + id + side)
						
						# set layers
						c_eyel.layers[0] = True			
						for i, layer in enumerate(c_eyel.layers):
							if i != 0:
								c_eyel.layers[i] = False
						
						eyel.layers[8] = True
						eyel.layers[0] = False
						
						# Deform property
						c_eyel.use_deform = False
						
						# Setup constraints
						bpy.ops.object.mode_set(mode='POSE')						
						
						# By transform constraint
						eyelid_pbone = get_pose_bone("eyelid" + id + side)
						cns = eyelid_pbone.constraints.new("TRANSFORM")
						cns.target = bpy.context.active_object
						cns.subtarget = "c_eyelid" + id + side
						cns.use_motion_extrapolate = True
						cns.from_min_z = 0.0
						cns.from_max_z = 1.5 
						cns.map_to_x_from = "Z"
						cns.map_to_z_from = "X"
						cns.map_to = "ROTATION"
						cns.to_max_x_rot = 1.4 / eyelid_pbone.length
						cns.target_space = cns.owner_space = "LOCAL"
						
						"""
						# By Damped Track constraint WARNING: does not work with auto-eyelid parent rotation
						cns = get_pose_bone("eyelid" + id + side).constraints.new("DAMPED_TRACK")
						cns.target = bpy.context.active_object
						cns.subtarget = "c_eyelid" + id + side
						"""
						
						# Other rotations axes get constrained
						cns1 = get_pose_bone("eyelid" + id + side).constraints.new("COPY_ROTATION")
						cns1.target = bpy.context.active_object
						cns1.subtarget = "c_eyelid" + id + side
						cns1.use_x = False
						cns1.target_space = cns1.owner_space = "LOCAL"
						
						# set color group
						c_eyel_pbone = get_pose_bone("c_eyelid" + id + side)
						c_eyel_pbone.bone_group = get_pose_bone("eyelid" + id + side).bone_group
						
						# transforms locks
						c_eyel_pbone.lock_location[0] = c_eyel_pbone.lock_location[1] = True
						c_eyel_pbone.lock_rotation[0] = True
						
						# Rotation mode
						c_eyel_pbone.rotation_mode = "XYZ"
						
						# Set custom shape
						if bpy.data.objects.get("cs_eyelid2") == None:
							append_from_arp(nodes=["cs_eyelid2"], type="object")
						
						c_eyel_pbone.custom_shape = bpy.data.objects["cs_eyelid2"]
						get_pose_bone("eyelid" + id + side).custom_shape = None
						c_eyel_pbone.bone.show_wire = True
		
		bpy.context.active_object.data.use_mirror_x = xmirror_state
		print("Eyelids updated.")
	
	
	if rig_add:
		# Enable secondary eyelids bones deform and remove them from rig_add
		if rig_add.data.bones.get("c_eyelid_top_01.l"): 
			print("Removing secondary eyelids from additive bones...")	
			
			for b in secondary_eyelids:
				for side in sides:					
					if get_data_bone(b + side):					
						get_data_bone(b + side).use_deform = True																
						
			edit_rig(rig_add)
			
			for b in secondary_eyelids:
				for side in sides:
					if get_edit_bone(b + side):
						bpy.context.active_object.data.edit_bones.remove(get_edit_bone(b+side))
						
			bpy.ops.object.mode_set(mode='OBJECT')
			rig_add.select_set(state=False)
			rig_add.hide_select = True
			rig_add.hide_viewport = True
			edit_rig(bpy.data.objects[rig_name])
	
		# remove the eye_offset bone from the rig_add
		for side in [".l", ".r"]:
			eye_off = rig_add.data.bones.get("c_eye_offset" + side)
			if eye_off:
				edit_rig(rig_add)
				bpy.context.active_object.data.edit_bones.remove(get_edit_bone("c_eye_offset" + side))
				
		bpy.ops.object.mode_set(mode='OBJECT')
		rig_add.select_set(state=False)
		rig_add.hide_select = True
		rig_add.hide_viewport = True
		edit_rig(bpy.data.objects[rig_name])
	
	# Correct the head lock property
	bpy.ops.object.mode_set(mode='POSE')
	scale_fix_bone = None	
	
		# retro-compatibility
	if bpy.context.active_object.data.bones.get("c_head_scale_fix.x"):
		scale_fix_bone = bpy.context.active_object.data.bones["c_head_scale_fix.x"]
	elif bpy.context.active_object.data.bones.get("head_scale_fix.x"):
		scale_fix_bone = bpy.context.active_object.data.bones["head_scale_fix.x"]
		
		# add the new ChildOf constraint if it's not there
	found_cns = False
	if scale_fix_bone:
		scale_fix_pbone = get_pose_bone(scale_fix_bone.name)
	
		for cns in scale_fix_pbone.constraints:
			if cns.name == "Child Of_traj":
				found_cns = True
		
		if not found_cns:
			print("Head lock ChildOf constraint not found, updating...")
			scale_fix_bone.use_inherit_scale = False
			scale_fix_bone.use_inherit_rotation = False
			
			new_cns = scale_fix_pbone.constraints.new("CHILD_OF")
			new_cns.name = "Child Of_traj"
			new_cns.target = bpy.context.active_object
			new_cns.subtarget = "c_traj"
			bpy.context.active_object.data.bones.active = scale_fix_pbone.bone
			my_context = bpy.context.copy()
			my_context["constraint"] = new_cns
			bpy.ops.constraint.move_up(my_context, constraint=new_cns.name, owner='BONE')		
			new_cns.inverse_matrix = get_pose_bone(new_cns.subtarget).matrix.inverted() 
					
			dr = bpy.context.active_object.driver_add('pose.bones["' + scale_fix_pbone.name + '"].constraints["Child Of_traj"].influence', -1)
			dr.driver.expression = "1-var"
			if len(dr.driver.variables) == 0:
				base_var = dr.driver.variables.new()
			else:
				base_var = dr.driver.variables[0]
			base_var.type = 'SINGLE_PROP'
			base_var.name = 'var'
			base_var.targets[0].id = bpy.context.active_object
			base_var.targets[0].data_path = 'pose.bones["c_head.x"].["head_free"]'
			
			
			print("Head lock constraint updated.")
				
	
	# Add the latest version update tag
	bpy.context.active_object.data["arp_updated"] = '3.41.18'
	
	#restore layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = layers_select[i] 
		
	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	#enable the proxy picker 
	try:	   
		bpy.context.scene.Proxy_Picker.active = True
	except:
		pass
	
	# update facial to disable new facial bones if necessary
	update_facial(self, context)
	 
	bpy.ops.object.mode_set(mode=current_mode)
	
		
	print('\nFinished armature update')
	
	
	
	
def clean_drivers():
	
	obj = bpy.context.active_object
	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='POSE')
	
	invalid_drivers_total = 0
	
	def is_driver_valid(dr, bone_name):
		if not dr.is_valid:
			return False
		if not obj.data.bones.get(bone_name):
			return False
		if "constraints" in dr.data_path:
			cns_name = dr.data_path.split('"')[3]
			target_bone = get_pose_bone(bone_name)	
			found_cns = False
			
			if len(target_bone.constraints) > 0:
				for cns in target_bone.constraints:
					if cns.name == cns_name:
						found_cns = True
				if "cns" in locals():	
					del cns
				
			if not found_cns:
				return False
				
		return True
		
	for dr in obj.animation_data.drivers:
		if 'pose.bones' in dr.data_path:			
			b  = dr.data_path.split('"')[1]			
			
			if not is_driver_valid(dr, b):
				# the driver is invalid 
				# assign a dummy but valid data path since we can't remove drivers
				# with invalid data path	
				#print("Invalid driver found:", dr.data_path)
				invalid_drivers_total += 1
				dr.array_index = 0
				dr.data_path = 'delta_scale'				
	
	if 'dr' in locals():
		del dr	
	
	print("Found", invalid_drivers_total, "invalid drivers")
	"""
	# need to toggle edit mode *2* times for update to avoid crash
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='EDIT')
	"""
	count = 0
	for dr in obj.animation_data.drivers:
		if dr.data_path == "delta_scale":
			obj.animation_data.drivers.remove(dr)
			count += 1
	
	
	print(count, "invalid drivers deleted")
	"""
	delta_scale_driver = obj.animation_data.drivers.find("delta_scale")
	if delta_scale_driver:
		#obj.driver_remove("delta_scale", -1)
		obj.animation_data.drivers.remove(delta_scale_driver)
		print("Invalid drivers deleted")
	"""
	
	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	
	
def _disable_limb(self, context):
	  
	#display all layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True
	
	
	#disable the proxy picker to avoid bugs
	try:	   
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass
		
	#Turn off mirror edit
	mirror_edit = bpy.context.active_object.data.use_mirror_x
	bpy.context.active_object.data.use_mirror_x = False
  
	sel_bone = bpy.context.selected_editable_bones[0].name	
	side = sel_bone[-2:]  
	drivers_data = bpy.context.active_object.animation_data.drivers
	
	rig = bpy.context.active_object
	rig_add = get_rig_add(rig)
	
	rig_type = ''
	if context.active_object.data.keys():
		if 'arp_rig_type' in context.active_object.data.keys():
			rig_type = context.active_object.data['arp_rig_type']
				
		
	def disable_display_bones(b_name):
		try:
			b = get_edit_bone(b_name)
			b.layers[22] = True
			b.layers[16] = False
			b.layers[0] = False
			b.layers[1] = False 
		except:
			print(b_name, 'is invalid')
		
  
	#ARMS	--------------------------------------
	arm_bones = auto_rig_datas.arm_bones
	arm_deform = auto_rig_datas.arm_deform
	arm_control = auto_rig_datas.arm_control
	arm_ref_bones = auto_rig_datas.arm_ref_bones
	fingers_list = ['thumb', 'index', 'middle', 'ring', 'pinky']
	fingers_control = auto_rig_datas.fingers_control

	if 'arm_' in sel_bone or 'shoulder' in sel_bone or 'hand' in sel_bone:		
		sel_bone_side = sel_bone[-2:]
		if '_dupli' in sel_bone:
			sel_bone_side = sel_bone[-12:]		
	
		bpy.ops.armature.select_all(action='DESELECT')
		# select the whole limb			
		for bone in arm_bones: 
			eb = get_edit_bone(bone + sel_bone_side)
			if eb:
				eb.select = True
				
		if "bone" in locals():	
			del bone
		
		# select proxy bones
		for bone in arm_control + fingers_control: 
			eb = get_edit_bone(bone + '_proxy' + sel_bone_side)
			if eb:
				eb.select = True
				
		if "bone" in locals():	
			del bone
		
		for bone in arm_ref_bones:
			eb = get_edit_bone(bone + sel_bone_side)
			if eb:
				eb.select = True
				
		if "bone" in locals():	
			del bone
		
		bpy.ops.armature.delete()	
		
		# delete visibility property
		cpos = get_pose_bone('c_pos')
		if cpos and '_dupli' in sel_bone:			
			if len(cpos.keys()) > 0:
				if 'arm '+sel_bone[-5:] in cpos.keys():				
					del cpos['arm '+sel_bone[-5:]]
		
		
		# rig_add bones 
		if rig_add:
			rig_add.hide_viewport = False
			edit_rig(rig_add)
			bpy.ops.armature.select_all(action='DESELECT')		 
				
				# delete
			for b_add in auto_rig_datas.arm_bones_rig_add:
				b_add_bone = get_edit_bone(b_add + sel_bone_side)
				if b_add_bone:
					bpy.context.active_object.data.edit_bones.remove(b_add_bone)
			
				# delete			
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			rig_add.hide_viewport = True
				
			edit_rig(rig)
		
				
	#LEGS -------------------------------------------------------------
	leg_bones = auto_rig_datas.leg_bones
	leg_deform = auto_rig_datas.leg_deform
	leg_control = auto_rig_datas.leg_control
	leg_ref_bones = auto_rig_datas.leg_ref_bones
	toes_list = ['thumb', 'index', 'middle', 'ring', 'pinky']
	toes_control = auto_rig_datas.toes_control
	
	if 'thigh' in sel_bone or 'leg' in sel_bone or 'foot' in sel_bone:	
		sel_bone_side = sel_bone[-2:]
		if '_dupli' in sel_bone:
			sel_bone_side = sel_bone[-12:]	 
		
		#select the whole dupli limb  
		bpy.ops.armature.select_all(action='DESELECT')
		for bone in leg_bones: 
			eb = get_edit_bone(bone + sel_bone_side)
			if eb:			  
				eb.select = True
				
		if "bone" in locals():	
			del bone
			
			#ref bones
		for bone in leg_ref_bones:
			eb = get_edit_bone(bone + sel_bone_side)
			if eb:
				eb.select = True
				
		if "bone" in locals():	
			del bone
		
			#proxy bones	   
		for bone in leg_control + toes_control: 
			eb = get_edit_bone(bone + '_proxy' + sel_bone_side)
			if eb:
				eb.select = True			
		
		if "bone" in locals():	
			del bone
		
		bpy.ops.armature.delete()			 
		
			
		# rig_add bones 
		if rig_add:
			rig_add.hide_viewport = False
			edit_rig(rig_add)
			bpy.ops.armature.select_all(action='DESELECT')
			
				# delete
			for b_add in auto_rig_datas.leg_bones_rig_add:
				b_add_bone = get_edit_bone(b_add + sel_bone_side)
				if b_add_bone:
					bpy.context.active_object.data.edit_bones.remove(b_add_bone)
					
			if "b_add" in locals(): 
				del b_add			
			
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			rig_add.hide_viewport = True
			
		
		edit_rig(rig)
		
		#delete visibility property 
		cpos = get_pose_bone('c_pos')
		if cpos and '_dupli' in sel_bone:
			if len(cpos.keys()) > 0:
				if 'leg '+sel_bone[-5:] in cpos.keys():
					del cpos['leg '+sel_bone[-5:]]
			
		
		
	def disable_finger(finger, suffix, bone_name):	
		to_del = []
		for bone in bpy.context.active_object.data.edit_bones:
			if (suffix in bone.name) and (finger in bone.name):
				to_del.append(bone)
			
		for b in to_del:
			bpy.context.active_object.data.edit_bones.remove(b)
		
	
	
	
	def disable_head(context, suffix):
	
		disable_facial(suffix)
		
		# Bones
		for bone in auto_rig_datas.head_bones:	
			bname = bone[:-2] + suffix
			cbone = get_edit_bone(bname)
			if cbone:
				bpy.context.active_object.data.edit_bones.remove(cbone)
				
		if "bone" in locals():	
			del bone
		
		# Proxy
		for bone in auto_rig_datas.head_control:
			bname = bone[:-2] + '_proxy' + suffix
			proxy_bone = get_edit_bone(bname)
			if proxy_bone:
				bpy.context.active_object.data.edit_bones.remove(proxy_bone)
		
		if "bone" in locals():	
			del bone
		
		# Ref bones
		for bone in ['head_ref.x']: 
			bname = bone[:-2] + suffix
			ref_bone = get_edit_bone(bname)
			if ref_bone:
				bpy.context.active_object.data.edit_bones.remove(ref_bone)
		
		if "bone" in locals():	
			del bone
			
					
		
			
	def disable_facial(suffix): 
		# Bones
		for bone in auto_rig_datas.facial_bones:
			for sided in ['.l', '.r']:
				if bone[-2:] != ".x":
					bone_name = bone + suffix[:-2] + sided
				if bone[-2:] == ".x":
					bone_name = bone[:-2] + suffix[:-2] + ".x"
				
				cbone = get_edit_bone(bone_name)
				if cbone:					
					bpy.context.active_object.data.edit_bones.remove(cbone)
		
		if "bone" in locals():	
			del bone
		
		# Ref
		for bone in auto_rig_datas.facial_ref:			
			for sided in ['.l', '.r']:
				bone_name = bone + suffix[:-2] + sided
				if bone[-2:] == ".x":
					bone_name = bone[:-2] + suffix[:-2] + ".x"
				
				ref_bone = get_edit_bone(bone_name)
				if ref_bone:	
					bpy.context.active_object.data.edit_bones.remove(ref_bone)
					
		if "bone" in locals():	
			del bone
		
		# Proxy
		for bone in auto_rig_datas.facial_control:
			for sided in ['.l', '.r']:
				bone_name = bone + '_proxy' + suffix[:-2] + sided
				if bone[-2:] == ".x":
					bone_name = bone[:-2] + '_proxy' + suffix[:-2] + ".x"
				
				proxy_bone = get_edit_bone(bone_name)
				if proxy_bone:			
					bpy.context.active_object.data.edit_bones.remove(proxy_bone)
		
		if "bone" in locals():	
			del bone
		
			
		
	def disable_neck(context, suffix):	
		# Bones
		for bone in auto_rig_datas.neck_bones:	
			b = get_edit_bone(bone[:-2] + suffix)
			if b:
				bpy.context.active_object.data.edit_bones.remove(b)
		
		if "bone" in locals():	
			del bone
		
		# Proxy
		for bone in auto_rig_datas.neck_control:	
			proxy_bone = get_edit_bone(bone[:-2] + '_proxy' + suffix)
			if proxy_bone:
				bpy.context.active_object.data.edit_bones.remove(proxy_bone)				
		
		if "bone" in locals():	
			del bone
		
		# Ref bones
		for bone in ['neck_ref.x']: 
			ref_bone = get_edit_bone(bone[:-2] + suffix)
			if ref_bone:
				bpy.context.active_object.data.edit_bones.remove(ref_bone)
		
		if "bone" in locals():	
			del bone			
		
		
	def disable_child_connections(current_bone):
	#check for existing parent connection
		for bone in bpy.context.active_object.data.edit_bones:
			if bone.layers[17]:
				if bone.parent == get_edit_bone(current_bone):
					bone.parent = None
		
		if "bone" in locals():	
			del bone
		
	def disable_spine(spine_bone, context): 
		
		if '01' in spine_bone:
			spine_deform = auto_rig_datas.spine01_deform
			spine_control = auto_rig_datas.spine01_control
		if '02' in spine_bone:
			spine_deform = auto_rig_datas.spine02_deform
			spine_control = auto_rig_datas.spine02_control
		if '03' in spine_bone:
			spine_deform = auto_rig_datas.spine03_deform
			spine_control = auto_rig_datas.spine03_control
			#change bend parent
			get_edit_bone('c_spine_02_bend.x').parent = get_edit_bone('spine_02.x')
		  
		
		for bone in spine_deform:
			b = get_edit_bone(bone)
			if b:
				b.use_deform = False
				b.layers[31] = False
				
		if "bone" in locals():	
			del bone
		
		for bone in spine_control:
			b = get_edit_bone(bone)
			if b:
				b.layers[22] = True
				b.layers[0] = False
				b.layers[1] = False
				b.layers[16] = False
		
		if "bone" in locals():	
			del bone
		
		switch_bone_layer(spine_bone , 17, 22, False)		 
		disable_child_connections(spine_bone)
		context.active_object.spine_disabled = True
		   
	def disable_bot(context):
		sides = ['.l', '.r']
		
		for side in sides:
			bot_ref = get_edit_bone('c_bot_bend' + side)
			bot_control = get_edit_bone('bot_bend_ref' + side)
			if bot_ref:
				bpy.context.active_object.data.edit_bones.remove(bot_ref)
			if bot_control:
				bpy.context.active_object.data.edit_bones.remove(bot_control)
				if rig_add:
					rig_add.data.bones['c_bot_bend' + side].use_deform = False					
				
				#proxy picker
				proxyb = get_edit_bone('c_bot_bend_proxy'+side)
				if proxyb:
					switch_bone_layer(proxyb.name, 1, 22, False)
				else:
					print("No bot proxy bones found, skip it")
			else:
				print("No bot_bend bone found, skip it")

				
	def disable_ear(suffix):		
		for i in range(1,17):	
			id = '%02d' % i
			# control
			cont = get_edit_bone('c_ear_' + id + suffix)
			if cont:
				bpy.context.active_object.data.edit_bones.remove(cont)
			
			# proxy
			proxyb = get_edit_bone('c_ear_' + id + '_proxy' + suffix)
			if proxyb:
				bpy.context.active_object.data.edit_bones.remove(proxyb)
			
			# ref			
			ref = get_edit_bone('ear_' + id + '_ref' + suffix)
			if ref:
				bpy.context.active_object.data.edit_bones.remove(ref)
		
		
	
	# Get suffix
	suffix = ""
	if '_dupli' in sel_bone:
		suffix = sel_bone[-12:]				
	else:
		suffix = sel_bone[-2:]
		
	# Facial
	for bone in auto_rig_datas.facial_ref:
		bname = ""
		if ".x" in bone:
			bname = bone[:-2] + suffix
		else:
			bname = bone + suffix
				
		# dupli, delete			
		if sel_bone == bname:
			disable_facial(suffix)
			break
			
	
	# Head
	if sel_bone.split('_')[0] == 'head':
		disable_head(context, suffix)
		
	# Neck
	if sel_bone.split('_')[0] == 'neck':
		set_neck(1)
		disable_head(context, suffix)
		disable_neck(context, suffix) 
		
	# Spine
	"""
	if sel_bone.split('_')[0] == 'spine':
		if '01' in sel_bone:
			disable_spine('spine_01_ref.x', context) 
			disable_spine('spine_02_ref.x', context) 
		if '02' in sel_bone:		  
			disable_spine('spine_02_ref.x', context) 
		if get_edit_bone('spine_03_ref.x'):
			disable_spine('spine_03_ref.x', context)	   
	   
	""" 
		
	# Root-spine
	if sel_bone.split('_')[0] == 'root' or sel_bone.split('_')[0] == 'spine':					
		for bname in auto_rig_datas.spine_bones + auto_rig_datas.spine_ref + auto_rig_datas.spine03_deform + auto_rig_datas.spine03_control + ['spine_03_ref.x']:
			# delete
			if get_edit_bone(bname):
				context.active_object.data.edit_bones.remove(get_edit_bone(bname))			
			
			# rig_add bones 
			if rig_add:
				rig_add.hide_viewport = False
				edit_rig(rig_add)
				bpy.ops.armature.select_all(action='DESELECT')		 
					
					# delete
				for b_add in auto_rig_datas.spine_bones_rig_add:
					b_add_bone = get_edit_bone(b_add)
					if b_add_bone:
						context.active_object.data.edit_bones.remove(b_add_bone)				
				
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				rig_add.hide_viewport = True
					
				edit_rig(rig)
					
	
	# Tail
	if sel_bone.split('_')[0] == 'tail':
		set_tail(False)
	# Breast
	if sel_bone.split('_')[0] == 'breast':
		set_breast(False) 
	# Ears
	if sel_bone.split('_')[0] == 'ear':		
		disable_ear(suffix)
		
	# Bot
	if sel_bone.split('_')[0] == 'bot' and sel_bone.split('_')[1] == 'bend':
		disable_bot(context)
	
	
	
	# Remove unused drivers
	clean_drivers()
	
	# Select at least one bone to avoid the pop up effect of the panel
	if len(bpy.context.selected_editable_bones) < 1:
		if get_edit_bone('root_ref.x'):
			bpy.context.active_object.data.edit_bones.active = get_edit_bone('root_ref.x')
		elif get_edit_bone('c_pos'):
			bpy.context.active_object.data.edit_bones.active = get_edit_bone('c_pos')
		elif len(bpy.context.active_object.data.edit_bones) > 0:
			bpy.context.active_object.data.edit_bones.active = bpy.context.active_object.data.edit_bones[0]
	
	# Display reference layer only	
	bpy.context.active_object.data.layers[17] = True
	for i in range(0,32):
		if i != 17:
			bpy.context.active_object.data.layers[i] = False
	
	
	# Restore the picker		   
	#if "Prox_Picker" in bpy.context.scene.keys():	   
	#	bpy.context.scene.Proxy_Picker.active = True
	
			
	# Restore mirror edit
	bpy.context.active_object.data.use_mirror_x = mirror_edit
	
			
 
def _pick_bone():
 
	bpy.context.scene.arp_driver_bone = bpy.context.active_object.data.bones.active.name

 
def _create_driver():
		
	obj_mesh = get_selected_pair(1)
	rig = get_selected_pair(2)
	shape_keys = obj_mesh.data.shape_keys.key_blocks
	shape_index = bpy.context.active_object.active_shape_key_index

	#create driver		  
	new_driver = shape_keys[shape_index].driver_add("value")
	new_driver.driver.expression = "var"
	new_var = new_driver.driver.variables.new()
	new_var.type = 'TRANSFORMS'
	new_var.targets[0].id = rig
	new_var.targets[0].bone_target = bpy.context.scene.arp_driver_bone

	new_var.targets[0].transform_type = bpy.context.scene.arp_driver_transform
	new_var.targets[0].transform_space = 'LOCAL_SPACE' 
	
	
	
	
def _set_shape_key_driver(self, value):
	obj = bpy.context.active_object
	shape_keys = obj.data.shape_keys.key_blocks
	shape_index = bpy.context.active_object.active_shape_key_index
	shape_key_driver = None
	shape_key_name = shape_keys[shape_index].name

	try:
		drivers_list = obj.data.shape_keys.animation_data.drivers
		for dr in drivers_list:
			if shape_key_name in dr.data_path:
				shape_key_driver = dr
	except:
		self.report({'ERROR'}, "No driver found for the selected shape key")
		return

	if shape_key_driver == None:
		self.report({'ERROR'}, "No driver found for the selected shape key")
		return

	# remove the fcurve modifier
	if len(shape_key_driver.modifiers) > 0:
		shape_key_driver.modifiers.remove(shape_key_driver.modifiers[0])

	bpy.ops.transform.translate(value=(0, 0, 0))  # update hack

	# create keyframe
	if value != 'reset':
		# get the bone driver
		bone_driver_name = shape_key_driver.driver.variables[0].targets[0].bone_target
		armature = shape_key_driver.driver.variables[0].targets[0].id
		bone_driver = armature.pose.bones[bone_driver_name]
		transform_type = shape_key_driver.driver.variables[0].targets[0].transform_type

		if transform_type == 'LOC_X':
			frame = bone_driver.location[0]
		if transform_type == 'LOC_Y':
			frame = bone_driver.location[1]
		if transform_type == 'LOC_Z':
			frame = bone_driver.location[2]

		if transform_type == 'ROT_X':
			frame = bone_driver.rotation_euler[0]
		if transform_type == 'ROT_Y':
			frame = bone_driver.rotation_euler[1]
		if transform_type == 'ROT_Z':
			frame = bone_driver.rotation_euler[2]

		if transform_type == 'SCALE_X':
			frame = bone_driver.scale[0]
		if transform_type == 'SCALE_Y':
			frame = bone_driver.scale[1]
		if transform_type == 'SCALE_Z':
			frame = bone_driver.scale[2]

		# first pass the X point value as an extreme value, since a bug prevents to set it a the right value when using small values (0.01)
		keyf = shape_key_driver.keyframe_points.insert(1000000000, float(value))

		# then correct it
		keyf.co[0] = frame

		# remove any previous keyframe at the same location
		for key in shape_key_driver.keyframe_points:
			if key.co[0] == keyf.co[0] and key.co[1] != keyf.co[1]:
				shape_key_driver.keyframe_points.remove(key)

		# the driver expression must be a plain "var", no additional factor for this to work
		shape_key_driver.driver.expression = "var"
		keyf.interpolation = 'LINEAR'

		# check if 1st key created
		first_key_created = False
		for key in shape_key_driver.keyframe_points:
			if round(key.co[0], 3) == 0:
				first_key_created = True

		if not first_key_created:
			keyf = shape_key_driver.keyframe_points.insert(10000000000, 0.00)
			keyf.co[0] = 0.0
			keyf.interpolation = 'LINEAR'

		# update fcurve
		shape_key_driver.update()


	else:  # reset

		# create driver
		print('reset')
		_id = shape_key_driver.driver.variables[0].targets[0].id
		_bone_target = shape_key_driver.driver.variables[0].targets[0].bone_target
		_transform_type = shape_key_driver.driver.variables[0].targets[0].transform_type
		_transform_space = shape_key_driver.driver.variables[0].targets[0].transform_space
		_expression = shape_key_driver.driver.expression
		print(_expression)

		# delete driver
		obj.data.shape_keys.driver_remove(shape_key_driver.data_path, -1)
		# create new one from old one
		new_driver = shape_keys[shape_index].driver_add("value")
		new_driver.driver.expression = _expression
		new_var = new_driver.driver.variables.new()
		new_var.type = 'TRANSFORMS'
		new_var.targets[0].id = _id
		new_var.targets[0].bone_target = _bone_target
		new_var.targets[0].transform_type = _transform_type
		new_var.targets[0].transform_space = _transform_space

	bpy.ops.transform.translate(value=(0, 0, 0))  # update hack 
	
	
def get_limb_suffix(side, bone_type):
	#find existing duplis  
	limb_id = 0
	found_base = False
	
	for _bone in bpy.context.active_object.data.edit_bones: 
		# arms
		if 'shoulder' in bone_type or 'arm' in bone_type or 'finger' in bone_type:
			if "shoulder_ref" in _bone.name and _bone.name[-2:] == side:
				found_base = True
			if "shoulder_ref_dupli_" in _bone.name and _bone.name[-2:] == side:				 
				current_id = int(float(_bone.name[-5:-2]))
				if current_id > limb_id:
					limb_id = current_id
		#legs
		if 'thigh' in bone_type or 'leg' in bone_type or 'toes' in bone_type:
			if "thigh_ref" in _bone.name and _bone.name[-2:] == side:
				found_base = True
			if "thigh_ref_dupli" in _bone.name and _bone.name[-2:] == side:				 
				current_id = int(float(_bone.name[-5:-2]))
				if current_id > limb_id:
					limb_id = current_id
		
		# heads
		if 'neck' in bone_type or 'head' in bone_type:	
			if "neck_ref" in _bone.name and _bone.name[-2:] == side:				
				found_base = True
			
			if "neck_ref_dupli" in _bone.name and _bone.name[-2:] == side:				 
				current_id = int(float(_bone.name[-5:-2]))
				if current_id > limb_id:
					limb_id = current_id
					
		# ears
		if 'ear' in bone_type:
			
			if "ear_01_ref" in _bone.name:				
				found_base = True
			
			if "ear_01_ref_dupli" in _bone.name:				 
				current_id = int(float(_bone.name[-5:-2]))
				print("current id", current_id)
				if current_id > limb_id:
					limb_id = current_id
					print("found dupli", current_id)
		# spine
		if 'spine' in bone_type:
			if "root_ref.x" in _bone.name:				
				found_base = True
		
		# breast
		if 'breast' in bone_type:
			if "breast_01_ref" in _bone.name:				
				found_base = True
				
		# tail
		if 'tail' in bone_type:
			if "tail_00_ref.x" in _bone.name:				
				found_base = True
			

	suffix = '{:03d}'.format(limb_id+1)
	
	return suffix, found_base
	
def _dupli_limb():
	
	rig = bpy.context.active_object
	rig_add = get_rig_add(rig)				
	rig_add.hide_viewport = False
	rig_add_name = rig_add.name
	
	#display all layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True	  

	#disable the proxy picker to avoid bugs
	try:	   
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass
		
	#disable x-mirror to avoid bugs
	mirror_x_state = bpy.context.active_object.data.use_mirror_x
	bpy.context.active_object.data.use_mirror_x = False
	
	arm_bones = auto_rig_datas.arm_bones
	arm_ref_bones = auto_rig_datas.arm_ref_bones
	arm_bones_rig_add = auto_rig_datas.arm_bones_rig_add
	leg_bones = auto_rig_datas.leg_bones
	leg_ref_bones = auto_rig_datas.leg_ref_bones
	leg_bones_rig_add = auto_rig_datas.leg_bones_rig_add
	
	selected_bone = [b.name for b in bpy.context.selected_editable_bones]

	sides = [".l", ".r"] 
	
	def duplicate_ref(limb, side, suffix):
		if limb == 'arm':
			bone_list = auto_rig_datas.arm_ref_bones			
		if limb == 'leg':
			bone_list = auto_rig_datas.leg_ref_bones
		if limb == 'head':
			bone_list = auto_rig_datas.facial_ref + ["head_ref.x", "neck_ref.x"]
		if limb == "ear":
			bone_list = auto_rig_datas.ear_ref
			
			#select bones			
		bpy.ops.armature.select_all(action='DESELECT')
		_sides = [side]
		if side == None:
			_sides = [".l", ".r"]
			
		for bone in bone_list:	
			for _side in _sides:
			
				bname = bone
				if bone[-2:] != ".x":
					bname = bone + _side
					
				limb_bone = get_edit_bone(bname)
				
				if limb_bone:
					if limb_bone.layers[22] == False:#if not disabled
						get_edit_bone(bname).select = True
						
				elif bpy.context.scene.arp_debug_mode:
					print(bname, "not found for limb duplication")
				
		bpy.ops.object.mode_set(mode='POSE')		   
		bpy.ops.object.mode_set(mode='EDIT')#debug selection			
		
		# Duplicate	   
		bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "mirror":False, "proportional":'DISABLED', "snap":False,"gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})		  
		
		# Rename				
		for bone in bpy.context.selected_editable_bones:
			#delete 'duplicate' property
			if len(bone.keys()) > 0:
				for prop in bone.keys():
					if 'arp_duplicate' in prop:
						del bone['arp_duplicate']
			trimmed = bone.name[:-4]
			bone.name = trimmed.replace(trimmed[-2:], '_dupli_' + suffix + trimmed[-2:])
			
	
		
	def duplicate_rig(limb, side, suffix):
		if limb == 'arm':  
			limb_bones_list = arm_bones
			limb_control = auto_rig_datas.arm_control + auto_rig_datas.fingers_control
			limb_bones_rig_add = arm_bones_rig_add
			bones_drivers_key = ['hand', 'arm']
			
		if limb == 'leg':
			limb_bones_list = leg_bones
			limb_control = auto_rig_datas.leg_control + auto_rig_datas.toes_control
			limb_bones_rig_add = leg_bones_rig_add
			bones_drivers_key = ['leg', 'thigh', 'foot', 'toes']
			
		if limb == 'head':
			limb_bones_list = auto_rig_datas.facial_bones + auto_rig_datas.head_bones + auto_rig_datas.neck_bones
			limb_control = auto_rig_datas.head_control + auto_rig_datas.facial_control + auto_rig_datas.neck_control		
			bones_drivers_key = ['c_eye', 'c_lips_', 'jaw_ret_', 'head_scale']
			limb_bones_rig_add = None
			
		if limb == 'ear':
			limb_bones_list = auto_rig_datas.ear_control
			limb_control = auto_rig_datas.ear_control
			bones_drivers_key = []
			limb_bones_rig_add = None
			
		drivers_data = bpy.context.active_object.animation_data.drivers		
		#drivers_armature = bpy.context.active_object.data.animation_data.drivers

		def create_limb_drivers(drivers_list):
			trim = 0
			
			dr_list_copy = [dr for dr in drivers_list]
			
			for dr in dr_list_copy:				
				
				#driver data
				if dr.data_path.partition('.')[0] == 'pose':
					trim = 12
				#driver armature
				else:
					trim = 7
					
				string = dr.data_path[trim:]
				dp_bone = string.partition('"')[0]
				
				# Do not create a driver if the dupli bone does not exist
				if get_data_bone(dp_bone[:-2] + '_dupli_' + suffix + dp_bone[-2:]) == None:
					#print("Don't create driver for", dp_bone[:-2] + '_dupli_' + suffix + dp_bone[-2:])
					continue
					
				is_limb = False
				
				for m_limb in bones_drivers_key:
					if (m_limb in dp_bone or ('bend_all' in dp_bone and limb == 'arm')):
						is_limb = True						  
				
				side_check = True
				if limb == "head":
					side_check = False			
								
				
				if (is_limb) and (dp_bone[-2:] == side or not side_check) and not '_dupli' in dp_bone:	
					
					#create new driver							:
					new_driver = drivers_list.from_existing(src_driver = drivers_list.find(dr.data_path))
					if new_driver == None:				
						new_driver = drivers_list.from_existing(src_driver = drivers_list.find(dr.data_path, index=dr.array_index))
				
					#set array index	
					try:
						new_driver.array_index = dr.array_index	 
					except:
						pass				 
					
					#change data path	 
				  
					if not 'foot_pole' in dp_bone:# can't create driver with 'from_existing' for foot pole Y location driver error hack, bug?	   
						new_driver.data_path = dr.data_path.replace(dp_bone, dp_bone[:-2] + '_dupli_' + suffix + dp_bone[-2:])
					
					else:						 
						new_driver = bpy.context.active_object.driver_add("location", dr.array_index)
						new_driver.data_path = dr.data_path.replace(dp_bone, dp_bone[:-2]+'_dupli_'+suffix+dp_bone[-2:]) 
						new_driver.driver.expression = dr.driver.expression
										
						for v in dr.driver.variables:						
					  
							v1 = new_driver.driver.variables.new()
							v1.type = v.type
							v1.name = v.name
							try:
								v1.targets[0].data_path = v.targets[0].data_path
								v1.targets[0].id_type = v.targets[0].id_type
								v1.targets[0].id = v.targets[0].id
							except:						 
								print("no data_path for: "+ v1.name)
					
					#change variable path
					for v1 in new_driver.driver.variables:						 
						try:													   
							string = v1.targets[0].data_path[12:]
							dp_bone = string.partition('"')[0]											  
							v1.targets[0].data_path = v1.targets[0].data_path.replace(dp_bone, dp_bone[:-2]+'_dupli_'+suffix+dp_bone[-2:])				   

						except:						 
							print("no data_path for: "+ v1.name)
					
		#-- end create drivers
	
		
		# Base rig - Select original bones
		bpy.ops.armature.select_all(action='DESELECT')
		
		
		_sides = [side]
		if side == None:# facial case, include both side
			_sides = [".l", ".r"]
			
		for bone in limb_bones_list:			
			for _side in _sides:
				bname = bone
				if bone[-2:] != ".x":
					bname = bone + _side
						
				ebone = get_edit_bone(bname)
				if ebone:
					if ebone.layers[22] == False:#if not disabled (finger, toes...)
						ebone.select = True
				elif bpy.context.scene.arp_debug_mode:
					print(bname, "not found for limb duplication")
	
		bpy.ops.object.mode_set(mode='POSE')		   
		bpy.ops.object.mode_set(mode='EDIT')#debug selection

			# Duplicate and move		 
		bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0.2, 0.0, 0.0), "constraint_axis":(False, False, False), "constraint_orientation":'LOCAL', "mirror":False, "proportional":'DISABLED', "snap":False, "remove_on_cancel":False, "release_confirm":False})		
		
		selected_bones = []
	
			# Rename			 
		for bone in bpy.context.selected_editable_bones:
			trimmed = bone.name[:-4]
			bone.name = trimmed.replace(trimmed[-2:], '_dupli_' + suffix + trimmed[-2:])
			selected_bones.append(bone.name)
			
		bpy.ops.object.mode_set(mode='POSE')	
		
		# Delete fingers action constraints (fingers fist) if any
		for bone in selected_bones:			
			if "c_thumb" in bone or "c_index" in bone or "c_middle" in bone or "c_ring" in bone or "c_pinky" in bone:
				if len(get_pose_bone(bone).constraints) > 0:
					for cns in get_pose_bone(bone).constraints:
						if cns.type == "ACTION":
							print("delete", cns.name)
							get_pose_bone(bone).constraints.remove(cns)
			

			# Create drivers
		if len(bones_drivers_key) > 0:
			create_limb_drivers(drivers_data)
			#create_limb_drivers(drivers_armature)		
			
		
		# Proxy bones
		bpy.ops.object.mode_set(mode='EDIT') 
		bpy.ops.armature.select_all(action='DESELECT')
		
			# Select
		for bone in limb_control:
			for _side in _sides:
				bproxyname = ""
				bname = bone			
				if bone[-2:] == ".x":
					bproxyname = bone[:-2] + "_proxy.x"
				if bone[-2:] != ".x":
					bproxyname = bone + "_proxy" + _side			
					bname = bone + _side
				
				if get_edit_bone(bproxyname) and get_edit_bone(bname):
					if get_edit_bone(bname).layers[22] == False:#if not disabled (finger, toes...)				
						get_edit_bone(bproxyname).select = True					
					
		bpy.ops.object.mode_set(mode='POSE')		   
		bpy.ops.object.mode_set(mode='EDIT')#debug selection
		
			
			# Duplicate
		bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "constraint_axis":(False, False, False), "constraint_orientation":'LOCAL', "mirror":False, "proportional":'DISABLED', "snap":False, "remove_on_cancel":False, "release_confirm":False})
		
		coef = 1
		axis = 0
		if side == '.r':
			coef = -1
		if limb == "head" or limb == "ear":
			coef *= -6
			axis = 2
		suffix_count = int(float(suffix))# move offset for each dupli, get number of the limb
		
		# Move
		for bone in bpy.context.selected_editable_bones:
			move_bone(bone.name, 0.26*coef*suffix_count, axis)
			
			#rename
		for bone in bpy.context.selected_editable_bones:
			trimmed = bone.name[:-4]
			bone.name = trimmed.replace(trimmed[-2:],  '_dupli_' + suffix + trimmed[-2:])
			#set proxy bone
			get_pose_bone(bone.name)['proxy'] = get_pose_bone(bone.name)['proxy'].replace(bone.name[-2:], '_dupli_' + suffix + bone.name[-2:])
		
		#Rig add - select original bones
		if limb_bones_rig_add:	
			
			edit_rig(rig_add)
			bpy.ops.armature.select_all(action='DESELECT')
			
			#disable x-axis mirror edit
			bpy.context.active_object.data.use_mirror_x = False
			
			for bone in limb_bones_rig_add:	   
				get_edit_bone(bone + side).select = True
		
			bpy.ops.object.mode_set(mode='POSE')		   
			bpy.ops.object.mode_set(mode='EDIT')#debug selection
			
			# Duplicate and move		   
			bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0.2, 0.0, 0.0), "constraint_axis":(False, False, False), "constraint_orientation":'LOCAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":0.111671, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
			
			# Rename				
			for bone in bpy.context.selected_editable_bones:				
				bone.name = bone.name[:-4].replace(side, '_dupli_' + suffix + side)
				
			# Update constraint targets
			bpy.ops.object.mode_set(mode='POSE')
			for b in bpy.context.selected_pose_bones:
				try:
					b.constraints[0].subtarget = b.constraints[0].subtarget.replace(side, '_dupli_' + suffix + side)
				except:
					pass
			
			edit_rig(rig)
			
		
		# Create dupli properties on the c_pos bones
		_s = side
		if side == None:
			_s = ".x"
		
		get_pose_bone('c_pos')[limb + ' ' + suffix + _s] = True
		
	
	
	#--End duplicate_rig()		
	
	
	# Duplicate the selected limb
	side = selected_bone[0][-2:]
	suffix = get_limb_suffix(side, selected_bone[0])[0]
	
		# arm	
	for i in arm_ref_bones:		
		if selected_bone[0] in i+side:					
			duplicate_rig("arm", side, suffix)	 
			duplicate_ref("arm", side, suffix)
			break
			
		# leg	
	for i in leg_ref_bones:
		if selected_bone[0] in i+side:					
			duplicate_rig("leg", side, suffix)		   
			duplicate_ref("leg", side, suffix)
			break
	
	_facial_ref = auto_rig_datas.facial_ref + ["head_ref.x", "neck_ref.x"]
	
		# head
	for i in _facial_ref:		
		if selected_bone[0][:-2] in i:			
			duplicate_rig("head", None, suffix)		   
			duplicate_ref("head", None, suffix)
			break
			
		# ear	
	for i in auto_rig_datas.ear_ref:
		if selected_bone[0][:-2] in i:
			duplicate_rig("ear", side, suffix)
			duplicate_ref("ear", side, suffix)
			break
	
	
	# mode switch necessary to avoid crash currently
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.data.objects[rig_add_name].select_set(state=False)
	bpy.data.objects[rig_add_name].hide_viewport = True		
	
	#display reference layer only
	for i in range(0,32):
		if i != 17:
			bpy.context.active_object.data.layers[i] = False
			
	#enable the proxy picker
	try:		 
		bpy.context.scene.Proxy_Picker.active = True
	except:
		pass
 
	#restore x mirror
	bpy.context.active_object.data.use_mirror_x = mirror_x_state
	
	

	
def get_selected_pair(obj_id):
	obj_1 =	 bpy.context.view_layer.objects.active	 
	obj_2 = None
	
	if bpy.context.selected_objects[0] == obj_1:
		obj_2 = bpy.context.selected_objects[1]
	else:
		obj_2 = bpy.context.selected_objects[0]
			
	if obj_id == 1:
		return obj_1
	if obj_id == 2:
		return obj_2
		

		
def get_rig_add(_rig):
	rig_add_obj = None
	
	for obj_child in _rig.parent.children:
		if 'rig_add' in obj_child.name and not 'prop'in obj_child.name:
			rig_add_obj = obj_child
			break
	
	if 'obj_child' in locals():
		del obj_child
			
	return rig_add_obj
		
def set_active_object(object_name):
	 bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
	 bpy.data.objects[object_name].select_set(state=1)
	 
	 
def is_facial_bone(bone_name):
	for bfacial in auto_rig_datas.facial_deform:
		if bfacial in bone_name:
			return True


def _bind_to_rig(self, context):
	
	print("Binding...")
	time_start = time.time()
	
	sides = ['.l', '.r']	
	rig = bpy.data.objects[bpy.context.view_layer.objects.active.name]
	selection_list = [obj.name for obj in bpy.context.selected_objects if obj.type == "MESH"]
	scene = bpy.context.scene
	
	rig_add = get_rig_add(rig)
	
	if rig_add == None:
		print("rig_add not found, cannot bind. Click Match to Rig to restore it first.")
		
		
	rig_add.hide_viewport = False	
	
	bind_rig = True
	bind_rig_add = True		
	enable_head_refine = True
	improve_eyelids_add = True
	smooth_weights = True
	
	# Copy temporarily the facial rig to the rig_add for better skin of the secondary eyelids		
	if is_facial_enabled(rig) and improve_eyelids_add:	
		print("Setup facial skin...")
		helper_bones = {'eyelid_h_bot_01':['c_eyelid_bot_01', 'c_eyelid_bot_02'], 'eyelid_h_bot_02':['c_eyelid_bot_02', 'c_eyelid_bot_03'], 'eyelid_h_top_01':['c_eyelid_top_01', 'c_eyelid_top_02'], 'eyelid_h_top_02':['c_eyelid_top_02', 'c_eyelid_top_03']}
		
		# Make a dict of bones transforms
		facial_dict = {}
		set_active_object(rig.name)
		bpy.ops.object.mode_set(mode='EDIT')
		
		facial_duplis = []
		facial_duplis_id = [""]
		
		for bone in bpy.context.active_object.data.edit_bones:
			if is_facial_bone(bone.name):
				facial_dict[bone.name] = bone.head.copy(), bone.tail.copy(), bone.roll
				
				_side = bone.name[-2:]
				if	"_dupli_" in bone.name:
					_side = bone.name[-12:]
					if not _side[:-2] in facial_duplis_id:
						facial_duplis_id.append(_side[:-2])
				if not _side in facial_duplis:
					facial_duplis.append(_side)
				
		
		
		#create helpers bones for eyelids			
		for bone in helper_bones:
			for side in sides:
				for id_dupli in facial_duplis_id:
					if get_edit_bone(helper_bones[bone][0] + id_dupli + side):
						new_bone = bpy.context.active_object.data.edit_bones.new(bone+ id_dupli + side) 
						new_bone.head, new_bone.tail = [get_edit_bone(helper_bones[bone][0] + id_dupli + side).tail, get_edit_bone(helper_bones[bone][1] + id_dupli + side).tail]		
		
		

		#temporarily set the lips bones in circle for a better skinning		
		lips_list = ["c_lips_top.x", "c_lips_top.l", "c_lips_top_01.l", "c_lips_smile.l", "c_lips_bot_01.l", "c_lips_bot.l", "c_lips_bot.x", "c_lips_top.r", "c_lips_top_01.r", "c_lips_smile.r", "c_lips_bot_01.r", "c_lips_bot.r"]
		
		lips_bones = {"c_lips_top.x": ["c_lips_top.r", "c_lips_top.l"], "c_lips_top.l":["c_lips_top.x", "c_lips_top_01.l"], "c_lips_top_01.l":["c_lips_top.l", "c_lips_smile.l"], "c_lips_bot_01.l":["c_lips_smile.l", "c_lips_bot.l"], "c_lips_bot.l":["c_lips_bot_01.l", "c_lips_bot.x"], "c_lips_bot.x":["c_lips_bot.l", "c_lips_bot.r"], "c_lips_top.r":["c_lips_top.x", "c_lips_top_01.r"], "c_lips_top_01.r":["c_lips_top.r", "c_lips_smile.r"], "c_lips_bot_01.r":["c_lips_smile.r", "c_lips_bot.r"], "c_lips_bot.r":["c_lips_bot_01.r", "c_lips_bot.x"]}
		
		initial_lips = {}
		
			#store in dict
		for bone in lips_list:
			for dupli_id in facial_duplis_id:			
				bname = bone.replace(bone[-2:], dupli_id) + bone[-2:]
				if get_edit_bone(bname):
					initial_lips[bname] = get_edit_bone(bname).head.copy(), get_edit_bone(bname).tail.copy(), get_edit_bone(bname).roll		
		
		
			
		for bone in lips_bones:			
			for dupli_id in facial_duplis_id:
				bname = bone.replace(bone[-2:], dupli_id) + bone[-2:]
				if initial_lips.get(bname):
					s1 = initial_lips[bname][0]				
					s2 = initial_lips[lips_bones[bone][0][:-2] + dupli_id + lips_bones[bone][0][-2:]][0]
					s3 = initial_lips[lips_bones[bone][1][:-2] + dupli_id + lips_bones[bone][1][-2:]][0]
					
					if get_edit_bone(bname):
						get_edit_bone(bname).head = (s1 + s2)*0.5			
						get_edit_bone(bname).tail = (s1 + s3)*0.5			
		
		bpy.ops.object.mode_set(mode='OBJECT')
		
		# Create or apply facial bones in rigg_add
		"""
		set_active_object(rig_add.name)
		bpy.ops.object.mode_set(mode='EDIT')
		for bone in facial_dict:				
			if not "eyelid" in bone and not "c_eye." in bone:
				if get_edit_bone(bone) == None:					
					current_bone = bpy.context.active_object.data.edit_bones.new(bone)						
				else:
					current_bone = get_edit_bone(bone)
					
				current_bone.head, current_bone.tail, current_bone.roll = facial_dict[bone]
		"""			
			
		
	bpy.ops.object.mode_set(mode='OBJECT')
	
	# Is there a particle system on the mesh? If so operate on a duplicate to preserve particles vertex groups, and transfer weights back at the end
	for obj_name in selection_list: 
		obj = bpy.data.objects[obj_name]
		if len(obj.modifiers) > 0 :
			for mod in obj.modifiers:
				if mod.type == "PARTICLE_SYSTEM":
					bpy.ops.object.select_all(action='DESELECT')
					set_active_object(obj.name)
					bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
					bpy.context.active_object.name = obj.name + "_arp_temp_skin"
					if len(bpy.context.active_object.vertex_groups) > 0:
						bpy.ops.object.vertex_group_remove(all=True)
					
					selection_list.remove(obj.name)
					selection_list.append(bpy.context.active_object.name)
					print("Found particles modifier")
					break
						
	# Is there high resolution meshes? If so reduce the polycount, and transfer weights back at the end
	if bpy.context.scene.arp_optimize_highres:
		for obj_name in selection_list:
			obj = bpy.data.objects[obj_name]
			
			if len(obj.data.polygons) > bpy.context.scene.arp_highres_threshold :	
				print("Found high res mesh:", obj.name)
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(obj.name)
				bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
				bpy.context.active_object.name = obj.name + "_arp_temp_skin"
				
				if len(bpy.context.active_object.vertex_groups) > 0:
					bpy.ops.object.vertex_group_remove(all=True)
					
				# apply modifiers
				bpy.ops.object.convert(target='MESH')
				# decimate
				decim_mod = bpy.context.active_object.modifiers.new("decimate", "DECIMATE")
				decim_mod.ratio = 0.2			
				bpy.ops.object.convert(target='MESH')
				
				selection_list.remove(obj.name)
				selection_list.append(bpy.context.active_object.name)
			
			
	
	for obj_name in selection_list:
		
		obj = bpy.data.objects[obj_name]
		
		#split loose parts better weight assignation
		if scene.arp_bind_split:
			print("Split...")
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object(obj.name)
			bpy.ops.mesh.separate(type='LOOSE')
			split_objects = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
		else:
			split_objects = [obj]
		
		
		
		for i, split_obj in enumerate(split_objects):				
			
			print('skinning split object: ', split_obj.name)
			mesh = split_obj
			
			def get_armature_mod(_name):
				for mod in bpy.context.active_object.modifiers:
					if mod.type == "ARMATURE":
						if mod.object:
							if mod.object.name == _name:
								return mod
							
			
			if bind_rig_add:
				# bind to rig add
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')	
				set_active_object(mesh.name)
				set_active_object(rig_add.name)				
				bpy.ops.object.parent_set(type='ARMATURE_AUTO')
				set_active_object(mesh.name)					
				get_armature_mod(rig_add.name).name = "rig_add"
				
			
			if bind_rig:
				# bind to rig					
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(mesh.name)
				set_active_object(rig.name)
				bpy.ops.object.parent_set(type='ARMATURE_AUTO')
				set_active_object(mesh.name)			
				get_armature_mod(rig.name).name = "rig"				
				
				
			
			# Order modifier stack
			for i in range(0,20):
				bpy.ops.object.modifier_move_up(modifier="rig")
			for i in range(0,20):
				bpy.ops.object.modifier_move_up(modifier="rig_add")
			
			# put mirror at first
			for m in bpy.context.active_object.modifiers:
				if m.type == 'MIRROR':
					for i in range(0,20):
						bpy.ops.object.modifier_move_up(modifier=m.name)
			
			bpy.context.active_object.modifiers["rig"].use_deform_preserve_volume = True
			
			# Make sure it's parented to the rig armature			
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object(mesh.name)
			set_active_object(rig.name)
			bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
			#bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

			
		# merge the split objects		
		bpy.ops.object.select_all(action='DESELECT')
		for split_obj in split_objects:
			set_active_object(split_obj.name)
		
		set_active_object(obj_name)		
		bpy.ops.object.join()			
		
		#transfer the helper eyelids vertex groups to the main eyelids			
		bpy.ops.object.mode_set(mode='OBJECT')		
		
		body = bpy.context.active_object	
		body_name = bpy.context.active_object.name
		
		eyelid_transf = {'eyelid_h_bot_01':['c_eyelid_bot_01', 'c_eyelid_bot_02'], 'eyelid_h_bot_02':['c_eyelid_bot_02', 'c_eyelid_bot_03'], 'eyelid_h_top_01':['c_eyelid_top_01', 'c_eyelid_top_02'], 'eyelid_h_top_02':['c_eyelid_top_02'] }
		
		def transfer_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None, list=None, target_group=None):			
				grp_name_base = group_name[:-2]					
				side = group_name[-2:]
				if "_dupli_" in group_name:
					side = group_name[-12:]
					grp_name_base = group_name[:-12]
					
				# Dict mode
				if list == None:
					if grp_name_base in dict:													
						if dict[grp_name_base][-2:] == '.x':
							side = side[:-2]
						
						for target_grp in dict[grp_name_base]:
							
							_target_group = target_grp + side
							
							if object.vertex_groups.get(_target_group) == None:
								object.vertex_groups.new(name=_target_group)							
								
							object.vertex_groups[_target_group].add([vertice.index], vertex_weight, 'ADD')
							
				# List mode
				if dict == None:
					if grp_name_base in list:		
						if object.vertex_groups.get(target_group):#if exists									
							object.vertex_groups[target_group].add([vertice.index], vertex_weight, 'ADD')	
		
		def copy_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None):			
			grp_name_base = group_name[:-2]					
			side = group_name[-2:]
			if "_dupli_" in group_name:
				side = group_name[-12:]
				grp_name_base = group_name[:-12]				
		
			if grp_name_base in dict:													
				if dict[grp_name_base][-2:] == '.x':
					side = side[:-2]
				
				for target_grp in dict[grp_name_base]:
					
					_target_group = target_grp + side
					
					if object.vertex_groups.get(_target_group) == None:
						object.vertex_groups.new(name=_target_group)							
						
					object.vertex_groups[_target_group].add([vertice.index], vertex_weight, 'REPLACE')	
					
		
		if improve_eyelids_add and is_facial_enabled(rig):				
			for vert in body.data.vertices:
				
				if len(vert.groups) > 0:
					for grp in vert.groups:
						grp_name = body.vertex_groups[grp.group].name										
						weight = grp.weight			
						transfer_weight(object=body, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=eyelid_transf)
					
			
			
			# Delete helpers vertex groups
			for vgroup in body.vertex_groups:
				if "eyelid_h_" in vgroup.name:
					body.vertex_groups.remove(vgroup)		
		
		
		# Improve head weights. for bipeds only.		
		
		if enable_head_refine and body.vertex_groups.get('head.x') and body.vertex_groups.get('neck.x') and rig.rig_type == 'biped':
			print("cleaning head weights...")
			if rig.pose.bones.get('jaw_ref.x'):
				jaw_loc = rig.matrix_world @ rig.pose.bones['jaw_ref.x'].tail
				head_length = (rig.matrix_world @ (rig.pose.bones['head_ref.x'].tail - rig.pose.bones['head_ref.x'].head)).magnitude				
				neck_tolerance = (jaw_loc[2] - head_length * 0.07)				
				remove_from_head = ["neck.x", "c_neck_01.x"]
				remove_other_parts = ["thumb", "hand", "index", "middle", "ring", "pinky", "arm_", "forearm", "shoulder_bend"]
					
				for vert in body.data.vertices:						
					is_in_head_group = False					
					
					if len(vert.groups) > 0:	
						#check if is in head
						for group in vert.groups:
							group_name = body.vertex_groups[group.group].name
							if group_name == "head.x":
								if group.weight > 0.1:
									is_in_head_group = True
						
						for group in vert.groups:
							group_name = body.vertex_groups[group.group].name
							
							#only if facial is disabled (facial provides a better skinning anyway)
							if not is_facial_enabled(rig) and scene.arp_bind_chin:
							
								#if higher than the chin, set almost null weight	
								if	group_name in remove_from_head:													
									if (body.matrix_world @ vert.co)[2] > neck_tolerance:
										body.vertex_groups[group_name].add([vert.index], 0.001, 'REPLACE')
							
							for part in remove_other_parts:
								if part in group_name and is_in_head_group:															
									body.vertex_groups[group_name].add([vert.index], 0.00, 'REPLACE')
			
						
			#smooth neck
			print('smoothing neck weights...')
			bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
			body.vertex_groups.active_index = body.vertex_groups['neck.x'].index
			bpy.context.active_object.data.use_paint_mask_vertex = True
			
			bpy.ops.paint.vert_select_all(action='SELECT')
			bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', factor=0.5, repeat=4, expand=0.0)

			
			
		
		smooth_twists = True
		if rig.arp_secondary_type == "bendy_bones":
			smooth_twists = False
		
		if smooth_twists:		
			print('smoothing twists weights...')	
			
			transfer_twists = {'c_arm_twist_offset' : ['arm_stretch'], 'forearm_stretch' : ['forearm_twist'], 'thigh_twist' : ['thigh_stretch'], 'leg_stretch' : ['leg_twist']}
			copy_weights = {'arm_stretch' : ['c_arm_twist_offset'], 'forearm_twist' : ['forearm_stretch'], 'thigh_stretch' : ['thigh_twist'], 'leg_twist' : ['leg_stretch']}
		
			# merge the stretch and twist groups together		
			for vert in body.data.vertices:					
				if len(vert.groups) > 0:
					for grp in vert.groups:
						grp_name = body.vertex_groups[grp.group].name										
						weight = grp.weight			
						transfer_weight(object=body, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=transfer_twists)
						

			for vert in body.data.vertices:					
				if len(vert.groups) > 0:
					for grp in vert.groups:
						grp_name = body.vertex_groups[grp.group].name										
						weight = grp.weight			
						copy_weight(object=body, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=copy_weights)
			
			# apply a gradient decay based on the bone head/tail position
			for vert in body.data.vertices:
				if len(vert.groups) > 0:
					for grp in vert.groups:
						current_grp_name = body.vertex_groups[grp.group].name
						
						side = current_grp_name[-2:]
						if "_dupli_" in current_grp_name:
							side = current_grp_name[-12:]
							
						for bone_group in transfer_twists:								
							first_bone = bone_group
							second_bone = transfer_twists[bone_group][0]
							
							if current_grp_name == first_bone + side or current_grp_name == second_bone + side:
							
								# get the vertice position projected on the arm bone line
								bone_head = rig.matrix_world @ rig.pose.bones[first_bone + side].head																
								bone_tail = rig.matrix_world @ rig.pose.bones[second_bone + side].tail										
								point = body.matrix_world @ vert.co
								pos = project_point_onto_line(bone_head, bone_tail, point)
								# get the normalized distance as decay factor
								distance = (bone_head - pos).magnitude / (bone_head - bone_tail).magnitude
															
								if first_bone in current_grp_name:										
									body.vertex_groups[first_bone + side].add([vert.index], grp.weight * (1-distance), 'REPLACE')
									
								if second_bone in current_grp_name:
									# if the projected point is below the bone's head, set distance to 0
									fac = get_point_projection_onto_line_factor(bone_head, bone_tail, point)										
									if fac[0] < 0:
										distance = 0	
										
									body.vertex_groups[second_bone + side].add([vert.index], grp.weight * distance, 'REPLACE')
									
								break
		
		if smooth_weights:
		
			print('smoothing eyelids weights...')	
			
			bpy.context.active_object.data.use_paint_mask_vertex = True				
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='DESELECT')
			
			vgroups = body.vertex_groups

			def select_overlap(vgroup1, vgroup2):					
				bpy.ops.mesh.select_all(action='DESELECT')#first					
				vgroups.active_index = vgroups[vgroup1].index
				bpy.ops.object.vertex_group_select()
				mesh = bmesh.from_edit_mesh(body.data)					
				list1 = [vert.index for vert in mesh.verts if vert.select]
				bpy.ops.mesh.select_all(action='DESELECT')#second					
				vgroups.active_index = vgroups[vgroup2].index
				bpy.ops.object.vertex_group_select()					
				list2 = [vert.index for vert in mesh.verts if vert.select]
				bpy.ops.mesh.select_all(action='DESELECT')
				overlap = [i for i in list1 if i in list2]				
			
				for vert in mesh.verts:						
					if vert.index in overlap:							
						vert.select = True
			
			eyelids_smooth = ["c_eyelid_bot_01", "c_eyelid_bot_02", "c_eyelid_bot_03", "c_eyelid_top_01", "c_eyelid_top_02", "c_eyelid_top_03"]
			
				
			for side in sides:	
				for bgroup in eyelids_smooth:						
					if body.vertex_groups.get(bgroup+side):
						# select verts							
						vgroups.active_index = vgroups[bgroup+side].index
						bpy.ops.object.vertex_group_select()
						
				#smooth weights
				bpy.ops.object.mode_set(mode='WEIGHT_PAINT')					
				bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=1, expand=0.5)
				
				
		bpy.context.active_object.data.use_paint_mask_vertex = False
		
		bpy.ops.object.mode_set(mode='OBJECT')				
							
			
		
		# Unselect all verts
		print("Unselect...")
		for v in bpy.context.active_object.data.vertices:
			v.select = False
			
		print("Done")
		
		# End loop objects
	
	# delete the temporary facial bones in rig_add
	if improve_eyelids_add:
		if is_facial_enabled(rig):		
			set_active_object(rig_add.name)
			bpy.ops.object.mode_set(mode='EDIT')		
			bpy.ops.object.mode_set(mode='OBJECT')
			
			# delete helpers bones from rig
			set_active_object(rig.name)
			bpy.ops.object.mode_set(mode='EDIT')
			for bone in helper_bones:
				for side in sides:
					for dupli_id in facial_duplis_id:
						b = get_edit_bone(bone + dupli_id + side)
						if b: 
							bpy.context.active_object.data.edit_bones.remove(b)

			# restore the initial lips transforms
			for bone in initial_lips:
				b = get_edit_bone(bone)
				if b:
					b.head, b.tail, b.roll = initial_lips[bone]
			
			
	
	bpy.ops.object.mode_set(mode='OBJECT')	
	
	# Particles modifier and high resolution meshes case: finally transfer weights from temp to original objects if any 
	for obj_name in selection_list:		
		obj = bpy.data.objects[obj_name]
		
		if "_arp_temp_skin" in obj.name:
			bpy.ops.object.select_all(action='DESELECT')				
			
			# select source object
			set_active_object(obj.name.replace("_arp_temp_skin", ""))
			
			# add armature modifiers
			if bind_rig_add:	
				new_mod = bpy.context.active_object.modifiers.new("rig_add", "ARMATURE")				
				new_mod.object = rig_add
				
				
			if bind_rig:									
				new_mod = bpy.context.active_object.modifiers.new("rig", "ARMATURE")	
				new_mod.object = rig
				new_mod.use_deform_preserve_volume = True				
			
				# Order modifier stack
			for i in range(0,20):
				bpy.ops.object.modifier_move_up(modifier="rig")
			for i in range(0,20):
				bpy.ops.object.modifier_move_up(modifier="rig_add")
			
				# put mirror at first
			for m in bpy.context.active_object.modifiers:
				if m.type == 'MIRROR':
					for i in range(0,20):
						bpy.ops.object.modifier_move_up(modifier=m.name)			
			
				# Make sure it's parented to the rig armature			
			mat = bpy.context.active_object.matrix_world
			bpy.context.active_object.parent = rig
			bpy.context.active_object.matrix_world = mat		
			
			# disable modifiers temporarily for weight transfers
			mod_save = []
			for mod in bpy.context.active_object.modifiers:
				mod_save.append(mod.show_viewport)
				mod.show_viewport = False
			
				
			# select target object
			set_active_object(obj.name)			
			for mod in bpy.context.active_object.modifiers:					
				mod.show_viewport = False				
				
							
			# Transfer weights
			
			bpy.ops.object.data_transfer(data_type='VGROUP_WEIGHTS', vert_mapping='POLYINTERP_NEAREST', layers_select_src='ALL', layers_select_dst='NAME')			
			print("Transferred temp object weights to original object") 
			
			# Clean weights
			set_active_object(obj.name.replace("_arp_temp_skin", ""))
			bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.01)
			
			# Restore modifiers states
			for i, mod in enumerate(bpy.context.active_object.modifiers):
				mod.show_viewport = mod_save[i]				
			
			# Remove temp object
			bpy.data.objects.remove(obj, do_unlink=True)
			print("Deleted temp object")				
	
	
		# Assign to collection		
		if len(rig.users_collection) > 0:
			rig_collecs = [col.name for col in rig.users_collection]
			for scene_collec in bpy.data.collections:				
				for child in scene_collec.children:
					if child.name in rig_collecs:
						name_split = child.name.split('_')
						if len(name_split) == 2:
							if name_split[1] == "rig":
								try:
									scene_collec.objects.link(obj)
									break
								except:
									pass			
	
	
	rig_add.hide_viewport = True	
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(rig.name)
	
	
	
	print("Binding done in " + str( round(time.time() - time_start, 2) ) + " seconds.")


def _unbind_to_rig():
	print('Unbinding...')
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			set_active_object(obj.name)
			
			# delete modifiers
			if len(obj.modifiers) > 0:
				for modifier in bpy.context.active_object.modifiers:
					if modifier.type == 'ARMATURE':
						try:
							bpy.ops.object.modifier_remove(modifier=modifier.name)
						except:
							print('Cannot delete modifier:', modifier.name)				
					
				#try:
				if len(obj.vertex_groups) > 0:
					for vgroup in obj.vertex_groups:
						if not '00_' in vgroup.name:
							obj.vertex_groups.remove(vgroup)
							
			# clear parent and keep transforms
			obj_mat = obj.matrix_world.copy()
			obj.parent = None
			obj.matrix_world = obj_mat
		
 
 
def _edit_ref():
	
	
	#display layer 17 only
	_layers = bpy.context.active_object.data.layers
	#must enabling one before disabling others
	_layers[17] = True	
	for i in range(0,32):
		if i != 17:
			_layers[i] = False 
			
	#set X-Ray
	bpy.context.active_object.show_in_front = True

	  
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='DESELECT')

	#enable x-axis mirror edit
	#bpy.context.active_object.data.use_mirror_x = True

def copy_driver_variables(variables, source_driver, suffix):
					
	for v1 in variables:  
		#create a variable
		clone_var = source_driver.driver.variables.new()
		clone_var.name = v1.name
		clone_var.type = v1.type
		
		#copy variable path
		try:
			clone_var.targets[0].data_path = v1.targets[0].data_path
			# increment bone data path name
			if '.r"]' in v1.targets[0].data_path:									 
				new_d_path = v1.targets[0].data_path
				new_d_path = new_d_path.replace('.r"]', suffix+'"]')
				
			   
			if '.l"]' in v1.targets[0].data_path:
				new_d_path = v1.targets[0].data_path
				new_d_path = new_d_path.replace('.l"]', suffix+'"]')									
				
			clone_var.targets[0].data_path = new_d_path
			
		except:									   
			print("no data_path for: "+ v1.name)
		
		try:
			clone_var.targets[0].bone_target = v1.targets[0].bone_target
		   
			if ".r" in v1.targets[0].bone_target:
				clone_var.targets[0].bone_target = v1.targets[0].bone_target.replace(".r", suffix)
			if ".l" in v1.targets[0].bone_target:
				clone_var.targets[0].bone_target = v1.targets[0].bone_target.replace(".l", suffix)
				
			
		except:
			print("no bone_target for: "+ v1.name)
		try:							
			clone_var.targets[0].transform_type = v1.targets[0].transform_type
		except:
			print("no transform_type for: "+ v1.name)
		try:
			clone_var.targets[0].transform_space = v1.targets[0].transform_space
		except:
			print("no transform_space for: " + v1.name)
		try:
			clone_var.targets[0].id_type = v1.targets[0].id_type
		except:
			print("no id_type for: " + v1.name)	  
		try:		
			clone_var.targets[0].id = v1.targets[0].id
		except:
			print("no id for: " + v1.name)


			
def _finalize_armature(self):

	scn = bpy.context.scene
	
	# Restore the proxy picker state
	try:
		scn.Proxy_Picker.active = self.state_proxy_picker
	except:
		pass
		
	# Restore x-axis mirror edit
	bpy.context.active_object.data.use_mirror_x = self.state_xmirror
		
	# Display layers 16, 0, 1 only	
	_layers = bpy.context.active_object.data.layers
		#must enabling one before disabling others
	_layers[16] = True	
	
	for i in range(0,32):
		if i != 16:
			_layers[i] = False 
	_layers[0] = True
	_layers[1] = True	
	
	

def _initialize_armature(self):
	
	scn = bpy.context.scene
	
	# Disable the proxy picker to avoid bugs
	try:
		self.state_proxy_picker = scn.Proxy_Picker.active	 
		scn.Proxy_Picker.active = False
	except:
		pass	
	
	# Switch to Edit mode
	# DEBUG: switch to Pose mode before, otherwise may lead to random crash with 2.8
	bpy.ops.object.mode_set(mode='POSE')
	bpy.ops.object.mode_set(mode='EDIT')
	
	# Disable x-axis mirror edit
	self.state_xmirror = bpy.context.active_object.data.use_mirror_x
	bpy.context.active_object.data.use_mirror_x = False
	
	# Active all layers 
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True
	


			
def _align_arm_bones(): 
	
	print("\n Aligning arm bones...\n")
	
	scn = bpy.context.scene		
	
	sides = limb_sides.arm_sides
	 
	#get bones
	prepole_name = "arm_fk_pre_pole"
	arm_name = "arm_ref"
	forearm_name = "forearm_ref"
	hand_name = "hand_ref"
	fk_pole_name = "arm_fk_pole"
	ik_pole_name = "c_arms_pole"
	shoulder_name = "shoulder_ref"
	shoulder_track_pole_name = "shoulder_track_pole"
	shoulder_pole_name = "shoulder_pole"
	arm_twist_offset_name = "c_arm_twist_offset"
	hand_rot_twist_name = "hand_rot_twist"
	stretch_arm_name = "c_stretch_arm"
	
	forearms = ["c_forearm_fk", "forearm_fk", "forearm_ik_nostr", "forearm_ik", "forearm_twist", "forearm_stretch", "forearm"]
	
	arms = ["c_arm_ik", "c_arm_fk", "arm_fk", "arm_ik_nostr", "arm_ik_nostr_scale_fix", "arm_ik", "arm_twist", "arm_stretch", "arm", "c_arm_twist_offset"]
	
	hands = ["hand", "c_hand_ik", "c_hand_fk", "c_hand_fk_scale_fix"]
	shoulders = ["shoulder", "c_shoulder"]
	arm_bends = ["c_shoulder_bend", "c_arm_bend", "c_elbow_bend", "c_forearm_bend", "c_wrist_bend"]
   
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	#START ALIGNING BONES
	
	# arms
	for side in sides:
		print("[", side, "]")
		for bone in arms:
			if get_edit_bone(bone+side):
			
				current_arm = get_edit_bone(bone+side)
				ref_arm = get_edit_bone(arm_name+side)
				arm_vec = ref_arm.tail - ref_arm.head
				
						
				if bone == arm_twist_offset_name:
					current_arm.head = ref_arm.head
					current_arm.tail = ref_arm.head + arm_vec * 0.4
					
								   
				else:
					if not 'stretch' in bone and not 'twist' in bone:
						current_arm.head = ref_arm.head
						current_arm.tail = ref_arm.tail
	
					else:
						if 'twist' in bone:
							current_arm.head = ref_arm.head
							current_arm.tail = ref_arm.head + (ref_arm.tail-ref_arm.head)*0.5									
						if 'stretch' in bone:
							
							if bpy.context.object.arp_secondary_type == "additive":
								current_arm.bbone_segments = 0
								current_arm.head = ref_arm.head + (ref_arm.tail-ref_arm.head)*0.5
								current_arm.tail = ref_arm.tail 
								
							
								
							if bpy.context.object.arp_secondary_type == "bendy_bones":
								current_arm.bbone_segments = 20
								current_arm.head = ref_arm.head
								current_arm.tail = ref_arm.tail 
								
		
				if 'c_arm_fk' in bone:
					shoulder_ref = get_edit_bone(shoulder_name+side)
				
					if shoulder_ref.parent:
						current_arm.parent = get_edit_bone('c_' + shoulder_ref.parent.name.replace('_ref.x', '.x'))
					else:
						current_arm.parent = get_edit_bone('c_traj')
						
		
		if "bone" in locals():				
			del bone
	
	
	# Delete drivers of bendy bones if any. Must be done now, generates cyclic dependencies and possible crash otherwise	
	if bpy.context.object.arp_secondary_type == "additive":
		drivers_list = bpy.context.active_object.animation_data.drivers
		deleted_drivers_count = 0
		for side in sides:
			for dri in drivers_list:	
				if '"arm_stretch' + side in dri.data_path or '"forearm_stretch' + side in dri.data_path:
					if "bbone_curveinx" in dri.data_path or "bbone_curveiny" in dri.data_path or "bbone_curveoutx" in dri.data_path or "bbone_curveouty" in dri.data_path or "bbone_scalein" in dri.data_path or "bbone_scaleout" in dri.data_path or "bbone_rollin" in dri.data_path or "bbone_rollout" in dri.data_path or "bbone_easein" in dri.data_path or "bbone_easeout" in dri.data_path: 
						
						bpy.context.active_object.driver_remove(dri.data_path, -1)	
						deleted_drivers_count += 1
			
		print("Deleted", deleted_drivers_count, "drivers")
		
	
	
	# stretch controller
	for side in sides:
		arm = get_edit_bone(arm_name+side)
		stretch_arm = get_edit_bone(stretch_arm_name+side)	
		
		if stretch_arm and arm:
			dir = stretch_arm.tail - stretch_arm.head
			stretch_arm.head = arm.tail
			stretch_arm.tail = stretch_arm.head + dir
		
			# arm pin controller	
			stretch_arm_pin = get_edit_bone("c_stretch_arm_pin"+side)	
			
			dir = stretch_arm.tail - stretch_arm.head
			stretch_arm_pin.head = arm.tail
			stretch_arm_pin.tail = stretch_arm_pin.head + (dir*0.05)		  
	
	
	
		# forearms	
		for bone in forearms:		   
			current_arm = get_edit_bone(bone+side)
			ref_arm = get_edit_bone(forearm_name+side)		

			
			if current_arm and ref_arm:
				if not 'stretch' in bone and not 'twist' in bone:
					current_arm.head = ref_arm.head
					current_arm.tail = ref_arm.tail		
				
				else:
					if 'twist' in bone:
						current_arm.head = ref_arm.head + (ref_arm.tail-ref_arm.head)*0.5
						current_arm.tail = ref_arm.tail					
					if 'stretch' in bone:
						if bpy.context.object.arp_secondary_type == "additive":
							current_arm.bbone_segments = 0
							current_arm.head = ref_arm.head
							current_arm.tail = ref_arm.head + (ref_arm.tail-ref_arm.head)*0.5
							
						if bpy.context.object.arp_secondary_type == "bendy_bones":
							current_arm.bbone_segments = 20
							current_arm.head = ref_arm.head
							current_arm.tail = ref_arm.tail
				
		if "bone" in locals():	
			del bone
		
		for bone in shoulders:			
			current_bone = get_edit_bone(bone+side)
			ref_bone = get_edit_bone(shoulder_name+side)	
				
			if current_bone and ref_bone:
				current_bone.head = ref_bone.head
				current_bone.tail = ref_bone.tail
				current_bone.roll = ref_bone.roll
				
				#parent bone
				if 'c_' in bone:
					if ref_bone.parent:
						if ref_bone.parent.name[:-2][-4:] == "_ref":
							current_bone.parent = get_edit_bone('c_' + ref_bone.parent.name.replace('_ref.x', '.x'))
						else:
							current_bone.parent = ref_bone.parent
					else:
						current_bone.parent = get_edit_bone('c_traj')
		
		if "bone" in locals():	
			del bone
			
	
	
		
		# align secondary bones
	for side in sides:
		for bone in arm_bends:		
			if get_edit_bone(bone + side):
						
				init_selection(bone + side)
								
				current_bone = get_edit_bone(bone+side)
				arm_ref = get_edit_bone(arm_name+side)
				forearm_ref = get_edit_bone(forearm_name+side) 
				length = 0.07
								
				if "shoulder" in bone: 
					current_bone.head = arm_ref.head + (arm_ref.tail-arm_ref.head) * 0.3
					#current_bone.tail = current_bone.head - arm_ref.z_axis * (length*arm_ref.length*4)
					current_bone.tail = current_bone.head + (arm_ref.y_axis * length * arm_ref.length*3)
					current_bone.roll = arm_ref.roll
					
				
				
				if "c_arm_bend" in bone: 
					arm_vec = arm_ref.tail - arm_ref.head
					current_bone.head = arm_ref.head + arm_vec*0.6
					#current_bone.tail = current_bone.head - arm_ref.z_axis * (length*arm_ref.length*4)
					current_bone.tail = current_bone.head + (arm_ref.y_axis * length * arm_ref.length*3)
					current_bone.roll = arm_ref.roll
			
				if "elbow" in bone:			   
					current_bone.head = arm_ref.tail
					#current_bone.tail = current_bone.head - arm_ref.z_axis * (length*arm_ref.length*4)
					current_bone.tail = current_bone.head + (arm_ref.y_axis * length * arm_ref.length*3)
					current_bone.roll = arm_ref.roll
					
			
				if "forearm" in bone:			 
					arm_vec = forearm_ref.tail - forearm_ref.head
					current_bone.head = forearm_ref.head + arm_vec*0.4
					#current_bone.tail = current_bone.head - forearm_ref.z_axis * (length*arm_ref.length*4)
					current_bone.tail = current_bone.head + (forearm_ref.y_axis * length * forearm_ref.length*3)
					current_bone.roll = forearm_ref.roll
				
				if "wrist" in bone: 
					current_bone.head = forearm_ref.tail - forearm_ref.y_axis * 0.12
					#current_bone.tail = current_bone.head - forearm_ref.z_axis * (length*arm_ref.length*4)
					current_bone.tail = current_bone.head + (forearm_ref.y_axis * length * forearm_ref.length*2.5)
					current_bone.roll = forearm_ref.roll
			
		if "bone" in locals():	
			del bone
		
	
	for side in sides:
		#align FK pre-pole	 
		prepole = get_edit_bone(prepole_name + side)
		arm =  get_edit_bone(arm_name + side)
		forearm =  get_edit_bone(forearm_name + side)
		
		if prepole and arm and forearm:
				# center the prepole in the middle of the chain	   
			prepole.head[0] = (arm.head[0] + forearm.tail[0])/2
			prepole.head[1] = (arm.head[1] + forearm.tail[1])/2
			prepole.head[2] = (arm.head[2] + forearm.tail[2])/2
				# point toward the elbow
			prepole.tail[0] = arm.tail[0]
			prepole.tail[1] = arm.tail[1]
			prepole.tail[2] = arm.tail[2]
				
		
			#align FK pole	   
			fk_pole = get_edit_bone(fk_pole_name + side)
				#get arm plane normal
			plane_normal = (arm.head - forearm.tail)
				#pole position
			prepole_dir = prepole.tail - prepole.head
			pole_pos = prepole.tail + (prepole_dir).normalized()
				#ortho project onto plane to align with the knee/elbow	
			pole_pos = project_point_onto_plane(pole_pos, prepole.tail, plane_normal)
				#make sure to keep a correct distance from the elbow
			pole_pos =	arm.tail + (pole_pos-arm.tail).normalized() * (arm.tail-arm.head).magnitude
			
			fk_pole.head = pole_pos#prepole.head + prepole_dir * 14
			fk_pole.tail = Vector((pole_pos)) + prepole_dir #prepole.tail + prepole_dir * 14	
				
			#align IK pole			
			ik_pole = get_edit_bone(ik_pole_name + side)		   
			ik_pole.head = fk_pole.head
			ik_pole.tail = [ik_pole.head[0], ik_pole.head[1], ik_pole.head[2]+(0.165 * arm.length*2)]	  
			
			# set the IK pole constraints if any
			bpy.ops.object.mode_set(mode='POSE')
			pb_ik_pole = get_pose_bone(ik_pole_name + side)
			if len(pb_ik_pole.constraints) > 0:
				for cns in pb_ik_pole.constraints:
					if cns.name == "Child Of_local":
						# try to find the missing target
						if cns.subtarget == "":
							_target_name = "c_root_master.x"
							if get_pose_bone(_target_name):
								cns.subtarget = _target_name
								
						else:
							# check the target is valid, if not set to None
							if not get_pose_bone(cns.subtarget):
								cns.subtarget = ""
						
			
			bpy.ops.object.mode_set(mode='EDIT')
			
	
		# arm and forearm roll adjust
	for side in sides:
		if get_edit_bone(forearm_name + side):
			init_selection(forearm_name+side)		 
			bpy.ops.armature.calculate_roll(type='POS_Z')			
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.pose.select_all(action='DESELECT')
			bpy.ops.object.mode_set(mode='EDIT')
			arm =  get_edit_bone(arm_name + side)
			arm.select = True	
			bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[forearm_name+side].bone	
			bpy.ops.armature.calculate_roll(type='ACTIVE') 
			if side[-2:] == ".r":
				get_edit_bone(forearm_name+side).roll += math.radians(-180)
				get_edit_bone(arm_name+side).roll += math.radians(-180)
	
	for side in sides:
		init_selection("null")
		#copy the roll to other bones	
		
		forearm =  get_edit_bone(forearm_name + side)
		arm =  get_edit_bone(arm_name + side)
		
		if forearm:
			for bone in forearms:		 
				current_bone = get_edit_bone(bone+side).select = True
				get_edit_bone(bone+side).roll = forearm.roll			  
			
			if "bone" in locals():	
				del bone
			
			for bone in arms:
				if get_edit_bone(bone+side):
					get_edit_bone(bone+side).roll = arm.roll

			if "bone" in locals():	
				del bone
		
			# shoulder poles	   
				#track pole		   
			shoulder_track_pole = get_edit_bone(shoulder_track_pole_name + side)		   
			shoulder_track_pole.select = True		  
			shoulder_track_pole.head = (arm.head + get_edit_bone(shoulder_name+side).head)/2
			shoulder_track_pole.head[2] += (0.04*arm.length*4)
			dir = forearm.head - shoulder_track_pole.head
			shoulder_track_pole.tail = shoulder_track_pole.head + dir / 4		 
			shoulder_track_pole.roll = arm.roll

		
			#shoulder visual position			
			p_shoulder = get_edit_bone("c_p_shoulder" + side)
			shoulder = get_edit_bone("c_shoulder" + side)			
			breast_02 = get_edit_bone("c_breast_02" + side)		
			
			if p_shoulder:
				p_shoulder.head = (shoulder.head + shoulder.tail)/2
				p_shoulder.head[2] += 0.05
				
				if breast_02:					
					p_shoulder.head[1] = breast_02.head[1]					
				else:
					p_shoulder.head[1] += -0.08
					
				p_shoulder.tail = p_shoulder.head + (shoulder.tail-shoulder.head)/2
				p_shoulder.tail[2] = p_shoulder.head[2]
				p_shoulder.roll = math.radians(180)	 
				mirror_roll("c_p_shoulder"+side, side)
				
			else:
				print("c_p_shoulder not found")

		
			# pole		  
			shoulder_pole = get_edit_bone(shoulder_pole_name + side)		   
			shoulder_pole.head = arm.head + arm.z_axis * (-0.1 * arm.length*8)
			shoulder_pole.tail = shoulder_pole.head + arm.y_axis * (0.1*arm.length*4)	   
		 

	
	# reset stretchy bone length	
	bpy.ops.object.mode_set(mode='POSE')	
	bpy.ops.object.mode_set(mode='OBJECT')	 
	bpy.ops.object.mode_set(mode='POSE')	 
	
	
	for side in sides:
		
		# Arms IK Stretch
		arm_ik_p = get_pose_bone("arm_ik"+side)
		forearm_ik_p = get_pose_bone("forearm_ik"+side)
		
		
		if arm_ik_p and forearm_ik_p:
			arm_ik_length = arm_ik_p.length
			forearm_ik_length = forearm_ik_p.length
		
			if arm_ik_length < forearm_ik_length:
				arm_ik_p.ik_stretch = (arm_ik_length ** (1 / 3)) / (forearm_ik_length ** (1 / 3))
				forearm_ik_p.ik_stretch = 1.0
			else:
				arm_ik_p.ik_stretch = 1.0
				forearm_ik_p.ik_stretch = (forearm_ik_length ** (1 / 3)) / (arm_ik_length ** (1 / 3))
				
			
			# Set the secondary bones deformation mode: Additive (default) or Bendy bones
					
			drivers_list = bpy.context.active_object.animation_data.drivers
			
			# Bendy bones
			if bpy.context.object.arp_secondary_type == "bendy_bones":
			
				# change parents
				bpy.ops.object.mode_set(mode='EDIT')	
				get_edit_bone("c_shoulder_bend" + side).parent = get_edit_bone("arm_stretch" + side)
				get_edit_bone("c_wrist_bend" + side).parent = get_edit_bone("forearm_stretch" + side)			
				
				# get bones lengths
				arm_length = get_edit_bone("arm_stretch" + side).length
				forearm_length = get_edit_bone("forearm_stretch" + side).length
				
				bpy.ops.object.mode_set(mode='POSE')
				
				# constraints				
				get_pose_bone("arm_stretch" + side).constraints["Copy Location"].head_tail = 0.0
				
				# disable twist deform and rig_add bend bones deform			
				get_pose_bone("c_arm_twist_offset" + side).bone.use_deform = False
				get_pose_bone("forearm_twist" + side).bone.use_deform = False
				_rig_add = get_rig_add(bpy.context.active_object)
				
				for add_bone in auto_rig_datas.arm_bones_rig_add:
					b = _rig_add.pose.bones.get(add_bone + side)
					if b:
						b.bone.use_deform = False	
					else:
						print("Error, " + add_bone + side + " not found")
				
				
				# hide the non-used controllers
				get_pose_bone("c_elbow_bend" + side).bone.hide = True
				get_pose_bone("c_arm_twist_offset" + side).bone.hide = True
				
					# proxy
				if get_pose_bone("c_elbow_bend" + "_proxy" + side):
					get_pose_bone("c_elbow_bend" + "_proxy" + side).bone.hide = True
				if get_pose_bone("c_arm_twist_offset" + "_proxy" + side):
					get_pose_bone("c_arm_twist_offset" + "_proxy" + side).bone.hide = True	
											
			
				# custom handles
				get_pose_bone("arm_stretch" + side).bone.bbone_handle_type_start = "ABSOLUTE"				
				get_pose_bone("arm_stretch" + side).bone.bbone_handle_type_end = "ABSOLUTE"
				get_pose_bone("forearm_stretch" + side).bone.bbone_handle_type_start = "ABSOLUTE"
				get_pose_bone("forearm_stretch" + side).bone.bbone_handle_type_end = "ABSOLUTE"
				
				get_pose_bone("arm_stretch" + side).bone.bbone_custom_handle_start = get_pose_bone("shoulder" + side).bone
				get_pose_bone("arm_stretch" + side).bone.bbone_custom_handle_end = get_pose_bone("forearm_stretch" + side).bone
				
				get_pose_bone("forearm_stretch" + side).bone.bbone_custom_handle_start = get_pose_bone("arm_stretch" + side).bone
				get_pose_bone("forearm_stretch" + side).bone.bbone_custom_handle_end = get_pose_bone("hand_rot_twist" + side).bone
				
				# Set the drivers			
							
				# driver assignation functions
				def configure_driver_bbone(driv = None, bone = None, b_side = None, loc = None, type = None, fac = None):	
										
					_expression = "var"
					if fac:
						_expression += "*" + str(fac)
						
					driv.driver.expression = _expression			
					
					# create a new var if necessary
					if len(driv.driver.variables) == 0:
						base_var = driv.driver.variables.new()
					else:
						base_var = driv.driver.variables[0]
						
					base_var.type = 'SINGLE_PROP'
					base_var.name = 'var'
					base_var.targets[0].id = bpy.context.active_object
					
					if type == "location":
						base_var.targets[0].data_path = 'pose.bones["' + bone + b_side + '"].location[' + str(loc) + ']'
					elif type == "scale":
						base_var.targets[0].data_path = 'pose.bones["' + bone + b_side + '"].scale[0]'
					elif type == "rotation":
						base_var.targets[0].data_path = 'pose.bones["' + bone + b_side + '"].rotation_euler[1]'
									

					# Arm bones (not forearm)
				driver_in_x = None
				driver_out_x = None
				driver_in_y = None
				driver_out_y = None
				driver_scale_in = None
				driver_scale_out = None
				driver_rot_in = None
				driver_rot_out = None
				driver_ease_in = None
				driver_ease_out = None
				
				# are the drivers already created?
				for dri in drivers_list:	
					if '"arm_stretch' + side in dri.data_path:
						if "bbone_curveinx" in dri.data_path: 
							driver_in_x = dri.data_path
						if "bbone_curveiny" in dri.data_path:
							driver_in_y = dri.data_path
						if "bbone_curveoutx" in dri.data_path:
							driver_out_x = dri.data_path
						if "bbone_curveouty" in dri.data_path:
							driver_out_y = dri.data_path
						if "bbone_scalein" in dri.data_path:
							driver_scale_in = dri.data_path
						if "bbone_scaleout" in dri.data_path:
							driver_scale_out = dri.data_path
						if "bbone_rotin" in dri.data_path:
							driver_rot_in = dri.data_path
						if "bbone_rotout" in dri.data_path:
							driver_rot_out = dri.data_path
						if "bbone_easein" in dri.data_path:
							driver_ease_in = dri.data_path
						if "bbone_easeout" in dri.data_path:
							driver_ease_out = dri.data_path
				
				fac_offset = "2.2"
				fac_ease = "8/"
								
				# Driver In X				
				if driver_in_x:				
					dr_inx = drivers_list.find(driver_in_x)
				else:
					dr_inx = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_curveinx', -1)		
					
				configure_driver_bbone(driv = dr_inx, bone = "c_shoulder_bend", b_side = side, loc = 0, type = "location", fac=fac_offset)#+str(arm_length))		
							
				# Driver In Y				
				if driver_in_y:			
					dr_iny = drivers_list.find(driver_in_y)
				else:
					dr_iny = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_curveiny', -1)		
					
				configure_driver_bbone(driv = dr_iny, bone = "c_shoulder_bend", b_side = side, loc = 2, type = "location", fac=fac_offset)#+str(arm_length))	
										
				# Driver Out X				
				if driver_out_x:						
					dr_outx = drivers_list.find(driver_out_x)
				else:
					dr_outx = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_curveoutx', -1)		
					
				configure_driver_bbone(driv = dr_outx, bone = "c_arm_bend", b_side = side, loc = 0, type = "location", fac=fac_offset)#+str(arm_length))	
										
				# Driver Out Y				
				if driver_out_y:					
					dr_outy = drivers_list.find(driver_out_y)
				else:
					dr_outy = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_curveouty', -1)		
				
				configure_driver_bbone(driv = dr_outy, bone = "c_arm_bend", b_side = side, loc = 2, type = "location", fac=fac_offset)#+str(arm_length))
				
				# Driver Scale In
				if driver_scale_in:					
					dr_scalein = drivers_list.find(driver_scale_in)
				else:
					dr_scalein = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_scalein', -1)

				configure_driver_bbone(driv = dr_scalein, bone = "c_shoulder_bend", b_side = side, type = "scale")
				
				# Driver Scale Out
				if driver_scale_out:					
					dr_scaleout = drivers_list.find(driver_scale_out)
				else:
					dr_scaleout = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_scaleout', -1)

				configure_driver_bbone(driv = dr_scaleout, bone = "c_arm_bend", b_side = side, type = "scale")
				
				# Driver Rot In
				if driver_rot_in:					
					dr_rotin = drivers_list.find(driver_rot_in)
				else:
					dr_rotin = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_rollin', -1)

				configure_driver_bbone(driv = dr_rotin, bone = "c_shoulder_bend", b_side = side, type = "rotation")
				
				# Driver Rot Out
				if driver_rot_out:					
					dr_rotout = drivers_list.find(driver_rot_out)
				else:
					dr_rotout = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_rollout', -1)

				configure_driver_bbone(driv = dr_rotout, bone = "c_arm_bend", b_side = side, type = "rotation")
				
				# Driver Ease In
				if driver_ease_in:					
					dr_easin = drivers_list.find(driver_ease_in)
				else:
					dr_easin = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_easein', -1)

				configure_driver_bbone(driv = dr_easin, bone = "c_shoulder_bend", b_side = side, loc = 1, type = "location", fac=fac_ease+str(arm_length))
				
				# Driver Ease Out
				if driver_ease_out:					
					dr_easout = drivers_list.find(driver_ease_out)
				else:
					dr_easout = bpy.context.active_object.driver_add('pose.bones["' + "arm_stretch" + side + '"].bbone_easeout', -1)

				configure_driver_bbone(driv = dr_easout, bone = "c_arm_bend", b_side = side, loc = 1, type = "location", fac='-'+fac_ease+str(arm_length))
					

					# Forearm bones
				driver_in_x = None
				driver_out_x = None
				driver_in_y = None
				driver_out_y = None
				driver_scale_in = None
				driver_scale_out = None
				driver_rot_in = None
				driver_rot_out = None
				driver_ease_in = None
				driver_ease_out = None
				
				for dri in drivers_list:	
					if '"forearm_stretch' + side in dri.data_path:
						if "bbone_curveinx" in dri.data_path: 
							driver_in_x = dri.data_path
						if "bbone_curveiny" in dri.data_path:
							driver_in_y = dri.data_path
						if "bbone_curveoutx" in dri.data_path:
							driver_out_x = dri.data_path
						if "bbone_curveouty" in dri.data_path:
							driver_out_y = dri.data_path
						if "bbone_scalein" in dri.data_path:
							driver_scale_in = dri.data_path
						if "bbone_scaleout" in dri.data_path:
							driver_scale_out = dri.data_path
						if "bbone_rotin" in dri.data_path:
							driver_rot_in = dri.data_path
						if "bbone_rotout" in dri.data_path:
							driver_rot_out = dri.data_path
						if "bbone_easein" in dri.data_path:
							driver_ease_in = dri.data_path
						if "bbone_easeout" in dri.data_path:
							driver_ease_out = dri.data_path
						
								
				# Driver In X				
				if driver_in_x:				
					dr_inx = drivers_list.find(driver_in_x)
				else:
					dr_inx = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_curveinx', -1)		
					
				configure_driver_bbone(driv = dr_inx, bone = "c_forearm_bend", b_side = side, loc = 0, type = "location", fac=fac_offset)#+str(forearm_length)) 
							
				# Driver In Y				
				if driver_in_y:			
					dr_iny = drivers_list.find(driver_in_y)
				else:
					dr_iny = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_curveiny', -1)		
					
				configure_driver_bbone(driv = dr_iny, bone = "c_forearm_bend", b_side = side, loc = 2, type = "location", fac=fac_offset)#+str(forearm_length))			
										
				# Driver Out X				
				if driver_out_x:						
					dr_outx = drivers_list.find(driver_out_x)
				else:
					dr_outx = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_curveoutx', -1)		
					
				configure_driver_bbone(driv = dr_outx, bone = "c_wrist_bend", b_side = side, loc = 0, type = "location", fac=fac_offset)#+str(forearm_length))			
										
				# Driver Out Y				
				if driver_out_y:					
					dr_outy = drivers_list.find(driver_out_y)
				else:
					dr_outy = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_curveouty', -1)		
				
				configure_driver_bbone(driv = dr_outy, bone = "c_wrist_bend", b_side = side, loc = 2, type = "location", fac=fac_offset)#+str(forearm_length))		

				# Driver Scale In
				if driver_scale_in:					
					dr_scalein = drivers_list.find(driver_scale_in)
				else:
					dr_scalein = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_scalein', -1)

				configure_driver_bbone(driv = dr_scalein, bone = "c_forearm_bend", b_side = side, type = "scale")
				
				# Driver Scale Out
				if driver_scale_out:					
					dr_scaleout = drivers_list.find(driver_scale_out)
				else:
					dr_scaleout = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_scaleout', -1)

				configure_driver_bbone(driv = dr_scaleout, bone = "c_wrist_bend", b_side = side, type = "scale")
				
				# Driver Rot In
				if driver_rot_in:					
					dr_rotin = drivers_list.find(driver_rot_in)
				else:
					dr_rotin = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_rollin', -1)

				configure_driver_bbone(driv = dr_rotin, bone = "c_forearm_bend", b_side = side, type = "rotation")
				
				# Driver Rot Out
				if driver_rot_out:					
					dr_rotout = drivers_list.find(driver_rot_out)
				else:
					dr_rotout = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_rollout', -1)

				configure_driver_bbone(driv = dr_rotout, bone = "c_wrist_bend", b_side = side, type = "rotation")
				
				# Driver Ease In
				if driver_ease_in:					
					dr_easin = drivers_list.find(driver_ease_in)
				else:
					dr_easin = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_easein', -1)

				configure_driver_bbone(driv = dr_easin, bone = "c_forearm_bend", b_side = side, loc = 1, type = "location", fac=fac_ease+str(forearm_length))
				
				# Driver Ease Out
				if driver_ease_out:					
					dr_easout = drivers_list.find(driver_ease_out)
				else:
					dr_easout = bpy.context.active_object.driver_add('pose.bones["' + "forearm_stretch" + side + '"].bbone_easeout', -1)

				configure_driver_bbone(driv = dr_easout, bone = "c_wrist_bend", b_side = side, loc = 1, type = "location", fac='-'+fac_ease+str(forearm_length))
				
			
			# else, additive mode
			if bpy.context.object.arp_secondary_type == "additive":
						
				
				# change parents
				bpy.ops.object.mode_set(mode='EDIT')
				get_edit_bone("c_shoulder_bend" + side).parent = get_edit_bone("arm_twist" + side)
				get_edit_bone("c_wrist_bend" + side).parent = get_edit_bone("forearm_twist" + side)
				bpy.ops.object.mode_set(mode='POSE')
			
				# custom handles
				get_pose_bone("arm_stretch" + side).bone.bbone_handle_type_start = 'AUTO'
				get_pose_bone("arm_stretch" + side).bone.bbone_handle_type_end = 'AUTO'
				get_pose_bone("forearm_stretch" + side).bone.bbone_handle_type_start = 'AUTO'
				get_pose_bone("forearm_stretch" + side).bone.bbone_handle_type_end = 'AUTO'
				
				# constraints
				get_pose_bone("arm_stretch" + side).constraints["Copy Location"].head_tail = 1.0
				
				# enable twist deform and rig_add bend bones
					# if not disabled
				if get_pose_bone("c_arm_twist_offset" + side).bone.layers[22] == False:
					get_pose_bone("c_arm_twist_offset" + side).bone.use_deform = True
					get_pose_bone("forearm_twist" + side).bone.use_deform = True			
					_rig_add = get_rig_add(bpy.context.active_object)		
						
					for add_bone in auto_rig_datas.arm_bones_rig_add:
						rig_add_pbone = _rig_add.pose.bones.get(add_bone + side)
						if rig_add_pbone:
							rig_add_pbone.bone.use_deform = True
					
				# Display the used controllers
				get_pose_bone("c_elbow_bend" + side).bone.hide = False			
				get_pose_bone("c_arm_twist_offset" + side).bone.hide = False	
				
					# proxy
				if get_pose_bone("c_elbow_bend" + "_proxy" + side):
					get_pose_bone("c_elbow_bend" + "_proxy" + side).bone.hide = False
				if get_pose_bone("c_arm_twist_offset" + "_proxy" + side):
					get_pose_bone("c_arm_twist_offset" + "_proxy" + side).bone.hide = False 
						
				
						
						
				
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	for side in sides:
		
		# align hand_rot_twist			
		hand =	get_edit_bone(hand_name + side)
		hand_rot_twist = get_edit_bone(hand_rot_twist_name + side)
		forearm = get_edit_bone(forearm_name + side)	
		
		if hand and hand_rot_twist:
			
			hand_rot_twist.head = hand.head + (hand.y_axis * 0.02 * hand.length*15) + (hand.z_axis * 0.04 * hand.length*15)#mult by hand.length to keep proportional when scaling the armature object and applying scale
			
			hand_rot_twist.tail = hand_rot_twist.head.copy() + (forearm.y_axis * 0.02 * hand.length*15)
			#hand_rot_twist.roll = forearm.roll		
			
			# align hands
			hands = ["hand"+side, "c_hand_ik"+side, "c_hand_fk"+side, "c_hand_fk_scale_fix"+side]

			for bone in hands:			
				current_hand = bpy.context.active_object.data.edit_bones[bone]
				ref_hand = bpy.context.active_object.data.edit_bones[hand_name + side]
				current_hand.head = ref_hand.head
				current_hand.tail = ref_hand.tail
				current_hand.roll = ref_hand.roll
			
			if "bone" in locals():	
				del bone
			
			
			# Align hand_rot_twist and forearm_twist rolls to the hand roll
			init_selection("null")		
			get_edit_bone(hand_rot_twist_name + side).select = True
			get_edit_bone(hand_name + side).select = True
			bpy.context.active_object.data.edit_bones.active = bpy.context.active_object.data.edit_bones[hand_name +side]	
			bpy.ops.armature.calculate_roll(type='ACTIVE')
			
			
			init_selection("null")		
			get_edit_bone("forearm_twist" + side).select = True
			get_edit_bone(hand_name + side).select = True		
			bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[hand_name +side].bone		
			bpy.ops.armature.calculate_roll(type='ACTIVE')		
			
			get_edit_bone("forearm_twist"+side).roll += math.radians(180)
			hand_rot_twist.roll += math.radians(180)
	
	# Align fingers
	print("	 Aligning fingers...")
	fingers_rot_prop = bpy.context.active_object.rig_fingers_rot
	fingers_shape_type = bpy.context.active_object.arp_fingers_shape_style
	
	for side in sides:		
		# Collect fingers
		fingers = []
		hand_def = get_edit_bone("hand" + side)
		
		if hand_def:
			init_selection(hand_def.name)
			bpy.ops.armature.select_similar(type='CHILDREN')
			
			if side[-2:] == ".l":
				opposite = ".r"
			else:
				opposite = ".l"
				
			for bone in bpy.context.selected_editable_bones[:]:
				if "thumb" in bone.name or "index" in bone.name or "middle" in bone.name or "ring" in bone.name or "pinky" in bone.name:
					if not opposite in bone.name:# fingers only, and one side only
						fingers.append(bone.name)
			
			
			# Align
			for finger in fingers:				
				init_selection(finger)			   
				substract = 0
				if len(side) > 2:
					 substract = 10
			
				if finger[:2] == "c_":
					bone_name = finger[2:-2-substract]+"_ref"+ side 
				else:
					bone_name = finger[:-2-substract]+"_ref"+ side		
				
				if "bend_all" in finger: # exception for the "bend_all" fingers to find the ref name
					bone_name = finger[:-11-substract]+"1_ref"+ side		 
				if "thumb1_base" in finger: # thumb1 base case
					bone_name = "thumb1_ref"+ side
				if "_rot." in finger or "_rot_" in finger: # rotation bone case
					bone_name = finger[2:-6-substract] + "_ref" + side
					
				
				bone_ref = get_edit_bone(bone_name)
				
				
				if get_edit_bone(finger) and bone_ref:
					current_bone = get_edit_bone(finger)
					current_bone.head = bone_ref.head
					current_bone.tail = bone_ref.tail
					current_bone.roll = bone_ref.roll  
					
					# Set shape
					# if not a user defined custom shape					
					if finger[:2] == "c_" and get_pose_bone(finger).custom_shape:									
						# CRASH AROUND HERE
						if not "cs_user" in get_pose_bone(finger).custom_shape.name:						
						
							bpy.ops.object.mode_set(mode='POSE')
						
							if not "_base" in finger:	
								cs_obj = None
								if fingers_shape_type == "box":			
									cs_obj = bpy.data.objects.get("cs_box")
									
								if fingers_shape_type == "circle":									
									cs_obj = bpy.data.objects.get("cs_torus_04")
								
								if cs_obj:
									get_pose_bone(finger).custom_shape = cs_obj						
								
						
							bpy.ops.object.mode_set(mode='EDIT')
							
			
			if "finger" in locals():		
				del finger
			if "bone_ref" in locals():		
				del bone_ref
			
			print("	 Setup fingers rotations...")
			
			#configure fingers rotation		
			for finger in fingers:				
				#if first phalange	controller	
				finger_name = finger.replace(side, "")
				if bpy.context.scene.arp_debug_mode:
					print("FINGER NAME", finger_name, "from", finger)
					
				
				# set rot from scale
				if finger_name[-1:] == "1" and finger[:2] == "c_":
					add_bone_name = finger[2:]				
					rot_bone = finger.replace(side, "_rot" + side)
					_name = rot_bone.split('_')[1].replace("1", "2")	
					rot_bone = rot_bone.replace(rot_bone.split('_')[1], _name)
					
					
					#if scale-rotation is set
					if fingers_rot_prop != 'no_scale':								
						
						#create bone if necessary					
						if get_edit_bone(add_bone_name) == None:						
							new_bone = bpy.context.active_object.data.edit_bones.new(add_bone_name) 
							new_bone.head = get_edit_bone(finger).head
							new_bone.tail = get_edit_bone(finger).tail
							new_bone.roll = get_edit_bone(finger).roll					
							
							#set layer
							for i in range(0,31):						
								new_bone.layers[i] = False						
							new_bone.layers[8] = True
							
							
							#set deform					
							get_edit_bone(finger).use_deform = False
							new_bone.use_deform = True
							
							#set parent							
							new_bone.parent = get_edit_bone(finger)							
							get_edit_bone(rot_bone).parent = new_bone
							
							#set constraint
							bpy.ops.object.mode_set(mode='POSE')
							cns = get_pose_bone(add_bone_name).constraints.new('COPY_SCALE')
							cns.target = bpy.context.active_object
							cns.subtarget = "hand" + side
							bpy.ops.object.mode_set(mode='EDIT')
						
							#set custom shape transform					
							get_pose_bone(finger).custom_shape_transform = get_pose_bone(add_bone_name)
							
						#assign parameters						
						get_edit_bone(add_bone_name).use_inherit_scale = False			
						bpy.ops.object.mode_set(mode='POSE')
						
						get_pose_bone(add_bone_name).constraints[0].mute = False
						
						#create new driver var if necessary					
						bend_all_name = finger.split('_')[1].replace(side, '')[:-1] + "_bend_all" + side
						
						if bpy.context.scene.arp_debug_mode:
							print("FINGER", finger)
							print("BEND ALL NAME", bend_all_name)
						
						dp = 'pose.bones["' + bend_all_name + '"].rotation_euler'
						dr = bpy.context.active_object.animation_data.drivers.find(dp)
					
						if dr:
							found_var = False
							for var in dr.driver.variables:
								if "var_002" in var.name:
									found_var = True
							
							if not found_var:					
								new_var = dr.driver.variables.new()
								new_var.name = "var_002"
								new_var.type = 'SINGLE_PROP'
								new_var.targets[0].id = dr.driver.variables[0].targets[0].id
								new_var.targets[0].data_path = 'pose.bones["' + finger + '"].scale[0]'
							
							dr.driver.expression = '-var - var_001 - (1-var_002)*2.5'
							
							print(rot_bone)
							rot_bone1_name = rot_bone[2:].replace("2_","1_").replace('_rot', '')
							print(rot_bone1_name)
							#rot_bone1_name = rot_bone[2:].split('_')[0].replace('2','1')
							rot_bone1 = get_pose_bone(rot_bone1_name)
							if rot_bone1:
								const = [x for x in rot_bone1.constraints if x.type == "COPY_ROTATION"]
								if len(const) > 0:	
									if fingers_rot_prop == 'scale_2_phalanges':						
										const[0].influence = 0.0
									else:#scale_3_phalanges
										const[0].influence = 1.0	
								else:
									print(rot_bone1.name + ": No constraint found, could not configure auto fingers rotation")
							else:
								print(rot_bone1_name, "not found")
						else:
							print("driver:", 'pose.bones["' + bend_all_name + '"].rotation_euler', 'not found, could not configure auto fingers rotation')
														
						
								
					else:#if finger_rot == "no_scale"	
						#only if the new bone setup exists
						
						if get_edit_bone(add_bone_name):
						
							#assign params
							get_edit_bone(add_bone_name).use_inherit_scale = True
							bpy.ops.object.mode_set(mode='POSE')
							get_pose_bone(add_bone_name).constraints[0].mute = True
							
							"""
							rot_bone1 = get_pose_bone(rot_bone.replace("2","1"))
							const = [x for x in rot_bone1.constraints if x.type == "COPY_ROTATION"]					
							const[0].influence = 1.0				
							"""
							
							#set driver expressions						
							bend_all_name = finger.split('_')[1].split('.')[0][:-1] + "_bend_all" + side						
							dp = 'pose.bones["' + bend_all_name + '"].rotation_euler'
							
							#print("DP", dp)
							#print("Side", side)
							dr = bpy.context.active_object.animation_data.drivers.find(dp)	
							
							dr.driver.expression = '-var - var_001'				
							
					
				bpy.ops.object.mode_set(mode='EDIT')
				
			if "finger" in locals():
				del finger
	
			
			# set auto rotation constraint from the pinky finger if any
			bpy.ops.object.mode_set(mode='POSE')
			fingers_autorot_dict = {'c_middle1_base':0.33, 'c_ring1_base':0.66}
			for finger_name in fingers_autorot_dict:				
				pinky = get_pose_bone("c_pinky1_base" + side)
				# set the constraint if there's the pinky
				current_finger = get_pose_bone(finger_name + side)
				if current_finger and pinky:
					cns = current_finger.constraints.get("Copy Rotation")
					if not cns:
						cns = current_finger.constraints.new("COPY_ROTATION")
						cns.name = "Copy Rotation"
					cns.target = bpy.context.active_object
					cns.subtarget = pinky.name
					cns.use_offset = True
					cns.owner_space = cns.target_space = 'LOCAL'
					cns.influence = fingers_autorot_dict[finger_name]
					
				# remove the constraint if there's no pinky
				if current_finger and not pinky:
					cns = current_finger.constraints.get("Copy Rotation")
					if cns:
						current_finger.constraints.remove(cns)
					
				
			bpy.ops.object.mode_set(mode='EDIT')
				
	
	if bpy.context.scene.arp_debug_mode == True:	   
		print("\n FINISH ALIGNING ARM BONES...\n")
	
def mirror_roll(bone, side):
	if side[-2:] == ".r":
		get_edit_bone(bone).roll *= -1

def _align_leg_bones():
	
	
	print("\n Aligning leg bones...\n")		
	
	#define the side
	sides = limb_sides.leg_sides
	 
	#get bones
	prepole_name = "leg_fk_pre_pole"
	thigh_name = "thigh_ref"
	leg_name = "leg_ref"
	foot_name = "foot_ref"
	toes_name = "toes_ref"
	fk_pole_name = "leg_fk_pole"
	ik_pole_name = "c_leg_pole"
	foot_pole_name = "foot_pole" 
	stretch_leg_name = "c_stretch_leg"	  
	
	legs = ["c_leg_fk", "leg_fk", "leg_ik_nostr", "leg_ik", "leg_twist", "leg_stretch", "leg"]
	
	thighs = ["c_thigh_ik", "c_thigh_fk", "thigh_fk", "thigh_ik_nostr", "thigh_ik", "thigh_twist", "thigh_stretch", "thigh"]
	
	feet = ["foot", "foot_fk", "c_foot_fk", "foot_ik", "c_foot_ik", "foot_snap_fk", "foot_ik_target", "c_foot_bank_01", "c_foot_bank_02", "c_foot_heel", "c_foot_01"]
		
	leg_bends = ["c_thigh_bend_contact", "c_thigh_bend_01", "c_thigh_bend_02", "c_knee_bend", "c_leg_bend_01", "c_leg_bend_02", "c_ankle_bend"]
	
	
	bpy.ops.object.mode_set(mode='EDIT')	

	
	# align thighs
	for side in sides:
		print("[", side, "]")
		for bone in thighs: 
			if get_edit_bone(bone+side):
				current_bone = get_edit_bone(bone+side)
				ref_bone = get_edit_bone(thigh_name+side)
				
				if not 'twist' in bone and not 'stretch' in bone:			
					current_bone.head = ref_bone.head
					current_bone.tail = ref_bone.tail	
				
				else:
					if 'twist' in bone:
						current_bone.head = ref_bone.head
						current_bone.tail = ref_bone.head + (ref_bone.tail-ref_bone.head)*0.5					
					if 'stretch' in bone:
						if bpy.context.object.arp_secondary_type == "additive":
							current_bone.bbone_segments = 0
							current_bone.head = ref_bone.head + (ref_bone.tail-ref_bone.head)*0.5
							current_bone.tail = ref_bone.tail		
						if bpy.context.object.arp_secondary_type == "bendy_bones":
							current_bone.bbone_segments = 20
							current_bone.head = ref_bone.head
							current_bone.tail = ref_bone.tail		
		
		if "bone" in locals():
			del bone
		
		
		#stretch bone		  
		stretch_leg = get_edit_bone(stretch_leg_name+side)
		thigh = get_edit_bone(thigh_name+side)
		
		if stretch_leg and thigh:
			dir = stretch_leg.tail - stretch_leg.head
			stretch_leg.head = thigh.tail
			stretch_leg.tail = stretch_leg.head + dir	   

			# pin controller	   
			stretch_leg_pin = get_edit_bone("c_stretch_leg_pin"+side)
			thigh = get_edit_bone(thigh_name+side)
			dir = stretch_leg_pin.tail - stretch_leg_pin.head
			stretch_leg_pin.head = thigh.tail
			stretch_leg_pin.tail = stretch_leg_pin.head + dir
	  
		# align legs
		for bone in legs:		   
			current_bone = get_edit_bone(bone+side)
			ref_bone = get_edit_bone(leg_name+side) 
			
			if current_bone and ref_bone:
				if not 'stretch' in bone and not 'twist' in bone:
					current_bone.head = ref_bone.head
					current_bone.tail = ref_bone.tail
				else:
					if 'twist' in bone:
						current_bone.head = ref_bone.head + (ref_bone.tail-ref_bone.head)*0.5
						current_bone.tail = ref_bone.tail					
					if 'stretch' in bone:
						if bpy.context.object.arp_secondary_type == "additive":
							current_bone.bbone_segments = 0
							current_bone.head = ref_bone.head
							current_bone.tail = ref_bone.head + (ref_bone.tail-ref_bone.head)*0.5
							
						if bpy.context.object.arp_secondary_type == "bendy_bones":
							current_bone.bbone_segments = 20
							current_bone.head = ref_bone.head
							current_bone.tail = ref_bone.tail
		
		if "bone" in locals():
			del bone			
	
	
	# Delete drivers of bendy bones if any. Must be done now, generates cyclic dependencies and possible crash otherwise	
	if bpy.context.object.arp_secondary_type == "additive":
		drivers_list = bpy.context.active_object.animation_data.drivers
		deleted_drivers_count = 0
		for side in sides:		
			for dri in drivers_list:	
				if '"thigh_stretch' + side in dri.data_path or '"leg_stretch' + side in dri.data_path:
					if "bbone_curveinx" in dri.data_path or "bbone_curveiny" in dri.data_path or "bbone_curveoutx" in dri.data_path or "bbone_curveouty" in dri.data_path or "bbone_scalein" in dri.data_path or "bbone_scaleout" in dri.data_path or "bbone_rollin" in dri.data_path or "bbone_rollout" in dri.data_path or "bbone_easein" in dri.data_path or "bbone_easeout" in dri.data_path:
						
						bpy.context.active_object.driver_remove(dri.data_path, -1)
						deleted_drivers_count += 1
						
		print("Deleted", deleted_drivers_count, "drivers")
			
	
	for side in sides:	  
		# align secondary bones
		for bone in leg_bends:
			if get_edit_bone(bone + side):
				init_selection(bone+side)
				current_bone = get_edit_bone(bone+side)
				thigh = get_edit_bone(thigh_name+side)
				leg = get_edit_bone(leg_name+side)
				thigh_vec = thigh.tail - thigh.head
				leg_vec = leg.tail - leg.head
				length = 0.04
				
				if "contact" in bone: 
					current_bone.head = thigh.head + thigh_vec*0.15
					current_bone.tail = current_bone.head + (thigh.y_axis * length * leg.length*3)
					current_bone.roll = thigh.roll
					
				if "thigh_bend_01" in bone:			   
					current_bone.head = thigh.head + thigh_vec*0.4				
					current_bone.tail = current_bone.head + (thigh.y_axis * length * leg.length*3)
					current_bone.roll = thigh.roll
					
				if "thigh_bend_02" in bone:			   
					current_bone.head = thigh.head + thigh_vec*0.75
					current_bone.tail = current_bone.head + (thigh.y_axis * length * leg.length*3)
					current_bone.roll = thigh.roll
					
				if "knee" in bone:			  
					current_bone.head = thigh.tail
					current_bone.tail = current_bone.head + (thigh.y_axis * length * leg.length*3)
					current_bone.roll = thigh.roll
					
				if "leg_bend_01" in bone:			
					current_bone.head = leg.head + leg_vec*0.25
					current_bone.tail = current_bone.head + (leg.y_axis * length * leg.length*3)
					current_bone.roll = leg.roll
					
				if "leg_bend_02" in bone:			
					current_bone.head = leg.head + leg_vec*0.6
					current_bone.tail = current_bone.head + (leg.y_axis * length * leg.length*3)
					current_bone.roll = leg.roll
					
				if "ankle" in bone: 
					current_bone.head = leg.head + leg_vec*0.85
					current_bone.tail = current_bone.head + (leg.y_axis * length * leg.length*3)
					current_bone.roll = leg.roll
					
				#set roll
				#bpy.ops.armature.calculate_roll(type='POS_X')
		
		if "bone" in locals():
			del bone
		
		
	def norm(x):
		return math.sqrt(x.dot(x))
	 
	def project_onto_plane(x, n):
		#x = point coord (vector3)
		#n = plane normal (vector3) 
		d = x.dot(n) / norm(n)
		p = [d * n.normalized()[i] for i in range(len(n))]
		return [x[i] - p[i] for i in range(len(x))] 
	
	 
	for side in sides:	 
		
		prepole = get_edit_bone(prepole_name + side)
		thigh =	 get_edit_bone(thigh_name + side)
		leg = get_edit_bone(leg_name + side)
		
		if prepole and thigh and leg:
			# center the prepole in the middle of the chain	   
			prepole.head[0] = (thigh.head[0] + leg.tail[0])/2
			prepole.head[1] = (thigh.head[1] + leg.tail[1])/2
			prepole.head[2] = (thigh.head[2] + leg.tail[2])/2
			# point toward the knee
			prepole.tail[0] = thigh.tail[0]
			prepole.tail[1] = thigh.tail[1]
			prepole.tail[2] = thigh.tail[2]			
			
			
			#align FK pole	   
			fk_pole = get_edit_bone(fk_pole_name + side)
				#get legs plane normal
			plane_normal = (thigh.head - leg.tail)		
				#pole position		
			prepole_dir = prepole.tail - prepole.head		
			pole_pos = prepole.tail + (prepole_dir).normalized()
			
				#ortho project onto plane to align with the knee/elbow	
			pole_pos = project_point_onto_plane(pole_pos, prepole.tail, plane_normal)
			
				#make sure to keep a correct distance from the knee
			pole_pos =	thigh.tail + (pole_pos-thigh.tail).normalized() * (thigh.tail-thigh.head).magnitude
							
			
			fk_pole.head = pole_pos
			fk_pole.tail = Vector((pole_pos)) + prepole_dir 
		
			#align IK pole				
			ik_pole = get_edit_bone(ik_pole_name + side)		   
			ik_pole.head = fk_pole.head
			ik_pole.tail = [ik_pole.head[0], ik_pole.head[1], ik_pole.head[2]+(0.1*thigh.length*2)]	   
			  
		
	for side in sides:
	
		if get_edit_bone(leg_name + side):
			# thigh and leg roll adjust
			init_selection(leg_name+side)		 
			bpy.ops.armature.calculate_roll(type='POS_Z')
			init_selection("null")	
			thigh = get_edit_bone(thigh_name + side)
			thigh.select = True	  
			bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[leg_name+side].bone	
			bpy.ops.armature.calculate_roll(type='ACTIVE')
			if side[-2:] == ".r":
				get_edit_bone(leg_name+side).roll += math.radians(-180)
				get_edit_bone(thigh_name+side).roll += math.radians(-180)
				  
		
	init_selection("null")	   
	 
	for side in sides:
		#copy the roll to other bones		   
		leg =  get_edit_bone(leg_name + side)
		thigh =	 get_edit_bone(thigh_name + side)
		
		if leg and thigh:
			for bone in legs:	 
				get_edit_bone(bone+side).roll = leg.roll						  
			
			for bone in thighs:
				if get_edit_bone(bone+side):
					get_edit_bone(bone+side).roll = thigh.roll				
			
		
			# foot poles			   
			foot_pole = get_edit_bone(foot_pole_name + side)	 
			coef = 1
			if side[-2:] == ".r":
				coef = -1
			foot_pole.head = leg.tail + (leg.x_axis * 0.24)*coef * leg.length + leg.y_axis * 0.03 * leg.length
			foot_pole.tail = foot_pole.head + (leg.y_axis * 0.05 * leg.length * 2)
			
			foot_pole.roll = leg.roll
			
	  
	
	# align feet
	feet = ["foot", "foot_fk", "c_foot_fk", "foot_ik", "c_foot_ik", "foot_snap_fk", "foot_ik_target", "c_foot_bank_01", "c_foot_bank_02", "c_foot_heel", "c_foot_01", "c_foot_fk_scale_fix"]
	foot_name = "foot_ref"
	
	for side in sides:
		for foot in feet:
			if get_edit_bone(foot + side):
				if foot == "foot_fk" or foot == "foot_ik" or foot == "foot":			   
					current_foot = get_edit_bone(foot+side)
					foot_ref = get_edit_bone(foot_name + side)
					current_foot.head = foot_ref.head
					current_foot.tail = foot_ref.tail
					current_foot.roll = foot_ref.roll
				
				if foot == "c_foot_fk" or foot == "c_foot_ik" or foot == "foot_snap_fk" or foot == "c_foot_fk_scale_fix":			   
					current_foot = bpy.context.active_object.data.edit_bones[foot+side]
					heel_ref = get_edit_bone('foot_heel_ref'+side)
					toes_ref = get_edit_bone(toes_name + side)	 
					foot_ref = get_edit_bone(foot_name + side)
					current_foot.head = foot_ref.head
					#current_foot.tail = foot_ref.head + (toes_ref.tail-toes_ref.head)
					current_foot.tail = foot_ref.head + (heel_ref.y_axis)*(heel_ref.head-toes_ref.tail).length/3#foot_ref.length/2
					#current_foot.tail[1] += -0.04
					#current_foot.roll = math.radians(180)
					current_foot.roll = heel_ref.roll# + math.radians(180)
					mirror_roll(foot+side, side)
				
				if foot == "foot_ik_target":			
					current_foot = bpy.context.active_object.data.edit_bones[foot+side]
					foot_ref = bpy.context.active_object.data.edit_bones[foot_name + side]			   
					current_foot.head = foot_ref.head
					current_foot.tail = current_foot.head - (foot_ref.y_axis*0.05*foot_ref.length*6)
					current_foot.roll = 0
			  
				if "bank" in foot or "foot_heel" in foot:			
					current_foot = bpy.context.active_object.data.edit_bones[foot+side]
					foot_ref = bpy.context.active_object.data.edit_bones[foot[2:]+"_ref"+side]
					current_foot.head = foot_ref.head
					current_foot.tail = foot_ref.tail
					current_foot.roll = foot_ref.roll
			  
				if foot == "c_foot_01":				  
					current_foot = get_edit_bone(foot+side)
					foot_ref = get_edit_bone(foot_name + side)
					current_foot.head = foot_ref.tail
					current_foot.tail = current_foot.head + (foot_ref.tail - foot_ref.head)/2
					current_foot.roll = foot_ref.roll
					#mirror_roll(foot+side, side)
					 
		if "foot" in locals():
			del foot	
		
		#align foot_01_pole		 
		current_foot = get_edit_bone("foot_01_pole"+side)
		c_foot_01 = get_edit_bone("c_foot_01"+side)
		
		if current_bone and c_foot_01:
			current_foot.head = c_foot_01.head + (c_foot_01.z_axis * 0.05 * c_foot_01.length * 40)
			current_foot.tail = current_foot.head + (c_foot_01.z_axis * 0.05 * c_foot_01.length * 40)
			current_foot.roll = math.radians(180)
			mirror_roll("foot_01_pole"+side, side)
	   
		#align foot visual position
		foot_ref = get_edit_bone(foot_name + side)
		heel_ref = get_edit_bone("foot_heel_ref" + side)
		p_foots = ["c_p_foot_ik", "c_p_foot_fk"]
		
		for p_f in p_foots:
			try:
				p_foot = get_edit_bone(p_f + side)			 
				p_foot.head = heel_ref.head
				
				p_foot.tail = heel_ref.tail
				p_foot.roll = get_edit_bone('foot_heel_ref'+side).roll + math.radians(-90)
				if side [-2:] == '.r':
					p_foot.roll += math.radians(180)				
				
			except:
				pass
		
		if "p_f" in locals():
			del p_f
		
		
	# Align toes
	toes = ["c_toes_fk", "c_toes_ik", "toes_01_ik", "c_toes_track", "toes_02", "c_toes_end", "c_toes_end_01", "toes_01"]
	
	
	for side in sides:	   
		#normalize toes axes   
		toes_ref = get_edit_bone(toes_name + side)
		foot_ref = get_edit_bone(foot_name + side)	
		
		if toes_ref and foot_ref:
			for bone in toes:
				
				if bone == "c_toes_end":		
					current_bone = get_edit_bone(bone + side)			
					current_bone.head = toes_ref.tail
					current_bone.tail = current_bone.head + (toes_ref.tail - toes_ref.head)/2
				
					bpy.ops.armature.select_all(action='DESELECT')
					bpy.context.active_object.data.edit_bones.active = current_bone	 
					bpy.context.active_object.data.edit_bones.active = toes_ref			
					bpy.ops.armature.calculate_roll(type='ACTIVE')
					current_bone.roll += math.radians(180)
				
				
					
				if bone == "c_toes_end_01":				 
					current_bone = get_edit_bone(bone+side) 
					current_bone.head = toes_ref.tail
					current_bone.tail = current_bone.head + (toes_ref.z_axis * 0.035 * toes_ref.length * 6)
					current_bone.roll = math.radians(180)
					mirror_roll(bone+side, side)
				
				if bone == "c_toes_fk" or bone == "c_toes_track" or bone == "c_toes_ik":	 
					current_bone = get_edit_bone(bone+side)							 
					current_bone.head = toes_ref.head
					current_bone.tail = toes_ref.tail
					current_bone.roll = toes_ref.roll + math.radians(180)
					if bone == 'c_toes_track':
						current_bone.roll += math.radians(-90)
			
			if "bone" in locals():
				del bone

			
	for side in sides:	  
		for bone in toes:
		
			if bone == "toes_01_ik" or bone == "toes_01":
				if get_edit_bone(bone + side):
					init_selection(bone+side)
					toes_ref = get_edit_bone(toes_name + side)		
					current_bone = get_edit_bone(bone+side)
					c_toes_fk = bpy.context.active_object.data.edit_bones["c_toes_fk"+side]
					current_bone.head = toes_ref.head
					dir = c_toes_fk.tail - c_toes_fk.head
					current_bone.tail = current_bone.head + dir/3
					bpy.ops.armature.select_all(action='DESELECT')
					bpy.context.active_object.data.edit_bones.active = current_bone	 
					bpy.context.active_object.data.edit_bones.active = toes_ref			
					bpy.ops.armature.calculate_roll(type='ACTIVE')
					current_bone.roll += math.radians(180)
				
			#toes_01 must deform if no individuals toes are found
			if bone == "toes_01":
				toes_01_bone = get_edit_bone("toes_01"+side)
				if toes_01_bone:
					if len(toes_01_bone.children) == 0:
						toes_01_bone.use_deform = True
				
			if bone == "toes_02":
				if get_edit_bone(bone + side):
					init_selection(bone+side)
					toes_ref = get_edit_bone(toes_name + side)		
					toes_01_ik = get_edit_bone("toes_01_ik" + side)
					current_bone = get_edit_bone(bone+side)
					c_toes_fk = get_edit_bone("c_toes_fk"+side)
					current_bone.head = toes_01_ik.tail			   
					current_bone.tail = c_toes_fk.tail
					#current_bone.roll = toes_ref.roll
					bpy.ops.armature.select_all(action='DESELECT')
					bpy.context.active_object.data.edit_bones.active = current_bone	 
					bpy.context.active_object.data.edit_bones.active = toes_ref			
					bpy.ops.armature.calculate_roll(type='ACTIVE')
					
					current_bone.roll = toes_ref.roll + math.radians(180)
					#bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')

		if "bone" in locals():
			del bone

		
	# toes fingers
	obj = bpy.context.active_object 
	toes_list=["toes_pinky", "toes_ring", "toes_middle", "toes_index", "toes_thumb"]
	fingers_shape_type = bpy.context.active_object.arp_fingers_shape_style

	for side in sides:
		for t in range (0,5): 
		
			max = 4
			if t == 4:
				max = 3#thumb case
			for i in range (1,max):			   
				ref_bone = toes_list[t]+str(i)+"_ref" +side		  
				c_bone = "c_"+toes_list[t]+str(i)+side 
				
				if get_edit_bone(ref_bone) and get_edit_bone(c_bone):
					if get_edit_bone(c_bone).use_deform:
						copy_bone_transforms(get_edit_bone(ref_bone), get_edit_bone(c_bone))
						
						# Set shape
						# if not a user defined custom shape		
						if get_pose_bone(c_bone).custom_shape:
							if not "cs_user" in get_pose_bone(c_bone).custom_shape.name:
								bpy.ops.object.mode_set(mode='POSE')
								
								if fingers_shape_type == "box":			
									cs_obj = bpy.data.objects["cs_box"]
								if fingers_shape_type == "circle":								
									cs_obj = bpy.data.objects["cs_torus_04"]
									
								get_pose_bone(c_bone).custom_shape = cs_obj
								
								bpy.ops.object.mode_set(mode='EDIT')
	
		
	#foot roll
	
	for side in sides:		 
		toes_ref = get_edit_bone(toes_name+side)
		heel_ref = get_edit_bone('foot_heel_ref'+side)
		
		if toes_ref and heel_ref:
			c_foot_roll = get_edit_bone("c_foot_roll"+side)
			c_foot_roll.head = heel_ref.head - heel_ref.y_axis*(toes_ref.head-toes_ref.tail).length*2		
			c_foot_roll.tail = c_foot_roll.head - heel_ref.y_axis*(toes_ref.head-toes_ref.tail).length*0.6	
			bpy.ops.armature.select_all(action='DESELECT')
			bpy.context.active_object.data.edit_bones.active = c_foot_roll	 
			bpy.context.active_object.data.edit_bones.active = toes_ref			
			bpy.ops.armature.calculate_roll(type='ACTIVE')
			c_foot_roll.roll += math.radians(-90+180)
	
			#cursor bank roll		
			c_foot_roll_cursor = get_edit_bone("c_foot_roll_cursor"+side)
			c_foot_roll_cursor.head = c_foot_roll.tail - (c_foot_roll.x_axis*c_foot_roll.length)
			
			
			c_foot_roll_cursor.tail = c_foot_roll_cursor.head - (c_foot_roll.tail - c_foot_roll.head)	
			bpy.ops.armature.select_all(action='DESELECT')
			bpy.context.active_object.data.edit_bones.active = c_foot_roll_cursor	
			bpy.context.active_object.data.edit_bones.active = toes_ref			
			bpy.ops.armature.calculate_roll(type='ACTIVE')
			c_foot_roll_cursor.roll += math.radians(-90+180)
			
			
			if side[-2:] == '.r':
				c_foot_roll_cursor.roll += math.radians(180)
		
			# align c_thigh_b	   
			c_thigh_b = bpy.context.active_object.data.edit_bones["c_thigh_b"+side]
			thigh_fk = bpy.context.active_object.data.edit_bones["thigh_fk"+side]
			dir = thigh_fk.tail - thigh_fk.head
			c_thigh_b.head = thigh_fk.head - dir/7
			c_thigh_b.tail = thigh_fk.head
			c_thigh_b.roll = thigh_fk.roll	
			
			#leg parent
			thigh_ref = get_edit_bone(thigh_name+side)
			if thigh_ref.parent:		
				if thigh_ref.parent.name[:-2][-4:] == "_ref":
					c_thigh_b.parent = get_edit_bone('c_' + thigh_ref.parent.name.replace('_ref.x', '.x'))
				else:
					c_thigh_b.parent = thigh_ref.parent
			else:
				c_thigh_b.parent = get_edit_bone('c_traj')
			
		

	
	#POSE MODE ONLY
	# reset stretchy bone length
	bpy.ops.object.mode_set(mode='OBJECT')	 
	bpy.ops.object.mode_set(mode='POSE')	 

	leg_add_bones = ["c_thigh_bend_contact", "c_thigh_bend_01", "c_thigh_bend_02", "c_knee_bend", "c_leg_bend_01", "c_leg_bend_02", "c_ankle_bend"]

	
	
	for side in sides:
		# Leg IK Stretch		
		thigh_ik_p = get_pose_bone("thigh_ik"+side)
		leg_ik_p = get_pose_bone("leg_ik"+side)
		
		if thigh_ik_p and leg_ik_p:
			thigh_ik_length = thigh_ik_p.length
			leg_ik_length = leg_ik_p.length
			
			if thigh_ik_length < leg_ik_length:
				thigh_ik_p.ik_stretch = (thigh_ik_length ** (1 / 3)) / (leg_ik_length ** (1 / 3))
				leg_ik_p.ik_stretch = 1.0
			else:
				thigh_ik_p.ik_stretch = 1.0
				leg_ik_p.ik_stretch = (leg_ik_length ** (1 / 3)) / (thigh_ik_length ** (1 / 3))
				
		
			
		
		# Set the secondary bones deformation mode: Additive (default) or Bendy bones
				
		drivers_list = bpy.context.active_object.animation_data.drivers
		
		# Bendy bones
		if get_pose_bone("thigh_stretch" + side):
			if bpy.context.object.arp_secondary_type == "bendy_bones":
				
				# change parents
				bpy.ops.object.mode_set(mode='EDIT')
				c_thigh_bend_01 = get_edit_bone("c_thigh_bend_01" + side)
				if c_thigh_bend_01:
					c_thigh_bend_01.parent = get_edit_bone("thigh_stretch" + side)

				# get bones lengths
				if get_edit_bone("thigh_stretch" + side):
					thigh_length = get_edit_bone("thigh_stretch" + side).length
					leg_length = get_edit_bone("leg_stretch" + side).length
				
				bpy.ops.object.mode_set(mode='POSE')
			
				# constraints			
				get_pose_bone("thigh_stretch" + side).constraints["Copy Location"].head_tail = 0.0
				
				# disable twist deform and rig_add bend bones deform			
				get_pose_bone("thigh_twist" + side).bone.use_deform = False
				get_pose_bone("leg_twist" + side).bone.use_deform = False
				_rig_add = get_rig_add(bpy.context.active_object)
				
				for add_bone in leg_add_bones:
					_rig_add.pose.bones[add_bone + side].bone.use_deform = False
					
				# hide the non-used controllers
				get_pose_bone("c_knee_bend" + side).bone.hide = True
				get_pose_bone("c_ankle_bend" + side).bone.hide = True
				get_pose_bone("c_thigh_bend_contact" + side).bone.hide = True
				
				if get_pose_bone("c_knee_bend" + "_proxy"+ side):
					get_pose_bone("c_knee_bend" + "_proxy"+ side).bone.hide = True
				if get_pose_bone("c_ankle_bend" + "_proxy"+ side):
					get_pose_bone("c_ankle_bend" + "_proxy"+ side).bone.hide = True
				if get_pose_bone("c_thigh_bend_contact" + "_proxy"+ side):
					get_pose_bone("c_thigh_bend_contact" + "_proxy"+ side).bone.hide = True
								
			
				# custom handles
				get_pose_bone("thigh_stretch" + side).bone.bbone_handle_type_start = "ABSOLUTE"
				get_pose_bone("thigh_stretch" + side).bone.bbone_handle_type_end = "ABSOLUTE"
				get_pose_bone("leg_stretch" + side).bone.bbone_handle_type_start = "ABSOLUTE"
				get_pose_bone("leg_stretch" + side).bone.bbone_handle_type_end = "ABSOLUTE"
				
				get_pose_bone("thigh_stretch" + side).bone.bbone_custom_handle_start = get_pose_bone("c_thigh_b" + side).bone
				get_pose_bone("thigh_stretch" + side).bone.bbone_custom_handle_end = get_pose_bone("leg_stretch" + side).bone
				
				get_pose_bone("leg_stretch" + side).bone.bbone_custom_handle_start = get_pose_bone("thigh_stretch" + side).bone
				get_pose_bone("leg_stretch" + side).bone.bbone_custom_handle_end = get_pose_bone("foot_pole" + side).bone
				
				# Set the drivers			
							
				# driver creation function
				def configure_driver_bbone(driv = None, bone = None, b_side = None, loc = None, type = None, fac = None):	
										
					_expression = "var"
					if fac:
						_expression += "*" + str(fac)
						
					driv.driver.expression = _expression						
					
					# create a new var if necessary
					if len(driv.driver.variables) == 0:
						base_var = driv.driver.variables.new()
					else:
						base_var = driv.driver.variables[0]				
					
					base_var.type = 'SINGLE_PROP'
					base_var.name = 'var'
					base_var.targets[0].id = bpy.context.active_object
					
					if type == "location":
						base_var.targets[0].data_path = 'pose.bones["' + bone + side + '"].location[' + str(loc) + ']'
					if type == "scale":
						base_var.targets[0].data_path = 'pose.bones["' + bone + side + '"].scale[0]'
					if type == "rotation":
						base_var.targets[0].data_path = 'pose.bones["' + bone + side + '"].rotation_euler[1]'
											
				

					# Thigh bones (not leg)
				driver_in_x = None
				driver_out_x = None
				driver_in_y = None
				driver_out_y = None
				driver_scale_in = None
				driver_scale_out = None
				driver_rot_in = None
				driver_rot_out = None
				driver_ease_in = None
				driver_ease_out = None
				
				# are the drivers already created?
				for dri in drivers_list:	
					if '"thigh_stretch' + side in dri.data_path:
						if "bbone_curveinx" in dri.data_path: 
							driver_in_x = dri.data_path
						if "bbone_curveiny" in dri.data_path:
							driver_in_y = dri.data_path
						if "bbone_curveoutx" in dri.data_path:
							driver_out_x = dri.data_path
						if "bbone_curveouty" in dri.data_path:
							driver_out_y = dri.data_path
						if "bbone_scalein" in dri.data_path:
							driver_scale_in = dri.data_path
						if "bbone_scaleout" in dri.data_path:
							driver_scale_out = dri.data_path
						if "bbone_rotin" in dri.data_path:
							driver_rot_in = dri.data_path
						if "bbone_rotout" in dri.data_path:
							driver_rot_out = dri.data_path
						if "bbone_easein" in dri.data_path:
							driver_ease_in = dri.data_path
						if "bbone_easeout" in dri.data_path:
							driver_ease_out = dri.data_path
				
				fac_offset = "2.2"
				fac_ease = "8/"
				
				# Driver In X				
				if driver_in_x:				
					dr_inx = drivers_list.find(driver_in_x)
				else:
					dr_inx = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_curveinx', -1)		
					
				configure_driver_bbone(driv = dr_inx, bone = "c_thigh_bend_01", b_side = side, loc = 0, type = "location", fac=fac_offset)#+str(thigh_length))		
							
				# Driver In Y				
				if driver_in_y:			
					dr_iny = drivers_list.find(driver_in_y)
				else:
					dr_iny = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_curveiny', -1)		
					
				configure_driver_bbone(driv = dr_iny, bone = "c_thigh_bend_01", b_side = side, loc = 2, type = "location", fac=fac_offset)#+str(thigh_length))		
										
				# Driver Out X				
				if driver_out_x:						
					dr_outx = drivers_list.find(driver_out_x)
				else:
					dr_outx = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_curveoutx', -1)		
					
				configure_driver_bbone(driv = dr_outx, bone = "c_thigh_bend_02", b_side = side, loc = 0, type = "location", fac=fac_offset)#+str(thigh_length))		
										
				# Driver Out Y				
				if driver_out_y:					
					dr_outy = drivers_list.find(driver_out_y)
				else:
					dr_outy = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_curveouty', -1)		
				
				configure_driver_bbone(driv = dr_outy, bone = "c_thigh_bend_02", b_side = side, loc = 2, type = "location", fac=fac_offset)#+str(thigh_length)) 
				
				# Driver Scale In
				if driver_scale_in:					
					dr_scalein = drivers_list.find(driver_scale_in)
				else:
					dr_scalein = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_scalein', -1)

				configure_driver_bbone(driv = dr_scalein, bone = "c_thigh_bend_01", b_side = side, type = "scale")
				
				# Driver Scale Out
				if driver_scale_out:					
					dr_scaleout = drivers_list.find(driver_scale_out)
				else:
					dr_scaleout = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_scaleout', -1)

				configure_driver_bbone(driv = dr_scaleout, bone = "c_thigh_bend_02", b_side = side, type = "scale")
				
				# Driver Rot In
				if driver_rot_in:					
					dr_rotin = drivers_list.find(driver_rot_in)
				else:
					dr_rotin = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_rollin', -1)

				configure_driver_bbone(driv = dr_rotin, bone = "c_thigh_bend_01", b_side = side, type = "rotation")
				
				# Driver Rot Out
				if driver_rot_out:					
					dr_rotout = drivers_list.find(driver_rot_out)
				else:
					dr_rotout = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_rollout', -1)

				configure_driver_bbone(driv = dr_rotout, bone = "c_thigh_bend_02", b_side = side, type = "rotation")
				
				# Driver Ease In
				if driver_ease_in:					
					dr_easin = drivers_list.find(driver_ease_in)
				else:
					dr_easin = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_easein', -1)

				configure_driver_bbone(driv = dr_easin, bone = "c_thigh_bend_01", b_side = side, loc = 1, type = "location", fac=fac_ease+str(thigh_length))
				
				# Driver Ease Out
				if driver_ease_out:					
					dr_easout = drivers_list.find(driver_ease_out)
				else:
					dr_easout = bpy.context.active_object.driver_add('pose.bones["' + "thigh_stretch" + side + '"].bbone_easeout', -1)

				configure_driver_bbone(driv = dr_easout, bone = "c_thigh_bend_02", b_side = side, loc = 1, type = "location", fac='-'+fac_ease+str(thigh_length))
				
				
					# Leg bones
				driver_in_x = None
				driver_out_x = None
				driver_in_y = None
				driver_out_y = None
				driver_scale_in = None
				driver_scale_out = None
				driver_rot_in = None
				driver_rot_out = None
				driver_ease_in = None
				driver_ease_out = None
				
				for dri in drivers_list:	
					if '"leg_stretch' + side in dri.data_path:
						if "bbone_curveinx" in dri.data_path: 
							driver_in_x = dri.data_path
						if "bbone_curveiny" in dri.data_path:
							driver_in_y = dri.data_path
						if "bbone_curveoutx" in dri.data_path:
							driver_out_x = dri.data_path
						if "bbone_curveouty" in dri.data_path:
							driver_out_y = dri.data_path
						if "bbone_scalein" in dri.data_path:
							driver_scale_in = dri.data_path
						if "bbone_scaleout" in dri.data_path:
							driver_scale_out = dri.data_path
						if "bbone_rotin" in dri.data_path:
							driver_rot_in = dri.data_path
						if "bbone_rotout" in dri.data_path:
							driver_rot_out = dri.data_path
						if "bbone_easein" in dri.data_path:
							driver_ease_in = dri.data_path
						if "bbone_easeout" in dri.data_path:
							driver_ease_out = dri.data_path
				
								
				# Driver In X				
				if driver_in_x:				
					dr_inx = drivers_list.find(driver_in_x)
				else:
					dr_inx = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_curveinx', -1)		
					
				configure_driver_bbone(driv = dr_inx, bone = "c_leg_bend_01", b_side = side, loc = 0, type = "location", fac=fac_offset)#+str(leg_length))		
							
				# Driver In Y				
				if driver_in_y:			
					dr_iny = drivers_list.find(driver_in_y)
				else:
					dr_iny = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_curveiny', -1)		
					
				configure_driver_bbone(driv = dr_iny, bone = "c_leg_bend_01", b_side = side, loc = 2, type = "location", fac=fac_offset)#+str(leg_length))	
										
				# Driver Out X				
				if driver_out_x:						
					dr_outx = drivers_list.find(driver_out_x)
				else:
					dr_outx = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_curveoutx', -1)		
					
				configure_driver_bbone(driv = dr_outx, bone = "c_leg_bend_02", b_side = side, loc = 0, type = "location", fac=fac_offset)#+str(leg_length))			
										
				# Driver Out Y				
				if driver_out_y:					
					dr_outy = drivers_list.find(driver_out_y)
				else:
					dr_outy = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_curveouty', -1)		
				
				configure_driver_bbone(driv = dr_outy, bone = "c_leg_bend_02", b_side = side, loc = 2, type = "location", fac=fac_offset)#+str(leg_length))		

				# Driver Scale In
				if driver_scale_in:					
					dr_scalein = drivers_list.find(driver_scale_in)
				else:
					dr_scalein = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_scalein', -1)

				configure_driver_bbone(driv = dr_scalein, bone = "c_leg_bend_01", b_side = side, type = "scale")
				
				# Driver Scale Out
				if driver_scale_out:					
					dr_scaleout = drivers_list.find(driver_scale_out)
				else:
					dr_scaleout = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_scaleout', -1)

				configure_driver_bbone(driv = dr_scaleout, bone = "c_leg_bend_02", b_side = side, type = "scale")
				
				# Driver Rot In
				if driver_rot_in:					
					dr_rotin = drivers_list.find(driver_rot_in)
				else:
					dr_rotin = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_rollin', -1)

				configure_driver_bbone(driv = dr_rotin, bone = "c_leg_bend_01", b_side = side, type = "rotation")
				
				# Driver Rot Out
				if driver_rot_out:					
					dr_rotout = drivers_list.find(driver_rot_out)
				else:
					dr_rotout = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_rollout', -1)

				configure_driver_bbone(driv = dr_rotout, bone = "c_leg_bend_02", b_side = side, type = "rotation")
				
				# Driver Ease In
				if driver_ease_in:					
					dr_easin = drivers_list.find(driver_ease_in)
				else:
					dr_easin = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_easein', -1)

				configure_driver_bbone(driv = dr_easin, bone = "c_leg_bend_01", b_side = side, loc = 1, type = "location", fac=fac_ease+str(leg_length))
				
				# Driver Ease Out
				if driver_ease_out:					
					dr_easout = drivers_list.find(driver_ease_out)
				else:
					dr_easout = bpy.context.active_object.driver_add('pose.bones["' + "leg_stretch" + side + '"].bbone_easeout', -1)

				configure_driver_bbone(driv = dr_easout, bone = "c_leg_bend_02", b_side = side, loc = 1, type = "location", fac='-'+fac_ease+str(leg_length))
				
			
			# else, additive mode
			if bpy.context.object.arp_secondary_type == "additive":
															
				# change parents
				bpy.ops.object.mode_set(mode='EDIT')
				get_edit_bone("c_thigh_bend_01" + side).parent = get_edit_bone("thigh_twist" + side)			
				bpy.ops.object.mode_set(mode='POSE')
			
				# custom handles
				get_pose_bone("thigh_stretch" + side).bone.bbone_handle_type_start = 'AUTO'
				get_pose_bone("thigh_stretch" + side).bone.bbone_handle_type_end = 'AUTO'
				get_pose_bone("leg_stretch" + side).bone.bbone_handle_type_start = 'AUTO'
				get_pose_bone("leg_stretch" + side).bone.bbone_handle_type_end = 'AUTO'
				
				# constraints
				get_pose_bone("thigh_stretch" + side).constraints["Copy Location"].head_tail = 1.0
				
				# display the used controllers
				get_pose_bone("c_knee_bend" + side).bone.hide = False
				get_pose_bone("c_ankle_bend" + side).bone.hide = False
				get_pose_bone("c_thigh_bend_contact" + side).bone.hide = False
				
				if get_pose_bone("c_knee_bend" + "_proxy"+ side):
					get_pose_bone("c_knee_bend" + "_proxy"+ side).bone.hide = False
				if get_pose_bone("c_ankle_bend" + "_proxy"+ side):
					get_pose_bone("c_ankle_bend" + "_proxy"+ side).bone.hide = False
				if get_pose_bone("c_thigh_bend_contact" + "_proxy"+ side):
					get_pose_bone("c_thigh_bend_contact" + "_proxy"+ side).bone.hide = False
				
				# enable twist deform and rig_add bend bones
				thigh_ik = get_pose_bone("c_thigh_ik" + side)
				if thigh_ik:
					if thigh_ik.bone.layers[22] == False:#if not disabled					
						thigh_twist = get_pose_bone("thigh_twist" + side)
						if thigh_twist:
							thigh_twist.bone.use_deform = True
						else:
							print("thigh_twist" + side + " not found")
							
						leg_twist = get_pose_bone("leg_twist" + side)
						if leg_twist:
							leg_twist.bone.use_deform = True	
						else:
							print("leg_twist" + side + " not found")
							
						_rig_add = get_rig_add(bpy.context.active_object)
						if _rig_add:
							for add_bname in leg_add_bones:
								add_bone = _rig_add.pose.bones.get(add_bname + side)
								if add_bone:
									add_bone.bone.use_deform = True
						else:
							print("Rig add not found")
							
				else:
					print("c_thigh_ik" + side + " not found")
				
				
					
						
				
							
	# end for side in sides		
		
				 
	bpy.context.active_object.data.pose_position = 'POSE'

	
	if bpy.context.scene.arp_debug_mode == True:	   
		print("\n FINISH ALIGNING LEG BONES...\n")
	
	#--END ALIGN LEGS BONES
	
def _set_inverse():

	#store the current pose
	bpy.ops.pose.select_all(action='SELECT')
	bpy.ops.pose.copy()
	#reset the pose and child of constraints
	auto_rig_reset.reset_all()
	#restore the pose
	bpy.ops.pose.paste(flipped=False)
	


def _align_spine_bones():
	
	
	print("\n Aligning spine bones...\n")
	 
	# Unit scale
	unit_scale = 1.0
	
	if bpy.context.scene.unit_settings.system != 'NONE':
		unit_scale = 1/bpy.context.scene.unit_settings.scale_length
	
	
	rig = bpy.context.active_object
	rig_add = get_rig_add(rig)
	 
	# Get reference bones
	root_name = "root_ref.x"
	spine_01_name = "spine_01_ref.x"
	spine_02_name = "spine_02_ref.x"  
	bot_bend_name = "bot_bend_ref"
	
	bpy.ops.object.mode_set(mode='EDIT')		
		
		
	# Align root master
	if get_edit_bone("c_root_master.x"):
		init_selection("c_root_master.x")
		c_root_master = get_edit_bone("c_root_master.x")
		c_root_ref = get_edit_bone(root_name)
		p_root_master = get_edit_bone("c_p_root_master.x")
		
	
		copy_bone_transforms(c_root_ref, c_root_master)
		#get_pose_bone("c_root_master.x").custom_shape_scale = (0.1 / c_root_master.length)#*unit_scale
		
			# set the visual shape position
		dir = c_root_ref.tail - c_root_ref.head
		p_root_master.head = c_root_master.head# + (c_root_master.tail-c_root_master.head)/2	 
		p_root_master.tail = p_root_master.head + dir/1.5
			# set the bone vertical if not quadruped
		if not bpy.context.active_object.rig_type == 'quadruped' and not p_root_master.head[2] == p_root_master.tail[2]:
			p_root_master.tail[1] = p_root_master.head[1]

		
		# Align root
		init_selection("c_root.x")
		c_root = get_edit_bone("c_root.x")
		root = get_edit_bone("root.x")
		c_root_ref = get_edit_bone(root_name)
		p_root = get_edit_bone("c_p_root.x")
		
		c_root.head = c_root_ref.tail
		c_root.tail = c_root_ref.head
		c_root.roll = c_root_ref.roll
		#get_pose_bone("c_root.x").custom_shape_scale = (0.1 / c_root.length)#*unit_scale
		copy_bone_transforms(c_root, root)
		
			# set the visual shape position
		dir = c_root_ref.tail - c_root_ref.head 
		p_root.head = c_root_ref.head + (c_root_ref.tail-c_root_ref.head)/2	 
		p_root.tail = p_root.head + dir
		
		p_root.roll = 0
		# set the bone vertical if not quadruped
		if not bpy.context.active_object.rig_type == 'quadruped' and not p_root.head[2] == p_root.tail[2]:
			p_root.tail[1] = p_root.head[1]
		
			#root bend
		root_bend = get_edit_bone("c_root_bend.x")
		dir = root_bend.tail - root_bend.head	 
		root_bend.head = c_root.head +(c_root.tail - c_root.head)/2
		root_bend.tail = root_bend.head + dir
		root_bend.roll = 0
	
	 #align bot_bend	
	for side in ['.l', '.r']:
		bot_ref = get_edit_bone(bot_bend_name+side)
		c_bot_bend = get_edit_bone("c_bot_bend"+side)
		
		if bot_ref:
			dir = bot_ref.tail - bot_ref.head
			c_bot_bend.head = bot_ref.head	 
			c_bot_bend.tail = bot_ref.tail - dir/2	
	
	# align tail if any
	if bpy.context.active_object.data.bones.get("c_tail_00.x"):
		# main tail bones
		last_existing_tail = None
		
		for i in range(0, bpy.context.active_object.rig_tail_count):		
			bone_name = 'tail_' + '%02d' % i
			c_bone = get_edit_bone("c_" + bone_name + ".x")
			ref_bone = get_edit_bone(bone_name + "_ref.x")
			
			if c_bone and ref_bone:
				copy_bone_transforms(ref_bone, c_bone)
				last_existing_tail = ref_bone.tail
				# parent
				if 'tail_00' in bone_name:
					b_parent = None
					
					if ref_bone.parent:
						b_parent = get_edit_bone('c_' + ref_bone.parent.name.replace('_ref.x', '.x'))
					
					traj_parent = get_edit_bone("c_traj")
					
					if b_parent:
						c_bone.parent = b_parent					
					elif traj_parent:
						c_bone.parent = traj_parent				
						
			else:
				print("Ref or control tail bone not found:", bone_name)
		
		if "i" in locals():
			del i
		
		# master tail bone
		c_tail_master = get_edit_bone('c_tail_master.x')
		
		if c_tail_master:
		
			tail_00_ref = get_edit_bone("tail_00_ref.x")		
			tail_vec = tail_00_ref.tail - tail_00_ref.head			
			if last_existing_tail:		
				tail_vec = last_existing_tail - tail_00_ref.head
				
			tail_origin = tail_00_ref.head
			tail_parent = tail_00_ref.parent		
		
			c_tail_master.head = tail_origin +	(tail_vec * 0.5)
			c_tail_master.tail = c_tail_master.head + (tail_vec*0.5)
			c_tail_master.roll = get_edit_bone("tail_00_ref.x").roll
			c_tail_master.parent = tail_parent
			c_tail_master.use_deform = False
		
		
	# Align spine 01
	if get_edit_bone("c_spine_01.x"):
		init_selection("c_spine_01.x")
		c_spine_01 = get_edit_bone("c_spine_01.x")
		spine_01 = get_edit_bone("spine_01.x")
		spine_01_ref = get_edit_bone(spine_01_name)
		p_spine_01 = get_edit_bone("c_p_spine_01.x")
		
		copy_bone_transforms(spine_01_ref, c_spine_01)
		copy_bone_transforms(c_spine_01, spine_01) 
		
			# set the visual shape position
		if p_spine_01:
			p_spine_01.head = c_spine_01.head	
			p_spine_01.tail = p_spine_01.head + (c_spine_01.tail-c_spine_01.head)
			p_spine_01.roll = c_spine_01.roll
			# Set the bone vertical if not quadruped
			if not bpy.context.active_object.rig_type == 'quadruped' and not p_spine_01.head[2] == p_spine_01.tail[2]:
				p_spine_01.tail[1] = p_spine_01.head[1] 
	
	
		# Waist bend
	waist_bend = get_edit_bone("c_waist_bend.x")
	c_root_ref = get_edit_bone(root_name)
	if waist_bend and c_root_ref:
		waist_bend.head = c_root_ref.tail
		waist_bend.tail = c_root_ref.tail + (c_root_ref.tail - c_root_ref.head)*0.5
		waist_bend.roll = 0

		# Spine_01_bend
	spine_01_bend = get_edit_bone("c_spine_01_bend.x")
	if spine_01_bend:
		#spine_01_bend.head = p_spine_01.tail + (p_spine_01.head - p_spine_01.tail)*0.5
		#spine_01_bend.tail = spine_01_bend.head - (p_spine_01.tail - p_spine_01.head)/2
		spine_01_bend.head = ((c_spine_01.tail + c_spine_01.head) * 0.5)
		spine_01_bend.tail = c_spine_01.head		
		spine_01_bend.roll = 0

	
	 # Align spine 02
	if get_edit_bone("c_spine_02.x"):
		init_selection("c_spine_02.x")
		c_spine_02 = get_edit_bone("c_spine_02.x")
		spine_02 = get_edit_bone("spine_02.x")
		spine_02_ref = get_edit_bone(spine_02_name)
		p_spine_02 = get_edit_bone("c_p_spine_02.x")		
		
		copy_bone_transforms(spine_02_ref, c_spine_02) 
		copy_bone_transforms(c_spine_02, spine_02)	
		
		# set the visual shape position
		if p_spine_02:
			p_spine_02.head = c_spine_02.head
			p_spine_02.tail = p_spine_02.head + (c_spine_02.tail-c_spine_02.head)*0.5
			p_spine_02.roll = c_spine_02.roll
		
			# set the bone vertical if not quadruped
			if not bpy.context.active_object.rig_type == 'quadruped' and not p_spine_02.head[2] == p_spine_02.tail[2]:
				p_spine_02.tail[1] = p_spine_02.head[1]
			
		# Spine_02_bend
		spine_02_bend = get_edit_bone("c_spine_02_bend.x")
		"""
		spine_02_bend.head = p_spine_02.tail
		spine_02_bend.tail = p_spine_02.head
		spine_02_bend.roll = 0
		"""
		if spine_02_bend:
			spine_02_bend.head = ((c_spine_02.tail + c_spine_02.head) * 0.5)
			spine_02_bend.tail = c_spine_02.head		
			spine_02_bend.roll = 0
			
	
	# Align spine 03
	spine_03_ref = get_edit_bone('spine_03_ref.x')
	c_spine_03 = get_edit_bone('c_spine_03.x')
	if spine_03_ref and c_spine_03:
		copy_bone_transforms(spine_03_ref, c_spine_03) 
		copy_bone_transforms(spine_03_ref, c_spine_03)	
	
			# Spine_03_bend
		spine_03_bend = get_edit_bone("c_spine_03_bend.x")	
		if spine_03_bend:
			spine_03_bend.head = ((c_spine_03.tail + c_spine_03.head) * 0.5)
			spine_03_bend.tail = c_spine_03.head		
			spine_03_bend.roll = 0

	print("\n Aligning heads")
	for dupli in limb_sides.head_sides:		
		
		print('[' + dupli + ']')
		# Neck	
		if get_edit_bone("c_neck" + dupli):
			init_selection("c_neck" + dupli)
			c_neck = get_edit_bone("c_neck" + dupli)
			c_neck_01 = get_edit_bone("c_neck_01" + dupli)
			neck = get_edit_bone("neck" + dupli)		
			p_neck = get_edit_bone("c_p_neck" + dupli)
			p_neck_01 =get_edit_bone("c_p_neck_01" + dupli)
			neck_ref = get_edit_bone("neck_ref" + dupli)
			
			# Neck parent	
			if neck_ref.parent:
				print("Set neck parent...")
				parent_name = neck_ref.parent.name	
				split_name = parent_name.split('_')
				ref_found = False
				if len(split_name) >= 2: 
					if 'ref' in split_name[1]:
						ref_found = True
				if len(split_name) >= 3: 
					if 'ref' in split_name[2]:
						ref_found = True					
				if ref_found:					
					parent_bone = get_edit_bone('c_' + neck_ref.parent.name.replace('_ref', ''))
					#print("paraent should be", 'c_' + neck_ref.parent.name.replace('_ref', ''))
					if parent_bone:
						c_neck.parent = parent_bone
						print("... assigned to", parent_bone.name)
						if c_neck_01:
							c_neck_01.parent = parent_bone
					else:
						print("	 Could not find the neck bone parent: ", neck_ref.parent.name)
						c_neck.parent = get_edit_bone('c_traj')
						if c_neck_01:
							c_neck_01.parent = get_edit_bone('c_traj')
				else:
					c_neck.parent = neck_ref.parent
					
					if c_neck_01: 
						c_neck_01.parent = neck_ref.parent
						
			else:
				print("No neck ref parent")
				traj_parent = get_edit_bone('c_traj')
				if traj_parent:
					c_neck.parent = traj_parent
					print("...assigning to c_traj")
					if c_neck_01:
						c_neck_01.parent = traj_parent
			
			
			copy_bone_transforms(neck_ref, c_neck) 
			copy_bone_transforms(neck_ref, neck) 
			if c_neck_01:
				c_neck_01.head = neck_ref.head
				c_neck_01.tail = c_neck_01.head	   
				
				c_neck_01.tail[1] += -neck_ref.length/3
				c_neck_01.roll = 0
			
			# set the visual shape position
			copy_bone_transforms(neck_ref, p_neck) 
			p_neck.head += (neck_ref.tail - neck_ref.head)/2
			p_neck.tail = p_neck.head + (neck_ref.tail - neck_ref.head)
			
			p_neck_01.head = neck_ref.head
			p_neck_01.head[1] += -0.07
			p_neck_01.tail = p_neck_01.head
			p_neck_01.tail[1] += -0.03
	
		# Head
		if get_edit_bone("c_head" + dupli):
			init_selection("c_head" + dupli)
			c_head = get_edit_bone("c_head" + dupli)
			head_ref = get_edit_bone("head_ref" + dupli)
			head = get_edit_bone("head" + dupli)
			head_scale_fix = get_edit_bone("head_scale_fix" + dupli)
			c_p_head = get_edit_bone("c_p_head" + dupli)	
			neck_twist = get_edit_bone("neck_twist" + dupli)
			
			copy_bone_transforms(head_ref, c_head)
			copy_bone_transforms(head_ref, head)
			copy_bone_transforms(head_ref, head_scale_fix)
			if neck_twist:#retro-compatibility
				copy_bone_transforms(head_ref, neck_twist)
				neck_twist.tail = neck_twist.head + (neck_twist.tail-neck_twist.head)*0.5
			
				# set the visual shape position
			if c_p_head:
				c_p_head.head = head.tail
				c_p_head.tail = c_p_head.head + (head.tail-head.head)/2
				c_p_head.roll = head.roll	
			
			
			# Skulls
				
			skulls = ["c_skull_01" + dupli, "c_skull_02" + dupli, "c_skull_03" + dupli]
			jaw_ref = get_edit_bone("jaw_ref" + dupli)
			project_vec = None
			head_vec = head_ref.tail - head_ref.head	
			
				# if facial is enabled, align skulls with the jaw tail (chin) height for more precise placement. Available only for the main facial, no duplicate
			if is_facial_enabled(bpy.context.active_object) and not '_dupli' in dupli:		
				head_jaw_vec = jaw_ref.tail - head_ref.tail
				project_vec = project_vector_onto_vector(head_jaw_vec, head_vec)
				
				# else align skulls at 1/3 of the neck height
			else:
				neck_ref = get_edit_bone("neck_ref" + dupli)
				head_neck_vec = (neck_ref.tail + (neck_ref.head - neck_ref.tail)*0.3) - head_ref.tail
				project_vec = project_vector_onto_vector(head_neck_vec, head_vec)
				
			
				# start aligning skulls
			i=0 
			for skull in skulls:
				skull_bone = get_edit_bone(skull)
				
				if skull_bone:
					if i == 0:			 
						skull_bone.head = head_ref.tail + project_vec*0.67
						skull_bone.tail = head_ref.tail + project_vec		
						skull_bone.roll = math.radians(90)
					if i == 1:							   
						skull_bone.head = head_ref.tail + project_vec*0.67
						skull_bone.tail = head_ref.tail + project_vec*0.3333
						skull_bone.roll = 0
					if i == 2:							   
						skull_bone.head = head_ref.tail + project_vec*0.3333
						skull_bone.tail = head_ref.tail
						skull_bone.roll = 0
				
				i += 1
			
			if "skull" in locals():
				del skull
			
			
		# Align facial
			# only if enabled
		if get_edit_bone("c_jawbone" + dupli):
			if get_edit_bone("c_jawbone" + dupli).layers[22] == False:
				print('\n Aligning facial...')
				
				#jaw
				c_jaw = get_edit_bone("c_jawbone" + dupli)
				jaw_ref = get_edit_bone("jaw_ref" + dupli)	
				
				# retro-compatibility
				# old case, the jaw is rotation based
				if get_edit_bone("jawbone" + dupli) == None:				
					copy_bone_transforms(jaw_ref, c_jaw)				
				else:
					# new case, the jaw is translation based
					jaw = get_edit_bone("jawbone" + dupli)
					copy_bone_transforms(jaw_ref, jaw)					
					c_jaw.head = jaw.head + (jaw.tail - jaw.head)*0.5
					c_jaw.tail	= c_jaw.head + (jaw.tail - jaw.head) * 0.5
					c_jaw.roll = jaw.roll
					
					
					
					# update lips retain drivers
					for driver in bpy.context.active_object.animation_data.drivers:
						dp_prop = driver.data_path.split(".")[len(driver.data_path.split("."))-1]
						if "jaw_ret_bone" + dupli in driver.data_path and dp_prop == "scale":
							jaw_ret_name = driver.data_path.split('"')[1]
							print("	 jaw_ret =", jaw_ret_name)
							jaw_ret_length = str(round(get_data_bone(jaw_ret_name).length, 4) * 1)
							
							dr = driver.driver							
							dr.expression = 'max(0.05, 1 - (jaw_rot / ' + jaw_ret_length + ') * stretch_value)'							
					if "driver" in locals():	
						del driver		
				
				#jaw_retain
				if bpy.context.active_object.data.edit_bones.get("jaw_ret_bone" + dupli):
					jaw_ret_bone = get_edit_bone("jaw_ret_bone" + dupli)
					copy_bone_transforms(jaw_ref, jaw_ret_bone)
					jaw_ret_bone.tail = jaw_ret_bone.head + (jaw_ret_bone.tail-jaw_ret_bone.head)*0.8
					
				
			
				#cheeks
				cheeks = ["c_cheek_smile", "c_cheek_inflate"]

				for side in [".l", ".r"]:
					for cheek in cheeks:		   
						cheek_ref = get_edit_bone(cheek[2:] + "_ref" + dupli[:-2] + side)
						cheek_bone = get_edit_bone(cheek + dupli[:-2] + side)						
						copy_bone_transforms(cheek_ref, cheek_bone)
					
					if "cheek" in locals(): 
						del cheek
					
					
					#nose
				noses = ["c_nose_01" + dupli, "c_nose_02" + dupli, "c_nose_03" + dupli]
				for nose in noses:
					nose_bone = bpy.context.active_object.data.edit_bones[nose] 
					ref_name = nose[2:-2]+"_ref" + dupli				
					if "_dupli_" in nose:
						ref_name = nose[2:-12]+"_ref" + dupli
					nose_ref = bpy.context.active_object.data.edit_bones[ref_name]
					copy_bone_transforms(nose_ref, nose_bone)
					
				if "nose" in locals():	
					del nose
				
				chins = ["c_chin_01" + dupli, "c_chin_02" + dupli]
				for chin in chins:
					bone = bpy.context.active_object.data.edit_bones[chin]
					bname = chin[2:-2]+"_ref" + dupli
					if "_dupli_" in chin:
						bname = chin[2:-12]+"_ref" + dupli
					ref_bone = get_edit_bone(bname)
					copy_bone_transforms(ref_bone, bone)
				
				if "chin" in locals():	
					del chin
				
				
					#mouth
				tongs = ["c_tong_01" + dupli, "c_tong_02" + dupli, "c_tong_03" + dupli]
				for tong in tongs:		  
					current_bone = get_edit_bone(tong)
					bname = tong[2:-2] + "_ref" + dupli
					if "_dupli_" in tong:
						bname = tong[2:-12] + "_ref" + dupli
					copy_bone_transforms(get_edit_bone(bname), current_bone)
					copy_bone_transforms(get_edit_bone(bname), get_edit_bone(tong[2:]))
					
				if "tong" in locals():	
					del tong
				
				
				teeth = ["c_teeth_top" + dupli, "c_teeth_bot" + dupli, 'c_teeth_top' + dupli[:-2] + ".l", 'c_teeth_top' + dupli[:-2] + ".r", 'c_teeth_bot' + dupli[:-2] + ".l", 'c_teeth_bot' + dupli[:-2] + ".r", 'c_teeth_top_master' + dupli, 'c_teeth_bot_master' + dupli]
				
				for tooth in teeth:			
					current_bone = get_edit_bone(tooth) 
				
					if current_bone:
						if not 'master' in tooth:
							ref_name = tooth.replace('.', '_ref.')[2:]
							if "_dupli_" in tooth:
								ref_name = (tooth[:-12] + "_ref" + dupli)[2:]
							
							tooth1 = get_edit_bone(ref_name)
							if tooth1:
								copy_bone_transforms(tooth1, current_bone)
							else:
								print("	 Missing tooth1:", ref_name)
								
						if tooth == 'c_teeth_top_master' + dupli:	
							ref_top_name = 'teeth_top_ref' + dupli
							ref_top = get_edit_bone(ref_top_name)
							if ref_top:		
								current_bone.head = ref_top.head + (ref_top.head - ref_top.tail)/2
								current_bone.tail = ref_top.tail + (ref_top.head - ref_top.tail)/2
							else:
								print("	 Missing tooth top ref", ref_top_name)
								
						if tooth == 'c_teeth_bot_master' + dupli:					
							ref_bot_name = 'teeth_bot_ref' + dupli
							ref_bot = get_edit_bone(ref_bot_name)
							if ref_bot:
								current_bone.head = ref_bot.head + (ref_bot.head - ref_bot.tail)/2
								current_bone.tail = ref_bot.tail + (ref_bot.head - ref_bot.tail)/2
							else:
								print("	 Missing tooth bot ref", ref_top_name)
					else:
						print("	 Missing tooth:", tooth)
					
				if "tooth" in locals():		
					del tooth

				
				lips = ["c_lips_top.x", "c_lips_bot.x", "c_lips_top", "c_lips_top_01", "c_lips_bot", "c_lips_bot_01", "c_lips_smile", "c_lips_corner_mini", "c_lips_roll_top.x", "c_lips_roll_bot.x"]		
				
				for lip in lips:
				   
					if lip[-2:] == ".x":	
						_sides = [dupli]
					else:
						_sides = [dupli[:-2] + ".l", dupli[:-2] + ".r"]
					
					for _side in _sides:
						ref_name = lip[2:].replace('.x', '') + "_ref" + _side					
						ref_bone = get_edit_bone(ref_name)					
						
						#lips controllers
						cont_name = lip.replace(".x", "") + _side				
						bone = get_edit_bone(cont_name)					
						copy_bone_transforms(ref_bone, bone)
						
						#lips offset bones
						offset_name = lip.replace(".x", "") + "_offset" + _side					
						if bpy.context.active_object.data.edit_bones.get(offset_name):#retro-compatibility
							offset_bone = get_edit_bone(offset_name)
							copy_bone_transforms(ref_bone, offset_bone)
							
						#lips retain bones
						retain_name = lip.replace(".x", "") + "_retain" + _side				
						if bpy.context.active_object.data.edit_bones.get(retain_name):#retro-compatibility
							retain_bone = get_edit_bone(retain_name)
							copy_bone_transforms(ref_bone, retain_bone)			
						
				if "lip" in locals():	
					del lip

				
				# Eyes
					#make list of all eyes bones
				eyes = []
				init_selection("c_eye_offset" + dupli[:-2] + ".l")
				bpy.ops.armature.select_similar(type='CHILDREN')
				for bone in bpy.context.selected_editable_bones[:]:
					if not ".r" in bone.name:#left side only
						eyes.append(bone.name[:-2])			
				
				
				if "bone" in locals():					
					del bone
				
				#direct copy from ref
				for side in [".l", ".r"]:
					for bone in eyes:	
						
						ref_name = bone.replace('c_', '') + "_ref" + side
						cname = bone + dupli[:-2] + side
						if "_dupli_" in bone:
							ref_name = bone.replace('c_', '')[:-10] + "_ref" + dupli[:-2] + side					
							cname = bone[:-10] + dupli[:-2] + side				
						
						bone_ref = get_edit_bone(ref_name)		
						current_bone = get_edit_bone(cname)						
					
						if bone_ref and current_bone:
							copy_bone_transforms(bone_ref, current_bone)
						else:
							if bpy.context.scene.arp_debug_mode:
								print("	 Can't copy bones eye transforms:", bone_ref, current_bone)
					
					if "bone" in locals():	
						del bone
					
					
					# Eyelids
					for id in ["_top", "_bot"]:
						if get_edit_bone("eyelid" + id + dupli[:-2] + side):												
							copy_bone_transforms(get_edit_bone("eyelid" + id + "_ref" + dupli[:-2] + side), get_edit_bone("eyelid" + id + dupli[:-2] + side))
							
							# if the eyelids bones have constraints, they're up to date: new alignment needed:
							bpy.ops.object.mode_set(mode='POSE')
							eyelid_pbone = get_pose_bone("eyelid" + id + dupli[:-2] + side)
							
							if len(eyelid_pbone.constraints) > 0:
								if eyelid_pbone.constraints[0].type == "TRANSFORM":
									print("	 New eyelids found, aligning", "eyelid" + id + dupli[:-2] + side, "...")
									bpy.ops.object.mode_set(mode='EDIT')
									c_eyel = get_edit_bone("c_eyelid" + id + dupli[:-2] + side)
									eyel = get_edit_bone("eyelid" + id + dupli[:-2] + side)
									eye_offset = get_edit_bone("eye_offset_ref" + dupli[:-2] + side)
									c_eyel.head = eyel.tail + (eyel.tail - eyel.head)*1.5
									c_eyel.tail = c_eyel.head + ((eyel.tail - eyel.head) * 0.5)
									
									c_eyel.roll = eyel.roll
									
									# set constraint scale
									bpy.ops.object.mode_set(mode='POSE')
									eyelid_pbone = get_pose_bone("eyelid" + id + dupli[:-2] + side)
									cns = eyelid_pbone.constraints[0]	
									cns.from_min_z = 0.0
									cns.from_max_z = 1.5 
									cns.to_max_x_rot = 1.4 / eyelid_pbone.length
									bpy.ops.object.mode_set(mode='EDIT')
						else:
							print("	 eyelid" + id + dupli[:-2] + side, "not found!")
					
					if "id" in locals():	
						del id
					
					
				eye_additions = ["c_eye", "c_eye_ref_track", "c_eyelid_base", "c_eye_ref"]
				
					#  additional bones	  
				for side in [".l", ".r"]:
					for bone in eye_additions:	   
						
						current_bone = get_edit_bone(bone + dupli[:-2] + side)		
						eye_reference = get_edit_bone("eye_offset_ref" + dupli[:-2] + side)
						copy_bone_transforms(eye_reference, current_bone)
						
						if bone == 'c_eye_ref':
							current_bone.head = eye_reference.tail + (eye_reference.tail-eye_reference.head)
							current_bone.tail = current_bone.head
							current_bone.tail[2] += -0.006
						if bone == 'c_eye_ref_track':
							current_bone.tail = current_bone.head + (current_bone.tail-current_bone.head)/2
				   
					if "bone" in locals():	
						del bone
					
					
					# eye shape scale	 
				
				eye_target_x = get_edit_bone("c_eye_target" + dupli)
				
					# get the distance between the two eyes for correct shape scale		
				eye_l = get_edit_bone("c_eye_target" + dupli[:-2] + ".l")
				eye_r = get_edit_bone("c_eye_target" + dupli[:-2] + ".r")
				eyesballs_dist = 0.1
				
				# Set the eye target distance according to the head size
				dist_from_head = (get_edit_bone("head_ref" + dupli).tail - get_edit_bone("head_ref" + dupli).head).magnitude
				
				# Set the eye target scale according to the eyeballs distance
				if eye_l and eye_r:
					eyesballs_dist = (eye_l.head - eye_r.head).magnitude
				
				print("	   Eyeball dist:", eyesballs_dist)
				
				for side in [".l", ".r"]:
					
					eye_ref = get_edit_bone("eye_offset_ref" + dupli[:-2] + side)
						# .x
				
					eye_target_x.head = eye_ref.head
					eye_target_x.head[0] = 0.0
					eye_target_x.head[1] += -dist_from_head * 1
					eye_target_x.tail = eye_target_x.head
					eye_target_x.tail[2] += 0.5 * eyesballs_dist
				
					# .l and .r		 
					eye_target_side = get_edit_bone("c_eye_target" + dupli[:-2] + side) 
					if round(eye_ref.head[0], 4) == round(eye_ref.tail[0], 4) and round(eye_ref.head[2], 4) == round(eye_ref.tail[2], 4):#if the eye is aligned vert/hor
						print("\n	 Aligned eye:", eye_ref.name)
						eye_target_side.head = eye_target_x.head
						eye_target_side.head[0] = eye_ref.head[0]
						eye_target_side.tail = eye_target_side.head
						eye_target_side.tail[2] = eye_target_x.tail[2]
					else:
						print("\n	 Non-aligned eye:", eye_ref.name, round(eye_ref.head[0], 4), round(eye_ref.tail[0], 4), round(eye_ref.head[2], 4), round(eye_ref.tail[2], 4))
						eye_target_side.head = eye_ref.head + (eye_ref.tail - eye_ref.head)*10
						eye_target_side.tail = eye_target_side.head
						eye_target_side.tail[2] += 0.05
				
				eye_target_x.head[0] = (eye_l.head[0] + eye_r.head[0])*0.5
				eye_target_x.tail[0] = eye_target_x.head[0]
				
				# eyebrows
				eyebrows = []
					# make list of eyebrows
				init_selection("eyebrow_full_ref" + dupli[:-2] + ".l")
				bpy.ops.armature.select_similar(type='CHILDREN')
				for bone in bpy.context.selected_editable_bones[:]:
					if not ".r" in bone.name:#fingers only and left side only
						eyebrows.append(bone.name[:-2])
					
				if "bone" in locals():	
					del bone
				
				for side in [".l", ".r"]:
					for eyebrow in eyebrows:						
						eyeb_name = "c_" + eyebrow[:-4] + dupli[:-2] + side
						ref_name = eyebrow + dupli[:-2] + side
						if "_dupli" in eyebrow:
							eyeb_name = "c_" + eyebrow[:-14] + dupli[:-2] + side
							ref_name = eyebrow[:-10] + dupli[:-2] + side
						
						current_bone = get_edit_bone(eyeb_name)				
						bone_ref = get_edit_bone(ref_name)
						current_bone.head = bone_ref.head
						current_bone.tail = bone_ref.tail
						current_bone.roll = bone_ref.roll  
				 
			 
	
		# Subnecks
		for i in range(1,17):
		
			# align			
			ref_subneck = get_edit_bone('subneck_' + str(i) + "_ref" + dupli)
			cont_subneck = get_edit_bone('c_subneck_' + str(i) + dupli)
			if ref_subneck and cont_subneck:
				cont_subneck.head, cont_subneck.tail, cont_subneck.roll = ref_subneck.head, ref_subneck.tail, ref_subneck.roll
				
				# parent
				if i == 1 and cont_subneck:
					_parent = None
					
					if ref_subneck.parent:
						parent_name = ref_subneck.parent.name.replace("_ref", "")
						if get_edit_bone(parent_name):
							_parent = get_edit_bone(parent_name)
							print("Found subneck parent", parent_name)
						else:
							_parent = ref_subneck.parent
							print("Assign subneck parent", _parent.name)
							
					cont_subneck.parent = _parent
					
		if "i" in locals(): 
			del i		
			
	print("\n Aligning ears")
	for dupli in limb_sides.ear_sides:		
		
		print('[' + dupli + ']')
		
		ears_list = []
		
		for ear_id in range(0,17):
			ear_n = 'ear_' + '%02d' % ear_id + '_ref' + dupli
			if get_edit_bone(ear_n):
				ears_list.append('ear_' + '%02d' % ear_id)
			
		if "ear_id" in locals():	
			del ear_id
		
		
		for ear in ears_list:					
			if get_edit_bone("c_" + ear + dupli):
				ear_bone = get_edit_bone("c_" + ear + dupli)
				if ear_bone.layers[22] == False:				
					ref_bone = get_edit_bone(ear + "_ref" + dupli)
					copy_bone_transforms(ref_bone, ear_bone)
					
					#ear parent
					if ear == "ear_01":					
						if ref_bone.parent: 
							
							if "head_ref" in ref_bone.parent.name:
								ear_bone.parent = get_edit_bone(ref_bone.parent.name.replace('head_ref', 'c_skull_02'))							
							else:
								if ref_bone.parent.name[:-2][-4:] == "_ref":
									if get_edit_bone('c_' + ref_bone.parent.name.replace('_ref', '')):
										ear_bone.parent = get_edit_bone('c_' + ref_bone.parent.name.replace('_ref', ''))
									else:
										ear_bone.parent = get_edit_bone('c_traj')
								else:						
									ear_bone.parent = ref_bone.parent
						else:
							ear_bone.parent = get_edit_bone('c_traj')
		if "ear" in locals():	
			del ear
		
		
   # if breast enabled 
	if get_edit_bone('c_breast_01.l'): 
		print('\n Aligning breasts...')
		breasts = ["c_breast_01", "c_breast_02"]   

		for side in [".l", ".r"]:
			for bone in breasts:		 
				control_bone = get_edit_bone(bone + side)				
				ref_bone = get_edit_bone(bone[2:] + "_ref" + side)
				
				if ref_bone and control_bone:					
					# set transforms
					copy_bone_transforms(ref_bone, control_bone)
				  
					# set parents
					# if the reference bones are parented to the spine bones, find the matching bone for the control bones parent
					parent_dict = {'spine_02_ref.x': 'c_spine_02_bend.x', 'spine_01_ref.x': 'c_spine_01_bend.x', 'spine_03_ref.x': 'c_spine_03.x', 'root_ref.x': 'root.x'}
					if ref_bone.parent:
						bone_ref_parent = ref_bone.parent.name
						if bone_ref_parent in parent_dict:
							corresponding_parent = get_edit_bone(parent_dict[bone_ref_parent])
							if corresponding_parent:
								control_bone.parent = corresponding_parent
					# if there's no parent assigned, find the default parent bone
					else:
						default_parent = get_edit_bone('c_spine_02_bend.x')
						default_parent_traj = get_edit_bone('c_traj')
						if default_parent:
							control_bone.parent = default_parent
						elif default_parent_traj:
							control_bone.parent = default_parent_traj
					
				else:
					if bpy.context.scene.arp_debug_mode == True:
						print("No breasts found, skip it")
		   
			if "bone" in locals():	
				del bone
		
	#switch pose state and mode
	bpy.ops.object.mode_set(mode='POSE')
	
	#set transform constraints factor according to current units
	units_length = bpy.context.scene.unit_settings.scale_length
	
	for pbone in bpy.context.object.pose.bones:
		if len(pbone.constraints) > 0:
			for cns in pbone.constraints:
				if cns.type == 'TRANSFORM':				
					cns.from_min_x *= 1/units_length
					cns.from_max_x *= 1/units_length
					cns.from_min_y *= 1/units_length
					cns.from_max_y *= 1/units_length
					cns.from_min_z *= 1/units_length
					cns.from_max_z *= 1/units_length
	
	if "pbone" in locals(): 
		del pbone
		
	bpy.context.active_object.data.pose_position = 'POSE'	
	
	
	if bpy.context.scene.arp_debug_mode == True:	   
		print("\n FINISH ALIGNING SPINE BONES...\n")
	
	if bpy.context.scene.arp_debug_mode == True:
		print("\n COPY BONES TO RIG ADD ")
	
	copy_bones_to_rig_add(rig, rig_add)
	
	if bpy.context.scene.arp_debug_mode == True:
		print("\n FINISHED COPYING TO RIG ADD ")
		
	
	#--END ALIGN SPINE BONES
	
def switch_bone_layer(bone, base_layer, dest_layer, mirror):
	
	if bone[-2:] == ".x":
		mirror = False
	
	if mirror == False: 
		if get_edit_bone(bone):
			get_edit_bone(bone).layers[dest_layer] = True
			get_edit_bone(bone).layers[base_layer] = False
	
	if mirror == True:
		if get_edit_bone(bone+".l")  and get_edit_bone(bone+".r"):
			get_edit_bone(bone+".l").layers[dest_layer] = True
			get_edit_bone(bone+".l").layers[base_layer] = False
			get_edit_bone(bone+".r").layers[dest_layer] = True
			get_edit_bone(bone+".r").layers[base_layer] = False							
	
def mirror_hack():
	bpy.ops.transform.translate(value=(0, 0, 0), orient_type='NORMAL', proportional='DISABLED')

def init_selection(bone_name):
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='DESELECT')
	
	if (bone_name != "null"):
		bpy.context.active_object.data.edit_bones.active = bpy.context.active_object.data.edit_bones[bone_name]
		get_edit_bone(bone_name).select_head = True
		get_edit_bone(bone_name).select_tail = True
		
		
def select_edit_bone(name):
	bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[name].bone
	get_edit_bone(name).select_head = True
	get_edit_bone(name).select_tail = True
	get_edit_bone(name).select = True
	
def get_data_bone(name):
	try:
		return bpy.context.active_object.data.bones[name]
	except:
		return None
 
def get_pose_bone(name):  
	try:
		return bpy.context.active_object.pose.bones[name]
	except:
		return None

def set_draw_scale(name, size):
	bone = bpy.context.active_object.pose.bones[name+".l"]
	bone.custom_shape_scale = size
	
	
def get_edit_bone(name):
	try:
		return bpy.context.active_object.data.edit_bones[name]
	except KeyError:
		
		return None
		
def is_facial_enabled(armature_object):
	if armature_object.type == "ARMATURE":
		if armature_object.data.bones.get("c_jawbone.x"):
			return True
	return False
	
def copy_bone_transforms(bone1, bone2):
	
	bone2.head = bone1.head
	bone2.tail = bone1.tail
	bone2.roll = bone1.roll
	

def copy_bone_transforms_mirror(bone1, bone2):
	
	bone01 = get_edit_bone(bone1+".l")
	bone02 = get_edit_bone(bone2+".l")
	
	bone02.head = bone01.head
	bone02.tail = bone01.tail
	bone02.roll = bone01.roll
	
	bone01 = get_edit_bone(bone1+".r")
	bone02 = get_edit_bone(bone2+".r")
	
	bone02.head = bone01.head
	bone02.tail = bone01.tail
	bone02.roll = bone01.roll
	
	
def copy_bones_to_rig_add(rig, rig_add):

	rig_add.hide_viewport = False
	
	bone_add_data = {}
	all_bones_data = {}
	edit_rig(rig)
	
	#make dictionnary of bones transforms in armature 1
	rig_add_bone_names = auto_rig_datas.arm_bones_rig_add + auto_rig_datas.leg_bones_rig_add + auto_rig_datas.spine_bones_rig_add
	
	for bone in rig.data.edit_bones:
		all_bones_data[bone.name] = (bone.head.copy(), bone.tail.copy(), bone.roll)
		
		bone_short_name = ""
		
		if not '_dupli_' in bone.name:
			bone_short_name = bone.name[:-2]			
			if bone.name[-2:] == ".x":
				bone_short_name = bone.name
		else:
			bone_short_name = bone.name[:-12]
			if bone.name[-2:] == ".x":
				bone_short_name = bone_short_name + ".x"
				
		if bone_short_name in rig_add_bone_names:
			bone_add_data[bone.name] = (bone.head.copy(), bone.tail.copy(), bone.roll)
	
	if "bone" in locals():	
		del bone
	
	#make sure rig_add collection is visible
	for collec in rig_add.users_collection:
		collec.hide_viewport = False		
	
	edit_rig(rig_add)
	bpy.context.active_object.data.use_mirror_x = False

	#apply the bones transforms to the armature
	"""
	for bone in rig_add.data.edit_bones:
		if bone.name in bone_add_data:
			bone.head, bone.tail, bone.roll = bone_add_data[bone.name]
	"""
	for b in bone_add_data:
		bone = get_edit_bone(b)
		if not bone:
			bone = bpy.context.active_object.data.edit_bones.new(b)
		bone.head, bone.tail, bone.roll = bone_add_data[bone.name]
			
	if "bone" in locals():	
		del bone
			
	#foot_bend, hand_bend, waist_end and epaules_bend bones to block the skin area
	c_waist_bend_end = get_edit_bone('c_waist_bend_end.x')
	if c_waist_bend_end and 'c_spine_02_bend' in all_bones_data:
		c_waist_bend_end.head, c_waist_bend_end.tail, c_waist_bend_end.roll = all_bones_data['c_spine_02_bend.x']
	
	epaules_bend = get_edit_bone('epaules_bend.x')
	if epaules_bend == None:
		print('epaules_bend is missing, create it')
		epaules_bend = bpy.context.active_object.data.edit_bones.new("epaules_bend.x")
		
	if epaules_bend and 'c_spine_02_bend.x' in all_bones_data:
		epaules_bend.head, epaules_bend.tail, epaules_bend.roll = all_bones_data['c_spine_02.x']
		epaules_bend.tail = all_bones_data['head.x'][1]
		print("set epaules_bend transforms:", epaules_bend.head, epaules_bend.tail)

	
	if len(limb_sides.leg_sides) > 0:
		for side in limb_sides.leg_sides:
			foot_bend = get_edit_bone('c_foot_bend'+side)
			if not foot_bend:
				foot_bend = bpy.context.active_object.data.edit_bones.new('c_foot_bend'+side)
			if 'foot'+side in all_bones_data:			
				foot_bend.head, foot_bend.tail, foot_bend.roll = all_bones_data['foot'+side]
		
		if "side" in locals():	
			del side	
	

	if len(limb_sides.arm_sides) > 0:
		for side in limb_sides.arm_sides:			
			hand_bend = rig_add.data.edit_bones.get('hand_bend'+side)
			if not hand_bend:
				hand_bend = bpy.context.active_object.data.edit_bones.new('hand_bend'+side)
			if 'hand' + side in all_bones_data:
				hand_ref_head, hand_ref_tail, hand_ref_roll = all_bones_data['hand'+side]
				hand_bend.head, hand_bend.tail, hand_bend.roll = all_bones_data['hand'+side]
				hand_bend.head += (hand_ref_tail - hand_ref_head)*0.2
				hand_bend.tail += (hand_ref_tail - hand_ref_head)*0.2
		
		if "side" in locals():	
			del side

	null_bend = rig_add.data.edit_bones.get('null_bend.x')
	c_thigh_bend_contact_r = rig_add.data.edit_bones['c_thigh_bend_contact.r']
	c_thigh_bend_contact_l = rig_add.data.edit_bones['c_thigh_bend_contact.l']
	c_waist_bend = rig_add.data.edit_bones['c_waist_bend.x']
	
	if null_bend == None:
		print('null_bend is missing, create it')
		null_bend = rig_add.data.edit_bones.new("null_bend.x")
		
	if c_thigh_bend_contact_l and c_thigh_bend_contact_r and c_waist_bend and null_bend:	
		null_bend.head = (c_thigh_bend_contact_r.head + c_thigh_bend_contact_l.head)*0.5	
		null_bend.tail = null_bend.head + (c_waist_bend.tail - c_waist_bend.head)		
	
	
	# Make sure constraints are ok
	bpy.ops.object.mode_set(mode='POSE')
	for b in rig_add.pose.bones:
		if rig.data.bones.get(b.name):
			cns = None
			if len(b.constraints) != 0:
				cns = b.constraints[0]
			else:
				cns = b.constraints.new("COPY_TRANSFORMS")
				
			cns.target = rig
			cns.subtarget = b.name
			cns.target_space = 'LOCAL'
			cns.owner_space = 'LOCAL'
			
			
	
	if "b" in locals(): 
		del b
	
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')	
	rig_add.hide_viewport = True
	bpy.context.view_layer.objects.active = rig 
	bpy.ops.object.mode_set(mode='POSE')
	
	
def edit_rig(_rig):
	try:
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
	except:
		pass
	_rig.hide_viewport = _rig.hide_select = False	
	_rig.select_set(state=1)	
	bpy.context.view_layer.objects.active = _rig
	
	bpy.ops.object.mode_set(mode='EDIT')
	
def move_bone(bone, value, axis):
	get_edit_bone(bone).head[axis] += value/bpy.context.scene.unit_settings.scale_length#*context.active_object.scale[0]
	get_edit_bone(bone).tail[axis] += value/bpy.context.scene.unit_settings.scale_length#*context.active_object.scale[0]
	
def set_breast(breast_state):

	current_mode = bpy.context.mode
	
	#disable the proxy picker to avoid bugs
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass		
		
	bpy.ops.object.mode_set(mode='EDIT')
	 
	breasts = ["breast_01", "breast_02"]		
   
	for bone in breasts:	
		for side in [".l", ".r"]:
		
			# disabled, delete bones
			if not breast_state: 
				if get_edit_bone("c_" + bone + side):
					bpy.context.active_object.data.edit_bones.remove(get_edit_bone("c_" + bone + side))
				if get_edit_bone(bone + "_ref" + side):
					bpy.context.active_object.data.edit_bones.remove(get_edit_bone(bone + "_ref" + side))
				
				# switch proxy bones layer		
				switch_bone_layer("c_"+bone+"_proxy" + side, 1, 22, False)				

			
			# enabled, create bones
			else:	
				b_ref = get_edit_bone(bone + '_ref' + side)
				b_control = get_edit_bone('c_' + bone + side)
				
				if b_ref == None:				
					b_ref = bpy.context.active_object.data.edit_bones.new(bone + '_ref' + side)
				if b_control == None:				
					b_control = bpy.context.active_object.data.edit_bones.new('c_' + bone + side)
					
				fac = 1
				if side == ".r":
					fac = -1
					
				spine_02 = get_edit_bone('spine_02_ref.x')
				c_traj = get_edit_bone('c_traj')
					
				if bone == 'breast_01': 
					# set bone transforms					
					if spine_02:
						b_ref.head = spine_02.head
						# set x pos
						b_ref.head += (spine_02.x_axis.normalized() * fac * spine_02.length * 0.5)
						# set y pos
						b_ref.head += (spine_02.z_axis.normalized() * spine_02.length * 1)
						
						b_ref.tail = b_ref.head + (spine_02.tail - spine_02.head)*0.25
						
					else:
						if c_traj:
							b_ref.head = [c_traj.length*0.5*fac, 0, 0]
							b_ref.tail = b_ref.head + Vector((0, 0, c_traj.length*0.2))
						else:
							b_ref.head = [fac, 0, 0]
							b_ref.tail = b_ref.head + Vector((0, 0, 1.0))
					
					b_ref.roll = math.radians(90 * fac)					
					
					
				if bone == 'breast_02': 
					# set bone transforms					
					breast_01 = get_edit_bone('breast_01_ref' + side)
					b_ref.head = breast_01.tail + (breast_01.x_axis.normalized() * fac * breast_01.length * 0.5)
					b_ref.tail = b_ref.head + (breast_01.tail - breast_01.head)
					b_ref.roll = breast_01.roll
			
				b_control.head, b_control.tail, b_control.roll = b_ref.head, b_ref.tail, b_ref.roll
					
				# set default parent
				if spine_02:
					b_ref.parent = spine_02
					
				# set deform
				b_ref.use_deform = False
				
				# Set layers						
					# ref bone			
				b_ref.layers[17] = True
				for idx, lay in enumerate(b_ref.layers):
					if idx != 17:
						b_ref.layers[idx] = False
					
					# controller				
				b_control.layers[1] = True
				for idx, lay in enumerate(b_control.layers):
					if idx != 1:
						b_control.layers[idx] = False				
				
				# move proxy bone layer
				switch_bone_layer("c_" + bone + "_proxy" + side, 22, 1, False)
				
				# Set custom shapes and groups
				bpy.ops.object.mode_set(mode='POSE')
				pbone_control = get_pose_bone('c_' + bone + side)
				pbone_ref = get_pose_bone(bone + '_ref' + side)
				
				grp = bpy.context.active_object.pose.bone_groups['body' + side]				
				pbone_control.bone_group = grp
				pbone_ref.bone_group = grp
				cs = None
				
				if bone == 'breast_01':
					if side == ".l":
						cs_name = 'cs_semi_sphere'
					else:
						cs_name = 'cs_semi_sphere_inv'
						
					if bpy.data.objects.get(cs_name) == None:
						append_from_arp(nodes=[cs_name], type="object")
						
					cs = bpy.data.objects[cs_name]					
					pbone_control.custom_shape_scale = 4.0
					
				if bone == 'breast_02':
					if bpy.data.objects.get("cs_arrow_02") == None:
						append_from_arp(nodes=["cs_arrow_02"], type="object")
					cs = bpy.data.objects["cs_arrow_02"]
					
				pbone_control.custom_shape = cs
				
				get_data_bone(pbone_control.name).show_wire = True
					
				bpy.ops.object.mode_set(mode='EDIT')
				
	if "side" in locals():			
		del side
		
	if "bone" in locals():	
		del bone		
	
	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	#restore picker 
	try:		
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state
	except:
		pass	
	
	return None


		
	
def set_tail(tail_state):
	context = bpy.context
	current_mode = context.mode
	active_bone = None
	
	if current_mode == 'POSE':
		try:
			active_bone = context.active_object.data.bones.active.name
		except:
			pass
	if current_mode == 'EDIT_ARMATURE':		   
		try:
			active_bone = context.active_object.data.edit_bones.active.name			
		except:
			pass
	
	# update hack
	bpy.ops.object.editmode_toggle()
	bpy.ops.object.editmode_toggle()
		
	bpy.ops.object.mode_set(mode='EDIT')	
	
	#disable the proxy picker to avoid bugs
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass

	#Active all layers
	#save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):  
		layers_select.append(_layers[i])
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True		
	
	# Get the last existing tail bone position to position bones later
	last_existing_tail = None	
	for i in range(0,32):				
		if get_edit_bone("tail_" + '%02d' % i + '_ref.x'):
			last_existing_tail = get_edit_bone("tail_" + '%02d' % i + '_ref.x').tail.copy()			
	
	# Tail disabled, remove all tail bones
	if not tail_state:
		for i in range(0,32):
			# tail bones names (controller, ref, proxy)
			tail_names = ["c_tail_" + '%02d' % i + '.x', "tail_" + '%02d' % i + '_ref.x', "c_tail_" + '%02d' % i + '_proxy' + '.x']
			for n in tail_names:
				if get_edit_bone(n):					
					context.active_object.data.edit_bones.remove(get_edit_bone(n))		
					print("Delete", n)
			
		tail_master = get_edit_bone("c_tail_master.x")
		if tail_master:
			context.active_object.data.edit_bones.remove(tail_master)	
			
			
	# Tail enabled, setup tail bones
	else:	
		tail_count = context.active_object.rig_tail_count
		assign_to_group = []
		
		
		# If the tail_00_ref bone does not exist, create it first
		if get_edit_bone("tail_00_ref.x") == None:
			root = get_edit_bone("c_traj")
			
			if get_edit_bone("c_root_master.x"):
				root = get_edit_bone("c_root_master.x")
				
			new_tail_ref = bpy.context.active_object.data.edit_bones.new("tail_00_ref.x")	
			new_tail_ref.use_deform = False
			new_tail_ref.head = root.head + (-root.z_axis.normalized() * (root.tail-root.head).magnitude)		
			new_tail_ref.tail = new_tail_ref.head + (-root.z_axis.normalized() * (root.tail-root.head).magnitude*4)
			new_tail_ref.use_deform = False
			if get_edit_bone("root_ref.x"):
				new_tail_ref.parent = get_edit_bone("root_ref.x")
			
		
		
		# If the c_tail_00 bone does not exist, create it first
		if get_edit_bone("c_tail_00.x") == None:			
			
			root = get_edit_bone("c_traj")			
			if get_edit_bone("c_root_master.x"):
				root = get_edit_bone("c_root_master.x")
				
			new_tail_cont = bpy.context.active_object.data.edit_bones.new("c_tail_00.x")	
			new_tail_cont.use_deform = False
			new_tail_cont.head = root.head + (-root.z_axis.normalized() * (root.tail-root.head).magnitude)		
			new_tail_cont.tail = new_tail_cont.head + (-root.z_axis.normalized() * (root.tail-root.head).magnitude*4)
			new_tail_cont.use_deform = True
			if get_edit_bone("root.x"):
				new_tail_cont.parent = get_edit_bone("root.x")
		
		
		
		# Build the tail chain	
		tail_00_ref = get_edit_bone("tail_00_ref.x")		
		tail_vec = tail_00_ref.tail - tail_00_ref.head
		
		if last_existing_tail:		
			tail_vec = last_existing_tail - tail_00_ref.head
			print("Found last tail bone:", last_existing_tail)
			
		tail_origin = tail_00_ref.head
		tail_parent = tail_00_ref.parent
		tail_rig_parent = get_edit_bone("c_tail_00.x").parent
			
		for i in range(0, tail_count):	
			tail_id = '%02d' % i
			tail_id_prev = '%02d' % (i-1)		
			new_tail_ref = None				
			new_tail_rig = None
			
			# if the ref bone does not exist, create it
			tail_ref_name = "tail_" + tail_id + "_ref.x"
			if get_edit_bone(tail_ref_name) == None:
				new_tail_ref = bpy.context.active_object.data.edit_bones.new(tail_ref_name)							
			else:
				new_tail_ref = get_edit_bone(tail_ref_name) 
				
			new_tail_ref.use_deform = False		
				
			# if the controller bone does not exist, create it
			if get_edit_bone("c_tail_" + tail_id + ".x") == None:
				new_tail_rig = bpy.context.active_object.data.edit_bones.new("c_tail_" + tail_id + ".x")				
			else:
				new_tail_rig = get_edit_bone("c_tail_" + tail_id + ".x")	
				new_tail_rig.use_deform = True
				
			assign_to_group.append(new_tail_ref.name)
			assign_to_group.append(new_tail_rig.name)
			
			
			# position the tail ref
			new_tail_ref.head = tail_origin + (tail_vec * (i)) / tail_count
			new_tail_ref.tail = new_tail_ref.head + (tail_vec / tail_count)
			new_tail_ref.roll = tail_00_ref.roll
			
			# position the tail controller
			new_tail_rig.head, new_tail_rig.tail, new_tail_rig.roll = new_tail_ref.head.copy(), new_tail_ref.tail.copy(), new_tail_ref.roll 
			
			# parent the tails		
			if new_tail_ref.parent == None:
				new_tail_ref.parent = get_edit_bone("tail_" + tail_id_prev + "_ref.x")
				new_tail_ref.use_connect = True
			if new_tail_rig.parent == None:
				new_tail_rig.parent = get_edit_bone("c_tail_" + tail_id_prev + ".x")					
			
			
		# Delete out of range tail bones
		for i in range(tail_count,32):
			# tail bones names (controller, ref, proxy)
			tail_names = ["c_tail_" + '%02d' % i + '.x', "tail_" + '%02d' % i + '_ref.x', "c_tail_" + '%02d' % i + '_proxy' + '.x']
			for n in tail_names:
				if get_edit_bone(n):			
					context.active_object.data.edit_bones.remove(get_edit_bone(n))		
					print("Delete", n)
				
		# Master tail controller
		c_tail_master = get_edit_bone("c_tail_master.x")
		
		# if does not exist, create it if more than 1 tail bone
		if tail_count > 1:		
			if c_tail_master == None:
				c_tail_master = bpy.context.active_object.data.edit_bones.new("c_tail_master.x")	
				
			c_tail_master.head = tail_origin +	(tail_vec * 0.5)
			c_tail_master.tail = c_tail_master.head + (tail_vec*0.5)
			c_tail_master.roll = get_edit_bone("tail_00_ref.x").roll
			c_tail_master.parent = tail_parent
			c_tail_master.use_deform = False
			assign_to_group.append(c_tail_master.name)	
		else:
			# if 1 tail bone only, no master needed
			if c_tail_master:
				bpy.context.active_object.data.edit_bones.remove(c_tail_master) 
				
				
		# Set display parameters
		bpy.ops.object.mode_set(mode='POSE')
		
		tail_pbone = get_pose_bone("c_tail_00.x")
		
		for i in assign_to_group:			
			pbone = get_pose_bone(i)
			
			# bone group		
			root_pbone = get_pose_bone("c_traj")
			if get_pose_bone("c_root.x"):
				root_pbone = get_pose_bone("c_root.x")
			pbone.bone_group = root_pbone.bone_group
			
			# custom shape
			if not "_ref.x" in i:
				if not "tail_master" in i:
					if bpy.data.objects.get("cs_torus_03") == None:
						append_from_arp(nodes=["cs_square"], type="object")
						
					pbone.custom_shape = bpy.data.objects["cs_torus_03"]				
					get_data_bone(pbone.name).show_wire = True
					
				if "tail_master" in i:		
					if bpy.data.objects.get("cs_square") == None:
						append_from_arp(nodes=["cs_square"], type="object")
					
					pbone.custom_shape = bpy.data.objects["cs_square"]
					get_data_bone(pbone.name).show_wire = True
				
			# Set layers				
			if not "_ref.x" in i:
			
				# deforming controller bones
				if not "_master" in i:
					for idx, lay in enumerate(get_data_bone(i).layers):
						if idx != 0 and idx != 31:
							get_data_bone(i).layers[idx] = False
						else:
							get_data_bone(i).layers[idx] = True
				
				# master controller
				if "_master" in i:
					for idx, lay in enumerate(get_data_bone(i).layers):
						if idx != 0:
							get_data_bone(i).layers[idx] = False
						else:
							get_data_bone(i).layers[idx] = True
				
				# reference bones
			else:				
				for idx, lay in enumerate(get_data_bone(i).layers):
					if idx != 17:
						get_data_bone(i).layers[idx] = False
						
		# Create tail master constraints
		for i in assign_to_group:
			pbone = get_pose_bone(i)
			if not "_ref.x" in i and not "c_tail_master" in i:			
				cns = None
				if pbone.constraints.get("tail_master_rot") == None:
					cns = pbone.constraints.new('COPY_ROTATION')
				else:
					cns = pbone.constraints["tail_master_rot"]
					
				cns.target = bpy.context.active_object
				cns.subtarget = "c_tail_master.x"
				cns.target_space = cns.owner_space = 'LOCAL'
				cns.use_offset = True
				cns.name = "tail_master_rot"
					
		if tail_count > 1:			
			if get_pose_bone("c_tail_master.x"):
				get_pose_bone("c_tail_master.x").custom_shape_transform = get_pose_bone("c_tail_00.x")
				get_pose_bone("c_tail_master.x").custom_shape_scale = 0.4
			
		
	# Restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'		
	
	bpy.ops.object.mode_set(mode=current_mode)
	
	# Restore selected bone
	if active_bone:
		bone_to_select = None
		if current_mode == 'POSE':		
			if get_pose_bone(active_bone):
				bone_to_select = get_pose_bone(active_bone).bone
			else:
				if get_pose_bone("c_pos"):
					bone_to_select = get_pose_bone("c_pos").bone
					
			if bone_to_select:
				bpy.context.active_object.data.bones.active = bone_to_select
			
			
		if current_mode == 'EDIT':	
			bone_to_select = None
			if get_edit_bone(active_bone):
				bone_to_select = get_edit_bone(active_bone)
			else:
				if get_edit_bone("root_ref.x"):
					bone_to_select = get_edit_bone("root_ref.x")
			if bone_to_select:
				bpy.context.active_object.data.edit_bones.active = bone_to_select
		
	# Restore layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = layers_select[i]		
		
	#restore picker 
	try:		
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state
	except:
		pass	
		
	
	

def set_toes(thumb, index, middle, ring, pinky):
	context = bpy.context
	active_bone = context.active_object.data.edit_bones.active.name
	rig_name = bpy.context.active_object.name
	
	# get the bone side
	side = ""
	if len(bpy.context.selected_editable_bones) > 0:
		b_name = bpy.context.selected_editable_bones[0].name		
		side = b_name[-2:]
		if '_dupli_' in b_name:
			side = b_name[-12:]						
	else:
		print("No bone selected")		
		
	foot_ref = get_edit_bone("foot_ref" + side)
	
	if not foot_ref:
		print("foot_ref" + side, "does not exist, cannot create toes")
		return
		
	foot_ref_dir = (foot_ref.tail - foot_ref.head)
	
	# disable X Mirror
	xmirror_state = bpy.context.object.data.use_mirror_x
	bpy.context.object.data.use_mirror_x = False
	
	#disable the proxy picker to avoid bugs
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass
	
	#Active all layers
	# and save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):  
		layers_select.append(_layers[i])
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True 
		
	def create_toe(toe_type=""):
		if toe_type == "thumb":
			toe_ref_list = auto_rig_datas.toes_thumb_ref_list
			toe_control_list = auto_rig_datas.toes_thumb_control_list			
			
		if toe_type == "index":
			toe_ref_list = auto_rig_datas.toes_index_ref_list
			toe_control_list = auto_rig_datas.toes_index_control_list
						
		if toe_type == "middle":
			toe_ref_list = auto_rig_datas.toes_middle_ref_list
			toe_control_list = auto_rig_datas.toes_middle_control_list
				
		if toe_type == "ring":
			toe_ref_list = auto_rig_datas.toes_ring_ref_list
			toe_control_list = auto_rig_datas.toes_ring_control_list
					
		if toe_type == "pinky":
			toe_ref_list = auto_rig_datas.toes_pinky_ref_list
			toe_control_list = auto_rig_datas.toes_pinky_control_list
						
		exist_already = False
		if get_edit_bone(toe_ref_list[0] + side):
			exist_already = True
			
		if not exist_already:		
			print("toe", toe_type, "does not exist, create bones")
			type = toe_type + side[-2:]
			addon_directory = os.path.dirname(os.path.abspath(__file__))		
			filepath = addon_directory + "/armature_presets/modules.blend"			
			
			# make a list of current custom shapes objects in the scene for removal later
			cs_objects = [obj.name for obj in bpy.data.objects if obj.name[:3] == "cs_"]			
			
			# load the objects in the blend file datas
			with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to): 
				# only import the necessary armature
				data_to.objects = [i for i in data_from.objects if i == "rig_toes_" + type]
									
			# link in scene
			for obj in data_to.objects:				
				context.scene.collection.objects.link(obj)
				print("Linked armature:", obj.name)
			bpy.ops.object.mode_set(mode='OBJECT')
			
			# replace custom shapes by custom shapes already existing in the scene
			set_active_object('rig_toes_' + type)			
			bpy.ops.object.mode_set(mode='POSE')			
			for b in bpy.context.active_object.pose.bones:				
				if b.custom_shape:					
					if b.custom_shape.name not in cs_objects:						
						if b.custom_shape.name.replace('.001', '') in cs_objects:
							b.custom_shape = bpy.data.objects[b.custom_shape.name.replace('.001', '')]
						
				# naming
				if "_dupli_" in side:
					b.name = b.name.split('.')[0] + side
					
							
				# find added/useless custom shapes and delete them			
				for obj in bpy.data.objects:
					if obj.name[:3] == "cs_":
						if not obj.name in cs_objects:						
							bpy.data.objects.remove(obj, do_unlink=True)			
			
			bpy.ops.object.mode_set(mode='OBJECT')			
			
			# Merge to the main armature
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object('rig_toes_' + type)
			set_active_object(rig_name)
			bpy.ops.object.mode_set(mode='OBJECT')	
			bpy.ops.object.join()
			
			# Parent lost bones
			bpy.ops.object.mode_set(mode='EDIT')	
			for bn in bpy.context.active_object.data.edit_bones:
				if len(bn.keys()) > 0:
					if "arp_parent" in bn.keys():
						parent_prop = get_edit_bone(bn["arp_parent"].split(".")[0]+side)
						if bn.parent == None and parent_prop:
							bn.parent = parent_prop
							
			# move all new toe bones near the foot			
			b1 = get_edit_bone(toe_ref_list[0] + side)
			if len(b1.keys()) > 0:
				if "arp_offset_matrix" in b1.keys():
					ob_mat = bpy.context.active_object.matrix_world
					foot_ref = get_edit_bone("toes_ref" + side)
					b1_local = Matrix(b1["arp_offset_matrix"]) @ ob_mat @ b1.matrix
					
					# store children bones matrix					
					children_bones = toe_ref_list + toe_control_list
					children_bones.remove(toe_ref_list[0])					
					children_mat_dict = {}
					for child_name in children_bones:
						children_mat_dict[get_edit_bone(child_name+side)] = b1.matrix.inverted() @ get_edit_bone(child_name+side).matrix
										
					# move b1
					b1.matrix = foot_ref.matrix @ b1_local
					# move other bones
					for child_ in children_mat_dict:
						child_.matrix = b1.matrix @ ob_mat @ children_mat_dict[child_]
						
					# store current bones coords copy in a new dict to avoid the multiple transform issue when bones have connected parent 
					bones_coords = {}
					for b in children_mat_dict:
						bones_coords[b] = b.head.copy(), b.tail.copy()
					
					# scale proportionally to the head bone
					scale_from_origin(ed_bone=b1, center=foot_ref.head, factor=(foot_ref.tail-foot_ref.head).magnitude*19)
					
					for eb in bones_coords:
						scale_from_origin(ed_bone=eb, center=foot_ref.head, head_coords=bones_coords[eb][0], tail_coords=bones_coords[eb][1], factor=(foot_ref.tail-foot_ref.head).magnitude*19)
	
		else:
			print(toe_type, "already created")
		# -- End function create_toe()
		
	def disable_toe(toe_type=""):
		if toe_type == "thumb":
			toe_ref_list = auto_rig_datas.toes_thumb_ref_list
			toe_control_list = auto_rig_datas.toes_thumb_control_list
		
		if toe_type == "index":
			toe_ref_list = auto_rig_datas.toes_index_ref_list
			toe_control_list = auto_rig_datas.toes_index_control_list
			
		if toe_type == "middle":
			toe_ref_list = auto_rig_datas.toes_middle_ref_list
			toe_control_list = auto_rig_datas.toes_middle_control_list
				
		if toe_type == "ring":
			toe_ref_list = auto_rig_datas.toes_ring_ref_list
			toe_control_list = auto_rig_datas.toes_ring_control_list
			
		if toe_type == "pinky":
			toe_ref_list = auto_rig_datas.toes_pinky_ref_list
			toe_control_list = auto_rig_datas.toes_pinky_control_list
		
		# delete bones
		for bname in toe_ref_list + toe_control_list:
			toe_bone = get_edit_bone(bname + side)
			if toe_bone:
				bpy.context.active_object.data.edit_bones.remove(toe_bone)
		
		if 'b_name' in locals():
			del b_name
		
		# proxy picker bones
		for bname in toe_control_list:
			toe_picker = get_edit_bone(bname + "_proxy" + side)
			if toe_picker:
				switch_bone_layer(toe_picker.name, 0, 22, False)
	
	
	# Set toes
	if not thumb:
		disable_toe(toe_type="thumb")		
	else:
		# create bones
		create_toe(toe_type="thumb")
						
	if not index:
		disable_toe(toe_type="index")		
	else:
		# create bones
		create_toe(toe_type="index")	

	if not middle:
		disable_toe(toe_type="middle")		
	else:
		# create bones
		create_toe(toe_type="middle")	
	
	if not ring:
		disable_toe(toe_type="ring")		
	else:
		# create bones
		create_toe(toe_type="ring")
		
	if not pinky:
		disable_toe(toe_type="pinky")		
	else:
		# create bones
		create_toe(toe_type="pinky")
		
	
	# Restore layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = layers_select[i]		
	
	# restore X Mirror state
	bpy.context.object.data.use_mirror_x = xmirror_state

	
	#restore picker 
	try:		
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state
	except:
		pass
		
	# End set_toes()

def set_fingers(thumb, index, middle, ring, pinky):
	context = bpy.context
	active_bone = context.active_object.data.edit_bones.active.name
	rig_name = bpy.context.active_object.name
	
	# get the bone side
	side = ""
	if len(bpy.context.selected_editable_bones) > 0:
		b_name = bpy.context.selected_editable_bones[0].name		
		side = b_name[-2:]
		if '_dupli_' in b_name:
			side = b_name[-12:]						
	else:
		print("No bone selected")		
		
	hand_ref = get_edit_bone("hand_ref" + side)
	
	if not hand_ref:
		print("hand_ref" + side, "does not exist, cannot create fingers")
		return
		
	#disable the proxy picker to avoid bugs
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass
	
	#Active all layers
	# and save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):  
		layers_select.append(_layers[i])
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True 
		
	def create_finger(finger_type=""):
		if finger_type == "thumb":
			finger_ref_list = auto_rig_datas.thumb_ref_list
			finger_control_list = auto_rig_datas.thumb_control_list
			finger_intern_list = auto_rig_datas.thumb_intern_list
			
		if finger_type == "index":
			finger_ref_list = auto_rig_datas.index_ref_list
			finger_control_list = auto_rig_datas.index_control_list
			finger_intern_list = auto_rig_datas.index_intern_list
			
		if finger_type == "middle":
			finger_ref_list = auto_rig_datas.middle_ref_list
			finger_control_list = auto_rig_datas.middle_control_list
			finger_intern_list = auto_rig_datas.middle_intern_list
		
		if finger_type == "ring":
			finger_ref_list = auto_rig_datas.ring_ref_list
			finger_control_list = auto_rig_datas.ring_control_list
			finger_intern_list = auto_rig_datas.ring_intern_list
			
		if finger_type == "pinky":
			finger_ref_list = auto_rig_datas.pinky_ref_list
			finger_control_list = auto_rig_datas.pinky_control_list
			finger_intern_list = auto_rig_datas.pinky_intern_list	
			
		exist_already = False
		if get_edit_bone(finger_ref_list[0] + side):
			exist_already = True
			
		if not exist_already:		
			print(finger_type, "does not exist, create bones")
			type = finger_type + side[-2:]
			addon_directory = os.path.dirname(os.path.abspath(__file__))		
			filepath = addon_directory + "/armature_presets/modules.blend"			
			
			# make a list of current custom shapes objects in the scene for removal later
			cs_objects = [obj.name for obj in bpy.data.objects if obj.name[:3] == "cs_"]			
			
			# load the objects in the blend file datas
			with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to): 
				# only import the necessary armature
				data_to.objects = [i for i in data_from.objects if i == "rig_" + type]
									
			# link in scene
			for obj in data_to.objects:				
				context.scene.collection.objects.link(obj)
				print("Linked armature:", obj.name)
			bpy.ops.object.mode_set(mode='OBJECT')
			
			# replace custom shapes by custom shapes already existing in the scene
			set_active_object('rig_' + type)			
			bpy.ops.object.mode_set(mode='POSE')			
			for b in bpy.context.active_object.pose.bones:				
				if b.custom_shape:					
					if b.custom_shape.name not in cs_objects:						
						if b.custom_shape.name.replace('.001', '') in cs_objects:
							b.custom_shape = bpy.data.objects[b.custom_shape.name.replace('.001', '')]
						
				# naming
				if "_dupli_" in side:
					b.name = b.name.split('.')[0] + side
					
				# set constraints			
				if len(b.constraints) > 0:
					for cns in b.constraints:
						try:
							if cns.target == None:
								cns.target = bpy.data.objects[rig_name]
							if "_dupli_" in side:
								if cns.subtarget == "hand" + side[-2:]:
									cns.subtarget = "hand" + side
						except:
							pass
			
			# replace drivers variables
			for dr in bpy.context.active_object.animation_data.drivers:
				if 'pose.bones' in dr.data_path:			
					b  = dr.data_path.split('"')[1]			
					if side in b and b.replace(side, "") in finger_intern_list:
						
						for var in dr.driver.variables:
							for tar in var.targets:
								if not side in tar.data_path:
									print("replaced driver var data path")
									print(tar.data_path)					
									tar.data_path = tar.data_path.replace(side[-2:], side)
									print("=>", tar.data_path)
					
				
				# find added/useless custom shapes and delete them			
				for obj in bpy.data.objects:
					if obj.name[:3] == "cs_":
						if not obj.name in cs_objects:						
							bpy.data.objects.remove(obj, do_unlink=True)			
			
			bpy.ops.object.mode_set(mode='OBJECT')			
			
			# Merge to the main armature
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object('rig_' + type)
			set_active_object(rig_name)
			bpy.ops.object.mode_set(mode='OBJECT')	
			bpy.ops.object.join()
			
			# Parent lost bones
			bpy.ops.object.mode_set(mode='EDIT')	
			for bn in bpy.context.active_object.data.edit_bones:
				if len(bn.keys()) > 0:
					if "arp_parent" in bn.keys():
						parent_prop = get_edit_bone(bn["arp_parent"].split(".")[0]+side)
						if bn.parent == None and parent_prop:
							bn.parent = parent_prop
							
			# move all new finger bones near the hand
			b1 = get_edit_bone(finger_ref_list[0] + side)
			if len(b1.keys()) > 0:				
				if "arp_offset_matrix" in b1.keys():
					ob_mat = bpy.context.active_object.matrix_world
					hand_ref = get_edit_bone("hand_ref" + side)
					b1_local = Matrix(b1["arp_offset_matrix"]) @ ob_mat @ b1.matrix
					
					# store children bones matrix					
					children_bones = finger_ref_list + finger_control_list + finger_intern_list
					children_bones.remove(finger_ref_list[0])					
					children_mat_dict = {}
					for child_name in children_bones:
						children_mat_dict[get_edit_bone(child_name+side)] = b1.matrix.inverted() @ get_edit_bone(child_name+side).matrix
										
					# move b1
					b1.matrix = hand_ref.matrix @ b1_local
					# move other bones
					for child_ in children_mat_dict:
						child_.matrix = b1.matrix @ ob_mat @ children_mat_dict[child_]
						
					# store current bones coords copy in a new dict to avoid the multiple transform issue when bones have connected parent 
					bones_coords = {}
					for b in children_mat_dict:
						bones_coords[b] = b.head.copy(), b.tail.copy()
					
					# scale proportionally to the head bone
					scale_from_origin(ed_bone=b1, center=hand_ref.head, factor=(hand_ref.tail-hand_ref.head).magnitude*19)
					
					for eb in bones_coords:
						scale_from_origin(ed_bone=eb, center=hand_ref.head, head_coords=bones_coords[eb][0], tail_coords=bones_coords[eb][1], factor=(hand_ref.tail-hand_ref.head).magnitude*19)
	
		else:
			print(finger_type, "already created")
		# -- End function create_finger()
		
	def disable_finger(finger_type=""):
		if finger_type == "thumb":
			finger_ref_list = auto_rig_datas.thumb_ref_list
			finger_control_list = auto_rig_datas.thumb_control_list
			finger_intern_list = auto_rig_datas.thumb_intern_list
			
		if finger_type == "index":
			finger_ref_list = auto_rig_datas.index_ref_list
			finger_control_list = auto_rig_datas.index_control_list
			finger_intern_list = auto_rig_datas.index_intern_list
			
		if finger_type == "middle":
			finger_ref_list = auto_rig_datas.middle_ref_list
			finger_control_list = auto_rig_datas.middle_control_list
			finger_intern_list = auto_rig_datas.middle_intern_list
		
		if finger_type == "ring":
			finger_ref_list = auto_rig_datas.ring_ref_list
			finger_control_list = auto_rig_datas.ring_control_list
			finger_intern_list = auto_rig_datas.ring_intern_list
			
		if finger_type == "pinky":
			finger_ref_list = auto_rig_datas.pinky_ref_list
			finger_control_list = auto_rig_datas.pinky_control_list
			finger_intern_list = auto_rig_datas.pinky_intern_list	
			
		# delete bones
		for bname in finger_ref_list + finger_control_list + finger_intern_list:
			finger_bone = get_edit_bone(bname + side)
			if finger_bone:
				bpy.context.active_object.data.edit_bones.remove(finger_bone)
		
		if 'b_name' in locals():
			del b_name
		
		# proxy picker bones
		for bname in finger_control_list:
			finger_picker = get_edit_bone(bname + "_proxy" + side)
			if finger_picker:
				switch_bone_layer(finger_picker.name, 0, 22, False)
	
		bpy.ops.object.mode_set(mode='OBJECT')
		clean_drivers()
		bpy.ops.object.mode_set(mode='EDIT')	
		
		
	# Set fingers
	if not thumb:
		disable_finger(finger_type="thumb")		
	else:
		# create bones
		create_finger(finger_type="thumb")
						
	if not index:
		disable_finger(finger_type="index")		
	else:
		# create bones
		create_finger(finger_type="index")	

	if not middle:
		disable_finger(finger_type="middle")		
	else:
		# create bones
		create_finger(finger_type="middle") 
	
	if not ring:
		disable_finger(finger_type="ring")		
	else:
		# create bones
		create_finger(finger_type="ring")
		
	if not pinky:
		disable_finger(finger_type="pinky")		
	else:
		# create bones
		create_finger(finger_type="pinky")
		
	
	# Restore layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = layers_select[i]		
		
	#restore picker 
	try:		
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state
	except:
		pass		
		
	# End set_fingers()
	
	
def set_neck(neck_count):

	context = bpy.context
	current_mode = context.mode
	
	active_bone = None
	
	if current_mode == 'POSE':
		try:
			active_bone = context.active_object.data.bones.active.name
		except:
			pass
	if current_mode == 'EDIT_ARMATURE':		   
		try:
			active_bone = context.active_object.data.edit_bones.active.name			
		except:
			pass
		
	bpy.ops.object.mode_set(mode='EDIT')	
	
	# update hack
	bpy.ops.object.editmode_toggle()
	bpy.ops.object.editmode_toggle()
	
	#disable the proxy picker to avoid bugs
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass
		
	#Active all layers
	#save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):  
		layers_select.append(_layers[i])

	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True 
		
		
	side = ".x"
	# get the bone side
	if len(bpy.context.selected_editable_bones) > 0:
		b_name = bpy.context.selected_editable_bones[0].name
		# only if it's a ref bone
		if len(b_name.split('_')) >= 2:
			if (b_name.split('_')[1][:3] == 'ref' and b_name.split('_')[0] == 'neck') or (b_name.split('_')[2][:3] == 'ref' and b_name.split('_')[0] == 'subneck'):
				side = b_name[-2:]
				if '_dupli_' in b_name:
					side = b_name[-12:]				
			else:
				print("No reference neck bone selected:", b_name)
	else:
		print("No bone selected")		
		
	assign_to_group = []	
	neck_ref = get_edit_bone("neck_ref" + side)
	neck_rig = get_edit_bone("c_neck" + side)		

	# More than 1 neck, add subneck
	if neck_count > 1:		
		neck_vec = None
		neck_origin = None
		neck_parent = None
		neck_rig_parent = None			
		
		if get_edit_bone("subneck_1_ref" + side) == None:
			neck_vec = neck_ref.tail - neck_ref.head
			neck_origin = neck_ref.head 
			neck_parent = neck_ref.parent
			neck_rig_parent = neck_rig.parent
		else:
			neck_vec = neck_ref.tail -	get_edit_bone("subneck_1_ref" + side).head
			neck_origin = get_edit_bone("subneck_1_ref" + side).head
			neck_parent = get_edit_bone("subneck_1_ref" + side).parent
			neck_rig_parent =  get_edit_bone("c_subneck_1" + side).parent
			
		# build the subneck chain
		for i in range(1, neck_count):	
			# print("I", i)
			# if the subneck does not exist, create it
			if get_edit_bone("subneck_" + str(i) + "_ref" + side) == None:
				subneck = bpy.context.active_object.data.edit_bones.new("subneck_" + str(i) + "_ref" + side)	
				subneck.use_deform = False				
			else:
				subneck = get_edit_bone("subneck_" + str(i) + "_ref" + side)					
			
			if get_edit_bone("c_subneck_" + str(i) + side) == None:
				subneck_rig = bpy.context.active_object.data.edit_bones.new("c_subneck_" + str(i) + side)				
			else:
				subneck_rig = get_edit_bone("c_subneck_" + str(i) + side)	
				
			assign_to_group.append(subneck.name)
			assign_to_group.append(subneck_rig.name)
			
			
			# position the subneck
			subneck.head = neck_origin + (neck_vec * (i-1)) / neck_count
			subneck.tail = subneck.head + (neck_vec / neck_count)
			subneck.roll = neck_ref.roll
			
			subneck_rig.head, subneck_rig.tail, subneck_rig.roll = subneck.head.copy(), subneck.tail.copy(), subneck.roll	
			
			# parent the subneck
			if i == 1:
				subneck.parent = neck_parent
				
			else:
				subneck.parent = get_edit_bone("subneck_" + str(i-1) + "_ref" + side)
				subneck_rig.parent = get_edit_bone("c_subneck_" + str(i-1) + side)					
				subneck.use_connect = True
		
		# Master neck controller
			# if does not exist, create it
		c_neck_master = get_edit_bone("c_neck_master" + side)
		if c_neck_master == None:
			c_neck_master = bpy.context.active_object.data.edit_bones.new("c_neck_master" + side)	
			
		c_neck_master.head = neck_origin +	(neck_vec * 0.5)
		c_neck_master.tail = c_neck_master.head + (neck_vec*0.5)
		c_neck_master.roll = neck_ref.roll
		c_neck_master.parent = neck_parent
		c_neck_master.use_deform = False
		assign_to_group.append(c_neck_master.name)		
		
		# Parent the neck_ref
		last_subneck = get_edit_bone("subneck_" + str(neck_count-1) + "_ref" + side)
		last_subneck_rig = get_edit_bone("c_subneck_" + str(neck_count-1) + side)
		neck_ref.parent = last_subneck
		neck_rig.parent = last_subneck_rig
		neck_rig.use_connect = True
		neck_ref.use_connect = True
		
		
	else:# just one neck			
		if get_edit_bone("subneck_1_ref" + side):
			neck_ref.head = get_edit_bone("subneck_1_ref" + side).head
			neck_ref.parent = get_edit_bone("subneck_1_ref" + side).parent
			neck_rig.head, neck_rig.tail  = neck_ref.head, neck_ref.tail
			
			# delete the neck master controller
			if get_edit_bone("c_neck_master" + side):
				bpy.context.active_object.data.edit_bones.remove(get_edit_bone("c_neck_master" + side))
				
				
	# Delete unused subnecks	
	for i in range(neck_count, 16):
		#print("checking bone", 'subneck_' + str(i) + side)
		subneck_ref = get_edit_bone('subneck_' + str(i) + '_ref' + side)
		if subneck_ref:
			bpy.context.active_object.data.edit_bones.remove(subneck_ref)
			#print("deleting")
			
		subneck_cont = get_edit_bone('c_subneck_' + str(i) + side)
		if subneck_cont:
			bpy.context.active_object.data.edit_bones.remove(subneck_cont)				
	
	# Set display parameters
	bpy.ops.object.mode_set(mode='POSE')
	
	neck_pbone = get_pose_bone("c_neck" + side)
	
	for i in assign_to_group:			
		pbone = get_pose_bone(i)
		
		# bone group
		if neck_pbone.bone_group:
			pbone.bone_group = neck_pbone.bone_group
		
		# custom shape
		if not "_ref" + side in i:
			if neck_pbone.custom_shape  and not "neck_master" in i:
				pbone.custom_shape = neck_pbone.custom_shape				
				get_data_bone(pbone.name).show_wire = True
				
			if "neck_master" in i:		
				if bpy.data.objects.get("cs_square") == None:
					append_from_arp(nodes=["cs_square"], type="object")
				
				pbone.custom_shape = bpy.data.objects["cs_square"]
				get_data_bone(pbone.name).show_wire = True
			
		# set layers
		#  deforming bones
		if not "_ref" + side in i:
			if not "_master" in i:
				for idx, lay in enumerate(get_data_bone(i).layers):
					if idx != 0 and idx != 31:
						get_data_bone(i).layers[idx] = False
						
			if "_master" in i:
				for idx, lay in enumerate(get_data_bone(i).layers):
					if idx != 0:
						get_data_bone(i).layers[idx] = False
					
		#  reference bones
		else:				
			for idx, lay in enumerate(get_data_bone(i).layers):
				if idx != 17:
					get_data_bone(i).layers[idx] = False
					
	# Create neck master constraints
	for i in assign_to_group + ["c_neck" + side]:	
		pbone = get_pose_bone(i)
		if not ("_ref" + side) in i and not "c_neck_master" in i:
		
			cns = None
			if pbone.constraints.get("neck_master_rot") == None:
				cns = pbone.constraints.new('COPY_ROTATION')
			else:
				cns = pbone.constraints["neck_master_rot"]
				
			cns.target = bpy.context.active_object
			cns.subtarget = "c_neck_master" + side
			cns.target_space = cns.owner_space = 'LOCAL'
			cns.use_offset = True
			cns.name = "neck_master_rot"
				
	if neck_count > 1:	
		neck_pbone.custom_shape_transform = None
		
		if get_pose_bone("c_neck_master" + side):
			get_pose_bone("c_neck_master" + side).custom_shape_transform = get_pose_bone("c_neck" + side)
			get_pose_bone("c_neck_master" + side).custom_shape_scale = 0.4
		if get_pose_bone("c_p_neck" + side):
			neck_pbone.custom_shape_transform = get_pose_bone('c_p_neck' + side)		
	
	
	# Restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'		
	
	bpy.ops.object.mode_set(mode=current_mode)
	
	# Restore selected bone
	if active_bone:
		if current_mode == 'POSE':		
			if get_pose_bone(active_bone):
				bpy.context.active_object.data.bones.active = get_pose_bone(active_bone).bone	 
		
		if current_mode == 'EDIT':		
		
			if get_edit_bone(active_bone):
				bpy.context.active_object.data.edit_bones.active = get_edit_bone(active_bone)
		
	# Restore layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = layers_select[i]		
		
	#restore picker 
	try:		
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state
	except:
		pass	
	
	# End set_necks()
				

def set_spine(bottom=False):
	context = bpy.context
	current_mode = context.mode
	
	if get_data_bone("root_ref.x") == None:
		print("root_ref.x not found, cannot set spine bones")
		return
	
	#disable the proxy picker to avoid bugs
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass	
	
	active_bone = None
	
	if current_mode == 'POSE':
		try:
			active_bone = context.active_object.data.bones.active.name
		except:
			pass
	if current_mode == 'EDIT_ARMATURE':		   
		try:
			active_bone = context.active_object.data.edit_bones.active.name			
		except:
			pass
	 
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='DESELECT')
	obj = bpy.context.active_object 
	rig_name = obj.name
	
	#Active all layers
		#save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):  
		layers_select.append(_layers[i])

	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True 
	
	all_is_there = False
	
	if obj.rig_spine_count >= 1:		
	
		# get current root-tip positions of the spine
		spine_root_tip = [get_edit_bone("root_ref.x").head.copy(), get_edit_bone("root_ref.x").tail.copy()]
		# get the root et tip children to restore afterward		
		tip_children = []
		total_spine_found = 1
		for idx in range(1, 5):				
			spine_ref = get_edit_bone('spine_0' + str(idx) + '_ref.x')
			if spine_ref:			
				spine_root_tip[1] = spine_ref.tail.copy()
				total_spine_found += 1
				
			else:			
				# store the tip children
				spine_bone_name = 'spine_0' + str(idx-1) + '_ref.x'
				if idx == 1:
					spine_bone_name = 'root_ref.x'
				
				spine_ref_previous = get_edit_bone(spine_bone_name)
				if spine_ref_previous:				
					for b in bpy.context.active_object.data.edit_bones:						
						if b.parent != None and b.layers[17]:													
							if b.parent == spine_ref_previous and not "spine_" in b.name:
								tip_children.append(b.name)							
				break				
			
		print("tip_children", tip_children)
		# if the all spine bones are already there, return
		if total_spine_found == obj.rig_spine_count:
			all_is_there = True
		
		if not all_is_there:		
			
			spine_vec = spine_root_tip[1] - spine_root_tip[0]
			
			# delete out of range spine bones if any			
			for idx in range(obj.rig_spine_count, 4):
				# ref bones
				spine_ref = get_edit_bone('spine_0' + str(idx) + '_ref.x')
				if spine_ref:
					print("Delete", spine_ref.name)
					bpy.context.active_object.data.edit_bones.remove(spine_ref)
			
				# control bones
				spine_cont = get_edit_bone("c_spine_0" + str(idx) + ".x")
				if spine_cont:
					print("Delete", spine_cont.name)
					bpy.context.active_object.data.edit_bones.remove(spine_cont)
					
				spine_bend_cont = get_edit_bone("c_spine_0" + str(idx) +"_bend.x")
				if spine_bend_cont:
					print("Delete", spine_bend_cont.name)
					bpy.context.active_object.data.edit_bones.remove(spine_bend_cont)
					
				# deform bones
				spine_def = get_edit_bone('spine_0' + str(idx) + '.x')
				if spine_def:
					print("Delete", spine_def.name)
					bpy.context.active_object.data.edit_bones.remove(spine_def)
				
					# delete the waist bend bone if only 1 spine bone
				if obj.rig_spine_count == 1:
					waist_bend = get_edit_bone("c_waist_bend.x")
					if waist_bend:
						bpy.context.active_object.data.edit_bones.remove(waist_bend)
						
						# from the rig_add too
						rig_add = get_rig_add(bpy.context.active_object)
						if rig_add:
							edit_rig(rig_add)
							waist_bend_add = get_edit_bone("c_waist_bend.x")
							if waist_bend_add:
								bpy.context.active_object.data.edit_bones.remove(waist_bend_add)
								
							bpy.ops.object.mode_set(mode='OBJECT')
							rig_add.select_set(state=False)
							edit_rig(bpy.data.objects[rig_name])
					
				# display position bones
				spine_c_p = get_edit_bone("c_p_spine_0" + str(idx) +".x")
				if spine_c_p:
					print("Delete", spine_c_p.name)
					bpy.context.active_object.data.edit_bones.remove(spine_c_p)
			
			
			
			# create new bones
			bones_created = []
			spine_bones_ref = ['root_ref.x']
			for idx in range(1, obj.rig_spine_count):
				ref_name = 'spine_0' + str(idx) + '_ref.x'
				spine_bones_ref.append(ref_name)
			
			for idx, ref_name in enumerate(spine_bones_ref):		
				
				# ref bones
				spine_ref = get_edit_bone(ref_name)
				if not spine_ref:
					spine_ref = bpy.context.active_object.data.edit_bones.new(ref_name) 
					spine_ref.use_deform = False
					bones_created.append(spine_ref.name)				
					# layer
					spine_ref.layers[17] = True
					for i, lay in enumerate(spine_ref.layers):
						if i != 17:
							spine_ref.layers[i] = False
				
					# reconnect spine tip children
				if idx == len(spine_bones_ref)-1:
					for bname in tip_children:
						child = get_edit_bone(bname)
						if child:
							print("REPARENTING", child.name, spine_ref.name)
							child.parent = spine_ref
					"""
					for _eb in bpy.context.active_object.data.edit_bones:				
						if _eb.parent == spine_ref and not "spine" in _eb.name:
							_eb.parent = None
					"""
					
					# set transforms
				spine_ref.head = spine_root_tip[0] + (spine_vec * (idx)) / (obj.rig_spine_count)
				spine_ref.tail = spine_ref.head + (spine_vec / (obj.rig_spine_count))
				
					#parent
				if idx > 0:# no parent for the root bone
					spine_ref.parent = get_edit_bone(spine_bones_ref[idx-1])
					spine_ref.use_connect = True
					
					
					
				# control bones				
				cont_name = 'c_' + ref_name.replace('_ref', '')
				spine_cont = get_edit_bone(cont_name)
				if not spine_cont:
					spine_cont = bpy.context.active_object.data.edit_bones.new(cont_name)
					spine_cont.use_deform = False
					bones_created.append(spine_cont.name)
					# set layer
					spine_cont.layers[0] = True
					for i, lay in enumerate(spine_cont.layers):
						if i != 0:
							spine_cont.layers[i] = False
				
					# set transforms
				if idx > 0:# no new transforms for the root bone
					spine_cont.head, spine_cont.tail, spine_cont.roll = spine_ref.head.copy(), spine_ref.tail.copy(), spine_ref.roll			
				
					# parent			
				if idx > 0:# no parent for the root bone
					if idx != 1:
						previous_cont_name = 'c_' + spine_bones_ref[idx-1].replace('_ref', '')						
					else:
						previous_cont_name = 'c_' + spine_bones_ref[idx-1].replace('_ref', '_master')				
					
					spine_cont.parent = get_edit_bone(previous_cont_name)		
				
				
				# deforming bones
				spine_def_name = cont_name[2:]
				spine_def = get_edit_bone(spine_def_name)
				if not spine_def:
					spine_def = bpy.context.active_object.data.edit_bones.new(spine_def_name)
					bones_created.append(spine_def_name)
					# set layer
					print("set layer", spine_def_name)
					spine_def.layers[8] = True
					for i, lay in enumerate(spine_def.layers):
						if i != 8:
							spine_def.layers[i] = False
					
					# set transforms
				if idx > 0:# no new transforms for the root bone
					spine_def.head, spine_def.tail, spine_def.roll = spine_ref.head.copy(), spine_ref.tail.copy(), spine_ref.roll			
				
					# parent
				if idx > 0:# no parent for the root bone				
					previous_cont_name = 'c_' + spine_bones_ref[idx].replace('_ref', '')			
					spine_def.parent = get_edit_bone(previous_cont_name)		
				
				
				# bend bones
				spine_bend_cont_name = cont_name.replace(str(idx), str(idx)+'_bend')
				spine_bend_cont = get_edit_bone(spine_bend_cont_name)
				if not spine_bend_cont:
					spine_bend_cont = bpy.context.active_object.data.edit_bones.new(spine_bend_cont_name)
					bones_created.append(spine_bend_cont.name)
						# set layer
					spine_bend_cont.layers[1] = True
					for i, lay in enumerate(spine_bend_cont.layers):
						if i != 1:
							spine_bend_cont.layers[i] = False						
			
				if idx > 0:
					spine_bend_cont.head = ((spine_cont.tail + spine_cont.head) * 0.5)
					spine_bend_cont.tail = spine_cont.head				
			
						#parent
				if idx > 0:# no parent for the root bone
					previous_cont_name = 'c_' + spine_bones_ref[idx].replace('_ref', '')
					spine_bend_cont.parent = get_edit_bone(previous_cont_name)	

					# add the waist bend bone if more than 1 spine bone
				if obj.rig_spine_count > 1:
					waist_bend = get_edit_bone("c_waist_bend.x")
					if not waist_bend:
						waist_bend = bpy.context.active_object.data.edit_bones.new("c_waist_bend.x")
						waist_bend.use_deform = False
						bones_created.append(waist_bend.name)
						
						# set transforms
						root_ref = get_edit_bone('root_ref.x')
						waist_bend.head = root_ref.tail
						waist_bend.tail = root_ref.tail + (root_ref.tail - root_ref.head) * 0.5
						waist_transforms = [waist_bend.head.copy(), waist_bend.tail.copy(), waist_bend.roll]
						
						# set parent
						waist_bend.parent = get_edit_bone("c_root.x")
						
						# set layer
						waist_bend.layers[1] = True
						for i, lay in enumerate(waist_bend.layers):
							if i != 1:
								waist_bend.layers[i] = False
						
						# create the waist_bend bone on the rig_add too
						rig_add = get_rig_add(bpy.context.active_object)
						if rig_add:
							edit_rig(rig_add)
							waist_bend_add_name = "c_waist_bend.x"
							waist_bend_add = get_edit_bone(waist_bend_add_name)
							if not waist_bend_add:
								waist_bend_add = bpy.context.active_object.data.edit_bones.new(waist_bend_add_name)
								waist_bend_add.head, waist_bend_add.tail, waist_bend_add.roll = waist_transforms[0], waist_transforms[1], waist_transforms[2]
								
								#set constraint
								bpy.ops.object.mode_set(mode='POSE')
								pb_waist_bend_add = get_pose_bone(waist_bend_add_name)
								cns = pb_waist_bend_add.constraints.new("COPY_TRANSFORMS")
								cns.target = bpy.data.objects[rig_name]
								cns.subtarget = waist_bend_add_name
								cns.owner_space = cns.target_space = "LOCAL"
							
							bpy.ops.object.mode_set(mode='OBJECT')
							bpy.ops.object.select_all(action='DESELECT')
							edit_rig(bpy.data.objects[rig_name])
					
				
			# Pose mode only
			bpy.ops.object.mode_set(mode='POSE')
			print(bones_created)
			for bname in bones_created:
				# set custom shapes
				if not '_ref' in bname:
					# main controls
						# custom shape
					if not '_bend' in bname:
						cs_name = 'cs_spine'
						cs = bpy.data.objects.get(cs_name)
						if not cs:
							append_from_arp(nodes=[cs_name], type='object')
							cs = bpy.data.objects.get(cs_name)
						print(bname)
						get_pose_bone(bname).custom_shape = cs	
						get_pose_bone(bname).custom_shape_scale = 0.450
					else:
						# bend controls
						cs_name = 'cs_torus_01'
						cs = bpy.data.objects.get(cs_name)
						if not cs:
							append_from_arp(nodes=[cs_name], type='object')
							cs = bpy.data.objects.get(cs_name)
						print(bname)
						get_pose_bone(bname).custom_shape = cs
						get_pose_bone(bname).custom_shape_scale = 1.2
						
				# set bone group
				get_pose_bone(bname).bone_group = bpy.context.active_object.pose.bone_groups.get('body.x')
				
				# set rotation mode
				get_pose_bone(bname).rotation_mode = 'XYZ'
				
				bpy.ops.object.mode_set(mode='EDIT')
	
	
	bpy.ops.object.mode_set(mode='EDIT')
	_set_picker_spine()
		
	
	# Set bottom bones	
	if bottom:
		bpy.ops.object.mode_set(mode='EDIT')
		root_ref = get_edit_bone("root_ref.x")
		bones_coords = {}
		
		if root_ref:
			# create bottoms			
			for side in (".l", ".r"):
				# ref bones
				bot_ref = get_edit_bone("bot_bend_ref"+side)
				if not bot_ref:
					bot_ref = bpy.context.active_object.data.edit_bones.new("bot_bend_ref"+side)
					
					# Set layers
					bot_ref.layers[17] = True
					for i, l in enumerate(bot_ref.layers):
						if i != 17:
							bot_ref.layers[i] = False
					
					root_ref = get_edit_bone("root_ref.x")		
					
					# Set transforms
					fac = 1
					if side == ".r":
						fac = -1
					bot_ref.head = root_ref.head + (-root_ref.z_axis.normalized() * (root_ref.tail-root_ref.head).magnitude) + (root_ref.x_axis.normalized() * (root_ref.tail-root_ref.head).magnitude*0.5 * fac)
					bot_ref.tail = bot_ref.head + (-root_ref.z_axis.normalized() * (root_ref.tail-root_ref.head).magnitude*0.3)				
					bot_ref.roll = 0
					
					bones_coords[bot_ref.name] = bot_ref.head.copy(), bot_ref.tail.copy(), bot_ref.roll
					
					# Set deform
					bot_ref.use_deform = False
				
				# control bones
				bot_control = get_edit_bone("c_bot_bend"+side)
				if not bot_control:
					bot_control = bpy.context.active_object.data.edit_bones.new("c_bot_bend"+side)
					
					# Set layers
					bot_control.layers[1] = True
					for i, l in enumerate(bot_control.layers):
						if i != 1:
							bot_control.layers[i] = False
							
					# Set transforms
					bot_control.head, bot_control.tail, bot_control.roll = bot_ref.head.copy(), bot_ref.tail.copy(), bot_ref.roll
					
					# Set deform
					bot_control.use_deform = False
					
					# Parent
					root_bend = get_edit_bone("c_root_bend.x")
					c_root = get_edit_bone("c_root.x")
					if root_bend:
						bot_control.parent = root_bend
					elif c_root:
						bot_control.parent = c_root 
					
				# custom shape
				bpy.ops.object.mode_set(mode='POSE')
				pb = get_pose_bone("c_bot_bend"+side)
				cs = bpy.data.objects.get("cs_torus_01")
				if cs:
					pb.custom_shape = cs
					
				# bone groups
				group_name = "body" + side
				grp = bpy.context.active_object.pose.bone_groups.get(group_name)
				if grp:
					pb.bone_group = grp
					
				bpy.ops.object.mode_set(mode='EDIT')
		else:
			print("Root bone not found, could not set the bottom bones")			
			
		# Rig_add		
		rig_add = get_rig_add(bpy.context.active_object)
		if rig_add:
			edit_rig(rig_add)
			for side in (".l", ".r"):	
				
				n = "c_bot_bend" + side
				bot_bone = get_edit_bone(n)
				if not bot_bone:
					bot_bone = bpy.context.active_object.data.edit_bones.new(n)
					bot_bone.head, bot_bone.tail, bot_bone.roll = bones_coords[bot_bone.name[2:].replace(side, '_ref'+side)]
				
					
				bpy.ops.object.mode_set(mode='POSE')
				pb_bot = get_pose_bone(n)
				cns = pb_bot.constraints.new("COPY_TRANSFORMS")
				cns.target_space = "LOCAL"
				cns.owner_space = "LOCAL"
				cns.target = bpy.data.objects[rig_name]
				cns.subtarget = n
				bpy.ops.object.mode_set(mode='EDIT')
				
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			rig_add.hide_viewport = True
			set_active_object(rig_name)
				
		print("Bottom bones created")
					
	else:
		bpy.ops.object.mode_set(mode='EDIT')	
		root_ref = get_edit_bone("root_ref.x")		
		
		
		if root_ref:
			for side in (".l", ".r"):
				print("deleting")
				# delete bottoms
				bottom_bones_ref = ["bot_bend_ref"]
				bottom_bones_control = ["c_bot_bend"]
				for b in bottom_bones_ref + bottom_bones_control:
					ebone = get_edit_bone(b+side)
					if ebone:
						bpy.context.active_object.data.edit_bones.remove(ebone)
												
				print("Bottom bones deleted")
	
		else:
			print("Root bone not found, could not set the bottom bones")	
	
		# Rig_add bones		
		rig_add = get_rig_add(bpy.data.objects[rig_name])
		if rig_add:
			edit_rig(rig_add)
			for side in (".l", ".r"):	
				n = "c_bot_bend" + side
				bot_bone = get_edit_bone(n)
				if bot_bone:
					bpy.context.active_object.data.edit_bones.remove(bot_bone)
				
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			rig_add.hide_viewport = True			
			set_active_object(rig_name)
		
		
	#restore layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = layers_select[i]	  

	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	if active_bone  and not 'spine_03' in active_bone:
		if current_mode == 'POSE':		
			bpy.context.active_object.data.bones.active = get_pose_bone(active_bone).bone	 
		   
		if current_mode == 'EDIT':		
			obj.data.edit_bones.active = get_edit_bone(active_bone)

	#restore picker 
	try:		
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state
	except:
		pass	

	return None
	

def set_facial(facial_state):

	context = bpy.context
	rig_name = bpy.context.active_object.name
	xmirror_state = bpy.context.object.data.use_mirror_x
	bpy.context.object.data.use_mirror_x = False
	
	# get the bone side
	side = ""
	"""
	print("ACTIVE OBJECT", bpy.context.active_object)
	for i in bpy.context.selected_editable_bones:
		print(i)
	"""
	if len(bpy.context.selected_editable_bones) > 0:
		b_name = bpy.context.selected_editable_bones[0].name		
		side = ".x"
		if '_dupli_' in b_name:
			side = b_name[-12:]
			side = side[:-2] + ".x"
	else:
		print("No bone selected")	
		
	#print(br)	
	head_ref = get_edit_bone("head_ref" + side)
	
	if not head_ref and facial_state:
		print("head_ref" + side, "does not exist, cannot create facial")
		return
		
	#disable the proxy picker to avoid bugs
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass
	
	#Active all layers
	# and save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):  
		layers_select.append(_layers[i])
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True 
		
	def create_facial():		
		exist_already = False
		if get_edit_bone(auto_rig_datas.facial_ref[0] + side[:-2] + ".l"):
			exist_already = True
			
		if not exist_already:		
			print("Facial does not exist, create bones...")			
			addon_directory = os.path.dirname(os.path.abspath(__file__))		
			filepath = addon_directory + "/armature_presets/modules.blend"			
			
			# make a list of current custom shapes objects in the scene for removal later
			cs_objects = [obj.name for obj in bpy.data.objects if obj.name[:3] == "cs_"]			
			
			# load the objects in the blend file datas
			with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to): 
				# only import the necessary armature
				data_to.objects = [i for i in data_from.objects if i == "rig_facial"]
									
			# link in scene
			for obj in data_to.objects:				
				context.scene.collection.objects.link(obj)
				print("Linked armature:", obj.name)
			bpy.ops.object.mode_set(mode='OBJECT')
			
			# replace custom shapes by custom shapes already existing in the scene
			set_active_object('rig_facial')			
			bpy.ops.object.mode_set(mode='POSE')			
			for b in bpy.context.active_object.pose.bones:				
				if b.custom_shape:					
					if b.custom_shape.name not in cs_objects:						
						if b.custom_shape.name.replace('.001', '') in cs_objects:
							b.custom_shape = bpy.data.objects[b.custom_shape.name.replace('.001', '')]
						
				# naming
				if "_dupli_" in side:
					# new name = eye + _dupli_001 + .l
					b.name = b.name.split('.')[0] + side[:-2] + b.name[-2:]

				# set constraints			
				if len(b.constraints) > 0:
					for cns in b.constraints:
						try:
							if cns.target == None:
								cns.target = bpy.data.objects[rig_name]							
						except:
							pass
			
			
			# replace drivers variables			
			for dr in bpy.context.active_object.animation_data.drivers:				
				if "_dupli_" in side:
					if 'pose.bones' in dr.data_path:											
						for var in dr.driver.variables:
							for tar in var.targets:			
								if not side[:-2] in tar.data_path:
									print("Replaced driver var data path", tar.data_path)											
									tar.data_path = tar.data_path.replace(side[-2:], side[:-2] + side[-2:])
									print("=>", tar.data_path)
				
				
				# find added/useless custom shapes and delete them			
				for obj in bpy.data.objects:
					if obj.name[:3] == "cs_":
						if not obj.name in cs_objects:						
							bpy.data.objects.remove(obj, do_unlink=True)			
			
			bpy.ops.object.mode_set(mode='OBJECT')			
			
			# Merge to the main armature
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object('rig_facial')
			set_active_object(rig_name)
			bpy.ops.object.mode_set(mode='OBJECT')				
			bpy.ops.object.join()
				
			# Parent lost bones
			bpy.ops.object.mode_set(mode='EDIT')	
			for bn in bpy.context.active_object.data.edit_bones:
				if len(bn.keys()) > 0:
					if "arp_parent" in bn.keys():
						parent_prop = get_edit_bone(bn["arp_parent"].split(".")[0]+side)
						if bn.parent == None and parent_prop:
							bn.parent = parent_prop
					
			# move all new facial bones near the head
			b1 = get_edit_bone(auto_rig_datas.facial_ref[0] + side[:-2] + ".l")			
			if len(b1.keys()) > 0:
				if "arp_offset_matrix" in b1.keys():
					ob_mat = bpy.context.active_object.matrix_world								
					head_ref = get_edit_bone("head_ref" + side)
					b1_local = Matrix(b1["arp_offset_matrix"]) @ ob_mat @ b1.matrix
					
					# store children bones matrix					
					children_bones = auto_rig_datas.facial_ref + auto_rig_datas.facial_bones
					#children_bones.remove(auto_rig_datas.facial_ref[0])					
					children_mat_dict = {}
					for child_name in children_bones:
						sides = []
						_name = child_name
						if _name[-2:] == ".x":
							_name = _name.replace(".x", "")
							sides.append(".x")
						else:
							sides.append(".l")
							sides.append(".r")
						
						# exception: remove the left side of the first bone, not to evaluate it twice in the transformation dict
						if child_name == auto_rig_datas.facial_ref[0]:
							sides.remove(".l")
						for side_2 in sides:							
							children_mat_dict[get_edit_bone(_name+side[:-2]+side_2)] = b1.matrix.inverted() @ get_edit_bone(_name+side[:-2]+side_2).matrix
										
					# move b1
					b1.matrix = head_ref.matrix @ b1_local										
										
					# move other bones
					for child_ in children_mat_dict:
						child_.matrix = b1.matrix @ ob_mat @ children_mat_dict[child_]				
					
					# store current bones coords copy in a new dict to avoid the multiple transform issue when bones have connected parent 
					bones_coords = {}
					for b in children_mat_dict:
						bones_coords[b] = b.head.copy(), b.tail.copy()
					
					# scale proportionally to the head bone
					scale_from_origin(ed_bone=b1, center=head_ref.head, factor=(head_ref.tail-head_ref.head).magnitude*3)
					
					for eb in bones_coords:
						scale_from_origin(ed_bone=eb, center=head_ref.head, head_coords=bones_coords[eb][0], tail_coords=bones_coords[eb][1], factor=(head_ref.tail-head_ref.head).magnitude*3)
					
		else:
			print("Facial already created")
	
	
	def delete_facial():	
		for b in auto_rig_datas.facial_ref + auto_rig_datas.facial_bones + ['c_p_head.x']:
		
			sides = []
			_name = b
			if _name[-2:] == ".x":
				_name = _name.replace(".x", "")
				sides.append(side[:-2] + ".x")
			else:
				sides.append(side[:-2] + ".l")
				sides.append(side[:-2] + ".r")
				
			for side_2 in sides:				
				bo = get_edit_bone(_name + side_2)
				if bo:
					bpy.context.active_object.data.edit_bones.remove(bo)
					
		print("Facial bones deleted.")			
		
			
		bpy.ops.object.mode_set(mode='OBJECT')
		clean_drivers()
		bpy.ops.object.mode_set(mode='EDIT')

		
	if facial_state:
		create_facial()
	else:		
		delete_facial()
		
	# Restore layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = layers_select[i]		
	
	bpy.context.object.data.use_mirror_x = xmirror_state
	
	#restore picker 
	try:		
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state
	except:
		pass	
		

def scale_from_origin(ed_bone=None, head_coords=None, tail_coords=None, center=None, factor=None):
	if head_coords == None and tail_coords == None:
		head_coords = ed_bone.head
		tail_coords = ed_bone.tail
		
	ed_bone.head = center + ((head_coords - center) * factor)
	ed_bone.tail = center + ((tail_coords - center) * factor)					
						
						
def set_ears(ears_amount, side_arg=None, offset_arg=None):
	
	
	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')
	
	# save X-Mirror state
	xmirror_state = bpy.context.object.data.use_mirror_x
	bpy.context.object.data.use_mirror_x = False	
	
	offset_translation = 0
	if offset_arg:
		offset_translation = offset_arg * 0.5
		
	
	sides = ['.l', '.r']
	
	# if the side is set, operate on the given ear sides only
	if side_arg:
		sides = [side_arg[:-2] + ".l", side_arg[:-2] + ".r"]		
		
	# else, get selected ears side
	else:
		if len(bpy.context.selected_editable_bones) > 0:
			b_name = bpy.context.selected_editable_bones[0].name
			# only if it's a ref bone
			if len(b_name.split('_')) >= 3:
				if b_name.split('_')[2][:3] == 'ref' and b_name.split('_')[0] == 'ear':
					sides = [b_name[-2:]]
					if '_dupli' in b_name:
						sides = [b_name[-12:]]						
						#sides = [dupli[:-2] + ".l", dupli[:-2] + ".r"]
				else:
					print("No reference ear bone selected:", b_name)
		else:
			print("No bone selected")
	
	
	#print("ear sides", sides)
	
	# First delete all ears bones
	start_end_pos = [Vector((0,0,0)), Vector((0,0,0))]
	ear_parent_name = None
	
	for i in range(0, 16):
		for side in sides:
			ref_bone = get_edit_bone('ear_' + '%02d' % (i+1)  + '_ref' + side)
			if ref_bone:			
				# save the start pos (first bone head position)
				if i == 0:
					start_end_pos[0] = ref_bone.head.copy()
					
					if ref_bone.parent:
						ear_parent_name = ref_bone.parent.name
					
				# save the end pos (last bone head position)
				start_end_pos[1] = ref_bone.tail.copy()				
			
				bpy.context.active_object.data.edit_bones.remove(ref_bone)			
				
			control_bone = get_edit_bone('c_ear_' + '%02d' % (i+1)	+ side)
			if control_bone:					
				bpy.context.active_object.data.edit_bones.remove(control_bone)				
				
				
			# proxy bones			
			switch_bone_layer('c_ear_' + '%02d' % (i+1)	 + '_proxy' + side, 0, 22, False)
	
	ear_vec = start_end_pos[1] - start_end_pos[0]
	
	# If ears enabled, create bones
	if ears_amount > 0:		
		assign_to_group = []
		for i in range(0, ears_amount):
			
			for side in sides:
				# ref bones
				ref_bone_name = 'ear_' + '%02d' % (i+1)	 + '_ref' + side
				ref_bone = get_edit_bone(ref_bone_name)
				
				if ref_bone == None:				
					ref_bone = bpy.context.active_object.data.edit_bones.new(ref_bone_name)
					assign_to_group.append(ref_bone.name)
				
				ref_bone.use_deform = False
				head_bone = get_edit_bone('head_ref.x')
				ref_bone['arp_duplicate'] = 1
				
				fac = 1
				if side[-2:] == ".r":
					fac = -1
					
				# if a previous bone chain exists, match the new bones positions with this one
				if ear_vec.magnitude != 0.0:									
					ref_bone.head = start_end_pos[0] + (ear_vec * (i)) / ears_amount
					ref_bone.tail = ref_bone.head + (ear_vec / ears_amount)
			
					
				# otherwise, use other default locations
				elif head_bone:
					ref_bone.head = ((head_bone.tail + head_bone.head) * 0.5) + (head_bone.x_axis.normalized() * head_bone.length * 0.2) * fac * (i+2)					
					ref_bone.tail = ((head_bone.tail + head_bone.head) * 0.5) + (head_bone.x_axis.normalized() * head_bone.length * 0.2) * fac * (i+3)
					
				else:
					ref_bone.head = Vector((0.1 * (i+1) * fac, 0, 0))
					ref_bone.tail = Vector((0.1 * (i+2) * fac, 0, 0))
				
				ref_bone.head += Vector((offset_translation, 0, 0))
				ref_bone.tail += Vector((offset_translation, 0, 0))
				
				# parent
				if i == 0:
					# parent by default the first bone to the head bone, if not already set					
					if not ear_parent_name:
						if head_bone:
							ref_bone.parent = head_bone 
							#print('1.parented ear bone to', head_bone.name)
					else:
						ref_bone.parent = get_edit_bone(ear_parent_name)
						#print('2.parented ear bone to', ear_parent_name)
				else:
					ref_bone.parent = get_edit_bone('ear_' + '%02d' % (i)  + '_ref' + side)
					#print('3.parented ear bone to', get_edit_bone('ear_' + '%02d' % (i)  + '_ref' + side))
				# control bones
				cont_bone_name = 'c_ear_' + '%02d' % (i+1)	+ side
				cont_bone = get_edit_bone(cont_bone_name)
				
				if cont_bone == None:				
					cont_bone = bpy.context.active_object.data.edit_bones.new(cont_bone_name)
					assign_to_group.append(cont_bone.name)
					
				cont_bone.head, cont_bone.tail, cont_bone.roll = ref_bone.head, ref_bone.tail, ref_bone.roll	

				# parent
				if get_edit_bone('c_ear_' + '%02d' % (i)  + side):
					cont_bone.parent = get_edit_bone('c_ear_' + '%02d' % (i) + side)
				
				# proxy bones		
				switch_bone_layer('c_ear_' + '%02d' % (i+1)	 + '_proxy' + side, 22, 0, False)				
				
				# Set display parameters
				bpy.ops.object.mode_set(mode='POSE')
				
				for j in assign_to_group:			
					pbone = get_pose_bone(j)					
					
					# bone group					
					grp_name = 'body' + j[-2:]
					if bpy.context.active_object.pose.bone_groups.get(grp_name):
						pbone.bone_group = bpy.context.active_object.pose.bone_groups[grp_name]
					
					# custom shape
					if not "_ref" in j:						
						cs_name = 'cs_torus_03'
						if bpy.data.objects.get(cs_name) == None:
							append_from_arp(nodes=[cs_name], type="object")
							
						pbone.custom_shape = bpy.data.objects[cs_name]	
						pbone.custom_shape_scale = 1.0
						get_data_bone(pbone.name).show_wire = True				
						
						
					# Set layers				
					if not "_ref" in j:					
						# controller		
						get_data_bone(j).layers[0] = True
						for idx, lay in enumerate(get_data_bone(j).layers):
							if idx != 0 and idx != 31:
								get_data_bone(j).layers[idx] = False
							else:
								get_data_bone(j).layers[idx] = True					
						
						# reference
					else:		
						get_data_bone(j).layers[17] = True
						for idx, lay in enumerate(get_data_bone(j).layers):
							if idx != 17:
								get_data_bone(j).layers[idx] = False
								
				bpy.ops.object.mode_set(mode='EDIT')
	
	# restore X-Mirror state
	bpy.context.object.data.use_mirror_x = xmirror_state
	
	# restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	
	
def update_facial(self, context):

	
	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')
	obj = bpy.context.active_object 
		
	# Check for head bone display override
	facial_display = True
	
	if get_edit_bone('head_ref.x'):
		if is_facial_enabled(obj) and get_edit_bone('head_ref.x').layers[17] == True:#display only if the head is not already disabled
			facial_display = True
		else:
			facial_display = False
 
	# Ref bones
	facial_ref = auto_rig_datas.facial_ref
   
	for bone_ref in facial_ref:			 
		#facial disabled   
		if not facial_display:					  
			# ref bones			
			switch_bone_layer(bone_ref, 17, 22, True)
			
		# facial enabled
		else:		
			switch_bone_layer(bone_ref, 22, 17, True)
		

	   
	# Control and Deform bones
	facial_deform =auto_rig_datas.facial_deform
	facial_control = auto_rig_datas.facial_control
	
	sides = [".l", ".r"]
	
	for bone in facial_deform:
		if not facial_display:#disabled 
			try: 
				switch_bone_layer(bone, 31, 22, True)
				
				for side in sides:				
					suff = side
					if bone[-2:] == ".x":
						suff = ""						
					get_edit_bone(bone + suff).use_deform = False
			except:
				pass
		else:#enabled	  
			try:
				switch_bone_layer(bone, 22, 31, True)
			
				for side in sides:
					suff = side
					if bone[-2:] == ".x":
						suff = ""
					get_edit_bone(bone + suff).use_deform = True
			except:
				pass
				

	
	for bone in facial_control:
	
		side = ".l"
		if bone[-2:] == ".x":
			side = ""
		
		if get_edit_bone(bone + side):
			src_layer = get_edit_bone(bone + side)['arp_layer']
			
			if not facial_display:#disabled					
				switch_bone_layer(bone, src_layer, 22, True)			
				#proxy			
				switch_bone_layer(bone.replace('.', '_proxy.'), src_layer, 22, True) 
				
			else:#enabled			
				switch_bone_layer(bone, 22, src_layer, True)		
				#proxy			
				switch_bone_layer(bone.replace('.', '_proxy.'), 22, src_layer, True)
		
	

				
	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	return None

def is_object_arp(object):
	if object:
		if object.type == 'ARMATURE':
			if get_pose_bone('c_pos'):
				return True
				
	return False
	
def get_arp_type(object):
	if len(object.data.keys()) > 0:
		if "arp_rig_type" in object.data.keys():			
			return object.data["arp_rig_type"]
				
			
# END FUNCTIONS


###########	 UI PANEL  ###################


class ARP_PT_auto_rig_pro_panel(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "ARP" 
	bl_label = "Auto-Rig Pro"
	bl_idname = "id_auto_rig"


	def draw(self, context):
		
		object = context.active_object		
		selected_objects = context.selected_objects
		prop_type = None
		scene = context.scene
		
		rig_is_selected = is_object_arp(object)
		
		layout = self.layout.column(align=True) 
		
		if rig_is_selected:
			prop_type = get_arp_type(object)
			if len(object.data.keys()) > 0:
				update_required = False
				if not "arp_updated" in object.data.keys():	
					update_required = True
				elif object.data["arp_updated"] != '3.41.18':
					update_required = True
				if update_required:	
					layout.operator("arp.update_armature_clicked", text="UPDATE REQUIRED!", icon="ERROR")
					layout.separator()
		
		
		#BUTTONS		
		layout.row().prop(scene, "arp_active_tab", expand=True)
		layout.separator()
		
		if scene.arp_active_tab == 'CREATE':
		
			col = layout.column(align=False)   
			row = col.row(align=True)
			row.operator_menu_enum("arp.append_arp", 'rig_presets', text = "Add Armature")#, icon = 'OUTLINER_OB_ARMATURE') 
			row.operator("arp.delete_arp", text="", icon='PANEL_CLOSE')
			
			col = layout.column(align=True)
			if object:				
				
				col.enabled = rig_is_selected
				
				col.separator()
				col.label(text="Rig Definition:")
				col.prop(object, "rig_type", text="", expand=False)				
				
				col = layout.column(align=True)
				
				# normal mode display
				if prop_type != "free":
				
					col.enabled = object.spine_disabled == False and rig_is_selected				
					#col.prop(object, 'rig_spine_count', text='Spine')
					
					
					col = layout.column(align=True)				
					col.enabled = rig_is_selected					   
					
					col.separator()
												
					row = layout.column(align=True).row(align=True)					
					row.enabled = rig_is_selected
					
			
				layout.separator()
				row = layout.row()				
				row.enabled = rig_is_selected						
					
				
				row.prop(scene, "arp_init_scale")
				layout.separator()
				layout.label(text="Secondary Controllers:")
				row = layout.row()
				row.prop(object, "arp_secondary_type", text="", icon='CURVE_NCURVE')
				
				layout.separator()
				layout.separator()
				col = layout.column(align=True)			
				col.enabled = rig_is_selected				
				col.operator_menu_enum('arp.add_limb', 'limbs', text='Add Limb', icon = 'PLUS')
				col.separator()
				layout.operator("arp.edit_ref", text="Edit Reference Bones", icon='EDITMODE_HLT')				
				layout.operator('arp.show_limb_params', text='Limb Options', icon = 'SETTINGS')
				row = layout.row(align=True)	   
				row.operator('arp.dupli_limb', text='Duplicate')		 
				row.operator('arp.disable_limb', text='Disable')
				
				#if prop_type != "free":
				#	layout.operator("arp.enable_all_limbs", text="Enable All")
					
				row = layout.row(align=True)
				row.operator('arp.import_ref', text='Import')
				row.operator('arp.export_ref', text='Export')		  
				layout.operator("arp.match_to_rig", text="Match to Rig", icon = 'POSE_HLT')				   
					 
				layout.separator()
				row = layout.row(align=True)
				if bpy.context.mode != 'EDIT_MESH':
					row.operator("arp.edit_custom_shape", text="Edit Shape...")#, icon="MESH_DATA") 
					row.operator("arp.mirror_custom_shape", text="", icon="MOD_MIRROR") 
				else:			 
					layout.operator("arp.exit_edit_shape", text="Apply Shape")

				layout.separator()
				row = layout.row(align=True)				
				row.operator("arp.add_fist_ctrl", text="Add Hand Fist")#, icon_value=arp_custom_icons["fist"].icon_id)#, icon="PLUS") 
				row.operator("arp.remove_fist_ctrl", text="", icon='PANEL_CLOSE')
				
				if bpy.context.scene.arp_debug_mode:
					layout.separator()
					layout.label(text="Developer tools:", icon="ERROR")
					col = layout.column(align=True)
					col.operator("arp.export_limbs", text="Export Limbs")
					col.operator("arp.export_data", text="Export Data")
			
		if scene.arp_active_tab == 'BIND':
			
			layout.label(text="Mesh Binding:")
			row = layout.column(align=True).row(align=True)
			row.prop(scene, "arp_bind_split", text="Split Parts")
			
			row1 = row.row()
			
			if object:
				if is_facial_enabled(object) or object.rig_type == 'quadruped':
					row1.enabled = False
			else:
				row1.enabled = True
			
			row1.prop(scene, "arp_bind_chin", text="Use Chin")
			
			col = layout.column()
			col.prop(scene, "arp_optimize_highres", text="Optimize High Res")
			col = layout.column()			
			col.enabled = scene.arp_optimize_highres
			col.prop(scene, "arp_highres_threshold", text="Polycount Threshold")
			
			layout.separator()
			row = layout.column(align=False).row(align=True)		
			
			row.operator("arp.bind_to_rig", text="Bind")
			row.operator("arp.unbind_to_rig", text="Unbind")
		
			layout.separator()
			
			#Shape Key Driver Tool	
			layout.label(text="Shapekeys Driver Tools:")		  
			active_armature = ""
			
			if len(context.selected_objects) > 0:
				if context.selected_objects[0].type == 'ARMATURE':			 
					active_armature = context.selected_objects[0].data.name
				else:
					if len(context.selected_objects) > 1:
						if context.selected_objects[1].type == 'ARMATURE':
							active_armature = context.selected_objects[1].data.name
					
			
			
			row = layout.row(align=True)			
			
			if context.active_object:
				if object.type == 'ARMATURE':
					row.enabled = True
			else:
				row.enabled = False
				
			if active_armature != "":
				row.prop_search(context.scene, "arp_driver_bone", bpy.data.armatures[active_armature], "bones", text="")
			row.operator("arp.pick_bone", text="", icon='EYEDROPPER')
			col = layout.column(align=True)			
			col.enabled = (active_armature != "")
			
			col.prop(scene, "arp_driver_transform", text = "")
			col = layout.column(align=True)
			
			col.enabled = (len(selected_objects) == 2)
			
			col.operator("arp.create_driver", text="Create Driver")	 
			
			row = layout.row(align=True)
			btn = row.operator('arp.set_shape_key_driver', text='0')
			btn.value = '0'
			btn = row.operator('arp.set_shape_key_driver', text='1')
			btn.value = '1'
			btn = row.operator('arp.set_shape_key_driver', text='Reset')
			btn.value = 'reset'
			
			layout.separator()			
			
			
		
		if scene.arp_active_tab == 'TOOLS':
			layout.separator()
		
			layout.operator("arp.update_armature_clicked", text="Update Armature")
			
			layout.separator()
			
			layout.label(text="Picker Panel:")
			col = layout.column(align=True)			
			row = col.row(align=True)			
			row.operator("arp.add_picker", text="Add Picker")#, icon = 'PLUS')
			row.operator("arp.remove_picker", text="", icon = 'PANEL_CLOSE')			
			row = col.row(align=True)
			row.operator("arp.import_picker", text="Import")
			row.operator("arp.export_picker", text="Export")
			col.operator("arp.set_picker_camera", text="Set Picker Cam")#, icon = 'CAMERA_DATA')
			
			row = col.row(align=True)
			row.operator("arp.screenshot_head_picker", text="Capture Facial")#, icon='RENDER_STILL')
			row = col.row(align=True)
			if len(context.scene.keys()) > 0:
				proxy_picker_found = True
				try:
					context.scene.Proxy_Picker.active
				except:
					proxy_picker_found = False
					
				if proxy_picker_found:
					if context.scene.Proxy_Picker.active:
						btn = row.operator("arp.move_picker_layout", text="Edit Layout...")
						btn.state = 'start'
					else:
						btn = row.operator("arp.move_picker_layout", text="Apply Layout")
						btn.state = 'end'
						
			row = col.row(align=True)
			row.operator("arp.mirror_picker", text="Mirror")#icon = 'MOD_MIRROR'
			
			layout.separator()
			
			
			layout.label(text='Color Theme:')#, icon='COLOR')
			row = layout.row(align=True)
			row.prop(scene, "color_set_right",text="")
			row.prop(scene, "color_set_middle",text="")
			row.prop(scene, "color_set_left",text="")
			row = layout.row(align=True)
			row.prop(scene, "color_set_panel",text="")
			row.prop(scene, "color_set_text",text="")
			row = layout.row(align=True)
			row.operator("arp.assign_colors", text="Assign")
			row = layout.row(align=True)
			row.operator("arp.import_colors", text="Import")
			row.operator("arp.export_colors", text="Export")
			
			layout.separator()	
			
		
			
###########	 REGISTER  ##################

arp_custom_icons = None

classes = (ARP_OT_report_message, ARP_OT_show_limb_params, ARP_OT_export_limbs, ARP_OT_export_data, ARP_OT_remove_picker, ARP_OT_add_picker, ARP_OT_import_picker, ARP_OT_export_picker, ARP_OT_add_fist_ctrl, ARP_OT_remove_fist_ctrl, ARP_OT_mirror_picker, ARP_OT_move_picker_layout, ARP_OT_screenshot_head_picker, ARP_OT_assign_colors, ARP_OT_clean_skin, ARP_OT_delete_arp, ARP_OT_append_arp, ARP_OT_exit_edit_shape, ARP_OT_edit_custom_shape, ARP_OT_mirror_custom_shape, ARP_OT_import_colors, ARP_OT_export_colors, ARP_OT_export_ref, ARP_OT_import_ref, ARP_OT_disable_limb, ARP_OT_update_armature_clicked, ARP_OT_update_armature_dialog, ARP_OT_update_armature_operator, ARP_OT_set_shape_key_driver, ARP_OT_pick_bone, ARP_OT_create_driver, ARP_OT_set_picker_camera, ARP_OT_bind_to_rig, ARP_OT_unbind_to_rig, ARP_OT_edit_ref, ARP_OT_add_limb, ARP_OT_dupli_limb, ARP_OT_match_to_rig, ARP_PT_auto_rig_pro_panel)

def register():	 
	from bpy.utils import register_class

	for cls in classes:
		register_class(cls)
	
	# custom icons
	global arp_custom_icons
	arp_custom_icons = bpy.utils.previews.new()	   
	icons_dir = os.path.join(os.path.dirname(__file__), "icons")
	arp_custom_icons.load("fist", os.path.join(icons_dir, "fist.png"), 'IMAGE')
	
	
	bpy.types.Object.rig_type = bpy.props.EnumProperty(items=(('biped', 'Biped', 'Biped Rig Type, vertical spine orientation'), ('quadruped', 'Multi-Ped', 'Multi-Ped rig type, free spine orientation')), name = "Rig Type", description="Rig type to define the spine controllers orientation")	
	bpy.types.Object.rig_fingers_rot = bpy.props.EnumProperty(items=(('scale_2_phalanges', 'Rot from Scale: 2', 'The mid and tip phalanges rotation are driven by the scale of the first one'), ('scale_3_phalanges', 'Rot from Scale: 3', 'All phalanges rotation are driven by the scale of the first one'), ('no_scale', 'Disabled', 'Phalanges rotations are not driven by the scale of the first one')), name="Fingers Rotation", description = "Automatic rotation of the fingers phalanges based on the scale of the first phalange")	
	bpy.types.Object.arp_secondary_type = bpy.props.EnumProperty(items = (('additive', 'Additive (Exportable)', 'Additive mode (default) for the secondary deformations used to curve the arms and legs.\nExportable to FBX'), ('bendy_bones', 'Bendy Bones', 'Bendy bones for the secondary deformations used to curve the arms and legs.\nGood for very stretchy/cartoony characters.\nWarning, the secondary controllers and twist bones will not be exportable to FBX (Advanced option)')), name = "Secondary Deformations", description = "Deformation mode for the secondary and twist bones of the arms and legs. Applied after Match to Rig.")	
	bpy.types.Object.arp_fingers_shape_style = bpy.props.EnumProperty(items=(('circle', 'Circle', 'Set circle shapes', 'MESH_CIRCLE', 1), ('box', 'Box', 'Set box shapes', 'MESH_CUBE', 2)), name="Finger Shapes", description="Default shapes of the fingers controllers, if not already edited\nApplied after Match to Rig")	
	bpy.types.Object.spine_disabled = bpy.props.BoolProperty(default=False) 
	bpy.types.Scene.arp_init_scale = bpy.props.BoolProperty(name="Init Scale", default=True, description="Initialize the armature scale (1) after Match to Rig")	
	bpy.types.Object.rig_spine_count = bpy.props.IntProperty(default=3, min=1, max=4, description='Number of spine bones')	
	bpy.types.Object.rig_tail_count = bpy.props.IntProperty(default=4, min=1, max=32, description='Number of tail bones')	
	bpy.types.Scene.arp_driver_bone = bpy.props.StringProperty(name="Bone Name", description="Bone driving the shape key")
	bpy.types.Scene.arp_driver_transform = bpy.props.EnumProperty(items=(('LOC_X', 'Loc X', 'X Location'),('LOC_Y', 'Loc Y', 'Y Location'), ('LOC_Z', 'Loc Z', 'Z Location'), ('ROT_X', 'Rot X', 'X Rotation'), ('ROT_Y', 'Rot Y', 'Y Rotation'), ('ROT_Z', 'Rot Z', 'Z Rotation'), ('SCALE_X', 'Scale X', 'X Scale'), ('SCALE_Y', 'Scale Y', 'Y Scale'), ('SCALE_Z', 'Scale Z', 'Z Scale')), name = "Bone Transform")
	bpy.types.Scene.arp_highres_threshold = bpy.props.IntProperty(name="High Res Threshold", description = "Meshes with polycount higher than this will be considered as high resolution meshes to optimize binding performances", default = 70000)
	bpy.types.Scene.arp_optimize_highres = bpy.props.BoolProperty(name="Optimize High Resolution Meshes", description = "Speed up binding time of high resolution meshes", default = False) 
	bpy.types.Scene.arp_bind_split = bpy.props.BoolProperty(default=True, description="Improve skinning by separating the loose parts (e.g: hats, buttons, belt...) before binding.\nWarning: meshes with a lot of separate pieces can take several minutes to bind.")
	bpy.types.Scene.arp_bind_chin = bpy.props.BoolProperty(default=False, description="Improve head skinning based on the chin (reference jawbone tail) position.\nOnly when facial is disabled, and biped type.")
	bpy.types.Scene.arp_active_tab = bpy.props.EnumProperty(items=(('CREATE', 'Rig', 'Create Tab'),('BIND', 'Skin', 'Bind Tab'), ('TOOLS', 'Misc', 'Misc Tab')))	
	bpy.types.Scene.color_set_right = bpy.props.FloatVectorProperty(name="Color Right", subtype="COLOR_GAMMA", default=(0.602,0.667,1.0), min=0.0, max=1.0, description="Right controllers color")
	bpy.types.Scene.color_set_middle = bpy.props.FloatVectorProperty(name="Color Middle", subtype="COLOR_GAMMA", default=(0.205,0.860,0.860), min=0.0, max=1.0, description="Middle controllers color")
	bpy.types.Scene.color_set_left = bpy.props.FloatVectorProperty(name="Color Left", subtype="COLOR_GAMMA", default=(0.8,0.432,0.0), min=0.0, max=1.0, description="Left controllers color")
	bpy.types.Scene.color_set_panel = bpy.props.FloatVectorProperty(name="Color Panel", subtype="COLOR_GAMMA", default=(0.2,0.2,0.2), min=0.0, max=1.0, description="Back picker panel color")
	bpy.types.Scene.color_set_text = bpy.props.FloatVectorProperty(name="Color Text", subtype="COLOR_GAMMA", default=(0.887,0.887,0.887), min=0.0, max=1.0, description="Text color in the picker panel")
	
	

	
def unregister(): 
	from bpy.utils import unregister_class
	
	for cls in reversed(classes):
		unregister_class(cls)	

	#custom icons
	global arp_custom_icons
	bpy.utils.previews.remove(arp_custom_icons)

	del bpy.types.Object.rig_type	
	del bpy.types.Object.rig_fingers_rot
	del bpy.types.Object.arp_secondary_type
	del bpy.types.Object.arp_fingers_shape_style	
	del bpy.types.Object.spine_disabled		
	del bpy.types.Scene.arp_init_scale
	del bpy.types.Object.rig_spine_count
	del bpy.types.Object.rig_tail_count 
	del bpy.types.Scene.arp_driver_bone
	del bpy.types.Scene.arp_driver_transform
	del bpy.types.Scene.arp_optimize_highres 
	del bpy.types.Scene.arp_highres_threshold	
	del bpy.types.Scene.arp_bind_split
	del bpy.types.Scene.arp_bind_chin
	del bpy.types.Scene.arp_active_tab	
	del bpy.types.Scene.color_set_right
	del bpy.types.Scene.color_set_middle
	del bpy.types.Scene.color_set_left
	del bpy.types.Scene.color_set_panel
	del bpy.types.Scene.color_set_text
		