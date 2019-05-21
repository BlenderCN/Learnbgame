bl_info = {
	"name": "Brender Panel Addon",
	"description": "Creates a panel to edit Brender Animations.",
	"author": "Lopez, Gustavo", # and Feras Khemakhem!
	'version': (1, 6, 0),
	'blender': (2, 6, 7),
	"location": "3D View > Tools",
	"warning": "", # used for warning icon and text in addons panel
	"wiki_url": "",
	"tracker_url": "",
	"category": "Development",
}

import bpy, os
import mathutils
import fnmatch
import json

from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper

from bpy.props import *

from bpy.types import (Panel,
					   Operator,
					   PropertyGroup,
					   )


class View3DPanel:
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'

class CyclesButtonsPanel:
	bl_space_type = "PROPERTIES"
	bl_region_type = "TOOLS"
	bl_context = "objectmode"
	COMPAT_ENGINES = {'CYCLES'}

	@classmethod
	def poll(cls, context):
		rd = context.scene.render
		return rd.engine in cls.COMPAT_ENGINES

###############################################################################
#		Properties will be stored in active scene
###############################################################################


def WireFrameUpdateFunction(self, context):
	bpy.ops.console.clear()
	#print("send noods")
	self.wireframe_toggle = True
	self.report({'INFO'}, 'hi')
	print("In update func...")
	context.scene.render.use_freestyle = True
	context.scene.select_edge_mark = True
	#context.scene.render.layers["RenderLayer"].use_freestyle = self.wireframe_toggle
	return


class BrenderSettings(PropertyGroup):

	testvar = FloatProperty(
		name = "TestVariable",
		description = "A float property",
		default = 0.0,
		step = 1.0,
		precision=1
		)

	x_rot_float = FloatProperty(
		name = "X",
		description = "A float property",
		default = 0.0,
		step = 1.0,
		precision=1
		)

	y_rot_float = FloatProperty(
		name = "Y",
		description = "A float property",
		default = 0.0,
		step = 1.0,
		precision=1
		)

	z_rot_float = FloatProperty(
		name = "Z",
		description = "A float property",
		default = 0.0,
		step = 1.0,
		precision=1
		)

	x_scale_float = FloatProperty(
		name = "X",
		description = "A float property",
		default = 1.0,
		min = 0.01,
		max = 30.0,
		step = 1.0
		)

	y_scale_float = FloatProperty(
		name = "Y",
		description = "A float property",
		default = 1.0,
		min = 0.01,
		max = 30.0,
		step = 1.0
		)

	z_scale_float = FloatProperty(
		name = "Z",
		description = "A float property",
		default = 1.0,
		min = 0.01,
		max = 30.0,
		step = 1.0
		)

	x_trans_float = FloatProperty(
		name = "X",
		description = "A float property",
		default = 0.0,
		min = -100.0,
		max = 100.0,
		step = 1.0
		)

	y_trans_float = FloatProperty(
		name = "Y",
		description = "A float property",
		default = 0.0,
		min = -100.0,
		max = 100.0,
		step = 1.0
		)

	z_trans_float = FloatProperty(
		name = "Z",
		description = "A float property",
		default = 0.0,
		min = -100.0,
		max = 100.0,
		step = 1.0
		)
	
	wf_bevel_depth = FloatProperty(
		name = "Depth",
		description = "A float property",
		default = 0.001,
		min = 0.000,
		max = 0.500,
		step = 0.1,
		precision = 3
		)

	wf_bevel_resolution = IntProperty(
		name = "Resolution",
		description = "A float property",
		default = 2,
		min = 0,
		max = 10
		)

	frameskip = IntProperty(
		name = "",
		description = "An integer property",
		default = 0,
		min = 0,
		max = 100
		)

	wf_offset = FloatProperty(
		name = "Offset",
		description = "A float property",
		default = 0.000,
		min = 0.000,
		max = 0.500,
		step = 0.1,
		precision = 3
		)

	wf_extrude = FloatProperty(
		name = "Extrude",
		description = "A float property",
		default = 0.000,
		min = 0.000,
		max = 0.500,
		step = 0.1,
		precision = 3
		)

	wireframe_obj_string = StringProperty(
		name="Wireframe Object Name",
		description=":",
		default="",
		maxlen=1024,
		)

	checker_mat_obj_string = StringProperty(
		name="Checker Material Object Name",
		description=":",
		default="",
		maxlen=1024,
		)

	blue_mat_obj_string = StringProperty(
		name="Blue Material Object Name",
		description=":",
		default="",
		maxlen=1024,
		)

	process_obj_name = StringProperty(
		name="Process Object Name",
		description=":",
		default="*_Cloth3D",
		maxlen=1024,
		)

	process_mat = StringProperty(
		name="Process Material Name",
		description=":",
		default="!ClothMaterial",
		maxlen=1024,
		)

	mat_scale = FloatProperty(
		name = "Material Scale",
		description = "A float property",
		default = 5.000,
		min = 0.001,
		max = 0.500,
		step = 0.1,
		precision = 3
		)

	cam_name = StringProperty(
		name="Camera Name",
		description=":",
		default="",
		maxlen=1024,
		)

	angle_thresh = IntProperty(
		name = "Angle Threshold",
		description = "A int property",
		default = 30,
		step = 1,
		)

	# wireframe_toggle = BoolProperty(
	# 	name = "Wireframe Toggle",
	# 	description = "tells if wireframe setting on or off",
	# 	update = WireFrameUpdateFunction
	# 	#set = WireFrameUpdateFunction,
	# 	)

# for exporting values
default_material_names = [
	"BlackMaterial",
	"GreenMaterial",
	"Clear2DMaterial",
	"Wireframe2DMaterial",
	"ClothMaterial",
	"CubeMaterial"
]

BRENDER_wf_names = []
# Uncomment following to keep track of brend objects 
# 		(uncomment labeled lines below as well)
# BRENDER_object_names = []

####################################################
# Run on Import
####################################################


###############################################################################
#		Operators
###############################################################################


# The following Function is a modification of 'cmomoney's blender_import_obj_anim method
class LoadObjAsAnimationAdvanced(bpy.types.Operator):
	bl_idname = 'load.obj_as_anim_advanced'
	bl_label = 'Advanced Import'
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Import Obj sequence as animation(s)"
	cFrame = 0
	filepath = StringProperty(name="File path", description="File filepath of Obj", maxlen=4096, default="")
	filter_folder = BoolProperty(name="Filter folders", description="", default=True, options={'HIDDEN'})
	filter_glob = StringProperty(default="*.obj", options={'HIDDEN'})
	files = CollectionProperty(name='File path', type=bpy.types.OperatorFileListElement)
	filename_ext = '.obj'
	objects = []
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		self.objects=[]
		scene = context.scene
		myaddon = scene.my_addon
		#get file names, sort, and set target mesh
		spath = os.path.split(self.filepath)
		files = [file.name for file in self.files]
		files.sort()
		
		#add all objs to scene
		# this makes the frame skip option available
		count=0
		lastframe = 0
		modval = myaddon.frameskip + 1
		for f in files:
			if count % modval == 0:
				fp = spath[0] + "/" + f
				self.load_obj(fp,f)
				lastframe+=1

			count+=1
		bpy.context.scene.frame_end = lastframe - 1
		# bpy.ops.time.view_all() # should view all, but needs to apply to timeline
		
		bpy.context.scene.frame_set(0)
		for i, ob in enumerate(self.objects):
			if i == 0:
				continue
			ob.hide = ob.hide_render = True
			ob.keyframe_insert(data_path='hide')
			ob.keyframe_insert(data_path='hide_render')

		for f, ob in enumerate(self.objects):
			if f == 0:
				continue
			# increment current frame to insert keyframe
			bpy.context.scene.frame_set(f)

			# Insert only as many keyframes as really needed
			ob_prev = self.objects[f-1]
			ob_prev.hide = ob_prev.hide_render = True
			ob_prev.keyframe_insert(data_path='hide')
			ob_prev.keyframe_insert(data_path='hide_render')
			
			ob = self.objects[f]
			ob.hide = ob.hide_render = False
			ob.keyframe_insert(data_path='hide')
			ob.keyframe_insert(data_path='hide_render')

		
		# Uncomment Following to keep track of Brender Objects
		# for name in files:
		# 	BRENDER_object_names.append(name.split('.', 1)[0]) # takes off .obj
		
				
		return{'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def load_obj(self, fp,fname):
		bpy.ops.object.select_all(action='DESELECT')
		bpy.ops.import_scene.obj(filepath=fp, filter_glob="*.obj;*.mtl",  use_edges=True, use_smooth_groups=True, use_split_objects=True, use_split_groups=True, use_groups_as_vgroups=False, use_image_search=True, split_mode='ON', global_clamp_size=0, axis_forward='Y', axis_up='Z')
		self.objects.append(bpy.context.selected_objects[0])
		return 



def GetCommonName(brenderObjname):
	returnBrenderName = brenderObjname
	if "_" in brenderObjname: # has naming scheme 00001_objname
		returnBrenderName = brenderObjname.split("_", 1)[1] # same last letters as brenderobj

	else: # just return selected object
		returnBrenderName = brenderObjname

	return returnBrenderName


def CreateImportedMatDefaults(mat):
	dummyvar = 0
	if mat not in bpy.data.materials:
		if mat in "ClothMaterial" or mat in "CubeMaterial" or mat in "CheckerGreyscale":
			CreateDefaultMaterials.execute(dummyvar, dummyvar)
		elif mat in "Wireframe2DMaterial":
			CreateWireframeMaterial.execute(dummyvar,dummyvar)
		elif mat in "BlackMaterial":
			createBlackBackground.execute(bpy.context, bpy.context)
		elif mat in "GreyMaterial":
			createGreyBackground.execute(bpy.context, bpy.context)
		elif mat in "GreenMaterial":
			createGreenBackground.execute(bpy.context, bpy.context)
		else:
			# Clear2DMaterial
			CreateClearClothMaterial.execute(dummyvar,dummyvar)


def applyMatDefaults(objname,mat):
	dummyvar = 0
	if mat not in bpy.data.materials:
		if mat in "ClothMaterial" or mat in "CubeMaterial":
			CreateDefaultMaterials.execute(dummyvar, dummyvar)
		elif mat in "Wireframe2DMaterial":
			CreateWireframeMaterial.execute(dummyvar,dummyvar)
		else:
			# Clear2DMaterial
			CreateClearClothMaterial.execute(dummyvar,dummyvar)

	ApplyMaterialToAll.general(objname,mat)
		


def Material_array():
	unique_objs = []
	# get name of 1 copy of each unique object
	for obj in bpy.data.objects:
		if obj.type in ['CURVE'] or obj.type in ['MESH']:
			if "_" in obj.name:
				testname = "000000_" + obj.name.split("_",1)[1]
			else:
				testname = obj.name

			if testname not in unique_objs:
				unique_objs.append(testname)

	# get material name for each unique object
	# now form of: "objectName:Material"
	unique_objs[:] = [name + ':' + bpy.data.objects[name].active_material.name for name in unique_objs]

	return unique_objs


def checkDefaultsMatArray(arr):
	mats = []
	for strval in arr:
		mat = strval.split(":",1)[1]
		if mat in default_material_names:
			mats.append(strval)

	return mats

def write_settings_data_json(context, filepath, myaddon):
	print("running write_settings_data...")
	objDict = {'Objects':[], 'Materials':[]}
	f = open(filepath, 'w', encoding='utf-8')
	unique_names = []
	for obj in bpy.data.objects:
		common_name = GetCommonName(obj.name)
		# Take this If statement out to export all object info (ex: 000000_Cloth2D-999999_Cloth2D)
		if common_name not in unique_names:
			unique_names.append(common_name)
			# if obj.name in BRENDER_object_names and not obj.name.startswith("000000"):
			# 	# skip it
			# 	continue
			# else:
			new_obj = {}
			new_obj['Name'] = obj.name
			new_obj['Type'] = obj.type
			if obj.type in 'MESH':
				new_obj['Parent'] = None
			elif obj.type in 'CURVE' and obj.name.endswith(".wireframe"):
				new_obj['Parent'] = obj.name.split(".", 1)[0] # take off ".wireframe"
				new_obj['Wireframe Depth'] = myaddon.wf_bevel_depth
				new_obj['Wireframe Resolution'] = myaddon.wf_bevel_resolution
				new_obj['Wireframe Offset'] = myaddon.wf_offset
				new_obj['Wireframe Extrude'] = myaddon.wf_extrude
			elif obj.type in 'LAMP' or obj.type in 'CAMERA':
				new_obj['Sub Type'] = obj.data.type
				new_obj['Loc X'] = obj.location[0]
				new_obj['Loc Y'] = obj.location[1]
				new_obj['Loc Z'] = obj.location[2]
				new_obj['Euler 0'] = obj.rotation_euler[0]
				new_obj['Euler 1'] = obj.rotation_euler[1]
				new_obj['Euler 2'] = obj.rotation_euler[2]
				new_obj['Euler Order'] = obj.rotation_euler.order

			if obj.type in 'MESH' or obj.type in 'CURVE':
				new_obj['Material'] = obj.active_material.name
			objDict['Objects'].append(new_obj)

	for mats in bpy.data.materials:
		new_mat = {'Name' : mats.name}
		objDict['Materials'].append(new_mat)
		

	new_string = json.dumps(objDict, indent=2)
	f.write(new_string)
	f.close()

	return {'FINISHED'}



def read_settings_data_json(context, filepath, myaddon):
	print("running read_settings_data...")
	f = open(filepath, 'r', encoding='utf-8')
	data = json.load(f)
	f.close()

	for mats in data['Materials']:
		CreateImportedMatDefaults(mats['Name'])

	for obj in data['Objects']:
		if obj['Type'] in 'MESH':
			if obj['Name'] in bpy.data.objects: # will work with brender objects ('000000_name')
				ApplyMaterialToAll.general(obj['Name'],obj['Material'])
			
		if obj['Type'] in 'CURVE' and obj['Name'].endswith('.wireframe'):
			# does the wireframe exist yet?
			# only do wireframe creation once
			if GetCommonName(obj['Parent'].split("_",1)[1]) not in BRENDER_wf_names:
				# wireframes havent been documented, create
				# assuming only one wireframed object
				myaddon.wireframe_obj_string = GetCommonName(obj['Parent'].split("_",1)[1])
				myaddon.wf_bevel_depth = obj['Wireframe Depth']
				myaddon.wf_bevel_resolution = obj['Wireframe Resolution']
				myaddon.wf_offset = obj['Wireframe Offset']
				myaddon.wf_extrude = obj['Wireframe Extrude']
				WireframeOverlay.apply_wireframe(myaddon.wireframe_obj_string)
				BRENDER_wf_names.append(myaddon.wireframe_obj_string)
				# apply material
				ApplyMaterialToAll.general(obj['Name'],obj['Material'])
			else:
				# already created
				continue
			# bpy.data.objects[obj['Name']].active_material = obj['Material']
		if obj['Type'] in 'LAMP':
			if obj['Name'] == 'brenderDefaults.Lamp':
				lightSetup2D.execute(bpy.context, bpy.context)
			else:
				# create lamp
				# NOTE: Lamp Creation doesnt include intensity, radius, etc at the moment
				bpy.ops.object.lamp_add()
				new_obj = bpy.context.active_object
				new_obj.data.type=obj['Sub Type']
				new_obj.name = obj['Name']
				new_obj.location = mathutils.Vector((obj['Loc X'], obj['Loc Y'], obj['Loc Z']))
				new_obj.rotation_euler = mathutils.Euler((obj['Euler 0'], obj['Euler 1'], obj['Euler 2']), obj['Euler Order'])
				new_obj.select = False

		if obj['Type'] in 'CAMERA':
			if obj['Name'] == 'brenderDefaults.Camera':
				cameraSetup2D.execute(bpy.context, bpy.context)
			else:
				# create lamp
				# NOTE: Lamp Creation doesnt include intensity, radius, etc at the moment
				bpy.ops.object.camera_add()
				new_obj = bpy.context.active_object
				new_obj.data.type=obj['Sub Type']
				new_obj.name = obj['Name']
				new_obj.location = mathutils.Vector((obj['Loc X'], obj['Loc Y'], obj['Loc Z']))
				new_obj.rotation_euler = mathutils.Euler((obj['Euler 0'], obj['Euler 1'], obj['Euler 2']), obj['Euler Order'])
				new_obj.select = False
				

	return {'FINISHED'}




# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
class ExportBrenderSettings(Operator, ExportHelper):
	"""This appears in the tooltip of the operator and in the generated docs"""
	bl_idname = "export_brend.settings_data"  # important since its how bpy.ops.import_test.settings_data is constructed
	bl_label = "Export Brender Settings"

	# ExportHelper mixin class uses this
	filename_ext = ".brend"

	filter_glob = StringProperty(
			default="*.brend",
			options={'HIDDEN'},
			maxlen=255,  # Max internal buffer length, longer would be clamped.
			)


	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		return write_settings_data_json(context, self.filepath, myaddon)


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
class ImportBrenderSettings(Operator, ImportHelper):
	"""This appears in the tooltip of the operator and in the generated docs"""
	bl_idname = "import_brend.settings_data"  # important since its how bpy.ops.import_brend.settings_data is constructed
	bl_label = "Import Brender Settings"

	# ImportHelper mixin class uses this
	filename_ext = ".brend"

	filter_glob = StringProperty(
			default="*.brend",
			options={'HIDDEN'},
			maxlen=255,  # Max internal buffer length, longer would be clamped.
			)


	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		return read_settings_data_json(context, self.filepath, myaddon)



class BatchDelete(bpy.types.Operator):
	"""Animation Object Resizing"""
	bl_idname = "object.delete_all"
	bl_label = "Delete all objects of same name"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		brenderObjname = context.active_object.name

		brenderObjname = GetCommonName(brenderObjname)

		for obj in bpy.data.objects:
			if obj.name.endswith(brenderObjname): # same last letters as brenderobj
				obj.hide = obj.hide_render = False
				obj.select = True
				bpy.ops.object.delete(use_global=False)
				obj.select = False
		for mesh in bpy.data.meshes:
			if mesh.name.endswith(brenderObjname): # same last letters as brenderobj
				bpy.data.meshes.remove(mesh)

		return {'FINISHED'}


class CreateDefaultMaterials(bpy.types.Operator):
	"""Animation Object Resizing"""
	bl_idname = "object.create_default_mats"
	bl_label = "Create Default Materials"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		if bpy.data.materials.get("ClothMaterial") is None:
			# create cloth material
			mat_name = "ClothMaterial"
			mat = bpy.data.materials.new(mat_name)
			mat.use_nodes = True 
			nodes = mat.node_tree.nodes
			# diffuse node is made by default
			diffnode = nodes["Diffuse BSDF"]
			checkernode = nodes.new('ShaderNodeTexChecker')
			uvmapnode = nodes.new('ShaderNodeUVMap')
			# organize nodes
			diffnode.location = (100,300)
			checkernode.location = (-100,300)
			uvmapnode.location = (-300,300)
			# apply checker primary and secondary colors
			checkernode.inputs[1].default_value = (0.456, 0.386, 0.150, 1)
			checkernode.inputs[2].default_value = (0.080, 0, 0, 1)
			# link nodes
			links = mat.node_tree.links
			links.new(checkernode.outputs[0], diffnode.inputs[0]) 
			links.new(uvmapnode.outputs[0], checkernode.inputs[0])

		if bpy.data.materials.get("CheckerGreyscale") is None:
			# create cloth material
			mat_name = "CheckerGreyscale"
			mat = bpy.data.materials.new(mat_name)
			mat.use_nodes = True 
			nodes = mat.node_tree.nodes
			# diffuse node is made by default
			diffnode = nodes["Diffuse BSDF"]
			checkernode = nodes.new('ShaderNodeTexChecker')
			uvmapnode = nodes.new('ShaderNodeUVMap')
			# organize nodes
			diffnode.location = (100,300)
			checkernode.location = (-100,300)
			uvmapnode.location = (-300,300)
			# apply checker primary and secondary colors
			# Black
			checkernode.inputs[1].default_value = (0.0, 0.0, 0.0, 1)
			# Dark Grey
			checkernode.inputs[2].default_value = (0.141, 0.133, 0.13, 1)

			# link nodes
			links = mat.node_tree.links
			links.new(checkernode.outputs[0], diffnode.inputs[0]) 
			links.new(uvmapnode.outputs[0], checkernode.inputs[0])

		if bpy.data.materials.get("CubeMaterial") is None:
			# create cube material
			mat_name2 = "CubeMaterial"
			mat2 = bpy.data.materials.new(mat_name2)
			mat2.use_nodes = True 
			nodes2 = mat2.node_tree.nodes
			diffnode2 = nodes2["Diffuse BSDF"]
			# apply checker primary and secondary colors
			diffnode2.inputs[0].default_value = (0.198, 0.371, 0.694, 1)

		return {'FINISHED'}

class CreateWireframeMaterial(bpy.types.Operator):
	"""Animation Object Resizing"""
	bl_idname = "object.create_default_wf_mat"
	bl_label = "Create Wireframe Material (2D Default)"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		if bpy.data.materials.get("Wireframe2DMaterial") is None:
			# create wireframe material
			mat_name = "Wireframe2DMaterial"
			mat = bpy.data.materials.new(mat_name)
			mat.use_nodes = True 
			nodes = mat.node_tree.nodes
			emissnode = nodes.new(type='ShaderNodeEmission')
			diffnode = nodes["Diffuse BSDF"]
			outputnode = nodes["Material Output"]
			# delete the diffuse node
			nodes.remove(diffnode)
			# apply emission defaults
			# emission color
			emissnode.inputs[0].default_value = (0.8, 0.8, 0.8, 1)
			#emission strength
			emissnode.inputs[1].default_value = (5.0)
			# link node to output
			links = mat.node_tree.links
			links.new(emissnode.outputs[0], outputnode.inputs[0])

		return {'FINISHED'}


class CreateClearClothMaterial(bpy.types.Operator):
	"""Animation Object Resizing"""
	bl_idname = "object.create_clear_mat"
	bl_label = "Create Clear Material (2D Cloth Default)"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		if bpy.data.materials.get("Clear2DMaterial") is None:
			# create wireframe material
			mat_name = "Clear2DMaterial"
			mat = bpy.data.materials.new(mat_name)
			mat.use_nodes = True 
			nodes = mat.node_tree.nodes
			translunode = nodes.new(type='ShaderNodeBsdfTransparent')
			diffnode = nodes["Diffuse BSDF"]
			outputnode = nodes["Material Output"]
			# delete the diffuse node
			nodes.remove(diffnode)
			# link node to output
			links = mat.node_tree.links
			links.new(translunode.outputs[0], outputnode.inputs[0])

		return {'FINISHED'}

# ShaderNodeBsdfTransparent

class ApplyMaterialToAll(bpy.types.Operator):
	"""Apply Animation Object Material"""
	bl_idname = "object.apply_material_to_all"
	bl_label = "Apply Selected Material"
	bl_options = {'REGISTER', 'UNDO'}

	# implementation now requires selection rather than active
	def execute(self, context):
		mat = bpy.context.object.active_material
		scene = context.scene
		myaddon = scene.my_addon

		bndrname = [obj.name for obj in context.selected_objects if not (obj.name.startswith('Camera') or obj.name.startswith('Lamp'))]
		for i,bndr in enumerate(bndrname):
			frame_location = bndr.find('.')
			if frame_location is not -1:
				bndrname[i] = bndr[:(-1 * frame_location)]

		for name in bndrname:
			self.report({'INFO'}, name)

		for obj in bpy.data.objects:
			for name in bndrname:
				if obj.name.startswith(name):
					# self.report({'INFO'}, obj.name)
					obj.select = True
					# append Material
					if obj.data.materials:
						obj.data.materials[0] = mat
					else:
						obj.data.materials.append(mat)
					obj.select = False

		# for obj in bpy.data.objects:
		# 	if obj.name.endswith(brenderObjname): # same last letters as brenderobj
		# 		obj.select = True
		# 		# append Material
		# 		if obj.data.materials:
		# 			obj.data.materials[0] = mat
		# 		else:
		# 			obj.data.materials.append(mat)
		# 		obj.select = False			


		return {'FINISHED'}

	def general(objname,matname):
		mat = bpy.data.materials[matname]
		scene = bpy.context.scene
		myaddon = scene.my_addon
		brenderObjname = GetCommonName(objname)

		for obj in bpy.data.objects:
			if obj.name.endswith(brenderObjname) or obj.name.startswith(objname): # same last letters as brenderobj
				obj.select = True
				# append Material
				if obj.data.materials:
					obj.data.materials[0] = mat
				else:
					obj.data.materials.append(mat)
				obj.select = False			

		return {'FINISHED'}


class AnimationObjectResize(bpy.types.Operator):
	"""Animation Object Resizing"""
	bl_idname = "object.resize_animation_objects"
	bl_label = "Update"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		# bndrname = context.active_object.name
		# brenderObjname = GetCommonName(bndrname)
		curr = bpy.data.scenes["Scene"].frame_current
		# scale_vals = []
		# objects = []
		# for obj in bpy.context.selected_objects:
			# scene.frame_set(curr)
			# objects.append(bpy.data.objects[obj.name])
			# scale_vals.append(obj.scale[0]) # x
			# scale_vals.append(obj.scale[1]) # y
			# scale_vals.append(obj.scale[2]) # z
		scale_vals = [bpy.context.selected_objects[0].scale[0], bpy.context.selected_objects[0].scale[1], bpy.context.selected_objects[0].scale[2]]

			# based on https://blenderartists.org/t/scale-selected-objects/633637/4

		for frame in range(scene.frame_start, scene.frame_end+1):
			# if obj.name.endswith(brenderObjname) or obj.name.startswith(bndrname): # same last letters as brenderobj
			scene.frame_set(frame)
		# bpy.ops.object.mode_set(mode='EDIT')
			# for index, obj in enumerate(objects):
			# 	obj.scale=(scale_vals[3*index], scale_vals[3*index+1], scale_vals[3*index+2])
			# 	# obj.rotation_mode = 'QUATERNION'
			# bpy.ops.anim.keyframe_insert_menu(type='Scaling')
			# bpy.ops.anim.keyframe_insert_menu(type='Rotation')
			# bpy.ops.anim.keyframe_insert_menu(type='Location')
			bpy.ops.transform.resize(
				value=(scale_vals[0], scale_vals[1], scale_vals[2]), # this is the transformation X,Y,Z
				constraint_axis=(False, False, False), 
				constraint_orientation='GLOBAL', 
				mirror=False, proportional='DISABLED', 
				proportional_edit_falloff='SMOOTH', 
				proportional_size=1)
			bpy.ops.anim.keyframe_insert_menu(type='Scaling')
			bpy.ops.anim.keyframe_insert_menu(type='Rotation')
			bpy.ops.anim.keyframe_insert_menu(type='Location')

		# for fc in bpy.context.selected_objects[0].animation_data.action.fcurves:
		# 	if fc.data_path.endswith(('scale')):
		# 		for key in fc.keyframe_points:
		# 			scene.frame_set(int(key.co[0]))
		# 			bpy.ops.transform.resize(
		# 				value=(scale_vals[0], scale_vals[1], scale_vals[2]), # this is the transformation X,Y,Z
		# 				constraint_axis=(False, False, False), 
		# 				constraint_orientation='GLOBAL', 
		# 				mirror=False, proportional='DISABLED', 
		# 				proportional_edit_falloff='SMOOTH', 
		# 				proportional_size=1)
		# 			bpy.ops.anim.keyframe_insert_menu(type='Scaling')
		# 			bpy.ops.anim.keyframe_insert_menu(type='Rotation')
		# 			bpy.ops.anim.keyframe_insert_menu(type='Location')
		# 			if key.co[0] == 1.0:
		# 				self.report({'INFO'}, 'frame: ' + str(key.co[0]) + ' value: ' + str(key.co[1]))
		# bpy.ops.object.mode_set(mode='OBJECT')

			# theobj.keyframe_insert(data_path='scale')
			# theobj.keyframe_insert(data_path='rotation_quaternion')
			# theobj.keyframe_insert(data_path='location')

			# theobj.select = False

		scene.frame_set(curr)
		return {'FINISHED'}


class AnimationObjectRotate(bpy.types.Operator):
	"""Animation Object Resizing"""
	bl_idname = "object.rotate_animation_objects"
	bl_label = "Update"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		bndrname = context.active_object.name
		brenderObjname = GetCommonName(bndrname)

		for obj in bpy.data.objects:
			if obj.name.endswith(brenderObjname) or obj.name.endswith(bndrname): # same last letters as brenderobj
				theobj = bpy.data.objects[obj.name]
				theobj.select = True
				theobj.rotation_euler = (myaddon.x_rot_float,myaddon.y_rot_float,myaddon.z_rot_float)
				theobj.select = False


		return {'FINISHED'}


class AnimationObjectTranslate(bpy.types.Operator):
	"""Animation Object Translating"""
	bl_idname = "object.translate_animation_objects"
	bl_label = "Update"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		bndrname = context.active_object.name
		brenderObjname = GetCommonName(bndrname)

		xTrans = myaddon.x_trans_float
		yTrans = myaddon.y_trans_float
		zTrans = myaddon.z_trans_float
		
		for obj in bpy.data.objects:
			if obj.name.endswith(brenderObjname) or obj.name.endswith(bndrname): # same last letters as brenderobj
				theobj = bpy.data.objects[obj.name]
				theobj.select = True
				vec = mathutils.Vector((xTrans,yTrans,zTrans))
				theobj.location = vec #theobj.location + vec
				theobj.select = False


		return {'FINISHED'}


class WireframeOverlay(bpy.types.Operator):
	"""Wireframe Overlay"""
	bl_idname = "object.wireframe_overlay"
	bl_label = "Create/Update Wireframe Overlay"
	bl_options = {'REGISTER', 'UNDO'}

	def DoesObjExist(objname):
		# self.objname = objname
		for obj in bpy.data.objects:
			if obj.name.endswith(objname):
				return True

		return False

	def execute(self, context):
		scn = context.scene 
		myaddon = scn.my_addon 
		objectname = myaddon.wireframe_obj_string
		# Check if name is typed in, if not, use selected object 
		if myaddon.wireframe_obj_string is not "":
			objectname = myaddon.wireframe_obj_string
		else:
			brenderObjname = context.active_object.name
			objectname = GetCommonName(brenderObjname)
			# set as wf_obj_string
			myaddon.wireframe_obj_string = objectname
		

		WireframeOverlay.apply_wireframe(objectname)


		return {'FINISHED'}
		# distinguish which object needs wireframe


	def apply_wireframe(objname): 
		scn = bpy.context.scene
		myaddon = scn.my_addon
		dupobjects = []

		objectname = GetCommonName(objname)
		# is selected object the wireframe overlay or base object
		if objectname.endswith(".wireframe"):
			copynames = objectname
		else:
			copynames = objectname + ".wireframe"

		if WireframeOverlay.DoesObjExist(copynames):
			# object copies exist. dont copy
			# update parameters
			scn.frame_set(0)

			for obj in bpy.data.objects:
				if obj.name.endswith(copynames):
					obj.select=True
					obj.data.bevel_depth=myaddon.wf_bevel_depth  #0.002
					obj.data.fill_mode='FULL'
					obj.data.bevel_resolution = myaddon.wf_bevel_resolution
					obj.data.offset = myaddon.wf_offset
					obj.data.extrude = myaddon.wf_extrude
					#deselect object
					obj.select=False

			return {'FINISHED'}

		else:
			# create copies
			# duplicate object loop
			for obj in bpy.data.objects:
				if obj.name.endswith(objectname):
					theobj = bpy.data.objects[obj.name]
					# duplicates and selects the new object
					new_obj = theobj.copy()
					origName = new_obj.name # to correct default mesh name
					new_obj.name = theobj.name + '.wireframe' # new naming convention
					new_obj.data = theobj.data.copy()
					new_obj.animation_data_clear()
					scn.objects.link(new_obj)
					dupobjects.append(new_obj)
					# make sure mesh data has same name
					mesh = bpy.data.meshes[origName]
					mesh.name = new_obj.name

			
			scn.frame_set(0)
			# hide for keyframes
			for i, obj in enumerate(dupobjects):
				if i == 0:
					continue
				obj.hide = obj.hide_render = True
				obj.keyframe_insert(data_path='hide')
				obj.keyframe_insert(data_path='hide_render')

			for f, obj in enumerate(dupobjects):
				if f == 0:
					continue
				# increment current frame to insert keyframe
				scn.frame_set(f)
		
				obj_prev = dupobjects[f-1]
				obj_prev.hide = obj_prev.hide_render = True
				obj_prev.keyframe_insert(data_path='hide')
				obj_prev.keyframe_insert(data_path='hide_render')
				
				obj = dupobjects[f]
				obj.hide = obj.hide_render = False
				obj.keyframe_insert(data_path='hide')
				obj.keyframe_insert(data_path='hide_render')

			# end of duplicating opjects
			scn.frame_set(0)
			# make mesh
			
			for obj in bpy.data.objects:
				if obj.name.endswith(copynames):
					#unhide object
					obj.hide = obj.hide_render = False
					scn.objects.active = obj
					bpy.ops.object.mode_set(mode='EDIT')
			
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')
			
					#execute any editmode tool
					bpy.ops.mesh.delete(type='ONLY_FACE')
			
					bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
					obj.select=True
					bpy.ops.object.convert(target='CURVE')
					obj.data.bevel_depth=myaddon.wf_bevel_depth  #0.002
					obj.data.fill_mode='FULL'
					obj.data.bevel_resolution = myaddon.wf_bevel_resolution
					obj.data.offset = myaddon.wf_offset
					obj.data.extrude = myaddon.wf_extrude
					#rehide object  
					obj.hide = obj.hide_render = True #hide mesh
					#deselect object
					obj.select=False

			# Uncomment Following to keep track of Brender objects
			#######################################################################
			# for obj in bpy.data.objects:
			# 	if obj.name.endswith(copynames):
			# 		BRENDER_object_names.append(obj.name)
			BRENDER_wf_names.append(copynames)


		return {'FINISHED'}


class wireframePreview(bpy.types.Operator):
	"""Wireframe Overlay Preview"""
	bl_idname = "object.wireframe_overlay_preview"
	bl_label = "Preview Wireframe Overlay"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		obj = context.object

		if obj.type in ['CURVE']:
			obj.data.bevel_depth=myaddon.wf_bevel_depth  #0.002
			obj.data.fill_mode='FULL'
			obj.data.bevel_resolution = myaddon.wf_bevel_resolution
			obj.data.offset = myaddon.wf_offset
			obj.data.extrude = myaddon.wf_extrude
		else:
			self.report({'ERROR'},'You must have a wireframe/curve object selected to preview.')

		return {'FINISHED'}


class cameraSetup2D(bpy.types.Operator):
	"""Wireframe Overlay Preview"""
	bl_idname = "object.cam_setup_2d"
	bl_label = "Apply Camera Defaults (2D)"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		
		cam = bpy.data.objects['Camera']

		# default naming for export
		cam.name = "brenderDefaults." + cam.name

		if cam.type in ['CAMERA']:
			cam.location = mathutils.Vector((0.5, 0.5, 2.15))
			cam.rotation_euler = mathutils.Euler((0.0, -0.0, 0.0), 'XYZ')
			cam.data.type = 'ORTHO'
			cam.data.ortho_scale = 1.9

		return {'FINISHED'}

class lightSetup2D(bpy.types.Operator):
	"""Wireframe Overlay Preview"""
	bl_idname = "object.light_setup_2d"
	bl_label = "Apply Lighting Defaults (2D)"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		
		light = bpy.data.objects['Lamp']##context.object
		# default naming for export
		light.name = "brenderDefaults.Lamp"

		if light.type in ['LAMP']:
			light.data.type = 'SUN'
			light.rotation_euler = mathutils.Euler((0.0,0.0,1.578),'XYZ')
			light.data.use_nodes = True
			ltnodes = light.data.node_tree.nodes
			outputnode = ltnodes['Lamp Output']
			emissnode = ltnodes.new(type='ShaderNodeEmission')
			emissnode.inputs[1].default_value = (4.000)

			links = light.data.node_tree.links
			links.new(emissnode.outputs[0], outputnode.inputs[0])


		return {'FINISHED'}


class createBlackBackground(bpy.types.Operator):
	"""Wireframe Overlay Preview"""
	bl_idname = "object.create_black_bg"
	bl_label = "Create Black BG (2D Default)"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		
		bpy.ops.mesh.primitive_plane_add()
		pln = bpy.context.active_object
		# default naming for export
		pln.name = "brenderDefaults.background"
		pln.location = mathutils.Vector((0.0, 0.0, -0.025))
		pln.scale =  mathutils.Vector((5.0, 5.0, 5.0))

		if bpy.data.materials.get("BlackMaterial") is None:
			# create cube material
			mat_name = "BlackMaterial"
			mat = bpy.data.materials.new(mat_name)
			mat.use_nodes = True 
			nodes = mat.node_tree.nodes
			diffnode = nodes["Diffuse BSDF"]
			# apply checker primary and secondary colors
			diffnode.inputs[0].default_value = (0.0, 0.0, 0.0, 1)
			diffnode.inputs[1].default_value = (0.0)

		pln = bpy.data.objects['brenderDefaults.background']
		mat = bpy.data.materials.get("BlackMaterial")
		pln.select = True

		if pln.data.materials:
			pln.data.materials[0] = mat
		else:
			pln.data.materials.append(mat)
		pln.select = False	


		return {'FINISHED'}

class createGreenBackground(bpy.types.Operator):
	"""Wireframe Overlay Preview"""
	bl_idname = "object.create_green_bg"
	bl_label = "Create Green BG (2D Default)"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		
		bpy.ops.mesh.primitive_plane_add()
		pln = bpy.context.active_object
		# default naming for export
		pln.name = "brenderDefaultsGreen.background"
		pln.location = mathutils.Vector((0.0, 0.0, -0.025))
		pln.scale =  mathutils.Vector((5.0, 5.0, 5.0))

		if bpy.data.materials.get("GreenkMaterial") is None:
			# create cube material
			mat_name = "GreenMaterial"
			mat = bpy.data.materials.new(mat_name)
			mat.use_nodes = True 
			nodes = mat.node_tree.nodes
			diffnode = nodes["Diffuse BSDF"]
			# apply checker primary and secondary colors
			diffnode.inputs[0].default_value = (0.0, 1.0, 0.0, 1)
			diffnode.inputs[1].default_value = (0.0)

		pln = bpy.data.objects['brenderDefaultsGreen.background']
		mat = bpy.data.materials.get("GreenMaterial")
		pln.select = True

		if pln.data.materials:
			pln.data.materials[0] = mat
		else:
			pln.data.materials.append(mat)
		pln.select = False	


		return {'FINISHED'}


class createGreyBackground(bpy.types.Operator):
	"""Wireframe Overlay Preview"""
	bl_idname = "object.create_grey_bg"
	bl_label = "Create Grey BG (3D Default)"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		scene = context.scene
		myaddon = scene.my_addon
		
		bpy.ops.mesh.primitive_plane_add()
		pln = bpy.context.active_object
		# default naming for export
		pln.name = "brenderDefaults3d.background"
		pln.location = mathutils.Vector((0.0, 0.0, -0.025))
		pln.scale =  mathutils.Vector((10.0, 10.0, 1.0))

		if bpy.data.materials.get("GreyMaterial") is None:
			# create cube material
			mat_name = "GreyMaterial"
			mat = bpy.data.materials.new(mat_name)
			mat.use_nodes = True 
			nodes = mat.node_tree.nodes
			diffnode = nodes["Diffuse BSDF"]
			# apply checker primary and secondary colors
			diffnode.inputs[0].default_value = (0.161, 0.151, 0.156, 1)
			diffnode.inputs[1].default_value = (0.0)

		pln = bpy.data.objects['brenderDefaults3d.background']
		mat = bpy.data.materials.get("GreyMaterial")
		pln.select = True

		if pln.data.materials:
			pln.data.materials[0] = mat
		else:
			pln.data.materials.append(mat)
		pln.select = False	


		return {'FINISHED'}


class CLothEdgesplit(bpy.types.Operator):
	"""Edgesplit for cloth normals"""
	bl_idname = "object.edgesplit"
	bl_label = "Apply Edgesplit value to cloth objects/materials"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		scene = bpy.context.scene
		myaddon = scene.my_addon

		# Find all objects in the scene by name (e.g., foo* would match foo0001, etc.).
		cloth_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "*_Cloth3D")]

		# Material to be applied. This material must already exist in the blender scene.
		mat = bpy.data.materials.get("ClothMaterial")

		# Any edge angle below this will be rendered with smooth normals
		angle_thresh = myaddon.angle_thresh*3.14159/180.0

		# Go through the objects
		for ob in cloth_objs:
			for poly in ob.data.polygons:
				poly.use_smooth = True
			# see if there is already a modifier named "EdgeSplit" and use it
			mod = ob.modifiers.get("EdgeSplit")
			if mod is None:
				# otherwise add a modifier to selected object
				mod = ob.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
			mod.split_angle = angle_thresh
			if ob.data.materials:
				ob.data.materials[0] = mat
			else:
				ob.data.materials.append(mat)

		return {'FINISHED'}


###############################################################################
#		Brender in Object mode UI Panels
###############################################################################

# Class for the panel, derived by Panel
# creating BrenderPanel inherited from Panel class
class BrenderImportPanel(View3DPanel, Panel):
	bl_idname = "SCENE_PT_Brender_import_panel"
	bl_label = "Import Obj Files as Animation"
	bl_category = "Brender"
	bl_context = "objectmode"
	# Removed poll classmethod so that this 
	# panel is always visible

	# Add UI elements here
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		myaddon = scene.my_addon

		layout.label("Import")
		layout.operator("load.obj_as_anim")
		layout.label("Advanced Import")
		row = layout.row()
		box = row.box()
		split = box.split()
		split.label("Skip every ")
		split.prop(myaddon, "frameskip")
		split.label("frames")
		split.operator("load.obj_as_anim_advanced", text="Import")
    	
###########################  WIPWIP  ###########################

# Toggle for if they want wireframe to be on or off
# class BrenderWireframeTogglePanel(View3DPanel, Panel):
# 	bl_idname = "SCENE_PT_Brender_wireframe_toggle"
# 	bl_label = "ToggleWireframe"
# 	bl_category = "Brender"
# 	bl_context = "objectmode"

# 	def draw(self, context):
# 		layout = self.layout
# 		scene = context.scene
# 		myaddon = scene.my_addon

# 		# layout.label("Base Obj Frame Import")
# 		# layout.operator("load.obj_as_base") # make import for this
# 		layout.label("Rigid Transformation Import")
# 		row = layout.row()
# 		box = row.box()
# 		split = box.split()
# 		split.label("Toggle Wireframe")
# 		split.prop(myaddon, "wireframe_toggle")
# 		#split.operator("load.wireframe", text="Wiretextoperator")


########################### wipwipwipwipIWPIPWIP ###########################

# # Rigid implementation starts
class BrenderRigidImportPanel(View3DPanel, Panel):
	bl_idname = "SCENE_PT_Brender_rigid_import_panel"
	bl_label = "Import Json File as Animation"
	bl_category = "Brender"
	bl_context = "objectmode"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		myaddon = scene.my_addon

		# layout.label("Base Obj Frame Import")
		# layout.operator("load.obj_as_base") # make import for this
		layout.label("Toggle Wireframe Rendering")
		row = layout.row()
		box = row.box()
		split = box.split()
		# split.label("Skip every ")
		# split.prop(myaddon, "frameskip")
		# split.label("frames")
		split.operator("load.rigid_as_anim", text="Import Json")
		# split2 = box.split()
		# split2.prop(myaddon, "wireframe_toggle")




class BrenderEditPanel(View3DPanel, Panel):
	bl_idname = "SCENE_PT_Brender_edit_panel"
	bl_label = "Edit"
	bl_category = "Brender"
	bl_context = "objectmode"
	# Removed poll classmethod so that this 
	# panel is always visible

	# Add UI elements here
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		myaddon = scene.my_addon
		
		layout.operator("object.delete_all")
		layout.label("Advanced")
		layout.operator(ExportBrenderSettings.bl_idname, text="Export Brender Settings")
		layout.operator(ImportBrenderSettings.bl_idname, text="Import Brender Settings")



class BrenderTransformPanel(View3DPanel, Panel):
	bl_idname = "OBJECT_PT_Brender_transform_panel"
	bl_label = "Transform"
	bl_category = 'Brender'
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}

	# not sure about this one
	@classmethod
	def poll(self,context):
		return context.object is not None

	# Add UI elements here
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		myaddon = scene.my_addon

		####### For Tuesday #######
		# recently added
		# row = layout.row()
		# box = row.box()
		# split = box.split()
		# split.label("Skip every ")
		# split.prop(myaddon, "frameskip")
		# split.label("frames")
		# split.operator("object.resize_animation_objects", text="Scale All Frames")
		layout.operator("object.resize_animation_objects", text="Scale All Frames")
		####### Done With For Tuesday #######
		
		# split = layout.split()
		# Scale Column
		# col = split.column(align=True)
		# col.label(text="Scale:")
		# col.prop(myaddon, "x_scale_float")
		# col.prop(myaddon, "y_scale_float")
		# col.prop(myaddon, "z_scale_float")
		# col.operator("object.resize_animation_objects")

		# # Location Column
		# col = split.column(align=True)
		# col.label(text="Location:")
		# col.prop(myaddon, "x_trans_float")
		# col.prop(myaddon, "y_trans_float")
		# col.prop(myaddon, "z_trans_float")
		# col.operator("object.translate_animation_objects")

		# # Rotation Column
		# col = split.column(align=True)
		# col.label(text="Rotation:")
		# col.prop(myaddon, "x_rot_float")
		# col.prop(myaddon, "y_rot_float")
		# col.prop(myaddon, "z_rot_float")
		# col.operator("object.rotate_animation_objects")


class BrenderMaterialPanel(View3DPanel, Panel):
	bl_idname = "OBJECT_PT_Brender_material_panel"
	bl_label = "Materials"
	bl_category = 'Brender'
	bl_context = "objectmode"


	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		myaddon = scene.my_addon
		ob = context.object

		layout.operator("object.create_default_mats")
		split = layout.split()

		if ob:
			layout.template_ID(ob, "active_material", new="material.new")
			row = layout.row()
			row.operator("object.apply_material_to_all")
			


class BrenderRenderPanel(View3DPanel, Panel):
	bl_idname = "OBJECT_PT_Brender_render_panel"
	bl_label = "Wireframe Overlay"
	bl_category = 'Brender'
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}
	# Removed poll classmethod so that this 
	# panel is always visible

	# Add UI elements here
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		myaddon = scene.my_addon

		row = layout.row()
		row.prop(myaddon, "wireframe_obj_string")

		split = layout.split()
		col = split.column()
		col.label(text="Bevel: ")
		col.prop(myaddon, "wf_bevel_depth")
		col.prop(myaddon, "wf_bevel_resolution")

		col = split.column()
		# The following is in "beta" since the modifications do not always produce ideal wireframes
		col.label(text="Modification: beta")
		col.prop(myaddon, "wf_offset")
		col.prop(myaddon, "wf_extrude")

		row = layout.row()
		row.operator("object.wireframe_overlay_preview")

		row = layout.row()
		row.operator("object.wireframe_overlay")


class BrenderProcessingPanel(View3DPanel, Panel):
	bl_idname = "OBJECT_PT_Brender_processing_panel"
	bl_label = "Object Processing"
	bl_category = 'Brender'
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}
	# Removed poll classmethod so that this 
	# panel is always visible

	# Add UI elements here
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		myaddon = scene.my_addon

		row = layout.row()
		row.prop(myaddon, "angle_thresh")
		layout.operator("object.edgesplit")

		
class BrenderScenePanel(View3DPanel, Panel):
	bl_idname = "OBJECT_PT_Brender_scene_panel"
	bl_label = "Scene Tools"
	bl_category = 'Brender'
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}
	# Removed poll classmethod so that this 
	# panel is always visible

	# Add UI elements here
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		myaddon = scene.my_addon

		layout.label(text="Camera Options")
		row = layout.row()
		# row.prop(myaddon, "cam_name")
		layout.operator("object.cam_setup_2d")

		layout.label(text="Light Options")
		layout.operator("object.light_setup_2d")

		layout.label(text="Default BG (Black)")
		layout.operator("object.create_black_bg")

		layout.label(text="Default BG (Green)")
		layout.operator("object.create_green_bg")

		layout.label(text="2D Material Defaults")
		layout.operator("object.create_default_wf_mat")
		layout.operator("object.create_clear_mat")

		layout.label(text="3D Material Defaults")
		layout.operator("object.create_grey_bg")

		# possible future addons
		# layout.label(text="2D Lighting defaults")
		# layout.label(text="under construction")


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.my_addon = PointerProperty(type=BrenderSettings)

def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.my_addon

if __name__ == "__main__":
	register()

	# exportBrenderSettings('INVOKE_DEFAULT')