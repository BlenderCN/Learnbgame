"""
Suicidator City Generator's Blender addon
Official website: http://cgchan.com/suicidator
Author: Arnaud Couturier (piiichan) couturier.arnaud@gmail.com
Licence: you can modify and reditribute this file as you wish.
"""

import bpy
import bmesh
import subprocess
import os
import time
import sys
import imp
import webbrowser
import re
import pickle
import math
import random


SCG_JAR_FILE_PATH = os.path.join(
	os.path.dirname(__file__),
	'SCG.jar')
	
bl_info = {
	"name": "Suicidator City Generator",
	"author": "Arnaud Couturier (piiichan)",
	"version": (0,5,7),
	"blender": (2, 6, 3),
	"api": 45996,
	"location": "View3D > Tool Shelf > 3D Nav",
	"description": "Build large and detailed cities very easily. Buy the Pro version for even more details and options.",
	"category": "Learnbgame"
}

	
#--------------------------------------------------------------------------------------------------------------------

# launches JAR
# returns (stdout,stderr,javaIsRecognized) if possible, (None,None) otherwise
# args = CLI array, only give VM and program arguments
def execJAR(cliArg, Xms=64, Xmx=64):
	stdOut = stdErr = None
	javaIsRecognized = False
	try:
		command = ['java','-Xms'+str(Xms)+'m','-Xmx'+str(Xmx)+'m','-jar',SCG_JAR_FILE_PATH]
		command.extend(cliArg)
		javaProcess = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		javaIsRecognized = True
		stdOut, stdErr = javaProcess.communicate()
	except Exception as e:
		print("Warning: \"java\" command unknown! ("+str(e)+") It the java bin folder in your PATH environment variable? Trying to execute JAR file without the java command as last chance...")
		try:
			javaProcess = subprocess.Popen('"'+SCG_JAR_FILE_PATH+'" '+''.join([" "+arg for arg in cliArg]), stdout=subprocess.PIPE, shell=True)
			stdOut, stdErr = javaProcess.communicate()
		except Exception as e:
			print("Cannot execute Java ("+str(e)+"). It is needed. Have you installed it?")
	return stdOut, stdErr, javaIsRecognized
	
#--------------------------------------------------------------------------------------------------------------------

# check java
JAVA_VERSION_STRING = None
JAVA_VERSION = None
try:
	javaOutput, javaError, javaIsRecognized = execJAR(['-showJavaVersion'])
	
	#JAVA_IS_DETECTED = len(exceptions) <= 0
	
	JAVA_VERSION_STRING = javaOutput.decode('UTF-8')
	JAVA_VERSION = JAVA_VERSION_STRING.split(".")
	JAVA_VERSION[0] = int(re.sub(r'[^0-9]','',JAVA_VERSION[0]))
	JAVA_VERSION[1] = int(re.sub(r'[^0-9]','',JAVA_VERSION[1]))
	JAVA_VERSION[2] = int(re.sub(r'[^0-9]','',JAVA_VERSION[2]))
	
except Exception as e:
	print("Couldn't get java version from string '"+JAVA_VERSION_STRING+"': "+str(e))


meshOps = bpy.ops.mesh
objectOps = bpy.ops.object
sys.path.append(bpy.app.tempdir)


#--------------------------------------------------------------------------------------------------------------------

def getOrCreateMesh(name):
	mesh = None
	try:
		mesh = bpy.data.meshes[name]
	except KeyError:
		mesh = bpy.data.meshes.new(name)
	return mesh
	
#--------------------------------------------------------------------------------------------------------------------

# returns the new mesh assigned to the object
def clearMeshOfObject(objectName):
	if objectName not in bpy.data.objects.keys():
		return
	initialMode = bpy.context.mode
	set_mode('OBJECT')
	object = bpy.data.objects[objectName]
	
	# create a new mesh, rename and delete old one
	oldMesh = object.data
	objectMeshName = object.data.name
	object.data.name = object.data.name + '_old'
	newMesh = bpy.data.meshes.new(objectMeshName)
	object.data = newMesh
	try:
		bpy.data.meshes.remove(oldMesh)
	except Error:
		pass
	set_mode(initialMode)
	object.hide = object.hide_select = object.hide_render = False
	return newMesh
		
#--------------------------------------------------------------------------------------------------------------------

def getOrCreateCurve(name):
	curve = None
	try:
		curve = bpy.data.curves[name]
	except:
		curve = bpy.data.curves.new(name, 'CURVE')
	return curve
		
#--------------------------------------------------------------------------------------------------------------------

def getOrCreateObject(name, data, scale=1):
	obj = None
	try:
		obj = bpy.data.objects[name]
		obj.data = data
	except KeyError:
		obj = bpy.data.objects.new(name, data)
		bpy.context.scene.objects.link(obj)
		obj.scale = (scale, scale, scale)
	return obj
	
#--------------------------------------------------------------------------------------------------------------------

def set_mode(mode):
	if bpy.context.mode != mode:
		bpy.ops.object.mode_set(mode=mode)
		
#--------------------------------------------------------------------------------------------------------------------

def hide_SCG_objects():
	for object in bpy.data.objects:
		if object.name.startswith('SCG_'):
			object.hide = object.hide_render = True
#--------------------------------------------------------------------------------------------------------------------

def scale_SCG_objects_around_origin(scale):
	for object in bpy.data.objects:
		if object.parent is None and object.name.startswith('SCG_'):
			object.scale = scale, scale, scale
			object.location.x /= scale
			object.location.y /= scale
			object.location.z /= scale
			
#--------------------------------------------------------------------------------------------------------------------

def delete_SCG_objects():
	initialMode = bpy.context.mode
	set_mode('OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	for object in bpy.data.objects:
		if object.name.startswith('SCG_'):
			object.select = True
			if object.hide:
				object.hide = False
	bpy.ops.object.delete()
	set_mode(initialMode)
	
#--------------------------------------------------------------------------------------------------------------------

def getOrCreateMaterial(name, specular_intensity=.05, specular_hardness=100):
	material = None
	try:
		material = bpy.data.materials[name]
	except KeyError:
		material = bpy.data.materials.new(name)
		material.specular_intensity = specular_intensity
	return material
	
#--------------------------------------------------------------------------------------------------------------------

def set_faces_material_index(mesh, faceIndicesByMatName, matIndicesByMatName):
	for materialName, materialFaces in faceIndicesByMatName.items():
		matIndex = matIndicesByMatName[materialName]
		for faceNb in materialFaces:
			mesh.tessfaces[faceNb].material_index = matIndex
	
#--------------------------------------------------------------------------------------------------------------------

# returns material index
def add_material_to_mesh(material, mesh):

	for i in range(len(mesh.materials)):
		if mesh.materials[i] == material:
			return i
			
	for i in range(len(mesh.materials)):
		if mesh.materials[i] == None:
			mesh.materials[i] = material
			return i
			
	mesh.materials.append(material)
	return len(mesh.materials)-1
	
#--------------------------------------------------------------------------------------------------------------------

def clear_material_nodes(material):
	try:
		for node in material.node_tree.nodes:
			material.node_tree.nodes.remove(node)
	except:
		pass
	
#--------------------------------------------------------------------------------------------------------------------

def clear_material_slots(material):
	if material is None:
		return
	for i in range(len(material.texture_slots)):
		material.texture_slots.clear(i)
	
#--------------------------------------------------------------------------------------------------------------------

def getOrLoadImage(name, url, reload=False):
	img = None
	try:
		img = bpy.data.images[name]
		if reload:
			img.reload()
	except KeyError:
		try:
			img = bpy.data.images.load(filepath=url)
		except:
			pass
	return img
	
#--------------------------------------------------------------------------------------------------------------------

# returns uv layer
def get_or_create_uv_layer(uvLayerName, mesh):
	if uvLayerName in mesh.tessface_uv_textures:
		return mesh.tessface_uv_textures[uvLayerName]
	newUVLayerName = mesh.uv_textures.new().name
	uvLayer = mesh.tessface_uv_textures[newUVLayerName]
	uvLayer.name = uvLayerName
	return uvLayer
	
#--------------------------------------------------------------------------------------------------------------------

# Method useful for backward compatibility because shader nodes' names changed with Blender 2.67
# node_type: 
def add_material_node(target_node_tree, node_type):
	result_node = None
	alternative_node_type = None
	
	if node_type == "GEOMETRY":
		alternative_node_type = "ShaderNodeGeometry"
	elif node_type == "MATERIAL_EXT":
		alternative_node_type = "ShaderNodeExtendedMaterial"
	elif node_type == "MIX_RGB":
		alternative_node_type = "ShaderNodeMixRGB"
	if node_type == "MATERIAL":
		alternative_node_type = "ShaderNodeMaterial"
	elif node_type == "TEXTURE":
		alternative_node_type = "ShaderNodeTexture"
	elif node_type == "OUTPUT":
		alternative_node_type = "ShaderNodeOutput"
		
	try:
		result_node = target_node_tree.nodes.new(type = node_type)
	except RuntimeError:
		result_node = target_node_tree.nodes.new(type = alternative_node_type)
	return result_node

#--------------------------------------------------------------------------------------------------------------------

def unwrap_mesh_from_data(mesh, uvLayer, facesMaterials, facesData):
	
	unwrappedFaces = facesData.keys()
	
	for faceNb, face in enumerate(mesh.polygons):
		
		if faceNb not in unwrappedFaces:
			continue
			
		faceData = facesData[faceNb]
		faceUVs = uvLayer.data[faceNb]
		
		faceUVs.uv1 = faceData[0], faceData[1]
		faceUVs.uv2 = faceData[2], faceData[3]
		faceUVs.uv3 = faceData[4], faceData[5]
		faceUVs.uv4 = faceData[6], faceData[7]
	
#--------------------------------------------------------------------------------------------------------------------

def getOrCreateTexture(name, type):
	texture = None
	try:
		texture = bpy.data.textures[name]
	except KeyError:
		texture = bpy.data.textures.new(name=name, type=type)
	return texture
	
#--------------------------------------------------------------------------------------------------------------------

def add_texture_to_material(texture, material):
	for textureSlot in material.texture_slots.values():
		if textureSlot != None and textureSlot.texture == texture:
			return textureSlot
	newTextureSlot = material.texture_slots.add()
	newTextureSlot.texture = texture
	return newTextureSlot
	
#--------------------------------------------------------------------------------------------------------------------

class SCG_show_manual_op(bpy.types.Operator):
	bl_idname = "object.scg_show_website"
	bl_description = "If you need help"
	bl_label = ""
	
	def execute(self, context):
		webbrowser.open_new_tab("http://arnaud.ile.nc/sce")
		return {'FINISHED'}		
	
#--------------------------------------------------------------------------------------------------------------------

class SCG_open_options_op(bpy.types.Operator):
	bl_idname = "object.scg_open_options"
	bl_description = "Set the generator options: city size, complexity, input and output"
	bl_label = ""

	def execute(self, context):
		javaOutput, javaError, javaIsRecognized = execJAR(['-showOptions'])
		return {'FINISHED'}

#--------------------------------------------------------------------------------------------------------------------

class SCG_activate_glsl_op(bpy.types.Operator):
	bl_idname = "object.scg_activate_glsl"
	bl_description = "Activates GLSL shading, so you can preview your city materials. Good graphics card needed: ATI or NVIDIA"
	bl_label = ""

	def execute(self, context):
		bpy.context.scene.game_settings.material_mode = 'GLSL'
		bpy.context.space_data.viewport_shade = 'TEXTURED'
		return {'FINISHED'}

#--------------------------------------------------------------------------------------------------------------------

class SCG_delete_objects_op(bpy.types.Operator):
	bl_idname = "object.scg_delete_objects"
	bl_description = "Remove all objects created by SCG. Useful if your scene gets cluttered by all the objects SCG creates"
	bl_label = ""

	def execute(self, context):
		delete_SCG_objects()
		return {'FINISHED'}

#--------------------------------------------------------------------------------------------------------------------

class SCG_build_city_op(bpy.types.Operator):
	bl_idname = "object.scg_build_city"
	bl_description = "Build the city, according to your settings. May take some time. Experiment with small cities first."
	bl_label = ""

	def execute(self, context):
		print("SCG starts city generation...")
		startTime = time.time()
		
		# delete previous output
		try:
			os.remove(os.path.join(bpy.app.tempdir, 'SCG_output.py'))
		except Exception as e:
			print("Could not remove previous SCG output because: "+str(e))
			
		
		javaOutput, javaError, javaIsRecognized = execJAR(['-generateCity', '-outputDir', '"'+bpy.app.tempdir+'"'], 64, bpy.context.scene.SCG_java_heap_max_size)
		print('java part done in '+str(time.time() - startTime))
		print('java said: ')
		try:
			print(javaOutput.decode(encoding='UTF-8'))
			print(javaError.decode(encoding='UTF-8'))
		except Exception as e:
			pass
		
		hide_SCG_objects()
		
		
		file, pathname, description = imp.find_module('SCG_output', [bpy.app.tempdir])
		SCG_output = imp.load_module('SCG_output', file, pathname, description)
		scale_SCG_objects_around_origin(.01)
		
		print("SCG made your city in "+str(time.time() - startTime))
		return {'FINISHED'}

#--------------------------------------------------------------------------------------------------------------------

class SCGPanel(bpy.types.Panel):
	bl_idname = "VIEW3D_PT_scg"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_label = "Suicidator City Generator "+str(bl_info["version"])

	def draw(self, context):
		layout = self.layout
		#view = context.space_data
		
		
		
		row = layout.row(align=True)
		#if not JAVA_IS_DETECTED:
			#row.label("Warning: Java can't be detected, SCG may not work", icon="ERROR")
		if not JAVA_VERSION or len(JAVA_VERSION) < 3:
			row.label("Java not found, SCG may not work", icon="ERROR")
		elif JAVA_VERSION[1] < 5:
			row.label("Error: Java is too old ("+str(JAVA_VERSION[1])+"."+str(JAVA_VERSION[2])+") SCG won't run", icon="ERROR")
		elif JAVA_VERSION[1] == 5:
			row.label("Java is ok but very old ("+str(JAVA_VERSION[1])+"."+str(JAVA_VERSION[2])+")", icon="FILE_TICK")
		elif JAVA_VERSION[1] == 6 and JAVA_VERSION[2] < 26:
			row.label("Java is ok but old ("+str(JAVA_VERSION[1])+"."+str(JAVA_VERSION[2])+")", icon="FILE_TICK")
		elif JAVA_VERSION[1] == 6 and JAVA_VERSION[2] >= 26:
			row.label("Java ok ("+str(JAVA_VERSION[1])+"."+str(JAVA_VERSION[2])+")", icon="FILE_TICK")
		elif JAVA_VERSION[1] >= 7:
			row.label("Java is optimal ("+str(JAVA_VERSION[1])+"."+str(JAVA_VERSION[2])+")", icon="FILE_TICK")
		else:
			row.label("Java OK "+str(JAVA_VERSION[1]))
		
		
		row = layout.row()
		row.prop(bpy.context.scene, "SCG_java_heap_max_size", slider=True)
		row = layout.row()
		row.operator("object.scg_show_website", text="Visit website")
		row = layout.row()
		row.operator("object.scg_delete_objects", text="Delete all SCG objects")
		
		row = layout.row()
		row.operator("object.scg_open_options", text="Set city options")
		row = layout.row()
		#row.alignment = 'LEFT'
		row.operator("object.scg_build_city", text="BUILD CITY", icon="OBJECT_DATAMODE")
		row = layout.row()
		row.operator("object.scg_activate_glsl", text="Preview city textures (GLSL)", icon="FACESEL_HLT")
		#row = layout.row()
		#row.label("Buy Pro for better cities")
		
#--------------------------------------------------------------------------------------------------------------------

def register():
	bpy.types.Scene.SCG_java_heap_max_size = bpy.props.IntProperty(default=256, name="Max potential RAM (MB)", description="Warning: increase ONLY if SCG needs more RAM and if your system has that much free memory. It's not even guaranteed values above 1200 will work.", min=128, max=4096)
	bpy.utils.register_module(__name__)

def unregister():
	del bpy.types.Scene.SCG_java_heap_max_size
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()