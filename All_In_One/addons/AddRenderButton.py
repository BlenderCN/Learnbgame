bl_info = {
	"name": "Blender 2.8b RenderButtons",
	"author": "Mitsuma",
	"version": (0, 0, 2),
	"blender": (2, 80, 0),
	"location": "Render Properties",
	"description": "",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame",
	}

import bpy 


class AddRenderPanel(bpy.types.Panel):
	"""Creates a Panel in the Object properties window"""
	bl_label = "Render"
	bl_idname = "OBJECT_PT_Add_Render"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "render"

	def draw(self, context):
		layout = self.layout

		rd = context.scene.render

		row = layout.row(align=True)
		row.operator("render.render", text="Render", icon='RENDER_STILL')
		row.operator("render.render", text="Animation", icon='RENDER_ANIMATION').animation = True
		
		split = layout.split()

		split.label(text="Display:")
		row = split.row(align=True)
		row.prop(rd, "display_mode", text="")
		row.prop(rd, "use_lock_interface", icon_only=True)

def register():
	bpy.utils.register_class(AddRenderPanel)

def unregister():
	bpy.utils.unregister_class(AddRenderPanel)

if __name__ == "__main__":
	register()
