# This stub runs a python script relative to the currently open
# blend file, useful when editing scripts externally.

import bpy
import os
import sys

# Use your own script name here:
filename = r"E:\paths-visualizer\__init__.py"

filepath = os.path.join(os.path.dirname(bpy.data.filepath), filename)
global_namespace = {"__file__": filepath, "__name__": "__main__"}

# add file's working directory to python path
sys.path.append(os.path.dirname(filepath))

with open(filepath, 'rb') as file:
    exec(compile(file.read(), filepath, 'exec'), global_namespace)

