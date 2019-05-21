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

ID=   'SettingsDefaultDisplacement'

NAME= 'Default displacement'
DESC= "Default displacement options."

PARAMS= (
	'override_on',
	'edgeLength',
	'viewDependent',
	'maxSubdivs',
	'tightBounds',
	'amount',
	'relative',
)


def add_properties(rna_pointer):
	class SettingsDefaultDisplacement(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsDefaultDisplacement)

	rna_pointer.SettingsDefaultDisplacement= PointerProperty(
		name= "Default Displacement",
		type=  SettingsDefaultDisplacement,
		description= "Default displacement settings"
	)

	SettingsDefaultDisplacement.override_on= BoolProperty(
		name= "Override",
		description= "Override settings globally",
		default= False
	)

	SettingsDefaultDisplacement.edgeLength= FloatProperty(
		name= "Edge length",
		description= "Max. height",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 4
	)

	SettingsDefaultDisplacement.viewDependent= BoolProperty(
		name= "View dependent",
		description= "Determines if view-dependent tesselation is used",
		default= True
	)

	SettingsDefaultDisplacement.maxSubdivs= IntProperty(
		name= "Max subdivs",
		description= "Determines the maximum subdivisions for a triangle of the original mesh",
		min= 0,
		max= 2048,
		soft_min= 0,
		soft_max= 1024,
		default= 256
	)

	SettingsDefaultDisplacement.tightBounds= BoolProperty(
		name= "Tight bounds",
		description= "When this is on, initialization will be slower, but tighter bounds will be computed for the displaced triangles making rendering faster",
		default= True
	)

	SettingsDefaultDisplacement.amount= FloatProperty(
		name= "Amount",
		description= "Determines the displacement amount for white areas in the displacement map",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	SettingsDefaultDisplacement.relative= BoolProperty(
		name= "Relative",
		description= "TODO",
		default= False
	)


def write(bus):
	ofile=  bus['files']['scene']
	scene=  bus['scene']

	rna_pointer= getattr(scene.vray, ID)
	ofile.write("\n%s %s {" % (ID,ID))
	for param in PARAMS:
		value= getattr(rna_pointer, param)
		ofile.write("\n\t%s= %s;"%(param, p(value)))
	ofile.write("\n}\n")

