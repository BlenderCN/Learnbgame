'''
Parse a gear from a blender object

@author: tom
'''

from . import wheel
from .. import util
from mathutils import Vector

def parse(ob):
	print("Parse Gear: "+ob.name)

	comp = ob.constraints.get('Compression')
	if not comp:
		return 'Warning: No compression limit...'
	
	if comp.type != 'LIMIT_LOCATION':
		return 'Warning: Wrong type for compression limit...'
	
	if not (		 not comp.use_min_x and not comp.use_max_x
					 and not comp.use_min_y and not comp.use_max_y
					 and		 comp.use_min_z and		 comp.use_max_z ):
		return 'Warning: Only use z-axis!'
	
	if comp.owner_space != 'LOCAL':
		return 'Warning: Set compression limit using local space'
	
	# check for wheels and contact point
	wheels = []
	
	for child in util.getAllChildren(ob, 'WHEEL'):
		wheels.append(wheel.parse(child))
	
	num_wheels = len(wheels)	
	if not num_wheels:
		return 'Warning: No wheel attached as child.'
	
	contact_point = Vector()
	for w in wheels:
		contact_point += Vector(w['contact_point'])
	contact_point /= num_wheels
	
	# move contact point to lowest possible point (== max extention)
	compression = ob.location.z - comp.min_z
	contact_point.z -= compression
	
	contact_point = ob.matrix_world * contact_point
	
	# calculate compression
	comp_dist = comp.max_z - comp.min_z
	print('Compression: %.3fm - %d Wheels - contact=(%.3f|%.3f|%.3f)' % (comp_dist, num_wheels, contact_point[0], contact_point[1], contact_point[2]))
	
	# collect all data
	gear = {
		'ob': ob,
		'wheels': wheels,
		'location': contact_point,
		'current-compression': compression,
		'gear': ob.fgfs.gear,
		'strut': ob.data.fgfs.strut
	}

	return gear