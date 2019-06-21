#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

bl_info = {
	"name": "render check list + misc",
	"author": "bookyakuno",
	"version": (1, 0, 3),
	"blender": (2, 79),
	"location": "Dimensions",
	"description": "render check list + misc",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame",
}

import bpy

from bpy.props import (BoolProperty,
					   FloatProperty,
					   FloatVectorProperty,
					   StringProperty,
					   PointerProperty)

from bpy.props import *




class set_f(bpy.types.Operator):
   bl_idname = "object.set_f"
   bl_label = "set_f"
   bl_description = "Change the number of sheets"
   def execute(self, context):

	   scn = context.scene

	   set_f = scn.frame_start + scn.floatSample
	   scn.frame_end = set_f

	   return {'FINISHED'}

class now_f(bpy.types.Operator):
   bl_idname = "object.now_f"
   bl_label = "now_f"
   bl_description = "Current number of sheets"

   def execute(self, context):

	   scn = context.scene

	   scn.floatSample = scn.frame_end - scn.frame_start


	   return {'FINISHED'}





class SampleUI_PT_object(bpy.types.Panel):
	bl_label = "UI For Sample Prop"
	bl_context = "object"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"

	def draw(self, context):
		self.layout.prop(context.object.sample_props,"floatSample")

		layout = self.layout
		row = layout.row(align=True)
		row.operator("object.fff", text="fff")



class render_cycleslots(bpy.types.Operator):
	bl_idname = "object.render_cycleslots"
	bl_label = "render_cycleslots"
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Slots change every time rendering"

	def execute(self, context):


		slots = bpy.data.images['Render Result'].render_slots
		slots.active_index=(slots.active_index+1)%8
		#bpy.ops.render.render('EXECUTION_CONTEXT')
		bpy.ops.render.render('INVOKE_DEFAULT')
		return {'FINISHED'}


class x_y_change(bpy.types.Operator):
	bl_idname = "object.x_y_change"
	bl_label = "X-Y"

	def execute(self, context):
#        main(context)
		old_x = bpy.context.scene.render.resolution_x
		old_y = bpy.context.scene.render.resolution_y
		mainScreen = bpy.context.screen
		scene = mainScreen.scene
		scene.render.resolution_x = old_y
		scene.render.resolution_y = old_x

		return {'FINISHED'}




def render_final_resolution_ui_z(self, context):



# =====================================================
# ↓=====================================================

	layout = self.layout

	scene = context.scene
	rd = scene.render

	row = layout.row(align=True)
	row.menu("RENDER_MT_presets", text=bpy.types.RENDER_MT_presets.bl_label)
	row.operator("render.preset_add", text="", icon='ZOOMIN')
	row.operator("render.preset_add", text="", icon='ZOOMOUT').remove_active = True

	split = layout.split()

	col = split.column()
	sub = col.column(align=True)
	subrow = sub.row(align=True)

	# subrow.label(text="Resolution:")

	rd = context.scene.render
	layout = self.layout

	final_res_x = (rd.resolution_x * rd.resolution_percentage) / 100
	final_res_y = (rd.resolution_y * rd.resolution_percentage) / 100

	if rd.use_border:
		final_res_x_border = round(
		(final_res_x * (rd.border_max_x - rd.border_min_x)))
		final_res_y_border = round(
		(final_res_y * (rd.border_max_y - rd.border_min_y)))
		subrow.label(text="{} x {} [B:{} x {}]".format(
		str(final_res_x)[:-2], str(final_res_y)[:-2],
		str(final_res_x_border), str(final_res_y_border)))
	else:
		subrow.label(text="{} x {}".format(
		str(final_res_x)[:-2], str(final_res_y)[:-2]))

	subrow.operator("object.x_y_change", text="", icon="FILE_REFRESH")


	sub.prop(rd, "resolution_x", text="X")
	sub.prop(rd, "resolution_y", text="Y")
	sub.prop(rd, "resolution_percentage", text="")
	sub.separator()


	row = col.row()
	row.prop(rd, "use_border", text="", icon="BORDER_RECT")
	sub = row.row()
	sub.active = rd.use_border
	sub.prop(rd, "use_crop_to_border", text="",icon="RENDER_REGION")


	scn = context.scene
	tt = scn.frame_end - scn.frame_start
	# row = layout.row(align=True)
	sub.label()
	col = split.column()
	sub = col.column(align=True)
	sub.label(text="Frame Range:    " + str(tt))
	# =====================================================

	sub.prop(scene, "frame_start")
	sub.prop(scene, "frame_end")
	sub.separator()
	sub.prop(scene, "frame_current")
	sub.separator()

	subrow = sub.row(align=True)

	subrow.operator("object.now_f", text="",icon="EYEDROPPER")
	subrow.operator("object.set_f", text="",icon="FILE_TICK")
	subrow.prop(scene, "floatSample", text="")




# ↑=====================================================
# =====================================================



	layout = self.layout
	scene = context.scene
	cscene = scene.cycles
	rd = context.scene.render



	col = layout.column(align=True)
	row = col.row(align=True)




	row.operator_context = 'EXEC_DEFAULT'
	row.operator("render.render", text="Render", icon='RENDER_STILL')
	row.operator("object.render_cycleslots", text="Slot", icon="RENDER_REGION")
	row.operator("render.render", text="Animation", icon='RENDER_ANIMATION').animation = True
	row.prop(rd, "use_lock_interface", icon_only=True)
	row = col.row(align=True)






	# col = split.column()
	row = col.row(align=True)

	row.prop(cscene, "film_transparent", text="BG Alpha", icon="WORLD")
	row.prop(rd, "use_overwrite", icon="ORTHO")

	split = layout.split()
	row = col.row(align=True)
	row.prop(context.scene, 'save_after_render', text='Auto Save Image', icon="IMAGE_DATA", toggle=False)

	row.prop(cscene, "use_square_samples", icon="IPO_QUAD")





	row = col.row(align=True)
	row.prop(rd, "use_stamp", icon="OUTLINER_DATA_FONT")
	row.prop(cscene, "samples", text="samples")


	row = col.row(align=True)
	row.prop(rd, "use_persistent_data", text="Persistent Images")

	row.prop(cscene, "preview_samples", text="Preview")


	# draw_samples_info(layout, context)









# =====================================================

# =====================================================

	sub.label()
	col = split.column()
	sub = col.column(align=True)


	sub.prop(scene, "frame_step")





	sub.label(text="Frame Rate:")

	self.draw_framerate(sub, rd)


	sub.label()
	col = split.column()
	sub = col.column(align=True)


	subrow = sub.row(align=True)
	subrow.label(text="Time Remapping:")
	subrow = sub.row(align=True)
	subrow.prop(rd, "frame_map_old", text="Old")
	subrow.prop(rd, "frame_map_new", text="New")


	sub.label(text="Aspect Ratio:")
	sub.prop(rd, "pixel_aspect_x", text="X")
	sub.prop(rd, "pixel_aspect_y", text="Y")


	# =====================================================

	# =====================================================


	# =====================================================

	# =====================================================


	original_draw_func = None

def register():
	bpy.utils.register_module(__name__)

	global original_draw_func
	original_draw_func = bpy.types.RENDER_PT_dimensions.draw
	bpy.types.RENDER_PT_dimensions.draw = render_final_resolution_ui_z



	bpy.types.Scene.floatSample = IntProperty(name="FloatPropSample", description="Number of sheets to be rendered", min=0, default=0)




def unregister():
	bpy.types.RENDER_PT_dimensions.remove(render_final_resolution_ui_z)




if __name__ == "__main__":
	register()
