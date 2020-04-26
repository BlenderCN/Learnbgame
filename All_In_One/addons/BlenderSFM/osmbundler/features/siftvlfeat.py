import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import subprocess, gzip, logging

from sift import Sift

className = "VlfeatSift"
class VlfeatSift(Sift):
    
    win32Executable = "vlfeat/bin/w32/sift.exe"
    linuxExecutable = "vlfeat/bin/glx/sift"

    def __init__(self, distrDir):
        Sift.__init__(self, distrDir)

    def extract(self, photo, photoInfo):
        print("Extracting features from photo %s" % photo)
        subprocess.call([self.executable, "%s.jpg.pgm" % photo, "-o", "%s.key" % photo])
        # perform conversion to David Lowe's format
        vlfeatTextFile = open("%s.key" % photo, "r")
        loweGzipFile = gzip.open("%s.key.gz" % photo, "wb")
        featureStrings = vlfeatTextFile.readlines()
        numFeatures = len(featureStrings)
        # write header
        loweGzipFile.write(bytes("%s 128\n" % numFeatures, 'UTF-8'))
        for featureString in featureStrings:
            features = featureString.split()
            # swap features[0] and features[1]
            tmp = features[0]
            features[0] = features[1]
            features[1] = tmp
            i1 = 0
            for i2 in (4,24,44,64,84,104,124,132):
                loweGzipFile.write(bytes("%s\n" % " ".join(features[i1:i2]), 'UTF-8'))
                i1 = i2
        loweGzipFile.close()
        vlfeatTextFile.close()
        # remove original SIFT file
        os.remove("%s.key" % photo)
        logging.info("\tFound %s features" % numFeatures)