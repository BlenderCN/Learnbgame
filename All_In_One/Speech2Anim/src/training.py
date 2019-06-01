import json, glob
import pose
import math
import unittest
import pdb


def labelWindows(computed_windows, computed_functionals, label_groups):
    """ 
    Sets labels on windows 
    computed_windows is an array of dicts valName:val
    computed_functionals is a dict valName_func:val
    label_groups is an array of label groups as defined
        in the default config file
    """
    labels = []
    #for every window w
    for cwindow in computed_windows:
        window_labels = []
        
        #for every group g
        for g in label_groups:
            isNull = True

            #evaluate labels from g
            for i, f in enumerate(g['label_evals']):
                if f(cwindow, computed_functionals):
                    isNull = False
                    #+1 because 0 is the null class
                    window_labels.append(i+1)
                    #if we place a label, exit for-loop
                    break
            
            #if no label has been set, g
            #has the null label for w
            if isNull:
                window_labels.append(0)
                
        labels.append(window_labels)

    return labels

def computeWindows(keypoints, wvalues, framerate, window_size, window_step):
    """ 
    Computes an array of windows. 
    result[i] is a dictionary of the form valueName:computedValue
    """
    #pdb.set_trace()
    #frame size in ms
    frame_size = 1/framerate*1000
    #window size in frames
    #frames_window_size = round(window_size/frame_size)
    frames_window_size = window_size/frame_size
    #displacement in frames
    displacement = math.ceil(frames_window_size/2)
    if frames_window_size % 2 != 0:
        displacement = displacement-1
    #step in frames
    step = math.ceil(window_step/frame_size)



    result = []
    #for each window
    #for i in range(0, len(keypoints)-1, frames_window_size):
    float_i = 0.0
    while float_i < len(keypoints):
        i = round(float_i)
        lowerBound = max(i-displacement, 0)
        #+1, range goes to higherBound-1
        higherBound = min(i+displacement+1, len(keypoints))
        #compute all values for this window
        values = {}
        for name, f in wvalues.items():
            values[name] = f(keypoints[lowerBound:higherBound])
        #append all computed values of this window to the result
        result.append(values)

        float_i += frames_window_size

    #print(len(keypoints),len(result), frame_size, frames_window_size, displacement, step)

    return result

def computeFunctionals(window_values, functionals):
    """
    Computes statistics about the window values
    returns a dict of the form valueName_func:value
    """
    result = {}
    wkeys = window_values[0].keys()

    for key in wkeys:
        l = []
        for wval in window_values:
            l.append(wval[key])

        for name, f in functionals.items():
            result[key+'_'+name] = f(l)

    return result



def getKeypoints(folder):
    """ Generates keypoints (frames with poses) from openpose output """
    keypointFiles = glob.glob(folder+"/*.json")
    keypoints = []
    for i, keypointFile in enumerate(keypointFiles):
        with open(keypointFile) as data:
            keypoint = json.load(data)
            
            personIndex = 0
            if len(keypoint["people"]) > 1:
                personIndex = pose.getBiggestPersonIndex(keypoint)

            p = pose.Pose()
            posekp = pose.PoseKeypoint(i, p)
            #if there's no person, use last keypoint data
            if personIndex in range(0, len(keypoint["people"])):
                p.fromData(keypoint["people"][personIndex])
                posekp = pose.PoseKeypoint(i, p)

            keypoints.append(posekp)

    return keypoints


class TestLabeling(unittest.TestCase):
    def test_basic(self):
        computed_windows = [
            {
                'val1': 1.0,
                'val2': 1.14
            },
            {
                'val1': 2.0,
                'val2': 2.14
            },
            {
                'val1': 3.0,
                'val2': 3.0
            },
        ]
        computed_functionals = {
            'val1_m': 0.5,
            'val2_m': 2.0
        }
        label_groups = [
            {
                'label_evals':[
                        lambda w_val, f_val: 
                            w_val['val1'] >= 2.0,
                        lambda w_val, f_val: 
                            w_val['val2'] < 2
                ]
            },
            {
                'label_evals':[
                        lambda w_val, f_val: 
                            w_val['val1'] ==  w_val['val2']
                ]
            }
        ]
        labels = labelWindows(computed_windows, computed_functionals, label_groups)
        result = [
            [2,0],
            [1,0],
            [1,1],
        ]
        self.assertEqual(labels, result)

if __name__ == '__main__':
    unittest.main()