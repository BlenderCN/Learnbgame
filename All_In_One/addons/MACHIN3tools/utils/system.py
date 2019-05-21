import bpy


def quotepath(path):
    if " " in path:
        path = '"%s"' % (path)
    return path


def add_path_to_recent_files(path):
    """
    add the path to the recent files list, for some reason it's not done automatically when saving or loading
    """

    try:
        recent_path = bpy.utils.user_resource('CONFIG', "recent-files.txt")
        with open(recent_path, "r+") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(path.rstrip('\r\n') + '\n' + content)

    except (IOError, OSError, FileNotFoundError):
        pass
