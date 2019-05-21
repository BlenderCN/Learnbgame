bl_info = {
	"name": "Nexus Override Materials",
	"author": "Nexus Studio",
	"version": (0, 1, 0),
	"blender": (2, 80, 0),
	"location": "Properties > View Layers",
	"description": "Tools for fast override materials in selected objects (MESH)",
	"warning": "",
	"wiki_url": "https://github.com/Hichigo/NexusOverrideMaterials",
	"category": "Learnbgame",
	}

import bpy

from bpy.props import (IntProperty,
						BoolProperty,
						StringProperty,
						CollectionProperty,
						PointerProperty)

from bpy.types import (Operator,
						Panel,
						PropertyGroup,
						UIList)

#-------------------------------------------------------------------
#	Functions
#-------------------------------------------------------------------

def OverrideMaterials(ctx):

	for ob in ctx.selected_objects:
		if ob.type == 'MESH':
			RememberAndOverrideMaterials(ob, ob.material_slots, ctx)



def RememberAndOverrideMaterials(currentObject, slots_original, ctx):
	currentObject.NOM_RecoverMaterials.clear()
	for slot in slots_original:
		currentMat = currentObject.NOM_RecoverMaterials.add()
		currentMat.material = slot.material.name #by mat name
		#currentMat.material = slot.material #by mat
		
		if not slot.material.NOM_isExclude:
			slot.material = ctx.scene.NOM_Material


def RecoverMaterials(ctx):
	for ob in ctx.selected_objects:
		if ob.type == 'MESH':
			i = 0
			for slot in ob.material_slots:
				slot.material = bpy.data.materials[ob.NOM_RecoverMaterials[i].material] #by mat name
				#slot.material = ob.NOM_RecoverMaterials[i].material #by mat
				i += 1



#-------------------------------------------------------------------
#	Operators
#-------------------------------------------------------------------

class NOM_OT_ExcludeMat(bpy.types.Operator):

	bl_idname = "exclude.material"
	bl_label = "Exclude material"

	index : bpy.props.IntProperty(
		name="Index material",
		description="Index material",
		default=-1
	)

	def execute(self, context):
		bpy.data.materials[self.index].NOM_isExclude = not bpy.data.materials[self.index].NOM_isExclude

		return {'FINISHED'}

class NOM_OT_OverrideMat(bpy.types.Operator):

	bl_idname = "override.materials"
	bl_label = "Override materials"

	def execute(self, context):
		scn = context.scene

		scn.NOM_isOverrided = True

		OverrideMaterials(context)

		self.report({'INFO'}, 'OVERRIDE WORKING!')

		return {'FINISHED'}

class NOM_OT_RecoverMat(bpy.types.Operator):

	bl_idname = "recover.materials"
	bl_label = "Recover materials"

	def execute(self, context):
		scn = context.scene

		scn.NOM_isOverrided = False

		RecoverMaterials(context)

		self.report({'INFO'}, 'RECOVER WORKING!')

		return {'FINISHED'}


#-------------------------------------------------------------------
#	Drawing
#-------------------------------------------------------------------

class NOM_UL_items(UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		mat = item

		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			row = layout.row(align=True)
			row.prop(mat, "name", text="", emboss=False, icon_value=layout.icon(mat))

			if mat.NOM_isExclude:
				iconName = 'CANCEL'
			else:
				iconName = 'FILE_TICK'

			row.operator("exclude.material", icon=iconName, text="").index = index

	def invoke(self, context, event):
		pass

class NOM_PT_objectList(Panel):
	"""Adds a custom panel to the TEXT_EDITOR"""
	bl_idname = 'NOM_PT_ListMaterials'
	bl_space_type = "PROPERTIES"
	bl_region_type = 'WINDOW'
	bl_context = "view_layer"
	bl_label = "Nexus Override Materials"

	def draw(self, context):
		layout = self.layout
		scn = context.scene
		data = bpy.data

		if not scn.NOM_isOverrided:
			col = layout.column()
			# split = layout.split()

			# col = split.column()
			col.prop_search(scn, "NOM_Material", bpy.data, "materials", icon='MATERIAL_DATA')

			box = layout.box()
			box.label(text='Exclude materials')
			box.template_list("NOM_UL_items", "custom_def_list", data, "materials", scn, "custom_index", rows=4)

			col = layout.column(align=True)
			col.operator("override.materials", icon="OVERLAY", text="Override materials")
		else:
			col = layout.column(align=True)
			col.operator("recover.materials", icon="DECORATE_OVERRIDE", text="Recover materials")




#-------------------------------------------------------------------
#	Collection
#-------------------------------------------------------------------

class NOM_PG_RecoverMaterials(PropertyGroup):
	material : StringProperty(#PointerProperty
		name='Materials',
		description='Recover materials',
		default=''
		# type=bpy.types.Material
	)

#-------------------------------------------------------------------
#	Register & Unregister
#-------------------------------------------------------------------

classes = (
	NOM_OT_ExcludeMat,
	NOM_OT_OverrideMat,
	NOM_OT_RecoverMat,
	NOM_UL_items,
	NOM_PT_objectList,
	NOM_PG_RecoverMaterials
)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)

	# Custom scene properties
	bpy.types.Scene.NOM_Material = PointerProperty(name='Material override', description='Material to override', type=bpy.types.Material)
	bpy.types.Scene.custom_index = IntProperty()
	bpy.types.Scene.NOM_isOverrided = BoolProperty(default=False)
	bpy.types.Object.NOM_RecoverMaterials = CollectionProperty(type=NOM_PG_RecoverMaterials)
	bpy.types.Material.NOM_isExclude = BoolProperty(default=False)


def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		unregister_class(cls)

	# delete custom scene properties
	del bpy.types.Scene.NOM_Material
	del bpy.types.Scene.custom_index
	del bpy.types.Scene.NOM_isOverrided
	del bpy.types.Object.NOM_RecoverMaterials
	del bpy.types.Material.NOM_isExclude


if __name__ == "__main__":
	register()