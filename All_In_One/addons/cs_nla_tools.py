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
	"name": "NLA Tools",
	"author": "Cenek Strichel",
	"version": (1, 0, 0),
	"blender": (2, 79, 0),
	"location": "NLA editor (headbar and hotkeys)",
	"description": "NLA tools",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from bpy.types import Header, Panel

	
################	
class NLAToolsButtons(Header):
	
	bl_space_type = 'NLA_EDITOR'
	
	
	tweakModeEnum = [
	("Disabled", "Disabled", "", "CANCEL", 0),
    ("PreviewRange", "Preview Range", "", "PREVIEW_RANGE", 1),
    ("ViewSelected", "View Selected", "", "RESTRICT_SELECT_OFF", 2),
    ("PreviewView", "Preview & View", "", "ACTION_TWEAK", 3)
    ]

	bpy.types.Scene.NLATweakMode = EnumProperty( 
	name = "", 
	description = "Changes with Tweak mode", 
	items=tweakModeEnum )
	
	bpy.types.Scene.NLAIsolate = BoolProperty( 
	name = "", 
	default = True, 
	description = "Isolate with Tweak mode")
	
	
	def draw(self, context):
		
		layout = self.layout
		col = layout.column()

		col = layout.column()
		row = col.row(align = True)
		
		scn = context.scene
		
		if(scn.NLAIsolate):
			newIcon = "SOLO_ON"
		else:
			newIcon = "SOLO_OFF"
			
		row.prop(scn, "NLAIsolate", icon = newIcon )
		row.prop(scn, "NLATweakMode" )
		
		col = layout.column()
		row = col.row(align = True)
		row.operator( "nla.cut_strip" , icon = "NLA")			
		
			
################
# CUT STRIP #
################
# copy and flip pose in one step
class CutStrip(bpy.types.Operator):

	'''Cut strip by scene setting'''
	bl_idname = "nla.cut_strip"
	bl_label = "Cut by Range"
	bl_options = {'REGISTER', 'UNDO'}

	
	def execute(self, context):
		
		# only for activated preview range
		if bpy.context.scene.use_preview_range :
			
			try:
			    selected_strips = [strip for strip in bpy.context.object.animation_data.nla_tracks.active.strips if strip.select]
			
			except AttributeError:
			    selected_strips = []

			# get range
			startFrame = bpy.context.scene.frame_preview_start
			endFrame = bpy.context.scene.frame_preview_end

			for strip in selected_strips :
				# set range animation
				strip.action_frame_start = startFrame
				strip.action_frame_end = endFrame
				
				# move animation clip
				strip.frame_start = startFrame
				strip.frame_end = endFrame
		
			# redraw 
			for area in bpy.context.screen.areas:
				if area.type == 'NLA_EDITOR':
					area.tag_redraw()
			
		else:
			self.report({'ERROR'}, "Preview Range in timeline must be activated!")	
			
		return {'FINISHED'}	
	
	
###################
# NLA Tweak mode #
##################
class NLATweakRangeToggle(bpy.types.Operator):


	'''Tweak and Range Toggle'''
	bl_idname = "nla.tweak_and_range"
	bl_label = "Tweak and Range Toggle"
	
	
	def execute(self, context):
		
		scn = context.scene
		
		# Enter #
		if( not bpy.context.scene.is_nla_tweakmode ):
			
			bpy.ops.nla.tweakmode_enter( isolate_action = scn.NLAIsolate )

			# Range by NLA
			if( scn.NLATweakMode == 'PreviewRange' or scn.NLATweakMode == 'PreviewView' ):
				bpy.ops.nla.previewrange_set()
				
			# Frame view for all editors
			if( scn.NLATweakMode == 'ViewSelected' or scn.NLATweakMode == 'PreviewView' ):
				bpy.ops.nla.view_selected()
				
				# set timeline to frame range
				for area in bpy.context.screen.areas:
					
					FrameForEditor( area, 'TIMELINE')
					FrameForEditor( area, 'DOPESHEET_EDITOR')
					FrameForEditor( area, 'GRAPH_EDITOR')

		# Exit # TODO: not working
		else:
			
			bpy.ops.nla.tweakmode_exit(isolate_action = scn.NLAIsolate)
			
			if( scn.NLATweakMode == 'PreviewRange' or scn.NLATweakMode == 'PreviewView' ):
				bpy.context.scene.use_preview_range = False
				
			bpy.ops.nla.view_selected() # needed for return back

		return {'FINISHED'}


def FrameForEditor( currentArea, testedArea ):
	
	if currentArea.type == testedArea:
		for region in currentArea.regions:
			if region.type == 'WINDOW':
				
				ctx = bpy.context.copy()
				ctx[ 'area'] = currentArea
				ctx['region'] = region
				
				if(testedArea == 'TIMELINE'):
					bpy.ops.time.view_all(ctx)
					
				elif(testedArea == 'DOPESHEET_EDITOR'):
					bpy.ops.action.view_all(ctx)
					
				elif(testedArea == 'GRAPH_EDITOR'):
					bpy.ops.graph.view_all(ctx)
						
				break
	

						
################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
	register()