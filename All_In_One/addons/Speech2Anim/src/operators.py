import os
import bpy
import sys
import importlib

import pdb

import DataManager
import BlenderManager
import wops
from csvfile import CSVFile
import config
import animation_config
#from config import ADDON_PATH, VERSION

def reloadConfig(context):
    p = bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH+'/src/'
    if context.scene.speech2anim_data.config_type == 'DEFAULT':
        wops.copy(p+'default_config.py', p+'config.py')
    else:
        wops.copy(context.scene.speech2anim_data.external_config_path, p+'config.py')
    importlib.reload(config)
    print("Using config version: ", config.VERSION)

def reloadAnimationConfig(context):
    p = bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH+'/src/'
    if context.scene.speech2anim_data.animation_config_type == 'DEFAULT':
        wops.copy(p+'default_animation_config.py', p+'animation_config.py')
    else:
        wops.copy(context.scene.speech2anim_data.external_animation_config_path, p+'animation_config.py')
    importlib.reload(animation_config)
    print("Using animation config version: ", animation_config.VERSION)

class TrainModel(bpy.types.Operator):
    """Trains the model using the training videos"""
    bl_idname = "s2a.train_model"
    bl_label = "Train"
 
    @classmethod
    def poll(cls, context):
        data = context.scene.speech2anim_data
        return (data.training_model_path != '' and data.training_videos_path != '')
 
    def execute(self, context):        
        self.report({'INFO'}, "Training model %s..." % context.scene.speech2anim_data.training_videos_path)
        os.chdir(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH+'/src')
        reloadConfig(context)
        #Clean previous output
        #pdb.set_trace()
        wops.rmdir(config.TEMPDATA_OUTPUT[3:], wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH))
        wops.mkdir(config.TEMPDATA_OUTPUT[3:], wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH))
        
        d = context.scene.speech2anim_data
        DataManager.Train(d.training_videos_path, d.training_model_path)

        paths = DataManager.getTrainingVideoPaths(d.training_videos_path)
        #TODO: refactor
        #for every video in the training folder
        for path in paths:
            #get the name
            name = path.split('/')[-1:][0].split('.')[0]
            exists = False
            #if we don't have it in the list, add it
            for p in d.training_videos_list:
                if p.name == name:
                    exists = True

            if not exists:
                item = d.training_videos_list.add()
                item.path = path
                item.name = name

        for i, p in enumerate(d.training_videos_list):
            exists = False
            for path in paths:
                name = path.split('/')[-1:][0].split('.')[0]
                if p.name == name:
                    exists = True
            if not exists:
                d.training_videos_list.remove(i)

        return {'FINISHED'}

class TrainModelMods(bpy.types.Operator):
    """Trains the model using the training videos and modifications"""
    bl_idname = "s2a.train_model_mods"
    bl_label = "Train modifications"
    @classmethod
    def poll(cls, context):
        data = context.scene.speech2anim_data
        return (data.training_model_path != '' and data.training_videos_path != '')

    def execute(self, context):
        os.chdir(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH+'/src')
        wops.rmdir(config.DATA_OUTPUT[3:], wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH))
        wops.mkdir(config.DATA_OUTPUT[3:], wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH))
        d = context.scene.speech2anim_data
        DataManager.GenerateFinalTrainingFile(d.training_model_path)
        DataManager.DoTrain()

        return {'FINISHED'}

class AnimateWithModel(bpy.types.Operator):
    """Animates the selected armature using the specified model and input file"""
    bl_idname = "s2a.animate"
    bl_label = "Animate Selected Armature"
 
    @classmethod
    def poll(cls, context):
        data = context.scene.speech2anim_data
        armature_selected = context.object is not None and context.object.type == 'ARMATURE'
        model_and_input = data.animate_model_path != '' and data.input_file != ''
        return (armature_selected and model_and_input)
 
    def execute(self, context):        
        self.report({'INFO'}, "Animating armature %s..." % context.scene.speech2anim_data.training_videos_path)
        os.chdir(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH+'/src')
        reloadAnimationConfig(context)
        d = context.scene.speech2anim_data
        result_path = DataManager.Predict(d.animate_model_path, d.input_file)
        data = CSVFile()
        data.from_file(result_path)
        data.tidy()
        data = data.to_dict()
        data = BlenderManager.fillFrameIndexes(data)
        armature = context.object
        BlenderManager.plotData(armature, data)
        BlenderManager.animate(armature, data)
        #load audio
        context.scene.sequence_editor_clear()
        #TODO:refactor, promote to function
        for area in bpy.context.screen.areas:
            if area.type == 'SEQUENCE_EDITOR':
                space_data = area.spaces.active
                override = {
                    'area':area, 
                    'screen':context.screen, 
                    'region':context.region,
                    'window':context.window,
                    'scene':context.scene,
                    'blend_data':context.blend_data
                }
                bpy.ops.sequencer.sound_strip_add(
                    override,
                    filepath=d.input_file,
                    frame_start=0)
        
        return {'FINISHED'}

class CreateConfigFile(bpy.types.Operator):
    """
    Creates a configuration file
    """
    bl_idname = "s2a.create_config"
    bl_label = "Create"
    bl_description = "Creates a new configuration file in the specified path"

    @classmethod
    def poll(cls, context):
        return context.scene.speech2anim_data.external_config_path != ''

    def execute(self, context):
        config_name = context.scene.speech2anim_data.external_config_path
        addon_path = wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH)

        wops.copy(addon_path+'/src/default_config.py', config_name)
        bpy.ops.s2a.open_file(path=config_name)
        return {'FINISHED'}

class CreateAnimationConfigFile(bpy.types.Operator):
    """
    Creates an animation configuration file
    """
    bl_idname = "s2a.create_animation_config"
    bl_label = "Create"
    bl_description = "Creates a new animation configuration file in the specified path"

    @classmethod
    def poll(cls, context):
        return context.scene.speech2anim_data.external_animation_config_path != ''

    def execute(self, context):
        config_name = context.scene.speech2anim_data.external_animation_config_path
        addon_path = wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH)

        wops.copy(addon_path+'/src/default_animation_config.py', config_name)
        bpy.ops.s2a.open_file(path=config_name)
        return {'FINISHED'}

class OpenTrainingLog(bpy.types.Operator):
    """
    Creates an animation configuration file
    """
    bl_idname = "s2a.open_training_log"
    bl_label = "Training log"
    bl_description = "Opens the latest training log in the text editor"

    @classmethod
    def poll(cls, context):
        addon_path = wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH)
        return os.path.isfile(addon_path+'/src/training.log')

    def execute(self, context):
        addon_path = wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH)
        bpy.ops.s2a.open_file(path=addon_path+'/src/training.log')
        return {'FINISHED'}

class OpenFile(bpy.types.Operator):
    bl_idname = "s2a.open_file"
    bl_label = "Open File"
    bl_description = "Load the file into the text editor"
    bl_options = {"REGISTER"}

    path = bpy.props.StringProperty(name = "Path", default = "")

    def execute(self, context):
        if not os.path.isfile(self.path):
            self.report({'ERROR'}, "The file doesn't exist")
            return {'CANCELLED'}

        space_data = None
        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                space_data = area.spaces.active
                break
            
        if space_data is None:
            self.report({'WARNING'}, "Please, open a text editor area to open the file")
            return {'CANCELLED'}

        text = None
        for text_block in bpy.data.texts:
            if text_block.filepath == self.path:
                text = text_block
                break
        if not text:
            text = bpy.data.texts.load(self.path, internal = False)

        space_data.text = text
        return {'FINISHED'}

class ResetStateFiles(bpy.types.Operator):
    """
    Clears all generated files
    """
    bl_idname = "s2a.reset_state"
    bl_label = "State"
    bl_description = "Removes temporary files and settings"

    def execute(self, context):
        #TODO: use constants
        context.scene.sequence_editor_clear()

        #remove linked files
        for i, item in enumerate(context.scene.speech2anim_data.training_videos_list):
            BlenderManager.remove_link(bpy.data.sounds, item.name+'.wav')
            BlenderManager.remove_link(bpy.data.movieclips, item.name+'.avi')

        addon_path = wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH)
        #wops.rmdir('tempAudioFiles', addon_path)
        context.scene.speech2anim_data.initialized = False
        context.scene.speech2anim_data.training_videos_path = ""
        context.scene.speech2anim_data.training_model_path = ""
        context.scene.speech2anim_data.animate_model_path = ""
        context.scene.speech2anim_data.input_file = ""
        context.scene.speech2anim_data.config_type = 'DEFAULT'
        context.scene.speech2anim_data.animation_config_type = 'DEFAULT'
        context.scene.speech2anim_data.external_config_path = ""
        context.scene.speech2anim_data.external_animation_config_path = ""
        context.scene.speech2anim_data.selected_training_video_index = 0
        context.scene.speech2anim_data.training_videos_list.clear()
        wops.rmdir('output', addon_path)
        wops.mkdir('output', addon_path)
        wops.rmdir('lib/openpose/TrainingVideos', addon_path)
        wops.rmdir('src/models', addon_path)
        wops.delete(addon_path+'/src/training.log')

        return {'FINISHED'}

class SaveLabelModifications(bpy.types.Operator):
    """
    Generates the final training file with the modifications
    to the labels of the current video
    """
    bl_idname = "s2a.save_label_modifications"
    bl_label = ""
    bl_description = "Saves label modifications"

    def execute(self, context):
        if not context.object.tempUserData:
            self.report({'ERROR'}, "There's no loaded data")
            return {'CANCELLED'}
        scn = context.scene
        idx = scn.speech2anim_data.selected_training_video_index
        addon_path = wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH)
        try:
            item = scn.speech2anim_data.training_videos_list[idx]
        except IndexError:
            return {'CANCELLED'}

        training_file = CSVFile()
        training_file.from_file(addon_path+'/output/tempdata/'+item.name+'/training_data.csv')
        training_file = training_file.to_dict()
        training_info = CSVFile()
        training_info.from_file(addon_path+'/output/tempdata/'+item.name+'/training_info.csv')
        training_info_dict = training_info.to_dict()
        for label_group in config.LABEL_GROUPS:
            group_name = label_group['group_name']
            #print(group_name)
            new_group_labels = [0] * len(training_file[group_name])
            for i, label_name in enumerate(label_group['label_names']):
                #print(label_name, i)
                for j, frame in enumerate(training_info_dict[config.FRAME_INDEX_COLNAME]):
                    context.scene.frame_set(int(frame))
                    value = int(context.object.tempUserData[label_name])
                    #print(frame, value, j)
                    training_info_dict[label_name][j] = value
                    if value:
                        #print("add to training","row:", j,"label:", i)
                        new_group_labels[j] = i+1


            training_file[group_name] = new_group_labels

        training_info.from_dict(training_info_dict)
        training_info.saveAs(addon_path+'/output/tempdata/'+item.name+'/training_info')
        new_training_file = CSVFile()
        new_training_file.from_dict(training_file)    
        new_training_file.saveAs(addon_path+'/output/tempdata/'+item.name+'/training_data')

        return {'FINISHED'}

class ClearAllGeneratedFiles(bpy.types.Operator):
    """
    Clears all generated files
    """
    bl_idname = "s2a.clear_training_generated_files"
    bl_label = "Temporal"
    bl_description = "Removes temporal files generated in the process"

    def execute(self, context):
        #TODO: use constants
        addon_path = wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH)
        wops.rmdir('lib/openpose/TrainingVideos', addon_path)
        wops.rmdir('src/models', addon_path)
        #wops.rmdir('tempAudioFiles', addon_path)

        return {'FINISHED'}

class ClearKeyframes(bpy.types.Operator):
    """
    Clears all the animation data (keyframes, nla_tracks)
    """
    bl_idname = "s2a.clear_animation"
    bl_label = "Animation"
    bl_description = "Removes the animation data of the selected armature"

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'

    def execute(self, context):
        context.object.animation_data_clear()

        return {'FINISHED'}


############
# list
############

class TrainingVideosListActions(bpy.types.Operator):
    bl_idname = "s2a.training_videos_list_actions"
    bl_label = "Training videos list"

    action = bpy.props.EnumProperty(
        items=(
            ('CLEAR_POSE', "Clear Pose", "Clear pose data (use if pose window properties changed)"),
            ('CLEAR_AUDIO', "Clear Audio", "Clear audio data (use if opensmile window properties or config file changed)"),
            ('SEE_INFO', "See training info", "Load the pose detection video and the features information")
        )
    )

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.speech2anim_data.selected_training_video_index
        addon_path = wops.clear(bpy.utils.user_resource("SCRIPTS", "addons")+config.ADDON_PATH)
        try:
            item = scn.speech2anim_data.training_videos_list[idx]
        except IndexError:
            pass

        else:
            if self.action == 'CLEAR_POSE':
                filename = item.name+'.avi'
                BlenderManager.erase_sequence(filename)
                wops.delete(addon_path+'/output/openpose/renders/'+filename)

                wops.rmdir('output/openpose/'+item.name, addon_path)
                self.report({'INFO'}, 'Pose cleared for video {}'.format(item.name))

            elif self.action == 'CLEAR_AUDIO':
                filename = item.name+'.wav'
                #BlenderManager.erase_sequence(filename)
                #wops.delete(addon_path+'/tempAudioFiles/'+filename)
                
                wops.rmdir('output/opensmile/'+item.name, addon_path)
                self.report({'INFO'}, 'Audio cleared for video {}'.format(item.name))

            elif self.action == 'SEE_INFO':
                if not context.object.type == 'ARMATURE':
                    self.report({'ERROR'}, 'Please, select an armature')
                    return {"CANCELLED"}

                data = CSVFile()
                data.from_file(addon_path+'/output/tempdata/'+item.name+'/training_info.csv')
                data = data.to_dict()
                data_funcs = CSVFile()
                data_funcs.from_file(addon_path+'/output/tempdata/'+item.name+'/training_info_funcs.csv')
                data_funcs = data_funcs.to_dict()
                all_data = {**data_funcs, **data}
                BlenderManager.plotData(context.object, all_data)
                #load video and audio
                context.scene.sequence_editor_clear()
                space_data=None
                #TODO:refactor, promote to function
                for area in bpy.context.screen.areas:
                    if area.type == 'SEQUENCE_EDITOR':
                        space_data = area.spaces.active
                        override = {
                            'area':area, 
                            'screen':context.screen, 
                            'region':context.region,
                            'window':context.window,
                            'scene':context.scene,
                            'blend_data':context.blend_data
                        }
                        if os.path.isfile(addon_path+'/output/openpose/renders/'+item.name+'.avi'):
                            bpy.ops.sequencer.movie_strip_add(
                                override,
                                filepath=addon_path+'/output/openpose/renders/'+item.name+'.avi',
                                frame_start=0)
                        else:
                            print("Can't find pose video:", addon_path+'/output/openpose/renders/'+item.name+'.avi')
                        if os.path.isfile(addon_path+'/tempAudioFiles/'+item.name+'.wav'):
                            bpy.ops.sequencer.sound_strip_add(
                                override,
                                filepath=addon_path+'/tempAudioFiles/'+item.name+'.wav',
                                frame_start=0)
                        else:
                            print("Can't find audio file:", addon_path+'/tempAudioFiles/'+item.name+'.wav')
                self.report({'INFO'}, 'Seeing info for video {}'.format(item.name))

        return {"FINISHED"}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)