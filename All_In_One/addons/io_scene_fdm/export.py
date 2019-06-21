'''
Write aircraft data to file(s)

@author: tom
'''
import math
from collections import OrderedDict
from mathutils import Euler, Matrix, Vector
from os import path

ft2m = 0.3048

import bpy, time, datetime
from bpy_extras.io_utils import ExportHelper
from . import aircraft, util

class AnimationsFGFS:
	'''Exporter for flightgear animations'''

	def __init__(self):
		self.model = util.XMLDocument('PropertyList')
		self.obs_transparent = []

	def save(self, filename):

		# Let transparent objects use the model-transparent effect to be compatible
		# with Rembrandt rendering of FlightGear
		if len(self.obs_transparent):
			eff = self.model.createChild('effect')
			eff.createPropChild('inherits-from', 'Effects/model-transparent')
			for ob in self.obs_transparent:
				eff.createPropChild('object-name', ob.name)

		self.model.createChild('path', path.basename(filename) + '.ac')

		f = open(filename + '.model.xml', 'w')
		self.model.writexml(f, "", "\t", "\n")
		f.close()

	def addGear(self, gear, i):
		'''
		@param ob_strut	Gear data
		@param i				Gear index
		'''
		node = 'gear/gear['+str(i)+']/'

		# Compression
		self.addAnimation(
			'translate',
			gear['ob'],
			node + 'compression-norm',
			axis = [0,0,1],
			factor = ft2m, # TODO check yasim
			offset = -gear['current-compression']
		)

		# Steering
		if gear['gear'].steering_type == 'STEERABLE':
			try:
				rotate_obj = bpy.data.objects[ gear['gear'].rotate_parent ]
			except KeyError:
				rotate_obj = gear['obj']
			self.addAnimation(
				'rotate',
				rotate_obj,
				node + 'steering-norm',
				axis = [0,0,-1],
				factor = math.degrees(gear['gear'].max_steer)
			)
		else:
			# TODO check CASTERED
			pass

		# Wheel spin
		dist = gear['wheels'][0]['diameter'] * math.pi
		self.addAnimation(
			'spin',
			[w['ob'] for w in gear['wheels']],
			node + 'rollspeed-ms',
			axis = [0,-1,0],
			factor = 60 / dist, # dist per revolution to rpm
			offset = -gear['current-compression']
		)

		# Tyre smoke
		m = self.model.createChild('model')
		m.createPropChild('path', "Aircraft/Generic/Effects/tyre-smoke.xml")
		p = m.createChild('overlay').createChild('params')
		p.createPropChild('property', node + 'tyre-smoke')
		m.createVectorChild('offsets', gear['location'], '-m')

	def addAnimation(	self,	anim_type, obs,
											prop = None,
											center = None,
											axis = None,
											factor = None,
											offset = None,
											table = None ):
		'''
		@param anim_type	Animation type
		@param obs				Single or list of objects names to be animated
		@param prop				Property used to control animation
		'''
		a = self.model.createChild('animation')
		a.createPropChild('type', anim_type)

		# ensure it's a list
		if not isinstance(obs, list):
			obs = [obs]
		for ob in obs:
			a.createPropChild('object-name', ob.name)

		if prop != None:
			a.createPropChild('property', prop)

		if factor != None:
			a.createPropChild('factor', factor)

		if offset != None:
			tag = 'offset'
			if anim_type == 'translate':
				tag += '-m'
			elif anim_type == 'rotate':
				tag += '-deg'
			a.createPropChild(tag, offset)

		if table != None:
			tab = a.createChild('interpolation')
			for entry in table:
				e = tab.createChild('entry')
				e.createPropChild('ind', entry[0])
				e.createPropChild('dep', entry[1])

		if anim_type in ['rotate', 'spin']:
			a.createCenterChild(center if center != None \
												       else obs[0].matrix_world.to_translation())

		if axis != None:
			a.createVectorChild('axis', axis)

		return a

	def addTransparentObject(self, ob):
		self.obs_transparent.append(ob)

class Exporter(bpy.types.Operator, ExportHelper):
	'''Export to Flightgear FDM (.xml)'''
	bl_idname = 'export_scene.fdm'
	bl_label = 'Export Flightgear FDM'
	bl_options = {'PRESET'}

	filename_ext = '.xml'

	def parseLevel( self,
									objects,
									ignore_select = False,
									local_transform = Matrix() ):
		'''
		Parse a level in the object hierarchy
		'''
		for ob in objects:

			# Objects from libraries don't have the select flag set even if their
			# proxy is selected. We therefore consider all objects from libraries as
			# selected, as the only possibility to get them considered is if their
			# proxy should be exported.
			if ob.is_visible(self.context.scene) and (ob.select or ignore_select):

				self.exportObject(ob, local_transform)

				# We need to check for dupligroups first as every type of object can be
				# converted to a dupligroup without removing the data from the old type.
				if ob.dupli_type == 'GROUP':
					children = [child for child in ob.dupli_group.objects
					                            if not child.parent
					                            or not child.parent.name in ob.dupli_group.objects]
					self.parseLevel(children, True, local_transform * ob.matrix_world)

			if len(ob.children):
				self.parseLevel(ob.children, ignore_select, local_transform)

	def exportObject(self, ob, tf):
		self.checkTransparency(ob)

		if ob.fgfs.type == 'STRUT':
			self.exportGear(ob, tf)
		elif ob.fgfs.type == 'PICKABLE':
			self.exportPickable(ob)
		elif ob.type == 'LAMP':
			self.exportLight(ob, tf)

		self.exportDrivers(ob, tf)

		if ob.constraints:
			self.constraint_objs.append(ob)
		if ob.parent_type == 'BONE':
			self.bone_objs.setdefault(ob.parent,[]).append(ob)

		# store world matrix (eg. needed for tracking constraints)
		self.world_matrices[ob.name] = tf * ob.matrix_world

	def execute(self, context):
		t = time.mktime(datetime.datetime.now().timetuple())

		self.device_root = ""
		self.gear_index = 0
		self.exp_anim = AnimationsFGFS()
		self.ground_reactions = util.XMLDocument('ground_reactions')
		self.context = context
		self.constraint_objs = []
		self.bone_objs = OrderedDict()
		self.world_matrices = {}

		self.parseLevel([ob for ob in bpy.data.objects if ob.parent == None and not ob.library])
		self.exportConstraints()
		self.exportBones()

		f = open(self.filepath, 'w')
		self.ground_reactions.writexml(f, "", "\t", "\n")
		f.close()

		file_name = path.splitext(self.filepath)
		self.exp_anim.save(file_name[0])

		t = time.mktime(datetime.datetime.now().timetuple()) - t
		print('Finished exporting in', t, 'seconds')

		return {'FINISHED'}

	def exportGear(self, ob, tf):
		gear = aircraft.gear.parse(ob)
		c = self.ground_reactions.createChild('contact')
		c.setAttribute('type', 'BOGEY')
		c.setAttribute('name', ob.name)

		l = c.createVectorChild('location', gear['location'])
		l.setAttribute('unit', 'M')

		c.createPropChild('static_friction', 0.8)
		c.createPropChild('dynamic_friction', 0.5)
		c.createPropChild('rolling_friction', 0.02)

		strut = gear['strut']
		c.createPropChild('spring_coeff', strut.spring_coeff, 'N/M')
		c.createPropChild('damping_coeff', strut.damping_coeff, 'N/M/SEC')

		if gear['gear'].steering_type == 'FIXED':
			max_steer = 0
		elif gear['gear'].steering_type == 'CASTERED':
			max_steer = 360
		else:
			max_steer = gear['gear'].max_steer
		c.createPropChild('max_steer', max_steer, 'DEG')

		c.createPropChild('brake_group', gear['gear'].brake_group)
		c.createPropChild('retractable', 1)

		self.exp_anim.addGear(gear, self.gear_index)
		self.gear_index += 1

	def exportDrivers(self, ob, tf):

		if not ob.animation_data:
			return

		matrix_world = tf * ob.matrix_world
		# object center in world coordinates
		center = matrix_world.to_translation()

		[loc, rot, scale] = ob.matrix_basis.decompose()
		rot = rot.to_euler()

		for driver in ob.animation_data.drivers:
			# get the animation axis in world coordinate frame
			# (vector from center to p2)
			p2 = Vector([0,0,0])
			p2[ driver.array_index ] = 1

			axis = matrix_world * p2 - center
			prop = None
			factor = 1
			offset = 0
			table = None

			for var in driver.driver.variables:
				if var.type == 'SINGLE_PROP':
					if len(var.targets) != 1:
						raise RuntimeError('SINGLE_PROP: wrong target count', var.targets)
				else:
					raise RuntimeError('Exporting ' + var.type + ' not supported yet!')

				tar = var.targets[0]
				if tar.id_type in ['OBJECT', 'SCENE', 'WORLD']:
					prop = var.targets[0].data_path.strip('["]')

			if not prop:
				raise RuntimeError('No property!')

			if len(driver.keyframe_points):
				cur_val = getattr(ob, driver.data_path)[driver.array_index]
				table = [[k.co[0], k.co[1] - cur_val] for k in driver.keyframe_points]
			else:
				for mod in driver.modifiers:
					if mod.type != 'GENERATOR':
						print('Driver: modifier type=' + mod.type + ' not supported yet!')
						continue

					if mod.poly_order != 1:
						print('Driver: polyorder != 1 not supported yet!')
						continue

					factor = mod.coefficients[1]

					# we don't need to get the offset coefficient as blender already has
					# applied it to the model for us. We need just to remove the offset
					# introduced by the current value of the property (if not zero)
					offset = -tar.id[prop] * factor

			if driver.data_path == 'rotation_euler':
				if table:
					table = [[k[0], round(math.degrees(k[1]), 1)] for k in table]
				else:
					factor = math.degrees(factor)
					offset = math.degrees(offset)
				anim_type = 'rotate'

				# compensate for rotations applied on export
				inv_rot = [0, 0, 0]
				for i in range(3):
					if i < driver.array_index:
						inv_rot[i] = -rot[i]
				axis = matrix_world * Euler(inv_rot, 'ZYX').to_matrix().to_4x4() * p2 - center

			elif driver.data_path == 'location':
				anim_type = 'translate'
			elif driver.data_path == 'hide':
			  anim_type = 'select'
			else:
				print('Exporting ' + driver.data_path + ' not supported yet!')
				continue

			# TODO check for real gear index
			prop = prop.replace('/gear/', 'gear/gear[0]/')

			if table:
				self.exp_anim.addAnimation(
					anim_type,
					ob,
					center = center,
					axis = axis,
					prop = prop,
					table = table
				)
			else:
				self.exp_anim.addAnimation(
					anim_type,
					ob,
					prop = prop,
					center = center,
					axis = axis,
					factor = factor,
					offset = offset
				)


	def exportConstraints(self):
		for ob in self.constraint_objs:
			for c in ob.constraints:
				if c.influence != 1.0:
					print('Constraint influence != 1.0 ignored.')

				if c.type == 'LOCKED_TRACK':
					self.exportLockedTrack(ob, c)
				else:
					print('Exporting ' + c.type + ' not supported yet!')

	def exportBones(self):
		for arm, obs in self.bone_objs.items():
			print('export bone: ' + arm.name + ", " + str([ob.name for ob in obs]))

			bones = arm.pose.bones
			if len(bones) != 2:
				print("Exporting armature with != 2 bones not supported!")
				return
			if    len(bones[0].constraints) != 0 \
				 or len(bones[1].constraints) != 1 \
				 or bones[1].constraints[0].type != 'IK':
				print("Exporting armature: only single IK constraint on second bone supported!")
				return

			ik = bones[1].constraints[0]
			target = ik.target
			target_center = self.world_matrices[target.name].to_translation()
			print(target.type)
			while target and target.type not in ['MESH', 'LATTICE', 'SURFACE', 'CURVE', 'GROUP']:
				print('get parent: ' + target.name)
				target = target.parent
			if not target:
				print("Exporting armature: no valid IK target (parent) found!")
				return

			ob = None
			slave_name = None
			for child in arm.children:
				print('child: ' + child.name + ' -> ' + child.parent_bone)
				if child.parent_bone == bones[0].name:
					ob = child
				elif child.parent_bone == bones[1].name:
					slave_name = child.name

			matrix_world = self.world_matrices[arm.name]
			matrix_world_3x3 = matrix_world.to_3x3()
			slave_center = (matrix_world * bones[1].matrix).to_translation()

			# Calculate lock axis based on the given rotation applied by blender. This will only work
			# if there is already a non-zero rotation applied. Straight bones in a line will not work
			# without a lock axis set manually.
			lock_axis_calc = (bones[1].tail - bones[0].head).cross(bones[0].tail - bones[0].head)

			lock = [[b.lock_ik_x, b.lock_ik_y, b.lock_ik_z] for b in bones]
			if not any(lock[0]):
				lock_axis = lock_axis_calc
			else:
				if not lock[0][0]:
					lock_axis = bones[0].x_axis
				elif not lock[0][1]:
					lock_axis = bones[0].y_axis
				else:
					lock_axis = bones[0].z_axis

				# compare with the rotation calculated on what rotation blender already has applied
				if lock_axis * lock_axis_calc < 0:
					# invert if blender has rotated into the other direction. I don't exactly know how
					# blender determines the direction of the rotation, but there are some rules which
					# somehow try to optimize the rotation.
					lock_axis *= -1

			# compensate for current effect of constraint on object
			lock_axis = matrix_world_3x3 * lock_axis.normalized()
			track_axis = matrix_world_3x3 * bones[0].vector.normalized()

			anim = self.exp_anim.addAnimation('locked-track', ob)
			anim.createCenterChild('center', matrix_world.to_translation())
			anim.createVectorChild('lock-axis', lock_axis)
			anim.createVectorChild('track-axis', track_axis)
			anim.createPropChild('target-name', target.name)
			anim.createCenterChild('target-center', target_center)

			if slave_name:
				anim.createPropChild('slave-name', slave_name)
			anim.createCenterChild('slave-center', slave_center)

			# Let slave rotate around two axis if 2 axis are unlocked.
			if lock[1].count(False) == 2:
				# TODO check if correct axis are locked
				anim.createPropChild('slave-dof', 2)

	def axisFromString(self, name):
		if name.endswith('_X'):
			axis = Vector([1,0,0])
		elif name.endswith('_Y'):
			axis = Vector([0,1,0])
		elif name.endswith('_Z'):
			axis = Vector([0,0,1])
		else:
			raise RuntimeError('unknown axis: ' + name)

		if name[:-2].endswith('NEGATIVE'):
			return -axis
		else:
			return axis

	def exportLockedTrack(self, ob, c):
		print(ob.name, c)
		if not c.target:
			print('Constraint target empty!')
			return
		if c.subtarget != '':
			print('Constraint subtarget/Vertex Group ignored.')

		matrix_world = self.world_matrices[ob.name]
		matrix_local = ob.matrix_local.to_3x3()

		# compensate for current effect of constraint on object
		lock_axis = matrix_local * self.axisFromString(c.lock_axis)
		track_axis = matrix_local * self.axisFromString(c.track_axis)

		anim = self.exp_anim.addAnimation('locked-track', ob)
		anim.createCenterChild('center', matrix_world.to_translation())
		anim.createVectorChild('lock-axis', lock_axis)
		anim.createVectorChild('track-axis', track_axis)
		anim.createPropChild('target-name', c.target.name)
		anim.createCenterChild('target-center', self.world_matrices[c.target.name].to_translation())

	def exportPickable(self, ob):
		props = ob.fgfs.clickable

		action = self.exp_anim.addAnimation('pick', ob).createChild('action')
		action.createChild('button', 0)
		binding = action.createChild('binding')
		binding.createChild('command', props.action)
		prop = props.prop
		if len(prop) == 0:
			prop = '/controls/instruments/'+ob.parent.name+'/input'
		binding.createChild('property', prop)
		if props.action in ['property-assign']:
			binding.createChild('value', ob.name)

	def exportLight(self, ob, tf):
		if ob.data.type != 'SPOT':
			return

		m = self.exp_anim.model.createChild('model')
		m.createPropChild('path', "Aircraft/Generic/Lights/light-cone.xml")
		m.createPropChild('name', ob.name)
		o = m.createVectorChild('offsets', ob.matrix_world.to_translation(),'-m')
		o.createPropChild('pitch-deg', -5)
		p = m.createChild('overlay').createChild('params')
		p.createPropChild('switch', "/controls/lighting/landing-lights")

	def checkTransparency(self, ob):
		is_transparent = False
		for slot in ob.material_slots:
			if slot.material and slot.material.use_transparency:
				is_transparent = True
				break

		if is_transparent:
			self.exp_anim.addTransparentObject(ob)
