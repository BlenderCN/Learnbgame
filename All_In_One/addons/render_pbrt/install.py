import os
import subprocess

def install():

    currDir = os.path.abspath(os.path.dirname(__file__))
    compressedIilePath = os.path.join(currDir, "PBRT-IILE.tgz")
    if os.path.exists(compressedIilePath):

        print("First run, extracting PBRT-IILE project files")

        # Extract
        subprocess.call([
            "tar",
            "-xf",
            "PBRT-IILE.tgz"
        ], cwd=currDir)

        # Delete the archive
        os.remove(compressedIilePath)

# Useful to check if PBRT or OBJ2PBRT are in one of the available paths
# Returns the path or executable name if found,
# returns None if not available
def getExecutablePath(userDefinedBuildPath, defaultIileBuildPath, execName):

    # Check user defined path
    userDefinedPbrt = os.path.join(userDefinedBuildPath, execName)
    if os.path.exists(userDefinedPbrt):
        return userDefinedPbrt

    # Check default path
    defaultPbrt = os.path.join(defaultIileBuildPath, execName)
    if os.path.exists(defaultPbrt):
        return defaultPbrt

    # Check if the executable is in PATH
    try:
        subprocess.call([execName, "-h"])
        return execName
    except OSError as e:
        return None

def findNodeDir(buildPath):
    iileDir = os.path.dirname(buildPath)
    pbrtIileDir = os.path.dirname(iileDir)
    nodeBinDir = os.path.join(pbrtIileDir, "node", "bin")
    nodePath = os.path.join(nodeBinDir, "node")
    if os.path.exists(nodePath):
        return nodeBinDir
    else:
        return None
