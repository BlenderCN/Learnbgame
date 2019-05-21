import bpy
import json
from .common import *
from shutil import copyfile


def speaker_data_path(blender_object):
    path = library_path(blender_object) + "speaker_data/" + blender_object.name + ".speaker_data"
    return path.strip('/')


def write(report, directory):

    blender_speakers = bpy.data.speakers

    for speaker in blender_speakers:

        filename = speaker.sound.name
        source_filepath = bpy.path.abspath(speaker.sound.filepath, library=speaker.library)
        filepath = library_path(speaker) + "sounds/" + filename
        full_filepath = directory + '/' + filepath
        os.makedirs(os.path.dirname(full_filepath), exist_ok=True)
        copyfile(source_filepath, full_filepath)

        print('Wrote: ' + full_filepath)

        volume = speaker.volume
        pitch = speaker.pitch

        light = {"volume": float(volume),
                 "pitch": float(pitch),
                 "sound": filepath}

        path = directory + '/' + speaker_data_path(speaker)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json_file = open(path, 'w')
        json.dump(light, json_file)
        json_file.close()
        report({'INFO'}, "Wrote:" + path)
    report({'INFO'}, "Wrote all speakers.")

