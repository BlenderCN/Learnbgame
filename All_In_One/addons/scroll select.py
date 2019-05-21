bl_info = {
	"name": "Scroll Select",
	"author": "Lee Hesketh",
	"version": (1, 0),
	"blender": (2, 79, 0),
	"location": "",
	"description": "Change mesh selection mode with the scroll wheel",
	"warning": "",
	"wiki_url": "",
	"category": "Mesh",
	}

import bpy


class scrollSelect(bpy.types.Operator):
	"""Change Selection mode with scroll wheel"""
	bl_idname = "mesh.scroll_select"
	bl_label = "Scroll Select"
	bl_options = { 'REGISTER', 'UNDO' }
	
	@classmethod
	def poll(cls, context):
		return (context.active_object is not None) 
	mode = 1
	mode_type = [(True, False, False), (False, True, False), (False, False, True)]

	def modal(self, context, event):
		if event.type == 'WHEELUPMOUSE' and self.mode < 2:
			self.mode +=1
		elif event.type == 'WHEELDOWNMOUSE' and self.mode > 0:
			self.mode -=1
		context.tool_settings.mesh_select_mode = self.mode_type[self.mode]
		if not event.shift:

			return {'FINISHED'}
		return {'RUNNING_MODAL'}
	def invoke(self, context, event):
		context.tool_settings.mesh_select_mode = (False, True, False)
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}


addon_keymaps = []	
def register():
	wm = bpy.context.window_manager
	km = wm.keyconfigs.default.keymaps['Mesh']
	kmi = km.keymap_items.new(scrollSelect.bl_idname, 'WHEELDOWNMOUSE', 'PRESS', shift=True)
	kmj = km.keymap_items.new(scrollSelect.bl_idname, 'WHEELUPMOUSE', 'PRESS', shift=True)
	addon_keymaps.append((km, kmi))
	addon_keymaps.append((km, kmj))
	
	bpy.utils.register_module(__name__)

	
def unregister():
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()
	
	bpy.utils.unregister_module(__name__)
if __name__ == "__main__":
	register()

