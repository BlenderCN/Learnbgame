bl_info = {
	"name": "Sketchup to Cities: Skylines Helper",
	"description": "Helps the user convert SketchUp assets to a format recognizable by Cities: Skylines. Created by CosignCosine (Elektrix on ST)",
	"author": "CosignCosine (Elektrix)",
	"version": (0, 5, 0),
	"location": "Properties > Scene",
	"warning": "This tool is still in beta.",
	"wiki_url": "https://community.simtropolis.com/profile/745638-elektrix/",
	"support": "COMMUNITY",
	"category": "UV"
}

import bpy, time

# Operators
class SCSHAll(bpy.types.Operator):
	bl_idname = "cosigncosine.scsh_all"
	bl_label = "Quick Convert"

	def execute(self, context):
		bpy.ops.cosigncosine.scsh_rm_sk_cm()
		self.report({'INFO'}, "Removed Sketchup Camera (1/5)")
		bpy.ops.cosigncosine.scsh_caaa()
		self.report({'INFO'}, "Created Texture Atlas (2/5)")
		bpy.ops.object.ms_auto()
		self.report({'INFO'}, "Unwrapped All to Atlas (3/5)")
		bpy.ops.cosigncosine.scsh_sk_rd()
		self.report({'INFO'}, "Marked Correct UVs as Renderable (4/5)")
		bpy.ops.cosigncosine.scsh_btta()
		self.report({'INFO'}, "Done! (5/5))")
		return {"FINISHED"}

class SCSHBlankCanvas(bpy.types.Operator):
	bl_idname = "cosigncosine.scsh_bl_cv"
	bl_label = "Blank Canvas"
	bl_options = {"UNDO"}

	def execute(self, context):
		bpy.ops.object.select_all(action='DESELECT')
		bpy.ops.object.select_all()
		bpy.ops.object.delete()
		return {"FINISHED"}

class SCSHRemoveSketchupCamera(bpy.types.Operator):
	bl_idname = "cosigncosine.scsh_rm_sk_cm"
	bl_label = "Remove Cameras"

	def execute(self, context):
		# remove all cameras
		bpy.ops.object.select_by_type(type='CAMERA')
		bpy.ops.object.delete()
		return {"FINISHED"}

class SCSH_TACreateAndAddAll(bpy.types.Operator):
	bl_idname = "cosigncosine.scsh_caaa"
	bl_label = "Create Atlas; Add All"

	def execute(self, context):
		# create texture atlas (may require ta plugin, not sure)
		bpy.ops.object.select_all(action='DESELECT')
		bpy.ops.object.select_all()
		bpy.ops.scene.ms_add_lightmap_group()
		bpy.data.scenes["Scene"].ms_lightmap_groups[0].resolutionX = "16384"
		bpy.data.scenes["Scene"].ms_lightmap_groups[0].resolutionY = "16384"

		# add all to texture atlas
		bpy.ops.scene.ms_add_selected_to_group()
		return {"FINISHED"}


class SCSHRenderableOperator(bpy.types.Operator):
	bl_idname = "cosigncosine.scsh_sk_rd"
	bl_label = "Batch Mark Correct UVs as Renderable"
	bl_options = {"UNDO"}

	def execute(self, context):
		st = time.clock()
		for mesh in bpy.data.meshes:
			if len(mesh.uv_textures) < 2:
				bpy.data.meshes.remove(mesh)
				bpy.context.scene.update()
				continue
			mesh.uv_textures[[i for i, texture in enumerate(mesh.uv_textures) if texture.name.startswith('ID')][0]].active_render = True
		ms = "Completed %i meshes in %f seconds." % (len(bpy.data.meshes), time.clock() - st)
		self.report({'INFO'}, ms)
		return {"FINISHED"}

class SCSHBakeToTextureAtlas(bpy.types.Operator):
	bl_idname = "cosigncosine.scsh_btta"
	bl_label = "Bake to Texture Atlas"

	def execute(self, context):
		# set bake options
		bpy.data.scenes["Scene"].render.bake_type = 'TEXTURE'
		bpy.data.scenes["Scene"].render.bake_margin = 0

		# select all (prepare for bake)
		bpy.ops.object.select_all(action='DESELECT')
		bpy.ops.object.select_all()
		bpy.context.scene.objects.active = bpy.data.objects["SketchUp"]

		# bake
		bpy.ops.object.bake_image()

		# join and remove other uvs (split into other operator? discuss.)
		bpy.ops.object.join()
		bpy.ops.scene.ms_remove_other_uv()
		return {"FINISHED"}

# Panels
class SCSHMainPanel(bpy.types.Panel):
	bl_idname = "cosigncosine.scsh_mainpanel"
	bl_label = "Sketchup to Cities: Skylines"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"

	def draw(self, context):
		scsh_a = self.layout.column(align=True)
		scsh_a.label(text="Setup", icon="MODIFIER")
		scsh_a.operator("cosigncosine.scsh_bl_cv", text="Blank Canvas", icon="CANCEL")

		scsh_b = self.layout.column(align=True)
		scsh_b.label(text="Automatic", icon="NEXT_KEYFRAME")
		scsh_b.operator("cosigncosine.scsh_all", text="Quick Convert", icon="SOLO_ON")

		scsh_c = self.layout.column(align=True)
		scsh_c.label(text="Manual", icon="VIEWZOOM")
		scsh_c.operator("cosigncosine.scsh_rm_sk_cm", text="Remove Cameras", icon="CAMERA_DATA")
		scsh_c.operator("cosigncosine.scsh_caaa", text="Create Atlas; Add All", icon="OUTLINER_OB_GROUP_INSTANCE")
		scsh_c.operator("object.ms_auto", text="Auto Unwrap to Atlas", icon="LAMP_SPOT")
		scsh_c.operator("cosigncosine.scsh_sk_rd", text="Batch Mark Correct UVs as Renderable", icon="GROUP_UVS")
		scsh_c.operator("cosigncosine.scsh_btta", text="Bake to Atlas", icon="RENDER_STILL")

# Registration

def register():
	print("SCSH Added")
	bpy.utils.register_class(SCSHRenderableOperator);
	bpy.utils.register_class(SCSHBlankCanvas);
	bpy.utils.register_class(SCSHRemoveSketchupCamera);
	bpy.utils.register_class(SCSH_TACreateAndAddAll);
	bpy.utils.register_class(SCSHBakeToTextureAtlas);
	bpy.utils.register_class(SCSHAll);
	bpy.utils.register_class(SCSHMainPanel);
def unregister():
	print("SCSH Removed")
	bpy.utils.unregister_class(SCSHRenderableOperator);
	bpy.utils.unregister_class(SCSHBlankCanvas);
	bpy.utils.unregister_class(SCSHRemoveSketchupCamera);
	bpy.utils.unregister_class(SCSH_TACreateAndAddAll);
	bpy.utils.unregister_class(SCSHBakeToTextureAtlas);
	bpy.utils.unregister_class(SCSHAll);
	bpy.utils.unregister_class(SCSHMainPanel);
