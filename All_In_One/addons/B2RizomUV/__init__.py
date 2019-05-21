bl_info = {
	"name": "B2RizomUV",
	"author": "Erik Sutton / Technical Artist",
	"version": (1, 5, 0),
	"blender": (2, 80, 0),
	"location": "UV > B2RizomUV - UV Unwrapper ",
	"description": "Blender to RizomUV bridge for Uv Unwrapping",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame",
}

import os
import subprocess
import tempfile
import os.path
from sys import platform
import bpy
from bpy.props import *
from bpy.types import Operator, AddonPreferences


# from . import addon_updater_ops //Looking into getting this added to the plugin

def B2RizomUV_AutoFunction():
	meshCheck()
	path, obj, nmList, inList = B2RizomUV_Utilites()

	# ---------------------------------------- Exporting ---------------------------------------

	bpy.ops.export_scene.obj(filepath=path + obj, check_existing=True, axis_forward='-Z', axis_up='Y',
	                         filter_glob="*.obj;*.mtl",
	                         use_selection=True, use_animation=False, use_mesh_modifiers=bpy.context.scene.modifierApply, use_edges=True,
	                         use_smooth_groups=False,
	                         use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=False,
	                         use_triangles=False,
	                         use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False,
	                         group_by_material=False,
	                         keep_vertex_order=True, global_scale=1, path_mode='AUTO')

	objfile_string = "U3dLoad({File={Path='" + path + obj + "', ImportGroups=true, XYZ=true}, NormalizeUVW=true})\n"

	textureSettings_string = "U3dSet({Path='Prefs.PackOptions.MapResolution', Value=" + str(bpy.context.scene.mapSize) + "})\n\
	U3dIslandGroups({Mode='SetGroupsProperties', MergingPolicy=8322, GroupPaths={ 'RootGroup' }, Properties={Pack={SpacingSize=" + str(
		bpy.context.scene.spacing) + "}}})\n\
	U3dIslandGroups({Mode='SetGroupsProperties', MergingPolicy=8322, GroupPaths={ 'RootGroup' }, Properties={Pack={MarginSize=" + str(bpy.context.scene.margin) + "}}})"

	main_string = "U3dIslandGroups({Mode='SetGroupsProperties', MergingPolicy=8322, GroupPaths={ 'RootGroup' }, Properties={Pack={Resolution=" + str(bpy.context.scene.packQuality) + "}}})\n\
	" + algorithmString + "\
	U3dCut({PrimType='Edge'})\n\
	U3dUnfold({PrimType='Edge', MinAngle=1e-005, Mix=1, Iterations=" + str(bpy.context.scene.optimize) + ", PreIterations=5, StopIfOutOFDomain=false, RoomSpace=0, PinMapName='Pin', ProcessNonFlats=true, ProcessSelection=true, ProcessAllIfNoneSelected=true, ProcessJustCut=true})\n\
	U3dIslandGroups({Mode='DistributeInTilesEvenly', MergingPolicy=8322, GroupPath='RootGroup'})\n\
	U3dPack({ProcessTileSelection=false, RecursionDepth=1, RootGroup='RootGroup', Scaling={}, Rotate={}, Translate=true, LayoutScalingMode=2})\n\
	U3dIslandGroups({Mode='DistributeInTilesByBBox', MergingPolicy=8322})\n\
	U3dIslandGroups({Mode='DistributeInTilesEvenly', MergingPolicy=8322, UseTileLocks=true, UseIslandLocks=true})\n\
	U3dPack({ProcessTileSelection=false, RecursionDepth=1, RootGroup='RootGroup', Scaling={Mode=0}, Rotate={Mode=0}, Translate=true, LayoutScalingMode=2})\n\
	U3dSave({File={Path='" + path + obj + "', UVWProps=true}, __UpdateUIObjFileName=true})\n\
	U3dQuit()"

	hierString = ""
	distoString = ""
	genString = ""

	if (bpy.context.scene.autoSeamAlgorithm == '0'):
		for options in hierOPTIONS:
			hierString += options

	if (bpy.context.scene.distoControl == True) and (bpy.context.scene.autoSeamAlgorithm == '0') or (
				bpy.context.scene.autoSeamAlgorithm == '1'):
		for disS in distoOPTIONS:
			distoString += disS

	if (bpy.context.scene.tFlips == True) or (bpy.context.scene.overlaps == True) or (bpy.context.scene.holeFill == True):
		for genOps in genOPTIONS:
			genString += genOps

	f = open(path + "Unwrap.lua", "w+")
	f.write(''.join([objfile_string, genString, distoString, hierString, textureSettings_string, main_string]))
	f.close()

	rizomUVPath = bpy.context.user_preferences.addons[__name__].preferences.filepath

	if platform == "darwin":
		l = os.listdir(rizomUVPath)
		appName = (str(l).strip("[]")).strip("'")
		subprocess.run([rizomUVPath + appName, '-cfi', path + 'Unwrap.lua'])
	elif platform == "win32":
		if os.path.isfile(rizomUVPath + 'unfold3d.exe'):
			subprocess.run([rizomUVPath + 'unfold3d.exe', '-cfi', path + 'Unwrap.lua'])
		else:
			subprocess.run([rizomUVPath + 'rizomuv.exe', '-cfi', path + 'Unwrap.lua'])

	B2RizomUV_ImportFunction(path, obj, nmList, inList)


def B2RizomUV_ManuelExport():
	meshCheck()
	path, obj, nmList, inList = B2RizomUV_Utilites()

	bpy.ops.export_scene.obj(filepath=path + obj, check_existing=True, axis_forward='-Z', axis_up='Y',
	                         filter_glob="*.obj;*.mtl",
	                         use_selection=True, use_animation=False, use_mesh_modifiers=bpy.context.scene.modifierApply, use_edges=True,
	                         use_smooth_groups=False,
	                         use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=False,
	                         use_triangles=False,
	                         use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False,
	                         group_by_material=False,
	                         keep_vertex_order=True, global_scale=1, path_mode='AUTO')

	objfile_string = "U3dLoad({File={Path='" + path + obj + "', ImportGroups=true, XYZUVW=true, UVWProps=true}})\n"

	f = open(path + "Unwrap.lua", "w+")
	f.write(''.join([objfile_string]))
	f.close()

	rizomUVPath = bpy.context.user_preferences.addons[__name__].preferences.filepath

	if platform == "darwin":
		l = os.listdir(rizomUVPath)
		appName = (str(l).strip("[]")).strip("'")
		subprocess.Popen([rizomUVPath + appName, '-cfi', path + 'Unwrap.lua'])

	elif platform == "win32":
		if os.path.isfile(rizomUVPath + 'unfold3d.exe'):
			subprocess.Popen([rizomUVPath + 'unfold3d.exe', '-cfi', path + 'Unwrap.lua'])
		else:
			subprocess.Popen([rizomUVPath + 'rizomuv.exe', '-cfi', path + 'Unwrap.lua'])




def B2RizomUV_ManuelImport():
	path = manList[0]
	obj = manList[1]
	nmList = manList[2]
	inList = manList[3]
	B2RizomUV_ImportFunction(path, obj, nmList, inList)

def B2RizomUV_ImportFunction(Path, Object, Names, ImportList):
	# ---------------------------------------- Importing ---------------------------------------
	# region Importing
	imported_object = bpy.ops.import_scene.obj(filepath=Path + Object)
	obj_object = bpy.context.selected_objects[0]

	for inObj in bpy.context.selected_objects:
		ImportList.append(inObj)
	ImportList.sort(key=lambda obj: obj.name)
	print(Names)
	print(ImportList)
	for obj in bpy.context.selected_objects:
		obj.select = False

	for imObjs in ImportList:

		# --------- Transfer UVs ----------
		imObjs.select = True
		tmpString = "" + '{:04d}'.format(Names[ImportList.index(imObjs)][1])
		bpy.data.objects[tmpString].select = True
		bpy.context.scene.objects.active = imObjs
		bpy.ops.object.join_uvs()

		# --------- Restoring Original Name ----------
		bpy.context.scene.objects.active = bpy.data.objects[tmpString]
		tmpObj = bpy.context.active_object
		tmpObj.name = str(Names[ImportList.index(imObjs)][0])

		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)
		bpy.ops.object.mode_set(mode='OBJECT')

		bpy.data.objects[tmpObj.name].select = False
		bpy.ops.object.delete()

		for oriObj in bpy.context.selected_objects:
			oriObj.select = False

	# endregion
	# ----------------- Clearing strings for further use after reimport ----------------------
	hierString = ""
	hierOPTIONS[:] = []
	distoString = ""
	distoOPTIONS[:] = []
	genString = ""
	genOPTIONS[:] = []
	manList[:] = []


# ----------------------------------------------------------------------------------------


algorithmCMDStrings = "U3dSelect({PrimType='Edge', Select=true, ResetBefore=true, WorkingSetPrimType='Island', ProtectMapName='Protect', FilterIslandVisible=true, Auto={SharpEdges={AngleMin=60, PipesCutter=true, HandleCutter=true}})"
algorithmString = ""

hierOPTIONS = []
distoOPTIONS = []
genOPTIONS = []
manList = []


# ---------------------------------------- HELPER FUNCTIONS -----------------------------------------

def B2RizomUV_Utilites():

	path = tempfile.gettempdir() + "/"
	path = '/'.join(path.split('\\'))
	obj = "Tmp_out.obj"
	# originalObj = bpy.data.objects.get(bpy.context.active_object.name)

	outList = []
	nmList = []
	inList = []

	for outObj in bpy.context.selected_objects:
		outList.append(outObj)

	for objs in outList:
		nmList.append([objs.name, outList.index(objs)])
		objs.name = '{:04d}'.format(nmList[outList.index(objs)][1])

	manList.append(path)
	manList.append(obj)
	manList.append(nmList)
	manList.append(inList)

	print(path)

	return (path, obj, nmList, inList)

def meshCheck():
	if not bpy.context.object.data.uv_layers:
		bpy.ops.mesh.uv_texture_add()

	# Add more mesh check here if proven important for reimporting failures

def set_settings():
	global genOPTIONS

	if bpy.context.scene.tFlips == True:
		genOPTIONS.append("U3dSet({Path='Prefs.TriangleFlipsOn', Value=true})\n")
	if bpy.context.scene.overlaps == True:
		genOPTIONS.append("U3dSet({Path='Prefs.BorderIntersectionsOn', Value=true})\n")
	if bpy.context.scene.holeFill == True:
		genOPTIONS.append("U3dSet({Path='Vars.Unwrap.FillHoles', Value=true})\n")

	print(genOPTIONS)

def set_algorithm(self, context):
	global algorithmCMDStrings, algorithmString, hierString

	algorithmCMDStrings = \
		[
			"U3dSelect({PrimType='Edge', Select=true, ResetBefore=true, WorkingSetPrimType='Island', ProtectMapName='Protect', FilterIslandVisible=true, Auto={Skeleton={}, Open=true, PipesCutter=true, HandleCutter=true}})",
			"U3dSelect({PrimType='Edge', Select=true, ResetBefore=true, WorkingSetPrimType='Island', ProtectMapName='Protect', FilterIslandVisible=true, Auto={QuasiDevelopable={Developability=" + str(
				bpy.context.scene.mosaicForce) + ", IslandPolyNBMin=5, FitCones=false, Straighten=true}, PipesCutter=true, HandleCutter=true}})",
			"U3dSelect({PrimType='Edge', Select=true, ResetBefore=true, WorkingSetPrimType='Island', ProtectMapName='Protect', FilterIslandVisible=true, Auto={SharpEdges={AngleMin=" + str(
				bpy.context.scene.sharpestAngle) + "}, PipesCutter=true, HandleCutter=true}})"]

	algorithmString = algorithmCMDStrings[(int(self.autoSeamAlgorithm))]

def set_mosaicForce(value):
	bpy.context.scene.mosaicForce = value

def tgl_manual(self, context):
	if(bpy.context.scene.manualTab == True):
		bpy.context.scene.autoTab = False

def tgl_auto(self, context):
	if (bpy.context.scene.autoTab == True):
		bpy.context.scene.manualTab = False

# ---------------------- Hierarchical Pelt Options -------------------------

def set_hierarchicalOps():
	global hierOPTIONS

	if bpy.context.scene.leaf == True:
		hierOPTIONS.append("U3dSet({Path='Vars.AutoSelect.Hierarchical.Leafs', Value=true})\n")
	if bpy.context.scene.branches == True:
		hierOPTIONS.append("U3dSet({Path='Vars.AutoSelect.Hierarchical.Branches', Value=true})\n")
	if bpy.context.scene.trunk == True:
		hierOPTIONS.append("U3dSet({Path='Vars.AutoSelect.Hierarchical.Trunk', Value=true})\n")
	print(hierOPTIONS)

# ----------------------------- Disto Options ------------------------------

def set_distoControlOps():
	global distoOPTIONS

	if bpy.context.scene.distoControl == True:
		distoOPTIONS.append(
			"U3dSet({Path='Vars.AutoSelect.Bijectiver', Value=true})\nU3dSet({Path='Vars.AutoSelect.BijectiverMinQ', Value=" + str(
				bpy.context.scene.distoControlForce) + "})\n")

# ------------------------------------------- SETTINGS -----------------------------------------------

def B2RizomUV_Settings():

	# region General Settings Properties
	bpy.types.Scene.packQuality = IntProperty \
			(
			name="Packing Quality",
			description="The quality of the packing algorithm. Smaller values are faster to compute but are less precise, whereas larger values are more precise but take longer to compute",
			default=200,
			min=10,
			max=2000
		)

	bpy.types.Scene.optimize = IntProperty \
			(
			name="Interations",
			description="Optimize UV Coordinate for less distortion (Number of iterations for the optimize algorithm)",
			default=1,
			min=1,
			max=750,
		)

	bpy.types.Scene.tFlips = BoolProperty \
			(
			name="T Flips",
			description="When active, RizomUV and Optimize will prevent creation of triangle flips, WARNING: Can increase greatly the computation time.",
			default=False
		)

	bpy.types.Scene.overlaps = BoolProperty \
			(
			name="Overlaps",
			description="When active, RizomUV and Optimize will prevent creation of self border intersections, WARNING: Can increase greatly the computation time.",
			default=False
		)

	bpy.types.Scene.holeFill = BoolProperty \
			(
			name="Fill Holes",
			description="When active, RizomUV and Optimize will fill the mesh's holes with invisible and temporary polygons so that they will prevent the mesh from collapsing in certain scenarios.",
			default=False
		)

	bpy.types.Scene.mapSize = IntProperty \
			(
			name="Map Resolution",
			description="The horizontal resolution of the texture map. It affects Margin and Spacing values if the Units are set to pixel (px)",
			subtype="PIXEL",
			default=1024,
			min=1,
			max=16384
		)

	bpy.types.Scene.spacing = FloatProperty \
			(
			name="Island Spacing",
			description="The space left around each island",
			subtype="FACTOR",
			default=0.002,
			min=0,
			max=0.02
		)

	bpy.types.Scene.margin = FloatProperty \
			(
			name="Margin",
			description="The space on the left/right/top/bottom of the UV tile",
			subtype="FACTOR",
			default=0.005,
			min=0,
			max=0.02
		)

	bpy.types.Scene.modifierApply = BoolProperty \
			(
			name="Modifier Apply",
			description="Applies all modifiers during the bridging process",
			default=False
		)

	# endregion

	#region Algorithm Settings
	bpy.types.Scene.autoSeamAlgorithm = EnumProperty \
			(
			name="Algorithm",
			description="This Auto Seams dropdown contains advanced algorithms to select edges automatically of the visible island set. These edges serve as a good candidate to cut and segment the islands",
			# (identifier, name, description, icon, number)
			items=[('0', "Hierarchical Pelt Algorithm", ''),
			       ('1', "Mosaic Algorithm", ''),
			       ('2', "Sharpest Angles Algorithm", ''),
			       ],
			default='2',
			update=set_algorithm
		)

	bpy.types.Scene.sharpestAngle = IntProperty \
			(
			name="Sharpest Angle",
			description="Edges that have their polygon's normals forming an angle superior to this value will be selected",
			default=60,
			min=1,
			max=180,
			update=set_algorithm
		)

	bpy.types.Scene.mosaicForce = FloatProperty \
			(
			name="Mosaic Force",
			description="High values will segment more so the islands will be unfolded with less distortion. Low values will segment less but the cut will generate more distortion",
			default=0.5,
			min=0.001,
			max=0.999,
			update=set_algorithm
		)

	bpy.types.Scene.leaf = BoolProperty \
			(
			name="Leafs",
			description="Hierarchical segmentation will select the leaf's sections",
			default=False,
			update=set_algorithm
		)

	bpy.types.Scene.branches = BoolProperty \
			(
			name="Branches",
			description="Hierarchical segmentation will select the branch sections",
			update=set_algorithm
		)

	bpy.types.Scene.trunk = BoolProperty \
			(
			name="Trunk",
			description="Hierarchical segmentation will select the trunk's sections",
			default=False,
			update=set_algorithm
		)

	bpy.types.Scene.distoControl = BoolProperty \
			(
			name="Disto Control",
			description="Hierarchical and Mosaic only! Add enough cuts to ensure no flips and no overlaps once the mesh will be unfolded as a post process of Hierarchical and Mosaic",
			default=False,
			update=set_algorithm
		)

	bpy.types.Scene.distoControlForce = FloatProperty \
			(
			name="Disto Control Force",
			description="High values give less distortion but select more edges (more islands count after cut)",
			default=0.5,
			min=0,
			max=0.99,
			update=set_algorithm
		)
	#endregion

	bpy.types.Scene.manualTab = BoolProperty \
			(
			name="Manual",
			description="Send and receive option for manual unwrapping in RizomUV",
			default=True,
			update=tgl_manual
		)

	bpy.types.Scene.autoTab = BoolProperty \
			(
			name="Auto",
			description="Automation options for Blender to RizomUV. Setup respective settings in Blender and have RizomUV execute them automatically",
			default=False,
			update=tgl_auto
		)


# ---------------------------------------- USER INTEFACE --------------------------------------------

class B2RizomUV(bpy.types.Operator):
	"""B2RizomUV Link"""
	bl_idname = "b2rizomuv.link"
	bl_label = "Link"

	def execute(self, context):
		set_hierarchicalOps()
		set_distoControlOps()
		set_settings()
		B2RizomUV_AutoFunction()
		return {'FINISHED'}

class B2RizomUVManuelExport(bpy.types.Operator):
	bl_idname = "b2rizomuvmanual.link"
	bl_label = "Manual Link"

	def execute(self, context):
		B2RizomUV_ManuelExport()
		return {'FINISHED'}

class B2RizomUVManuelImport(bpy.types.Operator):
	bl_idname = "b2rizomuvmanual.sync"
	bl_label = "Manuel Sync"

	def execute(self, context):
		B2RizomUV_ManuelImport()
		return{'FINISHED'}

class MosaicButton(bpy.types.Operator):
	bl_idname = "mosaic.value"
	bl_label = "force"
	mosaicValue = bpy.props.FloatProperty()

	def execute(self, context):
		set_mosaicForce(self.mosaicValue)
		return {'FINISHED'}


class RizomUVMain(bpy.types.Panel):
	"""Creates Main Panel in the Object properties window"""
	bl_label = "RizomUV Main"
	bl_context = "objectmode"
	#bl_idname = "RizomUV_Panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	#bl_category = "RizomUV"

	def draw(self, context):
		layout = self.layout
		scn = bpy.context.scene

		main = layout.row(align=True)
		main.prop(scn, "manualTab", toggle=True)
		main.prop(scn, "autoTab", toggle=True)

		devider = layout.box()

		if(scn.manualTab == True):
			# ---------- SEND BUTTON ------------
			ManualButtonExport = layout.row()
			ManualButtonExport.scale_y = 1.5
			ManualButtonExport.operator(B2RizomUVManuelExport.bl_idname, text="Send", icon="EXPORT")
			ManualButtonExport.scale_y = 1.5
			ManualButtonExport.operator(B2RizomUVManuelImport.bl_idname, text="Get", icon="IMPORT")

			settingsBox = layout.box()
			ModifierButton = settingsBox.row(align=True)
			ModifierButton.prop(scn, "modifierApply", toggle=True)

		if(scn.autoTab == True):
			# ---------- AUTO BUTTON ------------
			Autobutton = layout.row()
			Autobutton.scale_y = 1.2
			Autobutton.operator(B2RizomUV.bl_idname, text="Auto Unfold!", icon='TEXTURE_DATA')

			# -------- SETTINGS WINDOW ----------
			settingsBox = layout.box()
			settingsBox.label("RizomUV Settings")
			algorithmOps = settingsBox.column(True)
			algorithmOps.prop(scn, "autoSeamAlgorithm", icon="EDGESEL")

			if (scn.autoSeamAlgorithm == '0'):
				algorithmBox = settingsBox.box()
				hierarchicalOps = algorithmBox.row(align=True)
				hierarchicalOps.prop(scn, "leaf", toggle=True)
				hierarchicalOps.prop(scn, "branches", toggle=True)
				hierarchicalOps.prop(scn, "trunk", toggle=True)

				distoOps = algorithmBox.row(align=True)
				distoOps.prop(scn, "distoControl", toggle=True)
				if (scn.distoControl == True):
					distoOps.prop(scn, "distoControlForce")

			elif (scn.autoSeamAlgorithm == '1'):
				algorithmBox = settingsBox.box()
				forceButtons = algorithmBox.row(align=True)
				forceButtons.label("Presets")
				forceButtons.operator(MosaicButton.bl_idname, text="1").mosaicValue = 0.25
				forceButtons.operator(MosaicButton.bl_idname, text="2").mosaicValue = 0.5
				forceButtons.operator(MosaicButton.bl_idname, text="3").mosaicValue = 0.75
				forceButtons.operator(MosaicButton.bl_idname, text="4").mosaicValue = 0.95
				algorithmBox.prop(scn, "mosaicForce")

				distoOps = algorithmBox.row(align=True)
				distoOps.prop(scn, "distoControl", toggle=True)
				if (scn.distoControl == True):
					distoOps.prop(scn, "distoControlForce")

			elif (scn.autoSeamAlgorithm == '2'):
				algorithmBox = settingsBox.box()
				algorithmBox.prop(scn, "sharpestAngle")

			gSettingsBox = settingsBox.box()
			gSettingsBox.label("General Settings", icon='SCRIPTWIN')

			iterations = gSettingsBox.row(align=True)
			iterations.prop(scn, "optimize")

			prevents = gSettingsBox.column(True)
			prevents.prop(scn, "tFlips", toggle=True, icon="OUTLINER_DATA_MESH")
			prevents.prop(scn, "overlaps", toggle=True, icon="SNAP_FACE")
			prevents.prop(scn, "holeFill", toggle=True, icon="OUTLINER_DATA_LATTICE")

			textureSettings = gSettingsBox.column(True)
			textureSettings.prop(scn, "packQuality")
			textureSettings.prop(scn, "mapSize")
			textureSettings.prop(scn, "spacing", slider=True)
			textureSettings.prop(scn, "margin", slider=True)

			ModifierButton = settingsBox.row(align=True)
			ModifierButton.prop(scn, "modifierApply", toggle=True)


class RizomUVAddonPreferences(AddonPreferences):
	bl_idname = __name__

	filepath = StringProperty \
			(
			name="RizomUV Executable Path",
			subtype='DIR_PATH',
		)

	def draw(self, context):
		layout = self.layout
		layout.label(text="Set the path to the RizomUV Application")
		layout.prop(self, "filepath")

	# addon_updater_ops.update_settings_ui(self, context)


class OBJECT_OT_addon_prefs(Operator):
	bl_idname = "object.addon_prefs"
	bl_label = "Addon Preferences"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		user_preferences = context.user_preferences
		addon_prefs = user_preferences.addons[__name__].preferences

		info = ("Path: %s" % (addon_prefs.filepath))

		self.report({'INFO'}, info)
		print(info)

		return {'FINISHED'}

classes = (
	B2RizomUV,
	B2RizomUVManuelExport,
	B2RizomUVManuelImport,
	MosaicButton,
	RizomUVMain,
	RizomUVAddonPreferences,
	OBJECT_OT_addon_prefs	
	)

def register():
	# addon_updater_ops.register(bl_info)
	for cla in classes:
		bpy.utils.register_class(cla)
	B2RizomUV_Settings()

def unregister():
	for cla in classes:
		bpy.utils.unregister_class(cla)


if __name__ == "__main__":
	register()
