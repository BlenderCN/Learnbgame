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
	"name": "IK Setup",
	"author": "Cenek Strichel",
	"version": (1, 0, 1),
	"blender": (2, 79, 0),
	"location": "Pose > Inverse Kinematics > Add IK to Bone with Auto Chain",
	"description": "Easier IK Setup",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}

import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty
from bpy.types import Header, Panel
import math


################
# AUTO IK CHAIN #
################

class AddIkChain(bpy.types.Operator):
	# Without Pole Target\n # \n\nWith Pole Target\n1) IK Handle\n2) Pole Target\n3) IK Constraint
	'''1) IK Handle\n2) IK Constraint'''
	bl_idname = "pose.ik_add_chain_length"
	bl_label = "Add IK to Bone with Auto Chain"
	bl_options = {'REGISTER', 'UNDO'}

	autoChainLength = BoolProperty(name="Auto Chain Length", default=True)
	chainLength = IntProperty(name="Chain Length", default=2, min = 0)
	ikProperties = BoolProperty(name="IK Blend Properties", default=True)
#	poleAngle = FloatProperty(name="Pole Angle", default=0, min = -180, max = 180)
	
	
	def execute(self, context):

		bpy.ops.pose.ik_add(with_targets=True)

		# auto chain length
		if(self.autoChainLength):
			
			currentBone = bpy.context.active_bone
			chainLength = 1
			
			while( currentBone.parent != None ) :
				
				chainLength +=1
				
				if( not currentBone.parent.use_connect ):
					break
				
				else :	
					currentBone = currentBone.parent

			bpy.context.active_pose_bone.constraints["IK"].chain_count = chainLength
		
		# manual chain length	
		else:
			bpy.context.active_pose_bone.constraints["IK"].chain_count = self.chainLength
		
		
		#####################
		# IK CUSTOM SETTING #
		#####################
		# driver and target #
		if(self.ikProperties):
			
			bones = bpy.context.selected_pose_bones
			i = 0

			for bone in bones:
				
				i+=1
				
				# TODO - order is not preserved :(
				
			#	if( len(bones) == 3 and i == 3 ):
			#		ikConstrBone = bone
					
			#	if( len(bones) == 3 and i == 2 ):
			#		targetBone = bone

				if( len(bones) == 2 and i == 2 ):
					ikConstrBone = bone
				
				if( i == 1 ): # first selected
					bone["IK"] = 1.0
					bone["_RNA_UI"] = {}
					bone["_RNA_UI"]["IK"] = {"min":0.0,"max": 1.0,"soft_min":0.0,"soft_max":1.0}
					ikHandleBone = bone

	#		if( len(bones) == 3):
	#			ikConstrBone.constraints["IK"].pole_target = bpy.context.active_object
	#			ikConstrBone.constraints["IK"].pole_subtarget = targetBone.name
	#			ikConstrBone.constraints["IK"].pole_angle = math.radians( self.poleAngle )
				
			# add driver	
			driv = ikConstrBone.constraints["IK"].driver_add( 'influence' )
			driv.driver.expression = "var"
			
			# variable
			var = driv.driver.variables.new()
			var.name = 'var'
			var.type = 'SINGLE_PROP'
			
			var.targets[0].id = bpy.context.object
			var.targets[0].data_path = 'pose.bones["'+ikHandleBone.name+'"]["IK"]'

		
		return {'FINISHED'}


def menu_addIk(self, context):
	
    self.layout.operator(
        AddIkChain.bl_idname,
        icon="CONSTRAINT_DATA"
		)


################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_pose_ik.prepend(menu_addIk) # add auto ik chain to menu
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_pose_ik.remove(menu_addIk)
	
if __name__ == "__main__":
	register()