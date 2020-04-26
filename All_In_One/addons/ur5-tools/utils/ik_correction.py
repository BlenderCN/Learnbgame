import bpy
import bottom_limit_check, direction_check, mesh_intersect
import math
"""
Runner script to correct ik contraints to fix the issues brought up by the checks
"""
def prepare_ik_limits():
	"""
	Makes sure the ik_limits are turned on 
	"""

	bpy.data.objects['Armature'].pose.bones['Shoulder'].use_ik_limit_y = True
	bpy.data.objects['Armature'].pose.bones['Elbow'].use_ik_limit_y = True
	bpy.data.objects['Armature'].pose.bones['Wrist1'].use_ik_limit_y = True
	bpy.data.objects['Armature'].pose.bones['Wrist2'].use_ik_limit_y = True

def _set_ik_contraints(bone, min, max, axis = 'y'):
	"""
	Sets the ik_contraints for the input bone on the input axis. 

	The axis will default to 'y' since that is the rotation axis for bones in the UR5_Shoulder`.
	"""

	if(axis == 'y'):
		bone.ik_min_y = min
		bone.ik_max_y = max
	elif(axis == 'x'):
		bone.ik_min_x = min
		bone.ik_max_x = max
	elif(axis == 'z'):
		bone.ik_min_z = min
		bone.ik_max_z = max
	#Refresh the contraints
	bpy.context.scene.update()

def _change_ik_contraints(bone, change_min, change_max , is_increase = True, axis = 'y'):
	"""
	Changes the ik contraints for the input bone on the input axis

	The axis will default to 'y' and the change will be assumed to positive
	"""
	if(axis =='y'):
		bone.ik_min_y += (2*int(is_increase)-1)*change_min
		bone.ik_max_y += (2*int(is_increase)-1)*change_max
	if(axis =='x'):
		bone.ik_min_x += (2*int(is_increase)-1)*change_min
		bone.ik_max_x += (2*int(is_increase)-1)*change_max
	if(axis =='z'):
		bone.ik_min_z += (2*int(is_increase)-1)*change_min
		bone.ik_max_z += (2*int(is_increase)-1)*change_max
	#Refresh the contraints
	bpy.context.screen.update()
def fix_bottom_limit():
	"""
	Fixes the ik contraints of the shoulder to raise the armature over the safe table area

	As of now, it only changes the shoulder. If more limiting cases come up, more detailed change will be made
	"""
	while(bottom_limit_check.return_limiting_mesh() != None and bpy.data.objects['Armature'].pose.bones["Shoulder"].ik_min_y != 0):
		_change_ik_contraints(bpy.data.objects['Armature'].pose.bones["Shoulder"],0.5/180*math.pi,0)
	while(mesh_intersect.return_limiting_mesh != None and bpy.data.objects['Armature'].pose.bones["Shoulder"].ik_min_y != 0):
		_change_ik_contraints(bpy.data.objects['Armature'].pose.bones['Shoulder'],0.5/180*math.pi,0)

def fix_mesh_intersect():
	"""
	Fixes the ik contraints of a certain bone so meshes will not intersect with itself
	"""
	meshs = mesh_intersect.return_intersecting_meshs()
	while(meshes != None):
		if(meshes[0] == "UR5_Shoulder" or meshes[1] == "UR5_Shoulder"):
			if(bpy.data.objects['Armature'].pose.bones['Shoulder'].ik_min_y != 0):
				_change_ik_contraints(bpy.data.objects['Armature'].pose.bones["Shoulder"],0.5/180*math.pi,0)
			else: 
				_change_ik_contraints(bpy.data.objects['Armature'].pose.bones["Shoulder"],0,0.5/180*math.pi)
			if(bpy.data.objects['Armature'].pose.bones['Shoulder'].ik_min_y == 0 and bpy.data.objects['Armature'].pose.bones['Shoulder'].ik_max_y == math.pi):
				print("Error Encountered Changing Shoulder Intersect")
				bpy.data.objects['Armature'].pose.bones['Shoulder'].ik_max_y = 0
				bpy.data.objects['Armature'].pose.bones['Shoulder'].ik_min_y = -math.pi
				break
		elif(meshes[0] == "UR5_Elbow" or meshes[1] == "UR5_Elbow"):
			if(bpy.data.objects['Armature'].pose.bones['Elbow'].ik_min_y != 0):
				_change_ik_contraints(bpy.data.objects['Armature'].pose.bones["Elbow"],0.5/180*math.pi,0)
			else: 
				_change_ik_contraints(bpy.data.objects['Armature'].pose.bones["Elbow"],0,0.5/180*math.pi)
			if(bpy.data.objects['Armature'].pose.bones['Elbow'].ik_min_y == 0 and bpy.data.objects['Armature'].pose.bones['Elbow'].ik_max_y == math.pi):
				print("Error Encountered Changing Elbow Intersect")
				bpy.data.objects['Armature'].pose.bones['Shoulder'].ik_max_y = 0
				bpy.data.objects['Armature'].pose.bones['Shoulder'].ik_min_y = -math.pi
				break
		meshs = mesh_intersect.return_intersecting_meshs()

def fix_direction():
	"""
	Fixes the direction of the Elbow mesh
	"""
	bpy.data.objects['Armature'].pose.bones.['Elbow'].ik_max_y = math.pi
	while(direction_check.check_elbow_direction() and bpy.data.objects['Armature'].pose.bones['Shoulder'].ik_min_y != 0):
		_change_ik_contraints(bpy.data.objects['Armature'].pose.bones["Shoulder"],0.5/180*math.pi,0)

def fix_all():
	fix_bottom_limit()
	fix_direction()
	fix_mesh_intersect()