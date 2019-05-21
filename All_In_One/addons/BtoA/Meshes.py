import imp
from arnold import *
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty

if "bpy" in locals():
    imp.reload(PolyMesh)
else:
    import bpy
    from . import PolyMesh

from bl_ui import properties_data_mesh
for member in dir(properties_data_mesh):
    subclass = getattr(properties_data_mesh, member)
    try:
        subclass.COMPAT_ENGINES.add('BtoA')
    except:
        pass
del properties_data_mesh

class Meshes:
    '''This class handles the export of all lights'''
    def __init__(self,scene,materials):
        self.scene = scene
        self.materials=materials
        
    def writeMeshes(self):
        for i in self.scene.objects:
            if i.hide_render == False and i.type == "MESH":
                mesh = PolyMesh.PolyMesh(i,self.materials,self.scene)
                mesh.write()


