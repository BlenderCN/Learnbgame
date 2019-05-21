# File: pilbin.py

import os
import sys
import subprocess

def main():
    inputImage = "C:\\sfminput\\kermit000.jpg"
    outputImage = "C:\\sfmoutput\\kermit000.jpg"

    output = subprocess.check_output(["C:\\Program Files\\Blender Foundation\\Blender\\2.69\\scripts\\addons\\blenderSFM\\software\\pilbin\\build\\exe.win32-3.3\\pilbin.exe", inputImage, outputImage])
    print(output)
 
if __name__ == "__main__":
    main()