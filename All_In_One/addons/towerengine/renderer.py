import bpy

from . import viewport_render

class TowerEngineRenderEngine(bpy.types.RenderEngine):
	bl_idname = "towerengine_renderer"
	bl_label = "TowerEngine"
	bl_use_preview = True
	bl_use_texture_preview = True

	def render(self, scene):
		return

	def view_update(self, context):
		viewport_render.update(self, context)

	def view_draw(self, context):
		viewport_render.render(self, context)



def register():
	bpy.utils.register_class(TowerEngineRenderEngine)

def unregister():
	bpy.utils.register_class(TowerEngineRenderEngine)