bl_info = {
	"name": "Photographer",
	"description": "Adds Exposure, White Balance, Resolution and Autofocus controls to your camera",
	"author": "Fabien 'chafouin' Christin, @fabienchristin", 
	"version": (2, 0, 0),
	"blender": (2, 80, 0),
	"location": "Properties Editor > Data > Camera",
	"support": "COMMUNITY",
	"category": "Learnbgame",
	}

import bpy
import os
import bgl
import math
from bpy.app.handlers import persistent
from bpy_extras import view3d_utils
from bpy.props import (StringProperty,
					   BoolProperty,
					   IntProperty,
					   FloatProperty,
					   EnumProperty,
					   PointerProperty,
					   )
from bpy.types import (Panel,
					   Operator,
					   PropertyGroup,
					   AddonPreferences,
					   )
from mathutils.bvhtree import BVHTree
import bmesh #addbmesh   <<ADD



# Global variables                       
min_color_temperature = 2000
max_color_temperature = 14000
default_color_temperature = 6500
min_color_tint = -100
max_color_tint = 100
default_tint = 0

# Creating Color Temperature to RGB look up tables from http://www.vendian.org/mncharity/dir3/blackbody/UnstableURLs/bbr_color.html
# Using 6500 as default white: purposefully changed 255,249,251 to 255,255,255
color_temperature_red = ((2000, 255),(2200,255),(2400,255),(2700,255),(3000,255),(3300,255),(3600,255),(3900,255),(4300,255),(5000,255),(6000,255),(6500, 255),(7000,247),(8000,229),(9000,217),(10000,207),(11000,200),(12000,195),(13000,120),(14000, 30))
color_temperature_green = ((2000,141),(2200,152),(2400,162),(2700,174),(3000,185),(3300,195),(3600,203),(3900,206),(4300,219),(5000,231),(6000,246),(6500, 255),(7000,243),(8000,233),(9000,225),(10000,218),(11000,213),(12000,209),(13000,200),(14000, 100))
color_temperature_blue = ((2000,11),(2200,41),(2400,60),(2700,84),(3000,105),(3300,124),(3600,141),(3900,159),(4300,175),(5000,204),(6000,237),(6500, 255),(7000,255),(8000,255),(9000,255),(10000,255),(11000,255),(12000,255),(13000,255),(14000,255))
temperature_ratio = ((23.1818,2000),(6.2195,2200),(4.25,2400),(3.0357,2700),(2.4286,3000),(2.0565,3300),(1.8085,3600),(1.6038,3900),(1.5839,4300),(1.25,5000),(1.0759,6000),(1,6500),(0.8980,8000),(0.851,9000),(0.8118,10000),(0.7843,11000),(0.7647,12000),(0.4706,13000),(0.1176,14000))
ev_lookup =  ["Starlight","Aurora Borealis","Half Moon","Full Moon","Full Moon in Snowscape","Dim ambient artifical light","Dim ambient artifical light","Distant view of lighted buildings","Total eclipse of Moon","Fireworks","Candle","Campfire","Home interior","Night Street","Office Lighting","Neon Signs","Skyline after Sunset","Sunset","Heavy Overcast","Bright Cloudy","Hazy Sun","Sunny","Bright Sun"]

class AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__
																									  
	exposure_mode_pref : bpy.props.EnumProperty(
		name = "Default Exposure Mode",
		description = "Choose the default Exposure Mode",
		items = [('EV','EV', ''),('MANUAL','Manual','')],
		default = 'EV',
	)
	
	shutter_speed_slider_pref : bpy.props.BoolProperty(
		name = "Shutter Speed / Angle",
		description = "Use Slider for Shutter Speed / Angle",
		default = False
	)
	
	aperture_slider_pref : bpy.props.BoolProperty(
		name = "Aperture",
		description = "Use Slider for Aperture",
		default = False
	)
	
	iso_slider_pref : bpy.props.BoolProperty(
		name = "ISO",
		description = "Use Slider for ISO setting",
		default = False
	)
			
	def draw(self, context):
			layout = self.layout
			wm = bpy.context.window_manager
			
			box = layout.box()
			percentage_columns = 0.4
			# Default Exposure mode
			split = box.split(factor = percentage_columns)
			split.label(text = "Default Exposure Mode :")
			row = split.row(align=True)
			row.prop(self, 'exposure_mode_pref', expand=True)
			
			# Use camera values presets or sliders
			row = box.row(align=True)
			split = row.split(factor = percentage_columns)
			split.label(text = "Use Sliders instead of real Camera values for :")
			col = split.column()
			row = col.row()
			row.prop(self, 'shutter_speed_slider_pref')
			row.prop(self, 'aperture_slider_pref')
			row.prop(self, 'iso_slider_pref')
			layout.label(text="Changing these default values will take effect after saving the User Preferences and restarting Blender.")
			
			layout.separator()
			
			# Useful links

			box = layout.box()
			row = box.row(align=True)
			row.label(text='Useful links : ')
			row.operator("wm.url_open", text="Blender Artists Forum post").url = "https://blenderartists.org/t/addon-photographer-camera-exposure-white-balance-and-autofocus/1101721"
			row.operator("wm.url_open", text="Video Tutorials").url = "https://www.youtube.com/playlist?list=PLDS3IanhbCIXERthzS7cWG1lnGQwQq5vB"
			
 
bpy.utils.register_class (AddonPreferences)
 
class InterpolatedArray(object):
  # An array-like object that provides interpolated values between set points.

	def __init__(self, points):
		self.points = sorted(points)

	def __getitem__(self, x):
		if x < self.points[0][0] or x > self.points[-1][0]:
			raise ValueError
		lower_point, upper_point = self._GetBoundingPoints(x)
		return self._Interpolate(x, lower_point, upper_point)

	def _GetBoundingPoints(self, x):
	#Get the lower/upper points that bound x.
		lower_point = None
		upper_point = self.points[0]
		for point  in self.points[1:]:
			lower_point = upper_point
			upper_point = point
			if x <= upper_point[0]:
				break
		return lower_point, upper_point

	def _Interpolate(self, x, lower_point, upper_point):
	#Interpolate a Y value for x given lower & upper bounding points.
		slope = (float(upper_point[1] - lower_point[1]) / (upper_point[0] - lower_point[0]))
		return lower_point[1] + (slope * (x - lower_point[0]))


class PHOTOGRAPHER_PT_PhotographerPanel(bpy.types.Panel):
	bl_idname = "CAMERA_PT_Photographer"
	bl_label = "Photographer"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"
	
	@classmethod    
	def poll(cls, context):
		# Add Panel properties to cameras
		return context.camera
		
	def draw(self, context):
		layout = self.layout
		settings = context.camera.photographer
		scene = bpy.context.scene
		
		# UI if camera isn't active
		if scene.camera != bpy.context.active_object:
			split = layout.split(0.5,align=True)
			split.label(text="This is not the Active Camera")
			col=split.column(align=True)
			col.alignment = 'RIGHT'
			col.operator("photographer.makecamactive", text="Make Active Camera")
			col.operator("photographer.selectactivecam", text="Select Active Camera")

		col_full = layout.column(align=True)
		# Enable UI if Camera is Active
		if scene.camera != bpy.context.active_object:
			col_full.enabled = False
			
		row = col_full.row(align=True)
		row.operator("photographer.updatesettings", text="Apply all Settings")     
		row = col_full.row(align=True)
		row.label(text='')
			
		row = col_full.row(align=True)
		split = row.split(factor=0.8, align=True)
		row = split.row(align=True)
		split2 = row.split(factor=0.43, align=True)
		split2.prop(settings, 'exposure_enabled', text='Exposure')
		col = split2.column(align=True)
		if not settings.exposure_enabled:
			col.enabled = False
		col.prop(settings, 'dof_enabled', text='Depth of Field')
		col = row.column(align=True)
		col.prop(settings, 'motionblur_enabled', text='Motion Blur')
		if not settings.exposure_enabled:
			col.enabled = False
		
		# EV info when using Manual Settings
		if settings.exposure_mode == 'MANUAL':
			ev = calc_exposure_value(self, context)
			ev = str(ev)
			col=split.column(align=True)
			col.alignment = 'RIGHT'
			col.label(text = "EV: " + ev)

		# Check if the Motion Blur is enabled in the Render Settings    
		if settings.motionblur_enabled and not scene.render.use_motion_blur:
			row = col_full.row()
			split = row.split(factor=0.7)
			split.label(text="Motion Blur is disabled in the Render Tab")
			split.operator("photographer.rendermotionblur", text="Enable MB")
			
		col_exposure = col_full.column(align=True)
		col_exposure.enabled = settings.exposure_enabled
 
		# Settings in EV Mode
		if settings.exposure_mode == 'EV':            
			split = col_exposure.split()
			col2 = split.column(align=True)
			row = col2.row(align=True)
			
			# Shutter Speed parameter
			if settings.motionblur_enabled:
				if settings.shutter_mode == 'SPEED':
					split=col2.split(factor=0.05,align=True)
					split.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')
					if not settings.shutter_speed_slider_enable:
						split=split.split(factor=0.95, align=True)
						split.prop(settings, 'shutter_speed_preset', text='')
					else:
						split=split.split(factor=0.95, align=True)
						split.prop(settings, 'shutter_speed', slider=True)
					split.operator("photographer.setshutterangle",icon="TIME", text="")
				if settings.shutter_mode == 'ANGLE':
					split=col2.split(factor=0.05,align=True)
					split.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')
					if not settings.shutter_speed_slider_enable:
						split=split.split(factor=0.95, align=True)
						split.prop(settings, 'shutter_angle_preset', text='')
					else:
						split=split.split(factor=0.95, align=True)
						split.prop(settings, 'shutter_angle', slider=True)
					split.operator("photographer.setshutterspeed",icon="PREVIEW_RANGE", text="")
			
			# Aperture parameter
			if settings.dof_enabled:
				split=col2.split(factor=0.05,align=True)
				split.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')
				if not settings.aperture_slider_enable:
					split.prop(settings, 'aperture_preset', text='')
				else:
					split.prop(settings, 'aperture', slider=True, text='Aperture F-stop / Depth of Field only')
			
			col2.prop(settings, 'ev', slider=True)

		else:
			split = col_exposure.split()
			col2 = split.column(align=True)
			row = col2.row(align=True)
			
			# Shutter Speed parameter
			if settings.shutter_mode == 'SPEED':
				split=row.split(factor=0.05,align=True)
				split.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')
				if not settings.shutter_speed_slider_enable:
					split=split.split(factor=0.95, align=True)
					split.prop(settings, 'shutter_speed_preset', text='')
				else:
					split=split.split(factor=0.95, align=True)
					split.prop(settings, 'shutter_speed', slider=True)
				split.operator("photographer.setshutterangle",icon="TIME", text="")
			if settings.shutter_mode == 'ANGLE':
				split=col2.split(factor=0.05,align=True)
				split.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')
				if not settings.shutter_speed_slider_enable:
					split=split.split(factor=0.95, align=True)
					split.prop(settings, 'shutter_angle_preset', text='')
				else:
					split=split.split(factor=0.95, align=True)
					split.prop(settings, 'shutter_angle', slider=True)
				split.operator("photographer.setshutterspeed",icon="PREVIEW_RANGE", text="")
			
			# Aperture parameter
			split=col2.split(factor=0.05,align=True)
			split.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')
			if not settings.aperture_slider_enable:
				split.prop(settings, 'aperture_preset', text='')
			else:
				split.prop(settings, 'aperture', slider=True, text='Aperture F-stop / Depth of Field only')
			
			# ISO parameter
			split=col2.split(factor=0.05,align=True)
			split.prop(settings,'iso_slider_enable', icon='SETTINGS', text='')
			if not settings.iso_slider_enable:
				split.prop(settings, 'iso_preset', text='')
			else:
				split.prop(settings, 'iso', slider=True)

		row = col_exposure.row(align=True)
		row.prop(settings, 'exposure_mode',expand=True)
		
		row = col_exposure.row(align=True)
		ev_guide = update_exposure_guide(self, context)
		col=row.column(align=True)
		framerate_guide = "FPS : " + str(round(scene.render.fps/scene.render.fps_base,2))
		if settings.shutter_mode == 'ANGLE':
			shutter_speed_guide = "   -   " + "Shutter Speed : 1/" + str(int(settings.shutter_speed)) + " s"
			framerate_guide += shutter_speed_guide
		if settings.shutter_mode == 'SPEED':
			shutter_angle_guide = "   -   " + "Shutter Angle : " + str(round(settings.shutter_angle,1))
			framerate_guide += shutter_angle_guide
		col.label(text=framerate_guide)
		col=row.column(align=True)
		col.alignment = 'RIGHT'
		col.label(text = ev_guide)
		
		# If White Balance is disabled, then disable sliders
		row = col_full.row()
		row.label(text='')
		row = col_full.row()
		row.prop(context.scene.view_settings, 'use_curve_mapping', text='White Balance')
		
		col_wb = col_full.column(align=True)
		col_wb.enabled = context.scene.view_settings.use_curve_mapping
		row = col_wb.row(align=True)
		split = row.split(factor=0.85, align=True)
		split.prop(settings, "color_temperature", slider=True)
		split.prop(settings, "preview_color", text='')
		
		row = col_wb.row(align=True)
		split = row.split(factor=0.85, align=True)
		split.prop(settings, "tint", slider=True)
		split.prop(settings, "preview_color_tint", text='')

		row = col_wb.row(align=True)
		split = row.split(factor=0.5, align=True)
		split.operator("white_balance.picker",text='Picker', icon='EYEDROPPER')
		split.operator("white_balance.reset", text='Reset')

		row = col_full.row()
		row.label(text='')
		row = col_full.row()
		row.prop(settings, 'resolution_enabled', text='Resolution')
		
		col_res = col_full.column(align=True)
		col_res.enabled = settings.resolution_enabled
		row = col_res.row(align=True)
		row.prop(settings, 'resolution_mode',expand=True)
		row = col_res.row(align=True)
		
		if settings.resolution_mode == 'CUSTOM':
			row.prop(settings, "resolution_x", text='')
			row.prop(settings, "resolution_y", text='')
			row.prop(context.scene.render, "resolution_percentage", text='')
			row = col_res.row(align=True)
			row.prop(settings, 'resolution_rotation',expand=True)

		if not settings.resolution_mode == 'CUSTOM':
			row.prop(settings, "longedge")
			row.prop(context.scene.render, "resolution_percentage", text='')
			if not settings.resolution_mode == '11':
				row = col_res.row(align=True)
				row.prop(settings, 'resolution_rotation',expand=True)

		row = col_res.row(align=True)
		row.alignment='CENTER'

		resolution_x = str(int(context.scene.render.resolution_x * context.scene.render.resolution_percentage/100))
		resolution_y = str(int(context.scene.render.resolution_y * context.scene.render.resolution_percentage/100))
		row.label(text = resolution_x + " x " + resolution_y + " pixels")
		

def get_addon_preferences():
	addon_name = os.path.basename(os.path.dirname(os.path.abspath(__file__).split("utils")[0]))
	user_preferences = bpy.context.preferences
	addon_prefs = user_preferences.addons[addon_name].preferences 
	
	return addon_prefs        
		
#Camera Exposure functions ##############################################################

# Update Toggle
def update_settings(self, context):
	
	if context.scene.camera:
		settings = context.scene.camera.data.photographer

		if settings.exposure_enabled:
			update_aperture(self, context)
			update_shutter_speed(self, context)
			update_iso(self, context)
			update_shutter_angle(self, context)
		
			if context.scene.camera.data.dof_distance== 0:
				context.scene.camera.data.dof_distance = 3
			if context.scene.render.engine == 'CYCLES' and settings.dof_enabled:
				context.scene.camera.data.cycles.aperture_type = 'FSTOP'                
						
			if settings.resolution_enabled:
				update_resolution(self,context)
			
			if context.scene.view_settings.use_curve_mapping:
				settings.color_temperature = settings.color_temperature
				settings.tint = settings.tint

def update_exposure_guide(self, context):
	EV = calc_exposure_value(self,context)
	if EV <= 16 and EV >= -6:       
		EV = int(EV+6)
		ev_guide = ev_lookup[EV]
	else:
		ev_guide = "Out of realistic range"
	return ev_guide
	   
def calc_exposure_value(self, context):
	settings = context.scene.camera.data.photographer
	if settings.exposure_mode == 'EV':
		EV = settings.ev
	else:
		
		if not settings.aperture_slider_enable:
			aperture = float(settings.aperture_preset)
		else:
			aperture = settings.aperture
		A = aperture
		
		if not settings.shutter_speed_slider_enable and settings.shutter_mode == 'SPEED':
			shutter_speed = float(settings.shutter_speed_preset)
		else:
			shutter_speed = settings.shutter_speed
		S = 1 / shutter_speed
		
		if not settings.iso_slider_enable:
			iso = float(settings.iso_preset)
		else:
			iso = settings.iso
		I = iso
		
		EV = math.log((100*(A*A)/(I*S)), 2)
		EV = round(EV, 2)
	return EV

# Update EV
def update_ev(self, context):
	EV = calc_exposure_value(self,context)
		
	bl_exposure = -EV+8
	context.scene.view_settings.exposure = bl_exposure
	
# Update Aperture
def update_aperture(self, context):
	settings = context.scene.camera.data.photographer
	# if context.scene.render.engine == 'CYCLES' and settings.dof_enabled :
	if settings.dof_enabled :
		if context.scene.camera == bpy.context.active_object:
			if not settings.aperture_slider_enable:
				context.object.data.cycles.aperture_fstop = float(settings.aperture_preset) * context.scene.unit_settings.scale_length
				context.object.data.gpu_dof.fstop = float(settings.aperture_preset)
			else:
				context.object.data.cycles.aperture_fstop = settings.aperture * context.scene.unit_settings.scale_length
				context.object.data.gpu_dof.fstop = settings.aperture
	
	update_ev(self, context)
	
# Update Shutter Speed
def update_shutter_speed(self, context):
	scene = bpy.context.scene
	settings = context.scene.camera.data.photographer
	if settings.shutter_mode == 'SPEED':
		fps = scene.render.fps / scene.render.fps_base
		if not settings.shutter_speed_slider_enable:
			settings.shutter_angle = (fps * 360) / float(settings.shutter_speed_preset)
		else:
			settings.shutter_angle = (fps * 360) / settings.shutter_speed
		if settings.motionblur_enabled:
				scene.render.motion_blur_shutter = settings.shutter_angle / 360
				# Matching Eevee to Cycles
				scene.eevee.motion_blur_shutter = scene.render.motion_blur_shutter
			
	if settings.exposure_mode == 'MANUAL':
		update_ev(self, context)


def update_shutter_angle(self, context):
	scene = bpy.context.scene
	settings = context.scene.camera.data.photographer
	if settings.shutter_mode == 'ANGLE':
		fps = scene.render.fps / scene.render.fps_base
		
		if not settings.shutter_speed_slider_enable:
			shutter_angle = float(settings.shutter_angle_preset)
		else:
			shutter_angle = settings.shutter_angle
	
		settings.shutter_speed = 1 / (shutter_angle / 360) * fps
		
		if settings.motionblur_enabled:
			if scene.render.engine == 'Cycles':
				scene.render.motion_blur_shutter = shutter_angle / 360
				# Matching Eevee to Cycles 
				scene.eevee.motion_blur_shutter = scene.render.motion_blur_shutter

	if settings.exposure_mode == 'MANUAL':
		update_ev(self, context)

# Update ISO
def update_iso(self, context):
	update_ev(self, context)


# Update Resolution    
def update_resolution(self,context):
	settings = context.scene.camera.data.photographer
		
	resolution_x = 1920
	resolution_x = 1080
		
	if settings.resolution_mode == 'CUSTOM':
		resolution_x = settings.resolution_x
		resolution_y = settings.resolution_y
	
	if settings.resolution_mode == '11':
		resolution_x = settings.longedge
		resolution_y = resolution_x
		
	if settings.resolution_mode == '32':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/3)*2
		
	if settings.resolution_mode == '43':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/4)*3
		
	if settings.resolution_mode == '67':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/7)*6
	
	if settings.resolution_mode == '169':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/16)*9
		
	if settings.resolution_mode == '169':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/16)*9
		
	if settings.resolution_mode == '2351':
		resolution_x = settings.longedge
		resolution_y = settings.longedge/2.35

	if settings.resolution_rotation == 'LANDSCAPE': 
		context.scene.render.resolution_x = resolution_x
		context.scene.render.resolution_y = resolution_y
	
	if settings.resolution_rotation == 'PORTRAIT': 
		context.scene.render.resolution_x = resolution_y
		context.scene.render.resolution_y = resolution_x
			
		
			
		
#White Balance functions ##############################################################
		
def convert_temperature_to_RGB_table(color_temperature):

	# Interpolate Tables
	table_red = InterpolatedArray(color_temperature_red)
	table_green = InterpolatedArray(color_temperature_green)
	table_blue = InterpolatedArray(color_temperature_blue)
	
	# Convert Temperature to RGB using the look up tables
	red = table_red[color_temperature]
	green = table_green[color_temperature]
	blue = table_blue[color_temperature]
	
	return (red / 255, green / 255, blue / 255)
	
def convert_RGB_to_temperature_table(red, blue):
	
	table_ratio = InterpolatedArray(temperature_ratio)
	
	# Min and Max ratios from the table
	maxratio = 23.1818
	minratio = 0.1176
	
	# Make sure to not divide by 0
	if blue == 0:
		ratio = minratio
	else: ratio = red / blue
	
	#Clamping ratio to avoid looking outside of the table
	ratio = maxratio if ratio > maxratio else minratio if ratio < minratio else ratio

	color_temperature = table_ratio[ratio]
	
	return (color_temperature)

def convert_tint_to_color_preview(color_tint):
	red = 1.0
	green = 1.0
	blue = 1.0
  
	if color_tint < 0:
		red = red + color_tint / 150 # Dividing with 150. Not an accurate match to the actual Tint math, purposefully different so the preview color is pleasing
		blue = blue + color_tint / 150
		
	if color_tint > 0:
		green = green - color_tint / 150
		
	return red, green, blue  

# sRGB to linear function
def s2lin(x):
	a = 0.055
	if x <= 0.04045 :
		y = x * (1.0 / 12.92)
	else:
		y = pow( (x + a) * (1.0 / (1 + a)), 2.4)
	return y    
	
def convert_RBG_to_whitebalance(picked_color):
	photographer = bpy.context.camera.photographer
	#Need to convert picked color to linear
	red = s2lin(picked_color[0])
	green = s2lin(picked_color[1])
	blue = s2lin(picked_color[2])
	
	average = (red + blue) / 2
	
	# Calculating Curves values
	red_mult = red / average
	green_mult = green / average
	blue_mult = blue / average

	# # Accurate multiplier to test accuracy of color temperature conversion
	# bpy.context.scene.view_settings.curve_mapping.white_level[0] = red_mult
	# bpy.context.scene.view_settings.curve_mapping.white_level[1] = green_mult
	# bpy.context.scene.view_settings.curve_mapping.white_level[2] = blue_mult
		
	# Convert Curve value to Tint
	if green_mult < 1 :
		photographer.tint = (green_mult - 1) * 200 # Reverse Tint Math
	else:
		photographer.tint = (green_mult - 1) * 50 # Reverse Tint Math
  
	# Convert Curve value to Temperature
	photographer.color_temperature = convert_RGB_to_temperature_table(red_mult,blue_mult)
	
def calc_color_temperature_color(temperature):
	return convert_temperature_to_RGB_table(temperature)

def calc_tint_preview_color(tint):
	return convert_tint_to_color_preview(tint)   

def get_color_temperature_color_preview(self):
	def_k = calc_color_temperature_color(default_color_temperature)
	# inverting
	def_k = (def_k[2],def_k[1],def_k[0])
	return self.get('preview_color', def_k)  

def set_color_temperature_color(self, value):
	photographer = bpy.context.scene.camera.data.photographer
	context = bpy.context
	
	# Convert Temperature to Color
	white_balance_color = calc_color_temperature_color(photographer.color_temperature)
	# Set preview color in the UI - inverting red and blue channels
	self['preview_color'] = (white_balance_color[2],white_balance_color[1],white_balance_color[0])
	
	if context.scene.camera == context.active_object:
		# Calculate Curves values from color - ignoring green which is set by the Tint
		red = white_balance_color[0]
		blue = white_balance_color[2]
		average = (red + blue) / 2

		# Apply values to Red and Blue white levels
		context.scene.view_settings.curve_mapping.white_level[0] = red / average
		context.scene.view_settings.curve_mapping.white_level[2] = blue / average
		
		#Little trick to update viewport as Color Management Curves don't update automatically
		exposure = bpy.context.scene.view_settings.exposure
		bpy.context.scene.view_settings.exposure = exposure

def get_tint_preview_color(self):
	def_tint = calc_tint_preview_color(default_tint)
	return self.get('preview_color_tint', def_tint)

def set_tint_color(self, value):
	context = bpy.context
	photographer = context.scene.camera.data.photographer

	# Set preview color in the UI
	self['preview_color_tint'] = calc_tint_preview_color(photographer.tint)

	if photographer.tint < 0:
		tint_curve_mult = photographer.tint / 200 + 1 # Diving by 200 instead of 100 to avoid green level to go lower than 0.5. Gives more precision to the slider.
	else:
		tint_curve_mult = photographer.tint / 50 + 1  # Diving by 50 to avoid green level to go higher than 3. Gives more precision to the slider.
			
	# Apply value to Green white level
	bpy.context.scene.view_settings.curve_mapping.white_level[1] = tint_curve_mult
	
	#Little trick to update viewport as Color Management Curves don't update automatically
	exposure = bpy.context.scene.view_settings.exposure
	bpy.context.scene.view_settings.exposure = exposure

def set_picked_white_balance(picked_color):
	convert_RBG_to_whitebalance(picked_color)

			
# Photo Mode parameters ####################################################    
class PhotographerSettings(bpy.types.PropertyGroup):
	# bl_idname = __name__

	# UI Properties
	# initRefresh = bpy.props.BoolProperty(
		# name = "initRefresh",
		# description = "Is the automatic Panel refresh working?",
		# default = False
	# )
	exposure_enabled : bpy.props.BoolProperty(
		name = "Enable Exposure Controls",
		default = True,
		update = update_settings
	)
	dof_enabled : bpy.props.BoolProperty(
		name = "Enable Depth of Field control",
		description = "Depth of Field will be controlled by the Aperture Value",
		default = True,
		update = update_settings
	)
	motionblur_enabled : bpy.props.BoolProperty(
		name = "Enable Motion Blur control",
		description = "Motion Blur will be controlled by the Shutter Speed / Shutter Angle values",
		default = False,
		update = update_settings
	)
	
	# Exposure properties
	exposure_mode : bpy.props.EnumProperty(
		name = "Exposure Mode",
		description = "Choose the Exposure Mode",
		items = [('EV','EV', ''),('MANUAL','Manual','')],
		default = bpy.context.preferences.addons[__name__].preferences.exposure_mode_pref if bpy.context.preferences.addons[__name__].preferences.exposure_mode_pref else 'EV',
		update = update_settings
		# default = 'EV',
	)
	ev : bpy.props.FloatProperty(
		name = "Exposure Value",
		description = "Exposure Value: look at the Chart",
		soft_min = -6,
		soft_max = 16,
		step = 1,
		precision = 2,
		default = 10.61,
		update = update_ev
	)
	
	# Shutter Speed properties
	shutter_mode : bpy.props.EnumProperty(
		name = "Shutter Mode",
		description = "Choose the Shutter Mode",
		items = [('SPEED','Shutter Speed',''),('ANGLE','Shutter Angle', '')],
		default = 'SPEED',
		update = update_settings
	)
	shutter_speed : bpy.props.FloatProperty(
		name = "Shutter Speed 1/X second",
		description = "Shutter Speed - controls the amount of Motion Blur",
		soft_min = 0.1,
		soft_max = 1000,
		precision = 2,
		default = 50,
		update = update_shutter_speed
	)
	shutter_speed_slider_enable : bpy.props.BoolProperty(
		name = "Shutter Speed Slider",
		description = "Enable Shutter Speed slider instead of preset list",
		default = bpy.context.preferences.addons[__name__].preferences.shutter_speed_slider_pref if bpy.context.preferences.addons[__name__].preferences.shutter_speed_slider_pref else False,
		update = update_shutter_speed
		# default = False,
	)
	shutter_speed_preset : bpy.props.EnumProperty(
		name = "Shutter Speed",
		description = "Camera Shutter Speed",
		items = [('0.033','30 "',''),('0.04','25 "',''),('0.05','20 "',''),('0.066','15 "',''),('0.077','13 "',''),('0.1','10 "',''),('0.125','8 "',''),('0.1666','6 "',''),('0.2','5 "',''),('0.25','4 "',''),('0.3125','3.2 "',''),('0.4','2.5 "',''),
		('0.5','2 "',''),('0.625','1.6 "',''),('0.769','1.3 "',''),('1','1 "',''),('1.25','0.8 "',''),('1.666','0.6 "',''),('2','0.5 "',''),('2.5','0.4 "',''),('3.333','0.3 "',''),('4','1 / 4 s',''),('5','1 / 5 s',''),('6','1 / 6 s',''),
		('8','1 / 8 s',''),('10','1 / 10 s',''),('13','1 / 13 s',''),('15','1 / 15 s',''),('20','1 / 20 s',''),('25','1 / 25 s',''),('30','1 / 30 s',''),('40','1 / 40 s',''),('50','1 / 50 s',''),('60','1 / 60 s',''),('80','1 / 80 s',''),
		('100','1 / 100 s',''),('125','1 / 125 s',''),('160','1 / 160 s',''),('200','1 / 200 s',''),('250','1 / 250 s',''),('320','1 / 320 s',''),('400','1 / 400 s',''),('500','1 / 500 s',''),('640','1 / 640 s',''),('800','1 / 800 s',''),
		('1000','1 / 1000 s',''),('1250','1 / 1250 s',''),('1600','1 / 1600 s',''),('2000','1 / 2000 s',''),('2500','1 / 2500 s',''),('3200','1 / 3200 s',''),('4000','1 / 4000 s',''),('5000','1 / 5000 s',''),('6400','1 / 6400 s',''),('8000','1 / 8000 s', '')],
		default = '50',
		update = update_shutter_speed
	)
	
	# Shutter Angle properties
	shutter_angle : bpy.props.FloatProperty(
		name = "Shutter Angle",
		description = "Shutter Angle in degrees - controls the Shutter Speed and amount of Motion Blur",
		soft_min = 1,
		soft_max = 360,
		precision = 1,
		default = 180,
		update = update_shutter_angle
	)
	shutter_angle_preset : bpy.props.EnumProperty(
		name = "Shutter Angle",
		description = "Camera Shutter Angle",
		items = [('8.6','8.6 degree',''),('11','11 degree',''),('22.5','22.5 degree',''),('45','45 degree',''),('72','72 degree',''),('90','90 degree',''),('144','144 degree',''),('172.8','172.8 degree',''),('180','180 degree',''),
		('270','270 degree',''),('360','360 degree','')],
		default = '180',
		update = update_shutter_angle
	)
	
	# Aperture properties    
	aperture : bpy.props.FloatProperty(
		name = "Aperture F-stop",
		description = "Lens aperture - controls the Depth of Field",
		soft_min = 0.5,
		soft_max = 32,
		precision = 1,
		default = 5.6,
		update = update_aperture
	)
	aperture_slider_enable : bpy.props.BoolProperty(
		name = "Aperture Slider",
		description = "Enable Aperture slider instead of preset list",
		default = bpy.context.preferences.addons[__name__].preferences.aperture_slider_pref,
		update = update_aperture
	)
	aperture_preset : bpy.props.EnumProperty(
		name = "Lens Aperture Presets",
		description = "Lens Aperture",
		items = [('0.95','f / 0.95',''),('1.2','f / 1.2',''),('1.4','f / 1.4',''),('1.8','f / 1.8',''),('2.0','f / 2.0',''),('2.4','f / 2.4',''),('2.8','f / 2.8',''),('3.5','f / 3.5',''),('4.0','f / 4.0',''),('4.9','f / 4.9',''),('5.6','f / 5.6',''),
		('6.7','f / 6.7',''),('8.0','f / 8.0',''),('9.3','f / 9.3',''),('11','f / 11',''),('13','f / 13',''),('16','f / 16',''),('20','f / 20',''),('22','f / 22','')],
		default = '5.6',
		update = update_aperture
	)
	
	# ISO properties
	iso : bpy.props.IntProperty(
		name = "ISO",
		description = "ISO setting",
		soft_min = 50,
		soft_max = 12800,
		default = 100,
		update = update_iso
	)
	iso_slider_enable : bpy.props.BoolProperty(
		name = "Iso Slider",
		description = "Enable ISO setting slider instead of preset list",
		default = bpy.context.preferences.addons[__name__].preferences.iso_slider_pref,
		update = update_iso
	)   
	iso_preset : bpy.props.EnumProperty(
		name = "Iso Presets",
		description = "Camera Sensitivity",
		items = [('100','ISO 100',''),('125','ISO 125',''),('160','ISO 160',''),('200','ISO 200',''),('250','ISO 250',''),('320','ISO 320',''),('400','ISO 400',''),('500','ISO 500',''),('640','ISO 640',''),('800','ISO 800',''),('1000','ISO 1000',''),('1250','ISO 1250',''),
		('1600','ISO 1600',''),('2000','ISO 2000',''),('2500','ISO 2500',''),('3200','ISO 3200',''),('4000','ISO 4000',''),('5000','ISO 5000',''),('6400','ISO 6400',''),('8000','ISO 8000',''),('10000','ISO 10000',''),('12800','ISO 12800',''),('16000','ISO 16000',''),
		('20000','ISO 20000',''),('25600','ISO 25600',''),('32000','ISO 32000',''),('40000','ISO 40000',''),('51200','ISO 51200','')],
		default = '100',
		update = update_iso
	)
	
	# White Balance properties
	color_temperature : bpy.props.IntProperty(
		name="Color Temperature", description="Color Temperature (Kelvin)",
		min=min_color_temperature, max=max_color_temperature, default=default_color_temperature,
		update=set_color_temperature_color
	)
	preview_color : bpy.props.FloatVectorProperty(
		name='Preview Color', description="Color Temperature preview color",
		subtype='COLOR', min=0.0, max=1.0, size=3,
		get=get_color_temperature_color_preview,
		set=set_color_temperature_color
	)
	tint : bpy.props.IntProperty(
		name="Tint", description="Green or Magenta cast",
		min=min_color_tint, max=max_color_tint, default=default_tint,
		update=set_tint_color
	)
	preview_color_tint : bpy.props.FloatVectorProperty(
		name="Preview Color Tint", description="Tint preview color",
		subtype='COLOR', min=0.0, max=1.0, size=3,
		get=get_tint_preview_color,
		set=set_tint_color
	)
	
	# Resolution properties
	resolution_enabled : bpy.props.BoolProperty(
		name = "Enable Exposure Controls",
		default = False,
		update = update_resolution
	)
	resolution_mode : bpy.props.EnumProperty(
		name = "Resolution Mode",
		description = "Choose Custom Resolutions or Ratio presets",
		items = [('CUSTOM','Custom',''),('11','1:1', ''),('32','3:2', ''),('43','4:3', ''),('67','6:7', ''),('169','16:9', ''),('2351','2.35:1', '')],
		update = update_resolution
	)
	resolution_x : bpy.props.IntProperty(
		name="X", description="Horizontal Resolution",
		min=0, default=1920,subtype='PIXEL',
		update=update_resolution
	)
	resolution_y : bpy.props.IntProperty(
		name="Y", description="Vertical Resolution",
		min=0, default=1080, subtype='PIXEL',
		update=update_resolution
	)
	longedge : bpy.props.FloatProperty(
		name="Long Edge", description="Long Edge Resolution",
		min=0, default=1920, subtype='PIXEL',
		update=update_resolution
	)
	resolution_rotation : bpy.props.EnumProperty(
		name = "Resolution Rotation",
		description = "Choose the rotation of the camera",
		items = [('LANDSCAPE','Landscape',''),('PORTRAIT','Portrait', '')],
		update=update_resolution
	)
	
	# AF-C property
	af_continous_enabled : bpy.props.BoolProperty(
		name = "AF-C",
		description = "Autofocus Continuous",
		default = False
	)
	
class PHOTOGRAPHER_OT_SetShutterAngle(bpy.types.Operator):
	bl_idname = "photographer.setshutterangle"
	bl_label = "Switch to Shutter Angle"
	bl_description = "Switch to Shutter Angle"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		context.camera.photographer.shutter_mode = 'ANGLE'
		update_settings(self,context)
		return{'FINISHED'}

class PHOTOGRAPHER_OT_SetShutterSpeed(bpy.types.Operator):
	bl_idname = "photographer.setshutterspeed"
	bl_label = "Switch to Shutter Speed"
	bl_description = "Switch to Shutter Speed"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		context.camera.photographer.shutter_mode = 'SPEED'
		update_settings(self,context)        
		return{'FINISHED'}        
		
class PHOTOGRAPHER_OT_RenderMotionBlur(bpy.types.Operator):
	bl_idname = "photographer.rendermotionblur"
	bl_label = "Enable Motion Blur render"
	bl_description = "Enable Motion Blur in the Render Settings"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		context.scene.render.use_motion_blur = True
		context.scene.eevee.use_motion_blur = True
		return{'FINISHED'}
	
class PHOTOGRAPHER_OT_WBReset(bpy.types.Operator):
	bl_idname = "white_balance.reset"
	bl_label = "Reset White Balance"
	bl_description = "Reset White Balance"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		context.camera.photographer.color_temperature = default_color_temperature
		context.camera.photographer.tint = default_tint
		return{'FINISHED'} 

class PHOTOGRAPHER_OT_MakeCamActive(bpy.types.Operator):
	bl_idname = "photographer.makecamactive"
	bl_label = "Make Camera Active"
	bl_description = "Make this Camera the active camera in the Scene"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		bpy.context.scene.camera = bpy.context.active_object
		update_settings(self,context)
		return{'FINISHED'} 

class PHOTOGRAPHER_OT_UpdateSettings(bpy.types.Operator):
	bl_idname = "photographer.updatesettings"
	bl_label = "Update Settings"
	bl_description = "If you changed DoF, Framerate, Resolution or Curves settings outside of the Photographer addon, reapply the settings to make sure they are up to date"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		update_settings(self,context)
		return{'FINISHED'} 
		
class PHOTOGRAPHER_OT_SelectActiveCam(bpy.types.Operator):
	bl_idname = "photographer.selectactivecam"
	bl_label = "Select Active Camera"
	bl_description = "Select the Active Camera in the Scene"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		bpy.context.scene.objects.active = bpy.data.objects[bpy.context.scene.camera.name]
		return{'FINISHED'} 
		
class PHOTOGRAPHER_OT_WBPicker(bpy.types.Operator):
	bl_idname = "white_balance.picker"
	bl_label = "Pick White Balance"
	bl_description = "Pick a grey area in the 3D view to adjust the White Balance"
	bl_options = {'REGISTER', 'UNDO'}
 
	# Create stored values for cancelling
	stored_color_temperature = 6500
	stored_tint = 0
	stored_cm_display_device = "sRGB"
	stored_cm_view_transform = "Filmic"
	
	stored_cm_look = "None"
	
	def modal(self, context, event):
		context.area.tag_redraw()
 
		# Allow navigation for Blender and Maya shortcuts
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
			return {'PASS_THROUGH'}
			
		if event.type == 'LEFTMOUSE':
			# Reset White Balance to pick raw image, not an already white balanced one
			context.camera.photographer.color_temperature = default_color_temperature
			context.camera.photographer.tint = default_tint
			# Disabling color management to be able to convert picked color easily
			try: 
				context.scene.display_settings.display_device = "sRGB"
			except:
				context.scene.display_settings.display_device = "sRGB / BT.709"
			try:
				context.scene.view_settings.view_transform = "Default"
			except:
				context.scene.view_settings.view_transform = "sRGB EOTF"
				
			if context.scene.view_settings.view_transform == "sRGB EOTF":
				context.scene.view_settings.look = "None"

			# Picking color when releasing left mouse button
			if event.value == 'RELEASE' and not self.record:

				self.record = True
				self.mouse_position=(event.mouse_x, event.mouse_y)
				# Restore Mouse Cursor from Eyedropper Icon
				if self.cursor_set: context.window.cursor_modal_restore()
				
				buf = bgl.Buffer(bgl.GL_FLOAT, [1, 3])
				x,y = self.mouse_position
				
				# Sampling pixels under the mouse when released
				bgl.glReadPixels(x, y, 1,1 , bgl.GL_RGB, bgl.GL_FLOAT, buf)
				rgb = buf[0]
				# Calculate and apply Color Temperature and Tint
				set_picked_white_balance(rgb)
				
				# Restore Color Management Settings
				context.scene.display_settings.display_device = self.stored_cm_display_device 
				context.scene.view_settings.view_transform = self.stored_cm_view_transform
				context.scene.view_settings.look = self.stored_cm_look
		
				return {'FINISHED'}

		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			# Restore previous settings if cancelled
			context.camera.photographer.color_temperature = self.stored_color_temperature
			context.camera.photographer.tint = self.stored_tint
			
			# Restore Color Management Settings
			context.scene.display_settings.display_device = self.stored_cm_display_device 
			context.scene.view_settings.view_transform = self.stored_cm_view_transform
			context.scene.view_settings.look = self.stored_cm_look
		
			# Restore Mouse Cursor from Eyedropper Icon
			if self.cursor_set:
				context.window.cursor_modal_restore()
			return {'CANCELLED'}
			
		return {'RUNNING_MODAL'}
		
	def invoke(self, context, event):
			args = (self, context)
			context.window_manager.modal_handler_add(self)
			
			# Set Cursor to Eyedropper icon
			context.window.cursor_modal_set('EYEDROPPER')
			self.cursor_set = True
			self.record = False
			
			# Store current white balance settings in case of cancelling
			self.stored_color_temperature = context.camera.photographer.color_temperature
			self.stored_tint = context.camera.photographer.tint
			
			self.stored_cm_display_device = context.scene.display_settings.display_device
			self.stored_cm_view_transform = context.scene.view_settings.view_transform
			self.stored_cm_look = context.scene.view_settings.look
		
			context.area.tag_redraw()
			return {'RUNNING_MODAL'}
 

# Focus picker 
def focus_raycast(context, event, continuous):

	if continuous:
		for window in bpy.context.window_manager.windows:
			for area in window.screen.areas:
				if area.type == 'VIEW_3D':
					scene = bpy.context.scene
					region = area.regions[4]
					rv3d = area.spaces.active.region_3d
					
					obj = scene.camera
					cam = obj.data
					frame = cam.view_frame(scene = scene)

					# move from object-space into world-space 
					frame = [obj.matrix_world @ v for v in frame]

					# move into pixelspace
					from bpy_extras.view3d_utils import location_3d_to_region_2d
					frame_px = [location_3d_to_region_2d(region, rv3d, v) for v in frame]
					
					if frame_px != [None, None, None, None]:
						center = (frame_px[0] - frame_px[2])/2 + frame_px[2]
					else:
						center = [960,540] # Center of full HD resolution - better than throwing an error but will need to be fixed
					coord = center
		
	else:
		scene = context.scene
		region = context.region
		rv3d = context.region_data
		coord = event.mouse_region_x, event.mouse_region_y

	# Get the ray from the viewport and mouse
	view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
	ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

	ray_target = ray_origin + view_vector

	def visible_objects_and_duplis():
		"""Loop over (object, matrix) pairs (mesh only)"""

		for obj in context.visible_objects:
			if obj.type == 'MESH':
				yield (obj, obj.matrix_world.copy())

			# if obj.dupli_type != 'NONE':
			# 	obj.dupli_list_create(scene)
			# 	for dob in obj.dupli_list:
			# 		obj_dupli = dob.object
			# 		if obj_dupli.type == 'MESH':
			# 			yield (obj_dupli, dob.matrix.copy())

			# obj.dupli_list_clear()

	def obj_ray_cast(obj, matrix):
		"""Wrapper for ray casting that moves the ray into object space"""
		# bpy.context.scene.update()

		# get the ray relative to the object
		matrix_inv = matrix.inverted()
		ray_origin_obj = matrix_inv @ ray_origin
		ray_target_obj = matrix_inv @ ray_target
		ray_direction_obj = ray_target_obj - ray_origin_obj

		# cast the ray
		# success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
		bm = bmesh.new()
		bm.from_mesh(obj.data)
		bvhTreeObject = BVHTree.FromBMesh(bm)
		location, normal, face_index, distance = bvhTreeObject.ray_cast(ray_origin_obj, ray_direction_obj)

		if location is not None:
			return location, normal, face_index
		else:
			return None, None, None

	# cast rays and find the closest object
	best_length= -1.0
	raycast_lengths=[]

	for obj, matrix in visible_objects_and_duplis():
		if obj.type == 'MESH':
			# bpy.context.scene.update()
			hit, normal, face_index = obj_ray_cast(obj, matrix)
			if hit is not None:
				hit_world = matrix @ hit
				length = (hit_world - ray_origin).length
				raycast_lengths.append(length)
				
	if len(raycast_lengths) != 0:
		context.scene.camera.data.dof_distance = min(raycast_lengths)
	else:
		context.scene.camera.data.dof_distance = 100

class PHOTOGRAPHER_OT_FocusSingle(bpy.types.Operator):
	"""Autofocus Single: Click where you want to focus"""
	bl_idname = "photographer.focus_single"
	bl_label = "Photographer Focus Single"

	def modal(self, context, event):
		# Allow navigation for Blender and Maya shortcuts
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
			return {'PASS_THROUGH'}
		
		# Disable AF-C if using AF-C
		if context.scene.camera.data.photographer.af_continous_enabled:
			context.scene.camera.data.photographer.af_continous_enabled = False
		
		# Enter focus picker
		if event.type == 'LEFTMOUSE':
			if event.value == 'RELEASE':
				if context.space_data.type == 'VIEW_3D':
					try:
						focus_raycast(context, event, False)
					except:
						self.report({'ERROR'}, "An error occured during the raycast")
					context.window.cursor_modal_restore()                 
					return {'FINISHED'}
				else:
					self.report({'WARNING'}, "Active space must be a View3d")
					if self.cursor_set: context.window.cursor_modal_restore()
				return {'CANCELLED'}
		
		# Cancel Modal with RightClick and ESC
		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			if self.cursor_set:
				context.window.cursor_modal_restore()
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}
		  
	def invoke(self, context, event):
		self.cursor_set = True
		context.window.cursor_modal_set('EYEDROPPER')
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

# class PHOTOGRAPHER_OT_ModalTimerApplySettings(bpy.types.Operator):
	# bl_idname = "photographer.apply_settings"
	# bl_label = "Apply camera settings every seconds"

	# _timer = None

	# @classmethod
	# def running(cls, context):
		# return (cls._timer)
	
	# # @classmethod
	# # def poll(cls, context):
		# # return context.scene.camera == context.active_object
	
	# def modal(self, context, event):
		# # if event.type in {'RIGHTMOUSE', 'ESC'}:
			# # self.cancel(context)
			# # return {'CANCELLED'}

		# if event.type == 'TIMER':
			# update_settings(self,context)  

		# return {'PASS_THROUGH'}

	# def execute(self, context):
		# # print(type(self))
		# # if context.scene.camera == context.active_object:
		# wm = context.window_manager
		# type(self)._timer = wm.event_timer_add(3, window = context.window)
		# wm.modal_handler_add(self)
		# return {'RUNNING_MODAL'}

	# # def cancel(self, context):
		# # wm = context.window_manager
		# # wm.event_timer_remove(type(self)._timer)

# # Trick to add handler and start the modal timer to reapply panel settings        
# @persistent
# def apply_settings_handler2(scene):
	# bpy.ops.photographer.apply_settings()
	# bpy.app.handlers.frame_change_post.remove(apply_settings_handler2)
 
# @persistent
# def apply_settings_handler(scene):
	# bpy.app.handlers.frame_change_post.append(apply_settings_handler2)
	# bpy.context.scene.frame_current=bpy.context.scene.frame_current
	# bpy.app.handlers.depsgraph_update_post.remove(apply_settings_handler)        

# Focus continuous handler function    
@persistent
def focus_continuous(scene):
	context = bpy.context
	# Do not AF-C if active camera is not a camera
	if context.scene.camera:
		if context.scene.camera.type == 'CAMERA':
			settings = context.scene.camera.data.photographer
			if settings.af_continous_enabled:
				focus_raycast(context, None, True)
		
def focus_single_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	if context.scene.camera:
		if context.scene.camera.type == 'CAMERA':
			self.layout.operator("photographer.focus_single", text="AF-S", icon='RESTRICT_RENDER_OFF')
		
def focus_continuous_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	if context.scene.camera:
		if context.scene.camera.type == 'CAMERA':
			settings = context.scene.camera.data.photographer
			self.layout.prop(settings, "af_continous_enabled", text="AF-C", icon='RESTRICT_RENDER_OFF')
		
def focus_distance_header(self, context):
	if context.scene.camera:
		if context.scene.camera.type == 'CAMERA' and context.scene.camera.data.photographer.af_continous_enabled == False:
			dof_distance = str(round(context.scene.camera.data.dof_distance*context.scene.unit_settings.scale_length,2))
			if not context.scene.unit_settings.system == 'NONE':
				dof_distance = dof_distance + "m"
			self.layout.label(text=dof_distance)


classes = ( 
	PHOTOGRAPHER_PT_PhotographerPanel,
	PhotographerSettings,
	PHOTOGRAPHER_OT_SetShutterAngle,
	PHOTOGRAPHER_OT_SetShutterSpeed,
	PHOTOGRAPHER_OT_RenderMotionBlur,
	PHOTOGRAPHER_OT_WBReset,
	PHOTOGRAPHER_OT_MakeCamActive,
	PHOTOGRAPHER_OT_UpdateSettings,
	PHOTOGRAPHER_OT_SelectActiveCam,
	PHOTOGRAPHER_OT_WBPicker,
	PHOTOGRAPHER_OT_FocusSingle,
	# PHOTOGRAPHER_OT_ModalTimerApplySettings
)

def register():
	from bpy.utils import register_class

	for cls in classes:
		print(cls)
		register_class(cls)

	bpy.types.Camera.photographer = PointerProperty(type=PhotographerSettings)
	bpy.app.handlers.depsgraph_update_post.append(focus_continuous)
	# bpy.app.handlers.depsgraph_update_post.append(apply_settings_handler)
	bpy.types.VIEW3D_HT_header.append(focus_single_button)
	bpy.types.VIEW3D_HT_header.append(focus_continuous_button)
	bpy.types.VIEW3D_HT_header.append(focus_distance_header)
	

def unregister():
	from bpy.utils import unregister_class

	bpy.app.handlers.depsgraph_update_post.remove(focus_continuous)
	bpy.types.VIEW3D_HT_header.remove(focus_single_button)
	bpy.types.VIEW3D_HT_header.remove(focus_continuous_button)
	bpy.types.VIEW3D_HT_header.remove(focus_distance_header)

	for cls in classes:
		unregister_class(cls)
	del bpy.types.Camera.photographer
	
	unregister_class (AddonPreferences)