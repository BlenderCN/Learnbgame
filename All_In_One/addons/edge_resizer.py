# ###################### BEGIN GPL LICENSE BLOCK ###########################
#   																	   #
#  This program is free software; you can redistribute it and/or		   #
#  modify it under the terms of the GNU General Public License  		   #
#  as published by the Free Software Foundation; either version 2   	   #
#  of the License, or (at your option) any later version.   			   #
#   																	   #
#  This program is distributed in the hope that it will be useful,  	   #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of   	   #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the		   #
#  GNU General Public License for more details. 						   #
#   																	   #	
#  You should have received a copy of the GNU General Public License	   #
#  along with this program; if not, write to the Free Software Foundation, #
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.      #
#   																	   # 
# ###################### END GPL LICENSE BLOCK #############################


bl_info = {
	"name": "Edge Resize",
	"category": "Learnbgame",
	"author": "Regz",
	"version": (1,1,0),
	"blender": (2, 80, 0),
	"location": "Editmode > Edge > Edge Resize",
	"description": "Tools to resize edges with precision",
}
 
import bpy
import bmesh
import math

from bpy.types import Operator
from bpy.props import FloatProperty
from bpy.props import BoolProperty


perfectl = 2
lastdrive = False


def averageedgessize():
	# Get the active mesh
	obj = bpy.context.edit_object
	me = obj.data


	# Get a BMesh representation
	bm = bmesh.from_edit_mesh(me)
	l=0
	#number of edges (to make an average value of all the lenght)
	it = 0
	for e in bm.edges:
		if e.select:
			
			v1 = e.verts[0]
			v2 = e.verts[1]
			
			it+=1
			
			l += math.sqrt(
			(v1.co.x - v2.co.x)*(v1.co.x - v2.co.x)+
			(v1.co.y - v2.co.y)*(v1.co.y - v2.co.y)+
			(v1.co.z - v2.co.z)*(v1.co.z - v2.co.z))
	return l/it
	
def edgesize():
	# Get the active mesh
	obj = bpy.context.edit_object
	me = obj.data


	# Get a BMesh representation
	bm = bmesh.from_edit_mesh(me)
	l=0
	#number of edges (to make an average value of all the lenght)
	e = bm.select_history.active
			
	v1 = e.verts[0]
	v2 = e.verts[1]
	
	
	l += math.sqrt(
	(v1.co.x - v2.co.x)*(v1.co.x - v2.co.x)+
	(v1.co.y - v2.co.y)*(v1.co.y - v2.co.y)+
	(v1.co.z - v2.co.z)*(v1.co.z - v2.co.z))
	
	return l


def update_show_edges(self, context):
	if self.show_edges == True:
		bpy.context.space_data.overlay.show_extra_edge_length = True			
	else:
		bpy.context.space_data.overlay.show_extra_edge_length = False

	
class MESH_OT_EdgeResize(bpy.types.Operator):
	'''Edge Resize'''
	bl_idname = "mesh.edge_resize"
	bl_label = "Edge Resize"  
	bl_options = {'REGISTER', 'UNDO'}  
	
	edge_length: FloatProperty(  
		name="Length",  
		default=perfectl, 
		subtype='DISTANCE',  
		unit='LENGTH',  
		description="Length"  
		)  
   
	drive: bpy.props.BoolProperty(
		name="Drive",
		description="Checked only the active edge expends, the selected will follow"
		)

	show_edges: bpy.props.BoolProperty(
		name="Show Edges",
		description="Show the edge length in the viewport",
		default=False,
		update=update_show_edges		
		)   	 
						
	position: FloatProperty(  
		name="Position",  
		default=1.0,
		min=0.0,
		max=1.0,  
		subtype='DISTANCE',  
		unit='LENGTH',  
		description="Position"
		)
	
	
	def invoke(self, context, event):
		global lastdrive
		if self.drive:
			self.edge_length = edgesize()
		else:
			self.edge_length = averageedgessize()
		lastdrive = self.drive
		return {'FINISHED'}

	def execute(self, context): 
		
		global lastdrive
		if lastdrive != self.drive:
			lastdrive = self.drive
			
			if self.drive:
				self.edge_length = edgesize()
			else:
				self.edge_length = averageedgessize()
		
		#length that we want for the edge
		wanted_length = self.edge_length
		p = self.position
		mode = self.drive
		
		
		# Get the active mesh
		obj = bpy.context.edit_object
		me = obj.data


		# Get a BMesh representation
		bm = bmesh.from_edit_mesh(me)



		#e = bmesh.types.BMEditSelSeq.active
		#print(type(e))
		
		
		
		#if we want to modify only the active edge and the selected edge "follow"
		if mode:
			e = bm.select_history.active
			
			v1 = e.verts[0]
			v2 = e.verts[1]
			
			
			#which vertex should be v1, it must be the vertex linked to another selected edge, we count the link of each vertex, the one with the much linked vertices (should be 1 vs 2 if we are in front of a nice user ;) 
			
			switch = 0
			
			for el in bm.edges:
				if el.select:
					vl1 = el.verts[0]
					vl2 = el.verts[1]
					
					if vl1 == v1 or vl2 == v1:
						switch+=1
						
					if vl1 == v2 or vl2 == v2:
						switch-=1
						
			print(switch)
			
			if switch<0:
				v1,v2 = v2,v1
			
			l = math.sqrt(
			(v1.co.x - v2.co.x)*(v1.co.x - v2.co.x)+
			(v1.co.y - v2.co.y)*(v1.co.y - v2.co.y)+
			(v1.co.z - v2.co.z)*(v1.co.z - v2.co.z))
			print(l)
			ratio1 = wanted_length/l
			ratio2 = wanted_length/l
			#we've calculate the ratio needed to multiply the edge at the good size
			#we remove one, now we know the length to add to have the good size
			ratio1-=1
			ratio2-=1   		 
			
			print(ratio1)
			print(ratio2)
			print("-----")
			x1 = (v1.co.x - v2.co.x)*ratio1
			y1 = (v1.co.y - v2.co.y)*ratio1
			z1 = (v1.co.z - v2.co.z)*ratio1
			
			
			v1.co.x += x1
			v1.co.y += y1
			v1.co.z += z1
			
			#the vertices that we shoudn't touch
			done = [v1,v2]
			
			for el in bm.edges:
				if el.select:
					vl1 = el.verts[0]
					vl2 = el.verts[1]
					
					if vl1 not in done:
						done.append(vl1)
						vl1.co.x += x1
						vl1.co.y += y1
						vl1.co.z += z1
					
					if vl2 not in done:
						done.append(vl2)
						vl2.co.x += x1
						vl2.co.y += y1
						vl2.co.z += z1
		#if we want to resize all the edge with the same length
		else:
			for e in bm.edges:
				if e.select:
					v1 = e.verts[0]
					v2 = e.verts[1]
					

					l = math.sqrt(
					(v1.co.x - v2.co.x)*(v1.co.x - v2.co.x)+
					(v1.co.y - v2.co.y)*(v1.co.y - v2.co.y)+
					(v1.co.z - v2.co.z)*(v1.co.z - v2.co.z))
					print(l)
					ratio1 = wanted_length/l
					ratio2 = wanted_length/l
					#we've calculate the ratio needed to multiply the edge at the good size
					#we remove one, now we know the length to add to have the good size
					ratio1-=1
					ratio2-=1
					
					#now we multiply by -p and 1-p to get the length to add at each extremity 
					ratio1*=(1-p)
					ratio2*=-p
					
					print(ratio1)
					print(ratio2)
					print("-----")
					x1 = (v1.co.x - v2.co.x)*ratio1
					y1 = (v1.co.y - v2.co.y)*ratio1
					z1 = (v1.co.z - v2.co.z)*ratio1
					
					x2 = (v1.co.x - v2.co.x)*ratio2
					y2 = (v1.co.y - v2.co.y)*ratio2
					z2 = (v1.co.z - v2.co.z)*ratio2
					
					v1.co.x += x1
					v1.co.y += y1
					v1.co.z += z1
					
					v2.co.x += x2
					v2.co.y += y2
					v2.co.z += z2
					
					

		# Show the updates in the viewport
		# and recalculate n-gon tessellation.
		bmesh.update_edit_mesh(me, True)
			
		
		return {'FINISHED'} 


def MESH_MT_DrawEdgeResizeMenu(self, context):
	self.layout.operator("mesh.edge_resize", text="Edge Resize")

   
@classmethod  
def poll(cls, context):  
	ob = context.active_object  
	return ob is not None and ob.mode == 'EDIT_MESH'  


classes = (
	MESH_OT_EdgeResize, 				 
)


def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls) 

	bpy.types.VIEW3D_MT_edit_mesh_edges.append(MESH_MT_DrawEdgeResizeMenu)
	
def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		unregister_class(cls)

	bpy.types.VIEW3D_MT_edit_mesh_edges.remove(MESH_MT_DrawEdgeResizeMenu)

if __name__ == "__main__":  
	register() 