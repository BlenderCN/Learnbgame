import bpy

from bpy.types import (
    Panel, 
    Operator,
    Menu,
    PropertyGroup,
    SpaceView3D,
    WindowManager,
    )

from bpy.utils import (
    previews,
    register_class,
    unregister_class
    )

from . import addon_operator

class GENERATE_PT_FRUIT(Panel):
	bl_label = "Random Fruit"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fruit"

	def draw(self,context):
		layout = self.layout
		scene = context.scene
		row = layout.row()
		row.operator(addon_operator.GENERATE_OT_FRUIT.bl_idname)
		row1 = layout.row()
		row1.operator(addon_operator.MUTATE_OT_FRUIT.bl_idname)
		row2 = layout.row()
		row2.operator(addon_operator.EDIT_OT_FRUIT.bl_idname)
		row3 = layout.row()
		row3.operator(addon_operator.COMBINE_OT_FRUIT.bl_idname)


def register():
	register_class(GENERATE_PT_FRUIT)

def unregister():
	unregister_class(GENERATE_PT_FRUIT)
