
import bpy
from bpy.props import BoolProperty
from bpy_extras.io_utils import ExportHelper
from .export_mesh import ExportMesh


class TowerEngineMeshExporter(bpy.types.Operator, ExportHelper):
	bl_idname	   = "export_tem.tem"
	bl_label		= "Export"
	bl_options	  = {'PRESET'}
	
	filename_ext = ".tem"

	selection_prop = BoolProperty(name = "Selection Only", description = "Export selection only", default = True)
	include_tex_prop = BoolProperty(name = "Include Textures in File",
									description = "Include Texture Images directly into .tem file instead of copying and linking the URL",
									default = False)
	
	def execute(self, context):
		scene = bpy.data.scenes.values()[0]
		export_mesh = ExportMesh()
		
		for obj in bpy.data.objects:
			if self.selection_prop == True and obj.select == False:
				continue
			
			try:
				mesh = obj.to_mesh(scene, True, 'PREVIEW')
				mesh.transform(obj.matrix_world)
				mesh.calc_normals()
				export_mesh.add_mesh(mesh)
			except RuntimeError:
				continue
			
		export_mesh.save(self.filepath, self.include_tex_prop)
		
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(TowerEngineMeshExporter.bl_idname, text="TowerEngine Mesh (.tem)")

def register():
	bpy.utils.register_class(TowerEngineMeshExporter)
	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.types.INFO_MT_file_export.remove(menu_func)
	bpy.utils.unregister_class(TowerEngineMeshExporter)