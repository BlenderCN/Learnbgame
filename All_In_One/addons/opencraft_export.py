
#import Blender
import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper

bl_info = {
	"name": "Export OpenCraft mesh (.ocm)",
	"description": "This addon allows you to export OpenCraft mesh (.ocm) files.",
	"author": "Lassi Hämäläinen",
	"version": (0, 1),
	"blender": (2, 6, 0),
	#"api": ???,
	"location": "File > Export> OpenCraft mesh (.ocm)",
	"warning": "Work in progress.",
	"wiki_url": "http://nowiki",
	"tracker_url": "",
	"category": "Learnbgame"
}

def menu_func_export(self, context):
	self.layout.operator(ExportOpenCraftMesh.bl_idname, text='OpenCraft mesh (.ocm)')


def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
	register()
	

class ExportOpenCraftMesh(bpy.types.Operator, ExportHelper):
	bl_idname = 'export_mesh.export_ocm'
	bl_label = 'Export OpenCraft mesh'
	bl_options = {'PRESET'}

	filename_ext = '.ocm'

	filter_glob = StringProperty(
							default='*.ocm',
							options={'HIDDEN'}
							)


	def execute(self, context):
		file = open(self.filepath,"w")
		file.write("@OCMv1.0@\n")
		sce = bpy.data.scenes[0]
		ob = sce.objects.active
		mesh = bpy.data.meshes[ob.name]
		for face in mesh.faces:
			file.write("@FACEBEGIN@ %i\n" % len(face.vertices))
			for index in face.vertices:
				file.write("v %f %f %f\n" % (mesh.vertices[index].co.x,mesh.vertices[index].co.y,mesh.vertices[index].co.z))
				file.write("n %f %f %f\n" % (mesh.vertices[index].normal.x,mesh.vertices[index].normal.y,mesh.vertices[index].normal.z))
			file.write("@FACEEND@\n")
			
		file.close()
		return {'FINISHED'}

