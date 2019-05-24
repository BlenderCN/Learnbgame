#-------------------------------------------------------------------------------
#                    Extra Image List - Addon for Blender
#
# - Two display options (preview and plain list)
# - Button to clear all users for the selected image datablock
# - Double click on image in Node Editor opens the image in UV/Image Editor
#
# Version: 0.2
# Revised: 30.05.2017
# Author: Miki (meshlogic)
#-------------------------------------------------------------------------------
bl_info = {
	"name": "Extra Image List",
	"author": "Miki (meshlogic) - Rombout Versluijs (updated panel)",
	"category": "Learnbgame",
	"description": "An alternative image list for UV/Image Editor.",
	"location": "UV/Image Editor > Tools > Image List",
	"version": (0, 2, 2),
	"blender": (2, 78, 0),
	"wiki_url": "https://meshlogic.github.io/posts/blender/addons/extra-image-list/",
	"tracker_url": "https://github.com/schroef/Extra-Image-List",
}

import bpy
import os
from bpy.props import *
from bpy.types import Menu, Operator, Panel, UIList
from bpy.app.handlers import persistent


#-------------------------------------------------------------------------------
# UI PANEL - Extra Image List
#-------------------------------------------------------------------------------
class ExtraImageList_PT_ImagePreview(Panel):
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = "Image List"
	bl_label = "Extra Image List"

	def draw(self, context):
		layout = self.layout
		cs = context.scene
		props = cs.extra_image_list

		#--- Get the current image in the UV editor and list of all images
		img = context.space_data.image
		img_list = bpy.data.images

		#-----------------------------------------------------------------------
		# SETTINGS
		#-----------------------------------------------------------------------
		#--- List style buttons
		#--- Num. of rows & cols for image preview list
		row = layout.row(True)
		row.prop(props,"options", icon="PREFERENCES")
		if props.options:
			layout = layout.box()
			split = layout.split()

			colm = split.column()
			column = colm.column(True)
			column.label("Preview Style:")
			if props.style =='PREVIEW':
				column.label(" ")
				column.label(" ")
			column.label(" ")
			column.prop(props,"clean_enabled")

			colm = split.column()
			column = colm.column(True)
			column.prop(props, "style", text="")
			if props.style =='PREVIEW':
				column.prop(props, "rows")
				column.prop(props, "cols")
			column.label(" ")

			columr = colm.column(True)
			sub = columr
			sub.prop(props, "clear_mode", text="")
			sub.operator("extra_image_list.clear", text="Clear", icon='RADIO')
			sub.active = props.clean_enabled == True
			sub.enabled = props.clean_enabled == True

		layout = self.layout
		#row.prop(props, "style", expand=True)

		#-----------------------------------------------------------------------
		# PREVIEW List Style
		#-----------------------------------------------------------------------
		if props.style == 'PREVIEW':

			#--- Image preview list
			layout.template_ID_preview(
				context.space_data, "image",
				new = "image.new",
				open = "image.open",
				rows = props.rows, cols = props.cols
			)

		#-----------------------------------------------------------------------
		# LIST Style
		#-----------------------------------------------------------------------
		elif props.style == 'LIST':
			layout.row()
			layout.template_list(
				"extra_image_list.image_list", "",
				bpy.data, "images",
				props, "image_id",
				#rows = len(bpy.data.images)
			)

		#-----------------------------------------------------------------------
		# Image Source
		#-----------------------------------------------------------------------
		if img != None:

			#--- Image source
			row = layout.row()

			row.prop(img, "source")
			#row.label("Image Source:", icon='DISK_DRIVE')
			row = layout.row(True)

			if img.source == 'FILE':
				if img.packed_file:
					row.operator("image.unpack", text="", icon='PACKAGE')
				else:
					row.operator("image.pack", text="", icon='UGLYPACKAGE')

				row.prop(img, "filepath", text="")
				row.operator("image.reload", text="", icon='FILE_REFRESH')
			else:
				row.label(img.source + " : " + img.type)

			#--- Image size
			col = layout.column(True)
			row = layout.row(True)
			row.alignment = 'LEFT'

			if img.has_data:

				filename = os.path.basename(img.filepath)
				#--- Image name
				col.label(filename, icon='FILE_IMAGE')
				#--- Image size
				row.label("Size:", icon='TEXTURE')
				row.label("%d x %d x %db" % (img.size[0], img.size[1], img.depth))
			else:
				row.label("Can't load image file!", icon='ERROR')



		row = layout.row()
		split = row.split(percentage=0.5)
		#--- Navigation button PREV
		sub = split.column()
		sub.scale_y = 2
		sub.operator("extra_image_list.nav", text="", icon='BACK').dir = 'PREV'

		# Disable button for the first image or for no images
		sub.enabled = (img!=img_list[0] if (img!=None and len(img_list)>0) else False)

		#--- Navigation button NEXT
		sub = split.column()
		sub.scale_y = 2
		sub.operator("extra_image_list.nav", text="", icon='FORWARD').dir = 'NEXT'

		# Disable button for the last image or for no images
		sub.enabled = (img!=img_list[-1] if (img!=None and len(img_list)>0) else False)

#-------------------------------------------------------------------------------
# CUSTOM TEMPLATE_LIST FOR IMAGES
#-------------------------------------------------------------------------------
class ExtraImageList_UL(UIList):
	bl_idname = "extra_image_list.image_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

		# Image name and icon
		row = layout.row(True)
		row.prop(item, "name", text="", emboss=False, icon_value=icon)

		# Image status (fake user, zero users, packed file)
		row = row.row(True)
		row.alignment = 'RIGHT'

		if item.use_fake_user:
			row.label("F")
		else:
			if item.users == 0:
				row.label("0")

		if item.packed_file:
			#row.label(icon='PACKAGE')
			row.operator("image.unpack", text="", icon='PACKAGE', emboss=False)


#--- Update the active image when you select another item in the template_list
def update_active_image(self, context):
	try:
		id = bpy.context.scene.extra_image_list.image_id

		if id < len(bpy.data.images):
			img = bpy.data.images[id]
			bpy.context.space_data.image = img
	except:
		pass


#-------------------------------------------------------------------------------
# IMAGE NAVIGATION OPERATOR
#-------------------------------------------------------------------------------
class ExtraImageList_PT_Nav(Operator):
	bl_idname = "extra_image_list.nav"
	bl_label = "Nav"
	bl_description = "Navigation button"

	dir = EnumProperty(
		items = [
			('NEXT', "PREV", "PREV"),
			('PREV', "PREV", "PREV")
		],
		name = "dir",
		default = 'NEXT')

	def execute(self, context):

		# Get list of all images
		img_list = list(bpy.data.images)

		# Get index of the current image in UV editor, return if there is none image
		img = context.space_data.image
		if img in img_list:
			id = img_list.index(img)
		else:
			return{'FINISHED'}

		# Navigate
		if self.dir == 'NEXT':
			if id+1 < len(img_list):
				context.space_data.image = img_list[id+1]

		if self.dir == 'PREV':
			if id > 0:
				context.space_data.image = img_list[id-1]

		return{'FINISHED'}


#-------------------------------------------------------------------------------
# CLEAR IMAGE USERS OPERATOR
#-------------------------------------------------------------------------------
BAKE_TYPES = ('COMBINED', 'AO', 'SHADOW', 'NORMAL', 'UV', 'EMIT', 'ENVIRONMENT',
			  'DIFFUSE', 'GLOSSY', 'TRANSMISSION', 'SUBSURFACE', 'GRID',
			  'FULL', 'NORMALS', 'TEXTURE', 'DISPLACEMENT', 'DERIVATIVE', 'VERTEX_COLORS', 'EMIT',
			  'ALPHA', 'MIRROR_INTENSITY', 'MIRROR_COLOR', 'SPEC_INTENSITY', 'SPEC_COLOR')

class ExtraImageList_PT_Clear(Operator):
	bl_idname = "extra_image_list.clear"
	bl_label = "Clear Users"
	bl_description = """Use with caution !!\nClear all users for selected image datablocks.\nSo the image datablock can disappear after save and reload of the blend file."""

	def execute(self, context):
		cs = context.scene
		props = cs.extra_image_list

		#--- SELECTED IMAGE ----------------------------------------------------
		if props.clear_mode == 'SELECTED':

			# Get image in the editor
			img = context.space_data.image
			if img != None:
				img.user_clear()

		#--- NO USERS ----------------------------------------------------
		if props.clear_mode == 'NO USERS':

			for img in bpy.data.images:
				if img.users == 0:
					bpy.data.images.remove(img)

		#--- INVALID IMAGES ----------------------------------------------------
		elif props.clear_mode == 'INVALID':

			for img in bpy.data.images:

				# Load image in the editor
				context.space_data.image = img
				try:
					img.update()
				except:
					pass

				# Clear if loaded image has no data
				if img.has_data == False:
					img.user_clear()

		#--- GENERATED IMAGES --------------------------------------------------
		elif props.clear_mode == 'GENERATED':

			for img in bpy.data.images:
				if img.source == 'GENERATED':
					img.user_clear()

		#--- BAKED IMAGES ------------------------------------------------------
		elif props.clear_mode == 'BAKED':

			# Seek for images ending with "_baketype"
			bake_types = tuple(["_"+s for s in BAKE_TYPES])

			for img in bpy.data.images:

				# Get image name without extension
				name = img.name.upper()
				if len(name.split(".")[-1]) <= 3:
					name = name.rsplit(".", 1)[0]

				# Clear if name ends with a bake type
				if name.endswith(bake_types):
					img.user_clear()

		#--- ALL IMAGES --------------------------------------------------------
		elif props.clear_mode == 'ALL':
			for img in bpy.data.images:
				if img != None:
					img.user_clear()

		return{'FINISHED'}


#-------------------------------------------------------------------------------
# SHOW NODE IMAGE OPERATOR
# - Show node image in the IMAGE_EDITOR after double click on the node
#-------------------------------------------------------------------------------
IMG_NODES = ("ShaderNodeTexImage", "ShaderNodeTexEnvironment")

class ShowNodeImage_PT(Operator):
	bl_idname = "node.show_image"
	bl_label = "Show node image in the UV/Image Editor"

	def execute(self, context):
		node = context.active_node

		#--- Test if the active node is image type
		if node and node.bl_idname in IMG_NODES:

			# Find IMAGE_EDITOR
			for area in bpy.context.screen.areas:
				if area.type == 'IMAGE_EDITOR':
					space = area.spaces.active

					# Show image in IMAGE_EDITOR
					if node.image:
						space.image = node.image

		return {"FINISHED"}


#-------------------------------------------------------------------------------
# CUSTOM HANDLER (scene_update_post)
# - This handler is invoked after the scene updates
# - Keeps template_list synced with the active image
#-------------------------------------------------------------------------------
@persistent
def update_image_list(context):
	try:
		props = bpy.context.scene.extra_image_list

		# Try to find the active image in the IMAGE_EDITOR
		img = None
		for area in bpy.context.screen.areas:
			if area.type == 'IMAGE_EDITOR':
				img = area.spaces.active.image
				break

		# Update selected item in the template_list
		if img != None:
			id = bpy.data.images.find(img.name)
			if id != -1 and id != props.image_id:
				props.image_id = id
	except:
		pass


#-------------------------------------------------------------------------------
# CUSTOM SCENE PROPS
#-------------------------------------------------------------------------------
class ExtraImageList_Props(bpy.types.PropertyGroup):

	style = EnumProperty(
		items = [
			('PREVIEW', "Preview", "", 0),
			('LIST', "List", "", 1),
		],
		default = 'PREVIEW',
		name = "Style",
		description = "Image list style")

	clean_enabled = BoolProperty(
			default=False,
			name="Clean:",
			description="Enables option to clear scene of image textures. Be careful!")

	clear_mode = EnumProperty(
		items = [
			('NO USERS', "No Users", "Clears all images with no users", 0),
			('SELECTED', "Selected Image", "Clear the image selected in the editor", 1),
			('INVALID', "Invalid Images", "Clear invalid images (has_data == False)", 2),
			('GENERATED', "Generated Images", "Clear generated images (source == 'GENERATED')", 3),
			('BAKED', "Baked Images", "Clear images ending with a bake type e.g. '_COMBINED'", 4),
			('ALL', "All Images", "Clear all images", 4),
		],
		default = 'NO USERS',
		name = "Image Selection",
		description = "Select images to be cleared")

	rows = IntProperty(
		name = "Rows",
		description = "Num. of rows in the preview list",
		default = 4, min = 1, max = 15)

	cols = IntProperty(
		name = "Cols",
		description = "Num. of columns in the preview list",
		default = 8, min = 1, max = 30)

	# Index of the active image in the template_list
	image_id = IntProperty(
		default = 0,
		update = update_active_image)

	options = BoolProperty(
		 name="Options",
		 default=False)

	settings = BoolProperty(
		 name="Settings",
		 default=False)


#-------------------------------------------------------------------------------
# REGISTER/UNREGISTER ADDON CLASSES
#-------------------------------------------------------------------------------
keymaps = []

def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.extra_image_list = PointerProperty(type=ExtraImageList_Props)
	bpy.app.handlers.scene_update_post.append(update_image_list)

	# Add custom shortcut (image node double click)
	kc = bpy.context.window_manager.keyconfigs.addon
	km = kc.keymaps.new(name="Node Editor", space_type='NODE_EDITOR')
	kmi = km.keymap_items.new("node.show_image", 'ACTIONMOUSE', 'DOUBLE_CLICK')
	keymaps.append((km, kmi))

def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.extra_image_list
	bpy.app.handlers.scene_update_post.remove(update_image_list)

	# Remove custom shortcuts
	for km, kmi in keymaps:
		km.keymap_items.remove(kmi)
	keymaps.clear()

if __name__ == "__main__":
	register()

