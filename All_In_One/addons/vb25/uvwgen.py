'''

  V-Ray/Blender

  http://vray.cgdo.ru

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Blender modules '''
import bpy

''' vb modules '''
from vb25.utils import *
from vb25.plugins import *


def write_UVWGenPlanarWorld(bus):
	scene   = bus['scene']
	ofile   = bus['files']['textures']
	texture = bus['mtex']['texture']

	VRayTexture = texture.vray
	VRaySlot    = texture.vray_slot

	uvwgen = "UWVGPW%s" % bus['mtex']['name']

	ob = get_orco_object(scene, bus['node']['object'], VRayTexture)

	ofile.write("\nUVWGenPlanarWorld %s {" % uvwgen)
	if ob:
		uvw_transform = ob.matrix_world.copy().inverted()
		ofile.write("\n\tuvw_transform= %s; // Object: %s" % (a(scene, transform(uvw_transform)), ob.name))
	ofile.write("\n}\n")

	return uvwgen


def write_UVWGenProjection(bus):
	TYPE= {
		'NONE':   0,
		'FLAT':   1,
		'SPHERE': 2,
		'TUBE':   3,
		'BALL':   4,
		#'CUBE':   5, # cubic
		'CUBE':   6,  # triplanar (looks like Cube actually)
		'TRI':    6,  # triplanar
		'PERS':   8,
	}

	scene= bus['scene']
	ofile= bus['files']['textures']

	texture= bus['mtex']['texture']

	VRayTexture= texture.vray
	VRaySlot=    texture.vray_slot

	uvwgen= "UVP%s" % (bus['mtex']['name'])

	ob= get_orco_object(scene, bus['node']['object'], VRayTexture)

	ofile.write("\nUVWGenProjection %s {" % uvwgen)
	ofile.write("\n\ttype= %d;" % TYPE[VRayTexture.mapping])
	if ob:
		uvw_transform= mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X') # To match Blender mapping
		uvw_transform*= ob.matrix_world.copy().inverted()                    # To remove object transfrom
		ofile.write("\n\tuvw_transform= %s; // Object: %s" % (a(scene, transform(uvw_transform)), ob.name))
	# Add:
	#  - camera_settings
	#  - camera_view
	ofile.write("\n}\n")

	return uvwgen


def write_UVWGenChannel(bus):
	ofile = bus['files']['textures']
	sce   = bus['scene']

	texture = bus['mtex']['texture']
	slot    = bus['mtex'].get('slot')

	uvw_name = "UVC%s" % (bus['mtex']['name'])

	VRayExporter = sce.vray.exporter

	VRaySlot    = texture.vray_slot
	VRayTexture = texture.vray

	uvwgen = None
	if VRayTexture.texture_coords == 'ORCO':
		uvwgen = write_UVWGenProjection(bus)
	elif VRayTexture.texture_coords == 'WORLD':
		uvwgen = write_UVWGenPlanarWorld(bus)

	ofile.write("\nUVWGenMayaPlace2dTexture %s {" % uvw_name)
	if slot:
		if bus['preview']:
			ofile.write('\n\tuvw_channel=0;')
		else:
			if hasattr(slot, 'uv_layer') and slot.uv_layer:
				ofile.write('\n\tuv_set_name="%s";' % slot.uv_layer)
			else:
				ofile.write('\n\tuv_set_name="UVMap";')
			ofile.write("\n\ttranslate_frame_u=%.3f;" % slot.offset[0])
			ofile.write("\n\ttranslate_frame_v=%.3f;" % slot.offset[1])
			# ofile.write("\n\tcoverage_u=%.3f;" % slot.scale[0])
			# ofile.write("\n\tcoverage_v=%.3f;" % slot.scale[1])
	else:
		ofile.write('\n\tuvw_channel=0;')
	ofile.write("\n\tmirror_u=%d;" % VRayTexture.mirror_u)
	ofile.write("\n\tmirror_v=%d;" % VRayTexture.mirror_v)
	ofile.write("\n\trepeat_u=%.3f;" % VRayTexture.tile_u)
	ofile.write("\n\trepeat_v=%.3f;" % VRayTexture.tile_v)
	ofile.write("\n\trotate_frame=%.3f;" % VRaySlot.texture_rot)
	# Optional UVWGen from which the initial uvw coordinates
	# will be taken, instead of the surface point
	if uvwgen:
		ofile.write("\n\tuvwgen=%s;" % uvwgen)
	ofile.write("\n}\n")

	return uvw_name


def write_UVWGenEnvironment(bus):
	MAPPING_TYPE= {
		'SPHERE':  'spherical',
		'ANGULAR': 'angular',
		'SCREEN':  'screen',
		'TUBE':    'max_cylindrical',
		'CUBIC':   'cubic',
		'MBALL':   'mirror_ball',
	}

	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvw_name= "UVE%s" % (tex_name)

	VRayTexture= texture.vray
	VRaySlot=    texture.vray_slot

	uvw_matrix=  mathutils.Matrix.Rotation(VRaySlot.texture_rotation_h, 4, 'Z')
	uvw_matrix*= mathutils.Matrix.Rotation(VRaySlot.texture_rotation_v, 4, 'Y')
	#uvw_matrix*= mathutils.Matrix.Rotation(VRaySlot.texture_rotation_w, 4, 'X')

	ofile.write("\nUVWGenEnvironment %s {" % uvw_name)
	ofile.write("\n\tmapping_type= \"%s\";" % MAPPING_TYPE[VRayTexture.environment_mapping])
	if VRayTexture.environment_mapping not in ('SCREEN'):
		ofile.write("\n\tuvw_matrix= %s;" % transform(uvw_matrix))
	else:
		ofile.write("\n\tuvw_transform= %s;" % transform(uvw_matrix))
	ofile.write("\n\twrap_u=1;")
	ofile.write("\n\twrap_v=1;")
	ofile.write("\n\tcrop_u=0;")
	ofile.write("\n\tcrop_v=0;")
	ofile.write("\n}\n")

	return uvw_name


def write_uvwgen(bus):
	slot=    bus['mtex']['slot']
	texture= bus['mtex']['texture']

	if type(slot) is bpy.types.WorldTextureSlot or ('dome' in bus['mtex'] and bus['mtex']['dome']):
		return write_UVWGenEnvironment(bus)

	else:
		VRayTexture= texture.vray

		uvwgen= write_UVWGenChannel(bus)

		# Cache uvwgen under texture name
		bus['cache']['uvwgen'][ bus['mtex']['name'] ]= uvwgen

		# We need to pass normal uvwgen to BRDFBump
		if 'material' in bus:
			bus['material']['normal_uvwgen'] = uvwgen
			bus['material']['bump_uvwgen']   = uvwgen
		return uvwgen
