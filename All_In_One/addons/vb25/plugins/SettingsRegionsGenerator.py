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
import vb25.utils


TYPE= 'SETTINGS'
ID=   'SettingsRegionsGenerator'

NAME= 'Regions Generator'
DESC= "Regions generator settings"


def add_properties(parent_struct):
	class SettingsRegionsGenerator(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsRegionsGenerator)
	
	parent_struct.SettingsRegionsGenerator= PointerProperty(
		type= SettingsRegionsGenerator,
		name= NAME,
		description= DESC
	)

	SettingsRegionsGenerator.seqtype= EnumProperty(
		name= "Type",
		description= "Determines the order in which the regions are rendered",
		items=(
			('HILBERT',   "Hilbert",       ""),
			('TRIANGLE',  "Triangulation", ""),
			('IOSPIRAL',  "Spiral",        ""),
			('TBCHECKER', "Checker",       ""),
			('LRWIPE',    "Left-right",    ""),
			('TBWIPE',    "Top-bottom",    "") # 0
		),
		default= 'TRIANGLE'
	)

	SettingsRegionsGenerator.xymeans= EnumProperty(
		name= "XY means",
		description="XY means region width/height or region count",
		items=(
			('BUCKETS',  "Region count",  ""),
			('SIZE',     "Bucket W/H",    "") # 0
		),
		default= 'SIZE'
	)

	SettingsRegionsGenerator.reverse= BoolProperty(
		name= "Reverse",
		description= "Reverses the region sequence order",
		default= False
	)

	SettingsRegionsGenerator.lock_size= BoolProperty(
		name= "Lock size",
		description= "Lock bucket size (x = y)",
		default= True
	)

	SettingsRegionsGenerator.xc= IntProperty(
		name= "X",
		description= "Determines the maximum region width in pixels (Bucket W/H is selected) or the number of regions in the horizontal direction (when Region Count is selected)",
		min= 1,
		max= 1024,
		default= 32
	)

	SettingsRegionsGenerator.yc= IntProperty(
		name= "Y",
		description= "Determines the maximum region height in pixels (Bucket W/H is selected) or the number of regions in the vertical direction (when Region Count is selected)",
		min= 1,
		max= 1024,
		default= 32
	)


def write(bus):
	ofile=  bus['files']['scene']
	scene=  bus['scene']

	VRayScene= scene.vray
	SettingsRegionsGenerator= VRayScene.SettingsRegionsGenerator

	SEQTYPE= {
		'HILBERT':   5,
		'TRIANGLE':  4,
		'IOSPIRAL':  3,
		'TBCHECKER': 2,
		'LRWIPE':    1,
		'TBWIPE':    0,
	}

	XYMEANS= {
		'BUCKETS': 1,
		'SIZE':    0,
	}

	ofile.write("\nSettingsRegionsGenerator SettingsRegionsGenerator {")
	ofile.write("\n\txc= %i;" % SettingsRegionsGenerator.xc)
	if SettingsRegionsGenerator.lock_size:
		ofile.write("\n\tyc= %i;" % SettingsRegionsGenerator.xc)
	else:
		ofile.write("\n\tyc= %i;" % SettingsRegionsGenerator.yc)
	ofile.write("\n\treverse= %i;" % SettingsRegionsGenerator.reverse)
	ofile.write("\n\tseqtype= %i;" % SEQTYPE[SettingsRegionsGenerator.seqtype])
	ofile.write("\n\txymeans= %i;" % XYMEANS[SettingsRegionsGenerator.xymeans])
	ofile.write("\n}\n")
