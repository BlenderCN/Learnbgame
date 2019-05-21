bl_info = {
    "name": "Procedural Planets",
    "category": "Add Mesh",
    "author": "Rafael",
    "version": (0, 0),
    }

import bpy

from .tect import TectonicsOp
from .operatorCPU import GenerateCPU

import traceback
OCL_PRESENT = False
try:
    from .operatorOCL import clInit, GenerateGPU
    OCL_PRESENT = True
except:
    raise
    traceback.print_exc()

#############################################
# un-/register formalities
#############################################

def register():
    if OCL_PRESENT:
        clInit()
        bpy.utils.register_class(GenerateGPU)
    bpy.utils.register_class(GenerateCPU)
    bpy.utils.register_class(TectonicsOp)
    
def unregister():
    if OCL_PRESENT:
        bpy.utils.unregister_class(GenerateGPU)
    bpy.utils.unregister_class(GenerateCPU)
    bpy.utils.unregister_class(TectonicsOp)

if __name__ == "__main__": # lets you run the script from a Blender text block; useful during development
    register()
