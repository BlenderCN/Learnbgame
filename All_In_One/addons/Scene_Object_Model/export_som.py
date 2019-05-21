import bpy
import math
import bmesh
bonesCount = 0
def write(filepath,
			applyMods=False
			):
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
	bpy.ops.object.select_all(action='DESELECT')
	scene = bpy.context.scene
	meshData = MeshData()
	animsData = []
	bones = []
	for obj in bpy.context.visible_objects:
		if obj.pose is not None:
			for bone in obj.pose.bones:
				bones.append(bone)
	global bonesCount
	bonesCount = len(bones)
	for obj in bpy.context.visible_objects:
		if applyMods or obj.type != "MESH":
			try:
				me = obj.to_mesh(scene, True, "PREVIEW")
			except:
				me = None
			is_tmp_mesh = True
		else:
			try:
				me = obj.to_mesh(scene, False, "PREVIEW")
			except:
				me = None
			is_tmp_mesh = True
		if obj.animation_data is not None:
			for track in obj.animation_data.nla_tracks:
				for strip in track.strips:
					action = strip.action
					obj.animation_data.action = action
					animData = AnimData(action.name)
					for i in range(int(action.frame_range[0]), int(action.frame_range[1])):
						bpy.context.scene.frame_set(i)
						bpy.context.scene.update()
						for bone in bones:
							animData.addB_Position(bone.head)
							bone.rotation_mode = 'XYZ'
							animData.addB_Rotation(bone.rotation_euler)
							animData.addB_Scale(bone.scale)
					animsData.append(animData)  
		if me is not None:
			bm = bmesh.new()
			bm.from_mesh(me)
			#bmesh.ops.subdivide_edges(bm, edges=bm.edges, use_grid_fill=True, cuts=1)
			bmesh.ops.triangulate(bm, faces=bm.faces)
			bm.to_mesh(me)
			bm.free()
			del bm
			for vertex in me.vertices:
				found = 0
				for group in vertex.groups:
					i = 0
					for bone in bones:
						if obj.vertex_groups[group.group].name == bone.name:
							found = i
						i+=1
				meshData.addV_Position(vertex.co)
				meshData.addV_Normal(vertex.normal)
				meshData.addV_Bone(found)
				# empty value as place for material index later
				meshData.addV_Material(0)
			for polygon in me.polygons:
				meshData.addF_Vertex(polygon)
				meshData.addF_Material(polygon)
				meshData.addF_UVs(polygon, me)
			meshData.setF_Count(meshData.fCount + len(me.polygons))
			meshData.setV_Count(meshData.vCount + len(me.vertices))
			meshData.setM_Count(meshData.mCount + len(obj.material_slots))
			for mat_slot in obj.material_slots:
				meshData.addM_Color(mat_slot)  	  
			if is_tmp_mesh:
				bpy.data.meshes.remove(me)
	writeToFile(filepath, meshData, animsData)

def writeToFile(filepath, meshData, animsData):
	# open target file
	file = open(filepath, "w")
	i = 0
	# write the commons to the file
	commons = "".join("SOM (Scene Object Model) file created by Blender SOM exporter"
			+ "\n" + "project page: https://github.com/JohnsProject/JPGE2" + "\n")
	file.write(commons)
	# write the vertex data to the file
	i = 0
	file.write("vCount < " + str(meshData.vCount) + " > vCount" + "\n")
	file.write("vPosition < ")
	for value in meshData.vPosition:
		i += 1
		if (i < len(meshData.vPosition)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > vPosition" + "\n")
	i = 0
	file.write("vNormal < ")
	for value in meshData.vNormal:
		i += 1
		if (i < len(meshData.vNormal)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > vNormal" + "\n")
	i = 0
	file.write("vBone < ")
	for value in meshData.vBone:
		i += 1
		if (i < len(meshData.vBone)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > vBone" + "\n")
	i = 0
	file.write("vMaterial < ")
	for value in meshData.vMaterial:
		i += 1
		if (i < len(meshData.vMaterial)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > vMaterial" + "\n")
	file.write("\n")
	# write the face data to the file
	i = 0
	file.write("fCount < " + str(meshData.fCount) + " > fCount" + "\n")
	file.write("fVertex1 < ")
	for value in meshData.fVertex1:
		i += 1
		if (i < len(meshData.fVertex1)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > fVertex1" + "\n")
	i = 0
	file.write("fVertex2 < ")
	for value in meshData.fVertex2:
		i += 1
		if (i < len(meshData.fVertex2)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > fVertex2" + "\n")
	i = 0
	file.write("fVertex3 < ")
	for value in meshData.fVertex3:
		i += 1
		if (i < len(meshData.fVertex3)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > fVertex3" + "\n")
	i = 0
	file.write("fMaterial < ")
	for value in meshData.fMaterial:
		i += 1
		if (i < len(meshData.fMaterial)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > fMaterial" + "\n")
	i = 0
	file.write("fUV1 < ")
	for value in meshData.fUV1:
		i += 1
		if (i < len(meshData.fUV1)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > fUV1" + "\n")
	i = 0
	file.write("fUV2 < ")
	for value in meshData.fUV2:
		i += 1
		if (i < len(meshData.fUV2)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > fUV2" + "\n")
	i = 0
	file.write("fUV3 < ")
	for value in meshData.fUV3:
		i += 1
		if (i < len(meshData.fUV3)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	file.write(" > fUV3" + "\n")
	file.write("\n")
	# write the material data to the file
	i = 0
	file.write("mCount < " + str(meshData.mCount) + " > mCount" + "\n")
	file.write("mColor < ")
	for value in meshData.mColor:
		i += 1
		if (i < len(meshData.mColor)):
			file.write("%f," % value)
		else:
			file.write(("%f" % value))
	
	file.write(" > mColor" + "\n")
	file.write("\n")
	# write the animations to the file
	file.write("Animations < " + "\n")
	global bonesCount
	file.write((" BonesCount <%f" % bonesCount) + "> BonesCount \n")
	for animData in animsData:
		file.write(" Animation < " + "\n")
		file.write("  Name < " + animData.name + "> Name \n")
		i = 0
		file.write("  bPosition < ")
		for value in animData.bPosition:
			i += 1
			if (i < len(animData.bPosition)):
				file.write("%f," % value)
			else:
				file.write(("%f" % value))
		
		file.write(" > bPosition" + "\n")
		i = 0
		file.write("  bRotation < ")
		for value in animData.bRotation:
			i += 1
			if (i < len(animData.bRotation)):
				file.write("%f," % value)
			else:
				file.write(("%f" % value))
		
		file.write(" > bRotation" + "\n")
		i = 0
		file.write("  bScale < ")
		for value in animData.bScale:
			i += 1
			if (i < len(animData.bScale)):
				file.write("%f," % value)
			else:
				file.write(("%f" % value))
		
		file.write(" > bScale" + "\n")
		file.write(" > Animation " + "\n")
	file.write("> Animations" + "\n")
	
	# close file
	file.close()
class MeshData:
	def __init__(self):
		# v = vertex
		self.vCount = 0
		self.vPosition = []
		self.vNormal = []
		self.vBone = []
		self.vMaterial = []
		# f = face
		self.fCount = 0
		self.fVertex1 = []
		self.fVertex2 = []
		self.fVertex3 = []
		self.fMaterial = []
		self.fUV1 = []
		self.fUV2 = []
		self.fUV3 = []
		# m = material
		self.mCount = 0
		self.mColor = []
	
	def setV_Count(self, value):
		self.vCount = value
		
	def addV_Position(self, value):
		self.vPosition.append(value[0])
		self.vPosition.append(value[1])
		self.vPosition.append(value[2])
		
	def addV_Normal(self, value):
		self.vNormal.append(value[0])
		self.vNormal.append(value[1])
		self.vNormal.append(value[2])
		
	def addV_Bone(self, value):
		self.vBone.append(value)
		
	def addV_Material(self, value):
		self.vMaterial.append(value)
		
	def setF_Count(self, value):
		self.fCount = value

	def addF_Vertex(self, value):
		self.fVertex1.append(self.vCount + value.vertices[0])
		self.fVertex2.append(self.vCount + value.vertices[1])
		self.fVertex3.append(self.vCount + value.vertices[2])
		
	def addF_Material(self, value):
		self.fMaterial.append(self.mCount  + value.material_index)
		self.vMaterial[value.vertices[0]] = self.mCount + value.material_index
		self.vMaterial[value.vertices[1]] = self.mCount + value.material_index
		self.vMaterial[value.vertices[2]] = self.mCount + value.material_index
		
	
	def addF_UVs(self, value, me):
		if me.uv_layers.active is not None:
			self.fUV1.append(me.uv_layers.active.data[value.loop_indices[0]].uv[0])
			self.fUV1.append(me.uv_layers.active.data[value.loop_indices[0]].uv[1])
			self.fUV2.append(me.uv_layers.active.data[value.loop_indices[1]].uv[0])
			self.fUV2.append(me.uv_layers.active.data[value.loop_indices[1]].uv[1])
			self.fUV3.append(me.uv_layers.active.data[value.loop_indices[2]].uv[0])
			self.fUV3.append(me.uv_layers.active.data[value.loop_indices[2]].uv[1])
		else:
			self.fUV1.append(0)
			self.fUV1.append(0)
			self.fUV2.append(0)
			self.fUV2.append(0)
			self.fUV3.append(0)
			self.fUV3.append(0)
	
	def setM_Count(self, value):
		self.mCount = value

	def addM_Color(self, value):
		if value.material is not None:
			self.mColor.append(value.material.diffuse_color[0] * 255)
			self.mColor.append(value.material.diffuse_color[1] * 255)
			self.mColor.append(value.material.diffuse_color[2] * 255)
			self.mColor.append(value.material.alpha * 255)
		else:
			self.mColor.append(0)
			self.mColor.append(0)
			self.mColor.append(0)
			self.mColor.append(100)

class AnimData:
	def __init__(self, name):
		self.name = name
		self.bPosition = []
		self.bRotation = []
		self.bScale = []

	def addB_Position(self, value):
		self.bPosition.append(value[0]*100)
		self.bPosition.append(value[1]*100)
		self.bPosition.append(value[2]*100)	

	def addB_Rotation(self, value):
		self.bRotation.append(math.degrees(value[0]))
		self.bRotation.append(math.degrees(value[1]))
		self.bRotation.append(math.degrees(value[2]))		

	def addB_Scale(self, value):
		self.bScale.append(value[0])
		self.bScale.append(value[1])
		self.bScale.append(value[2])	






