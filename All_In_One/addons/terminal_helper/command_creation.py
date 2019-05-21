import bpy

def render_single_image(frame):
    return "{blender} -b {file} -f {frame}".format(
        blender = get_prepared_blender_path(),
        file = get_prepared_file_path(),
        frame = frame
    )

def render_whole_animation():
    return "{blender} -b {file} -a".format(
        blender = get_prepared_blender_path(),
        file = get_prepared_file_path()
    )


def get_prepared_blender_path():
    return doubleQuote(bpy.app.binary_path)

def get_prepared_file_path():
    return doubleQuote(bpy.data.filepath)

def doubleQuote(text):
    return '"{}"'.format(text)
