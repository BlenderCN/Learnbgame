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
from bpy.props import *

''' vb modules '''
from vb25.utils import *
from vb25.ui import ui


TYPE= 'CAMERA'
ID=   'Camera'

NAME= 'Camera'
DESC= "V-Ray camera settings"

PARAMS= (
)


def add_properties(rna_pointer):
	rna_pointer.mode= EnumProperty(
		name= "Mode",
		description= "Camera mode",
		items=(
			('NORMAL',   "Normal",   ""),
			('PHYSICAL', "Physical", "")
		),
		default= 'NORMAL'
	)

	rna_pointer.override_fov= BoolProperty(
		name= "Override FOV",
		description= "Override FOV (if you need FOV > 180)",
		default= False
	)

	rna_pointer.use_camera_loop= BoolProperty(
		name= "Use in \"Camera loop\"",
		description= "Use camera in \"Camera loop\"",
		default= False
	)

	rna_pointer.fov= FloatProperty(
		name= "FOV",
		description= "Field of vision",
		min= 0.0,
		max= math.pi * 2,
		soft_min= 0.0,
		soft_max= math.pi * 2,
		subtype= 'ANGLE',
		precision= 2,
		default= math.pi / 4
	)


	'''
	  Hide From View
	'''
	rna_pointer.hide_from_view= BoolProperty(
		name= "Hide From View",
		description= "Hide objects from current view",
		default= False
	)

	rna_pointer.hf_all= BoolProperty(
		name= "Hide from everything",
		description= "Hide objects completely",
		default= False
	)

	rna_pointer.hf_all_auto= BoolProperty(
		name= "Hide from everything (automatic)",
		description= "Create group with name \"hf_<camera-name>\"",
		default= False
	)

	rna_pointer.hf_all_objects= StringProperty(
		name= "Objects",
		description= "Objects to hide completely: name{;name;etc}",
		default= ""
	)

	rna_pointer.hf_all_groups= StringProperty(
		name= "Groups",
		description= "Groups to hide completely: name{;name;etc}",
		default= ""
	)

	for key in ('camera','gi','reflect','refract','shadows'):
		setattr(rna_pointer, 'hf_%s' % key, bpy.props.BoolProperty(
			name= "Hide from %s" % key,
			description= "Hide objects from %s" % key,
			default= False)
		)

		setattr(rna_pointer, 'hf_%s_auto' % key, bpy.props.BoolProperty(
			name= "Auto",
			description= "Hide objects automaically from %s" % key,
			default= False)
		)

		setattr(rna_pointer, 'hf_%s_objects' % key, bpy.props.StringProperty(
			name= "Objects",
			description= "Objects to hide from %s" % key,
			default= "")
		)

		setattr(rna_pointer, 'hf_%s_groups' % key, bpy.props.StringProperty(
			name= "Groups",
			description= "Groups to hide from %s" % key,
			default= "")
		)
