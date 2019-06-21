bl_info = {
	"name": "Set All Fake Users",
	"author": "Kenetics",
	"version": (0, 1),
	"blender": (2, 80, 0),
	"location": "File Menu > Set All Fake Users",
	"description": "Sets fake users in blend data",
	"warning": "Doesn't update GUI after running, you have to update GUI manually by mousing over windows.'",
	"wiki_url": "",
	"category": "Learnbgame",
}

import bpy
from bpy.props import EnumProperty, BoolProperty

def set_fake_users_in_data(datablock, action):
	for data in datablock:
		data.use_fake_user = action


class RAFU_OT_SetAllFakeUsers(bpy.types.Operator):
	"""Removes fake users from images, objects, mesh data, and curve data"""
	bl_idname = "system.rafu_ot_set_all_fake_users"
	bl_label = "Set All Fake Users"
	bl_options = {'REGISTER','UNDO'}

	# Properties
	action : EnumProperty(
		items=[
			("0","Remove","Removes fake users","ZOOMOUT",0),
			("1","Add","Adds fake users","ZOOMIN",1),
			],
		name="Action",
		description="Add/Remove fake users in datablocks",
		default="0"
	)
	
	set_brush : BoolProperty(
		name="Brushes",
		description="Sets fake users for all brush data",
		default=True
	)
	
	set_camera : BoolProperty(
		name="Cameras",
		description="Sets fake users for all camera data",
		default=True
	)

	set_curve : BoolProperty(
		name="Curves",
		description="Sets fake users for all curve data",
		default=True
	)

	set_font : BoolProperty(
		name="Fonts",
		description="Sets fake users for all font data",
		default=True
	)
	
	set_image : BoolProperty(
		name="Images",
		description="Sets fake users for all image data",
		default=True
	)
	
	set_light : BoolProperty(
		name="Lights",
		description="Sets fake users for all light data",
		default=True
	)
	
	set_lattice : BoolProperty(
		name="Lattices",
		description="Sets fake users for all lattice data",
		default=True
	)
	
	set_mask : BoolProperty(
		name="Masks",
		description="Sets fake users for all mask data",
		default=True
	)
	
	set_material : BoolProperty(
		name="Materials",
		description="Sets fake users for all material data",
		default=True
	)
	
	set_mesh : BoolProperty(
		name="Meshes",
		description="Sets fake users for all mesh data",
		default=True
	)
	
	set_metaball : BoolProperty(
		name="Metaballs",
		description="Sets fake users for all metaball data",
		default=True
	)

	set_movieclip : BoolProperty(
		name="Movieclips",
		description="Sets fake users for all movieclip data",
		default=True
	)

	set_node_group : BoolProperty(
		name="Node Groups",
		description="Sets fake users for all node group data",
		default=True
	)
	
	set_object : BoolProperty(
		name="Objects",
		description="Sets fake users for all object data",
		default=True
	)
	
	set_particle : BoolProperty(
		name="Particles",
		description="Sets fake users for all particle data",
		default=True
	)
	
	set_texture : BoolProperty(
		name="Textures",
		description="Sets fake users for all texture data",
		default=True
	)
	
	set_world : BoolProperty(
		name="Worlds",
		description="Sets fake users for all world data",
		default=True
	)

	@classmethod
	def poll(cls, context):
		return True

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		action = bool(int(self.action))
		
		if self.set_brush:
			set_fake_users_in_data(context.blend_data.brushes, action)
		if self.set_camera:
			set_fake_users_in_data(context.blend_data.cameras, action)
		if self.set_curve:
			set_fake_users_in_data(context.blend_data.curves, action)
		if self.set_font:
			set_fake_users_in_data(context.blend_data.fonts, action)
		if self.set_image:
			set_fake_users_in_data(context.blend_data.images, action)
		if self.set_light:
			set_fake_users_in_data(context.blend_data.lights, action)
		if self.set_lattice:
			set_fake_users_in_data(context.blend_data.lattices, action)
		if self.set_mask:
			set_fake_users_in_data(context.blend_data.masks, action)
		if self.set_material:
			set_fake_users_in_data(context.blend_data.materials, action)
		if self.set_mesh:
			set_fake_users_in_data(context.blend_data.meshes, action)
		if self.set_metaball:
			set_fake_users_in_data(context.blend_data.metaballs, action)
		if self.set_movieclip:
			set_fake_users_in_data(context.blend_data.movieclips, action)
		if self.set_node_group:
			set_fake_users_in_data(context.blend_data.node_groups, action)
		if self.set_object:
			set_fake_users_in_data(context.blend_data.objects, action)
		if self.set_particle:
			set_fake_users_in_data(context.blend_data.particles, action)
		if self.set_texture:
			set_fake_users_in_data(context.blend_data.textures, action)
		if self.set_world:
			set_fake_users_in_data(context.blend_data.worlds, action)
		
		return {'FINISHED'}


def set_fake_users_button(self, context):
	self.layout.operator(RAFU_OT_SetAllFakeUsers.bl_idname)
	#self.layout.operator(RAFU_OT_SetAllFakeUsers.bl_idname, text="New (Load UI)", icon='ZOOM_ALL').load_ui = True

def register():
	bpy.utils.register_class(RAFU_OT_SetAllFakeUsers)
	bpy.types.TOPBAR_MT_file_external_data.append(set_fake_users_button)

def unregister():
	bpy.types.TOPBAR_MT_file_external_data.remove(set_fake_users_button)
	bpy.utils.unregister_class(RAFU_OT_SetAllFakeUsers)

if __name__ == "__main__":
	register()
