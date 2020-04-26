import os
import bpy


DEBUG = True

if DEBUG:
    import sys
    sys.path.append(os.environ['PYDEV_DEBUG_PATH'])
    import pydevd
    
from . import testthis

class RenderSwitchOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "view3d.render_switch_opr"
    bl_label = "renderer switcher"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if DEBUG: pydevd.settrace()
        testthis.execute(context)
        return {'FINISHED'}
    
    
# class SwitchRenderEngine(bpy.types.Menu):
#    """ For testing the render settings of different render engines """
#    bl_label = "switch renderer"
#    bl_idname= "OBJECT_MT_switch_renderer"
#    
#    def draw(self , context):
#        layout = self.layout
#        layout.operator("object.render_switch_opr")
        


addon_keymaps = []

def make_map():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY', region_type='WINDOW')
    kmi = km.keymap_items.new(idname=RenderSwitchOperator.bl_idname, type='F9', value='PRESS')
    addon_keymaps.append((km, kmi))

def remove_map():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def register():
    bpy.utils.register_class(RenderSwitchOperator)
    make_map()

def unregister():
    remove_map()
    bpy.utils.register_class(RenderSwitchOperator)
    
