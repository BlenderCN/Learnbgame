from blendmotion.core import animation, effector, rigging

def register():
    animation.register()
    effector.register()
    rigging.register()

def unregister():
    rigging.unregister()
    effector.unregister()
    animation.unregister()
