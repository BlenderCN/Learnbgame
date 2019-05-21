# BlenderDeformTools/BlenderDeformTools.py at master · snowlt23/BlenderDeformTools · GitHub
# https://github.com/snowlt23/BlenderDeformTools/blob/master/BlenderDeformTools.py


import bpy
import bmesh

bl_info = {
	"name": "BlenderDeformTools bk.edit",
	"author": "shsnow23,bookyakuno",
	"version": (0, 2),
	"blender": (2, 7, 6),
	"location": "",
	"description": "",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Sculpt"
}




class MaskToVertexGroup_x(bpy.types.Operator):
    '''Mask To Vertex Group'''
    bl_idname = "mesh.masktovgroup_x"
    bl_label = "Mask To Vertex Group_x"
    bl_options = {'REGISTER'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'

    def execute(self, context):

        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :

           if context.sculpt_object.use_dynamic_topology_sculpting :

               dynatopoEnabled = True

               bpy.ops.sculpt.dynamic_topology_toggle()

           #print(context.active_object.use_dynamic_topology_sculpting)

           bmeshContainer = bmesh.new() # New bmesh container

           bmeshContainer.from_mesh(context.sculpt_object.data) # Fill container with our object

           mask = bmeshContainer.verts.layers.paint_mask.verify() # Set the active mask layer as custom layer

           newVertexGroup = context.sculpt_object.vertex_groups.new(name = "Mask") # Create an empty vgroup

           bmeshContainer.verts.ensure_lookup_table() # Just incase > Remove if unneccessary

           for x in bmeshContainer.verts:  # itterate from bmesh.verts

               if x[mask] > 0 : # if x BMVert has mask weight

                   maskWeight = x[mask] # assign float variable for weight from mask layer

                   newVertexGroup.add([x.index], maskWeight, "REPLACE") # add it to vgroup, set mask weight
               else :

                   newVertexGroup.add([x.index], 0, "REPLACE")

           bmeshContainer.free()

           if dynatopoEnabled :

               bpy.ops.sculpt.dynamic_topology_toggle()

               #print("Mask Converted to Vertex Group")
        bpy.ops.object.mode_set(mode='EDIT')


        return {'FINISHED'}




def mask_to_vertex_group():
	bpy.ops.object.mode_set(mode='SCULPT')
	bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.reveal()
	bpy.ops.object.vertex_group_assign_new()

class MaskToVGOperator(bpy.types.Operator):
	bl_idname = "wm.mask_to_vg_operator"
	bl_label = "MaskToVertexGroup"

	def execute(self, context):
		mask_to_vertex_group()
		return {'FINISHED'}

class DeformOperator(bpy.types.Operator):
	bl_idname = "wm.deform_operator"
	bl_label = "DeformOperator"

	def execute(self, context):
		mask_to_vertex_group()
		bpy.ops.object.vertex_group_select()
		saved_location = bpy.context.scene.cursor_location.copy()
		bpy.ops.view3d.snap_cursor_to_selected()
		bpy.ops.object.mode_set(mode='SCULPT')
		bpy.ops.mesh.masktovgroup_x()
		bpy.ops.object.mode_set(mode='EDIT')


		bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
		selected_verts = [i.co for i in bm.verts if i.select]

		top = None
		bottom = None
		left = None
		right = None
		front = None
		back = None
		for v in selected_verts:
			if top == None:
				top = v[2]
			elif top < v[2]:
				top = v[2]

			if bottom == None:
				bottom = v[2]
			elif bottom > v[2]:
				bottom = v[2]

			if left == None:
				left = v[1]
			elif left > v[1]:
				left = v[1]

			if right == None:
				right = v[1]
			elif right < v[1]:
				right = v[1]

			if front == None:
				front = v[0]
			elif front < v[0]:
				front = v[0]

			if back == None:
				back = v[0]
			elif back > v[0]:
				back = v[0]

		bpy.ops.mesh.select_all(action='DESELECT')

		lattice = bpy.data.lattices.new("Lattice")
		lattice_ob = bpy.data.objects.new("Lattice", lattice)

		x_scale = (front - back) / (lattice.points[5].co[0] - lattice.points[4].co[0])
		y_scale = (right - left) / (lattice.points[7].co[1] - lattice.points[5].co[1])
		z_scale = (top - bottom) / (lattice.points[5].co[2] - lattice.points[1].co[2])

		lattice_ob.scale = (x_scale, y_scale, z_scale)
		lattice_ob.location = ((front+back) / 2, (right+left) / 2, (top+bottom) / 2)

		scene = bpy.context.scene

		lattice_mod = scene.objects.active.modifiers.new("Lattice", 'LATTICE')
		lattice_mod.object = lattice_ob
		lattice_mod.vertex_group = bpy.context.object.vertex_groups.active.name

		scene.objects.link(lattice_ob)
		scene.update()

		for o in bpy.context.scene.objects:
			o.select = False
		lattice_ob.select = True
		bpy.context.scene.objects.active = lattice_ob
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.editmode_toggle()
		bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.lattice.select_all(action='SELECT')
		bpy.context.scene.cursor_location = saved_location


		return {'FINISHED'}

class DeformTools(bpy.types.Panel):
	bl_idname = "OBJECT_PT_deform_tools"
	bl_label = "DeformTools"
	bl_category = "Sculpt"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"

	def draw(self, context):
		layout = self.layout
		row_mask = layout.row()
		row_mask.operator("wm.mask_to_vg_operator", text="Mask to VertexGroup")
		row_deform = layout.row()
		row_deform.operator("wm.deform_operator", text="Create DeformBox")

def register():
	bpy.utils.register_class(MaskToVertexGroup_x)
	bpy.utils.register_class(MaskToVGOperator)
	bpy.utils.register_class(DeformOperator)
	bpy.utils.register_class(DeformTools)

def unregister():
	bpy.utils.unregister_class(MaskToVertexGroup_x)
	bpy.utils.unregister_class(MaskToVGOperator)
	bpy.utils.unregister_class(DeformOperator)
	bpy.utils.unregister_class(DeformTools)

if __name__ == "__main__":
	register()
