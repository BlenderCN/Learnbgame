bl_info = {
 "name": "TexTools Unit Testing",
 "description": "Automated testing for TexTools tools",
 "author": "renderhjs",
 "blender": (2, 7, 9),
 "version": (1, 0, 0),
 "category": "Learnbgame",
 "location": "Viewport > Tool shelf"
}

# Import local modules
# More info: https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Multi-File_packages
if "bpy" in locals():
	import imp
	imp.reload(utilities)
	imp.reload(tests_panel_size)
else:
	from . import utilities
	from . import tests_panel_size
	
import bpy

# Test Categories
# tests_size = []
# tests_layout = []
# tests_mesh = []
# tests_baking = []
# tests_color = []

tests = [
	['Size', tests_panel_size.tests]
]
# {
# 	'0_size':tests_size, 
# 	'1_layout':tests_layout, 
# 	'2_mesh':tests_mesh, 
# 	'3_baking':tests_baking, 
# 	'4_color':tests_color
# }

# tests_size.append( TT_Test('op_uv_resize', call=None))
# tests_size.append( TT_Test('op_texture_reload_all', call=None))
# tests_size.append( TT_Test('uv_channel', call=None))
# tests_size.append( TT_Test('op_uv_channel_add', call=None))
# tests_size.append( TT_Test('op_uv_channel_swap', call=None))

# tests_layout.append( TT_Test('op_island_align_edge', call=None))
# tests_layout.append( TT_Test('op_rectify', call=None))
# tests_layout.append( TT_Test('op_island_rotate_90', call=None))
# tests_layout.append( TT_Test('op_align', call=None))
# tests_layout.append( TT_Test('op_island_align_sort', call=None))
# tests_layout.append( TT_Test('op_unwrap_faces_iron', call=None))
# tests_layout.append( TT_Test('op_unwrap_peel_edge', call=None))
# tests_layout.append( TT_Test('op_select_islands_identical', call=None))
# tests_layout.append( TT_Test('op_select_islands_overlap', call=None))
# tests_layout.append( TT_Test('op_select_islands_outline', call=None))
# tests_layout.append( TT_Test('op_select_islands_flipped', call=None))
# tests_layout.append( TT_Test('op_textools_texel_checker_map', call=None))
# tests_layout.append( TT_Test('op_texel_density_get', call=None))
# tests_layout.append( TT_Test('op_texel_density_set', call=None))

# tests_baking.append( TT_Test('op_bake mode: ao', call=None))
# tests_baking.append( TT_Test('op_bake mode: cavity', call=None))
# tests_baking.append( TT_Test('op_bake mode: curvature', call=None))
# tests_baking.append( TT_Test('op_bake mode: diffuse', call=None))
# tests_baking.append( TT_Test('op_bake mode: displacment', call=None))
# tests_baking.append( TT_Test('op_bake mode: dust', call=None))
# tests_baking.append( TT_Test('op_bake mode: id_element', call=None))
# tests_baking.append( TT_Test('op_bake mode: id_material', call=None))
# tests_baking.append( TT_Test('op_bake mode: normal_object', call=None))
# tests_baking.append( TT_Test('op_bake mode: normal_tangent', call=None))
# tests_baking.append( TT_Test('op_bake mode: position', call=None))
# tests_baking.append( TT_Test('op_bake mode: selection', call=None))
# tests_baking.append( TT_Test('bake_sampling', call=None))
# tests_baking.append( TT_Test('bake_force_single', call=None))
# tests_baking.append( TT_Test('bake_force_single', call=None))
# tests_baking.append( TT_Test('op_select_bake_type', call=None))
# tests_baking.append( TT_Test('op_bake_organize_names', call=None))
# tests_baking.append( TT_Test('op_bake_explode', call=None))

# tests_mesh.append( TT_Test('op_smoothing_uv_islands', call=None))
# tests_mesh.append( TT_Test('op_mesh_texture', call=None))

def get_test(id_group, id_test):
	if id_group < len(tests):
		if id_test < len(tests[id_group][1]):
			return tests[id_group][1][id_test]
	return None



class op_find_blend(bpy.types.Operator):
	bl_idname = "textools.testing_findblend"
	id_group = bpy.props.IntProperty(default=0)
	id_test = bpy.props.IntProperty(default=0)
	bl_label = "Bake"
	def execute(self, context):
		test = get_test(self.id_group, self.id_test)
		if test:
			test.open_blend()
			return {'FINISHED'}	
		return {'CANCELLED'}



class op_find_python(bpy.types.Operator):
	bl_idname = "textools.testing_findpython"
	id_group = bpy.props.IntProperty(default=0)
	id_test = bpy.props.IntProperty(default=0)
	bl_label = "Bake"
	def execute(self, context):
		test = get_test(self.id_group, self.id_test)
		if test:
			test.open_python()
			return {'FINISHED'}	
		return {'CANCELLED'}



class op_run(bpy.types.Operator):
	bl_idname = "textools.testing_run"
	id_group = bpy.props.IntProperty(default=0)
	id_test = bpy.props.IntProperty(default=0)
	bl_label = "Bake"
	def execute(self, context):
		test = get_test(self.id_group, self.id_test)
		if test:
			test.run()
			return {'FINISHED'}	
		return {'CANCELLED'}



class op_run_all(bpy.types.Operator):
	bl_idname = "textools.testing_runall"
	bl_label = "Bake"
	def execute(self, context):
		print ("Run All")
		
		return {'FINISHED'}



class texTools_panel_testing(bpy.types.Panel):

	bl_idname = "textools_testing"
	bl_label = "TexTools Testing"
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	# bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):

		layout = self.layout
		layout.label(text="dsadas ")
		count = len( [test for collection in tests for test in collection[1]] )
		layout.operator(op_run_all.bl_idname, text="Run all {}x tests".format(count), icon='PLAY')
		# layout.separator()

		for i in range(len(tests)):
		# for collection in tests:
			collection = tests[i]
			count = len(collection[1])
			row = layout.row(align=True)
			row.label(text="{} {}x".format(collection[0], count))
			# row.operator(op_run_all.bl_idname, text="Run {}x".format(count), icon='PLAY')
			
			if count > 0:
				box = layout.box()
				col = box.column(align=True)
				for j in range(len(collection[1])):
				# for test in collection[1]:
					test = collection[1][j]
					row = col.row(align=True)
					
					if test.test != None:
						op = row.operator(op_run.bl_idname, text="", icon='PLAY')
						op.id_group = i
						op.id_test = j

					row.label(test.name)
					
					if test.blend != "":
						row.operator(op_find_blend.bl_idname, text="", icon='BLENDER')
						op.id_group = i
						op.id_test = j

					if test.python != "":
						op = row.operator(op_find_python.bl_idname, text="", icon='FILE_TEXT')
						op.id_group = i
						op.id_test = j


def export_FBX(path):

	print("Export: " + path)

	# Export
	bpy.ops.export_scene.fbx(
		filepath=path + ".fbx", 
		use_selection=True, 
		
		axis_forward='-Z', 
		axis_up='Y', 
		
		global_scale =0.01, 
		use_mesh_modifiers=True, 
		mesh_smooth_type='OFF', 
		batch_mode='OFF', 
		use_custom_props=True)



# registers
def register():
	bpy.utils.register_class(texTools_panel_testing)
	bpy.utils.register_class(op_run)
	bpy.utils.register_class(op_run_all)
	bpy.utils.register_class(op_find_blend)
	bpy.utils.register_class(op_find_python)
	


def unregister():
	bpy.utils.unregister_class(texTools_panel_testing)
	bpy.utils.unregister_class(op_run_all)
	bpy.utils.unregister_class(op_run)
	bpy.utils.unregister_class(op_find_blend)
	bpy.utils.unregister_class(op_find_python)
	

if __name__ == "__main__":
	register()
