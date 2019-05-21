import bpy , subprocess, threading

from .preferences import get_addon_preferences
from .misc_functions import absolute_path, create_dir, delete_file, get_file_in_folder

# render function
def render_function(cmd, total_frame, scene, folder_path, output_name, blend_file) :
    debug = bpy.context.scene.playblaster_debug
    # launch rendering
    if debug : print(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    frame_count = 0
    while True :
        if not bpy.context.scene.playblaster_is_rendering :
            process.kill()
            break
        line = process.stdout.readline()
        if line != '' :
            #debug
            if debug : print(line)
            if b"Append frame " in line :
                frame_count += 1
                try :
                    scene.playblaster_completion = frame_count / total_frame * 100
                except AttributeError :
                    #debug
                    if debug : print("AttributeError avoided")
                    pass

            if b"Blender quit" in line :
                break
        else:
            break

# launch threading
def threading_render(arguments) :
    render_thread = threading.Thread(target=render_function, args=arguments)
    render_thread.start()
