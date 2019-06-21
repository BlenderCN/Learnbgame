# Raco's BGE Tools: UV Transform v0.0.1

from mathutils import Vector, Matrix
from math import radians

class UVTransform:
	
	def get_object(self, name):
		try:
			return self.own.scene.objects[name]
		except KeyError:
			return None
			
	def get_ref_obj_trans(self):
		loc, rot, sca = self.ref_obj.worldTransform.decompose()
		translation = Matrix.Translation(loc)
		origin = self.ref_obj_offset * translation
		origin_inv = origin.inverted()
		rotation = origin * rot.to_matrix().to_4x4() * origin_inv
		scaling = origin * Matrix.Scale(sca.x, 4, (1, 0, 0)) * Matrix.Scale(sca.y, 4, (0, 1, 0)) * origin_inv
		return translation.inverted() * rotation.inverted() * scaling.inverted()
		
	def __init__(self, cont):
		
		# get references to the owner, mesh, material id and skipped tics
		
		def get_mat_id(mesh, identifier="_UV"):
			
			# get the material(s) that will be affected
			# if needed you can change the identifier
			# if the identifier is not found, all materials on the mesh will be affected
			
			for mat_id in range(mesh.numMaterials):
				if identifier in mesh.getMaterialName(mat_id):
					return mat_id
			return -1
			
		self.own = cont.owner
		self.mesh = self.own.meshes[0]
		self.mat_id = get_mat_id(self.mesh)
		self.always = cont.sensors[0]
		self.skipped = self.always.skippedTicks
		
		self.ref_obj = self.get_object(self.own["ref_obj_name"])
		self.ref_obj_offset = Matrix.Translation(Vector((0.5, 0.5, 0))) * self.own.worldTransform.inverted() * self.ref_obj.worldTransform
		if self.ref_obj:
			ref_obj_trans = self.get_ref_obj_trans()
			self.ref_obj_trans = ref_obj_trans
		else:
			self.ref_obj_trans = Matrix.Identity(4)
			
	def get_transform(self, props):
		loop, direction, timer, speed, time, pingpong = props
		transform = speed * direction
		if timer == time - 1:
			if loop > 0:
				loop -= 1
			if pingpong:
				direction *= -1
			timer = 0
		else:
			timer += 1
		return transform, loop, direction, timer
	
	# if movement over time and the loop is not finished, use its matrix for transformation
	# update centers for rotating and scaling
	# if rotating over time and the loop is not finished, add rotate to the matrix on center
	# if scaling over time and the loop is not finished, add scale to the matrix on center
	# transform uv coordinates to the matrix
		
	def main(self):
		self.ref_obj = self.get_object(self.own["ref_obj_name"])
		if self.ref_obj:
			ref_obj_trans = self.get_ref_obj_trans()
			ref_obj_delta = ref_obj_trans * self.ref_obj_trans.inverted()
			self.ref_obj_trans = ref_obj_trans
		else:
			ref_obj_delta = Matrix.Identity(4)
			
		translation_delta = Matrix.Translation(Vector((self.own["lin_vel_x"], self.own["lin_vel_y"], 0)))
		origin = Matrix.Translation(Vector((self.own["origin_x"], self.own["origin_y"], 0)))
		rotation_delta = origin * Matrix.Rotation(self.own["ang_speed"], 4, "Z") * origin.inverted()
		matrix = ref_obj_delta * translation_delta * rotation_delta
		
		self.mesh.transformUV(self.mat_id, matrix, 0)
		
def main(cont):
	if not cont.sensors[0].positive:
		return
	own = cont.owner
	if "uv_transform" not in own:
		own["uv_transform"] = UVTransform(cont)
	own["uv_transform"].main()
	