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
	"name": "Batch Render",
	"author": "Cenek Strichel",
	"version": (1, 0, 2),
	"blender": (2, 7, 9),
	"location": "Render > BATs commands",
	"description": "Create BAT file for easy rendering",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
import os
import glob

from platform import system as currentOS
from bpy.types import Header, Menu
from bpy.props import StringProperty, BoolProperty


# change object mode by selection			
class BatchRender(bpy.types.Operator):

	'''Create BAT file'''
	bl_idname = "screen.batch_render"
	bl_label = "Create BAT file"
	bl_options = {'REGISTER'}
	
	shutdown = BoolProperty(name="Shutdown", default=False)
	range = BoolProperty(name="Range", default=False)
	
	def execute(self, context):
		
		if( len(bpy.data.filepath) == 0 ):
			self.report({'ERROR'}, ("Scene must be saved!") )
			return {'FINISHED'}
			
		if( bpy.context.scene.camera == None ):
			self.report({'ERROR'}, ("Set camera in Scene Settings!") )
			return {'FINISHED'}
			
		# render command #
		command = 'start "Render" /b /low /wait '
		command += "\"" + bpy.app.binary_path + "\""
		command += " --background" + " \"" + bpy.data.filepath + "\""
		
		# range #
		if(self.range):
			start = str(context.scene.frame_preview_start)
			end = str(context.scene.frame_preview_end)
			command += " --frame-start " + start + " --frame-end " + end
			
		command += " --render-anim"
		command += " --scene " + "\"" + context.scene.name + "\""

		batFile = bpy.data.filepath.replace(".blend", ".bat")
		
		# shutdown #
		if(self.shutdown):
			batFile = batFile.replace(".bat", "_shutdown.bat")
			command += "\n"
			command += "shutdown -s -t 10"
			
		# delete bat #		
		command += "\n"
		command += "del \"" + batFile + "\""
		
		# save bat #
		batContent = open( batFile, 'w' )
		batContent.write( command )	
		batContent.close()
		
		# open path to folder #
		filepath = bpy.data.filepath
		relpath = bpy.path.relpath(filepath)
		path = filepath[0: -1 * (relpath.__len__() - 2)]

		bpy.ops.wm.path_open( filepath = path )

		return {'FINISHED'}


class MergeBatch(bpy.types.Operator):

	'''Merge BAT files'''
	bl_idname = "screen.batch_render_merge"
	bl_label = "Merge BAT files"
	bl_options = {'REGISTER'}
	

	def execute(self, context):
		
		filepath = bpy.data.filepath
		relpath = bpy.path.relpath(filepath)
		path = filepath[0: -1 * (relpath.__len__() - 2)]
		
		output = "RENDER_MERGE.bat" # merged bat name
		
		os.chdir(path)
	
		# delete previous Merge file
		if( os.path.exists(output) ):
			os.remove(output)

		o = open( str(output) , "a" )

		for files in glob.glob("*.bat"):
			if( files == output ): # skip Render_merge file is exist
				continue
				
			pathBat = path + files
			i = open( pathBat )
				
			while True:
				
				line = i.readline() # line from bat
				
				if len(line) == 0: # no new line means end
					break # EOF
					
				o.write(str(line)) # write to file
				
			o.write("\n\n")

			i.close()
			
		o.write("del \"" + str(path) + str(output) +"\"" )		
		o.close()

		return {'FINISHED'}
		
	
def menu_func(self, context):
	
	self.layout.separator()
	
	op = self.layout.operator( "screen.batch_render", icon="RESTRICT_RENDER_OFF", text = "BAT" )
	op.shutdown = False
	op.range = False

	op = self.layout.operator( "screen.batch_render", icon="RESTRICT_RENDER_ON", text = "BAT with Shutdown" )
	op.shutdown = True
	op.range = False
	
	start = str(context.scene.frame_preview_start)
	end = str(context.scene.frame_preview_end)
	op = self.layout.operator( "screen.batch_render", icon="PREVIEW_RANGE", text = "BAT with Range [" + start + " - " + end + "]" )
	op.shutdown = False
	op.range = True
	
	self.layout.separator()
	
	self.layout.operator( "screen.batch_render_merge", icon="AUTOMERGE_OFF", text = "BAT Merge" )
	
################################################################
# register #
############
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_render.append(menu_func)
		
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_render.remove(menu_func)
		
if __name__ == "__main__":
	register()