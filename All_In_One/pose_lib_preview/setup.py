#!/usr/bin/env python3
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Contribution: Sybren A. Stüvel <sybren@blender.studio>, Blender Cloud and
# Landscape Tools add-ons.

import io
import re
import sys
from distutils.command.bdist import bdist
from distutils.command.install import install
from distutils.command.install_egg_info import install_egg_info

from setuptools import find_packages, setup

# Prevents __pycache__ dirs from being created & packaged.
sys.dont_write_bytecode = True

with io.open('pose_thumbnails/__init__.py', 'rt', encoding='utf8') as f:
    firstbit = f.read(2048)
    version = re.search(r"__version__ = '(.*?)'", firstbit).group(1)


class BlenderAddonBdist(bdist):
    """Ensures that 'python setup.py bdist' creates a zip file."""

    def initialize_options(self):
        super().initialize_options()
        self.formats = ['zip']
        self.plat_name = 'addon'  # use this instead of 'linux-x86_64' or similar.


class BlenderAddonInstall(install):
    """Ensures the module is placed at the root of the zip file."""

    def initialize_options(self):
        super().initialize_options()
        self.prefix = ''
        self.install_lib = ''


class AvoidEggInfo(install_egg_info):
    """Makes sure the egg-info directory is NOT created.

    If we skip this, the user's addon directory will be polluted by egg-info
    directories, which Blender doesn't use anyway.
    """

    def run(self):
        pass


setup(
    cmdclass={
        'bdist': BlenderAddonBdist,
        'install': BlenderAddonInstall,
        'install_egg_info': AvoidEggInfo,
    },
    name='pose_thumbnails',
    description='Blender add-on that adds thumbnails to a pose library.',
    version=version,
    author='Jasper van Nieuwenhuizen',
    author_email='jasper@linesofjasper.com',
    packages=find_packages('.'),
    package_data={'pose_thumbnails': ['README.md', 'CHANGELOG.md', 'thumbnails/*.png']},
    include_package_data=True,
    scripts=[],
    url='https://github.com/jasperges/pose-thumbnails',
    license='GNU General Public License v2 or later (GPLv2+)',
    platforms='',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Environment :: Plugins',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)
