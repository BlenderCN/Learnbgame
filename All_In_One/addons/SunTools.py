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

# todo: Die Einstellung fuer preserve range entfernen. Die range sollte immer preserved weren
# todo: Moeglichkeit, wenn mehrere strips gecomposited werden, die gleiche omposition
# fuer alle strips mit gleicher quelle zu nehmen
# todo: Composites nicht hinzufuegen, sondern die eigentlichen strips ersetzen
# dabei aber einen toggle button, der die composites wieder durch die strips ersetzt.
# dafuer koennte man in der komposition ja die source datei speichern und dann
# kann man ganz einfach hin- und her switchen. dafuer muss man aber auch die quellen
# fuer alle anderen clips ersetzen!


bl_info = {
    "name": "SunTools",
    "description": "Define in- and outpoints of your material in the file browser",
    "author": "Björn Sonnenschein",
    "version": (1, 3),
    "blender": (2, 71, 0),
    "location": "File Browser > Tools",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Learnbgame",
}

import bpy, os
from os import listdir
from os.path import isfile, join
import glob

##TODO
# instead of setting area type for non-vse to file browser in edit range operator, save the current area type in a variable and switch back to it.
################################

scnType = bpy.types.Scene

###### Common Functions #######
def act_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return None

def get_masterscene():
    masterscene = None

    for i in bpy.data.scenes:
        if (i.timeline == True):
            masterscene = i
            break

    return masterscene

def detect_strip_type(filepath):
    imb_ext_image = [
    # IMG
    ".png",
    ".tga",
    ".bmp",
    ".jpg", ".jpeg",
    ".sgi", ".rgb", ".rgba",
    ".tif", ".tiff", ".tx",
    ".jp2",
    ".hdr",
    ".dds",
    ".dpx",
    ".cin",
    ".exr",
    # IMG QT
    ".gif",
    ".psd",
    ".pct", ".pict",
    ".pntg",
    ".qtif",
    ]

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
    if extension in imb_ext_image:
        type = 'IMAGE'
    elif extension in imb_ext_movie:
        type = 'MOVIE'
    elif extension in imb_ext_audio:
        type = 'SOUND'
    else:
        type = None

    return type

####### Scene Properties ########

### IOP Section 
BoolProperty = bpy.props.BoolProperty
scnType.custom_screen = BoolProperty( name="Custom Screen",
                                     description = "Use a custom screen layout for range editing ",
                                     default=False )

scnType.meta = BoolProperty( name="Metastrip",
                                     description = "Combine audio and video into metastrip on insertion into Masterscene",
                                     default=False )

scnType.zoom = BoolProperty( name="Zoom",
                                     description = "Zoom to the entire Clip after entering Edit Range",
                                     default=False )

scnType.show_options = BoolProperty( name="Show Options",
                                     description = "",
                                     default=False )

scnType.p25 = BoolProperty( name="25%",
                                     description = "Proxy sizes to be created",
                                     default=False )

scnType.p50 = BoolProperty( name="50%",
                                     description = "Proxy sizes to be created",
                                     default=False )

scnType.p75 = BoolProperty( name="75%",
                                     description = "Proxy sizes to be created",
                                     default=False )

scnType.p100 = BoolProperty( name="100%",
                                     description = "Proxy sizes to be created",
                                     default=False )
scnType.proxy_recursive = BoolProperty(name="Proxy: include subfoders",
                                     description = 'Generate proxies also for files in subfolders',
                                     default=False )

#Is it the timeline scene?
scnType.timeline = BoolProperty( name="Timeline",
                                     description = "Is this your actual timeline?",
                                     default=False)

#Declare usefulness
scnType.good_clip = BoolProperty( name="Good",
                                     description = "Is this an useful Clip? ",
                                     default=False )

#Define Screen to change to for editing range
StringProperty = bpy.props.StringProperty
editingrangestring = StringProperty(name="Editing Range Screen", description="The name of the screen layout you use for editing range", default="Video Editing" )
scnType.editing_range_screen = editingrangestring

#Define Screen to change to for editing
editingstring = StringProperty(name="Editing Screen", description="The name of the screen layout you use for editing", default="Video Editing" )
scnType.editing_screen = editingstring

#Channel selector
IntProperty = bpy.props.IntProperty
intprop = IntProperty( name="Channel", description="Define into which channel the new strip will be inserted ", default=1, min=1, max=30, step=1)
scnType.channel = intprop

#Define the Path of the File the Scene belongs to.
sourcepath = StringProperty(name="Source Path", description="The Path of the File the Scene belongs to.", default="none" )
scnType.source_path = sourcepath


### TrimTools Section

scnType.select_audio = BoolProperty( name="Select Audio",
                                     description = "Select appropriate audio strips, too? ",
                                     default=True )

####### Panels #####
class MovieManagerPanelBrowser(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOLS"
    bl_label = "Movie Manager"

    def draw(self, context):
        scn = bpy.context.scene
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.prop( scn, "p100" )
        row.prop( scn, "p75" )
        row.prop( scn, "p50" )
        row.prop( scn, "p25" )
        row = layout.row()
        col = row.column()
        col.operator( "file.moviemanager_proxy")
        row = layout.row()
        row.prop(scn, 'proxy_recursive')

        row = layout.row()
        col = row.column()
        col.operator( "file.moviemanager_edit_range" )

class MovieManagerPanel(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Movie Manager"

    def draw(self, context):
        scn = bpy.context.scene
        layout = self.layout

        if not bpy.context.scene.timeline:
            row = layout.row()
            row.operator( "sequencer.moviemanager_switch_back_to_timeline" )

            if bpy.context.scene.source_path != "none":
                row = layout.row()
                col = row.column()
                col.operator( "sequencer.moviemanager_hide" )
                row.prop(scn, "good_clip" )


        row = layout.row()
        col = row.column()
        if bpy.context.scene.timeline:
            col.operator( "sequencer.moviemanager_insert_strip" )

            row = layout.row()
            col = row.column()
            col.operator( "sequencer.moviemanager_clean" )


        if not bpy.context.scene.timeline:
            col.operator( "sequencer.moviemanager_insert_strip_masterscene" )

        row = layout.row()
        col = row.column()
        col.operator( "sequencer.moviemanager_unmeta" )
        # row.operator( "moviemanager.meta" )

        if not bpy.context.scene.timeline:
            row = layout.row()
            row.operator( "sequencer.moviemanager_set_timeline" )

        row = layout.row()

        if bpy.context.scene.timeline:
            row.prop( scn, "show_options" )

            if bpy.context.scene.show_options:

                row = layout.row()
                col = row.column()
                col.prop( scn, "channel" )

                row = layout.row()
                col = row.column()

                col.prop( scn, "editing_screen" )
                col.prop( scn, "editing_range_screen" )

                row = layout.row()
                col = row.column()
                row.prop( scn, "custom_screen" )
                col.prop( scn, "zoom" )

                row = layout.row()
                row.prop( scn, "meta" )

class TrimToolsPanel(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Trim Tools"

    def draw(self, context):
        scn = bpy.context.scene
        layout = self.layout

        row = layout.row()
        col = row.column()

        col.operator( "sequencer.trimtools_select_current" )
        row.prop( scn, "select_audio" )

        row = layout.row()
        col = row.column()

        col.operator( "sequencer.trimtools_cut_current" )
        row.operator( "sequencer.trimtools_snap_end" )

        row = layout.row()
        col = row.column()
        col.operator( "sequencer.trimtools_trim_left" )
        row.operator( "sequencer.trimtools_trim_right" )

##### MovieManager Operators ####

class Set_Timeline (bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_set_timeline"
    bl_label = "Set as Timeline"
    bl_description = "Set this scene as Timeline"

    def invoke (self, context, event):
        for i in bpy.data.scenes:
            i.timeline = False

        bpy.context.scene.timeline = True

        return {'FINISHED'}

class CleanupScenes (bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_clean"
    bl_label = "Clean Scenes"
    bl_description = "Delete scenes referring to clips that don't exists"

    def invoke (self, context, event):
        for scene_clip in bpy.data.scenes:
            source_path = scene_clip.source_path
            if source_path is not None:
                # check if strip file exists
                if not os.path.isfile(source_path):
                    bpy.data.scenes.remove(scene_clip, True)

        return {'FINISHED'}

class Hide_Operator (bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_hide"
    bl_label = "Hide"
    bl_description = "Hide clips that are not useful"

    def invoke (self, context, event):
        for scene_clip in bpy.data.scenes:
            source_path = scene_clip.source_path
            if (source_path != "none"):
                self.hide_file(source_path, scene_clip)

        return {'FINISHED'}

    def hide_file(self, filepath, scene_clip):
        path_directory, filename = os.path.split(filepath)

        changed = False
        if (filename[0] == "." and scene_clip.good_clip == True):
            filename_new = filename[1:]
            changed = True
        elif (filename[0] != "." and scene_clip.good_clip == False):
            filename_new = "." + filename
            changed = True
        if (changed == True):
            filepath_new = path_directory + filename_new
            os.rename(filepath, filepath_new)

            for sequence_scene in bpy.data.scenes:
                if (sequence_scene.source_path == filepath):
                    sequence_scene.source_path = filepath_new
                try:
                    for sequence in sequence_scene.sequence_editor.sequences_all:
                        if (sequence.filepath == bpy.path.relpath(filepath)):
                            sequence.filepath = bpy.path.relpath(filepath_new)
                except:
                    print("hadn't a sequencer. poor little scene!")


class Proxy_Operator(bpy.types.Operator):
    """ Automatically create proxies with given settings for all strips in the directory
    """
    bl_idname = "file.moviemanager_proxy"
    bl_label = "Create Proxies"

    def invoke(self, context, event ):
        masterscene = get_masterscene()
        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}

        if (masterscene.p50 == False and masterscene.p25 == False and masterscene.p75 == False and masterscene.p100 == False ):
            self.report({'ERROR_INVALID_INPUT'},'No Proxies to create!.')
            return {'CANCELLED'}

        #get directory
        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                directory = a.spaces[0].params.directory
                break
        try:
            directory
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}

        #Change the current area to VSE so that we can also call the operator from any other area type.
        bool_IsVSE = True
        native_area_type = 'SEQUENCE_EDITOR'
        if (bpy.context.area.type != 'SEQUENCE_EDITOR'):
            native_area_type = bpy.context.area.type
            bpy.context.area.type = 'SEQUENCE_EDITOR'
            bool_IsVSE = False

        # store whether to search files recursively from current scene, as qID will have it
        # set to False
        proxy_recursive = bpy.context.scene.proxy_recursive

        #Check if scene exists, if not -> new
        self.switch_to_scene(scene_name='qID')

        ## Get files in directory
        if proxy_recursive:
            filepaths = []
            for root, dirs, files in os.walk(directory):
                # only add files if they are not in a proxy directory
                if 'BL_proxy' not in root:
                    filepaths.extend([os.path.join(root, f) for f in files])
        else:
            filepaths = [ os.path.join(directory, f) for f in listdir(directory) if isfile(join(directory,f)) ]

        strips_created = self.create_strips_and_set_proxy_settings(masterscene, filepaths)

        if strips_created:
            self.report({'INFO'}, 'Generating Proxies. Blender freezes until job is finished.')
            bpy.ops.sequencer.select_all(action='SELECT')
            bpy.ops.sequencer.rebuild_proxy()
            bpy.ops.sequencer.delete()
        else:
            self.report({'INFO'},'No video files found.')

        if (bool_IsVSE == False):
            bpy.context.area.type = native_area_type

        Switch_back_to_Timeline_Operator.invoke(self, context, event)

        self.report({'INFO'}, 'Finished proxy generation.')

        return {'FINISHED'}

    def switch_to_scene(self, scene_name):
        """ If a scene of given name does not exist, create it. Then switch context to the scene
        
        :param scene_name: Name of the scene
        :return: 
        """
        scene_exists = False
        for i in bpy.data.scenes:
            if i.name == scene_name:
                scene_exists = True

        if (scene_exists == True):
            bpy.context.screen.scene = bpy.data.scenes[scene_name]
        else:
            new_scene = bpy.data.scenes.new(scene_name)

        scene = bpy.data.scenes[scene_name]
        bpy.context.screen.scene = scene

    def create_strips_and_set_proxy_settings(self, masterscene, filepaths):
        strips_created = False
        for path in filepaths:
            filename = os.path.basename(path)
            strip_type = detect_strip_type(filename)

            if (strip_type == 'MOVIE'):
                print('creating proxy for {}'.format(path))
                strips_created = True
                bpy.ops.sequencer.movie_strip_add(filepath=path)
                for sequence in bpy.context.scene.sequence_editor.sequences:
                    if (sequence.type == 'MOVIE'):
                        sequence.use_proxy = True
                        if (masterscene.p25 == True):
                            sequence.proxy.build_25 = True
                        if (masterscene.p50 == True):
                            sequence.proxy.build_50 = True
                        if (masterscene.p75 == True):
                            sequence.proxy.build_75 = True
                        if (masterscene.p100 == True):
                            sequence.proxy.build_100 = True

        return strips_created


class Edit_Range_Operator(bpy.types.Operator):
    bl_idname = "file.moviemanager_edit_range"
    bl_label = "Edit Range"
    bl_description = "Edit the Range of the selected clip in the File Browser. Use the new scene's Start and end Frame"

    def invoke (self, context, event):

        masterscene = get_masterscene()
        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}

        #get scene parameters
        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                scene_parameters = a.spaces[0].params
                break
        try:
            filename = scene_parameters.filename
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}

        if scene_parameters.filename == '':
            self.report({'ERROR_INVALID_INPUT'}, 'No file selected')
            return {'CANCELLED'}

        #Change the current area to VSE so that we can also call the operator from any other area type.
        bool_IsVSE = True
        if (bpy.context.area.type != 'SEQUENCE_EDITOR'):
            bpy.context.area.type = 'SEQUENCE_EDITOR'
            bool_IsVSE = False

        source_path = os.path.join(scene_parameters.directory, filename)
        strip_type = detect_strip_type(filename)
        scene_name = filename + "_Range"

        if (strip_type == 'MOVIE' or 'SOUND'):
            self.create_new_scene_with_strip_and_switch_to_scene(masterscene, source_path, strip_type, scene_name)
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'Invalid file format')
            return {'CANCELLED'}

        if (masterscene.zoom == True and bool_IsVSE == True):
            bpy.ops.sequencer.view_selected()
        if (bool_IsVSE == False):
            bpy.context.area.type = 'FILE_BROWSER'

        #Change to custom layout if wanted.
        if (masterscene.custom_screen == True):
            for screen in bpy.data.screens:
                bpy.ops.screen.screen_set(delta=1)
                if (bpy.context.screen.name == masterscene.editing_range_screen):
                    break
            bpy.context.screen.scene = bpy.data.scenes[scene_name]

        return {'FINISHED'}

    def create_new_scene_with_strip_and_switch_to_scene(self, masterscene, source_path, strip_type, scene_name):
        # get the according scene
        scene_exists = False
        for scene in bpy.data.scenes:
            if scene.source_path == source_path:
                scene_exists = True
                scene_name = scene.name

        if (scene_exists == True):
            bpy.context.screen.scene = bpy.data.scenes[scene_name]
            bpy.context.scene.sync_mode = masterscene.sync_mode
        else:
            scene = self.create_new_scene_with_settings_from_masterscene(masterscene, scene_name, source_path)
            bpy.context.screen.scene = scene
            bpy.context.scene.sync_mode = masterscene.sync_mode

            if (strip_type == 'MOVIE'):
                bpy.ops.sequencer.movie_strip_add(frame_start=0, filepath=source_path)
            elif (strip_type == 'SOUND'):
                bpy.ops.sequencer.sound_strip_add(frame_start=0, filepath=source_path)

            bpy.context.scene.frame_end = bpy.context.scene.sequence_editor.active_strip.frame_final_duration

    def create_new_scene_with_settings_from_masterscene(self, masterscene, scene_name, source_path):
        new_scene = bpy.data.scenes.new(scene_name)
        scene_name = new_scene.name
        bpy.data.scenes[scene_name].source_path = source_path

        new_scene.render.resolution_x = masterscene.render.resolution_x
        new_scene.render.resolution_y = masterscene.render.resolution_y
        new_scene.render.resolution_percentage = masterscene.render.resolution_percentage
        new_scene.render.fps = masterscene.render.fps
        new_scene.frame_start = 0

        return new_scene

class Switch_back_to_Timeline_Operator(bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_switch_back_to_timeline"
    bl_label = "Get Back"

    def invoke(self, context, event ):

        masterscene = get_masterscene()
        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'},'Please set a Timeline first.')
            return {'CANCELLED'}

        if (masterscene.custom_screen == True):
            for screen in bpy.data.screens:
                bpy.ops.screen.screen_set(delta=1)
                if (bpy.context.screen.name == masterscene.editing_screen):
                    break
            bpy.context.screen.scene = masterscene
        else:
            bpy.context.screen.scene = masterscene

        return {'FINISHED'}


class Insert_Strip_Masterscene(bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_insert_strip_masterscene"
    bl_label = "Insert into editing scene"
    bl_description = "Insert the selected Strip into the Timeline of the Editing Scene"

    def invoke(self, context, event):
        """ Called from the range scene. Insert the selected clip into the masterscene,
            performing 2 or 3-point editing if strips are selected in the masterscene.
        """
        masterscene = get_masterscene()
        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'}, 'Please set a Timeline first.')
            return {'CANCELLED'}

        strip_to_insert = bpy.context.scene.sequence_editor.active_strip
        if (strip_to_insert.type == 'MOVIE' or 'SOUND'):
            range_scene_name = bpy.context.scene.name
            bpy.context.screen.scene = masterscene

            frame_start, frame_final_start, frame_final_end, channel = self.get_destination_start_end_frames_and_channel(range_scene_name, strip_to_insert)
            if (strip_to_insert.type == 'MOVIE'):
                bpy.ops.sequencer.movie_strip_add(frame_start=frame_start, channel=channel, overlap=True, filepath=strip_to_insert.filepath)
            elif (strip_to_insert.type == 'SOUND'):
                bpy.ops.sequencer.sound_strip_add(frame_start=frame_start, channel=channel, overlap=True, filepath=strip_to_insert.sound.filepath)
            self.apply_in_and_out_points(masterscene, strip_to_insert, frame_final_start, frame_final_end, channel)

            # change visible scene back
            bpy.context.screen.scene = bpy.data.scenes[range_scene_name]

            return {'FINISHED'}
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'Please select a sound or movie strip.')
            return {'CANCELLED'}

    def get_destination_start_end_frames_and_channel(self, range_scene_name, strip_to_insert):
        # Get current frame and channel.
        # If sequences are selected in the master scene, set it to the active strip for 2-point editing
        if (bpy.context.selected_sequences):
            frame_final_start = bpy.context.screen.scene.sequence_editor.active_strip.frame_final_end
            channel = bpy.context.screen.scene.sequence_editor.active_strip.channel
        else:
            frame_final_start = bpy.context.scene.frame_current
            channel = bpy.data.scenes[range_scene_name].channel

        frame_final_end = frame_final_start + strip_to_insert.frame_final_duration
        frame_start = frame_final_start - (strip_to_insert.frame_final_start - strip_to_insert.frame_start)

        # If there is a selected strip, limit the length of the new one
        try:
            for selected_sequence in bpy.context.selected_sequences:
                if (selected_sequence.frame_final_start < frame_final_end and selected_sequence.frame_final_start > frame_final_start):
                    frame_final_end = selected_sequence.frame_final_start
        except:
            print("no selected sequences")

        return frame_start, frame_final_start, frame_final_end, channel

    def apply_in_and_out_points(self, masterscene, strip_to_insert, frame_final_start, frame_final_end, channel):
        # Apply in and out points
        if (strip_to_insert.type == 'MOVIE' and masterscene.meta == True):
            bpy.ops.sequencer.meta_make()
        for selected_sequence in bpy.context.selected_sequences:
            channel = selected_sequence.channel
            selected_sequence.frame_final_start = frame_final_start
            selected_sequence.frame_final_end = frame_final_end
            selected_sequence.channel = channel

class Insert_Strip(bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_insert_strip"
    bl_label = "Insert selected File"
    bl_description = "Insert the selected File into the Timeline"

    def invoke(self, context, event):
        masterscene = get_masterscene()

        if (masterscene is None):
            self.report({'ERROR_INVALID_INPUT'}, 'Please set a Timeline first.')
            return {'CANCELLED'}

        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                params = a.spaces[0].params
                break
        try:
            params
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}
        if params.filename == '':
            self.report({'ERROR_INVALID_INPUT'}, 'No file selected')
            return {'CANCELLED'}

        path = params.directory + params.filename
        strip_type = detect_strip_type(params.filename)

        if (strip_type == 'MOVIE' or 'SOUND'):
            # find the scene belonging to the strip
            scene_exists = False
            for scene in bpy.data.scenes:
                if scene.source_path == path:
                    scene_exists = True
                    scene = scene
                    break

            #Get current frame and channel
            if (bpy.context.selected_sequences):
                current_frame = bpy.context.screen.scene.sequence_editor.active_strip.frame_final_end
                channel = bpy.context.screen.scene.sequence_editor.active_strip.channel
            else:
                current_frame = bpy.context.scene.frame_current
                channel = bpy.context.scene.channel

            # if a scene exists, insert the strip with proper in- and outpoints.
            # else, insert new strip from filepath
            if (scene_exists == True):
                if (strip_type == 'MOVIE'):
                    bpy.ops.sequencer.movie_strip_add(frame_start=current_frame, channel=channel, filepath=path)
                elif (strip_type == 'SOUND'):
                    bpy.ops.sequencer.sound_strip_add(frame_start=current_frame, channel=channel, filepath=path)

                # get in and out points
                frame_start = bpy.context.scene.sequence_editor.active_strip.frame_start
                frame_end = bpy.context.scene.sequence_editor.active_strip.frame_final_end
                duration = bpy.context.scene.sequence_editor.active_strip.frame_duration
                end_offset = duration - scene.frame_end

                #Apply in and out points
                if (strip_type == 'MOVIE' and bpy.context.scene.meta == True):
                    bpy.ops.sequencer.meta_make()
                for selected_sequene in bpy.context.selected_sequences:
                    channel = scene.channel
                    selected_sequene.frame_final_start = frame_start + scene.frame_start
                    selected_sequene.frame_final_end = frame_end - end_offset + 1
                    selected_sequene.frame_start = frame_start - scene.frame_start
                    selected_sequene.channel = channel
            else:
                if (strip_type == 'MOVIE'):
                    bpy.ops.sequencer.movie_strip_add(frame_start=current_frame, channel=channel, filepath=path)
                elif (strip_type == 'SOUND'):
                    bpy.ops.sequencer.sound_strip_add(frame_start=current_frame, channel=channel, filepath=path)

            if (strip_type == 'MOVIE' and masterscene.meta == True):
                bpy.ops.sequencer.meta_make()
            return {'FINISHED'}


class Unmeta(bpy.types.Operator):
    bl_idname = "sequencer.moviemanager_unmeta"
    bl_label = "Unmeta"
    bl_description = "Separate Audio and Video"

    def invoke(self, context, event):
        for meta_strip in bpy.context.selected_sequences:
            if (meta_strip.type == 'META'):
                channel = meta_strip.channel
                self.separate_meta_strip(meta_strip)
                self.apply_meta_strip_channel(channel)
        return {'FINISHED'}

    def separate_meta_strip(self, meta_strip):
        frame_final_start = meta_strip.frame_final_start
        frame_final_end = meta_strip.frame_final_end
        bpy.ops.sequencer.select_all(action='DESELECT')
        meta_strip.select = True
        bpy.context.scene.sequence_editor.active_strip = meta_strip
        bpy.ops.sequencer.meta_separate()
        for sequence_from_meta in bpy.context.selected_sequences:
            sequence_from_meta.frame_final_start = frame_final_start
            sequence_from_meta.frame_final_end = frame_final_end

    def apply_meta_strip_channel(self, channel):
        for sequence_from_meta in reversed(bpy.context.selected_sequences):
            if (sequence_from_meta.type == 'MOVIE'):
                sequence_from_meta.channel = channel
            else:
                sequence_from_meta.channel = channel + 1

####### TrimTools Operators ########

class select_current (bpy.types.Operator):
    bl_idname = "sequencer.trimtools_select_current"
    bl_label = "Select current Strip"
    bl_description = "Select the Strip on the current frame"

    def invoke (self, context, event):
        channel = 0
        current_frame = bpy.context.scene.frame_current
        is_already_selection = False
        channel_of_selected_strip = 0
        something_is_selected = False
        first_selected_strip = None

        # find out whether an appropiate strip is already selected
        for sequence in bpy.context.scene.sequence_editor.sequences:
            if (sequence.type == 'MOVIE' or sequence.type == 'SCENE' or sequence.type == 'MOVIECLIP' or sequence.type == 'IMAGE' or sequence.type == 'COLOR' or sequence.type == 'MULTICAM'):
                if (sequence.frame_final_start <= current_frame and sequence.frame_final_end >= current_frame):
                    if (sequence.select == True):
                        first_selected_strip = sequence
                        is_already_selection = True
                        break

        for sequence in bpy.context.scene.sequence_editor.sequences:
            if (sequence.type == 'MOVIE' or sequence.type == 'SCENE' or sequence.type == 'MOVIECLIP' or sequence.type == 'IMAGE' or sequence.type == 'COLOR' or sequence.type == 'MULTICAM'):
                if (sequence.frame_final_start <= current_frame and sequence.frame_final_end >= current_frame):
                    if (sequence.channel > channel and is_already_selection == False):
                        bpy.ops.sequencer.select_all(action='DESELECT')
                        bpy.context.scene.sequence_editor.active_strip = sequence
                        sequence.select = True
                        channel = sequence.channel
                        selectedstrip = sequence
                        something_is_selected = True
                    elif (sequence.channel < first_selected_strip.channel and sequence.channel > channel_of_selected_strip and is_already_selection == True):
                        bpy.ops.sequencer.select_all(action='DESELECT')
                        bpy.context.scene.sequence_editor.active_strip = sequence
                        sequence.select = True
                        channel = sequence.channel
                        selectedstrip = sequence
                        channel_of_selected_strip = sequence.channel
                        something_is_selected = True

        if (something_is_selected == False and is_already_selection == True):
            bpy.ops.sequencer.select_all(action='DESELECT')

        # select the audio of the strip.
        # do selection by duration and position and not by name to cover case of externally recorded audio
        for sequence in bpy.context.scene.sequence_editor.sequences:
            if (sequence.type == 'SOUND' and something_is_selected == True and bpy.context.scene.select_audio == True):
                if (sequence.frame_final_start == selectedstrip.frame_final_start and sequence.frame_final_end == selectedstrip.frame_final_end):
                        sequence.select = True

        return {'FINISHED'}


class cut_current (bpy.types.Operator):
    bl_idname = "sequencer.trimtools_cut_current"
    bl_label = "Cut current Strip"
    bl_description = "Cut the Strip on the current frame"

    def invoke (self, context, event):
        bpy.ops.sequencer.trimtools_select_current()

        current_frame = bpy.context.scene.frame_current
        bpy.ops.sequencer.cut(frame=current_frame)

        return {'FINISHED'}


class trim_left (bpy.types.Operator):
    bl_idname = "sequencer.trimtools_trim_left"
    bl_label = "Trim Left"
    bl_description = "Set the selected clip's starting frame to current frame"

    def invoke (self, context, event):
        for selected_sequence in bpy.context.selected_sequences:
            selected_sequence.frame_final_start = bpy.context.scene.frame_current
        return {'FINISHED'}


class trim_right (bpy.types.Operator):
    bl_idname = "sequencer.trimtools_trim_right"
    bl_label = "Trim Right"
    bl_description = "Set the selected clip's ending frame to current frame"

    def invoke (self, context, event):
        for selected_sequence in bpy.context.selected_sequences:
            selected_sequence.frame_final_end = bpy.context.scene.frame_current
        return {'FINISHED'}


class snap_end (bpy.types.Operator):
    bl_idname = "sequencer.trimtools_snap_end"
    bl_label = "Snap End"
    bl_description = "Snap the Clip to the current frame with it´s end"

    def invoke (self, context, event):
        for selected_sequence in bpy.context.selected_sequences:
            selected_sequence.frame_start = bpy.context.scene.frame_current - selected_sequence.frame_offset_start - selected_sequence.frame_final_duration
        return {'FINISHED'}

def define_hotkeys():
    keymaps = bpy.context.window_manager.keyconfigs.addon.keymaps
    # keymap_sequencer = keymaps['Sequencer']
    keymap_sequencer = keymaps.new('Sequencer')
    keys_sequencer = keymap_sequencer.keymap_items
    # keymap_filebrowser = keymaps['File Browser Main']
    keymap_filebrowser = keymaps.new('File Browser Main')
    keys_filebrowser = keymap_filebrowser.keymap_items


    # Edit Range
    keys_filebrowser.new('file.moviemanager_edit_range',value='DOUBLE_CLICK',
               type='LEFTMOUSE',ctrl=False,alt=False,shift=False,oskey=False)
    keys_sequencer.new('sequencer.moviemanager_switch_back_to_timeline',value='PRESS',
               type='R',ctrl=False,alt=False,shift=True,oskey=False)
    keys_sequencer.new('sequencer.moviemanager_insert_strip_masterscene',value='PRESS',
               type='I',ctrl=False,alt=False,shift=False,oskey=False)

    # trimming
    keys_sequencer.new('sequencer.trimtools_trim_left',value='PRESS',
               type='Q',ctrl=False,alt=False,shift=True,oskey=False)
    keys_sequencer.new('sequencer.trimtools_trim_right',value='PRESS',
               type='W',ctrl=False,alt=False,shift=True,oskey=False)
    keys_sequencer.new('sequencer.trimtools_snap_end',value='PRESS',
               type='E',ctrl=False,alt=False,shift=True,oskey=False)
    keys_sequencer.new('sequencer.trimtools_select_current',value='PRESS',
               type='C',ctrl=False,alt=False,shift=True,oskey=False)

def register():
    bpy.utils.register_class( Edit_Range_Operator )
    bpy.utils.register_class( Proxy_Operator )
    bpy.utils.register_class( Set_Timeline )
    bpy.utils.register_class( Insert_Strip_Masterscene )
    bpy.utils.register_class( Switch_back_to_Timeline_Operator )
    bpy.utils.register_class( Insert_Strip )
    bpy.utils.register_class( MovieManagerPanel )
    bpy.utils.register_class( Unmeta )
    bpy.utils.register_class( Hide_Operator)
    bpy.utils.register_class(MovieManagerPanelBrowser)
    bpy.utils.register_class(CleanupScenes)
### TrimTools ###
    bpy.utils.register_class( TrimToolsPanel )
    bpy.utils.register_class( select_current )
    bpy.utils.register_class( cut_current )
    bpy.utils.register_class( trim_left )
    bpy.utils.register_class( trim_right )
    bpy.utils.register_class( snap_end )

    # define_hotkeys()

def unregister():
    bpy.utils.unregister_class( Edit_Range_Operator )
    bpy.utils.unregister_class( Proxy_Operator )
    bpy.utils.unregister_class( Set_Timeline )
    bpy.utils.unregister_class( Switch_back_to_Timeline_Operator)
    bpy.utils.unregister_class( Insert_Strip_Masterscene )
    bpy.utils.unregister_class( Insert_Strip )
    bpy.utils.unregister_class( MovieManagerPanel )
    bpy.utils.unregister_class( Unmeta )
    bpy.utils.unregister_class( Hide_Operator)
    bpy.utils.unregister_class(MovieManagerPanelBrowser)
    bpy.utils.unregister_class(CleanupScenes)
### TrimTools ###
    bpy.utils.unregister_class( TrimToolsPanel )
    bpy.utils.unregister_class( select_current )
    bpy.utils.unregister_class( cut_current )
    bpy.utils.unregister_class( trim_left )
    bpy.utils.unregister_class( trim_right )
    bpy.utils.unregister_class( snap_end )


if __name__ == "__main__":
    register()







