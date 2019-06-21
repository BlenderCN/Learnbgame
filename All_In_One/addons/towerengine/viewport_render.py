
import bpy
from bgl import *
from mathutils import *
from .towerengine import *
from .mesh_converter import MeshConverter
from .material_converter import MaterialConverter
from math import atan, degrees



def vec_te(blender_vec):
	return tVec(blender_vec.x, blender_vec.z, -blender_vec.y)

def vec2_te(blender_vec2):
	return tVec(blender_vec2.x, blender_vec2.y)

def mat3_te(blender_mat):
	x = tVec(blender_mat[0][0], blender_mat[0][2], -blender_mat[0][1])
	y = tVec(blender_mat[2][0], blender_mat[2][2], -blender_mat[2][1])
	z = tVec(-blender_mat[1][0], -blender_mat[1][2], blender_mat[1][1])
	return tMatrix3(x, y, z)

def vec_bl(te_vec):
	return Vector((te_vec.x, -te_vec.z, te_vec.y))


class TowerEngineContext:
	def __init__(self, context):
		if tEngine_Init():
			print("Tower Engine initialized.")
		else:
			print("Failed to initialize Tower Engine.")
			return

		self.world = tWorld()
		self.renderer = tDefaultDeferredRenderer(context.region.width, context.region.height, self.world)
		self.camera = self.renderer.GetCamera()

		#self.renderer.InitSSAO(False, 16, 0.2)
		self.renderer.SetFXAAEnabled(True)

		self.camera.SetPosition(tVec(3.0, 3.0, 3.0))
		self.camera.SetDirection(tVec(-1.0, -1.0, -1.0))

		self.coordinate_system_object = tCoordinateSystemObject()
		self.world.AddObject(self.coordinate_system_object)

		self.skybox = tSkyBox()
		self.world.SetSkyBox(self.skybox)

		self.objects = {}
		self.meshes = {}
		self.materials = {}
		self.point_lights = {}

		self.objects_updated = {}
		self.meshes_updated = {}
		self.materials_updated = {}
		self.point_lights_updated = {}


	def update_material(self, m):
		if m in self.materials_updated:
			return self.materials_updated[m]

		if m in self.materials:
			tmaterial = self.materials[m]
		else:
			tmaterial = None

		converter = TowerEngineMaterialConverter(self, tmaterial)
		converter.execute(m)
		tmaterial = converter.tmaterial

		self.materials_updated[m] = tmaterial

		return tmaterial


	def __update_mesh(self, context, o):
		if len(o.modifiers) > 0: # TODO: use o.is_modified()
			mesh_id = (o.data, o)
		else:
			mesh_id = (o.data, None)

		if mesh_id in self.meshes_updated:
			return self.meshes_updated[mesh_id]

		if mesh_id in self.meshes:
			tmesh = self.meshes[mesh_id]
			tmesh.ClearTriangles()
			tmesh.ClearVertices()
		else:
			tmesh = None

		mesh = o.to_mesh(context.scene, True, "PREVIEW")
		converter = TowerEngineMeshConverter(self, tmesh)
		converter.add_mesh(mesh)
		converter.execute()
		tmesh = converter.tmesh

		self.meshes_updated[mesh_id] = tmesh

		return tmesh


	def __update_mesh_object(self, context, o):
		if o.towerengine.disable_mesh:
			return

		tmesh = self.__update_mesh(context, o)

		if o in self.objects:
			tobject = self.objects[o]
			tobject.SetMesh(tmesh)
		else:
			tobject = tMeshObject(tmesh)
			self.world.AddObject(tobject)

		ttransform = tTransform()
		ttransform.SetPosition(vec_te(o.location))
		ttransform.SetBasis(mat3_te(o.matrix_world))
		tobject.SetTransform(ttransform)

		self.objects_updated[o] = tobject


	def __update_point_light(self, context, o):
		if o in self.point_lights:
			tlight = self.point_lights[o]
		else:
			tlight = tPointLight()
			tlight.InitShadow(512, True)
			self.world.AddObject(tlight)

		lamp = o.data
		tlight.SetPosition(vec_te(o.location))
		tlight.SetColor(tVec(lamp.color[0] * lamp.energy, lamp.color[1] * lamp.energy, lamp.color[2] * lamp.energy))
		tlight.SetDistance(lamp.distance)

		self.point_lights_updated[o] = tlight



	def __update_skybox_test(self, context):
		cubemap_tex = None
		for texture_slot in context.scene.world.texture_slots.values():
			if texture_slot is None:
				continue

			tex = texture_slot.texture

			if tex.type != "ENVIRONMENT_MAP":
				continue

			if tex.image is None:
				continue

			if texture_slot.use_map_horizon:
				cubemap_tex = tex

		if cubemap_tex is not None and self.skybox.GetCubeMap() == 0:
			cubemap_tex.image.gl_load()
			cubemap_gl = LoadGLCubeMap(cubemap_tex.image.filepath_from_user())
			self.skybox.SetCubeMap(cubemap_gl)
		# else:
		#	self.skybox.SetCubeMap(0)


	def __update_cleanup(self):
		for o in self.objects:
			if o not in self.objects_updated:
				tobject = self.objects[o]
				self.world.RemoveObject(tobject)
				del tobject

		for o in self.point_lights:
			if o not in self.point_lights_updated:
				tlight = self.point_lights[o]
				self.world.RemovePointLight(tlight)
				del tlight

		#for m in self.materials:
		#	if m not in self.materials_updated:
		#		del self.materials[m]


	def update(self, context):
		self.objects_updated = {}
		self.meshes_updated = {}
		self.materials_updated = {}
		self.point_lights_updated = {}


		for o in context.scene.objects:
			if not o.is_visible(context.scene):
				continue

			visible = False
			for layer in range(len(context.scene.layers)):
				if context.scene.layers[layer] and o.layers[layer]:
					visible = True
					break

			if not visible:
				continue

			if o.type == "MESH":
				self.__update_mesh_object(context, o)
			elif o.type == "LAMP":
				self.__update_point_light(context, o)

		self.__update_skybox_test(context)

		self.__update_cleanup()

		self.objects = self.objects_updated
		self.meshes = self.meshes_updated
		self.materials = self.materials_updated
		self.point_lights = self.point_lights_updated



	def render(self, context):
		region = context.region
		region3d = context.region_data
		space = context.space_data

		viewport = [region.x, region.y, region.width, region.height]

		self.renderer.ChangeSize(viewport[2], viewport[3])

		sensor_width = 32
		lens = space.lens
		angle = degrees(2 * atan(sensor_width / (2 * lens)))

		aspect = float(viewport[2]) / float(viewport[3])
		self.camera.SetFOVVerticalAngle(angle, aspect)

		view_matrix = region3d.view_matrix
		view_matrix_inv = view_matrix.inverted()

		cam_pos = view_matrix_inv * Vector((0.0, 0.0, 0.0))
		cam_dir = (view_matrix_inv * Vector((0.0, 0.0, -1.0))) - cam_pos

		cam_pos_te = vec_te(cam_pos)
		self.camera.SetPosition(cam_pos_te)

		cam_dir_te = vec_te(cam_dir)
		cam_dir_te.Normalize()
		self.camera.SetDirection(cam_dir_te)

		glClearColor(0.0, 1.0, 0.0, 1.0)
		glClear(GL_COLOR_BUFFER_BIT)

		glDisable(GL_SCISSOR_TEST)
		self.renderer.Render(0, viewport[0], viewport[1], viewport[2], viewport[3])
		glEnable(GL_SCISSOR_TEST)



class TowerEngineMeshConverter(MeshConverter):
	def __init__(self, te_context, mesh=None):
		super().__init__()

		self.te_context = te_context

		self.tmesh = mesh
		self.materials = {}

		if not self.tmesh:
			self.tmesh = tMesh()
			self.tmesh.thisown = 0

	def _add_material(self, material):
		tmaterial = self.te_context.update_material(material)
		self.tmesh.AddMaterial(str(material.name), tmaterial)
		self.materials[material.name] = tmaterial

	def _finish_materials(self):
		# TODO: remove old materials
		pass

	def _add_vertex(self, vertex, uv, normal):
		tvertex = tVertex()
		tvertex.pos = vec_te(vertex.co)
		tvertex.normal = vec_te(normal)
		tvertex.uv = tVec(uv[0], uv[1])
		self.tmesh.AddVertex(tvertex)

	def _add_triangle(self, vertices, material):
		ttriangle = tTriangle()
		if material in self.materials:
			tmaterial = self.materials[material]
		else:
			tmaterial = self.tmesh.GetIdleMaterial()
		ttriangle.mat = tmaterial
		ttriangle.SetVertices(vertices[0], vertices[1], vertices[2])
		self.tmesh.AddTriangle(ttriangle)

	def _finish(self):
		self.tmesh.CalculateAllTangents()
		self.tmesh.GenerateAABB()


class TowerEngineMaterialConverter(MaterialConverter):
	def __init__(self, te_context, tmaterial=None):
		super().__init__()

		self.te_context = te_context

		self.tmaterial = tmaterial

	def __get_gl_tex(self, tex):
		gl_tex = 0
		if tex:
			if tex.image:
				try:
					tex.image.gl_load()
					gl_tex = tex.image.bindcode[0]
				except RuntimeError as error:
					print("Error loading image: {0}".format(error))
		return gl_tex


	def _create_default_material(self, name,
								 base_color_tex, base_color,
								 metal_rough_reflect_tex, metallic, roughness, reflectance,
								 normal_tex,
								 bump_tex, bump_depth,
								 emission_tex, emission_color,
								 cast_shadow):

		if self.tmaterial is None or not isinstance(self.tmaterial, tStandardMaterial):
			self.tmaterial = tStandardMaterial()


		self.tmaterial.SetOwnTextures(False)

		self.tmaterial.SetBaseColor(tVec(base_color.r, base_color.g, base_color.b))
		self.tmaterial.SetTexture(tStandardMaterial.BASE_COLOR, self.__get_gl_tex(base_color_tex))

		self.tmaterial.SetMetallic(metallic)
		self.tmaterial.SetRoughness(roughness)
		self.tmaterial.SetReflectance(reflectance)
		self.tmaterial.SetTexture(tStandardMaterial.METAL_ROUGH_REFLECT, self.__get_gl_tex(metal_rough_reflect_tex))

		self.tmaterial.SetTexture(tStandardMaterial.NORMAL, self.__get_gl_tex(normal_tex))

		self.tmaterial.SetBumpDepth(bump_depth)
		self.tmaterial.SetTexture(tStandardMaterial.BUMP, self.__get_gl_tex(bump_tex))

		self.tmaterial.SetEmission(tVec(emission_color[0], emission_color[1], emission_color[2]))
		self.tmaterial.SetTexture(tStandardMaterial.EMISSION, self.__get_gl_tex(emission_tex))

		self.tmaterial.UpdateUniformBuffer()


	def _create_simple_forward_material(self, name,
										color_tex, color, alpha,
										blend_mode):

		if self.tmaterial is None or not isinstance(self.tmaterial, tSimpleForwardMaterial):
			self.tmaterial = tSimpleForwardMaterial()

		self.tmaterial.SetOwnTextures(False)

		blend_modes = { "ALPHA": tSimpleForwardMaterial.ALPHA,
						"ADD": tSimpleForwardMaterial.ADD,
						"MULTIPLY": tSimpleForwardMaterial.MULTIPLY }
		self.tmaterial.SetBlendMode(blend_modes[blend_mode])

		self.tmaterial.SetColor(tVec(color.r, color.g, color.b), alpha)
		self.tmaterial.SetTexture(self.__get_gl_tex(color_tex))


	def _create_refraction_material(self, name,
									color_tex, color,
									edge_color,
									normal_tex):

		#if self.tmaterial is None or not isinstance(self.tmaterial, tRefractionMaterial):
		self.tmaterial = tRefractionMaterial()

		self.tmaterial.SetOwnTextures(False)

		self.tmaterial.SetColor(tVec(color.r, color.g, color.b))
		self.tmaterial.SetColorTexture(self.__get_gl_tex(color_tex))

		self.tmaterial.SetEdgeColor(tVec(edge_color[0], edge_color[1], edge_color[2]), edge_color[3])

		self.tmaterial.SetNormalTexture(self.__get_gl_tex(normal_tex))



te_context = None

def update(render_engine, context):
	global te_context
	if not te_context:
		te_context = TowerEngineContext(context)
	te_context.update(context)

def render(render_engine, context):
	global te_context
	te_context.render(context)