bl_info = {
    "name": "Lunar Exporter",
    "category": "Import-Export"
}
import os
import bpy
class ExportLunar(bpy.types.Operator):
	bl_idname = 'export.lunar'
	bl_label = 'Lunar'
	vertex_positions = []
	texture_coordinates = []
	polygon_indices_by_submesh = {}
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	def execute(self, context):
		base_path = '/home/n2liquid/lunar-export'
		dynamic_vbo = base_path + '/dynamic.vbo'
		static_vbo = base_path + '/static.vbo'
		scene = context.scene
		with open(file_path, 'w') as file:
			for object in scene.objects:
				file.write(object.type + ': ' + object.name + '\n')
		return {'FINISHED'}
def menu_func(self, context):
	self.layout.operator(ExportLunar.bl_idname, text='Lunar', icon='BLENDER')
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func)
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func)
