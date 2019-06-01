import bpy, bmesh, math, bpy_extras, bgl
from bpy_extras import *
from math import degrees, pi
import mathutils
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from . import auto_rig_datas, auto_rig
#custom icons
import os
import bpy.utils.previews
from bpy.app.handlers import persistent


print ("\n Starting Auto-Rig Pro: Smart... \n")

blender_version = bpy.app.version_string

handles=[None]

debug = True

##########################	CLASSES	 ##########################
class restore_markers(bpy.types.Operator):
	  
	#tooltip
	""" Restore the markers position from the previous session """
	
	bl_idname = "id.restore_markers"
	bl_label = "restore_markers"
	bl_options = {'UNDO'}		

  
	"""
	@classmethod
	def poll(cls, context):
		if context.scene.markers_restored:
			return False
	"""

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False		
  
		try:		  
			_restore_markers()			
		  
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}


class turn(bpy.types.Operator):
	  
	#tooltip
	""" Turn the character to face the camera """
	
	bl_idname = "id.turn"
	bl_label = "turn"
	bl_options = {'UNDO'}	
	
	action = bpy.props.StringProperty()
  
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False	  
		
  
		try:		  
			_turn(context, self.action)			
		  
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}


class set_front_view(bpy.types.Operator):
	  
	#tooltip
	""" Select the character meshes objects then click it to quicky place the reference bones on the character """
	
	bl_idname = "id.set_front_view"
	bl_label = "set_front_view"
	bl_options = {'UNDO'}	
	
  
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			if context.active_object.type == 'MESH':
				return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False	  
		scene = context.scene		
		
		#check - are they all meshes?
		selection = context.selected_objects
		
		for obj in context.selected_objects:
			if obj.type != 'MESH':
				self.report({'ERROR'}, "Please select meshes only")
				return{'FINISHED'} 
			
		#add a 'arp_body_mesh' tag to the objects
		for obj in context.selected_objects:
			obj['arp_body_mesh'] = 1
		
		#duplicate,apply modifiers, merge		
		bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
		bpy.ops.object.convert(target='MESH')		
		bpy.ops.object.join()	
		context.active_object.name = "body_temp"
		del context.active_object['arp_body_mesh']	

		#disable X Mirror
		bpy.context.active_object.data.use_mirror_x = False
		bpy.context.object.data.use_mirror_topology = False

		#hide visibility
		for obj in bpy.data.objects:
			if not obj.select:
				obj.hide = True
				
		#hide from selection
		for obj in selection:
			obj.hide_select = True		
  
		try:		  
			_set_front_view()			
		  
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}

class match_ref_only(bpy.types.Operator):
	  
	#tooltip
	""" Click it to aumatically find the reference bones position """
	
	bl_idname = "id.match_ref_only"
	bl_label = "match_ref_only"
	bl_options = {'UNDO'}	
	
  
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		scene = context.scene
	

		try:
		  
			_match_ref()		   
			
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}

class match_ref(bpy.types.Operator):
	  
	#tooltip
	""" Click it to automatically match the reference bones and the markers """
	
	bl_idname = "id.match_ref"
	bl_label = "match_ref"
	bl_options = {'UNDO'}	
	
	arm_angle = bpy.props.FloatProperty(default = 0.0)
  
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False	
		scene = context.scene	
		
		# check if the rig is appended in the scene
		try:
			bpy.data.objects["rig"]
			bpy.data.objects["rig_add"]
		except:			
			if not ('2.78' in blender_version) or ('2.78' in blender_version and 'sub 5' in blender_version):
				auto_rig._append_arp()
			else:
				self.report({'ERROR'}, "Please append auto-rig pro in the scene first (Shift-F1), or use Blender 2.79 and above for automatic appending")
				return{'FINISHED'}
		
			
				 
		try:
			#unsimplify, subsurf needed for fingers detection
			simplify_value = bpy.context.scene.render.use_simplify			
			bpy.context.scene.render.use_simplify = False
			
		
			#clear selection
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			
			#ensure layer 1(0) is displayed otherwise can't select the armature
			bpy.context.scene.layers[0] = True
			
			#unfreeze character selection
			bpy.data.objects[context.scene.body_name].hide_select = False			
			bpy.data.objects['rig'].hide_select = False
			bpy.data.objects['rig'].hide = False
			
			# go				 
			_auto_detect(self)			 
		   
			set_active_object("rig")
			#set to 3 spine bones
			bpy.context.object.rig_spine_count = 3
			auto_rig.update_spine_count(self, context)
			
			_match_ref(self)
			
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.id.delete_big_markers()
			
			_delete_detected()			
			
			# Display the ref bones layer only
			set_active_object("rig")	

			bpy.ops.object.mode_set(mode='EDIT')			
			bpy.context.object.data.use_mirror_x = True
		
				#display layer 17 only
			_layers = bpy.context.object.data.layers
				#must enabling one before disabling others
			_layers[17] = True	
			for i in range(0,31):
				if i != 17:
					_layers[i] = False 
					
			# turn on XRays
			bpy.context.object.show_x_ray = True

			#restore simplify
			bpy.context.scene.render.use_simplify = simplify_value
			

					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
def draw_circle(self, context):
	
	if bpy.data.objects.get('markers') is not None:
		num_segments=360
		radius = 22
		
		#circle params
		theta = 2 * 3.1415926 / num_segments
		c = math.cos(theta)
		s = math.sin(theta)
		x =	 radius
		dot_radius = 5
		y = 0
		
		#dot params
		dot_num_segments = 10
		dot_theta = 2 * 3.1415926 / dot_num_segments
		dot_c = math.cos(theta)
		dot_s = math.sin(theta)
		dot_radius = 1
		dot_x =	 dot_radius			
		dot_y = 0
		
		
		_region = context.region
		_region_3d = context.space_data.region_3d
		
		for obj in bpy.data.objects['markers'].children:
			object_loc_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(_region, _region_3d, obj.matrix_world.translation, default=None)
			
			_x = object_loc_2d[0]
			_y = object_loc_2d[1]	
			
			#circle border
			bgl.glEnable(bgl.GL_BLEND)
			bgl.glColor4f(0, 0.85, 0.7, 0.2)		
			bgl.glPointSize(2)
			bgl.glBegin(bgl.GL_POINTS)		
			
			
			for i in range (num_segments):
				bgl.glVertex2f(x + _x, y +_y)
				t = x
				x = (c * x - s * y)
				y = (s * t + c * y)		
				
			bgl.glEnd()
			
			#circle solid
			bgl.glEnable(bgl.GL_BLEND)
			bgl.glColor4f(0.0, 0.7, 0.05, 0.15)	  
			bgl.glBegin(bgl.GL_TRIANGLE_FAN)		
			
			for i in range(0, num_segments):
				t = 2 * 3.1415926 * i / num_segments
				bgl.glVertex2f(_x + math.sin(t) * radius, _y + math.cos(t) * radius)
			
			bgl.glEnd()
			
			#dot		
			bgl.glEnable(bgl.GL_BLEND)
			bgl.glColor4f(1.0, 1.0, 1.0, 1.0)		
			bgl.glPointSize(2)
			bgl.glBegin(bgl.GL_POINTS)		
				
			for i in range (num_segments):
				bgl.glVertex2f(dot_x + _x, dot_y +_y)
				dot_t = dot_x
				dot_x = (dot_c * dot_x - dot_s * dot_y)
				dot_y = (dot_s * dot_t + dot_c * dot_y)		
			
			

class markers_fx(bpy.types.Operator):
	  
	#tooltip
	""" Markers fX"""
	
	bl_idname = "id.markers_fx"
	bl_label = "markers_fx" 
	
	active = bpy.props.BoolProperty()
		
	def modal(self, context, event):
		
			
		if bpy.data.objects.get('markers') is None or self.active == False or context.scene.quit:
			if debug:
				print('End Markers FX')
			try:
				bpy.types.SpaceView3D.draw_handler_remove(handles[0], 'WINDOW') 
			except:
				if debug:
					print('Handler already removed')
				pass
			
			return {'FINISHED'}

		return {'PASS_THROUGH'}
		
	def execute(self, context):		
		args = (self, context)	
		#first remove previous session handler if any	
		try:			
			bpy.types.SpaceView3D.draw_handler_remove(handles[0], 'WINDOW') 
		except:
			if debug:
				print('No handlers to remove already removed')	
			pass
				
		if self.active == True:	
			if debug:
				print('Start Markers FX')
			handles[0] = bpy.types.SpaceView3D.draw_handler_add(draw_circle, args, 'WINDOW', 'POST_PIXEL')			
			context.window_manager.modal_handler_add(self)
			
			return {'RUNNING_MODAL'}	
		
		return{'CANCELLED'}
		
	

class add_marker(bpy.types.Operator):
	  
	#tooltip
	""" Add the a marker to help auto-detection """
	
	bl_idname = "id.add_marker"
	bl_label = "add_marker"
	bl_options = {'UNDO'}	
	
	first_mouse_x = bpy.props.IntProperty()
	first_value = bpy.props.FloatProperty()

	body_part = bpy.props.StringProperty(name="Body Part")
	body_width = bpy.props.FloatProperty()
	body_height = bpy.props.FloatProperty()
	
	

	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	#first create the markers objects
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			
			
			_add_marker(self.body_part)		   
			
			
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
	#then keep them movable
	def modal(self, context, event):
		context.area.tag_redraw()		 
		
		if event.type == 'MOUSEMOVE':
			delta = self.first_mouse_x - event.mouse_x
			
			_region = bpy.context.region
			_region_3d = bpy.context.space_data.region_3d
			context.object.location = bpy_extras.view3d_utils.region_2d_to_location_3d(_region, _region_3d, (event.mouse_region_x, event.mouse_region_y), bpy.context.object.location)
			
			#limits
			if context.object.location[0] < 0 or self.body_part=="neck" or self.body_part == "root" or self.body_part == "chin":
				context.object.location[0] = 0
				
			if context.object.location[0] > self.body_width/2:
				context.object.location[0] = self.body_width/2
				
			if context.object.location[2] > self.body_height:
				context.object.location[2] = self.body_height
				
			if context.object.location[2] < 0:
				context.object.location[2] = 0
	
				
		elif event.type == 'LEFTMOUSE': 
			#restore markers size
			"""
			for obj in context.selected_objects:
				obj.empty_draw_size = self.draw_size
			"""
			return {'FINISHED'}

		elif event.type in {'RIGHTMOUSE', 'ESC'}:			
			context.object.location.x = self.first_value
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}
		
	def invoke(self, context, event):
		self.execute(context)
			
		#first time launch
		if self.body_part == 'neck':
			#bpy.ops.id.markers_fx(active=False)#close previous model if already running (when opening new blend file while markers still active)
			bpy.ops.id.markers_fx(active=True)
			bpy.context.space_data.show_manipulator = False
			

		
		self.body_width = bpy.data.objects[bpy.context.scene.body_name].dimensions[0]
		self.body_height = bpy.data.objects[bpy.context.scene.body_name].dimensions[2]
	
		if context.object:
			self.first_mouse_x = event.mouse_x
			self.first_value = context.object.location.x
			
			context.window_manager.modal_handler_add(self)
			
			
			
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "No active object, could not finish")
			return {'CANCELLED'}

class auto_detect(bpy.types.Operator):
	  
	#tooltip
	""" Select the body mesh then click it to try to automatically find the reference bones location. It will add an empty marker at each bone location """
	
	bl_idname = "id.auto_detect"
	bl_label = "auto_detect"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try:
				#check if an editable mesh is selected
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.object.mode_set(mode='OBJECT')			 
			except TypeError:
				self.report({'ERROR'}, "Please select the body object")
				return{'FINISHED'}
			
			_auto_detect(self)		

			bpy.data.objects[context.scene.body_name].hide_select = False
			bpy.data.objects['rig'].hide_select = False
			bpy.data.objects['rig'].hide = False
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}

class delete_detected(bpy.types.Operator):
	  
	#tooltip
	""" Delete the detected markers """
	
	bl_idname = "id.delete_detected"
	bl_label = "delete_detected"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try:
				bpy.data.objects["auto_detect_loc"]						 
			except KeyError:
				self.report({'ERROR'}, "No markers found")
				return{'FINISHED'}
					   
			_delete_detected()		  
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
	
class delete_big_markers(bpy.types.Operator):
	  
	#tooltip
	""" Delete the markers """
	
	bl_idname = "id.delete_big_markers"
	bl_label = "delete_big_markers"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try:
				bpy.data.objects["markers"]						 
			except KeyError:
				self.report({'ERROR'}, "No markers found")
				return{'FINISHED'}
			#save current mode
			current_mode = context.mode
			active_obj = context.active_object
		
			bpy.ops.object.mode_set(mode='OBJECT')
			
			#unfreeze character selection and restore visibility
			for obj in bpy.data.objects:
				if not 'rig_add' in obj.name:
					obj.hide = False
				if obj.parent != None:
					if obj.parent.name != "rig_ui" or '_char_name' in obj.name:
						obj.hide_select = False
				else:
					obj.hide_select = False		
			
				#delete the 'arp_body_mesh' tag from objects
				if len(obj.keys()) > 0:
					if 'arp_body_mesh' in obj.keys():
						del obj['arp_body_mesh']
					
			if bpy.data.objects.get('rig') != None:				
				bpy.data.objects['rig'].hide = False
				
			_delete_big_markers()
			
			
			#restore current mode
			try:
				set_active_object(active_obj.name)
			except:
				pass
				#restore saved mode	   
			if current_mode == 'EDIT_ARMATURE':
				current_mode = 'EDIT'
		
			try:
				bpy.ops.object.mode_set(mode=current_mode)
			except:
				pass
	
					   
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
	
	
 ##########################	 FUNCTIONS	##########################

	# extra functions -------------------------------------------------------------	   
def tolerance_check(source, target, axis, tolerance, x_check):
	if source[axis] <= target + tolerance and source[axis] >= target - tolerance:
		#left side only	 
		if x_check:		 
			if source[0] > 0:
				return True
		else:			
			return True	   
			
	   
		
def tolerance_check_2(source, target, axis, axis2, tolerance):
	if source[axis] <= target[axis] + tolerance and source[axis] >= target[axis] - tolerance:
		if source[axis2] <= target[axis2] + tolerance and source[axis2] >= target[axis2] - tolerance:
			#left side only
			if source[0] > 0:
				return True
			
def tolerance_check_3(source, target, tolerance, x_check):
	if source[0] <= target[0] + tolerance and source[0] >= target[0] - tolerance:
		if source[1] <= target[1] + tolerance and source[1] >= target[1] - tolerance:
			if source[2] <= target[2] + tolerance and source[2] >= target[2] - tolerance:
				#left side only
				if x_check:
					if source[0] > 0:
						return True
				else:
					return True	   
		
def clear_selection():
	bpy.ops.mesh.select_all(action='DESELECT')

def clear_object_selection():
	bpy.ops.object.select_all(action='DESELECT')
	
def set_active_object(object_name):
	 bpy.context.scene.objects.active = bpy.data.objects[object_name]
	 bpy.data.objects[object_name].select = True

	 
def _restore_markers():
	scene = bpy.context.scene
	for item in scene.markers_save:
		if bpy.data.objects.get(item.name) == None:
			#create it if does not exist
			_add_marker(item.name[:-4])

		bpy.data.objects[item.name].location = item.location
		
	#enable markers fx
	try:
		bpy.types.SpaceView3D.draw_handler_remove(handles[0], 'WINDOW')
		if debug:
			print('Removed handler')
	except:
		if debug:
			print('No handler to remove')
		pass
	bpy.ops.id.markers_fx(active=True)
	

	
#-- start create_hand_plane()
def create_hand_plane(_bound_up, _bound_top, _bound_bot, _bound_left, _bound_right, body_height, angle1, hand_offset, body, angle2):

	bpy.ops.object.mode_set(mode='OBJECT')		  

	bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=True, location=(0.0, 0.0, _bound_up + (body_height)), rotation=(0, 0, 0))
	bpy.context.object.name = "plane_matrix"	
	#disable X Mirror
	bpy.context.active_object.data.use_mirror_x = False
	
	bpy.ops.mesh.select_all(action='DESELECT')
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	
	mesh.verts.ensure_lookup_table() #debug
	# index: 0 bot right, 1 up right, 2 bot left, 3 up left
	mesh.verts[0].co[0] = _bound_bot
	mesh.verts[0].co[1] = _bound_right
	mesh.verts[1].co[0] = _bound_top
	mesh.verts[1].co[1] = _bound_right
	mesh.verts[2].co[0] = _bound_bot
	mesh.verts[2].co[1] = _bound_left
	mesh.verts[3].co[0] = _bound_top
	mesh.verts[3].co[1] = _bound_left
	
	# rotate it according to hand rotation
	 #enlarge borders safe
	bpy.ops.mesh.select_all(action='SELECT') 
	
	bpy.ops.transform.resize(value=(1.2, 1.2, 1.2), constraint_axis=(True, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
	
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
	hand_offset[0] = bpy.context.object.location[0]
	hand_offset[1] = bpy.context.object.location[1]
	hand_offset[2] = bpy.context.object.location[2]
	
		#Y rotate
	"""
	bpy.ops.object.mode_set(mode='EDIT') 
	bpy.context.space_data.pivot_point = 'BOUNDING_BOX_CENTER'
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.transform.rotate(value=angle2, axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.00168535)
	"""

		#Z rotate				
	bpy.context.object.rotation_euler[2] = -angle1*0.8
	
	
	#subdivide it 
	bpy.ops.object.mode_set(mode='OBJECT')		
	bpy.ops.object.modifier_add(type='SUBSURF')
	bpy.context.object.modifiers["Subsurf"].subdivision_type = 'SIMPLE'
	bpy.context.object.modifiers["Subsurf"].levels = 7
	bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
	
	#get edge length
	edge_dist = 0.0
	bpy.ops.object.editmode_toggle()
	
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	mesh.edges.ensure_lookup_table() #debug	 
	edge_dist = mesh.edges[0].calc_length()
	bpy.ops.object.editmode_toggle()
	
	#shrink on body
	bpy.ops.object.modifier_add(type='SHRINKWRAP')
	bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects['hand_aligned']
	bpy.context.object.modifiers["Shrinkwrap"].wrap_method = 'PROJECT'
	bpy.context.object.modifiers["Shrinkwrap"].use_negative_direction = True
	bpy.context.object.modifiers["Shrinkwrap"].use_project_z = True 
	
	
	bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")
	
	#delete upper part
	bpy.ops.object.editmode_toggle()
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	bpy.ops.mesh.select_all(action='DESELECT')

	
	mesh.verts.ensure_lookup_table() #debug	 
	for v in mesh.verts:		
		if tolerance_check(v.co, 0.0, 2, body_height/5, False):		 
			v.select = True				   
	bpy.ops.mesh.delete(type='VERT')
	
	#check for distorted grid (no space between thumb/palm)
	bpy.ops.mesh.select_all(action='DESELECT')
	mesh.edges.ensure_lookup_table() #debug	 
	for e in mesh.edges:
		if e.calc_length() > edge_dist * 10:
			for face in e.link_faces:
				face.select = True
	
	bpy.ops.mesh.delete(type='FACE')
	
	
	
#-- end create_hand_plane()	   
	

def copy_list(list1, list2):
	for pikwik in range(0, len(list1)):
		list2[pikwik] = list1[pikwik]
		
		
def _turn(context, action):

	body = bpy.data.objects[bpy.context.scene.body_name]
	
	wise = 1
	
	if action == 'positive':
		wise = 1
	else:
		wise = -1
	
	bpy.ops.object.select_all(action='DESELECT')
	
	#restore selection visibility
	body.hide_select = False
	body_objects = []
	for obj in bpy.data.objects:
		if len(obj.keys()) > 0:
			if 'arp_body_mesh' in obj.keys():
				body_objects.append(obj)
				obj.hide = False
				obj.hide_select = False
				set_active_object(obj.name)
				print('selected', obj.name)
				
	set_active_object(body.name)
	
	#rotate from world origin
	bpy.context.space_data.cursor_location = [0.0,0.0,0.0]
	bpy.context.space_data.pivot_point = 'CURSOR'
	
	bpy.ops.transform.rotate(value=math.pi/2*wise, axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.15013)
	
	bpy.context.space_data.pivot_point = 'BOUNDING_BOX_CENTER'

	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(body.name)
	#apply rotation
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
	
	#hide from selection
	body.hide_select = True
	for obj in body_objects:
		obj.hide_select = True
		obj.hide = True
		
	set_active_object('markers')
	bpy.ops.object.select_all(action='DESELECT')	
	

# START find_finger_top() ------------------------------------------------------ 
def find_finger_top(finger_top, vertex_border, dist, finger):	
	
	clear_selection()
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	go_up = True
	mesh.verts[vertex_border.index].select = True
	count = 0

	while go_up:
	
		go_up = False
		found_right = False		
		found_up = False
		found_bot = False


		for edge in vertex_border.link_edges:		   
			for v in edge.verts:
				if v.select == False: # it not selected
					if len(v.link_faces) < 4 and len(v.link_faces) > 0: #if it's a border vert
						if v.co[0] > vertex_border.co[0]+(dist/100): #if found a right vert
							found_right = True
							v_right = v
						if v.co[1] > vertex_border.co[1]+(dist/100): #if found an up vert
							found_up = True
							v_up = v
						if v.co[1] < vertex_border.co[1]-(dist/100): #if found a bot vert
							found_bot = True
							v_bot = v					   
						
						
		if (found_right and found_up) or (found_right and not found_up):
			v_right.select = True
			go_up = True
			vertex_border = v_right
			count += 1
		
		if found_up and not found_right:
			v_up.select = True
			go_up = True
			vertex_border = v_up
			count += 1
			
		if found_bot and not found_right:
			v_bot.select = True
			go_up = True
			vertex_border = v_bot
			count += 1
			


	copy_list(vertex_border.co, finger_top) 
 
	return vertex_border
				
	

 

def find_finger_bot(finger_bot, vertex_border, dist, phal_1_pos, phal_2_pos, finger_type, middle_bot):
	
	#clear_selection()
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	go_down = True

	finger_top_vert= [0.0,0.0,0.0]
	copy_list(finger_bot, finger_top_vert)	 
	finger_top_vert_index = vertex_border.index
	found_phal_1 = False
	found_phal_2 = False 
	count = 0
	x_min = 0
	direction_tolerance = 2
	
 
	while go_down:
	
		go_down = False
		found_left = False	   
		found_up = False
		found_bot = False

		for edge in vertex_border.link_edges:		   
			for v in edge.verts:
				if v.select == False: # it not selected
					if len(v.link_faces) < 4 and len(v.link_faces) > 0: #if it's a border vert
						if v.co[0] < vertex_border.co[0]-(dist/100): #if found a left vert
							found_left = True
							v_left = v
						if v.co[1] > vertex_border.co[1]+(dist/100): #if found an up vert
							found_up = True
							v_up = v
						if v.co[1] < vertex_border.co[1]-(dist/100): #if found a bot vert
							found_bot = True
							v_bot = v					   
						
						
		if (found_left and found_up) or (found_left and not found_up):
			v_left.select = True
			go_down = True
			vertex_border = v_left
			count += 1
		
		if found_up and not found_left:
			v_up.select = True
			go_down = True
			vertex_border = v_up
			count += 1
			
		if found_bot and not found_left:
			v_bot.select = True
			go_down = True
			vertex_border = v_bot
			count += 1
									
									
					  
	
	copy_list(vertex_border.co, finger_bot) 
	
	# Find the 2 phalanxes positions		  
	clear_selection()
	mesh.verts.ensure_lookup_table() #debug	  
	mesh.verts[finger_top_vert_index].select = True
	lower_bound = 1000
	_finger_bot = [0,0,0]
	copy_list(finger_bot, _finger_bot)
	
	if finger_type == "index":
		_finger_bot[0] = middle_bot[0]
	
	phal1_count = 0	   
	while found_phal_1 == False and phal1_count < 50:
		phal1_count += 1
		bpy.ops.mesh.select_more()
		
		# find the lower bound of the selection
		for mv in mesh.verts:
			mesh.verts.ensure_lookup_table() #debug				
			if mv.select == True:
				if mv.co[0] < lower_bound:
					lower_bound = mv.co[0]
					
		# if it's lower than 1/3 of the finger, set the vert pos as the phalanx pos
		if lower_bound <= (finger_top_vert[0] - (finger_top_vert[0]-_finger_bot[0])/3):
			# select the last line only
			for mv in mesh.verts:
				mesh.verts.ensure_lookup_table() #debug				
				if mv.select == True:
					if not tolerance_check(mv.co, lower_bound, 0, 0.0001, False):
						mv.select = False					 
			
			copy_list(find_selection_center(), phal_1_pos)				 

			
			found_phal_1 = True
	
			
	phal2_count = 0
	while found_phal_2 == False and phal2_count < 50:
		phal2_count += 1
		bpy.ops.mesh.select_more()
		# find the lower vert in selection
		for mv2 in mesh.verts:
			mesh.verts.ensure_lookup_table() #debug				
			if mv2.select == True:
				if mv2.co[0] < lower_bound:
					lower_bound = mv2.co[0]
					
		# if it's lower than 2/3 of the finger, set the vert pos as the phalanx pos
		if lower_bound <= (finger_top_vert[0] - ((finger_top_vert[0]-_finger_bot[0])/3)*2):
			# select the last line only
			for mv3 in mesh.verts:
				mesh.verts.ensure_lookup_table() #debug				
				if mv3.select == True:
					if not tolerance_check(mv3.co, lower_bound, 0, 0.0001, False):
						mv3.select = False
						
			# find the center of this line							 
			copy_list(find_selection_center(), phal_2_pos)						  
	  
			found_phal_2 = True
	
	if phal1_count > 49 or phal2_count > 49:
		bpy.context.scene.fingers_to_detect = 'NONE'

	return vertex_border

# end find_finger_bot() ------------------------------------------------------

def find_thumb_phalanxes(thumb_top, thumb_bot, phal_1_pos, phal_2_pos, body_height):
	
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)	  
  
	found_phal_1 = False
	found_phal_2 = False 
	
	
	# Find the 2 phalanxes positions		  
	
	mesh.verts.ensure_lookup_table() #debug	  
		#select top vertice
	clear_selection()
	has_selected = False
	sel_radius = body_height/400
	vert_selection = []
	
	while has_selected == False:
		sel_radius += body_height/600		 
		for v in mesh.verts:				
			if tolerance_check_3(v.co, thumb_top, sel_radius, False):
				v.select = True
				has_selected = True
				vert_selection.append(v)
		  
	  
	lower_bound = 1000 
	phal1_count = 0
	
	dist_thumb = (thumb_bot-vectorize3(thumb_top)).magnitude
	dist_to_bot = dist_thumb
	
	while found_phal_1 == False and phal1_count < 50:
		phal1_count += 1
		bpy.ops.mesh.select_more()
		
		
		#exclude the previous verts from selection
		mesh.verts.ensure_lookup_table()
		for vert in vert_selection:
			vert.select = False 
		
		
		# find the newly selected verts - thumb_bot distances
		mesh.verts.ensure_lookup_table() #debug 
		for mv in mesh.verts:						
			if mv.select:
				#store selected vert
				vert_selection.append(mv)
				#calculate dist
				current_dist = (mv.co - thumb_bot).magnitude
				
				if current_dist < dist_to_bot:
					dist_to_bot = current_dist				
		
		# if it's lower than 1/4 of the finger, set the vert pos as the phalanx pos
		if dist_to_bot <= dist_thumb*0.75:			
			copy_list(find_selection_center(), phal_1_pos)				
			found_phal_1 = True		
			
	
	phal2_count = 0 
	while found_phal_2 == False and phal2_count < 50:
		phal2_count += 1
		bpy.ops.mesh.select_more()		
		
		#exclude the previous verts from selection
		mesh.verts.ensure_lookup_table()
		for vert in vert_selection:
			vert.select = False			
		
		# find the newly selected verts - thumb_bot distances
		mesh.verts.ensure_lookup_table() #debug 
		for mv in mesh.verts:						
			if mv.select:
				#store selected vert
				vert_selection.append(mv)
				#calculate dist
				current_dist = (mv.co - thumb_bot).magnitude
		
				if current_dist < dist_to_bot:
					dist_to_bot = current_dist				
			
					
		# if it's lower than 1/4 of the finger, set the vert pos as the phalanx pos
		if dist_to_bot <= dist_thumb*0.5:			
			copy_list(find_selection_center(), phal_2_pos)				
			found_phal_2 = True		
			
			
	if phal1_count > 49 or phal2_count > 49:
		bpy.context.scene.fingers_to_detect = 'NONE'

def find_selection_center():	
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	c_x = []
	c_y = []
	c_z = []
	total_x = 0
	total_y = 0
	total_z = 0			   
	center = [0,0,0]

	for vert in mesh.verts:
		if vert.select == True:
			c_x.append(vert.co[0])
			c_y.append(vert.co[1])
			c_z.append(vert.co[2])
			
	for v in c_x:
		total_x += v				
	for v in c_y:
		total_y += v				
	for v in c_z:
		total_z += v
		
	center[0] = total_x/len(c_x)
	center[1] = total_y/len(c_y)
	center[2] = total_z/len(c_z)
	
	return center 

def create_empty_loc(radii, pos, name):
	bpy.ops.object.empty_add(type='PLAIN_AXES', radius = radii, view_align=True, location=(pos), rotation=(0, 0, 0))  
	# rename it		
	bpy.context.object.name = name + "_auto"
	# parent it
	bpy.context.object.parent = bpy.data.objects["auto_detect_loc"]
	
def vectorize3(list):
	return Vector((list[0], list[1], list[2]))

def init_selection(active_bone):
	try:
		bpy.ops.armature.select_all(action='DESELECT')
	except:
		pass
	bpy.ops.object.mode_set(mode='POSE')
	bpy.ops.pose.select_all(action='DESELECT')
	if (active_bone != "null"):
		bpy.context.object.data.bones.active = bpy.context.object.pose.bones[active_bone].bone #set the active bone for mirror
	bpy.ops.object.mode_set(mode='EDIT')
	
def mirror_hack():
	bpy.ops.transform.translate(value=(0, 0, 0), constraint_orientation='NORMAL', proportional='DISABLED')
   
def get_edit_bone(name):
	return bpy.context.object.data.edit_bones[name]

def get_object(name):
	return bpy.data.objects[name]
	
	# CLASS FUNCTIONS -------------------------------------------------------------	  
	
def _match_ref(self):
	
	print('\nMatching the reference bones...')
	
	scene = bpy.context.scene
	#scale the rig object according to the character height
	b_name = scene.body_name

	bpy.context.object.dimensions[2] = bpy.data.objects[b_name].dimensions[2] * 5.1
	bpy.context.object.scale[1] = bpy.context.object.scale[2] 
	bpy.context.object.scale[0] = bpy.context.object.scale[2] 

	bpy.ops.object.mode_set(mode='EDIT')
		#enable x-axis mirror edit
	bpy.context.object.data.use_mirror_x = True
		
	#display all layers
	_layers = bpy.context.object.data.layers	
	for i in range(0,31):	
		_layers[i] = True 
	
	side = ".l"
	
	rig_matrix_world = bpy.data.objects["rig"].matrix_world.inverted()
	
	
	# FOOT
	init_selection("foot_ref"+side)
	foot = get_edit_bone("foot_ref"+side)	 
	foot.head = rig_matrix_world * get_object("ankle_loc_auto").location
	foot.tail = rig_matrix_world * get_object("toes_start_auto").location
	bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
	mirror_hack()
	
	init_selection("toes_ref"+side)
	toes_ref = get_edit_bone("toes_ref"+side)	 
	toes_ref.head = rig_matrix_world * get_object("toes_start_auto").location
	toes_ref.tail = rig_matrix_world * get_object("toes_end_auto").location
	bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
	mirror_hack()
	
	init_selection("toes_end_ref"+side)
	toes_end_ref = get_edit_bone("toes_end_ref"+side)
	toes_end_auto = get_object("toes_end_auto").location  
	toes_end_ref.head = rig_matrix_world * vectorize3([toes_end_auto[0], toes_end_auto[1], 0])
	toes_end_ref.tail = toes_end_ref.head + vectorize3([0,0,0.01])
	mirror_hack()
	
	init_selection("foot_bank_01_ref"+side)
	foot_bank_01_ref = get_edit_bone("foot_bank_01_ref"+side)
	bank_right = get_object("bank_left_loc_auto").location	 
	foot_bank_01_ref.head = rig_matrix_world * bank_right
	foot_bank_01_ref.tail = foot_bank_01_ref.head + (scene.foot_dir.normalized() * get_edit_bone('foot_ref'+side).length*0.2)
	mirror_hack()
	
	init_selection("foot_bank_02_ref"+side)
	foot_bank_02_ref = get_edit_bone("foot_bank_02_ref"+side)
	bank_left = get_object("bank_right_loc_auto").location	
	foot_bank_02_ref.head = rig_matrix_world * bank_left
	foot_bank_02_ref.tail = foot_bank_02_ref.head + (scene.foot_dir.normalized() * get_edit_bone('foot_ref'+side).length*0.2)
	mirror_hack()
	
	init_selection("foot_heel_ref"+side)
	foot_heel_ref = get_edit_bone("foot_heel_ref"+side)
	heel_auto = get_object("bank_mid_loc_auto").location
	foot_heel_ref.head = rig_matrix_world * heel_auto
	foot_heel_ref.tail = foot_heel_ref.head + (scene.foot_dir.normalized() * get_edit_bone('foot_ref'+side).length*0.2)
	mirror_hack()
	
	toes_end_auto = get_object("toes_end_auto").location 
	heel_auto = get_object("bank_mid_loc_auto").location
	foot_length = (toes_end_auto - heel_auto).magnitude
	
		# toes fingers
	toes_list=["toes_pinky", "toes_ring", "toes_middle", "toes_index", "toes_thumb"]
	foot_bank_01_ref = get_edit_bone("foot_bank_01_ref"+side)
	foot_bank_02_ref = get_edit_bone("foot_bank_02_ref"+side)
	toes_ref = get_edit_bone("toes_ref"+side)
	
	foot_dir = rig_matrix_world * (toes_end_auto - heel_auto)
	
	#Disable mirror for toes, not selection based
	bpy.context.object.data.use_mirror_x = False
	
	_sides = ['.l', '.r']
	
	for _side in _sides:
		foot_bank_01_ref = get_edit_bone("foot_bank_01_ref"+_side)
		foot_bank_02_ref = get_edit_bone("foot_bank_02_ref"+_side)
		toes_ref = get_edit_bone("toes_ref"+_side)
			
		if _side == '.r':
			foot_dir[0] *= -1
		
		for t in range(0,5):
			max = 4
			if t == 4:
				max = 3 #thumb has less phalanges
			for p in range (1,max):			
				bone = get_edit_bone(toes_list[t] + str(p) + "_ref" + _side)				
				
				bone.head = (foot_bank_01_ref.head + ((foot_bank_02_ref.head - foot_bank_01_ref.head) * t) / 5)
				bone.head += foot_dir * 0.75 + (((foot_dir * 0.25) * p) / max)			
				bone.head[2] = toes_ref.head[2]
				
				#if last phalanges				
				if p == max-1:
					bone.tail = bone.head + ((foot_dir * 0.25) /max)					
					
			
	bpy.context.object.data.use_mirror_x = True
	
				

	# LEGS
	init_selection("thigh_ref"+side)
	thigh_ref = get_edit_bone("thigh_ref"+side)
	knee_auto = get_object("knee_loc_auto").location  
	thigh_ref.tail = rig_matrix_world * knee_auto
	thigh_ref.head = rig_matrix_world * get_object("leg_loc_auto").location	 
	mirror_hack()
	
	init_selection("bot_bend_ref"+side)
	bot_bend_ref = get_edit_bone("bot_bend_ref"+side)
	bot_auto = get_object("bot_empty_loc_auto").location  
	bot_bend_ref.head = rig_matrix_world * bot_auto

	bot_bend_ref.tail = bot_bend_ref.head + (rig_matrix_world * vectorize3([0, foot_length/4, 0]))
	mirror_hack()
	
		#disable it by default
	auto_rig._disable_limb(self, bpy.context)
		#display all layers again 
	for i in range(0,31):	
		_layers[i] = True 
	
	
	# SPINE
	init_selection("root_ref.x")
	root_ref = get_edit_bone("root_ref.x")
	root_auto = get_object("root_loc_auto").location  
	root_ref.head = rig_matrix_world * root_auto
	root_ref.tail = rig_matrix_world * get_object("spine_01_loc_auto").location
	
	init_selection("spine_01_ref.x")
	spine_01_ref = get_edit_bone("spine_01_ref.x")	 
	spine_01_ref.tail = rig_matrix_world * get_object("spine_02_loc_auto").location
	
	init_selection("spine_02_ref.x")
	spine_02_ref = get_edit_bone("spine_02_ref.x")	 
	spine_02_ref.tail = rig_matrix_world * get_object("neck_loc_auto").location 
	
	init_selection("neck_ref.x")
	neck_ref = get_edit_bone("neck_ref.x")
	neck_ref.head = rig_matrix_world * get_object("neck_loc_auto").location
	neck_ref.tail = rig_matrix_world * get_object("head_loc_auto").location
	
	init_selection("head_ref.x")
	head_ref = get_edit_bone("head_ref.x")
	head_ref.tail = rig_matrix_world * get_object("head_end_loc_auto").location
	
	init_selection("breast_01_ref"+side)
	breast_01_ref = get_edit_bone("breast_01_ref"+side)
	breast_01_ref.head = rig_matrix_world * get_object("breast_01_loc_auto").location
	spine_02_ref = get_edit_bone("spine_02_ref.x")	 
	breast_01_ref.tail = breast_01_ref.head + (vectorize3([0,0,(spine_02_ref.tail[2]-spine_02_ref.head[2])*0.3]))
	mirror_hack()
	
	init_selection("breast_02_ref"+side)
	breast_02_ref = get_edit_bone("breast_02_ref"+side)
	breast_02_ref.head = rig_matrix_world * get_object("breast_02_loc_auto").location
	spine_02_ref = get_edit_bone("spine_02_ref.x")	 
	breast_02_ref.tail = breast_02_ref.head + vectorize3([0,0,(spine_02_ref.tail[2]-spine_02_ref.head[2])*0.3])
	mirror_hack()
	
	# ARMS
	init_selection("shoulder_ref"+side)
	shoulder_ref = get_edit_bone("shoulder_ref"+side)	 
	shoulder_ref.head = rig_matrix_world * get_object("shoulder_base_loc_auto").location
	shoulder_ref.tail = rig_matrix_world * get_object("shoulder_loc_auto").location
	mirror_hack()
	
	init_selection("arm_ref"+side)
	arm_ref = get_edit_bone("arm_ref"+side)	   
	arm_ref.tail = rig_matrix_world * get_object("elbow_loc_auto").location
	mirror_hack()
	
	init_selection("forearm_ref"+side)
	forearm_ref = get_edit_bone("forearm_ref"+side)	   
	forearm_ref.tail = rig_matrix_world * get_object("hand_loc_auto").location
	mirror_hack()
	
	
	init_selection("hand_ref"+side)
	hand_ref = get_edit_bone("hand_ref"+side)
	
	#check if fingers are detected
	if scene.fingers_to_detect != 'NONE':
		hand_ref.tail = hand_ref.head + (rig_matrix_world*get_object("middle_top_auto").location - hand_ref.head)*0.4
	   
	else:
		forearm_ref = get_edit_bone("forearm_ref"+side)
		hand_ref.tail = hand_ref.head + ((forearm_ref.tail - forearm_ref.head)/3)
		
		#hand roll
	bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')

	mirror_hack()
	
	
	# FINGERS --------------------------------------------
	
	#disable or enable pinky (only 4 or 5 fingers detection atm)
	if scene.fingers_to_detect == '4':
		bpy.context.object.rig_pinky = False
	else:
		bpy.context.object.rig_pinky = True

		# make list of fingers bones
	finger_bones = []		 
	init_selection("hand_ref"+side)
	bpy.ops.armature.select_similar(type='CHILDREN')
	
	for bone in bpy.context.object.data.edit_bones:
			if bone.select and bone.name != "hand_ref"+side:
				finger_bones.append(bone.name)	

	bpy.ops.armature.select_all(action='DESELECT')
	
	#reset fingers transforms if it's the second time the button is pressed
	if len(scene.fingers_init_transform) > 0:
		for i in finger_bones:
			current_bone = get_edit_bone(i)
			try:
				current_bone.head = scene.fingers_init_transform[i].head
				current_bone.tail = scene.fingers_init_transform[i].tail
				current_bone.roll = scene.fingers_init_transform[i].roll
			except:
				pass
		
	#save initial fingers transform in the property collection if it's the first time the button is pressed
	if len(scene.fingers_init_transform) == 0:
		for i in finger_bones:
			current_bone = get_edit_bone(i)
			item = scene.fingers_init_transform.add()		
			item.name = i  
			item.head = current_bone.head
			item.tail = current_bone.tail
			item.roll = current_bone.roll

		#root
	fingers = ["thumb", "index", "middle", "ring", "pinky"]	   
		
	fingers_root = ["index1_base_ref"+side, "middle1_base_ref"+side, "ring1_base_ref"+side, "pinky1_base_ref"+side]
	
	if scene.fingers_to_detect != 'NONE':
	   
		auto_root = ["index_root_auto", "middle_root_auto", "ring_root_auto", "pinky_root_auto"]
		
		
		for i in range(0, len(fingers_root)):
			#if the detection marker exists
			if bpy.data.objects.get(auto_root[i]) != None:
				init_selection(fingers_root[i])		 
				root_ref = get_edit_bone(fingers_root[i])
				root_ref.head = rig_matrix_world * get_object(auto_root[i]).location
				root_ref.tail = rig_matrix_world * get_object(fingers[i+1]+"_bot_auto").location
				
				if self.arm_angle < 40:
					bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
				if self.arm_angle > 40:
					bpy.ops.armature.calculate_roll(type='GLOBAL_POS_X')
						
				mirror_hack()	
			
		
	   
		for f in range(0,5):
			#if the detection marker exists
			if bpy.data.objects.get(fingers[f]+"_bot_auto") != None:
				#bot
				init_selection(fingers[f]+"1_ref"+side)		 
				finger_bot = get_edit_bone(fingers[f]+"1_ref"+side)
				finger_bot.head = rig_matrix_world * get_object(fingers[f]+"_bot_auto").location
				finger_bot.tail = rig_matrix_world * get_object(fingers[f]+"_phal_2_auto").location
				if f != 0: #not thumb				
					if self.arm_angle < 40:
						bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
					if self.arm_angle > 40:
						bpy.ops.armature.calculate_roll(type='GLOBAL_POS_X')
				else:
					bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Y')

				mirror_hack()
				#phal1
				init_selection(fingers[f]+"2_ref"+side)
				finger_phal_1 = get_edit_bone(fingers[f]+"2_ref"+side)
				finger_phal_1.tail = rig_matrix_world * get_object(fingers[f]+"_phal_1_auto").location
				if f != 0: #not thumb
					if self.arm_angle < 40:
						bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
					if self.arm_angle > 40:
						bpy.ops.armature.calculate_roll(type='GLOBAL_POS_X')
				else:
					bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Y')
					
				mirror_hack()
				#phal2
				init_selection(fingers[f]+"3_ref"+side)
				finger_phal_2 = get_edit_bone(fingers[f]+"3_ref"+side)
				finger_phal_2.tail = rig_matrix_world * get_object(fingers[f]+"_top_auto").location
				if f != 0: #not thumb
					if self.arm_angle < 40:
						bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
					if self.arm_angle > 40:
						bpy.ops.armature.calculate_roll(type='GLOBAL_POS_X')
				else:
					bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Y')
				mirror_hack()
			
	else:#no finger detection case		 
			  
	  
		# Offset all finger bones close the hand bone
			# calculate offset vector
		rig_scale = bpy.data.objects["rig"].scale[0]
		offset_vec = (get_edit_bone("hand_ref"+side).tail - get_edit_bone("index1_base_ref"+side).head)*rig_scale	

		for b in finger_bones:
			get_edit_bone(b).select = True
	  
		bpy.ops.object.mode_set(mode='POSE') 
		bpy.ops.object.mode_set(mode='EDIT')		   
		bpy.ops.transform.translate(value=(offset_vec), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=True, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.0922959)
		
		bpy.ops.armature.select_all(action='DESELECT')
		
	# FACIAL
	facial_bones = auto_rig_datas.facial_ref

	# Offset all facial bones close the head ref bone

		# calculate offset vector
	rig_scale = bpy.data.objects["rig"].scale[0]
	head_ref = get_edit_bone("head_ref.x")
	head_length = head_ref.tail[2] - head_ref.head[2]
	offset_pos = get_edit_bone("neck_ref.x").tail + vectorize3([0,-head_length*2,0])
	offset_vec = (offset_pos - get_edit_bone("nose_01_ref.x").head)
	
	#jawbone height
	if bpy.data.objects.get("chin_loc"):		
		offset_vec[2] = (rig_matrix_world * bpy.data.objects["chin_loc"].location)[2] - get_edit_bone("jaw_ref.x").tail[2]
	
	offset_vec *= rig_scale
	
	bpy.ops.armature.select_all(action='DESELECT')

	for b in facial_bones:
		try:
			get_edit_bone(b).select = True
		except:
			pass
	
	bpy.ops.object.mode_set(mode='POSE') 
	bpy.ops.object.mode_set(mode='EDIT')	

	bpy.ops.transform.translate(value=(offset_vec), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=True, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.0922959)
	
	#check Use Chin for skinning
	scene.bind_chin = True
	
	#display layer 17 only			
	for i in range(0,31):
		if i != 17:
			_layers[i] = False 
	
	
		
	
	bpy.ops.armature.select_all(action='DESELECT')

	
		
	
def _add_marker(name):
	
	body = bpy.data.objects[bpy.context.scene.body_name]
	body_height = body.dimensions[2]
	scaled_radius = 0.0#body_height/20
	
	#apply mesh rotation
	set_active_object(body.name)
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)


	bpy.ops.object.mode_set(mode='OBJECT')
	
	# create an empty group for the markers
	try:
		#if the detect group already exist, don't create it
		bpy.data.objects["markers"]		  
	
	except KeyError:
		# if not create it
		bpy.ops.object.empty_add(type='PLAIN_AXES', radius = scaled_radius, view_align=False, location=(0,0,0), rotation=(0, 0, 0))	  
		bpy.context.object.name = "markers"
	
	# create the marker if not exists already
	try: #it already exists
		bpy.ops.object.select_all(action='DESELECT')

		bpy.data.objects[name+"_loc"].select = True
		set_active_object(name+"_loc")
	except KeyError:
		#create it
		bpy.ops.object.empty_add(type='PLAIN_AXES', radius = scaled_radius, view_align=False, location=(0,0,0), rotation=(0, 0, 0))	 
		bpy.context.object.empty_draw_type = 'CIRCLE'
		bpy.context.object.empty_draw_size = scaled_radius	  
		# rename it		
		bpy.context.object.name = name + "_loc"
		# parent it
		bpy.context.object.parent = bpy.data.objects["markers"]
		#enable xray
		bpy.context.active_object.show_x_ray = True
		
		
		if name == "shoulder" or name == "hand" or name == "foot":
			#limit mirror axis			
			cns = bpy.context.active_object.constraints.new('LIMIT_LOCATION')
			cns.use_min_x = True
			cns.use_transform_limit = True
	
			# create mirror object with constraint
			bpy.ops.object.empty_add(type='PLAIN_AXES', radius = scaled_radius, view_align=False, location=(0,0,0), rotation=(0, 0, 0))	 
			bpy.context.active_object.empty_draw_type = 'CIRCLE'
			bpy.context.active_object.empty_draw_size = scaled_radius
			# rename it		
			bpy.context.active_object.name = name + "_sym_loc"
			# parent it
			bpy.context.active_object.parent = bpy.data.objects["markers"]
			#enable xray
			bpy.context.active_object.show_x_ray = True
			#add mirror constraint			
			cns = bpy.context.active_object.constraints.new('COPY_LOCATION')
			cns.target = bpy.data.objects[name+"_loc"]
			cns.invert_x = True
			
			#select back the main empty
			set_active_object(name+"_loc")
			
	# markers specific options

	if name == "neck" or name == "root" or name == "chin":
		bpy.context.active_object.lock_location[0] = True
	
	
	   
		  
def _auto_detect(self): 	
	
	scene = bpy.context.scene
	print("\nAuto-Detecting... \n")

	#get character mesh name
	body = bpy.data.objects[scene.body_name]
	
	#apply transforms
	bpy.ops.object.select_all(action='DESELECT')
	body.select = True
	scene.objects.active = body
	bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
	
	#get its dimension
	body_width = body.dimensions[0]
	body_height = body.dimensions[2]
	body_depth = body.dimensions[1]
	
	hand_offset = [0,0,0]

	# create an empty group for the auto detected empties
		#delete existing if any
	for obj in bpy.data.objects:
		if obj.type == 'EMPTY':			
			if 'auto_detect_loc' in obj.name:
				if len(obj.children) == 0:				
					bpy.data.objects.remove(obj, True)
					
					
	_delete_detected()		
	
		# create it
	bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, view_align=True, location=(0,0,0), rotation=(0, 0, 0))	
	bpy.context.object.name = "auto_detect_loc"
	bpy.ops.object.select_all(action='DESELECT')


	# get the loc guides
	foot_loc = bpy.data.objects["foot_loc"]
	hand_loc = bpy.data.objects["hand_loc"]

		#enter character mesh edit mode
	body.select = True
	scene.objects.active = body
	bpy.ops.object.mode_set(mode='EDIT')
		#check for hidden vertices, can't be accessed if hidden
	bpy.ops.mesh.reveal()
	bpy.ops.mesh.select_all(action='DESELECT')

	#get the mesh (in edit mode only)
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	
	# HAND DETECTION -------------------------------------------------------
	
	if debug:
		print("find hands boundaries...\n")
	
	
	# Find the wrist center
		#select vertices around hand_loc
	
	print("find wrist...\n")

	#find wrist center and bounds by raycast
	my_tree = BVHTree.FromBMesh(mesh)
	ray_origin = hand_loc.location + vectorize3([0,-body_depth,0])
	ray_dir = vectorize3([0,body_depth*4,0])
	
	hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude)	   
	if hit == None or distance < 0.001:		
		print('    Could not find wrist front, marker out of mesh') 
	else:	
		wrist_bound_front = hit[1]
		have_hit = True
		last_hit = hit
		#iterate if multiples faces layers
		while have_hit:
			have_hit = False
			hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
			if hit != None:						
				have_hit = True
				last_hit = hit
				
		wrist_bound_back = last_hit[1]
	

	try:
		wrist_bound_back
	except:
		self.report({'ERROR'}, "No wrist vertices found, check the wrist maker position. Is it on mesh?")
	
	hand_loc_x = hand_loc.location[0]
	hand_loc_y = wrist_bound_back + ((wrist_bound_front - wrist_bound_back)*0.4)
	hand_loc_z = hand_loc.location[2]	 
	hand_empty_loc = [hand_loc_x, hand_loc_y, hand_loc_z]

   
	# FINGERS DETECTION	
	
	print("find fingers...\n")
		
	#initialize the hand rotation by creating a new hand mesh horizontally aligned
		#find the arm angle
	shoulder_pos = bpy.data.objects["shoulder_loc"].location
	arm_angle = Vector((hand_loc.location - shoulder_pos)).angle(Vector((1,0,0)))
	
	if debug:
		print('      Arm Angle:', math.degrees(arm_angle))
		
	self.arm_angle = math.degrees(arm_angle)
	
	body.hide_select = False
	bpy.ops.object.mode_set(mode='OBJECT')
	set_active_object(body.name)
	bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
	bpy.context.active_object.name = 'hand_aligned'
		#remove shape keys if any
	try:
		bpy.ops.object.shape_key_remove(all=True)
	except:
		pass
	
	
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='DESELECT')
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	
		#select the hand	
	for v in mesh.verts:	
		if v.co[0] < hand_loc.location[0] or v.co[2] < body_height*0.25:
			v.select = True
	
	bpy.ops.mesh.delete(type='VERT')
		#save current pivot mode
	pivot_mod = bpy.context.space_data.pivot_point
		#change for cursor
	bpy.context.space_data.pivot_point = 'CURSOR'
	bpy.context.space_data.cursor_location = shoulder_pos
	bpy.ops.mesh.select_all(action='SELECT')
		#rotate the hand to horizontal
	bpy.ops.transform.rotate(value=-arm_angle*1.3, axis=(0, 1, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=True, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.179859)
	
	
	#find the hand boundaries  
	bound_left = -10000	
	bound_right = 10000
	bound_top = 0.0
	bound_bot = 10000
	bound_up = 0.0	  
	middle_top = 0 # vertex id at the top of the middle finger
	clear_selection()
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	for i in mesh.verts:
		
		mesh.verts.ensure_lookup_table() #debug
		vert_x = i.co[0]
		vert_y = i.co[1]  
		vert_z = i.co[2]	  
		if vert_y > bound_left:
			bound_left = vert_y
		if vert_y < bound_right:
			bound_right = vert_y
		if vert_x < bound_bot:
			bound_bot = vert_x
		if vert_x > bound_top:
			bound_top = vert_x
			middle_top = i.index
		if vert_z > bound_up:
			bound_up = vert_z

	
	if scene.fingers_to_detect != 'NONE' :
		
		bpy.ops.object.mode_set(mode='OBJECT')
		
		bpy.ops.object.select_all(action='DESELECT')	
		set_active_object('hand_loc')
		
		#rotate the marker horizontal
		bpy.ops.transform.rotate(value=-arm_angle*1.3, axis=(0, 1, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.179859)
		
		set_active_object('hand_aligned')
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='DESELECT')
		mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
		

				
			# find the hand rotation by finding the middle(longer) finger angle
		finger_end_center = [0,0,0]
		finger_start_center = [0,0,0]
		mesh.verts.ensure_lookup_table() #debug	 
		mesh.verts[middle_top].select = True	
		selected_length = 0.0
		current_length = 0.0
		start = True
		vertex_top = -10000
		vertex_top_loc = None
		separate_phalanx = False
		
		if debug:
			print('    find longer finger direction...\n')
		iteration = 0
		while selected_length < (bound_top - bound_bot)/3.5 and separate_phalanx == False:
			
			bpy.ops.mesh.select_more()
			bpy.ops.view3d.snap_cursor_to_selected()
			
			if start == True:
				copy_list(bpy.context.space_data.cursor_location, finger_end_center)
			
				start = False 
					 
			else:
				copy_list(bpy.context.space_data.cursor_location, finger_start_center)
				if debug:
					print('    finger start center:', finger_start_center)
				
			
			#if iteration > 8:
			#	print(br)
			
			iteration += 1
		  

			#find the selected length
			for v in mesh.verts:
				if v.select == True:
					if v.co[0] < bound_top - selected_length:				 
						selected_length = bound_top - v.co[0]
						
					if v.co[2] > vertex_top:
						vertex_top = v.co[2]
						vertex_top_loc = v.co
						
			
			# check if separate phalanx case to avoid infinite loop
			if debug:
				print("    selected length = ", selected_length, " current_length = ", current_length)
			if selected_length > current_length:
				current_length = selected_length
			elif selected_length == current_length:
				separate_phalanx = True
				

		
		if debug:
			print('    finger cut =', vertex_top_loc, '... \n')
			

		if finger_start_center[2] == 0:
			print("    Non standard fingers, skip fingers detection\n")
			scene.fingers_to_detect = 'NONE'
		
	
	if scene.fingers_to_detect != 'NONE':
		finger_start_x = [finger_start_center[0], finger_start_center[1], 0.0] 
		finger_end_x = [finger_end_center[0], finger_end_center[1], 0.0]   
		
		finger_start_y = [finger_start_center[0], 0.0, finger_start_center[2]] 
		finger_end_y = [finger_end_center[0], 0.0, finger_end_center[2]]
		
		if debug:
			print("    find finger angle...\n")					   
		   
		#calculate X angle
		v1 = Vector((finger_end_x)) - Vector((finger_start_x)) 
		v2 = Vector((1, 0, 0))
	   
		try:
			angle_1 = v1.angle(v2)
		except ValueError:
			angle_1 = 0
			print("\n ERROR: Can't find hand location -> can't find hand angle")
			
		if angle_1 > pi * 0.5:
			angle_1 = pi - angle_1
		if finger_end_x[1] > finger_start_x[1]:
			angle_1 *= -1
			
		 #calculate Y angle
		v2 = Vector((finger_end_y)) - Vector((finger_start_y)) 
		v3 = Vector((1, 0, 0))
	   
		try:
			angle_2 = v2.angle(v3)
		except ValueError:
			angle_2 = 0
			print("\n ERROR: Can't find hand location -> can't find hand angle")
			
		if angle_2 > pi * 0.5:
			angle_2 = pi - angle_2
		if finger_end_y[1] > finger_start_y[1]:
			angle_2 *= -1

		finger_normal = -(v2.cross(vectorize3([0,1,0]))).normalized()
	
			
		f_dist = 1.0
		has_found = False
		
		#find finger thickness with raycast
		my_tree = BVHTree.FromBMesh(mesh)
	
		ray_origin1 = Vector((finger_start_center))#vertex_top_loc
		counter = 0
		global_counter = 0
		
		while has_found == False:
			
			hit, normal, index, distance = my_tree.ray_cast(ray_origin1, finger_normal, f_dist)#additional vector to avoid self overlap			
			if hit == None:
				#ray_origin1 += finger_normal.normalized() * 0.001
				f_dist += 0.01
				if debug:
					print('    origin = ', ray_origin1, 'normal = ', finger_normal.normalized(), 'hit = ', hit)				
				counter += 1
				global_counter += 1
				
				if counter > 30:
					#try inversing the ray in case of very curved fingers					
					print('    Inversing raycast direction, curved fingers?')
					finger_normal =	 -finger_normal
					f_dist = 1.0
					counter = 1
					
				if debug:	
					print('    Add length to find finger thickness\n')
					
				if global_counter > 100:
					print("Non standard fingers, exit detection!")
					has_found = True
					f_thickness = 0.0
					scene.fingers_to_detect = 'NONE'
			else:
				top_hit, normal, index, distance = my_tree.ray_cast(ray_origin1, -finger_normal, f_dist)
				if top_hit != None:
					if debug:
						print('    top hit = ', top_hit, 'hit = ', hit, 'ray_origin1 = ', ray_origin1, 'normal = ', -finger_normal)
					f_thickness = (hit - top_hit).magnitude*0.3 #(hit-vertex_top_loc).magnitude*0.3			  
					has_found = True
				else:
					print('    Cannot find top finger surface for finger thickness')
					f_thickness = (hit-vertex_top_loc).magnitude*0.3			  
					has_found = True
				if debug:
					print("    Finger thickness ray data:", "origin:", ray_origin1, 'hit:', hit, 'f_dist:', f_dist)
	  
		if debug:
			print("    create hand matrix ...\n")
			
		#create plane matrix
		
		create_hand_plane(bound_up, bound_top, bound_bot, bound_left, bound_right, body_height, angle_1, hand_offset, body, angle_2)		
		
		bpy.context.space_data.cursor_location = shoulder_pos
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')	
		
		
		#rotate back to original coords
		set_active_object('hand_loc')
		set_active_object('plane_matrix')			
		
		bpy.ops.transform.rotate(value=arm_angle*1.3, axis=(0, 1, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False, proportional='DISABLED')	
	
		bpy.ops.object.mode_set(mode='EDIT')
	

		#declare the fingers pos
		pinky_top = [-10000,0.0,0.0]
		pinky_bot = [-10000,0.0,0.0]
		pinky_phal_1 = [0.0,0.0,0.0]
		pinky_phal_2 = [0.0,0.0,0.0]
		
		ring_top = [-10000,0.0,0.0]
		ring_bot = [-10000,0.0,0.0]
		ring_phal_1 = [0.0,0.0,0.0]
		ring_phal_2 = [0.0,0.0,0.0]
		
		middle_top =[-10000,0.0,0.0]
		middle_bot =[-10000,0.0,0.0]
		middle_phal_1 = [0.0,0.0,0.0]
		middle_phal_2 = [0.0,0.0,0.0] 
		
		index_top = [-10000,0.0,0.0]
		index_bot = [-10000,0.0,0.0]
		index_phal_1 = [0.0,0.0,0.0]
		index_phal_2 = [0.0,0.0,0.0] 
		
		thumb_top = [-10000,0.0,0.0]
		thumb_bot = [-10000,0.0,0.0]
		thumb_phal_1 = [-10000,0.0,0.0]
		thumb_phal_2 = [-10000,0.0,0.0]

		# list verts under y_progress
		mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
		
		if debug:
			print("    find grid distance...\n")

			#find the distance y between verts
		dist = 100
		mesh.verts.ensure_lookup_table() #debug
		mesh.verts[0].select = True	  

		bpy.ops.mesh.select_more()
		mesh.verts[0].select = False   
		
		for i in mesh.verts:
			if i.select:
				current_dist = abs(abs(mesh.verts[0].co[1]) - abs(i.co[1]))

				if current_dist < dist and current_dist > 0.00001:
					dist = current_dist

		
		print("    grid_dist = ", dist)
		
		# Find matrix-plane left bound		  
		bound_left = -100
		vertex_border = 0
		
		for v in mesh.verts:
			
			mesh.verts.ensure_lookup_table() #debug	 
			vert_y = v.co[1]
			if vert_y > bound_left+0.001:
				bound_left = vert_y
				vertex_border = v
				clear_selection()
				v.select = True
		
		if debug:
			print("    start finger detection...\n")
		
		# Start detection	
		
		if scene.fingers_to_detect == '5':		
			#pinky
			vertex_border = find_finger_top(pinky_top, vertex_border, dist, "pinky")
			copy_list(pinky_top, pinky_bot)
			vertex_border = find_finger_bot(pinky_bot, vertex_border, dist, pinky_phal_1, pinky_phal_2, "pinky", middle_bot)	
		else:
			pinky_top = None
			pinky_bot = None
			pinky_phal_1 = None
			pinky_phal_2 = None
			
		
		#ring		 
		vertex_border = find_finger_top(ring_top, vertex_border, dist, "ring")		
		
		copy_list(ring_top, ring_bot)
		vertex_border = find_finger_bot(ring_bot, vertex_border, dist, ring_phal_1, ring_phal_2, "ring", middle_bot)
		
		#middle		   
		vertex_border = find_finger_top(middle_top, vertex_border, dist, "middle")
		
		copy_list(middle_top, middle_bot)
		vertex_border = find_finger_bot(middle_bot, vertex_border, dist, middle_phal_1, middle_phal_2, "middle", middle_bot)   
	  

		#index	 
		vertex_border = find_finger_top(index_top, vertex_border, dist, "index")		
		copy_list(index_top, index_bot)		  
		vertex_border = find_finger_bot(index_bot, vertex_border, dist, index_phal_1, index_phal_2, "index", middle_bot)
	   
		#thumb		 
		vertex_border = find_finger_top(thumb_top, vertex_border, dist, "thumb")
		
		
		#thumb_bot		  
		thumb_top_vec = bpy.data.objects["plane_matrix"].matrix_world * Vector((thumb_top[0], thumb_top[1], thumb_top[2]))
		hand_pos_vec = Vector((hand_loc_x, hand_loc_y, hand_loc_z))
		  
		thumb_bot_vec = hand_pos_vec + (thumb_top_vec - hand_pos_vec)*0.1
		
		thumb_bot = bpy.data.objects["plane_matrix"].matrix_world.inverted() * thumb_bot_vec
		
		find_thumb_phalanxes(thumb_top , thumb_bot, thumb_phal_1, thumb_phal_2, body_height)   
		
		
		print("    end finger detection, analyze data...\n")
		
	   
			# create empties for each finger location
		bpy.ops.object.mode_set(mode='OBJECT')
		
		 # Fingers bot		  
		if scene.fingers_to_detect == '5':
				# pinky bot		
			pinky_bot[1] = (pinky_top[1] + pinky_bot[1])*0.5
			pinky_bot[0] -= (bound_top-bound_bot)/13	
			
			pinky_bot_vec = bpy.data.objects["plane_matrix"].matrix_world * vectorize3(pinky_bot)			
			
			pinky_bot_vec += finger_normal * (f_thickness)
		else:
			pinky_bot_vec = None

			# ring bot		
		initial_z = ring_bot[2]
		length = (vectorize3(ring_phal_2) - vectorize3(ring_bot)).magnitude
		temp_dir = (vectorize3(ring_phal_2) - vectorize3(ring_top)).normalized()		
		ring_bot = vectorize3(ring_phal_2) + temp_dir*length
		ring_bot[2] = initial_z
		ring_bot_vec = bpy.data.objects["plane_matrix"].matrix_world * vectorize3(ring_bot) 
		ring_bot_vec += finger_normal * (f_thickness*1.0)
		create_empty_loc(0.01, ring_bot_vec, "ring_bot")		
		
	   
			# middle bot
		initial_z = middle_bot[2]
		length = (vectorize3(middle_phal_2) - vectorize3(middle_bot)).magnitude
		temp_dir = (vectorize3(middle_phal_2) - vectorize3(middle_top)).normalized()		
		middle_bot = vectorize3(middle_phal_2) + temp_dir*length
		middle_bot[2] = initial_z
		middle_bot_vec = bpy.data.objects["plane_matrix"].matrix_world * vectorize3(middle_bot) 
		middle_bot_vec += finger_normal * (f_thickness*0.5)
		create_empty_loc(0.01, middle_bot_vec, "middle_bot")	
				
		
			# index bot		
		length = (vectorize3(middle_phal_2) - vectorize3(middle_bot)).magnitude
		vec = (vectorize3(index_phal_2) - vectorize3(index_top)).normalized()
		index_bot = vectorize3(index_phal_2) + vec*length		
		index_bot_vec = bpy.data.objects["plane_matrix"].matrix_world * vectorize3(index_bot)
		index_bot_vec[2] = middle_bot_vec[2]		
		create_empty_loc(0.01, index_bot_vec, "index_bot")
		
	
		
		# Fingers root
		pinky_root = []
		ring_root = []
		middle_root = []
		index_root = []
		
		fingers_root_list = [pinky_root, ring_root, middle_root, index_root]
		fingers_bot_list = [pinky_bot_vec, ring_bot_vec, middle_bot_vec, index_bot_vec]
		
		#make wrist bounds thinner		
		wrist_bound_back = wrist_bound_back + (wrist_bound_front-wrist_bound_back)*0.3
		
		for i in range(0,4):
			if fingers_bot_list[i] != None:
				fingers_root_list[i] = hand_pos_vec + (fingers_bot_list[i] - hand_pos_vec)*0.3			   
				fingers_root_list[i][1] = (fingers_root_list[i][1] + (wrist_bound_back + (wrist_bound_front-wrist_bound_back)*i/4))/2
			else:
				fingers_root_list[i] = None
			
		
		fingers_root_dict = {'pinky_root' : [fingers_root_list[0], "pinky_root"], 'ring_root':[fingers_root_list[1], "ring_root"], 'middle_root':[fingers_root_list[2], "middle_root"], 'index_root':[fingers_root_list[3],"index_root"]}
			
		for key, value in fingers_root_dict.items():
			if value[0] != None:
				create_empty_loc(0.01, value[0], value[1])	   
				
		
		thumb_bot_vec = fingers_root_list[3] + fingers_root_list[3]-fingers_root_list[2]
		create_empty_loc(0.01, thumb_bot_vec, "thumb_bot")
		
		
		# Fingers top	 
		fingers_dict = {'pinky_top' : [pinky_top, "pinky_top"], 'ring_top' : [ring_top, "ring_top"], 'middle_top' : [middle_top, "middle_top"], 'index_top' : [index_top, "index_top"], 'thumb_top' : [thumb_top, "thumb_top"]}

		for key, value in fingers_dict.items():		   
				# convert "list" coordinates to "vector" (matrix)
			if value[0] != None:
				co = Vector((value[0][0], value[0][1], value[0][2]))
			
				global_pos = bpy.data.objects["plane_matrix"].matrix_world * co			
				global_pos += finger_normal * (f_thickness)			
				create_empty_loc(0.01, global_pos, value[1])
		 
		# pinky second iteration refine	
		if pinky_bot_vec != None:
			if pinky_bot_vec[0] > ring_bot_vec[0]:
				pinky_bot_vec[0] = ring_bot_vec[0]			
		
			  
			create_empty_loc(0.01, pinky_bot_vec, "pinky_bot")
		
		
		# Phalanges
			# thumb phalanges
		thumb_top_vec = bpy.data.objects["plane_matrix"].matrix_world * vectorize3(thumb_top)	
		
		thumb_phal_1 = bpy.data.objects["plane_matrix"].matrix_world * vectorize3(thumb_phal_1)
		thumb_phal_1 += vectorize3([0,0,-1]) * (f_thickness*0.5)		
		create_empty_loc(0.01, thumb_phal_1, "thumb_phal_1")
		
		thumb_phal_2 = bpy.data.objects["plane_matrix"].matrix_world * vectorize3(thumb_phal_2)
		thumb_phal_2 += vectorize3([0,0,-1]) * (f_thickness)
		thumb_phal_2_median = (thumb_phal_1 + thumb_bot_vec)*0.5
		thumb_phal_2 = Vector((thumb_phal_2_median[0], thumb_phal_2[1], thumb_phal_2_median[2]))
		create_empty_loc(0.01, thumb_phal_2, "thumb_phal_2")
		
	
		
		phalanxes_dict = {'pinky_phal_1':[pinky_phal_1, "pinky_phal_1"], 'pinky_phal_2':[pinky_phal_2,"pinky_phal_2"], 'ring_phal_1':[ring_phal_1,"ring_phal_1"], 'ring_phal_2':[ring_phal_2,"ring_phal_2"],'middle_phal_1':[middle_phal_1,"middle_phal_1"],'middle_phal_2':[middle_phal_2,"middle_phal_2"],'index_phal_1':[index_phal_1,"index_phal_1"],'index_phal_2':[index_phal_2,"index_phal_2"]}
		
		for key, value in phalanxes_dict.items():	
			if value[0] != None:
				# convert "list" coordinates to "vector" (matrix)
				co1 = Vector((value[0][0], value[0][1], value[0][2]))		   
				global_pos1 = bpy.data.objects["plane_matrix"].matrix_world * co1			
				global_pos1 += finger_normal * (f_thickness)		
			
					# pinky refine
				if pinky_bot_vec != None:
					if value[1] == "pinky_phal_1":
						global_pos1 = pinky_bot_vec + (get_object("pinky_top_auto").location - pinky_bot_vec)*0.70
					if value[1] == "pinky_phal_2":
						global_pos1 = pinky_bot_vec + (get_object("pinky_top_auto").location - pinky_bot_vec)*0.3
				
			
				create_empty_loc(0.01, global_pos1, value[1])
			
			
		#Second pass refine		
		refine_phalange_list = ['index', 'middle', 'ring']
		for phal in refine_phalange_list:
			get_object(phal+'_phal_1_auto').location[2] = (get_object(phal+'_phal_2_auto').location[2] + get_object(phal+'_top_auto').location[2])*0.5
		
		refine_bot_list = ['middle', 'ring']
		"""
		for finger in refine_bot_list:
			get_object(finger+'_bot_auto').location[1] = (get_object(finger+'_phal_2_auto').location[1] + get_object(finger+'_root_auto').location[1])*0.5
		"""

		# hand empty		 
		create_empty_loc(0.04, hand_empty_loc, "hand_loc")	
		
		#remove the matrix plane
		clear_object_selection()
		bpy.data.objects["plane_matrix"].select = True
		bpy.ops.object.delete()
		
	else:#no finger detection
		# hand empty  
		bpy.ops.object.mode_set(mode='OBJECT')
		create_empty_loc(0.04, hand_empty_loc, "hand_loc")	
		
	#delete hand_aligned object
	bpy.data.objects.remove(bpy.data.objects["hand_aligned"], True)
		
	
	print("find foot...\n")
	
	# FOOT POSITION -------------------------------------------------------------------------
	body.select = True
	set_active_object(body.name)
	
	bpy.ops.object.mode_set(mode='EDIT')
	foot_loc_z_loc = foot_loc.location[2]
	foot_loc_x_loc = foot_loc.location[0]

	#select vertices around the foot_loc 
	selected_index = []
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	
	for v in mesh.verts:	
		#if tolerance_check(v.co, foot_loc_z_loc, 2, body_height / 8.825, True):
		if v.co[2] <= foot_loc_z_loc and v.co[0] > 0:
				v.select = True
				selected_index.append(v.index)	

	
	bound_back = -10000.0
	bound_front = 10000.0
	bound_left = 10000.0
	bound_right = 0.0	
	
	#find the boundaries	
	if debug:
		print("    find foot boundaries...\n")
		
	clear_selection()
	bound_left_vpos = None
	bound_right_vpos = None
	
	for vi in selected_index:
		mesh.verts.ensure_lookup_table() #debug
		vert_y = mesh.verts[vi].co[1]
		vert_x = mesh.verts[vi].co[0]
		#back	 
		if vert_y > bound_back:
			bound_back = vert_y
		#front
		if vert_y < bound_front:
			bound_front = vert_y		
		#left
		if vert_x < bound_left:
			bound_left = vert_x
			bound_left_vpos = mesh.verts[vi].co
		#right
		if vert_x > bound_right:
			bound_right = vert_x
			bound_right_vpos = mesh.verts[vi].co
   
	if debug:
		print("    find toes...\n")
				 
	# Toes top
	bound_toes_top = 0.0

	#find the toes height
	
	for vi in selected_index:
		mesh.verts.ensure_lookup_table() #debug		   
		#find the toes end vertices
		vert_co = mesh.verts[vi].co
		vert_y = mesh.verts[vi].co[1]
		vert_z = mesh.verts[vi].co[2]
		
		if tolerance_check(vert_co, bound_front, 1, body_depth / 7, True):			
			if vert_z > bound_toes_top:
				bound_toes_top = vert_z
				mesh.verts[vi].select = True
	
	#raycast for foot direction
	my_tree = BVHTree.FromBMesh(mesh)
	ray_origin = vectorize3([0, bound_back + (bound_front-bound_back)*0.8, bound_toes_top*0.5]) + vectorize3([body_width*2,0.0,0.0])
	ray_dir = vectorize3([-body_width*4,0,0])
	
	have_hit = False
	
	while have_hit == False:	
		hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude)	   
		if hit == None or hit[0] < 0:
			ray_origin = vectorize3([ray_origin[0], ray_origin[1], ray_origin[2]*0.5])
	
		else:
			have_hit = True
			hit_front = hit
			last_hit = hit	
			
	if debug:
		print('    ray foot origin', ray_origin)
		print('    ray hit front', hit_front)
		
	while have_hit:#iterate if multiple polygons layers
		have_hit = False
		hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([-0.001,0,0]), ray_dir, ray_dir.magnitude)
		if hit != None:
			if hit[0] > 0:#right side only
				last_hit = hit
				have_hit = True
			
	hit_back = last_hit	
	
	if debug:
		print('    ray hit back', hit_back)
		
	hit_center = (hit_back+hit_front)/2	
	
	if debug:
		print("    find ankle...\n")
					
	# Ankle	   
	clear_selection()
	ankle_selection = [] 
	for v in mesh.verts:	
		if tolerance_check(v.co, foot_loc.location[2], 2, body_height / 80, True):
			v.select = True	   
			ankle_selection.append(v.index)			   
	

	ankle_back = -10000
	ankle_front = 10000
	
	for va in ankle_selection:		  
		mesh.verts.ensure_lookup_table() #debug		   
		vert_y = mesh.verts[va].co[1]		 
		#front	  
		if vert_y < ankle_front:
			ankle_front = vert_y
		# back
		if vert_y > ankle_back:
			ankle_back = vert_y		  
	
  
	ankle_empty_loc = [foot_loc.location[0], 0, foot_loc.location[2]] 
	ankle_empty_loc[1] = ankle_back + (ankle_front - ankle_back)*0.25 
	
	ankle_endfoot_dist = (vectorize3([ankle_empty_loc[0], bound_front, ankle_empty_loc[2]]) - vectorize3(ankle_empty_loc)).magnitude
	
	
	if debug:
		print("    find bank bones...\n")
	# Bank bones
	clear_selection()
	foot_bot_selection = [] 
	for v in mesh.verts:	
		if tolerance_check(v.co, 0.0, 2, body_height / 60, True):
			v.select = True	   
			foot_bot_selection.append(v.index)			  
	

	bpy.ops.object.mode_set(mode='OBJECT')	
	
	foot_dir = vectorize3([hit_center[0] - ankle_empty_loc[0], hit_center[1] - ankle_empty_loc[1], 0])
	scene.foot_dir = foot_dir
	
	#find the bank bones in foot direction space
		#create temp empty object for the coord space calculation
	angle = vectorize3([0,-1,0]).angle(foot_dir)
	bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 1, view_align=True, location=(0,0,0), rotation=(0, 0, angle))	
	# rename it		
	bpy.context.object.name = "foot_dir_space"
	foot_dir_matrix = bpy.data.objects['foot_dir_space'].matrix_world
	
	set_active_object(body.name)
	bpy.ops.object.mode_set(mode='EDIT')	
	
	
		#select vertices around the foot_loc	
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)	
	foot_back = [0,-10000.0,0]
	foot_front = [0,10000,0]
	foot_left = [10000.0,0,0]
	foot_right = [0,0,0]
	
		#find the boundaries in foot dir space			
	clear_selection()
	
	for vi in foot_bot_selection:
		mesh.verts.ensure_lookup_table()
		vert_co = mesh.verts[vi].co * foot_dir_matrix		
		
		#back	 
		if vert_co[1] > foot_back[1]:
			foot_back = vert_co			
		#front
		if vert_co[1] < foot_front[1]:
			foot_front = vert_co			
		#left
		if vert_co[0] < foot_left[0]:
			foot_left = vert_co			
		#right
		if vert_co[0] > foot_right[0]:
			foot_right = vert_co				
			
	bank_right_loc = [foot_left[0], foot_back[1], 0]
	bank_left_loc = [foot_right[0], foot_back[1], 0]
	bank_mid_loc = [(foot_left[0] + foot_right[0])/2, foot_back[1], 0]		
			
	bank_right_loc = vectorize3(bank_right_loc) * foot_dir_matrix.inverted()
	bank_left_loc = vectorize3(bank_left_loc) * foot_dir_matrix.inverted()
	bank_mid_loc = vectorize3(bank_mid_loc) * foot_dir_matrix.inverted()
		
	
	bpy.ops.object.mode_set(mode='OBJECT')	
	
	toes_end_loc = vectorize3(ankle_empty_loc) + (foot_dir.normalized() * ankle_endfoot_dist)
	toes_end_loc[2] = 0
	toes_start_loc = vectorize3(ankle_empty_loc) + (toes_end_loc-vectorize3(ankle_empty_loc))*0.7
	toes_start_loc[2] = bound_toes_top*0.5
	
	# create empty location	  
	foot_dict = {'ankle_loc':[ankle_empty_loc, "ankle_loc"], 'bank_left_loc':[bank_left_loc,"bank_left_loc"],'bank_right_loc':[bank_right_loc, "bank_right_loc"],'bank_mid_loc':[bank_mid_loc,"bank_mid_loc"],'toes_end':[toes_end_loc,"toes_end"],'toes_start':[toes_start_loc,"toes_start"]}

	for key, value in foot_dict.items():
		create_empty_loc(0.04, value[0], value[1])
	
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object('foot_dir_space')
	bpy.ops.object.delete(use_global=False)

	
	# ROOT POSITION --------------------------------------------------------------------------------------------
	
	print("find root position...\n")
	
		# get the loc guides
	root_loc = bpy.data.objects["root_loc"]
	set_active_object(body.name)
	bpy.ops.object.mode_set(mode='EDIT')
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	
	#select vertices in the overlapping sphere
	root_selection = []
	
	clear_selection()	
	
	base_dist = body_width / 15
	r_dist = base_dist
	has_selected = False
	vert_sel = []
	hips_back = None
	hips_front = None	
	hips_right = None
	
	while not has_selected:
		for v in mesh.verts:	
			if tolerance_check_2(v.co, root_loc.location, 0, 2, r_dist):
				#v.select = True	
				vert_sel.append(v)
				has_selected = True
				if hips_right == None:
					hips_right = v.co[0]
				if v.co[0] > hips_right:
					hips_right = v.co[0]
				if hips_back == None:
					hips_back = v.co[0]
				if v.co[1] > hips_back or hips_back == None:
					hips_back = v.co[1]
				if hips_front == None:
					hips_front = v.co[0]
				if v.co[1] < hips_front or hips_front == None:
					hips_front = v.co[1]
					
		r_dist += base_dist
		
	
	"""
	for i in range(0,3):
		bpy.ops.mesh.select_more()
		
	#exclude verts too high or too low	
	for v in mesh.verts:	
		if not tolerance_check(v.co, root_loc.location[2], 2, body_width / 15, True):
			v.select = False
			
		if v.select == True:
			root_selection.append(v.index)	 
	"""
	
	#find the hips boundaries
	if debug:
		print("    find hips boundaries...\n")	
	
	found_boundary = False#righ boundary
	while not found_boundary:
		print('loooping...')
		found_boundary = True
		for vert in vert_sel:
			for edge in vert.link_edges:
				for v in edge.verts:
					if not v in vert_sel and v.co[0] > vert.co[0]:
						if tolerance_check(v.co, root_loc.location[2], 2, body_width / 15, True):
							vert_sel.append(v)
							#v.select = True
							found_boundary = False
							if v.co[0] > hips_right:
								hips_right = v.co[0]
							if v.co[1] > hips_back:
								hips_back = v.co[1]
							if v.co[1] < hips_front:
								hips_front = v.co[1]		
	 
	"""
	#find the boundaries
	clear_selection()
	for vr in root_selection:		 
		mesh.verts.ensure_lookup_table() #debug
		mesh.verts[vr].select = True
		vert_y = mesh.verts[vr].co[1]
		vert_x = mesh.verts[vr].co[0]
		#back	 
		if vert_y < hips_back:
			hips_back = vert_y
		#front
		if vert_y > hips_front:
			hips_front = vert_y		   
		#left
		if vert_x < hips_left:
			hips_left = vert_x
		#right
		if vert_x > hips_right:
			hips_right = vert_x	   
    """
	
	
	
	# create root, legs and knee empty			
	root_empty_loc = [0, (hips_back+hips_front)/2, root_loc.location[2]]
	
	
	 # LEGS POSITION --------------------------------------------------------------------------------------------
		
	print("find legs...\n")
	 
	leg_empty_loc = [(hips_right)/2, root_empty_loc[1], root_empty_loc[2]]
	knee_empty_loc = [(leg_empty_loc[0] + ankle_empty_loc[0])/2, 0, (leg_empty_loc[2] + ankle_empty_loc[2])/2]
	bot_empty_loc = [leg_empty_loc[0], hips_front, leg_empty_loc[2]]
	 
	# find the knee boundaries
	
	if debug:
		print("    find knee boundaries...\n")
		
	clear_selection()
	knee_selection = []		
	has_selected_knee = False
	sel_dist = body_height / 25
		
	while has_selected_knee == False:
		for vb in mesh.verts:	 
			if tolerance_check(vb.co, knee_empty_loc[2], 2, sel_dist, True):
				vb.select = True	
				knee_selection.append(vb.index)
				has_selected_knee = True
				
		sel_dist *= 2		 
	"""
	for v in mesh.verts:	
		if tolerance_check(v.co, knee_empty_loc[2], 2, body_height / 25, True):
			v.select = True
			knee_selection.append(v.index)
	"""
	knee_back = -1000
	knee_front = 1000
	
	for vk in knee_selection:		 
		mesh.verts.ensure_lookup_table() #debug		   
		vert_y = mesh.verts[vk].co[1]		 
		#front	  
		if vert_y < knee_front:
			knee_front = vert_y
		# back
		if vert_y > knee_back:
			knee_back = vert_y		  
	 
	knee_empty_loc[1] = knee_back + (knee_front - knee_back)*0.7			

	bpy.ops.object.mode_set(mode='OBJECT')
		
	create_empty_loc(0.04, root_empty_loc, "root_loc")
	create_empty_loc(0.04, leg_empty_loc, "leg_loc")
	create_empty_loc(0.04, knee_empty_loc, "knee_loc")
	create_empty_loc(0.04, bot_empty_loc, "bot_empty_loc")
	
	# SPINE POSITION ---------------------------------------------------------
		
	print("find neck...\n")
	
		# Neck
	neck_loc = bpy.data.objects["neck_loc"]
	set_active_object(body.name)
	bpy.ops.object.mode_set(mode='EDIT')
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	
	#select vertices in the overlapping neck sphere	   
	neck_selection = []	   
	clear_selection() 
	
	has_selected_neck = False
	sel_dist = body_height / 25
		
	while has_selected_neck == False:
		for vb in mesh.verts:	 
			if tolerance_check_2(vb.co, neck_loc.location, 0, 2, sel_dist):
				vb.select = True	
				neck_selection.append(vb.index)
				has_selected_neck = True
				
		sel_dist *= 2		 

	
	# find the neck bounds	  
	if debug:
		print("    find neck boundaries...\n")	

	ray_origin = Vector((0,-body_depth*2, neck_loc.location[2]))
	ray_dir = vectorize3([0,body_depth*4,0])	
	
	hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude) 
	
	if distance == None or distance < 0.001:
		print('    Could not find neck pos, marker out of mesh?')		
	else:
		neck_front = hit
		have_hit = True
		last_hit = hit
		#iterate if multiples faces layers
		while have_hit:
			have_hit = False
			hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
			if hit != None:						
				have_hit = True
				last_hit = hit
				
		neck_back = last_hit
	
			
	neck_empty_loc = [0, neck_back[1] + (neck_front[1]-neck_back[1])*0.45, neck_loc.location[2]]	
	 
		# Head		  
	#select the top head vertices
	top_head_sel = []	 
	clear_selection() 
		
	for v in mesh.verts:	
		if tolerance_check(v.co, body_height, 2, body_height / 20, True):
			v.select = True	   
			top_head_sel.append(v.index)
	
	# find the head bounds
		
	print("    find head boundaries...\n")
	

	# Spine 01	
	my_tree = BVHTree.FromBMesh(mesh)
	vec =  (neck_loc.location - root_loc.location)*1/3
	ray_origin = root_loc.location + vec + vectorize3([0,-body_depth*2,0])
	ray_dir = vectorize3([0,body_depth*4,0])
	
	hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude) 
	if distance == None or distance < 0.001:
		print('    Could not find spine 01 front, marker out of mesh?')
	
	else:
		spine_01_front = hit
		have_hit = True
		last_hit = hit
		#iterate if multiples faces layers
		while have_hit:
			have_hit = False
			hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
			if hit != None:						
				have_hit = True
				last_hit = hit
				
		spine_01_back = last_hit
		
	spine_01_empty_loc = spine_01_front + (spine_01_back-spine_01_front)*0.65
	
	
	# Spine 02
	vec =  (neck_loc.location - root_loc.location)*2/3
	ray_origin = root_loc.location + vec + vectorize3([0,-body_depth*2,0])
	ray_dir = vectorize3([0,body_depth*4,0])
	
	hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude) 
	if distance == None or distance < 0.001:
		print('    Could not find spine 02 front, marker out of mesh')		
	else:
		spine_02_front = hit
		have_hit = True
		last_hit = hit
		#iterate if multiples faces layers
		while have_hit:
			have_hit = False
			hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
			if hit != None:						
				have_hit = True
				last_hit = hit
				
		spine_02_back = last_hit
			
	spine_02_empty_loc = spine_02_front + (spine_02_back-spine_02_front)*0.65
	
	# Breast	
	print("find breast...\n")
	
	#select vertices near spine02
	spine_02_selection = []	   
	clear_selection() 
	has_selected_spine_02 = False
	sel_dist = body_height / 17
	
	while has_selected_spine_02 == False:
		for vb in mesh.verts:	 
			if tolerance_check_2(vb.co, spine_02_empty_loc, 0, 2, sel_dist):
				vb.select = True	
				spine_02_selection.append(vb.index)
				has_selected_spine_02 = True
				
		sel_dist *= 2


	# find the spine 02 front bound
	spine_02_back = -1000
	spine_02_front = 1000
	
	if debug:
		print("    find breast boundaries...\n")
	
	for vs in spine_02_selection:		 
		mesh.verts.ensure_lookup_table() #debug		   
		vert_y = mesh.verts[vs].co[1]		 
		#front	  
		if vert_y < spine_02_front:
			spine_02_front = vert_y
		 #back	  
		if vert_y > spine_02_back:
			spine_02_back = vert_y	
	
	
	breast_01_loc = [shoulder_pos[0]/2, spine_02_front, spine_02_empty_loc[2]] 
	breast_02_loc = [shoulder_pos[0]/2, breast_01_loc[1] + (shoulder_pos[1]-breast_01_loc[1])*0.4, spine_02_empty_loc[2]+ (shoulder_pos[2]-spine_02_empty_loc[2])*0.5] 	   
	
	print("find spine 01...\n")
	
	#head	
	chin_loc = None
		#retro compatibility, chin was not defined in earlier versions
	if bpy.data.objects.get("chin_loc") != None:
		chin_loc = bpy.data.objects["chin_loc"]
		
	if chin_loc == None:
		head_height = neck_empty_loc[2] + (body_height - neck_empty_loc[2])*0.25
	else:
		head_height = chin_loc.location[2] + (body_height - chin_loc.location[2])*0.1
		
	ray_origin = Vector((0,-body_depth*2, head_height))
	ray_dir = vectorize3([0,body_depth*4,0])	
	
	hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude) 
	
	if distance == None or distance < 0.001:
		print('    Could not find head pos, marker out of mesh?')		
	else:
		head_front = hit
		have_hit = True
		last_hit = hit
		#iterate if multiples faces layers
		while have_hit:
			have_hit = False
			hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
			if hit != None:						
				have_hit = True
				last_hit = hit
				
		head_back = last_hit
	
	
	head_empty_loc = [0, head_back[1] + (head_front[1] - head_back[1]	)*0.3, head_height]
	head_end_empty_loc = [0, head_empty_loc[1], body_height]
	
	
	# create the empties	   
	bpy.ops.object.mode_set(mode='OBJECT')
	create_empty_loc(0.04, neck_empty_loc, "neck_loc")
	create_empty_loc(0.04, spine_01_empty_loc, "spine_01_loc")
	create_empty_loc(0.04, spine_02_empty_loc, "spine_02_loc")
	create_empty_loc(0.04, head_end_empty_loc, "head_end_loc")
	create_empty_loc(0.04, head_empty_loc, "head_loc")
	create_empty_loc(0.04, breast_01_loc, "breast_01_loc")
	create_empty_loc(0.04, breast_02_loc, "breast_02_loc")

   # ARMS ---------------------------------------------------------------------
   	
	print("find arms...\n")

	shoulder_loc = bpy.data.objects["shoulder_loc"]
	set_active_object(body.name)
	bpy.ops.object.mode_set(mode='EDIT')
	mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
	
	#select vertices in the overlapping shoulder sphere
	shoulder_selection = []	   
	clear_selection() 
	
	if debug:
		print("    find shoulders vertices...\n")
		
	for v in mesh.verts:	
		if tolerance_check_2(v.co, shoulder_loc.location, 0, 2, body_height / 25):
			v.select = True	   
			shoulder_selection.append(v.index)
	
	# find the shoulder bounds
	shoulder_back = -1000
	shoulder_front = 1000
	
	if debug:
		print("    find shoulders boundaries...\n")
	
	for vs in shoulder_selection:		 
		mesh.verts.ensure_lookup_table() #debug		   
		vert_y = mesh.verts[vs].co[1]		 
		#front	  
		if vert_y < shoulder_front:
			shoulder_front = vert_y
		# back
		if vert_y > shoulder_back:
			shoulder_back = vert_y	

	shoulder_empty_loc = [shoulder_loc.location[0], shoulder_back + (shoulder_front-shoulder_back)*0.4, shoulder_loc.location[2]]
	
	# shoulder_base
	shoulder_base_loc = [shoulder_empty_loc[0]/4, shoulder_empty_loc[1], shoulder_empty_loc[2]]
   
	
	# Elbow
	elbow_empty_loc = [(shoulder_empty_loc[0] + hand_empty_loc[0])/2, 0, (shoulder_empty_loc[2] + hand_empty_loc[2])/2]
	 
		# find the elbow boundaries
		
	if debug:
		print("    find elbow boundaries...\n")
		
	clear_selection()
	elbow_selection = []
	has_selected_v = False
	sel_rad = body_width / 20
	
	while has_selected_v == False:
		for v in mesh.verts:	
			if tolerance_check_2(v.co, elbow_empty_loc, 0, 2, sel_rad):
				v.select = True	 
				has_selected_v = True  
				elbow_selection.append(v.index)
				
		if has_selected_v == False:
			sel_rad *= 2	   
			
		   
	
	elbow_back = -1000
	elbow_front = 1000
	
	for ve in elbow_selection:		  
		mesh.verts.ensure_lookup_table() #debug		   
		vert_y = mesh.verts[ve].co[1]		 
		#front	  
		if vert_y < elbow_front:
			elbow_front = vert_y
		# back
		if vert_y > elbow_back:
			elbow_back = vert_y		   
	 
	elbow_empty_loc[1] = elbow_back + (elbow_front - elbow_back)*0.3   
	
	# create the empties	   
	bpy.ops.object.mode_set(mode='OBJECT')
	create_empty_loc(0.04, shoulder_empty_loc, "shoulder_loc")
	create_empty_loc(0.04, shoulder_base_loc, "shoulder_base_loc")
	create_empty_loc(0.04, elbow_empty_loc, "elbow_loc") 
	
	#restore the pivot mode
	bpy.context.space_data.pivot_point = pivot_mod


	# END - UPDATE VIEW --------------------------------------------------
	bpy.ops.transform.translate(value=(0, 0, 0))
	
	if debug:
		print("End Auto-Detection.\n")
	
	
	
#-- end _auto_detect()	   
	
def _delete_detected():
	clear_object_selection()
	if bpy.data.objects.get('auto_detect_loc') != None:
		bpy.data.objects["auto_detect_loc"].select = True
		bpy.context.scene.objects.active = bpy.data.objects["auto_detect_loc"]
		
		bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
		bpy.ops.object.delete()
		bpy.data.objects["auto_detect_loc"].select = True
		
		bpy.ops.object.delete()
	
def _delete_big_markers():
	scene = bpy.context.scene
	
	#save all markers position for later restore
		#clear it first
	#clear the bone collection
	if len(scene.markers_save) > 0:
		i = len(scene.markers_save)
		while i >= 0:		   
			scene.markers_save.remove(i)
			i -= 1
			
	for obj in bpy.data.objects['markers'].children:
		item = scene.markers_save.add()		
		item.name = obj.name 
		item.location = obj.location
	
	
	clear_object_selection()
	bpy.data.objects["markers"].select = True
	bpy.context.scene.objects.active = bpy.data.objects["markers"]	
	bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
	bpy.ops.object.delete()
	bpy.data.objects["markers"].select = True
	
	if bpy.data.objects.get('body_temp') != None:
		bpy.data.objects["body_temp"].select = True
	bpy.ops.object.delete()
	

	

def _set_front_view():
	bpy.context.scene.body_name = bpy.context.scene.objects.active.name
	try:
		bpy.context.space_data.show_relationship_lines = False
	except:
		pass
	
	bpy.ops.object.mode_set(mode='OBJECT')
	
	#get character mesh name
	body = bpy.data.objects[bpy.context.scene.body_name]	
	
	bpy.ops.object.select_all(action='DESELECT')
	body.select = True
	bpy.context.scene.objects.active = body
	#remove parent if any
	#body.parent = None
	bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

	#apply transforms
	bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	# set to vertex selection mode
	bpy.ops.mesh.select_mode(type="VERT")
	
	# remove double
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.remove_doubles()
	bpy.ops.mesh.remove_doubles(threshold=1e-006)
	bpy.ops.object.mode_set(mode='OBJECT')
	
	# remove any armature modifier
	if len(body.modifiers) > 0:
		for modifier in bpy.context.object.modifiers:
			if modifier.type == 'ARMATURE':					
				bpy.ops.object.modifier_remove(modifier=modifier.name)
				
		
	
	#center front view
	bpy.ops.view3d.viewnumpad(type='FRONT')
	bpy.ops.view3d.view_selected(use_all_regions=False)
	bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, view_align=False, location=(0,0,0), rotation=(0, 0, 0))	 
	bpy.context.object.name = "markers"
	bpy.ops.object.select_all(action='DESELECT')
	
	#set ortho
	bpy.context.space_data.region_3d.view_perspective = 'ORTHO'
	
	#freeze character selection
	bpy.data.objects[bpy.context.scene.body_name].hide_select = True
	if bpy.data.objects.get('rig') != None:
		bpy.data.objects['rig'].hide_select = True
		bpy.data.objects['rig'].hide = True


# COLLECTION PROPERTIES DEFINITION
class bone_transform(bpy.types.PropertyGroup):	  
	head = bpy.props.FloatVectorProperty(name="Head Position", default=(0.0, 0.0, 0.0), subtype='TRANSLATION', size=3)
	tail = bpy.props.FloatVectorProperty(name="Tail Position", default=(0.0, 0.0, 0.0), subtype='TRANSLATION', size=3)
	roll = bpy.props.FloatProperty(name="Head Position", default=0.0)
	
class markers_transform(bpy.types.PropertyGroup):
	location = bpy.props.FloatVectorProperty(name="Position", default=(0.0,0.0,0.0), subtype='TRANSLATION', size=3)

# END FUNCTIONS

###########	 UI PANEL  ###################

class proxy_utils_ui(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = "Auto-Rig Pro : Smart"
	bl_idname = "id_auto_rig_detect"
	
	@classmethod
	# buttons visibility conditions
	
	def poll(cls, context):
		if context.mode == 'POSE' or context.mode == 'OBJECT' or context.mode == 'EDIT_ARMATURE':
			return True
		else:
			return False
		
	def draw(self, context):
		global custom_icons
		layout = self.layout
		object = context.object
		scene = context.scene
		col = layout.column(align=False)
		
		button_state = 0
		
		#BUTTONS	  

		try:
			bpy.data.objects["markers"]
			button_state = 1
			
			try:
				bpy.data.objects["neck_loc"]
				button_state = 2
			except:
				pass
			try:
				bpy.data.objects["chin_loc"]
				button_state = 3
			except:
				pass
				
			try:
				bpy.data.objects["shoulder_loc"]
				button_state = 4
			except:
				pass
			try:
				bpy.data.objects["hand_loc"]
				button_state = 5
			except:
				pass
			try:
				bpy.data.objects["root_loc"]
				button_state = 6
			except:
				pass
			try:
				bpy.data.objects["foot_loc"]
				button_state = 7
			except:
				pass
		
		except:
			pass
		
			
		if button_state == 0:
			layout.operator("id.set_front_view", text="Get Selected Objects")
		
							
		if button_state == 1:	 
			col = layout.column(align=True)
			split=col.split(align=True)
			#row.alignment = 'LEFT'
			split.label("Turn")
			btn = split.operator("id.turn", "", icon_value=custom_icons["rotate"].icon_id)
			btn.action = "negative"
			btn = split.operator("id.turn", "", icon_value=custom_icons["rotate_inv"].icon_id)
			btn.action = "positive"
			props = layout.operator("id.add_marker", text="Add Neck", icon = 'PLUS') 
			props.body_part = "neck"
			
		if button_state == 2:	 
			props = layout.operator("id.add_marker", text="Add Chin", icon = 'PLUS') 
			props.body_part = "chin"	
			
		if button_state == 3:	 
			props = layout.operator("id.add_marker", text="Add Shoulders", icon = 'PLUS') 
			props.body_part = "shoulder"	
		if button_state == 4:	 
			props = layout.operator("id.add_marker", text="Add Wrists", icon = 'PLUS') 
			props.body_part = "hand"   
		if button_state == 5:	 
			props = layout.operator("id.add_marker", text="Add Spine Root", icon = 'PLUS') 
			props.body_part = "root" 
		if button_state == 6:	 
			props = layout.operator("id.add_marker", text="Add Ankles", icon = 'PLUS') 
			props.body_part = "foot"		 

		if button_state == 7:			
			layout.label("Auto-Detection:")			
			layout.prop(scene, "fingers_to_detect", text="")
			layout.operator("id.match_ref", text="Go!", icon='MOD_PARTICLES') 
			layout.separator() 
		
		
		if button_state > 0:
			col = layout.column(align=True)
			col.operator("id.restore_markers", text="Restore Last Session", icon='RECOVER_LAST')
			col.operator("id.delete_big_markers", text="Delete Markers", icon='PANEL_CLOSE')
		
		layout.separator() 
		
	  

@persistent
def cleanup(dummy):
	try:
		bpy.types.SpaceView3D.draw_handler_remove(handles[0], 'WINDOW') 
		print('Removed handler')
	except:
		print('No handler to remove')
	
#enable markers fx if any markers already in the scene when loading the file
@persistent
def enable_markers_fx(dummy):
	if bpy.data.objects.get('markers') is not None: 
		if len(bpy.data.objects['markers'].children) > 0:
			print('Markers already in scene, enable Markers FX')			
			bpy.ops.id.markers_fx(active=True)
			
			
	
bpy.app.handlers.load_pre.append(cleanup)
bpy.app.handlers.load_post.append(enable_markers_fx)

###########	 REGISTER  ##################
custom_icons = None

def register():	  
	global custom_icons
	custom_icons = bpy.utils.previews.new()	   
	icons_dir = os.path.join(os.path.dirname(__file__), "icons")
	custom_icons.load("rotate", os.path.join(icons_dir, "rotate.png"), 'IMAGE')
	custom_icons.load("rotate_inv", os.path.join(icons_dir, "rotate_inv.png"), 'IMAGE')
	bpy.types.Scene.body_name  = bpy.props.StringProperty(name="Body name", description = "Get the body object name")

	bpy.types.Scene.shape_keys_type = bpy.props.EnumProperty(items=(('SIMPLE', 'Simple', 'Simple'),
																	('MULTIPLE', 'Multiple', 'Multiple')												
																), name = 'Shape Key Type'																
															)	
	
	
	bpy.types.Scene.fingers_to_detect = bpy.props.EnumProperty(items=(('5', 'Find 5 Fingers', '5 fingers detection, from the thumb to the pinky'), ('4', 'Find 4 Fingers', '4 fingers detection, from the thumb to the ring'), ('NONE', 'Skip Fingers', 'No fingers detection, manual placement')), description = "How many fingers should be found on this model", name = "Fingers detection")
	bpy.types.Scene.fingers_init_transform = bpy.props.CollectionProperty(type=bone_transform)
	bpy.types.Scene.quit = bpy.props.BoolProperty(name="Quit", default=False)
	bpy.types.Scene.markers_save = bpy.props.CollectionProperty(type=markers_transform)
	bpy.types.Scene.foot_dir = bpy.props.FloatVectorProperty(name="Foot Direction", subtype='DIRECTION', default=(0,0,0))
	
	
def unregister():	
	global custom_icons
	bpy.utils.previews.remove(custom_icons)

	del bpy.types.Scene.body_name
	del bpy.types.Scene.fingers_to_detect
	del bpy.types.Scene.fingers_init_transform
	del bpy.types.Scene.quit
	del bpy.types.Scene.markers_save
	del bpy.types.Scene.foot_dir

	
	


	