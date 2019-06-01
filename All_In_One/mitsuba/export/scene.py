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

import bpy, os, copy, subprocess, math, mathutils
import string

from math import radians
from extensions_framework import util as efutil

from ..export			import resolution
from ..export			import geometry		as export_geometry
from ..export			import is_obj_visible
#from mitsuba.export.volumes import smoke_convertion
#from ..export.volumes import smoke_convertion
#import volumes
#import mitsuba.export.volumes
from mitsuba.export.volumes import volumes

from ..outputs import MtsLog

class SceneExporter:
	
	def __init__(self, directory, filename, materials = None, textures = None):
		mts_basename = os.path.join(directory, filename)
		(path, ext) = os.path.splitext(mts_basename)
		if ext == '.xml':
			mts_basename = path
		self.xml_filename = mts_basename + ".xml"
		self.meshes_dir = os.path.join(directory, "meshes")
		self.exported_cameras = []
		self.exported_meshes = {}
		self.exported_materials = []
		self.exported_textures = []
		self.exported_media = []
		self.materials = materials if materials != None else bpy.data.materials
		self.textures = textures if textures != None else bpy.data.textures
		self.hemi_lights = 0
		self.indent = 0
		self.stack = []
		if directory[-1] != '/':
			directory += '/'
		self.output_directory = directory
		efutil.export_path = self.xml_filename
	
	def writeHeader(self):
		try:
			self.out = open(self.xml_filename, 'w', encoding='utf-8', newline="\n")
		except IOError:
			MtsLog('Error: unable to write to file \"%s\"!' % self.xml_filename)
			return False
		self.out.write('<?xml version="1.0" encoding="utf-8"?>\n');
		self.openElement('scene',{'version' : '0.4.1'})
		return True
	
	def writeFooter(self):
		self.closeElement()
		self.out.close()
	
	def openElement(self, name, attributes = {}):
		self.out.write('\t' * self.indent + '<%s' % name)
		for (k, v) in attributes.items():
			self.out.write(' %s=\"%s\"' % (k, v))
		self.out.write('>\n')
		self.indent = self.indent+1
		self.stack.append(name)
	
	def closeElement(self):
		self.indent = self.indent-1
		name = self.stack.pop()
		self.out.write('\t' * self.indent + '</%s>\n' % name)
	
	def element(self, name, attributes = {}):
		self.out.write('\t' * self.indent + '<%s' % name)
		for (k, v) in attributes.items():
			self.out.write(' %s=\"%s\"' % (k, v))
		self.out.write('/>\n')
	
	def parameter(self, paramType, paramName, attributes = {}):
		self.out.write('\t' * self.indent + '<%s name="%s"' % (paramType, paramName))
		for (k, v) in attributes.items():
			self.out.write(' %s=\"%s\"' % (k, v))
		self.out.write('/>\n')
	
	def exportMatrix(self, trafo):
		value = ""
		for j in range(0,4):
			for i in range(0,4):
				value += "%f " % trafo[j][i]	#2.62 matrix fix
		self.element('matrix', {'value' : value})
	
	def exportWorldTrafo(self, trafo):
		self.openElement('transform', {'name' : 'toWorld'})
		value = ""
		for j in range(0,4):
			for i in range(0,4):
				value += "%f " % trafo[j][i]	#2.62 matrix fix
		self.element('matrix', {'value' : value})
		self.closeElement()
	
	def exportPoint(self, location):
		self.parameter('point', 'center', {'x' : location[0],'y' : location[1],'z' : location[2]})
	
	def exportCyclesEnvmap(self, world):
		if(not("Environment Texture" in world.node_tree.nodes)):
			MtsLog("[INFO] No envirnoment texture found")
			return
		else:
			env = world.node_tree.nodes['Environment Texture']
			MtsLog("[INFO] Found env map: "+str(env.image.filepath))
			if(env.projection != 'EQUIRECTANGULAR'):
				MtsLog("[ERROR] Envmap: Other projection than EQUIRECTANGULAR is allowed")
				return
			
			self.hemi_lights += 1
	
			self.parameter('string', 'filename', {'value' : env.image.filepath})	
			self.openElement('transform', {'name' : 'toWorld'})
			self.element("rotate", {"x":"1", "y":"0", "z":"0", "angle":"90"})
			self.element("rotate", {"x":"0", "y":"0", "z":"1", "angle":"90"})
			self.closeElement()
			self.closeElement()
			
			MtsLog("[INFO] EnvMap OK")
			
	def exportLamp(self, scene, lamp):
		ltype = lamp.data.type
		name = lamp.name
		mult = lamp.data.mitsuba_lamp.intensity
		if lamp.data.mitsuba_lamp.inside_medium:
			self.exportMedium(scene.mitsuba_media.media[lamp.data.mitsuba_lamp.lamp_medium])
		if ltype == 'POINT':
			self.openElement('shape', { 'type' : 'sphere'})
			self.exportPoint(lamp.location)
			self.parameter('float', 'radius', {'value' : 7*lamp.data.mitsuba_lamp.radius})			#7*
			self.openElement('emitter', { 'id' : '%s-light' % name, 'type' : 'area'})
			self.parameter('rgb', 'radiance', { 'value' : "%f %f %f"
					% (lamp.data.color.r*mult, lamp.data.color.g*mult, lamp.data.color.b*mult)})
			self.parameter('float', 'samplingWeight', {'value' : '%f' % lamp.data.mitsuba_lamp.samplingWeight})
			if lamp.data.mitsuba_lamp.inside_medium:
				self.element('ref', {'id' : lamp.data.mitsuba_lamp.lamp_medium})
			self.closeElement()
			self.closeElement()
		elif ltype == 'AREA':
			self.openElement('shape', { 'type' : 'rectangle'} )
			self.parameter('boolean', 'flipNormals', {'value' : 'true'})
			(size_x, size_y) = (lamp.data.size/2.0, lamp.data.size/2.0)
			if lamp.data.shape == 'RECTANGLE':
				size_y = lamp.data.size_y/2.0
			self.openElement('transform', {'name' : 'toWorld'})
			loc, rot, sca = lamp.matrix_world.decompose()
			mat_loc = mathutils.Matrix.Translation(loc)
			mat_rot = rot.to_matrix().to_4x4()
			mat_sca = mathutils.Matrix((
				(sca[0]*size_x,0,0,0),
				(0,sca[1]*size_y,0,0),
				(0,0,sca[2],0),
				(0,0,0,1),
			))
			self.exportMatrix(mat_loc * mat_rot * mat_sca)
			self.closeElement()
			self.openElement('emitter', { 'id' : '%s-arealight' % name, 'type' : 'area'})
			self.parameter('rgb', 'radiance', { 'value' : "%f %f %f"
					% (lamp.data.color.r*mult, lamp.data.color.g*mult, lamp.data.color.b*mult)})
			self.parameter('float', 'samplingWeight', {'value' : '%f' % lamp.data.mitsuba_lamp.samplingWeight})
			if lamp.data.mitsuba_lamp.inside_medium:
				self.element('ref', {'id' : lamp.data.mitsuba_lamp.lamp_medium})
			self.closeElement()
			self.openElement('bsdf', { 'type' : 'diffuse'})
			self.parameter('spectrum', 'reflectance', {'value' : '0'})
			self.closeElement()
			self.closeElement()
		elif ltype == 'SUN':
			# sun is considered hemi light by Mitsuba
			if self.hemi_lights >= 1:
				# Mitsuba supports only one hemi light
				return False
			self.hemi_lights += 1
			invmatrix = lamp.matrix_world
			skyType = lamp.data.mitsuba_lamp.mitsuba_lamp_sun.sunsky_type
			LampParams = getattr(lamp.data.mitsuba_lamp, 'mitsuba_lamp_sun' ).get_paramset(lamp)
			if skyType == 'sunsky':
				self.openElement('emitter', { 'id' : '%s-light' % name, 'type' : 'sunsky'})
			elif skyType == 'sun':
				self.openElement('emitter', { 'id' : '%s-light' % name, 'type' : 'sun'})
			elif skyType == 'sky':
				self.openElement('emitter', { 'id' : '%s-light' % name, 'type' : 'sky'})
				#self.parameter('boolean', 'extend', {'value' : '%s' % str(lamp.data.mitsuba_lamp.mitsuba_lamp_sun.extend).lower()})
			LampParams.export(self)
			self.openElement('transform', {'name' : 'toWorld'})
			#rotate around x to make z UP. Default Y - UP
			self.element('rotate', {'x' : '1', 'angle' : '90'})
			self.closeElement()
			#self.exportWorldTrafo()
			#self.parameter('float', 'turbidity', {'value' : '%f' % (lamp.data.mitsuba_lamp.mitsuba_lamp_sun.turbidity)})
			#ot_mat = mathutils.Matrix.Scale(-1, 4, mathutils.Vector([0, 0, 1]))	#to make Z up rotate 90 around X
			#rotatedSun = invmatrix * mathutils.Matrix.Scale(-1, 4, mathutils.Vector([1, 0, 0])) * mathutils.Matrix.Scale(-1, 4, mathutils.Vector([0, 0, 1]))
			self.parameter('vector', 'sunDirection', {'x':'%f' % invmatrix[0][2], 'y':'%f' % invmatrix[1][2], 'z':'%f' % invmatrix[2][2]})
			self.closeElement()
			
		elif ltype == 'SPOT':
			self.openElement('emitter', { 'id' : '%s-light' % name, 'type' : 'spot'})
			self.exportWorldTrafo(lamp.matrix_world * mathutils.Matrix.Scale(-1, 4, mathutils.Vector([0, 0, 1])))
			self.parameter('rgb', 'intensity', { 'value' : "%f %f %f"
					% (lamp.data.color.r*mult, lamp.data.color.g*mult, lamp.data.color.b*mult)})
			self.parameter('float', 'cutoffAngle', {'value' : '%f' % (lamp.data.spot_size * 180 / (math.pi * 2))})
			self.parameter('float', 'beamWidth', {'value' : '%f' % ((1-lamp.data.spot_blend) * lamp.data.spot_size * 180 / (math.pi * 2))})
			self.parameter('float', 'samplingWeight', {'value' : '%f' % lamp.data.mitsuba_lamp.samplingWeight})
			if lamp.data.mitsuba_lamp.inside_medium:
				self.element('ref', {'id' : lamp.data.mitsuba_lamp.lamp_medium})
			self.closeElement()
		elif ltype == 'HEMI':
			if self.hemi_lights >= 1:
				# Mitsuba supports only one hemi light
				return False
			self.hemi_lights += 1
			if lamp.data.mitsuba_lamp.envmap_type == 'constant':
				self.openElement('emitter', { 'id' : '%s-light' % name, 'type' : 'constant'})
				self.parameter('float', 'samplingWeight', {'value' : '%f' % lamp.data.mitsuba_lamp.samplingWeight})
				self.parameter('rgb', 'radiance', { 'value' : "%f %f %f"
						% (lamp.data.color.r*mult, lamp.data.color.g*mult, lamp.data.color.b*mult)})
				self.closeElement()
			elif lamp.data.mitsuba_lamp.envmap_type == 'envmap':
				self.openElement('emitter', { 'id' : '%s-light' % name, 'type' : 'envmap'})
				self.parameter('string', 'filename', {'value' : efutil.filesystem_path(lamp.data.mitsuba_lamp.envmap_file)})
				self.exportWorldTrafo(lamp.matrix_world * mathutils.Matrix.Rotation(radians(90.0), 4, 'X'))
				self.parameter('float', 'scale', {'value' : '%f' % lamp.data.mitsuba_lamp.intensity})
				self.parameter('float', 'samplingWeight', {'value' : '%f' % lamp.data.mitsuba_lamp.samplingWeight})
				self.closeElement()
	
	def exportIntegrator(self, scene):
		pIndent = self.indent
		IntegParams = scene.mitsuba_integrator.get_params()
		if scene.mitsuba_adaptive.use_adaptive == True:
			AdpParams = scene.mitsuba_adaptive.get_params()
			self.openElement('integrator', { 'id' : 'adaptive', 'type' : 'adaptive'})
			AdpParams.export(self)
		if scene.mitsuba_irrcache.use_irrcache == True:
			IrrParams = scene.mitsuba_irrcache.get_params()
			self.openElement('integrator', { 'id' : 'irrcache', 'type' : 'irrcache'})
			IrrParams.export(self)
		self.openElement('integrator', { 'id' : 'integrator', 'type' : scene.mitsuba_integrator.type})
		IntegParams.export(self)
		while self.indent > pIndent:
			self.closeElement()
	
	def exportSampler(self, sampler, camera):
		samplerParams = sampler.get_params()
		mcam = camera.data.mitsuba_camera
		self.openElement('sampler', { 'id' : '%s-camera_sampler'% camera.name, 'type' : sampler.type})
		#self.parameter('integer', 'sampleCount', { 'value' : '%i' % sampler.sampleCount})
		samplerParams.export(self)
		self.closeElement()
	
	def findTexture(self, name):
		if name in self.textures:
			return self.textures[name]
		else:
			raise Exception('Failed to find texture "%s"' % name)
	
	def findMaterial(self, name):
		if name in self.materials:
			return self.materials[name]
		else:
			raise Exception('Failed to find material "%s" in "%s"' % (name,
				str(self.materials)))
	
	def exportTexture(self, tex):
		if tex.name in self.exported_textures:
			return
		self.exported_textures += [tex.name]
		params = tex.mitsuba_texture.get_params()
		
		for p in params:
			if p.type == 'reference_texture':
				self.exportTexture(self.findTexture(p.value))
		
		self.openElement('texture', {'id' : '%s' % tex.name, 'type' : tex.mitsuba_texture.type})
		params.export(self)
		self.closeElement()
	
	def exportBump(self, mat):
		mmat = mat.mitsuba_mat_bsdf
		self.openElement('bsdf', {'id' : '%s-material' % mat.name, 'type' : mmat.type})
		self.element('ref', {'name' : 'bump_ref', 'id' : '%s-material' % mmat.mitsuba_bsdf_bump.ref_name})
		self.openElement('texture', {'type' : 'scale'})
		self.parameter('float', 'scale', {'value' : '%f' % mmat.mitsuba_bsdf_bump.scale})		
		self.element('ref', {'name' : 'bump_ref', 'id' : mmat.mitsuba_bsdf_bump.bump_texturename})
		self.closeElement()
		self.closeElement()
	
	def exportMaterial(self, mat):
		if not hasattr(mat, 'name') or mat.name in self.exported_materials:
			return
		self.exported_materials += [mat.name]
		mmat = mat.mitsuba_mat_bsdf
		if mmat.type == 'none':
			self.element('null', {'id' : '%s-material' % mat.name})
			return
		
		params = mmat.get_params()
		
		for p in params:			
			if p.type == 'reference_material' and p.value != '':
				self.exportMaterial(self.findMaterial(p.value))
			elif p.type == 'reference_texture' and p.value != '':
				self.exportTexture(self.findTexture(p.value))
				
		if mat.mitsuba_mat_subsurface.use_subsurface:		
			msss = mat.mitsuba_mat_subsurface
			if msss.type == 'dipole':
				self.openElement('subsurface', {'id' : '%s-subsurface' % mat.name, 'type' : 'dipole'})
				sss_params = msss.get_params()
				sss_params.export(self)
				self.closeElement()				
		
		# Export Surface BSDF	
		if mat.mitsuba_mat_bsdf.use_bsdf:
			if mmat.type == 'bump':
				self.exportBump(mat)
			else:
				bsdf = getattr(mmat, 'mitsuba_bsdf_%s' % mmat.type)
				mtype = mmat.type
				if mmat.type == 'diffuse' and (bsdf.alpha > 0 or (bsdf.alpha_usetexture and bsdf.alpha_texturename != '')):
					mtype = 'roughdiffuse'
				elif mmat.type == 'dielectric' and bsdf.thin:
					mtype = 'thindielectric'
				elif mmat.type in ['dielectric', 'conductor', 'plastic', 'coating'] and bsdf.distribution != 'none':
					mtype = 'rough%s' % mmat.type


				needTwoSided = False
				twoSidedMatherial = ['diffuse','conductor','plastic','phong' ,'coating','ward','blendbsdf','mixturebsdf']
				
				if mmat.type in twoSidedMatherial:
					sub_type = getattr(mmat, 'mitsuba_bsdf_%s' % mmat.type)					
					needTwoSided = sub_type.use_two_sided_bsdf
				
				if (mmat.type in twoSidedMatherial) and needTwoSided:				
					self.openElement('bsdf', {'id' : '%s-material' % mat.name, 'type' : "twosided"})
					self.openElement('bsdf', {'type' : mtype})
				else :
					self.openElement('bsdf', {'id' : '%s-material' % mat.name, 'type' : mtype})
				
				params.export(self)
				
				if mmat.type == 'hg':
					if mmat.g == 0:
						self.element('phase', {'type' : 'isotropic'})
					else:
						self.openElement('phase', {'type' : 'hg'})
						self.parameter('float', 'g', {'value' : str(mmat.g)})
						self.closeElement()
				
						
				self.closeElement()
								
				if (mmat.type in twoSidedMatherial) and needTwoSided:				
					self.closeElement()	
													
				
	def exportMaterialEmitter(self, ob_mat):
		lamp = ob_mat.mitsuba_mat_emitter
		mult = lamp.intensity
		self.openElement('emitter', { 'type' : 'area'})
		self.parameter('float', 'samplingWeight', {'value' : '%f' % lamp.samplingWeight})
		self.parameter('rgb', 'radiance', { 'value' : "%f %f %f"
				% (lamp.color.r*mult, lamp.color.g*mult, lamp.color.b*mult)})
		self.closeElement()
	
	def exportMediumReference(self, role, mediumName):
		if mediumName == "":
			return
		#if obj.data.users > 1:
		#	MtsLog("Error: medium transitions cannot be instantiated (at least for now)!")
		#	return
		#self.exportMedium(scene.mitsuba_media.media[mediumName])
		if role == '':
			self.element('ref', { 'id' : mediumName})
		else:
			self.element('ref', { 'name' : role, 'id' : mediumName})
	
	def exportPreviewMesh(self, scene, material):
		mmat_bsdf = material.mitsuba_mat_bsdf
		mmat_subsurface = material.mitsuba_mat_subsurface
		mmat_medium = material.mitsuba_mat_extmedium
		mmat_emitter = material.mitsuba_mat_emitter
		
		self.openElement('shape', {'id' : 'Exterior-mesh_0', 'type' : 'serialized'})
		self.parameter('string', 'filename', {'value' : 'matpreview.serialized'})
		self.parameter('integer', 'shapeIndex', {'value' : '1'})
		self.openElement('transform', {'name' : 'toWorld'})
		self.element('matrix', {'value' : '0.614046 0.614047 0 -1.78814e-07 -0.614047 0.614046 0 2.08616e-07 0 0 0.868393 1.02569 0 0 0 1'})
		self.element('translate', { 'z' : '0.01'})
		self.closeElement()
		
		if mmat_bsdf.use_bsdf and mmat_bsdf.type != 'none':
			self.element('ref', {'name' : 'bsdf', 'id' : '%s-material' % material.name})
		
		if mmat_subsurface.use_subsurface:
			if mmat_subsurface.type == 'dipole':
				self.element('ref', {'name' : 'subsurface', 'id' : '%s-subsurface' % material.name})	
			elif mmat_subsurface.type == 'homogeneous':
				self.element('ref', {'name' : 'interior', 'id' : '%s-interior' % mmat_subsurface.mitsuba_sss_participating.interior_medium})		#change the name 
		
		if mmat_medium.use_extmedium:
			self.element('ref', {'name' : 'exterior', 'id' : '%s-exterior' % mmat_medium.mitsuba_extmed_participating.exterior_medium})			#change the name 
		
		if mmat_emitter.use_emitter:
			mult = mmat_emitter.intensity
			self.openElement('emitter', {'type' : 'area'})
			self.parameter('rgb', 'radiance', { 'value' : "%f %f %f"
					% (mmat_emitter.color.r*mult, mmat_emitter.color.g*mult, mmat_emitter.color.b*mult)})
			self.closeElement()
		
		self.closeElement()
	
	def exportFilm(self, scene, camera):
		film = camera.data.mitsuba_film
		filmParams = film.get_params()
		self.openElement('film', {'id' : '%s-camera_film' % camera.name,'type': film.type})
		[width,height] = resolution(scene)
		self.parameter('integer', 'width', {'value' : '%d' % width})
		self.parameter('integer', 'height', {'value' : '%d' % height})
		filmParams.export(self)
		if film.rfilter in ['gaussian', 'mitchell', 'lanczos']:
			self.openElement('rfilter', {'type': film.rfilter})
			if film.rfilter == 'gaussian':
				self.parameter('float', 'stddev', {'value' : '%f' % film.stddev})
			elif film.rfilter == 'mitchell':
				self.parameter('float', 'B', {'value' : '%f' % film.B})
				self.parameter('float', 'C', {'value' : '%f' % film.C})
			else:
				self.parameter('integer', 'lobes', {'value' : '%d' % film.lobes})
			self.closeElement() # closing rfilter element
		else:
			self.element('rfilter', {'type' : film.rfilter})
		self.closeElement() # closing film element
	
	def exportCamera(self, scene, camera):
		if camera.name in self.exported_cameras:
			return
		self.exported_cameras += [camera.name]
		mcam = camera.data.mitsuba_camera
		cam = camera.data
		# detect sensor type
		camType = 'orthographic' if cam.type == 'ORTHO' else 'spherical' if cam.type == 'PANO' else 'perspective'
		if mcam.useDOF == True:
			camType = 'telecentric' if cam.type == 'ORTHO' else 'thinlens'
		self.openElement('sensor', { 'id' : '%s-camera' % camera.name, 'type' : str(camType)})
		self.openElement('transform', {'name' : 'toWorld'})
		if cam.type == 'ORTHO':
			self.element('scale', { 'x' : cam.ortho_scale / 2.0, 'y' : cam.ortho_scale / 2.0})
		loc, rot, sca = camera.matrix_world.decompose()
		mat_loc = mathutils.Matrix.Translation(loc)
		mat_rot = rot.to_matrix().to_4x4()
		self.exportMatrix(mat_loc * mat_rot * mathutils.Matrix.Scale(-1, 4, mathutils.Vector([1, 0, 0])) * mathutils.Matrix.Scale(-1, 4, mathutils.Vector([0, 0, 1])))
		self.closeElement()
		if cam.type == 'PERSP':
			if cam.sensor_fit == 'VERTICAL':
				sensor = cam.sensor_height
				axis = 'y'
			else:
				sensor = cam.sensor_width
				axis = 'x'
			fov = math.degrees(2.0 * math.atan((sensor / 2.0) / cam.lens))
			self.parameter('float', 'fov', {'value' : fov})
			self.parameter('string', 'fovAxis', {'value' : axis})
		self.parameter('float', 'nearClip', {'value' : str(cam.clip_start)})
		self.parameter('float', 'farClip', {'value' : str(cam.clip_end)})
		if mcam.useDOF == True:
			self.parameter('float', 'apertureRadius', {'value' : str(mcam.apertureRadius)})
			self.parameter('float', 'focusDistance', {'value' : str(cam.dof_distance)})
		
		self.exportSampler(scene.mitsuba_sampler, camera)
		self.exportFilm(scene, camera)
		
		#if scene.mitsuba_integrator.motionblur:
		#	frameTime = 1.0/scene.render.fps
		#	shuttertime = scene.mitsuba_integrator.shuttertime
		#	shutterOpen = (scene.frame_current - shuttertime/2) * frameTime
		#	shutterClose = (scene.frame_current + shuttertime/2) * frameTime
		#	self.parameter('float', 'shutterOpen', {'value' : str(shutterOpen)})
		#	self.parameter('float', 'shutterClose', {'value' : str(shutterClose)})
		if mcam.exterior_medium != '':
			self.exportMediumReference("exterior", scene.mitsuba_media.media[mcam.exterior_medium].name)
		self.closeElement() # closing sensor element 
	
	def exportVoxelData(self,objName , scene):
		obj = None		
		try :
			obj = bpy.data.objects[objName]
		except :
			MtsLog("ERROR : assigning the object")
		# path where to put the VOXEL FILES	
		scene_filename = efutil.scene_filename()
		geo = bpy.path.clean_name(scene.name)				
		sc_fr = '%s/%s/%s/%05d' %(self.meshes_dir , scene_filename , geo , scene.frame_current)		
		if not os.path.exists(sc_fr):
			os.makedirs(sc_fr)
		# path to the .bphys file	
		dir_name = os.path.dirname(bpy.data.filepath) + "/blendcache_" + os.path.basename(bpy.data.filepath)[:-6]		
		cachname = ("/%s_%06d_00.bphys"%(obj.modifiers['Smoke'].domain_settings.point_cache.name ,scene.frame_current) )
		cachFile = dir_name + cachname		
		volume = volumes()	
		filenames = volume.smoke_convertion( MtsLog, cachFile, sc_fr, scene.frame_current, obj)
		return filenames
	
	def reexportVoxelDataCoordinates(self, file):
		obj = None
		# get the Boundig Box object
		#updateBoundinBoxCoorinates(file , obj)
		
	
	def exportMedium(self, medium , scene):
		voxels = ['','']
		if medium.name in self.exported_media:
			return
		self.exported_media += [medium.name]
		self.openElement('medium', {'id' : medium.name, 'type' : medium.type})
		if medium.type == 'heterogeneous':			
			self.parameter('string', 'method', {'value' : str(medium.metode)})			
			self.openElement('volume', {'name' : 'density','type' : 'gridvolume'})
			if medium.externalDensity :
				self.parameter('string', 'filename', {'value' : str(medium.density)})
				# if medium.rewrite :
				#	reexportVoxelDataCoordinates(medium.density)					
			else :	
				voxels = self.exportVoxelData(medium.object,scene)			
				self.parameter('string', 'filename', {'value' : voxels[0] })
			self.closeElement()					
		if medium.g == 0:
			self.element('phase', {'type' : 'isotropic'})
		else:
			self.openElement('phase', {'type' : 'hg'})
			self.parameter('float', 'g', {'value' : str(medium.g)})
			self.closeElement()
		if medium.type == 'homogeneous':
			params = medium.get_params()
			params.export(self)
		else :	# the heterogeneous	
			if not medium.albedo_usegridvolume :		
				self.openElement('volume', {'name' : 'albedo','type' : 'constvolume'})
				self.parameter('spectrum', 'value', {'value' : "%f, %f, %f" %(medium.albado_color.r ,medium.albado_color.g, medium.albado_color.b)})							
			else :
				self.openElement('volume', {'name' : 'albedo','type' : 'gridvolume'})
				self.parameter('string', 'filename', {'value' : str(voxels[1])})
			self.closeElement()	
			self.parameter('float', 'scale', {'value' : str(medium.scale)})
		self.closeElement()
	
	def isMaterialSafe(self, mat):
		if mat.mitsuba_mat_subsurface.use_subsurface:
			return False
		
		if mat.mitsuba_mat_extmedium.use_extmedium:
			return False
		
		if mat.mitsuba_mat_emitter.use_emitter:
			return False
		
		mmat = mat.mitsuba_mat_bsdf
		params = mmat.get_params()
		
		for p in params:
			if p.type == 'reference_material':
				if not self.isMaterialSafe(self.findMaterial(p.value)):
					return False
		
		return True
	
	def export(self, scene):
		if scene.mitsuba_engine.binary_path == '':
			MtsLog("Error: the Mitsuba binary path was not specified!")
			return False
		
		MtsLog('MtsBlend: Writing Mitsuba xml scene file to "%s"' % self.xml_filename)
		if not self.writeHeader():
			return False
		
		self.exportIntegrator(scene)
		
		# === Export all the Participating media
		for media in scene.mitsuba_media.media:
			self.exportMedium(media,scene)
		
		# === Always export all Cameras, active camera last
		allCameras = [cam for cam in scene.objects if cam.type == 'CAMERA' and cam.name != scene.camera.name]
		for camera in allCameras:
			self.exportCamera(scene, camera)
		self.exportCamera(scene, scene.camera)
		
		# === Get env map is its exist
		self.exportCyclesEnvmap(bpy.data.worlds['World'])
		
		# === Get all renderable LAMPS
		renderableLamps = [lmp for lmp in scene.objects if is_obj_visible(scene, lmp) and lmp.type == 'LAMP']
		for lamp in renderableLamps:
			self.exportLamp(scene, lamp)
		
		# === Export geometry
		GE = export_geometry.GeometryExporter(self, scene)
		GE.iterateScene(scene)
		
		self.writeFooter()
		
		return True
