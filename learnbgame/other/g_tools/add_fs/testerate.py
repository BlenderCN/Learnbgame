#blinf
bl_info = {
    "name": "Testerate",
    "location": "View3D > Add > Mesh > Testerate",
    "description": "Testerate",
    "category": "Add Mesh"}

#importdefs
from g_tools.ops.testerate_ops import *
        
if __name__ == "__main__":
    register()