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

import bpy
from bl_ui.properties_material import active_node_mat


narrowui = 200


def context_tex_datablock(context):
	idblock = context.material
	if idblock:
		return active_node_mat(idblock)

	idblock = context.lamp
	if idblock:
		return idblock

	idblock = context.world
	if idblock:
		return idblock

	idblock = context.brush
	if idblock:
		return idblock

	if context.particle_system:
		idblock = context.particle_system.settings

	return idblock


def factor_but(layout, rna_pointer, use, factor, label= None, color= None):
	row= layout.row(align=True)
	row.prop(rna_pointer,
			 use,
			 text= "")
	sub= row.row(align=True)
	sub.active= getattr(rna_pointer, use)
	sub.prop(rna_pointer,
			 factor,
			 slider= True,
			 text= label if label else "")
	if color:
		sub.prop(rna_pointer, color, text="")

	invert= use+'_invert'
	if hasattr(rna_pointer, invert):
		sub.prop(rna_pointer, invert,text= "")


def influenceItemUI(layout, rna_pointer, attr, label):
	textureAttr   = "map_"+attr
	textureMult   = attr+"_mult"
	textureInvert = attr+"_invert"

	row = layout.row(align=True)
	row.prop(rna_pointer, textureAttr, text="")

	sub = row.row(align=True)
	sub.active = getattr(rna_pointer, textureAttr)
	sub.prop(rna_pointer, textureMult, slider=True, text=label)

	if hasattr(rna_pointer, textureInvert):
		sub.prop(rna_pointer, textureInvert, text="")


def engine_poll(cls, context):
	rd= context.scene.render
	return (rd.engine in cls.COMPAT_ENGINES)


def texture_type_poll(cls, context, tex, tex_type):
	if not engine_poll(cls, context):
		return False
	return tex and tex.type == 'VRAY' and tex.vray.type == tex_type


class VRayPanel:
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw_header(self, context):
		self.layout.label(text="", icon='VRAY_LOGO_MONO')


class VRayDataPanel(VRayPanel):
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'data'

	@classmethod
	def poll(cls, context):
		if not engine_poll(cls, context):
			return False
		return context.mesh or context.curve


class VRayLampPanel():
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'data'

	@classmethod
	def poll(cls, context):
		return context.lamp and engine_poll(cls, context)


class VRayMaterialPanel():
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'material'

	@classmethod
	def poll(cls, context):
		if not engine_poll(cls, context):
			return False

		ma = context.material
		if not ma:
			return False

		VRayMaterial = ma.vray
		if VRayMaterial.nodetree:
			return False

		return True


class VRayObjectPanel(VRayPanel):
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'object'

	@classmethod
	def poll(cls, context):
		return engine_poll(cls, context)


class VRayParticlePanel(VRayPanel):
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'particle'

	@classmethod
	def poll(cls, context):
		return context.particle_system and engine_poll(cls, context)


class VRayRenderPanel():
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'render'

	@classmethod
	def poll(cls, context):
		return engine_poll(cls, context)


class VRayRenderLayersPanel(VRayPanel):
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'render_layer'

	@classmethod
	def poll(cls, context):
		return engine_poll(cls, context)


class VRayScenePanel(VRayPanel):
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'scene'

	@classmethod
	def poll(cls, context):
		return engine_poll(cls, context)


class VRayTexturePanel(VRayPanel):
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'texture'

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		if not engine_poll(cls, context):
			return False
		tex= context.texture
		return tex and (tex.type != 'NONE')


class VRayWorldPanel():
	bl_space_type  = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context     = 'world'

	@classmethod
	def poll(cls, context):
		return context.world and engine_poll(cls, context)


# List item:
#  <item name> <item use-flag>
#
class VRayListUse(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		layout.label(item.name)
		layout.prop(item, 'use')


class VRayList(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		layout.label(item.name)


class VRayListDR(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		layout.label("%s [%s]" % (item.name, item.address))
		layout.prop(item, 'use', text="")


class VRayListMaterialSlots(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		ob   = data
		slot = item
		ma   = slot.material

		split = layout.split(percentage=0.75)

		if ma:
			split.label(text=ma.name, translate=False, icon_value=icon)
			split.prop(slot, 'link', text="", emboss=False, translate=False)
		else:
			split.label(text="")
			split.prop(slot, 'link', text="", emboss=False, translate=False)


def GetRegClasses():
	return (
		VRayListUse,
		VRayList,
		VRayListDR,
		VRayListMaterialSlots,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
