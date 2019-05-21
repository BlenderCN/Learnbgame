import bpy

data = bpy.data

def getSelected():
        return bpy.context.selected_objects

def set_loading_state(obj, value):
    """
    Set the loading state for the given blender object.
    """
    obj.opensim.state = value

def get_loading_state(obj):
    return str(obj.opensim.state)

def getVersion():
    return "Blender "+str(bpy.app.version_string)


