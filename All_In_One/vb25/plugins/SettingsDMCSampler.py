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


TYPE= 'SETTINGS'

ID=   'SettingsDMCSampler'

NAME= 'DMC sampler'
DESC= "DMC sampler options"

PARAMS= (
	'time_dependent',
	'adaptive_amount',
	'adaptive_threshold',
	'adaptive_min_samples',
	'subdivs_mult',
)


def add_properties(rna_pointer):
	class SettingsDMCSampler(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsDMCSampler)

	rna_pointer.SettingsDMCSampler= PointerProperty(
		name= "DMC Sampler",
		type=  SettingsDMCSampler,
		description= "DMC Sampler settings"
	)

	SettingsDMCSampler.adaptive_threshold= FloatProperty(
		name= "Noise threshold",
		description= "Controls V-Ray's judgement of when a blurry value is \"good enough\" to be used",
		min= 0.0,
		max= 1.0,
		soft_min= 0.001,
		soft_max= 0.1,
		default= 0.01,
		precision= 3
	)

	SettingsDMCSampler.adaptive_min_samples= IntProperty(
		name= "Min samples",
		description= "The minimum number of samples that must be made before the early termination algorithm is used",
		min= 1,
		max= 1000,
		default= 8
	)

	SettingsDMCSampler.adaptive_amount= FloatProperty(
		name= "Adaptive amount",
		description= "A value of 1.0 means full adaptation; a value of 0.0 means no adaptation",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.85,
		precision= 2
	)

	SettingsDMCSampler.time_dependent= BoolProperty(
		name= "Time dependent",
		description= "This make the samping pattern change with time",
		default= 0
	)

	SettingsDMCSampler.subdivs_mult= FloatProperty(
		name= "Subdivs mult",
		description= "This will multiply all subdivs values everywhere during rendering",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		default= 1.0
	)



'''
  OUTPUT
'''
def write(bus):
	ofile=  bus['files']['scene']
	scene=  bus['scene']

	rna_pointer= getattr(scene.vray, ID)
	ofile.write("\n%s %s {" % (ID,ID))
	for param in PARAMS:
		value= getattr(rna_pointer, param)
		ofile.write("\n\t%s= %s;"%(param, p(value)))
	ofile.write("\n}\n")

