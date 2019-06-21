import os
import json
import mathutils
import bpy

def getOffsetFromAToB(a, b):
	ta, ra, sa = a.matrix_world.decompose()
	tb, rb, sb = b.matrix_world.decompose()
	MtaInv = mathutils.Matrix.Translation(-ta)
	MraInv = ra.to_matrix().inverted().to_4x4()
	Mtb = mathutils.Matrix.Translation(tb)
	Mrb = rb.to_matrix().to_4x4()
	Moffset = MraInv @ MtaInv @ Mtb @ Mrb
	tOffset, rOffset, sOffset = Moffset.decompose()
	tOffset.x = tOffset.x / sa.x
	tOffset.y = tOffset.y / sa.y
	tOffset.z = tOffset.z / sa.z
	return tOffset, rOffset

def save(context, path):
	jsonObject = {}

	scene = context.scene
	jsonObject["gravity"] = scene.gravity[:]
	jsonObject["rigid_bodys"] = []
	jsonObject["constraints"] = []

	for obj in scene.objects:
		

		if obj.rigid_body is not None:
			transform = obj.matrix_world
			location, quaternion, scale = transform.decompose()
			rigidBodyObject = {}
			rigidBodyObject["name"] = obj.name
			rigidBodyObject["location"] = location[0:3]
			rigidBodyObject["quaternion"] = quaternion[0:4]
			rigidBodyObject["static"] = obj.rigid_body.type == 'PASSIVE'
			rigidBodyObject["kinematic"] = obj.rigid_body.kinematic
			rigidBodyObject["mass"] = 0 if obj.rigid_body.type == 'PASSIVE' else obj.rigid_body.mass
			rigidBodyObject["friction"] = obj.rigid_body.friction
			rigidBodyObject["restitution"] = obj.rigid_body.restitution
			rigidBodyObject["collision_shape"] = obj.rigid_body.collision_shape
			rigidBodyObject["use_margin"] = obj.rigid_body.use_margin
			rigidBodyObject["collision_margin"] = obj.rigid_body.collision_margin
			group = 0
			for i in range(0, len(obj.rigid_body.collision_collections)):
				if obj.rigid_body.collision_collections[i]:
					group = group | (1 << i)
			rigidBodyObject["group"] = group
			rigidBodyObject["mask"] = group
			jsonObject["rigid_bodys"].append(rigidBodyObject)


		if obj.rigid_body_constraint is not None:
			rigidBodyConstraintObject = {}
			constraintType = obj.rigid_body_constraint.type
			rigidBodyConstraintObject["type"] = constraintType
			rigidBodyConstraintObject["enabled"] = obj.rigid_body_constraint.enabled
			rigidBodyConstraintObject["disable_collisions"] = obj.rigid_body_constraint.disable_collisions
			rigidBodyConstraintObject["breaking_threshold"] = obj.rigid_body_constraint.breaking_threshold
			rigidBodyConstraintObject["use_breaking"] = obj.rigid_body_constraint.use_breaking #todo: replace by breaking thredhold value?
			rigidBodyConstraintObject["use_override_solver_iterations"] = obj.rigid_body_constraint.use_override_solver_iterations
			rigidBodyConstraintObject["solver_iterations"] = obj.rigid_body_constraint.solver_iterations

			object1 = obj.rigid_body_constraint.object1
			if object1 is not None:
				rigidBodyConstraintObject["object1"] = object1.name
				tOffset, rOffset = getOffsetFromAToB(object1, obj)
				rigidBodyConstraintObject["translation_offset_a"] = tOffset[0:3]
				rigidBodyConstraintObject["rotation_offset_a"] = rOffset[0:4]

			object2 = obj.rigid_body_constraint.object2
			if object2 is not None:
				rigidBodyConstraintObject["object2"] = object2.name
				tOffset, rOffset = getOffsetFromAToB(object2, obj)
				rigidBodyConstraintObject["translation_offset_b"] = tOffset[0:3]
				rigidBodyConstraintObject["rotation_offset_b"] = rOffset[0:4]
			
			if constraintType == 'HINGE':
				rigidBodyConstraintObject["use_limit_ang_z"] = obj.rigid_body_constraint.use_limit_ang_z
				rigidBodyConstraintObject["limit_ang_z_lower"] = obj.rigid_body_constraint.limit_ang_z_lower
				rigidBodyConstraintObject["limit_ang_z_upper"] = obj.rigid_body_constraint.limit_ang_z_upper
			elif constraintType == 'SLIDER':
				rigidBodyConstraintObject["use_limit_lin_x"] = obj.rigid_body_constraint.use_limit_lin_x
				rigidBodyConstraintObject["limit_lin_x_lower"] = obj.rigid_body_constraint.limit_lin_x_lower
				rigidBodyConstraintObject["limit_lin_x_upper"] = obj.rigid_body_constraint.limit_lin_x_upper
			elif constraintType == 'PISTON':
				rigidBodyConstraintObject["use_limit_lin_x"] = obj.rigid_body_constraint.use_limit_lin_x
				rigidBodyConstraintObject["limit_lin_x_lower"] = obj.rigid_body_constraint.limit_lin_x_lower
				rigidBodyConstraintObject["limit_lin_x_upper"] = obj.rigid_body_constraint.limit_lin_x_upper
				rigidBodyConstraintObject["use_limit_ang_x"] = obj.rigid_body_constraint.use_limit_ang_x
				rigidBodyConstraintObject["limit_ang_x_lower"] = obj.rigid_body_constraint.limit_ang_x_lower
				rigidBodyConstraintObject["limit_ang_x_upper"] = obj.rigid_body_constraint.limit_ang_x_upper
			elif constraintType == 'GENERIC' or constraintType == 'GENERIC_SPRING':
				rigidBodyConstraintObject["use_limit_lin_x"] = obj.rigid_body_constraint.use_limit_lin_x
				rigidBodyConstraintObject["limit_lin_x_lower"] = obj.rigid_body_constraint.limit_lin_x_lower
				rigidBodyConstraintObject["limit_lin_x_upper"] = obj.rigid_body_constraint.limit_lin_x_upper
				rigidBodyConstraintObject["use_limit_lin_y"] = obj.rigid_body_constraint.use_limit_lin_y
				rigidBodyConstraintObject["limit_lin_y_lower"] = obj.rigid_body_constraint.limit_lin_y_lower
				rigidBodyConstraintObject["limit_lin_y_upper"] = obj.rigid_body_constraint.limit_lin_y_upper
				rigidBodyConstraintObject["use_limit_lin_z"] = obj.rigid_body_constraint.use_limit_lin_z
				rigidBodyConstraintObject["limit_lin_z_lower"] = obj.rigid_body_constraint.limit_lin_z_lower
				rigidBodyConstraintObject["limit_lin_z_upper"] = obj.rigid_body_constraint.limit_lin_z_upper
				rigidBodyConstraintObject["use_limit_ang_x"] = obj.rigid_body_constraint.use_limit_ang_x
				rigidBodyConstraintObject["limit_ang_x_lower"] = obj.rigid_body_constraint.limit_ang_x_lower
				rigidBodyConstraintObject["limit_ang_x_upper"] = obj.rigid_body_constraint.limit_ang_x_upper
				rigidBodyConstraintObject["use_limit_ang_y"] = obj.rigid_body_constraint.use_limit_ang_y
				rigidBodyConstraintObject["limit_ang_y_lower"] = obj.rigid_body_constraint.limit_ang_y_lower
				rigidBodyConstraintObject["limit_ang_y_upper"] = obj.rigid_body_constraint.limit_ang_y_upper
				rigidBodyConstraintObject["use_limit_ang_z"] = obj.rigid_body_constraint.use_limit_ang_z
				rigidBodyConstraintObject["limit_ang_z_lower"] = obj.rigid_body_constraint.limit_ang_z_lower
				rigidBodyConstraintObject["limit_ang_z_upper"] = obj.rigid_body_constraint.limit_ang_z_upper
				if constraintType == 'GENERIC_SPRING':
					rigidBodyConstraintObject["use_spring_x"] = obj.rigid_body_constraint.use_spring_x
					rigidBodyConstraintObject["spring_stiffness_x"] = obj.rigid_body_constraint.spring_stiffness_x
					rigidBodyConstraintObject["spring_damping_x"] = obj.rigid_body_constraint.spring_damping_x
					rigidBodyConstraintObject["use_spring_y"] = obj.rigid_body_constraint.use_spring_y
					rigidBodyConstraintObject["spring_stiffness_y"] = obj.rigid_body_constraint.spring_stiffness_y
					rigidBodyConstraintObject["spring_damping_y"] = obj.rigid_body_constraint.spring_damping_y
					rigidBodyConstraintObject["use_spring_z"] = obj.rigid_body_constraint.use_spring_z
					rigidBodyConstraintObject["spring_stiffness_z"] = obj.rigid_body_constraint.spring_stiffness_z
					rigidBodyConstraintObject["spring_damping_z"] = obj.rigid_body_constraint.spring_damping_z
					rigidBodyConstraintObject["use_spring_ang_x"] = obj.rigid_body_constraint.use_spring_ang_x
					rigidBodyConstraintObject["spring_stiffness_ang_x"] = obj.rigid_body_constraint.spring_stiffness_ang_x
					rigidBodyConstraintObject["spring_damping_ang_x"] = obj.rigid_body_constraint.spring_damping_ang_x
					rigidBodyConstraintObject["use_spring_ang_y"] = obj.rigid_body_constraint.use_spring_ang_y
					rigidBodyConstraintObject["spring_stiffness_ang_y"] = obj.rigid_body_constraint.spring_stiffness_ang_y
					rigidBodyConstraintObject["spring_damping_ang_y"] = obj.rigid_body_constraint.spring_damping_ang_y
					rigidBodyConstraintObject["use_spring_ang_z"] = obj.rigid_body_constraint.use_spring_ang_z
					rigidBodyConstraintObject["spring_stiffness_ang_z"] = obj.rigid_body_constraint.spring_stiffness_ang_z
					rigidBodyConstraintObject["spring_damping_ang_z"] = obj.rigid_body_constraint.spring_damping_ang_z
					
			jsonObject["constraints"].append(rigidBodyConstraintObject)

	jsonText = json.dumps(jsonObject)
	f = open(path, 'w')
	f.write(jsonText)
	f.close()
	