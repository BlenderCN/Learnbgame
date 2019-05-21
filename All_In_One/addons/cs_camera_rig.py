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
	"name": "Camera Rig",
	"author": "Cenek Strichel",
	"version": (1, 0, 1),
	"blender": (2, 79, 0),
	"location": "Add > Armature > Camera Rig",
	"description": "Create Custom camera rig",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy

################################################################################### 
## This is the operator that will call all the functions and build the crane rig ##
###################################################################################

class CameraRig(bpy.types.Operator):
	
	"""Create camera rig"""
	bl_idname = "object.camera_rig"
	bl_label = "Create new Camera rig"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):

		addonsFolder = bpy.utils.user_resource('SCRIPTS', "addons")
		blendfile = addonsFolder + "\\cs_camera_rig.blend"
		section   = "\\Group\\"
		object    = "CameraRig"

		filepath  = blendfile + section + object
		directory = blendfile + section
		filename  = object

		# append rig
		bpy.ops.wm.append(
			filepath=filepath, 
			filename=filename,
			directory=directory)
			
		# delete wgts
		bpy.ops.object.select_all(action='DESELECT')

		bpy.data.objects['WGT_Camera'].select = True
		bpy.data.objects['WGT_Crane'].select = True
		bpy.data.objects['WGT_DOF'].select = True
		bpy.data.objects['WGT_Root'].select = True
		bpy.data.objects['WGT_Target'].select = True
		
		bpy.ops.object.delete(use_global=False)
		
		return {'FINISHED'}

##############################
##       Registration:      ##
##############################

#dolly button in Armature menu
def add_camera_rig_button(self, context):
	self.layout.operator( CameraRig.bl_idname, text="Camera Rig", icon='CAMERA_DATA')

def register():

	bpy.utils.register_class(CameraRig)
	bpy.types.INFO_MT_armature_add.append(add_camera_rig_button)

def unregister():

	bpy.utils.unregister_class(CameraRig)
	bpy.types.INFO_MT_armature_add.remove(add_camera_rig_button)


if __name__ == "__main__":
	register()
