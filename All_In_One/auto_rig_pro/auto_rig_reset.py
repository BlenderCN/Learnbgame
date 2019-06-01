import bpy

def reset_all():

	def set_inverse_child(b):
		pbone = bpy.context.active_object.pose.bones[b]
		context_copy = bpy.context.copy()
		context_copy["constraint"] = pbone.constraints["Child Of"]
		bpy.context.active_object.data.bones.active = pbone.bone
		try:
			bpy.ops.constraint.childof_set_inverse(context_copy, constraint="Child Of", owner='BONE')	
		except:
			print('Invalid bone constraint', b)
		
		
	# Reset transforms-------------g-----------------
	bpy.ops.pose.select_all(action='SELECT')
	bpy.ops.pose.loc_clear()
	bpy.ops.pose.rot_clear()
	bpy.ops.pose.scale_clear()

	# Reset Properties
	for bone in bpy.context.object.pose.bones:
		if len(bone.keys()) > 0:
			for key in bone.keys():
				if 'ik_fk_switch' in key:
					if 'hand' in bone.name:
						bone['ik_fk_switch'] = 1.0
					else:
						bone['ik_fk_switch'] = 0.0
				if 'stretch_length' in key:
					bone['stretch_length'] = 1.0
				if 'auto_stretch' in key:
					bone['auto_stretch'] = 1.0
				if 'pin' in key:
					if 'leg' in key:
						bone['leg_pin'] = 0.0
					else:
						bone['elbow_pin'] = 0.0
				if 'bend_all' in key:
					bone['bend_all'] = 0.0
					
		if len(bone.constraints) > 0:
			if 'hand' in bone.name or 'foot' in bone.name:
				for cns in bone.constraints:
					if 'Child Of' in cns.name:
						set_inverse_child(bone.name)
			if 'head' in bone.name:
				for cns in bone.constraints:
					if 'Child Of' in cns.name:	
						#set_inverse_child(bone.name)
						cns.inverse_matrix = bpy.context.object.pose.bones['c_neck.x'].matrix.inverted()
						


	bpy.ops.pose.select_all(action='DESELECT')