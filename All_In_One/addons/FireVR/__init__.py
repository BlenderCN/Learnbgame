bl_info = {
	"name" : "FireVR",
	"author" : "void",
	"version" : (0, 1),
	"blender" : (2, 75, 0),
	"location" : "View3D > Toolshelf > Misc",
	"description": "Exports the scene into FireBox HTML and publishes it to IPFS",
	"wiki_url" : "https://github.com/void4/FireVR",
	"category" : "Import-Export"
}

import importlib

if "bpy" in locals():
	if "ipfsvr_export" in locals():
		importlib.reload(ipfsvr_export)

import os
import time
import subprocess

import sys

_modules_path = os.path.join(os.path.dirname(__file__), "modules")
if not _modules_path in sys.path:
    sys.path.append(_modules_path)

from bpy.types import (
	Operator,
	Panel,
	AddonPreferences,
	RenderEngine,
	Scene,
	Object
	)

from bpy.props import (
	StringProperty,
	BoolProperty,
	EnumProperty,
	FloatProperty,
	FloatVectorProperty,
	IntProperty,
	IntVectorProperty
	)

from bpy_extras.io_utils import (
	ExportHelper
	)

import bpy

import bpy.utils.previews

from . import vr_export, vr_import

Scene.roomhash = StringProperty(name="", default="")

class ToolPanel(Panel):
	bl_label = "Firebox"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):
		self.layout.operator("fire.html", icon_value=custom_icons["custom_icon"].icon_id)
		if context.scene.roomhash:
			self.layout.prop(context.scene, "roomhash")
		# The licence of my contributions is public domain, too,
		# but I would prefer if this note stuck around.
		# Including the "Who needs sleep?" bit. - 20kdc, who needs sleep. (It's 2AM.)
		self.layout.label("Warning: Export may apply transforms.")
		self.layout.label("Save before usage. Who needs sleep?")
		self.layout.operator("export_scene.html")

Scene.janus_ipfs = BoolProperty(name="Use IPFS", default=False)
Scene.janus_gateway = BoolProperty(name="IPFS Gateway", default=False)
Scene.janus_ipns = BoolProperty(name="IPNS", default=False)
Scene.janus_ipnsname = StringProperty(name="", default="myroom")

Scene.janus_apply_rot = BoolProperty(name="Apply Rotation", default=False)
Scene.janus_apply_scale = BoolProperty(name="Apply Scale", default=False)
Scene.janus_apply_pos = BoolProperty(name="Apply Position", default=False)
Scene.janus_unpack = BoolProperty(name="Unpack Textures", default=True)

class ExportSettingsPanel(Panel):
	bl_label = "Export Settings"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):
		self.layout.operator("export_path.html")
		self.layout.prop(context.scene, "janus_ipfs")
		if context.scene.janus_ipfs:
			self.layout.prop(context.scene, "janus_gateway")
			self.layout.prop(context.scene, "janus_ipns")
		if context.scene.janus_ipns:
			self.layout.prop(context.scene, "janus_ipnsname")
		self.layout.prop(context.scene, "janus_apply_rot")
		self.layout.prop(context.scene, "janus_apply_scale")
		self.layout.prop(context.scene, "janus_apply_pos")
		self.layout.prop(context.scene, "janus_unpack")

Scene.janus_importpath = StringProperty(name="importpath", description="Specify the html page that includes the FireBoxHTML source", subtype="FILE_PATH", default="http://vesta.janusvr.com/kityandtom/freedome")

class ImportSettingsPanel(Panel):
	bl_label = "Import Settings"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):
		self.layout.operator("import_scene.html")
		col = self.layout.column()
		col.prop(context.scene, "janus_importpath")

Scene.janus_rendermode = EnumProperty(name="", default="2d", items=(("2d", "2D", "2D"),("sbs","Side by Side", "Side by Side"),("sbs_reverse", "Side by Side Reverse", "Side by Side Reverse"),("rift", "Rift", "Rift")))
Scene.janus_fullscreen = BoolProperty(name="JanusVR Fullscreen", default=True)
Scene.janus_size = IntVectorProperty(name="", size=2, default=(640, 480), min=1, max=10000)
Scene.janus_updaterate = IntProperty(name="Rate", default=100, min=1, max=5000)

class RunSettingsPanel(Panel):
	bl_label = "Run Settings"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):
		self.layout.operator("set_path.janus")
		self.layout.prop(context.scene, "janus_rendermode")
		self.layout.prop(context.scene, "janus_updaterate")
		self.layout.prop(context.scene, "janus_fullscreen")
		if not context.scene.janus_fullscreen:
			self.layout.label("Window size")
			self.layout.prop(context.scene, "janus_size")

Scene.janus_object_export = EnumProperty(name="", default=".obj", items=((".obj", "Wavefront (.obj)", "Wavefront object files"),(".dae", "Collada (.dae)", "Collada files")))
Object.janus_object_jsid = StringProperty(name="js_id", default="")
Object.janus_object_objtype = EnumProperty(name="", default="JOT_OBJECT", items=(("JOT_NONE", "No Export", "Don't export this object."), ("JOT_OBJECT", "Object (model)", "<Object>"), ("JOT_LINK", "Link (portal)", "<Link>")))
Object.janus_object_link_name = StringProperty(name="Link Name", default="")
Object.janus_object_link_url = StringProperty(name="Link URL", default="")
Object.janus_object_active = BoolProperty(name="Active", default=True)
Object.janus_object_collision = BoolProperty(name="Collision", default=True)
Object.janus_object_locked = BoolProperty(name="Locked", default=False)
Object.janus_object_lighting = BoolProperty(name="Lighting", default=True)
Object.janus_object_visible = BoolProperty(name="Visible", default=True)
Object.janus_object_color_active = BoolProperty(name="Set Color", default=False)
Object.janus_object_color = FloatVectorProperty(name="Color", default=(1.0,1.0,1.0), subtype="COLOR", size=3, min=0.0, max=1.0)
Object.janus_object_websurface = BoolProperty(name="Websurface", default=False)
Object.janus_object_websurface_url = StringProperty(name="URL", default="")
Object.janus_object_websurface_size = IntVectorProperty(name="", size=2, default=(1920, 1080), min=1, max=10000)
Object.janus_object_cullface = EnumProperty(name="", default="back", items=tuple(tuple([e,e,e]) for e in ["back", "front", "none"]))
Object.janus_object_shader_active = BoolProperty(name="GLSL Shader", default=False)
Object.janus_object_shader_frag = StringProperty(name="Frag Shader", subtype="FILE_PATH")
Object.janus_object_shader_vert = StringProperty(name="Vertex Shader", subtype="FILE_PATH")

Object.janus_object_sound = StringProperty(name="Sound", subtype="FILE_PATH", default="")
Object.janus_object_sound_dist = FloatProperty(name="Distance", default=1)
Object.janus_object_sound_xy1 = FloatVectorProperty(name="", size=2, default=(0, 0), min=-10000, max=10000)
Object.janus_object_sound_xy2 = FloatVectorProperty(name="", size=2, default=(0, 0), min=-10000, max=10000)
Object.janus_object_sound_loop = BoolProperty(name="Loop", default=False)
Object.janus_object_sound_once = BoolProperty(name="Play once", default=False)

class ObjectPanel(Panel):
	bl_label = "Objects"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):

		if context.object.type == "MESH":
			self.layout.prop(context.object, "janus_object_objtype")
			if context.object.janus_object_objtype != "JOT_NONE":
				self.layout.prop(context.object, "janus_object_jsid")
			if context.object.janus_object_objtype == "JOT_OBJECT":
				self.layout.prop(context.scene, "janus_object_export")
				self.layout.prop(context.object, "janus_object_collision")
				self.layout.prop(context.object, "janus_object_locked")
				self.layout.prop(context.object, "janus_object_lighting")
				self.layout.prop(context.object, "janus_object_visible")
				if context.object.janus_object_visible:
					self.layout.prop(context.object, "janus_object_color_active")
					if context.object.janus_object_color_active:
						self.layout.prop(context.object, "janus_object_color")

				self.layout.prop(context.object, "janus_object_websurface")
				if context.object.janus_object_websurface:
					self.layout.prop(context.object, "janus_object_websurface_url")
					self.layout.label("Width & Height")
					self.layout.prop(context.object, "janus_object_websurface_size")

				self.layout.label("Cull Face")
				self.layout.prop(context.object, "janus_object_cullface")

				self.layout.prop(context.object, "janus_object_shader_active")
				if context.object.janus_object_shader_active:
					self.layout.prop(context.object, "janus_object_shader_frag")
					self.layout.prop(context.object, "janus_object_shader_vert")
			elif context.object.janus_object_objtype == "JOT_LINK":
				self.layout.label("Use a standard plane,")
				self.layout.label(" and adjust the transform.")
				self.layout.label("(Don't edit the mesh itself)")
				self.layout.prop(context.object, "janus_object_link_name")
				self.layout.prop(context.object, "janus_object_link_url")
				self.layout.prop(context.object, "janus_object_active")

		elif context.object.type=="SPEAKER":
			self.layout.prop(context.object, "janus_object_sound")
			self.layout.prop(context.object, "janus_object_jsid")
			self.layout.prop(context.object, "janus_object_sound_dist")
			self.layout.label("XY1")
			self.layout.prop(context.object, "janus_object_sound_xy1")
			self.layout.label("XY2")
			self.layout.prop(context.object, "janus_object_sound_xy2")

			self.layout.prop(context.object, "janus_object_sound_loop")
			self.layout.prop(context.object, "janus_object_sound_once")

rooms = ["room_plane", "None", "room1", "room2", "room3", "room4", "room5", "room6", "room_1pedestal", "room_2pedestal", "room_3_narrow", "room_3_wide", "room_4_narrow", "room_4_wide", "room_box_small", "room_box_medium", "room1_new"]
roomlist = tuple(tuple([room, room, room]) for room in rooms)
Scene.janus_room = EnumProperty(name="", default="room_plane", items=roomlist)
Scene.janus_room_color = FloatVectorProperty(name="Color", default=(1.0,1.0,1.0), subtype="COLOR", size=3, min=0.0, max=1.0)
Scene.janus_room_visible = BoolProperty(name="Visible", default=False)

Scene.janus_room_skybox_active = BoolProperty(name="Select Skybox Images", default=False)
Scene.janus_room_skybox_left = StringProperty(name="Skybox Left", subtype="FILE_PATH")
Scene.janus_room_skybox_right = StringProperty(name="Skybox Right", subtype="FILE_PATH")
Scene.janus_room_skybox_front = StringProperty(name="Skybox Front", subtype="FILE_PATH")
Scene.janus_room_skybox_back = StringProperty(name="Skybox Back", subtype="FILE_PATH")
Scene.janus_room_skybox_up = StringProperty(name="Skybox Up", subtype="FILE_PATH")
Scene.janus_room_skybox_down = StringProperty(name="Skybox Down", subtype="FILE_PATH")

Scene.janus_room_gravity = FloatProperty(name="Gravity", default=-9.8, min=-100, max=100)
Scene.janus_room_walkspeed = FloatProperty(name="Walk Speed", default=1.8, min=-100, max=100)
Scene.janus_room_runspeed = FloatProperty(name="Run Speed", default=5.4, min=-100, max=100)

Scene.janus_room_jump = FloatProperty(name="Jump Velocity", default=5, min=-100, max=100)
Scene.janus_room_clipplane = FloatVectorProperty(name="", default=(0.0025,500.0), size=2, min=0.0, max=100000.0)
Scene.janus_room_teleport = FloatVectorProperty(name="", default=(5.0,100.0), size=2, min=0.0, max=100000.0)

Scene.janus_room_defaultsounds = BoolProperty(name="Default Sounds", default=True)
Scene.janus_room_cursorvisible = BoolProperty(name="Show cursor", default=True)

Scene.janus_room_fog = BoolProperty(name="Fog", default=False)
Scene.janus_room_fog_mode = EnumProperty(name="", default="exp", items=tuple(tuple([e,e,e]) for e in ["exp", "exp2", "linear"]))

Scene.janus_room_fog_density = FloatProperty(name="Density", default=0.2, min=0.0, max=1000.0)
Scene.janus_room_fog_start = FloatProperty(name="Start", default=1.0, min=0.0, max=100000.0)
Scene.janus_room_fog_end = FloatProperty(name="End", default=100.0, min=0.0, max=100000.0)
Scene.janus_room_fog_col = FloatVectorProperty(name="Color", default=(0.8,0.8,0.8), subtype="COLOR", size=3, min=0.0, max=1.0)

Scene.janus_room_script_active = BoolProperty(name="Asset Scripts", default=False)
Scene.janus_room_script1 = StringProperty(name="Script 1", subtype="FILE_PATH")
Scene.janus_room_script2 = StringProperty(name="Script 2", subtype="FILE_PATH")
Scene.janus_room_script3 = StringProperty(name="Script 3", subtype="FILE_PATH")
Scene.janus_room_script4 = StringProperty(name="Script 4", subtype="FILE_PATH")

Scene.janus_room_shader_active = BoolProperty(name="Global GLSL Shader", default=False)
Scene.janus_room_shader_frag = StringProperty(name="Frag Shader", subtype="FILE_PATH")
Scene.janus_room_shader_vert = StringProperty(name="Vertex Shader", subtype="FILE_PATH")

Scene.janus_room_locked = BoolProperty(name="Lock Room", default=False)

class RoomPanel(Panel):
	bl_label = "Room"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):
		self.layout.prop(context.scene, "janus_room")

		if context.scene.janus_room!="None":
			self.layout.prop(context.scene, "janus_room_visible")
			if context.scene.janus_room_visible:
				self.layout.prop(context.scene, "janus_room_color")

		self.layout.prop(context.scene, "janus_room_skybox_active")
		if context.scene.janus_room_skybox_active:
			self.layout.prop(context.scene, "janus_room_skybox_left")
			self.layout.prop(context.scene, "janus_room_skybox_right")
			self.layout.prop(context.scene, "janus_room_skybox_front")
			self.layout.prop(context.scene, "janus_room_skybox_back")
			self.layout.prop(context.scene, "janus_room_skybox_up")
			self.layout.prop(context.scene, "janus_room_skybox_down")

		self.layout.prop(context.scene, "janus_room_gravity")
		self.layout.prop(context.scene, "janus_room_walkspeed")
		self.layout.prop(context.scene, "janus_room_runspeed")

		self.layout.prop(context.scene, "janus_room_jump")
		self.layout.label("Clip Plane")
		self.layout.prop(context.scene, "janus_room_clipplane")

		self.layout.label("Teleport Range")
		self.layout.prop(context.scene, "janus_room_teleport")

		self.layout.prop(context.scene, "janus_room_defaultsounds")
		self.layout.prop(context.scene, "janus_room_cursorvisible")

		self.layout.prop(context.scene, "janus_room_fog")
		if context.scene.janus_room_fog:
				self.layout.prop(context.scene, "janus_room_fog_col")
				self.layout.prop(context.scene, "janus_room_fog_mode")
				if context.scene.janus_room_fog_mode in ["exp", "exp2"]:
						self.layout.prop(context.scene, "janus_room_fog_density")
				elif context.scene.janus_room_fog_mode == "linear":
						self.layout.prop(context.scene, "janus_room_fog_start")
						self.layout.prop(context.scene, "janus_room_fog_end")

		self.layout.prop(context.scene, "janus_room_script_active")
		if context.scene.janus_room_script_active:
			self.layout.prop(context.scene, "janus_room_script1")
			if context.scene.janus_room_script1:
				self.layout.prop(context.scene, "janus_room_script2")
				if context.scene.janus_room_script2:
					self.layout.prop(context.scene, "janus_room_script3")
					if context.scene.janus_room_script3:
						self.layout.prop(context.scene, "janus_room_script4")

		self.layout.prop(context.scene, "janus_room_shader_active")
		if context.scene.janus_room_shader_active:
			self.layout.prop(context.scene, "janus_room_shader_frag")
			self.layout.prop(context.scene, "janus_room_shader_vert")

		self.layout.prop(context.scene, "janus_room_locked")

Scene.janus_server_default = BoolProperty(name="Default Server", default=True)
Scene.janus_server = StringProperty(name="", default="babylon.vrsites.com")
Scene.janus_server_port = IntProperty(name="Port", default=5567, min=0, max=2**16-1)

class ServerPanel(Panel):
	bl_label = "Multiplayer"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):
		self.layout.prop(context.scene, "janus_server_default")
		if not context.scene.janus_server_default:
			self.layout.prop(context.scene, "janus_server")
			self.layout.prop(context.scene, "janus_server_port")


Scene.janus_debug = BoolProperty(name="JanusVR", default=False)
class DebugPanel(Panel):
	bl_label = "Debug"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):
		self.layout.prop(context.scene, "janus_debug")

class ipfsvr(AddonPreferences):
	bl_idname = __package__

	from os.path import expanduser
	home = expanduser("~")
	filename_ext = ""

	exportpath = StringProperty(name="", subtype="FILE_PATH", default="")
	januspath = StringProperty(name="januspath", subtype="FILE_PATH", default=os.path.join(home,"JanusVRBin/janusvr"))

	def draw(self, context):
		layout = self.layout
		layout.label("VR Preferences")
		#layout.prop(self, exportpath)

def setv(context, name, value):
	context.user_preferences.addons[__name__].preferences[name] = value

def getv(context, name):
	try:
		return context.user_preferences.addons[__name__].preferences[name]
	except KeyError:
		return None

def hasv(context, name):
	try:
		return getv(context, name)
	except KeyError:
		pass

class VRExportPath(Operator, ExportHelper):
	bl_idname = "export_path.html"
	bl_label = "Export path"
	bl_options = {"PRESET", "UNDO"}

	use_filter_folder = True
	filename_ext = ""
	filter_glob = ""

	def execute(self, context):
		keywords = self.as_keywords(ignore=("filter_glob","check_existing"))

		if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
			keywords["relpath"] = os.path.dirname((bpy.data.path_resolve("filepath", False).as_bytes()))

		if os.path.isdir(os.path.dirname(keywords["filepath"])):
			setv(context,"exportpath",os.path.dirname(keywords["filepath"]))
		else:
			self.report({"ERROR"}, "Please select a directory, not a file")

		return {"FINISHED"}

class VRJanusPath(Operator, ExportHelper, AddonPreferences):
	bl_idname = "set_path.janus"
	bl_label = "JanusVR path"
	bl_options = {"PRESET", "UNDO"}

	use_filter = False
	if os.name != "nt":
		filename_ext = ""
		filter_glob = StringProperty(
        default="janusvr",
        options={'HIDDEN'},
        )
	else:
		filename_ext = ".exe"
		filter_glob = StringProperty(
        default="janusvr.exe",
        options={'HIDDEN'},
        )

	def execute(self, context):
		keywords = self.as_keywords(ignore=("filter_glob","check_existing"))

		if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
			keywords["relpath"] = bpy.data.path_resolve("filepath", False).as_bytes()

		if os.path.isfile(keywords["filepath"]):
			setv(context,"januspath", keywords["filepath"])
		else:
			self.report({"ERROR"}, "Please select the JanusVR executable")

		return {"FINISHED"}

class VRImport(Operator):
	bl_idname = "import_scene.html"
	bl_label = "Import FireBoxHTML"
	bl_options = {"PRESET", "UNDO"}

	def execute(self, context):
		#use exportpath/tmp as working path
		exportpath = getv(context, "exportpath")
		if exportpath:
			workingpath = os.path.join(exportpath, "tmp")#time.strftime("%Y%m%d%H%M%S"))
			os.makedirs(workingpath, exist_ok=True)
			importpath = context.scene.janus_importpath
			if importpath:
				vr_import.load(self, context, filepath=importpath, workingpath=workingpath)
				self.report({"INFO"}, "Imported from %s" % importpath)
			else:
				self.report({"ERROR"}, "Invalid import path")
		else:
			self.report({"ERROR"}, "Invalid export (working) path")
		return {"FINISHED"}

class VRExport(Operator):
	bl_idname = "export_scene.html"
	bl_label = "Export FireBoxHTML"
	bl_options = {"PRESET", "UNDO"}

	def execute(self, context):
		exportpath = getv(context, "exportpath")
		if exportpath:
			filepath = os.path.join(exportpath, time.strftime("%Y%m%d%H%M%S"))
			os.makedirs(filepath, exist_ok=True)
			vr_export.save(self, context, filepath=filepath)
			setv(context, "filepath", filepath)
			self.report({"INFO"}, "Exported files to %s" % filepath)
		else:
			self.report({"ERROR"}, "Invalid export path")
		return {"FINISHED"}

def getURL(context, hashes):
	if context.scene.janus_gateway:
		return "http://gateway.ipfs.io/ipfs/"+hashes[-1]+"/index.html"
	else:
		return "localhost:8080/ipfs/"+hashes[-1]+"/index.html"

class VRJanus(Operator):
	bl_idname = "export_scene.vrjanus"
	bl_label = "Start JanusVR"
	bl_options = {"PRESET", "UNDO"}

	def execute(self, context):

		filepath = hasv(context, "filepath")

		if not filepath:
			self.report({"ERROR"}, "Did not export scene.")
			return {"FINISHED"}

		if context.scene.janus_ipfs:
			ipfs.start()

			hashes = ipfs.addRecursive(filepath)

			if not hashes:
				self.report({"ERROR"}, "IPFS Error")
				return {"FINISHED"}

			gateway = getURL(context, hashes)

			context.scene.roomhash = gateway

			self.report({"INFO"}, "Starting JanusVR on %s" % gateway)

		args = []
		if not context.scene.janus_fullscreen:
			args.append("-window")
			args.append("-width")
			args.append(str(context.scene.janus_size[0]))
			args.append("-height")
			args.append(str(context.scene.janus_size[1]))

		args += ["render", context.scene.janus_rendermode]
		args += ["rate", str(context.scene.janus_updaterate)]

		if not context.scene.janus_ipfs:
			filepath = os.path.join(filepath, "index.html")

		januspath = hasv(context, "januspath")
		if januspath:
			params = {}
			if not context.scene.janus_debug:
				params = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
			if context.scene.janus_ipfs:
				subprocess.Popen([januspath]+args+[gateway], close_fds=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			else:
				subprocess.Popen([januspath]+args+[filepath])
		else:
			self.report({"ERROR"}, "JanusVR path not set")
		return {"FINISHED"}

class VRFire(Operator):
	bl_idname = "fire.html"
	bl_label = "Start JanusVR"
	bl_options = {"PRESET", "UNDO"}

	def execute(self, context):
		bpy.ops.export_scene.html()
		bpy.ops.export_scene.vrjanus()
		return {"FINISHED"}

custom_icons = None

def register():
	global custom_icons
	custom_icons = bpy.utils.previews.new()
	script_path = os.path.realpath(__file__)
	icon_path = os.path.join(os.path.dirname(script_path), "icon.png")
	custom_icons.load("custom_icon", icon_path, "IMAGE")
	bpy.utils.register_module(__name__)
	if getv(bpy.context, "exportpath") is None:
		setv(bpy.context, "exportpath", "jvr")

def unregister():
	global custom_icons
	bpy.utils.previews.remove(custom_icons)
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
