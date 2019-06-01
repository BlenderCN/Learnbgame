######################################################################################################
# An simple add-on to auto cut in two and mirror an object                                           #
# Actualy partialy uncommented (see further version)                                                 #
# Author: Lapineige,Bookyakuno                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################


############# Add-on description (used by Blender)

bl_info = {
	"name": "Auto Mirror",
	"description": "Super fast cutting and mirroring for mesh",
	"author": "Lapineige, 2.8 update by Bookyakuno",
	"version": (2, 5,2),
	"blender": (2, 80, 0),
	"location": "View 3D > Toolbar > Tools tab > AutoMirror (panel)",
	"warning": "",
	"wiki_url": "http://www.le-terrier-de-lapineige.over-blog.com",
	"tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=18&p=7103#p7103",
	"category": "Learnbgame",
	}
#############

import bpy
from mathutils import Vector

import bmesh
import bpy
import collections
import mathutils
import math
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







class AUTOMIRROR_PT_preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	def draw(self, context):
		layout = self.layout

		preferences = context.preferences
		addon_prefs = preferences.addons[__name__].preferences

		#######################################################
		#######################################################

		col = layout.column(align=True)

		row = col.row(align=True)
		row.label(text="Link:", icon="URL")
		row = col.row(align=True)
		row.label(text="Once downloaded in gumroad, users can be notified of updates mail.")
		row = col.row(align=True)
		row.operator(
			"wm.url_open", text="gumroad",
			icon="URL").url = "https://gum.co/vgRSB"
		row = col.row(align=True)
		row = col.row(align=True)
		row.operator(
			"wm.url_open", text="lapineige blog",
			icon="URL").url = "http://www.le-terrier-de-lapineige.over-blog.com"
		row = col.row(align=True)
		row.label(text="")
		row = col.row(align=True)
		row.operator(
			"wm.url_open", text="Blender2.79 - lapineige github",
			icon="URL").url = "https://github.com/lapineige/Blender_add-ons/blob/master/AutoMirror/AutoMirror_V2-4.py"
		row = col.row(align=True)
		row.operator(
			"wm.url_open", text="Blender2.8 - Bookyakuno github",
			icon="URL").url = "https://github.com/bookyakuno/-Blender-/blob/master/AutoMirror_V2-5_2-8.py"
		row = col.row(align=True)
		row.label(text="")
		# row = col.row(align=True)
		# row.label(text="Description:")
		# row = col.row(align=True)
		# row.operator(
		# 	"wm.url_open", text="Description - BlenderArtists", icon="URL"
		# ).url = "https://blenderartists.org/t/simple-collection/1151341"
		# # row.operator(
		# # 	"wm.url_open", text="Description - Japanese", icon="URL"
		# # ).url = "http://bookyakuno.blog.fc2.com/blog-entry-56.html"
		# space = layout.row()










############### Operator

class AlignVertices(bpy.types.Operator):

	""" Automatically cut an object along an axis """

	bl_idname = "object.align_vertices"
	bl_label = "Align Vertices on 1 Axis"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		bpy.ops.object.mode_set(mode = 'OBJECT')

		x1,y1,z1 = bpy.context.scene.cursor.location
		bpy.ops.view3d.snap_cursor_to_selected()

		x2,y2,z2 = bpy.context.scene.cursor.location

		bpy.context.scene.cursor.location[0],bpy.context.scene.cursor.location[1],bpy.context.scene.cursor.location[2]  = 0,0,0

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

class AutoMirror(bpy.types.Operator):
	""" Automatically cut an object along an axis """
	bl_idname = "object.automirror"
	bl_label = "AutoMirror"
	bl_options = {'REGISTER'} # 'UNDO' ?

	@classmethod
	def poll(cls, context):
		return True

	def draw(self, context):
		layout = self.layout
		if bpy.context.object and bpy.context.object.type == 'MESH':
			layout.prop(context.scene, "AutoMirror_axis", text="Mirror axis")
			layout.prop(context.scene, "AutoMirror_orientation", text="Orientation")
			layout.prop(context.scene, "AutoMirror_threshold", text="Threshold")
			layout.prop(context.scene, "AutoMirror_toggle_edit", text="Toggle edit")
			layout.prop(context.scene, "AutoMirror_cut", text="Cut and mirror")
			if bpy.context.scene.AutoMirror_cut:
				layout.prop(context.scene, "AutoMirror_clipping", text="Clipping")
				layout.prop(context.scene, "AutoMirror_apply_mirror", text="Apply mirror")

		else:
			layout.label(icon="ERROR", text="No mesh selected")

	def get_local_axis_vector(self, context, X, Y, Z, orientation):
		loc = context.object.location
		bpy.ops.object.mode_set(mode="OBJECT") # Needed to avoid to translate vertices

		v1 = Vector((loc[0],loc[1],loc[2]))
		bpy.ops.transform.translate(value=(X*orientation, Y*orientation, Z*orientation), constraint_axis=((X==1), (Y==1), (Z==1)), orient_type='LOCAL')
		v2 = Vector((loc[0],loc[1],loc[2]))
		bpy.ops.transform.translate(value=(-X*orientation, -Y*orientation, -Z*orientation), constraint_axis=((X==1), (Y==1), (Z==1)), orient_type='LOCAL')

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

		bpy.ops.mesh.bisect(plane_co=(bpy.context.object.location[0], bpy.context.object.location[1], bpy.context.object.location[2]), plane_no=cut_normal, use_fill= False, clear_inner= bpy.context.scene.AutoMirror_cut, clear_outer= 0, threshold= bpy.context.scene.AutoMirror_threshold) # Cut the mesh

		bpy.ops.object.align_vertices() # Use to align the vertices on the origin, needed by the "threshold"

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




#################### Panel

# class tools_BisectMirror(bpy.types.Panel):
#     """ The AutoMirror panel on the toolbar tab 'Tools' """
#     bl_label = "Auto Mirror"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'TOOLS'
#     bl_category = "Tools"
#     bl_context = "mesh_edit"




class tools_BisectMirror(Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Tools'
	# bl_context = "mesh_edit"
	bl_label = "Auto Mirror"
	# bl_options = {'DEFAULT_CLOSED'}






	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		# layout.operator("object.booltool_auto_difference")
		#
		# if len(bpy.data.materials):
		#     for mat in bpy.data.materials:
		#         name = mat.name
		#         try:
		#             icon_val = layout.icon(mat)
		#         except:
		#             icon_val = 1
		#             print("WARNING [Mat Panel]: Could not get icon value for %s" % name)
		#
		#         op = col.operator("object.apply_material", text=name, icon_value=icon_val)
		#         op.mat_to_assign = name
		#     for mat in bpy.data.materials:
		#         name = mat.name
		#         try:
		#             icon_val = layout.icon(mat)
		#         except:
		#             icon_val = 1
		#             print("WARNING [Mat Panel]: Could not get icon value for %s" % name)
		#
		#         op = col.operator("object.apply_material", text=name, icon_value=icon_val)
		#         op.mat_to_assign = name
		# else:
		#     layout.label(text="No data materials")



		layout = self.layout
		if bpy.context.object and bpy.context.object.type == 'MESH':

			layout.operator("object.automirror")
			layout.prop(context.scene, "AutoMirror_axis", text="Mirror Axis", expand=True)
			layout.prop(context.scene, "AutoMirror_orientation", text="Orientation")
			layout.prop(context.scene, "AutoMirror_threshold", text="Threshold")
			layout.prop(context.scene, "AutoMirror_toggle_edit", text="Toggle Edit")
			layout.prop(context.scene, "AutoMirror_cut", text="Cut and Mirror")
			if bpy.context.scene.AutoMirror_cut:
				row = layout.row()
				row.prop(context.scene, "Use_Matcap", text="Use Clip")
				row.prop(context.scene, "AutoMirror_show_on_cage", text="Editable")
				layout.prop(context.scene, "AutoMirror_apply_mirror", text="Apply Mirror")

		else:
			layout.label(icon="ERROR", text="No mesh selected")



		# col = layout.column(align=True)
		# col.enabled = obs_len > 1
		# col.label("Auto Boolean:", icon="MODIFIER")
		# col.separator()
		# col.operator(OBJECT_OT_BoolTool_Auto_Difference.bl_idname, text='Difference', icon='PIVOT_ACTIVE')
		# col.operator(OBJECT_OT_BoolTool_Auto_Union.bl_idname, text='Union', icon='PIVOT_INDIVIDUAL')
		# col.operator(OBJECT_OT_BoolTool_Auto_Intersect.bl_idname, text='Intersect', icon='PIVOT_MEDIAN')






# define classes for registration
classes = (
	AUTOMIRROR_PT_preferences,
	tools_BisectMirror,
	AutoMirror,
	AlignVertices,

)



# registering and menu integration
def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	# bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(menu_func)
	# bpy.types.WindowManager.looptools = PointerProperty(type=LoopToolsProps)
	# update_panel(None, bpy.context)


# unregistering and removing menus
def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	# bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)
	# try:
		# del bpy.types.WindowManager.looptools
	# except Exception as e:
	#     print('unregister fail:\n', e)
	#     pass


if __name__ == "__main__":
	register()






# def register():
#     bpy.utils.register_class(tools_BisectMirror)
#     bpy.utils.register_class(AutoMirror)
#     bpy.utils.register_class(AlignVertices)
#
#
# def unregister():
#     bpy.utils.unregister_class(tools_BisectMirror)
#     bpy.utils.unregister_class(AutoMirror)
#     bpy.utils.unregister_class(AlignVertices)
#
#
# if __name__ == "__main__":
#     register()
