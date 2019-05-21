bl_info = {
	"name": "Auto-Rig Pro",
	"author": "Artell",
	"version": (0, 1),
	"blender": (2, 7, 5),
	"location": "3D View > Properties> Auto-Rig Pro",
	"description": "Automatic rig generation based on reference bones",		
	"category": "Learnbgame"
}	


import bpy, bmesh, mathutils, math, bpy_extras, ast, os
from . import auto_rig_datas, auto_rig_reset
from mathutils import Vector
print("\n Starting Auto-Rig Pro...\n")

blender_version = bpy.app.version_string
print('Blender version: ', blender_version)

debug_print = False

 ##########################	 CLASSES  ##########################
 

class mirror_picker(bpy.types.Operator):
	  
	#tooltip
	""" Mirror the selected picker bone(s) transforms"""
	
	bl_idname = "id.mirror_picker"
	bl_label = "mirror_picker"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if is_object_arp(context.object):
				if len(context.scene.keys()) > 0:
					if 'Proxy_Picker' in context.scene.keys():
						if not context.scene.Proxy_Picker.active:
							return True
				  
				
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False		 
			   
		try:		   
			_mirror_picker()
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 

class move_picker_layout(bpy.types.Operator):
	  
	#tooltip
	""" Edit the picker layout, buttons and text position. The picker selection will be disabled.\nClick Apply Layout to complete and enable again the picker selection"""
	
	bl_idname = "id.move_picker_layout"
	bl_label = "move_picker_layout"	
	
	state = bpy.props.StringProperty("")
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if is_object_arp(context.object):
				return True
				
	def execute(self, context):			   
			   
		_move_picker_layout(self.state)
	   
		return {'FINISHED'} 


 

class screenshot_head_picker(bpy.types.Operator):
	  
	#tooltip
	""" Capture the current view as the facial picker background image """
	
	bl_idname = "id.screenshot_head_picker"
	bl_label = "Save .PNG"	
	
	
			  
	filepath = bpy.props.StringProperty(subtype="DIR_PATH", default='')
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if is_object_arp(context.object):
				return True
				
	def execute(self, context):			   
		_screenshot_head_picker(self.filepath)		   
		return {'FINISHED'}		
	

	def invoke(self, context, event):
		self.filepath = 'picker_bg_face.png'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	
		
 
class assign_colors(bpy.types.Operator):
	  
	#tooltip
	""" Assign the colors """
	
	bl_idname = "id.assign_colors"
	bl_label = "assign_colors"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if is_object_arp(context.object):
				return True
				  
				
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False		 
			   
		try:		   
			_assign_colors()
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
		
class clean_skin(bpy.types.Operator):
	  
	#tooltip
	""" Clean weight groups	 """
	
	bl_idname = "id.clean_skin"
	bl_label = "clean_skin"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):	
		if context.object != None:
			if context.object.type == 'MESH':
				return True
	
				  
				
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False		 
			   
		try:		   
			_clean_skin()
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
		
		
class delete_arp(bpy.types.Operator):
	  
	#tooltip
	""" Delete the Auto-Rig Pro armature """
	
	bl_idname = "id.delete_arp"
	bl_label = "delete_arp"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		if bpy.data.objects.get('rig')!= None:
			if bpy.data.objects['rig'].type == 'ARMATURE':		
				return True
	
				  
				
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False		 
			   
		try:		   
			_delete_arp()
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}	 
 
 
class append_arp(bpy.types.Operator):
	  
	#tooltip
	""" Add the Auto-Rig Pro armature in the scene. Only compatible with Blender 2.79 and above, \nappend by hand (Shift-F1) otherwise."""
	
	bl_idname = "id.append_arp"
	bl_label = "append_arp"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		if not ('2.78' in blender_version) or ('2.78' in blender_version and 'sub 5' in blender_version or 'sub 6' in blender_version):
			if bpy.data.objects.get('rig') == None:				
				return True
	
				  
				
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False		 
			   
		try:		   
			_append_arp()
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
 

class exit_edit_shape(bpy.types.Operator):
	  
	#tooltip
	""" Edit the selected bone shape  """
	
	bl_idname = "id.exit_edit_shape"
	bl_label = "exit_edit_shape"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if context.mode == 'EDIT_MESH':	 
				if 'cs_user' in context.object.name:
					return True
				  
				
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False		 
			   
		try:		   
			_exit_edit_shape()
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
 
 
class edit_custom_shape(bpy.types.Operator):
	  
	#tooltip
	""" Edit the selected bone shape  """
	
	bl_idname = "id.edit_custom_shape"
	bl_label = "edit_custom_shape"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'POSE':
			if bpy.context.active_pose_bone != None:
				if 'c_' in bpy.context.active_pose_bone.name:
					return True
				  
				
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False		 
			   
		try:		   
			_edit_custom_shape()
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
		
class mirror_custom_shape(bpy.types.Operator):
	  
	#tooltip
	""" Mirror the selected bone shape to the other side """
	
	bl_idname = "id.mirror_custom_shape"
	bl_label = "mirror_custom_shape"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'POSE':
			if bpy.context.active_pose_bone != None:
				if 'c_' in bpy.context.active_pose_bone.name:
					return True
				  
				
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False		 
			   
		try:		   
			_mirror_custom_shape()
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
		
class import_colors(bpy.types.Operator):
	""" Import the color set """
	bl_idname = "id.import_colors"
	bl_label = "import_colors"

	filepath = bpy.props.StringProperty(subtype="FILE_PATH", default='py')


	def execute(self, context):		   
		_import_colors(self.filepath)
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = 'color_set.py'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
 
class export_colors(bpy.types.Operator):
	""" Export the color set """
	bl_idname = "id.export_colors"
	bl_label = "export_colors"

	filepath = bpy.props.StringProperty(subtype="FILE_PATH", default='py')
	

	def execute(self, context):		   
		_export_colors(self.filepath)
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = 'color_set.py'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class export_ref(bpy.types.Operator):
	""" Export the reference bones transforms data """
	bl_idname = "id.export_ref"
	bl_label = "Export Ref Bones"

	filepath = bpy.props.StringProperty(subtype="FILE_PATH", default='py')
	
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
		
class import_ref(bpy.types.Operator):
	""" Import the reference bones transform datas """
	bl_idname = "id.import_ref"
	bl_label = "Import Ref Bones"

	filepath = bpy.props.StringProperty(subtype="FILE_PATH", default='py')
	
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


 
 
class enable_all_limbs(bpy.types.Operator):
	  
	#tooltip
	""" Restore all disabled limbs (except duplicate limbs) """
	
	bl_idname = "id.enable_all_limbs"
	bl_label = "enable_all_limbs"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'EDIT_ARMATURE':			 
			return True
				  
				
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
			   
		try:		   
			_enable_all_limbs(self, context)
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'} 
 
class disable_limb(bpy.types.Operator):
	  
	#tooltip
	""" Exclude the selected limb from the rig """
	
	bl_idname = "id.disable_limb"
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
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
			   
		try:		   
			_disable_limb(self, context)
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}

 
class update_armature(bpy.types.Operator):
	"""Update the armature from previous 3.14 versions"""

	bl_idname = "id.update_armature"
	bl_label = "update_armature"
	bl_options = {'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if is_object_arp(context.object):
				return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
		print('Updating Armature...')		
		
		try:	
			
			_update_armature(self)
			
			
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'} 
 
class set_shape_key_driver(bpy.types.Operator):
	  
	#tooltip
	""" Add a keyframe point on the selected shape key driver curve (0 or 1) according the bone transform value"""
	
	bl_idname = "id.set_shape_key_driver"
	bl_label = "set_shape_key_driver"
	bl_options = {'UNDO'}	
	
	value = bpy.props.StringProperty(name="Driver Value")
	
	@classmethod
	def poll(cls, context):		  
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
		if context.object.type != 'MESH':	   
			self.report({'ERROR'}, "Select the mesh and the shape key")
			return{'FINISHED'}
		
		try:		   
			_set_shape_key_driver(self, self.value)		
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
 
class pick_bone(bpy.types.Operator):
	  
	#tooltip
	""" Get the selected bone """
	
	bl_idname = "id.pick_bone"
	bl_label = "pick_bone"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):		  
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
		if context.object.type != 'ARMATURE':	   
			self.report({'ERROR'}, "First select a bone to pick it.")
			return{'FINISHED'}
		
		try:		   
			_pick_bone()		
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
 
class create_driver(bpy.types.Operator):
	  
	#tooltip
	""" Create a driver for the selected shape key using the Bone name and Bone transform parameter. Select first the armature then the mesh object. """
	
	bl_idname = "id.create_driver"
	bl_label = "create_driver"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:		   
			_create_driver()		
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
 
class set_picker_camera(bpy.types.Operator):
	  
	#tooltip
	""" Display the bone picker in this active view"""
	
	bl_idname = "id.set_picker_camera"
	bl_label = "set_picker_camera"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if is_object_arp(context.object):
				return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:		   
			_set_picker_camera()		
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
 
class bind_to_rig(bpy.types.Operator):
	  
	#tooltip
	""" Select first the mesh(es), then the armature and click it to bind"""
	
	bl_idname = "id.bind_to_rig"
	bl_label = "bind_to_rig"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):		
		if context.object != None:
			if is_object_arp(context.active_object):
				return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			#simplify			
			simplify_value = bpy.context.scene.render.use_simplify
			simplify_subd = bpy.context.scene.render.simplify_subdivision
			bpy.context.scene.render.use_simplify = True
			bpy.context.scene.render.simplify_subdivision = 0
			
			#operate
			active_obj = context.active_object
			_unbind_to_rig()#unbind first if it has been binded already
			set_active_object(active_obj.name)
			_bind_to_rig(self, context)		

			#restore simplify
			bpy.context.scene.render.use_simplify = simplify_value
			bpy.context.scene.render.simplify_subdivision = simplify_subd
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
class unbind_to_rig(bpy.types.Operator):
	  
	#tooltip
	""" Unbind the selected mesh from the rig"""
	
	bl_idname = "id.unbind_to_rig"
	bl_label = "unbind_to_rig"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):	
		if context.object != None:
			if context.object.type == 'MESH':
				return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			
			_unbind_to_rig()		
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}


class edit_ref(bpy.types.Operator):
	  
	#tooltip
	""" Select the rig then click it to display the reference bones layer for editing"""
	
	bl_idname = "id.edit_ref"
	bl_label = "edit_ref"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if is_object_arp(context.object):
				if not context.object.data.layers[17]:
					return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try: #check if the armature is selected				  
				get_bones = bpy.context.active_object.data.bones					   
			except AttributeError:
				self.report({'ERROR'}, "Select the rig object")						
				return{'FINISHED'}
				
			_edit_ref()			   
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
class dupli_limb(bpy.types.Operator):
	  
	#tooltip
	""" Select a bone of the limb to duplicate, and click it to duplicate the whole limb"""
	
	bl_idname = "id.dupli_limb"
	bl_label = "dupli_limb"
	bl_options = {'UNDO'}	
	
	first_mouse_x = bpy.props.IntProperty()
	first_value = bpy.props.FloatProperty()
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'EDIT_ARMATURE':
			if len(context.selected_editable_bones) > 0:
				bone = context.selected_editable_bones[0]
				if len(bone.keys()) > 0:
					if 'arp_duplicate' in bone.keys():
						return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try: #check if the armature is selected				  
				get_bones = bpy.context.active_object.data.bones					   
			except AttributeError:
				self.report({'ERROR'}, "Select the rig object")						
				return{'FINISHED'}
				
			_dupli_limb()		  
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
	   
	
	
class align_arm_bones(bpy.types.Operator):
	  
	#tooltip
	""" Select the rig then click it to align the arm bones, roll, fk pole... from the main bones"""
	
	bl_idname = "id.align_arm_bones"
	bl_label = "align_arm_bones"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try:				
				get_bones = bpy.context.active_object.data.bones					   
			except AttributeError:
				self.report({'ERROR'}, "Select the rig object")						
				return{'FINISHED'}
				
			_align_arm_bones()			  
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
	
class align_spine_bones(bpy.types.Operator):
	  
	#tooltip
	""" Align the spine bones from the main bones"""
	
	bl_idname = "id.align_spine_bones"
	bl_label = "align_spine_bones"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try:				
				get_bones = bpy.context.active_object.data.bones					   
			except AttributeError:
				self.report({'ERROR'}, "Select the rig object")						
				return{'FINISHED'}
				
			_align_spine_bones()			
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
	
class align_leg_bones(bpy.types.Operator):
	  
	#tooltip
	""" Align the legs bones, roll, fk pole... from the main bones"""
	
	bl_idname = "id.align_leg_bones"
	bl_label = "align_leg_bones"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try:				
				get_bones = bpy.context.active_object.data.bones					   
			except AttributeError:
				self.report({'ERROR'}, "Select the rig object")						
				return{'FINISHED'}
				
			_align_leg_bones()			  
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
	
class align_all_bones(bpy.types.Operator):
	  
	#tooltip
	""" Select the rig then click it to match the rig with the reference bones"""
	
	bl_idname = "id.align_all_bones"
	bl_label = "align_all_bones"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if is_object_arp(context.object):
				return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try:				
				get_bones = bpy.context.active_object.data.bones					   
			except AttributeError:
				self.report({'ERROR'}, "Select the rig object")						
				return{'FINISHED'}
				
			#save mirror state 
			mirror_state = bpy.context.active_object.data.use_mirror_x	
			#simplify			
			simplify_value = bpy.context.scene.render.use_simplify
			simplify_subd = bpy.context.scene.render.simplify_subdivision
			bpy.context.scene.render.use_simplify = True
			bpy.context.scene.render.simplify_subdivision = 0
			
			_align_arm_bones()		  
			_align_leg_bones()			  
			_align_spine_bones()			
			_reset_stretches()
			_set_inverse()
			
			bpy.context.active_object.show_x_ray = False	
			#restore mirror state
			bpy.context.active_object.data.use_mirror_x = mirror_state
			#restore simplify
			bpy.context.scene.render.use_simplify = simplify_value
			bpy.context.scene.render.simplify_subdivision = simplify_subd

		   
			
			self.report({'INFO'}, "Rig Done")		
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}	  

	
 ##########################	 FUNCTIONS	##########################
def project_vector_onto_vector(a, b):		
		abdot = (a[0]*b[0])+(a[1]*b[1])+(a[2]*b[2])
		blensq = (b[0]**2)+(b[1]**2)+(b[2]**2)

		temp = abdot/blensq
		c = Vector((b[0]*temp,b[1]*temp,b[2]*temp))
		
		return c	

def project_point_onto_plane(q, p, n):
			n = n.normalized()
			return q - ((q-p).dot(n)) * n		
 
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
			
			
 
def _move_picker_layout(state):
	bpy.ops.object.mode_set(mode='POSE')	
	bpy.ops.pose.select_all(action='DESELECT')	

	if state == 'start':
		_value = False
	else:
		_value = True
		
	#disable picker
	try:
		bpy.context.scene.Proxy_Picker.active = _value
	except:
		pass
	
	#unlock transforms
	for pbone in bpy.context.active_object.pose.bones:
		if 'proxy' in pbone.name or 'layer_disp' in pbone.name:
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
			
			if len(pbone.constraints) > 0:
				for cns in pbone.constraints:
					cns.mute = True
			
	_mesh = None		
	objects_list = []
	rig_ui = None
	
	for child in bpy.context.active_object.children:
		if 'rig_ui' in child.name:
			rig_ui = child		
	
	for obj in bpy.data.objects:
		if 'picker_background' in obj.name:
			objects_list.append(obj.name)
			break		
	
	for child in rig_ui.children:
		if 'label' in child.name:
			objects_list.append(child.name)
		if '_mesh' in child.name:
			objects_list.append(child.name)
	
	for obj in objects_list:
		if bpy.data.objects.get(obj) != None:
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
	if bpy.data.objects.get('picker_background') != None:
		bpy.data.objects.remove(bpy.data.objects['picker_background'], True)
	
	#create empty image
	if bpy.data.objects.get('picker_background') == None:
		empty_image = bpy.data.objects.new("picker_background", None)
		scene = bpy.context.scene
		scene.objects.link(empty_image)
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
				
		vert_up_global = ui_mesh.matrix_world * vert_up.co
		vert_deep_global = ui_mesh.matrix_world * vert_deep.co
		
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
						
		
		empty_image.location = rig_ui.matrix_world.inverted() * empty_image.location
		empty_image.scale = rig_ui.matrix_world.inverted() * empty_image.scale
		empty_image.parent = rig_ui
		
		
		current_mode = bpy.context.mode	
		
		"""
		#only if the mesh has not been tweaked already, remove facial verts
		ui_mesh.hide_select = False
		set_active_object(ui_mesh.name)	
		bpy.ops.object.mode_set(mode='EDIT')			
		mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)			
		vert_count = len(mesh.verts)
		
		
		if vert_count == 105 and not '_ui' in ui_mesh.data.name:
			face_vert = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 37, 38, 39, 40, 59, 60]	
			bpy.ops.mesh.select_all(action='DESELECT')

			for idx in face_vert:
				mesh.verts.ensure_lookup_table()
				_vert = mesh.verts[idx]
				_vert.select = True				
				#mesh.verts.remove(_vert )
				
			bpy.ops.mesh.delete(type='VERT')
		
		#only hide select if the layout is not being edited
		if len(bpy.context.scene.keys()) > 0:
				if 'Proxy_Picker' in bpy.context.scene.keys():
					if bpy.context.scene.Proxy_Picker.active:
						ui_mesh.hide_select = True	
		"""

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

		#Middle
	_bone_groups["body.x"].colors.normal = scene.color_set_middle
	
	for i, channel in enumerate (_bone_groups["body.x"].colors.select):
		_bone_groups["body.x"].colors.select[i] = scene.color_set_middle[i]+0.4
		
	for i, channel in enumerate (_bone_groups["body.x"].colors.active):
		_bone_groups["body.x"].colors.active[i] = scene.color_set_middle[i]+0.5
		
		#Left
	_bone_groups["body.l"].colors.normal = scene.color_set_left
	
	for i, channel in enumerate (_bone_groups["body.l"].colors.select):
		_bone_groups["body.l"].colors.select[i] = scene.color_set_left[i]+0.4
		
	for i, channel in enumerate (_bone_groups["body.l"].colors.active):
		_bone_groups["body.l"].colors.active[i] = scene.color_set_left[i]+0.5
		
		
	#Materials
	_materials = bpy.context.blend_data.materials
	
	for mat in _materials:
		#Right
		if 'cs_' in mat.name and "_blue" in mat.name:
			#Selection color
			if '_sel' in mat.name:				
				for i, channel in enumerate (mat.diffuse_color):
					mat.diffuse_color[i] = scene.color_set_right[i]+0.4
			#Normal color
			else:
				for i, channel in enumerate (mat.diffuse_color):
					mat.diffuse_color[i] = scene.color_set_right[i]
					
		#Middle
		if 'cs_' in mat.name and "_green" in mat.name:
			#Selection color
			if '_sel' in mat.name:				
				for i, channel in enumerate (mat.diffuse_color):
					mat.diffuse_color[i] = scene.color_set_middle[i]+0.4
			#Normal color
			else:
				for i, channel in enumerate (mat.diffuse_color):
					mat.diffuse_color[i] = scene.color_set_middle[i]
					
		
		#Left
		if 'cs_' in mat.name and "_red" in mat.name:
			#Selection color
			if '_sel' in mat.name:				
				for i, channel in enumerate (mat.diffuse_color):
					mat.diffuse_color[i] = scene.color_set_left[i]+0.4
			#Normal color
			else:
				for i, channel in enumerate (mat.diffuse_color):
					mat.diffuse_color[i] = scene.color_set_left[i]
					
		#Panel back
		if 'cs' in mat.name and '_ui' in mat.name:			
			mat.diffuse_color = scene.color_set_panel
			mat.specular_color = (0,0,0)
			
		#Panel buttons
		if 'cs' in mat.name and 'button' in mat.name:			
			for i, channel in enumerate (mat.diffuse_color):
					mat.diffuse_color[i] = scene.color_set_panel[i]+0.2
			mat.specular_color = (0,0,0)
			
		#Panel text
		if ('cs' in mat.name and '_black' in mat.name) or  ('cs' in mat.name and '_text' in mat.name) or ('test_blend' in mat.name):			
			mat.diffuse_color = scene.color_set_text
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
						
def delete_children(passed_object):
	parent_obj = passed_object
	children = []

	for obj in bpy.data.objects:
		if obj.parent == parent_obj:
			children.append(obj)
			
			for _obj in children:
				for obj_1 in bpy.data.objects:
					if obj_1.parent == _obj:
						children.append(obj_1)
						
	for child in children:
		bpy.data.objects.remove(child, True)
		
	bpy.data.objects.remove(passed_object, True)

def _delete_arp():
	
	to_delete = ['cs_grp', 'char_grp']
	
	for object_to_delete in to_delete:
		if bpy.data.objects.get(object_to_delete) != None:		
			delete_children(bpy.data.objects[object_to_delete])
			
	
	#update
	bpy.context.scene.objects.active = bpy.context.scene.objects.active
		
 
def _append_arp():
	addon_directory = os.path.dirname(os.path.abspath(__file__))
	filepath = addon_directory + "/auto_rig.blend"
	
	#load the objects data in the file
	with bpy.data.libraries.load(filepath) as (data_from, data_to):
		data_to.objects = data_from.objects
	
	#add the objects in the scene
	for obj in data_to.objects:
		if obj is not None:
			bpy.context.scene.objects.link(obj)
			#change custom_shape objects layer to 19
			if "cs_" in obj.name or "c_sphere" in obj.name:
				obj.layers[19] = True
				
				for i in range(0, 19):#19 +1				
					obj.layers[i] = False
				
	bpy.context.space_data.show_relationship_lines = False
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object('rig')

	
 
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

def _mirror_custom_shape():
	
	armature = bpy.context.active_object

	for bone in bpy.context.selected_pose_bones:		
		bone_name = bone.name
		cs = bone.custom_shape
		side = bone.name[-2:]
		mirror_side = ""
		
		if side == '.l':
			mirror_side = ".r"
		if side == ".r":
			mirror_side = ".l"	
			
		#if there's a mirrored bone
		if bpy.data.objects[armature.name].pose.bones.get(bone.name[:-2] + mirror_side):
			mirror_bone = bpy.data.objects[armature.name].pose.bones[bone.name[:-2] + mirror_side]
			pivot_mode = bpy.context.space_data.pivot_point
			
			if not 'cs_user_' in mirror_bone.custom_shape.name:			
				#create the cs
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')		
				
				bpy.ops.mesh.primitive_plane_add(radius=1, view_align=True, enter_editmode=False, location=(-0, 0, 0.0), rotation=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
				mesh_obj = bpy.context.active_object
				mesh_obj.name = 'cs_user_' + mirror_bone.name	
				mesh_obj.data = cs.data
				bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
				mesh_obj.data.name = mesh_obj.name		
				
				#mirror it
				bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
				bpy.context.space_data.pivot_point = 'CURSOR'
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')

				bpy.ops.transform.mirror(constraint_axis=(True, False, False), constraint_orientation='LOCAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.111671)

				#bpy.ops.transform.mirror(constraint_axis=(True, False, False), constraint_orientation='GLOBAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.111671)								
				bpy.ops.object.mode_set(mode='OBJECT')
				
				#assign to bone
				mirror_bone.custom_shape = mesh_obj
				
				#move to last layer
				mesh_obj.layers[19] = True
				for i in mesh_obj.layers:
					if i != 19:
						mesh_obj.layers[i] = False
						
				mesh_obj.parent = bpy.data.objects['cs_grp']
				
			else:
				print("broumi")
				bpy.context.scene.layers[19] = True
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')		
				set_active_object(mirror_bone.custom_shape.name)
				mesh_obj = bpy.context.active_object
				mirror_bone.custom_shape.data = cs.data
				bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=False, obdata=True)
				mesh_obj.data.name = mesh_obj.name		
				
				
				#mirror it				
				bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
				bpy.context.space_data.pivot_point = 'CURSOR'
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.transform.mirror(constraint_axis=(True, False, False), constraint_orientation='LOCAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.111671)

				#bpy.ops.transform.mirror(constraint_axis=(True, False, False), constraint_orientation='GLOBAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.111671)	
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.context.scene.layers[19] = False
				
			set_active_object(armature.name)
			bpy.ops.object.mode_set(mode='POSE')
			bpy.context.space_data.pivot_point = pivot_mode
	
def _edit_custom_shape():
	bone = bpy.context.active_pose_bone
	armature = bpy.context.active_object
	cs = bpy.context.active_pose_bone.custom_shape
	cs_mesh = cs.data

	bpy.ops.object.posemode_toggle()

	bpy.ops.mesh.primitive_plane_add(radius=1, view_align=True, enter_editmode=False, location=(-0, 0, 0.0), rotation=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

	mesh_obj = bpy.context.active_object
	mesh_obj.name = 'cs_user_' + bone.name
	mesh_obj.data= cs_mesh
	
	if not 'cs_user' in cs.name:#if the shape is not already user tweaked, create new object data	
		bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
		mesh_obj.data.name = mesh_obj.name
		bone.custom_shape = mesh_obj
	else:#else just make instance 
		mesh_obj.data= cs_mesh
		mesh_obj['delete'] = 1.0

	if bone.custom_shape_transform != None:
		bone_transf = bone.custom_shape_transform
		mesh_obj.matrix_world = armature.matrix_world * bone_transf.matrix
	else:
		mesh_obj.matrix_world = armature.matrix_world * bone.matrix
	mesh_obj.scale *= bone.custom_shape_scale
	mesh_obj.scale *= bone.length 
	
	bpy.ops.object.mode_set(mode='EDIT')

def _exit_edit_shape():
	bpy.ops.object.mode_set(mode='OBJECT')
	obj = bpy.context.active_object
	delete_obj = False
	
	obj.parent = bpy.data.objects['cs_grp']
	
	
	if len(obj.keys()) > 0:
		for key in obj.keys():
			if 'delete' in key:
				delete_obj = True
	
	if delete_obj:
		bpy.ops.object.delete(use_global=False)
	else:
		#bpy.ops.object.rotation_clear(clear_delta=False)


		obj.layers[19] = True
		for i in range(0,20):
			if i != 20:
				obj.layers[i] = False
				
	
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
	
 
def _update_armature(self):

	sides = ['.l', '.r']

	def replace_var(dr):
			for v1 in dr.driver.variables:					
				if 'c_ikfk_arm' in v1.targets[0].data_path:							  
					v1.targets[0].data_path = v1.targets[0].data_path.replace('c_ikfk_arm', 'c_hand_ik')
					
				if 'c_ikfk_leg' in v1.targets[0].data_path:								  
					v1.targets[0].data_path = v1.targets[0].data_path.replace('c_ikfk_leg', 'c_foot_ik')
					
	#Save current mode
	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='POSE')

	
	#Active all layers
		#save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):  
		layers_select.append(_layers[i])

	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True 
		
	#disable the proxy picker to avoid bugs
	try:	   
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass
	
	need_update = False
	#create the ik_fk property if necessary (update from older armature version)
	try:
		get_pose_bone("c_foot_ik.l")["ik_fk_switch"]
		
	except KeyError:
		need_update = True
		for side in sides:
			get_pose_bone("c_foot_ik" + side)["ik_fk_switch"] = get_pose_bone("c_ikfk_leg" + side)["ik_fk_switch"]
			get_pose_bone("c_foot_ik" + side)["_RNA_UI"] = {}	   
			get_pose_bone("c_foot_ik" + side)["_RNA_UI"]['ik_fk_switch'] = {"min":0.0,"max": 1.0, "soft_min":0.0,"soft_max":1.0}	
			
			get_pose_bone("c_hand_ik" + side)["ik_fk_switch"] = get_pose_bone("c_ikfk_arm" + side)["ik_fk_switch"]
			get_pose_bone("c_hand_ik" + side)["_RNA_UI"] = {}	   
			get_pose_bone("c_hand_ik" + side)["_RNA_UI"]['ik_fk_switch'] = {"min":0.0,"max": 1.0, "soft_min":0.0,"soft_max":1.0}	
		
		print('....IK-FK properties updated')
		#update drivers
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
		
	
	#make sure properties limits are corrects
	for side in sides:		
		get_pose_bone("c_hand_ik" + side)["_RNA_UI"] = {}	   
		get_pose_bone("c_hand_ik" + side)["_RNA_UI"]['stretch_length'] = {"min":0.2, "max": 4.0}
		get_pose_bone("c_hand_ik" + side)["_RNA_UI"]['auto_stretch'] = {"min":0.0, "max": 1.0}
		get_pose_bone("c_hand_ik" + side)["_RNA_UI"]['ik_fk_switch'] = {"min":0.0, "max": 1.0}
		
		get_pose_bone("c_foot_ik" + side)["_RNA_UI"] = {}	   
		get_pose_bone("c_foot_ik" + side)["_RNA_UI"]['stretch_length'] = {"min":0.2, "max": 4.0}
		get_pose_bone("c_foot_ik" + side)["_RNA_UI"]['auto_stretch'] = {"min":0.0, "max": 1.0}
		get_pose_bone("c_foot_ik" + side)["_RNA_UI"]['ik_fk_switch'] = {"min":0.0, "max": 1.0}
	
	print('....Properties limits set')	
	
  
	#hide/delete obsolete ref bones - Pose mode only
	get_data_bone('toes_end_ref.l').hide = True
	get_data_bone('toes_end_ref.r').hide = True	   
				
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='DESELECT')
	
	sides = ['.l', '.r']
	
	try:
		for side in sides:
			get_bone('c_ikfk_arm'+side).select = True
			get_bone('c_ikfk_leg'+side).select = True
			need_update = True
			
		bpy.ops.armature.delete()
		print('....Deleted deprecated bones')
	except:
		pass

	
	#Update bone properties
	duplicate_bones = ['thigh_ref.l', 'leg_ref.l', 'foot_ref.l', 'thigh_ref.r', 'leg_ref.r', 'foot_ref.r', 'shoulder_ref.r', 'arm_ref.r', 'forearm_ref.r', 'hand_ref.r', 'shoulder_ref.l', 'arm_ref.l', 'forearm_ref.l', 'hand_ref.l']	

	for bone in duplicate_bones:
		get_bone(bone)['arp_duplicate'] = 1.0
		
	#update bones name
	try:		
		get_bone('c_stretch_arm_pin_proxy.r.001').name = 'c_stretch_leg_pin_proxy.r'
		get_bone('c_stretch_arm_pin_proxy.l.001').name = 'c_stretch_leg_pin_proxy.l'
	except:
		pass
	try:
		get_bone('eye_ref.l').name = 'c_eye_ref.l' 
		get_bone('eye_ref.r').name = 'c_eye_ref.r'	
		need_update = True
	except:
		pass  
	get_pose_bone('c_eye_ref_proxy.l')['proxy'] = 'c_eye_ref.l'
	get_pose_bone('c_eye_ref_proxy.r')['proxy'] = 'c_eye_ref.r'

	
	#update layers 
	for bone in bpy.context.active_object.data.edit_bones:		  
		try:
			bone['arp_layer'] = auto_rig_datas.bones_arp_layer[bone.name]
			
		except:
			pass
			
	bpy.ops.object.mode_set(mode='POSE')		
	
	for bone in bpy.context.active_object.pose.bones:
		try:			
			bone['arp_layer'] = auto_rig_datas.bones_arp_layer[bone.name]			 
		except:
			pass
			
	get_pose_bone('c_foot_ik.l')['fix_roll'] = 0.0
	get_pose_bone('c_foot_ik.r')['fix_roll'] = 0.0
	print('....Bone properties updated')
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	#Update parent 
	for side in sides:	  
		if get_bone('shoulder_ref'+side).parent == None:
			get_bone('shoulder_ref'+side).parent = get_bone('spine_02_ref.x') 
		if get_bone('thigh_ref'+side).parent == None:
			get_bone('thigh_ref'+side).parent = get_bone('root_ref.x')
		if get_bone('foot_bank_01_ref'+side).parent == None:
			get_bone('foot_bank_01_ref'+side).parent = get_bone('foot_ref'+side)
		

	#hide obsolete ref bones - Edit mode only
	get_bone('toes_end_ref.l').hide = True
	get_bone('toes_end_ref.r').hide = True

	#create new bones
	if get_bone('c_p_foot.l') != None:
		bpy.ops.armature.select_all(action='DESELECT')
		get_bone('c_p_foot.l').select = True
		get_bone('c_p_foot.r').select = True
		bpy.ops.object.mode_set(mode='POSE')		   
		bpy.ops.object.mode_set(mode='EDIT')#debug selection	   
		
		bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0, 0, 0), "mirror":False, "proportional":'DISABLED', "remove_on_cancel":False, "release_confirm":False})
		
		get_bone('c_p_foot.l.001').name = 'c_p_foot_fk.l'
		get_bone('c_p_foot.r.001').name = 'c_p_foot_fk.r'
		
		get_bone('c_p_foot.l').name = 'c_p_foot_ik.l'
		get_bone('c_p_foot.r').name = 'c_p_foot_ik.r'
		print('....New bones created')
	
		
	#update shoulders
	for side in sides:
		get_bone('c_p_shoulder'+side).parent = get_bone('c_shoulder' + side)
		
	#update layers
	for side in sides:
		switch_bone_layer('eyelid_top'+side, 0, 8, False)
		switch_bone_layer('eyelid_bot'+side, 0, 8, False)
		
	#update toes roll
	toes_ref = get_bone('toes_ref' + side)
	foot_ref = get_bone('foot_ref' + side)		  
	bpy.ops.armature.select_all(action='DESELECT')
	bpy.context.active_object.data.edit_bones.active = toes_ref	 
	bpy.context.active_object.data.edit_bones.active = foot_ref
	bpy.ops.armature.calculate_roll(type='ACTIVE') 
	print('....Toes roll updated')
	
	#update spine proxy locations
	spine_dict = auto_rig_datas.bone_update_locations
	
	for bone in spine_dict:
		get_bone(bone).head, get_bone(bone).tail = spine_dict[bone]
		
	bpy.ops.object.mode_set(mode='POSE')	  
	
	#update constraints
	for side in sides:	  
		get_pose_bone('c_p_shoulder'+side).constraints[0].mute = True		
		get_pose_bone('thigh_stretch' + side).constraints['Copy Location'].subtarget = 'thigh_twist' + side
		get_pose_bone('thigh_stretch' + side).constraints['Copy Location'].head_tail = 1.0
		get_pose_bone('arm_stretch' + side).constraints['Copy Location'].subtarget = 'arm_twist' + side
		get_pose_bone('arm_stretch' + side).constraints['Copy Location'].head_tail = 1.0
		
	#Update fcurve datapath
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
				#action.fcurves.remove(fcurve)
				invalid_fcurves.append(fcurve)
			   
		for fc in invalid_fcurves:			
			action.fcurves.remove(fc)
			
	
		
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
	"""
	if need_update:
		self.report({'ERROR'}, "Armature successfully updated! \n However the following features are not included in this corrective update, it's required to use the latest armature version:\n -New teeth controls")
	else:
	"""
	self.report({'INFO'}, "Armature Updated")
	 
	bpy.ops.object.mode_set(mode=current_mode)
	print('Finished armature update')
	
	
	
 
def _enable_all_limbs(self, context):
	#display all layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True
		

	#fingers / toes
	context.object.symetric_fingers = True
	context.object.symetric_toes = True
	fingers = ['thumb', 'index', 'middle', 'ring', 'pinky']
	
	for finger in fingers:
		bpy.context.active_object['rig_'+finger] = True
		bpy.context.active_object['rig_toes_'+finger] = True
	
	# other preset parts
	context.object['rig_breast'] = True	  
	context.object['rig_ears'] = True
	context.object['rig_facial'] = True
	context.object['rig_tail'] = True
	
	update_fingers(self, context)
	update_breast(self, context)
	update_toes(self, context)
	update_ears(self, context)
	update_facial(self, context)
	update_tail(self, context)
  
	#custom bone disabled	
	for bone in bpy.context.active_object.data.edit_bones:
		if bone.layers[22]:
			#switch to initial layer
			if len(bone.keys()) > 0:
				for prop in bone.keys():
					if 'arp_layer' in prop:
						switch_bone_layer(bone.name, 22, bone[prop], False)
						
			if '_ref' in bone.name and not 'eye_ref' in bone.name:#eye ref is the eye reflexion! eye reference is eye_offset_ref
				switch_bone_layer(bone.name, 22, 17, False)
				
	#enable arm deform
	sides = ['.l', '.r']
	arm_deform = auto_rig_datas.arm_deform
	leg_deform = auto_rig_datas.leg_deform
	for side in sides:
		for b_deform in arm_deform+leg_deform:
			get_bone(b_deform+side).use_deform = True
			get_bone(b_deform+side).layers[31] = True #deform layer for X-Muscles System
			
	#enable spine deform
	spine_deform = auto_rig_datas.head_deform + auto_rig_datas.neck_deform + auto_rig_datas.spine01_deform + auto_rig_datas.spine02_deform + auto_rig_datas.spine03_deform
	for b in spine_deform:
		try:
			get_bone(b).use_deform = True
			get_bone(b).layers[31] = True
		except:
			pass
	context.object.spine_disabled = False
		
	#enable bot deform	
	for side in sides:			  
		bpy.data.objects['rig_add'].data.bones['c_bot_bend'+side].use_deform = True		
	

	#display reference layer only
	for i in range(0,32):
		if i != 17:
			bpy.context.active_object.data.layers[i] = False
			
	
			
			
 
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
  
	#global var and functions
	sel_bone = bpy.context.selected_editable_bones[0].name
	side = sel_bone[-2:]  
	drivers_data = bpy.context.active_object.animation_data.drivers
	drivers_armature = bpy.context.active_object.data.animation_data.drivers
	
	
	rig = bpy.context.active_object
	rig_add = get_rig_add(rig)
					
	def remove_drivers(obj, drivers_list, sel_bone, limb_type):
		#workaround to pass bone name or bone data as argument
		try:
			sel_bone.name
			bone_name = sel_bone.name
		except:
			bone_name = sel_bone
			
		def _remove_driver(dp):
			try:
				obj.data.driver_remove(dp, -1)
			except:						
				obj.driver_remove(dp, -1)			 
  
		for dr in drivers_list:
			if bone_name[-12:] in dr.data_path:	 
				if limb_type == 'arm':
					if 'shoulder' in dr.data_path or 'arm' in dr.data_path or 'hand' in dr.data_path or 'bend_all' in dr.data_path:
						_remove_driver(dr.data_path)
							
				if limb_type == 'leg':
					if 'thigh' in dr.data_path or 'leg' in dr.data_path or 'foot' in dr.data_path or 'toes' in dr.data_path:
						_remove_driver(dr.data_path)
							
				if limb_type == 'finger':
					if 'bend_all' in dr.data_path:
						_remove_driver(dr.data_path)
					
					
	def disable_display_bones(b_name):
		try:
			b = get_bone(b_name)
			b.layers[22] = True
			b.layers[16] = False
			b.layers[0] = False
			b.layers[1] = False 
		except:
			print(b_name, 'is invalid')
		
  
	#ARMS	--------------------------------------
	arm_bones = auto_rig_datas.arm_bones
	arm_deform = auto_rig_datas.arm_deform
	arm_displayed = auto_rig_datas.arm_displayed
	arm_ref_bones = auto_rig_datas.arm_ref_bones
	fingers_list = ['thumb', 'index', 'middle', 'ring', 'pinky']
	fingers_displayed = auto_rig_datas.fingers_displayed

	if 'arm_' in sel_bone or 'shoulder' in sel_bone or 'hand' in sel_bone:
	
		#If dupli, delete all dupli bones		
		if '_dupli' in sel_bone:	 
			 #first remove drivers				  
			remove_drivers(context.object, drivers_data, get_bone(sel_bone), 'arm')
			remove_drivers(context.object, drivers_armature, get_bone(sel_bone), 'arm')
			
			bpy.ops.armature.select_all(action='DESELECT')
			#select the whole dupli limb			
			for bone in arm_bones: 
				try: #check if fingers deleted
					get_bone(bone+sel_bone[-12:]).select = True
				except:
					pass
			#select proxy bones
			for bone in arm_displayed + fingers_displayed: 
				try: #check if fingers deleted					  
					get_bone(bone+'_proxy'+sel_bone[-12:]).select = True
				except:
					pass
			for bone in arm_ref_bones:
				try:
					get_bone(bone+sel_bone[-12:]).select = True
				except:
					pass
				
			bpy.ops.armature.delete()	
			#delete visibility property
			try:
				del get_pose_bone('c_pos')['arm '+sel_bone[-5:]]
			except:
				print("Can't delete arm property")
			
							
			#rig_add bones			  
			rig_add.hide = False
			edit_rig(rig_add)
			bpy.ops.armature.select_all(action='DESELECT')
		 
			
			for bone in bpy.context.active_object.data.edit_bones:
				if sel_bone[-12:] in bone.name:
					bone.select = True					 
			bpy.ops.armature.delete()
			rig_add.hide = True
			edit_rig(rig)
			
		#If original limb, hide the bones and disable deform
		else:
			#deselect
			bpy.ops.armature.select_all(action='DESELECT')
			#set active
			bpy.context.active_object.data.edit_bones.active = get_bone('shoulder_ref'+sel_bone[-2:])	 
			#select children
			bpy.ops.armature.select_similar(type='CHILDREN')		  

			#Ref bones
			for bone in bpy.context.selected_editable_bones:		  
				switch_bone_layer(bone.name, 17, 22, False)	   
			
			#Deform bones	
			for b in arm_deform:
				get_bone(b+side).use_deform = False
				get_bone(b+side).layers[31] = False				
				
			#Displayed bones
			for bo in arm_displayed:
				disable_display_bones(bo + side)   
				disable_display_bones(bo + '_proxy' + side)
			
		
				
	#LEGS -------------------------------------------------------------
	leg_bones = auto_rig_datas.leg_bones
	leg_deform = auto_rig_datas.leg_deform
	leg_displayed = auto_rig_datas.leg_displayed
	leg_ref_bones = auto_rig_datas.leg_ref_bones
	toes_list = ['thumb', 'index', 'middle', 'ring', 'pinky']
	toes_displayed = auto_rig_datas.toes_displayed
	
	if 'thigh' in sel_bone or 'leg' in sel_bone or 'foot' in sel_bone:
		
		#If dupli, delete all dupli bones		
		if '_dupli' in sel_bone:	 
			#first remove drivers	   
			remove_drivers(context.object, drivers_data, get_bone(sel_bone), 'leg')
			remove_drivers(context.object, drivers_armature, get_bone(sel_bone), 'leg')			   
			
			#select the whole dupli limb  
			bpy.ops.armature.select_all(action='DESELECT')
			for bone in leg_bones: 
				try: #check if fingers deleted					  
					get_bone(bone+sel_bone[-12:]).select = True
				except:
					pass
				#ref bones
			for bone in leg_ref_bones:
				try:
					get_bone(bone+sel_bone[-12:]).select = True
				except:
					pass
				#proxy bones	   
			for bone in leg_displayed + toes_displayed: 
				try: #check if fingers deleted					  
					get_bone(bone+'_proxy'+sel_bone[-12:]).select = True
				except:
					pass
				
			bpy.ops.armature.delete()			 
			
				
			#rig_add bones			  
			rig_add.hide = False
			edit_rig(rig_add)
			bpy.ops.armature.select_all(action='DESELECT')
	
			
			for bone in bpy.context.active_object.data.edit_bones:
			 
				if sel_bone[-12:] in bone.name:
					bone.select = True					 
			bpy.ops.armature.delete()
			rig_add.hide = True
			edit_rig(rig)
			
			#delete visibility property
		   
			try:
				del get_pose_bone('c_pos')['leg '+sel_bone[-5:]]
			except:
				print("Can't delete arm property")
			
		#If original limb, hide the bones and disable deform
		else:
			#deselect
			bpy.ops.armature.select_all(action='DESELECT')
			#set active
			bpy.context.active_object.data.edit_bones.active = get_bone('thigh_ref'+sel_bone[-2:])	  
			#select children
			bpy.ops.armature.select_similar(type='CHILDREN')
			#Ref bones
			for bone in bpy.context.selected_editable_bones:		  
				switch_bone_layer(bone.name, 17, 22, False)	   
			
			#Deform bones	
			for b in leg_deform:
				get_bone(b+side).use_deform = False
				get_bone(b+side).layers[31] = False			
				
			#Displayed bones
			for bo in leg_displayed:
				disable_display_bones(bo + side)   
				disable_display_bones(bo + '_proxy' + side)
	
				
	#FINGERS --------------------------------------------------------------
	def disable_finger(finger, suffix, bone_name):
		
		#If multi, delete it
		if len(suffix) > 3:
			bpy.ops.armature.select_all(action='DESELECT')
			
			#first remove fingers drivers	  
			if not 'toes' in bone_name:
				remove_drivers(context.object, drivers_data, finger, 'finger')
				remove_drivers(context.object, drivers_armature, finger, 'finger')
			
			#Delete bones
				#rig
			for bone in bpy.context.active_object.data.edit_bones:
				if (suffix in bone.name) and (finger in bone.name):
					bone.select = True
			
			bpy.ops.armature.delete()
			
		
		#If original, hide it and disable deform
		if len(suffix) < 3:
			#finger and toes have different phalanges count
			i_start = 0	 
			i_end = 4
			prefix = ""
			
			if 'toes' in bone_name:
				i_start = 1				   
				prefix = 'toes_'
				if 'thumb' in bone_name:
					i_end = 3	
				
			for i in range (i_start,i_end):				   
				ref_bone = prefix + finger+str(i)+"_ref"+suffix				  
				proxy_bone = "c_"+ prefix + finger+str(i)+"_proxy"+suffix
				c_bone = "c_"+ prefix + finger+str(i)+suffix
					
				if i == 0:				  
					ref_bone = finger+str(i+1)+"_base_ref"+suffix
					c_bone = "c_"+finger+str(i+1)+"_base"+suffix				
					proxy_bone = "c_"+finger+str(i+1)+"_base_proxy"+suffix				 
					
					if 'thumb' in finger:
						ref_bone = finger+str(i+1)+"_ref"+suffix
						 
				# ref bones
				switch_bone_layer(ref_bone, 17, 22, False)
				# proxy bones			 
				switch_bone_layer(proxy_bone, 0, 22, False)
				# control bones
				switch_bone_layer(c_bone, 0, 22, False)
				switch_bone_layer(c_bone, 31, 22, False)
				get_bone(c_bone).use_deform = False
  
	
	for f in fingers_list:
		for bone in bpy.context.selected_editable_bones:		  
			if f in bone.name:			   
				if '_dupli' in bone.name:
					_suffix = bone.name[-12:]				
				else:
					_suffix = bone.name[-2:]
	  
					if 'toes' in bone.name:
						context.object.symetric_toes = False
				
					else:
						context.object.symetric_fingers = False
					
				disable_finger(finger=f, bone_name = bone.name, suffix=_suffix)
		  
	
	
	#SPINE
	def disable_head(context):
		context.object.rig_facial = False
		context.object.rig_ears = False
		
		head_deform = auto_rig_datas.head_deform
		head_displayed = auto_rig_datas.head_displayed
		
		for bone in head_deform:			
			get_bone(bone).use_deform = False
			get_bone(bone).layers[31] = False
		for bone in head_displayed:
			get_bone(bone).layers[22] = True
			get_bone(bone).layers[0] = False
			get_bone(bone).layers[1] = False
			get_bone(bone).layers[16] = False
		
		switch_bone_layer('head_ref.x', 17, 22, False)
		
	def disable_neck(context):		  
		
		neck_deform = auto_rig_datas.neck_deform
		neck_displayed = auto_rig_datas.neck_displayed
		
		for bone in neck_deform:
			get_bone(bone).use_deform = False
			get_bone(bone).layers[31] = False
		for bone in neck_displayed:
			get_bone(bone).layers[22] = True
			get_bone(bone).layers[0] = False
			get_bone(bone).layers[1] = False
			get_bone(bone).layers[16] = False
		
		switch_bone_layer('neck_ref.x', 17, 22, False)
		
	def disable_child_connections(current_bone):
	#check for existing parent connection
		for bone in bpy.context.active_object.data.edit_bones:
			if bone.layers[17]:
				if bone.parent == get_bone(current_bone):
					bone.parent = None
		
	def disable_spine(spine_bone, context):		   
		
		if '01' in spine_bone:
			spine_deform = auto_rig_datas.spine01_deform
			spine_displayed = auto_rig_datas.spine01_displayed
		if '02' in spine_bone:
			spine_deform = auto_rig_datas.spine02_deform
			spine_displayed = auto_rig_datas.spine02_displayed
		if '03' in spine_bone:
			spine_deform = auto_rig_datas.spine03_deform
			spine_displayed = auto_rig_datas.spine03_displayed
			#change bend parent
			get_bone('c_spine_02_bend.x').parent = get_bone('spine_02.x')
		  
		
		for bone in spine_deform:
			get_bone(bone).use_deform = False
			get_bone(bone).layers[31] = False
		for bone in spine_displayed:
			get_bone(bone).layers[22] = True
			get_bone(bone).layers[0] = False
			get_bone(bone).layers[1] = False
			get_bone(bone).layers[16] = False
		
		switch_bone_layer(spine_bone , 17, 22, False)		 
		disable_child_connections(spine_bone)
		context.object.spine_disabled = True
		   
	def disable_bot(context):
		sides = ['.l', '.r']
		switch_bone_layer('bot_bend_ref', 17, 22, True)		
		
		for side in sides:			  
			#get_bone('c_bot_bend'+side).use_deform = False
			rig_add.data.bones['c_bot_bend'+side].use_deform = False
			switch_bone_layer('c_bot_bend'+side, 1, 22, False)
			get_bone('c_bot_bend'+side).layers[31] = False
			#proxy picker
			switch_bone_layer('c_bot_bend_proxy'+side, 1, 22, False)
			
	
	#facial
	for bone in auto_rig_datas.facial_ref:
		if sel_bone == bone:
			context.object.rig_facial = False
	#head
	if 'head' in sel_bone:
		disable_head(context)
	#neck
	if 'neck' in sel_bone:
		disable_head(context)
		disable_neck(context) 
		
	#spine
	if 'spine' in sel_bone:
		if '01' in sel_bone:
			disable_spine('spine_01_ref.x', context) 
			disable_spine('spine_02_ref.x', context) 
		if '02' in sel_bone:		  
			disable_spine('spine_02_ref.x', context) 
		if get_bone('spine_03_ref.x') != None:
			disable_spine('spine_03_ref.x', context)	   
	   
		context.object.rig_breast = False		 
		disable_neck(context)
		disable_head(context)
	
	#tail
	if 'tail' in sel_bone:
		context.object.rig_tail = False
	#breast
	if 'breast' in sel_bone:
		context.object.rig_breast = False		 
	#ears
	if 'ear' in sel_bone:
		context.object.rig_ears = False
	#bot
	if 'bot_bend' in sel_bone:
		disable_bot(context)
	
	#Select at least one bone to avoid the pop up effect of the panel
	if len(bpy.context.selected_editable_bones) < 1:
		bpy.context.active_object.data.edit_bones.active = get_bone('root_ref.x')
		#bpy.context.active_object.data.edit_bones['root_ref.x'].select = True
		
	#display reference layer only
	for i in range(0,32):
		if i != 17:
			bpy.context.active_object.data.layers[i] = False
			
	#restore the picker		   
	try:	   
		bpy.context.scene.Proxy_Picker.active = True
	except:
		pass
			
	#Restore mirror edit
	bpy.context.active_object.data.use_mirror_x = mirror_edit
	
			
 
def _pick_bone():
 
	bpy.context.scene.driver_bone = bpy.context.active_object.data.bones.active.name

 
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
	new_var.targets[0].bone_target = bpy.context.scene.driver_bone

	new_var.targets[0].transform_type = bpy.context.scene.driver_transform
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
	
	#remove the fcurve modifier
	if len(shape_key_driver.modifiers) > 0:
		shape_key_driver.modifiers.remove(shape_key_driver.modifiers[0])
	
	#create keyframe
	if value != 'reset':
			#get the bone driver	
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
		
		
		keyf = shape_key_driver.keyframe_points.insert(frame, float(value))
		keyf.interpolation = 'LINEAR'
		#check if 1st key created
		first_key_created = False
		for key in shape_key_driver.keyframe_points:
			if round(key.co[0],2) == 0:
				first_key_created = True
		if not first_key_created:
			keyf = shape_key_driver.keyframe_points.insert(0, 0)
			keyf.interpolation = 'LINEAR'
			
	else:#reset
	
		#create driver	
		print('reset')
		_id = shape_key_driver.driver.variables[0].targets[0].id
		_bone_target = shape_key_driver.driver.variables[0].targets[0].bone_target
		_transform_type = shape_key_driver.driver.variables[0].targets[0].transform_type
		_transform_space =	shape_key_driver.driver.variables[0].targets[0].transform_space
		_expression = shape_key_driver.driver.expression
		print(_expression)
		
		#delete driver
		obj.data.shape_keys.driver_remove(shape_key_driver.data_path, -1)
		#create new one from old one
		new_driver = shape_keys[shape_index].driver_add("value")
		new_driver.driver.expression = _expression
		new_var = new_driver.driver.variables.new()
		new_var.type = 'TRANSFORMS'
		new_var.targets[0].id = _id
		new_var.targets[0].bone_target = _bone_target
		new_var.targets[0].transform_type = _transform_type
		new_var.targets[0].transform_space = _transform_space
	
			

		
		
	bpy.ops.transform.translate(value=(0, 0, 0))#update hack
	
def _dupli_limb():
	
	#display all layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True	  

	#disable the proxy picker to avoid bugs
	try:	   
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass
		
	bpy.context.active_object.data.use_mirror_x = False
	arm_bones = auto_rig_datas.arm_bones
	arm_ref_bones = auto_rig_datas.arm_ref_bones
	arm_bones_rig_add = auto_rig_datas.arm_bones_rig_add
	leg_bones = auto_rig_datas.leg_bones
	leg_ref_bones = auto_rig_datas.leg_ref_bones
	leg_bones_rig_add = auto_rig_datas.leg_bones_rig_add
	
	selected_bone = bpy.context.selected_editable_bones

	sides = [".l", ".r"] 
	
	def duplicate_ref(limb, side, suffix):
		if limb == 'arm':
			bone_list = auto_rig_datas.arm_ref_bones			
		if limb == 'leg':
			bone_list = auto_rig_datas.leg_ref_bones
			
			#select bones			
		bpy.ops.armature.select_all(action='DESELECT')

		for bone in bone_list:	  
			if get_bone(bone+side).layers[22] == False:#if not disabled (finger, toes...)
				get_bone(bone+side).select = True	 
				
		bpy.ops.object.mode_set(mode='POSE')		   
		bpy.ops.object.mode_set(mode='EDIT')#debug selection			
		
		#duplicate	   
		bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "mirror":False, "proportional":'DISABLED', "snap":False,"gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})		  
		
		# rename				
		for bone in bpy.context.selected_editable_bones:
			#delete 'duplicate' property
			if len(bone.keys()) > 0:
				for prop in bone.keys():
					if 'arp_duplicate' in prop:
						del bone['arp_duplicate']
			
			bone.name = bone.name[:-4].replace(side, '_dupli_' + suffix + side)
			
	
		
	def duplicate_rig(limb,side, suffix):
		if limb == 'arm':  
			limb_bones_list = arm_bones
			limb_displayed = auto_rig_datas.arm_displayed + auto_rig_datas.fingers_displayed
			limb_bones_rig_add = arm_bones_rig_add
			main_limbs = ['hand', 'arm']
		if limb == 'leg':
			limb_bones_list = leg_bones
			limb_displayed = auto_rig_datas.leg_displayed + auto_rig_datas.toes_displayed
			limb_bones_rig_add = leg_bones_rig_add
			main_limbs = ['leg', 'thigh', 'foot', 'toes']
			
		drivers_data = bpy.context.active_object.animation_data.drivers		
		drivers_armature = bpy.context.active_object.data.animation_data.drivers

		def create_limb_drivers(drivers_list):
			trim = 0
	
			for dr in drivers_list:
				#driver data
				if dr.data_path.partition('.')[0] == 'pose':
					trim = 12
				#driver armature
				else:
					trim = 7
					
				string = dr.data_path[trim:]
				dp_bone = string.partition('"')[0]
				
				is_limb = False
				
				for m_limb in main_limbs:
					if (m_limb in dp_bone or ('bend_all' in dp_bone and limb == 'arm')):
						is_limb = True						  
				
				if (is_limb) and dp_bone[-2:] == side and not '_dupli' in dp_bone:			  
					#create new driver						  
					new_driver = drivers_list.from_existing(src_driver = drivers_list.find(dr.data_path))
					"""
					if trim == 12:
						new_driver = bpy.context.active_object.driver_add(dr.data_path, -1)
					if trim == 7:
						new_driver = bpy.context.active_object.data.driver_add(dr.data_path, -1)
					"""				
					#set array index	
					try:
						new_driver.array_index = dr.array_index	 
					except:
						pass				 
					
					#change data path	 
				  
					if not 'foot_pole' in dp_bone:#can't create driver with 'from_existing' for foot pole Y location driver error hack, BUG???		   
						new_driver.data_path = dr.data_path.replace(dp_bone, dp_bone[:-2]+'_dupli_'+suffix+side)
					
					else:						 
						new_driver = bpy.context.active_object.driver_add("location", dr.array_index)
						new_driver.data_path = dr.data_path.replace(dp_bone, dp_bone[:-2]+'_dupli_'+suffix+side) 
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
							v1.targets[0].data_path = v1.targets[0].data_path.replace(dp_bone, dp_bone[:-2]+'_dupli_'+suffix+side)				   

						except:						 
							print("no data_path for: "+ v1.name)
					
		#-- end create drivers
	
	
		#base rig - select original bones
		bpy.ops.armature.select_all(action='DESELECT')
		
		for bone in limb_bones_list:
			try:
				if get_bone(bone+side).layers[22] == False:#if not disabled (finger, toes...)
					get_bone(bone+side).select = True
			except:
				print('INVALID BONE ', bone+side)
	
		bpy.ops.object.mode_set(mode='POSE')		   
		bpy.ops.object.mode_set(mode='EDIT')#debug selection

		#duplicate and move		 
		bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0.2, 0.0, 0.0), "constraint_axis":(False, False, False), "constraint_orientation":'LOCAL', "mirror":False, "proportional":'DISABLED', "snap":False, "remove_on_cancel":False, "release_confirm":False})
	
		# rename			 
		for bone in bpy.context.selected_editable_bones:				  
			bone.name = bone.name[:-4].replace(side, '_dupli_' + suffix + side)

		#create drivers
		bpy.ops.object.mode_set(mode='POSE')	 
		create_limb_drivers(drivers_data)
		create_limb_drivers(drivers_armature)
		
		#Proxy bones
		bpy.ops.object.mode_set(mode='EDIT') 
		bpy.ops.armature.select_all(action='DESELECT')
			#select
		for bone in limb_displayed:
			if get_bone(bone+side).layers[22] == False:#if not disabled (finger, toes...)
					get_bone(bone+'_proxy'+side).select = True					
					
		bpy.ops.object.mode_set(mode='POSE')		   
		bpy.ops.object.mode_set(mode='EDIT')#debug selection
		
		coef = 1
		if side == '.r':
			coef = -1
		suffix_count = int(float(suffix))#move offset for each dupli, get number of the limb
		
			#duplicate
		bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "constraint_axis":(False, False, False), "constraint_orientation":'LOCAL', "mirror":False, "proportional":'DISABLED', "snap":False, "remove_on_cancel":False, "release_confirm":False})
		
		#move
		for bone in bpy.context.selected_editable_bones:
			move_bone(bone.name, 0.26*coef*suffix_count, 0)
			
			#rename
		for bone in bpy.context.selected_editable_bones:
			bone.name = bone.name[:-4].replace(side, '_dupli_' + suffix + side)
			#set proxy bone
			get_pose_bone(bone.name)['proxy'] = get_pose_bone(bone.name)['proxy'].replace(side, '_dupli_' + suffix + side)
		
		#Rig add - select original bones		
		rig = bpy.context.active_object
		rig_add = get_rig_add(rig)
		rig_add.hide = False
		edit_rig(rig_add)
		bpy.ops.armature.select_all(action='DESELECT')
		#disable x-axis mirror edit
		bpy.context.active_object.data.use_mirror_x = False
		
		for bone in limb_bones_rig_add:	   
			get_bone(bone+side).select = True
	
		bpy.ops.object.mode_set(mode='POSE')		   
		bpy.ops.object.mode_set(mode='EDIT')#debug selection
		
		#duplicate and move		   
		bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0.2, 0.0, 0.0), "constraint_axis":(False, False, False), "constraint_orientation":'LOCAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":0.111671, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
		
		# rename				
		for bone in bpy.context.selected_editable_bones:				
			bone.name = bone.name[:-4].replace(side, '_dupli_' + suffix + side)
			
		#update constraint targets
		bpy.ops.object.mode_set(mode='POSE')
		for b in bpy.context.selected_pose_bones:
			try:
				b.constraints[0].subtarget = b.constraints[0].subtarget.replace(side, '_dupli_' + suffix + side)
			except:
				pass
		
		edit_rig(rig)
		rig_add.hide = True		
		
		#create dupli properties on the c_pos bones		   
		get_pose_bone('c_pos')[limb+' '+suffix+side] = True
		
		
	def get_suffix(side, bone_type):
		#find existing duplis  
		limb_id = 0
		for bone in bpy.context.active_object.data.edit_bones: 
			if 'shoulder' in bone_type or 'arm' in bone_type or 'finger' in bone_type:#arm dupli increment
				if "shoulder_ref_dupli_" in bone.name and bone.name[-2:] == side:				 
					current_id = int(float(bone.name[-5:-2]))
					if current_id > limb_id:
						limb_id = current_id
			if 'thigh' in bone_type or 'leg' in bone_type or 'toes' in bone_type:#leg dupli increment				
				if "thigh_ref_dupli" in bone.name and bone.name[-2:] == side:				 
					current_id = int(float(bone.name[-5:-2]))
					if current_id > limb_id:
						limb_id = current_id
   
		suffix = '{:03d}'.format(limb_id+1)
		return suffix
	
	#duplicate current limb
	side = selected_bone[0].name[-2:]
	suffix = get_suffix(side, selected_bone[0].name)

	for i in arm_ref_bones:
		if selected_bone[0].name in i+side:					
			duplicate_rig("arm", side, suffix)
   
			duplicate_ref("arm", side, suffix)
			break
	
	for i in leg_ref_bones:
		if selected_bone[0].name in i+side:					
			duplicate_rig("leg", side, suffix)
		   
			duplicate_ref("leg", side, suffix)
			break
				
	#display reference layer only
	for i in range(0,32):
		if i != 17:
			bpy.context.active_object.data.layers[i] = False
			
	#enable the proxy picker
	try:		 
		bpy.context.scene.Proxy_Picker.active = True
	except:
		pass
 
			

def _set_picker_camera():
	
	# go to object mode
	bpy.ops.object.mode_set(mode='OBJECT')
	
	#save current scene camera
	current_cam = bpy.context.scene.camera	  
	
	bpy.ops.object.select_all(action='DESELECT')

	 
	rig = bpy.context.active_object
	cam_ui = None
	
	for child in rig.children:
		if child.type == 'CAMERA' and 'cam_ui' in child.name:
			cam_ui = child
	
	cam_ui.select = True
	bpy.context.scene.objects.active = cam_ui
	bpy.ops.view3d.object_as_camera()
	
	#configure display
	bpy.context.space_data.lock_camera_and_layers = False 
	bpy.context.space_data.show_relationship_lines = False	
	bpy.context.space_data.use_matcap = False#disabled matcaps
	bpy.context.space_data.show_backface_culling = False#disabled backface cull
	bpy.context.space_data.lock_camera = False#unlock camera to view

	
	#set the camera clipping
	dist = (cam_ui.matrix_world.to_translation() - rig.matrix_world.to_translation()).length
	cam_ui.data.clip_start = dist*0.98	
	cam_ui.data.clip_end = dist*0.99
	cam_ui.data.ortho_scale = dist * 0.0563

	
	#restore the scene camera
	bpy.context.scene.camera = current_cam
	
	#back to pose mode
	bpy.ops.object.select_all(action='DESELECT')
	rig.select = True
	bpy.context.scene.objects.active = rig
	bpy.ops.object.mode_set(mode='POSE')
	
	

	
def get_selected_pair(obj_id):
	obj_1 =	 bpy.context.scene.objects.active	 
	obj_2 = None
	
	if bpy.context.selected_objects[0] == obj_1:
		obj_2 = bpy.context.selected_objects[1]
	else:
		obj_2 = bpy.context.selected_objects[0]
			
	if obj_id == 1:
		return obj_1
	if obj_id == 2:
		return obj_2
		

		
def get_rig_add(rig):
	rig_add = None
	
	for obj in rig.parent.children:
		if 'rig_add' in obj.name and not 'prop'in obj.name:
			rig_add = obj
			
	return rig_add
		
def set_active_object(object_name):
	 bpy.context.scene.objects.active = bpy.data.objects[object_name]
	 bpy.data.objects[object_name].select = True

def _bind_to_rig(self, context):
	
	sides = ['.l', '.r']	
	rig = bpy.context.scene.objects.active	
	selection_list = [obj for obj in bpy.context.selected_objects]
	scene = bpy.context.scene
	
	for obj in selection_list:
		if obj != rig:			
	
			rig_add = get_rig_add(rig) 
			rig_add.hide = False
			
			#split loose parts better weight assignation
			if scene.bind_split:
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(obj.name)
				bpy.ops.mesh.separate(type='LOOSE')
				split_objects = [obj for obj in bpy.context.selected_objects]
			else:
				split_objects = [obj]
			
			
			
			for i, split_obj in enumerate(split_objects):				
				
				print('skinning split object: ', split_obj.name)
				mesh = split_obj
				
				#bind to rig add
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')	
				set_active_object(mesh.name)
				set_active_object(rig_add.name)				
				bpy.ops.object.parent_set(type='ARMATURE_AUTO')
				
				#bind to rig
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(mesh.name)
				set_active_object(rig.name)
				bpy.ops.object.parent_set(type='ARMATURE_AUTO')
				set_active_object(mesh.name)
				bpy.context.active_object.modifiers["Armature"].name = "rig_add"
				bpy.context.active_object.modifiers["Armature.001"].name = "rig"
				
				#re-order at the top
				for i in range(0,20):
					bpy.ops.object.modifier_move_up(modifier="rig")
				for i in range(0,20):
					bpy.ops.object.modifier_move_up(modifier="rig_add")
				
				#put mirror at first
				for m in bpy.context.active_object.modifiers:
					if m.type == 'MIRROR':
						for i in range(0,20):
							bpy.ops.object.modifier_move_up(modifier=m.name)
				
				bpy.context.active_object.modifiers["rig"].use_deform_preserve_volume = True
				#unparent
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(mesh.name)
				bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
				
				
			#merge the split objects
			for split_obj in split_objects:
				set_active_object(split_obj.name)
			bpy.ops.object.join()			
			
			#improve head weights. for bipeds only. 
			enable_head_refine = True
			body = bpy.context.active_object	
			
			if enable_head_refine and body.vertex_groups.get('head.x') != None and rig.rig_type == 'biped':
				print("cleaning head weights...")
				jaw_loc = rig.matrix_world * rig.pose.bones['jaw_ref.x'].tail
				head_length = (rig.matrix_world * (rig.pose.bones['head_ref.x'].tail - rig.pose.bones['head_ref.x'].head)).magnitude				
				neck_tolerance = (jaw_loc[2] - head_length*0.07)				
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
							if not rig.rig_facial and scene.bind_chin:
								#if higher than the chin, set almost null weight	
								if	group_name in remove_from_head:													
									if (body.matrix_world * vert.co)[2] > neck_tolerance:
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
				bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', factor=0.5, repeat=4, expand=0.0, source='ALL')
			
			#smooth twist bones
			print('smoothing twist bones...')	
			smooth_twist_bones = True
			
			if smooth_twist_bones:
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
				
				twists = {'arm':['arm_stretch', 'c_arm_twist_offset'], 'forearm':['forearm_twist', 'forearm_stretch'], 'thigh':['thigh_twist', 'thigh_stretch'], 'leg':['leg_twist', 'leg_stretch']}
				
				for side in sides:	
					for bgroup in twists:
						#only if vgroup exists
						if body.vertex_groups.get(twists[bgroup][0] + side) != None and body.vertex_groups.get(twists[bgroup][1] + side) != None:
							bpy.ops.object.mode_set(mode='EDIT')
							select_overlap(twists[bgroup][0] + side, twists[bgroup][1] + side)
							bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
							for bone in twists[bgroup]:								
								vgroups.active_index = vgroups[bone+side].index							
								bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', factor=0.5, repeat=4, expand=0.0, source='ALL')
					
			bpy.context.active_object.data.use_paint_mask_vertex = False
			bpy.ops.object.mode_set(mode='OBJECT')
				
			

			rig_add.hide = True	 

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
					
				try:
					bpy.ops.object.vertex_group_remove(all=True)
				except:
					pass
 
 
 
def _edit_ref():
	
	
	#display layer 17 only
	_layers = bpy.context.active_object.data.layers
	#must enabling one before disabling others
	_layers[17] = True	
	for i in range(0,32):
		if i != 17:
			_layers[i] = False 
			
	#correct dupli names (.001)
	""""
	for armature in bpy.data.armatures:
			if 'rig' in armature.name and not 'add' in armature.name:
				armature.name = 'rig'
			if 'rig' in armature.name and 'add' in armature.name:
				armature.name = 'rig_add'
	"""
	  
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

def _align_arm_bones():
	
	
	print("\n Aligning arm bones...\n")
	
	#disable the proxy picker to avoid bugs
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass	
	
	#define the side
	sides = [".l",".r"]	   
	 
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
	
	arms = ["c_arm_fk", "arm_fk", "arm_ik_nostr", "arm_ik_nostr_scale_fix", "arm_ik", "arm_twist", "arm_stretch", "arm", "c_arm_twist_offset"]
	
	hands = ["hand", "c_hand_ik", "c_hand_fk", "c_hand_fk_scale_fix"]
	shoulders = ["shoulder", "c_shoulder"]
	arm_bends = ["c_shoulder_bend", "c_arm_bend", "c_elbow_bend", "c_forearm_bend", "c_wrist_bend"]
	
   
	
	bpy.ops.object.mode_set(mode='EDIT')
	#disable x-axis mirror edit
	bpy.context.active_object.data.use_mirror_x = False
	
	#Active all layers
		#save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):
		if bpy.context.active_object.data.layers[i] == True:	 
			layers_select.append(True)
		else:
			layers_select.append(False)		   
	
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True		

	
	bpy.ops.object.mode_set(mode='EDIT')
	
	#MULTI LIMBS SUPPORT------------------------
	#find if there are duplicated ref chains
	multi_ref_list = []
	
	for bone in bpy.context.active_object.data.edit_bones:
		if "shoulder_ref_dupli" in bone.name:
			multi_ref_list.append("_" + bone.name[-11:]) 
				


	for i in multi_ref_list:
		sides.append(i)#add this limb for align 
	
		
	bpy.ops.object.mode_set(mode='EDIT')
	#MULTI LIMBS SUPPORT------------------------
	
	#START ALIGNING BONES
	for side in sides:
		for bone in arms:
			#init_selection(bone+side)
			current_arm = get_bone(bone+side)
			ref_arm = get_bone(arm_name+side)
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
						current_arm.head = ref_arm.head + (ref_arm.tail-ref_arm.head)*0.5
						current_arm.tail = ref_arm.tail		
					
			
				
			if 'c_arm_fk' in bone:
				shoulder_ref = get_bone(shoulder_name+side)
				if shoulder_ref.parent != None:
					current_arm.parent = get_bone('c_' + shoulder_ref.parent.name.replace('_ref.x', '.x'))
				else:
					current_arm.parent = get_bone('c_traj')
					
	 
	
	# stretch controller
	for side in sides:
		arm = get_bone(arm_name+side)
		stretch_arm = get_bone(stretch_arm_name+side)	   
		dir = stretch_arm.tail - stretch_arm.head
		stretch_arm.head = arm.tail
		stretch_arm.tail = stretch_arm.head + dir
		
	# arm pin controller	
		stretch_arm_pin = get_bone("c_stretch_arm_pin"+side)		   
		dir = stretch_arm.tail - stretch_arm.head
		stretch_arm_pin.head = arm.tail
		stretch_arm_pin.tail = stretch_arm_pin.head + (dir*0.05)		  
		
	#arms	
		for bone in forearms:		   
			current_arm = get_bone(bone+side)
			ref_arm = get_bone(forearm_name+side)		

			if not 'stretch' in bone and not 'twist' in bone:
				current_arm.head = ref_arm.head
				current_arm.tail = ref_arm.tail		
			
			else:
				if 'twist' in bone:
					current_arm.head = ref_arm.head + (ref_arm.tail-ref_arm.head)*0.5
					current_arm.tail = ref_arm.tail					
				if 'stretch' in bone:
					current_arm.head = ref_arm.head
					current_arm.tail = ref_arm.head + (ref_arm.tail-ref_arm.head)*0.5
				
				
		
		for bone in shoulders:			
			current_bone = get_bone(bone+side)
			ref_bone = get_bone(shoulder_name+side)		
			current_bone.head = ref_bone.head
			current_bone.tail = ref_bone.tail
			current_bone.roll = ref_bone.roll 
			#parent bone
			if 'c_' in bone:
				if ref_bone.parent != None:
					current_bone.parent = get_bone('c_' + ref_bone.parent.name.replace('_ref.x', '.x'))
				else:
					current_bone.parent = get_bone('c_traj')
				
		
		# align secondary bones
	for side in sides:
		for bone in arm_bends:		 
			init_selection(bone+side)
			current_bone = get_bone(bone+side)
			arm = get_bone(arm_name+side)
			ref_arm = get_bone(forearm_name+side) 
			length = 0.07
			
			if "shoulder" in bone: 
				current_bone.head = arm.head + (arm.tail-arm.head) * 0.3
				current_bone.tail = current_bone.head - arm.z_axis * (length*arm.length*4)
			if "c_arm_bend" in bone: 
				arm_vec = arm.tail - arm.head
				current_bone.head = arm.head + arm_vec*0.6
				current_bone.tail = current_bone.head - arm.z_axis * (length*arm.length*4)
			if "elbow" in bone:			   
				current_bone.head = arm.tail
				current_bone.tail = current_bone.head - arm.z_axis * (length*arm.length*4)
			if "forearm" in bone:			 
				arm_vec = ref_arm.tail - ref_arm.head
				current_bone.head = ref_arm.head + arm_vec*0.5
				current_bone.tail = current_bone.head - ref_arm.z_axis * (length*arm.length*4)
			if "wrist" in bone: 
				current_bone.head = ref_arm.tail - ref_arm.y_axis * 0.025
				current_bone.tail = current_bone.head - ref_arm.z_axis * (length*arm.length*4)
			
			#set roll
			if side == '.l':
				bpy.ops.armature.calculate_roll(type='POS_Z')	
			else:
				bpy.ops.armature.calculate_roll(type='NEG_Z')	
  
	for side in sides:
		#align FK pre-pole	 
		prepole = get_bone(prepole_name + side)
		arm =  get_bone(arm_name + side)
		forearm =  get_bone(forearm_name + side)
	
			# center the prepole in the middle of the chain	   
		prepole.head[0] = (arm.head[0] + forearm.tail[0])/2
		prepole.head[1] = (arm.head[1] + forearm.tail[1])/2
		prepole.head[2] = (arm.head[2] + forearm.tail[2])/2
			# point toward the elbow
		prepole.tail[0] = arm.tail[0]
		prepole.tail[1] = arm.tail[1]
		prepole.tail[2] = arm.tail[2]
			
	
		#align FK pole	   
		fk_pole = get_bone(fk_pole_name + side)
			#get arm plane normal
		plane_normal = (arm.head - forearm.tail)
			#pole position
		prepole_dir = prepole.tail - prepole.head
		pole_pos = prepole.head + prepole_dir * 14
			#ortho project onto plane to align with the knee/elbow	
		pole_pos = project_point_onto_plane(pole_pos, prepole.tail, plane_normal)
		
		fk_pole.head = pole_pos#prepole.head + prepole_dir * 14
		fk_pole.tail = Vector((pole_pos)) + prepole_dir #prepole.tail + prepole_dir * 14	
		
	
		#align IK pole			
		ik_pole = get_bone(ik_pole_name + side)		   
		ik_pole.head = fk_pole.head
		ik_pole.tail = [ik_pole.head[0], ik_pole.head[1], ik_pole.head[2]+(0.1 * arm.length*2)]	  

   
		# arm and forearm roll adjust
	for side in sides:
		init_selection(forearm_name+side)		 
		bpy.ops.armature.calculate_roll(type='POS_Z')			
		bpy.ops.object.mode_set(mode='POSE')
		bpy.ops.pose.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='EDIT')
		arm =  get_bone(arm_name + side)
		arm.select = True	
		bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[forearm_name+side].bone	
		bpy.ops.armature.calculate_roll(type='ACTIVE') 
		if side[-2:] == ".r":
			get_bone(forearm_name+side).roll += math.radians(-180)
			get_bone(arm_name+side).roll += math.radians(-180)

	for side in sides:
		init_selection("null")
		#copy the roll to other bones			
		forearm =  get_bone(forearm_name + side)
		arm =  get_bone(arm_name + side)
		
		for bone in forearms:		 
			current_bone = get_bone(bone+side).select = True
			get_bone(bone+side).roll = forearm.roll			  
		
		for bone in arms:
			get_bone(bone+side).roll = arm.roll	  
	
		# shoulder poles	   
			#track pole		   
		shoulder_track_pole = get_bone(shoulder_track_pole_name + side)		   
		shoulder_track_pole.select = True		  
		shoulder_track_pole.head = (arm.head + get_bone(shoulder_name+side).head)/2
		shoulder_track_pole.head[2] += (0.04*arm.length*4)
		dir = forearm.head - shoulder_track_pole.head
		shoulder_track_pole.tail = shoulder_track_pole.head + dir / 4		 
		shoulder_track_pole.roll = arm.roll

	
		#shoulder visual position			
		p_shoulder = get_bone("c_p_shoulder"+side)
		shoulder = get_bone("c_shoulder"+side)
		is_dupli = False
		
		if get_bone("c_breast_02"+side) != None:
			breast_02 = get_bone("c_breast_02"+side)
		else:#no breast found, it's a duplicated arm, skip it
			is_dupli = True
	
		p_shoulder.head = (shoulder.head + shoulder.tail)/2
		p_shoulder.head[2] += 0.05
		if bpy.context.active_object.rig_breast and is_dupli == False:
			try:
				p_shoulder.head[1] = breast_02.head[1]
			except:
				print('Error with ', p_shoulder, breast_02)
		else:
			p_shoulder.head[1] += -0.08
		p_shoulder.tail = p_shoulder.head + (shoulder.tail-shoulder.head)/2
		p_shoulder.tail[2] = p_shoulder.head[2]
		p_shoulder.roll = math.radians(180)	 
		mirror_roll("c_p_shoulder"+side, side)

	
		# pole		  
		shoulder_pole = get_bone(shoulder_pole_name + side)		   
		shoulder_pole.head = arm.head + arm.z_axis * (-0.1 * arm.length*4)
		shoulder_pole.tail = arm.head + arm.z_axis * (-0.1*arm.length*4) + arm.y_axis * (0.1*arm.length*4)	   
	 

	
	# reset stretchy bone length
	
	bpy.ops.object.mode_set(mode='POSE')	
	bpy.ops.object.mode_set(mode='OBJECT')	 
	bpy.ops.object.mode_set(mode='POSE')	 
	
	#reset the stretch
	
	for side in sides:
		#ik
		arm_ik_p = get_pose_bone("arm_ik"+side)
		forearm_ik_p = get_pose_bone("forearm_ik"+side)
		arm_ik_length = arm_ik_p.length
		forearm_ik_length = forearm_ik_p.length
		
		if arm_ik_length < forearm_ik_length:
			arm_ik_p.ik_stretch = (arm_ik_length ** (1 / 3)) / (forearm_ik_length ** (1 / 3))
			forearm_ik_p.ik_stretch = 1.0
		else:
			arm_ik_p.ik_stretch = 1.0
			forearm_ik_p.ik_stretch = (forearm_ik_length ** (1 / 3)) / (arm_ik_length ** (1 / 3))
					  
	
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	for side in sides:
		# align hand_rot_twist			
		hand =	get_bone(hand_name + side)
		hand_rot_twist = get_bone(hand_rot_twist_name + side)
		forearm = bpy.context.active_object.data.edit_bones[forearm_name + side]	 
		
		
		hand_rot_twist.head = hand.head + (hand.y_axis * 0.02 * hand.length*15) + (hand.z_axis * 0.04 * hand.length*15)#mult by hand.length to keep proportional when scaling the armature object and applying scale
		hand_rot_twist.tail = hand_rot_twist.head + (forearm.y_axis * 0.02 * hand.length*15)
		hand_rot_twist.roll = forearm.roll
		

	
		# align hands
		hands = ["hand"+side, "c_hand_ik"+side, "c_hand_fk"+side, "c_hand_fk_scale_fix"+side]

		for bone in hands:			
			current_hand = bpy.context.active_object.data.edit_bones[bone]
			ref_hand = bpy.context.active_object.data.edit_bones[hand_name + side]
			current_hand.head = ref_hand.head
			current_hand.tail = ref_hand.tail
			current_hand.roll = ref_hand.roll

			
	# align fingers
	for side in sides:
		fingers = []
		hand_def = get_bone("hand" + side)
		init_selection(hand_def.name)
		bpy.ops.armature.select_similar(type='CHILDREN')
		if side[-2:] == ".l":
			opposite = ".r"
		else:
			opposite = ".l"
			
		for bone in bpy.context.selected_editable_bones[:]:
			if not "hand" in bone.name and not opposite in bone.name:#fingers only and one side only
				fingers.append(bone.name)

		for finger in fingers:		  
			init_selection(finger)
		   
			substract = 0
			if len(side) > 2:
				 substract = 10
		
			bone_name = finger[2:-2-substract]+"_ref"+ side
		   
			
			if "bend_all" in finger: #exception for the "bend_all" fingers to find the ref name
				bone_name = finger[:-11-substract]+"1_ref"+ side		 
			if "thumb1_base" in finger: #thumb1 base case
				bone_name = "thumb1_ref"+ side
			if "_rot." in finger or "_rot_" in finger: # rotation bone case
				bone_name = finger[2:-6-substract] + "_ref" + side
				
			bone_ref = get_bone(bone_name)
	   
			if get_bone(finger) != None and bone_ref != None:
				current_bone = get_bone(finger)
				current_bone.head = bone_ref.head
				current_bone.tail = bone_ref.tail
				current_bone.roll = bone_ref.roll  
  
   
   
	#display layers 16, 0, 1 only	
	_layers = bpy.context.active_object.data.layers
		#must enabling one before disabling others
	_layers[16] = True	
	for i in range(0,32):
		if i != 16:
			_layers[i] = False 
	_layers[0] = True
	_layers[1] = True	
			
	bpy.ops.object.mode_set(mode='POSE')			 
	bpy.context.active_object.data.pose_position = 'POSE'	 
	
	#reset the proxy picker state
	try:
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state
	except:
		pass
	
	if debug_print == True:	   
		print("\n FINISH ALIGNING ARM BONES...\n")

def mirror_roll(bone, side):
	if side[-2:] == ".r":
		get_bone(bone).roll *= -1

def _align_leg_bones():
	
	
	print("\n Aligning leg bones...\n")
	
	#disable the proxy picker to avoid bugs
	
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	  
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass	
	
	#define the side
	sides = [".l", ".r"]	
	 
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
	
	thighs = ["c_thigh_fk", "thigh_fk", "thigh_ik_nostr", "thigh_ik", "thigh_twist", "thigh_stretch", "thigh"]
	
	feet = ["foot", "foot_fk", "c_foot_fk", "foot_ik", "c_foot_ik", "foot_snap_fk", "foot_ik_target", "c_foot_bank_01", "c_foot_bank_02", "c_foot_heel", "c_foot_01"]
		
	leg_bends = ["c_thigh_bend_contact", "c_thigh_bend_01", "c_thigh_bend_02", "c_knee_bend", "c_leg_bend_01", "c_leg_bend_02", "c_ankle_bend"]
	
		
	bpy.ops.object.mode_set(mode='EDIT')
	#enable x-axis mirror edit
	bpy.context.active_object.data.use_mirror_x = False
	
	#Active all layers
		#save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):
		if bpy.context.active_object.data.layers[i] == True:	 
			layers_select.append(True)
		else:
			layers_select.append(False)

	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True 

	#MULTI LIMBS SUPPORT------------------------
	#find if there are duplicated ref chains
	multi_ref_list = []
	
	for bone in bpy.context.active_object.data.edit_bones:
		if "thigh_ref_dupli" in bone.name:
			multi_ref_list.append("_" + bone.name[-11:]) 
				

	for i in multi_ref_list:
		sides.append(i)#add this limb for align 
	
		
	bpy.ops.object.mode_set(mode='EDIT')
	#MULTI LIMBS SUPPORT------------------------

	#align every legs and thighs bones types with references locations
	for side in sides:
		for bone in thighs:			 
			current_bone = get_bone(bone+side)
			ref_bone = get_bone(thigh_name+side)
			
			if not 'twist' in bone and not 'stretch' in bone:			
				current_bone.head = ref_bone.head
				current_bone.tail = ref_bone.tail	
			
			else:
				if 'twist' in bone:
					current_bone.head = ref_bone.head
					current_bone.tail = ref_bone.head + (ref_bone.tail-ref_bone.head)*0.5					
				if 'stretch' in bone:
					current_bone.head = ref_bone.head + (ref_bone.tail-ref_bone.head)*0.5
					current_bone.tail = ref_bone.tail					
		
		#stretch bone		  
		stretch_leg = get_bone(stretch_leg_name+side)
		thigh = get_bone(thigh_name+side)
		dir = stretch_leg.tail - stretch_leg.head
		stretch_leg.head = thigh.tail
		stretch_leg.tail = stretch_leg.head + dir	   

		# pin controller	   
		stretch_leg_pin = get_bone("c_stretch_leg_pin"+side)
		thigh = get_bone(thigh_name+side)
		dir = stretch_leg_pin.tail - stretch_leg_pin.head
		stretch_leg_pin.head = thigh.tail
		stretch_leg_pin.tail = stretch_leg_pin.head + dir
	  
		
		for bone in legs:		   
			current_bone = get_bone(bone+side)
			ref_bone = get_bone(leg_name+side)	
			if not 'stretch' in bone and not 'twist' in bone:
				current_bone.head = ref_bone.head
				current_bone.tail = ref_bone.tail
			else:
				if 'twist' in bone:
					current_bone.head = ref_bone.head + (ref_bone.tail-ref_bone.head)*0.5
					current_bone.tail = ref_bone.tail					
				if 'stretch' in bone:
					current_bone.head = ref_bone.head
					current_bone.tail = ref_bone.head + (ref_bone.tail-ref_bone.head)*0.5
				
				
	
	for side in sides:	  
		# align secondary bones
		for bone in leg_bends:
			init_selection(bone+side)
			current_bone = get_bone(bone+side)
			thigh = get_bone(thigh_name+side)
			leg = get_bone(leg_name+side)
			thigh_vec = thigh.tail - thigh.head
			leg_vec = leg.tail - leg.head
			length = 0.04
			
			if "contact" in bone: 
				current_bone.head = thigh.head + thigh_vec*0.15
				current_bone.tail = current_bone.head + (thigh.y_axis * length * leg.length*3)
			if "thigh_bend_01" in bone:			   
				current_bone.head = thigh.head + thigh_vec*0.4
				#current_bone.head[0] += -0.03
				current_bone.tail = current_bone.head + (thigh.y_axis * length * leg.length*3)
			if "thigh_bend_02" in bone:			   
				current_bone.head = thigh.head + thigh_vec*0.75
				current_bone.tail = current_bone.head + (thigh.y_axis * length * leg.length*3)
			if "knee" in bone:			  
				current_bone.head = thigh.tail
				current_bone.tail = current_bone.head + (thigh.y_axis * length * leg.length*3)
				
			if "leg_bend_01" in bone:			
				current_bone.head = leg.head + leg_vec*0.25
				current_bone.tail = current_bone.head + (leg.y_axis * length * leg.length*3)
				
			if "leg_bend_02" in bone:			
				current_bone.head = leg.head + leg_vec*0.5
				current_bone.tail = current_bone.head + (leg.y_axis * length * leg.length*3)
				
			if "ankle" in bone: 
				current_bone.head = leg.head + leg_vec*0.85
				current_bone.tail = current_bone.head + (leg.y_axis * length * leg.length*3)
				
			
				
			#set roll
			bpy.ops.armature.calculate_roll(type='POS_X')

	def norm(x):
		return math.sqrt(x.dot(x))
	 
	def project_onto_plane(x, n):
		#x = point coord (vector3)
		#n = plane normal (vector3)	
		d = x.dot(n) / norm(n)
		p = [d * n.normalized()[i] for i in range(len(n))]
		return [x[i] - p[i] for i in range(len(x))] 
	
	 
	for side in sides:	 
		
		prepole = get_bone(prepole_name + side)
		thigh =	 get_bone(thigh_name + side)
		leg = get_bone(leg_name + side)
		
		# center the prepole in the middle of the chain	   
		prepole.head[0] = (thigh.head[0] + leg.tail[0])/2
		prepole.head[1] = (thigh.head[1] + leg.tail[1])/2
		prepole.head[2] = (thigh.head[2] + leg.tail[2])/2
		# point toward the knee
		prepole.tail[0] = thigh.tail[0]
		prepole.tail[1] = thigh.tail[1]
		prepole.tail[2] = thigh.tail[2]			
		
			
		#align FK pole	   
		fk_pole = get_bone(fk_pole_name + side)
			#get legs plane normal
		plane_normal = (thigh.head - leg.tail)
			#pole position		
		prepole_dir = prepole.tail - prepole.head
		pole_pos = prepole.head + prepole_dir * 14
			#ortho project onto plane to align with the knee/elbow	
		pole_pos = project_point_onto_plane(pole_pos, prepole.tail, plane_normal)
		
		fk_pole.head = pole_pos#prepole.head + prepole_dir * 14
		fk_pole.tail = Vector((pole_pos)) + prepole_dir #prepole.tail + prepole_dir * 14			
	
		#align IK pole		 
		fk_pole = get_bone(fk_pole_name + side)
		ik_pole = get_bone(ik_pole_name + side)		   
		ik_pole.head = fk_pole.head
		ik_pole.tail = [ik_pole.head[0], ik_pole.head[1], ik_pole.head[2]+(0.1*thigh.length*2)]	   
		  

	for side in sides:
		# thigh and leg roll adjust
		init_selection(leg_name+side)		 
		bpy.ops.armature.calculate_roll(type='POS_Z')
		init_selection("null")	
		thigh = get_bone(thigh_name + side)
		thigh.select = True	  
		bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[leg_name+side].bone	
		bpy.ops.armature.calculate_roll(type='ACTIVE')
		if side[-2:] == ".r":
			get_bone(leg_name+side).roll += math.radians(-180)
			get_bone(thigh_name+side).roll += math.radians(-180)
				  
		
	init_selection("null")	   
	 
	for side in sides:
		#copy the roll to other bones		   
		leg =  get_bone(leg_name + side)
		thigh =	 get_bone(thigh_name + side)
		
		for bone in legs:	 
			get_bone(bone+side).roll = leg.roll						  
		
		for bone in thighs:
			get_bone(bone+side).roll = thigh.roll				
	
	
		# foot poles			   
		foot_pole = get_bone(foot_pole_name + side)	 
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
			if foot == "foot_fk" or foot == "foot_ik" or foot == "foot":			   
				current_foot = get_bone(foot+side)
				foot_ref = get_bone(foot_name + side)
				current_foot.head = foot_ref.head
				current_foot.tail = foot_ref.tail
				current_foot.roll = foot_ref.roll
			  
			if foot == "c_foot_fk" or foot == "c_foot_ik" or foot == "foot_snap_fk" or foot == "c_foot_fk_scale_fix":			   
				current_foot = bpy.context.active_object.data.edit_bones[foot+side]
				heel_ref = get_bone('foot_heel_ref'+side)
				toes_ref = get_bone(toes_name + side)	 
				foot_ref = get_bone(foot_name + side)
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
				current_foot = get_bone(foot+side)
				foot_ref = get_bone(foot_name + side)
				current_foot.head = foot_ref.tail
				current_foot.tail = current_foot.head + (foot_ref.tail - foot_ref.head)/2
				current_foot.roll = foot_ref.roll
				#mirror_roll(foot+side, side)
				 
		 
			
			
		#align foot_01_pole		 
		current_foot = get_bone("foot_01_pole"+side)
		c_foot_01 = get_bone("c_foot_01"+side)
		current_foot.head = c_foot_01.head + (c_foot_01.z_axis * 0.05 * c_foot_01.length * 40)
		current_foot.tail = current_foot.head + (c_foot_01.z_axis * 0.05 * c_foot_01.length * 40)
		current_foot.roll = math.radians(180)
		mirror_roll("foot_01_pole"+side, side)
	   
		#align foot visual position
		foot_ref = get_bone(foot_name + side)
		heel_ref = get_bone("foot_heel_ref" + side)
		p_foots = ["c_p_foot_ik", "c_p_foot_fk"]
		
		for p_f in p_foots:
			try:
				p_foot = get_bone(p_f + side)			 
				p_foot.head = heel_ref.head
				
				p_foot.tail = heel_ref.tail
				p_foot.roll = get_bone('foot_heel_ref'+side).roll + math.radians(-90)
				if side [-2:] == '.r':
					p_foot.roll += math.radians(180)				
				
			except:
				pass
	
	# align toes
	toes = ["c_toes_fk", "c_toes_ik", "toes_01_ik", "c_toes_track", "toes_02", "c_toes_end", "c_toes_end_01", "toes_01"]
	
	
	for side in sides:	   
		#normalize toes axes   
		toes_ref = get_bone(toes_name + side)
		foot_ref = get_bone(foot_name + side)
	
		#toes_end_ref = get_bone("toes_end_ref"+side)
		#toes_end_ref.head[0] = toes_ref.tail[0]
		#toes_end_ref.tail[0] = toes_ref.tail[0]		 
		
		for bone in toes:
			
			if bone == "c_toes_end":		
				current_bone = get_bone(bone+side)			
				current_bone.head = toes_ref.tail
				current_bone.tail = current_bone.head + (toes_ref.tail - toes_ref.head)/2
				#current_bone.tail[2] = toes_ref.tail[2]
				#current_bone.roll = toes_ref.roll# + math.radians(180)	  
				bpy.ops.armature.select_all(action='DESELECT')
				bpy.context.active_object.data.edit_bones.active = current_bone	 
				bpy.context.active_object.data.edit_bones.active = toes_ref			
				bpy.ops.armature.calculate_roll(type='ACTIVE')
				current_bone.roll += math.radians(180)
			
				
			if bone == "c_toes_end_01":				 
				current_bone = get_bone(bone+side)	
				current_bone.head = toes_ref.tail
				current_bone.tail = current_bone.head + (toes_ref.z_axis * 0.035 * toes_ref.length * 6)
				current_bone.roll = math.radians(180)
				mirror_roll(bone+side, side)
			
			if bone == "c_toes_fk" or bone == "c_toes_track" or bone == "c_toes_ik":	 
				current_bone = get_bone(bone+side)							 
				current_bone.head = toes_ref.head
				current_bone.tail = toes_ref.tail
				current_bone.roll = toes_ref.roll + math.radians(180)
				if bone == 'c_toes_track':
					current_bone.roll += math.radians(-90)
				
				
	for side in sides:	  
		for bone in toes:
		
			if bone == "toes_01_ik" or bone == "toes_01":
				init_selection(bone+side)
				toes_ref = get_bone(toes_name + side)		
				current_bone = get_bone(bone+side)
				c_toes_fk = bpy.context.active_object.data.edit_bones["c_toes_fk"+side]
				current_bone.head = toes_ref.head
				dir = c_toes_fk.tail - c_toes_fk.head
				current_bone.tail = current_bone.head + dir/3
				bpy.ops.armature.select_all(action='DESELECT')
				bpy.context.active_object.data.edit_bones.active = current_bone	 
				bpy.context.active_object.data.edit_bones.active = toes_ref			
				bpy.ops.armature.calculate_roll(type='ACTIVE')
				current_bone.roll += math.radians(180)
				#current_bone.roll = toes_ref.roll
				#bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')		   
				#print(br)
			if bone == "toes_02":
				init_selection(bone+side)
				toes_ref = get_bone(toes_name + side)		
				toes_01_ik = get_bone("toes_01_ik" + side)
				current_bone = get_bone(bone+side)
				c_toes_fk = get_bone("c_toes_fk"+side)
				current_bone.head = toes_01_ik.tail			   
				current_bone.tail = c_toes_fk.tail
				#current_bone.roll = toes_ref.roll
				bpy.ops.armature.select_all(action='DESELECT')
				bpy.context.active_object.data.edit_bones.active = current_bone	 
				bpy.context.active_object.data.edit_bones.active = toes_ref			
				bpy.ops.armature.calculate_roll(type='ACTIVE')
				current_bone.roll = toes_ref.roll + math.radians(180)
				#bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')

			
	# toes fingers
	obj = bpy.context.active_object
	toes_bool_list = [obj.rig_toes_pinky, obj.rig_toes_ring, obj.rig_toes_middle, obj.rig_toes_index, obj.rig_toes_thumb]
	toes_list=["toes_pinky", "toes_ring", "toes_middle", "toes_index", "toes_thumb"]
 

	for side in sides:
		for t in range (0,5): 
			if toes_bool_list[t]:# if property true
				max = 4
				if t == 4:
					max = 3#thumb case
				for i in range (1,max):			   
					ref_bone = toes_list[t]+str(i)+"_ref" +side		  
					c_bone = "c_"+toes_list[t]+str(i)+side 
					if get_bone(ref_bone) != None and get_bone(c_bone) != None:
						copy_bone_transforms(get_bone(ref_bone), get_bone(c_bone))
			
			
	#foot roll
	for side in sides:		 
		toes_ref = get_bone(toes_name+side)
		heel_ref = get_bone('foot_heel_ref'+side)
		c_foot_roll = get_bone("c_foot_roll"+side)
		c_foot_roll.head = heel_ref.head - heel_ref.y_axis*(toes_ref.head-toes_ref.tail).length*2
		#c_foot_roll.head[2] = foot_ref.tail[2]
		#c_foot_roll.head[1] += 0.23
		c_foot_roll.tail = c_foot_roll.head - heel_ref.y_axis*(toes_ref.head-toes_ref.tail).length*0.6
		#c_foot_roll.roll = toes_ref.roll
		#c_foot_roll.tail[1] += -0.06
		bpy.ops.armature.select_all(action='DESELECT')
		bpy.context.active_object.data.edit_bones.active = c_foot_roll	 
		bpy.context.active_object.data.edit_bones.active = toes_ref			
		bpy.ops.armature.calculate_roll(type='ACTIVE')
		c_foot_roll.roll += math.radians(-90+180)
	
		#cursor bank roll		
		c_foot_roll_cursor = get_bone("c_foot_roll_cursor"+side)
		c_foot_roll_cursor.head = c_foot_roll.tail - (c_foot_roll.x_axis*c_foot_roll.length)
		
		#c_foot_roll_cursor.head[2] += 0.08
		c_foot_roll_cursor.tail = c_foot_roll_cursor.head - (c_foot_roll.tail - c_foot_roll.head)
		#c_foot_roll_cursor.tail[2] += 0.08
		#c_foot_roll_cursor.roll = toes_ref.roll + math.radians(90+180)
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
		thigh_ref = get_bone(thigh_name+side)
		if thigh_ref.parent != None:
			c_thigh_b.parent = get_bone('c_' + thigh_ref.parent.name.replace('_ref.x', '.x'))
		else:
			c_thigh_b.parent = get_bone('c_traj')
		
		 

	
	#POSE MODE ONLY
	# reset stretchy bone length
	bpy.ops.object.mode_set(mode='OBJECT')	 
	bpy.ops.object.mode_set(mode='POSE')	 

	#reset the stretch

	for side in sides:
		#ik
		thigh_ik_p = get_pose_bone("thigh_ik"+side)
		leg_ik_p = get_pose_bone("leg_ik"+side)
		thigh_ik_length = thigh_ik_p.length
		leg_ik_length = leg_ik_p.length
		
		if thigh_ik_length < leg_ik_length:
			thigh_ik_p.ik_stretch = (thigh_ik_length ** (1 / 3)) / (leg_ik_length ** (1 / 3))
			leg_ik_p.ik_stretch = 1.0
		else:
			thigh_ik_p.ik_stretch = 1.0
			leg_ik_p.ik_stretch = (leg_ik_length ** (1 / 3)) / (thigh_ik_length ** (1 / 3))
		
 
	
	#display layers 16, 0, 1 only	
	_layers = bpy.context.active_object.data.layers
		#must enabling one before disabling others
	_layers[16] = True	
	for i in range(0,32):
		if i != 16:
			_layers[i] = False 
	_layers[0] = True
	_layers[1] = True	
				 
	bpy.context.active_object.data.pose_position = 'POSE'

	#reset the proxy picker state
	try:
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state
	except:
		pass
	
	if debug_print == True:	   
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
	 
	#unit scale
	unit_scale = 1.0
	
	if bpy.context.scene.unit_settings.system != 'NONE':
		unit_scale = 1/bpy.context.scene.unit_settings.scale_length
   
	
	#disable the proxy picker to avoid bugs	  
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	  
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass   

	rig = bpy.context.active_object
	rig_add = get_rig_add(rig)
	
	#define the side
	sides = [".l",".r"]	   
	 
	#get reference bones
	root_name = "root_ref.x"
	spine_01_name = "spine_01_ref.x"
	spine_02_name = "spine_02_ref.x"  
	neck_name = "neck_ref.x"  
	head_name = "head_ref.x"
	jaw_name = "jaw_ref.x"
	eye_name = "eye_ref"
	bot_bend_name = "bot_bend_ref"
	
	bpy.ops.object.mode_set(mode='EDIT')
	#enable x-axis mirror edit
	bpy.context.active_object.data.use_mirror_x = False
	
	#select all layers
		#save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):
		if bpy.context.active_object.data.layers[i] == True:	 
			layers_select.append(True)
		else:
			layers_select.append(False)
		
	#display all layers for mirror to work
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True
		
		
	#align root master
	init_selection("c_root_master.x")
	c_root_master = bpy.context.active_object.data.edit_bones["c_root_master.x"]
	c_root_ref = bpy.context.active_object.data.edit_bones[root_name]
	p_root_master = bpy.context.active_object.data.edit_bones["c_p_root_master.x"]
	
	copy_bone_transforms(c_root_ref, c_root_master)
	#get_pose_bone("c_root_master.x").custom_shape_scale = (0.1 / c_root_master.length)#*unit_scale
	
		# set the visual shape position
	dir = c_root_ref.tail - c_root_ref.head
	p_root_master.head = c_root_master.head# + (c_root_master.tail-c_root_master.head)/2	 
	p_root_master.tail = p_root_master.head + dir/1.5
		# set the bone vertical if not quadruped
	if not bpy.context.active_object.rig_type == 'quadruped' and not p_root_master.head[2] == p_root_master.tail[2]:
		p_root_master.tail[1] = p_root_master.head[1]

	
	#align root
	init_selection("c_root.x")
	c_root = bpy.context.active_object.data.edit_bones["c_root.x"]
	root = bpy.context.active_object.data.edit_bones["root.x"]
	c_root_ref = bpy.context.active_object.data.edit_bones[root_name]
	p_root = bpy.context.active_object.data.edit_bones["c_p_root.x"]
	
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
	root_bend = get_bone("c_root_bend.x")
	dir = root_bend.tail - root_bend.head	 
	root_bend.head = c_root.head +(c_root.tail - c_root.head)/2
	root_bend.tail = root_bend.head + dir
	root_bend.roll = 0
	
	 #align bot_bend
	sides = ['.l', '.r']
	for side in sides:
		bot_ref = bpy.context.active_object.data.edit_bones[bot_bend_name+side]
		c_bot_bend = bpy.context.active_object.data.edit_bones["c_bot_bend"+side]
		dir = bot_ref.tail - bot_ref.head
		c_bot_bend.head = bot_ref.head	 
		c_bot_bend.tail = bot_ref.tail - dir/2	
	
	# align tail if any
	if bpy.context.active_object.rig_tail:
		tails = ["tail_00", "tail_01", "tail_02", "tail_03"]
		
		for bone in tails:			  
			copy_bone_transforms(get_bone(bone+"_ref.x"), get_bone("c_"+bone+".x"))
			 #parent
			if 'tail_00' in bone:
				tail_ref = get_bone(bone+"_ref.x")
				try:				
					get_bone('c_' + bone + '.x').parent = get_bone('c_' + tail_ref.parent.name.replace('_ref.x', '.x'))
				except:
					print('Invalid tail parent, replace by root')
					get_bone('c_' + bone + '.x').parent = get_bone('c_root.x')
	

	#align spine 01
	init_selection("c_spine_01.x")
	c_spine_01 = bpy.context.active_object.data.edit_bones["c_spine_01.x"]
	spine_01 = bpy.context.active_object.data.edit_bones["spine_01.x"]
	spine_01_ref = bpy.context.active_object.data.edit_bones[spine_01_name]
	p_spine_01 = bpy.context.active_object.data.edit_bones["c_p_spine_01.x"]
	
	copy_bone_transforms(spine_01_ref, c_spine_01)
	copy_bone_transforms(c_spine_01, spine_01) 
	
		# set the visual shape position
	p_spine_01.head = c_spine_01.head	
	p_spine_01.tail = p_spine_01.head + (c_spine_01.tail-c_spine_01.head)
	p_spine_01.roll = c_spine_01.roll
	# set the bone vertical if not quadruped
	if not bpy.context.active_object.rig_type == 'quadruped' and not p_spine_01.head[2] == p_spine_01.tail[2]:
		p_spine_01.tail[1] = p_spine_01.head[1]
	
	
	
		#waist bend
	waist_bend = get_bone("c_waist_bend.x")
	waist_bend.head = p_spine_01.head
	waist_bend.tail = p_spine_01.tail - (p_spine_01.tail - p_spine_01.head)/2
	waist_bend.roll = 0
	#get_pose_bone("c_waist_bend.x").custom_shape_scale = (0.15 / p_spine_01.length)#*unit_scale
		#spine_01_bend
	spine_01_bend = get_bone("c_spine_01_bend.x")
	spine_01_bend.head = p_spine_01.tail + (p_spine_01.head - p_spine_01.tail)*0.5
	spine_01_bend.tail = spine_01_bend.head - (p_spine_01.tail - p_spine_01.head)/2
	spine_01_bend.roll = 0
	#get_pose_bone("c_spine_01_bend.x").custom_shape_scale = (0.075 / spine_01_bend.length)#*unit_scale
	
	 #align spine 02
	init_selection("c_spine_02.x")
	c_spine_02 = bpy.context.active_object.data.edit_bones["c_spine_02.x"]
	spine_02 = bpy.context.active_object.data.edit_bones["spine_02.x"]
	spine_02_ref = bpy.context.active_object.data.edit_bones[spine_02_name]
	p_spine_02 = bpy.context.active_object.data.edit_bones["c_p_spine_02.x"]
	
	copy_bone_transforms(spine_02_ref, c_spine_02) 
	copy_bone_transforms(c_spine_02, spine_02)	
	
	# align spine 03
	try:
		copy_bone_transforms(get_bone('spine_03_ref.x'), get_bone('spine_03.x')) 
		copy_bone_transforms(get_bone('spine_03_ref.x'), get_bone('c_spine_03.x'))
		#get_pose_bone("c_spine_03.x").custom_shape_scale = (0.1 / get_bone('spine_03_ref.x').length)#*unit_scale
	except:
		pass
	
		# set the visual shape position
	p_spine_02.head = c_spine_02.head# + (c_spine_02.tail - c_spine_02.head)/2
	p_spine_02.tail = p_spine_02.head + (c_spine_02.tail-c_spine_02.head)*0.5
	p_spine_02.roll = c_spine_02.roll
	# set the bone vertical if not quadruped
	if not bpy.context.active_object.rig_type == 'quadruped' and not p_spine_02.head[2] == p_spine_02.tail[2]:
		p_spine_02.tail[1] = p_spine_02.head[1]
 
	
		#spine_02_bend
	spine_02_bend = get_bone("c_spine_02_bend.x")
	spine_02_bend.head = p_spine_02.tail# + (p_spine_02.tail - p_spine_02.head)*0.5
	spine_02_bend.tail = p_spine_02.head#spine_02_bend.head + (p_spine_02.tail - p_spine_02.head)*0.5
	spine_02_bend.roll = 0
	#get_pose_bone("c_spine_02_bend.x").custom_shape_scale = (0.08/ spine_02_bend.length)#*unit_scale
	
	#align neck	   
	init_selection("c_neck.x")
	c_neck = bpy.context.active_object.data.edit_bones["c_neck.x"]
	neck = bpy.context.active_object.data.edit_bones["neck.x"]
	c_neck_01 = bpy.context.active_object.data.edit_bones["c_neck_01.x"]
	p_neck = bpy.context.active_object.data.edit_bones["c_p_neck.x"]
	p_neck_01 = bpy.context.active_object.data.edit_bones["c_p_neck_01.x"]
	neck_ref = bpy.context.active_object.data.edit_bones[neck_name]	  
	
	copy_bone_transforms(neck_ref, c_neck) 
	copy_bone_transforms(neck_ref, neck) 
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
	
	#align head
	init_selection("c_head.x")
	c_head = bpy.context.active_object.data.edit_bones["c_head.x"]
	head_ref = bpy.context.active_object.data.edit_bones["head_ref.x"]
	head = bpy.context.active_object.data.edit_bones["head.x"]
	c_head_scale_fix = bpy.context.active_object.data.edit_bones["c_head_scale_fix.x"]
	c_p_head = get_bone("c_p_head.x") 
	
	copy_bone_transforms(head_ref, c_head)
	copy_bone_transforms(head_ref, head)
	copy_bone_transforms(head_ref, c_head_scale_fix)
		# set the visual shape position
	c_p_head.head = head.tail
	c_p_head.tail = c_p_head.head + (head.tail-head.head)/2
	c_p_head.roll = head.roll
	
	
	
		#skulls
		
	skulls = ["c_skull_01.x", "c_skull_02.x", "c_skull_03.x"]
	jaw_ref = bpy.context.active_object.data.edit_bones["jaw_ref.x"]	
	head_vec = head_ref.tail - head_ref.head
	head_jaw_vec = jaw_ref.tail - head_ref.tail
	project_vec = project_vector_onto_vector(head_jaw_vec, head_vec)
	
	i=0	
	for skull in skulls:
		skull_bone = bpy.context.active_object.data.edit_bones[skull]	
		
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
		
   #align facial
	if bpy.context.active_object.rig_facial:
		print('\n Aligning facial...')
		
		#jaw
		c_jaw = bpy.context.active_object.data.edit_bones["c_jawbone.x"]
		jaw_ref = bpy.context.active_object.data.edit_bones["jaw_ref.x"]	 
		copy_bone_transforms(jaw_ref, c_jaw)
	
		#cheeks
		cheeks = ["c_cheek_smile", "c_cheek_inflate"]

		for side in sides:
			for cheek in cheeks:		   
				cheek_ref = get_bone(cheek[2:]+"_ref"+side)
				cheek_bone = get_bone(cheek+side)
				copy_bone_transforms(cheek_ref, cheek_bone)
	   
		
			#nose
		noses = ["c_nose_01.x", "c_nose_02.x", "c_nose_03.x"]
		for nose in noses:
			nose_bone = bpy.context.active_object.data.edit_bones[nose]
			nose_ref = bpy.context.active_object.data.edit_bones[nose[2:-2]+"_ref.x"]
			copy_bone_transforms(nose_ref, nose_bone)
			
		chins = ["c_chin_01.x", "c_chin_02.x"]
		for chin in chins:
			bone = bpy.context.active_object.data.edit_bones[chin]
			ref_bone = get_bone(chin[2:-2]+"_ref.x")
			copy_bone_transforms(ref_bone, bone)
			
		# ears
		for side in sides:
			if bpy.context.active_object.rig_ears:
				ears_list=["ear_01", "ear_02"]
				for ear in ears_list:
					#copy_bone_transforms_mirror(ear+"_ref", "c_"+ear)
					if get_bone("c_"+ear+side) != None:
						bone = get_bone("c_"+ear+side)
						ref_bone = get_bone(ear+"_ref"+side)
						copy_bone_transforms(ref_bone, bone)
			
			#mouth
		tongs = ["c_tong_01.x", "c_tong_02.x", "c_tong_03.x"]
		for tong in tongs:		  
			current_bone = get_bone(tong)
			copy_bone_transforms(get_bone(tong[2:-2]+"_ref.x"), current_bone)
			copy_bone_transforms(get_bone(tong[2:-2]+"_ref.x"), get_bone(tong[2:]))
			
		teeth = ["c_teeth_top.x", "c_teeth_bot.x", 'c_teeth_top.l', 'c_teeth_top.r', 'c_teeth_bot.l', 'c_teeth_bot.r', 'c_teeth_top_master.x', 'c_teeth_bot_master.x']
		
		for tooth in teeth:
			try:
				current_bone = get_bone(tooth)		
				if not 'master' in tooth:		 
					copy_bone_transforms(get_bone(tooth.replace('.', '_ref.')[2:]), current_bone)
				if tooth == 'c_teeth_top_master.x':	   
					ref = get_bone('teeth_top_ref.x')
					current_bone.head = ref.head + (ref.head - ref.tail)/2
					current_bone.tail = ref.tail + (ref.head - ref.tail)/2
				if tooth == 'c_teeth_bot_master.x':	   
					ref = get_bone('teeth_bot_ref.x')
					current_bone.head = ref.head + (ref.head - ref.tail)/2
					current_bone.tail = ref.tail + (ref.head - ref.tail)/2
			except:
				print('Missing teeth skipped...')
			
		lips = ["c_lips_top.x", "c_lips_bot.x", "c_lips_top", "c_lips_top_01", "c_lips_bot", "c_lips_bot_01", "c_lips_smile", "c_lips_corner_mini", "c_lips_roll_top.x", "c_lips_roll_bot.x"]
		
		
		for lip in lips:
		   
			if lip[-2:] == ".x":
				ref_bone = get_bone(lip[2:-2]+"_ref.x")
				bone = get_bone(lip)			
				copy_bone_transforms(ref_bone, bone)
			else:
				for side in sides:				
					ref_bone = get_bone(lip[2:]+"_ref"+side)
					bone = get_bone(lip+side)			 
					copy_bone_transforms(ref_bone, bone)
				

			
			#eyes
				#make list of all eyes bones
		eyes = []
		init_selection("c_eye_offset.l")
		bpy.ops.armature.select_similar(type='CHILDREN')
		for bone in bpy.context.selected_editable_bones[:]:
			if not ".r" in bone.name:#left side only
				eyes.append(bone.name[:-2])	   
		
		
		
			#direct copy from ref
		for side in sides:
			for bone in eyes:		 
				try:
					bone_ref = get_bone(bone[2:]+"_ref"+ side)
					current_bone = bpy.context.active_object.data.edit_bones[bone+side]
					copy_bone_transforms(bone_ref, current_bone)
				except:
					pass
							  
				
				if "eyelid_top" in bone:
					
					copy_bone_transforms(get_bone("eyelid_top_ref"+side), get_bone("eyelid_top"+side))
				if "eyelid_bot" in bone:
					copy_bone_transforms(get_bone("eyelid_bot_ref"+side), get_bone("eyelid_bot"+side))		 
				
		eye_additions = ["c_eye", "c_eye_ref_track", "c_eyelid_base", "c_eye_ref"]
		
			#  additional bones	  
		for side in sides:
			for bone in eye_additions:	   
				
				current_bone = get_bone(bone+side)		
				eye_reference = get_bone("eye_offset_ref"+side)
				copy_bone_transforms(eye_reference, current_bone)
				
				if bone == 'c_eye_ref':
					current_bone.head = eye_reference.tail + (eye_reference.tail-eye_reference.head)
					current_bone.tail = current_bone.head
					current_bone.tail[2] += -0.006
				if bone == 'c_eye_ref_track':
					current_bone.tail = current_bone.head + (current_bone.tail-current_bone.head)/2
		   
		 
			# eye shape scale	 
		#get_pose_bone("c_eye.l").custom_shape_scale = (0.8*unit_scale)
		#get_pose_bone("c_eye.r").custom_shape_scale = 0.8*unit_scale
		
			# eye targets
		eye_target_x = get_bone("c_eye_target.x")
		for side in sides:
			eye_ref = get_bone("eye_offset_ref"+side)
				# .x
			eye_target_x.head = eye_ref.head
			eye_target_x.head[0] = 0.0
			eye_target_x.head[1] += -1
			eye_target_x.tail = eye_target_x.head
			eye_target_x.tail[2] += 0.028
		
			# .l and .r		 
			eye_target_side = get_bone("c_eye_target"+side) 
			if eye_ref.head[0] == eye_ref.tail[0] and eye_ref.head[2] == eye_ref.tail[2]:#if the eye is aligned vert/hor
				eye_target_side.head = eye_target_x.head
				eye_target_side.head[0] = eye_ref.head[0]
				eye_target_side.tail = eye_target_side.head
				eye_target_side.tail[2] = eye_target_x.tail[2]
			else:
		   
				eye_target_side.head = eye_ref.head + (eye_ref.tail - eye_ref.head)*10
				eye_target_side.tail = eye_target_side.head
				eye_target_side.tail[2] += 0.05
			
		# eyebrows
		eyebrows = []
			# make list of eyebrows
		init_selection("eyebrow_full_ref.l")
		bpy.ops.armature.select_similar(type='CHILDREN')
		for bone in bpy.context.selected_editable_bones[:]:
			if not ".r" in bone.name:#fingers only and left side only
				eyebrows.append(bone.name[:-2])
			   
		for side in sides:
			for eyebrow in eyebrows:			
				current_bone = get_bone("c_" + eyebrow[:-4]+ side)
				bone_ref = get_bone(eyebrow+side)
				current_bone.head = bone_ref.head
				current_bone.tail = bone_ref.tail
				current_bone.roll = bone_ref.roll  
		 
		 
		
   # if breast enabled 
	if bpy.context.active_object.rig_breast: 
		print('\n Aligning breasts...')
		breasts = ["c_breast_01", "c_breast_02"]   

		for side in sides:
			for bone in breasts:		 
				current_bone = get_bone(bone+side)
				current_pose_bone = get_pose_bone(bone+side)	
				
				try:
					ref_bone = get_bone(bone[2:] + "_ref" + side)
					# set transforms
					copy_bone_transforms(ref_bone, current_bone)
				  
					# set draw scale
					"""
					if not "_02" in bone: 
						current_pose_bone.custom_shape_scale = 4*unit_scale	 
					"""

				except:
					if debug_print == True:
						print("no breast ref, skip it")
		   
	 

   
	#display layers 16, 0, 1 only	
	_layers = bpy.context.active_object.data.layers
		#must enabling one before disabling others
	_layers[16] = True	
	for i in range(0,32):
		if i != 16:
			_layers[i] = False 
	_layers[0] = True
	_layers[1] = True	
	 
	
	#switch pose state and mode
	bpy.ops.object.mode_set(mode='POSE')
	bpy.context.active_object.data.pose_position = 'POSE'	 
	
	if debug_print == True:	   
		print("\n FINISH ALIGNING SPINE BONES...\n")
	
	if debug_print == True:
		print("\n COPY BONES TO RIG ADD ")
	
	copy_bones_to_rig_add(rig, rig_add)
	
	if debug_print == True:
		print("\n FINISHED COPYING TO RIG ADD ")
	
	#reset the proxy picker state
	try:
		bpy.context.scene.Proxy_Picker.active = proxy_picker_state	  
	except:
		pass
	
	#--END ALIGN SPINE BONES
	
def switch_bone_layer(bone, base_layer, dest_layer, mirror):
	
	if mirror == False:
		get_bone(bone).layers[dest_layer] = True
		get_bone(bone).layers[base_layer] = False
	
	if mirror == True:
		get_bone(bone+".l").layers[dest_layer] = True
		get_bone(bone+".l").layers[base_layer] = False
		get_bone(bone+".r").layers[dest_layer] = True
		get_bone(bone+".r").layers[base_layer] = False							
	
def mirror_hack():
	bpy.ops.transform.translate(value=(0, 0, 0), constraint_orientation='NORMAL', proportional='DISABLED')

def init_selection(active_bone):
	try:
		bpy.ops.armature.select_all(action='DESELECT')
	except:
		pass
	bpy.ops.object.mode_set(mode='POSE')
	bpy.ops.pose.select_all(action='DESELECT')
	if (active_bone != "null"):
		bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[active_bone].bone #set the active bone for mirror
	bpy.ops.object.mode_set(mode='EDIT')
	
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
	
	
def get_bone(name):
	try:
		return bpy.context.active_object.data.edit_bones[name]
	except KeyError:
		print('Edit bone', name, 'not found')
		return None
	
def copy_bone_transforms(bone1, bone2):
	bone2.head = bone1.head
	bone2.tail = bone1.tail
	bone2.roll = bone1.roll

def copy_bone_transforms_mirror(bone1, bone2):
	
	bone01 = get_bone(bone1+".l")
	bone02 = get_bone(bone2+".l")
	
	bone02.head = bone01.head
	bone02.tail = bone01.tail
	bone02.roll = bone01.roll
	
	bone01 = get_bone(bone1+".r")
	bone02 = get_bone(bone2+".r")
	
	bone02.head = bone01.head
	bone02.tail = bone01.tail
	bone02.roll = bone01.roll
	
def copy_bones_to_rig_add(rig, rig_add):
	rig_add.hide = False
	armature1 = rig
	armature2 = rig_add

	bone_data = {}
	
	edit_rig(armature1)
	#make dictionnary of bones transforms in armature 1
	for bone in armature1.data.edit_bones:
		bone_data[bone.name] = (bone.head.copy(), bone.tail.copy(), bone.roll)
		
	edit_rig(armature2)
	bpy.context.active_object.data.use_mirror_x = False

	#apply the bones transforms to the armature
	for bone in armature2.data.edit_bones:
		try:
			bone.head, bone.tail, bone.roll = bone_data[bone.name]
		except:
			pass
			
	#foot_bend, hand_bend, waist_end and epaules_bend bones to block the skin area
	try:#retro compatibility
		c_waist_bend_end = armature2.data.edit_bones['c_waist_bend_end.x']		
		c_waist_bend_end.head, c_waist_bend_end.tail, c_waist_bend_end.roll = bone_data['c_spine_01_bend.x']
	except:
		pass
	try:
		epaules_bend = armature2.data.edit_bones['epaules_bend.x']
		epaules_bend.head, epaules_bend.tail, epaules_bend.roll = bone_data['c_spine_02.x']
		epaules_bend.tail = bone_data['head.x'][1]
	except:
		pass	
	
	sides = ['.l', '.r']
	for side in sides:
		foot_bend = armature2.data.edit_bones['c_foot_bend'+side]
		foot_bend.head, foot_bend.tail, foot_bend.roll = bone_data['foot'+side]
		hand_bend = armature2.data.edit_bones['hand_bend'+side]
		hand_bend.head, hand_bend.tail, hand_bend.roll = bone_data['hand'+side]
		
	arm_bend = armature2.data.edit_bones['c_arm_bend.l']#just for setting the null_bend length
	c_thigh_bend_contact_r = armature2.data.edit_bones['c_thigh_bend_contact.r']
	c_thigh_bend_contact_l = armature2.data.edit_bones['c_thigh_bend_contact.l']
	c_waist_bend = armature2.data.edit_bones['c_waist_bend.x']
	null_bend = armature2.data.edit_bones['null_bend.x']
	null_bend.head = (c_thigh_bend_contact_r.head + c_thigh_bend_contact_l.head)*0.5	
	null_bend.tail = null_bend.head + (c_waist_bend.tail - c_waist_bend.head)

		
	
	bpy.ops.object.mode_set(mode='OBJECT')
	armature2.hide = True
	bpy.context.scene.objects.active = armature1
	#armature1.select = True
	bpy.ops.object.mode_set(mode='POSE')

def edit_rig(rig):
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	rig.select = True
	bpy.context.scene.objects.active = rig
	bpy.ops.object.mode_set(mode='EDIT')
	
def update_breast(self, context):

	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')
	
	#breast toggle	 
	breasts = ["breast_01", "breast_02"]		
   
	for bone in breasts:  
		# if disabled
		if not bpy.context.active_object.rig_breast: 
			# move rig bone layer
			switch_bone_layer("c_"+bone, 1, 22, True)
			switch_bone_layer("c_"+bone, 31, 22, True)
			# disable deform
			get_bone("c_"+bone+".l").use_deform = False
			get_bone("c_"+bone+".r").use_deform = False
			# move proxy and ref bone layer				
			switch_bone_layer("c_"+bone+"_proxy", 1, 22, True)
			switch_bone_layer(bone+"_ref", 17, 22, True)
			
		# if enabled
		else: 
			# move rig bone layer
			switch_bone_layer("c_"+bone, 22, 1, True)
			switch_bone_layer("c_"+bone, 22, 31, True)
			# enable deform
			get_bone("c_"+bone+".l").use_deform = True
			get_bone("c_"+bone+".r").use_deform = True
			# move proxy bone layer
			switch_bone_layer("c_"+bone+"_proxy", 22, 1, True)
			switch_bone_layer(bone+"_ref", 22, 17, True)

	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	return None
	
def update_tail(self, context):

	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')
	
	#tail toggle   
	tails = ["tail_00.x", "tail_01.x","tail_02.x", "tail_03.x"]		   
   
	for bone in tails:	
		# if disabled
		if not bpy.context.active_object.rig_tail: 
			# move rig bone layer
			switch_bone_layer("c_"+bone, 0, 22, False)
			switch_bone_layer("c_"+bone, 31, 22, False)
			# disable deform
			get_bone("c_"+bone).use_deform = False
			# move proxy and ref bone layer				
			switch_bone_layer("c_"+bone[:-2]+"_proxy.x", 0, 22, False)
			switch_bone_layer(bone[:-2]+"_ref.x", 17, 22, False)
			
			
		# if enabled
		else: 
			# move rig bone layer
			switch_bone_layer("c_"+bone, 22, 0, False) 
			switch_bone_layer("c_"+bone, 22, 31, False)
			# enable deform
			get_bone("c_"+bone).use_deform = True	
			# move proxy bone layer
			switch_bone_layer("c_"+bone[:-2]+"_proxy.x", 22, 0, False)
			switch_bone_layer(bone[:-2]+"_ref.x", 22, 17, False)

	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	return None
	
def update_toes(self, context):

	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')
	obj = bpy.context.active_object	  

	
	toes_list=["toes_pinky", "toes_ring", "toes_middle", "toes_index", "toes_thumb"]
	toes_bool_list = [obj.rig_toes_pinky, obj.rig_toes_ring, obj.rig_toes_middle, obj.rig_toes_index, obj.rig_toes_thumb]
	
	
	# the global toes bone deform will set to false if no additional toes are enabled
	get_bone("toes_01.l").use_deform = True
	get_bone("toes_01.r").use_deform = True
 
	# 3 bones toes
	for t in range (0,5):		 
		max = 4
		if t == 4:
			max = 3		   
		for i in range (1,max):
			#toes disabled	 
			if not toes_bool_list[t]:
				# ref bones
				switch_bone_layer(toes_list[t]+str(i)+"_ref", 17, 22, True)
				# proxy bones
				switch_bone_layer("c_"+toes_list[t]+str(i)+"_proxy", 0, 22, True)
				# control bones
				switch_bone_layer("c_"+toes_list[t]+str(i), 0, 22, True)
				switch_bone_layer("c_"+toes_list[t]+str(i), 31, 22, True)
				get_bone("c_"+toes_list[t]+str(i)+".l").use_deform = False
				get_bone("c_"+toes_list[t]+str(i)+".r").use_deform = False
				
			# toes enabled
			else:
				# set global toes bone to false if any additional toes is enabled
				get_bone("toes_01.l").use_deform = False
				get_bone("toes_01.r").use_deform = False
				# ref bones
				switch_bone_layer(toes_list[t]+str(i)+"_ref", 22, 17, True)
				# proxy bones
				switch_bone_layer("c_"+toes_list[t]+str(i)+"_proxy", 22, 0, True)
				 # control bones
				switch_bone_layer("c_"+toes_list[t]+str(i), 22, 0, True)
				switch_bone_layer("c_"+toes_list[t]+str(i), 22, 31, True)
				get_bone("c_"+toes_list[t]+str(i)+".l").use_deform = True
				get_bone("c_"+toes_list[t]+str(i)+".r").use_deform = True
  
 
	
	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	return None
	
def update_spine_count(self, context):
	current_mode = context.mode
	
	#disable the proxy picker to avoid bugs
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = False
	except:
		pass	
	
	active_bone = None
	
	if current_mode == 'POSE':
		try:
			active_bone = context.object.data.bones.active.name
		except:
			pass
	if current_mode == 'EDIT_ARMATURE':		   
		try:
			active_bone = context.object.data.edit_bones.active.name			
		except:
			pass
	 
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='DESELECT')
	obj = bpy.context.active_object	  
	

	#Active all layers
		#save current displayed layers
	_layers = bpy.context.active_object.data.layers
	layers_select = []
	for i in range(0,32):  
		layers_select.append(_layers[i])

	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = True 
		
	
		
	#Set to 4 bones	   
	if obj.rig_spine_count == 4:
		if get_bone('c_spine_03.x') == None and get_bone('c_spine_02.x').layers[22] == False:
			
			#subdivide spine
			bpy.ops.armature.select_all(action='DESELECT')
			obj.data.edit_bones.active = get_bone('c_spine_02.x')
			bpy.ops.armature.subdivide()
			get_bone('c_spine_02.x.001').name = 'c_spine_03.x'
			
			bpy.ops.armature.select_all(action='DESELECT')
			obj.data.edit_bones.active = get_bone('spine_02.x')
			bpy.ops.armature.subdivide()
			get_bone('spine_02.x.001').name = 'spine_03.x'
			
			bpy.ops.armature.select_all(action='DESELECT')
			obj.data.edit_bones.active = get_bone('spine_02_ref.x')
			bpy.ops.armature.subdivide()
			get_bone('spine_02_ref.x.001').name = 'spine_03_ref.x'
			
			bpy.ops.armature.select_all(action='DESELECT')
			obj.data.edit_bones.active = get_bone('c_spine_02_proxy.x')
			get_bone('c_spine_02_proxy.x').select = True
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, True), "constraint_orientation":'GLOBAL', "proportional":'DISABLED',"snap":False, "remove_on_cancel":False, "release_confirm":False})
	   
			get_bone('c_spine_02_proxy.x.001').name = 'c_spine_03_proxy.x'
			get_pose_bone('c_spine_03_proxy.x')['proxy'] = 'c_spine_03.x'			
			
			#move bone proxys
			move_bone('c_spine_03_proxy.x', 0.05, 2)
			move_bone('c_spine_02_proxy.x', -0.04, 2)
			move_bone('c_spine_02_bend_proxy.x', -0.01, 2)
			move_bone('c_breast_01_proxy.r', 0.045, 2)
			move_bone('c_breast_01_proxy.l', 0.045, 2)
			move_bone('c_breast_02_proxy.r', 0.045, 2)
			move_bone('c_breast_02_proxy.l', 0.045, 2)
			
			#copy constraints
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.pose.select_all(action='DESELECT')
			bpy.context.active_object.data.bones.active = get_pose_bone('spine_03.x').bone			   
			bpy.context.active_object.data.bones.active = get_pose_bone('spine_02.x').bone
			bpy.ops.pose.constraints_copy()

			
			for cns in get_pose_bone('spine_03.x').constraints:
				cns.subtarget = cns.subtarget.replace('02', '03')
			
			#set bone shape
			get_pose_bone('c_spine_03.x').custom_shape = get_pose_bone('c_spine_02.x').custom_shape
			get_pose_bone('c_spine_03.x').custom_shape_scale = get_pose_bone('c_spine_02.x').custom_shape_scale			  
			get_pose_bone("c_spine_02.x").custom_shape_transform = None
			#set transform parameter
			get_pose_bone('c_spine_03.x').rotation_mode = 'XYZ'
			for i in range(0,3):
				get_pose_bone('c_spine_03.x').lock_scale[i] = True
			
			#set bone group
			get_pose_bone('spine_03_ref.x').bone_group = bpy.context.active_object.pose.bone_groups['body.x']
			get_pose_bone('c_spine_03.x').bone_group = bpy.context.active_object.pose.bone_groups['body.x']
			
	#Set to 3 bones
	if obj.rig_spine_count == 3:
		if get_bone('c_spine_03.x') != None:
			bpy.ops.armature.select_all(action='DESELECT')
			obj.data.edit_bones.active = get_bone('c_spine_03.x')
			obj.data.edit_bones.active = get_bone('spine_03.x')
			obj.data.edit_bones.active = get_bone('spine_03_ref.x')
			obj.data.edit_bones.active = get_bone('c_spine_03_proxy.x')
			bpy.ops.armature.delete()
			 
			get_bone('c_spine_02.x').tail = get_bone('c_neck.x').head
			get_bone('spine_02.x').tail = get_bone('c_neck.x').head
			get_bone('spine_02_ref.x').tail = get_bone('neck_ref.x').head
			get_bone('neck_ref.x').use_connect = True
			
			#move bone proxys
			move_bone('c_spine_02_proxy.x', 0.04, 2)
			move_bone('c_spine_02_bend_proxy.x', 0.01, 2)
			move_bone('c_breast_01_proxy.r', -0.045, 2)
			move_bone('c_breast_01_proxy.l', -0.045, 2)
			move_bone('c_breast_02_proxy.r', -0.045, 2)
			move_bone('c_breast_02_proxy.l', -0.045, 2)
			
			#set bone shape
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.pose.select_all(action='DESELECT')
			#get_pose_bone('c_spine_02.x').custom_shape_scale *= 0.5
			get_pose_bone("c_spine_02.x").custom_shape_transform = get_pose_bone('c_p_spine_02.x')
			
			
						
			
	#restore layers
	for i in range(0,32):
		bpy.context.active_object.data.layers[i] = layers_select[i]	  

	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	if active_bone != None and not 'spine_03' in active_bone:
		if current_mode == 'POSE':		
			bpy.context.active_object.data.bones.active = get_pose_bone(active_bone).bone	 
		   
		if current_mode == 'EDIT':		
			obj.data.edit_bones.active = get_bone(active_bone)

	#restore picker 
	try:
		proxy_picker_state = bpy.context.scene.Proxy_Picker.active	 
		bpy.context.scene.Proxy_Picker.active = True
	except:
		pass	

	return None
	
def move_bone(bone, value, axis):
				get_bone(bone).head[axis] += value/bpy.context.scene.unit_settings.scale_length#*context.object.scale[0]
				get_bone(bone).tail[axis] += value/bpy.context.scene.unit_settings.scale_length#*context.object.scale[0]
	
def update_fingers(self, context):

	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')
	obj = bpy.context.active_object	  

	fingers_list=["pinky", "ring", "middle", "index", "thumb"]
	fingers_bool_list = [obj.rig_pinky, obj.rig_ring, obj.rig_middle, obj.rig_index, obj.rig_thumb]

 
	# 3 bones fingers
	for t in range (0,5): 
		max = 4		 
		for i in range (0,max):		   
			
			ref_bone = fingers_list[t]+str(i)+"_ref"
			proxy_bone = "c_"+fingers_list[t]+str(i)+"_proxy"
			c_bone = "c_"+fingers_list[t]+str(i)
				
			if i == 0:				  
				ref_bone = fingers_list[t]+str(i+1)+"_base_ref"
				proxy_bone = "c_"+fingers_list[t]+str(i+1)+"_base_proxy"
				c_bone = "c_"+fingers_list[t]+str(i+1)+"_base"
				
				if t == 4: # thumb
					ref_bone = fingers_list[t]+str(i+1)+"_ref"
				   
				
			#finger disabled   
			if not fingers_bool_list[t]:					
				# ref bones
				switch_bone_layer(ref_bone, 17, 22, True)
				# proxy bones
				switch_bone_layer(proxy_bone, 0, 22, True)
				# control bones
				switch_bone_layer(c_bone, 0, 22, True)
				switch_bone_layer(c_bone, 31, 22, True)
				get_bone(c_bone+".l").use_deform = False
				get_bone(c_bone+".r").use_deform = False
				
			# fingers enabled
			else:		
				# ref bones
				switch_bone_layer(ref_bone, 22, 17, True)
				# proxy bones
				switch_bone_layer(proxy_bone, 22, 0, True)
				 # control bones
				switch_bone_layer(c_bone, 22, 0, True)
				switch_bone_layer(c_bone, 22, 31, True)
				get_bone(c_bone+".l").use_deform = True
				get_bone(c_bone+".r").use_deform = True

				
	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	return None
	
def update_ears(self, context):

	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')
	obj = bpy.context.active_object	  

	ears_list=["ear_01", "ear_02"]	 

	#check for head bone display override
	facial_display = True
	
	if obj.rig_ears and get_bone('head_ref.x').layers[17] == True:
		ears_display = True
	else:
		ears_display = False
	
	#check if ears exist in the version
	for ear in ears_list:		 
		
		ref_bone = ear+"_ref"
		proxy_bone = "c_"+ear+"_proxy"
		c_bone = "c_"+ear			 
					  
		#ear disabled	
		if not ears_display:					
			# ref bones
			switch_bone_layer(ref_bone, 17, 22, True)
			# proxy bones
			switch_bone_layer(proxy_bone, 0, 22, True)
			# control bones
			switch_bone_layer(c_bone, 0, 22, True)
			switch_bone_layer(c_bone, 31, 22, True)
			get_bone(c_bone+".l").use_deform = False
			get_bone(c_bone+".r").use_deform = False
			
		# ear enabled
		else:		
			# ref bones
			switch_bone_layer(ref_bone, 22, 17, True)
			# proxy bones
			switch_bone_layer(proxy_bone, 22, 0, True)
			 # control bones
			switch_bone_layer(c_bone, 22, 0, True)
			switch_bone_layer(c_bone, 22, 31, True)
			get_bone(c_bone+".l").use_deform = True
			get_bone(c_bone+".r").use_deform = True

				
	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	return None
	
def update_facial(self, context):

	current_mode = bpy.context.mode
	bpy.ops.object.mode_set(mode='EDIT')
	obj = bpy.context.active_object 
		
	#check for head bone display override
	facial_display = True
	
	if obj.rig_facial and get_bone('head_ref.x').layers[17] == True:#display only if the head is not already disabled
		facial_display = True
	else:
		facial_display = False
 
	# Refbones
	facial_ref = auto_rig_datas.facial_ref
   
	for bone_ref in facial_ref:			 
		#facial disabled   
		if not facial_display:					  
			# ref bones
			try:
				switch_bone_layer(bone_ref, 17, 22, False)
			except:
				print(bone_ref, ' not found')
		# facial enabled
		else:	   
			try:
				switch_bone_layer(bone_ref, 22, 17, False)
			except:
				print(bone_ref, ' not found')

	   
	# Control and Deform bones
	facial_deform =auto_rig_datas.facial_deform
	facial_deform_rig_add =auto_rig_datas.facial_deform_rig_add	
	facial_displayed = auto_rig_datas.facial_displayed
	
	
	for bone in facial_deform:
		if not facial_display:#disabled 
			try: 
				switch_bone_layer(bone, 31, 22, False)
				get_bone(bone).use_deform = False
			except:
				print(bone, ' not found')
		else:#enabled	  
			try:
				switch_bone_layer(bone, 22, 31, False)
				get_bone(bone).use_deform = True
			except:
				print(bone, ' not found')
				
	rig = bpy.context.active_object
	rig_add = get_rig_add(rig)		
				
	for bone in facial_deform_rig_add:
		if not facial_display:#disabled 
			try:				
				rig_add.data.bones[bone].use_deform = False
			except:
				print(bone, ' not found')
		else:#enabled	  
			try:				
				rig_add.data.bones[bone].use_deform = True
			except:
				print(bone, ' not found')
	
	for bone in facial_displayed:
		if not facial_display:#disabled	 
			try:
				switch_bone_layer(bone, get_bone(bone)['arp_layer'], 22, False) 
			except:
				print(bone, ' not found')
			#proxy
			try:
				switch_bone_layer(bone.replace('.', '_proxy.'), get_bone(bone)['arp_layer'], 22, False) 
			except:
				print(bone.replace('.', '_proxy.'), ' not found')
		else:#enabled
			try:
				switch_bone_layer(bone, 22, get_bone(bone)['arp_layer'], False)
			except:
				print(bone, 'not found')
			#proxy
			try:
				switch_bone_layer(bone.replace('.', '_proxy.'), 22, get_bone(bone)['arp_layer'], False)
			except:
				print(bone.replace('.', '_proxy.'), ' not found')
	

				
	#restore saved mode	   
	if current_mode == 'EDIT_ARMATURE':
		current_mode = 'EDIT'
		
	bpy.ops.object.mode_set(mode=current_mode)
	
	return None

def is_object_arp(object):
	if object.type == 'ARMATURE':
		if get_pose_bone('c_pos') != None:
			return True
			
			
# END FUNCTIONS


###########	 UI PANEL  ###################

class auto_rig_pro_panel(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = "Auto-Rig Pro"
	bl_idname = "id_auto_rig"
	
	"""
	@classmethod
	# buttons visibility conditions
	
	def poll(cls, context):	  
	   
	   
		if bpy.context.active_object is not None:					  
			if context.mode == 'POSE' or context.mode == 'OBJECT' or context.mode == 'EDIT_ARMATURE' or context.mode == 'EDIT_MESH':
				return True
			else:
				return False
		else:
			return False
	"""

	def draw(self, context):
		layout = self.layout.column(align=True)
		
		object = context.object
		
		selected_objects = context.selected_objects
		scene = context.scene
		

		
		#BUTTONS
	
		
		
		
		layout.row().prop(scene, "active_tab", expand=True)
		layout.separator()
		
		if scene.active_tab == 'CREATE':
		
			col = layout.column(align=False)   
			row = col.row(align=True)
			row.operator("id.append_arp", "Add Armature", icon = 'OUTLINER_OB_ARMATURE')	
			row.operator("id.delete_arp", "", icon='PANEL_CLOSE')
			
			col = layout.column(align=True)
			if object != None:
				
				if is_object_arp(object):
					col.enabled = True
				else:
					col.enabled = False
					
				col.label("Rig Definition:")
				col.prop(object, "rig_type", "", expand=False)
				
				col = layout.column(align=True)
				if object.spine_disabled == False and is_object_arp(object):
					col.enabled = True
				else:
					col.enabled = False			   
				col.prop(object, 'rig_spine_count', 'Spine')
				
				row = layout.column(align=True).row(align=True)
				if is_object_arp(object):
					row.enabled = True
				else:
					row.enabled = False
				row.prop(object, "rig_facial", "Facial")		
				row.prop(object, "rig_breast", "Breast")		
				row = layout.column(align=True).row(align=True)
				if is_object_arp(object):
					row.enabled = True
				else:
					row.enabled = False
				row.prop(object, "rig_tail", "Tail")  
				row.prop(object, "rig_ears", "Ears")		
				
				layout.label("Fingers:")		 
					
				row = layout.column(align=True).row(align=True) 
				if object.symetric_fingers and is_object_arp(object):
					row.enabled = True
				else:
					row.enabled = False
				
				row.prop(object, "rig_pinky", "Pinky")
				row.prop(object, "rig_ring", "Ring")
				row = layout.column(align=True).row(align=True)
				
				if object.symetric_fingers and is_object_arp(object):
					row.enabled = True
				else:
					row.enabled = False
					
				row.prop(object, "rig_middle", "Middle")		   
				row.prop(object, "rig_index", "Index")
				
				row = layout.column(align=True).row(align=True)
				if object.symetric_fingers and is_object_arp(object):
					row.enabled = True
				else:
					row.enabled = False
					
				row.prop(object, "rig_thumb", "Thumb")
				if object.symetric_fingers and is_object_arp(object):
					row.enabled = True
				else:
					row.enabled = False
					
				layout.label("Toes:")
				row = layout.column(align=True).row(align=True)
				if object.symetric_toes and is_object_arp(object):
					row.enabled = True	
				else: 
					row.enabled = False
				
				row.prop(object, "rig_toes_pinky", "Pinky")
				row.prop(object, "rig_toes_ring", "Ring")
				
				row = layout.column(align=True).row(align=True) 
				if object.symetric_toes and is_object_arp(object):
					row.enabled = True	
				else: 
					row.enabled = False
					
				row.prop(object, "rig_toes_middle", "Middle")		   
				row.prop(object, "rig_toes_index", "Index")
				
				row = layout.column(align=True).row(align=True)
				if object.symetric_toes and is_object_arp(object):
					row.enabled = True	
				else: 
					row.enabled = False				   
				row.prop(object, "rig_toes_thumb", "Thumb")

				layout.separator()
				layout.separator()
				  
				layout.operator("id.edit_ref", text="Edit Reference Bones", icon = 'EDIT')
				
				row = layout.row(align=True)	   
				row.operator('id.dupli_limb', 'Duplicate')		 
				row.operator('id.disable_limb', 'Disable')	   
				layout.operator("id.enable_all_limbs", text="Enable All")	 
				row = layout.row(align=True)
				row.operator('id.import_ref', 'Import')
				row.operator('id.export_ref', 'Export')		  
				layout.operator("id.align_all_bones", text="Match to Rig", icon = 'POSE_HLT')				   
					 
				layout.separator()
				row = layout.row(align=True)
				if bpy.context.mode != 'EDIT_MESH':
					row.operator("id.edit_custom_shape", text="Edit Shape...") 
					row.operator("id.mirror_custom_shape", text="", icon="MOD_MIRROR") 
				else:			 
					layout.operator("id.exit_edit_shape", text="Apply Shape")	   
			
		if scene.active_tab == 'BIND':
			
			layout.label("Mesh Binding:")
			row = layout.column(align=True).row(align=True)
			row.prop(scene, "bind_split", "Split Parts")
			row1 = row.row()
			
			if object != None:
				if object.rig_facial or object.rig_type == 'quadruped':
					row1.enabled = False
			else:
				row1.enabled = True
			
			row1.prop(scene, "bind_chin", "Use Chin")
			
			row = layout.column(align=True).row(align=True)		
			row.operator("id.bind_to_rig", text="Bind")
			row.operator("id.unbind_to_rig", text="Unbind")
		
			layout.separator()
			
			#Shape Key Driver Tool	
			layout.label("Shapekeys Driver Tools:")		  
			active_armature = ""
			
			if len(context.selected_objects) > 0:
				if context.selected_objects[0].type == 'ARMATURE':			 
					active_armature = context.selected_objects[0].data.name
				else:
					if len(context.selected_objects) > 1:
						if context.selected_objects[1].type == 'ARMATURE':
							active_armature = context.selected_objects[1].data.name
					
			
			
			row = layout.row(align=True)			
			
			if context.object != None:
				if object.type == 'ARMATURE':
					row.enabled = True
			else:
				row.enabled = False
				
			if active_armature != "":
				row.prop_search(context.scene, "driver_bone", bpy.data.armatures[active_armature], "bones", "")
			row.operator("id.pick_bone", text="", icon='EYEDROPPER')
			col = layout.column(align=True)
			if active_armature != "":
				col.enabled = True
			else:
				col.enabled = False
			col.prop(scene, "driver_transform", text = "")
			col = layout.column(align=True)
			if len(selected_objects) == 2:
				col.enabled = True
			else:
				col.enabled = False
			col.operator("id.create_driver", text="Create Driver")	 
			
			row = layout.row(align=True)
			btn = row.operator('id.set_shape_key_driver', text='0')
			btn.value = '0'
			btn = row.operator('id.set_shape_key_driver', text='1')
			btn.value = '1'
			btn = row.operator('id.set_shape_key_driver', text='Reset')
			btn.value = 'reset'
			
			layout.separator()
			
			
			
		
		if scene.active_tab == 'TOOLS':
			layout.separator()
		
			layout.operator("id.update_armature", "Update Armature")
			
			layout.separator()
			
			layout.label("Picker Panel:")
			layout.operator("id.set_picker_camera", text="Set UI Cam", icon = 'CAMERA_DATA')
			
			layout.separator()
			
			
			layout.label('Color Theme:', icon='COLOR')
			row = layout.row(align=True)
			row.prop(scene, "color_set_right","")
			row.prop(scene, "color_set_middle","")
			row.prop(scene, "color_set_left","")
			row = layout.row(align=True)
			row.prop(scene, "color_set_panel","")
			row.prop(scene, "color_set_text","")
			row = layout.row(align=True)
			row.operator("id.assign_colors", "Assign")
			row = layout.row(align=True)
			row.operator("id.import_colors", "Import")
			row.operator("id.export_colors", "Export")
			
			layout.separator()			
			
			layout.label('Picker background:')
			row = layout.row(align=True)
			row.operator("id.screenshot_head_picker", "Capture Facial", icon='RENDER_STILL')
			row = layout.row(align=True)
			if len(context.scene.keys()) > 0:
				if 'Proxy_Picker' in context.scene.keys():
					if context.scene.Proxy_Picker.active:
						btn = row.operator("id.move_picker_layout", "Edit Layout...")
						btn.state = 'start'
					else:
						btn = row.operator("id.move_picker_layout", "Apply Layout")
						btn.state = 'end'
						
			row = layout.row(align=True)
			row.operator("id.mirror_picker", "Mirror Picker")#icon = 'MOD_MIRROR'
			
###########	 REGISTER  ##################

def register():	 
	fingers_description = 'Enable or disable left and right fingers. If greyed out, some fingers have been disabled using Disable Limb. Click Enable All limbs to restore'
	toes_description = 'Enable or disable left and right toes. If greyed out, some toes have been disabled using Disable Limb. Click Enable All limbs to restore'
	
	bpy.types.Object.rig_type = bpy.props.EnumProperty(items=(
	('biped', 'Biped', 'Biped Rig Type, vertical spine orientation'),	 
	('quadruped', 'Multi-Ped', 'Multi-Ped rig type, free spine orientation')), 
	name = "Rig Type")
	bpy.types.Object.rig_facial = bpy.props.BoolProperty(default=True, update=update_facial)
	bpy.types.Object.rig_tail = bpy.props.BoolProperty(default=False, update=update_tail)
	bpy.types.Object.rig_breast = bpy.props.BoolProperty(default=True, update=update_breast)
	
	bpy.types.Object.rig_ears = bpy.props.BoolProperty(default=True, update=update_ears)
	
	bpy.types.Object.rig_pinky = bpy.props.BoolProperty(default=True, update=update_fingers, description=fingers_description)
	bpy.types.Object.rig_ring = bpy.props.BoolProperty(default=True, update=update_fingers, description=fingers_description)
	bpy.types.Object.rig_middle = bpy.props.BoolProperty(default=True, update=update_fingers, description=fingers_description)
	bpy.types.Object.rig_index = bpy.props.BoolProperty(default=True, update=update_fingers,description=fingers_description)
	bpy.types.Object.rig_thumb = bpy.props.BoolProperty(default=True, update=update_fingers, description=fingers_description)
	
	bpy.types.Object.symetric_fingers = bpy.props.BoolProperty(default=True)	
	
	bpy.types.Object.rig_toes_pinky = bpy.props.BoolProperty(default=False, update=update_toes, description=toes_description)
	bpy.types.Object.rig_toes_ring = bpy.props.BoolProperty(default=False, update=update_toes, description=toes_description)
	bpy.types.Object.rig_toes_middle = bpy.props.BoolProperty(default=False, update=update_toes, description=toes_description)
	bpy.types.Object.rig_toes_index = bpy.props.BoolProperty(default=False, update=update_toes, description=toes_description)
	bpy.types.Object.rig_toes_thumb = bpy.props.BoolProperty(default=False, update=update_toes, description=toes_description)
	
	bpy.types.Object.symetric_toes = bpy.props.BoolProperty(default=True)
	bpy.types.Object.spine_disabled = bpy.props.BoolProperty(default=False)
	
	bpy.types.Object.rig_spine_count = bpy.props.IntProperty(default=3, min=3, max=4, update=update_spine_count, description='Set the number of spine bones')
	
	bpy.types.Scene.driver_bone = bpy.props.StringProperty(name="Bone Name", description="Bone driving the shape key")
	bpy.types.Scene.driver_transform = bpy.props.EnumProperty(items=(('LOC_X', 'Loc X', 'X Location'),('LOC_Y', 'Loc Y', 'Y Location'), ('LOC_Z', 'Loc Z', 'Z Location'), ('ROT_X', 'Rot X', 'X Rotation'), ('ROT_Y', 'Rot Y', 'Y Rotation'), ('ROT_Z', 'Rot Z', 'Z Rotation'), ('SCALE_X', 'Scale X', 'X Scale'), ('SCALE_Y', 'Scale Y', 'Y Scale'), ('SCALE_Z', 'Scale Z', 'Z Scale')), name = "Bone Transform")
	
	bpy.types.Scene.bind_split = bpy.props.BoolProperty(default=True, description="Improve skinning by separating the loose parts (e.g: hats, buttons, belt...) before binding.\nWarning: meshes with a lot of separate pieces can take several minutes to bind.")
	bpy.types.Scene.bind_chin = bpy.props.BoolProperty(default=False, description="Improve head skinning based on the chin (reference jawbone tail) position.\nOnly when facial is disabled, and biped type.")
	bpy.types.Scene.active_tab = bpy.props.EnumProperty(items=(('CREATE', 'Rig', 'Create Tab'),('BIND', 'Skin', 'Bind Tab'), ('TOOLS', 'Misc', 'Misc Tab')))
	
	bpy.types.Scene.color_set_right = bpy.props.FloatVectorProperty(name="Color Right", subtype="COLOR_GAMMA", default=(0.602,0.667,1.0), min=0.0, max=1.0, description="Right controllers color")
	bpy.types.Scene.color_set_middle = bpy.props.FloatVectorProperty(name="Color Middle", subtype="COLOR_GAMMA", default=(0.205,0.860,0.860), min=0.0, max=1.0, description="Middle controllers color")
	bpy.types.Scene.color_set_left = bpy.props.FloatVectorProperty(name="Color Left", subtype="COLOR_GAMMA", default=(0.8,0.432,0.0), min=0.0, max=1.0, description="Left controllers color")
	bpy.types.Scene.color_set_panel = bpy.props.FloatVectorProperty(name="Color Panel", subtype="COLOR_GAMMA", default=(0.2,0.2,0.2), min=0.0, max=1.0, description="Back picker panel color")
	bpy.types.Scene.color_set_text = bpy.props.FloatVectorProperty(name="Color Text", subtype="COLOR_GAMMA", default=(0.887,0.887,0.887), min=0.0, max=1.0, description="Text color in the picker panel")
	
def unregister():  
	del bpy.types.Object.rig_type
	del bpy.types.Object.rig_facial
	del bpy.types.Object.rig_tail
	del bpy.types.Object.rig_breast
	
	del bpy.types.Object.rig_ears
	
	del bpy.types.Object.rig_pinky
	del bpy.types.Object.rig_ring
	del bpy.types.Object.rig_middle
	del bpy.types.Object.rig_index
	del bpy.types.Object.rig_thumb	
	
	del bpy.types.Object.symetric_fingers  
	del bpy.types.Object.spine_disabled
	
	del bpy.types.Object.rig_toes_pinky
	del bpy.types.Object.rig_toes_ring
	del bpy.types.Object.rig_toes_middle
	del bpy.types.Object.rig_toes_index
	del bpy.types.Object.rig_toes_thumb 
	
	del bpy.types.Object.symetric_toes 

	del bpy.types.Object.rig_spine_count
	
	del bpy.types.Scene.driver_bone
	del bpy.types.Scene.driver_transform
	
	del bpy.types.Scene.bind_split
	del bpy.types.Scene.bind_chin
	del bpy.types.Scene.active_tab
	
	del bpy.types.Scene.color_set_right
	del bpy.types.Scene.color_set_middle
	del bpy.types.Scene.color_set_left
	del bpy.types.Scene.color_set_panel
	del bpy.types.Scene.color_set_text
	