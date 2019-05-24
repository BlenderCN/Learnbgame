bl_info = {
    "name": "Restart",
    "description": "Restart blender file",
    "author": "Sreenivas Alapati (cg-cnu)",
    "version": (1, 0),
    "blender": (2, 9, 0),
    "category": "Learnbgame",
}


import subprocess
import atexit
import time
import bpy


def launch():
    """
    launch the blender process
    """
    # get the binary path of blender
    binary_path = bpy.app.binary_path
    # get current blender file
    file_path = bpy.data.filepath
    # launch a background process
    subprocess.Popen([binary_path, file_path])


def main():
    """
    main func
    """
    # check if the file is not saved
    if bpy.data.is_dirty:
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    # ask for confirmation
    launch_code = launch
    atexit.register(launch_code)
    # sleep for a sec
    time.sleep(1)
    # quit blender
    exit()


class Restart(bpy.types.Operator):
    # TODO: created by admin @ 2017-10-25 19:38:16
    # move this one to scene ?
    bl_idname = "object.restart"
    bl_label = "Restart"

    def execute(self, context):
        main()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(Restart)


def unregister():
    bpy.utils.unregister_class(Restart)


if __name__ == "__main__":
    register()
