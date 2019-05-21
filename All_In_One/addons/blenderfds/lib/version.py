"""BlenderFDS, manage file format version"""

import bpy, sys

blender_version = bpy.app.version
blender_version_string = bpy.app.version_string

blenderfds_version = sys.modules.get("blenderfds").bl_info["version"]
blenderfds_version_string = "{0[0]}.{0[1]}.{0[2]}".format(blenderfds_version)


def get_file_version(context):
    file_version = context.scene.bf_file_version
    # This is an hack. No way to detect old files...
    for ob in bpy.data.objects[:10]: # Check first objects only
        if ob.bf_nl: # Check if an old namelist is set
            for ob in bpy.data.objects: ob.bf_nl = str() # Clear it  
            return 0,0,0 # This file is older than 2.0.1
    else: file_version = tuple(context.scene.bf_file_version)
    return file_version

def get_file_version_string(context):
    file_version = get_file_version(context)
    return file_version[0] and "{0[0]}.{0[1]}.{0[2]}".format(file_version) or "<2.0.1"

def check_file_version(context):
    """Check current file version and manage eventual conversion."""
    # Init
    file_version = get_file_version(context)
    file_version_string = get_file_version_string(context)
    print("BFDS: File version check:", file_version_string)
    # Protect bf_dialog operator
    if not context.window: return
    # Check older
    if file_version < (3,0,0): # Check latest file format change
        msg = "Check your old input data!"
        description = \
"""This file was created on BlenderFDS {1}. Automatic
data conversion to BlenderFDS {0} and FDS 6 is not
supported.""".format(blenderfds_version_string, file_version_string)
        bpy.ops.wm.bf_dialog('INVOKE_DEFAULT', msg=msg, description=description, type="ERROR")
    # Check newer
    elif file_version > blenderfds_version:
        msg = "Install BlenderFDS {} for full support of your data!".format(file_version_string)
        description = \
"""This file was created on BlenderFDS {1}. You are
currently using the older {0} version, new features
are not supported.""".format(blenderfds_version_string, file_version_string)
        bpy.ops.wm.bf_dialog('INVOKE_DEFAULT', msg=msg, description=description, type="ERROR")

def set_file_version(context):
    """Set current file version."""
    for sc in bpy.data.scenes: sc.bf_file_version = blenderfds_version

