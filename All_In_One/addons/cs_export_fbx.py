# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
	"name": "Export FBX",
	"author": "Cenek Strichel",
	"version": (1, 0, 8),
	"blender": (2, 79, 0),
	"location": "Export settings in Scene Properties, Export button in Header View3D",
	"description": "Export selected objects to destination (FBX) with override per object",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}
	

import bpy
from shutil import copyfile
from bpy.props import IntProperty, BoolProperty, FloatProperty, StringProperty, EnumProperty


class StringsGroup(bpy.types.PropertyGroup):
	
	bpy.types.Scene.Simplify = FloatProperty(
	name = "Simplify",
	default = 0.1,
	soft_min = 0.0,
	description = "How simplify baked animation\n0 is disabled")
	
	
	AnimationTypeEnum = [
		("NLA", "NLA Strips", "", "", 0),
	    ("Baked", "Baked", "", "", 100),
		("Disabled", "Disabled", "", "", 200)
	    ]
	
	bpy.types.Scene.NLAExport = EnumProperty( 
	name = "Animation", 
	description = "", 
	items = AnimationTypeEnum )

	bpy.types.Scene.ExportPath = StringProperty(
	name = "Export",
	default = "",
	subtype = "FILE_PATH",
	description = "Export path\nE:\\model.fbx")
	
	bpy.types.Scene.Backup = BoolProperty( 
	name = "Backup", 
	default = False, 
	description = "Optional\nEnable copy exported file to file")
	
	bpy.types.Scene.BackupPath = StringProperty( 
	name = "Backup Path", 
	default = "", 
	subtype = "FILE_PATH", 
	description = "Optional\nCopy exported file to file")
	
	bpy.types.Scene.Blacklist = StringProperty( 
	name = "", 
	default = "colliderBake.",
	description = "Optional\nYou can deselect objects with prefix")


	bpy.types.Object.ExportOverride = BoolProperty( 
	name = "Override", 
	default = False, 
	description = "Export override for object")
	
	
	bpy.types.Object.ExportPathOverride = StringProperty(
	name = "Export Path Override",
	default = "",
	subtype = "FILE_PATH",
	description = "Export path\nE:\\model_object.fbx")
	
	bpy.types.Object.NLAExportOverride = EnumProperty( 
	name = "Animation", 
	description = "", 
	items = AnimationTypeEnum )
	
	#
	'''
	FormatTypeEnum = [
		("FBX", "FBX", "", "", 0),
	    ("Blend", "Blend", "", "", 100)
	    ]
	
	bpy.types.Scene.ExportFormat = EnumProperty( 
	name = "Export Format", 
	description = "", 
	items = FormatTypeEnum )
	'''
	
	
class ExportToPlacePanel(bpy.types.Panel):
	
	bl_label = "Export Settings"
	bl_idname = "EXPORT_PANEL"
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	
	
	def draw(self, context):
		
		scn = context.scene
		layout = self.layout
		row = layout.row(align=True)

		# only first override is used
		override = False
		
		for obj in bpy.context.selected_objects:
			if( obj.ExportOverride ):
				override = True
				break
		
		#	
		
		'''
		box = layout.box()
		box.label("Format")
		box.prop( scn, "ExportFormat" )
		'''
		
		# Settings
		box = layout.box()
		box.label("Settings")
		box.prop( scn, "Simplify" )
		
		if( override ):
			box.label( "Animation Override: " + obj.NLAExportOverride )
		else:
			box.prop( scn, "NLAExport" )
			
		'''
		if(scn.ExportFormat == 'Blend'):
			box.enabled = False
		'''
			
		box = layout.box()	
		box.label("Blacklist")
		box.prop( scn, "Blacklist" )	

		# Export
		box = layout.box()
		
		
		if( override ):		
			box.label("Export Override")
			box.label( obj.ExportPathOverride )
	
		else:
			box.label("Export Paths")
			box.prop( scn, "ExportPath", text = "" )

			# Backup
			box.prop( scn, "Backup" )

			if(scn.Backup):
				box.prop( scn, "BackupPath", text = ""  )

		# Export button
		row = layout.row(align=True)
		row.scale_y = 2
		row.operator("cenda.export_to_place", text = "Export", icon="EXPORT" )


class ExportToPlaceObjectPanel(bpy.types.Panel):
	
	bl_label = "Export Selected Override"
	bl_idname = "EXPORT_PANEL_OVERRIDE"
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"
	
	
	def draw(self, context):
		
		scn = context.scene
		layout = self.layout
		row = layout.row(align=True)

		# Settings
		box = layout.box()
		
		box.prop( context.object, "ExportOverride" )
		
		if(bpy.context.object.ExportOverride):
			box.prop( context.object, "ExportPathOverride" )
			box.prop( context.object, "NLAExportOverride" )

		
# export button	
class ExportToPlace(bpy.types.Operator):
	
	
	"""Export selected FBX"""
	bl_idname = "cenda.export_to_place"
	bl_label = "Export to Place"


	def execute(self, context ):
		
		scn = context.scene
		exportPath = scn.ExportPath
		
		# right extension
	#	if(scn.ExportFormat == 'FBX'):
		extension = ".fbx"
		'''	
		else:
			extension = ".blend"	
		'''	
		overrideActive = False
		animExportSettings = context.scene.NLAExport
		
		# Override export object
		for obj in bpy.context.selected_objects:
			if( obj.ExportOverride ):
				if( not obj.ExportPathOverride.endswith (extension) and not obj.ExportPathOverride.endswith(str.upper(extension)) ):
					obj.ExportPathOverride += extension # save to settings

				exportPath = obj.ExportPathOverride # BUG, blend is not added
				animExportSettings = obj.NLAExportOverride
				
				overrideActive = True
				break
			
		# deselect all blacklisted
		if(len(context.scene.Blacklist) > 0):
			for ob in bpy.data.objects:
				if(ob.name.startswith( context.scene.Blacklist )):
					ob.select = False
				
		# check if something is selected
		if( len(context.selected_objects) == 0):
			self.report({'ERROR'}, ("No objects selected") )
			return{'FINISHED'}
		
		# check if path is setted
		if( exportPath == "" ):
			self.report({'ERROR'}, ("Export path is not setted") )
			return{'FINISHED'}

		# check extension
		if( not exportPath.endswith (extension) and not exportPath.endswith (str.upper(extension)) ):
			scn.ExportPath += extension # save to settings
			exportPath = scn.ExportPath # BUG, blend is not added
	
		# convert relative path to absolute
		exportPath = bpy.path.abspath( exportPath ) 
		
		
		# animation baked
		if( animExportSettings == "Baked" ):
			bakedAnimation = True
			nlaStrips = False
			
		elif( animExportSettings == "NLA" ):
			bakedAnimation = True
			nlaStrips = True
			
		elif( animExportSettings == "Disabled" ):
			bakedAnimation = False
			nlaStrips = False
		
		# Export #		
		if(len(exportPath) > 0):
			
			# FBX # export
			if(extension == ".fbx"):
				bpy.ops.export_scene.fbx(

				filepath = exportPath,
				check_existing = True,
				axis_forward = '-Z',
				axis_up = 'Y',
			#	version = 'BIN7400',

				use_selection = True,
				global_scale = 1.0,
				apply_unit_scale = False,
				bake_space_transform = False,
				apply_scale_options = 'FBX_SCALE_ALL',
				
				object_types = {'MESH', 'OTHER', 'EMPTY', 'CAMERA', 'LAMP', 'ARMATURE'},
				use_mesh_modifiers = True,
				use_mesh_modifiers_render = False,
				mesh_smooth_type = 'OFF',

				use_mesh_edges = False,
				use_tspace = False,
				use_custom_props = False,
				add_leaf_bones = False,
				primary_bone_axis = 'Y',
				secondary_bone_axis = 'X',
				use_armature_deform_only = True,
				armature_nodetype = 'NULL',

				bake_anim = bakedAnimation, # changing this
				bake_anim_use_all_bones = True,
				bake_anim_use_nla_strips = nlaStrips, # changing this
				bake_anim_use_all_actions = False,
				bake_anim_force_startend_keying = True,
				bake_anim_step = 1.0,
				bake_anim_simplify_factor = context.scene.Simplify,

			#	use_anim = True,
			#	use_anim_action_all = True,
			#	use_default_take = True,
			#	use_anim_optimize = True,
			#	anim_optimize_precision = 6.0,
			
				path_mode = 'AUTO',
				embed_textures = False,
				batch_mode = 'OFF',
				use_batch_own_dir = True
				)
				
			# Blend # export	
			elif(extension == ".blend"):
				try:
					bpy.ops.export_scene.selected(
					filepath= exportPath, 
					exporter='BLEND',
					exporter_index=0, 
					use_convert_mesh=False, 
					exporter_str="BLEND", 
					use_convert_dupli=False, 
					filter_glob="*.blend", 
					filename_ext=".blend", 
					use_file_browser=True
					)
					
				except:
					self.report({'ERROR'}, ("You need install Export Selected add-on!") )
					return{'FINISHED'}
			
		else:
			self.report({'ERROR'}, ("No export path found") )
			return{'FINISHED'}
		
		
		# BACKUP #
		if( scn.Backup and not overrideActive ):

			backupPath = scn.BackupPath
			
			# make backup
			if( backupPath == "" ):
				self.report({'ERROR'}, ("FBX backup path is not setted") )
				return{'FINISHED'}
	
			# check fbx
			if( not backupPath.endswith ( extension ) and not backupPath.endswith ( str.upper(extension) ) ):
				scn.BackupPath += extension
				backupPath += extension
				
			# convert relative path to absolute	
			backupPath = bpy.path.abspath( backupPath )
			
			# duplicate exported FBX	
			copyfile(exportPath, backupPath)
			
			self.report({'INFO'}, ("Exported to " + exportPath + " | Backup to " + backupPath) )
			
		else:
			self.report({'INFO'}, ("Exported to " + exportPath) )
			
		return{'FINISHED'} 


def ExportLayout(self, context):

	space = bpy.context.space_data
		
	# Normal view
	if(space.region_3d.view_perspective != 'CAMERA'): # only for camera
		
		# export
		layout = self.layout
		row = layout.row(align=True)
		
		if(bpy.context.active_object.mode  == 'OBJECT'):
			row.enabled = True
		else:
			row.enabled = False
			
		# only first override is used
		textExport = context.scene.ExportPath.rsplit('\\', 1)[-1]
		
		for obj in bpy.context.selected_objects:
			if( obj.ExportOverride ):
				textExport = "[ " + context.object.ExportPathOverride.rsplit('\\', 1)[-1] + " ]"
				break
			
		if(len(textExport) > 0):
			row.operator("cenda.export_to_place", icon = "EXPORT", text = textExport)

		
		
################################################################
# register #
############
def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_HT_header.prepend(ExportLayout)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_HT_header(ExportLayout)
	
if __name__ == "__main__":
	register()