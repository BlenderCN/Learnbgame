import argparse

flags = {
    'file': ['-f','--file'],
    'list': ['-l','--list'],
    'blend': ['-b', '--blend'],
    'output': ['-o', '--output'],
    'um/XYZ': ['--XYZ'],
    'um/VOL': ['--VOL'],
    'vol/xyz': ['--xyz'],
    'vol/VOL': ['--vol'],
    'vox/mesh': ['--vox'],
    'nm/vox': ['--nm'],
    # Nonstandard
    'tmp': ['--tmp'],
    'zspan': ['--zspan'],
    'zps': ['--zps'],
    'fps': ['--fps'],
    'task': ['-t', '--task'],
    'runs': ['-r', '--runs'],
}

def key(k):
    helps = {
        'folder': '/folder/ or /id_%%d/folder/',
        'file': '*_segmentation_%%d.stl (default {})',
        'list': '%%d:%%d:%%d... list for %%d in folder and file', 
        'output': 'Output folder to render scene images',
        'blend': 'Blender file to save output',
        'um/VOL': 'Set D:H:W size of volume measured in um (default {})',
        'um/XYZ': 'Set X:Y:Z origin of full volume in microns (default {})',
        'vol/VOL': 'Xn:Yn:Zn subvolumes in full volume (default {})',
        'vol/xyz': 'Xi:Yi:Zi # subvolumes offset from origin (default {})',
        'vox/mesh': 'w:h:d of voxels per mesh unit (default {})',
        'nm/vox': 'w:h:d of nm per voxel (default {})',
        # Nonstandard
        'tmp': 'Temporary folder (default {})',
        'zspan': 'start:stop slices (default all)',
        'zps': 'z slices per second (default {})',
        'fps': 'frames per second (default {})',
        'task': 'order in the list of jobs (default {})',
        'runs': 'length of the list of jobs (default {})',
    }
    defaults = {
        'file': '*.*',
        'output': '',
        'blend': '',
        'um/VOL': '50:50:50',
        'um/XYZ': '0:0:0',
        'vol/VOL': '1:1:1',
        'vol/xyz': '0:0:0',
        'vox/mesh': '1:1:1',
        'nm/vox': '4:4:30',
        # Nonstandard
        'tmp': 'tmp',
        'zspan': '',
        'fps': 1,
        'zps': 4,
        'task': 0,
        'runs': 1,
    }
    choices = {
        'fps': range(4,64),
    }
    keys = {
        'help': helps.get(k, '???'),
    }
    if k in defaults:
        v = defaults[k]
        keys['default'] = v
        keys['help'] = keys['help'].format(v)
        if type(v) is int:
            keys['type'] = int
    if k in choices:
        keys['choices'] = choices[k]

    return keys

def add_argument(cmd, i):

    words = flags.get(i,[i])
    cmd.add_argument(*words, **key(i))

def setup(_filename, _describe, _items=[], ez=False):
    COMMAND = _filename
    if not ez:
        COMMAND = 'blender -P '+_filename+' --'
    DETAILS = _describe + '\n'
    'The "folder" and "file" can take %%d'
    ' from --list %%d:%%d:%%d. At least one *'
    ' wildcard must find only digits if no'
    ' --list is given. --VOL and --XYZ set'
    ' the scene in physical micrometers.'
    ' The other spatial keywords simply'
    ' allow consistency between sources.'

    # Parse with defaults
    cmd = argparse.ArgumentParser(**{
        'prog': COMMAND,
        'description': DETAILS,
        'formatter_class': argparse.RawTextHelpFormatter,
    })

    positional = ['folder']
    optional = [
        'file', 'list', 'blend',
        'output', 'um/XYZ', 'um/VOL',
        'vol/xyz', 'vol/VOL',
        'vox/mesh', 'nm/vox',
    ]
    items = positional + optional
    # Allow custom items
    if _items:
        items = _items
    for i in items:
        add_argument(cmd, i)

    return cmd
