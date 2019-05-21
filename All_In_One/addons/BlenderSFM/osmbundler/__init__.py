import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import logging
import  tempfile, subprocess
import sqlite3
import csv

import matching
from matching import *
import features
from features import *

# a helper function to get list of photos from a directory
def getPhotosFromDirectory(photoDir):
    return [f for f in os.listdir(photoDir) if os.path.isfile(os.path.join(photoDir, f)) and os.path.splitext(f)[1].lower()==".jpg"]

distrPath = ""
camerasDatabase = ""
SCALE = 1.0
bundlerListFileName = "list.txt"


class OsmBundler():

    currentDir = ""

    workDir = ""
    
    # value of command line argument --photos=<..>
    photosArg = ""
    
    featureExtractor = None
    
    matchingEngine = None
    
    # list of photos with focal distances for bundler input
    bundlerListFile = None
    
    # list of files with extracted features
    featuresListFile = None
    
    # information about each processed photo is stored in the following dictionary
    # photo file name in self.workDir is used as the key in this dictionary
    photoDict = {}
    
    featureExtractionNeeded = True
    
    photoScalingFactor = 0
    bundlerOptions = (
    "--match_table matches.init.txt\n",
    "--output bundle.out\n",
    "--output_all bundle_\n",
    "--output_dir bundle\n",
    "--variable_focal_length\n",
    "--use_focal_estimate\n",
    "--constrain_focal\n",
    "--constrain_focal_weight 0.0001\n",
    "--estimate_distortion\n",
    "--run_bundle\n"
    )
# ==================================================================================================
    def __init__(self, pPluginDirectory, pImageDirectory, pWorkDirectory, pFeatureExtractor, pMaxPhotoDimension, pPhotoScalingFactor):

        self.distrPath = pPluginDirectory;
        self.camerasDatabase = self.distrPath + "\osmbundler\cameras\cameras.sqlite"

        # set parameters
        self.photosArg = pImageDirectory
        self.maxPhotoDimension = pMaxPhotoDimension
        self.photoScalingFactor = pPhotoScalingFactor
        self.matchingEngine = "bundler"
        self.featureExtractor = "siftvlfeat"

        # save current directory (i.e. from where RunBundler.py is called)
        self.currentDir = os.getcwd()
        # create a working directory
        self.workDir = pWorkDirectory
        print("Working directory created: "+self.workDir)
        
        if not (os.path.isdir(self.photosArg) or os.path.isfile(self.photosArg)):
            raise Exception("'%s' is neither directory nor a file name" % self.photosArg)
        
        # initialize mathing engine based on command line arguments
        self.initMatchingEngine()

        # initialize feature extractor based on command line arguments
        self.initFeatureExtractor()

# ==================================================================================================
    def openFiles(self):        
        # open list of photos with focal distances for bundler input
        self.bundlerListFile = open(os.path.join(self.workDir,bundlerListFileName), "w")
        self.featuresListFile = open(os.path.join(self.workDir,self.matchingEngine.featuresListFileName), "w")

# ==================================================================================================
    def closeFiles(self):
        if self.featuresListFile: self.featuresListFile.close()
        self.bundlerListFile.close()
           
    def _preparePhoto(self, photoInfo):

        photo = photoInfo['basename']
        photoDir = photoInfo['dirname']
        print("\nProcessing photo '%s':" % photo)
        inputFileName = os.path.join(photoDir, photo)
        photo = photo[:-4]
        outputFileName = os.path.join(self.workDir, photo)

        # get EXIF information and produce PGM output file
        pilbinOutput = subprocess.check_output(
            [self.distrPath + "\\software\\pilbin\\build\\exe.win32-3.3\\pilbin.exe", 
            inputFileName, 
            outputFileName]).decode("utf-8")
        exifData = pilbinOutput.split(",")
        exifMake = exifData[0]
        exifModel = exifData[1]
        exifFocalLength = float(exifData[2])
        exifImageWidth = float(exifData[3])
        exifImageHeight = float(exifData[4])

        self._calculateFocalDistance(photo, photoInfo, exifMake, exifModel, exifFocalLength, exifImageWidth, exifImageHeight)
        
        photoInfo['width'] = exifImageWidth
        photoInfo['height'] = exifImageHeight

        # put photoInfo to self.photoDict
        self.photoDict[photo] = photoInfo

        if self.featureExtractionNeeded:
            self.extractFeatures(photo)

    
    def _calculateFocalDistance(self, photo, photoInfo, exifMake, exifModel, exifFocalLength, exifImageWidth, exifImageHeight):
        hasFocal = False
        if exifMake and exifModel:
            # check if we have camera entry in the database
            ccdWidth = getCcdWidthFromDatabase(exifMake.strip(),exifModel.strip(), self.distrPath)
            print(ccdWidth)
            if ccdWidth:
                if exifFocalLength>0 and exifImageWidth>0 and exifImageHeight>0:
                    if exifImageWidth<exifImageHeight: exifImageWidth = exifImageHeight
                    focalPixels = exifImageWidth * (exifFocalLength / ccdWidth)
                    hasFocal = True
                    print("FOCAL LENGTH: ", exifFocalLength, ", CCD: ", ccdWidth)
                    self.bundlerListFile.write("%s.jpg 0 %s\n" % (photo,SCALE*focalPixels))
            else: print("\tEntry for the camera '%s', '%s' does not exist in the camera database" % (exif['Make'], exif['Model']))
        if not hasFocal:
            print("\tCan't estimate focal length in pixels for the photo '%s'" % os.path.join(photoInfo['dirname'],photoInfo['basename']))
            self.bundlerListFile.writelines("%s.jpg\n" % photo)


    def initMatchingEngine(self):
        try:
            matchingEngine = getattr(matching, self.matchingEngine)
            matchingEngineClass = getattr(matchingEngine, matchingEngine.className)
            self.matchingEngine = matchingEngineClass(os.path.join(self.distrPath, "software"))
        except:
            raise Exception("Unable initialize matching engine %s" % self.featureExtractor)

    def initFeatureExtractor(self):
        try:
            featureExtractor = getattr(features, self.featureExtractor)
            featureExtractorClass = getattr(featureExtractor, featureExtractor.className)
            self.featureExtractor = featureExtractorClass(os.path.join(self.distrPath, "software"))
        except:
            raise Exception("Unable initialize feature extractor %s" % self.featureExtractor)

    def extractFeatures(self, photo):
        # let self.featureExtractor do its job
        os.chdir(self.workDir)
        self.featureExtractor.extract(os.path.join(self.workDir, photo), self.photoDict[photo])
        self.featuresListFile.write("%s.%s\n" % (photo, self.featureExtractor.fileExtension))
        os.chdir(self.currentDir)
    
    def matchFeatures(self):
        # let self.matchingEngine do its job
        os.chdir(self.workDir)
        self.matchingEngine.match()
        os.chdir(self.currentDir)

    
    def doBundleAdjustment(self):
        # just run Bundler here
        print("\nPerforming bundle adjustment...")
        os.chdir(self.workDir)
        os.mkdir("bundle")
        
        # create options.txt
        optionsFile = open("options.txt", "w")
        optionsFile.writelines(self.bundlerOptions)
        optionsFile.close()

        bundlerExecutable = ''
        if sys.platform == "win32": bundlerExecutable = os.path.join(self.distrPath, "software/bundler/bin/bundler.exe")
        else: bundlerExecutable = os.path.join(self.distrPath, "software/bundler/bin/bundler")

        bundlerOutputFile = open("bundle/out", "w")
        subprocess.call([bundlerExecutable, "list.txt", "--options_file", "options.txt"], **dict(stdout=bundlerOutputFile))
        bundlerOutputFile.close()
        os.chdir(self.currentDir)
        print("Finished! See the results in the '%s' directory" % self.workDir)
    
    
    def openResult(self):
        if sys.platform == "win32":
            subprocess.call(["explorer", self.workDir])
        elif sys.platform == "linux2":
            subprocess.call(["xdg-open", self.workDir])
        else: 
            print ("Thanks")

# service function: get path of an executable (.exe suffix is added if we are on Windows)
def getExecPath(dir, fileName):
    if sys.platform == "win32": fileName = "%s.exe" % fileName
    return os.path.join(dir, fileName)

# a helper function to get CCD width from sqlite database
def getCcdWidthFromDatabase(exifMake, exifModel, pluginPath):

    cameraFilePath = pluginPath + "\osmbundler\cameras\cameras.txt"
    cameraFile  = open(cameraFilePath, "rt")
    reader = csv.reader(cameraFile)
    for row in reader:
        if (row[0] == exifMake and row[1] == exifModel):
            return float(row[2])
    cameraFile.close()