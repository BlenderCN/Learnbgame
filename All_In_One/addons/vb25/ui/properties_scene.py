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
from vb25.ui.ui import *
from vb25.plugins import *


class VRAY_RP_Layers(VRayRenderLayersPanel, bpy.types.Panel):
	bl_label   = "Render Elements"
	bl_options = {'HIDE_HEADER'}
	
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return engine_poll(__class__, context)

	def draw_header(self, context):
		VRayScene = context.scene.vray
		self.layout.prop(VRayScene, 'render_channels_use', text="")

	def draw(self, context):
		VRayScene = context.scene.vray
		self.layout.prop(VRayScene, 'render_channels_use', text="Use Render Elements")

		wide_ui = context.region.width > narrowui
		layout= self.layout

		sce= context.scene
		vsce= sce.vray
		render_channels= vsce.render_channels

		layout.active= vsce.render_channels_use

		row= layout.row()
		row.template_list("VRayListUse", "",
						  vsce, 'render_channels',
						  vsce, 'render_channels_index',
						  rows= 4)
		col= row.column()
		sub= col.row()
		subsub= sub.column(align=True)
		subsub.operator('vray.render_channels_add',	   text="", icon="ZOOMIN")
		subsub.operator('vray.render_channels_remove', text="", icon="ZOOMOUT")

		if vsce.render_channels_index >= 0 and len(render_channels) > 0:
			render_channel= render_channels[vsce.render_channels_index]

			layout.separator()

			if wide_ui:
				split= layout.split(percentage=0.2)
			else:
				split= layout.split()
			col= split.column()
			col.label(text="Name:")
			if wide_ui:
				col= split.column()
			row= col.row(align=True)
			row.prop(render_channel, 'name', text="")

			if wide_ui:
				split= layout.split(percentage=0.2)
			else:
				split= layout.split()
			col= split.column()
			col.label(text="Type:")
			if wide_ui:
				col= split.column()
			col.prop(render_channel, 'type', text="")

			layout.separator()

			if render_channel.type != 'NONE':
				# Box border
				layout= layout.box()

				plugin= PLUGINS['RENDERCHANNEL'].get(render_channel.type)
				if plugin is not None:
					render_channel_data= getattr(render_channel,plugin.PLUG)

					if render_channel.name == "" or render_channel.name == "RenderChannel":
						def get_unique_name():
							for chan in render_channels:
								if render_channel_data.name == chan.name:
									return render_channel_data.name + " (enter unique name)"
							return render_channel_data.name
						render_channel.name= get_unique_name()

					plugin.draw(getattr(render_channel,plugin.PLUG), layout, wide_ui)


class VRAY_SP_includer(VRayScenePanel, bpy.types.Panel):
	bl_label   = "Includes"
	bl_options = {'DEFAULT_CLOSED'}
	
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw_header(self, context):
		VRayScene = context.scene.vray
		Includer  = VRayScene.Includer
		self.layout.label(text="", icon='VRAY_LOGO_MONO')
		self.layout.prop(Includer, 'use', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		layout= self.layout

		row= layout.row()

		vs= context.scene.vray
		module= vs.Includer
		
		layout.active= module.use

		row.template_list("VRayListUse", "", module, 'nodes', module, 'nodes_selected', rows = 4)

		col= row.column()
		sub= col.row()
		subsub= sub.column(align=True)
		subsub.operator('vray.includer_add',    text="", icon="ZOOMIN")
		subsub.operator('vray.includer_remove', text="", icon="ZOOMOUT")
		sub= col.row()
		subsub= sub.column(align=True)
		subsub.operator("vray.includer_up",   icon='MOVE_UP_VEC',   text="")
		subsub.operator("vray.includer_down", icon='MOVE_DOWN_VEC', text="")

		if module.nodes_selected >= 0 and len(module.nodes) > 0:
			render_node= module.nodes[module.nodes_selected]

			layout.separator()

			layout.prop(render_node, 'name')
			layout.prop(render_node, 'scene')

		# layout.separator()
		# box= layout.box()
		# box.label(text="Enable options export in curent scene:")
		# split = box.split()
		# col= split.column()
		# col.prop(module, 'setting', text="Use export scene setting")
		# col.prop(module, 'camera', text="Use export camera")
		# col.prop(module, 'materials', text="Use export materials")
		
		# col.prop(module, 'environment', text="Use export environment")
		# col.prop(module, 'lights', text="Use export lights")
		# col.prop(module, 'colorMapping_standalone', text="Use Color Mapping")
		# col.prop(module, 'geometry', text="Use export geometry")
		# col.prop(module, 'scene_nodes', text="Use Vray Nodes")


class VRAY_SP_tools(VRayScenePanel, bpy.types.Panel):
	bl_label   = "Tools"
	bl_options = {'DEFAULT_CLOSED'}
	
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		layout= self.layout

		box= layout.box()
		box.label(text="Scene:")
		split= box.split()
		col= split.column()
		col.operator("vray.convert_materials", icon='MATERIAL')
		if wide_ui:
			col= split.column()
		col.operator("vray.settings_to_text", icon='TEXT')

		layout.separator()

		box= layout.box()
		box.label(text="Object:")
		split= box.split()
		col= split.column()
		col.operator("vray.copy_linked_materials", icon='MATERIAL')

		# layout.separator()

		# layout.operator("vray.update", icon='SCENE_DATA')


class VRAY_SP_lights_tweaker(VRayScenePanel, bpy.types.Panel):
	bl_label   = "Lights"
	bl_options = {'DEFAULT_CLOSED'}
	
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		layout= self.layout

		split= layout.split()
		col= split.column()

		if bpy.data.lamps:
			for lamp in bpy.data.lamps:
				VRayLamp= lamp.vray
				sub_t= col.row()
				sub_t.label(text= " %s" % lamp.name, icon='LAMP_%s' % lamp.type)

				sub= col.row(align= True)
				sub_c= sub.row()
				sub_c.prop(VRayLamp, 'enabled', text="")
				sub_c.prop(lamp,     'color',     text="")
				sub_v= sub.row()
				sub_v.prop(VRayLamp, 'intensity', text="")
				sub_v.prop(VRayLamp, 'subdivs',   text="")
		else:
			col.label(text="Nothing in bpy.data.lamps...")


def GetRegClasses():
	return (
		VRAY_RP_Layers,
		VRAY_SP_includer,
		VRAY_SP_tools,
		VRAY_SP_lights_tweaker,
	)


def register():
	from bl_ui import properties_scene
	for member in dir(properties_scene):
		subclass = getattr(properties_scene, member)
		try:
			subclass.COMPAT_ENGINES.add('VRAY_RENDER')
			subclass.COMPAT_ENGINES.add('VRAY_RENDER_PREVIEW')
		except:
			pass
	del properties_scene

	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	from bl_ui import properties_scene
	for member in dir(properties_scene):
		subclass = getattr(properties_scene, member)
		try:
			subclass.COMPAT_ENGINES.remove('VRAY_RENDER')
			subclass.COMPAT_ENGINES.remove('VRAY_RENDER_PREVIEW')
		except:
			pass
	del properties_scene

	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
