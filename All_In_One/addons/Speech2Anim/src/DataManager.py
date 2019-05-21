#call other processes
import subprocess, os, sys
import pdb
#access filesystem
import glob
import math
import argparse

#windows functions
from wops import w2p, rmdir, mkdir, xcopy, move
#training data functions
import training
from csvfile import CSVFile
#constants and config
import config
import utils

def getTrainingVideoPaths(training_videos_folder=config.TRAINING_VIDEOS_FOLDER):
    paths = []
    for filename in glob.glob(training_videos_folder+'/*'):
        video_path = w2p(filename)
        print(video_path)
        paths.append(video_path)
    return paths


def Clean():
    """
    rmdir(OPENPOSE_OUTPUT)
    mkdir(OPENPOSE_OUTPUT)
    """
    #rmdir(config.OPENSMILE_OUTPUT)
    #mkdir(config.OPENSMILE_OUTPUT)

    #rmdir(config.TEMP_AUDIO)
    #mkdir(config.TEMP_AUDIO)

    rmdir(config.TEMPDATA_OUTPUT)
    mkdir(config.TEMPDATA_OUTPUT)

    rmdir(config.DATA_OUTPUT)
    mkdir(config.DATA_OUTPUT)
    mkdir(config.DATA_OUTPUT+'/training')
    mkdir(config.DATA_OUTPUT+'/prediction')

def ExtractPoses(training_videos_folder=config.TRAINING_VIDEOS_FOLDER):
    """
    Extracts pose information from 
    videos in training_videos_folder
    and stores it in OPENPOSE_OUTPUT
    """
    #Copy videos to openpose root project
    #mkdir(OPENPOSE_ROOT+'/TrainingVideos')
    xcopy(training_videos_folder, config.OPENPOSE_ROOT+'/TrainingVideos/')
    #weird bug, can't find models, copy them temporarily
    xcopy(config.OPENPOSE_ROOT+'/models', 'models/')
    #Extract poses
    for filename in glob.glob(config.OPENPOSE_ROOT+'/TrainingVideos/*'):
        pFilename = w2p(filename)
        sys.stdout.flush()
        videoName = pFilename.split('/')[-1:][0].split('.')[0]
        videoPath = "/".join(pFilename.split('/')[-2:])
        outputPath = config.OPENPOSE_OUTPUT + '/' + videoName

        if len(glob.glob(outputPath)) > 0:
            print("Skipping pose extraction for "+videoName+"...")
            continue
        
        print("Extracting pose for "+videoName+"...")

        #Create folder
        mkdir(outputPath, config.OPENPOSE_ROOT)
        flags = [
            '-video', videoPath, 
            '-write_keypoint_json', outputPath, 
            '-no_display'
        ]
        if config.OPENPOSE_RENDER_VIDEO:
            mkdir('../output/openpose/renders/')
            flags += ['-write_video', videoName+'.avi']
        #Extract poses
        subprocess.call([config.OPENPOSE_ROOT+'/bin/OpenPoseDemo.exe'] + flags,
            cwd=config.OPENPOSE_ROOT)
        #Move output
        if config.OPENPOSE_RENDER_VIDEO:
            move(config.OPENPOSE_ROOT+'/'+videoName+'.avi', config.OPENPOSE_OUTPUT+'/renders/'+videoName+'.avi')
        xcopy(config.OPENPOSE_ROOT+'/'+outputPath, outputPath+'/')
        rmdir(config.OPENPOSE_ROOT+'/'+outputPath)
    #Clean
    rmdir(config.OPENPOSE_ROOT+'/TrainingVideos/')
    rmdir('models')

def ExtractAudioFeaturesFolder(input_folder):
    """
    Extracts audio features from
    videos in input_folder
    and stores them in OPENSMILE_OUTPUT
    """
    if len(glob.glob(config.TEMP_AUDIO)) == 0:
        mkdir(config.TEMP_AUDIO)

    for filename in glob.glob(input_folder+'/*'):
        ExtractAudioFeatures(filename)

def ExtractAudioFeatures(filename):
    """
    Extracts audio features from
    """
    pFilename = w2p(filename)
    #If extension is different from .wav, we assume video
    isVideo = (pFilename.split('.')[-1] != 'wav')
    name = pFilename.split('/')[-1:][0].split('.')[0]
    #videoPath = "/".join(pFilename.split('/')[-2:])
    outputPath = config.OPENSMILE_OUTPUT + '/' + name
    
    if isVideo:
        print("Generating audio for "+name+"...")
        sys.stdout.flush()
        audioFile = config.TEMP_AUDIO + '/' + name+'.wav'
        subprocess.call([config.FFMPEG_ROOT + "/ffmpeg.exe", 
            '-i', pFilename, 
            '-ab', '160k', #bitrate 
            '-ac', '2', #channels
            '-ar', '44100', #sampling rate
            '-n',
            '-vn', audioFile])
    else:
        audioFile = pFilename
    
    if len(glob.glob(outputPath)) > 0:
        print("Skipping audio feature extraction for "+name+"...")
        return
    
    print("Extracting audio features for "+name+"...")
    sys.stdout.flush()

    #Create output folder for this file
    mkdir(outputPath)

    subprocess.call([config.OPENSMILE_ROOT+'/bin/Win32/SMILExtract_Release.exe', 
        '-C', config.OPENSMILE_ROOT+'/'+config.OPENSMILE_CONFIG_FILE,
        '-I', audioFile,
        '-wstep', "{0:.3f}".format(config.AUDIO_WINDOW_STEP_MS/1000),
        '-wsize', "{0:.3f}".format(config.AUDIO_WINDOW_SIZE_MS/1000),
        #TODO: LLD is smaller and faster, expose to config file
        #'-lldcsvoutput', outputPath+'/features.csv'])
        '-csvoutput', outputPath+'/features.csv'])

def GenerateIndividualTrainingData(training_videos_folder=config.TRAINING_VIDEOS_FOLDER):

    for filename in glob.glob(training_videos_folder+'/*'):
        video_path = w2p(filename)
        if not os.path.isfile(w2p(filename)):
            print("Skipping folder "+filename+"...")
            continue
        video_name = (video_path.split('/')[-1]).split('.')[0]
        output_folder = config.TEMPDATA_OUTPUT+'/'+video_name
        if len(glob.glob(output_folder+'/*')) > 0:
            print("Skipping training for "+video_name+"...")
            continue

        print("Generating training data for "+video_name+"...")
        mkdir(output_folder)
        #array of poses
        keypoints = training.getKeypoints(config.OPENPOSE_OUTPUT+'/'+video_name)

        #get current video framerate
        framerate = utils.get_frame_rate(video_path)

        #array of window values (dicts valueName:value)
        computedWindows = training.computeWindows(keypoints, config.WINDOW_VALUES, 
            framerate, config.POSE_WINDOW_SIZE_MS, config.POSE_WINDOW_STEP_MS)

        #dict with statistics about window values (valueName_func:value)
        computedFuncs = training.computeFunctionals(computedWindows, config.FUNCTIONALS)
        cfuncs_names = list(computedFuncs.keys())
        func_outputfile = CSVFile(['frameIndex'] + cfuncs_names)
        #frame index 0
        row = [0]
        for name in cfuncs_names:
            row.append(computedFuncs[name])
        func_outputfile.addRow(row)
        func_outputfile.saveAs(output_folder+'/training_info_funcs')

        #array of arrays of labels (labels per window) 
        #labels = {x | |x| = len(config.LABEL_GROUPS) ^ x_i = label of group i}
        labels = training.labelWindows(computedWindows, computedFuncs, config.LABEL_GROUPS)

        #create info output file
        window_values_names = list(computedWindows[0].keys())

        #array of label names by order of definition
        label_names = utils.get_label_names(config.LABEL_GROUPS)
        labels_outputfile = CSVFile(['frameIndex'] + window_values_names + label_names)
        #step in frame count (frames/window)
        frames_per_pose_window = (config.POSE_WINDOW_STEP_MS/1000)*framerate
        #for each window
        for i, w in enumerate(computedWindows):
            #frame index
            row = [round(i*frames_per_pose_window)]

            #add all computed values (from pose data)
            for name in window_values_names:
                row.append(w[name])

            #window_labels contains a label for each group
            window_labels = labels[i]
            #for every group
            for j, g in enumerate(config.LABEL_GROUPS):
                #get the label of that group
                label_of_g = window_labels[j]
                #0 is null class
                for k in range(1, len(g['label_names'])+1):
                    row.append( int(k == label_of_g) )

            labels_outputfile.addRow(row)

        labels_outputfile.saveAs(output_folder+'/training_info')

        #create training data
        audio_features = CSVFile()
        audio_features.from_file(config.OPENSMILE_OUTPUT+'/'+video_name+'/features.csv')

        label_col = []
        #output file (without frametime col)
        regression_training_data = CSVFile(audio_features.getHeader()[1:]+window_values_names)
        group_names = utils.get_group_names(config.LABEL_GROUPS)
        training_data = CSVFile(audio_features.getHeader()[1:]+group_names)
        for row in audio_features.getRows():
            #row[0] is the tick number
            #frame in which the tick is contained
            frame = math.floor(((int(row[0])*config.AUDIO_WINDOW_SIZE_MS)/1000)*framerate)
            #window in which the frame is contained
            window = min(math.floor(frame/frames_per_pose_window), len(computedWindows)-1)
            #add classification row
            training_data.addRow(row[1:]+labels[window])

            #create regression row (append pose features to audio features)
            row_regression = row[1:]
            for name in window_values_names:
                row_regression.append(computedWindows[window][name])
            regression_training_data.addRow(row_regression)

        training_data.saveAs(output_folder+'/training_data')
        regression_training_data.saveAs(output_folder+'/regression_training_data')

def GenerateFinalTrainingFile(model_output):
    ncols = 0
    nrows = 0
    final_file = ""
    ngroups = len(config.LABEL_GROUPS)
    ###export csv
    #"""
    first = glob.glob(config.TEMPDATA_OUTPUT+'/*/training_data.csv')[0]
    final_csv = CSVFile()
    temp = CSVFile()
    temp.from_file(first)
    final_csv.setHeader(temp.getHeader())
    #"""
    ###export csv---
    current_file = CSVFile()
    for filename in glob.glob(config.TEMPDATA_OUTPUT+'/*/training_data.csv'):
        current_file.from_file(filename)
        nrows += current_file.get_row_count()
        ncols = len(current_file.getHeader())
        for row in current_file.getRows():
            #ecsv
            final_csv.addRow(row)
            #ecsv--
            #last ngroups rows are labels, which are ints
            for v in row[:-ngroups]:
                floatval = "0 "
                try:
                    floatval = "{0:.10f}".format(float(v)) + " "
                except:
                    print("Warning: can't transform to float: ", v)

                final_file += floatval

            for group_label in row[-ngroups:]:
                final_file += group_label + ' '

            final_file += '\n'

    mkdir(config.DATA_OUTPUT+'/training')
    final_csv.saveAs(config.DATA_OUTPUT+"/training/final_training_data")
    with open(config.DATA_OUTPUT+"/training/final_training_data.txt", "w") as output:
        output.write("0\n 0 \n {} {} {}\n".format(ncols, nrows, ngroups))
        for name in utils.get_group_names(config.LABEL_GROUPS):
            output.write(name + " ")
        output.write(model_output+"\n")
        output.write(final_file)

def GenerateFinalRegressionTrainingFile():
    ncols = 0
    nrows = 0
    final_file = ""
    ###export csv
    first = glob.glob(config.TEMPDATA_OUTPUT+'/*/regression_training_data.csv')[0]
    final_csv = CSVFile()
    temp = CSVFile()
    temp.from_file(first)
    final_csv.setHeader(temp.getHeader())
    ###export csv---
    current_file = CSVFile()
    for filename in glob.glob(config.TEMPDATA_OUTPUT+'/*/regression_training_data.csv'):
        current_file.from_file(filename)
        nrows += current_file.get_row_count()
        ncols = len(current_file.getHeader())
        for row in current_file.getRows():
            #ecsv
            final_csv.addRow(row)
            #ecsv--
            for v in row:
                final_file += "{0:.10f}".format(float(v)) + " "
            
            final_file += "\n"


    final_csv.saveAs(config.DATA_OUTPUT+"/training/final_regression_training_data")
    with open(config.DATA_OUTPUT+"/training/final_regression_training_data.txt", "w") as output:
        outputDimensions = len(config.WINDOW_VALUES)
        inputDimensions = ncols - outputDimensions
        output.write("0 \n 1 \n {} {} {}\n".format(inputDimensions, outputDimensions, nrows))
        output.write(final_file)

def DoTrain():
    """
    Uses all the gathered information to generate a model
    """
    with open("training.log", "w") as log:
        with open(config.DATA_OUTPUT+"/training/final_training_data.txt") as training_data:
            subprocess.call([config.MODEL_MANAGER], stdin=training_data, stderr=log)
    """
    with open(DATA_OUTPUT+"/training/final_regression_training_data.txt") as regression_training_data:
        subprocess.call([MODEL_MANAGER], stdin=regression_training_data)
    """


def DoPredictFolder():
    """ 
    Uses the audio features of the input videos
    to generate predicted values
    """
    #For every video in the input folder
    for filename in glob.glob(config.INPUT_VIDEOS_FOLDER+'/*'):
        DoPredict(filename)

def DoPredict(input_model, filename):
    """
    Generates predicted labels file.
    returns path to the generated file
    """
    name = w2p(filename).split('/')[-1:][0].split('.')[0]
    temp_folder = config.TEMPDATA_OUTPUT+'/'+name
    mkdir(temp_folder)
    output_folder = config.DATA_OUTPUT+'/prediction/'+name
    mkdir(output_folder)
    # get opensmile data
    opensmile_data = CSVFile()
    opensmile_data.from_file(config.OPENSMILE_OUTPUT+'/'+name+'/features.csv')
    #create prediction input data
    #option 1 prediction
    result_file = '1\n'
    #-1 because first col is not feature
    result_file += str(len(opensmile_data.getHeader())-1)+'\n'
    result_file += str(opensmile_data.get_row_count())+'\n'
    result_file += input_model+'\n'
    for row in opensmile_data.getRows():
        features = row[2:]
        for v in features:
            floatval = "0 "
            try:
                floatval = "{0:.10f}".format(float(v)) + " "
            except:
                print("Warning: can't transform to float: ", v)
            result_file += floatval
        result_file += '\n'

    with open(temp_folder+'/prediction_data.txt', 'w') as output:
        output.write(result_file)
    
    #get prediction output
    
    with open(temp_folder+'/prediction_data.txt') as data:
        with open(output_folder+'/predicted_labels.csv', 'w') as output:
            subprocess.call([config.MODEL_MANAGER], stdin=data, stdout=output)
            return output_folder+'/predicted_labels.csv'
    


def Train(training_videos=config.TRAINING_VIDEOS_FOLDER, model_output=config.MODEL_OUTPUT):
    ExtractPoses(training_videos)
    ExtractAudioFeaturesFolder(training_videos)
    GenerateIndividualTrainingData(training_videos)
    GenerateFinalTrainingFile(model_output)
    #GenerateFinalRegressionTrainingFile()
    DoTrain()

def Predict(input_model=config.MODEL_OUTPUT,audioFile=""):
    ExtractAudioFeatures(audioFile)
    return DoPredict(input_model, audioFile)

def main():
    parser = argparse.ArgumentParser(description='Trains or predict models')
    parser.add_argument('-c', help='Clears cached output', action='store_true')
    parser.add_argument('-t', help='Train', action='store_true')
    parser.add_argument('-p', help='Predict', action='store_true')
    args = parser.parse_args()

    if args.c:
        Clean()

    if args.t:
        Train()
    
    if args.p:
        Predict()
    
    if not (args.c or args.t or args.p):
        print('Please choose an option')
        parser.print_help()


if __name__ == "__main__":
    main()
    #Train('C:/Users/gerar/Documents/trainingvideostest')