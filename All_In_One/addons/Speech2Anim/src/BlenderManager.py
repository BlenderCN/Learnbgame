import bpy
import math
import random
import animation_config

import pdb
#from config import FRAME_INDEX_COLNAME, AUDIO_WINDOW_STEP_MS
import config
from csvfile import CSVFile

def fillFrameIndexes(data):
    #Frame list based on the audio window length
    if config.FRAME_INDEX_COLNAME not in list(data):
        firstKey = list(data)[0]
        frameList = []
        frame_size = 1/bpy.context.scene.render.fps
        frames_per_window = (config.AUDIO_WINDOW_STEP_MS/1000.0)/frame_size
        for i in range(0, len(data[firstKey])):
            frameList.append(round(frames_per_window*i))

        data[config.FRAME_INDEX_COLNAME] = frameList

    return data


def plotData(obj, data):
    """
    Plots the data by storing it in an object as keyframes

    Data is a dict of arrays, every element with 
    index i of the array represents the value of 
    the 'key' for the frame i
    If key FRAME_INDEX_COLNAME is not in data,
    then frame is assumed from AUDIO_WINDOW_STEP_MS
    """
    if len(list(data)) == 0:
        return

    #Class which will hold the loaded data temporarily
    class TempUserData(bpy.types.PropertyGroup):
        pass

    for field in list(data):
        if field is not config.FRAME_INDEX_COLNAME:
            setattr(TempUserData, field, bpy.props.FloatProperty())

    bpy.utils.register_class(TempUserData)
    bpy.types.Object.tempUserData = bpy.props.PointerProperty(type=TempUserData)
         
    ## Load data into selected object
    for fieldname in list(data):
        if config.FRAME_INDEX_COLNAME not in fieldname:
            for i, value in enumerate(data[fieldname]):
                try:
                    frame = int(data[config.FRAME_INDEX_COLNAME][i])
                    #print(i, ", ", value, ", ", frame)
                    setattr(obj.tempUserData, fieldname, float(value))
                except:
                    pdb.set_trace()
                obj.keyframe_insert(data_path="tempUserData."+fieldname, frame=frame)

def getLabels(data, frame):
    """
    data is {FRAME_INDEX_COLNAME: [...], Label: [...]
    returns the label corresponding to the frame
    """
    result = {}
    for i in range(0, len(data[config.FRAME_INDEX_COLNAME])-1):
        f1 = data[config.FRAME_INDEX_COLNAME][i]
        f2 = data[config.FRAME_INDEX_COLNAME][i+1]
        if frame >= f1 and frame < f2:
            for key, value in data.items():
                if key == config.FRAME_INDEX_COLNAME:
                    continue
                else:
                    result[key] = value[i]

            return result

    for key, value in data.items():
        if key == config.FRAME_INDEX_COLNAME:
            continue
        else:
            result[key] = value[-1]
            
    return result


def animate(armature, data):
    """
    Animates the armature using the predicted labels
    """
    sce = bpy.context.scene
    lastFrame = int(data[config.FRAME_INDEX_COLNAME][-1])
    sce.frame_end = lastFrame
    
    groups_per_frame = []
    #for every frame 
    for f in range(0, lastFrame):
        #TODO: get multilabels
        groups_per_frame.append(getLabels(data, f))

    for a in animation_config.ANIMATIONS:
        a(groups_per_frame, armature)

def erase_sequence(name):
    seqs = bpy.context.scene.sequence_editor.sequences
    if seqs[name]:
        seqs.remove(seqs[name])

def remove_link(data_obj, filename):
    """
    removes links and data references to file
    data_obj is a data collection (bpy.data.something)
    filename is a string contained in the filepath of the
        file to be removed
    """
    for obj in data_obj: 
        #print("filename:", filename, "filepath", obj.filepath)
        if filename in obj.filepath:
            data_obj.remove(obj, do_unlink=True)

def insertAction(action, start_frame, end_frame, action_frame_start=0, action_frame_end=0, scale=1, smooth_frames=20):
    """
    Pushes down an action to the selected armature
    """
    area = bpy.context.area
    old_area = area.type
    area.type='NLA_EDITOR'
    
    for track in bpy.context.object.animation_data.nla_tracks:
        track.select = False
    ntracks = len(bpy.context.object.animation_data.nla_tracks)
    if ntracks:
        bpy.context.object.animation_data.nla_tracks[-1].select=True
        
    bpy.ops.nla.tracks_add(above_selected=True)
    if ntracks:
        bpy.context.object.animation_data.nla_tracks[-2].select=False
        
    bpy.context.object.animation_data.nla_tracks[-1].select=True
    bpy.ops.nla.actionclip_add(action=action)
    added_strip = bpy.context.object.animation_data.nla_tracks[-1].strips[0]
    added_strip.frame_start = start_frame
    added_strip.frame_end = end_frame
    added_strip.blend_in=smooth_frames
    added_strip.blend_out=smooth_frames
    added_strip.action_frame_start = action_frame_start
    added_strip.action_frame_end = end_frame - start_frame
    #if action_frame_end:
    #    added_strip.action_frame_end = action_frame_end
    
    added_strip.scale = scale
    area.type=old_area

def clearActions():
    """
    Removes all nla tracks from the selected armature
    """
    area = bpy.context.area
    old_area = area.type
    area.type='NLA_EDITOR'
    tracks = bpy.context.object.animation_data.nla_tracks
    for track in tracks:
        tracks.remove(track)
    area.type=old_area
    

    
def getLabelIntervals(group_name, label, frames, threshold=1):
    result = []
    found = False
    not_equal_count = 0
    start = -1
    for frame, groups in enumerate(frames):
        if not found and groups[group_name] == label:
            found = True
            not_equal_count = threshold
            start = frame
        elif found and groups[group_name] == label:
            not_equal_count = threshold+1
        elif found and not groups[group_name] == label:
            not_equal_count = not_equal_count-1
            if not not_equal_count:
                found = False
                #append range
                result.append((start, frame))
                start = -1

    if start != -1:
        result.append((start, len(frames)-1))

    return result
            

