
import os
from math import radians
from struct import *

import bpy
from bpy.props import *
from mathutils import *
from bpy_extras.image_utils import load_image

#Default Config
def_scale = 1.0
def_axis = 2
def_smooth = True
def_remove_doubles = False

#Config Class
class OptionConfig:
	def __init__(self, context, path, scale=def_scale, axis=def_axis, smooth=def_smooth, remove_doubles=def_remove_doubles):
		self.context = context
		self.path = path
		self.scale = scale
		self.axis = int(axis)
		self.smooth = smooth
		self.remove_doubles = remove_doubles
		
def ReadWORD(fp):
	return BinaryToWORD(fp.read(2))

def ReadWORDArray(fp, count):
	values = []
	
	for i in range(count):
		values.append(ReadWORD(fp))
	return values

def ReadDWORD(fp):
	return BinaryToDWORD(fp.read(4))

def ReadDWORDArray(fp, count):
	values = []
	
	for i in range(count):
		values.append(ReadDWORD(fp))
	return values

def ReadByte(fp):
	return BinaryToByte(fp.read(1))

def ReadByteArray(fp, count):
	values = []
	
	for i in range(count):
		values.append(ReadByte(fp))
	return values

def ReadFloat(fp):
	return BinaryToFloat(fp.read(4))

def ReadFloatArray(fp, count):
	values = []
	
	for i in range(count):
		values.append(ReadFloat(fp))
	return values
	
def BinaryToByte(txt):
	return unpack('B', txt)[0]

def BinaryToDWORD(txt):
	return unpack('L', txt)[0]

def BinaryToWORD(txt):
	return unpack('H', txt)[0]

def BinaryToFloat(txt):
	return unpack('f', txt)[0]

class Header:
	def __init__(self):
		self.vertion = 0
		self.name = ""
		self.comment = ""

class Vertex:
	def __init__(self):
		self.pos = [0, 0, 0]
		self.normal = [0, 0, 0]
		self.uv = [0, 0]
		self.bone_indices = [0, 0]
		self.bone_weight = 0
		self.edge_enable = 0
		
class MaterialValue:
	def __init__(self):
		self.diffuse = [0, 0, 0]
		self.alpha = 0
		self.power = 0
		self.specular = [0, 0, 0]
		self.ambient = [0, 0, 0]
		self.toon = 0
		self.edge = 0
		self.face = 0
		self.texture = ""
		self.name = ""

class Bone:
	def __init__(self):
		self.name = ""
		self.parent_bone_index = 0xffff
		self.tail_pos_bone_index = 0xffff
		self.type = None
		self.ik_parent_bone_index = 0
		self.head_pos = [0, 0, 0]

class IK:
	def __init__(self):
		self.ik_bone_index = 0
		self.ik_target_bone_index = 0
		self.ik_chain_length = 0
		self.iterations = 0
		self.control_weight = 0
		self.ik_child_bone_index = []

class Skin:
	def __init__(self):
		self.name = ""
		self.vert_count = 0
		self.type = 0
		self.skin_verts = []

class SkinData:
	def __init__(self):
		self.vert_index = 0
		self.vert_translate = [0, 0, 0]

class BoneDisplay:
	def __init__(self):
		self.bone_index = 0
		self.display_frame_index = 0
		
class MMDLoad:
	fp = None
	
	def __init__(self):
		self.fp = None
		self.head = None
		self.vertices = []
		self.indices = []
		self.mtrls = []
	
	@staticmethod
	def load(path):
		buf = MMDLoad()
		MMDLoad.fp = open(path, "rb")
		
		#Header
		buf.head = MMDLoad.header()
		if(buf.head == None):
			MMDLoad.fp.close()
			print("Error: Not MMD Format")
			return None
		
		print("\r\n>>Data Information")
		
		#Read Data
		buf.vertices = MMDLoad.vertex()
		buf.indices = MMDLoad.index()
		buf.mtrls = MMDLoad.material()
		buf.bones = MMDLoad.bone()
		buf.ik_list = MMDLoad.ik()
		buf.skins = MMDLoad.skin()
		buf.skin_display = MMDLoad.skinDisplay()
		buf.bone_name = MMDLoad.boneName()
		buf.bone_display = MMDLoad.boneDisplay()
		
		#Extend
		ex = MMDLoad.fp.read()
		if(ex == None or len(ex) == 0):
			print("End:")
		else:
			print("Extend:")
		
		#File Close & End
		MMDLoad.fp.close()
		return buf
	
	@staticmethod
	def header():
		head = None
		
		if(MMDLoad.fp.read(3) == b'Pmd'):
			print("\r\n>>Head Information")
			head = Header()
			
			head.version = ReadFloat(MMDLoad.fp)
			print("Version:" + str(head.version))
			
			head.name = MMDLoad.fp.read(20).split(b"\x00")[0].decode("sjis").strip()
			print("Name:" + head.name)
			
			head.comment = MMDLoad.fp.read(256).split(b"\x00")[0].decode("sjis").strip()
			print("Comment:" + head.comment)
			
		return head
	
	@staticmethod
	def vertex():
		count = ReadDWORD(MMDLoad.fp)
		vertices = []
		
		for i in range(count):
			vertex = Vertex()
			
			#Position
			vertex.pos = ReadFloatArray(MMDLoad.fp, len(vertex.pos))
			vertex.pos[2] *= -1
			
			#Normalize
			vertex.normal = ReadFloatArray(MMDLoad.fp, len(vertex.normal))
			
			#Texcoord
			vertex.uv = ReadFloatArray(MMDLoad.fp, len(vertex.uv))
			
			#BoneIndices
			vertex.bone_indices = ReadWORDArray(MMDLoad.fp, len(vertex.bone_indices))
			
			#BoneWeights
			vertex.bone_weight = ReadByte(MMDLoad.fp)
			
			#EdgeFlag
			vertex.edge_enable = ReadByte(MMDLoad.fp)
			
			vertices.append(vertex)
		
		print("Vertex:" + str(count))
		return vertices
		
	@staticmethod
	def index():
		count = ReadDWORD(MMDLoad.fp)
		indices = ReadWORDArray(MMDLoad.fp, count)
		
		print("Index:" + str(count))
		return indices
		
	@staticmethod
	def material():
		count = ReadDWORD(MMDLoad.fp)
		materials = []
		
		for i in range(count):
			mtrl = MaterialValue()
			
			mtrl.diffuse = ReadFloatArray(MMDLoad.fp, len(mtrl.diffuse))
			mtrl.alpha = ReadFloat(MMDLoad.fp)
			mtrl.power = ReadFloat(MMDLoad.fp)
			mtrl.specular = ReadFloatArray(MMDLoad.fp, len(mtrl.specular))
			mtrl.ambient = ReadFloatArray(MMDLoad.fp, len(mtrl.ambient))
			mtrl.toon = ReadByte(MMDLoad.fp)
			mtrl.edge = ReadByte(MMDLoad.fp)
			mtrl.face = ReadDWORD(MMDLoad.fp)
			mtrl.texture = MMDLoad.fp.read(20).split(b"\x00")[0].decode().strip()
			mtrl.name = "Material_" + str(i)
			
			materials.append(mtrl)
		
		print("Material:" + str(count))
		return materials

	@staticmethod
	def bone():
		count = ReadWORD(MMDLoad.fp)
		bones = []
		
		for i in range(count):
			bone = Bone()
			bone.name = MMDLoad.fp.read(20).split(b"\x00")[0].decode("sjis").strip()
			bone.parent_bone_index = ReadWORD(MMDLoad.fp)
			bone.tail_pos_bone_index = ReadWORD(MMDLoad.fp)
			bone.type = ReadByte(MMDLoad.fp)
			bone.ik_parent_bone_index = ReadWORD(MMDLoad.fp)
			bone.head_pos = ReadFloatArray(MMDLoad.fp, len(bone.head_pos))
			bone.head_pos[2] *= -1
			
			bones.append(bone)

		print("Bone:" + str(count))
		return bones

	@staticmethod
	def ik():
		count = ReadWORD(MMDLoad.fp)
		ik_list = []
		
		for i in range(count):
			ik = IK()
			ik.ik_bone_index = ReadWORD(MMDLoad.fp)
			ik.ik_target_bone_index = ReadWORD(MMDLoad.fp)
			ik.ik_chain_length = ReadByte(MMDLoad.fp)
			ik.iterations = ReadWORD(MMDLoad.fp)
			ik.cotrol_weight = ReadFloat(MMDLoad.fp)

			for j in range(ik.ik_chain_length):
				ik.ik_child_bone_index.append(ReadWORD(MMDLoad.fp))

			ik_list.append(ik)

		print("IK:" + str(count))
		return ik_list

	@staticmethod
	def skin():
		count = ReadWORD(MMDLoad.fp)
		skins = []

		for i in range(count):
			skin = Skin()
			skin.name = MMDLoad.fp.read(20).split(b"\x00")[0].decode("sjis").strip()
			skin.vert_count = ReadDWORD(MMDLoad.fp)
			skin.type = ReadByte(MMDLoad.fp)

			for j in range(skin.vert_count):
				data = SkinData()
				data.vert_index = ReadDWORD(MMDLoad.fp)
				data.vert_translate = ReadFloatArray(MMDLoad.fp, len(data.vert_translate))

				skin.skin_verts.append(data)

			skins.append(skin)

		print("SKIN:" + str(count))
		return skins

	@staticmethod
	def skinDisplay():
		count = ReadByte(MMDLoad.fp)
		display = []

		for i in range(count):
			display.append(ReadWORD(MMDLoad.fp))

		print("SkinDisplay:" + str(count))
		return display

	@staticmethod
	def boneName():
		count = ReadByte(MMDLoad.fp)
		name = []

		for i in range(count):
			name.append(MMDLoad.fp.read(50).split(b"\x00")[0].decode("sjis").strip())

		print("BoneName:" + str(count))
		return name

	@staticmethod
	def boneDisplay():
		count = ReadDWORD(MMDLoad.fp)
		display = []
		
		for i in range(count):
			disp = BoneDisplay()
			disp.bone_index = ReadWORD(MMDLoad.fp)
			disp.display_frame_index = ReadByte(MMDLoad.fp)
			
			display.append(disp)

		print("BoneDisplay:" + str(count))
		return display
		
class DivMaterial:
	def __init__(self):
		self.materials = []
		self.textures = []
		self.indices = []
		self.useMtrl = []
		
def loadMMD(config):
	print(">>Loading...")
	print("FilePath:" + config.path)
	scene = config.context.scene
	
	transformMatrix = Matrix()
	
	#Scaling
	transformMatrix *= Matrix.Scale(config.scale, 4, Vector((1, 0, 0)))
	transformMatrix *= Matrix.Scale(config.scale, 4, Vector((0, 1, 0)))
	transformMatrix *= Matrix.Scale(config.scale, 4, Vector((0, 0, 1)))
	
	#Change AxisY
	if(config.axis == 1):
		transformMatrix *= Matrix.Rotation(radians(-90), 4, "X")
		
	#Change AxisZ
	if(config.axis == 2):
		transformMatrix *= Matrix.Rotation(radians(90), 4, "X")
		
	#Load File
	buf = MMDLoad.load(config.path)
	if(buf == None):
		return
	
	coords = []
	texcoord = []
	faces = buf.indices
	left = [0, 2, 1]
	
	for vertex in buf.vertices:
		coords.append(vertex.pos)
		texcoord.append(vertex.uv)
	
	#Create Material
	divMtrl = DivMaterial()
	divMtrls = [divMtrl]
	
	total = 0
	matIndex = 0
	
	for mtrl in buf.mtrls:
		material = bpy.data.materials.new(mtrl.name)
		material.diffuse_color = mtrl.diffuse
		material.alpha = mtrl.alpha
		material.mirror_color = mtrl.ambient
		material.specular_color = mtrl.specular
		material.specular_intensity = mtrl.power
		
		#Create Texture
		img = None
		
		if(len(mtrl.texture) != 0):
			if(mtrl.texture.find("*") >= 0):
				mtrl.texture = mtrl.texture.split("*")[0]
				
			pathName = mtrl.texture.replace("\\", "/")
			
			if(not os.path.exists(pathName)):
				dirName = os.path.dirname(config.path.replace("\\", "/"))
				pathName = dirName + "/" + pathName
				
			if(os.path.exists(pathName) == True):
				tex = bpy.data.textures.new("Tex_" + material.name, type="IMAGE")
				tex.image = img = load_image(pathName, os.path.dirname(config.path))
				mtex = material.texture_slots.add()
				mtex.texture = tex
				mtex.texture_coords = 'UV'
				mtex.use_map_color_diffuse = True
				
				print("TexturePath:" + pathName)
		
		divMtrl.materials.append(material)
		divMtrl.textures.append(img)
		
		#Create Index
		start = total
		total += mtrl.face
		tmp = faces[start:total]
		faceCnt = int(mtrl.face / 3)
		
		for faceIndex in range(faceCnt):
			face = [0, 0, 0]
			target = faceIndex * 3
			
			for index in range(3):
				face[ left[index] ] = tmp[target + index]
				
			divMtrl.indices.append(face)
			divMtrl.useMtrl.append(len(divMtrl.materials) - 1)
		
		if(len(divMtrl.materials) >= 16):
			divMtrl = DivMaterial()
			divMtrls.append(divMtrl)
		
	#Mesh
	objects = []
	
	for mtrlID, mtrl in enumerate(divMtrls):
		me = bpy.data.meshes.new(os.path.basename(config.path) + "_" + str(mtrlID))
		
		obj = bpy.data.objects.new(me.name, me)
		objects.append(obj)
		scene.objects.link(obj)
		
		for mat in mtrl.materials:
			me.materials.append(mat)
		
		me.vertices.add(len(coords))
		me.faces.add(len(mtrl.indices))
		
		for i in range(len(coords)):
			me.vertices[i].co = Vector(coords[i]) * transformMatrix
			
		for i in range(len(mtrl.indices)):
			for j in range(len(mtrl.indices[i])):
				me.faces[i].vertices_raw[j] = mtrl.indices[i][j]
				
		#Texcoord
		me.uv_textures.new()
		uv_faces = me.uv_textures.active.data[:]
		
		for i in range(len(uv_faces)):
			me.faces[i].material_index = mtrl.useMtrl[i]
			img = mtrl.textures[mtrl.useMtrl[i]]
			
			if(img):
				uv = uv_faces[i]
				uv.use_image = True
				uv.image = img
				index = me.faces[i].vertices_raw
				
				uv.uv1 = [texcoord[index[0]][0], 1 - texcoord[index[0]][1]]
				uv.uv2 = [texcoord[index[1]][0], 1 - texcoord[index[1]][1]]
				uv.uv3 = [texcoord[index[2]][0], 1 - texcoord[index[2]][1]]
				
	#Create Group
	name, ext = os.path.splitext(os.path.basename(config.path))
	group = bpy.data.objects.new(name + ext.replace(".", "_"), None)
	
	scene.objects.link(group)
	group.select = True
	scene.objects.active = group
	bpy.ops.group.create(name=group.name)
	
	#Remove Doubles & Smooth & Create Edge
	for obj in objects:
		obj.select = True
		scene.objects.active = obj
		bpy.ops.object.mode_set(mode='EDIT')
		
		if config.remove_doubles:
			bpy.ops.mesh.remove_doubles()
			
		if config.smooth:
			bpy.ops.mesh.faces_shade_smooth()
			
		bpy.ops.object.mode_set(mode='OBJECT')
		obj.parent = group
		
	#Frame Name
	bpy.ops.object.armature_add()
	obj = config.context.active_object
	obj.parent = group
	
	bpy.ops.object.mode_set(mode="EDIT")
	armature = obj.data
	bone = armature.edit_bones[-1]
	
	display = -1
	print("\r\n>>Bone Information")
	editBoneName =[]
	editBoneType =[]
	
	for disp in buf.bone_display:
		if(display != disp.display_frame_index):
			display = disp.display_frame_index
			print("Frame Name:" + buf.bone_name[display - 1])
	
		data = buf.bones[disp.bone_index]
		editBoneName.append(data.name)
		editBoneType.append(data.type)
		
		if(bone == None):
			bone = armature.edit_bones.new(data.name)
		else:
			bone.name = data.name
			
		head = data.head_pos
		tail = buf.bones[data.tail_pos_bone_index].head_pos
		
		bone.head = Vector(head) * transformMatrix
		bone.tail = Vector(tail) * transformMatrix
		
		text = " Head:{" + "{:.03f} {:.03f} {:.03f}".format(head[0], head[1], head[2]) + "}"
		text += " Tail:{" + "{:.03f} {:.03f} {:.03f}".format(tail[0], tail[1], tail[2]) + "}"
		text += " Type:" + str(data.type)
		print("  Bone:" + data.name + text)
		bone = None
		
	print("\r\n>>Ather Bone")
	
	for disp in buf.bone_display:
		data = buf.bones[disp.bone_index]
		bone = armature.edit_bones[data.name]
		index = data.parent_bone_index
		
		#if(data.type == 2):
		#	for ik in buf.ik_list:
		#		if(ik.ik_bone_index == disp.bone_index):
		#			index = ik.ik_target_bone_index
		#			break
			
		if(index != 0xffff):
			p_data = buf.bones[index]
			
			try:
				bone.parent = armature.edit_bones[p_data.name]
				
			except:
				if(p_data.type != 7):
					parent = armature.edit_bones.new(p_data.name)
					head = p_data.head_pos
					tail = buf.bones[p_data.tail_pos_bone_index].head_pos
					
					parent.head = Vector(head) * transformMatrix
					parent.tail = Vector(tail) * transformMatrix
					
					bone.parent = parent
					
					text = " Head:{" + "{:.03f} {:.03f} {:.03f}".format(head[0], head[1], head[2]) + "}"
					text += " Tail:{" + "{:.03f} {:.03f} {:.03f}".format(tail[0], tail[1], tail[2]) + "}"
					text += " Type:" + str(p_data.type)
					print("  Bone:" + p_data.name + text)
					
					editBoneName.append(p_data.name)
					editBoneType.append(p_data.type)
			print()
	
	bpy.ops.object.mode_set(mode="OBJECT")
	print(bpy.ops.armature)

AxisModes = []
AxisModes.append(("0", "Default", ""))
AxisModes.append(("1", "AxisY(Rotate X-90)", ""))
AxisModes.append(("2", "AxisZ(Rotate X90)", ""))

class MMDImporter(bpy.types.Operator):
    """Import to the MikuMikuDance format (.pmd)"""

    bl_idname = "import.mmd"
    bl_label = "Import MikuMikuDance"
    filename_ext = ".pmd"
    
    filepath = StringProperty()
    filename = StringProperty()
    directory = StringProperty()
    
    ImportScale = FloatProperty(name="Scale", description="Change of scale value.", min=0.01, max=100, soft_min=0.01, soft_max=10, default=def_scale)
    ImportAxis = EnumProperty(name="Upper Axis", description="Setting of the above axis.", items=AxisModes, default=str(def_axis))
    ImportSmooth = BoolProperty(name="Smooth", description="Smoothing of surface.", default= def_smooth)
    ImportRemoveDoubles = BoolProperty(name="Remove Doubles", description="Remove duplicate vertices.", default= def_remove_doubles)
    
    def execute(self, context):
        loadMMD( OptionConfig(context, self.filepath, self.ImportScale, self.ImportAxis, self.ImportSmooth, self.ImportRemoveDoubles) )
        
        return {"FINISHED"}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}
