import logging
import sys, os, getopt, tempfile, subprocess, shutil

# service function: get path of an executable (.exe suffix is added if we are on Windows)
def getExecPath(dir, fileName):
    if sys.platform == "win32": fileName = "%s.exe" % fileName
    return os.path.join(dir, fileName)

bundlerListFileName = "list.txt"

commandLineLongFlags = ["bundlerOutputPath=", "ClusterToCompute="]


class OsmCmvs():

    distrPath = ""
    currentDir = ""
    workDir = ""
    clusterToCompute = 1
    bundleOutArg = ""

    pmvsExecutable = ""
    cmvsExecutable = ""
    genOptionExecutable = ""
    bundler2PmvsExecutable = ""
    RadialUndistordExecutable = ""
    Bundle2VisExecutable = ""

    def __init__(self, pluginPath, bundlePath, clusters):
               
        self.distrPath = pluginPath
        self.setExecutables()
        self.bundleOutArg = bundlePath
        self.clusterToCompute = clusters

        # save current directory (i.e. from where RunBundler.py is called)
        self.currentDir = os.getcwd()
        # create a working directory
        self.workDir = self.bundleOutArg
        logging.info("Working directory created: "+self.workDir)
        
        if not (os.path.isdir(self.bundleOutArg) or os.path.isfile(self.bundleOutArg)):
            raise Exception ("'%s' is neither directory nor a file name" % self.bundleOutArg)
    
    def doBundle2PMVS(self):
        # just run Bundle2PMVS here
        logging.info("\nPerforming Bundler2PMVS conversion...")
        os.chdir(self.workDir)
        os.mkdir("pmvs")

        # Create directory structure
        os.mkdir("pmvs/txt")
        os.mkdir("pmvs/visualize")
        os.mkdir("pmvs/models")
        
        #$BASE_PATH/bin32/Bundle2PMVS.exe list.txt  bundle/bundle.out
        print("Running Bundle2PMVS to generate geometry and converted camera file")
        print("PMVS EXEC = ", self.bundler2PmvsExecutable)
        subprocess.call([self.bundler2PmvsExecutable, "list.txt", "bundle/bundle.out"])
		
        # Apply radial undistortion to the images
        print ("Running RadialUndistort to undistort input images")
        subprocess.call([self.RadialUndistordExecutable, "list.txt", "bundle/bundle.out", "pmvs"])
		
        print ("Running Bundle2Vis to generate vis.dat")
        subprocess.call([self.Bundle2VisExecutable, "pmvs/bundle.rd.out", "pmvs/vis.dat"])

        os.chdir(os.path.join(self.workDir,"pmvs"))
        #Rename all the files to the correct name
        undistortTextFile = open("list.rd.txt", "r")
        imagesStrings = undistortTextFile.readlines()
        print("Move files in the correct directory")
        cpt = 0
        for imageString in imagesStrings:
          image = imageString.split(".")
          # sh => mv pmvs/et001.rd.jpg pmvs/visualize/00000000.jpg
          shutil.copy(image[0]+".rd.jpg", "visualize/%08d.jpg"%cpt)
          # sh => mv pmvs/00000000.txt pmvs/txt/
          shutil.copy("%08d.txt"%cpt, "txt/%08d.txt"%cpt)
          os.remove(image[0]+".rd.jpg")
          os.remove("%08d.txt"%cpt)
          cpt+=1
        
        undistortTextFile.close()
		
        logging.info("Finished!")
    
    def doCMVS(self):
      os.chdir(os.path.join(self.workDir,"pmvs"))
      subprocess.call([self.cmvsExecutable, "./", str(self.clusterToCompute)])
      subprocess.call([self.genOptionExecutable, "./"])
      
      #find all the option-XXX files and run PMVS2 on it
      # three conditions are checked in the list comprehension below:
      # 1) f is file
      # 2) f don't have extension
      # 3) f starts with "option-"
      for file in [f for f in os.listdir("./") if os.path.isfile(os.path.join("./", f)) and os.path.splitext(f)[1]=='' and "option-" in f]:
        subprocess.call([self.pmvsExecutable, "./", file])
      #for root, dirs, files in os.walk("./"):
      #  for file in files:
      #    if "option-" in file:
      #      subprocess.call([self.pmvsExecutable, "./", file])
      os.chdir("C:\\")

        
    def doPMVS(self, path, optionFile):
        os.chdir(os.path.join(path,"pmvs"))
        print ("Run PMVS2 : %s " % self.pmvsExecutable)
        subprocess.call([self.pmvsExecutable, "./", optionFile])

    def setExecutables(self):
        self.pmvsExecutable = getExecPath(self.distrPath, "software/pmvs/bin/pmvs2")
        self.cmvsExecutable = getExecPath(self.distrPath, "software/cmvs/bin/cmvs")
        self.genOptionExecutable = getExecPath(self.distrPath, "software/pmvs/bin/genOption")

        bundlerBinPath = ''
        if sys.platform == "win32":
            bundlerBinPath = os.path.join(self.distrPath, "software/bundler/bin/")
        else:
            bundlerBinPath = os.path.join(self.distrPath, "software/bundler/bin/")

        self.bundler2PmvsExecutable = getExecPath(bundlerBinPath, "Bundle2PMVS")
        self.RadialUndistordExecutable = getExecPath(bundlerBinPath, "RadialUndistort")
        self.Bundle2VisExecutable = getExecPath(bundlerBinPath, "Bundle2Vis")
    
    def printHelpExit(self):
        self.printHelp()
        sys.exit(2)
    
    def openResult(self):
        if sys.platform == "win32": subprocess.call(["explorer", self.workDir])
        else: print ("See the results in the '%s' directory" % self.workDir)
    
    def printHelp(self):
        print ("Error")
        helpFile = open(os.path.join(self.distrPath, "osmcmvs/help.txt"), "r")
        print (helpFile.read())
        helpFile.close()

