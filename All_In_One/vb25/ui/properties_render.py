'''

  V-Ray/Blender

  http://vray.cgdo.ru

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *
from vb25.ui.ui import *
from vb25.plugins import *
from vb25 import version


class VRAY_MT_preset_IM(bpy.types.Menu):
	bl_label= "Irradiance Map Presets"
	preset_subdir= os.path.join("..", "startup", "vb25", "presets", "im")
	preset_operator= "script.execute_preset"
	draw= bpy.types.Menu.draw_preset


class VRAY_MT_preset_global(bpy.types.Menu):
	bl_label= "Global Presets"
	preset_subdir= os.path.join("..", "startup", "vb25", "presets", "render")
	preset_operator= "script.execute_preset"
	draw= bpy.types.Menu.draw_preset


class VRAY_MT_preset_gi(bpy.types.Menu):
	bl_label= "GI Presets"
	preset_subdir= os.path.join("..", "startup", "vb25", "presets", "gi")
	preset_operator= "script.execute_preset"
	draw= bpy.types.Menu.draw_preset


class VRAY_RP_dimensions(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Dimensions"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		scene= context.scene
		rd=    scene.render
		VRayScene= scene.vray

		# if VRayScene.image_aspect_lock:
		# 	rd.resolution_y= rd.resolution_x / VRayScene.image_aspect

		row = layout.row(align=True)
		row.menu("RENDER_MT_presets", text=bpy.types.RENDER_MT_presets.bl_label)
		row.operator("render.preset_add", text="", icon="ZOOMIN")
		row.operator("render.preset_add", text="", icon="ZOOMOUT").remove_active= True

		split= layout.split()
		col= split.column()
		col.label(text="Resolution:")
		sub= col.column(align=True)
		sub.prop(rd, "resolution_x", text="X")
		sub.prop(rd, "resolution_y", text="Y")
		# sub_aspect= sub.column()
		# sub_aspect.active= not VRayScene.image_aspect_lock
		# sub_aspect.prop(rd, "resolution_y", text="Y")
		sub.operator("vray.flip_resolution", text="", icon="FILE_REFRESH")
		sub.prop(rd, "resolution_percentage", text="")

		row= col.row()
		row.prop(rd, "use_border", text="Border")
		sub= row.row()
		sub.active = rd.use_border
		sub.prop(rd, "use_crop_to_border", text="Crop")

		if wide_ui:
			col= split.column()

		# sub = col.column(align=True)
		# sub.prop(VRayScene, "image_aspect_lock", text="Image aspect")
		# if VRayScene.image_aspect_lock:
		# 	sub.prop(VRayScene, "image_aspect")
		# sub.label(text="Pixel aspect:")
		# sub.prop(rd, "pixel_aspect_x", text="X")
		# sub.prop(rd, "pixel_aspect_y", text="Y")

		# split= layout.split()
		# col = split.column()
		sub = col.column(align=True)
		sub.label(text="Frame Range:")
		sub.prop(scene, "frame_start", text="Start")
		sub.prop(scene, "frame_end", text="End")
		sub.prop(scene, "frame_step", text="Step")

		# if wide_ui:
		# 	col= split.column()

		sub = col.column(align=True)
		sub.label(text="Frame Rate:")
		sub.prop(rd, "fps")
		sub.prop(rd, "fps_base", text="/")
		subrow = sub.row(align=True)
		subrow.prop(rd, "frame_map_old", text="Old")
		subrow.prop(rd, "frame_map_new", text="New")


class VRAY_RP_output(VRayRenderPanel, bpy.types.Panel):
	bl_label	   = "Output"

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW', 'VRAY_RENDER_RT'}

	def draw_header(self, context):
		VRayExporter= context.scene.vray.exporter
		self.layout.prop(VRayExporter, 'auto_save_render', text="")

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		scene = context.scene
		rd    = scene.render.image_settings

		VRayScene      = scene.vray
		VRayExporter   = VRayScene.exporter
		SettingsOutput = VRayScene.SettingsOutput

		layout.active= VRayExporter.auto_save_render

		if wide_ui:
			split= layout.split(percentage=0.2)
			col= split.column()
			col.label(text="Path:")
			col.label(text="Filename:")
			col= split.column()
			col.prop(SettingsOutput, 'img_dir',  text="")
			col.prop(SettingsOutput, 'img_file', text="")
		else:
			layout.prop(SettingsOutput, 'img_dir',  text="")
			layout.prop(SettingsOutput, 'img_file', text="")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(SettingsOutput, 'img_format', text= "Format")

		img_format = SettingsOutput.img_format

		split= layout.split()
		col= split.column()

		if img_format not in ('JPG', 'VRIMG'):
			col.prop(SettingsOutput, 'color_depth')
		if img_format == 'JPG':
			col.prop(rd, 'quality', slider= True)
		elif img_format == 'PNG':
			col.prop(rd, 'quality', slider= True, text= "Compression")
		elif img_format == 'EXR':
			row= col.row()
			row.prop(rd, 'exr_codec')

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(SettingsOutput, 'img_noAlpha')
		col.prop(SettingsOutput, 'img_separateAlpha')
		if wide_ui:
			col = split.column()
		if img_format == 'EXR':
			col.prop(SettingsOutput, 'relements_separateFiles')
		col.prop(SettingsOutput, 'relements_separateFolders')

		split= layout.split()
		col= split.column()
		col.prop(SettingsOutput, 'img_file_needFrameNumber')
		if wide_ui:
			col = split.column()
		col.prop(VRayExporter, 'image_to_blender')

		# sub= col.column()
		# sub.active= False
		# sub.prop(rd, "use_overwrite")


class VRAY_RP_render(VRayRenderPanel, bpy.types.Panel):
	bl_label       = "Render"

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		rd= context.scene.render

		VRayScene=       context.scene.vray
		VRayExporter=    VRayScene.exporter
		SettingsOptions= VRayScene.SettingsOptions

		split= layout.split()
		col= split.column()
		if VRayExporter.animation:
			render_label= "Animation"
			render_icon= 'RENDER_ANIMATION'
		elif VRayExporter.camera_loop:
			render_label= "Cameras"
			render_icon= 'RENDER_ANIMATION'
		else:
			render_label= "Image"
			render_icon= 'RENDER_STILL'

		col.operator('render.render', text= render_label, icon= render_icon)

		if not VRayExporter.auto_meshes:
			if wide_ui:
				col= split.column()
			col.operator('vray.write_geometry', icon='OUTLINER_OB_MESH')

		if VRayExporter.animation:
			layout.prop(VRayExporter, 'animation_type')

		split= layout.split()
		col= split.column()
		col.label(text="Modules:")
		col.prop(VRayScene.SettingsGI, 'on', text="Global Illumination")
		col.prop(VRayScene.SettingsCaustics, 'on', text="Caustics")
		col.prop(VRayExporter, 'use_displace')
		col.prop(VRayScene.VRayDR, 'on')
		col.prop(VRayScene.VRayBake, 'use')
		col.prop(VRayScene.RTEngine, 'enabled')
		col.prop(VRayScene.VRayStereoscopicSettings, 'use')
		if wide_ui:
			col= split.column()
		col.label(text="Pipeline:")
		col.prop(VRayExporter, 'activeLayers', text="Layers")
		if VRayExporter.activeLayers == 'CUSTOM':
			col.prop(VRayExporter, 'customRenderLayers', text="")
		col.prop(VRayExporter, 'animation')
		if not VRayExporter.animation:
			col.prop(VRayExporter, 'camera_loop')
		if VRayScene.SettingsGI.on:
			col.prop(SettingsOptions, 'gi_dontRenderImage')
		col.prop(VRayExporter, 'use_still_motion_blur')
		col.label(text="Options:")
		if VRayExporter.animation:
			col.prop(VRayExporter, 'check_animated')
		col.prop(VRayExporter, 'draft')

		layout.separator()
		layout.prop(rd, "display_mode", text="Display")



class VRAY_RP_SettingsOptions(VRayRenderPanel, bpy.types.Panel):
	bl_label   = "Globals"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		VRayScene= context.scene.vray
		VRayExporter=    VRayScene.exporter
		SettingsOptions= VRayScene.SettingsOptions

		split= layout.split()
		col= split.column()
		col.label(text="Geometry:")
		col.prop(SettingsOptions, 'geom_doHidden')
		col.prop(SettingsOptions, 'geom_backfaceCull')
		col.prop(SettingsOptions, 'ray_bias', text="Secondary bias")
		if wide_ui:
			col= split.column()
		col.label(text="Lights:")
		col.prop(SettingsOptions, 'light_doLights')
		# col.prop(SettingsOptions, 'light_doDefaultLights')
		col.prop(SettingsOptions, 'light_doHiddenLights')
		col.prop(SettingsOptions, 'light_doShadows')
		col.prop(SettingsOptions, 'light_onlyGI')

		layout.label(text="Materials:")
		split= layout.split()
		col= split.column()
		col.prop(SettingsOptions, 'mtl_override_on')
		if SettingsOptions.mtl_override_on:
			col.prop_search(SettingsOptions, 'mtl_override', bpy.data, 'materials', text="")
		col.prop(SettingsOptions, 'mtl_doMaps')
		if SettingsOptions.mtl_doMaps:
			col.prop(SettingsOptions, 'mtl_filterMaps')
			col.prop(SettingsOptions, 'mtl_filterMapsForSecondaryRays')
		if wide_ui:
			col= split.column()
		col.prop(SettingsOptions, 'mtl_reflectionRefraction')
		if SettingsOptions.mtl_reflectionRefraction:
			col.prop(SettingsOptions, 'mtl_limitDepth')
			if SettingsOptions.mtl_limitDepth:
				col.prop(SettingsOptions, 'mtl_maxDepth')
		col.prop(SettingsOptions, 'mtl_glossy')

		split= layout.split()
		col= split.column()
		col.prop(SettingsOptions, 'mtl_transpMaxLevels')
		if wide_ui:
			col= split.column()
		col.prop(SettingsOptions, 'mtl_transpCutoff')

		layout.separator()
		layout.label(text="Ray Intensity:")
		split = layout.split()
		col = split.column()
		col.prop(SettingsOptions, 'ray_max_intensity_on')
		col = split.column()
		col.active = SettingsOptions.ray_max_intensity_on
		col.prop(SettingsOptions, 'ray_max_intensity')


class VRAY_RP_exporter(VRayRenderPanel, bpy.types.Panel):
	bl_label   = "Exporter"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		rd= context.scene.render
		ve= context.scene.vray.exporter

		row= layout.row(align=True)
		row.menu("VRAY_MT_preset_global", text=bpy.types.VRAY_MT_preset_global.bl_label)
		row.operator("vray.preset_add", text="", icon="ZOOMIN")
		row.operator("vray.preset_add", text="", icon="ZOOMOUT").remove_active = True

		layout.separator()

		split= layout.split()
		col= split.column()
		col.label(text="Options:")
		col.prop(ve, 'autorun')
		col.prop(ve, 'auto_meshes')
		col.prop(ve, 'display')
		col.prop(ve, 'autoclose')
		col.prop(ve, 'debug')
		if wide_ui:
			col= split.column()
		col.label(text="Mesh export:")
		col.prop(ve, 'mesh_active_layers', text= "Active layers")
		col.prop(ve, 'use_instances')
		# col.prop(SettingsOptions, 'geom_displacement')
		col.prop(ve, 'mesh_debug')

		layout.separator()

		layout.label(text="Rendering:")
		split = layout.split()
		col = split.column()
		col.prop(ve, 'use_smoke')
		col.prop(ve, 'use_smoke_hires', text = "Smoke HR")
		if wide_ui:
			col= split.column()
		col.prop(ve, 'use_hair')
		col.prop(ve, 'random_material', text="Randomize Materials")

		layout.separator()

		layout.label(text="Experimental:")
		split = layout.split()
		col = split.column()
		col.prop(ve, 'use_feedback')
		if wide_ui:
			col= split.column()
		col.prop(ve, 'use_progress')

		layout.separator()

		layout.label(text="Advanced:")
		split= layout.split()
		col= split.column()
		col.prop(ve, 'detect_vray')
		if wide_ui:
			col= split.column()
		col.prop(ve, 'display_srgb')
		if not ve.detect_vray:
			split= layout.split()
			col= split.column()
			col.prop(ve, 'vray_binary')
		split= layout.split()
		col= split.column()
		if PLATFORM == "linux":
			col.prop(ve, 'log_window')
			if ve.log_window:
				col.prop(ve, 'log_window_type', text="Terminal")
				if ve.log_window_type == 'CUSTOM':
					col.prop(ve, 'log_window_term')
		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(ve, 'output', text="Export to")
		if ve.output == 'USER':
			col.prop(ve, 'output_dir')
		col.prop(ve, 'output_unique')

		layout.separator()

		layout.operator('vray.update', icon='FILE_REFRESH')

		# Manual render pipeline controls
		if ve.animation:
			render_label = "Animation"
			render_icon  = 'RENDER_ANIMATION'
		elif ve.camera_loop:
			render_label = "Cameras"
			render_icon  = 'RENDER_ANIMATION'
		else:
			render_label = "Image"
			render_icon  = 'RENDER_STILL'


class VRAY_RP_cm(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Color mapping"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		vs= context.scene.vray
		cm= vs.SettingsColorMapping

		split= layout.split()
		col= split.column()
		col.prop(cm, 'type')
		if cm.type == 'REIN':
			col.prop(cm, "dark_mult", text="Multiplier")
			col.prop(cm, "bright_mult",  text="Burn")
		elif cm.type in ('GCOR', 'GINT'):
			col.prop(cm, "bright_mult", text="Multiplier")
			col.prop(cm, "dark_mult", text="Inverse gamma")
		else:
			col.prop(cm, "bright_mult")
			col.prop(cm, "dark_mult")
		col.prop(cm, "gamma")
		col.prop(cm, "input_gamma")
		if wide_ui:
			col= split.column()
		col.prop(cm, "affect_background")
		col.prop(cm, "subpixel_mapping")
		col.prop(cm, "adaptation_only")
		col.prop(cm, "linearWorkflow")
		col.prop(cm, "clamp_output")
		if cm.clamp_output:
			col.prop(cm, "clamp_level")


class VRAY_RP_aa(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Image sampler"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		vs= context.scene.vray
		module= vs.SettingsImageSampler

		split= layout.split()
		col= split.column()
		col.prop(module, "type")

		split= layout.split()
		col= split.column()
		col.label(text="Parameters:")

		split= layout.split()
		col= split.column()
		if module.type == 'FXD':
			col.prop(module, "fixed_subdivs")
		elif module.type == 'DMC':
			col.prop(module, "dmc_minSubdivs")
			col.prop(module, "dmc_maxSubdivs")

			if wide_ui:
				col= split.column()
			col.prop(module, "dmc_treshhold_use_dmc", text= "Use DMC sampler thresh.")
			if not module.dmc_treshhold_use_dmc:
				col.prop(module, "dmc_threshold")
			col.prop(module, "dmc_show_samples")
		elif module.type == 'DMC':
			col.prop(module, "subdivision_minRate")
			col.prop(module, "subdivision_maxRate")
			col.prop(module, "subdivision_threshold")

			if wide_ui:
				col= split.column()
			col= split.column()
			col.prop(module, "subdivision_edges")
			col.prop(module, "subdivision_normals")
			if module.subdivision_normals:
				col.prop(module, "subdivision_normals_threshold")
			col.prop(module, "subdivision_jitter")
			col.prop(module, "subdivision_show_samples")
		else:
			col.prop(module, 'progressive_minSubdivs')
			col.prop(module, 'progressive_maxSubdivs')
			col.prop(module, 'progressive_showMask')
			if wide_ui:
				col = split.column()
			col.prop(module, 'progressive_threshold')
			col.prop(module, 'progressive_maxTime')
			col.prop(module, 'progressive_bundleSize')

		if module.type != 'PRG':
			layout.separator()
			
			split= layout.split()
			col= split.column()
			col.label(text="Filter type:")
			if wide_ui:
				col= split.column()
			col.prop(module, "filter_type", text="")
			if module.filter_type not in {'NONE', 'CATMULL'}:
				col.prop(module, "filter_size")


class VRAY_RP_dmc(VRayRenderPanel, bpy.types.Panel):
	bl_label = "DMC sampler"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		vs= context.scene.vray
		module= vs.SettingsDMCSampler

		split= layout.split()
		col= split.column()
		col.prop(module, "adaptive_threshold")
		col.prop(module, "subdivs_mult")
		col.prop(module, "time_dependent")

		if wide_ui:
			col= split.column()
		col.prop(module, "adaptive_amount")
		col.prop(module, "adaptive_min_samples")


class VRAY_RP_gi(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Global Illumination"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		SettingsGI= context.scene.vray.SettingsGI
		return super().poll(context) and SettingsGI.on

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		VRayScene=  context.scene.vray
		SettingsGI= VRayScene.SettingsGI

		row= layout.row(align=True)
		row.menu("VRAY_MT_preset_gi", text=bpy.types.VRAY_MT_preset_gi.bl_label)
		row.operator("vray.preset_gi_add", text="", icon="ZOOMIN")
		row.operator("vray.preset_gi_add", text="", icon="ZOOMOUT").remove_active = True

		layout.separator()

		split= layout.split()
		col= split.column()
		col.label(text="GI caustics:")
		sub= col.column()
		sub.prop(SettingsGI, "reflect_caustics", text="Reflect")
		sub.prop(SettingsGI, "refract_caustics", text="Refract")
		if wide_ui:
			col= split.column()
		col.label(text="Post-processing:")
		sub= col.column()
		sub.prop(SettingsGI, "saturation")
		sub.prop(SettingsGI, "contrast")
		sub.prop(SettingsGI, "contrast_base")

		layout.label(text="Primary engine:")
		if wide_ui:
			split= layout.split(percentage=0.35)
		else:
			split= layout.split()
		col= split.column()
		col.prop(SettingsGI, "primary_multiplier", text="Mult")
		if wide_ui:
			col= split.column()
		col.prop(SettingsGI, "primary_engine", text="")

		if SettingsGI.primary_engine != 'SH':
			layout.label(text="Secondary engine:")
			if wide_ui:
				split= layout.split(percentage=0.35)
			else:
				split= layout.split()
			col= split.column()
			col.prop(SettingsGI, "secondary_multiplier", text="Mult")
			if wide_ui:
				col= split.column()
			col.prop(SettingsGI, "secondary_engine", text="")


		layout.separator()

		layout.prop(SettingsGI, 'ao_on', text="Ambient occlusion")
		if SettingsGI.ao_on:
			split= layout.split()
			col= split.column()
			col.prop(SettingsGI, 'ao_amount', slider= True)
			if wide_ui:
				col= split.column()
			col.prop(SettingsGI, 'ao_radius')
			col.prop(SettingsGI, 'ao_subdivs')

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(SettingsGI, 'ray_distance_on')
		if wide_ui:
			col= split.column()
		sub= col.column()
		sub.active= SettingsGI.ray_distance_on
		sub.prop(SettingsGI, 'ray_distance')


class VRAY_RP_GI_sh(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Spherical Harmonics"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		module= context.scene.vray.SettingsGI
		return (engine_poll(__class__, context) and module.on and (module.primary_engine == 'SH'))

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		VRayScene=                  context.scene.vray
		SettingsGI=                 VRayScene.SettingsGI

		layout.prop(SettingsGI, 'spherical_harmonics', expand= True)

		layout.separator()

		if SettingsGI.spherical_harmonics == 'RENDER':
			SphericalHarmonicsRenderer= SettingsGI.SphericalHarmonicsRenderer

			split= layout.split()
			col= split.column()
			col.prop(SphericalHarmonicsRenderer, 'file_name')
			col.prop(SphericalHarmonicsRenderer, 'precalc_light_per_frame')

			layout.separator()

			split= layout.split()
			col= split.column()
			col.prop(SphericalHarmonicsRenderer, 'sample_environment')
			if SphericalHarmonicsRenderer.sample_environment:
				col.prop(SphericalHarmonicsRenderer, 'is_hemispherical')
				col.prop(SphericalHarmonicsRenderer, 'subdivs', slider= True)

			if wide_ui:
				col= split.column()

			col.prop(SphericalHarmonicsRenderer, 'apply_filtering')
			if SphericalHarmonicsRenderer.apply_filtering:
				col.prop(SphericalHarmonicsRenderer, 'filter_strength', slider= True)

		else:
			SphericalHarmonicsExporter= SettingsGI.SphericalHarmonicsExporter

			layout.prop(SphericalHarmonicsExporter, 'file_name')
			layout.prop(SphericalHarmonicsExporter, 'file_format')

			layout.separator()

			split= layout.split()
			col= split.column()
			col.prop(SphericalHarmonicsExporter, 'mode')

			if str(SphericalHarmonicsExporter.mode).endswith('_SEL'):
				col.prop_search(SphericalHarmonicsExporter, 'node',
								   context.scene,              'objects')

			col.prop(SphericalHarmonicsExporter, 'object_space')
			col.prop(SphericalHarmonicsExporter, 'per_normal')

			split= layout.split()
			col= split.column()
			col.prop(SphericalHarmonicsExporter, 'bands', slider= True)
			col.prop(SphericalHarmonicsExporter, 'subdivs', slider= True)
			if wide_ui:
				col= split.column()
			col.prop(SphericalHarmonicsExporter, 'ray_bias')

			if SphericalHarmonicsExporter.mode in ('INT_SEL', 'INT_ALL'):
				col.prop(SphericalHarmonicsExporter, 'bounces')
				col.prop(SphericalHarmonicsExporter, 'hit_recording')


class VRAY_RP_GI_im(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Irradiance Map"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		module= context.scene.vray.SettingsGI
		return engine_poll(__class__, context) and module.on and module.primary_engine == 'IM'

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		vs= context.scene.vray
		gi= vs.SettingsGI
		module= gi.SettingsIrradianceMap

		split= layout.split()
		colR= split.column()
		colR.prop(module, "mode", text="Mode")

		if module.mode not in ('FILE', 'ANIM_REND'):
			split= layout.split()
			col= split.column()
			col.label(text="Preset:")
			if wide_ui:
				col= split.column()
			col.menu('VRAY_MT_preset_IM', text="Preset")

			split= layout.split()
			split.label(text="Basic parameters:")

			split= layout.split()
			col= split.column(align=True)
			col.prop(module,"min_rate")
			col.prop(module,"max_rate")
			col.prop(module,"subdivs", text= "HSph. subdivs")
			if wide_ui:
				col= split.column(align=True)
			else:
				split= layout.split()
				col= split.column(align=True)
			col.prop(module,"color_threshold", text="Clr thresh", slider=True)
			col.prop(module,"normal_threshold", text="Nrm thresh", slider=True)
			col.prop(module,"distance_threshold", text="Dist thresh", slider=True)

			split= layout.split()
			split.column().prop(module,"interp_samples", text= "Interp. samples")
			if wide_ui:
				split.column()

			split= layout.split()
			split.label(text="Advanced parameters:")
			if wide_ui:
				split= layout.split(percentage=0.7)
			else:
				split= layout.split()
			col= split.column()
			col.prop(module,"interpolation_mode", text="Interp. type")
			col.prop(module,"lookup_mode")
			col.prop(module,"calc_interp_samples")
			if wide_ui:
				col= split.column()
			col.prop(module,"multipass")
			col.prop(module,"randomize_samples", text="Randomize")
			col.prop(module,"check_sample_visibility", text="Check sample")

		if module.mode == 'FILE':
			layout.label(text="Basic parameters:")
			layout.prop(module,"interp_samples", text= "Interp. samples")

			layout.label(text="Advanced parameters:")
			split= layout.split()
			col= split.column()
			col.prop(module,"interpolation_mode", text="Interp. type")
			col.prop(module,"lookup_mode")
			col.prop(module,"calc_interp_samples")

		if module.mode == 'ANIM_REND':
			split= layout.split()
			split.label(text="Basic parameters:")

			split= layout.split()
			colL= split.column()
			colL.prop(module,"interp_frames")

		split= layout.split()
		split.label(text="Detail enhancement:")
		if wide_ui:
			split= layout.split(percentage=0.07)
			split.column().prop(module, "detail_enhancement", text="")
			sub= split.column().row(align=True)
			sub.active= module.detail_enhancement
			sub.prop(module, "detail_radius", text="R")
			sub.prop(module, "detail_subdivs_mult", text="Subdivs", slider=True)
			sub.prop(module, "detail_scale", text="")
		else:
			split= layout.split()
			col= split.column()
			col.prop(module, "detail_enhancement", text="Use")
			sub= col.column(align=True)
			sub.active= module.detail_enhancement
			sub.prop(module, "detail_radius", text="R")
			sub.prop(module, "detail_subdivs_mult", text="Subdivs", slider=True)
			sub.prop(module, "detail_scale", text="")

		layout.label(text="Show:")
		split = layout.split()
		if wide_ui:
			col = split.row()
		else:
			col = split.column()
		col.prop(module,"show_calc_phase", text="Calc phase")
		sub = col.column()
		sub.active = module.show_calc_phase
		sub.prop(module,"show_direct_light", text="Direct light")
		col.prop(module,"show_samples", text="Samples")

		layout.label(text="Options:")
		split= layout.split()
		col= split.column()
		col.prop(module,"multiple_views", text="Use camera path")

		split= layout.split()
		split.label(text="Files:")
		split= layout.split(percentage=0.3)
		colL= split.column()
		colR= split.column()
		if module.mode in ('FILE', 'ANIM_REND'):
			colL.label(text="Map file name:")
			colR.prop(module,"file", text="")
		else:
			colL.prop(module,"auto_save", text="Auto save")
			colR.active= module.auto_save
			colR.prop(module,"auto_save_file", text="")


class VRAY_RP_GI_bf(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Brute Force"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		module= context.scene.vray.SettingsGI
		return engine_poll(__class__, context) and module.on and (module.primary_engine == 'BF' or module.secondary_engine == 'BF') and (module.primary_engine != 'SH')

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		vsce= context.scene.vray
		gi= vsce.SettingsGI
		module= gi.SettingsDMCGI

		split= layout.split()
		col= split.column()
		col.prop(module, "subdivs")
		if gi.secondary_engine == 'BF':
			if wide_ui:
				col= split.column()
			col.prop(module, "depth")


class VRAY_RP_GI_lc(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Light Cache"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		module= context.scene.vray.SettingsGI
		return (engine_poll(__class__, context) and module.on and (module.primary_engine == 'LC' or module.secondary_engine == 'LC')) and (module.primary_engine != 'SH')

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		vs= context.scene.vray
		module= vs.SettingsGI.SettingsLightCache

		split= layout.split()
		col= split.column()
		col.prop(module, "mode", text="Mode")

		if not module.mode == 'FILE':
			layout.label(text="Calculation parameters:")
			if wide_ui:
				split= layout.split(percentage=0.6)
			else:
				split= layout.split()
			col= split.column()
			col.prop(module, "subdivs")
			col.prop(module, "sample_size")
			col.prop(module, "world_scale", text="Sample scale")
			if not module.num_passes_auto:
				col.prop(module, "num_passes")
			col.prop(module, "depth", slider= True)

			if wide_ui:
				col= split.column()
			col.prop(module, "store_direct_light")
			col.prop(module, "adaptive_sampling")
			col.prop(module, "show_calc_phase")
			col.prop(module, "num_passes_auto")

		layout.label(text="Reconstruction parameters:")
		split= layout.split(percentage=0.2)
		split.column().prop(module, "filter")
		sub= split.column().row()
		sub.active= module.filter
		sub.prop(module, "filter_type", text="Type")
		if module.filter_type != 'NONE':
			if module.filter_type == 'NEAREST':
				sub.prop(module, "filter_samples")
			else:
				sub.prop(module, "filter_size")
		else:
			sub.label(text="")

		split= layout.split(percentage=0.2)
		split.column().prop(module, "prefilter")
		colR= split.column()
		colR.active= module.prefilter
		colR.prop(module, "prefilter_samples")

		split= layout.split()
		split= layout.split()
		col= split.column()
		col.prop(module, "use_for_glossy_rays")
		col.prop(module, "multiple_views")
		if wide_ui:
			col= split.column()
		col.prop(module, "retrace_enabled")
		sub= col.column()
		sub.active= module.retrace_enabled
		sub.prop(module, "retrace_threshold", text="Retrace thresh.")

		split= layout.split()
		split.label(text="Files:")
		split= layout.split(percentage=0.3)
		colL= split.column()
		colR= split.column()
		if module.mode == 'FILE':
			colL.label(text="Map file name:")
			colR.prop(module,"file", text="")
		else:
			colL.prop(module,"auto_save", text="Auto save")
			colR.active= module.auto_save
			colR.prop(module,"auto_save_file", text="")


class VRAY_RP_displace(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Displace / subdiv"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		VRayExporter= context.scene.vray.exporter
		return engine_poll(__class__, context) and VRayExporter.use_displace

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		VRayScene= context.scene.vray
		SettingsDefaultDisplacement= VRayScene.SettingsDefaultDisplacement

		split= layout.split()
		col= split.column()
		col.prop(SettingsDefaultDisplacement, 'amount')
		col.prop(SettingsDefaultDisplacement, 'edgeLength')
		col.prop(SettingsDefaultDisplacement, 'maxSubdivs')
		if wide_ui:
			col= split.column()
		col.prop(SettingsDefaultDisplacement, 'viewDependent')
		col.prop(SettingsDefaultDisplacement, 'tightBounds')
		col.prop(SettingsDefaultDisplacement, 'relative')
		col.prop(SettingsDefaultDisplacement, 'override_on')


class VRAY_RP_dr(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Distributed rendering"

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		vs= context.scene.vray
		module= vs.VRayDR
		return engine_poll(__class__, context) and module.on

	def draw(self, context):
		layout = self.layout

		VRayScene = context.scene.vray
		VRayDR          = VRayScene.VRayDR
		SettingsOptions = VRayScene.SettingsOptions

		layout.prop(VRayDR, 'transferAssets')

		if VRayDR.transferAssets == '0':
			layout.prop(VRayDR, 'shared_dir', text="Share Path")
			if PLATFORM == 'win32':
				layout.prop(VRayDR, 'share_name', text="Share Name")
		else:
			split= layout.split()
			col= split.column()
			col.prop(VRayDR, 'renderOnlyOnNodes')
			col.prop(SettingsOptions, 'misc_abortOnMissingAsset')
			col.prop(SettingsOptions, 'dr_overwriteLocalCacheSettings')
			split= layout.split()
			split.active = SettingsOptions.dr_overwriteLocalCacheSettings
			col= split.column()
			col.prop(SettingsOptions, 'dr_assetsCacheLimitType', text="Cache Limit")
			sub = col.row()
			sub.active = SettingsOptions.dr_assetsCacheLimitType != '0'
			sub.prop(SettingsOptions, 'dr_assetsCacheLimitValue', text="Limit")

		layout.separator()
		layout.prop(VRayDR, 'port', text="Port")

		layout.separator()

		split= layout.split()
		row= split.row()
		row.template_list("VRayListDR", "", VRayDR, 'nodes', VRayDR, 'nodes_selected', rows= 3)
		col= row.column(align=True)
		col.operator('vray.render_nodes_add',    text="", icon="ZOOMIN")
		col.operator('vray.render_nodes_remove', text="", icon="ZOOMOUT")

		col = col.row().column(align=True)
		col.operator('vray.dr_nodes_load',       text="", icon="FILE_FOLDER")
		col.operator('vray.dr_nodes_save',       text="", icon="SAVE_PREFS")

		if VRayDR.nodes_selected >= 0 and len(VRayDR.nodes) > 0:
			render_node= VRayDR.nodes[VRayDR.nodes_selected]

			layout.separator()

			layout.prop(render_node, 'name')
			layout.prop(render_node, 'address')


class VRAY_RP_bake(VRayRenderPanel, bpy.types.Panel):
	bl_label   = "Bake"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		VRayScene= context.scene.vray
		VRayBake= VRayScene.VRayBake
		return (engine_poll(__class__, context) and VRayBake.use)

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		VRayScene= context.scene.vray
		VRayBake= VRayScene.VRayBake

		layout= self.layout

		split= layout.split()
		col= split.column()
		col.prop_search(VRayBake, 'bake_node', context.scene, 'objects')
		
		col.prop(VRayBake, 'uvChannel')

		split= layout.split()
		col= split.column()
		col.prop(VRayBake, 'dilation')
		if wide_ui:
			col= split.column()
		col.prop(VRayBake, 'flip_derivs')


class VRAY_PA_SettingsVFB(VRayRenderPanel, bpy.types.Panel):
	bl_label = "Lens Effects"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw_header(self, context):
		VRayScene = context.scene.vray
		SettingsVFB = VRayScene.SettingsVFB
		self.layout.prop(SettingsVFB, 'use', text="")

	def draw(self, context):
		wide_ui = context.region.width > narrowui
		layout = self.layout

		VRayScene = context.scene.vray
		SettingsVFB = VRayScene.SettingsVFB

		layout.active = SettingsVFB.use

		layout.prop(SettingsVFB, 'bloom_on', text="Bloom")
		split = layout.split()
		split.active = SettingsVFB.bloom_on
		col = split.column()
		col.prop(SettingsVFB, 'bloom_mode', text="Mode")
		col.prop(SettingsVFB, 'bloom_fill_edges', text="Fill Edges")
		col.prop(SettingsVFB, 'bloom_weight', text="Weight")
		col.prop(SettingsVFB, 'bloom_size', text="Size")
		col.prop(SettingsVFB, 'bloom_shape', text="Shape")
		if wide_ui:
			col = split.column()
		col.prop(SettingsVFB, 'bloom_mask_intensity_on', text="Mask Intensity")
		col.prop(SettingsVFB, 'bloom_mask_intensity', text="Intensity")
		col.prop(SettingsVFB, 'bloom_mask_objid_on', text="Use Object ID")
		col.prop(SettingsVFB, 'bloom_mask_objid', text="Object ID")
		col.prop(SettingsVFB, 'bloom_mask_mtlid_on', text="Use Material ID")
		col.prop(SettingsVFB, 'bloom_mask_mtlid', text="Material ID")

		layout.prop(SettingsVFB, 'glare_on', text="Glare")
		split = layout.split()
		split.active = SettingsVFB.glare_on
		col = split.column()
		col.prop(SettingsVFB, 'glare_mode', text="Mode")
		col.prop(SettingsVFB, 'glare_type', text="Type")
		col.prop(SettingsVFB, 'glare_fill_edges', text="Fill Edges")
		col.prop(SettingsVFB, 'glare_weight', text="Weight")
		col.prop(SettingsVFB, 'glare_size', text="Size")
		col.prop(SettingsVFB, 'glare_diffraction_on', text="Use Diffraction")
		col.prop(SettingsVFB, 'glare_cam_blades_on', text="Use Blades")
		col.prop(SettingsVFB, 'glare_cam_num_blades', text="Num. Blades")
		col.prop(SettingsVFB, 'glare_cam_rotation', text="Rotation")
		col.prop(SettingsVFB, 'glare_cam_fnumber', text="F-Number")
		if wide_ui:
			col = split.column()
		col.prop(SettingsVFB, 'glare_mask_intensity_on', text="Mask Intensity")
		col.prop(SettingsVFB, 'glare_mask_intensity', text="Intensity")
		col.prop(SettingsVFB, 'glare_mask_objid_on', text="Use Object ID")
		col.prop(SettingsVFB, 'glare_mask_objid', text="Object ID")
		col.prop(SettingsVFB, 'glare_mask_mtlid_on', text="Use Material ID")
		col.prop(SettingsVFB, 'glare_mask_mtlid', text="Material ID")
		col.prop(SettingsVFB, 'glare_image_path', text="Image Path")
		col.prop(SettingsVFB, 'glare_use_obstacle_image', text="Use Obstacle Image")
		col.prop(SettingsVFB, 'glare_obstacle_image_path', text="Obstacle Path")

		layout.label("Misc")
		split = layout.split()
		col = split.column()
		col.prop(SettingsVFB, 'interactive')


class VRAY_RP_SettingsSystem(VRayRenderPanel, bpy.types.Panel):
	bl_label   = "System"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return engine_poll(__class__, context)

	def draw(self, context):
		layout= self.layout
		wide_ui= context.region.width > narrowui

		rd= context.scene.render

		VRayScene= context.scene.vray
		SettingsRaycaster=        VRayScene.SettingsRaycaster
		SettingsUnitsInfo=        VRayScene.SettingsUnitsInfo
		SettingsRegionsGenerator= VRayScene.SettingsRegionsGenerator
		SettingsOptions=          VRayScene.SettingsOptions
		VRayExporter=             VRayScene.exporter

		layout.label(text="Threads:")
		split= layout.split()
		col= split.column()
		col.row().prop(rd, "threads_mode", expand=True)
		if wide_ui:
			col= split.column(align=True)
		sub= col.column()
		sub.enabled= rd.threads_mode == 'FIXED'
		sub.prop(rd, 'threads', text="Count")
		layout.prop(VRayExporter, 'meshExportThreads')

		layout.separator()
		layout.label(text="Raycaster parameters:")
		split= layout.split()
		col= split.column()
		col.prop(SettingsRaycaster, 'maxLevels')
		col.prop(SettingsRaycaster, 'minLeafSize')
		if wide_ui:
			col= split.column()
		col.prop(SettingsRaycaster, 'faceLevelCoef')
		col.prop(SettingsOptions, 'misc_lowThreadPriority')
		split= layout.split()
		col= split.column()
		col.prop(SettingsRaycaster, 'dynMemLimit')

		layout.separator()
		layout.prop(SettingsRaycaster, 'embreeUse', text="Use Embree")
		split = layout.split()
		split.active = SettingsRaycaster.embreeUse
		col = split.column()
		col.prop(SettingsRaycaster, 'embreeUseMB', text="Use For Motion Blur")
		col.prop(SettingsRaycaster, 'embreeHighPrec', text="High Precision")
		if wide_ui:
			col = split.column()
		col.prop(SettingsRaycaster, 'embreeLowMemory', text="Low Memory")
		col.prop(SettingsRaycaster, 'embreeRayPackets', text="Ray Packets")

		# layout.separator()
		# layout.label(text="Units scale:")
		# split= layout.split()
		# col= split.column()
		# col.prop(SettingsUnitsInfo, 'meters_scale', text="Metric")
		# if wide_ui:
		# 	col= split.column()
		# col.prop(SettingsUnitsInfo, 'photometric_scale', text="Photometric")

		layout.separator()

		layout.label(text="Render region division:")
		split= layout.split()
		col= split.column()
		col.prop(SettingsRegionsGenerator, 'xymeans', text="XY")
		col.prop(SettingsRegionsGenerator, 'seqtype')
		col.prop(SettingsRegionsGenerator, 'reverse')
		if wide_ui:
			col= split.column()
		sub= col.row(align=True)
		sub.prop(SettingsRegionsGenerator, 'xc')
		sub= sub.column()
		sub.active= not SettingsRegionsGenerator.lock_size
		sub.prop(SettingsRegionsGenerator, 'yc')
		col.prop(SettingsRegionsGenerator, 'lock_size')

		layout.separator()
		layout.prop(VRayExporter, 'verboseLevel')


class VRAY_RP_about(VRayRenderPanel, bpy.types.Panel):
	bl_label   = "About"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return engine_poll(__class__, context)

	def draw(self, context):
		layout= self.layout

		split= layout.split()
		col= split.column()
		col.label(text="V-Ray For Blender %s" % version.VERSION)
		col.separator()
		col.label(text="URL: http://chaosgroup.com")
		col.label(text="Developer: Andrei Izrantcev")
		col.label(text="Email: andrei.izrantcev@chaosgroup.com")
		col.separator()
		col.label(text="IRC: irc.freenode.net #vrayblender")
		col.separator()
		col.label(text="V-Ray(R) is a registered trademark of Chaos Group Ltd.")


def GetRegClasses():
	return (
		VRAY_MT_preset_IM,
		VRAY_MT_preset_global,
		VRAY_MT_preset_gi,
		VRAY_RP_dimensions,
		VRAY_RP_output,
		VRAY_RP_render,
		VRAY_RP_SettingsOptions,
		VRAY_RP_exporter,
		VRAY_RP_cm,
		VRAY_RP_aa,
		VRAY_RP_dmc,
		VRAY_RP_gi,
		VRAY_RP_GI_sh,
		VRAY_RP_GI_im,
		VRAY_RP_GI_bf,
		VRAY_RP_GI_lc,
		VRAY_RP_displace,
		VRAY_RP_dr,
		VRAY_RP_bake,
		VRAY_PA_SettingsVFB,
		VRAY_RP_SettingsSystem,
		VRAY_RP_about,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
