bl_info = {
	"name": "Mask Tools",
	"author": "Stanislav Blinov,Yigit Savtur,Bookyakuno (2.8Update)",
	"version": (0, 39,0),
	"blender": (2, 80,0),
	"location": "3d View > Properties shelf (N) > Sculpt",
	"description": "Tools for Converting Sculpt Masks to Vertex groups",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame"
}



import bpy

from .maskToVGroup import *
from .vgroupToMask import *
from .maskFromCavity import *
from .maskToAction import *


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


class MASKTOOLS_AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text="– Deselect", icon='MOD_MASK')
		row.label(text="LEFT MOUSE   : DoubleClick + Ctrl + Shift",icon="MOUSE_LMB")

		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text="– Invert", icon='PIVOT_MEDIAN')
		row.label(text="RIGHT MOUSE : DoubleClick + Ctrl + Shift",icon="MOUSE_RMB")

		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text="– Invert", icon='PIVOT_MEDIAN')
		row.label(text="LEFT MOUSE   : DoubleClick + Ctrl + alt",icon="MOUSE_LMB")

		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text="– Smooth", icon='MOD_SMOOTH')
		row.label(text="LEFT MOUSE   : DoubleClick + Shift",icon="MOUSE_LMB")

		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text="– Sharp", icon='IMAGE_ALPHA')
		row.label(text="RIGHT MOUSE : DoubleClick + Shift",icon="MOUSE_RMB")

		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text="– Fat", icon='KEY_HLT')
		row.label(text="LEFT MOUSE   : DoubleClick + Alt",icon="MOUSE_LMB")

		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text="– Less", icon='KEY_DEHLT')
		row.label(text="RIGHT MOUSE : DoubleClick + Alt",icon="MOUSE_RMB")
		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text="– Remove", icon='KEY_DEHLT')
		row.label(text="BACKSPACE")



	def execute(self,context):
		return {'FINISHED'}





class MaskToolsPanel(Panel):
	"""Creates a Mask Tool Box in the Viewport Tool Panel"""
	bl_category = "Sculpt"
	bl_idname = "MESH_OT_masktools"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = "Mask Tools"

	bpy.types.Screen.open_vgroup = bpy.props.BoolProperty(default=False, description = "Save Mask to VGroup")
	bpy.types.Screen.open_mask = bpy.props.BoolProperty(default=False, description = "Import VGroup to Mask")
	bpy.types.Screen.open_smoothsharp = bpy.props.BoolProperty(default=False, description = "Smooth/Sharp")
	bpy.types.Screen.open_fatless = bpy.props.BoolProperty(default=False, description = "Fat/Less")
	bpy.types.Screen.open_edgecavity = bpy.props.BoolProperty(default=False, description = "Edge/Cavity")
	bpy.types.Screen.open_modifier = bpy.props.BoolProperty(default=False, description = "Modifier")
	bpy.types.Screen.open_misc = bpy.props.BoolProperty(default=False, description = "Misc")
	bpy.types.Screen.open_all = bpy.props.BoolProperty(default=False, description = "Misc")


	def draw(self, context):
		layout = self.layout

		###############################################################
		###############################################################
		row = layout.row(align = True)
		row.operator("masktools.open_all", text="Open All",icon="TRIA_DOWN" if context.screen.open_all else "TRIA_RIGHT")







		###############################################################
		###############################################################
		row = layout.row(align = True)
		row.operator("mesh.masktovgroup", text = "", icon = 'GROUP_VERTEX', emboss=False)

		row.prop(context.screen, "open_vgroup",
			icon="TRIA_DOWN" if context.screen.open_vgroup else "TRIA_RIGHT",
			text="Save Vertex Group :", emboss=True)

		if context.screen.open_vgroup:
			box = layout.box()
			space = box.row()
			col = box.column(align=True)
			col.scale_y = 1.3
			col.operator("mesh.masktovgroup", text = "Mask to VGroup", icon = 'GROUP_VERTEX')
			row = box.row(align = True)
			row.operator("mesh.masktovgroup_append", text = "Add VGroup", icon = 'EXPORT')
			row.operator("mesh.masktovgroup_remove", text = "Difference VGroup", icon = 'UNLINKED')
			# row.scale_x = 0.5
			row.operator("object.vertex_group_remove",text="", icon = 'REMOVE')
			space = box.row()

		space = layout.row()

		###############################################################


		###############################################################
		###############################################################
		row = layout.row(align = True)
		row.operator("mesh.vgrouptomask_append", text = "", icon = 'MOD_MASK', emboss=False)

		row.prop(context.screen, "open_mask",
			icon="TRIA_DOWN" if context.screen.open_mask else "TRIA_RIGHT",
			text="Import Mask :", emboss=True)

		if context.screen.open_mask:
			box = layout.box()
			space = box.row()
			row = box.row(align = True)
			row.scale_y = 1.3
			row.operator("mesh.vgrouptomask_append", text = "Add", icon = 'IMPORT')
			row.operator("mesh.vgrouptomask_remove", text = "Difference", icon = 'UNLINKED')
			row = box.row()
			row.operator("mesh.vgrouptomask", text = "New Mask", icon='NONE')
			space = box.row()


		###############################################################
		###############################################################
		space = layout.row()
		row = layout.row(align = True)
		row.operator("mesh.mask_smooth_all", text = "", icon = 'MOD_SMOOTH', emboss=False)

		row.prop(context.screen, "open_smoothsharp",
			icon="TRIA_DOWN" if context.screen.open_smoothsharp else "TRIA_RIGHT",
			text="Mask Smooth/Sharp :", emboss=True)
		row.operator("mesh.mask_sharp", text = "", icon = 'IMAGE_ALPHA', emboss=False)

		if context.screen.open_smoothsharp:
			box = layout.box()
			space = box.row()
			row = box.row(align = True)
			row.scale_y = 1.3
			row.operator("mesh.mask_smooth_all", text = "Smooth", icon = 'MOD_SMOOTH')
			row.operator("mesh.mask_sharp", text = "Sharp", icon = 'IMAGE_ALPHA')

			row = box.row(align = False)
			row.prop(bpy.context.scene,"mask_smooth_strength", text = "Smooth Strength", icon='MOD_MASK',slider = True)
			space = box.row()


		space = layout.row()

		###############################################################
		###############################################################
		row = layout.row(align = True)
		row.operator("mesh.mask_fat", text = "", icon = 'KEY_HLT', emboss=False)

		row.prop(context.screen, "open_fatless",
			icon="TRIA_DOWN" if context.screen.open_fatless else "TRIA_RIGHT",
			text="Mask Fat/Less :", emboss=True)
		row.operator("mesh.mask_less", text = "", icon = 'KEY_DEHLT', emboss=False)

		if context.screen.open_fatless:
			box = layout.box()
			space = box.row()
			row = box.row(align = True)
			row.scale_y = 1.3
			row.operator("mesh.mask_fat", text = "Mask Fat", icon = 'KEY_HLT')
			row.operator("mesh.mask_less", text = "Mask Less", icon = 'KEY_DEHLT')

			row = box.row(align = True)
			row.prop(bpy.context.scene,"mask_fat_repeat", text = "Fat Repeat", icon='MOD_MASK',slider = True)
			row.prop(bpy.context.scene,"mask_less_repeat", text = "Less Repeat", icon='MOD_MASK',slider = True)
			space = box.row()


		###############################################################
		###############################################################
		space = layout.row()
		row = layout.row(align = True)
		row.operator("mesh.mask_from_edges", text = "", icon = 'EDGESEL', emboss=False)

		row.prop(context.screen, "open_edgecavity",
			icon="TRIA_DOWN" if context.screen.open_edgecavity else "TRIA_RIGHT",
			text="Mask Smooth/Sharp :", emboss=True)
		row.operator("mesh.mask_from_cavity", text = "", icon = 'STYLUS_PRESSURE', emboss=False)

		if context.screen.open_edgecavity:
			box = layout.box()
			space = box.row()
			row = box.row(align = True)
			row.scale_y = 1.3
			row.operator("mesh.mask_from_edges", text = "Mask by Edges", icon = 'EDGESEL')

			row = box.row(align = True)
			row.prop(bpy.context.scene,"mask_edge_angle", text = "Edge Angle",icon='MOD_MASK',slider = True)
			row.prop(bpy.context.scene,"mask_edge_strength", text = "Mask Strength", icon='MOD_MASK',slider = True)

			space = box.row()
			space = box.row()

			row = box.row(align = True)
			row.scale_y = 1.3
			row.operator("mesh.mask_from_cavity", text = "Mask by Cavity", icon = 'STYLUS_PRESSURE')

			row = box.row(align = True)
			row.prop(bpy.context.scene,"mask_cavity_angle", text = "Cavity Angle",icon='MOD_MASK',slider = True)
			row.prop(bpy.context.scene,"mask_cavity_strength", text = "Mask Strength", icon='MOD_MASK',slider = True)
			space = box.row()

		###############################################################
		###############################################################
		space = layout.row()
		row = layout.row(align = True)
		row.label(text = "", icon = 'MODIFIER_DATA')

		row.prop(context.screen, "open_modifier",
			icon="TRIA_DOWN" if context.screen.open_modifier else "TRIA_RIGHT",
			text="Modifier :", emboss=True)

		if context.screen.open_modifier:

			box = layout.box()
			space = box.row()
			row = box.row(align = True)
			row.operator("mesh.maskmod_displace",text="Displace", icon = 'MOD_DISPLACE')
			row.prop(bpy.context.scene,"maskmod_displace_apply",text="", icon='FILE_TICK')
			col = box.column(align=True)
			col.prop(bpy.context.scene,"maskmod_displace_strength", icon='MOD_MASK',slider = True)
			row = box.row(align = True)
			row.operator("mesh.maskmod_solidify",text="Solidify", icon = 'MOD_SOLIDIFY')
			row.prop(bpy.context.scene,"maskmod_solidify_apply",text="", icon='FILE_TICK')
			col = box.column(align=True)
			col.prop(bpy.context.scene,"maskmod_solidify_thickness", icon='MOD_SOLIDIFY',slider = True)
			row = box.row(align = True)
			row.operator("mesh.maskmod_smooth",text="Smooth", icon = 'MOD_SMOOTH')
			row.prop(bpy.context.scene,"maskmod_smooth_apply",text="", icon='FILE_TICK')
			col = box.column(align=True)
			col.prop(bpy.context.scene,"maskmod_smooth_strength", icon='MOD_MASK',slider = True)
			# space = layout.row()
			# split = box.split()
			# col = split.column(align=True)
			# col.scale_x = 1.5
			# col.operator("mesh.maskmod_smooth",text="Smooth", icon = 'MOD_SMOOTH')
			# col.prop(bpy.context.scene,"maskmod_smooth_strength", icon='MOD_MASK',slider = True)
			# space = box.row()




		###############################################################
		###############################################################
		space = layout.row()
		row = layout.row(align = True)
		row.label(text = "", icon = 'FORCE_VORTEX')

		row.prop(context.screen, "open_misc",
			icon="TRIA_DOWN" if context.screen.open_misc else "TRIA_RIGHT",
			text="Mask Misc :", emboss=True)

		if context.screen.open_misc:
			box = layout.box()
			space = box.row()
			col = box.column(align=True)
			col.operator("mesh.mask_polygon_remove", text = "Remove",icon="PANEL_CLOSE")
			col.operator("mesh.mask_duplicate", text = "Duplicate",icon="COMMUNITY")
			col.operator("mesh.mask_separate", text = "Separate",icon="MOD_EXPLODE")
			space = box.row()
			row = box.row(align = True)
			row.operator("masktools.mask_exturde", text = "Exturde",icon="ORIENTATION_NORMAL")
			row = box.row(align = True)
			row.prop(bpy.context.scene,"mask_exturde_volume", text = "")
			row.prop(bpy.context.scene,"mask_exturde_edgerelax", text = "", icon = "MOD_CURVE")
			col = box.column(align=True)

			col.operator("mesh.mask_sharp_thick", text = "Mask Sharp (Thick)", icon = 'NONE')
			col.prop(bpy.context.scene,"mask_sharp_thick", text = "Mask Sharp Thick Strength", icon='MOD_MASK',slider = True)
			space = box.row()
			split = box.split()
			col = split.column(align=True)
			col.label(text="Use LoopTools Addon!", icon='ERROR')
			col.operator("mesh.mask_outline_relax", text = "Outline Relax")
			col.prop(bpy.context.scene,"mask_outlinerelax_remove_doubles", text = "")







classes = {
MASKTOOLS_AddonPreferences,
MaskToolsPanel,

MaskToVertexGroup,
MaskToVertexGroupAppend,
MaskToVertexGroupRemove,

VertexGroupToMask,
VertexGroupToMaskAppend,
VertexGroupToMaskRemove,

MaskFromCavity,
MaskFromEdges,
MaskSmoothAll,
MaskFat,
MaskLess,
MaskSharp,
MaskSharpThick,
MaskLattice,
MaskArmture,
MaskPolygonRemove,


MaskModSmooth,
MaskModDisplace,
MaskModSolidify,
MaskDuplicate,
MaskSeparate,
MaskExturde,
MaskOpenall,
MaskOutlinerelax,
}

addon_keymaps = []




################################################################
# # # # # # # # プロパティの指定に必要なもの
def kmi_props_setattr(kmi_props, attr, value):
	try:
		setattr(kmi_props, attr, value)
	except AttributeError:
		print("Warning: property '%s' not found in keymap item '%s'" %
			  (attr, kmi_props.__class__.__name__))
	except Exception as e:
		print("Warning: %r" % e)

################################################################




def register():

	for cls in classes:
		bpy.utils.register_class(cls)





	wm = bpy.context.window_manager
	#kc = wm.keyconfigs.user      # for adding hotkeys independent from addon
	#km = kc.keymaps['Screen']
	kc = wm.keyconfigs.addon    # for hotkeys within an addon

	wm = bpy.context.window_manager
	keynew = wm.keyconfigs.addon.keymaps.new




	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('paint.mask_lasso_gesture', 'RIGHTMOUSE', 'PRESS',ctrl=True,shift=True)
	kmi_props_setattr(kmi.properties, 'mode','VALUE')
	kmi_props_setattr(kmi.properties, "value", 0.0)
	kmi.active = True
	addon_keymaps.append((km, kmi))

	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('paint.mask_lasso_gesture', 'LEFTMOUSE', 'PRESS',ctrl=True,shift=True)
	kmi_props_setattr(kmi.properties, 'mode','VALUE')
	kmi_props_setattr(kmi.properties, "value", 1.0)
	kmi.active = True
	addon_keymaps.append((km, kmi))


	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('paint.mask_flood_fill', 'RIGHTMOUSE', 'DOUBLE_CLICK', ctrl=True,shift=True)
	kmi_props_setattr(kmi.properties, "mode",'INVERT')
	kmi.active = True
	addon_keymaps.append((km, kmi))
	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('paint.mask_flood_fill', 'LEFTMOUSE', 'DOUBLE_CLICK', ctrl=True,alt=True)
	kmi_props_setattr(kmi.properties, "mode",'INVERT')
	kmi.active = True
	addon_keymaps.append((km, kmi))


	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('paint.mask_flood_fill', 'LEFTMOUSE', 'DOUBLE_CLICK', ctrl=True,shift=True)
	kmi_props_setattr(kmi.properties, 'mode','VALUE')
	kmi_props_setattr(kmi.properties, "value", 0.0)
	kmi.active = True
	addon_keymaps.append((km, kmi))


	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('mesh.mask_smooth_all', 'LEFTMOUSE', 'DOUBLE_CLICK', shift=True)
	kmi.active = True
	addon_keymaps.append((km, kmi))
	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('mesh.mask_sharp', 'RIGHTMOUSE', 'DOUBLE_CLICK', shift=True)
	kmi.active = True
	addon_keymaps.append((km, kmi))

	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('mesh.mask_fat', 'LEFTMOUSE', 'DOUBLE_CLICK', alt=True)
	kmi.active = True
	addon_keymaps.append((km, kmi))
	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('mesh.mask_less', 'RIGHTMOUSE', 'DOUBLE_CLICK', alt=True)
	kmi.active = True
	addon_keymaps.append((km, kmi))

	################################################################
	km = keynew('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('mesh.mask_polygon_remove', 'BACK_SPACE', 'PRESS')
	kmi.active = True
	addon_keymaps.append((km, kmi))




	# add_hotkey()

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()
	# remove_hotkey()


if __name__ == "__main__":
	register()
