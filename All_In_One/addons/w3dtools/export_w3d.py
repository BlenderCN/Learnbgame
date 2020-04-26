#Written by Stephan Vedder and Michael Schnabel
#Last Modification 06.06.2016
#Exports the W3D Format used in games by Westwood & EA
import bpy
import operator
import struct
import os
import math
import sys
import bmesh
from bpy.props import *
from mathutils import Vector, Quaternion
from . import struct_w3d, import_w3d

#TODO 

# write AABTree to file

# change test if we need to write normal map chunk

# fix sphere calculation

# export animation data (when import works)

HEAD = 8 #4(long = chunktype) + 4 (long = chunksize)

#######################################################################################
# Basic Methods
#######################################################################################

def getStringSize(string):
	return len(string) + 1 #binary 0

def WriteString(file, string):
	file.write(bytes(string, 'UTF-8'))
	#write binary 0 to file
	file.write(struct.pack('B', 0))

def WriteFixedString(file, string):
	#truncate the string to 16
	nullbytes = 16-len(string)
	if(nullbytes<0):
		print("Warning: Fixed string is too long")

	file.write(bytes(string, 'UTF-8'))
	for i in range(nullbytes):
		file.write(struct.pack("B", 0))

def WriteLongFixedString(file, string):
	#truncate the string to 32
	nullbytes = 32-len(string)
	if(nullbytes<0):
		print("Warning: Fixed string is too long")

	file.write(bytes(string, 'UTF-8'))
	for i in range(nullbytes):
		file.write(struct.pack("B", 0))

def WriteRGBA(file, rgba):
	file.write(struct.pack("B", rgba.r))
	file.write(struct.pack("B", rgba.g))
	file.write(struct.pack("B", rgba.b))
	file.write(struct.pack("B", rgba.a))

# only if the chunk has subchunks -> else: WriteLong(file, data)
def MakeChunkSize(data):
	return (data | 0x80000000)

def WriteLong(file, num):
	file.write(struct.pack("<L", num))

def WriteSignedLong(file, num):
	file.write(struct.pack("<l", num))	

def WriteShort(file, num):
	file.write(struct.pack("<H", num))

def WriteLongArray(file, array):
	for a in array:
		WriteLong(file, a)

def WriteFloat(file, num):
	file.write(struct.pack("<f", num))

def WriteSignedByte(file, num):
	file.write(struct.pack("<b", num))

def WriteUnsignedByte(file, num):
	file.write(struct.pack("<B", num))

def WriteVector(file, vec):
	WriteFloat(file, vec[0])
	WriteFloat(file, vec[1])
	WriteFloat(file, vec[2])

def WriteQuaternion(file, quat):
	#changes the order from wxyz to xyzw
	WriteFloat(file, quat[1])
	WriteFloat(file, quat[2])
	WriteFloat(file, quat[3])
	WriteFloat(file, quat[0])

def MakeVersion(version):
	return (((version.major) << 16) | (version.minor))

#######################################################################################
# Triangulate
#######################################################################################	

def triangulate(mesh):
	import bmesh
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bmesh.ops.triangulate(bm, faces = bm.faces)
	bm.to_mesh(mesh)
	bm.free()

#######################################################################################
# Hierarchy
#######################################################################################

def getHierarchyHeaderChunkSize(header):
	return 36

def WriteHierarchyHeader(file, header):
	WriteLong(file, 257) #chunktype
	WriteLong(file, getHierarchyHeaderChunkSize(header)) #chunksize

	WriteLong(file, MakeVersion(header.version))
	WriteFixedString(file, header.name)
	WriteLong(file, header.pivotCount)
	WriteVector(file, header.centerPos)	

def getHierarchyPivotsChunkSize(pivots):
	size = 0
	for pivot in pivots:
		size += 60
	return size
	
def WritePivots(file, pivots):
	WriteLong(file, 258) #chunktype
	WriteLong(file, getHierarchyPivotsChunkSize(pivots)) #chunksize
	
	for pivot in pivots:
		WriteFixedString(file, pivot.name)
		WriteSignedLong(file, pivot.parentID)
		WriteVector(file, pivot.position)
		WriteVector(file, pivot.eulerAngles)
		WriteQuaternion(file, pivot.rotation)
		
def getPivotFixupsChunkSize(pivot_fixups):
	size = 0
	for fixup in pivot_fixups:
		size += 12
	return size

def WritePivotFixups(file, pivot_fixups):
	WriteLong(file, 259) #chunktype
	WriteLong(file, getPivotFixupsChunkSize(pivot_fixups)) #chunksize
	
	for fixup in pivot_fixups: 
		WriteVector(file, fixup)
		
def getHierarchyChunkSize(hierarchy):
	size = HEAD + getHierarchyHeaderChunkSize(hierarchy.header)
	size += HEAD + getHierarchyPivotsChunkSize(hierarchy.pivots)
	if len(hierarchy.pivot_fixups) > 0:
		size += HEAD + getPivotFixupsChunkSize(hierarchy.pivot_fixups)
	return size

def WriteHierarchy(file, hierarchy):
	#print("\n### NEW HIERARCHY: ###")
	WriteLong(file, 256) #chunktype
	WriteLong(file, MakeChunkSize(getHierarchyChunkSize(hierarchy))) #chunksize
	
	WriteHierarchyHeader(file, hierarchy.header)
	#print("Header")
	WritePivots(file, hierarchy.pivots)
	#print("Pivots")
	if len(hierarchy.pivot_fixups) > 0:
		WritePivotFixups(file, hierarchy.pivot_fixups)
		print("Pivot Fixups")
	
#######################################################################################
# Animation
#######################################################################################

def getAnimationHeaderChunkSize(header):
	return 44
	
def WriteAnimationHeader(file, header):
	WriteLong(file, 513) #chunktype
	WriteLong(file, getAnimationHeaderChunkSize(header)) #chunksize

	WriteLong(file, MakeVersion(header.version))
	WriteFixedString(file, header.name)
	WriteFixedString(file, header.hieraName)
	WriteLong(file, header.numFrames)
	WriteLong(file, header.frameRate)
	
def getAnimationChannelChunkSize(channel):
	return 12 + (len(channel.data) * channel.vectorLen) * 4

def WriteAnimationChannel(file, channel):
	WriteLong(file, 514) #chunktype
	WriteLong(file, getAnimationChannelChunkSize(channel)) #chunksize
	
	WriteShort(file, channel.firstFrame)
	WriteShort(file, channel.lastFrame)
	WriteShort(file, channel.vectorLen)
	WriteShort(file, channel.type)
	WriteShort(file, channel.pivot)
	WriteShort(file, channel.pad)
	
	print(len(channel.data))

	if channel.vectorLen == 1:
		for f in channel.data:
			WriteFloat(file, f)
	elif channel.vectorLen == 4:
		for quat in channel.data:
			WriteQuaternion(file, quat)
			
def getAnimationChunkSize(animation):
	size = HEAD + getAnimationHeaderChunkSize(animation.header)
	for channel in animation.channels:
		size += HEAD + getAnimationChannelChunkSize(channel)
	return size

def WriteAnimation(file, animation):
	print("\n### NEW ANIMATION: ###")
	WriteLong(file, 512) #chunktype
	WriteLong(file, MakeChunkSize(getAnimationChunkSize(animation))) #chunksize
	
	WriteAnimationHeader(file, animation.header)
	print("Header")
	for channel in animation.channels:
		WriteAnimationChannel(file, channel)
		print("Channel")
			
			
#def WriteCompressedAnimationHeader(file, size, header):
#	 WriteLong(file, 641) #chunktype
#	 WriteLong(file, size) #chunksize
#
#	 WriteLong(file, MakeVersion(header.version))
#	 WriteFixedString(file, header.name)
#	 WriteFixedString(file, header.hieraName)
#	 WriteLong(file, header.numFrames)
#	 WriteShort(file, header.frameRate)
#	 WriteShort(file, header.flavor)
	
#def WriteTimeCodedAnimVector(file, size, animVector):
#	 WriteLong(file, 644) #chunktype
#	 WriteLong(file, size) #chunksize
	
#	 print("#####not implemented yet!!")
	
#def WriteCompressedAnimation(file, compAnimation):
#	 #print("\n### NEW COMPRESSED ANIMATION: ###")
#	 WriteLong(file, 640) #chunktype
#	
#	 headerSize = 44
#	 vectorsSize = 0
#	 #for vec in compAnimation.animVectors:
#		 #vectorsSize += HEAD + 
#	 size = HEAD + headerSize #+ vectorsSize
	
#	 WriteLong(file, size) #chunksize

#	 WriteCompressedAnimationHeader(file, headerSize, compAnimation.header)	
	#print("Header")
	#for vec in compAnimation.animVectors:
		#WriteTimeCodedAnimVector(file, vec)
		#print("AnimVector")
	
#######################################################################################
# HLod
#######################################################################################

def getHLodHeaderChunkSize(header):
	return 40

def WriteHLodHeader(file, header):
	WriteLong(file, 1793) #chunktype
	WriteLong(file, getHLodHeaderChunkSize(header)) #chunksize
	
	WriteLong(file, MakeVersion(header.version))
	WriteLong(file, header.lodCount)
	WriteFixedString(file, header.modelName)
	WriteFixedString(file, header.HTreeName) 
	
def getHLodArrayHeaderChunkSize(arrayHeader):
	return 8

def WriteHLodArrayHeader(file, arrayHeader):
	WriteLong(file, 1795) #chunktype
	WriteLong(file, getHLodArrayHeaderChunkSize(arrayHeader)) #chunksize
	
	WriteLong(file, arrayHeader.modelCount)
	WriteFloat(file, arrayHeader.maxScreenSize)
	
def getHLodSubObjectChunkSize(subObject):
	return 36

def WriteHLodSubObject(file, subObject): 
	WriteLong(file, 1796) #chunktype
	WriteLong(file, getHLodSubObjectChunkSize(subObject)) #chunksize
	
	WriteLong(file, subObject.boneIndex)
	WriteLongFixedString(file, subObject.name)

def getHLodArrayChunkSize(lodArray):
	size = HEAD + getHLodArrayHeaderChunkSize(lodArray.header)
	for object in lodArray.subObjects: 
		size += HEAD + getHLodSubObjectChunkSize(object)
	return size		
	
def WriteHLodArray(file, lodArray):
	WriteLong(file, 1794) #chunktype
	WriteLong(file, MakeChunkSize(getHLodArrayChunkSize(lodArray))) #chunksize
	
	WriteHLodArrayHeader(file, lodArray.header)
	for object in lodArray.subObjects:
		WriteHLodSubObject(file, object)

def getHLodChunkSize(hlod):
	size = HEAD + getHLodHeaderChunkSize(hlod.header)
	size += HEAD + getHLodArrayChunkSize(hlod.lodArray)
	return size		
		
def WriteHLod(file, hlod):
	#print("\n### NEW HLOD: ###")
	WriteLong(file, 1792) #chunktype
	WriteLong(file, MakeChunkSize(getHLodChunkSize(hlod))) #chunksize
	
	WriteHLodHeader(file, hlod.header)
	#print("Header")
	WriteHLodArray(file, hlod.lodArray)
	#print("Array")
	
#######################################################################################
# Box
#######################################################################################	

def WriteBox(file, box):
	WriteLong(file, 1856) #chunktype
	WriteLong(file, 68) #chunksize
	
	WriteLong(file, MakeVersion(box.version)) 
	WriteLong(file, box.attributes)
	WriteLongFixedString(file, box.name)
	WriteRGBA(file, box.color)
	WriteVector(file, box.center)
	WriteVector(file, box.extend)
	
#######################################################################################
# Texture
#######################################################################################	

def getTextureChunkSize(texture):
	return HEAD + getStringSize(texture.name) # + HEAD + 12
	
def WriteTexture(file, texture):
	#print(texture.name)
	WriteLong(file, 49) #chunktype
	WriteLong(file,	 MakeChunkSize(getTextureChunkSize(texture)))#chunksize
	
	WriteLong(file, 50) #chunktype
	WriteLong(file, getStringSize(texture.name)) #chunksize
	
	WriteString(file, texture.name)
	
	#WriteLong(file, 51) #chunktype
	#WriteLong(file, 12) #chunksize 
	
	#WriteShort(file, texture.textureInfo.attributes)
	#WriteShort(file, texture.textureInfo.animType)
	#WriteLong(file, texture.textureInfo.frameCount)
	#WriteFloat(file, texture.textureInfo.frameRate)
	
def getTextureArrayChunkSize(textures):
	size = 0
	for tex in textures:
		size += HEAD + getTextureChunkSize(tex)
	return size

def WriteTextureArray(file, textures):
	WriteLong(file, 48) #chunktype
	WriteLong(file, MakeChunkSize(getTextureArrayChunkSize(textures))) #chunksize  
	
	for texture in textures:
		WriteTexture(file, texture)
		
#######################################################################################
# Material
#######################################################################################	

def getMeshTextureCoordArrayChunkSize(txCoords):
	return len(txCoords) * 8

def WriteMeshTextureCoordArray(file, txCoords):
	WriteLong(file, 74) #chunktype
	WriteLong(file, getMeshTextureCoordArrayChunkSize(txCoords)) #chunksize 
	for coord in txCoords:
		WriteFloat(file, coord[0])
		WriteFloat(file, coord[1])
		
def getMeshTextureStageChunkSize(textureStage):
	size = HEAD + len(textureStage.txIds) * 4
	size += HEAD + getMeshTextureCoordArrayChunkSize(textureStage.txCoords)
	return size

def WriteMeshTextureStage(file, textureStage):
	WriteLong(file, 72) #chunktype
	WriteLong(file, MakeChunkSize(getMeshTextureStageChunkSize(textureStage))) #chunksize  
	
	WriteLong(file, 73) #chunktype
	WriteLong(file, len(textureStage.txIds) * 4) #chunksize 
	WriteLongArray(file, textureStage.txIds)
	
	WriteMeshTextureCoordArray(file, textureStage.txCoords)
	
def getMeshMaterialPassChunkSize(matlPass):
	size = HEAD + len(matlPass.vmIds) * 4
	size += HEAD + len(matlPass.shaderIds) * 4
	if len(matlPass.txStage.txIds) > 0:
		size += HEAD + getMeshTextureStageChunkSize(matlPass.txStage)
	return size


def WriteMeshMaterialPass(file, matlPass):
	WriteLong(file, 56) #chunktype
	WriteLong(file, MakeChunkSize(getMeshMaterialPassChunkSize(matlPass))) #chunksize  
	
	WriteLong(file, 57) #chunktype
	WriteLong(file, len(matlPass.vmIds) * 4) #chunksize	 

	WriteLongArray(file, matlPass.vmIds)
 
	WriteLong(file, 58) #chunktype
	WriteLong(file, len(matlPass.shaderIds) * 4) #chunksize 
	
	WriteLongArray(file, matlPass.shaderIds)
	
	#if len(matlPass.dcg) > 0:
	#	 WriteLong(file, 59) #chunktype
	#	 WriteLong(file, len(matlPass.dcg) * 4) #chunksize 
 
	#	 for dcg in matlPass.dcg: 
	#		 WriteRGBA(file, dcg)
	
	if len(matlPass.txStage.txIds) > 0:
		WriteMeshTextureStage(file, matlPass.txStage)
		
def getMaterialChunkSize(mat):
	size = HEAD + getStringSize(mat.vmName)
	size += HEAD + 32
	if len(mat.vmArgs0) > 0:
		size += HEAD + getStringSize(mat.vmArgs0)
	if len(mat.vmArgs1) > 0:
		size += HEAD + getStringSize(mat.vmArgs1)
	return size

def WriteMaterial(file, mat):
	WriteLong(file, 43) #chunktype
	WriteLong(file, MakeChunkSize(getMaterialChunkSize(mat))) #chunksize
	
	WriteLong(file, 44) #chunktype
	WriteLong(file, getStringSize(mat.vmName)) #chunksize  #has to be size of the string plus binary 0
	
	WriteString(file, mat.vmName)
	
	WriteLong(file, 45) #chunktype
	WriteLong(file, 32) #chunksize 
	
	WriteLong(file, mat.vmInfo.attributes)
	WriteRGBA(file, mat.vmInfo.ambient)
	WriteRGBA(file, mat.vmInfo.diffuse)
	WriteRGBA(file, mat.vmInfo.specular)
	WriteRGBA(file, mat.vmInfo.emissive)
	WriteFloat(file, mat.vmInfo.shininess)
	WriteFloat(file, mat.vmInfo.opacity)
	WriteFloat(file, mat.vmInfo.translucency)
	
	if len(mat.vmArgs0) > 0:
		WriteLong(file, 46) #chunktype
		WriteLong(file, getStringSize(mat.vmArgs0)) #chunksize 
		WriteString(file, mat.vmArgs0)
	
	if len(mat.vmArgs1) > 0:
		WriteLong(file, 47) #chunktype
		WriteLong(file, getStringSize(mat.vmArgs1)) #chunksize 
		WriteString(file, mat.vmArgs1)
		
def getMeshMaterialArrayChunkSize(materials): 
	size = 0
	for material in materials:
		size += HEAD + getMaterialChunkSize(material)
	return size

def WriteMeshMaterialArray(file, materials):
	WriteLong(file, 42) #chunktype
	WriteLong(file, MakeChunkSize(getMeshMaterialArrayChunkSize(materials))) #chunksize

	for mat in materials:
		WriteMaterial(file, mat)
		
def getMeshMaterialSetInfoChunkSize(matSetInfo):
	return 16
		
def WriteMeshMaterialSetInfo (file, matSetInfo):
	WriteLong(file, 40) #chunktype
	WriteLong(file, getMeshMaterialSetInfoChunkSize(matSetInfo)) #chunksize
	
	WriteLong(file, matSetInfo.passCount)
	WriteLong(file, matSetInfo.vertMatlCount)
	WriteLong(file, matSetInfo.shaderCount)
	WriteLong(file, matSetInfo.textureCount)
	
#######################################################################################
# Vertices
#######################################################################################

def getMeshVerticesArrayChunkSize(vertices):
	return len(vertices) * 12

def WriteMeshVerticesArray(file, vertices):
	WriteLong(file, 2) #chunktype
	WriteLong(file, getMeshVerticesArrayChunkSize(vertices)) #chunksize
	
	for vert in vertices:
		WriteVector(file, vert)
		
def WriteMeshVerticesCopyArray(file, vertices):
	WriteLong(file, 3072) #chunktype
	WriteLong(file, getMeshVerticesArrayChunkSize(vertices)) #chunksize
	
	for vert in vertices:
		WriteVector(file, vert)

def getMeshVertexInfluencesChunkSize(influences):
	return len(influences) * 8		
		
def WriteMeshVertexInfluences(file, influences):
	WriteLong(file, 14) #chunktype
	WriteLong(file, getMeshVertexInfluencesChunkSize(influences)) #chunksize

	for inf in influences:
		WriteShort(file, inf.boneIdx)
		WriteShort(file, inf.xtraIdx)
		WriteShort(file, int(inf.boneInf * 100))
		WriteShort(file, int(inf.xtraInf * 100))		

#######################################################################################
# Normals
#######################################################################################
	
def WriteMeshNormalArray(file, normals):
	WriteLong(file, 3) #chunktype
	WriteLong(file, getMeshVerticesArrayChunkSize(normals)) #chunksize
	
	for norm in normals:
		WriteVector(file, norm)
		
def WriteMeshNormalCopyArray(file, normals):
	WriteLong(file, 3073) #chunktype
	WriteLong(file, getMeshVerticesArrayChunkSize(normals)) #chunksize
	
	for norm in normals:
		WriteVector(file, norm)
	
#######################################################################################
# Faces
#######################################################################################	

def getMeshFaceArrayChunkSize(faces):
	return len(faces) * 32

def WriteMeshFaceArray(file, faces):
	WriteLong(file, 32) #chunktype
	WriteLong(file, getMeshFaceArrayChunkSize(faces)) #chunksize
	
	for face in faces:
		WriteLong(file, face.vertIds[0])
		WriteLong(file, face.vertIds[1])
		WriteLong(file, face.vertIds[2])
		WriteLong(file, face.attrs)
		WriteVector(file, face.normal)
		WriteFloat(file, face.distance)
		
#######################################################################################
# Shader
#######################################################################################

def getMeshShaderArrayChunkSize(shaders):
	return len(shaders) * 16
	
def WriteMeshShaderArray(file, shaders):
	WriteLong(file, 41) #chunktype
	WriteLong(file, getMeshShaderArrayChunkSize(shaders)) #chunksize
	for shader in shaders:
		WriteUnsignedByte(file, shader.depthCompare)
		WriteUnsignedByte(file, shader.depthMask)
		WriteUnsignedByte(file, shader.colorMask)
		WriteUnsignedByte(file, shader.destBlend)
		WriteUnsignedByte(file, shader.fogFunc)		
		WriteUnsignedByte(file, shader.priGradient)
		WriteUnsignedByte(file, shader.secGradient)
		WriteUnsignedByte(file, shader.srcBlend)
		WriteUnsignedByte(file, shader.texturing)
		WriteUnsignedByte(file, shader.detailColorFunc)
		WriteUnsignedByte(file, shader.detailAlphaFunc)		
		WriteUnsignedByte(file, shader.shaderPreset)
		WriteUnsignedByte(file, shader.alphaTest)
		WriteUnsignedByte(file, shader.postDetailColorFunc)
		WriteUnsignedByte(file, shader.postDetailAlphaFunc)
		WriteUnsignedByte(file, shader.pad)
		
#######################################################################################
# Bump Maps
#######################################################################################

def getNormalMapHeaderChunkSize(header):
	return 37
	
def WriteNormalMapHeader(file, header): 
	WriteLong(file, 82) #chunktype
	WriteLong(file, getNormalMapHeaderChunkSize(header)) #chunksize
	
	WriteSignedByte(file, header.number)
	WriteLongFixedString(file, header.typeName)
	WriteLong(file, header.reserved)
	
def getNormalMapEntryStructSize(entryStruct):
	return 293 + getStringSize(entryStruct.diffuseTexName) + getStringSize(entryStruct.normalMap)

def WriteNormalMapEntryStruct(file, entryStruct): 
	WriteLong(file, 83) #chunktype
	WriteLong(file, 4 + 4 + getStringSize("DiffuseTexture") + 4 + getStringSize(entryStruct.diffuseTexName)) #chunksize
	WriteLong(file, 1) #texture type
	WriteLong(file, getStringSize("DiffuseTexture")) 
	WriteString(file, "DiffuseTexture")
	WriteLong(file, 1) #unknown value
	WriteString(file, entryStruct.diffuseTexName)
	
	WriteLong(file, 83) #chunktype
	WriteLong(file, 4 + 4 + getStringSize("NormalMap") + 4 + getStrinSize(entryStruct.normalMap)) #chunksize
	WriteLong(file, 1) #texture type
	WriteLong(file, getStringSize("NormalMap")) 
	WriteString(file, "NormalMap")
	WriteLong(file, 1) #unknown value
	WriteString(file, entryStruct.normalMap)
	
	WriteLong(file, 83) #chunktype
	WriteLong(file, 4 + 4 + getStringSize("BumpScale") + 4) #chunksize
	WriteLong(file, 2) #bumpScale
	WriteLong(file, getStringSize("BumpScale")) 
	WriteString(file, "BumpScale")
	WriteFloat(file, entryStruct.bumpScale)
	
	WriteLong(file, 83) #chunktype
	WriteLong(file, 4 + 4 + getStringSize("AmbientColor") + 16) #chunksize
	WriteLong(file, 5) #color
	WriteLong(file, getStringSize("AmbientColor")) 
	WriteString(file, "AmbientColor")
	WriteFloat(file, entryStruct.ambientColor[0])
	WriteFloat(file, entryStruct.ambientColor[1])
	WriteFloat(file, entryStruct.ambientColor[2])
	WriteFloat(file, entryStruct.ambientColor[3])
	
	WriteLong(file, 83) #chunktype
	WriteLong(file, 4 + 4 + getStringSize("DiffuseColor") + 16) #chunksize
	WriteLong(file, 5) #color
	WriteLong(file, getStringSize("DiffuseColor")) 
	WriteString(file, "DiffuseColor")
	WriteFloat(file, entryStruct.diffuseColor[0])
	WriteFloat(file, entryStruct.diffuseColor[1])
	WriteFloat(file, entryStruct.diffuseColor[2])
	WriteFloat(file, entryStruct.diffuseColor[3])
	
	WriteLong(file, 83) #chunktype
	WriteLong(file, 4 + 4 + getStringSize("SpecularColor") + 16) #chunksize
	WriteLong(file, 5) #color
	WriteLong(file, geStringSize("SpecularColor")) 
	WriteString(file, "SpecularColor")
	WriteFloat(file, entryStruct.specularColor[0])
	WriteFloat(file, entryStruct.specularColor[1])
	WriteFloat(file, entryStruct.specularColor[2])
	WriteFloat(file, entryStruct.specularColor[3])
	
	WriteLong(file, 83) #chunktype
	WriteLong(file, 4 + 4 + getStringSize("SpecularExponent") + 4) #chunksize
	WriteLong(file, 2) #specularExponent
	WriteLong(file, getStringSize("SpecularExponent")) 
	WriteString(file, "SpecularExponent")
	WriteFloat(file, entryStruct.specularExponent)
	
	WriteLong(file, 83) #chunktype
	WriteLong(file, 4 + 4 + getStringSize("AlphaTestEnable") + 1) #chunksize
	WriteLong(file, 7) #alphaTest
	WriteLong(file, getStringSize("AlphaTestEnable")) 
	WriteString(file, "AlphaTestEnable")
	WriteUnsignedByte(file, entryStruct.alphaTestEnable)
	
def getNormalMapChunkSize(normalMap):
	size = HEAD + getNormalMapHeaderChunkSize(normalMap.header)
	size += HEAD + getNormalMapEntryStructSize(normalMap.entryStruct)
	return size

def WriteNormalMap(file, normalMap):
	WriteLong(file, 81) #chunktype
	WriteLong(file, getNormalMapChunkSize(normalMap)) #chunksize

	WriteNormalMapHeader(file, normalMap.header)
	WriteNormalMapEntryStruct(file, normalMap.entryStruct)
	
def getMeshBumpMapArrayChunkSize(bumpMapArray):
	return HEAD + getNormalMapChunkSize(bumpMapArray.normalMap)
	
def WriteMeshBumpMapArray(file, bumpMapArray):
	WriteLong(file, 80) #chunktype
	WriteLong(file, MakeChunkSize(getMeshBumpMapArrayChunkSize(bumpMapArray))) #chunksize

	WriteNormalMap(file, bumpMapArray.normalMap)
	
#######################################################################################
# AABTree (Axis-aligned-bounding-box)
#######################################################################################	

def getAABTreeHeaderChunkSize(header):
	return 8

def WriteAABTreeHeader(file, header):
	WriteLong(file, 145) #chunktype
	WriteLong(file, getAABTreeHeaderChunkSize(header)) #chunksize

	WriteLong(file, header.nodeCount)
	WriteLong(file, header.polyCount)
	
def getAABTreePolyIndicesChunkSize(polyIndices):
	return len(polyIndices) * 4

def WriteAABTreePolyIndices(file, polyIndices):
	WriteLong(file, 146) #chunktype
	WriteLong(file, getAABTreePolyIndicesChunkSize(polyIndices)) #chunksize
	
	for poly in polyIndices:
		WriteLong(file, poly)

def getAABTreeNodesChunkSize(nodes):
	return len(nodes) * 32		
		
def WriteAABTreeNodes(file, nodes):
	WriteLong(file, 147) #chunktype
	WriteLong(file, getAABTreeNodesChunkSize(nodes)) #chunksize
	
	for node in nodes:
		WriteVector(file, node.min)
		WriteVector(file, node.max)
		WriteLong(file, node.frontOrPoly0)
		WriteLong(file, node.backOrPolyCount)
		
def getAABTreeChunkSize(aabtree):
	size = HEAD + getAABTreeHeaderChunkSize(aabtree.header)
	if polySize > 0:
		size += HEAD + getAABTreePolyIndicesChunkSize(aabtree.polyIndices)
	if nodeSize > 0:
		size += HEAD + getAABTreeNodesChunkSize(aabtree.nodes)

def WriteAABTree(file, aabtree):
	WriteLong(file, 144) #chunktype
	WriteLong(file, MakeChunkSize(getAABTreeChunkSize(aabtree))) #chunksize
	
	WriteAABTreeHeader(file, aabtree.header)
	
	if len(aabtree.polyIndices) > 0:
		WriteAABTreePolyIndices(file, aabtree.polyIndices)
	
	if len(aabtree.nodes) > 0:
		WriteAABTreeNodes(file, aabtree.nodes)
		
#######################################################################################
# Mesh
#######################################################################################

def getMeshHeaderChunkSize(header):
	return 116	

def WriteMeshHeader(file, header): 
	WriteLong(file, 31) #chunktype
	WriteLong(file, getMeshHeaderChunkSize(header)) #chunksize
	
	#print("## Name: " + header.meshName)
	WriteLong(file, MakeVersion(header.version)) 
	WriteLong(file, header.attrs) 
	WriteFixedString(file, header.meshName)
	WriteFixedString(file, header.containerName)
	WriteLong(file, header.faceCount) 
	WriteLong(file, header.vertCount) 
	WriteLong(file, header.matlCount)
	WriteLong(file, header.damageStageCount)
	WriteLong(file, header.sortLevel)
	WriteLong(file, header.prelitVersion)
	WriteLong(file, header.futureCount) 
	WriteLong(file, header.vertChannelCount) 
	WriteLong(file, header.faceChannelCount) 
	WriteVector(file, header.minCorner) 
	WriteVector(file, header.maxCorner) 
	WriteVector(file, header.sphCenter) 
	WriteFloat(file, header.sphRadius) 
	
def getMeshChunkSize(mesh):
	size = HEAD + getMeshHeaderChunkSize(mesh.header)
	size += HEAD + getMeshVerticesArrayChunkSize(mesh.verts)
	size += HEAD + getMeshVerticesArrayChunkSize(mesh.normals)
	size += HEAD + getMeshFaceArrayChunkSize(mesh.faces)
	size += HEAD + len(mesh.shadeIds) * 4 #shade indices
	if not mesh.userText == "":
		size += HEAD + getStringSize(mesh.userText)
	if len(mesh.vertInfs) > 0:
		size += HEAD + getMeshVertexInfluencesChunkSize(mesh.vertInfs)
	size += HEAD + getMeshMaterialSetInfoChunkSize(mesh.matInfo)
	if len(mesh.vertMatls) > 0:
		size += HEAD + getMeshMaterialArrayChunkSize(mesh.vertMatls)
	if len(mesh.shaders) > 0:
		size += HEAD + getMeshShaderArrayChunkSize(mesh.shaders)
	if len(mesh.textures) > 0:
		size += HEAD + getTextureArrayChunkSize(mesh.textures)
	if mesh.matInfo.passCount > 0:
		size += HEAD + getMeshMaterialPassChunkSize(mesh.matlPass)
		
	#if not mesh.bumpMaps.normalMap.entryStruct.diffuseTexName == "":
	#	 size += HEAD + getMeshBumpMapArrayChunkSize(mesh.bumpMaps)
	#if (mesh.aabtree.header.nodeCount > 0) or (mesh.aabtree.header.polyCount > 0):
	#	 size += HEAD + getAABTreeChunkSize(mesh.aabtree)
	return size
	
def WriteMesh(file, mesh):
	#print("\n### NEW MESH: ###")
	WriteLong(file, 0) #chunktype
	WriteLong(file, MakeChunkSize(getMeshChunkSize(mesh))) #chunksize
	
	WriteMeshHeader(file, mesh.header)
	#print("Header")
	WriteMeshVerticesArray(file, mesh.verts)
	#print("Vertices")
	WriteMeshNormalArray(file, mesh.normals)
	#print("Normals")
	WriteMeshFaceArray(file, mesh.faces)
	#print("Faces")
	
	WriteLong(file, 34) #chunktype
	WriteLong(file, len(mesh.verts) * 4) #chunksize
	WriteLongArray(file, mesh.shadeIds)
	#print("VertexShadeIndices")	
	
	if not mesh.userText ==	 "":
		WriteLong(file, 12) #chunktype
		WriteLong(file, getStringSize(mesh.userText)) #chunksize
		WriteString(file, mesh.userText)
		#print("UserText")
		
	if len(mesh.vertInfs) > 0:
		WriteMeshVertexInfluences(file, mesh.vertInfs) 
		#print("Vertex Influences")
	
	WriteMeshMaterialSetInfo(file, mesh.matInfo)
	#print("MaterialSetInfo")
	if mesh.matInfo.vertMatlCount > 0:
		WriteMeshMaterialArray(file, mesh.vertMatls)
		#print("Materials")
	if len(mesh.shaders) > 0:
		WriteMeshShaderArray(file, mesh.shaders)
		#print("Shader")
	if len(mesh.textures) > 0:
		WriteTextureArray(file, mesh.textures)
		#print("Textures")
	if mesh.matInfo.passCount > 0:
		WriteMeshMaterialPass(file, mesh.matlPass)
		#print("MaterialPass")
		
	#if not mesh.bumpMaps.normalMap.entryStruct.normalMap == "":
	#	 WriteMeshBumpMapArray(file, mesh.bumpMaps)
		#print("BumpMaps")
	#if (mesh.aabtree.header.nodeCount > 0) or (mesh.aabtree.header.polyCount > 0):
	#	 WriteAABTree(file, mesh.aabtree)
		#print("AABTree")
		
#######################################################################################
# Mesh Sphere
#######################################################################################	

def calculateMeshSphere(mesh, Header):
	# get the point with the biggest distance to x and store it in y
	x = mesh.vertices[0]
	y = mesh.vertices[1]
	dist = ((y.co[0] - x.co[0])**2 + (y.co[1] - x.co[1])**2 + (y.co[2] - x.co[2])**2)**(1/2)
	for v in mesh.vertices:
		curr_dist = ((v.co[0] - x.co[0])**2 + (v.co[1] - x.co[1])**2 + (v.co[2] - x.co[2])**2)**(1/2)
		if (curr_dist > dist):
			dist = curr_dist
			y = v
					
	#get the point with the biggest distance to y and store it in z
	z = mesh.vertices[2]
	dist = ((z.co[0] - y.co[0])**2 + (z.co[1] - y.co[1])**2 + (z.co[2] - y.co[2])**2)**(1/2)
	for v in mesh.vertices:
		curr_dist = ((v.co[0] - y.co[0])**2 + (v.co[1] - y.co[1])**2 + (v.co[2] - y.co[2])**2)**(1/2)
		if (curr_dist > dist):
			dist = curr_dist
			z = v	
			 
	# the center of the sphere is between y and z
	vec_y = Vector(y.co.xyz)
	vec_z = Vector(z.co.xyz)
	y_z = ((vec_z - vec_y)/2)
	m = Vector(vec_y + y_z)
	radius = y_z.length

	#test if any of the vertices is outside the sphere (if so update the sphere)
	for v in mesh.vertices:
		curr_dist = ((v.co[0] - m[0])**2 + (v.co[1] - m[1])**2 + (v.co[2] - m[2])**2)**(1/2)
		if curr_dist > radius:
			delta = (curr_dist - radius)/2
			radius += delta
			m += (Vector(v.co.xyz - m)).normalized() * delta		
	Header.sphCenter = m
	Header.sphRadius = radius
	
#######################################################################################
# get Animation data
#######################################################################################	
	
def getAnimationData(context, aniName, rig, Hierarchy):
	Animation = struct_w3d.Animation()
	Animation.header.name = aniName
	Animation.header.hieraName = Hierarchy.header.name
	Animation.header.numFrames = bpy.data.scenes["Scene"].frame_end
	Animation.header.frameRate = bpy.data.scenes["Scene"].render.fps

	rigList = [object for object in bpy.context.scene.objects if object.type == 'ARMATURE']
	if len(rigList) == 1:
		rig = rigList[0]
		index = 0
		for pivot in Hierarchy.pivots:
			if pivot.name == "ROOTTRANSFORM":
				index += 1
				continue
			
			rest_location = pivot.position
			rest_rotation = pivot.rotation
			
			try:
				obj = rig.pose.bones[pivot.name]
			except:
				obj = bpy.data.objects[pivot.name]
				
			qChannel = struct_w3d.AnimationChannel()
			qChannel.firstFrame = 0
			qChannel.lastFrame = bpy.data.scenes["Scene"].frame_end - 1
			qChannel.vectorLen = 4
			qChannel.type = 6
			qChannel.pivot = index
			qChannel.data = []
				
			if obj.parent == None:
				xChannel = struct_w3d.AnimationChannel()
				xChannel.firstFrame = 0
				xChannel.lastFrame = bpy.data.scenes["Scene"].frame_end - 1
				xChannel.vectorLen = 1
				xChannel.type = 0
				xChannel.pivot = index
				xChannel.data = []
				
				yChannel = struct_w3d.AnimationChannel()
				yChannel.firstFrame = 0
				yChannel.lastFrame = bpy.data.scenes["Scene"].frame_end - 1
				yChannel.vectorLen = 1
				yChannel.type = 1
				yChannel.pivot = index
				yChannel.data = []
				
				zChannel = struct_w3d.AnimationChannel()
				zChannel.firstFrame = 0
				zChannel.lastFrame = bpy.data.scenes["Scene"].frame_end - 1
				zChannel.vectorLen = 1
				zChannel.type = 2
				zChannel.pivot = index
				zChannel.data = []
			
			for frame in range(0, Animation.header.numFrames - 1):
				bpy.context.scene.frame_set(frame)
				bpy.context.scene.update()

				qChannel.data.append(pivot.rotation - obj.rotation_quaternion)

				if obj.parent == None:
					xChannel.data.append(pivot.position.x - obj.location.x)
					yChannel.data.append(pivot.position.y - obj.location.y)
					zChannel.data.append(pivot.position.z - obj.location.z)
			
			if obj.parent == None:
				Animation.channels.append(xChannel)
				Animation.channels.append(yChannel)
				Animation.channels.append(zChannel)
			Animation.channels.append(qChannel)
			index += 1
	else:
		context.report({'ERROR'}, "only one armature allowed!")
		print("Error: only one armature allowed!") 
	return Animation
				
#######################################################################################
# Main Export
#######################################################################################	

def MainExport(givenfilepath, self, context, EXPORT_MODE = 'M'):
	#print("Run Export")
	HLod = struct_w3d.HLod()
	HLod.lodArray.subObjects = []
	Hierarchy = struct_w3d.Hierarchy()
	amtName = ""
	
	roottransform = struct_w3d.HierarchyPivot()
	roottransform.name = "ROOTTRANSFORM"
	roottransform.parentID = -1
	Hierarchy.pivots.append(roottransform)
	
	#switch to object mode
	if bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')
	
	# Get all the armatures in the scene.
	rigList = [object for object in bpy.context.scene.objects if object.type == 'ARMATURE']
	if len(rigList) == 1:
		rig = rigList[0]
		amtName = rig.name
		for bone in rig.pose.bones:
			pivot = struct_w3d.HierarchyPivot()
			pivot.name = bone.name
			if not bone.parent == None:
				ids = [index for index, pivot in enumerate(Hierarchy.pivots) if pivot.name == bone.parent.name] #return an array of indices (in this case only one value)
				pivot.parentID = ids[0]
			else:
				pivot.parentID = 0
			pivot.position = bone.location
			pivot.eulerAngles = bone.rotation_euler
			pivot.rotation = bone.rotation_quaternion
			Hierarchy.pivots.append(pivot)	
	else:
		context.report({'ERROR'}, "only one armature allowed!")
		print("Error: only one armature allowed!")			

	# Get all the mesh objects in the scene.
	objList = [object for object in bpy.context.scene.objects if object.type == 'MESH']
	
	if EXPORT_MODE == 'M' or EXPORT_MODE == 'HAM':
		sknFile = open(givenfilepath, "wb")
		containerName = (os.path.splitext(os.path.basename(sknFile.name))[0]).upper()
		
		for mesh_ob in objList: 
			if mesh_ob.name == "BOUNDINGBOX":
				Box = struct_w3d.Box()
				Box.name = containerName + "." + mesh_ob.name
				Box.center = mesh_ob.location
				box_mesh = mesh_ob.to_mesh(bpy.context.scene, False, 'PREVIEW', calc_tessface = True)
				Box.extend = Vector((box_mesh.vertices[0].co.x * 2, box_mesh.vertices[0].co.y * 2, box_mesh.vertices[0].co.z))
			
				WriteBox(sknFile, Box)
			else:
				Mesh = struct_w3d.Mesh()
				Header = struct_w3d.MeshHeader()
				Mesh.bumpMaps = struct_w3d.MeshBumpMapArray()
				Mesh.matInfo = struct_w3d.MeshMaterialSetInfo()		
				Mesh.aabtree = struct_w3d.MeshAABTree()
				Mesh.aabtree.header = struct_w3d.AABTreeHeader()			
		
				verts = []
				normals = [] 
				faces = []
				vertInfs = []
				vertexShadeIndices = []

				Header.meshName = mesh_ob.name
				Header.containerName = containerName
				mesh = mesh_ob.to_mesh(bpy.context.scene, False, 'PREVIEW', calc_tessface = True)
		
				triangulate(mesh)
		
				Header.vertCount = len(mesh.vertices)
				Mesh.matlPass.txStage.txCoords = []
				Mesh.vertInfs = []
				group_lookup = {g.index: g.name for g in mesh_ob.vertex_groups}
				groups = {name: [] for name in group_lookup.values()}
				vertShadeIndex = 0
				for v in mesh.vertices:
					vertexShadeIndices.append(vertShadeIndex)
					vertShadeIndex += 1
					verts.append(v.co.xyz)
					normals.append(v.normal)
					Mesh.matlPass.txStage.txCoords.append((0.0, 0.0)) #just to fill the array 
				
					#vertex influences
					vertInf = struct_w3d.MeshVertexInfluences()
					if len(v.groups) > 0:
						#has to be this complicated, otherwise the vertex groups would be corrupted
						ids = [index for index, pivot in enumerate(Hierarchy.pivots) if pivot.name == mesh_ob.vertex_groups[v.groups[0].group].name] #return an array of indices (in this case only one value)
						if len(ids) > 0:
							vertInf.boneIdx = ids[0]
						vertInf.boneInf = v.groups[0].weight
						Mesh.vertInfs.append(vertInf)
					elif len(v.groups) > 1:
						#has to be this complicated, otherwise the vertex groups would be corrupted
						ids = [index for index, pivot in enumerate(Hierarchy.pivots) if pivot.name == mesh_ob.vertex_groups[v.groups[0].group].name] #return an array of indices (in this case only one value)
						if len(ids) > 0:
							vertInf.boneIdx = ids[0]
						vertInf.boneInf = v.groups[0].weight
						#has to be this complicated, otherwise the vertex groups would be corrupted
						ids = [index for index, pivot in enumerate(Hierarchy.pivots) if pivot.name == mesh_ob.vertex_groups[v.groups[1].group].name] #return an array of indices (in this case only one value)
						if len(ids) > 0:
							vertInf.boneIdx = ids[0]
						vertInf.xtraInf = v.groups[1].weight
						Mesh.vertInfs.append(vertInf)
					elif len(v.groups) > 2: 
						context.report({'ERROR'}, "max 2 bone influences per vertex supported!")
						print("Error: max 2 bone influences per vertex supported!")
	
				calculateMeshSphere(mesh, Header)
			
				Mesh.verts = verts
				Mesh.normals = normals
				Mesh.shadeIds = vertexShadeIndices
				Header.minCorner = Vector((mesh_ob.bound_box[0][0], mesh_ob.bound_box[0][1], mesh_ob.bound_box[0][2]))
				Header.maxCorner =	Vector((mesh_ob.bound_box[6][0], mesh_ob.bound_box[6][1], mesh_ob.bound_box[6][2]))

				for face in mesh.polygons:
					triangle = struct_w3d.MeshFace()
					triangle.vertIds = [face.vertices[0], face.vertices[1], face.vertices[2]]
					triangle.normal = face.normal
					tri_x = (verts[face.vertices[0]].x + verts[face.vertices[1]].x + verts[face.vertices[2]].x)/3
					tri_y = (verts[face.vertices[0]].y + verts[face.vertices[1]].y + verts[face.vertices[2]].y)/3
					tri_z = (verts[face.vertices[0]].z + verts[face.vertices[1]].z + verts[face.vertices[2]].z)/3
					tri_pos = Vector((tri_x, tri_y, tri_z))				
					triangle.distance = (mesh_ob.location - tri_pos).length
					faces.append(triangle)
				Mesh.faces = faces
			
				try:
					Mesh.userText = mesh_ob['userText'] 
				except:
					print("no userText")
			
				Header.faceCount = len(faces)
				#Mesh.aabtree.header.polyCount = len(faces)
			
				#uv coords
				bm = bmesh.new()
				bm.from_mesh(mesh)

				uv_layer = bm.loops.layers.uv.verify()
				#bm.faces.layers.tex.verify()
			
				index = 0
				for f in bm.faces:
					Mesh.matlPass.txStage.txCoords[Mesh.faces[index].vertIds[0]] = f.loops[0][uv_layer].uv
					Mesh.matlPass.txStage.txCoords[Mesh.faces[index].vertIds[1]] = f.loops[1][uv_layer].uv
					Mesh.matlPass.txStage.txCoords[Mesh.faces[index].vertIds[2]] = f.loops[2][uv_layer].uv
					index+=1
						
				Mesh.matlPass.vmIds = []
				Mesh.matlPass.shaderIds = []
				Mesh.matlPass.txStage.txIds = []
				Mesh.matlPass.vmIds.append(0)
				Mesh.matlPass.shaderIds.append(0)
				Mesh.matlPass.txStage.txIds.append(0)	   
					
				#shader
				shader = struct_w3d.MeshShader()
				Mesh.shaders = []
				Mesh.shaders.append(shader)
				Mesh.matInfo.shaderCount = 1
				
				Mesh.vertMatls = [] 
				Mesh.textures = [] 
				meshMaterial = struct_w3d.MeshMaterial()
				vertexMaterial = struct_w3d.VertexMaterial()
			
				for mat in mesh.materials:
					matName = (os.path.splitext(os.path.basename(mat.name))[1])[1:]
					if matName == "BumpMaterial":
						Mesh.matInfo.shaderCount = 0
						for tex in bpy.data.materials[mesh_ob.name + "." + matName].texture_slots:
							if not (tex == None):
								if '_NRM' in tex.name:
									Header.vertChannelCount = 99
									Mesh.bumpMaps.normalMap.entryStruct.normalMap = tex.name
								else:
									Mesh.bumpMaps.normalMap.entryStruct.diffuseTexName = tex.name	
					else:
						Mesh.matInfo.vertMatlCount += 1
						meshMaterial.vmName = matName
						vertexMaterial.ambient = struct_w3d.RGBA(r = 255, g = 255, b = 255, a = 255)
						vertexMaterial.diffuse = struct_w3d.RGBA(r = int(mat.diffuse_color.r), g = int(mat.diffuse_color.g), b = int(mat.diffuse_color.b), a = 255)
						vertexMaterial.specular = struct_w3d.RGBA(r = int(mat.specular_color.r), g = int(mat.specular_color.g), b = int(mat.specular_color.b), a = 255)
						vertexMaterial.shininess = 1.0#mat.specular_intensity
						vertexMaterial.opacity = 1.0#mat.diffuse_intensity		   
						meshMaterial.vmInfo = vertexMaterial
						Mesh.vertMatls.append(meshMaterial)
						if not meshMaterial.vmName == "":
							for tex in bpy.data.materials[mesh_ob.name + "." + meshMaterial.vmName].texture_slots:
								if not (tex == None):
									Mesh.matInfo.textureCount += 1
									texture = struct_w3d.Texture()
									texture.name = tex.name
									Mesh.textures.append(texture)

				Header.matlCount = len(Mesh.vertMatls)
			
				if len(mesh_ob.vertex_groups) > 0:		 
					Header.attrs = 131072 #type skin
					Header.vertChannelCount = 19
				else:
					Header.attrs = 0 #type normal mesh
				
					pivot = struct_w3d.HierarchyPivot()
					pivot.name = mesh_ob.name
					pivot.parentID = 0
					if not mesh_ob.parent_bone == "":
						ids = [index for index, pivot in enumerate(Hierarchy.pivots) if pivot.name == mesh_ob.parent_bone] #return an array of indices (in this case only one value)
						pivot.parentID = ids[0]
					pivot.position = mesh_ob.location
					pivot.eulerAngles = mesh_ob.rotation_euler
					pivot.rotation = mesh_ob.rotation_quaternion
					Hierarchy.pivots.append(pivot)	
				   
				Mesh.header = Header			
				WriteMesh(sknFile, Mesh)
			
			#HLod stuff
			subObject = struct_w3d.HLodSubObject()
			subObject.name = containerName + "." + mesh_ob.name
			subObject.boneIndex = 0
			ids = [index for index, pivot in enumerate(Hierarchy.pivots) if pivot.name == mesh_ob.name] #return an array of indices (in this case only one value)
			if len(ids) > 0:
				#if the mesh is of type skin, the bone is created for this mesh and the boneIndex in HLod is 0
				if Header.attrs == 0 or Header.attrs == 8192 or Header.attrs == 32768 or Header.attrs == 40960:
					subObject.boneIndex = ids[0]
			HLod.lodArray.subObjects.append(subObject)

	Hierarchy.header.pivotCount = len(Hierarchy.pivots)
		
	sklPath = givenfilepath.replace(".w4d", "_skl.w4d")
	sklName = (os.path.splitext(os.path.basename(sklPath))[0])
	
	if EXPORT_MODE == 'HAM' or EXPORT_MODE == 'S' or EXPORT_MODE == 'M':
		if len(rigList) == 1:
			if EXPORT_MODE == 'S':
				sklFile = open(sklPath.replace(sklName, amtName.lower()), "wb")
				Hierarchy.header.name = sklName
				WriteHierarchy(sklFile, Hierarchy)
				sklFile.close()
			elif EXPORT_MODE == 'M':
				HLod.header.HTreeName = amtName
				
		#write the hierarchy to the skn file (has no armature data)
		elif EXPORT_MODE == 'HAM':
			Hierarchy.header.name = containerName 
			WriteHierarchy(sknFile, Hierarchy)
			HLod.header.HTreeName = containerName
		else:
			context.report({'ERROR'}, "no armature data available!!")
			print("no armature data available!!")

	if EXPORT_MODE == 'A' or EXPORT_MODE == 'HAM':
		if EXPORT_MODE == 'A':
			aniFile = open(givenfilepath, "wb")
			aniName = (os.path.splitext(os.path.basename(aniFile.name))[0]).upper()
			Hierarchy.header.name = amtName
			Animation = getAnimationData(context, aniName, rig, Hierarchy)
			WriteAnimation(aniFile, Animation)
			aniFile.close()
		else:
			Animation = getAnimationData(context, containerName, rig, Hierarchy)
			WriteAnimation(sknFile, Animation)
	
	if EXPORT_MODE == 'M' or EXPORT_MODE == 'HAM':
		HLod.lodArray.header.modelCount = len(HLod.lodArray.subObjects)
		HLod.header.modelName = containerName
		WriteHLod(sknFile, HLod)

	try:
		sknFile.close()	 
	except:
		print("")