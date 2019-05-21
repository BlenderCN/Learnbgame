#  ***** GPL LICENSE BLOCK ***** DEV BRANCH
#
#                                                        May 21th 2015
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****

bl_info = {
	"name": "Easy Logging beta",
	"author": "Nicolas Priniotakis (Nikos), David McSween",
	"version": (0,2,1,5),
	"blender": (2, 7, 4, 0),
	"api": 44539,
	"category": "Sequencer",
	"location": "Sequencer > UI > Easy Logging",
	"description": "Logging system for the Video Sequence Editor",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",}

# -- IMPORT ------------------------------------------------------------
import bpy, random, time, os, ntpath, getpass
import pickle, time, re, platform
from string import ascii_uppercase

# -- Custom Properties & VARIABLES -------------------------------------
bpy.types.Object.tags = bpy.props.StringProperty()    
bpy.types.Object.inpoint = bpy.props.IntProperty()   
bpy.types.Object.outpoint = bpy.props.IntProperty() 
bpy.types.Scene.local_edit = bpy.props.BoolProperty(name="Local Edit",description="Edit in the opened sequencer",default = True)

bad_obj_types = ['CAMERA','LAMP','MESH']
global clip, clip_object, main_scene, log, fps, log_file, me, header_colors, current_scene
current_scene = ''
fps = 30

# -- FUNCTIONS - 2.0 ----------------------------------------------------
# clip = clip name
# clip_id = clip index in the log object
# tag is a tag name
# inpoint - for either a clip or a tag
# outpoint - for either a clip or a tag
# -----------------------------------------------------------------------

#zoom function : zoom ( x factor ) on the active strip
import bpy

def zoom(factor):
	# not useful here, but maybe later
	scene = bpy.context.scene
	original_type = bpy.context.area.type
	bpy.context.area.type = "SEQUENCE_EDITOR"
	new = bpy.context.selected_sequences

	if new:
		bpy.ops.sequencer.select_all(action = "DESELECT")
		''' variables '''
		frame = new[0].frame_final_start
		length = new[0].frame_final_end - frame
		start = (frame - length * factor) + length
		end = frame + length * factor
		chan = new[0].channel
		''' avoiding a big mess '''
		if start < scene.frame_start : start = scene.frame_start
		if end > scene.frame_end : end = scene.frame_end
		''' adding the temporary strip and delete it after the zoom '''
		bpy.ops.sequencer.effect_strip_add(frame_start=start, frame_end=end, type='COLOR', color=(1,1,1), overlap=True, channel=chan)
		bpy.ops.sequencer.view_selected()
		bpy.ops.sequencer.delete()
		''' reselect the new clips '''
		for s in new :
			s.select = True

	bpy.context.area.type = original_type


# Do I need to metastrip ?
def meta():
	meta = False
	list = []
	strips = bpy.context.scene.sequence_editor.sequences
	for s in strips:
		if s.type != 'COLOR' :
			list.append(s)
	if len(list) == 2 :
		if strips[0].name.split('.',-1)[0] == strips[1].name.split('.',-1)[0] :
			if strips[0].type == 'MOVIE' and strips[1].type == 'SOUND':
				return meta
			elif strips[1].type == 'MOVIE' and strips[0].type == 'SOUND':
				return meta
			else : return True
		else : return True
	elif len(list) == 1 : return meta
	else : return True

# the list of unique tags
def log_create_tags_list():
	global log, list_of_tags
	list_of_tags = set()
	for clip_file in log:
		if len(clip_file) > 1 :
			clip = clip_file[0]
			for tag_obj in clip_file[1:]:
				tag = tag_obj[0].split('.', 1)[0]
				list_of_tags.add(tag)
	print(list_of_tags)

# writes the list of clips associated with a tag
def log_clips_for_tag():
	global list_of_tags, log
	output = ''
	for t in list_of_tags:
		output += '\n' + u(t).upper() + '\n'
		for clip_file in log:
			if len(clip_file) > 1 :
				clip = clip_file[0]
				for tag_obj in clip_file[1:]:
					tag = tag_obj[0].split('.', 1)[0]
					inpoint = tag_obj[1]
					outpoint = tag_obj[2]
					length = outpoint - inpoint
					if tag == t:
						output += (clip[0].split('#')[0] + '\t' + tc(inpoint) + '\t' + tc(outpoint) + '\t' + tc(length) + '\n')
	return output

# list of clips
def log_list_of_clips():
	global log
	output = ''
	for clip_file in log:
		clip = clip_file[0]
		output += (clip[0].split('#')[0] + '\t' + tc(clip[1]) + '\t' + tc(clip[2]) + '')
		t = set()
		for tag_obj in clip_file[1:]:
			t.add(tag_obj[0].split('.', 1)[0])
		if len(t) > 0 :
			output += '\t#' + ', #'.join(t) + '\n'
		output += '\n'
	output +='\n'
	return output


# underlining function
def u(the_string):
	score = ''
	for x in str(the_string):
		score=score + '-'
	return the_string + '\n' + score

# Timecode conversion
def tc(fn):
	global fps
	ff = fn % fps
	s = fn // fps
	result = s // 3600, s // 60 % 60, s % 60, ff
	return ('['+ str(result[0]).zfill(2) + ':' + str(result[1]).zfill(2) + ':' + str(result[2]).zfill(2) + ':' + str(result[3]).zfill(2) + ']')

# Check if the path is already registered and add it if not
def add_path(path):
	global path_list
	path_list.add(path)
	#print (path_list)

def convert_path(original_user, me, path):
	# case windows
	path_ini = 'C:\\Users\\' + original_user + '\\'
	if path.startswith(path_ini):
		file_path = path[len(path_ini):]
		if 'Win' in my_os :
			new_path = os.path.expanduser('~') + '\\' + file_path
			return new_path
		else :
			file_path = file_path.replace('\\','/')
			new_path = os.path.expanduser('~') + '/' + file_path
			return new_path

	# Case osx
	path_ini = '/Users/' + original_user + '/'
	path_vol = '/Volumes/'
	
	if path.startswith(path_ini):
		file_path = path[len(path_ini):]
		if 'Win' in my_os :
			file_path = file_path.replace('/','\\')
			new_path = os.path.expanduser('~') + '\\' + file_path
			return new_path
		else :
			new_path = os.path.expanduser('~') + '/' + file_path
			return new_path

	elif path.startswith(path_vol):
		if 'Linux' in my_os :
			return path.replace('Volumes/','media/' + me + '/')
		elif 'Darwin' in my_os :
			return path.replace(original_user,me,1)
	
	# Case linux
	path_ini = '/home/' + original_user + '/'
	path_vol = '/media/'+ original_user + '/'
	
	if path.startswith(path_ini):
		file_path = path[len(path_ini):]
		if 'Win' in my_os :
			file_path = file_path.replace('/','\\')
			new_path = os.path.expanduser('~') + '\\' + file_path
			return new_path
		else :
			new_path = os.path.expanduser('~') + '/' + file_path
			return new_path
	
	elif path.startswith(path_vol):
		if 'Linux' in my_os :
			return path.replace(original_user,me)
		elif 'Darwin' in my_os :
			return path.replace(path_vol, '/Volumes/',1)
	else:
		return path

# Update the log file
def update_log_file(): 
	global log_file, log, path_list, user
	user = getpass.getuser()
	pickle.dump((path_list, user, log), open( log_file, "wb" ) )

# extract the filename from a path
def filename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

# Add a new clip
def add_clip(clip,inpoint,outpoint):
	size = os.stat(clip).st_size
	clip_name = filename(clip) + '#' + str(size)
	print (clip_name)
	log.append([[clip_name,inpoint,outpoint]])

# Add tag to a referenced clip
def add_tag(clip,name,inpoint,outpoint):
	tag = [name,inpoint,outpoint]
	if isinstance(clip,str):
		exists, id = clip_exists(clip)
	else:
		id = clip
	log[id].append(tag)
 
# Check if a clip is already referenced and return its id
def clip_exists(clip):
	try: size = os.stat(clip).st_size
	except: return (False, -1)
	f = filename(clip) + '#' + str(size)
	for x in log:
		if f in x[0][0]:
			return (True,log.index(x))
	return (False, -1)

# Update a clip in point
def update_inpoint(clip,inpoint):
	exists,id = clip_exists(clip)
	if exists:
		log[id][0][1] = inpoint
		
# Update a clip out point
def update_outpoint(clip,outpoint):
	exists,id = clip_exists(clip)
	if exists:
		log[id][0][2] = outpoint

# Update a clip in & out points
def update_clip(clip,inpoint,outpoint):
	update_inpoint(clip,inpoint)
	update_outpoint(clip,outpoint)

# Update a tag or create it
def update_tag(clip,tag,inpoint,outpoint):
	updated = False
	exists,id = clip_exists(clip)
	if exists:
		for x in log[id][1:]:
			if x[0] == tag :
				x[1] = inpoint
				x[2] = outpoint
				updated = True
	if not updated:
		add_tag(id,tag,inpoint,outpoint)

# Return the list of tags of a clip
def tag_list(clip):
	exists, id = clip_exists(clip)
	tags = []
	if exists:
		for y in log[id][1:]:
			tags.append([y[0],y[1],y[2]])
	return tags

# Remove a tag from a clip
def remove_tag(clip, tag):
	exists,id = clip_exists(clip)
	if exists:
		for x in log[id][1:]:
			if x[0] == tag :
				i = log[id].index(x)
				log[id].pop(i)

# Return the clip_object [name,in,out]
def get_clip(clip):
	exists,id = clip_exists(clip)
	if exists:
		return [clip,log[id][0][1],log[id][0][2]]
	else:
		add_clip(clip,-1,-1)
	return [clip,-1,-1]

# Returns TRUE if the scene already exists
def scene_exists(scene):
	for i in bpy.data.scenes:
		if i.name == scene:
			return True
	return False

# Create the 'Editing table' scene
def reset_editing_table():
	global main_scene, fps
	if scene_exists('Editing table'):
		bpy.context.screen.scene = bpy.data.scenes['Editing table']
		bpy.ops.scene.delete()                                    
	new_scene = bpy.data.scenes.new('Editing table')
	new_scene.render.fps = main_scene.render.fps
	new_scene.use_audio_sync = True
	new_scene.use_frame_drop = True
	return True
	  
# Define the main scene
def set_as_main_scene():
	global main_scene
	main_scene = bpy.context.screen.scene

# Set active scene to main
def goto_main_scene():
	global main_scene
	try:
		if main_scene != '':
			if scene_exists(main_scene.name):
				bpy.context.screen.scene = main_scene
				return True
			else:
				return False
		else:
			return False
	except: return False

# Create tag strip
def new_tag_strip(inpoint,outpoint,name):
	if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
		orginal_context = bpy.context.area.type
		bpy.context.area.type = "SEQUENCE_EDITOR"
		seq = bpy.ops.sequencer
		seq.effect_strip_add(frame_start=inpoint, frame_end=outpoint, type='COLOR', color=(random.uniform(0.5,1),random.uniform(0.5,1),1), overlap=False)
		new_strip = bpy.context.scene.sequence_editor.active_strip
		new_strip.name = name
		new_strip.blend_alpha = 0
		bpy.context.area.type = orginal_context

# Update clip and tags in the log
def update_log():
	global clip, log
	# tags
	new_tag_list = []
	try:
		for s in bpy.context.scene.sequence_editor.sequences_all:
			if s.type == 'COLOR':
				new_tag_list.append(s.name)
				tag = s.name
				inpoint = s.frame_start
				outpoint = s.frame_final_end
				update_tag(clip,tag,inpoint,outpoint)
	except: pass
	# delete removed tags
	old_tag_list = tag_list(clip)
	for x in old_tag_list:
		if not x[0] in new_tag_list:
			remove_tag(clip,x[0])

	# clip
	inpoint = bpy.data.scenes['Editing table'].frame_start
	outpoint = bpy.data.scenes['Editing table'].frame_end
	update_clip(clip,inpoint,outpoint)
	# Update the log file on disk
	update_log_file()

# Cool function written by Leon95
def header_refresh(self, context):
	global current_scene
	scene_name = bpy.context.screen.scene.name
	try:
		if current_scene == scene_name : return
		current_scene = scene_name
		pref = bpy.context.user_preferences
		header_colors = [(0.035,0.591,0.627), (0.631,0.694,0.318), (0.447,0.447,0.447)]
		if scene_name == 'Editing table': pref.themes[0].info.space.header = header_colors[0]
		elif scene_name.startswith("Tag: "): pref.themes[0].info.space.header = header_colors[1]
		else: pref.themes[0].info.space.header = header_colors[2]
	except: pass

# Returns the type of the selected element in the browser          
# Cool function written by Björn Sonnenschein 
def detect_strip_type(filepath):

	imb_ext_movie = [
	".avi",
	".flc",
	".mov",
	".movie",
	".mp4",
	".m4v",
	".m2v",
	".m2t",
	".m2ts",
	".mts",
	".mv",
	".avs",
	".wmv",
	".ogv",
	".dv",
	".mpeg",
	".mpg",
	".mpg2",
	".vob",
	".mkv",
	".flv",
	".divx",
	".xvid",
	".mxf",
	]

	imb_ext_audio = [
	".wav",
	".ogg",
	".oga",
	".mp3",
	".mp2",
	".ac3",
	".aac",
	".flac",
	".wma",
	".eac3",
	".aif",
	".aiff",
	".m4a",
	]
	
	if '#' in filepath :
		extension = filepath.split('#')[0]
		extension = '.' + extension.split('.')[1]
	else :
		extension = os.path.splitext(filepath)[1]
	extension = extension.lower()
	if extension in imb_ext_movie:
		type = 'MOVIE'
	elif extension in imb_ext_audio:
		type = 'SOUND'
	else:
		type = 'OTHER'
	return type

# import a trimed clip into a scene
def import_clip(scene,clip,inpoint,outpoint,mark):
	global path_list
	original_type = bpy.context.area.type
	bpy.context.area.type = "SEQUENCE_EDITOR"
	original_scene = bpy.context.screen.scene
	if inpoint < outpoint:
		bpy.context.screen.scene = bpy.data.scenes[scene.name]
		frame = bpy.context.scene.frame_current
		file_type = detect_strip_type(clip)
		if mark:
			for s in path_list:
				filepath = s + clip.split('#')[0]
				if os.path.isfile(filepath):
					if (file_type == "MOVIE"):
						try:
							bpy.ops.sequencer.movie_strip_add(filepath=filepath, frame_start=frame)
						except: pass
					elif (file_type == "SOUND"):
						try:
							bpy.ops.sequencer.sound_strip_add(filepath=filepath, frame_start=frame)
						except: pass
					break
		else :
			if (file_type == "MOVIE"):
				try:
					bpy.ops.sequencer.movie_strip_add(filepath=clip, frame_start=frame)
				except: pass
			if (file_type == "SOUND"):
				try:
					bpy.ops.sequencer.sound_strip_add(filepath=clip, frame_start=frame)
				except: pass

		length = outpoint - inpoint 
		try:
			for s in bpy.context.selected_sequences:
				s.frame_final_start = frame + inpoint
				s.frame_final_end = frame + outpoint
			bpy.ops.sequencer.snap(frame = bpy.context.scene.frame_current)
			if mark :
				bpy.ops.marker.add()
				bpy.ops.marker.rename(name=os.path.basename(clip).split('#')[0])
			bpy.context.scene.frame_current += length
			if mark :
				bpy.context.scene.frame_end = bpy.context.scene.frame_current
		except: pass

	bpy.context.screen.scene = original_scene
	bpy.context.area.type = original_type

# Delete the tag scenes
def delete_the_tag_scenes():
	original_scene = bpy.context.screen.scene
	for i in bpy.data.scenes:
		if i.name.startswith('Tag: ') :
			bpy.context.screen.scene = i
			bpy.ops.scene.delete()
	bpy.context.screen.scene = original_scene 

# Create the tag scenes
def create_tag_scenes():
	original_scene = bpy.context.screen.scene
	for i in bpy.data.scenes:
		if i.name.startswith('Tag: ') :
			bpy.context.screen.scene = i
			bpy.ops.scene.delete() 
	for clip_file in log:
		if len(clip_file) > 1 :
			for tag_obj in clip_file[1:]:
				tag = 'Tag: ' + tag_obj[0].split('.', 1)[0]
				inpoint = tag_obj[1]
				outpoint = tag_obj[2]
				length = outpoint-inpoint
				if not scene_exists(tag):
					new_scene = bpy.data.scenes.new(tag)
					new_scene.render.fps = original_scene.render.fps
					new_scene.use_audio_sync = True
					new_scene.use_frame_drop = True
				scene = bpy.data.scenes[tag]
				import_clip(scene, (clip_file[0][0]).split('#')[0], inpoint, outpoint, True)

	original_type = bpy.context.area.type
	bpy.context.area.type = "SEQUENCE_EDITOR"
	for i in bpy.data.scenes:
		if i.name.startswith('Tag: ') :
			bpy.context.screen.scene = i
			try:
				if len(bpy.context.scene.sequence_editor.sequences) > 0 :
					bpy.ops.sequencer.view_all()
				else:
					bpy.ops.scene.delete()
			except: pass

	bpy.context.area.type = original_type
	bpy.context.screen.scene = original_scene

# Create new log file
def create_new_log_file():
	global log_file
	log[:] = []
	filename = 'Easy-Logging-log-file'
	new_name = filename+' [' + time.strftime("%x") + '].ez'
	new_name = new_name.replace('/','-')
	directory = os.path.expanduser('~/Easy-logging files')
	filename = os.path.expanduser('~/%s.ez' % filename)
	if os.path.isfile(filename):
		if not os.path.exists(directory):
			os.makedirs(directory)
		os.rename(filename,directory + '/' + new_name)
	update_log_file()

# Trim an area regarding the IN and OUT points
def trim_area(scene, inpoint, outpoint):
	strips = bpy.context.scene.sequence_editor.sequences
	try:
		bpy.ops.sequencer.select_all(action = "SELECT")
		bpy.context.scene.frame_current = inpoint
		bpy.ops.sequencer.cut(frame=inpoint, type='SOFT', side='LEFT')
		bpy.ops.sequencer.delete()
	except:
		pass

	
	try:
		bpy.ops.sequencer.select_all(action = "SELECT")
		bpy.context.scene.frame_current = outpoint
		bpy.ops.sequencer.cut(frame=outpoint, type='SOFT', side='RIGHT')
		bpy.ops.sequencer.delete()
	except:
		pass

	bpy.context.scene.frame_current = inpoint

# Initialization ---------------------------------------------------------

inpoint = 0
outpoint = 0
tags = 'none'
me = getpass.getuser()
user = me
log = []
path_list = set()
# Load the log file
my_os = platform.system()
log_file = os.path.expanduser('~/%s.ez' % 'Easy-Logging-log-file')
if os.path.exists(log_file):
	try:
		path_list, user, log = pickle.load( open( log_file, "rb" ) )
		if not me == user:
			for i, s in enumerate(path_list):
				new_path = convert_path(user, me, s)
				path_list.remove(s)
				path_list.add(new_path)
	except EOFError: open(log_file, 'a').close()
else:
	print('Create the metadata file')
	open(log_file, 'a').close()
	

# --- CLASSES ---------------------------------------------------------------------

# Creating the PANEL    
class iop_panel(bpy.types.Header):     
	bl_space_type = "SEQUENCE_EDITOR"       
	bl_region_type = "UI"          
	bl_label = "Trim"
	global main_scene
	
	@classmethod
	def poll(self, context):
		return True
	
	def draw(self, context):
		layout = self.layout
		layout.separator()
		if bpy.context.screen.scene.name == 'Editing table':
			row=layout.row()
			row.operator("sequencer.trim", icon="ARROW_LEFTRIGHT")
			layout.separator()
			row.operator("sequencer.setin", icon="TRIA_RIGHT")
			row.operator("sequencer.setout", icon='TRIA_LEFT')
			row.operator("sequencer.setinout", icon='FULLSCREEN_EXIT')
			row.operator("sequencer.addtag", icon='PLUS')
			row.operator("sequencer.place", icon="PASTEFLIPDOWN")
			row.operator("sequencer.back", icon="LOOP_BACK")
		elif bpy.context.screen.scene.name.startswith('Tag: ') and main_scene:
			row=layout.row()
			row.operator("sequencer.place", icon="PASTEFLIPDOWN")
			row.operator("sequencer.back", icon="LOOP_BACK")
		else:
			row=layout.row()
			row.operator("sequencer.import", icon="ZOOMIN")
			row.operator("sequencer.trim", icon="ARROW_LEFTRIGHT")
			row.prop(context.scene,"local_edit")

# Creating the Place button operator - 2.0
class OBJECT_OT_Place(bpy.types.Operator):  
	bl_label = "Place"
	bl_idname = "sequencer.place"
	bl_description = "Place the clip in the timeline"
		
	def invoke(self, context, event):
		global main_scene
		if main_scene:
			scene = bpy.context.screen.scene
			inpoint = scene.frame_start
			outpoint = scene.frame_end

			if inpoint == outpoint:
				outpoint = inpoint + 50
				scene.frame_start = inpoint
				scene.frame_end = outpoint
			# Editing table context
			if scene.name == 'Editing table':
				update_log()
				trim_area(scene, inpoint, outpoint)
				# if metastrip is needed
				if meta() :
					# make metastrip
					bpy.ops.sequencer.select_all(action = "SELECT")
					bpy.ops.sequencer.meta_make()
					bpy.ops.sequencer.select_all(action = "SELECT")
				else:
					# select everything except tag strips
					bpy.ops.sequencer.select_all(action = "DESELECT")
					for s in context.scene.sequence_editor.sequences_all:
						if s.type != 'COLOR':
							s.select = True
				bpy.ops.sequencer.copy()
				goto_main_scene()
				try : bpy.ops.sequencer.select_all(action = "DESELECT")
				except : pass #nothing to deselect
				bpy.ops.sequencer.paste()
				zoom(3)
				bpy.context.scene.frame_current = bpy.context.scene.frame_current + (outpoint-inpoint)
				
				# clean up
				reset_editing_table()
				if main_scene.local_edit == False:
					bpy.context.screen.scene = bpy.data.scenes['Editing table']
				else:
					#bpy.ops.sequencer.view_selected()
					goto_main_scene()
				return {'FINISHED'}
			# Tag-scene context
			else :
				print("Tag-scene context")
				tag_strip = bpy.context.scene.sequence_editor.active_strip
				inpoint = tag_strip.frame_final_start
				outpoint = tag_strip.frame_final_end - 1
				print(inpoint)
				print(outpoint)
				print('---')
				bpy.ops.scene.new(type='FULL_COPY')
				temp_scene = bpy.context.screen.scene
				trim_area(temp_scene, inpoint, outpoint)
				bpy.ops.sequencer.select_all(action = "SELECT")
				bpy.ops.sequencer.copy()
				bpy.ops.scene.delete()
				goto_main_scene()
				bpy.ops.sequencer.paste()
				bpy.context.scene.frame_current = bpy.context.scene.frame_current + (outpoint-inpoint)
				bpy.ops.sequencer.view_selected()
				return {'FINISHED'}

# Creating the IMPORT button operator - 2.0
class OBJECT_OT_import(bpy.types.Operator): 
	bl_label = "Import clip"
	bl_idname = "sequencer.import"
	bl_description = "Import the selected clip in the browser"
	global main_scene  
	def invoke(self, context, event):

		for a in bpy.context.window.screen.areas:
			if a.type == 'FILE_BROWSER':
				params = a.spaces[0].params
				the_path = params.directory
				the_file = params.filename
				clip = the_path + the_file
				add_path(the_path)
				break

		try:
			if the_file == '':
				return {'FINISHED'}
		except : return {'FINISHED'}

		exists,id = clip_exists(clip)
		if exists:
			clip_object = get_clip(clip)
			inpoint = clip_object[1]
			outpoint = clip_object[2]

			if bpy.context.screen.scene.name != 'Editing table':
				set_as_main_scene()
			
			import_clip(main_scene,clip,inpoint,outpoint, False)
		else:
			try:
				bpy.ops.sequencer.movie_strip_add(filepath=clip, frame_start=bpy.context.scene.frame_current)
			except: pass

		return {'FINISHED'}

# Creating the TRIM (EDIT) button operator - 2.0
class OBJECT_OT_Trim(bpy.types.Operator): 
	bl_label = "Edit clip"
	bl_idname = "sequencer.trim"
	bl_description = "Trim the selected clip in the browser"
	
	def invoke(self, context, event):
		global main_scene, clip, clip_object
		
		 # set current scene as main scene
		if bpy.context.screen.scene.name != 'Editing table':
			set_as_main_scene()
		else:
			update_log()

		#get directory & name (path - clip)
		for a in bpy.context.window.screen.areas:
			if a.type == 'FILE_BROWSER':
				params = a.spaces[0].params
				the_path = params.directory
				the_file = params.filename
				clip = the_path + the_file
				add_path(the_path)
				break

		try:
			if the_file == '':
				return {'FINISHED'}
		except : return {'FINISHED'}

		file_type = detect_strip_type(clip)
		if (file_type not in "MOVIE SOUND") :
			return {'FINISHED'}

		#create the log scene if it doesn't already exist
		reset_editing_table()
		
		# Go to log scene, import the file and set start/end if exists
		bpy.context.screen.scene = bpy.data.scenes['Editing table']

		#check the type of the file and add its strips accordingly
		if (file_type == "MOVIE") or (file_type == "SOUND"):
			original_type = bpy.context.area.type
			bpy.context.area.type = "SEQUENCE_EDITOR"
			if (file_type == "MOVIE"):
				bpy.ops.sequencer.movie_strip_add(frame_start=1, filepath=clip)
			else:
				bpy.ops.sequencer.sound_strip_add(frame_start=1, filepath=clip)
			bpy.context.area.type = original_type

			# create clip entry in the log if not already registered
			# pick up the in and out point and the tags
			# initialize the object variables
			tags = []
			exists, id = clip_exists(clip)
			if exists:
				clip_object = get_clip(clip)
				tags = tag_list(clip)
				start = clip_object[1]
				end = clip_object[2]
			else:
				start = 1
				end = bpy.context.scene.sequence_editor.active_strip.frame_final_duration
				add_clip(clip, start,end)
			bpy.data.scenes['Editing table'].frame_start = start if start > 0 else 1
			bpy.data.scenes['Editing table'].frame_end = end if end > 1 else bpy.context.scene.sequence_editor.active_strip.frame_final_duration
			# add existing tags linked to the clip
			if len(tags) > 0:
				for x in tags:
					new_tag_strip(x[1],x[2],x[0])

		bpy.ops.sequencer.select_all(action = "SELECT")
		bpy.ops.sequencer.view_selected()
		return {'FINISHED'}
  
# creating the ADD TAG button operator - 2.0
class OBJECT_OT_addTag(bpy.types.Operator): 
	bl_label = "Add Tag"
	bl_idname = "sequencer.addtag"
	bl_description = "Add a new tag to the clip"
		
	def invoke(self, context, event):
		bpy.ops.sequencer.select_all(action = "DESELECT")
		inpoint = bpy.data.scenes['Editing table'].frame_current
		outpoint = inpoint + 50
		new_tag_strip(inpoint,outpoint,'new-tag')
		return {'FINISHED'}

# creating the SET IN&OUT button operator - 2.0
class OBJECT_OT_setInOut(bpy.types.Operator): 
	bl_label = "Set In & Out"
	bl_idname = "sequencer.setinout"
	bl_description = "Use selected tag strip to set the In and Out points of the editing table"
		
	def invoke(self, context, event):
		tag_strip = bpy.context.scene.sequence_editor.active_strip
		inpoint = tag_strip.frame_final_start
		outpoint = tag_strip.frame_final_end
		bpy.context.screen.scene.frame_start = inpoint
		bpy.context.screen.scene.frame_end = outpoint
		if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
			update_clip(clip, inpoint, outpoint)
		return {'FINISHED'}

# creating the IN button operator - 2.0
class OBJECT_OT_Setin(bpy.types.Operator): 
	bl_label = "IN"
	bl_idname = "sequencer.setin"
	bl_description = "Set the IN point of the clip"
	
	def invoke(self, context, event):
		global clip
		if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
			inpoint = bpy.context.scene.frame_current
			bpy.data.scenes['Editing table'].frame_start = inpoint
			update_inpoint(clip,inpoint)
		return {'FINISHED'}
		
# creating the OUT button operator - 2.0  
class OBJECT_OT_Setout(bpy.types.Operator):  
	bl_label = "OUT"
	bl_idname = "sequencer.setout"
	bl_description = "Set the OUT point of the clip"
		
	def invoke(self, context, event):
		global clip
		clip_object = get_clip(clip)
		if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
			outpoint = bpy.context.scene.frame_current
			bpy.data.scenes['Editing table'].frame_end = outpoint + 1
			update_outpoint(clip,outpoint)           
			if clip_object[1] < 1:
				inpoint = 1
				update_inpoint(clip,inpoint)
		return {'FINISHED'}

# creating the back button operator - 2.0 
class OBJECT_OT_Back(bpy.types.Operator):  
	bl_label = "Back to Sequence"
	bl_idname = "sequencer.back"
	bl_description = "Go back to the main sequence"
	def invoke(self, context, event):
		global main_scene
		if bpy.context.screen.scene.name == 'Editing table':
			update_log()
		goto_main_scene()
		return {'FINISHED'}

# creating the menu "create log file" operator   
class SEQUENCER_OT_createlog(bpy.types.Operator):
	bl_idname = "sequencer.createlog"
	bl_label = "Create the log file"
	def execute(self, context):
		#create_the_log_file()
		return {'FINISHED'}

# creating the tag scene menu operator        
class SEQUENCER_OT_create_tag_scenes(bpy.types.Operator):
	bl_idname = "sequencer.createtagtcenes"
	bl_label = "Create the tag scenes"
	@classmethod
	def poll(cls, context):
		return ('Tag:' not in bpy.context.screen.scene.name)
	def execute(self, context):
		create_tag_scenes()
		return {'FINISHED'}

# creating the create new log file operator
class SEQUENCER_OT_create_new_log_file(bpy.types.Operator):
	bl_idname = "sequencer.createnewlogfile"
	bl_label = "Create a new log file"
	def execute(self, context):
		create_new_log_file()
		return {'FINISHED'}

# creating the delete tag-scenes operator
class SEQUENCER_OT_delete_tag_scenes(bpy.types.Operator):
	bl_idname = "sequencer.deletetagscenes"
	bl_label = "Delete the tag-scenes"
	@classmethod
	def poll(cls, context):
		return ('Tag:' not in bpy.context.screen.scene.name)
	def execute(self, context):
		delete_the_tag_scenes()
		return {'FINISHED'}

# creating the log text operator
class SEQUENCER_OT_create_log_text(bpy.types.Operator):
	bl_idname = "sequencer.createlogtext"
	bl_label = "Create the log document"
	def execute(self, context):
		#Create the file
		the_time = (time.strftime("%d/%m/%Y")) + ' - ' + (time.strftime("%H:%M:%S"))
		log_text = bpy.data.texts.new('Log document')
		log_text.write(u('EASY LOGGING - LOG FILE  Author: ' + user + ' -- ' + the_time) + '\n')
		log_text.write('\n' + u('CLIPS BY TAGS') + '\n')
		log_create_tags_list()
		log_text.write(log_clips_for_tag())
		log_text.write('\n' + u('CLIPS : IN OUT & TAGS') + '\n')
		log_text.write(log_list_of_clips())
		return {'FINISHED'}

# -- MENU EASY LOGGING ----------------------------------------------------

class EasyLog(bpy.types.Menu):
	bl_label = "Easy Logging"
	bl_idname = "OBJECT_MT_easy_log"

	def draw(self, context):
		layout = self.layout

def draw_item(self, context):
	layout = self.layout
	layout.menu(EasyLog.bl_idname)
                 
def createTagScene_func(self, context):
	self.layout.operator(SEQUENCER_OT_create_tag_scenes.bl_idname, text="Build the tag scenes", icon='OOPS')

def deleteTagScene_func(self, context):
	self.layout.operator(SEQUENCER_OT_delete_tag_scenes.bl_idname, text="Delete the tag scenes", icon='CANCEL')

def createLogText_func(self, context):
	self.layout.operator(SEQUENCER_OT_create_log_text.bl_idname, text="Create the log document", icon='LINENUMBERS_ON')

def createNewLogfile_func(self, context):
	self.layout.operator(SEQUENCER_OT_create_new_log_file.bl_idname, text="Create a new log file", icon='FILE_SCRIPT')    


# ----------------- Registration -------------------     
def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.headerColor = bpy.props.FloatVectorProperty(
									 name = "Display Color",
									 subtype = "COLOR",
									 size = 4,
									 min = 0.0,
									 max = 1.0,
									 default = (0.355,0.366,0.57,1.0))
	bpy.types.INFO_HT_header.append(header_refresh)
	bpy.types.INFO_HT_header.append(draw_item)
	bpy.types.OBJECT_MT_easy_log.append(createTagScene_func)
	bpy.types.OBJECT_MT_easy_log.append(deleteTagScene_func)
	bpy.types.OBJECT_MT_easy_log.append(createLogText_func)
	bpy.types.OBJECT_MT_easy_log.append(createNewLogfile_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_HT_header.remove(header_refresh)
	bpy.types.INFO_HT_header.remove(draw_item)
	bpy.context.user_preferences.themes[0].info.space.header = (0.447,0.447,0.447)
	del bpy.types.Scene.headerColor

if __name__ == "__main__":
    register()


def updateStringParameter(self,context):
	print(self.my_string)
def updateIntParameter(self,context):
	print(self.my_int)
