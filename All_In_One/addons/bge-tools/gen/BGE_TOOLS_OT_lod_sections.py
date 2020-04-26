import bge, os, pickle

PROP_NAME = "BGE_TOOLS_LOD_SECTIONS"
PHYSICS_SUFFIX = "_PHYSICS"
LOD_SUFFIX = "_LOD"

class LODSections(bge.types.KX_GameObject):
	
	sections = []
	active_sections = []
	
	def __init__(self, own):
		self.visible = False
		normals_data = self.copy_custom_normals()
		self.sections = self.add_sections(normals_data)
		
	def copy_custom_normals(self):
		if not (PROP_NAME in self and self[PROP_NAME]):
			return
			
		dir_path = bge.logic.expandPath("//" + PROP_NAME)
		if not os.path.exists(dir_path):
			print("Warning:", dir_path, "does not exist.")
			
		file_path = os.path.join(dir_path, self.name + ".txt")
		with open(file_path, "rb") as f:
			normals_data = pickle.load(f)
			
		for ob_name, ob_normals in normals_data.items():
			ob = self.scene.objectsInactive[ob_name]
			mesh = ob.meshes[0]
			
			for mat_id in range(mesh.numMaterials):
				for vert_id in range(mesh.getVertexArrayLength(mat_id)):
					vert = mesh.getVertex(mat_id, vert_id)
					id = str([round(f) for f in vert.XYZ.xy])
					if id in ob_normals:
						vert.normal = ob_normals[id]
						
		return normals_data
		
	def add_sections(self, normals_data):
		sections = []
		for ob_name in normals_data:
			if LOD_SUFFIX in ob_name:
				continue
			inst = self.scene.addObject(ob_name)
			inst.setParent(self, False, False)
			inst.localTransform = self.localTransform * inst.localTransform
			sections.append(inst)
			
		return sections
		
	def update(self):
		active_sections = [sect.name for sect in self.sections if sect.currentLodLevel == 1]
		for sect in list(self.active_sections):
			if sect not in active_sections:
				self.active_sections.remove(sect)
				self.scene.objects[sect + PHYSICS_SUFFIX].endObject()
		for sect in active_sections:
			if sect not in self.active_sections:
				self.active_sections.append(sect)
				inst = self.scene.addObject(sect + PHYSICS_SUFFIX)
				inst.localTransform = self.localTransform * inst.localTransform
				
def get_mutated(cls, cont):
	obj = cont.owner
	if isinstance(obj, cls):
		return obj
		
	mutated_obj = cls(obj)
	assert(obj is not mutated_obj)
	assert(obj.invalid)
	assert(mutated_obj is cont.owner)
	
	return mutated_obj
	
def update(cont):
	lod_sections = get_mutated(LODSections, cont)
	lod_sections.update()
	