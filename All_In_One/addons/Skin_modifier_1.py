bl_info = {
	"name": "Vertice con skin y sursubf y mirror",
	"author": "Jose Ant. Garcia <garciagaete@gmail.com>",
	"version": (1, 0, 1),
	"blender": (2, 7, 2),
	"location": "View 3D > Tool Shelf",
	"description": "Vertice con skin y sursubf y mirror",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"support": "COMMUNITY",
	"category": "3D View",
}

import bpy
from bpy.props import *



class VerticeSkin(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Sculpt"
	bl_context = "objectmode"
	bl_label = "Skin Modifiers"
	
	def draw(self, context):
		wm = context.window_manager
		c = self.layout.column(align=True)
		
		c.operator("object.vertice")
		box = c.column(align=True).box().column()
		box.prop(wm,"Espejo","use mirror")
		box.prop(wm,"Dividir","use surface")
		if wm.Dividir==True:
			c.prop(wm,"CDivisiones","Subdivisions:")

class VerticeSkin(bpy.types.Operator):
	bl_idname = "object.vertice"
	bl_label = "Vertice con skin"
	bl_options = {"UNDO"}
	bl_description = "Vertice con skin y sursubf y mirror"



	
	def execute(self, context):

		wm = context.window_manager
		
		mesh = bpy.data.meshes.new("")
		mesh.from_pydata([context.scene.cursor_location], [], [])
		mesh.update()
		obj = bpy.data.objects.new("", mesh)
		context.scene.objects.link(obj)
		bpy.ops.object.select_all(action = "DESELECT")
		obj.select = True
		context.scene.objects.active = obj
		bpy.ops.object.mode_set(mode="EDIT")

		bpy.ops.object.modifier_add(type="SKIN")
		if wm.Espejo==True:
			bpy.ops.object.modifier_add(type="MIRROR")
		if wm.Dividir==True:
			bpy.ops.object.modifier_add(type="SUBSURF")
			bpy.context.object.modifiers["Subsurf"].levels = wm.CDivisiones

		return {"FINISHED"}


def register():
	bpy.utils.register_module(__name__)
	bpy.types.WindowManager.vertice_func = BoolProperty(default=False)	
	bpy.types.WindowManager.Espejo = BoolProperty(default=True)
	bpy.types.WindowManager.Dividir = BoolProperty(default=False)
	bpy.types.WindowManager.CDivisiones = IntProperty(min = 1, max = 3 ,default = 1)


def unregister():
	bpy.utils.unregister_module(__name__)

if __name__=="__main__":
	register()




 
