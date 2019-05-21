import bpy, bmesh
from mathutils import *
from math import *
import random, time, struct, ctypes, imp

from . import myprops, involute

def genGear(ob, scene):
    return involute.genGear(ob, scene);
    
def run(ctx=None):
    if ctx is None:
        ctx = bpy.context
        
    for ob in ctx.scene.objects:
        if ob.geargen.enabled:
            genGear(ob, ctx.scene)

class RecalcAllGears(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.geargen_recalc_all_gears"
    bl_label = "Recalc All Gears"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        run(context)
        return {'FINISHED'}

registered = False
def register():
    global registered
    if registered: return
    registered = True
    
    bpy.utils.register_class(RecalcAllGears)
    myprops.register()

def unregister():
    global registered
    if not registered: return
    registered = False
    
    bpy.utils.unregister_class(RecalcAllGears)
   
def on_update(self, context):
    if context.scene.geargen.auto_generate:
        run()

myprops.register_prop_update(on_update)
register()

if __name__ == "__main__":
    run()
