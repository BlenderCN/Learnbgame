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

import os

''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *
from vb25.ui import ui


TYPE= 'SETTINGS'
ID=   'SettingsCaustics'

NAME= 'Caustics'
DESC= "Caustics settings."

PARAMS= (
	'on',
	'max_photons',
	'search_distance',
	'max_density',
	'multiplier',
	'mode',
	'file',
	'dont_delete',
	'auto_save',
	'auto_save_file',
	'show_calc_phase'
)


def add_properties(parent_struct):
	class SettingsCaustics(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsCaustics)
	
	parent_struct.SettingsCaustics= PointerProperty(
		name= "Caustics",
		type=  SettingsCaustics,
		description= "Caustics settings"
	)

	SettingsCaustics.on= BoolProperty(
		name= "On",
		description= "Enable caustics computation",
		default= False
	)

	SettingsCaustics.max_photons= IntProperty(
		name= "Max photons",
		description= "TODO",
		min= 0,
		soft_min= 0,
		soft_max= 10000,
		default= 30
	)

	SettingsCaustics.search_distance= FloatProperty(
		name= "Search distance",
		description= "TODO",
		subtype= 'DISTANCE',
		min= 0.0,
		max= 1000.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.1
	)
	
	SettingsCaustics.max_density= FloatProperty(
		name= "Max density",
		description= "TODO",
		min= 0.0,
		max= 1000.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	SettingsCaustics.multiplier= FloatProperty(
		name= "Multiplier",
		description= "TODO",
		min= 0.0,
		max= 1000.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	SettingsCaustics.mode= EnumProperty(
		name= "Mode",
		description= "Caustics computaion mode",
		items= (
			('FILE', "From file", ""),
			('NEW',  "New",       ""),
		),
		default= 'NEW'
	)

	SettingsCaustics.file= StringProperty(
		name= "File",
		subtype= 'FILE_PATH',
		description= "TODO"
	)
	
	SettingsCaustics.auto_save= BoolProperty(
		name= "Auto save",
		description= "TODO",
		default= False
	)

	SettingsCaustics.auto_save_file= StringProperty(
		name= "Auto save file",
		subtype= 'FILE_PATH',
		description= "TODO"
	)

	SettingsCaustics.show_calc_phase= BoolProperty(
		name= "Show calc phase",
		description= "TODO",
		default= False
	)

	SettingsCaustics.dont_delete= BoolProperty(
		name = "Don\'t delete",
		default = False
	)



'''
  OUTPUT
'''
def write(bus):
	MODE= {
		'FILE': 1,
		'NEW':  0
	}

	ofile=  bus['files']['scene']
	scene=  bus['scene']

	VRayScene=        scene.vray
	SettingsCaustics= VRayScene.SettingsCaustics

	ofile.write("\n%s %s {" % (ID,ID))
	for param in PARAMS:
		if param in ('file','auto_save_file'):
			value= "\"%s\"" % path_sep_to_unix(bpy.path.abspath(getattr(SettingsCaustics, param)))
		elif param == 'mode':
			value= MODE[SettingsCaustics.mode]
		else:
			value= getattr(SettingsCaustics, param)
		ofile.write("\n\t%s= %s;"%(param, p(value)))
	ofile.write("\n}\n")



'''
  GUI
'''
class RENDER_PT_SettingsCaustics(ui.VRayRenderPanel, bpy.types.Panel):
	bl_label = NAME

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		scene= context.scene
		rd=    scene.render
		if not hasattr(scene.vray, ID):
			return False
		show= scene.vray.SettingsCaustics.on
		return (show and ui.engine_poll(__class__, context))

	def draw(self, context):
		wide_ui= context.region.width > ui.narrowui
		layout= self.layout

		vsce= context.scene.vray
		vmodule= getattr(vsce, ID)

		layout.prop(vmodule,'mode')

		if vmodule.mode == 'FILE':
			layout.separator()
			layout.prop(vmodule,'file')

			filePath = vmodule.file
			photonMapSize = "0 bytes"
			if os.path.exists(filePath):
				photonMapSize = GetStrSize(os.stat(filePath).st_size)

			layout.label("Photon map takes %s." % photonMapSize)
			layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(vmodule,'multiplier')
		col.prop(vmodule,'search_distance')
		if wide_ui:
			col = split.column()
		col.prop(vmodule,'max_photons')
		col.prop(vmodule,'max_density')

		if not vmodule.mode == 'FILE':
			split = layout.split()
			col = split.column()
			col.prop(vmodule, 'dont_delete')
			col = split.column()
			col.prop(vmodule, 'show_calc_phase')

			split= layout.split()
			split.label(text="Files:")
			split= layout.split(percentage=0.25)
			colL= split.column()
			colR= split.column()
			if wide_ui:
				colL.prop(vmodule,"auto_save", text="Auto save")
			else:
				colL.prop(vmodule,"auto_save", text="")
			colR.active= vmodule.auto_save
			colR.prop(vmodule,"auto_save_file", text="")


def GetRegClasses():
	return (
		RENDER_PT_SettingsCaustics,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
