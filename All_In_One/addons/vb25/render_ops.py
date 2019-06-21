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


''' Python modules  '''
import os
import subprocess
import tempfile
import time
import zipfile
import urllib.request
import sys

''' Blender modules '''
import bpy
import bgl
import bmesh
from bpy.props import *

''' vb modules '''
import vb25.render
import vb25.proxy

from vb25.lib     import VRaySocket
from vb25.utils   import *
from vb25.plugins import *

from vb25.lib                 import VRayProxy
from vb25.lib.VRaySceneParser import GetMaterialsNames
from vb25.lib.VrmatParser     import GetXMLMaterialsNames


VRAYBLENDER_MENU_ITEM= "V-Ray"


'''
  SCRIPT AUTOUPDATE
'''
class VRAY_OT_update(bpy.types.Operator):
	bl_idname      = "vray.update"
	bl_label       = "Update Exporter"
	bl_description = "Update exporter from github"

	def execute(self, context):
		# Check if target dir is writable
		cur_vb25_dirpath = get_vray_exporter_path()

		if not os.access(cur_vb25_dirpath, os.W_OK):
			self.report({'ERROR'}, "Exporter directory is not writable!")
			return {'CANCELLED'}

		# Downloading file
		self.report({'INFO'}, "Downloading 'master' branch archive...")

		GIT_MASTER_URL = "https://github.com/bdancer/vb25/zipball/master"

		# devnote: urllib2 not available, urllib's fancyurlopener returns errors anyways (when connection is not available)
		# so this is a working 'ugly fix' that at leasts works. Sorry the ghetto fix.
		try:
			(filename, headers) = urllib.request.urlretrieve(GIT_MASTER_URL)
		except urllib.error.URLError:
			self.report({'ERROR'}, "Error retrieving the files! Check your connection!")
			return {'CANCELLED'}

		# Extracting archive
		update_dir = create_dir(os.path.join(tempfile.gettempdir(), "vb25_update"))
		try:
			ziparchive = zipfile.ZipFile(filename)
			ziparchive.extractall(update_dir)
			ziparchive.close()
		except:
			self.report({'ERROR'}, "Error unpacking the archive!")
			return {'CANCELLED'}

		new_vb25_dirpath = ""
		dirnames = os.listdir(update_dir)
		for dirname in dirnames:
			if dirname.startswith("bdancer-vb25-"):
				new_vb25_dirpath = os.path.join(update_dir, dirname)
				break
		if not new_vb25_dirpath:
			self.report({'ERROR'}, "Update files not found!")
			return {'CANCELLED'}

		# Copying new files
		debug(context.scene, "Copying new files...")
		if os.path.exists(cur_vb25_dirpath):
			if sys.platform == 'win32':
				for item in os.listdir(cur_vb25_dirpath):
					s = os.path.join(cur_vb25_dirpath, item)
					if os.path.isdir(s):
						os.system("rmdir /Q /S %s" % s)
					else:
						os.system("del /Q /F %s" % s)
			else:
				shutil.rmtree(cur_vb25_dirpath)

		copytree(new_vb25_dirpath, cur_vb25_dirpath)

		if os.path.exists(filename):
			self.report({'INFO'}, "Removing update archive: %s"%(filename))
			os.remove(filename)

		if os.path.exists(update_dir):
			self.report({'INFO'}, "Removing update unpack directory: %s"%(update_dir))
			shutil.rmtree(update_dir)

		self.report({'INFO'}, "V-Ray/Blender updated! Please, restart Blender!")

		return {'FINISHED'}




'''
  Camera operators
'''
class VRAY_OT_lens_shift(bpy.types.Operator):
	bl_idname=      'vray.lens_shift'
	bl_label=       "Get lens shift"
	bl_description= "Calculate lens shift"

	@classmethod
	def poll(cls, context):
		return (context.camera)

	def execute(self, context):
		VRayCamera=     context.camera.vray
		CameraPhysical= VRayCamera.CameraPhysical

		CameraPhysical.lens_shift= PLUGINS['CAMERA']['CameraPhysical'].get_lens_shift(context.object)

		return {'FINISHED'}



'''
  Effects operators
'''
class VRAY_OT_effect_add(bpy.types.Operator):
	bl_idname=      'vray.effect_add'
	bl_label=       "Add Effect"

	bl_description= "Add effect"

	def execute(self, context):
		VRayScene= context.scene.vray

		VRayEffects= VRayScene.VRayEffects
		VRayEffects.effects.add()
		VRayEffects.effects[-1].name= "Effect"

		return {'FINISHED'}



class VRAY_OT_effect_remove(bpy.types.Operator):
	bl_idname=      'vray.effect_remove'
	bl_label=       "Remove Effect"
	bl_description= "Remove effect"

	def execute(self, context):
		VRayScene= context.scene.vray

		VRayEffects= VRayScene.VRayEffects

		if VRayEffects.effects_selected >= 0:
			VRayEffects.effects.remove(VRayEffects.effects_selected)
			VRayEffects.effects_selected-= 1

		return {'FINISHED'}



class VRAY_OT_effect_up(bpy.types.Operator):
	bl_idname=      'vray.effect_up'
	bl_label=       "Move effect up"
	bl_description= "Move effect up"

	def execute(self, context):
		VRayScene= context.scene.vray

		VRayEffects= VRayScene.VRayEffects

		if VRayEffects.effects_selected <= 0:
			return {'CANCELLED'}

		VRayEffects.effects.move(VRayEffects.effects_selected,
								 VRayEffects.effects_selected - 1)
		VRayEffects.effects_selected-= 1

		return {'FINISHED'}



class VRAY_OT_effect_down(bpy.types.Operator):
	bl_idname=      'vray.effect_down'
	bl_label=       "Move effect down"
	bl_description= "Move effect down"

	def execute(self, context):
		VRayScene= context.scene.vray

		VRayEffects= VRayScene.VRayEffects

		if VRayEffects.effects_selected == len(VRayEffects.effects) - 1:
			return {'CANCELLED'}

		VRayEffects.effects.move(VRayEffects.effects_selected,
								 VRayEffects.effects_selected + 1)
		VRayEffects.effects_selected+= 1

		return {'FINISHED'}



'''
  Includer operators
'''

class VRAY_OT_includer_add(bpy.types.Operator):
	bl_idname=      'vray.includer_add'
	bl_label=       "Add Include"
	bl_description= "Add Include *.vrsene"

	def execute(self, context):
		vs= context.scene.vray
		module= vs.Includer

		module.nodes.add()
		module.nodes[-1].name= "Include Scene"

		return {'FINISHED'}




class VRAY_OT_includer_remove(bpy.types.Operator):
	bl_idname=      'vray.includer_remove'
	bl_label=       "Remove Include"
	bl_description= "Remove Include *.vrsene"

	def execute(self, context):
		vs= context.scene.vray
		module= vs.Includer

		if module.nodes_selected >= 0:
		   module.nodes.remove(module.nodes_selected)
		   module.nodes_selected-= 1

		return {'FINISHED'}


class VRAY_OT_includer_up(bpy.types.Operator):
	bl_idname=      'vray.includer_up'
	bl_label=       "Up Include"
	bl_description= "Up Include *.vrsene"

	def execute(self, context):
		vs= context.scene.vray
		module= vs.Includer

		if module.nodes_selected <= 0:
			return {'CANCELLED'}

		module.nodes.move(module.nodes_selected,
								 module.nodes_selected - 1)
		module.nodes_selected-= 1

		return {'FINISHED'}


class VRAY_OT_includer_down(bpy.types.Operator):
	bl_idname=      'vray.includer_down'
	bl_label=       "Down Include"
	bl_description= "Down Include *.vrsene"

	def execute(self, context):
		vs= context.scene.vray
		module= vs.Includer

		if module.nodes_selected <= 0:
			return {'CANCELLED'}

		module.nodes.move(module.nodes_selected,
								 module.nodes_selected + 1)
		module.nodes_selected+= 1

		return {'FINISHED'}



'''
  Material operators
'''
def active_node_mat(mat):
	if mat:
		mat_node= mat.active_node_material
		if mat_node:
			return mat_node
		else:
			return mat
	return None


def find_brdf_pointer(rna_pointer):
	if rna_pointer.brdf_selected >= 0 and rna_pointer.brdfs[rna_pointer.brdf_selected].type == 'BRDFLayered':
		return find_brdf_pointer(getattr(rna_pointer.brdfs[rna_pointer.brdf_selected], 'BRDFLayered'))
	return rna_pointer


class VRAY_OT_brdf_add(bpy.types.Operator):
	bl_idname=      'vray.brdf_add'
	bl_label=       "Add BRDF"
	bl_description= "Add BRDF"

	def execute(self, context):
		ma= active_node_mat(context.material)
		if ma:
			rna_pointer= ma.vray.BRDFLayered
			# rna_pointer= find_brdf_pointer(VRayMaterial)

			rna_pointer.brdfs.add()
			rna_pointer.brdfs[-1].name= "BRDF"

			return {'FINISHED'}

		return {'CANCELLED'}



class VRAY_OT_brdf_remove(bpy.types.Operator):
	bl_idname=      'vray.brdf_remove'
	bl_label=       "Remove BRDF"
	bl_description= "Remove BRDF"

	def execute(self, context):
		ma= active_node_mat(context.material)
		if ma:
			rna_pointer= ma.vray.BRDFLayered
			# rna_pointer= find_brdf_pointer(VRayMaterial)

			if rna_pointer.brdf_selected >= 0:
				rna_pointer.brdfs.remove(rna_pointer.brdf_selected)
				rna_pointer.brdf_selected-= 1

			return {'FINISHED'}

		return {'CANCELLED'}



class VRAY_OT_brdf_up(bpy.types.Operator):
	bl_idname=      'vray.brdf_up'
	bl_label=       "Move BRDF up"
	bl_description= "Move BRDF up"

	def execute(self, context):
		ma= active_node_mat(context.material)
		if ma:
			rna_pointer= ma.vray.BRDFLayered
			# rna_pointer= find_brdf_pointer(VRayMaterial)

			if rna_pointer.brdf_selected <= 0:
				return {'FINISHED'}

			rna_pointer.brdfs.move(rna_pointer.brdf_selected,
								   rna_pointer.brdf_selected - 1)
			rna_pointer.brdf_selected-= 1

			return {'FINISHED'}

		return {'CANCELLED'}



class VRAY_OT_brdf_down(bpy.types.Operator):
	bl_idname=      'vray.brdf_down'
	bl_label=       "Move BRDF down"
	bl_description= "Move BRDF down"

	def execute(self, context):
		ma= active_node_mat(context.material)
		if ma:
			rna_pointer= ma.vray.BRDFLayered
			# rna_pointer= find_brdf_pointer(VRayMaterial)

			if rna_pointer.brdf_selected == len(rna_pointer.brdfs) - 1:
				return {'FINISHED'}

			rna_pointer.brdfs.move(rna_pointer.brdf_selected,
								   rna_pointer.brdf_selected + 1)
			rna_pointer.brdf_selected+= 1

			return {'FINISHED'}



'''
  Render channel operators
'''
class VRAY_OT_channel_add(bpy.types.Operator):
	bl_idname=      'vray.render_channels_add'
	bl_label=       "Add Render Channel"
	bl_description= "Add render channel"

	def execute(self, context):
		sce= context.scene
		vsce= sce.vray

		render_channels= vsce.render_channels

		render_channels.add()
		render_channels[-1].name= "RenderChannel"

		return {'FINISHED'}



class VRAY_OT_channel_del(bpy.types.Operator):
	bl_idname=      'vray.render_channels_remove'
	bl_label=       "Remove Render Channel"
	bl_description= "Remove render channel"

	def execute(self, context):
		sce= context.scene
		vsce= sce.vray

		render_channels= vsce.render_channels

		if vsce.render_channels_index >= 0:
		   render_channels.remove(vsce.render_channels_index)
		   vsce.render_channels_index-= 1

		return {'FINISHED'}



'''
  DR node operators
'''
class VRAY_OT_node_add(bpy.types.Operator):
	bl_idname=      'vray.render_nodes_add'
	bl_label=       "Add Render Node"
	bl_description= "Add render node"

	def execute(self, context):
		vs= context.scene.vray
		module= vs.VRayDR

		module.nodes.add()
		module.nodes[-1].name= "Render Node"

		return {'FINISHED'}



class VRAY_OT_node_del(bpy.types.Operator):
	bl_idname=      'vray.render_nodes_remove'
	bl_label=       "Remove Render Node"
	bl_description= "Remove render node"

	def execute(self, context):
		vs= context.scene.vray
		module= vs.VRayDR

		if module.nodes_selected >= 0:
			module.nodes.remove(module.nodes_selected)
			module.nodes_selected -= 1

		if module.nodes_selected == -1 and len(module.nodes):
			module.nodes_selected = 0

		return {'FINISHED'}



class VRAY_OT_dr_nodes_load(bpy.types.Operator):
	bl_idname      = "vray.dr_nodes_load"
	bl_label       = "Load DR Nodes"
	bl_description = "Load distributed rendering nodes list"

	def execute(self, context):
		VRayScene = context.scene.vray
		VRayDR = VRayScene.VRayDR

		nodesFilepath = os.path.join(GetUserConfigDir(), "vray_render_nodes.txt")

		if not os.path.exists(nodesFilepath):
			return {'CANCELLED'}

		with open(nodesFilepath, 'r') as nodesFile:
			VRayDR.nodes.clear()

			for line in nodesFile.readlines():
				l = line.strip()
				if not l:
					continue

				item = VRayDR.nodes.add()
				item.name, item.address = l.split(":")

		VRayDR.nodes_selected = 0

		return {'FINISHED'}


class VRAY_OT_dr_nodes_save(bpy.types.Operator):
	bl_idname      = "vray.dr_nodes_save"
	bl_label       = "Save DR Nodes"
	bl_description = "Save distributed rendering nodes list"

	def execute(self, context):
		VRayScene = context.scene.vray
		VRayDR = VRayScene.VRayDR

		nodesFilepath = os.path.join(GetUserConfigDir(), "vray_render_nodes.txt")

		with open(nodesFilepath, 'w') as nodesFile:
			for item in VRayDR.nodes:
				nodesFile.write("%s:%s\n" % (item.name, item.address))

		return {'FINISHED'}



'''
  Some usefull utils
'''
class VRAY_OT_convert_scene(bpy.types.Operator):
	bl_idname      = "vray.convert_materials"
	bl_label       = "Convert materials"
	bl_description = "Convert scene materials from Blender Internal to V-Ray"

	CONVERT_BLEND_TYPE= {
		'MIX':          'OVER',
		'SCREEN':       'OVER',
		'DIVIDE':       'OVER',
		'HUE':          'OVER',
		'VALUE':        'OVER',
		'COLOR':        'OVER',
		'SOFT LIGHT':   'OVER',
		'LINEAR LIGHT': 'OVER',
		'OVERLAY':      'OVER',
		'ADD':          'ADD',
		'SUBTRACT':     'SUBTRACT',
		'MULTIPLY':     'MULTIPLY',
		'DIFFERENCE':   'DIFFERENCE',
		'DARKEN':       'DARKEN',
		'LIGHTEN':      'LIGHTEN',
		'SATURATION':   'SATURATE',
	}

	def execute(self, context):
		for ma in bpy.data.materials:
			debug(context.scene, "Converting material: %s" % ma.name)

			rm= ma.raytrace_mirror
			rt= ma.raytrace_transparency

			VRayMaterial= ma.vray
			BRDFVRayMtl=  VRayMaterial.BRDFVRayMtl

			BRDFVRayMtl.diffuse = ma.diffuse_color

			if ma.emit > 0.0:
				VRayMaterial.type= 'BRDFLight'

			if rm.use:
				BRDFVRayMtl.reflect_color= tuple([rm.reflect_factor]*3)
				BRDFVRayMtl.reflect_glossiness= rm.gloss_factor
				BRDFVRayMtl.reflect_subdivs= rm.gloss_samples
				BRDFVRayMtl.reflect_depth= rm.depth
				BRDFVRayMtl.option_cutoff= rm.gloss_threshold
				BRDFVRayMtl.anisotropy= 1.0 - rm.gloss_anisotropic

				if rm.fresnel > 0.0:
					BRDFVRayMtl.fresnel= True
					BRDFVRayMtl.fresnel_ior= rm.fresnel

			for slot in ma.texture_slots:
				if slot and slot.texture and slot.texture.type in TEX_TYPES:
					VRaySlot=    slot.texture.vray_slot
					VRayTexture= slot.texture.vray

					VRaySlot.blend_mode= self.CONVERT_BLEND_TYPE[slot.blend_type]

					if slot.use_map_emit:
						VRayMaterial.type= 'BRDFLight'

						VRaySlot.map_diffuse=  True

					if slot.use_map_normal:
						VRaySlot.map_normal=             True
						VRaySlot.BRDFBump.bump_tex_mult= slot.normal_factor

					if slot.use_map_color_diffuse:
						VRaySlot.map_diffuse=  True
						VRaySlot.diffuse_mult= slot.diffuse_color_factor

					if slot.use_map_raymir:
						VRaySlot.map_reflect=  True
						VRaySlot.reflect_mult= slot.raymir_factor

					if slot.use_map_alpha:
						VRaySlot.map_opacity=  True
						VRaySlot.opacity_mult= slot.alpha_factor

		return {'FINISHED'}




class VRAY_OT_bake_procedural(bpy.types.Operator):
	bl_idname=      'vray.bake_procedural'
	bl_label=       "Bake procedural"
	bl_description= "Render procedural texture to file"

	def execute(self, context):
		debug(context.scene, "Bake procedural: In progress...")
		return {'FINISHED'}




class VRAY_OT_settings_to_text(bpy.types.Operator):
	bl_idname=      'vray.settings_to_text'
	bl_label=       "Settings to Text"
	bl_description= "Export settings to Text"

	bb_code= BoolProperty(
		name= "Use BB-code",
		description= "Use BB-code formatting",
		default= True
	)

	def execute(self, context):

		text= bpy.data.texts.new(name="Settings")

		bus= {}
		bus['scene']= context.scene
		bus['preview']= False
		bus['files']= {}
		bus['files']['scene']= text
		bus['filenames']= {}
		bus['plugins']= PLUGINS
		bus['effects']= {}
		bus['effects']['fog']= {}
		bus['effects']['toon']= {}
		bus['effects']['toon']['effects']= []
		bus['effects']['toon']['objects']= []

		text.write("V-Ray/Blender 2.0 | Scene: %s | %s\n" % (context.scene.name,
															 time.strftime("%d %b %Y %H:%m:%S")))

		for key in PLUGINS['SETTINGS']:
			if key in ('BakeView', 'RenderView', 'SettingsEnvironment'):
				# Skip some plugins
				continue

			plugin= PLUGINS['SETTINGS'][key]
			if hasattr(plugin, 'write'):
				plugin.write(bus)

		return {'FINISHED'}



class VRAY_OT_flip_resolution(bpy.types.Operator):
	bl_idname      = "vray.flip_resolution"
	bl_label       = "Flip resolution"
	bl_description = "Flip render resolution"

	def execute(self, context):
		scene= context.scene
		rd=    scene.render

		VRayScene= scene.vray

		if VRayScene.image_aspect_lock:
			VRayScene.image_aspect= 1.0 / VRayScene.image_aspect

		rd.resolution_x, rd.resolution_y = rd.resolution_y, rd.resolution_x
		rd.pixel_aspect_x, rd.pixel_aspect_y = rd.pixel_aspect_y, rd.pixel_aspect_x

		return {'FINISHED'}


def LoadProxyMeshToObject(ob, filepath, anim_type, anim_offset, anim_speed, anim_frame):
	meshFile = VRayProxy.MeshFile(filepath)

	err = meshFile.readFile()
	if err is not None:
		return "Error parsing VRayProxy file!"

	meshData = meshFile.getPreviewMesh(anim_type, anim_offset, anim_speed, anim_frame)
	if meshData is None:
		return "Can't find preview voxel!"

	meshName = bpy.path.clean_name(os.path.basename(filepath))

	# Add new mesh
	mesh = bpy.data.meshes.new(meshName)
	mesh.from_pydata(meshData['vertices'], [], meshData['faces'])
	mesh.update()

	# Replace object's mesh
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bm.to_mesh(ob.data)
	ob.data.update()

	# Remove temp
	bm.free()
	bpy.data.meshes.remove(mesh)


class VRAY_OT_proxy_load_preview(bpy.types.Operator):
	bl_idname      = "vray.proxy_load_preview"
	bl_label       = "Load Preview"
	bl_description = "Load VRayProxy mesh preview from file"

	def execute(self, context):
		GeomMeshFile = context.object.data.vray.GeomMeshFile

		proxyFilepath = os.path.normpath(path_sep_to_unix(bpy.path.abspath(GeomMeshFile.file)))

		err = LoadProxyMeshToObject(
			context.object,
			proxyFilepath,
			GeomMeshFile.anim_type,
			GeomMeshFile.anim_offset,
			GeomMeshFile.anim_speed,
			context.scene.frame_current-1
		)

		if err is not None:
			self.report({'ERROR'}, err)
			return {'CANCELLED'}

		return {'FINISHED'}


class VRAY_OT_create_proxy(bpy.types.Operator):
	bl_idname      = "vray.create_proxy"
	bl_label       = "Create proxy"
	bl_description = "Creates proxy from selection"

	def execute(self, context):
		sce = context.scene

		VRayScene    = sce.vray
		VRayExporter = VRayScene.exporter

		@TimeIt("Proxy generated in")
		def _create_proxy(ob):
			if ob.type in {'LAMP', 'CAMERA', 'ARMATURE', 'LATTICE', 'EMPTY'}:
				return

			GeomMeshFile= ob.data.vray.GeomMeshFile

			vrmesh_filename= GeomMeshFile.filename if GeomMeshFile.filename else clean_string(ob.name)
			vrmesh_filename+= ".vrmesh"

			vrmesh_dirpath= bpy.path.abspath(GeomMeshFile.dirpath)
			if not os.path.exists(vrmesh_dirpath):
				os.mkdir(vrmesh_dirpath)
			vrmesh_filepath= os.path.join(vrmesh_dirpath,vrmesh_filename)

			if GeomMeshFile.animation:
				selected_frame= sce.frame_current

				frame_start= sce.frame_start
				frame_end= sce.frame_end
				if GeomMeshFile.animation_range == 'MANUAL':
					frame_start= GeomMeshFile.frame_start
					frame_end= GeomMeshFile.frame_end

				# Export first frame to create file
				frame= frame_start
				sce.frame_set(frame)
				vb25.proxy.generate_proxy(sce,ob,vrmesh_filepath)
				frame+= 1
				# Export all other frames
				while(frame <= frame_end):
					sce.frame_set(frame)
					vb25.proxy.generate_proxy(sce,ob,vrmesh_filepath,append=True)
					frame+= 1
				sce.frame_set(selected_frame)

			else:
				if VRayExporter.experimental:
					bpy.ops.vray.generate_vrayproxy(
						filepath = vrmesh_filepath,
					)
				else:
					vb25.proxy.generate_proxy(sce,ob,vrmesh_filepath)

			ob_name= ob.name
			ob_data_name= ob.data.name

			VRayMesh= ob.data.vray

			if GeomMeshFile.mode == 'NONE':
				return
			elif GeomMeshFile.mode in {'THIS', 'REPLACE'}:
				if GeomMeshFile.add_suffix:
					ob.name += '_proxy'

				# Override settings
				VRayMesh.override      = True
				VRayMesh.override_type = 'VRAYPROXY'
				GeomMeshFile.file = RelPath(vrmesh_filepath)

				# Load preview mesh
				if GeomMeshFile.mode == 'REPLACE':
					LoadProxyMeshToObject(
						ob,
						vrmesh_filepath,
						GeomMeshFile.anim_type,
						GeomMeshFile.anim_offset,
						GeomMeshFile.anim_speed,
						context.scene.frame_current-1
					)

					if GeomMeshFile.apply_transforms:
						ob.select= True
						sce.objects.active= ob
						bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

			elif GeomMeshFile.mode == 'NEW':
				# Create new object and copy materials
				new_ob= bpy.data.objects.new(ob_name+'_proxy', bpy.data.meshes.new(ob_name+'_proxy'))
				sce.objects.link(new_ob)
				new_ob.matrix_world= ob.matrix_world
				bpy.ops.object.select_all(action='DESELECT')
				new_ob.select= True
				sce.objects.active= new_ob

				LoadProxyMeshToObject(
					new_ob,
					vrmesh_filepath,
					GeomMeshFile.anim_type,
					GeomMeshFile.anim_offset,
					GeomMeshFile.anim_speed,
					context.scene.frame_current-1
				)

				for slot in ob.material_slots:
					if slot and slot.material:
						new_ob.data.materials.append(slot.material)

				if GeomMeshFile.apply_transforms:
					ob.select= True
					sce.objects.active= ob
					bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

				VRayMesh= new_ob.data.vray
				VRayMesh.override= True
				VRayMesh.override_type= 'VRAYPROXY'

				GeomMeshFile= VRayMesh.GeomMeshFile
				GeomMeshFile.file= RelPath(vrmesh_filepath)

		if len(bpy.context.selected_objects):
			for ob in bpy.context.selected_objects:
				_create_proxy(ob)
		else:
			_create_proxy(context.object)

		return {'FINISHED'}



'''
  EXPORT OPERATORS
'''
def init(context):
	scene= context.scene

	# Settings bus
	bus= {}

	# Plugins
	bus['plugins']= PLUGINS

	# Scene
	bus['scene']= scene

	# Preview
	bus['preview']= False

	# V-Ray uses UV indexes, Blender uses UV names
	# Here we store UV name->index map
	bus['uvs']= get_uv_layers_map(scene)

	# Output files
	bus['files']=     {}
	bus['filenames']= {}

	init_files(bus)

	return bus

class VRAY_OT_write_scene(bpy.types.Operator):
	bl_idname      = "vray.write_scene"
	bl_label       = "Export scene"
	bl_description = "Export scene to \"vrscene\" file"

	def execute(self, context):

		vb25.render.write_scene(init(context))

		return {'FINISHED'}



class VRAY_OT_write_geometry(bpy.types.Operator):
	bl_idname      = "vray.write_geometry"
	bl_label       = "Export meshes"
	bl_description = "Export meshes into vrscene file"

	dialog_width = 180

	def draw(self, context):
		layout = self.layout
		split = layout.split()
		col = split.column()
		col.label(text = "Animation mode is active!")
		col.label(text = "Are you sure to export meshes?")

	def invoke(self, context, event):
		wm    = context.window_manager
		scene = context.scene

		VRayScene    = scene.vray
		VRayExporter = VRayScene.exporter

		if not bpy.app.background:
			if VRayExporter.animation and VRayExporter.animation_type == 'FULL':
				return wm.invoke_props_dialog(self, self.dialog_width)

		return self.execute(context)

	def execute(self, context):

		vb25.render.write_geometry(init(context))

		return {'FINISHED'}



class VRAY_OT_write_vrscene(bpy.types.Operator):
	bl_idname      = "vray.write_vrscene"
	bl_label       = "Export Scene"
	bl_description = "Export scene into a *.vrscene files"

	def execute(self, context):
		bpy.ops.vray.export_vrscene()
		return {'FINISHED'}



class VRAY_OT_render(bpy.types.Operator):
	bl_idname      = "vray.render"
	bl_label       = "V-Ray Renderer"
	bl_description = "Render operator"

	def execute(self, context):
		scene = context.scene

		VRayScene    = scene.vray
		VRayExporter = VRayScene.exporter

		vb25.render.render(None, scene)

		return {'FINISHED'}



class VRAY_OT_run(bpy.types.Operator):
	bl_idname      = "vray.run"
	bl_label       = "Run V-Ray"
	bl_description = "Run V-Ray renderer"

	def execute(self, context):

		vb25.render.run(None, context.scene)

		return {'FINISHED'}



class VRAY_OT_terminate(bpy.types.Operator):
	bl_idname      = "vray.terminate"
	bl_label       = "Terminate VRayRT"
	bl_description = "Terminates running VRayRT instance"

	def execute(self, context):
		s = VRaySocket()
		s.connect()
		s.send("stop", result=False)
		s.send("quit", result=False)
		s.disconnect()

		return {'FINISHED'}



class VRAY_OT_set_kelvin_color(bpy.types.Operator):
	bl_idname      = "vray.set_kelvin_color"
	bl_label       = "Kelvin color"
	bl_description = "Set color temperature"

	data_path= StringProperty(
		name= "Data",
		description= "Data path",
		maxlen= 1024,
		default= ""
	)

	d_color= EnumProperty(
		name= "Illuminant series D",
		description= "Illuminant series D",
		items= (
			('D75',  "D75",  "North sky Daylight"),
			('D65',  "D65",  "Noon Daylight"),
			('D55',  "D55",  "Mid-morning / Mid-afternoon Daylight"),
			('D50',  "D50",  "Horizon Light"),
		),
		default= 'D50'
	)

	use_temperature= BoolProperty(
		name= "Use temperature",
		description= "Use temperature",
		default= False
	)

	temperature= IntProperty(
		name= "Temperature",
		description= "Kelvin temperature",
		min= 1000,
		max= 40000,
		step= 100,
		default= 5000
	)

	dialog_width= 150

	def draw(self, context):
		layout= self.layout

		if 0:
			row= layout.split().row(align= True)
			row.prop(self, 'use_temperature', text= "")
			if self.use_temperature:
				row.prop(self, 'temperature', text= "K")
			else:
				row.prop(self, 'd_color', text= "Type")
		else:
			split= layout.split()
			col= split.column()
			col.prop(self, 'd_color', text= "Type")
			sub= col.row(align= True)
			sub.prop(self, 'use_temperature', text= "")
			sub.prop(self, 'temperature', text= "K")

	def invoke(self, context, event):
		wm= context.window_manager
		return wm.invoke_props_dialog(self, self.dialog_width)

	def execute(self, context):
		D_COLOR= {
			'D75': 7500,
			'D65': 6500,
			'D55': 5500,
			'D50': 5000,
		}

		def recursive_attr(data, attrs):
			if not attrs:
				return data
			attr= attrs.pop()
			return recursive_attr(getattr(data, attr), attrs)

		if self.data_path:
			attrs= self.data_path.split('.')
			attr= attrs.pop() # Attribute to set
			attrs.reverse()

			data_pointer= recursive_attr(context, attrs)

			temperature= D_COLOR[self.d_color]

			if self.use_temperature:
				temperature= self.temperature

			setattr(data_pointer, attr, tuple(kelvin_to_rgb(temperature)))

		return {'FINISHED'}



class VRAY_OT_add_sky(bpy.types.Operator):
	bl_idname      = "vray.add_sky"
	bl_label       = "Add Sky texture"
	bl_description = "Add Sky texture to the background"

	def execute(self, context):
		scene= context.scene

		try:
			for i,slot in enumerate(scene.world.texture_slots):
				if not slot:
					tex= bpy.data.textures.new(name= 'VRaySky',
											   type= 'VRAY')
					tex.vray.type= 'TexSky'
					new_slot= scene.world.texture_slots.create(i)
					new_slot.texture= tex
					break
		except:
			debug(scene,
				  "Sky texture only availble in \"%s\"!" % color("Special build",'green'),
				  error= True)

		return {'FINISHED'}




'''
  LINK MATERIAL OVERRIDE
'''
class VRAY_OT_copy_linked_materials(bpy.types.Operator):
	bl_idname      = "vray.copy_linked_materials"
	bl_label       = "Copy linked materials"
	bl_description = "Copy linked materials"

	def execute(self, context):
		scene=  context.scene
		object= context.active_object

		if not object:
			debug(scene, "No object selected!", error= True)
			return {'CANCELLED'}

		if object.type == 'EMPTY':
			debug(scene, "Empty object type is not supported! Use simple mesh instead.", error= True)
			return {'CANCELLED'}

		if object.dupli_type == 'GROUP':
			object.dupli_list_create(scene)

			for dup_ob in object.dupli_list:
				ob= dup_ob.object
				for slot in ob.material_slots:
					ma= slot.material
					if ma:
						materials= [slot.material for slot in object.material_slots]
						if ma not in materials:
							debug(scene, "Adding material: %s" % (ma.name))
							object.data.materials.append(ma)

			object.dupli_list_clear()

			return {'FINISHED'}

		debug(scene, "Object \"%s\" has no dupli-group assigned!" % (object.name), error= True)
		return {'CANCELLED'}



'''
  RENDER ENGINE
'''
class VRayRenderer(bpy.types.RenderEngine):
	bl_idname      = 'VRAY_RENDER'
	bl_label       = "%s" % VRAYBLENDER_MENU_ITEM
	bl_use_preview =  False

	# def view_update(self, context):
	# 	pass

	# def view_draw(self, context):
	# 	w = context.region.width
	# 	h = context.region.height

	# 	bgl.glColor3f(1.0, 0.5, 0.0)
	# 	bgl.glRectf(0, 0, w, h)

	def render(self, scene):
		VRayScene= scene.vray
		VRayExporter= VRayScene.exporter

		err = vb25.render.render(self, scene)

		if err is not None:
			self.report({'ERROR'}, err)



class VRayRendererPreview(bpy.types.RenderEngine):
	bl_idname      = 'VRAY_RENDER_PREVIEW'
	bl_label       = "%s (material preview)" % VRAYBLENDER_MENU_ITEM
	bl_use_preview = True

	def render(self, scene):
		VRayScene    = scene.vray
		VRayExporter = VRayScene.exporter

		if scene.name == "preview":
			if scene.render.resolution_x < 64:
				return
			vb25.render.render(self, scene, preview=True)
		else:
			err = vb25.render.render(self, scene)

			if err is not None:
				self.report({'ERROR'}, err)


class VRayMaterialNameMenu(bpy.types.Menu):
	bl_label = "Select Material Name"
	bl_idname = "VRayMaterialNameMenu"

	ma_list = []

	def draw(self, context):
		row = self.layout.row()
		sub = row.column()
		
		for i,maName in enumerate(self.ma_list):
			if i and i % 15 == 0:
				sub = row.column()
			sub.operator("vray.set_vrscene_material_name", text=maName).name = maName


class VRaySetMaterialName(bpy.types.Operator):
	bl_idname      = "vray.set_vrscene_material_name"
	bl_label       = "Set Material Name"
	bl_description = "Set material name from *.vrscene file"

	name = bpy.props.StringProperty()

	def execute(self, context):
		ma = context.material

		VRayMaterial = ma.vray
		if not VRayMaterial.type == 'MtlVRmat':
			return {'CANCELLED'}

		MtlVRmat = VRayMaterial.MtlVRmat
		MtlVRmat.mtlname = self.name

		return {'FINISHED'}


class VRayGetMaterialName(bpy.types.Operator):
	bl_idname      = "vray.get_vrscene_material_name"
	bl_label       = "Get Material Name"
	bl_description = "Get material name from *.vrscene file"

	def execute(self, context):
		ma = context.material

		VRayMaterial = ma.vray
		if not VRayMaterial.type == 'MtlVRmat':
			return {'CANCELLED'}

		MtlVRmat = VRayMaterial.MtlVRmat
		if not MtlVRmat.filename:
			return {'CANCELLED'}

		filePath = get_path(MtlVRmat.filename)
		if not os.path.exists(filePath):
			return {'CANCELLED'}

		if filePath.endswith(".vrscene"):
			VRayMaterialNameMenu.ma_list = GetMaterialsNames(filePath)
		else:
			VRayMaterialNameMenu.ma_list = GetXMLMaterialsNames(filePath)

		bpy.ops.wm.call_menu(name=VRayMaterialNameMenu.bl_idname)

		return {'FINISHED'}


def GetRegClasses():
	return (
		VRayMaterialNameMenu,
		VRayGetMaterialName,
		VRaySetMaterialName,
		VRAY_OT_update,
		VRAY_OT_lens_shift,
		VRAY_OT_effect_add,
		VRAY_OT_effect_remove,
		VRAY_OT_effect_up,
		VRAY_OT_effect_down,
		VRAY_OT_includer_add,
		VRAY_OT_includer_remove,
		VRAY_OT_includer_up,
		VRAY_OT_includer_down,
		VRAY_OT_brdf_add,
		VRAY_OT_brdf_remove,
		VRAY_OT_brdf_up,
		VRAY_OT_brdf_down,
		VRAY_OT_channel_add,
		VRAY_OT_channel_del,
		VRAY_OT_node_add,
		VRAY_OT_node_del,
		VRAY_OT_dr_nodes_load,
		VRAY_OT_dr_nodes_save,
		VRAY_OT_convert_scene,
		VRAY_OT_bake_procedural,
		VRAY_OT_settings_to_text,
		VRAY_OT_flip_resolution,
		VRAY_OT_proxy_load_preview,
		VRAY_OT_create_proxy,
		VRAY_OT_write_scene,
		VRAY_OT_write_geometry,
		VRAY_OT_write_vrscene,
		VRAY_OT_render,
		VRAY_OT_run,
		VRAY_OT_terminate,
		VRAY_OT_set_kelvin_color,
		VRAY_OT_add_sky,
		VRAY_OT_copy_linked_materials,
		VRayRenderer,
		VRayRendererPreview,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
