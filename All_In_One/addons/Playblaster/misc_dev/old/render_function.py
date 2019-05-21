import bpy
import os
import subprocess

from .preferences import get_addon_preferences
from .misc_functions import absolute_path, create_dir
from .global_variables import blender_executable

def playblaster_render_function() :

    # variables
    prefs = get_addon_preferences()
    folder_path = absolute_path(prefs.prefs_folderpath)

    scn = bpy.context.scene
    blender = blender_executable
    blend_filepath = bpy.data.filepath
    blend_dir = os.path.dirname(blend_filepath)
    blend_file = bpy.path.basename(blend_filepath)
    blend_name = os.path.splitext(blend_file)[0]
    new_blend_filepath = os.path.join(blend_dir, "temp_" + blend_file)
    output_name = "playblast_" + blend_name + "_" + scn.name
    output_filepath = os.path.join(folder_path, output_name)
    render_engine = scn.playblaster_render_engine

    # save current file
    bpy.ops.wm.save_as_mainfile(filepath = blend_filepath)

    # create dir if does not exist
    create_dir(folder_path)

    # change output
    scn.render.filepath = output_filepath

    # save temporary file
    bpy.ops.wm.save_as_mainfile(filepath = new_blend_filepath)

    # reopen old blend file
    bpy.ops.wm.open_mainfile(filepath=blend_filepath)

    # launch rendering
    cmd = blender + " -b " + new_blend_filepath + " -E " + render_engine + " -a"
    proc = subprocess.Popen(cmd, shell=False)

    # launch modal check
    for w in bpy.context.window_manager.windows :
        s = w.screen
        for a in s.areas:
            if a.type == 'VIEW_3D' :
                window = w
                area = a
                screen = window.screen
    override = {'window': window, 'screen': screen, 'area': area}

    bpy.ops.playblaster.modal_check(override)
    
    return proc