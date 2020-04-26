import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import subprocess,logging

from engine import MatchingEngine

className = "BundlerMatching"
class BundlerMatching(MatchingEngine):
    featuresListFileName = "list_features.txt"
    executable = ''
    
    def __init__(self, distrDir):
        if sys.platform == "win32":
            self.executable = os.path.join(distrDir, "bundler/bin/KeyMatchFull.exe")
        else:
            self.executable = os.path.join(distrDir, "bundler/bin/KeyMatchFull")
        logging.info("BundlerMatching executable path: %s" % self.executable)

    def match(self):
        logging.info("\nPerforming feature matching...")
        subprocess.call([self.executable, self.featuresListFileName, self.outputFileName])