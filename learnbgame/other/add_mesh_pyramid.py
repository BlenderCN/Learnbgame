import bpy
import mathutils

bl_info = {
		"name": "Add Pyramid",
		"description": "Adds a pyramid mesh to the Add Mesh menu",
		"author": "pmurphy",
		"version": (1, 0),
		"blender": (2, 74),
		"location": "View3D > Add > Mesh",
		"warning": "",
		"wiki_url": "",
		"category": "Add Mesh"
}

class pmurphypyramid(bpy.types.Operator):
	bl_idname = "mesh.primitive_pyramid_add"
	bl_label = "Pyramid"
	bl_options = {'REGISTER', 'UNDO'}
	
	def draw(self, context):
		layout = self.layout
		layout.operator("mesh.primitive_pyramid_add", text="Add Pyramid")
	
	def execute(self, context):
		verts = [(-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0), (0, 0, 1)]
		faces = [(0, 1, 2, 3), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]

		mesh = bpy.data.meshes.new("Pyramid")
		object = bpy.data.objects.new("Pyramid", mesh)

		object.location = bpy.context.scene.cursor_location
		bpy.context.scene.objects.link(object)

		mesh.from_pydata(verts, [], faces)
	
		return {'FINISHED'}

def menu_func_pmurphypyramid(self, context):
	self.layout.operator(pmurphypyramid.bl_idname, text="Pyramid", icon = "PLUGIN")
def register():
    bpy.utils.register_class(pmurphypyramid)
    bpy.types.INFO_MT_mesh_add.append(menu_func_pmurphypyramid)
def unregister():
    bpy.utils.unregister_class(pmurphypyramid)
    bpy.types.INFO_MT_mesh_add.remove(menu_func_pmurphypyramid)
if __name__ == '__main__':
    register()