from pathlib import Path
from tempfile import TemporaryDirectory
import os.path as op
import shutil
import subprocess


def get_NMS_dir(fpath):
    """ Returns the NMS file directory from the given filepath. """
    path = Path(fpath)
    parts = path.parts
    return str(Path(*parts[:parts.index('MODELS')]))
