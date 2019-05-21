#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Release packaging script for LDR Importer.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

END GPL LICENSE BLOCK

"""


from __future__ import print_function

import os
import sys
import shutil
import distutils.file_util
import distutils.dir_util

from __version__ import version

# Support Python 2 and 3 input
get_input = (input if sys.version_info[:2] >= (3, 0) else raw_input)  # noqa

# Required folders
curDir = os.path.dirname(os.path.realpath(__file__))
archivesFolder = os.path.join(curDir, "Archives")
tmpFolder = os.path.join(archivesFolder, "tmp")
blenderFolder = os.path.join(tmpFolder, "io_scene_ldrimporter")

scriptFiles = [
    "__init__.py",
    "__version__.py",
    "import_ldraw.py",
    "src/__init__.py",
    "src/ldcolors.py",
    "src/ldconsole.py",
    "src/ldmaterials.py",
    "src/ldprefs.py",
    "src/extras/__init__.py",
    "src/extras/cleanup.py",
    "src/extras/gaps.py",
    "src/extras/linked_parts.py"
]

proseFiles = [
    "README.md",
    "LICENSE"
]

print("Creating required folders")
if not os.path.exists(blenderFolder):
    os.makedirs(blenderFolder)

# Construct final version number (maj, min, patch) and archive filename
finalVersion = "v{0}.{1}.{2}".format(version[0], version[1], version[2])
archiveFile = "LDR-Importer-{0}".format(finalVersion)

# Copy the script and prose files
print("Copying required files")
for f in scriptFiles:
    partDir = os.path.join(blenderFolder, os.path.dirname(f))
    distutils.dir_util.create_tree(partDir, f)
    distutils.file_util.copy_file(f, partDir)

for f in proseFiles:
    distutils.file_util.copy_file(f, blenderFolder)

# Create the release archive
print("Creating release archive")
os.chdir(archivesFolder)
shutil.make_archive(archiveFile, format="zip", root_dir=tmpFolder)

# Clean up
print("Removing temporary files")
os.chdir(curDir)
distutils.dir_util.remove_tree(tmpFolder)
print("\nLDR Importer {0} packaged and saved to\n{1}.zip".format(
      finalVersion, os.path.join(archivesFolder, archiveFile)))
get_input("\nPress Enter to close. :) ")
raise SystemExit(0)
