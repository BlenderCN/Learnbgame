bl_info = {
        "name": "Import GameMaker: Studio 3D Model (.d3d .gml .txt)",
        "author": "JimmyBegg, Darknet",
        "version": (1, 2),
        "blender": (2, 7, 3),
        "location": "File > Import",
        "description": "Import 3D Model for GameMaker: Studio from .d3d, gml, and .txt. To create the mesh.",
        "warning": "",
        "wiki_url": "",
        "tracker_url": "",
        "category": "Learnbgame",
}

import bpy
from bpy.props import *
import mathutils, math, struct
import os
import bmesh

def addMesh(filename, objName, flippy):
	filehandle = open(filename, "r")
	way = 1

	if flippy:
			way = -1

	verts = []
	uvs = []

	has_texture = False

	with open(filename) as fin:
			lines = sum(1 for line in fin)

	print(lines)
	lines -= 4
	print(lines)

	def tsplit(s, sep):
			stack = [s]
			for char in sep:
					pieces = []
					for substr in stack:
							pieces.extend(substr.split(char))
					stack = pieces
			return stack

	for line in filehandle:
			words = tsplit(line, (",","(",")"," "))
			if words[0] == '6':
					x, y, z = float(words[1]), float(words[2]), float(words[3])
					v = (x,y*way,z)
					verts.append(v)
			if words[0] == '8':
					x, y, z = float(words[1]), float(words[2]), float(words[3])
					v = (x,y*way,z)
					verts.append(v)
					u, v = float(words[7]), float(words[8])
					u = [u,v]
					uvs.append(u)
					has_texture = True
			if words[0] == 'd3d_model_vertex_normal':
					x, y, z = float(words[3]), float(words[5]), float(words[7])
					v = (x,y*way,z)
					verts.append(v)
			if words[0] == 'd3d_model_vertex_normal_texture':
					x, y, z = float(words[3]), float(words[5]), float(words[7])
					v = (x,y*way,z)
					verts.append(v)
					u, v = float(words[15]), float(words[17])
					u = [u,v]
					uvs.append(u)
					has_texture = True

	filehandle.close()

	faces = []
	amount = int(len(verts)/3)

	for i in range(amount):
			f = (i*3,i*3+1,i*3+2)
			faces.append(f)

	# Create mesh and object
	me = bpy.data.meshes.new(objName)
	ob = bpy.data.objects.new(objName, me)
	ob.data.show_double_sided = False
	# Link object to scene
	scn = bpy.context.scene
	scn.objects.link(ob)
	scn.objects.active = ob
	scn.update()

	me.from_pydata(verts, [], faces)
	if has_texture:
			uvtex = bpy.ops.mesh.uv_texture_add()
			uvtex = me.uv_textures[-1]
			uvtex.name = 'UVLayer'
			uv_layer = me.uv_layers[-1]
			UVLayer = me.uv_textures.new('UVMap')
			uvIndex = 0
			for i in range(len(verts)):
					u = uvs[i][0]
					v = uvs[i][1]
					#print(u)
					#print(v)
					uv_layer.data[uvIndex].uv = ((float(u),float(1-v)))
					uvIndex +=1

	me.update(calc_edges=True)
	me.validate()

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.remove_doubles()
	if flippy:
			bpy.ops.mesh.flip_normals()
	bpy.ops.object.mode_set(mode='OBJECT')

def read(filepath,flippy):
	objName = bpy.path.display_name_from_filepath(filepath)
	addMesh(filepath, objName, flippy)

class Import_gm3d(bpy.types.Operator):
	'''Imports GameMaker: Studio 3D Model'''
	bl_idname = "import_object.txt"
	bl_label = "Import GameMaker: Studio 3D Model (.d3d .gml .txt )"

	filepath = StringProperty(
			subtype='FILE_PATH',
			)
			
	filter_glob = StringProperty(default="*.d3d;*.txt;*.gml", options={'HIDDEN'})

	flip_y = BoolProperty(name="Flip Y Coordinates",
													description="Flips the Y coordinates of the object",
													default=True)

	def execute(self, context):
		filepath = self.filepath
		imported = read(filepath,self.flip_y)
		
		if imported:
			print(filepath)
			message = "Import Finish! Path:" + filepath
		    
		self.report({'ERROR', 'INFO'}, "Finish Importing.")
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}

### REGISTER ###
def menu_func(self, context):
    self.layout.operator(Import_gm3d.bl_idname, text="GameMaker: Studio 3D Model Import (.d3d .gml .txt)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()