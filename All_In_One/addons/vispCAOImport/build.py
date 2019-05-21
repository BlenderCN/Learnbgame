#!/usr/bin/env python

from os.path import abspath, dirname, join as pjoin
import zipfile

SRC_DIR = dirname(abspath(__file__))

with zipfile.ZipFile('visp_cao_import.zip', 'w', zipfile.ZIP_DEFLATED) as arch:
    for filename in [
            '__init__.py',
            'import_cao.py']:
        arch.write(pjoin(SRC_DIR, filename), 'visp_cao_import/'+filename)

print('created file: visp_cao_import.zip')
