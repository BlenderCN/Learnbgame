######################################################################################################
# An simple add-on to auto cut in two and mirror an object                                           #
# Actualy partialy uncommented (see further version)                                                 #
# Author: Lapineige,
#  Robert Fornof & MX,
#  Bookyakuno                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################
# 2.8 update by Bookyakuno, meta-androcto

bl_info = {
	"name": "Auto Mirror 28",
	"description": "Super fast cutting and mirroring for mesh",
	"author": "Lapineige, Robert Fornof & MX",
	"version": (2, 6, 0),
	"blender": (2, 80, 0),
	"location": "View 3D > Rightbar > Tools tab > AutoMirror (panel)",
	"warning": "",
	"wiki_url": "https://wiki.blender.org/index.php/Extensions:2.6/"
				"Py/Scripts/Modeling/AutoMirror",
	"category": "Mesh"}


import bpy
from mathutils import Vector

import bmesh
import bpy
import collections
import mathutils
import math
import rna_keymap_ui # キーマップリストに必要
from bpy.app.handlers import persistent
from bpy_extras import view3d_utils
from bpy.types import (
		Operator,
		Menu,
		Panel,
		PropertyGroup,
		AddonPreferences,
		)
from bpy.props import (
		BoolProperty,
		EnumProperty,
		FloatProperty,
		IntProperty,
		PointerProperty,
		StringProperty,
		)



#------------------- FUNCTIONS------------------------------

def Operation(context,_operation):
	#         ''' select the object, then select what you want it's mirror object to be '''
			#select 2 context object

		try:
			# select objects

			if(len(bpy.context.selected_objects)) == 1 : # one is selected , add mirror mod immediately to that object#
				modifier_ob = bpy.context.active_object
				print("one is selected")
				mirror_mod = modifier_ob.modifiers.new("mirror_mirror","MIRROR")
			else:
				mirror_ob = bpy.context.active_object         # last ob selected
				mirror_ob.select_set(state = False) # pop modifier_ob from sel_stack
				print("popped")

				modifier_ob = bpy.context.selected_objects[0]
				print("Modifier object:" +str(modifier_ob.name))

				print("mirror_ob",mirror_ob)
				print("modifier_ob",modifier_ob)

			# put mirror modifier on modifier_ob

				mirror_mod = modifier_ob.modifiers.new("mirror_mirror","MIRROR")

			# set mirror object to mirror_ob
				mirror_mod.mirror_object = mirror_ob

			if _operation == "MIRROR_X":
				mirror_mod.use_axis[0] = True
				mirror_mod.use_axis[1] = False
				mirror_mod.use_axis[2] = False
			elif _operation == "MIRROR_Y":
				mirror_mod.use_axis[0] = False
				mirror_mod.use_axis[1] = True
				mirror_mod.use_axis[2] = False
			elif _operation == "MIRROR_Z":
				mirror_mod.use_axis[0] = False
				mirror_mod.use_axis[1] = False
				mirror_mod.use_axis[2] = True

				#selection at the end -add back the deselected mirror modifier object
			# mirror_ob.select= 1
			# modifier_ob.select=1
			bpy.context.view_layer.objects.active = modifier_ob

			print("Selected" + str(modifier_ob)) # modifier ob is the active ob
		except:
				print("please select exactly two objects, the last one gets the modifier unless its not a mesh")

#------------------- OPERATOR CLASSES ------------------------------
# Mirror Tool

class AUTOMIRROR_OT_MirrorX(bpy.types.Operator):
	"""This adds an X mirror to the selected object"""
	bl_idname = "automirror.mirror_mirror_x"
	bl_label = "Mirror X"
	bl_description = "Mirror another object to an axis.\n First select the objects you want to mirror,\n Second select the objects you want to be axis and then execute.\n Set up a regular mirror if there is only one selected object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		Operation(context,"MIRROR_X")

		return {'FINISHED'}


class AUTOMIRROR_OT_MirrorY(bpy.types.Operator):
#     """This  adds a Y mirror modifier"""
	bl_idname = "automirror.mirror_mirror_y"
	bl_label = "Mirror Y"
	bl_description = "Mirror another object to an axis.\n First select the objects you want to mirror,\n Second select the objects you want to be axis and then execute.\n Set up a regular mirror if there is only one selected object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		Operation(context,"MIRROR_Y")
		return {'FINISHED'}

class AUTOMIRROR_OT_MirrorZ(bpy.types.Operator):
	"""This  add a Z mirror modifier"""
	bl_idname = "automirror.mirror_mirror_z"
	bl_label = "Mirror Z"
	bl_description = "Mirror another object to an axis.\n First select the objects you want to mirror,\n Second select the objects you want to be axis and then execute.\n Set up a regular mirror if there is only one selected object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		Operation(context,"MIRROR_Z")
		return {'FINISHED'}


def active_object_mirror_mirror(_obj):
	try:
		if bpy.context.active_object.modifiers["mirror_mirror"]:
			return True
	except:
		return False

def active_object_mirror(_obj):
	try:
		if bpy.context.active_object.modifiers["Mirror"]:
			return True
	except:
		return False


class AUTOMIRROR_OT_toggle_mirror(bpy.types.Operator):
	bl_idname = "automirror.toggle_mirror"
	bl_label = "Toggle Mirror"
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Switch on / off the Modifier named Mirror or mirror_mirror"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		actObj = bpy.context.active_object
		if active_object_mirror_mirror(actObj):
			if bpy.context.object.modifiers["mirror_mirror"].show_viewport == True:
				bpy.context.object.modifiers["mirror_mirror"].show_viewport = False
			else:
				bpy.context.object.modifiers["mirror_mirror"].show_viewport = True
		if active_object_mirror(actObj):
			if bpy.context.object.modifiers["Mirror"].show_viewport == True:
				bpy.context.object.modifiers["Mirror"].show_viewport = False
			else:
				bpy.context.object.modifiers["Mirror"].show_viewport = True
		return {'FINISHED'}



# Operator

class AUTOMIRROR_OT_AlignVertices(bpy.types.Operator):
	""" Automatically cut an object along an axis """
	bl_idname = "automirror.align_vertices"
	bl_label = "Align Vertices on 1 Axis"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj and obj.type == "MESH"

	def execute(self, context):
		bpy.ops.object.mode_set(mode = 'OBJECT')

		x1,y1,z1 = bpy.context.scene.cursor.location
		bpy.ops.view3d.snap_cursor_to_selected()

		x2,y2,z2 = bpy.context.scene.cursor.location

		bpy.context.scene.cursor.location[0], \
		bpy.context.scene.cursor.location[1], \
		bpy.context.scene.cursor.location[2]  = 0, 0, 0

		#Vertices coordinate to 0 (local coordinate, so on the origin)
		for vert in bpy.context.object.data.vertices:
			if vert.select:
				if bpy.context.scene.AutoMirror_axis == 'x':
					axis = 0
				elif bpy.context.scene.AutoMirror_axis == 'y':
					axis = 1
				elif bpy.context.scene.AutoMirror_axis == 'z':
					axis = 2
				vert.co[axis] = 0
		#
		bpy.context.scene.cursor.location = x2,y2,z2

		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

		bpy.context.scene.cursor.location = x1,y1,z1

		bpy.ops.object.mode_set(mode = 'EDIT')
		return {'FINISHED'}


class AUTOMIRROR_OT_AutoMirror(bpy.types.Operator):
	""" Automatically cut an object along an axis """
	bl_idname = "automirror.automirror"
	bl_label = "AutoMirror"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj and obj.type == "MESH"

	def get_local_axis_vector(self, context, X, Y, Z, orientation):
		loc = context.object.location
		bpy.ops.object.mode_set(mode="OBJECT") # Needed to avoid to translate vertices

		v1 = Vector((loc[0],loc[1],loc[2]))
		bpy.ops.transform.translate(value=(X*orientation, Y*orientation, Z*orientation),
										constraint_axis=((X==1), (Y==1), (Z==1)),
										orient_type='LOCAL')
		v2 = Vector((loc[0],loc[1],loc[2]))
		bpy.ops.transform.translate(value=(-X*orientation, -Y*orientation, -Z*orientation),
										constraint_axis=((X==1), (Y==1), (Z==1)),
										orient_type='LOCAL')

		bpy.ops.object.mode_set(mode="EDIT")
		return v2-v1

	def execute(self, context):
		X,Y,Z = 0,0,0
		if bpy.context.scene.AutoMirror_axis == 'x':
			X = 1
		elif bpy.context.scene.AutoMirror_axis == 'y':
			Y = 1
		elif bpy.context.scene.AutoMirror_axis == 'z':
			Z = 1

		current_mode = bpy.context.object.mode # Save the current mode

		if bpy.context.object.mode != "EDIT":
			bpy.ops.object.mode_set(mode="EDIT") # Go to edit mode
		bpy.ops.mesh.select_all(action='SELECT') # Select all the vertices
		if bpy.context.scene.AutoMirror_orientation == 'positive':
			orientation = 1
		else:
			orientation = -1
		cut_normal = self.get_local_axis_vector(context, X, Y, Z, orientation)

		# Cut the mesh
		bpy.ops.mesh.bisect(
				plane_co=(
				bpy.context.object.location[0],
				bpy.context.object.location[1],
				bpy.context.object.location[2]
				),
				plane_no=cut_normal,
				use_fill= False,
				clear_inner= bpy.context.scene.AutoMirror_cut,
				clear_outer= 0,
				threshold= bpy.context.scene.AutoMirror_threshold)

		bpy.ops.automirror.align_vertices() # Use to align the vertices on the origin, needed by the "threshold"

		if not bpy.context.scene.AutoMirror_toggle_edit:
			bpy.ops.object.mode_set(mode=current_mode) # Reload previous mode

		if bpy.context.scene.AutoMirror_cut:
			bpy.ops.object.modifier_add(type='MIRROR') # Add a mirror modifier
			bpy.context.object.modifiers[-1].use_axis[0] = X # Choose the axis to use, based on the cut's axis
			bpy.context.object.modifiers[-1].use_axis[1] = Y
			bpy.context.object.modifiers[-1].use_axis[2] = Z
			bpy.context.object.modifiers[-1].use_clip = context.scene.Use_Matcap
			bpy.context.object.modifiers[-1].show_on_cage = context.scene.AutoMirror_show_on_cage
			if bpy.context.scene.AutoMirror_apply_mirror:
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.modifier_apply(apply_as= 'DATA', modifier= bpy.context.object.modifiers[-1].name)
				if bpy.context.scene.AutoMirror_toggle_edit:
					bpy.ops.object.mode_set(mode='EDIT')
				else:
					bpy.ops.object.mode_set(mode=current_mode)

		return {'FINISHED'}


# Panel

class AUTOMIRROR_PT_AutoMirror_panel(Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Tools'
	bl_label = "Auto Mirror"
	bl_options = {'DEFAULT_CLOSED'}


	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)

		layout = self.layout
		if bpy.context.object and bpy.context.object.type == 'MESH':

			layout.operator("automirror.automirror")
			layout.prop(context.scene, "AutoMirror_axis", text="Mirror Axis", expand=True)
			layout.prop(context.scene, "AutoMirror_orientation", text="Orientation")
			layout.prop(context.scene, "AutoMirror_threshold", text="Threshold")
			layout.prop(context.scene, "AutoMirror_toggle_edit", text="Toggle Edit")
			box = layout.box()
			box.prop(context.scene, "AutoMirror_cut", text="Cut and Mirror")
			if bpy.context.scene.AutoMirror_cut:
				box.prop(context.scene, "Use_Matcap", text="Use Clip")
				box.prop(context.scene, "AutoMirror_show_on_cage", text="Editable")
				box.prop(context.scene, "AutoMirror_apply_mirror", text="Apply Mirror")

			# mirror mirror
			layout.separator()
			layout.label(text="Mirror Mirror:")
			layout.operator("automirror.mirror_mirror_x")
			layout.operator("automirror.mirror_mirror_y")
			layout.operator("automirror.mirror_mirror_z")
			layout.separator()
			layout.label(text="Toggle Mirror:")
			layout.operator("automirror.toggle_mirror")

		else:
			layout.label(icon="ERROR", text="No mesh selected")






# Properties

bpy.types.Scene.AutoMirror_axis = bpy.props.EnumProperty(
	items = [("x", "X", "", 1),("y", "Y", "", 2),("z", "Z", "", 3)],
	description="Axis used by the mirror modifier")

bpy.types.Scene.AutoMirror_orientation = bpy.props.EnumProperty(
	items = [("positive", "Positive", "", 1),("negative", "Negative", "", 2)],
	description="Choose the side along the axis of the editable part (+/- coordinates)")

bpy.types.Scene.AutoMirror_threshold = bpy.props.FloatProperty(
	default= 0.001, min= 0.001,
	description="Vertices closer than this distance are merged on the loopcut")

bpy.types.Scene.AutoMirror_toggle_edit = bpy.props.BoolProperty(
	default= False,
	description="If not in edit mode, change mode to edit")

bpy.types.Scene.AutoMirror_cut = bpy.props.BoolProperty(
	default= True,
	description="If enabeled, cut the mesh in two parts and mirror it. If not, just make a loopcut")

bpy.types.Scene.AutoMirror_clipping = bpy.props.BoolProperty(
	default=True)
bpy.types.Scene.Use_Matcap = bpy.props.BoolProperty(default=True,
description="Use clipping for the mirror modifier")

bpy.types.Scene.AutoMirror_show_on_cage = bpy.props.BoolProperty(
	default=False,
	description="Enable to edit the cage (it's the classical modifier's option)")

bpy.types.Scene.AutoMirror_apply_mirror = bpy.props.BoolProperty(

		description="Apply the mirror modifier (useful to symmetrise the mesh)")


# Add-ons Preferences Update Panel

# Define Panel classes for updating
panels = (
		AUTOMIRROR_PT_AutoMirror_panel,
		)


def update_panel(self, context):
	message = ": Updating Panel locations has failed"
	try:
		for panel in panels:
			if "bl_rna" in panel.__dict__:
				bpy.utils.unregister_class(panel)

		for panel in panels:
			panel.bl_category = context.preferences.addons[__name__].preferences.category
			bpy.utils.register_class(panel)

	except Exception as e:
		print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
		pass


class AUTOMIRROR_MT_AddonPreferences(AddonPreferences):
	# this must match the addon name, use '__package__'
	# when defining this in a submodule of a python package.
	bl_idname = __name__

	category: StringProperty(
			name="Tab Category",
			description="Choose a name for the category of the panel",
			default="Tools",
			update=update_panel
			)

	def draw(self, context):

		preferences = bpy.context.preferences
		addon_prefs = bpy.context.preferences.addons[__name__].preferences

		layout = self.layout

		row = layout.row()
		col = row.column()
		col.label(text="Tab Category:")
		col.prop(self, "category", text="")


		################################################
		# キーマップリスト
		box = layout.box()
		col = box.column()

		col.label(text="Keymap List:",icon="KEYINGSET")

		kc = bpy.context.window_manager.keyconfigs.addon
		for km, kmi in addon_keymaps:
			km = km.active()
			col.context_pointer_set("keymap", km)
			rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)



# define classes for registration
classes = (
	AUTOMIRROR_PT_AutoMirror_panel,
	AUTOMIRROR_OT_AutoMirror,
	AUTOMIRROR_OT_AlignVertices,
	AUTOMIRROR_OT_MirrorX,
	AUTOMIRROR_OT_MirrorY,
	AUTOMIRROR_OT_MirrorZ,
	AUTOMIRROR_OT_toggle_mirror,
	AUTOMIRROR_MT_AddonPreferences,

	)


addon_keymaps = []
# registering and menu integration
def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	update_panel(None, bpy.context)




	# handle the keymap
	wm = bpy.context.window_manager
	km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
	kmi = km.keymap_items.new("automirror.mirror_mirror_x", 'X', 'PRESS',alt=True, shift = True)
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.mirror_mirror_y", 'Y', 'PRESS', alt=True, shift = True)
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.mirror_mirror_z", 'Z', 'PRESS', alt=True, shift = True)
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.toggle_mirror", 'F', 'PRESS', alt=True, shift = True)
	addon_keymaps.append((km, kmi))





# unregistering and removing menus
def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


	################################################
	# キーマップの削除
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

if __name__ == "__main__":
	register()
