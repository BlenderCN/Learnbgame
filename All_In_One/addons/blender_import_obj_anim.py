bl_info = {
	'name': 'Load Obj Sequence as animation',
	'author': 'cmomoney',
	'version': (0, 2),
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


class LoadObjAsAnimation(bpy.types.Operator):
	bl_idname = 'load.obj_as_anim'
	bl_label = 'Import OBJ as Animation'
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Import Obj sequence as animation(s)"
	cFrame = 0
	filepath = StringProperty(name="File path", description="Filepath of Obj", maxlen=4096, default="")
	filter_folder = BoolProperty(name="Filter folders", description="", default=True, options={'HIDDEN'})
	filter_glob = StringProperty(default="*.obj", options={'HIDDEN'})
	files = CollectionProperty(name='File path', type=bpy.types.OperatorFileListElement)
	filename_ext = '.obj'
	objects = []
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		self.objects=[]
		#get file names, sort, and set target mesh
		spath = os.path.split(self.filepath)
		files = [file.name for file in self.files]
		files.sort()
		#add all objs to scene
		for f in files:
			fp = spath[0] + "/" + f
			self.load_obj(fp,f)
		
		bpy.context.scene.frame_set(0)
		for i, ob in enumerate(self.objects):
			if i == 0:
				continue
			ob.hide = ob.hide_render = True
			ob.keyframe_insert(data_path='hide')
			ob.keyframe_insert(data_path='hide_render')

		for f, ob in enumerate(self.objects):
			if f == 0:
				continue
			# increment current frame to insert keyframe
			bpy.context.scene.frame_set(f)

			# Insert only as many keyframes as really needed
			ob_prev = self.objects[f-1]
			ob_prev.hide = ob_prev.hide_render = True
			ob_prev.keyframe_insert(data_path='hide')
			ob_prev.keyframe_insert(data_path='hide_render')
			
			ob = self.objects[f]
			ob.hide = ob.hide_render = False
			ob.keyframe_insert(data_path='hide')
			ob.keyframe_insert(data_path='hide_render')

		# this sets last frame to the last object -- G.Lopez
		numOfFrames = len(self.objects)
		bpy.context.scene.frame_end = numOfFrames - 1
				
		return{'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def load_obj(self, fp,fname):
		bpy.ops.object.select_all(action='DESELECT')
		bpy.ops.import_scene.obj(filepath=fp, filter_glob="*.obj;*.mtl",  use_edges=True, use_smooth_groups=True, use_split_objects=True, use_split_groups=True, use_groups_as_vgroups=False, use_image_search=True, split_mode='ON', global_clamp_size=0, axis_forward='Y', axis_up='Z')
		self.objects.append(bpy.context.selected_objects[0])
		return 
def menu_func_import(self, context):
	self.layout.operator(LoadObjAsAnimation.bl_idname, text="Obj As Animation")

def register():
	bpy.utils.register_class(LoadObjAsAnimation)
	bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
	bpy.utils.unregister_class(LoadObjAsAnimation)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
	register()
