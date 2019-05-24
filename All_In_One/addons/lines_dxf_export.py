bl_info = {
	"name": "Lines DXF Export",
	"author": "6d7367",
	"location": "View3D > Tools > Slicer Addon",
	"version": (0, 1, 0),
	"blender": (2, 6, 9),
	"description": "Export selected object's edges to DXF file",
	"wiki": "",
	"category": "Learnbgame",
}


def register():
	bpy.utils.register_class(LinesDxfExportOperator)
	bpy.utils.register_class(LinesDxfExportPanel)
	


def unregister():
	bpy.utils.unregister_class(LinesDxfExportPanel)
	bpy.utils.unregister_class(LinesDxfExportOperator)
	pass


import bpy
import bmesh

class LinesDxfExportPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "DXF Export"
	bl_label = "DXF Export Addon"
	# bl_context = "editmode"

	def draw(self, context):
		self.layout.prop(context.scene, "lines_dxf_export_file_path")
		self.layout.operator("object.lines_dxf_export")

	@classmethod
	def register(cls):
		pass

	@classmethod
	def unregister(cls):
		pass

class LinesDxfExportOperator(bpy.types.Operator):
	bl_idname = "object.lines_dxf_export"
	bl_label = "Export Selected Edges to DXF"

	def execute(self, context):
		file_path = context.scene.lines_dxf_export_file_path
		exprt = LinesDxfExporter()
		if (file_path):
			exprt.export(file_path)
			del exprt
			return {'FINISHED'}
		
		self.report(type = {'ERROR_INVALID_INPUT'}, message = "Empty path to DXF file output" )
		return {'CANCELLED'}

		

	@classmethod
	def register(cls):
		bpy.types.Scene.lines_dxf_export_file_path = bpy.props.StringProperty(
			name = "Path to DXF file output",
			description = "path to dxf file",
			default = ''
		)

	@classmethod
	def unregister(cls):
		pass


class LinesDxfExporter():
	def __init__(self):
		pass

	def export(self, filename):
		lines = self._get_lines()
		content = self._gen_dxf(lines)

		with open(filename, 'w') as f:
			f.write(content)


	def _get_lines(self):
		bm = bmesh.from_edit_mesh(bpy.context.object.data)
		lines = []
		for e in bm.edges:
			if e.select:
				line = []
				for v in e.verts:
					line.append(v.co)
				lines.append(line)
		return lines

	def _gen_dxf(self, lines):
		header = "0\nSECTION\n2\nENTITIES"
		footer = "0\nENDSECT\n0\nEOF"

		line_fmt = "\n0\nLINE\n8\n 0\n10\n{}\n20\n{}\n30\n{}\n11\n{}\n21\n{}\n31\n{}"

		content = ""


		for line in lines:
			if len(line) == 2:
				x1 = '{:.3f}'.format(round(line[0][0], 3))
				y1 = '{:.3f}'.format(round(line[0][1], 3))
				z1 = '{:.3f}'.format(round(line[0][2], 3))

				x2 = '{:.3f}'.format(round(line[1][0], 3))
				y2 = '{:.3f}'.format(round(line[1][1], 3))
				z2 = '{:.3f}'.format(round(line[1][2], 3))
				content += line_fmt.format(x1, y1, z1, x2, y2, z2)

		return header + content + footer
		print(header + content + footer)