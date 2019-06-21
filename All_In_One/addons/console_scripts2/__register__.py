
# Pass the registration if the script doesn't have any blender classes
# ie: doesn't define operators/panels etc.

def register():
    #pass
    bpy.utils.register_module(__name__)
 
def unregister():
    #pass
    bpy.utils.unregister_module(__name__)

