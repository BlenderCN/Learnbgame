"""
This script exports PayDay 2 Model File format files to Blender.

Usage:
Execute this script from the "File->Import" menu and choose where to
save the file.

"""

import bpy



def write(filepath):

    #TODO: implement export code
    
    # write to a file
    file = open(filepath, "w")
    file.close()
