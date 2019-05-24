bl_info = {
	"name": "Media Info Extractor",
	"description": "With Media Info operator sets render resolution, fps and start/end frame to match selected VSE strips",
	"author": "Patrick W. Crawford, Krzysztof Trzcinski, Tintwotin",
	"version": (1, 1),
	"blender": (2, 7, 9),
	"location": "VSE strip editor > Properties > Edit Strip (Panel): Match Strips",
	"wiki_url": "",
	"tracker_url":"",
	"category": "Learnbgame",
}

## Render Match VSE Strips(set strip properties code) by Patrick W. Crawford
## Parallel Render(external exe code) by Krzysztof Trzcinski
## Media Info handling code by Tintwotin

import bpy
import subprocess
import json
from bpy import props
from bpy import types
import os
import addon_utils

media_info_path=""
file_path=""

class SEQUENCE_OT_match_sequence_resolution(bpy.types.Operator):
	"""Change the render settings and scene length to match selected strips"""
	bl_label = "Match Strip"
	bl_idname = "sequencer.match_sequence_resolution"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
	
		# get the active strip
		selection = [seq for seq in context.scene.sequence_editor.sequences if seq.select]
		seq_active = context.scene.sequence_editor.active_strip
		if seq_active.type == None or seq_active.type in ['IMAGE',
                'MASK','CLIP','SOUND','SCENE','COLOR','CROSS',
                'ADD','SUBTRACT','ALPHA_OVER','ALPHA_UNDER',
                'GAMMA_CROSS','MULTIPLY','OVER_DROP','WIPE',
                'GLOW','TRANSFORM','COLOR','SPEED','MULTICAM',
                'ADJUSTMENT','GAUSSIAN_BLUR','TEXT']:
			self.report({'ERROR'}, "Active strip must be a video with inherent resolution")
			return {'CANCELLED'}
		
		# include active as well
		if seq_active not in selection:
			selection.append(seq_active)

		# base settings on the active strip
		global file_path
		file_path=bpy.path.abspath((str(bpy.context.scene.sequence_editor.active_strip.filepath)))#convert to absolute path
		print(file_path)
		print(media_info_path)
		#print(get_media_info(file_path)['raw_string'])
		if get_media_info(file_path)['raw_string'] == "Error in MediaInfo Execute path!":
			bpy.context.window_manager.popup_menu(oops, title="Error", icon='ERROR')
			return {'CANCELLED'}

		output_media_info_in_text_editor(file_path) # print to text editor and shell

		#get and add properties
		context.scene.render.resolution_x = int(get_media_info(file_path)['Width'].replace(' pixels','').replace(' ',''))
		context.scene.render.resolution_y = int(get_media_info(file_path)['Height'].replace(' pixels','').replace(' ',''))
		media_info_fps=float(get_media_info(file_path)['Frame rate'].replace(' FPS','').rstrip('(')[:6])

		# add pal and ntsc
		if round(media_info_fps)==media_info_fps:
			context.scene.render.fps_base = 1
			context.scene.render.fps = media_info_fps
		else:  
			context.scene.render.fps_base = 1.001
			context.scene.render.fps = round(media_info_fps)
			
		# limit range to strip:

		# initialize to smallest frame
		endframe = 0

		# initialize to a frame that definitely is after start
		startframe = seq_active.frame_final_end

		# base frame start/end  on all of selected strips
		for seq in selection:
			if endframe < seq.frame_final_end:
				endframe = seq.frame_final_end
			if startframe > seq.frame_final_start:
				startframe = seq.frame_final_start

		context.scene.frame_end = endframe-1
		context.scene.frame_start = startframe

		return {'FINISHED'}

def panel_append(self, context): # add button
	self.layout.operator(SEQUENCE_OT_match_sequence_resolution.bl_idname)

def _is_valid_mediainfo_executable(path): # check executive file path
	if not os.path.exists(path):
		return "Path `{}` does not exist".format(path)
	if not os.path.isfile(path):
		return "Path `{}` is not a file".format(path)
	if not os.access(path, os.X_OK):
		return "Path `{}` is not executable".format(path)

class MediaInfoPreferences(types.AddonPreferences):
	bl_idname = __name__

	mediainfo_executable = props.StringProperty(
		name="MediaInfo_Command_Line_Executable",
		description="Path to MediaInfo executable",
		default="MediaInfo.exe",
		update=lambda self, context: self.update(context),
		subtype='FILE_PATH'
	)

	#bpy.ops.file.make_paths_absolute() # Paths will be wrong without this
	mediainfo_status = props.StringProperty(default="")
	mediainfo_valid = props.BoolProperty(default=False)

	def update(self, context): # check media info path
		print("update")
		global media_info_path
		mi_exe_path=bpy.path.abspath(self.mediainfo_executable)#convert to absolute path
		error =""
		error = _is_valid_mediainfo_executable(mi_exe_path)

		if error is None:  # path is ok error is None and 
			info = subprocess.check_output(mi_exe_path+' --Version').decode('utf-8')
			self.mediainfo_valid = True
			self.mediainfo_status = 'Version: {}'.format(info)
			media_info_path=mi_exe_path
		else:   		  # path is not ok
			media_info_path=""
			self.mediainfo_executable.setvalue=''
			self.mediainfo_valid = False
			self.mediainfo_status = error
			context.scene.media_info_panel.update(context)

	def draw(self, context): # add info to properties
		layout = self.layout
		layout.prop(self, "mediainfo_executable")
		if self.mediainfo_valid:
			icon = 'INFO'   		  
		else: 
			icon = 'ERROR'
		layout.label(self.mediainfo_status, icon=icon)


def get_media_info(path, format='dict'): # extract data from filme with mediainfo
	""" Note this is media info cli """
	error = _is_valid_mediainfo_executable(media_info_path)
	if error is None:  
		cmd = media_info_path+' "%s"' % (path)
		process = subprocess.Popen(cmd,
								   shell=False,
								   stdin=subprocess.PIPE,
								   stdout=subprocess.PIPE,
								   stderr=subprocess.PIPE)

		o, e = process.communicate()
		if format == 'raw':
			return o

		sub = {}	#sub ['decription'] = value
		mains = {}  #Not in use: mains['catagory'] - Catagories may be: General, Video, Audio, Text, Chapter, Image, Menu, Other
		
		# make a dict of it
		for l in o.splitlines()[:-1]:
			l=str(l).strip('b'+chr(39)+' ')
			
			if ':' not in l and l != '':
				# We assume this is main keys
				cat = l.strip('\r')
				mains[cat] = ''

			elif l == '':
				mains[cat] = sub
			elif ':' in l and cat=='Video': #limit to Video for now(Audio can also have frame rates...)
				z = l.split(':', 1)
				k = z[0].strip('\r').strip()
				v = z[1].strip('\r').strip()
				sub[k] = v   
		sub['raw_string'] = o
		mains['raw_string'] = o

		#if format == 'json': Not in use, currently.
		#    return json.dumps(mains)

		return sub
	else:
		sub = {}		 
		sub['raw_string'] = "Error in MediaInfo Execute path!"
		return sub

def output_media_info_in_text_editor(path): #Uncomment this for output in new texteditor text

	filename = "MediaInfoOutput.txt" 
	if filename not in bpy.data.texts:
		bpy.data.texts.new(filename)	   # New document in Text Editor
	else:
		bpy.data.texts[filename].clear()	# Clear existing text

	mi=get_media_info(path)['raw_string']

	for l in mi.splitlines():
		l=str(l).strip('b'+chr(39)+' ')
		bpy.data.texts[filename].write(l+chr(10))   # Print to text editor
		print(l)									# Print to shell   

def oops(self, context):
	self.layout.label("MediaInfo path not valid in User Preferences!")

def register():
	bpy.utils.register_class(SEQUENCE_OT_match_sequence_resolution)
	bpy.types.SEQUENCER_PT_edit.append(panel_append)
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_class(SEQUENCE_OT_match_sequence_resolution)
	bpy.types.SEQUENCER_PT_edit.append(panel_append)
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
	
#unregister()
