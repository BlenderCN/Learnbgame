##   Todo   ########
#
#   V Get arguments working on OSX
#   - Get localview export working (not supported)
#   - Fix custom path and preload, with old scene opened wrong paths are used.
#     It uses the path from file for export and path for import fro ini. Add extra update for path on EXport
#   - Try scene without getConfig this is not needed as enum already loads settings
####################

####################
## v.0.6.3
## 29-12-18
## Changed
## - Added skip local view, some scene cause errors
##
## 12-01-19
## Fixed
## - Small UI change
## - Hotkey issue
##
## Added
## - Missing skip local to popup menu
##
## Changed
## - Popup menu doesnt have 2 buttons at the bottom, makes it more clear what export is
## - Label was replace due to new WM menu
## - Export button has more logical label

## v.0.6.4
## 12-01-19
## Changed
## - Popup menu doesnt have 2 buttons at the bottom, makes it more clear what export is
## - Label was replace due to new WM menu
## - Export button has more logical label
##
## Fixed
## - Apply modifier for bl 2.80
##
## Added
## - Undo for export operation in case of error or malfunction
####################

bl_info = {
	"name": "Headus UVLayout Bridge",
	"description": "Headus UVLayout Bridge - A bridge between Blender and Headus UVlayout for quick UVs unwrapping",
	"location": "3D VIEW > TOOLS > Headus UVlayout Panel",
	"author": "Rombout Versluijs // Titus Lavrov",
	"version": (0, 6, 4),
	"blender": (2, 78, 0),
#    "wiki_url": "https://gumroad.com/l/Blender2UVLayoutBridge",
	"wiki_url": "https://github.com/schroef/uvlayout_bridge",
	"tracker_url": "https://github.com/schroef/uvlayout_bridge/issues",
	"category": "Learnbgame",
}

import bpy
import os
import rna_keymap_ui
#import sys
import os.path
import subprocess
import tempfile
import time
import configparser


from sys import platform
from configparser import SafeConfigParser
from bpy.props import *
from bpy.types import Operator, AddonPreferences
from bpy_extras.io_utils import (ImportHelper)
from . config.registers import get_hotkey_entry_item

configFol = "config"
version = "Please choose version"

#-- LOAD / SET CONFIG FILE  --#
def setConfig(self, context):
	'''Save Custom Path in config file when property is updated

		:param context: context
	'''
	version = getattr(context.scene, "versionUVL", "")
	customPath = getattr(context.scene, "uvlb_customPath", "")
	pathEnable = getattr(context.scene, "uvlb_pathEnable", False)
	winPath = getattr(context.scene, "uvlb_winPath", "")
	config = configparser.ConfigParser()
	configPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), configFol + "/config.ini")
	print("UVlayout-Bridge: %s // %s // %s" % (customPath, pathEnable, winPath))
	config.read(configPath)
	if not config.has_section("main"):
		config.add_section('main')
	config.set('main', 'version', str(version))
	config.set('main', 'customPath', str(customPath))
	config.set('main', 'pathEnable', str(pathEnable))
	config.set('main', 'winPath', str(winPath))
	with open(configPath, 'w') as configfile:
		config.write(configfile)


def getVersionUVL():
	'''get UVlayout version from configuration file

		:return: versionUVL
		:rtype: bool
	'''

	version = "Please choose version"

	config = SafeConfigParser()
	for path in bpy.utils.script_paths():
		ConfigFile = os.path.join(path,"addons","uvlayout_bridge/",configFol + "/config.ini")
		if os.path.exists(ConfigFile):
			config.read(ConfigFile)
			try:
				version = config.get('main', 'version')
			except:
				version = "Please choose version"
	return version

def getCustomPath():
	'''get Custom Path version from configuration file

		:return: customPath
		:rtype: string
	'''

	customPath = "Please set path"
	pathEnable = False
	winPath = "Please set path"

	config = SafeConfigParser()
	for path in bpy.utils.script_paths():
		ConfigFile = os.path.join(path,"addons","uvlayout_bridge/",configFol + "/config.ini")
		if os.path.exists(ConfigFile):
			config.read(ConfigFile)
			try:
				customPath = config.get('main', 'customPath')
				pathEnable = config.getboolean('main', 'pathEnable')
				winPath = config.get('main', 'winPath')
			except:
				customPath = "Please set path"
				pathEnable = False
				winPath = "Please set path"

	return (customPath, pathEnable, winPath)



BoolProperty= bpy.types.BoolProperty
scn = bpy.types.Scene

#-- GET CUSTOM PATH / OSX & WIN --#
scn.uvlb_customPath = bpy.props.StringProperty(
	name="Custom Export Path",
	description = "Choose custom path instead of temp directory.",
	default = getCustomPath()[0],
	update = setConfig)

scn.uvlb_pathEnable = bpy.props.BoolProperty(
	name="Path Enable",
	description = "Choose custom path instead of temp",
	default = getCustomPath()[1],
	update = setConfig)

scn.uvlb_winPath = bpy.props.StringProperty(
	name="Path",
	description = "Choose custom path to Headus UVlayout application",
	default = getCustomPath()[2],
	subtype = 'DIR_PATH',
	update = setConfig)



#-- ENUM MENUS --#
scn.versionUVL = bpy.props.EnumProperty(
	items = (("Please choose version", "Please choose version", ""),("demo", "UVlayout Demo", "UVlayout Demo"),("student", "UVlayout Student", ""),("hobbist", "UVlayout Hobbist", ""),("pro", "UVlayout Pro", "")),
	name = "UVlayout Version",
	description = "Set UVlayout Version, needed for startin correct application",
	default = getVersionUVL(),
	update = setConfig)

def updateIcon(self, context):
	scn = bpy.types.Scene
	print("### Icons Updated ###")
	print(self.uvlb_mode)
	if (self.uvlb_mode == '0'):
		setattr(scn, "iconMode", 'EDITMODE_HLT')
	else:
		setattr(scn, "iconMode", 'MOD_SUBSURF')
	if (self.uvlb_uv_mode == '0'):
		setattr(scn, "iconUVMode", 'TEXTURE')
	else:
		setattr(scn, "iconUVMode", 'GROUP_UVS')


#-- BRIDGE ADDON OPTIONS --#
#---UV Channel selector---
scn.uvlb_uv_channel = IntProperty(
	name = "UV channel",
	description = "Select a UV channel for editing in export.",
	default = 1,
	min = 1,
	max = 8)

scn.spaceName = bpy.props.BoolProperty(
	name="Spaces in Name",
	default=False)

scn.selOnly = bpy.props.BoolProperty(
	name="Selection Only",
	description = "Export selected object(s) only. Otherwise all visible object are exported.",
	default=True)

scn.viewOnly = bpy.props.BoolProperty(
	name="Selection Only",
	default=False)

scn.appMod = bpy.props.BoolProperty(
	name="Apply Modifier",
	description="Applies subsurf modifer, also in Blender will this be applied. You can choose to make backup.",
	default=False)

scn.cloneOb = bpy.props.BoolProperty(
	name="Create Backup",
	description="Creates copy of the model before modifiers are applied.",
	default=False)

scn.useKeyMap = bpy.props.BoolProperty(
	name="Use short popup",
	description="Use Alt + Shit + U to open the popup window",
	default=True)

#--Icons Enummenus --#
scn.iconMode = EnumProperty(
	items = (('EDITMODE_HLT', "EDITMODE_HLT", ''),
		   ('MOD_SUBSURF', "MOD_SUBSURF", '')),
	name = "Mode",
	description = "POLY or SUBD",
	default = 'EDITMODE_HLT')

scn.iconUVMode = EnumProperty(
	items = (('TEXTURE', "TEXTURE", ''),('GROUP_UVS', "GROUP_UVS", '')),
	name = "UVMode",
	description = "Edit or New",
	default = 'TEXTURE')

#-- UVlayout OPTIONS --#
scn.uvlb_mode = EnumProperty(
	items = (('0', "Poly", ''),
		   ('1', "SUBD", '')),
	name = "Mode",
	description = "If the mesh being loaded is the control cage for a subdivision surface, then make sure that SUBD is selected. The subdivided surface will then be used in the flattening calculations, rather than the control cage itself, producing more accurate results. If the mesh isn't a subdivision surface, then select Poly. Mind that objects with low poly count can look different in UVlayout. The mesh isnt changed it only looks different in 3d view.",
	default = '0',
	update=updateIcon)

scn.uvlb_uv_mode = EnumProperty(
	items = (('0', "New", ''),('1', "Edit", '')),
	name = "UV",
	description = "If your mesh already has UVs and you want to reflatten them to reduce distortion, select Edit. Otherwise, select New to delete any existing UVs and start with a clean slate.",
	default = '0',
	update=updateIcon)

scn.uvlb_uv_weld = bpy.props.BoolProperty(
	name="Weld UV's",
	description = "If the loaded mesh has seams (green edges) between adjacent polys, reload with this option ticked. It'll weld all co-incident UVs together, but could break the OBJ Update tool and point correspondences between morph targets.",
	default=False)

scn.uvlb_uv_clean = bpy.props.BoolProperty(
	name="Clean",
	description = "If the loaded mesh has non-manifold edges (i.e. an edge is shared by more than two faces) then ticking this option will fix the problem geometry as its loaded. The clean will also remove duplicate faces. A summary of the changes made will be displayed once the file has been loaded.",
	default=False)

scn.uvlb_uv_detach = bpy.props.BoolProperty(
	name="Detach Flipped UVs",
	description = "Tick this option if you want flipped polys in UV space to be detached into separate shells.",
	default=False)

scn.uvlb_uv_geom = bpy.props.BoolProperty(
	name="Weld Geom Vertexes",
	description = "If there are geometry seams (blue edges) between seemingly continuous surfaces, then reload with this ticked to weld those up. Currently this triangulates the mesh also, so its recommended you only do this if you really have to.",
	default=False)

scn.uvlb_autoComm = bpy.props.BoolProperty(
	name="Automation:",
	description = "Use a couple commands to automate workflow. Can be a bit buggy!",
	default=False)

scn.uvlb_autoPack = bpy.props.BoolProperty(
	name="Packing",
	description = "Packs model or all models automatically.",
	default=False)

scn.uvlb_autoSave = bpy.props.BoolProperty(
	name="Auto Return",
	description = "Automatically sends the model back to Blender when all actions are done. Dont interupt this action, takes a small bit of time.",
	default=False)

scn.uvlb_help = bpy.props.BoolProperty(
	name="Help",
	description = "Hover over each button or menu for short detailed description of functions.",
	default=False)

scn.uvlb_autoCOMS = EnumProperty(
#    items = (('1', "Drop", ''),('2', "Flatten", ''),('3', "Optimize", ''),('4', "Drop-Flatten-Optimize", ''),('5', "Pack", ''),('6', "Drop-Flatten-Optimize-Pack", '')),
	items = (('5', "Pack", ''),('6', "Drop-Flatten-Optimize-Pack", '')),
	name = "Automation Commands",
	description = "Some commands are buggy and will crash the window. You need to redo the export from Blender and try again :(",
	default = '5')

scn.checkLocal = bpy.props.BoolProperty(
	name = "Skip Local",
	default = False,
	description="If issue with localview arrises skip it.")

	#---Check OS---
#    bpy.types.Scene.osSys = EnumProperty(
#            items = (('0', "WIN", ''),('1', "OSX", '')),
#            name = "OS check",
#            description="Check what OS is used",
#            default = '0')
	#--SYS check Enummenus --#
scn = bpy.types.Scene
if platform == "darwin":
	scn.osSys = '1'
if platform == "win32":
	scn.osSys = '0'
print("OS used: %s" % platform)


def is_local():
	for ob in bpy.context.scene.objects:
		print("ob: %s - %s" % (ob.name, ob.layers_local_view[0]))
		if ob.layers_local_view[0]:
			return True
		else:
			pass

#    if ob.layers_local_view[0]:
#        return True
#    else:
#        return False

def CheckSelection():
	objSelected = False
	if bpy.context.selected_objects != []:
		objSelected = True
	return objSelected


#-- Headus uvLayout Export/Import --#
def UVL_IO():
	scn = bpy.context.scene

	#---Variables---
	if platform == "win32":
		UVLayoutPath = scn.uvlb_winPath

	if scn.uvlb_pathEnable:
		path = scn.uvlb_customPath
	else:
		path = "" + tempfile.gettempdir()

#    path = "" + tempfile.gettempdir()
	path = '/'.join(path.split('\\'))

	file_Name = "Blender2UVLayout_TMP.obj"
	file_outName = "Blender2UVLayout_TMP.out"
	file_cmdName = "Blender2UVLayout_TMP.cmd"
	file_setName = "Blender2UVLayout_TMP.set"
	file_commands = "subd"
	uvl_exit_str = "exit"

	expObjs = []
	expMeshes = []
	uvlObjs = []
	Objs = []

	#--Check visible objects
	def layers_intersect(a, b, name_a="layers", name_b=None):
		return any(l0 and l1 for l0, l1 in zip(getattr(a, name_a), getattr(b, name_b or name_a)))

	def gather_objects(scene):
		objexcl = set()

		def no_export(obj):
#            return obj.select and (not obj.hide) and (not obj.hide_select) and layers_intersect(obj, scene) and obj.is_visible(scene)
			return (not obj.hide) and (not obj.hide_select) and layers_intersect(obj, scene) and obj.is_visible(scene)
		def is_selected(obj):
			return obj.select
		def add_obj(obj):
			if obj not in objexcl:
				scn.viewOnly = True
				if scn.selOnly:
					scn.viewOnly = False
					if (is_selected(obj)):
						objexcl.discard(obj)
					print ("Objects sel only: %s" % obj)
				else:
					objexcl.add(obj)
				print ("Objects include: %s" % obj)
				return

		for obj in scene.objects:
			if (not no_export(obj)):
				objexcl.discard(obj)
				continue
			add_obj(obj)

		return objexcl

	objexcl = gather_objects(bpy.context.scene)
#    print ("Objects: %s" % objexcl)
	for ob in objexcl:
		#--Select object only visible and set selection
		bpy.data.objects[ob.name].select = True
		print ("Objects exclude: %s" % ob.name)
		scn.selOnly = True

	#--Get selected objects---
	for ob in bpy.context.selected_objects:
		#---If space in name replace by underscore
		params = [" "] #list of search parameters
		#        [ o for o in bpy.context.scene.objects if o.active ]
		if any(x for x in params if x in ob.name): #search for params items in object name
			ob.name = ob.name.replace(" ","_")
			print("OB has space: %s" % ob.name)
			scn.spaceName = True

		if ob.type == 'MESH':
			if len(ob.data.uv_textures) < bpy.context.scene.uvlb_uv_channel:
				for n in range(bpy.context.scene.uvlb_uv_channel):
					ob.data.uv_textures.new()
		ob.data.uv_textures.active_index = (bpy.context.scene.uvlb_uv_channel - 1)
		Objs.append(ob)

	#---Lists buildUP---
	#---Create and prepare objects for export---
	for ob in Objs:
		for mod in ob.modifiers:
			if scn.appMod:
				if scn.cloneOb:
					newObj = ob.copy()
					newObj.data = ob.data.copy()
					newObj.name = ob.name + "_Backup"
					newObj.animation_data_clear()
					scn.objects.link(newObj)
				if mod.type == 'SUBSURF':
					print ("Obj Name: %s - Mod Applied: %s" % (ob.name, mod.type))
					bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
		newObj = ob.copy()
		newObj.data = ob.data.copy()
		newObj.animation_data_clear()
		newObj.name = ob.name + "__UVL"
		bpy.context.scene.objects.link(newObj)
		expObjs.append(newObj)
		expMeshes.append(newObj.data)
	#---Texture channels cleanup exept uvlb_uv_channel
	for ob in expMeshes:
		active_index = (bpy.context.scene.uvlb_uv_channel - 1)
		texName=ob.uv_textures[active_index].name
		uv_textures = ob.uv_textures
		ObjTexs=[]
		for t in uv_textures:
			ObjTexs.append(t.name)
		for u in ObjTexs:
			if u != texName:
				uv_textures.remove(uv_textures[u])

	#---Select objects for EXPORT
	bpy.ops.object.select_all(action='DESELECT')
	for ob in expObjs:
		bpy.data.objects[ob.name].select = True


	#---EXPORT---
	print("Export path: %s - File:%s" % (path, file_Name))
	bpy.ops.export_scene.obj(filepath=path + file_Name,
								check_existing = True,
								axis_forward = 'Y',
								axis_up = 'Z',
								filter_glob = "*.obj;*.mtl",
								use_selection = scn.selOnly,
								use_animation = False,
								use_mesh_modifiers = scn.appMod,
#                                use_mesh_modifiers_render = False,
								use_edges = False,
								use_smooth_groups = False,
								use_smooth_groups_bitflags = False,
								use_normals = True,
								use_uvs = True,
								use_materials = False,
								use_triangles = False,
								use_nurbs = False,
								use_vertex_groups = False,
								use_blen_objects = False,
								group_by_object = True,
								group_by_material = False,
								keep_vertex_order = True,
								global_scale = 1,
								path_mode = 'AUTO')
	#--Reset Sel only
	if scn.viewOnly:
		scn.selOnly = False
	#---OBJs Clean up and deselect before import
	for ob in expMeshes:
		bpy.data.meshes.remove(ob,True)

	bpy.ops.object.select_all(action='DESELECT')


#
	#-Set uvLayout mode
	if (bpy.context.scene.uvlb_mode == '0'):
		uvlb_mode = 'Poly'
	if (bpy.context.scene.uvlb_mode == '1'):
		uvlb_mode = 'SUBD'
	#-Set UVs mode
	if (bpy.context.scene.uvlb_uv_mode == '0'):
		uvlb_uv_mode = 'New'
	if (bpy.context.scene.uvlb_uv_mode == '1'):
		uvlb_uv_mode = 'Edit'
	#-Set Weld UVs
	if scn.uvlb_uv_weld:
		uvlb_uv_weld = 'Weld'
	if not scn.uvlb_uv_weld:
		uvlb_uv_weld = ''
	#-Set Clean
	if scn.uvlb_uv_clean:
		uvlb_uv_clean = 'Clean'
	if not scn.uvlb_uv_clean:
		uvlb_uv_clean = ''
	#-Set Detach UVs
	if scn.uvlb_uv_detach:
		uvlb_uv_deach = 'Detach flipped'
	if not scn.uvlb_uv_detach:
		uvlb_uv_deach = ''
	#-Set Weld GEOM Vertexes
	if scn.uvlb_uv_geom:
		uvlb_uv_geom = 'Geom vertexes'
	if not scn.uvlb_uv_geom:
		uvlb_uv_geom = ''

	#-- OS CHECK--
	if platform == "darwin":
		versionUVL = getattr(scn, "versionUVL")
		dropSet = 0
		if os.path.isfile(path + file_setName) == False:
			if dropSet == 0:
#                loadAction = 'run UVLayout|Pack|Pack All' + '\n' +'run UVLayout|Plugin|Save'
#                loadAction = "drop \ n auto obj \n auto dxf "
				loadAction = uvlb_mode + ',' + uvlb_uv_mode + ',' + uvlb_uv_weld + ',' + uvlb_uv_clean + ',' + uvlb_uv_deach + ',' + uvlb_uv_geom

				f = open(path + file_setName, "w+")
	#            print("Commands Sent: %s - %s" % (uvlb_mode, uvlb_uv_mode))
				f.write(''.join([loadAction]))
				f.close()
				dropSet = 1
#                time.sleep(2)

		uvlayoutpath = []
		appOpen = '/Applications/headus-UVLayout-'+versionUVL+'.app/Contents/MacOS/uvlayout-maya'

		uvlayoutpath.append(appOpen)
		uvlayoutpath.append(path+file_Name)
		uvlayout_proc = subprocess.Popen(uvlayoutpath)


	elif platform == "win32":
		uvlayout_proc = subprocess.Popen([UVLayoutPath + 'uvlayout.exe', '-plugin,' + uvlb_mode + ',' + uvlb_uv_mode, path + file_Name])

	dropCom = 0

	#---IMPORT---
	while not os.path.isfile(path + file_outName) and uvlayout_proc.poll() != 0:

		#-- SEND AUTOMATION COMMANDS ---
		if (os.path.isfile(path + file_cmdName) == False) and scn.uvlb_autoComm:
			if dropCom == 0:
				time.sleep(0)
				print("Commands Send")
#                comm = ''
				if scn.uvlb_autoCOMS == '1':
					comm = 'drop \n run UVLayout|Pack|Pack All'
				if scn.uvlb_autoCOMS == '2':
					comm = 'drop \n auto obj \ run UVLayout|Pack|Pack All'
				if scn.uvlb_autoCOMS == '3':
					comm = 'drop \n auto dxf \ run UVLayout|Pack|Pack All'
				if scn.uvlb_autoCOMS == '4':
					comm = 'drop \n auto obj \n auto dxf '
				if scn.uvlb_autoCOMS == '5':
					comm = 'run UVLayout|Pack|Pack All'
				if scn.uvlb_autoCOMS == '6':
					comm = 'drop \n auto obj \n auto dxf \n run UVLayout|Pack|Pack All'

				if scn.uvlb_autoPack:
					comm = 'run UVLayout|Pack|Pack All'
#                comm = 'drop \ n auto obj'
#                comm = "drop \ n auto obj \n auto eps \n auto dxf"
#                comm = "drop \ n auto dxf"

#                comm = 'run UVLayout|Pack|Pack All' + '\n' +'run UVLayout|Plugin|Save'
#                comm = "Poly"
#                comm = "drop \ n auto obj \n "
				f = open(path + file_cmdName, "w+")
	#            print("Commands Sent: %s - %s" % (uvlb_mode, uvlb_uv_mode))
				f.write(''.join([comm]))
				f.close()
				dropCom = 1

		#-- AUTO SAVE ACTION
		if (os.path.isfile(path + file_cmdName) == False) and scn.uvlb_autoSave:
			comm = ''
			time.sleep(2)
#                if scn.uvlb_autoDRPS:
			comm = 'run UVLayout|Plugin|Save'
			f = open(path + file_cmdName, "w+")
			f.write(''.join([comm]))
			f.close()
			dropCom = 2
#            time.sleep(1)

#        time.sleep(3)

		#-- IMPORT OBJ BACK TO BLENDER --
#        print("Import path: %s - File:%s" % (path, file_Name))
		if os.path.isfile(path + file_outName) == True:
#            time.sleep(1)
			bpy.ops.import_scene.obj(filepath = path + file_outName,
									axis_forward = 'Y',
									axis_up = 'Z',
									filter_glob = "*.obj;*.mtl",
									use_edges = False,
									use_smooth_groups = False,
									use_split_objects = True,
									use_split_groups = True,
									use_groups_as_vgroups = True,
									use_image_search = False,
									split_mode = 'ON',
									global_clamp_size = 0);

			#---Close UVLAYOUT ---
			f = open(path + file_cmdName, "w+")
			f.write(''.join([uvl_exit_str]))
			f.close()

			#---Transfer UVs and CleanUP---
			for ob in bpy.context.selected_objects:
				uvlObjs.append(ob)

			bpy.ops.object.select_all(action='DESELECT')

			for ob in uvlObjs:
				#---Get source object name
				refName=ob.name.split('__UVL')
				#---Select source object---
				bpy.data.objects[refName[0]].select = True
				#---Select UVL object
				bpy.context.scene.objects.active = bpy.data.objects[ob.name]
				#---Transfer UVs from UVL object to Source object
				bpy.ops.object.join_uvs()
				bpy.ops.object.select_all(action='DESELECT')

			bpy.ops.object.select_all(action='DESELECT')

			for ob in uvlObjs:
				print("DEL")
				bpy.data.meshes.remove(ob.data,True)

			bpy.ops.object.select_all(action='DESELECT')

			for ob in Objs:
#                bpy.data.objects[ob.name].select = True
				#---Make new seams
				ob.select = True
				bpy.context.scene.objects.active = ob
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.uv.seams_from_islands()
				bpy.ops.object.editmode_toggle()


class FILE_SN_choose_path(bpy.types.Operator, ImportHelper):
	"""Choose path custom export location """
	bl_idname = "open.path_loc"
	bl_label = "Choose path export location"

	#    filename_ext = "*.scn.thea; *.mat.thea"
	filter_glob = StringProperty(
		default="DIR_PATH",
		#            default="*.png;*.jpeg;*.jpg;*.tiff")#,
		options={'HIDDEN'}, )

	def execute(self, context):
		scn = context.scene
		if scn != None:
			setattr(scn, "uvlb_customPath", self.filepath)
			return {'FINISHED'}
#        else:
#            #            mat = bpy.data.materials["basic_gray"]
#            mat = bpy.data.materials[checkTheaExtMat()[1]]
#            setattr(mat, "thea_extMat", self.filepath)
#            return {'FINISHED'}


helper_tabs_items = [("EXECUTE", "Modifiers", "")]

#-- START EXPORT  --#
class UVLB_OT_Export(Operator):
	"""Unwrap models using Headus UVlayout, this Bridge provides a easy workflow."""
	bl_idname = "uvlb.export"
	bl_name = "UVlayout Bridge"
	bl_label = "UVlayout Bridge"
	bl_options = {'REGISTER','UNDO'}

	tab = EnumProperty(name = "Tab", default = "EXECUTE", items = helper_tabs_items)

	def execute(self, context):
		scn = bpy.context.scene
		scn.spaceName = False

		## Check if object is editmode
		if bpy.context.active_object.mode == 'EDIT':
			bpy.ops.object.editmode_toggle()

		if scn.checkLocal:
			if is_local():
				self.report({'ERROR'}, "Localview Not Supported")
				return {'FINISHED'}
		#-- OSX check if application is chosen correct
		if platform == "darwin":
			versionUVL = getattr(scn, "versionUVL")
			if os.path.isfile('/Applications/headus-UVLayout-'+versionUVL+'.app/Contents/MacOS/uvlayout-plugin') == False:
				info = "Wrong UVlayout version in addon settings"
				self.report({'ERROR'}, info)
				return {'FINISHED'}

		if scn.selOnly:
			if (CheckSelection() == False):
				self.report({'ERROR'}, "Nothing selected")
				return {'FINISHED'}

		#-- Run export eaction
		UVL_IO()

		#-- If files had space they are removed warning
		if scn.spaceName:
			self.report({'ERROR'}, "Some objects needed space removing")
			return {'FINISHED'}

		self.report ({'INFO'}, 'UVLayout bridge - Done!')

		return {'FINISHED'}


#-- BRIDGE PANEL TOOL TAB __#
class UVLBridge_Panel(bpy.types.Panel):
	"""Creates a Unfold3d bridge Panel"""
	bl_label = "Headus UVlayout Bridge"
	bl_idname = "UVLBridge"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Tools"
	bl_context = "objectmode"
	bl_options = {"DEFAULT_CLOSED"}

	@classmethod
	def poll(cls, context):
		# Only allow in Object mode and for a selected mesh.
		return (context.object is not None and context.object.type == "MESH")

	def draw(self, context):
		layout = self.layout
		scn = bpy.context.scene
		obj = bpy.context.object
		me = obj.data

		#-- UVLAYOUT LOAD OPTIONS --
		settingsBox = layout.box()
		uvlbHeader = settingsBox.split(.9)
		column = uvlbHeader.column()
		column.row().label("Load Options:")

		column = uvlbHeader.column()
		column.row().prop(scn, "uvlb_help", text="", icon_value=custom_icons["help"].icon_id, emboss=False)

		uvlbOptions = settingsBox.split(.5)
		column = uvlbOptions.column()
		column.row().label("Mode:")
		column.row().label("Uv Mode:")

		column = uvlbOptions.column()
		column.row().prop(scn, "uvlb_mode", text="",icon = getattr(scn,"iconMode",2))
		column.row().prop(scn, "uvlb_uv_mode", text="",icon = getattr(scn,"iconUVMode",2))

		uvlbOptions = settingsBox.split(.9)
		column = uvlbOptions.column()
		column.row().label("Weld UVs")
		column.row().label("Detach Flipped UV's")
		if (getattr(scn, "uvlb_uv_mode",) == '0'):
			column.row().label("Clean")

		column = uvlbOptions.column()
		column.row().prop(scn, "uvlb_uv_weld", text="")
		column.row().prop(scn, "uvlb_uv_detach", text="")
		if (getattr(scn, "uvlb_uv_mode",) == '0'):
			column.row().prop(scn, "uvlb_uv_clean", text="")
			# uvlbOptions.prop(scn, "uvlb_uv_geom") #Destroys linking import- triangulates the mesh

		#-- QUICK COMMANDS --#
		settingsBox = layout.box()
		uvlbAutoCom = settingsBox.split(.9)
		column = uvlbAutoCom.column()
		column.row().label("Automation:")
		if scn.uvlb_autoComm:
			column.row().label("Auto-Pack")
			column.row().label("Save & Return")

		column = uvlbAutoCom.column()
		column.row().prop(scn, "uvlb_autoComm", text="")
		if scn.uvlb_autoComm:
			column.row().prop(scn, "uvlb_autoPack", text="")
			column.row().prop(scn, "uvlb_autoSave", text="")

		#-- UVMAPS --
		uvMapBox = layout.box()
		uvMapChannel = uvMapBox.row()
		uvMapChannel = uvMapChannel.split(percentage=0.5)
		uvMapChannel.label("UV Channel:", icon="GROUP_UVS")
		uvMapChannel.prop(scn, "uvlb_uv_channel", text="")

		#-- OBJ EXPORT options --
		objBox = layout.box()
		objBox = objBox.split(0.9)

		column = objBox.column()
		column.row().label("OBJ Export Settings:")
		column.row().label("Selection Only")
		column.row().label("Apply Modifiers")
		if scn.appMod:
			column.row().label("Create Backup")
			column.row().label("Subsurf will be applied, backup?", icon='ERROR')
		column.row().label("Skip localview check")

		column = objBox.column()
		column.row().label("")
		column.row().prop(scn,"selOnly", text="")
		column.row().prop(scn,"appMod", text="")
		if scn.appMod:
			column.row().prop(scn,"cloneOb", text="")
			column.row().label(text="")
		column.row().prop(scn,"checkLocal", text="")

		#-- START EXPORT --
		layout.operator("uvlb.export", text = "Unwrap in UVlayout  >", icon_value=custom_icons["uvl"].icon_id)


#-- BRIDGE WM DIALOG MENU __#
class UVLAYOUT_OT_bridge(Operator):
	bl_idname = "uvlayout.bridge"
	bl_name = "UVlayout DIALOG MENU"
	bl_label = "Headus UVlayout Bridge"

	tab = EnumProperty(name = "Tab", default = "EXECUTE",  items = helper_tabs_items)

	def execute(self, context):
		return {'FINISHED'}

	def check(self, context):
		return True

	@classmethod
	def poll(cls, context):
		# Only allow in Object mode and for a selected mesh.
		return (bpy.context.object is not None and bpy.context.object.type == "MESH")

	def draw(self, context):
		layout = self.layout
		scn = bpy.context.scene
		obj = bpy.context.object
		me = obj.data

		#Replaces header panel
		layout.label(text=self.bl_label)

		#-- UVLAYOUT LOAD OPTIONS --
		settingsBox = layout.box()
		uvlbHeader = settingsBox.split(.92)
		column = uvlbHeader.column()
		column.row().label("Load Options:")

		column = uvlbHeader.column()
		column.row().prop(scn, "uvlb_help", text="", icon_value=custom_icons["help"].icon_id, emboss=False)

		uvlbOptions = settingsBox.split(.5)
		column = uvlbOptions.column()
		column.row().label("Mode:")
		column.row().label("Uv Mode:")

		column = uvlbOptions.column()
		column.row().prop(scn, "uvlb_mode", text="",icon = getattr(scn,"iconMode",2))
		column.row().prop(scn, "uvlb_uv_mode", text="",icon = getattr(scn,"iconUVMode",2))

		uvlbOptions = settingsBox.split(.92)
		column = uvlbOptions.column()
		column.row().label("Weld UVs")
		column.row().label("Detach Flipped UV's")
		if (getattr(scn, "uvlb_uv_mode",) == '0'):
			column.row().label("Clean")

		column = uvlbOptions.column()
		column.row().prop(scn, "uvlb_uv_weld", text="")
		column.row().prop(scn, "uvlb_uv_detach", text="")
		if (getattr(scn, "uvlb_uv_mode",) == '0'):
			column.row().prop(scn, "uvlb_uv_clean", text="")
			# uvlbOptions.prop(scn, "uvlb_uv_geom") #Destroys linking import- triangulates the mesh

		#-- QUICK COMMANDS --#
		settingsBox = layout.box()
		uvlbAutoCom = settingsBox.split(.92)
		column = uvlbAutoCom.column()
		column.row().label("Automation:")
		if scn.uvlb_autoComm:
			column.row().label("Auto-Pack")
			column.row().label("Save & Return")

		column = uvlbAutoCom.column()
		column.row().prop(scn, "uvlb_autoComm", text="")
		if scn.uvlb_autoComm:
			column.row().prop(scn, "uvlb_autoPack", text="")
			column.row().prop(scn, "uvlb_autoSave", text="")

		#-- UVMAPS --
		uvMapBox = layout.box()
		uvMapChannel = uvMapBox.row()
		uvMapChannel = uvMapChannel.split(percentage=0.5)
		uvMapChannel.label("UV Channel:", icon="GROUP_UVS")
		uvMapChannel.prop(scn, "uvlb_uv_channel", text="")

		#-- OBJ EXPORT options --
		objBox = layout.box()
		objBox = objBox.split(0.92)

		column = objBox.column()
		column.row().label("OBJ Export Settings:")
		column.row().label("Selection Only")
		column.row().label("Apply Modifiers")
		if scn.appMod:
			column.row().label("Create Backup")
			column.row().label("Subsurf will be applied, backup?", icon='ERROR')
		column.row().label("Skip localview check")

		column = objBox.column()
		column.row().label("")
		column.row().prop(scn,"selOnly", text="")
		column.row().prop(scn,"appMod", text="")
		if scn.appMod:
			column.row().prop(scn,"cloneOb", text="")
			column.row().label(text="")
		column.row().prop(scn,"checkLocal", text="")

		#---Send button---
		layout.operator("uvlb.export", text = "Unwrap in UVlayout  >", icon_value=custom_icons["uvl"].icon_id)
		layout.separator()

	def invoke(self, context, event):
		return context.window_manager.invoke_popup(self, width=425)
		#return context.window_manager.invoke_props_dialog(self, width=425)
#
#    def modal(self, context, event):
#        return context.window_manager.invoke_props_dialog(self, width=225)



#-- ADDON PREFS --#
class Blender2UVLayoutAddonPreferences(AddonPreferences):
	""" Preference Settings Addin Panel"""
	bl_idname = __name__


	def draw(self, context):
		layout = self.layout
		scene = context.scene


		if platform == "win32":
			box=layout.box()
			split = box.split()
			col = split.column()
			col.label(text = "Application Path Headus UVLayout v2.")
			col.prop(scene, "uvlb_winPath", text="")
			col.separator()
		if platform == "darwin":
			box=layout.box()
			split = box.split()
			col = split.column()
			col.label("Headus UVlayout Version:")
			col.prop(scene, "versionUVL", text="")
			col.label(text = "* No application path settings needed on OSX")
#            col.separator()

		col.separator()
		#-- CUSTOM EXPORT PATH --
		expBut = layout.box()
		expBut = expBut.split(.95)

		column = expBut.column()
		column.row().label("Custom export path:")
		if scene.uvlb_pathEnable:
			column.row().prop(scene, "uvlb_customPath", text="")
			column.row().label("Path will be saved per scene")
			column.separator()

		column = expBut.column()
		column.row().prop(scene,"uvlb_pathEnable", text="")
		if scene.uvlb_pathEnable:
			column.row().operator("open.path_loc", text="", icon='FILESEL')
			column.separator()

		box=layout.box()
		split = box.split()
		col = split.column()
#        col.separator()
		col.label('Hotkeys:')
		col.label('Do NOT remove hotkeys, disable them instead!')

		col.separator()
		wm = bpy.context.window_manager
		kc = wm.keyconfigs.user

		km = kc.keymaps['3D View']
		kmi = get_hotkey_entry_item(km, 'uvlb.export', 'EXECUTE', 'tab')
		if kmi:
			col.context_pointer_set("keymap", km)
			rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
			col.label("Quick export using last settings")

		else:
			col.label("Shift + V = quick export using last settings")
			col.label("restore hotkeys from interface tab")

		col.separator()
		km = kc.keymaps['3D View']
		kmi = get_hotkey_entry_item(km, 'uvlayout.bridge', 'EXECUTE', 'tab')
		if kmi:
			col.context_pointer_set("keymap", km)
			rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
			col.label("Opens the popup window")
		else:
			col.label("Alt + Shift + V = opens the popup window")
			col.label("restore hotkeys from interface tab")
		col.separator()



class OBJECT_OT_b2uvl_addon_prefs(Operator):
	bl_idname = "object.b2uvl_addon_prefs"
	bl_label = "Addon Preferences"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		if platform == "win32":
			user_preferences = context.user_preferences
			addon_prefs = user_preferences.addons[__name__].preferences

			info = ("Path: %s" % (addon_prefs.uvlb_winPath))

		self.report({'INFO'}, info)
		print(info)

		return {'FINISHED'}

def icon_Load():
	# importing icons
	import bpy.utils.previews
	global custom_icons
	custom_icons = bpy.utils.previews.new()

	# path to the folder where the icon is
	# the path is calculated relative to this py file inside the addon folder
	my_icons_dir = os.path.join(os.path.dirname(__file__), configFol)

	# load a preview thumbnail of a file and store in the previews collection
	custom_icons.load("uvl", os.path.join(my_icons_dir, "uvl.png"), 'IMAGE')
	custom_icons.load("help", os.path.join(my_icons_dir, "help.png"), 'IMAGE')

# global variable to store icons in
custom_icons = None


addon_keymaps = []
def register():
	bpy.utils.register_module(__name__)

	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon

	km = kc.keymaps.new(name = "3D View", space_type = "VIEW_3D")

	kmi = km.keymap_items.new("uvlayout.bridge", "V", "PRESS", alt = True, shift = True)
	kmi.properties.tab = "EXECUTE"
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("uvlb.export", "V", "PRESS", shift = True)
	kmi.properties.tab = "EXECUTE"

	addon_keymaps.append((km, kmi))
	icon_Load()




def unregister():
	global custom_icons
	bpy.utils.previews.remove(custom_icons)

	# handle the keymap
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()

