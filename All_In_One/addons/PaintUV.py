# bl_info
bl_info = {
	"name": "Paint UV islands",
	"author": "Nexus Studio",
	"version": (0,0,3),
	"blender": (2,79),
	"location": "T > Nexus Tools, Edit mesh > U > Unwrap and paint uv",
	"description": "Tools",
	"warning": "",
	"wiki_url": "None",
	"category": "User"
}

import bpy
from random import uniform


def MenuFuncUnwrap(self, context):
	self.layout.separator()
	self.layout.operator(MenuUnwrapOperator.bl_idname, text="Unwrap and paint uv", icon="VPAINT_HLT")

def SetRandomBrushColor():
	"""Generate random color to brush"""
	r = uniform(0.0, 1.0)
	g = uniform(0.0, 1.0)
	b = uniform(0.0, 1.0)
	bpy.data.brushes["Draw"].color = (r, g, b)


def IsWhiteVertex(color_map, index):
	""""Return True if vertex color equal white color (1.0, 1.0, 1.0)"""
	col = color_map.data[index].color
	return col[0] == 1.0 and col[1] == 1.0 and col[2] == 1.0


def CheckColorMapName(color_maps, FindName):
	for color_map in color_maps:
		if color_map.name == FindName:
			return True

	return False

def FindAndPaint():
	my_object = bpy.context.active_object.data

	my_object.use_paint_mask = True
	
	bpy.ops.object.mode_set( mode = 'EDIT' )
	bpy.ops.mesh.select_all( action = 'DESELECT' )
	bpy.ops.object.mode_set( mode = 'OBJECT' )

	color_map = ''
	# if not color map created else remove active color map and created new
	if not CheckColorMapName(my_object.vertex_colors, 'ISLANDS_PAINT'):
		color_map = my_object.vertex_colors.new()
		color_map.name = 'ISLANDS_PAINT'
		color_map.active = True
	else:
		my_object.vertex_colors['ISLANDS_PAINT'].active = True
		bpy.ops.mesh.vertex_color_remove()
		color_map = my_object.vertex_colors.new()
		color_map.name = 'ISLANDS_PAINT'
	polygons = my_object.polygons

	index = 0
	for poly in polygons:
		print("Index poly: ", poly.index)
		for idx in poly.loop_indices:
			if IsWhiteVertex(color_map, index):
				bpy.ops.object.mode_set(mode='VERTEX_PAINT')
				bpy.ops.paint.face_select_all( action = 'DESELECT' )
				poly.select = True
				bpy.ops.paint.face_select_linked()
				SetRandomBrushColor()
				bpy.ops.paint.vertex_color_set()
				bpy.ops.object.mode_set(mode='OBJECT')
			index += 1

	bpy.ops.object.mode_set(mode='VERTEX_PAINT')
	bpy.ops.paint.face_select_all( action = 'DESELECT' )

class PaintUVPanel(bpy.types.Panel):
	"""Creates a Panel in the view3d context of the tools panel (key "T")"""
	bl_label = "Paint UV"
	bl_idname = "paintuvid"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Nexus Tools"
	bl_context = "objectmode"

	def draw(self, context):
		layout = self.layout
		obj = context.object
		scene = context.scene

		row = layout.row()
		row.operator("object.paint_uv", text="Paint by UV")


class PaintUVOperator(bpy.types.Operator):
	"""Paint all UV islands"""
	bl_label = "Paint UV"
	bl_idname = "object.paint_uv"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def execute(self, context):
		FindAndPaint()

		return {'FINISHED'}

class MenuUnwrapOperator(bpy.types.Operator):
	"""Unwrap and paint all UV islands"""
	bl_label = "Unwrap and paint UV"
	bl_idname = "uv.unwrap_paint_uv"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == "EDIT_MESH"

	def execute(self, context):
		bpy.ops.uv.unwrap()
		FindAndPaint()

		return {'FINISHED'}

def register():
	bpy.utils.register_class(PaintUVPanel)
	bpy.utils.register_class(PaintUVOperator)
	bpy.utils.register_class(MenuUnwrapOperator)
	bpy.types.VIEW3D_MT_uv_map.append(MenuFuncUnwrap)

def unregister():
	bpy.utils.unregister_class(PaintUVPanel)
	bpy.utils.unregister_class(PaintUVOperator)
	bpy.utils.unregister_class(MenuUnwrapOperator)
	bpy.types.VIEW3D_MT_uv_map.remove(MenuFuncUnwrap)

if __name__ == "__main__":
	register()