# ##### BEGIN GPL LICENSE BLOCK #####
#
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
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	"name": "group_layer",
	"author": "bookyakuno",
	"version": (1,1),
	"location": "Outliner header",
	"description": "Outliner group like layer.",
	"warning": "",
	"category": "Learnbgame"
}


import bpy

class root_group_z(bpy.types.Operator):
	bl_idname = "object.root_group_z"
	bl_label = "root_group_z"
	bl_description = "Add object with no group to '_root'."

	def execute(self, context):



		x0 = bpy.context.scene.layers[0]
		x1 = bpy.context.scene.layers[1]
		x2 = bpy.context.scene.layers[2]
		x3 = bpy.context.scene.layers[3]
		x4 = bpy.context.scene.layers[4]
		x5 = bpy.context.scene.layers[5]
		x6 = bpy.context.scene.layers[6]
		x7 = bpy.context.scene.layers[7]
		x8 = bpy.context.scene.layers[8]
		x9 = bpy.context.scene.layers[9]
		x10 = bpy.context.scene.layers[10]
		x11 = bpy.context.scene.layers[11]
		x12 = bpy.context.scene.layers[12]
		x13 = bpy.context.scene.layers[13]
		x14 = bpy.context.scene.layers[14]
		x15 = bpy.context.scene.layers[15]
		x16 = bpy.context.scene.layers[16]
		x17 = bpy.context.scene.layers[17]
		x18 = bpy.context.scene.layers[18]
		x19 = bpy.context.scene.layers[19]
		#x20 = bpy.context.scene.layers[20]


		bpy.context.scene.layers[0] = True
		bpy.context.scene.layers[1] = True
		bpy.context.scene.layers[2] = True
		bpy.context.scene.layers[3] = True
		bpy.context.scene.layers[4] = True
		bpy.context.scene.layers[5] = True
		bpy.context.scene.layers[6] = True
		bpy.context.scene.layers[7] = True
		bpy.context.scene.layers[8] = True
		bpy.context.scene.layers[9] = True
		bpy.context.scene.layers[10] = True
		bpy.context.scene.layers[11] = True
		bpy.context.scene.layers[12] = True
		bpy.context.scene.layers[13] = True
		bpy.context.scene.layers[14] = True
		bpy.context.scene.layers[15] = True
		bpy.context.scene.layers[16] = True
		bpy.context.scene.layers[17] = True
		bpy.context.scene.layers[18] = True
		bpy.context.scene.layers[19] = True
		#bpy.context.scene.layers[20] = True


		for ob in bpy.context.scene.objects:
		   ob.select = True

		for group in bpy.data.groups:
		    for object in group.objects:
		#        print(object.name)
		#        o = bpy.data.objects
		#        o.select = True
		        ee = object
		        ee.select = False


		for o in bpy.context.selected_objects:
		    bpy.data.groups["_root"].objects.link(o)


		bpy.context.scene.layers[0] = x0
		bpy.context.scene.layers[1] = x1
		bpy.context.scene.layers[2] = x2
		bpy.context.scene.layers[3] = x3
		bpy.context.scene.layers[4] = x4
		bpy.context.scene.layers[5] = x5
		bpy.context.scene.layers[6] = x6
		bpy.context.scene.layers[7] = x7
		bpy.context.scene.layers[8] = x8
		bpy.context.scene.layers[9] = x9
		bpy.context.scene.layers[10] = x10
		bpy.context.scene.layers[11] = x11
		bpy.context.scene.layers[12] = x12
		bpy.context.scene.layers[13] = x13
		bpy.context.scene.layers[14] = x14
		bpy.context.scene.layers[15] = x15
		bpy.context.scene.layers[16] = x16
		bpy.context.scene.layers[17] = x17
		bpy.context.scene.layers[18] = x18
		bpy.context.scene.layers[19] = x19
		#bpy.context.scene.layers[20] = x20


		return {'FINISHED'}


class new_group_z(bpy.types.Operator):
	bl_idname = "object.new_group_z"
	bl_label = "new_group_z"
	bl_description = "all remove and Create new group."

	def execute(self, context):


		x0 = bpy.context.scene.layers[0]
		x1 = bpy.context.scene.layers[1]
		x2 = bpy.context.scene.layers[2]
		x3 = bpy.context.scene.layers[3]
		x4 = bpy.context.scene.layers[4]
		x5 = bpy.context.scene.layers[5]
		x6 = bpy.context.scene.layers[6]
		x7 = bpy.context.scene.layers[7]
		x8 = bpy.context.scene.layers[8]
		x9 = bpy.context.scene.layers[9]
		x10 = bpy.context.scene.layers[10]
		x11 = bpy.context.scene.layers[11]
		x12 = bpy.context.scene.layers[12]
		x13 = bpy.context.scene.layers[13]
		x14 = bpy.context.scene.layers[14]
		x15 = bpy.context.scene.layers[15]
		x16 = bpy.context.scene.layers[16]
		x17 = bpy.context.scene.layers[17]
		x18 = bpy.context.scene.layers[18]
		x19 = bpy.context.scene.layers[19]
		#x20 = bpy.context.scene.layers[20]


		bpy.context.scene.layers[0] = True
		bpy.context.scene.layers[1] = True
		bpy.context.scene.layers[2] = True
		bpy.context.scene.layers[3] = True
		bpy.context.scene.layers[4] = True
		bpy.context.scene.layers[5] = True
		bpy.context.scene.layers[6] = True
		bpy.context.scene.layers[7] = True
		bpy.context.scene.layers[8] = True
		bpy.context.scene.layers[9] = True
		bpy.context.scene.layers[10] = True
		bpy.context.scene.layers[11] = True
		bpy.context.scene.layers[12] = True
		bpy.context.scene.layers[13] = True
		bpy.context.scene.layers[14] = True
		bpy.context.scene.layers[15] = True
		bpy.context.scene.layers[16] = True
		bpy.context.scene.layers[17] = True
		bpy.context.scene.layers[18] = True
		bpy.context.scene.layers[19] = True
		#bpy.context.scene.layers[20] = True

		bpy.ops.group.objects_remove_all()
		# bpy.ops.group.objects_add_active(group='z_')
		bpy.ops.group.create(name="z_")


		bpy.context.scene.layers[0] = x0
		bpy.context.scene.layers[1] = x1
		bpy.context.scene.layers[2] = x2
		bpy.context.scene.layers[3] = x3
		bpy.context.scene.layers[4] = x4
		bpy.context.scene.layers[5] = x5
		bpy.context.scene.layers[6] = x6
		bpy.context.scene.layers[7] = x7
		bpy.context.scene.layers[8] = x8
		bpy.context.scene.layers[9] = x9
		bpy.context.scene.layers[10] = x10
		bpy.context.scene.layers[11] = x11
		bpy.context.scene.layers[12] = x12
		bpy.context.scene.layers[13] = x13
		bpy.context.scene.layers[14] = x14
		bpy.context.scene.layers[15] = x15
		bpy.context.scene.layers[16] = x16
		bpy.context.scene.layers[17] = x17
		bpy.context.scene.layers[18] = x18
		bpy.context.scene.layers[19] = x19
		#bpy.context.scene.layers[20] = x20




		return {'FINISHED'}

class all_remove_group_z(bpy.types.Operator):
	bl_idname = "object.all_remove_group_z"
	bl_label = "all_remove_group_z"
	bl_description = "all remove group.('object nothing group' data leave!! Better 'RMB > Delete Group')"

	def execute(self, context):


		x0 = bpy.context.scene.layers[0]
		x1 = bpy.context.scene.layers[1]
		x2 = bpy.context.scene.layers[2]
		x3 = bpy.context.scene.layers[3]
		x4 = bpy.context.scene.layers[4]
		x5 = bpy.context.scene.layers[5]
		x6 = bpy.context.scene.layers[6]
		x7 = bpy.context.scene.layers[7]
		x8 = bpy.context.scene.layers[8]
		x9 = bpy.context.scene.layers[9]
		x10 = bpy.context.scene.layers[10]
		x11 = bpy.context.scene.layers[11]
		x12 = bpy.context.scene.layers[12]
		x13 = bpy.context.scene.layers[13]
		x14 = bpy.context.scene.layers[14]
		x15 = bpy.context.scene.layers[15]
		x16 = bpy.context.scene.layers[16]
		x17 = bpy.context.scene.layers[17]
		x18 = bpy.context.scene.layers[18]
		x19 = bpy.context.scene.layers[19]
		#x20 = bpy.context.scene.layers[20]


		bpy.context.scene.layers[0] = True
		bpy.context.scene.layers[1] = True
		bpy.context.scene.layers[2] = True
		bpy.context.scene.layers[3] = True
		bpy.context.scene.layers[4] = True
		bpy.context.scene.layers[5] = True
		bpy.context.scene.layers[6] = True
		bpy.context.scene.layers[7] = True
		bpy.context.scene.layers[8] = True
		bpy.context.scene.layers[9] = True
		bpy.context.scene.layers[10] = True
		bpy.context.scene.layers[11] = True
		bpy.context.scene.layers[12] = True
		bpy.context.scene.layers[13] = True
		bpy.context.scene.layers[14] = True
		bpy.context.scene.layers[15] = True
		bpy.context.scene.layers[16] = True
		bpy.context.scene.layers[17] = True
		bpy.context.scene.layers[18] = True
		bpy.context.scene.layers[19] = True
		#bpy.context.scene.layers[20] = True

		bpy.ops.group.objects_remove_all()
		# bpy.ops.group.objects_add_active(group='z_')
		# bpy.ops.group.create(name="z_")


		bpy.context.scene.layers[0] = x0
		bpy.context.scene.layers[1] = x1
		bpy.context.scene.layers[2] = x2
		bpy.context.scene.layers[3] = x3
		bpy.context.scene.layers[4] = x4
		bpy.context.scene.layers[5] = x5
		bpy.context.scene.layers[6] = x6
		bpy.context.scene.layers[7] = x7
		bpy.context.scene.layers[8] = x8
		bpy.context.scene.layers[9] = x9
		bpy.context.scene.layers[10] = x10
		bpy.context.scene.layers[11] = x11
		bpy.context.scene.layers[12] = x12
		bpy.context.scene.layers[13] = x13
		bpy.context.scene.layers[14] = x14
		bpy.context.scene.layers[15] = x15
		bpy.context.scene.layers[16] = x16
		bpy.context.scene.layers[17] = x17
		bpy.context.scene.layers[18] = x18
		bpy.context.scene.layers[19] = x19
		#bpy.context.scene.layers[20] = x20




		return {'FINISHED'}


class move_group_z(bpy.types.Operator):
	bl_idname = "object.move_group_z"
	bl_label = "move_group_z"
	bl_description = "move to active group.(all remove and move to active object group)"

	def execute(self, context):
		#  アクティブオブジェクトの定義
		active = bpy.context.active_object
		#  一度、アクティブの選択を解除し、リネームする
		active.select = False

		bpy.ops.group.objects_remove_all()
		# bpy.ops.object.group_link()
		#  再度、アクティブを選択
		active.select = True
		bpy.ops.group.objects_add_active()



		return {'FINISHED'}








def group_layer_menu(self, context):

	space = context.space_data
	layout = self.layout
	# layout.menu("OUTLINER_MT_view", text="",icon="COLLAPSEMENU")
	# layout.menu("OUTLINER_MT_search", text="",icon="FILTER")


	if bpy.context.space_data.display_mode == 'GROUPS':
		row = layout.row()
		row = layout.row(align=True)

		# row.operator("group.objects_remove", text="", icon='X')
		row.operator("object.all_remove_group_z", text="", icon='CANCEL')
		# row.operator("object.group_link", text="", icon='ZOOMIN')
		row.operator("object.move_group_z", text="", icon='EXPORT')
		row.operator("object.new_group_z", text="", icon='NEW')
		row.operator("object.root_group_z", text="", icon='FILE_BACKUP')

	if space.display_mode == 'DATABLOCKS':
		layout.menu("OUTLINER_MT_edit_datablocks")







#
# class move_group_z_01(bpy.types.Operator):
# 	bl_idname = "object.move_group_z_01"
# 	bl_label = "move_group_z_01"
#
# 	def execute(self, context):
# 		bpy.ops.group.objects_remove_all()
#
# 		return {'FINISHED'}
#
# class move_group_z_02(bpy.types.Operator):
# 	bl_idname = "object.move_group_z_02"
# 	bl_label = "move_group_z_02"
#
# 	def execute(self, context):
# 		bpy.ops.object.group_link()
#
#
# 		return {'FINISHED'}
#
# class move_group_z_03(bpy.types.Operator):
# 	bl_idname = "object.move_group_z_03"
# 	bl_label = "move_group_z_03"
#
# 	def execute(self, context):
# 		bpy.ops.group.objects_add_active()
#
# 		return {'FINISHED'}
#
#
#
#
#
#
#
# class move_group_z(bpy.types.Macro):
# 	bl_idname = "object.move_group_z"
# 	bl_label = "move_group_z"
# 	bl_options = {'REGISTER','UNDO'}
#
# 	@classmethod
# 	def poll(cls, context):
# 		return context.active_object is not None
#
#






def register():
	# bpy.utils.register_class(root_group_z)
	# bpy.utils.register_class(new_group_z)
	# bpy.utils.register_class(move_group_z)

	bpy.utils.register_module(__name__)
	bpy.types.OUTLINER_HT_header.prepend(group_layer_menu)

	# # マクロ登録
	# move_group_z.define('OBJECT_OT_move_group_z_01')
	# move_group_z.define('OBJECT_OT_move_group_z_02')
	# move_group_z.define('OBJECT_OT_move_group_z_03')


def unregister():
	# bpy.utils.unregister_class(root_group_z)
	# bpy.utils.unregister_class(new_group_z)
	# bpy.utils.unregister_class(move_group_z)


	bpy.utils.unregister_module(__name__)

	bpy.types.INFO_HT_header.remove(group_layer_menu)


if __name__ == '__main__':
	register()
