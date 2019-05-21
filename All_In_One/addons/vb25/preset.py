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

''' vb modules '''
from vb25.utils import *


class VRAY_PRESETS():
	bl_options = {'REGISTER'}

	name= bpy.props.StringProperty(
		name= "Name",
		description= "Name of the preset, used to make the path name",
		maxlen= 64,
		default= "")

	remove_active= bpy.props.BoolProperty(
		default= False,
		options= {'HIDDEN'})

	@staticmethod
	def as_filename(name):
		for char in " !@#$%^&*(){}:\";'[]<>,.\\/?":
			name= name.replace(char, '_')
		return name.lower().strip()

	def execute(self, context):
		import os
		
		if hasattr(self, "pre_cb"):
			self.pre_cb(context)
		
		preset_menu_class = getattr(bpy.types, self.preset_menu)

		if not self.remove_active:		  
			if not self.name:
				return {'FINISHED'}

			filename= self.as_filename(self.name)
			
			target_path= os.path.normpath(os.path.join(get_vray_exporter_path(), "presets", self.preset_subdir))

			filepath= os.path.join(target_path, filename) + ".py"
			
			if hasattr(self, "add"):
				self.add(context, filepath)
			else:
				file_preset = open(filepath, 'w')
				file_preset.write("import bpy\n")

				for rna_path in self.preset_values:
					value = eval(rna_path)
					# convert thin wrapped sequences to simple lists to repr()
					try:
						value = value[:]
					except:
						pass

					file_preset.write("%s = %r\n" % (rna_path, value))

				file_preset.close()

			preset_menu_class.bl_label = bpy.path.display_name(filename)

		else:
			preset_active = preset_menu_class.bl_label

			filepath= os.path.join(get_vray_exporter_path(), "presets", self.preset_subdir, preset_active+".py")

			if not os.path.exists(filepath):
				return {'CANCELLED'}

			if hasattr(self, "remove"):
				self.remove(context, filepath)
			else:
				try:
					os.remove(filepath)
				except:
					import traceback
					traceback.print_exc()

			# XXX, stupid!
			preset_menu_class.bl_label = "Presets"

		if hasattr(self, "post_cb"):
			self.post_cb(context)

		return {'FINISHED'}

	def check(self, context):
		self.name = self.as_filename(self.name)

	def invoke(self, context, event):
		if not self.remove_active:
			wm = context.window_manager
			return wm.invoke_props_dialog(self)
		else:
			return self.execute(context)


class VRAY_PRESET_global_render(VRAY_PRESETS, bpy.types.Operator):
	'''Add a V-Ray global preset'''
	bl_label      = "Add V-Ray Global Preset"

	bl_idname     = "vray.preset_add"
	preset_menu   = "VRAY_MT_preset_global"
	preset_subdir = "render"

	preset_values= [
		"bpy.context.scene.vray.exporter.autorun",
		"bpy.context.scene.vray.exporter.animation",
		"bpy.context.scene.vray.exporter.auto_meshes",
		"bpy.context.scene.vray.exporter.debug",
		"bpy.context.scene.vray.exporter.image_to_blender",
		"bpy.context.scene.vray.exporter.active_layers",
		"bpy.context.scene.vray.exporter.mesh_active_layers",
		"bpy.context.scene.vray.exporter.check_animated",
		"bpy.context.scene.vray.exporter.use_displace",
		"bpy.context.scene.vray.exporter.use_instances",
		"bpy.context.scene.vray.exporter.use_hair",
		"bpy.context.scene.vray.exporter.detect_vray",
		"bpy.context.scene.vray.exporter.vray_binary",
		"bpy.context.scene.vray.exporter.output",
		"bpy.context.scene.vray.exporter.output_dir",
		"bpy.context.scene.vray.exporter.output_unique",

        "bpy.context.scene.vray.SettingsOptions.geom_displacement",
        "bpy.context.scene.vray.SettingsOptions.geom_doHidden",
        "bpy.context.scene.vray.SettingsOptions.light_doLights",
        "bpy.context.scene.vray.SettingsOptions.light_doDefaultLights",
        "bpy.context.scene.vray.SettingsOptions.light_doHiddenLights",
        "bpy.context.scene.vray.SettingsOptions.light_doShadows",
        "bpy.context.scene.vray.SettingsOptions.light_onlyGI",
        "bpy.context.scene.vray.SettingsOptions.gi_dontRenderImage",
        "bpy.context.scene.vray.SettingsOptions.mtl_reflectionRefraction",
        "bpy.context.scene.vray.SettingsOptions.mtl_limitDepth",
        "bpy.context.scene.vray.SettingsOptions.mtl_maxDepth",
        "bpy.context.scene.vray.SettingsOptions.mtl_doMaps",
        "bpy.context.scene.vray.SettingsOptions.mtl_filterMaps",
        "bpy.context.scene.vray.SettingsOptions.mtl_filterMapsForSecondaryRays",
        "bpy.context.scene.vray.SettingsOptions.mtl_transpMaxLevels",
        "bpy.context.scene.vray.SettingsOptions.mtl_transpCutoff",
        "bpy.context.scene.vray.SettingsOptions.mtl_override_on",
        "bpy.context.scene.vray.SettingsOptions.mtl_glossy",
        "bpy.context.scene.vray.SettingsOptions.geom_backfaceCull",
        "bpy.context.scene.vray.SettingsOptions.ray_bias",
        "bpy.context.scene.vray.SettingsOptions.misc_lowThreadPriority",

        "bpy.context.scene.vray.SettingsCaustics.on",
        "bpy.context.scene.vray.SettingsCaustics.max_photons",
        "bpy.context.scene.vray.SettingsCaustics.search_distance",
        "bpy.context.scene.vray.SettingsCaustics.max_density",
        "bpy.context.scene.vray.SettingsCaustics.multiplier",
        "bpy.context.scene.vray.SettingsCaustics.mode",
        "bpy.context.scene.vray.SettingsCaustics.file",
        "bpy.context.scene.vray.SettingsCaustics.auto_save",
        "bpy.context.scene.vray.SettingsCaustics.auto_save_file",
        "bpy.context.scene.vray.SettingsCaustics.show_calc_phase",

		"bpy.context.scene.vray.SettingsGI.on",
        "bpy.context.scene.vray.SettingsGI.refract_caustics",
        "bpy.context.scene.vray.SettingsGI.reflect_caustics",
        "bpy.context.scene.vray.SettingsGI.saturation",
        "bpy.context.scene.vray.SettingsGI.contrast",
        "bpy.context.scene.vray.SettingsGI.contrast_base",
        "bpy.context.scene.vray.SettingsGI.primary_engine",
        "bpy.context.scene.vray.SettingsGI.primary_multiplier",
        "bpy.context.scene.vray.SettingsGI.secondary_engine",
        "bpy.context.scene.vray.SettingsGI.secondary_multiplier",
        "bpy.context.scene.vray.SettingsGI.ray_distance_on",
        "bpy.context.scene.vray.SettingsGI.ray_distance",
        "bpy.context.scene.vray.SettingsGI.ao_on",
        "bpy.context.scene.vray.SettingsGI.ao_amount",
        "bpy.context.scene.vray.SettingsGI.ao_radius",
        "bpy.context.scene.vray.SettingsGI.ao_subdivs",
		
        "bpy.context.scene.vray.SettingsGI.SettingsDMCGI.subdivs",
        "bpy.context.scene.vray.SettingsGI.SettingsDMCGI.depth",

        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.min_rate",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.max_rate",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.subdivs",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.interp_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.calc_interp_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.interp_frames",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.color_threshold",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.normal_threshold",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.distance_threshold",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.detail_enhancement",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.detail_radius",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.detail_subdivs_mult",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.detail_scale",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.randomize_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.interpolation_mode",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.lookup_mode",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.mode",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.file",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.show_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.show_calc_phase",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.show_direct_light",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.multiple_views",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.multipass",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.check_sample_visibility",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.auto_save",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.auto_save_file",

        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.subdivs",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.sample_size",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.filter_type",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.filter_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.filter_size",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.prefilter",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.prefilter_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.depth",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.show_calc_phase",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.store_direct_light",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.world_scale",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.mode",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.file",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.auto_save",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.auto_save_file",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.num_passes",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.use_for_glossy_rays",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.adaptive_sampling",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.multiple_views",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.retrace_enabled",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.retrace_threshold",

		"bpy.context.scene.vray.SettingsDefaultDisplacement.override_on",
		"bpy.context.scene.vray.SettingsDefaultDisplacement.edgeLength",
		"bpy.context.scene.vray.SettingsDefaultDisplacement.viewDependent",
		"bpy.context.scene.vray.SettingsDefaultDisplacement.maxSubdivs",
		"bpy.context.scene.vray.SettingsDefaultDisplacement.tightBounds",
		"bpy.context.scene.vray.SettingsDefaultDisplacement.amount",
		"bpy.context.scene.vray.SettingsDefaultDisplacement.relative",

		"bpy.context.scene.vray.SettingsRegionsGenerator.xc",
		"bpy.context.scene.vray.SettingsRegionsGenerator.yc",
		"bpy.context.scene.vray.SettingsRegionsGenerator.reverse",
		"bpy.context.scene.vray.SettingsRegionsGenerator.seqtype",
		"bpy.context.scene.vray.SettingsRegionsGenerator.xymeans",

		"bpy.context.scene.vray.SettingsImageSampler.type",
		"bpy.context.scene.vray.SettingsImageSampler.fixed_subdivs",
		"bpy.context.scene.vray.SettingsImageSampler.dmc_minSubdivs",
		"bpy.context.scene.vray.SettingsImageSampler.dmc_threshold",
		"bpy.context.scene.vray.SettingsImageSampler.dmc_show_samples",
		"bpy.context.scene.vray.SettingsImageSampler.subdivision_minRate",
		"bpy.context.scene.vray.SettingsImageSampler.subdivision_maxRate",
		"bpy.context.scene.vray.SettingsImageSampler.subdivision_threshold",
		"bpy.context.scene.vray.SettingsImageSampler.subdivision_edges",
		"bpy.context.scene.vray.SettingsImageSampler.subdivision_normals",
		"bpy.context.scene.vray.SettingsImageSampler.subdivision_normals_threshold",
		"bpy.context.scene.vray.SettingsImageSampler.subdivision_jitter",
		"bpy.context.scene.vray.SettingsImageSampler.subdivision_show_samples",

		"bpy.context.scene.vray.SettingsRaycaster.maxLevels",
		"bpy.context.scene.vray.SettingsRaycaster.minLeafSize",
		"bpy.context.scene.vray.SettingsRaycaster.faceLevelCoef",
		"bpy.context.scene.vray.SettingsRaycaster.dynMemLimit",

		"bpy.context.scene.vray.SettingsDMCSampler.time_dependent",
		"bpy.context.scene.vray.SettingsDMCSampler.adaptive_amount",
		"bpy.context.scene.vray.SettingsDMCSampler.adaptive_threshold",
		"bpy.context.scene.vray.SettingsDMCSampler.adaptive_min_samples",
		"bpy.context.scene.vray.SettingsDMCSampler.subdivs_mult",

		"bpy.context.scene.vray.SettingsUnitsInfo.meters_scale",
		"bpy.context.scene.vray.SettingsUnitsInfo.photometric_scale",

		"bpy.context.scene.vray.SettingsColorMapping.affect_background",
		"bpy.context.scene.vray.SettingsColorMapping.dark_mult",
		"bpy.context.scene.vray.SettingsColorMapping.bright_mult",
		"bpy.context.scene.vray.SettingsColorMapping.gamma",
		"bpy.context.scene.vray.SettingsColorMapping.input_gamma",
		"bpy.context.scene.vray.SettingsColorMapping.subpixel_mapping",
		"bpy.context.scene.vray.SettingsColorMapping.clamp_output",
		"bpy.context.scene.vray.SettingsColorMapping.clamp_level",
		"bpy.context.scene.vray.SettingsColorMapping.adaptation_only",
		"bpy.context.scene.vray.SettingsColorMapping.linearWorkflow",

		"bpy.context.scene.vray.VRayDR.on",
		"bpy.context.scene.vray.VRayDR.shared_dir",
		"bpy.context.scene.vray.VRayDR.port",

		"bpy.context.scene.render.threads_mode",
		"bpy.context.scene.render.threads",
	]

bpy.utils.register_class(VRAY_PRESET_global_render)


class VRAY_PRESET_gi(VRAY_PRESETS, bpy.types.Operator):
	'''Add a V-Ray global preset'''
	bl_label      = "Add V-Ray Global Preset"

	bl_idname     = "vray.preset_gi_add"
	preset_menu   = "VRAY_MT_preset_gi"
	preset_subdir = "gi"

	preset_values= [
		"bpy.context.scene.vray.SettingsGI.on",
        "bpy.context.scene.vray.SettingsGI.refract_caustics",
        "bpy.context.scene.vray.SettingsGI.reflect_caustics",
        "bpy.context.scene.vray.SettingsGI.saturation",
        "bpy.context.scene.vray.SettingsGI.contrast",
        "bpy.context.scene.vray.SettingsGI.contrast_base",
        "bpy.context.scene.vray.SettingsGI.primary_engine",
        "bpy.context.scene.vray.SettingsGI.primary_multiplier",
        "bpy.context.scene.vray.SettingsGI.secondary_engine",
        "bpy.context.scene.vray.SettingsGI.secondary_multiplier",
        "bpy.context.scene.vray.SettingsGI.ray_distance_on",
        "bpy.context.scene.vray.SettingsGI.ray_distance",
        "bpy.context.scene.vray.SettingsGI.ao_on",
        "bpy.context.scene.vray.SettingsGI.ao_amount",
        "bpy.context.scene.vray.SettingsGI.ao_radius",
        "bpy.context.scene.vray.SettingsGI.ao_subdivs",
		
        "bpy.context.scene.vray.SettingsGI.SettingsDMCGI.subdivs",
        "bpy.context.scene.vray.SettingsGI.SettingsDMCGI.depth",

        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.min_rate",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.max_rate",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.subdivs",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.interp_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.calc_interp_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.interp_frames",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.color_threshold",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.normal_threshold",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.distance_threshold",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.detail_enhancement",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.detail_radius",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.detail_subdivs_mult",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.detail_scale",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.randomize_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.interpolation_mode",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.lookup_mode",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.mode",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.file",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.show_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.show_calc_phase",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.show_direct_light",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.multiple_views",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.multipass",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.check_sample_visibility",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.auto_save",
        "bpy.context.scene.vray.SettingsGI.SettingsIrradianceMap.auto_save_file",

        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.subdivs",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.sample_size",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.filter_type",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.filter_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.filter_size",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.prefilter",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.prefilter_samples",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.depth",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.show_calc_phase",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.store_direct_light",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.world_scale",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.mode",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.file",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.auto_save",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.auto_save_file",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.num_passes",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.use_for_glossy_rays",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.adaptive_sampling",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.multiple_views",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.retrace_enabled",
        "bpy.context.scene.vray.SettingsGI.SettingsLightCache.retrace_threshold",
	]

bpy.utils.register_class(VRAY_PRESET_gi)


# '''
#   BRDFSSS2Complex preset generator
# '''
# import os
# SSS2= {
# 	'Skin_brown': {
# 		'ior':                  1.3,
# 		'diffuse_color':        (169, 123, 92),
# 		'sub_surface_color':    (169, 123, 92),
# 		'scatter_radius':       (155, 94, 66),
# 		'scatter_radius_mult':  1.0,
# 		'phase_function':       0.8,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  0.5
# 	},
# 	'Skin_pink': {
# 		'ior':                  1.3,
# 		'diffuse_color':        (203, 169, 149),
# 		'sub_surface_color':    (203, 169, 149),
# 		'scatter_radius':       (177, 105, 84),
# 		'scatter_radius_mult':  1.0,
# 		'phase_function':       0.8,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  0.5
# 	},
# 	'Skin_yellow': {
# 		'ior':                  1.3,
# 		'diffuse_color':        (204, 165, 133),
# 		'sub_surface_color':    (204, 165, 133),
# 		'scatter_radius':       (177, 105, 84),
# 		'scatter_radius_mult':  1.0,
# 		'phase_function':       0.8,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  0.5
# 	},
# 	'Milk_skimmed': {
# 		'ior':                  1.3,
# 		'diffuse_color':        (230, 230, 210),
# 		'sub_surface_color':    (230, 230, 210),
# 		'scatter_radius':       (245, 184, 107),
# 		'scatter_radius_mult':  2.0,
# 		'phase_function':       0.8,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  0.8
# 	},
# 	'Milk_whole': {
# 		'ior':                  1.3,
# 		'diffuse_color':        (242, 239, 222),
# 		'sub_surface_color':    (242, 239, 222),
# 		'scatter_radius':       (188, 146,  90),
# 		'scatter_radius_mult':  2.0,
# 		'phase_function':       0.9,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  0.8
# 	},
# 	'Marble_white': {
# 		'ior':                  1.5,
# 		'diffuse_color':        (238, 233, 228),
# 		'sub_surface_color':    (238, 233, 228),
# 		'scatter_radius':       (235, 190, 160),
# 		'scatter_radius_mult':  1.0,
# 		'phase_function':       -0.25,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  0.7
# 	},
# 	'Ketchup': {
# 		'ior':                  1.3,
# 		'diffuse_color':        (102, 28,  0),
# 		'sub_surface_color':    (102, 28,  0),
# 		'scatter_radius':       (176, 62, 50),
# 		'scatter_radius_mult':  1.0,
# 		'phase_function':       0.9,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  0.7
# 	},
# 	'Cream': {
# 		'ior':                  1.3,
# 		'diffuse_color':        (224, 201, 117),
# 		'sub_surface_color':    (224, 201, 117),
# 		'scatter_radius':       (215, 153,  81),
# 		'scatter_radius_mult':  2.0,
# 		'phase_function':       0.8,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  0.6
# 	},
# 	'Potato': {
# 		'ior':                  1.3,
# 		'diffuse_color':        (224, 201, 117),
# 		'sub_surface_color':    (224, 201, 117),
# 		'scatter_radius':       (215, 153,  81),
# 		'scatter_radius_mult':  2.0,
# 		'phase_function':       0.8,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  0.8
# 	},
# 	'Spectration': {
# 		'ior':                  1.5,
# 		'diffuse_color':        (255, 255, 255),
# 		'sub_surface_color':    (255, 255, 255),
# 		'scatter_radius':       (  0,   0,   0),
# 		'scatter_radius_mult':  0.0,
# 		'phase_function':       0.0,
# 		'specular_amount':      0.0,
# 		'specular_glossiness':  0.0
# 	},
# 	'Water_clear': {
# 		'ior':                  1.3,
# 		'diffuse_color':        (  0,   0,   0),
# 		'sub_surface_color':    (  0,   0,   0),
# 		'scatter_radius':       (255, 255, 255),
# 		'scatter_radius_mult':  300.0,
# 		'phase_function':       0.95,
# 		'specular_amount':      1.0,
# 		'specular_glossiness':  1.0
# 	}
# }
# def generate_presets():
# 	for preset in SSS2:
# 		ofile= open("/home/bdancer/devel/vrayblender/exporter/vb25/presets/sss/%s.py"%(preset), 'w')
# 		ofile.write("import bpy\n")
# 		for param in SSS2[preset]:
# 			ps= SSS2[preset][param]
# 			if type(ps) == tuple:
# 				pss= ""
# 				for c in ps:
# 					pss+= "%.3f,"%(float(c / 255.0))
# 				ps= pss[:-1]
# 			s= "bpy.context.active_object.active_material.vray.BRDFSSS2Complex.%s = %s\n"%("%s"%(param), ps)
# 			ofile.write(s.replace(')','').replace('(',''))
# 		ofile.write("\n")
# 		ofile.close()
# generate_presets()

