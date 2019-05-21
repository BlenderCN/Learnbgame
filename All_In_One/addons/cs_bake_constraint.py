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
	"name": "Bake Constraint",
	"author": "Cenek Strichel",
	"version": (1, 0, 2),
	"blender": (2, 79, 0),
	"location": "Relations > Bake Constraint",
	"description": "For baking helpers (BAKE) constraint",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}

import bpy

from bpy.props import EnumProperty
from bpy.types import Header


class AnimConstraintSwitch(bpy.types.Operator):

	'''Switching for Animation Constraint'''
	bl_idname = "view3d.switch_anim_constraint"
	bl_label = "Constraint"
	
	switchStyleEnum = [
	("Toggle", "Toggle", "", "", 0),
    ("On", "On", "", "", 1),
    ("Off", "Off", "", "", 2),
    ]

	switchStyle = EnumProperty(name="switchStyle", items=switchStyleEnum) 
	
	
	def execute(self, context):

		bone = bpy.context.active_pose_bone
		state = False

		# first state
		if(self.switchStyle == 'Toggle'):
			for const in bone.constraints :
				if "BAKE" in const.name :
					state = const.mute
	
		# cycle all constraint
		for const in bone.constraints :
			if "BAKE" in const.name :
				
				# Toggle / On / Off
				if(self.switchStyle == 'Toggle'):
					const.mute = not state
					
				elif(self.switchStyle == 'On'):
					const.mute = False
					
				elif(self.switchStyle == 'Off'):
					const.mute = True
	
		# redraw constraint state
		for area in bpy.context.screen.areas:
			if area.type == 'PROPERTIES':
				area.tag_redraw()
		
		
		return {'FINISHED'}


class AnimConstraintBake(bpy.types.Operator):

	'''Baking for Animation Constraint'''
	bl_idname = "view3d.bake_anim_constraint"
	bl_label = "Bake"
	
	def execute(self, context):

		if( bpy.context.scene.is_nla_tweakmode ): # sometimes it is not working well
			
			self.report({'ERROR'},"Can not bake in NLA Tweak mode")
			
		else:
			if(bpy.context.scene.use_preview_range):
				startFrame = bpy.context.scene.frame_preview_start
				endFrame = bpy.context.scene.frame_preview_end
			else:
				startFrame = bpy.context.scene.frame_start
				endFrame = bpy.context.scene.frame_end
			
			# bake by range
			bpy.ops.nla.bake( frame_start = startFrame , frame_end = endFrame, visual_keying=True, use_current_action=True, bake_types={'POSE'} )
			
			# turn off constraint (it is showed only with Anim Constraint)
			bpy.ops.view3d.switch_anim_constraint( switchStyle = 'Off')

		return {'FINISHED'}
		
		
class AnimConstraintAdd(bpy.types.Operator):
	
	'''Mark constraint for bake with BAKE prefix'''
	bl_idname = "view3d.add_anim_constraint"
	bl_label = "Mark Constraint"
	
	def execute(self, context):
	
		bone = bpy.context.active_pose_bone
		
		for const in bone.constraints :
			if "BAKE" not in const.name : 
				const.name = "BAKE " + const.name
				break # only first

		return {'FINISHED'}
	
	
# PANEL #
class PanelBakeConstraint(bpy.types.Panel):
	
	bl_label = 'Bake Constraint'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = 'Relations'
	
	def draw(self, context):
		
		bone = bpy.context.active_pose_bone

		layout = self.layout
		col = layout.column(align=True)

		# buttons
		if( bone != None ):

			markedConstraint = False
			current_icon = ""
			
			# cycle all constraint
			for const in bone.constraints :
				
				if "BAKE" in const.name :
					
					if( const.mute ) :
						current_icon = 'VISIBLE_IPO_OFF'
						
					else:	
						current_icon = 'VISIBLE_IPO_ON'
						
				if(const.active):
					markedConstraint = True
					
					
			###################################################
			# CONSTRAINT
			###################################################
			
			# ADD MARK #
			if( current_icon == "" ): 
				
				if( markedConstraint ):
					col.operator("view3d.add_anim_constraint", icon = "CONSTRAINT")
				
				if( not markedConstraint ):
					col.label("No constraint found")
					
			# MARK IS THERE #
			else:
				col.operator("view3d.switch_anim_constraint", icon = current_icon).switchStyle = 'Toggle'	
				col.operator("view3d.bake_anim_constraint", icon = "BLANK1" )
				
		else:
			col.label("Select bone")


################################################################
# register #

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()