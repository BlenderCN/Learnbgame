#import pose
import statistics
import pose

##########
#CONFIG
##########
OPENSMILE_CONFIG_FILE   = "config/ComParE_2016_custom.conf"
#OPENSMILE_CONFIG_FILE  = "config/gemaps/eGeMAPSv01a.conf"
OPENPOSE_RENDER_VIDEO   = 1

#scores below this threshold will be 
#ignored when selecing the target person
SCORE_THRESHOLD         = 0.1

#defines window size and step:
#-to compute a pose value
POSE_WINDOW_SIZE_MS     = 300
POSE_WINDOW_STEP_MS     = 300
#-to compute the audio features
#NOTE:looks like opensmile works in increments of 300 ms
AUDIO_WINDOW_SIZE_MS    = 300
AUDIO_WINDOW_STEP_MS    = 300

##################
#WINDOW VALUES
##################
def computeAngularVelocity(lastPartA, lastPartB, partA, partB):
    lastVector = lastPartB.pos - lastPartA.pos
    currVector = partB.pos - partA.pos
    #if we get a zero vector, we can't compute angular velocity
    if not lastVector.isZero() and not currVector.isZero():
        return lastVector.CwAngleWith(currVector)
    else:
        return 0

def headAngularVelocity(keypoints):
    windowSum = 0
    lastNeck = keypoints[0].pose.getPart(pose.BodyPartType.NECK)
    lastNose = keypoints[0].pose.getPart(pose.BodyPartType.NOSE)
    for keypoint in keypoints:
        neck = keypoint.pose.getPart(pose.BodyPartType.NECK)
        nose = keypoint.pose.getPart(pose.BodyPartType.NOSE)
        windowSum += computeAngularVelocity(lastNeck, lastNose, neck, nose)
        lastNeck = neck
        lastNose = nose

    #value for this window (mean of visited frames)
    windowValue = windowSum/float(len(keypoints))
    return windowValue


def handsDistance(keypoints):
    windowSum = 0
    for keypoint in keypoints:
        right = keypoint.pose.getPart(pose.BodyPartType.RWRIST)
        left = keypoint.pose.getPart(pose.BodyPartType.LWRIST)
        v = right.pos - left.pos
        windowSum += v.getLength()

    #value for this window (mean of visited frames)
    windowValue = windowSum/float(len(keypoints))
    return windowValue

def neckNoseDistance(keypoints):
    windowSum = 0
    for keypoint in keypoints:
        neck = keypoint.pose.getPart(pose.BodyPartType.NECK)
        nose = keypoint.pose.getPart(pose.BodyPartType.NOSE)
        v = neck.pos - nose.pos
        windowSum += v.getLength()

    #value for this window (mean of visited frames)
    windowValue = windowSum/float(len(keypoints))
    return windowValue


#valueName:function(keypoints->value)
WINDOW_VALUES = {
    'headAngularVelocity':headAngularVelocity,
    'handsDistance': handsDistance,
    'neckNoseDistance': neckNoseDistance,
}

#funcName:function(window_values->value)
FUNCTIONALS = {
    'min':min,
    'max':max,
    'mean':statistics.mean,
    'median':statistics.median,
    'stdev':statistics.stdev,
}

#LABEL CLASSES (boolean functions, index is class number)
#w_val is window values (valueName:value)
#f_val is functional values (valueName_func:value)
#class 0 is reserved on GRT
"""
Syntax of label group:
{
    'group_name': '<group-name>',
    'labels':{
        '<label_name>':{
            'number': <class number>,
            'eval': <lambda function>
        }
    }
}
"""
LABEL_GROUPS = [
    {
        'group_name': 'HandSeparation',
        'label_names':[
            'hands_separated',
        ],
        'label_evals':[
                #hand_separated
                lambda w_val, f_val: w_val['handsDistance'] >
                     f_val['handsDistance_mean'],
        ]
    },
    {
        'group_name': 'Head',
        'label_names':[
            'turning_head_left',
            'turning_head_right',
            'reading'
        ],
        'label_evals':[
                #turning_head_left
                lambda w_val, f_val: w_val['headAngularVelocity'] > f_val['headAngularVelocity_stdev'],
                #turning_head_right
                lambda w_val, f_val: w_val['headAngularVelocity'] < -f_val['headAngularVelocity_stdev'], 
                #reading
                lambda w_val, f_val: w_val['neckNoseDistance'] < f_val['neckNoseDistance_mean'] 
        ]
    }
]
##########
#PATHS
##########
VERSION                 = 'Default'
#Path to src folder from the blender addons folder
ADDON_PATH              = "/speech2anim"
#Default path for training videos folder
TRAINING_VIDEOS_FOLDER  = "../TrainingVideos"
MODEL_OUTPUT            = "./best_model.grt"
#INPUT_VIDEOS_FOLDER    = "InputVideos"

OPENPOSE_ROOT           = "../lib/OpenPose"
OPENPOSE_OUTPUT         = "../output/openpose"

OPENSMILE_ROOT          = "../lib/opensmile"
OPENSMILE_OUTPUT        = "../output/opensmile"

#info and data for each video
TEMPDATA_OUTPUT         = "../output/tempdata"
TEMP_AUDIO              = "../tempAudioFiles"
DATA_OUTPUT             = "../output/data"

FFMPEG_ROOT             = "../lib/ffmpeg"

MODEL_MANAGER           = "./model_manager/TrainingBeta.exe"
FRAME_INDEX_COLNAME     = "frameIndex"
LABEL_COLNAME           = "Label"