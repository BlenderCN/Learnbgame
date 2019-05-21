bl_info = {
	"name": "Export Model to Java (.java)",
	"author": "Dacre Denny",
	"version": (1, 0),
	"blender": (2, 7, 9), 
	"location": "File -> Export",
	"description": "Exports selected models to Java source files",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame"
}

import os
import array
import bpy
from bpy.props import *
from bpy_extras.io_utils import ExportHelper 

### Export logic

def get_coordinate_str(vertex):
	co = list(vertex.co)
	return """			%.2ff, %.2ff, %.2ff""" % (co[0], co[2], co[1])

def do_export(context, props, filepath):
	
	package_name = "defaultpackage" if not props.package_name else props.package_name 

	basedir = os.path.dirname(filepath)
	filename = os.path.splitext(filepath)[0]
	classname = os.path.splitext(os.path.basename(filepath))[0]
	
	selection = context.selected_objects

	meshpath = os.path.join(basedir, "%s.java" % filename)
	file = open(meshpath, 'w')

	file.write("""package %s;
""" % package_name)

	file.write("""
public class %s {
""" % classname)

	for mesh in selection:

		if not (mesh.type == "MESH"):
			continue
		
		name = bpy.path.clean_name(mesh.name)

		vertexUVList = {}
		vertexPositionList = []
		vertexNormalList = []

		for triangle in mesh.data.polygons:

			i = 0
			vertices = list(triangle.vertices)			

			for vertex in vertices:
				vtx = mesh.data.vertices[vertex]
				
				vertexPosition = list(mesh.data.vertices[vertex].co)
				vertexPositionList.append("""			%.2ff, %.2ff, %.2ff""" % (vertexPosition[0], vertexPosition[2], vertexPosition[1]))
				
				vertexNormal = list(mesh.data.vertices[vertex].normal) if triangle.use_smooth else list(triangle.normal)
				vertexNormalList.append("""			%.2ff, %.2ff, %.2ff""" % (vertexNormal[0], vertexNormal[1], vertexNormal[2]))
				
				for uv_layer in mesh.data.uv_layers:
					uvCoord = uv_layer.data[triangle.loop_indices[i]].uv
					uvCoord = [uvCoord[0], 1 - uvCoord[1]]
					vertexUVList[ vtx.index ] = """		%.2ff, %.2ff""" % (uvCoord[0], uvCoord[1])
					
				i += 1
		
		facePositionList = []
		faceNormalList = []
		faceUVList = []
		n = 0
		
		mesh_data_vertices = mesh.data.vertices
		
		for triangle in mesh.data.polygons:
			vertices = list(triangle.vertices)
			
			if len(vertices) == 3:
				
				idx0 = vertices[0]
				idx1 = vertices[1]
				idx2 = vertices[2]
				
				facePositionList.append( get_coordinate_str(mesh_data_vertices[idx0]))
				facePositionList.append( get_coordinate_str(mesh_data_vertices[idx1]))
				facePositionList.append( get_coordinate_str(mesh_data_vertices[idx2]))
				
				faceNormalList.append(vertexNormalList[idx0])
				faceNormalList.append(vertexNormalList[idx1])
				faceNormalList.append(vertexNormalList[idx2])
				
				if len(vertexUVList) > 0:
					faceUVList.append(vertexUVList[idx0])
					faceUVList.append(vertexUVList[idx1])
					faceUVList.append(vertexUVList[idx2])
				
				n += 3
				
			elif len(vertices) == 4:
				
				idx0 = vertices[0]
				idx1 = vertices[1]
				idx2 = vertices[2]
				idx3 = vertices[3]
				
				facePositionList.append( get_coordinate_str(mesh_data_vertices[idx0]))
				facePositionList.append( get_coordinate_str(mesh_data_vertices[idx1]))
				facePositionList.append( get_coordinate_str(mesh_data_vertices[idx2]))
				
				facePositionList.append( get_coordinate_str(mesh_data_vertices[idx0]))
				facePositionList.append( get_coordinate_str(mesh_data_vertices[idx2]))
				facePositionList.append( get_coordinate_str(mesh_data_vertices[idx3]))
				
				faceNormalList.append(vertexNormalList[idx0])
				faceNormalList.append(vertexNormalList[idx1])
				faceNormalList.append(vertexNormalList[idx2])
				
				faceNormalList.append(vertexNormalList[idx0])
				faceNormalList.append(vertexNormalList[idx2])		   
				faceNormalList.append(vertexNormalList[idx3])
				
				if len(vertexUVList) > 0:
					faceUVList.append(vertexUVList[idx0])
					faceUVList.append(vertexUVList[idx1])
					faceUVList.append(vertexUVList[idx2])
					
					faceUVList.append(vertexUVList[idx0])
					faceUVList.append(vertexUVList[idx2])
					faceUVList.append(vertexUVList[idx3])		
				
				n += 6
		
		vertexPositionString = ",\n".join(facePositionList)
		vertexNormalString = ",\n".join(faceNormalList)
		vertexUVString = ",\n".join(faceUVList)
					
		file.write("""
	public static class %s
	{
		private static float[] vertexPositions = 
		{
%s
		};
		
		private static float[] vertexNormals = 
		{
%s
		};
		
		private static float[] vertexUVs = 
		{
%s
		};
		
		public static float[] GetVertexPositions() {
			return vertexPositions;
		}
		
		public static float[] GetVertexNormals() {
			return vertexNormals;
		}
		
		public static float[] GetVertexUVs() {
			return vertexUVs;
		}
		
		public static int GetCount() {
			return %i;
		}
	}
""" % (name, vertexPositionString, vertexNormalString, vertexUVString, n))
	
	file.write("""}""")

	file.flush()
	file.close()

### Export operator

class ExportModelJava(bpy.types.Operator, ExportHelper):
	'''Exports geometry of the active Model to a Java source file.'''
	bl_idname = "export_object.java"
	bl_label = "Export to Java (.java)"

	filename_ext = ".java"

	package_name = StringProperty(name="Package Name",
							description="The Package Name to use when generating the exported source file",
							default="")
	
	@classmethod
	def poll(cls, context):
		return context.active_object.type in ['MESH']

	def execute(self, context):
		
		props = self.properties
		
		filepath = self.filepath
		filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

		do_export(context, props, filepath)
					
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager

		if True:
			wm.fileselect_add(self) # will run self.execute()
			return {'RUNNING_MODAL'}
		elif True:
			wm.invoke_search_popup(self)
			return {'RUNNING_MODAL'}
		elif False:
			return wm.invoke_props_popup(self, event) #
		elif False:
			return self.execute(context)


### Register addon

def menu_func(self, context):
	self.layout.operator(ExportModelJava.bl_idname, text="Java Source File (.java)")

def register():
	bpy.utils.register_module(__name__)

	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)

	bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
	register()