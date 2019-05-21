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
	"name": "Render Tools",
	"category": "Cenda Tools",
	"author": "Cenek Strichel",
	"description": "Render Region & Render without file output",
	"location": "Hotkey (commands)",
	"version": (1, 0, 3),
	"blender": (2, 79, 0),
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
}


import bpy

from bpy.app.handlers import persistent
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Header, Panel

import bpy
import bgl
import blf


def draw_callback_px(self, context):

	bgl.glEnable(bgl.GL_BLEND)
	bgl.glColor4f(1.0, 0.0, 0.0, 0.5)
	bgl.glLineWidth(2)
	
	bgl.glBegin(bgl.GL_LINE_STRIP)
	
	for x, y in self.mouse_path:
		bgl.glVertex2i(self.startX, y)
		
	for x, y in self.mouse_path:	
		bgl.glVertex2i( x, self.startY)
		
	bgl.glEnd()
	
	bgl.glLineWidth(1)
	bgl.glDisable(bgl.GL_BLEND)
	bgl.glColor4f(1.0, 0.0, 0.0, 1.0)


################################################################
# RENDER REGION #
################################################################
class RenderRegion(bpy.types.Operator):
	
	
	bl_idname = "view3d.render_region"
	bl_label = "Render region"
	
	bpy.types.Scene.ViewportShading = StringProperty( 
	name = "", 
	default = "",
	description = "")
	
	'''
	startX = IntProperty()
	startY = IntProperty()
	drawGL = BoolProperty()
	'''
	
	def modal(self, context, event):

		context.area.tag_redraw()


		# RETURN BACK #
		if( bpy.context.space_data.viewport_shade == 'RENDERED' ):
			
			bpy.context.space_data.viewport_shade = context.scene.ViewportShading
			bpy.ops.view3d.clear_render_border()
			
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			
			bpy.context.window.cursor_set("DEFAULT")
			
			return {'FINISHED'}
		
		
		# SET REGION #
		elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':

			context.scene.ViewportShading = bpy.context.space_data.viewport_shade
			
			self.startX = event.mouse_region_x 
			self.startY = event.mouse_region_y 
			
			self.drawGL = True
			
		
		# RENDER AFTER SET REGION #
		elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':

			endX = event.mouse_region_x 
			endY = event.mouse_region_y 

			if(self.startY > endY and self.startX < endX):
				bpy.ops.view3d.render_border( xmin=self.startX, xmax=endX, ymin=endY, ymax=self.startY, camera_only=False )
				
			elif(self.startY < endY and self.startX > endX):
				bpy.ops.view3d.render_border( xmin=endX, xmax=self.startX, ymin=self.startY, ymax=endY, camera_only=False )
				
			elif(self.startY < endY and self.startX < endX):	
				bpy.ops.view3d.render_border( xmin=self.startX, xmax=endX, ymin=self.startY, ymax=endY, camera_only=False )
				
			elif(self.startY > endY and self.startX > endX):	
				bpy.ops.view3d.render_border( xmin=endX, xmax=self.startX, ymin=endY, ymax=self.startY, camera_only=False )
				
			bpy.context.space_data.viewport_shade = 'RENDERED'
			
			# remove draw
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			
			bpy.context.window.cursor_set("DEFAULT")
			
			return {'FINISHED'}
		
		# CANCEL REGION #
		elif event.type == 'ESC':
			
			bpy.context.window.cursor_set("DEFAULT")
			
			return {'FINISHED'}
		
		if(self.drawGL):
			
			self.mouse_path.append((event.mouse_region_x, event.mouse_region_y))

		return {'RUNNING_MODAL'}
	
	
	def invoke(self, context, event):

		self.drawGL = False

		args = (self, context)
		self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
		self.mouse_path = []
		self.mouse_path.clear()
		
		context.window_manager.modal_handler_add(self)
		
		bpy.context.window.cursor_set("CROSSHAIR")
		
		return {'RUNNING_MODAL'}


	'''
	def execute(self, context):
		
		print("RENDER")
		
		
		if( bpy.context.space_data.viewport_shade == 'RENDERED' ):
			
			bpy.context.space_data.viewport_shade = context.scene.ViewportShading # 'MATERIAL'
			bpy.ops.view3d.clear_render_border()

		else:
			
			context.scene.ViewportShading = bpy.context.space_data.viewport_shade
			bpy.ops.view3d.render_border('INVOKE_DEFAULT')
			bpy.context.space_data.viewport_shade = 'RENDERED'
		
		
		return {'FINISHED'}
	'''
	
	
################################################################
# RENDER WITHOUT FILE OUTPUT
################################################################
class RenderWithoutFileOutput(bpy.types.Operator):


	bl_idname = "render.render_without_fileoutput"
	bl_label = "Render without File Output"
	bl_options = {'REGISTER'}
	
	bpy.types.Scene.FileOutput = StringProperty( 
	name = "", 
	default = "",
	description = "")
	
	def execute(self, context):
		
		# switch on nodes and get reference #
		if(bpy.context.scene.use_nodes):

			# cycle all nodes
			for node in bpy.context.scene.node_tree.nodes:
				
				# node tree
				if( node.type == "OUTPUT_FILE" ):
					if(node.mute == False):	
						context.scene.FileOutput += node.name + ";"	# saved all except disabled
						node.mute = True
						
			# all node groups
			for ng in bpy.data.node_groups:
				for n in bpy.data.node_groups[ ng.name ].nodes:
					if( n.type == "OUTPUT_FILE" ):
						if(n.mute == False):	
							context.scene.FileOutput += n.name + ";" # saved all except disabled
							n.mute = True
				
		# rendering #
		bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=False, use_viewport=False )
		
		return {'FINISHED'}


@persistent
def render_handler(scene):
	
    # enable back output #	
	if(bpy.context.scene.use_nodes):
		
		if(len(bpy.context.scene.FileOutput) > 0):

			fileOutputs = bpy.context.scene.FileOutput.split(";")
			
			for f in fileOutputs:
				
				# cycle all nodes
				for node in bpy.context.scene.node_tree.nodes:
					
					# node tree
					if( node.type == "OUTPUT_FILE" ):
						if(node.name == f):
							node.mute = False
							
				# all node groups
				for ng in bpy.data.node_groups:
					for n in bpy.data.node_groups[ ng.name ].nodes:
						if( n.type == "OUTPUT_FILE" ):
							if(n.name == f):
								n.mute = False
									
			bpy.context.scene.FileOutput = ""


def RenderButtonEditor(self, context):
	
	layout = self.layout
	row = layout.row(align=True)

	row.operator( "render.render_without_fileoutput", text = "Render w/o Output", icon = "RENDER_STILL" )
	
	
def RenderButtonCamera(self, context):
	
	space = bpy.context.space_data
	
	# Normal view
	if(space.region_3d.view_perspective == 'CAMERA'): # only for camera
	
		layout = self.layout
		
		row = layout.row(align=True)
		row.operator( "render.render_without_fileoutput", text = "Render w/o Output", icon = "RENDER_STILL" )
	
		
################################################################
# register #
def register():
	bpy.utils.register_module(__name__)
	bpy.app.handlers.render_post.append(render_handler)
	bpy.types.IMAGE_HT_header.prepend(RenderButtonEditor)
	bpy.types.VIEW3D_HT_header.prepend(RenderButtonCamera)
	
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.IMAGE_HT_header(RenderButtonEditor)
	bpy.types.VIEW3D_HT_header(RenderButtonCamera)
	
if __name__ == "__main__":
	register()