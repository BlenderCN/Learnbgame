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
	"name": "Cache Manager",
	"category": "Cenda Tools",
	"author": "Cenek Strichel",
	"version": (1, 0, 2),
	"blender": (2, 79, 0),
	"description": "Manager for cache files of physics files",
	"location": "Properties physics panel",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
}


import bpy
import os
import subprocess

from shutil import copyfile
from bpy.props import IntProperty, BoolProperty, FloatProperty, StringProperty, EnumProperty


class CacheDeletePanel(bpy.types.Panel):
	
	"""Cache Manager Panel"""
	bl_label = "Cache Manager"
	bl_idname = "CACHEMANAGER_PT_layout"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "physics"
	
	bpy.types.Object.CacheDeleteFile = StringProperty( 
	name = "Cache File", 
	default = "",
	description = "Cache file")
	
	def draw(self, context):
		
		layout = self.layout
		
		obj = context.object
		scn = context.scene
		domainFound = False
		
		for modifier in obj.modifiers:
			if modifier.type == 'SMOKE':
					
				domainFound = True
				
				# cache file name
				row = layout.row(align=True)
			#	row = row.box()
				
				row.scale_y = 2
				row.operator("view3d.play_stop_end", text = "Play Once (any key to Stop)", icon = "PLAY") # Play stop end
				
			#	row.scale_y = 1				
			#	row.operator("view3d.bake_from_cache", text = "Bake from cache" ) # Play stop end
			
				row = layout.row(align=True)
				row = row.box()
				row.prop( obj, "CacheDeleteFile" ) # Cache File

				# cache file warning
				if(len(context.object.CacheDeleteFile) > 0):
					
					filepath = bpy.data.filepath.split("\\")
					file = filepath[ len(filepath)-1 ].replace(".blend","")
					directory = bpy.data.filepath.replace(filepath[ len(filepath)-1 ], "")
					frame = bpy.context.scene.frame_current 
					
					cachePresent = False
					fileCache = (directory + "blendcache_" + file + "\\" + context.object.CacheDeleteFile + "_" + str(frame).zfill(6) + "_00.bphys" )
					
					if(os.path.isfile( fileCache )):
						cachePresent = True
						
					# +1 because zero is not cached
					fileCache = (directory + "blendcache_" + file + "\\" + context.object.CacheDeleteFile + "_" + str(frame+1).zfill(6) + "_00.bphys" ) 
					
					if(os.path.isfile( fileCache )):
						cachePresent = True
					
					fileCacheInitial = (directory + "blendcache_" + file + "\\" + context.object.CacheDeleteFile + "_initial_state.bphys" )
					
					
					# open folder	
					row.operator("view3d.cache_file_folder_open", text = "Open Cache Folder", icon = "FILE_FOLDER")	# Open Cache Folder button
					
					row = layout.row(align=True)
					
					if( cachePresent ):

						# cache delete button
						row = layout.row(align=True)
						row.operator("view3d.cache_delete_files", text = "Delete Cache", icon = "CANCEL") # Delete Cache button
						
						# initial state
						row = layout.row(align=True)
						row.operator("view3d.save_initial_state", text = "Save Initial State", icon = "COPYDOWN") # Set Initial State button

						if( (os.path.isfile( fileCacheInitial )) ):
							row.operator("view3d.load_initial_state", text = "Load Initial State", icon = "PASTEDOWN") # Set Initial State button	
							
					elif(os.path.isfile( fileCacheInitial )):
						row = layout.row(align=True)
						row.operator("view3d.load_initial_state", text = "Load Initial State", icon = "PASTEDOWN") # Set Initial State button
						
						
		if(domainFound == False):
			row = layout.row(align=True)
			row.label("Select Smoke Object")

'''			
class BakeFromCache(bpy.types.Operator):

	"""Bake from Cache"""
	bl_label = "Bake from Cache"
	bl_idname = "view3d.bake_from_cache"

	def execute(self, context):
		
		a = {}
		a['point_cache'] = bpy.data.objects['Cube'].particle_systems['ParticleSystem'].point_cache
		bpy.ops.ptcache.bake_from_cache(a)

		return {'FINISHED'}
'''	
	
class SaveInitialState(bpy.types.Operator):

	"""Save Initial State"""
	bl_label = "Save Initial State"
	bl_idname = "view3d.save_initial_state"

	def execute(self, context):
		
		filepath = bpy.data.filepath.split("\\")
		file = filepath[ len(filepath)-1 ].replace(".blend","")
		directory = bpy.data.filepath.replace(filepath[ len(filepath)-1 ], "")
		frame = bpy.context.scene.frame_current
		
		fileCache = (directory + "blendcache_" + file + "\\" + context.object.CacheDeleteFile + "_" + str(frame).zfill(6) + "_00.bphys" )
		
		fileCacheInitial = (directory + "blendcache_" + file + "\\" + context.object.CacheDeleteFile + "_initial_state.bphys" ) # save
		
		copyfile(fileCache, fileCacheInitial)
		
		return {'FINISHED'}
		
		
class LoadInitialState(bpy.types.Operator):

	"""Load Initial State"""
	bl_label = "Load Initial State"
	bl_idname = "view3d.load_initial_state"

	def execute(self, context):
		
		filepath = bpy.data.filepath.split("\\")
		file = filepath[ len(filepath)-1 ].replace(".blend","")
		directory = bpy.data.filepath.replace(filepath[ len(filepath)-1 ], "")
		
		if(bpy.context.scene.use_preview_range):
			startFrame = bpy.context.scene.frame_preview_start+1
		else:
			startFrame = bpy.context.scene.frame_start+1
			
		fileCacheInitial = (directory + "blendcache_" + file + "\\" + context.object.CacheDeleteFile + "_initial_state.bphys" ) # load previous	
		
		fileCache = (directory + "blendcache_" + file + "\\" + context.object.CacheDeleteFile + "_" + str( startFrame ).zfill(6) + "_00.bphys" )
		copyfile(fileCacheInitial, fileCache)
		
		fileCache = (directory + "blendcache_" + file + "\\" + context.object.CacheDeleteFile + "_" + str( startFrame-1 ).zfill(6) + "_00.bphys" )
		copyfile(fileCacheInitial, fileCache)
		
		bpy.ops.screen.frame_jump() # skoci na zacatek
		
		return {'FINISHED'}
			
			
class OpenCacheFolder(bpy.types.Operator):

	"""Open folder with cache"""
	bl_label = "Open cache folder"
	bl_idname = "view3d.cache_file_folder_open"

	def execute(self, context):
		
		filepath = bpy.data.filepath.split("\\")
		file = filepath[ len(filepath)-1 ].replace(".blend","")
		directory = bpy.data.filepath.replace(filepath[ len(filepath)-1 ], "")
		finalDirectory = directory + "blendcache_" + file
		subprocess.Popen("explorer "+finalDirectory)

		return {'FINISHED'}
	
		
class CacheDelete(bpy.types.Operator):

	"""Delete cache by current time range"""
	bl_label = "Delete cache files"
	bl_idname = "view3d.cache_delete_files"

	def execute(self, context):

		if(len(context.object.CacheDeleteFile) == 0):
			self.report({'ERROR'}, ("Set cache file first") )
			return{'FINISHED'}
		
		else:
			cacheName = context.object.CacheDeleteFile


		filepath = bpy.data.filepath.split("\\")
		file = filepath[ len(filepath)-1 ].replace(".blend","")
		directory = bpy.data.filepath.replace(filepath[ len(filepath)-1 ], "")


		if(bpy.context.scene.use_preview_range):
			startFrame = bpy.context.scene.frame_preview_start
			endFrame = bpy.context.scene.frame_preview_end
		else:
			startFrame = bpy.context.scene.frame_start
			endFrame = bpy.context.scene.frame_end


		for i in range( startFrame, endFrame+1 ):
			
			fileCache = (directory + "blendcache_" + file + "\\" + cacheName + "_" + str(i).zfill(6) + "_00.bphys" )
			
			try:
				os.remove( fileCache )

			except OSError:
				pass
			
		bpy.ops.screen.frame_jump() # skoci na zacatek
			
		return {'FINISHED'}


class PlayStopEnd(bpy.types.Operator):

	"""Play Stop End"""
	bl_idname = "view3d.play_stop_end"
	bl_label = "Play Stop End"
	
	previousState = ""
	
	def modal(self, context, event):
		
		if(bpy.context.scene.use_preview_range):
			endFrame = bpy.context.scene.frame_preview_end
		else:
			endFrame = bpy.context.scene.frame_end
			
		if( (bpy.context.scene.frame_current >= endFrame) or (event.value == 'PRESS') ):
			
			bpy.ops.screen.animation_cancel(restore_frame=False)
			bpy.context.scene.sync_mode = self.previousState # load
			
			return {'FINISHED'}

		return {'RUNNING_MODAL'}
	
	def invoke(self, context, event):
		
		self.previousState = bpy.context.scene.sync_mode # save
		bpy.context.scene.sync_mode = 'NONE'
		
		bpy.ops.screen.animation_play()

		context.window_manager.modal_handler_add(self)
		
		return {'RUNNING_MODAL'}

	
############################################################################################
def register():
	bpy.utils.register_module(__name__)


def unregister():
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()