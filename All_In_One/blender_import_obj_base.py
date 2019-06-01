bl_info = {
	'name': 'Load Obj and Rigid Sequence as Base Frame',
	'author': 'Khemakhem, Feras',
	'version': (0, 1),
	'blender': (2, 6, 7),
	"category": "Learnbgame",
	'location': 'File > Import/Export',
	'wiki_url': ''}

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

import bpy, os
from bpy.props import *
import json
import time
from pprint import pprint

# class ToggleWireframe(bpy.types.Operator):
# 	bl_idname = 'load.wireframe'
# 	bl_label = 'Toggle wireframe'
# 	bl_description = 'Toggle wireframe checkboxes'
# 	wireframe_toggle = BoolProperty(name="toggle", description="", default=True)


# 	def execute (self, context):
# 		context.scene.render.layers["RenderLayer"].use_freestyle = wireframe_toggle

# 		return {'FINISHED'}

# The following function imports rigid files
class LoadRigidAsAnimation(bpy.types.Operator):
	bl_idname = 'load.rigid_as_anim'
	bl_label = 'Import Json as Animation'
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = 'Import Rigids for each frame of animation'
	filepath = StringProperty(name="File path", description="Filepath of Json", maxlen=4096, default="")
	cFrame = 0
	filter_folder = BoolProperty(name="Filter folders", description="", default=True, options={'HIDDEN'})
	filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
	files = CollectionProperty(name='File path', type=bpy.types.OperatorFileListElement)
	filename_ext = '.json'
	frames = 0
	objects = dict()
	states = dict()
	groupnames = []
	
	@classmethod
	def poll(cls, context):
		return True

	def execute (self, context):
		start = time.time()
    	# ###### this is for deleting old frames #####
		# # gather list of items of interest.
		# candidate_list = [item.name for item in bpy.data.objects if item.type == "MESH"]

		# # select them only.
		# for object_name in candidate_list:
		# 	bpy.data.objects[object_name].select = True

		# # remove all selected.
		# bpy.ops.object.delete()

		# # remove the meshes, they have no users anymore.
		# for item in bpy.data.meshes:
  		# 	bpy.data.meshes.remove(item)
		# self.objects.clear()
		# self.states.clear()
		# self.groupnames = []
		# self.frames = 0
		# ######## end of deleting frames #######

		# since there is no way to get a list of group names, we check if any group name matches this one
		for group in bpy.data.groups:
			self.groupnames.append(group.name)

		# get the first transformation file given
		spath = os.path.split(self.filepath)
		# file = [file.name for file in self.files[]]
		file = self.files[0].name
		fp = spath[0] + "/" + file
		with open(fp) as f:
			transformations = json.load(f)
		fname = os.path.splitext(file)[0]
		self.load_states(transformations, fname)

		for frame in transformations["body"]:
			self.load_frame(frame)

		bpy.context.scene.frame_set(0)

		# sets last frame to the last transformation
		if self.frames > 0:
			bpy.context.scene.frame_end = self.frames - 1
		else:
			bpy.context.scene.frame_end = 0

		end = time.time()
		self.report({'INFO'}, str(end - start))
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def load_states(self, transformations, fname):

		# determine the scaling factor from time to frame
		# if len(transformations[fname]) > 1:
		# 	scale = 1/(transformations[fname][1]["time"] - transformations[fname][0]["time"])
		# else:
		# scale = 1
		
		for state in transformations["header"]["states"]:
			# we receive the corresponding object index and name
			# then, we add that name to a dictionary, with the file path as key
			index = state["obj"]
			name = state["name"]
			group = ""
			if "group" in state:
				group = state["group"]

			# spath = os.path.split(name)
			# commented code is for relative filepath... current implementation using absolute filepath
			# file = [file.name for file in self.files[]]
			# file = self.files[0].name
			# fp = spath[0] + "/" + file

			self.states[name] = transformations["header"]["objs"][index]
			self.load_obj(self.states[name], name, group)
		
		return
	
	def load_obj(self, fp, name, group):
		# this implementation can let multiple objects be imported, but let's assume it is just one...
		bpy.ops.import_scene.obj(filepath=fp, filter_glob="*.obj;*.mtl",  use_edges=True, use_smooth_groups=True, use_split_objects=True, use_split_groups=True, use_groups_as_vgroups=False, use_image_search=True, split_mode='ON', global_clamp_size=0, axis_forward='Y', axis_up='Z')
		# take the first element of the newly created objects (ideally there's just one) and 
		bpy.context.selected_objects[0].name = name

		# check if group and add to group - https://docs.blender.org/api/blender_python_api_2_77_release/bpy.ops.object.html
		if group is not "": # if object needs to be added to a group
			if group in self.groupnames: # if already in a group
				grp = bpy.data.groups.get(group)
				grp.objects.link(bpy.context.selected_objects[0])
			else:
				self.groupnames.append(group)
				bpy.ops.group.create(name=group)



		# mark freestyle edge (only works if object is type mesh)
		for edge in bpy.context.selected_objects[0].data.edges:
			edge.use_freestyle_mark = True

		# mark as not selected
		bpy.context.selected_objects[0].select = False

		return 

	def load_frame(self, frame):
    	# make frame-1 to frame in order to fix the indexing problem
		bpy.context.scene.frame_set(frame["frame"]-1)
		for obj_to_load in frame:
			if obj_to_load == "frame": # we do not process anything with "frame"
				continue
			# obj = self.objects[obj_to_load] # gets the object from the name
			#self.report({'INFO'}, obj_to_load)
			obj = bpy.data.objects[obj_to_load]
			#self.report({'INFO'}, obj.name)
			# SRT
			obj.rotation_mode = 'QUATERNION'
			obj.scale = (frame[obj_to_load]["scale"][0],frame[obj_to_load]["scale"][1],frame[obj_to_load]["scale"][2])
			obj.rotation_quaternion = (frame[obj_to_load]["quat"][3],frame[obj_to_load]["quat"][0],frame[obj_to_load]["quat"][1],frame[obj_to_load]["quat"][2])
			obj.location = (frame[obj_to_load]["location"][0],frame[obj_to_load]["location"][1],frame[obj_to_load]["location"][2])
			obj.keyframe_insert(data_path='scale')
			obj.keyframe_insert(data_path='rotation_quaternion')
			obj.keyframe_insert(data_path='location')

		return


def menu_func_import(self, context):
	self.layout.operator(LoadObjAsBase.bl_idname, text='Obj As Base Frame')
	self.layout.operator(LoadRigidAsAnimation.bl_idname, text='Json as Animation Frame')

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
	register()
