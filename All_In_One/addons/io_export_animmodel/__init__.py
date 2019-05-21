bl_info = {
	"name":         "AnimModel format",
	"author":       "Istvan Jung",
	"blender":      (2,80,0),
	"version":      (0,1,0),
	"location":     "File > Import-Export",
	"description":  "Export into AnimModel format",
	"warning": "",
	"category":     "Import-Export"
}
		
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import (BoolProperty, IntProperty)

if "bpy" in locals():
	import imp
	if "export_animmodel" in locals():
		imp.reload(export_animmodel)

class ExportMyFormat(bpy.types.Operator, ExportHelper):
	bl_idname       = "export_my_format.amf"
	bl_label        = "Export"
	bl_options      = {'PRESET'}
	filename_ext    = ".amf"

	p_export_selection_only = BoolProperty(
		name="Export Selection Only?", default=False,
		description="If checked, only selected objects will be exports. Otherwise every object will be exported.")
	p_apply_modifiers = BoolProperty(
		name="Apply modifiers?", default=True,
		description="If checked, modifiers will be applied on exported objects.")
	p_export_animation = BoolProperty(
		name="Export animation?", default=True,
		description="If checked, animation will be exported from start frame to end frame (set on Blender's timeline).")
	p_export_global_matrix = BoolProperty(
		name="Use global matrix?", default=True,
		description="If checked, object's coordinates will be exported in world space, otherwise in object space.")
	p_export_uv = BoolProperty(
		name="Export UV?", default=True,
		description="If checked, UV coordinates will be exported.")
	p_frame_skip = IntProperty(
		name="Frame skip", default=0, min=0, max=255,
		description="Export every n-th frame.")
	p_export_vertex_groups = BoolProperty(
		name="Export Vertex Groups?", default=True,
		description="If checked, Vertex groups will be exported.")
		
	def execute(self, context):
		from . import export_animmodel
		export_animmodel.write(self, context, self.filepath, self.p_export_animation, self.p_export_selection_only, self.p_apply_modifiers, self.p_export_global_matrix, self.p_export_uv, self.p_frame_skip, self.p_export_vertex_groups)
		return {'FINISHED'}

def menu_func(self, context):
	self.layout.operator(ExportMyFormat.bl_idname, text="AnimModel format(.amf)")

def register():
	bpy.utils.register_class(ExportMyFormat)
	bpy.types.TOPBAR_MT_file_export.append(menu_func)
	
def unregister():
	bpy.utils.unregister_class(ExportMyFormat)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
	register()