import bpy

bl_info = {
	"name": "Auto Delete :)",
	"location": "View3D > Add > Mesh > Auto Delete,",
	"description": "Auto detect a delete elements",
	"author": "Vladislav Kindushov",
	"version": (0, 2),
	"blender": (2, 80, 0),
	"category": "Learnbgame",
}

obj = None
mesh = None


def find_connected_verts(me, found_index):
	edges = me.edges
	connecting_edges = [i for i in edges if found_index in i.vertices[:]]
	# print('connecting_edges',len(connecting_edges))
	return len(connecting_edges)


class AutoDelete_OT_darcvizer(bpy.types.Operator):
	""" Dissolves mesh elements based on context instead
	of forcing the user to select from a menu what
	it should dissolve.
	"""
	bl_idname = "mesh.autodelete_ot_darcvizer"
	bl_label = "Auto Delete"
	bl_options = {'UNDO'}

	use_verts = bpy.props.BoolProperty(name="Use Verts", default=False)

	@classmethod
	def poll(cls, context):
		return context.space_data.type == "VIEW_3D"

	# return (context.active_object is not None)# and (context.mode == "EDIT_MESH")

	def execute(self, context):
		if bpy.context.mode == 'OBJECT':
			sel = bpy.context.selected_objects

			bpy.ops.object.delete(use_global=True)
		# print ('fdfsd')
		elif bpy.context.mode == 'EDIT_MESH':
			select_mode = context.tool_settings.mesh_select_mode
			me = context.object.data
			if select_mode[0]:
				vertex = me.vertices

				bpy.ops.mesh.dissolve_verts()

				if vertex == me.vertices:
					bpy.ops.mesh.delete(type='VERT')


			elif select_mode[1] and not select_mode[2]:
				edges1 = me.edges

				bpy.ops.mesh.dissolve_edges(use_verts=True, use_face_split=False)
				if edges1 == me.edges:
					bpy.ops.mesh.delete(type='EDGE')

				bpy.ops.mesh.select_mode(type='EDGE')

				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.mode_set(mode='EDIT')
				vs = [v.index for v in me.vertices if v.select]
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')

				for v in vs:
					vv = find_connected_verts(me, v)
					if vv == 2:
						me.vertices[v].select = True
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.dissolve_verts()
				bpy.ops.mesh.select_all(action='DESELECT')

				for v in vs:
					me.vertices[v].select = True


			elif select_mode[2] and not select_mode[1]:
				bpy.ops.mesh.delete(type='FACE')
			else:
				bpy.ops.mesh.dissolve_verts()

		elif bpy.context.mode == 'EDIT_CURVE':
			print("ere")
			bpy.ops.curve.delete(type='VERT')
		return {'FINISHED'}


# bpy.utils.register_class(MeshDissolveContextual_OT_vlad)

classes = (AutoDelete_OT_darcvizer,)


def register():
	for c in classes:
		bpy.utils.register_class(c)
	global obj
	global mesh

	activConfig = bpy.context.window_manager.keyconfigs.active.name
	wm = bpy.context.window_manager
	keymaps_3DV = wm.keyconfigs[activConfig].keymaps['Object Mode']
	keymap = keymaps_3DV.keymap_items['object.delete']
	obj = keymap.idname
	keymap.idname = 'mesh.autodelete_ot_darcvizer'
	keymaps_3DV = wm.keyconfigs[activConfig].keymaps['Mesh']

	i = 0
	while (True):
		print(bpy.context.window_manager.keyconfigs[activConfig].keymaps['Mesh'].keymap_items[i].type)
		if bpy.context.window_manager.keyconfigs[activConfig].keymaps['Mesh'].keymap_items[i].type == 'X':
			mesh = bpy.context.window_manager.keyconfigs[activConfig].keymaps['Mesh'].keymap_items[i].idname
			bpy.context.window_manager.keyconfigs[activConfig].keymaps['Mesh'].keymap_items[i].idname = 'mesh.autodelete_ot_darcvizer'
			break
		else:
			i = i + 1



def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)


	global obj
	global mesh
	wm = bpy.context.window_manager
	keymaps_3DV = wm.keyconfigs[0].keymaps['Object Mode']
	keymap = keymaps_3DV.keymap_items['mesh.autodelete_ot_darcvizer']
	keymap.idname = obj
	keymaps = wm.keyconfigs[0].keymaps['Mesh']
	keymaps.keymap_items['mesh.autodelete_ot_darcvizer']
	keymap.idname = mesh
if __name__ == "__main__":
	register()
