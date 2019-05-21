# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	"name": "Id Tech 4 md5mesh and md5anim format",
	"author": "pink vertex",
	"version": (0, 1),
	"blender": (2, 77, 0),
	"location": "File -> Import-Export",
	"description": "Import-Export *.md5mesh and *.md5anim files",
	"warning": "",
	"wiki_url": "",
	"category": "Import-Export",
	}

if "bpy" in locals():
	import sys
	import importlib
	importlib.reload(sys.modules['io_md5.io_md5mesh'])
	importlib.reload(sys.modules['io_md5.io_md5anim'])
	importlib.reload(sys.modules['io_md5.import_hudguns'])

import os
import bpy
from bpy.props import StringProperty, IntProperty, FloatProperty, EnumProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

from .io_md5mesh import read_md5mesh, write_md5mesh
from .io_md5anim import read_md5anim, write_md5anim
from .import_hudguns import setup_cam, import_from_config

class MD5Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__
	sb_dir = StringProperty(name="Sauerbraten Directory", default="", subtype="DIR_PATH")

	def draw(self, context):
		self.layout.prop(self, "sb_dir")

class OT_IMPORT_MESH_md5mesh(bpy.types.Operator, ImportHelper):
	bl_idname = "import_mesh.md5"
	bl_label = "Import *.md5mesh Mesh"
	bl_options = {"REGISTER", "UNDO"}

	filename_ext = ".md5mesh"
	filter_glob = StringProperty(default="*.md5mesh", options={'HIDDEN'})

	def execute(self, context):
		read_md5mesh(self.filepath)
		return {"FINISHED"}


class OT_EXPORT_MESH_md5mesh(bpy.types.Operator, ExportHelper):
	bl_idname = "export_mesh.md5"
	bl_label = "Export *.md5mesh Mesh"
	bl_options = {"REGISTER", "UNDO"}

	filename_ext = ".md5mesh"
	filter_glob = StringProperty(default="*.md5mesh", options={'HIDDEN'})

	@classmethod
	def poll(cls, context):
		return (context.active_object and
				context.active_object.type == "ARMATURE")

	def execute(self, context):
		write_md5mesh(self.filepath, context.scene, context.active_object)
		return {"FINISHED"}

class OT_IMPORT_ANIM_md5anim(bpy.types.Operator, ImportHelper):
	bl_idname = "import_anim.md5"
	bl_label = "Import *.md5anim Animation"
	bl_options = {'REGISTER', "UNDO"}

	filename_ext = ".md5anim"
	filter_glob = StringProperty(default="*.md5anim", options={'HIDDEN'})

	@classmethod
	def poll(cls, context):
		return (context.active_object and
				context.active_object.type == "ARMATURE")

	def execute(self, context):
		bpy.ops.object.mode_set(mode="OBJECT")
		read_md5anim(self.filepath)
		return {'FINISHED'}

class OT_EXPORT_ANIM_md5anim(bpy.types.Operator, ExportHelper):
	bl_idname = "export_anim.md5"
	bl_label = "Export *.md5anim Anim"
	bl_options = {"REGISTER", "UNDO"}

	filename_ext = ".md5anim"
	filter_glob = StringProperty(default="*.md5anim", options={'HIDDEN'})
	bone_layer = IntProperty(name="BoneLayer", default=0)

	@classmethod
	def poll(cls, context):
		return (context.active_object and
			    context.active_object.type == "ARMATURE" and
				context.active_object.animation_data and
				context.active_object.animation_data.action)

	def execute(self, context):
		write_md5anim(self.filepath, context.scene, context.active_object, self.bone_layer)
		return {"FINISHED"}


class OT_IMPORT_MESH_sb_hudgun(bpy.types.Operator, ImportHelper):
	bl_idname = "import_mesh.sb_hudgun"
	bl_label = "Import Sauerbraten Hudgun"
	bl_options = {"REGISTER", "UNDO"}

	filename_ext = ".cfg"
	filter_glob = StringProperty(default="*.cfg", options={'HIDDEN'})
	playermodel = EnumProperty(items=(
		("MRFIXIT",       "Mr Fixit",      "", 0),
		("SNOUTX10K",     "SnoutX10K",     "", 1),
		("INKY",          "Inky",          "", 2),
		("CAPTAINCANNON", "CaptainCannon", "", 3)),
		name="Playermodel",
		default="SNOUTX10K"
	)

	weapon = EnumProperty(items=(
		("SHOTG",  "Shotgun",         "", 1),
		("CHAING", "Chaingun",        "", 2),
		("ROCKET", "Rocketlauncher",  "", 3),
		("RIFLE",  "Rifle",           "", 4),
		("GL",     "Grenadelauncher", "", 5),
		("PISTOL", "Pistol",          "", 6)),
		name="Weapon",
		default="RIFLE"
	)

	fov = FloatProperty(name="Field Of View", default=65.0, subtype="NONE")
	res_x = IntProperty(name="Window Width",  default=800,  subtype="PIXEL")
	res_y = IntProperty(name="Window Height", default=600,  subtype="PIXEL")
	directory = StringProperty(name="Directory", subtype="DIR_PATH",  description="Directory of the file")
	filename  = StringProperty(name="Filename",  subtype="FILE_NAME", description="Name of the file", default="", options={'SKIP_SAVE', 'TEXTEDIT_UPDATE'})
	# filesel = CollectionProperty(name="Files", type=bpy.types.OperatorFileListElement)

	def execute(self, context):
		pref = context.user_preferences.addons[__name__].preferences

		if self.filename == "":
			if pref.sb_dir == "":
				pref.sb_dir = self.directory
			self.filepath = os.path.join(
				pref.sb_dir, "packages", "models",
				self.playermodel.lower(), "hudguns", self.weapon.lower(), "md5.cfg")

		setup_cam(context.scene, self.fov, self.res_x, self.res_y)
		import_from_config(pref.sb_dir, self.filepath, self.weapon.lower())
		context.scene.update()
		context.scene.frame_set(0)
		return {"FINISHED"}

	def draw(self, context):
		pref = context.user_preferences.addons[__name__].preferences
		layout = self.layout
		if not context.space_data.params.filename == "":
			layout.label(text="File selected - Dropdown will be ignored", icon="QUESTION")
			enabled = False
		else:
			enabled = True
		col = layout.column()
		col.enabled = enabled
		col.prop(self, "playermodel")
		col.prop(self, "weapon")
		layout.prop(self, "fov")
		layout.prop(self, "res_x")
		layout.prop(self, "res_y")
		layout.prop(pref, "sb_dir")

reg_table = (
	[OT_IMPORT_MESH_md5mesh,   bpy.types.INFO_MT_file_import, "MD5 Mesh (.md5mesh)"	   ],
	[OT_IMPORT_ANIM_md5anim,   bpy.types.INFO_MT_file_import, "MD5 Animation (.md5anim)"],
	[OT_EXPORT_MESH_md5mesh,   bpy.types.INFO_MT_file_export, "MD5 Mesh (.md5mesh)"     ],
	[OT_EXPORT_ANIM_md5anim,   bpy.types.INFO_MT_file_export, "MD5 Animation (.md5anim)"],
	[OT_IMPORT_MESH_sb_hudgun, bpy.types.INFO_MT_file_import, "Sauerbraten Hudgun (.cfg)"]
)

def generate_menu_function(op_cls, description):
	def mnu_func(self, context):
		self.layout.operator(op_cls.bl_idname, text=description)
	return mnu_func

for row in reg_table:
	row[2] = generate_menu_function(row[0], row[2])

def register():
	bpy.utils.register_class(MD5Preferences)
	for cls, mnu, mnu_func in reg_table:
		bpy.utils.register_class(cls)
		mnu.append(mnu_func)

def unregister():
	bpy.utils.unregister_class(MD5Preferences)
	for cls, mnu, mnu_func in reg_table:
		mnu.remove(mnu_func)
		bpy.utils.unregister_class(cls)
