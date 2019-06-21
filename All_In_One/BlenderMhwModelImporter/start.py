#Ported to blender from "MT Framework tools" https://www.dropbox.com/s/4ufvrgkdsioe3a6/MT%20Framework.mzp?dl=0 
#(https://lukascone.wordpress.com/2017/06/18/mt-framework-tools/)

import os
import sys
cwd = os.getcwd()
sys.path.append("..")
from BlenderMhwModelImporter import register

register()