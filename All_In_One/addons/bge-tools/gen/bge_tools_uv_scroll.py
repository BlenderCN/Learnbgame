# Raco's BGE Tools: UV Scroll v0.0.1

from bge import logic
from mathutils import Vector, Matrix

class UVScroll:
	
	def __init__(self, cont):
		
		# get references to the owner, mesh and material id
		# get sprite size and Vector coordinates from string property "sprites"
		# convert string property "sequence" to an array of valid id's
		# get data from string properties "spin", "loop" and "pingpong"
		# initialize direction, id and offset
		
		PROP_NAME_SPRITES = "sprites"
		PROP_NAME_SEQUENCE = "sequence"
		PROP_NAME_LOOP = "loop"
		PROP_NAME_PINGPONG = "pingpong"
		PROP_NAME_LINKED = "linked"
		
		ERR_MSG_ILLEGAL_VALUE = "UV Scroll Sequence contains illegal value:\t"
		ERR_MSG_OUT_OF_RANGE = "UV Scroll Sequence is out of range:\t"
		
		def get_mesh(self):
			mesh = self.own.meshes[0]
			try:
				base_obj = self.own.scene.objectsInactive[self.own.name]
			except KeyError:
				if self.own[PROP_NAME_LINKED]:
					return mesh
			if not hasattr(logic, "libnews"):
				logic.libnews = 0
			mesh_name = mesh.name
			new_mesh = logic.LibNew(mesh_name + str(logic.libnews), "Mesh", [mesh_name])[0]
			self.own.replaceMesh(new_mesh)
			logic.libnews += 1
			return new_mesh
			
		def get_mat_id(mesh, identifier="_UV"):
			
			# get the material(s) that will be affected
			# if needed you can change the identifier
			# if the identifier is not found, all materials on the mesh will be affected
			
			for mat_id in range(mesh.numMaterials):
				if identifier in mesh.getMaterialName(mat_id):
					return mat_id
			return -1
			
		def get_sprite_data(self):
			sprites = [int(i) for i in self.own[PROP_NAME_SPRITES].split(", ")]
			sprite_size = Vector([1 / sprites[i] for i in range(2)]).to_3d()
			sprite_coords = []
			for y in range(sprites[1]):
				for x in range(sprites[0]):
					sprite_coords.append(Vector([x * sprite_size[0], y * sprite_size[1]]).to_3d())
			return sprite_coords, sprite_size
			
		def get_sequence(string):
			
			def digit_in_range(s, len):
				if not s.isdigit():
					return "ValueError"
				d = int(s)
				if not d < len:
					return "IndexError"
				return d
				
			def digits_in_range(l, len):
				return [digit_in_range(s, len) for s in l]
				
			sequence = []
			num_sprites = len(self.sprite_coords)
			for s in [s for s in string.replace(" ", "").split(",") if s != ""]:
				if "-" in s:
					ds = digits_in_range(s.split("-"), num_sprites)
					if "ValueError" in ds:
						self.errors.append(ERR_MSG_ILLEGAL_VALUE + s)
					elif "IndexError" in ds:
						self.errors.append(ERR_MSG_OUT_OF_RANGE + s)
					else:
						first, last = ds
						dir = -1 if first > last else 1
						for i in range(first, last + dir, dir):
							sequence.append(i)
				elif "*" in s:
					ds = digits_in_range(s.split("*"), num_sprites)
					if "ValueError" in ds:
						self.errors.append(ERR_MSG_ILLEGAL_VALUE + s)
					elif "IndexError" in ds:
						self.errors.append(ERR_MSG_OUT_OF_RANGE + s)
					else:
						id, num = ds
						for i in range(num):
							sequence.append(id)
				else:
					d = digit_in_range(s, num_sprites)
					if d == "ValueError":
						self.errors.append(ERR_MSG_ILLEGAL_VALUE + s)
					elif d == "IndexError":
						self.errors.append(ERR_MSG_OUT_OF_RANGE + s)
					else:
						sequence.append(d)
						
			return sequence
			
		def get_properties(self):
			sequence = get_sequence(self.own[PROP_NAME_SEQUENCE])
			loop = self.own[PROP_NAME_LOOP]
			pingpong = self.own[PROP_NAME_PINGPONG]
			return sequence, loop, pingpong
		
		self.own = cont.owner
		self.errors = []
		self.sprite_coords, self.sprite_size = get_sprite_data(self)
		self.sequence, self.loop, self.pingpong = get_properties(self)
		
		if self.errors:
			err_msg = "ERROR:\t" + self.own.name
			for e in self.errors:
				err_msg += "\n\t-> " + e
			print(err_msg)
			return
			
		self.mesh = get_mesh(self)
		self.mat_id = get_mat_id(self.mesh)
		self.always = cont.sensors[0]
		self.num_sequence = len(self.sequence)
		self.extremes = [0, self.num_sequence - 1]
		self.direction = 1
		self.end = False
		self.id = 0
		self.offset = Matrix.Translation(self.sprite_coords[self.sequence[self.id]])
		
	def main(self):
		
		# if there is no id this means the sequence has come to a stop, return
		# scroll uv coordinates to offset
		# get the next id
		# calculate offset between current and next id
		# update current id
		
		def get_offset(self, next_id):
			if not self.sequence:
				return Matrix.Identity(4)
			current_coords = self.sprite_coords[self.sequence[self.id]]
			next_coords = self.sprite_coords[self.sequence[next_id]]
			return Matrix.Translation(next_coords - current_coords)

		def get_next_id(self):
			next_id = self.id + self.direction
			if next_id in self.extremes:
				if self.loop:
					if self.loop > 0:
						self.loop -= 1
					if self.pingpong:
						self.direction *= -1
				else:
					self.end = True
			elif next_id == self.num_sequence:
				next_id = 0
			return next_id
		
		if self.errors:
			return
			
		self.mesh.transformUV(self.mat_id, self.offset, 0)
		
		if self.end:
			self.always.usePosPulseMode = False
			return
			
		next_id = get_next_id(self)
		self.offset = get_offset(self, next_id)
		self.id = next_id
		
def main(cont):
	if not cont.sensors[0].positive:
		return
	own = cont.owner
	if "uv_scroll" not in own:
		own["uv_scroll"] = UVScroll(cont)
	own["uv_scroll"].main()
	