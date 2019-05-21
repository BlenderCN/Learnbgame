from .Tila_KeymapManager import KeymapManager
import bpy
import os

bl_info = {
	"name": "Tilapiatsu Hotkeys",
	"description": "Hotkeys",
	"author": "Tilapiatsu",
	"version": (0, 1, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"wiki_url": "",
	"category": "Learnbgame",
	}


# TODO 
# - Create a rename /batch rename feature
# 	-- Update the view3d.viewport_rename operator to add batch rename functions
# - Modify the camera behaviour to slow the dolly speed based on the distance from the object
#   --Modify the camera bihaviour to be able to rotate around the last point under the mouse
# - Vertex Normal Pie Menu : Mark Hard, Mark Soft, update normal, Thief
# - UV Pie Menu : Split, sew, mak seam etc
# - Need to fix the rotate/scaling pivot point in UV context
# - Create a simple Bevel like Modo Does : Bevel + Inset + Segment count
# - Script to visualize Texture checker in all objects in the viewport
# - Fix the uv transform too which is always scaling uniformally
# - Fix the smart edit mode in UV context
# - Create an action center pie menu


# Addon to Enable

# -   Modifier tool
# -   Mesure It
# -   Extra Object Mesh and Curve
# -   Import Image as Plane
# -   fSpy
# -   3d print
# -   F2
# -   LoopTool
# -   MachineTool
# -   Mesh Align Plus
# -   Snaap_utility Line
# -   Node Wrangle
# -   Principled Bake
# -   BoolTool
# -   D-Noise
# -   Render Burst
# -   Magic UV
# -	  Photographer


class TilaKeymaps(KeymapManager.KeymapManager):

	def __init__(self):

		super(TilaKeymaps, self).__init__()

		self.k_viewfit = 'MIDDLEMOUSE'
		self.k_manip = 'LEFTMOUSE'
		self.k_cursor = 'MIDDLEMOUSE'
		self.k_nav = 'MIDDLEMOUSE'
		self.k_menu = 'SPACE'
		self.k_select = 'LEFTMOUSE'
		self.k_lasso = 'EVT_TWEAK_R'
		self.k_lasso_through = 'EVT_TWEAK_M'
		self.k_box = 'EVT_TWEAK_L'
		self.k_box_through = 'EVT_TWEAK_M'
		self.k_select_attatched = 'EVT_TWEAK_M'
		self.k_context = 'RIGHTMOUSE'
		self.k_more = 'UP_ARROW'
		self.k_less = 'DOWN_ARROW'
		self.k_linked = 'W'
		self.k_vert_mode = 'ONE'
		self.k_edge_mode = 'TWO'
		self.k_face_mode = 'THREE'

		self.k_move = 'G'
		self.k_rotate = 'R'
		self.k_scale = 'S'

	# Global Keymap Functions

	def global_keys(self):
		self.kmi_set_replace("screen.userpref_show", "TAB", "PRESS", ctrl=True)
		self.kmi_set_replace("wm.window_fullscreen_toggle", "F11", "PRESS")
		self.kmi_set_replace('screen.animation_play', self.k_menu, 'PRESS', shift=True)
		
		if self.km.name in ['3D View']:
			self.kmi_set_replace("popup.hp_properties", 'V', "PRESS")
			self.kmi_set_replace('popup.hp_materials', 'M', 'PRESS')
			self.kmi_set_replace('popup.hp_render', 'EQUAL', 'PRESS')
   
		self.kmi_set_replace('wm.call_menu_pie', 'A', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('name', 'HP_MT_pie_add')])
		self.kmi_set_replace('wm.call_menu_pie', 'TAB', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('name', 'HP_MT_pie_areas')])
		self.kmi_set_replace('wm.call_menu_pie', 'X', 'PRESS', alt=True, shift=True, properties=[('name', 'HP_MT_pie_symmetry')])

		self.kmi_set_replace('view3d.viewport_rename', 'F2', 'PRESS')
		# Disable Keymap
		self.kmi_set_active(False, type='X')
		self.kmi_set_active(False, type='X', shift=True)
		self.kmi_set_active(False, type='TAB', ctrl=True, shift=True)
		self.kmi_set_active(False, idname='wm.call_panel', type='X', ctrl=True)

	def navigation_keys(self, pan=None, orbit=None, dolly=None, roll=None):
		if orbit:
			self.kmi_set_replace(orbit, self.k_manip, "PRESS", alt=True)
		if pan:
			self.kmi_set_replace(pan, self.k_manip, "PRESS", alt=True, shift=True)
		if dolly:
			self.kmi_set_replace(dolly, self.k_manip, "PRESS", alt=True, ctrl=True)
		if roll:
			self.kmi_set_replace(roll, self.k_context, "PRESS", alt=True)

	def mode_selection(self):
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', properties=[('mode', 0), ('use_extend', False), ('use_expand', False), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', properties=[('mode', 1), ('use_extend', False), ('use_expand', False), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', properties=[('mode', 2), ('use_extend', False), ('use_expand', False), ('alt_mode', False)], disable_double=True)

		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', shift=True, properties=[('mode', 0), ('use_extend', True), ('use_expand', False), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', shift=True, properties=[('mode', 1), ('use_extend', True), ('use_expand', False), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', shift=True, properties=[
							 ('mode', 2), ('use_extend', True), ('use_expand', False), ('alt_mode', False)], disable_double=True)

		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', ctrl=True, properties=[('mode', 0), ('use_extend', False), ('use_expand', True), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', ctrl=True, properties=[
							 ('mode', 1), ('use_extend', False), ('use_expand', True), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', ctrl=True, properties=[
							 ('mode', 2), ('use_extend', False), ('use_expand', True), ('alt_mode', False)], disable_double=True)

		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', ctrl=True, shift=True, properties=[
							 ('mode', 0), ('use_extend', True), ('use_expand', True), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', ctrl=True, shift=True, properties=[
							 ('mode', 1), ('use_extend', True), ('use_expand', True), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', ctrl=True, shift=True, properties=[
							 ('mode', 2), ('use_extend', True), ('use_expand', True), ('alt_mode', False)], disable_double=True)

	def collection_visibility(self, collection_visibility_tool):
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_1', 'PRESS', any=True, properties=[('collection_index', 1)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_2', 'PRESS', any=True, properties=[('collection_index', 2)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_3', 'PRESS', any=True, properties=[('collection_index', 3)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_4', 'PRESS', any=True, properties=[('collection_index', 4)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_5', 'PRESS', any=True, properties=[('collection_index', 5)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_6', 'PRESS', any=True, properties=[('collection_index', 6)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_7', 'PRESS', any=True, properties=[('collection_index', 7)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_8', 'PRESS', any=True, properties=[('collection_index', 8)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_9', 'PRESS', any=True, properties=[('collection_index', 9)])
		self.kmi_set_active(False, idname=collection_visibility_tool, type='ZERO')

	def selection_keys(self,
						select_tool=None, 
						lasso_tool=None, select_through_tool=None,
						box_tool=None, box_through_tool=None, node_box_tool=None,
						circle_tool=None, gp_circle_tool=None,
						shortestpath_tool=None,
						loop_tool=None, ring_tool=None,
						more_tool=None, less_tool=None,
						next_tool=None, previous_tool=None, 
						linked_tool=None):

		# Select / Deselect / Add
		if select_tool:
			self.kmi_set_replace(select_tool, self.k_select, 'CLICK', disable_double=True)
			self.kmi_set_replace(select_tool, self.k_select, 'CLICK', shift=True, properties=[('extend', True)], disable_double=True)
			self.kmi_set_replace(select_tool, self.k_select, 'CLICK', ctrl=True, properties=[('deselect', True)], disable_double=True)
		
		# Lasso Select / Deselect / Add
		if lasso_tool:
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'ANY', disable_double=True)
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'ANY', shift=True, properties=[('mode', 'ADD')], disable_double=True)
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'ANY', ctrl=True, properties=[('mode', 'SUB')], disable_double=True)

		# Lasso through Select / Deselect / Add
		if select_through_tool:
			self.kmi_set_replace(select_through_tool, self.k_lasso_through, 'ANY', properties=[('type', 'LASSO'), ('mode', 'SET')], disable_double=True)
			self.kmi_set_replace(select_through_tool, self.k_lasso_through, 'ANY', shift=True, properties=[('type', 'LASSO'), ('mode', 'ADD')], disable_double=True)
			self.kmi_set_replace(select_through_tool, self.k_lasso_through, 'ANY', ctrl=True, properties=[('type', 'LASSO'), ('mode', 'SUB')], disable_double=True)
		
		# Box Select / Deselect / Add
		if box_tool:
			self.kmi_set_replace(box_tool, self.k_box, 'ANY', properties=[('mode', 'SET'), ('wait_for_input', False), ('tweak', False)], disable_double=True)
			self.kmi_set_replace(box_tool, self.k_box, 'ANY', shift=True, properties=[('mode', 'ADD'), ('wait_for_input', False), ('tweak', False)], disable_double=True)
			self.kmi_set_replace(box_tool, self.k_box, 'ANY', ctrl=True, properties=[('mode', 'SUB'), ('wait_for_input', False), ('tweak', False)], disable_double=True)
		
		if node_box_tool:
			self.kmi_set_replace(node_box_tool, self.k_select, 'CLICK_DRAG', properties=[('mode', 'SET'), ('wait_for_input', False), ('tweak', True)], disable_double=True)
			self.kmi_set_replace(node_box_tool, self.k_box, 'ANY', shift=True, properties=[('mode', 'ADD'), ('wait_for_input', False), ('tweak', False)], disable_double=True)
			self.kmi_set_replace(node_box_tool, self.k_box, 'ANY', ctrl=True, properties=[('mode', 'SUB'), ('wait_for_input', False), ('tweak', False)], disable_double=True)

		# Box Through Select / Deselect / Add
		if box_through_tool:
			self.kmi_set_replace(box_through_tool, self.k_box_through, 'ANY', properties=[('type', 'BOX'), ('mode', 'SET')], disable_double=True)
			self.kmi_set_replace(box_through_tool, self.k_box_through, 'ANY', shift=True, properties=[('type', 'BOX'), ('mode', 'ADD')], disable_double=True)
			self.kmi_set_replace(box_through_tool, self.k_box_through, 'ANY', ctrl=True, properties=[('type', 'BOX'), ('mode', 'SUB')], disable_double=True)
		
		# Circle
		if circle_tool:
			self.kmi_set_replace(circle_tool, self.k_select, 'CLICK_DRAG', shift=True, properties=[('wait_for_input', False), ('mode', 'ADD'), ('radius', 10)], disable_double=True)
			self.kmi_set_replace(circle_tool, self.k_select, 'CLICK_DRAG', ctrl=True, properties=[('wait_for_input', False), ('mode', 'SUB'), ('radius', 10)], disable_double=True)

		if gp_circle_tool:
			self.kmi_set_replace(gp_circle_tool, self.k_select, 'CLICK_DRAG', shift=True, properties=[('wait_for_input', False), ('mode', 'ADD'), ('radius', 10)], disable_double=True)
			self.kmi_set_replace(gp_circle_tool, self.k_select, 'CLICK_DRAG', ctrl=True, properties=[('wait_for_input', False), ('mode', 'SUB'), ('radius', 10)], disable_double=True)

		#  shortest Path Select / Deselect / Add
		if shortestpath_tool:
			self.kmi_remove(idname=shortestpath_tool)
			self.kmi_set_replace(shortestpath_tool, self.k_context, 'CLICK', shift=True, disable_double=True, properties=[('use_fill', False), ('use_face_step', False), ('use_topology_distance', False)])

		# Loop Select / Deselect / Add
		if loop_tool:
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', disable_double=True)
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', shift=True, properties=[('extend', True), ('ring', False)], disable_double=True)
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', ctrl=True, properties=[('extend', False), ('deselect', True)], disable_double=True)

		# Ring Select / Deselect / Add
		if ring_tool:
			self.kmi_set_replace(ring_tool, self.k_cursor, 'CLICK', ctrl=True, properties=[('ring', True), ('deselect', False), ('extend', False), ('toggle', False)], disable_double=True)
			self.kmi_set_replace(ring_tool, self.k_cursor, 'CLICK', ctrl=True, shift=True, properties=[('ring', True), ('deselect', False), ('extend', True), ('toggle', False)], disable_double=True)
			self.kmi_set_replace(ring_tool, self.k_cursor, 'DOUBLE_CLICK', ctrl=True, shift=True, properties=[('ring', True), ('deselect', True), ('extend', False), ('toggle', False)], disable_double=True)

		# Select More / Less
		if more_tool:
			self.kmi_set_replace(more_tool, self.k_more, 'PRESS', shift=True, disable_double=True)

		if less_tool:
			self.kmi_set_replace(less_tool, self.k_less, 'PRESS', shift=True, disable_double=True)
		
		# Select Next / Previous
		if next_tool:
			self.kmi_set_replace(next_tool, self.k_more, 'PRESS', disable_double=True)

		if previous_tool:
			self.kmi_set_replace(previous_tool, self.k_less, 'PRESS', disable_double=True)

		# Linked
		if linked_tool:
			self.kmi_set_replace(linked_tool, self.k_linked, 'PRESS', ctrl=False, properties=[('deselect', False), ('delimit', {'SEAM'})], disable_double=True)
			self.kmi_set_replace(linked_tool, self.k_linked, 'PRESS', ctrl=True, properties=[('deselect', True), ('delimit', {'SEAM'})], disable_double=True)
			self.kmi_set_replace(linked_tool, self.k_linked, 'PRESS', shift=True, properties=[('deselect', False), ('delimit', {'MATERIAL'})])
			self.kmi_set_replace(linked_tool, self.k_linked, 'PRESS', ctrl=True, shift=True, properties=[('deselect', True), ('delimit', {'MATERIAL'})])
			self.kmi_set_replace(linked_tool, self.k_linked, 'PRESS', alt=True, properties=[('deselect', False), ('delimit', {'UV'})])
			self.kmi_set_replace(linked_tool, self.k_linked, 'PRESS', ctrl=True, alt=True, properties=[('deselect', True), ('delimit', {'UV'})])

	def selection_tool(self):
		select_tool = self.kmi_find(idname='wm.tool_set_by_id', properties=KeymapManager.bProp([('name', 'builtin.select_box')]))
		if select_tool:
			self.kmi_prop_setattr(select_tool.properties, "name", 'Select')
			self.kmi_prop_setattr(select_tool.properties, "cycle", False)
		self.kmi_set_replace('wm.tool_set_by_id', self.k_menu, "PRESS", properties=[('name', 'builtin.select'), ('cycle', False)])

	def right_mouse(self):
		kmi = self.kmi_find(idname='wm.call_menu', type='RIGHTMOUSE', value='PRESS')

		if kmi is None:
			print('Cant find right mouse button contextual menu')
		else:
			kmi.value = 'RELEASE'
		
		kmi = self.kmi_find(idname='wm.call_panel', type='RIGHTMOUSE', value='PRESS')

		if kmi is None:
			print('Cant find right mouse button contextual menu')
		else:
			kmi.value = 'RELEASE'

	def duplicate(self, duplicate=None, duplicate_prop=None, duplicate_link=None, duplicate_link_prop=None):
		if duplicate:
			kmi = self.kmi_set_replace(duplicate, 'D', 'PRESS', ctrl=True)
			if duplicate_prop:
				self.kmi_prop_setattr(kmi.properties, duplicate_prop[0], duplicate_prop[1])
		if duplicate_link:
			kmi = self.kmi_set_replace(duplicate_link, 'D', 'PRESS', ctrl=True, shift=True)
			if duplicate_link_prop:
				self.kmi_prop_setattr(kmi.properties, duplicate_link_prop[0], duplicate_link_prop[1])

	def hide_reveal(self, hide=None, unhide=None):
		if hide:
			self.kmi_set_replace(hide, 'H', 'PRESS', properties=[('unselected', False)])
			self.kmi_set_replace(hide, 'H', 'PRESS', ctrl=True, properties=[('unselected', True)])
		if unhide:
			self.kmi_set_replace(unhide, 'H', 'PRESS', alt=True, shift=True, properties=[('select', False)])

	def snap(self, snapping=None, snapping_prop=None):
		type = 'X'

		self.kmi_set_replace('wm.context_toggle', type, 'PRESS', properties=[('data_path', 'tool_settings.use_snap')])
		if snapping is not None and snapping_prop is not None:
			self.kmi_set_replace(snapping, type, 'PRESS', shift=True, properties=snapping_prop)

	def tool_sculpt(self, sculpt=None):
		if sculpt:
			self.kmi_set_replace(sculpt, 'W', 'PRESS', ctrl=True, alt=True, shift=True)

	def tool_smooth(self):
		self.kmi_set_replace('wm.tool_set_by_id', 'S', 'PRESS', shift=True, properties=[('name', 'Smooth')])
	
	def tool_proportional(self):
		self.modal_set_replace('PROPORTIONAL_SIZE', 'MOUSEMOVE', 'ANY', alt=True)
	
	def tool_smart_delete(self):
		self.kmi_set_active(False, type='DEL')
		self.kmi_set_replace('object.tila_smartdelete', 'DEL', 'PRESS')

	def tool_radial_control(self, radius=None, opacity=None, eraser_radius=None):
		type = 'S'
		if radius:
			self.kmi_set_replace('wm.radial_control', type, 'PRESS', properties=radius, disable_double=True)
		if opacity:
			self.kmi_set_replace('wm.radial_control', type, 'PRESS', shift=True, properties=opacity, disable_double=True)
		if eraser_radius:
			self.kmi_set_replace('wm.radial_control', type, 'PRESS', ctrl=True, alt=True, properties=eraser_radius, disable_double=True)

	def tool_subdivision(self, subdivision=None):
		#  Disabling subdivision_set shortcut
		self.kmi_set_active(False, subdivision, type='ZERO')
		self.kmi_set_active(False, subdivision, type='ONE')
		self.kmi_set_active(False, subdivision, type='TWO')
		self.kmi_set_active(False, subdivision, type='THREE')
		self.kmi_set_active(False, subdivision, type='FOUR')
		self.kmi_set_active(False, subdivision, type='FIVE')

		self.kmi_set_replace(subdivision, 'NUMPAD_PLUS', 'PRESS', properties=[('level', 1), ('relative', True)])
		self.kmi_set_replace(subdivision, 'NUMPAD_MINUS', 'PRESS', disable_double=True, properties=[('level', -1), ('relative', True)])

	def tool_center(self, pivot=None, orientation=None):
		print(pivot, orientation)
		if pivot:
			self.kmi_set_replace('wm.call_panel', 'X', 'PRESS', ctrl=True, properties=[('name', pivot), ('keep_open', False)], disable_double=True)
		if orientation:
			self.kmi_set_replace('wm.call_panel', 'X', 'PRESS', ctrl=True, shift=True, properties=[('name', orientation), ('keep_open', False)], disable_double=True)
	
	def tool_transform(self):
		self.kmi_set_replace('wm.tool_set_by_id', self.k_move, 'PRESS', properties=[('name', 'builtin.move')])
		self.kmi_set_replace('wm.tool_set_by_id', self.k_rotate, 'PRESS', properties=[('name', 'builtin.rotate')])
		self.kmi_set_replace('wm.tool_set_by_id', self.k_scale, 'PRESS', properties=[('name', 'builtin.scale')])

	# Keymap define
	def set_tila_keymap(self):
		print("----------------------------------------------------------------")
		print("Assigning Tilapiatsu's keymaps")
		print("----------------------------------------------------------------")
		print("")

		# Window
		self.kmi_init(name='Window', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		# self.kmi_set_replace("wm.call_menu_pie", self.k_menu, "PRESS", ctrl=True, shift=True, alt=True)
		self.kmi_set_replace("wm.revert_without_prompt", "N", "PRESS", shift=True)
		self.kmi_set_replace('wm.console_toggle', 'TAB', 'PRESS', ctrl=True, shift=True)
		
		self.kmi_set_active(False, idname='wm.call_menu', type='F2')
		self.kmi_set_active(False, idname='wm.toolbar')
		self.selection_tool()

		# 3D View
		self.kmi_init(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool()
		self.tool_smart_delete()
		# Disabling zoom key
		self.kmi_set_replace('view3d.zoom', self.k_manip, 'PRESS', ctrl=True, alt=True)
		self.kmi_set_active(False, idname='view3d.select_circle', type="C")

		self.navigation_keys(pan='view3d.move',
							orbit='view3d.rotate',
							dolly='view3d.dolly',
					   		roll='view3d.view_roll')

		self.selection_keys(select_tool='view3d.select', 
							lasso_tool='view3d.select_lasso',
							select_through_tool='view3d.tila_select_through',
					  		circle_tool='view3d.select_circle')

		self.kmi_set_active(False, idname='view3d.select', shift=True)

		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)
		self.snap(snapping='wm.call_panel', snapping_prop=[('name', 'VIEW3D_PT_snapping')])

		self.mode_selection()

		self.kmi_set_replace('view3d.view_persportho', 'NUMPAD_ASTERIX', 'PRESS')

		self.collection_visibility('object.hide_collection')

		self.kmi_set_replace('view3d.view_selected', 'A', 'PRESS', ctrl=True, shift=True)

		self.tool_center(pivot='VIEW3D_PT_pivot_point', orientation='VIEW3D_PT_transform_orientations')

		self.kmi_set_replace('wm.call_menu_pie', 'Q', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('name', 'HP_MT_boolean')])
		

		# 3d Cursor
		kmi = self.kmi_set_replace('view3d.cursor3d', self.k_cursor, 'CLICK', ctrl=True, alt=True, shift=True, properties=[('use_depth', True)])
		self.kmi_prop_setattr(kmi.properties, 'orientation', 'GEOM')
		self.kmi_set_replace('transform.translate', 'EVT_TWEAK_M', 'ANY', ctrl=True, alt=True, shift=True, properties=[('cursor_transform', True), ('release_confirm', True)])

		# View2D
		self.kmi_init(name='View2D', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')

		# View2D buttons List
		self.kmi_init(name='View2D Buttons List', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')

		# Image
		self.kmi_init(name='Image', space_type='IMAGE_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='image.view_pan', orbit=None, dolly='image.view_zoom')

		# UV Editor
		self.kmi_init(name='UV Editor', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool()
		self.selection_keys(select_tool='uv.select',
					  		lasso_tool='uv.select_lasso',
					  		circle_tool='uv.select_circle',
					  		loop_tool='uv.select_loop',
					  		more_tool='uv.select_more',
					  		less_tool='uv.select_less',
					  		linked_tool='uv.select_linked_pick')
		
		self.kmi_set_replace('uv.cursor_set', self.k_cursor, 'PRESS', ctrl=True, alt=True, shift=True)
		self.tool_smooth()
		self.hide_reveal(hide='uv.hide', unhide='uv.reveal')
		self.snap(snapping='wm.context_menu_enum', snapping_prop=[('data_path', 'tool_settings.snap_uv_element')])
		self.tool_center(pivot='SpaceImageEditor.pivot_point')

		# Mesh
		self.kmi_init(name='Mesh', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.mode_selection()
		self.tool_transform()

		self.selection_keys(shortestpath_tool='mesh.shortest_path_pick',
							loop_tool='mesh.loop_select',
					  		ring_tool='mesh.edgering_select',
							more_tool='mesh.select_more',
							less_tool='mesh.select_less',
							next_tool='mesh.select_next_item',
							previous_tool='mesh.select_prev_item',
							linked_tool='mesh.select_linked_pick')

		# self.kmi_set_active(False, idname='mesh.select_linked_pick', ctrl=False)
		# self.kmi_set_active(False, idname='mesh.select_linked_pick', ctrl=True, alt=False, shift=False, properties=[('deselect', True)])

		self.duplicate(duplicate='mesh.duplicate_move')
		self.hide_reveal(hide='mesh.hide', unhide='mesh.reveal')
		self.tool_smart_delete()

		self.tool_smooth()
		self.kmi_set_active(False, 'view3d.select_box')
		self.kmi_set_replace('mesh.bevel', 'B', 'PRESS')
		self.kmi_set_replace('mesh.knife_tool', 'C', 'PRESS')
		self.kmi_set_replace('wm.tool_set_by_id', 'C', 'PRESS', alt=True, shift=True, properties=[('name', 'builtin.loop_cut')])
		self.kmi_set_replace('mesh.bridge_edge_loops', 'B', 'PRESS', shift=True)
		self.kmi_set_replace('mesh.edge_collapse', 'DEL', 'PRESS', shift=True)
		self.kmi_set_replace('mesh.fill', 'P', 'PRESS', shift=True, properties=[('use_beauty', True)])
		self.kmi_set_replace('mesh.edge_face_add', 'P', 'PRESS')
		self.kmi_set_replace('mesh.flip_normals', 'F', 'PRESS')
		self.kmi_set_replace('mesh.subdivide', 'D', 'PRESS')
		self.kmi_set_replace('mesh.extrude_region_shrink_fatten', 'E', 'PRESS', disable_double=True)

		self.kmi_set_replace('mesh.remove_doubles', 'M', 'PRESS', ctrl=True, shift=True, disable_double=True)
		kmi = self.kmi_set_replace('mesh.separate', 'D', 'PRESS', ctrl=True, shift=True, properties=(['type', 'SELECTED']))
		self.kmi_prop_setattr(kmi.properties, 'type', 'SELECTED')

		self.tool_subdivision(subdivision='object.subdivision_set')

		self.tool_sculpt('sculpt.sculptmode_toggle')
		
		self.tool_center(pivot='VIEW3D_PT_pivot_point', orientation='VIEW3D_PT_transform_orientations')

		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True)
		self.kmi_set_replace('mesh.toggle_x_symetry', 'X', 'PRESS', ctrl=True, alt=True)

		self.kmi_set_replace('mesh.toggle_use_automerge', 'BACK_SLASH', 'PRESS')
		self.kmi_set_replace('mesh.select_all', 'RIGHTMOUSE', 'CLICK', ctrl=True, alt=True, shift=True, properties=[('action', 'INVERT')])
		# self.kmi_set_replace('object.merge_tool', 'M', 'PRESS')
		self.kmi_set_replace('transform.tosphere', 'S', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True)
		self.kmi_set_replace('wm.call_menu_pie', 'S', 'PRESS', alt=True, shift=True, properties=[('name', 'TILA_MT_pie_normal')], disable_double=True)

		# Object Mode
		self.kmi_init(name='Object Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.tool_transform()
		self.duplicate(duplicate='object.duplicate_move', duplicate_link='object.duplicate_move_linked')

		self.tool_subdivision(subdivision='object.subdivision_set')
		self.kmi_set_replace('object.delete', 'DEL', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('use_global', True), ('confirm', True)])

		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True)
		
		self.kmi_set_replace('object.move_to_collection', 'M', 'PRESS', ctrl=True, alt=True, disable_double=True)
		# Set collection visibility shortcut
		self.collection_visibility('object.hide_collection')
		self.mode_selection()
		self.kmi_set_replace('view3d.tila_smart_editmode', 'TAB', 'PRESS', shift=True, properties=[('alt_mode', True)], disable_double=True)
		
		self.tool_sculpt('sculpt.sculptmode_toggle')
		self.kmi_set_replace('transform.tosphere', 'S', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True)
		self.kmi_set_replace('wm.call_menu_pie', 'S', 'PRESS', alt=True, shift=True, properties=[('name', 'TILA_MT_pie_normal')], disable_double=True)

		# Sculpt
		self.kmi_init(name='Sculpt', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.tool_sculpt('sculpt.sculptmode_toggle')

		self.tool_radial_control(radius=[('data_path_primary', 'tool_settings.sculpt.brush.size'), ('data_path_secondary', 'tool_settings.unified_paint_settings.size'), ('use_secondary', 'tool_settings.unified_paint_settings.use_unified_size'), ('rotation_path', 'tool_settings.sculpt.brush.texture_slot.angle'), ('color_path', 'tool_settings.sculpt.brush.cursor_color_add'), ('image_id', 'tool_settings.sculpt.brush')],
						   		opacity=[('data_path_primary', 'tool_settings.sculpt.brush.strength'), ('data_path_secondary', 'tool_settings.unified_paint_settings.strength'), ('use_secondary', 'tool_settings.unified_paint_settings.use_unified_strength'), (
							   'rotation_path', 'tool_settings.sculpt.brush.texture_slot.angle'), ('color_path', 'tool_settings.sculpt.brush.cursor_color_add'), ('image_id', 'tool_settings.sculpt.brush')],
						   		eraser_radius=[('data_path_primary', 'tool_settings.sculpt.brush.texture_slot.angle'), ('rotation_path', 'tool_settings.sculpt.brush.texture_slot.angle'), ('color_path', 'tool_settings.sculpt.brush.cursor_color_add'), ('image_id', 'tool_settings.sculpt.brush')])

		self.kmi_set_replace('sculpt.tila_multires_subdivision', 'D', 'PRESS', properties=[('subd', 1), ('relative', True), ('increase_subd', False)])
		self.kmi_set_replace('sculpt.tila_multires_subdivision', 'D', 'PRESS', ctrl=True, properties=[('subd', 1), ('relative', True), ('increase_subd', True)])
		self.kmi_set_replace('sculpt.tila_multires_subdivision', 'D', 'PRESS', shift=True, properties=[('subd', -1), ('relative', True), ('increase_subd', False)])
		self.kmi_set_replace('sculpt.dynamic_topology_toggle', 'D', 'PRESS', ctrl=True, alt=True, shift=True)
		
		self.kmi_set_replace('paint.mask_lasso_gesture', self.k_context, 'PRESS', ctrl=True, properties=[('value', 1.0), ('mode', 'VALUE')])
		self.kmi_set_replace('paint.mask_lasso_gesture', self.k_context, 'PRESS', shift=True, properties=[('value', 0.0), ('mode', 'VALUE')])

		self.kmi_set_replace('paint.hide_show', self.k_nav, 'CLICK_DRAG',  properties=[('action', 'HIDE'), ('wait_for_input', False), ('area', 'INSIDE')], disable_double=True)
		self.kmi_set_replace('paint.hide_show', self.k_nav, 'CLICK_DRAG', shift=True, properties=[('action', 'SHOW'), ('wait_for_input', False), ('area', 'OUTSIDE')], disable_double=True)
		
		# Curve
		self.kmi_init(name='Curve', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.tool_transform()
		self.right_mouse()
		self.duplicate(duplicate='curve.duplicate_move')
		self.tool_smart_delete()
		self.kmi_set_replace('curve.select_linked', self.k_select, 'DOUBLE_CLICK', shift=True)
		self.kmi_set_replace('curve.select_linked_pick', self.k_select, 'DOUBLE_CLICK')
		self.kmi_set_replace('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.shortest_path_pick', self.k_select, 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True, ctrl=True, shift=True, properties=[('wait_for_input', False)])

		# Outliner
		self.kmi_init(name='Outliner', space_type='OUTLINER', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('outliner.item_rename', 'F2', 'PRESS')

		self.tool_smart_delete()
		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)

		# File Browser
		self.kmi_init(name='File Browser', space_type='FILE_BROWSER', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_smart_delete()
		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)

		# Dopesheet
		self.kmi_init(name='Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='node.duplicate_move', duplicate_link='node.duplicate_move_keep_inputs')

		# Mask Editing
		self.kmi_init(name='Mask Editing', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('mask.duplicate_move', 'D', 'PRESS', ctrl=True)

		# Graph Editor
		self.kmi_init(name='Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='graph.duplicate_move')

		# Node Editor
		self.kmi_init(name='Node Editor', space_type='NODE_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		self.selection_keys(node_box_tool='node.select_box')
		self.kmi_set_active(False, idname='node.select_box', type=self.k_box)
		# self.kmi_set_active(False, idname='transform.translate', type=self.k_box)
		# self.kmi_set_active(False, idname='transform.translate', type=self.k_box, properties=[('release_confirm', True)])
		self.kmi_remove(idname='transform.translate', type=self.k_box)
		self.kmi_remove(idname='node.translate_attach', type=self.k_box)
		self.kmi_remove(idname='node.translate_attach', type=self.k_box)

		self.kmi_set_replace('transform.translate', self.k_box, 'ANY', properties=[('release_confirm', True)])
		# self.kmi_set_replace('node.translate_attach', self.k_select_attatched, 'ANY')

		self.duplicate(duplicate='node.duplicate_move', duplicate_link='node.duplicate_move_keep_inputs')
		self.snap(snapping='wm.context_menu_enum', snapping_prop=[('data_path', 'tool_settings.snap_node_element')])

		# Animation
		self.kmi_init(name='Animation', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		# Armature
		self.kmi_init(name='Armature', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='armature.duplicate_move')

		# Metaball
		self.kmi_init(name='Metaball', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='mball.duplicate_move')

		# NLA Editor
		self.kmi_init(name='NLA Editor', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='nla.duplicate', duplicate_link='nla.duplicate', duplicate_link_prop=('linked', True))

		# Grease Pencil
		self.kmi_init(name='Grease Pencil', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.mode_selection()
		self.duplicate(duplicate='gpencil.duplicate_move')
		self.kmi_set_replace('view3d.tila_smart_editmode', 'TAB', 'PRESS', shift=True, properties=[('alt_mode', True)], disable_double=True)
		self.selection_keys(select_tool='gpencil.select',
							lasso_tool='gpencil.select_lasso',
					  		gp_circle_tool='gpencil.select_circle',
					  		more_tool='gpencil.select_more',
					  		less_tool='gpencil.select_less',
					  		next_tool='gpencil.select_first',
					  		previous_tool='gpencil.select_last',
					  		linked_tool='gpencil.select_linked')

		self.tool_sculpt('gpencil.sculptmode_toggle')

		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True)

		# Grease Pencil Stroke Edit Mode
		self.kmi_init(name='Grease Pencil Stroke Edit Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='gpencil.duplicate_move')
		self.collection_visibility('object.hide_collection')
		self.mode_selection()
		self.tool_smart_delete()
		self.kmi_set_active(False, idname='gpencil.dissolve')
		self.kmi_set_active(False, idname='gpencil.active_frames_delete_all')
		self.kmi_set_replace('gpencil.dissolve', 'DEL', 'PRESS', shift=True, properties=[('type', 'POINTS')], disable_double=True)
		self.kmi_set_replace('gpencil.active_frames_delete_all', 'DEL', 'PRESS', ctrl=True, alt=True, shift=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', 'TAB', 'PRESS', shift=True, properties=[('alt_mode', True)], disable_double=True)
		self.selection_keys(gp_circle_tool='gpencil.select_circle',
							more_tool='gpencil.select_more',
					  		less_tool='gpencil.select_less')

		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True)

		# Grease Pencil Stroke Paint Mode
		self.kmi_init(name='Grease Pencil Stroke Paint Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='gpencil.duplicate_move')
		self.collection_visibility('object.hide_collection')
		self.mode_selection()
		self.kmi_set_replace('view3d.tila_smart_editmode', 'TAB', 'PRESS', shift=True, properties=[('alt_mode', True)], disable_double=True)
		self.tool_radial_control(radius=[('data_path_primary', 'tool_settings.gpencil_paint.brush.size')], opacity=[('data_path_primary', 'tool_settings.gpencil_paint.brush.gpencil_settings.pen_strength')],
								 eraser_radius=[('data_path_primary', 'preferences.edit.grease_pencil_eraser_radius')])
		
		# Grease Pencil Stroke Paint (Draw brush)
		self.kmi_init(name='Grease Pencil Stroke Paint (Draw brush)', space_type='EMPTY', region_type='WINDOW')
		kmi = self.kmi_find(idname='gpencil.draw', ctrl=False, alt=True, shift=False)
		if kmi:
			kmi.ctrl = True
			kmi.alt = False
			kmi.shift = True

		kmi = self.kmi_find(idname='gpencil.draw', ctrl=False, alt=True, shift=True)
		if kmi:
			kmi.ctrl = True
			kmi.alt = True
			kmi.shift = True

		# Grease Pencil Stroke Sculpt Mode
		self.kmi_init(name='Grease Pencil Stroke Sculpt Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_radial_control(radius=[('data_path_primary', 'tool_settings.gpencil_sculpt.brush.size')], opacity=[('data_path_primary', 'tool_settings.gpencil_sculpt.brush.strength')])

		# Frames
		self.kmi_init(name='Frames', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('screen.animation_play', 'SPACE', 'PRESS', ctrl=True, shift=True,  properties=[('reverse', True)])

		# Screen
		self.kmi_init(name='Screen', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('screen.screen_full_area', 'SPACE', 'PRESS', ctrl=True, alt=True)
		self.kmi_set_replace('screen.screen_full_area', 'SPACE', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('use_hide_panels', True)])

		# Transform Modal Map
		self.kmi_init(name='Transform Modal Map', space_type='EMPTY', region_type='WINDOW')
		self.tool_proportional()
		
		# Knife Tool Modal Map
		self.kmi_init(name='Knife Tool Modal Map', space_type='EMPTY', region_type='WINDOW')
		panning = self.kmi_find(propvalue='PANNING')
		if panning:
			panning.type = self.k_select
			panning.value = 'ANY'
			panning.any = True

		add_cut = self.kmi_find(propvalue='ADD_CUT')
		if add_cut:
			add_cut.type = 'RIGHTMOUSE'

		end_cut = self.kmi_find(propvalue='NEW_CUT')
		if end_cut:
			end_cut.type = 'MIDDLEMOUSE'

		self.modal_set_replace('NEW_CUT', 'SPACE', 'PRESS')
		
		# Gesture Box Modal Map
		self.kmi_init(name='Gesture Box', space_type='EMPTY', region_type='WINDOW')
		self.modal_set_replace('SELECT', self.k_cursor, 'RELEASE', any=True)

		print("----------------------------------------------------------------")
		print("Assignment complete")
		print("----------------------------------------------------------------")
		print("")


def hp_keymaps():

	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
	k_viewfit = 'MIDDLEMOUSE'
	k_manip = 'LEFTMOUSE'
	k_cursor = 'RIGHTMOUSE'
	k_nav = 'MIDDLEMOUSE'
	k_menu = 'SPACE'
	k_select = 'LEFTMOUSE'
	k_lasso = 'RIGHTMOUSE'

	def global_keys():
		kmi = km.keymap_items.new("screen.userpref_show", "TAB", "PRESS", ctrl=True)
		kmi = km.keymap_items.new("wm.window_fullscreen_toggle", "F11", "PRESS")
		kmi = km.keymap_items.new('screen.animation_play', 'PERIOD', 'PRESS')
		kmi = km.keymap_items.new("popup.hp_properties", 'V',"PRESS", ctrl=True, shift=True)
	# kmi = km.keymap_items.new('gpencil.blank_frame_add', 'B', 'PRESS', key_modifier='FOUR')
# "ACCENT_GRAVE"
#Window
	km = kc.keymaps.new('Window', space_type='EMPTY', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('object.hide_viewport', 'H', 'PRESS')
	kmi = km.keymap_items.new('wm.save_homefile', 'U', 'PRESS', ctrl=True)     
	kmi = km.keymap_items.new('transform.translate', 'SPACE', 'PRESS')

	kmi = km.keymap_items.new('view3d.smart_delete', 'X', 'PRESS')
	kmi = km.keymap_items.new('mesh.dissolve_mode', 'X', 'PRESS',ctrl=True)
#kmi = km.keymap_items.new('transform.resize', 'SPACE', 'PRESS', alt=True)
	kmi = km.keymap_items.new('transform.rotate', 'C', 'PRESS')
	kmi = km.keymap_items.new("wm.window_fullscreen_toggle","F11","PRESS")
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True ,shift=True, alt=True).properties.name="pie.areas"
	kmi = km.keymap_items.new("wm.revert_without_prompt","N","PRESS", alt=True)
	kmi = km.keymap_items.new("screen.redo_last","D","PRESS")
	kmi = km.keymap_items.new('wm.console_toggle', 'TAB', 'PRESS', ctrl=True, shift=True)     

	kmi = km.keymap_items.new("wm.call_menu_pie","S","PRESS", ctrl=True).properties.name="pie.save"
	kmi = km.keymap_items.new("wm.call_menu_pie","S","PRESS", ctrl=True, shift=True).properties.name="pie.importexport"
	kmi = km.keymap_items.new('script.reload', 'U', 'PRESS', shift=True)
	kmi = km.keymap_items.new("screen.repeat_last","THREE","PRESS", ctrl=True, shift=True)
	kmi = km.keymap_items.new("ed.undo","TWO","PRESS", ctrl=True, shift=True)
	kmi = km.keymap_items.new('popup.hp_materials', 'V', 'PRESS', shift=True)   
	kmi = km.keymap_items.new('screen.frame_jump', 'PERIOD', 'PRESS', shift=True)
# Map Image
	km = kc.keymaps.new('Image', space_type='IMAGE_EDITOR', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('image.view_all', k_viewfit, 'PRESS', ctrl=True, shift=True)
	kmi_props_setattr(kmi.properties, 'fit_view', True)
	kmi = km.keymap_items.new('image.view_pan', k_nav, 'PRESS', shift=True)
	kmi = km.keymap_items.new('image.view_zoom', k_nav, 'PRESS', ctrl=True)

# Map Node Editor
	km = kc.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('node.view_selected', k_viewfit, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('node.select_box', 'EVT_TWEAK_L', 'ANY')
	kmi_props_setattr(kmi.properties, 'extend', True)
	kmi_props_setattr(kmi.properties, 'tweak', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
# Map View2D
	km = kc.keymaps.new('View2D', space_type='EMPTY', region_type='WINDOW', modal=False)
# Map Animation
	km = kc.keymaps.new('Animation', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('anim.change_frame', k_select, 'PRESS')

	

# Map Graph Editor
	km = kc.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('graph.view_selected', k_viewfit, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('graph.cursor_set', k_cursor, 'PRESS')
	# kmi = km.keymap_items.new('graph.select_lasso', 'EVT_TWEAK_L', 'ANY', shift=True, ctrl=True)
	# kmi_props_setattr(kmi.properties, 'extend', True)
	# kmi = km.keymap_items.new('graph.select_lasso', 'EVT_TWEAK_L', 'ANY', ctrl=True)
	# kmi_props_setattr(kmi.properties, 'deselect', True)
	kmi = km.keymap_items.new('graph.select_box', 'EVT_TWEAK_L', 'ANY', ctrl=True, shift=True)
	kmi_props_setattr(kmi.properties, 'deselect', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('graph.select_box', 'EVT_TWEAK_L', 'ANY')
	kmi_props_setattr(kmi.properties, 'extend', False)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('graph.select_box', 'EVT_TWEAK_L', 'ANY', shift=True)
	kmi_props_setattr(kmi.properties, 'extend', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
# Map UV Editor
	km = kc.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True, alt=True).properties.name="pie.rotate90"
	kmi = km.keymap_items.new('uv.select_lasso', 'EVT_TWEAK_L', 'ANY', shift=True, ctrl=True)
	kmi_props_setattr(kmi.properties, 'extend', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('uv.select_lasso', 'EVT_TWEAK_L', 'ANY', ctrl=True)
	kmi_props_setattr(kmi.properties, 'deselect', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('uv.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
	kmi_props_setattr(kmi.properties, 'extend', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('uv.select_border', 'EVT_TWEAK_L', 'ANY')
	kmi_props_setattr(kmi.properties, 'extend', False)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
# Map Mask Editing
#    km = kc.keymaps.new('Mask Editing', space_type='EMPTY', region_type='WINDOW', modal=False)
#3D View
	km = kc.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('mesh.hp_extrude', 'SPACE', 'PRESS', shift=True)
	kmi = km.keymap_items.new('view3d.render_border', 'B', 'PRESS',shift=True, ctrl=True)
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True ,shift=True, alt=True).properties.name="pie.areas"
#    kmi = km.keymap_items.new('view3d.select_lasso', 'EVT_TWEAK_L', 'ANY', alt=True)
	kmi = km.keymap_items.new('view3d.view_selected', k_nav, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('view3d.move', k_nav, 'PRESS', shift=True)
	kmi = km.keymap_items.new('view3d.zoom', k_nav, 'PRESS', ctrl=True)
	kmi = km.keymap_items.new('view3d.rotate', k_nav, 'PRESS')
	kmi = km.keymap_items.new('view3d.manipulator', k_manip, 'PRESS')
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True).properties.name="pie.select"
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu, 'PRESS',ctrl=True, alt=True).properties.name="pie.rotate90"
	kmi = km.keymap_items.new("wm.call_menu_pie", 'V', 'PRESS').properties.name="pie.view"
	kmi = km.keymap_items.new('wm.call_menu_pie', k_menu,'PRESS',ctrl=True, shift=True).properties.name="pie.pivots"
	kmi = km.keymap_items.new("wm.call_menu_pie","Z","PRESS").properties.name="pie.shading"
	kmi = km.keymap_items.new("wm.call_menu_pie","D","PRESS",ctrl=True, shift=True).properties.name="pie.specials"
	kmi = km.keymap_items.new("wm.call_menu_pie","ONE","PRESS").properties.name="pie.modifiers"
	kmi = km.keymap_items.new("wm.call_menu_pie","X","PRESS",shift=True).properties.name="pie.symmetry"
	kmi = km.keymap_items.new('wm.call_menu_pie', 'B', 'PRESS',ctrl=True).properties.name="pie.hp_boolean"
	kmi = km.keymap_items.new("screen.repeat_last","Z","PRESS",ctrl=True, alt=True)
	kmi = km.keymap_items.new("screen.repeat_last","WHEELINMOUSE","PRESS",ctrl=True, shift=True, alt=True)
	kmi = km.keymap_items.new("ed.undo","WHEELOUTMOUSE","PRESS",ctrl=True, shift=True, alt=True)
	kmi = km.keymap_items.new("view3d.screencast_keys","U","PRESS",alt=True)
	kmi = km.keymap_items.new("paint.sample_color","V","PRESS",ctrl=True, shift=True)
	kmi = km.keymap_items.new('view3d.select_lasso', k_select, 'CLICK_DRAG', shift=True, ctrl=True)
	kmi = km.keymap_items.new('view3d.select_box', k_select, 'CLICK_DRAG', ctrl=True).properties.mode='SUB'
	kmi = km.keymap_items.new('view3d.select_box', k_select, 'CLICK_DRAG', shift=True).properties.mode='ADD'
	kmi = km.keymap_items.new('view3d.select_box', k_select, 'CLICK_DRAG').properties.mode='SET'
	kmi = km.keymap_items.new("wm.search_menu","FIVE","PRESS")
	kmi = km.keymap_items.new("view3d.subdivision_toggle","TAB","PRESS")
	kmi = km.keymap_items.new("view3d.smart_snap_cursor","RIGHTMOUSE","PRESS",ctrl=True)
	kmi = km.keymap_items.new("view3d.smart_snap_origin","RIGHTMOUSE","PRESS",ctrl=True, shift=True)
#Mesh
	km = kc.keymaps.new(name='Mesh')
	global_keys()
	#kmi = km.keymap_items.new('view3d.extrude_normal', 'EVT_TWEAK_L', 'ANY', shift=True)
	kmi = km.keymap_items.new("mesh.dupli_extrude_cursor", 'E', 'PRESS')
	kmi = km.keymap_items.new("transform.edge_bevelweight", 'E', 'PRESS', ctrl=True, shift=True)
	#kmi = km.keymap_items.new("mesh.primitive_cube_add_gizmo", 'EVT_TWEAK_L', 'ANY', alt=True)
	kmi = km.keymap_items.new('view3d.select_through_border', k_select, 'CLICK_DRAG')
	kmi = km.keymap_items.new('view3d.select_through_border_add', k_select, 'CLICK_DRAG', shift=True)
	kmi = km.keymap_items.new('view3d.select_through_border_sub', k_select, 'CLICK_DRAG', ctrl=True)
	kmi = km.keymap_items.new("wm.call_menu_pie","A","PRESS", shift=True).properties.name="pie.add"
	kmi = km.keymap_items.new("wm.call_menu","W","PRESS").properties.name="VIEW3D_MT_edit_mesh_specials"
	kmi = km.keymap_items.new("screen.userpref_show","TAB","PRESS", ctrl=True)
	kmi = km.keymap_items.new("view3d.subdivision_toggle","TAB","PRESS")
#    kmi = km.keymap_items.new('mesh.select_all', k_select, 'CLICK', ctrl=True)
#    kmi_props_setattr(kmi.properties, 'action', 'INVERT')
	kmi = km.keymap_items.new('mesh.shortest_path_pick', 'LEFTMOUSE', 'CLICK',ctrl=True, shift=True).properties.use_fill=True
	kmi = km.keymap_items.new('mesh.select_linked', k_select, 'DOUBLE_CLICK')
	kmi_props_setattr(kmi.properties, 'delimit', {'SEAM'})
	kmi = km.keymap_items.new('mesh.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
	kmi_props_setattr(kmi.properties, 'delimit', {'SEAM'})
	kmi = km.keymap_items.new('mesh.select_more', 'WHEELINMOUSE', 'PRESS',ctrl=True, shift=True)    
	kmi = km.keymap_items.new('mesh.select_less', 'WHEELOUTMOUSE', 'PRESS',ctrl=True, shift=True)
	kmi = km.keymap_items.new('mesh.select_more', 'Z', 'PRESS',alt=True)    
	kmi = km.keymap_items.new('mesh.select_next_item', 'WHEELINMOUSE', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.select_next_item', 'Z', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.select_prev_item', 'WHEELOUTMOUSE', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.edgering_select', k_select, 'DOUBLE_CLICK', alt=True).properties.extend = False
	kmi = km.keymap_items.new('mesh.loop_multi_select', k_select, 'DOUBLE_CLICK', alt=True, shift=True)
	kmi = km.keymap_items.new('mesh.loop_select', k_select, 'PRESS', alt=True, shift=True).properties.extend = True
	kmi = km.keymap_items.new('mesh.loop_select', k_select, 'PRESS', alt=True).properties.extend = False
	kmi = km.keymap_items.new('mesh.normals_make_consistent', 'N', 'PRESS', ctrl=True).properties.inside = False
	kmi = km.keymap_items.new("wm.call_menu_pie","FOUR","PRESS").properties.name="GPENCIL_PIE_tool_palette"
	kmi = km.keymap_items.new("mesh.select_prev_item","TWO","PRESS")
	kmi = km.keymap_items.new("mesh.select_next_item","THREE","PRESS")
	kmi = km.keymap_items.new("mesh.select_less","TWO","PRESS", ctrl=True)
	kmi = km.keymap_items.new("mesh.select_more","THREE","PRESS", ctrl=True)
	kmi = km.keymap_items.new("mesh.inset", "SPACE", "PRESS", alt=True)
	kmi = km.keymap_items.new("mesh.push_and_slide","G","PRESS", shift=True)
#    kmi_props_setattr(kmi.properties, 'use_even_offset', True)
	kmi = km.keymap_items.new('mesh.separate_and_select', 'P', 'PRESS')
#    kmi = km.keymap_items.new('view3d.extrude_normal', 'B', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.bridge_edge_loops', 'B', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.bridge_edge_loops', 'B', 'PRESS', ctrl=True, shift=True).properties.number_cuts = 12
	kmi = km.keymap_items.new('transform.edge_bevelweight','B', 'PRESS', alt=True).properties.value = 1
	kmi = km.keymap_items.new('mesh.smart_bevel','B', 'PRESS')
	kmi = km.keymap_items.new('mesh.merge', 'J', 'PRESS', ctrl=True)
	kmi_props_setattr(kmi.properties, 'type', 'LAST')
	kmi = km.keymap_items.new('mesh.reveal', 'H', 'PRESS', ctrl=True, shift=True)
#Grease Pencil
	km = kc.keymaps.new('Grease Pencil', space_type='EMPTY', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('gpencil.select_linked', k_select, 'DOUBLE_CLICK')
	kmi = km.keymap_items.new('gpencil.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
	kmi = km.keymap_items.new('gpencil.select_box', k_select,'CLICK_DRAG')
	kmi_props_setattr(kmi.properties, 'mode', 'SET')
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('gpencil.select_box', k_select,'CLICK_DRAG', ctrl=True)
	kmi_props_setattr(kmi.properties, 'mode', 'SUB')
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('gpencil.select_box', k_select, 'CLICK_DRAG', shift=True)
	kmi_props_setattr(kmi.properties, 'mode', 'ADD')
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)

#Object Mode
	km = kc.keymaps.new(name='Object Mode')
	global_keys()    
	kmi = km.keymap_items.new('object.select_all', k_select, 'CLICK_DRAG')
	kmi_props_setattr(kmi.properties, 'action', 'DESELECT')
#    kmi = km.keymap_items.new('object.select_all', k_select, 'CLICK', ctrl=True)
#    kmi_props_setattr(kmi.properties, 'action', 'INVERT')
	kmi = km.keymap_items.new('object.hide_view_clear', 'H', 'PRESS', ctrl=True, shift=True)

# Map Curve
	km = kc.keymaps.new('Curve', space_type='EMPTY', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('curve.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
	kmi = km.keymap_items.new('curve.select_linked_pick', k_select, 'DOUBLE_CLICK')
	kmi = km.keymap_items.new('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('curve.shortest_path_pick', k_select, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)

# Outliner
	km = kc.keymaps.new('Outliner', space_type='OUTLINER', region_type='WINDOW', modal=False)
	global_keys()

#    kmi = km.keymap_items.new('outliner.collection_drop', k_select, 'CLICK_DRAG',shift=True)
#    kmi = km.keymap_items.new('outliner.select_box', 'EVT_TWEAK_L', 'ANY')
	kmi = km.keymap_items.new('outliner.show_active', k_nav, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('wm.delete_without_prompt', 'X', 'PRESS')
# Map DOPESHEET_EDITOR
	km = kc.keymaps.new('Dopesheet Editor', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('time.start_frame_set', 'S', 'PRESS')
	kmi = km.keymap_items.new('time.end_frame_set', 'E', 'PRESS')
	kmi = km.keymap_items.new('time.view_all', 'HOME', 'PRESS')
	kmi = km.keymap_items.new('time.view_all', k_viewfit, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('time.view_all', 'NDOF_BUTTON_FIT', 'PRESS')
	kmi = km.keymap_items.new('time.view_frame', 'NUMPAD_0', 'PRESS')

keymap_List = {}
def register():
	TK = TilaKeymaps()
	TK.set_tila_keymap()

	keymap_List['new'] = TK.keymap_List['new']
	keymap_List['replaced'] = TK.keymap_List['replaced']
	# print("----------------------------------------------------------------")
	# print("Disabling redundant keymap ")
	# print("----------------------------------------------------------------")
	# print("")
	# for kmi in TK.keymap_List["disable"]:
	# 	print("Disabling '{}'".format(kmi.name))
	# 	kmi.active = False

def unregister():
	print("----------------------------------------------------------------")
	print("Reverting Tilapiatsu's keymap")
	print("----------------------------------------------------------------")
	print("")

	TK = TilaKeymaps()
	for k in keymap_List['replaced']:
		try:
			TK.km = k['km']
			print("{} : Replacing '{}' : '{}'  by '{}' : '{}'".format(k['km'].name, k['new_kmi'].idname, k['new_kmi'].to_string(), k['old_kmi'].idname, k['old_kmi'].to_string()))
			TK.replace_km(k['old_kmi'], k['kmis'].from_id(k['old_kmi_id']))
		except Exception as e:
			print("Warning: %r" % e)

	for k in keymap_List['new']:
		try:
			TK.km = k[0]
			print("{} : Removing keymap for '{}' : '{}'".format(k[0].name, k[1].idname, k[1].to_string()))
			TK.km.keymap_items.remove(k[1])
			
		except Exception as e:
			print("Warning: %r" % e)
	
	keymap_List.clear()

	print("----------------------------------------------------------------")
	print("Revert complete")
	print("----------------------------------------------------------------")
	print("")

if __name__ == "__main__":
	register()
