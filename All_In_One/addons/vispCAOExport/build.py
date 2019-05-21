#!/usr/bin/env python

from os.path import abspath, dirname, join as pjoin
import zipfile

SRC_DIR = dirname(abspath(__file__))

with zipfile.ZipFile('visp_cao_export.zip', 'w', zipfile.ZIP_DEFLATED) as arch:
    for filename in [
            '__init__.py',
            'export_cao.py',
			'property_panel.py',
			'treeview_circles.py',
			'treeview_faces.py',
			'treeview_cylinders.py',
			'treeview_lines.py']:
        arch.write(pjoin(SRC_DIR, filename), 'visp_cao_export/'+filename)

print('created file: visp_cao_export.zip')
