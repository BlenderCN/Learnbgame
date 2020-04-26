import bpy
from . import step1, step2, step3, step4, step5, step6

def register():
    step1.register()
    step2.register()
    step3.register()
    step4.register()
    step5.register()
    step6.register()

def unregister():
    step1.unregister()
    step2.unregister()
    step3.unregister()
    step4.unregister()
    step5.unregister()
    step6.unregister()

