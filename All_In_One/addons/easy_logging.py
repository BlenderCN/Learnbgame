#  ***** GPL LICENSE BLOCK *****
#
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
    "name": "Easy Logging",
    "author": "Nicolas Priniotakis",
    "version": (0,0,1),
    "blender": (2, 7, 0, 0),
    "api": 44539,
    "category": "Sequencer",
    "location": "Sequencer > UI > Easy Logging",
    "description": "Logging system for the Video Sequence Editor",
    "warning": "",
    "wiki_url": "http://vimeo.com/103362081",
    "tracker_url": "",}

# -- IMPORT ------------------------------------------------------------
import bpy, random, time, os
#import tag_scenes,log_file,in_out_tag


# -- Custom Properties & VARIABLES -------------------------------------
bpy.types.Object.tags = bpy.props.StringProperty()
bpy.types.Object.inpoint = bpy.props.IntProperty()
bpy.types.Object.outpoint = bpy.props.IntProperty()
bpy.types.Scene.local_edit = bpy.props.BoolProperty(name="Local Edit",description="Edit in the opened sequencer",default = True)
bpy.types.Scene.meta = bpy.props.BoolProperty(name="As Meta",description="Send trimed clip(s) as a meta strip to the sequencer",default = False)

bad_obj_types = ['CAMERA','LAMP','MESH']
global path, clip, clip_obj, inpoint, outpoint, start, end, main_scene

# Initialization -----
#main_scene = bpy.data.scenes['Scene']
inpoint = 0
outpoint = 0
tags = 'none'


# -- FUNCTIONS -----------------------------------------------------------

#delete objects
def remove_obj (obj):
     mesh = bpy.data.object[obj]
     mesh.user_clear()
     bpy.data.objects.remove(mesh)
     return

# Returns TRUE if the scene 'Editing table' already exists
def log_exists():
    z = False
    for i in bpy.data.scenes:
        if i.name == 'Editing table':
            z = True
            break
    return z

# Create the 'Editing table' scene
def reset_log():
    if log_exists():
        bpy.context.screen.scene = bpy.data.scenes['Editing table']
        bpy.ops.scene.delete()
    new_scene = bpy.data.scenes.new('Editing table')
    return True


# Define the main scene
def set_as_main_scene():
    global main_scene
    main_scene = bpy.context.screen.scene
    print('## => The main scene is now :'+ main_scene.name)
    return True

# Set active scene to main
def goto_main_scene():
    print('## => From : '+ bpy.context.screen.scene.name)
    print('## => Going to main scene('+ main_scene.name + ')')
    bpy.context.screen.scene = main_scene
    if bpy.context.screen.scene == main_scene:
        return True
    else:
        print ('## => Error: couldn\'t reach the main scene')

# Returns the type of the selected element in the browser
# This nice function has been written by Björn Sonnenschein
def detect_strip_type(filepath):
    print (filepath)

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

    extension = os.path.splitext(filepath)[1]
    extension = extension.lower()
    if extension in imb_ext_movie:
        type = 'MOVIE'
    elif extension in imb_ext_audio:
        type = 'SOUND'
    else:
        type = None
    print (type)
    return type

# ----------------------------------------------------------------------

def make_wagon():

# Make sure main_scene is already defined
    try:
        main_scene
    except NameError:
        return

    #random in out ? ** for test
#    for obj in main_scene.objects:
#        if obj.type not in bad_obj_types:
#            if len(obj.keys()) > 1:
#                obj.inpoint=random.randint(10,10)
#                obj.outpoint=obj.inpoint+random.randint(20,20)
#                print (obj.name+'\t'+str(obj.inpoint)+'\t'+str(obj.outpoint)+'\n')

    #find folders only
    folders=[]
    for obj in main_scene.objects:
        if obj.type not in bad_obj_types:
            if len(obj.keys()) > 1:
                if obj.parent == None:
                    folders.append(obj)


    #find proporties of children
    for f in folders:
        for obj in f.children:
            if len(obj.keys()) > 1:
                print(obj.name)


    #list all the tags
    tags=[]
    for obj in main_scene.objects:
        if obj.type not in bad_obj_types:
            if len(obj.keys()) > 1:
                if obj.parent != None:
                    temp=(obj.tags).split()
                    for i in temp:
                        if i not in tags:
                            tags.append(i)



    #Wagons of clips by tags

    #context
    original_type = bpy.context.area.type
    bpy.context.area.type = "SEQUENCE_EDITOR"
    # create a temporary scene
    bpy.ops.scene.new(type='NEW')
    bpy.context.scene.name = "temp"
    # iteration of tags
    for t in tags:
        clips=[]
        bpy.ops.scene.new(type='NEW')
        bpy.context.scene.name = "log_"+t
        bpy.context.scene.frame_current=1

        for obj in main_scene.objects:
            if obj.parent != None:
                if t in (obj.tags).split():
                    clips.append(obj)
        #iteration of clips
        for c in clips:
            inpoint=c.inpoint
            outpoint=c.outpoint
            length = outpoint-inpoint
            print('lenght : ', length)
            original_scene = bpy.context.screen.scene
            bpy.context.screen.scene = bpy.data.scenes['temp']
            if inpoint < outpoint:
                bpy.ops.sequencer.movie_strip_add(filepath=c.parent.name+'/'+c.name, frame_start=1)
                bpy.ops.sequencer.select_all(action = "SELECT")
                for s in bpy.context.selected_sequences:
                    s.frame_final_start = inpoint
                    s.frame_final_end = outpoint
                    bpy.context.scene.frame_current = s.frame_final_start
                bpy.ops.sequencer.copy()
                bpy.ops.sequencer.select_all(action = "SELECT")
                bpy.ops.sequencer.delete()
                bpy.context.scene.frame_current = 1
                bpy.context.screen.scene = original_scene
                bpy.ops.sequencer.paste()
                bpy.ops.marker.add()
                bpy.ops.marker.rename(name=c.name)
                bpy.context.scene.frame_current += length
#        bpy.ops.sequencer.select_all(action = "SELECT")
        bpy.ops.sequencer.view_all()
        bpy.context.scene.frame_end =  bpy.context.scene.frame_current
    bpy.context.screen.scene = bpy.data.scenes['temp']
    bpy.ops.scene.delete()
    bpy.context.area.type = original_type


# ----------------------------------------------------------------------

# underline function
def scores(the_string):
    score = ''
    for x in str(the_string):
        score=score + '-'
    return score

# create the log text file
def create_the_log_file():

# Make sure main_scene is already defined
    try:
        main_scene
    except NameError:
        return

    #find folders only
    folders=[]
    for obj in main_scene.objects:
        if obj.type not in bad_obj_types:
            if len(obj.keys()) > 1:
                if obj.parent == None:
                    folders.append(obj)


    #Create the file
    log_text = bpy.data.texts.new('Editing table')
    the_time = (time.strftime("%d/%m/%Y")) + ' - ' + (time.strftime("%H:%M:%S"))
    log_text.write(scores(the_time)+'\n')
    log_text.write(
    main_scene.name+'\n')
    log_text.write(the_time)
    log_text.write('\n' + scores(the_time))
    log_text.write('\n\n')

    log_text.write('\nCLIPS BY LOCATION\n' + scores('CLIPS BY LOCATION') + '\n')

    #find proporties of children
    for f in folders:
        log_text.write('\n['+f.name+']\n\n')
        log_text.write('clip\t\t\t\tin\t\t\tout\t\t\ttags\t\t\t\tnote\n----\t\t\t\t--\t\t\t---\t\t\t----\t\t\t\t----\n')
        for obj in f.children:
            if len(obj.keys()) > 1:
                log_text.write(obj.name+'\t\t\t'+ str(obj.inpoint) + '\t\t\t' + str(obj.outpoint) + '\t\t\t' + obj.tags+'\t\t\t\t\n')



    #list all the tags
    tags=[]
    for obj in main_scene.objects:
        if obj.type not in bad_obj_types:
            if len(obj.keys()) > 1:
                if obj.parent != None:
                    temp=(obj.tags).split()
                    for i in temp:
                        if i not in tags:
                            tags.append(i)

    log_text.write('\n\nLSIT OF TAGS :\n' + scores('List of tags :') + '\n')
    for t in tags:
        log_text.write(t+'\n')


    #list of clips by tags
    log_text.write('\n\nLIST OF CLIPS BY TAG :\n' + scores('LIST OF CLIPS BY TAG :') + '\n\n')
    log_text.write('clip\t\t\t\tin\t\t\tout\t\t\tnote\n----\t\t\t\t--\t\t\t---\t\t\t----\n')

    for t in tags:
        clips=[]
        for obj in main_scene.objects:
            if obj.parent != None:
                if t in (obj.tags).split():
                    clips.append(obj)
        log_text.write ("\n["+t+"]\n")
        for c in clips:
            log_text.write (c.name+'\t\t\t'+ str(c.inpoint) + '\t\t\t' + str(c.outpoint)+'\t\t\t\n')


# --CLASSES--------------------------------------------------------------------------

# Creating the IN/OUT PANEL
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
        if log_exists():
            if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
                row=layout.row()
                row.operator("sequencer.trim", icon="ARROW_LEFTRIGHT")
                layout.separator()
                row.operator("sequencer.setin", icon="TRIA_RIGHT")
                row.operator("sequencer.setout", icon='TRIA_LEFT')
                row.operator("sequencer.place", icon="PASTEFLIPDOWN")
                row.prop(context.scene,"meta")
                row.operator("sequencer.back", icon="LOOP_BACK")
            else:
                row=layout.row()
                row.operator("sequencer.import", icon="ZOOMIN")
                row.operator("sequencer.trim", icon="ARROW_LEFTRIGHT")
                row.prop(context.scene,"local_edit")
        else:
                row=layout.row()
                row.operator("sequencer.import", icon="ZOOMIN")
                row.operator("sequencer.trim", icon="ARROW_LEFTRIGHT")
                row.prop(context.scene,"local_edit")


class tags_panel(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Tags"

    @classmethod
    def poll(cls, context):
        return context.scene.name == 'Editing table'

    def draw(self, context):
        self.layout.prop(main_scene.objects.active, "tags")


# Creating the Place button operator
class OBJECT_OT_Place(bpy.types.Operator):
    bl_label = "Place"
    bl_idname = "sequencer.place"
    bl_description = "Place the clip in the timeline"

    def invoke(self, context, event):
        global inpoint
        global outpoint
        global main_scene

        inpoint = bpy.data.scenes['Editing table'].frame_start
        outpoint = bpy.data.scenes['Editing table'].frame_end

        if inpoint > 1 :
            bpy.ops.sequencer.select_all(action = "SELECT")
            bpy.context.scene.frame_current = inpoint
            bpy.ops.sequencer.cut(frame=inpoint, type='SOFT', side='LEFT')
            bpy.ops.sequencer.delete()

        bpy.ops.sequencer.select_all(action = "SELECT")

        bpy.context.   scene.frame_current = outpoint
        bpy.ops.sequencer.cut(frame=outpoint, type='SOFT', side='RIGHT')
        bpy.ops.sequencer.delete()

        bpy.context.scene.frame_current = inpoint
        bpy.ops.sequencer.select_all(action = "SELECT")

        if bpy.data.scenes['Editing table'].meta==True:
            bpy.ops.sequencer.meta_make()
            bpy.ops.sequencer.select_all(action = "SELECT")

        bpy.ops.sequencer.copy()
        goto_main_scene()
        bpy.ops.sequencer.paste()
        bpy.context.scene.frame_current = bpy.context.scene.frame_current + (outpoint-inpoint)
        # clean up
        bpy.context.screen.scene = bpy.data.scenes['Editing table']
        bpy.ops.sequencer.select_all(action = "SELECT")
        bpy.ops.sequencer.delete()
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_current = 1
        bpy.context.scene.frame_end = 250
        bpy.ops.sequencer.view_all()
        goto_main_scene()
        if main_scene.local_edit == False:
            bpy.context.screen.scene = bpy.data.scenes['Editing table']
        #bpy.context.area.type = original_type

        return {'FINISHED'}

# Creating the IMPORT button operator
class OBJECT_OT_import(bpy.types.Operator):
    bl_label = "Import clip"
    bl_idname = "sequencer.import"
    bl_description = "Import the selected clip in the browser"
    global main_scene
    def invoke(self, context, event):
        #main = bpy.context.screen.scene
        global clip_obj

        #get directory & name (path - clip)
        for a in bpy.context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                params = a.spaces[0].params
                path = params.directory
                clip = params.filename
                break

        if bpy.context.screen.scene.name != 'Editing table':
            set_as_main_scene()

        reset_log()

        file_exists = False
        for ob in main_scene.objects:
            if ob.name == clip:
                file_exists = True
                break

        if file_exists == True:
            bpy.context.scene.objects.active = bpy.data.objects[clip]
            clip_obj = bpy.data.objects[clip]
            start = clip_obj.inpoint
            end = clip_obj.outpoint

            bpy.context.screen.scene = bpy.data.scenes['Editing table']

            file_type = detect_strip_type(path+clip)
            if (file_type == "MOVIE") or (file_type == "SOUND"):
                original_type = bpy.context.area.type
                bpy.context.area.type = "SEQUENCE_EDITOR"
                if (file_type == "MOVIE"):
                    bpy.ops.sequencer.movie_strip_add(frame_start=0, filepath=path+clip)
                else:
                    bpy.ops.sequencer.sound_strip_add(frame_start=0, filepath=path+clip)
                bpy.context.area.type = original_type

                if start > 0:
                    bpy.data.scenes['Editing table'].frame_start = start
                else:
                    bpy.data.scenes['Editing table'].frame_start = 1

                if end >1:
                    bpy.data.scenes['Editing table'].frame_end = end
                else:
                    bpy.data.scenes['Editing table'].frame_end = bpy.context.scene.sequence_editor.active_strip.frame_final_duration

                bpy.context.scene.frame_current = start
                bpy.ops.sequencer.cut(frame=start, type='SOFT', side='LEFT')
                bpy.ops.sequencer.delete()

                bpy.ops.sequencer.select_all(action = "SELECT")

                bpy.context.scene.frame_current = end
                bpy.ops.sequencer.cut(frame=end, type='SOFT', side='RIGHT')
                bpy.ops.sequencer.delete()

                bpy.context.scene.frame_current = start
                bpy.ops.sequencer.select_all(action = "SELECT")
                bpy.ops.sequencer.copy()
                goto_main_scene()
                bpy.ops.sequencer.paste()
                bpy.context.scene.frame_current = bpy.context.scene.frame_current + (end-start)
        else:
                file_type = detect_strip_type(path+clip)
                if (file_type == "MOVIE"):
                        bpy.ops.sequencer.movie_strip_add(filepath=path+clip, frame_start=bpy.context.scene.frame_current)
                else:
                        bpy.ops.sequencer.sound_strip_add(filepath=path+clip, frame_start=bpy.context.scene.frame_current)


        return {'FINISHED'}


# Creating the TRIM (EDIT) button operator
class OBJECT_OT_Trim(bpy.types.Operator):
    bl_label = "Edit clip"
    bl_idname = "sequencer.trim"
    bl_description = "Trim the selected clip in the browser"
    global main_scene
    def invoke(self, context, event):
        #main = bpy.context.screen.scene
        global clip_obj

        #get directory & name (path - clip)
        for a in bpy.context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                params = a.spaces[0].params
                path = params.directory
                clip = params.filename
                break

        # set current scene as main scene
#        try:
#            main_scene
#        except NameError:
#        if log_exists():
        if bpy.context.screen.scene.name != 'Editing table':
            set_as_main_scene()
#        set_as_main_scene()

        #create the log scene if it doesn't already exist
        reset_log()

        # create folder object if it doesn't already exist

        folder_exists = False
        for ob in main_scene.objects:
            if ob.name == path:
                folder_exists = True
                break
        goto_main_scene()
#        if bpy.data.objects.get(path) is None and
        if folder_exists == False:
            bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(random.randint(-20,20), 0, 0), layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))
            bpy.context.object.show_name = True
            bpy.context.object.empty_draw_type = 'CUBE'
            temp_obj = bpy.context.active_object
            temp_obj.name = path
            temp_obj.inpoint = 1
            temp_obj.outpoint = 1
            temp_obj.tags = 'none'
        else:
            print(path+' EXISTS')

        # create clip object if it doesn't already exist
        file_exists = False
        for ob in main_scene.objects:
            if ob.name == clip:
                file_exists = True
                break
        if file_exists == False:
            bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, random.randint(1,10), random.randint(1,10)), layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))
            bpy.context.object.show_name = True
            bpy.context.object.empty_draw_type = 'SPHERE'
            temp_obj = bpy.context.active_object
            temp_obj.name = clip
            temp_obj.inpoint = -10
            temp_obj.outpoint = -10
            temp_obj.tags = 'none'
        else:
            bpy.context.scene.objects.active = bpy.data.objects[clip]
        # registering the two objects
        clip_obj = bpy.data.objects[clip]
        folder_obj = bpy.data.objects[path]

        # link the clip to the folder
        clip_obj.parent = folder_obj

        # retrieve the in&out points of the object
        start = clip_obj.inpoint
        end = clip_obj.outpoint
        tags = clip_obj.tags
        print (end)

        # Go to log scene, import the file and set start/end if exists
        bpy.context.screen.scene = bpy.data.scenes['Editing table']

        #check if the type of the file is MOVIE or SOUND
        file_type = detect_strip_type(path+clip)
        if (file_type == "MOVIE") or (file_type == "SOUND"):
            original_type = bpy.context.area.type
            bpy.context.area.type = "SEQUENCE_EDITOR"
            if (file_type == "MOVIE"):
                bpy.ops.sequencer.movie_strip_add(frame_start=0, filepath=path+clip)
            else:
                bpy.ops.sequencer.sound_strip_add(frame_start=0, filepath=path+clip)
            bpy.context.area.type = original_type

            if start > 0:
                bpy.data.scenes['Editing table'].frame_start = start
            else:
                bpy.data.scenes['Editing table'].frame_start = 1

            if end >1:
                bpy.data.scenes['Editing table'].frame_end = end
            else:
                bpy.data.scenes['Editing table'].frame_end = bpy.context.scene.sequence_editor.active_strip.frame_final_duration
        bpy.ops.sequencer.view_selected()
        return {'FINISHED'}

# creating the IN button operator
class OBJECT_OT_Setin(bpy.types.Operator):
    bl_label = "IN"
    bl_idname = "sequencer.setin"
    bl_description = "Set the IN point of the clip"

    def invoke(self, context, event):
        global inpoint, clip_obj
        if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
            inpoint=bpy.context.scene.frame_current
            bpy.data.scenes['Editing table'].frame_start = inpoint
            clip_obj.inpoint = inpoint
        return {'FINISHED'}


# creating the OUT button operator
class OBJECT_OT_Setout(bpy.types.Operator):
    bl_label = "OUT"
    bl_idname = "sequencer.setout"
    bl_description = "Set the OUT point of the clip"

    def invoke(self, context, event):
        global outpoint, inpoint
        if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
            outpoint=bpy.context.scene.frame_current
            bpy.data.scenes['Editing table'].frame_end = outpoint
            clip_obj.outpoint = outpoint
            print(inpoint)
            if clip_obj.inpoint < 1:
                inpoint = 1
                clip_obj.inpoint = inpoint
        return {'FINISHED'}

# creating the back button operator
class OBJECT_OT_Back(bpy.types.Operator):
    bl_label = "Back to Sequence"
    bl_idname = "sequencer.back"
    bl_description = "Go back to the main sequence"

    def invoke(self, context, event):
        global main_scene
        if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
            goto_main_scene()
        return {'FINISHED'}

# creating the menu "create log file" operator
class SEQUENCER_OT_createlog(bpy.types.Operator):
    bl_idname = "sequencer.createlog"
    bl_label = "Create the log file"
    def execute(self, context):
        create_the_log_file()
        return {'FINISHED'}

class SEQUENCER_OT_makewagon(bpy.types.Operator):
    bl_idname = "sequencer.makewagon"
    bl_label = "Create the tag scenes"
    def execute(self, context):
        make_wagon()
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

def log_func(self, context):
    self.layout.operator(SEQUENCER_OT_createlog.bl_idname, text="Create the log file", icon='LINENUMBERS_ON')

def wagon_func(self, context):
    self.layout.operator(SEQUENCER_OT_makewagon.bl_idname, text="Build the tag scenes", icon='OOPS')

# -- REGISTRATIONS -----------------------------------------------------

def register():
    bpy.utils.register_class(EasyLog)
    bpy.types.INFO_HT_header.append(draw_item)
    bpy.utils.register_class(iop_panel)
    bpy.utils.register_class(OBJECT_OT_Trim)
    bpy.utils.register_class(OBJECT_OT_Setin)
    bpy.utils.register_class(OBJECT_OT_Setout)
    bpy.utils.register_class(OBJECT_OT_Place)
    bpy.utils.register_class(OBJECT_OT_Back)
    bpy.utils.register_class(SEQUENCER_OT_createlog)
    bpy.types.OBJECT_MT_easy_log.append(log_func)
    bpy.utils.register_class(tags_panel)
    bpy.types.OBJECT_MT_easy_log.append(wagon_func)
    bpy.utils.register_class(SEQUENCER_OT_makewagon)
    bpy.utils.register_class(OBJECT_OT_import)


def unregister():
    bpy.utils.unregister_class(EasyLog)
    bpy.types.INFO_HT_header.remove(draw_item)
    bpy.utils.unregister_class(iop_panel)
    bpy.utils.unregister_class(OBJECT_OT_Trim)
    bpy.utils.unregister_class(OBJECT_OT_Setin)
    bpy.utils.unregister_class(OBJECT_OT_Setout)
    bpy.utils.unregister_class(OBJECT_OT_Place)
    bpy.utils.unregister_class(OBJECT_OT_Back)
    bpy.utils.unregister_class(SEQUENCER_OT_createlog)
    bpy.types.OBJECT_MT_easy_log.remove(log_func)
    bpy.utils.unregister_class(tags_panel)
    bpy.types.OBJECT_MT_easy_log.remove(wagon_func)
    bpy.utils.unregister_class(SEQUENCER_OT_makewagon)
    bpy.utils.unregister_class(OBJECT_OT_import)


if __name__ == "__main__":
    register()

def updateStringParameter(self,context):
#    # This def gets called when one of the properties changes state.
    print(self.my_string)
def updateIntParameter(self,context):
#    # This def gets called when one of the properties changes state.
    print(self.my_int)
