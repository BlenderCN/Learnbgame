bl_info = {
	"name": "Silent Set Scene Camera",
	"author": "Kenetics",
	"version": (0, 1),
	"blender": (2, 80, 0),
	"location": "View 3D > Select Camera > Object Context Menu",
	"description": "Changes the scene camera to selected active camera without changing viewport",
	"warning": "",
	"wiki_url": "",
	"category": "Learnbgame",
}

import bpy


class SCAC_OT_SilentSetSceneCamera(bpy.types.Operator):
	"""Changes active camera to selected active camera without changing viewport"""
	bl_idname = "camera.scac_ot_silent_set_scene_camera"
	bl_label = "Silent Set Scene Camera"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.type == 'CAMERA'

	def execute(self, context):
		context.scene.camera = context.active_object
		return {'FINISHED'}


def silent_set_scene_button(self, context):
	obj = context.object
	if obj is not None and obj.type == 'CAMERA':
		self.layout.operator(SCAC_OT_SilentSetSceneCamera.bl_idname)

#VIEW3D_MT_object_specials
def register():
	bpy.utils.register_class(SCAC_OT_SilentSetSceneCamera)
	bpy.types.VIEW3D_MT_object_context_menu.append(silent_set_scene_button)

def unregister():
	bpy.types.VIEW3D_MT_object_context_menu.remove(silent_set_scene_button)
	bpy.utils.unregister_class(SCAC_OT_SilentSetSceneCamera)

if __name__ == "__main__":
	register()
