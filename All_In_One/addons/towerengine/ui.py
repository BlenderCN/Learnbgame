
import bpy

from .renderer import TowerEngineRenderEngine


class TowerEnginePanel(bpy.types.Panel):
	COMPAT_ENGINES = {'towerengine_renderer'}

	@classmethod
	def poll(cls, context):
		rd = context.scene.render
		return rd.engine in cls.COMPAT_ENGINES


class TowerEngineAttributeList(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
		custom_icon = 'OBJECT_DATAMODE'

		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			layout.prop(item, 'name', icon_only=True)
			layout.prop(item, 'value', icon_only=True)

		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label("", icon=custom_icon)


class TowerEngineAttributeListAddItem(bpy.types.Operator):
	bl_idname = "towerengine.add_attr"
	bl_label = "Add attribute"

	def execute(self, context):
		context.object.towerengine.attributes.add()
		return{'FINISHED'}


class TowerEngineAttributeListDeleteItem(bpy.types.Operator):
	bl_idname = "towerengine.delete_attr"
	bl_label = "Delete attribute"

	@classmethod
	def poll(cls, context):
		return len(context.object.towerengine.attributes) > 0

	def execute(self, context):
		alist = context.object.towerengine.attributes
		index = context.object.towerengine.attribute_index

		alist.remove(index)

		return{ 'FINISHED'}


class TowerEngineObjectPanel(TowerEnginePanel):
	bl_idname = "OBJECT_PT_towerengine"
	bl_label = "TowerEngine"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"

	def draw(self, context):
		obj = context.object
		if not obj:
			return
		layout = self.layout

		if obj.type == "MESH":
			layout.prop(obj.towerengine, "disable_mesh")
		elif obj.type == "EMPTY":
			layout.prop(obj.towerengine, "object_type")

		layout.prop(obj.towerengine, 'tag')

		layout.label("Attributes:")
		layout.template_list("TowerEngineAttributeList", "TowerEngine Attribute List", obj.towerengine, "attributes", obj.towerengine, "attribute_index")

		row = layout.row()
		row.operator('towerengine.add_attr')
		row.operator('towerengine.delete_attr')


class TowerEngineMaterialTextureSlotInitOperator(bpy.types.Operator):
	bl_idname = "material.init_towerengine_texture_slots"
	bl_label = "Init TowerEngine Texture Slots"

	def execute(self, context):
		mat = context.material
		if not mat:
			return { "FINISHED" }

		for i in range(18 - len(mat.towerengine_texture_slots)):
			mat.towerengine_texture_slots.add()

		return { "FINISHED" }


class TowerEngineTexturePanel(TowerEnginePanel):
	bl_idname = "TEXTURE_PT_towerengine"
	bl_label = "Influence (TowerEngine)"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "texture"

	def draw(self, context):
		mat = context.material
		if not mat:
			return

		slot_index = mat.active_texture_index
		slot = mat.texture_slots[slot_index]

		if not slot:
			return

		layout = self.layout

		layout.prop(slot, "use_map_color_diffuse", text="Base Color")

		layout.prop(slot, "use_map_normal", text="Normal")

		row = layout.row()
		row.alignment = "LEFT"
		row.prop(slot, "use_map_displacement", text="Bump")
		if slot.use_map_displacement:
			row.prop(slot, "displacement_factor", text="Depth")

		layout.prop(slot, "use_map_emit", text="Emission")

		if len(mat.towerengine_texture_slots) < 18:
			layout.operator("material.init_towerengine_texture_slots")
		else:
			towerengine_slot = mat.towerengine_texture_slots[slot_index]
			layout.prop(towerengine_slot, 'use_map_metal_rough_reflect')


# From Blender Cycles Addon:
class TowerEngineMaterialContextPanel(TowerEnginePanel):
	bl_idname = "MATERIAL_PT_material_context_towerengine"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_label = ""
	bl_context = "material"
	bl_options = {'HIDE_HEADER'}

	@classmethod
	def poll(cls, context):
		return (context.material or context.object) and TowerEnginePanel.poll(context)

	def draw(self, context):
		layout = self.layout

		mat = context.material
		ob = context.object
		slot = context.material_slot
		space = context.space_data

		if ob:
			is_sortable = len(ob.material_slots) > 1
			rows = 1
			if (is_sortable):
				rows = 4

			row = layout.row()

			row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

			col = row.column(align=True)
			col.operator("object.material_slot_add", icon='ZOOMIN', text="")
			col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

			col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

			if is_sortable:
				col.separator()

				col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
				col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

			if ob.mode == 'EDIT':
				row = layout.row(align=True)
				row.operator("object.material_slot_assign", text="Assign")
				row.operator("object.material_slot_select", text="Select")
				row.operator("object.material_slot_deselect", text="Deselect")

		if ob:
			layout.template_ID(ob, "active_material", new="material.new")
		elif mat:
			layout.template_ID(space, "pin_id")


class TowerEngineMaterialPanel(TowerEnginePanel):
	bl_idname = "MATERIAL_PT_towerengine"
	bl_label = "Material (TowerEngine)"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "material"

	def draw(self, context):
		mat = context.material
		if not mat:
			return
		layout = self.layout
		layout.prop(mat.towerengine, 'mat_type')

		row = layout.row()
		row.enabled = True
		row.prop(mat, "diffuse_color", text="Base Color")

		if mat.towerengine.mat_type == "DEFAULT":
			layout.prop(mat.towerengine, 'metallic', slider=True)
			layout.prop(mat.towerengine, 'roughness', slider=True)
			layout.prop(mat.towerengine, 'reflectance', slider=True)

			layout.prop(mat.towerengine, "emission_color")

		elif mat.towerengine.mat_type == "SIMPLE_FORWARD":
			layout.prop(mat.towerengine, 'blend_mode')

		elif mat.towerengine.mat_type == "REFRACTION":
			layout.prop(mat.towerengine, "refraction_edge_color")


class TowerEngineMeshPanel(TowerEnginePanel):
	bl_idname = "DATA_PT_towerengine"
	bl_label = "TowerEngine"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "data"

	def draw(self, context):
		mesh = context.mesh

		if not mesh:
			return

		layout = self.layout
		layout.prop(mesh.towerengine, 'vertices_only')


class TowerEnginePhysicsPanel(TowerEnginePanel):
	bl_idname = "PHYSICS_PT_towerengine"
	bl_label = "TowerEngine"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "physics"

	def draw(self, context):
		obj = context.object

		if not obj:
			return

		layout = self.layout
		layout.prop(obj.towerengine, 'disable_mesh')
		layout.prop(obj.towerengine, 'compound_shape')

		if obj.towerengine.compound_shape and not obj.rigid_body:
			layout.label("Warning: Compund Shape need a rigid body to be created.")



reg_classes = [TowerEngineMeshPanel,
			   TowerEngineMaterialContextPanel,
			   TowerEngineMaterialPanel,
			   TowerEngineTexturePanel,
			   TowerEngineObjectPanel,
			   TowerEngineAttributeList,
			   TowerEngineAttributeListAddItem,
			   TowerEngineAttributeListDeleteItem,
			   TowerEnginePhysicsPanel,
			   TowerEngineMaterialTextureSlotInitOperator]

import bl_ui
compat = [bl_ui.properties_texture.TEXTURE_PT_context_texture,
		  bl_ui.properties_texture.TEXTURE_PT_image,
		  bl_ui.properties_texture.TEXTURE_PT_image_sampling,
		  bl_ui.properties_physics_rigidbody.PHYSICS_PT_rigid_body,
		  bl_ui.properties_physics_rigidbody.PHYSICS_PT_rigid_body_collisions,
		  bl_ui.properties_physics_rigidbody.PHYSICS_PT_rigid_body_dynamics,
		  bl_ui.properties_physics_common.PHYSICS_PT_add]


def register():
	for c in reg_classes:
		bpy.utils.register_class(c)

	for item in compat:
		item.COMPAT_ENGINES.add(TowerEngineRenderEngine.bl_idname)


def unregister():
	for c in reg_classes:
		bpy.utils.unregister_class(c)

	from bl_ui import properties_texture
	for item in compat:
		item.COMPAT_ENGINES.remove(TowerEngineRenderEngine.bl_idname)
