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
	"name": "Bake & Unbake",
	"author": "Cenek Strichel",
	"version": (1, 0, 1),
	"blender": (2, 79, 0),
	"location": "Physics > Rigid Body Settings",
	"description": "Bake / Unbake, Save / Load setttings",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Header, Panel




# GUI ###############################################################
class VIEW3D_PT_tools_rigid_body_save_load(bpy.types.Panel):
	
	bl_label = "Rigid Body Settings"
	bl_idname = "RB_ANIMATION_PANEL"
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Physics"
	bl_context = "objectmode"

	bpy.types.Scene.RBWorldSettings = bpy.props.BoolProperty( 
	name = "Load RB World Settings", 
	default = True, 
	description = "Optional\nLoad Rigid Body World settings")
	
	
	def draw(self, context):
		
		layout = self.layout
		row = layout.row(align=True)
		
		noRB= True
		
		# Save / Bake
		if ((bpy.context.object.rigid_body is not None) or (len(bpy.context.object.RBSettings) > 0) ):
			
			row.operator("object.rigid_body_bake", text="Bake", icon = "MESH_ICOSPHERE").bake = True
			row.operator("object.rigid_body_settings", text="Save", icon = "FILE_TICK").save = True

			row = layout.row(align=True)
			row.operator("object.rigid_body_bake", text="Unbake", icon = "X").bake = False
			row.operator("object.rigid_body_settings", text="Load", icon = "OPEN_RECENT").save = False
			
			row = layout.row(align=True)
			row.prop(context.scene, "RBWorldSettings")
			
			noRB = False
			
			
		if(noRB):	
			row.label("No Rigid Body or Saved data")

		
		
class RBSettings(bpy.types.Operator):
	
	'''Save / Load Rigidbody'''
	bl_idname = "object.rigid_body_settings"
	bl_label = "Save/Load RB setting"

	save = BoolProperty(name="Save",default=True)
	bpy.types.Object.RBSettings = bpy.props.StringProperty( name = "RBSetting", description = "")
	
	
	def execute(self, context):
		
		scn = bpy.context.scene
		obj = bpy.context.object
		
		# Save
		if(self.save) :
			
			bpy.ops.rigidbody.object_add()
			
			# SAVE
			obj.RBSettings = str(obj.rigid_body.enabled)+";"
			obj.RBSettings += str(obj.rigid_body.kinematic)+";"
			obj.RBSettings += str(obj.rigid_body.mass)+";"
			
			obj.RBSettings += str(obj.rigid_body.collision_shape)+";"
			obj.RBSettings += str(obj.rigid_body.mesh_source)+";"
			
			
			obj.RBSettings += str(obj.rigid_body.friction)+";"
			obj.RBSettings += str(obj.rigid_body.restitution)+";"
			obj.RBSettings += str(obj.rigid_body.use_margin)+";"
			obj.RBSettings += str(obj.rigid_body.collision_margin)+";"

						
			for i in range(20):
				obj.RBSettings += str(obj.rigid_body.collision_groups[i])+";"

			obj.RBSettings += str(obj.rigid_body.use_deactivation)+";"
			obj.RBSettings += str(obj.rigid_body.use_start_deactivated)+";"
			obj.RBSettings += str(obj.rigid_body.deactivate_linear_velocity)+";"
			obj.RBSettings += str(obj.rigid_body.deactivate_angular_velocity)+";"
			obj.RBSettings += str(obj.rigid_body.linear_damping)+";"
			obj.RBSettings += str(obj.rigid_body.angular_damping)+";"

			# GLOBAL
			bpy.context.object.RBSettings += str(scn.rigidbody_world.time_scale)+";"
			bpy.context.object.RBSettings += str(scn.rigidbody_world.steps_per_second)+";"
			bpy.context.object.RBSettings += str(scn.rigidbody_world.use_split_impulse)+";"
			bpy.context.object.RBSettings += str(scn.rigidbody_world.solver_iterations)+";"

		else :
			
			bpy.ops.rigidbody.object_add()
			savedSetting = str.split(bpy.context.object.RBSettings,";")
			
			# LOAD
			obj.rigid_body.enabled = True if savedSetting[0] == 'True' else False
			obj.rigid_body.kinematic = True if savedSetting[1] == 'True' else False
			obj.rigid_body.mass = float(savedSetting[2])
			
			obj.rigid_body.collision_shape = savedSetting[3]
			obj.rigid_body.mesh_source = savedSetting[4]

			
			obj.rigid_body.friction = float(savedSetting[5])
			obj.rigid_body.restitution = float(savedSetting[6])
			obj.rigid_body.use_margin = True if savedSetting[7] == 'True' else False
			obj.rigid_body.collision_margin = float(savedSetting[8])
			
			for i in range(9,29):
				obj.rigid_body.collision_groups[i-9] = True if savedSetting[i] == 'True' else False
			
			obj.rigid_body.use_deactivation = True if savedSetting[29] == 'True' else False
			obj.rigid_body.use_start_deactivated = True if savedSetting[30] == 'True' else False
			obj.rigid_body.deactivate_linear_velocity = float(savedSetting[31])
			obj.rigid_body.deactivate_angular_velocity = float(savedSetting[32])
			obj.rigid_body.linear_damping = float(savedSetting[33])
			obj.rigid_body.angular_damping = float(savedSetting[34])
			
			# GLOBAL
			if(scn.RBWorldSettings):
				scn.rigidbody_world.time_scale = float(savedSetting[35])
				scn.rigidbody_world.steps_per_second = float(savedSetting[36])
				scn.rigidbody_world.use_split_impulse = True if savedSetting[37] == 'True' else False
				scn.rigidbody_world.solver_iterations = float(savedSetting[38])
			
		return {'FINISHED'}	
	
	
class RBBake(bpy.types.Operator):
	
	'''Bake and Save Rigidbody\n\nUnbake and Load Rigidbody'''
	bl_idname = "object.rigid_body_bake"
	bl_label = "Bake/Unbake"

	bake = BoolProperty(name="Bake",default=True)
	
	def execute(self, context):
		
		if(self.bake):
			
			# save settings
			bpy.ops.object.rigid_body_settings( save = True )
			
			# bake by range
			if(bpy.context.scene.use_preview_range):
				startFrame = bpy.context.scene.frame_preview_start
				endFrame = bpy.context.scene.frame_preview_end
			else:
				startFrame = bpy.context.scene.frame_start
				endFrame = bpy.context.scene.frame_end
			
			bpy.ops.rigidbody.bake_to_keyframes(frame_start=startFrame, frame_end=endFrame)

	
		else:
			bpy.ops.screen.frame_jump() # jump to first frame

			# unlink action
			obj = bpy.context.object
			obj.animation_data.action = None
			
			# load rigid body
			bpy.ops.object.rigid_body_settings( save = False )
		
		return {'FINISHED'}
	
	
################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()