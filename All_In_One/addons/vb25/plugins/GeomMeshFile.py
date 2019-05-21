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


TYPE= 'GEOMETRY'
ID=   'GeomMeshFile'

NAME= 'Proxy'
DESC= "VRayProxy settings"

PARAMS= (
	'filter_blur'
)

def add_properties(rna_pointer):
	class GeomMeshFile(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(GeomMeshFile)

	rna_pointer.GeomMeshFile= PointerProperty(
		name= "V-Ray Proxy",
		type=  GeomMeshFile,
		description= "V-Ray proxy settings"
	)

	GeomMeshFile.use= BoolProperty(
		name= "Use Proxy",
		description= "Use proxy mesh",
		default= False
	)

	GeomMeshFile.file= StringProperty(
		name= "File",
		subtype= 'FILE_PATH',
		description= "Proxy file"
	)

	GeomMeshFile.anim_type= EnumProperty(
		name= "Animation type",
		description= "Proxy animation type",
		items= (
			('LOOP',     "Loop",      ""),
			('ONCE',     "Once",      ""),
			('PINGPONG', "Ping-pong", ""),
			('STILL',    "Still",     "")
		),
		default= 'LOOP'
	)

	GeomMeshFile.mode= EnumProperty(
		name= "Mode",
		description= "Proxy creation mode",
		items= (
			('NONE',    "None",        "Don\'t attach proxy"),
			('NEW',     "New object",  "Attach proxy to new object"),
			('THIS',    "This object", "Attach proxy to this object"),
			('REPLACE', "Replace",     "Replace this object with proxy"),
		),
		default= 'NONE'
	)

	GeomMeshFile.anim_speed= FloatProperty(
		name= "Speed",
		description= "Animated proxy playback speed",
		min= 0.0,
		max= 1000.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 1.0
	)

	GeomMeshFile.anim_offset= FloatProperty(
		name= "Offset",
		description= "Animated proxy initial frame offset",
		min= -1000.0,
		max= 1000.0,
		soft_min= -10.0,
		soft_max= 10.0,
		default= 0.0
	)

	GeomMeshFile.scale= FloatProperty(
		name= "Scale",
		description= "Size scaling factor",
		min= 0.0,
		max= 1000.0,
		soft_min= 0.0,
		soft_max= 2.0,
		default= 1.0
	)

	GeomMeshFile.apply_transforms= BoolProperty(
		name= "Apply transform",
		description= "Apply rotation, location and scale",
		default= False
	)

	GeomMeshFile.add_suffix= BoolProperty(
		name= "Add suffix",
		description= "Add \"_proxy\" suffix to object and mesh names",
		default= True
	)

	GeomMeshFile.dirpath= StringProperty(
		name= "Path",
		subtype= 'DIR_PATH',
		description= "Proxy generation directory",
		default= "//proxy"
	)

	GeomMeshFile.filename= StringProperty(
		name= "Name",
		subtype= 'NONE',
		description= "Proxy file name. If empty object's name is used",
		default= ""
	)

	GeomMeshFile.animation= BoolProperty(
		name= "Animation",
		description= "Animated proxy",
		default= False
	)

	GeomMeshFile.animation_range= EnumProperty(
		name= "Animation range",
		description= "Animation range type",
		items= (
			('MANUAL', "Manual", "Set manually"),
			('SCENE',  "Scene",  "Get from scene")
		),
		default= 'SCENE'
	)

	GeomMeshFile.add_velocity= BoolProperty(
		name= "Add velocity",
		description= "This makes it possible to add motion blur to the final animation. However exporting this extra information takes longer. If you are not going to need motion blur it makes sense to disable this option",
		default= False
	)

	GeomMeshFile.frame_start= IntProperty(
		name= "Start frame",
		description= "Proxy generation start frame",
		min= 1,
		max= 1000,
		soft_min= 1,
		soft_max= 250,
		default= 1
	)

	GeomMeshFile.frame_end= IntProperty(
		name= "End frame",
		description= "Proxy generation end frame",
		min= 1,
		max= 1000,
		soft_min= 1,
		soft_max= 250,
		default= 250
	)


def write(bus):
	ANIM_TYPE= {
		'LOOP'     : 0,
		'ONCE'     : 1,
		'PINGPONG' : 2,
		'STILL'    : 3,
	}

	ofile= bus['files']['nodes']
	scene= bus['scene']
	ob=    bus['node']['object']

	VRayData= ob.data.vray

	if hasattr(VRayData,'GeomMeshFile'):
		GeomMeshFile= VRayData.GeomMeshFile

		if not GeomMeshFile.file:
			debug(scene, "Object: %s => Proxy file is not set!" % (ob.name), error= True)
			return bus['node']['geometry']

		proxy_filepath= os.path.normpath(bpy.path.abspath(GeomMeshFile.file))

		# if PLATFORM == 'linux':
		# 	proxy_filepath= proxy_filepath.replace('\\', '/')

		# TODO: fix '\' on *nix
		# if not os.path.exists(proxy_filepath):
		# 	debug(scene, "Object: %s => Proxy file doesn\'t exist! [%s]" % (ob.name, proxy_filepath), error= True)
			# return bus['node']['geometry']

		proxy_filename= os.path.basename(proxy_filepath)[:-7]
		proxy_name= "PR%s" % clean_string(proxy_filename)

		if GeomMeshFile.anim_type not in ('STILL'):
			proxy_name= "OB%sPR%s" % (clean_string(ob.data.name),
									  clean_string(proxy_filename))

		if not append_unique(bus['cache']['proxy'], proxy_name):
			bus['node']['geometry']= proxy_name
			return proxy_name

		ofile.write("\nGeomMeshFile %s {" % proxy_name)
		# if PLATFORM == 'linux': # This is a hack to allow teams using both Windows and Linux (back-slash problem)
		# 	ofile.write("\n\tfile= \"%s\";" % get_full_filepath(bus, ob, GeomMeshFile.file.replace('\\','/')))
		# else:
		# 	ofile.write("\n\tfile= \"%s\";" % get_full_filepath(bus, ob, GeomMeshFile.file))
		ofile.write("\n\tfile= \"%s\";" % get_full_filepath(bus, ob, GeomMeshFile.file))
		ofile.write("\n\tanim_speed= %i;" % GeomMeshFile.anim_speed)
		ofile.write("\n\tanim_type= %i;" % ANIM_TYPE[GeomMeshFile.anim_type])
		ofile.write("\n\tanim_offset= %i;" % (GeomMeshFile.anim_offset - 1))
		ofile.write("\n}\n")

		bus['node']['geometry']= proxy_name
		return proxy_name
