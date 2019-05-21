import shutil
import os

def make(out_path):
    if not os.path.exists(out_path):
        try:
            os.makedirs(out_path)
        except OSError: 
            pass      

def format_glob(_glob, *args):
    val = _glob
    try:
        # Allow '/path/*/' % ()
        # Allow '/path/%d' % (id,)
        val = val % args
    except (TypeError, ValueError) as e:
        # Disallow '/path/%d' % ()
        if not len(args):
            raise err.MeshPathError(e.args[0], key, val)
        # Allow '/path/45' % (id,)
        pass
    return val

def link(_path, tmp_root, name, ext):
    # Create a temporary folder for this file
    tmp_folders = _path.replace('.','_').split(os.sep)
    tmp_path = os.path.join(tmp_root, *tmp_folders)
    tmp_link = os.path.join(tmp_path, '{}.{}'.format(name, ext))
    make(tmp_path)
    try:
        if os.path.exists(tmp_link):
            if os.path.isdir(tmp_link):
                os.rmdir(tmp_link)
            else:
                os.unlink(tmp_link)
    except OSError as e:
        raise err.TempPathError(e.args[0], _path, tmp_link)

    # Link the path temporarily
    os.symlink(_path, tmp_link)
    return tmp_link

def unlink(arg):
    # Remove tmp directory
    if os.path.exists(arg.tmp):
        shutil.rmtree(arg.tmp)


