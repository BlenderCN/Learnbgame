import bpy
from os.path import dirname,join,realpath
from .functions.utils import read_json

working_dir = dirname(realpath(__file__))
settings = read_json(join(working_dir,"settings.json"))

class LibManagerPanel(bpy.types.Panel):
    bl_label = 'Lib Manager'
    bl_category = settings['bl_category']
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        window_btn = layout.operator('libmanager.modal')
