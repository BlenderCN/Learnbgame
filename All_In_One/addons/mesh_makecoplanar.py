bl_info = {
	"name":"Make Coplanar",
	"author": "Scott Michaud",
	"version": (0,5),
	"blender": (2,72,0),
	"location": "View3D > Specials > Make Coplanar",
	"Description": "Forces currently selected vertices into their average plane, and a second selection of vertices into that plane.",
	"warning": "",
	"category": "Mesh"
}

import bpy
import bmesh
import mathutils
import time

class MakeCoplanar(bpy.types.Operator):
	bl_idname = 'mesh.makecoplanar'
	bl_label = 'Make Coplanar'
	bl_options = {'REGISTER', 'UNDO'}
	
	def get_timestamp():
		out_time = time.time()
		return out_time * 1000
	
	#Returns 1 if moves need to happen in first stage. 0 if nor. -1 if error.
	def get_plane(self, context):
		self.bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
		bm = self.bm
		vtxs = bm.verts
		selected_vtxs = [i for i in vtxs if i.select]
		num = len(selected_vtxs)
		list_normals = []
		list_distances = []
		avg_normal = mathutils.Vector((0.0,0.0,0.0))
		avg_distance = 0.0
		
		#If less then three vertices selected, cannot get a plane.
		if num < 3:
			return -1
		
		#Get a sample of normals. Each vertex will contribute to three.
		#All pairings would be better, but this is O(n) and probably good enough.
		for i in range(num):
			first_next = (i + 1) % num #Allow wrapping around for last two entries.
			second_next = (1 + 2) % num
			vector_1 = selected_vtxs[i].co - selected_vtxs[first_next].co
			vector_2 = selected_vtxs[i].co - selected_vtxs[second_next].co
			cross_12 = vector_1.cross(vector_2)
			list_normals.append(cross_12)
		
		#Make all normals acute (or right-angle) to one another.
		#This makes best use of floating point precision.
		for i in range(1, num):
			test_scalar = list_normals[i].dot(list_normals[0])
			if test_scalar < 0:
				list_normals[i] = -1 * list_normals[i]
		
		#Find the average normal by summing all samples and normalizing.
		for i in range(num):
			avg_normal += list_normals[i]
		avg_normal.normalize()
		self.normal = avg_normal
		
		#Get distance for each vertex to a plane that crosses origin.
		#The average distance will define our plane, that distance away from origin down average normal direction.
		for i in range(num):
			distance = selected_vtxs[i].co.dot(avg_normal)
			list_distances.append(distance)
			avg_distance += distance
		avg_distance /= num
		self.distance = avg_distance
		
		if num == 3:
			return 0
		else:
			return 1
		
	def conform_plane(self, context):
		bm = self.bm
		vtxs = bm.verts
		selected_vtxs = [i for i in vtxs if i.select]
		num = len(selected_vtxs)
		avg_normal = self.normal
		avg_distance = self.distance
		
		#Move vertexes to the nearest point on plane calculated in get_plane()
		for i in range(num):
			distance = selected_vtxs[i].co.dot(avg_normal)
			delta = distance - avg_distance
			adjust = avg_normal * delta
			selected_vtxs[i].co -= adjust
			selected_vtxs[i].select = False
		bpy.context.active_object.data.update()
	
	def execute(self, context):
		return {'FINISHED'}
	
	def modal(self, context, event):
		if event.type == 'ESC':
			return {'CANCELLED'}
		elif event.type == 'RET' and event.value == 'PRESS':
			delta_time = (MakeCoplanar.get_timestamp()) - (self.start_time)
			if delta_time > 250.0:
				self.conform_plane(context)
				return {'FINISHED'}
		else:
			self.execute(context)
			return {'PASS_THROUGH'}
		
	def invoke(self, context, event):
		returncode = self.get_plane(context)
		self.start_time = MakeCoplanar.get_timestamp()
		if returncode == -1:
			return {'CANCELLED'}
		if returncode == 0:
			context.window_manager.modal_handler_add(self)
			self.execute(context)
			return {'RUNNING_MODAL'}
		if returncode == 1:
			context.window_manager.modal_handler_add(self)
			self.conform_plane(context)
			self.execute(context)
			return {'RUNNING_MODAL'}

def menu_func(self, context):
	self.layout.operator_context = 'INVOKE_DEFAULT'
	self.layout.operator(MakeCoplanar.bl_idname, text="Make Coplanar")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_vertices.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_func)

if __name__ == "__main__":
	register()