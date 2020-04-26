# -----------------------------------------------------------------------------
# Blender Tips - Addon for daily blender tips
# Developed by Patrick W. Crawford
#

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

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

# blender
import bpy

# system
import textwrap

# local
from . import conf
from . import BDT_updater_ops
from . import BDT_requests


# -----------------------------------------------------------------------------
# PANEL and OPERATORS
# -----------------------------------------------------------------------------


class BDT_get_tips(bpy.types.Operator):
	"""Call which will popup tips after fetching from online"""
	bl_label = "Get blender tips"
	bl_idname = "dailytips.get_tips"
	bl_description = "Fetch daily blender tips from online"
	{'REGISTER','UNDO'}

	def execute(self, context):

		res = BDT_requests.check_tip_async(self, context)
		self.report(*res)

		return {"FINISHED"}


class BDT_show_tips(bpy.types.Operator):
	"""Call which will popup tips in a floating window"""
	bl_label = "Blender Daily Tips"
	bl_idname = "dailytips.show_tips"
	bl_description = "Show the reteived daily blender tips"
	{'REGISTER','UNDO'}

	def invoke(self, context, event):
		width = 400 * bpy.context.user_preferences.system.pixel_size
		return context.window_manager.invoke_popup(self,width=width)

	def draw(self, context):
		layout = self.layout
		layout.label("Most recent tips as of "+conf.latest())
		addon_prefs = bpy.context.user_preferences.addons[__package__].preferences

		if conf.error != ():
			layout.label("AN error occured while fetching tips", icon="ERROR")
			layout.lable(conf.error)

		#if len(conf.tips)==0: unnecessary, covered above

		tipCol = layout.column()

		
		if addon_prefs.tips_database==True:
			box = tipCol #tipCol.row()
			# tip should come from:
			# tip = conf.jsn["subscribed_check_cache"]["database"][-1]
			# tip = {"title":"TEST",
			# 		"description":"THIS IS A DESCRIPTION of what to place in a thing for a tip that is daily even though this is a PERSISTENT non-daily one you know what I mean? it's all the time all the palce.",
			# 		"url":"http://theduckcow.com",
			# 		"img_id":None,
			# 		"date":"(No date provided)"
			# 		}
			# draw_tip(box,tip,style=0,wrap=80,lines=5)
			box.label("DAILY TIP DATABASE",icon="INFO")
			box.label("Feature not yet available")
			line = box.box()
			line.label("")
			line.scale_y = 0.02
		
		if addon_prefs.tips_yanal_sosak==True:
			box = tipCol #tipCol.row()
			if "yanal_sosak" in conf.jsn["subscribed_check_cache"]:
				tip = conf.jsn["subscribed_check_cache"]["yanal_sosak"]
				draw_tip(box,tip,style=0,wrap=60,lines=6,title_icon="OUTLINER_DATA_CAMERA")
				
			else:
				box.label("Did not find latest tip from Yanal Sosak")
			line = box.box()
			line.label("")
			line.scale_y = 0.02

		## COL1
		# icon left gallery view of tips
		# operator to open video below

		## COL2
		# preview text from video via API
		# Channel / "Tweet this!"

		# label: Change feed and popup frequency in settings
		# open settings button

	def execute(self, context):
		if conf.error != ():
			self.report(*conf.error)
		return {'FINISHED'}


class BDT_show_tip_error(bpy.types.Operator):
	"""Callback to show errors relating to the daily blender tip"""
	bl_label = "Blender Daily Tips"
	bl_idname = "dailytips.show_tip_error"

	def execute(self, context):
		print("Error message:")
		print(conf.error)
		if conf.error !=():
			self.report({"ERROR"},conf.error[1])
			# conf.error = None

		return {"FINISHED"}


class BDT_clear_tipcache(bpy.types.Operator):
	"""Callback to show errors relating to """
	bl_label = "Clear daily tip cache"
	bl_idname = "dailytips.clear_cache"
	bl_description = "Clear the cache of daily tips saved locally"

	def execute(self, context):

		conf.jsn_clear()
		conf.jsn_save()
		context.area.tag_redraw()

		return {"FINISHED"}


# -----------------------------------------------------------------------------
# PANELS AND POPUPS
# -----------------------------------------------------------------------------

# for callbacks e.g. from enum or value changes in popups
def redraw(self, context):
	context.area.tag_redraw()


def draw_tip(draw_element,tip,style=0,wrap=100,lines=9,title_icon=None):
	# different layouts for tips to procedurally draw
	# draw_element: passed in layout var for which everything here is a child
	# tip: the raw, self-contained tip information
	# wrap: length of word wrapping (description only)
	# lines: max number of layout rows/lines, including title/action buttons
	
	if style==0:
		#TEXT ONLY TIP
		row = draw_element.row()
		# LINES: 1x
		if title_icon==None:
			row.label(tip["title"]) 
		else:
			row.label(tip["title"],icon=title_icon)

		row = draw_element.row()
		col = draw_element.column()
		col.scale_y = 0.7

		# convert text to friendlier view
		re_encode = str(tip["description"].encode('utf-8').decode('ascii', 'ignore'))

		# new wordwrapping method, and then split by line
		label_lines = textwrap.fill(re_encode, wrap)
		label_lines = label_lines.split("\n")

		truncate = ""
		if len(label_lines)>lines-3:
			label_lines = label_lines[:lines-3]
			truncate = "--- description truncated ---"

		for ln in label_lines:
			col.label(ln) # LINESS: N-3x
		if truncate != "":
			suncol =col.row()
			suncol.alignment = 'CENTER'
			label_lines.append(truncate)

		row = draw_element.row(align=True) # LINES: 1x
		row.operator("wm.url_open","View this tip online").url=tip["url"]
		row.operator("wm.url_open","View source website").url=tip["website"]
	else:
		# other styles:
		# Left-side image (gallery view) + 
		# tag redraw?
		# https://www.blender.org/forum/viewtopic.php?t=21706
		return


def bdt_draw_preferences(self, context):
	"""Preferences draw function"""

	layout = self.layout
	toprow = layout.row()
	split = toprow.split(percentage=0.35)

	topcol = split.column()
	box = topcol.box()
	box.label("Tip Frequency")
	col = box.column()
	col.prop(self,"auto_show_tips")
	col = box.column(align=True)
	col.enabled = self.auto_show_tips
	col.prop(self,"auto_show_frequency",text="Frequency (days)")
	rw = col.row(align=True)
	rw.scale_y = 1.8
	# subcol = rw.column(align=True)
	if conf.async_progress == True:
		rw.enabled = False
		rw.operator("dailytips.get_tips",text="Grabbing tips...")
	elif conf.async_progress == None:
		rw.operator("dailytips.get_tips",text="Get tips")
	else:
		rw.operator("dailytips.show_tip_error",text="Error occured")
	#subcol = rw.column(align=True)
	rw = col.row(align=True)
	rw.operator("dailytips.clear_cache",text="Clear tip cache")
	rw = col.row(align=True)
	rw.label("Last check: "+conf.latest())
	rw.scale_y = 0.8

	# updater draw function
	topcol = split.column()
	BDT_updater_ops.update_settings_ui(self,context,topcol)

	# display tip section
	tipSection = layout.row()
	tipCol = layout.column()
	wrap = 100

	

	box = tipCol.box()
	box.prop(self,"tips_database","Enable Daily Tip Database feed")
	if self.tips_database==True:
		# tip should come from:
		# tip = conf.jsn["subscribed_check_cache"]["blendernation"][-1]
		tip = {"title":"TEST",
				"description":"This is a location where the tip description is provided",
				"url":"http://theduckcow.com",
				"img_id":None,
				"date":"(No date provided)",
				"website":"http://theduckcow.com/dev/blender/"
				}
		#draw_tip(box,tip,style=0,wrap=wrap)
		box.label("Feature not yet available",icon="ERROR")
	
	box = tipCol.box()
	box.prop(self,"tips_yanal_sosak","Enable Yanal Sosak's daily video tips")
	if self.tips_yanal_sosak==True:
		# tip should come from:
		if "yanal_sosak" in conf.jsn["subscribed_check_cache"]:
			tip = conf.jsn["subscribed_check_cache"]["yanal_sosak"]
			draw_tip(box,tip,style=0,wrap=wrap)
		else:
			box.label("No tips loaded from Yanal Sosak,")
			box.label("try pressing get tips above.")


def bdt_helptip_draw_append(self, context):
	"""Function to add operator to help dropdown of info window"""
	self.layout.operator("dailytips.get_tips")


def tip_autocheck_handler(scene):
	# Triggered by auto check
	try:
		bpy.app.handlers.scene_update_post.remove(tip_autocheck_handler)
	except:
		pass

	BDT_requests.check_tip_async_uidraw()


def addResponseHandler():
	# add the function call to the scene refresh handler
	bpy.app.handlers.scene_update_post.append(tipResponseHandler)
	if conf.verbose:print("Adding callback to handler")

def tipResponseHandler(scene):
	# when the scene updates, this handler will run to show the popup
	# Ensure to auto remove the handler:
	try:
		bpy.app.handlers.scene_update_post.remove(tipResponseHandler)
	except:
		pass

	if conf.error!=():
		bpy.ops.dailytips.show_tip_error('INVOKE_DEFAULT')
	else:
		bpy.ops.dailytips.show_tips('INVOKE_DEFAULT')


# -----------------------------------------------------------------------------
# PROPERTYS AND PREFRENCES
# -----------------------------------------------------------------------------

# scene-saved settings
# class btd_props_scene(bpy.types.PropertyGroup):
#
# 	x = bpy.props.BoolProperty(
# 		name = "x",
# 		description = "x",
# 		default = False)


class BDT_preferences(bpy.types.AddonPreferences):
	bl_idname = __package__
	
	auto_show_tips = bpy.props.BoolProperty(
		name = "Auto show tips",
		description = "If enabled, auto-check latest tips once a day at most",
		default = True,
		)
	auto_show_frequency = bpy.props.IntProperty(
		name='Tip frequency (days)',
		description = "Number of days between auto-checking for tips, select 1 for daily",
		default=1,
		min=1,
		)

	
	# tip subscription sources

	tips_database = bpy.props.BoolProperty(
		name = "Daily Tips Database",
		description = "Get the latest daily tip generated by the community",
		default = True,
		)
	tips_yanal_sosak = bpy.props.BoolProperty(
		name = "Yanal Sosak Daily Tips",
		description = "Daily tip videos from Yanal Sosak",
		default = True,
		)


	# addon updater preferences

	updater_intrval_days = bpy.props.IntProperty(
		name='Days',
		description = "Number of days between checking for updates",
		default=7,
		min=0,
		)

	auto_check_update = bpy.props.BoolProperty(
		name = "Auto-check for Update",
		description = "If enabled, auto-check for updates using an interval",
		default = False,
		)
	
	updater_intrval_months = bpy.props.IntProperty(
		name='Months',
		description = "Number of months between checking for updates",
		default=0,
		min=0
		)
	updater_intrval_days = bpy.props.IntProperty(
		name='Days',
		description = "Number of days between checking for updates",
		default=7,
		min=0,
		)
	updater_intrval_hours = bpy.props.IntProperty(
		name='Hours',
		description = "Number of hours between checking for updates",
		default=0,
		min=0,
		max=23
		)
	updater_intrval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description = "Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59
		)

	def draw(self, context):
		bdt_draw_preferences(self, context)


# -----------------------------------------------------------------------------
# REGISTER
# -----------------------------------------------------------------------------


def register():

	bpy.utils.register_class(BDT_get_tips)
	bpy.utils.register_class(BDT_show_tips)
	bpy.utils.register_class(BDT_preferences)
	bpy.utils.register_class(BDT_clear_tipcache)
	bpy.utils.register_class(BDT_show_tip_error)

	bpy.types.INFO_MT_help.append(bdt_helptip_draw_append)

	# for auto-checking purposes only
	# verify: only runs when epxlicitly pressing check-enabled,
	# does not run with just by opening
	if tip_autocheck_handler not in bpy.app.handlers.scene_update_post:
		bpy.app.handlers.scene_update_post.append(tip_autocheck_handler)
	


def unregister():

	bpy.utils.unregister_class(BDT_get_tips)
	bpy.utils.unregister_class(BDT_show_tips)
	bpy.utils.unregister_class(BDT_preferences)
	bpy.utils.unregister_class(BDT_clear_tipcache)
	bpy.utils.unregister_class(BDT_show_tip_error)

	bpy.types.INFO_MT_help.remove(bdt_helptip_draw_append)

	if tip_autocheck_handler in bpy.app.handlers.scene_update_post:
		bpy.app.handlers.scene_update_post.remove(tip_autocheck_handler)
	
	
